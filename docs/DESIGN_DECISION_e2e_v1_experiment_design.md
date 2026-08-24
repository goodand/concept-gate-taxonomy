# DESIGN DECISION — E2E-v1 실험 설계 (D-E2E-v1-19)

- 사슬 항법: 이전 (없음 — 사슬 시작) · **D-19** · 다음 [[DESIGN_DECISION_o1_fixture_licensing|D-20]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: **2026-08-22**
- 도착 경로: 사용자가 `DESIGN_REQUEST_e2e_v1_experiment_design.md`(Q19)를
  설계 담당에게 공유하고 회신을 전달
- 판정 요지: **W5 = RESOLVED** · Q19.1 = **(a) O1 먼저**(O3는 이후 core
  oracle) · Q19.2 = **(iii) 2단계** — E2E-v1-M(계측 성립, control 8종) 후
  E2E-v1-C(능력, **동결 N=20, PASS≥16, final ERROR=0, unexpected
  UNSCORABLE=0**) · Q19.3 = 시행 주체 (a) H1a 방식 + 평가 대상 (c) 병행
  보고(단 **certified-only를 primary로 금지**, primary는 direct match)
- 저장: 트랜스크립트 verbatim 추출(M10). 본문 sha256: `47b875d520443e6cac7d7e044c49a632a1ae06853f1f200f75d6aa06b8baf453`.
  뒤따른 사용자 지시("검증 설계 -> 검증 -> 검증된 내용 저장")는 분리

## 운영 세션의 저장 전 검증 (2026-08-22)

| # | 판정문 주장 | 검증 | 결과 |
|---|---|---|---|
| V1 | 16/20의 one-sided 95% lower bound ≈ 0.599 → "80%는 benchmark 기준이지 모집단 주장 아님" | Clopper-Pearson 독립 재계산(이분법) | ✅ **0.5990** 정확 일치 |
| V2 | UCR 반례: PASS 20/FAIL 0/UNSCORABLE 80 → 조건부 100% vs UCR 20% | 산술 | ✅ |
| V3 | 의존 분해: O1·O3 각 5 family, 합집합 7, 공유 {Canonicalizer, Evaluator, ScopeTopology} → 병행 시 신규 4종 동시 유입 | 집합 재계산 | ✅ 산술 일치 |
| V3b | "O1의 binding family를 O2가 재사용" | manifest 원문 — O2 `world_sensitive_binding`(yaml:122) + evaluation_target `binding` | ✅ |
| V4 | W5 Boolean 5건(위조·오subject·구revision·무효verdict·raw혼합 → 인증 불가) | **각각 핀 테스트 실존 확인**: hand_written_refused / different_claim / stale_revision / assurance_caps / mixing_does_not_promote | ✅ 5/5 — 판정문 스스로 밝혔듯 Wolfram 검증은 계약의 논리 충분성이고, 구현 증거는 이 테스트+공격 5/5 기록 |
| V5 | P14 재감사 — 새 판정이 금지한 표현이 기존 문서에 있는가 | `O3 먼저`·certified-primary grep | ✅ 0건 (상신문 §5의 O3 선호는 격리 절이며 판정이 명시 반려 — 원문 보존) |

## 이 판정이 부과한 재사용 가능한 규율 (기록)

- **estimand 3분리**: 계측(M1) ⊅ 능력(M2) ⊅ 인증(M3) — 한 지표로 합치지
  않는다. 이름도 분리: E2E-v1-M / E2E-v1-C.
- **UCR(Usable Correct Rate)** = PASS / N_preregistered — UNSCORABLE·ERROR를
  분모에서 버리는 순간 측정 실패가 숨는다.
- **UNSCORABLE ≠ semantic failure** (= measurement incompleteness, capability
  주장 차단) — H1a의 `material_unavailable ≠ failed`와 같은 분리.
- **ERROR 재실행 규약**: 출력 생성 후 evaluator 실패 → 모델 재실행 금지,
  evaluator만 재실행. 생성 전 인프라 실패 → 사전등록된 mechanical retry 1회.
- **2×2 (Certified × OracleCorrect)** — B셀(Certified+Wrong)이 certification
  false-positive의 제품 지표. 상위 목적(피드백·인과)의 첫 데이터셋.
- **governance는 estimand에 비례** — H1a의 prompt-policy 감사 기계를 복제하지
  않는다.
- §12 외부 판정 필요 목록(estimand/oracle/threshold/N/primary 변경, oracle
  역류, Certified-gate) vs 운영 재량(클래스명·필드명·helper·caching·logging).

## 다음 단계 (판정 순서)

1. **Stage 1 (E2E-v1-M)**: Evaluate 모듈 + control 8종(PASS 2·FAIL 2·
   UNSCORABLE 2·ERROR 2, ERROR는 경계 negative로) + oracle 격리 가드 +
   정규화 음성 control → measurement_qualification 판정
2. **Stage 2 (E2E-v1-C)**: O1 fixture 20종 동결(사전등록 scope는 §11 목록만)
   → cold subagent 실행 → direct/coverage/yield 3지표 + 2×2 보고
3. O3는 O1 성립 후 (구현 준비 ≠ 실험 순서 — §13)

---

## 판정문 원문 (verbatim)

> **W5는 해소로 인정. Q19.1 = (a) O1 먼저. Q19.2 = (iii) 2단계. Q19.3 = 시행 주체 (a) + 평가 대상 (c).**
> 단, **“E2E-v1 성립”을 계측 성립과 semantic capability 성립으로 분리**하고, certified-only 성능을 primary metric으로 사용하지 않는 조건을 붙입니다.

요청서가 보고한 before-P1 구현과 P1 관통은 이 방향과 정합적입니다.

---

# 1. W5 — 해소 인정

## 판정: **RESOLVED**

요청서상 수정된 certification contract는 이제 단순:

```text
caller says PASS
→ Certified
```

가 아니라:

```text
authentic certificate
∧ subject binding
∧ graph revision binding
∧ verdict/decider/assurance validity
∧ no raw-verdict contamination
→ certifying authority
```

입니다.

이를 Wolfram에 Boolean contract로 넣어 검증한 결과:

```text
ForgeryCannotCertify       = True
WrongSubjectCannotCertify  = True
WrongRevisionCannotCertify = True
InvalidVerdictCannotCertify = True
RawMixedCannotCertify      = True
```

였습니다.

즉 제가 이전에 지적했던 핵심 결함:

[
WellFormedVerdict \not\Rightarrow AuthenticVerdict
]

가 이제:

[
Certified =
Authentic
\land SubjectBound
\land RevisionBound
\land Valid
]

로 수정됐습니다.

특히 서버측 `issue_claim_certificates`가 **raw bundle + claim만 받고 verdict를 in-process에서 계산**하도록 바뀐 것은 중요한 개선입니다. 클라이언트가 normalizer의 “응답”을 다시 제출하도록 하지 않은 것도 W5의 재발을 막습니다.

따라서 W5는 더 이상 E2E-v1 blocker가 아닙니다.

다만 이 판정에서 Wolfram이 검증한 것은 **제시된 인증 계약의 논리적 충분성**입니다. HMAC 구현 자체의 암호학적 구현 감사를 Wolfram이 한 것은 아닙니다. 그 구현 증거는 요청서의 5종 공격 5/5 차단 및 테스트 기록에 의존합니다.

---

# 2. Q19의 문제를 먼저 추상화

E2E-v1에는 사실 서로 다른 세 estimand가 있습니다.

### M1 — Measurement / instrumentation

> NL input부터 evaluator result까지 시스템이 **측정 가능한 형태로 관통하는가?**

### M2 — Semantic compilation capability

> LLM이 만든 predicted IR이 external formal oracle과 **실제로 일치하는가?**

### M3 — Certification behavior

> semantic output 중 어떤 것이 certification을 통과하며, 통과한 것의 correctness는 어떤가?

이 셋을 한 지표로 합치면 안 됩니다.

Wolfram 형식 검사:

```text
InstrumentationDoesNotImplyCapability = True
CapabilityDoesNotImplyCertification   = True
DirectAndCertifiedTargetsAreDistinct  = True
```

즉:

[
Instrumentation \not\Rightarrow SemanticCorrectness
]

이고

[
SemanticCorrectness \not\Rightarrow Certification
]

입니다.

이 때문에 Q19.2의 답은 거의 자동으로 **2단계**가 됩니다.

---

# 3. Q19.1 — 어느 Oracle부터 시작하는가

## 판정: **(a) O1 Quantifier Scope 먼저**

O3가 나쁜 선택이라는 뜻은 아닙니다. 오히려 O3의 `formula_generated` 성격은 강점입니다. 요청서가 말한 “gold의 구조적 확실성이 높다”는 이유도 타당합니다.

하지만 **첫 E2E의 목적은 최대 coverage가 아니라 failure attribution 가능성 확보**여야 합니다.

### O1이 첫 번째로 더 좋은 이유

O1:

```text
Quantifier
Variable
Binding
Scope topology
Canonicalizer
Evaluator
```

를 시험합니다.

O3:

```text
ModalOperator
LogicalOperator
Scope topology
Canonicalizer
Evaluator
```

를 시험합니다.

제가 이 supplied dependency decomposition을 Wolfram에서 집합으로 비교하면:

```text
O1 primitive families = 5
O3 primitive families = 5
O1 + O3 parallel union = 7
shared = {Canonicalizer, Evaluator, ScopeTopology}
```

입니다.

즉 O3가 단순히 “더 어렵기 때문에 더 좋은 최초 테스트”인 것은 아닙니다.

오히려 O1과 O3를 처음부터 병행하면:

```text
Quantifier
VariableBinding
ModalOperator
LogicalOperator
```

라는 서로 다른 신규 capability가 동시에 들어옵니다.

첫 실패가 났을 때 diagnosis surface가 커집니다.

---

## O1의 추가 장점

O1이 검증하는 `VariableBinding`은 O2의 world-variable / intensional binding에서도 다시 사용됩니다.

Wolfram에 supplied dependency를 넣었을 때:

```text
O1ProvidesBindingFamilyUsedByO2 = True
```

입니다.

따라서 manifest의:

```text
O1 → O2 → O3
```

순서는 단순 임의 ordering이라기보다 **shared semantic primitive를 점진적으로 검증하는 순서**로 읽을 수 있습니다.

### 따라서

```yaml
oracle_rollout:
  first: O1
  parallel_O1_O3_initially: false
```

로 판정합니다.

O1 E2E가 성립한 뒤 O3를 진행하는 것은 적극 권장할 수 있습니다.

---

# 4. Q19.2 — “E2E-v1 달성” 정의

## 판정: **(iii) 2단계**

이 부분은 반드시 이름도 분리하는 것이 좋습니다.

```text
E2E-v1-M = measurement-qualified
E2E-v1-C = capability-qualified
```

처럼요.

---

# Stage 1 — Measurement Qualification

목적:

> semantic capability를 평가하기 전에 **측정기가 실제로 작동하는지** 검증.

이 단계에서는 모델 성능에 관한 주장을 하지 않습니다.

## 권장 규모

**8개 qualification controls** 정도면 충분합니다.

예:

| 예상 결과수     |   |
| ---------- | - |
| PASS       | 2 |
| FAIL       | 2 |
| UNSCORABLE | 2 |
| ERROR      | 2 |

단, ERROR를 만들기 위해 production pipeline을 인위적으로 깨라는 뜻은 아닙니다.

- PASS/FAIL: canonical evaluator fixture
- UNSCORABLE: protocol상 명시적으로 score 불가능한 controlled fixture
- ERROR: evaluator boundary의 mutation/negative test

로 분리할 수 있습니다.

### Stage 1 PASS 조건

```text
8/8 expected outcome category
+
oracle leakage guards PASS
+
canonicalization negative tests PASS
+
no unexpected runtime failure
```

이면:

```yaml
measurement_qualification: PASS
```

입니다.

이때만:

> **“E2E measurement path가 성립했다.”**

고 말합니다.

아직:

> “semantic compiler가 잘한다.”

라고 하면 안 됩니다.

---

# Stage 2 — O1 Capability Cohort

## 최소 규모: **N = 20 frozen oracle fixtures**

여기서 중요한 것은 20이 확률 모집단을 추정하기 위한 통계적 표본이라기보다 **고정 benchmark cohort**라는 점입니다.

조건:

- 20개 모두 결과 보기 전에 동결
- Stage 1 control과 중복 금지
- oracle locator 고정
- expected IR 고정
- prompt/schema/model/config 고정
- 결과 후 fixture 교체 금지
- 결과 후 N 확대 금지

---

## Primary metric

단순:

```text
PASS / (PASS + FAIL)
```

만 사용하면 안 됩니다.

왜냐하면 UNSCORABLE/ERROR를 분모에서 버리는 순간 측정 실패를 숨길 수 있기 때문입니다.

Wolfram 예:

```text
PASS=20
FAIL=0
UNSCORABLE=80
```

이면:

```text
conditional accuracy = 100%
전체 preregistered 기준 usable correct rate = 20%
```

입니다.

따라서 primary는:

[
UCR =
\frac{PASS}{N\_{\text{preregistered}}}
]

즉 **Usable Correct Rate**를 권합니다.

---

## Stage 2 acceptance

초기 E2E-v1 engineering criterion으로:

```yaml
N: 20

acceptance:
  PASS: ">= 16"
  final_ERROR: 0
  unexpected_UNSCORABLE: 0
```

즉:

[
PASS \ge 16/20 = 0.80
]

입니다.

### 중요한 표현 제한

16/20을 통과했다고:

> “일반적인 semantic compilation accuracy가 80% 이상임을 통계적으로 증명했다”

라고 쓰면 안 됩니다.

Wolfram exact binomial 계산에서 16/20의 one-sided 95% lower bound는 약:

[
0.599
]

입니다.

따라서 80%는 **benchmark acceptance criterion**이지 population lower-bound claim이 아닙니다.

---

# 5. UNSCORABLE 규약

Capability cohort의 fixture는 **사전에 oracle-scorable로 qualification**되어 있어야 합니다.

그러므로 Stage 2에서 UNSCORABLE이 발생했다면:

```text
model semantic failure
```

라고 읽으면 안 됩니다.

정확한 의미:

```text
measurement contract failed for this preregistered item
```

입니다.

따라서:

```yaml
UNSCORABLE:
  counts_as_model_FAIL: false
  may_be_dropped: false
  may_be_replaced_posthoc: false
  blocks_E2E_v1_capability_claim: true
```

를 권합니다.

즉:

> **UNSCORABLE은 semantic failure의 증거가 아니라 measurement incompleteness의 증거입니다.**

H1a의 `material_unavailable ≠ failed`와 같은 종류의 분리입니다.

---

# 6. ERROR 규약

ERROR 역시 FAIL로 변환하지 않습니다.

```yaml
ERROR:
  semantic_verdict: none
  execution_failure: true
  drop_from_record: false
```

### 재실행 규칙은 사전등록

두 경우를 나누는 것이 좋습니다.

#### 모델 output이 이미 생성된 후 evaluator만 실패

모델을 다시 돌리지 않습니다.

```text
stored output
→ evaluator만 동일 input으로 재실행
```

#### 모델 output 자체가 생성되기 전에 infrastructure failure

한 번의 **mechanical retry** 정도는 사전등록할 수 있습니다.

조건:

- 동일 model/config
- 동일 prompt
- 동일 fixture
- 동일 seed가 존재하면 동일 seed
- 최초 ERROR도 기록 보존

두 번째도 실패하면 final ERROR입니다.

---

# 7. Q19.3 — 시행 주체

## 판정: **(a) H1a 방식 유지**

즉:

```text
cold subagent
schema forced
model fixed
tool unavailable
fresh context
oracle unavailable
certifier hidden information unavailable
```

가 적절합니다.

이유는 간단합니다.

이번 estimand는:

> **주어진 NL source에서 LLM이 intended semantic IR을 생성할 수 있는가**

이기 때문입니다.

Oracle이나 certification result가 output 생성 전에 들어오면 estimand가:

```text
independent semantic compilation
```

에서:

```text
oracle-assisted repair
```

로 바뀝니다.

따라서 기존 invariant:

```text
Oracle ─X→ Refine
Oracle ─X→ Verify
```

는 그대로 유지합니다.

---

# 8. Q19.3 — 평가 대상

## 판정: **(c) 둘 다 보고하되 반드시 estimand를 분리**

이 부분은 매우 중요합니다.

### Metric A — Direct Compilation

```text
Predicted IR
     ↓
Canonicalize
     ↓
Oracle comparison
```

이것이 **semantic compiler capability의 primary estimand**입니다.

[
M\_D = P(\text{oracle match})
]

---

### Metric B — Certification-conditioned

```text
Predicted IR
     ↓
Verify / Certified Projection
     ↓
Oracle comparison
```

이것은 다른 질문입니다.

[
M\_C = P(\text{oracle match}\mid Certified)
]

Wolfram formal check에서도 direct와 certified target은 동치가 아니었습니다.

---

## certified-only 결과만 보고하면 생기는 문제

예를 들어:

```text
20 outputs
↓
4개만 Certified
↓
그 4개 전부 oracle PASS
```

이면:

```text
Certified accuracy = 100%
```

라고 쓸 수 있지만 전체 system yield는:

```text
4 / 20 = 20%
```

입니다.

따라서 세 지표를 함께 보고하십시오.

### 1. Direct semantic match

[
DirectMatch =
\frac{DirectPASS}{N}
]

### 2. Certification coverage

[
CertificationCoverage =
\frac{Certified}{N}
]

### 3. Certified-correct yield

[
CertifiedCorrectYield =
\frac{Certified \land OraclePASS}{N}
]

그리고:

[
P(PASS\mid Certified)
]

는 **secondary diagnostic**으로만 둡니다.

---

# 9. 이렇게 하면 아주 유용한 2×2가 생긴다

각 LLM output을:

| Oracle correctOracle wrong |   |   |
| -------------------------- | - | - |
| **Certified**              | A | B |
| **Not Certified**          | C | D |

로 분류할 수 있습니다.

각 cell의 의미:

### A — Certified + Correct

이상적인 경우.

### B — Certified + Wrong

**가장 중요한 certification false-positive**.

즉 semantic defect를 certifier가 통과시킨 것입니다.

### C — Not Certified + Correct

certifier가 너무 보수적이거나 source-support contract가 semantic correctness와 다른 것을 측정한다는 신호.

### D — Not Certified + Wrong

정상적인 rejection 후보.

이 표가 사실상 지금 프로젝트가 원하는:

> **LLM output → structured feedback**

의 첫 제품 지표가 됩니다.

---

# 10. 이것이 상위 목적과 특히 잘 맞는 이유

H1a에서는 주로:

```text
prompt policy
→ behavioral response
```

를 봤습니다.

E2E-v1에서는 처음으로:

```text
LLM semantic proposal
       ↓
formal external oracle
       ↓
semantic correctness

        AND

LLM semantic proposal
       ↓
Verify / Certification
       ↓
certification result
```

두 경로를 동시에 얻습니다.

그러면 이후 다음을 분석할 수 있습니다.

[
P(Correct\mid Certified)
]

[
P(Certified\mid Correct)
]

[
P(Certified\mid Incorrect)
]

즉 단순 “LLM accuracy”보다 **feedback/certifier가 실제 오류를 얼마나 잘 분리하는가**라는 프로젝트 상위 목적에 직접 연결됩니다.

---

# 11. 사전등록 / freeze

## 판정: **예. 다만 H1a 전체 governance를 복제하지 않는다**

사전등록할 것은 다음 정도면 충분합니다.

- oracle ID / source locator
- fixture IDs + hashes
- expected canonical IR
- qualification vs capability fixture 분리
- model/version/config
- model-facing prompt hash
- output schema
- canonicalization profile
- evaluation rules
- PASS/FAIL/UNSCORABLE/ERROR mapping
- retry policy
- N=20
- acceptance 16/20
- direct/certified metrics
- oracle leakage prohibition
- no post-result fixture replacement/N increase

반대로 H1a에서 필요했던 모든 prompt-policy audit machinery를 E2E-v1에 다시 가져오면 안 됩니다.

이번 실험의 핵심 manipulation이 prompt policy가 아니기 때문입니다.

즉 governance도 **estimand에 비례**해야 합니다.

---

# 12. 외부 판정이 다시 필요한 변경 범위

다음은 외부 판정 대상으로 남깁니다.

- primary estimand 변경
- oracle 변경
- acceptance threshold 변경
- 결과 후 N 변경
- direct → certified-only로 primary metric 변경
- Oracle → Refine/Verify feedback 허용
- Certified-gate authority 전환

반면:

- 내부 클래스명
- JSON field명
- evaluator helper 분리
- caching
- logging

같은 구현 세부는 운영 세션이 결정해도 됩니다.

---

# 13. IR 구현 병행은 허용

요청서에서 P3 IR primitive를 Q19과 병행 착수했다고 했는데, 이는 문제 없습니다.

왜냐하면 Q19의 어떤 선택을 하더라도 최소:

```text
Variable
Binding
Quantifier
Scope
PredicateApplication
```

은 필요하기 때문입니다.

다만 O3용:

```text
ModalOperator
LogicalOperator
```

가 구현됐다는 이유로 O3 cohort까지 먼저 실행할 필요는 없습니다.

**implementation readiness와 experimental sequencing은 다른 문제**입니다.

---

# 14. 최종 판정

```yaml
D-E2E-v1-19:

  before_P1:
    W5:
      status: RESOLVED
      basis:
        - signed certificate
        - host-only signing key
        - domain separation
        - subject fingerprint binding
        - graph revision binding
        - verdict/decider/assurance validation
        - raw verdict path remains diagnostic_only
        - server-side verdict production

  Q19_1:
    decision: A
    first_oracle: O1
    reason:
      - progressive primitive validation
      - variable/binding foundation reused by O2
      - lower simultaneous novelty than O1+O3 parallel rollout
    O3:
      status: later_core_oracle

  Q19_2:
    decision: III_TWO_STAGE

    stage_1:
      name: measurement_qualification
      suggested_controls: 8
      capability_claim_allowed: false
      required:
        - expected PASS branch works
        - expected FAIL branch works
        - UNSCORABLE branch works
        - ERROR branch works
        - oracle isolation passes
        - canonicalization negative controls pass

    stage_2:
      oracle: O1
      N: 20
      fixed_before_results: true

      acceptance:
        PASS_min: 16
        final_ERROR: 0
        unexpected_UNSCORABLE: 0

      interpretation:
        threshold_kind: engineering_benchmark
        population_accuracy_claim: forbidden

    result_handling:
      FAIL:
        semantic_failure: true

      UNSCORABLE:
        semantic_failure: false
        measurement_failure: true
        drop_or_replace: false

      ERROR:
        semantic_failure: false
        execution_failure: true
        drop: false
        retry: preregistered_mechanical_only

  Q19_3:
    trial_subject:
      decision: A
      cold_subagent: true
      schema_forced: true
      oracle_access: false
      certifier_hidden_info_access: false

    evaluation_target:
      decision: C

      primary:
        direct_predicted_IR_vs_oracle: true

      additional:
        certification_coverage: true
        certified_correct_yield: true
        conditional_accuracy_given_certified:
          report: true
          primary: false

    preregistration:
      required: true
      scope: estimand_and_measurement_contract_only

  authority:
    Certified_gate_transition:
      status: NOT_DECIDED_HERE
```

## 핵심 한 문장

**E2E-v1의 첫 목표는 “O1에서 LLM이 잘 맞히는가” 하나가 아니라,** **`LLM output → semantic IR → external oracle score`****와** **`LLM output → certification`****을 서로 오염 없이 동시에 관측할 수 있는 계측계를 먼저 성립시키고, 그 다음 고정된 20개 O1 fixture에서 semantic capability와 certification utility를 별도 estimand로 측정하는 것입니다.**

이렇게 설계하면 E2E-v1은 단순 semantic benchmark가 아니라 이후 **LLM에게 어떤 feedback을 줘야 하는지, certification이 실제 오류를 얼마나 분리하는지**를 인과적으로 연구할 수 있는 첫 데이터셋이 됩니다.
