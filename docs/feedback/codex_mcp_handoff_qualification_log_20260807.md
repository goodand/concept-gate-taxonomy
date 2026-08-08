---
aliases:
  - Codex MCP Handoff Qualification
tags:
  - doc/feedback
  - stage/handoff
  - status/in-progress
---

# Codex MCP Handoff Qualification Log (2026-08-07)

## Scope And Status

### (0A) R1/R2/attempt-ledger — design approved, implementation not authorized

2026-08-07, user decision on
[[docs/feedback/claude_questions_for_source_session_20260807|questions for
the source session]]. Status of each item:

| Item | Issue | Status |
|---|---|---|
| R1 — per-cell ledger binding | score-only rewrite + ledger relink still passes primary gate | **design approved, implementation not authorized.** See [[docs/feedback/design_proposal_v8_v3_R1_R2_attempt_ledger_20260807]] |
| R2 — ledger matrix provenance | ledger arms/case_ids come from config declaration, not executed cells | **design approved, implementation not authorized.** Same document |
| C — attempt ledger terminal events | only `started` is recorded; completion/failure/interruption are indistinguishable | **design approved, implementation not authorized; required precondition before the first primary run.** Same document |

All three are bundled into a single next qualification surface — Codex v8 /
Claude surface v3 — rather than applied to the current v7/v2 artifacts, per
user decision: they share the same frozen surface, and applying them
separately would repeat paid re-qualification twice. No code, config,
qualification artifact, or ledger has been modified toward this — verified
`git status --short` shows none of `run_live_phase_c.py`, `_evaluator.py`,
`test_preprimary_gates.py`, or `results/` changed. Sequenced order: design →
bundle into v8/v3 → calibration → red-team → full local test → Codex v8
qualification → Claude surface v3 qualification → independent reaudit → only
then a primary-approval decision. The current v7/v2 state is not eligible for
primary until this sequence completes.

This log records the OAuth-parent / MCP-only Codex qualification work in
`experiments/2026-08-07_handoff_dynamic_controller`. It is a continuation
artifact for a cold-start agent, not a performance report. Do not run a
primary experiment from these observations.

Latest state: Codex v7 and Claude MCP-surface v2 `HD01 x 4` protocol
qualifications passed on the Amendment 21 frozen surface. Both artifacts are
bound to exact external qualification-ledger hashes and declare
`arm_effect_estimable=false`, `n_per_cell=1`. Claude v2 still records outcome
failures (`R_STATIC`: recall 0 with `R1/R2/T1`; `R_DYNAMIC`: `A1`), proving the
qualification/performance distinction is active. A primary dry-run is refused
because `PRIMARY_AUTHORIZATION.json` is absent. Primary remains unapproved.

## (1B) Amendment 21 Reaudit Feedback

Independent reaudit: [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Claude pre-primary reaudit]].
The reviewer used zero provider/MCP/network/paid calls, did not read hidden gold,
created no authorization or attempt ledger, and wrote only the linked review
document. The `/private/tmp` mutation copies were removed after the audit.

### A1-A10 Result

All ten attacks were `PASS` with demonstrated defect count `0`:

- A1: frozen primary config spec rejects one-cell matrix shrink, even when the
  copied ledger is also changed; all ten superseded configs fail closed.
- A2: one-byte qualification artifact edit fails the external ledger hash.
- A3: twelve independent field/ledger-rebinding combinations fail against the
  two independent anchors.
- A4: absent authorization stops before provider invocation and before attempt
  ledger creation.
- A5: six authorization mutations and the boolean `max_attempts` bypass fail;
  the well-formed fixture passes as the precision control.
- A6: changing output names cannot obtain a second claim for one authorization
  digest.
- A7: eight-process contention across five trials produced exactly one claim
  and one ledger row each time.
- A8: five test modules and v7/v2 configs are frozen; calibration, both
  red-teams, and both qualification artifacts report current drift `[]`.
