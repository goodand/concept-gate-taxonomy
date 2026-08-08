# Retention policy

How long each artifact class is kept.

## Classes

- Superseded decisions: retained indefinitely under `archive/`, audit only.
- Incident write-ups: retained 24 months.
- Generated indexes: not retained; rebuilt on demand.
- Retired fixtures: retained 6 months after the move completes, then deleted.

## Deletion authority

Deletion requires the workstream owner's approval. No automated job may delete
a retained artifact, including the nightly job.
