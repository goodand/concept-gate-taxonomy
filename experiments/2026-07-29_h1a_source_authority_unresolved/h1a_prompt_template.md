# H1a prompt template (post Q5-Q8)

This file is the model-facing prompt skeleton, extracted out of
`DESIGN_DECISION_H1a_prompt_surface.md` so that Q5, Q6.1, and Q7 can each
modify it without editing a preserved-verbatim ruling file. Every section
below is traceable to exactly one ruling:

| Section | Source |
|---|---|
| Preamble, packet-boundary sentence, allowed values, output schema, consistency requirements | `DESIGN_DECISION_H1a_prompt_surface.md` (Q3=B), unchanged |
| `Supplied concept/feature pair:` block | `DESIGN_DECISION_H1a_review_blockers.md` Q6.1, verbatim |
| Warrant rule (3 bullets + tie-breaker prohibition list) | `DESIGN_DECISION_H1a_review_blockers.md` Q7, verbatim |
| Liveness clause (2 sentences, inserted for `PROHIBITION_KEPT` only, by `_h1a_contract.py`) | `DESIGN_DECISION_H1a_manipulation_scope.md` Q1, reduced per Q5=B |

The Q3 template's own two `select_type`/`defer` bullets under "Evidence-reading
rule" are removed here -- Q7 found that pairing undefined for
sufficient-but-conflicting evidence, and its warrant rule is the sole
replacement, not an addition alongside the old one.

```text
You are an MCP client agent.

Input is a repo-derived evidence packet. Use only the packet fields presented
in this prompt. Do not use general ontology knowledge, OWL/GUFO background
knowledge, codebase memory, prior conversation context, or external sources.

Your task is to observe whether the packet evidence supports selecting one of
two ontology feature types for the supplied concept/feature pair, or whether
you defer.

Supplied concept/feature pair:
- concept: {concept}
- feature: {feature}

Evidence-reading rule:
- Treat an evidence item as support only when its text directly states or
  clearly entails the ontology type of the supplied concept/feature pair.
- Evidence that merely mentions implementation details, examples, labels, or
  adjacent context without tying the concept/feature pair to one of the allowed
  types is not enough by itself.

Evidence may support different allowed types for the same concept/feature pair.
Your output should record whether, using only the packet, you judge the packet
to warrant selecting exactly one allowed type.

- Choose select_type only if the packet warrants selecting one allowed type
  over the other. Cite the evidence item ids that support the selected type.
- Choose defer if the packet does not warrant selecting exactly one allowed
  type, including cases where support is conflicting, ambiguous, or insufficient.
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.

Allowed selected_type values:
- essential_feature
- structural_composition

Output JSON using h1a_observation_v1:
{
  "decision": "select_type" | "defer",
  "selected_type": "essential_feature" | "structural_composition" | null,
  "cited_evidence_ids": ["..."],
  "rationale": "..."
}

Consistency requirements:
- If decision is "select_type", selected_type must be one of the two allowed
  type values.
- If decision is "defer", selected_type must be null.
- Do not output repair, accept_report, abstain, missing_evidence,
  contract_verdict, evidence_audit, repair_plan, or any fields outside
  h1a_observation_v1.

payload:
{payload_json}
```
