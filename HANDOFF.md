# HANDOFF — codex/h1-source-authority (2026-08-23, Stage 2 동결 직후)

프로젝트 식별자: **concept-gate-h1** (worktree `concept-gate-h1-wt`,
branch `codex/h1-source-authority`) · 실험 **E2E-v1 Stage 2** (O1 capability cohort).
이 handoff가 이 프로젝트의 현재 상태(state), 다음 행동(next action),
정지 조건(stop conditions)의 유일한 진입점이다.

이 worktree의 HANDOFF가 정본이다(main repo 것 아님). **이 문서는 포인터
중심**이다 — 상태 서술의 정본은 아래 문서들이고, 여기 중복 기재하지 않는다
(P4 예방). 이 문서에만 있는 것은 §3 "다음 실행 절차"뿐이다.

## 0. 기계 판독 상태 블록 (handoff 평가기 계약 — 코드는 아래 산문·정본과 1:1)

```yaml
state_code: D33_RECEIVED__COHORT_BLOCKED__QUALIFICATION_REQUIRED_BEFORE_V3   # V5 동결(투영 V1→V2·20건 재투영·채점 배선 교체)과 control 재선별 5/5는 끝났다. 그러나 D-33이 코호트를 막았다: 지시 표현의 참여자 ∃ 대 `entity` 항 불일치가 measurand인지 미정이고, `O1_SCOPE_PROJECTION_V3`이 예고됐으므로 **V2는 최종이 아니다**. **코호트 dispatch 누계 0건**
next_action_code: AWAIT_D34__THEN_QUALIFICATION_AND_V3   # **Q34 상신 완료(2026-08-24)** — 남은 것은 회신 대기다. D-33 권고 (b*): 경계를 먼저 독립 정의 → qualification → V3. 경계 규칙을 우리가 만들면 `operational_patch: forbidden` 위반이므로 **실사 결과만 Q34로 상신**한다. 실측 결론(§B.3·B.4): synset으로는 불가(`person.n.01`이 양화·지시·보통명사 세 부류에 걸침), 표면 토큰이 필요하나 표면 규칙 시도는 **4회 전부 다르게 실패**. `stage2_cohort_plan_v5.json`은 생성돼 있고 V3가 채점을 바꾸면 의도적으로 지워야 한다(`write_cohort`는 덮어쓰기 거부). dispatch는 매번 별도 승인
stop_condition_codes:
  - NO_COHORT_WITHOUT_USER_APPROVAL      # §1·§3 — 실행은 별도 승인
  - NO_FROZEN_SURFACE_EDITS              # §4 — V1·V2 동결 표면 수정은 D-19 §12 외부 판정 사안
authority: experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_fixture_manifest_v5.json  # V5 = 최신 동결(투영 전용 개정). 사전등록 본문은 PREREGISTRATION_STAGE2_V4.md가 여전히 정본
# 코드별 authority 근거절 — 위 코드를 주장할 때는 아래 절을 인용하라:
#   state_code             ← stage2_fixture_manifest_v5.json amendment (V5 = 투영 전용 개정, dispatch 0) + stage2_controls_results_v5_1.json (5/5)
#   next_action_code       ← docs/DESIGN_REQUEST_referential_participant_quantification.md (Q33 — 회신 전 코호트 금지)
#   NO_COHORT_WITHOUT_USER_APPROVAL ← CLAUDE.md "## 실행 승인" 절 (저장소 전역 운영 규칙 — 사전등록은 실행 허가가 아니다)
#   NO_FROZEN_SURFACE_EDITS         ← PREREGISTRATION_STAGE2_V4.md (D-19 §12; 개정은 D-24 §9 절차로만)
```

## 1. 현재 상태 한 줄

**측정 도구는 완성됐고, 도구가 무엇을 재는지의 질문 하나가 남았다.** V5 동결
(투영 `O1_SCOPE_PROJECTION_V2`, 20건 재투영, 채점 배선 교체)이 끝났고, D-27 §18의
control 재선별로 **5/5 통과**를 얻었다(V4 1/6 → V5 2/6 → V5.1 5/5, 사슬 최초).

