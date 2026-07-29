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

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

_spec = importlib.util.spec_from_file_location("e24_cohort_score", HERE / "_cohort.py")
cohort = importlib.util.module_from_spec(_spec)
sys.modules["e24_cohort_score"] = cohort
_spec.loader.exec_module(cohort)

_rspec = importlib.util.spec_from_file_location("e24_review11_score", HERE / "_review_11.py")
review11 = importlib.util.module_from_spec(_rspec)
sys.modules["e24_review11_score"] = review11
_rspec.loader.exec_module(review11)

# experiment_screening_protocol.md Stage 1 (lives in the main checkout at
# ../../../concept-gate-taxonomy/docs/, not in this worktree).
THRESHOLD = 0.90
PROTOCOL_N = 10

STRENGTH = {"none": 0, "weak": 1, "implicit": 2, "explicit": 3}


def conformance(out: dict, payload: dict) -> list[str]:
    """Mechanically checkable semantic_constraints. Returns violations.

    `payload` is the model payload the trial saw (build_model_payload output).
    It is required rather than optional: constraints 4 and 6 need it, and an
    optional argument that silently disables checks is how a scorer starts
    reporting "clean" for things it never looked at.
    """
    v = []
    payload_evidence = {e["evidence_id"] for e in payload.get("evidence_items", [])}
    candidates = payload.get("candidate_concepts", [])
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

    for a in audit:
        if a.get("admissibility") == "direct_support" and not a.get("supported_type"):
            v.append(f"{a.get('evidence_id')}: direct_support with no supported_type")

    # Constraint 6 -- every cited id must exist in the payload the model saw.
    cited = set(scope.get("used_evidence_ids") or [])
    cited |= {a.get("evidence_id") for a in audit}
    for a in audit:
        cited |= set(a.get("conflicts_with_evidence_ids") or [])
    for fj in out.get("feature_judgments") or []:
        cited |= set(fj.get("evidence_ids") or [])
    for ic in out.get("invariant_checks") or []:
        cited |= set(ic.get("evidence_ids") or [])
    for st in plan.get("steps") or []:
        cited |= set(st.get("evidence_ids") or [])
    for eid in sorted(x for x in cited - payload_evidence if x is not None):
        v.append(f"cited evidence id {eid!r} is not in the payload")

    # Constraint 4 -- a repair must carry the whole input forward.
    if decision == "repair":
        repaired = {c.get("name"): {f.get("feature") for f in c.get("features") or []}
                    for c in out.get("repaired_concepts") or []}
        for c in candidates:
            if c["name"] not in repaired:
                v.append(f"repair dropped concept {c['name']!r} from repaired_concepts")
                continue
            for f in c["features"]:
                if f["feature"] not in repaired[c["name"]]:
                    v.append(f"repair dropped feature {c['name']}.{f['feature']}")

    # Steps 1-5, recomputed per feature from the audit entries that feature
    # actually cites. Deriving once over the whole audit would be wrong: rule 5
    # tells a trial to mark an unrelated filler feature insufficient even while
    # the repaired feature is sufficient, so a packet-global derivation reports
    # the contract-following answer as a violation.
    def derive(evidence_ids):
        cands = [by_id[e] for e in evidence_ids
                 if by_id.get(e, {}).get("admissibility") == "direct_support"]
        best: dict[str, int] = {}
        for a in cands:
            t = a.get("supported_type")
            if t:
                best[t] = max(best.get(t, 0),
                              STRENGTH.get(a.get("claim_strength", "none"), 0))
        if not best:
            return "insufficient", None
        top = max(best.values())
        winners = [t for t, s in best.items() if s == top]
        return ("sufficient", winners[0]) if len(winners) == 1 else ("conflicting", None)

    for fj in out.get("feature_judgments") or []:
        where = f"{fj.get('concept')}.{fj.get('feature')}"
        got = fj.get("sufficiency")
        derived, winner = derive(fj.get("evidence_ids") or [])
        if got in {"sufficient", "insufficient", "conflicting"} and got != derived:
            v.append(
                f"{where}: sufficiency={got} but the evidence it cites yields "
                f"{derived} under the 5-step procedure"
            )
        if got == "conflicting" and fj.get("selected_type") is not None:
            v.append(f"{where}: conflicting requires selected_type=null")
        if got == "sufficient" and derived == "sufficient" \
                and fj.get("selected_type") != winner:
            v.append(
                f"{where}: selected_type={fj.get('selected_type')} but step 3 "
                f"yields {winner} from the cited evidence"
            )

    return v


