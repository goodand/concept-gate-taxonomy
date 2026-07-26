---
id: loop-e2-4-execution
type: open_loop
title: Execute E2.4 Repo-Grounded Trials
status: blocked
project: ontology-reasoner-mcp
summary: fixture·scorer·provenance preregistration 뒤 CONTROL_REPO/A_REPO/CONTRACT_REPO를 실행해야 하는 open loop.
keywords:
  - E2.4 execution
  - cold context
  - CONTROL_REPO
  - A_REPO
  - CONTRACT_REPO
---

# Execute E2.4 Repo-Grounded Trials

실행은 [[loop-e2-4-scorer-fixtures]]가 닫힌 뒤에만 가능하다. Prompt/manifest hash, model, context isolation, tool access, raw response를 보존하고, 실행 후에만 E2.4를 검증된 결과로 승격할 수 있다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[loop-e2-4-scorer-fixtures]]
- `depends_on` → [[dec-e2-screening-policy]]
- `requires` → [[concept-context-isolation]]
