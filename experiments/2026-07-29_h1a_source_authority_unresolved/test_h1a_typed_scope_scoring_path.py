"""End-to-end check that the typed-scope cohort can actually be scored.

WHY A SEPARATE FILE FROM test_h1a_score_instrument.py
That file tests the scorer's guards in isolation, each against a synthetic
spec. This one runs the WHOLE path against the REAL frozen manifest --
`cohort_prompts_typed_scope.json`, its recorded freeze proof, the real coder
and its calibration -- with only the observations synthesized and only the
outputs redirected to tmp_path.

The gap this closes is specific. Every guard had a unit test and every unit
test passed while the path as a whole could not run at all: the scorer's four
output paths were module constants pointing at the preserved 2026-08-03
cohort, so scoring the typed-scope cohort raised ScoreOverwriteRefused with
nowhere to write. Verified by reverting the fix (2026-08-18 smoke run): the
pre-fix code fails here with exactly that exception. Unit tests could not see
it because each one supplied its own spec.

The dangerous version of that discovery is the one made AFTER 40 real
observations exist, when the cheapest-looking repair is to delete the refusal
that is protecting the preserved cohort.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _coder                    # noqa: E402
import _h1a_cohort as cohort_mod  # noqa: E402
import _h1a_cohort_run as cohort_run  # noqa: E402


def _load_score():
    """`_h1a_score.py` is underscore-prefixed and not importable as a module
    name pytest collects, so load it by path -- same approach as
    test_h1a_score_instrument.py."""
    spec = importlib.util.spec_from_file_location(
        "_h1a_score_e2e", HERE / "_h1a_score.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_h1a_score_e2e"] = module
    spec.loader.exec_module(module)
    return module


score = _load_score()
TYPED = cohort_mod.TYPED_SCOPE_COHORT


def _redirected(tmp_path, **over):
    """The real typed-scope cohort with only its OUTPUTS redirected.

    `cohort_path` stays real on purpose, so `freeze_proof_path` derives to the
    real recorded proof and the binding check runs against production bytes
    rather than a fixture that could agree with a broken implementation.
    """
    base = dict(
        cohort_id=TYPED.cohort_id,
        fixture_path=TYPED.fixture_path,
        cohort_path=TYPED.cohort_path,
        raw_path=tmp_path / "raw.json",
        trials_path=tmp_path / "trials.json",
        score_path=tmp_path / "score.json",
        order_seed=TYPED.order_seed,
        trial_id_prefix=TYPED.trial_id_prefix,
        n_per_arm=TYPED.n_per_arm,
    )
    base.update(over)
    return cohort_mod.CohortSpec(**base)


def _manifest() -> dict:
    return json.loads(TYPED.cohort_path.read_text(encoding="utf-8"))


def _synthetic_raw(kind_for_arm) -> dict:
    """Observations assembled through the REAL runner, not hand-built here.

    `_h1a_cohort_run.build_raw()` is what a live run uses, and it derives the
    per-arm prompt hashes from the dispatch plan -- the bytes handed to the
    dispatcher -- rather than reading them back out of the manifest. Building
    the document by hand here would test a shape that production never
    produces, and would also make the provenance comparison a check of the
    manifest against itself (independent review 2026-08-18, finding P2).

    The observation CONTENT is arbitrary: what is under test is the
    bookkeeping around `_coder.code()`, not the coder.
    """
    plan = cohort_run.build_dispatch_plan(TYPED)
    values = _coder.selected_type_values()
    outputs = {}
    for item in plan["items"]:
        kind = kind_for_arm(item["arm"])
        if kind == "selection":
            outputs[item["trial_id"]] = {
                "decision": "select_type", "selected_type": values[0],
                "cited_evidence_ids": ["ev1"], "rationale": "synthetic",
            }
        elif kind == "deferral":
            outputs[item["trial_id"]] = {
                "decision": "defer", "selected_type": None,
                "cited_evidence_ids": ["ev1", "ev3"], "rationale": "synthetic",
            }
        else:
            outputs[item["trial_id"]] = None
    return cohort_run.build_raw(
        plan, outputs,
        dispatch_script_sha256="0" * 64,   # no dispatch happened in a test
        run_date="2026-08-18",
        notes="synthetic observations written by the test suite",
    )


def test_the_typed_scope_cohort_can_be_scored_end_to_end(tmp_path) -> None:
    spec = _redirected(tmp_path)
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(
            lambda arm: "deferral" if arm == "PROHIBITION_KEPT" else "selection"
        )), encoding="utf-8",
    )

    assert score.main(spec) == 0
    summary = json.loads(spec.score_path.read_text(encoding="utf-8"))

    assert summary["cohort_id"] == "h1a-typed-scope-20260817"
    assert summary["trial_id_prefix"] == "H1AT"
    assert summary["n_expected"] == 40
    assert summary["n_recorded"] == 40
    assert summary["transport_failures"] == []
    assert len(summary["complete_replicates"]) == 20
    assert summary["incomplete_replicates"] == []

    # Non-vacuous: the bookkeeping must have discriminated the two arms. If
    # this only checked "did not crash", a scorer that categorised everything
    # as invalid would pass.
    assert summary["per_arm"]["PROHIBITION_KEPT"]["deferral"] == 20
    assert summary["per_arm"]["PROHIBITION_KEPT"]["selection"] == 0
    assert summary["per_arm"]["PROHIBITION_REMOVED"]["selection"] == 20
    assert summary["per_arm"]["PROHIBITION_REMOVED"]["deferral"] == 0
    assert summary["stage_a_pass"] is True


def test_the_scored_output_carries_the_licensed_path_rows(tmp_path) -> None:
    """PREREGISTRATION_TYPED_SCOPE_COHORT.md §7 requires the item-level values
    with the results. Checked on the real score file the real path produces,
    not on the proof artifact in isolation -- the failure mode was that the
    rows existed nowhere at all because `build_cohort()` discarded them."""
    spec = _redirected(tmp_path)
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(lambda arm: "selection")), encoding="utf-8")
    score.main(spec)
    summary = json.loads(spec.score_path.read_text(encoding="utf-8"))

    rows = summary["licensed_source_evaluation_path"]
    assert set(rows) == set(cohort_mod.contract.ARMS)
    # The contrast the freeze rests on: exactly one arm's path is open.
    assert rows["PROHIBITION_REMOVED"]["licensed_path"] is True
    assert rows["PROHIBITION_KEPT"]["licensed_path"] is False
    for row in rows.values():
        for field in ("source_attributes_visible", "source_meta_allowed",
                      "domain_ban_subsumes_source_meta", "hard_defer_mapping",
                      "residual_prohibition"):
            assert field in row, f"§7 needs item-level values; {field} missing"

    assert summary["freeze_proof_manifest_sha256"] == hashlib.sha256(
        TYPED.cohort_path.read_bytes()).hexdigest()


def test_transport_failures_do_not_become_outcomes(tmp_path) -> None:
    """P4: a null output is re-run, not recorded. Exercised on the real
    manifest because this is the branch a live 40-trial run is most likely to
    hit, and it has never executed on this cohort."""
    spec = _redirected(tmp_path)
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(
            lambda arm: "missing" if arm == "PROHIBITION_KEPT" else "selection"
        )), encoding="utf-8",
    )
    result = score.score(spec)

    assert len(result["transport_failures"]) == 20
    assert result["complete_replicates"] == []
    assert result["stage_a_pass"] is False, (
        "a run with 20 transport failures must not pass the Stage A gate"
    )
    # Nothing entered the comparison, so no arm shows a tally.
    for arm_counts in result["per_arm"].values():
        assert sum(arm_counts.values()) == 0


def test_scoring_the_typed_scope_cohort_never_touches_the_preserved_one(
    tmp_path,
) -> None:
    """The whole reason the output paths moved onto CohortSpec. Byte-compared,
    not argued: the preserved cohort's four artifacts must be identical after
    a full typed-scope scoring run."""
    preserved = [cohort_mod.ORIGINAL_COHORT.cohort_path,
                 cohort_mod.ORIGINAL_COHORT.raw_path,
                 cohort_mod.ORIGINAL_COHORT.trials_path,
                 cohort_mod.ORIGINAL_COHORT.score_path]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in preserved if p.exists()}
    assert len(before) == 4, f"precondition: all four must exist, got {before}"

    # Snapshot the typed-scope cohort's own outputs too. `None` for absent is
    # deliberate: "absent before and absent after" is as much a pass as
    # "unchanged", and this test must work both before and after the cohort
    # has been executed.
    real_before = {
        path.name: (hashlib.sha256(path.read_bytes()).hexdigest()
                    if path.exists() else None)
        for path in (TYPED.trials_path, TYPED.score_path, TYPED.raw_path)
    }

    spec = _redirected(tmp_path)
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(lambda arm: "selection")), encoding="utf-8")
    score.main(spec)

    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in preserved if p.exists()}
    assert after == before

    # And this tmp_path-redirected run must not have touched the typed-scope
    # cohort's REAL outputs either.
    #
    # 2026-08-22: this block used to assert those files do not exist, which
    # conflated "this test leaked nothing" with "the cohort has never run". The
    # second became false the moment the 40 trials were scored, and the test
    # failed for a reason that was not a defect. Its own P1 mistake: a true
    # proposition that was not the necessary one.
    #
    # The necessary proposition is that this test changed nothing, so it is
    # now measured that way -- byte-state before against byte-state after,
    # which detects a leaked path whether or not the real files exist.
    real_after = {
        path.name: (hashlib.sha256(path.read_bytes()).hexdigest()
                    if path.exists() else None)
        for path in (TYPED.trials_path, TYPED.score_path, TYPED.raw_path)
    }
    assert real_after == real_before, (
        f"a tmp_path-redirected run changed the cohort's real outputs, so an "
        f"output path is still hardwired: "
        f"{ {k for k in real_after if real_before[k] != real_after[k]} }"
    )


def test_a_run_whose_manifest_lacks_a_freeze_proof_cannot_be_scored(
    tmp_path,
) -> None:
    """§7's recording requirement, enforced on the path rather than trusted.
    A manifest copied without its proof sidecar must not score."""
    copied = tmp_path / "cohort_copy.json"
    copied.write_bytes(TYPED.cohort_path.read_bytes())
    spec = _redirected(tmp_path, cohort_path=copied)
    # A fully valid raw file, so the freeze-proof guard is unambiguously what
    # fires rather than the shape or provenance one.
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(lambda arm: "selection")), encoding="utf-8")

    assert not spec.freeze_proof_path.exists()
    with pytest.raises(score.FreezeProofMissing):
        score.score(spec)


# --- 2026-08-18: the confirmatory cohort had no provenance contract at all,
# while the capability diagnostics had had one since 2026-08-16 ---------------

def test_flat_pre_provenance_raw_files_are_refused(tmp_path) -> None:
    """Recall. The shape the preserved 2026-08-03 cohort's `trials_raw.json`
    is in: 40 bare trial ids, nothing about transport or model. Accepting it
    would mean the confirmatory cohort can be scored with its transport
    unproven -- the defect that forced the QF-SELECT re-run."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    spec.raw_path.write_text(json.dumps(doc["outputs"]), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing, match="flat"):
        score.score(spec)


