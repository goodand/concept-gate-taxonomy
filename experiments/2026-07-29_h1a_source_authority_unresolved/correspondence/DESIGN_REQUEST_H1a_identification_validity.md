# 설계 판정 요청 — 표적 기제가 양 arm에서 봉쇄되는가 (Q12)

- 작성: 2026-08-05
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 파일을 열지 않고 판정할 수 있게 썼다.
- 계기: **D-H1a-11(Q11=D, Q11.1=A, Q11.2=A) 반입·구현 완료 후 독립 리뷰 3명이
  전원 `FREEZE_BLOCKED`.** 운영 세션이 고칠 수 있는 것(공허한 가드, 코호트
  파괴 경로, 정책 계층 미배선)은 고쳤다. 남은 것은 **설계급**이어서 운영
  세션이 고칠 권한이 없다.
- 실행된 trial: **최초 코호트 40건**(`completed_nonidentifying`으로 동결 보존,
  D-H1a-10 Q10.1). **수선 코호트는 0건.** 따라서 이 판정도 **실행 전** 판정이다.
- 선행 판정 7건(전부 구속력 유지, 재론하지 않음): `DESIGN_DECISION.md`
  (D-H1a-1~7) / `_manipulation_scope`(Q1=B, Q2=B) / `_prompt_surface`
  (Q3=B, Q4) / `_review_blockers`(Q5=B, Q6=A, Q7=E, Q8=B) /
  `_evidence_symmetry`(Q9=A, Q9.2) / `_residual_prohibition`(D-H1a-10,
  Q10=E, Q10.1, Q10.2, Q10.3) / `_allowed_rendering`(D-H1a-11, Q11=D,
  Q11.1=A, Q11.2=A)

> **브랜치 주의 (배치상 사실, 판정과 무관)**
> 이 파일은 `codex/entailed-is-a-contract` 브랜치에서 작성됐다. 세션 격리
> 때문이다. 이 브랜치에는 인용 대상인 `DESIGN_DECISION_H1a_allowed_rendering.md`
> (D-H1a-11)와 `PREREGISTRATION_REPAIRED_COHORT.md`가 **없다** — h1 브랜치
> (`codex/h1-source-authority`)에만 있다. 이 커밋을 그 브랜치로
> **cherry-pick**해야 문서가 자기 이웃을 가리킨다. 손으로 복사하지 말 것
> (`CLAUDE.md` Project Structure: worktree 간 손복사 금지, 커밋 전파).

---

## 0. 한 줄 요약

**이 실험의 처치가 어느 arm에서도 표적 기제를 허용하지 않을 수 있다.** 운영
세션이 리뷰어 주장을 그대로 받지 않고 직접 재측정했고, **확인됐다.** 그렇다면
`PROHIBITION_REMOVED`는 "금지가 제거된 arm"이 아니라 "금지가 제거되었으나
행사할 licensed 경로가 없는 arm"이고, 관측될 null은 가설에 대한 증거가 아니라
**설계에 대한 증거**다. 재설계 방향은 여러 갈래이고 그중 둘은 이미 내려진
판정과 충돌하므로 운영 세션이 고를 수 없다.

---

## 1. 현재 바이트 — 실측 (2026-08-05, 수선 후)

### 1.1 양 arm의 정책 블록은 **완전히 동일하다**

D-H1a-11 Q11=D의 요구대로 기본허용 규칙이 양 arm에 byte-identical하게 방출되고,
공통 Q7 목록에서 표적 축 4개가 제거됐다. 렌더 결과 전문:

```text
[PROHIBITION_KEPT]  GLOBAL_DEFAULT_PERMISSION
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. Permission to consider a basis does not by
itself warrant selecting a type or favor either allowed type.

[PROHIBITION_KEPT]  Q7_TIEBREAKER_LIST
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence
  item's text.
```

```text
[PROHIBITION_REMOVED]  GLOBAL_DEFAULT_PERMISSION
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. Permission to consider a basis does not by
itself warrant selecting a type or favor either allowed type.

[PROHIBITION_REMOVED]  Q7_TIEBREAKER_LIST
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence
  item's text.
```

**두 arm의 정책 블록 diff = 없음.**

### 1.2 arm 간 유일한 차이 — KEPT에만 삽입되는 Q1 절

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

표적 축: `source_kind_priority`, `recency`, `authority`, `liveness`.

### 1.3 모델 payload에 표적 축의 내부 참조물이 **없다**

날짜·경로·커밋·버전 키가 payload에 없다(제작자 재확인). `source_kind`는
`"doc"`/`"code"` 라벨만 주고 **둘 사이의 순서는 주지 않는다.**

### 1.4 fixture의 evidence 텍스트가 우선순위를 **전혀 진술하지 않는다** (신규 실측)

