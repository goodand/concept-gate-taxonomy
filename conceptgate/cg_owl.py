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
from pathlib import Path
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

# gUFO endurants-only 서브셋 (RDF/XML — owlready2는 Turtle을 못 읽는다).
# 원본: vendor/scior/scior/resources/gufoEndurantsOnly.ttl. 풀 gufo.ttl은
# xsd:date DataAllValuesFrom 공리를 HermiT가 거부한다(OWL 2 datatype map 밖).
# 변환 출처·해시는 third_party/sources.lock.json에 고정.
_GUFO_OWL = Path(__file__).parent / "data" / "gufo.owl"
GUFO_NS = "http://purl.org/nemo/gufo#"

# stereotype → gUFO 실 클래스 로컬이름. 리뷰 발견 4는 로컬 마커(_GUFOPhase)로
# punning을 도입했고, finding 3이 이를 실 gUFO IRI로 교체했다 — 이제
# "Child rdf:type gufo:Phase" (punning, 메타타입) + "Child SubClassOf Person"
# (subsumption) 둘 다 표준 어휘이고, gUFO의 공리(Kind⊥SubKind, Phase⊥Role,
# Rigid⊥NonRigid 등)를 HermiT가 네이티브로 적용한다.
_GUFO_STEREOTYPE_CLASSES = {
    "kind": "Kind",
    "subkind": "SubKind",
    "phase": "Phase",
    "role": "Role",
    "category": "Category",
}


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
    seen_names: set = set()
    for i, c in enumerate(concepts):
        if not isinstance(c, dict):
            raise SerializationError(
                f"concepts[{i}] must be dict, got {type(c).__name__}")
        name = c.get("name")
        if not isinstance(name, str) or not name:
            raise SerializationError(
                f"concepts[{i}].name must be non-empty str, got {name!r}")
        # 중복 이름은 classes dict에서 나중 것이 이전 것을 덮어 개념이 조용히
        # 사라진다 — 빌드 전에 막는다.
        if name in seen_names:
            raise SerializationError(f"duplicate concept name: {name!r}")
        seen_names.add(name)
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
        if len(group) < 2:
            # AllDisjoint는 2개 이상이어야 의미가 있다 (0·1개는 무의미).
            raise SerializationError(
                f"disjoint_groups[{i}] must have >=2 members, got {len(group)}")
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

    # gUFO는 stereotype이 실제 쓰일 때만 로드한다 — 안 쓰는 빌드는 출력이
    # 이전과 동일해야 하고, 205 트리플 파싱·reasoner 부담도 피한다.
    # stereotype이 있는데 gUFO가 없으면 조용히 생략하지 않는다(fail-fast):
    # 생략하면 classify()의 stereotypes가 빈 채로 성공해 위조 통과가 된다.
    needed_stereotypes = {
        c["stereotype"] for c in concepts
        if c.get("stereotype") in _GUFO_STEREOTYPE_CLASSES
    }
    gufo_classes: Dict[str, Any] = {}
    if needed_stereotypes:
        if not _GUFO_OWL.exists():
            raise SerializationError(
                f"stereotype punning requires gUFO but {_GUFO_OWL} is missing")
        try:
            gufo_onto = world.get_ontology(_GUFO_OWL.resolve().as_uri()).load()
        except Exception as exc:
            raise SerializationError(f"gUFO load failed: {exc}") from exc
        onto.imported_ontologies.append(gufo_onto)
        for stereo in needed_stereotypes:
            gufo_cls = world[GUFO_NS + _GUFO_STEREOTYPE_CLASSES[stereo]]
            if gufo_cls is None:
                raise SerializationError(
                    f"gUFO class {_GUFO_STEREOTYPE_CLASSES[stereo]!r} "
                    f"not found in {_GUFO_OWL}")
            gufo_classes[stereo] = gufo_cls

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

            stereo = c.get("stereotype")
            if stereo in gufo_classes:
                # punning: cls는 SubClassOf로 genus를 특수화하면서 동시에
                # rdf:type으로 gufo 메타타입을 갖는다. owlready2의 .is_a는
                # 둘을 구분하지 않고 합쳐 보여주므로(punning 실험으로 확인),
                # classify()가 raw triple로 따로 걸러낸다.
                onto._add_obj_triple_spo(cls.storid, rdf_type,
                                         gufo_classes[stereo].storid)

        for group in disjoint_groups or []:
            unknown = [n for n in group if n not in classes]
            if unknown:
                raise SerializationError(
                    f"disjoint group references unknown classes: {unknown!r}")
            AllDisjoint([classes[n] for n in group])

    return world, onto, classes


