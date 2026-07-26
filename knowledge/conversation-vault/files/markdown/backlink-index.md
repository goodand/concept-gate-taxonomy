---
id: generated-backlink-index
type: map_of_content
generated: true
---

# Backlink Index

이 파일은 `build_vault.py`가 typed edge 원장에서 생성한 읽기 전용 탐색 view다.

## [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]]

Outbound:

- `depends_on` → [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] (`edge-080`)
- `motivates` → [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] (`edge-082`)
- `motivates` → [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]] (`edge-081`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-078`)
- `stated_in` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-079`)

Inbound:

- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `depends_on` (`edge-099`)
- [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] → `supports` (`edge-006`)

## [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]]

Outbound:

- `depends_on` → [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] (`edge-076`)
- `motivates` → [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] (`edge-077`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-074`)
- `stated_in` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-075`)

Inbound:

- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `supports` (`edge-038`)
- [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] → `supports` (`edge-005`)

## [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]]

Outbound:

- `depends_on` → [[concept-problem-status-claim|Date-Bound Problem-Status Claim]] (`edge-084`)
- `depends_on` → [[proc-literature-first-research|Literature-First Open-Problem Workflow]] (`edge-085`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-083`)
- `stated_in` → [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]] (`edge-086`)

Inbound:

- [[proc-literature-first-research|Literature-First Open-Problem Workflow]] → `gates` (`edge-069`)

## [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]]

Outbound:

- `depends_on` → [[concept-complete-state-contract|Complete-State Repair Contract]] (`edge-013`)
- `depends_on` → [[concept-evidence-sufficiency|Evidence Sufficiency]] (`edge-012`)
- `refines` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-014`)

Inbound:

- [[concept-evidence-sufficiency|Evidence Sufficiency]] → `gates` (`edge-010`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `gates` (`edge-065`)
- [[concept-complete-state-contract|Complete-State Repair Contract]] → `refines` (`edge-009`)
- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `tests` (`edge-045`)

## [[concept-complete-state-contract|Complete-State Repair Contract]]

Outbound:

- `refines` → [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] (`edge-009`)

Inbound:

- [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] → `depends_on` (`edge-013`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `requires` (`edge-064`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `tests` (`edge-026`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `tests` (`edge-032`)

## [[concept-problem-status-claim|Date-Bound Problem-Status Claim]]

Inbound:

- [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]] → `depends_on` (`edge-084`)
- [[concept-literature-first|Literature-First Research]] → `depends_on` (`edge-018`)
- [[proc-literature-first-research|Literature-First Open-Problem Workflow]] → `requires` (`edge-068`)

## [[concept-evidence-sufficiency|Evidence Sufficiency]]

Outbound:

- `depends_on` → [[concept-repo-derived-evidence|Repo-Derived Evidence]] (`edge-011`)
- `gates` → [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] (`edge-010`)

Inbound:

- [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] → `depends_on` (`edge-012`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `requires` (`edge-062`)
- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `tests` (`edge-044`)

## [[concept-global-feature-type-invariant|Global Feature-Type Invariant]]

Outbound:

- `refines` → [[concept-feature-type-vocabulary|Six-Type FeatureType Vocabulary]] (`edge-008`)

Inbound:

- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `depends_on` (`edge-043`)
- [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] → `refines` (`edge-014`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `requires` (`edge-063`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `tests` (`edge-025`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `tests` (`edge-031`)
- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `tests` (`edge-037`)

## [[concept-literature-first|Literature-First Research]]

Outbound:

- `depends_on` → [[concept-problem-status-claim|Date-Bound Problem-Status Claim]] (`edge-018`)

Inbound:

- [[proc-literature-first-research|Literature-First Open-Problem Workflow]] → `requires` (`edge-067`)

## [[concept-context-isolation|MCP Context Isolation]]

Inbound:

- [[concept-repo-derived-evidence|Repo-Derived Evidence]] → `refines` (`edge-015`)
- [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] → `requires` (`edge-093`)

## [[concept-symlink-classification-view|Relative Symlink Classification View]]

Outbound:

- `refines` → [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] (`edge-016`)

Inbound:

- [[concept-typed-semantic-edge|Typed Semantic Edge]] → `depends_on` (`edge-017`)
- [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] → `requires` (`edge-072`)
- [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] → `supports` (`edge-057`)

## [[concept-repo-derived-evidence|Repo-Derived Evidence]]

Outbound:

- `refines` → [[concept-context-isolation|MCP Context Isolation]] (`edge-015`)

Inbound:

- [[concept-evidence-sufficiency|Evidence Sufficiency]] → `depends_on` (`edge-011`)
- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `depends_on` (`edge-042`)
- [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]] → `refines` (`edge-050`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `requires` (`edge-061`)

## [[concept-feature-type-vocabulary|Six-Type FeatureType Vocabulary]]

Inbound:

- [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] → `refines` (`edge-008`)
- [[concept-is-a-vs-part-of|is-a vs has-a/part-of Boundary]] → `refines` (`edge-007`)
- [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] → `tests` (`edge-020`)

## [[concept-typed-semantic-edge|Typed Semantic Edge]]

Outbound:

- `depends_on` → [[concept-symlink-classification-view|Relative Symlink Classification View]] (`edge-017`)

Inbound:

- [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] → `requires` (`edge-071`)
- [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] → `supports` (`edge-058`)

## [[concept-is-a-vs-part-of|is-a vs has-a/part-of Boundary]]

Outbound:

- `refines` → [[concept-feature-type-vocabulary|Six-Type FeatureType Vocabulary]] (`edge-007`)

## [[dec-e2-screening-policy|E2 Screening and Futility Policy]]

Outbound:

- `derived_from` → [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] (`edge-054`)
- `gates` → [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] (`edge-053`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-052`)

Inbound:

- [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] → `depends_on` (`edge-092`)

## [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]]

Outbound:

- `gates` → [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] (`edge-049`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-048`)
- `refines` → [[concept-repo-derived-evidence|Repo-Derived Evidence]] (`edge-050`)
- `stated_in` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-051`)

Inbound:

- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `depends_on` (`edge-046`)

## [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]]

Outbound:

- `motivates` → [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] (`edge-056`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-055`)
- `stated_in` → [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]] (`edge-059`)
- `supports` → [[concept-symlink-classification-view|Relative Symlink Classification View]] (`edge-057`)
- `supports` → [[concept-typed-semantic-edge|Typed Semantic Edge]] (`edge-058`)

Inbound:

- [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] → `depends_on` (`edge-073`)
- [[mem-vault-operating-rule|Memory — Vault Operating Rule]] → `derived_from` (`edge-101`)
- [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]] → `motivates` (`edge-003`)
- [[concept-symlink-classification-view|Relative Symlink Classification View]] → `refines` (`edge-016`)

## [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]]

Outbound:

- `derived_from` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-022`)
- `motivates` → [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] (`edge-021`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-019`)
- `tests` → [[concept-feature-type-vocabulary|Six-Type FeatureType Vocabulary]] (`edge-020`)

Inbound:

- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `derived_from` (`edge-095`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `refines` (`edge-024`)

## [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]]

Outbound:

- `derived_from` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-028`)
- `motivates` → [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] (`edge-027`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-023`)
- `refines` → [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] (`edge-024`)
- `tests` → [[concept-complete-state-contract|Complete-State Repair Contract]] (`edge-026`)
- `tests` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-025`)

Inbound:

- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `derived_from` (`edge-096`)
- [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] → `motivates` (`edge-021`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `refines` (`edge-030`)

## [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]]

Outbound:

- `derived_from` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-034`)
- `motivates` → [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] (`edge-033`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-029`)
- `refines` → [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] (`edge-030`)
- `tests` → [[concept-complete-state-contract|Complete-State Repair Contract]] (`edge-032`)
- `tests` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-031`)

Inbound:

- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `derived_from` (`edge-097`)
- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `generalizes` (`edge-036`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `motivates` (`edge-027`)

## [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]]

Outbound:

- `derived_from` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-040`)
- `generalizes` → [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] (`edge-036`)
- `motivates` → [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] (`edge-039`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-035`)
- `supports` → [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] (`edge-038`)
- `tests` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-037`)

Inbound:

- [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] → `depends_on` (`edge-076`)
- [[dec-e2-screening-policy|E2 Screening and Futility Policy]] → `derived_from` (`edge-054`)
- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `derived_from` (`edge-098`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `motivates` (`edge-033`)

## [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]]

Outbound:

- `depends_on` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-043`)
- `depends_on` → [[concept-repo-derived-evidence|Repo-Derived Evidence]] (`edge-042`)
- `depends_on` → [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]] (`edge-046`)
- `derived_from` → [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] (`edge-047`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-041`)
- `tests` → [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] (`edge-045`)
- `tests` → [[concept-evidence-sufficiency|Evidence Sufficiency]] (`edge-044`)

Inbound:

- [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] → `depends_on` (`edge-080`)
- [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]] → `depends_on` (`edge-088`)
- [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]] → `gates` (`edge-049`)
- [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] → `motivates` (`edge-077`)
- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `motivates` (`edge-039`)

## [[vault-readme|Conversation Knowledge Vault]]

Outbound:

- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-105`)

