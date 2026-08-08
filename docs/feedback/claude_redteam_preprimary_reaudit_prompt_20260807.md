---
aliases:
  - Claude Pre-Primary Reaudit Prompt
tags:
  - doc/prompt
  - stage/handoff
  - status/pending-review
---

# Claude Red-Team Prompt: Amendment 21 Reaudit

Paste this into a completely new Claude Code session. Do not resume the
session that produced the original F1-F9 findings.

```text
Act as an independent red-team reviewer in:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

Mission: verify whether Amendment 21 actually closes F1-F7 from
docs/feedback/claude_redteam_preprimary_findings_20260807.md. This is a local
code/artifact audit. Do not run a pilot, primary, provider CLI, MCP, network
call, or paid model call. Do not create PRIMARY_AUTHORIZATION.json. Do not
read hidden_gold/gold.json or home-directory transcripts. Do not modify code,
config, result artifacts, ledgers, corpus, evaluator, or gold.

You may write exactly one new file:
docs/feedback/claude_redteam_preprimary_reaudit_20260807.md

Read these canonical inputs:
1. docs/feedback/claude_redteam_preprimary_findings_20260807.md
2. experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md
3. experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py
4. experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py
5. experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py
6. experiments/2026-08-07_handoff_dynamic_controller/phase_c_codex_mcp_v7_config.json
7. experiments/2026-08-07_handoff_dynamic_controller/phase_c_claude_mcp_surface_v2_config.json
8. experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger.jsonl
9. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json
10. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json

Permitted execution: local tests or in-memory/private-tmp mutation probes that
do not call a provider and do not write inside the experiment, except the one
review document.

Required attacks:
A1. Repeat the F1 one-cell matrix shrink. It must now fail against matrix data
owned by the frozen primary config spec, not artifact self-report.
A2. Edit one harmless artifact byte in a private-tmp copy while preserving all
internal fields. It must fail the external qualification ledger digest.
A3. Replace config_file/config_sha256/provider/sandbox independently and show
which external anchor rejects each change.
A4. Invoke the primary gate with the two genuine v7/v2 qualifications and no
authorization file. It must stop before any provider or attempt-ledger write.
A5. With private-tmp fixtures only, test wrong authorization config hash,
qualification hash, matrix, empty authorized_by, and max_attempts=0.
A6. Test attempt exhaustion with output-name changes. The same authorization
digest must not obtain a second attempt.
A7. Inspect `_claim_primary_attempt` for TOCTOU. Verify count+append occur under
one exclusive lock. If feasible, use two local processes against a temp ledger
and prove at most one claim succeeds for max_attempts=1.
A8. Verify every test_*.py and v7/v2 config is frozen and current calibration
and both red-team artifacts match the same surface.
A9. Confirm both new qualification artifacts declare
arm_effect_estimable=false and n_per_cell=1. Also confirm Claude outcome
failures remain visible; qualification must not erase or relabel them as PASS.
A10. Check that no PRIMARY_AUTHORIZATION.json or primary_attempt_ledger.jsonl
exists in the real results directory.

For every item, report PASS / FAIL / INCONCLUSIVE, exact file:line evidence,
the executed non-gold reproduction, and residual risk. Separate:
- protocol qualification;
- retrieval/outcome performance;
- trace-schema validity;
- human authorization.

Do not call the system safe merely because tests pass. In particular, state
that a local authorization file is auditable evidence, not cryptographic proof
of human identity. Do not commit.
```

## Backlinks

- [[docs/feedback/claude_redteam_preprimary_findings_20260807|Original findings]]
  define the attacks this reaudit must repeat.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Amendment 21 contract]]
  records the frozen repair claims.
- [[experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py|Regression suite]]
  is implementation evidence, not a substitute for independent mutation.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json|Codex v7 artifact]]
  and [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json|Claude v2 artifact]]
  are the exact ledger-bound qualification subjects.
