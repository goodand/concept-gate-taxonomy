---
id: proc-evidence-first-decision
type: procedure
title: Evidence-First Contract Decision
status: active
project: ontology-reasoner-mcp
summary: source confinement → evidence audit → sufficiency → invariant → accept/repair/abstain 순서를 강제하는 절차.
keywords:
  - evidence-first
  - evidence audit
  - sufficiency gate
  - invariant check
  - final decision
---

# Evidence-First Contract Decision

1. Packet 밖 정보 사용을 금지한다.
2. 관련 evidence item을 audit한다.
3. 각 feature/type 판단의 sufficiency를 정한다.
4. 충분한 판단에 한해서 global invariant를 검사한다.
5. `accept_report`, `repair`, `abstain` 중 하나를 선택한다.
6. Repair는 complete-state와 evidence citation을 보존한다.
7. Abstain은 필요한 추가 evidence를 요청한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `requires` → [[concept-repo-derived-evidence]]
- `requires` → [[concept-evidence-sufficiency]]
- `requires` → [[concept-global-feature-type-invariant]]
- `requires` → [[concept-complete-state-contract]]
- `gates` → [[concept-abstain-repair-contract]]
