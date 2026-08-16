"""Independent semantic review protocol -- D-H1a-13 Q13.5 conditions 11 and 12.

    condition_11:
      independent_semantic_review:
        reviewer_scope_declared: true
        rendered_prompt_reviewed: true
        expected_policy_graph_reviewed: true
        compiler_diff_reviewed: true
        adversarial_mutation_pack_used: true

    condition_12:
      All reviewers approve freeze after confirming that:
        1. no unresolved BLOCKER or MAJOR remains within their declared scope;
        2. all target-critical policy families have resolved semantic states;
        3. any remaining unknown states are explicitly classified as
           non-critical limitations.

WHY THE PROTOCOL IS CODE AND NOT A CHECKLIST
---------------------------------------------
The 2026-08-16 adversarial review missed a whole harness defect because the
session being reviewed chose what the reviewers would look at. Encoding the
protocol removes that discretion from whoever runs it: scopes are declared up
front, the packets are blinded, capability is scored before opinions are
counted, and an unqualified reviewer's approval is dropped mechanically rather
than by remembering to.

This module DOES NOT decide freeze. It assembles what condition 11 requires,
scores capability, and reports which approvals may be counted -- the same
separation between auditing and authority that D-H1a-14/15 installed for the
capability diagnostics.

Stdlib only.
"""

from __future__ import annotations

import _h1a_compiler_capability as capability
import _h1a_contract as contract
import _h1a_mutation_pack as mutation_pack
import _h1a_policy_audit as audit
import _h1a_semantic_compiler as sc

BLOCKER = "blocker"
MAJOR = "major"
MINOR = "minor"
SEVERITIES = (BLOCKER, MAJOR, MINOR)


class ReviewProtocolError(Exception):
    """The caller violated the protocol's preconditions."""


def rendered_arms() -> dict:
    template = contract.load_h1a_native_template()
    return {
        "kept": contract.render_arm(template, "PROHIBITION_KEPT"),
        "removed": contract.render_arm(template, "PROHIBITION_REMOVED"),
    }


def build_review_materials(reviewer_scopes: dict, seed: str) -> tuple[dict, dict]:
    """Everything condition 11 requires, plus the answer key held separately.

    Returns (materials, answer_key). `materials` is what reviewers may see;
    the key must not travel with it.
    """
    if not reviewer_scopes:
        raise ReviewProtocolError("condition 11 requires declared reviewer scopes")

    rendered = rendered_arms()
    proven = capability.proven_families()

    audits, diffs = {}, {}
    for arm_label, arm in (("kept", "PROHIBITION_KEPT"), ("removed", "PROHIBITION_REMOVED")):
        observed = sc.compile_policy_graph(rendered[arm_label], arm_label,
                                           proven_families=proven)
        expected = audit.expected_graph(arm_label)
        audits[arm_label] = {"observed": observed, "expected": expected}
        diffs[arm_label] = audit.compare(observed, expected)

    packets, key = mutation_pack.build_assignment(rendered, reviewer_scopes, seed=seed)

    materials = {
        "record_class": "h1a_review_materials",
        "ruling": "D-H1a-13 Q13.5 condition 11",
        "reviewer_scopes": dict(reviewer_scopes),
        # condition 11's five requirements, each pointing at what satisfies it.
        "rendered_prompt": rendered,
        "expected_policy_graph": {a: audits[a]["expected"] for a in audits},
        "observed_policy_graph": {a: audits[a]["observed"] for a in audits},
        "compiler_diff": diffs,
        "mutation_packets": packets,
        "capability_report": {
            "proven_families": sorted(proven),
            "unproven_families": sorted(frozenset(sc.POLICY_FAMILIES) - proven),
            "target_critical_unproven": capability.evaluate_capability()[
                "target_critical_unproven"],
        },
    }
    return materials, key


def _condition_11(materials: dict, scored: dict) -> dict:
    return {
        "reviewer_scope_declared": bool(materials["reviewer_scopes"]),
        "rendered_prompt_reviewed": bool(materials["rendered_prompt"]),
        "expected_policy_graph_reviewed": bool(materials["expected_policy_graph"]),
        "compiler_diff_reviewed": bool(materials["compiler_diff"]),
        "adversarial_mutation_pack_used": bool(scored),
    }


def assess(materials: dict, key: dict, reviewer_reports: dict) -> dict:
    """Score capability, then count only qualified reviewers' judgments.

    `reviewer_reports` maps reviewer_id -> {
        "packet_findings": {packet_id: bool},   # capability answers
        "scope_findings": [{"severity": ..., "summary": ...}, ...],
        "approves_freeze": bool,
    }
    """
    scored, unqualified = {}, []
    for reviewer_id in sorted(materials["reviewer_scopes"]):
        report = reviewer_reports.get(reviewer_id)
        if report is None:
            raise ReviewProtocolError(
                f"reviewer {reviewer_id!r} declared a scope but filed no report; "
                f"a silent reviewer is not an approving one"
            )
        result = mutation_pack.score_reviewer(
            reviewer_id, report.get("packet_findings", {}), key)
        scored[reviewer_id] = result
        if not result["qualified"]:
            unqualified.append(reviewer_id)

    # condition 12.1 -- only within a QUALIFIED reviewer's declared scope.
    unresolved = []
    for reviewer_id, result in scored.items():
        if not result["qualified"]:
            continue
        for finding in reviewer_reports[reviewer_id].get("scope_findings", []):
            if finding.get("severity") in (BLOCKER, MAJOR):
                unresolved.append({"reviewer_id": reviewer_id, **finding})

    # condition 12.2 -- target-critical families must not be unknown.
    target_critical_unknown = sorted({
        pid
        for diff in materials["compiler_diff"].values()
        for f in diff["findings"]
        if f.get("kind") == audit.UNRESOLVED and f.get("target_critical")
        for pid in [f["policy_id"]]
    })

    # Any target-critical structural or state divergence also blocks.
    blocking_divergences = [
        {"arm": arm, **f}
        for arm, diff in materials["compiler_diff"].items()
        for f in diff["findings"]
        if f.get("target_critical")
    ]

    counted = {
        reviewer_id: bool(reviewer_reports[reviewer_id].get("approves_freeze"))
        for reviewer_id, result in scored.items() if result["qualified"]
    }
    all_qualified_approve = bool(counted) and all(counted.values())

    conditions = _condition_11(materials, scored)
    condition_11_met = all(conditions.values()) and not unqualified
    condition_12_met = (
        all_qualified_approve
        and not unresolved
        and not target_critical_unknown
        and not blocking_divergences
    )

    return {
        "record_class": "h1a_independent_semantic_review",
        "ruling": "D-H1a-13 Q13.5",
        "condition_11": conditions,
        "condition_11_met": condition_11_met,
        "capability": scored,
        "unqualified_reviewers": unqualified,
        "approvals_counted": counted,
        "approvals_discarded": sorted(unqualified),
        "unresolved_blocker_or_major": unresolved,
        "target_critical_unknown": target_critical_unknown,
        "target_critical_divergences": blocking_divergences,
        "condition_12_met": condition_12_met,
        # The flag `_h1a_policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED` may be set
        # only when both hold. This module reports; a human sets the flag.
        "independent_semantic_review_passed": condition_11_met and condition_12_met,
        "note": (
            "An unqualified reviewer's approval is discarded, not weighed "
            "(Q13.5 condition 11). This record does not itself change any "
            "freeze flag."
        ),
    }
