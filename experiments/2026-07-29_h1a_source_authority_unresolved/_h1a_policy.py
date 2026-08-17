"""H1a decision-basis policy contract (D-H1a-10 Q10.2, revised by D-H1a-11).

WHY THIS MODULE EXISTS
----------------------
The 40-trial cohort of 2026-08-03 was ruled NON-IDENTIFYING (Q10=E). Both arms
kept a common Q7 warrant rule forbidding source_kind priority, recency,
authority and liveness as tie-breakers, so `PROHIBITION_REMOVED` never actually
permitted the mechanism the manipulation targets.

`assert_no_residual_prohibition` in `_h1a_contract.py` PASSED throughout, and
`test_guard_precision_the_clean_template_passes` actively certified the
template as clean. The guard was not buggy. It asserted the wrong proposition:

    asserted:  "Q1's clause bytes are absent from REMOVED"
    needed:    "no equivalent prohibition remains in REMOVED"

Q10.2 ordered that raised and forbade doing it with a closed keyword list. The
fix is structural: make a typed policy object canonical, generate the prompt
FROM it, and check the policy rather than the prose.

WHAT D-H1a-11 CHANGED IN THIS MODULE
------------------------------------
The first version of this file (commit 2aed01a) made design choices that Q11
had not yet ruled on. D-H1a-11 overrode four of them:

1. `carriers` was a TUPLE per axis. Now exactly ONE carrier per axis x arm
   (ruling sec 8, structural assertion 2). A state decided by two carriers is
   the Q10 defect by construction.
2. `outside_knowledge` declared PACKET_BOUNDARY as a second carrier. The ruling
   (sec 8) says packet-boundary / evidence-scope sentences are NOT carriers --
   they are `scope_constraints`, recorded separately, and only count as a
   carrier if they flip an axis to forbidden. So its carrier is Q7 alone.
3. `allowed` was one flat state. Now four states, and REMOVED's target axes are
   `allowed_by_default` -- explicitly NOT `unspecified` (ruling sec 9). The
   distinction is the whole point of Q11=D.
4. `REMOVED_ALLOWED_RENDERING` was None and fail-closed pending Q11. Q11 is
   ruled: option D, a common default-permission rule in BOTH arms and NO
   axis-specific permission text in REMOVED. The fail-closed gate is replaced
   by the ruling's own five freeze conditions.

WHY Q11=D RATHER THAN SILENCE
-----------------------------
Under pure silence, REMOVED would have neither a prohibition nor a permission,
and the surrounding scope constraints ("use only the packet") could still be
read as forbidding source-property reasoning. Another both-arms deferral pile
would then be undecidable between "permitted but no effect" and "silence not
read as permission" -- which is Q10's failure mode a second time. The common
default-permission rule makes the permission explicit at policy level while
keeping it byte-identical across arms, so it cannot act as an arm-specific
demand characteristic the way an axis-enumerating permission sentence would.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import textwrap

# Wrapping matches the surrounding template's existing style (76-column body,
# two-space continuation under a "- " bullet). Matching it is deliberate: R1
# mandates removing four axes from the list, not reflowing the prompt, and an
# unwrapped single line would be a surface change no ruling asked for.
_WRAP_WIDTH = 76
_BULLET_INDENT = "  "

# --------------------------------------------------------------------------
# Policy axes
# --------------------------------------------------------------------------
AXES = (
    "evidence_count",
    "evidence_item_presentation_order",
    "outside_domain_knowledge",
    "external_source_retrieval",
    "source_meta_reasoning",
)

# D-H1a-13 Q13.1 (2026-08-06): renamed from `source_order`. The old name was
# ambiguous between two distinct policies -- the order evidence items are
# PRESENTED in the packet (non-target, this axis) and prioritizing one
# SOURCE over another by kind (target, `source_meta_reasoning`'s
# `source_kind_priority` subaxis). Because `source_order` could plausibly
# read as either, rendering it in the common tie-breaker sentence risked
# re-forbidding the target axis in BOTH arms -- the exact Q10 defect shape,
# just with the ambiguity moved into a single word instead of a whole
# clause. The rename makes what this axis governs unambiguous from its name
# alone: only presentation order, never source priority.

# D-H1a-12 Q12=F: the four former target axes are now SUBAXES of
# source_meta_reasoning, which is a sibling of outside_domain_knowledge
# (no subsumption in either direction).
SUBAXES = {
    "source_meta_reasoning": (
        "source_kind_priority", "recency", "authority", "liveness",
    ),
}

TARGET_AXES = frozenset({"source_meta_reasoning"})
NONTARGET_AXES = frozenset(AXES) - TARGET_AXES

ARMS = ("PROHIBITION_KEPT", "PROHIBITION_REMOVED")
_ARM_KEY = {"PROHIBITION_KEPT": "kept", "PROHIBITION_REMOVED": "removed"}

# --------------------------------------------------------------------------
# States (D-H1a-11 sec 9)
# --------------------------------------------------------------------------
# Four states, not two. `allowed_by_default` and `unspecified` are different
# claims: the first says a rule in the prompt grants permission, the second
# says nothing addresses the axis at all. Q11=D exists precisely to keep
# REMOVED's target axes out of `unspecified`.
EXPLICITLY_FORBIDDEN = "explicitly_forbidden"
ALLOWED_BY_DEFAULT = "allowed_by_default"
EXPLICITLY_ALLOWED = "explicitly_allowed"
UNSPECIFIED = "unspecified"

STATES = (EXPLICITLY_FORBIDDEN, ALLOWED_BY_DEFAULT, EXPLICITLY_ALLOWED, UNSPECIFIED)
_FORBIDDING_STATES = frozenset({EXPLICITLY_FORBIDDEN})
_PERMITTING_STATES = frozenset({ALLOWED_BY_DEFAULT, EXPLICITLY_ALLOWED})

# --------------------------------------------------------------------------
# Carriers (D-H1a-11 sec 8)
# --------------------------------------------------------------------------
# A carrier is "the single authoritative path that normatively determines this
# axis's final policy state" -- not merely a sentence containing the word. One
# carrier may govern several axes; one axis x arm may have only one carrier.
CARRIER_Q1 = "Q1_LIVENESS_CLAUSE"              # KEPT only; Q1=B / Q5=B frozen bytes
CARRIER_Q7 = "Q7_NON_TARGET_TIEBREAKER"        # both arms; generated here
CARRIER_DOMAIN = "DOMAIN_KNOWLEDGE_BOUNDARY"   # both arms (D-H1a-12 sec 5)
CARRIER_DEFAULT = "GLOBAL_DEFAULT_PERMISSION"  # both arms, byte-identical

CARRIERS = (CARRIER_Q1, CARRIER_Q7, CARRIER_DOMAIN, CARRIER_DEFAULT)

# Which carriers can express which kind of state. Structural assertions 3 and 4
# check the pairing, so a `forbidden` state can never be attributed to the
# default-permission rule and vice versa.
_CARRIER_SEMANTICS = {
    CARRIER_Q1: _FORBIDDING_STATES,
    CARRIER_Q7: _FORBIDDING_STATES,
    CARRIER_DOMAIN: _FORBIDDING_STATES,
    CARRIER_DEFAULT: frozenset({ALLOWED_BY_DEFAULT}),
}

# Scope constraints are NOT carriers (ruling sec 8). They bound where evidence
# may come from without flipping any axis to forbidden, so they are recorded
# here for the audit trail and deliberately excluded from carrier cardinality.
SCOPE_CONSTRAINTS = ("PACKET_ONLY", "NO_EXTERNAL_SOURCES", "SCOPE_DISAMBIGUATION")

# D-H1a-12 sec 4, third sentence -- REPAIRED by D-H1a-13 Q13 (2026-08-06).
#
# The original two-sentence form's second sentence, "Source evaluation is
# governed by the arm-specific source-evaluation clause.", is a dangling
# reference in PROHIBITION_REMOVED: it names Q1's clause, which exists only
# in KEPT (referent_in_removed: none). Independent review 20260806 (axis b,
# BLOCKER) found this contradicts D-H1a-11's own default-permission design --
# the sentence asserts a governing rule exists in REMOVED too, which makes
# whether default-permission even applies there ambiguous, and it names the
# realized policy in model-facing prose, disclosing experiment structure
# ("arm-specific") to the trial subject. D-H1a-13 Q13 = C: delete the second
# sentence in BOTH arms; keep the first, which still does the real job (domain
# knowledge boundary does not itself decide source evaluation) without
# claiming a referent that isn't there in REMOVED.
#
# NOT a carrier: it flips no axis to forbidden. Byte-identical in both arms.
SCOPE_DISAMBIGUATION_ID = "SCOPE_DISAMBIGUATION"
SCOPE_DISAMBIGUATION_TEXT = (
    "- The restriction on outside domain or ontology knowledge does not "
    "itself govern evaluation of the supplied evidence items as sources."
)

# D-H1a-12 sec 4, second sentence. Carrier for outside_domain_knowledge and
# external_source_retrieval in BOTH arms.
DOMAIN_BOUNDARY_TEXT = (
    "- Do not use outside domain or ontology knowledge to supply facts about "
    "the concept-feature relation, and do not consult external sources."
)

# The scope constraint's own bytes (template lines 39-41, present verbatim and
# identically in both arms -- it predates D-H1a-11 and is Q3=B's packet-
# boundary preamble). Its wording legitimately says "Do not use ... external
# sources", which co-occurs with `outside_knowledge`'s surface tokens under the
# same verb-proximity test assert_5 and assert_6b use. That overlap is
# EXPECTED, not a duplicate carrier -- the ruling excludes scope constraints
# from carrier cardinality precisely because they are arm-invariant and cannot
# create or destroy an arm contrast. It must be excluded from the "text outside
# known carriers" scan the same way the Q1 clause and Q7 block are, or the scan
# false-positives on this sentence every time. Loaded as a constant here
# (rather than from the template) so a template edit that changes this
# sentence is caught by drift, not silently tolerated.
SCOPE_CONSTRAINT_TEXT = (
    "Input is a repo-derived evidence packet. Use only the packet fields "
    "presented in this prompt. Do not use general ontology knowledge, "
    "OWL/GUFO background knowledge, codebase memory, prior conversation "
    "context, or external sources."
)

# --------------------------------------------------------------------------
# Default permission (D-H1a-11 sec 1 / sec 5) -- byte-exact from the ruling
# --------------------------------------------------------------------------
# D-H1a-12 sec 7 rewrote the second sentence. The old wording ("Permission to
# consider a basis does not by itself warrant selecting a type") could be read
# as "that basis is not a warrant" -- which, under Q12's finding that
# source-meta reasoning is the only arm difference, would cancel the treatment
# itself. The replacement separates two propositions that the old sentence
# conflated:
#     permission status alone  != evidence
#     permitted basis applied to evidence = potentially relevant
#
# D-H1a-13 Q13.2 (2026-08-06) extended the third sentence and added a fourth.
# The old text said a permitted basis "may affect the decision only through
# its application to the supplied evidence" without saying whether "evidence"
# means the item's text alone or also its other recorded fields (e.g.
# source_kind) -- exactly the split source_meta_reasoning's permission in
# REMOVED needs, since that permission is specifically about evaluating an
# item's recorded fields as source information, not about what its text
# supports. The evidence-reading rule (declared elsewhere in the template)
# already governs text-support; this addition states explicitly that it does
# not ALSO prohibit reading an item's other recorded fields as source
# information -- separating "what type does this text support" from "how do I
# evaluate this item as a source" into two non-conflicting rules.
GLOBAL_DEFAULT_PERMISSION_TEXT = (
    "Within the supplied packet, a decision basis may be considered unless this\n"
    "prompt explicitly prohibits it. The fact that this prompt does not prohibit\n"
    "a decision basis is not itself a reason to select a type. A permitted basis\n"
    "may affect the decision only through its application to the supplied\n"
    "evidence items, including their recorded fields. The evidence-reading rule\n"
    "above determines what ontology type an item's text supports; it does not\n"
    "by itself prohibit evaluating the item's other recorded fields as source\n"
    "information."
)

POLICY_DEFAULTS = {
    "packet_internal_decision_basis": {
        "state": ALLOWED_BY_DEFAULT,
        "carrier": CARRIER_DEFAULT,
        # The second sentence is the demand neutralizer the ruling requires:
        # permission must not read as encouragement to select.
        "non_directive": True,
    }
}

# --------------------------------------------------------------------------
# The frozen policy table (D-H1a-11 sec 7 / sec 9)
# --------------------------------------------------------------------------
# Q11.2=A: this table is a preregistration device, not an implementation
# detail. Changing it is an experiment amendment, not a renderer refactor.
DECISION_BASIS_POLICY: dict[str, dict[str, dict[str, str]]] = {
    "evidence_count": {
        "kept": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q7},
        "removed": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q7},
    },
    "evidence_item_presentation_order": {
        "kept": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q7},
        "removed": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q7},
    },
    "outside_domain_knowledge": {
        "kept": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_DOMAIN},
        "removed": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_DOMAIN},
    },
    "external_source_retrieval": {
        "kept": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_DOMAIN},
        "removed": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_DOMAIN},
    },
    "source_meta_reasoning": {
        "kept": {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q1},
        "removed": {"state": ALLOWED_BY_DEFAULT, "carrier": CARRIER_DEFAULT},
    },
}

# Literal strings and declared semantic aliases per axis. Used ONLY to check
# rendered prose against the policy -- never to define policy, and never as the
# primary proof of absence (Q10.2 forbids that). Semantic completeness is not
# certifiable here; the guarantee comes from generating prose from the policy
# object. Assertion 12 uses this list and says so in its own message.
AXIS_SURFACE_TOKENS: dict[str, tuple[str, ...]] = {
    "evidence_count": ("evidence item count", "evidence count"),
    "evidence_item_presentation_order": (
        "order in which evidence items appear", "presentation order",
    ),
    "outside_domain_knowledge": ("outside domain", "ontology knowledge",
                                 "general ontology"),
    "external_source_retrieval": ("external sources", "consult external"),
    # D-H1a-12: the target axis is now the parent category; its subaxis
    # tokens all belong to it.
    "source_meta_reasoning": ("source_kind priority", "source_kind", "우선순위",
                              "recency", "more recent", "더 최신", "최신인지",
                              "authority", "authoritative", "권위",
                              "liveness", "still live", "살아있는"),
}

_Q7_AXIS_PHRASE = {
    "evidence_count": "evidence item count",
    "evidence_item_presentation_order": (
        "the order in which evidence items appear in the packet"
    ),
}


def _normalize_ws(text: str) -> str:
    """Collapse whitespace runs to single spaces, lowercased.

    Required, not cosmetic. Surface tokens are multi-word phrases and the
    template wraps at 76 columns, so a phrase can be split across a newline
    plus indent. Matching raw text would then miss an axis that IS present -- a
    false negative in the exact guard whose predecessor already failed this
    experiment once. Caught by a test when wrapping was introduced.
    """
    return " ".join(text.split()).lower()


class PolicyContractError(Exception):
    """A structural or deductive policy check failed. Never proceed."""


class FreezeGateBlocked(PolicyContractError):
    """A D-H1a-11 freeze condition is unmet."""


# --------------------------------------------------------------------------
# Deterministic renderer
# --------------------------------------------------------------------------
def state_of(axis: str, arm: str) -> str:
    return DECISION_BASIS_POLICY[axis][_ARM_KEY[arm]]["state"]


def carrier_of(axis: str, arm: str) -> str:
    return DECISION_BASIS_POLICY[axis][_ARM_KEY[arm]]["carrier"]


def _q7_forbidden_axes(arm: str) -> list[str]:
    """Axes this arm forbids *via the Q7 list*, in AXES order (deterministic)."""
    return [
        a for a in AXES
        if carrier_of(a, arm) == CARRIER_Q7
        and state_of(a, arm) in _FORBIDDING_STATES
    ]


def _join_english(phrases: list[str]) -> str:
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]} or {phrases[1]}"
    return ", ".join(phrases[:-1]) + f", or {phrases[-1]}"


def _bullet(body: str) -> str:
    return "\n".join(
        textwrap.wrap(
            f"- {body}",
            width=_WRAP_WIDTH,
            subsequent_indent=_BULLET_INDENT,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


def render_policy_block(arm: str) -> list[tuple[str, str]]:
    """Return [(carrier_id, text)] for this arm's policy-bearing prose.

    Returning provenance pairs rather than a blob is what makes Q10.2's
    requirement 5 ("every rendered policy sentence traceable to its policy ID")
    checkable instead of merely asserted.

    Under Q11=D there is no `allowed_rendering` parameter any more: the default
    permission is emitted in BOTH arms, byte-identically, and no arm gets
    axis-specific permission text. The arm contrast is carried entirely by
    Q1's clause, which `_h1a_contract.py` inserts.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")

    out: list[tuple[str, str]] = [(CARRIER_DEFAULT, GLOBAL_DEFAULT_PERMISSION_TEXT)]

    # Sentence 1 (D-H1a-12 sec 4): non-target tie-breakers only.
    forbidden = _q7_forbidden_axes(arm)
    if forbidden:
        missing = [a for a in forbidden if a not in _Q7_AXIS_PHRASE]
        if missing:
            # An axis is carried by the tie-breaker sentence but has no
            # declared phrase for it. Raise the contract error rather than
            # KeyError: a bare KeyError here reads as a crash, while this is a
            # policy/renderer disagreement -- exactly the class of defect this
            # module exists to surface. Found by
            # test_freeze_gate_runs_the_machine_checkable_conditions_before_failing
            # when D-H1a-12's split left the target axis without a phrase.
            raise PolicyContractError(
                f"[render] axes carried by {CARRIER_Q7} have no declared "
                f"phrase in _Q7_AXIS_PHRASE: {missing}"
            )
        phrase = _join_english([_Q7_AXIS_PHRASE[a] for a in forbidden])
        out.append((
            CARRIER_Q7,
            _bullet(
                f"Do not break ties using {phrase}, unless the packet "
                f"explicitly authorizes that basis."
            ),
        ))

    # Sentence 2: the domain-knowledge boundary. Emitted whenever any axis
    # is carried by it -- both arms, by the D-H1a-12 sec 5 table.
    if any(carrier_of(a, arm) == CARRIER_DOMAIN for a in AXES):
        out.append((CARRIER_DOMAIN, _rewrap(DOMAIN_BOUNDARY_TEXT)))

    # Sentence 3: scope disambiguation. Not a carrier (see SCOPE_CONSTRAINTS).
    out.append((SCOPE_DISAMBIGUATION_ID, _rewrap(SCOPE_DISAMBIGUATION_TEXT)))
    return out


