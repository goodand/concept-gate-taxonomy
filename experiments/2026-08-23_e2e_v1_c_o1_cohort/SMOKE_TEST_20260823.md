# Stage 2 코호트 실행 전 smoke test — 2026-08-23

- 문서 종류: **운영 로그**. 동결 표면이 아니며 동결 표면을 수정하지 않았다.
- 지시: "코호트 실행 전 smoke test를 진행해라, 이후에 코호트 승인한다."
- 결론 요약: **파이프라인 3단 전부 관통(S1·S2·S3 PASS) — 그러나 S3의 live
  산출이 봉쇄 결함 1건(B1)을 적발했다. 코호트는 현 동결 표면으로 실행하면
  구조적으로 수용 불가이므로, B1의 외부 판정(Q24) 전 실행 불가.**

## 0. 설계 — 무엇을 smoke라 정의했는가

동결 fixture 20건에 실제 subject를 붙이는 순간 그것은 smoke가 아니라 코호트
본체다. 따라서 smoke는 세 층으로 나눴고, live dispatch는 **코호트 밖 발명
재료 4건**으로만 했다:

| 층 | 내용 | dispatch | 동결 재료 접촉 |
|---|---|---|---|
| S1 | 동결 표면 무결성: profile hash 재계산, fixture 23/23 캐시 왕복, oracle 재도출(commitment 대조) 20+3 | 없음 | 읽기만 |
| S2 | 동결 구성(constructors=O1_V1 5종)으로 build_cohort→export_dispatch_args, 리허설이 실측한 API 계약 3건 + 봉투·verbatim·격리 검증 13항목 | 없음 | manifest의 profile만 참조 |
| S3 | 발명 4건을 실제 경로(세션 Workflow, `agentType: o1-compiler`, model haiku, 봉투 schema)로 live dispatch → 실제 `ingest_outputs`/`score` 관통 | **4 trial** | 없음 (재료 전부 발명) |

재사용 조사(Haiku, xhigh 위임)는 FULL_MATCH를 보고했으나 lead 재실측에서
**과다 주장**으로 정정(P12): 후보는 전부 조작 출력 기반 계약 테스트였고,
리허설(REHEARSAL_20260823.md)은 live였지만 **동결 전 구성**(constructor 4종,
root `$ref` schema — scratchpad `rehearsal/dispatch_args.json`으로 실측
대조)이었다. 판정 정정: COMBINABLE_PARTS — 기존 모듈을 조립하고 신규 코드는
scratchpad glue 3본뿐(저장소 외).

## 1. 결과

### S1 — PASS (4/4 + 뮤테이션 2/2 + 자격 3×5)

- profile hash 재계산 = manifest = freeze 모듈: `dcda0f63e19c980d…` 3자 일치
- fixture 캐시 왕복 23/23 (HANDOFF §3-1의 조건 충족 — 캐시 재구축 불필요)
- oracle 재도출: 코호트 20/20 + control 3/3, expected_ir_sha256 전부 일치
- 뮤테이션: expected_ir 1글자 변조→`OracleDrift` 발생 확인 / 캐시 바이트
  변조→`resolve_fixture` execution="unavailable" 확인 (둘 다 물었다)
- adapter 자격 게이트 3폴더(o1/sbn/fol) 각 5 passed — 코드 해시 라이브 대조

### S2 — PASS (13/13)

동결 구성으로 만든 dispatch 인자가 리허설이 400 응답으로 실측했던 API 계약
3건($schema 금지·root type 필수·root 결합자 금지→봉투)을 전부 충족.
`not` 분지가 schema에 실재(리허설 schema에는 없었다 — **이번 smoke 전까지
live dispatch 이력이 없던 유일한 constructor**). subject pin
`o1-compiler`=`891dd0d6c2cfc8f7…`, plan에 oracle 정보 구조적 부재, 프롬프트
verbatim 렌더 확인. 부수 확인: 합성 manifest의 `source_locator`를 문자열로
넣자 `_assert_commitment_entry_complete`가 거부 — 가드 실동작 증거.

### S3 — PASS (파이프라인) / 결함 적발 (내용)

live dispatch 4/4 완료(전부 봉투 준수, 도구 호출 각 1회), 실제
`ingest_outputs`→`score` 관통: 행 회계 4행 유령/누락 0, ERROR 0, report
산출(2×2, acceptance, stratum floor 평가), **결과 overwrite 재시도 →
`ResultsOverwriteRefused` 발생 확인**. `not`이 SMOKE-03/04 산출에 실제 등장
— 양화-부정 stratum의 표현 경로 live 확인.

채점 내용은 4/4 fail이었고, 그 원인 분해가 B1이다.

## 2. B1 — 봉쇄 결함: FOLIO 술어 라벨 규약 미정합

### 실측 사슬

