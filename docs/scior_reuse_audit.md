# Scior Reuse Audit

Date: 2026-07-05
Target: ConceptGate v7 is-a/has-a formal validation

## Summary

Scior was added as a read-only subtree under `vendor/scior` because the FOIS
2023 gUFO rules paper provides an actual Python implementation and rule
catalog. ConceptGate does not import Scior at runtime because Scior depends on
`rdflib` and `owlrl`. Instead, ConceptGate reuses Scior's rule metadata through
`cg_gufo.py`, a stdlib-only adapter.

## Reuse Decision

| Scior asset | Decision | Reason |
|---|---|---|
| `documentation/resources/rules_implementation.tsv` | Reuse via adapter | Stable rule code, base-rule mapping, and FOL text |
| `documentation/resources/rules_theoretical.tsv` | Reference | Useful for R01-R37 mapping and documentation |
| `scior/modules/rules/rule_group_ufo_all.py` | Reference, not import | Confirms RA02/RA03 behavior but imports rdflib |
| `tests/test_files/*_in.ttl`, `*_out.ttl` | Reference fixtures | Useful for future benchmark-style tests |
| Scior CLI runtime | Do not import | Pulls runtime dependencies into ConceptGate core |
| Alloy rules | Reference | Useful for formal comparison, not needed in stdlib core |

## Rules Selected First

| Theoretical | Scior impl | ConceptGate use |
|---|---|---|
| R22 | RA02 | Rigid child cannot have anti-rigid parent |
| R23 | RA03 | Semi-rigid child cannot have anti-rigid parent |
| R28 | RU01 | Sortal has exactly one Kind ancestor; future seed-gate candidate |

## Current Implementation

- `vendor/scior` is a git subtree.
- `cg_gufo.py` loads Scior's `rules_implementation.tsv` when present.
- `cg_gufo.py` has a minimal fallback so `files/`-only MCP installs still work.
- `OntoCleanMetaGate` includes Scior RA02/R22 reference metadata on rigidity
  violations.
- `RelationDiscriminationGate` blocks `type`/`relation_hint` contradictions
  before concepts enter the is-a DAG.

## Constraints

- Do not edit files under `vendor/scior`.
- Do not add `rdflib` or `owlrl` to ConceptGate core dependencies.
- Do not infer `rigid` from `essential_feature` as a hard rule.
- Use explicit seeds (`ontoclean`, `relation_hint`, later `gufo_category`) for
  hard gate decisions.

## Next Reuse Candidates

1. Use Scior TTL fixtures to create a small stdlib regression set for RA02/RA03.
2. Add seed-based RU01 checks only after a stable `gufo_category` schema exists.
3. Keep full Scior runtime as a reference path, not a default execution path.
