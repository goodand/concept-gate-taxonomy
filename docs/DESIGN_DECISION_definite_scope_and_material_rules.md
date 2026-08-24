# DESIGN DECISION — D-E2E-v1-31: 한정사 scope 지위·배제 규칙·중복 처리 (Q31 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_mrs_fail_closed_and_rights|D-30]] · **D-31** · 다음 (없음 — 사슬 끝) · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-24, 사용자 경유 (판정자: 외부 설계 담당, Wolfram으로 **선택지의 논리적 결과**를 검증했다고 명시 — 의미론적 사실 자체의 판정이 아니라고 스스로 한정)
- 원 요청: [[DESIGN_REQUEST_definite_scope_and_material_rules|Q31]]
- 요약: **Q31.1 (b) 유지** — 한정사를 BODY 경쟁자에서 제외하지 않는다("IR에 정의성
  구성자가 없다"가 "그 양화가 scope topology에 무영향"을 함의하지 않는다. 제외는
  **ambiguity를 uniqueness로 바꿀 수 있고** 그것이 D-30 fail-closed와 정면 충돌한다.
  +6/+93은 qualification utility이지 semantic soundness가 아니다) ·
  **Q31.2** E13·E14·E15 전부 승인, 단 사유가 다르다: E13은 "표현 불가"가 아니라
  `UNSUPPORTED_COMPOUND_CARDINAL_MAPPING_V1`(승인된 사상이 없어서 fail-closed) ·
  E14는 `NOT_CARDINAL_QUANTIFICATION` + **결정적 detector 필수**(사람 독법을
  production selector로 쓰지 말고, 확정 못 하면 `NEEDS_AUDIT`) · E15는
  `TYPE_MISMATCH`로 **정본 hard gate**(최상위) ·
  **Q31.3 (d\*)** exact pair는 collapse(대표자는 결정적 규칙), **동일 surface +
  상이 MRS는 `ORACLE_COLLISION`으로 별도 차단**(자동 대표자 선택 금지, cohort 부적격),
  `mrs_sha256` 필수 · **Q31.4** 현재 동작이 선언된 scope-only measurand와
  **불일치**(측정 오염 확인) → **운영 세션 즉석 수정 금지**, 후속 projection 판정 필요.
- **V5 freeze: BLOCKED 유지.** 재료 3/1·여유 0 그대로이고 Q31.4가 **새 blocker**다.
- 이번 판정의 핵심 원칙(판정문 인용): **"재료 부족을 해결하기 위해 scope
  competitor를 제거하지 않는다."**

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
# D-E2E-v1-31 판정

제출된 실측과 현재 계약만을 기준으로 판정합니다. Wolfram은 선택지의 **논리적 결과**—특히 ambiguity→uniqueness 변환, 타입 불일치, 중복 독립성, scope-only metric의 불변성—를 검증하는 데 사용했습니다. 의미론적 사실 자체를 Wolfram이 판정한 것은 아닙니다. 

## 판정 요약

| 질문                     | 판정                                                                  |
| ---------------------- | ------------------------------------------------------------------- |
| **Q31.1 한정사 BODY 경쟁자** | **(b) 유지** — 현재 증거로 제외 불가                                           |
| **Q31.2 E13**          | **승인**, 단 사유를 `unsupported compound cardinal mapping`으로 정정          |
| **Q31.2 E14**          | **승인**, deterministic detector 필요                                   |
| **Q31.2 E15**          | **승인, 정본 hard gate로 채택**                                            |
| **Q31.3 중복**           | **(d*)** exact pair는 collapse, 동일 surface+상이 MRS는 collision으로 별도 차단 |
| **Q31.4 제한식 비-머리 내용**  | **현재 동작은 scope-only measurand와 불일치** — 후속 projection 판정 필요          |

---

# Q31.1 — 한정사는 admissible BODY 경쟁자인가

## 판정: **(b) 유지**

현재 단계에서는 `_the_q`, `proper_q`, `pronoun_q`, `def_explicit_q`, `def_implicit_q`를 BODY 경쟁자에서 제외하지 않습니다.

핵심 이유는 다음 추론이 성립하지 않기 때문입니다.

```text
IR에 definiteness constructor가 없다
    ⇏
해당 MRS quantifier가 scope topology에 영향을 주지 않는다
```

Wolfram으로 이 구조를 반례 검사하면:

```text
unrepresented definiteness = true
scope-topology effect       = true
```

인 모델이 논리적으로 가능하고, 더 중요하게는

```text
제외 전 admissible BODY = 2
제외 후 admissible BODY = 1
```

인 경우가 존재합니다.

즉 제외 규칙이 **ambiguity를 uniqueness로 바꿀 수 있습니다.**

