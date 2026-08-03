# 설계 판정 — H1a 잔여 금지와 null 식별가능성

## 판정 식별자

**D-H1a-10**

* **Q10: E**
* **Q10.1: 탐색적·진단적 기록으로 보존하되 새 코호트와 병합하지 않음**
* **Q10.2: 잔여 금지 가드를 의미적 정책 계약으로 상향**
* **Q10.3: L3와 별도로 L4 등록**

---

## 1. 근거 상태

이 판정은 첨부 요청서에 embed된 프롬프트 대조, 실행 무결성 보고, 행동 분포 및 판정문 인용을 조건부 사실로 사용한다. 실제 저장소 파일, 커밋, 동결 bundle 및 trial 산출물은 독립적으로 조회하지 못했다.

| 결론                                    |                                    상태 | source type     |
| ------------------------------------- | ------------------------------------: | --------------- |
| Q7의 target-axis 금지가 양 arm에 공통으로 남음    |                             supported | prompt-given    |
| Q1의 두 문장만 arm 간 차이였음                  | supported, not independently verified | prompt-given    |
| 양 arm이 각각 20/20 defer였음               | supported, not independently verified | prompt-given    |
| 실행·채점 데이터 자체가 손상되었다는 근거               |                                    없음 | prompt-given    |
| 현재 대비가 의도한 source-priority 허용 효과를 식별함 |                               지원되지 않음 | model inference |
| 저장소 구현 및 커밋 일치 여부                     |               `insufficient_evidence` | repo-grounded   |
| ConceptGate taxonomy 판정               |                        `out_of_scope` | MCP-grounded    |
| 형식화된 금지 규칙의 논리적 대비                    |                                   검증됨 | MCP-grounded    |

따라서 판정은 다음 조건부 명제를 전제로 한다.

> 요청서에 제시된 동결 프롬프트의 바이트 대조와 실행 결과가 실제 저장소 산출물과 일치한다면, 현재 코호트는 의도한 H1a estimand를 식별하지 않는다.

---

## 2. Q10 판정

### 선택: E — 비식별 코호트로 보존하고, B 방식으로 새 실험 수행

이번 40 trial을 **데이터 오류나 실행 실패로 무효화하지 않는다.** 실행된 프롬프트 아래에서 관측된 행동은 유효한 관측이다.

그러나 이 데이터를 다음 명제의 확증 근거로 사용해서는 안 된다.

> liveness/source-priority 재판정 금지를 제거해도 모델의 select/defer 행동은 변하지 않는다.

현재 실험이 직접 추정한 것은 그보다 좁은 다음 대비다.

[
\tau_{\text{current}}
=====================

## E[Y\mid Q1=0,Q7_{\text{target}}=1,P]

E[Y\mid Q1=1,Q7_{\text{target}}=1,P]
]

여기서:

* (Q1=1): Q1의 서술형 금지가 존재함
* (Q7_{\text{target}}=1): Q7이 source-kind priority, recency, authority, liveness를 tie-breaker로 금지함
* (P): 현재의 고정 evidence packet
* (Y): select/defer 행동

따라서 이번 코호트의 관측값은 다음처럼만 보고할 수 있다.

[
\widehat{\tau}_{\text{current}}=0
]

즉:

> 공통 Q7 warrant rule이 유지된 현재 packet+prompt 조건에서는 Q1 두 문장의 제거에 따른 관측 행동 차이가 없었다.

이는 **의도한 허용 효과의 null**이 아니라, **공통 금지 아래에서 중복된 표면 문구를 제거한 대비의 zero contrast**다.

---

## 3. 형식적 식별성 평가

표적 행동 경로를 다음처럼 형식화한다.

* (Q1): source liveness·priority 추론 금지
* (Q7): 그 속성을 tie-break 근거로 사용하는 행위 금지
* (M): source 속성으로 충돌을 해결하는 표적 메커니즘

