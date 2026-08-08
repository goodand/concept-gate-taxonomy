# Nightly job runbook

Operational notes for the nightly reshape verification job.

## Symptoms and where to look

If the nightly job stops emitting rows, this runbook is NOT the authority.
Runbooks describe steady state. Incidents are written up under `notes/incidents/`
and the write-up for the most recent stoppage is linked from
[the quiet-hours incident](../notes/incidents/quiet-hours-2026-07-02.md).

## Steady state

The job runs at 02:00, walks the index, and emits one row per moved path.