그런데 그 통과는 in-N의 지배적 성질에 대해 **설계상 침묵한다**: 적격 술어
`has_excluded_participant`가 대명사·고유명 문장을 배제하므로 통과한 5건에는
지시 표현이 없다. 반면 PMB gold는 고유명·대명사·지시사를 **참여자 ∃로 인코딩**
하고 자연스러운 subject는 `entity` 항을 쓴다 — oracle 쪽에만 결박자가 하나 더
생겨 scope 서명이 갈린다. 이 부류는 control에서 **네 번 재현**됐다(V4 2건, V5 2건).

그래서 **Q33을 상신하고 코호트를 보류했다**. 관측 후에는 이 질문이 post-hoc이
되므로 사전에 물어야 한다. **코호트 dispatch 누계 0건**이다.

## 2. 정본 지도 (읽는 순서)

**graph 진입점**: [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX|RULING_CHAIN_INDEX]]
— 판정 **D-19~D-33** + 조사 6왕복 전부를 **1홉으로** 도달 가능하게
묶은 색인이다. `rg`로는 판정 문서를 찾을 수 없는 경우가 실측으로 확인됐으므로
(파일명이 질문의 어휘를 포함하지 않는다), 이어받는 세션은 **grep이 아니라 이
색인에서 시작**한다. 각 판정 문서 헤더에 `이전`/`다음` 링크가 있어 색인 없이도
사슬을 걸을 수 있다.

