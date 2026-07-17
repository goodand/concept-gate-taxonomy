#!/usr/bin/env python3
"""cg_owl 설계 증명 테스트 — owl-serialization-spec.md §6의 3가지.

P1  primitive는 spurious is-a를 막는다 (리뷰 발견 2의 Bird/Airplane 반례 차단)
P2  defined는 계층을 '생성'한다 (Square가 Rectangle·Rhombus 아래로 자동 분류)
P3  모순 개념은 unsatisfiable로 탐지된다

실행에는 Java(HermiT)가 필요 — 없으면 skip.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))


def _java_available() -> bool:
    java = shutil.which("java") or "/opt/homebrew/opt/openjdk/bin/java"
    try:
        subprocess.run([java, "-version"], capture_output=True, timeout=10)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _java_available(),
                                reason="Java(HermiT) 없음")

pytest.importorskip("owlready2", reason="owlready2 미설치 (선택 의존성)")

# owlready2가 java를 찾도록 PATH 보강
import os
os.environ["PATH"] = "/opt/homebrew/opt/openjdk/bin:" + os.environ.get("PATH", "")

from conceptgate import cg_owl


# ── P1: primitive → Bird/Airplane spurious is-a 차단 ─────────────────

def test_p1_primitive_blocks_spurious_subsumption():
    """Bird={날개}, Airplane={날개,제트} — 현행 집합 포함은 Bird→Airplane를
    만들었다. primitive(⊑) 직렬화에서는 어느 방향으로도 유도되지 않아야 한다."""
    world, onto, _ = cg_owl.build_ontology(
        concepts=[
            {"name": "Wing", "definition_kind": "primitive"},
            {"name": "JetEngine", "definition_kind": "primitive"},
            {"name": "Bird", "definition_kind": "primitive",
             "differentia": [
                 {"property": "hasPart", "restriction": "some", "filler": "Wing"}]},
            {"name": "Airplane", "definition_kind": "primitive",
             "differentia": [
                 {"property": "hasPart", "restriction": "some", "filler": "Wing"},
                 {"property": "hasPart", "restriction": "some",
                  "filler": "JetEngine"}]},
        ],
        object_properties=["hasPart"],
    )
    result = cg_owl.classify(world, onto)
    assert not cg_owl.is_subclass_of(onto, "Airplane", "Bird"), \
        "Airplane ⊑ Bird 가 유도되면 발견 2가 재현된 것"
    assert not cg_owl.is_subclass_of(onto, "Bird", "Airplane")
    assert result["unsatisfiable"] == []


# ── P2: defined → Square의 다중 부모 자동 분류 (계층 '생성') ──────────

def test_p2_defined_classes_generate_hierarchy():
    """Rectangle ≡ Parallelogram ⊓ 직각, Rhombus ≡ Parallelogram ⊓ 등변,
    Square ≡ Parallelogram ⊓ 직각 ⊓ 등변.
    reasoner가 Square ⊑ Rectangle 와 Square ⊑ Rhombus 를 스스로 유도해야 한다
    — 어디에도 명시하지 않았다."""
    world, onto, _ = cg_owl.build_ontology(
        concepts=[
            {"name": "Parallelogram", "definition_kind": "primitive"},
            {"name": "Rectangle", "definition_kind": "defined",
             "genus": "Parallelogram",
             "differentia": [
                 {"property": "hasRightAngles", "restriction": "value",
                  "filler": True}]},
            {"name": "Rhombus", "definition_kind": "defined",
             "genus": "Parallelogram",
             "differentia": [
                 {"property": "hasEqualSides", "restriction": "value",
                  "filler": True}]},
            {"name": "Square", "definition_kind": "defined",
             "genus": "Parallelogram",
             "differentia": [
                 {"property": "hasRightAngles", "restriction": "value",
                  "filler": True},
                 {"property": "hasEqualSides", "restriction": "value",
                  "filler": True}]},
        ],
        data_properties=[
            {"name": "hasRightAngles", "functional": True, "range": bool},
            {"name": "hasEqualSides", "functional": True, "range": bool},
        ],
    )
    cg_owl.classify(world, onto)
    assert cg_owl.is_subclass_of(onto, "Square", "Rectangle"), \
        "reasoner가 Square ⊑ Rectangle 를 유도하지 못함"
    assert cg_owl.is_subclass_of(onto, "Square", "Rhombus"), \
        "reasoner가 Square ⊑ Rhombus 를 유도하지 못함 (meet)"
    # 역방향은 없어야 함
    assert not cg_owl.is_subclass_of(onto, "Rectangle", "Square")


# ── P3: 모순 개념 → unsatisfiable 탐지 ───────────────────────────────

def test_p3_contradiction_detected_as_unsatisfiable():
    """disjoint 인 두 genus 를 동시에 갖는 defined 개념은 Nothing 과 동치."""
    world, onto, _ = cg_owl.build_ontology(
        concepts=[
            {"name": "Animal", "definition_kind": "primitive"},
            {"name": "Machine", "definition_kind": "primitive"},
            {"name": "RobotDog", "definition_kind": "defined",
             "genus": "Animal",
             "differentia": [
                 {"restriction": "subClassOf", "filler": "Machine"}]},
        ],
        disjoint_groups=[["Animal", "Machine"]],
    )
    result = cg_owl.classify(world, onto)
    assert "RobotDog" in result["unsatisfiable"], \
        f"모순 미탐지: {result['unsatisfiable']}"


# ── 직렬화 스키마 자체의 방어 (reasoner 불필요) ──────────────────────

def test_schema_rejects_unknown_restriction():
    with pytest.raises(cg_owl.SerializationError):
        cg_owl.build_ontology(concepts=[
            {"name": "X", "definition_kind": "defined",
             "differentia": [{"property": "p", "restriction": "vibes",
                              "filler": "Y"}]}])


def test_schema_rejects_defined_without_definition():
    with pytest.raises(cg_owl.SerializationError):
        cg_owl.build_ontology(concepts=[
            {"name": "X", "definition_kind": "defined"}])


# ── P5: phase stereotype punning (리뷰 발견 4) ───────────────────────

def test_p5_phase_stereotype_emits_rdf_type_and_subclassof():
    """gUFO Phase: Child rdf:type Phase(punning) *그리고* Child SubClassOf
    Person 둘 다 분류 결과에 나타나야 한다 — HANDOFF §5-1 수용기준."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "Person", "definition_kind": "primitive",
         "stereotype": "kind"},
        {"name": "Child", "definition_kind": "primitive",
         "genus": "Person", "stereotype": "phase"},
    ])
    result = cg_owl.classify(world, onto)
    assert result["unsatisfiable"] == []
    assert cg_owl.is_subclass_of(onto, "Child", "Person"), \
        "Child SubClassOf Person이 유도되지 않음"
    assert "Person" in result["hierarchy"]["Child"]
    assert result["stereotypes"].get("Child") == "Phase", \
        "Child rdf:type Phase 펀닝이 분류 결과에 나타나지 않음"
    assert result["stereotypes"].get("Person") == "Kind"
    # gUFO 클래스 자체는 도메인 hierarchy에 노출되지 않는다 (finding 3:
    # 실 gUFO import 후에도 hierarchy는 도메인 SubClassOf만 담는다 —
    # reasoner가 전파하는 gufo:AntiRigidType 등 gUFO 조상도 안 샌다)
    assert "Phase" not in result["hierarchy"]
    assert "Kind" not in result["hierarchy"]
    for parents in result["hierarchy"].values():
        assert not any(p in ("AntiRigidType", "RigidType", "Sortal",
                             "EndurantType") for p in parents), parents
    # owl:imports가 실제로 선언되어 있다
    assert any(o.base_iri.startswith("http://purl.org/nemo/gufo")
               for o in onto.imported_ontologies)


