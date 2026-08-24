# DESIGN DECISION — D-E2E-v1-32: 제한식 투영의 비-scope 내용 (Q32 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_definite_scope_and_material_rules|D-31]] · **D-32** · 다음 (없음 — 사슬 끝) · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-24, 사용자 경유 (판정자: 외부 설계 담당, Wolfram으로 **선택지의 논리적 결과**를 검증했다고 명시)
- 원 요청: [[DESIGN_REQUEST_restriction_projection|Q32]]
- 요약: **Q32.1 (a\*)** 비-scope 내용을 opaque atom으로 붕괴, 단 **empty/nonempty
  구별과 변수 incidence는 보존**(predicate erasure가 아니라 scope-measurement
  abstraction) · **Q32.2** 닫힌 profile — 직접 보존 `{forall, exists, count, prop,
  not}`, `and`/`or`는 하위에 scope가 있을 때만 **정체 없는 `SCOPE_JOIN`**,
  `implies`는 **desugar 생성분은 `Q_RSTR_BODY`** / 원본은 방향 있는
  `SCOPE_BRANCH`, **미지 연산자는 qualification_fail** · **Q32.3 (a)** 기존
  fixture 층 유지(재배정·배제 없음), 단 **20건 전량 재투영·서명 재생성·재동결
  필수** · **Q32.4 둘 다** — `PRE_EXECUTION_FREEZE_AMENDMENT_V1` 재사용 **+**
  `O1_SCOPE_PROJECTION_V2` 신설, **V1↔V2 점수 직접 비교 불가 선언** ·
  **Q32.5** 추상화 원칙을 **대칭화**하되 BODY를 `True`나 단일 atom으로 붕괴 금지
  (변수 incidence·중첩 scope 보존).
- 동결 전 고정할 **qualification test 8종**을 판정이 명시했다.
- V5: V2 구현 + qualification + 20건 재투영 + hash 재동결이 성공하면
  **설계 차단 요인 해소 가능**. 그 전까지 BLOCKED. 판정문 명시:
  "Q32가 해결되었다고 해서 즉시 dispatch하는 것은 아니다."

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
# D-E2E-v1-32 판정

제출된 Q32의 실측을 기준으로 판정합니다. 선언된 measurand가 **quantifier scope compilation**인데 현재 projection은 제한식의 비-scope predicate **개수·구조**까지 점수화하고 있으므로, D-31이 지적한 measurement contamination은 실제로 존재합니다. 동시에 nested quantifier topology는 이미 보존되고 있으므로, 필요한 변경은 “전체 단순화”가 아니라 **비-scope 영역만 선택적으로 opaque화**하는 것입니다. 

Wolfram 형식 검증에서는 다음이 확인됐습니다.

* 단일 opaque restriction은 modifier 추가/누락에 대해 불변성을 회복할 수 있음.
* `EMPTY`와 `NONEMPTY`를 별도로 두면 bare restriction과 실제 generalized restriction을 계속 구별할 수 있음.
* `and`/`or`의 연산자 정체성을 그대로 채점하면 동일한 quantifier topology를 불필요하게 구별함.
* amendment 절차와 projection profile version bump는 대안 관계가 아니라 **둘 다 필요**함.
* BODY를 `True`로 붕괴시키는 것은 부적절하고, variable-incidence는 유지해야 함.

---

## 판정 요약

| 질문                         | 판정                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------- |
| **Q32.1 붕괴 단위**            | **(a*)** 비-scope connected content를 opaque atom으로 붕괴. 단 **empty/nonempty + 변수 incidence 유지**         |
| **Q32.2 scope-bearing 정의** | 닫힌 profile 승인: `{forall, exists, count, prop, not}`는 직접 보존. `and/or/implies`는 조건부 structural carrier |
| **Q32.3 기존 2 fixture**     | **(a)** 유지. 재배정·배제 없음                                                                                |
| **Q32.4 동결 절차**            | **둘 다**: `PRE_EXECUTION_FREEZE_AMENDMENT_V1` 재사용 + `O1_SCOPE_PROJECTION_V2` 신설                       |
| **Q32.5 BODY 비대칭**         | 추상화 **원칙은 대칭화**. 단 BODY를 단일 atom/True로 만들지 않고 incidence-preserving opaque projection 사용              |

