"""H1a capability-diagnostic execution/persistence -- D-H1a-14/15.

Bridges `_h1a_qualification.py`'s pure deterministic scorer (fixture-free,
testable with synthetic outputs alone) to the real QF-SELECT material:
renders the model-facing prompt through the SAME pipeline the main cohort
uses (`_h1a_surface.qualify_fixture` -> `build_model_payload` ->
`_h1a_contract.render_qualification_surface` -> `render_prompt`), then
persists trial outputs and the diagnostics record with an F9-style overwrite
guard.

NOT the confirmatory cohort, and NOT a gate. Under D-H1a-14/15 these controls
are non-blocking capability diagnostics: nothing here grants or withholds
permission to run the cohort. This module accordingly does not call
`_h1a_cohort.build_cohort()` or `policy.assert_freezable()` -- freeze belongs
to the identification contract, and those are gated on
`INDEPENDENT_SEMANTIC_REVIEW_PASSED`, which diagnostics must be able to run
before.

SURFACE (Q14.3)
---------------
Qualification renders on `QUALIFICATION_COMMON`, which belongs to no
treatment arm. Its bytes are the common policy-filled template without Q1's
liveness clause -- currently identical to what
`render_arm(..., "PROHIBITION_REMOVED")` produces, which is what the ruling
froze it as. The recorded 5 QF-SELECT trials predate the name: they ran under
the `PROHIBITION_REMOVED` label on those same bytes, so the ruling permits
reclassifying rather than re-running them. That permission is CONDITIONAL on
byte identity, so it is machine-checked here
(`_assert_recorded_trials_match_the_qualification_surface`) instead of being
asserted in prose.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import _h1a_cohort as cohort_mod
import _h1a_contract as contract
import _h1a_qualification as qual
import _h1a_surface as surface

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]  # concept-gate-h1-wt/

# D-H1a-14/15 Q14.3: qualification belongs to NO treatment arm.
QUALIFICATION_SURFACE = contract.QUALIFICATION_SURFACE

# The label the 5 recorded QF-SELECT trials were run under, before the ruling
# named the surface. Kept so the reclassification is auditable.
SUPERSEDED_SURFACE_LABEL = "PROHIBITION_REMOVED"

# The rendered-prompt hash those 5 trials were actually served. The ruling
# permits reusing them INSTEAD OF re-running only while the new
# QUALIFICATION_COMMON surface reproduces these exact bytes, so this is
# machine-checked (`_assert_recorded_trials_match_the_qualification_surface`)
# rather than asserted in prose.
TRIALS_RENDERED_PROMPT_SHA256 = (
    "fd793fc70ee1b41e799e385e8548be35aec6e461747ba1fb6f46bddd3193dbaf"
)

# --- trial-subject contract, REUSED from the confirmatory cohort ----------
# Not copied. A capability diagnostic that runs a different subject, model or
# transport than the cohort it diagnoses measures nothing about that cohort,
# so these must move together by construction. (2026-08-16: the first
# QF-SELECT run predated this and did NOT match -- see OPERATIONS_LOG sec 11.)
TRIAL_MODEL = cohort_mod.MODEL
TRIAL_PARAMETERS = cohort_mod.PARAMETERS
CONTEXT_ISOLATION = "workflow_cold_subagent"
TRANSPORT = "schema_forced_structured_output"

SCHEMA_PATH = cohort_mod.SCHEMA_PATH

QF_SELECT_FIXTURE_PATH = HERE / "fixture_qf_select.json"
# QF-DEFER has no fixture: exhaustive eligibility-aware enumeration found no
# repo-grounded material (Q14, correspondence/DESIGN_REQUEST_H1a_
# qualification_defer_material.md sec 3). Recorded as material_unavailable,
# not fabricated -- see _h1a_qualification.py's module docstring.
QF_DEFER_FIXTURE_PATH = None

MANIFEST_PATH = HERE / "h1a_qualification_manifest.json"
RAW_PATH = HERE / "h1a_qualification_raw.json"
SCORE_PATH = HERE / "h1a_qualification_score.json"


# Ponytail rung 2 (codebase reuse): `_h1a_cohort._git_head` is the same call
# against the same REPO_ROOT. A byte-identical copy lived here until the
# 2026-08-16 review flagged it (finding D-7).
_git_head = cohort_mod._git_head


def render_control(fixture_path: Path) -> dict:
    """Render one control's model-facing prompt on the QUALIFICATION_COMMON
    surface, through the same validated pipeline `_h1a_cohort.build_cohort()`
    uses for the confirmatory fixture (fixture qualification -> payload ->
    no-anchor guard -> template render).

    The surface is treatment-invariant by contract (D-H1a-14/15 Q14.3), and
    that contract is checked here on every render rather than trusted.""" 
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    qualification_manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=True)
    if qualification_manifest["status"] != "passed":
        raise surface.SurfaceError(f"fixture qualification failed: {qualification_manifest}")

    model_payload = surface.build_model_payload(fixture, qualification_manifest)
    surface.assert_no_model_facing_type_anchor(model_payload)

    template = contract.load_h1a_native_template()
    contract.assert_qualification_surface_is_treatment_invariant(template)
    qualification_template = contract.render_qualification_surface(template)
    rendered_prompt = surface.render_prompt(qualification_template, model_payload)

    return {
        "fixture": fixture,
        "qualification_manifest": qualification_manifest,
        "model_payload": model_payload,
        "rendered_prompt": rendered_prompt,
    }


def decision_schema() -> dict:
    """The schema the transport forces. Same source the cohort uses."""
    doc = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return doc["variants"]["h1a_response"]["schema"]


def protocol_block() -> dict:
    """What the confirmatory cohort pins in `cohort_prompts.json["protocol"]`,
    restricted to the fields that describe the trial subject and transport.

    Recorded because the 2026-08-15 QF-SELECT run recorded none of it, so
    nothing in that artifact could reveal that it had been dispatched on a
    different transport (no schema forcing) and, by inheritance, a different
    model than `trial_model`. An unrecorded mismatch is not detectable, which
    is why this is pinned rather than assumed.
    """
    return {
        "experiment_id": "H1a",
        "context_isolation": CONTEXT_ISOLATION,
        "tool_access": TRIAL_PARAMETERS["tool_access"],
        "transport": TRANSPORT,
        "trial_model": TRIAL_MODEL,
        "trials_per_control": qual.TRIALS_PER_CONTROL,
    }


def build_manifest() -> dict:
    """The qualification gate's own pre-trial manifest: what each control's
    trial subjects were actually shown, pinned before results are scored --
    same rationale as `cohort_prompts.json` for the confirmatory cohort."""
    select = render_control(QF_SELECT_FIXTURE_PATH)
    _assert_trial_subject_matches_the_confirmatory_cohort()
    manifest = {
        "record_class": "h1a_qualification_manifest",
        "builder_commit": _git_head(),
        "ruling": "D-H1a-14/15",
        "surface": {
            "name": QUALIFICATION_SURFACE,
            "treatment_arm": None,
            "policy_role": "treatment_invariant",
            "byte_source": "COMMON_WITHOUT_Q1",
            "old_label": SUPERSEDED_SURFACE_LABEL,
            "reclassified_as": QUALIFICATION_SURFACE,
            "byte_identity_verified": True,
        },
        "controls_are_freeze_prerequisites": False,
        "trials_per_control": qual.TRIALS_PER_CONTROL,
        "protocol": protocol_block(),
        # Reused wholesale from the cohort harness: hashes the agent
        # definition AND the system-prompt body separately, and asserts
        # `tools: []` (P3's no_tools claim, which the harness's own agent
        # listing renders as "All tools" -- the definition file is the only
        # place it can be checked).
        "trial_subject_surface": cohort_mod._trial_subject_surface(),
        "decision_schema_sha256": surface.sha256_of(decision_schema()),
        qual.QF_SELECT: {
            "fixture_path": str(QF_SELECT_FIXTURE_PATH.relative_to(REPO_ROOT)),
            "fixture_sha256": surface.sha256_of(select["fixture"]),
            "model_payload_sha256": surface.sha256_of(select["model_payload"]),
            "rendered_prompt_sha256": surface.sha256_of(select["rendered_prompt"]),
        },
        qual.QF_DEFER: {
            "status": qual.MATERIAL_UNAVAILABLE,
            "reason": (
                "No repo-grounded, same-source_kind conflicting-type material "
                "exists for QF-DEFER (Q14, exhaustive enumeration). D-H1a-14/15 "
                "Q14.1 additionally forbids manufacturing one by reusing the "
                "confirmatory 칼/철 fixture "
                "(confirmatory_fixture_reused_as_capability_control: false). "
                "Recorded as unknown, not as failure (Q14.2); registered as "
                "limitation L9, and it does not block the cohort (Q15=G)."
            ),
        },
    }
    return manifest


class ManifestDriftError(Exception):
    """The live-rendered qualification manifest no longer matches the
    recorded one -- never silently proceed on drift (same discipline as
    `_h1a_contract.ContractDriftError`)."""


class QualificationScoreOverwriteRefused(Exception):
    """main() would destroy a previously recorded qualification score.

    Same fail-closed shape as `_h1a_score.py::ScoreOverwriteRefused` (F9,
    independent review 20260806 axis c) -- a qualification re-run must not
    silently overwrite a prior gate result."""


def _assert_recorded_trials_match_the_qualification_surface(manifest: dict) -> None:
    """The recorded QF-SELECT trials may stand in for QUALIFICATION_COMMON
    trials only while the surface reproduces the exact bytes they were served.

    D-H1a-14/15 Q14.3 made reuse conditional:

        may_reuse_existing_QF_SELECT_trials:
          only_if_byte_identical_to_old_removed_surface: true

    and stated the alternative explicitly -- "한 바이트라도 다르면 기존
    5/5는 historical diagnostic으로 보존하고 새 surface에서 다시 실행해야
    한다." A condition whose failure changes what must be re-run cannot be
    left to a reader to notice.
    """
    rendered_sha = manifest[qual.QF_SELECT]["rendered_prompt_sha256"]
    if rendered_sha != TRIALS_RENDERED_PROMPT_SHA256:
        raise ManifestDriftError(
            f"QUALIFICATION_COMMON now renders {rendered_sha!r}, but the "
            f"recorded QF-SELECT trials were served "
            f"{TRIALS_RENDERED_PROMPT_SHA256!r}. D-H1a-14/15 Q14.3 permits "
            f"reusing those trials ONLY while the bytes are identical. They "
            f"are now historical diagnostics: preserve them and re-run the "
            f"controls on the new surface. Do not delete this check to "
            f"proceed."
        )


PROVENANCE_KEYS = (
    "transport", "trial_model", "tool_access", "context_isolation",
    "trial_subject_definition_sha256", "decision_schema_sha256",
    "rendered_prompt_sha256",
)


def _assert_trial_subject_matches_the_confirmatory_cohort() -> None:
    """The diagnostic's subject must be the COHORT's subject, byte-for-byte.

    `_trial_subject_surface()` hashes the agent definition as it is on disk
    NOW. Comparing a freshly-computed hash against a manifest built from the
    same fresh computation compares a value to itself: if the definition
    drifts, both move together and the check stays silent. That is the F10
    shape -- a true proposition asserted about the wrong object.

    The only external anchor is the frozen cohort manifest, which recorded
    the definition hash at the time the 40 confirmatory trials ran. That is
    what "the same subject as the cohort" has to mean, so it is what is
    compared here.
    """
    frozen = json.loads(cohort_mod.COHORT_PATH.read_text(encoding="utf-8"))
    cohort_subject = frozen["trial_subject_surface"]
    live_subject = cohort_mod._trial_subject_surface()

    for field in ("trial_subject", "definition_sha256", "system_prompt_sha256"):
        if live_subject[field] != cohort_subject[field]:
            raise ManifestDriftError(
                f"trial subject {field} differs from the frozen confirmatory "
                f"cohort's: live={live_subject[field]!r} "
                f"cohort={cohort_subject[field]!r}. A capability diagnostic "
                f"run against a different subject than the cohort says "
                f"nothing about that cohort. If the definition was changed "
                f"deliberately, the confirmatory cohort's own subject record "
                f"is now stale too -- that is a freeze-integrity question, "
                f"not something to resolve by editing this check."
            )


def _assert_raw_provenance_matches_the_manifest(raw: dict, manifest: dict) -> None:
    """Trial outputs may only be scored against the surface/subject/transport
    they were actually produced under.

    The 2026-08-15 QF-SELECT run is why this exists. Its outputs were valid
    and its rendered prompt was byte-correct, but it was dispatched WITHOUT
    schema forcing and -- the agent definition pins no model, so the subject
    inherits the dispatching session's -- not necessarily on `trial_model`.
    Neither fact was recoverable from the artifact, because the artifact
    recorded neither. Byte-identity of the prompt was verified and was not
    sufficient: a capability diagnostic identifies a SUBJECT under a
    TRANSPORT, not just a prompt.

    So a raw file must now declare its own provenance and it must match the
    manifest. A file with no `provenance` block is refused rather than
    assumed compatible -- "unrecorded" is not "fine".
    """
    provenance = raw.get("provenance")
    if not provenance:
        raise ManifestDriftError(
            "raw trial outputs carry no `provenance` block, so the transport, "
            "trial model and trial-subject surface they were produced under "
            "cannot be established. Outputs recorded before 2026-08-16 are in "
            "this state (see OPERATIONS_LOG sec 11): preserve them as "
            "historical diagnostics and re-run the controls through the "
            "cohort's own transport. Do not delete this check to proceed."
        )

    expected = {
        "transport": manifest["protocol"]["transport"],
        "trial_model": manifest["protocol"]["trial_model"],
        "tool_access": manifest["protocol"]["tool_access"],
        "context_isolation": manifest["protocol"]["context_isolation"],
        "trial_subject_definition_sha256":
            manifest["trial_subject_surface"]["definition_sha256"],
        "decision_schema_sha256": manifest["decision_schema_sha256"],
        "rendered_prompt_sha256":
            manifest[qual.QF_SELECT]["rendered_prompt_sha256"],
    }
    mismatched = {
        key: (provenance.get(key), expected[key])
        for key in PROVENANCE_KEYS
        if provenance.get(key) != expected[key]
    }
    if mismatched:
        raise ManifestDriftError(
            "raw trial outputs were produced under a different subject or "
            "transport than this manifest describes; scoring them here would "
            "attribute one subject's behavior to another. Mismatches "
            "(recorded -> expected): "
            + ", ".join(f"{k}: {got!r} -> {want!r}" for k, (got, want) in sorted(mismatched.items()))
        )


def _assert_manifest_has_not_drifted(recorded: dict, fresh: dict) -> None:
    """The recorded manifest must still describe what the pipeline produces.

    Named `_assert_*` so `test_guard_negative_coverage.py`'s AST scan sees it:
    that gate only collects guards matching `GUARD_PREFIXES`, so a guard
    buried inside `_freeze_or_check_manifest()`/`main()` sat outside the
    mechanism this repo built precisely because the written "remember to add
    a negative test" discipline failed 7/7 times (2026-08-16 review, D-6).
    """
    # Compare every field that describes what the subject was shown and who
    # the subject was -- not the prompt hash alone. A manifest written before
    # `protocol`/`trial_subject_surface` existed has an UNCHANGED prompt hash,
    # so a hash-only check waves it through and `main()` then reads keys that
    # are not there. Structural staleness is drift.
    for key in ("protocol", "trial_subject_surface", "decision_schema_sha256"):
        if key not in recorded:
            raise ManifestDriftError(
                f"{MANIFEST_PATH.name} predates the {key!r} field and cannot "
                f"establish which subject or transport the trials ran under. "
                f"Delete it and re-freeze from the current pipeline; if trial "
                f"outputs were produced against it, they are historical "
                f"diagnostics (see OPERATIONS_LOG sec 11)."
            )
        if recorded[key] != fresh[key]:
            raise ManifestDriftError(
                f"{MANIFEST_PATH.name}: recorded {key!r} no longer matches "
                f"what the pipeline produces now. recorded={recorded[key]!r} "
                f"fresh={fresh[key]!r}. Refusing to score against a drifted "
                f"manifest."
            )

    recorded_sha = recorded[qual.QF_SELECT]["rendered_prompt_sha256"]
    fresh_sha = fresh[qual.QF_SELECT]["rendered_prompt_sha256"]
    if recorded_sha != fresh_sha:
        raise ManifestDriftError(
            f"{MANIFEST_PATH.name}: recorded QF-SELECT rendered_prompt_sha256 "
            f"{recorded_sha!r} no longer matches what the fixture/"
            f"template/policy pipeline produces now ({fresh_sha!r}). "
            f"The prompt trial subjects actually saw may differ from what "
            f"this manifest claims. Refusing to score against a drifted "
            f"manifest."
        )


def _assert_score_path_is_free() -> None:
    """Refuse to destroy a previously recorded qualification score.

    Same fail-closed shape as `_h1a_score.py::ScoreOverwriteRefused` (F9).
    Named `_assert_*` for the same reason as the function above.
    """
    if SCORE_PATH.exists():
        raise QualificationScoreOverwriteRefused(
            f"{SCORE_PATH.name} already exists. Re-running the qualification "
            f"scorer would overwrite a prior gate result irreversibly. Delete "
            f"or move it deliberately first if a re-score is actually intended."
        )


def _freeze_or_check_manifest() -> dict:
    fresh = build_manifest()
    _assert_recorded_trials_match_the_qualification_surface(fresh)
    if not MANIFEST_PATH.exists():
        MANIFEST_PATH.write_text(
            json.dumps(fresh, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return fresh
    recorded = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    _assert_manifest_has_not_drifted(recorded, fresh)
    return recorded


def load_raw() -> dict:
    return json.loads(RAW_PATH.read_text(encoding="utf-8"))


def main() -> int:
    manifest = _freeze_or_check_manifest()
    raw = load_raw()

    _assert_raw_provenance_matches_the_manifest(raw, manifest)

    select_outputs = raw[qual.QF_SELECT]
    defer_outputs = raw.get(qual.QF_DEFER)

    result = qual.score_qualification(select_outputs=select_outputs, defer_outputs=defer_outputs)
    # The score record must be self-describing: who the subject was, under
    # what transport, on which surface. The 2026-08-15 record carried none of
    # this and so could not reveal its own subject/transport mismatch.
    result["manifest"] = {
        "builder_commit": manifest["builder_commit"],
        "protocol": manifest["protocol"],
        "trial_subject_surface": manifest["trial_subject_surface"],
        "decision_schema_sha256": manifest["decision_schema_sha256"],
        "surface": manifest["surface"],
        qual.QF_SELECT: manifest[qual.QF_SELECT],
    }
    result["raw_provenance"] = raw["provenance"]

    _assert_score_path_is_free()
    SCORE_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
