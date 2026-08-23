# Stage 2 (E2E-v1-C) 사전등록 V4 — **REFROZEN 2026-08-23 (Amendment 2)**

이 문서 = V2 전문(V1+A1, 무수정) + AMENDMENT 2. V1·V2 파일도 바이트
그대로 보존된다(삼중 보존 — 게이트가 V1·V2 해시를 감시).

---

# Stage 2 (E2E-v1-C) 사전등록 V2 — **REFROZEN 2026-08-23 (Amendment 1)**

이 문서 = PART I(V1 전문, 무수정 보존) + AMENDMENT 1. V1 파일
`PREREGISTRATION_STAGE2.md`도 바이트 그대로 남아 있다(이중 보존).

---

# PART I — 원 사전등록 (V1, FROZEN 2026-08-23, 이하 무수정)

# Stage 2 (E2E-v1-C) 사전등록 — **FROZEN 2026-08-23**

status: **FROZEN** — 이 커밋이 동결이다. fixture manifest 20건
(`stage2_fixture_manifest.json`) + constructor profile(O1_V1) hash + 프롬프트
template이 이 커밋에서 함께 확정됐다. 이후 아래 항목의 변경은 D-19 §12의
외부 판정 사안이다. 동결 선별의 정본 규칙은 `freeze_stage2.py`(seed 포함,
손 선택 지점 0), 동결 직전 검증은 23/23(commitment 완전·resolver 왕복·
재복호 해시 일치·2경로 소속).

등록 항목은 D-E2E-v1-19 §11의 목록 그대로이며, 그 목록에 없는 governance를
추가하지 않는다(§11: "estimand에 비례").

## A. source 무관 — 지금 확정 (근거는 이 폴더의 커밋 이력)

| §11 항목 | 값 | 근거 |
|---|---|---|
| oracle ID | O1 (Quantifier Scope) | oracle manifest·D-21 |
| output schema | `cg_ir_schema.formula_json_schema(V0_O1_CONSTRUCTORS)` — plan의 `provenance.output_schema`에 embed + sha256 | 준비물 ② |
| model-facing prompt | `stage2_prompt_template.md`의 fenced block, `{sentence}` 단일 슬롯 — plan에 template sha256 pin | 준비물 ③, 프로브 A/B 실측 |
| subject | `o1-compiler` (no tools), definition_sha256 pin | 준비물 ①, 프로브 2종 |
| PASS/FAIL/UNSCORABLE/ERROR mapping | `cg_evaluate` 4치 경계 (Stage 1 자격 8/8) | Stage 1 |
| evaluation rules | canonical structural match (`canonicalize_v0` — α-rename만), 차원 귀속 5종 | cg_ir·cg_evaluate |
| direct/certified metrics | UCR(primary)·DirectMatch·Coverage·Yield(전부 분모 N)·P(PASS\|Cert)=secondary·2×2(B=false positive) | `_stage2_score.py` (준비물 ④) |
| N / acceptance | **N=20, PASS≥16 ∧ multi-quantifier stratum 4/5 ∧ 최종 ERROR=0 ∧ 예상 밖 UNSCORABLE=0** — D-22가 stratum floor·구성 제약(PMB ≤15 + 독립 제2 source ≥5=다중 양화 전담) 추가 | D-19·D-21·**D-22 §2-3·§16** |
| retry policy | 사전등록된 mechanical retry 1회(생성 전 인프라 실패만), semantic retry 없음 | D-19 §재실행 |
| SBN adapter 자격 | **9/9 PASS**(D-22 9항목), 코드 결박 — 변경 시 자동 실효 | `2026-08-23_sbn_adapter_qualification` |
| WSD 중립화 | `O1_PMB_LEMMA_NO_SENSE_V1`(`_stage2_eval_profile.py`) — 커널 밖, 리허설 실패 형태를 계약으로 재현·소멸 | 준비물, D-22 Q22.3 |
| 제2 source | **FOLIO v0.0 승인**(D-23 Q23.1) — 다중 양화 ≥5 전담, 단순 양화 control 2~4건은 N 밖 | D-23 |
| canonical comparison | 비교 전 양측 desugar: `FORALL(x,R,B)→FORALL(x,True,R→B)`, `EXISTS(x,R,B)→EXISTS(x,True,R∧B)` — 정의적, 양화 순서 불변, subject 방언 불변(§10) | D-23 §12 `canonical_comparison`, `_stage2_canonical_core.py` |
| oracle leakage prohibition | 구조적: dispatch-plan 빌더가 LF를 resolve하지 않음 + 누출 테스트 | 준비물 ③ |
| no post-result fixture replacement / N increase | 서약 — 위반은 §12 외부 판정 사안 | D-19 §12 |
| UNSCORABLE 회계 | freeze 전 unsupported=INELIGIBLE(표본 밖) / freeze 후=UNEXPECTED_UNSCORABLE(수용 FAIL) | D-21 §14 |
| 결과 보고 표기 | `O1-v1 source = PMB-5.1.0-gold(15) + FOLIO-v0.0(5)` 명시, wikisem 결과와 비교 서술 금지 | D-21 §11 |

