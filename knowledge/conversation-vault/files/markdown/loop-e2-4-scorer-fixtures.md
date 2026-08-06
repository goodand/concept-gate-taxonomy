---
id: loop-e2-4-scorer-fixtures
type: open_loop
title: Implement E2.4 Fixtures and Deterministic Scorer
status: open
project: ontology-reasoner-mcp
summary: four-class fixture, hidden oracle, provenance validator, cross-field semantic scorer를 구현해야 하는 open loop.
keywords:
  - E2.4 fixtures
  - hidden oracle
  - deterministic scorer
  - semantic constraints
  - provenance validator
---

# Implement E2.4 Fixtures and Deterministic Scorer

필요한 작업:

- 실행 commit SHA 고정
- `sufficient_consistent`, `sufficient_repairable`, `insufficient`, `conflicting` fixture 생성
- evidence ID uniqueness·existence, audit coverage, path/hash provenance 검증
- equal-strength conflict 규칙 형식화
- accept/repair/abstain cross-field 제약 완결
- full concept/feature preservation 검사

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[exp-e2-4-repo-contract]]
- `requires` → [[proc-evidence-first-decision]]
- `precedes` → [[loop-e2-4-execution]]
