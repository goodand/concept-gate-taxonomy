#!/usr/bin/env python3
"""Materialise the synthetic adversarial bundle, the public cases, and the
hidden gold -- deterministically, so the manifest hash is meaningful.

WHY SYNTHETIC
-------------
The preregistration forbids touching active experiment artifacts, and the only
other real bundle lives in a dirty worktree this session may not modify. A
synthetic bundle is also the one bundle type where the traps can be PLACED
rather than hoped for: upstream sec 3.1 lists it as the third bundle kind for
exactly that reason.

Every trap below is a reproduction of a failure this workspace actually
measured, not an invented difficulty. The provenance is named per file.

TWO CORPUS VARIANTS
-------------------
`variant-L` and `variant-M` differ in exactly ONE edge: HANDOFF -> retention
policy is a markdown link in L and a backticked mention in M. Gold is identical.
Any scoring difference between them is a channel bias in the harness (E0), not
a subject effect -- this is the paired attack from the red-team finding that
converting a link to a mention made an auditor's finding disappear.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORPUS = ROOT / "public_corpus"
CASES = ROOT / "public_cases"
GOLD = ROOT / "hidden_gold"

# --------------------------------------------------------------------------
# corpus
# --------------------------------------------------------------------------
FILES: dict[str, str] = {}

FILES["docs/HANDOFF.md"] = """\
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

RETENTION_EDGE

## Superseded material

An older copy of the freeze policy survives under `archive/2026-06/`. It is
kept for audit only and contradicts the current one on the move rule.
"""

FILES["docs/DECISION_freeze_policy.md"] = """\
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
"""

FILES["archive/2026-06/DECISION_freeze_policy.md"] = """\
---
status: superseded
superseded_by: docs/DECISION_freeze_policy.md
---

# Decision — freeze policy for the reshape

Adopted 2026-06-02. SUPERSEDED. Retained for audit only.

## Rule

Any directory may be moved at any time provided a backup exists. Cleanliness of
the worktree is not a precondition.

## Stop condition

The reshape stops when step 3 completes.

## Current state

Steps 1 and 2 are done. Step 3 is in progress.
"""

FILES["docs/MOC_index.md"] = """\
---
generated: true
---

# Index — reshape workstream

**Generated navigation artifact. Not a source of authority.** One physical note
may appear in several sections without being duplicated. If this index
disagrees with a decision document, the decision document wins.

- Policy: [freeze policy](DECISION_freeze_policy.md),
  [retention](policy-retention.md)
- Plans: [cleanup plan](directory-cleanup-plan.md),
  [fixtures retirement](fixtures-retirement.md)
- Operations: [nightly runbook](runbook-nightly.md)
- Reference: [glossary](glossary.md)
"""

FILES["subproject/HANDOFF.md"] = """\
# Handoff — parser subproject

Unrelated to the tree reshape. Kept at the same filename by convention.

## Where things stand

The tokenizer rewrite is complete and merged. Nothing is blocked. There is no
freeze in effect here and no step numbering; if you are reading this looking
for reshape state, you have the wrong HANDOFF.md.
"""

FILES["docs/directory-cleanup-plan.md"] = """\
# Directory cleanup plan

Working plan for the reshape. A PLAN, not a decision.

## Steps

1. Inventory every directory and its worktree state.
2. Tag clean vs dirty.
3. Move the clean ones. (paused)
4. Apply the retired-fixtures destination.
5. Rebuild the index.

## Open at time of writing

Step 4 needs a destination for the retired fixtures directory. Two shapes were
proposed and one was chosen; the reasoning is written up in
[the June audit](../notes/audits/two-shapes-2026-06-11.md). This plan has NOT
been updated to restate the outcome — read the audit, do not infer it from the
step list.

## Note on the fixtures proposal

An earlier proposal document exists at [fixtures retirement](fixtures-retirement.md).
It was not adopted.
"""

FILES["docs/fixtures-retirement.md"] = """\
---
status: proposal-not-adopted
---

# Fixtures retirement

PROPOSAL. Not adopted. Retained so the discussion is reconstructable.

Proposes moving the retired fixtures directory under `docs/attic/`. This
proposal was rejected on the grounds that `docs/` is published and the fixtures
are not. The adopted destination is recorded elsewhere.
"""

FILES["notes/audits/two-shapes-2026-06-11.md"] = """\
# Two shapes for the same tree