## B. source 종속 — **[TBD], 동결 시 확정**

| §11 항목 | 슬롯 |
|---|---|
| source locator | **확정**: PMB 5.1.0 gold 15건(전부 Tatoeba/CC-BY) + FOLIO v0.0 5건(전부 WikiLogic — subset 기록됨). locator·해시는 manifest |
| fixture IDs + hashes | **`stage2_fixture_manifest.json`** — 20건 + adapter control 3건(N 밖), commitment 필드만, 원문 0바이트 |
| expected canonical IR | manifest의 expected_ir_sha256 — SBN adapter(자격 9/9 v1)·FOL adapter(자격 9/9 v2) 산출, 동결 시 재복호 일치 확인 |
| canonicalization profile | **O1_V1 = (forall, exists, and, pred, not)**, hash `dcda0f63e19c980d…`(전체는 manifest) — descriptor에 IR constructor·source encoding(PMB_SBN_5_1/FOLIO_FOL_V0)·비교층(desugar+lemma profile) 분리 기록. `not` 포함 사유: 양화-부정 stratum이 subject의 부정 표현을 요구(동결 직전 점검에서 발견·template 동시 보강) |
| model/version/config | **haiku (claude-haiku-4-5-20251001)** — 사용자 확정(2026-08-23). 근거: 이 도구의 최다 사용 모델이자 agentic 성능의 바닥선 — haiku에서 작동하면 상위 모델로 일반화된다는 floor-model 가정. 프로브·리허설과도 동일 모델 |
| certification 축 | **dormant-by-design**(W3 선례): 본 코호트 전원 certified=False — 2×2의 C/D열만 실측, A/B 배선은 리허설로 검증된 상태로 기록. secondary 지표는 Coverage=0으로 보고(primary 무영향). 활성화는 의무 집합 정의와 함께 향후 사안 |
| qualification vs capability 분리 | **확정**: capability 20 = PMB{비례1·양화부정4·보편4·기수3·존재3} + FOLIO multi 5; adapter control 3건은 N 밖(D-22 §15) |

## C. 동결 절차 (예고)

1. 적격성 스캔: Path A(adapter 능력) + Path B(독립 constructor 스캐너) —
   불일치 시 FREEZE_BLOCKED (D-21 §15).
2. 선별 항목별 `.met` source/license 확인을 **같은 단계에** 묶는다
   (PMB 조사 결과 §운영 세션으로 넘길 핵심 사실).
3. manifest + profile hash + 이 문서의 TBD 해소를 **한 커밋**으로 동결,
   결과는 별도 커밋(방법론 §1).


---

# AMENDMENT 1 — D-E2E-v1-24 (2026-08-23, pre-execution)

status: **REFROZEN as V2** — 위 PART(원 사전등록 전문)는 V1 그대로 보존된
역사적 기록이다(`SUPERSEDED_PRE_EXECUTION`, 판정 §8). 이 절이 V2에서
바뀐 것 전부를 기록한다. **코호트 결과는 단 1건도 관측되지 않은 상태의
수정이다** (smoke는 코호트 밖 발명 재료 4건만 dispatch했다).

## A1.1 결함 (무엇이, 어떻게 발견됐나)

- **B1**: FOLIO oracle 술어가 대문자/CamelCase(`Lab`, `CanCatch`,
  `SpectatorsBetOn`)로 비교층에 남는데(V1 평가 profile은 synset 패턴만
  정규화) template은 subject에게 소문자를 강제 — **라벨 규약 차이만으로
  FOLIO 8건 전건 fail이 사전 결정**(control 0/3, multi floor 0/5).
