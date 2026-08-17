# DESIGN DECISION — H1a verification load-bearing (D-H1a-17)

- 수신: 2026-08-17
- 도착 경로: 사용자가 `correspondence/DESIGN_REQUEST_H1a_verification_load_bearing.md`
  (Q17)를 외부 설계 담당에게 공유하고 회신을 전달
- 판정 ID: 판정문 자신이 `D-H1a-17`로 표기
- 구속력: **있음.** D-H1a-1~16과 같은 외부 판정 채널
- **D-H1a-16과의 관계: 무효화가 아니라 적용 범위 한정(scope_narrowed)**

> ⚠️ **§1이 판정문 원문이다. 편집하지 말 것.** §2는 수신 세션의 실측 메모이며
> **판정의 일부가 아니다.**

---

# 1. 판정문 원문 (verbatim)

Wolfram MCP로 이번 입력을 **"정책 DSL 커버리지 문제"가 아니라 "검증 의무의
한계효용 문제"**로 추상화해 다시 검증했습니다. 결론은 **Q17=B**가 가장
일관됩니다. 세 의미 조건은 인과적으로 중요하지만, **그 조건을 추가로
canonical DSL에 복제해서 기계 인증하는 의무까지 인과적으로 load-bearing한
것은 아닙니다.**

## Q17: B — load-bearing 판별 기준을 도입하고, 비-load-bearing canonicalization은 freeze blocker에서 제외

### 1. Wolfram이 확인한 핵심 구분

S_i = 인과 식별에 필요한 의미 명제
C_i = 그 의미를 canonical DSL/compiler가 추가 인증함

```text
SemanticPreconditionCanBeLoadBearing = True
CanonicalizationCanBeLoadBearingInGeneral = True
CanonicalizationNotLoadBearingWhenIndependentEvidenceAlreadySuffices = True
```

두 명제가 동시에 참입니다.

> **"default permission이 실제로 적용된다"는 사실은 load-bearing일 수 있다.**

그러나:

> **"그 사실을 semantic compiler가 canonical expected graph와 비교해야 한다"는
> 특정 검증 방식은 load-bearing이 아닐 수 있다.**

이것이 Q16에서 빠졌던 구분입니다.

### 2. load-bearing 판별 기준

검증 의무 V를 제거했을 때 다음 반례 세계가 생길 수 있으면 causal-load-bearing
으로 분류합니다.

```text
OtherConditions ∧ ¬V ∧ SystemAcceptsCausalClaim ∧ ¬CausalIdentification
```

쉽게 말하면: **그 검사를 빼면 잘못된 인과 결론을 통과시킬 수 있는가?**

반대로 검사를 제거해도 이미 다른 독립 경로가 동일 의미 명제를 충분한
assurance로 확정하고 있어서 `AcceptedWorlds(+V) = AcceptedWorlds(−V)`라면 그
추가 검사는 **audit automation / redundancy**입니다.

### 3. 세 항목은 두 층으로 분류해야 한다

| 항목 | **의미 명제 자체** | **추가 canonicalization 의무** |
|---|---|---|
| `conflict_to_defer_mapping` | causal load-bearing | 현 증거 아래 audit automation |
| `recorded_field_access` | causal load-bearing | 현 증거 아래 audit automation |
| `default_permission_applicability` | causal load-bearing | 현 증거 아래 audit automation |

licensed-path 모델 `L = D ∧ R ∧ ¬H`에서 각 항을 제거했을 때 identification
조건이 바뀌는 반례가 존재하는지 검사한 결과:

```text
ConflictSemanticNecessary          = True
RecordedFieldSemanticNecessary     = True
DefaultPermissionSemanticNecessary = True
```

따라서 **세 의미를 검사하지 않아도 된다는 결론은 아닙니다.** 바뀌는 것은
검증하는 방법입니다.

### 4. 왜 Q17=B인가

요청서에 따르면 세 의미 명제는 canonical compiler 외에도 이미 확인돼
있습니다. `default_permission_applicability`는 특히 `assert_4`, `assert_9`,
arm-diff 검증, 독립 리뷰어들이 같은 결론에 도달했습니다.

이를 `existingEvidence=True`로 놓고 canonical coverage를 켰다 껐다 한 결과:

```text
AllExistingIndependentEvidenceAssumedSufficient_
NewCanonicalCoverageChangesCertification = False
```