def _rewrap(one_line_bullet: str) -> str:
    """Re-wrap a pre-written bullet to the template's 76-column style."""
    body = one_line_bullet[2:] if one_line_bullet.startswith("- ") else one_line_bullet
    return _bullet(body)


def render_policy_text(arm: str) -> str:
    return "\n\n".join(text for _, text in render_policy_block(arm))


# --------------------------------------------------------------------------
# The twelve structural assertions (D-H1a-11 sec 10), in the ruling's order
# --------------------------------------------------------------------------
def assert_0_table_keys_are_exactly_the_declared_axes() -> None:
    """Every assertion iterates AXES, so a table key OUTSIDE AxES is never
    visited by any of them. Independent review (2026-08-06, M7) added a
    `recency` entry forbidden by CARRIER_DOMAIN in both arms -- the substantive
    subsumption -- and all 167 tests passed because no assertion looks at keys
    it does not already expect. Pin the key set itself.
    """
    declared = set(AXES)
    actual = set(DECISION_BASIS_POLICY)
    extra = actual - declared
    missing = declared - actual
    if extra:
        raise PolicyContractError(
            f"[0] DECISION_BASIS_POLICY has keys outside AXES: {sorted(extra)}. "
            f"No other assertion visits them, so they are unchecked policy."
        )
    if missing:
        raise PolicyContractError(f"[0] AXES declared but absent from the table: {sorted(missing)}")


