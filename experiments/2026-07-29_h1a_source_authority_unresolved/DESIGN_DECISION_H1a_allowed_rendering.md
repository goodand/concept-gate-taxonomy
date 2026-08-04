# 설계 판정 — `removed: allowed` 렌더링과 KEPT 금지의 담지자

## 판정 식별자

**D-H1a-11**

| 질문    | 판정                                                    |
| ----- | ----------------------------------------------------- |
| Q11   | **D — 공통 기본허용 규칙을 렌더링하고, REMOVED에는 축별 허용문을 추가하지 않는다** |
| Q11.1 | **A — KEPT는 기존 Q1 절만을 표적 금지의 담지자로 유지한다**              |
| Q11.2 | **A — 축×arm×담지자 매핑을 사전등록에 동결한다**                      |

---

## 1. Q11 판정

### D — 공통 기본허용 규칙

`removed: allowed`를 다음 두 방식 중 어느 하나로 처리해서는 안 된다.

* 아무 의미 규칙도 없이 침묵하는 방식
* REMOVED에만 표적 축을 열거한 긍정 허용문을 추가하는 방식

대신 양 arm에 동일한 **공통 기본허용 규칙**을 추가한다.

```text
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. Permission to consider a basis does not by
itself warrant selecting a type or favor either allowed type.
```

이 문장은 다음 두 명제를 동시에 고정한다.

1. 프롬프트가 명시적으로 금지하지 않은 packet-internal 판단 근거는 사용할 수 있다.
2. 사용할 수 있다는 사실만으로 `select_type`이나 특정 type이 장려되지는 않는다.

따라서 `removed: allowed`는 축별 긍정 문장을 렌더링하지 않고, 공통 기본허용 규칙을 상속한다.

```yaml
removed_rendering:
  mode: inherited_default_permission
  axis_specific_text: none
  carrier: GLOBAL_DEFAULT_PERMISSION
```

---

## 2. 이 판정이 A와 다른 이유

순수한 A는 다음 상태다.

```text
표적 축 금지 없음
표적 축 허용 규칙도 없음
```

이 경우 모델이 금지의 부재를 허용으로 읽는다는 보장이 없다. 특히 주변 문장이 packet 사용 범위를 엄격하게 제한하므로, 다시 양 arm defer 쏠림이 발생하면 다음 둘을 구분할 수 없다.

* 표적 메커니즘을 허용했지만 효과가 없었음
* 모델이 침묵을 허용으로 해석하지 않았음

공통 기본허용 규칙은 이 모호성을 제거한다.

[
\neg\text{explicitly forbidden}
\Rightarrow
\text{permitted consideration}
]

따라서 REMOVED에서 표적 경로가 정책상 실제로 열린다.

---

## 3. 이 판정이 B와 다른 이유

B는 REMOVED에만 다음과 같은 축별 문장을 넣는다.

```text
You may take source_kind, recency, authority, or liveness into account.
```

그러면 arm 차이는 더 이상 금지문의 유무가 아니다.

```text
KEPT: 금지
REMOVED: 표적 축을 열거한 긍정적 허용
```

이 문장은 해당 축을 두드러지게 만들어 모델에게 사용을 암시할 수 있다. 즉 permission과 salience가 결합된다.

공통 기본허용 방식에서는 허용 규칙이 양 arm에 동일하므로, arm-specific demand characteristic가 생기지 않는다.

```text
공통: 명시적으로 금지되지 않은 packet-internal basis는 고려 가능
KEPT: Q1이 표적 축을 명시적으로 금지
REMOVED: 표적 축을 금지하는 문장 없음
```

따라서 관측 대비는 계속 다음과 같다.

[
\text{explicit prohibition}
\quad\text{vs.}\quad
\text{absence of prohibition under an explicit default-permission rule}
]

---

## 4. 이 판정이 C와 다른 이유

