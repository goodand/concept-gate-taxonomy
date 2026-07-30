"""Tests for the H3 pilot's descriptive scorer.

The scorer has no threshold and issues no verdict, so the usual "did it
certify correctly" tests do not apply. What can still go silently wrong is
arithmetic that flatters an arm: a denominator that drops malformed output, a
missing cell that reads as zero difference, or a class->action table that has
drifted away from the oracle. Those are what this file pins.
"""

from __future__ import annotations

import copy
import importlib.util
import json
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


score_mod = _load("e24_h3_score_test", HERE / "_h3_score.py")


def _trial(trial_id, fixture_id, arm, action, violations=None, verdict=None):
    output = {
        "action": action,
        "repaired_concepts": None,
        "cited_evidence_ids": [],
        "report": "",
    }
    if verdict is not None:
        output["contract_assessment"] = {"contract_verdict": verdict}
    return {
        "trial_id": trial_id,
        "parameters": {"fixture_id": fixture_id, "arm": arm, "replicate": 1},
        "output": output,
        "schema_violations": violations or [],
    }


CLASSES = {
    "E24-F-01": "sufficient_consistent",
    "E24-F-02": "sufficient_repairable",
    "E24-F-03": "insufficient",
}


# --- the denominator rule (DESIGN_DECISION_H3.md §4) ---------------------

def test_invalid_output_counts_as_action_incorrect_not_as_a_smaller_denominator():
    """4 defers + 1 malformed on the insufficient cell is 0.80, not 1.00.

    This is the specific way a scorer can lie: if invalid outputs were dropped
    from the denominator, an arm would be rewarded for emitting garbage
    instead of a wrong answer.
    """
    trials = [
        _trial(f"t{i}", "E24-F-03", "CONTRACT_REPO_H3", "defer") for i in range(4)
    ] + [_trial("t4", "E24-F-03", "CONTRACT_REPO_H3", "defer", violations=["$: bad"])]
    cell_map = score_mod.cells(trials, CLASSES)
    cell = cell_map[("insufficient", "CONTRACT_REPO_H3")]
    assert cell["n"] == 5 and cell["invalid"] == 1
    assert score_mod.rate(cell, "defer") == pytest.approx(0.80)


def test_invalid_output_is_excluded_from_every_action_count():
    trials = [_trial("t0", "E24-F-03", "A_REPO_H3", "defer", violations=["$: bad"])]
    cell = score_mod.cells(trials, CLASSES)[("insufficient", "A_REPO_H3")]
    assert cell["invalid"] == 1
    assert sum(cell["actions"].values()) == 0
    for action in score_mod.ACTIONS:
        assert score_mod.rate(cell, action) == 0.0


def test_unknown_action_value_is_treated_as_invalid():
    trials = [_trial("t0", "E24-F-03", "A_REPO_H3", "abstain")]
    cell = score_mod.cells(trials, CLASSES)[("insufficient", "A_REPO_H3")]
    assert cell["invalid"] == 1, "the legacy 'abstain' vocabulary is not a valid H3 action"


# --- the primary estimand ------------------------------------------------

def test_delta_is_contract_minus_comparison_arm():
    trials = (
        [_trial(f"c{i}", "E24-F-03", "CONTRACT_REPO_H3", "defer") for i in range(4)]
        + [_trial("c4", "E24-F-03", "CONTRACT_REPO_H3", "accept_report")]
        + [_trial(f"x{i}", "E24-F-03", "CONTROL_REPO_H3", "repair") for i in range(5)]
        + [_trial(f"a{i}", "E24-F-03", "A_REPO_H3", "defer") for i in range(2)]
        + [_trial(f"b{i}", "E24-F-03", "A_REPO_H3", "accept_report") for i in range(3)]
    )
    primary = score_mod.deltas(score_mod.cells(trials, CLASSES))
    assert primary["p_defer_insufficient"]["CONTRACT_REPO_H3"] == pytest.approx(0.80)
    assert primary["p_defer_insufficient"]["CONTROL_REPO_H3"] == pytest.approx(0.00)
    assert primary["p_defer_insufficient"]["A_REPO_H3"] == pytest.approx(0.40)
    assert primary["delta"]["vs_CONTROL_REPO_H3"] == pytest.approx(0.80)
    assert primary["delta"]["vs_A_REPO_H3"] == pytest.approx(0.40)


