"""Independent bounded semantic compiler -- D-H1a-13 Q13.6 (freeze condition 4/5).

WHAT THIS IS, AND WHAT IT IS NOT
---------------------------------
Q13.6 sec 9.4 is explicit about the direction of authority:

    Policy DSL -> Deterministic Renderer -> Rendered Prompt
                                                 |
                                    Independent Semantic Compiler
                                                 |
                                        Observed Policy Graph
                                                 |
                                   compared to Expected Policy Graph

The canonical artifact is the typed policy DSL (`_h1a_policy.DECISION_BASIS_POLICY`
+ the carrier registry + the rendering contract). This module does NOT produce
it and does not get to define policy. It reads the rendered natural language
and reports what it observes there, so that a DRIFT between the two can be
detected.

INDEPENDENCE IS THE POINT, SO THIS MODULE MUST NOT IMPORT THE POLICY
---------------------------------------------------------------------
`_h1a_policy` already contains `AXIS_SURFACE_TOKENS`, and assertion 12 checks
the rendered prose against it. If this compiler reused that list, it would be
checking the renderer against the renderer's own vocabulary and would agree
with it by construction -- the "true proposition asserted about the wrong
object" failure this experiment has now hit twice (F10, and the 2026-08-16
subject-hash guard). So: **this module imports nothing from `_h1a_policy` or
`_h1a_contract`.** Its detectors are written against the prompt text as a
reader would meet it. The comparison against the expected graph happens in the
caller, where both sides are visible and separate.

FAIL-CLOSED BY CONSTRUCTION (sec 9.6)
--------------------------------------
Q13.6 sec 9.6: a family's SILENCE may be read as `absent_verified` only after
the compiler has demonstrated it can detect that family across an adversarial
fixture set (paraphrase, conditional form, exception clause, double negation,
dangling reference, cross-sentence scope, field narrowing, a nearby
non-policy sentence, ...). Undemonstrated -> return `unknown`.

That is enforced structurally rather than remembered: `compile_policy_graph`
takes `proven_families`, and a family outside that set can never come back
`absent_verified` -- only `present` (something was actually found) or
`unknown`. A compiler that detects nothing is useless but harmless; a
compiler that reports `absent_verified` without proven recall is how a
prohibition silently survives in an arm that is supposed to be free of it,
which is the exact defect (D-H1a-10) that made the first cohort
non-identifying.

`proven_families` is COMPUTED by the capability suite
(`test_h1a_semantic_compiler.py`), never hand-maintained here.

ASSURANCE CEILING (sec 9.5)
----------------------------
Nothing this module emits may exceed `SEMANTIC_REVIEWED`. Even when a rule
engine computes deterministically over the observed graph, the conclusion is
capped by its input:  A_final = min(A_semantic_graph, A_rule_result).

Stdlib only.
"""

from __future__ import annotations

import re

# --- sec 9.2 vocabulary ---------------------------------------------------

PRESENT = "present"
ABSENT_VERIFIED = "absent_verified"
UNKNOWN = "unknown"
STATES = (PRESENT, ABSENT_VERIFIED, UNKNOWN)

FORBIDDEN = "forbidden"
ALLOWED_BY_DEFAULT = "allowed_by_default"
REQUIRED = "required"
NEUTRAL = "neutral"
POLARITIES = (FORBIDDEN, ALLOWED_BY_DEFAULT, REQUIRED, NEUTRAL)

KEPT = "kept"
REMOVED = "removed"
ARMS = (KEPT, REMOVED)

# sec 9.5: the ceiling. Named here so a caller cannot promote a claim by
# forgetting what produced it.
ASSURANCE_CEILING = "SEMANTIC_REVIEWED"

# --- sec 9.3 certified policy families ------------------------------------

