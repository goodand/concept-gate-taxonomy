---
id: concept-problem-status-claim
type: concept
title: Date-Bound Problem-Status Claim
status: active
project: ontology-reasoner-mcp
summary: open·partial·resolved·uncertain 상태를 문제의 고정 속성이 아니라 날짜와 근거가 붙는 claim으로 모델링하는 개념.
keywords:
  - problem status
  - as-of date
  - open
  - resolved
  - uncertain
---

# Date-Bound Problem-Status Claim

“이 문제는 미해결이다”는 영구 속성이 아니다. `as_of`, supporting sources, contradicting sources, confidence를 가진 claim이어야 한다. 최신 문헌 확인이 불완전하면 `uncertain`을 유지한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-literature-first]]
