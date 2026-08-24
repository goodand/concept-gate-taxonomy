# DESIGN DECISION — D-E2E-v1-32-C: `Q_RSTR_BODY`를 위치로 정의 (Q32-C 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_restriction_projection|D-32]] · **D-32-C** · 다음 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-24, 사용자 경유 (판정자: 외부 설계 담당, Wolfram 검증 명시)
- 원 요청: [[DESIGN_REQUEST_q_rstr_body_position|Q32-C]]
- 요약: **(a\*) 승인 — 단 `forall` 한정.** 운영 세션이 요청서에 쓴 "제한식이
  `True`인 **양화**의 직접 body"를 문자 그대로 모든 결박자에 적용하면 안 된다.
  근거: restricted universal `P→Q`는 `True→(P→Q)`와 **항상 동치**이나,
  existential은 `P∧Q` vs `True∧(P→Q)`로 **일반적으로 동치가 아니다**(반례
  `P=F,Q=F` / `P=F,Q=T`). 따라서 정본 패턴은 `forall(var, True, implies(R,B))`
  뿐이고 `exists`·`count`·`prop`은 **제외**다.
- provenance는 **debugging metadata로는 가능하나 scoring signature에 금지**
  (`may_affect_O1ScopeMatch: false`). 태깅 경로 (b)는 기각.
- 성격: D-32의 범위 확장이 아니라 **operational clarification**. 새 측정 차원을
  추가하지 않는다(`new_measurement_dimension_added: false`).
- 운영 세션에 대한 지시: (a) 구현을 계속하되 **상수·계약명을
  `implies_in_quantifier_body_position...`처럼 일반화하지 말고 `FORALL` 한정임이
  이름과 테스트에 드러나게** 고칠 것.

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
# D-E2E-v1-32-C 판정

## 판정: **(a*) 승인**

다만 문구를 **“양화 일반”이 아니라 `forall`에 한정**해서 확정하는 것이 맞습니다.

즉 D-32의

```yaml
implies_generated_by_forall_desugar:
  preserve_as: Q_RSTR_BODY
```

를 다음처럼 재해석하십시오.

```yaml
implies_in_forall_body_position_with_empty_restriction:
  preserve_as: Q_RSTR_BODY
```

정확한 패턴은:

```text
forall(x, True, implies(R, B))
```

에서 **직접 body의 `implies`**입니다. 

---

## 왜 provenance가 아니라 위치인가

제출 문서의 핵심 관찰이 맞습니다.

```text
forall(x, R, B)
```

를 desugar하면

```text
forall(x, True, implies(R, B))
```

가 되고, 처음부터 subject가

```text
forall(x, True, implies(R, B))
```

를 냈다면 normalization 후 두 표현은 동일합니다. 

그 이후 단계에서 provenance가 없다면:

```text
generated implies
vs
source-authored implies
```

를 구별할 **semantic information이 없습니다**.

여기에 provenance tag를 새로 넣으면 오히려:

```text
동일한 normalized semantics
+
서로 다른 surface encoding choice
→ 서로 다른 signature
```

가 됩니다.

이는 O1ScopeMatch가 **scope가 아니라 subject의 encoding 선택을 채점**하게 만드는 결과입니다.

---

## Wolfram 검증

두 규칙을 독립적인 stateless 계산으로 비교했습니다.

### 1. provenance 규칙

```text
desugared origin → Q_RSTR_BODY
source origin    → ordinary implies 처리
```

결과:

```text
ProvenanceRuleEncodingInvariant = False
```

### 2. 위치 규칙

둘 다

```text
forall + restriction=True + direct-body implies
```

이면 `Q_RSTR_BODY`로 읽게 했습니다.

결과:

```text
PositionRuleEncodingInvariant = True
Q_RSTR_BODY_PreservesLeftRightDirection = True
```

즉 위치 정의는 두 인코딩을 동일하게 처리하면서도

```text
R → B
```

와

```text
B → R
```

의 방향은 계속 구별합니다.

