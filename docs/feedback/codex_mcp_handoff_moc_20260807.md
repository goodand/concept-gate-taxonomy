---
aliases:
  - Codex MCP Handoff MOC
tags:
  - doc/moc
  - stage/handoff
  - status/in-progress
---

# Codex MCP Handoff MOC

Entry MOC for the isolated Codex MCP provider qualification. Use this map
before interpreting a pilot result or changing a frozen experiment surface.

## Current State

- [[docs/feedback/session_retrospective_20260811_codex_retrieval_migration_and_canary|Codex retrieval migration and canary retrospective]]
  continues the Codex-only `C-Ixx` issue chain with the portable Obsidian
  retrieval migration, permission-lane reproductions, and the bounded canary
  interpretation. It does not import Claude Code's defect counters.
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Continuation log]] records
  issues, repeated failures, hypotheses, evidence, and the next repair sequence.
- [[docs/feedback/codex_handoff_continuation_prompt_20260807|Continuation prompt]]
  gives a cold-start Codex session the required reading order, gold boundary,
  and evidence-to-repair procedure.
- [[docs/feedback/handoff_continuation_prompt_template|Cross-workspace template]]
  is the reusable source and the zero-context entry contract for reaching this
  handoff's canonical sources from another workspace; instantiate it with the
  receiving workspace rather than reusing this experiment's absolute paths.
- [[docs/feedback/claude_redteam_preprimary_prompt_20260807|Claude pre-primary red-team prompt]]
  assigns an independent, no-live-run audit of qualification and primary gates.
- [[docs/feedback/claude_redteam_preprimary_reaudit_prompt_20260807|Claude Amendment 21 reaudit prompt]]
  asks a fresh session to repeat F1-F7 attacks against the ledger-bound v7/v2
  artifacts before any authorization decision.
- [[docs/feedback/handoff_reuse_harness_developer_20260806|Vault-harness handoff-reuse developer note]]
  (2026-08-06, session `owl-wt`, read-only observation of `.vault-harness`)
  records when and how `HANDOFF_REUSE_HARNESS_PREREGISTRATION.md` and its
  runner/evaluator first appeared in the protected upstream harness this
  experiment's `PREREGISTRATION.md` §0 cites and hash-pins. Direct-linked
  2026-08-07 per the orphan-taxonomy decision (in-scope, previously
  unlinked).
- [[docs/feedback/session_retrospective_20260807_handoff_tooling_redteam|Handoff repair-loop red-team retrospective]]
  documents I30-I39, including I38 — the empty AST meta-test defect this
  session re-verified as fixed
  ([[docs/feedback/redteam_handoff_repair_loop_20260806|redteam_handoff_repair_loop_20260806]]
  §6-7). Direct-linked 2026-08-07, same reason.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Prere-registration]]
  is the canonical statement of amendments and what each version may claim.
  **Worktree-qualified deliberately** — `concept-gate-owl-wt` has an
  unrelated same-named `PREREGISTRATION.md` under the identical relative
  path, and the unqualified form silently resolved there instead
  (2026-08-07 discovery, see
  [[notes/audits/vault/orphan-classification-methodology-2026-08-07|orphan
  audit]]).
- [[experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS|Provider adapters]]
  defines the OAuth-parent and single-tool boundary.
- [[docs/feedback/claude_redteam_preprimary_findings_20260807|Independent pre-primary findings]]
  demonstrated the forged one-cell qualification and authorization gap that
  caused the v7/v2 gate revision.
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 reaudit findings]]
  confirms A1-A10 and records residual risks R1-R4; it does not authorize
  primary.
- [[docs/feedback/claude_continuation_prompt_20260807|Claude current continuation prompt]]
  gives a new Claude Code session the latest R1-R4 scope, safety boundary, and
  recording order.
