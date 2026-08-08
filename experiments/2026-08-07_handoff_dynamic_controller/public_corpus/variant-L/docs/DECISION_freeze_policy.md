---
status: current
supersedes: archive/2026-06/DECISION_freeze_policy.md
---

# Decision — freeze policy for the reshape

Adopted 2026-07-14. This is the authority for what may move.

## Rule

A directory may be moved only when its worktree is clean. A dirty worktree is
protected: it may be read and searched, never moved, renamed, or annotated.

## Stop condition

The reshape stops when step 5 completes AND every moved path resolves from the
index. Partial completion is not completion.

## Current state

Steps 1 and 2 are done. Step 3 is paused. Step 4 must not start before the
retired-fixtures destination is applied from the audit that decided it.

## What this does not decide

It does not decide where retired fixtures go. That was settled separately and
this document deliberately does not restate it, to avoid two sources drifting.
