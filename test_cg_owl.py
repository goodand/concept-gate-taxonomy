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
