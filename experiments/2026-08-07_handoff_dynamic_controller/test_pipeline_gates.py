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


def _run(*args: str, receipt_dir: str | None = None) -> subprocess.CompletedProcess:
    """Drive the CLI. Release receipts are redirected away from `results/`.

    Round 21: `e2e --release` writes a receipt recording the git commit and
    dirty flag, so running the suite against the real tree deposited a new file
    in the committed, append-only `results/` on every invocation -- and a clean
    vs dirty tree produced different documents, so committing one guaranteed the
    next run wrote another. Tests must not add to the experiment's evidence.
    """
    import os
    import tempfile
    env = dict(os.environ)
    env["CG_RELEASE_RECEIPT_DIR"] = receipt_dir or tempfile.mkdtemp(
        prefix="cg-receipts-")
    return subprocess.run([sys.executable, *args], cwd=HERE,
                          capture_output=True, text=True, env=env)


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
    # Round 21: `produced_by` was the marker, and it was also the forgery --
    # a string the caller types. Authentication is now an HMAC, and it lives in
    # the LAUNCHER, so that is where the marker is checked. Asserting it in
    # run_pipeline.py only proved run_pipeline mentions a word.
    launcher = (HERE / "reviewer_runner.py").read_text(encoding="utf-8")
    assert "RECEIPT_DOMAIN" in launcher and "sign(doc, key" in launcher, (
        "launcher receipts are not authenticated")
    assert "produced_by" not in launcher.split('"""')[2], (
        "the forgeable produced_by marker is still live code")
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
    assert hasattr(run_pipeline, "DECLARED_OBLIGATIONS"), (
        "coverage is still computed from stages")
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "set(STAGE_IDS.values()) - set(UNGUARDED_STAGES)" not in source, (
        "the stage set-difference is still the coverage計算")


def test_overall_is_pass_only_when_every_obligation_is_pass():
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    names = rp.DECLARED_OBLIGATIONS
    allpass = {k: rp.RunVerdict(Verdict.PASS, "observed") for k in names}
    assert rp.overall_verdict(allpass) is Verdict.PASS
    # One UNKNOWN is enough to deny PASS -- the rule cg_obligations already
    # applies, reused rather than re-derived.
    poisoned = {**allpass,
                "reviewer.isolation.enforced": rp.RunVerdict(
                    Verdict.UNKNOWN, "sandbox unavailable")}
    assert rp.overall_verdict(poisoned) is Verdict.UNKNOWN
    poisoned2 = {**allpass,
                 "audit.input-validated": rp.RunVerdict(Verdict.FAIL, "gate off")}
    assert rp.overall_verdict(poisoned2) is Verdict.FAIL
    # Round 21: and a PASS with no evidence is not a PASS. The invariant comes
    # from the obligation layer, applied through the registry seam.
    hollow = {**allpass,
              "packet.blinding.applied": rp.RunVerdict(Verdict.PASS, "")}
    assert rp.overall_verdict(hollow) is Verdict.FAIL, (
        "an obligation asserted PASS with no observation behind it")


