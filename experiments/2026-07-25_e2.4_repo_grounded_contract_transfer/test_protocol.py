import hashlib
import importlib.util
import json
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


def _load_cert_core():
    spec = importlib.util.spec_from_file_location("cert_core", HERE / "_cert_core.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fixture_paths():
    return sorted(HERE.glob("fixture_*.json"))


def _load_json(path):
    return json.loads(path.read_text())


def _project_server_response(response, expected):
    return {key: response.get(key) for key in expected}


def test_fixtures_match_required_shape_and_hashes():
    for path in _fixture_paths():
        packet = _load_json(path)
        assert packet["record_class"] == "repo_evidence_packet", path.name
        assert packet["experiment_id"] == "E2.4", path.name
        assert packet["repo"] == "goodand/concept-gate-taxonomy", path.name
        assert packet["extraction_policy"]["outside_knowledge_policy"] == "forbidden"
        assert isinstance(packet["run_pipeline_input"], list), path.name
        assert isinstance(packet["candidate_concepts"], list), path.name
        assert isinstance(packet["evidence_items"], list), path.name
        assert isinstance(packet["server_response"], dict), path.name

        evidence_ids = {item["evidence_id"] for item in packet["evidence_items"]}

        for item in packet["evidence_items"]:
            assert set(item) == {
                "evidence_id",
                "source_path",
                "source_kind",
                "locator",
                "text",
                "text_sha256",
                "extraction_note",
            }, path.name
            actual_hash = hashlib.sha256(item["text"].encode()).hexdigest()
            assert actual_hash == item["text_sha256"], path.name

        for concept in packet["run_pipeline_input"]:
            assert set(concept) == {"name", "features"}, path.name
            for feature in concept["features"]:
                assert set(feature) == {"feature", "type", "evidence"}, path.name
                assert len(feature["evidence"]) >= 4, path.name

        for concept in packet["candidate_concepts"]:
            assert set(concept) == {"name", "features"}, path.name
            for feature in concept["features"]:
                assert set(feature) == {"feature", "type", "evidence_refs"}, path.name
                assert set(feature["evidence_refs"]) <= evidence_ids, path.name


def test_candidate_concepts_match_run_pipeline_input_surface():
    for path in _fixture_paths():
        packet = _load_json(path)
        candidate = [
            {
                "name": concept["name"],
                "features": [
                    {
                        "feature": feature["feature"],
                        "type": feature["type"],
                    }
                    for feature in concept["features"]
                ],
            }
            for concept in packet["candidate_concepts"]
        ]
        run_input = [
            {
                "name": concept["name"],
                "features": [
                    {
                        "feature": feature["feature"],
                        "type": feature["type"],
                    }
                    for feature in concept["features"]
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


# Model-facing metadata must not name a decision/verdict or state an expectation.
# `evidence_packet_schema.json` says hidden-oracle fields must not reach the model,
# but extraction_note/locator ARE shipped inside evidence_items and so are model-facing.
# fixture_conflicting.json once carried "CONTRACT_REPO's correct behavior is still to
# abstain ... the expected contract_verdict is loosened to ..." in an extraction_note,
# which handed the model its answer and invalidated that fixture's smoke result.
# Bare "repair" is deliberately NOT listed: ev5's source commit genuinely discusses
# "an available repair value", so the word is unavoidable in describing it.
_VERDICT_TOKENS = (
    "accept_report",
    "abstain",
    "sufficient_consistent",
    "sufficient_repairable",
    "insufficient_evidence",
    "conflicting_evidence",
    "out_of_scope",
)
_EXPECTATION_PHRASES = re.compile(
    r"correct behavior|expected (contract_)?verdict|should abstain|hidden oracle|정답|기대 판정",
    re.IGNORECASE,
)


def test_model_facing_metadata_does_not_leak_the_oracle():
    for path in _fixture_paths():
        packet = _load_json(path)
        for item in packet["evidence_items"]:
            for field in ("extraction_note", "locator"):
                value = item.get(field, "")
                leaked = [t for t in _VERDICT_TOKENS if t in value]
                assert not leaked, (
                    f"{path.name} {item['evidence_id']}.{field} names a decision/verdict "
                    f"{leaked} -- this field is shipped to the model"
                )
                assert not _EXPECTATION_PHRASES.search(value), (
                    f"{path.name} {item['evidence_id']}.{field} states an expected outcome "
                    f"-- this field is shipped to the model"
                )


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
    path = HERE / "fixture_sufficient_repairable.json"
    packet = _load_json(path)

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
