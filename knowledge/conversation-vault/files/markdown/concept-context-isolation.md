---
id: concept-context-isolation
type: concept
title: MCP Context Isolation
status: active
project: ontology-reasoner-mcp
summary: MCP 평가에서 허용된 입력과 tool output만 사용하고 이전 대화·메모리·배경지식의 영향을 차단하는 실험 원칙.
keywords:
  - MCP context isolation
  - context contamination
  - source confinement
  - cold context
  - tool output separation
---

# MCP Context Isolation

MCP 자체의 판단 능력을 시험하려면 입력 fixture, MCP 출력, 모델 해석을 분리하고 허용하지 않은 context를 배제해야 한다. 현재 대화에서는 “MCP 출력”과 “모델의 해석”을 별도 섹션으로 보고하고, 입력이 부족하면 추정하지 않는 방식이 반복적으로 요구되었다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `requires` → [[concept-repo-derived-evidence]]
- `refines` → [[proc-evidence-first-decision]]
