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
    # `_launcher_available()` may name the module, but PASS must still rest on
    # probe fields -- not on the file being there.
    assert "def _launcher_available" in source
    assert "produced_by" in source, "launcher receipts are not authenticated"
    # doctor no longer reads booleans at all: it calls the launcher's own
    # verifier, which rejects a receipt that was not produced by the launcher
    # or whose contents no longer match its hash.
    assert "verify_isolation_receipt" in source, (
        "doctor still reads the reviewer's own booleans")


# --------------------------------------------------------------------------
# Round 20, step E -- ONE canonicalization for the provenance receipt.
#
# Commit 1f12e2f was titled "one canonical for each thing" and shipped
# `_receipt_sha256` twice, in the packet builder and in the adjudicator. Its
# comment cited a test named
# `test_the_receipt_hash_is_computed_the_same_way_on_both_sides` that did not
# exist -- the fifth instance this session of a comment teaching a contract
# the code does not implement.
#
# The fix is a LEAF module. Measured before choosing: importing _provenance
# into apply_safety_audit would take its import from 5.0ms to ~19ms and, more
# importantly, drag run_live_phase_c -> run_smoke, run_calibration,
# _providers into the adjudicator -- development modules becoming production
# dependencies, the inversion round 14 already named.
# --------------------------------------------------------------------------

def test_the_receipt_hash_has_exactly_one_implementation():
    impls = [p.name for p in HERE.glob("*.py")
             if not p.name.startswith("test_")
             and "def receipt_sha256" in p.read_text(encoding="utf-8")]
    assert impls == ["_receipt.py"], impls
    for name in ("_provenance.py", "make_safety_audit_blind_input.py",
                 "apply_safety_audit.py"):
        source = (HERE / name).read_text(encoding="utf-8")
        assert "def _receipt_sha256" not in source, f"{name} still has a copy"
        assert "from _receipt import" in source, f"{name} does not import it"


def test_the_receipt_hash_is_computed_the_same_way_on_both_sides():
    """The test the old comment claimed existed."""
    import apply_safety_audit as asa
    import make_safety_audit_blind_input as mk
    from _receipt import receipt_sha256
    assert mk.receipt_sha256 is receipt_sha256
    assert asa.receipt_sha256 is receipt_sha256
    sample = {"mode": "verified", "b": 1, "a": [2, 3]}
    assert receipt_sha256(sample) == receipt_sha256(dict(reversed(list(sample.items()))))
    assert receipt_sha256(None) is None


def test_the_receipt_module_is_a_leaf():
    """No local imports. If it grows one, the adjudicator inherits it."""
    import ast
    tree = ast.parse((HERE / "_receipt.py").read_text(encoding="utf-8"))
    local = {p.stem for p in HERE.glob("*.py")}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not ({a.name for a in node.names} & local), ast.dump(node)
        if isinstance(node, ast.ImportFrom):
            assert node.module not in local, node.module


# --------------------------------------------------------------------------
# Round 20, step A -- OBLIGATION is the unit of completion, not stage.
#
# Measured on 1f12e2f: `reviewer.assignment.frozen` was explicitly UNKNOWN,
# yet its stage counted as covered because a DIFFERENT obligation on the same
# stage was guarded. So "3 unguarded stages" was true and "3 unguarded
# obligations" was not -- there were at least 4, and my commit message
# reported the stage number as if it were the coverage.
# --------------------------------------------------------------------------

def test_the_completion_unit_is_the_obligation():
    import run_pipeline
    assert hasattr(run_pipeline, "OBLIGATIONS"), (
        "coverage is still computed from stages")
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "set(STAGE_IDS.values()) - set(UNGUARDED_STAGES)" not in source, (
        "the stage set-difference is still the coverage計算")


def test_overall_is_pass_only_when_every_obligation_is_pass():
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    obligations = dict(rp.OBLIGATIONS)
    assert rp.overall_verdict(obligations) in (Verdict.PASS, Verdict.UNKNOWN,
                                               Verdict.FAIL)
    # One UNKNOWN is enough to deny PASS -- the rule cg_obligations already
    # applies, reused rather than re-derived.
    poisoned = {**{k: Verdict.PASS for k in obligations},
                "reviewer.isolation.enforced": Verdict.UNKNOWN}
    assert rp.overall_verdict(poisoned) is Verdict.UNKNOWN
    allpass = {k: Verdict.PASS for k in obligations}
    assert rp.overall_verdict(allpass) is Verdict.PASS
    poisoned2 = {**allpass, "audit.input-validated": Verdict.FAIL}
    assert rp.overall_verdict(poisoned2) is Verdict.FAIL


def test_every_mutation_obligation_appears_in_the_pipeline_registry():
    """SET equality between the acceptance gate's obligations and the
    pipeline's. A mutation for an obligation the pipeline does not declare
    guards nothing; a declared obligation with no mutation is UNKNOWN."""
    import run_pipeline as rp
    import test_e2e_acceptance as ac
    mutated = {o.obligation_id for o in ac.OBLIGATIONS
               if o.obligation_id not in ac.NO_SIGNAL_YET}
    declared = set(rp.OBLIGATIONS)
    assert mutated <= declared, f"mutations for undeclared obligations: {mutated - declared}"
    from conceptgate.cg_obligations import Verdict
    for name, verdict in rp.OBLIGATIONS.items():
        mechanism = rp.PROVEN_BY[name]
        if verdict is Verdict.PASS and mechanism == "mutation":
            assert name in mutated, (
                f"{name} claims PASS by mutation but none demonstrates it")
        if verdict is not Verdict.PASS:
            assert name in rp.UNKNOWN_REASONS, (
                f"{name} is not PASS and records no reason")


