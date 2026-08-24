# DESIGN DECISION — D-E2E-v1-25: oracle granularity와 측정 계약 (Q25 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_folio_predicate_labels|D-24]] · **D-25** · 다음 [[DESIGN_DECISION_subject_dialect_expressiveness|D-26]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: 2026-08-23, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_oracle_granularity.md`
  (sha256 `8150ba41c2e332aecbbf7487aea8199397947f1dc9eb57ed9b391056b5cf17bd`)
- 요약:
  > **진단**: V2 측정 계약은 코호트 전체에 대해 satisfiable하지 않다
  > (최대 가능 PASS 5 < 16 — 수학적 불가). 이는 fixture 결함이 아니라
  > **DirectMatch가 O1 estimand보다 많은 의미 구조를 요구한 측정계약 결함**.
  > **Q25.1 = (d)=(a\*)** — `O1_SCOPE_PROJECTION_V1`: oracle·subject **양측**
  > 에서 scope-bearing 구조만 추출해 비교하는 **measurement function**
  > (formula 재작성 아님, 동치 주장 없음). retain: target 양화 종류·순서,
  > 부정, scope-bearing 함의, 제한/본문 관계, 결박. exclude: 사건/시간
  > 변수·∃, role 술어. FOLIO topology는 투영 후에도 구분 유지(104 반례
  > 재인용). primary metric 개명: `O1ScopeMatch`. **estimand 불변,
  > operationalization 변경** — 그 변경 승인이 이 판정이다(D-19 §12)
  > **Q25.2 = (d)** — template에 명명 규칙 추가 금지(annotator 규약 학습
  > 실험이 되므로). **exact predicate label을 primary score에서 제거**,
  > binding topology(occurrence·arity·인자 결박·제한/본문 위치)는 채점 유지.
  > P(x,y)≠P(y,x). 기존 D-24 codec은 삭제하지 않되 **진단 전용으로 강등**.
  > `predicate_arguments` 차원을 `predicate_label_identity`(DIAGNOSTIC_ONLY)
  > 와 `predicate_binding_topology`(SCORED)로 분리
  > **Q25.3 = (ii)** — control 2/3은 게이트의 정상 작동(측정계약 결함 발견).
  > **계약이 바뀌면 새 측정** — V3 후 control 재실행은 semantic retry 아님
  > (필수). V2 control 결과는 삭제하지 않고 역사적 증거로 보존
  > **Q25.4 = 강한 승인** — **Measurement Satisfiability Gate**: freeze 전에
  > "허용된 subject 언어 안에 PASS 가능한 출력이 최소 1개 존재"를 결정론적
  > hidden witness로 검증. witness는 절대 model-facing 금지(적격성 전용).
  > 실패 시 pre-freeze=INELIGIBLE / post-freeze pre-execution=
  > FROZEN_MEASUREMENT_DEFECT
  > **V3 재동결 필수**(V2는 SUPERSEDED_PRE_EXECUTION 보존; 신규 manifest·
  > 평가 profile·projection profile·사전등록 hash). 자격:
  > `O1_SCOPE_PROJECTION_QUALIFICATION_V1` P1~P6 + **PMB live control 2~3건
  > 신설**(N 밖) + FOLIO control 재실행. N=20·임계값 16/20·multi 4/5 유지.
  > 결과 보고 표기: "O1 quantifier-scope structural match rate"

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP로 Q25를 검토한 결과, 이번 문제는 **fixture 몇 건의 라벨 결함이 아니라 현재 `DirectMatch`가 O1의 estimand보다 더 많은 의미 구조를 요구하는 측정계약 결함**으로 보는 것이 맞습니다.

핵심 판정은 다음입니다.

> **Q25.1 = (d): (a)를 더 엄격하게 수정한 `O1_SCOPE_PROJECTION_V1`을 도입합니다.**
> full oracle formula를 “간략한 동치식”으로 재작성하는 것이 아니라, **oracle과 subject 양쪽에서 O1이 측정하려는 scope-bearing structure만 추출해 비교**합니다.
>
> **Q25.2 = (d): template에 추가적인 라벨 명명 규칙을 넣지 않습니다.** exact predicate-label equality를 O1의 acceptance metric에서 제거하고, predicate의 **binding/topology만 유지**합니다.
>
> **Q25.3 = (ii): control 2/3은 V2 측정계약의 결함을 정상적으로 발견한 것이며, V3 계약으로 수정한 뒤 control을 다시 실행하는 것은 semantic retry가 아닙니다.**
>
> **Q25.4 = 승인:** freeze 전에 `subject-passability`보다 조금 더 엄밀한 **Measurement Satisfiability Gate**를 필수화합니다.

