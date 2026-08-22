# DESIGN DECISION — Refine ↔ Verify v0 구현 리뷰 (W5 BLOCKER 포함)

- 수신: **2026-08-22**
- 도착 경로: 사용자가 진행 보고
  (`PROGRESS_REPORT_refine_verify_v0_for_design_agent.md`)를 설계 담당에게
  공유하고 회신을 전달
- 판정 요지: **PASS_WITH_BLOCKER** — v0 승인 항목 8건, 신규 BLOCKER 1건(W5:
  `prior_verdicts` provenance laundering), W2=(a)-refined(두 축 분리),
  G32=통일 금지, oracle title 교정 필수
- 저장 방법: 트랜스크립트 verbatim 추출(M10). 본문 sha256: `2a17ec3aa16fbd581a3adbca07890be7b545fd6d813b344f420a33ef34e6e2a7`.
  판정문 뒤에 붙어 있던 사용자 지시("검증 설계, 검증 후 저장")는 분리했다

## 운영 세션의 저장 전 검증 (2026-08-22)

| # | 판정문 주장 | 검증 방법 | 결과 |
|---|---|---|---|
| V1 | **W5**: 조작된 prior_verdicts만으로 게이트 미실행 claim이 인증된다 | **공격 재현** — 게이트 0회 실행 claim + 전부-pass 조작 prior 공급 | ✅ **CONFIRMED** — `certified_claim_ids == ['evil']`. 가설이 아니라 실증 |
| V2 | Dockerfile이 `default-jre-headless`를 명시 설치, `runtime: docker` — 진행 보고의 "Java 없음(기본 Render)" 전제와 모순 | Dockerfile·render.yaml 직접 판독 | ✅ **판정문이 옳다.** docstring의 "기본 Render"는 네이티브 python 런타임을 지칭했고 실배포는 docker+JRE. **운영 세션 보고 §6-①의 전제 오류** — P14 규율로 아래 정정 |
| V3 | classify_owl이 모든 예외를 단일 `REASONER_UNAVAILABLE`로 잡는다 | 이 세션에서 기측정 (server.py:819-827) | ✅ 일치 |
| V4 | O1·O2·O3·R1 verbatim 제목 표 | O1·O3는 운영 세션이 직접 웹 실측, O2·R1은 haiku C축 감사와 일치 — **독립 검증 2계통 합치** | ✅ |
| V5 | "135 passed / 8-0-1은 CI 미검증" | 사실 — 이 저장소에 GitHub CI 없음 | ✅ 정직한 한정 |

## 즉시 적용한 잠정 조치 (판정의 `until_fixed` 요구)

- `certify_relation_claims` / MCP tool `certify_claims`의 응답에
  **`"authority": "diagnostic_only"`** 필드를 추가하고, docstring 최상단에
  W5 경고를 넣었다 — W5가 닫히기 전까지 `certified_claim_ids`를 권위 있는
  인증으로 취급 금지.
- W5 재현을 **테스트로 고정**(`test_w5_laundering_reproduces_until_fixed`) —
  수정이 착륙하면 이 테스트를 뒤집는 것이 수정 완료의 정의가 된다.
- P14 정정 2건: 진행 보고 §6-①과 구현 기록 §8의 "Java 없음(기본 Render)"
  전제에 취소선 + 정정.

## W5 수정 방향 (판정문 §3 — 다음 회차)

기존 receipt 선례(`_receipt.py` 계열의 canonical/HMAC)를 재사용해
obligation certificate에 issuer·subject_fingerprint·graph_revision 결박과
서명을 넣고, `certify_claims`가 **authenticity → binding → validity** 순서로
검증한 뒤에만 projection을 계산한다. 새 subsystem 금지(판정문 명시).

---

## 판정문 원문 (verbatim)

결론부터 말하면 **v0 구현은 설계 의도와 대체로 잘 맞습니다.** 다만 `certify_claims`의 현재 신뢰 경계에서 **새로운 BLOCKER 1건(W5)**을 발견했습니다. 이 부분을 고치기 전에는 MCP 표면의 `certified_claim_ids`를 권위 있는 certification 결과로 취급하면 안 됩니다. 진행 보고의 나머지 P0 구현은 승인 가능한 수준입니다.

## 1. 전체 판정