# --------------------------------------------------------------------------
# Round 20, step B -- three modes, ONE pipeline.
#
# Finding #2: there was no release mode, and both E2E tests accepted exit 0 OR
# 2. A program can stay PARTIAL forever with a green suite. The fix is a mode
# whose only success is 0 -- and the modes must not be three pipelines, or
# each would drift (the canonical-path requirement of
# DESIGN_DECISION_surface_separation.md §3 and its required test #7).
# --------------------------------------------------------------------------

def test_the_three_modes_share_one_pipeline():
    import run_pipeline as rp
    assert hasattr(rp, "RunSpec") and hasattr(rp, "run_pipeline")
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    # Every mode must funnel into run_pipeline(spec); no mode may assemble its
    # own sequence of stages.
    assert source.count("def run_pipeline(") == 1
    for mode in ("offline-smoke", "release", "primary"):
        assert mode in source, f"mode {mode} is not declared"


def test_release_mode_does_not_accept_partial():
    """The whole point of the split. smoke tolerates PARTIAL; release does
    not, or PARTIAL becomes permanent."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    smoke = rp.RunSpec.for_mode("offline-smoke")
    release = rp.RunSpec.for_mode("release")
    assert smoke.allow_partial is True
    assert release.allow_partial is False
    assert release.require_launcher is True
    assert release.require_closure is True


def test_release_mode_passes_and_every_obligation_is_demonstrated():
    """Round 20's completion goal. release accepts only PASS, so exit 0 here
    means all ten obligations are demonstrated -- not that the run finished."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    if rp._closure_receipt() is None:
        # Editing any audit-surface file invalidates the receipt -- which is
        # the mechanism working. `test_every_frozen_artifact_is_current`
        # already reports that loudly; reporting the same fact twice would
        # make one un-run command look like two defects. BLOCKED, not FAIL.
        pytest.skip("closure receipt is stale; run `run_pipeline.py closure` "
                    "as the last step before committing")
    proc = _run("run_pipeline.py", "e2e", "--release")
    assert proc.returncode == PASS, proc.stdout[-2000:] + proc.stderr[-500:]
    assert rp.overall_verdict() is Verdict.PASS
    assert '"obligations_unknown": []' in proc.stdout


def test_release_names_the_obligation_when_a_precondition_is_missing():
    """When something IS missing, release must say which obligation -- not
    just fail. Reproduced by removing the closure receipt in
    test_release_refuses_without_a_current_closure_receipt."""
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "requires {len(unmet)} thing(s)" in source
    assert "freeze.closure.current:" in source
    assert "reviewer.isolation.enforced:" in source


def test_release_refuses_without_a_current_closure_receipt(tmp_path):
    """The acceptance test that demonstrates `freeze.closure.current`.

    Not a mutation: the obligation is that release REFUSES when no receipt
    describes the current surface, and the way to observe that is to remove
    the receipt, not to remove the check. (Removing the check in a tree that
    still has a valid receipt changes nothing observable -- the mutation would
    be a no-op, which run_calibration's applied-check calls a harness defect.)
    """
    import shutil
    repo = tmp_path / "repo"
    target = repo / "experiments" / HERE.name
    shutil.copytree(HERE, target,
                    ignore=shutil.ignore_patterns("__pycache__",
                                                  "audit_workspace",
                                                  ".pytest_cache"))
    shutil.copytree(HERE.parents[1] / "conceptgate", repo / "conceptgate",
                    ignore=shutil.ignore_patterns("__pycache__"))
    receipts = list((target / "results").glob("closure_*.json"))
    assert receipts, "no closure receipt to remove; run run_pipeline.py closure"
    for path in receipts:
        path.unlink()

    proc = subprocess.run([sys.executable, "run_pipeline.py", "e2e", "--release"],
                          cwd=target, capture_output=True, text=True, timeout=180)
    assert proc.returncode == FAIL, proc.stdout[-1500:]
    assert "freeze.closure.current" in proc.stdout


def test_every_obligation_records_how_it_is_proven():
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    assert set(rp.PROVEN_BY) == set(rp.OBLIGATIONS)
    for name, verdict in rp.OBLIGATIONS.items():
        if verdict is not Verdict.PASS:
            continue
        mechanism = rp.PROVEN_BY[name]
        assert mechanism == "mutation" or mechanism.startswith("acceptance:"), (
            f"{name}: unrecognised mechanism {mechanism!r}")
        if mechanism.startswith("acceptance:"):
            test_name = mechanism.split(":", 1)[1]
            found = any(f"def {test_name}" in p.read_text(encoding="utf-8")
                        for p in HERE.glob("test_*.py"))
            assert found, f"{name} cites {test_name}, which does not exist"