- A9: both artifacts retain `arm_effect_estimable=false`, `n_per_cell=1`, and
  cell payload hashes; Claude v2 `R_STATIC` (`recall=0`, `R1/R2/T1`) and
  `R_DYNAMIC` (`A1`) remain visible and are not relabeled as PASS.
- A10: `PRIMARY_AUTHORIZATION.json` and `primary_attempt_ledger.jsonl` are
  absent at their exact real-results paths.

### Residual Risks R1-R4

These are not demonstrated F1-F7 defects, but the reaudit found them as open
design limits:

| Risk | Evidence/status | Follow-up |
|---|---|---|
| R1 score-only rewrite | Rewriting outcome metrics and recomputing the ledger row can pass; ledger is outside frozen surface and append-only is procedural | Consider ledger cell-level `judged_payload_sha256` and `full_hard_gate` commitments plus paired mutation tests |
| R2 ledger matrix provenance | Ledger matrix currently repeats config-declared values rather than independently recording observed execution values | Record and compare execution-derived cell keys and artifact result keys |
| R3 advisory lock boundary | `flock` passed 8-process x 5-trial contention, but is advisory | Treat the writer as trusted or add an OS/external lock authority if stronger guarantees are required |
| R4 attempt ledger mutation | Attempt ledger has no external signature or immutable replica | Preserve as audit evidence and do not treat it as proof of human identity or complete historical absence |

### Reaudit Claim Boundary

The four axes remain separate:

1. Qualification artifact integrity: conditional pass because R1 remains.
2. Protocol/trace compliance: pass for the audited artifacts.
3. Retrieval/outcome performance: not established; `n_per_cell=1` and
   `arm_effect_estimable=false` make arm-effect claims ineligible.
4. Human primary authorization: absent. Technical readiness does not authorize
   execution. `PRIMARY_AUTHORIZATION.json` is an auditable record, not
   cryptographic proof of human identity.

The reaudit's distinction is also relevant to cross-workspace handoff: a
backlink or MOC can establish document discovery while the emitted trace still
fails its schema. That state must be recorded as `partial discovery / trace
invalid`, not as evaluator PASS.

## (1C) Recording Completeness Audit

The reaudit was compared against the prior log and the original F1-F9 findings.
The following items were not previously recorded as separate actionable entries
and are now captured here:

| Omitted item | What was not recorded | Current classification |
|---|---|---|
| F8 historical artifact-kind drift | `live_pilot_attempt2`–`attempt9` carry historical `live-subject-primary` kind, and older passed Claude artifacts lack an explicit superseded marker | Documentation/provenance drift; current v7/v2 spec selection is fail-closed |
| F9 historical vehicle artifact | `live_pilot_codex_mcp_v5_vehicle.json` is `passed=true`, `n_runs=1`, but is intentionally not a qualification prerequisite | Historical navigation hazard; no current gate authority |
| A5 fixture shared-reference error | First authorization mutation appeared to pass because the test mutated the same `verified` dict object on both sides; `deepcopy` corrected the test and the independent mutation failed | Validation-process issue corrected during audit; future mutation fixtures must be independent |
| D1 stale provider documentation | `PROVIDER_ADAPTERS.md` still contains `91 passed` and old v2/v1 qualification order in its historical sections | Documentation drift, not current gate defect |
| D2 duplicate log numbering | The cold-start file list contains duplicate item numbers `7` and `8` | Documentation clarity drift |
| D3 under-described F4 | The log previously called arm-effect protection “controlled”; A9 shows it is a machine-enforced non-estimability field, not merely a convention | Documentation wording corrected by this entry; no code defect |
| D4 hard-gate visibility | Codex v7 `S_DYNAMIC` has `full_hard_gate=false` while `failure_codes=[]`; readers scanning only failure codes can misread it as clean | Reporting clarity risk; always read hard gate and state/next/stop accuracy together |