def _is_reportable_class(x) -> bool:
    """보고 가능한 도메인 명명 클래스인가 — 익명 제약식·Thing·Nothing·gUFO
    조상을 제외한다. parents(is_a)와 equivalence 그룹 수집이 같은 위생 규칙을
    공유하도록 술어를 한 곳에 둔다(중복 필터 제거 + 재사용)."""
    return (hasattr(x, "name") and x is not Thing and x is not Nothing
            and not getattr(x, "iri", "").startswith(GUFO_NS))


def _connected_groups(adj: Dict[str, set]) -> List[List[str]]:
    """무방향 인접에서 크기>1 연결요소를 정렬해 반환 — 파생 동치의 전이 폐포.
    owlready2의 INDIRECT_equivalent_to는 gUFO import 시 명명 클래스를
    누락하므로(실험 확인) 직접 equivalent_to 간선을 모아 여기서 병합한다."""
    seen: set = set()
    groups: List[List[str]] = []
    for start in adj:
        if start in seen:
            continue
        stack, comp = [start], []
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            comp.append(n)
            stack.extend(adj[n] - seen)
        if len(comp) > 1:
            groups.append(sorted(comp))
    return sorted(groups)


def classify(world, onto) -> Dict[str, Any]:
    """HermiT 실행 → 유도된 계층·stereotype 펀닝·unsatisfiable 목록 반환.

    hierarchy는 SubClassOf만 담는다(기존 계약 불변). stereotype 펀닝
    (rdf:type)은 raw triple로 별도 추출한다 — owlready2는 클래스 엔티티의
    rdf:type과 rdfs:subClassOf를 .is_a 하나로 합쳐 보여주므로, 메타타입을
    거기 섞으면 "Child ⊑ gufo:Phase"처럼 보여 subsumption과 meta-typing이
    혼동된다(punning 실험으로 확인).
    """
    with onto:
        sync_reasoner(world, infer_property_values=False, debug=0)

    gufo_storid_to_label = {}
    for gufo_name in _GUFO_STEREOTYPE_CLASSES.values():
        gufo_cls = world[GUFO_NS + gufo_name]
        if gufo_cls is not None:
            gufo_storid_to_label[gufo_cls.storid] = gufo_name
    gufo_storids = set(gufo_storid_to_label)

    hierarchy: Dict[str, List[str]] = {}
    stereotypes: Dict[str, str] = {}
    unsat: List[str] = []
    equiv_adj: Dict[str, set] = {}
    # onto.classes()는 이 온톨로지에 선언된 클래스만 — import된 gUFO
    # 클래스는 애초에 순회에 없다. 단 punning 병합 때문에 gUFO 클래스가
    # 부모 목록(is_a)에는 나타나므로 네임스페이스로 걸러낸다 (reasoner가
    # gufo:Phase ⊑ gufo:AntiRigidType 전파로 5종 밖의 gUFO 조상도 추가함).
    for cls in onto.classes():
        # ponytail: raw triple 조회(_get_obj_triples_spo_spo)를 쓴다. build에서
        # rdf:type을 raw triple로 주입했으므로 metaclass(type(cls))는 여전히
        # owlready2 ThingClass이고 gufo 메타타입을 노출하지 않는다(실험 확인).
        # .is_a는 rdf:type과 subClassOf를 합쳐 subsumption과 혼동된다. 따라서
        # 이 low-level 접근자가 정확한 조회 경로다 — owlready2가 내부에서
        # 표준으로 쓰는 API이며, 대체 시 위 두 제약을 먼저 확인할 것.
        type_targets = {o for _, _, o in
                        onto._get_obj_triples_spo_spo(cls.storid, rdf_type, None)}
        hit = type_targets & gufo_storids
        if hit:
            stereotypes[cls.name] = gufo_storid_to_label[next(iter(hit))]
        parents = sorted(
            p.name for p in cls.is_a
            if _is_reportable_class(p) and p.name != cls.name
        )
        equiv = list(cls.equivalent_to)
        is_unsat = Nothing in cls.is_a or Nothing in equiv
        if is_unsat:
            unsat.append(cls.name)
        else:
            # 파생 동치 간선 수집 (리뷰 발견 A·B). 직접 equivalent_to에서
            # 명명 클래스만 무방향 간선으로 모아 뒤에서 연결요소로 병합한다.
            # unsat(≡Nothing)는 서로 동치로 얽히므로 제외해 unsatisfiable과
            # 축을 분리한다(Nothing 동치는 unsatisfiable이 이미 보고).
            for x in equiv:
                if _is_reportable_class(x):
                    equiv_adj.setdefault(cls.name, set()).add(x.name)
                    equiv_adj.setdefault(x.name, set()).add(cls.name)
        hierarchy[cls.name] = parents
    equivalence_groups = _connected_groups(equiv_adj)
    # gUFO 경로에서 HermiT가 동치류의 SubClassOf를 대표에만 부여해 나머지
    # 멤버의 부모가 유실된다(적대 검증 발견 #1, HEAD부터 있던 기존 결함).
    # A≡B이면 B의 상위는 A의 상위다 — 그룹 부모 합집합으로 복원한다.
    # 그룹 자신은 제외해 별칭이 부모로 새지 않게 한다(펼치기 반려 결정 유지).
    for group in equivalence_groups:
        merged = sorted({p for m in group for p in hierarchy[m]} - set(group))
        for m in group:
            hierarchy[m] = merged
    return {"hierarchy": hierarchy, "unsatisfiable": sorted(unsat),
            "stereotypes": stereotypes,
            "equivalence_groups": equivalence_groups,
            # old client가 hierarchy만 읽어도 "이 결과를 그대로 믿으면 위험"을
            # 알 수 있는 얇은 경보등 (파생 동치가 하나라도 있으면 True).
            "has_nontrivial_equivalences": bool(equivalence_groups)}


