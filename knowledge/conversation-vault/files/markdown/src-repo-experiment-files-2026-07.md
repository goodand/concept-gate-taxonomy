---
id: src-repo-experiment-files-2026-07
type: source_record
title: Repo Experiment Source Set — E2.2.1 to E2.4
status: captured
project: ontology-reasoner-mcp
summary: 실험 노트의 사실·수치·설계 상태를 확인하는 데 사용한 repository source set.
keywords:
  - repo provenance
  - experiment README
  - trial data
  - decision schema
  - concept-gate-taxonomy
---

# Repo Experiment Source Set — E2.2.1 to E2.4

기준 worktree는 `repo-e24-contract-design`이다. 다음 파일군을 source로 사용했다.

- `experiments/2026-07-24_e2.2.1_directed_pc_vocabulary_fix/`
- `experiments/2026-07-24_e2.2.2_directed_pc_invariant_fix/`
- `experiments/2026-07-25_e2.2.3_directed_pc_ablation/`
- `experiments/2026-07-25_e2.3_global_invariant_generalization/`
- `experiments/2026-07-25_e2.4_repo_grounded_contract/`
- `docs/obligation_layer_roadmap.md`
- `experiments/README.md`

Subagent는 E2.2.1–E2.3의 `trials.json`을 각 `evaluate.py`로 재채점하고 provenance 검증 통과를 보고했다. E2.4는 설계 packet만 존재하며 trial 실행 결과는 없다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `supports` → [[claim-global-invariant-generalizes]]
- `supports` → [[claim-e2-4-design-only]]
