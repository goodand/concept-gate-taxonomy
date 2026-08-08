"""H1a arm-prompt construction -- H1a-native template per Q3=B, Q5=B.

Three external rulings shaped this module, in sequence:

1. `DESIGN_DECISION_H1a_manipulation_scope.md` (Q1=B, 2026-07-30): the
   manipulation is "delete every model-facing clause that prohibits
   liveness/source-priority/recency/authority/supersession adjudication,
   while preserving every other packet-boundary constraint." A full-text scan
   of E2.4's contract_prompt.md fenced block found exactly two such clauses,
   block-relative "L8" (preamble) and "L24-25" (rule 1, third bullet).

2. `DESIGN_DECISION_H1a_prompt_surface.md` (Q3=B, 2026-07-31): reusing E2.4's
   contract_prompt.md rules 1-7 wholesale (this module's first version) turned
   out to be unusable -- rule 3 step 4 maps H1a's exact fixture shape (an
   explicit doc/code tie at equal claim strength) to a hard `selected_type =
   null`, independent of the liveness manipulation. That would put a
   prompt-authored ceiling under both arms that Q2's anchor-flip diagnostic
   cannot detect (it only compares anchor levels within an arm). The ruling
   replaced E2.4's rules 2-7 and preamble with an H1a-native task instruction
   built for `h1a_observation_v1`, and kept only rule 1's packet-boundary
   substance -- expressed in the ruling's own English wording, not E2.4's
   Korean rule 1 text.

3. `DESIGN_DECISION_H1a_review_blockers.md` (Q5=B, 2026-08-01): a second
   independent review found that the manipulated clause's third sentence,
   "그 판정은 이미 끝났고 너의 범위가 아니다" ("that adjudication is already
   finished and is not in your scope"), had lost its antecedent when Q3
   dropped the E2.4 preamble it used to point at -- leaving the payload's
   recorded type as the only thing in the prompt readable as "an already
   finished adjudication," which uniquely authorized the anchor for
   PROHIBITION_KEPT. Q5's repair is to drop that third sentence rather than
   restore the antecedent (Q5.1 forbids restoring it: it would reintroduce a
   provenance/eligibility assertion H1a does not need, and Q6 removes the
   anchor it would otherwise protect anyway). The manipulated clause is now
   exactly two sentences.

What this module does
----------------------
The H1a-native template now lives in `h1a_prompt_template.md` (a sibling file
in this experiment folder), not in the Q3 ruling file -- Q5's own sentence
edit, plus Q6.1's concept/feature block and Q7's warrant rule, all modify the
template body, and a ruling file must stay a preserved-verbatim record. See
`h1a_prompt_template.md`'s own header table for which ruling contributed which
section.
Q1's frozen liveness clauses (reduced to two sentences by Q5=B; Q3 did not
reopen Q1's wording otherwise) are inserted into that template for
PROHIBITION_KEPT only, immediately after the template's own "external
sources." sentence, which is the one remaining packet-boundary locus once
E2.4's rule 1 and preamble were dropped. This positions them at the ruling's
"frozen locations" as literally as a template with only one packet-boundary
paragraph allows.

Construction judgment call, flagged for independent review
------------------------------------------------------------
The ruling's template is authored in English; Q1's frozen clauses are
Korean. Two options existed: translate the clauses to fit the English prose,
or insert the original Korean bytes as-is. This module does the latter --
translation is itself an unreviewed authorial act (translation nuance can
change how strongly a clause reads), whereas inserting the Q1-approved bytes
verbatim carries no new judgment beyond where to place them. The result is a
mixed-language paragraph for PROHIBITION_KEPT. This choice, and no other part
of the construction, is the one this module's docstring most wants an
independent reviewer to check.
"""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DESIGN_DECISION_PATH = HERE / "h1a_prompt_template.md"

ARMS = ("PROHIBITION_KEPT", "PROHIBITION_REMOVED")

# Q1's frozen clauses, reduced to two sentences by Q5=B (the third sentence,
# "그 판정은 이미 끝났고 너의 범위가 아니다", is dropped -- it lost its
# antecedent when Q3 removed the E2.4 preamble it used to refer to, and Q5.1
# forbids restoring that antecedent). Kept as the raw, as-approved bytes --
# see LIVENESS_CLAUSE_TEXT below for the whitespace-normalized form actually
# inserted into the template.
LIVENESS_PRIORITY_CLAUSES = {
    "L8": " 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.",
    "L24_25": (
        "   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를\n"
        "     추론하지 마라.\n"
    ),
}