def test_outputs_produced_without_schema_forcing_are_refused(tmp_path) -> None:
    """The exact 2026-08-15 QF-SELECT failure, one layer over. The outputs are
    valid and the prompt hashes are right; only the transport is wrong. If
    this passed, prompt byte-identity would again be mistaken for proof that
    the subject was identified."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    doc["provenance"]["transport"] = "plain_text_prompt"
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing, match="transport"):
        score.score(spec)


def test_outputs_produced_on_another_model_are_refused(tmp_path) -> None:
    """The other half of the same 2026-08-15 failure: the agent definition
    pins no model, so an unrecorded run inherits the dispatching session's."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    doc["provenance"]["trial_model"] = "claude-sonnet-5"
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing, match="trial_model"):
        score.score(spec)


def test_a_prompt_hash_matching_only_one_arm_is_refused(tmp_path) -> None:
    """Per-arm hashes, not one. The cohort's entire design is that the arms
    differ by exactly the Q1 clause, so a single hash could match KEPT and say
    nothing about REMOVED -- and the arm it says nothing about is half the
    comparison."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    by_arm = doc["provenance"]["rendered_prompt_sha256_by_arm"]
    by_arm["PROHIBITION_REMOVED"] = by_arm["PROHIBITION_KEPT"]
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing,
                       match="rendered_prompt_sha256_by_arm"):
        score.score(spec)


def test_the_provenance_guard_accepts_a_correct_run(tmp_path) -> None:
    """Precision. A guard that raised unconditionally would pass all four
    recall tests above, and would also make the cohort unscoreable."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    result = score.score(spec)
    assert result["trial_provenance"]["transport"] == (
        "schema_forced_structured_output")
    assert result["trial_provenance"]["trial_model"] == "claude-opus-5"
    assert result["n_recorded"] == 40


