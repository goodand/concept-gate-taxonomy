# DESIGN DECISION — D-E2E-v1-38 (프로파일 개정: 새 identity + 서명 본체의 profile commitment)

- 사슬 항법: 이전 [[DESIGN_DECISION_r4_source_equivalence|D-37]] · **D-38** · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-09-01 · 발신: 외부 설계 담당(저장소 접근 없음, Wolfram 검증 명시)
- 요청 문서: [[DESIGN_REQUEST_certification_profile_amendment|Q38]]
- 상태: **동결.** 이 문서는 판정 기록이다. 우리 실측이 이 판정을 소급 수정하지
  못한다. 변경이 필요하면 새 요청서로 올린다.
- `VERBATIM_SHA256`: `7fd7e3a1cc48df83724bda6667ac879abc60713dc4cbcceda833cc3f1f32e3a8`
  (끝 개행 제외, D-30 이후 규약)

## 판정 요지 (한 줄씩)

| 질문 | 판정 |
|---|---|
| ㄱ `_v0` 제자리 확장 vs `_v1` 신설 | **NEW_PROFILE_IDENTITY_PREFERRED** — 제자리 확장은 논리적으로 가능하나 **계약 안전하지 않다**(v0의 역사적 의미를 보존해야 한다면). `_v1`은 논리적 필연이 아니라 **감사 계약 요구** |
| ㄴ 서명 본체에 `profile` | **독립 검증에 필요하다 = 예.** 허용 형태 `profile_id` 또는 `profile_id + required_hash`. schema bump는 논리적 자동은 아니나 **서명 payload shape이 바뀌면 필요** |
| ㄷ MCP 호출 = 실험 관측 | **아니다.** 제품 계약 사용은 별개 상태. 단 제품 계약 변경에 **별도 backward-compatibility 규칙이 필요하다는 근거**는 된다 |
| 금지 3종 | `operational_patch` · `immediate_projection` · `dispatch` 모두 **unchanged** |

---

VERBATIM-BEGIN
## Q38 판정

Wolfram으로 Q38의 핵심 논리 구조를 별도로 확인했다.

### 결론

**ㄱ은 조건부로 갈린다. ㄴ은 사실상 “예”이며, ㄷ은 “아니오”에 가깝다.**

정확히는:

1. **`required` 추가 자체는 `_v0` 제자리 확장도 논리적으로 가능하고 `_v1` 신설도 가능하다.**
   그러나 **이미 배포된 profile의 계약 의미를 보존해야 한다면 `_v0`를 제자리에서 재정의해서는 안 되고, 새 profile identity가 필요하다.**
2. **`profile` 또는 그것과 동등한 profile commitment를 서명 본체에 넣어야 한다.** 그렇지 않으면 서명된 결과만으로는 어떤 인증 계약이 적용됐는지 독립적으로 판별할 수 없다.
3. **MCP 호출 이력은 실험의 `confirmatory_outcomes_observed`와 동일시할 수 없다.** 제품 계약이 실제로 호출됐다는 사실과 실험 모집단의 관측은 다른 상태다. 다만 **제품 계약 변경에 별도의 backward-compatibility/amendment 규칙이 필요하다는 근거**는 된다.

---

## ㄱ. `_v0` 제자리 확장인가, `_v1`인가

여기서 먼저 중요한 논리적 사실이 있다.

현재 required set을 `C₀`, 새 의무를 `p`라고 하면

```text
C₁ = C₀ ∪ {p}
```

이고 인증 조건은

```text
Certified(C,V) = 모든 c ∈ C에 대해 V(c)=PASS
```

이다.

그러므로:

```text
Certified(C₁,V) ⇒ Certified(C₀,V)
```

는 참이지만,

```text
Certified(C₀,V) ⇒ Certified(C₁,V)
```

는 일반적으로 거짓이다.

즉 새 의무를 추가하면 **인증 가능 집합이 단조롭게 줄어든다.**

따라서 `legacy_relation_claim_v0`의 의미를 실제로 바꾸면서도 이름을 그대로 유지하면:

```text
profile_id = legacy_relation_claim_v0
        │
        ├─ 과거: C₀
        └─ 현재: C₁
```

