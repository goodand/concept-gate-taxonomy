# RESEARCH REQUEST (3차) — ERG/MRS + Redwoods의 item locator와 권리

- 수신자: **조사용 agent** (다른 workspace, zero context 전제 — 이 문서가
  맥락 전부. 설계용 agent 아님)
- 발신: ConceptGate 운영 세션, 2026-08-24
- 관계: 1차(기수 source)·2차(비례 + BLOCKED 해소 + 방언 정합) 회신을
  수령·검증 완료했다. 이 3차는 **2차가 남긴 단 하나의 유망 경로**를 좁힌다.
- 후속: 회신을 운영 세션이 검증 후 적격성은 별도 기계 실측.
  **조사에게 적격성 판정을 청하지 않는다** — 사실 확인만.

## 0. ★ Prior Rulings / Excluded Sources — 다시 제안하지 마라

> **판정 D-E2E-v1-29 Q29.4로 이 절이 필수화됐다.** 단순 blacklist가 아니라
> source별로 `status / 판정 id / 사유 / scope / reopen 조건`을 기록한다 —
> 과거 배제가 영원한 금지가 되어 새 release를 자동 배제하는 반대 오류도
> 막기 위해서다. **reopen 조건이 충족된 경우에만** 재검토 대상이 된다.

```yaml
prior_source_rulings:
  wikisem:
    status: EXCLUDED
    ruling: D-E2E-v1-21
    scope: O1_v1_sentence_level_acceptance
    reasons: [article_level_LF, sentence_level_alignment_absent,
              O1_v0_coverage_zero, discourse_operators_outside_profile]
    reopen_only_if: [upstream_publishes_sentence_level_aligned_LF,
                     materially_different_version]
  amr_bp_amrnews:
    status: EXCLUDED
    scope: O1_v1 (English only)
    reasons: [language_mismatch_portuguese, amr_does_not_represent_scope]
    reopen_only_if: [english_release_with_scope_representation]
  amr_3_0_english:
    status: EXCLUDED
    reasons: [amr_normative_doc_states_no_quantifier_scope]
    reopen_only_if: [scope_layer_added_upstream]
  fracas:
    status: EXCLUDED
    reasons: [gold_is_inference_label_not_formal_MR]
    reopen_only_if: [formal_MR_layer_published]
  pmb_and_derivatives:
    status: IN_USE_SEPARATE_CHAIN
    reasons: [already_primary_source, derivatives_violate_independence]
  folio_v0_0:
    status: IN_USE
    scope: multi_quantifier_stratum
  qure_gqg_gqnli_udeplambda_qald:
    status: EXCLUDED_PENDING_EVIDENCE
    reasons: [no_sentence_level_full_formal_MR_evidence]
    reopen_only_if: [full_MR_gold_locator_provided]
```

아래 표는 위 스키마의 사람용 서술이다.

**이 절은 3차에 신설됐다.** 2차 회신이 유력 후보로 제시한 자원 하나가
우리 선행 설계 판정으로 **이미 부적격 처리된 것**이었고, 그 원인은 우리가
배제 목록을 조사에 알리지 않은 것이었다(같은 오류 2회 반복). 앞으로 모든
조사 요청서는 이 절을 갖는다.

| 배제된 source | 배제 근거 (우리 판정·실측) |
|---|---|
| **Ohio State Wikisem (Simple English Wikipedia → typed lambda)** | 선행 판정이 **부적격** 처리. 단위가 **기사**이고 우리 IR 프로파일과 교집합이 0(`0/121`). 우리 로컬 캐시 재실측: record 131건이 각각 여러 문장을 담은 단일 거대 LOGIC 식, `InAnaphorSet` 1690회·`Equal` 1297회(우리 방언 밖 담화 구성자), **논문에 나오는 `ratio=`·`count=`·`Most`가 배포본에는 0회**, `most` 54회 중 48회가 최상급 형용사(`A-aN:most`). → 후보 아님 |
| **PMB (Parallel Meaning Bank) 및 그 파생·재수출판** | 이미 주 source로 사용 중이며 별도 판정 사슬이 있다. 파생판도 독립성 조건 위반 |
| **FOLIO v0.0** | 이미 사용 중(다중 양화 전담) |
| **FraCaS** | 2차 확정: gold가 **함의 라벨**이고 문장별 형식 표상이 없다 |
| **AMRNews / AMR-BP (Brazilian Portuguese)** | 언어 불일치(우리 subject는 영어만) + AMR 정본이 quantifier scope 비표상 명시 |
| **AMR 3.0 (영어)** | 기수는 `:quant`로 남지만 정본이 quantifier scope 비표상을 명시 — 우리 측정 대상과 충돌 |
| **QuRe / GQG / GQNLI / UDepLambda / QALD** | 2차 확정: 양화 annotation은 있으나 **문장 단위 full formal MR**의 근거 미확보 |

