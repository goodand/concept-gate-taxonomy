"""Tests for the independent review protocol -- Q13.5 conditions 11 and 12.

The property that matters: an UNQUALIFIED reviewer's approval must be
discarded mechanically, not weighed. Q13.5 says so in as many words, and the
whole point of encoding the protocol is that "remember to drop it" is exactly
the kind of discipline this repo has watched fail.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_review_protocol_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


proto = _load("proto", "_h1a_review_protocol.py")
mp = _load("mp", "_h1a_mutation_pack.py")

SCOPES = {"RA": mp.SCOPE_TARGET_AXIS, "RB": mp.SCOPE_REFERENTIAL}
SEED = "test-seed"


def _materials():
    return proto.build_review_materials(SCOPES, seed=SEED)


def _perfect_answers(key, reviewer):
    return {pid: e["mutation_id"] is not None
            for pid, e in key.items() if e["reviewer_id"] == reviewer}


def _report(key, reviewer, *, approves=True, findings=None, answers=None):
    return {
        "packet_findings": _perfect_answers(key, reviewer) if answers is None else answers,
        "scope_findings": findings or [],
        "approves_freeze": approves,
    }


# --- condition 11 ---------------------------------------------------------

def test_materials_cover_every_condition_11_requirement():
    materials, _ = _materials()
    for field in ("reviewer_scopes", "rendered_prompt", "expected_policy_graph",
                  "compiler_diff", "mutation_packets"):
        assert materials[field], field


def test_materials_and_answer_key_are_separate_values():
    materials, key = _materials()
    assert "answer" not in str(materials.keys()).lower()
    for packet in materials["mutation_packets"]:
        assert "mutation_id" not in packet


def test_declared_scopes_are_required():
    with pytest.raises(proto.ReviewProtocolError, match="declared reviewer scopes"):
        proto.build_review_materials({}, seed=SEED)


def test_a_reviewer_who_files_no_report_is_refused():
    materials, key = _materials()
    with pytest.raises(proto.ReviewProtocolError, match="filed no report"):
        proto.assess(materials, key, {"RA": _report(key, "RA")})


# --- the load-bearing rule ------------------------------------------------

def test_an_unqualified_reviewers_approval_is_discarded_not_weighed():
    """Q13.5: '이 capability check를 통과하지 않은 리뷰어의 "문제 없음"은
    freeze 승인으로 계산하지 않는다.'"""
    materials, key = _materials()
    blind = {pid: False for pid, e in key.items() if e["reviewer_id"] == "RA"}
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA", approves=True, answers=blind),   # missed everything
        "RB": _report(key, "RB", approves=True),
    })
    assert "RA" in result["unqualified_reviewers"]
    assert "RA" not in result["approvals_counted"]
    assert "RA" in result["approvals_discarded"]
    assert result["condition_11_met"] is False
    assert result["independent_semantic_review_passed"] is False


def test_flagging_every_packet_also_disqualifies():
    materials, key = _materials()
    always = {pid: True for pid, e in key.items() if e["reviewer_id"] == "RA"}
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA", answers=always),
        "RB": _report(key, "RB"),
    })
    assert "RA" in result["unqualified_reviewers"]


def test_all_qualified_and_approving_passes_both_conditions():
    materials, key = _materials()
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA"), "RB": _report(key, "RB")})
    assert result["condition_11_met"] is True
    assert result["condition_12_met"] is True
    assert result["independent_semantic_review_passed"] is True


# --- condition 12 ---------------------------------------------------------

def test_an_unresolved_major_from_a_qualified_reviewer_blocks():
    materials, key = _materials()
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA", findings=[
            {"severity": proto.MAJOR, "summary": "something in scope"}]),
        "RB": _report(key, "RB"),
    })
    assert result["unresolved_blocker_or_major"]
    assert result["condition_12_met"] is False


def test_findings_from_an_unqualified_reviewer_do_not_count_either_way():
    """Symmetry: if their all-clear does not count, neither does their alarm.
    An unmeasured reviewer's judgment is unmeasured in both directions."""
    materials, key = _materials()
    blind = {pid: False for pid, e in key.items() if e["reviewer_id"] == "RA"}
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA", answers=blind, findings=[
            {"severity": proto.BLOCKER, "summary": "from an unqualified reviewer"}]),
        "RB": _report(key, "RB"),
    })
    assert result["unresolved_blocker_or_major"] == []


def test_a_qualified_reviewer_withholding_approval_blocks():
    materials, key = _materials()
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA", approves=False), "RB": _report(key, "RB")})
    assert result["condition_12_met"] is False
    assert result["approvals_counted"]["RA"] is False


def test_the_record_does_not_itself_change_any_freeze_flag():
    """This module reports; a human sets the flag."""
    materials, key = _materials()
    result = proto.assess(materials, key, {
        "RA": _report(key, "RA"), "RB": _report(key, "RB")})
    assert "does not itself change any freeze flag" in result["note"]
