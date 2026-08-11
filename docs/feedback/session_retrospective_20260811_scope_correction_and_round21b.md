# Codex Session Self-Retrospective — Scope, Attribution, and Verification

- Date: 2026-08-11
- Subject: issues encountered or caused by **this Codex session**
- Entry point: [[../HANDOFF_20260810_primary_blocked]]
- Related Codex review: [[external_review_round21_20260811_reviewer_launcher_and_runtime]]
- Claude Code's Round 21b response is evidence read by Codex, not a Codex-owned issue log:
  [[plan_round21b_audit_path_bypasses_the_launcher]]

## Boundary and numbering

The previous draft of this file was wrong. It mostly catalogued defects implemented and
repaired by Claude Code and continued the project's `I113...` numbering. The user requested
a retrospective of **Codex's own work in the current session**. That attribution error is
itself recorded below as `C-I03`.

This document therefore uses the independent `C-Ixx` namespace. Project defects, Claude Code
implementation defects, and Codex review defects must not share a counter. They may be linked
as evidence, but they are not the same author's failure history.

The core experiment is limited to two questions:

1. Can a zero-context agent find a handoff and related documents and accurately reconstruct
   current state, evidence, blockers, prohibited actions, completion conditions, and next
   action?
2. Do static versus dynamic search workflows and retrieval-subagent absence versus presence
   change search performance?

## Evidence boundary

- This Codex session did not call a provider/model, MCP subject, network service, or paid API.
- This Codex session did not read `hidden_gold/gold.json`.
- No experiment code, config, result artifact, or ledger was edited.
- Codex directly inspected the current worktree, commit history, Round 21 review, Round 21b
  plan, handoff, and prior retrospective counts.
- Codex reran the current experiment suite twice. Both runs passed; the second, with skip
  reasons enabled, returned `310 passed, 1 skipped`. The skip was
  `test_safety_audit.py:867: miniature spec runs without provenance`.
- Earlier Codex execution had observed `274 passed, 20 failed, 1 skipped` in a managed parent
  sandbox and `294 passed, 1 skipped` with host permission. That historical result is retained
  as an environment-dependent observation, not treated as the current checkout's result.

## (1) New Codex issues — C-I01 through C-I09

| ID | Codex issue | Concrete occurrence | Immediate impact |
|---|---|---|---|
| **C-I01** | **Research scope expansion.** Codex described the target as a broad secure evaluation/provenance platform rather than the two retrieval questions | The research-agent prompt and subsequent reviews included reviewer isolation, HMAC receipts, ledger security, supply-chain identity, and release attestation as if they were coequal research objectives | Search experiment completion was obscured by support-harness work |
| **C-I02** | **Premature blocker judgment.** Codex said safety-audit F1-F3 had to be fixed before a live canary | Those defects can invalidate a blind safety headline, but they do not change handoff-file Recall, host-recorded reads, state reconstruction, or the static/dynamic × subagent comparison | Codex recommended postponing the first evidence-producing retrieval canary for a noncausal reason |
| **C-I03** | **Wrong subject of this retrospective.** Codex initially logged Claude Code/project defects instead of Codex's own issues | The first draft continued project IDs `I113-I124`, imported Round 21b implementation defects, and treated them as the requested “current session issues” | The log would have concealed Codex's actual mistakes and falsely attributed other-agent work |
| **C-I04** | **Invalid recurrence accounting.** Codex imported cumulative counts from Claude/project retrospectives as if they measured Codex behavior | The first draft continued counts such as helper-wiring 8→10 and self-modification regression 10→12 | Pattern frequency and ownership would have been statistically meaningless |
| **C-I05** | **Stale workspace assumption risk.** The carried session summary described the tree around `fb69fbb`, but another agent had advanced it to `3a28132` with Round 21b repairs | Codex re-ran `git log`, read the new plan and handoff, and found commits `ba50236..3a28132` before finalizing the log | Without re-reading, Codex would have reported resolved F1/F2 as current blockers |
| **C-I06** | **Environment-sensitive verification result.** Identical test intent produced different outcomes depending on parent sandbox permissions and later checkout state | Historical managed run: 20 Seatbelt/socket failures; historical host run: all passed; current Codex run: `310 passed, 1 skipped` | A bare “tests pass/fail” statement could be mistaken for a code verdict when it was partly an environment verdict |
| **C-I07** | **Unverified external precedent intake.** Codex received benchmark names and numerical/descriptive claims without direct primary-source links | Agent Retrieval Bench, ContextBench, SWE-Explore, LongMemEval-family, ClawArena-Team, and TRAJECT-Bench were supplied by another search agent | Treating them as verified evidence would contaminate experiment design with possibly wrong names, numbers, or interpretations |
| **C-I08** | **Review depth displaced vertical execution.** Codex repeatedly produced detailed critiques of the audit harness while the user wanted a working end-to-end retrieval experiment | Multiple review rounds focused on increasingly narrow reviewer/audit/receipt defects; the user explicitly questioned whether troubleshooting was consuming too many resources | More was learned about the evaluator than about whether the retrieval workflow works on a real subject |
| **C-I09** | **Requirement interpretation was not checked before a large write.** The phrase “현재 세션” was interpreted as “current project history” despite the user's reference to prior Claude Code logs | Codex wrote a long first draft before confirming that the requested owner was Codex | Rework was required and another misleading artifact briefly existed in the worktree |