현재 사실관계는 요청서가 잘 정리하고 있습니다. PMB 15건은 subject가 완벽히 지시를 따라도 neo-Davidsonian 사건/시간/role 구조 때문에 full structural DirectMatch에서 실패하고, FOLIO control 역시 라벨 선택만으로 2/3에 머뭅니다. 본 cohort는 아직 dispatch 0건입니다. 

---

# 1. 먼저: 현재 V2는 수학적으로 acceptance 불가능

현재 사실을 그대로 Wolfram에 넣으면:

```text
PMB 15건
→ 현재 full DirectMatch 계약에서는 전부 구조적으로 도달 불가능

FOLIO 5건만 최대 PASS 가능
```

이므로:

```text
CurrentFrozenContract_MaxPossibleMainPass = 5
AcceptanceRequires                         = 16
AcceptanceMathematicallyPossible           = False
```

입니다.

또 control:

```text
Observed = 2
Required = 3
GatePass = False
```

입니다.

따라서 이 상태에서 cohort를 실행하는 것은:

> 모델 능력을 측정하는 실험

이 아니라

> 이미 실패가 결정된 measurement contract를 실행하는 것

이 됩니다.

즉 **실행 차단은 정확합니다.**

---

# 2. Q25.1 — PMB F3 처리

## 판정: **(d) = (a*) `O1_SCOPE_PROJECTION_V1`**

단순히:

```text
PMB IR
→ event/time ∃ 삭제
→ role predicate 삭제
→ 다시 formula로 만들어 exact match
```

하는 것은 권하지 않습니다.

그렇게 하면 실제로 oracle formula를 우리가 다른 formula로 **재작성**하게 됩니다.

대신 다음처럼 합니다.

```text
Oracle IR ────────┐
                  ├─ O1 Scope Projection → Scope Signature
Subject IR ───────┘
                                  ↓
                               Compare
```

즉 projection은 **formula transformer가 아니라 measurement function**입니다.

---

# 3. 중요한 구분

### 금지

```text
Published PMB semantics
↓
“scope와 무관해 보이는 것을 삭제”
↓
새로운 gold logical form
```

그리고:

> “이 새 formula가 원래 PMB formula와 동치다.”

라고 주장하는 것.

---

### 허용

```text
Published PMB semantics
↓
O1에서 측정하지 않는 dimension을 평가에서 제외
↓
O1-specific structural signature
```

즉:

[
FullFormulaEquivalence
]

를 주장하지 않고:

[
SameO1ScopeSignature
]

만 주장합니다.

Wolfram에서도 nuisance node를 제거한 graph projection에서 **retained target operator의 ancestor/order 관계**를 보존하는 것은 가능하지만, 그것이 full formula의 논리적 동치를 뜻하지는 않는다고 분리됐습니다.

```text
TargetOrderPreserved = True

but

Projection ≠ proof of full logical equivalence
```

이 구분을 정본에 넣어야 합니다.

---

# 4. 무엇을 O1 projection에 남길 것인가

최소한 다음은 **반드시 유지**합니다.

```text
Quantifier type
Quantifier nesting/order
Negation
Restriction/body position
Variable binding
scope-bearing implication structure
```

즉:

```text
FORALL
EXISTS
NOT
IMPLIES
restriction/body edges
binding edges
```

가 핵심입니다.

Cardinal/proportional이 실제 fixture에 있다면 해당 operator type도 유지합니다.

---

# 5. 무엇을 nuisance로 제외할 수 있는가

O1의 declared estimand와 무관한:

```text
event variable
time variable
event-only existential
time-only existential

Agent
Experiencer
Stimulus
Theme
Time
EQU
TPR
...
```

등은 **O1 score에서 제외할 수 있습니다.**

단 조건이 있습니다.

> 제거 대상이라는 판정이 모델 출력이나 결과를 보고 정해져서는 안 됩니다.

즉 frozen rule이 필요합니다.

예:

```yaml
O1_SCOPE_PROJECTION_V1:

  retain:
    - target_quantifier
    - target_negation
    - scope_bearing_implication
    - restriction_body_relation
    - target_variable_binding

  ignore_for_scoring:
    - event_semantics_scaffolding
    - temporal_scaffolding
    - semantic_role_predicates
    - non_target_existentials
```

---

# 6. 여기서 `target quantifier` 정의가 중요

단순히:

```text
모든 EXISTS를 유지
```

하면 PMB 문제가 그대로 남습니다.

추천하는 기준은:

> **O1의 surface scope trigger에 대응하는 quantifier만 target operator로 취급**

하는 것입니다.

예:

```text
all
every
each
some
no
most
cardinal expression
negation
...
```

처럼 **동결된 scope-trigger lexicon/rule로 source text에서 식별 가능한 것**입니다.

이렇게 하면:

```text
event ∃
time ∃
```

처럼 overt quantifier-scope trigger에 대응하지 않는 PMB 내부 변수가 primary target에서 빠집니다.

---

# 7. D-24의 FOLIO topology는 여전히 살아 있어야 한다

이 projection을 너무 거칠게 만들면 안 됩니다.

예를 들어:

[
\forall x\exists y((A\land B)\to C)
]

와

[
\forall x(A\to\exists y(B\land C))
]

는 이전 Q24에서처럼 실제로 다를 수 있습니다.

Wolfram exhaustive finite-domain 검사에서도:

```text
EquivalentOnAll2ElementInterpretations = False
CountermodelCount = 104
```

였습니다.

따라서 projection 후에도:

```text
FORALL → EXISTS → IMPLIES
```

와

```text
FORALL → IMPLIES → EXISTS
```

는 달라야 합니다.

이번에도 간단한 structural signature로:

```text
FOLIO gold:
FORALL, EXISTS, IMPLIES

alternative:
FORALL, IMPLIES, EXISTS
```

를 비교하면 서로 다른 signature로 남습니다.

즉:

> **event semantics는 버리지만 scope-bearing topology는 버리지 않는다.**

가 경계입니다.

---

# 8. primary metric 명칭도 바꿔야 한다

현재:

```text
DirectMatch
=
full normalized IR structural identity
```

는 더 이상 정확한 이름이 아닙니다.

권장:

```text
O1ProjectedDirectMatch
```

또는 더 명확하게:

```text
O1ScopeMatch
```

입니다.

### BEFORE

[
Score =
ExactStructuralMatch(
CanonicalIR_{subject},
CanonicalIR_{oracle}
)
]

### AFTER

[
Score =
ExactStructuralMatch(
ScopeProjection(IR_{subject}),
ScopeProjection(IR_{oracle})
)
]

중요하게 **projection 이후에는 여전히 exact structural match**입니다.

즉 fuzzy scoring을 도입하는 것이 아닙니다.

---

# 9. estimand가 바뀌는가?

## 판정: **declared estimand는 유지, operational metric은 변경**

기존 O1:

> Quantifier Scope

를 그대로 유지합니다.

오히려 full neo-Davidsonian structure를 요구했던 V2가 declared estimand보다 넓었습니다.

따라서:

```yaml
estimand:
  sentence_level_quantifier_scope: unchanged

operationalization:
  old: full_IR_DirectMatch
  new: O1_Scope_Projected_DirectMatch
```

라고 기록하면 됩니다.

다만 D-19에서 primary metric 변경을 외부 판정 사안으로 두었으므로 **Q25가 바로 그 변경 승인**입니다.

---

# 10. N과 threshold는 유지

변경하지 않습니다.

```yaml
N: 20

acceptance:
  overall_PASS_min: 16
  FOLIO_multi_quantifier_PASS_min: 4_of_5
  final_ERROR: 0
  unexpected_UNSCORABLE: 0
```

V2 결과가 하나도 없으므로 기존 결과와 metric을 섞는 문제도 없습니다. 

---

# 11. Q25.2 — F1/F2 라벨 문제

## 판정: **(d) exact label을 O1 primary score에서 제거**

저는 `(a)`처럼 subject prompt를 더 세밀하게 만드는 것을 권하지 않습니다.

예를 들어:

```text
multiword는 붙여 써라
head noun만 써라
shortest span을 선택해라
```