This table is a completeness record, not a claim that these historical or
documentation items authorize primary. The actual unresolved design risks remain
R1-R4 above.

## (1A) New Issues From Independent Pre-Primary Red Team

Canonical review: [[docs/feedback/claude_redteam_preprimary_findings_20260807|pre-primary findings]].

| Issue | Demonstrated mechanism | Resolution state |
|---|---|---|
| F1 matrix shrink | Artifact changed its own pilot matrix to one cell and passed | Resolved in code: matrix comes from frozen config spec |
| F2 artifact edit | Qualification content could change without an external digest | Resolved in code: append-only qualification ledger hash required |
| F3 weak default | CLI default selected historical v1 config | Resolved in code: `--config` required; absent specs fail closed |
| F4 arm-effect misuse | One-cell pilot exposed `R_STATIC` hard-gate 0 beside 1s | Resolved: machine-enforced non-estimability fields (`arm_effect_estimable=false`, `n_per_cell=1` on both v7/v2 artifacts). **This does not mean retrieval performance or arm effects are resolved** — only that the pilot cannot silently be read as a performance result |
| F5 approval gap | Qualification alone permitted primary; output names bypassed run count | Resolved in code: exact authorization + pre-call attempt ledger |
| F6 compliance conflation | Primary host-action miss could appear as retrieval failure | Resolved in reporting: separate `C5` execution code and judged-payload hash |
| F7 test drift | Test modules were outside frozen surface | Resolved: every `test_*.py` is frozen and mechanically checked |

No `PRIMARY_AUTHORIZATION.json` was created. The implementation must not be
interpreted as approval.

## (2A) Validation Of Amendment 21

- Local tests: `107 passed`; one pre-existing unknown `asyncio_mode` warning.
- New attack regressions: `10 passed`, including forged one-cell matrix,
  post-qualification edit, missing authorization, mismatched matrix, and
  exhausted attempt allowance.
- Evaluator calibration: positive `8/8`, negative `58/58`, clean judge agreed.
- Codex MCP red-team: `8/8`.
- Provider isolation: 33 probes; hardened v2 leaks `0`. Historical v1 home
  transcript leaks remain documented and v1 has no eligible primary spec.
- Live qualification calls after Amendment 21: Codex v7 `4`, Claude surface
  v2 `4`; primary calls `0`.
- Qualification ledger: exactly two entries; each stored SHA-256 matches its
  current artifact.
- Primary dry-run: refused before provider invocation with `explicit
  authorization file is missing`; no attempt ledger was created.

## (3A) Exact Next Sequence

1. Do not create a primary authorization file.
2. Track R1-R4 as open limitations; do not silently upgrade conditional
   integrity to full provenance.
3. Stop and request explicit user approval. Only then may a separately created
   `PRIMARY_AUTHORIZATION.json` bind exact config, qualification hashes,
   matrix, and `max_attempts`.

## (1) New Issues In This Session

### N1. OAuth Is Available Only When The Codex Parent Is Not Seatbelt-Denied

**Problem.** The historical Codex Seatbelt-v2 design denied all `~/.codex`.
That denied both prior transcript material and the Codex binary/OAuth state.
The provider failed before a subject could act. Allowing an auth-file exception
would also expose it to model-issued Bash, which is unacceptable.

**Resolution status.** Resolved architecturally for the current provider:
OAuth remains with the Codex parent; the evaluated model receives no Bash or
native discovery tools. It receives only the `handoff_action` stdio MCP tool.

**Evidence.**

- [`_providers.py`](../../experiments/2026-08-07_handoff_dynamic_controller/_providers.py)
  disables `shell_tool`, `unified_exec`, browser, apps, computer use, code
  mode, image generation, and multi-agent features.
- [`live_subject_mcp.py`](../../experiments/2026-08-07_handoff_dynamic_controller/live_subject_mcp.py)
  exports exactly one MCP tool and no resources or prompts.
