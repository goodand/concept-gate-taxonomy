"""H1a qualification gate -- D-H1a-13 Q13.3, AMENDED 2026-08-15 (QF-DEFER
demoted from freeze-blocking to non-blocking diagnostic).

WHY THIS MODULE EXISTS
-----------------------
D-H1a-13 Q13.3 withdrew the old "if both arms of this cohort fall into the
same modal behavior category" ceiling condition (PREREGISTRATION_TYPED_SCOPE_COHORT.md
sec 5, now WITHDRAWN): independent review 20260806 (F6, MAJOR) found that
condition restated the primary result rather than providing independent
floor/ceiling information, and that its own re-registration had silently
added unapproved normative text.

The replacement is a qualification gate SEPARATE from the confirmatory
cohort: two small, non-target fixtures with an unambiguous expected
behavior (QF-SELECT: exactly one type is warranted; QF-DEFER: neither type
is uniquely warranted), run BEFORE the confirmatory cohort, not pooled with
it, and not counted toward D-H1a-11's licensed-path contrast.

2026-08-15 AMENDMENT -- QF-DEFER is no longer freeze-blocking
---------------------------------------------------------------
Q13.3's original text required BOTH controls to pass at 0.80 before
`cohort_freeze: allowed`. Building QF-DEFER surfaced that no independent,
repo-grounded, same-source_kind conflicting-type material exists in this
repository (Q14 request, `correspondence/DESIGN_REQUEST_H1a_qualification_
defer_material.md`) -- and design consultation on that request, checked
against this experiment's own documented purpose, found the "both must
pass" rule stronger than H1a's stated identifiability requirement supports:

  - README.md sec 2: H1a's estimand is a pure descriptive contrast
    ("선택/보류 행동 분포가 달라지는가"), with explicit causal-attribution
    and generalization prohibitions. Nothing in that definition requires
    proving the trial subject can defer before a KEPT/REMOVED contrast is
    evidential.
  - DESIGN_DECISION_H1a_residual_prohibition.md sec 3's formal
    identifiability test is `M_allowed = NOT Q1 AND NOT Q7` -- a property
    of the ARM DESIGN (what the manipulation permits), not of trial-subject
    capability. QF-SELECT/QF-DEFER sit entirely outside that formal
    definition; they were bundled into Q13.3 as a symmetric pair without
    an independent argument for why defer-capability specifically must be
    a hard precondition rather than an interpretive aid.

The qualification gate's own stated purpose (Q13.3's rationale) is to
protect against MISREADING a null or same-modal-category confirmatory
result as "no treatment effect" when it could instead be a floor/ceiling
artifact of instrument incompetence. That protection is only load-bearing
WHEN the confirmatory result is actually null/ceiling-suspicious. A clear
KEPT/REMOVED contrast is evidential on its own regardless of QF-DEFER.

QF-SELECT's freeze-blocking status is UNCHANGED by this amendment -- only
QF-DEFER was actually litigated (Q14, plus two direct clarifying
questions the user answered: "does H1a's treatment-effect judgment
require QF-DEFER?" -> no; "does a large KEPT/REMOVED difference count as
H1a evidence without QF-DEFER?" -> yes). Whether QF-SELECT should be
treated symmetrically (also non-blocking, since an "always select"
ceiling would produce the identical spurious-null failure mode QF-DEFER
protects against, just from the other direction) is flagged as an OPEN
QUESTION in PREREGISTRATION_TYPED_SCOPE_COHORT.md sec 5a, not decided here
-- expanding scope beyond what was actually asked would be exactly the
un-requested change this project's own discipline warns against.

WHAT THIS MODULE DOES NOT DO
-----------------------------
It does not construct or freeze the QF-SELECT/QF-DEFER fixtures. QF-SELECT
is grounded (`fixture_qf_select.json`); QF-DEFER's absence is now a
recorded, non-blocking limitation (L9) rather than a blocker. This module
is the DETERMINISTIC SCORING contract -- given raw trial outputs, it
classifies them (via `_coder.code`, never `rationale`, same P5 discipline
as the main cohort) and applies the pass/fail rule. It is independently
testable with synthetic outputs and does not require the fixtures to exist.

Stdlib only.
"""

from __future__ import annotations

import _coder

TRIALS_PER_CONTROL = 5
REQUIRED_RATE = 0.80

QF_SELECT = "QF-SELECT"
QF_DEFER = "QF-DEFER"
CONTROLS = (QF_SELECT, QF_DEFER)

