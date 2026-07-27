# experiments/

프롬프트/가이드 변경을 뒷받침하는 실험 기록. 각 실험은 날짜 폴더에
원시 데이터(trials.json) + 결정적 채점 스크립트(evaluate.py) + 보고서(README.md)를
함께 두어 재현 가능하게 한다.

| 실험 | 질문 | 결론 |
|------|------|------|
| [2026-07-06_tool_description_ab](2026-07-06_tool_description_ab/) | run_pipeline tool description에 is-a edge 계약을 명시하면 클라이언트 LLM이 올바른 DAG 입력을 만드는가? | 구 description 0/5 → 신 description 4/5 완전 계층 형성. 계약 명시 채택 + linter 교차 검사 추가 |
| [2026-07-06_multidomain_generalization](2026-07-06_multidomain_generalization/) | EDGE CONTRACT + 도메인 중립 linter가 어텐션 밖 임의 도메인에서도 작동하는가? | 생물·기하·법·요리 4도메인 12/12 완전 계층 형성 (기하는 다중상속 lattice까지), cross-lint 오탐 0 |
| [2026-07-18_obligation_certificate_ab](2026-07-18_obligation_certificate_ab/) | obligation certificate가 클라이언트 수리 행동을 바꾸는가? | 천장 효과 — 양 arm 5/5 repair (음성). 기존 anti_patterns/lint가 이미 포화. certificate의 값은 행동이 아니라 assurance 감사 + 미래 semantic obligation의 certificate-only 신호에 있음. reasoner 지연 median 498ms 관측 |
| [2026-07-18_isa_certificate_only_ab](2026-07-18_isa_certificate_only_ab/) | relation.is_a certificate-only 신호가 클라이언트 수리 행동을 바꾸는가? (E2 — 3-arm 신호분해 + truth oracle + nonce fixture) | **Reconstructed record, empirical 미검증.** scorer는 기록된 13개 응답의 집계를 재현하지만 원 실행 provenance가 없다. evidence 임시성 단서로 baseline도 침묵하지 않는 설계 confound를 확인했으며, E2.1에서 clean baseline으로 재실행한다. |
| [2026-07-19_isa_certificate_only_ab_clean_baseline](2026-07-19_isa_certificate_only_ab_clean_baseline/) | provenance가 있는 clean baseline에서 warning/certificate가 확정 보고를 억제하는가? (E2.1) | **Preregistered / not run.** 동일 반복 prompt를 고정 순서로 교차 배치한 30개 cold-context trial. prompt/manifest hash·모델·시각·context·원문 응답 필수이며, 형식 실패도 제외하지 않고 `INVALID`로 채점한다. |
| [2026-07-23_isa_certificate_structure_bvsc](2026-07-23_isa_certificate_structure_bvsc/) | 같은 relation.is_a 정보를 구조화 certificate(B)로 주는 것과 평문 warning(C)으로 주는 것에 차이가 있는가? (E2.2) | Δ_BC=+0.32, **NO_GO**. directed positive control(`dir1_directed`)이 0/10으로 실패 — 이 실패가 E2.2.1의 출발점이 됐다 |
| [2026-07-24_e2.2.1_directed_pc_vocabulary_fix](2026-07-24_e2.2.1_directed_pc_vocabulary_fix/) | directed-PC 실패가 프롬프트/스키마에 structural_composition 어휘가 노출 안 된 탓인가? (E2.2.1) | rate=0.15, **NO_GO**. 어휘 노출만으로는 부족 — 원인 재분석이 필요했다 |
| [2026-07-24_e2.2.2_directed_pc_invariant_fix](2026-07-24_e2.2.2_directed_pc_invariant_fix/) | 진짜 원인은 어휘가 아니라 미명시 구조 계약(전역 feature-type invariant + complete-state) 아닌가? (E2.2.2) | rate=1.00, **GO**. 20/20. E2.2.1의 "어휘" 진단이 틀렸음을 확인 |
| [2026-07-25_e2.2.3_directed_pc_ablation](2026-07-25_e2.2.3_directed_pc_ablation/) | E2.2.2의 복합 수정 중 어느 요소가 실제로 효과를 냈는가? (OFAT ablation) | A_ONLY=20/20, B_ONLY=1/20, C_ONLY=0/20 — **A(전역 invariant 규칙) 단독으로 충분** |
| [2026-07-25_e2.3_global_invariant_generalization](2026-07-25_e2.3_global_invariant_generalization/) | A_ONLY의 효과가 fixture 특유의 문장 효과인가, 일반화되는 추론 계약인가? | CONTROL 0/2, A_ONLY 10/10, PARAPHRASE 9/10, TOPOLOGY 9/10, DECOY 10/10 — 전부 screened PASS |
| [2026-07-25_e2.4_repo_grounded_contract_transfer](2026-07-25_e2.4_repo_grounded_contract_transfer/) | 구조화 evidence 계약(CONTRACT_REPO)이 **이 저장소 자체의 실제 코드/문서** evidence 위에서 claim/abstain/repair 경계를 지키는가? | **진행 중 — 본 3-arm 실험 미실행.** fixture 4종 준비 완료(consistent 7/7, repairable 5/5, insufficient 5/5, conflicting 1/1 ⚠️재검증 필요). 상태는 `docs/HANDOFF.md` §4 참조 |

## 채점 원칙

- **에이전트 자기보고 금지** — 각 trial의 concepts JSON을 실제
  `ConceptPipeline`/`cg_input_linter`에 통과시켜 edge/isolated/경고를 계산한다.
- empirical trial은 원문 응답과 실행 provenance를 함께 수정 없이 커밋한다
  (`trials.json`). 복원 기록은 `record_class=reconstructed_record`로 명시한다.
- 채점 스크립트는 stdlib + repo 모듈만 사용해 어디서든 재현 가능해야 한다.
