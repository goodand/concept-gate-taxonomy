---
id: concept-complete-state-contract
type: concept
title: Complete-State Repair Contract
status: active
project: ontology-reasoner-mcp
summary: repair 결과가 변경 diff가 아니라 입력의 모든 concept와 feature를 보존한 완전 상태여야 한다는 계약.
keywords:
  - complete-state contract
  - full-set preservation
  - destructive repair
  - repaired_concepts
  - structural preservation
---

# Complete-State Repair Contract

수리 출력은 변경된 concept 하나만 반환하는 diff가 아니라 입력의 전체 concept/feature 상태를 반환해야 한다. E2.2.2에서는 prompt 규칙과 `minItems: 2`가 함께 적용되었고, E2.2.3은 prompt 규칙 B와 schema 강제 C를 분리했다.

E2.4는 이 원칙을 더 일반화해 이름 변경·추가·삭제도 명시 근거 없이는 금지한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-abstain-repair-contract]]
