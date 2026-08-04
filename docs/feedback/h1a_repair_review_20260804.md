# 독립 리뷰 4차 — D-H1a-11 수선분 (2026-08-04)

- 지위: **동결 조건 5**(D-H1a-11 §13 `independent semantic review passed`)로
  실행된 리뷰. 결과 **FREEZE_BLOCKED**.
- 리뷰어: 별도 에이전트 **3명**, 근거 축 분할(`adversarial-review` 스킬의 설계
  원리 — persona 분할이 아니라 근거 축 분할이라 발견이 상관되지 않는다).
  전원 제작자 결론 미고지 + "제작자 테스트를 증거로 받지 말고 직접 재현하라"
  지시 + 저장소 쓰기 금지 명시(과거 리뷰 에이전트가 스스로 commit·push한
  사례 때문).
- 세 리뷰 전부 독립적으로 **FREEZE_BLOCKED** 판정.

| 축 | 판정 |
|---|---|
| 판정 충실도 (ruling fidelity) | blocker 1 + major 3 + minor 5 + clean 5 |
| 적대적 공격 (adversarial) | CRITICAL 4 + HIGH 4 + MEDIUM 3 + LOW-MEDIUM 1 |
| 실험 타당도 (validity) | blocker 3 + major 6 + minor 3 + clean 2 |

---

## 0. 제작자가 직접 재검증한 것 (리뷰어 주장을 그대로 받지 않았다)

두 건 모두 **사실로 확인**됐다.

### `assert_5_no_duplicate_forbidding_carrier`는 완전히 vacuous하다

```text
본문에서 'rendered' 등장 횟수: 0
분기1 도달: 0회 / 분기2 도달: 0회
오염된 rendered(KEPT에 recency·authority·liveness 금지 불릿 추가) → 통과
```

두 분기가 **동어반복적으로 도달 불가**다. `_q7_forbidden_axes(arm)`가
`carrier_of(a, arm) == CARRIER_Q7`로 유도되므로 `declared != CARRIER_Q7 and
axis in _q7_forbidden_axes(arm)`은 `declared == Q7 and declared != Q7`이다.
docstring은 "When `rendered` is supplied this checks that too"라고 약속하는데
매개변수를 읽지 않는다.

**이것은 이 실험이 세 번째로 같은 자리에서 실패한 것이다** — 가드가 참인 명제를
주장하지만 필요한 명제가 아니다(패턴 P1). 그리고
`PREREGISTRATION_REPAIRED_COHORT.md` §4가 carrier cardinality를 "✅ 자동"으로
표기했다. **거짓 표기였다.**

### `_h1a_cohort.py`가 보존 대상 코호트를 파괴한다

```text
ORDER_SEED: H1A-fixed-order-v1          (사전등록 요구: H1A-repaired-fixed-order-v1)
trial_id:   H1A-{arm}-{replicate:02d}   (사전등록 요구: H1AR-{arm}-{replicate:02d})
COHORT_PATH: HERE / "cohort_prompts.json"  ← 원본 코호트 동결 매니페스트
COHORT_PATH 무조건 write_text: True
'H1A-REPAIRED-01' 코드 내 존재: False
assert_freezable 호출: False
```

수선 커밋 2건(`6d46c3f`, `6b832f5`)이 이 파일을 **건드리지 않았다.** 사전등록에
새 id·seed·경로를 적어놓고 배선하지 않았다. `freeze()`를 실행하면 Q10.1이
보존을 명령한 매니페스트가 **되돌릴 수 없이** 덮어써지고, trial id가 기존 40건과
구별 불가능해진다 — `merge_original_and_repaired_cohorts: false`의 가장
비가역적인 위반.

**즉시 조치(2026-08-04)**: `freeze()`에 `CohortOverwriteRefused` fail-closed
가드 추가. 실효 확인 완료, 원본 `cohort_prompts.json` 해시가
`COHORT_STATUS_20260803_nonidentifying.md` 기록값과 일치함을 재확인(무손상).

---

## 1. 두 리뷰어가 독립적으로 수렴한 발견 — 가장 무거운 것

### 정책 계층이 실행 경로에 없다

`_h1a_cohort.build_cohort()`는 두 가드만 호출한다:

```python
contract.assert_no_residual_prohibition(...)          # 닫힌 어휘 목록
contract.diff_is_restricted_to_the_liveness_clause(...)
```

`_h1a_policy`의 단언은 **하나도 호출하지 않는다.** `assert_freezable`은
`test_h1a_policy.py`에서만 불린다. 따라서 **오늘 코호트를 만들면
2026-08-03에 실패한 바로 그 가드만이 보호한다.** 그 모듈 자신의 주석이
"run them here rather than trusting the test suite ran them last"라고 적혀
있는데 새 계층은 거기 없다.

### 산문 가드가 실제 프롬프트를 한 번도 보지 않는다

