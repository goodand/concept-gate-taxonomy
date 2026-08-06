---
id: proc-literature-first-research
type: procedure
title: Literature-First Open-Problem Workflow
status: active
project: ontology-reasoner-mcp
summary: 원문 보존, 문헌 검색, 결과 비교, 날짜가 붙은 상태 claim, solution-attempt gate를 순서대로 수행하는 절차.
keywords:
  - literature-first workflow
  - literature search
  - open problem database
  - solution attempt gate
  - abstain
---

# Literature-First Open-Problem Workflow

1. 원문과 페이지 metadata를 source record로 보존한다.
2. 문제·사람·문헌을 canonical node로 정규화한다.
3. 최신 문헌 검색 activity를 실행한다.
4. 기존 결과와 부분 해결을 비교한다.
5. 날짜와 근거가 있는 problem-status claim을 만든다.
6. 근거가 충돌하거나 검색이 불완전하면 `uncertain`으로 둔다.
7. 여전히 미해결이라는 근거가 확보된 뒤에만 새 solution attempt를 허용한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `requires` → [[concept-literature-first]]
- `requires` → [[concept-problem-status-claim]]
- `gates` → [[claim-open-status-date-bound]]
