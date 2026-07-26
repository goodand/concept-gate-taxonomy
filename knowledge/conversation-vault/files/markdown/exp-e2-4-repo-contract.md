---
id: exp-e2-4-repo-contract
type: experiment
title: E2.4 — Repo-Grounded Evidence Contract
status: designed
project: ontology-reasoner-mcp
summary: CONTROL_REPO, A_REPO, CONTRACT_REPO로 repo evidence 앞의 claim·abstain·repair 경계를 검증하도록 설계된 미실행 bridge 실험.
keywords:
  - E2.4
  - CONTROL_REPO
  - A_REPO
  - CONTRACT_REPO
  - repo-grounded evidence
  - design only
---

# E2.4 — Repo-Grounded Evidence Contract

E2.4는 invariant 자체보다 실제 repo evidence에서 확정·보류·수리 경계를 지키는지 시험하도록 설계되었다.

| arm | prompt/schema | 목적 |
|---|---|---|
| `CONTROL_REPO` | ordinary prompt + legacy schema | 과확정·과수리 baseline |
| `A_REPO` | global invariant + legacy schema | A 규칙의 repo evidence 전이 |
| `CONTRACT_REPO` | audit → sufficiency → invariant → decision | evidence contract 효과 |

Fixture family는 `sufficient_consistent`, `sufficient_repairable`, `insufficient`, `conflicting` 네 class가 제안되어 있다.

## 현재 상태

README, input/output schema, prompt block만 작성됐다. Fixture, hidden oracle, extractor, scorer, prompt generator, trials, 결과 보고서는 아직 없다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `depends_on` → [[concept-repo-derived-evidence]]
- `depends_on` → [[concept-global-feature-type-invariant]]
- `tests` → [[concept-evidence-sufficiency]]
- `tests` → [[concept-abstain-repair-contract]]
- `depends_on` → [[dec-repo-evidence-source]]
- `depends_on` → [[loop-e2-4-scorer-fixtures]]
- `derived_from` → [[src-repo-experiment-files-2026-07]]
