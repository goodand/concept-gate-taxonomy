---
id: concept-literature-first
type: concept
title: Literature-First Research
status: active
project: ontology-reasoner-mcp
summary: 오픈 문제에 새 풀이를 시도하기 전에 최신 문헌에서 기존 해결·부분 해결·상태를 확인하는 연구 원칙.
keywords:
  - literature-first
  - open problem
  - retrieval
  - hallucination mitigation
  - research context
---

# Literature-First Research

오픈 문제 원문은 문제 진술뿐 아니라 제안자, 부분 해결, 참고문헌, 페이지 수정일을 함께 포함할 수 있다. 따라서 모델은 먼저 문헌을 검색하고 알려진 결과와 비교한 뒤, 여전히 미해결이라는 근거가 있을 때만 새 풀이를 시도해야 한다.

실행 절차는 [[proc-literature-first-research]]에 둔다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[concept-problem-status-claim]]
