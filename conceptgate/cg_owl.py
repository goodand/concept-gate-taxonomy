#!/usr/bin/env python3
"""cg_owl — concepts를 OWL 2 DL로 직렬화해 풀 DL reasoner가 계층을 생성하게 한다.

설계: owl-serialization-spec.md (Project_in_progress)
핵심: primitive(⊑, 필요조건만) vs defined(≡, 필요충분) 구분.
  - 자연종(Bird)은 primitive → feature가 겹쳐도 spurious is-a가 생기지 않는다.
  - 형식개념(Square)은 defined → reasoner가 다중 부모(meet)를 자동 분류한다.
이것이 "essential 집합 포함 = is-a" (리뷰 발견 2)의 근본 대체다.

의존성: owlready2 (분류 실행에는 Java 필요 — HermiT).
이 모듈은 concept-gate 코어와 독립적인 L3 검증층이다. LLM/normalizer가
definition_kind와 restriction을 '제안'하고, 이 모듈이 OWL로 옮기면
reasoner가 subsumption을 '판정'한다.
"""
from __future__ import annotations

import types
from typing import Any, Dict, List, Optional

from owlready2 import (
    AllDisjoint,
    DataProperty,
    FunctionalProperty,
    Nothing,
    ObjectProperty,
    Thing,
    World,
    rdf_type,
    sync_reasoner,
)

SUPPORTED_RESTRICTIONS = {"some", "only", "exactly", "min", "max", "value",
                          "subClassOf"}

# gUFO stereotype (owl-serialization-spec.md §2). "defined_class"는 meta-type이
# 아니라 definition_kind="defined"의 동의어라 punning 마커가 없다.
GUFO_STEREOTYPES = frozenset(
    {"kind", "subkind", "phase", "role", "category", "defined_class"})

# stereotype -> punning 마커 클래스의 로컬 이름. 리뷰 발견 4: gUFO는
# "Child rdf:type gufo:Phase" (punning, me타타입) + "Child SubClassOf Person"
# (subsumption) 둘 다로 phase를 표현한다 — 기존 코드는 후자조차 없었다.
# 마커는 도메인 개념과 이름이 겹치지 않도록 접두어를 둔다(사용자가 개념을
# "Phase"라 명명할 수 있음).
_STEREOTYPE_MARKERS = {
    "kind": "_GUFOKind",
    "subkind": "_GUFOSubKind",
    "phase": "_GUFOPhase",
    "role": "_GUFORole",
    "category": "_GUFOCategory",
}
_MARKER_TO_LABEL = {v: v[len("_GUFO"):] for v in _STEREOTYPE_MARKERS.values()}


class SerializationError(ValueError):
    """직렬화 입력이 스키마를 위반. stage='owl-serialize' 오류로 표면화."""


# value restriction의 literal filler로 허용하는 타입 (owlready2 지원 범위)
_VALUE_FILLER_TYPES = (bool, int, float, str)


def _validate_inputs(concepts, object_properties, data_properties,
                     disjoint_groups, iri) -> None:
    """owlready2에 닿기 전에 payload 전체를 타입 검증한다.

    build 도중의 TypeError/KeyError/AttributeError는 서버에서 unhandled
    crash로 노출된다 — 여기서 전부 SerializationError로 바꾼다.
    """
    if not isinstance(iri, str) or not iri:
        raise SerializationError(f"iri must be non-empty str, got {iri!r}")
    if not isinstance(concepts, list):
        raise SerializationError(
            f"concepts must be list, got {type(concepts).__name__}")
    for i, c in enumerate(concepts):
        if not isinstance(c, dict):
            raise SerializationError(
                f"concepts[{i}] must be dict, got {type(c).__name__}")
        name = c.get("name")
        if not isinstance(name, str) or not name:
            raise SerializationError(
                f"concepts[{i}].name must be non-empty str, got {name!r}")
        genus = c.get("genus")
        if genus is not None and not isinstance(genus, str):
            raise SerializationError(
                f"{name}: genus must be str|None, got {type(genus).__name__}")
        stereotype = c.get("stereotype")
        if stereotype is not None and (
                not isinstance(stereotype, str)
                or stereotype not in GUFO_STEREOTYPES):
            raise SerializationError(
                f"{name}: unknown stereotype {stereotype!r}, "
                f"must be one of {sorted(GUFO_STEREOTYPES)}")
        for field in ("differentia", "necessary_only"):
            specs = c.get(field, [])
            if specs is None:
                continue
            if not isinstance(specs, list):
                raise SerializationError(
                    f"{name}.{field} must be list, "
                    f"got {type(specs).__name__}")
            for j, spec in enumerate(specs):
                _validate_restriction_spec(spec, f"{name}.{field}[{j}]")
    if not isinstance(object_properties or [], list):
        raise SerializationError(
            f"object_properties must be list, "
            f"got {type(object_properties).__name__}")
    for i, pname in enumerate(object_properties or []):
        if not isinstance(pname, str) or not pname:
            raise SerializationError(
                f"object_properties[{i}] must be non-empty str, got {pname!r}")
    if not isinstance(data_properties or [], list):
        raise SerializationError(
            f"data_properties must be list, "
            f"got {type(data_properties).__name__}")
    for i, dspec in enumerate(data_properties or []):
        if not isinstance(dspec, dict):
            raise SerializationError(
                f"data_properties[{i}] must be dict, "
                f"got {type(dspec).__name__}")
        dname = dspec.get("name")
        if not isinstance(dname, str) or not dname:
            raise SerializationError(
                f"data_properties[{i}].name must be non-empty str, "
                f"got {dname!r}")
    if not isinstance(disjoint_groups or [], list):
        raise SerializationError(
            f"disjoint_groups must be list, "
            f"got {type(disjoint_groups).__name__}")
    for i, group in enumerate(disjoint_groups or []):
        if not isinstance(group, list):
            raise SerializationError(
                f"disjoint_groups[{i}] must be list, "
                f"got {type(group).__name__}")
        for n in group:
            if not isinstance(n, str):
                raise SerializationError(
                    f"disjoint_groups[{i}] names must be str, got {n!r}")


