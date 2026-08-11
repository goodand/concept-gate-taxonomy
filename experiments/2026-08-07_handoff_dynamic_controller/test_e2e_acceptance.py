#!/usr/bin/env python3
"""GATE — every production obligation the offline E2E claims to cover must be
shown to FAIL the E2E when it is removed from the SOURCE.

AUDIT SURFACE.

Round 17 asked for this; round 18 showed the first version did not deliver it.
That version monkeypatched a function to always succeed, which the E2E caught
by its own separate comparison -- so the real risk, the ADJUDICATOR dropping
its qualification call site, went undetected:

    e2e_passed_with_adjudicator_qualification_disabled: True

And "all stages are covered" was checked as `len(stages) >= 7 and
len(mutations) >= 5`, a count, not a mapping. Two unprotected stages passed it.

This version follows the two mechanisms this repository already trusts:

  * `run_calibration.py`'s APPLIED-CHECK: a mutation that turns out to be a
    no-op is a HARNESS DEFECT, not evidence about the evaluator. Here each
    mutation compares the source sha256 before and after and fails if they
    match.
  * `conceptgate/cg_obligations.py`'s typed verdicts: a claim needs evidence,
    and anything that is not a demonstrated PASS is not a pass.

Each obligation names the production file it lives in, the source it deletes,
and the string the E2E must print. Mutations are applied to the real file and
the E2E is run in a FRESH SUBPROCESS, because an in-process monkeypatch cannot
show that the call site exists -- only that a function can be replaced.
"""
from __future__ import annotations

import hashlib
import json
import contextlib
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    stage_id: str          # which printed E2E stage this obligation guards
    target: str            # production file the obligation lives in
    remove: str            # exact source fragment whose deletion disables it
    replace_with: str      # what to put in its place (keeps syntax valid)
    expected_signal: str   # what the E2E must print once it is gone
    mode: str = "--offline"  # some obligations only run under --release


OBLIGATIONS = (
    Obligation(
        obligation_id="audit.input-validated",
        stage_id="audit.input-validated",
        target="make_safety_audit_blind_input.py",
        remove="    traces_by_key = validate_audit_input(data, spec, source=result_path.name)",
        replace_with="    traces_by_key = {_cell_key(t): t for t in (data.get('traces') or [])}",
        expected_signal="audit gate ACCEPTED",
    ),
    Obligation(
        obligation_id="audit.provenance.bytes-compared",
        stage_id="audit.input-validated",
        target="run_live_phase_c.py",
        # The round-18 defect itself: the completed row was matched by
        # `output_file` NAME and the artifact's bytes were never compared, so
        # a result edited after its attempt completed was accepted. Disabling
        # the byte comparison is the one mutation that isolates it -- the CLI
        # and `build()` both call the verifier, so removing either call site
        # alone leaves the other enforcing (defence in depth, which is why
        # neither of those is the obligation).
        remove='        if entry.get("output_sha256") == output_sha256:',
        replace_with='        if entry.get("output_sha256") is not None:',
        expected_signal="ACCEPTED a result edited after its attempt completed",
    ),
    Obligation(
        obligation_id="audit.provenance.propagated",
        stage_id="bundle.persisted",
        target="apply_safety_audit.py",
        # The receipt must be PROMOTED into the bundle. Round 19: it reached
        # the packet and stopped, so the final JSON could not be told apart
        # from an audit of a real run.
        remove='        "provenance": (None if provenance is None else {',
        replace_with='        "provenance": (None if True else {',
        expected_signal="does not state its provenance mode",
    ),
    Obligation(
        obligation_id="packet.blinding.applied",
        stage_id="packet.blinded",
        target="make_safety_audit_blind_input.py",
        # Blinding is a property of what the packet CONTAINS. Re-adding the
        # arm is the smallest regression that breaks it, and the E2E's leak
        # scan must see it.
        remove='                "case_id": cid,\n                "case_query"',
        replace_with='                "case_id": cid, "arm": row.get("arm"),\n                "case_query"',
        expected_signal="packet leaks",
    ),
    Obligation(
        obligation_id="reviewer.qualification.required",
        stage_id="reviewer.qualification-enforced",
        target="apply_safety_audit.py",
        remove="        wrong = _qualify_reviewer(doc)",
        replace_with="        wrong = []",
        expected_signal="accepted an unqualified reviewer",
    ),
    Obligation(
        obligation_id="reviewer.assignment.frozen",
        stage_id="reviewer.assignment-enforced",
        target="apply_safety_audit.py",
        remove='        if doc["reviewer_id"] not in declared_ids:',
        replace_with="        if False:",
        expected_signal="accepted an undeclared reviewer",
    ),
    Obligation(
        obligation_id="reviewer.isolation.enforced",
        stage_id="reviewer.assignment-enforced",
        target="reviewer_runner.py",
        # Removing `elif leaked:` was tried first and is a no-op IN EFFECT:
        # with nothing leaking there is no leak to miss, so the source changed
        # and the observable behaviour did not. run_calibration's applied-check
        # catches no-op mutations at the source level; this is the same trap
        # one level deeper -- an applied mutation on an unexercised path.
        #
        # So the mutation opens the boundary instead: a profile that allows
        # everything makes the forbidden probes reachable, and the E2E must
        # notice.
        # Round 21 replaced v1 with v2 here (finding #2), so the fragment moved.
        # The mutation is unchanged in kind: open the boundary completely.
        remove='    return seatbelt_profile_v2(HERE, HERE / "results")',
        replace_with='    return "(version 1)\\n(allow default)"',
        expected_signal="reached",
        mode="--release",
    ),
    Obligation(
        obligation_id="bundle.written.to.disk",
        stage_id="bundle.persisted",
        target="apply_safety_audit.py",
        remove="    out.write_text(json.dumps(data, ensure_ascii=False, indent=1),",
        replace_with="    _ = (lambda *a, **k: None)(json.dumps(data, ensure_ascii=False, indent=1),",
        expected_signal="no final bundle",
    ),
    Obligation(
        obligation_id="reviewer.count.enforced",
        stage_id="adjudication.applied",
        target="apply_safety_audit.py",
        remove='    if len(ids) < min_reviewers and not spec["allow_single_reviewer"]:',
        replace_with="    if False:",
        expected_signal="single reviewer produced a bundle",
    ),
)