- [[docs/feedback/claude_questions_for_source_session_20260807|Questions and requests for the source session]]
  compiles the requests (R1/R2/attempt-ledger completion status, doc drift) and
  open judgment questions (approval identity, CLAUDE_CONFIG_DIR, DS07, mention
  channel, AST meta-test re-mutation) this audit chain surfaced but cannot
  answer itself; the 2026-08-07 `## 답변` section records the user's decisions
  on all seven, without deleting the original questions.
- [[docs/feedback/design_proposal_v8_v3_R1_R2_attempt_ledger_20260807|R1/R2/attempt-ledger design proposal]]
  is design-only (no diff applied to any file) for bundling R1, R2, and
  attempt-ledger terminal events into a future Codex v8 / Claude surface v3
  qualification; implementation still requires separate approval.
- [[docs/feedback/design_decision_mention_channel_and_stub_floor_20260807|Mention channel and stub-floor decision]]
  records the user's judgment on the repair-loop harness's open 경로 C / 구멍 7
  items; deferred to the next repair-loop version and confirmed out of the
  dynamic-controller frozen surface.
- [[docs/feedback/ds07_independent_curator_protocol_20260807|DS07 independent curator protocol]]
  designs the blind-judgment procedure for DS07 and explicitly disqualifies
  this reviewing session as curator, since it already read arm-level results.
- [[docs/HANDOFF_EXPERIMENT_KEY_ACHIEVEMENT_20260807|Key achievement synthesis]]
  states the session's main claim (recall-lift is not the achievement; the
  verifiable evidence/authority/approval contract is) and corrects two
  overstatements: the 0.688→1.000 progression is upstream design evidence, not
  this experiment's own live result, and claim exposure reached 1.0 across all
  8 cells while critical path recall did not (Claude v2 R_STATIC is 0.0).
- [[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|Evidence-bounded agency targets]]
  names the threat this harness exists to prevent (False-Justified Autonomy) and
  the acceptance conditions; its first four conditions are the implemented hard
  gate itself, and it records which ones are still unmet.
- [[docs/HANDOFF_EXPERIMENT_PURPOSE_HIERARCHY|Purpose hierarchy]]
  reconstructs what this experiment is a specialization of (is-a / part-of /
  depends-on) and records why protocol qualification does not inherit from
  retrieval performance; it is a concept map, not experimental authority.
- [[docs/feedback/session_synthesis_20260807_empty_guard_and_authorization_chain|Empty-guard and approval-bypass synthesis]]
  is the cross-session summary of the 12-time empty-guard pattern and the
  approval-bypass chain, with the invariants that replaced each human rule; it
  is a synthesis, not experimental authority.
- [[docs/feedback/claude_continuation_prompt_reply_20260807|Claude review reply prompt]]
  instructs the reviewing session to correct the three misplaced paths, record
  the R1 frozen-surface re-qualification cost, add the Claude provider red-team
  evidence, remove the duplicate template link, and separate discovery from
  trace validity.

Current gate state: Codex v7 and Claude surface v2 qualifications passed and
their artifact hashes match the external qualification ledger. These are
protocol qualifications, not performance results: Claude v2 includes an
`R_STATIC` retrieval miss and an `R_DYNAMIC` false-absence code. Primary is
technically blocked by the absent authorization file and remains unapproved.

## Evidence

- [[experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v5|v5 full pilot]]
  is a failed qualification, not an arm-effect result; `R_STATIC` is invalid.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v5_vehicle.json|v5 vehicle probe]]
  proves the MCP tool reached the host but is intentionally incomplete.
  **Extension- and worktree-qualified 2026-08-07** — the prior unqualified
  form had zero backlinks (dangling), per
  [[experiments/2026-08-07_handoff_dynamic_controller/ARTIFACT_MANIFEST|artifact manifest]]
  group B.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v6.json|v6 full pilot]]
  passes the stated Codex qualification matrix but is not an arm-effect
  result. Extension- and worktree-qualified 2026-08-07, same reason.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v1.json|Claude surface pilot]]
  passes the same `HD01 x 4` qualification boundary after Codex v6; it is also
  insufficient for an arm-effect estimate. Extension- and worktree-qualified
  2026-08-07, same reason.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json|Codex v7 qualification]]
  is the current ledger-bound Codex protocol qualification. Extension- and
  worktree-qualified 2026-08-07 — this is a canonical artifact
  (manifest group A) and the prior link was dangling.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json|Claude surface v2 qualification]]
  is the current ledger-bound Claude protocol qualification and preserves its
  outcome failures rather than treating qualification as performance.
  Extension- and worktree-qualified 2026-08-07, same reason.
