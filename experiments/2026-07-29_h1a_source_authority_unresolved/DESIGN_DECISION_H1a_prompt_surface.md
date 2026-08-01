# DESIGN DECISION - H1a prompt surface

decided_by: OpenAI Codex
date: 2026-07-31

## Source-Grounded Review

| source type | material used | role |
|---|---|---|
| prompt-given | `DESIGN_REQUEST_H1a_prompt_surface.md` N1-N8, H3 precedent, Q3/Q4 options, constraints | Primary evidence for this decision |
| repo-grounded | `DESIGN_DECISION_H1A_MANIPULATION_SCOPE.md` in the visible workspace | Confirms Q1 semantic prohibition removal and Q2 anchor diagnostic constraints |
| MCP-grounded | None | Not needed; this is prompt-surface and experiment-design control, not taxonomy classification |
| literature-grounded | None | Not needed for this local design decision |
| model inference | Formal manipulation-validity and identifiability analysis | Used only after source review |

## Q3 - Prompt Surface Construction

Decision: **B - keep rule 1 plus an H1a-native minimal task instruction.**

### Rationale

H1a's dependent variable is the model's `select_type` versus `defer` behavior
under two source-authority/liveness prohibition surfaces. Therefore the prompt
must not contain an independent rule that decides `defer` before the
manipulation can act.

The supplied measurements show that directly inheriting E2.4 rules 1-7 is not
schema-neutral:

- the preamble names `server_response`, but H1a removed that payload field
- the preamble and rules use `repair`, `abstain`, and `accept_report`, which are
  not H1a decisions
- rules 5-7 require audit and repair fields absent from `h1a_observation_v1`
- rule 3 step 4 maps the exact H1a fixture shape to `selected_type = null`

The last point is decisive. H1a's fixture contains explicit doc evidence for
`essential_feature` and explicit code evidence for `structural_composition`.
Rule 3 step 4 says that when incompatible types tie at the highest strength,
the model must leave `selected_type` null and must not break the tie. In H1a's
schema that is `defer`. If this rule remains, both arms can be pushed into a
defer ceiling by a rule that is independent of the liveness-prohibition
manipulation.

Option A would only be admissible if rule 3's tie clause were known to be
manipulation-neutral. The supplied document says this clause has never actually
been exercised in the project. Treating it as neutral would be an unsupported
assumption.

Option C would remove the immediate tie-ceiling clause, but it does so by
editing a non-liveness rule after Q1 has already defined the manipulation as
semantic removal of liveness/source-priority prohibitions. It also leaves rule
3 procedurally incomplete.

Accordingly, H1a should use an H1a-native prompt surface:

1. Preserve the packet-boundary part of rule 1 in both arms.
2. Apply Q1's semantic removal to all liveness, source-priority, recency,
   authority, and supersession prohibitions.
3. Replace E2.4 rules 2-7 with a short H1a-specific task instruction that
   matches `h1a_observation_v1`.
4. Keep the response schema unchanged.
5. Freeze both rendered prompt hashes before any diagnostic or main trial.

### Q3.1 - Does rule 3's "plausibility" cover recency/authority?

Decision: **Yes, operationally.**

Even if the word "plausible" is narrower than recency or authority in ordinary
language, rule 3 step 4 is algorithmic: if incompatible types tie at the
highest claim strength, selected_type is null. The rule gives no registered
channel for source priority, recency, authority, or liveness to break the tie.
So under H1a it functionally covers, or at least suppresses, the behavior the
manipulation is meant to observe.

### Q3.2 - Schema expansion if option A were chosen

Not applicable. **Do not choose A.**

If A is nevertheless forced by an external decision, the only coherent version
would be an H3-style schema expansion with a separate `contract_assessment`
object for all fields demanded by rules 2-7. However, that would still not fix
the rule 3 defer ceiling. Schema expansion solves output validity, not
manipulation validity.

### Q3.3 - Preserve rule 2's evidence-reading discipline under B?

