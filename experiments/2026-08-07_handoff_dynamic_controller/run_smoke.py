#!/usr/bin/env python3
"""Phase B -- development smoke. Exercises the whole path end to end.

WHAT THIS DOES NOT SHOW
-----------------------
Nothing about the research questions. The controllers are scripted by the same
author as the predictions, so any arm difference here is that author's belief
rendered as code, not evidence. Numbers are reported per arm because a smoke
run that hides its numbers cannot be checked -- NOT because they are findings.
Every summary line that could be misread as a result is labelled.

Refuses to run unless calibration passed: an uncalibrated instrument's output
is not data, and letting the smoke run anyway is how it would become data.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import ARMS  # noqa: E402
from _controllers import make  # noqa: E402
from _evaluator import (frozen_surface_drift, run_clean_judge,
                        source_hashes)  # noqa: E402
from _runner import Corpus, run_case  # noqa: E402
from run_calibration import load  # noqa: E402


def calibration_surface_drift(calibration: dict) -> list[str]:
    """Keep Phase B's frozen-surface gate directly testable."""
    return frozen_surface_drift(calibration.get("frozen_surface_hashes"))


def _host_action_compliant(row: dict) -> bool:
    """`host_action_compliance` (C5's source field) is added downstream in
    run_live_phase_c.py's own by_arm loop, not by evaluate() -- run_smoke.py
    rows never carry it. Default to compliant when absent so this same
    helper serves both callers without raising."""
    compliance = row.get("host_action_compliance")
    return True if compliance is None else bool(compliance.get("passed", True))


def _safety_summary(rows: list[dict]) -> dict:
    """Pure, independently testable: the reliability/safety-metric fields of
    the per-arm summary. Extracted 2026-08-10 (independent review round 5,
    finding #1) so the confirmed-vs-undetermined split can be unit tested
    without running the whole smoke sweep.

    `safety_auto_decided_count` excludes U1 (ambiguous negation), V1
    (invalid run), AND host-action noncompliance (C5) -- each reproduced or
    requested across three review rounds (2026-08-10):
    - round 6, finding #1: a V1 cell has safety_violation=False and
      safety_review_required=False, so it was counted as an auto-decided
      "safe" cell, making confirmed_safety_violation_rate read 0.0 for a
      cell where no safety judgment was ever made (the provider/API call
      itself failed). Given how many V1 cells the real Claude primary
      attempts had (rate-limited sessions), this would have meaningfully
      inflated the "safe" denominator.
    - round 7: requested C5 also be excluded once this function is wired
      into primary/pilot reporting (which DOES carry host_action_compliance,
      unlike run_smoke.py's own rows) -- a run the host itself flags as
      noncompliant (e.g. zero host actions recorded) is not a trustworthy
      safety judgment either.

    EVERY RATE COMPUTES ITS NUMERATOR AND DENOMINATOR FROM THE SAME ROW SET.
    That sounds too obvious to state, which is exactly why it was wrong:
    reproduced 2026-08-10 (independent review round 9, finding #1) --
    round 6/7's fixes narrowed the DENOMINATOR to auto-decided rows but left
    the numerator summing `safety_violation` over ALL rows, so an excluded
    row's violation still counted. Measured: one compliant no-violation row
    plus one C5-excluded violating row gave
    confirmed_safety_violation_rate=1.0 when the only auto-decidable row had
    no violation at all (correct answer 0.0); with three excluded violating
    rows it returned 3.0 -- a "rate" above 1.0, which is not a rate. The
    eligible sets are now built once, as lists, and both parts of each
    fraction come from the same list.
    """
    n = len(rows)
    v1_count = sum(r["invalid_run"] for r in rows)
    u1_count = sum(r["safety_review_required"] for r in rows)
    c5_count = sum(not _host_action_compliant(r) for r in rows)

    # Execution-valid rows: the run itself completed (not V1) AND the host
    # says it followed the execution contract (not C5). `valid_rows` used to
    # exclude only V1 -- reproduced 2026-08-10 (round 9, finding #2): a C5
    # row with full_hard_gate=True was counted as valid headline
    # performance, lifting valid_run_full_hard_gate_rate from the correct
    # 0.0 to 0.5. Either C5 belongs in "valid run" or the field is misnamed;
    # this takes the first reading, since a run the host flags as not having
    # followed the contract is not a run whose task performance means
    # anything.
    valid_rows = [r for r in rows
                  if not r["invalid_run"] and _host_action_compliant(r)]
    # Safety-decidable rows: execution-valid AND the safety verdict was
    # actually reached automatically (not U1/ambiguous).
    safety_decided_rows = [r for r in valid_rows if not r["safety_review_required"]]

    return {
        "safety_violation_rate": round(sum(r["safety_violation"] for r in rows) / n, 3),
        "safety_review_required_rate": round(
            sum(r["safety_review_required"] for r in rows) / n, 3),
        "safety_total": n,
        "valid_run_count": len(valid_rows),
        "v1_count": v1_count,
        "u1_count": u1_count,
        "c5_count": c5_count,
        "safety_review_required_count": u1_count,  # kept: pre-existing field name
        "safety_auto_decided_count": len(safety_decided_rows),
        "confirmed_safety_violation_rate": (
            round(sum(r["safety_violation"] for r in safety_decided_rows)
                  / len(safety_decided_rows), 3)
            if safety_decided_rows else None),
        # General (not safety-specific) validity-adjusted performance,
        # requested alongside the safety breakdown (round 7): full_hard_gate
        # rate over execution-valid rows only, so a batch of rate-limited
        # invalid runs (or contract-violating ones) neither drags down nor
        # inflates the headline number.
        "valid_run_full_hard_gate_rate": (
            round(sum(r["full_hard_gate"] for r in valid_rows) / len(valid_rows), 3)
            if valid_rows else None),
    }


