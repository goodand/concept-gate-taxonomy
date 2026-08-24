# DESIGN DECISION — D-E2E-v1-26: subject 방언 표현력 (Q26 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_oracle_granularity|D-25]] · **D-26** · 다음 [[DESIGN_DECISION_equivalence_idioms|D-27]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-23, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_subject_dialect_expressiveness.md`
  (sha256 `e22fe5c1924a6329b24466ab659dd19bc942621f94fcfd07e45a8ed341cdcf0c`)
- 요약:
  > **Q26.1 = (a)** — subject 방언에 `implies` 추가(O1_V1 → 6종).
  > estimand 확장이 아니라 **measurement-language repair**: D-24/D-25가
  > 이미 estimand로 선언한 topology를 표현할 문법의 최소 복구.
  > **Q26.2 = 4건 전부 승인** — template은 constructor 1행 추가만(semantic
  > hint 금지); implies 임의 위치 사용 허용(제한식형↔명시형은 정규화 동치,
  > 단 양화 경계 넘는 이동·재배열은 계속 금지); 자격은 P1~P6 유지 + P7
  > (양화 아래 함의 왕복 보존) + P8(함의 위치 구분, 104 반례 쌍을 음성
  > control로) + **기존 schema 검증에 implies branch 필수**(별도 P9 불요);
  > D-21 §16 위반 아님 — gate→상신→판정→재동결의 명시적 amendment 경로.
  > **Q26.3 = (ii)** — 운영 세션 권고(유지)와 달리
  > `predicate_label_reachability`를 적격성에서 **진단 전용으로 강등**.
  > 근거: 라벨은 더 이상 primary 채점 차원이 아니므로 필요조건이 아니고
  > (PASS 가능한데 라벨 도달 불가인 상태가 실재), 유지하면 채점에서 제거한
  > lexical nuisance를 **표본 추출에서만 계속 쓰는** sampling frame 왜곡이
  > 된다. "자유도 0" 논리 기각: 결정론 선별의 재현성은 seed+동결 규칙으로
  > 충분하며 후보 유일성과는 별개(C(17,5)=6188이어도 무방).
  > **multi 풀 = 17**로 복구, 기존 5건 유지 금지 — **전체 적격 풀에서
  > 동결 selector 재실행**(우연히 같으면 그대로, 아니면 새 commitment).
  > gate는 `MEASUREMENT_SATISFIABILITY_V2`로 개정(도달성은 diagnostic 필드).
  > N·임계값 불변. **V3는 ABORTED_PRE_FREEZE로 기록, 다음 동결 = V4**
  > (필수 해시 8종: template·schema·constructor profile·canonicalization
  > profile·projection profile·satisfiability profile·manifest·prereg).

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP로 Q26의 표현력과 정규화 계약을 검토했습니다. 판정은 다음과 같습니다.

> **Q26.1 = (a) 승인 — `implies`를 subject 방언에 추가합니다.**
> **Q26.2의 4개 구속 조건도 승인**하되, P7/P8은 projection-layer 자격으로 충분하고 기존 schema-validity 검사가 새 `implies` branch를 반드시 포함해야 합니다.
> **Q26.3은 운영 세션 권고와 달리 (ii) — `predicate_label_reachability`를 적격성에서 내려 diagnostic-only로 전환**하는 것이 맞습니다.

이유는 `implies`가 없어서 현재 FOLIO topology가 **언어적으로 표현 불가능**한 반면, label reachability는 D-25 이후 더 이상 primary PASS의 필요조건이 아니기 때문입니다. 

---

# 1. Q26.1 — `implies` 추가

## 판정: **(a) 승인**

현재 target topology가 요구하는 constructor 집합을 Wolfram으로 비교했습니다.

```text
target:
forall, exists, and, pred, implies

old dialect:
forall, exists, and, pred, not

new dialect:
forall, exists, and, pred, not, implies
```

결과:

```text
OldDialectMissingTargetConstructors = {"implies"}
OldDialectExpressiveEnough          = False

NewDialectMissingTargetConstructors = {}
NewDialectExpressiveEnough          = True
```

즉 현재 2/17 문제는 모델 능력이 아니라 **subject language의 표현력 결손**입니다.

요청서의 실제 전수 측정에서도:

```text
old dialect   → 2/17 satisfiable
+ implies     → 17/17 satisfiable
```

이므로 둘이 정합합니다. 

---

# 2. 이것은 estimand 확장이 아니다

중요한 구분은:

```text
새로운 의미 현상을 측정
```

하는 것과

```text
이미 측정 대상으로 선언한 의미 현상을 표현할 문법을 제공
```

하는 것입니다.

D-24/D-25에서 이미:

```text
∀x∃y((A∧B)→C)
```

의 implication 위치를 **O1 scope topology의 일부**로 판정했습니다.

따라서 `implies` 추가는:

```text
estimand:
  before = quantifier/scope topology
  after  = quantifier/scope topology
```

이고,

```text
subject language:
  before = insufficient
  after  = sufficient
```

입니다.

즉:

> **estimand expansion이 아니라 measurement-language repair**입니다.

---

# 3. Q26.2-1 — template 개정

## 승인

다음 한 줄 추가로 충분합니다.

```json
{"kind":"implies","left":<formula>,"right":<formula>}
```

기존 지시는 그대로 둡니다.

추가로 모델에게:

> “언제 implies를 써라”

같은 semantic hint를 제공할 필요는 없습니다.

그렇게 하면 오히려 prompt가 oracle topology를 가르치는 방향으로 갈 수 있습니다.

다만 동결 artifact 관점에서는 동시에 다음이 변경되어야 합니다.

```text
template hash
schema hash
constructor-profile hash
```

---

# 4. Q26.2-2 — `implies` 자유 사용

## 승인

subject가 두 표현 중 어느 것을 사용하더라도:

### restricted form

```text
forall(x, R, B)
```

### explicit form

```text
forall(
  x,
  True,
  implies(R,B)
)
```

canonical core에서 동일하게 만들 수 있습니다.

Wolfram에서 실제 canonicalization rule을 넣어 확인한 결과:

```text
RestrictedVsExplicitSameNormalizeEqual = True
```

였습니다.

따라서 subject의 표기 자유는 neutralizable합니다.

---

# 5. 단, 내부 implication은 절대 끌어올리지 않는다

비교:

### FOLIO형

```text
FORALL x
  EXISTS y
    IMPLIES(A∧B, C)
```

### 자연 독해형

```text
FORALL x
  IMPLIES(
    A,
    EXISTS y ...
  )
```

위 두 구조는 canonicalization 후에도 서로 다르게 남아야 합니다.

Wolfram 검사:

```text
InternalImplicationRemainsDistinctFromRestrictedNaturalReading
= True
```

즉 기존 원칙:

```text
notation normalization
YES

quantifier-crossing implication rewrite
NO
```

를 그대로 유지하면 됩니다.

---

# 6. canonicalization contract

권장 정본:

```yaml
O1_CANONICAL_CORE_V3:

  forall_restricted_desugar:

    input:
      forall(x, R, B)

    output:
      forall(
        x,
        true,
        implies(R,B)
      )

  forall_true:
    idempotent: true

  implies:
    recursive_only: true

  forbidden:
    - move_implies_across_exists
    - move_implies_across_forall
    - quantifier_reordering
    - theorem_equivalence
```

핵심은 **idempotence**입니다.

이미:

```text
forall(x, True, implies(R,B))
```

인 것을 다시:

```text
forall(x, True, implies(True, implies(R,B)))
```

로 만들면 안 됩니다.

---

# 7. Q26.2-3 — P7/P8

## 판정: **승인, 기존 P1~P6과 함께라면 충분**

