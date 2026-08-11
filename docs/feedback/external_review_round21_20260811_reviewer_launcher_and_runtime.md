# External Review Round 21 — Reviewer Launcher, Release Evidence, Runtime Permissions

- Date: 2026-08-11
- Review target: `eca3edb..fb69fbb`
- Experiment: `experiments/2026-08-07_handoff_dynamic_controller`
- Review mode: read-only code review plus local execution; no provider/model call
- Related handoff: [[../HANDOFF_20260810_primary_blocked]]
- Related implementation plan: [[plan_round21_forgeable_receipts_and_real_reviewer]]

## 0. Scope correction and supersession

The factual findings in this review remain valid for commit `fb69fbb`. Round 21b subsequently
resolved F1, F1b, F2, F5, and the current-state part of F7; see
[[plan_round21b_audit_path_bypasses_the_launcher]].

The final sentence below that treated F1-F3 as blockers for a **retrieval-only live canary**
is superseded. Those findings could invalidate a blind safety headline, but they do not alter
handoff-file retrieval, host-recorded reads, state reconstruction, or the static/dynamic ×
subagent comparison. The corrected scope and blocker rule are recorded in
[[session_retrospective_20260811_scope_correction_and_round21b]].

## 1. Verdict

Round 21 materially improved the launcher. The release E2E now executes a process inside
Seatbelt, validates its stdout, writes labels from that stdout, verifies an HMAC receipt,
checks the label bytes against `reviewer_output_sha256`, and passes those labels to the
adjudicator before adjudication. The reported `release=0`, `offline=2`, `primary=2`, and
`doctor=1` states were reproduced.

At reviewed commit `fb69fbb`, the completion claim was nevertheless too strong. The real audit CLI could still bypass the
launcher and its receipt, the documented reviewer CLI remains probe-only, and the final
release receipt discards the launcher evidence it summarizes. Therefore "only the live
canary remains" was false **for a canary intended to produce a blind safety headline**. A
canonical production audit path was required for that claim; durable evidence binding remains
separate audit/reproducibility debt. This paragraph is historical and must be read with the
scope correction above.

## 2. Reproduced execution results

| Check | Observed result | Interpretation |
|---|---:|---|
| `git status --short` | empty | reviewed tree was clean |
| `run_pipeline.py e2e --release` | exit 0 | synthetic stub reviewer path completed, 11/11 effective obligations |
| `run_pipeline.py e2e --offline` | exit 2 | reviewer labels correctly remain UNKNOWN |
| `run_pipeline.py e2e --primary` | exit 2 | explicit refusal; no attempt claimed |
| `run_pipeline.py doctor` | exit 1 | qualification artifact stale; assignment UNASSIGNED |
| Codex managed sandbox: `pytest . -q` | 274 passed, 20 failed, 1 skipped | nested Seatbelt/socket execution returned `Operation not permitted` |
| Same command with host permission | 294 passed, 1 skipped | matches the Claude Code report |

### 2.1 Permission-dependent result

The 20-test difference is real and is not explained by workspace contents. In the managed
Codex execution context the root error was:

```text
sandbox-exec: sandbox_apply: Operation not permitted
```

Running the identical command against the identical checkout with host permission produced
`294 passed, 1 skipped`. Claude Code and Codex can therefore report different suite outcomes
on the same workspace because their parent sandbox, subprocess, Unix-socket, and Seatbelt
permissions differ. This is an environment verdict, not evidence that one agent read a
different tree.

The current release receipt records only whether `/usr/bin/sandbox-exec` exists. Existence
does not establish that the current process may apply a profile. Capability must be measured
by an allowed probe plus forbidden probes and recorded as `PASS/BLOCKED/FAIL`.

## 3. Findings

### F1 — HIGH: the production audit path still bypasses the launcher

`run_pipeline.py` uses `reviewer_runner.run_reviewer(...)`, verifies its receipt, compares
the output bytes, and then invokes the adjudicator. That is a valid E2E integration path.

The actual audit CLI, `apply_safety_audit.py`, accepts only result, packet, key, and label
files. It neither accepts an isolation receipt nor calls `verify_isolation_receipt()`.
The operating handoff still tells reviewers to submit label JSON directly and then invokes
`apply_safety_audit.py`. The public `reviewer_runner.py` CLI also calls
`run_reviewer(..., command=None)`, so it produces a probe-only receipt and no labels.

Consequently, the HMAC and `reviewer_output_sha256` protect the synthetic release wrapper,
not the canonical audit procedure. A hand-authored label file that satisfies the adjudicator's
public hashes, IDs, and qualification fields can reach the safety headline without any
launcher receipt. The comment that "the adjudicator calls" the receipt verifier is false.

This is the same mechanism as the earlier workspace failure where a helper existed but the
consumed production path did not call it. A live canary run through a new one-off script would
repeat that failure instead of closing it.

### F2 — HIGH: agent assignment makes `doctor` follow an impossible receipt path

