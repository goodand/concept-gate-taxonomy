# DESIGN DECISION — D-E2E-v1-24: FOLIO 술어 라벨 규약 (Q24 판정)

- 수신: 2026-08-23, 사용자 경유 (판정자: 외부 설계 담당, Wolfram MCP 검토 명시)
- 원 요청: `DESIGN_REQUEST_folio_predicate_labels.md`
  (sha256 `54aa1a7d719f66226c17c577768eb4c575ececf97038b6dc1fa37324ee3e133d`)
- 요약:
  > **Q24.1 = (a)** — FOLIO 전용 lowercase codec `FOLIO_LABEL_LOWERCASE_V1`
  > (소문자화만; 분절·동의어·lemma·병합 금지, source-bound, 커널 밖) /
  > **Q24.2 = (a)** — 도달 불가 술어 fixture 부적격 + 신규 적격성 불변식
  > `predicate_label_reachability`(동결된 기계 판정), 동일 seed·동일 층 정의로
  > **affected stratum 전체** 결정론 재선별(수동 4건 교체 금지), 풀 부족 시
  > BLOCKED 재상신 /
  > **Q24.3 = 승인+강화** — 기존 freeze(f57ae12)는 불변 보존
  > (`SUPERSEDED_PRE_EXECUTION`), amendment 기록 후 **Freeze V2 신규 생성**
  > (`PRE_EXECUTION_FREEZE_AMENDMENT_V1` 절차 정본화; 재검증: FOLIO controls·
  > codec 음성 테스트·smoke 전체·Path A/B 합치) /
  > **Q24.4 = (a)** — FOLIO gold topology는 estimand의 일부, 비교층 rewrite
  > 금지 유지, 사전등록에는 "known source-specific challenge"로 기록(특정
  > item의 예상 실패 라벨링 금지) /
  > **Stage 2: BLOCKED_UNTIL_REFREEZE**

---

## 판정 전문 (verbatim — 수신 그대로, 아래 검증 기록의 해시 대상)

<!-- VERBATIM-BEGIN -->
Wolfram MCP로 Q24를 검토했습니다. 결론은 다음입니다.

> **Q24.1 = (a)** — FOLIO 전용 lowercase codec 추가
> **Q24.2 = (a)** — 문장으로부터 도달 불가능한 oracle 술어가 있는 fixture는 부적격 처리 후 결정론적으로 재선별
> **Q24.3 = 운영 세션 권고안을 승인하되, 기존 freeze를 수정하지 말고 “pre-execution amendment → affected stratum 재생성 → 재동결” 절차로 강화**
> **Q24.4 = (a)** — FOLIO의 quantifier/implication topology는 현재 estimand의 일부이며 비교층에서 자연 독해 형태로 rewrite하면 안 됨

이번 smoke test는 cohort 결과를 본 뒤 threshold를 조정한 사건이 아니라, **실행 전에 measurement contract가 fixture 일부를 원천적으로 실패시키는 결함을 발견한 것**입니다. 따라서 수정은 허용되지만 기존 freeze를 소급 덮어쓰면 안 됩니다. 

---

# 1. Q24.1 — FOLIO predicate label codec

## 판정: **(a) 승인**

FOLIO에 한해서:

```text
Zorble → zorble
CanCatch → cancatch
```

같은 **case normalization만** 평가 profile에서 허용합니다.

권장 명칭:

```yaml
FOLIO_LABEL_LOWERCASE_V1
```

위치는 반드시:

```text
O1 / FOLIO evaluation profile
```

입니다.

다음에는 넣지 않습니다.

```text
Shared Kernel global canonicalizer
```

---

## 왜 허용 가능한가

현재 관측된 첫 부류는:

```text
oracle = Zorble(x)
subject = zorble(x)
```

이고 구조·arity·argument topology는 동일합니다. 

Wolfram 형식화에서도:

```text
case-only mismatch
+
source-bound normalization
+
topology unchanged
```

인 경우 label mismatch를 제거하면서 구조적 signal은 그대로 보존할 수 있었습니다.

따라서:

[
CaseDifference
]

를 O1 semantic error로 세는 것은 현재 estimand에 불필요합니다.

---

# 2. codec의 범위는 매우 좁게

이번 승인으로 다음까지 허용되는 것은 아닙니다.

```text
CamelCase segmentation
synonym substitution
WordNet lookup
lemmatization
predicate paraphrase
annotator vocabulary guessing
```

현재 정본은:

```yaml
FOLIO_LABEL_LOWERCASE_V1:
  lowercase: true

  preserve:
    - predicate_occurrence
    - arity
    - argument_edges
    - scope_position

  forbidden:
    - lexical_substitution
    - semantic_aliasing
    - node_merging
```

정도로 제한하는 것이 맞습니다.