를 계속 추가하면 결국 LLM에게 **FOLIO annotator의 naming convention을 학습시키는 실험**이 됩니다.

그건 O1이 아닙니다.

---

# 12. F1은 실제로 label이 식별되지 않는 사례

현재 CTRL-02에서:

```text
lab
equipped_in_lab
```

둘 다 현 template을 준수할 수 있습니다.

이를 Wolfram에서 단순하게 모델링하면:

```text
NumberOfCompliantLabels = 2
UniqueCompliantLabel     = False

CompliantButDifferentScoresExist = True
```

입니다.

즉:

[
TemplateCompliance
\not\Rightarrow
UniqueScoredLabel
]

입니다.

이 상태에서 exact string match는 semantic capability가 아니라 **arbitrary naming choice**를 점수에 섞습니다.

---

# 13. 따라서 label은 어떻게 처리할까

O1 primary scoring에서는:

```text
predicate lexical identity
```

를 제거합니다.

대신 다음은 유지합니다.

```text
predicate occurrence
arity
argument incidence
variable binding
restriction/body location
scope position
```

즉:

```text
Zorble(x)
```

와:

```text
zorble(x)
```

뿐 아니라 현재 O1 metric에서는 필요하다면:

```text
Lab(x)
```

와:

```text
equipped_in_lab(x)
```

도 동일한 **predicate slot**로 볼 수 있습니다.

하지만:

```text
P(x,y)
```

와:

```text
P(y,x)
```

는 여전히 달라야 합니다.

---

# 14. 이것이 semantic aliasing인가?

일반 시스템이라면 그럴 수 있습니다.

하지만 O1에서는 아닙니다.

왜냐하면 선언된 estimand가:

```text
predicate lexical semantics
WSD
paraphrase resolution
```

가 아니라:

```text
quantifier scope
operator nesting
binding
```

이기 때문입니다.

따라서 이것은:

> `dog = cat`

이라고 ontology에 주장하는 것이 아니라,

> **이 실험에서는 predicate lexical identity dimension을 채점하지 않는다**

는 뜻입니다.

Shared Kernel의 semantic alias가 아닙니다.

---

# 15. 기존 Q24 label codec은 어떻게 하나

삭제할 필요 없습니다.

다만 지위를 낮춥니다.

### 기존

```text
label codec
→ acceptance score에 load-bearing
```

### V3

```text
label codec
→ provenance / diagnostics / reachability support
```

PMB의 synset→lemma, FOLIO lowercase 같은 정보는 여전히 디버깅에 유용합니다.

하지만 O1 PASS/FAIL의 primary cause가 되지 않습니다.

---

# 16. `predicate_arguments` 차원 개정

기존 명칭이 의미를 혼동시킬 수 있습니다.

권장:

### BEFORE

```text
predicate_arguments
=
predicate label + argument structure
```

### AFTER

둘로 분리합니다.

```text
predicate_label_identity
→ DIAGNOSTIC_ONLY

predicate_binding_topology
→ SCORED
```

후자는:

* occurrence 수
* arity
* variable incidence
* restriction/body 위치

를 검사합니다.

이렇게 하면 scope와 binding은 계속 측정하면서 WSD/annotator naming은 제거됩니다.

---

# 17. Q25.3 — control 2/3의 지위

## 판정: **(ii)**

이번 2/3은:

> LLM이 capability test에서 실패했다

는 결과로 해석하면 안 됩니다.

정확한 의미는:

> **V2 measurement contract가 model-facing dialect와 oracle dialect를 일치시키지 못했다는 것을 qualification control이 발견했다.**

입니다.

즉 control gate는 제대로 작동했습니다.

---

# 18. control 재실행은 semantic retry인가?

## 아닙니다.

Wolfram으로 상태를 분리하면:

```text
same fixture + same measurement contract + result 다시 얻기
→ retry

same fixture + changed measurement contract
→ new measurement
```

입니다.

결과:

```text
SameItemDifferentMeasurementContractIsSameTrial = False
OldControlResultRemainsHistoricalEvidenceAboutOldContract = True
NewControlRunNeededToQualifyNewContract = True
```

따라서 V3로 고친 후 control을 다시 실행해야 합니다.

---

# 19. V2 control 결과는 삭제하지 않는다

다음처럼 보존합니다.

