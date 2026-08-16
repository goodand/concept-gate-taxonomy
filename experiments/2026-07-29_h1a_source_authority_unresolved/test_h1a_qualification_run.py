"""Tests for `_h1a_qualification_run.py` -- the qualification gate's
execution/persistence layer (D-H1a-13 Q13.3).

Same negative-coverage discipline as `test_h1a_score_instrument.py`/F9: an
overwrite guard with no test that proves it can actually fire is
indistinguishable from a guard that is always a no-op.
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
    assert manifest[run.qual.QF_DEFER]["status"] == run.qual.DEFER_MATERIAL_UNAVAILABLE


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
        json.dumps({"QF-SELECT": [select_output] * 5, "QF-DEFER": None}),
        encoding="utf-8",
    )

    assert run.main() == 0
    assert (tmp_path / "manifest.json").exists()
    assert (tmp_path / "score.json").exists()
    written = json.loads((tmp_path / "score.json").read_text(encoding="utf-8"))
    # QF-DEFER was not administered, so the gate blocks (D-H1a-13 sec 6).
    assert written["cohort_freeze"] == "blocked"
    assert written["QF-DEFER"]["status"] == run.qual.DEFER_MATERIAL_UNAVAILABLE


# --- the real recorded score is what the gate actually decided --------------

def test_the_real_recorded_score_shows_qf_select_passing_but_gate_blocked():
    """QF-SELECT genuinely passed 5/5 on 2026-08-15. The gate still blocks,
    because QF-DEFER was never administered -- Q13.3 requires both. The
    2026-08-15 amendment briefly recorded "allowed" here; that was retracted
    on 2026-08-16 (docs/feedback/h1a_qf_defer_amendment_review_20260816.md)."""
    recorded = json.loads(run.SCORE_PATH.read_text(encoding="utf-8"))
    assert recorded[run.qual.QF_SELECT]["rate"] == 1.0
    assert recorded[run.qual.QF_SELECT]["passes"] is True
    assert recorded["cohort_freeze"] == "blocked"
    assert recorded["QF-DEFER"]["status"] == run.qual.DEFER_MATERIAL_UNAVAILABLE
    assert recorded["qualification_incomplete"] is True
