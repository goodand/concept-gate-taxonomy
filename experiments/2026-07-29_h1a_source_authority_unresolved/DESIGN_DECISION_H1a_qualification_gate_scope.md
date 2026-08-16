# DESIGN DECISION — H1a qualification gate scope (D-H1a-14/15)

- 수신: 2026-08-16
- 도착 경로: 사용자가 외부 설계 담당에게
  `correspondence/DESIGN_REQUEST_H1a_qualification_gate_scope.md`를 공유하고
  회신을 전달
- 선행 요청: 위 재상신 문서(Q14 재상신 + Q14.1/14.2/14.3 + Q15).
  그 이전 원안은 `correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md`
- 판정 ID: 판정문 자신이 `D-H1a-14_15`로 표기
- 구속력: **있음.** D-H1a-1~13과 같은 외부 판정 채널을 거쳤다.
  (대조: 2026-08-15의 QF-DEFER 강등은 이 채널을 거치지 않아 철회됐다 —
  `docs/feedback/h1a_qf_defer_amendment_review_20260816.md`)

> ⚠️ **§1이 판정문 원문이다. 편집하지 말 것.** §2는 수신 세션의 실측 메모이며
> **판정의 일부가 아니다.**

---

# 1. 판정문 원문 (verbatim)

Wolfram으로 형식화해 보면, 이번 문제는 **재료 부족**보다 **hard gate와
diagnostic의 역할 혼합**이 핵심입니다. 첨부 요청서의 실측을 전제로 판정합니다.

## 추상화 결과

기호를 다음처럼 두었습니다.

* (C): H1a의 arm contrast가 식별 가능한 상태
* (S): QF-SELECT 통과
* (D): QF-DEFER 통과

Wolfram 검사는 다음을 반환했습니다.

```text
C → (S ∧ D)    : tautology가 아님
S ∧ D          : SELECT/DEFER 교환에 대해 대칭
S only gate    : SELECT/DEFER 교환에 대해 비대칭
```

명시적 반례도 존재합니다.

```text
C = True, D = False
C = True, S = False
```

즉 **qualification을 hard prerequisite로 만드는 것은 H1a 식별성에서
연역되는 사실이 아니라 추가적인 설계 규칙**입니다.

또 두 control의 실패 형태를 바꾸어 써 보면:

| QF-SELECT | QF-DEFER | 진단                         |
| --------- | -------- | -------------------------- |
| fail      | pass     | always-defer / floor 위험    |
| pass      | fail     | always-select / ceiling 위험 |
| pass      | pass     | 양쪽 행동 능력 관측                |
| fail      | fail     | 더 일반적인 task-mapping 문제     |

따라서 SELECT와 DEFER는 구조적으로 대칭입니다. 한쪽만 hard gate로 남기려면
**별도의 비대칭 원리**가 필요합니다. 현재 요청서에는 그런 원리가 없습니다.

---

# DESIGN DECISION — H1a qualification gate scope

**Q14: E — qualification gate 자체를 재설계**

**Q15: G — QF-SELECT와 QF-DEFER 모두 non-blocking capability diagnostic으로
재분류**

핵심 변경은:

```text
기존
QF-SELECT ∧ QF-DEFER
        ↓
cohort_freeze allowed

수정
QF-SELECT / QF-DEFER
        ↓
floor/ceiling diagnostic evidence
        ╳
cohort_freeze
```

입니다.

즉 qualification 결과가 **실험 실행 허가를 직접 생성하지 않습니다.**

---

## Q14 근거

Q13.3의 중요한 개선은 옛 M4처럼 본 결과로 본 결과를 진단하지 않고
**독립 fixture를 사용한다**는 것이었습니다.

그 개선은 유지해야 합니다.

하지만:

IndependentDiagnostic ⇏ HardFreezePrerequisite

입니다.

"독립적으로 측정한다"와 "통과하지 않으면 본 실험을 실행할 수 없다"는
서로 다른 설계 결정입니다.

따라서 Q13.3에서 보존할 부분은:

```text
독립 control
별도 trial
main cohort와 비풀링
floor/ceiling 진단
```

이고, 철회할 부분은:

```text
한 control이라도 실패/부재
→ cohort_freeze blocked
```

입니다.

---

## Q14.1 — 칼/철 재사용과 Q10.1

**Q10.1 자체의 직접 위반이라고 보지는 않습니다.**

