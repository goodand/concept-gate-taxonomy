"""Negative test for the Stage-A instrument gate in `_h1a_score.py`.

`_assert_instrument_speaks` refuses to score when the coder's calibration is
not `passed`. That refusal path had no test: the positive direction is covered
implicitly by every scoring run, but nothing proved the guard can actually
fire, so a vacuous rewrite would have gone undetected. `test_guard_negative_coverage.py`
at the repo root is what surfaced it.

Both directions, per skills-catalog pattern 8 (`checker-recall-and-precision`).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    """Load a sibling module under a unique `sys.modules` key.

    Same reason as `test_h1a_policy.py`: experiment folders hold same-named
    modules as frozen copies and one experiment has already been observed
    running on another's code because whichever loaded first won `sys.modules`.
    """
    key = f"_h1a_score_instrument_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    # `_h1a_score` does a bare `import _coder` / `import _h1a_cohort`, so its
    # own directory has to be importable before the module body runs.
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


score = _load("score", "_h1a_score.py")


def _calibration(state: str) -> dict:
    return {
        "coder_version": "test",
        "cases": 4,
        "matched": 4 if state == "passed" else 2,
        "state": state,
        "mismatches": [] if state == "passed" else ["case-3", "case-4"],
        "by_axis": {},
    }


@pytest.mark.parametrize("state", ["failed", "error", "not_run"])
def test_scoring_refuses_when_the_coder_calibration_is_not_passed(
    monkeypatch: pytest.MonkeyPatch, state: str
) -> None:
    """Recall. A silent instrument's silence means nothing -- the guard must
    raise rather than let the cohort be scored by an uncalibrated coder."""
    monkeypatch.setattr(score._coder, "run_calibration", lambda: _calibration(state))

    with pytest.raises(score._coder.CoderError, match="refusing to score"):
        score._assert_instrument_speaks()


def test_scoring_proceeds_and_summarizes_when_calibration_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Precision. The guard must not fire on a passing instrument, and it must
    drop the per-case rows -- only the summary belongs in the score file."""
    monkeypatch.setattr(score._coder, "run_calibration", lambda: _calibration("passed"))

    summary = score._assert_instrument_speaks()

    assert summary == {
        "coder_version": "test",
        "cases": 4,
        "matched": 4,
        "state": "passed",
        "by_axis": {},
    }
    assert "mismatches" not in summary


# --- F9 (independent review 20260806, axis c): main() had no equivalent of
# freeze()'s overwrite refusal, so re-running the scorer for any reason
# silently destroyed the preserved 2026-08-03 cohort's scored output -------

def _spec(tmp_path, *, cohort_id="score-test", prefix="H1AQT",
          trials_name="trials.json", score_name="h1a_cohort_score.json"):
    """A throwaway CohortSpec. Built from the real class so the test cannot
    drift from the production constructor -- if a required field is added and
    not passed here, this fails loudly rather than testing a stale shape."""
    return score.cohort_mod.CohortSpec(
        cohort_id=cohort_id,
        fixture_path=score.cohort_mod.FIXTURE_PATH,
        cohort_path=tmp_path / "cohort.json",
        raw_path=tmp_path / "raw.json",
        trials_path=tmp_path / trials_name,
        score_path=tmp_path / score_name,
        order_seed="H1A-SCORE-TEST-v1",
        trial_id_prefix=prefix,
        n_per_arm=5,
        stage_a_replicates=[1, 2, 3, 4, 5],
    )


def test_main_refuses_to_overwrite_the_preserved_trials_file():
    """Recall against the REAL repo state, not a synthetic fixture: the
    preserved cohort's trials.json genuinely exists at this path right now.
    If this ever stops raising, the preserved artifact is one `main()` call
    away from being silently overwritten again."""
    assert score.cohort_mod.ORIGINAL_COHORT.trials_path.exists(), (
        "precondition: the preserved cohort's trials.json must exist for "
        "this to be a meaningful recall check"
    )
    with pytest.raises(score.ScoreOverwriteRefused, match="trials.json"):
        score.main()


def test_main_refuses_to_overwrite_the_preserved_score_file(tmp_path) -> None:
    """The check is a loop over both paths, not just the first one -- isolate
    score_path by pointing trials_path somewhere that doesn't exist, so a
    regression that only checks the first path still gets caught here."""
    original = score.cohort_mod.ORIGINAL_COHORT
    assert original.score_path.exists(), (
        "precondition: the preserved cohort's h1a_cohort_score.json must "
        "exist for this to be a meaningful recall check"
    )
    spec = _spec(tmp_path, cohort_id="h1a-original-20260803")
    spec.trials_path = tmp_path / "absent_trials.json"
    spec.score_path = original.score_path
    with pytest.raises(score.ScoreOverwriteRefused, match="h1a_cohort_score.json"):
        score.main(spec)


def test_main_proceeds_when_neither_output_path_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """Precision: the guard must not fire when there is nothing to destroy --
    the cohort_id-qualified paths of a genuinely new cohort."""
    spec = _spec(tmp_path)
    monkeypatch.setattr(score._coder, "run_calibration", lambda: _calibration("passed"))
    monkeypatch.setattr(score, "score", lambda _spec_arg=None: {
        "records": [], "coder_calibration": _calibration("passed"),
    })

    assert score.main(spec) == 0
    assert spec.trials_path.exists()
    assert spec.score_path.exists()


# --- 2026-08-18: cohort parameterization. Three cohort identities share this
# folder, so "which cohort is being scored" must be a parameter, and the
# manifest read must be pinned to the spec that named the output paths -------

