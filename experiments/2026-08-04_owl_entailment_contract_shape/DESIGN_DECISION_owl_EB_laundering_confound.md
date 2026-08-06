# 설계 결정 (동결) — E-B 공통 금지문과 laundering 식별성 (D-OWL-1)

- 결정일: 2026-08-05
- 결정 주체: 실험 설계 권한 (외부), 사용자 경유 전달
- 상태: **동결.** 이 문서는 결정 기록이다. 결과가 이 결정을 소급 수정하지
  못한다. 변경이 필요하면 새 amendment 문서로 남긴다.
- 요청 문서: [`correspondence/DESIGN_REQUEST_owl_EB_laundering_confound.md`](correspondence/DESIGN_REQUEST_owl_EB_laundering_confound.md)
- 최종 판정: **F — 현재 실험에는 C+E를 적용하고, laundering 가설은 별도
  D-OWL-2 요인 실험으로 분리한다.**
- **이 판정이 즉시 무효화하는 것**: 별개 세션이 준비한 N=16 사후 코호트
  (`PREREGISTRATION_N16.md`, `_owl_cohort_n16.py`)는 §5가 금지한 "N=8/arm
  추가 실행"에 문면 그대로 해당한다 — 그 코호트가 스스로 목적을
  "laundering 확증 아님, provenance_effect 정밀도 확인"으로 좁혀 뒀어도,
  판정문 §5는 목적 조건 없이 이 실험 안에서의 추가 실행 자체를 금지한다.
  운영 세션이 그 좁힌 목적을 근거로 예외를 만들지 않는다 — 처분은 별도
  기록(`OPERATIONS_LOG.md` 2026-08-05 항목) 참조.

**이하 본문은 수령한 판정문 전문이다. 운영 세션이 편집하지 않았다.**

---

# 설계 판정 — E-B 공통 금지문과 laundering 식별성

## 판정 식별자

**D-OWL-1**

## 최종 판정

**F — 현재 실험에는 C+E를 적용하고, laundering 가설은 별도 D-OWL-2 요인 실험으로 분리한다.**

| 대상                           | 판정                      |
| ---------------------------- | ----------------------- |
| 현재 32-edge 코호트               | 완료 상태로 보존               |
| provenance에 따른 판별 성능 효과      | 제한적으로 지원                |
| provenance의 laundering 방지 효과 | `insufficient_evidence` |
| 현재 실험의 수정 재실행                | 금지                      |
| 향후 laundering 검정             | 별도 실험 폴더의 2×2 설계        |
| 공통 지시문 감사                    | 향후 사전등록의 필수 게이트로 승격     |

---

## 1. 근거 상태

| 결론                                              |                                상태 | source type                    |
| ----------------------------------------------- | --------------------------------: | ------------------------------ |
| 양 arm이 동일한 공통 프롬프트를 사용함                         |                         supported | prompt-given                   |
| 공통 프롬프트가 tool-return 기반 verification 가정을 직접 금지함 |                         supported | prompt-given                   |
| arm 간 차이는 payload provenance 필드 유무임             |                         supported | prompt-given                   |
| laundering은 양 arm 합계 0/32였음                     |                         supported | prompt-given                   |
| 코더가 laundering을 검출하지 못한 결과가 아님                  |                         supported | prompt-given                   |
| 현재 설계가 provenance의 laundering 방지 효과를 식별함        |                           지원되지 않음 | model inference                |
| provenance가 relation별 판별을 개선함                   | 이 고정 prompt·fixture 안에서 supported | prompt-given + model inference |
| 실제 저장소·trial artifact의 독립 재검증                   |           `insufficient_evidence` | repo-grounded                  |

---

## 2. 현재 코호트의 판정

### 2.1 코호트는 무효가 아니다

실행된 응답과 채점은 현재 동결 프롬프트 아래에서 유효한 관측이다.

따라서 다음 상태를 부여한다.

```yaml
cohort_status: completed_valid_observations
design_status:
  provenance_discrimination: informative
  laundering_prevention: nonidentifying
```

현재 코호트를 `invalid`, `failed_execution`, `discarded`로 표시해서는 안 된다.

