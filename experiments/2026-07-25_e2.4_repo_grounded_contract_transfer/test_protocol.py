import hashlib
import importlib.util
import json
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