| 항목판정                                        |                                      |
| ------------------------------------------- | ------------------------------------ |
| Shared Kernel / identity                    | **승인**                               |
| CertificationProfile / projection           | **승인**                               |
| revision binding                            | **승인**                               |
| certification cycle detector                | **승인, W3 생산자 부재는 허용**                |
| ERROR 추가 방향                                 | **개념은 승인, 현재 단일 Verdict 구현은 수정 권고**  |
| `certify_claims` MCP 배선                     | **조건부 승인 — W5 BLOCKER**              |
| UNKNOWN vs UNSCORABLE                       | **통합 금지**                            |
| Oracle title 교정                             | **필수**                               |
| P1 legacy E2E 진행                            | **W5와 runtime-state 계약을 먼저 고친 뒤 진행** |
| Certified-only Reason/Derive authority flip | **계속 별도 판정 대상**                      |

GitHub에서 실제로 `cg_identity.py`, CertificationProfile, revision binding, cycle detection, Certified Projection이 구현된 것을 확인했습니다. 특히 projection은 입력 claim을 변경하지 않는 view로 구현되어 있어 Verify가 graph writer가 되지 않는다는 원래 경계를 보존합니다.

또 자기감사에서 “단위 E2E가 실제 MCP 배선을 증명하지 않는다”는 W1을 찾아낸 뒤 `certify_claims`를 실제 tool surface에 추가한 것도 적절합니다.

단, 보고서의 `135 passed`, root gate `8/0/1`은 **운영 세션 보고로는 받아들이지만 GitHub CI로 독립 검증된 사실은 아닙니다.** 해당 커밋에는 GitHub combined status가 등록되어 있지 않았습니다.

---

# 2. 새 발견 — W5: `prior_verdicts` provenance laundering

이게 가장 중요합니다.

현재 `certify_claims`는 호출자가 전달한:

```python
prior_verdicts = {
    "claim_id": {
        "source.snapshot_hash": "pass",
        "source.span_evidence": "pass",
        ...
    }
}
```

를 받아서 enum 값인지만 확인한 뒤 Certified Projection 계산에 그대로 사용합니다.

즉 검사하는 것은:

```text
"pass"라는 문자열이 유효한 Verdict인가?
```

이지,

```text
그 PASS를 실제 cg_normalizer / CompositionGate가 발급했는가?
```

가 아닙니다.

Wolfram으로 현재 논리를 추상화하면:

```text
required checks:
snapshot ∧ span ∧ anchoring ∧ antisymmetry ∧ acyclicity ∧ exclusivity
```

이고 `anchoring`만 서버가 직접 계산하며 나머지를 caller가 모두 `True/PASS`로 공급하면:

```text
CallerCanSatisfyAllPriorChecksBySupplyingTrue = True
```

가 됩니다.

따라서 현재 certification의 실제 논리는:

# [ Certified

AllRequiredPass
]

가 아니라 반드시:

# [ Certified

AuthenticPriorCertificate
\land
AllRequiredPass
]

이어야 합니다.

이 두 번째 항이 현재 없습니다.

## 왜 심각한가

현재 아키텍처에서 MCP client는 LLM agent일 수 있습니다.

그런데:

```text
LLM/client
→ prior_verdicts="pass"
→ Verify-side Certified Projection
```

이 가능하면 **Refine/LLM이 certification authority를 우회 취득**하는 것과 같습니다.

이는 프로젝트가 계속 막아온 deterministic laundering의 정확한 변형입니다.

---

# 3. W5 수정 권고

검사를 다시 구현하지 않는다는 운영 세션의 판단은 맞습니다.

문제는:

```text
gate를 재실행하지 않는다
```

가 아니라:

```text
gate 결과의 provenance를 인증하지 않는다
```

입니다.

### BEFORE

```text
previous MCP response
       ↓
LLM/client extracts verdict strings
       ↓
certify_claims(prior_verdicts)
       ↓
Certified
```

### AFTER

```text
existing gate
    ↓
authenticated obligation certificate / receipt
    ↓
certify_claims verifies receipt + subject binding + revision
    ↓
Certified
```

최소 envelope는 다음이면 됩니다.

```yaml
ObligationCertificate:
  issuer:
    tool: run_pipeline
    verifier_version: "..."

  subject_fingerprint: "..."
  graph_revision: "..."

  results:
    - obligation: source.snapshot_hash
      verdict: pass
      assurance: RULE_CHECKED
      decider: local_rule
      evidence: "..."

  receipt:
    scheme: "..."
    key_id: "..."
    signature: "..."
```

`certify_claims`는 최소 다음을 확인해야 합니다.

```text
receipt authenticity
AND subject fingerprint binding
AND graph revision binding
AND obligation/decider/assurance validity
```

그 다음에만 profile projection을 계산합니다.

### 중요한 점

새 certification subsystem을 만들라는 뜻은 아닙니다.