def assert_0b_subaxes_are_not_reparented_under_a_sibling_category() -> None:
    """D-H1a-12 sec 5's non-subsumption, ENFORCED rather than asserted.

    Independent review (2026-08-06, M1) declared `source_meta_reasoning` a
    subaxis of `outside_domain_knowledge` and nothing caught it -- the sibling
    claim lived only in a comment and a test name. The two categories must not
    contain each other in either direction, and no target axis may be declared
    a child of any non-target axis.
    """
    for parent, subs in SUBAXES.items():
        for sub in subs:
            if sub in TARGET_AXES and parent not in TARGET_AXES:
                raise PolicyContractError(
                    f"[0b] target axis {sub!r} is declared a subaxis of "
                    f"non-target {parent!r} -- that is the subsumption Q12=F removed"
                )
            if sub in AXES:
                raise PolicyContractError(
                    f"[0b] {sub!r} is both a top-level axis and a subaxis of "
                    f"{parent!r}; the containment structure is ambiguous"
                )
    # And the domain carrier must never govern the target axis or its subaxes.
    for axis in sorted(TARGET_AXES):
        for sub in (axis,) + tuple(SUBAXES.get(axis, ())):
            if sub in DECISION_BASIS_POLICY:
                for arm in ARMS:
                    if carrier_of(sub, arm) == CARRIER_DOMAIN:
                        raise PolicyContractError(
                            f"[0b] {arm}: {sub!r} is carried by {CARRIER_DOMAIN}; "
                            f"the domain ban would subsume the target mechanism"
                        )


