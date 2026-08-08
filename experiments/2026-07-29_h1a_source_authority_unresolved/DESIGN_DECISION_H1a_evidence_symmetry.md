# DESIGN DECISION - H1a evidence symmetry

decided_by: OpenAI Codex  
date: 2026-08-02

## Source-Grounded Review

| source type | material used | role |
|---|---|---|
| prompt-given | `DESIGN_REQUEST_H1a_evidence_symmetry.md`, including the rendered 1-vs-1 payload, source-line measurements, options A-E, and binding Q8/Q8.1 constraints | Primary evidence for Q9 |
| repo-grounded | `DESIGN_DECISION_H1A_REVIEW_BLOCKERS.md` and its Q7-Q8 rationale in the visible workspace | Confirms the warrant rule, the reason for 1-vs-1 count symmetry, and the prohibition on out-of-enum type names |
| MCP-grounded | None | Not needed; Q9 concerns experimental identifiability and fixture construction, not taxonomy adjudication |
| literature-grounded | None | Not needed for this bounded, local pre-execution design decision |
| model inference | Conditional-estimand and arm-invariance analysis | Applied only after reviewing the supplied measurements and binding decisions |

## DESIGN DECISION - H1a evidence symmetry

### Q9 - Evidence-content asymmetry

Decision: **A - keep the byte-faithful 1-vs-1 evidence packet and declare the
argumentative asymmetry as a limitation.**

### Rationale

The asymmetry is real: `ev3` does more argumentative work than `ev1`. It
acknowledges the doc-side premise, rejects the competing interpretation, and
states a separating principle. `ev1` states and supports only its own
classification. Count symmetry therefore does not imply argumentative-strength
symmetry.

This does not, however, create an arm-varying confounder. The same ordered,
byte-identical evidence packet is shown in both arms. H1a can therefore estimate
only the descriptive arm contrast conditional on this packet:

```text
Pr(decision | arm, this fixed rhetorically asymmetric packet,
   frozen model and sampling parameters)
```

It cannot estimate the effect of the prohibition for content-balanced conflicts,
for arbitrary doc/code conflicts, or for the repository population.

Option A is different from tolerating the Q8 defect. Q8's 2-vs-1 count
asymmetry was introduced by fixture selection: `ev2` could be removed while
preserving the concept/feature pair, both direct type claims, byte fidelity, and
the two-value task. Q9's content asymmetry is intrinsic to the only supplied
verbatim statements for this pair. The proposed repairs would instead change a
binding or constitutive property of the fixture:

- B reopens Q8.1 and exposes out-of-enum types and adjacent examples;
- C selectively truncates the code argument and misrepresents its actual
  rationale;
- D replaces the empirical conflict under study and is not known to yield a
  more symmetric source pair.

Perfect rhetorical symmetry is not a hidden requirement of this fixed-packet
descriptive experiment. Source fidelity and arm invariance take precedence
here. The cost is a strict limit on interpretation: the code-side rhetorical
advantage is part of the experimental condition, not evidence for code
authority, semantic correctness, or a general source preference.

### Q9.1 - Exact limitation text for the preregistration

Add the following as **L3**, at the same reporting level as L1 and L2:

```text
L3 - Intrinsic evidence-content asymmetry

The model-facing packet is symmetric in evidence-item count (one doc item and
one code item) but not in argumentative structure. The code item (`ev3`)
acknowledges and rebuts the competing essential-feature rationale and adds the
general distinction that material essentiality and the relation type are
separate axes. The doc item (`ev1`) states only its own essential-feature
rationale. This asymmetry is present in the unique byte-faithful source excerpts
for the fixed concept/feature pair and is held identical, in the same order, in
both arms.

Accordingly, H1a estimates only a descriptive arm contrast conditional on this
specific rhetorically asymmetric packet. Absolute selected-type frequencies,
and the presence, absence, size, or direction of a select/defer arm difference,
must not be generalized to content-balanced conflicts, other doc/code pairs, or
a repository-level population. The code-side rhetorical advantage must not be
interpreted as evidence that structural_composition is correct, that code is
generally more authoritative, or that the same behavior would occur with
argumentatively symmetric evidence. A null result is only a null for this fixed
packet; it does not establish that the prohibition is behaviorally inert in
general.
```

### Q9.2 - Does this decision reopen Q8.1?

**No.** Q8.1 remains binding without exception. Do not widen either excerpt to
expose `contextual_usage`, `locational`, or any other out-of-enum type name.

## Deferred

- `Q9-D-FUTURE`: Whether the repository contains another byte-faithful,
  argumentatively closer 1-vs-1 doc/code pair is deferred to a future
  multi-fixture or generalization study. Its absence or presence is not needed
  to run the current fixed-packet descriptive H1a, and searching for a new pair
  must not be used to replace this fixture after observing H1a outcomes.

## New Constraints

- Add L3 verbatim to the preregistration and issue register before trial 1.
- Keep `ev1` and `ev3` byte-faithful, unabridged at their currently registered
  source spans, and identical across arms.
- Freeze evidence IDs, source spans, rendered text, order, payload hash, prompt
  hash, model, and sampling parameters before trial 1.
- Keep Q8.1 in force; do not expose out-of-enum type names to manufacture
  rhetorical symmetry.
- Primary interpretation is the within-packet arm contrast in `select_type`
  versus `defer`; do not present absolute `selected_type` proportions as a
  source-authority or semantic-correctness result.
- Do not use rationale text, citations, or perceived argument quality as a
  post-hoc outcome, exclusion rule, or reweighting factor unless a separate
  analysis is specified and frozen before trial 1.
- If the two arms yield the same modal category or no detectable difference,
  report a packet-conditional null, not evidence of general prohibition
  irrelevance.
- Any future alternative-pair search must be specified independently of H1a
  results and analyzed as a separate experiment, not substituted into this
  frozen cohort.

## Experiment Status

실험 진행 여부: **계속**

사유:

The evidence-content asymmetry is source-intrinsic, byte-faithful, and constant
across arms. It narrows the estimand but does not destroy the conditional
within-packet arm comparison. Proceed only after L3 and the constraints above
are registered and the unchanged surfaces are re-frozen before the first trial.
