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

import cg_owl


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
