# DESIGN DECISION — D-E2E-v1-29: 기수·비례 방언과 MRS source (Q29 판정)

- 수신: 2026-08-24, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_cardinal_dialect_and_mrs_source.md`
  (sha256 `991b69a91e7baff950fb…`)
- 요약:
  > **Q29.1 = (a\*)** — `count` constructor 도입, 단 `rel`을
  > **`eq|ge|le|gt|lt`로 확장**(운영 세션안 `eq|ge|le`는 좁다 — ATIS의
  > `> 3`을 담으려면 정수 산술 정규화가 계약에 들어간다). 숫자는 term이
  > 아니라 **operator parameter** → 항 문법 `Variable | Entity` 불변.
  > 수치 term 도입 (b)는 기각(범용 수치 언어를 만들게 된다).
  > **비례는 `count`에 흡수하지 않고 별도 `prop` constructor** — `most`는
  > 어떤 고정 기수 threshold로도 표현할 수 없다(restrictor 크기 의존).
  > v1은 `prop.rel := most`만 지원하고 half·ratio·percentage는 source가
  > 생길 때 profile revision으로 추가. 최종 방언 **8종**.
  > `count`의 의미도 동결: `|{x: R(x)∧B(x)}| rel num`이며 **자체가
  > scope-bearing binder**다 — `EXISTS + 수치 주석`이 아니다.
  > **Q29.2 = (a)** — Redwoods/MRS를 **`CONDITIONALLY_QUALIFIED_CANDIDATE`**
  > 로 승인(APPROVED_SOURCE 아님). source 동결 전 필수: proportional item
  > locator, 선택 component 권리 확인, 기수 ≥3·비례 ≥1, MRS→IR adapter
  > 자격, card attachment fail-closed 자격, Gate C. MRS→count mapping은
  > **같은 결박 변수로 연결될 때만** package하고 `MRS_COUNT_PROJECTION_V1`
  > 의 reject 조건 5종(다중 card 후보·변수 불일치·미해소 handle·수치 부착
  > 모호·미지원 관계)을 갖는다. 이것은 **measurement projection이지 정리
  > 재작성이 아니다**(full MRS 의미식과의 동치를 주장하지 않는다).
  > adapter 자격에 기수·비례 특화 뮤테이션 5종 필수: 값 변조(3→4) FAIL,
  > 관계 변조(ge→gt) FAIL, attachment 변조(다른 양화 변수에 붙이기) FAIL,
  > scope 변조(RSTR/BODY 교환) FAIL, 비례 변조(most→일반 양화) FAIL.
  > **Q29.3 = (ii)** — MRS의 cardinal EP와 `CARG`는 **scored target
  > signal**이며 비계가 아니다. 제거하면 `3≠4`가 소실돼 cardinal fixture가
  > cardinal을 측정하지 않는 상태가 된다 — G3와 정확히 같은 failure class.
  > MRS 요소별 지위 표(event var·tense=nuisance / 어휘 라벨=diagnostic /
  > RSTR·BODY·card 관계·CARG·`_most_q` kind·그 RSTR/BODY=scored)를
  > projection profile에 명시.
  > **Q29.4 = 승인** — 조사 요청서에 `Prior Rulings / Excluded Sources`
  > 절 필수화. 단순 blacklist가 아니라 **source별로 status·판정 id·사유·
  > scope·reopen 조건**을 기록한다(새 release가 나왔을 때 과거 판정으로
  > 자동 배제하는 반대 오류도 막는다). 권장 요청서 구조 8절 제시.
  > **full O1은 여전히 freeze BLOCKED** — 설계 결손은 해소됐으나 material
  > qualification(기수 확보 0/3, 비례 0/1)이 남았다.

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP로 Q29의 핵심 형식 조건을 검토했습니다. 결론은 다음입니다.

> **Q29.1 = (a*)** — `count` constructor를 도입하되 `rel`은 `eq|ge|le|gt|lt`로 확장합니다. 비례는 `count`에 흡수하지 않고 별도 `prop` constructor로 둡니다.
> **Q29.2 = (a)** — ERG/MRS + Redwoods를 **조건부 제3 source 후보로 승인**합니다. 아직 fixture source로 최종 승격시키지는 않습니다.
> **Q29.3 = (ii)** — MRS의 cardinal EP는 반드시 scored projection에 남겨야 합니다. 제거하면 cardinal stratum 자체가 사라집니다.
> **Q29.4 = 승인** — 조사 요청마다 `Prior Exclusions / Reopen Conditions` 절을 필수화합니다.

현재 full O1은 그대로 유지하며, 기수·비례 material이 실제로 확보되기 전에는 재동결하지 않는 것이 맞습니다. 

---

# 1. Q29.1 — `count` constructor

## 판정: **(a*) 승인**

Wolfram에서 선언된 boundary와 subject language를 분리하면:

```text
Declared O1:
  cardinal_quantifier = already present