- v5 raw event summaries contain only `mcp_tool_call` for `handoff_action` and
  `agent_message`; no `session_id` or `thread_id` remains in saved artifacts.

### N2. MCP Child Did Not Inherit The Disposable Host Socket Path

**Problem.** The first local FastMCP stdio smoke launched the bridge but the
MCP child did not inherit `HANDOFF_LIVE_TOOL_SOCKET`; `handoff_action` failed
with “not set.” Parent-process environment inheritance is not a valid
assumption for this transport.

**Resolution status.** Resolved.

**Resolution.** `codex_mcp_command()` supplies a server-specific
`mcp_servers.handoff.env` override containing the dynamically allocated Unix
socket path. The bridge reuses the existing public client's `request()`
protocol, so host-side action validation and trace ownership are unchanged.

**Evidence.** A local FastMCP stdio smoke listed exactly
`['handoff_action']` and recorded a host `reformulate_query` action. The v5
vehicle probe subsequently recorded 9 host actions and 4 reads.

### N3. Codex MCP Calls Were Cancelled Before Reaching The Host

**Problem.** v1 and v3 completed model calls but every MCP event ended in
`user cancelled MCP tool call`; all host action counts were zero. This is a
vehicle/approval failure, not retrieval failure.

**Resolution status.** Resolved in v5.

**Resolution.** Codex required `--approve-for-me` for noninteractive MCP
calls. That flag cannot coexist with explicit `--sandbox`; v5 therefore uses
Codex automatic-review mode without an explicit sandbox flag while retaining
the native-tool disable set and disposable `subject/` cwd.

**Evidence.**

- v1: four cells, all calls cancelled, `0` host actions.
- v3: four cells, all calls cancelled, `0` host actions despite
  `approval_policy="never"`.
- v5 vehicle: host actions `9`, reads `4`, accepted terminal action `answer`,
  no invalid-run code, only the named MCP tool in raw events.

### N4. Codex CLI Option Placement/Compatibility Was Assumed Rather Than Probed

**Problem.** `--ask-for-approval` is a top-level Codex option, not a `codex
exec` option. v2 therefore exited before model invocation. v4 then showed that
`--approve-for-me` and explicit `--sandbox` are mutually exclusive.

**Resolution status.** Resolved for the launch contract; retain both failed
artifacts as evidence.

**Resolution.** v3 changed the approval preference to a valid config override
(`-c approval_policy="never"`). v5 uses the parser-valid combination
`--approve-for-me` with no explicit `--sandbox`. Parser smokes and red-team
assertions now cover this exact command shape.

**Evidence.** `codex exec -c 'approval_policy="never"' --help` and
`codex exec --approve-for-me -c 'approval_policy="never"' --help` both parse.
The focused provider test asserts the no-bypass/no-explicit-sandbox v5 command.

### N5. Historical: Full Codex Qualification Failed in v5 `R_STATIC`

**Problem.** In v5, `R_STATIC` made host-observed actions
`search -> expand_candidates -> read_candidate -> follow_link`, then attempted
an action outside the static recovery sequence. The host required the next
action to be `read_candidate`; later follow/finish attempts became `V1`.

**Resolution status.** Resolved in v6 by making the post-follow read a
deterministic host-provided `static_next` transition. The gate was not lowered.

**Evidence.**

- v5 isolated an invalid static action; v6 returns the exact next required
  `read_candidate` path after follow and keeps paired negative rejection tests.
- v6 Codex qualification has all four cells valid with host compliance and
  critical-path recall `1`.
- Claude MCP-surface v1 independently re-qualified all four cells on the same
  frozen surface. Its `R_STATIC` full hard gate is `0` but it is valid, has
  host compliance `1`, and critical-path recall `1`; it is not a protocol or
  transport failure.

## (2) Repeated Issues And Updated Counts

