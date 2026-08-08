---
aliases:
  - Claude Red Team Pre-Primary Prompt
tags:
  - doc/prompt
  - stage/handoff
  - status/pending-review
---

# Claude Red-Team Prompt: Pre-Primary Gate Audit

Use this in a **new Claude Code session**. Do not resume a prior session.
This is a code-and-artifact audit, not a live retrieval evaluation.

```text
You are an independent red-team reviewer. Work only in:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

Mission: determine whether the handoff dynamic-controller experiment can
incorrectly permit, mislabel, or overinterpret a future primary run after both
provider qualifications passed. Do not execute a primary, pilot, provider CLI,
or any paid model call. Do not modify code, configs, corpus, evaluator, result
artifacts, or gold. Write only one new review document under docs/feedback/.

Hard boundaries:
- Do not read, search for, copy, print, or infer from
  experiments/2026-08-07_handoff_dynamic_controller/hidden_gold/gold.json.
- Do not read home-directory transcripts, credentials, or other agent session
  state. Do not use --resume, --continue, or session reuse.
- Do not treat MOCs or the qualification log as authority; use them only to
  locate canonical code, contract, and immutable results.
- Do not run commands that invoke Claude, Codex, MCP, network access, or a live
  experiment. Local unit tests that do not invoke a provider are allowed only
  if needed to confirm a finding.

Read in this order:
1. docs/feedback/codex_mcp_handoff_moc_20260807.md
2. docs/feedback/codex_mcp_handoff_qualification_log_20260807.md
3. experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md
4. experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS.md
5. experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py
6. experiments/2026-08-07_handoff_dynamic_controller/_providers.py
7. experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py
8. experiments/2026-08-07_handoff_dynamic_controller/phase_c_claude_mcp_surface_config.json
9. experiments/2026-08-07_handoff_dynamic_controller/phase_c_codex_mcp_v6_config.json
10. the two qualification results:
    results/live_pilot_codex_mcp_v6.json and
    results/live_pilot_claude_mcp_surface_v1.json

Audit questions. For every finding, provide exact file:line evidence, an
attack/reproduction thought experiment that does not use gold, severity, and a
minimal fix plus a paired regression test.

Q1. Can --primary pass with incomplete, stale, wrong-provider, renamed, or
synthetically edited qualification artifacts? Check matrix coverage, result
kind, provider/sandbox/config identity, frozen hashes, overwrite behavior, and
the order in which the runner validates these conditions.

Q2. Can a qualification artifact be structurally valid while no real provider
action occurred, or while the host trace is fabricated/decoupled from provider
output? Trace data ownership from host socket through saved artifact and clean
judge. Distinguish a proven guard from a convention.

Q3. Does the current gate distinguish protocol readiness from estimated arm
effect? In particular, assess whether `R_STATIC` full_hard_gate=0 in the
Claude qualification is documented and mechanically prevented from becoming a
performance claim.

Q4. Can a frozen-surface change invalidate one provider qualification without
the primary gate detecting it? Include new config, red-team, test, MCP bridge,
provider adapter, evaluator, corpus, and contract changes.

Q5. Are historical v1-v5 artifacts or stale documentation capable of being
selected as a current prerequisite or misread as evidence? Check naming,
links, config references, and default CLI behavior.

Q6. Is the ability to run a primary itself separately authorized by the user,
or does a code path permit it solely because qualifications pass? Report this
as a governance gap if technical enforcement cannot prove user intent.

Required output:
- Create docs/feedback/claude_redteam_preprimary_audit_YYYYMMDD.md only.
- Begin with PASS / FAIL / INCONCLUSIVE for each Q1-Q6.
- Separate demonstrated defects from untested risks and from documentation
  drift.
- If no defect is found, state residual risks and the test coverage gap; do not
  claim that the system is safe.
- Add an Obsidian backlink section linking the MOC, contract, runner, provider
  adapter, evaluator, configs, and both qualification result artifacts. Give a
  one-sentence reason for each link.
- Do not commit.
```

## Why A New Session

The review must not inherit the implementation session's assumptions or a
previous agent's transcript. It may inspect only the declared canonical files
and immutable qualification artifacts, and it must leave the live experimental
surface untouched.

## Follow-Up Integration Rule

After the red team returns, a main agent must independently verify each cited
line and reproduce only local, non-provider tests before changing a frozen
surface. A report is evidence for a repair hypothesis, not permission to run
primary.

## Backlink Context

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Entry MOC]] identifies the
  current artifact graph.
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Qualification log]]
  records what the provider qualifications establish and what they do not.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Prere-registration]]
  is the experiment's claim and amendment authority.