def assert_0c_declared_states_match_the_ruling_table() -> None:
    """MAJOR (2026-08-06, M3/M3b): the state column was unpinned.

    assert_3 only inspects forbidding states and assert_4 only
    allowed_by_default, so downgrading a ruling-forbidden axis to `unspecified`
    in BOTH arms passed everything while the prose kept forbidding it -- table
    and prompt disagreeing, which is the Q10 defect in the opposite direction.
    """
    ruling = {
        "evidence_count": (EXPLICITLY_FORBIDDEN, EXPLICITLY_FORBIDDEN),
        "evidence_item_presentation_order": (EXPLICITLY_FORBIDDEN, EXPLICITLY_FORBIDDEN),
        "outside_domain_knowledge": (EXPLICITLY_FORBIDDEN, EXPLICITLY_FORBIDDEN),
        "external_source_retrieval": (EXPLICITLY_FORBIDDEN, EXPLICITLY_FORBIDDEN),
        "source_meta_reasoning": (EXPLICITLY_FORBIDDEN, ALLOWED_BY_DEFAULT),
    }
    for axis, (want_kept, want_removed) in ruling.items():
        got = (state_of(axis, ARMS[0]), state_of(axis, ARMS[1]))
        if got != (want_kept, want_removed):
            raise PolicyContractError(
                f"[0c] {axis!r}: ruling sec 5 states {(want_kept, want_removed)}, "
                f"table says {got}"
            )


def assert_1_every_axis_arm_has_a_state() -> None:
    for axis in AXES:
        for arm in ARMS:
            try:
                state = state_of(axis, arm)
            except KeyError as exc:
                raise PolicyContractError(
                    f"[1] {axis} x {arm}: no state declared ({exc})"
                ) from exc
            if state not in STATES:
                raise PolicyContractError(
                    f"[1] {axis} x {arm}: state {state!r} not in {STATES}"
                )


def assert_2_exactly_one_valid_carrier_per_axis_arm() -> None:
    for axis in AXES:
        for arm in ARMS:
            entry = DECISION_BASIS_POLICY[axis][_ARM_KEY[arm]]
            if "carrier" not in entry:
                raise PolicyContractError(f"[2] {axis} x {arm}: no carrier")
            carrier = entry["carrier"]
            if isinstance(carrier, (list, tuple, set)):
                raise PolicyContractError(
                    f"[2] {axis} x {arm}: carrier is a collection {carrier!r} -- "
                    f"exactly one carrier per axis x arm (ruling sec 8)"
                )
            if carrier not in CARRIERS:
                raise PolicyContractError(
                    f"[2] {axis} x {arm}: unknown carrier {carrier!r}"
                )


def assert_3_forbidden_states_use_forbidding_carriers() -> None:
    for axis in AXES:
        for arm in ARMS:
            state, carrier = state_of(axis, arm), carrier_of(axis, arm)
            if state in _FORBIDDING_STATES and state not in _CARRIER_SEMANTICS[carrier]:
                raise PolicyContractError(
                    f"[3] {axis} x {arm}: state {state!r} attributed to "
                    f"{carrier!r}, which cannot express a prohibition"
                )


def assert_4_default_permission_states_use_the_default_carrier() -> None:
    for axis in AXES:
        for arm in ARMS:
            if state_of(axis, arm) == ALLOWED_BY_DEFAULT and carrier_of(axis, arm) != CARRIER_DEFAULT:
                raise PolicyContractError(
                    f"[4] {axis} x {arm}: allowed_by_default must be carried by "
                    f"{CARRIER_DEFAULT}, got {carrier_of(axis, arm)!r}"
                )


