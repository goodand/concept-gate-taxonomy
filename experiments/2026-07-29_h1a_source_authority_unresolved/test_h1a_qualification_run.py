"""Tests for `_h1a_qualification_run.py` -- the capability diagnostics'
execution/persistence layer (D-H1a-14/15).

Same negative-coverage discipline as `test_h1a_score_instrument.py`/F9: a
guard with no test that proves it can actually fire is indistinguishable from
a guard that is always a no-op. Every `_assert_*` here is exercised in both
directions, and `test_guard_negative_coverage.py` at the repo root enforces
that mechanically.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_qualification_run_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


run = _load("run", "_h1a_qualification_run.py")


# --- render_control / build_manifest produce a real, valid, no-anchor surface

def test_render_control_produces_a_no_anchor_payload_for_qf_select():
    rendered = run.render_control(run.QF_SELECT_FIXTURE_PATH)
    assert rendered["qualification_manifest"]["status"] == "passed"
    run.surface.assert_no_model_facing_type_anchor(rendered["model_payload"])
    assert "{payload_json}" not in rendered["rendered_prompt"]


def test_build_manifest_records_qf_select_and_marks_qf_defer_unavailable():
    manifest = run.build_manifest()
    assert manifest[run.qual.QF_SELECT]["rendered_prompt_sha256"]
    assert manifest[run.qual.QF_DEFER]["status"] == run.qual.MATERIAL_UNAVAILABLE


def test_manifest_records_the_surface_as_belonging_to_no_treatment_arm():
    """D-H1a-14/15 Q14.3. A reader must not be able to conclude the
    diagnostic ran "in the REMOVED condition"."""
    surface_block = run.build_manifest()["surface"]
    assert surface_block["name"] == "QUALIFICATION_COMMON"
    assert surface_block["treatment_arm"] is None
    assert surface_block["policy_role"] == "treatment_invariant"
    assert surface_block["old_label"] == run.SUPERSEDED_SURFACE_LABEL
    assert surface_block["byte_identity_verified"] is True


def test_manifest_declares_the_controls_are_not_freeze_prerequisites():
    assert run.build_manifest()["controls_are_freeze_prerequisites"] is False


# --- manifest drift detection ------------------------------------------------

def test_freeze_or_check_writes_a_new_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "MANIFEST_PATH", tmp_path / "manifest.json")
    written = run._freeze_or_check_manifest()
    assert (tmp_path / "manifest.json").exists()
    assert written[run.qual.QF_SELECT]["rendered_prompt_sha256"]


def test_freeze_or_check_passes_when_recorded_manifest_matches(tmp_path, monkeypatch):
    manifest_path = tmp_path / "manifest.json"
    monkeypatch.setattr(run, "MANIFEST_PATH", manifest_path)
    run._freeze_or_check_manifest()  # writes it once
    result = run._freeze_or_check_manifest()  # second call: must not raise
    assert result[run.qual.QF_SELECT]["rendered_prompt_sha256"]


def test_freeze_or_check_raises_on_drift(tmp_path, monkeypatch):
    """Recall: a recorded manifest whose QF-SELECT hash no longer matches
    what the live pipeline produces must be refused, not silently trusted."""
    manifest_path = tmp_path / "manifest.json"
    fresh = run.build_manifest()
    fresh[run.qual.QF_SELECT]["rendered_prompt_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(fresh), encoding="utf-8")
    monkeypatch.setattr(run, "MANIFEST_PATH", manifest_path)

    with pytest.raises(run.ManifestDriftError, match="rendered_prompt_sha256"):
        run._freeze_or_check_manifest()


# --- Q14.3: trial reuse is conditional on byte identity -------------------

def test_recorded_trials_match_the_current_qualification_surface():
    """Precision, and the substantive claim: the 5 recorded QF-SELECT trials
    were served exactly the bytes QUALIFICATION_COMMON renders today, which
    is what licenses reclassifying instead of re-running them."""
    manifest = run.build_manifest()
    assert (manifest[run.qual.QF_SELECT]["rendered_prompt_sha256"]
            == run.TRIALS_RENDERED_PROMPT_SHA256)
    run._assert_recorded_trials_match_the_qualification_surface(manifest)


def test_assert_recorded_trials_match_fires_when_the_surface_moves():
    """Recall. If the surface ever changes by one byte, the ruling says the
    recorded trials become historical diagnostics and the controls must be
    re-run -- so this must fail loudly rather than let stale trials stand in
    for a surface they were never served."""
    manifest = run.build_manifest()
    manifest[run.qual.QF_SELECT]["rendered_prompt_sha256"] = "0" * 64
    with pytest.raises(run.ManifestDriftError, match="historical diagnostics"):
        run._assert_recorded_trials_match_the_qualification_surface(manifest)


# --- the two guards called directly, so test_guard_negative_coverage.py's
# AST scan can see their recall proven (2026-08-16 review, D-6) -------------

def test_assert_manifest_has_not_drifted_fires_on_mismatch():
    fresh = run.build_manifest()
    stale = json.loads(json.dumps(fresh))
    stale[run.qual.QF_SELECT]["rendered_prompt_sha256"] = "0" * 64
    with pytest.raises(run.ManifestDriftError, match="rendered_prompt_sha256"):
        run._assert_manifest_has_not_drifted(stale, fresh)


def test_assert_manifest_has_not_drifted_passes_when_identical():
    """Precision: an unchanged manifest must not trip the guard."""
    fresh = run.build_manifest()
    run._assert_manifest_has_not_drifted(fresh, fresh)  # must not raise


def test_assert_score_path_is_free_fires_when_the_score_exists():
    """Recall against the REAL repo state: the recorded qualification score
    genuinely exists right now."""
    assert run.SCORE_PATH.exists(), (
        "precondition: h1a_qualification_score.json must exist for this to "
        "be a meaningful recall check"
    )
    with pytest.raises(run.QualificationScoreOverwriteRefused, match="h1a_qualification_score.json"):
        run._assert_score_path_is_free()


def test_assert_score_path_is_free_passes_when_absent(tmp_path, monkeypatch):
    """Precision: nothing to destroy, so the guard must stay quiet."""
    monkeypatch.setattr(run, "SCORE_PATH", tmp_path / "score.json")
    run._assert_score_path_is_free()  # must not raise


# --- F9-style overwrite guard on the score file -----------------------------

def test_main_refuses_to_overwrite_an_existing_score_file():
    """Recall against the REAL repo state: this score file genuinely exists
    right now, from the actual 5-trial QF-SELECT run this session executed.
    If this ever stops raising, that result is one `main()` call away from
    being silently overwritten."""
    assert run.SCORE_PATH.exists(), (
        "precondition: h1a_qualification_score.json must exist for this to "
        "be a meaningful recall check"
    )
    with pytest.raises(run.QualificationScoreOverwriteRefused, match="h1a_qualification_score.json"):
        run.main()


def test_main_proceeds_when_score_path_absent(tmp_path, monkeypatch):
    """Precision: the guard must not fire when there is nothing to destroy."""
    monkeypatch.setattr(run, "MANIFEST_PATH", tmp_path / "manifest.json")
    monkeypatch.setattr(run, "RAW_PATH", tmp_path / "raw.json")
    monkeypatch.setattr(run, "SCORE_PATH", tmp_path / "score.json")

    select_output = {
        "decision": "select_type", "selected_type": "structural_composition",
        "cited_evidence_ids": ["ev1", "ev2"], "rationale": "t",
    }
    (tmp_path / "raw.json").write_text(
        json.dumps({
            "provenance": _provenance_from(run.build_manifest()),
            "QF-SELECT": [select_output] * 5,
            "QF-DEFER": None,
        }),
        encoding="utf-8",
    )

    assert run.main() == 0
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "score.json").exists()
    written = json.loads((tmp_path / "score.json").read_text(encoding="utf-8"))
    assert written["cohort_freeze"] == {"determined_by": "identification_contract"}
    assert (written["capability_diagnostics"]["qf_defer"]["status"]
            == run.qual.MATERIAL_UNAVAILABLE)


# --- the real recorded diagnostics --------------------------------------

def test_the_real_recorded_diagnostics_are_what_was_observed():
    """QF-SELECT genuinely passed 5/5 on 2026-08-15; QF-DEFER was never
    administered. Under D-H1a-14/15 neither fact gates anything -- the record
    reports capability and hands freeze to the identification contract."""
    recorded = json.loads(run.SCORE_PATH.read_text(encoding="utf-8"))
    select = recorded["capability_diagnostics"]["qf_select"]
    assert select["rate"] == 1.0
    assert select["status"] == run.qual.DIAGNOSTIC_PASSED

    defer = recorded["capability_diagnostics"]["qf_defer"]
    assert defer["status"] == run.qual.MATERIAL_UNAVAILABLE
    assert defer["implies_subject_failure"] is False

    assert recorded["cohort_freeze"] == {"determined_by": "identification_contract"}
    assert recorded["diagnostic_summary"] == {
        "select_capability_observed": True,
        "defer_capability_observed": "unknown",
        "floor_risk_independently_checked": True,
        "ceiling_risk_independently_checked": False,
    }
    assert recorded["manifest"]["surface"]["name"] == "QUALIFICATION_COMMON"


# --- provenance: outputs must declare the subject/transport they came from
# (2026-08-16: found by comparing this harness against _h1a_cohort.py, which
# pins protocol/trial_subject_surface/decision_schema while this one did not)

def test_manifest_pins_the_same_trial_subject_contract_as_the_cohort():
    """The diagnostic must run the cohort's subject, not merely a subject.
    These are REUSED from `_h1a_cohort`, not copied, so a change to the
    cohort's pinned model or tool access moves the diagnostic with it."""
    import _h1a_cohort as cohort_mod
    manifest = run.build_manifest()
    assert manifest["protocol"]["trial_model"] == cohort_mod.MODEL
    assert manifest["protocol"]["tool_access"] == cohort_mod.PARAMETERS["tool_access"]
    assert manifest["protocol"]["transport"] == "schema_forced_structured_output"
    assert manifest["trial_subject_surface"]["tools"] == []