이는 D-30의 fail-closed 원칙과 직접 충돌합니다.

```text
UNKNOWN / underspecified
      ↓ node exclusion
UNIQUE / resolved
```

가 되어서는 안 됩니다.

### F3의 +6 / +93은 근거가 아니다

한정사를 제외하면 재료가

```text
proportional 1 → 7
cardinal candidate 11 → 104
```

로 늘어난다는 사실은 **qualification utility**를 보여줄 뿐, semantic soundness를 증명하지 않습니다. 

오히려 여유가 0이라는 현재 상황에서는 이 구분을 더 엄격히 해야 합니다. 재료 확보를 위한 규칙 변경과 의미론적 정당화가 결합되면 selection pressure가 생깁니다.

### `(a)`를 승인하려면 무엇이 추가로 필요한가

후속 증거가 다음을 독립적으로 입증하면 재상신할 수 있습니다.

```yaml
DEFINITE_SCOPE_NONCOMPETITOR_QUALIFICATION:
  require:
    - exclusion does not change relative scope among measured operators
    - exclusion cannot convert a multi-solution completion into a unique measured completion
    - rule is source-general, not fixture-selected
    - rule has deterministic structural criterion
    - rule is independently regression-tested
```

단순히 “우리 IR에 definiteness가 없다”는 것은 충분하지 않습니다.

### 닫힌 열거 vs 성질 기반

이번 판정에서는 제외 자체를 승인하지 않으므로 결정할 필요가 없습니다.

나중에 승인된다면 **v1은 닫힌 열거가 우선**입니다. `"RSTR가 유일 개체를 지시한다"` 같은 의미 성질 판별은 Shared Kernel/adapter에 새로운 semantic judgment를 도입합니다.

---

# Q31.2 — E13 / E14 / E15

세 규칙 모두 v1 exclusion contract로 승인합니다. 다만 각각의 **정당화가 다릅니다.**

## E13 — disjunctive/range cardinal

### 승인하되 사유 수정

현재 설명:

> count는 단일 `num`만 갖는다.

만으로는 충분하지 않습니다.

왜냐하면 전체 IR 방언에는 `or`, `and`, 여러 `count`를 조합할 능력이 있기 때문입니다.

예를 들어 추상적으로는:

```text
two or three bottles
```

를

```text
or(
  count(eq,2,...),
  count(eq,3,...)
)
```

처럼 표현할 가능성을 완전히 배제할 수 없습니다.

따라서 E13의 정확한 사유는:

```yaml
E13_disjunctive_or_range_cardinal:
  decision: REJECT
  reason: unsupported_compound_cardinal_mapping_v1
```

이어야 합니다.

즉:

> **표현 불가능해서가 아니라, 현재 승인된 semantics-preserving mapping이 없어서 fail-closed reject한다.**

Wolfram 형식화도 이를 `REJECT_UNSUPPORTED_MAPPING_V1`으로 분류했습니다.

이는 중요한 차이입니다. 향후 dialect 확장 없이도 별도의 검증된 projection rule로 지원 가능할 여지를 남깁니다.

---

## E14 — numeric designator

### 승인

```text
Intel 286
386 microprocessors
```

처럼 숫자가 **개체 수를 양화하지 않고 명칭 일부**라면 O1 cardinal quantification의 대상이 아닙니다.

분류는:

```text
REJECT_NOT_CARDINAL_QUANTIFICATION
```

이 맞습니다.

다만 Gate C의 사람 독법만을 production selector로 사용하면 안 됩니다.

동결 전에는 반드시 deterministic trigger가 필요합니다.

```yaml
E14:
  semantic_category: numeric_designator
  detector:
    deterministic: required
    fixture_specific_exception_table: forbidden
```

자동 detector가 안전하게 확정할 수 없는 경우에는:

```text
INELIGIBLE / NEEDS_AUDIT
```

로 보내야지 추측해서 cardinal로 채택해서는 안 됩니다.

---

## E15 — non-entity bound variable

### **강하게 승인. 정본 hard type gate로 채택**

이 셋 중 가장 명확합니다.

subject `count`의 `var`는 개체 변수인데 MRS에서:

```text
card.ARG1 = i
```

또는

```text
card.ARG1 = e
```

라면 이를 `count`로 사상하려면 **변수 타입을 바꾸는 coercion**이 필요합니다.

이는 현재 adapter 계약에 없습니다.

따라서:

```yaml
E15_non_entity_bound_variable:
  require:
    card.ARG1.type: x
  otherwise:
    reject: TYPE_MISMATCH
```

로 두는 것이 맞습니다.

Wolfram 분류도:

```text
E15 → REJECT_TYPE_MISMATCH
```

로 나왔습니다.

### 승수/측정 label heuristic과 관계

