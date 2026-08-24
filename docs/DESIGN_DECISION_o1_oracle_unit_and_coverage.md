# DESIGN DECISION — D-E2E-v1-21: O1 오라클의 단위·적용범위 (Q21 판정)

- 사슬 항법: 이전 [[DESIGN_DECISION_o1_fixture_licensing|D-20]] · **D-21** · 다음 [[DESIGN_DECISION_pmb_source_qualification|D-22]] · 색인 [[RULING_CHAIN_INDEX]]
- 수령: 2026-08-23, 사용자 경유 (설계 담당, Wolfram MCP 형식화 명시)
- 상신 원문: `DESIGN_REQUEST_o1_oracle_unit_and_coverage.md` (Q21)
- 요지: **Q21.1=(b)** 문장 단위 유지 + O1 instance source 교체 /
  **Q21.2=(b\*)** 교체 승인하되 PMB는 후보일 뿐 자동 승격 아님(단독
  수용 게이트 금지 유지) / **Q21.3** whitelist 승인 + constructor profile을
  사전등록 대상으로 승격 / **Q21.4** Stage 1 유효 유지, adapter 자격 5→7
  승인. wikisem은 "잘못된 oracle"이 아니라 **O1-v0의 단위·표현 경계에
  부적합한 source**로 분류 — 폐기하지 않고 discourse 확장·스트레스 테스트
  후보로 보존. O1 재료 미확보 동안 O3 독립 선행을 조건부 허용(O1을
  통과한 것으로 간주 금지).
- 검증: 수령 당일 5건 완료(아래 "수신 검증 기록"), 이후 verbatim 보존.
  **이 파일의 판정 본문은 수신 그대로이며 편집하지 않는다.**

---

## 판정 원문 (verbatim)

Wolfram MCP로 Q21을 **“O1 estimand를 유지하면서 fixture material을 바꿀 수 있는가”**라는 문제로 형식화했습니다.

결론은 다음입니다.

> **Q21.1 = (b)** — 문장 단위를 유지하고 O1 instance source를 교체합니다.
> **Q21.2 = (b*)** — source 교체를 승인하되, PMB는 *후보*일 뿐 자동 승격하지 않습니다. PMB만으로 initial acceptance gate를 구성하는 것은 현재 manifest와 충돌합니다.
> **Q21.3 = whitelist 승인 + preregistration 대상 승격.**
> **Q21.4 = Stage 1은 그대로 유효, adapter qualification은 5→7 승인.**

현재 wikisem은 “잘못된 oracle”이라기보다 **현재 O1-v0의 단위와 표현 경계에 부적합한 oracle source**로 분류하는 것이 정확합니다. 

---

# 1. Wolfram 형식 판정

O1-v0 fixture가 유지해야 할 조건을 네 가지로 두었습니다.

[
E =
SentenceUnit
\land V0Coverage
\land ExternalOracleUnmodified
\land SameEstimand
]

선택지별로 넣은 결과:

```text
article_unit
  SentenceUnit              False
  V0Coverage                False
  ExternalOracleUnmodified  True
  EstimandPreserved         False

replace_source
  SentenceUnit              True
  V0Coverage                True
  ExternalOracleUnmodified  True
  EstimandPreserved         True

extract_subLF
  SentenceUnit              True
  V0Coverage                False
  ExternalOracleUnmodified  False
  EstimandPreserved         False

expand_IR_to_discourse
  SentenceUnit              False
  V0Coverage                True
  ExternalOracleUnmodified  True
  EstimandPreserved         False
```

Wolfram의 eligible option은:

```text
{"replace_source"}
```

하나뿐이었습니다.

물론 이는 요청서에 명시된 **sentence-level O1 + full structural DirectMatch**라는 현재 estimand를 유지한다는 조건하의 판정입니다. 

---

# 2. Q21.1 — fixture 단위

## 판정: **(b) 문장 단위 유지 + source 교체**

`fixture_template`의 문장 단위 정의를 바꾸지 않습니다.

### BEFORE

```text
1 fixture
=
1 sentence
+
that sentence's external formal representation
```

### AFTER

**변경 없음.**

```text
1 fixture
=
1 sentence
+
that sentence's external formal representation
```

바꾸는 것은 `source_authority.primary`의 **instance 공급원**입니다.

---

## 왜 (a) 기사 단위를 기각하는가

이 변경은 단순 storage/layout 변경이 아닙니다.

