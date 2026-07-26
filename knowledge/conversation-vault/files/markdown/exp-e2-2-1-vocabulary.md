---
id: exp-e2-2-1-vocabulary
type: experiment
title: E2.2.1 — Directed PC Vocabulary Fix
status: completed
project: ontology-reasoner-mcp
summary: 여섯 FeatureType vocabulary 노출만 시험했으며 3/20으로 0.80 기준에 미달한 단일-arm 실험.
keywords:
  - E2.2.1
  - vocabulary exposure
  - structural_composition
  - directed positive control
  - 3/20
---

# E2.2.1 — Directed PC Vocabulary Fix

## 질문

`structural_composition`을 포함한 여섯 FeatureType 값을 prompt와 schema에 노출하면 directed repair가 회복되는가?

## 설계와 결과

- `FULL` 단일 arm
- N=20, threshold=0.80
- 결과: 3/20 = 0.15, `NO_GO`
- 실패 분포: wrong-direction 11, destructive 6, correct 3

Vocabulary 노출은 소폭 개선을 만들었지만 충분하지 않았다. 이 실험만으로 vocabulary가 필요조건인지는 알 수 없다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `tests` → [[concept-feature-type-vocabulary]]
- `motivates` → [[exp-e2-2-2-invariant]]
- `derived_from` → [[src-repo-experiment-files-2026-07]]
