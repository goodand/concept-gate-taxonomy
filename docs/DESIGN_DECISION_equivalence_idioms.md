# DESIGN DECISION — D-E2E-v1-27: 동치 관용구와 측정 경계 (Q27 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_subject_dialect_expressiveness|D-26]] · **D-27** · 다음 [[DESIGN_DECISION_pmb_projection_signal_loss|D-28]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-23, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_equivalence_idioms.md`
  (sha256 `09340cdc863e852b1431...` — 전체는 git 이력)
- 요약:
  > **판정 원리**: "논리적으로 동치인가"와 "이 실험에서 같은 답으로
  > 취급해야 하는가"는 **다른 질문**이다. 기준은 그 변환이 **O1이 현재
  > 점수화하는 축(양화 종류·순서·부정/함의 위치·결박)을 건드리는가**다.
  > **Q27.1 = (c)** — **curry만** 국소 정규화 허용
  > (`implies(and(A,B),C) ↔ implies(A,implies(B,C))`, 정본형은 uncurried,
  > 양화·부정 경계 교차 금지, 진리표 검증 artifact를 profile hash와 함께
  > 동결). **`¬∃ ↔ ∀¬`는 불허** — 논리 동치는 확인되나 scored quantifier
  > type을 exists→forall로 바꾸므로, 허용하면 "quantifier type is scored"
  > 계약을 부분 철회하는 것이 되고 그것은 estimand 변경 사안이다.
  > 열린 정리-동치 엔진은 계속 금지 — 허용된 것은 **닫힌 열거 표**다.
  > **Q27.2 = (b)** — PMB 대명사/고유명 fixture를 **표면 규칙으로 제외**.
  > projection folding 불허(∃ 참여자와 지정 개체는 논리적으로 비동치 —
  > Male(e) 가정 하에서도 반례 존재). **synset만 보고 제거하는 것도 금지**
  > ("a man"의 ∃는 진짜 명사 양화일 수 있음). PMB 15건은 새 표면 필터로
  > **재census·재선별 필수**, 15건 미만이면 BLOCKED 재상신(임계값·비율
  > 자동 하향 금지).
  > **Q27.3 = control 전용 보수 선별 규칙 정본화** — 표면(지원 한정사 정확
  > 1개·대명사/고유명/관용구/미지원 한정사 부재·길이 상한(값은 운영이
  > 재선별 전 확정))**과** oracle projection 복잡도(target 양화 1·중첩 0·
  > 참여자 추가 양화 0·미지원 연산자 0·satisfiable) **양층 통과**.
  > source별 최소 branch 커버(단순 보편 1~2 + 단순 존재 1) — FOLIO의
  > 제한식→implication 경로를 시험하려면 implication을 전부 배제하면 안 됨.
  > control은 **모집단 대표 표본이 아니라 measurement-chain sanity check**
  > 임을 사전등록에 명기. 기존 1/6 기록은 보존(qualification failure).
  > **Q27.4 = 승인** — Measurement Satisfiability는 **필요조건**이며 자연
  > 도달성의 충분조건이 아니다. 게이트 2층: **Gate A**(형식적 가능성,
  > 결정론 witness) + **Gate B**(경험적 사용가능성, 실제 cold subject로
  > control). Gate B를 결정론 oracle 게이트로 만들면 Gate A의 중복 측정이
  > 되므로 금지. 코호트는 control 통과까지 차단 유지.
  > 부수: 이 2층 구분은 향후 MCP 사용 테스트(Level 5~7)에도 그대로 적용 —
  > "tool callable ≠ tool naturally usable".

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP 검증 결과를 기준으로 보면, Q27은 **동치성 자체보다 “그 동치 변환이 현재 O1이 점수화하는 축을 건드리는가”**로 판정해야 합니다.

결론은 다음과 같습니다.

> **Q27.1 = (c): curry만 국소 정규화 허용. `¬∃ ↔ ∀¬`는 허용하지 않음.**
> **Q27.2 = (b): PMB 대명사/고유명 fixture를 O1-v1에서 기계적으로 제외.**
> **Q27.3 = control 전용의 보수적인 기계 선별 규칙을 정본화.**
> **Q27.4 = 승인: Measurement Satisfiability는 필요조건일 뿐 자연 도달성의 충분조건이 아님.**

