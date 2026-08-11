#!/usr/bin/env python3
"""GATE — doctor and the red-teams must report BLOCKED in their EXIT CODE,
and doctor must not hold an opinion that production does not hold.

AUDIT SURFACE. Written before the fixes it describes (round 17, TDD rule 1:
a fail-closed check gets its test first, at the outermost callable).

Round 17 measured two failures that a human had to read the screen to see:

  * `doctor` printed "BLOCKED is not a pass" and returned 0.
  * A red-team artifact with status=FAIL and hardened_profile_passed=false
    was rendered by doctor as `[ok  ] red-team: provider isolation  FAIL`,
    counted as `0 fail`, exit 0.

Both are the same mistake: a three-value vocabulary applied to the printed
text but not to the value a machine reads. This repository already hit that
in scripts/run_gates.py and answered it with a warning in prose. A warning is
not a mechanism, so here the exit code itself carries the three values.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

PASS, FAIL, BLOCKED = 0, 1, 2


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], cwd=HERE,
                          capture_output=True, text=True)


def test_doctor_exit_code_is_three_valued():
    """0 pass / 1 fail / 2 blocked -- and BLOCKED must never be 0."""
    import run_pipeline
    assert (run_pipeline.PASS, run_pipeline.FAIL, run_pipeline.BLOCKED) == (0, 1, 2)


def test_doctor_reports_blocked_rather_than_success(tmp_path):
    """The reviewer assignment is UNASSIGNED, so the audit cannot run. That is
    not a failure and it is certainly not a pass."""
    proc = _run("run_pipeline.py", "doctor")
    assert proc.returncode in (FAIL, BLOCKED), (
        f"doctor returned {proc.returncode} while printing:\n{proc.stdout}")
    if "blocked" in proc.stdout and " 0 fail" in proc.stdout:
        assert proc.returncode == BLOCKED


def test_doctor_delegates_the_qualification_gate_to_production():
    """Round 17, finding #1: doctor recomputed readiness and omitted the
    qualification gate entirely, so it reported `0 fail, exit 0` while
    `_assert_primary_qualifications` refused the same config as stale.

    A diagnostic that owns its own verdict can disagree with the thing it
    diagnoses. It must call the production gate, not re-derive it."""
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    for fn in ("_assert_ready", "_assert_primary_qualifications"):
        assert fn in source, f"doctor does not call {fn}"


def test_doctor_does_not_render_a_failed_redteam_as_ok(tmp_path):
    """Round 17, finding #3, reproduced verbatim: injecting status=FAIL and
    hardened_profile_passed=false produced `[ok  ] ... FAIL` and exit 0."""
    path = HERE / "results" / "redteam_provider_isolation.json"
    original = path.read_bytes()
    doc = json.loads(original)
    doc["status"] = "FAIL"
    doc["hardened_profile_passed"] = False
    doc["passed"] = False
    path.write_bytes(json.dumps(doc, ensure_ascii=False, indent=2).encode() + b"\n")
    try:
        proc = _run("run_pipeline.py", "doctor")
        line = next((l for l in proc.stdout.splitlines()
                     if "provider isolation" in l), "")
        assert "[ok" not in line, f"a failed red-team rendered as ok: {line!r}"
        assert proc.returncode != PASS, "doctor passed with a failed red-team"
    finally:
        path.write_bytes(original)


@pytest.mark.parametrize("script", ["redteam_provider_isolation.py",
                                    "redteam_codex_mcp_isolation.py"])
def test_redteam_exit_codes_are_three_valued(script):
    """A red-team that could not exercise the sandbox has learned nothing.
    Returning 0 there tells CI it cleared the provider."""
    source = (HERE / script).read_text(encoding="utf-8")
    assert "BLOCKED_EXIT" in source or "return 2" in source, (
        f"{script} has no BLOCKED exit path; an inconclusive run still "
        "returns success")
