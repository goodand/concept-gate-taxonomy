"""Compiler capability gate -- D-H1a-13 Q13.6 sec 9.6.

Before the semantic compiler's SILENCE about a policy family may be read as
`absent_verified`, it has to demonstrate it can detect that family in the
adversarial forms the ruling enumerates:

    직접 금지문 / 의역된 금지문 / 조건부 금지문 / 예외가 있는 금지문 /
    이중 부정 / dangling reference / 문장 간 scope 결합 / 필드 범위 축소 /
    가까운 비정책 문장

and each target-critical family needs POSITIVE and NEGATIVE fixtures both.
Undemonstrated detection returns `unknown`.

WHY THE PROVEN SET IS COMPUTED, NOT DECLARED
---------------------------------------------
`evaluate_capability()` runs the fixtures and derives which families passed.
Nothing here hand-maintains a list of "families we believe work" -- that list
is precisely the thing that rots into a false claim of coverage, and this
experiment has already been burned by a guard that asserted a true
proposition about the wrong object (F10) and by a manual discipline that
failed 7/7 (`test_guard_negative_coverage.py`).

A LIMIT WORTH STATING PLAINLY
------------------------------
The same session wrote these fixtures and the detectors they test. Fixtures
authored to match a detector prove nothing, so they are written to the
RULING's enumerated forms rather than to what the regexes happen to handle,
and the failures are reported rather than tuned away. A family that does not
pass stays unproven and its silence stays `unknown` -- which is the safe
direction. This does NOT substitute for the independent reviewer capability
check of Q13.5; it is the compiler's half.

Stdlib only.
"""

from __future__ import annotations

import _h1a_semantic_compiler as sc

# --- fixture forms enumerated by sec 9.6 -----------------------------------

DIRECT = "직접 금지문"
PARAPHRASED = "의역된 금지문"
CONDITIONAL = "조건부 금지문"
WITH_EXCEPTION = "예외가 있는 금지문"
DOUBLE_NEGATION = "이중 부정"
CROSS_SENTENCE_SCOPE = "문장 간 scope 결합"
FIELD_NARROWING = "필드 범위 축소"
NEARBY_NON_POLICY = "가까운 비정책 문장"

POSITIVE_FORMS = (
    DIRECT, PARAPHRASED, CONDITIONAL, WITH_EXCEPTION,
    DOUBLE_NEGATION, CROSS_SENTENCE_SCOPE, FIELD_NARROWING,
)

