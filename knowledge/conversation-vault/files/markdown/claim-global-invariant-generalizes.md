---
id: claim-global-invariant-generalizes
type: claim
title: Global Invariant Generalizes Across E2.3 Screens
status: supported
project: ontology-reasoner-mcp
summary: E2.3 screening은 global feature-type invariant가 새 어휘·paraphrase·topology·decoy 조건에서 높은 통과율을 보였음을 지지한다.
keywords:
  - generalization claim
  - E2.3 result
  - screened not confirmed
  - global invariant
  - protocol bounded
---

# Global Invariant Generalizes Across E2.3 Screens

E2.3은 A_ONLY 10/10, A_PARAPHRASE 9/10, A_TOPOLOGY 9/10, A_DECOY 10/10을 보고했다. 이 수치는 특정 fixture 문구만의 효과라는 설명보다 의미 규칙의 일반화를 지지한다.

## Boundaries

- `confirmed`가 아니라 `screened`다.
- CONTROL은 0/2 sanity check이며 full N=10 결과가 아니다.
- 실제 repo-derived evidence에서의 작동은 E2.4 이전에는 알 수 없다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `stated_in` → [[src-repo-experiment-files-2026-07]]
- `depends_on` → [[exp-e2-3-generalization]]
- `motivates` → [[exp-e2-4-repo-contract]]
