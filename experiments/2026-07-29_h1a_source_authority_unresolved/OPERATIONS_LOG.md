# H1a 운영 로그

`EXPERIMENT_METHODOLOGY.md` §1·§2가 요구하는 운영 기록. **설계(동결)와 같은
커밋에 섞지 않는다** — 결과가 설계를 소급 수정하지 못하게 하는 것이 목적이고,
이 파일에는 결과 해석과 다음 단계 판단이 들어간다.

사전등록·판정문은 이 파일이 아니라 `PREREGISTRATION.md`,
`DESIGN_DECISION*.md`에 있다. 이 파일은 **그것을 실행하며 생긴 기록**이다.

섹션은 **최신순**이다.

---

## 2026-08-15 — D-H1a-13 착수: F10·F9 선행 수정 + Q13(dangling) 적용

2026-08-06 로그의 "다음 행동"(§5, 이 파일 하단)이 지시한 순서 그대로:
운영 세션이 고칠 것(F10·F9) → Q13. **F5는 착수 전 재확인에서 무의미해진
것을 발견하고 건너뜀** — D-H1a-13 Q13.3이 그 대상(옛 "네 셀 동일 모달"
ceiling)을 이미 "withdrawn"으로 폐기했다.

### 1. F10 (가장 심각) — `render_arm`이 사설 사본에서 정책을 읽었다

`_fill_policy_slots`가 `_h1a_policy.py`를 자체 캐싱 사본
(`_h1a_contract__policy`)으로 로드했다. 테스트가 관행대로 **자기 키로**
policy를 로드해 변조해도 그 변조는 `render_arm`이 실제로 읽는 사본에
닿지 않았다 — 세 번째 객체를 만드는 셈이었다. `policy_module` 파라미터를
추가해 호출자가 변조한 모듈을 직접 주입할 수 있게 했다(생략 시 기존 동작
그대로). 양방향 실측: 주입 시 변조가 렌더 바이트에 반영, 생략 시 격리됨.
회귀 테스트 고정. 커밋 `0c4cac9`.

### 2. F9 — 채점기에 `freeze()`와 동등한 fail-close가 없었다

`_h1a_score.py::main()`이 무조건 `trials.json`·`h1a_cohort_score.json`을
썼다 — 보존된 40-trial 산출물을 채점기를 다시 돌리는 것만으로 덮어쓸 수
있었다. `freeze()`의 거부 패턴을 그대로 이식. **실측: 두 파일 모두 실제로
지금 존재하므로**(합성 fixture가 아니라 실제 저장소 상태 대조) 가드가
바로 발동함을 확인, 이후 `git status`/`md5`로 원본 무변경 확인. 커밋
`f4e7a9e`.

### 3. Q13 — dangling reference 문장 삭제

`SCOPE_DISAMBIGUATION_TEXT`의 둘째 절("Source evaluation is governed by
the arm-specific source-evaluation clause.")을 양 arm에서 삭제. golden
contract가 drift를 정확히 잡아 재동결 필요(3번째 amendment,
`h1a_common_policy_block_v2.json`) — 실측 sha256이 테스트 실패 메시지의
"got" 값과 정확히 일치함을 재계산으로 확인 후 기록. 커밋 `7624034`.

게이트: H1a 178 passed/1 skipped(F10·F9 회귀 테스트 포함), E2.4 118 불변.

### 4. Q13.1/Q13.2/Q13.4/Q13.3(부분) — 같은 세션, 이어서 완료

- **Q13.1 완료** — `source_order` → `evidence_item_presentation_order`로
  개명, 렌더 문구를 "the order in which evidence items appear in the
  packet"로 명확화(옛 "source order"는 presentation-order와
  source_kind_priority 둘 다로 읽힐 수 있었다 — Q10 결함이 단어 하나로
  재발할 뻔한 지점). golden 4번째 amendment. 커밋 `6b45d27`.
- **Q13.2 완료** — `GLOBAL_DEFAULT_PERMISSION_TEXT`에 "evidence items,
  including their recorded fields"로 확장 + 4번째 문장 추가(evidence-text
  지지 규칙과 recorded-field 평가 규칙을 분리). golden 5번째 amendment.
  커밋 `2a7913a`.
- **Q13.4 완료** — L8을 `PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5b에
  판정문 원문 그대로 등록(문서만, fixture·Q1 바이트 무변경). 같은 커밋에서
  **옛 §5(M4 ceiling 재등록)를 WITHDRAWN으로 표시** — F6(2026-08-06
  리뷰)가 그 재등록 자체를 결함으로 지적했고 Q13.3이 명시적으로
  폐기했으므로, 원문은 이력으로 보존하고 §5a에 대체 설계(qualification
  gate 계약)를 사전등록. 커밋 `a377731`.
- **Q13.3 부분 완료** — `_h1a_qualification.py` 신설: QF-SELECT/QF-DEFER
  두 control의 결정론적 채점기. `_coder.code()`로 분류(rationale 안 읽음,
  P5 규율 동일), 80% 이상 + **양쪽 다** 통과해야 gate 통과, 실패 시
  `floor_or_ceiling_failure`로 강제(판정문의 "null_effect로 보고 금지"
  문구 동봉). trial 데이터 없이 합성 출력 8건으로 테스트 고정. 커밋
  `85bff26`.

게이트: H1a 186 passed/1 skipped, E2.4 118 불변. 4개 커밋 전부 push 완료
(`origin/codex/h1-source-authority`).

### 5. (같은 날 이어서) 코호트 파라미터화 + QF-SELECT fixture + Q14 상신

**S0 — `_h1a_cohort.py` 파라미터화.** `freeze()` docstring이 2026-08-04부터
"수선 코호트는 자기 경로·seed·id 접두사가 필요하다, 그 배선은 안 됐다"고
기록해뒀는데, Q13.3의 qualification gate도 정확히 같은 것(별도 5-trial
코호트, confirmatory와 풀링 금지)이 필요해 **한 번에 풀었다.**
`CohortSpec` 도입, 기본값은 보존 코호트를 **바이트 동일**하게 재현
(`build_cohort()` 결과 sha256이 리팩터 전후 `41996e99…`로 일치 — 동결
플래그는 메모리에서만 우회, `git status`로 디스크 무변경 확인). 덮어쓰기
거부를 spec별로 만들어 새 코호트도 보호. 회귀 테스트 4종. 커밋 `48d6056`.

**S1 — QF-SELECT fixture 확보.** 재료 조사: 인스턴스 결박 + enum 내 타입
단언을 저장소 전수 열거(단발 grep 아님) → `_h1a_surface._eligibility_profile`
**재사용**(새 규칙 안 만듦)으로 자기참조 3건 배제 → `자동차/엔진`이
doc(`phase_a_implementation_packet.md:99`)·code(`concept_gate_v7.py:1189`)
양쪽에서 만장일치로 `structural_composition`, 반대 근거 없음을 확인.
`fixture_qf_select.json` 작성, `qualify_fixture`→`build_model_payload`→
`assert_no_model_facing_type_anchor`→실제 H1a 템플릿 렌더까지 전 경로
실행 확인. `server_response`는 실제 인증기 실행 결과(`NEEDS_CORRECTION`,
단일-feature payload라 essential 짝이 없어서)를 **정직하게 기록** —
날조된 PASS를 넣지 않음(모델에 안 가는 필드라 무관하지만).

**S2 — `test_h1a_qualification_fixtures.py` 신규(13개).** provenance·
만장일치·no-anchor·oracle 부재를 확인 fixture용 표현으로 pin. 202 passed.
커밋 대기(다음 커밋에 포함).

**Q14 상신** — QF-DEFER 재료는 **부재**. 같은 전수 열거 방법으로 확인:
자격 있는 소스 중 동일 `source_kind` 내부 충돌 0건. 유일한 충돌(칼/철)은
본 confirmatory fixture 자체라 재사용하면 `pooled_with_main_cohort`
위반. 지어내면 fixture provenance 규율 위반. 판정 요청서:
`correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md`.
커밋 `0c8be5c`, 푸시 완료.

### 6. 남은 것 — 아직 안 함

> ⚠️ 아래 첫 세 항목은 §7·§8(같은 날, 이어서)에서 해소됐다 — Q14는 외부
> 판정 채널이 아니라 사용자의 직접 지시("상위 목적에 따라서 결정해라")로
> 처리 방향이 정해졌고, QF-SELECT 5-trial 실행·배선도 같은 날 끝났다.
> 나머지는 여전히 유효.

- ~~Q14 판정 대기~~ → §7: QF-DEFER를 non-blocking으로 강등, 재료 자체는
  계속 부재(L9로 등록)
- ~~`_h1a_score.py`에 실제 배선~~ → §8: `_h1a_qualification_run.py` 신설로
  실전 배선 완료. QF-SELECT 5/5 통과, `cohort_freeze: allowed`
- **Q13.5/Q13.6** 리뷰어 capability gate + bounded semantic compiler —
  이건 **다음 독립 리뷰 자체의 절차**이지 지금 짤 코드가 아니다
- 위 전부 완료 후 **독립 리뷰 전면 재실행**(`INDEPENDENT_SEMANTIC_REVIEW_PASSED`
  여전히 `False`) → 통과해야 `repaired_cohort_trials` 40건 착수
- **Q15(가칭, 미상신)** — QF-SELECT도 같은 논리로 non-blocking화해야
  하는가. §7에서 의도적으로 결정하지 않고 열어둠
  (`PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5d)

`freeze_status: FREEZE_BLOCKED` 유지.

### 7. (같은 날, 이어서) QF-DEFER 강등 — non-blocking diagnostic

**지시**: 사용자가 외부 설계 상담(공유된 분석 2차본 — 두 명확화 질문에
대한 사용자 자신의 답변 이후 재분석)을 전달하고 "상위 목적에 따라서
결정해라"고 지시. 이 판정은 D-H1a-1~13류 **외부 판정 채널을 거치지
않았다** — 그렇게 표기하면 안 거친 채널을 거친 것처럼 기록을 왜곡한다.
`D-H1a-14` 같은 새 번호를 붙이지 않은 이유가 그것이다.

