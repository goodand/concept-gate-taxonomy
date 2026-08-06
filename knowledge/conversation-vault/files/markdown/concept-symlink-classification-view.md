---
id: concept-symlink-classification-view
type: concept
title: Relative Symlink Classification View
status: active
project: ontology-reasoner-mcp
summary: canonical file을 복제하지 않고 node type·project·topic·status 분류 tree에 투영하는 상대 심링크 view.
keywords:
  - relative symlink
  - classification view
  - canonical file
  - faceted navigation
  - no duplication
---

# Relative Symlink Classification View

실제 파일은 `files/<format>/`에 한 번만 둔다. `views/`는 node type, project, topic, status라는 독립 facet으로 같은 파일을 상대 심링크한다.

심링크는 탐색 projection이고 의미 관계의 권위 원장은 아니다. semantic authority는 stable ID 기반 manifest와 [[concept-typed-semantic-edge]]에 있다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[dec-vault-storage-graph]]