E15를 **더 상위의 정본 gate**로 두십시오.

권장 순서:

```text
card candidate
    ↓
ARG1 type == x ?
    ├─ no  → E15 REJECT
    └─ yes
         ↓
    remaining semantic/attachment checks
```

측정 명사와의 label 공유 등의 규칙은 이후의 별도 보조 exclusion으로 남길 수 있습니다.

즉 8,220건을 위해 복잡한 multiplier detector를 먼저 돌릴 이유가 없습니다.

---

# Q31.3 — MRS 동일 중복

## 판정: **(d*)**

두 종류를 분리해야 합니다.

### Case A — 동일 surface + 동일 MRS

예:

```text
item A:
  text_sha256 = T
  mrs_sha256  = M

item B:
  text_sha256 = T
  mrs_sha256  = M
```

이는 실제로 같은 trial입니다.

**하나만 남깁니다.**

대표자는 의미론적으로 선택하지 말고 결정적으로:

```text
minimum item_id
```

같은 규칙을 사용합니다.

```yaml
duplicate_policy:
  exact_surface_and_mrs:
    action: collapse
    representative: deterministic
```

428건은 이 방식으로 제거하면 됩니다. 

---

### Case B — 동일 surface + 상이 MRS

예:

```text
T + M1
T + M2
```

이 경우 `(b)`처럼 text hash만으로 하나를 임의 제거하면 안 됩니다.

subject가 보는 입력은 동일한데 oracle이 둘이기 때문입니다.

Wolfram으로 trial identity를 형식화하면:

```text
same input + same oracle
→ EXACT_DUPLICATE_COLLAPSE

same input + different oracle
→ SAME_INPUT_DIFFERENT_ORACLE_COLLISION
```

입니다.

후자는 단순 dedup 문제가 아니라 **oracle identity conflict**입니다.

따라서:

```yaml
same_surface_different_mrs:
  status: ORACLE_COLLISION
  cohort_eligibility: false
  resolution:
    - externally adjudicate
    - or exclude all conflicting analyses
```

로 처리하십시오.

한 gold를 임의 선택하면 fixture selection 단계가 oracle ambiguity를 해결해 버립니다.

---

## `mrs_sha256`을 넣는가

**예.**

권장 material identity는 최소:

```yaml
fixture_material_identity:
  source_id: ...
  item_id: ...
  text_sha256: ...
  mrs_sha256: ...
```

그리고 adapter 산출물을 별도로:

```yaml
adapter_output:
  expected_ir_sha256: ...
  adapter_version: ...
  canonicalization_profile_hash: ...
```

로 두는 편이 명확합니다.

현재 `lf_sha256`이 **정확히 원본 MRS byte artifact의 hash**라는 계약이라면 이름만 명확히 해도 됩니다. 그렇지 않다면 `mrs_sha256`을 별도 필드로 추가하십시오.

핵심은:

```text
source artifact identity
≠
adapter output identity
```

를 혼동하지 않는 것입니다.

---

# Q31.4 — 제한식의 비-머리 내용은 measurand인가

## 판정: **현재 동작은 선언된 scope-only measurand와 일치하지 않습니다**

F6은 중요한 측정 오염을 보여줍니다.

현재:

```text
Two previous exorcisms have failed.
```

에서 subject가

```text
two exorcisms
```

의 quantifier scope를 정확히 맞춰도 `previous`에 해당하는 restriction predicate를 빠뜨리면 structural mismatch가 날 수 있습니다. 

그렇다면 O1ScopeMatch는 사실상 두 능력을 동시에 재고 있습니다.

```text
1. quantifier scope compilation
2. restriction-internal semantic decomposition
```

그런데 선언된 measurand는 전자입니다.

Wolfram에서 요구되는 불변성을 형식화하면:

```text
scope topology 동일
+
non-scope restriction predicate 내용만 다름
→ O1ScopeMatch 동일
```

이어야 하는데 현재 구조는 이 불변성을 깨뜨릴 수 있습니다.

형식 결과:

```text
ScopeOnlyInvarianceViolated = True
```

였습니다.

---

## 그렇다고 restriction 전체를 하나의 atom으로 지우면 안 된다

제거 대상은 **non-scope-bearing content**뿐이어야 합니다.

예를 들어:

```text
previous exorcisms
```

의 `previous` 같은 비-scope 술어는 projection에서 비계로 축약할 수 있습니다.

그러나 restriction 내부에 실제 양화 구조가 있다면:

```text
a representative of every company
```

같은 경우 `every`의 topology까지 지워서는 안 됩니다.

따라서 후속 projection은 대략:

```text
restriction
├── ordinary lexical/event predicates → canonical opaque restriction content
└── scope-bearing operators           → preserve structure
```

