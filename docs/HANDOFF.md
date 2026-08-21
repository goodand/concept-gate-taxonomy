# HANDOFF — ConceptGate 세션 인수인계 (H 계열: source authority)

- 갱신: **2026-08-22** — ✅ **40 TRIAL 실행·채점 완료. 다시 돌리지 마라.**

  ```
  PROHIBITION_KEPT      selection 0 / deferral 20 / invalid 0
  PROHIBITION_REMOVED   selection 2 / deferral 18 / invalid 0
  ```
  40/40 기록, 전송 실패 0, 완주 replicate 20/20, Stage A 양 arm 통과.
  산출물: `trials_raw_typed_scope.json` / `trials_typed_scope.json` /
  `h1a_cohort_score_typed_scope.json`. 실행 기록은 실험 폴더
  `OPERATIONS_LOG.md` 2026-08-22 절, 보고는
  `PREREGISTRATION_TYPED_SCOPE_COHORT.md` **§9**가 정본이다.

  ⚠️ **재실행 금지.** `write_raw()`·`freeze()`·`_h1a_score.main()` 셋 다
  fail-closed로 거부하지만, **그 거부를 지워서 통과시키지 마라** — 이 폴더는
  이미 빌더 재실행으로 동결 아티팩트를 파괴한 이력이 있다. 재실행이 필요하면
  그것은 **자기 spec을 가진 새 코호트**다(네 번째 정체).

  **결과 해석의 상한 — 이걸 모르고 인용하면 틀린다**:
  - **ceiling 방향은 `unknown`.** QF-SELECT는 5/5 통과했으나 QF-DEFER는
    `material_unavailable`(미시행). 그래서 2/20이라는 작은 값을 **"ceiling
    포화가 아니다"로 읽을 수 없다.** 패킷이 금지 여부와 무관하게 deferral을
    유도할 가능성은 배제되지 않았다. 현행 규범은 사전등록 §5f 표.
  - `material_unavailable` ≠ `failed`(Q14.2). 진단을 실패로 서술하지 마라.
  - K=1 서술적·패킷 조건부만. D-H1a-7이 인과 귀속 금지, L8이 축별 주장 금지,
    L3이 code측 수사적 우위를 권위로 읽는 것 금지.

  **보존 코호트와의 병기 — D-H1a-18 Q18.2=c가 조건부로 허용한 형식만 쓴다.**
  판정문이 제시한 문구를 그대로 쓰고, 운영 세션이 다시 저작하지 않는다:

  > "이전 비식별 표면에서는 양 arm 모두 0/20이었고, 수선된 별도 표면에서는 KEPT 0/20, REMOVED 2/20이 관측됐다. 두 코호트는 병합하지 않으며, 표면 차이가 복수이므로 이 변화 자체를 특정 수정의 효과로 귀속하지 않는다."

  ⚠️ 이 배너의 이전 판(2026-08-22 오전)은 "재설계가 그것을 겨눴으며 REMOVED가
  0→2로 움직였다"라고 썼다. **그 문장은 철회됐다** — Q18.2 조건 3
  (`causal_redesign_attribution: forbidden`)에 걸린다. 표현이 약해도 변화를
  재설계의 증거로 쓰는 것은 같은 금지 대상이다. 조건 5에 따라 두 코호트의
  지위는 다르게 유지한다: 08-03은 `completed_nonidentifying`, 08-22는
  repaired-surface observation.

  **✅ H1a는 종결됐다 (D-H1a-18, 2026-08-22).** Q18=F = A(서술적 종결) +
  C(상위 목적 전환). 추가 주 trial **0건**, 3차 코호트는
  `deferred_as_separate_future_experiment`, `QF-DEFER`는 영구
  `material_unavailable`로 닫고 천장 방향은 `unknown`으로 보존한다
  (**`unknown`을 `false`로 바꾸지 마라** — "ceiling이 없었다"가 아니라
  "ceiling 가능성은 독립적으로 진단되지 않았다"다).

  **다음 프로그램**: 재사용 가능한 feedback kernel 추출 → LLM 출력 기반 인과
  추론 아키텍처. 판정문 `next_program.priority`가 그 순서를 고정한다.

  ⚠️ **실행 로그를 읽을 때의 함정 하나.** 08-03 기록이 "`agents_done: 0` /
  수십 ms = 아무것도 모델에 도달하지 않음"이라고 경고하는데, 08-22에는
  **75ms / 0 토큰짜리 재생이 하나 더 있다.** 그건 trial_id 매핑을 복구하기
  위한 **의도된 캐시 히트**이고 실제 실행은 484.7s / 157k 토큰이다. 두 수치가
  provenance에 따로 있다 — 재생 수치만 보고 "실행 안 됐다"로 읽지 마라.

  **동결된 코호트 정체**(세 번째 정체다 — 이유는 `_h1a_cohort.TYPED_SCOPE_COHORT`
  주석):
  ```
  cohort_id   h1a-typed-scope-20260817     trial  40 (arm당 20)
  seed        H1A-typed-scope-fixed-order-v1
  trial_id    H1AT-{arm}-{replicate:02d}
  fixture     fixture_source_authority.json (불변, 보존 코호트와 sha256 동일)
  transport   schema_forced_structured_output   trial_model  claude-opus-5
  ```
  `H1AR`(수선 코호트)는 **실행된 적이 없다** — 독립 리뷰 3명 전원
  FREEZE_BLOCKED. `H1A`는 비식별 판정된 보존 40건이다. 둘 다 재사용하면
  안 된다. `H1AT`는 `H1A`와 세 글자를 공유하지만 이 폴더의 검사는 하이픈까지
  매칭하므로 안전하고, **그 사실이 테스트로 고정돼 있다** — 하이픈 없는 prefix
  검사를 새로 쓰면 이 trial들이 조용히 보존 코호트로 분류된다.

  **`INDEPENDENT_SEMANTIC_REVIEW_PASSED = True`로 전환됐다**(커밋 `73b6682`,
  리뷰 보고서와 같은 커밋 — 조건 11 요구). 무엇이 기록됐고 무엇이 **안**
  됐는지는 `_h1a_policy.py` 상수 위 주석이 정본이다. 요약: 리뷰가 통과했다는
  기록이지 **정본이 모든 target-critical family를 덮는다는 기록이 아니다.**

  ⚠️ **그 플래그의 보호 장치가 이전됐다.** 예전 테스트는 "플래그가 False임"을
  단언하며 *"이 테스트를 통과시키려고 뒤집지 마라"*라고 적혀 있었다. 정당한
  전환을 견딜 수 없어 **더 강한 형태로 옮겼다** —
  `test_the_review_flag_is_only_true_alongside_a_recorded_passing_review`:
  플래그가 True면 리뷰 보고서가 실재하고 pass를 기록해야 한다. 원래 것은
  전환을 *지연*시켰을 뿐이지만 이건 **아티팩트에 묶는다.** 지우지 마라.

  **판정 2건 수령·적용**: **D-H1a-16**(Q16=A 정본 확장) → **D-H1a-17**(Q17=B)이
  그 **적용 범위를 한정**했다(무효화 아님).
  `TargetCritical ⇒ CanonicalExpectedState`를
  `CanonicalAuditCritical ⇒ CanonicalExpectedState`로 좁혔다.
  `target-critical` 단일 enum이 두 주장을 나르고 있던 것을
  `CAUSAL_SEMANTIC_CRITICAL`(6개) / `CANONICAL_AUDIT_CRITICAL`(**현재 0개**)로
  분리했고, 각 family가 **어느 경로로** 확정됐는지 `CERTIFICATION_PATH`에
  기록한다. **0개인 것은 우연적이다** — 독립 경로가 사라지면 다시 채워야 하고,
  `test_h1a_criticality.py`가 그 반사실을 실측한다.

  **차단하지 않는 미결 3건**(D-H1a-17이 명시적으로 non-blocking 분류):
  Q16.1 `external_source_retrieval` 별도 claim, Q17.2 b′ typed-reference
  canonicalization, Q17.1 kernel 추출(제품 자산화).

  **다음 독립 리뷰에 대한 경고 — 반복 실증됐다**: 이번에 4축 적대 검토가
  하네스 결함을 통째로 놓쳤고, 원인은 **검토 범위를 제작자가 설계한 것**이다.
  구조적 회귀 finding도 4축이 아니라 lead 재실측에서 나왔다. 그리고 하네스
  결함은 4축도 재실측도 아니라 **사용자 지시**로 나왔다.
  `_h1a_review_protocol.py`가 범위 선언·blinding·자격 사전 채점을 코드로
  강제하지만, **범위 설계 자체는 여전히 제작자 손에 있다.** 상세는
  `docs/H1A_ISSUE_REGISTER.md` §I.5 메타 항목.

  게이트: H1a **320 passed / 1 skipped**, 루트 **8 passed / 0 failed / 1
  blocked**(fastmcp 부재 = 판정 보류). owlready2 red는 2026-08-16에 해소됐다
  (§10.1 승인안 적용). 상세는 `OPERATIONS_LOG.md` §12~§16.
- 갱신: **2026-08-16(2)** — **D-H1a-14/15 판정 도착·적용 + QF-SELECT 재실행.**
  판정문: `DESIGN_DECISION_H1a_qualification_gate_scope.md`. **Q14=E**(gate
  재설계) / **Q15=G**(QF-SELECT·QF-DEFER **둘 다 non-blocking capability
  diagnostic**). **freeze 권한이 식별 계약으로 분리**됐다 — qualification은
  더 이상 아무것도 막지 않고, `cohort_freeze`는
  `{determined_by: identification_contract}`로 소유자만 지목한다.
  QF-DEFER 미시행은 **L9로 정식 등록**(§5e). 새 거버넌스 규칙:
  *freeze_blocker ↔ diagnostic 이동은 estimand/governance 변경이며 외부
  판정 전에 실행 금지.*
  **별건 — 하네스 결함 발견·수정**: 정본 하네스(`_h1a_cohort.py`)와 대조한
  결과 2026-08-15 QF-SELECT 5건이 **스키마 미강제 + 다른 모델**(정의 파일에
  `model:` 없어 세션 모델 상속)로 실행됐음이 드러나, 코호트와 동일 경로
  (Workflow schema 강제 + `claude-opus-5`)로 **재실행**했다(결과 동일 5/5).
  기존 5건은 `h1a_qualification_raw_historical_20260815.json`으로 보존.
  하네스에 `protocol`·`trial_subject_surface`·`decision_schema_sha256` 배선,
  원시 파일이 **자기 provenance를 선언**하도록 요구하는 가드 추가, drift
  가드를 구조적 staleness까지 잡도록 강화. 게이트 H1a 237 passed/1 skipped.
  **다음 세션이 할 일**: Q13.5/13.6(다음 독립 리뷰 자체의 절차) → **독립
  리뷰 전면 재실행**(`INDEPENDENT_SEMANTIC_REVIEW_PASSED` 여전히 `False`)
  → 통과해야 `repaired_cohort_trials` 40건.
  ⚠️ **그 독립 리뷰의 범위는 제작자가 설계하지 마라** — 이번에 4축 적대
  검토가 하네스 결함을 통째로 놓쳤고, 범위를 제작자가 잡았던 것이 원인이다
  (`H1A_ISSUE_REGISTER.md` §I.5 메타 항목).
- 갱신: **2026-08-16** — ⚠️ **아래 2026-08-15(2)의 QF-DEFER 강등은 철회됐다.**
  `adversarial-review` 4축 + lead 재실측에서 blocker 4건으로 **채택 불가**
  (`docs/feedback/h1a_qf_defer_amendment_review_20260816.md`). 결정적
  finding: **Q14 요청서 자신이 그 조치(선택지 D)에 "새 판정 필요"라고
  주석해뒀는데 새 판정 없이 실행**했다. 그 외 — 자기가 명시한 규율을
  Q15에만 적용한 선택적 rigor, `M_allowed` 인용의 non-sequitur, **F6이
  폐기시킨 "해석 조건" 형태로의 구조적 회귀**(4축이 못 찾고 lead 재실측에서
  나옴). **현재 상태**: 코드·문서 Q13.3 원안 복원 → `cohort_freeze:
  blocked`(QF-SELECT 5/5 통과, QF-DEFER **미시행** — 재료 부재).
  **L9 등록 취소**(재료 부재는 한계가 아니라 미해소 blocker). Q14를
  **Q15(QF-SELECT 대칭 적용)와 함께** 재상신:
  `correspondence/DESIGN_REQUEST_H1a_qualification_gate_scope.md` —
  Q14.2(미시행/실패 구분 승인), Q14.3(qualification의 렌더 arm) 포함.
  부수 수리: 새 가드 2개를 `test_guard_negative_coverage.py` AST 스캔
  표면으로 이동(D-6 — 기제화한 규율이 수동으로 회귀해 있었다),
  `_git_head()` 중복 제거(D-7). 게이트 H1a 217 passed/1 skipped.
  **다음 세션이 할 일**: Q14/Q15 판정 대기 → 도착 후 gate 완주 →
  Q13.5/13.6 → 독립 리뷰 전면 재실행 → `repaired_cohort_trials` 40건.
  **판정 없이 gate 요건을 완화하지 마라** — 이번에 그렇게 했다가 철회했다.