## (2) Repeated Codex issues and increased recurrence counts

Only occurrences attributable to Codex are counted here. Counts are lower bounds based on
observable outputs in this conversation; they do not import Claude Code's counters.

| Codex pattern | Prior observable occurrences in this session | New occurrence | Current lower-bound count | Evidence |
|---|---:|---|---:|---|
| **C-P1 Scope expansion / overintervention** | 2 | C-I03's first draft repeated the expansion | **3** | Overcomplex research-agent target; audit defects treated as retrieval blockers; first retrospective again centered the whole harness |
| **C-P2 Premature blocking before causal mapping** | 1 | The first retrospective repeated the same blocker classification before user correction | **2** | Round 21 verdict and the initial log both said support-harness defects should precede the retrieval canary |
| **C-P3 Attribution boundary blur** | 1 | C-I03/C-I04 | **2** | External search-agent output arrived without primary links; then Claude/project defects and counters were imported into a Codex self-log |
| **C-P4 Review-before-E2E bias** | at least 2 review cycles | C-I08 continued the pattern | **at least 3** | Successive detailed reviews produced more hardening tasks while the 1×1 retrieval canary remained unrun |
| **C-P5 Current-state assumption without immediate refresh** | 0 confirmed earlier in this subtask | C-I05 | **1** | Session summary lagged behind another agent's Round 21b commits. This was caught before final reporting and is not yet a repeated pattern |
| **C-P6 Large output before intent validation** | 0 explicitly counted | C-I09 | **1** | The first long retrospective was written against the wrong subject. This is new, not yet repeated |

### What increased most materially

`C-P1` reached at least three occurrences and `C-P4` reached at least three review cycles. The
two reinforce each other:

```text
scope expands
  -> more components appear safety-critical
  -> more findings are classified as blockers
  -> E2E evidence is delayed
  -> uncertainty remains
  -> another broad review appears necessary
```

This loop is the primary Codex process defect in the current session.

## (3) Codex issues with resolution evidence

| Issue | Resolution evidence | Strength of evidence | Residual limit |
|---|---|---|---|
| C-I01 | User restated the two research questions; Codex rewrote the scope at the top of this log and amended the Round 21 review | Direct requirement correction | A document alone does not ensure future reviews obey the scope |
| C-I02 | Each Round 21 finding was mapped to the data path for retrieval outcomes versus safety publication | Causal-path analysis shows no effect on retrieval Recall or state reconstruction | A future canary can still expose a different causal blocker |
| C-I03 | The wrong project-wide draft was deleted and replaced by this Codex-only log before completion | Direct artifact correction; no misleading second file remains | The git diff must still be checked to ensure no fragments of the wrong attribution remain |
| C-I04 | Counters were reset to the `C-Ixx`/`C-Px` namespace and only observable Codex occurrences were counted | Ownership is explicit and auditable | Counts are lower bounds because the entire historical transcript was not mechanically classified |
| C-I05 | `git log -8`, current handoff, Round 21b plan, and current status were read after detecting the mismatch | Direct current-worktree verification | Another concurrent agent could still change the tree after the check |
| C-I06 | Current suite rerun twice; second run included `-rs` and identified the exact skip | Direct local execution at `3a28132` | It does not reproduce the earlier blocked parent sandbox and is not a provider canary |
| C-I07 | External candidates are explicitly marked unverified and excluded from numerical evidence | Correct evidence classification | Primary-source verification remains undone |
| C-I09 | User correction was accepted immediately and the draft was replaced rather than defended | Direct correction | Prevention requires a pre-write ownership check, not just willingness to repair |

## (4) Codex issue resolution status

| Status | Issues | Reason |
|---|---|---|
| **Resolved in the current artifact** | C-I03, C-I04 | Wrong attribution and invalid counters were removed from this log |
| **Resolved as a decision, mechanism still needed** | C-I01, C-I02, C-I09 | Scope and blocker rules are corrected, but future compliance depends on using the procedure in section (7) |
| **Diagnosed and bounded** | C-I05, C-I06, C-I07 | Current state, environment limit, and source-verification boundary are explicit |
| **Not yet resolved** | C-I08 | The real 1×1 retrieval canary has not been executed in this Codex session; review displacement ends only when vertical evidence is produced |