가 되어야 합니다.

예:

```text
restriction(
  and(
    exorcism(x),
    previous(x)
  )
)
```

→

```text
restriction(ATOM)
```

하지만:

```text
restriction(
  and(
    representative(x),
    forall(y, company(y), ...)
  )
)
```

라면:

```text
forall(...)
```

의 scope-bearing topology는 보존해야 합니다.

---

## 이 변경은 운영 세션이 즉석에서 해서는 안 된다

F6은 V4 cohort에도 이미 같은 현상이 있음을 보여줍니다. 따라서 단순 bug fix가 아닙니다.

이는 scorer projection 정의를 바꾸므로:

```text
measurement contract change
```

입니다.

따라서 별도 판정으로 올리는 것이 맞습니다.

그 전까지는:

```yaml
Q31_4:
  current_behavior:
    status: MEASURAND_CONTAMINATION_IDENTIFIED
  operational_patch: forbidden
  next_action: explicit_projection_ruling_required
```

로 기록하십시오.

---

# D-31 정본 제안

```yaml
D_E2E_v1_31:

  Q31_1:
    decision: B
    definite_quantifiers_remain_BODY_competitors: true

    rationale:
      - absence_of_definiteness_constructor_does_not_imply_non_scopal
      - removing_competitors_can_convert_ambiguity_to_uniqueness
      - material_yield_is_not_semantic_evidence

    future_exclusion_requires:
      independent_non_scopal_proof: true
      deterministic_rule: true
      no_ambiguity_to_uniqueness_conversion: true

  Q31_2:

    E13:
      approved: true
      status: REJECT
      reason: UNSUPPORTED_COMPOUND_CARDINAL_MAPPING_V1
      intrinsically_unexpressible_claim: false

    E14:
      approved: true
      status: REJECT
      reason: NOT_CARDINAL_QUANTIFICATION
      deterministic_detector_required: true

    E15:
      approved: true
      status: REJECT
      reason: TYPE_MISMATCH
      require_ARG1_type: x
      role: primary_hard_gate

  Q31_3:
    decision: D_STAR

    exact_duplicate:
      key:
        - text_sha256
        - mrs_sha256
      action: COLLAPSE
      representative: deterministic

    same_text_different_mrs:
      action: ORACLE_COLLISION
      automatic_representative_selection: forbidden
      cohort_eligible: false

    material_manifest:
      mrs_sha256: required

  Q31_4:
    intended_scope_only_metric:
      non_scope_restriction_content_scored: false

    current_projection:
      status: CONTAMINATED

    followup_required:
      collapse_non_scope_restriction_content: true
      preserve_nested_scope_bearing_structure: true
      operational_hotfix: forbidden
```

## V5 상태

이번 판정으로 **V5 freeze를 열어서는 안 됩니다.**

Q31.1에서 한정사 제외를 승인하지 않았으므로 F1의 현재 확정 재료는 여전히:

```text
cardinal     = 3
proportional = 1
margin       = 0
```

입니다. 그리고 Q31.4가 새 measurement-contract 문제를 드러냈습니다. 

따라서 현재 상태는:

```text
cardinal/material minimum: satisfied, zero margin
proportional minimum:      satisfied, zero margin
definite exclusion:        NOT APPROVED
dedup policy:              resolved by D-31
E13/E14/E15:               resolved by D-31
restriction projection:    NEW BLOCKER
V5 freeze:                 BLOCKED
```

로 두는 것이 일관됩니다.

특히 이번 Q31에서 중요한 원칙은 **재료 부족을 해결하기 위해 scope competitor를 제거하지 않는 것**입니다. 한정사를 제거해 후보가 크게 늘어나는 것은 운영상 유용한 신호지만, 그 규칙이 ambiguity를 uniqueness로 바꿀 수 있는 한 D-30의 fail-closed 조건보다 우선할 수 없습니다.

<!-- VERBATIM-END -->

---

# B. 운영 세션 수신 검증 (2026-08-24)

`VERBATIM_SHA256: 2fab19ecfe9fbe9dea8409f319ad4c23036bdc82f309c220d04ef0c7b43d096d`
(BEGIN 다음 개행 ~ END 직전, UTF-8. verbatim 627행)

## B.0 검증 설계

이 판정은 앞선 것들과 성격이 다르다. **우리 제안을 기각**하고(Q31.1), 기각
근거로 **기계 검증 가능한 논리 주장 3건**을 제시한다: ambiguity→uniqueness
변환 · 타입 불일치 · scope-only 불변성 위반. 판정자가 Wolfram으로 **선택지의
논리적 결과**만 검증했고 의미론적 사실은 판정하지 않았다고 스스로 한정했으므로,
우리 검증의 초점은 **"그 논리적 반례가 우리 실물에 실재하는가"** 다.

