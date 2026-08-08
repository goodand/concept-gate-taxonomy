"""PARKED -- not collected by pytest. Negative coverage for the three guards
that decide whether a paid live run may start.

Run it by hand with:  pytest pending_guard_negative_tests.py
No provider is called; the guards read local artifacts only.

What was wrong (2026-08-08)
---------------------------
`_assert_provider_preflight`, `_assert_ready`, and `_assert_safe_destination`
had zero tests that made them raise. Repo-root `test_guard_negative_coverage.py`
failed on exactly these three. A positive-only test cannot tell a working guard
from a no-op one, and these are the guards that refuse a run when the red-team
report is missing, failed, or stale -- the P1 pattern this repo has recorded
thirteen times.

Why this is parked instead of landed
------------------------------------
Landing it is not free. `test_preprimary_gates.py::test_all_test_modules_are_frozen`
requires every `test_*.py` here to appear in `_evaluator.FROZEN_SURFACE_FILES`,
and every name in that tuple becomes a key in `frozen_surface_hashes()`. One
extra key makes `frozen_surface_drift()` non-empty against every pinned
artifact -- including `results/live_pilot_codex_mcp_v7.json` and
`results/live_pilot_claude_mcp_surface_v2.json`, the two ledger-recorded
provider qualifications produced by 8 live model runs (gpt-5.6-sol and
claude-opus-5, 4 arms each). `_assert_provider_preflight` then refuses every
further live run until both are re-run. A free test change would force a paid
re-qualification, so the file waits for one that is already planned.

An earlier draft of this file claimed that staying outside the pin table was
legitimate because it changed no pinned byte. `test_all_test_modules_are_frozen`
refutes that: this repo has already decided no test module may escape the
freeze. Renaming out of `test_*.py` satisfies the letter of that gate and not
its intent, which is why the file is parked and recorded as debt rather than
quietly kept green.

Is the danger real right now? Measured, not asserted
----------------------------------------------------
Emptying all three guard bodies in a throwaway copy made 12 of the 12 tests
below fail with DID NOT RAISE. So "these guards are not vacuous" is a measured
fact as of 2026-08-08. What is missing is standing regression protection, not
present-tense evidence.

Closing condition
-----------------
Fold into the v8/surface-v3 re-qualification (pending item 4, R1/R2/
attempt-ledger): rename back to `test_live_phase_c_guards.py`, add it to
`FROZEN_SURFACE_FILES`, re-run calibration and both red-teams (local, free) and
both provider pilots (paid), then delete the three `KNOWN_UNPROVEN` entries in
repo-root `test_guard_negative_coverage.py`. Full record: `ARTIFACT_MANIFEST.md`
section "미결 산출물".
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_live_phase_c as rlpc
from build_live_public_bundle import BundleError, _assert_safe_destination
from run_live_phase_c import (LiveRunError, _assert_provider_preflight,
                              _assert_ready)

# A key the frozen surface cannot contain, so drift is forced without depending
# on any real file's contents.
_ABSENT_PIN = {"__not_a_frozen_surface_entry__": "0" * 64}


def _results(tmp_path, monkeypatch, name=None, payload=None):
    """Point RESULTS_DIR at an empty tmp dir, optionally seeding one report."""
    monkeypatch.setattr(rlpc, "RESULTS_DIR", tmp_path)
    if name is not None:
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_safe_destination_rejects_a_bundle_inside_the_project():
    with pytest.raises(BundleError, match="outside Project_in_progress"):
        _assert_safe_destination(HERE / "would_leak_into_the_repo")


def test_safe_destination_rejects_a_non_empty_destination(tmp_path):
    (tmp_path / "leftover.txt").write_text("stale", encoding="utf-8")
    with pytest.raises(BundleError, match="not empty"):
        _assert_safe_destination(tmp_path)


@pytest.mark.parametrize("payload, expected", [
    (None, "MCP-isolation red-team is missing"),
    ({"passed": False}, "MCP-isolation red-team failed"),
    ({"passed": True, "frozen_surface_hashes": _ABSENT_PIN},
     "MCP-isolation red-team is stale"),
    ({"passed": True}, "MCP-isolation red-team is stale"),  # pins absent entirely
])
def test_provider_preflight_refuses_a_codex_mcp_run(tmp_path, monkeypatch, payload,
                                                    expected):
    name = None if payload is None else "redteam_codex_mcp_isolation.json"
    _results(tmp_path, monkeypatch, name, payload)
    with pytest.raises(LiveRunError, match=expected):
        _assert_provider_preflight({"provider": "codex-mcp-cli"})


@pytest.mark.parametrize("payload, expected", [
    (None, "provider-isolation red-team is missing"),
    ({"hardened_profile_passed": False},
     "hardened provider-isolation red-team failed"),
    ({"hardened_profile_passed": True, "frozen_surface_hashes": _ABSENT_PIN},
     "stale"),
])
def test_provider_preflight_refuses_a_seatbelt_v2_run(tmp_path, monkeypatch, payload,
                                                      expected):
    name = None if payload is None else "redteam_provider_isolation.json"
    _results(tmp_path, monkeypatch, name, payload)
    with pytest.raises(LiveRunError, match=expected):
        _assert_provider_preflight({"sandbox_policy": "seatbelt-v2-hardened"})


@pytest.mark.parametrize("payload, expected", [
    (None, "calibration.json is missing"),
    ({"failures": ["HD01"]}, "calibration has failures"),
    ({"failures": [], "frozen_surface_hashes": _ABSENT_PIN},
     "frozen surface drifted"),
])
def test_assert_ready_refuses_an_unqualified_live_run(tmp_path, monkeypatch, payload,
                                                      expected):
    name = None if payload is None else "calibration.json"
    _results(tmp_path, monkeypatch, name, payload)
    with pytest.raises(LiveRunError, match=expected):
        _assert_ready("phase_c_live_config.json")


def test_provider_preflight_allows_a_provider_it_does_not_gate(tmp_path, monkeypatch):
    """The guard must refuse *selectively*. Without this, a guard that raised
    for every input would satisfy all the negative tests above while being
    useless -- the mirror image of the vacuous-guard failure."""
    _results(tmp_path, monkeypatch)
    _assert_provider_preflight({"provider": "claude-cli", "sandbox_policy": "none"})
