---
id: src-conversation-context-2026-07
type: source_record
title: Conversation Context Snapshot — 2026-07
status: partial
project: ontology-reasoner-mcp
summary: 현재 제공된 대화 요약과 메시지 구간을 범위 제한과 함께 보존한 source record.
keywords:
  - conversation provenance
  - context coverage
  - MCP isolation
  - E2 experiments
  - vault architecture
---

# Conversation Context Snapshot — 2026-07

이 노트는 전체 원문이라고 주장하지 않는다. 현재 세션에 제공된 프로젝트 대화 요약, 외부 메시지 330–363, 현재 요청을 정규화한 기록이다. 제품이 생략한 과거 메시지는 복원하지 않았다.

## 포함된 흐름

- MCP 결과와 모델 해석을 분리하는 context-isolation 실험
- `is-a`와 `has-a`/`part-of` 혼동 문제
- E2.2.1 → E2.2.2 → E2.2.3 → E2.3 실험 전개
- E2.4 repo-grounded evidence contract 설계
- 파일 형식별 canonical storage와 심링크/백링크 그래프 설계
- open problem을 위한 literature-first gate

## Provenance

- 원시 범위 설명: `files/text/available-context-snapshot.txt`
- 구조화 사건 목록: `files/json/conversation_extract.json`
- repo 근거 목록: [[src-repo-experiment-files-2026-07]]

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `motivates` → [[dec-vault-storage-graph]]
- `motivates` → [[proc-vault-ingestion]]