def _provenance_from(manifest: dict) -> dict:
    return {
        "transport": manifest["protocol"]["transport"],
        "trial_model": manifest["protocol"]["trial_model"],
        "tool_access": manifest["protocol"]["tool_access"],
        "context_isolation": manifest["protocol"]["context_isolation"],
        "trial_subject_definition_sha256":
            manifest["trial_subject_surface"]["definition_sha256"],
        "decision_schema_sha256": manifest["decision_schema_sha256"],
        "rendered_prompt_sha256": manifest[run.qual.QF_SELECT]["rendered_prompt_sha256"],
    }


def test_assert_raw_provenance_passes_on_a_matching_run():
    manifest = run.build_manifest()
    raw = {"provenance": _provenance_from(manifest), "QF-SELECT": [], "QF-DEFER": None}
    run._assert_raw_provenance_matches_the_manifest(raw, manifest)  # must not raise


def test_assert_raw_provenance_refuses_outputs_with_no_provenance_block():
    """Recall. "Unrecorded" must not be treated as "compatible" -- that is
    exactly how the 2026-08-15 run's transport/model mismatch went unnoticed."""
    manifest = run.build_manifest()
    with pytest.raises(run.ManifestDriftError, match="no `provenance` block"):
        run._assert_raw_provenance_matches_the_manifest({"QF-SELECT": []}, manifest)


