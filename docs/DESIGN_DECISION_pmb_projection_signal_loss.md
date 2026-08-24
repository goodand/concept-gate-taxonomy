# DESIGN DECISION — D-E2E-v1-28: projection 신호 소실과 층 술어 (Q28 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_equivalence_idioms|D-27]] · **D-28** · 다음 [[DESIGN_DECISION_cardinal_dialect_and_mrs_source|D-29]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-23, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_pmb_projection_signal_loss.md`
  (sha256 `61fef029a712c4515ac02b2c…`)
- 요약:
  > **새 failure class 인정**: "nuisance를 제거하는 projection이 그 자체로
  > measurement destruction을 일으킬 수 있다." 앞으로는 `projection
  > succeeds`가 아니라 **`projection succeeds AND target signal survives`**
  > 를 확인해야 한다.
  > **Q28.1 = (d)** — 사건 술어를 참여자 술어로 **재작성 금지**
  > (`∃e(Smile(e)∧Agent(e,x)) ≢ Smile(x)`). 대신 측정 전용
  > **`PMB_EVENT_INCIDENCE_PROJECTION_V1`**: 사건 술어의 **어휘 진리값은
  > 버리고**, role edge로부터 "이 양화된 참여자가 body의 어떤 내용 술어에
  > 참여한다"는 **결박 incidence만 무라벨 slot으로 보존**. 보존: 양화
  > 계보·부정/함의 위치·제한/본문 영역·참여자 incidence·술어 occurrence
  > 존재. fail-closed: 참여자 incidence 0 / 중첩 사건 결합 모호 / scope
  > 교차 / 양화 재배열 필요. **신규 `ProjectionSignalGate` 필수**.
  > **Q28.2 = (c)** — G1 비례 분류기 즉시 정정(bare `\bmost\b` 금지,
  > 최상급 제외, `most of`·`most+복수명사`만). G2 현행 기수 3건은 제거하되
  > **조용한 재배분 금지** — cardinal·proportional은 **이미 O1 declared
  > boundary에 있으므로** 삭제는 명시적 boundary amendment다. 두 갈래를
  > 명시 선택: (i) full O1 유지(진짜 기수 source 재조사+표현 지원) 또는
  > (ii) **`O1_CORE_V1`**으로 재동결하며 cardinal/proportional을
  > **deferred**로 명기(빠른 실사용 테스트가 목적이면 판정자 권고).
  > 결과 표기도 "O1-Core ScopeMatch"로 바뀌어야 하며 "full O1 boundary
  > accuracy"라 부를 수 없다. 정정: 기수 constructor 추가는 declared
  > boundary 확대가 **아니다**(이미 포함) — implies와 구조적으로 유사한
  > coverage 복구다. 단 현행 3건(several/many/how many)은 성격이 서로
  > 달라 그 근거가 되지 못한다.
  > **Q28.3 = PMB `REQUALIFICATION_REQUIRED`** — source 폐기 아님. 확정된
  > 것은 "old projection = unsuitable"이지 "PMB = impossible"이 아니다.
  > 15건 patch 금지, **전체 풀 재census**(표면→scope 관련성→새 projection→
  > signal gate→satisfiability→material audit→결정론 선별). 부족하면
  > **FOLIO 단독 자동 전환 금지** — 독립 문장 단위 source 재조사가 기본이며
  > FOLIO-only는 별도 governance amendment.
  > **Q28.4 = Gate C 승인** (사람의 재료 감사, 동결 전). 단 "예상 subject
  > 형태"를 사람이 적는 것은 **금지**(새 수동 oracle이 된다) — 대신 문장·
  > 층·overt trigger·투영 signature·채점 차원·버려진 구조·signal/SAT 상태를
  > 표시하고 5개 질문에 OK/BLOCK만. Gate 3층 확정: **A**(형식 측정 타당성)
  > → 결정론 선별 → **C**(사람 재료 감사) → freeze → **B**(live control)
  > → 코호트. Gate C가 규칙을 바꾸면 **후보 풀부터 결정론 선별을 다시**
  > 하며 사람이 교체 fixture를 고르지 않는다.
  > **코호트 dispatch 계속 차단.**

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP로 Q28의 핵심을 검토했습니다. 이번에는 **PMB를 바로 폐기할 필요는 없지만, 현재 projection을 그대로 유지해서도 안 됩니다.**

판정은 다음과 같습니다.

> **Q28.1 = (d)** — 사건 술어를 참여자 술어로 “논리식 재작성”하지 않고, **측정 전용 event-incidence projection**을 도입합니다.
> **Q28.2 = (c)** — G1 층 술어는 즉시 정정하되, cardinal/proportional을 조용히 삭제·재배분하지 않습니다. 원래 O1 boundary에 이미 포함되어 있으므로 삭제는 명시적 boundary amendment입니다.
> **Q28.3 = 조건부 PMB 유지** — 새 projection과 signal gate를 통과하는 PMB material만 사용합니다.
> **Q28.4 = Gate C 인간 material audit 승인**, 그리고 그 앞에 기계적인 **Projection Signal Gate**도 둡니다.

현재 발견은 단순 fixture 오류가 아니라, **projection이 nuisance를 제거하면서 target signal까지 제거할 수 있다는 새로운 failure class**입니다. 

---

# 1. Q28.1 — `smile(e)+Agent(e,x)`를 `smile(x)`로 바꿔도 되는가

## 그대로는 **안 됩니다**

Wolfram으로 다음을 비교했습니다.

[
\exists e,[Smile(e)\land Agent(e,x)]
]

vs.

[
Smile(x)
]

bridge axiom 없이 전수 Boolean countermodel을 만들면:

```text
EventExistentialVsDirectParticipantPredicateEquivalent = False
CountermodelCount = 16
```

입니다.

즉:

[
\exists e(Smile(e)\land Agent(e,x))
\not\equiv Smile(x)
]

입니다.

따라서 Q28.1(a)를:

```text
PMB event formula
→ participant-level formula
```

라는 **semantic rewrite**로 구현하면 안 됩니다.

---

# 2. 하지만 측정 projection으로는 가능

Q25에서 이미:

> projection은 새로운 gold formula가 아니라 measurement function

이라고 경계를 만들었습니다.

이번에도 같은 원칙을 적용할 수 있습니다.

### 금지

```text
smile(e)
Agent(e,x)
↓
assert smile(x)
```

### 허용

```text
smile(e)
Agent(e,x)
↓
measurement projection
↓
unlabeled predicate occurrence attached to x
```

즉 결과가:

```text
PRED_SLOT{x}
```

입니다.

이 `PRED_SLOT`은 새로운 semantic predicate가 아닙니다.

---

# 3. 권장 새 profile

## `PMB_EVENT_INCIDENCE_PROJECTION_V1`

예를 들어 PMB:

```text
FORALL x
  EXISTS e
    smile(e)
    Agent(e,x)
