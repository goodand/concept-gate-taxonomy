# DESIGN DECISION — H1a canonical policy coverage (D-H1a-16)

> ⚠️ **이 파일은 2026-08-22에 트랜스크립트에서 복원됐다.** 판정은 2026-08-17에
> 수령·적용됐으나 **원문이 저장소에 커밋되지 않았다.** 그 사이 이 판정을
> 인용한 곳(`OPERATIONS_LOG.md`, `PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5h,
> `correspondence/DESIGN_REQUEST_H1a_verification_load_bearing.md`)의 인용이
> **원문 대조 불가 상태**였다.
>
> 이것은 이 저장소가 이미 한 번 등재한 결함과 같은 형태다 —
> `docs/DIRECTIVE_2026-07-29_operations_change.md`가 만들어진 이유가
> "원문 미커밋으로 인용 검증 불가"였다. 판정문 10건은 저장됐고 이 1건이
> 빠진 것이므로, 규약의 부재가 아니라 **누락**이다.

- 수신: **2026-08-17** (저장: 2026-08-22)
- 도착 경로: 사용자가 외부 설계 담당에게
  `correspondence/DESIGN_REQUEST_H1a_canonical_policy_coverage.md`를 공유하고
  회신을 전달
- 선행 요청: 위 요청서 (Q16 + Q16.1)
- 판정 ID: `D-H1a-16`
- 구속력: **있음.** D-H1a-1~15와 같은 외부 판정 채널을 거쳤다
- 복원 경로: 이 세션 트랜스크립트의 사용자 메시지에서 verbatim 추출.
  같은 메시지 끝에 붙어 있던 **사용자 자신의 후속 질문**("default permission
  절"이 무엇인지 설명 요구)은 판정문이 아니므로 분리했다
- 복원된 판정 본문 sha256: `1420aac643ef19cb09596fa39ee6a892ab4b539d926a04559879a69e646cd010`
- **범위 한정 주의**: 이 판정은 **D-H1a-17(Q17=B)이 적용 범위를 좁혔다**
  (무효화 아님). `TargetCritical ⇒ CanonicalExpectedState`가
  `CanonicalAuditCritical ⇒ CanonicalExpectedState`로 축소됐다. 현행 구속
  범위는 `DESIGN_DECISION_H1a_verification_load_bearing.md`와 사전등록 §5h를
  함께 읽어야 확정된다 — **이 파일만 읽고 12개 제약 전부를 현행으로 읽으면
  틀린다.**

---

## 판정문 원문 (verbatim)

아래는 수령한 텍스트 그대로다. 운영 세션이 정본을 저작하지 않는다는 규율에
따라 **재작성·요약·정정하지 않았다** — 오탈자·표기 흔들림도 그대로 둔다.

---

Wolfram MCP로 추상화해 검증한 결과, 이번 Q16은 **compiler의 결함이 아니라 canonical model의 불완전성**입니다. 핵심은 “정본으로부터 반증 가능한가”입니다. 

## Wolfram에서 확인된 핵심

target-critical 6개를 (T), canonical expected state 존재 여부를 (C(x))라 두면 현재:

```text
canonical coverage 있음:
- source_meta
- outside_domain
- presentation_order

canonical coverage 없음:
- conflict_to_defer
- recorded_field_access
- default_permission
```

Wolfram 결과:

```text
CurrentMachineAdjudicableAllTargetCritical = False
CurrentFreezeNoUnknownFromCompilerAlone    = False
```

선택지 비교도 명확했습니다.

```text
A: 전체 canonical coverage        = True
B: reviewer만으로 대체            = False
C: target-critical을 줄이면       = True
D: default_permission만 추가       = False
```

즉 **현재 target-critical 정의를 유지한다면 A만 구조적으로 완결됩니다.**

---

# DESIGN DECISION — H1a canonical policy coverage

**decided_by:** External design review + Wolfram formal check
**date:** 2026-08-16

## Q16: **A — 정본 DSL을 확장**

다만 기존 `DECISION_BASIS_POLICY`의 `axis`에 세 항목을 억지로 집어넣는 방식은 권하지 않습니다.

문제의 세 항목은 성격이 다릅니다.

```text
decision basis
├─ source_meta_reasoning
├─ outside_domain_knowledge
└─ presentation_order

template / decision semantics
├─ conflict_to_defer_mapping
├─ recorded_field_access
└─ default_permission_applicability
```

따라서 정본을 **두 종류의 typed policy**로 확장하는 것이 좋습니다.

```yaml
canonical_policy:
  decision_basis_policy:
    ...

  decision_semantics:
    conflict_to_defer_mapping:
      ...

    recorded_field_access:
      ...

    default_permission_applicability:
      ...
```

핵심은:

> target-critical이라고 선언한 의미는 모두 canonical source에서 기대 상태를 도출할 수 있어야 한다.

입니다.

형식적으로:

[
TargetCritical(x)
\Rightarrow
CanonicalExpectedState(x)
]

를 freeze invariant로 추가해야 합니다.

---

## 왜 B는 기각하는가

리뷰어가 실제 의미를 잘 읽었더라도:

```text
Rendered Prompt
     ↓
Human reviewer
     ↓
state 결정
```

만으로 target-critical 상태를 닫으면, 실질적으로 **정본이 typed DSL이라는 원칙이 깨집니다.**

정본에 없는 의미를 사람이 보충하면 권위 방향이:

```text
Policy DSL
→ Renderer
→ Prompt
→ Reviewer
→ 사실상의 정책 정의
```

가 됩니다.

이는 원래 설계한:

```text
Policy DSL
→ expected graph
```

의 방향과 다릅니다.

따라서 human review는 **정본의 누락을 보충하는 source of truth**가 아니라, 정본과 렌더링 사이의 일치 여부를 adjudicate하는 역할이어야 합니다.

---

## 왜 C도 기각하는가

C는 논리적으로는 성립합니다.

Wolfram도:

```text
OptionCOnlyWorksByShrinkingTargetCriticalSet = True
```

를 반환했습니다.

하지만 이것은 공백을 해결하는 게 아니라 **검사해야 할 집합을 줄이는 것**입니다.

특히 세 항목은 실제 licensed path에 직접 관여합니다.

```text
conflict_to_defer
→ 결과를 defer로 강제할 수 있음

recorded_field_access
→ source_kind 사용 가능성을 결정

default_permission
→ REMOVED에서 source-meta path를 여는 핵심
```

따라서 단순히 target-critical에서 내리면 이전 Q10~Q13에서 발견한 실패 경로를 다시 비정본 영역으로 밀어냅니다.

---

## 왜 D도 부족한가

`default_permission`이 가장 직접적으로 load-bearing한 것은 맞습니다.

하지만 나머지 둘도 독립적으로 표적 경로를 봉쇄할 수 있습니다.

[
LicensedPath =
DefaultPermission
\land RecordedFieldAccess
\land \neg HardConflictToDefer
]

따라서 default permission만 canonicalize해도:

```text
RecordedFieldAccess = unknown
ConflictToDefer     = unknown
```

이면 licensed path 전체는 여전히 인증되지 않습니다.

Wolfram도:

```text
OptionDFullCanonicalCoverage = False
```

로 확인했습니다.

---

# Q16.1 — `external_source_retrieval`

## 판정: **별도 semantic family로 분리**

다만 **코드 detector 함수까지 반드시 별개일 필요는 없습니다.**

중요한 구분은:

```text
implementation sharing
≠
semantic identity
```

입니다.

현재 canonical DSL에:

```text
outside_domain_knowledge
external_source_retrieval
```

가 별도 axis로 존재한다면 compiler도 최소한 별도 claim을 출력해야 합니다.

```yaml
- policy_id: outside_domain_knowledge
  state: ...

- policy_id: external_source_retrieval
  state: ...
```

같은 detector 코드가 두 claim을 추출하는 것은 허용됩니다.

그러나 한 detection 결과를 두 policy의 검증으로 간주하면 안 됩니다.

Wolfram에서 두 canonical boolean 상태를 하나의 shared detector 출력으로 압축해 보니 **정보 손실이 반드시 발생**했습니다.

```text
SharedDetectorHasInformationLoss = True
```

예를 들어 서로 다른:

```text
outside=False, external=False
outside=False, external=True
outside=True,  external=False
```

상태가 하나의 shared signal 아래에서 구별되지 않을 수 있습니다.

따라서 새 규칙:

> **carrier 공유는 detector-family 통합의 근거가 아니다.**

각 canonical policy ID마다 독립적으로:

* expected state
* observed claim
* capability evidence
* diff

가 있어야 합니다.

---

# Q16.2 — 조건부 규칙

## 판정: **정본 DSL에 조건을 표현하고, freeze 시 antecedent를 별도로 평가**

둘 중 하나만 하면 부족합니다.

현재 같은 규칙:

```text
forbidden unless packet explicitly authorizes that basis
```

은 flat state 하나로 표현할 수 없습니다.

Wolfram 결과:

```text
antecedent = False → forbidden
antecedent = True  → allowed

FlatStateCanRepresentBothBranches = False
```

즉 현재의:

```yaml
state: forbidden
carrier: Q7
```

만으로는 의미 손실이 있습니다.

### 권장 canonical 형식

```yaml
evidence_item_presentation_order:
  rule_type: conditional
  default_state: forbidden

  exception:
    when:
      predicate: packet_explicitly_authorizes_basis
    state: allowed
```

또는 더 일반적으로:

```yaml
state_function:
  if:
    packet_explicitly_authorizes_basis: allowed
  else: forbidden
```

---

## 그리고 fixture binding은 별도 단계

정본은:

```text
어떤 조건에서 상태가 바뀌는가
```

를 정의합니다.

freeze-time evaluator는:

```text
현재 packet에서 그 조건이 참인가
```

를 검사합니다.

즉:

```text
Canonical conditional policy
          ↓
Fixture antecedent evaluation
          ↓
Effective state
```

입니다.

현재 fixture에서 antecedent가 false라면:

```yaml
canonical_rule:
  default: forbidden
  exception_if_authorized: allowed

fixture_evaluation:
  packet_explicitly_authorizes_basis: false

effective_state:
  forbidden
```

으로 도출합니다.

### 피해야 할 구조

정본은 평면 상태로 놔두고:

```text
"이번 fixture에서는 예외가 발동 안 함"
```

만 외부 freeze check로 처리하는 것입니다.

그러면 정본 자체가 여전히 렌더 문장의 의미를 완전히 표현하지 못합니다.

---

# Q16.3 — 리뷰어 육안 독해 assurance

## 판정: **assurance 수준은 `SEMANTIC_REVIEWED`를 유지하되 adjudication path를 별도 표기**

새 assurance rank를 즉석에서 만들 필요는 없습니다.

대신 두 축을 분리합니다.

### 의미 검토의 질

```yaml
assurance: SEMANTIC_REVIEWED
```

### 어떤 경로로 얻었는가

```yaml
adjudication_mode:
  - compiler_expected_graph
  - human_diff_resolution
  - human_only_no_canonical_counterpart
```

세 번째는 중요하게 다르게 취급합니다.

```yaml
assurance: SEMANTIC_REVIEWED
adjudication_mode: human_only_no_canonical_counterpart
freeze_eligible: false
```

즉 사람이 잘 읽었다는 사실 자체를 낮은 품질로 취급할 이유는 없습니다.

하지만:

> **정본에 기대값이 없는 상태를 human review가 대신 만들어낸 경우에는 target-critical freeze evidence로 사용할 수 없다.**

이렇게 분리합니다.

---

## canonical expansion 이후에는 달라진다

정본을 확장한 뒤:

```text
Canonical expected state
          ↕
Rendered prompt
          ↓
Compiler
          ↓
diff
          ↓
Human reviewer adjudication
```

이라면 reviewer 결과는 정상적으로:

```yaml
assurance: SEMANTIC_REVIEWED
adjudication_mode: human_diff_resolution
freeze_eligible: true
```

가 될 수 있습니다.

즉 문제는 **human review 자체가 아니라 canonical anchor의 부재**입니다.

---

# 권장 canonical 구조

전략적으로는 다음처럼 나누는 게 가장 안정적입니다.

```yaml
canonical_policy:

  decision_basis:
    evidence_count: ...
    evidence_item_presentation_order: ...
    outside_domain_knowledge: ...
    external_source_retrieval: ...
    source_meta_reasoning: ...

  decision_semantics:

    conflict_resolution:
      conflict_alone_implies_select: false
      conflict_alone_implies_defer: false

    evidence_field_access:
      type_support_source:
        - text

      source_evaluation_fields:
        - source_kind

    default_permission:
      scope: packet_internal_decision_basis
      state: allowed_unless_explicitly_prohibited

  structural_constraints:
    referential_integrity:
      dangling_reference_allowed: false
```

이 구조의 장점은 `axis` 개념을 무리하게 확장하지 않으면서도 **모든 target-critical claim을 canonicalized**한다는 점입니다.

---

# freeze invariant를 하나 더 추가

기존에는 주로:

```text
target-critical에 unknown 없음
```

을 검사했습니다.

그보다 먼저 다음을 검사해야 합니다.

```text
target-critical에 canonical expected state가 존재하는가?
```

즉 두 단계:

[
CoverageComplete
================

\forall x\in T,;Expected(x)\neq null
]

그 다음:

[
SemanticComplete
================

\forall x\in T,;State(x)\neq unknown
]

입니다.

순서가 중요합니다.

```text
Canonical coverage
      ↓
Semantic adjudication
      ↓
No unknown
      ↓
Freeze eligibility
```

정본에 항목 자체가 없는데 reviewer가 `unknown`을 제거하는 방식은 허용하지 않습니다.

---

# deferred

**없음.**

Q16.1~Q16.3은 현재 제공된 자료와 기존 판정 원칙만으로 판정 가능합니다.

단, 실제 DSL 필드명과 migration 방식은 구현 세부이므로 운영 세션이 위 의미 계약을 보존하는 범위에서 정할 수 있습니다.

---

# new_constraints

1. 모든 target-critical family는 canonical expected counterpart를 가져야 한다.
2. `expected_state: null`인 target-critical claim이 하나라도 있으면 freeze 불가.
3. target-critical 범위를 줄이는 방식으로 canonical coverage 오류를 해소하지 않는다.
4. decision-basis axis와 template/decision semantics를 별도 canonical namespace로 둔다.
5. canonical axis가 별도이면 compiler claim도 별도로 존재해야 한다.
6. 동일 carrier 또는 detector 구현 공유는 semantic family 통합 근거가 아니다.
7. 조건부 렌더 규칙은 canonical DSL에서도 조건부로 표현한다.
8. effective state는 canonical condition + fixture antecedent evaluation으로 도출한다.
9. human review는 canonical source를 대체할 수 없다.
10. `SEMANTIC_REVIEWED` assurance와 `adjudication_mode`를 분리한다.
11. `human_only_no_canonical_counterpart`는 target-critical freeze evidence가 될 수 없다.
12. canonical model 변경 후 expected graph 및 compiler capability suite를 다시 생성·검증한다.

---

# INDEPENDENT_SEMANTIC_REVIEW_PASSED 설정 가부

**현재는 설정하면 안 됩니다.**

이유:

리뷰어들이 잘못 리뷰해서가 아닙니다.

오히려 리뷰가 성공했기 때문에:

```text
canonical coverage gap
```

을 발견했습니다.

따라서 현 리뷰의 올바른 산출물은:

```yaml
review_execution: passed
reviewer_capability: passed
design_freeze_review: blocked_by_canonical_gap
INDEPENDENT_SEMANTIC_REVIEW_PASSED: false
```

입니다.

A안 구현 후에는:

1. canonical DSL 확장
2. expected graph 재생성
3. compiler family/capability fixture 갱신
4. conditional rule 테스트
5. target-critical coverage 검사
6. independent semantic review 재실행

을 거쳐야 합니다.

프롬프트 바이트가 그대로더라도 **감사 대상 정본이 바뀌므로 리뷰 재실행이 필요**합니다.

---

# 실험 진행 여부

**계속 — 단 freeze는 유지 차단**

confirmatory trial이 0건이므로 이 문제는 지금 수정하기 가장 좋은 시점입니다.

현재 결함은 H1a estimand 자체를 다시 정의해야 하는 문제가 아니라:

> **이미 target-critical이라고 선언한 의미를 canonical model이 충분히 표현하지 못하는 문제**

입니다.

따라서 실험을 중단하거나 target-critical 정의를 축소하기보다 **정본 표현력을 target-critical 계약 수준까지 올리는 것**이 가장 작은 구조적 수정입니다.

### 최종 요약

```yaml
D-H1a-16:

  Q16:
    decision: A
    canonical_extension: required

  Q16_1:
    external_source_retrieval:
      separate_semantic_family: true
      shared_detector_implementation: allowed
      independent_claim_and_capability_status: required

  Q16_2:
    conditional_policy:
      encode_in_canonical_DSL: true
      freeze_time_antecedent_evaluation: true
      flat_state_only: forbidden

  Q16_3:
    reviewer_assurance:
      assurance: SEMANTIC_REVIEWED
      separate_adjudication_mode: required
      human_only_without_canonical_counterpart:
        freeze_eligible: false

  freeze:
    canonical_target_coverage_complete: required
    target_critical_unknown: forbidden
    current_status: blocked

  independent_semantic_review_passed:
    set_now: false
    rerun_after_canonical_expansion: true
```

Wolfram을 사용한 이번 판정에서 가장 중요한 인사이트는 하나입니다.

> **“unknown이 없는가?”보다 먼저 “그 명제를 정본이 표현할 수 있는가?”를 검사해야 합니다.**

즉 앞으로의 순서는 `semantic completeness`보다 **canonical coverage completeness**가 먼저입니다.
