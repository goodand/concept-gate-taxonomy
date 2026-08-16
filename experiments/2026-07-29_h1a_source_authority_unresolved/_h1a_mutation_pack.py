"""Blinded adversarial mutation pack -- D-H1a-13 Q13.5 (condition 11).

    각 리뷰어는 자신의 배정 범위와 관련된 blinded mutation을 최소 한 건
    탐지해야 한다. 이 capability check를 통과하지 않은 리뷰어의 "문제 없음"은
    freeze 승인으로 계산하지 않는다.

WHY A REVIEWER CAPABILITY CHECK EXISTS AT ALL
----------------------------------------------
An "all clear" is only informative from a reviewer who would have said
otherwise had there been something to find. This experiment has the receipts:
five independent reviews passed before one finally caught that `assert_5` was
completely vacuous, and D-H1a-10 was discovered only after 40 trials had been
spent on a cohort whose two arms forbade the same thing. Unmeasured reviewer
recall is how both survived.

TWO PROPERTIES MAKE THIS A REAL TEST
-------------------------------------
1. CLEAN PACKETS ARE INCLUDED. Without them, "always report a mutation" is a
   winning strategy and the check measures nothing. False positives on a clean
   packet are recorded and disqualify just as a miss does.

2. THE MUTATIONS ARE VERIFIED TO BE REAL. A "mutation" that does not change
   policy meaning would be an unfair test and a meaningless credential, so
   every mutation is put through the expected-vs-observed audit
   (`_h1a_policy_audit`) and must produce a finding there.
   `verify_mutations_are_real()` is that check, and the test suite runs it.

BLINDING
--------
`build_assignment()` returns packets and an answer key as SEPARATE values. The
caller hands out packets and keeps the key. Nothing in a packet says whether
it was mutated -- not a field, not an id, not the ordering, which is derived
from a seeded hash rather than from mutation status.

The seed makes this reproducible without making it guessable from the packet
alone; whoever holds the seed holds the key, so it must not travel with the
packets.

Stdlib only.
"""

from __future__ import annotations

import hashlib

# Mutation scopes -- a reviewer's declared scope determines which mutations
# count as "related to their assignment" (condition 11).
SCOPE_TARGET_AXIS = "target_axis_prohibition"
SCOPE_REFERENTIAL = "referential_integrity"
SCOPE_NON_TARGET_AXES = "non_target_axes"
SCOPE_EVIDENCE_SCOPE = "evidence_scope"
SCOPE_DECISION_MAPPING = "decision_mapping"

SCOPES = (
    SCOPE_TARGET_AXIS, SCOPE_REFERENTIAL, SCOPE_NON_TARGET_AXES,
    SCOPE_EVIDENCE_SCOPE, SCOPE_DECISION_MAPPING,
)

CLEAN = "clean"


class MutationPackError(Exception):
    """The caller violated this module's preconditions."""


def _append(sentence: str):
    def apply(text: str) -> str:
        return text.rstrip("\n") + "\n" + sentence + "\n"
    return apply


def _replace(old: str, new: str):
    def apply(text: str) -> str:
        if old not in text:
            raise MutationPackError(
                f"mutation target not found in the rendered prompt: {old!r}. "
                f"The prompt drifted from what this pack was written against, "
                f"so the mutation would be a no-op and the reviewer check "
                f"would silently measure nothing."
            )
        return text.replace(old, new, 1)
    return apply


# Each entry is one of Q13.5's own listed examples.
MUTATIONS: dict[str, dict] = {
    "M1_residual_target_prohibition": {
        "scope": SCOPE_TARGET_AXIS,
        "arm": "removed",
        "description": (
            "A source-priority prohibition left in REMOVED. Both arms then "
            "forbid the same thing and the contrast collapses -- D-H1a-10's "
            "actual defect, found only after 40 trials."
        ),
        "apply": _append("모델은 출처의 liveness나 우선순위를 재판정하지 않는다."),
    },
    "M2_residual_prohibition_in_english": {
        "scope": SCOPE_TARGET_AXIS,
        "arm": "removed",
        "description": (
            "The same residual prohibition restated in the other language "
            "surface, so a reviewer anchored on the frozen Korean bytes misses it."
        ),
        "apply": _append(
            "Do not reason about which source is more authoritative or more recent."
        ),
    },
    "M3_dangling_reference": {
        "scope": SCOPE_REFERENTIAL,
        "arm": "removed",
        "description": (
            "Reintroduces the sentence Q13 deleted: it refers to an "
            "arm-specific source-evaluation clause that REMOVED does not contain."
        ),
        "apply": _append(
            "Source evaluation is governed by the arm-specific source-evaluation clause."
        ),
    },
    "M4_presentation_order_widened": {
        "scope": SCOPE_NON_TARGET_AXES,
        "arm": "removed",
        "description": (
            "Reverts Q13.1's disambiguation: 'source order' reads as both "
            "presentation order and source-kind priority, so a non-target "
            "axis quietly starts covering the target one."
        ),
        "apply": _replace(
            "the order in which evidence\n  items appear in the packet",
            "source order",
        ),
    },
    "M5_recorded_fields_narrowed": {
        "scope": SCOPE_EVIDENCE_SCOPE,
        "arm": "removed",
        "description": (
            "Text-only field narrowing: undoes Q13.2 by making the permission "
            "cover only item text, so source-kind evaluation is silently barred."
        ),
        # Both mentions must go: Q13.2 states the permission twice (scope
        # sentence + the explicit non-prohibition sentence), and removing only
        # one leaves the family detectable and the mutation inert. The
        # reality check caught that.
        "apply": lambda text: _replace(
            "evidence items, including their recorded fields.",
            "evidence items, but only their text.",
        )(_replace(
            "it does not\nby itself prohibit evaluating the item's other recorded fields as source\ninformation.",
            "Only an item's text may be evaluated.",
        )(text)),
    },
    "M6_conflict_to_defer_hard_mapping": {
        "scope": SCOPE_DECISION_MAPPING,
        "arm": "removed",
        "description": (
            "Turns Q7=E's warrant rule into a hard mapping: conflict forces "
            "defer, which manufactures the very behavior the experiment measures."
        ),
        "apply": _replace(
            "- The presence of conflicting evidence does not by itself require either\n"
            "  selection or deferral.",
            "- Conflicting evidence requires you to defer.",
        ),
    },
}