`assert_6b` / `assert_10` / `assert_11` / `assert_freezable`은 폴더 전체에서
두 방식으로만 호출된다 — 합성 문자열 `_repaired_rendered()`, 그리고
`cohort_prompts.json`. **`render_arm(load_h1a_native_template(), arm)`로는 단
한 번도 호출되지 않는다.**

적대적 리뷰어의 표현: *"asserting a true proposition about the wrong object"*
— **원 결함과 구조적으로 동일한 오류**다.

---

## 2. 적대적 공격 실측 — 새 계층은 같은 종류의 약점을 가진다

| 공격 | 결과 |
|---|---|
| REMOVED에 표적 축 금지 밀어넣기 (18종) | **11종 LEAKED** — 70개 테스트 전부 green 유지 |
| `assert_6b`가 잡은 것 | 18종 중 **1종**(옛 문구 그대로). 나머지 차단은 전부 **옛** 어휘 목록이 한 것 |
| REMOVED에 축별 허용문 (10종) | **10/10 LEAKED** — Q11=D의 핵심 금지가 영어 조동사 5개로만 집행됨 |
| 표적 축을 표현하나 토큰 목록에 없는 단어 | 33종 중 **31종 미포함** (`newer`, `fresher`, `stale`, `supersede`, `trustworthy`, `canonical`, `dead code` …) |
| 단일 셀 뮤테이션 168종 전수 | **8종이 12개 단언 + 연역 검사 전부 통과** |
| `AXIS_SURFACE_TOKENS`를 bare word로 축소 | **70 passed** — 탐지 표가 테스트로 고정돼 있지 않다 |
| `_PROHIBITION_VERBS`를 1개로 축소 | **70 passed** — 동일 |

**측정된 사각지대**: `assert_6b`는 6개 리터럴 동사가 축 토큰과 240자 이내에
있어야 발화한다. 깨끗한 REMOVED arm에서 그 중 2개만 등장하므로
**2356자 중 1511자(64.1%)가 표적 축 단어가 보이지 않는 창**이다.

`_PROHIBITION_VERBS`는 항목 6개인데, 이것이 대체한 가드는 30개였다.

---

## 3. 설계급 발견 — 운영 세션이 고칠 수 없다 (Q12 상신 대상)

### B2 (validity) — 수선이 식별 결함을 제거하지 못했을 수 있다. **가장 중대**

모델 payload에는 날짜·경로·커밋·버전 키가 **없다**(제작자 재확인). `recency`·
`authority`·`liveness`에 대응하는 packet 내부 참조물이 존재하지 않는다.
`source_kind`는 `"doc"`/`"code"` 라벨만 주고 **둘 사이의 순서는 주지 않는다.**

그런데 기본허용 규칙은 **"Within the supplied packet"** 으로 범위가 한정되고,
양 arm에 남은 Q7 불릿은 **`outside knowledge`를 금지**한다. 순서를 매기려면
"live code governs" 같은 사전지식을 들여와야 하고 그것이 정확히
`outside_knowledge`다.

따라서 이 fixture에 맞는 형식화는

```text
M_allowed = ¬Q1 ∧ ¬Q7_target ∧ ¬Q7_outside_knowledge   →   KEPT=0, REMOVED=0
```

즉 **L4 결함이 다른 담지자로 재현**된다. `target_mechanism_allowed()`는
`TARGET_AXES`만 순회하므로 `target_mechanism_contrast: True`는 **참이지만
무관하다** — 패턴 P1의 일곱 번째 사례. D-H1a-10 §5는 `outside knowledge`가
조작과 "무관"하다고 단정했는데, 이 fixture에서는 표적 축이 그것의 **사례**다.

### B1 (validity) — 공통 defer 불릿이 이 fixture 모양을 defer로 명명한다

양 arm 공통: *"Choose defer if the packet does not warrant selecting exactly one
allowed type, **including cases where support is conflicting**"* 이고, fixture
자신의 `builder_metadata.purpose`가 *"This is a genuine 1-vs-1 conflict"* 다.

