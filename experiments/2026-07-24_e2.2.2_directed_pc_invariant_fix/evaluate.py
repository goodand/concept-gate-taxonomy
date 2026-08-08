"""E2.2.2 scorer: single-arm control-affordance check for the directed PC,
round 2 (invariants, not just vocabulary).

NOT a B-C hypothesis test. Same pass/fail definition as E2.2 and E2.2.1
(classify_directed_repair, copied verbatim below) - only the prompt/schema
under test changed again.

Go/No-go: single criterion, pass_rate >= 0.80 (same threshold used in
E2.2/E2.2.1 for comparability).

Run (repo root or worktree):
    python3 experiments/2026-07-24_e2.2.2_directed_pc_invariant_fix/evaluate.py
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

from _cert_core import run_and_certify  # noqa: E402
from conceptgate.concept_gate_v7 import ParseGate  # noqa: E402

EXPERIMENT_ID = "E2.2.2"
PASS_THRESHOLD = 0.80


def _read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_fixtures():
    return {fx["id"]: fx for fx in _read_json(
        os.path.join(HERE, "fixture.json"))["fixtures"]}


# ── copied verbatim from E2.2 evaluate.py (commit 49f030b), via E2.2.1 ─────

def _parse_ok(concepts):
    parsed, report = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    return parsed if report.passed else None


def classify_directed_repair(concepts, original, part_feature):
    """Pass only if part_feature is exactly one structural_composition on every
    concept and the concept set is preserved (evidence-determined direction)."""
    parsed = _parse_ok(concepts)
    if parsed is None:
        return "invalid_repair"
    if {c.name for c in parsed} != {c["name"] for c in original}:
        return "destructive_repair"
    for concept in parsed:
        parts = [f for f in concept.features if f.feature == part_feature]
        if len(parts) != 1 or parts[0].type.value != "structural_composition":
            return "wrong_direction_repair"
    return "structural_composition_repair"

# ── end copied section ──────────────────────────────────────────────────────


def fixture_preconditions(fixtures):
    print("fixture preconditions")
    errors = []
    for fid, fx in fixtures.items():
        resp = run_and_certify(fx["input_concepts"])
        observed = {
            "status": resp["status"],
            "anti": len(resp["anti_patterns"]),
        }
        expected = {
            "status": fx["precondition"]["status"],
            "anti": fx["precondition"]["anti"],
        }
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
        "fixture": trial["fixture"], "trial": trial["trial"],
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
        repaired, fixture["input_concepts"], fixture["oracle"]["part_feature"])
    row["pass"] = row["repair_kind"] == "structural_composition_repair"
    return row


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
    n = len(rows)
    n_pass = sum(r["pass"] for r in rows)
    rate = n_pass / n if n else 0.0

    from collections import Counter
    breakdown = Counter(r["repair_kind"] for r in rows)

    print(f"\ndirected PC (dir1_directed), n={n}")
    print(f"  structural_composition_repair (PASS): {n_pass}/{n} = {rate:.3f}")
    print("  repair_kind breakdown:")
    for kind, count in sorted(breakdown.items(), key=lambda kv: -kv[1]):
        print(f"    {kind:<28} {count}")

    verdict = "GO" if rate >= PASS_THRESHOLD else "NO_GO"
    print(f"\nGo/No-go (control-affordance check only, threshold={PASS_THRESHOLD}): {verdict}")
    print(json.dumps({
        "experiment_id": EXPERIMENT_ID,
        "n": n, "pass": n_pass, "rate": rate,
        "threshold": PASS_THRESHOLD, "verdict": verdict,
        "note": "Single-arm affordance check. Does NOT test or reuse the "
                "E2.2 B-C main hypothesis.",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
