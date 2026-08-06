---
id: exp-e2-2-3-ablation
type: experiment
title: E2.2.3 — Directed PC OFAT Ablation
status: completed
project: ontology-reasoner-mcp
summary: A/B/C를 단독 arm으로 분리해 A_ONLY 20/20, B_ONLY 1/20, C_ONLY 0/20을 관측한 진단 실험.
keywords:
  - E2.2.3
  - OFAT ablation
  - A_ONLY
  - B_ONLY
  - C_ONLY
  - factor sufficiency
---

# E2.2.3 — Directed PC OFAT Ablation

Vocabulary baseline 위에서 세 요인을 하나씩 켰다.

| arm | 요인 | 결과 |
|---|---|---:|
| `A_ONLY` | global consistency prompt | 20/20 |
| `B_ONLY` | complete-state prompt | 1/20 |
| `C_ONLY` | schema `minItems: 2` | 0/20 |

이 fixture에서는 A가 단독 충분했다. 그러나 B+C 조합 arm이 없으므로 A의 필요성은 알 수 없고, fixture 밖 일반화도 아직 확정할 수 없었다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[exp-e2-2-2-invariant]]
- `tests` → [[concept-global-feature-type-invariant]]
- `tests` → [[concept-complete-state-contract]]
- `motivates` → [[exp-e2-3-generalization]]
- `derived_from` → [[src-repo-experiment-files-2026-07]]
