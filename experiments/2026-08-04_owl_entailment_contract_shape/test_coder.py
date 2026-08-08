"""Coder calibration -- hand-authored synthetic responses, not real model
output. Per project discipline (checker-recall-and-precision, pattern 8):
an instrument's silence only means something after it has been shown able to
speak. These pin both directions before any trial runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from _coder import code_ea_response, code_eb_response

HERE = Path(__file__).resolve().parent
FIX_A = json.loads((HERE / "fixture_owl_entailment.json").read_text())
FIX_B = json.loads((HERE / "fixture_candidate_vs_entailed.json").read_text())


def _all_correct_ea():
    out = []
    for e in FIX_A["edges"]:
        truth = "asserted" if e["origin"] == "asserted_and_entailed" else "derived"
        out.append({"subject": e["subject"], "object": e["object"],
                     "origin_judgment": truth, "basis": "x"})
    return out


def test_ea_all_correct():
    r = code_ea_response({"per_relationship": _all_correct_ea(), "summary": "x"}, FIX_A)
    assert r["invalid"] is False
    assert r["counts"] == {"correct": 5}


def test_ea_overclaim_derived_as_asserted():
    items = _all_correct_ea()
    for it in items:
        if it["subject"] == "Square" and it["object"] == "Rectangle":
            it["origin_judgment"] = "asserted"
    r = code_ea_response({"per_relationship": items, "summary": "x"}, FIX_A)
    assert r["counts"]["overclaim_derived_as_asserted"] == 1
    assert r["counts"]["correct"] == 4


def test_ea_underclaim_asserted_as_derived():
    items = _all_correct_ea()
    for it in items:
        if it["subject"] == "Rectangle":
            it["origin_judgment"] = "derived"
    r = code_ea_response({"per_relationship": items, "summary": "x"}, FIX_A)
    assert r["counts"]["underclaim_asserted_as_derived"] == 1


def test_ea_cannot_tell_is_its_own_category_not_correct_or_error():
    items = _all_correct_ea()
    items[0]["origin_judgment"] = "cannot_tell"
    r = code_ea_response({"per_relationship": items, "summary": "x"}, FIX_A)
    assert r["counts"]["cannot_tell"] == 1
    assert "correct" not in r["counts"] or r["counts"]["correct"] == 4


def test_ea_invalid_enum_value_is_invalid_not_silently_coerced():
    items = _all_correct_ea()
    items[0]["origin_judgment"] = "probably_asserted"
    r = code_ea_response({"per_relationship": items, "summary": "x"}, FIX_A)
    assert r["invalid"] is True


def test_ea_missing_edge_is_invalid():
    items = _all_correct_ea()[:-1]  # drop one edge
    r = code_ea_response({"per_relationship": items, "summary": "x"}, FIX_A)
    assert r["invalid"] is True


def test_ea_malformed_shape_is_invalid_not_a_crash():
    r = code_ea_response({"summary": "x"}, FIX_A)
    assert r["invalid"] is True
    r2 = code_ea_response({"per_relationship": "not a list"}, FIX_A)
    assert r2["invalid"] is True


def _all_correct_eb():
    out = []
    for e in FIX_B["edges"]:
        truth = "verified" if e["assurance"] == "REASONER_PROVED" else "not_verified"
        out.append({"subject": e["subject"], "object": e["object"],
                     "verification_judgment": truth, "basis": "x"})
    return out


def test_eb_all_correct():
    r = code_eb_response({"per_relationship": _all_correct_eb(), "summary": "x"}, FIX_B)
    assert r["invalid"] is False
    assert r["counts"] == {"correct": 2}


def test_eb_laundering_is_its_own_named_category():
    """The failure mode this experiment exists to detect."""
    items = _all_correct_eb()
    for it in items:
        if it["subject"] == "Trapezoid":
            it["verification_judgment"] = "verified"
    r = code_eb_response({"per_relationship": items, "summary": "x"}, FIX_B)
    assert r["counts"]["laundered_proposed_as_verified"] == 1
    assert r["counts"]["correct"] == 1


def test_eb_excess_caution_is_a_different_category_from_laundering():
    items = _all_correct_eb()
    for it in items:
        if it["subject"] == "Square":
            it["verification_judgment"] = "not_verified"
    r = code_eb_response({"per_relationship": items, "summary": "x"}, FIX_B)
    assert r["counts"]["excess_caution_proven_as_unverified"] == 1
    assert "laundered_proposed_as_verified" not in r["counts"]


def test_eb_cannot_tell_is_separate():
    items = _all_correct_eb()
    items[0]["verification_judgment"] = "cannot_tell"
    r = code_eb_response({"per_relationship": items, "summary": "x"}, FIX_B)
    assert r["counts"]["cannot_tell"] == 1


def test_eb_invalid_enum_value_is_invalid():
    items = _all_correct_eb()
    items[0]["verification_judgment"] = "probably_fine"
    r = code_eb_response({"per_relationship": items, "summary": "x"}, FIX_B)
    assert r["invalid"] is True