의사결정 출력에 도달하는 표적 경로가 열리려면 최소한 다음 조건이 필요하다.

[
M_{\text{allowed}}=\neg Q1\land\neg Q7
]

현재 설계:

| arm     | (Q1) | (Q7) | (M_{\text{allowed}}) |
| ------- | ---: | ---: | -------------------: |
| KEPT    |    1 |    1 |                    0 |
| REMOVED |    0 |    1 |                    0 |

Wolfram 연역 검사 결과:

```text
CurrentDesign:
  KEPT: False
  REMOVED: False
  TargetMechanismContrast: False

ProofCurrentNoContrast: True
```

이 증명은 위 형식화가 맞다는 조건 아래, 현재 두 arm 사이에 **표적 메커니즘의 허용 여부 차이가 없음**을 보여준다.

다만 이것이 `select_type` 자체가 논리적으로 불가능했다는 뜻은 아니다. 요청서가 지적한 `ev3`의 실질적 반박 논거처럼, source priority가 아닌 evidence merit를 이용한 선택 경로는 남아 있었다.

따라서 두 명제를 구별해야 한다.

1. **표적 source-priority 경로에는 arm 간 차이가 없었다.**
2. **모든 select_type 경로가 닫힌 것은 아니었다.**

첫 번째는 식별 결함이다. 두 번째 때문에 이번 0/40은 완전히 기계적으로 강제된 결과라고 단정할 수는 없다.

---

## 4. 왜 A가 아닌가

A는 실행 결과를 기술하는 데에는 허용되지만, H1a의 종료 판정으로는 부적합하다.

Q7 문제를 단순한 일반화 한계로 처리하면 다음 두 명제를 혼동하게 된다.

* 표적 메커니즘을 허용했지만 행동 변화가 없었다.
* 표적 메커니즘이 양 arm에서 모두 금지되어 있었다.

현재 자료는 두 번째 구조에 해당한다. 따라서 "조작 효과가 없었다"는 결론은 `insufficient_evidence`다.

---

## 5. 왜 C가 아닌가

C는 Q7 전체를 조작 위치로 이동시켜 다음 선행 설계를 실질적으로 변경한다.

* Q1=B
* Q5=B
* Q3=B의 모델 대면 표면 구조

또한 Q7에는 조작 대상과 무관한 축도 포함되어 있다.

* evidence count
* source order
* outside knowledge

Q7 전체의 유무를 조작하면 target-axis 효과와 비표적 warrant 제한 효과가 함께 변한다. 이는 현재 결함을 고치면서 새로운 복합 조작을 도입한다.

따라서 최소 수정 원칙상 C보다 B가 우선한다.

---

## 6. 왜 D를 기본 판정으로 채택하지 않는가

2×2 요인 설계는 다음 질문에는 유용하다.

* Q1 문구와 Q7 규칙이 중복되는가
* 둘 사이에 상호작용이 있는가
* 모델이 서술형 금지와 의사결정 규칙에 다르게 반응하는가

그러나 이것은 원래 H1a를 복구하기 위한 최소 조건보다 넓은 새 연구 질문이다.

또한 현재 형식화에서는 표적 경로가 열리는 cell이 하나뿐이다.

| Q1 금지 | Q7 target 금지 | 표적 경로 |
| ----: | -----------: | ----: |
|    있음 |           있음 |    닫힘 |
|    있음 |           없음 |    닫힘 |
|    없음 |           있음 |    닫힘 |
|    없음 |           없음 |    열림 |

따라서 2×2는 redundancy와 interaction을 연구하는 후속 실험으로는 정당하지만, H1a의 최소 복구에 필수적이지 않다. K=1 fixture 한계도 해결하지 않는다.

**D는 후속 탐색 실험으로 유보한다.**

---

## 7. 재설계 명령

### D-H1a-10-R1 — Q7 부분 개정

양 arm의 공통 Q7 목록에서 조작 대상 축만 제거한다.

제거 대상:

```text
source_kind priority
recency
authority
liveness
```

유지 대상:

```text
evidence item count
source order
outside knowledge
```

수정 후 정책은 다음처럼 구성되어야 한다.

| 판단 근거                |      KEPT | REMOVED |
| -------------------- | --------: | ------: |
| evidence count       |        금지 |      금지 |
| source order         |        금지 |      금지 |
| outside knowledge    |        금지 |      금지 |
| source_kind priority | Q1에 의해 금지 |      허용 |
| recency              | Q1에 의해 금지 |      허용 |
| authority            | Q1에 의해 금지 |      허용 |
| liveness             | Q1에 의해 금지 |      허용 |

형식적으로:

| arm     | (Q1) | (Q7_{\text{target}}) | (M_{\text{allowed}}) |
| ------- | ---: | -------------------: | -------------------: |
| KEPT    |    1 |                    0 |                    0 |
| REMOVED |    0 |                    0 |                    1 |

Wolfram 검사 결과:

```text
MinimalRepair:
  KEPT: False
  REMOVED: True
  TargetMechanismContrast: True

ProofRepairCreatesContrast: True
```

이 수정은 Q1의 두 문장을 조작 표면으로 유지하면서, 그 문장을 제거한 arm에서 표적 행동 경로가 실제로 열리게 한다.

### D-H1a-10-R2 — 양 arm 전체 재실행

새 실험에서는 **KEPT와 REMOVED를 모두 다시 실행해야 한다.**

기존 KEPT를 새 REMOVED와 비교해서는 안 된다. Q7 문구 변경은 양 arm의 표면을 바꾸므로, 기존 KEPT와 수정된 KEPT도 동일한 프롬프트가 아니다.

새 코호트는:

* 새 사전등록
* 새 prompt freeze
* 새 arm-diff 검증
* 새 cohort identifier
* 양 arm 신규 표본
* 기존 코호트와 독립된 분석

을 사용해야 한다.

---

## 8. Q10.1 — 기존 40 trial의 처리

### 판정

**폐기하지 않는다. 탐색적·진단적 코호트로 동결 보존한다.**

권장 상태값:

```yaml
cohort_status: completed_nonidentifying
analysis_role: exploratory_diagnostic
confirmatory_h1a_eligible: false
merge_with_repaired_cohort: false
reason: common_residual_prohibition_blocked_target_mechanism
```

보존해야 할 것:

* 동결 프롬프트
* cohort hash
* trial 원문
* coder 산출물
* 독립 재집계 결과
* 발견된 잔여 금지
* 발견 시점이 결과 확인 이후였다는 사실
* 본 판정문

허용되는 보고:

> 기존 코호트에서는 양 arm 모두 20/20 defer였다. 이 코호트는 Q7 target-axis 금지가 양 arm에 공통으로 남아 있었으므로, 의도한 H1a 조작 효과의 확증 검정에는 사용하지 않았다.

허용되지 않는 보고:

> 금지를 제거해도 행동은 변하지 않았다.

또한 기존 40 trial을 수정 코호트의 표본 수에 포함하거나, 기존 arm 하나를 재사용하거나, 두 코호트를 합산해서는 안 된다.

---

## 9. Q10.2 — 잔여 금지 가드

### 판정

`assert_no_residual_prohibition`의 표적 명제를 상향해야 한다.

기존 명제:

```text
REMOVED arm에 Q1의 특정 문자열 또는 절이 없는가
```

필요한 명제:

```text
REMOVED arm의 실행 가능한 의사결정 정책에
조작 대상 메커니즘을 금지하는 다른 규칙이 남아 있지 않은가
```

그러나 이를 폐쇄된 금지어 목록이나 raw-string 검색으로 구현해서는 안 된다. 동등한 금지는 임의의 paraphrase로 표현될 수 있으므로 lexical completeness를 인증할 수 없다.

### 필수 구조 변경

프롬프트 문구보다 먼저 구조화된 정책 계약을 정의한다.