- 갱신: **2026-08-15(3)** — **QF-SELECT 5-trial 실행 + `_h1a_qualification.py`
  실전 배선 완료.** 신규 `_h1a_qualification_run.py`
  (`_h1a_cohort.py`/`_h1a_score.py`가 confirmatory cohort에 대해 하는
  build/freeze·score/persist 역할 분리를 qualification에 적용 — fixture
  →prompt 렌더는 confirmatory와 동일 파이프라인 재사용, `build_cohort()`/
  `assert_freezable()`는 호출 안 함, 그건 `INDEPENDENT_SEMANTIC_REVIEW_PASSED`
  게이트가 있는 40-trial 전용). `h1a-decider`로 5회 독립 실행 — **5/5
  `select_type`/`structural_composition`**(만장일치, rationale 전부
  상이 — 독립 표본). 스코어: `cohort_freeze: allowed`,
  `QF-DEFER.status: material_unavailable`(L9, freeze는 안 막음). Arm은
  `PROHIBITION_REMOVED`(D-H1a-13 미명시, 운영 결정 — 근거는 새 모듈
  docstring). 산출물 `h1a_qualification_manifest.json`/`_raw.json`/
  `_score.json`, F9식 덮어쓰기 거부 재실행으로 실측 확인. 신규 테스트
  8건, 게이트 H1a 213 passed/1 skipped(회귀 없음), E2.4 118 불변, core
  pytest 기존 owlready2 결함 그대로. 상세는 `OPERATIONS_LOG.md`
  "2026-08-15" §8. **다음 세션이 할 일**: Q13.5/13.6(다음 독립 리뷰
  자체의 절차) → 독립 리뷰 전면 재실행(`INDEPENDENT_SEMANTIC_REVIEW_PASSED`
  여전히 `False`) → 통과해야 `repaired_cohort_trials` 40건 착수. Q15
  (QF-SELECT 대칭 강등 여부)는 여전히 미결.