### P7 — implies preservation

최소:

```text
EXISTS y
  IMPLIES(A,B)
```

가:

```text
projection
→ witness
→ canonicalization
```

왕복 후에도 같은 위치에 남아야 합니다.

---

### P8 — implication location discrimination

반드시:

```text
FORALL → EXISTS → IMPLIES
```

와:

```text
FORALL → IMPLIES → EXISTS
```

가 서로 다른 signature/hash를 내야 합니다.

이전 104개 finite-model counterexample 쌍을 negative control로 사용하는 것도 적절합니다.

---

## 별도 P9는 필요하지 않음

다만 기존 generic schema qualification에 다음은 추가되어야 합니다.

```text
implies.left  = required Formula
implies.right = required Formula

missing left/right → reject
non-formula operand → reject
```

이것은 새로운 semantic qualification이 아니라 기존 **output schema validity**의 새 branch입니다.

따라서:

```text
P1–P8
+
existing schema validation updated for implies
```

면 충분합니다.

---

# 8. Q26.2-4 — D-21의 “임의 확장 금지”

## 확인: 이번 변경은 허용된 판정 경로

맞습니다.

D-21의 의도는:

```text
실험이 막힐 때 운영 세션이 몰래 constructor 추가
```

를 금지한 것입니다.

이번 경우는:

```text
Measurement Satisfiability Gate
→ 표현력 결손 검출
→ 외부 판정 Q26
→ constructor 변경 승인
→ 새 freeze
```

입니다.

따라서 architecture deviation이 아니라 **명시적 design amendment**입니다.

---

# 9. Q26.3 — predicate_label_reachability

여기서는 운영 세션의 `(i) 유지` 권고를 채택하지 않습니다.

## 판정: **(ii) diagnostic-only로 강등**

D-24 당시 이 조건의 목적은:

```text
oracle label을 subject가 생성할 수 없다
→ exact label score를 절대 PASS할 수 없다
```

를 막는 것이었습니다.

하지만 D-25에서:

```text
predicate lexical identity
→ primary score에서 제거
```

했습니다.

따라서 근거가 사라졌습니다.

---

# 10. Wolfram 논리 검사

현재 primary PASS를 단순화해서:

```text
PASS =
scope expressible
AND
binding expressible
```

라고 두고 label reachability를 별도 변수로 두었습니다.

결과:

```text
PassWithoutLabelReachabilityCountermodelExists = True

LabelReachabilityNecessaryForPrimaryPass = False

OldEligibilityIsStrictSubsetPossible = True
```

즉 다음 상태가 가능합니다.

```text
scope correct       = YES
binding correct     = YES
label reachable     = NO

O1 primary PASS     = YES
```

따라서 label reachability는 더 이상 **Measurement Satisfiability의 필요조건이 아닙니다.**

---

# 11. 유지하면 오히려 sampling frame을 바꾼다

현재:

```text
reachability 유지 → 5 eligible
reachability 제거 → 17 eligible
```

입니다. 

label을 채점하지 않으면서 eligibility에서는 label을 요구하면:

> **scope 실험인데 lexical alignment가 좋은 FOLIO만 표본으로 뽑는 것**

이 됩니다.

이는 불필요한 selection restriction입니다.

즉:

```text
scoring nuisance는 제거했는데
sampling nuisance는 남겨둔 상태
```

가 됩니다.

---

# 12. “5개뿐이라 selection freedom이 0”은 유지 근거가 아니다

조합 수를 Wolfram으로 계산하면:

```text
5 candidates에서 5 선택 = 1
17 candidates에서 5 선택 = 6188
```

입니다.

하지만 selection freedom이 많다는 것 자체가 문제가 아닙니다.

이미:

```text
frozen deterministic rule
+
frozen seed
+
pre-outcome selection
```

이 있으면 한 cohort가 결정됩니다.

즉:

```text
ZeroSelectionFreedomIsNotNeededForDeterministicSelection = True
```

