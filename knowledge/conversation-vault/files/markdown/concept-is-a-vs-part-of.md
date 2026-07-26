---
id: concept-is-a-vs-part-of
type: concept
title: is-a vs has-a/part-of Boundary
status: active
project: ontology-reasoner-mcp
summary: 분류적 포함과 구성적 분해를 분리하여 코드·이름·기능을 잘못 taxonomy edge로 만들지 않게 하는 경계.
keywords:
  - is-a
  - has-a
  - part-of
  - taxonomy DAG
  - structural composition
---

# is-a vs has-a/part-of Boundary

`is-a`는 분류적 관계이고 `has-a`/`part-of`는 구성적 관계다. ConceptGate에서 essential feature 기반 포함은 taxonomy DAG를 만들 수 있지만, 위치·기능·사회적 취급·구성 부분은 같은 방식으로 parent–child edge를 만들면 안 된다.

코드나 이름을 개념으로 다룰 때 “모듈에 함수가 있다”와 “모듈이 함수의 종류다”를 혼동하는 것이 대표적 실패다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-feature-type-vocabulary]]