`pooled_with_main_cohort: false`가 금지하는 것은 기본적으로 실행 결과의
병합이기 때문입니다.

하지만 qualification 독립성 관점에서는 사용하지 않는 것이 맞습니다.

```text
같은 fixture
→ 먼저 capability diagnostic
→ 이후 같은 fixture로 confirmatory effect 측정
```

은 main estimand와 qualification을 불필요하게 결합합니다.

따라서 새 판정에서는 이 문제를 해결하기 위해 칼/철을 QF-DEFER로 재사용하지
않습니다.

```yaml
confirmatory_fixture_reused_as_capability_control: false
```

---

## Q14.2 — `material_unavailable` vs `diagnostic_failed`

**구분을 승인하며, 같은 result category를 사용하지 않습니다.**

Wolfram에서도

```text
material_unavailable ≡ diagnostic_failed
```

는 tautology가 아니었습니다.

둘은 인식론적으로 완전히 다릅니다.

### 미시행

```yaml
QF_DEFER:
  status: material_unavailable
  subject_verdict: none
```

뜻:

> 검사할 수 없었다.

### 시행 후 실패

```yaml
QF_DEFER:
  status: diagnostic_failed
  observed_risk: ceiling_susceptibility
```

뜻:

> 검사했으며 기대 행동을 보이지 않았다.

따라서 기존의:

```yaml
result_category: floor_or_ceiling_failure
```

를 둘 모두에 붙이지 않습니다.

권장:

```yaml
qualification_diagnostics:
  select:
    status: passed | failed | material_unavailable
  defer:
    status: passed | failed | material_unavailable
```

`material_unavailable`에서 피험자 능력에 대한 부정적 결론을 내리면 안 됩니다.

---

# Q14.3 — qualification은 어느 arm으로 렌더하는가

**어느 treatment arm에도 속하지 않는 `QUALIFICATION_COMMON` surface를
정의합니다.**

다만 새 문장을 저작할 필요는 없습니다.

현재 H1a에서 KEPT와 REMOVED의 유일한 차이가 Q1 절이고, 기존 QF-SELECT가
사용한 REMOVED 표면이 그 절 없는 공통 표면이라면:

```text
QUALIFICATION_COMMON bytes
=
current PROHIBITION_REMOVED bytes
```

로 동결합니다.

중요한 것은 이름을 `REMOVED`에서 빌려 쓰는 것이 아니라 **qualification이
treatment condition에 속하지 않는다는 계약**입니다.

```yaml
qualification_surface:
  policy_role: treatment_invariant
  byte_source: COMMON_WITHOUT_Q1
  must_equal_current_removed_bytes: true
```

### 기존 QF-SELECT 5/5 재실행

**byte identity가 검증되면 재실행할 필요 없습니다.**

기존 5건을:

```yaml
surface:
  old_label: PROHIBITION_REMOVED
  reclassified_as: QUALIFICATION_COMMON
  byte_identity_verified: true
```

로 기록하면 됩니다.

반대로 한 바이트라도 다르면 기존 5/5는 historical diagnostic으로 보존하고
새 surface에서 다시 실행해야 합니다.

---

# Q15 — G: 둘 다 non-blocking

QF-DEFER만 diagnostic으로 낮추고 QF-SELECT를 hard gate로 남기는 **H안은
기각**합니다.

왜냐하면 두 실패가 정확히 반대 방향의 동일한 종류의 포화 위험이기
때문입니다.

```text
QF-SELECT fail
→ always-defer 가능
→ lower-end/floor saturation

QF-DEFER fail
→ always-select 가능
→ upper-end/ceiling saturation
```

둘 다 H1a의 null을 약하게 만들 수 있습니다.

따라서:

Role(QF_SELECT) = Role(QF_DEFER)

가 원칙적으로 맞습니다.

---

# 그러면 diagnostic 실패 시 결과를 어떻게 해석하는가

이 부분이 중요합니다.

### 둘 다 통과

```text
main effect / null 모두 정상적으로 해석
+ obvious floor/ceiling 대안 설명이 약화됨
```

### 하나가 실패

confirmatory 실행은 가능하지만:

```text
null 또는 작은 effect
→ 해당 floor/ceiling 설명을 배제하지 못함
```

으로 보고합니다.

### 하나가 material unavailable

역시 실행 가능하지만:

```text
그 방향의 capability는 독립적으로 진단되지 않음
```

을 한계로 등록합니다.

### 그런데 main cohort에서 큰 arm 차이가 발생

