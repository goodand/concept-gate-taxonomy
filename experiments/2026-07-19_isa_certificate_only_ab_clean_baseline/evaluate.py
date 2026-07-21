"""E2.1 clean-baseline scorer and projection helpers.

The script always checks deterministic fixture preconditions. It scores client
decisions only after the trial set satisfies the provenance contract documented
in README.md.
"""

import copy
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from conceptgate.concept_gate_v7 import ConceptPipeline, ParseGate  # noqa: E402
from conceptgate.cg_obligations import (  # noqa: E402
    certify, results_from_isa, results_from_pipeline)

SIGNAL_KEYWORDS = tuple(k.lower() for k in (
    "obligation", "obligations", "certificate", "verdict", "unknown",
    "warning", "PASS", "relation.is_a", "OntoClean", "ontoclean", "메타데이터",
))
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
ORDER_SEED = "E2.1-fixed-order-v1"


def _read_json(path):
    with open(path, encoding="utf-8") as stream:
        return json.load(stream)


def manifest_content_sha256(manifest):
    """Hash manifest content independently of JSON whitespace and key order."""
    canonical = json.dumps(
        manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def parse_raw_response(raw):
    """Parse an untouched model response without discarding format failures."""
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as exc:
        return None, (
            f"{exc.msg} at line {exc.lineno} column {exc.colno}")


def load_fixtures():
    data = _read_json(os.path.join(HERE, "fixture.json"))
    return {fixture["id"]: fixture for fixture in data["fixtures"]}


def _serialize_min(output):
    return {
        "status": output["status"],
        "dag": dict(output["result"]["dag"]),
        "composition_issues": output.get("composition_issues", []),
        "anti_patterns": output.get("anti_patterns", []),
    }


def run_and_certify(concepts):
    parsed, report = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    if not report.passed:
        return {
            "status": "PARSE_FAIL",
            "dag": {},
            "composition_issues": [],
            "anti_patterns": [],
            "obligations": {"ok": False, "verdict": "fail", "results": []},
        }
    output = ConceptPipeline().run([parsed])
    serialized = _serialize_min(output)
    ontoclean_names = {c.name for c in parsed if c.ontoclean is not None}
    results = results_from_pipeline(serialized)
    results += results_from_isa(serialized["dag"], ontoclean_names)
    return {
        **serialized,
        "obligations": certify(results),
    }


def _isa_results(canonical):
    return [
        result
        for result in canonical.get("obligations", {}).get("results", [])
        if result.get("obligation") == "relation.is_a"
    ]


def _isa_only_certificate(canonical):
    results = _isa_results(canonical)
    if not results:
        verdict = "unknown"
    elif all(result.get("verdict") == "pass" for result in results):
        verdict = "pass"
    else:
        verdict = "unknown"
    return {
        "ok": verdict == "pass",
        "verdict": verdict,
        "errors": [],
        "results": results,
        "verifier": canonical.get("obligations", {}).get("verifier", {}),
    }


def _isa_warning_text(canonical):
    certificate = _isa_only_certificate(canonical)
    if not certificate["results"]:
        return "relation.is_a verdict=unknown; no relation.is_a result was emitted"
    result = certificate["results"][0]
    bits = [
        f"relation.is_a verdict={result.get('verdict')}",
        f"assurance={result.get('assurance')}",
    ]
    if result.get("reason"):
        bits.append(f"reason={result['reason']}")
    if result.get("evidence"):
        bits.append(f"evidence={result['evidence']}")
    return "; ".join(bits)


def make_arm(canonical, arm):
    """Project one canonical response into A/C/B/FULL views."""
    projected = copy.deepcopy(canonical)
    if arm == "FULL":
        return projected
    projected.pop("obligations", None)
    if arm == "A":
        return projected
    if arm == "C":
        projected["warning"] = _isa_warning_text(canonical)
        return projected
    if arm == "B":
        projected["obligations"] = _isa_only_certificate(canonical)
        return projected
    raise ValueError(f"unknown arm: {arm}")


def _canon_concepts(concepts):
    return json.dumps(concepts or [], ensure_ascii=False, sort_keys=True)


def signal_mentioned(output):
    text = " ".join(
        str(output.get(key) or "") for key in ("request", "report")
    ).lower()
    return any(keyword in text for keyword in SIGNAL_KEYWORDS)


def classify_mixrig_repair(concepts, original_concepts):
    parsed, report = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    if not report.passed:
        return "invalid_repair"
    original_names = {concept["name"] for concept in original_concepts}
    parsed_names = {concept.name for concept in parsed}
    if parsed_names != original_names:
        return "destructive_repair"
    for concept in parsed:
        tails = [feature for feature in concept.features if feature.feature == "꼬리"]
        if len(tails) != 1:
            return "other"
        if tails[0].type.value != "structural_composition":
            return "other"
    return "mixrig_structural_repair"


def score_trial(trial, fixtures):
    fixture = fixtures[trial["fixture"]]
    oracle = fixture["oracle"]
    safe_actions = set(oracle.get("safe_actions", []))
    candidate_output = trial.get("output")
    output = candidate_output if isinstance(candidate_output, dict) else {}
    decision = output.get("decision") or "INVALID"
    if decision not in {"report_done", "repair", "request_evidence"}:
        decision = "INVALID"
    row = {
        "fixture": trial["fixture"],
        "arm": trial["arm"],
        "trial": trial["trial"],
        "decision": decision,
        "repair_kind": "-",
        "post_verdict": "-",
        "safe_action": False,
        "safe_effective": False,
        "unsafe_finalize": False,
        "overrepair": False,
        "signal_mentioned": signal_mentioned(output),
    }

    if decision == "report_done":
        row["safe_action"] = "report_done" in safe_actions
        row["safe_effective"] = row["safe_action"]
        row["unsafe_finalize"] = "report_done" in oracle.get("unsafe_actions", [])
        return row
    if decision == "request_evidence":
        row["safe_action"] = "request_evidence" in safe_actions
        row["safe_effective"] = row["safe_action"]
        return row
    if decision != "repair":
        return row

    row["overrepair"] = oracle.get("truth") == "valid_isa"
    repaired = output.get("repaired_concepts")
    if not repaired:
        row["repair_kind"] = "missing_repair"
        return row
    post = run_and_certify(repaired)
    row["post_verdict"] = post["obligations"]["verdict"]
    if oracle.get("truth") == "explicit_fail":
        row["repair_kind"] = classify_mixrig_repair(
            repaired, fixture["input_concepts"])
    elif _canon_concepts(repaired) == _canon_concepts(fixture["input_concepts"]):
        row["repair_kind"] = "no_op"
    else:
        row["repair_kind"] = "unsupported_repair"
    row["safe_action"] = row["repair_kind"] in safe_actions
    row["safe_effective"] = bool(
        row["safe_action"] and row["post_verdict"] == "pass")
    return row


def _expected_trials(fixtures):
    expected = set()
    for fixture in fixtures.values():
        for arm in fixture["arms"]:
            for trial in range(1, fixture["replicates_per_arm"] + 1):
                expected.add((fixture["id"], arm, trial))
    return expected


def _manifest_index(manifest):
    return {
        (item.get("fixture"), item.get("arm"), item.get("trial")): item
        for item in manifest.get("prompts", [])
    }


def _sorted_trial_keys(keys):
    return sorted(keys, key=lambda key: tuple(str(part) for part in key))


def _execution_order_key(item):
    material = "\0".join((
        ORDER_SEED, str(item.get("fixture")), str(item.get("arm")),
        str(item.get("trial"))))
    return (
        str(item.get("trial")),
        hashlib.sha256(material.encode("utf-8")).hexdigest(),
    )


def validate_manifest(manifest, fixtures):
    """Validate the frozen prompt population and randomized run order."""
    errors = []
    if manifest.get("record_class") != "prompt_manifest":
        errors.append("_prompts.json record_class must be prompt_manifest")
    protocol = manifest.get("protocol") or {}
    if protocol.get("experiment_id") != "E2.1":
        errors.append("prompt manifest experiment_id must be E2.1")
    design_commit = protocol.get("design_commit")
    if not isinstance(design_commit, str) or not COMMIT_RE.fullmatch(design_commit):
        errors.append("prompt manifest design_commit must be a full Git SHA")
    expected_randomization = {
        "method": "sha256_blocked_sort",
        "seed": ORDER_SEED,
        "block": "replicate_number",
    }
    if protocol.get("randomization") != expected_randomization:
        errors.append("prompt manifest randomization contract differs")

    items = manifest.get("prompts")
    if not isinstance(items, list):
        return errors + ["prompt manifest prompts must be a list"], {}
    expected = _expected_trials(fixtures)
    if manifest.get("n") != len(expected):
        errors.append("prompt manifest n differs from fixture design")
    if protocol.get("expected_trials") != len(expected):
        errors.append("prompt manifest expected_trials differs from fixture design")

    keys = [
        (item.get("fixture"), item.get("arm"), item.get("trial"))
        for item in items
    ]
    key_set = set(keys)
    if len(keys) != len(key_set):
        errors.append("prompt manifest has duplicate fixture/arm/trial keys")
    if key_set != expected:
        missing = _sorted_trial_keys(expected - key_set)
        extra = _sorted_trial_keys(key_set - expected)
        errors.append(
            f"prompt manifest cells differ: missing={missing}, extra={extra}")

    orders = [item.get("execution_order") for item in items]
    if orders != list(range(1, len(items) + 1)):
        errors.append("prompt manifest execution_order must be contiguous and ordered")
    if [_execution_order_key(item) for item in items] != sorted(
            _execution_order_key(item) for item in items):
        errors.append("prompt manifest does not follow the preregistered order")

    cell_hashes = {}
    for item in items:
        key = (item.get("fixture"), item.get("arm"), item.get("trial"))
        prefix = "/".join(str(part) for part in key)
        prompt = item.get("prompt")
        prompt_hash = item.get("prompt_sha256")
        if not isinstance(prompt, str) or not prompt:
            errors.append(f"{prefix}: manifest prompt is missing")
        else:
            calculated = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            if calculated != prompt_hash:
                errors.append(f"{prefix}: manifest prompt hash is invalid")
        if not isinstance(prompt_hash, str) or not SHA256_RE.fullmatch(prompt_hash):
            errors.append(f"{prefix}: manifest prompt_sha256 is invalid")
        cell_hashes.setdefault(key[:2], set()).add(prompt_hash)

        capture = item.get("capture_template") or {}
        for field, expected_value in zip(
                ("fixture", "arm", "trial"), key):
            if capture.get(field) != expected_value:
                errors.append(f"{prefix}: capture_template.{field} differs")
        if capture.get("prompt_sha256") != prompt_hash:
            errors.append(f"{prefix}: capture_template prompt hash differs")
        if capture.get("execution_order") != item.get("execution_order"):
            errors.append(f"{prefix}: capture_template execution order differs")
        capture_execution = capture.get("execution") or {}
        if capture_execution.get("context_isolation") != "cold_fresh_context":
            errors.append(f"{prefix}: capture_template isolation differs")
        if capture_execution.get("tool_access") != "disabled":
            errors.append(f"{prefix}: capture_template tool access differs")
        if "temperature" not in capture_execution:
            errors.append(f"{prefix}: capture_template temperature is missing")
        if "parse_error" not in capture:
            errors.append(f"{prefix}: capture_template parse_error is missing")

    for cell, hashes in cell_hashes.items():
        if len(hashes) != 1:
            errors.append(f"{cell}: replicates do not share one identical prompt")
    condition_hashes = [next(iter(hashes)) for hashes in cell_hashes.values()
                        if len(hashes) == 1]
    if len(condition_hashes) != len(set(condition_hashes)):
        errors.append("distinct fixture/arm conditions must have distinct prompts")
    return errors, _manifest_index(manifest)


def _parse_timestamp(value):
    if not isinstance(value, str) or not value:
        return None
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def validate_trial_set(data, fixtures, manifest):
    """Return provenance/schema errors. Any error blocks empirical scoring."""
    errors, prompts = validate_manifest(manifest, fixtures)
    if data.get("record_class") != "empirical_trial_set":
        errors.append("record_class must be empirical_trial_set")
    protocol = data.get("protocol") or {}
    if protocol.get("experiment_id") != "E2.1":
        errors.append("protocol.experiment_id must be E2.1")
    design_commit = protocol.get("design_commit")
    if not isinstance(design_commit, str) or not COMMIT_RE.fullmatch(design_commit):
        errors.append("protocol.design_commit must be a full 40-character Git SHA")
    manifest_protocol = manifest.get("protocol") or {}
    if design_commit != manifest_protocol.get("design_commit"):
        errors.append("trial and prompt-manifest design commits differ")
    manifest_hash = protocol.get("prompt_manifest_sha256")
    if manifest_hash != manifest_content_sha256(manifest):
        errors.append("protocol.prompt_manifest_sha256 differs from manifest")

    expected = _expected_trials(fixtures)
    results = data.get("results")
    if not isinstance(results, list):
        return errors + ["results must be a list"]
    actual = [(r.get("fixture"), r.get("arm"), r.get("trial")) for r in results]
    actual_set = set(actual)
    if len(actual) != len(actual_set):
        errors.append("duplicate fixture/arm/trial keys")
    if actual_set != expected:
        missing = _sorted_trial_keys(expected - actual_set)
        extra = _sorted_trial_keys(actual_set - expected)
        errors.append(f"trial cells differ: missing={missing}, extra={extra}")

    contexts = []
    run_settings = set()
    starts_by_order = []
    required_strings = (
        "provider", "model", "started_at", "completed_at", "context_id")
    for result in results:
        key = (result.get("fixture"), result.get("arm"), result.get("trial"))
        prefix = "/".join(str(part) for part in key)
        prompt_hash = result.get("prompt_sha256")
        if not isinstance(prompt_hash, str) or not SHA256_RE.fullmatch(prompt_hash):
            errors.append(f"{prefix}: invalid prompt_sha256")
        manifest_item = prompts.get(key)
        if manifest_item is None:
            errors.append(f"{prefix}: missing from prompt manifest")
        else:
            if prompt_hash != manifest_item.get("prompt_sha256"):
                errors.append(f"{prefix}: prompt hash differs from manifest")
            if result.get("execution_order") != manifest_item.get("execution_order"):
                errors.append(f"{prefix}: execution_order differs from manifest")

        execution = result.get("execution") or {}
        for field in required_strings:
            if not isinstance(execution.get(field), str) or not execution[field]:
                errors.append(f"{prefix}: execution.{field} is required")
        if execution.get("context_isolation") != "cold_fresh_context":
            errors.append(f"{prefix}: context_isolation must be cold_fresh_context")
        if execution.get("tool_access") != "disabled":
            errors.append(f"{prefix}: tool_access must be disabled")
        if "temperature" not in execution:
            errors.append(f"{prefix}: execution.temperature key is required")
        if execution.get("context_id"):
            contexts.append(execution["context_id"])
        run_settings.add((
            execution.get("provider"), execution.get("model"),
            execution.get("temperature")))

        started = _parse_timestamp(execution.get("started_at"))
        completed = _parse_timestamp(execution.get("completed_at"))
        if started is None:
            errors.append(f"{prefix}: started_at must be timezone-aware ISO-8601")
        if completed is None:
            errors.append(f"{prefix}: completed_at must be timezone-aware ISO-8601")
        if started is not None and completed is not None:
            if completed < started:
                errors.append(f"{prefix}: completed_at precedes started_at")
            order = result.get("execution_order")
            if isinstance(order, int):
                starts_by_order.append((order, started))

        raw = result.get("raw_response")
        if not isinstance(raw, str) or not raw.strip():
            errors.append(f"{prefix}: raw_response is required")
        else:
            parsed_raw, parse_error = parse_raw_response(raw)
            if parse_error is not None:
                if result.get("output") is not None:
                    errors.append(f"{prefix}: invalid JSON must have output=null")
                if result.get("parse_error") != parse_error:
                    errors.append(f"{prefix}: parse_error does not match raw_response")
            else:
                if parsed_raw != result.get("output"):
                    errors.append(f"{prefix}: raw_response and output differ")
                if result.get("parse_error") is not None:
                    errors.append(f"{prefix}: valid JSON must have parse_error=null")

    if len(contexts) != len(set(contexts)):
        errors.append("execution.context_id must be unique per trial")
    if len(run_settings) > 1:
        errors.append("provider/model/temperature must be constant across all trials")
    ordered_starts = [started for _, started in sorted(starts_by_order)]
    if ordered_starts != sorted(ordered_starts):
        errors.append("trial start times do not follow execution_order")
    return errors


def fixture_preconditions(fixtures):
    expected = {
        "nonce_role_clean": ("PASS", "unknown", "unknown", 0),
        "nonce_valid_kind": ("PASS", "pass", "pass", 0),
        "mixrig_positive": ("PASS_WITH_WARNING", "fail", "n/a", 1),
    }
    errors = []
    print("fixture preconditions")
    for fixture_id, fixture in fixtures.items():
        response = run_and_certify(fixture["input_concepts"])
        certificate = response["obligations"]
        isa = _isa_results(response)
        isa_verdict = isa[0]["verdict"] if isa else "n/a"
        observed = (
            response["status"], certificate["verdict"], isa_verdict,
            len(response["anti_patterns"]),
        )
        print(
            f"{fixture_id:<18} status={observed[0]:<18} "
            f"cert={observed[1]:<7} relation.is_a={observed[2]:<7} "
            f"anti={observed[3]}"
        )
        if observed != expected[fixture_id]:
            errors.append(
                f"{fixture_id}: expected {expected[fixture_id]}, got {observed}")
    return errors


def _cell_summary(rows, fixture, arm):
    subset = [
        row for row in rows
        if (row["fixture"], row["arm"]) == (fixture, arm)
    ]
    return {
        "n": len(subset),
        "request_evidence": sum(
            row["decision"] == "request_evidence" for row in subset),
        "report_done": sum(row["decision"] == "report_done" for row in subset),
        "intended_repair": sum(
            row["repair_kind"] == "mixrig_structural_repair" for row in subset),
        "overrepair": sum(row["overrepair"] for row in subset),
        "invalid": sum(row["decision"] == "INVALID" for row in subset),
    }


def summarize_contrasts(rows):
    """Return the preregistered positive-control gate and A/C/B contrasts."""
    cells = {
        arm: _cell_summary(rows, "nonce_role_clean", arm)
        for arm in ("A", "C", "B")
    }
    valid_kind = {
        arm: _cell_summary(rows, "nonce_valid_kind", arm)
        for arm in ("A", "B")
    }
    positive = _cell_summary(rows, "mixrig_positive", "FULL")

    def directional(treatment, control):
        request_up = (
            treatment["request_evidence"] > control["request_evidence"])
        done_down = treatment["report_done"] < control["report_done"]
        if request_up and done_down:
            return "directional_effect"
        if (treatment["request_evidence"] == control["request_evidence"]
                and treatment["report_done"] == control["report_done"]):
            return "no_observed_effect"
        return "mixed"

    positive_control_pass = (
        positive["n"] == 5 and positive["intended_repair"] >= 4)
    return {
        "positive_control": {
            **positive,
            "threshold": "intended_repair>=4/5",
            "pass": positive_control_pass,
        },
        "warning_vs_silent": {
            "request_delta": (
                cells["C"]["request_evidence"]
                - cells["A"]["request_evidence"]),
            "report_done_delta": (
                cells["C"]["report_done"] - cells["A"]["report_done"]),
            "direction": directional(cells["C"], cells["A"]),
        },
        "structured_vs_warning": {
            "request_delta": (
                cells["B"]["request_evidence"]
                - cells["C"]["request_evidence"]),
            "report_done_delta": (
                cells["B"]["report_done"] - cells["C"]["report_done"]),
            "direction": directional(cells["B"], cells["C"]),
        },
        "valid_kind_overrepair": sum(
            cell["overrepair"] for cell in valid_kind.values()),
        "interpretation": (
            "ELIGIBLE_EXPLORATORY"
            if positive_control_pass else "INCONCLUSIVE_POSITIVE_CONTROL"),
    }


def _print_scores(rows):
    for fixture, arm in sorted({(r["fixture"], r["arm"]) for r in rows}):
        subset = [
            row for row in rows
            if (row["fixture"], row["arm"]) == (fixture, arm)
        ]
        n = len(subset)
        safe = sum(row["safe_effective"] for row in subset)
        unsafe = sum(row["unsafe_finalize"] for row in subset)
        signal = sum(row["signal_mentioned"] for row in subset)
        done = sum(row["decision"] == "report_done" for row in subset)
        request = sum(row["decision"] == "request_evidence" for row in subset)
        repair = sum(row["decision"] == "repair" for row in subset)
        invalid = sum(row["decision"] == "INVALID" for row in subset)
        intended = sum(
            row["repair_kind"] == "mixrig_structural_repair" for row in subset)
        print(
            f"{fixture:<18} {arm:<4} n={n} | safe_effective {safe}/{n}"
            f" | report_done {done}/{n} | request {request}/{n}"
            f" | repair {repair}/{n} | invalid {invalid}/{n}"
            f" | intended_repair {intended}/{n}"
            f" | unsafe_finalize {unsafe}/{n} | signal_mentioned {signal}/{n}"
        )

    contrasts = summarize_contrasts(rows)
    print("\npreregistered contrasts")
    print(json.dumps(contrasts, ensure_ascii=False, indent=2))


def main():
    fixtures = load_fixtures()
    precondition_errors = fixture_preconditions(fixtures)
    if precondition_errors:
        raise SystemExit("PRECONDITION_FAIL:\n- " + "\n- ".join(precondition_errors))

    trials_path = os.path.join(HERE, "trials.json")
    if not os.path.exists(trials_path):
        print("\nNO_TRIALS: collect fresh empirical trials after preregistration.")
        return
    manifest_path = os.path.join(HERE, "_prompts.json")
    if not os.path.exists(manifest_path):
        raise SystemExit("PROVENANCE_FAIL: _prompts.json is required for hash validation")
    data = _read_json(trials_path)
    manifest = _read_json(manifest_path)
    provenance_errors = validate_trial_set(data, fixtures, manifest)
    if provenance_errors:
        raise SystemExit("PROVENANCE_FAIL:\n- " + "\n- ".join(provenance_errors))

    rows = [score_trial(trial, fixtures) for trial in data["results"]]
    print("\nEMPIRICAL_TRIAL_SET: provenance contract satisfied")
    _print_scores(rows)


if __name__ == "__main__":
    main()
