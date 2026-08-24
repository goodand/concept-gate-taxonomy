# DESIGN DECISION — D-E2E-v1-33-V (D-33의 주장 유형 확정)

- 수신: 2026-08-24 · 발신: 외부 설계 담당(저장소 접근 없음, Wolfram 검증 명시)
- 사슬 항법: 이전 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · **D-33-V** · 다음 [[DESIGN_REQUEST_referential_existential_qualification|Q34]] · 색인 [[RULING_CHAIN_INDEX]]
- 성격: **D-33을 뒤집지 않는 재검증.** 핵심 결론(`B_STAR` · `insufficient_evidence` ·
  `dispatch: blocked` · `operational_patch: forbidden`)은 유지되고, 우리가
  `CONFIRMED`로 적은 것들의 **유형을 갈랐다** — 논리적 확인 / corpus 실사 /
  의미론 미확정이 섞여 있었다.
- `VERBATIM_SHA256: 2ed52e4be7b1fe4e93252dba5b43253770643be29404a699062da753447923fd`
  (범위: BEGIN 다음 개행 ~ END 직전 개행 **제외** — D-30 이후 규약)

## 우리 문서에 요구된 정정 (전부 적용했다)

| 곳 | 우리가 쓴 것 | 정정 |
|---|---|---|
| D-33 §B.3 제목 | "경계는 **synset으로 그을 수 없다**" | "**이 gold corpus에서는** synset alone이 원하는 분류를 식별하지 못한다" — 의미론 주장이 아니라 corpus 실사로 범위를 좁힌다 |
| D-33 §B.4 · 회고 §18.4 | "계측기가 못 만들어진 것이 **재료의 성질**이다" | "**현재 시도한 proxy들이** 불충분·불안정하다" — 4회 실패를 "원리적 불가"로 확대하면 안 된다 |
| `B*`의 강도 | "referential ∃는 measurand 밖이라는 **방향이 맞다**" | 확정된 것은 그보다 약하다: **encoding과 scope가 식별 불가**라는 것이고, projection의 **semantic boundary는 미확정**이다 |

## 이 재검증이 강화한 것 — V4b는 **non-injective mapping**이다

우리가 "두 원인이 같은 진단 값을 낸다"고만 적은 것을, 판정이 구조로 다시
적었다: 서로 다른 latent cause A(인코딩 불일치)·B(진짜 scope 오류)가 같은
observable(`scope_signature_v2 = fail`)로 사상되므로 관측 함수가
**non-injective**다. 따라서

```text
Y = O1ScopeMatch = f(scope ability, representation convention compatibility)
```

이고, 원하는 것은 `Y_scope = f(scope ability)`다. 두 항을 분리할 수 없으면
**Y를 scope ability의 순수한 measurand라고 선언할 수 없다** — 이것이 (a)를
기각하는 가장 강한 논거다.

## 확정된 주장 유형 (판정의 표 그대로)

| 주장 | 유형 |
|---|---|
| `∃x[P∧B]`를 일반적으로 `B(x)`로 지울 수 없다 | **Wolfram 확인** |
| 현재 signature가 encoding mismatch와 scope 오류를 구별하지 못한다 | **Wolfram + adversarial 확인** |
| `him`은 non-quantificational, `someone`은 quantificational이다 | **Wolfram으로 확정 불가** |
| PMB gold의 특정 binder가 referential participant binder라는 것 | **gold annotation 의존** |
| control PASS가 Q33을 인증하지 않는다 | **논리적으로 확인** |
| 따라서 즉시 normalization하면 안 된다 | **설계 inference** |

우리 §B.10이 의미론 주장을 UNVERIFIABLE로 보고한 것을 판정이 **그대로 유지하라**고
했다 — "오히려 이 문장이 D-33의 과학적 엄밀성을 높인다".

---

# A. 재검증 verbatim

<!-- VERBATIM-BEGIN -->
검증했습니다. **이번 D-33은 이전 답변보다 한 단계 더 강하게 방어할 수 있습니다.** 다만 문서 안에서 `CONFIRMED`라고 부른 것 중 일부는 논리적으로 확인된 것이고, 일부는 **gold 인코딩에 대한 실사 결과**이지 의미론적 사실의 증명은 아닙니다.

## 최종 판정

**D-E2E-v1-33의 핵심 결론은 유지해도 됩니다.**

특히:

```yaml
decision: B_STAR
status: insufficient_evidence
dispatch: blocked
operational_patch: forbidden
```

은 현재 증거에 가장 잘 맞습니다.

다만 다음 두 표현은 구분해서 기록하는 것이 좋습니다.

