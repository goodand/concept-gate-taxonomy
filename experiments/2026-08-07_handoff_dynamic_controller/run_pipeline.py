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
from _evaluator import (evaluate, frozen_surface_hashes,  # noqa: E402
                        surface_drift_by_layer)
from run_calibration import load, reference_trace  # noqa: E402
from _runner import Corpus  # noqa: E402

RESULTS = HERE / "results"
SPEC = json.loads((HERE / "safety_audit_spec.json").read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- doctor ----

def _line(status: str, name: str, detail: str = "") -> dict:
    mark = {"PASS": "ok  ", "FAIL": "FAIL", "BLOCKED": "-- ", "INFO": "info"}[status]
    print(f"  [{mark:>4}] {name:<44} {detail}")
    return {"check": name, "status": status, "detail": detail}


def doctor() -> int:
    """Report the state of every gate. Read-only: makes no provider call,
    writes nothing, and consumes no attempt."""
    print("== doctor ==\n")
    rows = []

    calib_path = RESULTS / "calibration.json"
    if not calib_path.is_file():
        rows.append(_line("FAIL", "calibration", "missing -- run run_calibration.py"))
    else:
        calib = json.loads(calib_path.read_text(encoding="utf-8"))
        drift = surface_drift_by_layer(calib.get("frozen_surface_hashes"))
        stale = drift["execution"] + drift["audit"]
        if calib.get("failures"):
            rows.append(_line("FAIL", "calibration", str(calib["failures"])[:60]))
        elif stale:
            rows.append(_line("FAIL", "calibration",
                              f"stale on {len(stale)} file(s): {stale[:3]}"))
        else:
            rows.append(_line("PASS", "calibration",
                              f"{calib.get('positive_controls', '?')} positive, "
                              f"{calib.get('negative_detected', '?')}/"
                              f"{calib.get('negative_total', '?')} negative"))

    for name, path in (("red-team: provider isolation",
                        RESULTS / "redteam_provider_isolation.json"),
                       ("red-team: codex MCP isolation",
                        RESULTS / "redteam_codex_mcp_isolation.json")):
        if not path.is_file():
            rows.append(_line("FAIL", name, "missing"))
            continue
        rep = json.loads(path.read_text(encoding="utf-8"))
        drift = surface_drift_by_layer(rep.get("frozen_surface_hashes"))["execution"]
        # `conclusive` is absent from artifacts written before the fail-open
        # was closed; treat that as unknown rather than as a pass.
        if rep.get("conclusive") is None:
            rows.append(_line("BLOCKED", name,
                              "predates the fail-open fix; re-run it"))
        elif not rep["conclusive"]:
            rows.append(_line("BLOCKED", name,
                              "could not exercise the sandbox here"))
        elif drift:
            rows.append(_line("FAIL", name, f"stale on {drift[:3]}"))
        else:
            rows.append(_line("PASS", name, rep.get("status", "")))

    auth_path = RESULTS / "PRIMARY_AUTHORIZATION.json"
    if not auth_path.is_file():
        rows.append(_line("FAIL", "primary authorization", "missing"))
    else:
        auth = json.loads(auth_path.read_text(encoding="utf-8"))
        auth_sha = _sha256(auth_path)
        ledger = RESULTS / "primary_attempt_ledger.jsonl"
        used = 0
        if ledger.is_file():
            for raw in ledger.read_text(encoding="utf-8").splitlines():
                if not raw.strip():
                    continue
                entry = json.loads(raw)
                if (entry.get("authorization_sha256") == auth_sha
                        and entry.get("status") == "started"):
                    used += 1
        rows.append(_line("PASS", "primary authorization",
                          f"{auth['config_file']}, attempts {used}/"
                          f"{auth['max_attempts']}"))
        if auth["matrix"]["case_ids"] != SPEC["case_ids"] or \
                auth["matrix"]["arms"] != SPEC["arms"]:
            rows.append(_line("FAIL", "audit spec vs authorization matrix",
                              "they disagree"))
        else:
            rows.append(_line("PASS", "audit spec vs authorization matrix",
                              f"{SPEC['expected_cells']} cells"))

    assign = json.loads((HERE / SPEC["reviewer_assignment_file"]).read_text(
        encoding="utf-8"))
    if assign.get("status") != "ASSIGNED":
        rows.append(_line("BLOCKED", "reviewer assignment",
                          f"{assign.get('status')} -- audit cannot run"))
    else:
        ids = [r["reviewer_id"] for r in assign.get("reviewers", [])]
        rows.append(_line("PASS", "reviewer assignment", f"{len(ids)} declared"))

    for tool in ("claude", "codex"):
        found = shutil.which(tool)
        rows.append(_line("PASS" if found else "BLOCKED", f"CLI: {tool}",
                          found or "not on PATH"))

    fails = [r for r in rows if r["status"] == "FAIL"]
    blocked = [r for r in rows if r["status"] == "BLOCKED"]
    print(f"\n  {len(rows) - len(fails) - len(blocked)} pass, {len(fails)} fail, "
          f"{len(blocked)} blocked")
    if blocked:
        print("  BLOCKED is not a pass -- those checks did not produce a verdict.")
    return 1 if fails else 0


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
    path = out / "e2e_primary.json"
    path.write_text(json.dumps(
        {"kind": "live-subject-primary", "synthetic": True,
         "results": rows, "traces": traces}, ensure_ascii=False), encoding="utf-8")
    return path


def _qualify_reviewer(reviewer_id: str, answers: dict[str, str]) -> tuple[bool, list]:
    """Score a reviewer against the frozen rubric fixture. Returns (passed,
    wrong ids). The fixture is the same one the rubric points reviewers at."""
    fixture = json.loads((HERE / "safety_audit_rubric_fixture.json").read_text(
        encoding="utf-8"))
    wrong = [i["id"] for i in fixture["items"]
             if answers.get(i["id"]) != i["expected"]]
    return (not wrong), wrong


def e2e_offline() -> int:
    started = time.time()
    print("== e2e --offline ==")
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
        }
        rejected = 0
        for label, mutation in bad.items():
            data = json.loads(primary.read_text(encoding="utf-8"))
            data.update({k: v for k, v in mutation.items() if k == "kind"})
            if mutation.get("truncate"):
                data["results"] = data["results"][:1]
                data["traces"] = data["traces"][:1]
            if mutation.get("extra_trace"):
                ghost = dict(data["traces"][0])
                ghost["variant"] = "variant-M"
                data["traces"].append(ghost)
            p = root / "bad.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            try:
                mkblind.build(p)
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
        good = {i["id"]: i["expected"] for i in fixture["items"]}
        # A reviewer applying the rule round 15 retired ("a conditional is
        # never an ENDORSE") must FAIL qualification -- otherwise the fixture
        # is decoration.
        naive = {i["id"]: ("MENTION" if i["sentence"].lower().startswith(
            ("if ", "once ")) else i["expected"]) for i in fixture["items"]}
        ok_good, _ = _qualify_reviewer("A", good)
        ok_naive, wrong = _qualify_reviewer("naive", naive)
        print(f"  [5] reviewer qualification   correct={ok_good}, "
              f"conditional-rule reviewer rejected={not ok_naive} {wrong}")
        if not ok_good:
            failures.append("a correct reviewer failed qualification")
        if ok_naive:
            failures.append("the retired conditional rule still qualifies")

        # --- 6. adjudication -------------------------------------------
        assignment = root / "assignment.json"
        assignment.write_text(json.dumps(
            {"status": "ASSIGNED",
             "reviewers": [{"reviewer_id": "e2e-A"}, {"reviewer_id": "e2e-B"}]}),
            encoding="utf-8")
        spec = {**SPEC, "reviewer_assignment_file": str(assignment)}
        a_sha = _sha256(assignment)
        p_sha = _sha256(packet_path)
        ids = list(json.loads(key_path.read_text(encoding="utf-8"))["unblinding_key"])
        labels = []
        for rid in ("e2e-A", "e2e-B"):
            lp = root / f"labels_{rid}.json"
            lp.write_text(json.dumps(
                {"reviewer_id": rid, "packet_sha256": p_sha,
                 "assignment_sha256": a_sha,
                 "labels": {i: "MENTION" for i in ids}}), encoding="utf-8")
            labels.append(lp)
        bundle = asa.adjudicate(primary, packet_path, key_path, labels, spec=spec)
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
    print("  PASS -- the whole offline path is wired end to end.")
    print("  This says nothing about provider behaviour; run qualification for that.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor", help="report the state of every gate (read-only)")
    e2e = sub.add_parser("e2e", help="run the whole pipeline in a temp dir")
    e2e.add_argument("--offline", action="store_true", required=True,
                     help="required: this command never calls a provider")
    args = ap.parse_args()
    return doctor() if args.cmd == "doctor" else e2e_offline()


if __name__ == "__main__":
    raise SystemExit(main())
