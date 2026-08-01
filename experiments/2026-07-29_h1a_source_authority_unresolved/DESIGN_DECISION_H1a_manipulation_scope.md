# DESIGN DECISION - H1a manipulation scope

decided_by: OpenAI Codex
date: 2026-07-30

## Source-Grounded Review

| source type | material used | role |
|---|---|---|
| prompt-given | `DESIGN_REQUEST_H1a_manipulation_scope.md` M1-M9, Q1/Q2 options, non-negotiable constraints | Primary evidence for this decision |
| repo-grounded | Local search found no H1a-specific implementation files in the visible workspace; only the earlier E2.4 `contract_prompt.md` was located | Background only; not used to override embedded measurements |
| MCP-grounded | None | Not needed; this is experimental-design and prompt-surface control, not taxonomy classification |
| literature-grounded | None | Not needed for this local design block |
| model inference | Formal identifiability and manipulation-validity analysis | Used only after source review |

## Q1 - Scope Of Manipulation

Decision: **B - include L24-25 in the manipulation.**

### Rationale

The intervention must be defined by the semantic rule it removes, not by the
accidental sentence count in the prompt.

Let `J` be the model behavior "adjudicate liveness, source priority, recency, or
authority." The intended `PROHIBITION_REMOVED` arm is supposed to remove the
contractual prohibition against `J`.

But the supplied measurements say the prompt contains two clauses that both
entail `do not J`:

- block L8: the model does not re-judge source liveness or priority
- block L24-25: the model must not infer which source is newer, more authoritative,
  or live code

Removing only L8 while retaining L24-25 does not remove the prohibition. It
leaves a logically equivalent prohibition in the model-facing surface. Therefore
option A is not merely weak; it fails to instantiate the treatment.

Option C would create the cleanest single-sentence micro-ablation, but it answers
a different question: the effect of a newly authored H1a-only contract. H1a is
currently about the behavior of the existing contract surface when the liveness
prohibition is removed. For that question, the honest minimal edit is not "delete
one line"; it is "delete every clause that performs the same prohibition while
leaving the rest of the packet-boundary contract intact."

Accordingly, D-H1a-5 should be restated as:

> Minimal semantic edit: remove all model-facing clauses that prohibit liveness,
> source-priority, recency, authority, or supersession adjudication. Preserve all
> other packet-boundary and no-external-knowledge constraints.

### Freeze Test Requirements

1. Assign stable clause IDs to the contract surface before rendering.
2. Mark L8 and L24-25, and any equivalent clause if later discovered, as
   `liveness_priority_prohibition`.
3. `PROHIBITION_KEPT` must contain all clauses in that category.
4. `PROHIBITION_REMOVED` must contain zero clauses in that category.
5. The removed arm must still retain general packet-boundary rules, including
   "use only packet evidence" and "do not use outside knowledge."
6. The rendered prompt diff must be restricted to the approved clause IDs and
   whitespace mechanically required by their deletion.
7. A residual-prohibition guard must fail the removed arm if it contains a
   model-facing instruction equivalent to:
   - do not judge liveness
   - do not judge source priority
   - do not infer which source is newer
   - do not infer which source is more authoritative
   - do not infer whether a source is live code
   - that judgment is already done
   - that judgment is outside the model's scope
8. This guard must be structure-based where possible. Keyword scanning may be a
   secondary tripwire, not the sole proof of absence.
9. Both arms must keep identical fixture, evidence order, schema, model,
   parameters, coder, and payload field whitelist.
10. Commit or otherwise freeze the two rendered prompt hashes and the clause
    manifest before any H1a trial.

## Q2 - Identifiability Of A Null Result

Decision: **B, with a pre-freeze diagnostic gate.**

### Rationale

The main H1a design cannot distinguish these two states after the fact:

- the prohibition manipulation has no observable effect
- the `candidate_concepts` anchor pushes both arms to the code-side answer and
  produces a ceiling

