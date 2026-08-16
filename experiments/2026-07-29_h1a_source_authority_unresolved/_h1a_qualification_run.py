"""H1a qualification gate execution/persistence -- D-H1a-13 Q13.3.

Bridges `_h1a_qualification.py`'s pure deterministic scorer (fixture-free,
testable with synthetic outputs alone) to the real QF-SELECT/QF-DEFER
material: renders the model-facing prompt from a fixture through the SAME
pipeline the main cohort uses (`_h1a_surface.qualify_fixture` ->
`build_model_payload` -> `_h1a_contract.render_arm` -> `render_prompt`), then
persists trial outputs and the score with an F9-style overwrite guard.

NOT the confirmatory cohort. Qualification is `confirmatory_sample: false`,
`pooled_with_main_cohort: false` (D-H1a-13 sec 6), so this module does not
call `_h1a_cohort.build_cohort()` or `policy.assert_freezable()` -- those
freeze the 40-trial main manifest and are gated on
`INDEPENDENT_SEMANTIC_REVIEW_PASSED`, which would make the qualification
gate unable to serve its own stated purpose (a PRE-freeze diagnostic that
must be able to run before that flag is set).

Arm choice for qualification packets (operational choice, NOT litigated by
D-H1a-13): `PROHIBITION_REMOVED`, the baseline surface with no inserted
liveness clause. D-H1a-13 sec 6 specifies "trials_per_control: 5" -- one run
per control, not one run per arm -- and does not say which arm's surface to
render qualification packets under. QF-SELECT/QF-DEFER fixtures carry no
source-liveness conflict for that clause to act on (see each fixture's
`builder_metadata`), so the choice should not affect measured behavior; it
is recorded here for transparency and reproducibility, not as a new
external design ruling (contrast with the D-H1a-1..13 ruling channel; see
`PREREGISTRATION_TYPED_SCOPE_COHORT.md` sec 5c for that distinction as
applied to the 2026-08-15 QF-DEFER amendment).
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

ARM_FOR_QUALIFICATION = "PROHIBITION_REMOVED"

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


def render_control(fixture_path: Path, arm: str = ARM_FOR_QUALIFICATION) -> dict:
    """Render one qualification control's model-facing prompt from its
    fixture, through the same validated pipeline `_h1a_cohort.build_cohort()`
    uses for the confirmatory fixture (fixture qualification -> payload ->
    no-anchor guard -> template render)."""
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    qualification_manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=True)
    if qualification_manifest["status"] != "passed":
        raise surface.SurfaceError(f"fixture qualification failed: {qualification_manifest}")

    model_payload = surface.build_model_payload(fixture, qualification_manifest)
    surface.assert_no_model_facing_type_anchor(model_payload)

    template = contract.load_h1a_native_template()
    arm_template = contract.render_arm(template, arm)
    rendered_prompt = surface.render_prompt(arm_template, model_payload)

    return {
        "fixture": fixture,
        "qualification_manifest": qualification_manifest,
        "model_payload": model_payload,
        "rendered_prompt": rendered_prompt,
    }


def build_manifest() -> dict:
    """The qualification gate's own pre-trial manifest: what each control's
    trial subjects were actually shown, pinned before results are scored --
    same rationale as `cohort_prompts.json` for the confirmatory cohort."""
    select = render_control(QF_SELECT_FIXTURE_PATH)
    manifest = {
        "record_class": "h1a_qualification_manifest",
        "builder_commit": _git_head(),
        "arm_for_qualification": ARM_FOR_QUALIFICATION,
        "trials_per_control": qual.TRIALS_PER_CONTROL,
        qual.QF_SELECT: {
            "fixture_path": str(QF_SELECT_FIXTURE_PATH.relative_to(REPO_ROOT)),
            "fixture_sha256": surface.sha256_of(select["fixture"]),
            "model_payload_sha256": surface.sha256_of(select["model_payload"]),
            "rendered_prompt_sha256": surface.sha256_of(select["rendered_prompt"]),
        },
        qual.QF_DEFER: {
            "status": qual.DEFER_MATERIAL_UNAVAILABLE,
            "reason": (
                "No repo-grounded, same-source_kind conflicting-type material "
                "exists for QF-DEFER (Q14, exhaustive enumeration). See "
                "correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md "
                "sec 3 and PREREGISTRATION_TYPED_SCOPE_COHORT.md sec 5c/5e (L9)."
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


def _assert_manifest_has_not_drifted(recorded: dict, fresh: dict) -> None:
    """The recorded manifest must still describe what the pipeline produces.

    Named `_assert_*` so `test_guard_negative_coverage.py`'s AST scan sees it:
    that gate only collects guards matching `GUARD_PREFIXES`, so a guard
    buried inside `_freeze_or_check_manifest()`/`main()` sat outside the
    mechanism this repo built precisely because the written "remember to add
    a negative test" discipline failed 7/7 times (2026-08-16 review, D-6).
    """
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

    select_outputs = raw[qual.QF_SELECT]
    defer_outputs = raw.get(qual.QF_DEFER)

    result = qual.score_qualification(select_outputs=select_outputs, defer_outputs=defer_outputs)
    result["manifest"] = {
        "builder_commit": manifest["builder_commit"],
        "arm_for_qualification": manifest["arm_for_qualification"],
        qual.QF_SELECT: manifest[qual.QF_SELECT],
    }

    _assert_score_path_is_free()
    SCORE_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