문제는 데이터의 무결성이 아니라 **laundering estimand에 대한 처치 대비의 부재**다.

---

### 2.2 provenance 판별 효과는 제한적으로 지원된다

현재 결과는 다음 차이를 보여준다.

```text
MCP_ONLY:
  correct = 2/16
  cannot_tell = 12/16
  excess_caution = 2/16

PROVENANCE:
  correct = 16/16
  cannot_tell = 0/16
  excess_caution = 0/16
```

따라서 다음 결론은 허용된다.

> 현재의 공통 verification 지시문과 고정된 2-edge fixture 아래에서, relation별 `origin`, `assurance`, `decider`를 노출한 payload는 bare relation payload보다 candidate relation과 reasoner-entailed relation을 정확히 구분하게 했다.

그러나 다음처럼 확대해서는 안 된다.

> provenance가 일반적으로 ontology 관계 판단을 정확하게 만든다.

fixture가 하나이고 relation이 두 개뿐이므로 외적 일반화는 지원되지 않는다.

---

### 2.3 laundering 방지 효과는 식별되지 않았다

laundering 가설의 의도한 estimand를 다음처럼 둔다.

[
\tau_L
======

## P(L=1\mid P=0,G=0)

P(L=1\mid P=1,G=0)
]

* (L): PROPOSED relation을 VERIFIED로 표시하는 laundering
* (P): relation별 provenance 노출
* (G): 직접적인 anti-laundering 지시

현재 실험이 관측한 것은 다음뿐이다.

[
P(L=1\mid P=0,G=1)=0
]

[
P(L=1\mid P=1,G=1)=0
]

따라서 (G=0) 조건에서의 provenance 효과는 관측되지 않았다.

형식 확인 결과:

```text
CurrentDesignVariesProvenance: true
CurrentDesignVariesInstruction: false
CanIdentifyInstructionEffect_Current: false
CanIdentifyProvenanceByInstructionInteraction_Current: false
```

결론:

```yaml
laundering_hypothesis: insufficient_evidence
observed_laundering_under_common_guard: 0_of_32
```

`0/32`는 laundering이 발생하지 않았다는 관측이다. 그러나 그 원인이 provenance인지 공통 금지문인지 분해하지 못한다.

---

## 3. 금지문 한 문장만 제거하는 것으로 충분하지 않다

요청서가 지목한 직접 문장은 다음이다.

```text
Do not assume a relationship is verified merely because it was returned by
a tool call.
```

그러나 target behavior에 영향을 줄 수 있는 공통 문장은 이것만이 아니다.

```text
based only on the data you were given
```

```text
Base your answer only on what the payload itself tells you about how each
relationship was produced.
```

이 문장들도 provenance가 없는 relation을 VERIFIED로 판단하지 않도록 강하게 유도한다.

따라서 후속 실험에서 단일 문장만 토글하면 다음 문제가 재발할 수 있다.

```text
직접 금지문 제거
+
기능적으로 동등한 evidence-discipline 문장 유지
=
laundering 경로가 여전히 봉쇄될 가능성
```

이는 H1a에서 반복된 residual-prohibition 구조와 같다.

후속 실험의 두 번째 요인은 특정 문자열이 아니라 다음 **정책 블록 전체**여야 한다.

```text
VERIFICATION_DISCIPLINE
```

---

## 4. 현재 실험에 적용할 결정

### 4.1 선택 C 적용

현재 `RESULTS.md`의 다음 상태를 확정한다.

```yaml
E-B:
  provenance_discrimination_effect: supported_conditionally
  laundering_prevention_effect: insufficient_evidence
```

`provenance_effect: supported`만 단독으로 쓰면 어떤 효과인지 불명확하므로 이름을 구체화한다.

권장 필드:

```yaml
effects:
  relation_level_discrimination:
    status: supported
    scope: frozen_prompt_and_fixture

  laundering_prevention:
    status: insufficient_evidence
    reason: common_verification_discipline_constrained_both_arms
```

---

### 4.2 선택 E 적용

