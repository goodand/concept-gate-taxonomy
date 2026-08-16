"""Tests for the H1a capability diagnostics -- D-H1a-14/15 (Q14=E, Q15=G).

The controls are NON-BLOCKING: they never grant or withhold permission to run
the confirmatory cohort. Two properties are load-bearing and each has a test
that fails first if it is undone:

  - `cohort_freeze` must never again become a verdict this module issues
    (`test_cohort_freeze_is_a_pointer_not_a_verdict`). A 2026-08-15 amendment
    and the pre-ruling code both emitted allowed/blocked here; the ruling
    assigned that authority to the identification contract instead.
  - the two controls must stay symmetric (`test_the_two_controls_are_treated
    _symmetrically`). Q15=G rejected privileging either one, and the failure
    modes are mirror images: QF-SELECT fail -> floor, QF-DEFER fail -> ceiling.

Synthetic trial outputs only -- QF-SELECT has a real fixture
(`fixture_qf_select.json`); QF-DEFER has no repo-grounded material (Q14) and
per Q14.1 the confirmatory fixture must not be reused to manufacture one.
Scoring is pinned independently of fixture availability, per this folder's
convention of committing scorers before any trial data exists.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_qualification_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


qual = _load("qual", "_h1a_qualification.py")


def _select_output(evidence_id: str = "ev1") -> dict:
    return {
        "decision": "select_type", "selected_type": "essential_feature",
        "cited_evidence_ids": [evidence_id], "rationale": "test",
    }


def _defer_output() -> dict:
    return {
        "decision": "defer", "selected_type": None,
        "cited_evidence_ids": [], "rationale": "test",
    }


def _invalid_output() -> dict:
    return {"decision": "select_type", "selected_type": None,
            "cited_evidence_ids": [], "rationale": "test"}


PASSING_SELECT = [_select_output()] * 5
PASSING_DEFER = [_defer_output()] * 5
FAILING_SELECT = [_select_output()] * 3 + [_invalid_output()] * 2   # 0.6
FAILING_DEFER = [_defer_output()] * 3 + [_select_output()] * 2      # 0.6


def _diag(result: dict, control: str) -> dict:
    return result["capability_diagnostics"][control]


# --- the separation of authority the ruling installed ---------------------

def test_cohort_freeze_is_a_pointer_not_a_verdict():
    """The load-bearing regression. Before D-H1a-14/15 this module emitted
    `cohort_freeze: allowed|blocked` -- a verdict no freeze gate ever read
    (`_h1a_policy.assert_freezable` has never referenced qualification).
    The ruling assigned freeze to the identification contract, so this field
    may only name its owner."""
    for kwargs in (
        {"select_outputs": PASSING_SELECT, "defer_outputs": PASSING_DEFER},
        {"select_outputs": FAILING_SELECT, "defer_outputs": FAILING_DEFER},
        {"select_outputs": PASSING_SELECT},
        {},
    ):
        result = qual.score_qualification(**kwargs)
        assert result["cohort_freeze"] == {"determined_by": "identification_contract"}
        assert result["cohort_freeze"] not in ("allowed", "blocked")


def test_no_control_outcome_changes_the_freeze_field():
    """Stronger form: the freeze field is invariant across every combination
    of control outcomes. If any branch ever makes it vary, the coupling is
    back."""
    freeze_values = {
        str(qual.score_qualification(select_outputs=s, defer_outputs=d)["cohort_freeze"])
        for s in (PASSING_SELECT, FAILING_SELECT, None)
        for d in (PASSING_DEFER, FAILING_DEFER, None)
    }
    assert len(freeze_values) == 1, freeze_values


# --- Q15=G: the two controls are symmetric --------------------------------

def test_the_two_controls_are_treated_symmetrically():
    """Q15=G: `Role(QF_SELECT) = Role(QF_DEFER)`. Failing one must produce
    the mirror image of failing the other -- same structure, opposite
    saturation direction. An asymmetry here would re-encode exactly what the
    ruling rejected."""
    select_failed = qual.score_qualification(
        select_outputs=FAILING_SELECT, defer_outputs=PASSING_DEFER)
    defer_failed = qual.score_qualification(
        select_outputs=PASSING_SELECT, defer_outputs=FAILING_DEFER)

    assert _diag(select_failed, "qf_select")["status"] == qual.DIAGNOSTIC_FAILED
    assert _diag(defer_failed, "qf_defer")["status"] == qual.DIAGNOSTIC_FAILED

    # same keys on both sides -- no control carries extra machinery
    assert set(_diag(select_failed, "qf_select")) == set(_diag(defer_failed, "qf_defer"))

    # opposite risk directions
    assert _diag(select_failed, "qf_select")["observed_risk"] == "floor_susceptibility"
    assert _diag(defer_failed, "qf_defer")["observed_risk"] == "ceiling_susceptibility"

    # and the interpretation block has the same shape either way
    assert set(select_failed["interpretation"]) == set(defer_failed["interpretation"])


def test_either_control_can_be_unavailable():
    """The signature must not privilege one control. Q14 happens to be about
    QF-DEFER, but nothing in the contract may assume that."""
    only_defer = qual.score_qualification(defer_outputs=PASSING_DEFER)
    assert _diag(only_defer, "qf_select")["status"] == qual.MATERIAL_UNAVAILABLE
    assert only_defer["diagnostic_summary"]["floor_risk_independently_checked"] is False
    assert only_defer["diagnostic_summary"]["ceiling_risk_independently_checked"] is True


# --- both pass ------------------------------------------------------------

def test_both_passing_weakens_both_saturation_explanations():
    result = qual.score_qualification(
        select_outputs=PASSING_SELECT, defer_outputs=PASSING_DEFER)
    summary = result["diagnostic_summary"]
    assert summary["select_capability_observed"] is True
    assert summary["defer_capability_observed"] is True
    assert summary["floor_risk_independently_checked"] is True
    assert summary["ceiling_risk_independently_checked"] is True
    assert "interpretation" not in result
    assert "unavailable_diagnostics" not in result


def test_passes_at_exactly_the_required_rate_boundary():
    """0.80 of 5 is 4/5 -- the boundary itself must pass (>=, not >)."""
    result = qual.score_qualification(
        select_outputs=[_select_output()] * 4 + [_invalid_output()],
        defer_outputs=PASSING_DEFER)
    assert _diag(result, "qf_select")["rate"] == 0.8
    assert _diag(result, "qf_select")["status"] == qual.DIAGNOSTIC_PASSED


# --- failure: bounds interpretation, does not invalidate a real effect ----

def test_a_failed_diagnostic_limits_null_reporting_but_not_a_nonzero_effect():
    result = qual.score_qualification(
        select_outputs=PASSING_SELECT, defer_outputs=FAILING_DEFER)
    interpretation = result["interpretation"]
    assert interpretation["null_effect_requires_limitation"] is True
    assert interpretation["nonzero_effect_invalidated"] is False
    assert interpretation["affected_controls"] == [qual.QF_DEFER]


def test_the_q13_3_approved_sentence_is_carried_verbatim():
    """D-H1a-14/15 restated this obligation but did not retract the sentence.
    Rewording approved text to match new vocabulary is the F6 defect."""
    result = qual.score_qualification(
        select_outputs=FAILING_SELECT, defer_outputs=PASSING_DEFER)
    assert result["interpretation"]["approved_reporting_sentence"] == (
        "A failed qualification gate must not be reported as evidence "
        "of a null treatment effect."
    )


# --- Q14.2: unavailable is not failure ------------------------------------

def test_material_unavailable_is_recorded_as_unknown_not_as_failure():
    """Q14.2: `material_unavailable`에서 피험자 능력에 대한 부정적 결론을
    내리면 안 된다. The current real state for QF-DEFER."""
    result = qual.score_qualification(select_outputs=PASSING_SELECT)
    defer = _diag(result, "qf_defer")
    assert defer["status"] == qual.MATERIAL_UNAVAILABLE
    assert defer["subject_verdict"] is None
    assert defer["implies_subject_failure"] is False
    assert result["diagnostic_summary"]["defer_capability_observed"] == "unknown"
    assert result["unavailable_diagnostics"]["treat_as_failure"] is False
    assert result["unavailable_diagnostics"]["record_as_unknown"] is True
    # an un-run control must not be reported as a failed one
    assert "interpretation" not in result


def test_unavailable_and_failed_never_collapse():
    """The two must stay distinguishable in the record -- Q14.2 forbids
    giving them one shared category."""
    unavailable = _diag(qual.score_qualification(select_outputs=PASSING_SELECT), "qf_defer")
    failed = _diag(
        qual.score_qualification(select_outputs=PASSING_SELECT, defer_outputs=FAILING_DEFER),
        "qf_defer")
    assert unavailable["status"] != failed["status"]
    assert unavailable["implies_subject_failure"] is False
    assert failed["implies_subject_failure"] is True


def test_the_retired_hard_gate_category_is_gone():
    """`floor_or_ceiling_failure` named a gate outcome that blocked the
    cohort. Under the ruling nothing blocks, so re-adding it would smuggle
    the retired semantics back in."""
    assert not hasattr(qual, "FLOOR_OR_CEILING_FAILURE")
    result = qual.score_qualification(
        select_outputs=FAILING_SELECT, defer_outputs=FAILING_DEFER)
    assert "result_category" not in result


# --- precondition guards -------------------------------------------------

def test_refuses_the_wrong_number_of_trials():
    with pytest.raises(qual.QualificationContractError, match="expected exactly 5"):
        qual.score_qualification(select_outputs=[_select_output()] * 4)


def test_refuses_an_unknown_control_name():
    with pytest.raises(qual.QualificationContractError, match="unknown control"):
        qual._score_one_control("QF-BOGUS", PASSING_SELECT)


def test_invalid_outputs_count_as_misses_not_as_excluded():
    """An invalid (malformed) output must not be dropped from the
    denominator -- that would let a subject dodge the diagnostic by producing
    garbage instead of a wrong-but-valid answer."""
    import _coder
    result = qual.score_qualification(
        select_outputs=[_select_output()] * 4 + [_invalid_output()])
    select = _diag(result, "qf_select")
    assert select["n"] == 5
    assert select["categories"].count(_coder.INVALID) == 1
