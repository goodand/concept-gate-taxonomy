# DESIGN DECISION — D-E2E-v1-23: FOLIO 승인 + FOL encoding profile (Q23)

- 수령: 2026-08-23, 사용자 경유 (설계 담당, Wolfram MCP 형식 검토 명시)
- 상신 원문: `DESIGN_REQUEST_folio_second_source.md` (Q23)
- 요지: **Q23.1 FOLIO 승인**(제2 source, v0.0, 다중 양화 ≥5) /
  **Q23.2(a) 승인** — `∀x(P→Q)`→restricted forall은 "definitional
  representation lowering"(숨은 필드 복원이 아님) / **(b) 제안 기각·수정**
  — 존재양화 분할은 source-근거 유일성이 없으므로 **neutral existential**
  (`restriction=True, body=φ`)로; subject의 restricted 출력은 비교 전
  **정의적 desugar**(`EXISTS(v,R,B)→EXISTS(v,True,R∧B)`,
  `FORALL(x,R,B)→FORALL(x,True,R→B)`)로 수렴 / **(c) prefix 순서 보존
  승인**, 양화를 가로지르는 implication 이동은 side condition이 있는 정리
  변환이라 v0 금지 / **(d) fail-closed 승인**, IMPLIES는 지원 구성자로
  승격 / **Q23.3** 자격 9항목 승인(8=FOL definitional lowering 정확성,
  9=scope·순서+미지원 음성 판별), §14의 뮤테이션 A·B·C를 자격에 포함.
- 검증: 수령 당일 — 형식 명제 4건을 **유한 모델 전수 열거로 독립 재계산,
  반례 수 56까지 정확 일치**. 말미 "수신 검증 기록". 본문 무편집.

---

## 판정 원문 (verbatim)

Wolfram MCP로 Q23의 **source 독립성**, **FOL→restricted-quantifier IR 변환의 의미 보존**, **존재양화 restriction/body 분할의 유일성**, **prefix scope 보존**을 분리해서 검토했습니다.

결론은:

> **Q23.1: FOLIO 승인**
> **Q23.2(a): 승인**
> **Q23.2(b): 제안 규칙은 기각하고 neutral existential mapping으로 수정**
> **Q23.2(c): prefix 순서 보존 승인, quantifier를 가로지르는 implication rewrite는 v0에서 금지**
> **Q23.2(d): fail-closed 승인**
> **Q23.3: 9항목 qualification 승인하되 8·9번 내용을 수정**

입니다. FOLIO는 요청서에 제시된 6개 독립성 조건을 모두 만족하는 것으로 보고되었고, 다중 양화 후보 수도 필요한 5건을 충분히 넘습니다. 

# 1. Q23.1 — FOLIO 제2 source

## 판정: **승인**

현재 제공된 사실에 따르면 FOLIO는 D-22에서 요구한:

```text
different corpus authority
independently authored gold
not PMB-derived
not project-generated
separate locator
separate adapter profile
```

을 모두 만족합니다. 

따라서 역할은 다음처럼 확정합니다.

```yaml
FOLIO_v0_0:
  O1_role: independent_second_source
  status: APPROVED

  confirmatory_role:
    multi_quantifier_scope: true
    minimum_fixtures: 5

  adapter_qualification_controls:
    simple_quantifier:
      N: 2_to_4
      counted_in_main_N: false
```

기존 cohort도 유지합니다.

```text
PMB ≤ 15
FOLIO ≥ 5
Total = 20
```

그리고 기존 acceptance:

```text
overall PASS ≥ 16/20
FOLIO multi-quantifier PASS ≥ 4/5
final ERROR = 0
unexpected UNSCORABLE = 0
```

도 변경하지 않습니다.

---

# 2. Q23.2(a) — `∀x(P → Q)` 복호

## 판정: **승인**

다음 변환:

[
\forall x(P(x)\rightarrow Q(x))
]

→

```text
FORALL x
  restriction = P(x)
  body        = Q(x)
```

은 허용합니다.

다만 정확한 분류는:

> **FOLIO가 restricted quantifier를 직접 encoding했다기보다, FOL의 implication 구조를 project IR의 restricted universal constructor로 definitionally lowering하는 것**

입니다.

즉 “FOLIO source에 숨겨진 `restriction` 필드를 복원한다”는 식으로 설명하면 너무 강합니다.

권장 명칭:

```yaml
rule:
  id: fol_forall_implication_lowering
  source_profile: FOLIO_FOL_V0
  kind: definitional_representation_lowering
```