def assert_5_no_duplicate_forbidding_carrier(
    rendered: dict[str, str] | None = None, q1_clause_text: str | None = None
) -> None:
    """No axis x arm is forbidden by more than one carrier.

    KNOWN LIMITATION, corrected 2026-08-04. The original version of this
    function never read `rendered` and both its branches were tautologically
    unreachable: `_q7_forbidden_axes` is DERIVED from `carrier_of(a, arm) ==
    CARRIER_Q7`, so `declared != CARRIER_Q7 and axis in _q7_forbidden_axes(arm)`
    reduces to `declared == Q7 and declared != Q7`, which is never true. An
    independent review (`docs/feedback/h1a_repair_review_20260804.md`) found
    this by constructing a poisoned `rendered` dict with a second forbidding
    bullet in KEPT and observing the function pass. Re-verified by the
    operating session before this fix, independently of the review's report.

    The real check: locate each axis's declared carrier's OWN text span in the
    rendered arm (the Q7 block's bytes, or Q1's clause bytes), remove exactly
    those known spans, and scan what remains for another mention that forbids
    the same axis. Structural, not lexical-complete -- it still uses
    `_PROHIBITION_VERBS`/`AXIS_SURFACE_TOKENS` to recognize a mention in the
    remainder, so it inherits their coverage limits (documented on
    `assert_6b`). What it newly guarantees is that a duplicate landing
    ANYWHERE outside the two known carrier regions is visible, rather than
    never being looked for at all.

    `rendered` and `q1_clause_text` are optional so the no-args structural
    suite (`assert_structural_no_args`) can still run before any prompt is
    rendered; the prose check is skipped in that case, matching the original
    function's most permissive behavior, but now for a real reason (nothing to
    scan) rather than a dead branch.
    """
    for axis in AXES:
        for arm in ARMS:
            if state_of(axis, arm) not in _FORBIDDING_STATES:
                continue
            declared = carrier_of(axis, arm)
            emitted = {cid for cid, _ in render_policy_block(arm)}
            if declared == CARRIER_Q7 and CARRIER_Q7 not in emitted:
                raise PolicyContractError(
                    f"[5] {axis} x {arm}: declared carrier is Q7 but no Q7 block "
                    f"was emitted"
                )

    if rendered is None:
        return

    for arm in ARMS:
        if arm not in rendered:
            raise PolicyContractError(f"[5] rendered text missing for arm {arm!r}")
        text = rendered[arm]

        # Strip the known carrier spans AND the scope constraint, normalized
        # first because the template hard-wraps at 76 columns and none of
        # these spans can be matched as an exact multi-line substring
        # otherwise (the same reason `_normalize_ws` exists at all). What
        # remains is text no declared carrier -- and no scope constraint --
        # accounts for; any forbidding mention found there is, by
        # construction, a SECOND carrier.
        remainder = _normalize_ws(text)
        q7_text = dict(render_policy_block(arm)).get(CARRIER_Q7)
        if q7_text:
            remainder = remainder.replace(_normalize_ws(q7_text), " ", 1)
        if arm == "PROHIBITION_KEPT" and q1_clause_text:
            remainder = remainder.replace(_normalize_ws(q1_clause_text), " ", 1)
        remainder = remainder.replace(_normalize_ws(SCOPE_CONSTRAINT_TEXT), " ", 1)
        # D-H1a-12 sec 4 added two more arm-invariant spans. They must be
        # stripped for the same reason the scope constraint is: they are
        # known, declared, byte-identical-across-arms text, so their tokens
        # are NOT evidence of a duplicate forbidding carrier. Failing to
        # register a new carrier's span here is what this guard caught on
        # the first implementation attempt -- keep them in lockstep.
        for known in (DOMAIN_BOUNDARY_TEXT, SCOPE_DISAMBIGUATION_TEXT):
            remainder = remainder.replace(_normalize_ws(known), " ", 1)

        for axis in AXES:
            if state_of(axis, arm) not in _FORBIDDING_STATES:
                continue
            declared = carrier_of(axis, arm)
            for token in AXIS_SURFACE_TOKENS[axis]:
                tok = _normalize_ws(token)
                if tok not in remainder:
                    continue
                for verb in _PROHIBITION_VERBS:
                    v = _normalize_ws(verb)
                    if v not in remainder:
                        continue
                    for vi in _all_indices(remainder, v):
                        for ti in _all_indices(remainder, tok):
                            if abs(ti - vi) <= 240:
                                raise PolicyContractError(
                                    f"[5] {axis} x {arm}: declared carrier is "
                                    f"{declared!r}, but text outside that "
                                    f"carrier's own span also forbids it "
                                    f"({verb!r} near {token!r}) -- duplicate "
                                    f"carrier, the Q10 defect"
                                )


def assert_6_removed_target_axes_have_no_forbidding_carrier() -> None:
    for axis in sorted(TARGET_AXES):
        state = state_of(axis, "PROHIBITION_REMOVED")
        if state in _FORBIDDING_STATES:
            raise PolicyContractError(
                f"[6] {axis} x REMOVED: state {state!r} -- the repaired REMOVED "
                f"arm must not forbid any target axis"
            )


_PROHIBITION_VERBS = (
    "do not break ties using",
    "do not use",
    "must not use",
    "may not use",
    "재판정하지 않는다",
    "추론하지 마라",
)


def assert_6b_removed_prose_has_no_target_prohibition(rendered: dict[str, str]) -> None:
    """Prose-level companion to assertion 6.

    Assertion 6 reads the declared table; this reads the assembled prompt. Both
    are needed, and this one is what actually catches the cohort that ran: its
    REMOVED prompt named all four target axes inside "Do not break ties
    using ...", while the table would have said allowed_by_default.

    This is the check the old byte-absence guard did not make. It asks whether
    a target axis is forbidden ANYWHERE in the arm, so a paraphrased or
    relocated prohibition does not escape by not matching a known sentence.
    """
    removed = _normalize_ws(rendered["PROHIBITION_REMOVED"])
    for axis in sorted(TARGET_AXES):
        if effective_state(axis, "PROHIBITION_REMOVED") in _FORBIDDING_STATES:
            continue  # assertion 6 already rejects this; nothing to cross-check
        for token in AXIS_SURFACE_TOKENS[axis]:
            tok = _normalize_ws(token)
            if tok not in removed:
                continue
            for verb in _PROHIBITION_VERBS:
                v = _normalize_ws(verb)
                if v not in removed:
                    continue
                # Same sentence-ish window: the verb and the axis token within
                # 240 normalized characters of each other. Windowed rather than
                # whole-document so an unrelated prohibition elsewhere in the
                # prompt does not produce a false positive.
                for vi in _all_indices(removed, v):
                    for ti in _all_indices(removed, tok):
                        if abs(ti - vi) <= 240:
                            raise PolicyContractError(
                                f"residual prohibition: REMOVED forbids target "
                                f"axis {axis!r} -- {verb!r} co-occurs with "
                                f"{token!r} while the policy declares it "
                                f"{effective_state(axis, 'PROHIBITION_REMOVED')!r}"
                            )


def _all_indices(haystack: str, needle: str) -> list[int]:
    out, i = [], haystack.find(needle)
    while i != -1:
        out.append(i)
        i = haystack.find(needle, i + 1)
    return out


def assert_7_kept_target_axes_are_carried_only_by_q1() -> None:
    for axis in sorted(TARGET_AXES):
        carrier = carrier_of(axis, "PROHIBITION_KEPT")
        if carrier != CARRIER_Q1:
            raise PolicyContractError(
                f"[7] {axis} x KEPT: carrier {carrier!r}, must be {CARRIER_Q1} "
                f"only (Q11.1=A forbids restoring target axes to Q7)"
            )


def assert_8_nontarget_axes_identical_in_state_and_carrier() -> None:
    for axis in sorted(NONTARGET_AXES):
        k = DECISION_BASIS_POLICY[axis]["kept"]
        r = DECISION_BASIS_POLICY[axis]["removed"]
        if k["state"] != r["state"] or k["carrier"] != r["carrier"]:
            raise PolicyContractError(
                f"[8] non-target axis {axis!r} differs across arms: "
                f"kept={k}, removed={r}"
            )