# Secondary tripwire (manipulation-scope requirement 8: "keyword scanning may
# be a secondary tripwire, not the sole proof of absence"). The primary proof
# is LIVENESS_PRIORITY_CLAUSES absence, checked structurally above.
#
# Korean surface -- the language Q1's frozen clauses are written in. The two
# phrases naming the dropped third sentence ("판정은 이미 끝났", "너의 범위가
# 아니다") are removed here too -- Q5=B took them out of the manipulation
# itself, so they are no longer part of what this guard exists to detect.
#
# "출처의 liveness" (phrase), not bare "liveness" -- Q7's warrant rule
# legitimately uses the bare English word "liveness" in the tie-breaker
# prohibition list ("...recency, authority, liveness, or outside knowledge
# ..."), in BOTH arms. A bare-word tripwire would fire on the clean template,
# i.e. zero precision, the same trap "outside" was already documented as.
RESIDUAL_TRIPWIRES_KO = (
    "출처의 liveness", "우선순위를 재판정", "더 최신인지", "더 권위 있는지",
    "아직 살아있는", "추론하지 마라",
)

# English surface. ADDED 2026-08-01 after an independent review demonstrated
# by injection that the guard passed this sentence clean:
#
#   "Do not judge which source is more authoritative, newer, or still live;
#    that judgment is already done and is outside your scope."
#
# The gap was live, not hypothetical. Q3=B made the template English, and the
# template is loaded from a hand-editable markdown ruling file -- so a
# prohibition added there would land in BOTH arms, which the arm-diff test
# cannot see (it only proves KEPT == REMOVED + clause), leaving this guard as
# the only device that could catch it. Implements manipulation-scope
# requirement 7, whose seven English propositions had been binding since
# 2026-07-30 and were never wired up.
#
# Phrases, not bare words, wherever a bare word could occur innocently:
# "outside" appears legitimately in the template ("fields outside
# h1a_observation_v1"), so only scoping phrases are matched. Matching is
# case-insensitive. "liveness" is likewise no longer a bare word after Q7 --
# the warrant rule's own tie-breaker prohibition list legitimately says
# "...recency, authority, liveness, or outside knowledge..." in BOTH arms, so
# "liveness of" is used instead (matches the ruling's actual proposition,
# "the liveness of any source", without matching Q7's legitimate mention).
# test_h1a_contract.py pins BOTH directions -- each of the ruling's seven
# propositions is caught (recall), and the clean template passes (precision).
RESIDUAL_TRIPWIRES_EN = (
    "liveness of",
    "source priority",
    "authoritative",
    "which source is newer",
    "more recent",
    "still live",
    "live code",
    "already done",
    "already finished",
    "already settled",
    "outside your scope",
    "outside the model's scope",
    "not your scope",
    "not within your scope",
    # ADDED 2026-08-02 -- independent review demonstrated three further
    # paraphrases of the same prohibition slip past the list above
    # undetected (none of them repeat the seven propositions' wording):
    #   "do not second-guess which document is fresher or carries more weight"
    #   "do not treat the code as having superseded the documentation"
    #   "that determination has already been made for you and is not
    #    something you need to figure out"
    "second-guess", "carries more weight", "fresher",
    "superseded the documentation",
    "already been made for you", "not something you need to figure out",
)

# KNOWN LIMITATION, not fixed by the addition above: this list is a closed
# enumeration of phrasings, not a semantic check, so it structurally can only
# catch paraphrases someone has already thought of. Every addition to this
# tuple has been reactive -- one injection caught, phrases added, guard
# closed for that wording only. Treat "the guard passes" as "no known
# paraphrase was tried," never as "no prohibition is present." A hand-edit to
# `h1a_prompt_template.md` reintroducing this prohibition in genuinely novel
# wording would still land in both arms undetected by this guard AND by the
# arm-diff test (which only proves KEPT == REMOVED + the one known clause).
# Closing this properly needs a semantic check (e.g. an LLM-based reviewer of
# the rendered template against the prohibited-meaning list), which is out of
# scope for this module.

RESIDUAL_TRIPWIRES = RESIDUAL_TRIPWIRES_KO + RESIDUAL_TRIPWIRES_EN

# The one remaining packet-boundary sentence in the H1a-native template.
# The liveness clause is appended immediately after it, for KEPT only.
_INSERTION_ANCHOR = "or external sources."


class ContractDriftError(Exception):
    """Raised when a source artifact (the ruling file or E2.4's frozen
    contract) no longer matches the text this module was built against.
    Never silently proceed."""


