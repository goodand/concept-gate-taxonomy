"""Fixture-level self-checks for E2.4 (repo_evidence_fixture_v2).

Structural guarantees about the model-facing surface live in test_surface.py.
This file checks the fixtures themselves: that they satisfy the v2 schema, that
the model-facing concept surface still mirrors what was actually submitted to
the pipeline, that server_response is reproducible, and that the one designated
repair leaves a clean pipeline state.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("e24_surface_protocol", HERE / "_surface.py")


def _load_cert_core():
    return _load("e24_cert_core", HERE / "_cert_core.py")


def _fixture_paths():
    return sorted(HERE.glob("fixture_*.json"))


def _load_json(path):
    return json.loads(path.read_text())


def _project_server_response(response, expected):
    return {key: response.get(key) for key in expected}


def test_fixtures_satisfy_the_v2_schema():
    """validate_fixture is the schema; there is no separate .json to drift from."""
    for path in _fixture_paths():
        surface.validate_fixture(_load_json(path))


def test_fixtures_qualify_against_the_working_tree():
    """Every cited excerpt must still resolve byte-for-byte where it claims to be.

    This is the check that would catch an evidence source being edited,
    moved, or rewritten out from under a frozen fixture.
    """
    for path in _fixture_paths():
        manifest = surface.qualify_fixture(_load_json(path), REPO_ROOT, run_tests=False)
        assert manifest["status"] == "passed", (path.name, manifest["evidence_checks"])


def test_candidate_concepts_match_run_pipeline_input_surface():
    for path in _fixture_paths():
        packet = _load_json(path)
        candidate = [
            {
                "name": concept["name"],
                "features": [
                    {"feature": f["feature"], "type": f["type"]}
                    for f in concept["features"]
                ],
            }
            for concept in packet["candidate_concepts"]
        ]
        run_input = [
            {
                "name": concept["name"],
                "features": [
                    {"feature": f["feature"], "type": f["type"]}
                    for f in concept["features"]
                ],
            }
            for concept in packet["run_pipeline_input"]
        ]
        assert candidate == run_input, path.name


def test_server_response_is_reproducible_from_run_pipeline_input():
    cert_core = _load_cert_core()
    for path in _fixture_paths():
        packet = _load_json(path)
        observed = cert_core.run_and_certify(packet["run_pipeline_input"])
        expected = packet["server_response"]
        assert _project_server_response(observed, expected) == expected, path.name


# Diagnostics only, per DESIGN_DECISION_surface_separation.md §7: the guard is
# defense-in-depth and must never be the reason something is considered safe.
# The enforcement is build_model_payload's whitelist construction, covered in
# test_surface.py. This scans what the model actually receives rather than raw
# fixture fields -- builder prose now lives in builder_metadata, which the
# builder cannot reach, so scanning fixture text would prove nothing.
_VERDICT_TOKENS = (
    "accept_report",
    "abstain",
    "sufficient_consistent",
    "sufficient_repairable",
    "insufficient_evidence",
    "conflicting_evidence",
    "out_of_scope",
    "direct_support",
    "indirect_context",
)
_EXPECTATION_PHRASES = re.compile(
    r"correct behavior|expected (contract_)?verdict|should abstain|hidden oracle|"
    r"정답|기대 판정",
    re.IGNORECASE,
)


def test_built_payload_carries_no_verdict_vocabulary():
    for path in _fixture_paths():
        fixture = _load_json(path)
        manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
        payload = surface.build_model_payload(fixture, manifest)

        # `text` is verbatim repo content pinned by sha256 and re-verified by
        # qualification, so it is excluded: a source file legitimately may
        # discuss these terms, and an author cannot inject there without
        # changing the repo itself.
        scanned = surface.canonical_json(
            {
                "candidate_concepts": payload["candidate_concepts"],
                "evidence_ids": [e["evidence_id"] for e in payload["evidence_items"]],
                "source_kinds": [e["source_kind"] for e in payload["evidence_items"]],
                "server_response": payload["server_response"],
            }
        )
        leaked = [t for t in _VERDICT_TOKENS if t in scanned]
        assert not leaked, f"{path.name}: verdict vocabulary in payload metadata {leaked}"
        assert not _EXPECTATION_PHRASES.search(scanned), path.name


def test_sufficient_repairable_single_repair_yields_clean_pass():
    """Pins fixture_sufficient_repairable.json's intended Rule 3 repair:
    돌체's 바퀴 (essential_feature, evidence states 구성 부분/part-whole)
    should repair to structural_composition, keeping 갑종 as essential so
    the concept still has an essential axis post-repair. Both pre-repair
    (as shipped in run_pipeline_input) and post-repair states must be a
    clean PASS with no anti-patterns -- this is the deterministic half of
    the Rule 3 sufficiency claim; the LLM admissibility/sufficiency
    judgment itself is verified separately via independent review and a
    live CONTRACT_REPO smoke test, not by this test.
    """
    cert_core = _load_cert_core()
    packet = _load_json(HERE / "fixture_sufficient_repairable.json")

    pre = packet["run_pipeline_input"]
    assert pre == [
        {
            "name": "돌체",
            "features": [
                {
                    "feature": "바퀴",
                    "type": "essential_feature",
                    "evidence": "바퀴가 항목에 기록되어 있다",
                },
                {
                    "feature": "갑종",
                    "type": "essential_feature",
                    "evidence": "갑종이(가) 항목에 기록되어 있다",
                },
            ],
        }
    ]

    pre_observed = cert_core.run_and_certify(pre)
    assert pre_observed["status"] == "PASS"
    assert pre_observed["anti_patterns"] == []
    assert pre_observed["composition_issues"] == []

    post = json.loads(json.dumps(pre))
    post[0]["features"][0]["type"] = "structural_composition"
    post_observed = cert_core.run_and_certify(post)
    assert post_observed["status"] == "PASS"
    assert post_observed["anti_patterns"] == []
    assert post_observed["composition_issues"] == []
