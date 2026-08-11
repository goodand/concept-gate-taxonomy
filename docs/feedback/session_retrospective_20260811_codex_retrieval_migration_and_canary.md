# Codex Session Retrospective - Retrieval Migration and Canary Interpretation

- Date: 2026-08-11
- Owner: **Codex**
- Scope: issues Codex directly caused, encountered, or reproduced after `C-I01..C-I09`
- Previous record: [[session_retrospective_20260811_scope_correction_and_round21b]]
- Retrieval design: [[evidence-evaluator/docs/DESIGN_OBSIDIAN_RETRIEVAL_CANONICAL]]
- Migration status: [[evidence-evaluator/docs/MIGRATION_STATUS_OBSIDIAN_RETRIEVAL]]
- Active handoff: [[../HANDOFF_20260810_primary_blocked]]

## Attribution rule

This is not a copy of Claude Code's defect history. A row belongs here only when:

1. Codex made the mistake while exploring, implementing, or reporting; or
2. Codex directly reproduced an issue that constrained Codex's conclusion.

Claude Code reports are leads, not resolution evidence. A lead becomes evidence here only
after source inspection, hash comparison, an executable reproduction, or a deliberately
bounded artifact comparison by Codex.

The product boundary remains narrow:

1. Can a zero-context agent find the handoff and supporting documents and reconstruct the
   current state, evidence, restrictions, completion conditions, and next action?
2. Do static/dynamic retrieval and retrieval-subagent absence/presence change retrieval
   performance?

## (1) New issues Codex experienced - C-I10 through C-I21

| ID | Type | Issue Codex experienced | Concrete occurrence | Impact |
|---|---|---|---|---|
| **C-I10** | Codex-caused | **Parsed an old harness artifact before reading its actual schema** | The first parity script assumed result fields and produced empty path arrays. Codex then inspected the top-level keys and corrected the parser | The first comparison was meaningless and could have been misreported as a retrieval miss |
| **C-I11** | Codex-caused | **Declared the portable retrieval slice complete before a host-capable output-contract smoke** | Unit/integration tests passed, but an actual `output_k=3` CLI smoke exposed hundreds of paths through `retrieved_paths`; internal graph discovery had leaked into the caller-visible result | Context bounds were violated even though the test suite was green |
| **C-I12** | Codex-caused | **Applied a precise-looking patch to the wrong duplicate assertion** | While adding the `output_k=1` regression, the first patch changed a similar earlier assertion instead of the intended assertion. The focused test failed and the exact target was then patched | One edit/retest cycle was wasted; without the focused test the intended guard would not have existed |
| **C-I13** | Codex-caused, caught during design | **Considered globally disabling Obsidian after one app-discovery failure** | A path-specific query failed while a known `CLAUDE.md` backlink query succeeded in the host lane. Global caching would have converted one path failure into loss of all later CLI graph evidence | A transient or path-specific failure could silently suppress valid backlinks for the rest of the process |
| **C-I14** | Codex-encountered and repeatedly reproduced | **Permission lane changes observable behavior** | The managed Python subprocess could not discover Obsidian while an unsandboxed backend returned four backlinks. Later, the canary experiment suite reported `328 passed / 1 skipped` in a host-capable lane but Codex reproduced `298 passed / 30 failed / 1 skipped` in the managed lane, concentrated in Seatbelt/isolation checks | A bare pass/fail total conflates code behavior with IPC/sandbox capability |
| **C-I15** | Codex-caused | **Used an unverified query as if it were a parity probe** | The old harness returned zero for a phrase not present in its indexed surface. Codex used `rg` to find the actual vocabulary and reran with `Obsidian CLI` | The original zero hit tested query choice, not old-versus-new retrieval quality |
| **C-I16** | Codex-encountered | **A lexical condition was reported as semantic Reconstruction FAIL** | `_terms_hit()` is OR-of-AND substring matching, and `next_action_accuracy` directly uses it. The canary sidecar nevertheless says the failure is at interpretation and is a subject result, while its own `not_established` field says the reason remains unknown | The report establishes `next_action lexical match=false`, not semantic misunderstanding |
| **C-I17** | Codex-encountered | **Retrieval PASS did not establish evidence sufficiency for the next action** | The canary read three authority documents and scored path Recall 1.0, but the subject identified `notes/audits/two-shapes-2026-06-11.md` as needed to choose a destination and did not read it | Gold path Recall can pass while a decision-critical claim remains unsupported |
| **C-I18** | Codex-encountered | **`follow_link` loses trajectory provenance** | `run_live_phase_c.py` knows `path` and `result`, but records only `_record("follow_link", before)` | The trace proves that a graph action happened but not which edge or result set the subject followed |
| **C-I19** | Codex-encountered | **The canary assessment sidecar is hash-correct but not fail-closed** | Codex recomputed the source and config SHA-256 values and they matched. No code, schema, or test consumes `live-subject-canary-assessment-v1` or rejects contradictory derived fields | The sidecar is a correct assertion, not an enforced derived artifact contract |
| **C-I20** | Codex-encountered | **`git_dirty: true` lacks before/after provenance** | Frozen-surface and source hashes matched, but the sidecar cannot distinguish a pre-existing dirty tree from files generated by the canary itself | Reproducibility is ambiguous even though no frozen-surface mismatch was found |
| **C-I21** | Codex-caused during this log | **Used filesystem-relative traversal syntax in cross-workspace Obsidian wikilinks** | The first draft linked the `evidence-evaluator` records with `../../../...`; Codex's link review caught that the vault uses root-qualified worktree paths and replaced both links | A zero-context agent could have received a fragile or unresolved entry path from the log intended to improve discoverability |