```

를 full semantics로 다시 쓰지 않고 측정용으로:

```text
FORALL x
  BODY:
    PRED_SLOT(x)
```

로 투영합니다.

subject:

```text
FORALL x
  BODY:
    smiled(x)
```

에서도 label은 이미 scoring 밖이므로:

```text
FORALL x
  BODY:
    PRED_SLOT(x)
```

가 됩니다.

따라서 두 쪽이 같은 scope signature를 가질 수 있습니다.

---

# 4. Wolfram으로 확인한 경계

작은 graph contraction으로 검사했을 때:

```text
TargetParticipantUnderForallBefore = True
TargetParticipantUnderForallAfter  = True
QuantifierAncestryPreserved        = True
LogicalEquivalenceClaimed          = False
```

였습니다.

그리고 oracle event-role graph와 subject direct-predicate graph를 동일한 incidence signature로 만들면서도 scope mutation은 구별할 수 있었습니다.

```text
EventRoleIncidenceProjectionCanMatchDirectPredicateIncidence = True
ScopeMutationStillDistinguishable = True
```

이것이 Q28의 안전한 중간 지점입니다.

---

# 5. 무엇을 보존해야 하는가

새 projection에서 반드시 보존:

```text
quantifier type
quantifier nesting
negation position
implication position
restriction/body region
participant variable incidence
predicate occurrence presence
```

반대로 제거 가능:

```text
event variable identity
time variable
Agent/Theme/Experiencer 같은 role label
verb synset label
event predicate lexical identity
```

즉:

> **“무슨 동사였는가”는 버릴 수 있지만 “그 quantifier의 body에 어떤 participant와 연결된 내용 predicate가 존재하는가”는 버리면 안 됩니다.**

G3는 바로 이 마지막 정보까지 제거해서 발생했습니다. 

---

# 6. fail-closed 조건

모든 event structure를 억지로 contract하면 안 됩니다.

예를 들어:

```yaml
PMB_EVENT_INCIDENCE_PROJECTION_V1:

  contract_event_if:
    lexical_event_predicate_present: true
    retained_participant_incidence_min: 1
    same_scope_region: true

  preserve:
    participant_incidence: true
    quantifier_ancestry: true
    scope_region: true

  fail_closed_if:
    - zero_retained_participants
    - event_scope_crossing_ambiguous
    - unresolved_nested_event_attachment
    - contraction_would_change_quantifier_order
    - contraction_would_move_negation
    - contraction_would_move_implication