Q16의 질문("canonical counterpart가 없으면 어떻게 메울까")보다 먼저 물어야
했던 질문은 **"그 counterpart가 없으면 인과적으로 잘못된 세계가 새로
통과하는가"**였고, 답은 **아니오**입니다.

### 5. `target-critical`을 둘로 쪼개야 한다

```yaml
criticality:
  causal_semantic_critical:    # 이 의미가 거짓이면 causal identification이 깨짐
  canonical_audit_critical:    # canonical DSL→compiler 경로로도 인증해야 함
```

세 항목의 현재 상태는 `causal_semantic_critical: true`,
`canonical_audit_critical: false`입니다. 단, 두 번째가 false인 이유는
canonicalization이 쓸모없어서가 아니라 **이미 독립 검증 경로가 존재하기
때문**입니다. 그 경로를 제거하면 다시 true가 될 수 있습니다.

### 6. 일반화된 판별 규칙

| 질문 | Yes이면 |
|---|---|
| 이 의미 명제가 틀리면 estimand/causal attribution이 깨지는가? | `causal_semantic_critical` |
| 현재 이 검증 방식을 제거하면 그 오류를 막을 독립 경로가 없어지는가? | 해당 verification도 load-bearing |
| 검증 방식을 제거해도 동일 의미가 독립적으로 충분히 확인되는가? | audit/redundancy |

이렇게 하면 **"정책이 중요한가?"와 "정책을 compiler가 인증하는 것이
중요한가?"를 혼동하지 않습니다.**

## Q17.1 — 실사용/제품 재사용 관점

| 장치 | 제품 재사용 가능성 | 판단 |
|---|---|---|
| typed policy/obligation graph | 높음 | 실제 MCP feedback contract에 직접 재사용 가능 |
| fail-closed `unknown` 처리 | 높음 | deterministic laundering 방지에 직접 유용 |
| semantic graph diff | 중~높음 | 모델 대면 contract drift 검사 가능 |
| mutation framework | 높음 | 제품 validator의 negative coverage 테스트로 재사용 |
| 특정 H1a mutation fixture | 낮음 | 실험 전용 |
| QF-SELECT/QF-DEFER capability controls | 낮음 | 거의 실험 전용 |
| H1a `conflict_to_defer` 감사 | 중간 이하 | 제품 contract에 같은 결정 구조가 있을 때만 |

```text
Reusable verification kernel  ≠  H1a-specific verification policy
```

제품 자산으로 보존할 가치가 높은 것은
`typed obligation → semantic claim → assurance ceiling → negative coverage →
structured feedback`라는 **일반 검증 kernel**입니다. 반면 특정 H1a 문구가
canonical expected graph에 모두 들어가야 confirmatory trial을 실행할 수
있다는 규칙은 **실험 내부 governance**입니다. 상위 목적에 따르면 후자가 제품
자산이라는 이유로 causal evidence 생산을 계속 차단해서는 안 됩니다.

## Q17.2 — `default_permission_applicability` 표현

### 결론: **단순 b는 불충분하지만, typed-reference 방식의 b′는 성립**

순수 b(`derived_from: GLOBAL_DEFAULT_PERMISSION_TEXT`)만으로는 부족합니다.

```text
RawReferenceAloneSatisfiesCanonicalExpectedSemantics = False
```

기대값과 감사 대상의 의미 원천이 같아질 수 있기 때문입니다.

### 성립하는 것은 b′ — typed semantic reference

유효 조건: `immutableRef ∧ independentMeaning ∧ independentObservation`

```yaml
default_permission_applicability:
  kind: meta_rule_reference
  carrier_ref: GLOBAL_DEFAULT_PERMISSION
  semantic_role_ref: ALLOWED_BY_DEFAULT
  scope_ref: packet_internal_decision_basis
  integrity:
    frozen_carrier_required: true
```

중요한 것은 `semantic_role_ref: ALLOWED_BY_DEFAULT`입니다. 의미를 자연어
문장에서 매번 추출하는 것이 아니라, 이미 존재하는 typed invariant
(`allowed_by_default → CARRIER_DEFAULT`)를 정본의 의미 anchor로 쓰고, 별도로
compiler가 렌더 문장이 그 의미를 보존하는지 봅니다. expected와 observed의
의미 경로가 분리되므로 순환이 아닙니다.

