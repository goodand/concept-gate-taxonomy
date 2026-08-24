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
next_action_code: DEFINE_REFERENTIAL_EXISTENTIAL_THEN_Q34   # D-33 권고 (b*): referential ∃ 경계를 **먼저 독립 정의** → qualification → V3. 경계 규칙을 우리가 만들면 `operational_patch: forbidden` 위반이므로 **실사 결과만 Q34로 상신**한다. 실측 결론(§B.3·B.4): synset으로는 불가(`person.n.01`이 양화·지시·보통명사 세 부류에 걸침), 표면 토큰이 필요하나 표면 규칙 시도는 **4회 전부 다르게 실패**. `stage2_cohort_plan_v5.json`은 생성돼 있고 V3가 채점을 바꾸면 의도적으로 지워야 한다(`write_cohort`는 덮어쓰기 거부). dispatch는 매번 별도 승인
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
— 판정 D-19~D-29 + Q30 상신 + 조사 6왕복 전부를 **1홉으로** 도달 가능하게
묶은 색인이다. `rg`로는 판정 문서를 찾을 수 없는 경우가 실측으로 확인됐으므로
(파일명이 질문의 어휘를 포함하지 않는다), 이어받는 세션은 **grep이 아니라 이
색인에서 시작**한다. 각 판정 문서 헤더에 `이전`/`다음` 링크가 있어 색인 없이도
사슬을 걸을 수 있다.

| 알고 싶은 것 | 정본 |
|---|---|
| 최신 상태·패턴 원장 | [[concept-gate-h1-wt/docs/H1A_PROBLEM_ANALYSIS\|H1A_PROBLEM_ANALYSIS]] **마지막 절** — 규약상 항상 문서 끝이 최신(현재 §13). 이 이름은 vault에 9개 있으므로 경로로 지정한다 |
| 판정·조사 사슬 전체 | [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX\|RULING_CHAIN_INDEX]] |
| 판정 대기 중인 것 | [[DESIGN_REQUEST_mrs_fail_closed_and_rights\|Q30]] — 7문항. **이것이 현재 유일한 차단 요인**이다 |
| 무엇이 동결됐고 무엇이 금지인가 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/PREREGISTRATION_STAGE2_V4.md` (V4 = 최신 동결. **D-27~D-29 구현으로 실효**, V5 대기) |
| fixture commitment | 같은 폴더 `stage2_fixture_manifest_v4.json` (원문 0바이트 — 해시·locator만) |
| 선별이 조작 불가능한 이유 | 같은 폴더 `freeze_stage2_v4.py` (seed·층 술어 전부 코드가 정본) |
| 동결이 실효됐다는 선언 | 같은 폴더 `test_stage2_freeze_v4.py`의 `FREEZE_STATE` — SUPERSEDED 선언 하에서는 **drift가 존재해야 통과**한다(선언이 거짓일 수 없게) |
| MRS 재료가 왜 아직 부적격인가 | [[RESEARCH_RESULT_mrs_redwoods_round3\|3차 조사 회신 + 우리 검증]] §B — 전수 37,066건 실측, 적격 기수 **0건**(BODY 비제약이 유일 장애 16,584건) |
| adapter 자격(코드 결박) | `experiments/2026-08-23_{o1,sbn,fol}_adapter_qualification/` — test_protocol이 코드 해시를 라이브와 대조: **커널·adapter를 고치면 자격이 자동 실효**된다(2026-08-24 실측: `cg_ir` 확장으로 3건 실효 → 재자격 9/9·9/9·7/7 재현) |
| 적대 검증 결과 | [[ADVERSARIAL_VALIDATION_20260823]] |
| 이 handoff가 실제로 복원 가능한가 | [[HANDOFF_EVALUATION_20260823]] — zero-context 평가기 실측(3/3) + 결함 2건 수리 + 남은 한계 4건 |
| 실행 기제 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/_stage2_*.py` + `conceptgate/cg_{sbn,fol}_adapter.py`, `cg_mrs_reader.py`, `cg_fixture_resolver.py` |

## 3. 다음 실행 절차 (사용자 승인 후 — 이 문서의 유일한 고유 내용)

전제: 게이트 `python3 scripts/run_gates.py` = 13 passed / 0 failed / 1
blocked(owlready2 — 무관) 확인.

**0. 먼저 V5 재동결이 끝나야 한다(D-32).** 아래 1~4는 **V5 동결 이후**의
절차다. 현재 동결(V4)은 실효 상태이고, D-32가 새 투영 profile
`O1_SCOPE_PROJECTION_V2`를 명했으므로 그 전에:

   a. **Q32-C 회신**을 받는다(`docs/DESIGN_REQUEST_q_rstr_body_position.md`).
      회신 전 재동결 금지 — 태깅 지시가 오면 20건 서명을 다시 찍어야 한다.
   b. **20건 전량 재투영** → `expected_ir_sha256` 재생성.
      **20/20이 바뀌는 것이 정상**이다(V2는 모든 술어를 opaque incidence로
      바꾼다). 5/20 같은 부분 변경을 기대하면 잘못 잰 것이다 — 실측 근거는
      회고 §16 G121.
   c. manifest에 `measurement_contract`(profile·profile_hash·module_sha256) ·
      `supersedes: [O1_SCOPE_PROJECTION_V1]` · `score_comparability.V1_to_V2.
      direct_numeric_comparison: false` 를 넣는다. 사슬에
      `V1–V4 = V1 semantics` / `V5 onward = V2 semantics` 선언.
   d. `PRE_EXECUTION_FREEZE_AMENDMENT_V1` 절차로 **V5 동결**. V1~V4 파일은
      바이트 불변(특히 `_stage2_scope_projection.py` V1을 고치지 마라 —
      그 해시가 V4 manifest에 핀돼 있고 역사적 측정 의미론의 증인이다).
   e. 채점 배선을 V2로 교체하고 게이트 재확인.