이 경우에는 중요한 정보가 하나 추가됩니다.

예를 들어 한 arm에서 select가 많고 다른 arm에서 defer가 많다면 main 데이터
자체가:

```text
always-select가 아님
always-defer가 아님
```

을 보여줍니다.

따라서 missing QF diagnostic의 중요성은 결과 형태에 따라 달라집니다.

이것이 diagnostic을 hard gate로 만들지 말아야 하는 또 하나의 이유입니다.

---

# freeze와 diagnostic을 분리

현재 `cohort_freeze`에 capability control을 연결하지 않는 것이 좋습니다.

### Freeze blocker

기존 H1a에서 실제 식별성을 구성하는 것들:

```text
target mechanism contrast
licensed path
residual prohibition 없음
prompt semantic audit
carrier consistency
independent review
preregistration integrity
```

### Non-blocking diagnostics

```text
QF-SELECT
QF-DEFER
```

즉:

```text
IDENTIFICATION CONTRACT
        ↓
      freeze

CAPABILITY DIAGNOSTICS
        ↓
interpretation strength
```

로 분리합니다.

---

# `floor_or_ceiling_failure`도 재정의

기존 이름은 hard gate 시절의 의미를 담고 있으므로 그대로 두면 혼동됩니다.

추천:

```yaml
capability_diagnostics:
  qf_select:
    status: passed
    rate: 1.00

  qf_defer:
    status: material_unavailable

diagnostic_summary:
  select_capability_observed: true
  defer_capability_observed: unknown
  floor_risk_independently_checked: true
  ceiling_risk_independently_checked: false
```

그리고:

```yaml
cohort_freeze:
  determined_by: identification_contract
```

로 분리합니다.

---

# 절차에 대한 판정

2026-08-15 운영 세션의 무판정 집행은 **결론의 옳고 그름과 별개로 절차
위반**이라는 현재 기록을 유지합니다.

다만 새 제약을 과도하게 추가할 필요는 없습니다.

재발 방지 규칙 하나면 충분합니다.

> **기존 판정에서 `freeze_blocker`인 조건을 `diagnostic`으로 낮추거나 그
> 반대로 승격하는 변경은 구현 변경이 아니라 estimand/governance 변경으로
> 취급하고, 외부 판정 전에는 실행하지 않는다.**

---

# 최종 판정 요약

```yaml
D-H1a-14_15:
  Q14:
    decision: E
    qualification_gate:
      redesign: true
      controls_are_freeze_prerequisites: false

    QF_DEFER:
      role: capability_diagnostic
      material_status: unavailable
      freeze_blocker: false

    confirmatory_fixture_as_QF_DEFER:
      allowed: false

    status_taxonomy:
      material_unavailable:
        distinct_from: diagnostic_failed
      diagnostic_failed:
        implies_subject_failure: true
      material_unavailable:
        implies_subject_failure: false

    qualification_surface:
      name: QUALIFICATION_COMMON
      treatment_arm: none
      may_reuse_existing_QF_SELECT_trials:
        only_if_byte_identical_to_old_removed_surface: true

  Q15:
    decision: G

    QF_SELECT:
      role: capability_diagnostic
      freeze_blocker: false

    QF_DEFER:
      role: capability_diagnostic
      freeze_blocker: false

  freeze:
    capability_diagnostics_control_freeze: false
    identification_contract_controls_freeze: true

  interpretation:
    diagnostic_failure:
      null_effect_requires_limitation: true
      nonzero_effect_invalidated: false

    diagnostic_unavailable:
      record_as_unknown: true
      treat_as_failure: false
```

## 전략적 결론

이번 Wolfram 검증이 보여준 핵심은 두 가지입니다.

1. **`C → S∧D`는 논리적 필연이 아닙니다.**
   즉 QF 두 개를 hard gate로 만드는 것은 식별성 자체에서 나오는 요구가
   아닙니다.

2. **SELECT와 DEFER control은 대칭입니다.**
   `S∧D`는 label swap에 대해 대칭이지만 `S`만 hard gate로 두는 순간 그
   대칭성이 깨집니다. 현재 설계에는 그 비대칭을 정당화할 별도 원리가
   없습니다.

따라서 가장 안정적인 구조는 **QF-SELECT/QF-DEFER를 모두 독립 capability
diagnostic으로 유지하면서, freeze 권한은 식별 계약에서 분리**하는 것입니다.

---