공통 Q7에는 예외 조항이 있다 — *"unless that priority is **directly stated
inside an evidence item's text**"*. 이 조항이 발동하면 REMOVED에 licensed
경로가 생기므로, 운영 세션은 리뷰어의 `M_allowed = 0` 주장을 받기 전에 fixture를
직접 스캔했다. evidence 텍스트 전문(2건이 전부):

```text
[evidence_sources[0].text]
(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)

[evidence_sources[1].text]
        "(4) 재료-대상: 철은 칼의 재료 → structural_composition "
        "(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)\n"
```

우선순위·최신성·권위 어휘 스캔 결과 **evidence 텍스트에서 0건**. 검출된 5건은
전부 `builder_metadata`에 있고, 그 필드 자신이 이렇게 적고 있다:

```text
[builder_metadata.liveness_is_harness_only]
That the documentation is older than the code is knowledge held by the harness
and by readers of README §3. It is NOT in this fixture and does not reach
the model.
```

**따라서 예외 조항은 이 fixture에서 발동하지 않는다.** 리뷰어의 주장이 실측으로
확인됐다.

---

## 2. Q12 — 표적 기제가 양 arm에서 봉쇄된 것을 어떻게 처리하는가

### 2.1 형식화

기본허용 규칙의 범위는 `Within the supplied packet`으로 한정된다. 표적 축으로
두 출처의 순서를 매기려면 *"live code governs"* 류의 사전지식이 필요하고, 그것이
정확히 공통 Q7이 금지하는 `outside knowledge`다. §1.4가 예외 조항의 부재를
확인했으므로:

```text
M_allowed(arm) = ¬Q1(arm) ∧ ¬Q7_outside_knowledge ∧ (packet이 우선순위를 진술)

  KEPT    : ¬Q1 = 0                       → M_allowed = 0
  REMOVED : ¬Q1 = 1, 그러나 뒤 두 항 = 0   → M_allowed = 0
```

**대비 = 0 − 0 = 0.** `target_mechanism_contrast: True`는 `TARGET_AXES`만
순회하기 때문에 참이며, **참이지만 무관하다** — 패턴 P1(가드가 참인 명제를
검사하나 필요한 명제가 아니다)의 또 하나의 사례.

### 2.2 이것이 D-H1a-10 §5와 충돌한다

D-H1a-10 §5는 `outside knowledge`가 조작과 **무관**하다고 단정하여 공통 Q7에
남기도록 판정했다. 그러나 이 fixture에서 표적 축 4개는 `outside_knowledge`의
**사례**다 — 판정 당시 이 포섭 관계가 검토되지 않았다.

### 2.3 선택지

| # | 내용 | 알려진 충돌·비용 |
|---|---|---|
| **A** | fixture payload에 표적 축의 내부 참조물을 넣는다(날짜·경로·커밋 노출) | **D-H1a-3/Q3=B와 `assert_no_model_facing_type_anchor`와 충돌.** payload에서 정답 앵커를 제거한 것이 그 판정의 핵심이었다. 경로·날짜는 liveness의 앵커가 되어 오라클 유출로 되돌아간다 |
| **B** | 공통 Q7에서 `outside knowledge` 금지를 제거한다 | D-H1a-10 §5를 뒤집는다. 또한 `evidence_count`·`source_order`와 한 불릿에 묶여 있어 그 두 축의 통제가 함께 풀린다 |
| **C** | evidence 텍스트 **자체**가 우선순위를 진술하도록 fixture를 교체한다(Q7 예외 조항을 정당하게 발동) | 예외 조항을 쓰므로 기존 판정과 충돌하지 않는다. 대신 새 fixture가 필요하고, "텍스트가 우선순위를 말하면 그건 이미 packet 내부 근거"라서 **가설이 source-authority에서 in-text-priority로 이동**한다 |
| **D** | 표적 축이 `outside_knowledge`의 하위사례임을 인정하고 **가설을 재정의**한다(측정 대상을 "출처 속성 기반 판정"에서 "prompt가 금지한 근거의 사용"으로) | 실험이 성립하지만 H1의 원래 질문에서 멀어진다 |
| **E** | H1a를 **성립 불가로 판정하고 종료**, 별도 실험으로 분리한다 | 40건 코호트와 수선 작업이 negative result로 남는다. E2.4 `conflicting` class가 같은 자리에서 이 경로를 택한 선례가 있다 |

**운영 세션은 A~E 중 어느 것도 단독으로 고를 수 없다** — A와 B는 선행 판정을
뒤집고, C·D는 가설을 바꾸고, E는 실험을 종료한다.

---

## 3. Q12.1 — 공통 defer 불릿이 이 fixture 모양을 defer로 명명한다 (G3 재발)

양 arm 공통 문안:

```text
Choose defer if the packet does not warrant selecting exactly one allowed
type, including cases where support is conflicting.
```

fixture 자신의 `builder_metadata.purpose`:

```text
This is a genuine 1-vs-1 conflict
```

**G3의 재발이다.** `_h1a_contract.py:15-20`이 Q3=B가 규칙 3을 지운 이유를
기록해 뒀다 — *"rule 3 step 4 maps H1a's exact fixture shape ... to a hard
`selected_type = null`, independent of the liveness manipulation"*. Q7=E가 더
부드러운 문구로 **같은 매핑을 재도입**했고, 그 시점에 G3 검사를 다시 돌린
사람이 없다.

선택지: (a) 불릿 유지(대비 소실을 한계로 선언) / (b) `including cases where
support is conflicting`만 삭제 / (c) 불릿 전체 삭제 / (d) fixture를 1-vs-1
conflict가 아닌 모양으로 교체(Q12=C와 묶임).

---

## 4. Q12.2 — demand neutralizer가 처치를 무효화할 수 있다

D-H1a-11이 명령한 중립화 문장:

```text
Permission to consider a basis does not by itself warrant selecting a type
or favor either allowed type.
```

의도는 *"허용이라는 사실 자체가 warrant는 아니다"*이지만, *"그 근거는 warrant가
아니다"*로도 읽힌다. Q12 아래에서 source-property가 arm 간 유일한 차이라면,
후자로 읽히는 순간 REMOVED에 새 경로가 없다.

선택지: (a) 유지 / (b) 삭제(demand characteristic 위험을 되받는다) /
(c) 재문안 — 예: *"The fact that this prompt does not prohibit a basis is not
itself a reason to select a type."*

---

## 5. Q12.3 — 판정문 내부 충돌: D-H1a-11 §5 대 §10 assertion 12

`assert_12_common_q7_excludes_target_axis_strings_and_aliases`가 통과하는 이유는
토큰 목록이 한국어 `우선순위`는 별칭으로 선언하면서 영어 `priority`는 빼놨기
때문이다. 그런데 렌더된 공통 Q7에는 판정문 §5 **자신의 처방 문구**가 들어 있다:

```text
... unless that priority is directly stated inside an evidence item's text.
```

`priority`를 별칭 토큰에 추가하면 `assert_12`가 **즉시 발화**한다. 즉 §5의
처방 문구와 §10의 단언 12가 서로 충돌하며, 구현이 그 충돌을 조용히 해소했다.

선택지: (a) §5 문구 우선 — `priority`를 토큰에서 영구 제외하고 그 이유를
단언에 문서화 / (b) §10 우선 — §5 문구를 `that ordering` 등으로 재문안 /
(c) 예외 조항 자체를 삭제(Q12=C를 배제하는 효과).

**이 항목은 어느 쪽이든 판정이 필요하다** — 현 상태는 "토큰 목록이 우연히
불완전해서 통과"이고, 그건 근거가 아니다.

---

## 6. Q12.4 — `assert_9`의 raise 경로 3개가 모두 도달 불가 (2026-08-05 신규)

이번 세션에 도입한 가드 음성-테스트 게이트(`test_guard_negative_coverage.py`,
커밋 `d8db0eb`)가 `assert_9_default_permission_is_byte_identical_across_arms`를
**음성 테스트 없는 가드**로 지목했다. 음성 테스트를 쓰려 했으나 쓸 수 없었다:

```python
# _h1a_policy.py — render_policy_block()
out: list[tuple[str, str]] = [(CARRIER_DEFAULT, GLOBAL_DEFAULT_PERMISSION_TEXT)]
```

`render_policy_block`이 **모듈 상수를 직접 읽어 양 arm에 무조건 방출**하므로
`assert_9`의 세 명제가 코드에 의해 구조적으로 참이 된다:

| raise 경로 | 도달 가능성 |
|---|---|
| 기본허용 블록 개수 != 1 | 방출이 무조건적 → 불가 |
| arm 간 텍스트 불일치 | 양 arm이 같은 상수 → 불가 |
| 상수로부터 drift | 비교 대상이 그 상수 자신 → 불가 |

발동시키려면 `render_policy_block`을 모킹해야 하고, 그러면 **모킹을 검증하는
셈**이다. 운영 세션은 음성 테스트를 날조하지 않고 `KNOWN_UNPROVEN`에 이유와
담당을 적어 공백을 가시화했다.

이것은 D-H1a-11 §10의 12개 구조 단언 중 하나이므로 판정이 필요하다.

선택지: (a) 잉여로 판정하고 assertion 9를 철회 / (b) `render_policy_block`이
상수를 직접 읽지 않게 하고(예: 렌더 결과를 판정문 바이트와 독립 비교) 단언을
유효하게 만든다 / (c) 현행 유지 + `KNOWN_UNPROVEN` 등재를 영구 승인.