```yaml
decision_basis_policy:
  evidence_count:
    kept: forbidden
    removed: forbidden

  source_order:
    kept: forbidden
    removed: forbidden

  outside_knowledge:
    kept: forbidden
    removed: forbidden

  source_kind_priority:
    kept: forbidden
    removed: allowed

  recency:
    kept: forbidden
    removed: allowed

  authority:
    kept: forbidden
    removed: allowed

  liveness:
    kept: forbidden
    removed: allowed
```

그다음 프롬프트를 이 정책 객체에서 생성해야 한다.

하드 가드는 최소한 다음을 검증한다.

```text
1. target-axis 상태가 KEPT=forbidden, REMOVED=allowed인가
2. 비표적 축은 양 arm에서 동일한가
3. arm 간 정책 차이가 사전등록된 target-axis 집합과 정확히 같은가
4. 동일 policy ID를 금지하는 중복 규칙이 다른 섹션에 없는가
5. 렌더된 모든 정책 문장이 원래 policy ID로 추적 가능한가
6. raw free-text 규칙이 별도의 정책 의미를 도입하지 않는가
```

### LLM 의미 검사기의 지위

LLM reviewer는 도입할 수 있지만 **인증 게이트의 단독 판정자**가 되어서는 안 된다.

적절한 역할:

```text
semantic lint
adversarial paraphrase search
duplicate-prohibition candidate detection
human-review escalation
```

부적절한 역할:

```text
sole certification oracle
single-run PASS/FAIL gate
expected arm difference를 아는 상태의 비맹검 리뷰
```

권장 계층:

[
\text{typed policy schema}
\rightarrow
\text{deterministic renderer}
\rightarrow
\text{structural assertions}
\rightarrow
\text{deductive policy check}
\rightarrow
\text{LLM semantic lint}
\rightarrow
\text{human sign-off}
]

Wolfram 같은 연역 도구는 정규화된 정책 명제에서 다음을 검증하는 데 사용할 수 있다.

```text
KEPT에서 target mechanism이 금지되는가
REMOVED에서 target mechanism이 허용되는가
비표적 제약이 두 arm에서 동일한가
동시에 만족할 수 없는 정책 조합이 존재하는가
```

자연어 자체를 Wolfram에 직접 넣는 것이 아니라, 자연어를 policy ID와 논리식으로 컴파일한 뒤 검사해야 한다.

---

## 10. Q10.3 — L4 필요 여부

### 판정

**L4가 별도로 필요하다.**

L3는 외적 일반화 한계다.

> 이 packet에서 관측된 select/defer 차이의 유무·크기·방향을 다른 packet이나 일반적 모델 행동으로 확장하지 않는다.

Q10의 문제는 내적 식별 한계다.

> 현재 packet 안에서도 의도한 조작 메커니즘이 arm 간 다르게 구현되지 않았다.

따라서 L3로 L4를 대체할 수 없다.

### 등록할 L4 문안

```text
L4 — Residual-prohibition identification limit

The original 40-trial cohort retained, in both arms, a common warrant rule
prohibiting source_kind priority, recency, authority, and liveness from being
used as tie-breakers. Consequently, the cohort did not instantiate an arm
contrast in whether the targeted source-priority mechanism was permitted.

The observed 20/20 versus 20/20 deferral distribution is descriptive only of
the frozen packet-and-prompt bundles. It must not be interpreted as evidence
that permitting source-priority or liveness reasoning has no effect on
select_type versus defer behavior.
```

한국어 기록문:

```text
L4 — 잔여 금지에 따른 식별 한계

최초 40-trial 코호트는 source_kind priority, recency, authority, liveness를
tie-breaker로 사용하는 행위를 금지하는 공통 warrant rule을 양 arm에 모두
유지했다. 따라서 이 코호트에는 표적 source-priority 메커니즘의 허용 여부에
대한 arm 간 대비가 구현되지 않았다.

관측된 20/20 대 20/20 보류 분포는 동결된 packet+prompt bundle의 기술적
결과로만 기록한다. 이를 source-priority 또는 liveness 추론을 허용해도
select_type/defer 행동에 효과가 없다는 증거로 해석하지 않는다.
```

