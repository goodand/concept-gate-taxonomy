# DESIGN DECISION — D-E2E-v1-33 (지시 표현의 참여자 ∃가 measurand인가)

- 수신: 2026-08-24 · 발신: 외부 설계 담당(저장소 접근 없음)
- 요청서: [[DESIGN_REQUEST_referential_participant_quantification|Q33]]
- 사슬 항법: 이전 [[DESIGN_DECISION_q_rstr_body_position|D-32-C]] · **D-33** · 다음 [[DESIGN_DECISION_d33_claim_status|D-33-V(재검증)]] → [[DESIGN_REQUEST_referential_existential_qualification|Q34]] · 색인 [[RULING_CHAIN_INDEX]]
- `VERBATIM_SHA256: e618857ba9900f2cb1072deb6d5b9d62c701d9c886f3bc48796369f61cbcb42a`
  (범위: `<!-- VERBATIM-BEGIN -->` 다음 개행부터 `<!-- VERBATIM-END -->` 직전 개행 **제외**까지 — D-30~D-32-C와 같은 규약)

## 판정 요약 (우리 요약 — 정본은 §A)

- **선택지 네 개 전부 그대로는 기각.** (a) 기각(인코딩 관례로 scope measurand
  오염) · (b) **방향은 인정, 즉시 구현 금지**(referential ∃의 경계가 미정의) ·
  (c) 기각(이론적 근거 없이 층별로 measurand를 바꿈) · (d) 기각(사전등록 모집단
  변경 + 측정 곤란 사례를 골라 제거).
- **권고는 `(b*)`** — 원래 선택지에 없던 것. **강도 주의**(D-33-V §8): 확정된
  것은 "referential ∃가 measurand 밖이다"가 아니라 **"encoding과 scope가 현재
  측정으로 식별 불가"**이고, projection의 **semantic boundary는 미확정**이다: 먼저
  `REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1`으로 "어떤 ∃가 순수 referential
  participant binder인가"를 독립 정의하고, 그 qualification 통과 후에만
  `O1_SCOPE_PROJECTION_V3`에서 referential binder를 measurand 밖으로 투영한다.
- **현재 상태 = `insufficient_evidence`.** `dispatch: blocked`,
  `operational_patch: forbidden`.
- 핵심 논거 두 개가 **양방향으로 우리를 막는다**: `∃x[P(x)∧B(x)] ≢ B(x)`이므로
  "같은 의미니까 정규화한다"는 정당화는 불가하고, 동시에 `someone`·`something`
  같은 **진짜 양화 ∃를 접으면 scope 연산자를 제거**하므로 "participant니까
  비-scope"도 불가하다. 즉 D-32와 같은 오류를 새 층에서 반복하지 말라는 것이다.
- 우리 요청서의 §9(control 5/5는 Q33을 인증하지 못한다)는 **정확하다고 확인**됐다:
  "control eligibility excludes X → control PASS therefore says nothing about X".

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
# Q33 판정

**결론: 현재 증거만으로 (b)를 즉시 채택하면 안 됩니다.**

제가 Wolfram으로 논리 구조를 따로 검증한 결과, 가장 중요한 구분은 이것입니다.

> **“참여자 ∃를 entity와 동일하게 취급하는 것”은 논리적 동치가 아니라, O1이 scope-only measurand라는 전제 아래 도입할 수 있는 별도의 measurement projection 규칙입니다.**

Wolfram 결과에서도 일반적으로

```text
∃x [P(x) ∧ B(x)]
```

와

```text
B(x)
```

를 논리적으로 동일하다고 할 수 없었습니다.

따라서 **“entity와 participant-∃가 같은 의미니까 normalization한다”**라고 정당화하면 안 됩니다.

---

## 1. 그러나 (a)도 그대로 받아들이면 안 됨

(a)의 문제는 더 명확합니다.

현재처럼

```text
gold:
  ∃(him, B)

subject:
  entity("him")
```

을 그대로 비교하면:

```text
oracle binder count = 2
subject binder count = 1
```

이므로 mismatch가 발생합니다.

그런데 그 차이가

```text
scope reasoning failure
```

인지

```text
representation convention mismatch
```

인지 현재 O1 signature만으로는 분리할 수 없습니다.

따라서 이것을 무조건 오답으로 세면:

> **O1ScopeMatch = scope compilation ability + PMB representation-convention matching**

이 됩니다.

이는 현재 선언된 **scope-only measurand**와 불일치합니다.

**판정: literature-independent model inference + Wolfram logical analysis**

---