### Chained status from (1) and (2)

1. `C-I01` expanded scope.
2. Expanded scope made `C-I02`'s premature blocker judgment plausible.
3. That judgment fed `C-I08`, repeated review instead of vertical execution.
4. The same scope error then caused `C-I03`, the wrong retrospective subject.
5. `C-I03` imported alien counters, producing `C-I04`.
6. User correction exposed the chain; replacing the artifact resolves the attribution output,
   but only the canary-first procedure can prevent recurrence.

## (5) Problem definitions for repeated, evidence-backed Codex issues

### Problem A — Scope expansion turns support mechanisms into research objectives

**Issues:** C-I01, C-I02, C-I08.  
**Repeated pattern:** C-P1 and C-P4.

Codex did not merely add implementation detail. It changed the implicit objective function:

```text
Requested objective:
  maximize accurate handoff retrieval and state reconstruction
  compare static/dynamic and subagent/no-subagent workflows

Codex-implied objective:
  build a secure, provenance-complete, independently auditable agent evaluation platform
```

The second objective includes the first but is much harder. Optimizing it before the first
canary makes every auxiliary weakness look blocking. The concrete harm is not verbosity; it
is delayed evidence and a distorted priority order.

### Problem B — Severity inside a subsystem was confused with causal relevance to the experiment

**Issues:** C-I02.  
**Repeated pattern:** C-P2.

The Round 21 launcher bypass was legitimately High for a claim that labels came from an
isolated reviewer. Codex incorrectly transferred that severity to the retrieval canary. A
defect can be severe in component `A` and irrelevant to outcome `B`.

Formal distinction:

```text
subsystem severity = impact if that subsystem's claim is consumed
experiment blocker = can alter a primary outcome, arm comparability, or run validity
```

Without naming the consumed outcome, “High” is insufficient to block an experiment.

### Problem C — Evidence and issue ownership were not kept separate

**Issues:** C-I03, C-I04, C-I07.  
**Repeated pattern:** C-P3.

Codex had three different kinds of material:

1. defects Codex itself caused or encountered;
2. defects Claude Code implemented and repaired;
3. claims supplied by an external research agent.

The first draft merged all three into one current-session counter. This breaks recurrence
analysis because author, environment, verification level, and remediation owner differ.
Evidence can cross boundaries; failure counts cannot.

### Problem D — Review can become a substitute for the observation it is meant to protect

**Issues:** C-I08, supported by C-I01/C-I02.  
**Repeated pattern:** C-P4.

Detailed review lowers local uncertainty about code but does not answer whether a real
zero-context agent retrieves the needed documents. Once the walking skeleton exists, another
review has lower information gain than one small real run unless a known defect can invalidate
that run.

### Problem E — A session summary is a hint, not current workspace authority

**Issues:** C-I05, C-I06.

The conversation summary correctly described an earlier point, but another agent committed
Round 21b before Codex finalized this task. Similarly, a test result is bound to a checkout and
permission environment. Both are temporal evidence. Codex must refresh current authority
before turning them into present-tense claims.

## (6) Hypotheses and verification methods used by Codex

### H1 — A finding is a retrieval-canary blocker only if it reaches a core outcome

- **Hypothesis:** safety-audit receipt defects do not invalidate a retrieval-only canary when
  the canary's scored outputs are host-recorded searches, reads, required-file Recall, and
  state reconstruction.
- **Method:** trace each finding forward to the scored outputs.
- **Falsification criterion:** identify a path by which missing receipt verification changes
  retrieved files, host trace, state answer, invalid-run classification, or arm comparison.
- **Observed result:** no such path was found. The defects affect a later safety headline.
- **Judgment:** C-I02 is resolved as a decision; the previous blocker verdict is superseded.

### H2 — The requested retrospective must survive removal of all other-agent defects

- **Hypothesis:** a valid Codex self-retrospective remains meaningful if every Claude Code
  implementation finding is removed.
- **Method:** classify each row by actor: `Codex-caused`, `Codex-encountered`,
  `Claude-implemented`, or `external-unverified`.
- **Falsification criterion:** if a row only describes what Claude Code's code did and no
  Codex decision, verification limit, or process error, it does not belong in section (1).
- **Observed result:** the first draft failed this test; this replacement passes by using the
  `C-Ixx` namespace and actor-specific descriptions.

### H3 — Current state must be re-read after any evidence of concurrent work

- **Hypothesis:** the summary's `fb69fbb` state is stale if current `git log` contains later
  Round 21b commits.
- **Method:** inspect `git log`, `git status`, latest handoff, latest plan, and commit stats.
- **Observed result:** HEAD was `3a28132`; Round 21b had fixed F1/F2/F5 and updated the current
  receipt pointer.