- 발견: 코호트 실행 전 smoke test(`SMOKE_TEST_20260823.md`)의 live
  산출 원인 분해. 상신 `DESIGN_REQUEST_folio_predicate_labels.md`
  (sha256 54aa1a7d…) → 판정 `docs/DESIGN_DECISION_folio_predicate_labels.md`
  (D-E2E-v1-24, verbatim sha256 d563f12c…, 수신 검증 4/4 CONFIRMED).

## A1.2 before → after (정확한 diff)

| 표면 | V1 (보존) | V2 |
|---|---|---|
| 평가 profile | `O1_PMB_LEMMA_NO_SENSE_V1` 단일 | source별 dispatch: PMB→기존, FOLIO→**`FOLIO_LABEL_LOWERCASE_V1`**(소문자화만; 분절·동의어·lemma·병합 금지, 예약 토큰 `True` 불변). 미지 접두어는 거부(fail-closed). `_stage2_eval_profile.py`·`_stage2_run.py` |
| profile descriptor | `predicate_labels: "O1_PMB_LEMMA_NO_SENSE_V1"` | `predicate_labels: {"PMB": …, "FOLIO": "FOLIO_LABEL_LOWERCASE_V1"}` |
| profile hash | `dcda0f63e19c980d…` | **`c9d22d5c482dab0a…`** (전체는 manifest_v2) |
| FOLIO 적격성 | D-23 6조건 | + **`predicate_label_reachability`**: codec 통과 라벨 전건이 동결 기계 규칙(`scan_folio_eligibility_v2.py`, sha256 1ffb1d6d13602449…)으로 문장 파생 가능, Path A/B 라벨 집합 합의 필수 |
| FOLIO 선별 | multi 17→5, control 963→3 | 도달성 필터 후 **multi 17→5(전원 — 자유도 0), control 963→422→3**; 동일 SEED·동일 층 술어·동일 순서 규칙(`freeze_stage2_v2.py`가 V1에서 import) |
| FOLIO in-N | 142p1·695p1·**404p3·721p1·274p1** | 142p1·695p1·**404p0·376p4·598p4** |
| controls | 175p1·**500p4**·1377p0 | 175p1·1377p0·**1420p2** |
| PMB 15 | — | **선별·commitment(text/lf/expected_ir) 불변** — `canonicalization_profile_hash` 필드만 V2 값. `test_stage2_freeze_v2.py`가 V1 바이트 해시(13b47362…)와 함께 기계 보증 |
| manifest | `stage2_fixture_manifest.json` (byte-frozen) | `stage2_fixture_manifest_v2.json` |

## A1.3 known source-specific challenge (판정 Q24.4·§15 문안)

> FOLIO source contains prefix-quantified implication structures whose gold
> topology may differ from alternative natural-language readings. Under
> FOLIO_FOL_V0, the published gold topology is preserved exactly;
> comparison-layer quantifier/implication rewrites are prohibited.

(비동치는 유한 모델 전수로 실측: 2원소 domain 256 해석 중 반례 104 —
판정 §13, 수신 검증 V1 재계산 일치. 특정 동결 item의 결과를 미리
분류하지 않는다.)

## A1.4 재검증 (판정 §11 요구 — V2 동결 조건)

codec 자격 3종+α(계약 `test_stage2_eval_profile.py` 20건: positive/
negative Zorble≠Creature/구조 보존/예약 토큰/dispatch fail-closed) ·
FOLIO adapter 자격 5/5 재실행 · V1↔V2 diff 게이트 8건 · smoke S1(23/23
왕복+drift 0)–S2(dispatch 계약 13/13)–S3(live 4건 관통) V2 재실행 ·
Path A/B 합의(도달성 스캔에 내장) · `run_gates.py` 전체. 결과 수치는
운영 로그(`SMOKE_TEST_20260823.md` 추기)와 게이트 출력이 정본.

## A1.5 절차 정본화

이 amendment는 판정 §9 `PRE_EXECUTION_FREEZE_AMENDMENT_V1` 절차의 첫
적용례다. 전제 충족: cohort_execution_started=false,
confirmatory_outcomes_observed=false.


---