| 축 | 판정의 검증 가능한 주장 | 수단 |
|---|---|---|
| V1 | 4문항 전부 응답, D-30 fail-closed와 정합 | 요청서·D-30 원문 대조 |
| **V2** | **제외 전 admissible ≥2 → 제외 후 1인 경우가 존재한다** | 37,060건 전수 재스캔 + 실물 READ |
| V3 | E15를 최상위 hard gate로 두는 것이 정당하다 | 게이트 순서 교환성 + 2차 게이트 대상 수 |
| V4 | 동일 surface + 상이 MRS는 별개 문제(`ORACLE_COLLISION`)다 | `text_sha256` 그룹 내 `mrs_sha256` 분해 |
| V5 | `lf_sha256`이 원본 artifact 해시라면 이름만 명확히 하면 된다 | 실물 바이트와 해시 대조 |
| V6 | `ScopeOnlyInvarianceViolated = True`, 단 중첩 scope는 보존해야 한다 | 투영 불변성 실측 2방향 |
| V7 | `operational_patch: forbidden` 준수 | 작업트리 diff(부작위 검증) |
| V8 | V5 freeze BLOCKED, restriction projection이 NEW BLOCKER | 상태 문서 갱신 목록 |

## B.1 V1 — 응답 완전성·무충돌: **CONFIRMED**

Q31.1~Q31.4 전부 판정됐고 부수 질문(닫힌 열거 vs 성질 기반, `mrs_sha256`)도
답했다. 선행 판정과의 관계:

- **D-30 Q30.1과 정합**: 한정사 제외를 기각한 근거가 D-30의 fail-closed
  원칙 자체다(`UNKNOWN → node exclusion → UNIQUE`가 되어서는 안 된다).
  D-30을 뒤집는 것이 아니라 **그 절차의 2단계("BODY 후보가 될 수 없는 label
  제거")를 좁게 읽으라**는 확정이다.
- **D-29 §11과 무충돌**: E15를 최상위로 올리는 것은 require 목록의 **순서**를
  정하는 것이고 D-29는 순서를 정하지 않았다.
- **D-25의 "실패 예정 계약 금지"와 무충돌**: 재료가 3/1로 하한을 충족하므로
  Q31.1(b)가 실패 예정 계약을 만들지 않는다. 여유 0은 위험이지 실패 확정이 아니다.
- 우리가 **권고하지 않은** 선택지가 채택됐다(Q31.1은 3안을 대등하게 올렸다).
  P19 억제 2회차의 결과가 기각이며, 판정문이 그 이유를 명시했다 —
  "재료 확보를 위한 규칙 변경과 의미론적 정당화가 결합되면 selection pressure가 생긴다."

## B.2 V2 — 판정의 반례가 **99건 실재**한다 (핵심)

37,060 record를 전수 재스캔해 `제외 전 admissible` → `제외 후 admissible`을
비교했다.

| 변환 | 건수 |
|---|---:|
| 2→1 | 28 |
| 3→1 | 25 |
| 4→1 | 17 |
| 5→1 | 13 |
| 6→1 | 7 |
| 7→1 | 3 |
| 8→1 | 3 |
| 10→1 | 2 |
| **11→1** | **1** |
| **합계 (ambiguity→uniqueness 변환)** | **99** |
| 1→1 (변환 아님, 원래 유일) | 12 |

**결정적 사실**: Q31 요청서 §F3이 보고한 재료 증가분 **+6(비례) + 93(기수) =
99**가 이 표의 변환 합과 **정확히 일치한다.** 즉 그 증가분은 **전부**
ambiguity→uniqueness 변환의 산물이고 "원래 유일했던" 사례는 **0건**이다.
그리고 현재 적격 12건(기수 11 + 비례 1)은 전부 `1→1`로 제외의 영향을 받지 않는다.

`11→1`이 가장 극단적이다 — 후보 11개 중 10개가 한정사 제외로 사라진다.
판정이 "제외 규칙이 ambiguity를 uniqueness로 바꿀 수 있다"고 쓴 것은 논리적
가능성 진술이었고, **우리 corpus에서는 그것이 유일한 발생 형태**였다.

2→1 표본 실물(READ):

| item | 대상 양화 | 표면 |
|---|---|---|
| `20048010` | `_the_q` | The two banks merged in 1985. |
| `20255005` | `udef_q` | Pilgrim had been closed for 32 months. |
| `20290029` | `udef_q` | Here are two cases to illustrate. |
| `20322029` | `_most_q` | The dollar gained against most foreign currencies. |
| `20465035` | `udef_q` | They have about seven candidates. |
| `20738003` | `_both_q` | Both moves are effective today. |

표본을 읽으면 판정의 우려가 더 구체화된다: `20255005`의 `32 months`는 **측정
구문**(E0)이고 `20738003`은 **`_both_q`**(E6)다 — 즉 +93 중 상당수는 한정사를
제외해 통과시켜도 **다른 배제 규칙에 다시 걸린다.** 재료 증가분의 실질은 99보다
작고, 그럼에도 그 전부가 변환이다. **판정 (b)를 우리 실측이 지지한다.**

## B.3 V3 — E15 최상위 hard gate: 결과 불변, 비용 논거는 부분적

게이트 순서를 바꿔 전수 실행했다.

| 순서 | 2차 게이트가 볼 대상 | 최종 통과 |
|---|---:|---:|
| E15(타입) → E0(label 공유) | 21,257 | **15,084** |
| E0 → E15 | 15,430 | **15,084** |

**최종 집합이 동일하다**(교환성 성립) — E15를 정본 hard gate로 올려도 적격
결과가 바뀌지 않는다. 이것이 판정 채택의 안전 근거다.

한 가지 정정: 판정문은 "8,220건을 위해 복잡한 multiplier detector를 먼저 돌릴
이유가 없다"고 적었다. 항목당 비용에서는 맞다(E15는 문자열 접두 검사, E0은
HCONS 해소가 필요하다). 그러나 **2차 게이트가 볼 대상 수는 오히려 늘어난다**
(15,430 → 21,257). 총비용은 여전히 E15-first가 유리하지만, "먼저 돌릴 이유가
없다"의 근거는 **비용이 아니라 계약 명확성**(타입 게이트는 hard, label 공유는
heuristic)으로 읽는 것이 실측에 맞다.

