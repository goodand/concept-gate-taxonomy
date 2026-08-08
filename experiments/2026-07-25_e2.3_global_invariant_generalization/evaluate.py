"""E2.3 scorer: Global Feature-Type Invariant Generalization, 2-stage
adaptive screening (docs/experiment_screening_protocol.md).

Tests whether E2.2.3's finding -- a single prompt rule (global feature-type
consistency, "factor A") was independently sufficient (20/20) to recover
the directed-PC repair -- generalizes beyond the single fixture every prior
E2.2.x round used. Five arm-cells across three new fixtures: CONTROL/
A_ONLY/A_PARAPHRASE on baseline_directed, A_TOPOLOGY on topology_directed
(3 concepts, 2 independent shared-feature conflicts), A_DECOY on
decoy_directed (stronger local-evidence decoy than any prior round).

classify_directed_repair here is a GENERALIZATION of the E2.2/E2.2.1/
E2.2.2/E2.2.3 scorer, not a byte-identical copy: it accepts a LIST of
part_features (topology_directed has two, each spanning only a subset of
the fixture's concepts) instead of a single part_feature assumed present
on every concept. For a single-part-feature fixture (baseline_directed,
decoy_directed) it reduces to the same check the E2.2.x lineage used.

Screening protocol (docs/experiment_screening_protocol.md, restated by the
user for this experiment): N=10/arm-cell, threshold 0.90 for Stage 1.
9-10/10 -> screened PASS. <=6/10 -> screened FAIL (NO_GO), no escalation.
7-8/10 -> escalate to Stage 2 (increment +10 -> cumulative N=20,
threshold 0.80 like the rest of the E2.x lineage). Do not call any Stage-1
result "confirmed" -- use screened/screened out/provisional/candidate gate.

Run (repo root or worktree):
    python3 experiments/2026-07-25_e2.3_global_invariant_generalization/evaluate.py
"""

import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from _cert_core import run_and_certify  # noqa: E402
from conceptgate.concept_gate_v7 import ParseGate  # noqa: E402

EXPERIMENT_ID = "E2.3"
STAGE1_THRESHOLD = 0.90
STAGE1_FAIL_MAX = 0.60
STAGE2_THRESHOLD = 0.80
ARM_ORDER = ["CONTROL", "A_ONLY", "A_PARAPHRASE", "A_TOPOLOGY", "A_DECOY"]
ANCHORS = {
    "E2.2.3 A_ONLY (dir1_directed, N=20)": {"n": 20, "pass": 20, "rate": 1.00},
    "E2.2.3 B_ONLY (dir1_directed, N=20)": {"n": 20, "pass": 1, "rate": 0.05},
    "E2.2.3 C_ONLY (dir1_directed, N=20)": {"n": 20, "pass": 0, "rate": 0.00},
}


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_fixtures():
    return {fx["id"]: fx for fx in _read_json(
        os.path.join(HERE, "fixture.json"))["fixtures"]}


def _parse_ok(concepts):
    parsed, report = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    return parsed if report.passed else None


def classify_directed_repair(concepts, original, part_features):
    """Generalized from E2.2/E2.2.1/E2.2.2/E2.2.3's classify_directed_repair.

    Pass only if, for EVERY part_feature in part_features, every ORIGINAL
    concept that carried that feature has exactly one instance of it typed
    structural_composition in the repair, AND the concept-name set is
    preserved (evidence-determined direction, no dropped concepts)."""
    parsed = _parse_ok(concepts)
    if parsed is None:
        return "invalid_repair"
    if {c.name for c in parsed} != {c["name"] for c in original}:
        return "destructive_repair"
    by_name = {c.name: c for c in parsed}
    for part_feature in part_features:
        owners = [c["name"] for c in original
                  if any(f["feature"] == part_feature for f in c["features"])]
        for owner in owners:
            concept = by_name[owner]
            parts = [f for f in concept.features if f.feature == part_feature]
            if len(parts) != 1 or parts[0].type.value != "structural_composition":
                return "wrong_direction_repair"
    return "structural_composition_repair"


def fixture_preconditions(fixtures):
    print("fixture preconditions")
    errors = []
    for fid, fx in fixtures.items():
        resp = run_and_certify(fx["input_concepts"])
        observed = {"status": resp["status"], "anti": len(resp["anti_patterns"])}
        expected = {"status": fx["precondition"]["status"], "anti": fx["precondition"]["anti"]}
        ok = observed == expected
        print(f"  {fid:<20} {str(observed):<48}{'OK' if ok else 'FAIL'}")
        if not ok:
            errors.append(f"{fid}: expected {expected}, got {observed}")
    return errors


def validate_trial_set(data, fixtures, manifest):
    errors = []
    if data.get("record_class") != "empirical_trial_set":
        errors.append("record_class must be empirical_trial_set")
    protocol = data.get("protocol") or {}
    if protocol.get("experiment_id") != EXPERIMENT_ID:
        errors.append(f"protocol.experiment_id must be {EXPERIMENT_ID}")
    if protocol.get("design_commit") != (manifest.get("protocol") or {}).get("design_commit"):
        errors.append("trial and manifest design commits differ")

    expected_keys = {(p["fixture"], p["arm"], p["trial"]) for p in manifest["prompts"]}
    manifest_by_key = {(p["fixture"], p["arm"], p["trial"]): p for p in manifest["prompts"]}
    results = data.get("results")
    if not isinstance(results, list):
        return errors + ["results must be a list"]
    result_keys = {(r.get("fixture"), r.get("arm"), r.get("trial")) for r in results}
    if result_keys != expected_keys:
        errors.append(f"trial cells differ from manifest: "
                       f"missing={expected_keys - result_keys} extra={result_keys - expected_keys}")

    for r in results:
        key = (r.get("fixture"), r.get("arm"), r.get("trial"))
        prefix = "/".join(str(k) for k in key)
        item = manifest_by_key.get(key)
        if item and r.get("prompt_sha256") != item.get("prompt_sha256"):
            errors.append(f"{prefix}: prompt hash differs from manifest")
        ex = r.get("execution") or {}
        if ex.get("context_isolation") != "workflow_cold_subagent":
            errors.append(f"{prefix}: context_isolation must be workflow_cold_subagent")
        if ex.get("tool_access") != "schema_only":
            errors.append(f"{prefix}: tool_access must be schema_only")
        raw = r.get("raw_response")
        if not isinstance(raw, str) or not raw.strip():
            errors.append(f"{prefix}: raw_response required")
        else:
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{prefix}: raw_response invalid JSON ({exc})")
                parsed = None
            if parsed is not None and parsed != r.get("output"):
                errors.append(f"{prefix}: raw_response and output differ")
    return errors