def _validate_restriction_spec(spec: Any, where: str) -> None:
    """restriction spec 하나의 타입을 검증한다 (표현식 생성 전)."""
    if not isinstance(spec, dict):
        raise SerializationError(
            f"{where}: restriction spec must be dict, "
            f"got {type(spec).__name__}")
    kind = spec.get("restriction")
    if kind not in SUPPORTED_RESTRICTIONS:
        raise SerializationError(f"{where}: unknown restriction: {kind!r}")
    filler = spec.get("filler")
    if kind == "value":
        prop = spec.get("property")
        if not isinstance(prop, str) or not prop:
            raise SerializationError(
                f"{where}: property must be non-empty str, got {prop!r}")
        if not isinstance(filler, _VALUE_FILLER_TYPES):
            raise SerializationError(
                f"{where}: value filler must be bool|int|float|str, "
                f"got {type(filler).__name__}")
        return
    if not isinstance(filler, str) or not filler:
        raise SerializationError(
            f"{where}: filler must be non-empty str (class name), "
            f"got {filler!r}")
    if kind != "subClassOf":
        prop = spec.get("property")
        if not isinstance(prop, str) or not prop:
            raise SerializationError(
                f"{where}: property must be non-empty str, got {prop!r}")


def _restriction_expr(onto, spec: Dict[str, Any], classes: Dict[str, Any],
                      props: Dict[str, Any]):
    # 타입은 _validate_inputs가 보증 — 여기서는 참조 해석만 검사한다
    kind = spec["restriction"]

    if kind == "subClassOf":
        # genus 참조 — 명명된 클래스 그 자체
        filler = classes.get(spec["filler"])
        if filler is None:
            raise SerializationError(f"unknown class: {spec['filler']!r}")
        return filler

    prop = props.get(spec["property"])
    if prop is None:
        raise SerializationError(f"unknown property: {spec.get('property')!r}")

    if kind == "value":
        return prop.value(spec["filler"])

    filler = classes.get(spec["filler"])
    if filler is None:
        raise SerializationError(f"unknown class: {spec['filler']!r}")
    if kind == "some":
        return prop.some(filler)
    if kind == "only":
        return prop.only(filler)
    n = spec.get("cardinality")
    if not isinstance(n, int) or n < 0:
        raise SerializationError(f"cardinality required for {kind}: {spec}")
    return getattr(prop, kind)(n, filler)