---

# Q32.1 — 붕괴 단위

## **(a*) 승인**

권장 규칙은 다음입니다.

```text
non-scope restriction content
        ↓
OPAQUE_RESTRICTION(variable-incidence)
```

예:

```text
and(previous(x), exorcism(x))
```

과

```text
exorcism(x)
```

은 둘 다:

```text
RESTRICTION_ATOM(x)
```

으로 투영합니다.

따라서 F1의 두 subject output은 같은 scope signature를 갖게 됩니다.

### 그러나 empty/nonempty는 반드시 구별합니다

다음은 같아져서는 안 됩니다.

```text
exists(x, True, B)
```

```text
exists(x, dog(x), B)
```

권장 canonical representation:

```text
EMPTY_RESTRICTION
```

대

```text
RESTRICTION_ATOM(x)
```

입니다.

Wolfram 검증:

```text
modifier omission invariant       = True
empty/nonempty distinction        = True
```

를 동시에 만족시킬 수 있었습니다.

따라서 generalized-quantifier 층이 비워지지 않습니다.

---

## 왜 (c)까지 가지 않는가

`binding variable set만 유지`는 필요 이상으로 강합니다.

최소한 다음 두 정보는 구별해야 합니다.

```text
restriction absent
restriction present and constrains x
```

즉 권장 projection의 의미는:

```text
lexical content → discard
predicate count → discard
predicate internal Boolean shape → discard
content presence → preserve
variable incidence → preserve
nested scope structure → preserve
```

입니다.

이를 **predicate erasure가 아니라 scope-measurement abstraction**으로 기록하는 것이 맞습니다.

---

# Q32.2 — `scope-bearing` 닫힌 정의

단순한 이분법보다 세 종류로 나눠야 합니다.

## 1. 직접 scope-bearing — 그대로 보존

```yaml
PRIMARY_SCOPE_OPERATORS:
  - forall
  - exists
  - count
  - prop
  - not
```

### `not` 포함

`not`은 반드시 포함합니다.

이유는 이미 `quantifier_negation_scope`가 측정 대상이고,

```text
NOT > Q
```

와

```text
Q > NOT
```

를 구별해야 하기 때문입니다.

제한식 안에 있더라도 동일합니다.

---

## 2. 순수 non-scope content — opaque화

```yaml
NON_SCOPE_CONTENT:
  - pred
```

그리고 predicate들만으로 구성된 `and/or/implies` 영역도 결국 opaque content로 접을 수 있습니다.

예:

```text
dog(x) or cat(x)
```

과

```text
dog(x)
```

은 scope-only metric에서는 동일한:

```text
RESTRICTION_ATOM(x)
```

으로 갈 수 있습니다.

이는 propositional equivalence를 주장하는 것이 아닙니다.

> O1 측정 함수가 그 차원을 의도적으로 관측하지 않는 것입니다.

---

## 3. structural scope carrier — 조건부 보존

여기가 중요합니다.

```yaml
SCOPE_CARRIERS:
  - and
  - or
  - implies
```

이들은 **자체가 measurand는 아니지만**, descendant에 scope-bearing operator가 있으면 그 topology를 연결하기 위해 보존되어야 합니다.

### `and` / `or`

예:

```text
and(
  pred(x),
  exists(y, ...)
)
```

전체를 atom으로 접으면 `exists`가 사라지므로 금지입니다.

그러나 `and`와 `or`라는 **연산자 정체 자체를 채점할 필요는 없습니다.**

따라서:

```text
and(pred, exists(...))
```

과