```yaml
V2_controls:
  result: 2_of_3
  interpretation:
    model_capability_failure: false
    measurement_contract_failure: true

  superseded_by:
    D-E2E-v1-25
```

이 기록이 오히려 중요합니다.

왜 V3 metric이 생겼는지를 설명하는 직접 증거입니다.

---

# 20. Q25.4 — 신규 pre-freeze gate

## 판정: **강하게 승인**

다만 이름을:

```text
subject-passability gate
```

보다:

# **Measurement Satisfiability Gate**

로 두는 것을 권합니다.

검사하려는 것은:

> 모델이 실제로 잘 맞힐 것인가?

가 아니기 때문입니다.

검사하려는 것은:

> **허용된 subject language 안에 이 fixture를 PASS시킬 수 있는 출력이 최소 하나라도 존재하는가?**

입니다.

---

# 21. 핵심 정의

fixture (f)에 대해:

[
\exists y \in SubjectLanguage
:
Score(y,Oracle_f)=PASS
]

가 가능한지를 검사합니다.

없으면:

```text
MEASUREMENT_UNSATISFIABLE
```

입니다.

이 fixture는 모델 성능과 무관하게 실패가 예정되어 있으므로 cohort에 들어가면 안 됩니다.

---

# 22. 실제 구현은 더 간단하게 가능

LLM에게 물어볼 필요가 없습니다.

hidden deterministic witness를 만듭니다.

```text
External Oracle
      ↓
Oracle Adapter
      ↓
Frozen O1 Projection
      ↓
Subject-dialect canonical witness
      ↓
Subject schema validation
      ↓
Evaluator
```

그리고:

```text
witness score == PASS?
```

를 봅니다.

### PASS

fixture가 최소한 측정 가능한 상태.

### FAIL

fixture 자체가 contract상 불가능.

---

# 23. 중요한 보안/실험 경계

이 witness는 **절대 model-facing이 아닙니다.**

```text
Measurement qualification only
```

입니다.

금지:

```text
Witness → Refine prompt
Witness → subject context
Witness → repair feedback
```

허용:

```text
Witness → fixture eligibility gate
```

뿐입니다.

그러면 oracle leakage가 발생하지 않습니다.

---

# 24. 이 gate가 F3을 잡았을 방식

V2에서는 PMB oracle을 subject dialect에 넣으려 하면:

```text
event existential required
time existential required
role predicate required
```

인데 subject schema/template은 그런 출력을 허용하지 않습니다.

따라서:

```text
no valid subject witness
→ MEASUREMENT_UNSATISFIABLE
```

가 됩니다.

즉 15/15가 freeze 전에 차단됐을 것입니다.

---

# 25. V3에서는 반대로

O1 projection을 적용하면:

```text
PMB full IR
↓
O1 scope signature
```

가 subject dialect에서도 표현 가능해야 합니다.

hidden witness가:

```text
schema valid
+
projection score PASS
```

하면 fixture를 freeze할 수 있습니다.

---

# 26. Measurement Satisfiability Gate의 최소 검사

```yaml
MEASUREMENT_SATISFIABILITY_V1:

  required:

    oracle_adapter_success: true

    oracle_projection_success: true

    subject_dialect_expressible: true

    subject_schema_valid: true

    hidden_witness_can_score_PASS: true

    no_oracle_only_required_vocabulary: true

    no_unsupported_scored_operator: true
```

마지막 두 개는 projection 이후의 **scored dimensions에 대해서만** 적용하면 됩니다.

---

# 27. V3 re-freeze 절차

이번 변경은 D24보다 범위가 큽니다.

왜냐하면 fixture 몇 건뿐 아니라 **primary scoring profile 자체가 바뀌기 때문**입니다.

따라서 V2 manifest 일부만 고치지 않습니다.

### V2

```text
status:
SUPERSEDED_PRE_EXECUTION
```

으로 보존.

### V3

새로운:

```text
manifest hash
evaluation profile hash
projection profile hash
preregistration hash
```

를 만듭니다.

fixture source bytes 자체가 바뀌지 않는 항목은 기존 commitment hash를 그대로 사용할 수 있습니다.

---

# 28. V3에서 다시 해야 하는 테스트

Stage 1 8/8 전체를 폐기할 필요는 없습니다.

그건 evaluator 기본 boundary를 검증했습니다.

하지만 이번에 **새 projection layer**가 measurement path에 들어옵니다.