@pytest.mark.parametrize("field,bad", [
    ("transport", "free_text"),
    ("trial_model", "claude-haiku-4-5-20251001"),
    ("tool_access", "all_tools"),
    ("decision_schema_sha256", "0" * 64),
    ("trial_subject_definition_sha256", "0" * 64),
])
def test_assert_raw_provenance_refuses_each_kind_of_subject_mismatch(field, bad):
    """Recall, per field. A diagnostic run on a different model or transport
    than the cohort attributes one subject's behavior to another."""
    manifest = run.build_manifest()
    provenance = _provenance_from(manifest)
    provenance[field] = bad
    raw = {"provenance": provenance, "QF-SELECT": [], "QF-DEFER": None}
    with pytest.raises(run.ManifestDriftError, match="different subject or"):
        run._assert_raw_provenance_matches_the_manifest(raw, manifest)


def test_the_superseded_2026_08_15_run_is_preserved_and_marked():
    """D-H1a-14/15 Q14.3 prescribes preserving a superseded run as a
    historical diagnostic rather than deleting it."""
    historical = HERE / "h1a_qualification_raw_historical_20260815.json"
    assert historical.exists()
    doc = json.loads(historical.read_text(encoding="utf-8"))
    assert doc["record_class"].endswith("HISTORICAL")
    assert doc["provenance_recorded"] is False
    assert len(doc["QF-SELECT"]) == 5
