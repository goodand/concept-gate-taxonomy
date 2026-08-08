"""Tests for the decision-basis policy contract (D-H1a-10 Q10.2).

Both directions, per skills-catalog pattern 8 (`checker-recall-and-precision`):
a guard that has only been shown to pass on good input has unknown recall, and
this experiment already lost a cohort to exactly that.

The load-bearing test here is
`test_the_actual_nonidentifying_cohort_prompt_is_rejected` -- it feeds the real
frozen bytes of the 40-trial cohort that D-H1a-10 ruled non-identifying into the
new guard and requires rejection. Synthetic mutations show the guard *can* fire;
that test shows it fires on what actually happened.
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

    Experiment folders in this repo deliberately hold same-named modules
    (`_cert_core.py`, `evaluate.py`, ...) as byte-identical frozen copies, and
    one experiment has already been observed running on another's code because
    whichever loaded first won `sys.modules`. Unique keys, always.
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


@pytest.fixture
def clean_policy():
    """Restore DECISION_BASIS_POLICY after a mutation test."""
    original = copy.deepcopy(policy.DECISION_BASIS_POLICY)
    yield policy.DECISION_BASIS_POLICY
    policy.DECISION_BASIS_POLICY.clear()
    policy.DECISION_BASIS_POLICY.update(original)


# ==========================================================================
# precision -- the declared policy is internally consistent
# ==========================================================================
def test_all_axes_declare_both_arms_and_carriers():
    for axis in policy.AXES:
        p = policy.DECISION_BASIS_POLICY[axis]
        assert p["kept"] in (policy.FORBIDDEN, policy.ALLOWED)
        assert p["removed"] in (policy.FORBIDDEN, policy.ALLOWED)
        assert p["carriers"], f"{axis} declares no carrier"
        for c in p["carriers"]:
            assert c in policy.CARRIERS, f"{axis} declares unknown carrier {c!r}"


def test_structural_assertions_pass_on_the_declared_policy():
    policy.assert_target_axis_states()
    policy.assert_nontarget_axes_are_arm_invariant()
    policy.assert_arm_difference_is_exactly_the_target_set()
    policy.assert_manipulated_axes_have_exactly_one_carrier()


def test_target_and_nontarget_partition_the_axes():
    assert policy.TARGET_AXES | policy.NONTARGET_AXES == set(policy.AXES)
    assert not (policy.TARGET_AXES & policy.NONTARGET_AXES)


def test_r1_target_set_is_exactly_the_four_axes_the_ruling_names():
    assert policy.TARGET_AXES == {
        "source_kind_priority", "recency", "authority", "liveness",
    }


def test_r1_retains_exactly_the_three_nontarget_axes():
    assert policy.NONTARGET_AXES == {
        "evidence_count", "source_order", "outside_knowledge",
    }


# ==========================================================================
# deductive check -- reproduces D-H1a-10 sec 3 rather than restating it
# ==========================================================================
def test_deductive_check_passes_and_reports_contrast():
    r = policy.assert_deductive_check()
    assert r["kept_target_forbidden"] is True
    assert r["removed_target_allowed"] is True
    assert r["nontarget_constraints_equal"] is True
    assert r["no_unsatisfiable_combination"] is True
    assert r["target_mechanism_contrast"] is True
    assert r["proof_repair_creates_contrast"] is True


def test_m_allowed_matches_the_rulings_repair_table():
    # D-H1a-10-R1: KEPT False, REMOVED True.
    assert policy.target_mechanism_allowed("PROHIBITION_KEPT") is False
    assert policy.target_mechanism_allowed("PROHIBITION_REMOVED") is True


def test_truth_table_opens_exactly_one_cell():
    table = policy.truth_table()
    assert len(table) == 4
    opened = [c for c in table if c["m_allowed"]]
    assert len(opened) == 1
    assert opened[0] == {"q1_forbids": False, "q7_forbids": False, "m_allowed": True}


# ==========================================================================
# renderer
# ==========================================================================
def test_nontarget_bullet_names_all_three_axes_in_both_arms():
    """Compared whitespace-normalized: the bullet wraps at 76 columns, so a
    two-word phrase legitimately straddles a newline plus indent."""
    for arm in policy.ARMS:
        text = policy._normalize_ws(policy.render_policy_text(arm, allowed_rendering="silence"))
        for phrase in ("evidence item count", "source order", "outside knowledge"):
            assert policy._normalize_ws(phrase) in text, f"{arm}: {phrase!r} missing"


def test_rendered_bullet_omits_every_target_axis_r1():
    """R1's actual edit: the four target axes leave the COMMON list."""
    for arm in policy.ARMS:
        text = policy._normalize_ws(policy.render_policy_text(arm, allowed_rendering="silence"))
        for phrase in ("source_kind priority", "recency", "authority", "liveness"):
            assert policy._normalize_ws(phrase) not in text, (
                f"{arm}: {phrase!r} still in common list"
            )