| 주장                                                                    | 판정                                  |
| --------------------------------------------------------------------- | ----------------------------------- |
| `∃x[P(x) ∧ B(x)]`를 일반적으로 `B(x)`로 지울 수 없다                              | **Wolfram 확인**                      |
| 현재 signature가 encoding mismatch와 실제 scope 오류를 구별하지 못한다                | **Wolfram + 제시된 adversarial 결과 확인** |
| `him`은 semantic상 non-quantificational이고 `someone`은 quantificational이다 | **Wolfram으로 확정 불가**                 |
| PMB gold에서 특정 binder가 referential participant binder라는 것              | **gold/annotation에 의존**             |
| 현재 control PASS가 Q33을 인증하지 않는다                                        | **논리적으로 확인**                        |
| 따라서 즉시 normalization하면 안 된다                                           | **설계 inference**                    |

---

# 1. 가장 중요한 Wolfram 검증

문서의 이 문장:

> `∃x[P(x)∧B(x)] ≢ B(x)`

는 정확합니다.

유한 도메인에서 실제 반례를 구성하면:

```text
P = {False, False}
B = {False, True}
```

일 때

```text
∃x(P(x) ∧ B(x)) = False
```

지만

```text
B(x)
```

는 어떤 x에서는 `True`입니다.

즉 **제한식을 단순히 제거해서 entity 표현으로 바꾸는 것은 논리적 동치 변환이 아닙니다.**

따라서 D-33의 다음 주장은 유지 가능합니다.

> "`entity`와 participant-∃가 같은 의미이므로 normalization한다"는 것은 논리적 equivalence에 의해 정당화되지 않는다.

**source type: literature-independent / Wolfram-grounded**

---

# 2. 그런데 이 결과가 `him ≠ someone`을 증명하는 것은 아니다

여기가 문서에서 가장 조심해야 할 부분입니다.

Wolfram은 다음을 보여줄 수 있습니다.

```text
∃x[P(x) ∧ B(x)]
```

와

```text
B(c)
```

가 일반적으로 동치가 아니라는 것.

그러나 이것만으로:

```text
him = referential
someone = quantificational
```

이라는 자연언어 의미론을 증명할 수는 없습니다.

그것은 **gold annotation과 언어학적 이론에 대한 별도 주장**입니다.

따라서 B.10의:

> "`someone`과 `him`의 quantificational force가 다르다는 의미론 주장은 우리 도구로 검증하지 못했다."

는 **그대로 유지하는 것이 맞습니다.**

오히려 이 문장이 D-33의 과학적 엄밀성을 높입니다.

**source type: model inference / insufficient_evidence for semantic proof**

---

# 3. V4b는 상당히 강한 검증이다

이 부분은 특히 중요합니다.

두 latent cause:

```text
A = representation/encoding mismatch
B = genuine scope error
```

가 있고 관측값이 둘 다:

```text
scope_signature_v2 = fail
```

이라면 mapping은:

```text
A ──┐
    ├──> FAIL
B ──┘
```

입니다.

즉 관측 함수가 이 두 원인을 구별하지 못합니다.

Wolfram에서도 이 mapping이 **non-injective**임을 확인했습니다.

따라서:

> 현재 `scope_signature_v2`만으로는 "왜 실패했는가"를 causal identification할 수 없다.

는 주장은 상당히 강하게 유지할 수 있습니다.

이것은 단순히 “두 사례가 비슷해 보인다”가 아니라 **동일한 observable에 서로 다른 latent cause가 mapping되는 구조**입니다.

**source type: Wolfram-grounded + prompt-given experiment**

---

# 4. 이것은 Q33의 핵심을 정확히 찌른다

따라서 현재 측정값을

```text
Y = O1ScopeMatch
```

라고 하면 실제로는:

```text
Y = f(
      scope ability,
      representation convention compatibility
    )
```

일 가능성이 있습니다.

원래 원했던 것은:

```text
Y_scope = f(scope ability)
```

입니다.

현재 데이터만으로 두 항을 분리할 수 없다면:

```text
Y
```

를 `scope ability`의 순수한 measurand라고 선언할 수 없습니다.

이것이 D-33에서 **(a)를 기각하는 가장 강한 논거**입니다.

---

# 5. `control excludes X → PASS says nothing about X`도 정확하다

이 부분은 논리적으로 아주 단순합니다.

control eligibility를:

```text
Eligible(x) = ¬X(x)
```

라고 하고 control이:

```text
PASS
```

했다면, 관측한 것은

```text
x ∈ ¬X
```

에서의 성능입니다.

그것으로:

```text
x ∈ X
```

에서의 성능을 추론할 수는 없습니다.

즉:

```text
control PASS
        ↓
X에 대한 인증
```

은 성립하지 않습니다.

