"""adapter 자격 게이트 — 기록 PASS + 라이브 재현 + 코드 결박 (D-21 §18·§20).

Stage 1 test_protocol의 양방향 규율에 셋째 축이 추가된다: 기록된
provenance 해시가 **라이브 모듈**과 일치해야 한다. adapter나 cg_ir이
자격 실행 이후에 바뀌면 이 게이트가 실패한다 — 재자격 없이 낡은 자격을
쓰는 것이 구조적으로 불가능해진다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_adapter_qualification import (  # noqa: E402
    PINNED_MODULES, SPEC_PATH, module_source_sha256, run_qualification)

RULED_ITEMS = ("syntax_parse", "alpha_rename_invariance",
               "quantifier_reordering_negative_control",
               "binding_preservation", "deterministic_replay",
               "output_schema_validity", "closed_form_preservation")


def _spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_items_are_exactly_the_seven_ruled_items_in_ruled_order():
    assert tuple(i["item_id"] for i in _spec()["items"]) == RULED_ITEMS


def test_the_two_new_items_carry_direct_negative_checks():
    """D-21 §20: 마지막 둘은 aggregate가 아니라 직접 음성 테스트."""
    spec = _spec()
    by_id = {i["item_id"]: i for i in spec["items"]}
    assert any(c["kind"] == "adapt_refused"
               for c in by_id["output_schema_validity"]["checks"])
    cf = by_id["closed_form_preservation"]["checks"]
    assert any(c["expected_free"] for c in cf if c["kind"] == "free_vars"), (
        "닫힘 항목에 '열린 것은 열린 채'(과잉 폐쇄 금지) 음성 검사가 없다")


def test_recorded_state_is_pass_with_all_items_recorded():
    spec = _spec()
    assert spec["qualification_state"] == "PASS", (
        "자격이 아직 실행·기록되지 않았거나 실패 상태다 — Stage 2 착수 금지")
    assert len(spec["results"]) == len(RULED_ITEMS)
    assert all(r["item_pass"] for r in spec["results"])


def test_qualification_reproduces_as_pass_live():
    outcome = run_qualification()
    assert outcome["state"] == "passed", outcome["failures"]


def test_recorded_code_hashes_match_live_modules():
    """자격은 그 코드에 결박된다(§18). 불일치 = 자격 실효, 재실행 필요."""
    prov = _spec()["provenance"]
    for name, key in zip(PINNED_MODULES,
                         ("adapter_source_sha256", "cg_ir_source_sha256")):
        assert prov[key] == module_source_sha256(name), (
            f"{name}이 자격 실행 시점과 다르다 — 재자격 전까지 이 자격은 무효")
