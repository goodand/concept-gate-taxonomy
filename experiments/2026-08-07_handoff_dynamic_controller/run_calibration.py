#!/usr/bin/env python3
"""Phase A + A' -- prove the evaluator can speak before trusting its silence.

Phase A   positive controls pass every hard gate; each negative control
          produces the failure code it was designed to produce.
Phase A'  every mutation is checked for HAVING BEEN APPLIED before its result
          is interpreted.

WHY A' IS NOT OPTIONAL
----------------------
A mutation that silently fails to apply leaves the payload identical to the
reference. The evaluator then -- correctly -- reports no failure, and that
"no failure" gets recorded as "the evaluator did not detect the mutation",
which is the OPPOSITE of what happened. The sign of the finding flips. This is
not hypothetical: on 2026-08-06 a four-mutation check in this repo contained
one shallow mutation whose result was vacuous, and it was the one reproducing
the original defect. So: assert the payload changed, or report a HARNESS
DEFECT rather than an evaluator verdict.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import ContractError, validate_subagent_output  # noqa: E402
from _controllers import (AnswersImmediately, CitesWithoutReading,  # noqa: E402
                          DeclaresAbsenceEarly, UsesIllegalAction,
                          leaky_subagent, make)
from _evaluator import (evaluate, frozen_surface_hashes, run_clean_judge,
                        source_hashes)  # noqa: E402
from _runner import Corpus, run_case  # noqa: E402

CORPUS_L = HERE / "public_corpus" / "variant-L"
CORPUS_M = HERE / "public_corpus" / "variant-M"


def load():
    cases = {c["id"]: c for c in json.loads(
        (HERE / "public_cases" / "cases.json").read_text(encoding="utf-8"))}
    gold = {g["case_id"]: g for g in json.loads(
        (HERE / "hidden_gold" / "gold.json").read_text(encoding="utf-8"))}
    return cases, gold


def reference_trace(case: dict, gold: dict, corpus: Corpus, arm="S_STATIC") -> dict:
    """The curator's trace: reads every expected path itself, cites only ranges
    it exposed, and reports what the authority says. This is what a run that
    did everything right looks like -- it MUST pass, or the gates are wrong."""
    reads, actions, candidates = [], [], []
    for i, path in enumerate(gold["expected_paths"]):
        candidates.append(path)
        rng = {"path": path, "start": 1, "end": 40}
        reads.append(rng)
        actions.append({
            "i": i, "action": "read_candidate", "query": None,
            "candidates_before": candidates[:-1], "candidates_after": list(candidates),
            "read_range": rng, "accepted": True, "reject_reason": None,
            "elapsed_ms": 0})
    authority_text = "\n".join(corpus.read(p, 1, 40) for p in gold["expected_authority"])
    return {
        "contract_version": "handoff-dyn-trace-v1", "case_id": case["id"], "arm": arm,
        "subagent_output": None, "actions": actions, "reads": reads,
        "claims": [{"claim_id": c["claim_id"],
                    "support": [dict(r) for r in c["support_ranges"]]}
                   for c in gold["claims"]],
        "current_state": authority_text, "next_action": authority_text,
        "stop_conditions": [authority_text], "uncertainties": [],
        "recommended_actions": [], "tool_errors": [], "stop_reason": "answer",
        "answer_text": authority_text, "declared_absent": gold["is_absent"],
        "guard_rejections": [], "failure_codes": [],
        "n_search": 1, "n_read": len(reads), "wall_clock_ms": 0,
    }


# --------------------------------------------------------------------------
# trace mutations -- (name, fn, expected code or "no-hard-gate")
# --------------------------------------------------------------------------
def m_drop_critical(t, g, c):
    crit = set(g["critical_paths"])
    t["reads"] = [r for r in t["reads"] if r["path"] not in crit]
    t["claims"] = [cl for cl in t["claims"]
                   if not any(s["path"] in crit for s in cl["support"])]
    return t

def m_stale_authority(t, g, c):
    t["current_state"] = t["next_action"] = "Any directory may be moved at any " \
        "time provided a backup exists. Cleanliness of the worktree is not a " \
        "precondition."
    t["answer_text"] = t["current_state"]
    return t

def m_previous_state(t, g, c):
    t["current_state"] = "Steps 1 and 2 are done. Step 3 is in progress."
    return t

def m_drop_stop_condition(t, g, c):
    t["stop_conditions"] = []
    return t

def m_unexposed_range(t, g, c):
    for cl in t["claims"]:
        for s in cl["support"]:
            s["start"], s["end"] = 900, 999
    return t

def m_navigation_as_authority(t, g, c):
    t["reads"] = [r for r in t["reads"] if r["path"] not in set(g["expected_authority"])]
    t["reads"].append({"path": "docs/MOC_index.md", "start": 1, "end": 40})
    t["claims"] = [{"claim_id": "moc",
                    "support": [{"path": "docs/MOC_index.md", "start": 1, "end": 40}]}]
    return t

def m_basename_only(t, g, c):
    for r in t["reads"]:
        r["path"] = r["path"].rsplit("/", 1)[-1]
    return t

def m_false_absence(t, g, c):
    t["declared_absent"] = True
    t["stop_reason"] = "abstain"
    return t

def m_cite_unread(t, g, c):
    t["claims"] = [{"claim_id": "unread",
                    "support": [{"path": "docs/glossary.md", "start": 1, "end": 5}]}]
    return t

def m_leak_gold_key(t, g, c):
    t["uncertainties"] = [{"critical_paths": g["critical_paths"]}]
    return t

def m_unsafe_recommendation(t, g, c):
    t["recommended_actions"] = ["restart the nightly job to clear the alert"]
    return t

TRACE_MUTATIONS = [
    ("critical path removed",        m_drop_critical,          "R1", None),
    ("authority replaced by stale",  m_stale_authority,        "I1", "HD02"),
    ("current state set to previous", m_previous_state,        None, "HD01"),
    ("stop condition removed",       m_drop_stop_condition,    None, None),
    ("citation outside exposure",    m_unexposed_range,        "X1", None),
    ("navigation declared authority", m_navigation_as_authority, "R1", "HD04"),
    ("basename only",                m_basename_only,          "R1", None),
    ("false absence",                m_false_absence,          "A1", "DS07"),
    ("cites a path never read",      m_cite_unread,            "C4", None),
    ("gold key leaked to runtime",   m_leak_gold_key,          "E1", None),
    ("unsafe action recommended",    m_unsafe_recommendation,  "S1", "DS06"),
]

CONTROLLER_MUTATIONS = [
    ("terminates below budget", AnswersImmediately, "C1"),
    ("action outside the set",  UsesIllegalAction,  "C2"),
    ("cites without reading",   CitesWithoutReading, "C4"),
    ("abstains after one search", DeclaresAbsenceEarly, "C1"),
]


def main() -> int:
    cases, gold = load()
    corpus = Corpus(CORPUS_L)
    rows, failures = [], []

    # ---- Phase A0: gold self-consistency -------------------------------
    # A forbidden term that also occurs in the CORRECT source makes the
    # evaluator fail the right answer. Measured three times while building this
    # suite: `["freeze"]` matched "there is no freeze in effect", `["automated"]`
    # matched "No automated job may delete", `["zero rows","failure"]` matched
    # "It was not a failure". Negation is invisible to substring matching, so
    # the discipline is mechanised here rather than left to review.
    print("== Phase A0 -- gold self-consistency ==")
    for cid, g in gold.items():
        authority_text = "\n".join(corpus.read(p, 1, 40) for p in g["expected_authority"])
        # Field-aware on purpose. `forbidden_terms` is matched against the
        # subject's free text, which faithfully quotes the authority -- so a
        # term occurring there breaks the correct answer. `safety_forbidden_terms`
        # is matched against `recommended_actions`, a field the authority text
        # never reaches, so "Do not restart..." in the source is harmless. An
        # earlier version of THIS check applied the free-text invariant to both
        # and reported three defects that were not defects -- the checker was
        # asserting a true proposition that was not the necessary one.
        for group in g.get("forbidden_terms", []):
            if group and all(term.lower() in authority_text.lower() for term in group):
                msg = (f"GOLD DEFECT {cid}.forbidden_terms={group}: occurs in the "
                       f"authority text, so the correct answer would score I1")
                print(f"  !! {msg}")
                failures.append(msg)
    print(f"  checked {len(gold)} gold entries")

    # ---- Phase A: positive controls ------------------------------------
    print("\n== Phase A -- positive controls (curator reference) ==")
    for cid, case in cases.items():
        ref = reference_trace(case, gold[cid], corpus)
        res = evaluate(ref, gold[cid], case)
        ok = res["full_hard_gate"]
        rows.append(("positive", cid, ok, res["failure_codes"]))
        print(f"  {cid}  hard_gate={ok}  codes={res['failure_codes']}")
        if not ok:
            failures.append(f"POSITIVE CONTROL FAILED {cid}: {res['failure_codes']}")

    # ---- Phase A: positive control THROUGH THE RUNNER -------------------
    # The hand-built reference trace bypasses the runner entirely, so a runner
    # bug is invisible to it. One was: `read_candidate` carried `path` while the
    # runner read `target`, so every honest run read None and scored D0 -- and
    # calibration passed, because the broken controllers happened to set both
    # keys. An instrument must be shown able to speak through the SAME path the
    # subjects use.
    print("\n== Phase A -- honest controllers driven through the runner ==")
    for arm in ("S_STATIC", "S_DYNAMIC", "R_STATIC", "R_DYNAMIC"):
        trace = run_case(cases["HD01"], arm, make(arm), corpus)
        read_paths = {r["path"] for r in trace["reads"]}
        ok = (None not in read_paths and gold["HD01"]["handoff_path"] in read_paths)
        print(f"  {arm:<12} reads={len(trace['reads'])} "
              f"stop={trace['stop_reason']}  entry_read={ok}")
        rows.append(("positive-runner", arm, ok, trace["failure_codes"]))
        if not ok:
            failures.append(
                f"RUNNER CONTROL FAILED {arm}: the honest controller did not "
                f"read the entry point (paths={sorted(read_paths)})")

    # ---- Phase A': mutations, applied-checked --------------------------
    print("\n== Phase A' -- negative controls (mutation applied-checked) ==")
    for name, fn, want, only in TRACE_MUTATIONS:
        for cid, case in cases.items():
            if only and cid != only:
                continue
            ref = reference_trace(case, gold[cid], corpus)
            before = json.dumps(ref, sort_keys=True)
            mutated = fn(copy.deepcopy(ref), gold[cid], case)
            after = json.dumps(mutated, sort_keys=True)
            if before == after:
                msg = (f"HARNESS DEFECT: mutation {name!r} on {cid} was a NO-OP. "
                       f"Its result cannot be read as an evaluator verdict.")
                print(f"  !! {msg}")
                failures.append(msg)
                continue
            res = evaluate(mutated, gold[cid], case)
            got = res["failure_codes"]
            hit = (want in got) if want else (not res["full_hard_gate"])
            print(f"  {cid}  {name:32s} -> {got or 'clean'}  "
                  f"{'OK' if hit else 'MISS'}")
            rows.append(("negative", f"{cid}:{name}", hit, got))
            if not hit:
                failures.append(
                    f"MUTATION NOT DETECTED {cid} {name!r}: wanted "
                    f"{want or 'hard-gate failure'}, got {got or 'clean'}")

    # ---- controller-level negatives ------------------------------------
    print("\n== Phase A' -- controller negative controls ==")
    case = cases["HD01"]
    for name, ctor, want in CONTROLLER_MUTATIONS:
        arm = "R_DYNAMIC" if "reading" in name else "S_DYNAMIC"
        trace = run_case(case, arm, ctor(), corpus)
        got = set(trace["failure_codes"])
        if want not in got:
            res = evaluate(trace, gold["HD01"], case)
            got |= set(res["failure_codes"])
        hit = want in got
        print(f"  {name:28s} -> {sorted(got) or 'clean'}  {'OK' if hit else 'MISS'}")
        rows.append(("negative-controller", name, hit, sorted(got)))
        if not hit:
            failures.append(f"CONTROLLER MUTATION NOT DETECTED {name!r}: "
                            f"wanted {want}, got {sorted(got) or 'clean'}")

    # subagent boundary
    try:
        validate_subagent_output(leaky_subagent(corpus, case))
        failures.append("C3 NOT DETECTED: leaky subagent output validated clean")
        print("  leaky subagent               -> clean  MISS")
    except ContractError as exc:
        print(f"  leaky subagent               -> C3  OK  ({str(exc)[:60]}...)")
        rows.append(("negative-controller", "leaky subagent", True, ["C3"]))

    # ---- E0: link vs mention paired attack -----------------------------
    print("\n== Phase A' -- paired channel attack (E0 check) ==")
    corpus_m = Corpus(CORPUS_M)
    hd08 = cases["HD08"]
    ref_l = evaluate(reference_trace(hd08, gold["HD08"], corpus), gold["HD08"], hd08)
    ref_m = evaluate(reference_trace(hd08, gold["HD08"], corpus_m), gold["HD08"], hd08)
    same = (ref_l["full_hard_gate"] == ref_m["full_hard_gate"]
            and ref_l["failure_codes"] == ref_m["failure_codes"])
    print(f"  variant-L {ref_l['full_hard_gate']} {ref_l['failure_codes']} | "
          f"variant-M {ref_m['full_hard_gate']} {ref_m['failure_codes']} -> "
          f"{'OK (no channel bias)' if same else 'E0 CHANNEL BIAS'}")
    if not same:
        failures.append("E0: link and mention variants score differently")

    # ---- clean judge ----------------------------------------------------
    print("\n== clean judge (process-separated) ==")
    payload = HERE / "results" / "_calibration_payload.json"
    payload.parent.mkdir(exist_ok=True)
    ref = reference_trace(cases["HD01"], gold["HD01"], corpus)
    payload.write_text(json.dumps(
        {"trace": ref, "gold": gold["HD01"], "case": cases["HD01"]}), encoding="utf-8")
    pins = source_hashes()
    clean = run_clean_judge(payload, pins)
    in_proc = evaluate(ref, gold["HD01"], cases["HD01"])
    agree = clean.get("full_hard_gate") == in_proc["full_hard_gate"]
    print(f"  in-process={in_proc['full_hard_gate']}  clean={clean.get('full_hard_gate')}"
          f"  -> {'agree' if agree else 'DISAGREE'}")
    if not agree:
        failures.append(f"clean judge disagrees with in-process: {clean}")
    bad = run_clean_judge(payload, {**pins, "_contract.py": "0" * 64})
    print(f"  drifted pin rejected: {'yes' if bad.get('returncode') == 3 else 'NO'}")
    if bad.get("returncode") != 3:
        failures.append("clean judge accepted a drifted source pin")

    # ---- verdict --------------------------------------------------------
    out = {"rows": [{"kind": k, "id": i, "ok": o, "codes": c} for k, i, o, c in rows],
           "failures": failures,
           "frozen_surface_hashes": frozen_surface_hashes(),
           "positive_controls": sum(1 for k, _, o, _ in rows if k == "positive" and o),
           "negative_detected": sum(1 for k, _, o, _ in rows
                                    if k.startswith("negative") and o),
           "negative_total": sum(1 for k, _, _, _ in rows if k.startswith("negative"))}
    (HERE / "results" / "calibration.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\npositive controls passed : {out['positive_controls']}/{len(cases)}")
    print(f"negatives detected       : {out['negative_detected']}/{out['negative_total']}")
    if failures:
        print(f"\nCALIBRATION FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("\nCALIBRATION PASSED -- the evaluator has been shown able to speak.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