GLOBAL_DEFAULT_PERMISSION = "GLOBAL_DEFAULT_PERMISSION"
SOURCE_META_REASONING_PROHIBITION = "SOURCE_META_REASONING_PROHIBITION"
OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION = "OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION"
EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION = (
    "EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION"
)
EVIDENCE_COUNT_PROHIBITION = "EVIDENCE_COUNT_PROHIBITION"
CONFLICT_TO_DEFER_MAPPING = "CONFLICT_TO_DEFER_MAPPING"
RECORDED_FIELDS_ACCESS = "RECORDED_FIELDS_ACCESS"
TEXT_TYPE_SUPPORT_RULE = "TEXT_TYPE_SUPPORT_RULE"

POLICY_FAMILIES = (
    GLOBAL_DEFAULT_PERMISSION,
    SOURCE_META_REASONING_PROHIBITION,
    OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION,
    EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION,
    EVIDENCE_COUNT_PROHIBITION,
    CONFLICT_TO_DEFER_MAPPING,
    RECORDED_FIELDS_ACCESS,
    TEXT_TYPE_SUPPORT_RULE,
)

# sec 9.3 "별도 구조 항목" -- structural, not policy-family, checks.
DANGLING_REFERENCE = "DANGLING_REFERENCE"
EXPERIMENT_ARM_DISCLOSURE = "EXPERIMENT_ARM_DISCLOSURE"
DUPLICATE_CARRIER = "DUPLICATE_CARRIER"
# Q13.1 renamed `source_order` because it read as BOTH presentation order and
# source-kind priority -- one non-target axis quietly covering the target one.
# Reverting to the ambiguous wording restores that defect while leaving the
# policy "present", so presence alone cannot catch it.
AMBIGUOUS_AXIS_PHRASING = "AMBIGUOUS_AXIS_PHRASING"
# R5, 2026-08-16: absence of a conflict-to-defer hard mapping is NECESSARY but
# not SUFFICIENT for decision-mapping neutrality. Nothing in the family
# vocabulary asks whether the select and defer branches actually partition the
# outcome space, so a prompt could leave a gap (neither branch licensed) or an
# overlap (both licensed) while CONFLICT_TO_DEFER_MAPPING reads absent_verified.
DECISION_BRANCH_PARTITION = "DECISION_BRANCH_PARTITION"

STRUCTURAL_ITEMS = (
    DANGLING_REFERENCE, EXPERIMENT_ARM_DISCLOSURE, DUPLICATE_CARRIER,
    AMBIGUOUS_AXIS_PHRASING, DECISION_BRANCH_PARTITION,
)

# Q13.5: families where `unknown` is not an acceptable terminal state. Listed
# here for the caller's gate; this module still RETURNS unknown when that is
# the honest answer -- forcing a verdict is what the list exists to prevent.
TARGET_CRITICAL = frozenset({
    SOURCE_META_REASONING_PROHIBITION,
    OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION,
    EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION,
    CONFLICT_TO_DEFER_MAPPING,
    RECORDED_FIELDS_ACCESS,
    GLOBAL_DEFAULT_PERMISSION,
})


# A policy sentence carrying an exception clause does not state an
# unconditional rule: its state depends on whether the antecedent fires. The
# 2026-08-16 independent review (R3) found the compiler reporting a flat
# `present` for the tie-breaker prohibition even though it reads "...unless the
# packet explicitly authorizes that basis", so whether it actually binds
# depends on payload content the compiler never inspected. R3 did that check by
# hand. An instrument that reports a conditional rule as unconditional invites
# exactly that manual rescue.
_EXCEPTION_CLAUSE = re.compile(
    r"(?:,\s*)?\b(?:unless|except(?:\s+(?:where|when|for))?|other than)\b[^.]*",
    re.IGNORECASE,
)


def _condition_on(span: str) -> "str | None":
    """The exception clause qualifying a rule, if it carries one."""
    if not span:
        return None
    match = _EXCEPTION_CLAUSE.search(span)
    return match.group(0).strip(" ,") if match else None


class CompilerContractError(Exception):
    """The caller violated this module's preconditions."""


# --- sentence segmentation -------------------------------------------------

def _sentences(text: str) -> list[str]:
    """Split into inspectable units.

    Bullets are units too: the rendered prompt carries several prohibitions as
    list items, and a splitter that only broke on '.' would fuse a bullet with
    its neighbour and make scope attribution wrong.
    """
    units: list[str] = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        for piece in re.split(r"(?<=[.!?])\s+", line):
            piece = piece.strip()
            if piece:
                units.append(piece)
    return units


