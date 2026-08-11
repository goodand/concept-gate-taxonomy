# Safety audit changelog — AUDIT SURFACE

Audit-only amendments go here, not in `PREREGISTRATION.md`.

`PREREGISTRATION.md` is execution surface, so appending an audit-only change
there re-invalidates provider qualification — the exact cost the two-layer
split exists to remove. Round 15 raised this; it was then measured while
adding `run_pipeline.py`, where the doctor reported both red-teams stale
because the surface lists and the audit tests lived in execution-layer files.

An amendment belongs here when it changes **how the audit is conducted** and
nothing about what a run means or how it executes: rubric wording, label
definitions, the authority manifest, reviewer assignment or qualification, the
packet builder, the adjudicator.

It belongs in `PREREGISTRATION.md` when it touches the evaluator, contract,
corpus, cases, gold, runner, host, provider, isolation, or an active config —
including a change made *for* the audit that also edits one of those.

This file is itself audit surface, so writing in it does not invalidate
provider evidence.

## A-1 — 2026-08-11

First entry is procedural: the split of `test_safety_audit.py` out of
`test_protocol.py` and of the surface lists into
`frozen_surface_execution.json` / `frozen_surface_audit.json` is recorded in
`PREREGISTRATION.md` (Amendment 37) because it edited `_evaluator.py`. From
here on, an audit-only change should not need to touch that file at all.

Measured after the split, on a realistic three-file audit change bundle
(rubric + audit tests + audit surface list):

```
execution drift: []
audit drift    : ['SAFETY_AUDIT_RUBRIC.md', 'frozen_surface_audit.json',
                  'test_safety_audit.py']
provider red-team still valid: True
```
