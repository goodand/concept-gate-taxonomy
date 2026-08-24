# DESIGN DECISION — D-E2E-v1-30: MRS fail-closed·기수 관계 사상·재료 권리 (Q30 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_cardinal_dialect_and_mrs_source|D-29]] · **D-30** · 다음 (없음 — 사슬 끝) · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-24, 사용자 경유 (판정자: 외부 설계 담당, Wolfram 형식화 검토 명시)
- 원 요청: [[DESIGN_REQUEST_mrs_fail_closed_and_rights|Q30]]
- 요약: Q30.1 **(a\*)** `BODY_resolved` = admissible BODY target 유일성
  (raw label count는 정의가 아니라 fast path) · Q30.2 **(a)** 결박 변수별
  ambiguity · Q30.3 **(a\*)** 닫힌 사상표 + 구조적 attachment 증명, `_over_p`·
  `_under_p`는 이름만으로 불허 · Q30.4 **(a)** 저장소 기본값 `sha256` ·
  Q30.5 취득은 APPROVED이나 **source 승격 BLOCKED**(license/NC/SA 전부
  UNRESOLVED) · Q30.6 **(a\*)** `generic_entity` 적격, 단
  `restriction_lexical_identity_scored: false`를 계약으로 동결 ·
  Q30.7 control 어휘 **개정 승인**(`most` 지원, 기수는 열거가 아니라
  결정적 정수 표현 클래스), `CONTROL_SURFACE_PROFILE_V2`로 버전·해시 고정 후
  **전체 재스캔**. **full O1 freeze는 계속 BLOCKED — 주 잔여 차단은 rights gate.**
- 운영상 핵심 지시: F4의 **16,584 attachment를 적격 fixture로 승격 금지**.
  새 계약으로 전 코퍼스를 다시 fail-closed scan해 **record 단위** 최종
  eligible count를 산출해야 한다.

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
# D-E2E-v1-30 판정

제출된 실측을 기준으로 판정합니다. 핵심은 이번 문제가 “MRS를 살리기 위한 범위 확장”이 아니라, **D-29의 추상 계약을 실제 MRS 표현 규약에 맞게 fail-closed로 구체화하는 문제**라는 점입니다. 

Wolfram으로 조건을 형식화해 검증한 결과도 다음 세 결론을 지지합니다.

* `BODY`를 완전히 제거하는 Q30.1(c)는 실제 ambiguous multi-scope도 통과시키므로 부적절합니다.
* `multiple_card`는 문장 전체가 아니라 **결박 변수별 ambiguity**로 정의해야 독립적인 cardinal 두 개를 오탐 거부하지 않습니다.
* 권리 gate는 semantic/material qualification과 독립적이므로, 의미론적 재료가 충분해도 rights가 unresolved이면 freeze는 성립하지 않습니다.

## 판정 요약

| 질문                           | 판정                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------ |
| **Q30.1 BODY_resolved**      | **(a*) 승인 — “유일하게 해소 가능”**, 단 raw label count가 아니라 admissible BODY target의 유일성 |
| **Q30.2 multiple card**      | **(a) 승인 — 같은 결박 변수에 대해서만 중복 후보 거부**                                           |
| **Q30.3 degree → count.rel** | **(a*) 승인 — 닫힌 사상표 + 구조적 attachment 증명**                                       |
| **Q30.4 WSJ surface 저장**     | **(a) 승인 — repo에는 sha256만**, 기본값 `sha256`                                      |
| **Q30.5 Open SDP rights**    | **조건부 후보 유지. 기술적 사용 가능, APPROVED_SOURCE 승격은 보류**                               |
| **Q30.6 generic_entity**     | **(a*) 적격 인정**, 단 lexical identity가 실제로 projection 밖이라는 계약 고정                  |
| **Q30.7 control lexicon**    | **갱신 승인** — `most` 지원, cardinal은 열거 단어가 아니라 parseable integer 표현 클래스           |

---

## Q30.1 — `BODY_resolved`: **(a*)**

### 판정

D-29의

```yaml
BODY_resolved: true
```

를 다음처럼 정의합니다.