Shared Kernel의 일반 theorem simplifier로 두지는 않습니다.

---

# 3. Q23.2(b) — 존재양화의 `restriction/body`

여기서는 제안안을 **수정해야 합니다.**

제안:

```text
∃y(A1 ∧ ... ∧ An)

leftmost unary predicates on y
→ restriction

remaining conjuncts
→ body
```

## 판정: **기각**

문제는 결정성이 아니라 **source-grounded uniqueness가 없다는 것**입니다.

Wolfram에서 restricted existential의 의미를:

[
Exists(y,R,B)\equiv \exists y(R\land B)
]

로 놓고 비교했습니다.

결과:

```text
ExistentialConjunctionPartition1EquivalentPartition2 = True
ExistentialConjunctionPartitionEquivalentNeutralTrueRestriction = True
ExistentialRestrictionBodyPartitionIsSemanticallyNonUnique = True
```

예를 들어:

[
\exists y(A\land B\land C)
]

는 모두 같은 의미를 가집니다.

```text
restriction=A
body=B∧C
```

```text
restriction=A∧B
body=C
```

```text
restriction=True
body=A∧B∧C
```

따라서 “최좌 단항 predicate” 선택은 **FOL이 제공한 사실이 아니라 우리 쪽 ontology/linguistic convention**입니다.

그 convention을 Oracle에 넣으면 expected answer의 일부를 우리가 제작하게 됩니다.

---

# 4. Q23.2(b) 대체안 — Neutral Existential

권장 mapping은 훨씬 단순합니다.

[
\exists y\phi
]

→

```text
EXISTS y
  restriction = TRUE
  body = Translate(φ)
```

예:

```text
∃y (Company(y) ∧ Holds(x,y))
```

→

```text
EXISTS y
  restriction = TRUE
  body =
    AND(
      Company(y),
      Holds(x,y)
    )
```

이것은 source에 없는 `restriction/body` 분할을 발명하지 않습니다.

---

# 5. subject가 restricted existential을 출력하면?

예를 들어 모델이:

```text
EXISTS y
  restriction = Company(y)
  body = Holds(x,y)
```

라고 출력할 수 있습니다.

그걸 오답으로 처리할 필요는 없습니다.

기존 directive가 허용한 **syntactic sugar expansion**을 사용하면 됩니다.

Canonical comparison 전에:

```text
EXISTS(v, R, B)
```

를:

```text
EXISTS(v, TRUE, AND(R, B))
```

로 lowering합니다.

### BEFORE

```text
subject:
EXISTS(y, Company(y), Holds(x,y))

oracle:
EXISTS(y, TRUE, Company(y) ∧ Holds(x,y))

→ structural mismatch
```

### AFTER

둘 다:

```text
EXISTS y
  TRUE
  AND(
    Company(y),
    Holds(x,y)
  )
```

로 비교합니다.

이것은 arbitrary theorem equivalence가 아니라 **IR constructor의 정의적 desugaring**으로 한정합니다.

---

# 6. 중요한 효과

이렇게 하면 Oracle Adapter가 다음을 판단할 필요가 없어집니다.

> “Company가 restriction이고 Holds가 nuclear scope인가?”

그 질문은 O1의 quantifier-scope estimand에 불필요합니다.

즉:

```text
source syntax
→ neutral IR
```

로 만들고,

```text
subject dialect
→ same neutral IR
```

로 만든 뒤 비교합니다.

이것이 가장 깨끗합니다.

---

# 7. Q23.2(c) — prefix 양화열

## 판정: **prefix order 그대로 보존**

이는 강한 invariant로 둡니다.

```text
∀x ∃y
```

는:

```text
FORALL x
  EXISTS y
```

이고,

```text
∃y ∀x
```

는:

```text
EXISTS y
  FORALL x
```

입니다.

Wolfram에서 2원소 domain의 모든 Boolean relation을 조사했을 때:

```text
QuantifierOrderGenerallyNonEquivalent = True
CountermodelCountOn2ElementDomain = 2
```

였고, 실제 반례 relation도 존재했습니다.

따라서 prefix ordering은 canonicalization 대상이 아닙니다.

---

# 8. 그런데 `∀x ∃y(P(x) → Q(x,y))`는 별도 문제

요청서가 지적한 이 형식이 중요합니다. 

문자 그대로는:

```text
FORALL x
  EXISTS y
    IMPLIES(
      P(x),
      Q(x,y)
    )
```