| Pattern | Current-session reproductions | Current interpretation | Status |
|---|---:|---|---|
| MCP call fails to reach host | 2 live pilot surfaces (v1, v3), plus 1 local smoke before env fix | Transport/approval vehicle failure, not retrieval quality | Resolved in v5 |
| CLI launch contract rejected before model work | 2 live surfaces (v2 option placement, v4 incompatible flags) | Parser-contract assumption was not tested at the exact subcommand level | Resolved in v5, parser smoke retained |
| Full qualification blocked by one invalid cell | 1 current full surface (v5 `R_STATIC`) | Static continuation was ambiguous; v6 host `static_next` made it deterministic | Resolved in v6 |
| Partial result could be mistaken for a full qualification | 1 newly identified gate gap | `--arm` overrides can make a passing one-cell artifact unless matrix coverage is checked | Resolved by primary matrix gate |
| Source/evaluator drift after provider changes | Recurred after each provider surface revision | A calibration result is valid only for the exact frozen inputs | Controlled, not eliminated: latest calibration is required |

The older Codex Seatbelt-v2 OAuth launch failure is a predecessor of N1, not
counted as a new MCP surface run here. Keep it as the reason the architecture
changed, not as performance evidence.

## (3) Issues With Resolution Evidence

1. **Socket environment propagation:** resolved by server-specific MCP env;
   direct stdio smoke and v5 host actions confirm it.
2. **Native-tool containment:** resolved for the observed event surface;
   v5 event summaries contain only `handoff_action`, and the red-team rejects
   command/non-handoff MCP events.
3. **Saved provider-session identifiers:** resolved for current saved raw
   artifacts; sanitizer removes `session_id` and `thread_id`, and v5 artifacts
   have neither string.
4. **Partial qualification accepted by primary:** resolved in code; primary
   now requires `n_runs == len(pilot.arms) * len(pilot.case_ids)` and per-arm
   coverage. A one-cell vehicle probe cannot satisfy it.
5. **MCP approval cancellation:** resolved operationally in the v5 vehicle
   probe, then independently confirmed in all four v5 arms by nonzero host
   action counts.

## (4) Resolution State By Issue

| Issue | State | What must not be inferred |
|---|---|---|
| OAuth-parent / MCP-only separation | Resolved for this adapter | It does not prove the parent process is OS-isolated from the user account |
| MCP socket transport | Resolved | It does not prove static or dynamic retrieval quality |
| Approval cancellation | Resolved for v5 | It does not authorize primary execution |
| Command parser compatibility | Resolved for v5 launch shape | It does not validate future Codex CLI versions |
| Raw event allowlist and ID sanitation | Resolved for observed v5 events | It is not a proof against an unreported future event type |
| `R_STATIC` action sequence | Resolved in v6 | Do not pool the single-case qualification arms or claim an arm effect |
| Cross-provider qualification | Resolved for current frozen surface | It does not authorize primary execution |

## (5) Problem Definitions For Repeated, Evidenced Patterns

### P1. Vehicle Failure Is Being Misread as Retrieval Failure

**Definition.** A model may emit tool-call intents while no host action is
accepted. If scoring sees only missing reads/claims, this can be incorrectly
reported as poor retrieval. The actual failure is the execution vehicle:
environment propagation, approval policy, CLI parse contract, or transport.

**Observable discriminator.** Compare all three channels:

1. raw provider event indicates a call attempt;
2. host-owned `trace.actions` records accepted/rejected actions; and
3. final trace validity/terminal action.

v1/v3 had (1) but not (2); v5 vehicle had all three. Therefore v1/v3 are not
retrieval observations.

### P2. A “Passing Pilot” Is Not Sufficient if Its Matrix Is Incomplete

**Definition.** A runner that permits an arm override can write a passing
one-cell artifact. If primary checks only `qualification.passed`, a partial
probe can satisfy a full-pilot prerequisite.

