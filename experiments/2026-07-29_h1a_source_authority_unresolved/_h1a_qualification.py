"""H1a capability diagnostics -- D-H1a-14/15 (supersedes D-H1a-13 Q13.3's gate).

QF-SELECT and QF-DEFER are NON-BLOCKING capability diagnostics. They do not
grant or withhold permission to run the confirmatory cohort. The ruling
separated the two authorities:

    IDENTIFICATION CONTRACT -> freeze
    CAPABILITY DIAGNOSTICS  -> interpretation strength

WHY THIS MODULE EXISTS
-----------------------
D-H1a-13 Q13.3 withdrew the old "if both arms of this cohort fall into the
same modal behavior category" ceiling condition (PREREGISTRATION_TYPED_SCOPE_COHORT.md
sec 5, WITHDRAWN): independent review 20260806 (F6, MAJOR) found it restated
the primary result instead of providing independent floor/ceiling
information, and that its own re-registration had silently added unapproved
normative text.

Q13.3's replacement -- independent, non-pooled, separately-run fixtures --
is PRESERVED by D-H1a-14/15. What that ruling withdrew is only the coupling
"a control failed or is missing -> cohort_freeze: blocked", on the grounds
that `IndependentDiagnostic` does not entail `HardFreezePrerequisite`:
identifiability (C) does not logically require both controls to pass, and
`C -> (S AND D)` is not a tautology.

Q15=G additionally made the two controls symmetric -- `Role(QF_SELECT) =
Role(QF_DEFER)` -- because their failures are mirror images of one saturation
risk:

    QF-SELECT fail -> always-defer possible  -> floor saturation
    QF-DEFER  fail -> always-select possible -> ceiling saturation

so the status vocabulary here is control-agnostic by design.

HOW A DIAGNOSTIC OUTCOME IS READ
---------------------------------
  both pass          : floor and ceiling explanations independently weakened
  one fails          : cohort still runs; a null/small effect must NOT be
                       reported as ruling out that saturation explanation.
                       A NON-null effect is not invalidated.
  one unavailable    : cohort still runs; that direction is simply not
                       independently diagnosed. Recorded as unknown, and
                       explicitly NOT as failure -- it licenses no negative
                       conclusion about the trial subject (Q14.2).

HISTORY -- a retracted amendment, kept because the argument was persuasive
--------------------------------------------------------------------------
On 2026-08-15 this session demoted QF-DEFER to non-blocking WITHOUT a ruling,
and adversarial review retracted it the next day
(`docs/feedback/h1a_qf_defer_amendment_review_20260816.md`). D-H1a-14/15 then
reached a compatible conclusion through the proper channel -- and went
further, applying it symmetrically to BOTH controls.

The outcome converging does not vindicate the procedure. Two of the review's
findings stand independently of where the ruling landed:

  - The Q14 request document had itself annotated that exact move with
    "새 판정 필요" (a new ruling is required). Acting anyway was the defect,
    regardless of the answer.
  - The amendment's stated grounds were a non-sequitur: it argued from
    `M_allowed = NOT Q1 AND NOT Q7`'s silence about QF-DEFER, but Q13.3 never
    derived the controls from `M_allowed` (they did not exist when D-H1a-10
    was written). D-H1a-14/15 reaches the same demotion from an entirely
    different and valid argument -- the diagnostic/prerequisite distinction.
    Being right by luck is not being right.

D-H1a-14/15 accordingly imposed one standing rule:

    Moving a condition between `freeze_blocker` and `diagnostic` in either
    direction is an estimand/governance change, not an implementation
    change, and must not be executed before an external ruling.

WHAT THIS MODULE DOES NOT DO
-----------------------------
It does not construct or freeze the fixtures. QF-SELECT is grounded
(`fixture_qf_select.json`); QF-DEFER has no repo-grounded material (Q14), and
per Q14.1 the confirmatory 칼/철 fixture must NOT be reused to manufacture
one. This module is the DETERMINISTIC SCORING contract -- given raw trial
outputs it classifies them (via `_coder.code`, never `rationale`, same P5
discipline as the main cohort). It is independently testable with synthetic
outputs and does not require the fixtures to exist.

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

# Control-agnostic status vocabulary (D-H1a-14/15 Q14.2's recommended block).
# Not prefixed per-control because Q15=G made the two roles identical:
# `Role(QF_SELECT) = Role(QF_DEFER)`. A defer-only vocabulary would re-encode
# the asymmetry the ruling rejected.
DIAGNOSTIC_PASSED = "passed"
DIAGNOSTIC_FAILED = "failed"
MATERIAL_UNAVAILABLE = "material_unavailable"

# Q14.2: these two must NOT collapse into one category. "could not be tested"
# and "was tested and did not show the expected behavior" are epistemically
# different, and the ruling is explicit that `material_unavailable` licenses
# NO negative conclusion about subject capability.
_IMPLIES_SUBJECT_FAILURE = {
    DIAGNOSTIC_PASSED: False,
    DIAGNOSTIC_FAILED: True,
    MATERIAL_UNAVAILABLE: False,
}

# Which saturation risk each control probes (ruling's failure-mode table):
#   QF-SELECT fail -> always-defer possible  -> floor saturation
#   QF-DEFER  fail -> always-select possible -> ceiling saturation
_RISK_DIRECTION = {
    QF_SELECT: "floor",
    QF_DEFER: "ceiling",
}

# Retired 2026-08-16 (D-H1a-14/15). The name encoded the hard-gate era: it
# named a GATE OUTCOME that blocked the cohort. Under the ruling the controls
# do not gate anything, so a "failure category" on the run itself would be a
# category error. Failure is now recorded per control as a `status`, and its
# consequence is an interpretation limit, not a block.
# FLOOR_OR_CEILING_FAILURE = "floor_or_ceiling_failure"

# Q13.3 approved this sentence and D-H1a-14/15 did not retract it -- it
# restated the same obligation as `null_effect_requires_limitation: true`.
# Kept VERBATIM rather than reworded to match the new vocabulary: silently
# rewriting approved text is the F6 defect this experiment already paid for.
APPROVED_NULL_EFFECT_SENTENCE = (
    "A failed qualification gate must not be reported as evidence "
    "of a null treatment effect."
)


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


def _diagnose_control(control: str, outputs: "list | None") -> dict:
    """One control's capability diagnostic.

    Returns a `status` and, when the control actually ran, the observed rate.
    Deliberately emits NO `passes` boolean: a bare pass/fail invites callers
    to re-derive a gate from it, which is the coupling D-H1a-14/15 removed.
    """
    if outputs is None:
        return {
            "control": control,
            "status": MATERIAL_UNAVAILABLE,
            # Q14.2: material_unavailable licenses NO negative conclusion
            # about the trial subject's capability.
            "subject_verdict": None,
            "implies_subject_failure": _IMPLIES_SUBJECT_FAILURE[MATERIAL_UNAVAILABLE],
        }

    scored = _score_one_control(control, outputs)
    met_rate = scored.pop("passes")
    scored["status"] = DIAGNOSTIC_PASSED if met_rate else DIAGNOSTIC_FAILED
    scored["implies_subject_failure"] = _IMPLIES_SUBJECT_FAILURE[scored["status"]]
    if not met_rate:
        scored["observed_risk"] = f"{_RISK_DIRECTION[control]}_susceptibility"
    return scored


def score_qualification(
    select_outputs: "list | None" = None, defer_outputs: "list | None" = None
) -> dict:
    """Score both capability diagnostics -- D-H1a-14/15 (Q14=E, Q15=G).

    These controls DO NOT gate anything. The ruling separated the two
    authorities outright:

        IDENTIFICATION CONTRACT -> freeze
        CAPABILITY DIAGNOSTICS  -> interpretation strength

    so this function reports what was observed and what that does (and does
    not) license, and names `identification_contract` as freeze's owner
    instead of issuing a verdict of its own. The old
    `cohort_freeze: allowed|blocked` field was a verdict no freeze gate ever
    read -- `_h1a_policy.assert_freezable` has never referenced qualification
    -- so emitting it invited exactly the confusion this ruling resolved.

    Both parameters default to None, symmetrically: Q15=G established
    `Role(QF_SELECT) = Role(QF_DEFER)`, so neither control is privileged in
    this signature. QF-DEFER is currently None because its material does not
    exist in this repository (Q14).
    """
    select = _diagnose_control(QF_SELECT, select_outputs)
    defer = _diagnose_control(QF_DEFER, defer_outputs)

    def _observed(entry: dict):
        if entry["status"] == MATERIAL_UNAVAILABLE:
            return "unknown"
        return entry["status"] == DIAGNOSTIC_PASSED

    result = {
        "record_class": "h1a_capability_diagnostics",
        "ruling": "D-H1a-14/15",
        "required_rate": REQUIRED_RATE,
        "trials_per_control": TRIALS_PER_CONTROL,
        "capability_diagnostics": {"qf_select": select, "qf_defer": defer},
        "diagnostic_summary": {
            "select_capability_observed": _observed(select),
            "defer_capability_observed": _observed(defer),
            # "checked" means the diagnostic was administered at all, whatever
            # its outcome -- an executed-and-failed check IS independent
            # information about that risk; an un-run one is not.
            "floor_risk_independently_checked": select["status"] != MATERIAL_UNAVAILABLE,
            "ceiling_risk_independently_checked": defer["status"] != MATERIAL_UNAVAILABLE,
        },
        # Not a verdict -- a pointer to who owns the verdict.
        "cohort_freeze": {"determined_by": "identification_contract"},
    }

    failed = [e for e in (select, defer) if e["status"] == DIAGNOSTIC_FAILED]
    unavailable = [e for e in (select, defer) if e["status"] == MATERIAL_UNAVAILABLE]

    if failed:
        result["interpretation"] = {
            "null_effect_requires_limitation": True,
            "nonzero_effect_invalidated": False,
            "affected_controls": [e["control"] for e in failed],
            # Verbatim Q13.3 text, not reworded (see APPROVED_NULL_EFFECT_SENTENCE).
            "approved_reporting_sentence": APPROVED_NULL_EFFECT_SENTENCE,
            "note": (
                "A null or small effect must not be reported as ruling out the "
                "corresponding floor/ceiling explanation. A non-null effect is "
                "NOT invalidated by a failed capability diagnostic."
            ),
        }
    if unavailable:
        result["unavailable_diagnostics"] = {
            "controls": [e["control"] for e in unavailable],
            "record_as_unknown": True,
            "treat_as_failure": False,
            "note": (
                "Capability in this direction was not independently diagnosed. "
                "This licenses no negative conclusion about the trial subject "
                "(Q14.2) and does not block the cohort (Q15=G). Registered as "
                "a limitation, not a blocker."
            ),
        }
    return result
