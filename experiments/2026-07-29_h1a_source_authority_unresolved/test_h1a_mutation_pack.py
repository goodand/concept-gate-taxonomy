"""Tests for the blinded reviewer mutation pack -- Q13.5 condition 11.

Two properties decide whether this is a real capability check or a ritual:

  - every mutation must actually change the policy graph
    (`test_every_mutation_is_a_real_defect`), or a reviewer would be credited
    or faulted for noticing nothing;
  - "always report a defect" must FAIL
    (`test_flagging_everything_does_not_qualify`), which is what the clean
    packets are for.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_mutation_pack_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


mp = _load("mp", "_h1a_mutation_pack.py")
audit = _load("audit", "_h1a_policy_audit.py")
sc = _load("sc", "_h1a_semantic_compiler.py")
cap = _load("cap", "_h1a_compiler_capability.py")
contract = _load("contract", "_h1a_contract.py")

PROVEN = cap.proven_families()
TPL = contract.load_h1a_native_template()
RENDERED = {
    "kept": contract.render_arm(TPL, "PROHIBITION_KEPT"),
    "removed": contract.render_arm(TPL, "PROHIBITION_REMOVED"),
}
SCOPES = {
    "reviewer_a": mp.SCOPE_TARGET_AXIS,
    "reviewer_b": mp.SCOPE_REFERENTIAL,
    "reviewer_c": mp.SCOPE_EVIDENCE_SCOPE,
}


# --- the mutations must be real -------------------------------------------

def test_every_mutation_is_a_real_defect():
    """A mutation that leaves the audit unchanged tests nothing."""
    results = mp.verify_mutations_are_real(RENDERED, audit, PROVEN)
    inert = sorted(mid for mid, r in results.items() if not r["changed_the_graph"])
    assert not inert, f"these mutations do not change the policy graph: {inert}"


def test_the_target_axis_mutations_are_target_critical():
    """A residual prohibition in REMOVED is the defect that made the first
    cohort non-identifying; it must escalate, not merely be noted."""
    results = mp.verify_mutations_are_real(RENDERED, audit, PROVEN)
    assert results["M1_residual_target_prohibition"]["target_critical"]
    assert results["M2_residual_prohibition_in_english"]["target_critical"]


def test_a_mutation_whose_anchor_vanished_refuses_rather_than_no_ops():
    """If the prompt drifts from what the pack was written against, a silent
    no-op would make the reviewer check measure nothing."""
    with pytest.raises(mp.MutationPackError, match="mutation target not found"):
        mp.MUTATIONS["M6_conflict_to_defer_hard_mapping"]["apply"](
            "a prompt with none of the expected sentences")


def test_the_audit_catches_a_reintroduced_dangling_reference():
    """Regression for the gap the reality check exposed: `compare()` ignored
    sec 9.3's structural items entirely, so M3 produced no finding at all."""
    mutated = mp.MUTATIONS["M3_dangling_reference"]["apply"](RENDERED["removed"])
    report = audit.audit_arm(mutated, "removed", proven_families=PROVEN)
    structural = [f for f in report["findings"] if f["kind"] == audit.STRUCTURAL_DEFECT]
    assert any(f["structural_item"] == sc.DANGLING_REFERENCE for f in structural)


def test_the_audit_catches_the_reverted_ambiguous_axis_wording():
    """Q13.1 renamed the axis because 'source order' covers the target axis
    too. Reverting it leaves the policy 'present', so presence alone misses
    it -- it needs its own structural finding."""
    mutated = mp.MUTATIONS["M4_presentation_order_widened"]["apply"](RENDERED["removed"])
    report = audit.audit_arm(mutated, "removed", proven_families=PROVEN)
    assert any(f.get("structural_item") == sc.AMBIGUOUS_AXIS_PHRASING
               for f in report["findings"])
    clean = audit.audit_arm(RENDERED["removed"], "removed", proven_families=PROVEN)
    assert not any(f.get("structural_item") == sc.AMBIGUOUS_AXIS_PHRASING
                   for f in clean["findings"])


# --- blinding -------------------------------------------------------------

def test_packets_carry_no_marker_of_whether_they_are_mutated():
    packets, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    for packet in packets:
        assert set(packet) == {
            "packet_id", "reviewer_id", "declared_scope", "arm", "rendered_prompt"}
        assert "mutation" not in str(packet["packet_id"]).lower()
    assert set(key) == {p["packet_id"] for p in packets}


