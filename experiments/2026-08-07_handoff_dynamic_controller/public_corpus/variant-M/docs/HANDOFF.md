# Handoff — tree reshape workstream

Entry point for anyone picking this up cold.

## Where things stand

The reshape is paused at step 3 of 5. Steps 1-2 landed; step 4 is blocked on a
decision that has already been made but is not linked from the plan, which is
the trap this handoff exists to defuse.

## Read these, in this order

1. [Freeze policy](DECISION_freeze_policy.md) — governs what may be moved.
2. [Directory cleanup plan](directory-cleanup-plan.md) — the working plan.
   It is a PLAN, not a decision; where it disagrees with the freeze policy,
   the freeze policy wins.
3. [Index](MOC_index.md) — generated navigation. Not an authority.

## Subproject

The parser subproject keeps its own handoff at
[subproject handoff](../subproject/HANDOFF.md). Same filename, different
workstream. Do not read one for the other.

## Nightly job

Operational context lives in [the nightly runbook](runbook-nightly.md).

## Retention

Retention rules are in `docs/policy-retention.md`.

## Superseded material

An older copy of the freeze policy survives under `archive/2026-06/`. It is
kept for audit only and contradicts the current one on the move rule.