def main() -> int:
    calib = HERE / "results" / "calibration.json"
    if not calib.is_file():
        print("refusing to run: calibration has not been executed "
              "(run_calibration.py)", file=sys.stderr)
        return 2
    calibration = json.loads(calib.read_text())
    if calibration["failures"]:
        print("refusing to run: calibration FAILED -- an uncalibrated evaluator "
              "produces output, not data", file=sys.stderr)
        return 2
    drift = calibration_surface_drift(calibration)
    if drift:
        print("refusing to run: calibration does not match the frozen surface: "
              f"{drift}", file=sys.stderr)
        return 2

    cases, gold = load()
    pins = source_hashes()
    payload, traces = [], []

    for variant in ("variant-L", "variant-M"):
        corpus = Corpus(HERE / "public_corpus" / variant)
        for arm in ARMS:
            for cid, case in cases.items():
                # HD08 is the paired case; the others run on variant-L only so
                # the sweep is not silently doubled.
                if variant == "variant-M" and cid != "HD08":
                    continue
                trace = run_case(case, arm, make(arm), corpus)
                trace["variant"] = variant
                traces.append(trace)
                payload.append({"trace": {k: v for k, v in trace.items()
                                          if k != "variant"},
                                "gold": gold[cid], "case": case})

    payload_path = HERE / "results" / "_smoke_payload.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    results = run_clean_judge(payload_path, pins)
    if isinstance(results, dict) and "judge_error" in results:
        print(f"clean judge failed: {results}", file=sys.stderr)
        return 2
    for res, trace in zip(results, traces):
        res["variant"] = trace["variant"]

    # ---- per-arm decomposition -----------------------------------------
    by_arm = defaultdict(list)
    for res in results:
        by_arm[res["arm"]].append(res)

    print("== Phase B smoke -- HARNESS EXERCISE, NOT AN ARM COMPARISON ==\n")
    header = (f"{'arm':<12}{'gate':>6}{'critR':>7}{'auth':>6}{'V1':>5}"
              f"{'srch':>6}{'read':>6}{'rej':>5}{'ms':>7}")
    print(header)
    print("-" * len(header))
    summary = {}
    for arm in ARMS:
        rows = by_arm[arm]
        n = len(rows)
        summary[arm] = {
            "n": n,
            "full_hard_gate_rate": round(sum(r["full_hard_gate"] for r in rows) / n, 3),
            "critical_path_recall": round(
                sum(r["critical_path_recall"] for r in rows) / n, 3),
            "exact_authority_hit_rate": round(
                sum(r["exact_authority_hit"] for r in rows) / n, 3),
            "invalid_run_rate": round(sum(r["invalid_run"] for r in rows) / n, 3),
            "false_absence_rate": round(sum(r["false_absence"] for r in rows) / n, 3),
            # Both *_rate fields inside _safety_summary divide by total n --
            # kept for backward compatibility, but reproduced 2026-08-10
            # (independent review round 5, finding #1): if U1 rate differs
            # by arm, dividing every safety metric by the SAME total n
            # distorts cross-arm/cross-model comparison. Example: 10 cells,
            # 2 U1, 2 confirmed S1 -> safety_violation_rate reads 0.2, but
            # the confirmed-violation rate among the 8 auto-decidable cells
            # is 2/8 = 0.25. confirmed_safety_violation_rate is the one to
            # use for comparing models/arms.
            **_safety_summary(rows),
            "mean_search": round(sum(r["n_search"] for r in rows) / n, 2),
            "mean_read": round(sum(r["n_read"] for r in rows) / n, 2),
            "mean_guard_rejections": round(
                sum(r["guard_rejections"] for r in rows) / n, 2),
            "mean_wall_clock_ms": round(sum(r["wall_clock_ms"] for r in rows) / n, 1),
            "failure_codes": dict(Counter(
                c for r in rows for c in r["failure_codes"]).most_common()),
        }
        s = summary[arm]
        print(f"{arm:<12}{s['full_hard_gate_rate']:>6}{s['critical_path_recall']:>7}"
              f"{s['exact_authority_hit_rate']:>6}{s['invalid_run_rate']:>5}"
              f"{s['mean_search']:>6}{s['mean_read']:>6}"
              f"{s['mean_guard_rejections']:>5}{s['mean_wall_clock_ms']:>7}")

    print("\n-- failure code decomposition --")
    for arm in ARMS:
        print(f"  {arm:<12} {summary[arm]['failure_codes'] or '{}'}")

    print("\n-- per case (full_hard_gate) --")
    print(f"  {'case':<7}" + "".join(f"{a:>12}" for a in ARMS))
    for cid in cases:
        marks = []
        for arm in ARMS:
            row = next((r for r in by_arm[arm]
                        if r["case_id"] == cid and r.get("variant") == "variant-L"), None)
            marks.append("pass" if row and row["full_hard_gate"] else
                         (",".join(row["failure_codes"]) or "gate") if row else "-")
        print(f"  {cid:<7}" + "".join(f"{m:>12}" for m in marks))

    # ---- E0 re-check on real runs, not just the reference ---------------
    l_rows = {r["arm"]: r for r in results
              if r["case_id"] == "HD08" and r["variant"] == "variant-L"}
    m_rows = {r["arm"]: r for r in results
              if r["case_id"] == "HD08" and r["variant"] == "variant-M"}
    channel = {arm: {"L": l_rows[arm]["failure_codes"],
                     "M": m_rows[arm]["failure_codes"],
                     "same": l_rows[arm]["failure_codes"] == m_rows[arm]["failure_codes"]}
               for arm in ARMS if arm in l_rows and arm in m_rows}
    print("\n-- HD08 link vs mention (channel bias check on live runs) --")
    for arm, row in channel.items():
        print(f"  {arm:<12} L={row['L'] or 'clean'}  M={row['M'] or 'clean'}  "
              f"{'same' if row['same'] else 'DIFFERENT -> E0'}")

    # ---- incremental gain by action type --------------------------------
    gains = defaultdict(list)
    for res in results:
        for g in res["incremental_gains"]:
            gains[g["action"]].append(g["gain"])
    print("\n-- mean incremental recall gain by action (post-hoc, not causal) --")
    for action, values in sorted(gains.items(), key=lambda x: -sum(x[1]) / len(x[1])):
        print(f"  {action:<20} n={len(values):<4} mean={sum(values)/len(values):+.4f}")

    out = {
        "kind": "development-smoke",
        "claims_about_arms": "none -- controllers are scripted by the author of "
                             "the predictions; this measures the harness",
        "judge": "process-separated (subprocess -B -E -P -I -X pycache_prefix, "
                 "cache redirected); "
                 "NOT OS-level isolation",
        "judge_pins": pins,
        "calibration_frozen_surface_hashes": calibration["frozen_surface_hashes"],
        "n_runs": len(results),
        "per_arm": summary,
        "channel_check_HD08": channel,
        "mean_gain_by_action": {a: round(sum(v) / len(v), 4) for a, v in gains.items()},
        "results": results,
    }
    (HERE / "results" / "smoke.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / "results" / "smoke_traces.json").write_text(
        json.dumps(traces, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"\n{len(results)} runs written to results/smoke.json "
          f"(+ full traces in results/smoke_traces.json)")
    print("REMINDER: no arm effect may be read off these numbers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
