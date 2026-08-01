"""Tests for the H1a arm-prompt construction (Q3=B ruling).

The load-bearing claim: PROHIBITION_REMOVED contains no clause equivalent to
"do not judge liveness/priority/recency/authority", and the two arms differ
by exactly that clause and nothing else -- the same proposition Q1's blocker
#16 needed, now checked against the H1a-native template rather than E2.4's
contract_prompt.md.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
E24 = REPO_ROOT / "experiments" / "2026-07-25_e2.4_repo_grounded_contract_transfer"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


h1a_contract = _load("h1a_contract", HERE / "_h1a_contract.py")
h1a_surface = _load("h1a_surface_for_contract", HERE / "_h1a_surface.py")
h1a_schema = json.loads((HERE / "h1a_schema.json").read_text(encoding="utf-8"))


def template() -> str:
    return h1a_contract.load_h1a_native_template()


# --- the template is loaded from the ruling file, not retyped --------------

def test_ruling_file_has_the_template_fence():
    assert h1a_contract.DESIGN_DECISION_PATH.exists()
    t = template()
    assert t.startswith("You are an MCP client agent.")
    assert "{payload_json}" in t


def test_missing_fence_raises_loudly(tmp_path):
    bogus = tmp_path / "no_fence.md"
    bogus.write_text("# nothing here\n", encoding="utf-8")
    with pytest.raises(h1a_contract.ContractDriftError):
        h1a_contract.load_h1a_native_template(bogus)


# --- Q1's clauses trace back to E2.4's unchanged original text -------------
#
# Q5=B (2026-08-01) shortened LIVENESS_PRIORITY_CLAUSES["L24_25"] to two
# sentences, dropping the dangling third sentence. E2.4's own frozen
# contract_prompt.md is NOT touched by Q5 -- it still carries the original
# three-sentence form. So the check is no longer "our clause occurs verbatim
# in E2.4" (it doesn't, by design); it is "E2.4's original text is unchanged,
# and our shortened clause is a documented, deliberate prefix of it."

def _e24_contract_block() -> str:
    e24_surface = _load("e24_surface_for_h1a_contract", E24 / "_surface.py")
    return e24_surface.load_contract_prompt(E24 / "contract_prompt.md")


def test_l8_clause_still_occurs_exactly_once_in_e24_contract():
    block = _e24_contract_block()
    assert block.count(h1a_contract.LIVENESS_PRIORITY_CLAUSES["L8"]) == 1


def test_l24_25_clause_is_q5s_documented_prefix_of_the_unchanged_e24_original():
    block = _e24_contract_block()
    original_three_sentence_form = (
        "   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를\n"
        "     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.\n"
    )
    assert block.count(original_three_sentence_form) == 1, (
        "E2.4's original three-sentence clause must remain unchanged -- Q5 "
        "only shortens H1a's own copy, it does not edit E2.4's frozen file"
    )
    shortened = h1a_contract.LIVENESS_PRIORITY_CLAUSES["L24_25"]
    assert shortened != original_three_sentence_form
    assert h1a_contract._normalize_clause(shortened) in \
        h1a_contract._normalize_clause(original_three_sentence_form)
    assert "그 판정은 이미 끝났고 너의 범위가 아니다" not in shortened


# --- normalization preserves content, only collapses whitespace -----------

def test_normalization_preserves_every_non_whitespace_character():
    for clause_id, raw in h1a_contract.LIVENESS_PRIORITY_CLAUSES.items():
        normalized = h1a_contract._normalize_clause(raw)
        raw_no_ws = re.sub(r"\s+", "", raw).lstrip("-")
        norm_no_ws = re.sub(r"\s+", "", normalized)
        assert raw_no_ws == norm_no_ws, clause_id


# --- PROHIBITION_REMOVED is the template, unchanged -------------------------

def test_removed_arm_is_byte_identical_to_the_template():
    t = template()
    assert h1a_contract.render_arm(t, "PROHIBITION_REMOVED") == t


# --- PROHIBITION_KEPT inserts the clause at the one packet-boundary locus --

def test_kept_arm_contains_the_combined_liveness_clause():
    kept = h1a_contract.render_arm(template(), "PROHIBITION_KEPT")
    assert h1a_contract.LIVENESS_CLAUSE_TEXT in kept


def test_kept_arm_inserts_immediately_after_the_packet_boundary_sentence():
    kept = h1a_contract.render_arm(template(), "PROHIBITION_KEPT")
    assert (
        "or external sources. " + h1a_contract.LIVENESS_CLAUSE_TEXT
    ) in kept


def test_render_arm_rejects_unknown_arm_name():
    with pytest.raises(ValueError):
        h1a_contract.render_arm(template(), "CONTROL_REPO")


def test_render_arm_fails_loudly_if_the_anchor_no_longer_occurs_exactly_once():
    drifted = template().replace("or external sources.", "or external sources. or external sources.")
    with pytest.raises(h1a_contract.ContractDriftError):
        h1a_contract.render_arm(drifted, "PROHIBITION_KEPT")


# --- no residual prohibition in the REMOVED arm -----------------------------

def test_removed_arm_has_no_residual_prohibition():
    h1a_contract.assert_no_residual_prohibition(template())


# --- the residual guard's recall, measured against the ruling's own list ---
#
# Independent review 20260801 finding 7: the guard held only Korean tripwires
# while Q3=B had made the template English, so it passed an English
# prohibition clean. manipulation-scope requirement 7 enumerates seven English
# propositions the guard MUST fail on; these are those seven, written as a
# sentence someone might plausibly add to the ruling file.

RULING_REQUIREMENT_7_PROPOSITIONS = {
    "do not judge liveness":
        "Do not judge the liveness of any source.",
    "do not judge source priority":
        "Do not judge source priority between the evidence items.",
    "do not infer which source is newer":
        "Do not infer which source is newer than the other.",
    "do not infer which source is more authoritative":
        "Do not infer which source is more authoritative.",
    "do not infer whether a source is live code":
        "Do not infer whether a source is live code that still runs.",
    "that judgment is already done":
        "That judgment is already done before you see the packet.",
    "that judgment is outside the model's scope":
        "That judgment is outside your scope as the deciding model.",
}


@pytest.mark.parametrize("proposition,sentence",
                         sorted(RULING_REQUIREMENT_7_PROPOSITIONS.items()))
def test_guard_catches_each_ruling_proposition(proposition, sentence):
    """Recall. A guard that has never been shown to fail proves nothing by
    passing (skills-catalog pattern 8)."""
    injected = template().replace(
        "or external sources.", f"or external sources. {sentence}", 1)
    with pytest.raises(AssertionError):
        h1a_contract.assert_no_residual_prohibition(injected)


def test_guard_catches_the_exact_sentence_the_reviewer_used():
    """The literal injection that exposed the gap, kept as a regression."""
    injected = template().replace(
        "or external sources.",
        "or external sources. Do not judge which source is more authoritative, "
        "newer, or still live; that judgment is already done and is outside "
        "your scope.", 1)
    with pytest.raises(AssertionError):
        h1a_contract.assert_no_residual_prohibition(injected)


def test_guard_is_case_insensitive_on_the_english_surface():
    injected = template().replace(
        "or external sources.",
        "or external sources. THAT JUDGMENT IS ALREADY DONE.", 1)
    with pytest.raises(AssertionError):
        h1a_contract.assert_no_residual_prohibition(injected)


def test_guard_precision_the_clean_template_passes():
    """Precision. Recall without precision would be a guard that fires on
    everything, which is the same as no guard."""
    h1a_contract.assert_no_residual_prohibition(template())


def test_guard_does_not_fire_on_the_templates_legitimate_use_of_outside():
    """`outside` occurs innocently in the template's 'any fields outside
    h1a_observation_v1' (line-wrapped in the source). Only the scoping
    phrases may be matched, never the bare word -- a bare `outside` tripwire
    would fire on the clean template, i.e. zero precision."""
    assert "outside" in template()
    assert "outside" not in h1a_contract.RESIDUAL_TRIPWIRES_EN
    h1a_contract.assert_no_residual_prohibition(template())


def test_removed_arm_keeps_the_general_packet_boundary_sentence():
    t = h1a_contract.render_arm(template(), "PROHIBITION_REMOVED")
    assert "Do not use general ontology knowledge" in t
    assert "or external sources." in t


# --- the diff is restricted to exactly the liveness clause ------------------

def test_diff_between_arms_is_restricted_to_the_liveness_clause():
    t = template()
    kept = h1a_contract.render_arm(t, "PROHIBITION_KEPT")
    removed = h1a_contract.render_arm(t, "PROHIBITION_REMOVED")
    ok, detail = h1a_contract.diff_is_restricted_to_the_liveness_clause(kept, removed)
    assert ok, detail


def test_kept_and_removed_are_not_identical():
    t = template()
    assert h1a_contract.render_arm(t, "PROHIBITION_KEPT") != \
           h1a_contract.render_arm(t, "PROHIBITION_REMOVED")


# --- the embedded schema illustration matches h1a_schema.json exactly ------

def test_embedded_schema_block_matches_h1a_schema_json():
    """Q3.3's ruling explicitly forbids E2.4 fields (repair, abstain, ...)
    appearing as REQUIRED output -- but the template's own consistency
    section legitimately NAMES them as things not to output. The structural
    guarantee we can actually check is that the illustrated schema's fields,
    enum values, and null-ability match h1a_observation_v1 exactly."""
    t = template()
    variant = h1a_schema["variants"]["h1a_response"]["schema"]

    assert '"decision": "select_type" | "defer"' in t
    for enum_value in variant["properties"]["decision"]["enum"]:
        assert f'"{enum_value}"' in t

    type_enum = variant["properties"]["selected_type"]["anyOf"][0]["enum"]
    for enum_value in type_enum:
        assert f'"{enum_value}"' in t
    assert "null" in t

    for field in variant["required"]:
        assert field in t


def test_template_never_silently_requires_an_e24_only_field():
    """The E2.4-only vocabulary that appears in the template does so only
    inside the "Do not output ..." negation -- never as something the model
    is told to actually produce. Checked by requiring each E2.4-only token to
    appear on the same line as "Do not output", and nowhere else."""
    e24_only = ("repair", "accept_report", "abstain", "missing_evidence",
                "contract_verdict", "evidence_audit", "repair_plan")
    t = template()
    lines = t.split("\n")
    negation_lines = [l for l in lines if "Do not output" in l or
                       (lines.index(l) > 0 and "Do not output" in lines[lines.index(l) - 1])]
    for token in e24_only:
        occurrences = [i for i, l in enumerate(lines) if token in l]
        for i in occurrences:
            window = "\n".join(lines[max(0, i - 1):i + 1])
            assert "Do not output" in window, (
                f"{token!r} appears outside the 'Do not output' negation at line {i}: {lines[i]!r}"
            )


# --- server_response never appears (H1a payload has no such key) ----------

def test_template_never_mentions_server_response():
    assert "server_response" not in template()


# --- neutrality: the template does not favor select_type or defer ----------

EVALUATIVE_TOKENS = (
    "correct", "incorrect", "right answer", "wrong answer", "정답", "오답",
    "best", "should prefer", "more reliable", "more trustworthy",
)


def test_template_carries_no_evaluative_language_favoring_either_behavior():
    t = template().lower()
    for token in EVALUATIVE_TOKENS:
        assert token.lower() not in t, token


def test_template_gives_defer_and_select_type_symmetric_treatment():
    """Both instructions are phrased as plain conditionals ('Choose X only
    if/if...'), neither hedged nor encouraged relative to the other. Q7's
    warrant rule (2026-08-01) is the current source of this pairing."""
    t = template()
    assert "Choose select_type only if" in t
    assert "Choose defer if" in t
    assert "Cite the evidence item ids" in t


def test_template_carries_q7_tie_breaker_prohibition_list():
    """Q7's explicit list of forbidden tie-breakers must be present verbatim
    -- this is the rule that replaces the undefined-defer gap C7/Q7 found."""
    t = template()
    for forbidden in ("evidence item count", "source order", "source_kind",
                      "recency", "authority", "liveness", "outside knowledge"):
        assert forbidden in t, forbidden
