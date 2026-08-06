---
id: claim-open-status-date-bound
type: claim
title: Open-Problem Status Must Be Date-Bound
status: supported
project: ontology-reasoner-mcp
summary: 미해결 여부는 고정 속성이 아니라 최신 문헌 근거와 as-of 날짜가 필요한 claim이라는 설계 원칙.
keywords:
  - open problem status
  - date-bound claim
  - literature evidence
  - uncertainty
  - hallucination mitigation
---

# Open-Problem Status Must Be Date-Bound

오픈 문제 페이지가 “이미 해결되었을 수 있다”고 경고한다면, 모델은 페이지 문구만으로 현재 상태를 확정해서는 안 된다. 검색 날짜와 supporting/contradicting source를 붙이고, 불충분하면 `uncertain`으로 남겨야 한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[concept-problem-status-claim]]
- `depends_on` → [[proc-literature-first-research]]
- `stated_in` → [[src-conversation-context-2026-07]]