> **BODY_resolved(q) iff 해당 quantifier의 admissible BODY target 집합의 크기가 정확히 1이다.**

즉:

[
\texttt{BODY_resolved}(q)
\iff
|\mathrm{AdmissibleBodyTargets}(q)| = 1
]

HCONS에 BODY가 명시적으로 등장하는지는 **유일성을 증명하는 한 방식**일 뿐, 정의 그 자체가 아닙니다.

따라서 실물의 최외곽 quantifier처럼 BODY handle이 HCONS에 직접 제약되어 있지 않더라도, 다른 제약을 적용한 뒤 가능한 BODY target이 하나뿐이면 통과할 수 있습니다.

### 중요한 제한

`"남은 label 수 == 1"`을 정의로 삼으면 안 됩니다.

그것은 v1에서 사용할 수 있는 **충분조건/fast path** 정도로 한정해야 합니다.

예를 들면:

```text
1. RSTR를 먼저 해소
2. restriction 내부 label 및 BODY 후보가 될 수 없는 label 제거
3. 기존 HCONS / scope topology와 모순되는 후보 제거
4. admissible BODY target 계산
5. 후보 수 == 1 → resolved
6. 후보 수 == 0 또는 >1 → reject
7. 결과가 closed + well-formed scope structure인지 검증
```

따라서 `21618050` 같은 경우 단순히 “h2 하나 남았다”가 아니라,

```text
AdmissibleBodyTargets(udef_q) = {h2}
```

임을 증명해야 합니다.

### 외부 scope solver는 요구하지 않습니다

v1에서 외부 solver를 새 의존성으로 넣을 이유가 없습니다.

**결정적인 local completion만 허용**하면 됩니다. 해가 여러 개여서 실제 scope resolution이 필요한 순간에는 fail-closed로 거부합니다.

이 차이가 중요합니다.

* 하나뿐인 completion을 계산 → **representation completion**
* 여러 completion 중 하나를 선택 → **semantic scope decision**

후자는 금지하고 전자만 허용합니다.

Wolfram 검증에서도 이 정의는:

```text
unique outermost BODY     → ACCEPT
ambiguous multi-scope     → REJECT
explicit constrained BODY → ACCEPT
```

를 동시에 만족했습니다. 반면 Q30.1(c)는 ambiguous multi-scope까지 ACCEPT합니다.

따라서 **(c)는 기각**합니다.

그리고 이 판정은 O1 semantic boundary 확대가 아닙니다. `BODY_resolved`의 실물 표현상 의미를 명확히 한 것입니다.

---

## Q30.2 — `multiple_card_EP_candidates`: **(a)**

현재의

> 문장에 `card` EP가 2개 이상이면 reject

는 지나치게 넓은 거부 규칙입니다.

ambiguity의 단위는 문장이 아니라 **cardinality attachment 대상인 bound variable**이어야 합니다.

따라서:

```text
for each bound variable x:
    candidates = card EPs attachable to x

    if len(candidates) == 0:
        no cardinal package for x
    elif len(candidates) == 1:
        unambiguous
    else:
        reject multiple_card_EP_candidates
```

예:

```text
three papers and two books
```

가 각각 `x1`, `x2`를 결박한다면

```text
x1 -> {card("3")}
x2 -> {card("2")}
```

이므로 ambiguity가 아닙니다.

반면

```text
x1 -> {card_A, card_B}
```

이면 reject입니다.

Wolfram으로도 `{1,1}`처럼 두 변수에 card 하나씩 존재하는 경우에는 variable-local rule만 통과시키면서, `{2}`처럼 동일 변수에 후보 두 개가 있는 경우에는 양쪽 규칙 모두 거부함을 확인했습니다.

**현재의 sentence-wide 구현은 수정 대상**입니다.

---

## Q30.3 — degree modifier → `count.rel`: **(a*)**

닫힌 사상표를 승인합니다. 다만 **predicate name만 보고 사상해서는 안 됩니다.**

사상 계약은 두 부분이어야 합니다.

```text
1. lexical/operator mapping이 등록되어 있다.
2. 해당 degree modifier가 바로 그 cardinal package에 구조적으로 attach됨이 증명된다.
```