# Obligations with no E2E signal YET. Recorded rather than dropped: an
# obligation the E2E does not observe is a gap in the E2E, and the honest
# place for it is a list someone reads, not silence.
NO_SIGNAL_YET: dict[str, str] = {}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_e2e_subprocess(cwd: Path | None = None, mode: str = "--offline"
                        ) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "run_pipeline.py", "e2e", mode],
        cwd=cwd or HERE, capture_output=True, text=True, timeout=180)


@contextlib.contextmanager
def _mutation_workspace():
    """A throwaway COPY of the experiment directory. Mutations happen there.

    Round 19, finding #4: mutations edited the active worktree's production
    files and restored them in `finally`. That is safe only on a clean exit --
    a SIGKILL, a parallel pytest run, or another session reading the tree at
    the wrong moment observes or keeps mutated production code. "Fresh
    subprocess" solves Python's module cache, not the filesystem.

    A copy rather than `git worktree add HEAD`: the mutation must be applied
    to the CURRENT working state, and a worktree at HEAD silently tests the
    last commit instead -- which would make this gate report on code nobody
    is running.

    The workspace precedent is the same idea one level up: experiment lines
    live in separate worktrees so one cannot affect another or main
    (`docs/EXPERIMENT_METHODOLOGY.md` §4).
    """
    with tempfile.TemporaryDirectory(prefix="mut-ws-") as tmp:
        # Mirror the real layout: <repo>/experiments/<name>/ plus
        # <repo>/conceptgate. run_pipeline resolves cg_obligations through
        # HERE.parents[1], so a flat copy would make the mutant fail on an
        # ImportError and every mutation would look "detected" for the wrong
        # reason -- a false positive in the gate that is supposed to be the
        # last line of defence.
        repo = Path(tmp) / "repo"
        target = repo / "experiments" / HERE.name
        shutil.copytree(
            HERE, target,
            ignore=shutil.ignore_patterns("__pycache__", "audit_workspace",
                                          ".pytest_cache"))
        shutil.copytree(HERE.parents[1] / "conceptgate", repo / "conceptgate",
                        ignore=shutil.ignore_patterns("__pycache__"))
        yield target


def test_the_unmutated_e2e_does_not_fail():
    """Control. Without it, a mutation could be 'detected' because the E2E is
    broken for an unrelated reason.

    PASS (0) or PARTIAL (2) are both acceptable here; FAIL (1) is not. PARTIAL
    means every step ran but some stage has no mutation guarding it -- which
    is exactly what this file is for."""
    proc = _run_e2e_subprocess()
    assert proc.returncode in (0, 2), proc.stdout + proc.stderr
    assert "FAIL" not in proc.stdout, proc.stdout


@pytest.mark.parametrize("ob", [o for o in OBLIGATIONS
                                if o.obligation_id not in NO_SIGNAL_YET],
                         ids=lambda o: o.obligation_id)
