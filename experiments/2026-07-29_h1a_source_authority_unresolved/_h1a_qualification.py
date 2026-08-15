"""H1a qualification gate -- D-H1a-13 Q13.3.

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
it, and not counted toward D-H1a-11's licensed-path contrast. If the trial
subject cannot reliably select when selection is warranted, or cannot
reliably defer when deferral is warranted, a null result on the real (K=1)
fixture is uninterpretable -- the instrument itself has not been shown to
respond to its own dependent variable.

WHAT THIS MODULE DOES NOT DO
-----------------------------
It does not construct or freeze the QF-SELECT/QF-DEFER fixtures. Those are
a separate design task (grounded, verified evidence, same discipline as
`fixture_source_authority.json`) tracked as still-pending in
PREREGISTRATION_TYPED_SCOPE_COHORT.md sec 5a. This module is the
DETERMINISTIC SCORING contract Q13.3 prescribes -- given raw trial outputs
for both controls, it classifies them (via `_coder.code`, never `rationale`,
same P5 discipline as the main cohort) and applies the ruling's exact
pass/fail rule. It is independently testable with synthetic outputs and
does not require the fixtures to exist.

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


def score_qualification(select_outputs: list, defer_outputs: list) -> dict:
    """The whole gate, in one call.

    Both controls are scored independently and BOTH must pass -- Q13.3
    requires "select_control: required_rate 0.80" AND "defer_control:
    required_rate 0.80", not either/or. A trial subject that reliably
    selects but never defers (or vice versa) has not demonstrated the
    instrument responds to its dependent variable in both directions.
    """
    select_result = _score_one_control(QF_SELECT, select_outputs)
    defer_result = _score_one_control(QF_DEFER, defer_outputs)
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
    return result