둘 다 만족해야 합니다.

### v1 권장 최소 표

```yaml
MRS_CARDINAL_RELATION_MAP_V1:

  bare_card:
    rel: eq

  _at+least_x_deg:
    rel: ge
    require_card_attachment: true

  _more+than_p:
    rel: gt
    require_card_attachment: true
```

반면:

```yaml
_about_x_deg: REJECT
_only_x_deg:  REJECT
unknown:      REJECT
```

`_over_p`, `_under_p`는 F5 자체가 **전치사 용법 혼재**라고 보고하므로 predicate 이름만으로

```text
_over_p  -> gt
_under_p -> lt
```

를 허용해서는 안 됩니다.

구조적으로 numeric degree/card attachment임을 별도 판별할 수 있을 때에만 표에 넣는 것이 맞습니다.

즉 원칙은:

```text
recognized relation
AND
unique structural attachment to the same cardinal package
→ map

otherwise
→ unsupported_numeric_relation
```

입니다.

### `rel` 5값은 축소하지 않습니다

관측 코퍼스에서 `le`가 운동하지 않는다고 해서

```text
rel ∈ {eq, ge, le, gt, lt}
```

를 줄일 이유는 없습니다.

**표현 능력과 실험 coverage는 별개**입니다.

결과 보고에는 오히려:

```yaml
rel_coverage:
  eq: ...
  ge: ...
  gt: ...
  le: 0
  lt: ...
```

처럼 공개해야 합니다.

`le=0`이라면 “count.rel 전체를 검증했다”고 주장하지 않으면 됩니다.

---

## Q30.4 — WSJ surface: **(a)**

공개 저장소 기본 정책은:

```yaml
surface_display: sha256
```

로 판정합니다.

즉 Git에는:

```yaml
source_locator: ...
text_sha256: ...
mrs_sha256: ...
```

등만 저장하고 **WSJ 문장 원문을 넣지 않습니다.**

Gate C의 사람이 읽는 대조 작업은 로컬 material cache에서 수행하면 됩니다.

따라서 D-29의 `surface reading` 요구는 다음처럼 고치는 것이 적절합니다.

```yaml
audit_surface:
  repository_display: sha256
  local_authorized_display: full
```

`surface_display`에 호출자 명시를 강제했던 현재 구현은 좋은 방어였고, 이번 판정 후 기본값은 **`sha256`**로 두어도 됩니다.

---

## Q30.5 — Open SDP 1.2 rights: **승격 보류**

여기는 의미론 판정과 분리해야 합니다.

제출된 사실만으로는 세 표기가 존재합니다. 

```yaml
distribution_page:
  license: CC-BY-NC-SA-2.0

repository_metadata:
  license: CC-BY-NC-SA-4.0

artifact_LICENSE_txt:
  license: CC-BY-NC-SA-3.0-Unported
```

이를 하나로 정규화하면 안 됩니다.

### 정본 기록

따라서:

```yaml
license_status: AMBIGUOUS_VERSION

license_notices:
  distribution_page: CC-BY-NC-SA-2.0
  repository_metadata: CC-BY-NC-SA-4.0
  artifact_notice: CC-BY-NC-SA-3.0-Unported
```

로 세 개를 그대로 보존해야 합니다.

`canonical_license: CC-...`를 임의 지정하지 않습니다.

### NC

현재 자료만으로는 “우리 사용이 NC와 양립한다”를 판정할 수 없습니다.

그것은 최소한:

* 실제 프로젝트 이용 성격
* 서비스/배포 방식
* 조직적·상업적 맥락

등의 사실과 라이선스 해석이 필요합니다.

따라서 설계 상태는:

```yaml
nc_compatibility: UNRESOLVED
```

입니다.

### SA

마찬가지로 MRS를 adapter로 변환한 IR이나 manifest가 라이선스상 Adapted Material인지, 또는 단순한 사실/분석 결과인지 여부는 **semantic compiler 설계가 결정할 수 있는 문제가 아닙니다.**

따라서:

```yaml
sa_propagation_to_adapter_output: UNRESOLVED
```

입니다.

