"""Tests for the expected-vs-observed policy audit -- Q13.6 sec 9.4.

The load-bearing tests here are the MUTATION ones. A comparison that reports
"clean" on the shipping prompt and has never been shown to catch anything is
indistinguishable from a comparison that always reports clean -- and this
experiment already shipped exactly that (assert_5 was completely vacuous while
its positive test passed; an external reviewer found it, not the suite).

The mutation that matters most injects a residual source-priority prohibition
into REMOVED. That is the real defect from D-H1a-10: a prohibition survived in
the arm meant to be free of it, both arms therefore forbade the same thing,
and the 40-trial cohort came out non-identifying. If this audit cannot catch
that, it is not worth running.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_policy_audit_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


audit = _load("audit", "_h1a_policy_audit.py")
sc = _load("sc", "_h1a_semantic_compiler.py")
cap = _load("cap", "_h1a_compiler_capability.py")
contract = _load("contract", "_h1a_contract.py")

PROVEN = cap.proven_families()


def _rendered(arm: str) -> str:
    return contract.render_arm(contract.load_h1a_native_template(), arm)


def _findings_for(report, policy_id, kind=None):
    return [f for f in report["findings"]
            if f.get("policy_id") == policy_id and (kind is None or f["kind"] == kind)]


# --- the shipping prompts -------------------------------------------------

def test_every_mappable_family_agrees_in_both_arms():
    for label, arm in (("kept", "PROHIBITION_KEPT"), ("removed", "PROHIBITION_REMOVED")):
        report = audit.audit_arm(_rendered(arm), label, proven_families=PROVEN)
        assert set(report["agreed"]) == {
            sc.EVIDENCE_COUNT_PROHIBITION,
            sc.EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION,
            sc.OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION,
            sc.SOURCE_META_REASONING_PROHIBITION,
        }, label
        assert report["target_critical_blocking"] == [], label


def test_the_manipulated_axis_agrees_with_the_dsl_in_both_directions():
    """The experiment's identifiability claim, checked against the canonical
    policy rather than against the renderer's own vocabulary."""
    kept = audit.audit_arm(_rendered("PROHIBITION_KEPT"), "kept", proven_families=PROVEN)
    removed = audit.audit_arm(_rendered("PROHIBITION_REMOVED"), "removed", proven_families=PROVEN)
    assert sc.SOURCE_META_REASONING_PROHIBITION in kept["agreed"]
    assert sc.SOURCE_META_REASONING_PROHIBITION in removed["agreed"]


# --- mutation: can this audit catch anything at all? ----------------------

def test_a_residual_prohibition_in_removed_is_caught():
    """D-H1a-10's actual defect. A source-priority prohibition left in REMOVED
    makes both arms forbid the same thing and the cohort non-identifying."""
    mutated = _rendered("PROHIBITION_REMOVED") + (
        "\n모델은 출처의 liveness나 우선순위를 재판정하지 않는다.\n")
    report = audit.audit_arm(mutated, "removed", proven_families=PROVEN)

    [finding] = _findings_for(report, sc.SOURCE_META_REASONING_PROHIBITION,
                              audit.STATE_MISMATCH)
    assert finding["expected_state"] == sc.ABSENT_VERIFIED
    assert finding["observed_state"] == sc.PRESENT
    assert finding["target_critical"] is True
    assert report["target_critical_blocking"], (
        "a residual target-axis prohibition must block, not merely be noted"
    )


def test_an_english_paraphrase_of_the_residual_prohibition_is_also_caught():
    """A residual prohibition restated in the other language surface is still
    a residual prohibition -- the frozen clause being Korean must not become
    the only thing that is looked for."""
    mutated = _rendered("PROHIBITION_REMOVED") + (
        "\nDo not reason about which source is more authoritative.\n")
    report = audit.audit_arm(mutated, "removed", proven_families=PROVEN)
    assert _findings_for(report, sc.SOURCE_META_REASONING_PROHIBITION,
                         audit.STATE_MISMATCH)
    assert report["target_critical_blocking"]


