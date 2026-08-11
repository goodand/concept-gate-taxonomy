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
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


@dataclass(frozen=True)
class Obligation:
    obligation_id: str
    target: str            # production file the obligation lives in
    remove: str            # exact source fragment whose deletion disables it
    replace_with: str      # what to put in its place (keeps syntax valid)
    expected_signal: str   # what the E2E must print once it is gone


OBLIGATIONS = (
    Obligation(
        obligation_id="audit.input.validated",
        target="make_safety_audit_blind_input.py",
        remove="    traces_by_key = validate_audit_input(data, spec, source=result_path.name)",
        replace_with="    traces_by_key = {_cell_key(t): t for t in (data.get('traces') or [])}",
        expected_signal="audit gate ACCEPTED",
    ),
    Obligation(
        obligation_id="audit.provenance.bytes-compared",
        target="_provenance.py",
        # The round-18 defect itself: the completed row was matched by
        # `output_file` NAME and the artifact's bytes were never compared, so
        # a result edited after its attempt completed was accepted. Disabling
        # the byte comparison is the one mutation that isolates it -- the CLI
        # and `build()` both call the verifier, so removing either call site
        # alone leaves the other enforcing (defence in depth, which is why
        # neither of those is the obligation).
        remove="        if recorded == result_sha:",
        replace_with="        if recorded is not None:",
        expected_signal="ACCEPTED a result edited after its attempt completed",
    ),
    Obligation(
        obligation_id="reviewer.qualification.required",
        target="apply_safety_audit.py",
        remove="        wrong = _qualify_reviewer(doc)",
        replace_with="        wrong = []",
        expected_signal="accepted an unqualified reviewer",
    ),
    Obligation(
        obligation_id="reviewer.assignment.frozen",
        target="apply_safety_audit.py",
        remove='        if doc["reviewer_id"] not in declared_ids:',
        replace_with="        if False:",
        expected_signal="",   # see test below: this one has no E2E signal yet
    ),
    Obligation(
        obligation_id="bundle.written.to.disk",
        target="apply_safety_audit.py",
        remove="    out.write_text(json.dumps(data, ensure_ascii=False, indent=1),",
        replace_with="    _ = (lambda *a, **k: None)(json.dumps(data, ensure_ascii=False, indent=1),",
        expected_signal="no final bundle",
    ),
    Obligation(
        obligation_id="reviewer.count.enforced",
        target="apply_safety_audit.py",
        remove='    if len(ids) < min_reviewers and not spec["allow_single_reviewer"]:',
        replace_with="    if False:",
        expected_signal="single reviewer produced a bundle",
    ),
)

# Obligations with no E2E signal YET. Recorded rather than dropped: an
# obligation the E2E does not observe is a gap in the E2E, and the honest
# place for it is a list someone reads, not silence.
NO_SIGNAL_YET = {
    "reviewer.assignment.frozen":
        "the E2E always submits reviewers that ARE in the assignment, so "
        "deleting this check changes nothing it observes. Needs an E2E stage "
        "that submits an undeclared reviewer_id, the same way stage 6 submits "
        "an unqualified one.",
}


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _run_e2e_subprocess() -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "run_pipeline.py", "e2e", "--offline"],
        cwd=HERE, capture_output=True, text=True, timeout=120)


def test_the_unmutated_e2e_passes():
    """Control. Without it, a mutation could be 'detected' because the E2E is
    broken for an unrelated reason."""
    proc = _run_e2e_subprocess()
    assert proc.returncode == 0, proc.stdout + proc.stderr


@pytest.mark.parametrize("ob", [o for o in OBLIGATIONS
                                if o.obligation_id not in NO_SIGNAL_YET],
                         ids=lambda o: o.obligation_id)
def test_removing_a_production_obligation_makes_the_e2e_fail(ob, tmp_path):
    path = HERE / ob.target
    original = path.read_text(encoding="utf-8")
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
    try:
        path.write_text(mutated, encoding="utf-8")
        proc = _run_e2e_subprocess()
    finally:
        path.write_text(original, encoding="utf-8")

    manifest["observed_exit"] = proc.returncode
    manifest["observed_signal"] = ob.expected_signal in proc.stdout
    (tmp_path / "mutation.json").write_text(json.dumps(manifest, indent=1),
                                            encoding="utf-8")

    assert proc.returncode != 0, (
        f"{ob.obligation_id}: the E2E passed with this obligation removed, so "
        f"it does not actually cover it.\n{json.dumps(manifest, indent=1)}\n"
        f"{proc.stdout[-2000:]}")
    assert ob.expected_signal in proc.stdout, (
        f"{ob.obligation_id}: the E2E failed, but not with the expected "
        f"signal {ob.expected_signal!r} -- it may be failing for an unrelated "
        f"reason.\n{proc.stdout[-2000:]}")


def test_the_source_was_restored_after_every_mutation():
    """The mutations edit real production files. If a `finally` ever fails to
    restore one, this is the check that says so instead of the next fifty
    tests failing mysteriously."""
    for ob in OBLIGATIONS:
        assert ob.remove in (HERE / ob.target).read_text(encoding="utf-8"), (
            f"{ob.target} was not restored after mutating {ob.obligation_id}")


def test_every_e2e_stage_maps_to_an_obligation_or_a_recorded_gap():
    """Round 18: the previous version compared COUNTS -- `>= 7 stages` and
    `>= 5 mutations` -- so two unprotected stages passed. This maps them."""
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    stages = sorted(set(int(n) for n in
                        __import__("re").findall(r'print\(f?"  \[(\d)\]', source)))
    covered = len(OBLIGATIONS) - len(NO_SIGNAL_YET)
    assert stages == list(range(1, len(stages) + 1)), (
        f"stage numbering has a gap: {stages}")
    assert covered >= 5, f"only {covered} obligations carry an E2E signal"
    for name, reason in NO_SIGNAL_YET.items():
        assert any(o.obligation_id == name for o in OBLIGATIONS), name
        assert len(reason) > 40, f"{name}: reason is too thin to review"
