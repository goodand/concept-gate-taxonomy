# DESIGN DECISION — H1a post-execution scope (D-H1a-18)

- 수신: **2026-08-22**
- 도착 경로: 사용자가 외부 설계 담당에게
  `correspondence/DESIGN_REQUEST_H1a_post_execution_scope.md`(Q18)를 공유하고
  회신을 전달
- 선행 요청: 위 요청서 (Q18 + Q18.1~Q18.4)
- 판정 ID: 판정문 자신이 `D-H1a-18`로 표기
- 구속력: **있음.** D-H1a-1~17과 같은 외부 판정 채널을 거쳤다
- 판정 요지: **Q18 = F = A(서술적 종결) + C(상위 목적 전환).** H1a는 현재
  코호트를 서술적으로 보고하고 **종결**한다. `QF-DEFER` 확보와 3차 코호트는
  종결의 필수조건이 **아니다**

## 운영 세션의 독립 검증 (2026-08-22, 저장 전)

판정문이 통계 계산을 근거로 삼으므로, 운영 세션이 **Wolfram을 쓰지 않고
Python 정확 조합 계산으로 독립 재계산**했다. 판정을 받았기 때문에 맞다고
가정하지 않는다.

| 판정문 주장 | 독립 재계산 | 일치 |
|---|---|---|
| Fisher two-sided p = 0.48718 | 0.48718 | ✅ |
| Fisher one-sided p = 0.24359 | 0.24359 | ✅ |
| KEPT 0/20 95% exact CI = [0, 0.1684] | [0.0000, 0.1684] | ✅ |
| REMOVED 2/20 95% exact CI = [0.0123, 0.3170] | [0.0123, 0.3170] | ✅ |
| 같은 N=20/arm 재실행 시 양측 p<0.05 도달 확률 ≈ 4.3% | **4.32%** | ✅ |

방법: 초기하분포 `P(k) = C(S,k)·C(N−S,n1−k)/C(N,n1)`로 Fisher 정확검정
(양측은 `P ≤ P_obs` 합), 신뢰구간은 Clopper-Pearson(이분포 꼬리 이분법),
민감도는 `p_K=0, p_R=0.10, n=20`에서 **441개 표 전수 열거**(확률질량 합
1.000000 확인).

**열거가 판정문보다 더 말해주는 것 하나** — 판정문은 4.3%라는 수치만 제시하나,
전수 열거는 그 이유를 보여준다: `a=0`일 때 양측 p<0.05에 도달하는 최소값은
**b=5**(p=0.04712)다. 즉 **5/20 = 25%** 규모가 필요하고, 관측된 2/20(10%)은
그 절반 미만이다. 유의성에 기여하는 확률질량의 대부분(0.0319/0.0432 = 74%)이
`a=0, b=5` 한 칸에서 나온다. D(3차 코호트)를 같은 N으로 돌리는 것이 왜
정보량이 낮은지가 이 한 줄로 설명된다.

**비통계 주장 대조**:

| 판정문 주장 | 확인 |
|---|---|
| "`QF-DEFER`는 D-H1a-14/15에서 non-blocking diagnostic으로 재분류됐다" | ✅ `_h1a_qualification.py` `cohort_freeze.determined_by = identification_contract`, `controls_are_freeze_prerequisites: false`(사전등록 §5f) |
| "`material_unavailable`은 `failed`와 분리된다" | ✅ Q14.2. 코드에서 `_IMPLIES_SUBJECT_FAILURE[MATERIAL_UNAVAILABLE] = False` |
| "D-H1a-7 / R3은 그대로 유지" | ✅ 이 판정문이 소급 변경하지 않음을 명시 |

---

## 판정문 원문 (verbatim)

아래는 수령한 텍스트 그대로다. 운영 세션이 정본을 저작하지 않는다는 규율에
따라 **재작성·요약·정정하지 않았다.**

---

Wolfram MCP로 **통계적 정보량**, **QF-DEFER의 논리적 지위**, **기존/신규 코호트의 비교 가능 범위**를 분리해 검토했습니다. 결론은 **Q18=F, 즉 A(서술적 종결)+C(상위 목적으로 전환)**가 가장 타당합니다.

# DESIGN DECISION — H1a post-execution scope

**Q18: F = A + C**

* **H1a 자체는 현재 코호트를 서술적으로 보고하고 종결**
* **다음 개발/연구 자원은 상위 목적—LLM feedback + output 기반 causal inference—으로 이동**
* `QF-DEFER` 확보나 3차 코호트는 H1a 종결의 필수조건으로 두지 않음

---

## 1. Wolfram이 보여준 현재 관측의 강도

현재:

* KEPT: 0/20 select
* REMOVED: 2/20 select
* 관측 risk difference = **+0.10**

Wolfram exact 계산:

```text
Fisher two-sided p       = 0.48718
Fisher one-sided p       = 0.24359

95% exact binomial CI:
KEPT 0/20      = [0, 0.1684]
REMOVED 2/20   = [0.0123, 0.3170]
```