# ==========================================================================
# Independent adversarial review, 2026-08-18 (four ground-truth axes, haiku).
# Each test below is one surviving finding, pinned so it cannot come back.
# ==========================================================================

def test_the_frozen_prompts_reproduce_from_the_renderer() -> None:
    """Findings P2/P3: nothing verified that the frozen `rendered_prompts` are
    what the renderer actually produces.

    The reviewers were right that no test pinned it, and wrong that it was
    broken -- measured 2026-08-18, both arms reproduce byte-identically. This
    test is the difference between those two facts: it makes the agreement
    checked rather than incidental.

    IF THIS FAILS, the frozen cohort no longer corresponds to the current
    template. That is information, not a nuisance: the trials the model saw
    are the frozen bytes, so a divergence means the template moved after the
    freeze and any claim resting on "the arms differ only by the Q1 clause"
    must be re-derived. Record the divergence; do not delete the test.
    """
    import _h1a_contract as contract
    import _h1a_surface as surface

    manifest = _manifest()
    fixture = json.loads(TYPED.fixture_path.read_text(encoding="utf-8"))
    qualification = surface.qualify_fixture(
        fixture, cohort_mod.REPO_ROOT, run_tests=False)
    payload = surface.build_model_payload(fixture, qualification)
    template = contract.load_h1a_native_template()

    for arm in contract.ARMS:
        fresh = surface.render_prompt(contract.render_arm(template, arm), payload)
        frozen = manifest["rendered_prompts"][arm]
        assert fresh == frozen, (
            f"{arm}: the frozen prompt is not what the renderer produces now. "
            f"The trials ran on the frozen bytes, so this divergence must be "
            f"recorded, not papered over."
        )