C는 양 arm의 표적 문장을 새로 저작하거나 Q1의 한국어 절을 다시 작성해야 한다. 이는 다음 선행 결정을 동시에 흔든다.

* Q1=B
* Q5=B
* 동결된 Q1 두 문장
* 기존 manipulation surface

현재 문제를 해결하는 데 Q1 절의 재저작은 필요하지 않다.

공통 기본허용 규칙은 양 arm에 동일하게 추가되므로:

* Q1 절 바이트를 보존한다.
* arm-specific 언어 차이를 새로 만들지 않는다.
* L2의 기존 언어 전환 한계를 해결하지는 않지만 확대하지도 않는다.

L2 해소는 이번 수선과 분리된 별도 실험 변경으로 남긴다.

```text
L2 remediation: out_of_scope
```

---

## 5. 최종 렌더링 구조

### 양 arm 공통

packet boundary 뒤 또는 warrant rule 직전에 다음 문장을 둔다.

```text
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. Permission to consider a basis does not by
itself warrant selecting a type or favor either allowed type.
```

수정된 공통 Q7 문구:

```text
- Choose select_type only if the packet warrants selecting one allowed type
  over the other. Cite the evidence item ids that support the selected type.
- Choose defer if the packet does not warrant selecting exactly one allowed
  type, including cases where support is conflicting, ambiguous, or insufficient.
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence item's
  text.
```

### PROHIBITION_KEPT에만 유지

기존 Q1 절의 바이트를 변경하지 않는다.

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

### PROHIBITION_REMOVED

표적 축별 추가 문장을 렌더링하지 않는다.

REMOVED의 허용 상태는 공통 기본허용 규칙으로부터 결정된다.

---

## 6. Q11.1 판정

### A — KEPT는 Q1 절만 유지

KEPT의 Q7 목록에 표적 축을 다시 넣지 않는다.

수선 후 KEPT:

```text
GLOBAL_DEFAULT_PERMISSION
+
Q1_LIVENESS_CLAUSE override
+
COMMON_Q7_NON_TARGET_PROHIBITIONS
```

수선 후 REMOVED:

```text
GLOBAL_DEFAULT_PERMISSION
+
COMMON_Q7_NON_TARGET_PROHIBITIONS
```

정책 계산은 다음과 같다.

[
\operatorname{effective}(a)
===========================

\operatorname{explicit\ override}(a)
;\text{if present, otherwise};
\operatorname{default}(a)
]

표적 축에 대해:

| arm     |     기본값 | 명시적 override |     최종 상태 |
| ------- | ------: | -----------: | --------: |
| KEPT    | allowed | Q1 forbidden | forbidden |
| REMOVED | allowed |           없음 |   allowed |

이 구조에서 KEPT에 Q7 금지를 복원하면 동일 축에 두 개의 금지 담지자가 생긴다.

```text
Q1_LIVENESS_CLAUSE
Q7_TIEBREAKER_LIST
```

이는 blocker #16과 Q10의 중복 금지 구조를 다시 도입한다. 따라서 허용하지 않는다.

### 금지 강도에 대한 판정

수선 전 KEPT에 금지 문장이 두 곳 있었다는 사실을 "더 강한 처치"의 정상 상태로 간주해서는 안 된다. 그것은 중복 carrier 결함이었다.

수선 후 KEPT의 처치는 다음 명제 하나로 정의한다.

> 표적 source-priority 메커니즘은 Q1 절에 의해 금지된다.

실험이 측정해야 하는 것은 금지문 수나 반복 강도가 아니라 표적 정책 상태다.

[
\text{KEPT state}=\text{forbidden}
]

Q1 절이 이 fixture에서 해당 상태를 전달하지 못한다는 별도 근거가 생기면, 그것은 Q7을 중복 복원할 이유가 아니라 Q1 manipulation 자체를 재설계할 이유다.

---

## 7. Q11.2 판정

### A — carrier를 사전등록에 동결