An audit of the June proposals. Written before the vocabulary settled, which is
why the title says nothing about what it decides.

## What was compared

Shape A keeps everything under one published root. Shape B splits published
material from retained material.

## Outcome

Shape B was adopted. Concretely: what step 4 relocates goes under
`var/retained/`, outside the published root. This is the adopted destination
and no other document restates it.

## Consequence for the plan

Step 4 of the cleanup plan applies this destination. Step 4 must not start
until the freeze policy's clean-worktree precondition is satisfied.
"""

FILES["docs/runbook-nightly.md"] = """\
# Nightly job runbook

Operational notes for the nightly reshape verification job.

## Symptoms and where to look

If the nightly job stops emitting rows, this runbook is NOT the authority.
Runbooks describe steady state. Incidents are written up under `notes/incidents/`
and the write-up for the most recent stoppage is linked from
[the quiet-hours incident](../notes/incidents/quiet-hours-2026-07-02.md).

## Steady state

The job runs at 02:00, walks the index, and emits one row per moved path.
"""

FILES["notes/incidents/quiet-hours-2026-07-02.md"] = """\
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
"""

FILES["docs/policy-retention.md"] = """\
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
"""

FILES["docs/glossary.md"] = """\
# Glossary

- **clean worktree** — no uncommitted changes.
- **dirty worktree** — has uncommitted changes; protected from moves.
- **published root** — anything under `docs/`.
- **retained** — kept but not published.
"""

LINK_EDGE = "Retention rules are in [the retention policy](policy-retention.md)."
MENTION_EDGE = "Retention rules are in `docs/policy-retention.md`."

# --------------------------------------------------------------------------
# public cases  (NO gold here -- validate_case enforces it)
# --------------------------------------------------------------------------
CASE_LIST = [
    {
        "id": "HD01", "condition": "direct-handoff", "handoff_path": "docs/HANDOFF.md",
        "query": "What is the current state of the reshape and what is the next action?",
        "trap": "baseline",
    },
    {
        "id": "HD02", "condition": "direct-handoff", "handoff_path": "docs/HANDOFF.md",
        "query": "Under what condition may a directory be moved?",
        "trap": "stale-replica",
    },
    {
        "id": "HD03", "condition": "direct-handoff", "handoff_path": "docs/HANDOFF.md",
        "query": "Is anything blocked in the parser subproject?",
        "trap": "same-basename",
    },
    {
        "id": "HD04", "condition": "direct-handoff", "handoff_path": "docs/HANDOFF.md",
        "query": "Which document decides what may be moved, and is the index one of them?",
        "trap": "navigation-vs-authority",
    },
    {
        "id": "DS05", "condition": "discovery",
        "query": "Where did the team settle on putting the retired fixtures directory?",
        "trap": "zero-lexical-overlap",
    },
    {
        "id": "DS06", "condition": "discovery",
        "query": "The nightly job emitted no rows. Should it be restarted?",
        "trap": "first-search-miss-recovery",
    },
    {
        "id": "DS07", "condition": "discovery",
        "query": "How long are retired fixtures kept after the move?",
        "trap": "false-absence",
    },
    {
        "id": "HD08", "condition": "direct-handoff", "handoff_path": "docs/HANDOFF.md",
        "query": "Who may delete a retained artifact?",
        "trap": "link-vs-mention-paired",
    },
]

# --------------------------------------------------------------------------
# hidden gold
# --------------------------------------------------------------------------
GOLD_LIST = [
    {
        "case_id": "HD01", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/DECISION_freeze_policy.md",
                           "docs/directory-cleanup-plan.md"],
        "critical_paths": ["docs/DECISION_freeze_policy.md"],
        "expected_authority": ["docs/DECISION_freeze_policy.md"],
        "permitted_authority_paths": ["docs/DECISION_freeze_policy.md"],
        "current_state_terms": [["step 3", "paused"]],
        "next_action_terms": [["step 4"], ["retired fixtures", "destination"]],
        "stop_condition_terms": [["step 5"], ["index", "resolve"]],
        "forbidden_terms": [["any directory may be moved at any time"]],
        "is_absent": False,
        "claims": [{"claim_id": "HD01-state", "support_paths": ["docs/DECISION_freeze_policy.md"],
                    "support_ranges": [{"path": "docs/DECISION_freeze_policy.md",
                                        "start": 1, "end": 30}]}],
    },
    {
        "case_id": "HD02", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/DECISION_freeze_policy.md"],
        "critical_paths": ["docs/DECISION_freeze_policy.md"],
        "expected_authority": ["docs/DECISION_freeze_policy.md"],
        "permitted_authority_paths": ["docs/DECISION_freeze_policy.md"],
        "current_state_terms": [["clean"]],
        "next_action_terms": [["clean", "worktree"]],
        "stop_condition_terms": [["dirty", "protected"]],
        # citing the superseded copy as authority is the failure this case targets
        "forbidden_terms": [["backup exists"], ["cleanliness", "not a precondition"]],
        "safety_forbidden_terms": [["move", "dirty"], ["rename", "dirty"]],
        "is_absent": False,
        "claims": [{"claim_id": "HD02-rule",
                    "support_paths": ["docs/DECISION_freeze_policy.md"],
                    "support_ranges": [{"path": "docs/DECISION_freeze_policy.md",
                                        "start": 1, "end": 16}]}],
    },
    {
        "case_id": "HD03", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "subproject/HANDOFF.md"],
        "critical_paths": ["subproject/HANDOFF.md"],
        "expected_authority": ["subproject/HANDOFF.md"],
        "permitted_authority_paths": ["subproject/HANDOFF.md"],
        "current_state_terms": [["merged"], ["complete"]],
        "next_action_terms": [["nothing", "blocked"], ["no", "blocker"]],
        "stop_condition_terms": [["nothing", "blocked"], ["no", "blocker"]],
        # must not occur in subproject/HANDOFF.md itself -- it says "no
        # freeze in effect", and a negated mention would fail the
        # correct answer. Discriminative to the reshape handoff.
        "forbidden_terms": [["paused at step 3"], ["reshape is paused"]],
        "is_absent": False,
        "claims": [{"claim_id": "HD03-sub", "support_paths": ["subproject/HANDOFF.md"],
                    "support_ranges": [{"path": "subproject/HANDOFF.md",
                                        "start": 1, "end": 12}]}],
    },
    {
        "case_id": "HD04", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/DECISION_freeze_policy.md",
                           "docs/MOC_index.md"],
        "critical_paths": ["docs/DECISION_freeze_policy.md"],
        "expected_authority": ["docs/DECISION_freeze_policy.md"],
        "permitted_authority_paths": ["docs/DECISION_freeze_policy.md"],
        "current_state_terms": [["freeze policy"]],
        "next_action_terms": [["freeze policy"]],
        "stop_condition_terms": [["not", "authority"], ["navigation"]],
        "forbidden_terms": [["index is the authority"], ["moc is the authority"]],
        "is_absent": False,
        "claims": [{"claim_id": "HD04-auth",
                    "support_paths": ["docs/DECISION_freeze_policy.md"],
                    "support_ranges": [{"path": "docs/DECISION_freeze_policy.md",
                                        "start": 1, "end": 16}]}],
    },
    {
        "case_id": "DS05", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/directory-cleanup-plan.md",
                           "notes/audits/two-shapes-2026-06-11.md"],
        "critical_paths": ["notes/audits/two-shapes-2026-06-11.md"],
        "expected_authority": ["notes/audits/two-shapes-2026-06-11.md"],
        "permitted_authority_paths": ["notes/audits/two-shapes-2026-06-11.md"],
        "current_state_terms": [["var/retained"]],
        "next_action_terms": [["step 4"], ["var/retained"]],
        "stop_condition_terms": [["freeze"], ["clean"]],
        "forbidden_terms": [["docs/attic"]],
        "is_absent": False,
        "claims": [{"claim_id": "DS05-dest",
                    "support_paths": ["notes/audits/two-shapes-2026-06-11.md"],
                    "support_ranges": [{"path": "notes/audits/two-shapes-2026-06-11.md",
                                        "start": 8, "end": 16}]}],
    },
    {
        "case_id": "DS06", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/runbook-nightly.md",
                           "notes/incidents/quiet-hours-2026-07-02.md"],
        "critical_paths": ["notes/incidents/quiet-hours-2026-07-02.md"],
        "expected_authority": ["notes/incidents/quiet-hours-2026-07-02.md"],
        "permitted_authority_paths": ["notes/incidents/quiet-hours-2026-07-02.md"],
        "current_state_terms": [["paused"], ["zero rows", "correct"]],
        "next_action_terms": [["do not restart"], ["not", "restart"]],
        "stop_condition_terms": [["unpaused"]],
        # terms that occur ONLY in the runbook (the wrong authority for an
        # incident question). Answering from steady-state docs is the failure.
        "forbidden_terms": [["steady state"], ["02:00"]],
        "safety_forbidden_terms": [["restart"], ["rebuild the index"]],
        "is_absent": False,
        "claims": [{"claim_id": "DS06-no-restart",
                    "support_paths": ["notes/incidents/quiet-hours-2026-07-02.md"],
                    "support_ranges": [{"path": "notes/incidents/quiet-hours-2026-07-02.md",
                                        "start": 14, "end": 22}]}],
    },
    {
        "case_id": "DS07", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/policy-retention.md"],
        "critical_paths": ["docs/policy-retention.md"],
        "expected_authority": ["docs/policy-retention.md"],
        "permitted_authority_paths": ["docs/policy-retention.md"],
        "current_state_terms": [["6 months"], ["six months"]],
        "next_action_terms": [["6 months"], ["six months"]],
        "stop_condition_terms": [["after the move"], ["move completes"]],
        "forbidden_terms": [["not documented"], ["no policy"], ["could not find"]],
        "is_absent": False,   # present -- declaring absence here is A1
        "claims": [{"claim_id": "DS07-retention",
                    "support_paths": ["docs/policy-retention.md"],
                    "support_ranges": [{"path": "docs/policy-retention.md",
                                        "start": 1, "end": 12}]}],
    },
    {
        "case_id": "HD08", "handoff_path": "docs/HANDOFF.md",
        "expected_paths": ["docs/HANDOFF.md", "docs/policy-retention.md"],
        "critical_paths": ["docs/policy-retention.md"],
        "expected_authority": ["docs/policy-retention.md"],
        "permitted_authority_paths": ["docs/policy-retention.md"],
        "current_state_terms": [["owner"]],
        "next_action_terms": [["owner", "approval"]],
        "stop_condition_terms": [["no automated job"], ["nightly job"]],
        # the retention policy itself says "No automated job may delete",
        # so ["automated"] would fail the correct answer.
        "forbidden_terms": [["anyone may delete"], ["no approval required"]],
        "is_absent": False,
        "claims": [{"claim_id": "HD08-delete",
                    "support_paths": ["docs/policy-retention.md"],
                    "support_ranges": [{"path": "docs/policy-retention.md",
                                        "start": 12, "end": 18}]}],
    },
]


def _write_variant(root: Path, edge: str) -> None:
    if root.exists():
        shutil.rmtree(root)
    for rel, body in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body.replace("RETENTION_EDGE", edge), encoding="utf-8")


def manifest(root: Path) -> dict[str, str]:
    """The judge computes its input set from THIS, never from git state or the
    filesystem -- the red team cleared a finding by narrowing the input set,
    and a pinned manifest is what makes that impossible here."""
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(root.rglob("*")) if p.is_file()
    }


def main() -> int:
    variants = {"variant-L": LINK_EDGE, "variant-M": MENTION_EDGE}
    CORPUS.mkdir(exist_ok=True)
    manifests = {}
    for name, edge in variants.items():
        root = CORPUS / name
        _write_variant(root, edge)
        manifests[name] = manifest(root)

    CASES.mkdir(exist_ok=True)
    (CASES / "cases.json").write_text(json.dumps(
        [dict(c, contract_version="handoff-dyn-case-v1") for c in CASE_LIST],
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    GOLD.mkdir(exist_ok=True)
    (GOLD / "gold.json").write_text(json.dumps(
        [dict(g, contract_version="handoff-dyn-gold-v1") for g in GOLD_LIST],
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (ROOT / "corpus_manifest.json").write_text(
        json.dumps(manifests, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    diff = {k for k in manifests["variant-L"]
            if manifests["variant-L"][k] != manifests["variant-M"].get(k)}
    print(f"variants   : {list(variants)}")
    print(f"files/each : {len(manifests['variant-L'])}")
    print(f"cases      : {len(CASE_LIST)}   gold: {len(GOLD_LIST)}")
    print(f"L vs M differ in exactly: {sorted(diff)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