def test_wrapping_cannot_hide_an_axis_from_the_checker():
    """Regression for a false negative the wrapping change introduced.

    A hard-wrapped phrase must still be seen. Without whitespace normalization
    the presence check missed "outside knowledge" the moment the renderer began
    wrapping -- i.e. the guard would have reported an axis absent while it sat
    in the prompt, split across two lines.
    """
    wrapped = ("- Do not break ties using evidence item count,\n"
               "  source order, or outside\n  knowledge unless stated.")
    rendered = {
        # KEPT must also name the target axes -- Q1's clause is their carrier.
        "PROHIBITION_KEPT": wrapped + "\n" + contract.LIVENESS_CLAUSE_TEXT,
        "PROHIBITION_REMOVED": wrapped,
    }
    # Must NOT raise "no surface token" for outside_knowledge / evidence_count.
    policy.assert_declared_carriers_match_rendered_text(
        rendered, allowed_rendering="silence"
    )


def test_silence_mode_makes_the_two_arms_policy_blocks_identical():
    kept = policy.render_policy_text("PROHIBITION_KEPT", allowed_rendering="silence")
    removed = policy.render_policy_text("PROHIBITION_REMOVED", allowed_rendering="silence")
    assert kept == removed, (
        "under Q11 option A the generated block carries no arm difference; the "
        "whole contrast lives in Q1's clause, which _h1a_contract.py inserts"
    )


def test_explicit_permission_mode_adds_a_removed_only_sentence():
    kept = policy.render_policy_block("PROHIBITION_KEPT", allowed_rendering="explicit_permission")
    removed = policy.render_policy_block("PROHIBITION_REMOVED", allowed_rendering="explicit_permission")
    assert policy.CARRIER_PERMISSION not in {c for c, _ in kept}
    assert policy.CARRIER_PERMISSION in {c for c, _ in removed}


def test_every_rendered_sentence_is_traceable_to_a_carrier():
    """Q10.2 requirement 5."""
    for arm in policy.ARMS:
        for mode in policy.RENDERING_MODES:
            for carrier, sentence in policy.render_policy_block(arm, mode):
                assert carrier in policy.CARRIERS
                assert sentence.strip()


def test_renderer_is_deterministic():
    for arm in policy.ARMS:
        a = policy.render_policy_text(arm, "silence")
        b = policy.render_policy_text(arm, "silence")
        assert a == b


# ==========================================================================
# Q11 fail-closed
# ==========================================================================
def test_rendering_removed_arm_raises_while_q11_is_unruled():
    assert policy.REMOVED_ALLOWED_RENDERING is None, (
        "Q11 is unruled; if this fails, a ruling landed and the fail-closed "
        "tests below must be revisited rather than deleted"
    )
    with pytest.raises(policy.Q11Undecided):
        policy.render_policy_block("PROHIBITION_REMOVED")


def test_kept_arm_renders_without_q11_because_it_has_no_allowed_axis():
    block = policy.render_policy_block("PROHIBITION_KEPT")
    assert {c for c, _ in block} == {policy.CARRIER_Q7}


def test_freeze_is_refused_while_q11_is_unruled():
    with pytest.raises(policy.Q11Undecided):
        policy.assert_freezable()


def test_an_invalid_rendering_mode_is_rejected():
    with pytest.raises(policy.PolicyContractError):
        policy.render_policy_block("PROHIBITION_REMOVED", allowed_rendering="maybe")


# ==========================================================================
# recall -- mutations must be CAUGHT
# ==========================================================================
def test_mutation_readding_a_target_axis_to_the_q7_list_is_caught(clean_policy):
    """The Q10 defect, injected structurally."""
    clean_policy["liveness"]["carriers"] = (policy.CARRIER_Q1, policy.CARRIER_Q7)
    with pytest.raises(policy.PolicyContractError, match="carriers"):
        policy.assert_manipulated_axes_have_exactly_one_carrier()