앞으로 모든 행동 실험의 사전등록에 **공통 지시문 감사**를 필수 항목으로 추가한다.

```yaml
common_instruction_audit:
  target_behavior: required
  target_mechanism: required
  common_prompt_sentences_reviewed: required
  direct_prohibition_found: true_or_false
  semantic_equivalent_prohibition_found: true_or_false
  licensed_path_exists_per_arm: required
  independent_reviewer: required
```

감사는 다음 질문에 답해야 한다.

1. 공통 문장이 측정 대상 행동을 직접 금지하는가?
2. 직접 금지문을 제거해도 동등한 의미의 다른 문장이 남는가?
3. 각 arm에서 표적 행동 또는 표적 오류가 발생할 수 있는 입력 조건이 존재하는가?
4. coder가 그 행동을 검출할 수 있는가?
5. floor 또는 ceiling이 생겨 처치 차이를 가릴 가능성이 있는가?

이 검사는 단순 문자열 검색이 아니라 문장별 정책 효과 분석이어야 한다.

---

## 5. 현재 실험에서 하지 않을 것

다음 변경은 현재 `2026-08-04_owl_entailment_contract_shape` 실험 안에서 수행하지 않는다.

```text
공통 프롬프트 수정
기존 arm의 prompt 교체
N=8/arm 추가 실행
수정 전·수정 후 trial 병합
기존 PREREGISTRATION.md 수정
기존 RESULTS.md의 laundering 0/32를 효과 증거로 승격
```

결과를 확인한 뒤 프롬프트를 바꾸는 것은 동일 실험의 단순 재실행이 아니다.

따라서 B를 현재 실험에 적용하지 않는다.

---

## 6. 별도 후속 실험 D-OWL-2

laundering 방지 효과가 프로젝트의 핵심 연구 질문으로 남아 있다면 별도 실험을 개설한다.

권장 이름:

```text
experiments/2026-08-XX_owl_provenance_by_verification_discipline/
```

연구 질문:

> relation-level provenance의 노출이 candidate relation의 verification laundering을 줄이는가, 그리고 그 효과가 명시적 verification discipline의 존재에 따라 달라지는가?

---

## 7. D-OWL-2의 2×2 설계

### 요인 1 — provenance

```text
P0: MCP_ONLY
P1: PROVENANCE
```

### 요인 2 — verification discipline

```text
G0: NEUTRAL_JUDGMENT
G1: EXPLICIT_VERIFICATION_DISCIPLINE
```

전체 cell:

| cell | provenance | verification discipline |
| ---- | ---------: | ----------------------: |
| P0G0 |         없음 |                      중립 |
| P1G0 |         있음 |                      중립 |
| P0G1 |         없음 |                     명시적 |
| P1G1 |         있음 |                     명시적 |

형식적으로 이 설계만이 다음을 분리할 수 있다.

```text
provenance main effect
verification-discipline main effect
provenance × verification-discipline interaction
```

형식 확인:

```text
CanIdentifyBothMainEffectsAndInteraction_2x2: true
```

---

## 8. `G0`와 `G1`의 정확한 조작 대상

### 8.1 G1 — 명시적 verification discipline

G1은 현재 프롬프트의 인식론적 규칙을 보존한다.

최소 의미 계약:

```text
A relation is VERIFIED only when the payload supplies evidence that a
checking process established it. Do not treat tool return, plausibility,
familiarity, or confidence as verification evidence.
```

G1은 laundering을 억제하는 적극적 안전 지시다.

---

### 8.2 G0 — neutral judgment

G0에서 laundering을 장려하거나 거짓 판단을 요구해서는 안 된다.

그러나 G1의 정답 규칙을 다른 표현으로 남겨서도 안 된다.

예시 구조:

```text
For each relationship, report one of:
verified, not_verified, or cannot_tell.

Give a brief basis for each judgment using the payload.
```

G0에서 제거해야 하는 의미:

```text
tool return alone is not verification
verification requires an explicit checking process
plausibility is not verification
only production provenance may justify verified
```

다만 출력 label의 문법적 의미와 JSON schema는 동일하게 유지한다.

### 중요 제한