```

예를 들어 `"Everybody wants to win"`처럼 nested event가 복잡하면 자동으로 salvage한다고 가정하지 않습니다.

안전한 contraction이 안 되면 그 fixture는:

```text
INELIGIBLE
```

입니다.

---

# 7. 새로운 `Projection Signal Gate`

이것이 이번 Q28에서 추가되어야 하는 기계 gate입니다.

현재 Satisfiability는:

```text
gold 모양을 흉내 낸 witness가 존재
```

만 확인해서 G3를 통과시켰습니다.

이제 freeze 전에 추가로 확인합니다.

```text
projection 후 target scope region에
실제 scored content signal이 남아 있는가?
```

예를 들어 `"Everyone smiled"`에서:

### 잘못된 현재 projection

```text
FORALL
  restriction: PRED_SLOT
  body: TRUE
```

→ **signal failure**

### 새 incidence projection

```text
FORALL
  restriction: PRED_SLOT
  body: PRED_SLOT
```

→ signal retained.

---

# 8. 최소 Signal Gate

```yaml
PROJECTION_SIGNAL_V1:

  for_each_target_quantifier:

    require:
      quantifier_type_retained: true
      scope_region_retained: true

    and_at_least_one:
      restriction_scored_content: true
      body_scored_content: true

  reject_if:
    projected_target_content_collapses_to_true: true
```

단 원문 자체가 정말 vacuous한 경우에는 예외를 명시적으로 profile에 넣어야 합니다.

기본은 fail-closed입니다.

---

# 9. Q28.2 — G1 `most beautiful`

## 층 술어 오류: 바로 수정

이건 semantic ambiguity보다 앞선 단순 classification bug입니다.

```text
The most beautiful flowers ...
```

의 `most`는 proportional quantifier가 아닙니다. 

따라서 bare regex:

```regex
\bmost\b
```

는 폐기합니다.

최소한:

```text
the most ADJ ...
```

같은 superlative pattern은 제외해야 합니다.

proportional stratum은:

```text
most of ...
most + plural nominal
```

같은 실제 quantificational pattern만 받도록 다시 census해야 합니다.

---

# 10. 그런데 Q28.2(a)의 cardinal 삭제는 그대로 승인할 수 없음

여기서 중요한 모순이 있습니다.

원래 O1 semantic boundary에는 이미:

```text
cardinal_quantifier
proportional_quantifier
```

가 들어 있습니다.

따라서 Wolfram set 판정:

```text
DeclaredBoundaryContainsCardinal     = True
DeclaredBoundaryContainsProportional = True