def test_every_mutation_obligation_appears_in_the_pipeline_registry():
    """SET equality between the acceptance gate's obligations and the
    pipeline's. A mutation for an obligation the pipeline does not declare
    guards nothing; a declared obligation with no mutation is UNKNOWN."""
    import run_pipeline as rp
    import test_e2e_acceptance as ac
    mutated = {o.obligation_id for o in ac.OBLIGATIONS
               if o.obligation_id not in ac.NO_SIGNAL_YET}
    declared = set(rp.DECLARED_OBLIGATIONS)
    assert mutated <= declared, f"mutations for undeclared obligations: {mutated - declared}"
    from conceptgate.cg_obligations import Verdict
    for name, record in rp.demonstrated_obligations().items():
        mechanism = rp.PROVEN_BY[name]
        if record.verdict is Verdict.PASS and mechanism == "mutation":
            assert name in mutated, (
                f"{name} claims PASS by mutation but none demonstrates it")
        # Round 21: a non-PASS obligation carries its reason in the record
        # itself, so there is no separate table to forget to update.
        if record.verdict is not Verdict.PASS:
            assert record.evidence, f"{name} is not PASS and records no reason"


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
    assert '"effective_unknown": []' in proc.stdout


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
    assert set(rp.PROVEN_BY) == set(rp.DECLARED_OBLIGATIONS)
    for name, record in rp.demonstrated_obligations().items():
        if record.verdict is not Verdict.PASS:
            continue
        mechanism = rp.PROVEN_BY[name]
        assert mechanism == "mutation" or mechanism.startswith("acceptance:"), (
            f"{name}: unrecognised mechanism {mechanism!r}")
        if mechanism.startswith("acceptance:"):
            test_name = mechanism.split(":", 1)[1]
            found = any(f"def {test_name}" in p.read_text(encoding="utf-8")
                        for p in HERE.glob("test_*.py"))
            assert found, f"{name} cites {test_name}, which does not exist"


# --------------------------------------------------------------- round 21 ----
# Finding #4: `e2e --primary` advertised "the 32-cell run" and then executed
# `_synthetic_primary()` -- no provider, no authorization, no attempt claim.
# release and primary had IDENTICAL RunSpec fields, so the two modes were the
# same program under two names. A caller who trusted the help text would
# record a synthetic result as a primary one.

def test_primary_mode_refuses_until_a_real_runner_is_connected():
    """A mode that cannot do what it is named must not exit 0."""
    proc = subprocess.run([sys.executable, "run_pipeline.py", "e2e", "--primary"],
                          cwd=HERE, capture_output=True, text=True, timeout=180)
    assert proc.returncode == BLOCKED, (
        f"--primary returned {proc.returncode}; a mode with no provider behind "
        f"it must not report success\n{proc.stdout[-1500:]}")
    out = proc.stdout + proc.stderr
    assert "not implemented" in out and "no attempt was claimed" in out, out[-800:]
    # It must not have built the synthetic artifact either -- refusing after
    # doing the work still teaches a reader that the work is the primary run.
    assert "primary.synthetic-built" not in out, (
        "--primary ran the synthetic pipeline before refusing")


def test_primary_mode_has_no_runnable_spec():
    """The refusal lives in one place. `for_mode` must not hand out a spec
    that `run_pipeline` would happily execute."""
    import run_pipeline as rp
    with pytest.raises(SystemExit, match="not implemented"):
        rp.RunSpec.for_mode("primary")


# ---- #6: the closure verifier must check everything the generator writes ----
def _current_closure_fields(rp):
    from _evaluator import frozen_surface_hashes
    now = frozen_surface_hashes()
    digest = __import__("hashlib").sha256(
        json.dumps(now, sort_keys=True).encode("utf-8")).hexdigest()
    return now, digest


def test_a_minimal_json_is_not_a_closure_receipt(tmp_path, monkeypatch):
    """Reproduced before the fix: `_closure_receipt()` read exactly one field.

        {"frozen_surface_hashes": {...current...}}   -> accepted as valid

    kind, frozen_surface_digest, the digest in the filename, steps, and the
    artifact hashes were all WRITTEN by the generator and read by nobody. That
    is the `output_sha256` pattern again -- a field recorded to look rigorous
    and never compared.
    """
    import run_pipeline as rp
    now, _digest = _current_closure_fields(rp)
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    (tmp_path / "closure_deadbeefcafe.json").write_text(
        json.dumps({"frozen_surface_hashes": now}), encoding="utf-8")
    assert rp._closure_receipt() is None, (
        "a one-key document was accepted as a freeze-closure receipt")


@pytest.mark.parametrize("break_field", [
    "kind", "frozen_surface_digest", "steps", "artifacts", "filename"])
