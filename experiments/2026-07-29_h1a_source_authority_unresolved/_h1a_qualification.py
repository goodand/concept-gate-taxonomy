"""H1a qualification gate -- D-H1a-13 Q13.3, as ruled (both controls block).

⚠️ 2026-08-15 AMENDMENT RETRACTED 2026-08-16
---------------------------------------------
A 2026-08-15 amendment demoted QF-DEFER to a non-blocking diagnostic so
`cohort_freeze` depended on QF-SELECT alone. Adversarial review the next day
(`docs/feedback/h1a_qf_defer_amendment_review_20260816.md`) did not adopt it,
on four blockers. The decisive one is self-inflicted: the Q14 request
document that raised the question had already annotated this exact move --
its own option D, "relax Q13.3's both-must-pass requirement" -- with "새 판정
필요" (a new ruling is required), and the amendment proceeded without one.

The review also found the change was a structural regression: Q13.3 exists
precisely because independent review F6 judged an *interpretation condition*
insufficient and replaced it with a *hard gate*. Demoting QF-DEFER to a
recorded limitation converted that half back into an interpretation
condition -- the form F6 condemned -- via an operating session's own
re-registration, which is the shape of defect F6 flagged.

This module is therefore back to the ruling as written: BOTH controls must
pass. QF-DEFER's material does not exist (Q14), so the gate blocks. That is
the ruling working, not a defect to route around. The question is resubmitted
as Q14 (with Q15) through the external ruling channel; until it returns,
`cohort_freeze` stays blocked.

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

WHY THE ARGUMENT FOR DEMOTING QF-DEFER DID NOT SURVIVE
-------------------------------------------------------
Recorded because the reasoning was plausible enough to be acted on once,
and a future session will meet it again. The retracted amendment argued:

  - README.md sec 2 defines a purely descriptive estimand and says nothing
    about needing to prove defer capability first; and
  - DESIGN_DECISION_H1a_residual_prohibition.md sec 3's identifiability
    test `M_allowed = NOT Q1 AND NOT Q7` is about ARM DESIGN permissions,
    not trial-subject capability, so QF-DEFER sits outside it.

Both citations are textually accurate. The inference from them is not.
Q13.3 never derived QF-SELECT/QF-DEFER from `M_allowed` -- those constructs
did not exist when D-H1a-10 was written -- so `M_allowed`'s silence about
QF-DEFER was never in dispute and licenses nothing. Q13.3 introduced the
two controls for a separate stated purpose: preventing a null or
same-modal-category confirmatory result from being misread as a genuine
null effect when it could instead be an instrument floor/ceiling artifact.
Arguing from an unrelated document's silence is a non-sequitur.

The amendment's own text also conceded that the protection is load-bearing
exactly when the confirmatory result turns out null -- yet switched it off
prospectively, at zero trials, before anyone could know whether that is the
case. A safeguard removed for precisely the scenario its own rationale says
it exists for.

WHAT THIS MODULE DOES NOT DO
-----------------------------
It does not construct or freeze the QF-SELECT/QF-DEFER fixtures. QF-SELECT
is grounded (`fixture_qf_select.json`); QF-DEFER has no repo-grounded
material (Q14, still open), so the gate cannot currently complete. This
module is the DETERMINISTIC SCORING contract -- given raw trial outputs, it
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

    Both controls are scored and BOTH must pass -- Q13.3 requires
    "select_control: required_rate 0.80" AND "defer_control: required_rate
    0.80", not either/or. A trial subject that reliably selects but never
    defers (or vice versa) has not demonstrated the instrument responds to
    its dependent variable in both directions.

    `defer_outputs=None` means QF-DEFER was not run because no repo-grounded
    material for it exists (Q14). That control therefore does not pass, so
    the gate blocks -- which is what Q13.3 prescribes and NOT a defect to be
    routed around. The `status` field records WHY it did not pass
    (`DEFER_MATERIAL_UNAVAILABLE`, not `DEFER_DIAGNOSTIC_FAILED`) so the
    record never claims the subject failed a diagnostic that was never
    administered.
    """
    select_result = _score_one_control(QF_SELECT, select_outputs)

    if defer_outputs is None:
        defer_result = {
            "control": QF_DEFER,
            "status": DEFER_MATERIAL_UNAVAILABLE,
            # An un-administered control has not met the required rate. The
            # ruling's gate is "both pass"; "not run" is not "passed".
            "passes": False,
        }
    else:
        defer_result = _score_one_control(QF_DEFER, defer_outputs)
        defer_result["status"] = (
            DEFER_DIAGNOSTIC_PASSED if defer_result["passes"] else DEFER_DIAGNOSTIC_FAILED
        )

    gate_passes = select_result["passes"] and defer_result["passes"]

    result = {
        "record_class": "h1a_qualification_score",
        "required_rate": REQUIRED_RATE,
        "trials_per_control": TRIALS_PER_CONTROL,
        QF_SELECT: select_result,
        QF_DEFER: defer_result,
        "cohort_freeze": "allowed" if gate_passes else "blocked",
    }
    if not gate_passes:
        result["result_category"] = FLOOR_OR_CEILING_FAILURE
        # Q13.3's own required sentence -- analysis/reporting contract only,
        # never rendered into the model-facing prompt.
        result["reporting_note"] = (
            "A failed qualification gate must not be reported as evidence "
            "of a null treatment effect."
        )

    if defer_result["status"] == DEFER_MATERIAL_UNAVAILABLE:
        # Descriptive bookkeeping, NOT a new normative category. Q13.3
        # prescribes one result_category for a non-passing gate and this does
        # not add a second; it records which of the two ways QF-DEFER failed
        # to pass, so a reader never mistakes "never administered" for
        # "administered and failed". Whether the ruling intends these two to
        # share a result_category at all is an open question submitted as
        # Q14.2 -- it is asked, not answered here.
        result["qualification_incomplete"] = True
        result["qualification_incomplete_reason"] = (
            "QF-DEFER was not administered: no repo-grounded, same-source_kind "
            "conflicting-type material exists for it (Q14). This is not a "
            "diagnostic failure by the trial subject. The gate blocks because "
            "D-H1a-13 sec 6 requires both controls to pass; resolving it "
            "requires the Q14 ruling, not a code change."
        )
    return result