따라서 두 가지를 분리해야 합니다.

### 사실로 보고 가능한 것

```text
REMOVED에서 2/20 select가 관측됨
KEPT에서는 0/20 select가 관측됨
```

### 현재 자료가 지지하지 않는 것

```text
두 arm의 underlying selection probability가 다르다고 확립됨
Q1 제거가 selection을 야기함
```

즉 **관측은 보고 가능하지만 추론 강도는 낮습니다.**

---

# 2. 왜 E는 아닌가

E는 "2/20은 우연과 구별되지 않으므로 관측 자체를 보고하면 안 된다"는 안입니다.

이건 너무 강합니다.

통계적 불확실성이 크다는 것과 관측값을 보고할 수 없다는 것은 다릅니다.

[
\text{weak inferential evidence}
\neq
\text{unreportable observation}
]

따라서 §2.1의 데이터는 정상적으로 보고해야 합니다.

---

# 3. 왜 B를 강제하지 않는가

`QF-DEFER`는 이미 D-H1a-14/15에서 **non-blocking diagnostic**으로 재분류되었습니다. 요청서도 그 상태를 명시합니다.

따라서:

```text
QF-DEFER material unavailable
```

에서

```text
H1a cannot close
```

는 연역되지 않습니다.

정확한 상태는:

```yaml
ceiling_direction:
  status: unknown
  reason: QF-DEFER material unavailable
```

입니다.

즉 **천장 대안 설명을 제거하지 못한 채 종결할 수 있습니다.**

새 fixture를 저작해서 diagnostic을 채우는 것은 H1a의 현재 estimand를 더 잘 측정하는 것이라기보다 **새로운 증거 재료와 설계 의무를 추가하는 것**입니다.

상위 목적과 비교할 때 한계효용이 낮습니다.

---

# 4. 왜 D도 지금은 권하지 않는가

D는 과학적으로 무의미한 안은 아닙니다.

표면 하나만 달리한 새 코호트라면:

```text
어떤 redesign component가 행동 변화와 연결됐는가?
```

라는 새 질문에 접근할 수 있습니다.

하지만 그것은 **현재 H1a를 해석하는 작업이 아니라 새로운 component-ablation experiment**입니다.

그리고 현재 2/20의 규모를 참고해 (p_K=0,\;p_R=0.10) 정도의 실제 차이가 있다고 가정하고 20/arm을 다시 실행하는 상황을 Wolfram으로 계산하면, 양측 Fisher exact test가 0.05를 넘길 확률은 약:

```text
4.3%
```

에 불과했습니다.

이는 사후 power 설계값으로 사용하라는 뜻이 아니라:

> **같은 N=20/arm의 3차 코호트가 현재 관측 정도의 작은 효과를 명확하게 분리할 가능성은 매우 낮다**

는 민감도 점검입니다.

D를 하려면 단순히 "한 번 더 40 trial"이 아니라 **새 estimand + 새 sample-size rationale**가 필요합니다.

그것은 H1a 후속 별도 실험으로 두는 편이 낫습니다.

---

# 5. 따라서 A와 C를 조합한다

A와 C는 실질적으로 충돌하지 않습니다.

### A가 담당하는 것

**H1a의 연구 기록을 어떻게 닫는가**

```text
현재 코호트를 제한사항 R1~R8 아래 서술적으로 보고
QF-DEFER = material_unavailable
ceiling = unknown
H1a 종료
```

### C가 담당하는 것

**프로젝트가 다음에 어디로 가는가**

```text
H1a에서 만들어진
- obligation structure
- assurance
- semantic audit
- mutation testing
- structured feedback

중 제품 재사용 가치가 있는 kernel을 추출
↓
LLM feedback / causal reasoning architecture로 이동
```

그래서 선택지는:

```text
F = A(reporting closure) + C(next strategic direction)
```

입니다.

---

# Q18.1 — 허용 서술 형식

## 판정: **(b)**

가장 안전한 문장:

> **"이 코호트에서 `PROHIBITION_REMOVED` arm에서만 `select_type`이 관측되었다(2/20 vs 0/20)."**

조금 더 확장하면:

> "관측 빈도는 REMOVED에서 2/20, KEPT에서 0/20이었다. 이 고정 fixture의 현 코호트에서는 REMOVED에서만 selection이 발생했지만, 표본이 작고 QF-DEFER가 미시행이므로 이를 안정적인 분포 차이나 Q1 제거의 인과 효과로 해석하지 않는다."

### `(a) 달라졌다`

수학적으로 관측 empirical distribution은 다릅니다.

하지만 "분포가 달라졌다"는 문장은 쉽게 population-level inference로 읽힙니다.

따라서 주 보고 문구로는 사용하지 않는 것이 좋습니다.

---

# Q18.2 — 두 코호트 병기

## 판정: **(c) 조건부 허용**

Wolfram 논리 검사에서도:

```text
juxtaposition = True
pooling       = False
```

인 상태는 모순이 아니며,

```text
different surface + juxtaposition
```