따라서 별도 자격 gate를 추가해야 합니다.

## `O1_SCOPE_PROJECTION_QUALIFICATION_V1`

최소 다음 정도면 됩니다.

### P1 — nuisance invariance

PMB event/time/role 구조를 추가해도 동일 scope signature.

```text
expected: PASS
```

### P2 — quantifier swap

```text
FORALL → EXISTS
```

를:

```text
EXISTS → FORALL
```

로 바꾸면:

```text
expected: FAIL
```

### P3 — negation movement

```text
NOT(FORALL(...))
```

vs:

```text
FORALL(... NOT ...)
```

```text
expected: FAIL
```

### P4 — FOLIO topology

```text
FORALL → EXISTS → IMPLIES
```

vs:

```text
FORALL → IMPLIES → EXISTS
```

```text
expected: FAIL
```

### P5 — label-only variation

```text
Lab
equipped_in_lab
```

동일 topology:

```text
expected O1 score: PASS
```

### P6 — target quantifier deletion

target operator 하나 삭제:

```text
expected: FAIL
```

이 정도면 충분합니다.

---

# 29. 실제 source control도 하나 빠졌었다

이번 F3이 늦게 발견된 이유는 요청서대로 live control이 전부 FOL형이었기 때문입니다. 

V3에서는 적어도:

```text
PMB live projection controls: 2~3
FOLIO live controls: 기존 3
```

를 cohort N 밖에서 실행하는 것을 권합니다.

PMB control은:

1. PMB full event semantics → correct scope signature PASS
2. target scope mutation → FAIL

정도만 있어도 현재 blind spot을 직접 막습니다.

---

# 30. 기존 threshold

V3에서도 유지 가능합니다.

```yaml
Stage2:
  N: 20

  acceptance:
    O1ScopeMatch_PASS_min: 16

    FOLIO_multi_quantifier:
      N: 5
      PASS_min: 4

    final_ERROR: 0
    unexpected_UNSCORABLE: 0
```

단 결과 보고에서는 더 이상:

```text
full semantic IR accuracy
```

라고 쓰면 안 됩니다.

정확한 표현은:

> **O1 quantifier-scope structural match rate**

입니다.

---

# 최종 판정

```yaml
D_E2E_v1_25:

  diagnosis:
    V2_measurement_contract:
      satisfiable_for_full_cohort: false

    evidence:
      PMB_full_granularity_mismatch: true
      FOLIO_label_indeterminacy: true
      main_cohort_dispatched: false

  Q25_1:
    decision: D
    refinement_of: A

    profile:
      id: O1_SCOPE_PROJECTION_V1

    interpretation:
      formula_rewrite: false
      measurement_projection: true
      full_logical_equivalence_claim: false

    retain:
      - target_quantifier_type
      - target_quantifier_order
      - negation_scope
      - scope_bearing_implication
      - restriction_body_relation
      - target_variable_binding

    exclude_from_primary_score:
      - event_variables
      - time_variables
      - event_only_existentials
      - time_only_existentials
      - semantic_role_predicates
      - non_target_event_structure

    FOLIO_gold_topology:
      retain: true

    primary_metric:
      old: FullIR_DirectMatch
      new: O1ScopeMatch

    estimand:
      changed: false
      operationalization_changed: true

  Q25_2:
    decision: D

    subject_template:
      add_join_rule: false
      add_head_noun_rule: false

    predicate_label_identity:
      primary_score: false
      diagnostic_only: true

    predicate_binding_topology:
      scored: true

    existing_source_codecs:
      retain_for_diagnostics: true

  Q25_3:
    control_2_of_3:
      valid_gate_signal: true
      interpretation: MEASUREMENT_CONTRACT_FAILURE

    rerun_after_V3:
      allowed: true
      required: true
      semantic_retry: false

    V2_results:
      delete: false
      historical_record: true

  Q25_4:
    MeasurementSatisfiabilityGate:
      required_before_freeze: true

      criterion:
        exists_valid_subject_witness_that_scores_PASS: true

      witness:
        deterministic: true
        hidden_from_subject: true
        model_facing: false

      on_failure:
        prefreeze: INELIGIBLE
        postfreeze_preexecution: FROZEN_MEASUREMENT_DEFECT

  amendment:
    V2:
      mutate: false
      status: SUPERSEDED_PRE_EXECUTION

    V3:
      new_freeze_required: true
      new_evaluation_profile_hash: true
      new_projection_profile_hash: true
      new_preregistration_hash: true

    qualifications:
      O1_scope_projection_controls: required
      PMB_live_controls: required
      FOLIO_controls_rerun: required

  acceptance:
    N: 20
    overall_PASS_min: 16
    FOLIO_multi_quantifier_PASS_min: 4_of_5
    final_ERROR: 0
    unexpected_UNSCORABLE: 0
```