# 2. 그렇다고 participant ∃를 전부 제거하면 더 위험함

여기서 Q33의 핵심입니다.

다음 두 종류를 구분해야 합니다.

### Referential existential

```text
∃x [entity/person/name-like(x) ∧ B(x)]
```

실제로 특정 참여자를 도입하기 위한 표현.

### Quantificational existential

```text
∃x [student(x) ∧ B(x)]
```

또는

```text
someone
something
some passenger
```

처럼 **양화 자체가 의미의 일부인 ∃**.

후자를 entity로 접어버리면 실제 scope operator를 제거합니다.

따라서:

```text
participant ∃ → 무조건 제거
```

는 D-32와 동일한 오류를 새 층에서 반복합니다.

**판정: Wolfram-grounded logical distinction**

---

# 3. Q33에서 가장 중요한 것은 “지시 표현”이라는 semantic criterion

현재 요청서에는:

```text
male.n.02
person.n.01
entity.n.01
Name
pronoun
demonstrative
```

등이 잠재적으로 섞여 있습니다.

그런데 이것들을 단순히

> “participant existential이므로 비-scope”

라고 묶으면 새로운 문제가 생깁니다.

예를 들어:

```text
someone
```

과

```text
him
```

은 모두 사람을 가리킬 수 있지만 **quantificational force가 동일하지 않습니다.**

마찬가지로:

```text
the man
```

같은 definite description을 단순히 entity로 취급할지 여부도 별도 semantic ruling이 필요합니다.

따라서 현재 상태에서는

```yaml
participant_existential:
  normalize_to_entity: true
```

라는 규칙을 바로 넣으면 **경계가 임의적**입니다.

**판정: model inference**

---

# 4. 따라서 제가 권고하는 답은 `(b*)`

원래 선택지에는 없지만, 가장 안전한 것은:

> **(b)의 방향은 인정하되, normalization rule을 지금 즉시 만들지 않는다.**

즉:

```text
Q33
 ↓
“이 mismatch는 scope measurand에 포함시키지 않아야 할 가능성이 높다”
 ↓
그러나
 ↓
“어떤 ∃가 순수 referential participant ∃인가?”
를 먼저 독립적으로 정의
 ↓
qualification
 ↓
projection V3
```

입니다.

현재는:

```yaml
Q33:
  immediate_decision: insufficient_evidence
  dispatch: BLOCKED
  operational_patch: forbidden
```

이 맞습니다.

---

# 5. 필요한 것은 `REFERENTIAL_EXISTENTIAL` qualification

제가 추천하는 최소 contract는 다음입니다.

```yaml
REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1:

  may_normalize_only_if:

    referent_introduction:
      true

    quantificational_force:
      false

    scope_bearing_role:
      false

    representation:
      participant_reference

    semantic_class:
      independently_identified

  normalize:
    existential_binder: false
    referential_incidence: preserve

  preserve:
    genuine_quantificational_exists: true
    nested_scope: true
    binder_relationships: true
```

핵심은:

```text
∃를 제거한다
```

가 아니라

```text
referential ∃의 binder-creation을
O1 scope measurand에서 projection한다
```

입니다.

이 차이가 중요합니다.

---

# 6. `male.n.02` 하나만 보고 제거하면 안 됨

Q33의 실측에서:

```text
male.n.02 → participant binder
```

가 나타났다고 해서

```text
male.n.02 = non-scopal
```

이라는 일반 규칙을 만들 수는 없습니다.

그것은 현재 gold encoding에 대한 관찰이지 semantic theorem이 아닙니다.

같은 방식으로:

```text
person.n.01
entity.n.01
Name
pronoun
demonstrative
```

도 각각 qualification이 필요합니다.

특히 **고유명/대명사/지시사**와 **명사구 기반 양화 표현**을 같은 규칙으로 처리하면 안 됩니다.

---

# 7. Q33과 D-32의 관계

D-32:

```text
non-scope predicate content
        ↓
opaque
```

Q33:

```text
referential participant binder
        ↓
?
```

입니다.

즉 Q33은 **D-32의 extension이 아닙니다.**

다만 D-32의 원칙을 적용하면 방향은 분명합니다.

> scope-only measurand가 아닌 구조는 제거할 수 있지만, 그것이 scope-bearing이라는 것을 먼저 반증해야 한다.

따라서 Q33에서 **“∃니까 scope-bearing”**이라고 보는 것도 너무 강하고,

**“participant니까 non-scope”**라고 보는 것도 너무 강합니다.

**판정: prompt-given + model inference**

---