# ── P6: gUFO 공리 발화 증명 (finding 3) ──────────────────────────────

def test_p6_gufo_disjointness_axiom_fires():
    """owl:imports가 장식이 아니다 — gUFO의 Phase⊥Role 공리가 HermiT에서
    실제로 발화하는지 증명한다. P5는 '일관된 입력이 통과한다'만 보이므로,
    import한 gUFO 공리가 reasoner에 정말 닿는지는 모순 입력으로 증명한다.
    공개 스키마는 stereotype이 개념당 하나라 이 모순을 못 만들므로, raw
    triple로 Child에 Phase+Role 이중 punning을 주입한다."""
    from owlready2 import rdf_type, OwlReadyInconsistentOntologyError
    world, onto, classes = cg_owl.build_ontology(concepts=[
        {"name": "Person", "definition_kind": "primitive",
         "stereotype": "kind"},
        {"name": "Child", "definition_kind": "primitive",
         "genus": "Person", "stereotype": "phase"},
    ])
    role = world[cg_owl.GUFO_NS + "Role"]
    assert role is not None, "gUFO Role 클래스가 import되지 않음"
    onto._add_obj_triple_spo(classes["Child"].storid, rdf_type, role.storid)
    with pytest.raises(OwlReadyInconsistentOntologyError):
        cg_owl.classify(world, onto)