현재 O1의 질문은 대략:

[
NL_{sentence}
\rightarrow QuantifierScopeIR
]

입니다.

기사 단위로 바꾸면:

[
NL_{discourse}
\rightarrow
Quantification
+
Anaphora
+
Intensionality
+
Identity
+\cdots
]

가 됩니다.

즉 failure가 발생했을 때:

```text
quantifier scope 실패인지
anaphora 실패인지
intension 실패인지
discourse binding 실패인지
```

분리할 수 없습니다.

요청서의 실측대로 모든 nonempty article LF에 `InAnaphorSet`이 있다면 특히 그렇습니다. 

따라서 기사 단위로 바꾸고 기존:

```text
PASS >= 16 / 20
```

을 유지하는 것은 같은 benchmark를 더 어렵게 만드는 것이 아니라 **다른 benchmark에 같은 숫자를 붙이는 것**입니다.

기각합니다.

---

# 3. Q21.1(c) — 문장별 LF 추출도 기각

이 부분은 D-E2E-v1-20의:

> commitment ≠ correctness

원칙이 정확히 적용됩니다.

기사 LF에서:

```text
article LF
→ deterministic slicing rule
→ sentence LF
```

를 만든다고 해도 hash는 그 slicing rule이 **고정됐음**만 보여줍니다.

그 slicing이 저자의 intended sentence semantics와 일치하는지는 증명하지 않습니다.

형식적으로:

[
Deterministic(Extractor)
\not\Rightarrow
OracleCorrect(Extractor)
]

입니다.

특히 `InAnaphorSet` 같은 문장 간 구조를 잘라내는 순간 “결박 보존”과도 충돌합니다.

따라서:

```text
published oracle
→ our extraction
→ expected answer
```

구조를 O1 acceptance oracle로 허용하지 않습니다.

---

# 4. Q21.2 — 0건 coverage의 의미

## 판정: **v0 subset이 틀렸다고 보지 않는다**

현재 사실은:

```text
Coverage(v0, wikisem-article-LF) = 0
```

입니다.

여기서:

```text
Therefore v0 is wrong
```

은 나오지 않습니다.

마찬가지로:

```text
Therefore wikisem is bad
```

도 나오지 않습니다.

정확한 결론은:

> **wikisem article-level LF와 O1-v0 acceptance-fixture contract의 교집합이 비어 있다.**

즉 compatibility 문제입니다.

```text
good formal corpus
+
reasonable v0 subset
+
incompatible interface
```

는 동시에 가능합니다.

---

# 5. 따라서 Q21.2 = **(b*) source replacement**

다만 사용자 선택지의 단순 `(b)`보다 조건을 하나 붙입니다.

## `b*`

> **O1의 primary instance source를 sentence-level formal-semantic resource로 교체한다. 단 후보 자원은 fixture freeze 전에 O1-v0 eligibility qualification을 통과해야 한다.**

필수 조건:

```yaml
O1_instance_source_eligibility:

  unit:
    one_sentence_per_fixture: true
    external_representation_for_same_sentence: true

  semantic_boundary:
    quantifier_scope_relevant: true

  representation:
    fully_representable_in_frozen_v0_constructor_profile: true

  oracle:
    externally_authored: true
    no_project_authored_scope_resolution: true

  quantity:
    eligible_items_min: 20
```

즉 “문장 단위 corpus다”만으로는 부족합니다.

---

# 6. PMB Gold의 지위

## **candidate source로 승인, O1 source로 자동 승인하지 않음**

요청서가 제공한 정보로는 PMB가 sentence-level formal representation을 제공한다는 점까지는 근거가 있습니다. 

하지만 아직 다음은 입증되지 않았습니다.

```text
PMB에서
O1 quantifier-scope relevant
AND v0 constructor profile 안에 완전히 들어오는
독립 fixture가 >= 20개 존재하는가?
```

따라서 PMB는:

```yaml
PMB_for_O1:
  candidate: true
  qualified: false
```

로 둡니다.

먼저 전수/충분 coverage scan이 필요합니다.

---

# 7. 더 중요한 문제 — PMB의 이중 역할

현재 manifest에는 이미:

> **PMB Gold를 유일한 initial acceptance gate로 사용하지 않는다**

는 규칙이 있습니다. 

여기서 단순히 fixture ID를 둘로 나눠:

```text
PMB
├─ O1 acceptance slice
└─ regression slice
```

