"""Fixture and surface-copy checks for H1a.

Two things need pinning here that the coder tests do not cover.

First, H1a carries a *copy* of E2.4's frozen surface pipeline (D-H1a-1 = B).
A copy is a liability: it can drift from its original silently, and then H1a
would be running a builder nobody audited. So the deviation is enumerated and
tested rather than described.

Second, the fixture's whole point is a genuine conflict between documentation
and live code about one exact concept/feature pair. If either side turns out
not to be instance-bound, or if the harness's own knowledge that the docs are
older leaks into the model payload, the manipulated variable is destroyed and
the experiment measures nothing.
"""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
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


h1a_surface = _load("h1a_surface", HERE / "_h1a_surface.py")
e24_surface = _load("e24_surface_for_h1a", E24 / "_surface.py")

FIXTURE_PATH = HERE / "fixture_source_authority.json"


def fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


# --- the surface copy must not drift from its original --------------------

DOCUMENTED_DEVIATIONS = {"ELIGIBILITY_PROFILES", "_eligibility_profile"}


def test_h1a_surface_deviates_from_e2_4_only_where_documented():
    """Every function body except the one documented deviation must be
    byte-identical to E2.4's frozen original."""
    drifted = []
    for name, e24_fn in vars(e24_surface).items():
        if not inspect.isfunction(e24_fn) or name in DOCUMENTED_DEVIATIONS:
            continue
        h1a_fn = getattr(h1a_surface, name, None)
        assert h1a_fn is not None, f"{name} disappeared from the H1a copy"
        if inspect.getsource(h1a_fn) != inspect.getsource(e24_fn):
            drifted.append(name)
    assert not drifted, f"undocumented drift from E2.4's surface: {drifted}"


def test_h1a_surface_constants_match_except_the_documented_one():
    for name, value in vars(e24_surface).items():
        if name.startswith("_") or name in DOCUMENTED_DEVIATIONS:
            continue
        if not isinstance(value, (str, tuple, frozenset, set, dict)):
            continue
        assert getattr(h1a_surface, name, None) == value, name


def test_the_deviation_is_exactly_the_docs_profile():
    added = h1a_surface.ELIGIBILITY_PROFILES - e24_surface.ELIGIBILITY_PROFILES
    assert added == {"repository_prose"}
    assert not (e24_surface.ELIGIBILITY_PROFILES - h1a_surface.ELIGIBILITY_PROFILES)


def test_e24_surface_still_rejects_docs_paths():
    """The reason the deviation exists. If E2.4 ever accepts docs/ on its own,
    this copy's justification is gone and should be revisited."""
    ref = {"kind": "file_lines", "path": "docs/anything.md", "start_line": 1, "end_line": 1}
    with pytest.raises(e24_surface.SurfaceError):
        e24_surface._eligibility_profile(ref, "doc")


def test_profile_name_does_not_assert_staleness():
    """A profile named `stale_documentation` would be the harness recording
    the very judgment H1a is asking about."""
    banned = ("stale", "outdated", "obsolete", "superseded", "deprecated", "old")
    for profile in h1a_surface.ELIGIBILITY_PROFILES:
        assert not any(word in profile.lower() for word in banned), profile


# --- the fixture qualifies against the live repository --------------------

def test_fixture_qualifies_with_tests_actually_run():
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=True)
    assert manifest["status"] == "passed"
    assert len(manifest["evidence_checks"]) == 4
    for check in manifest["evidence_checks"]:
        assert check["locator_resolved"], check["evidence_id"]
        assert check["excerpt_exact_match"], check["evidence_id"]
        assert check["text_sha256_verified"], check["evidence_id"]


def test_cited_test_is_actually_executed_and_passes():
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=True)
    ev4 = next(c for c in manifest["evidence_checks"] if c["evidence_id"] == "ev4")
    assert ev4["eligibility_profile"] == "verified_by_passing_test"
    assert ev4["verification_refs"], "the R6b test must have been run, not assumed"
    assert "(not run)" not in ev4["verification_refs"][0]


def test_every_evidence_text_is_verbatim_from_its_source():
    for item in fixture()["evidence_sources"]:
        ref = item["source_ref"]
        if ref["kind"] == "test":
            body = (REPO_ROOT / ref["path"]).read_text(encoding="utf-8")
            assert item["text"] in body, item["evidence_id"]
        else:
            lines = (REPO_ROOT / ref["path"]).read_text(encoding="utf-8").split("\n")
            excerpt = "\n".join(lines[ref["start_line"] - 1: ref["end_line"]])
            assert excerpt == item["text"], item["evidence_id"]
        assert hashlib.sha256(item["text"].encode()).hexdigest() == item["text_sha256"]