def assert_9_default_permission_is_byte_identical_across_arms() -> None:
    """D-H1a-12 sec 9: verified against an INDEPENDENT golden contract.

    The previous form compared `render_policy_block`'s output to
    GLOBAL_DEFAULT_PERMISSION_TEXT -- the very constant the renderer emits.
    Producer and expectation shared one source, so all three raise paths were
    unreachable by construction and no negative test could exist without
    mocking the renderer (which would prove the mock). It sat in
    `test_guard_negative_coverage.py`'s KNOWN_UNPROVEN for that reason.

    Now the expectation lives in `h1a_common_policy_block_v2.json` (frozen
    text + sha256), which the renderer does not read. A drift in the renderer,
    in the constant, or in BOTH TOGETHER now fails -- the last case being the
    one the ruling singled out (sec 9: "양 arm 이 서로 같더라도 golden digest
    와 다르면 실패해야 한다").
    """
    golden = _load_golden_common_block()

    per_arm = {}
    for arm in ARMS:
        blocks = render_policy_block(arm)
        ids = [cid for cid, _ in blocks]
        for carrier in golden["carriers_included"]:
            count = ids.count(carrier)
            if count != 1:
                raise PolicyContractError(
                    f"[9] {arm}: expected exactly 1 {carrier} block, got {count}"
                )
        by_id = dict(blocks)
        per_arm[arm] = "\n\n".join(
            by_id[c] for c in golden["carriers_included"]
        )

    a, b = (per_arm[arm] for arm in ARMS)
    if a != b:
        raise PolicyContractError(
            "[9] the common policy block is not byte-identical across arms"
        )

    actual = hashlib.sha256(a.encode("utf-8")).hexdigest()
    if actual != golden["sha256"]:
        raise PolicyContractError(
            f"[9] the rendered common block drifted from the frozen golden "
            f"contract. expected sha256 {golden['sha256']}, got {actual}. "
            f"If this change is intended it is an experiment amendment: "
            f"re-freeze {GOLDEN_COMMON_BLOCK_PATH.name} in its own commit and "
            f"say why."
        )


GOLDEN_COMMON_BLOCK_PATH = pathlib.Path(__file__).resolve().parent / \
    "h1a_common_policy_block_v2.json"