# ── P7: unsatisfiable 클래스가 Nothing을 parents로 흘리지 않음 (PR#2 #7) ──

def test_p7_unsatisfiable_class_excludes_nothing_from_parents():
    """C ⊑ A, C ⊑ B, A⊥B → C는 unsatisfiable(is_a에 Nothing)이지만 온톨로지는
    consistent. Nothing이 parents 목록으로 새면 안 된다."""
    world, onto, _ = cg_owl.build_ontology(
        concepts=[
            {"name": "A", "definition_kind": "primitive"},
            {"name": "B", "definition_kind": "primitive"},
            {"name": "C", "definition_kind": "primitive", "genus": "A",
             "differentia": [{"restriction": "subClassOf", "filler": "B"}]},
        ],
        disjoint_groups=[["A", "B"]])
    result = cg_owl.classify(world, onto)
    assert "C" in result["unsatisfiable"]
    assert "Nothing" not in result["hierarchy"].get("C", [])
    assert all("Nothing" not in parents
               for parents in result["hierarchy"].values())


# ── P8: 파생 동치 보고 (리뷰 발견 A·B) ──────────────────────────────

def _sa(name, filler="SelfAttention"):
    """defined 개념 하나 — hasPart.some.<filler> 로만 정의."""
    return {"name": name, "definition_kind": "defined",
            "differentia": [{"property": "hasPart", "restriction": "some",
                             "filler": filler}]}


def test_p8_accidental_equivalence_reported_hierarchy_intact():
    """Encoder ≡ Decoder(동일 정의)는 파생 동치다. equivalence_groups로
    노출되어야 하고, hierarchy는 여전히 '직계 부모'만 담아야 한다 —
    RichEncoder는 부모를 [Decoder]로만 보고(그룹으로 펼치지 않음)."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "SelfAttention", "definition_kind": "primitive"},
        {"name": "FFN", "definition_kind": "primitive"},
        _sa("Encoder"), _sa("Decoder"),
        {"name": "RichEncoder", "definition_kind": "defined",
         "differentia": [
             {"property": "hasPart", "restriction": "some",
              "filler": "SelfAttention"},
             {"property": "hasPart", "restriction": "some", "filler": "FFN"}]},
    ], object_properties=["hasPart"])
    r = cg_owl.classify(world, onto)
    assert ["Decoder", "Encoder"] in r["equivalence_groups"], \
        f"파생 동치 미보고: {r['equivalence_groups']}"
    assert r["has_nontrivial_equivalences"] is True
    # hierarchy는 펼치지 않는다 — 직계 부모 의미 보존 (부모 펼치기 반려)
    assert "Decoder" in r["hierarchy"]["RichEncoder"]
    assert r["unsatisfiable"] == []


def test_p8_transitive_equivalence_single_group():
    """A ≡ B ≡ C — INDIRECT_equivalent_to의 전이 폐포로 한 그룹 3원소.
    (union-find를 직접 짜지 않고 라이브러리가 병합한다는 계약을 고정.)"""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "SelfAttention", "definition_kind": "primitive"},
        _sa("A"), _sa("B"), _sa("C"),
    ], object_properties=["hasPart"])
    r = cg_owl.classify(world, onto)
    assert r["equivalence_groups"] == [["A", "B", "C"]], \
        f"전이 폐포가 한 그룹이 아님: {r['equivalence_groups']}"


def test_p8_equivalence_group_excludes_gufo_and_top():
    """stereotype punning과 동치가 공존해도 그룹엔 도메인 이름만 —
    Thing/Nothing/gUFO(Kind 등)가 섞이면 안 된다(_is_reportable_class 위생)."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "SelfAttention", "definition_kind": "primitive"},
        {**_sa("Encoder"), "stereotype": "kind"},
        {**_sa("Decoder"), "stereotype": "kind"},
    ], object_properties=["hasPart"])
    r = cg_owl.classify(world, onto)
    assert r["equivalence_groups"] == [["Decoder", "Encoder"]]
    flat = {n for g in r["equivalence_groups"] for n in g}
    assert not (flat & {"Thing", "Nothing", "Kind", "SubKind", "Phase",
                        "Role", "Category"}), flat