이는 D-32가 원했던 두 성질을 동시에 만족합니다.

---

# 중요한 제한: `forall`에만 적용

여기서 요청서의 표현:

> “제한식이 `True`인 **양화**의 직접 body”

를 문자 그대로 모든 quantifier에 적용하면 안 됩니다.

D-32의 원래 규칙은 **`FORALL` desugar**에서 나온 것이기 때문입니다.

Wolfram으로 local Boolean semantics를 확인하면:

### universal

```text
restricted universal:
P → Q

empty restriction + implication body:
True → (P → Q)
```

는 항상 동치입니다.

결과:

```text
ForallRestrictedVsEmptyRestrictionImplicationEquivalent = True
```

반면 existential analog를 생각하면:

```text
exists restriction/body semantics:
P ∧ Q
```

대

```text
empty restriction + implication:
True ∧ (P → Q)
```

는 일반적으로 동치가 아닙니다.

Wolfram 결과에서도 existential 쪽 동치는 일반적으로 성립하지 않았고, 예를 들어:

```text
P=False, Q=False
P=False, Q=True
```

에서 반례가 나왔습니다.

따라서 다음처럼 해서는 안 됩니다.

```yaml
any_quantifier:
  restriction: True
  body: implies(...)
  -> Q_RSTR_BODY
```

---

# 권장 정본 정의

```yaml
Q_RSTR_BODY_POSITION_V1:

  match:
    operator: forall
    restriction: canonical_True
    body:
      direct_operator: implies

  project_as:
    Q_RSTR_BODY:
      restriction_branch: implies.left
      body_branch: implies.right

  provenance_required: false

  non_matches:
    - exists_with_true_restriction_and_implies_body
    - count_with_implies_body
    - prop_with_implies_body
    - implies_not_directly_under_forall_body

  preserve:
    - left_right_direction
    - nested_scope_bearing_descendants

  forbidden:
    - desugar_origin_tag_in_scoring_signature
```

여기서 `canonical_True`라고 쓴 이유는 projection 전에 이미 canonical/desugar 단계가 있으므로, raw surface spelling이 아니라 정규화된 `True`를 검사해야 하기 때문입니다.

---

## 이 변경의 성격

이것은 D-32의 범위를 새로 넓히는 판정이라기보다 **D-32가 구현 가능하려면 필요한 operational clarification**으로 분류하는 것이 맞습니다.

특히 다음을 새로 허용하는 것이 아닙니다.

```text
arbitrary source implies → quantifier restriction/body
```

허용되는 것은 오직:

```text
forall
└─ restriction = True
└─ direct body = implies(R,B)
```

라는 이미 정규형으로 정의된 위치입니다.

따라서 arbitrary implication inference나 theorem-equivalence normalization도 아닙니다.

---

# 태깅 경로 (b)는 기각

`desugar_generated=true` 같은 provenance를 남기는 것은 debugging metadata로는 가능하지만, **scoring signature에는 들어가면 안 됩니다.**

즉:

```yaml
provenance:
  may_exist_for_diagnostics: true
  may_affect_O1ScopeMatch: false
```

가 맞습니다.

그렇지 않으면 동일 의미를 두 dialect-legal encoding으로 표현한 subject가 서로 다른 점수를 받을 수 있습니다. 제출 문서가 지적한 교란이 정확히 발생합니다. 

---

# 정본

```yaml
D_E2E_v1_32_C:

  decision: A_STAR

  reinterpretation:
    old:
      implies_generated_by_forall_desugar

    new:
      implies_in_forall_direct_body_with_empty_restriction

  exact_pattern:
    forall(var, True, implies(R, B))

  projection:
    result: Q_RSTR_BODY
    left: R
    right: B

  provenance:
    required: false
    scoring_relevant: false

  encoding_invariance:
    required: true

  left_right_direction:
    preserved: true

  scope:
    forall_only: true
    exists: excluded
    count: excluded
    prop: excluded

  status:
    D32_intent_preserved: true
    new_measurement_dimension_added: false
    operational_implementation_allowed: true
```