def test_every_recorded_closure_field_is_verified(break_field, tmp_path, monkeypatch):
    """One parametrised case per field the generator writes. A field nobody
    reads is indistinguishable from a field nobody writes."""
    import run_pipeline as rp
    real = sorted(rp.RESULTS.glob("closure_*.json"))
    if not real:
        pytest.skip("no closure receipt to derive a case from")
    doc = json.loads(real[-1].read_text(encoding="utf-8"))
    now, digest = _current_closure_fields(rp)
    doc["frozen_surface_hashes"] = now
    doc["frozen_surface_digest"] = digest
    name = f"closure_{digest[:12]}.json"
    if break_field == "kind":
        doc["kind"] = "something-else"
    elif break_field == "frozen_surface_digest":
        doc["frozen_surface_digest"] = "0" * 64
    elif break_field == "steps":
        doc["steps"] = doc["steps"][:1]
    elif break_field == "artifacts":
        doc["artifacts"] = {k: "0" * 64 for k in doc["artifacts"]}
    elif break_field == "filename":
        name = "closure_000000000000.json"
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    (tmp_path / name).write_text(json.dumps(doc), encoding="utf-8")
    assert rp._closure_receipt() is None, (
        f"a receipt with a broken {break_field} was accepted")


def test_the_real_closure_receipt_still_verifies(monkeypatch):
    """The other direction. A verifier that rejects everything would pass every
    test above and make `closure` unusable."""
    import run_pipeline as rp
    from _evaluator import frozen_surface_drift
    real = [p for p in sorted(rp.RESULTS.glob("closure_*.json"))
            if not frozen_surface_drift(
                json.loads(p.read_text(encoding="utf-8")).get(
                    "frozen_surface_hashes"))]
    if not real:
        pytest.skip("no current closure receipt; run `run_pipeline.py closure`")
    assert rp._closure_receipt() is not None, (
        "the generator's own output does not pass the verifier")


# ---- #8: a release run must leave evidence of what it observed -------------
def test_a_release_run_records_its_environment(tmp_path, monkeypatch):
    """Finding #8. `e2e --release` reported exit 0 on one host and exit 1 with
    two BLOCKED isolation probes on another, and NOTHING was written down. The
    exit code was a property of the environment presented as a property of the
    commit -- and the next session had no way to tell which it had been told.

    The reviewer proposed folding this into the closure receipt. It cannot go
    there: release REQUIRES a current closure receipt, so a closure receipt
    that recorded release's outcome would need release to have run first.
    Separate receipt, one direction: release records the closure digest it
    consumed.
    """
    import run_pipeline as rp
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    path = rp.write_release_receipt(rp.RunSpec.for_mode("release"), rp.PASS,
                                    closure_digest="deadbeefcafe",
                                    obligations={"x": "pass"})
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["kind"] == rp.RELEASE_KIND
    # Round 21c renamed `obligations` -> `declared_proofs_present` (the bare
    # name read as "these were demonstrated here") and added `isolation`.
    for field in ("git_commit", "git_dirty", "python", "platform",
                  "sandbox_available", "mode", "exit", "closure_digest",
                  "declared_proofs_present", "isolation"):
        assert field in doc, f"release receipt does not record {field}"
    assert doc["exit"] == "PASS" and doc["mode"] == "release"
    # Idempotent: the same state must not accumulate near-identical receipts in
    # an append-only directory.
    again = rp.write_release_receipt(rp.RunSpec.for_mode("release"), rp.PASS,
                                    closure_digest="deadbeefcafe",
                                    obligations={"x": "pass"})
    assert again == path
    assert len(list(tmp_path.glob("release_*.json"))) == 1


def test_a_blocked_release_is_recorded_too(tmp_path, monkeypatch):
    """The receipt exists to explain a DISAGREEMENT between hosts. Writing it
    only on success would keep exactly the case that needs explaining out of
    the record."""
    import run_pipeline as rp
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    path = rp.write_release_receipt(rp.RunSpec.for_mode("release"), rp.BLOCKED,
                                    closure_digest=None, obligations={})
    assert json.loads(path.read_text(encoding="utf-8"))["exit"] == "BLOCKED"