에서 causal attribution이 자동으로 나오지도 않습니다.

따라서 다음 조건 아래 병기할 수 있습니다.

1. **병합하지 않는다.**
2. 하나의 effect estimate로 계산하지 않는다.
3. "0→2가 redesign 때문에 발생했다"고 쓰지 않는다.
4. 두 코호트의 prompt surface가 여러 곳 다름을 같은 표/문장에 표시한다.
5. 첫 코호트는 `completed_nonidentifying`, 둘째는 repaired-surface observation으로 서로 다른 지위를 유지한다.

허용되는 표현:

> "이전 비식별 표면에서는 양 arm 모두 0/20이었고, 수선된 별도 표면에서는 KEPT 0/20, REMOVED 2/20이 관측됐다. 두 코호트는 병합하지 않으며, 표면 차이가 복수이므로 이 변화 자체를 특정 수정의 효과로 귀속하지 않는다."

### 금지

> "재설계로 selection이 0에서 2로 증가했다."

이건 Q10.1보다도 R3에 더 직접적으로 걸립니다.

---

# Q18.3 — 2/20을 N=20에서 보고할 수 있는가

## 예. 단 **descriptive count/proportion**으로 보고

반드시 같이 제시:

```text
2/20 = 10%
0/20 = 0%
N fixed ex ante
no post-result extension
```

그리고 아래 중 하나를 같이 붙이는 것이 적절합니다.

> "표본이 작아 arm 간 probability difference에 대한 정밀한 추론을 지원하지 않는다."

또는 더 정량적으로:

> "양측 Fisher exact comparison은 p≈0.487이었다."

단, H1a가 원래 확증적 유의성 검정으로 사전등록된 것이 아니라면 **p-value를 primary verdict로 승격시키지 않습니다.**

Wolfram 계산은 결과의 정보량을 설명하는 보조 진단입니다.

---

# Q18.4 — QF-DEFER를 영구 `material_unavailable`로 닫을 수 있는가

## **예**

D-H1a-14/15가 이미 이것을 `failed`와 분리하고 non-blocking diagnostic으로 재분류했습니다.

따라서 최종 기록:

```yaml
QF_DEFER:
  status: material_unavailable
  executed: false

ceiling_diagnostic:
  status: unknown

experiment_closure:
  blocked_by_QF_DEFER: false
```

가 맞습니다.

중요한 것은:

```text
unknown → false
```

로 바꾸지 않는 것입니다.

즉:

> "ceiling이 없었다"

가 아니라:

> **"ceiling 가능성은 독립적으로 진단되지 않았다."**

로 영구 보존합니다.

---

# D-H1a-7 / R3의 지위

그대로 유지합니다.

현재 코호트에서:

```text
Q1 removed
→ selection caused
```

를 주장할 수 없습니다.

D와 같은 새 실험을 별도로 설계한다면 그 새 실험의 estimand와 귀속 규칙을 새로 판정할 수 있지만, 그것이 **현재 H1a의 R3을 소급 변경하지는 않습니다.**

---

# 전략적 판정

이번 시점에서 H1a의 추가 정밀화는 수익 체감 구간에 들어갔다고 봅니다.

H1a가 이미 준 더 중요한 자산은 특정 `2/20` 숫자보다:

```text
LLM output
↓
explicit obligation / policy state
↓
deterministic or semantic checks
↓
assurance-aware feedback
↓
causal experiment design
```

라는 아키텍처입니다.

사용자가 명시한 상위 목적과도 이쪽이 더 직접적으로 정렬됩니다.

## 최종 판정

```yaml
D-H1a-18:

  Q18:
    decision: F
    composition:
      - A_descriptive_closure
      - C_transition_to_upper_level_goal

  H1a:
    close: true
    additional_main_trials: 0
    current_cohort:
      report: true
      causal_attribution: forbidden
      generalization: forbidden

  Q18_1:
    decision: b
    preferred_wording:
      removed_only_selection_observed: true

  Q18_2:
    decision: c
    juxtaposition_allowed: true
    pooling: forbidden
    cross_cohort_effect_estimate: forbidden
    causal_redesign_attribution: forbidden

  Q18_3:
    report_2_of_20: allowed
    mode: descriptive
    inferential_strength: weak
    post_result_N_change: forbidden

  Q18_4:
    QF_DEFER:
      final_status: material_unavailable
      ceiling_direction: unknown
      blocks_closure: false

  next_program:
    priority:
      - reusable_feedback_kernel
      - LLM_output_based_causal_inference
    H1a_third_cohort:
      status: deferred_as_separate_future_experiment
```

가장 중요한 한 문장만 남기면:

> **H1a는 "REMOVED에서만 2/20 selection이 관측됐다"까지 보고하고 닫는 것이 맞고, 그 2건을 더 강한 인과 주장으로 만들기 위해 H1a를 계속 확장하기보다 이제 검증·피드백 kernel을 상위 causal-reasoning 아키텍처로 옮기는 것이 더 높은 가치가 있습니다.**
