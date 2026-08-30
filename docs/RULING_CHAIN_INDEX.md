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
| **Q34** | **판정 도착(D-34)** — D-33이 명한 (b*)의 선행 실사. **두 승인 source가 지시 표현을 반대로 인코딩한다**(PMB=∃ 결박자 / FOLIO=상수, 적격 풀 799건 중 116건). 경계는 제안하지 않고 gold가 기록하는 증거만 올렸다 | [[DESIGN_REQUEST_referential_existential_qualification]] | — |
| **Q34-B** | *보충, 새 문항 없음* — Q34 §7이 선언한 측정 한계 둘을 닫았다. **PMB gold 12,053 전수**: 지시 후보 노드 15,810개 중 닫힌 양화 어휘가 해결하는 것은 **2%**, **96%가 미결정**. **FOLIO 전수**: 상수 160회 중 **67% 미결정**이고 보통명사·물질명사·파싱 잔여도 상수다 → Q34 §1 자기 정정. (a)의 형태가 "FOLIO 규약 채택"에서 "새 경계를 세워 두 corpus를 사상"으로 바뀐다 | [[DESIGN_REQUEST_referential_boundary_corpus_scale]] | — |
| D-34 | **경계 정의는 수행하지 않는다 — `insufficient_evidence`.** (a) **기각**(corpus 규약을 semantic authority로 승격시키는 것) · synset은 식별 함수가 아니다 · **양방향 부등식**(`FOLIO constant ≠ referential` · `PMB binder ≠ quantificational force`) · `immediate_projection: forbidden` 추가. **다음은 분류기가 아니라 독립적 semantic qualification을 줄 source 결정**이다 | [[DESIGN_REQUEST_referential_existential_qualification]] + [[DESIGN_REQUEST_referential_boundary_corpus_scale|Q34-B]] | [[DESIGN_DECISION_referential_existential_qualification]] |
| Q35 | **판정 도착(D-35)** — D-34가 명한 source 결정의 첫 후보. **PMB는 지시 기능을 별도 role 주석으로 기록한다**(`Name` 3,841=24% · `ANA` 1,022=6%, 후보 15,810 전수) — 우리가 고른 목록이 아니라 **주석자의 판단**이다. 그런데 **우리 선별이 `ANA` 보유 문서를 배제**했다(in-N `ANA` 0건). 묻는 것: 이 층이 D-34 §9가 금지한 "corpus 규약"과 같은 지위인가 | [[DESIGN_REQUEST_annotation_layer_admissibility]] | [[DESIGN_DECISION_annotation_layer_admissibility|D-35]] |
| D-35 | **`Name`·`ANA`는 증거로 적격, semantic authority로 미확립.** `evidence`에서 `truth`로 가는 단계는 별개다 — "명명된 개체를 지시한다"와 "measurand에서 제거해야 한다"는 다른 명제다. **30% coverage의 비대칭**(있음→referential 가능, 없음→non-referential 불가) · **`ANA` 배제 되돌리기 금지**(관측 결과에 맞춘 계약 수정이 된다) · **주석 정확성 감사가 선행 조건** · `immediate_projection: forbidden` 유지 | [[DESIGN_REQUEST_annotation_layer_admissibility]] | [[DESIGN_DECISION_annotation_layer_admissibility]] |
| **Q36** | **구속 조건은 R1이 아니라 R2(독립 검증 가능성)다.** 고리를 그려 보니 네 시도(synset·표면 목록·FOLIO 규약·`Name`/`ANA`) 전부 못 끊고, 끊는 간선은 apparatus 밖 권위 하나다. 요건 R1~R4를 도출했고 **R2가 병목**이다 — 후보 넷 중 R2에 붙는 것은 둘뿐이고 둘 다 자기 검증 문제를 만든다. `sbn_spec.py` 원천 부재를 R2 공백의 구체 사례로 냈다 | [[DESIGN_REQUEST_independent_verifiability_constraint]] | [[DESIGN_DECISION_independent_verifiability_constraint|D-36]] |
| D-36 | **R2는 실제 구속 조건 — 그러나 R1~R4는 정리(theorem)가 아니라 후보 분해.** `ANA` 100% 구조 일관성은 R2의 **부분 증거일 뿐** 의미적 정확성으로 승격 불가 — **삼층 분리**(L1 encoding consistency 지지 / L2 annotation correctness 미검증 / L3 semantic qualification 미검증)를 명하고 "이 셋을 합치지 마라"가 핵심. **다른 corpus는 R2 후보가 될 수 있으나 독립성을 별도 입증**해야 한다(`automatically_independent: no`) · **사람 판정도 마찬가지** — R2는 "사람이 판단했다"가 아니라 "**검증 절차가 독립적인가**". `sbn_spec.py`는 material이나 충분조건 아님. **R2 미확립 ≠ 경계 원리적 불가** → `unestablished` / `insufficient_evidence`. **동결 PMB 15건 무효화 금지·수정 금지** — 재료의 무효화와 측정 계약의 미완성은 다르다. 문제가 "**authority를 어떻게 독립 인증하는가**"로 상승 | [[DESIGN_REQUEST_independent_verifiability_constraint|Q36]] | [[DESIGN_DECISION_independent_verifiability_constraint]] |
| **Q36** | **판정 도착(D-36)** — 고리를 그려 보니 **구속 조건이 R1이 아니라 R2(독립 검증 가능성)**다. 후보 넷이 R1은 다 채우고 R2는 둘만 채운다(다른 주석 corpus는 같은 순환을 물려받고, 판정 채널은 자기 검증 문제). R2 부분 기제로 **내부 구조 일관성**을 찾았다(`ANA` 1,036/1,036 노드 간선 대 `NEGATION` 546/546 행 첫 토큰, 위치 분리). 그리고 R2의 공백: 주석 규약 사양 `sbn_spec.py`가 **우리 손에 없고 전사만 있다** | [[DESIGN_REQUEST_independent_verifiability_constraint]] | — |