Old subject dialect:
  count = absent

New subject dialect:
  count = present
```

결과:

```text
CardinalAlreadyDeclared             = True
AddingCountChangesDeclaredBoundary = False
OldDialectHasCardinalConstructor    = False
NewDialectHasCardinalConstructor    = True
```

따라서 `count` 추가는 새로운 estimand를 집어넣는 것이 아니라:

> **이미 선언된 cardinal_quantifier를 subject가 실제로 표현할 수 있게 만드는 coverage repair**

입니다.

D-28의 판단을 그대로 확정할 수 있습니다.

---

# 2. 다만 `rel = eq|ge|le`는 조금 좁습니다

요청서 자체에 ATIS 사례가:

```text
> 3
```

으로 들어 있습니다. 

이를:

```text
gt 3 → ge 4
```

로 바꿀 수도 있지만, 그러면 처음부터 정수 산술 normalization을 계약에 넣어야 합니다.

그럴 이유가 없습니다.

권장 v1:

```json
{
  "kind": "count",
  "rel": "eq|ge|le|gt|lt",
  "num": 3,
  "var": "x",
  "restriction": {},
  "body": {}
}
```

즉 숫자는 term이 아니라 **count operator의 parameter**입니다.

이렇게 하면 기존:

```text
Term := Variable | Entity
```

계약도 그대로 유지됩니다.

---

# 3. `count`의 의미도 명시해야 함

constructor 형태만 정하면 부족합니다.

예를 들어:

```text
count(
  rel=ge,
  num=3,
  var=x,
  restriction=dog(x),
  body=bark(x)
)
```

는 O1에서 다음 generalized-quantifier reading을 나타낸다고 동결해야 합니다.

[
|{x:R(x)\land B(x)}| \ge 3
]

즉 대략:

> “적어도 세 R이 B이다.”

중요한 것은 `count`가 단순히:

```text
EXISTS + numeric annotation
```

가 아니라 **자체적으로 scope-bearing binder**라는 점입니다.

따라서 projection에서도 다음을 모두 scored dimension으로 유지합니다.

```text
count kind
rel
num
restriction/body
binder
nested scope position
```

---

# 4. 숫자를 term으로 넣는 (b)는 기각

예:

```text
pred("ge", count(x), num(3))
```

같은 식은 지금 프로젝트에 불필요한 확장을 일으킵니다.

새로 필요해지는 것:

```text
numeric term
comparison predicate
possibly arithmetic expression
count/set-size term
type validation for numeric arguments
```

이 됩니다.

반면 `count` operator 방식은 O1에 필요한 수치 정보만 캡슐화합니다.

따라서:

```text
numeric general-purpose language
```

를 만들지 않고:

```text
cardinal quantifier language
```

만 추가하는 쪽이 더 좁습니다.

---

# 5. 비례를 `count.rel="most"`로 합치면 안 됨

## 별도 `prop` 필요

Wolfram으로 `most`를 고정 숫자 threshold로 표현할 수 있는지 검사했습니다.

정의:

[
Most(R,B) \iff |R\cap B| > |R|/2
]

그리고 임의의 고정된:

[
|R\cap B|\ge n
]

과 일치하는 `n`이 있는지 restrictor size 1~8에 대해 전수 검사했습니다.

결과:

```text
FixedNumericThresholdsMatchingMostAcrossRestrictorSizes = {}
AnyFixedCountThresholdWorks = False
```

즉 `most`는 cardinal threshold가 아닙니다.

restrictor 크기에 의존합니다.

따라서:

```text
count(rel="most")
```

는 두 semantic family를 한 operator에 과도하게 섞습니다.

---

# 6. 권장 proportional constructor

현재 material 근거가 `_most_q`뿐이라면 v1을 작게 유지하십시오.

```json
{
  "kind": "prop",
  "rel": "most",
  "var": "x",
  "restriction": {},
  "body": {}
}
```

즉 당장은:

```text
prop.rel := most
```

만 지원해도 됩니다.

아직 source가 없는:

```text
half
ratio
percentage
```

까지 미리 설계하지 않습니다.

향후 source qualification이 생기면 profile revision으로 추가하면 됩니다.

---

# 7. 최종 subject dialect

따라서 full O1용 dialect는:

```text
forall
exists
and
pred
not
implies
count
prop
```

8종이 됩니다.

이 중:

```text
count
prop
```

는 일반 논리언어 확장이 아니라 각각 이미 선언된:

```text
cardinal_quantifier
proportional_quantifier
```

의 measurement representation입니다.

---

# 8. Q29.2 — ERG/MRS + Redwoods

## 판정: **(a) 조건부 승인**

제공된 사실만 보면 현재 조사 후보 중 MRS가 구조적으로 가장 잘 맞습니다.

특히:

```text
bare_div_q_rel(... x ...)
  RSTR
  BODY

