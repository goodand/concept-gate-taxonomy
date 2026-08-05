# H1a 사전등록 — 수선 코호트 (D-H1a-10-R2)

- 작성: 2026-08-04
- 지위: **사전등록.** 수선 코호트 trial **0건 시점**에 작성된다.
- 왜 새 문서인가: `PREREGISTRATION.md`는 **최초 코호트의 동결 기록**이고, 그
  코호트는 실행됐다(`COHORT_STATUS_20260803_nonidentifying.md`). 방법론 §1이
  결과가 설계를 소급 수정하지 못하게 하라고 요구하므로 그 문서를 고쳐 쓰지 않고
  새로 만든다. D-H1a-10-R2도 "새 사전등록"을 명시했다.
- 근거 판정: `DESIGN_DECISION_H1a_residual_prohibition.md`(D-H1a-10) +
  `DESIGN_DECISION_H1a_allowed_rendering.md`(**D-H1a-11**)

> ## 🔴 이 문서만으로 trial을 실행하지 마라 (2026-08-05, D-H1a-12로 부분 대체)
>
> 독립 리뷰 3명 전원이 이 문서가 반영한 설계를 `FREEZE_BLOCKED`로 판정했다
> (`docs/feedback/h1a_repair_review_20260804.md`) — §2의 정책 계약(Q11.2=A
> 담지자 표)과 §4의 freeze gate(5조건)가 **표적 대비를 봉쇄한다는 게 이유다**
> (표적 축이 `outside_knowledge`에 포섭되어 양 arm 모두 봉쇄, B2 발견).
> 그 뒤 받은 `DESIGN_DECISION_H1a_identification_validity.md`(D-H1a-12,
> Q12=F typed-scope split)가 §2의 정책 계약을 **다시 설계**했고, §4의
> 5조건 freeze gate 대신 **§16의 12조건**이 적용된다. §0·§1·§3·§5·§6·§7은
> 그대로 유효하다 — 바뀐 건 §2(정책 계약)와 §4(gate 조건 개수·내용)뿐이다.
> **실행 전 체크리스트는 `docs/HANDOFF.md` §10.4 또는
> `DESIGN_DECISION_H1a_identification_validity.md` §16을 따르고, 이 문서의
> §2·§4를 그대로 구현으로 옮기지 마라.**

---

## 0. 이 코호트가 최초 결과를 아는 상태에서 설계됐다는 공개 (D-H1a-10 §11)

판정문이 요구한 7항을 그대로 등재한다. **이 코호트를 최초 코호트와 같은
의미의 사전등록이나 독립 복제라고 부르지 않는다.**

```text
1. 최초 코호트 결과는 양 arm 20/20 defer였다.
2. 최초 결과 확인 후 공통 Q7 규칙의 의미적 중복이 발견되었다.
3. 재설계 사유는 결과의 방향이 아니라 동결 프롬프트의 구조적 대조다.
4. 기존 coder와 outcome 정의는 변경하지 않는다.
5. 기존 코호트와 수정 코호트를 병합하지 않는다.
6. 수정된 양 arm을 모두 새로 실행한다.
7. 수정 코호트는 post-result design revision임을 기록한다.
```

3항의 실질: 재설계를 촉발한 관측은 **두 프롬프트의 바이트 대조**이며, 그것은
행동 결과를 보지 않고도 성립한다. 다만 **발견 시점이 사후라는 사실은 지워지지
않는다.**

---

## 1. 승계 — 최초 사전등록에서 변경 없이 가져오는 것

| 항목 | 상태 |
|---|---|
| §0 허용 결론의 상한(K=1) | **불변.** N을 늘려도 상한은 오르지 않는다 |
| P1 시행 수 arm당 20 / 총 40 | **불변** |
| P2 randomization (bundle, `sha256_blocked_sort`) | **불변.** seed는 §5에서 새로 지정 |
| P3 모델 파라미터 (`claude-opus-5`, `tools: []`, cold subagent, temperature 설정 불가) | **불변** |
| P4 제외 기준 (전송 실패만 재실행, 내용 기반 제외 없음) | **불변** |
| **P5 행동 코딩** | **불변.** D-H1a-10 §11-4가 명시적으로 요구 — 코더는 `rationale`을 읽지 않는다 |
| P6 invalid 처리 (제3 범주, 분모 포함) | **불변** |
| P7 종료 기준 (결과 방향 조기종료 없음) | **불변** |
| 코더 교정 코퍼스 18건 | **불변.** 실행 직전 재측정 |
| fixture (`ev1`/`ev3` 1-vs-1, byte-faithful) | **불변.** Q9=A |

**변경되는 것은 프롬프트 표면 하나뿐이다.** fixture·스키마·코더·payload는
건드리지 않는다.

---

## 2. 동결되는 정책 계약 — 축 × arm × 담지자 (Q11.2=A)

**Q11.2=A가 이 표를 사전등록 장치로 지정했다. 이 표를 바꾸는 것은 renderer
refactor가 아니라 experiment amendment다.**

