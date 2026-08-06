---
id: dec-e2-screening-policy
type: decision
title: E2 Screening and Futility Policy
status: provisional
project: ontology-reasoner-mcp
summary: E2.4 실행 비용 정책으로 core arm-cell당 N=10, threshold 0.90, 두 실패 시 futility stop을 사용하는 제안.
keywords:
  - N=10
  - threshold 0.90
  - two-failure futility stop
  - screening
  - E2.4
---

# E2 Screening and Futility Policy

E2.4 design packet은 core arm-cell당 N=10, threshold 0.90으로 시작하고, 두 실패가 발생해 threshold 달성이 불가능해지면 arm을 중단하는 방식을 제안한다.

이 정책은 CONTRACT_REPO의 의미 계약이 아니라 실행 비용 정책이며, 정확한 arm × fixture matrix가 preregister될 때 확정해야 한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `gates` → [[loop-e2-4-execution]]
- `derived_from` → [[exp-e2-3-generalization]]