## (2) Repeated Codex issues and increased counts

Counts are lower bounds for Codex behavior only. Claude/project recurrence counters are not
imported.

| Codex pattern | Previous lower bound | New Codex occurrence | Current lower bound | Status |
|---|---:|---:|---:|---|
| **C-P1 Scope expansion / overintervention** | 3 | 0 | **3** | No increase. The reusable retrieval package explicitly excludes release governance, paid-run authorization, and safety adjudication |
| **C-P4 Review-before-E2E bias** | at least 3 | 0 | **at least 3** | No increase. This review followed a real 1x1 canary rather than delaying it |
| **C-P6 Large conclusion before validation** | 1 | 1 (`C-I11`) | **2** | Completion language preceded the host-capable bounded-output smoke |
| **C-P7 Permission-lane conflation** | 1 (`C-I06`) | 2 (`C-I14`: Obsidian IPC and Seatbelt suite) | **3** | Repeated. The same checkout/intent has materially different observability across lanes |
| **C-P8 Schema or vocabulary assumption before inspection** | 0 | 2 (`C-I10`, `C-I15`) | **2** | New repeated pattern. Both failures produced empty output for reasons unrelated to retrieval ability |
| **C-P9 Similar-text edit without unique target verification** | 0 | 1 (`C-I12`) | **1** | New, not yet repeated in the Codex-only counter |
| **C-P10 Green tests mistaken for an external contract proof** | 0 | 1 (`C-I11`) | **1** | New. The live transport exposed an untested cardinality invariant |
| **C-P11 Filesystem path semantics applied to vault links** | 0 | 1 (`C-I21`) | **1** | New. The error was corrected before commit and incoming backlinks were checked with Obsidian CLI |

The largest increase is `C-P7`: one prior environment-dependent verification issue became
three directly observed Codex cases. `C-P8` is the most important newly repeated process
problem because both occurrences manufactured a false zero before Codex inspected the input
contract.

## (3) Issues with resolution evidence

| Issue | Resolution evidence produced or checked by Codex | Evidence strength | Residual limit |
|---|---|---|---|
| C-I10 | Codex inspected the actual old-harness JSON keys, corrected the parser, and reran the comparison | Direct parser/output check | No generic schema adapter was added to the old harness |
| C-I11 | `retrieved_paths` now equals bounded `selected_paths`; `discovered_path_count` reports internal breadth; per-turn `new_paths` is bounded; `output_k=1` regression passes | Code path plus focused regression plus host-capable smoke | Ranking parity with the project-specific harness is deliberately not claimed |
| C-I12 | The focused test failed after the wrong edit; Codex patched the exact assertion and reran the suite | Direct negative then positive execution | The patching process still relies on reading enough context around duplicate text |
| C-I13 | Backend retries per path and does not globally cache app unavailability; a test verifies one failing path does not disable another | Characterization test plus mixed live observation | Actual IPC remains unavailable in the managed lane |
| C-I14 | Both runtime lanes and their exact outcomes are recorded in the migration document and this log | Direct execution in named environments | Cross-lane equivalence is not solved; it is made explicit |
| C-I15 | `rg` established corpus vocabulary before the corrected `Obsidian CLI` comparison | Direct corpus inspection and rerun | A single query is not a retrieval evaluation set |
| C-I16 | Codex read `_terms_hit()` and its `next_action_accuracy` call site and compared them with the handoff and assessment wording | Static causal-path inspection | Semantic adjudication has not run; the canary interpretation remains unresolved |
| C-I17 | Codex compared discovered candidates, actual read paths, and the subject's own uncertainty statement | Artifact-level trace comparison | Existing gold does not encode every decision-support read |
| C-I18 | Codex traced the call site: `path` and `result` exist before `_record`, but are omitted from the stored action | Direct implementation inspection | No repair or mutation test exists yet |
| C-I19 | Codex recomputed both SHA-256 values and searched for all consumers of the sidecar kind | Positive hash check plus negative consumer search | A manually edited but internally consistent sidecar is still possible |
| C-I20 | Codex checked current frozen-surface/source hashes and found no mismatch | Bounded integrity check | Pre-run dirty state and generated changes remain indistinguishable |
| C-I21 | Codex inspected the outgoing link forms, changed them to vault-root-qualified paths, and used Obsidian CLI to confirm two incoming backlinks to this record | Direct graph query | Outgoing target resolution still depends on both target files remaining inside the same vault |

