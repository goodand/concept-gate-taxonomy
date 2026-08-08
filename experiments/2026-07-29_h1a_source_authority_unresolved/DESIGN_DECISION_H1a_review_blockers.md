# DESIGN DECISION - H1a review blockers

decided_by: OpenAI Codex
date: 2026-08-01

## Source-Grounded Review

| source type | material used | role |
|---|---|---|
| prompt-given | `DESIGN_REQUEST_H1a_review_blockers.md` Q5-Q8, embedded rendered prompt, payload, reviewer findings | Primary evidence for this decision |
| repo-grounded | `DESIGN_DECISION_H1A_MANIPULATION_SCOPE.md`, `DESIGN_DECISION_H1A_PROMPT_SURFACE.md` in the visible workspace | Confirms binding Q1-Q4 decisions and the H1a-native prompt skeleton |
| MCP-grounded | None | Not needed; this is experiment-design and prompt-surface control, not taxonomy classification |
| literature-grounded | None | Not needed for this local design decision |
| model inference | Formal identifiability and manipulation-validity analysis | Used only after source review |

## Q5 - Loss Of Antecedent In The Manipulation Clause

Decision: **B - remove the third Korean sentence from the manipulated clause.**

### Rationale

The sentence `그 판정은 이미 끝났고 너의 범위가 아니다` no longer has the
antecedent it had in the E2.4 surface. Under Q3=B, the provenance/eligibility
preamble was removed. In the resulting H1a-native prompt, the deictic expression
`그 판정` is under-specified and can be read as attaching special status to the
payload anchor.

Restoring the E2.4 antecedent in both arms would fix the grammar, but it would
also reintroduce a provenance/eligibility assertion that H1a does not otherwise
need. Because Q6 removes the model-facing type anchor, there is no reason to
repair Q5 by adding a new authority-like common constant. The cleaner repair is
to remove the dangling sentence and keep the prohibition as two explicit
sentences:

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다.
어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

This changes the previously frozen span, but no trial has run. The repair must
therefore be recorded as a pre-execution re-freeze, not a post-hoc edit.

### Q5.1 - Does option A's restored sentence authorize the anchor?

**Yes, potentially.** If the prompt says the packet evidence passed
provenance/eligibility verification, the model can treat all model-facing packet
claims as already qualified. With the current anchor present, that would risk
authorizing the anchor. Even after Q6 removes the anchor, the sentence remains
an unnecessary common source-authority assertion. Do not restore it.

## Q6 - Type Anchor Hands The Model One Candidate Answer

Decision: **A - remove the model-facing type anchor before diagnostics and main trials.**

### Rationale

The current payload gives the model:

```json
"type": "structural_composition"
```

inside `candidate_concepts`. That value is one of the two allowed output values.
Even if no hidden correctness oracle is exposed, this field creates a no-cost
path to `select_type`: repeat the recorded repository state. That directly
acts on the dependent variable.

The Q2 anchor diagnostic was designed as a pre-freeze check for a possible
anchor ceiling. The review has now shown the stronger condition: the anchor is
itself a model-facing answer candidate. Since no trial has run, the correct
repair is to remove the anchor from the H1a model-facing payload rather than
measure its interference and proceed conditionally.

The payload should identify the supplied concept/feature pair without giving a
candidate type:

```json
{
  "concept_feature_pair": {
    "concept": "칼",
    "feature": "철",
    "evidence_refs": ["ev1", "ev2", "ev3"]
  },
  "evidence_items": [...]
}
```

The exact key names may follow local implementation style, but no
model-facing field may contain either allowed selected_type value except inside
the evidence text and the allowed-value list.

### Q6.1 - How should the task statement change under option A?

Keep the task statement but make the pair explicit:

```text
Your task is to observe whether the packet evidence supports selecting one of
two ontology feature types for the supplied concept/feature pair, or whether
you defer.

Supplied concept/feature pair:
- concept: 칼
- feature: 철
```

The model should infer support from evidence items, not from a pre-filled
candidate type.

### Q6.2 - What happens to the Q2 anchor diagnostic under option A?

The original Q2 anchor-flip diagnostic becomes **unnecessary and inapplicable**,
because the model-facing type anchor is removed from the main payload. Replace
it with a structural pre-freeze guard:

- fail if any model-facing payload field outside `evidence_items[].text` and
  the allowed-value list contains `essential_feature` or
  `structural_composition`
- fail if any `candidate_concepts`-like object reintroduces a `type`,
  `selected_type`, `expected_type`, `current_type`, `recorded_type`, or
  equivalent answer-bearing key
- keep the previously registered Q4 diagnostic-uniformity note only as
  historical superseded text; do not run the 20-call anchor diagnostic unless a
  later design reintroduces a model-facing anchor