# AMENDMENT 2 — D-E2E-v1-25 + D-E2E-v1-26 (2026-08-23, pre-execution)

status: **REFROZEN as V4** — 위 전문(V1 + AMENDMENT 1)은 무수정 보존.
V2는 SUPERSEDED_PRE_EXECUTION, **V3는 ABORTED_PRE_FREEZE**(artifact 미생성 —
Measurement Satisfiability Gate가 multi 풀 2/17을 동결 전에 적발, Q26 상신).
**코호트 결과는 여전히 0건 관측 상태의 수정이다** (adapter control V2 실행
2/3은 측정계약 결함의 게이트 신호로 판정됨 — D-25 Q25.3, 역사 기록 보존).

## A2.1 결함과 판정 사슬

- **F3** (D-25): PMB oracle이 사건 의미론 granularity로 인코딩 — full-IR
  DirectMatch 아래서 15/15 구조적 unpassable(최대 PASS 5 < 16, 수학적 불가).
- **F-dialect** (D-26): FOLIO 다중 양화 gold의 ∃-scope 함의를 subject 방언
  (함의=forall 제한식만)이 표현 불가 — multi 풀 2/17.
- 판정: D-25(projection·O1ScopeMatch·라벨 진단화·SAT gate)·D-26(implies
  방언·도달성 적격 강등·selector 재실행). 전부 verbatim+sha256 수록
  (`docs/DESIGN_DECISION_oracle_granularity.md`,
  `docs/DESIGN_DECISION_subject_dialect_expressiveness.md`).

## A2.2 V4에서 바뀐 것 (before → after)

| 표면 | V2 | V4 |
|---|---|---|
| subject 방언 | 5종 (forall/exists/and/pred/not) | **6종 (+implies)** — template V4 1행 추가(semantic hint 금지), schema·profile hash 갱신 |
| primary metric | DirectMatch (full-IR) | **O1ScopeMatch** — `O1_SCOPE_PROJECTION_V1` signature 사이 exact structural match. estimand 불변, operationalization 변경(D-25 §9) |
| 라벨 정체성 | 채점(codec 경유) | **DIAGNOSTIC_ONLY** — 행별 `diagnostic_label_identity` 필드로 보존, 채점 무관여 |
| 적격성 | 라벨 도달성(D-24) | **MEASUREMENT_SATISFIABILITY_V2** (결정론 hidden witness, model-facing 금지) — 도달성은 진단 필드로 강등(D-26 Q26.3) |
| FOLIO in-N | 142p1·695p1·404p0·376p4·598p4 | **142p1·695p1·404p3·721p1·274p1** — 적격 풀 16(식별자 부재 1건 기계 제외)에서 seed selector 재실행. 주: V1의 원 선별과 우연히 일치(D-26 §16의 "우연히 동일" 경로) |
| controls | FOLIO 3 | FOLIO 3(175p1·500p4·1377p0) + **PMB projection control 3 신설**(p12-d2559·p11-d2268·p24-d2685 — D-25 §29, F3형 사각 차단) |
| PMB in-N 15 | — | 선별·commitment 3필드 불변(기계 보증: `test_stage2_freeze_v4.py`), profile hash 필드만 V4 |
| 코드 결박 | adapter만 | + projection·satisfiability·canonical core·eval profile 모듈 해시를 manifest `contract_hashes`에 pin — 수정 시 동결 자동 실효 |

manifest V4 sha256: `723ed98c2ce1c2d9edb7892c6aeb2760dc18e03ad93b94081d9e0d5dbc8b4ec8`
profile hash V4: `15b01b4bfd282e348f822511870c5a2d12a0e411bb39a43b811696f8a43a0899`

## A2.3 수용 기준 (불변 — D-25 §10, D-26 §17)

N=20, O1ScopeMatch PASS≥16 ∧ multi 4/5 ∧ 최종 ERROR=0 ∧ 예상 밖
UNSCORABLE=0. 결과 보고 표기: **"O1 quantifier-scope structural match
rate"** — "full semantic IR accuracy"라는 서술 금지(D-25 §30).

## A2.4 known source-specific challenge (유지)

AMENDMENT 1의 문안 그대로 유지 — FOLIO gold topology는 estimand이며
비교층 재작성 금지(반례 104/256, D-25 §13 재확인).
