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
    "source_order",
    "outside_domain_knowledge",
    "external_source_retrieval",
    "source_meta_reasoning",
)

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

# D-H1a-12 sec 4, third sentence. NOT a carrier: it flips no axis to
# forbidden. It exists to stop the domain-knowledge boundary from being read
# as also governing source evaluation -- which is precisely the subsumption
# that made the previous cohort nonidentifying. Byte-identical in both arms.
SCOPE_DISAMBIGUATION_ID = "SCOPE_DISAMBIGUATION"
SCOPE_DISAMBIGUATION_TEXT = (
    "- The restriction on outside domain or ontology knowledge does not "
    "itself govern evaluation of the supplied evidence items as sources. "
    "Source evaluation is governed by the arm-specific source-evaluation "
    "clause."
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
GLOBAL_DEFAULT_PERMISSION_TEXT = (
    "Within the supplied packet, a decision basis may be considered unless this\n"
    "prompt explicitly prohibits it. Permission to consider a basis does not by\n"
    "itself warrant selecting a type or favor either allowed type."
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
    "source_order": {
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
    "source_order": ("source order",),
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
    "source_order": "source order",
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
                f"Do not break ties using {phrase} unless the packet "
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
    texts = {}
    for arm in ARMS:
        found = [t for cid, t in render_policy_block(arm) if cid == CARRIER_DEFAULT]
        if len(found) != 1:
            raise PolicyContractError(
                f"[9] {arm}: expected exactly 1 default-permission block, got {len(found)}"
            )
        texts[arm] = found[0]
    if texts[ARMS[0]] != texts[ARMS[1]]:
        raise PolicyContractError(
            "[9] the default-permission text is not byte-identical across arms"
        )
    if texts[ARMS[0]] != GLOBAL_DEFAULT_PERMISSION_TEXT:
        raise PolicyContractError(
            "[9] the emitted default-permission text drifted from the ruling's bytes"
        )


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


def assert_12_common_q7_excludes_target_axis_strings_and_aliases() -> None:
    """No target axis, nor a declared alias of one, appears in the common Q7 list.

    KNOWN LIMITATION, stated because the ruling's wording ("의미상 별칭") asks
    for semantic completeness that a declared alias list cannot certify. This
    check is a cross-check, not the guarantee. The guarantee is that the Q7
    block is GENERATED from the policy table, so a target axis can only appear
    there if the table says it is Q7-carried -- which assertion 7 forbids.
    """
    for arm in ARMS:
        q7 = [t for cid, t in render_policy_block(arm) if cid == CARRIER_Q7]
        haystack = _normalize_ws(" ".join(q7))
        for axis in sorted(TARGET_AXES):
            for token in AXIS_SURFACE_TOKENS[axis]:
                if _normalize_ws(token) in haystack:
                    raise PolicyContractError(
                        f"[12] {arm}: common Q7 list names target axis {axis!r} "
                        f"via {token!r}"
                    )


STRUCTURAL_ASSERTIONS_NO_ARGS = (
    assert_1_every_axis_arm_has_a_state,
    assert_2_exactly_one_valid_carrier_per_axis_arm,
    assert_3_forbidden_states_use_forbidding_carriers,
    assert_4_default_permission_states_use_the_default_carrier,
    assert_5_no_duplicate_forbidding_carrier,
    assert_6_removed_target_axes_have_no_forbidding_carrier,
    assert_7_kept_target_axes_are_carried_only_by_q1,
    assert_8_nontarget_axes_identical_in_state_and_carrier,
    assert_9_default_permission_is_byte_identical_across_arms,
    assert_12_common_q7_excludes_target_axis_strings_and_aliases,
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
INDEPENDENT_SEMANTIC_REVIEW_PASSED = False


def assert_freezable(rendered: dict[str, str], q1_clause_text: str) -> dict:
    """All five D-H1a-11 freeze conditions, as a conjunction."""
    assert_structural_no_args()
    assert_5_no_duplicate_forbidding_carrier(rendered, q1_clause_text)
    assert_6b_removed_prose_has_no_target_prohibition(rendered)
    assert_10_q1_clause_is_kept_only_and_unchanged(rendered, q1_clause_text)
    assert_11_removed_has_no_axis_specific_permission_text(rendered)
    proof = assert_deductive_check()
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