**Observable discriminator.** The artifact must cover every declared pilot
case and arm exactly once: `n_runs`, per-arm keys, and per-arm counts must
match the frozen config.

### P3. Static Workflow Is a Protocol, Not Advice

**Definition.** The static arm is a finite host-enforced action sequence. A
model prompt that describes the sequence but leaves branch behavior ambiguous
can still generate a valid-looking answer after a host `V1`. It is not enough
that the model used the right tools; the ordered transition contract must be
followed.

**Observable discriminator.** Read the host action list and the exact
`strict_static` expected action in the rejection message. In v5 `R_STATIC`,
the sequence was valid through its first follow; the later action was not the
required `read_candidate` recovery/continuation.

## (6) Hypotheses And Validation Methods Used for Resolution Decisions

| Hypothesis | Test / falsifier | Result | Decision |
|---|---|---|---|
| The MCP server can forward one action without exposing corpus files | FastMCP stdio smoke with a disposable socket and `list_tools()` | Only `handoff_action`; host search recorded | Accept narrow bridge |
| Parent OAuth can coexist with no model shell | Command feature disable set + raw-event allowlist | v5 only named MCP tool observed; no session/thread IDs saved | Accept provisionally for this CLI version |
| `approval_policy="never"` alone prevents MCP cancellation | v3 `HD01 x 4` | Falsified: all calls cancelled | Do not treat config preference as tool approval |
| `--approve-for-me` with explicit sandbox is valid | v4 one-cell vehicle | Falsified by parser exit 2 | Split flags; retain failed artifact |
| `--approve-for-me` without explicit sandbox permits the narrow MCP call | v5 one-cell vehicle | Confirmed: 9 host actions, 4 reads, accepted finish | Expand to full pilot |
| v5 full transport works across all arms | full `HD01 x 4` host traces | Confirmed: every main/R subagent path had host actions | Transport qualified, arm qualification not yet passed |
| Passing one-cell probe cannot gate primary | unit test plus `_assert_primary_qualifications()` checks | Confirmed by 95-test suite | Keep matrix gate |
| Current evaluator still detects intended positives/negatives after edits | `run_calibration.py` | positive 8/8, negative 58/58, clean judge agreement | Accept latest frozen surface |

## (7) Concrete Repair Procedure

### A. Preserve Current Evidence

1. Do not edit or overwrite `live_pilot_codex_mcp_v1.json` through
   `live_pilot_codex_mcp_v5.json`, or either vehicle artifact.
2. Do not reinterpret v1-v4 as retrieval scores. They are transport/parser
   failures.
3. Keep v5 as a failed full qualification: it proves transport, not a valid
   static-vs-dynamic comparison.

### B. Historical Repair: `R_STATIC` Without Metric Fitting

1. Read `_prompt()` and `LiveToolState.static_steps` in
   [`run_live_phase_c.py`](../../experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py), then
   read the v5 `R_STATIC` raw event and host action list.
2. Form a falsifiable explanation for why the model chose an action other than
   the expected `read_candidate` after the accepted follow. Possible causes to
   distinguish are: prompt wording, no newly surfaced candidate, or an
   incorrect static-state transition for the R arm. Do not assume one.
3. Add a deterministic host/controller test that reproduces the exact action
   prefix and asserts the intended next action. Add a paired negative test that
   still rejects an extra follow/finish.
4. Make the smallest contract-preserving change. Prefer returning the exact
   next required action/reason in the host response or making the prompt name
   the same concrete candidate transition. Do not relax `V1` merely because a
   pilot failed.
5. Create a new `phase_c_codex_mcp_v6_config.json` and a new result name.
   Never mutate v5 config/result or reuse it as a qualification prerequisite.

### C. Completed: Re-qualify Codex

1. Add every new source/config/red-team file to `FROZEN_SURFACE_FILES`.
2. Run `python3 -B redteam_codex_mcp_isolation.py` and require a current,
   passing report.