def is_subclass_of(onto, child_name: str, parent_name: str) -> bool:
    """분류 후: child ⊑ parent (전이 포함) 인가.

    ponytail: gUFO 메타타입 조회에는 쓰지 말 것 — onto[name]은 도메인
    네임스페이스만 찾으므로 "Phase" 같은 gUFO 이름은 unknown class가 되고,
    설령 도메인 개념이 같은 이름이어도 punning 조상과 섞인다. 메타타입은
    classify()의 stereotypes로 조회하라.
    """
    if not isinstance(child_name, str) or not isinstance(parent_name, str):
        raise SerializationError(
            f"class names must be str: {child_name!r}/{parent_name!r}")
    child = onto[child_name]
    parent = onto[parent_name]
    if child is None or parent is None:
        raise SerializationError(f"unknown class: {child_name}/{parent_name}")
    return parent in child.ancestors()


# gUFO 구조 제약 (SHACL). Phase/Role은 anti-rigid라 rigid Kind의 특수화가
# 필요하다는 gUFO 모델링 규칙을 reasoner 실행 *전에* 구조로 검사한다.
_GUFO_SHAPES = Path(__file__).parent / "data" / "gufo_shapes.ttl"


def validate_gufo(world, onto) -> Dict[str, Any]:
    """pyshacl로 gUFO 구조 제약을 검증한다 — 경고 반환, 흐름 차단 없음.

    build_ontology() 결과를 받아 SHACL shapes(_GUFO_SHAPES)에 대조한다.
    반환: {ok: True, warnings: [{code, detail}...]} — 위반은 경고이지
    에러가 아니다(점진 도입). pyshacl 미설치면 PYSHACL_UNAVAILABLE 경고
    하나로 알리고 통과시킨다. ponytail: 추후 서버 파이프라인에 내장해
    fail-closed로 올릴 여지를 둔 별도 함수.
    """
    try:
        import pyshacl
    except ImportError:
        return {"ok": True, "warnings": [
            {"code": "PYSHACL_UNAVAILABLE",
             "detail": "pyshacl 미설치 — gUFO 구조 검증 생략 "
                       "(pip install conceptgate-mcp[shacl])"}]}
    if not _GUFO_SHAPES.exists():
        return {"ok": True, "warnings": [
            {"code": "SHAPES_MISSING",
             "detail": f"{_GUFO_SHAPES} 없음 — gUFO 구조 검증 생략"}]}

    # owlready2의 rdflib 브리지는 graph-aware store가 아니라 pyshacl이
    # 직접 못 받는다 — 일반 Graph로 트리플을 복사해 넘긴다.
    import rdflib
    data_graph = rdflib.Graph()
    for triple in world.as_rdflib_graph():
        data_graph.add(triple)
    conforms, _, results_text = pyshacl.validate(
        data_graph, shacl_graph=str(_GUFO_SHAPES), inference="none")
    warnings = []
    if not conforms:
        warnings.append({"code": "GUFO_SHAPE_VIOLATION",
                         "detail": results_text.strip()[:2000]})
    return {"ok": True, "warnings": warnings}
