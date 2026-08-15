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

def test_main_refuses_to_overwrite_the_preserved_trials_file():
    """Recall against the REAL repo state, not a synthetic fixture: the
    preserved cohort's trials.json genuinely exists at this path right now.
    If this ever stops raising, the preserved artifact is one `main()` call
    away from being silently overwritten again."""
    assert score.TRIALS_PATH.exists(), (
        "precondition: the preserved cohort's trials.json must exist for "
        "this to be a meaningful recall check"
    )
    with pytest.raises(score.ScoreOverwriteRefused, match="trials.json"):
        score.main()


def test_main_refuses_to_overwrite_the_preserved_score_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """The check is a loop over both paths, not just the first one -- isolate
    SCORE_PATH by redirecting TRIALS_PATH to somewhere that doesn't exist, so
    a regression that only checks TRIALS_PATH still gets caught here."""
    assert score.SCORE_PATH.exists(), (
        "precondition: the preserved cohort's h1a_cohort_score.json must "
        "exist for this to be a meaningful recall check"
    )
    monkeypatch.setattr(score, "TRIALS_PATH", tmp_path / "trials.json")
    with pytest.raises(score.ScoreOverwriteRefused, match="h1a_cohort_score.json"):
        score.main()


def test_main_proceeds_when_neither_output_path_exists(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    """Precision: the guard must not fire when there is nothing to destroy --
    e.g. a genuinely new cohort_id-qualified path once that separation is
    wired in."""
    monkeypatch.setattr(score, "TRIALS_PATH", tmp_path / "trials.json")
    monkeypatch.setattr(score, "SCORE_PATH", tmp_path / "h1a_cohort_score.json")
    monkeypatch.setattr(score._coder, "run_calibration", lambda: _calibration("passed"))
    monkeypatch.setattr(score, "score", lambda: {
        "records": [], "coder_calibration": _calibration("passed"),
    })

    assert score.main() == 0
    assert (tmp_path / "trials.json").exists()
    assert (tmp_path / "h1a_cohort_score.json").exists()
