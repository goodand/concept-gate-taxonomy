---
id: concept-abstain-repair-contract
type: concept
title: Claim–Abstain–Repair Contract
status: active
project: ontology-reasoner-mcp
summary: 근거 audit와 sufficiency 판정 뒤 accept_report, repair, abstain을 선택하게 하는 reasoning contract.
keywords:
  - claim abstain repair
  - reasoning contract
  - mandatory abstention
  - repairability
  - missing evidence
---

# Claim–Abstain–Repair Contract

이 계약은 “잘 고치는가”뿐 아니라 “고칠 수 없을 때 멈추는가”를 다룬다.

- 현재 상태가 충분히 지지되면 `accept_report`.
- target type이 충분히 지지되고 전역 invariant 위반이 수리 가능하면 `repair`.
- evidence가 부족·다의적·충돌하거나 packet 밖 지식이 필요하면 `abstain`.

`abstain`은 수리 결과를 비워 두고 필요한 concept/feature/relation 근거를 구체적으로 요청해야 한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[concept-evidence-sufficiency]]
- `depends_on` → [[concept-complete-state-contract]]
- `refines` → [[concept-global-feature-type-invariant]]