현재 control 1/6은 모델 성능 실패라기보다, **V4가 “표현 가능”과 “자연스럽게 같은 표상을 낼 수 있음”을 구분하지 못했다는 qualification failure**로 해석하는 것이 맞습니다. 본 cohort는 아직 dispatch 0건입니다. 

# 1. Q27.1 — 두 동치쌍은 논리적으로는 모두 동치

먼저 Wolfram으로 확인했습니다.

### Curry

[
(A\land B)\rightarrow C
]

와

[
A\rightarrow(B\rightarrow C)
]

는 모든 Boolean valuation에서 일치했습니다.

```text
CurryEquivalent_AllBooleanCases = True
```

### 부정된 존재양화

[
\neg\exists x(R(x)\land B(x))
]

와

[
\forall x(R(x)\rightarrow\neg B(x))
]

도 2원소 domain의 모든 해석에서 일치했습니다.

```text
NegExistsVsForallNeg_Equivalent_OnAll2ElementInterpretations = True
```

따라서 두 사례 모두 **classical logical equivalence**라는 운영 세션의 판단은 맞습니다.

하지만 실험 설계 판정은 여기서 끝나지 않습니다.

---

# 2. O1의 scored dimension을 건드리는지가 다르다

현재 O1은 명시적으로 다음을 측정합니다.

```text
quantifier type
quantifier order
negation position
implication position
binding
```

두 변환을 이 기준으로 다시 보면 차이가 생깁니다.

Wolfram으로 signature를 비교하면:

```text
CurryChangesQuantifierTypeOrCount = False

NegExistsToForallNegChangesQuantifierType = True
```

즉:

### Curry

```text
(A ∧ B) → C
```

→

```text
A → (B → C)
```

는 **quantifier operator를 바꾸지 않습니다.**

반면:

```text
NOT EXISTS
```

→

```text
FORALL ... NOT
```

은 실제로:

```text
EXISTS → FORALL
```

로 scored quantifier kind를 바꿉니다.

---

# 3. 따라서 Q27.1 = **(c)**

## Curry만 허용

다만 일반적인 theorem equivalence를 여는 것이 아닙니다.

정확히 다음 한 패턴만 허용합니다.

```text
(A AND B) IMPLIES C
↔
A IMPLIES (B IMPLIES C)
```

그리고 **quantifier/negation boundary를 가로지르지 않는 동일 local Boolean region 안에서만** 적용합니다.

예:

```text
FORALL x
  EXISTS y
    ((A ∧ B) → C)
```

에서 안쪽 Boolean skeleton의 curry는 허용 가능합니다.

하지만:

```text
FORALL
↔ EXISTS 이동
```

이나

```text
NOT
↔ quantifier 이동
```

은 그대로 금지합니다.

---

# 4. 권장 canonical rule

예를 들어 uncurried form을 정본으로 정할 수 있습니다.

```yaml
O1_LOCAL_IDIOM_NORMALIZATION_V1:

  curry:
    enabled: true

    equivalence:
      left:
        implies(and(A, B), C)

      right:
        implies(A, implies(B, C))

    canonical_form:
      implies(and(A, B), C)

    constraints:
      same_quantifier_region: true
      same_negation_region: true
      may_cross_quantifier: false
      may_cross_negation: false
```

그리고 이 exact pair의 truth-table verification artifact를 profile hash와 함께 동결합니다.

---

# 5. `¬∃ ↔ ∀¬`는 왜 허용하지 않는가

논리적으로 틀려서가 아닙니다.

현재 O1의 선언된 target이:

```text
target_quantifier_type
```

까지 포함하기 때문입니다.

이를 허용하면:

```text
Nobody ...
```

에서 모델이:

```text
NOT EXISTS
```

를 썼는지

```text
FORALL NOT
```

을 썼는지

더 이상 구분하지 않게 됩니다.

그러면 기존:

```text
quantifier type is scored
```

계약을 부분적으로 철회하는 셈입니다.

따라서 이 변환을 도입하려면 단순 normalization amendment가 아니라 **O1 estimand 변경**이 필요합니다.

현재 Q27에서는 하지 않습니다.

---

# 6. 이 규칙이 theorem-equivalence 금지를 무너뜨리는가

아닙니다. 단 다음처럼 명시해야 합니다.

### 금지된 기존 방식

```text
arbitrary formula
↓
theorem prover
↓
equivalent canonical formula
```

### 이번 허용

```text
AST
↓
exact frozen syntactic pattern match
↓
one enumerated rewrite
```

즉:

```text
open-ended equivalence engine = NO
closed equivalence idiom table = YES
```

입니다.

---

# 7. Q27.2 — PMB 대명사 참여자 ∃

여기는 curry와 완전히 다른 문제입니다.

예를 들어 PMB:

[
\exists x(Male(x)\land P(x))
]

를 subject의:

[
P(he)
]

와 동일 취급한다고 합시다.

이건 일반적으로 논리적 동치가 아닙니다.

Wolfram 전수 검사:

```text
ExistsParticipantVsEntityPredicateEquivalent = False
CountermodelCount = 5
```

심지어 지정된 entity가 `Male`이라고 추가 가정해도:

```text
EvenAssumingMaleOfDesignatedEntity_Equivalent = False
```

였습니다.

즉 단순히:

```text
male/person participant ∃
→ entity
```

로 folding하면 의미 변환이 됩니다.

---

# 8. 따라서 Q27.2 = **(b)**

O1-v1에서는 PMB의 대명사/고유명 포함 fixture를 **surface-rule로 제외**하는 것이 가장 안전합니다.

이유는:

```text
PMB referent
↔ source pronoun entity
```

의 정확한 alignment를 보장하는 별도 외부 annotation contract가 현재 요청서에 제시되어 있지 않기 때문입니다.

그 상태에서 projection이 이를 추측하면 Oracle Adapter가 semantic judge가 됩니다.

---

# 9. 기계적 exclusion rule

권장:

```yaml
PMB_O1_V1_PARTICIPANT_FILTER:

  exclude_if_source_contains:
    - personal_pronoun
    - possessive_pronoun
    - demonstrative_pronoun
    - proper_name

  reason:
    participant_reference_encoding_mismatch
```

실제 구현에서는 동결된 tokenizer/tagger 또는 명시적 token lexicon을 사용하십시오.

중요한 것은:

```text
male.n.*
person.n.*
```

자체를 모두 제외하면 안 된다는 점입니다.

예를 들어:

```text
a man ...
```

의 existential participant는 실제 overt nominal quantification일 수 있습니다.

따라서 **oracle synset만 보고 제거하는 것은 금지**합니다.

---

# 10. PMB 15건은 재선별 필요

현재 in-N 15건에 대명사형 participant가 만연할 위험이 있다고 보고되어 있습니다. 

따라서:

```text
기존 PMB 15 그대로 사용
```

하면 안 됩니다.

먼저 전체 eligible pool에 새 surface filter를 적용해 다시 census합니다.

### 충분하면

같은 deterministic selector + frozen seed로 PMB 15를 재선별.

### 15건 미만이면

```text
BLOCKED
```

로 보고하고 재상신합니다.

threshold나 PMB 비율을 자동으로 낮추지 않습니다.

---

# 11. 왜 projection folding보다 exclusion이 낫나

현재 O1-v1의 목적은 **빠르게 quantifier-scope 사용 테스트를 시작하는 것**입니다.

대명사 referent projection까지 해결하려 하면:

```text
coreference alignment
entity anchoring
pronoun semantics
name semantics
```

가 새 measurement subsystem으로 들어옵니다.

이건 O1을 빠르게 실행하려는 현재 목적과 반대입니다.

따라서 v1에서는:

> **어려운 현상을 일반화해 해결하지 말고, estimand와 무관한 현상을 기계적으로 제거**

하는 것이 맞습니다.