---

## 11. 사후 발견에 따른 새 사전등록 조건

수정 코호트는 최초 결과를 모르는 상태에서 설계된 실험으로 표현해서는 안 된다.

새 사전등록에 다음을 명시해야 한다.

```text
1. 최초 코호트 결과는 양 arm 20/20 defer였다.
2. 최초 결과 확인 후 공통 Q7 규칙의 의미적 중복이 발견되었다.
3. 재설계 사유는 결과의 방향이 아니라 동결 프롬프트의 구조적 대조다.
4. 기존 coder와 outcome 정의는 변경하지 않는다.
5. 기존 코호트와 수정 코호트를 병합하지 않는다.
6. 수정된 양 arm을 모두 새로 실행한다.
7. 수정 코호트는 post-result design revision임을 기록한다.
```

이 공개는 새 실험을 무효화하지 않는다. 다만 최초 코호트와 동일한 의미의 사전등록 또는 독립 복제로 부르면 안 된다.

---

## 12. 철학적·형식적 평가

### Gödel식 제한

현재 자료에서 증명되는 것은 현재 프롬프트 bundle의 관측 결과뿐이다. 표적 메커니즘의 효과가 없다는 명제는 현재 공리와 자료에서 증명되지 않는다.

따라서 결론은 `null_effect`가 아니라:

```text
target_effect: insufficient_evidence
current_bundle_contrast: observed_zero
```

로 분리해야 한다.

### Wittgenstein식 사용 규칙

Q1과 Q7의 문장이 문자적으로 다르다는 사실은 결정적이지 않다. 실험에서 prohibition의 의미는 모델의 의사결정에서 어떤 근거의 사용을 허용하거나 금지하는지에 의해 정해진다.

따라서 "추론하지 마라"와 "tie-break에 사용하지 마라"가 동일한 관측 경로를 차단한다면, 해당 fixture에서는 기능적으로 중복된 규칙이다.

### Kripke식 식별자 구분

"Q1 clause 제거"라는 문구 식별자와 "source-priority 메커니즘 허용"이라는 정책 상태를 동일시해서는 안 된다.

* Q1 clause: 특정 프롬프트 표면
* target permission: 여러 문장에 의해 결정될 수 있는 의미 상태

잔여 금지 가드는 전자가 아니라 후자를 검사해야 한다.

### Lewis식 반사실 비교

의도한 반사실은 다음이다.

> 나머지 조건은 동일하게 두고 source-priority 사용 허용 여부만 바꾸면 행동이 달라지는가?

현재 REMOVED world에서도 Q7이 해당 사용을 금지했으므로, 실제 비교는 이 반사실을 구현하지 않았다.

---

## 최종 명령

```yaml
Q10:
  decision: E
  interpretation:
    current_cohort: valid_observations_but_nonidentifying_for_intended_H1a
    observed_result: zero_contrast_under_common_Q7
    target_effect: insufficient_evidence

  repair:
    method: B
    remove_from_common_Q7:
      - source_kind_priority
      - recency
      - authority
      - liveness
    retain_in_common_Q7:
      - evidence_count
      - source_order
      - outside_knowledge
    rerun_both_arms: true

Q10_1:
  preserve_original_cohort: true
  status: exploratory_diagnostic
  pool_with_new_cohort: false
  reuse_old_arm: false

Q10_2:
  raise_guard_to_semantic_policy_contract: true
  lexical_guard_alone: insufficient
  structured_policy_schema: required
  deterministic_renderer: required
  deductive_check: required
  LLM_semantic_reviewer: advisory_only

Q10_3:
  register_L4: true
  L3_subsumes_L4: false
```