# 8. 15건 표는 중요한 증거지만, normalization의 증명은 아님

제시한 15건은 상당히 유용합니다.

특히:

```text
Tom bought Mary some chocolates.
```

에서

```text
oracle: ∃ · ∃ · ∃
subject: entity(Tom) · entity(Mary) · ∃(chocolates)
```

가 되는 것은 **scope mismatch와 encoding mismatch를 실제로 분리해야 한다는 강한 동기**입니다.

하지만 이것으로

```text
Tom/Mary의 ∃는 반드시 measurand 밖이다
```

까지 증명되지는 않습니다.

따라서 이 표는:

```text
problem existence:      supported
problem recurrence:     supported
problem classification: unresolved
```

로 읽는 것이 정확합니다.

**판정: prompt-given**

---

# 9. control 5/5는 Q33을 인증하지 못함

이 부분의 판단은 요청서가 정확합니다.

control selector가:

```python
has_excluded_participant(...)
```

로 participant-containing sentence를 제외한다면,

```text
5/5 control PASS
```

은 Q33에 대한 증거가 아닙니다.

오히려 논리적으로:

```text
control eligibility
    excludes X

control PASS
    therefore says nothing about X
```

입니다.

따라서:

> **control silence는 Q33의 안전성을 인증하지 않습니다.**

D-27의 control contract와 Q33의 in-N measurement contract를 분리해야 합니다.

**판정: prompt-given / model inference**

---

# 10. 재료를 빼는 `(d)`는 가장 나쁜 해결책에 가까움

현재:

```text
N = 20
PASS ≥ 16
```

이 동결되어 있다면 participant fixture를 제거하는 것은 단순한 fixture cleanup이 아닙니다.

```text
population definition
        ↓
changed
```

입니다.

그리고 문제의 표현이 여러 층에 퍼져 있으므로, 측정하기 어려운 사례를 제거하는 방식이 됩니다.

따라서 현재는:

**(d) 기각.**

**판정: prompt-given contract + model inference**

---

# 최종 판정

```yaml
D_E2E_v1_33:

  question:
    participant_existential_vs_entity_encoding:
      status: MEASUREMENT_CONTRACT_UNRESOLVED

  (a):
    reject_as_final:
      reason: contaminates_scope_measurand_with_encoding_convention

  (b):
    directionally_supported: true
    immediate_implementation: false
    reason: referential_existential_boundary_is_undefined

  (c):
    reject:
      reason: layer_specific_scoring_changes_measurand_without_theoretical_basis

  (d):
    reject:
      reason: changes_preregistered_population_and_selects_on_measurement_problem

  recommended:
    decision: B_STAR
    next_step:
      define_REFERENTIAL_EXISTENTIAL_qualification
      qualify_before_projection_change
      then_issue_O1_SCOPE_PROJECTION_V3

  dispatch:
    blocked: true

  operational_patch:
    forbidden: true
```

## 한 문장으로 정리

**Q33은 “participant ∃를 entity와 같게 만들어라”가 아니라, 먼저 “어떤 ∃가 순수한 referential participant binder이고 어떤 ∃가 실제 양화 범위를 만드는가”를 독립적인 qualification rule로 정의해야 하는 문제입니다.**

그리고 그 qualification이 통과된 뒤에만 `O1_SCOPE_PROJECTION_V3`에서 referential participant binder를 measurand 밖으로 projection하는 것이 과학적으로 방어 가능한 순서입니다.

**현재는 `insufficient_evidence`가 정확한 상태입니다.**
<!-- VERBATIM-END -->

---

# B. 우리 수신 검증 (2026-08-24)

설계 → **설계 적대검증** → 검증 → 기록 순서로 했다. 정본을 **먼저 저장**한 뒤
검증을 띄웠다 — D-32에서 정본 없이 적대검증을 띄워 4건 중 3건이 오조준된
이력(G123) 때문이다. 이번엔 오조준 0건이다.

## B.1 설계 적대검증이 내 설계를 4곳에서 막았다 (3건 수용·1건 반증)