보고서와 커밋 설명에 이미 `_receipt.py` 계열의 canonical/signing 선례가 언급되어 있으므로, 가능하면 **그 receipt mechanism을 재사용**하십시오.

그 전까지는:

```yaml
certify_claims:
  authority: diagnostic_only
```

로 두는 편이 안전합니다.

---

# 4. ① W2 — ERROR 생산 방식

## 판정: **(a)**

단, 단순히 error code만 둘로 나누는 것보다 한 단계 더 명확하게 해야 합니다.

원래 설계에는:

```text
PASS / FAIL / UNKNOWN / NA
```

가 semantic/check 상태이고,

```text
ERROR
```

는 **실행 장애를 별도 상태로 둔다**는 원칙이 있었습니다.

현재 구현은 `Verdict.ERROR`를 같은 enum에 넣었습니다. GitHub에서도 그렇게 구현되어 있습니다.

이것은 v0에서는 작동하지만 장기적으로는 두 축을 다시 분리하는 것이 좋습니다.

## 권장 모델

```yaml
semantic_verdict:
  PASS | FAIL | UNKNOWN | NA

execution_status:
  OK | UNAVAILABLE | ERROR
```

예:

```text
ontology inconsistency 발견
→ semantic = FAIL
→ execution = OK
```

```text
optional reasoner가 deployment profile상 없음
→ semantic = UNKNOWN
→ execution = UNAVAILABLE
```

```text
HermiT 실행 도중 timeout / crash
→ semantic = UNKNOWN
→ execution = ERROR
```

Wolfram으로 product state를 검토하면 이 두 축을 분리할 때 원인 정보가 보존되며, 단일 enum으로 합치면 `UNKNOWN`과 실행 불가의 원인이 쉽게 섞입니다.

### 그리고 현재 저장소에는 중요한 사실 불일치가 있습니다

진행 보고에는 “Java 없음(기본 Render)”이라고 되어 있지만, 현재 해당 커밋의 `Dockerfile`은 **명시적으로** **`default-jre-headless`****를 설치**하고 있습니다. `render.yaml` 역시 `runtime: docker`입니다.

따라서 현재 배포 계약에서 Java 부재가 발생한다면 오히려:

```text
required dependency unexpectedly missing
```

일 수 있습니다.

즉 먼저 다음을 정의해야 합니다.

```yaml
reasoner_capability:
  deployment_requirement: required | optional
```

그리고:

```text
optional + unavailable
→ execution_status = UNAVAILABLE

required + unavailable
→ execution_status = ERROR
```

가 더 정확합니다.

### `classify_owl` 현재 구현

현재는 모든 예외를 하나의:

```text
REASONER_UNAVAILABLE
```

로 잡고 있으며 Java 부재와 실제 HermiT crash를 구분하지 않습니다. 그리고 obligation은 둘 다 `UNKNOWN`으로 변환합니다.

따라서 다음처럼 나누십시오.

```text
REASONER_DEPENDENCY_UNAVAILABLE
REASONER_TIMEOUT
REASONER_PROCESS_CRASH
REASONER_PROTOCOL_ERROR
```

그리고 예상된 unavailable과 unexpected runtime failure를 구별합니다.

---

# 5. aggregate의 `FAIL > ERROR > PASS > UNKNOWN`

현재 의미에서는 큰 문제는 없습니다.

GitHub 코드의 설명대로:

```text
FAIL
= 이미 확정된 위반

ERROR
= 다른 검사가 실행 불가

UNKNOWN
= 증거상 미결정
```

이라면 다른 검사 하나가 확정 FAIL을 냈는데 또 다른 검사기가 죽었다고 전체를 ERROR로 덮어쓰지 않는 것은 합리적입니다.

다만 execution axis를 분리하면 더 깔끔해집니다.

예:

```yaml
aggregate:
  semantic_verdict: FAIL
  execution_status: ERROR
```

즉 정보를 버리지 않습니다.

현재의:

```text
aggregate = FAIL
```

만 반환하면 “동시에 reasoner 하나가 죽었다”는 정보가 aggregate level에서 사라질 수 있습니다.

그래서 장기 contract는 **priority enum이 아니라 product state**를 권합니다.

---

# 6. ② G32 — UNKNOWN vs UNSCORABLE

## 판정: **같지 않다. 통일하지 않는다.**

Wolfram 검토 결과도:

```text
UNKNOWNEqualsUNSCORABLE = False
```

로 두는 것이 구조적으로 맞습니다.

두 단어는 다른 layer를 말합니다.

### UNKNOWN

Verify/check의 인식론적 상태입니다.

