"""The eight tests required by DESIGN_DECISION_surface_separation.md §7.

The point of this file is that the model-facing surface is closed *by
construction* and stays that way. The defect being retired here shipped
judgment information to the model through `extraction_note` for weeks while a
schema description claimed it could not happen, so the checks below execute
rather than describe.

Test 3 uses the six leak sentences that were actually found in this
experiment's fixtures. They are committed as a positive-control corpus
precisely because the earlier ad hoc guard's negative control was run once by
hand and never persisted, which left nothing to stop a later edit from
silently weakening it.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    """Load a sibling/tool module by path under a unique name.

    Registering in sys.modules is required, not cosmetic: dataclasses resolve
    their annotations through sys.modules[cls.__module__]. The unique name is
    what keeps this from re-creating the very collision that made the gate
    runner necessary.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("e24_surface", HERE / "_surface.py")


# Real repo text: conceptgate/cg_partwhole.py line 36. Its sha256 is the same
# value the pre-migration fixture recorded for ev3, so this anchors the tests
# to genuine committed content rather than to a synthetic string.
EV3_TEXT = '    "material_of":     "structural_composition",  # Winston stuff-object (has-a)'

# The six sentences that really leaked, verbatim (PROBLEM_2_conflicting.md §2).
KNOWN_LEAKS = [
    "CONTRACT_REPO's correct behavior is still to abstain rather than force a decision"
    " -- but the expected contract_verdict is loosened to 'abstain via"
    " insufficient_evidence, conflicting_evidence, or out_of_scope (any of the three)'",
    "audit should classify this as indirect_context or ambiguous, never direct_support"
    " for any specific FeatureType",
    "This directly contradicts the currently-assigned type: the evidence supports"
    " structural_composition, not essential_feature",
    "Live @mcp.tool docstring ... kept as corroborating context, not sole support",
    "Combined with ev9's general definition of what structural_composition means,"
    " this binds the abstract type definition to this specific feature",
    "frozen and reused across two prior, unrelated experiments before this E2.4"
    " fixture was built",
]


def _head_commit() -> str:
    import subprocess

    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
        capture_output=True, text=True,
    ).stdout.strip()


def make_fixture() -> dict:
    return {
        "fixture_version": surface.FIXTURE_VERSION,
        "experiment_id": "E2.4",
        "repo": "goodand/concept-gate-taxonomy",
        "source_commit": _head_commit(),
        "run_pipeline_input": [
            {
                "name": "테스트개념",
                "features": [
                    {
                        "feature": "재료",
                        "type": "essential_feature",
                        "evidence": "재료가 항목에 기록되어 있다",
                    }
                ],
            }
        ],
        "candidate_concepts": [
            {
                "name": "테스트개념",
                "features": [
                    {
                        "feature": "재료",
                        "type": "essential_feature",
                        "evidence_refs": ["ev3"],
                    }
                ],
            }
        ],
        "evidence_sources": [
            {
                "evidence_id": "ev3",
                "source_kind": "code",
                "source_ref": {
                    "kind": "file_lines",
                    "path": "conceptgate/cg_partwhole.py",
                    "start_line": 36,
                    "end_line": 36,
                },
                "text": EV3_TEXT,
                "text_sha256": surface.sha256_of(EV3_TEXT),
            }
        ],
        "server_response": {
            "status": "PASS",
            "dag": {},
            "composition_issues": [],
            "anti_patterns": [],
        },
        "builder_metadata": {"evidence_notes": {}, "change_history": []},
    }


def qualified(fixture):
    manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
    assert manifest["status"] == "passed", manifest
    return manifest


# --- 1. output key-set is exactly the schema, recursively -------------------

