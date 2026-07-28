#!/usr/bin/env python3
"""Score the clean rerun cohort against the hidden oracle.  python3 _score.py

Reads trials.json (outputs) and oracle_manifest.json (expected). Kept out of the
execution path per OPERATIONS_PLAN.md principle 6: the runner establishes a
deterministic floor, the scorer compares against the oracle afterwards, and the
oracle is never on the path that builds a prompt.

Phase 6 scores agreement with the expected **contract_verdict**, not merely with
`decision`. The distinction is load-bearing: PROBLEM_2 §5.1 saw decision hold at
5/5 abstain while contract_verdict split 4-1, so a decision-only score would
have read as unanimous agreement over an unstable judgment.

Contract conformance is scored separately from correctness. A trial that reaches
the expected verdict through a rationale the contract forbids -- adjudicating
source liveness, naming a conflict without a symmetric counterpart -- is right
for the wrong reason, and the cohort should be able to say so.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
THRESHOLD = 0.90  # docs/experiment_screening_protocol.md; below this -> escalate

STRENGTH = {"none": 0, "weak": 1, "implicit": 2, "explicit": 3}


def conformance(out: dict) -> list[str]:
    """Mechanically checkable semantic_constraints. Returns violations."""
    v = []
    decision = out.get("decision")
    verdict = out.get("contract_verdict")
    audit = out.get("evidence_audit") or []
    scope = out.get("evidence_scope") or {}
    plan = out.get("repair_plan") or {}
    abstain = out.get("abstain") or {}

    pairs = {
        "repair": "sufficient_repairable",
        "accept_report": "sufficient_consistent",
    }
    if decision in pairs and verdict != pairs[decision]:
        v.append(f"decision={decision} requires contract_verdict={pairs[decision]}, got {verdict}")
    if decision == "abstain" and verdict not in {
        "insufficient_evidence", "conflicting_evidence", "out_of_scope"
    }:
        v.append(f"decision=abstain with contract_verdict={verdict}")

    if decision == "abstain":
        if plan.get("allowed") is not False:
            v.append("abstain requires repair_plan.allowed=false")
        if out.get("repaired_concepts") is not None:
            v.append("abstain requires repaired_concepts=null")
        if abstain.get("required") is not True:
            v.append("abstain requires abstain.required=true")
    if decision == "repair" and plan.get("allowed") is not True:
        v.append("repair requires repair_plan.allowed=true")

    if scope.get("outside_knowledge_used") is not False:
        v.append("outside_knowledge_used must be false")

    by_id = {a.get("evidence_id"): a for a in audit}
    for a in audit:
        eid = a.get("evidence_id")
        if a.get("admissibility") == "conflict":
            v.append(f"{eid}: 'conflict' was removed from the admissibility enum in v2")
        for other in a.get("conflicts_with_evidence_ids") or []:
            peer = by_id.get(other)
            if peer is None:
                v.append(f"{eid}: conflicts_with unknown evidence id {other}")
                continue
            if eid not in (peer.get("conflicts_with_evidence_ids") or []):
                v.append(f"{eid}<->{other}: conflict relation is not symmetric")
            if a.get("admissibility") != "direct_support" or peer.get("admissibility") != "direct_support":
                v.append(f"{eid}<->{other}: conflict named between non-direct_support items")

    # Step 1-5 of the adjudication procedure, recomputed from the audit the
    # trial itself produced. Disagreement means the trial's own audit does not
    # entail its own sufficiency judgment.
    cands = [a for a in audit if a.get("admissibility") == "direct_support"]
    best: dict[str, int] = {}
    for a in cands:
        t = a.get("supported_type")
        if t:
            best[t] = max(best.get(t, 0), STRENGTH.get(a.get("claim_strength", "none"), 0))
    if not cands:
        derived = "insufficient"
    else:
        top = max(best.values(), default=0)
        winners = [t for t, s in best.items() if s == top]
        derived = "sufficient" if len(winners) == 1 else "conflicting"

    for fj in out.get("feature_judgments") or []:
        got = fj.get("sufficiency")
        if got in {"sufficient", "insufficient", "conflicting"} and got != derived:
            v.append(
                f"{fj.get('concept')}.{fj.get('feature')}: sufficiency={got} but the "
                f"trial's own audit yields {derived} under the 5-step procedure"
            )
        if got == "conflicting" and fj.get("selected_type") is not None:
            v.append(f"{fj.get('concept')}.{fj.get('feature')}: conflicting requires selected_type=null")

    return v


def main() -> int:
    trials = json.loads((HERE / "trials.json").read_text(encoding="utf-8"))
    oracle = json.loads((HERE / "oracle_manifest.json").read_text(encoding="utf-8"))["fixtures"]

    cells: dict[str, list] = {}
    for t in trials["trials"]:
        cells.setdefault(t["parameters"]["fixture_id"], []).append(t)

    report, escalate = {}, []
    for fixture_id, rows in sorted(cells.items()):
        exp = oracle[fixture_id]
        hits, verdicts, decisions, viol = 0, Counter(), Counter(), {}
        for t in rows:
            out = t["output"]
            verdicts[out.get("contract_verdict")] += 1
            decisions[out.get("decision")] += 1
            if out.get("contract_verdict") == exp["expected_contract_verdict"]:
                hits += 1
            bad = conformance(out)
            if bad:
                viol[t["trial_id"]] = bad

        rate = hits / len(rows)
        clean = sum(1 for t in rows
                    if t["output"].get("contract_verdict") == exp["expected_contract_verdict"]
                    and not conformance(t["output"]))
        report[fixture_id] = {
            "n": len(rows),
            "expected_contract_verdict": exp["expected_contract_verdict"],
            "expected_decision": exp["expected_decision"],
            "verdict_hits": hits,
            "verdict_rate": round(rate, 3),
            "clean_hits": clean,
            "clean_rate": round(clean / len(rows), 3),
            "verdict_distribution": dict(verdicts),
            "decision_distribution": dict(decisions),
            "conformance_violations": viol,
        }
        # Certification uses clean_rate: the expected verdict reached without
        # breaking the contract that makes the verdict mean anything.
        if clean / len(rows) < THRESHOLD:
            escalate.append(fixture_id)

    certified = [f for f in report if f not in escalate]
    out = {
        "cohort_version": trials["cohort_version"],
        "threshold": THRESHOLD,
        "scored_on": "contract_verdict (OPERATIONS_PLAN.md Phase 6), gated on contract conformance",
        "per_fixture": report,
        "escalate_cells": escalate,
        "certified_classes": len(certified),
        "max_attainable_classes": 3,
        "excluded": trials.get("excluded", {}),
    }
    (HERE / "cohort_score.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    for fid, r in sorted(report.items()):
        mark = "ok  " if fid not in escalate else "ESC "
        print(f"  [{mark}] {fid}  clean {r['clean_hits']}/{r['n']} "
              f"({r['clean_rate']})  verdict {r['verdict_hits']}/{r['n']}  "
              f"expected={r['expected_contract_verdict']}")
        if r["verdict_distribution"]:
            print(f"          verdicts: {r['verdict_distribution']}")
        for tid, bad in r["conformance_violations"].items():
            for b in bad:
                print(f"          ! {tid}: {b}")
    print(f"\n  certified {len(certified)}/3 classes  -> cohort_score.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