### 결과적으로 Open SDP 상태

두 층으로 구분해야 합니다.

```yaml
OpenSDP_1_2:
  acquisition_source: APPROVED
  technical_qualification_candidate: APPROVED
  repository_redistribution: NOT_APPROVED
  O1_APPROVED_SOURCE: NOT_YET
  rights_gate: BLOCKED
```

즉 **로컬에서 파싱·qualification·adapter 시험을 계속하는 것은 가능**하지만, D-29가 요구한 “실제 component/item rights 확인”이 완료됐다고 간주해서 `APPROVED_SOURCE`로 승격해서는 안 됩니다.

Wolfram 형식화에서도 semantic/material gate가 모두 true여도

```text
rightsResolved = False
```

이면 전체 freeze 조건은 `False`였습니다.

---

## Q30.6 — `generic_entity`: **(a*) 적격**

`20214052`:

> `Most are trim.`

을 proportional fixture로 인정합니다.

이유는 현재 O1ScopeMatch 계약에서 **restriction predicate의 lexical identity가 scoring target이 아니기 때문**입니다.

측정 대상이:

```text
prop
├── restriction
└── body
```

라는 구조이고, restriction 내부 predicate label이 projection에서 익명화된다면 subject가 `generic_entity`라는 ERG 내부 어휘를 맞출 필요는 없습니다.

즉 평가가 실제로 묻는 것은:

> “`most`의 restriction domain을 나타내는 구조적 노드가 존재하는가?”

이지

> “ERG의 `generic_entity`라는 이름을 알고 있는가?”

가 아닙니다.

Wolfram에서도 다음 조건을 형식화하면 해당 fixture가 적격입니다.

```text
surface signals proportional quantification = true
restriction node structurally required       = true
lexical restriction identity scored          = false
generic restriction exists                   = true
```

### 단, 사전 계약 하나는 필요합니다

fixture 특례가 아니라 일반 규칙으로:

```yaml
implicit_restriction_policy:
  restriction_structure_scored: true
  restriction_lexical_identity_scored: false
```

를 freeze해야 합니다.

subject IR에서는 어떤 anonymous/generic predicate를 사용하든 projection 결과가 동일해야 합니다.

이 조건이 성립한다면 이 1건은 **비례 ≥1 하한을 형식적으로 충족할 수 있습니다.**

단, 이것이 전체 source qualification을 즉시 통과시킨다는 뜻은 아닙니다. adapter/attachment/rights/control gates가 별도입니다.

그리고 단지 quota를 채우기 위해 440개 multi-quantifier `_most_q`로 범위를 넓히는 Q30.6(c)는 필요하지 않습니다.

---

## Q30.7 — control surface vocabulary: **갱신 승인**

현재 상태:

```text
declared subject dialect: prop 포함
control lexicon: most = unsupported
```

는 계약 내부 모순입니다.

또:

```text
declared subject dialect: count 포함
control lexicon: cardinal = unclassified
```

이면 cardinal fixture를 적격 스캐너가 원천적으로 찾지 못합니다.

Wolfram 형식화에서도 두 상태 모두 declared dialect와 불일치했습니다.

따라서 D-27 control 계약의 **명시적 개정**을 승인합니다.

### `most`

```diff
UNSUPPORTED:
- most

SUPPORTED:
+ most -> prop(rel=most)
```

### cardinal

`two`, `three`, `five`를 단순 정적 단어 목록에 계속 추가하는 방식은 권하지 않습니다.

다음과 같은 semantic lexical class가 맞습니다.

```yaml
SUPPORTED_CARDINAL_EXPRESSION:
  require:
    integer_parseable: true
    numeric_value_in_IR_range: true
    recognized_as_cardinal_use: true
  maps_to:
    operator: count
```

즉:

```text
three
twenty
twenty-one
3
```

같은 표현을 deterministic integer parser가 인정하는 경우 `count` 후보로 분류합니다.

`about three`, `at least three` 등의 relation은 Q30.3의 별도 operator/attachment 규칙이 처리합니다.

이를 예를 들어:

```yaml
CONTROL_SURFACE_PROFILE_V2
```