PMB pronoun handling은 이후 별도 extension으로 남기면 됩니다.

---

# 12. Q27.3 — control 선별 규칙

운영 세션의 초안 방향은 맞지만, **surface 조건만으로는 부족**합니다.

이번 FOLIO monitor 사례처럼 surface상 단순해 보여도 gold abstraction이 subject의 자연 표현과 다를 수 있기 때문입니다. 

따라서 control은 두 층을 모두 통과해야 합니다.

---

# 13. Control Eligibility = Surface Simplicity + Oracle Simplicity

## A. Surface filter

권장:

```yaml
surface:

  overt_supported_quantifier_count: 1

  overt_quantifier_lexicon:
    - all
    - every
    - each
    - some
    - no

  exclude:
    pronoun: true
    proper_name: true

    known_idiom:
      - "anything but"
      - "all right"
      - "at all"
      - "all of a sudden"

    unsupported_quantifier:
      - few
      - fewer
      - several
      - many
      - most   # if not supported by this control profile
```

실제 지원 lexicon과 맞춰 동결해야 합니다.

---

# 14. 문장 길이 상한

허용하되 **실험 결과를 보고 정하지 말고 사전 고정**합니다.

예를 들어:

```text
token_count <= 15
```

정도의 engineering bound를 둘 수 있습니다.

다만 제가 특정 숫자를 필수 정본으로 강제할 근거는 현재 자료에 없습니다.

따라서:

```yaml
max_tokens:
  required_to_freeze: true
  exact_value: operations_select_before_reselection
```

정도로 판정합니다.

---

# 15. B. Projected oracle complexity filter

이쪽이 더 중요합니다.

control은 representative benchmark가 아니라 **measurement-chain sanity check**입니다.

그러므로 gold를 이용해 단순한 구조만 고르는 것이 허용됩니다.

권장:

```yaml
oracle_projection:

  target_quantifier_count: 1

  nested_target_quantifier_count: 0

  participant_extra_quantifier_count: 0

  unsupported_operator_count: 0

  measurement_satisfiable: true
```

그리고 source별 adapter가 제대로 작동하는 최소 구조여야 합니다.

---

# 16. implication control은 별도 strata로 관리

FOLIO에서는 `forall restriction`이 canonical core에서 implication이 됩니다.

따라서 모든 implication을 control에서 제거하면 FOLIO adapter의 핵심 path를 시험하지 못합니다.

권장:

### Simple universal control

```text
FORALL
  restriction
  body
```

1~2건

### Simple existential control

```text
EXISTS
```

1건

처럼 source별 최소 branch를 명시적으로 커버합니다.

---

# 17. Control은 capability benchmark가 아니다

이것을 사전등록에 명시하십시오.

```text
Control fixture selection is intentionally conservative.

Controls are not sampled to represent the O1 population.
They are selected to establish that a valid, simple, model-reachable
instance can traverse the frozen measurement contract.
```

그래서 main cohort보다 엄격한 단순성 조건을 써도 문제가 없습니다.

---

# 18. control을 다시 재선별해도 되는가

네.

현재 1/6 결과가 **control-selection contract의 결함을 드러낸 상태**이고 main cohort dispatch는 0건입니다. 

따라서 D24/D25와 동일한 amendment 절차를 사용합니다.

```text
old controls
→ historical qualification evidence

new control eligibility profile
→ deterministic reselection

new controls
→ qualification rerun
```

기존 1/6 기록을 삭제하지 않습니다.

---

# 19. Q27.4 — Measurement Satisfiability의 지위

## 판정: **승인**

이번 실측은 아주 중요한 구분을 보여줍니다.

Measurement Satisfiability는:

[
\exists y\in SubjectLanguage:
Score(y,Oracle)=PASS
]

를 뜻합니다.

즉 **PASS 가능한 표현이 존재한다**는 것뿐입니다.

하지만 실제 LLM이 자연스럽게 그 표현을 낼 가능성까지 보장하지 않습니다.

---

# 20. Wolfram 논리 모델

다음 관계를 가정합니다.

[
NaturallyReachable \Rightarrow Satisfiable
]