# --- the conflict is real and instance-bound ------------------------------

CONCEPT, FEATURE = "칼", "철"


def test_both_sides_of_the_conflict_are_present():
    kinds = {i["source_kind"] for i in fixture()["evidence_sources"]}
    assert {"doc", "code", "test"} <= kinds


def test_conflict_is_instance_bound_on_both_sides():
    """C2. A generic mapping rule on one side and an instance claim on the
    other would not be a conflict about *this* feature."""
    items = {i["evidence_id"]: i["text"] for i in fixture()["evidence_sources"]}
    assert CONCEPT in items["ev1"] and FEATURE in items["ev1"], "doc side not bound to 칼/철"
    assert FEATURE in items["ev4"], "test side not bound to 철"
    assert "structural_composition" in items["ev4"]
    assert "essential_feature" in items["ev1"]


def test_the_two_sides_actually_disagree():
    items = {i["evidence_id"]: i["text"] for i in fixture()["evidence_sources"]}
    doc_claim = "essential_feature" in items["ev1"]
    code_claim = "structural_composition" in items["ev3"]
    test_claim = "structural_composition" in items["ev4"]
    assert doc_claim and code_claim and test_claim


def test_candidate_records_the_repositorys_actual_enforced_state():
    """The recorded type must not be invented. R6b pins 철 as
    structural_composition and passes, so that is what the fixture records."""
    feature = next(f for c in fixture()["candidate_concepts"]
                   for f in c["features"] if f["feature"] == FEATURE)
    assert feature["type"] == "structural_composition"


def test_server_response_is_reproducible():
    cert = _load("h1a_cert_core", E24 / "_cert_core.py")
    observed = cert.run_and_certify(fixture()["run_pipeline_input"])
    expected = fixture()["server_response"]
    assert {k: observed[k] for k in expected} == expected


# --- no oracle, and no liveness leak into the model surface ---------------

ORACLE_TOKENS = (
    "expected_decision", "expected_type", "expected_contract_verdict",
    "semantic_class", "correct", "정답", "기대 판정", "oracle",
)


def test_fixture_contains_no_oracle_field():
    """H1a scores no correctness (D-H1a-4), so no field may name a right answer."""
    def walk(node, path="$"):
        if isinstance(node, dict):
            for key, value in node.items():
                assert key not in ORACLE_TOKENS, f"{path}.{key}"
                walk(value, f"{path}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{path}[{i}]")
    walk(fixture())


LIVENESS_TOKENS = (
    "stale", "outdated", "obsolete", "superseded", "deprecated",
    "newer", "older", "more recent", "authoritative",
    "낡", "최신", "구식", "권위", "우선",
)


def test_model_payload_carries_no_liveness_or_authority_hint():
    """The harness knows the docs predate the code. The model must not.
    Leaking it would collapse the manipulated variable."""
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = h1a_surface.build_model_payload(fixture(), manifest)
    blob = h1a_surface.canonical_json(payload)
    for token in LIVENESS_TOKENS:
        assert token not in blob, token


def test_model_payload_exposes_only_the_three_evidence_keys():
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = h1a_surface.build_model_payload(fixture(), manifest)
    assert set(payload) == set(h1a_surface.MODEL_PAYLOAD_KEYS)
    for item in payload["evidence_items"]:
        assert set(item) == set(h1a_surface.MODEL_EVIDENCE_KEYS)


def test_builder_metadata_never_reaches_the_payload():
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = h1a_surface.build_model_payload(fixture(), manifest)
    blob = h1a_surface.canonical_json(payload)
    for value in fixture()["builder_metadata"].values():
        assert value not in blob


def test_eligibility_profile_never_reaches_the_payload():
    """The refuted 'leak dilemma' -- kept as a standing check, not a memory."""
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = h1a_surface.build_model_payload(fixture(), manifest)
    blob = h1a_surface.canonical_json(payload)
    for profile in h1a_surface.ELIGIBILITY_PROFILES:
        assert profile not in blob, profile


def test_known_e24_leak_sentences_absent():
    e24_tests = _load("e24_test_surface_for_h1a", E24 / "test_surface.py")
    manifest = h1a_surface.qualify_fixture(fixture(), REPO_ROOT, run_tests=False)
    payload = h1a_surface.build_model_payload(fixture(), manifest)
    blob = h1a_surface.canonical_json(payload)
    for leak in e24_tests.KNOWN_LEAKS:
        assert leak not in blob