def test_the_two_cohorts_do_not_share_any_output_path(tmp_path) -> None:
    """PREREGISTRATION_TYPED_SCOPE_COHORT.md §6: `cohort_id`·출력 파일은 기존
    코호트와 분리. Separation is only real if every output path differs -- one
    shared filename is enough to destroy the preserved cohort's artifact."""
    original = score.cohort_mod.ORIGINAL_COHORT
    typed = score.cohort_mod.TYPED_SCOPE_COHORT

    assert original.cohort_id != typed.cohort_id
    for field in ("cohort_path", "raw_path", "trials_path", "score_path"):
        a, b = getattr(original, field), getattr(typed, field)
        assert a != b, f"{field} is shared between the two cohorts: {a}"


def test_scoring_refuses_a_manifest_belonging_to_another_cohort(tmp_path) -> None:
    """Recall for the identity guard. The mirror-image of the freeze accident:
    not writing over another cohort's manifest, but reading one cohort's
    manifest and filing its scores under another cohort's name. Both files
    would parse and both would look complete, so nothing else catches it."""
    spec = _spec(tmp_path, prefix="H1AT")
    spec.cohort_path.write_text(
        json.dumps({"trials": [
            {"trial_id": "H1A-PROHIBITION_KEPT-01", "arm": "PROHIBITION_KEPT",
             "replicate": 1},
        ]}), encoding="utf-8",
    )
    spec.raw_path.write_text("{}", encoding="utf-8")

    with pytest.raises(score.CohortIdentityMismatch, match="H1AT-"):
        score.score(spec)


def test_the_identity_guard_compares_the_prefix_with_its_hyphen(tmp_path) -> None:
    """`"H1AT-KEPT-01".startswith("H1A")` is True. If the guard ever drops the
    hyphen, every typed-scope trial passes as a preserved-cohort one and the
    guard above goes silent while still looking present. HANDOFF.md flags this
    exact hazard, so it is pinned rather than trusted to review."""
    spec = _spec(tmp_path, prefix="H1A")
    spec.cohort_path.write_text(
        json.dumps({"trials": [
            {"trial_id": "H1AT-PROHIBITION_KEPT-01", "arm": "PROHIBITION_KEPT",
             "replicate": 1},
        ]}), encoding="utf-8",
    )
    spec.raw_path.write_text("{}", encoding="utf-8")

    with pytest.raises(score.CohortIdentityMismatch):
        score.score(spec)


def test_the_identity_guard_accepts_its_own_cohorts_manifest(tmp_path) -> None:
    """Precision: the guard must not fire on the matching spec. Without this,
    a guard that raised unconditionally would pass both recall tests."""
    spec = _spec(tmp_path, prefix="H1AT")
    cohort_doc = {"trials": [
        {"trial_id": "H1AT-PROHIBITION_KEPT-01", "arm": "PROHIBITION_KEPT",
         "replicate": 1},
    ]}
    score._assert_manifest_belongs_to_the_spec(cohort_doc, spec)


def test_the_identity_guard_fires_when_called_directly(tmp_path) -> None:
    """The two tests above reach the guard through `score()`. This one calls it
    directly, so a refactor that stops invoking it from `score()` cannot leave
    its recall untested -- and the negative-coverage scanner needs the direct
    raising call to count it as covered at all."""
    spec = _spec(tmp_path, prefix="H1AT")
    with pytest.raises(score.CohortIdentityMismatch):
        score._assert_manifest_belongs_to_the_spec(
            {"trials": [{"trial_id": "H1A-PROHIBITION_KEPT-01"}]}, spec
        )


# --- 2026-08-18: §7 requires the licensed-path values be recorded with the
# results. `build_cohort()` discarded the proof, so nothing enforced it -------

def test_scoring_refuses_when_the_freeze_proof_was_never_recorded(
    tmp_path,
) -> None:
    """Recall: absent proof must stop the scoring, not warn. §7's requirement
    had no enforcement at all before this guard -- the obligation existed only
    in prose while `build_cohort()` threw the proof away."""
    spec = _spec(tmp_path)
    assert not spec.freeze_proof_path.exists()
    with pytest.raises(score.FreezeProofMissing, match="absent"):
        score._assert_the_freeze_proof_is_recorded(spec)


def test_scoring_refuses_a_freeze_proof_bound_to_different_manifest_bytes(
    tmp_path,
) -> None:
    """Recall for the binding half. A proof present but computed against other
    bytes describes a different freeze, and looks identical to a correct one on
    inspection -- so presence alone must not satisfy the guard."""
    spec = _spec(tmp_path)
    spec.cohort_path.write_text('{"trials": []}', encoding="utf-8")
    spec.freeze_proof_path.write_text(
        json.dumps({
            "cohort_manifest_sha256": "0" * 64,
            "licensed_source_evaluation_path": {},
        }), encoding="utf-8",
    )
    with pytest.raises(score.FreezeProofMissing, match="does not describe"):
        score._assert_the_freeze_proof_is_recorded(spec)


def test_the_freeze_proof_guard_accepts_a_correctly_bound_proof(tmp_path) -> None:
    """Precision: a guard that raised unconditionally would pass both recall
    tests above. This is the one that separates working from vacuous."""
    import hashlib

    spec = _spec(tmp_path)
    spec.cohort_path.write_text('{"trials": []}', encoding="utf-8")
    digest = hashlib.sha256(spec.cohort_path.read_bytes()).hexdigest()
    rows = {"PROHIBITION_REMOVED": {"licensed_path": True}}
    spec.freeze_proof_path.write_text(
        json.dumps({
            "cohort_manifest_sha256": digest,
            "licensed_source_evaluation_path": rows,
        }), encoding="utf-8",
    )

    proof = score._assert_the_freeze_proof_is_recorded(spec)
    assert proof["licensed_source_evaluation_path"] == rows