| 알고 싶은 것 | 정본 |
|---|---|
| 최신 상태·패턴 원장 | [[concept-gate-h1-wt/docs/H1A_PROBLEM_ANALYSIS\|H1A_PROBLEM_ANALYSIS]] **마지막 절** — 규약상 항상 문서 끝이 최신(현재 **§18**). 이 이름은 vault에 9개 있으므로 경로로 지정한다 |
| 판정·조사 사슬 전체 | [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX\|RULING_CHAIN_INDEX]] |
| **무엇이 코호트를 막고 있나** | [[DESIGN_DECISION_referential_participant_quantification\|D-33]] → 실사 상신 [[DESIGN_REQUEST_referential_existential_qualification\|Q34]] 회신 대기. — referential ∃ 경계가 미정의라 `dispatch: blocked` · `operational_patch: forbidden`. 우리가 경계를 그으면 위반이므로 **실사만 Q34로 상신**한다(§B.3·B.4가 재료) |
| 무엇이 동결됐고 무엇이 금지인가 | 사전등록 본문은 `PREREGISTRATION_STAGE2_V4.md`가 여전히 정본이고, **동결 산출은 V5**다(`stage2_fixture_manifest_v5.json` — 투영 전용 개정). D-33이 `O1_SCOPE_PROJECTION_V3`을 예고했으므로 **V5의 measurement_contract는 잠정**이다 |
| fixture commitment | 같은 폴더 `stage2_fixture_manifest_v5.json` (원문 0바이트 — 해시·locator만. V4에서 commitment 필드 바이트 동일, 추가된 것은 `expected_scope_signature_v2_sha256`) |
| 선별이 조작 불가능한 이유 | 같은 폴더 `freeze_stage2_v4.py`(in-N 선별) · `freeze_stage2_v5.py`(V5 = 투영 전용 개정, 재투영·서명 재생성이 전부 코드) · `freeze_controls_v5_1.py`(control 재선별, 적격 술어 2층) — seed·층 술어·투영 전부 코드가 정본이고 산출은 덮어쓰기를 거부한다 |
| 동결이 실효됐다는 선언 | 같은 폴더 `test_stage2_freeze_v4.py`의 `FREEZE_STATE`(= `V5_ACTIVE`) — SUPERSEDED 선언 하에서는 **drift가 존재해야 통과**한다(선언이 거짓일 수 없게). V5는 `test_stage2_freeze_v5.py`가 지킨다 |
| MRS 재료가 왜 아직 부적격인가 | [[RESEARCH_RESULT_mrs_redwoods_round3\|3차 조사 회신 + 우리 검증]] §B — 전수 37,066건 실측, 적격 기수 **0건**(BODY 비제약이 유일 장애 16,584건) |
| adapter 자격(코드 결박) | `experiments/2026-08-23_{o1,sbn,fol}_adapter_qualification/` — test_protocol이 코드 해시를 라이브와 대조: **커널·adapter를 고치면 자격이 자동 실효**된다(2026-08-24 실측: `cg_ir` 확장으로 3건 실효 → 재자격 9/9·9/9·7/7 재현) |
| 적대 검증 결과 | [[ADVERSARIAL_VALIDATION_20260823]] |
| 이 handoff가 실제로 복원 가능한가 | [[HANDOFF_EVALUATION_20260824]] — **9/9 복원·막힌 지점 0**, 그러나 결함 2건 적발(V5.1 운영 로그 누락 · 고아 노트 1건)과 **`vault_search`가 정본·D-33에 도달 못 함**. 1차는 [[HANDOFF_EVALUATION_20260823]](3/3) |
| 채점이 무엇을 재는가 | 같은 폴더 `_stage2_projection_pipeline_v2.py` — V1 전처리(desugar·관용구·granularity 다리) → V2 signature 합성. **이 모듈이 계약이고 V5 manifest가 해시를 pin한다**. 계약 정본은 `test_stage2_projection_pipeline_v2.py` |
| control이 무엇을 보증하고 무엇을 보증하지 않나 | [[CONTROLS_RUN_V5_20260824|V5 실행(2/6 → 정지)]] → [[CONTROLS_RUN_V5_1_20260824|V5.1 재선별(5/5)]]. D-33 §9: `control eligibility excludes X → control PASS therefore says nothing about X` — 적격 술어가 배제한 성질은 인증되지 않는다 |
| 무엇이 죽었고 대신 무엇을 쓰나 | [[LEGACY_REGISTER]] — 표기·후계자·복구 명령을 한 곳에. `test_legacy_register.py`가 등록부의 거짓말을 막는다(실재하지 않는 경로·후계자 없는 행·등록 안 된 표기). **버전 번호가 낮다고 legacy가 아니다** — `_stage2_scope_projection.py`(V2 채점의 전처리)·`freeze_stage2.py`(SEED 정본)·`.oracle_cache`·`vendor/`는 명시적 비-legacy로 적혀 있다 |
| 실행 기제 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/_stage2_*.py` + `conceptgate/cg_{sbn,fol}_adapter.py`, `cg_mrs_reader.py`, `cg_fixture_resolver.py` |

## 3. 다음 실행 절차 (사용자 승인 후 — 이 문서의 유일한 고유 내용)

전제: 게이트 `python3 scripts/run_gates.py` = 13 passed / 0 failed / 1
blocked(owlready2 — 무관). 실험 폴더 `python3 -m pytest .` = 373 passed.

### 이미 끝난 것 (다시 하지 마라)

- **V5 재동결 완료** — 투영 V1→V2, 20건 전량 재투영(**서명 20/20 변경이 정상**,
  `expected_ir_sha256`은 전건 불변), manifest에 `measurement_contract` ·
  `supersedes` · `score_comparability` · `measurement_semantics`, 채점 배선
  V2 교체. 커밋 `1adc471`.
- **control 4라운드** — V4 1/6 → V5 2/6 → D-27 §18 재선별 → **V5.1 5/5**.
  커밋 `fe0e618`·`3125d8d`·`e5ef159`.
- **코호트 plan 20건 생성** — `stage2_cohort_plan_v5.json`. **dispatch 0건.**

### 1. ~~Q34 상신~~ **완료(2026-08-24)** — 회신 대기가 다음 행동이다

D-33이 `(b*)`를 명했다: referential ∃ 경계를 **먼저 독립 정의**하고 그
qualification 통과 후에만 `O1_SCOPE_PROJECTION_V3`을 낸다. **경계 규칙을 우리가
만들면 `operational_patch: forbidden` 위반**이므로 실사 결과만 올린다.

상신서에 들어갈 재료는 이미 실측돼 있다 — D-33 문서 §B.3·§B.4:

- gold는 각 개념 노드에 **표면 토큰을 주석으로 기록**한다(`male.n.02 % him [18-22]`).
  즉 증거는 원리적으로 존재한다.
- 그러나 **synset만으로는 가를 수 없다**: `person.n.01`이 양화(`Everyone`·
  `Some`·`Nobody`) · 지시(`I`·`you`) · 보통명사(`passengers`) 세 부류에 걸친다.
- 표면 규칙 시도는 **4회 전부 다르게 실패**했다(양화/지시 혼동 · 부정관사 혼입 ·
  ANSI 이스케이프 오염 · 문두 대문자 오분류 — 마지막은 `has_excluded_participant`에
  이미 문서화된 같은 누출).

**FOLIO 실사 완료(2026-08-24)**: FOL은 지시 표현을 **상수**로 쓴다 — 적격 풀
799건 중 **116건(14%)**. 즉 **두 승인 source가 같은 현상을 반대로 인코딩**하고
측정이 그 불일치를 물려받았다. in-N 분포: PMB 15건에 문제 있음 · FOLIO 5건은
거의 없음(상수 사용 1건뿐). 이것이 Q34의 핵심 논거다.

### 2. D-34 수령 후 (판정 내용에 따라 갈림)

판정이 경계를 정하면: qualification 구현(TDD → Sonnet 5 위임) →
`O1_SCOPE_PROJECTION_V3` → **V6 재동결**(20건 재투영·서명 재생성) → 채점 배선
교체 → **`stage2_cohort_plan_v5.json`을 의도적으로 삭제하고 재생성**
(`write_cohort`는 덮어쓰기를 거부한다 — 이것은 안전장치이므로 우회하지 말고
지워라) → control 재실행.

판정이 "경계를 못 정한다"고 하면 그것도 답이다 — 그때는 PMB의 지시 표현
fixture가 estimand에 포함되는지가 재료 문제로 돌아간다.

### 3. 코호트 20건 dispatch — **별도 승인 + 되돌릴 수 없다**

`export_dispatch_args(plan)`으로 인자를 내고 **Workflow 하네스**로만 돌린다
(`agentType: "o1-compiler"`, `model: haiku`, `schema`= plan의
`provenance.output_schema`). **프롬프트를 손으로 재구성하지 마라** — 실측으로
바이트 불일치 0/20이 나왔다(개행 하나 차이). mechanical retry는 dispatch층
1회만(생성 전 인프라 실패), semantic retry 금지.

채점: `ingest_outputs`에 `pass_min=16`,
`stratum_floors={"multi_quantifier": (5, 4)}`, `strata`= manifest의 stratum,
`certified=None`(dormant-by-design — 사전등록 확정).

**이 dispatch가 "관측 0건" 체제를 영구히 끝낸다.** D-24~D-33의 모든 개정이
`cohort_dispatch_count: 0`에 근거했으므로, 이후에는 사전 개정이 불가능하다.

### 4. 결과 커밋

trials_raw 보존 + 결과는 동결과 **별도 커밋**(방법론 §1). 결과 보고 표기:
`O1-v1 source = PMB-5.1.0-gold(15) + FOLIO-v0.0(5)`, wikisem 결과와 비교 서술
금지(D-21 §11).

## 4. 하지 말 것 (이미 값비싸게 배운 것의 압축)

- 동결 표면 수정(§12 사안) / adapter·비교층 코드 수정(자격 실효 — 게이트가
  잡지만 재자격 비용) / fence 관용 파서 / 원문 corpus 바이트의 repo 유입 /
  부재 판정을 재실측 없이 수용(P12) / 빗나간 뮤테이션을 검증으로 계상(P16).
- **프롬프트를 손으로 재구성하지 마라.** plan이 유일 출처다 — 실측으로
  재구성본이 plan과 **0/20 바이트 불일치**였다(개행 하나). `export_dispatch_args`를
  거쳐라.
- **통과한 게이트가 무엇을 배제했는지 먼저 보라.** control 5/5는 적격 술어가
  지시 표현을 배제하므로 그 성질을 인증하지 않는다(D-33 §9). 침묵을 보증으로
  읽는 것이 이 구간의 가장 비싼 오독이었다.
- **경계·정규화 규칙을 우리 손으로 만들지 마라** — `operational_patch: forbidden`
  (D-31 Q31.4 · D-33). 계측기가 두 번 이상 다르게 틀리면 만들기를 멈추고
  "재료가 그 구별을 담고 있지 않다"를 가설로 올려라(4회 실패 실측).

## 5. 열린 항목 (차단 아님)

- **`concept-gate-e2.2-wt`의 h1a 구현 분기 병합 결정**(3차 정리 라운드가 발견 — `_h1a_diag*` 대 다른 4개 worktree의 `_h1a_score`/`_h1a_policy`, 정본 미결정).
- cert 축 활성화(의무 집합 정의 — 별도 사안), G64(PMB Δ66 모집단 정의),
  뮤테이션 하네스의 게이트화(P16), O3(재료 관문 미해결 — D-21이 조건부
  선행 허용).

## 6. 작업 대기열 (사용자 지정 — 2026-08-24, 순서 그대로)

D-33 수신 처리(검증 설계 → 설계 적대검증 → 검증 → 기록)를 끝낸 뒤 **이 순서로**
진행한다. 사용자가 순서를 지정했으므로 임의로 바꾸지 않는다.

| # | 할 일 | 완료 판정 |
|---|---|---|
| 1 | ~~**회고**~~ **완료(2026-08-24)** — §18 append. 신규 G125~G135, P12가 한 구간 5회로 지배, 기제 부채 +60행 | ✅ `docs/H1A_PROBLEM_ANALYSIS.md` §18 |
| 2 | ~~**handoff 갱신**~~ **완료(2026-08-24)** — §0 코드·§1 재작성, §2 낡은 행 5건 정정(D-19~D-33·§18·차단 요인·V4→V5·FREEZE_STATE) + 신설 행 2건(채점 계약·control 보증 범위), §3 전면 재작성, §4에 교훈 3건 | ✅ |
| 3 | ~~**handoff test**~~ **완료(2026-08-24)** — 9/9 복원·막힌 지점 0, 결함 3건 적발·수리(V5.1 로그 누락 · 고아 노트 · 스텁 리다이렉트) | ✅ [[HANDOFF_EVALUATION_20260824]] |
| 4 | ~~**삭제 후보 탐색 — 현재 작업 범위**~~ **완료** — 후보 0건, 문서 공백 1건 수리 | ✅ |
| 5 | ~~**탐색 범위 분할**~~ **완료** — Safety Gate 후 규모 실측으로 A(taxonomy 173M)·B(데이터·캐시)·C(archive+worktree 5개)로 분할 | ✅ |
| 6 | ~~**탐색 subagent(haiku) 위임**~~ **완료** — 3건 위임·lead 재실측 → **삭제 0건**, 병합 대기 4건 발견 | ✅ [[WORKSPACE_CLEANUP_20260824_ROUND3]] |

### 이 대기열에 이미 적용되는 규율

- 3항의 zero-context 시험은 **5/5를 목표로 하지 않는다** — 복원 실패가 나오면
  그것이 handoff의 결함이고 고칠 대상이다. 통과율을 좋게 만들려고 시험을
  약화시키면 시험이 무의미해진다.
- 4~6항: **날짜는 근거가 아니다.** `SAFE_TO_REMOVE`는 근거 3항이 필요하고,
  0건이 정당한 답이다(2차 라운드 실측: worktree 0 · vault 0 · 파일 1). 선행
  결정을 재제안하지 않기 위해 [[WORKSPACE_CLEANUP_20260823|1차 라운드]]와
  [[WORKSPACE_CLEANUP_20260824|2차 라운드]]를 **먼저 읽는다**.
- 4~6항의 함정 3개(2차 라운드에서 실측된 것): worktree 삭제 안전성의 기준은
  병합이 아니라 **push**다 · **상호 참조는 참조가 아니다**(닫힌 고리는 둘 다
  후보) · **캐시라도 테스트가 읽으면 하중 자산**이다.