card_rel(... x ...)
  CARG 3
```

가 서로 분리되어 있고 같은 participant variable을 통해 연결된다는 점이 중요합니다. 

이 구조는 우리가 원하는:

```text
binder
restriction
body
cardinality
```

를 서로 구분한 채 보존할 수 있습니다.

---

# 9. MRS → `count` mapping

권장 measurement mapping:

```text
MRS quantifier EP:
  variable = x
  RSTR = R
  BODY = B

MRS card EP:
  variable = x
  relation = r
  CARG = n
```

동일한 `x`로 확실히 연결될 때만:

```text
count(
  var=x,
  rel=r,
  num=n,
  restriction=R,
  body=B
)
```

로 package합니다.

Wolfram에서 retained fields를 tuple로 모델링해 round-trip 여부를 확인하면:

```text
RetainedFieldsRoundTrip = True
```

였습니다.

즉 **선택한 측정 필드에 한해서는** 이 mapping이 정보를 잃지 않습니다.

---

# 10. 중요한 제한

이것을:

> “MRS 전체 의미식이 count IR과 논리적으로 동치다.”

라고 주장하면 안 됩니다.

분류는 Q25/Q28과 같습니다.

```text
full MRS semantics
    ↓
O1 measurement projection
    ↓
count/prop scope representation
```

입니다.

즉 **measurement projection**, not theorem rewrite.

---

# 11. MRS fail-closed 조건

다음은 최소한 필요합니다.

```yaml
MRS_COUNT_PROJECTION_V1:

  require:
    quantifier_EP_present: true
    cardinal_EP_present: true
    same_bound_variable: true
    RSTR_resolved: true
    BODY_resolved: true
    numeric_CARG_parseable: true
    cardinal_relation_supported: true

  reject_if:
    - multiple_card_EP_candidates
    - card_and_quantifier_variable_disagree
    - unresolved_handle_constraint
    - numeric_scope_attachment_ambiguous
    - unsupported_numeric_relation
```

즉 `card_rel`가 문장 어딘가 있다는 이유로 가장 가까운 quantifier에 붙이면 안 됩니다.

---

# 12. Redwoods의 현재 지위

아직:

```text
APPROVED_SOURCE
```

가 아닙니다.

정확한 지위는:

```yaml
Redwoods_MRS:
  status: CONDITIONALLY_QUALIFIED_CANDIDATE
