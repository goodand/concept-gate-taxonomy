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
state_code: RULING_D29_RECEIVED_AWAITING_MATERIAL   # 방언 8종 설계 승인(count·prop) — 재료 0/3·0/1로 freeze BLOCKED
next_action_code: IMPLEMENT_COUNT_PROP_THEN_AWAIT_ROUND3   # D-29: count(eq|ge|le|gt|lt)·prop(most) constructor + MRS_COUNT_PROJECTION_V1 계약은 재료와 독립 구현 가능; Redwoods locator는 3차 조사 대기
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

**Stage 2 V2 — adapter control 2/3(해석 가능 조건 미달) → 본 코호트
미실행, Q25 판정 대기.** control 원인 분해가 상위 결함을 노출했다:
F1 라벨 span 미결정(derivable ≠ unique), F2 다중 토큰 join 규약 부재
(in-N FOLIO 4/5), **F3 PMB 15/15 — oracle이 사건 의미론 granularity라
template 준수 subject는 원리적으로 fail** (V1부터 존재, subject-통과
가능성 게이트 부재가 근본 원인). 기록: `experiments/…/CONTROLS_RUN_
20260823.md`, 상신: `docs/DESIGN_REQUEST_oracle_granularity.md`.
코호트 dispatch 0건 — 결과에 조건화된 것 없음.

## 2. 정본 지도 (읽는 순서)

| 알고 싶은 것 | 정본 |
|---|---|
| 최신 상태·패턴 원장 | `docs/H1A_PROBLEM_ANALYSIS.md` **마지막 절(§11)** — 규약상 항상 문서 끝이 최신 |
| 무엇이 동결됐고 무엇이 금지인가 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/PREREGISTRATION_STAGE2.md` (FROZEN) |
| fixture 20+3건의 commitment | 같은 폴더 `stage2_fixture_manifest.json` (원문 0바이트 — 해시·locator만) |
| 선별이 조작 불가능한 이유 | 같은 폴더 `freeze_stage2.py` (seed·층 술어·ANA 제외 전부 코드가 정본) |
| 외부 판정 사슬 | `docs/DESIGN_DECISION_*` — D-19(실험 구조)·D-20(commitment)·D-21(oracle 교체)·D-22(PMB 부분자격+stratum floor)·D-23(FOLIO+FOL codec). 전부 verbatim+sha256, 말미에 수신 검증 기록 |
| adapter 자격(코드 결박) | `experiments/2026-08-23_{o1,sbn,fol}_adapter_qualification/` — 각 test_protocol이 코드 해시를 라이브와 대조: **adapter·비교층을 고치면 자격이 자동 실효**된다 |
| 적대 검증 결과 | `docs/ADVERSARIAL_VALIDATION_20260823.md` |
| 이 handoff가 실제로 복원 가능한가 | `docs/HANDOFF_EVALUATION_20260823.md` — zero-context 평가기 실측(3/3 accepted) + 발견된 결함 2건과 수리 + 남은 한계 4건 |
| 실행 기제 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/_stage2_{cohort,run,score,eval_profile,canonical_core}.py` + `conceptgate/cg_{sbn,fol}_adapter.py`, `cg_fixture_resolver.py` |

## 3. 다음 실행 절차 (사용자 승인 후 — 이 문서의 유일한 고유 내용)

전제: 게이트 `python3 scripts/run_gates.py` = 13 passed / 0 failed / 1
blocked(owlready2 — 무관) 확인.

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