def test_deleting_the_prohibition_from_kept_is_caught():
    """The mirror mutation: KEPT losing its manipulation collapses the
    contrast just as surely."""
    kept = _rendered("PROHIBITION_KEPT")
    without = kept.replace(contract.LIVENESS_CLAUSE_TEXT, "")
    assert without != kept, "precondition: the clause was actually removed"

    report = audit.audit_arm(without, "kept", proven_families=PROVEN)
    [finding] = _findings_for(report, sc.SOURCE_META_REASONING_PROHIBITION,
                              audit.STATE_MISMATCH)
    assert finding["expected_state"] == sc.PRESENT
    assert finding["observed_state"] == sc.ABSENT_VERIFIED
    assert report["target_critical_blocking"]


def test_a_non_target_axis_mutation_is_caught_but_is_not_target_critical():
    """Precision on severity: evidence_count is a real divergence and must be
    reported, but it is not one of the target-critical families, so it must
    not be escalated to blocking."""
    removed = _rendered("PROHIBITION_REMOVED")
    without = removed.replace("evidence item count", "the number of items")
    assert without != removed

    report = audit.audit_arm(without, "removed", proven_families=PROVEN)
    findings = _findings_for(report, sc.EVIDENCE_COUNT_PROHIBITION)
    assert findings, "removing the count prohibition's surface must diverge"
    assert not any(f.get("target_critical") for f in findings)


# --- honesty about what is NOT audited ------------------------------------

def test_families_without_a_dsl_axis_are_reported_not_counted_as_agreement():
    """Silently dropping them would leave whole families unaudited while the
    report reads clean."""
    report = audit.audit_arm(_rendered("PROHIBITION_REMOVED"), "removed",
                             proven_families=PROVEN)
    for family in (sc.GLOBAL_DEFAULT_PERMISSION, sc.CONFLICT_TO_DEFER_MAPPING,
                   sc.RECORDED_FIELDS_ACCESS, sc.TEXT_TYPE_SUPPORT_RULE):
        assert _findings_for(report, family, audit.NO_EXPECTED_COUNTERPART), family
        assert family not in report["agreed"], family


def test_an_unproven_family_surfaces_as_unresolved_not_as_agreement():
    """sec 9.6 silence is `unknown`; the audit must escalate that rather than
    let it pass as a match."""
    report = audit.audit_arm(_rendered("PROHIBITION_REMOVED"), "removed",
                             proven_families=frozenset())
    unresolved = [f for f in report["findings"] if f["kind"] == audit.UNRESOLVED]
    assert unresolved
    assert all(f["policy_id"] not in report["agreed"] for f in unresolved)


def test_every_dsl_axis_is_either_mapped_or_reported_as_unaudited():
    import _h1a_policy as policy
    covered = {a for axes in audit.FAMILY_TO_AXES.values() for a in axes}
    expected = audit.expected_graph("removed")
    assert set(policy.AXES) - covered == set(expected["axes_without_a_family"])


# --- contract -------------------------------------------------------------

def test_comparing_different_arms_is_refused():
    observed = sc.compile_policy_graph(_rendered("PROHIBITION_KEPT"), "kept")
    with pytest.raises(audit.AuditContractError, match="arm mismatch"):
        audit.compare(observed, audit.expected_graph("removed"))


def test_expected_graph_validates_its_arm():
    with pytest.raises(audit.AuditContractError, match="arm must be one of"):
        audit.expected_graph("PROHIBITION_KEPT")


def test_the_audit_assurance_is_capped_by_the_observed_graph():
    """sec 9.5: A_final = min(A_semantic_graph, A_rule_result). A rule engine
    computing deterministically over a semantic graph does not upgrade it."""
    report = audit.audit_arm(_rendered("PROHIBITION_REMOVED"), "removed",
                             proven_families=PROVEN)
    assert report["assurance"] == sc.ASSURANCE_CEILING


def test_expected_states_come_from_the_dsl_not_from_the_prompt():
    """If the expectation were derived from the rendered text, the comparison
    would be self-confirming and could never diverge."""
    import _h1a_policy as policy
    expected = audit.expected_graph("kept")
    entry = expected["expectations"][sc.SOURCE_META_REASONING_PROHIBITION]
    dsl_state = policy.DECISION_BASIS_POLICY["source_meta_reasoning"]["kept"]["state"]
    assert dsl_state == policy.EXPLICITLY_FORBIDDEN
    assert entry["expected_state"] == sc.PRESENT

    removed_entry = audit.expected_graph("removed")["expectations"][
        sc.SOURCE_META_REASONING_PROHIBITION]
    assert removed_entry["expected_state"] == sc.ABSENT_VERIFIED