## B.4 V4 — Case B가 Case A보다 **크다**

`text_sha256`으로 묶고 그룹 내 `mrs_sha256`을 분해했다.

| 분류 | 그룹 | item | 판정의 처리 |
|---|---:|---:|---|
| Case A 동일 surface + 동일 MRS | 83 | 초과 **205** | `COLLAPSE`(결정적 대표자) |
| **Case B 동일 surface + 상이 MRS** | **69** | **395** | **`ORACLE_COLLISION`, cohort 부적격** |

Case B 표본: `Ad Notes. . . .`(item 10 / MRS 2종) · `PAPERS:`(3 / 2) ·
centennial 면책문(**12 / 3종**) · `New York City:`(2 / 2). 전부 WSJ 상용구이고
ERG 파스 선택 차이다.

**판정의 Case A/B 분리가 필수임이 실측으로 확인된다.** 요청서가 보고한
"428건"은 MRS 해시 기준 중복이었고, 표면 기준으로 다시 묶으면 **더 큰 문제
(395건)가 그 아래 있었다.** 텍스트 해시만으로 dedup하면(요청서 선택지 b)
395건에서 **fixture selection이 oracle ambiguity를 임의 해결**하게 된다 —
판정이 금지한 그것이다.

## B.5 V5 — `lf_sha256`은 **원본 artifact 해시**다 (필드 추가 불필요)

`PMB-p69-d1730`의 기록값을 후보들과 대조했다.

| 후보 | 일치 |
|---|---|
| **원본 SBN 파일 바이트** | **★일치** |
| 원본 SBN(주석 제거) | 불일치 |
| 표면 텍스트 | 불일치(그것은 `text_sha256`) |
| adapter 산출 IR(정렬/비정렬 json) | 불일치 |

그리고 `expected_ir_sha256`이 **별도 필드로 이미 존재**한다. 즉 판정이 요구한
`source artifact identity ≠ adapter output identity` 분리는 **manifest에 이미
성립**하며, 남은 것은 **이름**뿐이다(`lf_` = logical form이지만 실체는 원본
artifact 바이트). MRS fixture에서는 같은 필드가 `.mrs` 파일 바이트를 담게 된다.
동결 표면의 필드명 변경은 별건이므로 **계약 문서에 정의를 명문화**하는 것으로
충족한다 — 판정문이 허용한 경로다.

## B.6 V6 — 불변성 위반 재현 + 중첩 scope는 **이미 보존**된다

판정이 요구한 형식 그대로 측정했다.

```text
scope topology 동일 + 비-scope 제한식 내용만 상이 → signature 동일?  False
→ ScopeOnlyInvarianceViolated = True        (판정과 일치)
```

`count(eq,2,x, exorcism(x), fail(x))`와
`count(eq,2,x, and(previous(x),exorcism(x)), fail(x))`의 signature가 다르다.

**반대편도 측정했다** — 판정이 "지워서는 안 된다"고 명한 쪽:

```text
제한식 내부에 중첩 forall 보유 vs 평평한 2술어 → 구별되는가?  True
```

