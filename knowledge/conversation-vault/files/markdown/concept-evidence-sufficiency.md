---
id: concept-evidence-sufficiency
type: concept
title: Evidence Sufficiency
status: active
project: ontology-reasoner-mcp
summary: packet 안의 direct support가 선택한 판단을 명시적으로 지지하고 동등한 직접 충돌이 없을 때만 확정을 허용하는 기준.
keywords:
  - evidence sufficiency
  - direct support
  - conflicting evidence
  - evidence audit
  - packet-only
---

# Evidence Sufficiency

E2.4 설계에서 판단은 다음 조건을 만족할 때만 `sufficient`다.

1. 선택한 type을 지지하는 `direct_support`가 최소 하나 있다.
2. 양립 불가능한 type을 지지하는 동등한 직접 근거가 없다.
3. packet 안의 evidence ID를 인용한다.
4. 명시되지 않은 repo 지식이나 일반 배경지식에 의존하지 않는다.

간접 문맥, 다의적 근거, 누락, 직접 충돌은 `insufficient` 또는 `conflicting`으로 라우팅한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `gates` → [[concept-abstain-repair-contract]]
- `depends_on` → [[concept-repo-derived-evidence]]