def test_every_reviewer_gets_an_in_scope_mutation_and_a_clean_packet():
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    for reviewer, scope in SCOPES.items():
        mine = [e for e in key.values() if e["reviewer_id"] == reviewer]
        mutated = [e for e in mine if e["mutation_id"]]
        clean = [e for e in mine if e["mutation_id"] is None]
        assert mutated and clean, reviewer
        assert all(mp.MUTATIONS[e["mutation_id"]]["scope"] == scope for e in mutated)


def test_a_reviewer_with_no_mutations_in_scope_is_refused(monkeypatch):
    """Unreachable with the current pack -- every scope has mutations -- so the
    branch is exercised by emptying the pack rather than left unproven. A
    reviewer whose scope has nothing to detect cannot be measured, and
    silently qualifying them would be the failure this check exists to stop."""
    monkeypatch.setattr(mp, "MUTATIONS", {})
    with pytest.raises(mp.MutationPackError, match="no mutations"):
        mp.build_assignment(RENDERED, {"r": mp.SCOPE_DECISION_MAPPING}, seed="s")


def test_clean_packets_cannot_be_switched_off():
    with pytest.raises(mp.MutationPackError, match="at least one clean packet"):
        mp.build_assignment(RENDERED, SCOPES, seed="s1", clean_packets=0)


def test_unknown_scope_is_refused():
    with pytest.raises(mp.MutationPackError, match="unknown scope"):
        mp.mutations_for_scope("not_a_scope")


# --- scoring --------------------------------------------------------------

def _answers(key, reviewer, *, flag):
    """flag(entry) -> bool, for building a reviewer's reported findings."""
    return {pid: flag(e) for pid, e in key.items() if e["reviewer_id"] == reviewer}


def test_a_reviewer_who_detects_in_scope_and_stays_quiet_on_clean_qualifies():
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    perfect = _answers(key, "reviewer_a", flag=lambda e: e["mutation_id"] is not None)
    result = mp.score_reviewer("reviewer_a", perfect, key)
    assert result["qualified"] is True
    assert result["approval_counts_toward_freeze"] is True
    assert result["detected"] and not result["false_positives"]


def test_flagging_everything_does_not_qualify():
    """The reason clean packets exist. Without them this strategy wins and the
    check measures nothing."""
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    always = _answers(key, "reviewer_a", flag=lambda e: True)
    result = mp.score_reviewer("reviewer_a", always, key)
    assert result["qualified"] is False
    assert result["false_positives"]


def test_missing_every_mutation_does_not_qualify():
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    silent = _answers(key, "reviewer_a", flag=lambda e: False)
    result = mp.score_reviewer("reviewer_a", silent, key)
    assert result["qualified"] is False
    assert result["missed"]
    assert result["approval_counts_toward_freeze"] is False


def test_unanswered_packets_disqualify():
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    partial = _answers(key, "reviewer_a", flag=lambda e: e["mutation_id"] is not None)
    partial.pop(sorted(partial)[0])
    result = mp.score_reviewer("reviewer_a", partial, key)
    assert result["qualified"] is False
    assert result["unanswered_packets"]


def test_scoring_an_unassigned_reviewer_is_refused():
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    with pytest.raises(mp.MutationPackError, match="no packets assigned"):
        mp.score_reviewer("nobody", {}, key)


def test_the_verdict_carries_its_freeze_consequence():
    """Q13.5's consequence must travel with the verdict, not be remembered
    separately between here and the freeze decision."""
    _, key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    result = mp.score_reviewer(
        "reviewer_b", _answers(key, "reviewer_b", flag=lambda e: False), key)
    assert result["approval_counts_toward_freeze"] is False
    assert "does not count as freeze approval" in result["note"]


def test_assignment_is_reproducible_from_the_seed():
    a_packets, a_key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    b_packets, b_key = mp.build_assignment(RENDERED, SCOPES, seed="s1")
    assert [p["packet_id"] for p in a_packets] == [p["packet_id"] for p in b_packets]
    assert a_key == b_key

    c_packets, _ = mp.build_assignment(RENDERED, SCOPES, seed="s2")
    assert [p["packet_id"] for p in a_packets] != [p["packet_id"] for p in c_packets]