입니다.

이것을 곧바로:

```text
FORALL x
  restriction=P(x)
  body=
    EXISTS y
      Q(x,y)
```

로 바꾸려면 단순 AST decoding을 넘어섭니다.

Wolfram에서 제한된 경우를 exhaustively 검사했습니다.

`P`에 `y`가 자유로 나타나지 않는 경우:

[
\forall x\exists y(P(x)\to Q(x,y))
]

와

[
\forall x(P(x)\to\exists yQ(x,y))
]

는 2원소 nonempty domain 전수 검사에서 일치했습니다.

```text
SafePatternEquivalentOn2ElementDomain = True
```

하지만 antecedent가 existential variable에 의존하면:

```text
DependentAntecedentCanBreakRewrite = True
DependentAntecedentCountermodels = 56
```

이었습니다.

즉 이 rewrite는 **side condition을 가진 logical transformation**입니다.

---

# 9. 따라서 Q23.2(c)의 수정

v0에서는 그런 이동을 하지 않습니다.

### 권장 FOLIO canonical core

```text
FORALL
EXISTS
AND
NOT
IMPLIES
PREDICATE_APPLICATION
TRUE
```

를 허용합니다.

즉:

```text
∀x ∃y(P(x)→Q(x,y))
```

는 그대로:

```text
FORALL x
  restriction = TRUE
  body =
    EXISTS y
      restriction = TRUE
      body =
        IMPLIES(
          P(x),
          Q(x,y)
        )
```

로 보존합니다.

이후 subject의 restricted universal:

```text
FORALL(x, P, B)
```

은 canonical comparison을 위해:

```text
FORALL(x, TRUE, IMPLIES(P,B))
```

로 definitionally lower할 수 있습니다.

이렇게 하면 **quantifier 이동 theorem을 Oracle Adapter가 수행하지 않아도 됩니다.**

---

# 10. 이것이 O1 estimand를 넓히는가?

## 판정: **아니오, 조건부**

`IMPLIES`를 subject에게 새로 맞히게 요구하면 estimand가 넓어집니다.

하지만 여기서는 `IMPLIES`가 **comparison core representation**일 뿐입니다.

subject는 여전히:

```text
forall(variable, restriction, body)
```

형태를 출력할 수 있습니다.

Evaluator가 이를:

```text
forall(variable, TRUE, implies(restriction, body))
```

로 lowering합니다.

따라서 모델에게 추가 capability를 요구하지 않습니다.

```text
representation core enlarged
≠
subject estimand enlarged
```

입니다.

---

# 11. Q23.2(d) — fail-closed

## 판정: **승인**

FOLIO_FOL_V0의 지원 밖 요소:

```text
OR
EQUALITY
XOR
BICONDITIONAL
기타 미등록 operator
```

는 그대로:

### freeze 전

```text
INELIGIBLE
```

### freeze 후 발견

```text
UNEXPECTED_UNSCORABLE
```

로 둡니다.

기존 D-21 회계 규칙을 변경하지 않습니다.

단 `IMPLIES`는 이번 판정으로 **지원 구성자**가 됩니다.

---

# 12. 최종 FOLIO_FOL_V0 profile

권장 정본은 다음입니다.

```yaml
FOLIO_FOL_V0:

  source:
    corpus: FOLIO
    version: "v0.0"

  supported_source_operators:
    - FORALL
    - EXISTS
    - AND
    - NOT
    - IMPLIES
    - PREDICATE_APPLICATION
    - TRUE

  unsupported:
    - OR
    - EQUALITY
    - XOR
    - BICONDITIONAL

  quantifier_order:
    preserve_prefix_order: true
    reorder: forbidden

  universal:

    immediate_implication:
      source:
        "forall x (R -> B)"
      target:
        "forall(x, restriction=R, body=B)"
      allowed: true

    canonical_core_lowering:
      "forall(x,R,B)":
        "forall(x,TRUE,implies(R,B))"

  existential:

    source:
      "exists x φ"

    target:
      restriction: TRUE
      body: "Translate(φ)"

    unary_left_chain_heuristic:
      allowed: false

    canonical_core_lowering:
      "exists(x,R,B)":
        "exists(x,TRUE,and(R,B))"

  quantifier_crossing_rewrites:
    allowed_by_default: false

  fail_closed:
    unknown_operator: true
```

---

# 13. Q23.3 — adapter qualification

## 판정: **9항목 구조 승인**