입니다.

**선택의 재현성**과 **후보가 하나뿐임**은 다른 문제입니다.

---

# 13. 따라서 D-24 invariant 개정

### BEFORE

```yaml
predicate_label_reachability:
  eligibility_required: true
```

### AFTER

```yaml
predicate_label_reachability:

  eligibility_required: false

  diagnostic:
    enabled: true

  report:
    - reachable_predicate_fraction
    - unreachable_predicate_count
```

label diagnostic은 여전히 보존하십시오.

향후 lexical-semantic 실험을 할 때 유용합니다.

하지만 O1 fixture를 제거하는 근거로 쓰지는 않습니다.

---

# 14. Measurement Satisfiability Gate도 수정

### V2/V3 초기

```text
scope expressible
AND
label reachable
AND
...
```

### Q26 이후

```text
scored scope structure expressible
AND
scored binding topology expressible
AND
subject schema valid
AND
hidden witness scores PASS
```

만 load-bearing입니다.

즉:

```yaml
MEASUREMENT_SATISFIABILITY_V2:

  required:
    oracle_projection_success: true
    subject_scope_expressible: true
    subject_binding_expressible: true
    subject_schema_valid: true
    hidden_witness_scores_PASS: true

  diagnostic_only:
    predicate_label_reachability: true
```

---

# 15. FOLIO pool은 17건으로 복구

따라서 Q26 이후:

```text
FOLIO multi candidate pool
= 17
```

로 보는 것이 맞습니다.

그중:

```text
deterministic selector
+
same preregistered seed
+
same strata
```

로 5건을 선택합니다.

사람이 결과를 보고 고르는 것은 금지합니다.

---

# 16. 기존 5건을 그대로 유지하는 것도 권하지 않음

“마침 reachability를 만족했던 5건이 있으니 그냥 그 5건을 쓰자”는 방식은 깔끔하지 않습니다.

왜냐하면 이제 eligibility rule 자체가 달라졌기 때문입니다.

권장:

```text
17 eligible
↓
frozen deterministic selector를 처음부터 재실행
↓
새 FOLIO 5
```

입니다.

우연히 동일한 5개가 나오면 그대로 사용하면 되고, 아니면 새 commitment를 만듭니다.

---

# 17. threshold/N은 변경 없음

```yaml
N: 20

PMB:
  N: 15

FOLIO_multi:
  N: 5
  PASS_min: 4

overall:
  PASS_min: 16

final_ERROR: 0
unexpected_UNSCORABLE: 0
```

모두 유지합니다.

---

# 18. freeze 절차

Q26은 동결 surface 변경입니다.

따라서 V3를 억지로 이어 쓰지 말고, 다음 freeze version을 새로 만드는 것이 좋습니다.

예:

```text
V3 draft
→ BLOCKED_BY_Q26

D-E2E-v1-26
→ dialect amendment

V4
→ new frozen surface
```

V3가 실제 freeze 전에 막혔다면 `ABORTED_PRE_FREEZE` 정도로 기록하고 새 버전을 만들면 됩니다.

필수 hash:

```text
subject template
subject schema
constructor profile
canonicalization profile
projection profile
measurement satisfiability profile
fixture manifest
preregistration
```

---

# 최종 판정

