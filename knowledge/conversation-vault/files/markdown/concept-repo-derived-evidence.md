---
id: concept-repo-derived-evidence
type: concept
title: Repo-Derived Evidence
status: active
project: ontology-reasoner-mcp
summary: 특정 commit의 코드·문서·테스트·fixture·캡처된 commit message에서 명시적 span으로 추출한 evidence.
keywords:
  - repo-derived evidence
  - source confinement
  - commit provenance
  - evidence packet
  - exact excerpt
---

# Repo-Derived Evidence

E2.4에서 evidence는 특정 commit에 묶인 명시 텍스트다. 경로명이나 symbol name만으로는 direct support가 될 수 없다. evidence item은 source path, source kind, locator, exact text, text SHA-256, extraction note를 가진다.

현재 source repository 결정은 [[dec-repo-evidence-source]]에 기록한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-context-isolation]]