로 하는 것만으로는 이 규칙이 충족되지 않습니다.

왜냐하면:

```text
distinct fixture sets
≠
distinct source authority
```

이기 때문입니다.

즉 item leakage는 막지만 **PMB가 유일한 acceptance source라는 사실은 그대로**입니다.

---

# 8. PMB를 쓰려면 두 가지 가능성이 있다

## 허용안 1 — PMB + 독립 source

예:

```text
O1 Stage 2
├─ independent sentence-level oracle source A
└─ PMB Gold subset
```

이 경우 PMB는 유일한 acceptance gate가 아닙니다.

가장 깨끗합니다.

---

## 허용안 2 — manifest를 별도 개정

PMB 20건만 사용하려면 기존:

```text
Do not use PMB Gold as the only initial acceptance gate
```

를 철회하거나 범위를 바꿔야 합니다.

현재 Q21에서 그 조항을 우회해서는 안 됩니다.

**저는 현 시점에서 이 개정은 권하지 않습니다.**

PMB-only 사용의 필요성이 아직 입증되지 않았기 때문입니다.

---

# 9. 따라서 현재 Stage 2 상태

```yaml
O1_stage2_material:

  wikisem:
    status: ineligible_for_v0_acceptance
    reason:
      - article_level_oracle
      - zero_full_v0_coverage

  PMB:
    status: candidate
    qualification_required: true
    sole_acceptance_source_allowed: false

  freeze:
    allowed_now: false
```

즉 fixture 20건 동결을 계속 차단하는 것이 맞습니다.

---

# 10. 다만 전체 E2E 프로그램까지 멈출 필요는 없다

여기서는 D-E2E-v1-19의 “O1 먼저”를 조금 더 정확하게 수정할 필요가 있습니다.

### BEFORE

```text
O1
→ O2
→ O3
```

### AFTER

```text
if eligible O1 material exists:
    O1 → O2 → O3

else:
    O1 = MATERIAL_BLOCKED
    O3 may proceed as independent core-oracle experiment
```

즉 O1 우선순위를:

> **무조건적인 시간 순서**

가 아니라:

> **eligible fixture가 존재할 때의 preferred capability order**

로 한정합니다.

이는 O1의 binding primitive가 O2에 재사용된다는 D-19의 기술적 이유를 철회하는 것이 아닙니다.

그 이유는 여전히 맞습니다.

다만:

[
PreferredOrder
\not\Rightarrow
UnavailableExperimentBlocksAllOtherExperiments
]

입니다.

따라서 독립 O1 source 확보가 길어질 경우 O3를 먼저 실행하는 것을 **조건부 허용**합니다.

O1을 “통과한 것으로 간주”해서는 안 됩니다.

---

# 11. estimand / N / threshold / primary metric

source 교체 자체가 다음 조건을 만족하면:

```text
sentence unit
same O1 semantic boundary
same frozen v0 IR
same DirectMatch evaluator
```

### **변경하지 않습니다**

```yaml
estimand:
  sentence_level_quantifier_scope_compilation: unchanged

N:
  20

acceptance:
  PASS_min: 16
  final_ERROR: 0
  unexpected_UNSCORABLE: 0

primary_metric:
  DirectMatch: unchanged
```

즉 16/20을 source가 바뀌었다는 이유만으로 다시 조정하지 않습니다.

현재 80%는 이미 population claim이 아니라 **engineering benchmark**로 규정했기 때문입니다.

다만 결과 보고에는 반드시:

```text
O1-v1 source = <new source>
```

를 명시하고 wikisem 기반 결과와 비교 가능한 것처럼 쓰지 않습니다.

wikisem cohort는 애초에 실행되지 않았으므로 실질적인 cross-source comparability 문제도 없습니다.

---

# 12. Q21.3 — whitelist

## 판정: **승인**

더 강하게 말하면 blacklist보다 whitelist 방식이 현재 실험에는 맞습니다.

이번에 실제로:

```text
unknown constructor
→ ordinary Predicate로 조용히 통과
```

가 발생했기 때문입니다. 

이 실패 형태에서는:

```text
unknown means allowed
```

가 가장 위험합니다.

따라서:

```text
head ∉ SupportedConstructors
→ reject as unsupported
```

를 유지합니다.

---

# 13. 다만 whitelist는 단순 구현 세부가 아니다

이 질문에서 중요한 부분입니다.

whitelist 내용은:

> **무엇을 O1-v0 능력 범위에 포함하는가**