가 된다.

그러면 profile ID만 보고서는 동일한 인증 결과가 **어떤 계약 아래에서 나온 것인지** 구별할 수 없다.

### 따라서 판정

**새 profile identity를 만드는 쪽이 원칙적으로 맞다.**

예:

```text
legacy_relation_claim_v0
        ↓ 보존
legacy_relation_claim_v1
        ↓
C₀ + claim.evidence_provenance
```

다만 이것은 **수학적 필연성**은 아니다. 같은 ID를 유지하면서 별도 유효기간·revision·amendment registry를 엄격히 관리하는 시스템도 논리적으로 만들 수 있다.

따라서 정확한 표현은:

> **`_v1`은 required-set 변경이라는 사실에서 논리적으로 강제되는 것이 아니라, 배포된 계약의 역사적 의미를 보존하고 독립적인 재현·감사를 가능하게 하려면 필요한 식별 수단이다.**

이 프로젝트의 선례(D-32)가 요구한 `_v1` 신설은 이 의미에서 **정책/계약 요구**로 정당화된다.

---

## ㄴ. `profile`을 서명 본체에 넣어야 하는가

여기는 훨씬 강하다.

현재 서명 본체가 대략

```text
schema
issuer
subject_fingerprint
graph_revision
results[]
```

이고 `profile`이 서명 밖이라면, 동일한 `results[]`를 가진 두 문서를 생각할 수 있다.

```text
Certificate A
  profile = C₀
  results = R

Certificate B
  profile = C₁
  results = R
```

서명되는 바이트가 profile을 포함하지 않는다면 **A와 B의 signed payload가 동일할 수 있다.**

따라서 verifier는 서명 자체로

```text
R was evaluated under C₀
```

인지

```text
R was evaluated under C₁
```

인지 증명할 수 없다.

이것은 단순한 표시 문제보다 심각하다. **인증 결과의 의미를 정의하는 계약이 서명된 증거와 분리되어 있기 때문이다.**

### 필요한 형태

최소한 다음 중 하나가 서명 대상에 들어가야 한다.

```text
profile_id
```

또는 더 강하게:

```text
profile_id
profile_required_hash
```

후자가 특히 유용하다.

```text
profile_id = legacy_relation_claim_v1
required_hash = H(required obligations)
```

그러면 verifier가

```text
signed certificate
      ↓
profile identity
      ↓
exact required-set
```

를 재구성할 수 있다.

### schema version은?

**profile commitment를 추가한다고 해서 논리적으로 반드시 certificate schema v2가 되는 것은 아니다.**

하지만 현재 `obligation_certificate_v1`의 **서명 payload 정의 자체가 바뀐다면**, 기존 v1과 새로운 payload를 동일 schema라고 부르는 것은 위험하다.

따라서 이 저장소의 기존 선례까지 적용하면:

```text
obligation_certificate_v1
        ↓ signed-body shape 변경
obligation_certificate_v2
```

가 가장 방어 가능한 처분이다.

핵심은:

> **profile version과 certificate schema version은 서로 다른 축이다.**

```text
profile version
= 어떤 의무를 요구했는가

certificate schema version
= 그 사실을 서명 데이터에 어떤 구조로 표현하는가
```

새 profile만 만든다고 certificate schema가 자동으로 바뀌는 것은 아니고, 반대로 profile commitment를 서명 구조에 새로 넣는다면 schema 개정이 필요해진다.

---

## ㄷ. MCP 호출 = 실험 관측인가?

**아니다.**

Q38의 가장 중요한 구분이다.

실험의

```text
cohort_execution_started
confirmatory_outcomes_observed
dispatch
```

는 특정 **실험 모집단에 대한 관측 상태**다.

반면 MCP 호출은

```text
production/client interaction
```

이라는 제품 운영 상태다.

둘은 다음처럼 별개의 축으로 두는 것이 맞다.

| 상태                    | 의미                  |
| --------------------- | ------------------- |
| MCP가 배포됨              | 계약이 외부에 노출됨         |
| MCP가 호출됨              | 제품 계약이 실제 사용됨       |
| certification 결과가 생성됨 | 특정 입력에 대해 계약이 적용됨   |
| experiment dispatch   | 동결된 실험 모집단에 관측이 발생함 |
| confirmatory outcome  | 실험 결과가 관측됨          |

