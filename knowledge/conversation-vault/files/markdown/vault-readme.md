---
id: moc-vault-root
type: map_of_content
title: Conversation Knowledge Vault
status: active
project: ontology-reasoner-mcp
summary: 파일 형식 저장소, 심링크 분류 views, Obsidian backlinks, typed edge graph의 진입점.
keywords:
  - knowledge vault
  - canonical storage
  - symlink view
  - Obsidian backlink
  - typed edge
---

# Conversation Knowledge Vault

이 vault는 **물리 저장과 의미 분류를 분리**한다.

- 실제 파일은 확장자/형식에 따라 `files/`에 한 번만 저장한다.
- `views/`는 node type, project, topic, status별 상대 심링크다.
- Markdown wikilink는 사람이 탐색하는 문맥 링크다.
- `graph/edges.jsonl`은 관계 이유와 근거를 보존하는 typed-edge 원장이다.
- `graph/keyword-edges.csv`는 파일별 핵심 키워드의 공출현과 명시 edge 연결을 집계한다.
- `manifests/files.jsonl`은 stable ID, hash, summary, keyword를 기록한다.

## 시작점

- 프로젝트 지도: [[moc-ontology-reasoner-mcp]]
- 구조 지도: [[moc-vault-architecture]]
- source coverage: [[src-conversation-context-2026-07]]
- repo sources: [[src-repo-experiment-files-2026-07]]

## 재생성

```bash
python3 scripts/build-vault.py --check
```

빌더는 views, backlink index, manifest, CSV index를 재생성하고 JSON·wikilink·relation domain/range·symlink 무결성을 검사한다.
