---
id: dec-repo-evidence-source
type: decision
title: E2.4 Repository-Only Evidence Source
status: active
project: ontology-reasoner-mcp
summary: E2.4 evidence를 goodand/concept-gate-taxonomy 자체의 명시적 repo artifact로 한정한다는 결정.
keywords:
  - repository-only evidence
  - goodand/concept-gate-taxonomy
  - source policy
  - E2.4
  - commit provenance
---

# E2.4 Repository-Only Evidence Source

## Decision

E2.4의 유일한 evidence source는 `goodand/concept-gate-taxonomy` 저장소다.

허용 대상은 명시적 docstring/comment, 문서, expected behavior를 직접 encode한 테스트·fixture, SHA와 정확한 excerpt를 포함한 commit message다. 외부 문헌, 외부 repo, 일반 ontology/OWL/GUFO 지식, 경로명이나 symbol name만으로 만든 추론은 금지한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `gates` → [[exp-e2-4-repo-contract]]
- `refines` → [[concept-repo-derived-evidence]]
- `stated_in` → [[src-repo-experiment-files-2026-07]]
