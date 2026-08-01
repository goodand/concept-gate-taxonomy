"""Tests for the H1a anchor-sensitivity diagnostic (PREREGISTRATION.md §11).

The load-bearing claim is narrow and exact: flipping the anchor changes the
recorded type and NOTHING else. If any evidence text, id, source kind, or
ordering moved with it, the diagnostic would be measuring the wrong thing --
it would confound "anchor" with "whatever else drifted", and its verdict about
ceiling effects would be worthless in either direction.

That claim is proved by reconstruction, not by inspection: rebuild the flipped
payload from the unflipped one by changing only the anchor field, and require
byte equality. (`difflib.SequenceMatcher` was tried for the analogous check in
`_h1a_contract.py` and rejected -- its greedy LCS misaligns deletion boundaries
around short repeated substrings.)
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


diag = _load("h1a_diag", HERE / "_h1a_diag.py")
h1a_surface = _load("h1a_surface_for_diag", HERE / "_h1a_surface.py")
contract = _load("h1a_contract_for_diag", HERE / "_h1a_contract.py")


def fixture() -> dict:
    return diag.load_fixture()


# --- the factor structure matches what was preregistered -------------------

def test_factors_and_repetitions_match_preregistration():
    assert diag.ARMS == ("PROHIBITION_KEPT", "PROHIBITION_REMOVED")
    assert set(diag.ANCHORS) == {"structural_composition", "essential_feature"}
    assert diag.R_DIAG == 5
    assert len(diag.diagnostic_cells()) == 4
    assert len(diag.diagnostic_bundle()) == 20


def test_every_cell_has_exactly_R_DIAG_replicates():
    counts = {}
    for trial in diag.diagnostic_bundle():
        counts[(trial["arm"], trial["anchor"])] = counts.get(
            (trial["arm"], trial["anchor"]), 0) + 1
    assert len(counts) == 4
    assert set(counts.values()) == {diag.R_DIAG}


def test_trial_ids_are_unique():
    ids = [t["trial_id"] for t in diag.diagnostic_bundle()]
    assert len(set(ids)) == len(ids) == 20


def test_every_trial_is_labelled_non_certifying():
    """§11.1: these outputs must never be readable as main-cohort results."""
    for trial in diag.diagnostic_bundle():
        assert trial["label"] == "non_certifying_diagnostic"


# --- §11.2b batching -------------------------------------------------------

def test_batches_split_by_arm_and_are_ten_each():
    b1, b2 = diag.batch(1), diag.batch(2)
    assert len(b1) == len(b2) == 10
    assert {t["arm"] for t in b1} == {"PROHIBITION_KEPT"}
    assert {t["arm"] for t in b2} == {"PROHIBITION_REMOVED"}


def test_each_batch_contains_both_anchors_whole():
    """The reason batching is by arm: §11.2's rules are all within-arm anchor
    comparisons, so each comparison must live entirely inside one batch. A
    split by anchor would confound the anchor contrast with batch and time."""
    for n in (1, 2):
        anchors = [t["anchor"] for t in diag.batch(n)]
        assert set(anchors) == set(diag.ANCHORS)
        for anchor in diag.ANCHORS:
            assert anchors.count(anchor) == diag.R_DIAG


def test_batches_partition_the_bundle_exactly():
    combined = [t["trial_id"] for t in diag.batch(1) + diag.batch(2)]
    assert sorted(combined) == sorted(t["trial_id"] for t in diag.diagnostic_bundle())


def test_batch_rejects_out_of_range():
    with pytest.raises(diag.DiagnosticError):
        diag.batch(3)


# --- the anchor flip changes the anchor, and only the anchor ---------------

def test_the_fixture_records_the_repositorys_enforced_state():
    """The unflipped level must be the real state, not the counterfactual."""
    assert diag.recorded_anchor(fixture()) == "structural_composition"


def test_flip_sets_the_requested_anchor():
    for anchor in diag.ANCHORS:
        variant = diag.fixture_with_anchor(fixture(), anchor)
        assert diag.recorded_anchor(variant) == anchor


def test_flip_rejects_a_type_outside_the_two_levels():
    for bad in ("functional", "locational", "not_a_type"):
        with pytest.raises(diag.DiagnosticError):
            diag.fixture_with_anchor(fixture(), bad)


def test_flip_changes_exactly_one_field_reconstruction_proof():
    """Rebuild the flipped fixture from the base by touching only the anchor
    field, and require byte equality with what `fixture_with_anchor` produced.
    Anything else that moved shows up as a mismatch."""
    base = fixture()
    flipped = diag.fixture_with_anchor(base, "essential_feature")

    rebuilt = json.loads(json.dumps(base))  # independent deep copy
    for concept in rebuilt["candidate_concepts"]:
        if concept["name"] == diag.CONCEPT:
            for feat in concept["features"]:
                if feat["feature"] == diag.FEATURE:
                    feat["type"] = "essential_feature"

    assert h1a_surface.canonical_json(rebuilt) == h1a_surface.canonical_json(flipped)


def test_flip_leaves_the_base_fixture_untouched():
    """`fixture_with_anchor` must not mutate its argument -- the main cohort
    reads the same object."""
    base = fixture()
    before = h1a_surface.canonical_json(base)
    diag.fixture_with_anchor(base, "essential_feature")
    assert h1a_surface.canonical_json(base) == before


def test_evidence_is_byte_identical_to_the_base_fixture_at_both_anchors():
    """The whole point. Evidence is what the model reads; if it moved with the
    anchor, the diagnostic would measure evidence drift, not anchor effect.

    Anchored to the BASE fixture on purpose. An earlier version of this test
    compared the two variants against *each other* and a mutation test caught
    it leaking: corruption applied identically to both variants keeps them
    equal to each other while both differ from the source. The proposition
    that is actually needed is "unchanged from the fixture", not "the two
    agree" (skills-catalog pattern 10, guard-asserts-the-wrong-proposition)."""
    base_evidence = h1a_surface.canonical_json(fixture()["evidence_sources"])
    for anchor in diag.ANCHORS:
        variant = diag.fixture_with_anchor(fixture(), anchor)
        assert h1a_surface.canonical_json(variant["evidence_sources"]) == base_evidence, anchor


