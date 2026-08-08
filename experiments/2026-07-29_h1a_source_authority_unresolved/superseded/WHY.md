# Superseded — Q2 anchor-sensitivity diagnostic (retired by Q6=A)

These five files implemented the Q2 anchor-flip diagnostic: a 2 arms x 2
anchor levels x 5 repeats = 20-call harness that measured how sensitive
`select_type`/`defer` was to the payload's pre-filled `type` value, as a
pre-freeze check before the main cohort.

- `_h1a_diag.py`
- `_h1a_diag_score.py`
- `test_h1a_diag.py`
- `test_h1a_diag_score.py`
- `h1a-decider.md` (the shared agent definition both arms of the diagnostic used)

## Why retired, not fixed

`DESIGN_DECISION_H1a_review_blockers.md` Q6=A (2026-08-01): a second
independent review found the type anchor itself is a model-facing answer
candidate (a no-cost path to `select_type`: repeat the recorded repository
state), not merely something whose *interference* needed measuring. Q6.2 is
explicit:

> The original Q2 anchor-flip diagnostic becomes **unnecessary and
> inapplicable**, because the model-facing type anchor is removed from the
> main payload.

Since the anchor no longer exists in `build_model_payload`'s output
(`_h1a_surface.py` deviation #3, `concept_feature_pair` instead of
`candidate_concepts` with `type`), there is nothing left for a 20-call
anchor-sensitivity measurement to detect. The 47 tests these files carried
were not wrong when written — they correctly measured the anchor that
existed at the time. The ruling changed what exists to measure, not whether
the measurement was done correctly.

## What replaced it

`_h1a_surface.py::assert_no_model_facing_type_anchor` — a structural
pre-freeze guard, per Q6.2's own specification:

- fails if any model-facing payload key is answer-bearing (`type`,
  `selected_type`, `expected_type`, `current_type`, `recorded_type`)
- fails if any model-facing string value equals an allowed type name
  (`essential_feature`, `structural_composition`) outside
  `evidence_items[].text`

This is a presence/absence check, not a behavioral-sensitivity measurement —
appropriate once the thing being guarded against is a payload shape, not a
model response distribution.

## Provenance discipline

These files are committed to history (not deleted outright) so that the
retirement itself is traceable: the diagnostic was built correctly against
D-H1a's prior design, then retired by a binding ruling once that design
changed — not discovered as a defect. `git log --follow` on any file here
reaches the commit where it was built and tested (18/18, 29/29 passing at
the time) before this move.