PMB의 synset→lemma codec과도 별도 profile로 유지합니다.

---

# 3. Q24.2 — 문장에 없는 annotator predicate

## 판정: **(a) fixture 부적격 처리**

이 네 건은 단순 표기 차이와 다릅니다.

요청서의 실측:

```text
SpectatorsBetOn
OnRoof
WentWrong
HoldingCompany
Racing
```

등이 subject가 받는 문장에 존재하지 않으며, template은 “sentence's content words”에서 predicate name을 만들도록 요구합니다. 

따라서 subject에게 oracle 정보가 없는 상태에서는:

```text
observable input
↛ required oracle label
```

입니다.

이런 fixture를 exact label scoring에 넣으면 사실상:

> **숨겨진 annotator vocabulary를 추측했는가**

를 측정하게 됩니다.

이는 O1의 quantifier-scope estimand가 아닙니다.

---

# 4. 새로운 eligibility invariant

따라서 FOLIO fixture에 다음 조건을 추가합니다.

```yaml
predicate_label_reachability:
  required: true
```

형식적으로:

[
\forall p\in OraclePredicates:
ReachableFromSentence(p)
]

이어야 합니다.

여기서 `ReachableFromSentence`는 임의 LLM 의미판단이 아니라 **동결된 lexical codec으로 기계 판정 가능한 것**이어야 합니다.

예:

```text
oracle label
↓ FOLIO_LABEL_LOWERCASE_V1
normalized label
↓
frozen subject predicate-name derivation rule
↓
sentence-derived?
```

YES만 eligibility 통과.

---

# 5. freeze 전과 freeze 후 회계

이번 결함을 일반화하면:

### freeze 전 발견

```text
oracle predicate not subject-reachable
→ INELIGIBLE
```

### freeze 후, cohort 실행 전 발견

이번 경우처럼:

```text
FROZEN_MEASUREMENT_DEFECT
→ amendment required
```

### cohort 실행 후 발견

그때는 단순 replacement를 허용하면 안 됩니다.

이미 결과를 본 뒤 표본을 바꾸는 것이 되므로 별도 cohort/version이 필요합니다.

---

# 6. Q24.2 재선별 방식

여기서 중요한 것은 **사람이 네 개를 보고 마음에 드는 네 개를 교체하면 안 된다는 것**입니다.

권장:

```text
same original candidate pool
+
same frozen seed
+
same stratum rules
+
new reachability eligibility predicate
↓
rerun deterministic selector
```

입니다.

Wolfram 형식 검토에서도:

```text
selection depends on
  seed + eligibility

NOT
  observed cohort outcomes
```

이면 outcome-conditioned selection을 피할 수 있습니다.

따라서:

```yaml
replacement:
  manual_pick: forbidden
  same_seed: true
  same_stratum_definition: true
  new_eligibility_rule:
    predicate_label_reachability: required
```

로 고정하십시오.

---

# 7. Q24.3 — 동결 후 amendment 절차

## 판정: **승인하되 더 엄격한 versioning 필요**

운영 세션의 네 항목은 방향이 맞습니다. 

다만:

> “기존 manifest의 문제 entry를 수정”

으로 처리하지 말고:

> **기존 freeze를 immutable historical artifact로 남기고 새 freeze version을 생성**

해야 합니다.

---

# 8. BEFORE → AFTER

## BEFORE

```text
f57ae12
Stage2 frozen
```

이 artifact를 직접 고침.

### 금지

---

## AFTER

```text
Freeze V1
f57ae12
status:
  SUPERSEDED_PRE_EXECUTION
reason:
  measurement-surface defect Q24
        │
        ▼
Amendment D-E2E-v1-24
        │
        ▼
Freeze V2
new manifest hash
new profile hash
new fixture commitments
```

즉 V1이 “틀린 과거”로 삭제되는 것이 아니라 **감사 가능한 이전 상태**로 남습니다.

---

# 9. 정본 amendment protocol

향후에도 재사용할 수 있도록 다음으로 확정하는 것을 권합니다.

```yaml
PRE_EXECUTION_FREEZE_AMENDMENT_V1:

  trigger:
    - frozen measurement defect
    - oracle incompatibility
    - fixture eligibility defect
    - frozen profile implementation mismatch

  prerequisites:
    cohort_execution_started: false
    confirmatory_outcomes_observed: false

  procedure:

    1:
      action: halt_execution

    2:
      action: preserve_original_freeze
      mutation_of_old_manifest: forbidden

    3:
      action: record_amendment
      required:
        - defect
        - discovery_method
        - affected_contract
        - external_design_ruling
        - exact_before_after_diff

    4:
      action: update_eligibility_or_profile

    5:
      action: deterministically_regenerate_affected_stratum
      preserve:
        - original_seed
        - original_stratum_definition
        - original_N
        - original_threshold

    6:
      action: regenerate_hash_commitments

    7:
      action: rerun_affected_qualification_and_smoke

    8:
      action: create_new_freeze_version

    9:
      action: cohort_execution_may_begin
```