def build_ontology(concepts: List[Dict[str, Any]],
                   object_properties: Optional[List[str]] = None,
                   data_properties: Optional[List[Dict[str, Any]]] = None,
                   disjoint_groups: Optional[List[List[str]]] = None,
                   iri: str = "http://conceptgate.local/onto.owl"):
    """concept dict 목록 → owlready2 온톨로지.

    concept 스키마 (스펙 §2):
      {name, definition_kind: primitive|defined, genus: str|None,
       differentia: [restriction...], necessary_only: [restriction...]}
    반환: (world, onto, classes) — world는 격리된 owlready2 World.
    """
    _validate_inputs(concepts, object_properties, data_properties,
                     disjoint_groups, iri)
    world = World()
    onto = world.get_ontology(iri)
    classes: Dict[str, Any] = {}
    props: Dict[str, Any] = {}

    with onto:
        for pname in object_properties or []:
            props[pname] = types.new_class(pname, (ObjectProperty,))
        for dspec in data_properties or []:
            bases = (DataProperty,)
            if dspec.get("functional"):
                bases = (DataProperty, FunctionalProperty)
            p = types.new_class(dspec["name"], bases)
            rng = dspec.get("range")
            if rng is not None:
                p.range = [rng]
            props[dspec["name"]] = p

        # gUFO stereotype 마커 (실제 쓰이는 것만 선언 — 안 쓰는 빌드는
        # 출력이 이전과 바이트 단위로 동일해야 한다)
        needed_markers = {
            _STEREOTYPE_MARKERS[c["stereotype"]] for c in concepts
            if c.get("stereotype") in _STEREOTYPE_MARKERS
        }
        markers = {m: types.new_class(m, (Thing,)) for m in needed_markers}

        # 1차: 클래스 선언 (genus 참조가 순서 무관하도록 먼저 전부 만든다)
        for c in concepts:
            classes[c["name"]] = types.new_class(c["name"], (Thing,))

        # 2차: 공리 부착
        for c in concepts:
            cls = classes[c["name"]]
            kind = c.get("definition_kind", "primitive")
            if kind not in ("primitive", "defined"):
                raise SerializationError(
                    f"{c['name']}: definition_kind must be primitive|defined")

            parts = []
            genus = c.get("genus")
            if genus:
                g = classes.get(genus)
                if g is None:
                    raise SerializationError(f"{c['name']}: unknown genus {genus!r}")
                parts.append(g)
            for spec in c.get("differentia") or []:
                parts.append(_restriction_expr(onto, spec, classes, props))

            necessary = [
                _restriction_expr(onto, spec, classes, props)
                for spec in c.get("necessary_only") or []
            ]

            if kind == "defined":
                if not parts:
                    raise SerializationError(
                        f"{c['name']}: defined인데 genus/differentia 없음")
                expr = parts[0]
                for p in parts[1:]:
                    expr = expr & p
                cls.equivalent_to = [expr]
                for n in necessary:
                    cls.is_a.append(n)
            else:  # primitive: 전부 필요조건(⊑)으로만
                for n in parts + necessary:
                    cls.is_a.append(n)

            marker_name = _STEREOTYPE_MARKERS.get(c.get("stereotype"))
            if marker_name:
                # punning: cls는 SubClassOf로 genus를 특수화하면서 동시에
                # rdf:type으로 meta-type을 갖는다. owlready2의 .is_a는 둘을
                # 구분하지 않고 합쳐 보여주므로(punning 시 확인됨), classify()
                # 가 raw triple로 따로 걸러낸다.
                onto._add_obj_triple_spo(cls.storid, rdf_type,
                                         markers[marker_name].storid)

        for group in disjoint_groups or []:
            unknown = [n for n in group if n not in classes]
            if unknown:
                raise SerializationError(
                    f"disjoint group references unknown classes: {unknown!r}")
            AllDisjoint([classes[n] for n in group])

    return world, onto, classes


def classify(world, onto) -> Dict[str, Any]:
    """HermiT 실행 → 유도된 계층·stereotype 펀닝·unsatisfiable 목록 반환.

    hierarchy는 SubClassOf만 담는다(기존 계약 불변). stereotype 펀닝
    (rdf:type)은 raw triple로 별도 추출한다 — owlready2는 클래스 엔티티의
    rdf:type과 rdfs:subClassOf를 .is_a 하나로 합쳐 보여주므로, 마커를
    거기 섞으면 "Child ⊑ Phase"처럼 보여 subsumption과 meta-typing이
    혼동된다(punning 실험으로 확인).
    """
    with onto:
        sync_reasoner(world, infer_property_values=False, debug=0)

    marker_storid_to_label = {}
    for marker_name, label in _MARKER_TO_LABEL.items():
        marker_cls = onto[marker_name]
        if marker_cls is not None:
            marker_storid_to_label[marker_cls.storid] = label
    marker_storids = set(marker_storid_to_label)

    hierarchy: Dict[str, List[str]] = {}
    stereotypes: Dict[str, str] = {}
    unsat: List[str] = []
    for cls in onto.classes():
        if cls.storid in marker_storids:
            continue  # 마커 자체는 도메인 개념이 아니다
        type_targets = {o for _, _, o in
                        onto._get_obj_triples_spo_spo(cls.storid, rdf_type, None)}
        hit = type_targets & marker_storids
        if hit:
            stereotypes[cls.name] = marker_storid_to_label[next(iter(hit))]
        parents = sorted(
            p.name for p in cls.is_a
            if hasattr(p, "name") and p is not Thing and p.name != cls.name
            and p.storid not in marker_storids
        )
        equiv = list(cls.equivalent_to)
        if Nothing in cls.is_a or Nothing in equiv:
            unsat.append(cls.name)
        hierarchy[cls.name] = parents
    return {"hierarchy": hierarchy, "unsatisfiable": sorted(unsat),
            "stereotypes": stereotypes}


def is_subclass_of(onto, child_name: str, parent_name: str) -> bool:
    """분류 후: child ⊑ parent (전이 포함) 인가.

    ponytail: stereotype 마커(_GUFOPhase 등)를 parent_name으로 넘기면
    owlready2의 .ancestors()가 punning으로 추가된 rdf:type도 subsumption처럼
    따라간다 — True가 나올 수 있다. 마커 조회는 classify()의 stereotypes를
    쓸 것. 실 gUFO owl:imports(finding 3)가 들어오면 이 구분이 다시 필요.
    """
    if not isinstance(child_name, str) or not isinstance(parent_name, str):
        raise SerializationError(
            f"class names must be str: {child_name!r}/{parent_name!r}")
    child = onto[child_name]
    parent = onto[parent_name]
    if child is None or parent is None:
        raise SerializationError(f"unknown class: {child_name}/{parent_name}")
    return parent in child.ancestors()