def mutations_for_scope(scope: str) -> list[str]:
    if scope not in SCOPES:
        raise MutationPackError(f"unknown scope {scope!r}, expected one of {SCOPES}")
    return sorted(mid for mid, m in MUTATIONS.items() if m["scope"] == scope)


def _packet_order(seed: str, reviewer_id: str, index: int) -> str:
    """Deterministic but not inferable from the packet's content."""
    material = "\0".join((seed, reviewer_id, str(index)))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def build_assignment(
    rendered_by_arm: dict, reviewer_scopes: dict, seed: str, clean_packets: int = 1
) -> tuple[list[dict], dict]:
    """Build blinded packets and the answer key, as SEPARATE return values.

    Every reviewer gets at least one mutation inside their declared scope and
    at least one clean packet. Which is which is not derivable from a packet:
    packet ids are seeded hashes and carry no mutation marker.
    """
    if not reviewer_scopes:
        raise MutationPackError("no reviewers assigned")
    if clean_packets < 1:
        raise MutationPackError(
            "at least one clean packet is required, otherwise 'always report a "
            "mutation' passes the check and it measures nothing"
        )

    packets, key = [], {}
    for reviewer_id, scope in sorted(reviewer_scopes.items()):
        scoped = mutations_for_scope(scope)
        if not scoped:
            raise MutationPackError(
                f"reviewer {reviewer_id!r} has scope {scope!r} with no mutations; "
                f"their capability could not be measured"
            )
        entries = [(mid, MUTATIONS[mid]) for mid in scoped]
        entries += [(None, None)] * clean_packets

        for index, (mutation_id, mutation) in enumerate(entries):
            arm = mutation["arm"] if mutation else "removed"
            base = rendered_by_arm[arm]
            text = mutation["apply"](base) if mutation else base
            packet_id = _packet_order(seed, reviewer_id, index)[:16]
            packets.append({
                "packet_id": packet_id,
                "reviewer_id": reviewer_id,
                "declared_scope": scope,
                "arm": arm,
                "rendered_prompt": text,
            })
            key[packet_id] = {
                "reviewer_id": reviewer_id,
                "mutation_id": mutation_id,   # None == clean
                "scope": scope,
            }

    packets.sort(key=lambda p: p["packet_id"])
    return packets, key


def score_reviewer(reviewer_id: str, reported: dict, key: dict) -> dict:
    """Did this reviewer detect a mutation in their own scope?

    `reported` maps packet_id -> bool ("I found a policy defect here").
    Condition 11 asks for at least one detection within the declared scope;
    a false positive on a clean packet disqualifies too, because a reviewer
    who flags everything has demonstrated nothing.
    """
    mine = {pid: entry for pid, entry in key.items() if entry["reviewer_id"] == reviewer_id}
    if not mine:
        raise MutationPackError(f"no packets assigned to reviewer {reviewer_id!r}")

    missing = sorted(set(mine) - set(reported))
    detected, missed, false_positives = [], [], []
    for pid, entry in sorted(mine.items()):
        said_defect = bool(reported.get(pid, False))
        if entry["mutation_id"] is None:
            if said_defect:
                false_positives.append(pid)
        elif said_defect:
            detected.append(entry["mutation_id"])
        else:
            missed.append(entry["mutation_id"])

    qualified = bool(detected) and not false_positives and not missing
    return {
        "reviewer_id": reviewer_id,
        "detected": sorted(detected),
        "missed": sorted(missed),
        "false_positives": false_positives,
        "unanswered_packets": missing,
        "qualified": qualified,
        # Q13.5's consequence, carried with the verdict so it cannot be
        # dropped between here and the freeze decision.
        "approval_counts_toward_freeze": qualified,
        "note": (
            "An unqualified reviewer's 'no problems found' does not count as "
            "freeze approval (Q13.5 condition 11)."
        ),
    }


def verify_mutations_are_real(rendered_by_arm: dict, audit_module, proven_families) -> dict:
    """Every mutation must actually change the policy graph.

    A mutation that leaves the audit clean would test nothing, and crediting a
    reviewer for 'detecting' it -- or faulting them for missing it -- would be
    measuring noise. Imported lazily via a parameter so this module stays
    dependency-light and the compiler's independence rules stay unaffected.
    """
    results = {}
    for mutation_id, mutation in sorted(MUTATIONS.items()):
        arm = mutation["arm"]
        mutated = mutation["apply"](rendered_by_arm[arm])
        report = audit_module.audit_arm(mutated, arm, proven_families=proven_families)
        baseline = audit_module.audit_arm(
            rendered_by_arm[arm], arm, proven_families=proven_families)
        new_findings = [
            f for f in report["findings"] if f not in baseline["findings"]
        ]
        results[mutation_id] = {
            "scope": mutation["scope"],
            "changed_the_graph": bool(new_findings),
            "new_findings": [f["kind"] for f in new_findings],
            "target_critical": bool(report["target_critical_blocking"])
            and not baseline["target_critical_blocking"],
        }
    return results
