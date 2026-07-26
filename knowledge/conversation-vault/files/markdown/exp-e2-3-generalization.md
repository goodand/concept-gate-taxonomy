---
id: exp-e2-3-generalization
type: experiment
title: E2.3 — Global Invariant Generalization
status: screened
project: ontology-reasoner-mcp
summary: 새 어휘·paraphrase·복잡 topology·강한 decoy에서 global invariant 효과를 2-stage protocol로 screening한 실험.
keywords:
  - E2.3
  - global invariant generalization
  - paraphrase invariance
  - topology generalization
  - decoy resistance
  - adaptive screening
---

# E2.3 — Global Invariant Generalization

## 질문

E2.2.3의 A 규칙 효과가 단일 fixture의 어휘와 구조를 넘어서는가?

## Screening 결과

| arm | 결과 | protocol label |
|---|---:|---|
| `CONTROL` | 0/2 | sanity check |
| `A_ONLY` | 10/10 | screened |
| `A_PARAPHRASE` | 9/10 | screened |
| `A_TOPOLOGY` | 9/10 | screened |
| `A_DECOY` | 10/10 | screened |

이 결과는 일반화를 지지하지만 protocol상 `confirmed`라고 부르지 않는다. CONTROL은 full N=10이 아니라 N=2 sanity check다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `generalizes` → [[exp-e2-2-3-ablation]]
- `tests` → [[concept-global-feature-type-invariant]]
- `supports` → [[claim-global-invariant-generalizes]]
- `motivates` → [[exp-e2-4-repo-contract]]
- `derived_from` → [[src-repo-experiment-files-2026-07]]