```text
or(pred, exists(...))
```

는 예컨대 둘 다:

```text
SCOPE_JOIN(
    OPAQUE(...),
    exists(...)
)
```

로 투영할 수 있습니다.

Wolfram에서도:

```text
keep AND/OR identity
→ same quantifier topology인데 signature가 달라짐

generic scope carrier
→ invariant
```

가 확인됐습니다.

---

## `implies`는 두 종류를 반드시 구별

여기는 provenance가 필요합니다.

### A. `FORALL` desugar가 생성한 `implies`

이것은 단순 논리 connective가 아니라 현재 canonical encoding에서:

```text
RSTR vs BODY
```

를 구별하는 구조적 장치입니다.

따라서 일반 source `implies`와 같은 규칙으로 접으면 안 됩니다.

권장:

```text
FORALL-generated implies
    ↓
Q_RSTR_BODY(left, right)
```

처럼 전용 structural marker로 취급합니다.

### B. source-authored `implies`

FOLIO 등에서 실제 의미식에 존재하던 implication입니다.

* descendant에 scope-bearing operator 없음 → opaque
* descendant에 scope-bearing operator 있음 → directional structural carrier 보존

예:

```text
implies(pred(x), forall(y,...))
```

→

```text
SCOPE_BRANCH(
  OPAQUE(x),
  forall(...)
)
```

좌/우 방향은 보존합니다.

---

## 따라서 V2의 닫힌 profile

```yaml
O1_SCOPE_PROJECTION_V2:

  primary_scope:
    preserve_exact:
      - forall
      - exists
      - count
      - prop
      - not

  structural_carriers:
    and:
      if_no_scope_descendant: collapse
      if_scope_descendant: SCOPE_JOIN

    or:
      if_no_scope_descendant: collapse
      if_scope_descendant: SCOPE_JOIN

    implies_generated_by_forall_desugar:
      preserve_as: Q_RSTR_BODY

    implies_source:
      if_no_scope_descendant: collapse
      if_scope_descendant: SCOPE_BRANCH

  lexical_content:
    pred:
      collapse_to_opaque_incidence: true

  restriction:
    distinguish_empty_nonempty: true
```

이 정도면 closed-world inference semantics와도 맞습니다. 새 operator를 발견하면 추정하지 말고 projection qualification에서 막으면 됩니다.

---

# Q32.3 — 기존 PMB 2건

## **(a) 그대로 유지**

두 fixture를 재배정하거나 제거할 이유가 없습니다.

```text
PMB-p43-d3444
PMB-p00-d1657
```

은 여전히 `single_universal` fixture입니다.

변경되는 것은:

> fixture가 어떤 층에 속하는가

가 아니라:

> 그 fixture에서 어떤 비-scope 세부사항을 점수화하는가

입니다.

따라서 새 V2 projection 아래에서는 관계절·예외구의 lexical/internal predicate multiplicity가 사라지고, 원래 의도했던 **universal scope 구조**를 측정하게 됩니다.

Wolfram 형식화에서도:

```text
projection scoring property changes = True
single-universal membership changes  = False
```

로 분리됐습니다.

단, 기존 V4 결과를 그대로 재사용해서는 안 됩니다.

**20건 전체를 V2로 다시 projection → expected signature 재생성 → hash 재동결**해야 합니다.

---

# Q32.4 — 동결 개정 절차

## 둘 다 필요합니다

질문의 두 선택지는 배타적이지 않습니다.

### Governance 절차

기존:

```text
PRE_EXECUTION_FREEZE_AMENDMENT_V1
```

을 재사용합니다.

왜 변경됐는지, 어떤 선행 ruling이 명령했는지, dispatch가 여전히 0건인지 기록하는 절차입니다.

### Measurement artifact

동시에:

```text
O1_SCOPE_PROJECTION_V2
```

를 신설해야 합니다.

이유는 projection의 semantic contract 자체가 바뀌었기 때문입니다.