1. **재료 캐시 확인**: `.oracle_cache/`(gitignore)가 비어 있으면 재구축 —
   PMB는 `docs/RESEARCH_RESULT_o1_corpus_access.md` 부록의 URL 14개에서
   재취득(공식 zip sha256 `1533d2a5…`), FOLIO는 GitHub v0.0 raw(sha256은
   `PMB_SELECTION_RULE_DRAFT.md` FOLIO 층 절). 그 후 `freeze_stage2.py`를
   **실행하지 말 것**(manifest 존재 시 자체 거부하지만, 캐시 재구축은
   manifest의 해시로 `cg_fixture_resolver.resolve_fixture` 왕복 확인으로
   충분하다 — 23/23이어야 한다).
2. **adapter control 3건 먼저**(N 밖, D-22 §15): manifest의
   `folio_simple_controls`로 spec을 만들어 `_stage2_cohort.build_cohort`
   (constructors=O1_V1 5종) → dispatch는 **세션의 Workflow 하네스**로 —
   `agentType: "o1-compiler"`, `model: haiku`, `schema` = plan의
   `provenance.output_schema`(envelope — 실행기 `export_dispatch_args`가
   그대로 내준다). 산출을 `_stage2_run.ingest_outputs`로 채점. 3/3 통과가
   본 코호트 해석 가능 조건.
3. **본 코호트 20건**: 같은 경로. `derive_expected_irs`의 adapter 인자는
   case_id 접두어로 분기(PMB-→adapt_sbn, FOLIO-→adapt_fol) — LF 바이트를
   받아 IR 반환. 채점 인자: `pass_min=16`,
   `stratum_floors={"multi_quantifier": (5, 4)}`,
   `strata`= manifest entries의 stratum 필드에서, `certified=None`
   (dormant-by-design — 사전등록 확정). mechanical retry는 dispatch층
   1회만(생성 전 인프라 실패), semantic retry 금지.
4. **결과 커밋**: trials_raw 보존 + 결과는 동결과 별도 커밋(방법론 §1).
   결과 보고 표기: `O1-v1 source = PMB-5.1.0-gold(15) + FOLIO-v0.0(5)`,
   wikisem 결과와 비교 서술 금지(D-21 §11).

## 4. 하지 말 것 (이미 값비싸게 배운 것의 압축)

- 동결 표면 수정(§12 사안) / adapter·비교층 코드 수정(자격 실효 — 게이트가
  잡지만 재자격 비용) / fence 관용 파서 / 원문 corpus 바이트의 repo 유입 /
  부재 판정을 재실측 없이 수용(P12) / 빗나간 뮤테이션을 검증으로 계상(P16).

## 5. 열린 항목 (차단 아님)

- cert 축 활성화(의무 집합 정의 — 별도 사안), G64(PMB Δ66 모집단 정의),
  뮤테이션 하네스의 게이트화(P16), O3(재료 관문 미해결 — D-21이 조건부
  선행 허용).

## 6. 작업 대기열 (사용자 지정 — 2026-08-24, 순서 그대로)

D-33 수신 처리(검증 설계 → 설계 적대검증 → 검증 → 기록)를 끝낸 뒤 **이 순서로**
진행한다. 사용자가 순서를 지정했으므로 임의로 바꾸지 않는다.

| # | 할 일 | 완료 판정 |
|---|---|---|
| 1 | ~~**회고**~~ **완료(2026-08-24)** — §18 append. 신규 G125~G135, P12가 한 구간 5회로 지배, 기제 부채 +60행 | ✅ `docs/H1A_PROBLEM_ANALYSIS.md` §18 |
| 2 | **handoff 갱신** | 이 문서의 §0 코드·§1·§3이 실제 상태와 1:1 |
| 3 | **handoff test** — ① `evidence-evaluator` MCP 사용(handoff 시점의 도구다) ② **zero-context subagent 복원 시험** | 무맥락 agent가 §0만 읽고 다음 행동을 정확히 재구성. 실패 항목은 숨기지 않고 기록 |
| 4 | **삭제 후보 탐색 — 현재 작업 범위** | 이번 세션이 만든 산출물 중 중복·미채택·재생성 가능분을 먼저 식별 |
| 5 | **탐색 범위 분할** | 겹치지 않는 범위로 쪼갠다(3차 라운드) |
| 6 | **탐색 subagent(haiku) 위임** | 범위별 위임 → **lead가 상위 후보 직접 재실측**(P12) 후에만 삭제 |

### 이 대기열에 이미 적용되는 규율

- 3항의 zero-context 시험은 **5/5를 목표로 하지 않는다** — 복원 실패가 나오면
  그것이 handoff의 결함이고 고칠 대상이다. 통과율을 좋게 만들려고 시험을
  약화시키면 시험이 무의미해진다.
- 4~6항: **날짜는 근거가 아니다.** `SAFE_TO_REMOVE`는 근거 3항이 필요하고,
  0건이 정당한 답이다(2차 라운드 실측: worktree 0 · vault 0 · 파일 1). 선행
  결정을 재제안하지 않기 위해 `docs/WORKSPACE_CLEANUP_20260823.md`와
  `docs/WORKSPACE_CLEANUP_20260824.md`를 **먼저 읽는다**.
- 4~6항의 함정 3개(2차 라운드에서 실측된 것): worktree 삭제 안전성의 기준은
  병합이 아니라 **push**다 · **상호 참조는 참조가 아니다**(닫힌 고리는 둘 다
  후보) · **캐시라도 테스트가 읽으면 하중 자산**이다.
