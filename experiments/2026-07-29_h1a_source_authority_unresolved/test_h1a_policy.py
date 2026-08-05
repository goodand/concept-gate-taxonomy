"""Tests for the decision-basis policy contract (D-H1a-10 Q10.2 / D-H1a-11).

Both directions, per skills-catalog pattern 8 (`checker-recall-and-precision`):
a guard shown only to pass on good input has unknown recall, and this
experiment already lost a cohort to exactly that.

The load-bearing test is `test_the_actual_nonidentifying_cohort_prompt_is_rejected`
-- it feeds the real frozen bytes of the 40-trial cohort D-H1a-10 ruled
non-identifying and requires rejection. Synthetic mutations show the guard CAN
fire; that test shows it fires on what actually happened.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    """Load a sibling module under a unique sys.modules key.

    Experiment folders here deliberately hold same-named modules as frozen
    copies, and one experiment has already been observed running on another's
    code because whichever loaded first won `sys.modules`. Unique keys, always.
    """
    key = f"_h1a_policy_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


policy = _load("policy", "_h1a_policy.py")
contract = _load("contract", "_h1a_contract.py")

Q1 = contract.LIVENESS_CLAUSE_TEXT


def _repaired_rendered() -> dict[str, str]:
    """The post-repair arms as this module would render them.

    Q1's clause is appended to KEPT only, mirroring what _h1a_contract.py does
    to the full template. Used to exercise the rendered-text assertions without
    depending on the template file, which is not yet rewired.
    """
    out = {}
    for arm in policy.ARMS:
        text = policy.render_policy_text(arm)
        if arm == "PROHIBITION_KEPT":
            text = text + "\n\n" + Q1
        out[arm] = text
    return out


@pytest.fixture
def clean_policy():
    original = copy.deepcopy(policy.DECISION_BASIS_POLICY)
    yield policy.DECISION_BASIS_POLICY
    policy.DECISION_BASIS_POLICY.clear()
    policy.DECISION_BASIS_POLICY.update(original)


# ==========================================================================
# precision -- the frozen table and all twelve assertions
# ==========================================================================
def test_all_twelve_structural_assertions_pass():
    policy.assert_structural_no_args()
    rendered = _repaired_rendered()
    policy.assert_5_no_duplicate_forbidding_carrier(rendered, Q1)
    policy.assert_6b_removed_prose_has_no_target_prohibition(rendered)
    policy.assert_10_q1_clause_is_kept_only_and_unchanged(rendered, Q1)
    policy.assert_11_removed_has_no_axis_specific_permission_text(rendered)


def test_table_matches_the_ruling_sec_7_verbatim():
    """D-H1a-12 sec 5 is a preregistration device; pin it cell by cell.

    RETARGETED from D-H1a-11 sec 7 (2026-08-05). Q12=F replaced that table:
    `outside_knowledge` is split into `outside_domain_knowledge` +
    `external_source_retrieval` (both arms forbidden, DOMAIN_KNOWLEDGE_BOUNDARY)
    and the four former target axes become subaxes of `source_meta_reasoning`,
    which Q1 alone governs. The proposition this test pins is unchanged --
    every axis x arm has exactly the carrier the ruling assigns -- only the
    ruling it pins moved.
    """
    expected = {
        "evidence_count": ("Q7_NON_TARGET_TIEBREAKER", "Q7_NON_TARGET_TIEBREAKER"),
        "source_order": ("Q7_NON_TARGET_TIEBREAKER", "Q7_NON_TARGET_TIEBREAKER"),
        "outside_domain_knowledge": ("DOMAIN_KNOWLEDGE_BOUNDARY",
                                     "DOMAIN_KNOWLEDGE_BOUNDARY"),
        "external_source_retrieval": ("DOMAIN_KNOWLEDGE_BOUNDARY",
                                      "DOMAIN_KNOWLEDGE_BOUNDARY"),
        "source_meta_reasoning": ("Q1_LIVENESS_CLAUSE", "GLOBAL_DEFAULT_PERMISSION"),
    }
    assert set(expected) == set(policy.AXES)
    for axis, (kept_carrier, removed_carrier) in expected.items():
        assert policy.carrier_of(axis, "PROHIBITION_KEPT") == kept_carrier
        assert policy.carrier_of(axis, "PROHIBITION_REMOVED") == removed_carrier


def test_outside_knowledge_carrier_is_q7_only_not_the_packet_boundary():
    """D-H1a-11 sec 8: scope constraints are not carriers.

    Axis renamed by D-H1a-12 (outside_knowledge -> outside_domain_knowledge)
    and its carrier moved from Q7 to the new DOMAIN_KNOWLEDGE_BOUNDARY. The
    proposition is unchanged: a scope constraint is never a carrier.
    """
    for arm in policy.ARMS:
        assert policy.carrier_of("outside_domain_knowledge", arm) == policy.CARRIER_DOMAIN
    assert "PACKET_ONLY" in policy.SCOPE_CONSTRAINTS
    assert "PACKET_ONLY" not in policy.CARRIERS


def test_domain_knowledge_and_source_meta_are_siblings_not_nested():
    """D-H1a-12 sec 5: the whole point of Q12=F.

    source_meta_reasoning must NOT be subsumed by outside_domain_knowledge --
    that subsumption is what made the previous cohort nonidentifying. They are
    separate top-level axes with different carriers, and the target axis is
    the one Q1 alone governs.
    """
    assert "outside_domain_knowledge" in policy.AXES
    assert "source_meta_reasoning" in policy.AXES
    assert policy.TARGET_AXES == frozenset({"source_meta_reasoning"})
    for arm in policy.ARMS:
        assert policy.carrier_of("outside_domain_knowledge", arm) == policy.CARRIER_DOMAIN
    # The domain boundary is arm-invariant; the target axis is not.
    assert policy.state_of("outside_domain_knowledge", "PROHIBITION_KEPT") == \
        policy.state_of("outside_domain_knowledge", "PROHIBITION_REMOVED")
    assert policy.state_of("source_meta_reasoning", "PROHIBITION_KEPT") != \
        policy.state_of("source_meta_reasoning", "PROHIBITION_REMOVED")
    # The four former target axes survive as declared subaxes.
    assert set(policy.SUBAXES["source_meta_reasoning"]) == {
        "source_kind_priority", "recency", "authority", "liveness"}


def test_removed_target_state_is_allowed_by_default_not_unspecified():
    """D-H1a-11 sec 9 says this explicitly, and it is the point of Q11=D."""
    for axis in sorted(policy.TARGET_AXES):
        assert policy.state_of(axis, "PROHIBITION_REMOVED") == policy.ALLOWED_BY_DEFAULT
        assert policy.state_of(axis, "PROHIBITION_REMOVED") != policy.UNSPECIFIED


def test_target_and_nontarget_partition_the_axes():
    assert policy.TARGET_AXES | policy.NONTARGET_AXES == set(policy.AXES)
    assert not (policy.TARGET_AXES & policy.NONTARGET_AXES)


# ==========================================================================
# renderer -- Q11=D
# ==========================================================================
def test_default_permission_is_emitted_in_both_arms_byte_identically():
    policy.assert_9_default_permission_is_byte_identical_across_arms()
    for arm in policy.ARMS:
        blocks = dict(policy.render_policy_block(arm))
        assert blocks[policy.CARRIER_DEFAULT] == policy.GLOBAL_DEFAULT_PERMISSION_TEXT


def test_default_permission_text_matches_the_ruling_bytes():
    expected = (
        "Within the supplied packet, a decision basis may be considered unless this\n"
        "prompt explicitly prohibits it. Permission to consider a basis does not by\n"
        "itself warrant selecting a type or favor either allowed type."
    )
    assert policy.GLOBAL_DEFAULT_PERMISSION_TEXT == expected


def test_default_permission_carries_the_demand_neutralizer():
    """The second sentence must deny that permission encourages selecting."""
    text = policy._normalize_ws(policy.GLOBAL_DEFAULT_PERMISSION_TEXT)
    assert "does not by itself warrant selecting a type" in text
    assert "favor either allowed type" in text
    assert policy.POLICY_DEFAULTS["packet_internal_decision_basis"]["non_directive"] is True


def test_common_q7_names_all_three_nontarget_axes_in_both_arms():
    """RETARGETED by D-H1a-12 sec 4: the single Q7 bullet became THREE
    sentences with different carriers. `outside knowledge` is no longer in the
    tie-breaker sentence -- it moved to DOMAIN_KNOWLEDGE_BOUNDARY. Each
    carrier is now checked against its own sentence, so a sentence carrying
    the wrong axis is still caught.
    """
    for arm in policy.ARMS:
        blocks = dict(
            (c, policy._normalize_ws(txt))
            for c, txt in policy.render_policy_block(arm)
        )
        for phrase in ("evidence item count", "source order"):
            assert policy._normalize_ws(phrase) in blocks[policy.CARRIER_Q7], \
                f"{arm}: {phrase!r} missing from the tie-breaker sentence"
        # The tie-breaker sentence must NOT name the domain axes any more.
        assert "outside domain" not in blocks[policy.CARRIER_Q7]
        for phrase in ("outside domain or ontology knowledge", "external sources"):
            assert policy._normalize_ws(phrase) in blocks[policy.CARRIER_DOMAIN], \
                f"{arm}: {phrase!r} missing from the domain-boundary sentence"


def test_common_q7_omits_every_target_axis():
    policy.assert_12_common_q7_excludes_target_axis_strings_and_aliases()


def test_the_two_arms_generated_blocks_are_identical():
    """Q11=D: the generated block carries NO arm difference.

    The entire contrast lives in Q1's clause, which _h1a_contract.py inserts.
    """
    a = policy.render_policy_text("PROHIBITION_KEPT")
    b = policy.render_policy_text("PROHIBITION_REMOVED")
    assert a == b


def test_removed_has_no_axis_specific_permission_sentence():
    policy.assert_11_removed_has_no_axis_specific_permission_text(_repaired_rendered())


def test_renderer_is_deterministic():
    for arm in policy.ARMS:
        assert policy.render_policy_text(arm) == policy.render_policy_text(arm)


def test_every_rendered_block_is_traceable_to_a_carrier():
    """Q10.2 requirement 5."""
    for arm in policy.ARMS:
        for carrier, text in policy.render_policy_block(arm):
            # D-H1a-12 sec 4 added a scope-disambiguation sentence. It is
            # deliberately NOT a carrier (it flips no axis), but it still must
            # be traceable to a declared ID -- untraceable prose is exactly
            # what Q10.2 requirement 5 forbids.
            assert carrier in policy.CARRIERS or carrier in policy.SCOPE_CONSTRAINTS
            assert text.strip()


# ==========================================================================
# effective-state resolution + deductive check
# ==========================================================================
def test_effective_state_resolves_the_default_for_removed_target_axes():
    for axis in sorted(policy.TARGET_AXES):
        assert policy.effective_state(axis, "PROHIBITION_KEPT") == policy.EXPLICITLY_FORBIDDEN
        assert policy.effective_state(axis, "PROHIBITION_REMOVED") == policy.ALLOWED_BY_DEFAULT


def test_deductive_check_proves_the_repair_creates_a_contrast():
    r = policy.assert_deductive_check()
    for key in (
        "kept_target_forbidden",
        "removed_target_allowed",
        "target_mechanism_contrast",
        "nontarget_constraints_equal",
        "removed_target_state_is_allowed_by_default",
        "removed_target_state_is_not_unspecified",
        "proof_repair_creates_contrast",
    ):
        assert r[key] is True, key


def test_m_allowed_matches_the_rulings_repair_table():
    assert policy.target_mechanism_allowed("PROHIBITION_KEPT") is False
    assert policy.target_mechanism_allowed("PROHIBITION_REMOVED") is True


def test_truth_table_opens_exactly_one_cell():
    table = policy.truth_table()
    assert len(table) == 4
    opened = [c for c in table if c["m_allowed"]]
    assert opened == [{"q1_forbids": False, "q7_forbids": False, "m_allowed": True}]


# ==========================================================================
# freeze gate -- conjunction, blocked on the unverifiable condition
# ==========================================================================
def test_freeze_is_blocked_until_the_independent_review_is_recorded():
    assert policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED is False, (
        "if this flips, the review must have been run and its report committed "
        "in the same change -- do not flip it to make this test pass"
    )
    with pytest.raises(policy.FreezeGateBlocked, match="independent semantic review"):
        policy.assert_freezable(_repaired_rendered(), Q1)


def test_freeze_gate_runs_the_machine_checkable_conditions_before_failing():
    """The review condition must not mask a structural failure.

    If a structural condition is broken, the gate must report THAT, not the
    review flag -- otherwise a real defect hides behind a pending checkbox.
    """
    original = copy.deepcopy(policy.DECISION_BASIS_POLICY)
    try:
        policy.DECISION_BASIS_POLICY["source_meta_reasoning"]["removed"] = {
            "state": policy.EXPLICITLY_FORBIDDEN, "carrier": policy.CARRIER_Q7,
        }
        with pytest.raises(policy.PolicyContractError) as exc:
            policy.assert_freezable(_repaired_rendered(), Q1)
        assert "independent semantic review" not in str(exc.value)
    finally:
        policy.DECISION_BASIS_POLICY.clear()
        policy.DECISION_BASIS_POLICY.update(original)


# ==========================================================================
# recall -- mutations must be CAUGHT
# ==========================================================================
def test_mutation_carrier_as_a_collection_is_caught(clean_policy):
    """D-H1a-11 sec 8: exactly one carrier per axis x arm."""
    clean_policy["source_meta_reasoning"]["kept"]["carrier"] = (policy.CARRIER_Q1, policy.CARRIER_Q7)
    with pytest.raises(policy.PolicyContractError, match=r"\[2\]"):
        policy.assert_2_exactly_one_valid_carrier_per_axis_arm()


def test_mutation_restoring_a_target_axis_to_q7_in_kept_is_caught(clean_policy):
    """Q11.1=A forbids this; it is the Q10 duplicate-carrier structure."""
    clean_policy["source_meta_reasoning"]["kept"]["carrier"] = policy.CARRIER_Q7
    with pytest.raises(policy.PolicyContractError, match=r"\[7\]"):
        policy.assert_7_kept_target_axes_are_carried_only_by_q1()
    # D-H1a-12 note: assertion 12 no longer fires from this mutation alone.
    # With the typed-scope split the tie-breaker sentence enumerates only
    # non-target axes, so re-pointing the target axis's carrier changes the
    # POLICY without changing that sentence's PROSE. Assertion 12's job (the
    # rendered common sentence must not name a target axis) is pinned by
    # test_common_q7_names_all_three_nontarget_axes_in_both_arms and by
    # test_mutation_paraphrased_residual_prohibition_is_caught instead.
    # Recorded rather than silently dropped -- see D-H1a-12 sec 8, which
    # explicitly demotes lexical alias scanning to lint and requires the
    # semantic check to carry certification.


def test_mutation_forbidding_a_target_axis_in_removed_is_caught(clean_policy):
    clean_policy["source_meta_reasoning"]["removed"] = {
        "state": policy.EXPLICITLY_FORBIDDEN, "carrier": policy.CARRIER_Q7,
    }
    with pytest.raises(policy.PolicyContractError, match=r"\[6\]"):
        policy.assert_6_removed_target_axes_have_no_forbidding_carrier()


def test_mutation_allowed_by_default_on_a_non_default_carrier_is_caught(clean_policy):
    clean_policy["source_meta_reasoning"]["removed"]["carrier"] = policy.CARRIER_Q7
    with pytest.raises(policy.PolicyContractError, match=r"\[4\]"):
        policy.assert_4_default_permission_states_use_the_default_carrier()


def test_mutation_forbidden_state_on_the_default_carrier_is_caught(clean_policy):
    clean_policy["source_order"]["kept"] = {
        "state": policy.EXPLICITLY_FORBIDDEN, "carrier": policy.CARRIER_DEFAULT,
    }
    with pytest.raises(policy.PolicyContractError, match=r"\[3\]"):
        policy.assert_3_forbidden_states_use_forbidding_carriers()


def test_mutation_unspecified_removed_target_state_is_caught(clean_policy):
    """Q11=D explicitly rejects `unspecified` -- that was option A."""
    clean_policy["source_meta_reasoning"]["removed"]["state"] = policy.UNSPECIFIED
    with pytest.raises(policy.PolicyContractError):
        policy.assert_deductive_check()


def test_mutation_nontarget_axis_made_arm_varying_is_caught(clean_policy):
    clean_policy["source_order"]["removed"] = {
        "state": policy.ALLOWED_BY_DEFAULT, "carrier": policy.CARRIER_DEFAULT,
    }
    with pytest.raises(policy.PolicyContractError, match=r"\[8\]"):
        policy.assert_8_nontarget_axes_identical_in_state_and_carrier()


def test_mutation_invalid_state_value_is_caught(clean_policy):
    clean_policy["source_meta_reasoning"]["kept"]["state"] = "sort_of_forbidden"
    with pytest.raises(policy.PolicyContractError, match=r"\[1\]"):
        policy.assert_1_every_axis_arm_has_a_state()


def test_mutation_q1_clause_leaking_into_removed_is_caught():
    rendered = _repaired_rendered()
    rendered["PROHIBITION_REMOVED"] = rendered["PROHIBITION_REMOVED"] + "\n" + Q1
    with pytest.raises(policy.PolicyContractError, match=r"\[10\]"):
        policy.assert_10_q1_clause_is_kept_only_and_unchanged(rendered, Q1)


def test_mutation_axis_specific_permission_in_removed_is_caught():
    rendered = _repaired_rendered()
    rendered["PROHIBITION_REMOVED"] += (
        "\n- You may take source_kind, recency, authority, or liveness into account."
    )
    with pytest.raises(policy.PolicyContractError, match=r"\[11\]"):
        policy.assert_11_removed_has_no_axis_specific_permission_text(rendered)


def test_assert_5_actually_reads_rendered_and_catches_a_duplicate_carrier():
    """Regression for the vacuous-guard defect an independent review found.

    The original assert_5 never referenced its `rendered` parameter and both
    branches were tautologically unreachable (see the function's own
    docstring for the derivation). A poisoned KEPT arm carrying a second,
    independent prohibition of a Q1-carried axis passed it. This pins that the
    fixed version (a) passes on the real rendered template and (b) actually
    fires on that exact poisoned input -- on the REAL rendered arms, not a
    synthetic fixture, so a regression here means the fix regressed against
    the artifact that matters.
    """
    template = contract.load_h1a_native_template()
    kept = contract.render_arm(template, "PROHIBITION_KEPT")
    removed = contract.render_arm(template, "PROHIBITION_REMOVED")

    # (a) the real, unmodified prompts must pass.
    policy.assert_5_no_duplicate_forbidding_carrier(
        {"PROHIBITION_KEPT": kept, "PROHIBITION_REMOVED": removed}, Q1
    )

    # (b) the reviewer's exact poisoning must be caught.
    poisoned_kept = kept + "\n- Do not use recency or authority to decide."
    with pytest.raises(policy.PolicyContractError, match=r"\[5\]"):
        policy.assert_5_no_duplicate_forbidding_carrier(
            {"PROHIBITION_KEPT": poisoned_kept, "PROHIBITION_REMOVED": removed}, Q1
        )


def test_assert_5_does_not_false_positive_on_the_scope_constraint_sentence():
    """The packet-boundary sentence legitimately says 'or external sources',
    which co-occurs with outside_knowledge's tokens under the same
    verb-proximity window assert_5 uses. That overlap is ruled EXPECTED
    (D-H1a-11 sec 8: scope constraints are not carriers), so it must not be
    flagged -- this was the first thing the corrected assert_5 got wrong
    before SCOPE_CONSTRAINT_TEXT was excluded from the scan.
    """
    template = contract.load_h1a_native_template()
    rendered = {
        arm: contract.render_arm(template, arm) for arm in contract.ARMS
    }
    policy.assert_5_no_duplicate_forbidding_carrier(rendered, Q1)  # must not raise


def test_mutation_paraphrased_residual_prohibition_is_caught():
    """The case a closed keyword list cannot certify.

    Q10.2 forbids proving absence lexically because an equivalent prohibition
    can be paraphrased. This guard asks whether a target axis is FORBIDDEN in
    an arm that declares it permitted, so novel phrasing does not help it hide.
    """
    rendered = _repaired_rendered()
    rendered["PROHIBITION_REMOVED"] += (
        "\n- Do not use the authority of a source when the packet is in tension."
    )
    with pytest.raises(policy.PolicyContractError, match="residual prohibition"):
        policy.assert_6b_removed_prose_has_no_target_prohibition(rendered)


def test_wrapping_cannot_hide_an_axis_from_the_checker():
    """Regression for a false negative the 76-column wrapping introduced.

    Without whitespace normalization the presence check missed "outside
    knowledge" the moment the renderer began wrapping -- the guard would report
    an axis absent while it sat in the prompt, split across two lines.
    """
    assert policy._normalize_ws("outside\n  domain") == "outside domain"
    for arm in policy.ARMS:
        # RETARGETED by D-H1a-12 sec 4: `outside knowledge` moved out of the
        # tie-breaker sentence into DOMAIN_KNOWLEDGE_BOUNDARY. The proposition
        # is unchanged -- a multi-word axis token split by the 76-column wrap
        # must still be found -- so it is now checked on the sentence that
        # actually carries such a token.
        raw = " ".join(
            txt for c, txt in policy.render_policy_block(arm)
            if c == policy.CARRIER_DOMAIN
        )
        assert "\n" in raw, "the domain-boundary bullet should be hard-wrapped"
        assert "outside domain or ontology knowledge" in policy._normalize_ws(raw)


# ==========================================================================
# the load-bearing regression: the real non-identifying cohort is rejected
# ==========================================================================
def test_the_actual_nonidentifying_cohort_prompt_is_rejected():
    """Feed the frozen bytes of the ruled-non-identifying cohort to the new guard.

    `cohort_prompts.json` is the manifest of the 40 trials that ran on
    2026-08-03 and that D-H1a-10 ruled non-identifying. Under the OLD guard,
    `assert_no_residual_prohibition` passed on these exact bytes and
    `test_guard_precision_the_clean_template_passes` certified them clean.

    The new guard must reject them. If this ever stops failing on the old
    bytes, the raise ordered by Q10.2 has been undone.
    """
    manifest = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    rendered = manifest["rendered_prompts"]
    assert set(rendered) == set(policy.ARMS)

    # Sanity: these really are the pre-repair bytes.
    for arm in policy.ARMS:
        low = rendered[arm].lower()
        for phrase in ("recency", "authority", "liveness", "source_kind"):
            assert phrase in low, (
                f"{arm}: {phrase!r} absent -- cohort_prompts.json is no longer "
                f"the pre-repair manifest, so this test is testing nothing"
            )

    with pytest.raises(policy.PolicyContractError, match="residual prohibition"):
        policy.assert_6b_removed_prose_has_no_target_prohibition(rendered)


def test_old_guard_still_passes_those_same_bytes():
    """Pin the contrast so the improvement is documented rather than asserted.

    Not a defence of the old guard -- evidence that the two guards assert
    different propositions, which is the whole finding behind Q10.2.
    """
    manifest = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    removed = manifest["rendered_prompts"]["PROHIBITION_REMOVED"]
    contract.assert_no_residual_prohibition(removed)  # passes, as it always did