| # | 지적 | lead 판정 |
|---|---|---|
| 1 | V2가 **measurand drift**다 — 판정 §3은 "quantificational force"라는 **의미론** 주장인데 V2는 gold **인코딩**을 재고 그것을 그 주장의 검증이라 이름 붙였다 | **수용.** V2를 "의미론 주장의 검증"이 아니라 **재료 실사**(가를 신호를 gold가 기록하는가)로 다시 규정했다. 의미론 주장 자체는 우리 도구로 검증 불가이고 그렇게 보고한다 |
| 2 | V4가 순환이다 — 판정 §8이 `classification: unresolved`인데 V4는 다층 분포를 분류 해결로 읽는다 | **반증.** §8은 15건 표의 **증거력**에 대한 것이고 V4가 겨눈 것은 **§10의 (d) 기각 근거**("문제의 표현이 여러 층에 퍼져 있으므로")다. 서로 다른 주장이라 순환이 아니다. 다만 지적에서 파생된 **V4b는 신규 항으로 채택**했다 |
| 3 | V3의 "각 조건 1건씩"은 도구가 겨눠진다는 것만 보이고 15건 적용 가능성은 미검증 | **수용.** 표본을 버리고 전수로 바꿨다 |
| 4 | V3이 **정의/자동화 순서를 뒤집는다** — 판정은 "먼저 의미론적으로 정의"인데 V3은 "우리 도구가 판정 가능한가"를 묻는다. 도구 능력이 의미 경계를 정하게 된다 | **수용.** 이것이 가장 날카로운 지적이다. `operational_patch: forbidden`이 새는 경로가 정확히 그것이다. V3을 "무엇을 결정해야 하는가"가 아니라 "gold가 어떤 증거를 **기록하는가**"의 실사로 축소했다 |

함정 절도 정정했다: 첫 항이 표본 일반화(P16류)를 경고했는데 V2에서 실제로
일어나는 것은 **measurand 표류(P22)** 다. 경고가 다른 실패를 가리키고 있었다.

## B.2 V1 — 판정 서두의 논리 주장: **CONFIRMED** (유한 모형 전수)

Q33에 실제로 해당하는 두 형태를 도메인 2에서 전수 확인했다.

| 비교 | 반례 | 예 |
|---|---:|---|
| `∃x[P(x)∧B(x)]` vs `∃x[B(x)]` (제한식 제거) | **5건** | `P=(F,F) B=(F,T)` → 좌 F, 우 T |
| `∃x[P(x)∧B(x)]` vs `B(c)` (entity 치환) | **10건** | `P=(F,F) B=(F,T) c=1` → 좌 F, 우 T |

둘 다 동치가 아니다 → "같은 의미니까 정규화한다"는 정당화는 성립하지 않는다.

**이 항의 REFUTE 경로**: 반례 0건이면 판정의 (b) 즉시구현 금지 근거가 약해졌을
것이다. 그렇게 되지 않았다 — 즉 이 검증은 판정에 유리한 방향으로만 설계되지
않았다.

## B.3 V2(수리판) — 재료 실사: **이 corpus에서는** synset alone이 부류를 식별하지 못한다

PMB fixture 20건(in-N 15 + control 5, 중복 제거) 개념 노드 **93개 전수**.

gold는 각 개념 노드에 **표면 토큰을 주석으로 기록**한다(`male.n.02 % him [18-22]`).
그래서 증거는 원리적으로 존재한다. 그러나 **synset만으로는 부류를 가를 수 없다**:

| synset | 양화 용법 | 지시 용법 | 보통명사 용법 |
|---|---|---|---|
| `person.n.01` | `Everyone` · `Some` · `Nobody` | `I` · `you` | `passengers` |
| `entity.n.01` | `everything` · `some` | — | — |

`person.n.01` 하나가 세 부류에 걸친다. 이 결론은 아래 계측기 결함과 **무관하게
성립한다** — `Everyone`/`I`/`passengers`는 모호하지 않은 사례다.

**주장의 범위**(D-33-V §6이 요구한 정정): 이것은 "이 gold corpus에서 synset
alone이 원하는 분류를 식별하지 못한다"는 **corpus 실사**다. `I`가 의미론적으로
referential이라는 **증명이 아니다** — 그 판단은 gold annotation과 언어학 이론에
대한 별개 주장이다.

판정 §6("`male.n.02` 하나만 보고 제거하면 안 된다")이 **실측으로 확인**됐다.

## B.4 계측기를 세 번 만들었고 세 번 다르게 틀렸다 — 이것이 결과다

경계 규칙을 만들려는 시도가 아니라 규모를 재려는 시도였는데도 그랬다.

| 시도 | 실패 형태 |
|---|---|
| 1차(Q33 상신 전) | 양화 대명사(`everyone`, 양측이 모두 양화)와 지시 표현(`him`, oracle만 양화)을 **섞었다** |
| 2차 | 부정관사 ∃가 혼입했다 |
| 3차(이번) | SBN의 **ANSI 이스케이프**가 표면 토큰을 오염시켰다(`person.n.01 ← '\x1b'` ×7) |
| 4차(이번) | ANSI를 고치자 **문두 대문자**를 고유명으로 오분류했다(`'Not everyone'` → referential). `has_excluded_participant`에 이미 문서화된 **같은 누출**이다 |