---

# 10. “changed entry만 교체”는 조건부 승인

운영 세션의:

> 변경된 entry만 교체

는 **affected FOLIO stratum의 selector가 독립적**일 경우 가능합니다.

더 안전한 규칙은:

> **affected stratum 전체를 동일 seed로 재생성한다.**

예:

```text
PMB stratum
→ unchanged

FOLIO control stratum
→ regenerate

FOLIO multi-quantifier stratum
→ regenerate
```

입니다.

수동으로 4개 ID만 골라 끼우지 않습니다.

---

# 11. 무엇을 다시 검증해야 하나

### 다시 실행 필요 없음

기존 Stage 1 evaluator qualification 자체:

```text
E2E-v1-M 8/8
```

은 adapter/profile 이전 계층을 시험한 것이므로 유지 가능합니다.

---

### 다시 실행 필요

이번 amendment가 직접 건드리는 것:

```text
FOLIO label profile
FOLIO control fixtures
FOLIO main fixtures
```

따라서 최소:

```text
FOLIO adapter controls 2–4
FOLIO label-codec negative tests
full frozen-surface smoke
Path A / Path B eligibility agreement
```

을 재실행합니다.

그 뒤에만 V2를 freeze합니다.

---

# 12. 새 label-codec qualification

최소 다음 세 개를 추가하십시오.

### Positive

```text
Zorble
zorble
→ equal labels
```

### Negative — lexical substitution 금지

```text
Zorble
Creature
→ unequal
```

### Structural preservation

casefold 전후:

```text
arity
argument order
scope location
predicate occurrence count
```

가 모두 동일해야 합니다.

---

# 13. Q24.4 — FOLIO quantifier/implication topology

## 판정: **(a), 현 estimand의 일부**

이 문제는 label gap과 성격이 다릅니다.

비교 대상:

[
\forall x\exists y((A(x)\land B(y))\to C(x,y))
]

와 subject의 자연 독해 후보:

[
\forall x(A(x)\to\exists y(B(y)\land C(x,y)))
]

를 Wolfram에서 2원소 domain의 모든 Boolean interpretation에 대해 계산했습니다.

결과:

```text
EquivalentOnAll2ElementInterpretations = False
CountermodelCount = 104
```

즉 이 둘은 단순 surface notation 차이가 아닙니다.

실제로 다른 의미를 가질 수 있습니다.

---

# 14. 따라서 비교층에서 이어주면 안 된다

다음을 하면:

```text
FOLIO formula
↓
“더 자연스러운” formula로 rewrite
↓
compare
```

Oracle Adapter가 semantic adjudicator가 됩니다.

이는 D-23의:

```text
prefix quantifier order preserved
cross-quantifier implication rewrite forbidden
```

을 다시 무너뜨립니다.

따라서 그대로 유지합니다.

---

# 15. 다만 표현은 “예상 실패”보다 “known source-specific challenge”

사전등록에는 이렇게 쓰는 것을 권합니다.

### 피할 표현

> “FOLIO-142p1은 실패할 것으로 예상된다.”

특정 동결 item의 결과를 미리 사실상 분류하는 것처럼 보일 수 있습니다.

### 권장

> “FOLIO source contains prefix-quantified implication structures whose gold topology may differ from alternative natural-language readings. Under FOLIO_FOL_V0, the published gold topology is preserved exactly; comparison-layer quantifier/implication rewrites are prohibited.”

즉 **source-specific difficulty를 기록**하되 결과 label은 미리 부여하지 않습니다.

---

# 16. label 문제와 topology 문제의 핵심 차이

| 문제                             | 성격                      | 처리                 |
| ------------------------------ | ----------------------- | ------------------ |
| `Zorble` vs `zorble`           | 표기 convention           | source codec으로 중립화 |
| `SpectatorsBetOn`이 문장에 없음      | input reachability 위반   | fixture 부적격        |
| `∀∃((A∧B)→C)` vs `∀(A→∃(B∧C))` | 실제 logical structure 차이 | oracle topology 유지 |

즉:

```text
notation noise
→ normalize

hidden oracle vocabulary
→ exclude

semantic topology difference
→ measure
```

로 구분하는 것이 맞습니다.

---

# 최종 판정