따라서

```text
MCP call > 0
```

이라고 해서

```text
confirmatory_outcomes_observed = true
```

라고 할 수 없다.

반대로 현재 제공된 실측에서

```text
production wiring = 0 calls
stored certificates = 0
experiment dispatch = 0
```

라면 **현재 제품 계약 변경에 실질적 사용자 결과가 누적되지 않았다는 별도 사실**은 있다.

하지만 이것을 실험 amendment prerequisite에 그대로 대입해서는 안 된다.

---

# 최종 판정안

```yaml
Q38:

  question_a:
    decision: NEW_PROFILE_IDENTITY_PREFERRED
    legacy_v0_in_place_expansion:
      logically_possible: true
      contract_safe: false
        # if v0's historical meaning must remain stable
    v1_required:
      logical_necessity: false
      audit_contract_requirement: true

  question_b:
    profile_commitment_in_signed_body:
      required_for_independent_verification: true
    acceptable_forms:
      - profile_id
      - profile_id_plus_required_hash
    certificate_schema_bump:
      logically_automatic: false
      required_if_signed_payload_shape_changes: true

  question_c:
    mcp_call_equals_experimental_observation: false
    production_contract_usage:
      distinct_state: true
    experiment_freeze_prerequisite:
      transferable_without_explicit_rule: false

  operational_patch:
    forbidden: unchanged

  immediate_projection:
    forbidden: unchanged

  dispatch:
    blocked: unchanged
```

### 한 문장

**Q38에서 새 의무의 추가는 단순히 `required += 1`인 내부 구현 문제가 아니라, “어떤 계약으로 인증했는가”의 역사성을 보존해야 하는 문제이므로 새 profile identity가 적절하고, 그 profile identity(또는 동등한 commitment)는 인증서의 서명 본체에 들어가야 하며, MCP 사용 이력은 실험의 관측 상태와 별개의 제품 생명주기 상태로 취급해야 합니다.**
VERBATIM-END

---

# 운영 세션의 수신 검증 (2026-09-01)

프로토콜 4단계를 전수 진행했다: **검증 설계 → 설계의 적대적 검증 → 검증 →
저장.** D-37 수신 때 2단계를 건너뛴 것이 사용자 지시로 기본값이 된 계기였고,
이번에는 밟았다.

## 1. 검증 설계 (8항목)

판정이 우리 주장을 어떻게 다뤘는지부터 항목화했다 — 판정이 우리 진단을
**넘어선** 곳이 둘 있었다:

| 우리가 쓴 것 | 판정 | 검증 결과 |
|---|---|---|
| 상신서 §3.5 “인증은 저장 안 되는 view라 ‘발급된 인증서의 지위’ 문항 자체가 **부정확**했다”(`:183`) | ㄴ이 그 관점을 **넘어섰다** — 저장 여부가 아니라 **서명 payload 동일성**이 문제 | **우리 진단이 과소 진술이었다.** V3 참조 |
| 질문 ㄷ “상응한다면 이미 관측 후이므로 제자리 확장이 봉쇄된다”(`:253`) | **아니오** — 우리 우려를 완화 | 우리에게 유리한 방향이라 적대검증이 엄격화를 요구했고, V6에서 실제로 정정이 나왔다 |

## 2. 설계의 적대적 검증 — 채택 4 · 부분 기각 1

| 지적 | 판정 |
|---|---|
| **#3 `required_hash` 정의 부재로 V4가 “가능한가”만 본다** | **채택.** 구체 정의로 재구성했다(V4) |
| **#1 prerequisites 사실 축 검증 항목이 없다** | **채택.** V8에 조건 성립 여부 재료를 넣었다 |
| **#4·#6 “production 배선 0건”이 오독을 부른다** | **채택 — 실제 정정을 낳았다**(V6) |
| #7·#8 V7b·V8은 판정 미도착이라 실행 불가 | **범위 재분류.** 검증자에게 판정문을 주지 않은 것은 내 프롬프트의 결함이다. 판정은 도착해 있어 둘 다 실행했다 |
| **#2·#5·(D) “V3 구성 불가 — `issue_claim_certificate`가 profile을 안 받는다” = blocker** | **부분 기각.** 함수 사실은 맞으나 **다른 함수를 봤다** — `certify_relation_claims`가 `profile` 인자를 받는다(실측). V3은 그 경로로 구성 가능했고, 실제로 구성해 판정 ㄴ의 논거를 **확증**했다 |