## (4) Resolution status and issue chain

| Status | Issues | Meaning |
|---|---|---|
| **Resolved with an implemented mechanism** | C-I10, C-I11, C-I12, C-I13, C-I21 | The direct failure was reproduced and a focused guard, code change, or graph check now rejects it |
| **Resolved as an evidence boundary** | C-I14, C-I15 | The prior conclusion was corrected; the environment/query limitation is explicit rather than silently normalized |
| **Diagnosed, not resolved** | C-I16, C-I17, C-I18, C-I19, C-I20 | Codex established the mechanism and limit, but the experiment code/artifact contract has not been repaired |

The causal chain is:

```text
C-I10/C-I15: input schema or vocabulary assumed
  -> false empty comparison
  -> inspect the real artifact/corpus
  -> corrected parity probe

C-I11: tests green
  -> completion stated too early
  -> host-capable CLI smoke
  -> retrieved_paths cardinality violation exposed
  -> output set separated from discovery diagnostics

C-I14: same intent, different permission lane
  -> conflicting test/CLI outcomes
  -> classify capability as PASS / FAIL / BLOCKED per lane
  -> never turn a managed-lane IPC block into a retrieval regression

C-I16: lexical false
  + C-I17: unread decision-support document
  + C-I18: incomplete graph provenance
  -> semantic cause cannot be uniquely identified
  -> Reconstruction must remain unresolved pending adjudication
```

## (5) Problem definitions for repeated, evidence-backed Codex issues

### Problem A - A green internal suite does not prove the caller-visible contract

**Issues:** C-I11, C-I12.  
**Repeated patterns:** C-P6, C-P9, C-P10.

The retriever had correct internal breadth for recall, but the public field exposed that
breadth without respecting `output_k`. Tests proved that files could be found; they did not
prove the transport's context bound.

Formally:

```text
internal discovery invariant:
  discovered_count may exceed output_k

public output invariant:
  len(candidates) <= output_k
  len(retrieved_paths) <= output_k

diagnostic invariant:
  discovered_count is a number, not an unbounded path payload
```

Testing only the first invariant allowed the third-party caller contract to fail.

### Problem B - An empty result is uninterpretable until the input contract is verified

**Issues:** C-I10, C-I15.  
**Repeated pattern:** C-P8.

An empty array can mean no relevant document, wrong JSON field, unsupported query vocabulary,
excluded scope, unavailable runtime, or parser failure. Codex initially treated two such
zeros as retrieval observations before checking schema and corpus vocabulary.

The correct null hypothesis is not `retrieval failed`; it is `the probe has not yet been
shown to exercise retrieval`.

### Problem C - Runtime capability is part of evidence provenance

**Issues:** C-I14, continuing C-I06.  
**Repeated pattern:** C-P7.

Obsidian and Seatbelt both cross process/IPC boundaries. Filesystem identity alone does not
make Claude host execution and Codex managed execution equivalent. A result must be bound to:

```text
checkout + command + parent sandbox + IPC capability + observed control probe
```

Without those fields, `passed` and `failed` are not portable facts.

### Problem D - Metric names can claim more semantics than the matcher establishes

**Issues:** C-I16, C-I17.  

`next_action_accuracy` sounds semantic, but its implementation only establishes whether one
OR-of-AND substring group appears. `Retrieval PASS` sounds sufficient, but the gold set does
not include every source the subject says it needs for its choice. The names exceed the
observations.