또한 다음 사실은 **재조사 금지**(1·2차에서 확정):
GeoQuery GPL 2.0·수작업 250건·`at least one`의 존재 구조 환원 / ATIS의
`LDC User Agreement`·원 정본 SQL·`at least N→>N` mismatch / Overnight의
2차 배포 `CC BY-SA 4.0`·grammar 생성 LF·AMT paraphrase / QuantML의
`numRel+num`·`relativeSize`·`scoping` 구조와 ISO 24617-12 정본 지위.

## 1. 왜 ERG/MRS만 남았는가 (조사에 필요한 최소 맥락)

우리 subject 방언은 `forall / exists / and / pred / not / implies`이고
항은 변수·개체뿐이다 — **수치 상수·비교자·집합 크기 연산이 없다.**

2차 회신이 정본 근거로 답한 것: QuantML·Overnight·ATIS는 기수를 지우면
양화 구조가 무너진다(자동 `∃` 환원 규칙 없음). 즉 그 재료들은 기수를
버리고 쓸 수도 없다.

**유일한 예외가 ERG/MRS다.** 2차가 인용한 구조:

```text
Three dogs bark …
  bare_div_q_rel(… x …)  RSTR …  BODY …   ← 양화 EP
  card_rel(… x …)        CARG 3           ← 기수 EP (별개 노드)
  _dog_n(… x …)
_most_q(x, hRestrictor, hBody)             ← 비례 양화자
```

기수 EP와 양화 EP가 분리돼 있어, 우리 선행 투영 논리(비계를 제거하고
scope 구조만 측정)를 그대로 재사용할 수 있다. 그래서 3차는 이 계열만 본다.

2차가 남긴 정확한 공백: **"ERG/MRS formalism이 기수·비례를 표현한다"는
확인됐지만, "재배포 가능한 특정 Redwoods release 안에 실제 gold record로
존재한다"는 item-level locator는 미확보(BLOCKED)**.

## 2. 조사 질문

### R1 — Redwoods release 내 **비례(proportional) gold item locator** ★최우선

특정 배포본에서 `_most_q`(또는 그에 상응하는 비례 양화 EP)를 갖는
**실제 gold record**를 찾아라. 필요한 것:

1. release 식별자(예: Redwoods Ninth Growth, ERG 버전, DELPH-IN 배포 태그)
2. 그 안의 profile/파일 경로와 item 식별자
3. 그 item의 **표면 문장**과 **MRS 조각**(`_most_q`의 인자 handle 포함)
4. annotator가 그 분석을 선택했음을 보이는 근거(gold 여부)

**주의**: `most`가 최상급(`the most beautiful`)이나 상한 기수(`at most N`)
또는 부사(`mostly`)인 경우는 우리 정의의 비례가 **아니다** — 우리 쪽에서
이 오분류가 네 번의 동결을 통과한 이력이 있다. `_most_q`처럼 restrictor/
body handle을 갖는 **명사구 양화자**만 해당한다.

### R2 — Redwoods 내 **기수 gold item locator**

같은 형식으로, `card_rel`(`CARG N`)을 갖는 gold record 3건 이상.
정확수·하한·상한 중 어느 것인지 표시하라. 표면 문장과 MRS 조각 포함.
가능하면 **양화 EP와 card EP가 실제로 분리돼 있음**을 보이는 조각으로.

### R3 — 권리 사슬: metadata GPL과 component별 권리

2차가 확인한 것: 배포 metadata의 권리 표기가 **GPL**이고, Redwoods는
여러 출처의 component corpora를 포함한다.

1. 그 GPL 표기의 **정확한 원문과 위치**(어느 배포처의 어느 필드).
2. component corpora 목록과 **각 component의 출처·권리 표기**(예: 대화
   전사, 공개 웹 텍스트, 저작권 있는 문헌이 섞였는지). 우리는 원문을
   저장소에 담지 않고 해시·locator만 커밋하지만 **로컬 캐시 사용 조건**이
   걸린다.
3. R1·R2에서 찾은 item이 **어느 component에 속하는지**.

### R4 — MRS 정본 문법 (adapter 설계용)

우리는 MRS→우리 IR adapter를 새로 만들어야 한다. 필요한 정본 근거:

1. MRS의 정식 정의 문서(논문/매뉴얼)와 그 안의 **EP·handle·qeq/scope
   제약**의 규범적 서술 위치.