> “이 claim의 참/적합 여부를 현재 evidence로 결정하지 못했다.”

예:

```text
semantic_support = UNKNOWN
```

### UNSCORABLE

Evaluate의 평가 가능성 상태입니다.

> “이 evaluation protocol로 이 사례에 점수를 부여할 수 없다.”

예:

```text
Oracle locator 없음
gold structure가 해당 phenomenon을 annotate하지 않음
evaluation adapter가 target dimension을 정의하지 않음
```

따라서:

```text
Verify vocabulary:
PASS / FAIL / UNKNOWN / NA
+ execution status

Evaluate vocabulary:
PASS / FAIL / UNSCORABLE
+ execution status
```

가 맞습니다.

### 중요한 예

Semantic compiler가:

```text
quantifier_scope = UNKNOWN
```

을 냈다고 해서 Oracle evaluator가 반드시 `UNSCORABLE`인 것은 아닙니다.

Oracle은 존재할 수 있고, predicted output이 UNKNOWN이라면 그것 자체를:

```text
FAIL 또는 unresolved prediction
```

로 평가할 수 있습니다.

반대로 predicted graph는 완전히 determinate해도 Oracle source 자체가 해당 item을 scoring하지 못하면:

```text
UNSCORABLE
```

일 수 있습니다.

그러므로 둘은 등가가 아닙니다.

---

# 7. ③ Oracle YAML title

## 판정: **교정 필수**

운영 세션의 지적이 맞습니다.

현재 YAML은 `title` 필드에 descriptive label을 넣은 곳이 있습니다. 예를 들어 O1은 현재:

```yaml
title: "A Corpus of Scope-Disambiguated English Text"
```

인데 GitHub YAML에서 실제 그렇게 저장되어 있습니다.

그러나 ACL의 실제 논문 제목은:

**A Corpus of Encyclopedia Articles with Logical Forms** 입니다. ([ACL 앤솔로지](https://aclanthology.org/2020.lrec-1.132/?utm_source=chatgpt.com "A Corpus of Encyclopedia Articles with Logical Forms - ACL Anthology"))

확인된 네 건은 다음처럼 교정해야 합니다.

| Oracle현재 title실제 bibliographic title |                                                            |                                                                                                  |
| ------------------------------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| O1                                   | `A Corpus of Scope-Disambiguated English Text`             | **A Corpus of Encyclopedia Articles with Logical Forms**                                         |
| O2                                   | `Intensionality in Abstract Meaning Representation`        | **Intensionalizing Abstract Meaning Representations: Non-Veridicality and Scope**                |
| O3                                   | `Controlled Natural Language / Formal Modal Logic Dataset` | **Logical forms complement probability in understanding language model (and human) performance** |
| R1                                   | `A Formalization of Modal Logic S5 in Lean`                | **A Henkin-style completeness proof for the modal logic S5**                                     |

O2는 ACL 원문으로 확인됩니다. ([ACL 앤솔로지](https://aclanthology.org/2021.law-1.17/?utm_source=chatgpt.com "Intensionalizing Abstract Meaning Representations: Non-Veridicality and Scope - ACL Anthology")) O3도 ACL 원문과 다릅니다. ([ACL 앤솔로지](https://aclanthology.org/2025.acl-long.824/?utm_source=chatgpt.com "Logical forms complement probability in understanding language model (and human) performance - ACL Anthology")) R1의 arXiv 실제 제목도 확인됩니다. ([arXiv](https://arxiv.org/abs/1910.01697 "\[1910.01697] A Henkin-style completeness proof for the modal logic S5"))

## 권장 schema

설명 이름이 유용하므로 버리지는 마십시오.

```yaml
oracle_id: O1
name: Quantifier Scope

source_authority:
  primary:
    title: "A Corpus of Encyclopedia Articles with Logical Forms"
```

처럼:

```text
name
= 우리 architecture에서의 역할 이름

title
= 출처의 verbatim bibliographic title
```

로 분리하면 됩니다.

가능하면 같이 고정:

```yaml
source_locator:
  anthology_id: "2020.lrec-1.132"
```

같은 stable locator를 추가하십시오.

---

# 8. W3 — `depends_on` producer 부재

운영 세션 판단에 동의합니다.

```text
cycle detector가 있으니
→ 가짜 dependency를 만들어서 실행해야 한다
```

는 잘못입니다.

그건 detector를 위해 데이터를 제조하는 것이므로 정확히 vacuous verification이 됩니다.

따라서:

```yaml
W3:
  detector: implemented_and_tested
  production_trigger: not_yet_present
  status: dormant_by_design
```

이면 충분합니다.

실제 Refine repair/provenance dependency가 생길 때만 producer를 배선하십시오.

---

# 9. 현재 구현에서 승인할 부분

특히 잘 된 부분은 다음입니다.

- `cg_identity`를 **leaf module**로 유지하고 판단형 API를 AST negative contract로 막은 것.
- fingerprint에 kind domain separation을 넣어 `node`와 `claim` identity를 상호 대체하지 못하게 한 것.
- missing required check를 PASS가 아닌 UNKNOWN으로 처리한 것.
- Certified Projection이 graph lifecycle을 직접 변경하지 않는 것.
- lexical anchoring을 semantic support라고 부르지 않고, 어휘 부재를 FAIL로 세탁하지 않은 것.
- certification-cycle 검사에서 `static_order()` generator를 실제 소비해야 한다는 vacuity bug를 negative test로 잡은 것.
- W4를 통해 기존 mutation gate의 `conceptgate/` 사각지대까지 발견한 것.

이 부분들은 원래 설계의:

```text
shared representation
+
separate judgment
+
fail-closed verification
```

과 잘 정렬되어 있습니다.

---

# 10. canonical hash에 대한 작은 제한

현재 `canonical_bytes()`는:

```python
json.dumps(sort_keys=True, ensure_ascii=False)
```

입니다.

**Python 내부 v0 identity에는 충분합니다.**

다만 향후 Oracle Adapter나 외부 언어 구현이 이 hash를 공유하기 시작하면 “표준 canonical JSON”이라고 부르면 안 됩니다.

특히:

- float 표현
- Unicode escaping
- cross-language number serialization

에서 차이가 생길 수 있습니다.

따라서 v0 contract는:

```yaml
canonicalization:
  scope: python_internal_v0
```

정도로 고정하고, cross-runtime fingerprint가 실제 요구될 때만 RFC 8785/JCS 여부를 다시 판단하십시오.

지금 당장 새 dependency를 도입할 이유는 없습니다.

---

# 11. 다음 진행 순서

제가 운영 세션에 내릴 판정은 다음입니다.

```yaml
REFINE_VERIFY_V0_REVIEW:

  overall:
    architecture_alignment: PASS_WITH_BLOCKER

  accepted:
    - stable_identity
    - shared_kernel_negative_contract
    - certification_profile
    - certified_projection_view
    - graph_revision_binding
    - certification_cycle_detection
    - lexical_anchoring_boundary
    - MCP_surface_wiring_as_mechanism

  W5:
    severity: BLOCKER
    issue: caller_supplied_prior_verdicts_are_not_authenticated
    required_fix:
      - bind prior results to actual issuing tool/certificate
      - bind certificate to subject fingerprint
      - bind certificate to graph revision
      - validate decider/assurance/provenance
    until_fixed:
      certify_claims_authority: diagnostic_only

  W2:
    decision: A_REFINED
    semantic_verdict:
      - PASS
      - FAIL
      - UNKNOWN
      - NA
    execution_status:
      - OK
      - UNAVAILABLE
      - ERROR
    dependency_absence:
      optional: UNAVAILABLE
      required: ERROR
    unexpected_crash: ERROR

  G32:
    UNKNOWN_equals_UNSCORABLE: false
    UNKNOWN_layer: Verify
    UNSCORABLE_layer: Evaluate

  oracle_titles:
    correction_required: true
    descriptive_name_separate_from_bibliographic_title: true

  W3:
    keep_dormant_until_real_dependency_producer_exists: true

  next:
    before_P1:
      - fix_W5
      - resolve_runtime_status_contract
      - correct_oracle_titles
    then:
      - run_real_legacy_fixture_E2E
      - preserve_candidate_certified_derived_provenance

  certified_gate_authority_flip:
    proceed_now: false
    requires_separate_ruling: true
```

## 핵심 판단

운영 세션은 이번 구현에서 **“코드가 존재한다”와 “실제 경로에 배선됐다”를 구별하는 데 성공**했습니다. W1/W4를 스스로 찾은 것이 그 증거입니다. 다만 `certify_claims`를 실제 MCP 경로에 붙이는 순간 새로운 trust boundary가 생겼고, 바로 그 경계에서 **well-formedness를 authenticity로 착각하는 한 단계의 laundering 위험**이 생겼습니다.

따라서 v0를 폐기하거나 재설계할 필요는 없습니다.

**W5만 닫고, ERROR를 semantic verdict와 execution status의 두 축으로 정리한 뒤 P1 실 fixture 관통으로 넘어가는 것이 가장 작은 다음 단계입니다.**