def test_missing_cell_yields_none_not_a_zero_difference():
    """An arm that never ran is not an arm that scored zero."""
    trials = [_trial(f"c{i}", "E24-F-03", "CONTRACT_REPO_H3", "defer") for i in range(5)]
    primary = score_mod.deltas(score_mod.cells(trials, CLASSES))
    assert primary["p_defer_insufficient"]["CONTROL_REPO_H3"] is None
    assert primary["delta"]["vs_CONTROL_REPO_H3"] is None


def test_primary_estimand_uses_only_the_common_action_field():
    """contract_verdict must not influence the primary number (D-H3-3)."""
    base = [_trial(f"c{i}", "E24-F-03", "CONTRACT_REPO_H3", "defer",
                   verdict="insufficient_evidence") for i in range(5)]
    swapped = copy.deepcopy(base)
    for trial in swapped:
        trial["output"]["contract_assessment"]["contract_verdict"] = "out_of_scope"
    assert (score_mod.deltas(score_mod.cells(base, CLASSES))
            == score_mod.deltas(score_mod.cells(swapped, CLASSES)))


# --- oracle drift guard --------------------------------------------------

def test_class_to_action_table_matches_the_oracle_manifest():
    classes = score_mod.fixture_classes()
    assert set(classes) >= set(CLASSES)
    for fixture_id, semantic_class in CLASSES.items():
        assert classes[fixture_id] == semantic_class


def test_drifted_class_action_table_is_rejected(monkeypatch):
    """The cross-check must actually fire, not just exist."""
    drifted = dict(score_mod.TARGET_ACTION, insufficient="accept_report")
    monkeypatch.setattr(score_mod, "TARGET_ACTION", drifted)
    with pytest.raises(score_mod.ScoreError):
        score_mod.fixture_classes()


def test_scorer_reads_the_oracle_but_the_renderer_cannot():
    """The oracle belongs on the scoring side of the boundary only."""
    assert "oracle_manifest" in (HERE / "_h3_score.py").read_text(encoding="utf-8")
    assert "oracle_manifest" not in (HERE / "_h3.py").read_text(encoding="utf-8")


# --- secondary metrics ---------------------------------------------------

def test_contract_action_verdict_mismatch_is_detected():
    trials = [
        _trial("ok", "E24-F-03", "CONTRACT_REPO_H3", "defer", verdict="insufficient_evidence"),
        _trial("bad", "E24-F-03", "CONTRACT_REPO_H3", "defer", verdict="sufficient_consistent"),
    ]
    result = score_mod.secondary(trials, score_mod.cells(trials, CLASSES), CLASSES)
    mismatch = result["contract_action_verdict_mismatch"]
    assert mismatch["checked"] == 2 and mismatch["mismatched"] == 1
    assert mismatch["cases"][0]["trial_id"] == "bad"


def test_mismatch_check_ignores_non_contract_arms():
    trials = [_trial("t0", "E24-F-03", "CONTROL_REPO_H3", "defer")]
    result = score_mod.secondary(trials, score_mod.cells(trials, CLASSES), CLASSES)
    assert result["contract_action_verdict_mismatch"]["checked"] == 0


def test_false_defer_rate_covers_both_sufficient_classes():
    trials = [
        _trial("a", "E24-F-01", "CONTRACT_REPO_H3", "defer"),
        _trial("b", "E24-F-02", "CONTRACT_REPO_H3", "repair"),
    ]
    result = score_mod.secondary(trials, score_mod.cells(trials, CLASSES), CLASSES)
    false_defer = result["false_defer_rate"]
    assert false_defer["sufficient_consistent|CONTRACT_REPO_H3"] == pytest.approx(1.0)
    assert false_defer["sufficient_repairable|CONTRACT_REPO_H3"] == pytest.approx(0.0)


# --- the non-certifying contract ----------------------------------------

def test_score_output_is_marked_non_certifying():
    path = HERE / "h3_pilot_trials.json"
    if not path.exists():
        pytest.skip("pilot not yet recorded")
    result = score_mod.score(path)
    assert result["certifying"] is False
    assert "non-certifying" in result["note"].lower()
    for banned in ("certified", "screened_PASS", "threshold"):
        assert banned not in json.dumps(result), banned


def test_recorded_pilot_has_every_frozen_trial():
    path = HERE / "h3_pilot_trials.json"
    manifest = HERE / "h3_pilot_prompts.json"
    if not (path.exists() and manifest.exists()):
        pytest.skip("pilot not yet recorded")
    recorded = {t["trial_id"] for t in json.loads(path.read_text(encoding="utf-8"))["trials"]}
    frozen = {t["trial_id"] for t in json.loads(manifest.read_text(encoding="utf-8"))["trials"]}
    assert recorded == frozen