def _normalize_clause(raw: str) -> str:
    """Collapse a clause's original bulleted/line-wrapped layout to a single
    prose sentence for embedding in the new template's paragraph.

    Whitespace-only: every non-whitespace character is preserved in order.
    test_h1a_contract.py checks that by stripping all whitespace from both
    the raw and normalized forms and comparing them -- the normalization
    cannot silently drop or alter a word while collapsing formatting.
    """
    return " ".join(raw.strip().lstrip("-").split())


LIVENESS_CLAUSE_TEXT = (
    _normalize_clause(LIVENESS_PRIORITY_CLAUSES["L8"])
    + " "
    + _normalize_clause(LIVENESS_PRIORITY_CLAUSES["L24_25"])
)


def load_h1a_native_template(path: Path = DESIGN_DECISION_PATH) -> str:
    """The H1a-native prompt template, loaded verbatim from
    `h1a_prompt_template.md`'s first ```text fenced block.

    Loaded rather than retyped into this module -- retyping is exactly the
    transcription-error mode this project's provenance rules exist to
    prevent (E2.4_ISSUE_REGISTER has prior incidents from hand-copied text).
    """
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", text, re.DOTALL)
    if not blocks:
        raise ContractDriftError(f"{path}: no ```text fenced block found")
    return blocks[0]


def render_arm(template: str, arm: str) -> str:
    """Return the arm-specific H1a-native prompt (payload slot unfilled).

    PROHIBITION_KEPT inserts Q1's frozen liveness clauses immediately after
    the template's packet-boundary sentence. PROHIBITION_REMOVED is the
    template unchanged.
    """
    if arm not in ARMS:
        raise ValueError(f"arm must be one of {ARMS}, got {arm!r}")
    if arm == "PROHIBITION_REMOVED":
        return template

    count = template.count(_INSERTION_ANCHOR)
    if count != 1:
        raise ContractDriftError(
            f"insertion anchor {_INSERTION_ANCHOR!r} occurs {count} times in "
            f"the template, expected exactly 1 -- the ruling's template "
            f"drifted from the text this module was built against"
        )
    return template.replace(
        _INSERTION_ANCHOR, f"{_INSERTION_ANCHOR} {LIVENESS_CLAUSE_TEXT}", 1
    )


def assert_no_residual_prohibition(removed_arm_text: str) -> None:
    """Structural guard first (normalized clause absence), keyword tripwire
    second -- the two-tier pattern manipulation-scope requirement 8 asks for.

    Both language surfaces are scanned. Korean is matched as written (the
    frozen clauses are Korean and case has no meaning there); English is
    matched case-insensitively, since a prohibition someone types into the
    ruling file will not match the casing of this list by luck.
    """
    assert LIVENESS_CLAUSE_TEXT not in removed_arm_text, (
        "residual prohibition: the combined liveness clause text is present"
    )
    for clause_id, clause_text in LIVENESS_PRIORITY_CLAUSES.items():
        normalized = _normalize_clause(clause_text)
        assert normalized not in removed_arm_text, (
            f"residual prohibition: normalized clause {clause_id!r} still present"
        )
    for tripwire in RESIDUAL_TRIPWIRES_KO:
        assert tripwire not in removed_arm_text, (
            f"residual prohibition: KO tripwire {tripwire!r} still present"
        )
    lowered = removed_arm_text.lower()
    for tripwire in RESIDUAL_TRIPWIRES_EN:
        assert tripwire.lower() not in lowered, (
            f"residual prohibition: EN tripwire {tripwire!r} still present"
        )


def diff_is_restricted_to_the_liveness_clause(kept_text: str, removed_text: str) -> tuple[bool, list]:
    """The rendered diff between arms must be restricted to the inserted
    liveness clause (plus the one mechanically-required space) -- nothing
    else. Proved by reconstruction, not character-level diffing: rebuild
    PROHIBITION_KEPT from PROHIBITION_REMOVED by inserting exactly the
    expected span at the expected anchor, and require byte equality with the
    actual KEPT text. (`difflib.SequenceMatcher` was tried for the analogous
    Q1 check and rejected -- its greedy LCS misaligns deletion boundaries
    around short repeated substrings.)
    """
    expected_kept = render_arm(removed_text, "PROHIBITION_KEPT")
    if expected_kept == kept_text:
        return True, []
    for i, (a, b) in enumerate(zip(expected_kept, kept_text)):
        if a != b:
            return False, [f"diverges at index {i}: expected {a!r}, got {b!r}"]
    return False, [
        f"length mismatch: expected {len(expected_kept)}, got {len(kept_text)}"
    ]