def test_payload_key_sets_match_schema_exactly():
    fixture = make_fixture()
    payload = surface.build_model_payload(fixture, qualified(fixture))

    assert tuple(sorted(payload)) == tuple(sorted(surface.MODEL_PAYLOAD_KEYS))
    for concept in payload["candidate_concepts"]:
        assert tuple(sorted(concept)) == tuple(sorted(surface.MODEL_CONCEPT_KEYS))
        for feature in concept["features"]:
            assert tuple(sorted(feature)) == tuple(sorted(surface.MODEL_FEATURE_KEYS))
    for item in payload["evidence_items"]:
        assert tuple(sorted(item)) == tuple(sorted(surface.MODEL_EVIDENCE_KEYS))
    assert tuple(sorted(payload["server_response"])) == tuple(
        sorted(surface.MODEL_SERVER_RESPONSE_KEYS)
    )


def test_builder_only_fields_never_appear_in_payload():
    fixture = make_fixture()
    payload = surface.build_model_payload(fixture, qualified(fixture))
    serialized = surface.canonical_json(payload)
    for hidden in ("source_ref", "text_sha256", "builder_metadata", "run_pipeline_input",
                   "source_commit", "fixture_version", "repo", "cg_partwhole"):
        assert hidden not in serialized, hidden


# --- 2. hidden-field noninterference ----------------------------------------

def test_builder_metadata_cannot_move_the_payload_one_byte():
    fixture = make_fixture()
    baseline = surface.build_model_payload(fixture, qualified(fixture))
    baseline_bytes = surface.canonical_json(baseline)

    loud = copy.deepcopy(fixture)
    loud["builder_metadata"] = {
        "evidence_notes": {"ev3": " ".join(KNOWN_LEAKS)},
        "change_history": [{"note": "the correct answer is abstain"}],
    }
    after = surface.build_model_payload(loud, qualified(loud))

    assert surface.canonical_json(after) == baseline_bytes
    assert surface.sha256_of(after) == surface.sha256_of(baseline)


# --- 3. positive control over the six sentences that really leaked ----------

@pytest.mark.parametrize("leak", KNOWN_LEAKS, ids=range(len(KNOWN_LEAKS)))
def test_known_leak_sentence_never_reaches_the_rendered_prompt(leak):
    fixture = make_fixture()
    fixture["builder_metadata"]["evidence_notes"]["ev3"] = leak

    payload = surface.build_model_payload(fixture, qualified(fixture))
    rendered = surface.render_prompt(
        surface.load_contract_prompt(HERE / "contract_prompt.md"), payload
    )

    assert leak not in rendered
    # a distinctive fragment, in case the whole sentence is reflowed somewhere
    assert leak.split(",")[0][:40] not in surface.canonical_json(payload)


# --- 4. structured locator rejects prose fields -----------------------------

@pytest.mark.parametrize(
    "bad_ref",
    [
        {"kind": "file_lines", "path": "conceptgate/cg_partwhole.py",
         "start_line": 36, "end_line": 36, "note": "trust me, this one is live"},
        {"kind": "file_lines", "path": "conceptgate/cg_partwhole.py",
         "start_line": 36, "end_line": 36, "description": "why it matters"},
        {"kind": "file_lines", "path": "conceptgate/cg_partwhole.py", "start_line": 36},
        {"kind": "file_lines", "path": "/etc/passwd", "start_line": 1, "end_line": 1},
        {"kind": "file_lines", "path": "../outside.py", "start_line": 1, "end_line": 1},
        {"kind": "file_lines", "path": "a.py", "start_line": 9, "end_line": 2},
        {"kind": "commit", "sha": "4017aff", "part": "body"},
        {"kind": "prose", "path": "a.py"},
    ],
    ids=["note", "description", "missing_key", "absolute_path", "escape_path",
         "reversed_lines", "short_sha", "unknown_kind"],
)
def test_source_ref_rejects_malformed_and_prose_bearing_locators(bad_ref):
    fixture = make_fixture()
    fixture["evidence_sources"][0]["source_ref"] = bad_ref
    with pytest.raises(surface.SurfaceError):
        surface.validate_fixture(fixture)