**피해야 할 b**: 같은 텍스트를 semantic compiler에 두 번 통과시켜 expected와
observed를 만드는 self-comparison.

## D-H1a-16과의 관계 — **적용 범위 한정**

D-H1a-16의 핵심 통찰은 유지하되, 그 앞에 gate를 둡니다.

```text
Semantic proposition → Causally load-bearing?
   ├─ No  → diagnostic/audit
   └─ Yes → Already independently established to required assurance?
              ├─ Yes → canonicalization optional/non-blocking
              └─ No  → canonical coverage becomes freeze-critical
```

`TargetCritical ⇒ CanonicalExpectedState`를
`CanonicalAuditCritical ⇒ CanonicalExpectedState`로 좁힙니다. 무효화가 아니라
**적용 대상을 더 정확하게 정의하는 amendment**입니다.

## freeze — **조건부 해제**

> **Q16에서 발견된 canonical coverage gap 자체는 더 이상 freeze blocker가
> 아니다.**

다만 다른 기존 freeze 조건까지 자동 통과시킨다는 뜻은 아닙니다. 세 의미
명제에 대해 다음을 기록해야 합니다.

```yaml
semantic_status:
  conflict_to_defer_mapping:
    resolved: true
    certification_path: existing_guard_plus_independent_review
  recorded_field_access:
    resolved: true
    certification_path: rendered_surface_plus_independent_review
  default_permission_applicability:
    resolved: true
    certification_path: policy_invariants_plus_golden_contract_plus_review

canonical_automation:
  status: deferred
  freeze_blocker: false
```

prompt bytes가 바뀌지 않았다면 Q17 때문에 confirmatory surface를 다시 저작할
이유는 없습니다.

## `INDEPENDENT_SEMANTIC_REVIEW_PASSED`

Q16 당시에는 `False` 유지가 맞았습니다. Q17 이후에는 다릅니다. 리뷰어가
발견한 것은 semantic error가 아니라 **canonical automation coverage gap**
이었고, 이번 판정에서 후자를 non-blocking audit gap으로 재분류했습니다.

따라서 **다른 BLOCKER/MAJOR가 없다는 전제에서** 기존 리뷰 결과를 다시
기록하고 flag를 `True`로 전환할 수 있습니다. 새 semantic review를 처음부터
다시 할 필요는 없습니다 — 정본이나 rendered prompt가 바뀐 것이 아니기
때문입니다.

## 실험 진행 여부 — **계속**

verification infrastructure의 추가분은 `추가 검증 부재 ⇒ 잘못된 causal
claim이 통과 가능`일 때만 confirmatory evidence 생성을 막아야 합니다. 단지
`human/guard certification → machine canonical certification`으로 **인증
주체만 바뀌는 것**이라면 제품화·감사 자동화 backlog로 이동시키는 것이 맞습니다.

## 최종 판정

```yaml
D-H1a-17:
  Q17:
    decision: B
    criterion:
      causal_load_bearing:
        removal_can_admit_false_or_nonidentified_causal_claim: true
      audit_only:
        independent_sufficient_certification_already_exists: true
        causal_acceptance_set_changes_when_removed: false
    classification:
      conflict_to_defer_mapping:
        semantic_fact: causal_load_bearing
        additional_canonicalization: audit_only
      recorded_field_access:
        semantic_fact: causal_load_bearing
        additional_canonicalization: audit_only
      default_permission_applicability:
        semantic_fact: causal_load_bearing
        additional_canonicalization: audit_only
  Q17_1:
    reusable_product_assets:
      semantic_graph_kernel: yes
      assurance_and_unknown_handling: yes
      mutation_framework: yes
      H1a_specific_controls: mostly_no
  Q17_2:
    representation: typed_reference_b_prime
    raw_text_reference_only: insufficient
    requires:
      - immutable_carrier_reference
      - independently_typed_semantic_role
      - independent_observed_semantics
  D_H1a_16:
    relation: scope_narrowed
    canonical_coverage_required_for: [canonical_audit_critical]
    not_automatically_required_for: [every_causal_semantic_critical_fact]
  freeze:
    canonical_gap_from_Q16:
      blocker: false
    other_existing_freeze_conditions:
      remain_in_force: true
  experiment:
    proceed_when_remaining_identification_contract_passes: true
```