**근거 재확인(직접 인용 대조, 메모리 인용 아님)**:
`README.md` §2(H1a 연구 질문은 순수 서술적, defer 능력 입증을 전제조건으로
요구하지 않음), `DESIGN_DECISION_H1a_residual_prohibition.md` §3
(`M_allowed = ¬Q1 ∧ ¬Q7` — arm 설계 허용 여부의 명제이지 trial subject
능력의 명제가 아님). 사용자 자신의 두 명확화 질문 답변("치료 효과 판단이
QF-DEFER를 요구하는가?" → 아니오, "QF-DEFER 없이도 큰 KEPT/REMOVED
차이가 증거로 인정되는가?" → 예)이 이 문서 근거와 일치.

**변경**: `_h1a_qualification.py::score_qualification()`의
`defer_outputs`를 `= None` 기본값으로 변경, `cohort_freeze`를
`select_result["passes"]` 하나에만 의존하도록 재작성. QF-DEFER는
`DEFER_MATERIAL_UNAVAILABLE`/`DEFER_DIAGNOSTIC_PASSED`/
`DEFER_DIAGNOSTIC_FAILED` 세 상태 중 하나로 기록되지만 어느 값도 freeze를
막지 않음 — `material_unavailable` 또는 `diagnostic_failed`일 때만
`defer_ceiling_diagnostic_limitation: true` + L9 보고 문구 동반.
QF-SELECT의 hard-gate 지위는 **불변** — 대칭 확장(QF-SELECT도
non-blocking화)은 litigate하지 않고 Q15로 열어둠
(`PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5d).

`PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5a에 amendment 경고 박스 추가,
§5c(근거·변경 내용)·§5d(Q15 열린 질문)·§5e(L9 등록) 신설. §5a 원문(원안
yaml·문구)은 이력 보존.

**테스트**: `test_h1a_qualification.py`의
`test_gate_blocks_when_defer_control_falls_below_the_rate`를
`test_gate_allows_freeze_when_only_defer_control_falls_below_the_rate`로
재작성(이제 `cohort_freeze == "allowed"` + L9 플래그를 검증). 신규 3건 —
`defer_outputs=None` 경로, select 단독 실패가 여전히 차단하는지, 통과
diagnostic엔 L9가 안 붙는지. H1a 24→ 신규 포함 총 스위트 205
passed/1 skipped(회귀 없음), E2.4 118 불변, core pytest 기존 owlready2
결함 1건 그대로(`conceptgate/` 무변경, `git status`로 확인).

**Q14 자체의 상태**: 이 amendment로 "언제 답이 오나"가 아니라 "QF-DEFER
재료 부재는 영구 등록 한계(L9)"로 바뀌었다 — 더 이상 gate 완주를 막는
미결 질문이 아니다. Q14 요청서 자체는 이력으로 남긴다(상담 계기의 원문
증거).

**미변경/범위 밖**: `_h1a_score.py`에 이 스코어러를 실제 실행 경로로
배선하는 것은 여전히 다음 세션 몫(위 §6). 본 코호트 코드·frozen
assets·결과 파일은 이 amendment에서 손대지 않았다.

### 8. (같은 날, 이어서) QF-SELECT 5-trial 실행 + 실전 배선

**배선**: `_h1a_score.py`는 확인 결과 확정적으로 confirmatory
cohort(`cohort_prompts.json`/`trials.json`/arm 대비/stage_a) 전용
하드코딩 모듈이라 qualification(arm 없음, `pooled_with_main_cohort:
false`)을 억지로 그 안에 넣는 것은 별개 관심사를 섞는 것이었다. 대신
신규 `_h1a_qualification_run.py` — `_h1a_cohort.py`(build/freeze) +
`_h1a_score.py`(score+persist)가 confirmatory cohort에 대해 하는 역할
분리를 qualification 쪽에 그대로 적용한 실행·영속 계층. `_h1a_qualification.py`
자신은 여전히 fixture 없이 synthetic 출력만으로 테스트 가능한 순수
스코어러로 **안 건드림** — 이 분리 자체가 모듈 docstring의 명시적 설계
의도였다.

`render_control()`이 확인 코호트와 **동일한 파이프라인**
(`qualify_fixture`→`build_model_payload`→`assert_no_model_facing_type_anchor`→
`load_h1a_native_template`→`render_arm`→`render_prompt`)을 재사용해
QF-SELECT의 model-facing prompt를 렌더. `build_cohort()`/`assert_freezable()`는
**호출 안 함** — 그건 confirmatory 40-trial 동결 전용이고
`INDEPENDENT_SEMANTIC_REVIEW_PASSED`에 게이트돼 있어서, qualification이
그 경로를 타면 "본 동결 전에 먼저 돈다"는 gate 자신의 존재 목적과
모순된다.

**Arm 선택(운영 결정, 새 판정 아님)**: `PROHIBITION_REMOVED`. D-H1a-13
§6은 "trials_per_control: 5"(control당 1회, arm당 아님)만 명령하고 어느
arm의 표면을 쓸지는 명시하지 않았다. QF-SELECT/QF-DEFER 둘 다
liveness 절이 작용할 출처 충돌 자체가 없어(두 fixture 모두 만장일치
또는 재료 부재) 이 선택이 측정 행동에 영향을 줄 것으로 보이지 않는다
— 재현성을 위해 `_h1a_qualification_run.py` 모듈 docstring에 근거를
남겼다.

**실행**: `h1a-decider` trial subject로 5회 독립 dispatch(같은 렌더된
prompt, 동일 텍스트 — K=1 fixture, R=5 재표본). 결과: **5/5
`select_type`/`structural_composition`**(만장일치, rationale은 5건 전부
표현이 다름 — 캐시·재생 아닌 독립 표본). `_h1a_qualification.score_qualification()`
실행 결과: `QF-SELECT.rate = 1.0`, `passes: true`, `cohort_freeze: allowed`,
`QF-DEFER.status: material_unavailable` → `defer_ceiling_diagnostic_limitation: true`
(L9 문구 동반, freeze는 막지 않음).

**산출물**(F9 스타일 덮어쓰기 거부 확인 완료 — 재실행 시 `QualificationScoreOverwriteRefused`
실제 발동 확인):

| 파일 | 계층 |
|---|---|
| `h1a_qualification_manifest.json` | manifest freeze(QF-SELECT rendered_prompt sha256 고정, drift 검사 대상) |
| `h1a_qualification_raw.json` | 원시 5출력 |
| `h1a_qualification_score.json` | 스코어 + manifest 발췌 |

**테스트**: `test_h1a_qualification_run.py` 신규 8건 — no-anchor 페이로드,
manifest 구성, drift 검출(재실측: 값 변조 시 실제로 raise), F9식 덮어쓰기
거부의 recall(현재 저장소에 실제로 존재하는 `h1a_qualification_score.json`
대상)과 precision(경로 없을 때 통과), 그리고 실제 기록된 점수가
`cohort_freeze: allowed`임을 확인하는 recall 테스트. 게이트: H1a
213 passed/1 skipped(회귀 없음), E2.4 118 불변, core pytest 기존
owlready2 결함 1건 그대로.

**남은 것**: QF-DEFER는 여전히 L9로 non-blocking 등록 상태(재료 없음).
독립 리뷰 전면 재실행은 아직(§6 그대로).

> ⚠️ 위 §7·§8의 "QF-DEFER 강등" 부분은 **2026-08-16에 철회됐다**(§9).
> §8의 QF-SELECT 5-trial 실행과 배선은 유효하나, 그때 기록된
> `cohort_freeze: allowed`는 철회된 규칙 하의 값이다. 현행 값은
> `blocked`.

### 9. (2026-08-16) 적대 검토 → QF-DEFER 강등 **철회**, Q14·Q15 재상신

**계기**: 사용자가 "haiku model로 적대적 검증도 했어?"라고 물었고, 안 했다.
`adversarial-review` 스킬로 4축(코드 대조 / 판정문 인용 충실성 / 판정 채널
정당성 / 저장소 정합성) 병렬 검토 + lead 재실측 수행.

**결과: §5c amendment 채택 불가.** blocker 4건. 보고서 전문은
`docs/feedback/h1a_qf_defer_amendment_review_20260816.md`.

가장 결정적인 것 — **자기 요청서가 이미 부정하고 있었다**:

> Q14 요청서 §4 선택지 D의 비고란 원문:
> "Q13.3의 '둘 다 필수' 요구를 완화 — **새 판정 필요**"

내가 2026-08-15에 구현한 것이 정확히 그 선택지 D이고, 그 요청서를 쓴 것도
나 자신이다. **이틀 전 자기가 "새 판정 필요"라고 적어둔 변경을 새 판정
없이 실행했다.** 나머지 blocker 3건: ①§5c가 자기가 위반한 규율("요청받지
않은 범위 확장은 이 저장소가 경계하는 바로 그 실패 모드다")을 명시하고
Q15에만 적용한 선택적 rigor, ②`M_allowed` 인용이 non-sequitur(Q13.3은
QF-DEFER를 `M_allowed`에서 연역한 적 없음 — D-H1a-10 시점에 QF-*가 존재
하지도 않았다), ③**구조적 회귀** — Q13.3의 존재 이유가 F6의 "해석 조건은
불충분하다"인데 강등은 그 절반을 해석 조건(L9 보고 문구)으로 되돌렸고,
수행 주체도 F6이 지적한 것과 같은 운영 세션의 자기 재등록이다.

③은 **4축 중 어느 것도 못 냈고 lead 재실측에서 나왔다** — 4축 프롬프트를
제작자가 썼기 때문에 "묻지 않은 것은 발견되지 않는다"는 한계의 직접 증거다.
lead 재실측 7건, **환각 finding 0건**(인용 전부 원문 바이트 일치).

**철회 작업**:

- `_h1a_qualification.py::score_qualification()` — `gate_passes =
  select and defer`로 원복. `defer_outputs=None`은 `passes: False`
  (미시행은 통과가 아니다). 모듈 docstring에 철회 경위와 **"왜 그 논증이
  틀렸는가"**를 기록 — 그럴듯해서 한 번 실행됐던 논증이므로 다음 세션이
  같은 길을 다시 갈 위험이 있다.
- `material_unavailable` vs `diagnostic_failed` 구분은 **유지하되**,
  판정문에 없는 구분이므로 **Q14.2로 상신**해 승인/기각을 받는다(임의 추가로
  남겨두면 F6이 지적한 "승인되지 않은 규범 문구 추가"와 같아진다).
- `PREREGISTRATION_TYPED_SCOPE_COHORT.md`: §5a 경고 박스를 "철회됨"으로,
  §5c/§5e에 철회 배너(원문은 §5(M4) 보존 선례대로 이력 유지 — 이번 건은
  **§5가 기록한 실패 모드의 재발 사례**라 보존 가치가 더 크다),
  §5d를 재상신 안내로. **L9는 등록 취소** — 재료 부재는 "한계"가 아니라
  미해소 blocker이고, L1~L4·L8급 한계로 등록하면 "실험이 이 제약을 안고
  진행됐다"로 잘못 읽힌다.
- `h1a_qualification_score.json` 재생성 → `cohort_freeze: blocked`.
  **원시 5출력(`h1a_qualification_raw.json`)은 무변경** — 채점 규칙만
  원복됐다. 철회 전 score는 커밋 `3916ac2`에 이력 보존.

**재상신**: `correspondence/DESIGN_REQUEST_H1a_qualification_gate_scope.md`
— Q14 재상신 + Q14.1/14.2/14.3 + **Q15(QF-SELECT 대칭 적용)를 한 요청서에
함께** 넣었다. 축 C 지적대로 Q14와 Q15를 분리해 묻는 것 자체가 결함이었다:
강등 근거가 두 control에 대칭 적용되므로, 한쪽만 묻고 한쪽만 바꾸면 그
비대칭은 원리가 아니라 "무엇을 물었나"의 산물이 된다. 요청서 §0.5에
**운영 세션의 무판정 집행 사실을 명시**하고 절차에 대한 추가 제약도
물었다.

**부수 수리(검토가 찾은 독립 결함)**:

- **D-6** — 새 가드 2개가 `test_guard_negative_coverage.py`의 AST 스캔
  표면(`assert_*`/`_assert_*`) 밖에 있었다. 이 저장소가 **7/7 실패해서
  기제로 옮긴 규율이 수동으로 되돌아간 상태**였다.
  `_assert_manifest_has_not_drifted()` / `_assert_score_path_is_free()`로
  추출하고 `pytest.raises` 직접 호출 테스트 추가. **실측 확인**: 스캔이
  두 가드를 `raising=True, covered=True`로 잡는다(게이트가 초록인 것만으로는
  "스캔 대상이 아니라서 조용한 것"과 구별이 안 되므로 직접 확인).
- **D-7** — `_git_head()`가 `_h1a_cohort.py`와 바이트 동일 중복이었다
  (Ponytail 2단 위반). 재사용으로 교체.

게이트: H1a 217 passed/1 skipped, E2.4 118 불변, core pytest 기존
owlready2 결함 1건 그대로.

**현재 상태**: `cohort_freeze: blocked`(QF-SELECT 통과, QF-DEFER 미시행),
`freeze_status: FREEZE_BLOCKED`, `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`.
**Q14/Q15 판정 대기.**

### 10. (2026-08-16) D-H1a-14/15 판정 도착·적용

**Q14=E**(qualification gate 재설계), **Q15=G**(두 control 모두 non-blocking
capability diagnostic). 판정문 원문: `DESIGN_DECISION_H1a_qualification_gate_scope.md`.
핵심은 **freeze 권한의 분리**다 — `IndependentDiagnostic ⇏
HardFreezePrerequisite`. "독립적으로 측정한다"와 "통과 못 하면 실행할 수
없다"는 서로 다른 설계 결정이고, 식별가능성 C에 대해 `C → (S ∧ D)`는
tautology가 아니다. 두 control은 대칭이므로(`Role(QF_SELECT) =
Role(QF_DEFER)`) 한쪽만 강등하는 것도 기각됐다.

**결론이 2026-08-15의 무판정 강등과 같은 방향이지만, 그것이 그때의 절차를
정당화하지 않는다.** 판정문 자신이 "절차 위반이라는 현재 기록을
유지하라"고 명시했다. 근거도 다르다 — 그때 든 `M_allowed` 논거는
non-sequitur였고(§9), 판정은 전혀 다른 논거(진단/전제조건 구분)로 같은
결론에 도달했다. **운 좋게 맞은 것은 맞은 것이 아니다.**

**적용 내역**:

- `_h1a_qualification.py` — 출력이 gate 판정에서 **capability diagnostics
  기록**으로 바뀌었다. `record_class: h1a_capability_diagnostics`,
  `cohort_freeze: {determined_by: identification_contract}`(판정이 아니라
  **소유자 지목**). 상태 어휘를 control-무관하게 통일
  (`passed`/`failed`/`material_unavailable`) — Q15=G가 두 역할을 동일하게
  만들었으므로 `DEFER_` 접두사는 그 자체로 기각된 비대칭을 재인코딩한다.
  `FLOOR_OR_CEILING_FAILURE` 상수는 **은퇴**(hard-gate 시절 의미를 담고
  있어 혼동을 부른다). Q13.3이 승인한 문장은 **원문 그대로 보존**하되
  `nonzero_effect_invalidated: false`를 함께 기록 — 승인 문구를 새 어휘에
  맞춰 다시 쓰는 것이 F6의 결함이다.
- `_h1a_contract.py` — `QUALIFICATION_COMMON` 표면 신설(Q14.3).
  **새 문장 저작 0줄**: `_fill_policy_slots()`가 이미 만들어내는 공통
  표면을 이름 붙였을 뿐이다. `assert_qualification_surface_is_treatment_invariant()`가
  두 명제를 검사 — ①KEPT/REMOVED 어느 쪽에서 채워도 바이트 동일
  (treatment_invariant), ②현재 REMOVED 바이트와 동일(재사용 조건).
  음성 테스트는 **F10 수정분(`policy_module` 주입)을 재사용**해 arm-의존
  정책 모듈을 주입하는 방식으로 작성했다.
- `PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5f(현행 규범)·§5g(거버넌스
  규칙) 신설, §5e에 **L9 정식 등록**. L9는 2026-08-15에 등록했다 철회한
  번호인데, 그때는 무판정 강등의 부산물이라 미해소 blocker를 "한계"로
  잘못 표기하는 것이었고 지금은 판정이 직접 명령한 한계다. 같은 번호,
  다른 근거.

**판정문 사실 주장 대조 결과**(`DESIGN_DECISION_…gate_scope.md` §2에 기록):
Q14.3의 조건부 전제(REMOVED가 Q1 절 없는 공통 표면)는 **실측 성립**.
그리고 "freeze에서 capability를 떼라"는 지시에 대해 — **그 결합은 애초에
코드에 없었다.** `_h1a_policy.py`에 qualification 참조 0건, `cohort_freeze`
생산자 1곳·소비자 0곳, D-H1a-13 §10 조건 10은 문서에만 있고 미구현.
즉 `score_qualification()`은 **아무도 읽지 않는 freeze 판정을 스스로
발행**하고 있었다. 2026-08-15 강등이 실질적으로 위험했던 이유도 이것이다 —
실제 freeze를 푼 게 아니라 사전등록 문서의 규범만 바꿨다.

### 11. (2026-08-16) 하네스 대조 → **QF-SELECT 5건 재실행**

**계기**: 사용자가 "실험용 하네스가 문제라면 codex가 만든 하네스의 코드를
directly READ then comparison"이라고 지시. 정본 하네스
(`_h1a_cohort.py`+`_h1a_score.py`)와 내가 만든
`_h1a_qualification_run.py`를 **무엇을 고정(pin)하는가** 기준으로 대조했다.

**결과 — 적대 검토 4축이 전부 놓친 결함이 나왔다.** 놓친 이유가 명확하다:
내가 검토 범위를 **"판정문/amendment"로 잡고 "하네스"로 잡지 않았다.**
제작자가 검토 범위를 설계할 때의 한계가 §9의 L-1에 이어 **두 번째로**
실증됐다.

정본 하네스가 고정하는데 내 하네스가 고정하지 않던 것:

| 누락 | 정본 기록값 |
|---|---|
| `protocol.transport` | `schema_forced_structured_output` |
| `protocol.trial_model` | `claude-opus-5` |
| `trial_subject_surface` | 정의 파일 sha + system prompt sha + `tools: []` 단언 |
| `decision_schema_sha256` | (있음) |
| `contract_prompt_sha256`·`payload_sha256`·`qualification_sha256` | (있음) |

**실질 결함 2건**:

1. **transport 불일치.** 본 코호트는 Workflow `agent(prompt, {schema})`로
   **스키마 강제** 실행됐다. 2026-08-15 QF-SELECT 5건은 Agent 도구로
   dispatch했는데 **그 도구에는 schema 파라미터가 없다** — 출력이 JSON이었던
   것은 프롬프트가 요청해서지 강제된 것이 아니다.
2. **피험자 모델 불일치(추정).** `h1a-decider.md`에 `model:` 지정이 없어
   **부모 세션 모델을 상속**한다. 5건 dispatch 당시 세션은 Sonnet 5였고
   코호트 protocol은 `trial_model: claude-opus-5`다. → 본 코호트의 피험자가
   아닌 다른 모델을 진단한 셈.

**그리고 이것이 핵심**: 2번을 **산출물로 증명할 수 없었다.** 내 manifest가
모델·transport·피험자 표면을 하나도 안 남겼기 때문이다. **증명 불가 자체가
결함**이며, 이 결함은 자기 자신을 은폐한다.

**교훈(재사용 가치 높음)**: **prompt byte-identity는 필요조건이지
충분조건이 아니다.** capability diagnostic이 식별하는 것은 *프롬프트*가
아니라 **어떤 TRANSPORT 하의 어떤 SUBJECT**다. Q14.3의 byte-identity 재사용
조건을 통과했다고 재사용이 정당화되지 않는다.

**수정**:

- `_h1a_qualification_run.py`가 `protocol`·`trial_subject_surface`·
  `decision_schema_sha256`을 기록. 피험자 계약은 **복제가 아니라 재사용** —
  `TRIAL_MODEL = cohort_mod.MODEL`, `TRIAL_PARAMETERS = cohort_mod.PARAMETERS`,
  `cohort_mod._trial_subject_surface()` 호출. 코호트의 모델이 바뀌면 진단도
  자동으로 따라간다(따라가지 않으면 진단이 무의미해지므로 구조로 강제).
- **원시 출력 파일이 자기 provenance를 선언하도록 요구**
  (`_assert_raw_provenance_matches_the_manifest`). provenance 블록이 없으면
  **"호환된다고 가정"하지 않고 거부**한다 — "기록 안 됨"은 "괜찮음"이 아니다.
  2026-08-15 파일이 이 가드에 정확히 걸린다.
- drift 가드 강화. 기존 가드는 `rendered_prompt_sha256`만 비교했는데 그 값은
  **구조가 낡아도 안 바뀐다**(실제로 `protocol` 없는 낡은 manifest가 조용히
  통과해 `KeyError`로 터졌다). 이제 `protocol`·`trial_subject_surface`·
  `decision_schema_sha256`까지 비교하고, 필드 자체가 없으면 "이 manifest는
  해당 필드 이전 것"이라고 거부한다. **구조적 staleness도 drift다.**
- score 레코드가 **자기 출처를 서술**하도록 `protocol`·`trial_subject_surface`·
  `decision_schema_sha256`·`raw_provenance`를 발췌 포함.

**재실행**: 코호트와 동일 경로로 5건 재실행 — Workflow `agent()` +
`schema` 강제 + `model: 'opus'` 명시. 결과 **5/5
`select_type`/`structural_composition`**(변화 없음). rationale이 이전 실행보다
확연히 길고 구조가 달라, 다른 모델이었다는 정황과 일치한다.

기존 5건은 **삭제하지 않고** `h1a_qualification_raw_historical_20260815.json`으로
보존 — 실제 관측이고, Q14.3이 superseded run의 historical 보존을 지시한다.
`record_class`에 `_HISTORICAL`, `provenance_recorded: false`, 그리고 왜
superseded인지를 파일 안에 기록했다. **채점하지 않고 QF-SELECT 증거로
인용하지 않는다.**

게이트: H1a 237 passed/1 skipped, E2.4 118 불변, core pytest 기존 owlready2
결함 1건 그대로. 새 `_assert_*` 가드 4개 전부 AST 스캔에 잡히고 covered
확인(게이트 초록만으로는 "스캔 대상 아님"과 구별되지 않으므로 직접 확인).

**현재 상태**: QF-SELECT `passed`(5/5, 올바른 피험자·transport),
QF-DEFER `material_unavailable`(L9 등록). `cohort_freeze`는 이 계층이
판정하지 않는다. `freeze_status: FREEZE_BLOCKED`,
`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지.

### 13. (2026-08-16) Q13.6 완결 + Q13.5 + 독립 리뷰 — **condition_12 미완(할당량)**

의존성 분석 후 ①→②→③→④ 순서로 진행.

**① expected graph 비교(§9.4 마지막 화살표)** — `_h1a_policy_audit.py` 신설.
compiler는 정책을 import하면 안 되고(AST 강제), 그 독립성은 누군가 비교해야
값이 있으므로 **양쪽을 볼 수 있는 유일한 모듈**로 분리했다. mutation 테스트가
핵심: REMOVED에 잔여 금지를 주입하면 target-critical `state_mismatch`로 잡힌다
(한국어·영어 양쪽). KEPT에서 절을 지우는 역방향도 잡힌다. **family(8)과
axis(5)가 1:1이 아니며**(template-level 3개는 대응 axis 없음,
`external_source_retrieval`은 전용 family 없음) 양방향 모두 findings로 노출한다 —
조용히 버리면 family 하나가 통째로 미감사인 채 보고서가 clean으로 읽힌다.

**② GLOBAL_DEFAULT_PERMISSION 탐지 능력** — target-critical 중 유일한 미입증
이었다. 원인이 둘로 갈렸다: (a) 내 fixture가 **라벨과 다른 것**을 담고 있었고
("필드 범위 축소"인데 내용은 Q13.2의 범위 *확장*), (b) 조건부 형태를 놓치는
**진짜 detector 결함**. 고정 문구 목록을 의미 핵심(허가 표현 + 금지 참조 공기)
으로 교체.

**가장 중요한 부분**: 모든 fixture를 통과시킨 뒤 **fixture 밖 변형으로
일반화 검증**을 했더니 3개 중 2개를 놓쳤다. 거기서 "proven"을 보고했으면 이
계층이 막으려던 허위 커버리지 주장 그 자체가 된다. **probe의 실패를 fixture로
승격**했고(자기가 아는 약점보다 약한 fixture 집합은 거짓 proven을 만든다),
detector를 확장했다(`forbid`가 금지 어휘에 아예 없었다). 남은 1건(비국소
부정)은 `KNOWN_DETECTION_LIMITS`에 사유·담당과 함께 등재 —
저장소의 `KNOWN_UNPROVEN` 관례 그대로이며, 조용히 동작하기 시작하면 실패하는
테스트로 썩는 것을 막는다.

**③ blinded mutation pack(Q13.5)** — `_h1a_mutation_pack.py`.
**clean packet 필수**(없으면 "항상 결함 있다고 답하기"가 통과해 아무것도 측정
못 한다), **답안지 분리 반환**, 그리고 **변이 진위 검증**(정책 의미를 안 바꾸는
변이로 리뷰어를 시험하면 노이즈를 재는 것).

그 진위 검증이 6개 중 **3개가 무력함**을 잡아냈고, 원인은 전부 결함이었다:
- **`compare()`가 §9.3 구조 항목을 통째로 무시**하고 있었다. dangling
  reference를 재주입해도 findings가 0건 — **D-H1a-13을 낳은 바로 그 결함
  종류가 조용히 통과**했다. 구조 항목을 findings로 편입.
- presentation-order detector가 Q13.1이 **모호해서 개명한** `source order`를
  여전히 유효 표현으로 받았다. 되돌려도 "present"라 존재 검사로는 못 잡는다 →
  `AMBIGUOUS_AXIS_PHRASING` 구조 항목 신설.
- M5 변이가 Q13.2의 두 문장 중 하나만 지워 무력했다.

**④ 독립 리뷰 실행** — `_h1a_review_protocol.py`로 절차를 **코드화**했다.
2026-08-16 적대 검토가 하네스 결함을 통째로 놓친 원인이 "검토 대상 세션이
검토 범위를 정한 것"이었으므로, 범위 선언·blinding·자격 채점을 실행자 재량에서
빼앗는다. 자격 미달자의 승인은 **기계적으로 폐기**되고, 대칭적으로 **그의
blocker도 세지 않는다**(측정 안 된 판단은 양방향으로 측정 안 된 것이다).

**condition_11 결과: 통과.** 리뷰어 5명(target_axis / referential /
non_target / evidence_scope / decision_mapping) 전원 자격 취득 —
변이 6건 **전원 탐지, 오탐 0, 누락 0**.

1차 실행에서 **내 프로토콜 결함 2건**이 리뷰어에 의해 드러났다:
- condition_11은 `rendered_prompt_reviewed`와 `adversarial_mutation_pack_used`를
  **별개 요구**로 나열하는데 내가 변이 패킷만 주고 실물을 안 줬다 → 그들의
  `scope_findings`는 주입 변이를 실험 결함으로 읽은 것이라 리뷰로 셀 수 없다.
- R4가 잡음: 내가 준 것은 `{payload_json}` **미치환 arm 템플릿**이었지 피험자가
  실제로 보는 렌더 결과가 아니었다.
둘 다 바로잡아 2차(condition_12)를 실물 아티팩트로 재실행했다.

**condition_12 결과: 충족 (한도 복구 후 재실행 완료).**
1차 시도에서 5명 중 4명이 조직 월 지출 한도로 중단됐고 R3만 완료했다.
한도 복구 후 **R1·R2·R4·R5만 재실행**(자격 검증은 이미 통과했고 대상이
바뀌지 않았으므로 재실행 안 함). **5명 전원 승인, blocker 0 · major 0.**

각 리뷰어가 자기 범위의 target-critical 상태를 **compiler에 의존하지 않고
직접 독해로** 해소했다고 명시했다. 리뷰어들이 독립 실측한 것: 양 arm 차이는
Q1 절 하나뿐(`kept.replace(Q1,'',1) == removed`), Q7 불릿·payload 바이트
동일, REMOVED의 `absent_verified`는 침묵이 아니라 GLOBAL_DEFAULT 절이 적극
담보, payload가 양 arm 모두 최종 위치라 그 뒤 지시문 없음, 옛 conflict→defer
문구가 `cohort_prompts.json`에 남은 것은 폐기된 2026-08-03 코호트의 의도적
provenance이며 live render 경로가 안 읽음.

**R2가 1차에서 제기한 trust-boundary 가설을 실물 확인 후 스스로 철회**했다.

`assess()` 판정: `condition_11_met: True`, `condition_12_met: True`,
`independent_semantic_review_passed: True`. **그러나 플래그는 사람이
설정한다** — 모듈이 그렇게 설계됐고, 이번 세션이 무판정 집행으로 한 번
철회당한 뒤 세운 규율이다. `INDEPENDENT_SEMANTIC_REVIEW_PASSED`는 **아직
`False`**이며 사용자 결정 대기.

**리뷰어가 찾은 계측 결함 — 4명이 독립적으로 같은 지점**:
`EVIDENCE_COUNT_PROHIBITION`이 capability report에는 미입증인데 동시에
`agreed`에 계상돼 커버리지를 과대 표시했다(R1·R2·R4·R5). 수정 완료
(`agreed` / `agreed_by_unproven_detector` 분리). **R2가 붙인 제약을
기록이 준수한다** — "freeze 기록이 EVIDENCE_COUNT나 GLOBAL_DEFAULT에 대해
compiler_diff를 독립 확인 근거로 인용하면 그 인용은 부당하다."

**미수정 3건(다음 세션)**: ①정본 DSL에 기대값 없는 target-critical family
3개는 compiler로 구조적 반증 불가 — 특히 `GLOBAL_DEFAULT_PERMISSION`은
REMOVED의 absent_verified를 담보하는 유일 carrier인데 compiler가 판정 보류
하는 자리다(R2·R4). ②분기 상보성을 표현하는 family 부재(R5).
③조건부 carve-out의 payload 의존성을 compiler가 평면 present로 보고(R3).

전문: `docs/feedback/h1a_independent_semantic_review_20260816.md`

게이트: H1a 301 passed/1 skipped, 루트 8 passed/0 failed/1 blocked.

**남은 것**: `INDEPENDENT_SEMANTIC_REVIEW_PASSED` 설정 여부 **사용자 결정** →
설정 시 `repaired_cohort_trials` 40건 착수 가능. 계측 미수정 3건은 코호트
실행을 막지 않으나(리뷰어들이 독해로 해소했다) 다음 리뷰 전에 닫는 것이 좋다.

---

### 12. (2026-08-16) Q13.6 착수 — semantic compiler + capability gate

**owlready2 게이트 red 해소 먼저**(HANDOFF §10.1 승인·적용). 이 저장소가 이미
3곳에서 쓰는 optional-dep 스킵 관례를 이 테스트만 안 따라 맨손 checkout에서
게이트가 red였다. `OPTIONAL_DEPS` 안의 이름일 때만 스킵하고 `conceptgate.X`
부재는 계속 실패시킨다(진짜 drift). 스킵이 drift 탐지를 삼키지 않는지 양성
테스트로 고정. **루트 게이트 8 passed / 0 failed / 1 blocked** — 이 세션 처음
green. (Render 배포는 이 문제와 무관하다 — Render는 산출물이 도는 곳이고
이건 로컬 테스트가 모듈을 직접 import하는 것이다.)

**Q13.6 §9 구현**. 정본(typed policy DSL)은 이미 `_h1a_policy`에 있으므로
만든 것은 **독립 drift auditor**다.

- **독립성을 AST로 강제**. `_h1a_policy`엔 이미 `AXIS_SURFACE_TOKENS`가 있고
  assertion 12가 그걸로 렌더 산문을 검사한다. compiler가 그걸 가져다 쓰면
  렌더러를 렌더러 자신의 어휘로 검사하는 셈이라 **구성상 항상 동의**한다 —
  F10과 오늘 오전 피험자 해시 가드에서 이미 두 번 당한 패턴이다. 주석으로
  적으면 다음 세션이 편의상 import하므로 테스트로 막았다.
- **fail-closed(§9.6)**. `proven_families` 밖의 침묵은 구조적으로
  `absent_verified`가 될 수 없고 `unknown`이 된다. 기본값은 공집합.
  아무것도 못 잡는 compiler는 무용하지만 무해하고, 입증 없이 verified
  absence를 내는 compiler는 **금지가 arm에 살아남는 경로**다(D-H1a-10이
  실제로 그랬다).
- `proven_families`는 fixture 실행으로 **계산**한다. 손으로 적은 목록은
  썩어서 허위 커버리지 주장이 된다.

**capability gate가 실제로 잡은 것** — 코드를 확인해준 게 아니라 결함을
찾았다. `CONFLICT_TO_DEFER_MAPPING` detector가 실제 렌더 문장(hard mapping의
**정반대**인 "does not by itself require either selection or deferral")에
`found=True`를 냈다. boolean이 자기 family 이름과 어긋나 모든 호출자가
오독할 상태였다. 수정.

**미입증으로 남긴 것(정직하게 보고, regex로 맞춰 지우지 않음)**:
`GLOBAL_DEFAULT_PERMISSION`이 조건부·필드범위축소 형태를 놓친다(**target-critical
이라 Q13.5상 freeze 전 해소 필요**). `EVIDENCE_COUNT`·`TEXT_TYPE_SUPPORT`는
fixture 미작성. 셋 다 침묵이 `unknown`으로 나가므로 안전한 방향이다.

`detect_duplicate_carrier`는 **`detect_repeated_mentions`로 재규정**했다.
한 정책이 여러 문장에 걸친 것과 carrier가 둘인 것을 구별하지 못하는데
(실측: outside-domain 3, 그 외 2), 그 판별에는 carrier registry가 필요하고
이 모듈은 그걸 읽으면 안 된다. 권위 있어 보이는데 아닌 검사는 믿어버리므로
`establishes_duplicate_carriage: false`를 명시한 후보 목록으로 낮췄다.

**핵심 결과**: 정책 모듈을 한 번도 참조하지 않은 auditor가 실제 렌더
프롬프트에서 `SOURCE_META_REASONING_PROHIBITION`을 **KEPT=present /
REMOVED=absent_verified**로 관측했다. 첫 코호트를 비식별로 만든 바로 그
대비에 대한 **독립 증거**다. 양 arm 모두 arm 메타언어 노출 0건, dangling
reference 0건(Q13이 지운 문장의 회귀 검사).

게이트: H1a 256 passed/1 skipped, 루트 8 passed/0 failed/1 blocked.

**남은 것 (Q13.5/13.6 완료까지)**:
- expected policy graph 생성 + 관측 graph와 **비교** 단계(§9.4 화살표 마지막)
- `GLOBAL_DEFAULT_PERMISSION` 탐지 능력 확보 — target-critical이라 필수
- `EVIDENCE_COUNT`·`TEXT_TYPE_SUPPORT` fixture
- **Q13.5 reviewer capability gate** — blinded mutation pack, 리뷰어별 배정
  범위 선언, 최소 1건 탐지 못 하면 그 리뷰어의 "문제 없음"을 freeze 승인으로
  계산하지 않음
- 그 다음에야 독립 리뷰 전면 재실행 → `repaired_cohort_trials` 40건

---

---

## 2026-08-06 — D-H1a-12 §16 구현(조건 1~10) + 독립 리뷰 5차 → FREEZE_BLOCKED

worktree `concept-gate-h1a-scope-wt`(브랜치 `codex/h1a-typed-scope-split`)에
격리해 진행. h1 브랜치는 무손상. **trial 0건 유지.**

### 1. 구현 — §16의 12조건 중 10개

174 passed / 1 skipped. 가드 커버리지 게이트 10 passed.

| # | 조건 | 결과 |
|---|---|---|
| 1 | typed-scope split | 축 7→5, `source_meta_reasoning`이 형제 범주, 옛 표적 축 4개는 하위 축 |
| 2 | 공통 Q7 3문장 분리 | Q7 / DOMAIN / SCOPE_DISAMBIGUATION |
| 3 | defer 규칙 비방향화 | `conflict`→outcome 직접 매핑 제거 |
| 4 | demand neutralizer 재문안 | 두 명제 분리 |
| 5 | `assert_12` 의미 검사화 | 정책 객체 검사, lexical은 `lint_common_q7`로 격하 |
| 6 | golden contract | `h1a_common_policy_block_v2.json` |
| 7 | 음성 테스트 5종 | 삭제·중복·KEPT 1자·REMOVED 1자·**양 arm 동일 변경** |
| 8 | `licensed_source_evaluation_path` | 5-항 논리곱, §10 진리표 일치 |
| 9 | M4 ceiling 복구 | Q4 승인 문안 범위 갱신 재등재 |
| 10 | 새 사전등록 | `PREREGISTRATION_TYPED_SCOPE_COHORT.md` |

### 2. 구현 중 가드가 제작자를 잡은 3회 (전부 테스트 약화 아님, 구현 수정)

1. **`assert_5`가 `[5] outside_domain_knowledge`로 발화** — 새 담지자
   (`DOMAIN_KNOWLEDGE_BOUNDARY`)를 추가하면서 그 span을 strip 목록에 등록하지
   않았다. 가드가 옳고 구현이 미완성이었다.
2. **뮤테이션 테스트가 renderer의 `KeyError`를 잡았다** — Q7이 담지하는 축에
   선언된 문구가 없을 때 죽었다. `PolicyContractError`로 바꿔 "정책/렌더러
   불일치"라는 실제 성격이 드러나게 했다.
3. **golden contract가 neutralizer 변경을 즉시 drift로 잡고** "의도된 변경이면
   별도 커밋으로 재동결하고 이유를 밝혀라"라고 지시했다. 그대로 따라
   `amendment_history`에 `at_trials: 0`과 함께 기록했다. **자기동일성 검사였던
   옛 `assert_9`로는 원리상 불가능한 탐지** — 조건 6·7의 목적이 이것이었다.

### 3. 독립 리뷰 5차 — 세 축, 리뷰어 3명

1차 시도(2026-08-05)는 세 명 전원 API 세션 한도로 조기 종료. **전송 실패이지
리뷰 결과가 아니므로 통과로 기록하지 않았다**(E2.4가 30 trial 중 22개를 같은
이유로 잃었을 때와 동일 판정). 한도 리셋 후 재실행.

전문: `../../docs/feedback/h1a_typed_scope_review_20260806.md`

#### 축 (b) 렌더된 프롬프트 — BLOCKER 1 + MAJOR 4 + MINOR 3

**BLOCKER: 판정문 §4가 verbatim 처방한 세 번째 문장이 REMOVED arm에서
dangling reference다.** "Source evaluation is governed by the arm-specific
source-evaluation clause."인데 REMOVED에는 그 절이 없다(Q1은 KEPT 전용).
제작 세션이 리뷰어 주장을 그대로 받지 않고 직접 실측:

```
PROHIBITION_KEPT:    Q1절=True   "arm-specific...clause" 참조=True
PROHIBITION_REMOVED: Q1절=False  "arm-specific...clause" 참조=True
```

이 문장이 §4 자신이 의존하는 기제를 무너뜨린다 — §4는 REMOVED가 작동하는
이유를 "Q1이 없으므로 공통 기본허용 규칙이 적용된다"로 설명하는데, 이 문장이
그 basis에 **더 구체적인** 지배자를 지목하므로 specific-beats-general 읽기에서
기본허용이 적용되지 않는다. 침묵에 의한 허용이 불가능해진다.

**D-H1a-11의 "이식된 절이 선행사를 잃는다" 패턴 재발이고, 이번엔 판정문이
처방한 문장 자체가 그 결함을 갖고 있다** → 운영 세션 수정 불가, D-H1a-13 상신.

#### 축 (a) 정책 계약 — BLOCKER 2 + MAJOR 3 + MINOR 1, 미탐지 뮤테이션 5건

리뷰어가 뮤테이션 9개를 시도해 **5개가 167 통과로 빠져나갔다.** 전부 수정하고
제작 세션이 직접 재현 검증했다(M1 3 failed / M3 3 failed / M7 4 failed,
M2는 회귀 테스트로 고정, 복원 후 byte-identical 확인).

- **BLOCKER: §10 술어가 실행 경로에 없었다.** `assert_freezable`이
  `assert_licensed_path_contrast`를 호출하지 않아, freeze를 실제로 막는
  게이트는 여전히 `deductive_check`의 `target_mechanism_contrast`(§10이
  "필요한 명제를 보장하지 못한다"고 교체 명령한 그 술어)에 기대고 있었고
  대체 술어는 테스트에서만 돌았다. **이번 세션 초반에 내가 고친 "정책 계층이
  실행 경로에 없다" 결함을 한 층 위에서 그대로 반복했다.** 배선하고 V·H를
  keyword-only 필수 인자로 만들었다(모듈 기본값 제거 — 기본값이 남으면 한
  인자 호출이 두 fixture 사실을 조용히 인증한다).
- **BLOCKER: 비포섭이 주장만 되고 강제되지 않았다.** 근본 원인은 **모든 단언이
  `AXES`를 순회하므로 `AXES` 밖의 표 키는 어떤 단언도 방문하지 않는다**는 것.
  신규 `assert_0`(표 키 == AXES)·`assert_0b`(재부모화 금지 + 표적축이
  `CARRIER_DOMAIN`에 담지 안 됨)로 강제. `assert_12`의 subaxis 루프도
  `== CARRIER_Q7`에서 "Q1이 아닌 모든 forbidding carrier"로 넓혔다.
- **MAJOR: §5의 state 열이 고정되지 않았다.** ruling-forbidden 축을 양 arm
  `UNSPECIFIED`로 강등해도 통과했고 산문은 여전히 금지 — 표와 프롬프트 불일치,
  Q10 결함의 반대 방향. 신규 `assert_0c`가 5축 state 쌍을 고정.
- **MAJOR: golden artifact가 tie-breaker 문장을 덮지 않았다.**
  `carriers_included`에 `Q7_NON_TARGET_TIEBREAKER`가 빠져 그 문장에 동결
  바이트가 어디에도 없었다. 리뷰어의 M2(§8이 제거 명령한 "unless that priority
  is directly stated inside an evidence item's text" 복원)가 통과하며 **실제
  trial 표면에 도달**했다. lint가 침묵한 이유도 §8 자신이 인용한 그 누락
  (bare `priority`가 `AXIS_SURFACE_TOKENS`에 없음)이다. Q7 포함 재동결 +
  회귀 테스트 고정.

리뷰어 CONFIRMED-OK: §5 담지자/arm 배정 정확, `assert_12`가 진짜 semantic,
golden artifact가 진짜 독립(positive control M5 → 8 failed), §9 음성 5종 전부
존재하며 "양 arm 동일 변경" 케이스 실제 커버, `assert_5` span-stripping과
`assert_6b` window가 이식·의역 산문 금지를 잡음(M6 → 2 failed, M6b → 5 failed).

#### 축 (c) 사전등록·게이트 — BLOCKER 2 + MAJOR 5 + MINOR 3

리뷰어가 §4 표의 "✅ 자동" 10건을 **하나씩 독립 검증**했다. 결과: 3·4·5·7은
참, 나머지는 과장 또는 거짓이었다. 제작 세션이 상위 2건을 직접 재현했다.

**F10 (가장 중대) — 게이트가 렌더러와 다른 모듈 객체를 인증한다.**
`_h1a_contract._fill_policy_slots`가 `_h1a_policy.py`를 `sys.modules`의
**별도 키**(`_h1a_contract__policy`)로 두 번째로 로드한다
(`_h1a_contract.py:239-245`). 제작 세션 실측:

```
사본 존재: True | 같은 객체: False
copy A(테스트가 변조하는 객체) 변조가 렌더에 반영: False
```

즉 **프롬프트 바이트는 사본 B가 만들고, 모든 정책 단언·연역 검사·`assert_12`·
`INDEPENDENT_SEMANTIC_REVIEW_PASSED`는 사본 A에서 읽힌다. 둘이 일치한다고
단정하는 검사가 없다.** 결과적으로 이 세션이 쓴 모든 뮤테이션-recall 테스트는
사본 A만 변조하므로 **모델 대면 바이트를 생성하는 객체의 결함을 원리상 탐지할
수 없다.** `_h1a_cohort.py` 자신의 주석이 이름 붙인 "참인 명제를 잘못된 객체에
대해 단정한다"가 가장 깊은 층에서 실현된 것이다.

첫 재현 시도는 실패했다 — 제가 `_h1a_policy`를 먼저 import해서 로더가 재사용한
것으로 착각했다. 사본은 `_fill_policy_slots`가 **호출될 때** lazy로 생기므로
`render_arm`을 실제로 돌린 뒤에야 드러난다. 리뷰어 지적이 정확했다.

**F5 (BLOCKER) — 조건 9(M4 ceiling) 배선이 약속만 되고 구현되지 않았다.**
판정문 §14 action 4가 "golden artifact 또는 구조 검사에 배선"을 요구하는데
`_h1a_score.py`에 `ceiling|modal|uninterpretable|prompt_surface`가 **0건**
(제작 세션 실측). 사전등록 §5의 "배선한다"는 미래형이었고, §4 표의
"9 | M4 ceiling 복구 | ✅ 이 문서로"와 §8의 "조건 1~10 전부 구현·통과"는
**둘 다 거짓**이다.

**F6 (MAJOR) — §5 재등록이 범위만이 아니라 규범 내용을 바꿨다.** 제가
"규범적 내용은 Q4 승인 문안 그대로"라고 적었는데 거짓이다:
① `, and MUST NOT be reported as null_effect`를 **추가**했다(승인 문안엔 없음,
게다가 세 줄 아래 "not a new blocking rule"과 나란히 있다). ② 발동 조건을
"네 진단 셀"→"이 코호트의 두 arm"으로 바꾼 것은 범위 갱신이 아니다 — 네 셀은
주 결과 **외부의** anchor×arm 대비였고, "두 arm이 같은 modal 범주"는 **주 결과
자체**다. 조건이 자기가 수식하는 것에 의해 정의상 함의되므로 ceiling에 대한
독립 정보를 담지 않는다. ③ "세 문장이 golden에 동결됨"이라 적었으나 F2가
반증한다.

**F2 (MAJOR) — 공통 tie-breaker 문장을 아무것도 동결하지 않는다.** golden의
`carriers_included`에 `Q7_NON_TARGET_TIEBREAKER`가 없었고, `grep "break ties"`가
테스트에서 **0건**이라 §4 표 2행의 "contract 테스트"는 존재하지 않는다.
리뷰어가 `_Q7_AXIS_PHRASE`를 바꿔 **공통** 문장이 표적 하위축을 금지하게
만들었는데("how recently a source was updated", "whether a source is still
maintained") `assert_9`·`assert_12`·`assert_6b`·`licensed_path` 전부 PASS,
`lint`는 finding 0 — 토큰 목록에 `more recent`는 있고 `recent`는 없고,
`liveness`는 있고 `still maintained`는 없는 그 우연한 누락이다.
(제작 세션이 그 뒤 Q7을 golden에 포함시켰으나 **F2의 이 변종은 별개**다.)

**F9 (MAJOR) — §13 재사용·병합 방지가 한쪽만 되어 있다.** `freeze()`는
fail-close하지만 **`_h1a_score.py`에는 동등한 가드가 없다** — `main()`이
`trials.json`·`h1a_cohort_score.json`을 무조건 쓰고 보존된
`trials_raw.json`을 읽는다. **채점기를 돌리면 보존된 40 trial을 재채점하고
보존 산출물을 덮어쓴다.** 이 세션이 `freeze()`에 대해 막은 것과 같은
비가역 위반이 하네스의 반대쪽 절반에 남아 있다. 또 `cohort_id` 필드가
`_h1a_cohort.py`·매니페스트 어디에도 없어 §6의 "cohort_id 분리"는 미구현이고,
`PREREGISTRATION_REPAIRED_COHORT.md`에 이 문서 참조가 0건이라 그 문서 독자가
지배 사전등록에 도달할 수 없다.

**F1 (MAJOR) — §4/§8의 완결 주장이 이 문서 자신의 §8.2와 모순된다.** §4는
조건 1~10을 ✅로 표시하고 §8은 "전부 구현·통과"라 쓰는데, §8.2는 조건 1의
분리를 모델 대면 프롬프트에서 **구현하는 그 문장**이 REMOVED에서 dangling
reference라고 기록한다. 조건 1은 정책 표에서는 충족, 렌더 표면에서는 미충족이다.

**F3·F8·F11·F12는 CONFIRMED-OK 또는 MINOR**: `assert_freezable` 순서는 실측
확인됨(구조 결함이 리뷰 플래그를 가리지 않는다), `KNOWN_UNPROVEN` 비움은
정당(19 raising 가드 전부 커버), §8.1이 실패한 리뷰를 통과로 취급하지 않음이
grep으로 확인됨(`= False` 외 대입 0건).

**§16 항목 대조(리뷰어 Q2)**: 1↔1 ~ 12↔12, 누락·병합·재번호 없음. 결함은
열거가 아니라 **✅ 표시가 무엇을 주장하는가**에 있다.


### 4. 이 라운드가 확인한 방법론적 사실

**세 축 합계 BLOCKER 4 + MAJOR 9. 가드가 전부 통과하는 상태에서 리뷰어들이
뮤테이션 6개 이상을 빠져나갔고, 그중 F10은 테스트가 애초에 잘못된 객체를
검사하고 있었음을 보였다.**

가장 값진 발견은 **§4 표의 "✅ 자동" 표시 자체가 검증 대상이었다는 것**이다.
리뷰어 (c)가 10건을 하나씩 재현하자 3·4·5·7만 참이었다. 제작 세션이 "구현했고
테스트가 통과한다"를 "그 조건이 충족됐다"로 등치한 것이 바로 이 실험이
반복해서 실패한 그 등치다.

**가드 12개가 전부 통과하는 상태에서 리뷰어가 뮤테이션 5개를 빠져나갔다.**
그중 둘은 구조적 사각지대였다 — 단언이 `AXES`를 순회하니 그 밖의 키는 안
보이고, golden artifact가 담지자 하나를 빼먹으니 그 문장은 어디에도 동결
바이트가 없었다. 두 경우 다 "가드가 있다"는 사실이 "그 명제가 지켜진다"를
뜻하지 않았다.

**세 발견(렌더 축의 BLOCKER, MAJOR 1·2)은 전부 공통 템플릿 문장에 있어
arm-diff 증명과 잔여-금지 tripwire가 원리상 볼 수 없다** —
`_h1a_contract.py`의 KNOWN LIMITATION 주석이 예고한 그대로다.

그리고 **제작자가 자기 산출물의 결함을 못 본다**는 이 실험의 반복 관찰이
다시 확인됐다: BLOCKER 3건 전부 제작 세션이 아니라 별도 리뷰어가 찾았고,
그 시점에 제작 세션의 테스트는 전부 통과 중이었다.

### 5. 다음 행동

**운영 세션이 고칠 것(판정 불필요) — 먼저 한다:**

1. **F10 사본 분기** — `_h1a_contract`가 정책을 재로드하지 않게 하거나, 두
   사본이 일치함을 단정하는 검사를 넣는다. 이걸 고치기 전의 모든 뮤테이션
   테스트 결과는 신뢰할 수 없다.
2. **F9 `_h1a_score.py` 덮어쓰기 가드** — `freeze()`와 동등한 fail-close.
   보존된 40 trial 산출물을 덮어쓸 수 있는 상태다.
3. **F5 M4 배선** — `_h1a_score.py`에 실제 구현. §4 표의 ✅를 그때까지 ⬜로 정정.
4. **F6 §5 문안** — 추가된 `MUST NOT be reported as null_effect`를 제거하거나
   Q4 승인 범위를 넘는 추가임을 명시. 발동 조건이 주 결과와 동어반복이 되는
   문제는 설계 판정이 필요할 수 있다.
5. **F1·F2 ✅ 표시 정정** — 과장된 항목을 실제 상태로.

**그 다음 D-H1a-13 상신.** 렌더 축 BLOCKER와 MAJOR 1·2, 그리고 F6의 발동 조건
동어반복 문제가 판정문 처방 문구(§4·§7·§14)의 결함이라 운영 세션이 고칠 수
없다.

`FREEZE_BLOCKED` 유지 · `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` ·
trial 0건.

---

## 2026-08-03(3) — Q10.2 정책 계약 구현, Q11 상신

### 1. 신규 — `_h1a_policy.py` + `test_h1a_policy.py` (28 passed)

Q10.2가 명령한 계층 중 앞 네 개를 구현했다. LLM 의미 검사기는 판정문이
"advisory only"로 못박았으므로 구현하지 않았다.

```text
typed policy schema → deterministic renderer → structural assertions
→ deductive policy check → (LLM semantic lint: 미구현, 보조) → human sign-off
```

**핵심은 `carriers` 필드다.** 옛 가드에 없던 것이고, 그것이 없었기 때문에
blocker #16과 Q10이 같은 결함으로 두 번 났다. 축의 **상태**만 알면
부족하고, 그 상태를 **어느 섹션이 담지하는가**를 알아야 "한 축이 두 번
금지되고 있는가"를 검사할 수 있다.

| 단언 | Q10.2 요구사항 | 무엇을 잡는가 |
|---|---|---|
| `assert_target_axis_states` | 1 | 표적 축이 KEPT=forbidden/REMOVED=allowed가 아님 |
| `assert_nontarget_axes_are_arm_invariant` | 2 | 비표적 축이 arm 간 달라짐 |
| `assert_arm_difference_is_exactly_the_target_set` | 3 | arm 차이 집합 ≠ 사전등록 표적 집합 |
| `assert_manipulated_axes_have_exactly_one_carrier` | 4 | **조작 대상 축의 중복 금지 = Q10의 결함** |
| `assert_declared_carriers_match_rendered_text` | 5·6 | 선언과 산문의 불일치, **양방향** |
| `assert_deductive_check` | 연역 | `M_allowed = ¬Q1 ∧ ¬Q7_target`를 정책 객체에서 **재도출** |

연역 검사는 판정문 §3·§6의 표를 **복사하지 않고 재생산한다** — 진리표 4셀을
열거해 표적 경로가 열리는 셀이 정확히 하나(`¬Q1 ∧ ¬Q7`)임을 보이고,
KEPT=False / REMOVED=True / contrast=True를 정책에서 유도한다. Wolfram 없이
결정론적 Python으로 충분했다(판정문이 연역 도구를 permissive하게 허용했고,
새 의존성은 "영향 최소" 원칙에 어긋난다).

### 2. 가장 중요한 테스트 — 실제로 실행된 코호트가 거부되는가

`test_the_actual_nonidentifying_cohort_prompt_is_rejected`가
`cohort_prompts.json`의 **동결 바이트**(2026-08-03에 실제로 40 trial에 쓰인 것)를
새 가드에 넣고 **거부를 요구**한다. 그 옆에
`test_old_guard_still_passes_those_same_bytes`가 옛 가드는 같은 바이트를
**통과**시킴을 고정한다.

**즉 "새 가드가 실제로 일어난 일을 잡는다"가 합성 뮤테이션이 아니라 실물로
증명된다.** 뮤테이션 8종은 가드가 발화할 수 있음을 보이고, 이 두 테스트는
발화 대상이 맞다는 것을 보인다.

### 3. 구현 중 테스트가 잡은 실제 결함 1건

서식을 원본(76열 wrap)에 맞추자 **두 테스트가 즉시 깨졌다.** 원인은 테스트가
아니라 가드였다 — surface token이 다어절 구(`outside knowledge`)인데 wrap이
그것을 개행+들여쓰기로 쪼개면 substring 검사가 **실패한다**. 프롬프트에 축이
있는데 가드가 없다고 보고하는 **거짓 음성**이고, 정확히 옛 가드가 이 실험을
한 번 무너뜨린 종류의 결함이다.

`_normalize_ws`로 공백을 정규화해 수정하고,
`test_wrapping_cannot_hide_an_axis_from_the_checker`로 회귀를 고정했다.
**wrap을 도입하지 않았다면 이 결함은 발견되지 않은 채 남았을 것이다.**

### 4. R1 — 내용은 구현, 템플릿 교체는 **의도적으로 보류**

| 부분 | 상태 |
|---|---|
| R1의 내용 결정(어느 축이 공통 목록을 떠나는가) | ✅ `render_policy_text`가 구현, 테스트로 고정 |
| 템플릿의 하드코딩 불릿 → 정책 생성 placeholder 교체 | ⬜ **보류** |

보류 이유:

1. **Q11이 REMOVED 블록의 불릿 개수를 결정한다**(침묵=1개, 명시 허용=2개).
   배선을 지금 확정할 수 없다.
2. `test_h1a_contract.py:330::test_template_carries_q7_tie_breaker_prohibition_list`
   가 수선 전 바이트를 고정하고 있다. 지금 바꾸면 그 테스트를 고치고,
   Q11 후에 **또** 고쳐야 한다.
3. **재동결은 더 이상 무료가 아니다** — 40 trial이 실행됐다. 두 번 동결하는
   것보다 판정 후 한 번이 낫다.

R1 적용 후 공통 불릿의 예정 형태(렌더러 실측 출력):

```text
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence
  item's text.
```

### 5. Q11 상신

`correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md`.
**Q11**(`removed: allowed`의 렌더링 — 침묵/명시 허용/양 arm 형식 대칭) +
**Q11.1**(R1이 KEPT 금지도 약화시키는데 그대로 두는가) +
**Q11.2**(`carrier` 매핑을 사전등록에 동결하는가).

인용 대조 **9/9 통과** — 템플릿 46-52행 verbatim, `LIVENESS_CLAUSE_TEXT`,
렌더 길이 2318/2235(delta 83), packet-boundary 문장의 양 arm 존재, tie-breaker
불릿의 양 arm 존재(수선 전), Q1 절의 KEPT 단독 존재를 전부 실측으로 확인했다.

**Q11.1은 판정문에 없던 질문이다.** R1의 표는 KEPT를 "Q1에 의해 금지"로
적었지만, 수선 전 KEPT는 Q1(산문)과 Q7(의사결정 규칙) **두 곳**에서
금지받고 있었다. R1은 REMOVED를 열면서 **KEPT의 담지자도 하나 줄인다.**
판정문 §12가 그 둘을 "이 fixture에서 기능적으로 중복"이라고 했으므로 무해할
수 있으나, 그 전제가 참이라는 것이 바로 Q10의 근거였으므로 같은 전제를
반대 방향으로 쓰는 것이 타당한지는 판정 대상이다.

### 6. Fail-closed

`REMOVED_ALLOWED_RENDERING = None`이고, `assert_freezable()`이 그 값이
None인 동안 **동결을 거부한다.** 판정 없이 프롬프트가 trial에 도달하는 경로를
코드가 막는다. `render_policy_block("PROHIBITION_REMOVED")`도 모드 없이
호출하면 `Q11Undecided`를 던진다 — 다만 모드를 명시적으로 넘기면 렌더되므로
테스트는 양 분기를 다 검사할 수 있다(실험이 선택하지 않은 상태로).

### 7. 게이트

```text
H1a       106 → 134 passed / 1 skipped   (+28)
E2.4      118 passed                      (불변)
core      1 failed (owlready2 미설치 — §10의 기존 결함, 이번 변경과 무관)
```

### 8. 다음

**Q11 판정 대기.** 판정 전에 템플릿 교체·재동결·trial 실행·독립 리뷰를 하지
않는다. 독립 리뷰는 표면이 **확정된 뒤** 필수다 — Q9 때 생략 근거가 "표면
불변"이었고 지금은 "표면 미확정"이라 아직 이르지만, R1이 적용되는 순간
3차 리뷰(2026-08-02)는 무효가 된다.

---

## 2026-08-03(2) — Q10 판정 도착·반입 (D-H1a-10)

판정문: `DESIGN_DECISION_H1a_residual_prohibition.md`.
**Q10=E / Q10.1=보존(비병합) / Q10.2=가드 상향 / Q10.3=L4 등록.**

### 1. 판정 요지

| 항목 | 판정 |
|---|---|
| 이번 40 trial | **무효화 아님.** 실행된 프롬프트 아래의 관측은 유효 |
| 그러나 | 의도한 H1a estimand를 **식별하지 않음**(`TargetMechanismContrast: False`) |
| 결론 표기 | `target_effect: insufficient_evidence` + `current_bundle_contrast: observed_zero`. **`null_effect` 아님** |
| 수선 | **B 방식** — 공통 Q7 목록에서 표적 축 4개만 제거(R1), **양 arm 재실행**(R2) |

판정문 §3이 형식 검사로 뒷받침한다 — `M_allowed = ¬Q1 ∧ ¬Q7`이므로 현재
설계는 KEPT·REMOVED 둘 다 `M_allowed=0`, 수선 후에는 REMOVED만 `1`이 된다.
A(그대로 종료)는 "표적을 허용했는데 변화 없음"과 "양 arm에서 금지돼 있었음"을
혼동시키므로 기각, C(Q7 전체 이동)는 비표적 축까지 함께 바꿔 복합 조작이
되므로 기각, D(2×2)는 정당하지만 최소 복구에 불필요해 후속으로 유보됐다.

### 2. 이번 세션이 반입·등록한 것 (문서·메타데이터만, 표면 무변경)

| # | 작업 | 파일 |
|---|---|---|
| 1 | 판정문 저장(평면, 기존 4건과 같은 자리) | `DESIGN_DECISION_H1a_residual_prohibition.md` |
| 2 | **L4 등재** — 영문 원문 + 한국어 기록문, 의역 없음. L1~L3와 성격이 다름을 표로 명시(외적 일반화 한계 vs 내적 식별 한계, `L3_subsumes_L4: false`) | `PREREGISTRATION.md` §0.1 |
| 3 | 헤더의 **"전부 trial 0건 시점이라 재동결 비용 없음" 정정** — 이제 거짓이다. 갱신 4·5 이력 추가 | `PREREGISTRATION.md` 헤더 |
| 4 | **코호트 상태 동결** — Q10.1의 YAML 상태값 + 산출물 11종 sha256 + 보고 규약(허용/금지 문구) | `COHORT_STATUS_20260803_nonidentifying.md`(신규) |

**상태값을 `h1a_cohort_score.json`에 넣지 않았다** — `_h1a_score.py::main()`이
`SCORE_PATH.write_text(...)`로 매 실행 덮어쓰므로(`_h1a_score.py:168-170`
실측) 손으로 넣으면 채점기 재실행 시 조용히 사라진다. 같은 이유로
`trials.json`도 재생성 대상이라, 상태 파일의 해시 표에 그 사실을 명시했다.

### 3. 실측으로 재검증한 것 (요청서 인용을 그대로 받지 않음)

판정문·요청서가 인용한 사실 3건을 **원본 파일에서** 직접 확인했다:

| 주장 | 검증 |
|---|---|
| 가드가 bare `liveness`를 의도적으로 제외했다 | `_h1a_contract.py:99-103`·`:126-130` 주석 실측 — 요청서 인용과 일치 |
| `test_guard_precision_the_clean_template_passes`가 clean 인증 | `test_h1a_contract.py:218` 존재 확인 |
| 채점기가 score json을 덮어쓴다 | `_h1a_score.py:161-171` 실측 |

### 4. 다음 단계 — Phase 3 이후는 승인 대상

문서 등록(Phase 1~2)은 끝났다. 남은 것은 **동결 아티팩트를 실제로 바꾸는**
작업이라 별도 승인이 필요하다:

1. **R1 — Q7 부분 개정**: `h1a_prompt_template.md:50-52`에서 표적 축 4개
   (`source_kind priority`, `recency`, `authority`, `liveness`) 제거, 비표적
   3개(`evidence item count`, `source order`, `outside knowledge`) 유지.
   **동결 프롬프트 변경이다.**
2. **Q10.2 — 가드 상향**: `LIVENESS_PRIORITY_CLAUSES` + `RESIDUAL_TRIPWIRES_KO/EN`
   어휘 방식 → `decision_basis_policy` 타입 스키마 + 결정론적 렌더러 +
   구조 단언 6항 + 연역 검사. LLM 검사기는 **보조만**(단독 인증 게이트 금지).
3. **새 사전등록** — 판정문 §11의 post-result 공개 7항. 이 파일이 아니라
   **새 사전등록 문서**에 들어간다(기존 `PREREGISTRATION.md`는 최초 코호트의
   동결 기록으로 보존).
4. **독립 리뷰** — 표면이 바뀌므로 3차 리뷰(2026-08-02)는 **무효가 된다.**
   Q9 때 생략이 정당했던 근거("표면 불변")가 이제 성립하지 않는다.
5. **양 arm 40 trial 재실행** — 별도 승인.

### 5. Phase 3에서 확정해야 할 미결 설계 질문 (운영 세션이 임의로 정하지 않음)

**`removed: allowed`를 프롬프트에 어떻게 렌더링하는가?** 판정문의 정책
스키마는 표적 축을 REMOVED에서 `allowed`로 표기하지만, 그것이 프롬프트에
**명시적 허용 문장으로 렌더링되는지**, 아니면 **침묵(문장 없음)인지**를
판정하지 않았다.

- 침묵이면: REMOVED는 금지도 허용도 없는 상태. 모델이 관행적으로 출처
  속성을 안 쓸 가능성이 남는다.
- 명시적 허용이면: 이전에 없던 **새 문장**이 생기고, KEPT(금지 산문) 대
  REMOVED(허용 산문)의 비대칭이 새로 도입된다 — 조작 표면이 커진다.

Q10.2의 렌더러 요구사항 5("렌더된 모든 정책 문장이 원래 policy ID로 추적
가능한가")는 `allowed` 상태도 문장을 낼 수 있음을 함의하는 것으로 읽히나,
단정할 수 없다. **P7의 "고칠 대상을 임의로 정하지 않는다"에 해당하므로
Q11로 상신하거나 사용자 판단을 받는다.**

---

## 2026-08-03 — Q9 반입, 동결, 본 코호트 40 trial 실행, Q10 상신

### 1. Q9=A 반입·적용 (trial 0건 시점)

- `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`를 저장소로 반입 →
  `DESIGN_DECISION_H1a_evidence_symmetry.md`(기존 명명 규칙, H1a 소문자 a).
  `diff` 무출력으로 byte-identical 확인. notes 원본은 원문 보존을 위해 그대로.
- `PREREGISTRATION.md` §0.1 신설 — L1·L2(등록부 [DECLARE] 표에서 인용)와
  **L3(판정문 Q9.1 원문 그대로, 의역 없음)** 를 같은 보고 층위에 등록.
- fixture·코드 무변경(Q9=A가 명시적으로 요구).
- 4차 독립 리뷰: **사용자 승인으로 생략.** 표면(prompt/payload/fixture)이
  바뀌지 않았다는 근거.

### 2. 신규 harness 2개

| 파일 | 역할 | 규율 |
|---|---|---|
| `_h1a_cohort.py` | 동결 — qualify → payload+가드 → 양 arm 렌더 → 40 trial manifest → bundle 순서 고정 → `cohort_prompts.json` | 기존 모듈을 재구현하지 않고 호출만 한다. bundle 순서는 E2.3 `sha256_blocked_sort` 패턴, seed `H1A-fixed-order-v1`(P2에 사전등록된 값) |
| `_h1a_score.py` | 채점 — P4 제외/P5 코딩/P7 Stage A 게이트 | **trial 출력을 읽기 전에 작성했다.** 결과를 본 뒤 만든 채점 규칙은 규칙이 아니라 사후 합리화(P7 §7.2). 코딩 로직은 한 줄도 새로 쓰지 않고 전부 `_coder.code()`에 위임 |

`_h1a_surface.py`는 E2.4 동결 사본이라 **손대지 않았다**(문서화된 3개 일탈을
테스트가 고정하고 있다).

### 3. 실행 전에 닫은 구멍 — trial subject 표면 미해싱

`trial_manifest()`는 fixture/payload/prompt/schema를 해싱하지만 **trial
subject의 system prompt는 해싱하지 않는다.** E2.4가 §11.1에서 정확히 이
구멍을 찾아 `system_prompt_sha256`을 추가했던 사안이 H1a에는 반영돼 있지
않았다.

`_h1a_surface.py`를 고치지 않고(동결 사본) `_h1a_cohort.py`에서 닫았다:

- `definition_sha256` + `system_prompt_sha256` 기록
- `tools: []`를 **정의 파일에서 직접 확인** — 하네스의 agent 목록은 이
  에이전트를 "All tools"로 표시하므로, P3의 `no_tools` 주장을 검증할 수 있는
  곳은 정의 파일뿐이다
- 음성 대조: `tools: [Read, Bash]`를 주입하니 **CAUGHT** — 잡지 못하는
  가드는 장식(skills-catalog 패턴 8)

### 4. 동결 검증

| 검사 | 결과 |
|---|---|
| 재실행 결정론 | 2회 실행 byte-identical |
| fixture qualification | `passed` |
| `assert_no_model_facing_type_anchor` (§11.0) | 통과 |
| `assert_no_residual_prohibition` | 통과 — **그러나 §6 참조. 이 통과가 무엇을 뜻하는지가 이번 발견의 핵심이다** |
| `diff_is_restricted_to_the_liveness_clause` | 통과(재구성 방식) |
| 렌더 직접 확인 | KEPT에 Q1 2문장 있음 / REMOVED에 없음. 길이 2680 vs 2597 |
| 워크플로 스크립트 임베딩 | `cohort_prompts.json`의 `rendered_prompts`와 round-trip byte-identical 확인 후에만 dispatch |
| 테스트 | H1a 106 passed/1 skipped, E2.4 118 불변 |

### 5. 실행

| 항목 | 값 |
|---|---|
| transport | Workflow tool, `parallel()` × 40, `agentType: h1a-decider`, forced schema |
| run id / task id | `wf_055b8173-3b1` / `wqfunuszs` |
| 결과 | 40 dispatched / **40 done** / 0 error / 0 empty |
| 토큰·시간 | 114,330 subagent tokens / 49.7s |
| 전송 실패(P4) | **0건** — 재실행 없음, 완주 bundle 20/20 |
| 코더 교정 | 실행 직전 재측정 **18/18 passed** |

`args`를 쓰지 않고 프롬프트·trial 목록·schema를 스크립트 리터럴로 임베드했다
(skills-catalog 2026-07-30: `args`는 문자열로 도착한다). trial 신원은
`.then()` 매핑으로 workflow 반환값에 실었다 — `journal.jsonl`은 content
hash로 키를 잡아 신원 복구에 못 쓴다.

**전송 실패 함정 확인**: `agents_done: 0` / 수십 ms는 아무것도 모델에
도달하지 않았다는 뜻이다. 이번 실행은 40/40·49.7s·114k 토큰이므로 실제 실행.

행동 분포(P5.2 기계 코딩, `rationale` 미열람):

| arm | selection | deferral | invalid |
|---|---|---|---|
| PROHIBITION_KEPT | 0 | **20** | 0 |
| PROHIBITION_REMOVED | 0 | **20** | 0 |

### 6. 발견 — Q10 상신 (이번 세션의 실질 산출물)

**0/40이라는 바닥값을 "조작이 효과 없었다"로 읽지 않고 검증한 결과**, Q7=E가
도입한 warrant rule의 tie-breaker 금지가 **양 arm에 남아 있다**는 것을
찾았다. 이 fixture가 정확히 그 tie이므로(1-vs-1, 양쪽 직접 type 진술, 어느
텍스트에도 우선순위 진술 없음 → `unless` 예외 안 열림) `PROHIBITION_REMOVED`
arm도 조작 대상 행동을 여전히 금지한다.

**blocker #16의 재발**이되, 구현 오류가 아니라 판정문 자신이 그 목록을 양 arm
구속으로 명시한 것이다. 그래서 운영 세션이 고치지 않고 상신했다 — "고칠
대상을 임의로 정하지 않는다"(P7).

잔여-금지 가드가 왜 못 잡았는지가 중요하다: **잡지 않도록 의도적으로
조정돼 있었다.** bare `liveness`를 tripwire에서 뺀 이유가 "Q7's warrant rule
legitimately uses [it] ... in BOTH arms"라고 코드 주석에 적혀 있고,
`test_guard_precision_the_clean_template_passes`가 현재 template을 clean으로
적극 인증한다.

| | 명제 |
|---|---|
| 가드가 검사한 것 | "Q1 절 바이트가 REMOVED에 없는가" |
| 필요했던 것 | "REMOVED에 **동등한 금지가 남아 있지 않은가**" |

**공정하게 기록**: select_type이 논리적으로 불가능하진 않았다. Q7이 막은 것은
동점을 *출처 속성*으로 깨는 것이고, `ev3`의 반박절(= L3 비대칭)을 merit로
읽어 고르는 것은 허용된다. 40/40이 그 경로를 택하지 않았을 뿐이다.

상신: `correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md`
(Q10, 선택지 A~E + Q10.1~10.3). 인용 전수 실측 대조 완료.

### 7. 결과 데이터의 독립 교차검증

두 방향으로 확인했다(패턴 9 — 위임된 경로의 all-clean 보고를 그대로 받지
않는다):

1. **코딩**: `_coder.code()`를 거치지 않는 독립 재집계 → 동일한 20/20·20/20
2. **원시 데이터**: `journal.jsonl`(하네스가 씀, `trials_raw.json`을 뽑아낸
   task-output 파일과 **다른 경로**)의 40개 result를 정규화해 집합 비교 →
   sha256 일치(`98f409c531c03a21…`). 상세는 `h1a_attempt_log.json`

40개 rationale이 전부 상이하므로 캐시·재생이 아닌 실제 독립 표본이다.

### 8. 산출물

| 파일 | 계층 |
|---|---|
| `cohort_prompts.json` | manifest freeze (동결 후 불변) |
| `trials_raw.json` | results — 원시 출력 `{trial_id: output}` |
| `trials.json` | results — manifest + 출력 + 코딩 |
| `h1a_cohort_score.json` | 채점 요약 |
| `h1a_attempt_log.json` | **P4 요구** 시도 이력 + 독립 교차검증 |
| `h1a_cohort_workflow.js.txt` | 실행 스크립트(운영 기록) |
| 이 파일 / `docs/HANDOFF.md` / `docs/H1A_ISSUE_REGISTER.md` §H | ops-docs |

### 9. 미결 — 다음 세션

> ⚠️ **아래 1번은 2026-08-03(2)에 해소됐다** — Q10 판정이 도착했다(D-H1a-10).
> 최신 상태는 이 파일 상단 섹션. 2·3번은 여전히 유효하다.

1. ~~**Q10 판정 대기.**~~ → **도착.** Q10=E. 이번 코호트는
   `completed_nonidentifying`으로 동결 보존되고 새 코호트와 병합하지 않는다.
   **"금지를 제거해도 행동은 변하지 않았다"로 인용하는 것은 여전히 금지**이며,
   허용 문구는 `COHORT_STATUS_20260803_nonidentifying.md` §4에 있다.
2. **커밋 안 함.** 전부 미커밋. 커밋할 때는 방법론 §1의 순서를 지킨다 —
   manifest freeze / results / ops-docs를 **각각 독립 커밋**으로.
3. `_h1a_cohort.py`·`_h1a_score.py`에 대한 `test_protocol.py`급 자기검증이
   없다. 다른 실험 폴더의 표준 파일 세트에는 있다. Q10 판정에 따라 이 harness가
   재사용될지가 갈리므로 그때 판단한다.

### 10. 환경 공백 (회귀 아님)

- `owlready2` 미설치 → `test_cg_obligations.py::test_registered_handlers_resolve`
  FAIL. `HANDOFF.md` §9·§10.1이 기록한 **기존 결함**이며 이번 변경분은
  `conceptgate/`를 건드리지 않았다(`git status`로 확인).
- `fastmcp` 미설치 → `test_server.py` BLOCKED(러너가 분리 보고).