The minimum honest claims are:

```text
next_action_lexical_match = false
gold_required_path_recall = 1.0
semantic_next_action_correctness = unresolved
decision_evidence_sufficient = unresolved
```

### Problem E - A trace action without arguments is not graph-walk provenance

**Issues:** C-I18.

Recording `follow_link` without source/target/result identifies an action class, not the
evidence path. It cannot distinguish a useful graph walk from an unrelated hop, and it cannot
support replay or edge-level evaluation.

### Problem F - Hash fields do not enforce themselves

**Issues:** C-I19, C-I20.

A sidecar can contain correct hashes and still have no consumer. A dirty flag can be true and
still omit when dirtiness arose. Integrity metadata becomes a mechanism only when a consumer
recomputes it, rejects mismatch, and records the before/after boundary needed by the claim.

## (6) Hypotheses and verification methods Codex used

### H7 - `output_k` must bound every caller-visible path list

- Hypothesis: a retrieval response that advertises `output_k=k` must not return more than `k`
  actionable paths, even if graph discovery found more.
- Method: run a host-capable smoke with `output_k=3`, inspect cardinalities, then add a focused
  `output_k=1` regression with graph discoveries greater than one.
- Falsification: any caller-visible actionable path list exceeds `output_k`.
- Result: the first live smoke falsified the old implementation; the repaired implementation
  returns bounded `retrieved_paths` and a separate count.
- Judgment: C-I11 resolved.

### H8 - Obsidian failure is path-local unless a control proves process-wide failure

- Hypothesis: one `unable to find Obsidian` response does not justify disabling the backend
  for all later paths.
- Method: compare a failing path with a known `CLAUDE.md` backlink control in the same host
  process; encode a test where the first path fails and the second succeeds.
- Falsification: every known-good control fails in the same process boundary.
- Result: mixed success occurred; global disable would have been wrong.
- Judgment: C-I13 resolved by path-local retry/warning behavior.

### H9 - Environment-dependent failures require a named lane and a control

- Hypothesis: the Codex-managed Seatbelt/Obsidian failures are `BLOCKED` capability results,
  not code regressions, if host controls pass on the same functional path.
- Method: compare exact commands and root errors across host and managed lanes; identify the
  failure concentration in IPC/isolation tests rather than deterministic retrieval tests.
- Result: host Obsidian returned four backlinks and host suite totals were higher; managed
  subprocess and Seatbelt tests failed at the environment boundary.
- Judgment: C-I14 is bounded, not eliminated.

### H10 - The canary cannot establish semantic failure through `_terms_hit()` alone

- Hypothesis: if `next_action_accuracy` is computed only by substring groups, `false` cannot
  distinguish subject misunderstanding from paraphrase, incomplete gold, or missing evidence.
- Method: read the matcher and call site; compare them with the sidecar's stronger prose and
  `not_established` list.
- Falsification: find an independent semantic judge result bound to the canary.
- Result: no such judgment exists; the sidecar itself defers causal classification.
- Judgment: C-I16 remains unresolved; `Reconstruction FAIL` is too strong.

### H11 - Gold Recall 1.0 does not imply decision-evidence sufficiency

- Hypothesis: if the subject names an unread document as necessary for selecting the next
  action, Recall over a smaller gold path set cannot prove sufficient retrieval.
- Method: compare candidate paths, read trace, answer uncertainty, and scored gold fields.
- Result: `two-shapes-2026-06-11.md` was discovered but not read; path Recall still passed.
- Judgment: C-I17 remains unresolved and requires a prospective gold extension.

### H12 - A sidecar is enforced only if a consumer rejects contradiction

- Hypothesis: matching hashes demonstrate current integrity but not a durable artifact
  contract when no validator consumes the sidecar kind.
- Method: recompute source/config SHA-256 and search source/tests/schema for the sidecar kind.
- Result: hashes matched; no consumer was found.
- Judgment: C-I19 diagnosed, not resolved.

### H13 - A handoff backlink is valid only if the vault graph can observe it

- Hypothesis: a Markdown link that looks valid in a filesystem diff may still be a poor
  Obsidian entry edge when it uses the wrong path semantics.
- Method: normalize cross-workspace links to vault-root-qualified paths and query Obsidian
  backlinks for this new record.
- Result: Obsidian returned both the previous Codex retrospective and the Codex MCP handoff
  MOC as incoming links.
- Judgment: C-I21 resolved before commit.

## (7) Concrete resolution method