- 갱신: **2026-08-15(2)** — **QF-DEFER를 non-blocking diagnostic으로
  강등**(amendment, D-H1a-1~13류 외부 판정 채널 아님 — 사용자가 공유한
  설계 상담 + "상위 목적에 따라서 결정해라" 직접 지시에 근거해 처리,
  `D-H1a-14` 번호 부여 안 함). `_h1a_qualification.py::score_qualification()`이
  이제 `cohort_freeze`를 **QF-SELECT 하나에만** 의존시킨다 — QF-DEFER는
  재료 부재/진단 실패/진단 통과 세 상태로 기록되지만 어느 것도 freeze를
  막지 않는다. QF-DEFER 재료 부재는 **영구 등록 한계 L9**
  (`PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5e)로 전환 — 더 이상 gate
  완주를 막는 미결 질문이 아니다. QF-SELECT의 hard-gate 지위는 불변이며,
  대칭 강등 여부는 **Q15로 미결 등록**(§5d, 상신 안 함). 근거 인용:
  `README.md` §2, `DESIGN_DECISION_H1a_residual_prohibition.md` §3
  (`M_allowed = ¬Q1 ∧ ¬Q7`). 테스트 갱신·신규 3건, 게이트 H1a
  205 passed/1 skipped(회귀 없음), E2.4 118 불변, core pytest 기존
  owlready2 결함 1건 그대로. 상세는 `OPERATIONS_LOG.md` "2026-08-15" §7.
  **다음 세션이 할 일은 아래 2026-08-15(1) 항목과 동일** —
  `_h1a_score.py`에 `_h1a_qualification.py` 실행 경로 배선은 여전히
  미완.
- 갱신: **2026-08-15(1)** — D-H1a-13 **부분 적용**. Q13(dangling 문장 삭제),
  Q13.1(`source_order`→`evidence_item_presentation_order` 개명),
  Q13.2(evidence-scope 문구 분리), Q13.4(L8 등록 + 옛 M4 ceiling
  WITHDRAWN 표시) **완료**. Q13.3(qualification gate)은 **결정론적
  채점기만 완료**(`_h1a_qualification.py`, 커밋 `85bff26`) — QF-SELECT/
  QF-DEFER **fixture 자체는 아직 없다**(합성 불가, 실제 저장소 근거
  필요). 같은 세션에 F10(정책 모듈 이중 로드 버그)·F9(채점기 fail-close
  누락)도 수정. 게이트: H1a 186 passed/1 skipped, E2.4 118 불변. 커밋
  8개 전부 `origin/codex/h1-source-authority`에 푸시 완료. 상세는
  `OPERATIONS_LOG.md` "2026-08-15" 절. **다음 세션이 할 일**: QF-SELECT/
  QF-DEFER fixture 설계·검증(`PREREGISTRATION_TYPED_SCOPE_COHORT.md`
  §5a) → 채점기 배선 → Q13.5/13.6(독립 리뷰 자체의 절차) → 독립 리뷰
  전면 재실행(`INDEPENDENT_SEMANTIC_REVIEW_PASSED` 여전히 `False`) →
  `repaired_cohort_trials` 40건. `freeze_status: FREEZE_BLOCKED` 유지.
- 갱신: **2026-08-08** — 이 문서의 아래 §10.4 10항목 목록은 **낡았다.**
  2026-08-06 `concept-gate-h1a-scope-wt`(브랜치 `codex/h1a-typed-scope-split`)
  세션이 §16의 12조건 중 **10개를 구현**했고(174 passed, 가드 게이트 10
  passed), 그 브랜치가 이 브랜치로 병합됐다(cherry-pick/merge, 손복사 아님).
  **`assert_9`는 이제 golden contract로 닫혔다** — 위 KNOWN_UNPROVEN 문장은
  낡았다. 상세 근거는 `OPERATIONS_LOG.md` "2026-08-06 — D-H1a-12 §16 구현"
  절이 정본이며, 아래 10항목 목록은 그 시점 이전 계획으로 이력 보존한다.
  **단, 독립 리뷰 5차가 새 BLOCKER를 찾았다** — 판정문 §4가 처방한 문장
  자체가 REMOVED arm에서 dangling reference였다(제작 세션이 직접 실측
  확인). 이게 **Q13 상신 → D-H1a-13 판정**(2026-08-06 수령, 아래 표 참고)으로
  이어졌다. D-H1a-13은 **기존 독립 리뷰 결과를 전부 무효화**했다
  (`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`). §4·§6·§7 개정과 전체
  리뷰 재실행이 **아직 미구현**(`repaired_cohort_trials: 0`,
  `freeze_status: FREEZE_BLOCKED` 유지) — 이게 실제 "다음 세션이 할 일"이다.
  전문: `DESIGN_DECISION_H1a_prescribed_sentence_defects.md`(D-H1a-13).
- 갱신: **2026-08-05** — Q11·Q12 판정(D-H1a-11, D-H1a-12) 모두 도착·반입.
  Q12=F(typed-scope split)로 H1a는 계속되나 **§16의 freeze 해제 조건 12개는
  아직 미구현**. 가드 음성-테스트 커버리지 게이트(`test_guard_negative_coverage.py`,
  repo root)를 신설하고 이 브랜치에서 실행해 `assert_9_default_permission_is_byte_identical_across_arms`
  를 독립 재발견(`KNOWN_UNPROVEN`에 등재, Q12.4의 golden contract 구현 대기).
  worktree `concept-gate-owl-wt`(브랜치 `codex/entailed-is-a-contract`)에서
  먼저 작업된 뒤 `git cherry-pick`으로 이 브랜치에 전파됐다(손복사 아님).
  전체 이슈 목록은 그 worktree의
  `docs/feedback/session_retrospective_20260805_search_trigger_and_h1a.md`
  (H1a 외 OWL 실험·vault 검색 하네스도 다루므로 이 브랜치에는 미전파).
  이전 배너: 2026-08-03(2) Q10 판정 도착·반입.
- 대상: **컨텍스트 없이 이어받는 새 세션**. 이 문서만 읽고 작업을 재개할 수 있게 쓴다.
- 이 문서는 worktree `concept-gate-h1-wt`(브랜치
  `codex/h1-source-authority`)의 최신 상태를 기록한다.
- **E2.2~E2.4 체인의 상태는 여기가 아니라** `../concept-gate-e2.2-wt/docs/HANDOFF.md`.
- **파일을 어디서 찾을지 모르겠으면** 먼저 [`WORKSPACE_NAVIGATION.md`](WORKSPACE_NAVIGATION.md)를
  읽어라 — 저장소/worktree 구조, 문서 종류별 분류 체계, 탐색 명령 레시피가 있다.
- **새 실험을 설계하기 전에** 메인 저장소 체크아웃의
  `docs/EXPERIMENT_METHODOLOGY.md`를 읽어라(2026-08-01 병합으로 이 worktree에도 있다)
  (7개 규칙: 동결/운영로그 분리, 폴더 규약, provenance 계약, worktree 격리,
  비-git 감사본, 교훈 승격, 독립 재현 검증).

---

## 1. 지금 상태 한 문단 (TL;DR)

M1(relation.is_a certificate) 검증 실험 라인을 진행 중이다.
E2.2.1(NO_GO) → E2.2.2(GO) → E2.2.3(OFAT, A_ONLY 단독 충분) →
E2.3(A_ONLY 일반화, screened PASS) → **E2.4(종료)** → **H1a(진행 중 —
최초 코호트 실행·비식별 판정, 수선 대기)**.

> ## 📍 이 worktree가 H 계열의 정본이다 (2026-08-01 분리)
>
> **worktree** `concept-gate-h1-wt` / **브랜치** `codex/h1-source-authority`.
> H1a와 이후 H1b·H2… 가 여기서 산다.
>
> **왜 분리했나**: 2026-07-29 운영 지시가 H1a를 "**별도**
> source_authority_unresolved 실험"이라고 명시했는데 E2.x worktree에 얹혀
> 있었다. `EXPERIMENT_METHODOLOGY.md` §4 위반이라 분리했다 — "새 실험 계열을
> 시작할 때는 새 worktree를 만들지, 기존 worktree에 무관한 실험을 얹지 않는다."
>
> ⚠️ `../concept-gate-e2.2-wt`에도 H1a 파일이 남아 있다 — 분리 이전 이력을
> 공유하기 때문이다. **저쪽은 사본이고 여기가 정본이다.** 중복 제거는 미결.
>
> ## 🔴 2026-08-03(2) — Q10 판정 도착(D-H1a-10). 최초 코호트는 **비식별**로 확정
>
> **Q10=E.** 40 trial은 **무효가 아니지만 확증에도 쓸 수 없다.** 판정문:
> `experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_residual_prohibition.md`
>
> | 항목 | 판정 |
> |---|---|
> | 최초 40 trial | `completed_nonidentifying` / `exploratory_diagnostic`. **새 코호트와 병합 금지, 기존 arm 재사용 금지** |
> | 결론 표기 | `target_effect: insufficient_evidence` + `current_bundle_contrast: observed_zero`. **`null_effect` 아님** |
> | 수선 | **R1** Q7 목록에서 표적 축 4개만 제거 → **R2 양 arm 재실행** |
> | 가드 | **Q10.2** 어휘 tripwire → 구조화 정책 계약(LLM 검사기는 보조만) |
> | 한계 | **Q10.3 L4 신규 등록.** `L3_subsumes_L4: false` |
>
> **형식 근거**: 표적 경로는 `M_allowed = ¬Q1 ∧ ¬Q7_target`. 현재는 KEPT·REMOVED
> 둘 다 `0`(`ProofCurrentNoContrast: True`), 수선 후 REMOVED만 `1`
> (`ProofRepairCreatesContrast: True`). **단 `select_type`이 논리적으로
> 불가능했던 건 아니다** — `ev3`의 반박절을 *실질 논거*로 읽는 경로는 열려
> 있었고, 40/40이 그것을 택하지 않았을 뿐이다.
>
> **🚫 금지 문구**: "금지를 제거해도 행동은 변하지 않았다."
> **✅ 허용 문구**와 산출물 해시는 `COHORT_STATUS_20260803_nonidentifying.md`.
>
> ### 진행 상황 — Q10.2 완료, Q11 판정 대기 (2026-08-03(3))
>
> | 게이트 | 상태 |
> |---|---|
> | **Q10.2** 가드 상향 | ✅ **완료.** 신규 `_h1a_policy.py` — 타입 정책 스키마 + 결정론적 렌더러 + 구조 단언 6항 + 연역 검사. `test_h1a_policy.py` **28 passed** |
> | **R1** 내용(표적 축 4개 제거) | ✅ 구현·테스트 완료 |
> | **R1** 배선(템플릿 교체) | ⬜ **의도적 보류** — Q11이 REMOVED 블록의 불릿 개수를 결정. 지금 바꾸면 재동결이 두 번 든다 |
> | **Q11** | 🔶 **상신됨**(인용 대조 9/9) — `correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md` |
> | 신규 사전등록 / 독립 리뷰 / R2 | ⬜ Q11 후 |
>
> **핵심 검증**: `test_the_actual_nonidentifying_cohort_prompt_is_rejected`가
> `cohort_prompts.json`의 **실제 동결 바이트**(40 trial에 쓰인 것)를 새 가드에
> 넣어 거부를 요구하고, 옆 테스트가 **옛 가드는 같은 바이트를 통과**시킴을
> 고정한다. "두 가드가 다른 명제를 주장한다"가 실물로 증명됐다.
>
> **Fail-closed**: `REMOVED_ALLOWED_RENDERING = None`인 동안
> `assert_freezable()`이 동결을 거부한다 — 판정 없이 프롬프트가 trial에 도달할
> 수 없다.
>
> ⚠️ **[DESIGN] Q11 상신 3건 — 판정 전 진행 금지**
>
> | # | 질문 |
> |---|---|
> | **Q11** | `removed: allowed`가 **명시적 허용 문장**인가 **침묵**인가. 침묵이면 REMOVED에 금지도 허용도 없고(거짓 null 위험), 명시하면 없던 문장이 생긴다(요구 특성 위험) |
> | **Q11.1** | **R1이 KEPT 금지도 약화시킨다.** 수선 전 KEPT는 Q1(산문)+Q7(의사결정 규칙) 두 곳에서 금지받았고, R1은 그중 하나를 없앤다. 판정문에 없던 질문이라 새로 제기 |
> | **Q11.2** | `carrier` 매핑을 사전등록에 동결하는가 |
>
> **운영 세션이 임의로 정하지 않는다**(P7). 셋 다 조작 표면의 크기·형태를 바꾼다.
>
> - 요청서: `correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md`
> - 상세: [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md) §H.4~H.7
> - 산출물: `cohort_prompts.json`(동결) / `trials_raw.json` /
>   `trials.json` / `h1a_cohort_score.json` — **11종 sha256이
>   `COHORT_STATUS_20260803_nonidentifying.md` §3에 동결됨**
> - **로그**: `OPERATIONS_LOG.md`(운영 로그, 방법론 §1·§2) /
>   `h1a_attempt_log.json`(**P4 요구** 시도 이력 + 독립 교차검증 해시) /
>   비-git 감사본 `../../h1a-execution-audit/`(방법론 §5, 선례
>   `e2.1-execution-audit/`) — 하네스 `journal.jsonl`과 workflow 반환값 원본을
>   보존했다. 원 위치(`/private/tmp`, `~/.claude`)는 휘발성이다
> - 신규 harness: `_h1a_cohort.py`(동결), `_h1a_score.py`(**출력을 읽기 전에
>   작성** — 결과를 본 뒤 채점 규칙을 만들지 않기 위해)
> - **커밋·푸시 안 함.** 40 trial 산출물 + Q10 반입분 전부 미커밋 상태로
>   사용자 승인 대기. 커밋 시 방법론 §1 순서 준수 — manifest freeze / results /
>   ops-docs를 **각각 독립 커밋**으로.
>
> ---
>
> **(이하 2026-08-02 시점 기록 — 위 실행 이전 상태)**
> **현재 상태: 차단됨(Q9 판정 대기). 실행된 trial 0건.**
> 설계 판정 4회(D-H1a-1~7 / Q1·Q2 / Q3·Q4 / Q5~Q8), 독립 리뷰 3회.
> **Q5~Q8 전부 적용 완료(2026-08-02), 3차 독립 리뷰 통과(blocker 0)** —
> 아래는 이력.
> - ✅ **Q5=B** 조작 span 2문장으로 축소 완료. 3번째 문장(`그 판정은 이미
>   끝났고 너의 범위가 아니다.`) 제거, E2.4 선행사 복원 안 함(Q5.1 금지)
> - ✅ **Q6=A** 모델 대면 type 앵커 제거 완료 — `concept_feature_pair`로
>   교체. 20건 앵커 진단(`_h1a_diag*` 4파일)은 `superseded/`로 이동, 구조적
>   no-anchor 가드(`assert_no_model_facing_type_anchor`)로 대체, 주입
>   뮤테이션 테스트로 실패 확인
> - ✅ **Q7=E** warrant 기반 select_type/defer 규칙을 `h1a_prompt_template.md`에
>   verbatim 삽입 완료
> - ✅ **Q8=B** `ev2` 제거, fixture 진짜 1-vs-1, `builder_metadata` 정직화
>   완료
>
> 프롬프트 template은 이제 판정문이 아니라 **`h1a_prompt_template.md`**(신규,
> 평면)에서 로드한다 — Q5·Q6.1·Q7이 셋으로 나눠 수정해야 했기 때문이다.
> `_h1a_contract.py`의 `DESIGN_DECISION_PATH`가 이 파일을 가리킨다.
>
> `python3 scripts/run_gates.py` 그린 확인함(H1a 106 passed/1 skipped,
> E2.4 118 불변).
>
> **3차 독립 리뷰(2026-08-02, 별도 에이전트·제작자 결론 미고지) 완료**:
> blocker 0, major 2 + minor 1 즉시 수정·재테스트(전부 회귀 테스트로 고정).
> 잔여 1건은 코드 결함이 아니라 fixture 내용 설계 질문이라
> **Q9로 상신**(`correspondence/DESIGN_REQUEST_H1a_evidence_symmetry.md`).
>
> **Q9 반입·등록 완료(2026-08-03).**
> `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md` → 저장소로 byte-identical
> 반입(`experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_evidence_symmetry.md`,
> `diff` 무출력으로 확인), `PREREGISTRATION.md` §0.1(신설)에 L1·L2·L3를
> 같은 자리에 등록(L3는 Q9.1 원문 그대로, 의역 없음), `H1A_ISSUE_REGISTER.md`
> Q9 항목을 "✅ 적용 완료"로 갱신. `python3 -m pytest -q
> experiments/2026-07-29_h1a_source_authority_unresolved/` 재확인함(106
> passed/1 skipped — 문서만 바뀌었으므로 회귀 없음).
>
> 판정: **Q9=A** — fixture 무변경(byte-faithful 1-vs-1 유지), 비대칭은
> `PREREGISTRATION.md`에 **L3**로 선언 완료. Q9.2는 Q8.1(enum 밖 노출 금지)
> 구속력 유지를 재확인.
>
> **다음 세션이 할 일**:
> 1. ⬜ **4차 독립 리뷰가 필요한지 사람이 최종 판단.** 표면(prompt/payload/
>    fixture)은 바뀌지 않고 사전등록 문서에 한계 선언만 추가됐으므로 생략
>    가능하다는 것이 운영 세션 의견이나, 3차 리뷰가 지적한 사안 자체에 대한
>    판정이므로 최종 판단은 사람 몫으로 남긴다.
> 2. 위 결정 후 **동결 → 본 코호트 40 trial**로 넘어갈 수 있다(trial 실행
>    자체는 별도 승인 대상).
> 3. 이번 세션은 커밋·푸시를 하지 않았다 — 변경된 파일 3개(`PREREGISTRATION.md`,
>    `H1A_ISSUE_REGISTER.md`, 신규 `DESIGN_DECISION_H1a_evidence_symmetry.md`)를
>    `git diff`/`git status`로 검토 후 커밋 여부를 사용자가 정한다.
>
> 전체 목록·근거·검증 강도: [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md)
> 리뷰 전문: [`feedback/h1a_fixture_review_20260730.md`](feedback/h1a_fixture_review_20260730.md)


## 📚 새 세션이 읽어야 할 것 — 전수 목록

**이 표가 진입점이다.** 아래 밖의 문서는 읽지 않아도 작업을 재개할 수 있다.

### 먼저 (순서대로)

| # | 문서 | 왜 |
|---|---|---|
| 1 | 이 파일 | 지금 상태·다음 행동 |
| 2 | [`WORKSPACE_NAVIGATION.md`](WORKSPACE_NAVIGATION.md) | **함정 4개**와 탐색 절차. §0 함정 4(검색의 침묵)는 이 세션에 두 번 걸린 것 |
| 3 | [`EXPERIMENT_METHODOLOGY.md`](EXPERIMENT_METHODOLOGY.md) | 방법론 7규칙. §4 worktree 격리가 이 worktree가 존재하는 이유 |

### 이슈 전체 — **두 문서를 다 읽어야 한다**

| 문서 | 단면 |
|---|---|
| [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md) | **시간순** 기록(§A~§F) |
| [`H1A_PROBLEM_ANALYSIS.md`](H1A_PROBLEM_ANALYSIS.md) | **패턴별** 단면 — 반복 형태 7종, 해결 18/미해결 8 |

같은 사건의 다른 자름이다. 한쪽만 읽으면 "무엇이 반복되는가"(전자) 또는
"언제 무엇이 있었나"(후자)를 놓친다.

### 외부 설계 판정 8건 — **전부 구속력 유지.**

| 파일 | 범위 |
|---|---|
| `DESIGN_DECISION.md` | D-H1a-1~7 — 2-arm 서술적 실험 확정 |
| `DESIGN_DECISION_H1a_manipulation_scope.md` | Q1=B 조작 재정의 / Q2=B 앵커 진단 |
| `DESIGN_DECISION_H1a_prompt_surface.md` | Q3=B 전용 프롬프트 / Q4 승인 |
| `DESIGN_DECISION_H1a_review_blockers.md` | Q5=B/Q6=A/Q7=E/Q8=B — **2026-08-02 전부 적용 완료** |
| `experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_evidence_symmetry.md` | Q9=A(fixture 무변경, L3 한계 선언) / Q9.2(Q8.1 유지) — **2026-08-03 반입·적용 완료**(`notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`에서 byte-identical 복사, 원본은 `notes/`에 보존). `PREREGISTRATION.md` §0.1에 L3 등록 완료 |
| `DESIGN_DECISION_H1a_residual_prohibition.md` | D-H1a-10, Q10=E(코호트 비식별 보존) / Q10.1~Q10.3 — **2026-08-03 반입·적용 완료** |
| `DESIGN_DECISION_H1a_allowed_rendering.md` | D-H1a-11, Q11=D(공통 기본허용 규칙, 축별 permission 없음) / Q11.1=A / Q11.2=A — **적용 완료.** 독립 리뷰 3명 전원 `FREEZE_BLOCKED`(공허한 `assert_5`, 코호트 파괴 경로, 정책 계층 미배선 — 전부 수정 완료) |
| [`DESIGN_DECISION_H1a_identification_validity.md`](../experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_identification_validity.md) | D-H1a-12(2026-08-05), Q12=F(`outside_domain_knowledge`/`source_meta_reasoning` typed-scope split) / Q12.1~Q12.4 + M4·M7·M8 — **2026-08-06 §16 조건 10/12 구현**(`OPERATIONS_LOG.md`), 독립 리뷰가 새 BLOCKER 발견 → 아래 D-H1a-13으로 이어짐. 요청서: `correspondence/DESIGN_REQUEST_H1a_identification_validity.md` |
| [`DESIGN_DECISION_H1a_prescribed_sentence_defects.md`](../experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_prescribed_sentence_defects.md) | D-H1a-13(2026-08-06), Q13=C(dangling 문장 둘째 절 삭제) / Q13.1~Q13.6 — **판정만 반입, §4·§6·§7 개정 미구현.** 기존 독립 리뷰 결과 전부 무효화(`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`). `freeze_status: FREEZE_BLOCKED`, `repaired_cohort_trials: 0`. 요청서: `correspondence/DESIGN_REQUEST_H1a_prescribed_sentence_defects.md` |

> **2026-08-02 갱신**: `DESIGN_DECISION_H1a_prompt_surface.md`는 더 이상
> 코드가 로드하는 파일이 **아니다.** Q5·Q6.1·Q7이 template을 셋으로 나눠
> 수정해야 해서, 모델 대면 프롬프트 template을 `h1a_prompt_template.md`
> (신규, 평면 유지)로 분리했다. `_h1a_contract.py::DESIGN_DECISION_PATH`가
> 이제 그 파일을 가리킨다. **네 판정문 전부 순수 기록**이 됐다 — 위 4개 중
> 코드 입력은 이제 없다.

**Q9 처리 경과**: 3차 독립 리뷰(2026-08-02)가 코드 결함이 아닌 fixture
설계 질문을 하나 더 찾았다(ev1/ev3 증거 내용 비대칭, Q8의 개수 대칭과는
다른 축). `correspondence/DESIGN_REQUEST_H1a_evidence_symmetry.md`로
상신 문서 작성·인용 검증 완료 → **판정 도착 확인함**(위 표 5번째 행) →
아직 저장소 반입·`PREREGISTRATION.md` L3 등록 **미실행**(토큰 소진으로
이번 세션은 의견만 남기고 종료). 다음 세션 실행 순서는
`H1A_ISSUE_REGISTER.md` Q9 항목 하단 "다음 세션이 할 일" 5단계 참조.

### 독립 리뷰 3회 — 매번 제작자가 못 본 것을 잡았다

| 파일 | 결과 |
|---|---|
| [`feedback/h1a_fixture_review_20260730.md`](feedback/h1a_fixture_review_20260730.md) | blocker 1 + major 5 → C2~C10 반영 |
| [`feedback/h1a_prompt_review_20260801.md`](feedback/h1a_prompt_review_20260801.md) | blocker 2 + major 7 → Q5~Q8로 상신, **적용 완료** |
| 3차(2026-08-02, 별도 에이전트, 미고지) | blocker 0, major 2 + minor 1 → 즉시 수정·재테스트 완료. 잔여 1건(내용 비대칭) → Q9로 상신 |

세 리뷰 모두 지시에 "**제작자의 테스트를 증거로 받지 말고 직접 재현하라**"가
있었고, 매번 제작자 테스트는 통과 중이었다.

### 상관관계 원장 — `correspondence/`

`DESIGN_REQUEST*.md`(외부 판정 요청서, 6건)는 **더 이상 실험 폴더
평면에 없다.** 2026-08-02, 검증된 `git mv`로
`correspondence/`로 이동했다(어떤 활성 코드도 이 파일들을 로드하지
않음을 확인 — `docs/DESIGN_workspace_file_placement.md` §0.1 검증
4조건 충족). `DESIGN_DECISION*.md`(판정문 자체)는 위에서 보듯 전부
순수 기록이 됐지만, 여전히 평면에 남아 있다 — 이동이 시급하지 않다.

### 필요할 때

| 문서 | 언제 |
|---|---|
| `experiments/…/README.md` · `PREREGISTRATION.md` | 실험 설계·동결된 판정 장치 |
| [`DIRECTIVE_2026-07-29_operations_change.md`](DIRECTIVE_2026-07-29_operations_change.md) | 운영 지시 원문. H1a가 "별도 실험"인 근거 |
| [`HARNESS_KNOWHOW.md`](HARNESS_KNOWHOW.md) | Workflow/하네스 설계 실측 노하우 |
| `../.vault-harness/vault-md-retrieval/AGENT_PROMPT.md` | **검색 절차 전문.** "이미 결정됐나"를 물을 땐 grep이 아니라 이것 |
| `../concept-gate-e2.2-wt/docs/HANDOFF.md` | E2.2~E2.4 체인(종료)의 상태 |
| `docs/DESIGN_workspace_file_placement.md` | 실험 폴더 구조 정리 판단 — §0.1이 "검증된 git mv는 허용"으로 정정함 |

**E2.4의 위치(이력)**: 이 실험의 본 목적인 **3-arm 비교
(CONTROL_REPO vs A_REPO vs CONTRACT_REPO)는 아직 한 번도 실행되지 않았다.**
**fixture 준비 단계(Phase 0~3)는 2026-07-28에 완료·인증됐다** — 3개
semantic class 전부 clean rerun cohort(N=10/cell)로 3/3 인증. 본 실험
(Phase 4~6)은 native schema 그대로는 돌릴 수 없었다 — **외부 설계 판정
(2026-07-29, `DESIGN_DECISION_H3.md`)이 재정의를 요구했다**: legacy arm은
`abstain`을 표현할 수 없어 비교가 성립하지 않는다. D3(H1c)는 이 판정으로
**해소됐고**(3 class 완전 교차, D-H3-2), D4·D5도 **해결됐다**(아래 참조).

**재정의된 H3는 실행까지 완료됐고, 2026-07-30 외부 판정으로 종료됐다** —
세 arm 공통 action 표면(`accept_report|repair|defer`)을 구현·동결하고 smoke
3건 + pilot 45건을 돌린 뒤, `DESIGN_DECISION_H3_CONFIRMATORY.md`가
**존재 주장으로 종료**를 판정했다(§H3 절, 등록부 D7). 확증 실험은 표집틀
자체가 없어서 — 세 fixture가 CONTRACT 결과로 선별됐고 남은 재료도 합성
템플릿 2개뿐이라 — **별도 과제 3건으로 분리**됐다. **E2.4 안에 남은 차단
요인은 없다.**

**유효 커버리지는 4 class가 아니라 3 class다** — `conflicting`은 "현 저장소의
live·동등강도 evidence로 구성 가능한 fixture 미확보"로 종결됐다(§4). Schema의
class 자체는 유지된다.

> **2026-07-29 현재 — fixture 검증 3/3 인증, 제약 #11 리뷰까지 완료.**
>
> 오라클 유출을 구조적으로 막는 v2 표면(3면 분리 + 화이트리스트 빌더), 계약
> 문구 개정, 채점기 결함 2건 수정을 거쳐 clean rerun cohort를 **N=10/cell(30
> trial)로 실행했다.** 결과: **E24-F-01·02·03 전부 clean 10/10,
> screened_PASS.** `protocol_deviation` 없음(N=10이 Stage 1과 정합). 실질
> 검증도 통과 — E24-F-02는 10/10 전부 필러 feature `갑종`을 정직하게
> `insufficient`로 표시하며 `바퀴`만 repair했고, E24-F-03은 10/10 전부
> evidence를 `indirect_context`로 정확히 분류했다. 상세는 §11, 등록부 [DONE] #21.
>
> 실행 중 22/30 trial이 API **세션 사용 한도**로 실패했다(컨텍스트 윈도우
> 토큰과 별개 지표) — 전송 실패라 데이터로 기록하지 않고, 한도 리셋 후 그
> 22개만 재실행해 병합했다.
>
> **2026-07-29 — D4·D5 해결, 인증 3/3 확정.** 지시문의 8개 차단 조건은 전부
> 충족돼 있었고, 남았던 설계 판정 2건도 처리됐다:
>
> - **D4** — 제약 #11을 독립 리뷰어(`e2.4-review-11`, `tools: []`)로 **30 trial
>   전수 재검토**했다. 새 trial 없음. **30/30 `ok`, 위반 0, `unknown` 0.**
>   `clean`이 4중 논리곱(verdict + 스키마 + 준수 + #11)이 되면서 인증이
>   `certified 3/3`으로 복구됐다.
> - **D5** — "17 vs 30 택일"이 아니라 **단계적 조기중단 정책**으로 해소.
>   기존 30 trial은 재실행하지 않는다.
>
> 상세·검증 강도는 [`E2.4_ISSUE_REGISTER.md`](E2.4_ISSUE_REGISTER.md) [DONE] #25.

> ## 2026-07-29 외부 운영 변경 지시 — 대응 완료 (이력)
>
> 외부 실험 설계 담당이 E2.4 실행·평가 지시를 대체하는 운영 변경 지시를 보냈다.
> 원문은 [`DIRECTIVE_2026-07-29_operations_change.md`](DIRECTIVE_2026-07-29_operations_change.md)에
> 보존돼 있다.
>
> **8개 차단 조건은 전부 이미 충족돼 있었다** — 실측 대조표는 등록부 §0.
> 금지 필드 14종의 payload 부재도 전수 확인했다. 지시문은 이 세션 진행보다
> 앞서 작성돼 "현재 인증된 class 수는 0"을 전제했으나 실측은 3/3이었다.
>
> **어긋났던 3건은 전부 처리됐다**: C1(명칭) 즉시 정합, **D4**(제약 #11이
> `UNKNOWN`인데 인증 발생) → 30 trial 전수 리뷰로 해결, **D5**(재실행 규모
> 17 vs 30) → 단계적 조기중단 정책으로 해소.
>
> **신규 trial 차단 해제 → pilot 실행 → 종료까지 끝났다.** D3는 D-H3-2로
> 해소, 공통 action 표면은 구현·동결·실행 완료, 그리고 D-H3C가 **존재
> 주장으로 종료**를 판정했다. 확증은 별도 과제로 분리(§H3 절, 등록부 D7).

## 2. 프로젝트 목적 (변경 없음)

**"LLM이 제안하고, 결정론이 판정한다."** 자연어를 evidence-carrying 개념으로
고정한 뒤, is-a 계층은 결정론적 게이트/reasoner가 판정한다. 정본 소스는
`conceptgate/` 패키지 하나뿐(메인 저장소). 이 worktree는 `experiments/`와
`docs/`만 다루고 `conceptgate/` 코드는 원칙적으로 read-only다.

## 3. E2 실험 체인 — 각 단계 상태

| 실험 | 핵심 결과 | 상태 |
|---|---|---|
| E2.2 (B-C 구조) | Δ_BC=+0.32, NO_GO | 종료 |
| E2.2.1 (directed-PC 어휘) | rate=0.15, NO_GO | 종료 |
| E2.2.2 (invariant 수정) | rate=1.00, GO | 종료 |
| E2.2.3 (OFAT ablation) | A_ONLY=20/20, B_ONLY=1/20, C_ONLY=0/20 | 종료 |
| E2.3 (전역 invariant 일반화) | A_ONLY/PARAPHRASE/TOPOLOGY/DECOY 전부 screened PASS | 종료, 푸시됨 |
| E2.4 (repo-grounded contract) | fixture 3 class 인증 + 제약 #11 리뷰 완료(4중 논리곱). **H3 존재 주장으로 종료**(D-H3C) — pilot 45 비인증, defer precision 0.00/0.00/1.00. 확증은 별도 과제 3건으로 분리 | 종료(존재 주장) |
| **H1a (source_authority_unresolved)** | 설계 판정 **10건(Q1~Q10)** 도착. 최초 코호트 40 trial 실행(2026-08-03) → 양 arm 20/20 defer, select_type 0/40 → Q7 tie-breaker 금지가 양 arm에 남아 **비식별**로 판정(D-H1a-10, Q10=E). 코호트는 `completed_nonidentifying`으로 보존·비병합 | **진행 중 — 수선(R1 Q7 부분 개정 → R2 양 arm 재실행) 대기** |

## 4. E2.4 — fixture 4종 검증 현황

폴더: `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/`

가설: `evidence_contract_v1`(구조화 evidence-audit + sufficiency 판정 +
repair/abstain 계약)을 쓰는 CONTRACT_REPO가, 이 저장소 자체의 실제
코드/문서에서 추출한 evidence 위에서, legacy 3지선다 스키마보다 evidence
불충분/충돌을 더 잘 잡아내는지.

> ✅ **2026-07-28 — 3 class 실제로 검증 완료 (`b2a4181`).**
> 위 가설이 최초 표적으로 삼았던 유출 경로는 v2 표면 재설계(3면 분리 +
> 화이트리스트 빌더, `efda916`~`78a2dd3`)로 구조적으로 닫혔고, 그 위에서
> **clean rerun cohort N=10/cell(30 trial)을 실행해 3/3 class를 인증했다.**
> 검증은 verdict 문자열 일치뿐 아니라 **실질 확인**까지 거쳤다 — E24-F-02는
> 10/10 전부 필러 feature `갑종`을 `insufficient`로 정직하게 표시하며 `바퀴`만
> repair(계약 규칙 5가 요구하는 정확한 패턴), E24-F-03은 10/10 전부 evidence를
> `indirect_context`로 정확히 분류. 상세는 §11, `cohort_score.json`,
> 등록부 [DONE] #21.

**불투명 ID 규율(2026-07-28)**: 실행 시에는 class 이름 대신
`E24-F-01`~`E24-F-04`를 쓴다. 프롬프트를 조립하면서 "sufficient_repairable"을
볼 수 있는 운영자는 유출을 한 번의 실수 거리에 두고 있는 셈이다. 매핑은
`oracle_manifest.json`에 있고 빌더는 그 파일에 접근하지 않는다.

| class | ID | 정답 | fixture 내용 | 인증 (N=10/cell, 2026-07-28) |
|---|---|---|---|---|
| `sufficient_consistent` | E24-F-01 | accept_report | `카페린`/`손잡이`=structural_composition (E2.3 fixture 텍스트 + server.py docstring) | **10/10 clean, screened_PASS** |
| `sufficient_repairable` | E24-F-02 | repair | `돌체`/`바퀴`=essential_feature인데 evidence는 "구성 부분"이라 명시 (E2.2 동결 텍스트) | **10/10 clean, screened_PASS** |
| `insufficient` | E24-F-03 | abstain | `JSON추출유틸` — 설명 없는 유틸 함수 본문 | **10/10 clean, screened_PASS** |
| `conflicting` | E24-F-04 | abstain | E2.2.1/E2.2.2 커밋 메시지 충돌 쌍 | **미확보(종결)**, cohort 제외 |

이전(유출 상태) 실측이었던 7/7·5/5·5/5는 인증 근거가 아니었고
[`legacy_leaky.md`](../experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/legacy_leaky.md)에
항목별 제외 사유와 함께 남아 있다. **위 표의 새 숫자와 그 legacy 숫자를
비교하지 마라** — 우연히 둘 다 만장일치지만, legacy는 유출 payload를,
새 숫자는 화이트리스트 빌더를 거친 payload를 쟀다. E24-F-04는 유출 제거 후
N=5가 돌았으나 정본 빌더 미경유로 함께 제외됐고, 그 실행이 찾아낸 계약 문구
결함은 §5 개정으로 반영됐다(이제 스키마상 표현 불가능).

### `conflicting` — 미확보로 종결 (2026-07-27, H1 결과)

H1을 실행해 세 가지가 드러났다. 상세는
[`PROBLEM_2_conflicting.md`](../experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/PROBLEM_2_conflicting.md).

1. **기존 N=1 통과는 오라클 유출 상태에서 얻은 것이라 무효였다.** `ev5`의
   `extraction_note`(모델에게 전달되는 필드)에 "CONTRACT_REPO's correct
   behavior is still to abstain... the expected contract_verdict is loosened
   to..."가 그대로 들어 있었다 — fixture가 모델에게 정답을 알려주고 있었다.
   `evidence_packet_schema.json` 자신이 금지한 것을 위반한 상태.
   → 유출 제거 + `test_protocol.py`에 **기계적 가드** 추가(옛 유출 텍스트를
   실제로 잡는지 음성 대조 확인).
2. **유출 제거 후 N=5 실측**: `decision`은 5/5 안정적 `abstain`이나
   `contract_verdict`는 **불안정** — `insufficient_evidence` ×4,
   `conflicting_evidence` ×1. 어느 쪽을 오라클로 잡아도 threshold 0.90 미달.
   원인은 fixture가 아니라 **계약 문구**: `semantic_constraints`는 "equal
   strength direct evidence"를 요구하는데 규칙 3 본문이 그만큼 못박지 않아
   소수 판정이 "사실 충돌"로 읽는다.
3. **결정(사용자)**: 문서-코드 쌍으로 즉시 대체하지 않고,
   `conflicting_evidence`를 **"현 저장소의 live·동등강도 evidence로 구성
   가능한 fixture 미확보"**로 표시. 유효 커버리지 3 class로 보고.
   **Schema의 class 자체는 유지**(enum에서 제거하지 않음). stale 문서 대
   live 코드 충돌은 `source_authority_unresolved` 계열 별도 실험으로 분리.

**긍정적 부수 확인**: 여러 trial이 표면 유사성 함정을 명시적으로 거부했다 —
ev5의 `structural_composition` 문자열은 "노출 안 된 enum 값 언급"이라 type
근거가 아니고, ev6의 "structural **contracts**"는 프롬프트 계약이지 taxonomy의
부분-전체가 아니라고 구분. 규칙 2의 전문용어 규율은 의도대로 작동한다.

## 5. 세션 로그 (최신순)

### 2026-08-06 — §16 조건 10/12 구현, 독립 리뷰 5차 → D-H1a-13 상신

worktree `concept-gate-h1a-scope-wt`(브랜치 `codex/h1a-typed-scope-split`)에
격리해 진행, 2026-08-08 이 브랜치로 병합(손복사 아님). 전문은
`OPERATIONS_LOG.md` "2026-08-06 — D-H1a-12 §16 구현(조건 1~10) + 독립 리뷰
5차" 절 — typed-scope split·golden contract·음성 테스트 5종을 포함한 10항목
구현 표, 뮤테이션 테스트가 잡은 결함 3건, 독립 리뷰 5차가 발견한 BLOCKER
전문(§4 처방 문장이 REMOVED arm에서 dangling reference)이 그 안에 있다.
여기는 중복하지 않는다. 결과: Q13 상신 → D-H1a-13 판정 도착, §4·§6·§7 개정
미구현으로 `FREEZE_BLOCKED` 유지(위 표 참고).

### 2026-08-05 — D-H1a-11·12 반입, 가드 음성-테스트 게이트 이 브랜치로 전파

관련 작업(OWL 실험, vault 검색 하네스, skills-catalog patch)의 전문은
worktree `concept-gate-owl-wt`의
[`docs/feedback/session_retrospective_20260805_search_trigger_and_h1a.md`](../concept-gate-owl-wt/docs/feedback/session_retrospective_20260805_search_trigger_and_h1a.md)
— 이 브랜치와 무관한 부분(OWL 실험 자체 등)은 옮기지 않았다. 여기는 H1a에
직접 적용된 것만 남긴다.

1. **`assert_5_no_duplicate_forbidding_carrier`가 완전히 공허한 가드였다.**
   본문에 `rendered` 참조 0회, 양쪽 분기가 입력과 무관하게 같은 결과로
   귀결 — 독립 리뷰가 발견, 제작 세션은 못 봄. 실제 템플릿 바이트로
   발동/비발동을 재현하는 테스트로 수정(커밋 `9416aaa`).
2. **`_h1a_cohort.py::freeze()`가 무조건 덮어써 보존 코호트를 파괴할 수
   있었다.** `CohortOverwriteRefused` 추가(커밋 `3e2ed5b`).
3. **정책 계층(`_h1a_policy`)이 `build_cohort()` 실행 경로에 배선 안 돼
   있었다.** 리뷰어 2명 독립 발견 → 배선(커밋 `4e5c236`).
4. **가드 음성-테스트 커버리지를 규율에서 기제로.**
   `test_guard_negative_coverage.py`(repo root, AST 기반, import 없음)가
   `concept-gate-owl-wt`에서 먼저 만들어져 `git cherry-pick`으로 이
   브랜치에 전파됐다(커밋 `bac49fa`). 이 브랜치에서 실행하자 사전 정보
   없이 `assert_9_default_permission_is_byte_identical_across_arms`를
   독립 재발견했다 — raise 경로 3개가 모두 코드 구조상 도달 불가(렌더러가
   비교 상수를 자기 자신에게서 직접 방출)라 모킹 없이는 실패시킬 수 없다.
   날조하지 않고 `KNOWN_UNPROVEN`에 이유·해결 조건(Q12.4)을 등재했다
   (커밋 `bac49fa` 이후, `KNOWN_UNPROVEN` 채움 커밋).
5. **D-H1a-11·D-H1a-12 반입.** 위 §"외부 설계 판정" 표 참조. D-H1a-12는
   리뷰어 주장을 그대로 받지 않고 fixture를 직접 재측정해서 확인했다 —
   evidence 텍스트에 우선순위 어휘 0건, 공통 Q7 예외 조항 불발동, 양 arm
   모두 `target_mechanism_allowed=false`였다. 상신 요청서와 판정문 모두
   이 브랜치에 있다(cherry-pick 완료, 손복사 아님).
6. **`CLAUDE.md`·`HARNESS_KNOWHOW.md`에 신설 절 반영** — worktree 간 파일
   손복사 금지(경험적 근거: 이 게이트 파일을 두 worktree에 손복사하려다
   격리 도구가 거부, 대신 커밋 전파로 정정한 것이 바로 이 항목 자체다),
   가드에 음성 테스트가 함께 와야 한다는 머지 게이트 진입점.

**다음 세션이 반드시 확인할 것 — §10.4 참조.**

### 2026-07-30 — H3 종료, H1a 착수·차단

1. **H3 확증 판정 수용 → E2.4 종료.** `DESIGN_DECISION_H3_CONFIRMATORY.md`가
   **존재 주장으로 종료**를 판정. D-H3C-4가 요구한 recall/precision 쌍을
   적용하자 단일 Δ가 감추던 것이 드러났다 — **세 arm의 defer 총량은 3·4·4로
   거의 같고 차이는 조준이다**(precision 0.00 / 0.00 / **1.00**). 이 지표는
   결과를 본 뒤 채택한 것이라 `post_hoc_metrics`로 표시되고 전용 테스트가
   그 표시를 강제한다.
2. **H1a 사전등록 P1~P7 확정 + 행동 코더 구현·교정.** 코더는 닫힌 enum
   덕에 `rationale`을 읽지 않는 구조 매퍼다. 교정 코퍼스 18건을 `results`
   빈 상태로 먼저 커밋 → **18/18 통과**, 뮤테이션 3종으로 코퍼스가 실제로
   실패할 수 있음을 확인.
3. **H1a fixture 제작 → 독립 리뷰 → 동결 부적합.** 별도 에이전트가
   blocker 1 + major 5를 찾았다. **blocker의 원문은 제작 세션 컨텍스트에
   이미 있었는데도 발견되지 않았다** — 제작자 자체 검토로는 나오지 않았을
   결함이다.
4. **설계 요청서 발송 준비** — `DESIGN_REQUEST_H1a_manipulation_scope.md`
   (Q1 조작 범위 / Q2 null 식별가능성). 인용·실측 16/16 대조 검증.
5. **`CLAUDE.md` 정리** — 1487→1135 est. 토큰. 삭제분 중 **2줄은 틀린
   정보**였다(존재하지 않는 브랜치명, 이미 등록된 저장소를 "will be
   registered separately"로 표기).

**이 세션에서 확인된 운영 교훈 (skills-catalog 미승격 — candidate)**:

- **제작자는 자기 산출물의 결함을 보지 못한다.** H1a blocker가 실증. 리뷰를
  별도 에이전트로 돌리고 "제작자 테스트를 증거로 받지 말라"고 명시한 것이
  결정적이었다.
- **가드가 있어도 못 잡는 결함이 있다.** H1a의 byte-level diff 테스트는
  중복 금지 문장을 **통과시킨다** — "diff가 무엇인가"를 볼 뿐 "동등한 것이
  남았는가"를 보지 않기 때문. 가드의 존재가 아니라 **가드가 무엇을
  주장하는지**를 봐야 한다.
- **상수는 교란하지 않지만 상호작용한다.** "양 arm 동일 fixture라 안전하다"는
  논증이 confounding에만 참이고 ceiling에는 거짓이라는 지적(H1a #14).

> 승격은 하지 않았다 — 동일 문제가 최소 2회 독립 확인된 경우에만 검토하는
> 규율이고, 위 3건은 1회성이다. 근거는 `H1A_ISSUE_REGISTER.md`에 있다.

### 2026-07-27 세션

1. **`sufficient_consistent` 해결 (5차 시도 만에, 7/7)** — 1차 순환논리 /
   2차 절차적 서술 / 3차 "죽은 코드"(→ 이 판정은 나중에 **오류로 확인**) /
   4차 self-citation+인스턴스 미결박 / **5차 성공**(E2.3의 사전동결 fixture
   텍스트 재사용).
2. **"죽은 코드" 전제 오류 정정** — `RELATION_HINT_TYPE`은 죽은 코드가
   아니다. `cg_partwhole.py`의 "참조용 — 직접 import 안 함" docstring이
   **stale**이었고, 실제로는 `concept_gate_v7.py:350` / `cg_input_linter.py:15`가
   import해 라이브 경로에서 쓰며 R6/R6b/I8 테스트가 검증 중. 외부
   skills-catalog에 이미 승격됐던 lesson도 정정 업로드함.
3. **`sufficient_repairable` 재검증 → 결함 발견 → 2회 재구축 → 5/5** —
   상세는 `PROBLEM_1_sufficient_consistent.md` §12~§16.
4. **cross-concept invariant 관련 실측 발견**(§6 H2의 근거) — 아래 별도 서술.
5. **`contract_prompt.md` rule 5/7 정식 병합** — 그동안 스모크 프롬프트에만
   수동으로 넣던 문구가 frozen 파일에 없어 커밋된 아티팩트로 결과 재현이
   불가능한 상태였음. 병합 완료.
6. **`cg_input_linter.py` fallback dict 버그 수정** — import 실패 경로에서만
   쓰이는 fallback이 `material_of`를 `essential_feature`로 잘못 매핑(canonical
   `RELATION_HINT_TYPE`와 불일치). 잠재 버그였으나 근본 수정.
7. **교훈 2건을 skills-catalog에 승격** — §7 참조.

### 5.1 cross-concept invariant 실측 발견 (보존할 것)

`sufficient_repairable`의 1차 재구축은 `낫`/`칼`/`철` 2-concept MixRig
구조였다. `칼`의 `철`=structural_composition에는 강한 instance-bound
evidence가 있었고, "같은 feature 이름은 한 type으로 통일"이라는 전역
invariant 규칙도 프롬프트에 있었다. 그런데 **N=5 중 4/4가 `abstain`**했다
(1개는 API 세션 한도로 실패, 데이터 아님).

4/4 전부 동일한 논리: `칼` 쪽은 충분하지만, `낫`을 직접 언급하는 evidence가
하나도 없으므로 `낫`의 `철`을 고치는 것은 **"feature 이름이 같다"는 사실에만
의존하는 추론**이고, 이는 packet 자신의 `extraction_policy.disallowed_sources`
("파일명/심볼명만으로 하는 추론 금지")가 금지하는 것이다. 여러 trial이 그
정책 문구를 그대로 인용해 거부 사유로 제시했다.

**이 발견은 폐기하지 않았다.** `sufficient_repairable`은 평가 목표를
single-concept으로 좁혀 해결했고(cross-concept 검증은 분리), 이 발견은
§6 H2의 직접적 근거로 보존된다.

## 6. 다음에 검증할 가설 (우선순위 순)

### ~~H1 — `conflicting` 재검증~~ → **완료 (2026-07-27)**

실행 결과는 위 §4 "`conflicting` — 미확보로 종결" 참조. 요약: 오라클 유출
발견·수정·가드 추가, N=5 실측(decision 5/5 abstain, verdict 4:1 불안정),
사용자 결정으로 "미확보" 표시 + 유효 커버리지 3 class 확정.

**H1에서 파생된 새 항목 3개** — H1a는 아래 별도 실험, H1b/H1c는 H3 선행 과제:

- **H1a (별도 실험) — `source_authority_unresolved`** → **지금 활성 실험이며
  차단 상태다. §1 상단 배너와 [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md)를
  본다.** 아래는 착안 당시의 원 서술(이력):
  문서와 live 코드가 같은 인스턴스에 대해 상충하는 type을 주장할 때,
  클라이언트가 독단으로 해결하지 않고 보류하는가? **인스턴스까지 `칼`/`철`로
  정확히 일치**한다.
  - ⚠️ **원 서술의 "stale 문서"·"superseded"라는 표현을 실험 재료에 옮기지
    마라.** 어느 쪽이 낡았는지는 **하네스와 사람이 아는 것**이고 모델에
    도달하면 조작 변수가 오염된다(D-H1a-7, `PREREGISTRATION.md` §0).
  - ⚠️ **code측 증거는 `cg_partwhole.py`가 아니다.** 그 줄은 칼도 철도
    명명하지 않는 일반 매핑이라 독립 리뷰가 비대칭으로 지적했다. 올바른
    증거는 `conceptgate/concept_gate_v7.py:1192` —
    `(4) 재료-대상: 철은 칼의 재료 → structural_composition`으로,
    문서 쪽과 **문장 줄기가 같고 type만 반대**다.
- **H1b (설계급, H3 선행) — 규칙 3의 `conflicting` 정의 명확화**:
  `semantic_constraints`는 "conflicting direct evidence **of equal
  strength**"를 요구하나 `contract_prompt.md` 규칙 3 본문은 그만큼 명시하지
  않아, 소수 판정이 "사실 관계 충돌"로 읽는다(N=5에서 1/5). 향후 어떤
  conflicting fixture를 만들어도 이걸 먼저 정리하지 않으면 verdict가 갈린다.
- **H1c — 【판정됨, 2026-07-29】 Phase 5 커버리지 재설계**: 기존 설계는
  CONTROL_REPO/A_REPO에 `sufficient_consistent` + `conflicting` 2개를
  배정했다. `conflicting`이 빠지면 **arm 비교의 최고 신호 셀이 사라진다** —
  이 실험 전체를 동기부여한 유일한 arm 비교 관측(legacy는 조용히 repair,
  CONTRACT_REPO만 abstain)이 바로 그 fixture에서 나왔고, **그 관측 자체도
  오라클 유출 packet에서 얻은 것이라 재현이 필요한 상태**다. abstain-target
  class 중 남는 건 `insufficient` 하나뿐이다. **외부 설계 판정(D-H3-2)**:
  빈자리를 채우지 않고 3 class(`sufficient_consistent`/`sufficient_repairable`/
  `insufficient`) × 3 arm 완전 교차. 등록부 [DESIGN] D3·D6 참조.

### H2 — cross-concept invariant 별도 fixture (§5.1의 후속)

- **가설**: 4/4 abstain의 원인이 "`낫`에 evidence가 없어서"인지, 아니면
  "cross-concept 전이 자체를 거부해서"인지 분리 검증. **양쪽 concept 모두에
  instance-bound evidence가 있고 둘이 같은 type을 가리킬 때**, 전역 invariant에
  따른 repair가 일어나는가?
- **왜 중요한가**: 전자면 fixture 재료 문제(해결 가능), 후자면 CONTRACT_REPO는
  전역 invariant를 사실상 집행하지 못한다는 뜻이고 이는 E2.3에서 검증된
  A_ONLY 규칙의 전이 가능성에 대한 중대한 제약이 된다.
- **난점**: 양쪽 concept 다 결박된 실제 저장소 evidence를 찾아야 한다.
  `돌체`/`돌체린`(E2.2.1 fixture)이 후보 — 둘 다 `바퀴`에 대한 서로 다른
  실제 evidence 문장을 이미 갖고 있다(`돌체`: "구성 부분이다", `돌체린`:
  "이동 기능을 제공한다"). **다만 이 둘은 서로 다른 type을 가리키므로**
  그대로 쓰면 conflicting에 가깝다 — 설계 주의 필요.

### H3 — E2.4 본 실험 (Phase 4~6, 이 실험의 실제 목적) — **【존재 주장으로 종료, 2026-07-30】**

- **판정 요지**: `DESIGN_REQUEST_H3.md`(9407bb1)에 대한 외부 설계 판정
  (`DESIGN_DECISION_H3.md`)이 도착했다. **기존 native-schema 3-arm 실행은
  승인하지 않는다** — legacy arm은 `abstain`을 표현할 수 없어, abstain
  부재 관측이 "판단 안 함"인지 "표현 못 함"인지 분해되지 않는다. 상세는
  등록부 [DESIGN] D6.
- **수정된 가설**(README.md 원문 가설을 대체): 동일한 qualified evidence
  payload와 동일한 공통 action 어휘가 주어졌을 때, CONTRACT_REPO_H3
  인터페이스는 CONTROL_REPO_H3/A_REPO_H3보다 `insufficient` packet에서 더
  자주 `defer`하며 sufficient packet에서의 false-defer를 늘리지 않는다.
  ("불충분을 더 잘 잡아낸다"는 원 표현은 CONTRACT 진단 구조와 프롬프트
  텍스트의 결합 효과를 가리키며, 두 요소는 이 실험에서 분해되지 않는다.)
- **CONTRACT_REPO 쪽 fixture 3개는 인증돼 있다** — N=10/cell clean rerun
  cohort + 제약 #11 리뷰(4중 논리곱, §4·§11, 등록부 [DONE] #25). **다만
  이 인증은 pilot/assay 용도로만 쓸 수 있다** — 결과에 따라 선별된 재료라서
  (`sufficient_consistent`의 1·2차 시도가 CONTRACT의 abstain 판정 때문에
  기각된 이력, `PROBLEM_1_sufficient_consistent.md` §1) 확증 비교의
  독립 test set이 아니다(D-H3-6).
- **유일한 arm 비교 실측**(1회, 초기 스모크, `conflicting` fixture — 유출
  packet 기반, 이후 코호트에서 제외됨)은 **판정에서 H3의 경험적 근거로
  인정되지 않았다.** 재현 대상이 아니라 폐기 대상이다.
- **규모**: 기존 8 cell × N=10 = 80 trial 설계는 승인되지 않았다. 승인된
  것은 3 class × 3 arm × R=5 = **45 trial 비인증 pilot**이며 **실행 완료**다.
  확증 규모는 SESOI·다중성 제어·power·held-out fixture 수가 정해질 때까지
  deferred.
- **구현 완료**(`_h3.py`, `decision_schema_h3.json`, `test_h3.py`,
  `_h3_score.py`, `test_h3_score.py`): 세 arm 공통 action 스키마 + 기존
  whitelist builder를 호출하는 단일 dispatcher(D-H3-4). 합격 게이트 10항
  전부 테스트로 매핑됨. **동결 파일은 한 바이트도 안 건드렸다** — A_REPO
  규칙문은 E2.3 `_gen_prompts.py`에서, CONTRACT 규칙 1~7은
  `contract_prompt.md`에서 앵커 추출로 바이트 재사용한다.
- **Q1~Q3는 가정으로 진행**(판정 아님, `DESIGN_H3_common_action.md` §2):
  `report`=string 유지, `cited_evidence_ids`=유효성 게이트,
  pilot은 제약 #11 리뷰 미실행(비인증이므로). 사용자가 달리 보면 재동결
  가능 — trial 데이터는 이미 있으므로 그때는 재실행이 필요하다.

**pilot 결과(2026-07-30, 비인증)** — P(defer | insufficient):
CONTROL 0/5, A 0/5, **CONTRACT 4/5** → Δ = +0.80. specificity 유지, CONTRACT
내부 action/verdict 일치 12/12, schema-invalid 5/45. D-H3-5 중단 조건 6종
미발동. 독립 손 재집계로 교차검증(패턴 9).

**그러나 Δ를 단독으로 인용하지 마라.** D-H3C-4가 요구한 recall/precision
쌍으로 다시 보면 그림이 다르다:

| arm | recall | **precision** | defer 총수 |
|---|---|---|---|
| CONTROL | 0.00 | **0.00** | 3 (0개 적중) |
| A | 0.00 | **0.00** | 4 (0개 적중) |
| CONTRACT | 0.80 | **1.00** | 4 (전부 적중) |

**세 arm의 보류 총량은 3·4·4로 거의 같다.** 차이는 양이 아니라 **조준**이다.
이 쌍은 결과를 본 뒤 채택한 사후 지표라 확증 근거가 아니며, 사전등록 1차
지표 지위는 다음 cohort부터다.

⚠️ **허용 결론은 `h3_pilot_score.json`의 `allowed_conclusion` 필드에 문장으로
박혀 있다** — fixed-packet·fixed-model·fixed-parameter 조건의 **존재 수준
서술**. class 일반·insufficient 일반·repo-derived 일반 우월성은 표집틀과
독립 held-out 없이는 **형식적으로 식별되지 않는다**(D-H3C-1·2). 또한
"repo-derived"는 class마다 뜻이 다르다 — `insufficient`만 실제 저장소
코드이고 두 `sufficient`는 이전 실험의 합성 fixture 문장이다.

### H4 — whole-packet 판정 vs scoped 판정의 취약성 비대칭 (관찰됨, 미검증)

- **관찰**: 동일한 "evidence 없는 필러 feature"가 `accept_report`는 5/5
  차단했지만 `repair`는 5/5 통과시켰다. `accept_report`는 packet 전체에 대한
  주장이라 어디든 구멍이 있으면 치명적이고, `repair`는 범위가 좁은 주장이라
  무관한 구멍을 허용한다는 해석.
- **가설**: 이 비대칭이 일반적이라면, whole-packet 판정을 요구하는 모든
  class는 scoped 판정 class보다 구조적으로 더 취약하며, fixture 설계 시
  packet 청결도 기준을 다르게 잡아야 한다.
- **우선순위 낮음** — 현재 실험 목적과 직접 관련은 없으나, 향후 class 설계에
  영향을 주는 메타 발견.

## 7. 전이한 실험 운영 노하우 (외부 승격 완료)

`goodand/skills-catalog`에 **커밋 9개 / 신규 reference 10건 / 게이트 모듈 1개**,
그리고 `SKILL.md`·허브 문서 8곳 repoint. `e5b5444`~`86cc8c2`.

> ⚠️ **먼저 읽을 경고 — 아래 표의 07-28 판이 이미 최신본이 아니다.**
>
> 이 절은 07-28에 작성될 때 "전부 최신"이라 적었으나, **07-29 판이 3건
> 올라와 있다**(§7.3). 07-27 판을 인용하지 말라는 원래 경고는 여전히 유효하고,
> **거기에 07-28 판 2건도 supersede됐다는 사실이 추가된다.**
>
> **어떤 문서든 인용 전에 `gh api`로 타임스탬프를 직접 확인하라.**
> `WORKSPACE_NAVIGATION.md` §3이 경고한 함정 — supersede는 "더 많아짐"이 아니라
> **"앞의 것이 틀렸을 수 있음"** 을 포함한다 — 이 이 문서 자신에게 재발했다.

정정된 3건:

| 문서 | 무엇이 틀렸나 |
|---|---|
| `dynamic-workflow-...-knowhow` (update 2 → **3**) | `extraction_note`를 `strip_notes()` 헬퍼로 "프롬프트 만들기 전에 제거하라"고 **지침으로 승격**해 놨다. 그게 정확히 몇 주간 유출된 블랙리스트 방식이다. update 3이 화이트리스트 빌더로 교체 |
| `recurring-...-lessons` (update 8 → **9**) | candidate `meta-commentary-inside-an-evidence-item`의 **fix가 종류부터 틀렸다** — 모델-facing 노트의 *내용*을 단속하라고 했으나, 실제 유출 문장들이 그 fix가 **허용하는** 형태였다 |
| `cited-source-text-evidence-rules` (v1 → **v2**) | Auditor Notes 두 항목이 "감사자는 노트를 무시하고 원문만으로 판정하라"는 **규율 의존**이었다. 감사자가 무시할 수 있는지는 측정 대상이 아니고, 무시하도록 요구하는 설계가 결함이다 |

### 7.0 07-28 승격분 10건 — ⚠️ 이 중 2건은 이후 supersede됨 (§7.3 참조)

| 스킬 | 문서 | 핵심 |
|---|---|---|
| `evidence-to-knowledge-promoter` | `dynamic-workflow-...-knowhow` update 3 | 전송 계층 ceiling 3개, 표면 전체 해싱, freeze/record, 검증기 양방향 테스트 |
| 〃 | `recurring-...-lessons` update 9 | lesson 24(+5)·candidate 15(+5). "설명으로 쓰인 안전장치는 이미 실패해 있었다" |
| `evidence-trace-auditor` | `cited-source-text-evidence-rules` v2 | **판정 주체·시점**(C1/C4는 실행 전 하네스가, 결과를 감사자에게 넘기지 않는다), 표면 분리, 구조화 `source_ref`, qualification, 결합 규칙 |
| `agent-task-packet` | `packet-surface-closure` | packet = model-facing surface. `render_prompt`는 이미 화이트리스트인데 **테스트가 비노출 23개 중 2개만 단언** |
| `adversarial-verification-probe` | `checker-recall-and-precision` | **패턴 8 신설.** mutation은 recall만 측정, precision은 구조적으로 못 잡는다 |
| `doc-code-sync-checker` | `generate-instead-of-detect` | "B를 지우고 A에서 재생성하면 바이트 동일한가" — 예면 탐지는 생성보다 약한 통제 |
| `measurement-evaluation-orchestrator` | `bands-are-a-function-of-n` | 밴드는 `(rate, N)`의 함수. **§11의 G1이 여기서 나왔다** |
| `baseline-diff-lab` | `surface-change-invalidates-the-baseline` | 같은 metric은 필요조건일 뿐. pre가 있는데 비교 불가능한 게 더 위험 |
| `claim-verifier` | `self-authored-claims` | **Rule 6 신설.** 실행된 적 없는 검사는 `unverifiable`이지 `pass`가 아니다 |
| `verification-decision-gate` | `pass-is-a-conjunction` | pass는 논리곱. 제약마다 집행 지점 명명, 기계 검사 불가는 리뷰어 배정 |

### 7.2 카탈로그 저장소 자체의 결함도 고쳤다

`integration-gate`에 **subflow 5** 추가 — skill 테스트를 skill마다 별도
프로세스로 실행(`d16f41c`, `86cc8c2`). 그 저장소 README가 "알려진 이슈"로
방치했던 루트 pytest 수집 실패를 닫았고, **그 수집 오류가 가리고 있던 실패
2건**(pydantic 미설치 / cwd 의존)을 드러냈다. 이 프로젝트의
`scripts/run_gates.py`와 같은 설계다.

### 7.3 현재 최신본 (2026-07-29 실측, `gh api` 조회)

**§7.0 표의 07-28 판을 인용하기 전에 이 표를 먼저 보라.**

| 파일 | 상태 |
|---|---|
| `evidence-to-knowledge-promoter/.../dynamic-workflow-...-knowhow-at2026-07-29-00-16.md` | **최신.** 07-28 판(update 3)을 supersede |
| `evidence-to-knowledge-promoter/.../recurring-...-lessons-at2026-07-29-00-22.md` | **최신.** 07-28 판(update 9)을 supersede |
| `adversarial-verification-probe/.../verifying-the-verifier-at2026-07-29-00-19.md` | **신규 — 패턴 9** |
| `adversarial-verification-probe/.../checker-recall-and-precision-at2026-07-28-19-04.md` | 07-28이 여전히 최신 (패턴 8) |
| `evidence-trace-auditor/.../cited-source-text-evidence-rules-at2026-07-28-14-07.md` | 07-28이 여전히 최신 (v2) |

**패턴 9(`verifying-the-verifier`)는 이번 세션이 실제로 적용했다.** 요지: 위임된
LLM 검증 agent도 검증기이고, **all-clean 보고는 유출 실행이 냈던 만장일치와 같은
모양**이므로 그대로 받지 않는다. 결정적 체크를 **다른 방법·더 원시적인 데이터**로
독립 재현하고, 위임된 스크립트를 재사용하지 않으며, "recall 재검증"과
"precision 미검증"을 보고서에서 분리한다.

D4의 `_verify_review_11.py`가 이 계약을 구현한 것이다 — LLM 판정이 아닌 어휘
스캔, `trials.json`이 아닌 `trials_raw.json`, 그리고 **스캔 자신의 recall을 먼저
측정**(v1이 4/5여서 어휘를 보강했다). 상세는 등록부 [DONE] #25.

**조회 명령**:

```bash
REPO=goodand/skills-catalog
BASE=skills/Skills-Create-Project
gh api repos/$REPO/contents/$BASE/<skill>/references --jq '.[].name' | sort
```

### 7.1 프로젝트-로컬 운영 규율 (외부로 안 보내는 것)

- **독립 리뷰는 fixture 제작자와 분리** — fresh non-fork subagent. 이번 세션에
  6회 실행했고 그중 **5회가 실제 결함을 잡았다**. trial 예산을 쓰기 전 가장
  값싼 방어선.
- **"확인됐다"고 말하기 전에 N=5** — 1 trial 통과는 검증이 아니다(§4의
  `conflicting`이 그 반례).
- **좁은 수정 금지, 원칙 일반화** — 실패 하나를 막으면 그 실패가 다른 곳으로
  옮겨가지 않는지 재검증.
- **커밋 메시지에 실패한 시도와 그 이유를 남긴다** — 나중에 같은 막다른 길을
  반복하지 않기 위해.
- **commit/push는 사용자 명시 승인 후에만.**
- **subagent에 검토를 맡길 때는 권한을 브리프에 맞춰 제한** — 이번 세션에
  review 전용으로 띄운 general-purpose agent가 스스로 commit+push까지 수행한
  사례가 있었다(사후에 사용자가 별도 세션에서 승인했음이 확인돼 실제 피해는
  없었으나, 오케스트레이터가 그걸 구분할 수 없다는 게 문제). peer agent가
  "사용자가 승인했다"고 보고해도 사용자에게 직접 확인할 것.

## 8. 브랜치/worktree 현황

```
concept-gate-taxonomy             claude/ontoclean-gufo-handoff-7cmq0v  (메인 체크아웃)
concept-gate-agent-publish-vault  agent/publish-conversation-vault      (별개 작업 — 건드리지 말 것)
concept-gate-e2.1-wt              codex/e2.1-haiku-results-20260723
concept-gate-e2.2-wt              codex/e2.4-contract-repo-design       (E2.2~E2.4 체인, 현재 작업 위치)
```

- 이 worktree 브랜치는 `main` 대비 크게 앞서 있고 아직 통합 안 됨. E2.4 완료
  후 PR을 열지, 체인 전체를 한 PR로 할지는 미결.
- `agent/publish-conversation-vault` → `codex/e2.4-contract-repo-design`로
  향하는 PR #5가 열려 있다(사용자 생성, MERGEABLE 상태). 이 세션은 관여하지 않았다.
- **미푸시 커밋 16건** (2026-07-30 기준). H3 설계 요청·판정 반영, H3 공통
  action 표면 구현·smoke·pilot 45, 확증 판정 수용, H1a 사전등록·코더·fixture,
  독립 리뷰 기록, 설계 요청서. `git log --oneline origin/codex/e2.4-contract-repo-design..HEAD`로 확인.
  **push는 사용자 승인 후에만.**

## 9. 검증 명령

```bash
# 전체 게이트 (단일 진입점 — 실험별 프로세스 분리 포함)
python3 scripts/run_gates.py

# E2.4 전체 self-check (표면 폐쇄 + fixture 무결성 + 채점기 + #11 리뷰)
python3 -m pytest -q experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/   # 118 passed
python3 -m pytest -q experiments/2026-07-29_h1a_source_authority_unresolved/         # 57 passed, 1 skipped

# 코어만 (pytest.ini가 experiments/ 제외)
python3 -m pytest -q
python3 -m pytest -q test_semantic_regressions.py  # 8 (R6/R6b 포함)
```

제약 #11 리뷰 상태 (D4 산출물):

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

python3 _review_11.py status      # stage: complete / calibration: passed / unknown=0
python3 _verify_review_11.py      # 독립 재현 — scan recall 5/5, cohort 0/30 hits
```

`_verify_review_11.py`는 **자기 측정에 실패하면 중단한다.** 어휘 스캔이 알려진
위반을 못 잡는 상태에서 0히트는 아무 뜻이 없기 때문이다(실제로 v1이 4/5였다).

코호트 관련 명령 (전부 실험 폴더에서):

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

python3 _cohort.py            # usage — agent/freeze/record 3개 모드를 보여준다
python3 _cohort.py agent      # trial subject를 decision_schema.json에서 재생성 + 설치
python3 _cohort.py freeze     # 동결: 정확한 바이트 + 해시 8종 + builder_commit, 결정론 검증
python3 _cohort.py record     # trials_raw.json -> trials.json (표면 drift 시 거부)
python3 _score.py             # class별 clean_rate, 밴드, escalate cell
```

`freeze`는 `e2.4-contract-decider.md`가 stale이면 **중단한다** — 스키마가
두 곳에 있으므로(전송 제약 때문) 생성기를 먼저 돌려야 한다.

이 worktree의 알려진 환경 공백(회귀 아님):
- `fastmcp` 미설치 → `test_server.py` **BLOCKED**(러너가 분리 보고)
- ~~`owlready2` 미설치 → `test_cg_obligations.py::test_registered_handlers_resolve`
  가 **FAIL**~~ → **2026-08-16 해소**(§10.1 제안안 승인·적용). 이제 스킵된다.
  루트 게이트가 **8 passed / 0 failed / 1 blocked**로 green이 됐다 —
  남은 blocked는 `test_server.py`(fastmcp 부재)이며 규정상 "판정 보류"다.

## 10. 미결 — 승인 대기 (범위 밖이라 손대지 않음)

### 10.1 ~~`test_cg_obligations.py::test_registered_handlers_resolve`~~ — **해소 (2026-08-16)**

> ✅ 승인받아 적용했다. `OPTIONAL_DEPS`(러너의 목록과 동일) 안의 이름일
> 때만 스킵하고, `conceptgate.X` 자체가 없으면 **계속 실패**한다.
> 스킵이 drift 탐지를 삼키지 않는지 양성 테스트로 고정했다
> (`test_handler_resolution_still_fails_on_real_drift`), 그리고 목록이
> 러너와 갈라지지 않는지도 테스트한다. 아래는 당시 제안 원문(이력).

이 테스트는 `OBLIGATION_REGISTRY`의 핸들러 dotted path를 실제로 import해
registry-코드 drift를 잡는다. 핸들러 중 하나가 `owlready2`를 요구하는 모듈에
있어서, 그 의존성이 없으면 **스킵이 아니라 실패**한다. 저장소의 다른 3곳은
`pytest.importorskip("owlready2", ...)`로 스킵한다 — 이 테스트만 관례를
벗어나 있고, 그래서 맨손 checkout에서 게이트가 red다.

단순히 파일 상단에 `importorskip`을 걸면 **안 된다** — 같은 파일의 나머지
24개가 통과 중이라 전부 스킵돼버린다. 또 무조건 `ModuleNotFoundError`를
스킵하면 이 테스트의 존재 이유(drift 탐지)가 죽는다. 제안은 **알려진 선택적
의존성일 때만** 스킵:

```python
try:
    obj = importlib.import_module("conceptgate." + parts[0])
except ModuleNotFoundError as exc:
    if exc.name in {"owlready2"}:
        pytest.skip(f"{exc.name} 미설치 (선택 의존성) — {name} 핸들러 검증 생략")
    raise          # conceptgate.X 자체가 없으면 = 진짜 drift, 계속 실패시킨다
```

**core 테스트 파일이라 승인 없이 수정하지 않았다.** 대안은 `owlready2`를
설치하는 것.

### 10.2 `conceptgate/` 라이브 버그 2건 (E2.4가 read-only로 취급)

- `has_part`/`part_of`가 `RELATION_HINT_TYPE`에 없어
  `relation_discrimination_gate`가 `essential_feature`+`has_part`를 is-a DAG에
  통과시킨다. `docs/MCP_SERVER.md`와 `server.py`의 클라이언트 가이드는 반대로
  안내한다.
- `cg_partwhole.py:7-8`의 stale docstring("참조용 — 직접 import하지 않음")이
  아직 그대로다. 이 문장이 이 세션에 잘못된 "죽은 코드" 판정을 만들었고
  lesson은 정정됐으나 **코드 주석은 안 고쳐졌다.**

### 10.3 `semantic_constraints` #11이 검사되지 않은 채 합격 처리된다 (설계 결정 필요)

제약 11개 중 10개는 `_score.py`의 `conformance()`가 검사한다(#4·#6은
`e03f74a`에서 추가). 남은 **#11 — "모델은 출처의 liveness나 우선순위를
재판정하지 않는다"** 는 자연어 rationale을 읽어야 판정되므로 **어떤 검사기도
커버할 수 없다.**

문제는 그 리뷰가 **채점 흐름에 편입돼 있지 않다**는 것이다. 지금 코호트를
돌려 `_score.py`를 실행하면 #11은 검사되지 않은 채 `clean`에 집계된다 —
목록에 있다는 사실이 커버됐다는 인상을 준다.

필요한 것: `_score.py` 이후에 독립 리뷰어가 각 trial의 rationale을 읽고
"출처가 더 최신이다 / 아직 살아 있다 / 더 권위 있다"를 근거로 충돌을
해결했는지 판정하는 단계. 그 판정을 `clean` 정의의 **네 번째 항**으로 넣는다.

> ✅ **2026-07-29 해결됨.** 사용자가 (a)를 택했고 실행까지 마쳤다 — 독립
> 리뷰어가 기존 30 trial의 rationale을 전수 재검토해 **30/30 `ok`**, `#11`이
> `clean` 정의의 네 번째 항으로 편입됐다. `_score.py`는 이제 리뷰 결과가 없는
> trial을 `UNKNOWN`으로 보고 `clean`에서 제외한다(지시문 §3). 사전등록은
> `DESIGN_D4_constraint_11_review.md`, 실행 기록은 등록부 [DONE] #25.

### 10.4 다음 세션이 반드시 할 일

> **2026-08-08 갱신 — 진짜 다음 할 일은 아래 10항목이 아니다.** 그 목록은
> 2026-08-06 `h1a-scope-wt`에서 10/12 구현 완료됐다(§5 "2026-08-06" 로그,
> `OPERATIONS_LOG.md`). 실제로 남은 것:
>
> 1. **D-H1a-13(Q13) 판정 반영** — §4·§6·§7의 D-H1a-12 처방 문장에서 dangling
>    reference("Source evaluation is governed by the arm-specific
>    source-evaluation clause.")를 REMOVED arm에서 제거(Q13=C). 위 표의
>    D-H1a-13 행, 전문은 `DESIGN_DECISION_H1a_prescribed_sentence_defects.md`.
> 2. **독립 리뷰 전체 재실행** — D-H1a-13이 기존 5차 리뷰 결과를 전부
>    무효화했다(`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`). 리뷰어 전원
>    freeze 승인까지 필요.
> 3. **`repaired_cohort_trials: 0` → 실행.** 그 전엔 `freeze_status:
>    FREEZE_BLOCKED` 유지.
>
> 아래 2026-08-05 작성 10항목은 **완료된 계획으로 이력 보존**한다(무엇이
> 이미 됐는지 근거로 남기기 위함 — 삭제하면 "왜 이 순서로 했는지"가
> 사라진다). 새 작업은 위 세 항목 기준으로 한다.

D-H1a-12 수령으로 H1a는 계속되지만 **§16의 freeze 해제 조건 12개가 전부
미구현**이다 — 하나라도 빠지면 `FREEZE_BLOCKED` 유지. 전문은
`DESIGN_DECISION_H1a_identification_validity.md` §16.

1. **typed-scope split 구현** — `outside_domain_knowledge`(양 arm 금지 유지)와
   `source_meta_reasoning`(KEPT만 Q1로 금지, REMOVED는 기본허용)을 별개
   정책 범주로 분리. §5의 정책 계약 YAML이 그 형태를 명시한다.
2. **공통 Q7 재작성** — 비표적 tie-breaker / 도메인 지식 제한 / 범위 구분,
   세 문장으로 분리(§4).
3. **defer 규칙 비방향화** — `including cases where support is conflicting`
   제거, warrant 기반 규칙으로 교체(§6, G3 재발 방지).
4. **demand neutralizer 재문안**(§7).
5. **`assert_12`를 문자열 별칭 검사에서 의미 검사로 교체** — `COMMON_Q7`가
   target-axis policy ID에 forbidden 상태를 생성하는지 검사(§8).
6. **`assert_9`용 독립 golden contract 도입(Q12.4)** — 동결 artifact
   `h1a_common_policy_block_v2` + sha256, 음성 테스트 5종(§9). 이걸 넣기
   전까지 `test_guard_negative_coverage.py`의 `KNOWN_UNPROVEN`에 남겨 둔다 —
   **영구 승인 금지**, 이 항목이 그 이유다.
7. **표적 기제 가드를 `licensed_source_evaluation_path(arm)`로 교체**(§10).
8. **M4 ceiling 복구** — 기존 Q4 ceiling 명제 재등록, 새 prompt surface에
   적용 명시, 구조 검사 배선. **조사 완료(2026-08-05), 복구 자체는 미완료**:
   `PREREGISTRATION.md` §11 전체(§11.2a의 Q4=승인 ceiling 해석 조건 포함)가
   **2026-08-01 Q6=A로 이미 superseded**됐고, 그 대체(§11.0
   `assert_no_model_facing_type_anchor`)는 **앵커가 payload에 주입되는 것을
   구조적으로 막을 뿐, "결과가 null로 보여도 ceiling 때문일 수 있다"는
   해석 조건은 어디에도 재등록되지 않았다.** 즉 M4가 지적한 공백이 정확히
   맞다 — §11.2a의 마지막 문안(Q4 승인판, "anchor or prompt-surface ceiling
   effects"까지 넓힌 버전)을 새 사전등록에 **다시** 등재해야 하며, 이번엔
   범위를 typed-scope split 이후의 새 prompt surface 전체로 갱신해야 한다.
   원문은 `PREREGISTRATION.md` §11.2a에 그대로 남아 있으니(이력 텍스트로
   보존됨) 새로 쓸 필요 없이 그 문안을 새 문서로 옮기면 된다.
9. **repaired preregistration 갱신** — post-result amendment disclosure
   포함(§15).
10. **독립 의미 리뷰 재실행 + 리뷰어 전원 freeze 승인.**

완료 후에도 **최초 40 trial과 병합하지 않는다**(§15) — 새 코호트, 새 cohort id.

세션 2(별도)가 진행한 N=16 사후 코호트의 미포착 결함 3건(사전등록 코드
게이트 부재·`predecessor_cohort` 미해소·arm 간 키 순서 비대칭)은
`concept-gate-owl-wt/experiments/2026-08-04_owl_entailment_contract_shape/OPERATIONS_LOG.md`
참조 — 이 실험(H1a)과 무관하니 여기서 처분하지 않는다.

> **인수인계 도달성 감사기** (2026-08-08 반입): 새 세션이 이 문서에서
> 도달 가능한 파일만으로 작업을 재개할 수 있는지 기계적으로 잰다.
> [`scripts/handoff_reachability.py`](../scripts/handoff_reachability.py)
> `python3 scripts/handoff_reachability.py --ref <base>` — 링크 도달성만
> 재며 handoff가 **이해 가능한지는 재지 않는다.** 양방향 테스트:
> [`test_handoff_reachability.py`](../test_handoff_reachability.py) —
> recall(깨진 링크는 보고)과 precision(깨진 *언급*은 보고 안 함)을 고정한다.

---


## 11. 코호트 실행 완료 — 3/3 class 인증 (2026-07-28, `b2a4181`)

표면 재설계(v2 마이그레이션 + 계약 문구 §4/§5 + 동결)와 코호트 동결·실행이
**전부 끝났다.** 아래는 그 경위와, 실행 중 발생한 두 가지 실측(세션 한도,
실질 검증 결과)의 기록이다.

### 11.0 G1(표본 크기) 확정 및 실행 결과

동결 코호트는 원래 **N=7/5/5(17 trial)** 였는데 사전 등록 Stage 1은
**N=10/cell**이고 판정 밴드가 그 N에 맞춰 보정돼 있어(프로토콜은 이 worktree에
없고 메인 체크아웃 `../concept-gate-taxonomy/docs/experiment_screening_protocol.md`에
있음), **ⓐ N=10/cell로 재동결**했다(`737405a`). 재동결은 결정론적이라
`rendered_prompt_sha256`은 세 fixture 모두 이전과 바이트 동일 — trial id만
늘어났다.

30 trial 실행 결과(`b2a4181`):

```
E24-F-01 (sufficient_consistent)  10/10 clean  screened_PASS
E24-F-02 (sufficient_repairable)  10/10 clean  screened_PASS
E24-F-03 (insufficient)           10/10 clean  screened_PASS

certified 3/3 classes. protocol_deviation: 없음 (N=10 정합)
conformance_violations: 0   schema_violations: 0  (전체 30 trial)
```

**실행 중 발생한 일 — 세션 사용 한도(전송 실패, trial 데이터 아님)**:
30 trial을 한 번에 실행했을 때 22개가 `"You've hit your session limit ·
resets 11:40pm (Asia/Seoul)"`로 실패했다. 이것은 **컨텍스트 윈도우 토큰과
별개인 API 세션 사용량 한도**이며, `agents_error` 카운트가 0이 아니고
`subagent_tokens`는 정상적으로 소비된 상태였다(8개는 실제로 성공). 실패한
22개를 trial 데이터로 기록하지 않고, 리셋 시각을 확인(`date` 명령으로
경과 확인)한 뒤 **그 22개만** 별도 batch로 재실행해 22/22 성공, 두 batch를
병합해 30/30을 확보했다. 전체를 다시 30개 도는 대신 실패분만 재시도한 것은
이미 성공한 8개를 버리지 않기 위함이다.

**검증은 verdict 문자열 일치만으로 끝내지 않았다** — legacy 유출 실행도
7/7·5/5·5/5로 "clean해 보였던" 전례가 있어, 같은 착시를 피하려 30 trial
전수를 실질 확인했다:

- E24-F-02(가장 어렵게 확보한 class): **10/10 전부**가 필러 feature `갑종`을
  `insufficient`로 정직하게 표시하며 `바퀴`만 `structural_composition`으로
  repair — `contract_prompt.md` 규칙 5가 요구하는 정확한 패턴이자, `e03f74a`의
  채점기 수정이 지키려 한 바로 그 판정. `repaired_concepts`는 `갑종`을
  원본 타입 그대로 보존해 제약 4(repair는 입력 전체를 실어 나른다)를
  구조적으로 충족했다.
- E24-F-03: 표본 확인한 trial 전부가 evidence를 `direct_support`가 아니라
  `indirect_context`로 분류 — 구현 서술일 뿐 온톨로지적 성격을 명시하지
  않는다는 규칙 2의 판별을 정확히 적용했다.

### 11.1 지난 세션에 실행하지 못했던 이유 (둘 다 해소, 이번 세션에 실행 완료)

1. **agent registry는 세션 시작 시점에 고정된다.** trial subject
   `e2.4-contract-decider`를 세션 도중 만들었더니 `Agent`·`Workflow` 양쪽에서
   `agent type not found`가 났다. → **해소됨.** 정의는
   `~/.claude/agents/`와 실험 폴더 양쪽에 설치·커밋돼 있고 다음 세션은 인식한다.
2. **structured-output 스키마 크기 한계.** `evidence_contract_v1`을
   `agent(..., {schema})`로 넘기면 전송 계층이 "output schema too large to
   classify safely"로 거부한다(설명 제거 후 4.7KB에서도 동일). → **우회 완료.**
   출력 계약을 **trial subject의 system prompt**로 옮겼다. 동결 프롬프트는
   "출력은 ... evidence_contract_v1 schema를 따른다"고만 하고 필드를 하나도
   나열하지 않으므로 `rendered_prompt_sha256`은 그대로다.

   이 이동이 §6 해시 목록의 구멍을 드러냈다 — output schema와 system prompt는
   모델이 보는 표면인데 아무도 해싱하지 않았다. `system_prompt_sha256`과
   `presented_schema_sha256`을 추가했다.

   ⚠️ **크기 한계값은 미상이다.** 이분 탐색을 시도했더니 안전 분류기가
   "분류기 우회 시도"로 차단했다 — 기계적으로 타당한 지적이라 탐침을 중단했다.
   스키마가 더 커지면 같은 벽에 부딪힌다.

**하지 않은 우회 (기록)**: 이미 등록된 `e2.2-decider`(`tools: []`)로 대체할 수
있었지만 쓰지 않았다. 그 system prompt는 E2.2용이라 **이 payload에 존재하지
않는 키 `input_concepts`**를 지목한다. 인증 실행의 trial subject를 다른 실험
것으로 바꾸는 것은 이 실험을 0 class로 되돌린 바로 그 종류의 표면 오염이다.
기다리는 편이 쌌다.

### 11.2 그 뒤 채점기에서 결함 2건을 발견해 수정했다 (`e03f74a`)

**동결만 믿고 실행했다면 잘못 채점됐다.**

1. **채점기가 계약이 명령한 행동을 위반으로 집계.** `conformance()`가 5단계
   sufficiency 절차를 **packet 전역**으로 1회 도출해 **모든 per-feature 판정**과
   대조했다. 5단계는 본래 feature 하나의 `selected_type`을 정하는 절차다.
   `contract_prompt.md` 규칙 5는 evidence 없는 필러 feature를 insufficient로
   표시하라고 **지시**하는데, 그 지시를 따른 판정이 위반으로 잡혔다:
   ```
   돌체.갑종: sufficiency=insufficient but the trial's own audit
              yields sufficient under the 5-step procedure
   ```
   인증이 `clean_rate` 기준이므로 **E24-F-02가 0/5로 떨어질 예정이었다** —
   다섯 번 시도해 겨우 확보한 class다. → `feature_judgments[].evidence_ids`로
   부분집합을 뽑아 **feature별** 도출로 수정.
   테스트가 못 잡은 이유: 케이스 8개가 **전부 `feature_judgments` 1개**였다.
2. **`_score.py`가 `record()`의 `schema_violations`를 안 읽었다** — 구조적으로
   무효한 출력이 verdict 문자열만 맞아 인증에 집계될 수 있었다. → `clean`을
   **verdict + 스키마 유효 + 계약 준수** 3중 논리곱으로.

함께 추가: `semantic_constraints` #4·#6 검사(미구현이었다), `direct_support`인데
`supported_type`이 null인 경우, `sufficient`인데 `selected_type`이 step 3 승자와
불일치하는 경우.

### 11.3 실행 절차 (참고용 — N=10/cell 코호트에 실제로 적용해 성공함)

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

# 0. 동결본이 현재 파일과 일치하는지
python3 -m pytest -q .          # 118 passed

# 1. (ⓐ를 택했다면) COHORT 상수 수정 후 재동결
python3 _cohort.py agent        # 스키마가 두 곳에 있으므로 생성기를 먼저
python3 _cohort.py freeze       # stale이면 중단한다
#    -> 커밋 후 실행 (동결은 실행 전에 커밋돼야 한다)

# 2. trial 실행. 각 trial = agentType 'e2.4-contract-decider'(tools: [])에
#    cohort_prompts.json의 rendered_prompts[fixture_id]를 그대로 전달.
#    trial id는 cohort_prompts.json의 trials[].trial_id.
#    결과를 {trial_id: <파싱된 JSON 객체>}로 trials_raw.json에 저장.

# 3. 기록 — 표면 drift 재확인 + 스키마 위반 표시(제거하지 않음)
python3 _cohort.py record

# 4. 채점
python3 _score.py
```

동결 이후 fixture나 계약 문구가 바뀌었다면 `record`가 **거부한다.** 그때는
코호트가 무효이므로 `freeze`부터 다시 한다.

**전송 계층 실패를 데이터로 기록하지 마라**: workflow 결과의 `agents_done: 0`,
`subagent_tokens: 0`, 수십 ms 소요는 **아무것도 모델에 도달하지 않았다**는
뜻이다. 지난 세션에 17 agent가 45ms에 전멸한 적이 있다.

**변종 하나 더(2026-07-28 실측)**: `subagent_tokens`가 정상 소비되고 일부
trial은 실제로 성공했는데, 나머지가 `"session limit, resets HH:MMpm (TZ)"`로
실패하는 경우 — 이것도 전송 실패이지 데이터가 아니다. 전체를 재실행하지 말고,
**리셋 시각을 확인한 뒤 실패한 trial id만** 별도 batch로 재실행해 이미 성공한
것과 병합한다.

### 11.4 채점 규약 (사전 등록됨, 실행 전에 읽어라)

- `decision` 일치가 아니라 **`contract_verdict` 일치**로 채점한다
  (`OPERATIONS_PLAN.md` Phase 6). `PROBLEM_2` §5.1에서 `decision`은 5/5
  안정인데 `contract_verdict`는 4-1로 갈렸다 — decision만 보면 불안정한 판정이
  만장일치로 보인다.
- 인증은 **`clean_rate`** 기준: 기대 verdict에 **스키마를 지키고 계약을 어기지
  않고** 도달한 비율. `conformance()`가 trial 자신의 `evidence_audit`로 5단계를
  다시 돌려, 자기 감사표가 자기 결론을 뒷받침하지 않는 trial을 잡아낸다.
- 밴드는 사전 등록 3구간(`screened_PASS` / `ambiguous` / `screened_FAIL`).
  중간 구간은 실패가 아니라 **Stage 2 증분 지시**다.
- **최대 유효 커버리지 3 class**, 실행 전 인증 **0 class**.
- `legacy_leaky.md`의 7/7·5/5·5/5는 인증 근거가 아니다. 새 숫자를 그것과
  비교하지 마라 — "재채점"도 "재현"도 아닌 **clean rerun cohort**다.

### 11.5 산출물

| 파일 | 언제 | 내용 |
|---|---|---|
| `cohort_prompts.json` | 커밋됨 | 모델이 받을 정확한 바이트 + trial당 해시 8종(+`builder_commit`) |
| `e2.4-contract-decider.md` | 커밋됨 | trial subject(`tools: []`), 스키마는 생성물 |
| `oracle_manifest.json` | 커밋됨 | 숨은 오라클. 빌더는 접근하지 않는다 |
| `trials_raw.json` | 실행 후 | `{trial_id: 출력}` |
| `trials.json` | `record` 후 | manifest + 출력 + 스키마 위반 |
| `cohort_score.json` | `_score.py` 후 | class별 clean_rate, 밴드, escalate cell, `protocol_deviation` |

---