즉 **현 투영은 제한식 내부의 scope-bearing 구조를 이미 보존한다.** 후속
projection 판정이 만들어야 하는 것은 **붕괴 절반뿐**이고, 보존 절반은 이미
성립한다. 이것은 후속 판정의 구현 범위를 줄이는 사실이다.

## B.7 V7 — 금지 준수(부작위 검증): **위반 0**

`operational_patch: forbidden`. 작업트리에 투영·비교층(`_stage2_scope_projection`
·`_stage2_score`·`_stage2_run`·`_stage2_mrs_count_projection`·`cg_evaluate`·
`cg_ir`) 변경 **0건**. 한정사 제외도 구현하지 않았다. Q31.4는 코드가 아니라
**BLOCKER로만 기록**한다.

## B.8 V8 — 상태 전이

```yaml
cardinal_minimum:        satisfied (3), margin 0
proportional_minimum:    satisfied (1), margin 0
definite_exclusion:      NOT_APPROVED        # 우리 실측이 지지
dedup_policy:            resolved (Case A collapse / Case B ORACLE_COLLISION)
E13_E14_E15:             approved (사유 각각 상이)
restriction_projection:  NEW BLOCKER         # Q31.4
V5_freeze:               BLOCKED
```

## B.9 이 판정이 만드는 구현·상신 항목

**구현(판정으로 확정, 착수 가능)**
1. E15를 `MRS_COUNT_PROJECTION_V1`의 **최상위 hard gate**로(`TYPE_MISMATCH`).
   교환성이 확인됐으므로 적격 결과는 불변이다.
2. E13 사유 코드를 `UNSUPPORTED_COMPOUND_CARDINAL_MAPPING_V1`으로. "표현 불가"
   주장을 계약에서 제거한다 — 향후 검증된 projection rule로 지원할 여지를 남긴다.
3. E14 **결정적 detector** 신설 + 확정 불가 시 `NEEDS_AUDIT`.
   fixture별 예외표는 금지다.
4. dedup: Case A `COLLAPSE`(대표자 = 결정적 규칙, 예: 최소 item_id) /
   Case B `ORACLE_COLLISION` → cohort 부적격. **자동 대표자 선택 금지.**
5. material identity에 MRS artifact 해시를 명문화(`lf_sha256`의 정의를 계약에
   적거나 MRS 계열에 대해 `mrs_sha256`으로 명명).

**상신(판정 필요)**
6. **Q32 — restriction projection**: 비-scope 제한식 내용을 canonical opaque로
   붕괴하고 중첩 scope-bearing 구조는 보존하는 투영. V4 코호트에도 이미 있는
   현상이므로 **동결 표면 개정 절차**를 함께 청해야 한다.
7. 재상신 후보 — `DEFINITE_SCOPE_NONCOMPETITOR_QUALIFICATION` 5요건.
   V2가 그중 하나(`no_ambiguity_to_uniqueness_conversion`)를 **우리 corpus에서
   99건 반증**했으므로, 현재 재료로는 재상신 근거가 없다. 기록만 한다.

## B.10 한계

- V2의 99건은 **내 admissible 시제품**으로 센 값이다(계약 결박 전).
  `admissible_body_targets`가 계약으로 구현되면 수치가 바뀔 수 있다 — 다만
  "+6/+93과 정확히 일치"라는 **내부 정합**은 같은 도구로 두 번 센 결과의
  일치이므로 도구 오류를 배제하지 못한다. 계약 구현 후 재확인 대상이다.
- V4의 Case B 395건은 **배제로 종결 가능**하다. 판정이 남긴 두 경로(외부
  adjudication / 전량 배제) 중 후자를 택하면 되고 **비용이 0**이다 — 적격 4건
  (`20413069`·`20725062`·`21618050`·`20214052`)이 전부 **그룹 크기 1**(중복도
  충돌도 없는 유일 문장)임을 확인했다. 외부 adjudication은 재료 여유를 늘리려
  할 때의 선택 카드이고 **현재 차단 요인이 아니다.**
- V6-b의 "중첩 scope 보존"은 **합성 입력**으로 확인했다(실물에 중첩 양화
  제한식 사례를 아직 찾지 못했다). P15 관점에서 잠정이다.
- Q31.4는 **V4 코호트에도 있는 현상**이므로, 후속 판정이 투영을 바꾸면
  기존 20건의 채점 성질도 바뀐다 — 재동결 범위가 MRS 재료에 한정되지 않는다.

---

# C. 구현 기록 — D-31 확정분 5항 (2026-08-24)

