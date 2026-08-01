"""H1a arm-prompt construction -- H1a-native template per Q3=B.

Two external rulings shaped this module, in sequence:

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

What this module does
----------------------
The H1a-native template lives in `DESIGN_DECISION_H1a_prompt_surface.md`
itself (the first ```text fenced block under "Recommended H1a-native prompt
shape"), loaded here rather than retyped -- retyping is exactly the
transcription-error mode this project's provenance rules exist to prevent.
Q1's frozen liveness clauses (still the correct, ruling-approved bytes -- Q3
did not reopen Q1) are inserted into that template for PROHIBITION_KEPT only,
immediately after the template's own "external sources." sentence, which is
the one remaining packet-boundary locus once E2.4's rule 1 and preamble were
dropped. This positions them at the ruling's "frozen locations" as literally
as a template with only one packet-boundary paragraph allows.

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
DESIGN_DECISION_PATH = HERE / "DESIGN_DECISION_H1a_prompt_surface.md"

ARMS = ("PROHIBITION_KEPT", "PROHIBITION_REMOVED")

# Q1's frozen clauses (unchanged from the manipulation-scope ruling). Kept as
# the raw, as-approved bytes -- see LIVENESS_CLAUSE_TEXT below for the
# whitespace-normalized form actually inserted into the new template.
LIVENESS_PRIORITY_CLAUSES = {
    "L8": " 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.",
    "L24_25": (
        "   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를\n"
        "     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.\n"
    ),
}

# Secondary tripwire (manipulation-scope requirement 8: "keyword scanning may
# be a secondary tripwire, not the sole proof of absence"). The primary proof
# is LIVENESS_PRIORITY_CLAUSES absence, checked structurally above.
#
# Korean surface -- the language Q1's frozen clauses are written in.
RESIDUAL_TRIPWIRES_KO = (
    "liveness", "우선순위를 재판정", "더 최신인지", "더 권위 있는지",
    "아직 살아있는", "추론하지 마라", "판정은 이미 끝났", "너의 범위가 아니다",
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
# case-insensitive. test_h1a_contract.py pins BOTH directions -- each of the
# ruling's seven propositions is caught (recall), and the clean template
# passes (precision).
RESIDUAL_TRIPWIRES_EN = (
    "liveness",
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
)

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
    """The H1a-native prompt template, loaded verbatim from the ruling file's
    first ```text fenced block (under "Recommended H1a-native prompt shape").

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