def test_outputs_for_trial_ids_outside_the_freeze_are_refused(tmp_path) -> None:
    """Reviewer D's surviving gap: nothing made the `unexpected` check raise.

    A trial id that is not in the freeze is an observation of something the
    preregistration never specified. Scoring it would put a number in the
    results whose provenance is a mystery.
    """
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    doc["outputs"]["H1AT-PROHIBITION_KEPT-99"] = {
        "decision": "defer", "selected_type": None,
        "cited_evidence_ids": [], "rationale": "not in the freeze",
    }
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(ValueError, match="not in the freeze"):
        score.score(spec)


def test_an_empty_manifest_does_not_satisfy_the_identity_check(tmp_path) -> None:
    """Reviewer A finding 1. The prefix check is a comprehension over
    `trials`, so an empty list made it vacuously true -- a guard that goes
    silent while still looking present, which is this folder's signature
    defect."""
    empty = tmp_path / "empty.json"
    empty.write_text(json.dumps({"trials": []}), encoding="utf-8")
    spec = _redirected(tmp_path, cohort_path=empty)

    with pytest.raises(score.CohortIdentityMismatch, match="no trials"):
        score.score(spec)


def test_an_empty_trial_id_prefix_is_refused(tmp_path) -> None:
    """Reviewer A finding 4. An empty prefix reduces the check to 'starts with
    a hyphen', which identifies nothing."""
    spec = _redirected(tmp_path, trial_id_prefix="")
    with pytest.raises(score.CohortIdentityMismatch, match="empty"):
        score.score(spec)