다만 8·9번은 제안보다 조금 더 강하게 정의합니다.

### 1–7은 그대로

1. syntax parsing
2. alpha-renaming invariance
3. quantifier-reordering negative control
4. binding preservation
5. deterministic replay
6. output schema validity
7. closed-form preservation

---

## 8. FOL definitional lowering correctness

다음을 모두 검증합니다.

```text
∀x(R→B)
↔ restricted FORALL(x,R,B)

∃x φ
→ EXISTS(x,TRUE,φ)

restricted EXISTS(x,R,B)
→ neutral EXISTS(x,TRUE,R∧B)
```

그리고 AST/output schema가 동일한 canonical core를 만드는지 봅니다.

---

## 9. scope/order + unsupported negative discrimination

한 항목 안에 서로 관련된 음성 계약을 묶습니다.

반드시 포함:

```text
∀x∃y R(x,y)
≠
∃y∀x R(x,y)
```

그리고:

```text
cross-quantifier implication rewrite
without proven side condition
→ forbidden
```

또한:

```text
OR / EQUALITY / XOR / IFF
→ rejected
```

가 실제로 fail-closed되는지 확인합니다.

---

# 14. 특히 qualification에 넣어야 할 mutation

이번 Wolfram 결과를 직접 negative fixture로 옮길 수 있습니다.

### Mutation A — quantifier swap

```text
FORALL x EXISTS y R(x,y)
```

→

```text
EXISTS y FORALL x R(x,y)
```

canonical hash가 같아지면 **FAIL**.

---

### Mutation B — arbitrary existential split

source:

```text
∃y(A(y) ∧ B(y) ∧ C(y))
```

Adapter가 source 근거 없이:

```text
restriction=A
body=B∧C
```

처럼 arbitrary split하면 **FAIL**.

expected:

```text
restriction=TRUE
body=A∧B∧C
```

---

### Mutation C — unsafe implication crossing

예를 들어 existential variable이 antecedent에 나타나는 식에서 quantifier를 implication 밖/안으로 이동시키면 **FAIL**.

Wolfram이 실제 countermodel이 있음을 확인했습니다.

---

# 15. FOLIO subset 선택

FOLIO 전체를 자동으로 eligible로 만들지는 않습니다.

요청서의 census는 충분한 candidate 수가 있음을 보여줍니다. 

fixture eligibility는:

```text
FOLIO source
AND
multi-quantifier
AND
all operators ∈ FOLIO_FOL_V0
AND
closed after translation
AND
schema-valid
AND
Path A = Path B eligibility
```

를 모두 만족해야 합니다.

그리고 freeze 전에 정확히 5개 이상을 고정합니다.

---

# 16. HybLogic / WikiLogic

이 구분은 **source independence blocker는 아닙니다.**

둘 다 동일 FOLIO authority 아래의 외부 artifact이기 때문입니다. 

다만 fixture manifest에는 반드시:

```yaml
folio_subset:
  WikiLogic | HybLogic
```

을 기록하십시오.

가능하면 5개를 모두 같은 subset에서 취하기보다는, **결과를 본 뒤 subset을 고르는 일이 없도록 selection rule을 사전 동결**하면 충분합니다.

현재 정보만으로 특정 subset을 반드시 택하라고 판정할 근거는 없습니다.

---

# 17. source-confound control은 유지

D-22의 구조도 그대로 유지합니다.

FOLIO 5개가 모두 multi-quantifier이기 때문에:

```text
source = FOLIO
```

와

```text
phenomenon = multi_quantifier
```

가 confounded됩니다.

따라서 main N 밖에서:

```text
FOLIO simple-quantifier controls: 2–4
```

를 먼저 실행합니다.

이 controls가 adapter/profile 정상 작동을 증명해야 main 5개를 해석할 수 있습니다.

---

# 최종 판정