DroppingCardinalNarrowsDeclaredBoundary = True
```

입니다.

즉:

> “cardinal constructor가 없으니 cardinal 층을 삭제한다”

는 것은 단순 fixture 정리가 아닙니다.

**declared estimand의 일부를 제거하는 변경**입니다.

---

# 11. 반대로 cardinal constructor 추가는?

이 점에서는 운영 세션의 설명도 조금 수정할 필요가 있습니다.

O1 manifest에 cardinal이 이미 포함되어 있으므로:

```text
cardinal constructor 추가
```

는 declared boundary를 새로 넓히는 것이 아닙니다.

Wolfram 결과:

```text
AddingCardinalConstructorWouldEnlargeDeclaredBoundary = False
```

정확한 해석은:

> **subject language를 확장하지만, 이미 선언된 O1 boundary에 대한 표현 coverage를 복구한다.**

입니다.

즉 D26의 `implies`와 구조적으로 더 가깝습니다.

---

# 12. 다만 현재 G2 fixture가 cardinal constructor 추가의 근거는 아니다

현재 세 문장:

```text
Several children ...
Many a quarrel ...
How many grams ...
```

은 서로 성격도 다릅니다. 

* `several`: vague quantity
* `many`: generalized quantity
* `how many`: interrogative

이들을 하나의 clean cardinal stratum으로 보는 것부터 문제가 있습니다.

따라서 지금 바로 cardinal constructor를 추가하는 것도 권하지 않습니다.

먼저 **true cardinal fixture의 정의와 source encoding**을 다시 정해야 합니다.

예:

```text
three dogs ...
exactly two ...
at least three ...
```

같은 명시적 cardinal 계열을 무엇으로 볼지 먼저 결정해야 합니다.

---

# 13. 따라서 Q28.2 = **(c)**

제가 권하는 것은:

### 즉시

```text
G1 proportional classifier 수정
G2 현재 3 fixture는 cardinal stratum에서 제거
```

### 그리고 둘 중 하나를 명시적으로 선택

#### Full O1 유지

```text
cardinal_quantifier
proportional_quantifier
```

를 계속 semantic boundary에 유지하고,

* genuine fixtures 재조사
* 필요하면 새 constructor/profile
* 별도 qualification

을 진행.

#### Fast O1-v1-core

이번 iteration에서는:

```text
cardinal
proportional
```

을 **명시적으로 deferred**하고 새 boundary 이름으로 재동결.

예:

```text
O1_CORE_V1
```

그러면:

```text
quantifier-negation
simple universal
simple existential
multi-quantifier
```

만 confirmatory scope로 둘 수 있습니다.

---

# 14. 중요한 점

다음처럼 하면 안 됩니다.

```text
cardinal 3건 삭제
→ 다른 층으로 3건 채움
→ 여전히 같은 O1이라고 부름
```

그렇게 하면 fixture count는 20이지만 **측정 boundary가 조용히 달라집니다.**

N=20과 16/20 engineering threshold 자체는 새 version에서도 유지할 수 있습니다.

하지만 결과 이름은 바뀌어야 합니다.

예:

```text
O1-Core ScopeMatch
```

이지:

```text
full O1 boundary accuracy
```

가 아닙니다.

---

# 15. 빠르게 진행한다면

현재까지 이미 상당한 시간을 oracle granularity에 쓰고 있으므로, **빠른 실제 사용 테스트가 목적이라면 저는 O1_CORE_V1을 권합니다.**

즉 당장은:

```text
cardinal/proportional
→ deferred O1-v2
```

로 명시하고,

안정적으로 측정 가능한:

```text
universal
existential
quantifier-negation
multi-quantifier
```

부터 실행합니다.

단 이것은 **공식 boundary amendment**로 기록해야 합니다.

---

# 16. Q28.3 — PMB 자체를 버릴 것인가

## 판정: **아직 아니다**

현재 발견으로 확정된 것은:

```text
old PMB projection = unsuitable
```

이지:

```text
PMB source itself = impossible
```

는 아닙니다.

새 event-incidence projection에는 아직 유효한 중간 지점이 있습니다.

따라서 PMB를:

```yaml
PMB:
  status: REQUALIFICATION_REQUIRED