def test_a_non_mapping_provenance_is_refused_cleanly(tmp_path) -> None:
    """Reviewer A finding 2. A non-empty string passed the truthiness check
    and then died on `.get` with an AttributeError -- which reads as a broken
    checker rather than a rejected input, and an AttributeError is exactly the
    kind of failure someone 'fixes' by loosening the guard."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    doc["provenance"] = "schema_forced_structured_output"
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing, match="not a mapping"):
        score.score(spec)


def test_a_non_mapping_outputs_block_is_refused_cleanly(tmp_path) -> None:
    """Reviewer A finding 6. A list reached the `unexpected` check and failed
    with a message about trial ids, misdescribing the problem."""
    spec = _redirected(tmp_path)
    doc = _synthetic_raw(lambda arm: "selection")
    doc["outputs"] = ["H1AT-PROHIBITION_KEPT-01"]
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")

    with pytest.raises(score.RawProvenanceMissing, match="not a mapping"):
        score.score(spec)


def test_observations_are_bound_to_the_manifest_bytes(tmp_path) -> None:
    """Findings P1/P4/P5: everything in provenance was the runner's own claim.

    This binding is the one element that is not: the raw file is written after
    the freeze, by a separate call, from the dispatch plan -- so it cannot
    agree with a manifest hash it never saw. Recall on both halves."""
    spec = _redirected(tmp_path)

    doc = _synthetic_raw(lambda arm: "selection")
    doc["cohort_manifest_sha256"] = "0" * 64
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(score.RawProvenanceMissing, match="manifest changed"):
        score.score(spec)

    doc = _synthetic_raw(lambda arm: "selection")
    del doc["cohort_manifest_sha256"]
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(score.RawProvenanceMissing, match="no `cohort_manifest_sha256`"):
        score.score(spec)

    doc = _synthetic_raw(lambda arm: "selection")
    doc["cohort_id"] = "h1a-original-20260803"
    spec.raw_path.write_text(json.dumps(doc), encoding="utf-8")
    with pytest.raises(score.RawProvenanceMissing, match="must not be filed"):
        score.score(spec)


def test_the_score_file_says_which_manifest_and_surfaces_it_describes(
    tmp_path,
) -> None:
    """Finding P5. §7 asks that the basis of the contrast be reconstructable
    afterwards. A score file that does not name the manifest or the surfaces
    requires the reader to be handed the right manifest and trust it."""
    spec = _redirected(tmp_path)
    spec.raw_path.write_text(
        json.dumps(_synthetic_raw(lambda arm: "selection")), encoding="utf-8")
    score.main(spec)
    summary = json.loads(spec.score_path.read_text(encoding="utf-8"))

    assert summary["cohort_manifest_sha256"] == hashlib.sha256(
        TYPED.cohort_path.read_bytes()).hexdigest()
    by_arm = summary["rendered_prompt_sha256_by_arm"]
    assert set(by_arm) == set(cohort_mod.contract.ARMS)
    assert len(set(by_arm.values())) == 2, (
        "the two arms must have different surfaces; identical hashes would "
        "mean the treatment was never applied"
    )