단순히 모듈 SHA만 새로 찍으면 안 됩니다.

---

## V5 manifest에 명시할 것

예:

```yaml
measurement_contract:
  projection_profile: O1_SCOPE_PROJECTION_V2
  projection_profile_hash: ...
  projection_module_sha256: ...

supersedes:
  - O1_SCOPE_PROJECTION_V1

score_comparability:
  V1_to_V2:
    direct_numeric_comparison: false
    reason: non_scope_restriction_and_body_content_projection_changed
```

그리고 ruling chain에는:

```text
V1–V4:
  historical measurement semantics = V1

V5 onward:
  measurement semantics = V2
```

라고 명시해야 합니다.

Wolfram 검증에서도:

```text
amendment procedure needed = True
profile bump needed         = True
new freeze hash needed      = True
cross-version comparability declaration needed = True
```

였습니다.

---

# Q32.5 — BODY 비대칭

## 원칙은 **대칭화**해야 합니다

현재처럼:

```text
restriction:
    predicate count/shape preserved

body:
    event lexical meaning partly erased,
    variable incidence preserved
```

인 것은 동일한 scope-only measurand에 대해 설명하기 어렵습니다. 

그러나 답은 BODY 전체를:

```text
True
```

또는 단일:

```text
BODY_ATOM
```

으로 만드는 것이 아닙니다.

그렇게 하면 선행 판정이 이미 발견했던 degenerate skeleton 문제가 돌아옵니다.

---

## 권장 통일 원칙

RESTRICTION과 BODY 모두:

> **비-scope lexical content는 버리되, binder-variable incidence와 scope-bearing descendant topology는 보존한다.**

즉 abstraction policy를 동일하게 합니다.

예를 들어 BODY:

```text
and(
  fail(e),
  agent(e,x)
)
```

에서 lexical/event truth content는 제거하더라도:

```text
OPAQUE_INCIDENT(e,x)
```

처럼 결박 incidence는 남깁니다.

그리고:

```text
pred(x)
and pred2(x)
```

처럼 동일 incidence만 반복되는 것은 predicate 개수 때문에 score가 달라지지 않게 해야 합니다.

권장 개념:

```yaml
NON_SCOPE_CONTENT_PROJECTION:
  predicate_labels: discard
  predicate_multiplicity_with_same_incidence: discard
  lexical_boolean_internal_structure: discard

  preserve:
    - empty_vs_nonempty
    - variable_incidence
    - primary_scope_operators
    - necessary_scope_carrier_topology
```

이 규칙을 restriction/body 양쪽에 사용합니다.

---

# 필요한 V2 qualification tests

동결 전에 최소 다음은 contract test로 고정하는 것이 좋습니다.

1. `previous(x) ∧ exorcism(x)` vs `exorcism(x)` → **same**
2. `True` restriction vs `dog(x)` → **different**
3. nested `exists/forall/count/prop` 추가 → **different**
4. `Q > not` vs `not > Q` → **different**
5. lexical-only `and` vs `or` → **same**
6. `and/or` 안에 nested quantifier → quantifier topology **preserved**
7. generated `implies`의 RSTR/BODY 방향 → **preserved**
8. BODY lexical multiplicity만 변화 → same, 단 variable incidence 변화 → **different**

F3의 nested-quantifier 보존은 현재 합성 사례만 있으므로, 이를 **qualification negative control**로 명시하는 것이 적절합니다. 실물 fixture가 반드시 존재해야 V5를 freeze할 필요까지는 없습니다.

---

# 정본 판정