def score_trial(trial, fixture):
    output = trial.get("output") if isinstance(trial.get("output"), dict) else {}
    decision = output.get("decision")
    row = {
        "fixture": trial["fixture"], "arm": trial["arm"], "trial": trial["trial"],
        "decision": decision, "repair_kind": "-", "pass": False,
    }
    if decision != "repair":
        row["repair_kind"] = f"non_repair:{decision}"
        return row
    repaired = output.get("repaired_concepts")
    if not repaired:
        row["repair_kind"] = "missing_repair"
        return row
    row["repair_kind"] = classify_directed_repair(
        repaired, fixture["input_concepts"], fixture["oracle"]["part_features"])
    row["pass"] = row["repair_kind"] == "structural_composition_repair"
    return row


def _stage_verdict(n, n_pass):
    rate = n_pass / n if n else 0.0
    if n >= 20:
        status = "candidate_gate_pass" if rate >= STAGE2_THRESHOLD else "candidate_gate_fail"
    elif rate >= STAGE1_THRESHOLD:
        status = "screened"
    elif rate <= STAGE1_FAIL_MAX:
        status = "screened_out"
    else:
        status = "provisional_escalate"
    return rate, status


def _report_arm(arm, rows):
    n = len(rows)
    n_pass = sum(r["pass"] for r in rows)
    rate, status = _stage_verdict(n, n_pass)
    breakdown = Counter(r["repair_kind"] for r in rows)
    print(f"\n  arm={arm} n={n}")
    print(f"    structural_composition_repair (PASS): {n_pass}/{n} = {rate:.3f}  [{status}]")
    print("    repair_kind breakdown:")
    for kind, count in sorted(breakdown.items(), key=lambda kv: -kv[1]):
        print(f"      {kind:<28} {count}")
    return {"n": n, "pass": n_pass, "rate": rate, "status": status, "breakdown": dict(breakdown)}


def main():
    fixtures = load_fixtures()
    precondition_errors = fixture_preconditions(fixtures)
    if precondition_errors:
        raise SystemExit("PRECONDITION_FAIL:\n- " + "\n- ".join(precondition_errors))

    trials_path = os.path.join(HERE, "trials.json")
    if not os.path.exists(trials_path):
        print("\nNO_TRIALS: run the workflow after freezing the manifest.")
        return
    manifest_path = os.path.join(HERE, "_prompts.json")
    if not os.path.exists(manifest_path):
        raise SystemExit("PROVENANCE_FAIL: _prompts.json required for validation")
    data = _read_json(trials_path)
    manifest = _read_json(manifest_path)

    provenance_errors = validate_trial_set(data, fixtures, manifest)
    if provenance_errors:
        raise SystemExit("PROVENANCE_FAIL:\n- " + "\n- ".join(provenance_errors))
    print("\nEMPIRICAL_TRIAL_SET: provenance contract satisfied")

    rows = [score_trial(t, fixtures[t["fixture"]]) for t in data["results"]]
    by_arm = defaultdict(list)
    for r in rows:
        by_arm[r["arm"]].append(r)

    print(f"\nE2.3 global-invariant generalization, n={len(rows)} total")
    summary = {}
    for arm in ARM_ORDER:
        if arm in by_arm:
            summary[arm] = _report_arm(arm, by_arm[arm])

    print("\ncomparison against E2.2.3 anchors (different fixture, dir1_directed):")
    for label, anchor in ANCHORS.items():
        print(f"  {label:<38} {anchor['pass']}/{anchor['n']} = {anchor['rate']:.3f}")
    for arm, s in summary.items():
        print(f"  E2.3 {arm:<33} {s['pass']}/{s['n']} = {s['rate']:.3f}  {s['status']}")

    escalate = [arm for arm, s in summary.items() if s["status"] == "provisional_escalate"]
    print("\nScreening verdicts are NOT 'confirmed' -- see docs/experiment_screening_protocol.md.")
    if escalate:
        print(f"Arms requiring Stage 2 escalation (+10 trials each): {escalate}")
    else:
        print("No arms in the 7-8/10 ambiguous band -- no Stage 2 escalation needed.")

    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "stage1_threshold": STAGE1_THRESHOLD,
        "stage1_fail_max": STAGE1_FAIL_MAX,
        "stage2_threshold": STAGE2_THRESHOLD,
        "arms": summary,
        "escalate_to_stage2": escalate,
        "anchors": ANCHORS,
        "note": "2-stage adaptive screening (docs/experiment_screening_protocol.md). "
                "n=10 status values (screened/screened_out/provisional_escalate) are "
                "not confirmatory. n=20 status values (candidate_gate_pass/fail) are "
                "the only ones eligible for 'candidate gate' language.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