1. SMOKE-02("Every zorble glims.", LF `∀x (Zorble(x) → Glims(x))`)가
   `predicate_arguments`로 fail. 정규화 양측을 직접 대조:
   oracle 술어 = `{Zorble, Glims}`, subject 술어 = `{zorble, glims}` —
   **전체 소문자화하면 두 IR이 완전 동일**. 즉 유일한 차이가 대소문자.
2. 원인: `adapt_fol`은 술어명을 원문 그대로 보존하고,
   `O1_PMB_LEMMA_NO_SENSE_V1`은 **synset 형태(`X.n.01`)만** lemma·소문자화
   한다(`_stage2_eval_profile.py` SYNSET_PATTERN). FOLIO형 술어(`Lab`,
   `CanCatch`)는 패턴 불일치로 정규화를 통과하지 못하고 대문자로 남는다.
   반면 동결 template은 subject에게 "Use lowercase predicate names taken
   from the sentence's content words"를 강제한다.
3. 동결 FOLIO 8건(N내 5 + control 3) 전수 실측 — oracle 술어가 전부
   대문자/CamelCase:

   | case | oracle 술어 | 분류 |
   |---|---|---|
   | FOLIO-142p1 | Ball, CanCatch, Good | 대소문자만 |
   | FOLIO-695p1 | Communicate, Know, UniversalLanguage | 대소문자만 |
   | FOLIO-404p3 | …, **SpectatorsBetOn** | 문장에 없는 저작 어휘 |
   | FOLIO-721p1 | Dog, **OnRoof**, **WentWrong** | 문장에 없는 저작 어휘 |
   | FOLIO-274p1 | **Company, HoldingCompany**, Holds | 문장에 없는 저작 어휘 |
   | FOLIO-175p1 | Cheaper, Lab | 대소문자만 |
   | FOLIO-500p4 | Horse, Racehorse, **Racing** | 문장에 없는 저작 어휘 |
   | FOLIO-1377p0 | Eat, Human | 대소문자만 |

### 파급 (동결 수용 기준에 대입)

- control 3/3 = 코호트 해석 가능 조건(HANDOFF §3-2) → **0/3 확정적**
- multi_quantifier floor 4/5(D-22) → FOLIO 5건 전부 라벨 fail → **0/5 확정적**
- 따라서 PMB 15건의 성적과 무관하게 **수용 불가가 사전 결정**되어 있다 —
  측정하려는 것(scope 컴파일)과 무관한 라벨 규약 차이로 estimand가 오염된다
  (Q22.3이 PMB WSD에 대해 죽인 것과 동형의 문제).

### 왜 사전 검증 23/23이 놓쳤는가

동결 전 검증과 자격 게이트는 adapter·비교층·격리를 **각각** 검증했고,
리허설 술어 정합 요건("술어 명명 규약의 template↔adapter 정합")은 Q22.3이
**PMB에 대해서만** 해소했다(O1_PMB_LEMMA_NO_SENSE_V1 — 이름부터 PMB다).
D-23은 FOLIO의 **구조**(lowering·중립 ∃·순서 불변식)만 다뤘고 술어 라벨
규약 언급이 0건이다(grep 실측). 즉 두 판정의 이음새가 공백이었고, 그
공백은 **동결 구성 전체를 한 번에 live로 관통**해야만 보였다 — 이번 smoke가
그 첫 관통이다.

### 왜 여기서 고치지 않았는가

해소 경로가 전부 동결 표면이다: template 수정(동결), 비교층/profile 확장
(D-19 §12 판정 사안), fixture 교체(동결 manifest). stop condition
`NO_FROZEN_SURFACE_EDITS`에 따라 수정 없이 상신한다 —
`docs/DESIGN_REQUEST_folio_predicate_labels.md` (Q24).

부수 관찰(차단 아님, Q24에 병기): SMOKE-01이 `operator_type`으로 fail —
발명 LF를 FOLIO 표면 관행(∀x∃y(A∧B→C))으로 썼더니 subject의 자연 독해
(∀x(A→∃y(B∧C)))와 구조가 갈렸고, D-23이 implication-crossing 재작성을
금지(56/256 반례)하므로 비교층이 이를 이어줄 수 없다. 동결 FOLIO-142p1이
정확히 이 형태다. 라벨이 해소되어도 이 topology 차이가 남을 수 있다.

## 3. 재현

- 재료·스크립트: scratchpad `smoke/`(s1_integrity.py, s2_dispatch_contract.py,
  s3_ingest_score.py, dispatch_outputs.json) — 저장소 밖, 커밋 안 함.
  발명 4문장과 LF는 s2 스크립트 CASES 상수에 verbatim.
- live dispatch 기록: 세션 Workflow `wf_2129e74d-4d7` (4 agents, 오류 0).
- B1 재현 1줄: `adapt_fol("∀x (Zorble(x) → Glims(x))")`의 술어명이 대문자로
  남는 것 + `_stage2_eval_profile.SYNSET_PATTERN`이 그것을 건드리지 않는 것.

---

## 추기 (같은 날) — V2 재동결 후 smoke 전체 재실행 (판정 §11 요구)