```yaml
D_E2E_v1_32:

  Q32_1:
    decision: A_STAR

    non_scope_restriction:
      collapse: opaque_atom
      preserve:
        - empty_vs_nonempty
        - variable_incidence

      discard:
        - predicate_label
        - predicate_count
        - non_scope_internal_structure

  Q32_2:
    primary_scope_operators:
      - forall
      - exists
      - count
      - prop
      - not

    carriers:
      and:
        lexical_only: collapse
        contains_scope: generic_SCOPE_JOIN

      or:
        lexical_only: collapse
        contains_scope: generic_SCOPE_JOIN

      generated_implies:
        preserve_as: Q_RSTR_BODY

      source_implies:
        lexical_only: collapse
        contains_scope: directional_SCOPE_BRANCH

    closed_profile: true
    unknown_operator: qualification_fail

  Q32_3:
    decision: A

    existing_fixtures:
      retain: true
      reassign: false
      exclude: false

    whole_cohort_reprojection: required

  Q32_4:
    amendment_procedure:
      use: PRE_EXECUTION_FREEZE_AMENDMENT_V1

    projection_profile:
      new_version: O1_SCOPE_PROJECTION_V2

    V1_V2_score_comparable: false
    V5_new_hashes_required: true

  Q32_5:
    restriction_body_abstraction_policy:
      symmetric: true

    body:
      collapse_to_true: false
      collapse_to_single_untyped_atom: false
      preserve_variable_incidence: true
      preserve_nested_scope: true

  V5:
    after_V2_implementation_and_qualification:
      design_blocker: removable
    before_that:
      status: BLOCKED
```

따라서 **Q32가 해결되었다고 해서 즉시 dispatch하는 것은 아니지만**, 이 판정을 구현하고 V2 qualification + 20건 전체 reprojection + V5 hash freeze가 성공하면, 제출 문서가 말한 현재의 유일한 **설계** 차단 요인은 해소된 것으로 볼 수 있습니다.

<!-- VERBATIM-END -->

---

# B. 운영 세션 수신 검증 (2026-08-24)

`VERBATIM_SHA256: 5c5ed5c7523d43456c2e825100d4dcfa07b278235baccca40d326ba9db192f76`
(BEGIN 다음 개행 ~ END 직전, 개행 제외. verbatim 665행)

## B.0 검증 설계

이 판정은 이례적으로 **구현 계약을 거의 다 써 주었다**(닫힌 profile +
qualification test 8종 + V5 manifest 필드). 그래서 검증의 초점은 "판정이
옳은가"가 아니라 **"판정이 명한 것이 우리 구조에서 구현 가능한가"** 다.
8축을 세우고, **그 설계 자체를 적대 검증에 붙였다**(사용자 권장).

| 축 | 검증 대상 |
|---|---|
| V1 | 5문항 응답·선행 판정(D-25 desugar·D-27 topology·D-28 incidence·D-30/31) 무충돌 |
| **V2** | qualification test 8종이 **동시 만족 가능**한가 |
| **V3** | generated vs source `implies`를 구별할 수 있는가 |
| V4 | `not` in restriction — `Q>not` vs `not>Q` |
| V5 | `and`/`or` 정체가 현재 채점되는가 |
| V6 | BODY 대칭화 — 현재 BODY가 판정 정책을 이미 만족하는가 |
| V7 | 20건 전량 재투영 영향 규모 |
| V8 | V5 동결 산출물 목록 |

## B.1 V1 — 응답·무충돌: **CONFIRMED**

Q32.1~Q32.5 전부 판정됐고 부수 질문(empty/nonempty 유지, `implies` provenance,
BODY 대칭)도 답했다. 선행 판정과의 관계:
- **D-27과 정합**: `not`을 primary scope에 넣어 `quantifier_negation_scope`
  층을 지켰다. 그리고 아래 B.5가 확인한 대로 **binding topology 요구가
  incidence의 정의를 순서로 강제한다.**
- **D-28과 정합**: BODY의 incidence 보존 원칙을 그대로 이어받고 `True` 붕괴를
  금지했다(그때 해소한 degenerate skeleton 회귀 방지).
- **D-31과 정합**: Q31.4가 명령한 후속이고 `operational_patch: forbidden`을
  지킨 상태에서 왔다.
