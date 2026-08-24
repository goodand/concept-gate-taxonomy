# E2E-v1 판정·조사 사슬 색인 (graph 진입점)

이 노트의 용도는 **graph traversal 진입점**이다. `rg`/grep으로는 판정 문서를
찾을 수 없는 경우가 실측으로 확인됐다(결정 문서의 파일명이 질문의 어휘를
하나도 포함하지 않을 수 있다 — 저장소 CLAUDE.md "무언가를 찾을 때" 절).
그래서 **모든 판정·요청·조사 회신을 여기서 1홉으로 도달 가능하게** 둔다.

zero-context agent를 위한 읽는 순서:

1. 이 색인에서 **가장 큰 번호의 판정**을 먼저 읽는다 — 사슬은 뒤로 갈수록
   앞의 결정을 좁히거나 뒤집는다.
2. 그 판정의 헤더에 있는 `이전`/`다음` 링크로 사슬을 거슬러 올라간다.
3. 상태·정지 조건은 이 색인이 아니라 **worktree 루트 handoff**가 정본이다:
   [[concept-gate-h1-wt/HANDOFF|HANDOFF (concept-gate-h1-wt 루트)]]
   — `HANDOFF`라는 이름의 파일이 이 vault에 **46개** 있으므로 반드시 경로로
   지정한다. bare name 링크는 조용히 다른 worktree를 가리킨다.
4. 패턴·이슈 원장은
   [[concept-gate-h1-wt/docs/H1A_PROBLEM_ANALYSIS|H1A_PROBLEM_ANALYSIS (이 worktree)]]
   의 **마지막 절**이 항상 최신이다 — 이 이름도 vault에 **9개** 있다.

## 판정 사슬 (외부 설계 담당 — 저장소 접근 없는 판정자)

각 행: 판정 ID · 무엇을 정했나 · 요청서 ↔ 판정문.
판정문은 전부 **verbatim + `VERBATIM_SHA256`** 수록이고, 말미에 우리 수신
검증 기록이 붙는다.

| ID | 무엇을 정했나 | 요청 | 판정 |
|---|---|---|---|
| D-19 | 실험 구조·schema 강제 dispatch | [[DESIGN_REQUEST_e2e_v1_experiment_design]] | [[DESIGN_DECISION_e2e_v1_experiment_design]] |
| D-20 | fixture commitment·라이선스 | [[DESIGN_REQUEST_o1_fixture_licensing]] | [[DESIGN_DECISION_o1_fixture_licensing]] |
| D-21 | oracle 단위·coverage (Wikisem 배제) | [[DESIGN_REQUEST_o1_oracle_unit_and_coverage]] | [[DESIGN_DECISION_o1_oracle_unit_and_coverage]] |
| D-22 | PMB 부분 자격 + stratum floor | [[DESIGN_REQUEST_pmb_source_qualification]] | [[DESIGN_DECISION_pmb_source_qualification]] |
| D-23 | FOLIO 제2 source + FOL codec | [[DESIGN_REQUEST_folio_second_source]] | [[DESIGN_DECISION_folio_second_source]] |
| D-24 | FOLIO 술어 라벨 규약 · pre-execution amendment | [[DESIGN_REQUEST_folio_predicate_labels]] | [[DESIGN_DECISION_folio_predicate_labels]] |
| D-25 | oracle 입도 · projection 명령 · 실패 예정 계약 금지 | [[DESIGN_REQUEST_oracle_granularity]] | [[DESIGN_DECISION_oracle_granularity]] |
| D-26 | 방언 표현력 (`implies` 추가) | [[DESIGN_REQUEST_subject_dialect_expressiveness]] | [[DESIGN_DECISION_subject_dialect_expressiveness]] |
| D-27 | 동치 관용구(curry만) · 대명사 ∃ · 게이트 2층 | [[DESIGN_REQUEST_equivalence_idioms]] | [[DESIGN_DECISION_equivalence_idioms]] |
| D-28 | 투영 신호 손실 · event-incidence · Gate C 3층 | [[DESIGN_REQUEST_pmb_projection_signal_loss]] | [[DESIGN_DECISION_pmb_projection_signal_loss]] |
| D-29 | 기수·비례 방언(`count`·`prop`) · MRS 조건부 후보 | [[DESIGN_REQUEST_cardinal_dialect_and_mrs_source]] | [[DESIGN_DECISION_cardinal_dialect_and_mrs_source]] |
| D-30 | MRS fail-closed 구체화(admissible BODY target)·변수별 card·기수 관계 사상표·권리 gate 분리 | [[DESIGN_REQUEST_mrs_fail_closed_and_rights]] | [[DESIGN_DECISION_mrs_fail_closed_and_rights]] |