따라서 운영 세션이 구현 중인 **(a)는 계속 진행해도 됩니다**, 단 상수/계약명을 `implies_in_quantifier_body_position...`처럼 일반화하지 말고 **`FORALL` 한정임이 이름과 테스트에 드러나도록 수정**하는 것이 필요합니다.

<!-- VERBATIM-END -->

---

# B. 운영 세션 수신 검증 (2026-08-24)

`VERBATIM_SHA256: ee6f3d7e4738f82548400f87ca892f9d4c84e63af82c6652787d4fb835f32bf5`
(BEGIN 다음 개행 ~ END 직전, 개행 제외. verbatim 319행)

## B.0 검증 설계 (6축) + **설계 자체의 적대 검증**

이 판정은 우리 재해석을 **승인하되 좁혔다.** 그래서 검증의 초점은 "판정이
옳은가"가 아니라 **"판정이 좁힌 범위가 우리 구현에 반영돼 있는가"** 다.
사용자 권장에 따라 설계를 세운 뒤 **그 설계를 적대 검증에 붙였고**, 이번에는
**정본을 먼저 저장한 뒤** 공격을 붙였다(G123 수정 — 지난 라운드에 정본 파일이
없어 공격자가 우리 질문서를 답으로 착각해 3건이 오조준됐다).

| 축 | 검증 대상 | 결과 |
|---|---|---|
| V1 | 응답 완전성 · D-32/D-27 무충돌 | CONFIRMED |
| **V2** | 현 구현이 4종 결박자 전부에 위치 규칙을 적용하는가 | **결함 확정** |
| **V3** | 판정의 동치 주장 독립 재계산 | **정확히 재현** |
| V4 | encoding invariance | **desugar 경유 시에만** 성립 |
| V5 | 이름·계약이 `forall` 한정을 드러내는가 | 결함 → 수리 |
| V6 | provenance가 signature에 없는가 | CONFIRMED |

## B.1 V1 — 무충돌: CONFIRMED

이 판정은 D-32의 범위 확장이 아니라 **operational clarification**이라고 스스로
분류했고(`new_measurement_dimension_added: false`), 우리 대조도 그와 같다.
D-27(binding topology)·D-32(닫힌 profile)와 충돌하지 않는다. `left_right_
direction: preserved`는 D-27의 요구를 그대로 잇는다.

**주목할 점**: 이것은 운영 세션의 제안이 **네 번째로 좁혀진** 사례다(P19).
우리가 요청서에 "제한식이 `True`인 **양화**"라고 쓴 것을 판정이 `forall`로
좁혔고, 그 근거가 우리가 제시하지 않은 **국소 Boolean 의미론**이었다.

## B.2 V2 — 과일반화가 **우리 코드에 실재한다** (결함 확정)

실측: `FORALL_RSTR_BODY` 이전 표지(`QRB`)가 **4종 결박자 전부**에 붙고 있었다.
판정이 `non_matches`로 명시한 `exists`·`count`·`prop` 세 종이 전부 틀렸다.

**계약이 이것을 잡지 못한 이유**: `test_q7_q_rstr_body_direction_is_preserved`가
`forall`만 시험 입력으로 썼고, 나머지 3종 경로에는 **테스트가 없었다.**
판정이 명한 `non_matches`를 계약이 결박하지 않았으므로 과일반화가 침묵했다.

수리 후 계약 8건을 추가해 결박했다(`exists`/`count`/`prop` 각각 ·
직접 body 아닌 위치 · 제한식이 비어 있지 않은 경우 · 방향 보존 · 이름 노출 ·
provenance 부재). **40 passed.**

## B.3 V3 — 판정의 동치 주장을 **독립 도구로 이중화**

2원소 전수 열거(Wolfram 미사용 — D-23의 유한 모델 열거와 같은 방식):

| P | Q | universal 동치 | existential 동치 |
|---|---|---|---|
| F | F | True | **False** |
| F | T | True | **False** |
| T | F | True | True |
| T | T | True | True |