- **D-25와 정합**: 허용 정규화가 "닫힌 열거"라는 규율을 `closed_profile: true` ·
  `unknown_operator: qualification_fail`로 이어받았다.

## B.2 V2 — 8종 동시 만족: **시제품으로 입증(8/8)**

먼저 **현재** 투영에 8종을 적용해 기준선을 얻었다.

| test | 현재 | V2 목표 | 델타 |
|---|---|---|---|
| 1 modifier 유무 → same | **False** | True | **고쳐야 함** |
| 2 empty vs nonempty → diff | True | True | 이미 충족 |
| 3 중첩 양화 추가 → diff | True | True | 이미 충족 |
| 4 `Q>not` vs `not>Q` → diff | True | True | 이미 충족 |
| 5 lexical and vs or → same | **False** | True | **고쳐야 함** |
| 6 carrier 안 중첩 양화 보존 | True | True | 이미 충족 |
| 7 생성/원본 implies 구별 | **False** | — | B.3 |
| 8 BODY 다중도/incidence | 다중도 접힘 True · incidence 변화 구별 True | True | 이미 충족 |

**즉 V2가 실제로 바꾸는 것은 #1과 #5 둘이다.** 나머지는 이미 성립한다.

그리고 판정의 닫힌 profile을 **시제품으로 구현해 8종을 동시에 통과시켰다**
(`EMPTY_RESTRICTION` vs `OPAQUE(incidence)` · `SCOPE_JOIN` · 위치 기반
`Q_RSTR_BODY` · `SCOPE_BRANCH`). 첫 실행은 6/8이었고 실패 2건이 **제 시험
입력의 오조준**이었다(아래 B.5).

## B.3 V3 — `implies` provenance: 판정의 문면은 구현 불가, **위치 규칙으로 해소**

실측: desugar가 `FORALL(x,R,B) → FORALL(x,True,implies(R,B))`로 정규화하므로
**생성 `implies`와 원본 `implies`가 바이트 동일**하다. 판정이 "여기는
provenance가 필요하다"고 적은 그 지점이다.

경로 3개를 평가했다.

| 경로 | 판정 |
|---|---|
| (1) 구현 불가로 종결 | 판정의 요구를 버리는 것이므로 부적절 |
| (2) desugar가 생성분에 태그를 남긴다 | 구현 가능하나 **부작용이 크다** — `forall(x,dog,bark)`와 `forall(x,True,implies(dog,bark))`가 **구별되기 시작한다**(현재는 동일). 그것은 subject가 고른 **인코딩**을 채점하는 것이고, **판정이 방금 제거한 교란과 같은 부류**다 |
| **(3) 위치 규칙** | **채택 권고** — 제한식이 `True`인 양화의 **직접 body**에 있는 `implies`는 provenance와 무관하게 `Q_RSTR_BODY`로 읽는다 |

(3)이 옳은 이유: 그 위치의 `implies`는 **역할이 RSTR/BODY**다. 원본이 썼든
desugar가 만들었든 의미론적으로 같은 역할이므로 provenance를 물을 필요가 없다.
결정적이고, 태깅이 불필요하며, (2)의 부작용을 만들지 않는다.
시제품에서 작동을 확인했고 test 7(방향 보존)도 통과한다.

**단 이것은 판정 문면의 재해석이므로 확인이 필요하다** — 운영 세션이
`implies_generated_by_forall_desugar`를 `implies_in_quantifier_body_position`
으로 읽어도 되는지. 이 재해석 없이는 (2)의 부작용을 감수해야 한다.

## B.4 V6/V7 — BODY는 이미 만족, 영향은 **5/20**

**V6**: BODY가 판정 정책을 **이미 만족한다**. 사건 어휘 다중도가 접히고
(`bark`+`howl`이 같은 사건이면 동일 서명), 참여자 집합이 실제로 달라지면
구별된다. 따라서 **Q32.5의 "대칭화"는 BODY를 바꾸는 것이 아니라 제한식을
BODY의 기존 정책 수준으로 올리는 것**이다 — 구현 범위가 줄어든다.