This is not ordinary confounding. The anchor is arm-constant, so it does not
covary with treatment, but it can still interact with treatment by saturating
the observable behavior. With K=1 and no anchor-flipped counterpart inside the
main cohort, a post-run null would be underidentified.

Because no H1a trials have run, the reviewer proposal is admissible if it is
promoted from "off-protocol trial" to a separately preregistered, non-estimating
diagnostic. It may block the main experiment, but it must not be merged into the
main H1a cohort or used to tune N after seeing results.

### Required Diagnostic

Before freezing and running the main H1a cohort, create an
`anchor_sensitivity_diagnostic` cohort:

- factors:
  - arm: `PROHIBITION_KEPT`, `PROHIBITION_REMOVED`
  - anchor: `structural_composition`, `essential_feature`
- fixed repetitions: `R_diag = 5` per cell
- total diagnostic calls: `2 x 2 x 5 = 20`
- payload delta: only the `candidate_concepts` recorded type changes
- evidence text, evidence IDs, source kinds, evidence order, schema, model,
  parameters, and coder remain identical
- diagnostic outputs are labeled `non_certifying_diagnostic`
- diagnostic outputs are never merged into the main H1a result table

Predeclare a blocking rule before the diagnostic runs:

> Treat gross anchor sensitivity as present if flipping only the anchor changes
> the modal behavior category or modal selected type in either arm, or changes
> the selection/defer count by at least 2 out of 5 in either arm comparison.

If gross anchor sensitivity is present, the main H1a cohort must not report
"no difference observed" as an interpretable null. The design must then be
reopened and choose one of:

- remove the type anchor from the model-facing `candidate_concepts`
- convert H1a into a positive-effect-only observation where null is explicitly
  unreportable
- redesign H1a as a crossed anchor/manipulation pilot rather than the current
  2-arm design

If gross anchor sensitivity is not observed, the main H1a cohort may proceed,
but any null conclusion must be worded narrowly:

> Under this fixed packet, fixed source order, fixed anchor, model, transport,
> and parameters, no arm difference was observed; the anchor diagnostic did not
> detect gross ceiling behavior under the preregistered perturbation.

It must not be reported as proof that the prohibition has no effect in general.

## Deferred

None. The supplied measurements are sufficient for the design decision. Exact
implementation paths are intentionally outside this external-design decision.

## New Constraints

- H1a's manipulation is now a semantic prohibition removal, not a literal
  one-sentence deletion.
- A prompt diff test is insufficient unless paired with a residual-prohibition
  absence test.
- The removed arm must not contain any model-facing equivalent of "source
  liveness, priority, recency, authority, or supersession is outside your scope."
- General packet-boundary and no-outside-knowledge rules must remain in both
  arms.
- The anchor-sensitivity diagnostic must be frozen, run, and archived as a
  separate `non_certifying_diagnostic` cohort before the main H1a cohort.
- The diagnostic may block the main experiment but may not change the main
  cohort N, be merged into the main results, or be used to rewrite conclusions
  after main outputs are known.
- A null result is reportable only if the diagnostic does not detect gross anchor
  sensitivity, and even then only as a fixed-packet observation.
- All previous H1a preregistration text that allows "did not differ" must be
  amended to include the diagnostic precondition.
- Trial execution remains blocked until the revised prompt surface, clause
  manifest, residual guard, diagnostic protocol, and hashes are frozen.

## Experiment Status

실험 진행 여부: **재정의 필요**

사유:

The current `PROHIBITION_REMOVED` arm does not remove the relevant prohibition,
so Q1 blocks prompt generation. In addition, the current main design cannot
identify an interpretable null because the type anchor may create a ceiling.
The experiment should not be stopped permanently: trial count is still zero, so
the surface and preregistration can be revised without result-contingent
contamination. It may proceed only after Q1's semantic-removal surface and Q2's
pre-freeze anchor diagnostic gate are implemented and frozen.
