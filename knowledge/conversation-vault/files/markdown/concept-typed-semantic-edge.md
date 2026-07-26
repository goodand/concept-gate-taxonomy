---
id: concept-typed-semantic-edge
type: concept
title: Typed Semantic Edge
status: active
project: ontology-reasoner-mcp
summary: tree로 표현할 수 없는 의미 관계를 stable node ID, 제한 relation, 근거, confidence로 기록하는 그래프 단위.
keywords:
  - typed edge
  - semantic graph
  - stable ID
  - domain range validation
  - backlink index
---

# Typed Semantic Edge

심링크는 다중 분류를 보여 주지만 “왜 연결되었는가”를 표현하지 못한다. typed edge는 `from`, `relation`, `to`, `evidence`, `rationale`, `confidence`를 보존한다.

관계 vocabulary는 `is_a`, `part_of`, `derived_from`, `supports`, `tests`, `motivates`, `depends_on`, `gates` 같은 제한 집합만 허용한다. 역링크는 edge 원장에서 계산한다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[concept-symlink-classification-view]]
