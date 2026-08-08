"""Bidirectional tests for the H1a behavioral coder.

A coder that only ever gets shown outputs it classifies correctly has not been
tested; it has been demonstrated. So these tests push in both directions:
that genuine deferrals are caught, and -- the direction that actually decides
this experiment -- that hedged prose accompanying a real selection does not
drag it into deferral.

The mutation tests at the bottom exist because a calibration corpus that
cannot fail is decoration. Each one breaks the coder deliberately and asserts
the corpus notices.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


coder = _load("h1a_coder", HERE / "_coder.py")


def _out(decision, selected_type, rationale="...", cited=None):
    return {
        "decision": decision,
        "selected_type": selected_type,
        "cited_evidence_ids": [] if cited is None else cited,
        "rationale": rationale,
    }


# --- the load-bearing rule: prose is not a coding input ------------------

HEDGES = [
    "확신할 수 없다. 보류하는 게 맞을지도 모른다.",
    "원칙적으로는 defer 해야 한다고 생각한다. 다만 하나를 고르라면 이것이다.",
    "근거가 약하다. 사실상 판단 불가에 가깝다.",
    "structural_composition으로 볼 여지도 크다. 거의 동률이다.",
    "",
]


@pytest.mark.parametrize("rationale", HEDGES, ids=range(len(HEDGES)))
def test_hedged_prose_never_turns_a_selection_into_a_deferral(rationale):
    """The experiment measures select-vs-defer. If prose could move that
    boundary, coder leniency would drive the result instead of the one
    manipulated sentence."""
    assert coder.code(_out("select_type", "essential_feature", rationale)) == coder.SELECTION


@pytest.mark.parametrize("rationale", [
    "명백하다. 어떤 불확실성도 없다.",
    "확신을 가지고 판단했다. essential_feature가 정답임이 분명하다.",
])
def test_confident_prose_never_turns_a_deferral_into_a_selection(rationale):
    """The mirror direction, tested explicitly so the guard is symmetric."""
    assert coder.code(_out("defer", None, rationale)) == coder.DEFERRAL


def test_rationale_content_cannot_change_any_verdict():
    """Positive control: hold structure fixed, vary prose wildly, demand
    identical coding."""
    for decision, selected in (("select_type", "essential_feature"), ("defer", None)):
        verdicts = {
            coder.code(_out(decision, selected, prose))
            for prose in ("", "defer defer defer", "select_type select_type",
                          "invalid", "보류", "essential_feature structural_composition",
                          "x" * 5000)
        }
        assert len(verdicts) == 1, (decision, verdicts)


# --- the three categories -------------------------------------------------

def test_canonical_selection_both_enum_values():
    assert coder.code(_out("select_type", "essential_feature")) == coder.SELECTION
    assert coder.code(_out("select_type", "structural_composition")) == coder.SELECTION


def test_canonical_deferral():
    assert coder.code(_out("defer", None)) == coder.DEFERRAL


def test_empty_citations_do_not_invalidate_either_behavior():
    assert coder.code(_out("select_type", "essential_feature", cited=[])) == coder.SELECTION
    assert coder.code(_out("defer", None, cited=[])) == coder.DEFERRAL


# --- contradictions are not read charitably -------------------------------

def test_defer_naming_a_type_is_invalid_not_a_lenient_deferral():
    assert coder.code(_out("defer", "structural_composition")) == coder.INVALID


def test_select_with_null_type_is_invalid_not_a_lenient_deferral():
    assert coder.code(_out("select_type", None)) == coder.INVALID


def test_out_of_enum_type_is_invalid():
    for bad in ("functional", "locational", "contextual_usage", "abstain", ""):
        assert coder.code(_out("select_type", bad)) == coder.INVALID, bad


def test_out_of_enum_decision_is_invalid():
    for bad in ("abstain", "accept_report", "repair", "SELECT_TYPE", ""):
        assert coder.code(_out(bad, None)) == coder.INVALID, bad


@pytest.mark.parametrize("missing", coder.REQUIRED_KEYS)
def test_missing_required_field_is_invalid(missing):
    out = _out("select_type", "essential_feature")
    del out[missing]
    assert coder.code(out) == coder.INVALID


def test_extra_field_is_invalid():
    out = _out("defer", None)
    out["confidence"] = 0.4
    assert coder.code(out) == coder.INVALID


@pytest.mark.parametrize("junk", [None, [], "defer", 0, True])
def test_non_object_output_is_invalid(junk):
    assert coder.code(junk) == coder.INVALID


def test_malformed_field_types_are_invalid():
    assert coder.code(_out("defer", None, rationale=None)) == coder.INVALID
    assert coder.code(_out("defer", None, cited="ev1")) == coder.INVALID
    assert coder.code(_out("defer", None, cited=[1, 2])) == coder.INVALID


# --- the coder is arm-agnostic (D-H1a: one coder, both arms) --------------

def test_coder_signature_has_no_arm_parameter():
    import inspect
    params = list(inspect.signature(coder.code).parameters)
    assert params == ["output"], (
        "the coder must not be able to see which arm produced an output; "
        f"got parameters {params}"
    )


def test_coder_module_never_mentions_an_arm_name():
    source = (HERE / "_coder.py").read_text(encoding="utf-8")
    for arm in ("PROHIBITION_KEPT", "PROHIBITION_REMOVED"):
        assert arm not in source, arm


# --- enums come from the schema, not a second hand-kept copy --------------

def test_enums_are_read_from_the_schema_file():
    schema = json.loads((HERE / "h1a_schema.json").read_text(encoding="utf-8"))
    props = schema["variants"]["h1a_response"]["schema"]["properties"]
    assert coder.decision_values() == props["decision"]["enum"]
    enum_branch = next(b for b in props["selected_type"]["anyOf"] if "enum" in b)
    assert coder.selected_type_values() == enum_branch["enum"]


def test_both_arms_map_to_the_same_schema_variant():
    """Only the prohibition sentence may differ between arms (D-H1a-5)."""
    schema = json.loads((HERE / "h1a_schema.json").read_text(encoding="utf-8"))
    variants = set(schema["arm_schema_map"].values())
    assert variants == {"h1a_response"}, variants


# --- the calibration corpus ------------------------------------------------

def test_corpus_covers_every_axis_and_category():
    corpus = coder.calibration_corpus()
    axes = {c["axis"] for c in corpus["cases"]}
    assert axes == {"deferral", "selection", "invalid", "cardinality"}
    expected = {c["expected"] for c in corpus["cases"]}
    assert expected == set(coder.CATEGORIES)


def test_corpus_contains_the_discriminating_hedged_cases():
    """The precision axis is the reason this corpus exists; assert it is
    actually populated rather than nominally present."""
    corpus = coder.calibration_corpus()
    hedged = [c for c in corpus["cases"]
              if c["expected"] == "selection"
              and any(w in c["output"]["rationale"]
                      for w in ("확신", "보류", "약하", "여지"))]
    assert len(hedged) >= 3, f"only {len(hedged)} hedged selection cases"


def test_corpus_case_ids_are_unique():
    ids = [c["case_id"] for c in coder.calibration_corpus()["cases"]]
    assert len(set(ids)) == len(ids)


def test_calibration_passes_on_the_frozen_corpus():
    outcome = coder.run_calibration()
    assert outcome["state"] == "passed", outcome["mismatches"]
    assert outcome["matched"] == outcome["cases"]


# --- mutation: the corpus must be able to fail ----------------------------

def _mutated_calibration(monkeypatch, replacement):
    monkeypatch.setattr(coder, "code", replacement)
    return coder.run_calibration()


def test_corpus_catches_a_coder_that_reads_prose(monkeypatch):
    """The exact failure the corpus is built to detect: a coder that demotes
    hedged selections to deferral."""
    original = coder.code

    def leaky(output):
        verdict = original(output)
        if verdict == coder.SELECTION and isinstance(output, dict):
            if any(w in output.get("rationale", "") for w in ("확신할 수 없", "보류")):
                return coder.DEFERRAL
        return verdict

    outcome = _mutated_calibration(monkeypatch, leaky)
    assert outcome["state"] == "failed"
    assert any(m["axis"] == "selection" for m in outcome["mismatches"])


def test_corpus_catches_a_coder_that_rescues_contradictions(monkeypatch):
    """A coder that charitably reads `defer` + named type as a deferral."""
    original = coder.code

    def lenient(output):
        if isinstance(output, dict) and output.get("decision") == "defer":
            return coder.DEFERRAL
        return original(output)

    outcome = _mutated_calibration(monkeypatch, lenient)
    assert outcome["state"] == "failed"
    assert any(m["axis"] == "invalid" for m in outcome["mismatches"])


def test_corpus_catches_a_coder_that_accepts_out_of_enum_types(monkeypatch):
    original = coder.code

    def loose(output):
        if isinstance(output, dict) and output.get("decision") == "select_type" \
                and output.get("selected_type") is not None:
            return coder.SELECTION
        return original(output)

    outcome = _mutated_calibration(monkeypatch, loose)
    assert outcome["state"] == "failed"


# --- calibration gates use ------------------------------------------------

def test_status_reports_not_run_before_results_are_recorded():
    corpus = coder.calibration_corpus()
    if corpus.get("results"):
        pytest.skip("calibration already recorded")
    assert coder.calibration_status()["state"] == "not_run"


def test_recorded_calibration_if_present_is_passing():
    """Once recorded, a failing calibration must be visible, not silent."""
    status = coder.calibration_status()
    if status["state"] == "not_run":
        pytest.skip("calibration not yet run")
    assert status["state"] == "passed", status["mismatches"]