def _join_wrapped(text: str) -> str:
    """The rendered prompt hard-wraps, so a single rule spans several lines.

    Detectors that matched line-by-line would miss any rule whose subject and
    verb land on different lines -- which is most of them, and exactly the
    'cross-sentence scope' case sec 9.6 requires the compiler to survive.
    """
    return re.sub(r"\s+", " ", text)


# --- detectors -------------------------------------------------------------
# Each returns (found: bool, span: str, polarity: str). They are written
# against the prompt as a reader meets it, NOT against the policy module's
# token table -- see the module docstring on independence.

_NEGATED_PROHIBITION = re.compile(
    r"\b(?:does not|do not|is not|are not|shall not|must not|never)\b",
    re.IGNORECASE,
)


def _find_rule(text: str, subject_patterns: tuple[str, ...]) -> tuple[bool, str]:
    """Locate a sentence that carries one of the subject phrasings."""
    flat = _join_wrapped(text)
    for sentence in re.split(r"(?<=[.!?])\s+", flat):
        for pattern in subject_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return True, sentence.strip()
    return False, ""


def _detect_evidence_count(text: str):
    found, span = _find_rule(text, (r"evidence item count", r"evidence count"))
    return found, span, FORBIDDEN if found else NEUTRAL


def _detect_presentation_order(text: str):
    found, span = _find_rule(
        text,
        (r"order in which evidence items appear", r"presentation order", r"source order"),
    )
    return found, span, FORBIDDEN if found else NEUTRAL


def _detect_outside_domain(text: str):
    found, span = _find_rule(
        text,
        (r"outside domain or ontology knowledge",
         r"general ontology knowledge",
         r"outside knowledge"),
    )
    return found, span, FORBIDDEN if found else NEUTRAL


def _detect_source_meta_reasoning(text: str):
    """Q1's liveness/source-priority prohibition -- the manipulated axis.

    Both language surfaces are scanned. The frozen clause is Korean; an
    English restatement would be a residual prohibition and must not be
    read as absence.
    """
    found, span = _find_rule(
        text,
        (r"liveness", r"재판정", r"우선순위", r"더 최신", r"더 권위",
         r"살아있는 코드", r"source priority", r"which source is more recent",
         r"more authoritative"),
    )
    return found, span, FORBIDDEN if found else NEUTRAL


_PERMISSION_EXPRESSION = re.compile(
    r"\b(?:may be considered|may be used|may consider|remains available"
    r"|is (?:still )?available"
    # Double negation of unavailability -- sec 9.6 lists 이중 부정 as a form
    # the compiler must survive. Written against the CONSTRUCTION (a negation
    # scoping over a negative-availability word) rather than against any one
    # sentence, so it generalises past the fixture that exposed the gap.
    r"|not\s+(?:\w+\s+){0,2}(?:unavailable|disallowed|impermissible|barred"
    r"|off[- ]limits|excluded))\b",
    re.IGNORECASE,
)
_PROHIBITION_REFERENCE = re.compile(
    r"\b(?:unless|prohibit\w*|forbid\w*|disallow\w*)\b", re.IGNORECASE
)


def _detect_global_default_permission(text: str):
    """The default-permission rule: a basis is available UNLESS prohibited.

    Matched by co-occurrence of a permission expression and a reference to
    prohibition in one sentence, rather than by fixed phrasings. The capability
    gate showed why: the conditional form ("If a basis is not prohibited here,
    it may be considered.") carries neither "may be considered unless" nor
    "does not prohibit", so a phrase list missed it while the rule was plainly
    present. Requiring BOTH halves is what keeps this from firing on any
    sentence that merely contains "unless".
    """
    flat = _join_wrapped(text)
    for sentence in re.split(r"(?<=[.!?])\s+", flat):
        if _PERMISSION_EXPRESSION.search(sentence) and _PROHIBITION_REFERENCE.search(sentence):
            return True, sentence.strip(), ALLOWED_BY_DEFAULT
    return False, "", NEUTRAL