**V7**: 동결 20건 전수를 adapter로 재생해 V2가 서명을 바꿀 fixture를 셌다.

| case_id | 층 | 사유 |
|---|---|---|
| `PMB-p43-d3444` | single_universal | 제한식 다중(관계절) |
| `PMB-p00-d1657` | single_universal | 제한식 다중(예외구) |
| `FOLIO-142p1` | **multi_quantifier** | 제한식 다중 + 어휘 전용 and/or |
| `FOLIO-695p1` | **multi_quantifier** | 제한식 다중 |
| `FOLIO-721p1` | **multi_quantifier** | 제한식 다중 + 어휘 전용 and/or |

**5/20이고 그중 3건이 `multi_quantifier`** — estimand의 중심 층이다.

**Q32 상신서 §F2의 자기 정정**: 그 문서에 "동결 코호트에 이미 **2건**"이라
적었다. PMB 15건만 재고 FOLIO 5건을 재지 않은 채 일반화한 오류다(§13의
G100과 같은 형태 — 관측 범위를 전체로 오독). 정본은 **5건**이다.

## B.5 검증 설계의 적대 검증 (사용자 권장) — 4건 중 **3건 반증**

Haiku red team을 **검증 설계 자체**에 붙였다. 결과와 lead 재실측:

| Finding | red team | lead 재실측 | 판정 |
|---|---|---|---|
| F1 V1 축 누락 — "판정 질문 미회신 감지 불가" | blocker | **REFUTED** — 답을 찾으려고 `DESIGN_REQUEST`(우리 질문서)를 grep했다. 답은 판정문에 있고 5/5 응답했다 | 오조준 |
| F2 opaque atom과 empty/nonempty **동시 만족 불가** | blocker | **REFUTED** — 시제품이 8/8 동시 통과. 판정이 이미 두 canonical form(`EMPTY_RESTRICTION` / `RESTRICTION_ATOM`)을 명시했고 그것으로 충분하다 | 반증 |
| F3 implies 분기 **구현 불가**(세 경로 전부 막힘) | blocker | **부분 반증** — "위치 규칙은 투영 후 추적 불가"라는 근거가 틀렸다. 위치 판정은 **투영 중** 트리를 걸으며 하므로 가능하고 시제품이 작동한다. 다만 태깅 경로(2)의 부작용 지적은 유효하고 lead가 독립으로 같은 결론에 도달했다 | 불가능성 반증, 부작용 지적 채택 |
| F4 BODY 정책 미정의 | major | **REFUTED** — F1과 같은 오조준. 판정 Q32.5가 답했고 V6 실측이 이미 충족을 확인했다 | 오조준 |

### 오조준 3건의 원인은 **내 브리프**다

공격을 붙인 시점에 **판정 정본 파일이 아직 없었다**. 브리프에 판정 요지를
산문으로 넣고 참고 파일로 `DESIGN_REQUEST`(우리 질문서)를 줬으니, 공격자가
"답변"을 찾으려면 그 파일을 볼 수밖에 없었다. **정본을 먼저 저장하고 공격을
붙여야 한다** — 규율로 등재한다.

### 그럼에도 이 적대 검증이 값을 냈다

F3이 lead에게 **위치 규칙을 명시적으로 평가하게 만들었다.** 그 결과 (2)의
부작용을 문서화하고 (3)을 권고로 올렸다. 공격이 반증됐어도 **설계 결정을
드러내는 값**이 있었다.

## B.6 검증이 드러낸 판정의 미명세 1건 — `variable incidence`의 정의

시제품 첫 실행에서 test 8이 실패했다. 원인: 내가 incidence를 **변수 집합**으로
구현했고, 그러면 `P(x)`와 `P(x,x)`가 같아진다. 더 심각하게는
**`P(x,y)`와 `P(y,x)`도 같아진다** — 그것은 **D-27이 유지를 명한 binding
topology를 파괴**한다.