3. Run `python3 -B run_calibration.py` and require positive `8/8`, negative
   `58/58`, clean-judge agreement.
4. Run the focused provider/static tests and then the complete local suite.
5. Run a new `HD01 x 4` Codex pilot. Require: no invalid cells, host action
   compliance for all main cells and both R subagents, no forbidden raw event,
   no transient IDs, and full pilot matrix coverage.
6. Record a fresh result artifact; do not overwrite v5.

### D. Completed: Re-qualify Claude After Codex Passes

1. `phase_c_claude_mcp_surface_config.json` qualification passed on the same
   current frozen surface: [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v1.json|Claude result]].
2. Both provider artifacts satisfy their `HD01 x 4` qualification matrix.
3. Stop. Request explicit user approval before any primary run.

## Files A Cold-Start Agent Must Read First

1. [`codex_mcp_handoff_qualification_log_20260807.md`](codex_mcp_handoff_qualification_log_20260807.md)
2. [`PREREGISTRATION.md`](../../experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md)
3. [`PROVIDER_ADAPTERS.md`](../../experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS.md)
4. [`run_live_phase_c.py`](../../experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py)
5. [`_providers.py`](../../experiments/2026-08-07_handoff_dynamic_controller/_providers.py)
6. [`live_subject_mcp.py`](../../experiments/2026-08-07_handoff_dynamic_controller/live_subject_mcp.py)
7. [[docs/feedback/codex_handoff_continuation_prompt_20260807|Continuation prompt]]
   for the reusable new-session instructions and gold-set boundary.
8. [[docs/feedback/claude_redteam_preprimary_prompt_20260807|Claude red-team prompt]]
   for the pending independent audit before any primary approval decision.
9. [`live_pilot_codex_mcp_v5.json`](../../experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v5.json)
10. [`redteam_codex_mcp_isolation.json`](../../experiments/2026-08-07_handoff_dynamic_controller/results/redteam_codex_mcp_isolation.json)
11. [`calibration.json`](../../experiments/2026-08-07_handoff_dynamic_controller/results/calibration.json)

## Obsidian Backlink Map

Use this note as the entry point. These wikilinks create a graph path from the
handoff log to the experiment contract, provider boundary, live runner, and
immutable observations:

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Phase C preregistration]]
- [[experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS|Provider adapter contract]]
- [[experiments/2026-08-07_handoff_dynamic_controller/RESULTS|Experiment results overview]]
- [[experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v5|Failed v5 full qualification]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v5_vehicle.json|Passing v5 transport vehicle probe]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v6.json|Passing v6 Codex qualification]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v1.json|Passing Claude MCP-surface qualification]]

Implementation files are not source authority for experimental claims, but a
repairing agent must inspect them after reading the contract and result:

- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py|Live runner and static transition]]
- [[experiments/2026-08-07_handoff_dynamic_controller/_providers.py|Codex provider boundary]]
- [[experiments/2026-08-07_handoff_dynamic_controller/live_subject_mcp.py|Single MCP bridge]]
- [[experiments/2026-08-07_handoff_dynamic_controller/redteam_codex_mcp_isolation.py|Codex MCP red-team]]

## Verification Snapshot At Log Creation

- Red-team for v6 launch surface: `8/8` checks passed.
- Evaluator calibration: positives `8/8`, negatives `58/58`, clean judge
  agreed.
- Local test suite: `97 passed` (one unrelated pytest configuration warning).
- FastMCP local stdio smoke: one listed tool and one host-recorded action.
- v5 vehicle probe: passed, but intentionally ineligible for primary gating.
- v5 full qualification: failed only at `R_STATIC`; do not claim arm effects.
- v6 full qualification: passed the stated validity/compliance criteria; still
  do not infer arm effects from one case and one replicate.
- Claude MCP-surface v1: passed the same validity/compliance criteria after
  v6; primary is still unapproved and no arm effect may be inferred.