```yaml
D_E2E_v1_24:

  Q24_1:
    decision: A

    FOLIO_label_codec:
      id: FOLIO_LABEL_LOWERCASE_V1
      source_bound: true
      lowercase: true

      preserve:
        - predicate_occurrence
        - arity
        - argument_topology
        - scope_position

      forbidden:
        - synonym_mapping
        - semantic_aliasing
        - global_kernel_application
        - predicate_node_merge

  Q24_2:
    decision: A

    new_eligibility:
      predicate_labels_must_be_subject_reachable: true

    unreachable_predicate:
      prefreeze: INELIGIBLE

    current_4_fixtures:
      retain: false
      replacement: deterministic

    reselection:
      same_seed: true
      same_strata: true
      manual_selection: false
      rerun_affected_FOLIO_strata: true

    if_eligible_pool_insufficient:
      result: BLOCKED
      re_adjudication_required: true

  Q24_3:
    amendment_procedure:
      approved: true

      original_freeze:
        mutate: false
        retain: true
        status: SUPERSEDED_PRE_EXECUTION

      amendment:
        record_before_after_diff: true
        record_no_cohort_results_observed: true
        external_ruling_reference: D-E2E-v1-24

      regenerate:
        affected_strata_only: true
        same_seed: true

      requalification:
        FOLIO_controls: required
        label_codec_tests: required
        smoke_test: required
        PathA_PathB_agreement: required

      new_freeze_version: required

  Q24_4:
    decision: A

    FOLIO_gold_topology:
      part_of_estimand: true

    comparison_layer:
      implication_quantifier_rewrite: forbidden

    preregistration:
      record_as_known_source_specific_challenge: true
      prelabel_expected_failure: false

  Stage2:
    execution_status: BLOCKED_UNTIL_REFREEZE
```

가장 중요한 원칙은 다음입니다.

> **subject가 볼 수 없는 oracle 어휘를 맞히게 하는 것은 semantic compilation이 아니라 hidden-label guessing이므로 제거해야 하지만, 외부 gold가 명시한 quantifier/scope topology를 “더 자연스러워 보이는” 구조로 바꾸는 것은 Oracle 자체를 우리가 수정하는 것이므로 제거하면 안 됩니다.**

이번 수정은 estimand를 완화하는 것이 아니라, **표기 잡음과 숨은 어휘를 제거하고 실제 semantic topology만 남기는 measurement repair**로 보는 것이 맞습니다. 
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

판정문의 기계 검증 가능 주장 4건을 수신 즉시 독립 재검증했다.

| # | 주장 | 방법 | 결과 |
|---|---|---|---|
| V1 | `∀x∃y((A∧B)→C)` vs `∀x(A→∃y(B∧C))` — 2원소 domain 전 해석에서 반례 **104** | 256개 해석(unary 4×4 × binary 16) 전수 열거 독립 재계산 | **CONFIRMED — 정확히 104/256** (D-23 검증의 2/16·56/256 재현과 동일 기법) |
| V2 | 대소문자만 문제인 fixture는 codec으로 정합 회복 | 동결 FOLIO 8건에 codec 규칙(소문자화만) 적용 후 문장 도달성 재분류 | **CONFIRMED — 도달 가능 4건**(142p1·695p1·175p1·1377p0) = 요청서 분류와 일치 |
| V3 | codec 금지 목록(분절·lemma 금지)과 부적격 분류의 정합 | V2 동일 계산 | **CONFIRMED — `Racing`(500p4)은 codec만으로 여전히 불가** → 부적격 분류 정합. 404p3·721p1·274p1도 동일 |
| V4 | §11 "E2E-v1-M 8/8" 식별자의 실재 | 저장소 전수 grep | **CONFIRMED — E2E-v1-M은 D-19가 명명한 Stage 1 식별자**(`DESIGN_DECISION_e2e_v1_experiment_design.md`, control 8종). 지칭 오류 아님 |

주의 기록 (판정 적용 시 구속되는 해석 2건):

1. **도달성 판정 규칙은 아직 미동결이다.** V2/V3의 재분류는 잠정 규칙
   (문장 소문자·공백제거 문자열에의 부분문자열 포함)을 썼다 — 판정 §4가
   요구하는 "frozen subject predicate-name derivation rule"은 재선별 구현
   시 **동결 대상**이며, 특히 `CanCatch→cancatch`(공백 병합)형 도달성은
   그 규칙의 정의에 따라 갈린다. 규칙 확정은 amendment 기록에 포함한다.
2. **재선별 범위는 §10의 엄격안을 따른다**: FOLIO 두 stratum(control·
   multi_quantifier) **전체**를 동일 seed로 재생성 — 수동 4건 교체 금지.
   PMB stratum 15건은 불변.

수신 텍스트의 sha256 (아래 "해시 산출 규약"대로):
`VERBATIM_SHA256: d563f12c8281a254199754fc2576b80e8b4203c65e2517576780da197fb23fb3`

해시 산출 규약: 이 파일의 `<!-- VERBATIM-BEGIN -->` 다음 개행부터
`<!-- VERBATIM-END -->` 직전 개행까지의 바이트열(UTF-8).