# The category `_coder.code()` must return for each control to count as a
# "pass" on that single trial.
_EXPECTED_CATEGORY = {
    QF_SELECT: _coder.SELECTION,
    QF_DEFER: _coder.DEFERRAL,
}

FLOOR_OR_CEILING_FAILURE = "floor_or_ceiling_failure"

# QF-DEFER outcome states (2026-08-15 amendment). Distinct from QF-SELECT's
# plain pass/fail because "material never existed" and "material existed and
# the subject failed the diagnostic" carry different reporting obligations --
# collapsing them would be exactly the "DEFER capability failed != DEFER
# material unavailable" confusion the design consultation flagged.
DEFER_MATERIAL_UNAVAILABLE = "material_unavailable"
DEFER_DIAGNOSTIC_PASSED = "diagnostic_passed"
DEFER_DIAGNOSTIC_FAILED = "diagnostic_failed"


class QualificationContractError(Exception):
    """Raised when the caller violates the gate's own preconditions -- e.g.
    the wrong number of trials. Never silently proceed on malformed input;
    that is exactly the shape of defect this gate exists to prevent one
    layer up (D-H1a-13 sec 8, `_h1a_score.py`'s counterpart discipline)."""


def _score_one_control(control: str, outputs: list) -> dict:
    if control not in CONTROLS:
        raise QualificationContractError(f"unknown control {control!r}, expected one of {CONTROLS}")
    if len(outputs) != TRIALS_PER_CONTROL:
        raise QualificationContractError(
            f"{control}: expected exactly {TRIALS_PER_CONTROL} trial outputs, got {len(outputs)}"
        )
    expected = _EXPECTED_CATEGORY[control]
    categories = [_coder.code(out) for out in outputs]
    hits = sum(1 for c in categories if c == expected)
    rate = hits / len(categories)
    return {
        "control": control,
        "expected_category": expected,
        "n": len(categories),
        "hits": hits,
        "rate": rate,
        "categories": categories,
        "passes": rate >= REQUIRED_RATE,
    }


def score_qualification(select_outputs: list, defer_outputs: "list | None" = None) -> dict:
    """The whole gate, in one call.

    2026-08-15 amendment: `cohort_freeze` depends on QF_SELECT ALONE.
    QF-DEFER is scored when `defer_outputs` is supplied, but never blocks
    freeze -- it is a non-blocking ceiling diagnostic, not a precondition
    for H1a's identifiability (see module docstring for the grounding).
    Passing `defer_outputs=None` records QF-DEFER as
    `DEFER_MATERIAL_UNAVAILABLE`, which is the current real state (Q14
    pending) rather than a failure.
    """
    select_result = _score_one_control(QF_SELECT, select_outputs)

    if defer_outputs is None:
        defer_result = {
            "control": QF_DEFER,
            "status": DEFER_MATERIAL_UNAVAILABLE,
            "passes": None,
        }
    else:
        defer_result = _score_one_control(QF_DEFER, defer_outputs)
        defer_result["status"] = (
            DEFER_DIAGNOSTIC_PASSED if defer_result["passes"] else DEFER_DIAGNOSTIC_FAILED
        )

    gate_passes = select_result["passes"]  # QF_DEFER no longer gates freeze

    result = {
        "record_class": "h1a_qualification_score",
        "required_rate": REQUIRED_RATE,
        "trials_per_control": TRIALS_PER_CONTROL,
        QF_SELECT: select_result,
        QF_DEFER: defer_result,
        "cohort_freeze": "allowed" if gate_passes else "blocked",
    }
    if not select_result["passes"]:
        result["result_category"] = FLOOR_OR_CEILING_FAILURE
        # Q13.3's own required sentence -- analysis/reporting contract only,
        # never rendered into the model-facing prompt.
        result["reporting_note"] = (
            "A failed qualification gate must not be reported as evidence "
            "of a null treatment effect."
        )

    if defer_result["status"] in (DEFER_MATERIAL_UNAVAILABLE, DEFER_DIAGNOSTIC_FAILED):
        # Non-blocking: does not affect cohort_freeze. Bounds interpretation
        # of a null/ceiling-suspicious confirmatory result, per L9.
        result["defer_ceiling_diagnostic_limitation"] = True
        result["defer_ceiling_reporting_note"] = (
            "The QF-DEFER ceiling diagnostic did not confirm defer "
            "capability (unavailable or failed). A null or "
            "ceiling-suspicious confirmatory result must not be read as "
            "ruling out a defer-side floor/ceiling artifact; L9 applies. "
            "A clear KEPT/REMOVED contrast is unaffected by this limitation."
        )
    return result
