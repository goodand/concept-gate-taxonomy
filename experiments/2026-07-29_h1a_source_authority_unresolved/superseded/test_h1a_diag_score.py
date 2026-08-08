"""Tests for the diagnostic scorer, written before any trial ran.

A scorer that can only be shown to stay silent proves nothing. Every rule
here is exercised in BOTH directions -- a case that must fire it and a case
that must not -- and each of §11.2's three limbs is fired independently, so
a limb that was accidentally wired to a constant would be caught rather than
hidden behind another limb that happened to fire.

All inputs are hand-written synthetic responses. Using real model output
would mean seeing results before the instrument is frozen.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scorer = _load("h1a_diag_score", HERE / "_h1a_diag_score.py")
diag = _load("h1a_diag_for_score_test", HERE / "_h1a_diag.py")

KEPT, REMOVED = diag.ARMS
SC, EF = diag.ANCHORS


# --- synthetic response builders ------------------------------------------

def sel(t=SC, rationale="x"):
    return {"decision": "select_type", "selected_type": t,
            "cited_evidence_ids": ["ev1"], "rationale": rationale}


def dfr(rationale="x"):
    return {"decision": "defer", "selected_type": None,
            "cited_evidence_ids": [], "rationale": rationale}


def bad():
    """Contradictory combination -- P5 says this codes `invalid`, never a
    charitable read of either behavior."""
    return {"decision": "defer", "selected_type": SC,
            "cited_evidence_ids": [], "rationale": "x"}


def trials(spec):
    """spec: {(arm, anchor): [response, ...]} -> flat trial list."""
    out = []
    for (arm, anchor), responses in spec.items():
        for i, response in enumerate(responses, 1):
            out.append({"trial_id": f"{arm}-{anchor}-{i:02d}",
                        "arm": arm, "anchor": anchor, "output": response})
    return out


def uniform(**per_cell):
    """Build all four cells from a per-cell response factory count."""
    return trials({
        (KEPT, SC): per_cell["kept_sc"], (KEPT, EF): per_cell["kept_ef"],
        (REMOVED, SC): per_cell["rem_sc"], (REMOVED, EF): per_cell["rem_ef"],
    })


# --- the preregistered constants are what the code actually uses ----------

def test_threshold_and_replicates_match_preregistration():
    assert scorer.COUNT_CHANGE_THRESHOLD == 2
    assert scorer.R_DIAG == 5


# --- cell aggregation ------------------------------------------------------

def test_invalid_stays_in_the_denominator():
    """P6: invalid is a third observed category, not a dropped row."""
    cell = scorer.score_cell([sel(), sel(), bad(), bad(), bad()])
    assert cell["n"] == 5
    assert cell["invalid"] == 3
    assert cell["modal_category"] == frozenset({"invalid"})


def test_modal_ties_are_not_broken_silently():
    cell = scorer.score_cell([sel(), sel(), dfr(), dfr()])
    assert cell["modal_category"] == frozenset({"selection", "deferral"})


def test_modal_selected_type_is_empty_when_no_selections():
    cell = scorer.score_cell([dfr()] * 5)
    assert cell["modal_selected_type"] == frozenset()


def test_score_cells_rejects_a_missing_cell():
    incomplete = trials({(KEPT, SC): [sel()] * 5, (KEPT, EF): [sel()] * 5,
                         (REMOVED, SC): [sel()] * 5})
    with pytest.raises(scorer.ScoreError):
        scorer.score_cells(incomplete)


def test_score_cells_rejects_a_trial_missing_fields():
    with pytest.raises(scorer.ScoreError):
        scorer.score_cells([{"trial_id": "x", "arm": KEPT}])


# --- §11.2 limb 1: modal category change ----------------------------------

def test_anchor_sensitivity_fires_on_modal_category_change():
    result = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[dfr()] * 5,   # flip -> category moved
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))["gross_anchor_sensitivity"]
    assert result["present"]
    assert result["by_arm"][KEPT]["modal_category_changed"]
    assert not result["by_arm"][REMOVED]["modal_category_changed"]


# --- §11.2 limb 2: modal selected_type change ------------------------------

def test_anchor_sensitivity_fires_on_modal_selected_type_change_alone():
    """Category stays `selection` in both anchors and counts are identical --
    only the *type* chosen moves. This limb must fire on its own."""
    result = scorer.score(uniform(
        kept_sc=[sel(SC)] * 5, kept_ef=[sel(EF)] * 5,
        rem_sc=[sel(SC)] * 5, rem_ef=[sel(SC)] * 5,
    ))["gross_anchor_sensitivity"]
    arm = result["by_arm"][KEPT]
    assert not arm["modal_category_changed"], "category must be unchanged here"
    assert arm["selection_delta"] == 0, "counts must be unchanged here"
    assert arm["modal_selected_type_changed"]
    assert result["present"]


# --- §11.2 limb 3: count change >= 2 of 5 ----------------------------------

def test_anchor_sensitivity_fires_on_count_delta_of_exactly_two():
    result = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 3 + [dfr()] * 2,
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))["gross_anchor_sensitivity"]
    arm = result["by_arm"][KEPT]
    assert arm["selection_delta"] == 2
    assert arm["count_changed_by_threshold"]
    assert result["present"]


def test_anchor_sensitivity_does_not_fire_on_count_delta_of_one():
    """The threshold is 'at least 2 out of 5'. A delta of 1 must not fire --
    otherwise the rule is stricter than what was preregistered."""
    result = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 4 + [dfr()],
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))["gross_anchor_sensitivity"]
    arm = result["by_arm"][KEPT]
    assert arm["selection_delta"] == 1
    assert not arm["count_changed_by_threshold"]
    assert not result["present"]


def test_anchor_sensitivity_silent_when_the_anchor_changes_nothing():
    result = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 5,
        rem_sc=[dfr()] * 5, rem_ef=[dfr()] * 5,
    ))["gross_anchor_sensitivity"]
    assert not result["present"]
    for arm in diag.ARMS:
        assert not any(result["by_arm"][arm][k] for k in
                       ("modal_category_changed", "modal_selected_type_changed",
                        "count_changed_by_threshold"))


def test_either_arm_firing_is_enough():
    """The rule says 'in either arm'. Firing only in REMOVED must still count."""
    result = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 5,
        rem_sc=[sel()] * 5, rem_ef=[dfr()] * 5,
    ))["gross_anchor_sensitivity"]
    assert not result["by_arm"][KEPT]["present"]
    assert result["by_arm"][REMOVED]["present"]
    assert result["present"]


# --- §11.2a interpretability condition ------------------------------------

def test_uniform_condition_fires_when_all_four_cells_share_a_modal_category():
    result = scorer.score(uniform(
        kept_sc=[dfr()] * 5, kept_ef=[dfr()] * 5,
        rem_sc=[dfr()] * 5, rem_ef=[dfr()] * 5,
    ))["uniform_modal_category"]
    assert result["uniform"]
    assert result["shared_modal_category"] == ["deferral"]
    assert "uninterpretable" in result["consequence"]


def test_uniform_condition_silent_when_cells_differ():
    result = scorer.score(uniform(
        kept_sc=[dfr()] * 5, kept_ef=[dfr()] * 5,
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))["uniform_modal_category"]
    assert not result["uniform"]
    assert result["shared_modal_category"] is None


def test_uniform_condition_can_fire_on_invalid():
    """If every cell is mostly malformed output, that is a real answer to
    'do all four cells share a modal category', not an error to swallow."""
    result = scorer.score(uniform(
        kept_sc=[bad()] * 5, kept_ef=[bad()] * 5,
        rem_sc=[bad()] * 5, rem_ef=[bad()] * 5,
    ))["uniform_modal_category"]
    assert result["uniform"]
    assert result["shared_modal_category"] == ["invalid"]


def test_uniform_condition_is_declared_non_blocking():
    """The ruling is explicit that this is neither a blocking rule nor a
    success criterion. Pin that so a later edit cannot quietly promote it."""
    result = scorer.score(uniform(
        kept_sc=[dfr()] * 5, kept_ef=[dfr()] * 5,
        rem_sc=[dfr()] * 5, rem_ef=[dfr()] * 5,
    ))["uniform_modal_category"]
    assert result["is_blocking_rule"] is False
    assert result["is_success_criterion"] is False


# --- the two rules are independent ----------------------------------------

def test_the_two_rules_can_disagree_in_both_directions():
    """The §11.2a condition exists precisely because §11.2 can report
    'absent' while the diagnostic established nothing. Confirm that
    combination is reachable, and that the reverse is too."""
    both_quiet_but_uniform = scorer.score(uniform(
        kept_sc=[dfr()] * 5, kept_ef=[dfr()] * 5,
        rem_sc=[dfr()] * 5, rem_ef=[dfr()] * 5,
    ))
    assert not both_quiet_but_uniform["gross_anchor_sensitivity"]["present"]
    assert both_quiet_but_uniform["uniform_modal_category"]["uniform"]

    sensitive_but_not_uniform = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[dfr()] * 5,
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))
    assert sensitive_but_not_uniform["gross_anchor_sensitivity"]["present"]
    assert not sensitive_but_not_uniform["uniform_modal_category"]["uniform"]


# --- top-level report contract --------------------------------------------

def test_report_is_labelled_non_certifying_and_not_mergeable():
    report = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 5,
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))
    assert report["label"] == "non_certifying_diagnostic"
    assert report["merge_into_main_cohort"] is False
    assert report["n_trials"] == 20


def test_both_rules_always_reported_regardless_of_outcome():
    report = scorer.score(uniform(
        kept_sc=[sel()] * 5, kept_ef=[sel()] * 5,
        rem_sc=[sel()] * 5, rem_ef=[sel()] * 5,
    ))
    assert "gross_anchor_sensitivity" in report
    assert "uniform_modal_category" in report