- [[experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger.jsonl|Qualification ledger (canonical JSONL)]]
  is the external hash anchor that binds the current Codex v7 and Claude
  surface v2 qualification artifacts. It is non-Markdown canonical evidence:
  inspect it with the filesystem or `rg`, not `vault_read`, and do not treat a
  matching ledger row as human authorization for primary.
- [[experiments/2026-08-07_handoff_dynamic_controller/results/calibration|Calibration]]
  establishes evaluator sensitivity for the current frozen surface.
- [[experiments/2026-08-07_handoff_dynamic_controller/results/redteam_codex_mcp_isolation|MCP red-team]]
  establishes the current launch boundary checks for the Codex MCP surface.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/redteam_provider_isolation.json|Provider isolation red-team]]
  is a separate execution prerequisite: Claude surface v2 declares a
  `seatbelt-v2` sandbox policy, so the runner's preflight refuses that provider
  unless this artifact reports `hardened_profile_passed` with no frozen-surface
  drift. Its two recorded leaks are v1-historical and v1 has no eligible
  primary spec. Extension- and worktree-qualified 2026-08-07 — this is a
  frequently-needed diagnostic artifact (manifest group B) and the prior link
  was dangling.
- [[experiments/2026-08-07_handoff_dynamic_controller/ARTIFACT_MANIFEST|Phase C artifact manifest]]
  is the single entry point for the 27 historical/superseded config and pilot
  artifacts (manifest groups C-G) that are individually classified but not
  individually linked here — per
  [[notes/audits/vault/DESIGN_DECISION_orphan_taxonomy_and_worktree_qualified_links_20260807|the orphan-taxonomy decision]],
  "개별 분류 필요 ≠ 개별 Markdown wikilink 필요."

## Repair Surface

- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py|Live runner]]
  owns `LiveToolState`, static sequencing, host trace authority, and primary
  gates. **Worktree-qualified deliberately** — same cross-worktree collision
  as `PREREGISTRATION.md` above; `concept-gate-owl-wt` has its own unrelated
  `run_live_phase_c.py` at the identical relative path.
- [[experiments/2026-08-07_handoff_dynamic_controller/_providers.py|Provider adapter]]
  owns the Codex command and raw event allowlist.
- [[experiments/2026-08-07_handoff_dynamic_controller/live_subject_mcp.py|MCP bridge]]
  exposes only `handoff_action` and forwards to the host socket.
- [[experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py|Pre-primary regression tests]]
  reproduce matrix shrinking, artifact editing, missing authorization, and
  attempt-limit attacks without a provider call.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/phase_c_codex_mcp_v7_config.json|Codex v7 config]]
  is the next Codex qualification surface. Extension- and worktree-qualified
  2026-08-07 — canonical artifact (manifest group A), prior link was
  dangling.
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/phase_c_claude_mcp_surface_v2_config.json|Claude surface v2 config]]
  is the next cross-provider qualification surface after Codex v7. Extension-
  and worktree-qualified 2026-08-07, same reason.

## Rules

- Do not overwrite `results/live_pilot_*` artifacts.
- Do not treat MOC, tags, or navigation views as experimental authority.
- Read the selected Markdown evidence before changing a policy or claim.
- A new provider/static repair requires a new config, current red-team,
  calibration, tests, and a full qualification matrix.
- The current v7/v2 qualifications do not authorize primary. Require an
  explicit authorization artifact bound to their exact hashes and matrix.