# ---- #5: declared / demonstrated / current-run ------------------------------
def test_obligation_verdicts_are_not_source_constants():
    """Finding #5. Every obligation was `Verdict.PASS` written into a dict, and
    `PROVEN_BY` was a string beside it. Nothing connected either to a mutation
    result, so the pipeline asserted its own coverage.

    Now `demonstrated` is DERIVED: an obligation is demonstrated only while its
    mutation case (or the acceptance test it names) exists. Delete the case and
    the obligation degrades to UNKNOWN with nobody editing a verdict."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert "OBLIGATIONS: dict[str, Verdict] = {" not in source, (
        "the hand-maintained PASS dict is still the source of truth")
    demonstrated = rp.demonstrated_obligations()
    assert set(demonstrated) == set(rp.DECLARED_OBLIGATIONS)
    for name, record in demonstrated.items():
        if record.verdict is Verdict.PASS:
            assert record.evidence, f"{name} is PASS with no evidence"


def test_deleting_a_mutation_case_degrades_its_obligation(monkeypatch):
    """The property that makes `demonstrated` a measurement rather than a
    claim."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    full = rp.demonstrated_obligations()
    victim = "packet.blinding.applied"
    assert full[victim].verdict is Verdict.PASS
    original = rp._mutation_registry()      # capture BEFORE patching, or the
    monkeypatch.setattr(rp, "_mutation_registry",   # lambda calls itself
                        lambda: original - {victim})
    degraded = rp.demonstrated_obligations()
    assert degraded[victim].verdict is not Verdict.PASS, (
        "removing the only proof left the obligation reported as PASS")


