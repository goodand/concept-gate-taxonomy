# Incident — no rows during quiet hours

2026-07-02. Resolved.

## What happened

The nightly job emitted zero rows for three consecutive runs. It was not a
failure: the job emits one row per MOVED path, and the reshape had been paused
at step 3, so there were no moved paths to emit.

## Resolution

No code change. The job's silence was correct and the alert threshold was
wrong. The alert now fires only when the reshape is unpaused AND rows are zero.

## Standing instruction

Do not restart the nightly job to "fix" zero rows while the reshape is paused.
Restarting rebuilds the index and would move paths the freeze policy protects.
