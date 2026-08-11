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


def test_doctor_reads_a_typed_verdict_not_the_exception_text():
    """Round 18, finding #4: doctor decided FAIL vs BLOCKED by searching the
    exception message for the word "BLOCKED", so a diagnostic's
    classification depended on prose it did not own. Rewording a message
    would have silently reclassified a gate."""
    import run_live_phase_c as live
    import run_pipeline
    assert live.LiveRunError.verdict == "FAIL"
    assert live.LiveRunBlocked.verdict == "BLOCKED"
    assert issubclass(live.LiveRunBlocked, live.LiveRunError)
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert '"BLOCKED" in msg' not in source
    # And the classification actually comes from the type.
    row, value = run_pipeline._delegate(
        "synthetic", lambda: (_ for _ in ()).throw(
            live.LiveRunBlocked("refusing: nothing to see")))
    assert row["status"] == "BLOCKED" and value is None


def test_doctor_does_not_recount_the_attempt_ledger_itself():
    """The contract for which rows consume an attempt belongs with the code
    that writes them."""
    import run_live_phase_c as live
    assert hasattr(live, "remaining_primary_attempts")
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "remaining_primary_attempts" in source
    assert 'entry.get("status") == "started"' not in source, (
        "doctor re-derives the attempt-counting contract")


# --------------------------------------------------------------------------
# Round 19, step 2 -- ONE provenance verifier.
#
# The criterion is not "a shared module exists"; it is that no second reader
# of the ledger exists anywhere. Round 18 removed one weak copy and round 19
# found `_provenance.py` had grown another, because the shared verifier could
# not be pointed at a synthetic tree.
# --------------------------------------------------------------------------

def test_the_ledger_has_exactly_one_parser():
    impls = [p for p in HERE.glob("*.py")
             if not p.name.startswith("test_")
             and "def _parse_ledger_lines" in p.read_text(encoding="utf-8")]
    assert [p.name for p in impls] == ["run_live_phase_c.py"], impls


def test_audit_code_never_reads_the_ledger_directly():
    """The audit takes a receipt. It does not open the ledger, the
    authorization, or the config."""
    for name in ("make_safety_audit_blind_input.py", "apply_safety_audit.py"):
        source = (HERE / name).read_text(encoding="utf-8")
        assert "primary_attempt_ledger" not in source, name
        assert "attempt_ledger" not in source, name


def test_provenance_applies_the_legacy_prefix_pin():
    """The claim gate checks the git-committed pin on the pre-chain rows; the
    audit's verifier must apply the SAME checks, or a ledger the runner would
    refuse still yields a receipt (round 19, finding #6, same class)."""
    source = (HERE / "_provenance.py").read_text(encoding="utf-8")
    for check in ("verify_ledger_chain",
                  "_legacy_ledger_prefix_matches_known_hashes",
                  "verify_primary_attempt_artifacts"):
        assert check in source, f"_provenance does not apply {check}"


def test_a_redteam_artifact_without_a_typed_status_is_blocked(tmp_path):
    """Round 19, finding #5: `if status not in (None, "PASS")` let an artifact
    with no typed verdict through the same door as a PASS. A missing verdict
    is not a pass -- it is an artifact that predates the contract, and the
    fix for that is to re-run it, not to grandfather it."""
    import run_live_phase_c as live
    report = {"checked_configs": [{"file": "x.json", "sha256": "0" * 64}],
              "frozen_surface_hashes": {}}
    with pytest.raises(live.LiveRunBlocked, match="no typed verdict"):
        live._assert_redteam_covers_config(report, "x.json", "test run")


def test_doctor_attempt_capacity_applies_the_same_checks_as_the_claim(tmp_path):
    """Round 19, finding #6: `remaining_primary_attempts` parsed rows and
    counted `started`, while the real claim additionally verified the chain,
    the legacy pin and prior artifacts. On a corrupted ledger doctor could
    show capacity remaining and the claim refuse."""
    import run_live_phase_c as live
    import inspect
    src = inspect.getsource(live.remaining_primary_attempts)
    for check in ("verify_ledger_chain", "_legacy_ledger_prefix_matches_known_hashes",
                  "verify_primary_attempt_artifacts"):
        assert check in src, f"attempt capacity does not apply {check}"


def test_agent_reviewer_isolation_needs_probe_evidence_not_a_file(tmp_path):
    """Round 19: 'the launcher file exists' would let an empty stub PASS --
    a vacuous guard by another name. PASS requires an artifact showing the
    sandbox blocked what it must block, the way _providers.py's Seatbelt v2
    probes ran /bin/cat instead of reading a profile string."""
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "reviewer_runner.py" not in source, (
        "isolation still passes on file existence")
    for field in ("forbidden_probe_passed", "answer_key_reachable",
                  "repository_reachable", "sandbox_profile_sha256"):
        assert field in source, f"probe artifact does not require {field}"
