---
id: exp-e2-2-2-invariant
type: experiment
title: E2.2.2 — Directed PC Invariant Fix
status: completed
project: ontology-reasoner-mcp
summary: global consistency, complete-state prompt, schema minItems를 결합해 20/20을 얻었지만 요인별 기여는 식별하지 못한 실험.
keywords:
  - E2.2.2
  - global consistency
  - complete state
  - schema minItems
  - 20/20
---

# E2.2.2 — Directed PC Invariant Fix

## 질문

Vocabulary만으로 부족했던 수리를 전역 일관성(A), complete-state(B), fixture-specific `minItems: 2`(C)의 결합으로 회복할 수 있는가?

## 결과

- N=20
- 결과: 20/20 = 1.00, `GO`
- 제한: A/B/C를 동시에 적용했으므로 어떤 요인이 필요하거나 충분했는지 식별할 수 없음

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[exp-e2-2-1-vocabulary]]
- `tests` → [[concept-global-feature-type-invariant]]
- `tests` → [[concept-complete-state-contract]]
- `motivates` → [[exp-e2-2-3-ablation]]
- `derived_from` → [[src-repo-experiment-files-2026-07]]