D-E2E-v1-24 적용(`FOLIO_LABEL_LOWERCASE_V1` codec + source별 dispatch +
도달성 적격 술어 + FOLIO 두 stratum 재선별 → `stage2_fixture_manifest_v2.json`,
profile hash `c9d22d5c…`) 후 S1~S3을 V2 구성으로 재실행했다.

| 층 | 결과 |
|---|---|
| S1 (V2 manifest) | PASS — profile hash 3자 일치(manifest=재계산=`freeze_stage2_v2.PROFILE_HASH_V2`), fixture 왕복 23/23, oracle drift 0 (20+3) |
| S1 (V1 manifest) | PASS — V1 감사 표면 무손상 교차 확인 |
| S2 | PASS 13/13 — smoke 재료 case_id를 `FOLIO-SMK-*`로 갱신(비교층 dispatch가 source 결박이므로) |
| S3 | PASS — live 4/4 봉투 준수, 행 회계 정확, overwrite 거부 |

**B1 소멸의 live 차등 증거** (동일 발명 문장, V1 파이프라인 대 V2):

| 재료 | V1 결과 | V2 결과 | 해석 |
|---|---|---|---|
| Every zorble glims (대소문자만 차이) | fail `[predicate_arguments]` | **pass** | B1이 죽었다 |
| Some tikk does not prax | fail `[predicate_arguments]` | **pass** | `not` 경로 + codec 동시 확인 |
| No zorble glims (subject가 ¬∃로 표현) | fail | fail `[operator_type]` | 재작성 금지 유지 — **estimand 신호** |
| Every quux mels some florp (topology 차이) | fail `[operator_type]` | fail `[operator_type]` | Q24.4: 측정 대상 그대로 |

라벨 잡음이 사라지고 semantic topology 차이만 남았다 — 판정이 정의한
"measurement repair"의 실측 형태다. 게이트 전체: **13 passed / 0 failed /
1 blocked**(owlready2 — 무관), cohort 실험 게이트 60→90 tests.

구현 이력 각주: 재사용 조사(Haiku·xhigh)는 `freeze_stage2.py`의
"module-level 실행 위험"을 과보수로, 존재하지 않는 `folio_entry` 심볼을
재사용 후보로 보고했다(P12 — lead 재실측으로 정정). codec 위임 구현
(Haiku·Medium)은 지시에 없는 `SMOKE-` dispatch 분지를 추가했다가 검수에서
제거됐고, 그 거부가 계약(`test_dispatch_unknown_prefix_refuses`)에
고정됐다. desugar가 중립 제한식을 `name=="True"` 문자열로 식별하므로
codec이 예약 토큰을 보존해야 한다는 함정은 조사·위임 모두 못 봤고 lead
재실측이 잡아 계약화했다(`test_folio_preserves_reserved_true_token`).

---

## 추기 2 (같은 날) — V4 재동결 후 smoke 재실행 (D-25·D-26 적용 검증)

V4(방언 6종 +implies, O1ScopeMatch=projection 위 exact match, SAT gate V2,
FOLIO selector 재실행, PMB projection control 3 신설, profile hash
`15b01b4b…`)로 S1~S3 재실행:

| 층 | 결과 |
|---|---|
| S1 | PASS — 왕복 26/26(코호트 20 + control 6), drift 0, profile 자기 일관 |
| S2 | PASS 15/15 — **implies 분지가 schema·template에 실재**(live 이력 없던 constructor) |
| S3 | PASS — live 5/5 봉투 준수(∃-scope 함의 재료 SMK-05 포함), O1ScopeMatch 지표 산출, overwrite 거부 |

채점 내용(발명 재료 — 파이프라인 검증 목적): pass 2 / fail 3, **fail 전부
operator_type(scope topology)** — 라벨·granularity 잡음 0. V2 대비 차등:
같은 재료의 실패 원인이 predicate_arguments(라벨)에서 순수 scope 신호로
이동 완료. subject는 implies가 주어져도 SMK-05를 제한식 ∀-형으로 컴파일해
gold의 ∃-scope 함의와 갈렸다 — D-26 §2가 예고한 "이제 측정 가능해진
estimand" 그 자체다.

계보 기록: V3는 artifact 생성 전 SAT gate에 차단(ABORTED_PRE_FREEZE).
FOLIO in-N 재선별(적격 16, 식별자 부재 1건 기계 제외)이 **V1의 원 선별과
우연히 일치** — V2의 도달성 선별만이 우회로였다(D-26 §16 "우연히 동일"
경로). 게이트: 13/0/1, cohort 실험 128 tests. 탐색 사다리 각주: projection·
SAT·V4 freeze의 공백은 이 실험의 동결 계약(판정 retain/exclude 목록)에
결박된 고유 로직이라 subtree 단계는 YAGNI로 생략(이전 codec 라운드와 동일
판단), witness 렌더러 포함 전부 기존 모듈 확장으로 해소.
