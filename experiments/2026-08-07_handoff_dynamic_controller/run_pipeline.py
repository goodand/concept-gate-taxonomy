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

from conceptgate.cg_obligations import Verdict, aggregate  # noqa: E402
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
}

# OBLIGATIONS -- the unit of completion.
#
# Round 20, finding #1: coverage was computed as a set difference over STAGES,
# so `reviewer.assignment.frozen` -- explicitly unverified -- was hidden
# because another obligation on the same stage was guarded. "3 unguarded
# stages" was true; "3 unguarded obligations" was not. A stage can carry
# several obligations, and a stage is covered only when all of them are.
#
# PASS here means "a mutation removing it makes the release E2E fail", proven
# by test_e2e_acceptance.py. UNKNOWN means nobody has shown that. Nothing is
# recorded as PASS on the strength of an assertion inside the E2E itself.
OBLIGATIONS: dict[str, Verdict] = {
    "audit.input-validated":           Verdict.PASS,
    "audit.provenance.bytes-compared": Verdict.PASS,
    "audit.provenance.propagated":     Verdict.PASS,
    "packet.blinding.applied":         Verdict.PASS,
    "reviewer.qualification.required": Verdict.PASS,
    "reviewer.assignment.frozen":      Verdict.PASS,
    "reviewer.count.enforced":         Verdict.PASS,
    "bundle.written.to.disk":          Verdict.PASS,
    "reviewer.isolation.enforced":     Verdict.PASS,
    "freeze.closure.current":          Verdict.PASS,
}

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
    "freeze.closure.current":
        "acceptance:test_release_refuses_without_a_current_closure_receipt",
}

# Why each UNKNOWN is still UNKNOWN. Empty is the goal; a name here is a
# commitment someone can read, not silence.
UNKNOWN_REASONS: dict[str, str] = {}


def overall_verdict(obligations: dict[str, Verdict] | None = None) -> Verdict:
    """PASS only when every obligation is PASS.

    Delegates to conceptgate.cg_obligations.aggregate -- the same rule the
    obligation layer already applies, so UNKNOWN cannot be laundered into PASS
    by a second implementation.
    """
    @dataclass
    class _R:            # aggregate() only reads .verdict
        verdict: Verdict

    return aggregate([_R(v) for v in (obligations or OBLIGATIONS).values()])


def _launcher_available() -> bool:
    """A launcher exists AND can produce receipts. File presence alone is the
    check round 20 rejected -- an empty stub would satisfy it."""
    module = HERE / "reviewer_runner.py"
    if not module.is_file():
        return False
    source = module.read_text(encoding="utf-8")
    return all(marker in source for marker in
               ("def probe_isolation", "def run_reviewer", "produced_by"))