## Q7 - Undefined Meaning Of `defer` Under Conflicting Evidence

Decision: **E - define `select_type` and `defer` by warrant, without a hard conflict tie rule.**

### Rationale

The current H1a prompt defines `defer` only for insufficient evidence. But this
fixture contains directly type-bearing evidence on both sides. Therefore the
prompt leaves the key case, sufficient-but-conflicting evidence, undefined.

Option B would restore the H3 defer ceiling that Q3 rejected. Option C would
create the opposite ceiling. Option A acknowledges conflict but still leaves the
decision language too loose. Option D would make the dependent variable a count
over categories the model invents during the trial.

Use an H1a-native warrant rule instead:

```text
Evidence may support different allowed types for the same concept/feature pair.
Your output should record whether, using only the packet, you judge the packet
to warrant selecting exactly one allowed type.

- Choose `select_type` only if the packet warrants selecting one allowed type
  over the other. Cite the evidence item ids that support the selected type.
- Choose `defer` if the packet does not warrant selecting exactly one allowed
  type, including cases where support is conflicting, ambiguous, or insufficient.
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.
```

This rule defines the observable behavior while preserving H1a's measurement
target: whether the liveness/source-priority prohibition surface changes the
model's willingness to select or defer under a fixed conflicting packet.

## Q8 - 2-vs-1 Evidence Asymmetry

Decision: **B - remove `ev2` and run the fixture as 1-vs-1.**

### Rationale

The fixture claims to be a 1-vs-1 conflict, but the model-facing packet is
currently doc 2 versus code 1. That count asymmetry can act as a prompt-level
pressure toward the doc-side type.

Adding the omitted code-side `주의:` sentence would restore 2-vs-2 count
symmetry, but it would expose type names outside H1a's selected_type enum and
broaden the model-facing ontology space. H1a needs a minimal conflicting packet,
not a fuller ontology instruction excerpt.

Removing `ev2` gives the cleanest packet:

- one direct doc claim for `essential_feature`
- one direct code claim for `structural_composition`
- no unmatched emphasis item
- no out-of-enum type names
- metadata truthfully describes the model-facing evidence shape

### Q8.1 - Is exposure of out-of-enum type names allowed?

**No for this H1a fixture.** It is not logically impossible to expose
out-of-enum names in some future design, but doing so here would add an
unnecessary prompt-surface perturbation. The model-facing evidence should
contain only the two allowed selected_type names unless a later experiment is
explicitly about out-of-enum handling.

## Deferred

None. The embedded prompt, payload, reviewer measurements, and visible prior
H1a decisions are sufficient to decide Q5-Q8.

## New Constraints

- Re-freeze Q1's manipulated span as the two explicit Korean prohibition
  sentences only; remove the dangling `그 판정은...` sentence from both the kept
  clause definition and residual-prohibition expectations.
- Do not restore the E2.4 provenance/eligibility antecedent sentence in H1a.
- Remove model-facing type anchors before any diagnostic or main trial.
- Replace the original 20-call Q2 anchor-flip diagnostic with a structural
  no-anchor guard unless a later design reintroduces a type anchor.
- The model-facing payload must identify the concept/feature pair without
  carrying an answer-bearing `type` field.
- H1a's prompt must define `select_type` and `defer` by warrant for exactly one
  allowed type, including the conflicting-evidence case.
- The prompt must not force `defer` merely because evidence conflicts.
- The prompt must not force `select_type` merely because each side has direct
  evidence.
- Do not use evidence count, order, source_kind priority, recency, authority,
  liveness, or outside knowledge as tie-breakers unless such priority is
  directly stated inside evidence text.
- Remove `ev2` from the main fixture and update metadata from 2-vs-1 to 1-vs-1
  truthfully.
- Do not add the code-side `주의:` sentence for H1a because it exposes
  out-of-enum type names and broadens the task.
- Freeze the revised prompt hashes, payload whitelist, evidence IDs, evidence
  order, schema, coder, and blocker-resolution decision before the first trial.

## Experiment Status

실험 진행 여부: **재정의 필요**

사유:

H1a should continue only after the model-facing prompt and fixture are
redefined. The current surface contains a dangling manipulated sentence, a
model-facing answer anchor, an undefined conflict/defer rule, and a 2-vs-1
evidence asymmetry. Because zero trials have run, these are pre-execution
design repairs rather than result-contingent changes.

After applying this decision, H1a becomes a fixed-packet descriptive experiment:
under a 1-vs-1 conflicting packet with no answer-bearing payload anchor, observe
whether the two-sentence liveness/source-priority prohibition changes the
model's `select_type` versus `defer` behavior.
