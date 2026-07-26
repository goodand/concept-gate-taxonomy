---
id: proc-vault-ingestion
type: procedure
title: Vault Ingestion and Graph Enrichment
status: active
project: ontology-reasoner-mcp
summary: source 보존, atomic note 분해, subagent 요약·키워드·edge 제안, main-agent 검증, view 재생성을 수행하는 절차.
keywords:
  - vault ingestion
  - atomic notes
  - subagent enrichment
  - keyword normalization
  - edge review
---

# Vault Ingestion and Graph Enrichment

1. 제공된 source와 coverage limit를 보존한다.
2. 파일을 source, concept, claim, procedure, experiment, decision, open loop로 분해한다.
3. 각 canonical file을 형식별 storage에 저장한다.
4. Subagent가 파일별 summary와 keyword를 추출한다.
5. Subagent가 제한 vocabulary로 edge 후보를 제안한다.
6. Main agent가 repo 근거, domain/range, status를 검토한 edge만 채택한다.
7. Builder가 manifest, keyword graph, backlink index, symlink views를 재생성한다.
8. 해시·JSON·wikilink·symlink·graph 무결성을 검증한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `requires` → [[concept-typed-semantic-edge]]
- `requires` → [[concept-symlink-classification-view]]
- `depends_on` → [[dec-vault-storage-graph]]