def test_p8_unsatisfiable_excluded_from_equivalence_groups():
    """C·D 둘 다 unsatisfiable(≡Nothing이라 서로도 동치). 이 축은
    unsatisfiable로만 보고하고 equivalence_groups로 새지 않아야 한다."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "A", "definition_kind": "primitive"},
        {"name": "B", "definition_kind": "primitive"},
        {"name": "C", "definition_kind": "defined", "genus": "A",
         "differentia": [{"restriction": "subClassOf", "filler": "B"}]},
        {"name": "D", "definition_kind": "defined", "genus": "A",
         "differentia": [{"restriction": "subClassOf", "filler": "B"}]},
    ], disjoint_groups=[["A", "B"]])
    r = cg_owl.classify(world, onto)
    assert set(r["unsatisfiable"]) == {"C", "D"}
    assert r["equivalence_groups"] == []
    assert r["has_nontrivial_equivalences"] is False


# ── P9: gUFO 경로에서 동치 멤버의 직계 부모 유실 복원 (적대 검증 발견 #1) ──

def test_p9_gufo_equivalence_members_keep_direct_parents():
    """gUFO import 시 HermiT가 SubClassOf를 동치 대표에만 부여해 나머지
    멤버의 부모가 유실됐다(적대 검증 발견 #1, HEAD부터 있던 기존 결함).
    그룹 부모 합집합 복원 후에는 Encoder·Decoder 둘 다 Block을 직계 부모로
    보고해야 하고, 서로(별칭)는 부모 목록에 나타나면 안 된다."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "Block", "definition_kind": "primitive",
         "stereotype": "category"},
        {"name": "SelfAttn", "definition_kind": "primitive",
         "stereotype": "kind"},
        {"name": "Encoder", "definition_kind": "defined", "genus": "Block",
         "stereotype": "subkind",
         "differentia": [{"property": "hasPart", "restriction": "some",
                          "filler": "SelfAttn"}]},
        {"name": "Decoder", "definition_kind": "defined", "genus": "Block",
         "stereotype": "subkind",
         "differentia": [{"property": "hasPart", "restriction": "some",
                          "filler": "SelfAttn"}]},
    ], object_properties=["hasPart"])
    r = cg_owl.classify(world, onto)
    assert r["equivalence_groups"] == [["Decoder", "Encoder"]]
    assert r["hierarchy"]["Encoder"] == ["Block"], "비대표 멤버 부모 유실 재발"
    assert r["hierarchy"]["Decoder"] == ["Block"]
    # 별칭은 부모가 아니다 (부모 펼치기 반려 결정 유지)
    assert "Decoder" not in r["hierarchy"]["Encoder"]
    assert "Encoder" not in r["hierarchy"]["Decoder"]


# ── P10: quotient 대표 매핑 (의미충실도 리뷰 R3) ─────────────────────