로 버전화하고 hash-pin한 뒤 **fixture eligibility scan을 다시 실행**해야 합니다.

기존 surface filter 결과는 count/prop 재료 적격성 판단에는 더 이상 정본이 아닙니다.

---

# Freeze 상태

이번 판정 후에도 **full O1 V5를 바로 재동결하면 안 됩니다.**

이유는 의미론 쪽보다 권리 gate입니다.

권장 상태는:

```yaml
D_E2E_v1_30:

  Q30_1:
    decision: A_STAR
    BODY_resolved:
      definition: unique_admissible_body_target
      criterion: cardinality == 1
      raw_remaining_label_count_is_definition: false
      external_scope_solver_required: false
      ambiguous_completion: REJECT

  Q30_2:
    decision: A
    multiple_card_EP_candidates:
      scope: per_bound_variable
      independent_cardinals_allowed: true

  Q30_3:
    decision: A_STAR
    mapping_policy: closed_fail_closed_table
    structural_attachment_required: true
    unknown_modifier: REJECT
    about: REJECT
    only: REJECT
    over_under:
      lexical_name_alone_sufficient: false
    unexercised_rel_values_remain_in_IR: true

  Q30_4:
    decision: A
    repository_surface_default: sha256
    verbatim_WSJ_commit: false

  Q30_5:
    acquisition_source: APPROVED
    O1_source_promotion: BLOCKED
    license_version: UNRESOLVED
    nc_compatibility: UNRESOLVED
    sa_propagation: UNRESOLVED
    rights_gate: BLOCKED

  Q30_6:
    decision: A_STAR
    generic_entity_fixture: ELIGIBLE
    restriction_structure_scored: true
    restriction_lexical_identity_scored: false

  Q30_7:
    control_contract_update: APPROVED
    most: SUPPORTED_PROP
    cardinal:
      policy: deterministic_integer_cardinal_class
    profile_version_bump: required
    rescan_before_freeze: required

  full_O1_freeze:
    status: BLOCKED
    principal_remaining_blocker: rights_gate
```

한 가지 운영상 중요한 점은, F4의 **16,584 attachment**를 곧바로 “16,584개의 적격 fixture”라고 승격해서는 안 된다는 것입니다. Q30.1·Q30.2·Q30.3·Q30.7의 새 계약으로 전체 코퍼스를 다시 fail-closed scan한 뒤 **record 단위 최종 eligible count**를 새로 산출해야 합니다.

따라서 다음 상태 전이는:

```text
D-30 계약 반영
    ↓
adapter / attachment regression 재자격
    ↓
CONTROL_SURFACE_PROFILE_V2로 전체 재스캔
    ↓
cardinal ≥ 3 / proportional ≥ 1 확인
    ↓
rights gate 별도 해결
    ↓
그 뒤에만 V5 freeze
```

가 맞습니다.

이번 실측이 보여준 것은 MRS source가 원리적으로 부적격이라는 것이 아니라, **D-29의 `BODY_resolved`가 MRS의 실제 underspecification 관례에 대해 충분히 정의되지 않았다는 것**입니다. 유일 completion만 허용하는 이번 판정은 그 공백을 메우면서도 multi-scope ambiguity를 계속 fail-closed로 유지합니다.

<!-- VERBATIM-END -->

---

# B. 운영 세션 수신 검증 (2026-08-24)

`VERBATIM_SHA256: 05fceca20ec2ae207bec7b9c6436c11d2af089adb2322f16c0243f8169b3c21d`
(BEGIN 다음 개행 ~ END 직전, UTF-8. verbatim 604행)

## B.0 검증 설계

이 판정은 **우리 실측을 근거로 우리 계약을 고치라**고 명한다. 따라서 검증의
초점은 "판정이 옳은가"가 아니라 **"판정의 정의를 실물에 적용하면 판정이
예측한 대로 동작하는가"** 다. 예측이 어긋나면 그것이 보고 대상이다.