| policy axis | KEPT state | KEPT carrier | REMOVED state | REMOVED carrier |
|---|---|---|---|---|
| `evidence_count` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` |
| `source_order` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` |
| `outside_knowledge` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` | `explicitly_forbidden` | `Q7_TIEBREAKER_LIST` |
| `source_kind_priority` | `explicitly_forbidden` | `Q1_LIVENESS_CLAUSE` | **`allowed_by_default`** | `GLOBAL_DEFAULT_PERMISSION` |
| `recency` | `explicitly_forbidden` | `Q1_LIVENESS_CLAUSE` | **`allowed_by_default`** | `GLOBAL_DEFAULT_PERMISSION` |
| `authority` | `explicitly_forbidden` | `Q1_LIVENESS_CLAUSE` | **`allowed_by_default`** | `GLOBAL_DEFAULT_PERMISSION` |
| `liveness` | `explicitly_forbidden` | `Q1_LIVENESS_CLAUSE` | **`allowed_by_default`** | `GLOBAL_DEFAULT_PERMISSION` |

구현: `_h1a_policy.py::DECISION_BASIS_POLICY`.
`test_h1a_policy.py::test_table_matches_the_ruling_sec_7_verbatim`가 셀 단위로
고정한다.

### 2.1 REMOVED의 표적 축은 `unspecified`가 아니다

D-H1a-11 §9가 명시했다. 상태는 **`allowed_by_default`** 이고, 그 허용을
담지하는 것은 양 arm 공통의 기본허용 규칙이다. 이 구분이 Q11=D의 요점이며,
`unspecified`(= 폐기된 선택지 A)와 혼동하면 안 된다.

### 2.2 carrier의 의미 (D-H1a-11 §8)

> 해당 axis의 최종 정책 상태를 규범적으로 결정하는 **유일한** 권위 경로.

- 한 carrier가 여러 axis를 담당할 수 있다(`Q1_LIVENESS_CLAUSE`가 표적 4축).
- **한 axis × arm 상태가 복수 carrier로 결정되어서는 안 된다.** 이것이
  blocker #16과 Q10의 구조이며, 구조 단언 2·5·7이 막는다.

### 2.3 scope constraint는 carrier가 아니다

```yaml
scope_constraints:
  - PACKET_ONLY
  - NO_EXTERNAL_SOURCES
```

packet boundary 문장("Use only the packet fields presented in this prompt.
Do not use general ontology knowledge, ... or external sources.")은 판단 근거의
**출처 범위**를 제한하지만, 특정 axis를 `forbidden`으로 바꾸지 않는 한 그
axis의 carrier로 계산하지 않는다. 최초 구현이 이것을 `outside_knowledge`의 두
번째 carrier로 선언했던 것을 D-H1a-11 §8이 정정했다.

---

## 3. 동결되는 프롬프트 표면

### 3.1 양 arm 공통 — 기본허용 규칙 (신규, byte-identical)

```text
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. Permission to consider a basis does not by
itself warrant selecting a type or favor either allowed type.
```

두 번째 문장이 **demand neutralizer**다(D-H1a-11 §13 `demand_neutralizer:
required`) — 허용이 선택 권장으로 읽히는 것을 막는다.

### 3.2 양 arm 공통 — 수선된 Q7 tie-breaker 목록

표적 4축이 빠지고 비표적 3축만 남는다:

```text
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence
  item's text.
```

### 3.3 KEPT에만 — Q1 절 (바이트 불변)

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

### 3.4 REMOVED — 축별 허용문 없음

Q11=D가 **금지**한다. REMOVED의 표적 축 허용은 §3.1의 공통 규칙에서 나온다.

### 3.5 arm-diff 계약 (D-H1a-11 §11)

```yaml
arm_diff:
  allowed_regions:
    - Q1_LIVENESS_CLAUSE
  common_new_text:
    - GLOBAL_DEFAULT_PERMISSION
    - REPAIRED_Q7_TIEBREAKER_LIST
