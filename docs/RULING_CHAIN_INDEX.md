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

| D-32 | 제한식 비-scope 내용을 opaque 붕괴(empty/nonempty·incidence 보존) · 닫힌 profile `O1_SCOPE_PROJECTION_V2` · 20건 전량 재투영 · amendment+profile 둘 다 | [[DESIGN_REQUEST_restriction_projection]] | [[DESIGN_DECISION_restriction_projection]] |

| D-32-C | `Q_RSTR_BODY`를 위치로 정의 **승인, 단 `forall` 한정**(existential은 `P∧Q`≢`True∧(P→Q)`) · provenance는 scoring signature 금지 | [[DESIGN_REQUEST_q_rstr_body_position]] | [[DESIGN_DECISION_q_rstr_body_position]] |
| D-33 | 선택지 **네 개 전부 그대로는 기각** — (a) 인코딩 관례가 scope measurand 오염 · (b) 방향만 인정·**즉시 구현 금지**(referential ∃ 경계 미정의) · (c)(d) 기각. 권고는 선택지에 없던 **(b\*)**: `REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1`을 먼저 정의한 뒤에만 `O1_SCOPE_PROJECTION_V3`. `dispatch: blocked` · `operational_patch: forbidden` | [[DESIGN_REQUEST_referential_participant_quantification]] | [[DESIGN_DECISION_referential_participant_quantification]] |
| D-33-V | **D-33 재검증 — 뒤집지 않고 주장 유형을 갈랐다.** 논리 확인(∃ 비환원·signature의 **non-injective** 인과 미식별) / corpus 실사(synset alone 불충분) / **의미론 미확정**(`him` 대 `someone`)을 분리하고, `B*`의 강도를 "encoding과 scope가 식별 불가"로 좁혔다 | — | [[DESIGN_DECISION_d33_claim_status]] |
| **Q34** | *판정 대기* — D-33이 명한 (b*)의 선행 실사. **두 승인 source가 지시 표현을 반대로 인코딩한다**(PMB=∃ 결박자 / FOLIO=상수, 적격 풀 799건 중 116건). 경계는 제안하지 않고 gold가 기록하는 증거만 올렸다 | [[DESIGN_REQUEST_referential_existential_qualification]] | — |
| **Q34-B** | *보충, 새 문항 없음* — Q34 §7이 선언한 측정 한계 둘을 닫았다. **PMB gold 12,053 전수**: 지시 후보 노드 15,810개 중 닫힌 양화 어휘가 해결하는 것은 **2%**, **96%가 미결정**. **FOLIO 전수**: 상수 160회 중 **67% 미결정**이고 보통명사·물질명사·파싱 잔여도 상수다 → Q34 §1 자기 정정. (a)의 형태가 "FOLIO 규약 채택"에서 "새 경계를 세워 두 corpus를 사상"으로 바뀐다 | [[DESIGN_REQUEST_referential_boundary_corpus_scale]] | — |
| D-34 | **경계 정의는 수행하지 않는다 — `insufficient_evidence`.** (a) **기각**(corpus 규약을 semantic authority로 승격시키는 것) · synset은 식별 함수가 아니다 · **양방향 부등식**(`FOLIO constant ≠ referential` · `PMB binder ≠ quantificational force`) · `immediate_projection: forbidden` 추가. **다음은 분류기가 아니라 독립적 semantic qualification을 줄 source 결정**이다 | [[DESIGN_REQUEST_referential_existential_qualification]] + [[DESIGN_REQUEST_referential_boundary_corpus_scale|Q34-B]] | [[DESIGN_DECISION_referential_existential_qualification]] |

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

## 파일명 규약 — 접두어를 새로 만들지 마라

이 채널의 문서는 **네 접두어뿐**이다.

| 접두어 | 무엇 |
|---|---|
| `DESIGN_REQUEST_` | 외부 설계 담당에게 보내는 상신서 |
| `DESIGN_DECISION_` | 그 판정문(verbatim + sha256 + 우리 수신 검증) |
| `RESEARCH_REQUEST_` | 조사용 agent에게 보내는 요청서 |
| `RESEARCH_RESULT_` | 그 회신(verbatim + sha256 + 우리 검증) |

**규모가 작아도 접두어를 바꾸지 않는다.** 2026-08-24 실측: 문항 1개짜리
재해석 확인을 `CONFIRMATION_REQUEST_`로 만들었더니 사용자가 **다른 파일인지
헷갈렸다.** 같은 채널·같은 형식의 문서인데 이름이 규약 밖이면 사람도
zero-context agent도 그것이 무엇이고 사슬의 어디인지 알 수 없다. 작은 상신은
접두어를 유지하고 **번호로 구별한다**(예: Q32의 후속 = `Q32-C`).

이것은 §"md 문서를 만들 때"(저장소 CLAUDE.md)의 graph 규약과 같은 목적이다 —
**파일이 있는 것과 알아볼 수 있는 것은 다르다.**

## 이 색인을 고칠 때

새 판정·조사가 오면 **여기에 행을 추가하고**, 그 문서 헤더의 `이전`/`다음`
링크를 잇는다. 두 곳을 같이 고치는 이유: 색인만 있으면 색인이 사라질 때
사슬이 끊기고, 인접 링크만 있으면 사슬 중간부터 읽는 사람이 전체를 못 본다.