# policy_id -> {form: text}. POSITIVE fixtures: the family IS expressed, so a
# capable compiler must report `present`.
POSITIVE_FIXTURES: dict[str, dict[str, str]] = {
    sc.SOURCE_META_REASONING_PROHIBITION: {
        DIRECT: "모델은 출처의 liveness나 우선순위를 재판정하지 않는다.",
        PARAPHRASED: (
            "Do not attempt to work out which source is more recent or more "
            "authoritative than another."
        ),
        CONDITIONAL: (
            "If two evidence items disagree, you must not resolve the "
            "disagreement by judging which source is more authoritative."
        ),
        WITH_EXCEPTION: (
            "Except where an evidence item's own text says so, do not reason "
            "about source priority."
        ),
        DOUBLE_NEGATION: (
            "It is not the case that you may disregard the restriction on "
            "reasoning about which source is more recent."
        ),
        CROSS_SENTENCE_SCOPE: (
            "Two evidence items may come from different places.\n"
            "Whether one of them is a more authoritative source is not for "
            "you to decide."
        ),
        FIELD_NARROWING: (
            "Only an evidence item's text may be read; its source priority "
            "must not be assessed."
        ),
    },
    sc.EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION: {
        DIRECT: (
            "Do not break ties using the order in which evidence items appear "
            "in the packet."
        ),
        PARAPHRASED: "The presentation order of the items carries no weight.",
        CONDITIONAL: (
            "If the items are tied, you may not settle it by the order in "
            "which evidence items appear."
        ),
        WITH_EXCEPTION: (
            "Unless the packet authorizes it, presentation order must not "
            "decide the outcome."
        ),
        DOUBLE_NEGATION: (
            "You may not ignore the rule that presentation order is not a "
            "permitted basis."
        ),
        CROSS_SENTENCE_SCOPE: (
            "The items are listed in a fixed sequence.\n"
            "That presentation order is not a permitted tie-breaker."
        ),
        FIELD_NARROWING: (
            "Only item text counts; the order in which evidence items appear "
            "does not."
        ),
    },
    sc.OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION: {
        DIRECT: (
            "Do not use outside domain or ontology knowledge to supply facts "
            "about the concept-feature relation."
        ),
        PARAPHRASED: (
            "Do not rely on general ontology knowledge you happen to have."
        ),
        CONDITIONAL: (
            "If the packet is silent on a fact, you still may not use outside "
            "knowledge to fill it in."
        ),
        WITH_EXCEPTION: (
            "Apart from what the packet states, outside knowledge is not a "
            "permitted basis."
        ),
        DOUBLE_NEGATION: (
            "It is not permitted to disregard the restriction on outside "
            "knowledge."
        ),
        CROSS_SENTENCE_SCOPE: (
            "You may know things about this domain already.\n"
            "General ontology knowledge is nevertheless not a permitted basis."
        ),
        FIELD_NARROWING: (
            "Only the supplied items may be used; outside knowledge may not."
        ),
    },
    sc.GLOBAL_DEFAULT_PERMISSION: {
        DIRECT: (
            "Within the supplied packet, a decision basis may be considered "
            "unless this prompt explicitly prohibits it."
        ),
        PARAPHRASED: (
            "Anything this prompt does not prohibit remains available to you "
            "as a decision basis."
        ),
        CONDITIONAL: (
            "If a basis is not prohibited here, it may be considered."
        ),
        WITH_EXCEPTION: (
            "A decision basis may be considered unless prohibited, except "
            "where the packet says otherwise."
        ),
        DOUBLE_NEGATION: (
            "A basis this prompt does not prohibit is not thereby unavailable."
        ),
        CROSS_SENTENCE_SCOPE: (
            "This prompt lists several prohibitions.\n"
            "A decision basis may be considered unless it appears among them."
        ),
        FIELD_NARROWING: (
            "The permission covers the supplied evidence items, including "
            "their recorded fields."
        ),
    },
    sc.RECORDED_FIELDS_ACCESS: {
        DIRECT: (
            "The evidence-reading rule does not by itself prohibit evaluating "
            "the item's other recorded fields as source information."
        ),
        PARAPHRASED: (
            "An item's recorded fields remain available to you."
        ),
        CONDITIONAL: (
            "If an item carries recorded fields, those fields may be read."
        ),
        WITH_EXCEPTION: (
            "Other than the type-support rule, nothing here restricts the "
            "recorded fields."
        ),
        DOUBLE_NEGATION: (
            "It is not the case that the recorded fields are unavailable."
        ),
        CROSS_SENTENCE_SCOPE: (
            "Each item carries text and other attributes.\n"
            "Those recorded fields may be evaluated as source information."
        ),
        FIELD_NARROWING: (
            "The text determines type support; the recorded fields are a "
            "separate matter."
        ),
    },
    sc.CONFLICT_TO_DEFER_MAPPING: {
        DIRECT: (
            "Conflicting evidence requires you to defer."
        ),
        PARAPHRASED: (
            "When the items conflict, conflicting evidence must lead to defer."
        ),
        CONDITIONAL: (
            "If conflicting evidence is present, you must defer."
        ),
        WITH_EXCEPTION: (
            "Except where one item is decisive, conflicting evidence requires "
            "defer."
        ),
        DOUBLE_NEGATION: (
            "It is not optional: conflicting evidence requires defer."
        ),
        CROSS_SENTENCE_SCOPE: (
            "The two items disagree.\n"
            "Conflicting evidence requires defer in that situation."
        ),
        FIELD_NARROWING: (
            "For text conflicts specifically, conflicting evidence requires "
            "defer."
        ),
    },
}

