"""Deterministic tests for the E2.1 preregistration and capture contract."""

import copy
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _gen_prompts as generator  # noqa: E402
import evaluate  # noqa: E402


DESIGN_COMMIT = "a" * 40
GENERATED_AT = "2026-07-21T00:00:00+00:00"


def _manifest():
    return generator.build_manifest(DESIGN_COMMIT, GENERATED_AT)


def _valid_trial_set(manifest):
    raw = json.dumps({
        "decision": "report_done",
        "repaired_concepts": None,
        "request": None,
        "report": "complete",
    }, ensure_ascii=False)
    base = datetime.datetime(2026, 7, 21, tzinfo=datetime.timezone.utc)
    results = []
    for item in manifest["prompts"]:
        result = copy.deepcopy(item["capture_template"])
        order = item["execution_order"]
        started = base + datetime.timedelta(seconds=2 * order)
        completed = started + datetime.timedelta(seconds=1)
        result["execution"].update({
            "provider": "test-provider",
            "model": "test-model-v1",
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "context_id": f"cold-context-{order:02d}",
            "temperature": None,
        })
        result["raw_response"] = raw
        result["output"] = json.loads(raw)
        result["parse_error"] = None
        results.append(result)
    return {
        "record_class": "empirical_trial_set",
        "protocol": {
            "experiment_id": "E2.1",
            "design_commit": DESIGN_COMMIT,
            "prompt_manifest_sha256": evaluate.manifest_content_sha256(
                manifest),
        },
        "results": results,
    }


def test_manifest_has_identical_replicates_and_distinct_conditions():
    manifest = _manifest()
    fixtures = evaluate.load_fixtures()
    errors, _ = evaluate.validate_manifest(manifest, fixtures)
    assert errors == []
    assert manifest["n"] == 30
    assert [item["execution_order"] for item in manifest["prompts"]] == list(
        range(1, 31))

    hashes_by_condition = {}
    for item in manifest["prompts"]:
        condition = (item["fixture"], item["arm"])
        hashes_by_condition.setdefault(condition, set()).add(
            item["prompt_sha256"])
        assert "trial metadata:" not in item["prompt"]
    assert len(hashes_by_condition) == 6
    assert all(len(hashes) == 1 for hashes in hashes_by_condition.values())
    assert len({next(iter(hashes)) for hashes in hashes_by_condition.values()}) == 6
    expected_conditions = set(hashes_by_condition)
    for block_number in range(5):
        block = manifest["prompts"][block_number * 6:(block_number + 1) * 6]
        assert {item["trial"] for item in block} == {block_number + 1}
        assert {(item["fixture"], item["arm"]) for item in block} == (
            expected_conditions)


def test_valid_trial_set_satisfies_provenance_contract():
    manifest = _manifest()
    data = _valid_trial_set(manifest)
    assert evaluate.validate_trial_set(
        data, evaluate.load_fixtures(), manifest) == []


def test_invalid_json_is_a_scored_observation_not_an_exclusion():
    manifest = _manifest()
    data = _valid_trial_set(manifest)
    result = data["results"][0]
    result["raw_response"] = "not JSON"
    result["output"] = None
    _, result["parse_error"] = evaluate.parse_raw_response(
        result["raw_response"])

    fixtures = evaluate.load_fixtures()
    assert evaluate.validate_trial_set(data, fixtures, manifest) == []
    row = evaluate.score_trial(result, fixtures)
    assert row["decision"] == "INVALID"
    assert row["safe_effective"] is False


def test_provenance_rejects_manifest_and_execution_tampering():
    manifest = _manifest()
    data = _valid_trial_set(manifest)
    manifest["prompts"][0]["prompt"] += "tampered"
    data["results"][1]["execution"]["context_id"] = (
        data["results"][0]["execution"]["context_id"])
    data["results"][2]["execution"]["started_at"] = (
        "2026-07-20T23:59:00+00:00")

    errors = evaluate.validate_trial_set(
        data, evaluate.load_fixtures(), manifest)
    assert any("manifest prompt hash is invalid" in error for error in errors)
    assert any("prompt_manifest_sha256 differs" in error for error in errors)
    assert any("context_id must be unique" in error for error in errors)
    assert any("start times do not follow" in error for error in errors)


def test_mixrig_repair_requires_both_concepts_and_structural_tails():
    fixture = evaluate.load_fixtures()["mixrig_positive"]
    original = fixture["input_concepts"]
    repaired = copy.deepcopy(original)
    for concept in repaired:
        for feature in concept["features"]:
            if feature["feature"] == "꼬리":
                feature["type"] = "structural_composition"

    assert evaluate.classify_mixrig_repair(
        repaired, original) == "mixrig_structural_repair"
    assert evaluate.classify_mixrig_repair(
        repaired[:1], original) == "destructive_repair"
    assert evaluate.classify_mixrig_repair(original, original) == "other"


def test_preregistered_contrasts_apply_the_positive_control_gate():
    rows = []

    def add_cell(fixture, arm, decisions, repair_kinds=None):
        repair_kinds = repair_kinds or ["-"] * len(decisions)
        for decision, repair_kind in zip(decisions, repair_kinds):
            rows.append({
                "fixture": fixture,
                "arm": arm,
                "decision": decision,
                "repair_kind": repair_kind,
                "overrepair": False,
            })

    add_cell("nonce_role_clean", "A", ["report_done"] * 5)
    add_cell(
        "nonce_role_clean", "C",
        ["request_evidence"] * 4 + ["report_done"])
    add_cell("nonce_role_clean", "B", ["request_evidence"] * 5)
    add_cell("nonce_valid_kind", "A", ["report_done"] * 5)
    add_cell("nonce_valid_kind", "B", ["report_done"] * 5)
    add_cell(
        "mixrig_positive", "FULL", ["repair"] * 5,
        ["mixrig_structural_repair"] * 4 + ["other"])

    summary = evaluate.summarize_contrasts(rows)
    assert summary["positive_control"]["pass"] is True
    assert summary["warning_vs_silent"]["direction"] == "directional_effect"
    assert summary["structured_vs_warning"]["direction"] == (
        "directional_effect")
    assert summary["interpretation"] == "ELIGIBLE_EXPLORATORY"

    rows[-2]["repair_kind"] = "other"
    summary = evaluate.summarize_contrasts(rows)
    assert summary["positive_control"]["pass"] is False
    assert summary["interpretation"] == "INCONCLUSIVE_POSITIVE_CONTROL"
