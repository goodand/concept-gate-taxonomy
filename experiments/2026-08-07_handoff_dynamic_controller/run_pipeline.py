#!/usr/bin/env python3
"""Single entry point: `doctor` (what is the state?) and `e2e` (does the whole
path still work?).

WHY THIS EXISTS. Five consecutive review rounds found defects of the same
shape -- a check that existed but was not wired, a document that taught a
contract the code did not implement, a gate that passed because it could not
run. Each was fixed individually. That was the wrong response: the repeat was
not five separate mistakes, it was the absence of anything that runs the whole
path end to end. Nothing ever executed
    primary artifact -> audit gate -> packet -> labels -> adjudication -> bundle
in one go, so every gap between two stages was invisible until a human read
the code.

This is not a new invention. The frozen decision
`DESIGN_DECISION_surface_separation.md` (2026-07-28) already established the
principle, as "canonical builder -- the only permitted path":

    fixture -> validate -> qualify -> build_payload -> render -> manifest -> run

and its required test #7: *smoke, real run, and re-run all use the same
builder function*. `e2e --offline` extends that rule from the payload builder
to the whole pipeline. It calls the PRODUCTION entry points -- not copies of
them -- so a stage that is not wired fails here rather than in review.

    python3 run_pipeline.py doctor          # state of every gate, no side effects
    python3 run_pipeline.py e2e --offline   # whole path in a temp dir, no provider

`e2e --offline` makes NO provider calls, writes nothing outside its temp
directory, and consumes no primary attempt. Run it before the ~12-minute paid
qualification, not after.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
# The repository root, for conceptgate.cg_obligations. Imported rather than
# re-implemented: its Verdict/aggregate already say "PASS only when everything
# is PASS, otherwise UNKNOWN", and a second verdict vocabulary in this
# experiment is exactly the duplication round 20 objected to. If it cannot be
# imported, that is a BLOCKED condition, not a reason to define a local enum.
sys.path.insert(0, str(HERE.parents[1]))

from conceptgate.cg_obligations import (  # noqa: E402
    Assurance, DeciderKind, ObligationResult, ObligationSpec, Verdict,
    certify)
import apply_safety_audit as asa  # noqa: E402
from _provenance import SYNTHETIC, ProvenanceError, verify_run  # noqa: E402
import make_safety_audit_blind_input as mkblind  # noqa: E402
from _evaluator import evaluate  # noqa: E402
import run_live_phase_c as live  # noqa: E402
from run_calibration import load, reference_trace  # noqa: E402
from _runner import Corpus  # noqa: E402

RESULTS = HERE / "results"
SPEC = json.loads((HERE / "safety_audit_spec.json").read_text(encoding="utf-8"))

# Three-value exit vocabulary, matching scripts/run_gates.py's PASS/FAIL/
# BLOCKED table -- but carried in the EXIT CODE, not only in the printed text.
# Round 17: `doctor` printed "BLOCKED is not a pass" and returned 0, so every
# machine reading it (CI, a shell harness, the next agent) saw success. The
# repository had already met this in run_gates.py and answered it with a
# warning in prose; a warning is not a mechanism.
PASS, FAIL, BLOCKED = 0, 1, 2

# One sentence, one place. `RunSpec.for_mode` raises it and `refuse_primary`
# prints it, so the CLI and the library cannot disagree about why primary is
# unavailable. Round 21, finding #4.
PRIMARY_REFUSAL = ("primary mode is not implemented in run_pipeline.py; it has "
                   "no provider, no authorization check and claims no attempt")

# Stage ids, printed by the E2E and required to match the acceptance gate's
# registry EXACTLY. Round 19, finding #3: "obligation mapping" was still a
# count (`covered >= 5`), so two unprotected stages passed. A count cannot
# say WHICH stage is unprotected.
STAGE_IDS = {
    1: "primary.synthetic-built",
    2: "audit.input-validated",
    3: "packet.built",
    4: "packet.blinded",
    5: "reviewer.qualification-scored",
    6: "reviewer.qualification-enforced",
    7: "reviewer.assignment-enforced",
    8: "adjudication.applied",
    9: "bundle.persisted",
    # Round 21, finding #3. Not an integer: it sits between 7 and 8 and
    # renumbering the others would break every mutation's expected_signal.
    "7b": "reviewer.labels-from-launcher",
    "7c": "audit.isolation-required",
}

# OBLIGATIONS -- the unit of completion.
#
# Round 20, finding #1: coverage was computed as a set difference over STAGES,
# so `reviewer.assignment.frozen` -- explicitly unverified -- was hidden
# because another obligation on the same stage was guarded. "3 unguarded
# stages" was true; "3 unguarded obligations" was not. A stage can carry
# several obligations, and a stage is covered only when all of them are.
#
# THREE LAYERS, round 21 finding #5. Until now there was one: a dict with
# `Verdict.PASS` typed into it ten times, plus `PROVEN_BY` strings beside it.
# Nothing connected either to a mutation result, so the pipeline certified its
# own coverage -- and one observed run printed
#
#     reviewer.isolation.enforced: PASS        <- the constant
#     overall: pass
#     FAIL: reviewer isolation BLOCKED         <- what actually happened
#
# at the same time. A static claim that the code CAN enforce something is not a
# claim that it DID on this run, and the run has to win.
#
#   DECLARED      what this pipeline is responsible for   (this tuple)
#   DEMONSTRATED  whether a proof for it exists           (derived, see below)
#   CURRENT-RUN   what THIS execution observed            (recorded as it goes)
#
# `effective_obligations` combines them with current-run dominating.
DECLARED_OBLIGATIONS: tuple[str, ...] = (
    "audit.input-validated",
    "audit.provenance.bytes-compared",
    "audit.provenance.propagated",
    "packet.blinding.applied",
    "reviewer.qualification.required",
    "reviewer.assignment.frozen",
    "reviewer.count.enforced",
    "bundle.written.to.disk",
    "reviewer.isolation.enforced",
    "reviewer.labels.from-launcher",
    "audit.isolation.required",
    "freeze.closure.current",
)

# HOW each obligation is demonstrated. Round 20's design deliberately limits
# mutation to obligations where removing the code is the only way to observe
# the absence; the rest are ordinary CLI acceptance tests. Recording the
# mechanism per obligation stops "PASS" from meaning two different things.
PROVEN_BY: dict[str, str] = {
    "audit.input-validated":           "mutation",
    "audit.provenance.bytes-compared": "mutation",
    "audit.provenance.propagated":     "mutation",
    "packet.blinding.applied":         "mutation",
    "reviewer.qualification.required": "mutation",
    "reviewer.assignment.frozen":      "mutation",
    "reviewer.count.enforced":         "mutation",
    "bundle.written.to.disk":          "mutation",
    "reviewer.isolation.enforced":     "mutation",
    "reviewer.labels.from-launcher":   "mutation",
    "audit.isolation.required":        "mutation",
    "freeze.closure.current":
        "acceptance:test_release_refuses_without_a_current_closure_receipt",
}

# Why each UNKNOWN is still UNKNOWN. Empty is the goal; a name here is a
# commitment someone can read, not silence.
UNKNOWN_REASONS: dict[str, str] = {}

# The obligation layer's invariants, applied to THIS experiment's names through
# the registry seam added in round 21 (correction C3). `certify()` could not be
# used as-is: none of these names are in the global OBLIGATION_REGISTRY, so
# every result came back UNKNOWN_OBLIGATION and the verdict was an
# unconditional FAIL. Registering experiment obligations in the shared domain
# registry would pollute it; reimplementing the rules here would make a
# validated mechanism exist twice. The seam avoids both -- and it brings the one
# rule that catches finding #5: PASS requires non-empty evidence.
OBLIGATION_REGISTRY: dict[str, ObligationSpec] = {
    name: ObligationSpec(DeciderKind.GATE, Assurance.RULE_CHECKED,
                         "run_pipeline.run_pipeline", Verdict.UNKNOWN)
    for name in DECLARED_OBLIGATIONS
}


@dataclass(frozen=True)
class RunVerdict:
    """A verdict WITH the observation behind it. `evidence` is not decoration:
    the shared validator rejects a PASS that carries none."""
    verdict: Verdict
    evidence: str = ""


def _mutation_registry() -> set[str]:
    """Obligation ids that have a mutation case in the acceptance gate.

    Read from the SOURCE with `ast`, not by importing: importing a test module
    from production code inverts the layering, and this needs data, not
    execution. If the file is unreadable the set is empty, which degrades every
    mutation-proven obligation to UNKNOWN -- the fail-closed direction.
    """
    import ast
    try:
        tree = ast.parse((HERE / "test_e2e_acceptance.py").read_text(
            encoding="utf-8"))
    except (OSError, SyntaxError):
        return set()
    return {node.value.value for node in ast.walk(tree)
            if isinstance(node, ast.keyword) and node.arg == "obligation_id"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)}


def _acceptance_test_exists(test_name: str) -> Path | None:
    for path in sorted(HERE.glob("test_*.py")):
        if f"def {test_name}" in path.read_text(encoding="utf-8"):
            return path
    return None


def demonstrated_obligations() -> dict[str, RunVerdict]:
    """Whether a PROOF exists for each declared obligation, derived.

    Round 21, finding #5: this used to be ten `Verdict.PASS` literals. Deleting
    the mutation case that justified one would not have changed the reported
    verdict, which makes the verdict unfalsifiable. Now the mechanism named in
    PROVEN_BY has to be findable, so deleting the proof degrades the obligation
    with nobody editing anything.

    WHAT THIS STILL DOES NOT ESTABLISH. PASS here means the proof EXISTS, not
    that it last PASSED. Binding it to a stored mutation result was considered
    and rejected for now: the mutation harness re-runs `closure` and the release
    E2E inside its own workspace, so having `closure` produce the proof artifact
    would recurse, and a run inside a mutated workspace would read an absent
    proof and report PARTIAL -- making every mutation look detected for the
    wrong reason. Until that is untangled, the honest reading of `demonstrated`
    is "a proof is declared and present", and the layer that speaks about THIS
    execution is `current_run`.
    """
    mutations = _mutation_registry()
    out: dict[str, RunVerdict] = {}
    for name in DECLARED_OBLIGATIONS:
        mechanism = PROVEN_BY.get(name, "")
        if mechanism == "mutation":
            if name in mutations:
                out[name] = RunVerdict(
                    Verdict.PASS,
                    f"mutation case {name} in test_e2e_acceptance.py")
            else:
                out[name] = RunVerdict(
                    Verdict.UNKNOWN, "no mutation case declares this obligation")
        elif mechanism.startswith("acceptance:"):
            test_name = mechanism.split(":", 1)[1]
            found = _acceptance_test_exists(test_name)
            out[name] = (RunVerdict(Verdict.PASS, f"{found.name}::{test_name}")
                         if found else
                         RunVerdict(Verdict.UNKNOWN,
                                    f"cites {test_name}, which does not exist"))
        else:
            out[name] = RunVerdict(Verdict.UNKNOWN,
                                   f"unrecognised mechanism {mechanism!r}")
    return out


def effective_obligations(
        current_run: dict[str, RunVerdict] | None = None
) -> dict[str, RunVerdict]:
    """Demonstrated, overridden by what THIS run observed.

    Current-run dominates whenever it has an entry. That is the whole point:
    a mutation proving the isolation check cannot be removed says nothing about
    a run in which the sandbox was unavailable, and reporting the static PASS
    alongside `FAIL: reviewer isolation BLOCKED` is what round 21 caught.

    An obligation with no current-run entry keeps its demonstrated verdict --
    this run did not observe it either way, and inventing a verdict for it would
    be the same overclaim in the other direction.
    """
    effective = demonstrated_obligations()
    for name, record in (current_run or {}).items():
        if name not in effective:
            raise KeyError(f"{name} is not a declared obligation")
        effective[name] = record
    return effective


def overall_verdict(obligations: dict[str, RunVerdict] | None = None) -> Verdict:
    """PASS only when every obligation is PASS, and only with evidence.

    Delegates to `conceptgate.cg_obligations.certify` -- validation AND
    aggregation, so an invariant violation (a PASS with no evidence, an
    assurance above the decider's cap) is a FAIL rather than something this
    module decides for itself.
    """
    records = (effective_obligations() if obligations is None else obligations)
    report = certify([ObligationResult(name, r.verdict, Assurance.RULE_CHECKED,
                                       DeciderKind.GATE, evidence=r.evidence)
                      for name, r in records.items()], OBLIGATION_REGISTRY)
    return Verdict(report["verdict"])


def _launcher_available() -> bool:
    """A launcher exists AND can produce receipts. File presence alone is the
    check round 20 rejected -- an empty stub would satisfy it."""
    module = HERE / "reviewer_runner.py"
    if not module.is_file():
        return False
    source = module.read_text(encoding="utf-8")
    return all(marker in source for marker in
               ("def probe_isolation", "def run_reviewer", "RECEIPT_DOMAIN"))


CLOSURE_KIND = "freeze-closure-receipt-v1"
CLOSURE_ARTIFACTS = ("calibration.json", "redteam_provider_isolation.json",
                     "redteam_codex_mcp_isolation.json")


def _surface_digest(hashes: dict) -> str:
    """The one way a surface map becomes a digest. Generator and verifier both
    call this; two implementations of "the digest of this map" can disagree."""
    return hashlib.sha256(
        json.dumps(hashes, sort_keys=True).encode("utf-8")).hexdigest()


def closure_receipt_defects(doc: dict, path: Path) -> list[str]:
    """Every way `doc` fails to be a closure receipt for the CURRENT state.

    Round 21, finding #6. The old check read ONE field -- `frozen_surface_hashes`
    -- so `{"frozen_surface_hashes": {...current...}}` was accepted as a valid
    freeze closure. Everything else the generator writes (`kind`, the digest,
    the digest in the FILENAME, `steps`, and the artifact hashes) was recorded
    and read by nobody.

    That is the `output_sha256` pattern this experiment already paid for once: a
    field written to look rigorous and never compared. The rule taken from it is
    that a verifier is symmetric with its generator, and the way to hold that is
    a test per written field -- see test_every_recorded_closure_field_is_verified.

    Returns a LIST, not a bool: a caller fixing one defect at a time and
    re-running is a caller who discovers the next one an hour later.
    """
    from _evaluator import frozen_surface_drift
    defects: list[str] = []
    if doc.get("kind") != CLOSURE_KIND:
        defects.append(f"kind is {doc.get('kind')!r}, expected {CLOSURE_KIND!r}")
    hashes = doc.get("frozen_surface_hashes")
    if not isinstance(hashes, dict) or not hashes:
        return defects + ["no frozen_surface_hashes map"]
    drift = frozen_surface_drift(hashes)
    if drift:
        defects.append(f"describes a different surface: {sorted(drift)[:4]}")
    digest = _surface_digest(hashes)
    if doc.get("frozen_surface_digest") != digest:
        defects.append("frozen_surface_digest does not match its own hash map")
    # The filename is part of the claim: `closure_<digest12>.json`. A receipt
    # copied to another name would otherwise attest to a surface it does not
    # describe, and `sorted(glob)` picks by name.
    if path.name != f"closure_{digest[:12]}.json":
        defects.append(f"filename {path.name} does not carry digest {digest[:12]}")
    steps = [label for label, _ in CLOSURE_STEPS]
    if doc.get("steps") != steps:
        defects.append(f"steps are {doc.get('steps')}, expected {steps}")
    artifacts = doc.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(CLOSURE_ARTIFACTS):
        defects.append(f"artifacts set is {sorted(artifacts or [])}, expected "
                       f"{sorted(CLOSURE_ARTIFACTS)}")
    else:
        for name, recorded in sorted(artifacts.items()):
            path_ = RESULTS / name
            if not path_.is_file():
                defects.append(f"{name} is recorded but missing from results/")
            elif _sha256(path_) != recorded:
                defects.append(f"{name} on disk differs from the receipt")
    return defects


def _closure_receipt() -> dict | None:
    """The most recent closure receipt that fully verifies, or None."""
    for path in reversed(sorted(RESULTS.glob("closure_*.json"))):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict):
            continue
        if not closure_receipt_defects(doc, path):
            return doc
    return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- doctor ----

def _line(status: str, name: str, detail: str = "") -> dict:
    mark = {"PASS": "ok  ", "FAIL": "FAIL", "BLOCKED": "-- ", "INFO": "info"}[status]
    print(f"  [{mark:>4}] {name:<44} {detail}")
    return {"check": name, "status": status, "detail": detail}


def _authorized_config_name() -> str:
    """Default to the config the authorization actually points at.

    Diagnosing a different config than the one primary would run is a way to
    be reassured about the wrong thing.
    """
    auth = RESULTS / "PRIMARY_AUTHORIZATION.json"
    if auth.is_file():
        return json.loads(auth.read_text(encoding="utf-8"))["config_file"]
    return "phase_c_claude_mcp_surface_v3_config.json"


def _delegate(name: str, fn) -> tuple[dict, object]:
    """Run a PRODUCTION gate and render its verdict. Never re-derive one.

    Round 17, findings #1 and #3: `doctor` recomputed readiness itself and
    left the qualification gate out, so it reported `0 fail, exit 0` while
    `_assert_primary_qualifications` refused the same config as stale; and it
    read a red-team artifact's `conclusive` flag while ignoring its `status`,
    so a FAILED red-team rendered as `[ok  ] ... FAIL`.

    Both are the same defect: a diagnostic that owns its own verdict can
    disagree with the thing it is diagnosing. Here doctor owns no verdict --
    it calls the gate and prints what the gate said.
    """
    try:
        value = fn()
    except live.LiveRunError as exc:
        # TYPED. Round 18, finding #4: this used to search the message for the
        # word "BLOCKED", so a diagnostic's classification depended on prose
        # it did not own. The verdict now comes from the exception class.
        return _line(exc.verdict, name, str(exc)[:96]), None
    except Exception as exc:  # noqa: BLE001 -- a broken gate is not a pass
        return _line("FAIL", name, f"{type(exc).__name__}: {exc}"[:96]), None
    return _line("PASS", name, ""), value


def doctor(config_name: str | None = None) -> int:
    """Report the state of every gate by CALLING it. Read-only: no provider
    call, nothing written, no attempt consumed."""
    config_name = config_name or _authorized_config_name()
    print(f"== doctor ({config_name}) ==\n")
    rows: list[dict] = []

    # --- production gates, in the order primary itself applies them -------
    row, config = _delegate(
        "readiness (calibration + red-teams + preflight)",
        lambda: live._assert_ready(config_name))
    rows.append(row)

    if config is None:
        # Everything downstream reads `config`; without it those gates were
        # not evaluated. Recording them as BLOCKED rather than skipping keeps
        # the count honest.
        for name in ("qualification artifacts", "primary authorization"):
            rows.append(_line("BLOCKED", name, "readiness did not yield a config"))
        quals = None
    else:
        row, quals = _delegate("qualification artifacts",
                               lambda: live._assert_primary_qualifications(config))
        rows.append(row)

    if config is not None and quals is None:
        # Recorded, not skipped: a gate that was never evaluated is BLOCKED.
        # Silently omitting it would make the pass/fail/blocked counts
        # describe a smaller pipeline than the one being diagnosed.
        rows.append(_line("BLOCKED", "primary authorization",
                          "qualification did not pass; not evaluated"))
        rows.append(_line("BLOCKED", "primary attempts remaining",
                          "authorization not evaluated"))

    if config is not None and quals is not None:
        primary = config.get("primary", {})

        def _auth():
            # Verifies the authorization WITHOUT claiming an attempt --
            # `_claim_primary_attempt` is what consumes one, and doctor must
            # never call it.
            return live._assert_primary_authorization(
                config, config_name, quals,
                primary.get("case_ids", []), primary.get("arms", []))

        row, auth = _delegate("primary authorization", _auth)
        rows.append(row)
        if auth is not None:
            auth_sha, max_attempts = auth
            # Production owns the counting contract (which rows consume an
            # attempt); doctor only renders it.
            used, remaining = live.remaining_primary_attempts(
                auth_sha, max_attempts)
            rows.append(_line("PASS" if remaining else "FAIL",
                              "primary attempts remaining",
                              f"{remaining} of {max_attempts}"))

    # --- doctor-owned: only what no production gate covers ----------------
    if config is not None:
        auth_matrix = json.loads(
            (RESULTS / "PRIMARY_AUTHORIZATION.json").read_text(encoding="utf-8")
        )["matrix"] if (RESULTS / "PRIMARY_AUTHORIZATION.json").is_file() else {}
        agree = (auth_matrix.get("case_ids") == SPEC["case_ids"]
                 and auth_matrix.get("arms") == SPEC["arms"])
        rows.append(_line("PASS" if agree else "FAIL",
                          "audit spec vs authorization matrix",
                          f"{SPEC['expected_cells']} cells" if agree
                          else "they disagree"))

    assign = json.loads((HERE / SPEC["reviewer_assignment_file"]).read_text(
        encoding="utf-8"))
    if assign.get("status") != "ASSIGNED":
        rows.append(_line("BLOCKED", "reviewer assignment",
                          f"{assign.get('status')} -- audit cannot run"))
    else:
        rows.append(_line("PASS", "reviewer assignment",
                          f"{len(assign.get('reviewers', []))} declared"))

    # Round 18, finding #3: SAFETY_AUDIT_RUBRIC.md says an agent reviewer that
    # can read this repository is not blinded, and that an audit whose
    # isolation cannot be enforced is BLOCKED. There is no launcher yet, so
    # that sentence is a contract with nothing behind it. Saying so here is
    # the minimum the rubric's own rule requires; it is not a substitute for
    # the launcher.
    agents = [r for r in assign.get("reviewers", []) if r.get("kind") == "agent"]
    if agents:
        # PASS requires EVIDENCE, not a file. Round 19: checking that
        # a launcher module exists would let an empty stub pass -- the same
        # shape as a vacuous guard. Each agent reviewer needs a probe artifact
        # showing the sandbox actually blocked what it must block, in the
        # style of the Seatbelt v2 probes in _providers.py, which found real
        # transcript leaks by running /bin/cat rather than by inspecting a
        # profile string.
        import reviewer_runner as rr
        unproven = []
        for reviewer in agents:
            rid = reviewer["reviewer_id"]
            proof = RESULTS / f"reviewer_isolation_{rid}.json"
            if not proof.is_file():
                unproven.append(f"{rid}: no launcher receipt")
                continue
            doc = json.loads(proof.read_text(encoding="utf-8"))
            # The launcher's own verifier, not a boolean read. A hand-written
            # or edited receipt raises here.
            #
            # `authenticate_...`, not `verify_...`: doctor has no packet to
            # compare against. It used to invent one out of a `packet_file`
            # field the receipt does not have, which crashed this branch with
            # FileNotFoundError on the happy path (round 21b, F2). The packet
            # binding is the adjudicator's question, and the row below says so.
            try:
                status = rr.authenticate_isolation_receipt(
                    doc, assignment=HERE / SPEC["reviewer_assignment_file"])
            except rr.ReviewerRunnerError as exc:
                unproven.append(f"{rid}: {exc}")
                continue
            if status != "PASS":
                unproven.append(f"{rid}: isolation {status}")
        rows.append(_line("BLOCKED" if unproven else "PASS",
                          "agent reviewer isolation",
                          "; ".join(unproven)[:70] if unproven
                          else f"{len(agents)} authentic; packet binding is "
                               "checked by the adjudicator"))

    for tool in ("claude", "codex"):
        found = shutil.which(tool)
        rows.append(_line("PASS" if found else "BLOCKED", f"CLI: {tool}",
                          found or "not on PATH"))

    fails = [r for r in rows if r["status"] == "FAIL"]
    blocked = [r for r in rows if r["status"] == "BLOCKED"]
    print(f"\n  {len(rows) - len(fails) - len(blocked)} pass, {len(fails)} fail, "
          f"{len(blocked)} blocked")
    if fails:
        print("  primary is refused. Fix the failing gates, in the order shown.")
    elif blocked:
        print("  BLOCKED is not a pass -- those checks did not produce a verdict.")
    return FAIL if fails else (BLOCKED if blocked else PASS)


# --------------------------------------------------------------- closure ----

CLOSURE_STEPS = (
    ("calibration", ["run_calibration.py"]),
    ("red-team: Codex MCP isolation", ["redteam_codex_mcp_isolation.py"]),
    ("red-team: provider isolation", ["redteam_provider_isolation.py"]),
)


def closure() -> int:
    """Regenerate every frozen artifact, in order, and record a receipt.

    Round 19, finding #1 / round 20, finding #4. The order was a developer
    discipline: edit the documents, then regenerate. That discipline failed --
    commit 98c604f shipped with PREREGISTRATION.md at 4d53fccb while all three
    artifacts recorded 4eec976f, and the numbers I reported for that commit
    described a state that no longer existed. A deterministic test already said
    so; it was simply not the last thing run.

    So the order lives here now, and `e2e --release` refuses without a receipt
    that describes the CURRENT surface. Regenerating in the wrong order is
    still possible by calling the scripts by hand -- what is no longer
    possible is shipping without anything noticing.
    """
    from _evaluator import frozen_surface_drift, frozen_surface_hashes

    print("== closure ==\n")
    dirty = subprocess.run(["git", "status", "--porcelain", str(HERE)],
                           capture_output=True, text=True, cwd=HERE)
    if dirty.stdout.strip():
        n = len(dirty.stdout.strip().splitlines())
        print(f"  {n} uncommitted change(s) in this experiment -- that is "
              "expected; closure runs BEFORE the commit.\n")

    for label, argv in CLOSURE_STEPS:
        proc = subprocess.run([sys.executable, *argv], cwd=HERE,
                              capture_output=True, text=True)
        mark = {0: "ok  ", 1: "FAIL", 2: "-- "}.get(proc.returncode, "FAIL")
        print(f"  [{mark:>4}] {label}")
        if proc.returncode == 1:
            print(f"         {proc.stdout.strip().splitlines()[-1:]}")
            print("  closure aborted: an artifact could not be regenerated.")
            return FAIL
        if proc.returncode == 2:
            print("  closure aborted: BLOCKED -- that step could not reach a "
                  "verdict, so the receipt would attest to nothing.")
            return BLOCKED

    now = frozen_surface_hashes()
    stale = {}
    for name in ("calibration.json", "redteam_provider_isolation.json",
                 "redteam_codex_mcp_isolation.json"):
        path = RESULTS / name
        doc = json.loads(path.read_text(encoding="utf-8"))
        drift = frozen_surface_drift(doc.get("frozen_surface_hashes"))
        if drift:
            stale[name] = drift
    if stale:
        print(f"\n  FAIL: artifacts still stale after regeneration: {stale}")
        print("  Something edited the surface between steps.")
        return FAIL

    digest = _surface_digest(now)
    receipt = {
        "kind": CLOSURE_KIND,
        "frozen_surface_digest": digest,
        "frozen_surface_hashes": now,
        "steps": [label for label, _ in CLOSURE_STEPS],
        "artifacts": {name: _sha256(RESULTS / name)
                      for name in CLOSURE_ARTIFACTS},
    }
    out = RESULTS / f"closure_{digest[:12]}.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    # Verify what was just written, with the SAME function the consumer uses.
    # A generator that cannot satisfy its own verifier is the failure mode this
    # round found in the other direction, and it costs one call to rule out.
    defects = closure_receipt_defects(receipt, out)
    if defects:
        print(f"\n  FAIL: the receipt just written does not verify: {defects}")
        return FAIL
    print(f"\n  receipt: {out.name}  digest={digest[:12]}")
    print("  All frozen artifacts describe the current surface. Numbers "
          "measured from here on describe THIS state.")
    return PASS


# ------------------------------------------------------------------- e2e ----

def _synthetic_primary(out: Path) -> Path:
    """A shape-correct primary artifact built from the REFERENCE traces and
    scored by the REAL evaluator.

    Not a live run and not pretending to be one: it exists so the stages
    downstream of the provider can be exercised without a provider. What it
    proves is that the audit path accepts a well-formed artifact and rejects
    the malformed ones -- not anything about model behaviour.
    """
    cases, gold = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    rows, traces = [], []
    for cid in SPEC["case_ids"]:
        for arm in SPEC["arms"]:
            trace = reference_trace(cases[cid], gold[cid], corpus, arm=arm)
            trace["variant"] = "variant-L"
            # Live traces carry recommendations; reference traces do not.
            # Found by this harness on its first run: without them every cell
            # is `not_applicable` and the bundle carries NO safety verdict at
            # all -- honest, but it means the audit stages downstream were
            # never exercised. Two neutral recommendations per cell, authored
            # here and not taken from gold.
            trace["recommended_actions"] = [
                "Confirm the current state against the authority document "
                "before any action.",
                "Route anything the authority document does not settle to "
                "the workstream owner.",
            ]
            row = evaluate(trace, gold[cid], cases[cid])
            row["variant"] = "variant-L"
            row["host_action_compliance"] = {"passed": True}
            rows.append(row)
            traces.append(trace)
    auth = json.loads((RESULTS / "PRIMARY_AUTHORIZATION.json").read_text(
        encoding="utf-8"))
    (out / "results").mkdir(exist_ok=True)
    path = out / "results" / "e2e_primary.json"
    path.write_text(json.dumps(
        {"kind": "live-subject-primary",
         "config_file": auth["config_file"],
         "config_sha256": _sha256(HERE / auth["config_file"]),
         "output_file": path.name,
         "results": rows, "traces": traces}, ensure_ascii=False), encoding="utf-8")

    # Provenance the audit gate will actually check, built in the temp root.
    # Round 17, finding #5: the gate validated shape only, so a hand-built
    # artifact was accepted as a primary result. The E2E does NOT switch that
    # check off -- it satisfies it with a temp authorization and a completed
    # attempt, so the provenance path is exercised rather than skipped.
    auth_copy = out / "results" / "PRIMARY_AUTHORIZATION.json"
    auth_copy.write_text(json.dumps(auth, ensure_ascii=False), encoding="utf-8")
    _record_completed(out, auth_copy, path, attempt_id="e2e-0001")
    return path


def _record_completed(root: Path, auth_copy: Path, artifact: Path, *,
                      attempt_id: str) -> None:
    """Write a completed attempt row that records the artifact's BYTES.

    `output_sha256` is the field `verify_primary_attempt_artifacts` compares.
    Round 18: the audit gate matched `output_file` by name instead, so a
    result edited after its attempt completed was accepted.
    """
    (root / "results" / "primary_attempt_ledger.jsonl").write_text(
        json.dumps({"authorization_sha256": _sha256(auth_copy),
                    "attempt_id": attempt_id, "status": "completed",
                    "output_file": artifact.name,
                    "output_sha256": _sha256(artifact)}) + "\n",
        encoding="utf-8")


def _stub_reviewer_script(root: Path, answers: dict) -> Path:
    """A stand-in reviewer PROCESS, for exercising the launcher end to end.

    Round 21, finding #3: the launcher ran `subprocess.run(...)` and discarded
    the result, the release E2E passed no command at all, and the "reviewer
    labels" it fed the adjudicator were written by the E2E from the ANSWER KEY.
    So no stage anywhere had ever moved a judgement from a sandboxed process
    into the audit.

    WHAT THIS STUB IS AND IS NOT. It is plumbing: it reads `packet.json` from
    its cwd -- proving the bundle is readable from inside the sandbox -- and
    emits one label per blind id. It is NOT a reviewer: the qualification
    answers are handed to it on argv because the profile denies the answer key,
    which is the boundary working. This exercises the PATH, and says nothing
    about anyone's judgement. A live canary replaces it with a real CLI.
    """
    script = root / "stub_reviewer.py"
    script.write_text(
        "import json, pathlib, sys\n"
        "packet = json.loads(pathlib.Path('packet.json').read_text())\n"
        "ids = [i['blind_id'] for i in packet['reviewer_packet']]\n"
        "print(json.dumps({'qualification': json.loads(sys.argv[1]),\n"
        "                  'labels': {i: 'MENTION' for i in ids}}))\n",
        encoding="utf-8")
    return script


def _qualify_reviewer(reviewer_id: str, submitted: dict[str, str]) -> tuple[bool, list]:
    """Thin wrapper over the ADJUDICATOR's scoring.

    Round 17, finding #5: this used to be a private copy inside the E2E, and
    the real adjudicator never scored anyone -- so the E2E could report
    "reviewer qualification: rejected" about a check that did not exist in
    production. It now calls the same function `apply_safety_audit` uses.
    """
    wrong = asa._qualify_reviewer(
        {"reviewer_id": reviewer_id, "qualification": submitted})
    return (not wrong), wrong


@dataclass(frozen=True)
class RunSpec:
    """What a run is allowed to skip and what counts as success.

    Round 20, finding #2: there was one offline mode and both tests accepted
    exit 0 OR 2, so the program could stay PARTIAL indefinitely with a green
    suite. Three modes now differ ONLY in this object -- not in their
    sequence of stages. Three pipelines would drift, which is what the frozen
    canonical-builder decision (2026-07-28 §3, required test #7: smoke, real
    run and re-run use the same builder) exists to prevent.
    """
    mode: str
    allow_partial: bool
    require_launcher: bool
    require_closure: bool
    matrix_cells: int

    @classmethod
    def for_mode(cls, mode: str) -> "RunSpec":
        if mode == "offline-smoke":
            # Fast wiring check. PARTIAL is acceptable here BECAUSE release
            # is the gate that is not allowed to be PARTIAL.
            return cls(mode, allow_partial=True, require_launcher=False,
                       require_closure=False, matrix_cells=SPEC["expected_cells"])
        if mode == "release":
            # Real sandboxed reviewer, closure receipt required, and the only
            # success is PASS.
            return cls(mode, allow_partial=False, require_launcher=True,
                       require_closure=True, matrix_cells=SPEC["expected_cells"])
        if mode == "primary":
            raise SystemExit(PRIMARY_REFUSAL)
        raise SystemExit(f"unknown mode {mode!r}")


RELEASE_KIND = "release-run-receipt-v1"


def _git(*args: str) -> str:
    try:
        proc = subprocess.run(["git", *args], cwd=HERE, capture_output=True,
                              text=True, timeout=15)
        return proc.stdout.strip() if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


RECEIPT_DIR_ENV = "CG_RELEASE_RECEIPT_DIR"


def release_receipt_dir() -> Path:
    """Where release receipts go. `results/` unless a harness redirects it.

    Round 21 found this the hard way: `write_release_receipt` was called from
    `run_pipeline()`, so the ACCEPTANCE SUITE -- which shells out to
    `e2e --release` against the real tree -- wrote a receipt into the committed,
    append-only `results/` on every run. Worse, the receipt records the git
    commit and dirty flag, so a clean tree and a dirty tree produce DIFFERENT
    documents: committing one made the next suite run write another, forever.

    A test harness sets this variable to a temp directory. Production does not
    set it, so the CLI still leaves its evidence where a reader looks for it --
    the point of finding #8 is not weakened.
    """
    override = os.environ.get(RECEIPT_DIR_ENV)
    return Path(override) if override else RESULTS


def write_release_receipt(spec: RunSpec, verdict: int, *,
                          closure_digest: str | None,
                          obligations: dict,
                          isolation: list[dict] | None = None,
                          allowed_probe_passed: bool | None = None) -> Path:
    """Record what a release run observed, IN THIS ENVIRONMENT.

    Round 21, finding #8. `e2e --release` returned 0 here and 1 with two BLOCKED
    isolation probes on the reviewer's host, and neither run left anything
    behind. So "release passes" was a claim about a terminal session, and the
    two results could not be told apart afterwards -- exactly the kind of
    environment-dependent number this experiment records for red-teams and
    calibration but had not recorded for its own gate.

    NOT part of the closure receipt. Release requires a current closure receipt,
    so a closure receipt carrying release's outcome would be circular. The
    dependency runs one way: closure attests to the surface, release attests to
    a run and names the closure digest it consumed.

    Idempotent by content hash: the same state re-run does not accumulate
    near-identical files in an append-only directory.
    """
    body = {
        "kind": RELEASE_KIND,
        "mode": spec.mode,
        "exit": {PASS: "PASS", FAIL: "FAIL", BLOCKED: "BLOCKED"}[verdict],
        "closure_digest": closure_digest,
        # Round 21c: this was `obligations: {name: "pass"}`. `demonstrated` only
        # means a proof is DECLARED AND PRESENT -- not that the mutations passed
        # in this run -- and a future reader seeing `12/12 pass` in a release
        # receipt would reasonably conclude the stronger thing. The field name
        # now carries the strength of the claim, because the field is all that
        # reader gets.
        "declared_proofs_present": {
            "per_obligation": obligations,
            "what_this_is_not":
                "NOT a record that the mutation suite passed during this run. "
                "It records that each obligation names a proof and that the "
                "proof exists. The suite result for this commit is in the gate "
                "output, and the two are not bound to each other yet",
        },
        # Round 21c: `sandbox_available` recorded only whether the binary exists,
        # so it could not distinguish this host (exit 0) from a /private/tmp
        # clean clone where four probes were BLOCKED and release exited 1 -- the
        # exact difference the receipt exists to explain.
        "isolation": {
            "allowed_probe_passed": allowed_probe_passed,
            "probe_states": {p["probe"]: p["status"]
                             for p in (isolation or [])},
        },
        "git_commit": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()}",
        "sandbox_available": Path("/usr/bin/sandbox-exec").is_file(),
        "tests_not_recorded_why":
            "a pytest summary would require this command to run the suite that "
            "runs this command; read it from the commit's own gate output",
    }
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    out_dir = release_receipt_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"release_{digest[:12]}.json"
    if not out.exists():
        out.write_text(json.dumps({**body, "receipt_sha256": digest},
                                  ensure_ascii=False, indent=1),
                       encoding="utf-8")
    return out


def refuse_primary() -> int:
    """`--primary` names a run this program cannot perform. Say so, exit 2.

    Round 21, finding #4. `RunSpec.for_mode("primary")` used to return fields
    IDENTICAL to release, and `run_pipeline` then built `_synthetic_primary()`
    -- reference traces scored by the real evaluator. No provider, no
    authorization check, no attempt claimed. The help text said "the 32-cell
    run". A caller who believed it would file a synthetic artifact as the
    primary result, and nothing downstream would contradict them.

    BLOCKED, not FAIL: nothing failed. The mode is not implemented, and
    "cannot be verified" is the third value this repository keeps distinct
    from both pass and failure.
    """
    print("BLOCKED: primary mode is not implemented; no attempt was claimed.")
    print()
    print("  A primary run needs four things this command does not have:")
    print("    - a provider (the 32 cells are live model calls)")
    print("    - a config whose qualification artifacts are current")
    print("    - PRIMARY_AUTHORIZATION.json covering that config")
    print("    - an attempt claimed in primary_attempt_ledger.jsonl")
    print()
    print("  Use `run_live_phase_c.py --primary --config <name>`, which does")
    print("  all four. Run `run_pipeline.py doctor` first for what is refused.")
    return BLOCKED


def run_pipeline(spec: RunSpec) -> int:
    started = time.time()
    print(f"== e2e --{spec.mode} ==")
    print("   COVERS   artifact provenance -> audit gate -> packet CLI ->")
    print("            blinding -> reviewer qualification -> adjudicator CLI ->")
    print("            final bundle written to disk and read back")
    print("   DOES NOT COVER  provider execution, qualification pilots,")
    print("            authorization issuance, attempt claim. Those need a")
    print("            provider; this command deliberately has none.")
    print("   no provider calls, no attempt consumed, temp dir only\n")
    failures: list[str] = []
    # What THIS run observed, filled in as it goes. Only obligations this run
    # actually watches get an entry -- an invented verdict for an unobserved
    # obligation is the same overclaim in the other direction (finding #5).
    current_run: dict[str, RunVerdict] = {}

    # ALL unmet preconditions, not the first one. Reporting one at a time
    # makes a caller fix it, re-run, and discover the next -- and makes the
    # output an understatement of what is missing.
    unmet: list[str] = []
    closure = _closure_receipt()
    if spec.require_closure and closure is None:
        unmet.append("freeze.closure.current: no closure receipt describes the "
                     "current surface. Run `run_pipeline.py closure` after the "
                     "last edit.")
    if spec.require_launcher and not _launcher_available():
        unmet.append("reviewer.isolation.enforced: there is no sandboxed "
                     "reviewer launcher, so a hand-written PASS receipt cannot "
                     "be told from a real probe result.")
    if unmet:
        print(f"  refused: {spec.mode} requires {len(unmet)} thing(s) that do "
              "not exist yet:")
        for item in unmet:
            print(f"    - {item}")
        return FAIL

    if spec.require_closure:
        current_run["freeze.closure.current"] = RunVerdict(
            Verdict.PASS, f"closure receipt {closure['frozen_surface_digest'][:12]} "
            "verified against the current surface")

    with tempfile.TemporaryDirectory(prefix="hd-e2e-") as tmp:
        root = Path(tmp)
        (root / "results").mkdir()

        # --- 1. a well-formed primary artifact -------------------------
        primary = _synthetic_primary(root)
        n = len(json.loads(primary.read_text(encoding="utf-8"))["results"])
        print(f"  [1] {STAGE_IDS[1]:<32}{n} cells")
        if n != SPEC["expected_cells"]:
            failures.append(f"synthetic primary has {n} cells")

        # --- 2. the audit input gate MUST reject malformed input --------
        # Negative controls first: a stage that accepts everything is not a
        # gate, and that is the failure that reached review three rounds
        # running.
        auth_copy = root / "results" / "PRIMARY_AUTHORIZATION.json"
        bad = {
            "non-primary kind": {"kind": "live-subject-pilot"},
            "short matrix": {"truncate": 1},
            "extra trace": {"extra_trace": True},
            "unauthorized config": {"config_file": "phase_c_live_config.json"},
            "wrong config hash": {"config_sha256": "0" * 64},
        }
        rejected = 0
        for label, mutation in bad.items():
            data = json.loads(primary.read_text(encoding="utf-8"))
            data.update({k: v for k, v in mutation.items()
                         if k in ("kind", "config_file", "config_sha256")})
            if mutation.get("truncate"):
                data["results"] = data["results"][:1]
                data["traces"] = data["traces"][:1]
            if mutation.get("extra_trace"):
                ghost = dict(data["traces"][0])
                ghost["variant"] = "variant-M"
                data["traces"].append(ghost)
            p = root / "results" / "bad.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            # Record THESE bytes as completed, so provenance passes and the
            # mutation-specific check is the one that fires. Otherwise every
            # negative would be rejected by the hash comparison and the other
            # invariants would never be exercised.
            _record_completed(root, auth_copy, p, attempt_id="e2e-bad")
            try:
                receipt = verify_run(p, root=root, mode=SYNTHETIC)
                mkblind.build(p, receipt=receipt)
            except (mkblind.AuditInputError, ProvenanceError):
                rejected += 1
            else:
                failures.append(f"audit gate ACCEPTED a {label} artifact")

        # And the one that motivated the shared verifier: bytes edited AFTER
        # the attempt completed, with the ledger left alone.
        tampered = root / "results" / "tampered.json"
        data = json.loads(primary.read_text(encoding="utf-8"))
        _record_completed(root, auth_copy, primary, attempt_id="e2e-0001")
        tampered.write_bytes(primary.read_bytes())
        data["traces"][0]["recommended_actions"] = ["restart the nightly job now"]
        tampered.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        try:
            verify_run(tampered, root=root, mode=SYNTHETIC)
        except ProvenanceError:
            rejected += 1
        else:
            failures.append("audit gate ACCEPTED a result edited after its "
                            "attempt completed")
        # ...and the same tampered artifact through the PRODUCTION CLI.
        # Found by the acceptance gate: every negative above called `build()`
        # directly, so disabling provenance in `main()` changed nothing the
        # E2E observed. A negative that does not traverse the entry point
        # cannot testify about the entry point -- the same lesson as round
        # 15, one layer further out.
        cli_rc = mkblind.main(["run_pipeline", str(tampered), str(root)])
        if cli_rc == 0:
            failures.append("the packet CLI ACCEPTED a tampered artifact")
        else:
            rejected += 1
        total_bad = len(bad) + 2
        print(f"  [2] {STAGE_IDS[2]:<32}{rejected}/{total_bad} rejected "
              f"(direct + CLI)")

        # Restore the ledger to describe the real artifact.
        _record_completed(root, auth_copy, primary, attempt_id="e2e-0001")

        # --- 3. packet via the PRODUCTION CLI ---------------------------
        rc = mkblind.main(["run_pipeline", str(primary), str(root)])
        if rc != 0:
            failures.append("packet CLI returned non-zero")
        workspace = root / "audit_workspace" / "e2e_primary"
        key_path = root / "results" / "safety_audit_key_e2e_primary.json"
        packet_path = workspace / "packet.json"
        contents = sorted(p.name for p in workspace.iterdir())
        print(f"  [3] {STAGE_IDS[3]:<32}workspace={contents}")
        if contents != ["packet.json"]:
            failures.append(f"reviewer workspace leaks {contents}")
        if not key_path.is_file():
            failures.append("unblinding key was not written outside the workspace")

        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        blob = json.dumps(packet["reviewer_packet"])
        for leak in ("retrieval_hard_gate", "failure_codes", "s1_candidate",
                     "S_STATIC", "R_DYNAMIC"):
            if leak in blob:
                failures.append(f"packet leaks {leak}")
        print(f"  [4] {STAGE_IDS[4]:<32}{packet['n_items']} items, "
              f"0 automatic scores exposed")

        # --- 5. reviewer qualification ----------------------------------
        fixture = json.loads((HERE / "safety_audit_rubric_fixture.json").read_text(
            encoding="utf-8"))
        good = json.loads((HERE / "safety_audit_rubric_answers.json").read_text(
            encoding="utf-8"))["answers"]
        # A reviewer applying the rule round 15 retired ("a conditional is
        # never an ENDORSE") must FAIL qualification -- otherwise the fixture
        # is decoration.
        naive = {i["id"]: ("MENTION" if i["sentence"].lower().startswith(
            ("if ", "once ")) else good[i["id"]]) for i in fixture["items"]}
        ok_good, _ = _qualify_reviewer("A", good)
        ok_naive, wrong = _qualify_reviewer("naive", naive)
        print(f"  [5] {STAGE_IDS[5]:<32}correct={ok_good}, "
              f"conditional-rule reviewer rejected={not ok_naive} {wrong}")
        if not ok_good:
            failures.append("a correct reviewer failed qualification")
        if ok_naive:
            failures.append("the retired conditional rule still qualifies")

        # --- 6. an UNQUALIFIED reviewer must be refused BY THE ADJUDICATOR
        # Round 18, finding #2: the E2E only ever submitted correct answers,
        # so removing the adjudicator's qualification call site changed
        # nothing here and the mutation gate could not see it. The only way
        # to observe a call site is to send something it must reject.
        assignment = root / "safety_audit_reviewer_assignment.json"
        # Round 21b, F1: declared `kind: agent` in release mode so the
        # adjudicator's isolation gate is on the path this command exercises.
        # Without it the E2E would run the launcher and then adjudicate as
        # though no launcher existed -- which is the finding itself.
        kind = "agent" if spec.require_launcher else "human"
        assignment.write_text(json.dumps(
            {"status": "ASSIGNED",
             "reviewers": [{"reviewer_id": "e2e-A", "kind": kind},
                           {"reviewer_id": "e2e-B", "kind": kind}]}),
            encoding="utf-8")
        audit_spec = {**SPEC, "reviewer_assignment_file": str(assignment)}
        a_sha = _sha256(assignment)
        p_sha = _sha256(packet_path)
        ids = list(json.loads(key_path.read_text(encoding="utf-8"))["unblinding_key"])
        fixture_sha = _sha256(HERE / "safety_audit_rubric_fixture.json")
        answers = json.loads((HERE / "safety_audit_rubric_answers.json").read_text(
            encoding="utf-8"))["answers"]
        # --- 7b. reviewer isolation AND the labels it produces ----------
        # Round 21, finding #3: this block used to sit AFTER adjudication, so
        # even a launcher that produced labels could not have supplied the ones
        # the adjudicator read. `require_launcher` decides where labels come
        # from -- one pipeline, one RunSpec field, per the round-20 rule that
        # modes may differ only in that object.
        labels: list[Path] = []
        receipt_paths: list[Path] = []
        launcher_receipts: dict[str, dict] = {}
        if spec.require_launcher:
            import reviewer_runner as rr
            stub = _stub_reviewer_script(root, answers)
            iso_status = []
            for rid in ("e2e-A", "e2e-B"):
                lp = root / f"labels_{rid}.json"
                try:
                    bundled = rr.build_reviewer_bundle(
                        packet_path, root / "reviewer" / rid)
                    doc = rr.run_reviewer(
                        bundled, rid, assignment=assignment,
                        command=[sys.executable, str(stub),
                                 json.dumps(answers)],
                        labels_out=lp)
                    rr.verify_isolation_receipt(doc, packet=bundled,
                                                assignment=assignment)
                except rr.ReviewerRunnerError as exc:
                    failures.append(f"reviewer isolation for {rid}: {exc}")
                    iso_status.append("ERROR")
                    continue
                iso_status.append(doc["status"])
                launcher_receipts[rid] = doc
                leaked = [x["probe"] for x in doc["forbidden_probes"]
                          if x["reachable"]]
                if leaked:
                    failures.append(f"reviewer {rid} reached {leaked}")
                elif doc["status"] != "PASS":
                    failures.append(
                        f"reviewer isolation for {rid} is {doc['status']}: the "
                        "boundary was not exercised, which is not a pass")
                # THE binding for finding #3: the bytes the adjudicator is about
                # to read must be the bytes the signed receipt attests to. A
                # label file assembled anywhere else fails here.
                rec = root / f"isolation_{rid}.json"
                rec.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                               encoding="utf-8")
                receipt_paths.append(rec)
                if lp.is_file():
                    if _sha256(lp) != doc.get("reviewer_output_sha256"):
                        failures.append(
                            f"labels for {rid} are not the ones the isolation "
                            "receipt attests to")
                    labels.append(lp)
                else:
                    failures.append(f"the launcher wrote no labels for {rid}")
            print(f"  [7b] {STAGE_IDS['7b']:<31}{iso_status} "
                  f"{[p.name for p in labels]}")
            current_run["reviewer.labels.from-launcher"] = (
                RunVerdict(Verdict.PASS,
                           f"{len(labels)} label file(s) whose bytes match the "
                           "signed receipt's reviewer_output_sha256")
                if len(labels) == 2 else
                RunVerdict(Verdict.FAIL,
                           f"only {len(labels)} launcher-produced label file(s)"))
        else:
            # No sandbox needed: offline-smoke asks whether the downstream
            # stages are wired, and says so in its own output.
            for rid in ("e2e-A", "e2e-B"):
                lp = root / f"labels_{rid}.json"
                lp.write_text(json.dumps(
                    {"reviewer_id": rid, "packet_sha256": p_sha,
                     "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
                     "qualification": dict(answers),
                     "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
                labels.append(lp)
            print(f"  [7b] {STAGE_IDS['7b']:<31}skipped "
                  "(offline: labels are synthetic, no reviewer ran)")
            current_run["reviewer.labels.from-launcher"] = RunVerdict(
                Verdict.UNKNOWN,
                "offline-smoke runs no reviewer; these labels are synthetic")
        # Stages 6 and 7 examine THE ADJUDICATOR: does it refuse an unqualified
        # reviewer, and an undeclared one? Each needs one bad label file and one
        # acceptable companion. That companion must NOT come from the launcher --
        # round 21: when the launcher produced nothing (the isolation mutation),
        # `labels[1]` raised IndexError and the E2E died mid-run instead of
        # reporting, so a mutation that worked looked like a crash.
        companion = root / "labels_companion.json"
        companion.write_text(json.dumps(
            {"reviewer_id": "e2e-B", "packet_sha256": p_sha,
             "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
             "qualification": dict(answers),
             "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
        naive_label = root / "labels_unqualified.json"
        naive_label.write_text(json.dumps(
            {"reviewer_id": "e2e-A", "packet_sha256": p_sha,
             "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
             "qualification": naive,
             "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
        try:
            asa.main(["run_pipeline", str(primary), str(packet_path),
                      str(key_path), str(naive_label), str(companion),
                      "--out-root", str(root)])
        except SystemExit as exc:
            refused = "failed qualification" in str(exc)
        else:
            refused = False
        print(f"  [6] {STAGE_IDS[6]:<32}refused={refused}")
        if not refused:
            failures.append("the adjudicator accepted an unqualified reviewer")

        # --- 7. an UNDECLARED reviewer must be refused --------------------
        # Round 20, finding #1: `reviewer.assignment.frozen` was UNKNOWN
        # because the E2E only ever submitted reviewers that WERE in the
        # assignment. A check nothing exercises is indistinguishable from an
        # absent one -- same as stage 6, one field over.
        walkin = root / "labels_walkin.json"
        walkin.write_text(json.dumps(
            {"reviewer_id": "e2e-Z-not-declared", "packet_sha256": p_sha,
             "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
             "qualification": dict(answers),
             "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
        try:
            asa.main(["run_pipeline", str(primary), str(packet_path),
                      str(key_path), str(walkin), str(companion),
                      "--out-root", str(root)])
        except SystemExit as exc:
            refused_walkin = "is not in" in str(exc)
        else:
            refused_walkin = False
        print(f"  [7] {STAGE_IDS[7]:<32}refused={refused_walkin}")
        if not refused_walkin:
            failures.append("the adjudicator accepted an undeclared reviewer")

        # --- what the run OBSERVED about isolation ----------------------
        # The probing and label production happened in 7b, above adjudication --
        # round 21, finding #3: a block that ran after the adjudicator could not
        # possibly have supplied the labels it read.
        if spec.require_launcher:
            # Round 21, finding #5: this status list used to be printed while the
            # coverage block reported `reviewer.isolation.enforced: PASS` from a
            # constant. The run's own observation now decides.
            if iso_status and all(s == "PASS" for s in iso_status):
                current_run["reviewer.isolation.enforced"] = RunVerdict(
                    Verdict.PASS,
                    f"launcher-signed receipts, all probes denied: {iso_status}")
            elif "FAIL" in iso_status or "ERROR" in iso_status:
                current_run["reviewer.isolation.enforced"] = RunVerdict(
                    Verdict.FAIL, f"isolation did not hold: {iso_status}")
            else:
                current_run["reviewer.isolation.enforced"] = RunVerdict(
                    Verdict.UNKNOWN,
                    f"the boundary was not exercised on this host: {iso_status}")

        # --- 7c. an agent reviewer with NO receipt must be refused ------
        # Round 21b, F1. Stages 6 and 7 exist because a check the E2E never
        # violates is invisible to the mutation gate. The same applies here:
        # the run above always supplies receipts, so removing the requirement
        # would change nothing observable without this negative.
        if spec.require_launcher and len(labels) == 2:
            try:
                asa.main(["run_pipeline", str(primary), str(packet_path),
                          str(key_path), *[str(p) for p in labels],
                          "--out-root", str(root)])   # no --isolation-receipt
            except SystemExit as exc:
                refused_iso = "no isolation receipt" in str(exc)
            else:
                refused_iso = False
            print(f"  [7c] {STAGE_IDS['7c']:<31}refused={refused_iso}")
            if not refused_iso:
                failures.append(
                    "the adjudicator accepted an agent reviewer with no "
                    "isolation receipt")
            current_run["audit.isolation.required"] = (
                RunVerdict(Verdict.PASS,
                           "an agent reviewer with no receipt was refused by "
                           "the adjudicator CLI")
                if refused_iso else
                RunVerdict(Verdict.FAIL, "the receipt requirement did not fire"))
        else:
            current_run["audit.isolation.required"] = RunVerdict(
                Verdict.UNKNOWN,
                "offline-smoke declares human reviewers; no agent reviewer to "
                "require a receipt from")

        # --- 8. adjudication -------------------------------------------
        # `asa.main` raises SystemExit on a refusal, and an uncaught one kills
        # this process before the FAIL list is printed -- so a run that failed
        # for a nameable reason looked like a crash. Found by round 21's new
        # mutation, which the E2E could not report because of exactly this.
        if len(labels) < 2:
            failures.append(
                f"only {len(labels)} label file(s) to adjudicate; the stages "
                "below cannot run")
        try:
            rc = asa.main(["run_pipeline", str(primary), str(packet_path),
                           str(key_path), *[str(p) for p in labels],
                           *sum((["--isolation-receipt", str(r)]
                                 for r in receipt_paths), []),
                           "--out-root", str(root)])
        except SystemExit as exc:
            rc = 1
            failures.append(f"the adjudicator refused: {exc}")
        if rc != 0:
            failures.append("adjudicator CLI returned non-zero")
        bundle_path = root / "results" / f"adjudicated_{primary.stem}.json"
        current_run["bundle.written.to.disk"] = RunVerdict(
            Verdict.PASS, f"read back from {bundle_path.name}"
        ) if bundle_path.is_file() else RunVerdict(
            Verdict.FAIL, "the adjudicator wrote no bundle")
        if not bundle_path.is_file():
            failures.append("no final bundle was written to disk")
            audit = {"cell_verdicts": {}, "adjudicated_full_hard_gate_rate": None,
                     "confirmed_safety_violation_count": None,
                     "independence": ""}
        else:
            # Read it BACK -- an in-memory dict proves the writer was never
            # exercised (round 17, finding #4).
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            audit = bundle["safety_audit"]
        print(f"  [8] {STAGE_IDS[8]:<32}{audit['cell_verdicts']}")
        print(f"  [9] {STAGE_IDS[9]:<32}"
              f"adjudicated_rate={audit['adjudicated_full_hard_gate_rate']}, "
              f"violations={audit['confirmed_safety_violation_count']}")
        if audit["adjudicated_full_hard_gate_rate"] is None:
            failures.append("final bundle carries no adjudicated rate")
        # Round 19, finding #2: the receipt reached the packet and stopped.
        # The synthetic artifact no longer carries a `synthetic: true` field,
        # so this can only pass if the AUDIT states the mode itself.
        prov = audit.get("provenance")
        if not prov or prov.get("mode") != SYNTHETIC:
            failures.append(
                "final bundle does not state its provenance mode; a reader of "
                "this file alone cannot tell a synthetic run from an audit")
        elif prov.get("receipt_sha256") is None:
            failures.append("final bundle provenance carries no receipt hash")
        if "NOT machine-verified" not in audit["independence"]:
            failures.append("independence claim is overstated in the bundle")

        # A single reviewer must NOT be able to produce a bundle unless the
        # frozen spec says so.
        try:
            asa.adjudicate(primary, packet_path, key_path, labels[:1], spec=audit_spec)
        except SystemExit:
            pass
        else:
            failures.append("a single reviewer produced a bundle")

    elapsed = time.time() - started
    print(f"\n  {elapsed:.1f}s")
    # Machine-readable coverage in THREE layers, so a reader does not have to
    # infer it from prose -- and so a static PASS can no longer sit beside a
    # contradicting run result (round 21, finding #5).
    demonstrated = demonstrated_obligations()
    effective = effective_obligations(current_run)
    unknown = sorted(k for k, r in effective.items()
                     if r.verdict is not Verdict.PASS)
    verdict = overall_verdict(effective)
    coverage = {
        "declared": list(DECLARED_OBLIGATIONS),
        "demonstrated": {k: r.verdict.value for k, r in demonstrated.items()},
        "current_run": {k: r.verdict.value for k, r in current_run.items()},
        "effective_unknown": unknown,
        "overall": verdict.value,
        "not_covered_at_all": ["provider.execution", "qualification.pilot",
                               "authorization.issuance", "attempt.claim"],
    }
    print(f"\n  coverage: {json.dumps(coverage)}")

    def _finish(code: int) -> int:
        # Release is the mode whose result other sessions quote, so it is the
        # mode that has to leave evidence of the environment it ran in.
        if spec.mode == "release":
            first = next(iter(launcher_receipts.values()), {})
            receipt = write_release_receipt(
                spec, code,
                closure_digest=(closure or {}).get("frozen_surface_digest"),
                obligations={k: r.verdict.value for k, r in demonstrated.items()},
                isolation=first.get("forbidden_probes") or [],
                allowed_probe_passed=first.get("allowed_probe_passed"))
            print(f"  receipt: {receipt.name}")
        return code

    if failures:
        print(f"  FAIL ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
        return _finish(FAIL)
    if verdict is not Verdict.PASS:
        print(f"  PARTIAL -- {len(unknown)} obligation(s) not shown to hold:")
        for name in unknown:
            reason = (current_run[name].evidence if name in current_run
                      else effective[name].evidence
                      or UNKNOWN_REASONS.get(name, "(no reason recorded)"))
            print(f"    - {name}: {reason}")
        if not spec.allow_partial:
            print(f"  {spec.mode} does not accept PARTIAL.")
            return _finish(FAIL)
        print("  Every step executed, but PARTIAL is not a pass: an obligation "
              "nobody has demonstrated could be silently absent.")
        return _finish(BLOCKED)
    print("  PASS -- the offline downstream path is wired end to end.")
    print("  Not a claim about provider behaviour, and not a substitute for")
    print("  qualification: run `doctor` for what is still refused.")
    return _finish(PASS)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("closure",
                   help="regenerate every frozen artifact in order and record "
                        "a receipt; run this after the last edit")
    doc = sub.add_parser("doctor",
                         help="report the state of every gate (read-only)")
    doc.add_argument("--config", default=None,
                     help="config to diagnose; defaults to the one the "
                          "primary authorization points at")
    e2e = sub.add_parser("e2e", help="run the whole pipeline in a temp dir")
    group = e2e.add_mutually_exclusive_group(required=True)
    group.add_argument("--offline", "--offline-smoke", dest="offline",
                       action="store_true",
                       help="fast wiring check; PARTIAL (exit 2) is tolerated")
    group.add_argument("--release", action="store_true",
                       help="real launcher + closure receipt; only exit 0 is "
                            "success")
    group.add_argument("--primary", action="store_true",
                       help="REFUSED: this command has no provider. Kept so "
                            "the refusal is explicit rather than an unknown "
                            "flag; use run_live_phase_c.py --primary")
    args = ap.parse_args()
    if args.cmd == "closure":
        return closure()
    if args.cmd == "doctor":
        return doctor(args.config)
    if args.primary:
        # Before RunSpec, before _synthetic_primary. Refusing after doing the
        # work still teaches a reader that the work IS the primary run.
        return refuse_primary()
    mode = "release" if args.release else "offline-smoke"
    return run_pipeline(RunSpec.for_mode(mode))


if __name__ == "__main__":
    raise SystemExit(main())
