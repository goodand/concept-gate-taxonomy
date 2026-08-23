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