def test_a_blocked_current_run_dominates_a_demonstrated_pass():
    """THE contradiction round 21 observed in one output:

        reviewer.isolation.enforced: PASS      <- static capability
        overall: pass
        FAIL: reviewer isolation BLOCKED       <- what actually happened

    A static proof that the code CAN enforce something says nothing about
    whether it DID on this run. The run's verdict has to win."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    effective = rp.effective_obligations(
        {"reviewer.isolation.enforced": rp.RunVerdict(
            Verdict.UNKNOWN, "sandbox-exec unavailable")})
    assert effective["reviewer.isolation.enforced"].verdict is Verdict.UNKNOWN
    assert rp.overall_verdict(effective) is not Verdict.PASS, (
        "a BLOCKED current run was laundered into an overall pass")


def test_a_pass_without_evidence_is_rejected_by_the_shared_validator():
    """The invariant that catches this class already exists in the obligation
    layer (`PASS는 evidence 필수`). Round 21 reuses it through a registry seam
    instead of reimplementing the rule here."""
    import run_pipeline as rp
    from conceptgate.cg_obligations import (Assurance, DeciderKind,
                                            ObligationResult, Verdict,
                                            validate_result)
    bogus = ObligationResult("packet.blinding.applied", Verdict.PASS,
                             Assurance.RULE_CHECKED, DeciderKind.GATE,
                             evidence="")
    errors = validate_result(bogus, registry=rp.OBLIGATION_REGISTRY)
    assert any(e["code"] == "MISSING_EVIDENCE" for e in errors), errors


def test_the_suite_does_not_add_receipts_to_the_committed_results_dir():
    """Round 21, a defect I introduced with finding #8's fix.

    `write_release_receipt` was called from `run_pipeline()`, so every suite run
    that exercised `e2e --release` against the real tree deposited a file in the
    committed, append-only `results/`. And because the receipt records the git
    commit and dirty flag, a clean tree and a dirty tree produce DIFFERENT
    documents -- committing one guaranteed the next run wrote another. Tests
    must not add to the experiment's evidence.
    """
    import run_pipeline as rp
    before = {p.name for p in (HERE / "results").glob("release_*.json")}
    proc = _run("run_pipeline.py", "e2e", "--release")
    after = {p.name for p in (HERE / "results").glob("release_*.json")}
    assert after == before, (
        f"the suite wrote {sorted(after - before)} into results/ "
        f"(exit {proc.returncode})")
    # And the redirect must actually have produced a receipt somewhere, or this
    # test would pass by the receipt never being written at all.
    assert "receipt: release_" in proc.stdout or proc.returncode != PASS, (
        "no receipt was written anywhere; the redirect disabled the mechanism")


# --------------------------------------------------------------- round 21b ---
DOC_PATHS = ("docs/HANDOFF_20260810_primary_blocked.md",
             "experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md")


def _operating_docs():
    repo = HERE.parents[1]
    return [(name, (repo / name).read_text(encoding="utf-8")) for name in DOC_PATHS]


def test_the_operating_docs_state_the_real_obligation_count():
    """F7's mechanism, rewritten. The first version was a BLACKLIST of three
    strings, and `n = len(DECLARED_OBLIGATIONS)` was used only in the error
    message. Measured: replacing every `의무 11/11`/`의무 12/12` in the handoff
    with `의무 99/99` and running it gave `1 passed`.

    That is the vacuous-guard pattern -- the ninth recorded instance in this
    repository, created while fixing the eighth, inside the very finding about
    documents that disagree with code. Its docstring claimed it compared against
    the declared count, which the code did not do: a comment teaching a contract
    the code does not implement, the other pattern this session keeps recording,
    in the same function.

    `HARNESS_KNOWHOW.md` B4 is both precedent and instruction: do not ask whether
    a guard exists, ask what proposition it makes true. So this PARSES the number
    out of the prose and compares it to the code."""
    import re
    import run_pipeline as rp
    n = len(rp.DECLARED_OBLIGATIONS)
    found_any = False
    for name, text in _operating_docs():
        for pattern in (r"의무\s+(\d+)/(\d+)", r"obligations\s+(\d+)/(\d+)"):
            for match in re.finditer(pattern, text):
                found_any = True
                assert int(match.group(2)) == n, (
                    f"{name} claims {match.group(0)!r}; the code declares {n}")
    assert found_any, (
        "no obligation count appears in the operating docs at all -- the entry "
        "block must state what a reader should expect")


def test_the_operating_docs_state_the_real_offline_exit_code():
    """Parsed, then compared to the actual process. `e2e --offline` returns 2
    because it runs no reviewer, and a document promising 0 makes a reader treat
    an honest PARTIAL as a failure -- or a failure as success."""
    import re
    actual = _run("run_pipeline.py", "e2e", "--offline").returncode
    claimed_any = False
    for name, text in _operating_docs():
        for match in re.finditer(r"e2e --offline\s+exit (\d+)", text):
            claimed_any = True
            assert int(match.group(1)) == actual, (
                f"{name} promises offline exit {match.group(1)}; it is {actual}")
    assert claimed_any, "no document states the offline exit code"


def test_the_agent_reviewer_procedure_names_the_launcher_and_the_receipt():
    """Round 21c. The handoff told a reader to submit label files by hand and
    call the adjudicator with no `--isolation-receipt`. With `kind: agent` the
    code REFUSES that procedure -- the entry document described a workflow the
    program rejects.

    This matters more than ordinary drift: this handoff IS the corpus a subject
    agent reads. If it contradicts the code, a subject failure cannot be
    attributed to retrieval rather than to the document."""
    joined = "\n".join(text for _, text in _operating_docs())
    for token in ("reviewer_runner.py", "--command", "--labels-out",
                  "--isolation-receipt"):
        assert token in joined, (
            f"the operating docs never mention {token}; an agent reviewer "
            "cannot be run or adjudicated by following them")


def test_the_operating_docs_do_not_describe_the_removed_receipt_scheme():
    """`produced_by` plus a public `receipt_sha256` was the FORGEABLE scheme
    round 21 replaced with an HMAC. A document presenting it as current teaches
    a reader that a hand-written receipt would be caught -- the opposite of what
    was true."""
    for name, text in _operating_docs():
        assert "`produced_by`와" not in text, (
            f"{name} still presents the removed produced_by scheme as current")
    joined = "\n".join(text for _, text in _operating_docs())
    assert "HMAC" in joined, "no document says how a receipt is authenticated"


def _tree_with_agent_reviewer(tmp_path, *, receipt: dict | None,
                              write_receipt: bool = True) -> Path:
    """A COPY of the experiment whose assignment declares an agent reviewer.

    F2's lesson, and why this helper exists: doctor's agent branch had never
    executed. The assignment ships `UNASSIGNED`, so nothing reached the code --
    and code that referenced a field the receipt does not have survived four
    rounds. Calling the function directly would have reproduced neither. A test
    for a guarded branch has to MAKE THE STATE that reaches it.
    """
    import shutil
    repo = HERE.parents[1]
    target = tmp_path / "experiments" / HERE.name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(repo / "conceptgate", tmp_path / "conceptgate")
    shutil.copytree(HERE, target)
    path = target / "safety_audit_reviewer_assignment.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["status"] = "ASSIGNED"
    doc["reviewers"] = [{"reviewer_id": "agent-A", "kind": "agent",
                         "isolation": "reviewer_runner.py packet-only bundle"}]
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    if write_receipt and receipt is not None:
        (target / "results" / "reviewer_isolation_agent-A.json").write_text(
            json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
    return target


def _launcher_receipt(target: Path) -> dict:
    """A REAL receipt, produced by the launcher inside `target`."""
    code = (
        "import json, sys, tempfile\n"
        "from pathlib import Path\n"
        "sys.path.insert(0, '.')\n"
        "import reviewer_runner as rr\n"
        "d = Path(tempfile.mkdtemp()); p = d / 'packet.json'\n"
        "p.write_text(json.dumps({'reviewer_packet': [{'blind_id': 'R0000'}]}))\n"
        "b = rr.build_reviewer_bundle(p, d / 'bundle')\n"
        "print(json.dumps(rr.run_reviewer(b, 'agent-A')))\n")
    proc = subprocess.run([sys.executable, "-c", code], cwd=target,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        pytest.skip(f"launcher unavailable here: {proc.stderr[-200:]}")
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_doctor_does_not_crash_when_an_agent_reviewer_is_assigned(tmp_path):
    """F2, reproduced before the fix.

        FileNotFoundError: .../results/missing

    `doctor` verified the receipt with `packet=RESULTS / doc.get("packet_file",
    "missing")`, and `IsolationReceipt.as_dict()` has no `packet_file`. So the
    HAPPY path -- a correctly signed, passing receipt -- crashed the diagnostic
    with a traceback. Reported as "may conflict"; measured as a crash."""
    target = _tree_with_agent_reviewer(tmp_path,
                                       receipt=None, write_receipt=False)
    receipt = _launcher_receipt(target)
    (target / "results" / "reviewer_isolation_agent-A.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
    proc = subprocess.run([sys.executable, "run_pipeline.py", "doctor"],
                          cwd=target, capture_output=True, text=True, timeout=300)
    assert "Traceback" not in proc.stderr, (
        f"doctor crashed instead of reporting:\n{proc.stderr[-600:]}")
    line = next((l for l in proc.stdout.splitlines()
                 if "agent reviewer isolation" in l), "")
    assert line, f"doctor printed no agent-reviewer row:\n{proc.stdout[-800:]}"
    assert "[ok" in line, f"a valid passing receipt was not accepted: {line!r}"


def test_doctor_reports_blocked_for_a_forged_agent_receipt(tmp_path):
    """The other direction: a receipt this host cannot have signed must not be
    accepted, and must not crash either."""
    forged = {"reviewer_id": "agent-A", "status": "PASS",
              "packet_sha256": "0" * 64, "assignment_sha256": "0" * 64,
              "sandbox_profile_sha256": "0" * 64, "allowed_probe_passed": True,
              "forbidden_probes": [], "reviewer_command_sha256": None,
              "reviewer_output_sha256": None, "signature": "0" * 64}
    target = _tree_with_agent_reviewer(tmp_path, receipt=forged)
    proc = subprocess.run([sys.executable, "run_pipeline.py", "doctor"],
                          cwd=target, capture_output=True, text=True, timeout=300)
    assert "Traceback" not in proc.stderr, proc.stderr[-400:]
    line = next((l for l in proc.stdout.splitlines()
                 if "agent reviewer isolation" in l), "")
    assert "[ --" in line or "BLOCKED" in line, (
        f"a forged receipt was not reported as BLOCKED: {line!r}")


def test_the_receipt_verifier_separates_authenticity_from_packet_binding():
    """Why the fix is a SPLIT and not a new `packet_file` field.

    A path inside a signed receipt is host-specific and would have to be
    re-resolved by every reader. What `doctor` actually needs is: is this
    receipt authentic, is it bound to the frozen assignment, and what does it
    say. It has no packet to compare against -- the packet belongs to an audit
    run. Making the packet comparison optional inside one function would be the
    fail-open shape this repository keeps removing, so there are two functions
    and the caller states which question it is asking."""
    import reviewer_runner as rr
    assert hasattr(rr, "authenticate_isolation_receipt")
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    assert 'doc.get("packet_file"' not in source, (
        "doctor still guesses a packet path out of the receipt")


def test_the_release_receipt_does_not_overclaim_its_obligation_evidence(
        tmp_path, monkeypatch):
    """Round 21c. The receipt recorded `obligations: {name: "pass"}`, and
    `demonstrated` only means "a proof is declared and present" -- not that the
    12 mutations passed in THIS run. A later session reading `12/12 pass` in a
    release receipt would reasonably conclude the stronger thing.

    The field name has to carry the strength of the claim, because the field is
    all a future reader gets."""
    import run_pipeline as rp
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    path = rp.write_release_receipt(
        rp.RunSpec.for_mode("release"), rp.PASS, closure_digest="d" * 12,
        obligations={"x": "pass"},
        isolation=[{"probe": "answer_key", "status": "DENIED"}],
        allowed_probe_passed=True)
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert "obligations" not in doc, (
        "the bare name `obligations` reads as 'these were demonstrated here'")
    assert "declared_proofs_present" in doc
    assert "what_this_is_not" in doc["declared_proofs_present"], (
        "the receipt does not say what the field is NOT")


def test_the_release_receipt_records_probe_states_not_binary_presence(
        tmp_path, monkeypatch):
    """Round 21c. `sandbox_available` recorded only whether /usr/bin/sandbox-exec
    exists. The reviewer ran the SAME commit in a /private/tmp clean clone and
    got exit 1 with four BLOCKED probes -- and the receipt could not express the
    difference between that host and this one. A field that cannot distinguish
    the two outcomes it exists to explain is not evidence."""
    import run_pipeline as rp
    monkeypatch.setattr(rp, "RESULTS", tmp_path)
    path = rp.write_release_receipt(
        rp.RunSpec.for_mode("release"), rp.BLOCKED, closure_digest=None,
        obligations={}, allowed_probe_passed=False,
        isolation=[{"probe": "answer_key", "status": "BLOCKED"},
                   {"probe": "host_transcripts", "status": "DENIED"}])
    doc = json.loads(path.read_text(encoding="utf-8"))
    iso = doc["isolation"]
    assert iso["allowed_probe_passed"] is False
    assert iso["probe_states"] == {"answer_key": "BLOCKED",
                                   "host_transcripts": "DENIED"}