## 3. 검증 결과

| # | 항목 | 결과 |
|---|---|---|
| **V1·V2** | 단조 축소 `Certified(C₁)⇒Certified(C₀)` | **판정 기초 확증.** 판정 집합 **2⁷=128 전수**에서 정방향 반례 **0건**, 역방향 반례 **1건**(provenance만 UNKNOWN) |
| **V3** | 서명 payload 동일성 — 판정 ㄴ의 결정적 논거 | **확증, 판정보다 강하다.** 같은 입력을 `profile=C₀`·`C₁`로 인증하니 인증서 payload가 **바이트 동일**(양쪽 sha256 `e5f9ff2796a271f8`). 판정은 “동일할 수 **있다**”고 했는데 우리 구현에서는 **항상 동일**하다 — 그 payload에는 `signature` 필드조차 없다(`anchoring_certificate`는 무서명) |
| **V4** | `required_hash` 구제 경로 | **가능.** 정의를 못박아 실측: `sha256(canonical_json({profile_id, sorted(required)}))` → C₀ `bf454234…` / C₁ `bda594b6…` **구별됨**, 그리고 required 순서를 뒤집어도 **불변**(정렬 덕) |
| **V5** | schema bump 필요 조건 | **필요.** 서명 본체 최상위는 `schema·issuer·subject_fingerprint·graph_revision·results`이고 08-31 `v0→v1` 개정이 바꾼 것은 `results` 행에 `invariant` 추가였다. profile 추가도 **같은 종류의 shape 변경**이다 |
| **V6** | 배선 범위 | **정정 발생.** 인증 경로는 **배포돼 있다** — MCP tool 13종, `issue_claim_certificate` 호출 5곳, `certify_relation_claims` 1곳. 상신서 §5 G의 “production 호출 0건”은 **새 의무(`resolve_cited_evidence`)에만** 해당(실측 0건)이고, 인증 자체는 배포·호출 가능하다. 판정 ㄷ의 결론은 이 수치에 의존하지 않아 **그대로 유효**하나, 우리 표현은 오독을 부를 수 있었다 |
| **V7a** | 우리 문서 자기 서술 | 위 §1 표의 인용 3건 모두 원문 일치(`:183` `:253` `:267`) |
| **V8** | 판정이 답하지 않은 것 | 질문 ㄱ의 “(c) 조건은 무엇인가”에 판정은 조건을 **명시했다** — “v0의 역사적 의미를 보존해야 한다면”. 그러나 **그 조건이 우리 경우 성립하는지는 판정이 정하지 않았고, 우리 재료가 서로 다른 방향을 가리킨다**: 저장된 인증서 **0건**(보존할 역사가 없다) vs **배포된 MCP tool 13종**(계약문이 이미 외부에 노출됐다). 이 판단이 다음 작업의 입력이다 |

## 4. 이 판정이 명령하는 것 — 실행 전 상태

아직 **아무 것도 실행하지 않았다**(코드 변경 0). 판정이 요구하는 처분은 셋이고
서로 결박돼 있다:

1. `legacy_relation_claim_v1` 신설(`_v0` 보존) — ㄱ
2. 서명 본체에 `profile_id`(+`required_hash`) 추가 — ㄴ
3. 그 결과 `CERTIFICATE_SCHEMA` → `obligation_certificate_v2` — ㄴ + V5

**V8의 미결 판단이 1의 전제**이므로 그것을 먼저 정해야 한다. 그리고 3은 서명
형식 변경이라 기존 인증서 검증 경로를 건드린다 — `test_obligation_invariant_fqn.py`
가 08-31 개정 때 세운 계약들이 그 회귀를 지킬 것이다.
