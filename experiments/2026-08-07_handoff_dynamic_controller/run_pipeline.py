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
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import apply_safety_audit as asa  # noqa: E402
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
        msg = str(exc)
        # A gate that could not reach a verdict is BLOCKED, not FAIL. The
        # red-teams say so explicitly; anything else that refuses has failed.
        status = "BLOCKED" if "BLOCKED" in msg or "inconclusive" in msg else "FAIL"
        return _line(status, name, msg[:96]), None
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
            used = 0
            ledger = RESULTS / "primary_attempt_ledger.jsonl"
            if ledger.is_file():
                for raw in ledger.read_text(encoding="utf-8").splitlines():
                    if raw.strip():
                        entry = json.loads(raw)
                        if (entry.get("authorization_sha256") == auth_sha
                                and entry.get("status") == "started"):
                            used += 1
            rows.append(_line("PASS" if used < max_attempts else "FAIL",
                              "primary attempts remaining",
                              f"{max_attempts - used} of {max_attempts}"))

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
    path = out / "e2e_primary.json"
    path.write_text(json.dumps(
        {"kind": "live-subject-primary", "synthetic": True,
         "config_file": auth["config_file"],
         "config_sha256": _sha256(HERE / auth["config_file"]),
         "output_file": path.name,
         "results": rows, "traces": traces}, ensure_ascii=False), encoding="utf-8")

    # Provenance the audit gate will actually check, built in the temp root.
    # Round 17, finding #5: the gate validated shape only, so a hand-built
    # artifact was accepted as a primary result. The E2E does NOT switch that
    # check off -- it satisfies it with a temp authorization and a completed
    # attempt, so the provenance path is exercised rather than skipped.
    (out / "results").mkdir(exist_ok=True)
    auth_copy = out / "results" / "PRIMARY_AUTHORIZATION.json"
    auth_copy.write_text(json.dumps(auth, ensure_ascii=False), encoding="utf-8")
    (out / "results" / "primary_attempt_ledger.jsonl").write_text(
        json.dumps({"authorization_sha256": _sha256(auth_copy),
                    "status": "completed", "output_file": path.name}) + "\n",
        encoding="utf-8")
    return path


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


def e2e_offline() -> int:
    started = time.time()
    print("== e2e --offline ==")
    print("   COVERS   artifact provenance -> audit gate -> packet CLI ->")
    print("            blinding -> reviewer qualification -> adjudicator CLI ->")
    print("            final bundle written to disk and read back")
    print("   DOES NOT COVER  provider execution, qualification pilots,")
    print("            authorization issuance, attempt claim. Those need a")
    print("            provider; this command deliberately has none.")
    print("   no provider calls, no attempt consumed, temp dir only\n")
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="hd-e2e-") as tmp:
        root = Path(tmp)
        (root / "results").mkdir()

        # --- 1. a well-formed primary artifact -------------------------
        primary = _synthetic_primary(root)
        n = len(json.loads(primary.read_text(encoding="utf-8"))["results"])
        print(f"  [1] primary artifact         {n} cells")
        if n != SPEC["expected_cells"]:
            failures.append(f"synthetic primary has {n} cells")

        # --- 2. the audit input gate MUST reject malformed input --------
        # Negative controls first: a stage that accepts everything is not a
        # gate, and this is the failure that reached review three rounds
        # running.
        bad = {
            "non-primary kind": {"kind": "live-subject-pilot"},
            "short matrix": {"truncate": 1},
            "extra trace": {"extra_trace": True},
            "unauthorized config": {"config_file": "phase_c_live_config.json"},
            "wrong config hash": {"config_sha256": "0" * 64},
            "no completed attempt": {"output_file": "never_ran.json"},
        }
        rejected = 0
        for label, mutation in bad.items():
            data = json.loads(primary.read_text(encoding="utf-8"))
            data.update({k: v for k, v in mutation.items()
                         if k in ("kind", "config_file", "config_sha256",
                                  "output_file")})
            if mutation.get("truncate"):
                data["results"] = data["results"][:1]
                data["traces"] = data["traces"][:1]
            if mutation.get("extra_trace"):
                ghost = dict(data["traces"][0])
                ghost["variant"] = "variant-M"
                data["traces"].append(ghost)
            p = root / "bad.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            spec = {**SPEC, "provenance": {**SPEC["provenance"],
                                           "root": str(root)}}
            try:
                mkblind.build(p, spec=spec)
            except mkblind.AuditInputError:
                rejected += 1
            else:
                failures.append(f"audit gate ACCEPTED a {label} artifact")
        print(f"  [2] audit gate negatives     {rejected}/{len(bad)} rejected")

        # --- 3. packet via the PRODUCTION CLI ---------------------------
        rc = mkblind.main(["run_pipeline", str(primary), str(root)])
        if rc != 0:
            failures.append("packet CLI returned non-zero")
        workspace = root / "audit_workspace" / "e2e_primary"
        key_path = root / "results" / "safety_audit_key_e2e_primary.json"
        packet_path = workspace / "packet.json"
        contents = sorted(p.name for p in workspace.iterdir())
        print(f"  [3] packet (production CLI)  workspace={contents}")
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
        print(f"  [4] blinding                 {packet['n_items']} items, "
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
        print(f"  [5] reviewer qualification   correct={ok_good}, "
              f"conditional-rule reviewer rejected={not ok_naive} {wrong}")
        if not ok_good:
            failures.append("a correct reviewer failed qualification")
        if ok_naive:
            failures.append("the retired conditional rule still qualifies")

        # --- 6. adjudication -------------------------------------------
        assignment = root / "safety_audit_reviewer_assignment.json"
        assignment.write_text(json.dumps(
            {"status": "ASSIGNED",
             "reviewers": [{"reviewer_id": "e2e-A"}, {"reviewer_id": "e2e-B"}]}),
            encoding="utf-8")
        spec = {**SPEC, "reviewer_assignment_file": str(assignment)}
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
        print(f"  [6] adjudication             {audit['cell_verdicts']}")
        print(f"  [7] final bundle             "
              f"adjudicated_rate={audit['adjudicated_full_hard_gate_rate']}, "
              f"violations={audit['confirmed_safety_violation_count']}")
        if audit["adjudicated_full_hard_gate_rate"] is None:
            failures.append("final bundle carries no adjudicated rate")
        if "NOT machine-verified" not in audit["independence"]:
            failures.append("independence claim is overstated in the bundle")

        # A single reviewer must NOT be able to produce a bundle unless the
        # frozen spec says so.
        try:
            asa.adjudicate(primary, packet_path, key_path, labels[:1], spec=spec)
        except SystemExit:
            pass
        else:
            failures.append("a single reviewer produced a bundle")

    elapsed = time.time() - started
    print(f"\n  {elapsed:.1f}s")
    if failures:
        print(f"  FAIL ({len(failures)}):")
        for f in failures:
            print(f"    - {f}")
        return 1
    print("  PASS -- the offline downstream path is wired end to end.")
    print("  Not a claim about provider behaviour, and not a substitute for")
    print("  qualification: run `doctor` for what is still refused.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    doc = sub.add_parser("doctor",
                         help="report the state of every gate (read-only)")
    doc.add_argument("--config", default=None,
                     help="config to diagnose; defaults to the one the "
                          "primary authorization points at")
    e2e = sub.add_parser("e2e", help="run the whole pipeline in a temp dir")
    e2e.add_argument("--offline", action="store_true", required=True,
                     help="required: this command never calls a provider")
    args = ap.parse_args()
    return doctor(args.config) if args.cmd == "doctor" else e2e_offline()


if __name__ == "__main__":
    raise SystemExit(main())
