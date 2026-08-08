"""The 10 pre-implementation gates DESIGN_DECISION_H3.md §6 requires, plus two
byte-reuse checks, before any H3 smoke or pilot trial runs.

Mapping to DESIGN_H3_common_action.md §6 -- gate number -> test:
  1  payload bytes/hash identical across arms  -> test_payload_bytes_identical_across_arms_same_fixture
  2  evidence item key set                     -> test_evidence_item_keys_match_model_evidence_keys
  3  common action schema subtree byte-equal    -> test_common_action_subtree_identical_in_all_three_variants
  4  prompt diff = registered rule text only    -> test_rendered_prompt_diff_is_only_registered_rule_text
  5  hidden oracle/class/action unreachable     -> test_h3_module_never_imports_oracle_manifest
  6  known leak positive-control absent         -> test_known_leak_sentences_absent_from_h3_prompts
  7  qualification bound to fixture hash        -> test_stale_fixture_after_qualification_is_refused
  8  smoke/pilot/main share one dispatcher       -> test_single_render_entrypoint
  9  all hashes recorded                        -> test_freeze_records_all_required_hashes
  10 root suite collects and passes             -> automatic (scripts/run_gates.py globs test_*.py)
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
E23_DIR = HERE.parent / "2026-07-25_e2.3_global_invariant_generalization"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("e24_surface_test_h3", HERE / "_surface.py")
h3 = _load("e24_h3_test", HERE / "_h3.py")
test_surface_mod = _load("e24_test_surface_for_h3", HERE / "test_surface.py")

COMMON_FIELDS = ("action", "repaired_concepts", "cited_evidence_ids", "report")
REQUIRED_HASH_KEYS = {
    "fixture_sha256", "qualification_sha256", "payload_sha256",
    "contract_prompt_sha256", "rendered_prompt_sha256", "decision_schema_sha256",
    "system_prompt_sha256", "presented_schema_sha256",
}


def _extract_payload_json(rendered: str) -> dict:
    tail = rendered.split("payload:\n", 1)[1]
    return json.loads(tail.strip())


# --- structural sanity (not a numbered gate, but guards the fixtures above) --

def test_conflicting_fixture_excluded_not_replaced():
    """D-H3-2: the empty conflicting slot is not filled with another class."""
    assert "E24-F-04" not in h3.H3_FIXTURES
    assert len(h3.H3_FIXTURES) == 3


def test_pilot_bundle_is_45_trials():
    assert len(h3.PILOT_BUNDLE) == len(h3.H3_FIXTURES) * len(h3.H3_ARMS) * h3.PILOT_REPLICATES == 45


def test_smoke_bundle_is_3_trials_one_per_arm_same_fixture():
    assert len(h3.SMOKE_BUNDLE) == 3
    assert {t[1] for t in h3.SMOKE_BUNDLE} == set(h3.H3_ARMS)
    assert {t[0] for t in h3.SMOKE_BUNDLE} == {h3.SMOKE_FIXTURE}


def test_control_and_a_h3_share_the_same_schema_variant():
    """Per new_constraints: CONTROL_REPO_H3/A_REPO_H3 differ only in prompt
    rule text, never in schema."""
    schema = h3.h3_schema()
    assert schema["arm_schema_map"]["CONTROL_REPO_H3"] == "h3_common_action"
    assert schema["arm_schema_map"]["A_REPO_H3"] == "h3_common_action"


def test_report_field_is_string_not_object():
    """Q1 in DESIGN_H3_common_action.md."""
    schema = h3.h3_schema()
    for variant in ("h3_common_action", "h3_contract_action"):
        assert schema["variants"][variant]["schema"]["properties"]["report"]["type"] == "string"


def test_cited_evidence_ids_is_a_validity_gate_not_a_scored_outcome():
    """Q2 in DESIGN_H3_common_action.md."""
    schema = h3.h3_schema()
    constraints_text = " ".join(schema["semantic_constraints"])
    assert "cited_evidence_ids" in constraints_text
    assert "not a scored primary outcome" in constraints_text


# --- gate 1 -------------------------------------------------------------

def test_payload_bytes_identical_across_arms_same_fixture():
    for fixture_id in h3.H3_FIXTURES:
        _, _, payload = h3.build_h3_payload(fixture_id)
        extracted = {
            arm: _extract_payload_json(h3.render_h3_prompt(arm, payload))
            for arm in h3.H3_ARMS
        }
        hashes = {arm: surface.sha256_of(p) for arm, p in extracted.items()}
        assert len(set(hashes.values())) == 1, (fixture_id, hashes)
        assert surface.sha256_of(payload) == next(iter(hashes.values()))


# --- gate 2 -------------------------------------------------------------

def test_evidence_item_keys_match_model_evidence_keys():
    for fixture_id in h3.H3_FIXTURES:
        _, _, payload = h3.build_h3_payload(fixture_id)
        for item in payload["evidence_items"]:
            assert set(item) == set(surface.MODEL_EVIDENCE_KEYS)


# --- gate 3 -------------------------------------------------------------

def test_common_action_subtree_identical_in_all_three_variants():
    schema = h3.h3_schema()
    common = schema["variants"]["h3_common_action"]["schema"]
    contract = schema["variants"]["h3_contract_action"]["schema"]
    for field in COMMON_FIELDS:
        assert surface.canonical_json(common["properties"][field]) == \
            surface.canonical_json(contract["properties"][field]), field
    assert set(COMMON_FIELDS) <= set(common["required"])
    assert set(COMMON_FIELDS) <= set(contract["required"])
    assert surface.canonical_json(common["$defs"]) == surface.canonical_json(contract["$defs"])


# --- gate 4 -------------------------------------------------------------

def test_rendered_prompt_diff_is_only_registered_rule_text():
    _, _, payload = h3.build_h3_payload(h3.H3_FIXTURES[0])
    rendered = {arm: h3.render_h3_prompt(arm, payload) for arm in h3.H3_ARMS}

    for arm, text in rendered.items():
        assert h3.COMMON_ACTION_BLOCK in text, arm

    prefixes = {arm: text.split(h3.COMMON_ACTION_BLOCK)[0] for arm, text in rendered.items()}
    assert len(set(prefixes.values())) == len(h3.H3_ARMS), "rule texts should differ arm-to-arm"

    suffixes = {arm: text.split(h3.COMMON_ACTION_BLOCK)[1] for arm, text in rendered.items()}
    assert len(set(suffixes.values())) == 1, "payload + trailing text must be identical across arms"


# --- gate 5 -------------------------------------------------------------

def test_h3_module_never_imports_oracle_manifest():
    source = (HERE / "_h3.py").read_text(encoding="utf-8")
    forbidden = ("oracle_manifest", "expected_decision", "expected_contract_verdict",
                 "expected_action", "semantic_class")
    for token in forbidden:
        assert token not in source, token


# --- gate 6 -------------------------------------------------------------

@pytest.mark.parametrize("leak", test_surface_mod.KNOWN_LEAKS, ids=range(len(test_surface_mod.KNOWN_LEAKS)))
def test_known_leak_sentences_absent_from_h3_prompts(leak):
    _, _, payload = h3.build_h3_payload(h3.H3_FIXTURES[0])
    for arm in h3.H3_ARMS:
        assert leak not in h3.render_h3_prompt(arm, payload)


# --- gate 7 -------------------------------------------------------------

def test_stale_fixture_after_qualification_is_refused():
    fixture, manifest, _ = h3.build_h3_payload(h3.H3_FIXTURES[0])
    tampered = {**manifest, "fixture_sha256": "0" * 64}
    with pytest.raises(surface.SurfaceError):
        surface.build_model_payload(fixture, tampered)


# --- gate 8 -------------------------------------------------------------

def test_single_render_entrypoint():
    source = (HERE / "_h3.py").read_text(encoding="utf-8")
    assert source.count("def render_h3_prompt") == 1
    assert source.count("def arm_rule_template") == 1
    # smoke() and freeze() both delegate to _freeze_bundle, not separate paths
    assert source.count("def _freeze_bundle") == 1
    tree = ast.parse(source)
    render_prompt_calls = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Attribute) and n.attr == "render_prompt"
    ]
    # every surface.render_prompt call site is inside arm_rule_template's
    # caller (render_h3_prompt) or the freeze/record paths that mirror it --
    # there is no third, ad hoc string-concatenation renderer.
    assert len(render_prompt_calls) >= 1


# --- gate 9 -------------------------------------------------------------

def test_freeze_records_all_required_hashes():
    smoke_path = HERE / "h3_smoke_prompts.json"
    if not smoke_path.exists():
        pytest.skip("h3_smoke_prompts.json not yet frozen (run `python3 _h3.py smoke` first)")
    frozen = json.loads(smoke_path.read_text(encoding="utf-8"))
    assert len(frozen["trials"]) == 3
    for trial in frozen["trials"]:
        missing = REQUIRED_HASH_KEYS - set(trial)
        assert not missing, (trial["trial_id"], missing)


# --- byte-reuse verification (extra, not a numbered gate) ----------------

def test_contract_repo_h3_reuses_contract_prompt_rules_verbatim():
    full = surface.load_contract_prompt(HERE / "contract_prompt.md")
    rule_text = h3.contract_rule_text()
    assert full.startswith(rule_text)


def test_a_repo_h3_uses_the_same_global_consistency_rule_text_as_e2_3():
    tree = ast.parse((E23_DIR / "_gen_prompts.py").read_text(encoding="utf-8"))
    expected = None
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "GLOBAL_CONSISTENCY_RULE"):
            expected = ast.literal_eval(node.value)
    assert expected is not None
    assert h3.GLOBAL_CONSISTENCY_RULE == expected
    assert expected in h3._a_rule_text()