그래서 분류기 제작을 **중단했다**. 계속하면 그것이 곧 판정이 금지한
`operational_patch`다 — 우리 손으로 경계를 그으면, 도구가 정할 수 없는 것을
도구가 정하게 된다(B.1 지적 4와 같은 실패).

**이 네 번의 실패가 판정 §3("경계가 임의적")의 가장 강한 경험적 증거다.**
추상적으로 동의한 것이 아니라, 네 번 시도해서 네 번 다른 방식으로 틀렸다.

**주장의 범위**(D-33-V §7이 요구한 정정): 정확한 결론은 **"현재 시도한 proxy들이
불충분·불안정하다"**이고, "4번 실패했으므로 원리적으로 분류 불가능하다"로
확대하면 안 된다. 표면적·구문적 proxy만으로 경계를 안정적으로 추출할 수 있다는
**증거가 없다**는 것이 우리가 말할 수 있는 전부다.

## B.5 V4 — (d) 기각 근거: **CONFIRMED**

지시 표현이 PMB **5개 층**(단순보편·단순존재·부정 scope·기수·비례)에 분포한다.
판정 §10의 "문제의 표현이 여러 층에 퍼져 있으므로"가 사실이다.

## B.6 V4b (적대검증 파생 신규 항) — 분류 unresolved: **CONFIRMED (기계 확인)**

`PMB-p87-d1860` "Tom bought Mary some chocolates."에 두 종류의 오답을 넣었다.

```text
(A) 인코딩만 다름   : ∃z[chocolate(z)] buy(entity tom, entity mary, z)
    → result=fail  dims=['scope_signature_v2']
(B) 진짜 scope 오류 : ∀z[chocolate(z)] ∃x ∃y buy(x,y,z)
    → result=fail  dims=['scope_signature_v2']
```

**두 원인이 같은 진단 값을 낸다.** 판정 §1("현재 O1 signature만으로는 분리할 수
없다")과 §8(`problem classification: unresolved`)이 기계로 확인됐다.

## B.7 V5 — `dispatch: blocked`가 상태와 일치: **CONFIRMED**

in-N 결과 파일 **0건**(`stage2_controls_results*`만 존재 — control 4라운드).
코호트 dispatch 누계 0건이 유지된다.

## B.8 V6·V7 — 선행 판정과의 정합, 그리고 **실효되는 것**

- `operational_patch: forbidden`은 D-31 Q31.4와 같은 방향이다(그 판정도 같은
  문구로 운영 세션의 임의 수리를 금지했다).
- 판정 §7이 D-32의 확장이 아님을 명시했고, 우리 요청서 §6의 논거와 일치한다.
- **실효 고지**: 판정이 `O1_SCOPE_PROJECTION_V3`을 예고했으므로
  **V2는 최종이 아니다.** V5 동결의 `measurement_contract`는 잠정이고,
  V5로 얻은 control 5/5도 V3에서 재확인이 필요하다. 이것을 숨기지 않는다 —
  V5 동결이 헛일이었다는 뜻은 아니다(V2가 없으면 이 질문 자체가 안 보였다).

## B.9 우리 요청서의 정정 사항

판정 §9가 우리 §9(control 5/5는 Q33을 인증하지 못한다)를 정확하다고 확인했고,
그 형식화를 더 명료하게 줬다: `control eligibility excludes X → control PASS
therefore says nothing about X`. 이 문장을 계약 문서에 넣을 값이 있다.

## B.10 한계

- 판정 §3의 **의미론 주장**(`someone`과 `him`의 quantificational force가 다르다)
  자체는 우리 도구로 검증하지 못했다. 우리가 가진 것은 gold 인코딩과 표면
  토큰이고, 그것은 의미론의 증거이지 의미론이 아니다. **UNVERIFIABLE로 보고한다.**
- B.3의 전수는 **PMB 20건**이다. FOLIO는 이 문제의 형태가 다르므로(FOL이
  고유명을 상수로 쓴다) 별도 실사가 필요하다 — 하지 않았다.
- 다음 상신(referential ∃ 경계 정의)의 재료로 무엇을 더 실측해야 하는지는
  이 검증이 정하지 않았다. B.3·B.4가 "synset으로는 불가, 표면 토큰이 필요,
  그러나 표면 규칙은 네 번 실패"까지 말해 준다.
