# Stage 2 (E2E-v1-C) 사전등록 — **DRAFT, 미동결**

status: **DRAFT**. 동결 조건 = 신규 O1 source가 적격성 6조건(D-E2E-v1-21
Q21.2 b\*)을 통과하고 fixture manifest 20건 + constructor profile hash가
같은 커밋에서 확정될 때. 그 전까지 이 문서는 예고이지 계약이 아니다.
`[TBD-*]` 슬롯이 남아 있는 한 동결 커밋을 만들지 마라 — 이 문장 자체가
동결 게이트의 검사 대상이다.

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
| oracle leakage prohibition | 구조적: dispatch-plan 빌더가 LF를 resolve하지 않음 + 누출 테스트 | 준비물 ③ |
| no post-result fixture replacement / N increase | 서약 — 위반은 §12 외부 판정 사안 | D-19 §12 |
| UNSCORABLE 회계 | freeze 전 unsupported=INELIGIBLE(표본 밖) / freeze 후=UNEXPECTED_UNSCORABLE(수용 FAIL) | D-21 §14 |
| 결과 보고 표기 | `O1-v1 source = [TBD-SOURCE]` 명시, wikisem 결과와 비교 서술 금지 | D-21 §11 |

## B. source 종속 — **[TBD], 동결 시 확정**

| §11 항목 | 슬롯 |
|---|---|
| source locator | PMB 5.1.0 = **QUALIFIED_PARTIAL_SOURCE**(D-22, ≤15건) + `[TBD-SOURCE-2]` 독립 제2 source(≥5건, 다중 양화 gold, PMB 파생 금지 — 조사 위임 예정) |
| fixture IDs + hashes | `[TBD-MANIFEST]` — commitment 필드만(D-20), 원문 0바이트 |
| expected canonical IR | `[TBD-EXPECTED-IR-HASHES]` — adapter(자격 7/7 PASS, 코드 결박) 산출의 sha256 |
| canonicalization profile | `[TBD-PROFILE-HASH]` — D-22 §19: IR constructor와 source encoding profile(PMB_SBN_5_1 ¬∃¬→∀ codec) 분리 기록; 평가측 O1_PMB_LEMMA_NO_SENSE_V1(lemma 정규화, 커널 밖) — constructor 목록에서 유도(②의 단일 출처), manifest와 같은 커밋에서 hash 동결 |
| model/version/config | `[TBD-MODEL]` — 프로브는 haiku로 수행했으나 코호트 모델은 동결 시 확정 |
| qualification vs capability fixture 분리 | `[TBD-SPLIT]` — 적격성 스캔(2경로, 불일치=FREEZE_BLOCKED) 통과 목록에서 분리 |

## C. 동결 절차 (예고)

1. 적격성 스캔: Path A(adapter 능력) + Path B(독립 constructor 스캐너) —
   불일치 시 FREEZE_BLOCKED (D-21 §15).
2. 선별 항목별 `.met` source/license 확인을 **같은 단계에** 묶는다
   (PMB 조사 결과 §운영 세션으로 넘길 핵심 사실).
3. manifest + profile hash + 이 문서의 TBD 해소를 **한 커밋**으로 동결,
   결과는 별도 커밋(방법론 §1).