**주의**: (a)를 택하면 "판정문 바이트로부터의 drift를 아무도 검사하지 않는"
상태가 된다. D-H1a-11이 그 검사를 요구한 취지와 상충하는지 확인이 필요하다.

---

## 7. 추가 설계급 3건 — 판정 필요 여부 자체를 묻는다

리뷰가 설계급으로 분류했으나 위 항목들에 종속될 수 있다. **각각 독립 판정이
필요한지, Q12의 결과에 따라 자동 해소되는지**를 알려주기 바란다.

- **M7 (mention-vs-prohibition 교란)**: 표적 축이 KEPT에서만 명명되고,
  `unless this prompt explicitly prohibits it`이 금지 열거를 지시하므로
  REMOVED에서는 `outside knowledge`가 오히려 더 부각될 수 있다. 옵션 B를
  기각한 사유가 부호만 바뀌어 재현.
- **M8 (경로 정보 소실)**: merit 경로와 authority 경로가 **같은 type**
  (`structural_composition`)을 가리켜 `selected_type` 분포가 어느 경로로
  도달했는지를 담지하지 못한다.
- **M4 (ceiling 장치 소실)**: 프롬프트 표면 ceiling을 잡는 유일한 사전등록
  장치(§11.2a, Q4 승인, 범위가 명시적으로 prompt surface까지 확장된 것)가
  §11 배너로 무효화됐고, 대체물은 ceiling에 대해 아무것도 말하지 않는다.

---

## 8. 판정 전까지 운영 세션이 하는 것 / 하지 않는 것

**한다**

- 최초 코호트 40건의 `completed_nonidentifying` 동결 보존 유지(D-H1a-10 Q10.1).
  산출물 11종 sha256은 `COHORT_STATUS_20260803_nonidentifying.md`에 고정
- 운영 세션 소관 결함 수리: 리뷰 §4의 M5·M6·m11(사전등록 문안)
- 가드 음성-테스트 게이트 유지. `assert_9`는 `KNOWN_UNPROVEN`에 가시화된 상태

**하지 않는다**

- **수선 코호트 실행 0건 유지.** 이 판정 전에 trial을 돌리지 않는다
- fixture·payload·공통 Q7·중립화 문장 변경 — 전부 이 요청서의 판정 대상
- `INDEPENDENT_SEMANTIC_REVIEW_PASSED` 플래그 전환. 동결 게이트는 차단 상태 유지
- Q12=E(종료) 방향으로의 선제 정리

---

## 9. 이 요청서의 지위

판정 요청이다. **운영 세션의 §2.3 표는 선택지 열거이며 권고가 아니다.**
판정이 오면 `DESIGN_DECISION_H1a_identification_validity.md`로 동결 기록하고,
`PREREGISTRATION.md`는 고치지 않고 필요한 변경은 새 사전등록 문서로 남긴다
(D-H1a-10 §11의 7항 절차).

**이 문제가 이미 다뤄졌는지 먼저 찾았다** (`CLAUDE.md`의 "아직 안 풀렸다고
단정하지 마라"): D-H1a-10 §5가 `outside knowledge`를 조작과 무관하다고 판정한
것이 이 문제에 **가장 가까운 선행 판정**이며, 이 요청서는 그 판정의 전제
(포섭 관계 부재)가 이 fixture에서 성립하지 않음을 실측으로 제시한다.
E2.4 `PROBLEM_2_conflicting.md` §5는 "실제 저장소가 모순된 동등강도 쌍을 보존할
이유가 없다"는 같은 계열의 구조적 결론에 도달해 별도 실험으로 분리했고, 그것이
Q12=E의 선례다. 그 외에 이 질문을 해소하는 판정은 찾지 못했다.

---

## 10. 운영 세션 의견 (판정 아님, 참고용)

§1.4의 실측 때문에 Q12는 "리뷰어가 그럴 수도 있다고 말한 것"이 아니라
**확인된 사실**로 취급되어야 한다고 본다. 그 위에서 A와 B는 선행 판정을
뒤집으므로 비용이 가장 크고, C는 가설을 in-text-priority로 옮기지만 기존
판정과 충돌하지 않으며 Q7 예외 조항을 **설계된 용도대로** 쓴다. D는 측정
대상을 넓혀 실험을 살리되 H1의 원 질문에서 멀어진다. E는 정직하지만 40건과
수선 작업을 negative result로 남긴다.

다만 이것은 의견이고, Q12.3(§5 대 assertion 12)의 판정이 C의 가용성을
좌우하므로 **Q12.3을 먼저 판정하는 것이 순서상 유리할 수 있다** — 예외 조항을
삭제하는 (c)를 택하면 C가 자동으로 배제된다.