Decision: **Yes, but only as schema-neutral H1a task guidance.**

Preserve the useful part of rule 2: evidence text must directly speak to the
ontology type of the given concept/feature pair before it can support selecting
that type. But do not require the model to output E2.4 audit fields such as
`direct_support`, `indirect_context`, `ambiguous`, `out_of_scope`, or
`conflicts_with_evidence_ids`.

Recommended H1a-native prompt shape:

```text
You are an MCP client agent.

Input is a repo-derived evidence packet. Use only the packet fields presented
in this prompt. Do not use general ontology knowledge, OWL/GUFO background
knowledge, codebase memory, prior conversation context, or external sources.

Your task is to observe whether the packet evidence supports selecting one of
two ontology feature types for the supplied concept/feature pair, or whether
you defer.

Evidence-reading rule:
- Treat an evidence item as support only when its text directly states or
  clearly entails the ontology type of the supplied concept/feature pair.
- Evidence that merely mentions implementation details, examples, labels, or
  adjacent context without tying the concept/feature pair to one of the allowed
  types is not enough by itself.
- If you select a type, cite the evidence item ids that support that selection.
- If the packet evidence is not enough for you to select either allowed type,
  choose defer.

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

For the `PROHIBITION_KEPT` arm only, add the Q1-approved prohibition clauses in
their frozen locations. For the `PROHIBITION_REMOVED` arm, those clauses must be
absent. The two arms must otherwise be byte-identical apart from mechanically
necessary whitespace.

## Q4 - Auxiliary Interpretability Condition

Decision: **Approve, with one clarifying label.**

Approved text, revised only for precision:

```text
If all four diagnostic cells fall into the same modal behavior category
(`select_type` or `defer`), the diagnostic does not establish that the anchor
and prompt surface are free of ceiling effects. In that case, a null main
result is uninterpretable with respect to anchor or prompt-surface ceiling
effects.

This rule is not an additional trial, not a post-hoc exclusion, not a new
blocking rule, and not a new success criterion. It is a pre-freeze
interpretability condition for reading the diagnostic gate.
```

### Rationale

The Q2 diagnostic gate detects gross anchor sensitivity by checking whether an
anchor flip changes modal behavior or selected type. It does not prove the
absence of ceiling behavior when all cells look the same. If all four cells are
uniform, "no anchor sensitivity detected" is not equivalent to "the anchor and
prompt cannot be masking the treatment."

Because this condition was registered before any diagnostic trial, adds no
calls, changes no treatment, and does not exclude outputs, it is admissible as a
pre-freeze interpretability rule. It should be reported as a limitation on
null interpretation, not as a pass/fail criterion.

## Deferred

None. The supplied prompt and the visible prior H1a manipulation decision are
sufficient to decide Q3 and Q4.

## New Constraints

- H1a must not inherit E2.4 rules 2-7 wholesale.
- H1a must use a prompt surface written against `h1a_observation_v1`.
- The existing H1a schema should remain unchanged unless a later decision
  explicitly reopens it.
- The prompt must not contain a hard tie rule that maps the known H1a fixture
  shape to `defer` independently of the prohibition manipulation.
- Evidence-reading discipline may be preserved only as schema-neutral guidance,
  not as hidden audit obligations or extra output fields.
- Both arms must keep identical fixture, payload whitelist, evidence order,
  model, parameters, schema, and coder.
- The only arm difference must be the Q1-approved semantic
  liveness/source-priority prohibition surface.
- Diagnostic uniformity across all four cells limits null interpretability; it
  must not be represented as proof of anchor noninterference.

## Experiment Status

실험 진행 여부: **재정의 필요**

사유:

The existing E2.4 prompt body is not compatible with H1a's schema or estimand.
The experiment may continue only after an H1a-native prompt surface is written,
the Q1 prohibition clauses are applied to that surface, the Q4 interpretability
condition is recorded, and all prompt/schema hashes are frozen before the first
trial.