**순서 보존 incidence**(술어별 인자 이름 튜플의 순서 있는 목록, 동일 튜플의
중복만 제거)로 바꾸니 8/8이 통과했다:

| 재조준 후 | 결과 |
|---|---|
| test 7 방향 보존(피연산자가 서로 다를 때) | **diff ✓** |
| `P(x,y)` vs `P(y,x)` (D-27 요구) | **diff ✓** |
| 동일 incidence 다중도(판정 요구) | **same ✓** |

즉 판정의 `variable_incidence`는 **집합이 아니라 순서**로 읽어야 하고, 그
근거는 판정문이 아니라 **선행 판정 D-27**이다. 이것은 새 판정이 필요한 공백이
아니라 **선행 정본이 이미 결정한 것**이므로 구현에 그렇게 반영한다.

test 7의 첫 실패는 **내 시험 입력의 오조준**이었다 — 양쪽 피연산자가 같은
opaque atom으로 접히면 좌우 교환이 원리상 관측 불가이고, 그것은 결함이 아니라
계약의 귀결이다(P16의 반복 형태).

## B.7 V8 — V5 동결 산출물 (구현 항목)

판정이 manifest에 명시하라고 한 것:

```yaml
measurement_contract:
  projection_profile: O1_SCOPE_PROJECTION_V2
  projection_profile_hash: ...
  projection_module_sha256: ...
supersedes: [O1_SCOPE_PROJECTION_V1]
score_comparability:
  V1_to_V2:
    direct_numeric_comparison: false
    reason: non_scope_restriction_and_body_content_projection_changed
```

그리고 사슬에 `V1–V4 = V1 semantics` / `V5 onward = V2 semantics`를 선언한다.
절차는 `PRE_EXECUTION_FREEZE_AMENDMENT_V1` **재사용 + profile 신설 둘 다**.

## B.8 이 판정이 만드는 구현 항목

1. `O1_SCOPE_PROJECTION_V2` 신설 — 닫힌 profile. **델타는 #1(제한식 opaque
   붕괴 + empty/nonempty)과 #5(and/or 정체 미채점)** 이고 나머지는 현행 유지.
2. **순서 보존 incidence**로 구현(B.6). 집합으로 구현하면 D-27 위반.
3. **위치 기반 `Q_RSTR_BODY`**(B.3) — 재해석 확인이 필요한 항목.
4. qualification test 8종을 계약으로 고정. F3의 중첩 양화 보존은 판정이 명한
   대로 **negative control**로 표기(실물 사례 없음).
5. `unknown_operator: qualification_fail` — 미지 연산자에 추정 금지.
6. 20건 전량 재투영 → `expected_ir_sha256` 재생성 → V5 재동결(영향 5/20).
7. manifest에 B.7의 `measurement_contract` · `score_comparability` 추가.

## B.9 한계

- B.2의 8/8은 **시제품**이다. 계약 결박된 구현에서 재확인해야 한다.
- B.3의 위치 규칙은 **판정 문면의 재해석**이다. 확인 없이 구현하면 판정을
  운영 세션이 좁힌 것이 된다(P19). 구현 시 이 재해석을 명시한다.
- B.4의 5/20은 두 성질(제한식 다중·어휘 전용 carrier)로 추정한 값이다.
  실제 서명 변화는 V2 구현 후 재투영으로 확정된다.
- 적대 검증이 **정본 저장 전에** 수행돼 3건이 오조준됐다. 재공격하지 않았다 —
  하중 주장 2건은 시제품으로 직접 반증했으므로 재공격의 한계효용이 낮다.
- V5는 여전히 BLOCKED다. 판정문 명시: "Q32가 해결되었다고 해서 즉시 dispatch
  하는 것은 아니다."