가능한 상태는:

```text
Natural   SAT
False     False
False     True
True      True
```

입니다.

Wolfram 결과:

```text
Counterexample_SatisfiableButNotNaturallyReachable
= {False, True}
```

즉:

[
Satisfiable
\not\Rightarrow
NaturallyReachable
]

입니다.

이번 control이 바로 그 counterexample을 실제 시스템에서 발견한 것입니다.

---

# 21. 따라서 gate 구조를 2단계로 정의

## Gate A — Measurement Satisfiability

질문:

> PASS 가능한 출력이 언어 안에 존재하는가?

결정론적 hidden witness.

---

## Gate B — Control Reachability

질문:

> 간단하고 정상적인 입력에서 실제 subject가 frozen contract를 통과할 수 있는가?

실제 cold subject를 사용.

```text
Gate A PASS
+
Gate B PASS
→ main cohort interpretable
```

입니다.

---

# 22. 중요한 차이

Control Reachability를 다시 deterministic oracle gate로 만들면 안 됩니다.

그러면 다시 Satisfiability만 중복 측정합니다.

Control의 목적은 실제 LLM 사용 테스트입니다.

즉:

```text
Satisfiability
= formal possibility

Control
= empirical usability
```

로 두십시오.

이 구분은 이후 MCP 사용 테스트에서도 그대로 재사용할 수 있습니다.

---

# 23. 이번 Q27이 Level 5~7 Fast Track에도 주는 교훈

앞서 이야기했던 빠른 MCP 사용 테스트에도 똑같이 적용됩니다.

MCP API가 호출 가능하다는 것:

```text
Tool callable
```

은

LLM이 실제로 적절하게 사용할 수 있다는 것:

```text
Tool naturally usable
```

과 다릅니다.

즉 향후 MCP 테스트도:

```text
formal satisfiability
↓
simple live controls
↓
real cohort
```

3층으로 가면 됩니다.

현재 O1 control에서 그 구조를 먼저 발견한 셈입니다.

---

# 최종 판정

```yaml
D_E2E_v1_27:

  Q27_1:
    decision: C

    local_equivalence_normalization:

      curry:
        allowed: true

        equivalence:
          "(A AND B) -> C":
            "A -> (B -> C)"

        constraints:
          frozen_pair_only: true
          finite_truth_table_verified: true
          cross_quantifier_boundary: false
          cross_negation_boundary: false

      neg_exists_forall_neg:
        allowed: false

        logical_equivalence:
          verified: true

        rejection_reason:
          changes_scored_quantifier_type: true

    arbitrary_theorem_equivalence:
      allowed: false

  Q27_2:
    decision: B

    PMB_pronoun_participant:

      projection_fold_to_entity:
        allowed: false

      reason:
        existential_participant_and_designated_entity_not_logically_equivalent: true

    eligibility:

      exclude_source_with:
        - pronoun
        - proper_name

      synset_only_filter:
        allowed: false

    PMB_stratum:
      re_census_required: true
      deterministic_reselection_required: true

      if_eligible_count_below_15:
        status: BLOCKED
        re_adjudication: required

  Q27_3:

    control_profile:
      frozen: true

      surface:
        exactly_one_supported_overt_quantifier: true
        pronoun_absent: true
        proper_name_absent: true
        unsupported_quantifier_absent: true
        known_idiom_absent: true
        max_length_bound: required

      oracle_projection:
        target_quantifier_count: 1
        nested_target_quantifier_count: 0
        extra_participant_quantifier_count: 0
        unsupported_operator_count: 0
        measurement_satisfiable: true

      purpose:
        representative_population_sample: false
        measurement_chain_sanity_check: true

    old_control_results:
      retain: true
      interpretation: qualification_failure

    reselection:
      deterministic: true
      pre_outcome_rule: true

  Q27_4:

    MeasurementSatisfiability:
      necessary_condition: true
      sufficient_for_natural_reachability: false

    ControlReachability:
      empirical_gate: true

    main_cohort_interpretable_if:
      - MeasurementSatisfiability_PASS
      - ControlReachability_PASS

  cohort:
    dispatch:
      remain_blocked_until_controls_pass: true
```

