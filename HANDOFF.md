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
state_code: D32C_APPLIED__READY_FOR_20_REPROJECTION_AND_V5   # D-32-C 수령·검증·수리 완료. 판정이 재해석을 **승인하되 `forall` 한정으로 좁혔고**, 적대 검증이 우리 구현의 과일반화(4종 전부 적용)를 적발해 수리했다. 계약 40건. **설계 차단 요인 없음** — 남은 것은 실행 절차뿐
next_action_code: REPROJECT_20__MANIFEST__FREEZE_V5   # §3의 0-b~0-e: 20건 전량 재투영(**20/20 변경이 정상**) → manifest에 measurement_contract·score_comparability → PRE_EXECUTION_FREEZE_AMENDMENT_V1로 V5 동결 → 채점 배선 V2 교체. **desugar → signature 순서를 배선에서 재확인**(불변성이 desugar에 의존한다). 코호트 dispatch는 그 뒤에도 별도 승인
stop_condition_codes:
  - NO_COHORT_WITHOUT_USER_APPROVAL      # §1·§3 — 실행은 별도 승인
  - NO_FROZEN_SURFACE_EDITS              # §4 — V1·V2 동결 표면 수정은 D-19 §12 외부 판정 사안
authority: experiments/2026-08-23_e2e_v1_c_o1_cohort/PREREGISTRATION_STAGE2_V4.md
# 코드별 authority 근거절 — 위 코드를 주장할 때는 아래 절을 인용하라:
#   state_code             ← PREREGISTRATION_STAGE2_V4.md AMENDMENT 2 (V1·V2 보존, V3=ABORTED_PRE_FREEZE)
#   next_action_code       ← PREREGISTRATION_STAGE2_V4.md A2.2 controls 행 (FOLIO 3 + PMB 3 선행)
#   NO_COHORT_WITHOUT_USER_APPROVAL ← CLAUDE.md "## 실행 승인" 절 (저장소 전역 운영 규칙 — 사전등록은 실행 허가가 아니다)
#   NO_FROZEN_SURFACE_EDITS         ← PREREGISTRATION_STAGE2_V4.md (D-19 §12; 개정은 D-24 §9 절차로만)
```

## 1. 현재 상태 한 줄

**설계 차단 요인이 하나로 좁혀졌다 — Q32-C 회신 1건.** 재료(기수 3·비례 1)와
권리는 해소됐고, D-30~D-32의 계약은 전부 구현·결박됐다. 남은 것은 `Q_RSTR_BODY`를
provenance가 아니라 **위치**로 정의해도 되는지의 확인이며(문면대로는 구현 불가 —
desugar 후 생성분과 원본이 바이트 동일), 그 회신 뒤 **20건 재투영 → manifest →
V5 동결**을 한 흐름으로 한다. **코호트 dispatch 누계 0건**이고 V5 동결 후에도
실행은 별도 승인 사안이다.

측정 계약의 현재 형태: 방언 8종(`forall/exists/and/or/not/implies/pred` +
`count`·`prop`) · 채점 `O1ScopeMatch` · 투영은 **`O1_SCOPE_PROJECTION_V2`**
(비-scope 내용을 opaque incidence로 붕괴, empty/nonempty와 순서 보존 incidence는
유지, 닫힌 profile로 미지 연산자 거부). **V1은 바이트 보존**돼 있고
`V1–V4 = V1 semantics` / `V5 onward = V2 semantics`를 선언해야 한다.

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
