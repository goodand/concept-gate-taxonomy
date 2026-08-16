"""Expected-vs-observed policy graph comparison -- Q13.6 sec 9.4's last arrow.

    Policy DSL -> Deterministic Renderer -> Rendered Prompt
                                                 |
                                    Independent Semantic Compiler
                                                 |
                                        Observed Policy Graph
                                                 |
                                   compared to Expected Policy Graph   <- HERE

THE ONLY MODULE PERMITTED TO SEE BOTH SIDES
--------------------------------------------
`_h1a_semantic_compiler` must not import the policy (enforced by AST test) so
that its observations are independent. That independence is only useful if
something eventually compares the two, and this is that something. It imports
both deliberately, which is why the comparison lives here and not there.

WHAT A DIVERGENCE MEANS
------------------------
The canonical is the DSL. A divergence is therefore a claim that the RENDERED
PROSE no longer says what the policy object says -- the drift D-H1a-10 found
too late, when a prohibition survived in an arm that was supposed to be free
of it and the cohort came out non-identifying.

THE MAPPING IS NOT ONE-TO-ONE, AND THAT IS REPORTED
----------------------------------------------------
The compiler's eight families and the DSL's five axes were defined for
different purposes by different rulings. Three families (conflict-to-defer
mapping, recorded-fields access, text/type support rule) have NO axis in
`DECISION_BASIS_POLICY` -- they are template-level rules from Q7=E and Q13.2.
One axis (`external_source_retrieval`) has no dedicated family; it shares a
carrier with `outside_domain_knowledge` and the compiler's detector covers
both at once.

Silently dropping either side would let a whole family go unaudited while the
report reads clean, so both directions are surfaced explicitly as coverage
findings rather than omitted.

Stdlib only.
"""

from __future__ import annotations

import _h1a_policy as policy
import _h1a_semantic_compiler as sc

# --- family <-> axis mapping ----------------------------------------------
# A family maps to the axes whose prohibition it would observe in prose.
# An empty tuple means "no counterpart in the canonical DSL" -- adjudicated
# elsewhere, and reported as a coverage finding rather than passed silently.

FAMILY_TO_AXES: dict[str, tuple[str, ...]] = {
    sc.EVIDENCE_COUNT_PROHIBITION: ("evidence_count",),
    sc.EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION: ("evidence_item_presentation_order",),
    # One detector covers both: they share CARRIER_DOMAIN and are rendered as
    # a single sentence pair, so the compiler cannot separate them from prose
    # alone. Recorded here rather than hidden -- it is a real granularity
    # limit of the audit, not an equivalence.
    sc.OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION: (
        "outside_domain_knowledge", "external_source_retrieval",
    ),
    sc.SOURCE_META_REASONING_PROHIBITION: ("source_meta_reasoning",),
    # Carrier-level, not an axis: GLOBAL_DEFAULT_PERMISSION is the default
    # permission text every non-forbidden basis falls back to.
    sc.GLOBAL_DEFAULT_PERMISSION: (),
    sc.CONFLICT_TO_DEFER_MAPPING: (),      # Q7=E warrant rule, template-level
    sc.RECORDED_FIELDS_ACCESS: (),         # Q13.2 scope text
    sc.TEXT_TYPE_SUPPORT_RULE: (),         # evidence-reading rule
}

# Divergence kinds.
STATE_MISMATCH = "state_mismatch"
UNRESOLVED = "unresolved"
NO_EXPECTED_COUNTERPART = "no_expected_counterpart"
NO_OBSERVED_COUNTERPART = "no_observed_counterpart"
MIXED_EXPECTATION = "mixed_expectation"
STRUCTURAL_DEFECT = "structural_defect"

# sec 9.3's "별도 구조 항목" are defects in their own right, independent of any
# family's present/absent state. `compare()` ignored them until 2026-08-16,
# when the mutation pack's reality check showed a reintroduced dangling
# reference produced NO audit finding at all -- the defect class that
# produced D-H1a-13 in the first place would have passed silently.
STRUCTURAL_IS_DEFECT = {
    sc.DANGLING_REFERENCE: True,
    sc.EXPERIMENT_ARM_DISCLOSURE: True,
    sc.AMBIGUOUS_AXIS_PHRASING: True,
    sc.DUPLICATE_CARRIER: False,   # candidate list only -- see its docstring
}


class AuditContractError(Exception):
    """The caller violated this module's preconditions."""


_ARM_TO_DSL = {sc.KEPT: "kept", sc.REMOVED: "removed"}


def expected_graph(arm: str) -> dict:
    """Derive what the rendered prose SHOULD say, from the canonical DSL."""
    if arm not in sc.ARMS:
        raise AuditContractError(f"arm must be one of {sc.ARMS}, got {arm!r}")
    dsl_arm = _ARM_TO_DSL[arm]

    expectations = {}
    for family, axes in FAMILY_TO_AXES.items():
        if not axes:
            expectations[family] = {
                "policy_id": family,
                "axes": (),
                "expected_state": None,   # no canonical counterpart
                "carriers": (),
            }
            continue
        states = {policy.DECISION_BASIS_POLICY[a][dsl_arm]["state"] for a in axes}
        carriers = tuple(sorted(
            policy.DECISION_BASIS_POLICY[a][dsl_arm]["carrier"] for a in axes))
        if len(states) > 1:
            # Axes folded into one family disagree -- the family cannot have a
            # single expected state, and asserting one would be a guess.
            expected_state = None
            mixed = True
        else:
            only = states.pop()
            expected_state = (
                sc.PRESENT if only == policy.EXPLICITLY_FORBIDDEN else sc.ABSENT_VERIFIED
            )
            mixed = False
        expectations[family] = {
            "policy_id": family,
            "axes": axes,
            "expected_state": expected_state,
            "expected_mixed": mixed,
            "carriers": carriers,
        }

    covered_axes = {a for axes in FAMILY_TO_AXES.values() for a in axes}
    return {
        "record_class": "h1a_expected_policy_graph",
        "arm": arm,
        "source": "DECISION_BASIS_POLICY (canonical typed policy DSL)",
        "expectations": expectations,
        "axes_without_a_family": sorted(set(policy.AXES) - covered_axes),
    }