# NEGATIVE fixtures: the family is genuinely absent. A capable compiler must
# NOT report `present`. `NEARBY_NON_POLICY` is sec 9.6's own trap -- prose
# that sits near the policy vocabulary without being a policy statement.
NEGATIVE_FIXTURES: dict[str, dict[str, str]] = {
    sc.SOURCE_META_REASONING_PROHIBITION: {
        NEARBY_NON_POLICY: (
            "Evidence items are drawn from a repository and presented to you "
            "as a packet. Each item records where it came from."
        ),
        DIRECT: "Choose select_type only if exactly one allowed type is warranted.",
    },
    sc.EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION: {
        NEARBY_NON_POLICY: (
            "The packet contains two evidence items. Read both before "
            "deciding."
        ),
        DIRECT: "Cite the evidence item ids that support the selected type.",
    },
    sc.OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION: {
        NEARBY_NON_POLICY: (
            "The concept and feature named below come from an ontology used "
            "elsewhere in the repository."
        ),
        DIRECT: "Output JSON using h1a_observation_v1.",
    },
    sc.GLOBAL_DEFAULT_PERMISSION: {
        NEARBY_NON_POLICY: (
            "This prompt states several rules. Follow them exactly as "
            "written."
        ),
        DIRECT: "If decision is defer, selected_type must be null.",
    },
    sc.RECORDED_FIELDS_ACCESS: {
        NEARBY_NON_POLICY: (
            "Each evidence item has an id and a body of text."
        ),
        DIRECT: "Do not output repair, accept_report, or abstain.",
    },
    sc.CONFLICT_TO_DEFER_MAPPING: {
        NEARBY_NON_POLICY: (
            "The presence of conflicting evidence does not by itself require "
            "either selection or deferral."
        ),
        DIRECT: "Choose defer if neither allowed type is uniquely warranted.",
    },
}


def evaluate_family(policy_id: str) -> dict:
    """Run every fixture for one family and report what actually happened."""
    detector = sc._DETECTORS[policy_id]

    positives = {}
    for form, text in POSITIVE_FIXTURES.get(policy_id, {}).items():
        found, _, _ = detector(text)
        positives[form] = found

    negatives = {}
    for form, text in NEGATIVE_FIXTURES.get(policy_id, {}).items():
        found, _, _ = detector(text)
        negatives[form] = not found  # pass == did NOT false-positive

    has_both = bool(positives) and bool(negatives)
    return {
        "policy_id": policy_id,
        "positive": positives,
        "negative": negatives,
        "recall_misses": sorted(f for f, ok in positives.items() if not ok),
        "false_positives": sorted(f for f, ok in negatives.items() if not ok),
        # sec 9.6 requires BOTH directions; a family with only positives is
        # not demonstrated, however many of them pass.
        "proven": has_both and all(positives.values()) and all(negatives.values()),
    }


def evaluate_capability() -> dict:
    """The whole gate. `proven_families` is DERIVED here, never declared."""
    families = {pid: evaluate_family(pid) for pid in sc.POLICY_FAMILIES}
    proven = frozenset(pid for pid, r in families.items() if r["proven"])
    return {
        "record_class": "h1a_compiler_capability",
        "ruling": "D-H1a-13 Q13.6 sec 9.6",
        "families": families,
        "proven_families": proven,
        "unproven_families": frozenset(sc.POLICY_FAMILIES) - proven,
        "target_critical_unproven": sorted(sc.TARGET_CRITICAL - proven),
    }


def proven_families() -> frozenset:
    """What `compile_policy_graph` may treat as capable of verified absence."""
    return evaluate_capability()["proven_families"]