| 축 | 판정의 검증 가능한 예측 | 우리 검증 수단 |
|---|---|---|
| V1 | 7문항 전부 응답, 선행 판정과 무충돌 | 요청서·D-29 대조 |
| V2 | unique outermost BODY → ACCEPT / ambiguous multi-scope → REJECT / explicit constrained BODY → ACCEPT | admissible-target 시제품을 실물 4건에 적용 |
| V3 | 문장 규칙은 독립 기수를 오탐 거부한다 | 전 코퍼스에서 `card≥2` 분해 |
| V4 | `restriction_lexical_identity_scored: false`가 성립해야 Q30.6이 가능 | 투영에 `generic_entity` vs 다른 라벨 투입 |
| V5 | 새 계약으로 재스캔해야 record 단위 적격 수가 나온다(16,584 승격 금지) | 시제품 재스캔 |

## B.1 V1 — 응답 완전성·무충돌: **CONFIRMED**

Q30.1~Q30.7 전부 판정됐다. 선행 판정과의 관계도 정합한다:
- D-29 `BODY_resolved`를 **폐기하지 않고 정의를 부여**했다 — boundary 확대가
  아니라 미정의 공백의 충전이라는 판정의 자기 서술이 우리 관측과 일치한다.
- D-25의 "실패가 예정된 계약 금지"와 정합: 0건을 내던 문면이 고쳐졌다.
- D-27 control 계약의 **명시적 개정**으로 처리했다 — 운영 세션이 임의로
  고치지 않고 상신한 것(§F8)이 옳은 경로였음이 확인됐다.
- Q30.6(c)(440건으로 범위 확대)를 **불필요**로 기각했다 — 우리가 권고하지
  않은 선택지이고, quota 목적의 확대를 금지한 것은 P19 규율과 같은 방향이다.

## B.2 V2 — admissible BODY target: **3/3 예측 적중**

시제품(판정 §Q30.1의 7단계: RSTR 해소 → 제한식 내부·비후보 label 제거 →
다른 양화의 RSTR target 제거 → 후보 계산)을 실물에 적용:

| item | 표면 | 결과 | admissible set |
|---|---|---|---|
| `21618050` | Two ironies intrude. | **RESOLVED** | `{h2}` |
| `20214052` | Most are trim. | **RESOLVED** | `{h2}` |
| `20725062` | Five were interested. | **RESOLVED** | `{h2}` |
| `21438006` | Three companies began trading over the counter. | **REJECT** | `{h12,h17,h2}` (양화 2개) |

**판정이 §Q30.1에 적은 `AdmissibleBodyTargets(udef_q) = {h2}`가 정확히
재현됐다.** 그리고 다중 양화는 계속 fail-closed로 거부된다 — 판정이 (c)를
기각한 이유(ambiguous multi-scope까지 ACCEPT)가 실물에서 확인된다.

명시 제약 경로도 검증했다: `21618050`의 BODY에 `QEQ h2`를 인위로 추가하면
`explicit` 경로로 `{h2}` → RESOLVED. **세 예측 전부 성립.**

주의로 기록: 조사가 찾아온 기수 3건 중 `21438006`은 이 정의에서 **탈락**한다
(over the counter의 `_the_q`가 두 번째 양화다). 회신의 locator가 곧 적격이
아니라는 점이 다시 확인된다.

## B.3 V3 — 문장 단위 규칙의 오탐 규모: **CONFIRMED, 7,669건**

`card` EP가 2개 이상인 record를 분해:

| 상태 | 건수 | 문장 규칙(현 구현) | 변수 규칙(판정) |
|---|---:|---|---|
| card 전부가 **서로 다른 변수** | **7,669** | 거부(오탐) | 허용 |
| **같은 변수**에 후보 2개 이상 | **86** | 거부 | 거부 |

**7,669 + 86 = 7,755** — §B.11의 `multiple_card_EP_candidates` 거부 수와
정확히 일치한다. 즉 그 버킷의 **98.9%가 오탐**이었다. 판정 Q30.2(a)가
정당하고, 내가 §F7에서 드러내 둔 선택이 실제로 그만큼을 좌우했다.

## B.4 V4 — `restriction_lexical_identity_scored: false`: **이미 성립**