def test_evidence_order_is_the_preregistered_one():
    """P2.1: ev1 -> ev2 -> ev3, identical in both arms and both anchors."""
    for anchor in diag.ANCHORS:
        variant = diag.fixture_with_anchor(fixture(), anchor)
        ids = [i["evidence_id"] for i in variant["evidence_sources"]]
        assert ids == ["ev1", "ev2", "ev3"]


# --- the diagnostic payload obeys the same surface rules as the main cohort -

def test_payloads_differ_only_in_the_recorded_type():
    """Also anchored to an independently built reference payload rather than
    to the other variant -- same reason as the evidence test above."""
    base = fixture()
    base_manifest = h1a_surface.qualify_fixture(base, REPO_ROOT, run_tests=False)
    reference = h1a_surface.build_model_payload(base, base_manifest)
    reference_evidence = h1a_surface.canonical_json(reference["evidence_items"])

    payloads = diag.diagnostic_payloads()
    for anchor, payload in payloads.items():
        assert set(payload) == set(h1a_surface.MODEL_PAYLOAD_KEYS), anchor
        assert h1a_surface.canonical_json(payload["evidence_items"]) == \
               reference_evidence, anchor
        types = [f["type"] for c in payload["candidate_concepts"] for f in c["features"]]
        assert types == [anchor], anchor


def test_diagnostic_payload_never_carries_server_response():
    """C11 applies here too -- the anchor flip must not reopen the structural
    oracle leak by routing around `build_model_payload`."""
    for payload in diag.diagnostic_payloads().values():
        assert "server_response" not in payload
        assert set(payload) == {"candidate_concepts", "evidence_items"}


def test_flipped_variant_introduces_no_oracle_field():
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

    for anchor in diag.ANCHORS:
        walk(diag.fixture_with_anchor(fixture(), anchor))


def test_flipped_payload_carries_no_liveness_or_authority_hint():
    LIVENESS_TOKENS = (
        "stale", "outdated", "obsolete", "superseded", "deprecated",
        "newer", "older", "more recent", "authoritative",
        "낡", "최신", "구식", "권위", "우선",
    )
    for payload in diag.diagnostic_payloads().values():
        blob = h1a_surface.canonical_json(payload)
        for token in LIVENESS_TOKENS:
            assert token not in blob, token


# --- rendering (added after the Q3=B ruling) -------------------------------
#
# The predecessor of this section was `test_module_does_not_render_prompts_yet`,
# which forbade a renderer while the prompt surface was still under external
# adjudication. The Q3 ruling landed, so that guard was retired and replaced by
# the checks below. Freezing and execution remain outside this module.

def test_module_still_does_not_freeze_or_execute():
    for forbidden in ("freeze", "run_trials", "dispatch", "record"):
        assert not hasattr(diag, forbidden), f"{forbidden} does not belong here"


def test_four_cells_render_to_four_distinct_prompts():
    rendered = diag.rendered_cells()
    assert len(rendered) == 4
    assert len(set(rendered.values())) == 4, "two cells rendered identically"