`doctor` loads `results/reviewer_isolation_<id>.json` and resolves the packet from
`doc.get("packet_file", "missing")`. `IsolationReceipt` has no `packet_file` field, and the
reviewer CLI does not add one before writing the receipt.

The failure was reproduced with a correctly HMAC-signed receipt: verification attempts to
hash `results/missing` and raises an uncaught `FileNotFoundError`. Once an agent reviewer is
assigned, the readiness command can crash instead of returning `BLOCKED`.

This must be corrected before assigning the live canary reviewer. The receipt must contain a
packet artifact identity, not an arbitrary host path, and doctor must resolve it through a
canonical audit-run manifest.

### F3 — MEDIUM-HIGH: release discards the evidence behind its PASS

The release E2E stores both HMAC receipts in the local `launcher_receipts` dictionary and
uses them during the run. That dictionary is never consumed again. The E2E runs in a temporary
directory, so the label artifacts and launcher receipts disappear after completion.

`release_<digest>.json` preserves only obligation strings, closure digest, commit, dirty
state, Python/platform, and binary existence. It does not preserve the packet hash,
assignment hash, profile hash, allowed/forbidden probe outcomes, reviewer command identity,
reviewer output hash, label artifact hash, or final adjudicated bundle hash.

Thus the byte binding was verified at runtime, but a later session cannot independently
verify the evidence summarized by `reviewer.labels.from-launcher: pass`. This is especially
important because the HMAC key is deliberately host-local.

### F4 — MEDIUM-HIGH: `11/11 PASS` is not bound to executed mutation results

`demonstrated_obligations()` explicitly defines PASS as "a mutation/acceptance proof is
declared and present", not that the proof last passed. It discovers mutation IDs by parsing
the test source and acceptance checks by finding a function name. `e2e --release` does not
execute that mutation suite, and its receipt states that tests were not recorded.

The full host suite did pass in this review, so the current checkout has supporting evidence.
The committed release receipt does not bind that evidence, however. A later edit can preserve
the mutation declaration and function name while breaking their assertions, and release can
still report demonstrated PASS.

### F5 — MEDIUM: `reviewer_command_sha256` identifies argv, not the reviewer

The hash is computed from NUL-joined command arguments. Replacing the script or executable at
the same path leaves the hash unchanged. For a live CLI, model version, adapter code, prompt,
schema, settings, and executable bytes may all change while `reviewer_command_sha256` remains
constant.

The receipt therefore proves which argv string was requested, not which reviewer
implementation produced the labels.

### F6 — MEDIUM: stdout schema validation is shallower than reported

`REVIEWER_OUTPUT_SCHEMA` requires two top-level objects but does not set
`additionalProperties: false`, does not type their values, and does not constrain the
qualification key set. Label IDs and vocabulary are checked afterwards, and the adjudicator
later validates qualification answers, so this is not currently fail-open at the final
adjudicator. It is still inaccurate to describe the launcher schema itself as a complete
reviewer-output contract.

### F7 — MEDIUM: current documentation contains contradictory runtime state

The top of the handoff still reports 10/10 obligations while the current program has 11.
Earlier PREREGISTRATION status text says offline exits 0 and release uses a probe-only run;
the current behavior is offline exit 2 and release executes the stub reviewer. Later sections
partially correct these statements, leaving two plausible current states in one entry document.

For a zero-context agent this is not cosmetic drift. It directly changes which command it
runs and what it interprets as success.

### F8 — LOW: append-only receipts have become a navigation surface

The result directory currently contains multiple closure and release receipts. The verifier
can select a current closure, but a human or cold-start agent sees many equally official-looking
files. Content-addressing prevents overwrite; it does not provide a canonical current pointer
or a supersession index.

## 4. Claims accepted and rejected

| Reported claim | Verdict | Reason |
|---|---|---|
| launcher executes a reviewer process | accepted for release E2E | `subprocess.run` stdout reaches label artifact |
| parse/schema/id/vocabulary/nonzero failures are refused | mostly accepted | schema is shallow; later checks close the important label paths |
| adjudicator receives launcher-produced bytes | accepted for release E2E | output hash is compared before the same paths are passed to adjudication |
| probe-only and reviewer runs are distinguishable | accepted | command/output hashes are null only for probe-only |
| release 11/11 completed | accepted as an observed synthetic release run | not a durable proof of all mutation executions |
| only live canary remains | rejected | F1-F3 and F2's doctor crash remain before a canary is interpretable |
| 294 passed / 1 skipped | accepted only for host-capable environment | managed Codex sandbox produced a different, BLOCKED environment result |

## 5. Improvement strategy using workspace precedents

### S1 — One canonical audit runner, not another helper

Create one production entry point, for example `run_safety_audit.py`, that owns this sequence:

```text
validate primary provenance
  -> build public packet
  -> launch declared reviewers
  -> verify HMAC receipts and output bytes
  -> adjudicate exactly those label artifacts
  -> persist an audit-run manifest and final bundle
```

