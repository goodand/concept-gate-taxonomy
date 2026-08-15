"""Tests for the D-H1a-13 Q13.3 qualification gate, AMENDED 2026-08-15
(QF-DEFER demoted to non-blocking -- see PREREGISTRATION_TYPED_SCOPE_COHORT.md
sec 5c and _h1a_qualification.py's module docstring for the full rationale).

Synthetic trial outputs only -- QF-SELECT has a real fixture now
(fixture_qf_select.json); QF-DEFER's material does not exist in this
repository (Q14, sec 5c) and its control is exercised here only via
synthetic outputs to pin the SCORING contract independently of fixture
availability, per this folder's convention of committing scorers before
any trial data exists.
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


# --- both controls pass -----------------------------------------------

def test_gate_passes_when_both_controls_meet_the_required_rate():
    result = qual.score_qualification(
        select_outputs=[_select_output()] * 5,
        defer_outputs=[_defer_output()] * 5,
    )
    assert result["cohort_freeze"] == "allowed"
    assert result[qual.QF_SELECT]["passes"] is True
    assert result[qual.QF_SELECT]["rate"] == 1.0
    assert result[qual.QF_DEFER]["passes"] is True
    assert "result_category" not in result


def test_gate_passes_at_exactly_the_required_rate_boundary():
    """0.80 of 5 is 4/5 -- the boundary itself must pass (>=, not >)."""
    select = [_select_output()] * 4 + [_invalid_output()]
    result = qual.score_qualification(select_outputs=select, defer_outputs=[_defer_output()] * 5)
    assert result[qual.QF_SELECT]["rate"] == 0.8
    assert result[qual.QF_SELECT]["passes"] is True
    assert result["cohort_freeze"] == "allowed"


# --- either control failing blocks the whole gate ----------------------

def test_gate_blocks_when_select_control_falls_below_the_rate():
    select = [_select_output()] * 3 + [_invalid_output()] * 2  # 3/5 = 0.6
    result = qual.score_qualification(select_outputs=select, defer_outputs=[_defer_output()] * 5)
    assert result[qual.QF_SELECT]["passes"] is False
    assert result[qual.QF_DEFER]["passes"] is True
    assert result["cohort_freeze"] == "blocked"
    assert result["result_category"] == qual.FLOOR_OR_CEILING_FAILURE


def test_gate_allows_freeze_when_only_defer_control_falls_below_the_rate():
    """2026-08-15 amendment: QF-DEFER no longer gates freeze. A subject that
    selects reliably but fails the defer diagnostic still gets
    cohort_freeze: allowed -- the failure is recorded as a non-blocking
    ceiling-diagnostic limitation (L9), not a block."""
    defer = [_defer_output()] * 3 + [_select_output()] * 2  # 3/5 = 0.6
    result = qual.score_qualification(select_outputs=[_select_output()] * 5, defer_outputs=defer)
    assert result[qual.QF_SELECT]["passes"] is True
    assert result[qual.QF_DEFER]["passes"] is False
    assert result[qual.QF_DEFER]["status"] == qual.DEFER_DIAGNOSTIC_FAILED
    assert result["cohort_freeze"] == "allowed"
    assert "result_category" not in result
    assert result["defer_ceiling_diagnostic_limitation"] is True
    assert "L9" in result["defer_ceiling_reporting_note"]


def test_gate_allows_freeze_when_defer_material_is_unavailable():
    """The current real state (Q14 pending, no repo-grounded QF-DEFER
    material exists): defer_outputs=None must not block freeze, and must
    be distinguished from a failed diagnostic."""
    result = qual.score_qualification(select_outputs=[_select_output()] * 5)
    assert result["cohort_freeze"] == "allowed"
    assert result[qual.QF_DEFER]["status"] == qual.DEFER_MATERIAL_UNAVAILABLE
    assert result[qual.QF_DEFER]["passes"] is None
    assert result["defer_ceiling_diagnostic_limitation"] is True


def test_gate_still_blocks_on_select_failure_when_defer_material_is_unavailable():
    """QF-SELECT remains the sole hard gate regardless of QF-DEFER's
    availability."""
    select = [_select_output()] * 3 + [_invalid_output()] * 2  # 3/5 = 0.6
    result = qual.score_qualification(select_outputs=select)
    assert result["cohort_freeze"] == "blocked"
    assert result["result_category"] == qual.FLOOR_OR_CEILING_FAILURE


def test_defer_diagnostic_passed_status_carries_no_limitation():
    """A passed QF-DEFER diagnostic is not a limitation -- it is confirmatory
    evidence the instrument can defer, so no L9 flag should attach."""
    result = qual.score_qualification(
        select_outputs=[_select_output()] * 5,
        defer_outputs=[_defer_output()] * 5,
    )
    assert result[qual.QF_DEFER]["status"] == qual.DEFER_DIAGNOSTIC_PASSED
    assert "defer_ceiling_diagnostic_limitation" not in result


def test_a_blocked_gate_carries_the_rulings_exact_reporting_sentence():
    """Q13.3's own required sentence must travel with a failed gate --
    analysis/reporting contract, never rendered to the model."""
    result = qual.score_qualification(
        select_outputs=[_invalid_output()] * 5,
        defer_outputs=[_defer_output()] * 5,
    )
    assert result["reporting_note"] == (
        "A failed qualification gate must not be reported as evidence "
        "of a null treatment effect."
    )


# --- precondition guards -------------------------------------------------

def test_refuses_the_wrong_number_of_trials():
    with pytest.raises(qual.QualificationContractError, match="expected exactly 5"):
        qual.score_qualification(
            select_outputs=[_select_output()] * 4,
            defer_outputs=[_defer_output()] * 5,
        )


def test_refuses_an_unknown_control_name():
    with pytest.raises(qual.QualificationContractError, match="unknown control"):
        qual._score_one_control("QF-BOGUS", [_select_output()] * 5)


# --- invalid outputs count against the rate, not silently excluded ------

def test_invalid_outputs_count_as_misses_not_as_excluded():
    """An invalid (malformed) output must not be dropped from the
    denominator -- that would let a subject dodge the gate by producing
    garbage instead of a wrong-but-valid answer."""
    select = [_select_output()] * 4 + [_invalid_output()]
    result = qual.score_qualification(select_outputs=select, defer_outputs=[_defer_output()] * 5)
    assert result[qual.QF_SELECT]["n"] == 5
    assert result[qual.QF_SELECT]["categories"].count(_coder_invalid_marker()) == 1


def _coder_invalid_marker() -> str:
    import _coder
    return _coder.INVALID