`carrier`는 구현 세부가 아니다. 조작이 어떤 프롬프트 표면에 의해 실현되는지를 지정하므로 실험 처치의 일부다.

사전등록에는 최소한 다음 표가 들어가야 한다.

| policy axis          | KEPT state | KEPT carrier       | REMOVED state | REMOVED carrier           |
| -------------------- | ---------- | ------------------ | ------------- | ------------------------- |
| evidence_count       | forbidden  | Q7_TIEBREAKER_LIST | forbidden     | Q7_TIEBREAKER_LIST        |
| source_order         | forbidden  | Q7_TIEBREAKER_LIST | forbidden     | Q7_TIEBREAKER_LIST        |
| outside_knowledge    | forbidden  | Q7_TIEBREAKER_LIST | forbidden     | Q7_TIEBREAKER_LIST        |
| source_kind_priority | forbidden  | Q1_LIVENESS_CLAUSE | allowed       | GLOBAL_DEFAULT_PERMISSION |
| recency              | forbidden  | Q1_LIVENESS_CLAUSE | allowed       | GLOBAL_DEFAULT_PERMISSION |
| authority            | forbidden  | Q1_LIVENESS_CLAUSE | allowed       | GLOBAL_DEFAULT_PERMISSION |
| liveness             | forbidden  | Q1_LIVENESS_CLAUSE | allowed       | GLOBAL_DEFAULT_PERMISSION |

이 표를 바꾸는 것은 renderer refactor가 아니라 experiment amendment다.

---

## 8. carrier의 정확한 의미

`carrier`는 단순히 특정 단어가 포함된 문장이 아니다.

> 해당 axis의 최종 정책 상태를 규범적으로 결정하는 유일한 권위 경로.

동일한 carrier가 여러 axis를 담당할 수 있다.

```text
Q1_LIVENESS_CLAUSE
  ├─ source_kind_priority
  ├─ recency
  ├─ authority
  └─ liveness
```

그러나 하나의 axis×arm 상태가 복수 carrier에 의해 중복 결정되어서는 안 된다.

### 허용되는 구조

```text
source_kind_priority × KEPT
→ Q1_LIVENESS_CLAUSE
```

### 금지되는 구조

```text
source_kind_priority × KEPT
→ Q1_LIVENESS_CLAUSE
→ Q7_TIEBREAKER_LIST
```

packet boundary나 evidence-only scope 문장은 carrier가 아니라 `scope_constraint`로 따로 기록한다.

```yaml
scope_constraints:
  - PACKET_ONLY
  - NO_EXTERNAL_SOURCES
```

이 문장들이 판단 근거의 출처 범위를 제한하더라도, 특정 axis를 forbidden으로 바꾸지 않는 한 그 axis의 carrier로 계산하지 않는다.

---

## 9. 정책 스키마

권장 계약:

```yaml
policy_defaults:
  packet_internal_decision_basis:
    state: allowed
    carrier: GLOBAL_DEFAULT_PERMISSION
    non_directive: true

decision_basis_policy:
  evidence_count:
    kept:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST
    removed:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST

  source_order:
    kept:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST
    removed:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST

  outside_knowledge:
    kept:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST
    removed:
      state: forbidden
      carrier: Q7_TIEBREAKER_LIST

  source_kind_priority:
    kept:
      state: forbidden
      carrier: Q1_LIVENESS_CLAUSE
    removed:
      state: allowed
      carrier: GLOBAL_DEFAULT_PERMISSION

  recency:
    kept:
      state: forbidden
      carrier: Q1_LIVENESS_CLAUSE
    removed:
      state: allowed
      carrier: GLOBAL_DEFAULT_PERMISSION

  authority:
    kept:
      state: forbidden
      carrier: Q1_LIVENESS_CLAUSE
    removed:
      state: allowed
      carrier: GLOBAL_DEFAULT_PERMISSION

  liveness:
    kept:
      state: forbidden
      carrier: Q1_LIVENESS_CLAUSE
    removed:
      state: allowed
      carrier: GLOBAL_DEFAULT_PERMISSION
```

