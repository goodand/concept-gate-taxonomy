---
id: concept-global-feature-type-invariant
type: concept
title: Global Feature-Type Invariant
status: active
project: ontology-reasoner-mcp
summary: 동일 feature 이름은 그 feature를 가진 모든 concept에서 하나의 type으로 정규화되어야 한다는 전역 계약.
keywords:
  - global feature-type invariant
  - global consistency rule
  - feature identity
  - global state normalization
  - MixRig
---

# Global Feature-Type Invariant

> 동일 feature 이름은 그 feature를 가진 모든 concept에서 같은 type이어야 한다.

이 규칙은 concept별 local evidence를 독립적으로 정당화하는 대신 공유 feature의 전역 상태를 정규화하도록 요구한다. E2.2.3과 E2.3에서 중심 개입 A로 사용되었다.

E2.4에서는 이 invariant가 근거 충분성보다 앞설 수 없다. 목표 type을 직접 근거로 고를 수 없으면 통일 수리가 아니라 abstain이 필요하다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-feature-type-vocabulary]]
- `depends_on` → [[concept-evidence-sufficiency]]
