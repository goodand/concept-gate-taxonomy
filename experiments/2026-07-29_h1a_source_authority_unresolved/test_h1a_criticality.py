"""D-H1a-17's classification, measured rather than accepted.

The ruling split one enum into two and classified three families as
`causal_semantic_critical: true, canonical_audit_critical: false` -- the
semantic proposition matters, but requiring the canonical DSL -> compiler path
to certify it does not, because independent routes already do.

That is a COUNTERFACTUAL claim: remove the canonical route and ask whether a
false causal claim can now pass. This repo does not accept counterfactual
claims on a ruling's word -- Q13.3's own gate exists because a condition that
merely restated the primary result got through five reviews. So the
counterfactual is run here.

WHAT THE FIRST MEASUREMENT GOT WRONG, KEPT AS A TEST
-----------------------------------------------------
Deleting the clause from the RENDERED STRING is caught only by the compiler;
`assert_9` re-renders from the module and structurally cannot see a
post-render edit. That looked like a refutation of the ruling. It was not --
it was the wrong threat model. Canonical/renderer drift and post-render
tampering are different failures with different independent routes:

    canonical drift    -> assert_9 golden contract  (compiler-independent)
    post-render edit   -> manifest rendered_prompt_sha256 (compiler-independent)

Both are pinned below, because "which route covers which failure" is the whole
content of the audit_only classification.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_criticality_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


sc = _load("sc", "_h1a_semantic_compiler.py")
policy = _load("policy", "_h1a_policy.py")
contract = _load("contract", "_h1a_contract.py")

SENTENCE_1 = ("Within the supplied packet, a decision basis may be considered unless this\n"
              "prompt explicitly prohibits it. ")


# --- the two-layer split itself -------------------------------------------

def test_the_two_criticality_layers_are_distinct_claims():
    """D-H1a-17: one enum was carrying two different propositions."""
    assert sc.CAUSAL_SEMANTIC_CRITICAL
    assert sc.CANONICAL_AUDIT_CRITICAL <= sc.CAUSAL_SEMANTIC_CRITICAL, (
        "a family cannot require canonical certification without the "
        "proposition itself mattering"
    )


def test_target_critical_stays_the_causal_layer_for_existing_callers():
    assert sc.TARGET_CRITICAL == sc.CAUSAL_SEMANTIC_CRITICAL


def test_every_causal_critical_family_records_its_certification_path():
    """`canonical_audit_critical: false` is only honest if some other route is
    named. An unnamed route is an assumption, not evidence."""
    for family in sc.CAUSAL_SEMANTIC_CRITICAL:
        assert family in sc.CERTIFICATION_PATH, family
        assert len(sc.CERTIFICATION_PATH[family]) > 30, family


# --- the counterfactual, per failure mode ---------------------------------

def test_canonical_drift_is_caught_without_the_compiler():
    """Failure mode (a): the renderer stops emitting the default permission.

    This is the realistic drift, and `assert_9` catches it by comparing the
    re-rendered block against an independently frozen golden contract. That is
    the compiler-independent route the audit_only classification rests on."""
    original = policy.GLOBAL_DEFAULT_PERMISSION_TEXT
    assert SENTENCE_1 in original
    policy.GLOBAL_DEFAULT_PERMISSION_TEXT = original.replace(SENTENCE_1, "", 1)
    try:
        with pytest.raises(policy.PolicyContractError, match="golden contract"):
            policy.assert_9_default_permission_is_byte_identical_across_arms()
    finally:
        policy.GLOBAL_DEFAULT_PERMISSION_TEXT = original


def test_post_render_edits_are_caught_by_the_frozen_manifest_hash():
    """Failure mode (b): the text changes after rendering.

    `assert_9` cannot see this by construction. The frozen cohort manifest
    can -- it pins `rendered_prompt_sha256` per trial, so an edited prompt no
    longer matches what was frozen. Also compiler-independent.

    Asserting the FIELD EXISTS would not establish that, which is what this
    test did in its first form. A present-but-decorative hash is
    indistinguishable from a working one under that assertion -- the exact
    defect class this repo has been burned by (assert_5, the forgeable
    receipts). So the route is exercised: the frozen hash must reproduce from
    the frozen prompt, and a one-character edit must break it."""
    surface = _load("surface", "_h1a_surface.py")
    cohort = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    trial = cohort["trials"][0]
    frozen_hash = trial["manifest"]["rendered_prompt_sha256"]
    frozen_prompt = cohort["rendered_prompts"][trial["arm"]]

    # precision: the pinned hash actually describes the pinned prompt
    assert surface.sha256_of(frozen_prompt) == frozen_hash, (
        "the manifest hash does not reproduce from the frozen prompt, so it "
        "certifies nothing"
    )
    # recall: a post-render edit is detectable through it
    assert surface.sha256_of(frozen_prompt + " ") != frozen_hash


def test_the_compiler_also_catches_it_which_is_why_it_is_redundant_not_useless():
    """The compiler route works -- that is precisely why it is redundant here.
    `audit_only` means 'another route already suffices', not 'this route is
    broken'."""
    import _h1a_compiler_capability as cap
    rendered = contract.render_arm(contract.load_h1a_native_template(),
                                   "PROHIBITION_REMOVED")
    mutated = rendered.replace(SENTENCE_1, "", 1)
    assert mutated != rendered

    proven = cap.proven_families()
    graph = sc.compile_policy_graph(mutated, "removed", proven_families=proven)
    state = next(c["state"] for c in graph["claims"]
                 if c["policy_id"] == sc.GLOBAL_DEFAULT_PERMISSION)
    assert state != sc.PRESENT


def test_the_semantic_proposition_itself_is_still_treated_as_critical():
    """D-H1a-17 classified the canonicalization as audit_only, NOT the
    proposition. Dropping GLOBAL_DEFAULT_PERMISSION from the causal layer
    would be reading the ruling backwards."""
    assert sc.GLOBAL_DEFAULT_PERMISSION in sc.CAUSAL_SEMANTIC_CRITICAL
    assert sc.RECORDED_FIELDS_ACCESS in sc.CAUSAL_SEMANTIC_CRITICAL
    assert sc.CONFLICT_TO_DEFER_MAPPING in sc.CAUSAL_SEMANTIC_CRITICAL


# --- the premise the ruling attached to flipping the flag -----------------

def test_no_freeze_condition_other_than_the_review_flag_is_unmet():
    """The ruling permitted setting INDEPENDENT_SEMANTIC_REVIEW_PASSED only
    'assuming no other BLOCKER/MAJOR'. That premise is machine-checkable, so
    it is checked rather than assumed.

    The flag is patched in memory only; the module on disk is untouched."""
    template = contract.load_h1a_native_template()
    rendered = {arm: contract.render_arm(template, arm) for arm in contract.ARMS}

    original = policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED

    policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED = False
    try:
        with pytest.raises(policy.FreezeGateBlocked, match="condition 5"):
            policy.assert_freezable(rendered, contract.LIVENESS_CLAUSE_TEXT,
                                    source_attributes_visible=True,
                                    hard_defer_mapping=False)
    finally:
        policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED = original

    policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED = True
    try:
        result = policy.assert_freezable(rendered, contract.LIVENESS_CLAUSE_TEXT,
                                         source_attributes_visible=True,
                                         hard_defer_mapping=False)
    finally:
        policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED = original

    assert result["removed_target_state_is_allowed_by_default"] is True
    assert result["removed_target_state_is_not_unspecified"] is True
    assert result["target_mechanism_contrast"] is True