def test_replicates_within_a_cell_are_byte_identical():
    """Nothing in the prompt varies with `replicate`, so all R_DIAG trials in
    a cell must be the same bytes. If they diverge, they are not replicates."""
    payloads = diag.diagnostic_payloads()
    for cell in diag.diagnostic_cells():
        renders = {
            diag.render_diagnostic_prompt(cell["arm"], cell["anchor"], payloads)
            for _ in range(diag.R_DIAG)
        }
        assert len(renders) == 1, cell


def test_only_the_kept_arm_carries_the_liveness_clause():
    rendered = diag.rendered_cells()
    for (arm, anchor), text in rendered.items():
        has_clause = contract.LIVENESS_CLAUSE_TEXT in text
        assert has_clause == (arm == "PROHIBITION_KEPT"), (arm, anchor)


def test_removed_arm_renders_carry_no_residual_prohibition():
    for (arm, anchor), text in diag.rendered_cells().items():
        if arm == "PROHIBITION_REMOVED":
            contract.assert_no_residual_prohibition(text)


def test_same_arm_renders_differ_only_by_the_anchor_value():
    """Holding arm fixed and flipping the anchor, the rendered prompts must
    differ only where the recorded type is serialized -- reconstruction proof,
    not a character diff.

    The `count == 1` assertion is load-bearing: without it a replacement that
    matched nothing (wrong separator spacing, say) would leave `rebuilt == a`,
    and the test would report a real mismatch as a formatting problem or, if
    the two cells ever became identical, pass while proving nothing."""
    rendered = diag.rendered_cells()
    for arm in diag.ARMS:
        a = rendered[(arm, "structural_composition")]
        b = rendered[(arm, "essential_feature")]
        needle = '"type": "structural_composition"'
        assert a.count(needle) == 1, (arm, "anchor field not uniquely locatable")
        rebuilt = a.replace(needle, '"type": "essential_feature"', 1)
        assert rebuilt != a, (arm, "replacement was a no-op")
        assert rebuilt == b, arm


def test_same_anchor_renders_differ_only_by_the_liveness_clause():
    rendered = diag.rendered_cells()
    for anchor in diag.ANCHORS:
        kept = rendered[("PROHIBITION_KEPT", anchor)]
        removed = rendered[("PROHIBITION_REMOVED", anchor)]
        ok, detail = contract.diff_is_restricted_to_the_liveness_clause(kept, removed)
        assert ok, (anchor, detail)


def test_render_rejects_unknown_arm_or_anchor():
    with pytest.raises(diag.DiagnosticError):
        diag.render_diagnostic_prompt("CONTROL_REPO", "structural_composition")
    with pytest.raises(diag.DiagnosticError):
        diag.render_diagnostic_prompt("PROHIBITION_KEPT", "functional")


# --- the trial subject's system prompt -------------------------------------

AGENT_DEF = HERE / "h1a-decider.md"


def test_one_agent_definition_serves_both_arms():
    """H3 needed one agent per arm because the schemas differed. Here the Q3
    template inlines `h1a_observation_v1` in the prompt, so both arms can and
    MUST share a system prompt -- a per-arm system prompt would be a second
    manipulated variable riding alongside the liveness clause."""
    assert diag.AGENT_TYPE == "h1a-decider"
    assert AGENT_DEF.exists()
    body = AGENT_DEF.read_text(encoding="utf-8")
    assert "tools: []" in body
    assert f"name: {diag.AGENT_TYPE}" in body


def test_agent_definition_names_no_arm_and_no_anchor():
    """If the system prompt mentioned an arm or an anchor level, the subject
    would know which condition it is in."""
    body = AGENT_DEF.read_text(encoding="utf-8")
    for token in ("PROHIBITION_KEPT", "PROHIBITION_REMOVED",
                  "structural_composition", "essential_feature"):
        assert token not in body, token


def test_agent_definition_does_not_duplicate_the_schema():
    """The schema lives in the prompt (Q3 template). Restating it in the
    system prompt would create two copies that can drift, and the model would
    have no way to know which governs."""
    body = AGENT_DEF.read_text(encoding="utf-8")
    for token in ('"decision"', '"selected_type"', "additionalProperties", "enum"):
        assert token not in body, token


def test_rendered_prompt_carries_no_liveness_hint_beyond_the_manipulation():
    """The payload half must stay clean in every cell -- the only place
    liveness vocabulary may appear is the KEPT arm's manipulated clause."""
    for (arm, anchor), text in diag.rendered_cells().items():
        if arm == "PROHIBITION_KEPT":
            text = text.replace(contract.LIVENESS_CLAUSE_TEXT, "")
        for token in ("stale", "outdated", "obsolete", "superseded", "deprecated",
                      "낡", "구식"):
            assert token not in text, (arm, anchor, token)
