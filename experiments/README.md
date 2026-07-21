# experiments/

프롬프트/가이드 변경을 뒷받침하는 실험 기록. 각 실험은 날짜 폴더에
원시 데이터(trials.json) + 결정적 채점 스크립트(evaluate.py) + 보고서(README.md)를
함께 두어 재현 가능하게 한다.

| 실험 | 질문 | 결론 |
|------|------|------|
| [2026-07-06_tool_description_ab](2026-07-06_tool_description_ab/) | run_pipeline tool description에 is-a edge 계약을 명시하면 클라이언트 LLM이 올바른 DAG 입력을 만드는가? | 구 description 0/5 → 신 description 4/5 완전 계층 형성. 계약 명시 채택 + linter 교차 검사 추가 |
| [2026-07-06_multidomain_generalization](2026-07-06_multidomain_generalization/) | EDGE CONTRACT + 도메인 중립 linter가 어텐션 밖 임의 도메인에서도 작동하는가? | 생물·기하·법·요리 4도메인 12/12 완전 계층 형성 (기하는 다중상속 lattice까지), cross-lint 오탐 0 |
| [2026-07-18_obligation_certificate_ab](2026-07-18_obligation_certificate_ab/) | obligation certificate가 클라이언트 수리 행동을 바꾸는가? | 천장 효과 — 양 arm 5/5 repair (음성). 기존 anti_patterns/lint가 이미 포화. certificate의 값은 행동이 아니라 assurance 감사 + 미래 semantic obligation의 certificate-only 신호에 있음. reasoner 지연 median 498ms 관측 |
| [2026-07-18_isa_certificate_only_ab](2026-07-18_isa_certificate_only_ab/) | relation.is_a certificate-only 신호가 클라이언트 수리 행동을 바꾸는가? (E2 — 3-arm 신호분해 + truth oracle + nonce fixture) | 천장 효과 재현 — safe_effective 100% 전 cell, arm 간 격차 0 (실증 불가). 단 manipulation check로 "신호는 읽혔으나 행동 안 바꿈" 확정. 근본 원인: evidence 문장 임시성 단서 잔존(결함 6) → baseline 미침묵. laundering 0/13, 양성·음성 대조 성립. |

## 채점 원칙

- **에이전트 자기보고 금지** — 각 trial의 concepts JSON을 실제
  `ConceptPipeline`/`cg_input_linter`에 통과시켜 edge/isolated/경고를 계산한다.
- 원시 데이터는 수정 없이 커밋한다 (trials.json).
- 채점 스크립트는 stdlib + repo 모듈만 사용해 어디서든 재현 가능해야 한다.