가장 중요한 변화는 하나입니다.

> **O1에서 “oracle 전체 의미표상을 그대로 재현했는가?”를 묻지 말고, “외부 oracle이 규정한 quantifier/scope 구조를 정확히 재현했는가?”를 물어야 합니다.**

PMB의 event semantics나 FOLIO annotator의 predicate naming은 유용한 의미 정보이지만, 그것을 O1 acceptance에 넣는 순간 O1은 더 이상 quantifier-scope 실험이 아닙니다. 이번 Q25에서는 그 **oracle granularity와 estimand의 경계를 측정계약 수준에서 명시적으로 분리**하는 것이 맞습니다.
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | 최대 가능 PASS 5 < 16 (수학적 불가) | V2 manifest 기준 PMB 15건 전수 — subject-산출불가 요소(role/scaffold 술어·문장 밖 개념) 보유 재확인 | **CONFIRMED — 15/15, max=5** |
| V2 | 반례 104 (§7) | D-24 수신 검증 V1에서 256 해석 전수로 독립 확정한 값의 재인용 | **CONFIRMED (교차 참조)** |
| V3 | 투영 후 FOLIO topology 구분 유지 + nuisance 불변(P1) | 판정 retain 규칙의 시제품 투영 구현으로 기계 확인 | **CONFIRMED — ①topology 구분 유지 ②사건/시간/role 부가 시 signature 불변** |
| V4 | Stage 1 8/8 유지 | D-24 V4에서 확정(E2E-v1-M = D-19 명명 실물) | **CONFIRMED (교차 참조)** |
| V5 | P5(라벨만 상이→PASS)와 결박 topology 유지의 양립 | 동일 시제품 | **CONFIRMED — ③lab/equipped_in_lab 동일 signature ④P(x,y)≠P(y,x) 구분** |

주의 기록 (적용 시 구속되는 해석·미결 구현 사항):

1. **target quantifier ↔ surface trigger 대응 규칙이 기계적으로 미정의다.**
   판정 §6은 "동결된 scope-trigger lexicon으로 문장에서 식별"을 권하나,
   IR 양화사와 문장 trigger의 **정렬(alignment)**을 어떻게 결정론으로
   하는지는 열려 있다. 수신 검증의 시제품은 구조 휴리스틱(제한 True인
   ∃ 중 변수가 role 술어에만 쓰이는 것 제거)을 썼는데 이는 판정의
   lexicon 방식과 다르다 — V3 설계에서 규칙을 동결하고, 두 방식의 불일치
   사례가 있으면 재상신한다.
2. **차원 분리의 구현 위치**: `predicate_arguments` 차원은 커널
   (`cg_evaluate`)의 어휘다. 판정의 분리(SCORED/DIAGNOSTIC_ONLY)를 커널
   반입 없이 실험 폴더 계층(projection + 채점 배선)에서 실현해야 한다
   (Q22.3 §10의 커널 금지 원칙 유지).
3. **D-24 codec 강등**: `FOLIO_LABEL_LOWERCASE_V1`·lemma profile은
   acceptance 경로에서 빠지고 진단/도달성 지원으로 남는다 — D-24의 해당
   부분은 이 판정으로 **부분 supersede**된다(문서 자체는 불변 보존).
4. **PMB live control 신설(§29)은 코호트 N 밖 신규 dispatch**다 — V3
   실행 절차에 포함하되 실행은 여전히 사용자 승인 게이트를 거친다.

수신 텍스트의 sha256 (규약: `<!-- VERBATIM-BEGIN -->` 다음 개행부터
`<!-- VERBATIM-END -->` 직전까지의 UTF-8 바이트열):
`VERBATIM_SHA256: 3f9c5bf907406baae48259b6c00b17b9d92d67d83ef3996ad60688f021de76af`