따라서 D-27 control이 Q33을 인증한다고 해석하는 것은 잘못입니다.

**source type: Wolfram-independent logical inference**

---

# 6. `person.n.01` / `entity.n.01` 실사는 매우 중요하지만 의미론의 증명은 아님

B.3의 결과:

```text
person.n.01
 ├─ Everyone
 ├─ I
 └─ passengers
```

그리고:

```text
entity.n.01
 ├─ everything
 └─ some
```

라는 관찰은 **synset을 classification boundary로 사용할 수 없다는 매우 강한 실사 결과**입니다.

즉:

```text
synset → referential/quantificational class
```

라는 단순 rule은 사용할 수 없습니다.

하지만 이것도:

> `I`가 의미론적으로 referential이다.

를 증명하는 것은 아닙니다.

정확한 표현은:

> **“이 gold corpus에서는 synset alone이 원하는 분류를 식별하지 못한다.”**

입니다.

이렇게 쓰는 것이 좋습니다.

**source type: prompt-given corpus inspection**

---

# 7. 네 번의 classifier 실패는 설계상 의미가 있다

B.4의 네 번 실패는 단순한 구현 실패 목록이 아닙니다.

특히 순서가:

```text
1. 양화 대명사 혼입
2. 부정관사 ∃ 혼입
3. ANSI escape 오염
4. 문두 대문자 → 고유명 오분류
```

였다면 현재 증거는 다음을 보여줍니다.

> **현재 사용 가능한 표면적/구문적 proxy만으로 referential participant의 경계를 안정적으로 추출할 수 있다는 증거가 없다.**

이것은 `REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1`을 바로 구현하는 것을 막는 좋은 이유입니다.

다만 **“4번 실패했으므로 원리적으로 분류 불가능하다”**라고 확대하면 안 됩니다.

정확히는:

```text
현재 시도한 proxy들:
    insufficient / unstable
```

입니다.

---

# 8. 그래서 `B*`의 정확한 의미

여기서 제가 한 가지 문구를 수정 권고합니다.

`B*`를:

> “referential binder는 measurand 밖이라는 방향이 맞다”

라고 너무 강하게 쓰면 안 됩니다.

현재 증거가 확정한 것은 그보다 약합니다.

더 정확한 것은:

```yaml
B_STAR:

  observed_problem:
    encoding_and_scope_are_not_identifiable:
      true

  possible_resolution:
    referential_binder_projection:
      plausible: true

  semantic_status:
    referential_binder_definition:
      unresolved: true

  implementation:
    forbidden_until_qualification: true
```

즉 **projection의 필요 가능성은 강하지만 projection의 semantic boundary는 아직 확정되지 않았습니다.**

이 차이가 중요합니다.

---

# 9. 따라서 D-33 → Q34 연결은 올바르다

현재 사슬은:

```text
D-31
  ↓
D-32
  ↓
D-33
  ↓
Q34: REFERENTIAL_EXISTENTIAL_QUALIFICATION
  ↓
?
  ↓
O1_SCOPE_PROJECTION_V3
```

가 되어야 합니다.

반대로:

```text
D-33
  ↓
곧바로 projection rule 구현
```

으로 가면 **D-33 자체가 금지한 operational patch를 실행하게 됩니다.**

---

# 최종적으로 제가 문서에 남길 판정

```yaml
D-E2E-v1-33:
  status: accepted_as_design_ruling

  core_claim:
    current_scope_signature_is_not_purely_scope_identifying: true

  logical_claims:
    restricted_existential_not_reducible_to_entity:
      status: wolfram_confirmed

    current_signature_non_identifies_encoding_vs_scope_cause:
      status: wolfram_plus_adversarial_confirmed

  semantic_claims:
    referential_vs_quantificational_force:
      status: insufficient_evidence

  corpus_claims:
    synset_alone_identifies_referential_class:
      status: refuted_by_supplied_corpus_inspection

  control:
    Q33_certified_by_control_pass:
      status: false

  decision:
    a: rejected
    b: directionally_plausible_but_not_implementable
    c: rejected
    d: rejected
    b_star: accepted_as_interim_design_direction

  dispatch: blocked

  operational_patch: forbidden

  next_question: Q34
```

**핵심적으로, 이번 검증은 D-33을 뒤집지 않았습니다. 오히려 `B*`가 왜 필요한지 더 명확하게 만들었습니다.** 다만 `B*`는 “referential ∃가 실제로 measurand 밖이다”라는 결론이 아니라, **현재 measurand가 encoding convention과 scope ability를 분리하지 못하므로 그 경계를 독립적으로 정의하기 전에는 projection을 구현해서는 안 된다는 판정**으로 동결하는 것이 가장 엄밀합니다.
<!-- VERBATIM-END -->