def _closure_receipt() -> dict | None:
    """The most recent closure receipt, if it describes the CURRENT surface."""
    from _evaluator import frozen_surface_drift
    candidates = sorted(RESULTS.glob("closure_*.json"))
    for path in reversed(candidates):
        doc = json.loads(path.read_text(encoding="utf-8"))
        if not frozen_surface_drift(doc.get("frozen_surface_hashes")):
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
            try:
                status = rr.verify_isolation_receipt(
                    doc, packet=RESULTS / doc.get("packet_file", "missing"),
                    assignment=HERE / SPEC["reviewer_assignment_file"])
            except rr.ReviewerRunnerError as exc:
                unproven.append(f"{rid}: {exc}")
                continue
            if status != "PASS":
                unproven.append(f"{rid}: isolation {status}")
        rows.append(_line("BLOCKED" if unproven else "PASS",
                          "agent reviewer isolation",
                          "; ".join(unproven)[:70] if unproven
                          else f"{len(agents)} probed"))

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

    digest = hashlib.sha256(
        json.dumps(now, sort_keys=True).encode("utf-8")).hexdigest()
    receipt = {
        "kind": "freeze-closure-receipt-v1",
        "frozen_surface_digest": digest,
        "frozen_surface_hashes": now,
        "steps": [label for label, _ in CLOSURE_STEPS],
        "artifacts": {name: _sha256(RESULTS / name) for name in (
            "calibration.json", "redteam_provider_isolation.json",
            "redteam_codex_mcp_isolation.json")},
    }
    out = RESULTS / f"closure_{digest[:12]}.json"
    out.write_text(json.dumps(receipt, ensure_ascii=False, indent=1),
                   encoding="utf-8")
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
            return cls(mode, allow_partial=False, require_launcher=True,
                       require_closure=True, matrix_cells=SPEC["expected_cells"])
        raise SystemExit(f"unknown mode {mode!r}")


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

    # ALL unmet preconditions, not the first one. Reporting one at a time
    # makes a caller fix it, re-run, and discover the next -- and makes the
    # output an understatement of what is missing.
    unmet: list[str] = []
    if spec.require_closure and _closure_receipt() is None:
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
        assignment.write_text(json.dumps(
            {"status": "ASSIGNED",
             "reviewers": [{"reviewer_id": "e2e-A"}, {"reviewer_id": "e2e-B"}]}),
            encoding="utf-8")
        audit_spec = {**SPEC, "reviewer_assignment_file": str(assignment)}
        a_sha = _sha256(assignment)
        p_sha = _sha256(packet_path)
        ids = list(json.loads(key_path.read_text(encoding="utf-8"))["unblinding_key"])
        fixture_sha = _sha256(HERE / "safety_audit_rubric_fixture.json")
        answers = json.loads((HERE / "safety_audit_rubric_answers.json").read_text(
            encoding="utf-8"))["answers"]
        labels = []
        for rid in ("e2e-A", "e2e-B"):
            lp = root / f"labels_{rid}.json"
            lp.write_text(json.dumps(
                {"reviewer_id": rid, "packet_sha256": p_sha,
                 "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
                 "qualification": dict(answers),
                 "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
            labels.append(lp)
        naive_label = root / "labels_unqualified.json"
        naive_label.write_text(json.dumps(
            {"reviewer_id": "e2e-A", "packet_sha256": p_sha,
             "assignment_sha256": a_sha, "fixture_sha256": fixture_sha,
             "qualification": naive,
             "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
        try:
            asa.main(["run_pipeline", str(primary), str(packet_path),
                      str(key_path), str(naive_label), str(labels[1]),
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
                      str(key_path), str(walkin), str(labels[1]),
                      "--out-root", str(root)])
        except SystemExit as exc:
            refused_walkin = "is not in" in str(exc)
        else:
            refused_walkin = False
        print(f"  [7] {STAGE_IDS[7]:<32}refused={refused_walkin}")
        if not refused_walkin:
            failures.append("the adjudicator accepted an undeclared reviewer")

        # --- reviewer isolation (release only) --------------------------
        if spec.require_launcher:
            import reviewer_runner as rr
            iso_status = []
            for rid in ("e2e-A", "e2e-B"):
                try:
                    bundled = rr.build_reviewer_bundle(
                        packet_path, root / "reviewer" / rid)
                    doc = rr.run_reviewer(bundled, rid, assignment=assignment)
                    rr.verify_isolation_receipt(doc, packet=bundled,
                                                assignment=assignment)
                except rr.ReviewerRunnerError as exc:
                    failures.append(f"reviewer isolation for {rid}: {exc}")
                    iso_status.append("ERROR")
                    continue
                iso_status.append(doc["status"])
                leaked = [x["probe"] for x in doc["forbidden_probes"]
                          if x["reachable"]]
                if leaked:
                    failures.append(f"reviewer {rid} reached {leaked}")
                elif doc["status"] != "PASS":
                    failures.append(
                        f"reviewer isolation for {rid} is {doc['status']}: the "
                        "boundary was not exercised, which is not a pass")
            print(f"  [--] reviewer.isolation-enforced      {iso_status}")

        # --- 8. adjudication -------------------------------------------
        rc = asa.main(["run_pipeline", str(primary), str(packet_path),
                       str(key_path), *[str(p) for p in labels],
                       "--out-root", str(root)])
        if rc != 0:
            failures.append("adjudicator CLI returned non-zero")
        bundle_path = root / "results" / f"adjudicated_{primary.stem}.json"
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
    # Machine-readable coverage, so a reader does not have to infer it from
    # prose that can drift from the code.
    unknown = sorted(k for k, v in OBLIGATIONS.items() if v is not Verdict.PASS)
    coverage = {
        "obligations_pass": sorted(k for k, v in OBLIGATIONS.items()
                                   if v is Verdict.PASS),
        "obligations_unknown": unknown,
        "overall": overall_verdict().value,
        "not_covered_at_all": ["provider.execution", "qualification.pilot",
                               "authorization.issuance", "attempt.claim"],
    }
    print(f"\n  coverage: {json.dumps(coverage)}")

    if failures:
        print(f"  FAIL ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
        return FAIL
    if overall_verdict() is not Verdict.PASS:
        print(f"  PARTIAL -- {len(unknown)} obligation(s) not shown to hold:")
        for name in unknown:
            print(f"    - {name}: {UNKNOWN_REASONS.get(name, '(no reason recorded)')}")
        if not spec.allow_partial:
            print(f"  {spec.mode} does not accept PARTIAL.")
            return FAIL
        print("  Every step executed, but PARTIAL is not a pass: an obligation "
              "nobody has demonstrated could be silently absent.")
        return BLOCKED
    print("  PASS -- the offline downstream path is wired end to end.")
    print("  Not a claim about provider behaviour, and not a substitute for")
    print("  qualification: run `doctor` for what is still refused.")
    return 0


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
                       help="the 32-cell run; allowed only after --release "
                            "passes")
    args = ap.parse_args()
    if args.cmd == "closure":
        return closure()
    if args.cmd == "doctor":
        return doctor(args.config)
    mode = ("release" if args.release else
            "primary" if args.primary else "offline-smoke")
    return run_pipeline(RunSpec.for_mode(mode))


if __name__ == "__main__":
    raise SystemExit(main())