`allowed`와 침묵을 혼동하지 않도록 내부 enum을 다음처럼 세분할 수 있다.

```text
explicitly_forbidden
allowed_by_default
explicitly_allowed
unspecified
```

이번 REMOVED의 표적 축 상태는 다음이다.

```text
allowed_by_default
```

`unspecified`가 아니다.

---

## 10. 필수 구조 단언

freeze 전에 다음이 모두 통과해야 한다.

```text
1. 모든 axis×arm에 state가 존재한다.
2. 모든 axis×arm에 유효한 carrier가 정확히 하나 존재한다.
3. forbidden 상태는 forbidden 의미를 가진 carrier에 연결된다.
4. allowed_by_default 상태는 GLOBAL_DEFAULT_PERMISSION에 연결된다.
5. 동일 axis×arm을 금지하는 중복 carrier가 없다.
6. REMOVED의 표적 4축에는 forbidden carrier가 없다.
7. KEPT의 표적 4축에는 Q1_LIVENESS_CLAUSE만 존재한다.
8. 비표적 3축은 양 arm에서 상태와 carrier가 동일하다.
9. GLOBAL_DEFAULT_PERMISSION 문장은 양 arm에서 byte-identical하다.
10. Q1_LIVENESS_CLAUSE는 KEPT에만 존재하며 기존 동결 바이트와 동일하다.
11. REMOVED에는 축별 positive-permission 문장이 없다.
12. 공통 Q7에는 표적 4축의 문자열과 의미상 별칭이 없다.
```

---

## 11. arm-diff 계약

공통 기본허용 문장을 추가한 뒤 양 arm을 새로 생성하므로, 최종 arm diff는 다시 다음 하나로 제한되어야 한다.

```text
Q1_LIVENESS_CLAUSE present
vs.
Q1_LIVENESS_CLAUSE absent
```

즉 공통 템플릿이 바뀌지만 arm 간 차이는 확대되지 않는다.

```yaml
arm_diff:
  allowed_regions:
    - Q1_LIVENESS_CLAUSE
  common_new_text:
    - GLOBAL_DEFAULT_PERMISSION
    - REPAIRED_Q7_TIEBREAKER_LIST
```

수선 전 프롬프트와 수선 후 프롬프트가 같다는 주장은 하지 않는다. R2에 따라 양 arm 모두 새로 실행한다.

---

## 12. 한계 등록

공통 기본허용 규칙은 A의 비식별 위험과 B의 arm-specific demand characteristic를 줄인다. 그러나 완전히 제거하지는 않는다.

등록할 한계:

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

L4와의 관계:

* L4: 최초 코호트에는 표적 permission contrast가 없었다.
* L5: 수선 코호트에는 정책상 contrast가 있지만 모델이 기본허용 규칙을 어떻게 실행하는지는 별도 문제다.

L5는 L4를 대체하지 않는다.

---

## 13. 최종 명령

```yaml
D-H1a-11:
  Q11:
    decision: D
    rendering:
      common_default_permission: required
      removed_axis_specific_permission_text: forbidden
      removed_target_state: allowed_by_default
      demand_neutralizer: required

  Q11_1:
    decision: A
    kept_target_carrier:
      only: Q1_LIVENESS_CLAUSE
    restore_target_axes_to_Q7: forbidden

  Q11_2:
    decision: A
    freeze_carrier_mapping: required
    carrier_change_requires_amendment: true

  freeze_gate:
    status_before_implementation: blocked
    unblock_when:
      - policy schema valid
      - carrier cardinality valid
      - common default permission byte-identical
      - arm diff restricted to Q1 clause
      - independent semantic review passed

  execution:
    rerun_both_arms: true
    reuse_original_trials: false
    merge_original_and_repaired_cohorts: false
```