> **"그 의미가 인과적으로 중요하다"와 "그 의미를 반드시 한 특정 기계 검증
> 경로가 인증해야 한다"는 같은 명제가 아닙니다.**

---

# 2. 수신 세션 실측 메모 (판정의 일부 아님)

판정문의 **사실 주장만** 대조했다.

## 2.1 `assert_4`의 typed invariant — 확인, 그리고 공허하지 않음

Q17.2의 b′는 `allowed_by_default → CARRIER_DEFAULT`가 **이미 존재하는 typed
invariant**임을 전제한다. 실측: 존재하고, 양방향 확인했다.

```text
assert_4_default_permission_states_use_the_default_carrier()  → 통과
carrier를 CARRIER_Q7로 변조 → PolicyContractError 발생 (공허하지 않음)
```

따라서 b′의 의미 anchor는 실재한다.

## 2.2 "다른 BLOCKER/MAJOR가 없다" — **실측으로 확인**

판정문은 flag 전환을 *"다른 BLOCKER/MAJOR가 없다는 전제에서"* 허용했다. 그
전제를 검증했다.

`assert_freezable`을 현재 상태로 실행하면 **조건 5(리뷰 플래그) 하나에서만**
막힌다. 플래그를 **메모리에서만** True로 두고 재실행하면 나머지가 전부
통과한다(디스크 무변경 확인: line 1127 `= False`, `git status` clean):

```text
kept_target_forbidden:                     True
removed_target_allowed:                    True
target_mechanism_contrast:                 True
nontarget_constraints_equal:               True
removed_target_state_is_allowed_by_default: True
removed_target_state_is_not_unspecified:    True
M_allowed truth table:                      4행 전부 산출
```

독립 리뷰어 5명의 finding도 **전부 minor**였다(blocker 0 · major 0).

## 2.3 판정문 논거를 **강화하는** 실측 하나

판정문은 `default_permission_applicability`를 "기계(compiler) vs 리뷰어"의
인증 주체 문제로 서술했다. 실측은 그보다 강하다 — **이미 다른 기계 경로가
그 명제를 인증하고 있다.** 위 §2.2의

```text
removed_target_state_is_allowed_by_default: True
removed_target_state_is_not_unspecified:    True
```

는 `assert_freezable`이 **정본 DSL을 직접 읽어** 산출한 값이다. 즉 "침묵이
아니라 허가"라는 바로 그 명제가 semantic compiler 없이도 기계 검증된다.
따라서 `AcceptedWorlds(+V) = AcceptedWorlds(−V)`라는 판정문의 판단은
리뷰어 증거뿐 아니라 **기존 정책 불변식만으로도** 성립한다.

## 2.4 Q17.1의 재사용 경계 — **이미 의존성 수준에서 실현돼 있음**

판정문은 `Reusable verification kernel ≠ H1a-specific verification policy`를
권고한다. 실측: 그 분리가 **이미 import 수준에서 성립**한다.

| 모듈 | H1a 코드 import | 외부 import |
|---|---|---|
| `_h1a_mutation_pack.py` | **0개** | `hashlib`만 |
| `_h1a_semantic_compiler.py` | **0개** | `re`만 |
| `_h1a_compiler_capability.py` | 1 (compiler) | — |
| `_h1a_policy_audit.py` | 2 (policy, compiler) | — |
| `_h1a_review_protocol.py` | 5 | — |

가장 재사용 가치가 높다고 판정된 둘(mutation framework, semantic graph
kernel)이 **H1a 코드를 하나도 import하지 않는다.** H1a 특수성은 기계가 아니라
**데이터**(MUTATIONS 항목, family 상수, detector 정규식)에만 있다. 즉 추출은
리팩터가 아니라 **패키징 문제**다.

## 2.5 렌더 바이트 무변경 — 재확인

`render_policy_block`은 `GLOBAL_DEFAULT_PERMISSION_TEXT`·`DECISION_BASIS_POLICY`·
`_Q7_AXIS_PHRASE`만 읽는다. 따라서 `criticality`/`semantic_status` 같은 메타
필드를 추가해도 렌더 바이트가 변하지 않고 golden contract 재동결이 불필요하다
— 판정문의 "prompt bytes가 바뀌지 않았다면 confirmatory surface를 다시
저작할 이유는 없다"와 일치한다.