```

공통 템플릿이 바뀌지만 **arm 간 차이는 확대되지 않는다.** 수선 전 프롬프트와
수선 후 프롬프트가 같다는 주장은 하지 않는다 — R2에 따라 양 arm 모두 새로
실행한다.

---

## 4. 동결 게이트 (D-H1a-11 §13 `freeze_gate`)

`status_before_implementation: blocked`. 다섯 조건이 **논리곱**으로 충족돼야
해제된다.

| # | 조건 | 검사 지점 | 상태 |
|---|---|---|---|
| 1 | policy schema valid | 구조 단언 1·2·3·4 | ✅ 자동 |
| 2 | carrier cardinality valid | 구조 단언 2·5·7 | ✅ 자동 |
| 3 | common default permission byte-identical | 구조 단언 9 | ✅ 자동 |
| 4 | arm diff restricted to Q1 clause | 구조 단언 10·11 + `diff_is_restricted_to_the_liveness_clause` | ✅ 자동 |
| 5 | **independent semantic review passed** | **기계 검사 불가** | ⬜ **미충족** |

조건 5는 코드로 검증할 수 없다. 이 프로젝트의 `pass-is-a-conjunction` 규율에
따라 **검사 불가 조건은 명명하고 담당을 배정한다** —
`_h1a_policy.py::INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`이고
`assert_freezable()`이 그 값이 False인 동안 `FreezeGateBlocked`를 던진다.
리뷰 보고서를 커밋하는 **같은 커밋에서만** True로 바꾼다.

`test_freeze_gate_runs_the_machine_checkable_conditions_before_failing`이
조건 5가 구조적 결함을 **가리지 못하도록** 고정한다 — 구조가 깨져 있으면
게이트는 리뷰 플래그가 아니라 그 결함을 보고해야 한다.

### 4.1 독립 리뷰 지시 (조건 5)

- **별도 에이전트.** 제작자(이 세션)의 결론을 고지하지 않는다.
- **제작자의 테스트를 증거로 받지 말고 직접 재현하라**고 명시한다 — 이 실험의
  리뷰 3회 전부 그 지시가 있었고, 매번 제작자 테스트는 통과 중이었다.
- 우선 점검 대상: (a) 기본허용 규칙이 salience를 만들지 않는가, (b) REMOVED에
  잔여 금지가 정말 없는가(가드를 신뢰하지 말고 렌더된 프롬프트를 직접 읽어라),
  (c) 영어 본문 + 한국어 Q1 절의 혼용(L2)이 확대되지 않았는가.

---

## 5. 실행 규약

| 항목 | 값 |
|---|---|
| cohort id | `H1A-REPAIRED-01` (최초 코호트와 구별되는 새 식별자) |
| N | arm당 20, 총 40 |
| randomization seed | `H1A-repaired-fixed-order-v1` (최초의 `H1A-fixed-order-v1`과 다르게 지정 — 같은 seed를 재사용하면 두 코호트의 순서가 겹쳐 독립성이 흐려진다) |
| trial id | `H1AR-{arm}-{replicate:02d}` |
| 병합 | **금지.** 최초 40 trial을 표본 수에 포함하지 않고, 기존 arm 하나를 재사용하지 않으며, 두 코호트를 합산하지 않는다 |
| 단계 | Stage A(10) → 하네스 점검 → Stage B(30). 최초와 동일 |

---

## 6. 한계 선언 — L1~L5

L1·L2·L3는 `PREREGISTRATION.md` §0.1에서 그대로 승계한다. L4는 **최초 코호트
전용**이라 이 코호트에 적용되지 않는다. L5가 신규다.

| # | 성격 | 이 코호트에 적용 |
|---|---|---|
| L1 | evidence-reading rule이 select 쪽에만 작용 | ✅ 승계 |
| L2 | 조작이 언어 전환과 분리 불가(영어 본문 + 한국어 절), placebo arm 없음 | ✅ 승계. **D-H1a-11 §4가 L2 해소를 `out_of_scope`로 판정** — 확대하지도 않는다 |
| L3 | evidence 내용 비대칭(`ev3`가 반박, `ev1`은 지지만) | ✅ 승계 |
| L4 | 잔여 금지로 표적 permission contrast 부재 | ❌ **적용 안 됨** — 수선의 목적이 이 결함 제거다 |
| **L5** | 기본허용 규칙의 해석 한계 | ✅ **신규** |

### L5 (D-H1a-11 §12 원문 그대로, 의역 없음)

```text
L5 — Default-permission interpretation limit

The repaired prompt states a shared default rule under which packet-internal
decision bases are permitted unless explicitly prohibited. This makes the
REMOVED arm's target-axis permission explicit at the policy level without
enumerating those axes only in that arm.

The experiment nevertheless cannot establish that every model operationalizes
the shared default rule identically. Observed behavior remains conditional on
the model's interpretation of the frozen rendering.
```

**L4와 L5의 관계**(판정문 명시): L4는 "최초 코호트에는 표적 permission
contrast가 없었다"이고, L5는 "수선 코호트에는 정책상 contrast가 있지만 모델이
기본허용 규칙을 어떻게 실행하는지는 별도 문제다". **L5는 L4를 대체하지
않는다.**

---

## 7. 이 코호트가 null을 낼 경우의 보고 규약 (결과 보기 전 고정)

L5가 남아 있으므로, 양 arm이 다시 같은 modal 범주로 떨어지면 다음 **두 가지가
여전히 구별되지 않는다**:

1. 표적 메커니즘이 정책상 허용됐으나 행동이 바뀌지 않았다
2. 모델이 공통 기본허용 규칙을 표적 축 허용으로 실행하지 않았다

따라서 null은 다음 형태로만 보고한다:

```text
target_effect:            insufficient_evidence   (2가 배제되지 않으므로)
current_bundle_contrast:  observed_zero
policy_level_contrast:    present                 (구조 단언·연역 검사로 증명)
```

**"금지를 제거해도 행동은 변하지 않았다"는 여전히 금지된다.** 정책 수준에서
contrast가 있다는 것(L4 해소)과 모델이 그것을 그렇게 읽었다는 것(L5 미해소)은
다른 주장이다.

manipulation check로 쓸 수 있는 것: REMOVED arm의 `rationale`이 기본허용
규칙을 인용하거나 표적 축을 근거로 명시하는 빈도. **P5.4대로 별도 지표로만
기록하고 행동 분포에 합산하지 않는다.**