```

로 둡니다.

---

# 17. PMB 전체 pool을 다시 qualification

현재 15개만 patch하지 않습니다.

다음 새 조건으로 전체 eligible pool을 다시 census합니다.

```text
source filter
↓
scope relevance
↓
new event-incidence projection
↓
Projection Signal Gate
↓
Measurement Satisfiability
↓
material audit
```

그 다음 deterministic selector를 다시 실행합니다.

---

# 18. PMB를 유지할 최소 조건

예를 들어 다음을 만족하는 material만:

```text
target quantifier preserved
participant incidence preserved
nontrivial body/restriction signal retained
no ambiguous nested-event contraction
```

PMB O1 source로 사용합니다.

나머지는 ineligible.

---

# 19. 만약 PMB eligible pool이 부족하면

그때는 Q28.3(b)가 됩니다.

하지만 다음처럼 자동으로:

```text
FOLIO-only
```

로 전환하지 않습니다.

현재 experiment는 두 source authority를 의도적으로 사용해 source-specific artifact와 capability를 분리하려 했습니다.

따라서:

```text
PMB insufficient
→ independent sentence-level source 재조사
```

가 기본입니다.

FOLIO-only로 바꾸려면 별도 governance amendment가 필요합니다.

---

# 20. Q28.4 — Gate C

## 판정: **승인**

이번 사건은 아주 명확한 근거입니다.

해시/구조/SAT gate가 전부 통과해도:

```text
The most beautiful flowers ...
```

를 사람이 보면 바로 proportional 오분류를 발견할 수 있었습니다. 

Wolfram Boolean 모델에서도:

```text
Integrity = PASS
Satisfiability = PASS
MechanicalRunnable = PASS
MaterialAppropriate = FAIL
```

인 상태가 논리적으로 가능합니다.

```text
FormalGatesCanAllPassWhileMaterialAuditFails = True
```

따라서 인간 material gate는 중복이 아닙니다.

---

# 21. 다만 “예상 subject 형태”는 조심

사용자 제안의:

```text
문장
oracle projection
층 배정
예상 subject 형태
```

중 마지막은 그대로 쓰지 않는 편이 좋습니다.

정확한 expected IR을 사람이 적기 시작하면 **새로운 수동 oracle**이 생길 수 있습니다.

대신:

```text
expected scored dimensions
```

를 기록하십시오.

예:

```text
sentence:
  Everyone smiled.

stratum:
  simple_universal

overt_scope_trigger:
  everyone

projected_oracle:
  FORALL
    restriction: content-slot
    body: content-slot

scored_dimensions:
  quantifier_kind: FORALL
  quantifier_depth: 1
  body_content_required: true

dropped_by_projection:
  event_variable: 1
  role_predicate: Agent
  verb_label: smile.v.01
```

이 정도입니다.

---

# 22. Gate C 정본

```yaml
GATE_C_MATERIAL_AUDIT_V1:

  timing:
    before_fixture_freeze: true

  per_fixture_display:
    - source_sentence
    - source_locator
    - assigned_stratum
    - overt_scope_trigger
    - oracle_projected_signature
    - scored_dimensions
    - dropped_structure_summary
    - measurement_satisfiability_status
    - projection_signal_status

  reviewer_questions:

    - Does the assigned stratum match the actual sentence?
    - Does the projected oracle retain the claimed O1 signal?
    - Is any scored structure unsupported by the sentence?
    - Did projection delete the semantic material that makes the sentence nontrivial?
    - Is this fixture actually testing the declared phenomenon?

  reviewer_output:
    - OK
    - BLOCK

  forbidden:
    - hand_author_new_oracle_IR
    - hand_rewrite_gold
    - choose_replacement_based_on_model_outcome
