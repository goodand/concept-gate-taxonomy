---
aliases:
  - Cross Workspace Handoff Prompt Template
tags:
  - doc/template
  - stage/handoff
---

# Cross-Workspace Handoff Continuation Prompt Template

Copy this file into the receiving workspace, fill every `{{PLACEHOLDER}}`, and
then give the rendered prompt to a new agent. Do not keep a placeholder value
from the source workspace.

## Instance Manifest

| Variable | Required value |
|---|---|
| `{{WORKSPACE_ROOT}}` | Absolute path to the receiving workspace |
| `{{ENTRY_MOC}}` | Workspace-relative Markdown entry map |
| `{{CONTINUATION_LOG}}` | Workspace-relative issue/evidence log |
| `{{EXPERIMENT_CONTRACT}}` | Preregistration, protocol, or operating contract |
| `{{RESULT_ARTIFACT}}` | Latest immutable result relevant to this handoff |
| `{{CANONICAL_IMPLEMENTATION}}` | Comma-separated canonical code/config files, or `none` |
| `{{TRACE_CONTRACT}}` | Required trace schema/evaluator contract, or `none` |
| `{{VALIDATION_COMMAND}}` | Exact non-live command that validates the handoff trace |
| `{{GOLD_POLICY}}` | `no hidden gold`, or exact clean-judge-only boundary/path |
| `{{LIVE_RUN_POLICY}}` | What needs explicit user approval and what is permitted |
| `{{ACTIVE_ARTIFACT_POLICY}}` | Paths that may only be read, not moved/renamed/edited |

## Rendered Prompt

```text
Continue work in {{WORKSPACE_ROOT}}.

Scope: {{SESSION_SCOPE}}

First read these workspace-relative documents in order:
1. {{ENTRY_MOC}}
2. {{CONTINUATION_LOG}}
3. {{EXPERIMENT_CONTRACT}}
4. {{RESULT_ARTIFACT}}
5. {{CANONICAL_IMPLEMENTATION}}
6. {{TRACE_CONTRACT}}

Authority and safety boundaries:
- Navigation notes, tags, symlinks, generated views, and MOCs are discovery
  surfaces. Read the selected canonical source before making a factual claim.
- {{GOLD_POLICY}}
- Never overwrite an immutable result artifact. A live-surface repair requires
  a new versioned config and a new result filename.
- {{LIVE_RUN_POLICY}}
- {{ACTIVE_ARTIFACT_POLICY}}
- The host-owned trace or equivalent execution record is authoritative for
  actions, reads, and terminal state; model prose and subagent output are not.
- Finding the handoff, MOC, backlinks, and canonical source is retrieval
  success only. It is not an evaluator pass until the emitted trace validates
  against {{TRACE_CONTRACT}}.

Before changing code, policy, or a protocol:
1. State one falsifiable defect hypothesis and cite its trace, test, or
   canonical source.
2. Add a positive and a paired negative test for that exact mechanism.
3. Make the smallest contract-preserving repair. Do not relax a safety gate
   merely because a model run failed.
4. If the evaluated surface changed, create a new versioned config and run the
   required red-team/calibration/validation before any live qualification.
5. Before claiming PASS, run: {{VALIDATION_COMMAND}}. Preserve required fields
   such as exact path, line_start, line_end, and citation objects; do not replace
   a machine trace with a prose summary.

Before ending this session:
1. Update {{CONTINUATION_LOG}} with new issue evidence, recurrence counts,
   resolution state, unproven limits, hypothesis, validation, and exact next
   steps.
2. Update {{ENTRY_MOC}} with Obsidian wikilinks to every new canonical code,
   config, result, or log. Add one sentence explaining each relationship.
3. Report changed files, commands/tests run, result status, and whether the
   next action requires user approval.
4. Report four states separately: entry discovery, canonical-source read,
   trace-contract validity, and evaluator hard-gate result. Use `partial` when
   discovery succeeds but trace validation does not.
```

## Gold-Set Example

Use one of these exact policy values:

- No gold set: `There is no hidden gold set. Do not create one retroactively
  from observed answers.`
- Clean-judge gold: `Do not read, expose, copy, or edit
  hidden_gold/gold.json in a subject/controller context. It is accessible only
  to the clean judge; use public host traces and reported metrics to diagnose
  a miss.`

The second form prevents a successor agent from turning an evaluator answer
key into a retrieval policy.

## Minimal Instance Example

```text
{{WORKSPACE_ROOT}} = /workspace/example
{{ENTRY_MOC}} = docs/feedback/handoff_moc.md
{{CONTINUATION_LOG}} = docs/feedback/handoff_log.md
{{EXPERIMENT_CONTRACT}} = experiments/retrieval/PREREGISTRATION.md
{{RESULT_ARTIFACT}} = experiments/retrieval/results/qualification_v2.json
{{CANONICAL_IMPLEMENTATION}} = experiments/retrieval/runner.py,
experiments/retrieval/evaluator.py
{{TRACE_CONTRACT}} = experiments/retrieval/trace.schema.json and
experiments/retrieval/evaluator.py
{{VALIDATION_COMMAND}} = python3 experiments/retrieval/validate_trace.py
{{GOLD_POLICY}} = Do not read, expose, copy, or edit
experiments/retrieval/hidden_gold/gold.json in a subject/controller context.
{{LIVE_RUN_POLICY}} = Do not run a primary evaluation without explicit user
approval; qualification runs are allowed only after local validation passes.
{{ACTIVE_ARTIFACT_POLICY}} = Do not move, rename, merge, delete, or annotate
artifacts under experiments/active/.
```

## Cross-Workspace Failure Pattern

A backlink can correctly lead a cold-start agent from an entry MOC to a
handoff while the run still fails because its trace omits line boundaries or
uses prose instead of citation objects. Classify that result as `retrieval
found / trace invalid`, not as a full pass and not as a retrieval miss.
