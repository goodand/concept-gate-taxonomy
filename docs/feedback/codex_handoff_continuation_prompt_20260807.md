---
aliases:
  - Codex Handoff Continuation Prompt
  - Dynamic Controller Experiment Handoff Prompt
tags:
  - doc/guide
  - stage/handoff
  - status/active
---

# Codex Handoff Continuation Prompt

This is the rendered instance of
[[docs/feedback/handoff_continuation_prompt_template|Cross-workspace template]].
For another workspace, copy the template and replace every variable there;
do not copy this project's paths unchanged.

```text
Continue the isolated handoff-retrieval experiment in:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

Scope: [state the demonstrated defect or evidence-review task; do not run
primary unless the user explicitly approves it]

First read these workspace-relative documents in order:
1. docs/feedback/codex_mcp_handoff_moc_20260807.md
2. docs/feedback/codex_mcp_handoff_qualification_log_20260807.md
3. experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md
4. the result artifact linked by the MOC for the task at hand
5. experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS.md,
   run_live_phase_c.py, _providers.py, live_subject_mcp.py, and relevant tests
6. experiments/2026-08-07_handoff_dynamic_controller/live_subject_response.schema.json,
   retrieval_subagent_response.schema.json, _contract.py, and _evaluator.py

Authority and safety boundaries:
- MOCs, tags, symlinks, and generated views are discovery surfaces. Read a
  selected canonical source before making a factual claim.
- Do not read, expose, copy, or edit hidden_gold/gold.json in a
  subject/controller context. It is for the clean judge only; use public host
  traces and reported metrics to diagnose a miss.
- Never overwrite results/live_pilot_*.json. A repair needs a new versioned
  config and a new result name.
- Do not run a primary experiment without explicit user approval. Passing
  qualification proves protocol readiness, not an arm effect.
- Active experiment artifacts outside this experiment directory may be read
  but must not be moved, renamed, merged, deleted, or annotated.
- Host-owned trace is authoritative for actions, reads, and terminal state;
  model prose and subagent output are not.
- Finding the handoff and canonical source is only retrieval success. Do not
  claim evaluator PASS unless the exact trace schema, citation ranges, and
  hard gate also pass.

Before changing code or protocol:
1. State one falsifiable defect hypothesis, citing a trace, evaluator, test,
   or canonical source.
2. Add a positive and paired negative test for that mechanism.
3. Make the smallest contract-preserving repair; do not weaken V1 or a guard
   merely because a pilot failed.
4. When a live surface changes, create a new config and run red-team,
   calibration, focused tests, then the full local suite before qualification.
5. Report entry discovery, canonical read, trace validity, and hard-gate result
   separately. A found document with an invalid trace is `partial`, not PASS.

Before ending:
1. Update docs/feedback/codex_mcp_handoff_qualification_log_20260807.md with
   issue evidence, recurrence count, resolution/unproven limit, hypothesis,
   validation, and exact next steps.
2. Update docs/feedback/codex_mcp_handoff_moc_20260807.md with Obsidian
   wikilinks to new canonical code, config, result, and log files, including a
   one-sentence relationship reason for each link.
3. Report changed files, commands/tests run, result status, and whether the
   next action needs user approval.
```

## Current Evidence Links

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Entry MOC]] maps source
  authority and current artifacts.
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Qualification log]]
  records defect evidence and the current decision boundary.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Prere-registration]]
  defines what qualification and primary results may claim.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v6.json|Codex qualification]]
  and [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v1.json|Claude qualification]]
  establish the current provider surface, not arm effects.