가장 중요한 판정은 **“논리적으로 동치인가?”와 “이 실험에서 같은 답으로 취급해야 하는가?”는 다른 질문**이라는 점입니다.

Curry는 동치이면서 O1의 양화 축을 건드리지 않으므로 notation normalization으로 취급할 수 있습니다. 반면 `¬∃ ↔ ∀¬`도 논리적으로 동치지만 **현재 O1이 명시적으로 측정하는 quantifier kind를 바꾸므로**, 지금 단계에서는 같은 답으로 합치면 안 됩니다.

그리고 이번 1/6은 Measurement Satisfiability Gate의 실패가 아니라 그 다음 단계, 즉 **“형식적으로 가능한 답을 실제 LLM이 자연스럽게 생성할 수 있는가”를 처음 측정한 유효한 control 결과**로 보는 것이 정확합니다. 
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | curry 동치 (전 Boolean valuation) | 8 valuation 전수 | **CONFIRMED — 불일치 0** |
| V2 | `¬∃(R∧B) ↔ ∀(R→¬B)` 동치 (2원소 전 해석) | 16 해석 전수 | **CONFIRMED — 불일치 0** |
| V3 | curry는 양화축 불변 / `¬∃→∀¬`는 scored 양화 종류 변경 | 실제 `project_scope_for_case` signature 대조 | **CONFIRMED** — curry 양화열 `[forall]`=`[forall]`, ¬∃/∀¬는 `[exists]`vs`[forall]`이며 signature 불일치 |
| V4 | `∃x(Male∧P)` vs `P(e)` 비동치, 반례 5 | 전수 열거 | **CONFIRMED — 2원소·지정개체 고정 16 해석 중 반례 정확히 5**; Male(e) 가정 추가 시에도 8 중 1 (비동치 유지) |
| V5 | Satisfiable ⇏ NaturallyReachable | 이 세션 V4 control 실측(1/6)이 실물 반례 | **CONFIRMED (경험적 교차 참조)** |

부수 실측 (판정 적용에 직접 쓰이는 사실):

- **curry 정규화는 아직 미구현**이다 — V3a에서 curry 쌍의 projection
  signature가 현재 **불일치**(`signature 동일: False`). 즉 Q27.1(c)은
  신규 구현 대상이며, 구현 후 이 쌍이 일치로 바뀌는 것이 회귀 계약이 된다.
- 판정 §14가 남긴 유일한 열린 값: control 문장 길이 상한. 운영이 재선별
  **전에** 확정·동결해야 한다(결과 관측 후 결정 금지).

주의 기록 (적용 시 구속 해석):

1. **P14 2회 연속**: Q26.3과 Q27.1 모두에서 운영 세션 권고가 부분 기각
   됐다(도달성 유지 → 강등, 동치 2쌍 → curry만). 두 기각 모두 "채점축을
   건드리는가"라는 같은 기준에서 나왔다 — 앞으로 동치·정규화 제안 시
   **먼저 scored dimension 영향을 실측 signature로 제시**한다.
2. **PMB 15 재선별은 Q24·Q26의 "우연히 동일" 경로와 다르다** — 새 표면
   필터가 in-N 표본을 실제로 바꿀 가능성이 크다. 재census 결과가 15 미만
   이면 임계값을 만지지 않고 BLOCKED 상신한다(판정 §10).
3. **control 재선별 시 기존 6건 결과는 삭제하지 않는다** — V4 control
   1/6은 qualification failure의 역사적 증거로 보존(판정 §18).
4. **Gate B의 성격**: control은 실제 LLM dispatch여야 하며, 결정론 검사로
   대체하면 Gate A의 중복이 된다(판정 §22). 즉 control 재실행은 매번
   사용자 승인 대상 dispatch다.

수신 텍스트의 sha256 (BEGIN 다음 개행 ~ END 직전, UTF-8):
`VERBATIM_SHA256: afa811932d0d2d7b3394092279faa6429594c409a5690cd8cdecb84139245294`