# 2. 수신 세션 실측 메모 (판정의 일부 아님)

판정문의 **사실 주장**만 대조했다. 판정 자체는 재론하지 않는다.

## 2.1 Q14.3의 조건부 전제 — **충족 확인**

판정문은 "KEPT와 REMOVED의 유일한 차이가 Q1 절이고, REMOVED가 그 절 없는
공통 표면이라면" 재실행이 불필요하다는 **조건부** 판정을 내렸다. 실측:

```python
tpl    = contract.load_h1a_native_template()
filled = contract._fill_policy_slots(tpl, "PROHIBITION_REMOVED")   # 정책 슬롯만 채운 공통 표면
removed = contract.render_arm(tpl, "PROHIBITION_REMOVED")
kept    = contract.render_arm(tpl, "PROHIBITION_KEPT")
```

| 명제 | 결과 |
|---|---|
| `removed == filled` (REMOVED에 Q1 절이 삽입되지 않음) | **True** |
| `kept == insert_liveness_clause(filled)` | **True** |
| `diff_is_restricted_to_the_liveness_clause(kept, removed)` | **True** |

따라서 `QUALIFICATION_COMMON bytes == current PROHIBITION_REMOVED bytes`가
성립하며, **기존 QF-SELECT 5/5는 재실행 불필요**하고 재분류로 처리한다.
이 실측은 코드 계약으로 고정한다(구현 §3의 새 가드).

## 2.2 "freeze와 diagnostic 분리" — 코드상 실제 결합은 없었다

판정문은 `cohort_freeze`에서 capability control을 떼라고 했다. 실측 결과
**그 결합은 애초에 코드에 존재하지 않았다**:

- `_h1a_policy.py`에 `qualification`/`QF_SELECT`/`QF_DEFER` 참조 **0건** —
  `assert_freezable()`은 qualification을 검사한 적이 없다.
- `cohort_freeze` 키를 **생산**하는 곳은 `_h1a_qualification.py:180` 하나뿐이고,
  **소비**하는 코드는 없다(테스트의 단언 제외).
- D-H1a-13 §10의 14조건 중 10번("qualification select/defer controls가 모두
  통과한다")은 **문서에만 있고 구현되지 않았다**. `_h1a_policy.py`의
  `assert_10_*`/`assert_11_*`/`assert_12_*`는 **다른 번호 체계**(D-H1a-11/12의
  policy-table 단언)이며 이 목록과 무관하다.

즉 `score_qualification()`은 **아무도 읽지 않는 freeze 판정을 스스로 발행**하고
있었다 — 권위 있어 보이지만 작동하지 않는 필드다. 판정문의 분리 지시는
코드상 "그 참칭 필드를 없애는 것"으로 실현된다. (2026-08-15 강등이 위험했던
이유도 여기 있다: 실제 freeze를 푼 것이 아니라, 사전등록 문서의 규범만
바꿔놓고 코드는 원래부터 무관했다.)

## 2.3 영향 범위 — `_h1a_qualification.py` + 테스트로 국한

`FLOOR_OR_CEILING_FAILURE`·`result_category`·`reporting_note`·`cohort_freeze`의
전체 참조가 `_h1a_qualification.py`, `test_h1a_qualification.py`,
`test_h1a_qualification_run.py` 안에만 있다. 다른 실험 폴더·루트 게이트·
confirmatory 경로에 파급 없음.

## 2.4 L 번호

사용 중: L1~L5, L8. **L9는 비어 있다**(2026-08-15에 등록했다가 철회, 발효된
적 없음). 판정문이 요구하는 "그 방향의 capability는 독립적으로 진단되지
않음" 한계는 **L9로 등록**한다 — 이번에는 강등의 부산물이 아니라 판정이
직접 명령한 한계다.

## 2.5 승인된 문구의 처리 — 구현 시 주의

Q13.3이 승인한 문장:

> `A failed qualification gate must not be reported as evidence of a null
> treatment effect.`

이 판정문은 이 문장을 명시적으로 철회하지 않았고, 대신
`diagnostic_failure: null_effect_requires_limitation: true`로 같은 취지를
재진술했다. **승인된 문장을 임의로 재작성하지 않는다**(F6이 지적한 실패
모드). 구현은 문장을 **원문 그대로 보존**하되, 판정문이 새로 명령한
`nonzero_effect_invalidated: false`를 함께 기록해 "실패해도 비-null 효과는
무효화되지 않는다"를 명시한다.