투영 실측: `prop(most, x, generic_entity(x), trim(x))`와
`prop(most, x, thing(x), trim(x))`의 signature가 **동일**하고,
제한식 노드 자체를 없애면 **다르다**. 즉 판정이 Q30.6의 전제로 요구한
계약이 우리 투영에서 **이미 참**이다 — 새로 만들 것이 아니라 **명시적
계약으로 동결**하고 테스트로 결박하면 된다(구현 항목).

## B.5 V5 — 새 계약 하 잠정 재스캔: 하한이 **충족된다**

판정의 지시대로 16,584을 적격으로 승격하지 않고, 새 정의로 record 단위
재스캔했다. **아래는 시제품(계약 결박 전) 측정이므로 잠정값이다** —
계약 구현 후 재산출이 정본이다(판정 §Freeze 상태의 요구).

| 항목 | 잠정값 |
|---|---|
| **기수 적격** | **11건** (하한 3 **충족**) |
| **비례 적격** | **1건** (`20214052`, 하한 1 **충족**) |
| 거부: BODY 미해소/모호 | 16,576 |
| 거부: CARG 비정수 | 8,464 |
| 거부: 결박 양화 불일치 | 4,606 |
| 거부: 같은 변수 다중 card | 87 |

판정 Q30.3이 공개를 요구한 `rel_coverage`(잠정):

```yaml
rel_coverage:
  eq: 11
  ge: 0
  gt: 0
  le: 0
  lt: 0
```

**즉 `ge`/`gt` 재료는 156건이 존재하지만 전체 게이트를 통과하지 못한다.**
따라서 "`count.rel` 전체를 검증했다"고 주장할 수 없다 — 판정이 명한
공개 방식 그대로 기록한다.

## B.6 이 판정이 바꾸는 것 (구현 항목)

1. `_stage2_mrs_count_projection.py` — `BODY_resolved`를 admissible-target
   유일성으로, `multiple_card`를 변수 단위로. **현재 계약 테스트 14건 중
   실물 거부를 보존하던 2건은 이제 뒤집어야 한다**(판정이 왔으므로 그 뒤집기가
   정당한 변경이다 — 그 테스트의 docstring이 그렇게 예고해 뒀다).
2. `MRS_CARDINAL_RELATION_MAP_V1` 신설 — `bare_card→eq`,
   `_at+least_x_deg→ge`, `_more+than_p→gt` + **구조적 attachment 증명 요구**.
   `_about_x_deg`·`_only_x_deg`·`_over_p`·`_under_p`·unknown은 REJECT.
3. `implicit_restriction_policy` 동결 + 음성 테스트(라벨을 바꿔도 동일,
   노드를 없애면 다름).
4. `CONTROL_SURFACE_PROFILE_V2` — `most`를 SUPPORTED(→`prop`),
   기수는 **결정적 정수 표현 클래스**(열거 아님). 버전·해시 고정 후 재스캔.
5. Gate C `surface_display` 기본값을 `sha256`으로. `audit_surface`
   2층(repository / local_authorized) 반영.
6. Open SDP 권리 상태를 **3표기 보존**으로 기록(`license_status:
   AMBIGUOUS_VERSION`), `canonical_license` 지정 금지.
   `rights_gate: BLOCKED`가 freeze 조건에 들어간다.

## B.7 한계

- B.5는 **시제품 측정**이다. `admissible_body_targets`가 계약으로 결박되지
  않았고(테스트 0건), 판정 §Q30.1의 7단계 중 "scope topology와 모순되는
  후보 제거"를 내가 근사했다(다른 양화의 RSTR target 제외로). 정본 수치는
  계약 구현 후에 나온다 — **11건·1건을 적격 fixture로 확정하지 마라.**
- Q30.3의 구조적 attachment 증명을 B.5에서는 **술어 존재 여부로 근사**했다.
  정본 구현은 attachment를 구조로 판정해야 하므로 `ge`/`gt` 수가 바뀔 수 있다.
- rights gate(NC·SA·라이선스 버전)는 **설계로 해소되지 않는다** — 판정이
  UNRESOLVED로 둔 세 항목은 사실 확인과 법적 해석이 필요하다. full O1
  freeze의 주 차단 요인이 의미론에서 **권리로 이동**했다.