def _detect_recorded_fields_access(text: str):
    found, span = _find_rule(
        text, (r"recorded fields", r"other recorded fields", r"recorded field")
    )
    return found, span, ALLOWED_BY_DEFAULT if found else NEUTRAL


def _detect_text_type_support_rule(text: str):
    found, span = _find_rule(
        text,
        (r"directly states or\s+clearly entails", r"directly states or clearly entails",
         r"treat an evidence item as support only when"),
    )
    return found, span, REQUIRED if found else NEUTRAL


def _detect_conflict_to_defer_mapping(text: str):
    """Q7=E: conflict must NOT be hard-mapped to defer.

    The rendered contract states the NON-mapping ("does not by itself require
    either selection or deferral"). A hard mapping would instead say conflict
    requires defer, so polarity distinguishes the two readings rather than
    mere presence.
    """
    flat = _join_wrapped(text)

    # The explicit NON-mapping must be recognised first. It contains every
    # word the hard-mapping pattern looks for ("conflicting evidence",
    # "require", "deferral") while asserting the opposite, so a detector that
    # checked for the hard mapping first would report the ruled-in rule as if
    # it were the ruled-out one. The capability gate caught exactly that:
    # the sec 9.6 "가까운 비정책 문장" fixture is this sentence, taken from the
    # live rendered prompt, and the detector fired on it.
    #
    # `found` means "a hard conflict->defer mapping is present", so this
    # branch is found=False. That is what the family NAME claims, and a
    # detector whose boolean disagrees with its own name will be misread by
    # every caller.
    non_mapping = re.search(
        r"conflicting evidence does not by itself require"
        r"|does not by itself require either selection or deferral",
        flat, re.IGNORECASE,
    )
    if non_mapping:
        return False, non_mapping.group(0).strip(), NEUTRAL

    hard = re.search(
        r"conflicting evidence[^.]*\b(?:requires?|must)\b[^.]*\bdefer",
        flat, re.IGNORECASE,
    )
    if hard:
        return True, hard.group(0).strip(), REQUIRED
    return False, "", NEUTRAL


_DETECTORS = {
    EVIDENCE_COUNT_PROHIBITION: _detect_evidence_count,
    EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION: _detect_presentation_order,
    OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION: _detect_outside_domain,
    SOURCE_META_REASONING_PROHIBITION: _detect_source_meta_reasoning,
    GLOBAL_DEFAULT_PERMISSION: _detect_global_default_permission,
    RECORDED_FIELDS_ACCESS: _detect_recorded_fields_access,
    TEXT_TYPE_SUPPORT_RULE: _detect_text_type_support_rule,
    CONFLICT_TO_DEFER_MAPPING: _detect_conflict_to_defer_mapping,
}


# --- structural checks (sec 9.3 별도 구조 항목) ----------------------------

_REFERRING_EXPRESSION = re.compile(
    r"\b(?:that (?:clause|sentence|rule|prohibition)|the (?:above|preceding|"
    r"arm-specific) [a-z-]+(?: clause| rule)?)\b",
    re.IGNORECASE,
)

_ARM_METALANGUAGE = re.compile(
    r"\b(?:arm|condition group|treatment(?: condition)?|experimental group|"
    r"PROHIBITION_KEPT|PROHIBITION_REMOVED|control group)\b"
)


def detect_dangling_reference(text: str) -> list[dict]:
    """A referring expression whose referent is not present in this arm.

    This is the defect class that produced D-H1a-13 in the first place: the
    ruling's own prescribed sentence referred to an "arm-specific
    source-evaluation clause" that does not exist in REMOVED.
    """
    flat = _join_wrapped(text)
    claims = []
    for match in _REFERRING_EXPRESSION.finditer(flat):
        expression = match.group(0)
        # A reference to an "arm-specific ... clause" resolves only if some
        # arm-specific clause is actually rendered here.
        resolved = None
        if re.search(r"arm-specific", expression, re.IGNORECASE):
            resolved = None
        claims.append({
            "expression": expression,
            "resolved_to": resolved,
            "source_span": match.group(0),
        })
    return claims