**G3의 재발이다.** `_h1a_contract.py:15-20`이 Q3=B가 규칙 3을 지운 이유를
"rule 3 step 4 maps H1a's exact fixture shape ... to a hard `selected_type =
null`, independent of the liveness manipulation"이라고 기록해 뒀는데, Q7=E가
더 부드러운 문구로 같은 매핑을 재도입했고 아무도 G3 검사를 다시 돌리지 않았다.

### B3 (validity) — demand neutralizer가 처치 자체를 무효화할 수 있다

*"Permission to consider a basis does not by itself warrant selecting a type"* —
의도는 "허용이라는 사실이 warrant는 아니다"이지만, "그 근거는 warrant가
아니다"로도 읽힌다. B2 아래에서 source-property가 arm 간 유일한 차이라면, 이
문장이 그 근거를 warrant에서 배제한다고 읽히는 순간 REMOVED에 새 경로가 없다.

### 판정문 내부 충돌 — §5 대 §10 assertion 12

`assert_12`가 통과하는 이유는 토큰 목록이 한국어 `우선순위`는 별칭으로
선언하면서 영어 `priority`는 빼놨기 때문이다. 렌더된 공통 Q7에는 판정문 §5
자신의 문구 *"unless that **priority** is directly stated"* 가 있고,
`priority`를 토큰에 추가하면 `assert_12`가 즉시 발화한다. **§5의 처방 문구와
§10의 단언 12가 서로 충돌**하며, 구현이 그것을 조용히 해소했다.

### 기타 설계급

- **M7**: mention-vs-prohibition 교란. 표적 축이 KEPT에서만 명명되고,
  "unless this prompt explicitly prohibits it"이 금지 열거를 지시하므로
  REMOVED에서는 `outside knowledge`가 오히려 더 부각될 수 있다. 옵션 B를
  기각한 사유가 부호만 바뀌어 재현.
- **M8**: merit 경로와 authority 경로가 **같은 type**(`structural_composition`)을
  가리켜 `selected_type` 분포가 경로 정보를 담지 못한다.
- **M4**: 프롬프트 표면 ceiling을 잡는 유일한 사전등록 장치(§11.2a, Q4 승인,
  범위가 명시적으로 prompt surface까지 넓혀진 것)가 §11 배너로 무효화됐고,
  대체물은 ceiling에 대해 아무것도 말하지 않는다.

---

## 4. 제작자 자신의 사전등록 문안 결함 (운영 세션이 고칠 것)

- **M5**: §7의 발동 조건("양 arm이 같은 modal 범주")과 처방값
  (`observed_zero`)이 **동일 외연이 아니다.** KEPT 20 defer / REMOVED 12 defer +
  8 select는 같은 modal 범주인데 zero contrast가 아니다. 현 문안은 40%p 대비를
  zero로 보고하도록 허용한다. 그리고 **차이가 났을 때의 보고 형식이 없다** —
  거짓 null에는 엄격하고 거짓 양성에는 침묵.
- **M6**: §7의 manipulation check가 P5.4를 근거로 인용하는데, P5.4는 **KEPT**
  arm에 대한 것이고 성공/실패 표기를 금지한다. §7은 REMOVED로 범위를 바꾸고
  manipulation check(= 성공/실패 판정)로 용도를 바꿨다 — 패턴 P4(아티팩트가
  자기 근거를 잘못 서술).
- **m11**: §1 승계표가 §10(freeze-before-run 순서)과 §11.0을 누락.

---

## 5. clean confirmation — 실제로 견고한 부분

- **28개 셀 3중 대조 무불일치**(판정문 §7 / §9 YAML / 사전등록 §2 / 코드).
- **기본허용 문구 byte-identical** — 판정문 §1·§5와 211자 완전 일치, 양 arm 동일.
- **arm-diff**: 독립 방법(`SequenceMatcher` + 공통 접두·접미 계산)으로 재현,
  비동일 opcode **정확히 1개**(Q1 절 + 선행 공백 1). delta 83.
- **L5 verbatim 등재** 확인.
- **구조적 생성 부분은 실제로 건전하다** — Q7 목록을 표에서 생성하므로 그
  영역 안에서는 duplicate-carrier drift가 불가능하다.
- **조건 5의 순서**가 옳다 — 기계 검사가 먼저 돌고 리뷰 플래그가 마지막이라
  구조 결함을 가리지 않는다(전용 테스트로 고정됨).
- **L2는 확대되지 않았다** — 한국어 바이트 불변, 새 한국어 없음.

---

## 6. 이 리뷰가 확인한 방법론적 사실

**독립 리뷰 3회를 통과한 설계가 실행 후 식별 결함을 드러냈고(Q10), 그 수선분이
다시 3명의 리뷰어에게 전부 blocked 판정을 받았다.** 그리고 이번 리뷰가 잡은
것 중 두 건은 **제작자가 같은 세션에서 작성하고 테스트까지 붙인 코드**의
결함이다(vacuous `assert_5`, 실행 경로 미배선).

- **가드가 통과한다는 사실은 가드가 무엇을 주장하는지와 무관하다.** 세 번째
  재발이며, 이번에는 가드가 매개변수를 아예 읽지 않았다.
- **테스트가 green이라는 사실도 마찬가지다.** 탐지 표를 축소해도 70 passed다.
- **근거 축 분할이 값을 냈다.** 세 리뷰어의 발견이 두 곳에서만 수렴했고
  (실행 경로 미배선, 산문 가드가 합성 객체를 본다) 나머지는 전부 서로 달랐다.
  단일 리뷰어였다면 대부분을 놓쳤을 것이다.
