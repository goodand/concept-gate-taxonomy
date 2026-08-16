"""Tests for the independent bounded semantic compiler -- Q13.6 sec 9.

Two properties carry the whole design and each has a test that fails first if
it is undone:

  - INDEPENDENCE (`test_the_compiler_does_not_import_the_policy_or_renderer`).
    Checked with AST, not asked for in a comment. A compiler that reads
    `_h1a_policy.AXIS_SURFACE_TOKENS` agrees with the renderer by
    construction and audits nothing -- the "true proposition about the wrong
    object" failure this experiment has already hit twice.
  - FAIL-CLOSED (`test_silence_about_an_unproven_family_is_unknown_...`).
    sec 9.6 permits reading silence as `absent_verified` only after
    demonstrated detection. The unsafe direction is a confident absence, so
    that is the one pinned.
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_semantic_compiler_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


sc = _load("sc", "_h1a_semantic_compiler.py")
cap = _load("cap", "_h1a_compiler_capability.py")
contract = _load("contract", "_h1a_contract.py")


def _rendered(arm: str) -> str:
    return contract.render_arm(contract.load_h1a_native_template(), arm)


# --- independence ---------------------------------------------------------

FORBIDDEN_IMPORTS = {"_h1a_policy", "_h1a_contract", "_h1a_surface"}


def test_the_compiler_does_not_import_the_policy_or_renderer():
    """sec 9.4: the compiler is an INDEPENDENT drift auditor. If it imports
    the canonical policy or the renderer, it inherits their vocabulary and
    confirms them by construction."""
    tree = ast.parse((HERE / "_h1a_semantic_compiler.py").read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    leaked = imported & FORBIDDEN_IMPORTS
    assert not leaked, (
        f"the semantic compiler imports {sorted(leaked)}, so it is no longer "
        f"independent of what it audits (Q13.6 sec 9.4)"
    )


# --- fail-closed (sec 9.6) ------------------------------------------------

def test_silence_about_an_unproven_family_is_unknown_not_absent_verified():
    """The load-bearing safety property."""
    graph = sc.compile_policy_graph("Nothing policy-like here at all.", "removed")
    states = {c["policy_id"]: c["state"] for c in graph["claims"]}
    assert set(states.values()) == {sc.UNKNOWN}
    assert sc.ABSENT_VERIFIED not in states.values()


def test_absent_verified_requires_the_family_to_be_proven():
    text = "Nothing policy-like here at all."
    unproven = sc.compile_policy_graph(text, "removed", proven_families=frozenset())
    proven = sc.compile_policy_graph(
        text, "removed", proven_families=frozenset({sc.EVIDENCE_COUNT_PROHIBITION}))

    def state(graph, pid):
        return next(c["state"] for c in graph["claims"] if c["policy_id"] == pid)

    assert state(unproven, sc.EVIDENCE_COUNT_PROHIBITION) == sc.UNKNOWN
    assert state(proven, sc.EVIDENCE_COUNT_PROHIBITION) == sc.ABSENT_VERIFIED


def test_a_detected_family_is_present_even_when_unproven():
    """Detection is evidence of presence regardless of capability status --
    only ABSENCE claims need the capability gate."""
    graph = sc.compile_policy_graph(
        "Do not break ties using the order in which evidence items appear.",
        "removed", proven_families=frozenset())
    claim = next(c for c in graph["claims"]
                 if c["policy_id"] == sc.EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION)
    assert claim["state"] == sc.PRESENT
    assert claim["capability_proven"] is False


def test_arm_is_validated():
    with pytest.raises(sc.CompilerContractError, match="arm must be one of"):
        sc.compile_policy_graph("text", "PROHIBITION_KEPT")


# --- capability suite computes, never declares ----------------------------

def test_proven_families_is_derived_from_fixtures_not_hardcoded():
    """If someone replaces the computation with a literal, the two stop
    agreeing the moment a detector regresses."""
    report = cap.evaluate_capability()
    recomputed = frozenset(
        pid for pid in sc.POLICY_FAMILIES if cap.evaluate_family(pid)["proven"])
    assert report["proven_families"] == recomputed
    assert cap.proven_families() == recomputed


def test_a_family_needs_both_directions_to_count_as_proven():
    """sec 9.6 requires positive AND negative fixtures. Passing every
    positive while never being tested for false positives is not
    demonstrated capability."""
    for pid in sc.POLICY_FAMILIES:
        result = cap.evaluate_family(pid)
        if result["proven"]:
            assert result["positive"], pid
            assert result["negative"], pid


def test_families_without_fixtures_are_not_proven():
    for pid in sc.POLICY_FAMILIES:
        result = cap.evaluate_family(pid)
        if not result["positive"] or not result["negative"]:
            assert result["proven"] is False, pid


def test_the_capability_report_names_unproven_target_critical_families():
    """Honest reporting of what is NOT demonstrated is the point of the gate;
    Q13.5 then forbids leaving those unknown at freeze."""
    report = cap.evaluate_capability()
    assert set(report["target_critical_unproven"]) == (
        sc.TARGET_CRITICAL - report["proven_families"])


# --- what the compiler actually observes on the live prompts --------------

def test_the_manipulated_axis_is_present_in_kept_and_absent_in_removed():
    """The whole experiment's identifiability claim, checked by a reader that
    never consulted the policy module."""
    proven = cap.proven_families()
    assert sc.SOURCE_META_REASONING_PROHIBITION in proven, (
        "this assertion is only meaningful while the compiler's ability to "
        "detect the manipulated axis is demonstrated"
    )

    def state(arm_label, arm):
        graph = sc.compile_policy_graph(_rendered(arm), arm_label, proven_families=proven)
        return next(c["state"] for c in graph["claims"]
                    if c["policy_id"] == sc.SOURCE_META_REASONING_PROHIBITION)

    assert state("kept", "PROHIBITION_KEPT") == sc.PRESENT
    assert state("removed", "PROHIBITION_REMOVED") == sc.ABSENT_VERIFIED


def test_no_experiment_arm_disclosure_in_either_rendered_arm():
    for arm_label, arm in (("kept", "PROHIBITION_KEPT"), ("removed", "PROHIBITION_REMOVED")):
        graph = sc.compile_policy_graph(_rendered(arm), arm_label)
        assert graph["structural"][sc.EXPERIMENT_ARM_DISCLOSURE] == [], arm


def test_arm_disclosure_detector_is_not_vacuous():
    """Recall for the structural check."""
    graph = sc.compile_policy_graph(
        "You are in the PROHIBITION_KEPT arm of this experiment.", "kept")
    assert graph["structural"][sc.EXPERIMENT_ARM_DISCLOSURE]


def test_repeated_mentions_does_not_claim_to_establish_duplicate_carriage():
    """It over-reports on the live prompt (one policy elaborated across
    sentences reads as several), so it must present as a candidate list. A
    check that looks authoritative and is not gets believed."""
    graph = sc.compile_policy_graph(_rendered("PROHIBITION_REMOVED"), "removed")
    block = graph["structural"][sc.DUPLICATE_CARRIER]
    assert block["establishes_duplicate_carriage"] is False
    assert "carrier registry" in block["note"]


def test_dangling_reference_detector_finds_an_unresolved_arm_specific_clause():
    """The defect class that produced D-H1a-13: the ruling's own prescribed
    sentence referred to a clause REMOVED does not contain."""
    graph = sc.compile_policy_graph(
        "Source evaluation is governed by the arm-specific source-evaluation "
        "clause.", "removed")
    dangling = graph["structural"][sc.DANGLING_REFERENCE]
    assert dangling
    assert dangling[0]["resolved_to"] is None


def test_live_prompts_carry_no_dangling_reference():
    """Q13 deleted that sentence; this is the regression check."""
    for arm in ("PROHIBITION_KEPT", "PROHIBITION_REMOVED"):
        graph = sc.compile_policy_graph(_rendered(arm), "kept" if "KEPT" in arm else "removed")
        assert graph["structural"][sc.DANGLING_REFERENCE] == [], arm


# --- assurance ceiling (sec 9.5) ------------------------------------------

def test_the_graph_never_claims_more_than_semantic_reviewed():
    graph = sc.compile_policy_graph(_rendered("PROHIBITION_REMOVED"), "removed")
    assert graph["assurance"] == "SEMANTIC_REVIEWED"
    assert "RULE_CHECKED" not in graph["assurance"]
    assert "min(" in graph["assurance_note"]


def test_unresolved_target_critical_reports_only_unknown_ones():
    proven = cap.proven_families()
    graph = sc.compile_policy_graph(
        _rendered("PROHIBITION_REMOVED"), "removed", proven_families=proven)
    unresolved = sc.unresolved_target_critical(graph)
    for pid in unresolved:
        claim = next(c for c in graph["claims"] if c["policy_id"] == pid)
        assert claim["state"] == sc.UNKNOWN
        assert pid in sc.TARGET_CRITICAL


# --- known detection limits must stay real --------------------------------

def test_known_detection_limits_are_not_stale():
    """If a recorded limit silently starts working, the record has become a
    false claim about the compiler's weakness -- remove the entry rather than
    leave it. Mirrors `test_guard_negative_coverage`'s staleness check."""
    for policy_id, cases in cap.KNOWN_DETECTION_LIMITS.items():
        detector = sc._DETECTORS[policy_id]
        for sentence, reason in cases.items():
            found, _, _ = detector(sentence)
            assert not found, (
                f"{policy_id} now detects {sentence!r}; delete its "
                f"KNOWN_DETECTION_LIMITS entry instead of keeping a stale "
                f"claim that it cannot ({reason})"
            )


def test_every_known_limit_has_a_reason_and_an_owner():
    for policy_id, cases in cap.KNOWN_DETECTION_LIMITS.items():
        assert cases, policy_id
        for sentence, reason in cases.items():
            assert len(reason) > 40, (policy_id, sentence)
            assert "Owner:" in reason, (policy_id, sentence)


def test_global_default_permission_capability_is_now_demonstrated():
    """Q13.5 forbids leaving a target-critical family unknown at freeze, and
    this was the last one outstanding."""
    report = cap.evaluate_capability()
    assert sc.GLOBAL_DEFAULT_PERMISSION in report["proven_families"]
    assert report["target_critical_unproven"] == []
