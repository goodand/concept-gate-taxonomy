"""Fixture checks for D-H1a-13 Q13.3's qualification-gate controls.

QF-SELECT only. QF-DEFER is deliberately absent -- exhaustive enumeration
found no same-source_kind conflicting-type material in this repository
(`correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md`, Q14
submitted, awaiting judgment). Fabricating one would violate the same
evidence-provenance discipline that shaped `fixture_source_authority.json`
through C2-C10 -- excerpts must be real, instance-bound, verbatim, and not
self-referential.

This mirrors `test_h1a_fixture.py`'s discipline for the confirmatory
fixture, adapted for the opposite shape: QF-SELECT must show UNANIMOUS
support for one type (not a conflict) from at least two independently
eligible sources with no counter-evidence anywhere.
"""

from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name: str, filename: str):
    key = f"_h1a_qf_fixture_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


surface = _load("surface", "_h1a_surface.py")

FIXTURE_PATH = HERE / "fixture_qf_select.json"


def fixture() -> dict:
    import json
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


# --- provenance: every byte traces to a real, current repo location -------

def test_fixture_qualifies_against_the_live_repository():
    manifest = surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    assert manifest["status"] == "passed"
    for check in manifest["evidence_checks"]:
        assert check["locator_resolved"], check["evidence_id"]
        assert check["excerpt_exact_match"], check["evidence_id"]
        assert check["text_sha256_verified"], check["evidence_id"]


def test_source_commit_exists_in_repo_history():
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"{fixture()['source_commit']}^{{commit}}"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_every_evidence_text_is_verbatim_from_its_source():
    for item in fixture()["evidence_sources"]:
        ref = item["source_ref"]
        lines = (REPO_ROOT / ref["path"]).read_text(encoding="utf-8").split("\n")
        excerpt = "\n".join(lines[ref["start_line"] - 1: ref["end_line"]])
        assert excerpt == item["text"], item["evidence_id"]
        assert hashlib.sha256(item["text"].encode()).hexdigest() == item["text_sha256"]


# --- the whole point: unanimous, instance-bound, no counter-evidence ------

CONCEPT, FEATURE, EXPECTED_TYPE = "자동차", "엔진", "structural_composition"


def test_both_sources_are_eligible_and_independent():
    items = {i["evidence_id"]: i for i in fixture()["evidence_sources"]}
    assert items["ev1"]["source_kind"] == "doc"
    assert items["ev2"]["source_kind"] == "code"
    assert items["ev1"]["source_ref"]["path"] != items["ev2"]["source_ref"]["path"]


def test_conflict_is_instance_bound_on_both_sides():
    items = {i["evidence_id"]: i["text"] for i in fixture()["evidence_sources"]}
    for eid in ("ev1", "ev2"):
        assert CONCEPT in items[eid] and FEATURE in items[eid], (
            f"{eid} not bound to {CONCEPT}/{FEATURE}"
        )


def test_the_two_sources_agree_this_is_the_qualification_shape():
    """QF-SELECT's defining property, inverted from the confirmatory
    fixture's conflict check: both eligible sources must assert the SAME
    type, and no other type may appear anywhere in either text."""
    items = {i["evidence_id"]: i["text"] for i in fixture()["evidence_sources"]}
    for eid in ("ev1", "ev2"):
        assert EXPECTED_TYPE in items[eid], f"{eid} missing {EXPECTED_TYPE!r}"
        assert "essential_feature" not in items[eid], (
            f"{eid} names the other allowed type -- this would no longer be "
            f"unanimous support"
        )


def test_candidate_records_the_unanimous_type():
    feature = next(
        f for c in fixture()["candidate_concepts"]
        for f in c["features"] if f["feature"] == FEATURE
    )
    assert feature["type"] == EXPECTED_TYPE


def test_no_oracle_field_present():
    ORACLE_TOKENS = (
        "expected_decision", "expected_type", "expected_contract_verdict",
        "semantic_class", "correct", "정답", "기대 판정", "oracle",
    )

    def walk(node, path="$"):
        if isinstance(node, dict):
            for key, value in node.items():
                assert key not in ORACLE_TOKENS, f"{path}.{key}"
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
    walk(fixture())


# --- model-facing payload: same discipline as the confirmatory fixture ---

def test_model_payload_carries_concept_feature_pair_with_no_type():
    manifest = surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = surface.build_model_payload(fixture(), manifest)
    pair = payload["concept_feature_pair"]
    assert pair["concept"] == CONCEPT
    assert pair["feature"] == FEATURE
    assert set(pair["evidence_refs"]) == {"ev1", "ev2"}
    assert "type" not in pair


def test_no_anchor_guard_passes_the_real_payload():
    manifest = surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = surface.build_model_payload(fixture(), manifest)
    surface.assert_no_model_facing_type_anchor(payload)  # must not raise


def test_model_payload_never_carries_server_response():
    manifest = surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = surface.build_model_payload(fixture(), manifest)
    assert "server_response" not in payload
    assert set(payload) == {"concept_feature_pair", "evidence_items"}


def test_server_response_reflects_the_real_certifier_not_a_fabricated_pass():
    """This fixture's server_response.status is NEEDS_CORRECTION because the
    single-feature run_pipeline_input has no essential_feature sibling for
    자동차 (verified by direct execution against the real certifier -- see
    builder_metadata.server_response_honesty). That is recorded honestly
    rather than inventing an unrelated essential_feature fact about 자동차
    that does not exist in this repository merely to force a PASS. It does
    not matter for the model: server_response is never forwarded
    (H1a deviation #2), confirmed by the previous test."""
    assert fixture()["server_response"]["status"] == "NEEDS_CORRECTION"


def test_not_pooled_with_the_confirmatory_cohort_is_declared():
    assert "not_pooled" in fixture()["builder_metadata"]
    assert "pooled_with_main_cohort" in fixture()["builder_metadata"]["not_pooled"] or \
        "confirmatory" in fixture()["builder_metadata"]["not_pooled"]