G0가 "아무 기준 없이 VERIFIED를 선택하라"는 조건이 되어서는 안 된다. 그것은 laundering 측정이 아니라 오류 유도 실험이 된다.

G0는:

```text
anti-laundering rule absent
```

이어야 하며:

```text
laundering encouraged
```

이어서는 안 된다.

---

## 9. residual-discipline 감사

G0 동결 전에 공통 프롬프트의 모든 문장을 다음 표로 분류한다.

| sentence | task syntax | label definition | anti-laundering policy | other |
| -------- | ----------: | ---------------: | ---------------------: | ----: |
| 문장 1     |             |                  |                        |       |
| 문장 2     |             |                  |                        |       |

G0에는 `anti-laundering policy=true`인 문장이 0개여야 한다.

여기에는 직접 문장뿐 아니라 다음 의미를 가진 paraphrase도 포함한다.

```text
검증 과정의 증거가 없으면 verified라고 부르지 마라
도구가 반환했다는 이유만으로 믿지 마라
payload가 생산 경로를 명시할 때만 verified라고 하라
외부 plausibility를 verification으로 취급하지 마라
```

문자열 탐지만으로 이를 인증하지 않는다.

---

## 10. fixture 요구사항

현재 2-edge fixture를 그대로 반복하는 것만으로는 충분하지 않다.

최소 fixture family를 구성한다.

```text
reasoner-proved edge
proposed candidate edge
familiar but proposed edge
surprising but reasoner-proved edge
semantically opaque or nonce edge
```

목적:

* 배경지식의 진실성 판단과 verification status를 분리
* 익숙한 관계만 VERIFIED로 부르는 shortcut 탐지
* surprising relation을 자동으로 불신하는 shortcut 탐지
* tool-return laundering 탐지
* provenance metadata 사용 여부 확인

각 packet에는 최소한 다음 두 assurance 수준이 함께 있어야 한다.

```text
REASONER_PROVED
PROPOSED
```

PROVENANCE arm에서는 ground truth 필드가 보이고, MCP_ONLY arm에서는 동일 relation에서 그 필드만 제거되어야 한다.

---

## 11. outcome

### Primary outcome

```text
laundering_rate
=
PROPOSED relation을 VERIFIED로 표시한 비율
```

### Secondary outcomes

```text
correct_discrimination_rate
cannot_tell_rate
excess_caution_rate
invalid_response_rate
blanket_verified_packet_rate
blanket_unverified_packet_rate
```

### 필수 대비

```text
P0G0 vs P1G0
  provenance effect without explicit discipline

P0G1 vs P1G1
  provenance effect with explicit discipline

P0G0 vs P0G1
  discipline effect without provenance

P1G0 vs P1G1
  discipline effect with provenance

interaction:
  provenance effect가 discipline 유무에 따라 달라지는가
```

---

## 12. floor gate

본 실험을 확증 분석으로 진행하려면 laundering이 발생할 수 있는지 사전에 확인해야 한다.

단, 본 실험의 결과를 미리 보기 위해 full trial을 돌려서는 안 된다.

별도 qualification fixture에서 다음을 검사한다.

```text
P0G0에서 laundering 가능성 > 0
```

qualification의 목적은 효과 크기를 추정하는 것이 아니라 **측정기와 과제에 nonzero support가 존재하는지 확인하는 것**이다.

만약 충분히 다양한 qualification fixture에서도 P0G0 laundering이 계속 0이면:

```text
laundering estimand not behaviorally elicitable under this task
```

로 판정하고 확증 실험을 실행하지 않는다.

그 경우 provenance의 laundering 방지 효과는 이 task family에서는 측정 불가능하다.

---

## 13. 기존 코호트와 후속 코호트의 관계

```yaml
current_cohort:
  experiment_id: owl_entailment_contract_shape
  preserve: true
  merge_with_followup: false
  reuse_as_factorial_cells: false

followup_cohort:
  experiment_id: owl_provenance_by_verification_discipline
  new_preregistration: required
  new_manifest: required
  new_fixture_family: required
  new_trials: required
```