- **Judgment:** C-I05 was caught before final reporting. Re-reading prevented a false current
  blocker claim.

### H4 — Permission-dependent failures must be reproduced in a named environment

- **Hypothesis:** the earlier 20 failures were environmental if the same checkout/command
  passes with host permission and fails only when nested Seatbelt application is denied.
- **Method:** compare exact command, checkout, root error, and parent permission; later rerun
  current checkout with skip reasons.
- **Observed evidence:** earlier managed versus host divergence and current
  `310 passed, 1 skipped` result.
- **Judgment:** environment dependence is established; no current code failure is claimed.

### H5 — An external benchmark claim is not evidence until its primary source is checked

- **Hypothesis:** names and summaries without direct links are useful search leads but cannot
  justify metric choices or numerical comparisons.
- **Method:** require official repository/paper, exact task definition, annotation method,
  metric formula, and limitation before promotion from `candidate` to `evidence`.
- **Observed result:** the supplied report omitted links, so C-I07 remains bounded rather than
  silently accepted.

### H6 — Another review is justified only when it has higher expected information gain than a canary

- **Hypothesis:** after a complete walking skeleton and green local suite, a 1×1 canary is
  more informative than another broad static review unless a causal blocker exists.
- **Method:** compare what each action can newly establish.
- **Result:** review can find more harness defects; canary alone establishes provider
  compliance, real trace production, retrieval behavior, and vertical artifact persistence.
- **Judgment:** C-I08 is unresolved until the canary runs; future work should choose the canary.

## (7) Concrete Codex resolution method

### A. Mandatory ownership check before writing another retrospective

1. Write the requested actor at the top: `Codex`, `Claude Code`, `subagent`, or `system`.
2. Give every issue an owner and an observer.
3. Use a separate namespace per owner; never continue another owner's recurrence counter.
4. Permit an external issue in a Codex log only when the row describes Codex's handling of it,
   such as wrong severity, failed verification, or stale interpretation.
5. Before saving, apply H2: remove all other-agent defects and confirm the Codex log still
   describes the session.

### B. Scope gate before severity or blocker labels

1. Restate the two core research questions.
2. For each finding, name the exact affected output:
   `retrieved_paths`, required-file Recall, read trace, reconstructed state, next action,
   invalid-run status, or arm comparability.
3. If none is affected, label it `support-harness debt`.
4. Separate `subsystem severity` from `experiment blocker` in the finding table.
5. Require a causal path or failing canary before postponing the canary.
6. Revisit deferred safety/release defects only before publishing the claim they protect.

### C. Canary-first execution rule

1. Freeze one case and one arm.
2. Ensure the subject receives only the public bundle; no hidden gold, evaluator, or prior
   trace.
3. Use the real provider adapter in a fresh session.
4. Require at least one host-owned search/read action.
5. Persist the full action trace and answer even on invalid or failed runs.
6. Evaluate required-file Recall and state reconstruction only.
7. Do not replace failed/invalid runs.
8. Let the observed vertical failure choose the next repair.
9. Expand to the static/dynamic × subagent/no-subagent matrix only after the 1×1 path is
   interpretable.

### D. Current-state refresh protocol

1. Run `git status --short` and `git log -8 --oneline` immediately before conclusions.
2. Search for newer handoff, amendment, result, and feedback files.
3. Read the latest entry document and the specific implementation response; do not rely only
   on the conversation summary.
4. Record commit and environment beside every test result.
5. If another agent changes the tree during review, invalidate present-tense conclusions and
   re-read the touched surface.

### E. Three-state verification protocol

1. Separate deterministic tests from host-isolation tests.
2. For isolation, execute an allowed control and forbidden probes under the actual parent
   runtime.
3. Report `PASS`, `FAIL`, or `BLOCKED`; skipped isolation is `BLOCKED` for the isolation claim.
4. Never compare Claude Code and Codex test totals without naming permission environment and
   checkout.
5. Do not rerun the whole suite merely to improve a number; rerun only to answer a specific
   uncertainty, as the second run here identified the exact skip reason.

### F. External precedent intake

1. Keep unlinked agent results in a `candidate` section.
2. Verify each candidate against its official repository or paper.
3. Extract only retrieval-relevant dimensions: gold context/file Recall, explored versus used
   context, read provenance, stale-document errors, abstention, dynamic workflow, and subagent
   comparison.
4. Exclude patch correctness, generic platform security, and unrelated orchestration metrics
   from primary outcomes.
5. Add numerical claims only after metric definitions and evaluation units are verified.

## Current Codex decision

The largest Codex error was not missing another guard. It was allowing the support harness to
replace the research target, then using support-harness findings to delay the retrieval
canary. The next high-information action is the real **1 case × 1 arm retrieval canary**.
Further Codex review is justified only by a demonstrated causal blocker or by a failure
observed in that vertical run.