```

---

# 23. Gate 구조를 이제 세 층으로

현재까지의 교훈을 정리하면 상당히 깔끔합니다.

## Gate A — Formal Measurement Validity

```text
integrity
adapter qualification
projection qualification
Measurement Satisfiability
Projection Signal
```

질문:

> 형식적으로 측정 가능한가?

---

## Gate B — Live Control Reachability

실제 cold subject.

질문:

> 단순 정상 사례에서 실제 LLM도 이 계약을 사용할 수 있는가?

---

## Gate C — Material Audit

사람이 실제 fixture를 읽음.

질문:

> 우리가 정말 측정하고 싶은 현상을 이 재료가 담고 있는가?

---

# 24. 순서

권장:

```text
candidate pool
     ↓
Gate A
     ↓
deterministic selection
     ↓
Gate C material audit
     ↓
freeze
     ↓
Gate B live controls
     ↓
main cohort
```

Gate C가 문제를 발견해서 eligibility rule이 바뀌면 **다시 candidate pool부터 deterministic selection**으로 돌아갑니다.

사람이 replacement fixture를 직접 고르지는 않습니다.

---

# 최종 판정

```yaml
D_E2E_v1_28:

  Q28_1:
    decision: D

    reject:
      event_formula_to_participant_formula_rewrite: true

    introduce:
      profile: PMB_EVENT_INCIDENCE_PROJECTION_V1

    semantics:
      logical_equivalence_claim: false
      measurement_projection_only: true

    contract:
      event_predicate:
        retain_as_lexical_truth: false
        retain_as_unlabeled_content_slot: true

      role_edges:
        use_for_participant_incidence: true
        role_label_scored: false

      preserve:
        - quantifier_ancestry
        - negation_position
        - implication_position
        - restriction_body_region
        - participant_incidence
        - predicate_occurrence_presence

      fail_closed_on:
        - zero_participant_incidence
        - ambiguous_nested_event_contraction
        - scope_crossing
        - quantifier_reordering_required

    new_gate:
      ProjectionSignalGate: required

  Q28_2:
    decision: C

    G1:
      proportional_classifier:
        bare_most_regex: forbidden
        superlative_most: exclude
        quantificational_most_only: true

    G2:
      current_cardinal_fixtures:
        retain: false

      silent_reallocation:
        allowed: false

      reason:
        cardinal_is_already_in_declared_O1_boundary: true

      options:
        full_O1:
          genuine_cardinal_source_required: true
          subject_representation_support_required: true

        fast_O1_core:
          explicit_boundary_amendment: required
          cardinal: deferred
          proportional_if_no_valid_fixture: deferred

  Q28_3:
    PMB:
      final_status: REQUALIFICATION_REQUIRED

      retain_if:
        new_projection_pass: true
        projection_signal_pass: true
        measurement_satisfiable: true
        material_audit_pass: true

      recensus_full_pool: required

      if_insufficient:
        automatic_FOLIO_only: false
        new_independent_source_or_governance_amendment: required

  Q28_4:
    Gate_C:
      approved: true
      type: human_material_audit
      prefreeze: true

    exact_expected_subject_IR:
      human_authored: forbidden

    review_instead:
      - actual_sentence
      - assigned_stratum
      - overt_scope_trigger
      - projected_oracle_signature
      - retained_scored_dimensions
      - dropped_information
      - projection_signal_status

  cohort:
    dispatch: remains_blocked