를 결정합니다.

따라서 두 층으로 분리합니다.

### 구현 선택

```text
blacklist보다 whitelist fail-closed를 사용
```

→ 승인된 implementation policy.

### 실험 정본

```text
어떤 constructors가 whitelist에 들어가는가
```

→ **preregistered estimand boundary**.

예:

```yaml
supported_constructor_profile:
  id: O1_V0
  allowed:
    - Some
    - All
    - And
    - PredicateApplication
    - True
    - ...
```

정확한 실제 enum 이름을 사용하십시오.

이 profile의 hash를 fixture manifest와 함께 동결합니다.

---

# 14. whitelist와 UNSCORABLE 회계

다음처럼 처리합니다.

## fixture freeze 이전

scanner가:

```text
unsupported head 발견
```

하면:

```text
fixture = INELIGIBLE
```

입니다.

UNSCORABLE cohort result가 아닙니다.

아직 실험 표본에 들어오지 않았기 때문입니다.

---

## fixture freeze 이후

사전 eligibility를 통과했다고 기록된 fixture가 실제 evaluator/adapter에서:

```text
unsupported constructor
```

를 만나면:

```text
UNEXPECTED_UNSCORABLE
```

입니다.

그리고 기존 Stage 2 criterion:

```text
unexpected_UNSCORABLE = 0
```

을 실패합니다.

이렇게 해야 pre-scan과 production adapter의 drift를 잡을 수 있습니다.

---

# 15. 매우 중요한 dual-check

이번 0건 발견이 adapter-independent scanner로도 재현됐다는 것은 좋은 패턴입니다. 

앞으로 fixture eligibility도:

```text
Path A:
Oracle Adapter capability scan

Path B:
independent constructor scanner
```

두 경로를 사용할 것을 권합니다.

둘이 불일치하면:

```text
FREEZE_BLOCKED
```

입니다.

이는 또 하나의 full semantic compiler를 만드는 것이 아니라 **constructor coverage라는 기계적으로 checkable property의 독립 교차검증**입니다.

---

# 16. whitelist 확장은 외부 판정 대상

예를 들어 앞으로:

```text
InAnaphorSet
Intension
Equal
```

을 whitelist에 넣자는 변경은 단순 feature 추가가 아닙니다.

특히 현재 evaluator가 전체 graph match를 사용한다면:

[
Target =
QuantifierScope
]

에서:

[
Target =
QuantifierScope
+
DiscourseCoreference
+
Intensionality
+
Identity
]

로 바뀝니다.

따라서:

```yaml
constructor_profile_change:
  adds_new_semantic_family: external_design_review_required
```

로 두십시오.

---

# 17. Q21.4 — Stage 1

## 판정: **Stage 1은 그대로 유효**

요청서에 따르면 Stage 1의 8 controls는 **손으로 작성된 IR을 evaluator에 넣어 evaluator boundary를 검증**했습니다. Adapter는 경로에 없었습니다. 

그래서 adapter가 수정됐다는 사실에서:

[
AdapterChanged
\Rightarrow
Stage1Invalid
]

은 나오지 않습니다.

Wolfram 결과:

```text
AdapterChangeLogicallyForcesStage1Invalid = False
```

입니다.

따라서:

```yaml
E2E_v1_M:
  status: PASS
  rerun_required_due_to_adapter_change: false
```

로 유지합니다.

---

# 18. 그러나 Stage 2는 adapter qualification을 다시 요구

E2E-v1-C readiness는:

[
Stage1MeasurementPASS
\land
OracleAdapterQualified
]

입니다.

Wolfram에서도:

```text
Stage2ReadyRequiresStage1 = True
Stage2ReadyRequiresAdapterQualification = True
```

로 설정할 수 있습니다.

즉:

```text
Stage 1 PASS
```

가 그대로 유지되더라도 새 adapter가 자격 미통과면 Stage 2는 못 갑니다.

---

# 19. adapter qualification 5 → 7

## 판정: **승인**

기존 다섯 항목:

1. syntax parse
2. alpha-renaming invariance
3. quantifier-reordering negative test
4. binding preservation
5. deterministic replay

에:

6. **output schema validation**
7. **closed-form preservation**

을 추가합니다.

Wolfram으로 “기존 5개를 통과하면 새 2개도 자동으로 보장되는가?”를 검증했습니다.

결과:

```text
FiveChecksImplyOutputSchemaValidity      = False
FiveChecksImplyClosedFormPreservation    = False
SevenStrictlyStrongerCountermodelExists = True
SevenImpliesFive                         = True
```

즉 새 두 검사는 중복이 아닙니다.

실제 결함도 각각 독립적으로 이 두 축을 침범했습니다. 

따라서 7개로 늘리는 것은 estimand 변경이 아니라 **measurement integrity 강화**입니다.

---

# 20. Adapter qualification v1 확정

```yaml
O1_oracle_adapter_qualification_v1:

  required:

    - syntax_parse

    - alpha_rename_invariance

    - quantifier_reordering_negative_control

    - binding_preservation

    - deterministic_replay

    - output_schema_validity

    - closed_form_preservation

  pass_rule:
    all_required: PASS
```

특히 마지막 둘은 aggregate 하나만 검사하지 말고 **각 fixture 또는 canonical test class에 대해 직접 음성 테스트**를 두는 것이 좋습니다.

---

# 21. 이번 wikisem corpus는 폐기하지 않는다

현재 자원은 O1-v0 acceptance에는 부적합하지만 연구 가치가 사라진 것이 아닙니다.

권장 상태:

```yaml
wikisem:
  role:
    O1_v0_acceptance: ineligible

  future_role:
    discourse_semantics_extension: candidate
    adapter_stress_test: candidate

  reason:
    - article_level_formalization
    - discourse_coreference
    - intensionality
    - equality
```

특히 이번 adapter의 silent-laundering 결함 3개를 잡아낸 **negative/adversarial corpus**로 가치가 큽니다.

다만 그것을 O1-v0 score에 넣지는 않습니다.

---

# 22. 이번 발견이 의미하는 것

이번 사건은 오히려 D-E2E-v1-20의 설계가 제대로 작동한 사례에 가깝습니다.

잘못된 초기 상태는:

```text
adapter says 22 fixtures supported
→ expected IR hash 생성
→ commitment valid
```

이었을 것입니다.

그러나 ORACLE-11:

```text
commitment ≠ correctness
```

를 별도 gate로 뒀기 때문에:

```text
adapter correctness audit
→ free variables 발견
→ unsupported operators 발견
→ invalid IR 발견
→ false coverage 22 → true coverage 0
```

으로 교정됐습니다. 

즉 이것은 O1 실험 실패가 아닙니다.

**fixture freeze 전에 measurement corruption을 잡은 성공적인 pre-execution failure**입니다.

---

# 최종 판정

```yaml
D_E2E_v1_21:

  Q21_1:
    decision: B

    fixture_unit:
      sentence_level: retained

    wikisem_article_LF:
      use_as_O1_v0_fixture: false

    sub_LF_extraction:
      allowed_for_acceptance_oracle: false

  Q21_2:
    decision: B_STAR

    action:
      replace_O1_instance_source: true
      expand_v0_to_fit_wikisem: false

    estimand:
      sentence_level_quantifier_scope: unchanged

    N:
      value: 20
      changed: false

    acceptance:
      PASS_min: 16
      final_ERROR: 0
      unexpected_UNSCORABLE: 0
      changed: false

    primary_metric:
      DirectMatch: unchanged

    PMB:
      status: candidate_source
      requires_O1_v0_eligibility_scan: true
      may_be_only_initial_acceptance_source: false

    source_qualification:
      minimum_eligible_fixtures: 20
      same_sentence_LF_pair_required: true
      full_v0_constructor_coverage_required: true
      externally_authored_oracle_required: true

    sequence:
      O1_preferred_if_material_available: true
      if_O1_material_blocked:
        O3_may_proceed: true
        O1_must_not_be_marked_passed: true

  Q21_3:
    whitelist:
      approved: true
      fail_closed: true

      constructor_profile:
        preregister: true
        hash_pin: true

      prefreeze_unsupported:
        result: INELIGIBLE

      postfreeze_unsupported:
        result: UNEXPECTED_UNSCORABLE
        acceptance_effect: FAIL

      semantic_family_expansion:
        external_design_review_required: true

  Q21_4:
    Stage1:
      prior_8_of_8: remains_valid
      rerun_due_to_adapter_change: false

    adapter_qualification:
      changed_from: 5
      changed_to: 7
      approved: true

      required:
        - syntax_parse
        - alpha_rename_invariance
        - quantifier_reordering_negative_control
        - binding_preservation
        - deterministic_replay
        - output_schema_validity
        - closed_form_preservation

      Stage2_requires_all_PASS: true

  wikisem:
    O1_v0_acceptance_role: incompatible
    future_discourse_or_stress_role: retained
```