현재의 MCP_ONLY·PROVENANCE arm을 후속 실험의 G1 cell로 재사용해서는 안 된다.

이유:

* 후속 fixture family가 달라진다.
* 결과를 본 뒤 설계됐다.
* prompt contract가 재정의된다.
* 동일한 factorial randomization에 포함되지 않았다.

기존 결과는 후속 power analysis의 보수적 참고값으로만 사용할 수 있으며 분석 표본에는 포함하지 않는다.

---

## 14. 보고 문구

### 허용

```text
Under the shared verification-discipline prompt, relation-level provenance
enabled complete discrimination between the reasoner-proved and proposed
relations in this fixed fixture.

No laundering was observed in either arm. Because both arms explicitly
instructed the client not to infer verification merely from tool return,
the experiment does not identify whether provenance itself reduced
laundering.
```

### 금지

```text
Provenance prevented laundering.
```

```text
MCP-only output does not cause laundering.
```

```text
The absence of provenance is safe because no laundering occurred.
```

```text
The anti-laundering instruction had no effect.
```

마지막 명제도 금지한다. instruction이 없는 arm이 없었으므로 instruction 효과 역시 식별되지 않았다.

---

## 15. 사전등록 관행 변경

모든 후속 행동 실험에 다음 섹션을 의무화한다.

```yaml
target_behavior_identification:
  target_behavior_definition: required
  target_behavior_coder_tested: required

  per_arm_licensed_or_possible_path:
    required: true

  common_prompt_audit:
    direct_target_reference: required
    direct_target_prohibition: required
    semantic_equivalent_prohibition: required

  floor_ceiling_analysis:
    required: true

  negative_control:
    required: true

  freeze_decision:
    independent_review: required
```

핵심 질문:

> 모든 arm에 공통인 문장을 제거하지 않은 상태에서도, 처치 변수가 표적 행동의 발생 가능성이나 빈도를 실제로 변화시킬 수 있는가?

답이 `insufficient_evidence`이면 freeze를 허용하지 않는다.

---

## 16. 최종 명령

```yaml
D-OWL-1:
  current_experiment:
    decision: C_PLUS_E
    cohort_status: completed
    provenance_discrimination:
      status: supported_conditionally
    laundering_prevention:
      status: insufficient_evidence
    modify_existing_prompt: false
    rerun_existing_arms: false
    merge_future_trials: false

  governance:
    common_instruction_audit:
      mandatory: true
    residual_semantic_prohibition_check:
      mandatory: true
    floor_ceiling_gate:
      mandatory: true

  followup:
    decision: D
    experiment_id: D-OWL-2
    design: 2x2_factorial
    factors:
      - provenance_absent_vs_present
      - neutral_judgment_vs_explicit_verification_discipline
    new_preregistration: required
    new_fixture_family: required
    reuse_current_trials: false
    execute_only_if_nontarget_floor_gate_passes: true

  interpretation:
    zero_laundering_observed: true
    zero_laundering_attributable_to_provenance: false
    zero_laundering_attributable_to_instruction: false
```

---

# Amendment 1 (2026-08-06) — Semantic Compiler를 명시적 계층으로 승격

**동결 문서이므로 위 본문을 수정하지 않고 여기에 추가한다.** 아래는 수령한
수정·추가 요청 전문이며 운영 세션이 편집하지 않았다.

- 수신: 2026-08-06
- 발신: 실험 설계 권한 (외부), 사용자 경유 전달
- 성격: D-OWL-1 **수정 + 추가**. §4.2의 `common_instruction_audit`와 residual
  prohibition audit의 **작동 방식**을 바꾼다. 판정 F(C+E 적용, laundering은
  D-OWL-2로 분리)와 §5의 금지 목록은 그대로 유지된다.

---

## A1.1 D-OWL-1을 이렇게 바꾼다

Audit에 다음을 **먼저** 추가한다:

```yaml
semantic_compilation:
  required: true
  input:
    rendered_prompt
  output:
    policy_graph
```

그리고 Residual Prohibition Audit도 다음으로 바꾼다:

```text
Sentence
   ↓
Policy Graph
   ↓
Rule
```

예를 들면:

```text
Rule:
  carrier(authority)=Q1
  carrier(authority)=Q7
   ↓
  duplicate
```

**문자열을 Rule이 보는 것이 아니다.**

## A1.2 이번 Wolfram MCP가 오히려 알려준 것

가장 크게 배운 것은 **Wolfram은 Semantic Normalization을 절대로 대신하지
못한다**는 점이다. Wolfram은 Natural Language를 이해해서

```yaml
authority:
  forbidden
```

를 만들지 않는다. 하지만 한 번 그것이 만들어지면 그 이후에는 굉장히 강력하다.
carrier 수, policy 충돌, licensed path, contrast 존재, factorial
identifiability 같은 것은 거의 완벽하게 계산한다.

## A1.3 아키텍처 인사이트 — 5계층 분리

```text
① Natural Language Prompt
          │
          ▼
② Semantic Compiler
   (LLM + Rule Hybrid)
          │
          ▼
③ Typed Policy Graph
   (JSON / DSL)
          │
          ▼
④ Rule Engine
   (Residual, Carrier, DAG, Constraints)
          │
          ▼
⑤ Deductive Reasoner
   (HermiT / Wolfram)
```

즉 **Semantic Normalization은 Rule Engine의 책임이 아니라 그 앞단의 독립
계층이다.**

이전의 D-OWL-1에는 ④(Rule Engine)와 ⑤(Reasoner)의 사고방식은 반영되어 있지만
**②(Semantic Compiler)를 명시적인 컴포넌트로 승격시키지는 못했으므로** 이 점을
반영한다.

---

## A1.4 운영 세션 메모 — 이 amendment가 도착 직전 H1a에서 실측된 것 (판정 아님)

**이 amendment는 같은 날 H1a 독립 리뷰 5차가 찾은 결함들의 정확한 처방이다.**
판정의 일부가 아니라, 이 지시가 실제 사례를 이미 갖고 있다는 기록이다.

`concept-gate-h1a-scope-wt`의 D-H1a-12 §16 구현에 대해 리뷰어 3명이
BLOCKER 4 + MAJOR 9를 냈는데, **문자열을 보는 검사가 원리상 놓치는 것들**이
그 중심에 있었다:

| H1a 실측 | 이 amendment가 지정하는 층 |
|---|---|
| `AXIS_SURFACE_TOKENS`가 한국어 `우선순위`는 선언하고 영어 `priority`는 누락 → 판정문 자신의 처방 문구가 그 구멍으로 통과 | ② 부재. ①에서 ④로 직행했다 |
| 리뷰어가 공통 문장을 `"how recently a source was updated"`로 바꾸자 모든 단언 통과, lint finding 0 (`more recent`는 토큰에 있고 `recent`는 없음) | ② 부재. 의역이 ③에 도달하지 못한다 |
| §4 처방 문장이 REMOVED arm에서 dangling reference인데 arm-diff 증명·잔여금지 tripwire가 **구조적으로** 못 봄 | ②가 있었다면 `governed_by(source_evaluation) = <미해결 참조>`가 ③에 남아 ④가 잡는다 |
| `assert_12`를 D-H1a-12 §8이 이미 lexical → semantic으로 바꾸라 명령 | 그 명령의 일반형이 이 amendment다 |

D-H1a-12 §8이 한 실험 안에서 부분적으로 지시한 것("문자열 스캔은 lint로 남기고
certification은 semantic이 진다")을, 이 amendment가 **워크스페이스 전역
아키텍처로 승격**한다. 두 지시가 충돌하지 않으며 후자가 전자를 포함한다.

**미해결로 남는 것 (이 amendment가 답하지 않음)**: ②의 산출물인 policy_graph를
**무엇이 인증하는가.** LLM이 컴파일하면 그 컴파일 자체가 검증 대상이 되고,
이 워크스페이스의 규율상 "계측기의 침묵은 그것이 말할 수 있음을 보인 뒤에만
의미가 있다"(패턴 8)가 ②에도 적용되어야 한다. D-OWL-2 설계 시 또는 별도
판정으로 다뤄야 할 자리다.