| D-31 | 한정사는 BODY 경쟁자 **유지**(제외는 ambiguity→uniqueness 변환) · E13~E15 승인(사유 각각 상이, E15는 최상위 hard gate) · 중복은 Case A collapse / Case B ORACLE_COLLISION · 제한식 비-머리 내용은 **measurand 오염** | [[DESIGN_REQUEST_definite_scope_and_material_rules]] | [[DESIGN_DECISION_definite_scope_and_material_rules]] |

| **Q32** | **판정 대기** — 제한식 투영: 비-scope 내용의 지위(D-31 Q31.4가 명한 후속) | [[DESIGN_REQUEST_restriction_projection]] | (없음) |

별도 계열(이 실험 전 단계): [[DESIGN_DECISION_refine_verify_v0_review]]

## 조사 왕복 (조사용 agent — 다른 workspace, zero context)

조사 채널은 **사실 확인만** 한다. 적격성 판정을 청하지 않는다.
회신은 verbatim + sha256으로 수록하고, 우리 검증은 같은 문서의 별도 절에 둔다
— 조사의 주장과 우리 실측을 섞어 읽으면 안 된다.

| 회차 | 주제 | 요청 | 회신 |
|---|---|---|---|
| 1 | PMB O1 적격성 | [[RESEARCH_REQUEST_pmb_o1_eligibility]] | [[RESEARCH_RESULT_pmb_o1_eligibility]] |
| 2 | O1 corpus 접근 | [[RESEARCH_REQUEST_o1_corpus_access]] | [[RESEARCH_RESULT_o1_corpus_access]] |
| 3 | 제2 source·다중 양화 | [[RESEARCH_REQUEST_second_source_multiquant]] | [[RESEARCH_RESULT_second_source_multiquant]] |
| 4 | 기수 gold source | [[RESEARCH_REQUEST_cardinal_quantifier_source]] | [[RESEARCH_RESULT_cardinal_quantifier_source]] |
| 5 | 비례 source + BLOCKED 해소 | [[RESEARCH_REQUEST_cardinal_proportional_round2]] | [[RESEARCH_RESULT_cardinal_proportional_round2]] |
| 6 | ERG/MRS·Redwoods locator·권리·scope | [[RESEARCH_REQUEST_mrs_redwoods_round3]] | [[RESEARCH_RESULT_mrs_redwoods_round3]] |

## 그 밖의 정본

- 적대 검증: [[ADVERSARIAL_VALIDATION_20260823]]
- handoff 자체의 복원 가능성 실측(zero-context 평가기): [[HANDOFF_EVALUATION_20260823]]
- 다이어그램 규약(추상화 우선순위·semantic zoom): [[concept-gate-h1-wt/docs/diagrams/README|diagrams/README]]

## 이 색인을 고칠 때

새 판정·조사가 오면 **여기에 행을 추가하고**, 그 문서 헤더의 `이전`/`다음`
링크를 잇는다. 두 곳을 같이 고치는 이유: 색인만 있으면 색인이 사라질 때
사슬이 끊기고, 인접 링크만 있으면 사슬 중간부터 읽는 사람이 전체를 못 본다.