```

## 핵심

이번 Q28의 중요한 교훈은:

> **“nuisance를 제거하는 projection”도 자체적으로 measurement destruction을 일으킬 수 있다.**

따라서 앞으로는 단순히:

```text
projection succeeds
```

가 아니라:

```text
projection succeeds
AND
target signal survives
```

를 확인해야 합니다.

PMB event semantics는 아직 버릴 필요는 없습니다. 하지만 `smile(e)+Agent(e,x)`를 `smile(x)`라는 새 논리적 gold로 바꾸는 대신, **event-role graph에서 “이 quantified participant가 body의 한 내용 predicate에 참여한다”라는 측정 신호만 구조적으로 contract**하는 것이 현재 authority boundary를 가장 잘 보존합니다. 
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | `∃e(Smile(e)∧Agent(e,x)) ≢ Smile(x)`, 반례 16 | 2원소 도메인 전조합(S 4 × A 16 × x 2 = 128) 열거 | **결론 CONFIRMED (비동치)** / **반례 수 미재현** — 실측 40/128, x 고정 시 20/64. 판정의 인코딩 파라미터가 명시되지 않아 16을 재현하지 못했다. 판정의 논거는 "비동치"이며 그것은 확정됐다 |
| V2 | event-incidence projection이 oracle↔subject를 정합시키면서 scope mutation은 구별 | 판정 §3-5 규칙의 시제품 구현으로 실측 | **CONFIRMED** — `∀x∃e(smile(e)∧Agent(e,x))` 투영 `∀(□;□)` = subject `∀x(everyone(x)→smiled(x))` 투영 `∀(□;□)` → **pass**; `∀→∃` 변이는 `∃(□;□)` → **fail** |
| V3 | cardinal·proportional이 **이미** O1 declared boundary에 포함 | 저장소 실물 확인 | **CONFIRMED** — `semantic_boundary: [quantifier_scope, generalized_quantifier, cardinal_quantifier, proportional_quantifier, multi_quantifier_scope]` (`docs/DESIGN_REQUEST_o1_oracle_unit_and_coverage.md:38-40`). 운영 세션의 "기수 층 삭제" 권고는 boundary 축소를 조용히 하는 것이었다 — 기각이 정당하다 |
| V4 | 형식 게이트 전부 통과 + 재료 감사 실패가 동시 가능 | 이 세션의 G1(최상급 오분류)이 실물 반례 | **CONFIRMED (경험적)** |

주의 기록 (적용 시 구속 해석):

1. **반례 수 미재현은 첫 사례다.** D-24(2·56·104)·D-25·D-26·D-27(5)에서는
   판정의 수치를 매번 정확히 재현했다. 이번 16은 재현 못했고 결론만
   일치한다 — 향후 판정 인용 시 "반례 16"을 우리 기록의 실측값으로
   제시하지 않는다(실측: 40/128, 20/64).
2. **P14 3회 연속**: Q26.3·Q27.1에 이어 Q28.2에서도 운영 세션 권고가
   기각됐다. 이번 기각 근거는 **우리 자신의 선행 기록**(declared boundary
   목록)이었고, 상신 전 그 목록을 확인하지 않은 것이 원인이다. 규율 추가:
   **estimand·boundary에 영향을 주는 제안은 상신 전 O1 manifest의 선언
   목록을 인용해 영향 범위를 명시한다.**
3. **Q28.2의 두 갈래는 사용자 결정 사항이다** — full O1 유지(기수 source
   재조사) vs `O1_CORE_V1` 재동결(기수·비례 deferred). 판정자는 빠른
   실사용 테스트 목적이면 후자를 권고했고, 그 경우 결과 표기가
   "O1-Core ScopeMatch"로 바뀐다(범위 축소의 정직한 표기).
4. **Gate C의 금지 조항**: 사람이 expected IR을 적으면 새 수동 oracle이
   된다 — 표시 항목과 OK/BLOCK만 허용된다.

수신 텍스트의 sha256 (BEGIN 다음 개행 ~ END 직전, UTF-8):
`VERBATIM_SHA256: d364e4721d4d606e9f01132b42e5846b63c7bf98fd5480bc87d6a2e9f938ed6b`