```

입니다.

최종 source 승격 전에 요청서의 네 조건을 모두 충족해야 합니다. 

* proportional item locator 확보
* 실제 selected component/item의 rights 확인
* MRS→IR adapter qualification
* card/prop attachment fail-closed qualification

그리고 당연히:

```text
eligible cardinal >= 3
eligible proportional >= 1
```

을 실제로 확인해야 합니다.

---

# 13. adapter qualification

기존 “9항목 동형”만 기계적으로 복사하는 것보다 **기수/비례 특화 검사를 명시적으로 포함**해야 합니다.

최소 핵심 추가 mutation은:

### Cardinal-value mutation

```text
3 → 4
```

하면 반드시 FAIL.

### Relation mutation

```text
ge → gt
```

하면 FAIL.

### Attachment mutation

같은 문장 안의 다른 quantifier variable에 `card_rel`를 붙이면 FAIL.

### Scope mutation

RSTR/BODY를 바꾸면 FAIL.

### Proportional mutation

```text
most → ordinary quantifier
```

가 같은 signature가 되면 FAIL.

기존 generic adapter checks에 이것들을 포함시키면 됩니다.

---

# 14. Q29.3 — card EP를 지워도 되는가

## 판정: **(ii)**

여기는 매우 명확합니다.

예를 들어:

```text
three dogs ...
```

와:

```text
four dogs ...
```

를 생각합니다.

full O1 signature:

```text
COUNT eq 3 RSTR BODY
COUNT eq 4 RSTR BODY
```

는 다릅니다.

그런데 cardinal 정보를 제거하면 둘 다:

```text
Q RSTR BODY
```

가 됩니다.

Wolfram 확인:

```text
FullSignaturesDifferent            = True
AfterDroppingCardinalityDifferent = False
```

즉 cardinal EP를 projection에서 지우면:

[
3 \neq 4
]

라는 O1 signal이 완전히 사라집니다.

---

# 15. 따라서 (i)는 boundary의 조용한 축소

fixture 이름만:

```text
cardinal_quantifier
```

로 유지하고 실제 scoring에서는 card를 지우면:

> **cardinal fixture가 cardinal을 측정하지 않는 상태**

가 됩니다.

G3에서 동사 signal을 지웠던 것과 정확히 같은 failure class입니다.

따라서:

```text
card_rel = nuisance
```

로 분류하면 안 됩니다.

O1에서는:

```text
card_rel + CARG
```

가 **target signal**입니다.

---

# 16. MRS에서 무엇이 비계이고 무엇이 signal인가

구분은 다음과 같습니다.

| MRS 요소                  | O1 지위       |
| ----------------------- | ----------- |
| event variable          | nuisance 가능 |
| tense/event role        | nuisance 가능 |
| lexical predicate label | diagnostic  |
| quantifier RSTR/BODY    | **scored**  |
| card relation           | **scored**  |
| CARG numeric value      | **scored**  |
| `_most_q` kind          | **scored**  |
| `_most_q` RSTR/BODY     | **scored**  |

이 표를 projection profile에 명시하는 것이 좋습니다.

---

# 17. proportional `_most_q`

`_most_q(x,hR,hB)`가 실제 proportional reading임이 source qualification에서 확인되면:

```text
prop(
  rel=most,
  var=x,
  restriction=R,
  body=B
)
```

로 직접 대응시키는 것이 가장 단순합니다.

단 superlative `most beautiful`과 혼동해서는 안 됩니다.

Q28의 실패를 반복하지 않으려면 Gate C에:

```text
surface reading
MRS predicate
assigned stratum
```

을 같이 표시해야 합니다.

---

# 18. Q29.4 — 조사 채널에 prior exclusions 전달

## 판정: **승인**

Wikisem이 다시 후보로 들어온 문제는 조사 자체의 문제가 아니라 **research request가 현재 design state를 전달하지 못한 것**으로 보는 것이 맞습니다. 

앞으로 조사 요청에 필수 절을 둡니다.

# `Prior Rulings / Excluded Sources`

예:

```yaml
prior_source_rulings:

  wikisem:
    status: EXCLUDED
    ruling: D-E2E-v1-21
    reasons:
      - article_level_LF
      - sentence_level_alignment_absent
      - O1_v0_coverage_zero
      - discourse_operators_outside_profile

    reopen_only_if:
      - new_sentence_level_external_gold_release
      - materially_different_version