## [[moc-ontology-reasoner-mcp|MOC — Ontology and Reasoner MCP]]

Outbound:

- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-103`)

## [[moc-vault-architecture|MOC — Vault Architecture]]

Outbound:

- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-104`)

## [[mem-experiment-progression|Memory — E2 Experiment Progression]]

Outbound:

- `depends_on` → [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] (`edge-099`)
- `derived_from` → [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] (`edge-095`)
- `derived_from` → [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] (`edge-096`)
- `derived_from` → [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] (`edge-097`)
- `derived_from` → [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] (`edge-098`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-094`)

## [[mem-vault-operating-rule|Memory — Vault Operating Rule]]

Outbound:

- `depends_on` → [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] (`edge-102`)
- `derived_from` → [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] (`edge-101`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-100`)

## [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]]

Outbound:

- `depends_on` → [[dec-e2-screening-policy|E2 Screening and Futility Policy]] (`edge-092`)
- `depends_on` → [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]] (`edge-091`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-090`)
- `requires` → [[concept-context-isolation|MCP Context Isolation]] (`edge-093`)

Inbound:

- [[dec-e2-screening-policy|E2 Screening and Futility Policy]] → `gates` (`edge-053`)
- [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] → `motivates` (`edge-082`)

## [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]]

Outbound:

- `depends_on` → [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] (`edge-088`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-087`)
- `requires` → [[proc-evidence-first-decision|Evidence-First Contract Decision]] (`edge-089`)

Inbound:

- [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] → `depends_on` (`edge-091`)
- [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] → `motivates` (`edge-081`)

## [[proc-evidence-first-decision|Evidence-First Contract Decision]]

Outbound:

- `gates` → [[concept-abstain-repair-contract|Claim–Abstain–Repair Contract]] (`edge-065`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-060`)
- `requires` → [[concept-complete-state-contract|Complete-State Repair Contract]] (`edge-064`)
- `requires` → [[concept-evidence-sufficiency|Evidence Sufficiency]] (`edge-062`)
- `requires` → [[concept-global-feature-type-invariant|Global Feature-Type Invariant]] (`edge-063`)
- `requires` → [[concept-repo-derived-evidence|Repo-Derived Evidence]] (`edge-061`)

Inbound:

- [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]] → `requires` (`edge-089`)

## [[proc-literature-first-research|Literature-First Open-Problem Workflow]]

Outbound:

- `gates` → [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]] (`edge-069`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-066`)
- `requires` → [[concept-literature-first|Literature-First Research]] (`edge-067`)
- `requires` → [[concept-problem-status-claim|Date-Bound Problem-Status Claim]] (`edge-068`)

Inbound:

- [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]] → `depends_on` (`edge-085`)

## [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]]

Outbound:

- `depends_on` → [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] (`edge-073`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-070`)
- `requires` → [[concept-symlink-classification-view|Relative Symlink Classification View]] (`edge-072`)
- `requires` → [[concept-typed-semantic-edge|Typed Semantic Edge]] (`edge-071`)

Inbound:

- [[mem-vault-operating-rule|Memory — Vault Operating Rule]] → `depends_on` (`edge-102`)
- [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] → `motivates` (`edge-056`)
- [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]] → `motivates` (`edge-004`)

## [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]]

Inbound:

- [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] → `part_of` (`edge-078`)
- [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] → `part_of` (`edge-074`)
- [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]] → `part_of` (`edge-083`)
- [[dec-e2-screening-policy|E2 Screening and Futility Policy]] → `part_of` (`edge-052`)
- [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]] → `part_of` (`edge-048`)
- [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] → `part_of` (`edge-055`)
- [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] → `part_of` (`edge-019`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `part_of` (`edge-023`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `part_of` (`edge-029`)
- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `part_of` (`edge-035`)
- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `part_of` (`edge-041`)
- [[loop-e2-4-execution|Execute E2.4 Repo-Grounded Trials]] → `part_of` (`edge-090`)
- [[loop-e2-4-scorer-fixtures|Implement E2.4 Fixtures and Deterministic Scorer]] → `part_of` (`edge-087`)
- [[mem-experiment-progression|Memory — E2 Experiment Progression]] → `part_of` (`edge-094`)
- [[mem-vault-operating-rule|Memory — Vault Operating Rule]] → `part_of` (`edge-100`)
- [[moc-ontology-reasoner-mcp|MOC — Ontology and Reasoner MCP]] → `part_of` (`edge-103`)
- [[moc-vault-architecture|MOC — Vault Architecture]] → `part_of` (`edge-104`)
- [[vault-readme|Conversation Knowledge Vault]] → `part_of` (`edge-105`)
- [[proc-evidence-first-decision|Evidence-First Contract Decision]] → `part_of` (`edge-060`)
- [[proc-literature-first-research|Literature-First Open-Problem Workflow]] → `part_of` (`edge-066`)
- [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] → `part_of` (`edge-070`)
- [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]] → `part_of` (`edge-001`)
- [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]] → `part_of` (`edge-002`)

## [[src-conversation-context-2026-07|Conversation Context Snapshot — 2026-07]]

Outbound:

- `motivates` → [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] (`edge-003`)
- `motivates` → [[proc-vault-ingestion|Vault Ingestion and Graph Enrichment]] (`edge-004`)
- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-001`)

Inbound:

- [[claim-open-status-date-bound|Open-Problem Status Must Be Date-Bound]] → `stated_in` (`edge-086`)
- [[dec-vault-storage-graph|Format Storage, Symlink Views, Typed Graph]] → `stated_in` (`edge-059`)

## [[src-repo-experiment-files-2026-07|Repo Experiment Source Set — E2.2.1 to E2.4]]

Outbound:

- `part_of` → [[project-ontology-reasoner-mcp|Ontology and Reasoner MCP Project]] (`edge-002`)
- `supports` → [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] (`edge-006`)
- `supports` → [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] (`edge-005`)

Inbound:

- [[exp-e2-2-1-vocabulary|E2.2.1 — Directed PC Vocabulary Fix]] → `derived_from` (`edge-022`)
- [[exp-e2-2-2-invariant|E2.2.2 — Directed PC Invariant Fix]] → `derived_from` (`edge-028`)
- [[exp-e2-2-3-ablation|E2.2.3 — Directed PC OFAT Ablation]] → `derived_from` (`edge-034`)
- [[exp-e2-3-generalization|E2.3 — Global Invariant Generalization]] → `derived_from` (`edge-040`)
- [[exp-e2-4-repo-contract|E2.4 — Repo-Grounded Evidence Contract]] → `derived_from` (`edge-047`)
- [[claim-e2-4-design-only|E2.4 Is Designed but Not Executed]] → `stated_in` (`edge-079`)
- [[claim-global-invariant-generalizes|Global Invariant Generalizes Across E2.3 Screens]] → `stated_in` (`edge-075`)
- [[dec-repo-evidence-source|E2.4 Repository-Only Evidence Source]] → `stated_in` (`edge-051`)