def detect_experiment_arm_disclosure(text: str) -> list[str]:
    """Model-facing prompts must not name the experimental structure."""
    flat = _join_wrapped(text)
    return sorted({m.group(0) for m in _ARM_METALANGUAGE.finditer(flat)})


_AMBIGUOUS_PHRASINGS = {
    "source order": (
        "Q13.1 renamed this axis because 'source order' reads as both "
        "presentation order and source-kind priority. The disambiguated "
        "wording is 'the order in which evidence items appear in the packet'."
    ),
}


def detect_ambiguous_axis_phrasing(text: str) -> list[dict]:
    flat = _join_wrapped(text).lower()
    return [
        {"phrasing": phrase, "why": why}
        for phrase, why in sorted(_AMBIGUOUS_PHRASINGS.items())
        if phrase in flat
    ]


_SELECT_BRANCH = re.compile(
    r"choose\s+select_type\s+(?:only\s+)?if\b([^.]*)", re.IGNORECASE)
_DEFER_BRANCH = re.compile(
    r"choose\s+defer\s+if\b([^.]*)", re.IGNORECASE)


def detect_decision_branch_partition(text: str) -> dict:
    """Do the select and defer branches partition the outcome space?

    Reports, it does not decide. Literal complementarity is checkable
    (`defer if NOT <select condition>`); anything else needs a reader to judge
    whether the two conditions are complements under their intended reading,
    and saying otherwise would be the instrument claiming a semantic
    competence it does not have.

    Exists because R5 (2026-08-16) showed CONFLICT_TO_DEFER_MAPPING can read
    absent_verified while the branches still fail to partition -- absence of a
    hard mapping is necessary, not sufficient.
    """
    flat = _join_wrapped(text)
    select = _SELECT_BRANCH.search(flat)
    defer = _DEFER_BRANCH.search(flat)
    if not (select and defer):
        return {
            "branches_found": False,
            "literal_complement": None,
            "requires_reviewer_adjudication": True,
            "note": "one or both decision branches were not located",
        }

    select_cond = " ".join(select.group(1).split()).strip(" ,")
    defer_cond = " ".join(defer.group(1).split()).strip(" ,")
    negations = ("not ", "neither ", "no ")
    literal = any(defer_cond.lower().startswith(n) for n in negations) and (
        select_cond.lower().lstrip("not ").strip() in defer_cond.lower()
    )
    return {
        "branches_found": True,
        "select_condition": select_cond,
        "defer_condition": defer_cond,
        "literal_complement": literal,
        # Not a defect claim: non-literal wording can still be complementary
        # under the only coherent reading, which is a judgment for a reader.
        "requires_reviewer_adjudication": not literal,
        "note": (
            "The defer branch is not the literal negation of the select "
            "branch. That may still be complementary under the intended "
            "reading, but this module cannot establish it; a reviewer must."
        ) if not literal else "The defer branch is the literal negation.",
    }


def detect_repeated_mentions(text: str) -> dict[str, int]:
    """Sentences that each independently express a family -- a CANDIDATE list.

    ⚠️ This does NOT establish duplicate carriage, and must not be reported as
    if it did. Measured against the live prompt it returns 3 for the
    outside-domain family and 2 for several others, and inspection shows those
    are one policy elaborated across sentences, not two carriers. Deciding
    which it is needs the carrier registry, which lives on the EXPECTED-graph
    side -- and this module is forbidden from importing it (see the module
    docstring on independence), because a duplicate-carrier check that reads
    the carrier registry would agree with the renderer by construction.

    So this stays a candidate list for the reviewer and for the expected-graph
    comparison to resolve. Q10.2's real failure mode -- one prohibition carried
    twice, so deleting one carrier leaves the manipulation undone, which is
    what made the 2026-08-03 cohort non-identifying -- is exactly what the
    comparison step must settle, not this counter.
    """
    counts: dict[str, int] = {}
    for family, detector in _DETECTORS.items():
        flat = _join_wrapped(text)
        hits = 0
        for sentence in re.split(r"(?<=[.!?])\s+", flat):
            found, _, _ = detector(sentence)
            if found:
                hits += 1
        if hits > 1:
            counts[family] = hits
    return counts