# --- 5. visible-field sensitivity -------------------------------------------

def _hashes(fixture):
    payload = surface.build_model_payload(fixture, qualified(fixture))
    rendered = surface.render_prompt(
        surface.load_contract_prompt(HERE / "contract_prompt.md"), payload
    )
    return surface.sha256_of(payload), surface.sha256_of(rendered)


def test_every_visible_field_moves_both_hashes():
    base_payload, base_prompt = _hashes(make_fixture())

    mutations = {}

    text = make_fixture()
    changed = EV3_TEXT.replace("Winston", "Winstonn")
    text["evidence_sources"][0]["text"] = changed
    text["evidence_sources"][0]["text_sha256"] = surface.sha256_of(changed)
    # text no longer matches the cited lines, so qualification must refuse it
    manifest = surface.qualify_fixture(text, REPO_ROOT, run_tests=False)
    assert manifest["status"] == "failed"
    assert manifest["evidence_checks"][0]["excerpt_exact_match"] is False

    kind = make_fixture()
    kind["evidence_sources"][0]["source_kind"] = "doc"
    mutations["source_kind"] = kind

    ctype = make_fixture()
    ctype["candidate_concepts"][0]["features"][0]["type"] = "structural_composition"
    mutations["candidate_type"] = ctype

    for name, mutated in mutations.items():
        payload_hash, prompt_hash = _hashes(mutated)
        assert payload_hash != base_payload, name
        assert prompt_hash != base_prompt, name


# --- 6. qualification binding -----------------------------------------------

def test_payload_refused_when_fixture_changed_after_qualification():
    fixture = make_fixture()
    manifest = qualified(fixture)

    tampered = copy.deepcopy(fixture)
    tampered["candidate_concepts"][0]["features"][0]["type"] = "structural_composition"

    with pytest.raises(surface.SurfaceError, match="changed after qualification"):
        surface.build_model_payload(tampered, manifest)


def test_payload_refused_when_qualification_failed():
    fixture = make_fixture()
    manifest = qualified(fixture)
    manifest["status"] = "failed"
    with pytest.raises(surface.SurfaceError, match="not 'passed'"):
        surface.build_model_payload(fixture, manifest)


# --- 7. canonical path end to end -------------------------------------------

def test_canonical_pipeline_pins_the_whole_surface():
    fixture = make_fixture()
    manifest = qualified(fixture)
    payload = surface.build_model_payload(fixture, manifest)
    contract = surface.load_contract_prompt(HERE / "contract_prompt.md")
    rendered = surface.render_prompt(contract, payload)
    schema = json.loads((HERE / "decision_schema.json").read_text(encoding="utf-8"))

    trial = surface.trial_manifest(
        trial_id="E24-R2-000",
        fixture=fixture,
        qualification_manifest=manifest,
        model_payload=payload,
        contract_prompt=contract,
        rendered_prompt=rendered,
        decision_schema=schema,
        builder_commit=_head_commit(),
        model="test",
    )

    for key in ("fixture_sha256", "qualification_sha256", "payload_sha256",
                "contract_prompt_sha256", "rendered_prompt_sha256",
                "decision_schema_sha256"):
        assert len(trial[key]) == 64, key
    assert trial["rendered_prompt_sha256"] == surface.sha256_of(rendered)
    # the payload really is embedded in what the model receives
    assert json.dumps(payload, ensure_ascii=False) in rendered


# --- 8. this experiment is actually executed by the gate runner -------------

def test_gate_runner_executes_this_experiment():
    runner = _load("run_gates", REPO_ROOT / "scripts" / "run_gates.py")
    covered = [cwd for _name, _argv, cwd, _is_pytest in runner.gates()]
    assert HERE in covered, (
        "scripts/run_gates.py must run this experiment's suite; otherwise these "
        "guards only execute when someone remembers to cd here"
    )