def test_p10_representatives_enable_quotient_folding():
    """동치류를 하나의 노드로 접기 위한 결정적 대표(사전순 최소)를 반환한다.
    equivalence_groups는 정렬돼 있어 g[0]이 대표. 클라이언트가
    representatives로 alias를 접으면 부모 정보가 중복 복제되지 않는다."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "SelfAttn", "definition_kind": "primitive"},
        {"name": "Encoder", "definition_kind": "defined",
         "differentia": [{"property": "hasPart", "restriction": "some",
                          "filler": "SelfAttn"}]},
        {"name": "Decoder", "definition_kind": "defined",
         "differentia": [{"property": "hasPart", "restriction": "some",
                          "filler": "SelfAttn"}]},
    ], object_properties=["hasPart"])
    r = cg_owl.classify(world, onto)
    # 대표는 사전순 최소 = Decoder (D < E), 전원이 같은 대표를 가리킨다
    assert r["representatives"] == {"Decoder": "Decoder", "Encoder": "Decoder"}
    # quotient graph를 만들 수 있다 — alias가 대표 노드로 접힌다
    rep = lambda n: r["representatives"].get(n, n)
    assert rep("Encoder") == rep("Decoder")


def test_p10_representatives_empty_without_equivalence():
    """동치가 없으면 representatives는 빈 맵 — equivalence_groups와 대칭 계약."""
    world, onto, _ = cg_owl.build_ontology(concepts=[
        {"name": "Para", "definition_kind": "primitive"},
        {"name": "Rect", "definition_kind": "defined", "genus": "Para",
         "differentia": [{"property": "r", "restriction": "value",
                          "filler": True}]},
    ], data_properties=[{"name": "r", "functional": True, "range": bool}])
    r = cg_owl.classify(world, onto)
    assert r["representatives"] == {}
    assert r["equivalence_groups"] == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))


# ── P4: 완전 배선 — 자연어 근거 → map_to_owl → HermiT 분류 ──────────

def test_p4_natural_language_to_reasoner_end_to_end():
    """자연어 스냅샷의 span 근거로 typed 제안을 만들고, map_to_owl 검증을
    거쳐 HermiT가 정사각형 ⊑ 직사각형을 스스로 유도한다 — 전 구간 배선."""
    from conceptgate import cg_normalizer as N
    text = ("평행사변형은 사각형이다. 직사각형은 네 각이 직각인 평행사변형이다. "
            "정사각형은 네 변이 같고 네 각이 직각인 평행사변형이다.")
    snap = N.make_snapshot(text)["snapshot"]
    t = snap["text"]
    def sp(p):
        i = t.find(p); return {"start": i, "end": i + len(p)}
    bundle = {"snapshot": snap, "concepts": [
        {"name": "평행사변형", "definition_kind": "primitive"},
        {"name": "직사각형", "definition_kind": "defined",
         "kind_rationale": "본문이 '직각인 평행사변형'으로 정의함",
         "genus": "평행사변형",
         "differentia": [{"property": "직각성", "restriction": "value",
                          "filler": True,
                          "evidence_span": sp("네 각이 직각인 평행사변형")}]},
        {"name": "정사각형", "definition_kind": "defined",
         "kind_rationale": "본문이 '네 변이 같고 직각인 평행사변형'으로 정의함",
         "genus": "평행사변형",
         "differentia": [
             {"property": "직각성", "restriction": "value", "filler": True,
              "evidence_span": sp("네 각이 직각인 평행사변형")},
             {"property": "등변성", "restriction": "value", "filler": True,
              "evidence_span": sp("네 변이 같고")}]},
    ]}
    m = N.map_to_owl(bundle)
    assert m["ok"], m.get("errors")
    world, onto, _ = cg_owl.build_ontology(
        concepts=m["owl"]["concepts"],
        object_properties=m["owl"]["object_properties"],
        data_properties=[{**d, "functional": True, "range": bool}
                         for d in m["owl"]["data_properties"]],
        disjoint_groups=m["owl"]["disjoint_groups"])
    result = cg_owl.classify(world, onto)
    assert result["unsatisfiable"] == []
    assert cg_owl.is_subclass_of(onto, "정사각형", "직사각형"), \
        "HermiT가 정사각형 ⊑ 직사각형을 유도하지 못함"
    # 근거는 전부 L1
    assert all(c["verification_status"] == "source_span_verified"
               for c in m["claims"])