```

---

# 19. 단순 blacklist로 만들지는 말 것

과거 배제는 영원한 금지가 아닐 수 있습니다.

따라서 각 source에:

```text
status
decision id
reason
scope
reopen condition
```

을 기록합니다.

예:

```yaml
source: Wikisem
scope: O1_v1_sentence_level_acceptance
status: EXCLUDED
reopen_if:
  upstream publishes sentence-level aligned LF
```

이렇게 해야 새로운 release가 나왔을 때 과거 판정 때문에 자동 배제하는 반대 오류도 피할 수 있습니다.

---

# 20. 조사 요청서의 권장 구조

```text
1. Research question
2. Required source properties
3. Declared IR/measurement boundary
4. Prior accepted candidates
5. Prior excluded sources + reasons
6. Reopen conditions
7. Unknowns to investigate
8. Required evidence format
```

이 정도면 동일 source를 반복 조사하는 비용이 상당히 줄어듭니다.

---

# 21. full O1의 현재 상태

이번 Q29 이후에도 바로 freeze하면 안 됩니다.

현재 상태는:

```yaml
full_O1:

  dialect:
    cardinal:
      design: APPROVED
      constructor: count

    proportional:
      design: APPROVED
      constructor: prop

  source:
    PMB: requalification path
    FOLIO: multi_quantifier source
    Redwoods_MRS: conditional candidate

  material:
    cardinal_required: 3
    cardinal_confirmed: 0

    proportional_required: 1
    proportional_confirmed: 0

  freeze:
    status: BLOCKED
```

즉 설계 결손은 상당 부분 해소되지만 **material qualification은 아직 안 끝났습니다.** 

---

# 최종 판정

```yaml
D_E2E_v1_29:

  Q29_1:
    decision: A_STAR

    subject_dialect_add:

      count:
        fields:
          kind: count
          rel:
            - eq
            - ge
            - le
            - gt
            - lt
          num: integer
          var: variable
          restriction: Formula
          body: Formula

        scored:
          - rel
          - num
          - binder
          - restriction
          - body
          - scope_position

      prop:
        separate_from_count: true

        v1:
          rel:
            - most

        fields:
          kind: prop
          rel: enum
          var: variable
          restriction: Formula
          body: Formula

    numeric_terms:
      add: false

    interpretation:
      declared_estimand_expansion: false
      subject_language_coverage_repair: true

  Q29_2:
    decision: A

    Redwoods_MRS:
      status: CONDITIONALLY_QUALIFIED_CANDIDATE

      required_before_source_freeze:
        - proportional_item_locator
        - selected_component_rights_verified
        - cardinal_items_min_3
        - proportional_items_min_1
        - MRS_adapter_qualification
        - fail_closed_card_attachment
        - Gate_C_material_audit

  Q29_3:
    decision: II

    cardinal_EP:
      nuisance: false
      scored_target_signal: true

    CARG:
      scored: true

    remove_card_EP:
      allowed: false
      reason: collapses_distinct_cardinal_readings

    MRS_projection:
      combine_q_and_card_if:
        same_bound_variable: true
        handles_resolved: true
        attachment_unambiguous: true

      output:
        count_node: true

  Q29_4:
    decision: APPROVE

    research_request_required_section:
      name: Prior_Rulings_and_Excluded_Sources

      per_source:
        - source_id
        - ruling_id
        - status
        - exclusion_reason
        - scope
        - reopen_condition

      default:
        reconsider_excluded_source: false

      exception:
        reopen_condition_satisfied: true

  full_O1:
    freeze: BLOCKED
    unblock_when:
      - cardinal_material_qualified
      - proportional_material_qualified
      - count_prop_schema_qualified
      - MRS_adapter_qualified_if_Redwoods_used