def compare(observed: dict, expected: dict) -> dict:
    """Compare an observed graph against the expected one.

    Reports rather than raises: this module is an auditor, and the freeze gate
    is what decides. Returning findings keeps that separation, the same one
    D-H1a-14/15 installed between diagnostics and freeze authority.
    """
    if observed["arm"] != expected["arm"]:
        raise AuditContractError(
            f"arm mismatch: observed {observed['arm']!r} vs expected "
            f"{expected['arm']!r} -- comparing different arms would "
            f"manufacture divergences that are not there"
        )

    observed_by_id = {c["policy_id"]: c for c in observed["claims"]}
    findings = []

    for family, exp in expected["expectations"].items():
        claim = observed_by_id.get(family)
        if claim is None:
            findings.append({
                "kind": NO_OBSERVED_COUNTERPART, "policy_id": family,
                "detail": "the compiler emitted no claim for this family",
            })
            continue

        if exp["expected_state"] is None:
            findings.append({
                "kind": MIXED_EXPECTATION if exp.get("expected_mixed") else NO_EXPECTED_COUNTERPART,
                "policy_id": family,
                "observed_state": claim["state"],
                "axes": list(exp["axes"]),
                "detail": (
                    "folded axes disagree, so no single expected state exists"
                    if exp.get("expected_mixed") else
                    "no axis in the canonical DSL corresponds to this family; "
                    "it is a template-level rule and must be adjudicated by "
                    "other means, not counted as agreement"
                ),
            })
            continue

        if claim["state"] == sc.UNKNOWN:
            findings.append({
                "kind": UNRESOLVED, "policy_id": family,
                "expected_state": exp["expected_state"],
                "target_critical": family in sc.TARGET_CRITICAL,
                "detail": (
                    "the compiler could not decide; capability for this "
                    "family is not demonstrated (Q13.6 sec 9.6)"
                ),
            })
            continue

        if claim["state"] != exp["expected_state"]:
            findings.append({
                "kind": STATE_MISMATCH, "policy_id": family,
                "expected_state": exp["expected_state"],
                "observed_state": claim["state"],
                "carriers": list(exp["carriers"]),
                "source_span": claim["source_span"],
                "target_critical": family in sc.TARGET_CRITICAL,
                "detail": (
                    "the rendered prose does not say what the canonical policy "
                    "says -- this is drift, and the DSL is canonical"
                ),
            })

    for item, is_defect in sorted(STRUCTURAL_IS_DEFECT.items()):
        if not is_defect:
            continue
        observed_item = observed["structural"].get(item)
        if observed_item:
            findings.append({
                "kind": STRUCTURAL_DEFECT, "structural_item": item,
                "observed": observed_item,
                # Referential integrity is one of Q13.5's target-critical
                # families; an unresolved referent is not a stylistic note.
                "target_critical": item in (
                    sc.DANGLING_REFERENCE, sc.EXPERIMENT_ARM_DISCLOSURE),
                "detail": "sec 9.3 structural item present in the rendered prompt",
            })

    for axis in expected["axes_without_a_family"]:
        findings.append({
            "kind": NO_OBSERVED_COUNTERPART, "axis": axis,
            "detail": (
                "no compiler family observes this axis on its own, so its "
                "rendered state is unaudited by this comparison"
            ),
        })

    # Agreement from a detector whose capability is NOT demonstrated must not
    # be pooled with agreement from a proven one. Found by reviewer R3 in the
    # 2026-08-16 condition-12 review: EVIDENCE_COUNT_PROHIBITION appeared under
    # `agreed` while the same report listed it as unproven, so a reader
    # reconciling the two fields got a coverage claim the instrument had not
    # earned. The match may well be correct -- a positive detection is
    # self-evidencing in a way an absence is not -- but "it matched" and "this
    # detector is known to match this family reliably" are different claims and
    # are now reported as different fields.
    matched = [
        family for family, exp in expected["expectations"].items()
        if exp["expected_state"] is not None
        and observed_by_id.get(family, {}).get("state") == exp["expected_state"]
    ]
    proven_here = {
        family for family in matched
        if observed_by_id[family].get("capability_proven")
    }
    agreed = sorted(proven_here)
    agreed_by_unproven_detector = sorted(set(matched) - proven_here)
    blocking = [
        f for f in findings
        if f["kind"] in (STATE_MISMATCH, UNRESOLVED) and f.get("target_critical")
    ]

    return {
        "record_class": "h1a_policy_audit",
        "arm": observed["arm"],
        # sec 9.5: capped by the observed graph that fed it.
        "assurance": observed["assurance"],
        "agreed": agreed,
        "agreed_by_unproven_detector": agreed_by_unproven_detector,
        "findings": findings,
        "target_critical_blocking": blocking,
        "clean": not findings,
    }


def audit_arm(rendered_text: str, arm: str, proven_families=None) -> dict:
    """Convenience: compile, derive expectations, compare."""
    observed = sc.compile_policy_graph(rendered_text, arm, proven_families=proven_families)
    return compare(observed, expected_graph(arm))