# --- the compiler ----------------------------------------------------------

def compile_policy_graph(
    rendered_text: str, arm: str, proven_families: "frozenset[str] | None" = None
) -> dict:
    """Observe the rendered prompt and report a policy graph (sec 9.2).

    `proven_families` is the set whose detection capability the fixture suite
    has DEMONSTRATED (sec 9.6). Anything outside it can never be reported
    `absent_verified`; silence there is `unknown`. Default is the empty set,
    so an uninstrumented caller gets the safe answer rather than a confident
    wrong one.
    """
    if arm not in ARMS:
        raise CompilerContractError(f"arm must be one of {ARMS}, got {arm!r}")
    proven = frozenset(proven_families or frozenset())
    unknown_families = sorted(set(POLICY_FAMILIES) - proven)

    claims = []
    for family in POLICY_FAMILIES:
        found, span, polarity = _DETECTORS[family](rendered_text)
        if found:
            state = PRESENT
        elif family in proven:
            state = ABSENT_VERIFIED
        else:
            # sec 9.6: undemonstrated detection returns unknown, never a
            # verified absence.
            state = UNKNOWN
        condition = _condition_on(span) if found else None
        claims.append({
            "policy_id": family,
            "arm": arm,
            "state": state,
            "polarity": polarity,
            "carrier": None,
            "source_span": span or None,
            "scope": "rendered_prompt",
            "referents": [],
            "capability_proven": family in proven,
            # `present` alone would overstate a rule that only binds when its
            # antecedent fails to fire (R3, 2026-08-16).
            "conditional": condition is not None,
            "condition": condition,
            "condition_note": (
                "This rule carries an exception clause, so its effective state "
                "depends on content this module does not inspect (the payload). "
                "Resolving whether the antecedent fires requires reading that "
                "content."
            ) if condition else None,
        })

    dangling = detect_dangling_reference(rendered_text)
    for claim in claims:
        if claim["policy_id"] == GLOBAL_DEFAULT_PERMISSION:
            claim["referents"] = dangling

    return {
        "record_class": "h1a_observed_policy_graph",
        "arm": arm,
        "assurance": ASSURANCE_CEILING,
        "assurance_note": (
            "sec 9.5: never promoted to RULE_CHECKED or REASONER_PROVED. A "
            "downstream rule engine's conclusion is capped by this input: "
            "A_final = min(A_semantic_graph, A_rule_result)."
        ),
        "claims": claims,
        "structural": {
            DANGLING_REFERENCE: dangling,
            EXPERIMENT_ARM_DISCLOSURE: detect_experiment_arm_disclosure(rendered_text),
            AMBIGUOUS_AXIS_PHRASING: detect_ambiguous_axis_phrasing(rendered_text),
            DECISION_BRANCH_PARTITION: detect_decision_branch_partition(rendered_text),
            # Candidate list only -- see detect_repeated_mentions' docstring.
            DUPLICATE_CARRIER: {
                "repeated_mention_counts": detect_repeated_mentions(rendered_text),
                "establishes_duplicate_carriage": False,
                "note": (
                    "Repeated mention is not duplicate carriage. Resolving it "
                    "requires the carrier registry, which this module may not "
                    "read; the expected-graph comparison decides."
                ),
            },
        },
        "capability": {
            "proven_families": sorted(proven),
            "unproven_families": unknown_families,
            "note": (
                "Silence about an unproven family is reported as unknown, not "
                "as absent_verified (sec 9.6)."
            ),
        },
    }


def unresolved_target_critical(graph: dict) -> list[str]:
    """Target-critical families still `unknown` -- Q13.5 forbids leaving these.

    Returned rather than raised: this module reports, the freeze gate decides.
    """
    return sorted(
        claim["policy_id"] for claim in graph["claims"]
        if claim["policy_id"] in TARGET_CRITICAL and claim["state"] == UNKNOWN
    )
