---
id: dec-vault-storage-graph
type: decision
title: Format Storage, Symlink Views, Typed Graph
status: active
project: ontology-reasoner-mcp
summary: 실제 파일은 형식별로 한 번 저장하고 분류는 심링크, 의미 관계는 Obsidian 링크와 typed edge로 표현한다는 결정.
keywords:
  - format-first storage
  - canonical storage
  - symlink views
  - Obsidian backlinks
  - typed edge ledger
---

# Format Storage, Symlink Views, Typed Graph

## Decision

1. 실제 파일은 `files/<format>/`에 한 번만 저장한다.
2. 개념적 tree 분류는 `views/`의 상대 심링크로 만든다.
3. tree로 표현할 수 없는 의미 관계는 Markdown wikilink와 `edges.jsonl`에 기록한다.
4. stable ID는 파일명과 content hash에서 분리한다.
5. 심링크는 탐색용이며 typed edge 원장이 관계의 정식 표현이다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `motivates` → [[proc-vault-ingestion]]
- `supports` → [[concept-symlink-classification-view]]
- `supports` → [[concept-typed-semantic-edge]]
- `stated_in` → [[src-conversation-context-2026-07]]
