#!/usr/bin/env python3
"""Semantic regression tests — 2026-07-12 gUFO 정합 수정을 계약으로 고정.

배경 (adversarial-verification-research-agenda.md):
  R1  기존 identity 규칙이 방향이 반대라 gUFO 표준 패턴
      Category(-I) -> Kind(+I)를 거부했다.
  R3  category 문자열 동일성 규칙이 Kind->Role 같은 유효 specialization을 거부했다.
  R6  material_of가 essential_feature로 오매핑되어 있었다 (Winston stuff-object는 has-a).

실행: python3 -m pytest test_semantic_regressions.py -q  (또는 python3 직접 실행)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from conceptgate import concept_gate_v7 as cg


def _run(concepts_dict):
    raw = json.dumps(concepts_dict, ensure_ascii=False)
    concepts, rep = cg.ParseGate.parse(raw)
    assert rep.passed, f"ParseGate failed: {[r.message for r in rep.failures]}"
    return cg.ConceptPipeline().run([concepts])


def _ontoclean_failures(out):
    return [
        g for r in out["all_reports"][0] for g in getattr(r, "failures", [])
        if g.gate_name == "OntoClean Meta Gate"
    ]


def _mk(name, feats, category, rigidity, identity, unity="non_unity",
        dependence="independent"):
    return {
        "name": name,
        "ontoclean": {"category": category, "rigidity": rigidity,
                      "identity": identity, "unity": unity,
                      "dependence": dependence},
        "features": [{"feature": f, "type": "essential_feature",
                      "evidence": f"{f} 근거"} for f in feats],
    }


# ── R1: gUFO Category -> Kind 는 유효해야 한다 ──────────────────────────

def test_r1_category_parent_can_subsume_kind_child():
    """gUFO: 'PhysicalObject may be considered a gufo:Category, encompassing cars'."""
    out = _run({"concepts": [
        _mk("PhysicalObject", ["물리적존재"], "category", "rigid",
            "does_not_supply_identity"),
        _mk("Car", ["물리적존재", "차량"], "kind", "rigid",
            "supplies_identity", unity="unified_whole"),
    ]})
    assert out["status"] == "PASS", f"status={out['status']}"
    assert dict(out["result"]["dag"]) == {"PhysicalObject": ["Car"]}
    assert not _ontoclean_failures(out)


# ── R2: 수정된 identity 방향 — +I 부모가 -I 자식을 subsume하면 위반 ────────

def test_r2_identity_carrying_parent_cannot_subsume_non_identity_child():
    out = _run({"concepts": [
        _mk("사람", ["사람"], "kind", "rigid", "supplies_identity",
            unity="unified_whole"),
        _mk("무정체", ["사람", "추가"], "role", "anti_rigid",
            "does_not_supply_identity", dependence="dependent"),
    ]})
    fails = _ontoclean_failures(out)
    assert any("identity-carrying parent" in g.message for g in fails), \
        f"identity 위반 미검출: {[g.message for g in fails]}"


def test_r2b_old_backwards_rule_is_gone():
    """(-I 부모, +I 자식)은 더 이상 identity 위반이 아니다 (R1이 곧 그 케이스)."""
    out = _run({"concepts": [
        _mk("Entity", ["존재"], "category", "rigid", "does_not_supply_identity"),
        _mk("Person", ["존재", "인격"], "kind", "rigid", "supplies_identity",
            unity="unified_whole"),
    ]})
    fails = _ontoclean_failures(out)
    assert not any("identity" in g.message for g in fails), \
        f"역방향 규칙 잔존: {[g.message for g in fails]}"


# ── R3: UFO stereotype 행렬 — Kind -> Role 허용, Role -> Kind 차단 ────────

def test_r3_kind_parent_role_child_allowed():
    """Person(Kind) -> Student(Role): 유효한 cross-stereotype specialization."""
    out = _run({"concepts": [
        _mk("Person", ["사람"], "kind", "rigid", "carries_identity",
            unity="unified_whole"),
        _mk("Student", ["사람", "재학"], "role", "anti_rigid",
            "carries_identity", dependence="dependent"),
    ]})
    assert out["status"] == "PASS", f"status={out['status']}"
    assert dict(out["result"]["dag"]) == {"Person": ["Student"]}


def test_r3b_role_parent_kind_child_blocked():
    out = _run({"concepts": [
        _mk("Student", ["사람"], "role", "anti_rigid", "carries_identity",
            dependence="dependent"),
        _mk("Person", ["사람", "인격"], "kind", "rigid", "supplies_identity",
            unity="unified_whole"),
    ]})
    fails = _ontoclean_failures(out)
    assert any("category:" in g.message for g in fails) or \
           any("rigidity:" in g.message for g in fails), \
        f"Role->Kind 차단 실패: {[g.message for g in fails]}"


# ── R4: free-form category 불일치는 기존대로 차단 (M2 계약과 동일 방향) ────

def test_r4_freeform_category_mismatch_still_blocked():
    out = _run({"concepts": [
        _mk("트랜스포머", ["모델"], "model_architecture", "rigid",
            "supplies_identity", unity="unified_whole"),
        _mk("어텐션", ["모델", "계산"], "mechanism", "rigid",
            "supplies_identity", unity="unified_whole"),
    ]})
    fails = _ontoclean_failures(out)
    assert any("category:" in g.message for g in fails)


# ── R6: material_of 는 has-a (structural_composition) ─────────────────────

def test_r6_material_of_maps_to_structural():
    from conceptgate.cg_partwhole import hint_to_feature_type
    assert hint_to_feature_type("material_of") == "structural_composition"


def test_r6b_material_feature_not_in_isa_dag():
    """재료 feature(structural + material_of hint)는 is-a DAG에 불참."""
    out = _run({"concepts": [
        {"name": "칼", "features": [
            {"feature": "도구", "type": "essential_feature",
             "evidence": "자르는 데 쓰는 도구이다"},
            {"feature": "철", "type": "structural_composition",
             "evidence": "철을 재료로 만든다", "relation_hint": "material_of"},
        ]},
        {"name": "부엌칼", "features": [
            {"feature": "도구", "type": "essential_feature",
             "evidence": "자르는 데 쓰는 도구이다"},
            {"feature": "조리용", "type": "essential_feature",
             "evidence": "조리 목적에 사용한다"},
        ]},
    ]})
    assert out["status"] == "PASS", f"status={out['status']}"
    # 철(재료)은 essential이 아니므로 칼의 essential은 {도구} — 부엌칼이 subsume됨
    assert dict(out["result"]["dag"]) == {"칼": ["부엌칼"]}


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