### A. Prevent another false-zero comparison

1. Inspect `--help`, schema, or one known-good artifact before writing a parser.
2. Validate required keys and types; fail if an expected field is absent.
3. Use `rg` to confirm at least one query token exists or deliberately label the query as a
   lexical-miss case.
4. Run one known-positive control and one known-negative control.
5. Only then compare rankings or Recall.

### B. Close the output contract before calling a retrieval slice complete

1. Define caller-visible lists separately from internal search state.
2. Assert `len(candidates) <= output_k` and `len(retrieved_paths) <= output_k` at service and
   transport boundaries.
3. Expose internal breadth as counts or a separately bounded pool.
4. Run Python service, CLI, and MCP against the same fixture.
5. Run one host-capable Obsidian smoke in the production permission lane.
6. Do not use “complete” until both synthetic and host-bound contracts pass.

### C. Make patch application observable

1. Read enough surrounding context to distinguish duplicate assertions.
2. Use a unique patch anchor that includes the function name and target assertion.
3. Immediately inspect `git diff -- <file>` after applying the patch.
4. Run the smallest focused negative test first.
5. Run the full package suite only after the focused test proves the intended location changed.

### D. Report runtime results by lane

1. Record checkout, exact command, parent runtime, and sandbox profile.
2. Execute an allowed IPC control before interpreting forbidden-probe failures.
3. Report deterministic tests separately from host-isolation tests.
4. Use `PASS`, `FAIL`, and `BLOCKED`; a skipped or denied isolation probe is not PASS.
5. Never compare aggregate Claude/Codex test totals without the lane metadata.

### E. Repair canary interpretation before the 1x4 pilot

1. Preserve the raw canary artifact byte-for-byte.
2. Replace the sidecar's semantic headline with:
   `Reconstruction = UNRESOLVED_PENDING_ADJUDICATION`.
3. Preserve the measured auxiliary value:
   `next_action_lexical_match = false`.
4. Run an isolated judge that returns exactly one of:
   `SUBJECT_SEMANTIC_MISS`, `LEXICAL_MATCHER_FALSE_NEGATIVE`,
   `GOLD_AMBIGUOUS`, or `WORKFLOW_EVIDENCE_INSUFFICIENT`.
5. Bind that judgment to the raw artifact SHA-256 and judge input manifest.
6. Do not retrofit the current canary into confirmatory evidence after changing gold.

### F. Extend retrieval sufficiency prospectively

1. Add `required_action_support_paths`, `support_ranges`, and `required_reads` to a new gold
   version.
2. Include `two-shapes-2026-06-11.md` only if an independent curator verifies that it is
   required for the selected next action.
3. Freeze the new gold before the 1x4 pilot.
4. Score file discovery and actual reading separately.
5. Treat the existing 1x1 canary as diagnostic evidence under the old gold.

### G. Complete graph-walk provenance

1. Record `from_path`, bounded `result_paths`, and `static_next_path` for `follow_link`.
2. Include a digest when the result set exceeds the display bound.
3. Add negative tests that remove each field from an otherwise valid trace.
4. Replay one recorded follow-link step and verify the same canonical edge set.

### H. Turn the assessment sidecar into a small derived-artifact contract

1. Implement one generator/validator, not another general governance framework.
2. Recompute source and config hashes.
3. Derive runtime/retrieval lexical metrics from the raw artifact rather than accepting them
   from input JSON.
4. Reject a sidecar whose metrics contradict the source.
5. Record `pre_run_git_dirty`, `pre_run_diff_sha256`, `post_run_git_dirty`, and generated paths.

### I. Validate handoff graph edges before saving

1. Use vault-root-qualified wikilinks for targets in sibling worktrees or repositories.
2. Add the new record to one small entry MOC and to its immediate predecessor.
3. Query Obsidian backlinks for the new record.
4. Require the expected incoming files to appear; do not infer backlink validity from text
   search alone.

## Current Codex conclusion

The reusable Obsidian retrieval slice is implemented and locally committed as
`evidence-evaluator` commit `745323c`; its bounded-output defect was found by a real smoke and
repaired before this record. It is not yet a parity replacement for the project-specific
`.vault-harness` ranking policy.

The canary establishes a working provider-to-host vertical path, a valid runtime, and Recall
1.0 over the current gold-required paths. It does **not** yet establish semantic next-action
failure or complete decision-evidence sufficiency. The next justified work is the small
adjudication/provenance repair in sections E-G, not another broad safety/governance review.
