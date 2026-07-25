# E2.4 — Repo-Grounded Evidence Sufficiency + Abstain/Repair Contract (design)

E2.3 showed that the global feature-type invariant is not just a one-fixture
prompt accident:

```
CONTROL      0/2
A_ONLY       10/10
A_PARAPHRASE 9/10
A_TOPOLOGY   9/10
A_DECOY      10/10
```

The next question is no longer whether the invariant works. The next question
is whether a client agent can keep the boundary between **claim, abstain,
and repair** when the evidence is derived from real repository artifacts.

## Evidence Source Decision

Use this repository, `goodand/concept-gate-taxonomy`, as the only evidence
source for E2.4.

**Allowed repo-derived evidence:**
- `conceptgate/` module names, function/class names, docstrings, and explicit
  comments that describe behavior.
- `docs/`, `reference/`, and `experiments/` prose that states a relation,
  feature role, invariant, or contract directly.
- Tests and fixtures when they encode expected behavior directly.
- Commit messages only when copied into the evidence packet with commit hash
  and exact subject/body excerpt.

**Disallowed evidence:**
- General model knowledge about ontology, OWL, GUFO, transformers, or software
  architecture.
- Inferences from a file path or symbol name alone unless the evidence packet
  also contains an explicit supporting text span.
- External repositories or papers. Those are future generalization tests, not
  this repo-grounded bridge.

## Arms

| arm | prompt contract | output schema | purpose |
|---|---|---|---|
| CONTROL_REPO | repo evidence + ordinary client decision prompt | legacy decision schema | Measures overclaiming/overrepair from repo evidence alone. |
| A_REPO | repo evidence + E2.3 global feature-type invariant | legacy decision schema | Checks whether A still helps when evidence comes from repository artifacts. |
| CONTRACT_REPO | repo evidence + sufficiency/abstain/repair contract | `evidence_contract_v1` | Tests whether a structured contract controls the claim/abstain/repair boundary. |

CONTRACT_REPO is a new mechanism. It is not "A plus more wording." It must
first audit evidence, then decide sufficiency, then check invariants, then
choose `accept_report`, `repair`, or `abstain`.

## CONTRACT_REPO Contract

### 1. Source confinement

The model may use only `evidence_packet.evidence_items`. It must not fill gaps
from background knowledge. If a claim is plausible but not directly supported
by a supplied evidence item, the correct decision is `abstain`.

### 2. Evidence audit before decision

Every relevant evidence item must be classified as one of:

| admissibility | meaning |
|---|---|
| `direct_support` | The text explicitly supports a feature type/relation. |
| `indirect_context` | The text is relevant context but does not by itself support a final claim. |
| `ambiguous` | The text permits more than one interpretation. |
| `conflict` | The text directly conflicts with another admissible item. |
| `out_of_scope` | The item is not usable for this candidate judgment. |

Only `direct_support` can make a candidate judgment sufficient.

### 3. Sufficiency gate

A feature/type judgment is sufficient only if:
- at least one `direct_support` evidence item supports the selected type;
- no same-strength direct evidence supports an incompatible type;
- the judgment cites evidence ids from the packet;
- the judgment does not depend on unstated repo knowledge.

Otherwise it is `insufficient` or `conflicting`.

### 4. Global invariant, guarded by sufficiency

The E2.3 invariant still applies: the same feature name must have one type
across every concept that carries it.

But E2.4 adds a guard: do not repair merely because an invariant violation
exists. Repair only when the evidence is sufficient to choose the target
type. If a shared feature has inconsistent types but the evidence cannot
determine the correct unified type, the correct decision is `abstain`, not
`repair`.

### 5. Repairability

`repair` is allowed only when all of the following are true:
- the invariant violation is identified;
- the target type is evidence-sufficient;
- every changed feature cites supporting evidence ids;
- `repaired_concepts` returns the complete input concept set, not a diff;
- no concept or feature is added, removed, or renamed unless the evidence
  packet explicitly asks for that operation.

### 6. Abstain

`abstain` is required when:
- the evidence is missing, ambiguous, or conflicting;
- a repair target type cannot be selected from direct evidence;
- the model would need background knowledge outside the evidence packet;
- the payload is malformed or outside the experiment scope.

The abstain output must include `missing_evidence` requests that name the
concept/feature/relation needing more support.

## Decision Table

| condition | required decision |
|---|---|
| Evidence supports current server response and no repair is needed | `accept_report` |
| Evidence is sufficient and a global invariant violation is repairable | `repair` |
| Evidence is insufficient for the target type | `abstain` |
| Evidence directly conflicts across incompatible target types | `abstain` |
| Any decision would require non-packet knowledge | `abstain` |

## Files In This Design Packet

- `evidence_packet_schema.json`: shape of the repo-derived evidence packet
  that future fixture builders should give to the model.
- `decision_schema.json`: arm-to-schema map. CONTRACT_REPO uses the new
  `evidence_contract_v1` schema.
- `contract_prompt.md`: prompt block for CONTRACT_REPO.

## Scoring Obligations

The future scorer should not rely on self-reported success. It must check:
- `outside_knowledge_used` is `false`.
- every cited `evidence_id` exists in the evidence packet.
- `decision=repair` only when every changed feature judgment is `sufficient`.
- `decision=abstain` appears for hidden-oracle insufficient/conflicting cases.
- `repaired_concepts`, when present, preserves the complete concept and
  feature set unless the fixture explicitly allows structural edits.
- the same shared feature name has one selected type across all involved
  concepts when evidence is sufficient.

## Suggested Fixture Classes

This design intentionally leaves concrete trial operation to the execution
session. The fixture set should still cover four semantic classes:

| class | hidden oracle | expected CONTRACT_REPO behavior |
|---|---|---|
| sufficient_consistent | repo evidence supports current state | `accept_report` |
| sufficient_repairable | repo evidence supports one target type and current state violates it | `repair` |
| insufficient | evidence is only indirect, weak, or missing | `abstain` |
| conflicting | direct evidence supports incompatible target types | `abstain` |

Run cost can follow the E2.3 screening style: start with N=10 per core arm-cell,
threshold 0.90, and stop an arm once two failures make the threshold impossible.
That is an execution policy, not part of the contract itself.