프로토콜: 분석 사다리(일치→부분→조합→추상화) · 탐색 범위(workspace→subtree→
TDD+위임) · **구현 위임은 Sonnet 5**(Agent tool에 `effort`가 없어 프로토콜의
`(Haiku,xhigh)`를 실을 수 없다). 계약(TDD)은 운영 세션이 쓰고 구현만 위임했다.

| 항목 | 사다리 결과 | 처리 |
|---|---|---|
| ① E15 최상위 hard gate(`type_mismatch`) | 1단계 — 대상 모듈이 오늘 쓴 것이라 재사용 질문 없음 | 계약 8건 추가 → Sonnet 구현. **22 passed** |
| ② E13 사유 코드 개정 | 같음 | 같은 위임에 포함 |
| ③ E14 결정적 detector | 1단계 **없음**(신규) | 계약 14건 → Sonnet 구현 `_stage2_numeric_designator.py` 68행. **14 passed** |
| ④ dedup Case A/B | 1단계 **없음** — 선별 코드에 중복 처리 0건(위임 조사 + 재실측) | 계약 15건 → Sonnet 구현 `_stage2_dedup.py` 80행. **15 passed** |
| ⑤ material identity 명문화 | 1단계 **일치** — 계약이 이미 성립 | 코드 0행. 명시적 결박 3건 추가, **구현 없이 GREEN** |

## C.1 ⑤가 구현 없이 끝난 이유

판정: "현재 `lf_sha256`이 정확히 원본 artifact byte의 hash라는 계약이라면
**이름만 명확히 해도** 된다." 실측으로 그 계약이 성립함을 두 경로로 확인했다.

- 계산부: `freeze_stage2_v4.py:162` `put_cache(f.encode())`(FOLIO의 FOL 텍스트) ·
  `:232` `put_cache(sbn_bytes)`(PMB의 원본 바이트)
- 구조: `.oracle_cache`가 그 해시로 **content-addressed**다 — 기존 테스트
  `test_all_v4_fixtures_satisfiable_from_cache`가 `cache/e["lf_sha256"]`로
  조회하므로, 값이 artifact 바이트 해시가 아니면 그 테스트가 이미 깨진다.

즉 **간접 보장만 있고 명시 단언이 없었다.** 그래서 세 단언을 추가했다:
캐시 내용 재해시 = `lf_sha256` · `lf_sha256 ≠ expected_ir_sha256 ≠ text_sha256`
(신원 층 분리) · 신원 필드 전원 존재. `mrs_sha256` 필드 추가는 **불필요**하고,
MRS 계열에서는 같은 필드가 `.mrs` 바이트를 담게 된다.

## C.2 ④의 미완 부분 — 배선은 V5 동결의 몫이다

`_stage2_dedup.partition`은 계약으로 결박됐으나 **선별에 배선되지 않았다.**
선별은 `freeze_stage2_v4.py`에 있고 그것은 동결 표면이며, V5 동결 스크립트는
아직 없다(V5가 Q32로 차단돼 있다). 따라서 dedup 적용은 **V5 동결 시점**에
들어간다 — 지금 배선하면 동결 표면을 고치는 것이 된다.

Case B 395건은 **배제로 종결 가능**하다(적격 4건이 전부 그룹 크기 1). 배선 시
`collisions`를 cohort 부적격으로 흘리면 그것으로 충족한다.

## C.3 위임 감사 (P12)

세 산출 전부 재실측·감사했다.

| 파일 | 행 | import | 금지 패턴 | fixture 예외표 흔적 |
|---|---:|---:|---:|---:|
| `_stage2_mrs_count_projection.py` | 160 | 2 | **0** | **0** |
| `_stage2_dedup.py` | 80 | 1 | **0** | **0** |
| `_stage2_numeric_designator.py` | 68 | 1 | **0** | **0** |

실험 스위트 **284 passed**, 저장소 게이트 **13 passed / 0 failed / 1 blocked**.
테스트 파일 diff는 **운영 세션의 개정**(신규 8건 + 구 단언 2건 정리)이고
위임자들은 읽기만 했다 — G101의 계약 4요소(API 못박기·금지사항 이름 명시·과거
기각 사례 인용·"테스트를 고쳤는가" 보고 강제)가 세 번째로 작동했다.

부수 관측 2건:
- ①의 위임이 게이트 `12 passed, 1 failed`를 보고했다. 원인은 **병행 위임 2건의
  미완성 테스트**(모듈이 아직 없어 collection error)였고, 위임자가 `git stash`로
  자기 변경과 무관함을 스스로 검증해 보고했다. 병렬 위임의 부작용이며
  실패 귀속을 정확히 했다.
- ④의 위임이 "지시문은 16건이라 했는데 실제는 15건"이라고 보고했다 — 내 브리프의
  개수 오기이고, 테스트를 고치지 않고 사실만 보고한 것이 옳은 처리다.