```yaml
D_E2E_v1_23:

  Q23_1:
    FOLIO:
      approved_as_second_source: true
      version: v0.0

      role:
        multi_quantifier_scope: true

      confirmatory:
        minimum_fixtures: 5

      qualification_controls:
        simple_quantifier:
          N: 2_to_4
          counted_in_main_N: false

  Q23_2:

    universal_implication:
      decision: APPROVE

      mapping:
        "forall x (R -> B)":
          "forall(x, restriction=R, body=B)"

      classification:
        definitional_representation_lowering

      global_theorem_rewrite: false

    existential_restriction_split:
      proposed_leftmost_unary_rule:
        decision: REJECT

      replacement:
        source:
          "exists x φ"
        target:
          restriction: TRUE
          body: φ

      reason:
        restriction_body_partition_not_source_unique: true

    prefix_quantifier_order:
      decision: APPROVE
      preserve_exactly: true

      cross_quantifier_implication_rewrite:
        default: forbidden

    FOLIO_FOL_V0:
      supported:
        - FORALL
        - EXISTS
        - AND
        - NOT
        - IMPLIES
        - PREDICATE_APPLICATION
        - TRUE

      unsupported_fail_closed:
        - OR
        - EQUALITY
        - XOR
        - BICONDITIONAL
        - UNKNOWN_OPERATOR

  canonical_comparison:

    forall_desugar:
      "FORALL(x,R,B)":
        "FORALL(x,TRUE,IMPLIES(R,B))"

    exists_desugar:
      "EXISTS(x,R,B)":
        "EXISTS(x,TRUE,AND(R,B))"

    quantifier_reordering: forbidden
    theorem_equivalence: forbidden

  Q23_3:
    adapter_qualification:
      count: 9

      required:
        - syntax_parse
        - alpha_rename_invariance
        - quantifier_reordering_negative_control
        - binding_preservation
        - deterministic_replay
        - output_schema_validity
        - closed_form_preservation
        - FOL_definitional_lowering_correctness
        - scope_order_and_unsupported_negative_discrimination

      all_required_PASS: true

  experiment:
    N: 20
    overall_PASS_min: 16

    FOLIO_multi_quantifier:
      N_min: 5
      PASS_min: 4

    final_ERROR: 0
    unexpected_UNSCORABLE: 0

    fixture_freeze:
      after_PathA_PathB_agreement: true
```

가장 중요한 수정은 **존재양화의 restriction을 우리가 추측하지 않는 것**입니다.

FOLIO는 독립 제2 source로 충분히 쓸 수 있지만, FOL은 `∃x(A∧B)`에서 무엇이 restrictor이고 무엇이 nuclear scope인지 말해주지 않습니다. 따라서 Oracle Adapter는 그 구분을 만들어내지 말고 **neutral core로 보존**해야 합니다.

반대로 `∀x(P→Q)`의 antecedent/consequent는 AST에서 명확하므로 restricted-universal 표현으로 내리는 것은 허용할 수 있습니다. 이 비대칭을 명시하는 것이 FOLIO adapter의 핵심 contract입니다.

---

## 수신 검증 기록 (2026-08-23, 운영 세션 — 본문 밖)

판정 본문 sha256 (이 절 추가 전):
`1412de542fb535ca6cf3e7f788c0dd3573fb5591b447f7afd3690745b14ff7ec`

형식 명제 4건을 **2원소 유한 모델 전수 열거로 독립 재계산** (Wolfram과
다른 도구·다른 형식화):

| # | 판정 명제 | 재계산 | 결과 |
|---|---|---|---|
| V1 | ∃ 분할 3종 전수 동치(비유일성의 근거) | 단항 A·B·C 전수 64조합 | **True 일치** |
| V2 | ∀∃≠∃∀, 2원소 반례 relation = **2** | 16개 relation 전수 | **2/16 정확 일치** |
| V3 | 안전 패턴(P에 y 무의존) 전수 동치 | P·Q 전수 64조합 | **True 일치** |
| V4 | 의존 antecedent 반례 = **56** | 이항 P·Q 전수 256쌍 | **56/256 정확 일치** — 형식화 재량이 있었음에도 수치까지 재현 |

정합성 검토:
- **(b) 기각이 우리 SBN 측과 무모순**: SBN adapter는 이미 exists를
  restriction=True로 방출하고 forall의 restriction은 source(짝 NEGATION
  box)가 유일하게 지정한다 — D-23의 비대칭 원칙("source가 지정하면
  restricted, 아니면 neutral") 그대로.
- **desugar의 위치**: canonical comparison 층(평가 전 양측 lowering).
  subject 방언은 불변 — estimand 확장 없음(§10). IR core에 `implies`·`not`
  이 비교층에서만 등장.
- D-22 acceptance(16/20 ∧ multi 4/5 ∧ 0/0) 무변경 확인.

적용 효과: FOL adapter가 완전 규정됨(§12 profile이 정본) — 외부 요청 없이
구현·자격·적격성 스캔까지 가능. 자격 9항목의 8·9는 §13-§14 명세(뮤테이션
A·B·C 포함).