`apply_safety_audit.py` should either accept and verify the receipts itself or be callable only
through this runner. The handoff, smoke, canary, and primary audit must all invoke the same
entry point. Remove direct manual label submission as an accepted agent-review path.

Precedent: `DESIGN_DECISION_surface_separation.md` §3 freezes one canonical builder and
forbids manual payload construction; smoke, qualification, primary, and rerun must share it.
`WORKSPACE_NAVIGATION.md` likewise requires a committed whitelist builder and byte-level
qualification before execution.

### S2 — Persist one evidence manifest and make release reference it

Write an `audit_run_manifest.json` outside the reviewer workspace containing hashes of:

- primary result and provenance receipt
- packet, assignment, rubric, qualification fixture, and schema
- exact sandbox profile and all control/deny probe outcomes
- each reviewer implementation identity and stdout-derived label artifact
- each HMAC receipt
- final adjudicated bundle
- runtime capability probe and environment fingerprint

The release receipt should contain `audit_run_manifest_sha256`, not eleven unexpandable PASS
strings. The manifest may omit the HMAC secret; it must preserve the signed receipts and every
public input required for same-host verification.

Precedent: `DESIGN_DECISION_surface_separation.md` §6 records fixture, qualification,
payload, prompt, schema, builder commit, model, and parameters in a trial manifest. The key
principle is to hash the complete surface actually consumed, not only its launcher command.

### S3 — Replace argv identity with reviewer execution identity

Record the following as a canonical `reviewer_execution` object:

- argv
- executable path, version, and executable/script SHA-256 where readable
- provider adapter SHA-256
- model ID and provider-reported canonical model
- rendered reviewer prompt SHA-256
- response schema SHA-256
- settings/config SHA-256
- packet SHA-256

Hash that object and put its digest in the isolation receipt. This follows the existing trial
manifest precedent rather than inventing another provenance vocabulary.

### S4 — Treat permission capability as a measured three-state gate

Split verification into two named lanes:

1. deterministic lane: no Seatbelt assumption, fast unit and evaluator tests;
2. host-isolation lane: real `sandbox-exec`, socket, allowed probe, permissive control, and
   forbidden probes.

The host-isolation lane is required for release. If the parent agent sandbox prevents the
probe, record `BLOCKED`, not FAIL and not PASS. Run Claude Code and Codex comparisons through
the same host wrapper when comparing implementations.

Precedent: the current reviewer runner's permissive control is the correct local mechanism;
`HARNESS_KNOWHOW.md` B4/B4a explains why positive existence checks cannot distinguish a
working guard from a no-op. The capability probe must include both a success that must be
possible and a violation that must be denied.

### S5 — Bind release to the focused acceptance run

Do not make release run the entire recursive pytest suite. Add a non-recursive focused command
that executes the 11 obligation controls once and writes a content-addressed
`verification_manifest.json`. Release verifies its source-tree digest, environment verdict,
case set, observed failure signals, and overall PASS before accepting it.

This avoids recursion while closing F4. The mutation harness must continue to assert both
source-level application and behavioral activation. `HARNESS_KNOWHOW.md` B4a is the direct
precedent: a positive test cannot identify a no-op guard, so each obligation needs a violating
input and the expected rejecting signal.

### S6 — Execute a thin canary only after the two integration blockers

Do not start another broad review loop. The shortest completion sequence is:

1. wire the canonical audit runner and make `apply_safety_audit` unable to bypass receipts;
2. repair doctor by resolving packet identity through the audit-run manifest;
3. run a two-item fake-reviewer E2E through the public CLI, not helper calls;
4. persist and read back the evidence manifest and final bundle;
5. run one real provider canary (`1 case x 1 arm`) through that same entry point;
6. if the canary passes, refresh qualifications and proceed to the authorized matrix.

No additional mutation framework or module extraction should be added unless one of these
vertical steps exposes a concrete failure.

Precedent: the canonical builder decision requires the canary and primary to share the path.
The handoff-reuse harness separates producer, cold-start subject, deterministic evaluator, and
adversarial reviewer roles; the real reviewer adapter should preserve the same separation
rather than letting the E2E synthesize another role's artifact.

### S7 — Make current state generated and singular

Keep amendment history, but generate one small `CURRENT_STATE.md` from doctor/release outputs.
The handoff links to that file instead of repeating counts and exit codes in multiple sections.
Add a `results/CURRENT.json` index that names the current closure, release, qualification, and
audit-run manifests without modifying the append-only artifacts themselves.

## 6. Gate decision

Do not run the live reviewer canary yet. This is not a request for another large hardening
round. F1 and F2 are narrow integration blockers: without them the canary either exercises a
one-off path that primary can bypass, or makes doctor crash once the agent assignment is
activated. Close those two through one canonical CLI, preserve its manifest, then run the
canary immediately.
