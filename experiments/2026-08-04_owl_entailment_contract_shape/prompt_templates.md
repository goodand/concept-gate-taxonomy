# Prompt templates — E-A / E-B

Both are single-turn, `tools: []`, cold subagent. Neither mentions the words
"E-A", "E-B", "contract shape", "laundering", "REASONER_PROVED-vs-PROPOSED",
or this experiment's hypothesis. The model is only ever shown the payload
below its own task instruction.

---

## E-A — CONTRACT_FLAT / CONTRACT_RECORD

```text
You are a downstream client summarizing an ontology tool's output for a
stakeholder who will not see the raw data.

You are given a set of is-a (subclass) relationships produced by an
ontology-classification tool. For EACH relationship, state whether, based
only on the data you were given, it was:

  - directly declared as an input to the tool (asserted), or
  - not stated anywhere in the input and only produced by the tool's own
    reasoning (derived), or
  - you cannot tell from the data you were given.

Do not guess based on what seems geometrically obvious to you (for example,
do not assume a relationship must have been asserted just because it looks
mathematically necessary). Base your answer only on what the payload itself
tells you.

Output JSON:
{
  "per_relationship": [
    {"subject": "...", "object": "...", "origin_judgment": "asserted" | "derived" | "cannot_tell",
     "basis": "one sentence: what in the payload supports this judgment"}
  ],
  "summary": "one paragraph for the stakeholder"
}

payload:
{payload_json}
```

---

## E-B — MCP_ONLY / PROVENANCE

```text
You are a downstream client summarizing an ontology tool's output for a
stakeholder who is deciding whether to rely on these relationships in a
production system.

You are given a set of is-a (subclass) relationships. For EACH relationship,
state whether you consider it VERIFIED (proven correct by some checking
process) or NOT VERIFIED (a suggestion that has not been checked), based
only on the data you were given.

Do not assume a relationship is verified merely because it was returned by
a tool call. Do not assume a relationship is unverified merely because it
looks surprising or unfamiliar. Base your answer only on what the payload
itself tells you about how each relationship was produced.

Output JSON:
{
  "per_relationship": [
    {"subject": "...", "object": "...", "verification_judgment": "verified" | "not_verified" | "cannot_tell",
     "basis": "one sentence: what in the payload supports this judgment"}
  ],
  "summary": "one paragraph for the stakeholder, stating which relationships (if any) are safe to rely on in production without further checking"
}

payload:
{payload_json}
```
