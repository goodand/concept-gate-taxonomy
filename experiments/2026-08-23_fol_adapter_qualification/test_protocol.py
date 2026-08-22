"""FOL adapter 자격 게이트 — 기록 PASS + 라이브 재현 + 3중 코드 결박.

SBN판과 동형이되 pin이 셋이다: adapter·cg_ir·**비교층(canonical core)** —
항목 8의 desugar 수렴이 비교층 코드를 경유하므로 그것이 바뀌어도 자격은
실효한다(D-23 §13).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_fol_qualification import (  # noqa: E402
    PINNED, SPEC_PATH, run_qualification, source_sha256)

RULED_ITEMS = ("syntax_parse", "alpha_rename_invariance",
               "quantifier_reordering_negative_control",
               "binding_preservation", "deterministic_replay",
               "output_schema_validity", "closed_form_preservation",
               "FOL_definitional_lowering_correctness",
               "scope_order_and_unsupported_negative_discrimination")


def _spec() -> dict:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def test_items_are_exactly_the_nine_ruled_items_in_order():
    assert tuple(i["item_id"] for i in _spec()["items"]) == RULED_ITEMS


def test_item_nine_carries_all_four_forbidden_operators():
    by_id = {i["item_id"]: i for i in _spec()["items"]}
    refusals = [c["fol"] for c in by_id[RULED_ITEMS[-1]]["checks"]
                if c["kind"] == "adapt_refused"]
    assert sum(1 for f in refusals for op in "∨=↔⊕" if op in f) >= 4


def test_recorded_state_is_pass_with_all_items():
    spec = _spec()
    assert spec["qualification_state"] == "PASS", (
        "자격 미실행·미기록 또는 실패 — FOLIO fixture 동결 착수 금지")
    assert len(spec["results"]) == len(RULED_ITEMS)
    assert all(r["item_pass"] for r in spec["results"])


def test_qualification_reproduces_as_pass_live():
    outcome = run_qualification()
    assert outcome["state"] == "passed", outcome["failures"]


def test_recorded_code_hashes_match_live_modules():
    prov = _spec()["provenance"]
    for key, path in PINNED:
        assert prov[key] == source_sha256(path), (
            f"{path.name}이 자격 시점과 다르다 — 재자격 전까지 무효")