`universal 4/4 동치` · `existential 반례 = {(F,F), (F,T)}` — **판정문이 든
반례와 정확히 일치한다.** 즉 `forall` 한정의 근거가 우리 재계산으로 확증된다.

## B.4 V4 — encoding invariance는 **desugar가 만든다** (운영 전제)

| 입력 | 두 인코딩의 signature |
|---|---|
| raw(비정규화) | **다르다** |
| desugar 경유 | **같다** |

즉 판정의 `encoding_invariance: required: true`는 **desugar가 먼저 정규화하기
때문에** 만족되고, 위치 규칙 자체가 만드는 성질이 아니다. 비정규화 입력에 이
투영을 쓰면 불변성이 깨진다. 이것은 계약이 못박아야 할 **운영 전제**이므로
`test_encoding_invariance_holds_through_desugar`가 desugar를 명시적으로 거치고
docstring에 그 이유를 적었다.

## B.5 V5·V6 — 이름 노출(수리) · provenance 부재(확인)

- **V5**: 판정의 명시 지시("`FORALL` 한정임이 이름과 테스트에 드러나도록")에
  따라 표지를 `QRB` → **`FORALL_RSTR_BODY`** 로 바꾸고 `Q_RSTR_BODY_SCOPE =
  ("forall",)` 상수를 노출했다. `REINTERPRETATION` 문구도 판정의 확정 문면과
  근거(반례 두 개 포함)로 교체했다. 계약이 이름과 scope를 검사한다.
- **V6**: signature는 중첩 tuple뿐이고 문자열 원소가 정해진 어휘에서만 나온다.
  `desugar`·`origin`·`generated`·`provenance` 문자열 부재를 계약으로 결박했다
  (부재의 증명 방식 — 판정의 `forbidden` 항목).

## B.6 설계 적대 검증 결과 — **오조준 0건**

| Finding | red team | lead 재실측 |
|---|---|---|
| F1·F2 과일반화 4종 + `non_matches` 미집행 | blocker | **CONFIRMED** — lead가 독립으로 먼저 확정 |
| F3 encoding invariance에 desugar 필요 | major | **CONFIRMED** — lead도 독립 확정 |
| F4 이름이 `forall` 한정을 드러내지 않음 | major | **CONFIRMED** — 신규(lead 미발견) |
| F5 existential 반례 타당 | 확인 | CONFIRMED |
| F6 signature에 provenance 없음 | 확인 | CONFIRMED |

**이번 라운드는 오조준이 0건이다.** 직전 라운드는 4건 중 3건이 오조준이었고
원인이 "정본 파일 없이 공격을 붙인 내 브리프"였다. 정본을 먼저 저장하고
브리프에 그 경로와 "상신서는 답이 아니다"를 명시한 것이 차이다 —
**G123의 수리가 한 라운드 만에 효과를 냈다.**

## B.7 이 검증이 잡은 내 측정 오류 1건

첫 V2 실측에서 표지를 `Q_RSTR_BODY` 문자열로 찾았는데 구현은 `QRB`를 쓰고
있었다. 결과가 "4종 전부 False"로 나왔고 그것이 **불가능하게 균일**해서
(§14의 규칙 — 이질적 입력에 균일한 결과는 측정기 점검 신호) 재조준했다.
재조준하니 4종 전부 True였다. P16의 반복이며, §14의 규칙이 또 값을 냈다.

## B.8 한계

- 수리는 **소규모(2곳)라 위임하지 않고 직접** 했다(G102 선례 — 이탈 사유를
  적는다). 컨텍스트 압박도 사유다.
- `forall` 한정의 근거는 **국소 Boolean 의미론**이다. 우리 방언의 `count`·`prop`
  결박자에 대해 같은 논증을 전개하지는 않았다 — 판정이 `excluded`로 못박았고
  우리는 그것을 따랐다.
- V4의 운영 전제(desugar 선행)는 계약으로 결박했으나, **파이프라인이 실제로
  그 순서를 지키는지**는 V5 재동결 시 배선에서 재확인해야 한다.
