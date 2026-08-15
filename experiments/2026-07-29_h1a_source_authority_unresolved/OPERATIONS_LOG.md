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

### 5. 남은 것 — 아직 안 함

- **Q13.3 나머지** — QF-SELECT/QF-DEFER **fixture 자체**(실제 저장소
  근거 필요, `fixture_source_authority.json`과 같은 검증 규율 — 합성
  불가) + `_h1a_score.py`(또는 별도 실행 경로)에 `_h1a_qualification.py`
  실제 배선. 지금은 채점기만 있고 잴 데이터가 없다
- **Q13.5/Q13.6** 리뷰어 capability gate + bounded semantic compiler —
  이건 **다음 독립 리뷰 자체의 절차**이지 지금 짤 코드가 아니다
- 위 전부 완료 후 **독립 리뷰 전면 재실행**(`INDEPENDENT_SEMANTIC_REVIEW_PASSED`
  여전히 `False`) → 통과해야 `repaired_cohort_trials` 40건 착수

`freeze_status: FREEZE_BLOCKED` 유지. 미푸시(커밋만, 푸시는 별도 승인).

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