def test_mutation_forbidding_a_target_axis_in_removed_is_caught(clean_policy):
    clean_policy["recency"]["removed"] = policy.FORBIDDEN
    with pytest.raises(policy.PolicyContractError):
        policy.assert_target_axis_states()
    with pytest.raises(policy.PolicyContractError):
        policy.assert_arm_difference_is_exactly_the_target_set()


def test_mutation_making_a_nontarget_axis_arm_varying_is_caught(clean_policy):
    clean_policy["source_order"]["removed"] = policy.ALLOWED
    with pytest.raises(policy.PolicyContractError):
        policy.assert_nontarget_axes_are_arm_invariant()
    with pytest.raises(policy.PolicyContractError):
        policy.assert_arm_difference_is_exactly_the_target_set()


def test_mutation_allowing_a_target_axis_in_kept_is_caught(clean_policy):
    clean_policy["authority"]["kept"] = policy.ALLOWED
    with pytest.raises(policy.PolicyContractError):
        policy.assert_target_axis_states()


def test_mutation_breaking_the_contrast_is_caught_by_the_deductive_check(clean_policy):
    clean_policy["liveness"]["carriers"] = (policy.CARRIER_Q7,)
    clean_policy["liveness"]["removed"] = policy.FORBIDDEN
    with pytest.raises(policy.PolicyContractError):
        policy.assert_deductive_check()


def test_mutation_paraphrased_residual_prohibition_is_caught():
    """The case a closed keyword list cannot certify.

    Q10.2 forbids proving absence lexically because an equivalent prohibition
    can be paraphrased. This guard instead asks whether the axis is NAMED in an
    arm that declares it allowed, so novel phrasing does not help it hide.
    """
    base = policy.render_policy_text("PROHIBITION_KEPT", "silence")
    smuggled = (
        base
        + "\n- Treat the more recently written source as carrying more weight "
          "when its authority is clearer."
    )
    rendered = {
        "PROHIBITION_KEPT": base + " " + contract.LIVENESS_CLAUSE_TEXT,
        "PROHIBITION_REMOVED": smuggled,
    }
    with pytest.raises(policy.PolicyContractError, match="residual prohibition"):
        policy.assert_declared_carriers_match_rendered_text(
            rendered, allowed_rendering="silence"
        )


def test_mutation_dropping_a_forbidden_axis_from_the_prose_is_caught():
    """Reverse direction: the policy claims a constraint the prompt lacks."""
    rendered = {
        "PROHIBITION_KEPT": "- Do not break ties using source order.",
        "PROHIBITION_REMOVED": "- Do not break ties using source order.",
    }
    with pytest.raises(policy.PolicyContractError, match="no surface token"):
        policy.assert_declared_carriers_match_rendered_text(
            rendered, allowed_rendering="silence"
        )


# ==========================================================================
# the load-bearing regression: the real non-identifying cohort is rejected
# ==========================================================================
def test_the_actual_nonidentifying_cohort_prompt_is_rejected():
    """Feed the frozen bytes of the ruled-non-identifying cohort to the new guard.

    `cohort_prompts.json` is the manifest of the 40 trials that actually ran on
    2026-08-03 and that D-H1a-10 ruled non-identifying. Under the OLD guard,
    `assert_no_residual_prohibition` passed on these exact bytes and
    `test_guard_precision_the_clean_template_passes` certified them clean.

    The new guard must reject them. If this test ever passes trivially -- or
    stops failing on the old bytes -- the raise ordered by Q10.2 has been undone.
    """
    manifest = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    rendered = manifest["rendered_prompts"]
    assert set(rendered) == set(policy.ARMS)

    # Sanity: these really are the pre-repair bytes -- both arms still name the
    # target axes in the common tie-breaker list.
    for arm in policy.ARMS:
        low = rendered[arm].lower()
        for phrase in ("recency", "authority", "liveness", "source_kind"):
            assert phrase in low, (
                f"{arm}: {phrase!r} absent -- cohort_prompts.json is no longer "
                f"the pre-repair manifest, so this regression test is testing "
                f"nothing"
            )

    with pytest.raises(policy.PolicyContractError, match="residual prohibition"):
        policy.assert_declared_carriers_match_rendered_text(
            rendered, allowed_rendering="silence"
        )


def test_old_guard_still_passes_those_same_bytes():
    """Pin the contrast, so the improvement is documented rather than asserted.

    Not a defence of the old guard -- evidence that the two guards assert
    different propositions, which is the whole finding behind Q10.2.
    """
    manifest = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    removed = manifest["rendered_prompts"]["PROHIBITION_REMOVED"]
    contract.assert_no_residual_prohibition(removed)  # passes, as it always did