def test_removing_a_production_obligation_makes_the_e2e_fail(ob, tmp_path):
    source_path = HERE / ob.target
    original = source_path.read_text(encoding="utf-8")
    assert ob.remove in original, (
        f"{ob.obligation_id}: the source this mutation deletes is no longer in "
        f"{ob.target}. Either it moved -- update the obligation -- or it was "
        "removed, which is what this gate exists to catch.")
    mutated = original.replace(ob.remove, ob.replace_with, 1)

    # APPLIED-CHECK, borrowed from run_calibration.py: a no-op mutation tells
    # you nothing about the system, so treat it as a harness defect rather
    # than as a passing test.
    assert _sha256(mutated) != _sha256(original), (
        f"{ob.obligation_id}: mutation was a NO-OP")

    manifest = {
        "obligation_id": ob.obligation_id,
        "target": ob.target,
        "before_sha256": _sha256(original),
        "after_sha256": _sha256(mutated),
        "mutation_applied": True,
        "expected_signal": ob.expected_signal,
        "fresh_subprocess": True,
    }
    with _mutation_workspace() as work_dir:
        # The active tree is never written to. A crash here leaves a temp
        # worktree behind at worst, not mutated production code.
        (work_dir / ob.target).write_text(mutated, encoding="utf-8")
        manifest["tree"] = str(work_dir)
        if ob.mode == "--release":
            # `--release` requires a closure receipt describing the CURRENT
            # surface, and the mutation just changed it. Re-closing inside the
            # workspace makes the mutant a coherent tree: without this every
            # release-mode mutation would be "detected" by the closure gate
            # rather than by the check under test -- a false positive in the
            # gate of last resort.
            closed = subprocess.run(
                [sys.executable, "run_pipeline.py", "closure"], cwd=work_dir,
                capture_output=True, text=True, timeout=300)
            manifest["workspace_closure_exit"] = closed.returncode
            assert closed.returncode == 0, closed.stdout[-800:]
        proc = _run_e2e_subprocess(cwd=work_dir, mode=ob.mode)

    manifest["observed_exit"] = proc.returncode
    manifest["observed_signal"] = ob.expected_signal in proc.stdout
    (tmp_path / "mutation.json").write_text(json.dumps(manifest, indent=1),
                                            encoding="utf-8")

    assert proc.returncode == 1, (
        f"{ob.obligation_id}: the E2E did not FAIL with this obligation "
        f"removed (exit {proc.returncode}; 2 = PARTIAL, which is not "
        f"detection), so "
        f"it does not actually cover it.\n{json.dumps(manifest, indent=1)}\n"
        f"{proc.stdout[-2000:]}")
    assert ob.expected_signal in proc.stdout, (
        f"{ob.obligation_id}: the E2E failed, but not with the expected "
        f"signal {ob.expected_signal!r} -- it may be failing for an unrelated "
        f"reason.\n{proc.stdout[-2000:]}")


def test_mutations_never_touch_the_active_worktree():
    """Round 19, finding #4. The obligations still have to be FINDABLE in the
    active source -- that is how a moved check is caught -- but nothing here
    may write to it."""
    for ob in OBLIGATIONS:
        assert ob.remove in (HERE / ob.target).read_text(encoding="utf-8"), (
            f"{ob.obligation_id}: its source fragment is not in {ob.target}")
    source = (HERE / "test_e2e_acceptance.py").read_text(encoding="utf-8")
    assert "_mutation_workspace" in source, (
        "mutations must run in a throwaway copy, not the active tree")
    assert "shutil.copytree" in source


def test_obligations_match_the_pipeline_registry_exactly():
    """SET equality on OBLIGATIONS, not on stages.

    Round 20, finding #1: coverage was a set difference over stages, so an
    explicitly unverified obligation hid behind a guarded sibling on the same
    stage. The unit of completion is the obligation.
    """
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    mutated = {o.obligation_id for o in OBLIGATIONS
               if o.obligation_id not in NO_SIGNAL_YET}
    declared = set(rp.DECLARED_OBLIGATIONS)
    assert mutated <= declared, (
        f"mutations for obligations the pipeline does not declare: "
        f"{sorted(mutated - declared)}")
    for name, record in rp.demonstrated_obligations().items():
        if record.verdict is Verdict.PASS:
            mechanism = rp.PROVEN_BY[name]
            if mechanism == "mutation":
                assert name in mutated, (
                    f"{name} is declared PASS by mutation but no mutation "
                    "demonstrates it")
            else:
                # An acceptance-test mechanism is checked in
                # test_pipeline_gates.test_every_obligation_records_how_it_is_proven
                assert mechanism.startswith("acceptance:"), mechanism
        else:
            # Round 21: the reason travels with the verdict. A separate
            # UNKNOWN_REASONS table was one more thing to keep in step.
            assert record.evidence, f"{name} is not PASS and records no reason"
    # Every obligation must point at a stage the E2E actually prints.
    stages = set(rp.STAGE_IDS.values())
    for ob in OBLIGATIONS:
        assert ob.stage_id in stages, (
            f"{ob.obligation_id} guards stage {ob.stage_id!r}, which the E2E "
            "does not print")


def test_the_e2e_reports_partial_while_any_obligation_is_unknown():
    import run_pipeline as rp
    from conceptgate.cg_obligations import Verdict
    if rp.overall_verdict() is Verdict.PASS:
        pytest.skip("nothing unknown; the PARTIAL path has nothing to report")
    proc = _run_e2e_subprocess()
    assert "PARTIAL" in proc.stdout, (
        "the E2E reports PASS while obligations are unproven")
    assert proc.returncode == 2, (
        f"unproven obligations must exit BLOCKED (2), got {proc.returncode}")