```yaml
D_E2E_v1_26:

  Q26_1:
    decision: A

    subject_dialect:
      add:
        kind: implies
        fields:
          left: Formula
          right: Formula

    interpretation:
      estimand_expansion: false
      measurement_language_repair: true

    observed_effect:
      FOLIO_multi_satisfiable:
        before: 2_of_17
        after: 17_of_17

  Q26_2:

    template:
      one_constructor_line_addition: sufficient
      additional_semantic_hint: forbidden

    implies_usage:
      arbitrary_formula_position: allowed

    canonicalization:
      restricted_forall_to_explicit_implies: allowed
      explicit_implies_same_position: equivalent_representation
      move_implies_across_quantifier: forbidden
      quantifier_reorder: forbidden

    qualification:
      P1_to_P6: retain

      P7:
        implication_roundtrip_under_quantifier: required

      P8:
        implication_position_discrimination: required

      generic_schema_validation:
        implies_branch: required

      additional_P9: not_required

    governance:
      D21_arbitrary_extension_violation: false
      externally_approved_dialect_amendment: true

  Q26_3:
    decision: II

    predicate_label_reachability:
      eligibility_condition: false
      diagnostic_only: true

    reason:
      label_identity_is_not_primary_scored_dimension: true
      reachability_not_required_for_PASS: true
      retaining_it_would_change_sampling_frame_for_unscored_reason: true

    FOLIO_multi_pool:
      eligible_after_implies: 17

    selection:
      N: 5
      deterministic: true
      frozen_seed: true
      rerun_selector_from_full_eligible_pool: true

  acceptance:
    N: 20
    overall_PASS_min: 16
    FOLIO_multi_PASS_min: 4_of_5
    final_ERROR: 0
    unexpected_UNSCORABLE: 0

  refreeze:
    required: true
```

가장 중요한 결론은 두 가지입니다.

1. **`implies`는 새 능력을 시험하기 위한 확장이 아니라, 이미 oracle이 요구하고 있던 scope topology를 subject가 표현할 수 있게 하는 최소 복구입니다.**
2. **predicate label을 더 이상 채점하지 않는다면, label reachability로 fixture를 탈락시키는 것도 같이 중단해야 합니다.** 그렇지 않으면 평가에서는 lexical nuisance를 제거하면서 표본 추출에서는 같은 nuisance를 계속 사용하게 됩니다.
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | 결손 constructor = {implies}; 2/17→17/17 | 이 세션의 게이트 전수 실측(요청서 §2)과 교차 참조 | **CONFIRMED** |
| V2 | 제한식형 ≡ 명시형 (정규화 후 동일) | 실제 `desugar`+`evaluate` 기계 확인 | **CONFIRMED** |
| V3 | ∃ 아래 함의는 정규화 후에도 제한식형 자연 독해와 구분 | 동일 기계 확인 (판정 §5의 쌍 그대로) | **CONFIRMED** |
| V4 | 정규화 idempotence — 이중 implies 포장 없음 | `desugar(desugar(x))==desugar(x)` + implies 수 1 확인 | **CONFIRMED** |
| V5 | C(17,5) = 6188 | 재계산 | **CONFIRMED** |

주의 기록 (적용 시 구속 해석):

1. **P14 재발 방지 각주**: 운영 세션의 Q26.3 권고(유지)가 기각됐다 —
   판정 논거(sampling frame 왜곡·자유도 0 무근거)를 수용하며, 이 기각은
   상신서에 양안을 실측과 함께 제시한 관행이 작동한 사례로 기록한다.
2. **V4 재선별은 seed 순서 상위 5**가 아니라 "동결 selector를 전체 적격
   풀(17)에서 재실행"이다 — 우연히 V2의 5건과 같으면 유지, 다르면 새
   commitment (§16).
3. gate 구현의 GATE_ID는 `MEASUREMENT_SATISFIABILITY_V2`로 개정하고
   도달성은 required가 아니라 diagnostic 필드로 배선한다(§14).
4. `example_id` 부재 record 1건은 판정이 다루지 않았다 — 식별자 없는
   commitment는 D-20 완전성 요건상 불성립이므로 적격성에서 기계 제외하고
   V4 기록에 명문화한다(선별 전 제외 — outcome 무관).

수신 텍스트의 sha256 (규약: BEGIN 마커 다음 개행부터 END 마커 직전까지 UTF-8):
`VERBATIM_SHA256: e4756433768660af3154d93d76aaf96950ea3fe4c42dbc4b3c59106e7c434c70`