def _load_golden_common_block() -> dict:
    try:
        data = json.loads(GOLDEN_COMMON_BLOCK_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PolicyContractError(
            f"[9] the golden common-block contract is missing "
            f"({GOLDEN_COMMON_BLOCK_PATH.name}). Assertion 9 cannot certify "
            f"anything without it -- do not proceed."
        ) from exc
    for key in ("sha256", "text", "carriers_included"):
        if key not in data:
            raise PolicyContractError(f"[9] golden contract lacks {key!r}")
    restated = hashlib.sha256(data["text"].encode("utf-8")).hexdigest()
    if restated != data["sha256"]:
        raise PolicyContractError(
            "[9] the golden contract is internally inconsistent: its own "
            "`text` does not hash to its own `sha256`"
        )
    return data


def assert_10_q1_clause_is_kept_only_and_unchanged(
    rendered: dict[str, str], q1_clause_text: str
) -> None:
    kept, removed = rendered["PROHIBITION_KEPT"], rendered["PROHIBITION_REMOVED"]
    if q1_clause_text not in kept:
        raise PolicyContractError("[10] Q1 clause absent from KEPT")
    if q1_clause_text in removed:
        raise PolicyContractError("[10] Q1 clause present in REMOVED")


def assert_11_removed_has_no_axis_specific_permission_text(
    rendered: dict[str, str]
) -> None:
    """Q11=D forbids axis-enumerating permission text in REMOVED.

    The generated block cannot produce one (the renderer has no such branch),
    so this checks the assembled prompt for a permission verb co-occurring with
    a target axis outside the shared default rule.
    """
    removed = _normalize_ws(rendered["PROHIBITION_REMOVED"])
    default = _normalize_ws(GLOBAL_DEFAULT_PERMISSION_TEXT)
    remainder = removed.replace(default, " ")
    permission_verbs = ("you may", "may take", "may consider", "is permitted", "are permitted")
    for axis in sorted(TARGET_AXES):
        for token in AXIS_SURFACE_TOKENS[axis]:
            tok = _normalize_ws(token)
            if tok not in remainder:
                continue
            for verb in permission_verbs:
                if verb in remainder:
                    raise PolicyContractError(
                        f"[11] REMOVED names target axis {axis!r} ({token!r}) "
                        f"alongside permission verb {verb!r} outside the shared "
                        f"default rule -- Q11=D forbids axis-specific permission text"
                    )


def assert_12_common_q7_generates_only_nontarget_forbidden_states() -> None:
    """D-H1a-12 sec 8: SEMANTIC check, not a lexical alias scan.

    The old form scanned the rendered tie-breaker sentence for target-axis
    tokens. The ruling demoted that: a token list cannot certify semantic
    absence, and this experiment already lost a cohort to a guard whose
    passing meant less than it looked (the Q10 defect). Worse, the token list
    was *incidentally* incomplete -- it declared the Korean alias `우선순위`
    but not the English `priority`, and the ruling's own sec 5 prescription
    contained the bare word `priority`. Passing was an accident of that gap.

    What is certified now: the set of axes the COMMON tie-breaker carrier
    forbids is exactly the declared non-target set. This is checked against
    the policy object, which the prose is generated FROM, so it cannot be
    satisfied by rewording. Lexical scanning survives as `lint_common_q7`
    below -- reportable, never certifying (ruling sec 8: `role: lint_only`).
    """
    for arm in ARMS:
        carried = {
            a for a in AXES
            if carrier_of(a, arm) == CARRIER_Q7
            and state_of(a, arm) in _FORBIDDING_STATES
        }
        offending = carried & TARGET_AXES
        if offending:
            raise PolicyContractError(
                f"[12] {arm}: the common tie-breaker carrier ({CARRIER_Q7}) "
                f"forbids target axis/axes {sorted(offending)}. A target axis "
                f"must be governed by {CARRIER_Q1} in KEPT only -- otherwise "
                f"both arms forbid it and the contrast is destroyed."
            )
        # Subaxes are governed through their parent; none may be carried
        # directly by the common sentence either.
        for parent, subs in SUBAXES.items():
            if parent in TARGET_AXES:
                for sub in subs:
                    if sub in DECISION_BASIS_POLICY and \
                       carrier_of(sub, arm) != CARRIER_Q1 and \
                       state_of(sub, arm) in _FORBIDDING_STATES:
                        # Was `== CARRIER_Q7` only; independent review (M7)
                        # forbade a subaxis via CARRIER_DOMAIN undetected.
                        raise PolicyContractError(
                            f"[12] {arm}: subaxis {sub!r} of target axis "
                            f"{parent!r} is forbidden by "
                            f"{carrier_of(sub, arm)}, not {CARRIER_Q1}"
                        )


def lint_common_q7(arm: str) -> list[str]:
    """Lexical alias scan, DEMOTED to lint by D-H1a-12 sec 8.

    Returns findings instead of raising. A finding is a signal to read the
    sentence, not a certification failure -- the certifying check is
    `assert_12_common_q7_generates_only_nontarget_forbidden_states`. Keeping it
    as lint (rather than deleting it) preserves the recall it does have while
    removing its false authority.
    """
    try:
        q7 = [txt for cid, txt in render_policy_block(arm) if cid == CARRIER_Q7]
    except PolicyContractError as exc:
        # Lint never raises -- that is what makes it lint. A render failure is
        # itself a finding worth reporting, not a reason to abort the caller.
        return [f"{arm}: could not render for lint ({exc})"]
    haystack = _normalize_ws(" ".join(q7))
    findings = []
    for axis in sorted(TARGET_AXES):
        for token in AXIS_SURFACE_TOKENS.get(axis, ()):
            if _normalize_ws(token) in haystack:
                findings.append(
                    f"{arm}: tie-breaker sentence contains target-axis token "
                    f"{token!r} (axis {axis!r})"
                )
    return findings


STRUCTURAL_ASSERTIONS_NO_ARGS = (
    assert_0_table_keys_are_exactly_the_declared_axes,
    assert_0b_subaxes_are_not_reparented_under_a_sibling_category,
    assert_0c_declared_states_match_the_ruling_table,
    assert_1_every_axis_arm_has_a_state,
    assert_2_exactly_one_valid_carrier_per_axis_arm,
    assert_3_forbidden_states_use_forbidding_carriers,
    assert_4_default_permission_states_use_the_default_carrier,
    assert_5_no_duplicate_forbidding_carrier,
    assert_6_removed_target_axes_have_no_forbidding_carrier,
    assert_7_kept_target_axes_are_carried_only_by_q1,
    assert_8_nontarget_axes_identical_in_state_and_carrier,
    assert_9_default_permission_is_byte_identical_across_arms,
    assert_12_common_q7_generates_only_nontarget_forbidden_states,
)


def assert_structural_no_args() -> None:
    for fn in STRUCTURAL_ASSERTIONS_NO_ARGS:
        fn()


# --------------------------------------------------------------------------
# Effective-state resolution and the deductive check
# --------------------------------------------------------------------------
def effective_state(axis: str, arm: str) -> str:
    """effective(a) = explicit override if present, else the default.

    D-H1a-11 sec 6's formula. Written as a resolution rather than a lookup so
    the default-permission mechanism is visible in code, not just in prose.
    """
    declared = DECISION_BASIS_POLICY[axis][_ARM_KEY[arm]]
    if declared["carrier"] == CARRIER_DEFAULT:
        return POLICY_DEFAULTS["packet_internal_decision_basis"]["state"]
    return declared["state"]


def target_mechanism_allowed(arm: str) -> bool:
    """M_allowed: no target axis is forbidden in this arm."""
    return not any(
        effective_state(a, arm) in _FORBIDDING_STATES for a in TARGET_AXES
    )


# --------------------------------------------------------------------------
# D-H1a-12 sec 10 -- licensed_source_evaluation_path(arm)
# --------------------------------------------------------------------------
# Replaces `target_mechanism_contrast`, which checked only the target axis's
# state and therefore did not guarantee the needed proposition. The ruling's
# five conjuncts:
#   L(a) = V and S(a) and not D_S and not H and not R(a)
# V   : model-visible evidence source attributes exist
# S(a): source_meta_reasoning is allowed in this arm
# D_S : the domain-knowledge ban subsumes source-meta reasoning
# H   : a common rule maps the fixture's conflict shape directly to defer
# R(a): any other carrier prohibits source_meta_reasoning in this arm

# V and H are properties of the fixture and the shared prompt, not of this
# policy table, so they cannot be derived here. They are injected by the
# caller and default to the values the ruling's post-repair table asserts --
# but `assert_licensed_path_contrast` requires the caller to pass them
# explicitly, so a stale default can never silently certify a freeze.
# NO module-level defaults. Independent review (2026-08-06) noted that keeping
# them let a one-argument call certify both fixture facts silently. Callers must
# state them; there is nowhere for a stale value to hide.


def _domain_ban_subsumes_source_meta() -> bool:
    """D_S: is source_meta_reasoning captured by the domain-knowledge ban?

    Under Q12=F they are sibling categories and neither subsumes the other, so
    this must be False. It is computed, not assumed: if some future edit points
    source_meta_reasoning's carrier at the domain boundary, the subsumption is
    back and this returns True.
    """
    if "source_meta_reasoning" not in DECISION_BASIS_POLICY:
        return True  # the axis is gone; treat as captured -- fail closed
    return any(
        carrier_of("source_meta_reasoning", arm) == CARRIER_DOMAIN
        for arm in ARMS
    )


def _residual_prohibition(arm: str) -> bool:
    """R(a): a carrier OTHER than Q1 forbids source_meta_reasoning in `arm`."""
    if state_of("source_meta_reasoning", arm) not in _FORBIDDING_STATES:
        return False
    return carrier_of("source_meta_reasoning", arm) != CARRIER_Q1


def licensed_source_evaluation_path(
    arm: str,
    source_attributes_visible: bool,
    hard_defer_mapping: bool,
) -> dict:
    """Return each conjunct plus the conjunction (D-H1a-12 sec 10).

    Returns the parts, not just the boolean: a bare False would not say WHICH
    condition failed, and this experiment has already been set back twice by
    checks whose passing/failing carried less information than it appeared to.
    """
    v = bool(source_attributes_visible)
    s = state_of("source_meta_reasoning", arm) in _PERMITTING_STATES
    d_s = _domain_ban_subsumes_source_meta()
    h = bool(hard_defer_mapping)
    r = _residual_prohibition(arm)
    return {
        "arm": arm,
        "source_attributes_visible": v,
        "source_meta_allowed": s,
        "domain_ban_subsumes_source_meta": d_s,
        "hard_defer_mapping": h,
        "residual_prohibition": r,
        "licensed_path": v and s and (not d_s) and (not h) and (not r),
    }


def assert_licensed_path_contrast(
    source_attributes_visible: bool,
    hard_defer_mapping: bool,
) -> dict:
    """D-H1a-12 sec 10 freeze condition, as a conjunction over both arms.

        licensed_source_evaluation_path(KEPT)    == False
        licensed_source_evaluation_path(REMOVED) == True

    Both fixture-level facts must be passed in explicitly -- see the note on
    the module defaults. Returns the two rows so a caller can log them.
    """
    rows = {
        arm: licensed_source_evaluation_path(
            arm, source_attributes_visible, hard_defer_mapping
        )
        for arm in ARMS
    }
    expected = {"PROHIBITION_KEPT": False, "PROHIBITION_REMOVED": True}
    for arm, want in expected.items():
        got = rows[arm]["licensed_path"]
        if got != want:
            raise PolicyContractError(
                f"[licensed_path] {arm}: expected {want}, got {got}. "
                f"Conjuncts: {rows[arm]}"
            )
    return rows


def truth_table() -> list[dict]:
    """All four (Q1 override present, Q7 forbids target) cells."""
    return [
        {"q1_forbids": q1, "q7_forbids": q7, "m_allowed": (not q1) and (not q7)}
        for q1 in (True, False)
        for q7 in (True, False)
    ]


def deductive_check() -> dict:
    kept = target_mechanism_allowed("PROHIBITION_KEPT")
    removed = target_mechanism_allowed("PROHIBITION_REMOVED")
    result = {
        "kept_target_forbidden": kept is False,
        "removed_target_allowed": removed is True,
        "target_mechanism_contrast": kept != removed,
        "nontarget_constraints_equal": all(
            DECISION_BASIS_POLICY[a]["kept"] == DECISION_BASIS_POLICY[a]["removed"]
            for a in NONTARGET_AXES
        ),
        "removed_target_state_is_allowed_by_default": all(
            state_of(a, "PROHIBITION_REMOVED") == ALLOWED_BY_DEFAULT
            for a in TARGET_AXES
        ),
        "removed_target_state_is_not_unspecified": all(
            state_of(a, "PROHIBITION_REMOVED") != UNSPECIFIED for a in TARGET_AXES
        ),
        "truth_table": truth_table(),
    }
    result["proof_repair_creates_contrast"] = all(
        v for k, v in result.items() if isinstance(v, bool)
    )
    return result


def assert_deductive_check() -> dict:
    r = deductive_check()
    if not r["proof_repair_creates_contrast"]:
        failed = [
            k for k, v in r.items()
            if isinstance(v, bool) and not v and k != "proof_repair_creates_contrast"
        ]
        raise PolicyContractError(f"deductive policy check failed: {failed}")
    return r


# --------------------------------------------------------------------------
# Freeze gate (D-H1a-11 sec 13 `freeze_gate`)
# --------------------------------------------------------------------------
# The ruling lists five unblock conditions. Four are machine-checkable. The
# fifth -- "independent semantic review passed" -- is not, and per this
# project's `pass-is-a-conjunction` lesson an unverifiable condition must be
# named and assigned rather than silently assumed. It stays False until a human
# records the review outcome, so `assert_freezable` cannot pass on code alone.
#
# 2026-08-17: SET TO TRUE. What this records, precisely:
#
#   - The review ran under the encoded protocol (`_h1a_review_protocol.py`),
#     which scores reviewer capability BEFORE counting any opinion. Five
#     reviewers declared scopes, took blinded packets mixing mutated and clean
#     material, and all five qualified: six mutations detected, zero misses,
#     zero false positives.
#   - All five then approved on the real artifact. No blocker, no major.
#     Report: `docs/feedback/h1a_independent_semantic_review_20260816.md`.
#   - The reviewers found a canonical AUTOMATION coverage gap, not a semantic
#     error. D-H1a-17 reclassified that gap as non-blocking audit work after a
#     counterfactual analysis, narrowing D-H1a-16's
#     `TargetCritical => CanonicalExpectedState` to
#     `CanonicalAuditCritical => CanonicalExpectedState`.
#   - The ruling permitted this flag only "assuming no other BLOCKER/MAJOR".
#     That premise is machine-checkable and was checked, not assumed:
#     `assert_freezable` blocked on condition 5 alone, and with the flag
#     patched in memory every other condition passed
#     (`test_h1a_criticality.py::test_no_freeze_condition_other_than_the_
#     review_flag_is_unmet` pins it).
#
# What this does NOT record: that the canonical model now covers every
# target-critical family. It does not (D-H1a-17 sec 5 / PREREGISTRATION
# sec 5h). Three families are certified by routes other than the canonical
# expected graph, each named in `_h1a_semantic_compiler.CERTIFICATION_PATH`,
# and the counterfactual for each is measured rather than asserted.
INDEPENDENT_SEMANTIC_REVIEW_PASSED = True


def assert_freezable(
    rendered: dict[str, str],
    q1_clause_text: str,
    *,
    source_attributes_visible: bool,
    hard_defer_mapping: bool,
) -> dict:
    """D-H1a-11's five conditions PLUS D-H1a-12 sec 10's licensed-path contrast.

    BLOCKER fixed 2026-08-06 (independent review): this function did not call
    `assert_licensed_path_contrast`, so sec 10's replacement predicate ran only
    in tests while the production path (`_h1a_cohort.build_cohort`) certified
    freezes using `deductive_check`'s `target_mechanism_contrast` -- the very
    predicate sec 10 line 466 says does not guarantee the needed proposition.
    That is the "policy layer is not on the execution path" defect, reproduced
    one layer up from where it was first found.

    V and H are KEYWORD-ONLY and have NO defaults on purpose. They are fixture
    and shared-prompt facts that this module cannot derive, and a positional
    call with stale module defaults is exactly how an unverified fixture fact
    would silently certify a freeze.
    """
    assert_structural_no_args()
    assert_5_no_duplicate_forbidding_carrier(rendered, q1_clause_text)
    assert_6b_removed_prose_has_no_target_prohibition(rendered)
    assert_10_q1_clause_is_kept_only_and_unchanged(rendered, q1_clause_text)
    assert_11_removed_has_no_axis_specific_permission_text(rendered)
    licensed = assert_licensed_path_contrast(
        source_attributes_visible, hard_defer_mapping
    )
    proof = assert_deductive_check()
    proof["licensed_source_evaluation_path"] = licensed
    if not INDEPENDENT_SEMANTIC_REVIEW_PASSED:
        raise FreezeGateBlocked(
            "freeze condition 5 unmet: independent semantic review has not been "
            "recorded as passed. D-H1a-11 lists it alongside the four "
            "machine-checkable conditions, and it cannot be verified from code. "
            "Run the review (separate agent, maker's conclusions withheld), then "
            "set INDEPENDENT_SEMANTIC_REVIEW_PASSED = True in the same commit "
            "that records its report."
        )
    return proof