```

가장 중요한 두 가지는 다음입니다.

1. **`count`와 `prop`은 분리해야 합니다.** `3`, `≥3` 같은 cardinality와 `most` 같은 proportionality는 같은 수치 relation family가 아닙니다. Wolfram 검사에서도 `most`를 어떤 고정 count threshold로도 표현할 수 없었습니다.
2. **MRS의 `card_rel`을 지우면 안 됩니다.** 양화 EP가 별도로 남아 있다는 사실은 MRS를 O1에 쓰기 쉽게 만들어 주지만, 그 때문에 cardinal EP가 nuisance가 되는 것은 아닙니다. 오히려 full O1에서는 그 EP가 바로 측정하려는 신호입니다.
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-24, 운영 세션)

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | `most`를 고정 기수 threshold로 표현 불가 (restrictor 1~8 전수, 해집합 공집합) | `Most(R,B) ⟺ \|R∩B\| > \|R\|/2` vs 고정 `n`의 `≥n`을 전수 대조 | **CONFIRMED — 해집합 공집합.** 크기별 필요 threshold가 `{1:1,2:2,3:2,4:3,5:3,6:4,7:4,8:5}`로 `\|R\|`에 의존 → 고정 불가. **count/prop 분리의 논거 성립** |
| V2 | cardinal EP를 지우면 `3≠4` 신호 소실 | `count(eq,3)` vs `count(eq,4)`를 일반 양화로 강등해 signature 대조 | **CONFIRMED** — full 상이 True / 제거 후 상이 **False** |
| V3 | `count` 추가가 declared boundary를 넓히지 않음 | D-28 수신 검증 V3에서 확인한 `semantic_boundary` 실물(cardinal·proportional 포함) 교차 참조 | **CONFIRMED (교차 참조)** |
| V4 | MRS retained-field 왕복 무손실 + fail-closed | 판정 §9·§11의 mapping 시제품 구현 후 직렬화 왕복과 거부 조건 실측 | **CONFIRMED** — 왕복 동일; 변수 불일치·미지원 관계·CARG 비정수 **3종 모두 거부** |
| V5 | `rel`에 `gt` 필요 (운영 세션안 `eq\|ge\|le`는 좁다) | ATIS 실측 인코딩 `( > (stops $0) 3:i )`를 `ge`로 담으려면 `3→4` 산술이 계약에 들어감 | **CONFIRMED — 판정의 확장이 정당** |

주의 기록 (적용 시 구속 해석):

1. **P14 4회 연속이지만 성격이 다르다.** Q26.3·Q27.1·Q28.2는 운영 세션
   권고가 **기각**됐고, 이번 Q29.1은 권고가 **채택되며 범위가 확장**됐다
   (`rel` 3종 → 5종, 비례 흡수 금지). 즉 기각이 아니라 정밀화다 —
   앞으로 constructor 제안 시 **source 실측 인코딩 전체를 열거**해
   필요한 `rel` 집합을 먼저 도출한다(이번엔 ATIS `>`를 빠뜨렸다).
2. **`count`는 binder다.** `EXISTS + 수치 주석`으로 구현하면 판정 §3
   위반이다 — 투영에서 `rel`·`num`·결박·제한/본문·중첩 위치가 전부 채점
   대상이어야 한다.
3. **`prop.rel`은 v1에서 `most` 하나뿐이다.** half·ratio·percentage를
   미리 설계하지 않는다(source 없음). 확장은 profile revision 사안.
4. **Redwoods는 아직 source가 아니다** — `CONDITIONALLY_QUALIFIED_CANDIDATE`.
   7개 선행 조건을 전부 충족해야 승격하며, 그중 2건(locator·권리)은 3차
   조사에 이미 상신돼 있다.
5. **freeze는 계속 BLOCKED** — 설계는 승인됐으나 재료가 0/3·0/1이다.
   D-28이 금지한 "실패가 예정된 계약 실행"을 피하려면 재료 확보가 선행이다.

수신 텍스트의 sha256 (BEGIN 다음 개행 ~ END 직전, UTF-8):
`VERBATIM_SHA256: 72b3d4ce3940fc09e8c282ffa86aa7c0b8a733d32a0ef3f439153778ad378573`