def band(rate: float) -> str:
    """The pre-registered Stage 1 verdict bands.

    ../../../concept-gate-taxonomy/docs/experiment_screening_protocol.md:
    0.90-1.00 screened PASS, 0.70-0.80 ambiguous (auto-promote to Stage 2),
    0.00-0.60 screened FAIL. Reported as three bands rather than a pass/fail
    threshold because the middle band is not a failure -- it is an instruction
    to run a Stage 2 increment on that cell.
    """
    if rate >= 0.90:
        return "screened_PASS"
    if rate >= 0.70:
        return "ambiguous"
    return "screened_FAIL"


def payload_for(fixture_id: str) -> dict:
    fixture = json.loads(
        (HERE / cohort.FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8")
    )
    manifest = cohort.surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
    return cohort.surface.build_model_payload(fixture, manifest)


def main() -> int:
    trials = json.loads((HERE / "trials.json").read_text(encoding="utf-8"))
    oracle = json.loads((HERE / "oracle_manifest.json").read_text(encoding="utf-8"))["fixtures"]

    cells: dict[str, list] = {}
    for t in trials["trials"]:
        cells.setdefault(t["parameters"]["fixture_id"], []).append(t)

    # Constraint #11 is the one semantic_constraint no checker can cover: it
    # needs a rationale read. A trial with no review result is UNKNOWN, and the
    # 2026-07-29 directive §3 requires UNKNOWN to block rather than pass, so an
    # absent verdict is not a pass here. See DESIGN_D4_constraint_11_review.md.
    reviews = review11.review_verdicts()
    calibration = review11.calibration_status()

    report, escalate = {}, []
    for fixture_id, rows in sorted(cells.items()):
        exp = oracle[fixture_id]
        payload = payload_for(fixture_id)
        verdicts, decisions, viol, malformed = Counter(), Counter(), {}, {}
        review_counts = Counter()
        hits = decision_hits = clean = pre_review_clean = 0

        for t in rows:
            out = t["output"]
            verdicts[out.get("contract_verdict")] += 1
            decisions[out.get("decision")] += 1
            verdict_ok = out.get("contract_verdict") == exp["expected_contract_verdict"]
            hits += verdict_ok
            decision_hits += out.get("decision") == exp["expected_decision"]

            bad = conformance(out, payload)
            if bad:
                viol[t["trial_id"]] = bad
            # record() computed these against the frozen schema; a structurally
            # invalid output must not count toward certification just because
            # its contract_verdict string happened to match.
            broke_schema = t.get("schema_violations") or []
            if broke_schema:
                malformed[t["trial_id"]] = broke_schema

            review = reviews.get(t["trial_id"], "unknown")
            review_counts[review] += 1

            mechanical_ok = verdict_ok and not bad and not broke_schema
            # Kept separate so the drop caused by an unrun review is legible as
            # "not yet verified" rather than looking like a scoring regression.
            pre_review_clean += mechanical_ok
            if mechanical_ok and review == "ok":
                clean += 1

        n = len(rows)
        report[fixture_id] = {
            "n": n,
            "expected_contract_verdict": exp["expected_contract_verdict"],
            "expected_decision": exp["expected_decision"],
            "verdict_hits": hits,
            "verdict_rate": round(hits / n, 3),
            "decision_hits": decision_hits,
            "clean_hits": clean,
            "clean_rate": round(clean / n, 3),
            "band": band(clean / n),
            "pre_review_clean_hits": pre_review_clean,
            "constraint_11_review": dict(review_counts),
            "verdict_distribution": dict(verdicts),
            "decision_distribution": dict(decisions),
            "conformance_violations": viol,
            "schema_violations": malformed,
        }
        # Certification uses clean_rate: the expected verdict reached without
        # breaking either the output schema or the contract that makes the
        # verdict mean anything.
        if clean / n < THRESHOLD:
            escalate.append(fixture_id)

    certified = [f for f in report if f not in escalate]
    off_protocol = sorted(f for f, r in report.items() if r["n"] != PROTOCOL_N)
    out = {
        "cohort_version": trials["cohort_version"],
        "threshold": THRESHOLD,
        "scored_on": "contract_verdict (OPERATIONS_PLAN.md Phase 6), gated on "
                     "output-schema validity, contract conformance, and the "
                     "constraint #11 rationale review",
        "constraint_11_review": {
            "state": review11.stage_status(reviews, trials["trials"])["stage"],
            "calibration": calibration,
            "reviewed": len(reviews),
            "of": sum(len(rows) for rows in cells.values()),
            "note": "#11 cannot be checked mechanically (it requires reading a "
                    "rationale), so it is scored by an independent reviewer. A "
                    "trial with no review result counts as UNKNOWN and is "
                    "excluded from clean_hits per directive §3 -- absence of a "
                    "verification result blocks rather than passes.",
        },
        "per_fixture": report,
        "escalate_cells": escalate,
        "certified_classes": len(certified),
        "max_attainable_classes": 3,
        "excluded": trials.get("excluded", {}),
    }
    if calibration["state"] != "passed":
        out["certification_blocked"] = {
            "reason": "constraint_11_reviewer_uncalibrated",
            "detail": "The reviewer's recall and precision have not been measured "
                      "against review_11_calibration.json. An unmeasured checker "
                      "must not be cited as safety grounds "
                      "(checker-recall-and-precision-at2026-07-28-19-04.md).",
            "certified_classes_are_not_claimable": True,
        }
    if off_protocol:
        out["protocol_deviation"] = {
            "cells": {f: report[f]["n"] for f in off_protocol},
            "expected_n_per_cell": PROTOCOL_N,
            "note": "experiment_screening_protocol.md Stage 1 is N=10/cell. This "
                    "cohort's N came from DESIGN_DECISION §8, which specified 17 "
                    "trials to mirror the legacy counts. The band labels above are "
                    "computed from rates, but the protocol's bands were calibrated "
                    "for N=10 -- at N=5 the ambiguous band is a single trial wide, "
                    "and at N=7 the rate 6/7=0.857 falls in a gap the table does "
                    "not name. Read the bands accordingly.",
        }
    (HERE / "cohort_score.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    if calibration["state"] != "passed":
        print(f"  [BLOCKED] constraint #11 reviewer is uncalibrated "
              f"({calibration['state']}); certified_classes below is not claimable\n")

    for fid, r in sorted(report.items()):
        mark = "ok  " if fid not in escalate else "ESC "
        print(f"  [{mark}] {fid}  clean {r['clean_hits']}/{r['n']} "
              f"({r['clean_rate']}, {r['band']})  verdict {r['verdict_hits']}/{r['n']}  "
              f"expected={r['expected_contract_verdict']}")
        print(f"          #11 review: {dict(r['constraint_11_review'])}  "
              f"(pre-review clean was {r['pre_review_clean_hits']}/{r['n']})")
        if r["verdict_distribution"]:
            print(f"          verdicts: {r['verdict_distribution']}")
        for tid, bad in r["schema_violations"].items():
            for b in bad[:3]:
                print(f"          X {tid}: schema: {b}")
        for tid, bad in r["conformance_violations"].items():
            for b in bad:
                print(f"          ! {tid}: {b}")
    if off_protocol:
        print(f"\n  protocol deviation: cells {off_protocol} are not N={PROTOCOL_N} "
              f"(experiment_screening_protocol.md Stage 1)")
    print(f"\n  certified {len(certified)}/3 classes  -> cohort_score.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