## 가장 중요한 결론

이번에 바꿔야 하는 것은 **O1의 의미론적 범위가 아니라 O1 fixture를 공급하는 source**입니다.

`0/121` coverage를 보고 v0에 `InAnaphorSet`, `Intension`, `Equal`을 추가하면 source에 맞추기 위해 estimand가 팽창합니다. 반대로 기사 LF를 문장 LF로 자르면 우리 시스템이 oracle의 일부를 제작합니다.

따라서 가장 작은 수정은:

> **sentence-level quantifier-scope O1을 그대로 유지하고, 그 contract를 실제로 만족하는 sentence-level external oracle source를 새로 qualification하는 것**입니다.

그리고 그 source가 준비되지 않는 동안에는 **O1을 억지로 통과시키지 말고 O3를 독립적으로 먼저 진행할 수 있습니다.**

---

## 수신 검증 기록 (2026-08-23, 운영 세션 — 판정 본문 밖)

판정 본문 sha256 (이 절 추가 전 파일 전체):
`2b53f1fdb6b35e5794fc4bc3f3920e435265bf44d9a3e3ef8ef6b3ea8fdffd3a`

| # | 판정의 반증가능 주장 | 검증 방법 | 결과 |
|---|---|---|---|
| V1 | 적격성 진리표에서 eligible = {replace_source} 단독 | 이 세션의 실측(단위=기사, coverage 0/121, 추출=오라클 제작, 담화 구성자=estimand 확장)을 전제로 4×4 진리표 독립 재계산 | **일치** |
| V2 | `FiveChecksImply{OutputSchema,ClosedForm} = False` | **실물 반례**: 자격 5항목 스위트가 초록이던 `38e5d4b`의 구 adapter를 git에서 추출·실행 — 닫힌 LF → 자유변수 `{z}`(항목 7 위반), 람다-인자 술어 → `PRED_ARG_NOT_TERM`(항목 6 위반), 결정적 재실행은 여전히 통과 | **확인** — 반례가 구성물이 아니라 우리 커밋 이력 |
| V3 | "Stage 1 경로에 adapter 부재" | Stage 1 실험 폴더 전체에서 `cg_oracle_adapter` grep | **0건 — 확인** |
| V4 | 인용된 두 조항의 실재 | D-19 `unexpected_UNSCORABLE: 0`(411행·899행), manifest `"Do not use PMB Gold as the only initial acceptance gate."`(283행) | **verbatim 확인** |
| V5 | 선행 판정과의 무모순 | D-19 §12(oracle 변경=외부 판정 — 본 판정이 그 채널), ORACLE-11 유지, O1 우선 근거(binding 재사용)는 철회가 아니라 조건화 | **모순 없음** |

적용 효과(판정이 명령한 것):

1. **fixture 20건 동결: 계속 차단** — 새 sentence-level source가
   `O1_instance_source_eligibility` 6조건을 통과할 때까지.
2. **wikisem: `ineligible_for_v0_acceptance`** — 폐기 아님(discourse 확장·
   adapter 스트레스 후보로 보존). O1-v0 점수에 불포함.
3. **PMB: candidate, qualified 아님** — 적격성 전수 스캔 필요, 단독 수용
   source 금지 유지(fixture ID 분할로는 불충족 — source authority가 기준).
4. **constructor profile을 사전등록 정본으로 승격** — fixture manifest와
   함께 hash 동결(따라서 지금은 함께 차단). 확장(InAnaphorSet/Intension/
   Equal 등 새 의미 family)은 외부 판정 대상.
5. **UNSCORABLE 회계 확정**: freeze 전 unsupported → `INELIGIBLE`(표본
   밖), freeze 후 unsupported → `UNEXPECTED_UNSCORABLE`(수용 기준 FAIL).
6. **Stage 1 유효 유지, 재실행 불요.** adapter 자격 5→7 승인 —
   `output_schema_validity`, `closed_form_preservation` 추가, 전 항목 PASS가
   Stage 2 전제.
7. **O1 = MATERIAL_BLOCKED 동안 O3 독립 선행 조건부 허용** — O1을 통과로
   간주 금지. estimand/N/임계값/주 지표 무변경, 결과 보고에 `O1-v1 source`
   명시.