2. **양화자 EP의 표준 형태**(`_q` 접미 규약, RSTR/BODY 인자, generalized
   quantifier 목록 — `_every_q`, `_some_q`, `_most_q`, `bare_div_q_rel`,
   `udef_q` 등)와 각각의 의미.
3. **scope underspecification**의 처리: MRS는 scope를 완전 결정하지 않고
   handle 제약으로 남기는 것으로 알려져 있다. 그렇다면 (a) gold record가
   scope를 **하나로 확정**하는가, 아니면 (b) 여러 scope resolution이
   가능한 상태로 남는가? 후자면 어떤 도구·규약으로 resolution을 얻는가
   (예: utool, MRS→DMRS 변환, `scope resolution` 알고리즘)? **이 답이
   우리 오라클 성립 여부를 좌우한다** — 오라클은 하나의 확정 구조여야 한다.
4. 부정·함의가 MRS에서 어떻게 표현되는지(`neg_rel`, implication 처리) —
   우리 방언의 `not`·`implies`와 대응시키기 위해.

### R5 — 접근·형식·규모

1. Redwoods/ERG 배포의 실제 다운로드 경로(**URL을 원문 철자 그대로**).
   등록·라이선스 동의가 필요한지.
2. 파일 형식(profile 디렉터리 구조, `[incr tsdb()]` 등)과 MRS를 텍스트로
   얻는 표준 방법(예: `ace`, `pydelphin`, export 형식).
3. R1·R2 조건을 만족하는 item의 **대략적 규모 신호**(정확 수 불요, 출처
   명시). 비례가 1건뿐인지 수십 건인지가 우리 선별에 영향을 준다.

### R6 — 대안 DELPH-IN gold (R1이 BLOCKED로 끝날 경우만)

Redwoods 밖에 ERG로 분석된 다른 gold treebank가 있는가(예: DeepBank,
WeScience, ERG의 다른 profile). 있으면 각각 R1·R3의 최소 사실만.
**§0의 배제 목록에 있는 것은 제외한다.**

## 3. 독립성 조건 (변경 없음)

```yaml
third_source:
  different_corpus_authority: true      # PMB·FOLIO와 다른 기관/저작 주체
  independently_authored_gold: true     # 사람이 저작 또는 사람이 선택·검수한 gold
  not_derived_from_PMB: true
  not_project_generated: true
  separate_source_locator: true
  separate_adapter_profile_if_formalism_differs: true
  english_sentences: true               # 우리 subject는 영어만 받는다
```

Redwoods는 "annotator가 후보 분석 중 의도한 reading을 선택"하는 방식이므로
`independently_authored_gold`를 **사람이 선택·검수한 gold**로 읽는다 —
이 해석의 근거가 되는 원문 서술을 R3에 함께 인용해 주면 좋다.

## 4. 유지되는 3원칙 (1·2차에서 실제로 작동했다)

1. **라이선스를 정책으로 추정 금지** — 배포처의 명시 문구만 verbatim.
   문서(논문·표준)의 저작권을 **데이터**에 전이하지 마라. 2차가 SEMPRE의
   Apache 2.0을 Overnight 데이터에 전이하지 않은 것이 정확한 처리였다.
2. **원문 철자·URL 문자 그대로 시도** — 2차가 Wikisem 배포 페이지의
   `/dwnload` 철자를 그대로 쓴 것이 옳다(교정하면 404가 난다).
3. **BLOCKED와 없음을 구분** — 2차가 8건을 부재 판정 없이 BLOCKED로 유지한
   것이 옳다. 렌더러가 대용량 파일을 못 여는 것은 자료 부재가 아니다.

**추가 4원칙(3차 신설)**: **논문의 예시와 배포 corpus의 실물을 구분하라.**
2차에서 논문에 정의된 연산자(`ratio=`, `count=`)를 배포 corpus의 사실처럼
인접 서술한 사례가 있었고, 우리 실측에서 그 연산자가 배포본에 0회였다.
"정본 문법이 X를 표현할 수 있다"와 "이 배포본의 이 item에 X가 있다"를
**항상 별도 문장으로** 적어라.

## 5. 보고 형식

R항목별로: **사실 / 근거(URL·파일 경로·verbatim 인용) / 확신도 / BLOCKED
여부**. 시도했으나 실패한 경로 포함. §0의 배제·확정 사실은 다시 적지 마라.

우리가 자체 실측할 것(조사 범위 아님): 문장 단위 1:1 / 동결 방언 표현
가능성 / 표면 필터(대명사·고유명 배제) / 투영 신호 보존 / 측정 가능성 /
adapter 자격. 적격 하한은 **기수 ≥3건, 비례 ≥1건**이다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
