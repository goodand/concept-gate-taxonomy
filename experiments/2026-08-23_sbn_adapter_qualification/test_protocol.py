"""SBN adapter 자격 게이트 — 기록 PASS + 라이브 재현 + 코드 결박 (D-22 §5-§6).

wikisem판(2026-08-23_o1_adapter_qualification)과 같은 3축: 기록만 보면
드리프트를, 재실행만 보면 미기록을 놓치고, 코드 해시 대조가 자격을 그
코드에 결박한다 — adapter가 바뀌면 재자격 없이는 이 게이트가 실패한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_sbn_qualification import (  # noqa: E402
    PINNED_MODULES, SPEC_PATH, module_source_sha256, run_qualification)

RULED_ITEMS = ("syntax_parse", "comment_invariance",
               "quantifier_reordering_negative_control",
               "binding_preservation", "deterministic_replay",
               "output_schema_validity", "closed_form_preservation",
               "documented_universal_pattern_decode",
               "decode_reencode_round_trip_and_negative_controls")


def _spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_items_are_exactly_the_nine_ruled_items_in_order():
    assert tuple(i["item_id"] for i in _spec()["items"]) == RULED_ITEMS


def test_the_two_new_items_carry_negative_discrimination():
    """D-22 §5: 항목 8·9는 음성 판별 필수 — 일반 부정·빈 restriction·
    바깥 문맥이 ∀로 오인되지 않아야 한다."""
    by_id = {i["item_id"]: i for i in _spec()["items"]}
    ud = by_id["documented_universal_pattern_decode"]["checks"]
    assert sum(1 for c in ud if "forall" in c.get("must_not_contain", [])) >= 2
    rt = by_id["decode_reencode_round_trip_and_negative_controls"]["checks"]
    assert any(c["kind"] == "round_trip" for c in rt)


def test_recorded_state_is_pass_with_all_items():
    spec = _spec()
    assert spec["qualification_state"] == "PASS", (
        "자격이 미실행·미기록이거나 실패 상태 — PMB fixture 동결 착수 금지")
    assert len(spec["results"]) == len(RULED_ITEMS)
    assert all(r["item_pass"] for r in spec["results"])


def test_qualification_reproduces_as_pass_live():
    outcome = run_qualification()
    assert outcome["state"] == "passed", outcome["failures"]


def test_recorded_code_hashes_match_live_modules():
    prov = _spec()["provenance"]
    for name, key in zip(PINNED_MODULES,
                         ("sbn_adapter_source_sha256", "cg_ir_source_sha256")):
        assert prov[key] == module_source_sha256(name), (
            f"{name}이 자격 시점과 다르다 — 재자격 전까지 이 자격은 무효")