| **Q37** | **판정 도착(D-37)** — D-36 §2가 명시적으로 열어 둔 **R4 한 문항만**. `R4 = source 간 동일 기준`이 **읽기 A(같은 annotation mechanism)** 인지 **읽기 B(동일 measurand의 의미적으로 동등한 qualification)** 인지. 우리 쌍(PMB=SBN/box · FOLIO=일차 논리식)은 **어느 읽기로도 떨어지나 실패의 의미가 다르다** — A는 형식 차이(이 쌍만의 문제), B는 measurand 차이(D-34의 `FOLIO constant ≠ referential expression`이 이미 함의). **값은 이 쌍이 아니라 다음 source를 찾을 때의 수락 기준에 있다** — 읽기에 따라 찾을 대상이 완전히 달라진다. D-36 §6·§7이 만든 다른 질문(두 번째 corpus·사람 판정의 R2 자격)은 **싣지 않았다**(회신 후 별건) | [[DESIGN_REQUEST_r4_source_equivalence]] | — |

| D-37 | **R4는 기제 동일성이 아니라 `cross-source measurand comparability`다.** 읽기 A **기각**(unnecessarily_strong), 읽기 B 채택하되 **결과 동일성으로 정의 금지**(순환) — `Q_PMB ≡_M Q_FOLIO`, `≡_M`은 **독립적으로 정의된 M에 대해 보존되는** 동등성. **A/B 이분법도 동결 금지**(mechanism identity·qualification equivalence·translation-preserving equivalence를 comparability의 가능 조건들로). **우리 §4 연결 기각** — `¬(A⇒B)`에서 `¬B`가 나오지 않는다. D-34는 `constant ⇒ referential`을 배제했을 뿐 `FOLIO_cannot_qualify_referentiality`는 **미확립**이고, 그 도약은 D-34가 금지한 다리의 **역방향 반복**이다. **R4 ⊥ R2**(Wolfram 반례: QP=QF=True·R2P=True·R2F=False) — 어느 쪽도 상대를 함의하지 않는다. **경계 근거·V3 발동 근거는 추가되지 않는다**: `boundary_definition: still_unresolved` · dispatch/patch/projection 금지 유지 | [[DESIGN_REQUEST_r4_source_equivalence|Q37]] | [[DESIGN_DECISION_r4_source_equivalence]] |
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
- [[REFINE_VERIFY_STAGE_SURVEY_20260830]] — Refine↔Verify·Graph Diff 의 **검증 단계와 구현 단계** 내부 감사(근거 축 2분할: 사양 haiku / 코드 sonnet). 결론: **Verify 는 지어지고 MCP 까지 배선됐으나 Refine 이 없어 아직 루프가 아니다**(`repair` grep 0 · `git log -S` 0 · 테스트 자신이 "Refine 자리는 하드코딩된 stand-in"이라 적음). **Graph Diff 는 사양에도 코드에도 없다** — 다섯 철자 `git log -S` 전부 0건이고 가장 가까운 `graph_fingerprint` 는 **프로덕션 호출 0**(테스트 전용). 축 A 가 낸 W5 blocker 는 **이미 해소돼 있었다**(내 위임이 `DESIGN_IMPL` 을 두 축 어디에도 안 넣은 결함)


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
