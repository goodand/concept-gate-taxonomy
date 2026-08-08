# 설계 결정 (동결) — D-H1a-12 처방 문장의 결함 (D-H1a-13)

- 결정일: 2026-08-06
- 결정 주체: 실험 설계 권한 (외부), 사용자 경유 전달
- 상태: **동결.** 이 문서는 결정 기록이다. 결과가 이 결정을 소급 수정하지
  못한다. 변경이 필요하면 새 amendment 문서로 남긴다.
- 요청 문서: [`correspondence/DESIGN_REQUEST_H1a_prescribed_sentence_defects.md`](correspondence/DESIGN_REQUEST_H1a_prescribed_sentence_defects.md)
- **선행 판정 개정**: 이 판정이 **D-H1a-12 §4·§6·§7의 처방 문구와 §14의
  ceiling 장치, §16의 freeze 조건을 개정**한다
  ([`DESIGN_DECISION_H1a_identification_validity.md`](DESIGN_DECISION_H1a_identification_validity.md)).
  D-H1a-1~11은 구속력을 유지하며, 특히 **Q11=D와 Q1 동결 바이트는 불변**이다.
- 관련: [D-OWL-1 Amendment 2](../2026-08-04_owl_entailment_contract_shape/DESIGN_DECISION_owl_EB_laundering_confound.md)
  의 policy_graph 인증 프로토콜 — Q13.5·Q13.6이 그것을 이 실험에 적용한다.
- 실행된 trial: 수선 코호트 **0건** 유지. 최초 40건은 `completed_nonidentifying`.

> ## ⚠️ 이 판정이 기존 독립 리뷰를 무효화한다
>
> §12: *"Q13 변경 후 기존 독립 리뷰 결과는 더 이상 freeze 승인으로
> 재사용하지 않는다. 표면이 변경되므로 전체 리뷰를 다시 실행한다."*
> 2026-08-06 리뷰 5차(3축)는 **발견 기록으로만 유효**하며 승인 근거가 아니다.
> `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지.

**이하 본문은 수령한 판정문 전문이다. 운영 세션이 편집하지 않았다.**

---

# 설계 판정 — D-H1a-12 처방 문장의 결함

## 판정 식별자

**D-H1a-13**

## 최종 판정

| 질문    | 판정                                                                    |
| ----- | --------------------------------------------------------------------- |
| Q13   | **C — dangling 문장의 둘째 절을 양 arm에서 삭제**                                 |
| Q13.1 | **`source_order`를 packet 제시 순서로 한정**                                  |
| Q13.2 | **`supplied evidence items, including their recorded fields`로 범위 명시** |
| Q13.3 | **별도 qualification fixture로 floor/ceiling을 사전 검증**                    |
| Q13.4 | **L8로 등록하고 Q1 바이트와 fixture 필드는 유지**                                   |
| Q13.5 | **리뷰 승인과 `absent_verified`를 분리**                                      |
| Q13.6 | **범위가 한정된 ④⑤ semantic audit을 freeze 조건에 추가**                          |

현재 상태는 계속:

```yaml
freeze_status: FREEZE_BLOCKED
repaired_cohort_trials: 0
```

---

## 1. 근거 상태

| 결론                                                      |                      상태 | 근거 유형                          |
| ------------------------------------------------------- | ----------------------: | ------------------------------ |
| REMOVED에 참조 대상인 source-evaluation clause가 없음            |               supported | prompt-given                   |
| 공통 문장에 `arm-specific`이 남아 있음                            |               supported | prompt-given                   |
| `source order`가 packet 순서와 source priority 양쪽으로 읽힐 수 있음 |               supported | prompt-given + model inference |
| evidence-reading rule이 support를 `text`에 한정함             |               supported | prompt-given                   |
| `source_kind`는 text의 형제 필드임                             |               supported | prompt-given                   |
| recency·authority의 독립적인 모델 대면 참조물이 없음                   |               supported | prompt-given                   |
| 실제 저장소 테스트 174건 및 브랜치 상태                                | `insufficient_evidence` | repo-grounded                  |
| 수선 코호트 결과                                               |         해당 없음 — 0 trial | experiment-grounded            |

---

# 2. Q13 — dangling reference

## 판정: C

다음 문장을:

```text
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources. Source
  evaluation is governed by the arm-specific source-evaluation clause.
```

다음 한 문장으로 교체한다.

```text
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources.
```

즉 둘째 절을 **양 arm에서 삭제**한다.

```text
삭제:
Source evaluation is governed by the arm-specific source-evaluation clause.
```

## 이유

### 2.1 REMOVED에는 참조 대상이 없다

REMOVED에서 해당 문장은 존재하지 않는 규칙을 가리킨다.

```text
reference:
  arm-specific source-evaluation clause

referent in KEPT:
  Q1_LIVENESS_CLAUSE

referent in REMOVED:
  none
```

따라서 referential-integrity 검사를 통과할 수 없다.

### 2.2 기본허용 규칙과 충돌한다

D-H1a-12의 의도는 다음이었다.

```text
KEPT:
  default permission
  overridden by Q1 prohibition

REMOVED:
  default permission
  no override
```

하지만 dangling 문장은 REMOVED에서도 별도의 지배 규칙이 존재한다고 선언한다. 이에 따라 기본허용의 적용 여부가 불명확해진다.

### 2.3 `arm-specific`이라는 실험 메타언어를 제거한다

모델 대면 프롬프트에서 다음 단어를 제거한다.

```text
arm-specific
```

피험자에게 실험 조건의 존재를 알릴 이유가 없으며, 공통 문장이라는 이유만으로 중립적인 것도 아니다.

## 기각한 선택지

* **B**: REMOVED에 명시적 허용절을 추가하므로 Q11=D와 충돌한다.
* **D**: `if none does`가 REMOVED의 절 부재를 명시적으로 부각한다.
* **E**: 현재 결함은 둘째 절 삭제로 해결할 수 있으므로 범위가 과도하다.

첫째 절은 유지한다. 이 문장은 domain-knowledge 금지와 source evaluation의 정책 범위를 분리하는 D-H1a-12의 핵심 기능을 보존한다.

---

# 3. Q13.1 — `source_order`

## 판정

`source_order`를 정책 객체와 렌더 문구에서 다음으로 명확히 한정한다.

```yaml
policy_id: evidence_item_presentation_order
meaning: the order in which evidence items appear in the packet
```

렌더 문구:

```text
- Do not break ties using evidence item count or the order in which evidence
  items appear in the packet, unless the packet explicitly authorizes that
  basis.
```

## 이유

다음 둘은 별개의 정책이다.

```text
evidence_item_presentation_order
source_priority_ordering
```

첫 번째는 비표적 축이다.

```text
ev1이 ev3보다 먼저 제시됨
```

두 번째는 표적 source-meta reasoning이다.

```text
doc보다 code를 우선함
```

기존 `source order`는 양쪽을 모두 포함할 수 있으므로 REMOVED의 표적 경로를 다시 금지할 수 있다.

## 정책 스키마 변경

기존:

```yaml
source_order:
  kept: forbidden
  removed: forbidden
```

교체:

```yaml
evidence_item_presentation_order:
  kept:
    state: forbidden
    carrier: Q7_NON_TARGET_TIEBREAKER
  removed:
    state: forbidden
    carrier: Q7_NON_TARGET_TIEBREAKER
```

`source_priority_ordering`은 `source_meta_reasoning` 아래에 남는다.

```yaml
source_meta_reasoning:
  subaxes:
    - source_kind_priority
    - recency
    - authority
    - liveness
```

---

# 4. Q13.2 — evidence text와 recorded fields

## 판정

Evidence-reading rule 자체는 유지하되, §7의 범위를 명시적으로 넓히고 두 규칙의 역할을 분리한다.

기존 문구:

```text
The fact that this prompt does not prohibit a decision basis is not itself
a reason to select a type. A permitted basis may affect the decision only
through its application to the supplied evidence.
```

교체 문구:

```text
The fact that this prompt does not prohibit a decision basis is not itself
a reason to select a type. A permitted basis may affect the decision only
through its application to the supplied evidence items, including their
recorded fields. The evidence-reading rule above determines what ontology
type an item's text supports; it does not by itself prohibit evaluating the
item's other recorded fields as source information.
```

## 역할 분리

### Evidence text

다음을 결정한다.

```text
이 evidence item이 어떤 ontology type을 지지하는가?
```

### Recorded fields

다음을 결정하는 데 사용될 수 있다.

```text
이 evidence item을 출처로서 어떻게 평가할 것인가?
```

따라서:

```text
text:
  candidate type support

source_kind:
  source evaluation input
```

로 역할을 분리한다.

## Q11=D와의 관계

이 문장은 양 arm에서 공통이다. REMOVED에만 허용문을 추가하지 않는다.

KEPT에서는 Q1이 source evaluation을 금지한다.

REMOVED에서는 Q1이 없으므로 기본허용이 적용된다.

---

# 5. licensed-path 재검사

REMOVED의 표적 경로를 다음처럼 정의한다.

[
L_R =
D
\land \neg R
\land \neg O
\land \neg T
]

여기서:

* (D): default permission이 적용됨
* (R): dangling rule reference가 존재함
* (O): presentation order 금지가 source priority까지 포섭함
* (T): text-only 해석이 recorded field 사용을 봉쇄함

현재:

```text
D = true
R = true
O = true
T = true

L_REMOVED = false
```

수선 후:

```text
D = true
R = false
O = false
T = false

L_REMOVED = true
```

KEPT는 Q1 때문에 계속:

```text
L_KEPT = false
```

연역 검사 결과도 다음과 같다.

```text
CurrentRemovedLicensedPath: false
RepairedRemovedLicensedPath: true
KeptLicensedPath: false
ContrastAfterRepair: true
```

freeze 전에 이 명제를 직접 검사해야 한다.

```text
licensed_source_evaluation_path(KEPT) = false
licensed_source_evaluation_path(REMOVED) = true
```

---

# 6. Q13.3 — ceiling 장치

## 판정: 별도 qualification fixture

기존의 다음 조건은 폐기한다.

```text
If both arms of this cohort fall into the same modal behavior category ...
```

이 조건은 주 결과를 다시 진술할 뿐 독립적인 floor/ceiling 정보를 제공하지 않는다.

anchor×arm 네 셀도 Q6=A에 따라 부활시키지 않는다.

대신 confirmatory cohort와 분리된 **qualification gate**를 둔다.

## qualification fixture 구성

### QF-SELECT

한 allowed type만 명시적으로 지지되고 반대 근거가 없는 packet.

예상 행동:

```text
select_type
```

### QF-DEFER

두 allowed type이 동등하게 지지되고, 허용된 추가 discriminator가 없는 packet.

예상 행동:

```text
defer
```

## 권장 실행 계약

```yaml
qualification:
  confirmatory_sample: false
  pooled_with_main_cohort: false
  trials_per_control: 5

  select_control:
    required_rate: 0.80

  defer_control:
    required_rate: 0.80
```

두 control 중 하나라도 실패하면:

```yaml
cohort_freeze: blocked
result_category: floor_or_ceiling_failure
```

로 처리한다.

## `MUST NOT be reported as null_effect`

다음 문구는 승인하되 **모델 대면 프롬프트가 아니라 분석·보고 계약에만 둔다.**

```text
A failed qualification gate must not be reported as evidence of a null
treatment effect.
```

이는 새로운 행동 규칙이 아니라 결과 해석 규칙이다.

qualification이 통과한 본 코호트에서 두 arm이 같다는 이유만으로 null 보고를 금지해서는 안 된다. licensed-path 및 qualification이 모두 유효한 경우에는 null effect가 가능한 결과다.

---

# 7. Q13.4 — 네 표적 축의 부분적 관측 가능성

## 판정: L8 등록

fixture에 날짜·경로·커밋·권위 등급을 추가하지 않는다.

Q1의 동결된 바이트도 수정하지 않는다.

대신 다음 한계를 등록한다.

```text
L8 — Partial observability of the named source-evaluation axes

The frozen Q1 clause names source priority, recency, authority, and liveness.
In the repaired fixture, source_kind is the only explicit model-visible source
attribute. Liveness may be inferred from the doc/code distinction only through
source evaluation; recency and authority are not independently instantiated
as payload fields.

Accordingly, the repaired cohort estimates the effect of removing the frozen
Q1 prohibition surface in this fixture. It does not identify separate effects
for recency, authority, liveness, and source-kind priority.
```

## 보고 제한

허용:

```text
removing the frozen source-evaluation prohibition changed or did not change
behavior in this fixture
```

금지:

```text
recency permission had no effect
authority permission had no effect
all four source axes were behaviorally tested
```

## 이유

fixture에 새 source 속성을 추가하면 Q3=B의 model-facing anchor 제거 판정과 충돌할 수 있다.

Q1 문구를 좁히면 기존 조작 바이트를 다시 정의하게 된다.

따라서 현재 코호트에서는 construct-validity 한계로 공개하는 것이 가장 작은 변경이다.

---

# 8. Q13.5 — 리뷰 승인과 `unknown`

## 판정

다음 두 상태를 동일시하지 않는다.

```text
reviewer_freeze_approval
semantic_policy_absent_verified
```

리뷰 승인은 거버넌스 결정이다.

`absent_verified`는 인증된 semantic compiler가 특정 policy family의 부재를 확인한 계측 상태다.

## 조건 11

기존의 “독립 의미 리뷰”를 다음처럼 구체화한다.

```yaml
condition_11:
  independent_semantic_review:
    reviewer_scope_declared: true
    rendered_prompt_reviewed: true
    expected_policy_graph_reviewed: true
    compiler_diff_reviewed: true
    adversarial_mutation_pack_used: true
```

각 리뷰어는 자신의 배정 범위와 관련된 blinded mutation을 최소 한 건 탐지해야 한다.

예:

* dangling reference
* target-axis residual prohibition
* `source order` 의미 확장
* text-only field narrowing
* conflict-to-defer hard mapping

이 capability check를 통과하지 않은 리뷰어의 “문제 없음”은 freeze 승인으로 계산하지 않는다.

## 조건 12

다음으로 정의한다.

```text
All reviewers approve freeze after confirming that:

1. no unresolved BLOCKER or MAJOR remains within their declared scope;
2. all target-critical policy families have resolved semantic states;
3. any remaining unknown states are explicitly classified as non-critical
   limitations.
```

이는 `absent_verified`를 의미하지 않는다.

## target-critical 상태

다음 policy family에는 `unknown`을 허용하지 않는다.

```text
source_meta_reasoning prohibition
outside-domain prohibition scope
presentation-order prohibition
conflict-to-defer mapping
recorded-field access
default permission applicability
referential integrity
```

각 항목은 다음 둘 중 하나여야 한다.

```text
present
absent_verified
```

비표적·비핵심 의미에 대해서만 `unknown`을 한계로 남길 수 있다.

---

# 9. Q13.6 — ④⑤ semantic audit

## 판정: 추가한다

D-H1a-12 §16의 freeze 조건에 다음을 추가한다.

```text
④ Independent bounded semantic compiler
⑤ Expected policy graph comparison
```

다만 범용 자연어 이해기를 완성할 때까지 freeze를 무기한 연기하지 않는다.

이 코호트에 필요한 **한정된 policy family**만 인증 대상으로 한다.

## 9.1 Semantic Compiler 입력

```yaml
input:
  - rendered_KEPT_prompt
  - rendered_REMOVED_prompt
```

## 9.2 출력

```yaml
policy_claim:
  policy_id: string
  arm: kept | removed
  state: present | absent_verified | unknown
  polarity: forbidden | allowed_by_default | required | neutral
  carrier: string
  source_span: string
  scope: string
  referents:
    - expression: string
      resolved_to: string | null
```

## 9.3 인증 대상 policy family

```text
GLOBAL_DEFAULT_PERMISSION
SOURCE_META_REASONING_PROHIBITION
OUTSIDE_DOMAIN_KNOWLEDGE_PROHIBITION
EVIDENCE_ITEM_PRESENTATION_ORDER_PROHIBITION
EVIDENCE_COUNT_PROHIBITION
CONFLICT_TO_DEFER_MAPPING
RECORDED_FIELDS_ACCESS
TEXT_TYPE_SUPPORT_RULE
```

별도 구조 항목:

```text
DANGLING_REFERENCE
EXPERIMENT_ARM_DISCLOSURE
DUPLICATE_CARRIER
```

## 9.4 Expected graph

정본은 typed policy DSL이다.

```text
DECISION_BASIS_POLICY
+
carrier registry
+
rendering contract
```

Semantic Compiler는 정본을 생성하는 주체가 아니라, 렌더된 자연어가 정본 의미를 보존했는지 확인하는 독립 drift auditor다.

```text
Policy DSL
    ↓
Deterministic Renderer
    ↓
Rendered Prompt
    ↓
Independent Semantic Compiler
    ↓
Observed Policy Graph
    ↓
Expected Policy Graph와 비교
```

## 9.5 assurance ceiling

Compiler 결과의 최고 assurance는:

```text
SEMANTIC_REVIEWED
```

이다.

`RULE_CHECKED`나 `REASONER_PROVED`로 승격하지 않는다.

Rule Engine이 semantic graph 위에서 결정적으로 계산하더라도 전체 결론의 assurance는 입력 graph의 assurance를 넘을 수 없다.

[
A_{\text{final}}
================

\min(A_{\text{semantic graph}},A_{\text{rule result}})
]

## 9.6 compiler capability gate

compiler의 침묵을 `absent_verified`로 읽기 전에 다음 fixture family를 통과해야 한다.

```text
직접 금지문
의역된 금지문
조건부 금지문
예외가 있는 금지문
이중 부정
dangling reference
문장 간 scope 결합
필드 범위 축소
가까운 비정책 문장
```

각 target-critical policy family에 대해 positive와 negative fixture가 모두 있어야 한다.

탐지 능력이 입증되지 않은 항목은:

```text
unknown
```

으로 반환한다.

---

# 10. 새 구조 단언

freeze 전에 다음을 모두 검사한다.

```text
1. 모든 지시 표현의 referent가 각 arm에서 해소된다.
2. REMOVED에는 존재하지 않는 clause를 가리키는 참조가 없다.
3. 모델 대면 프롬프트에 arm, condition, treatment 등 실험 메타언어가 없다.
4. presentation-order와 source-priority는 별도 policy ID다.
5. 공통 Q7은 source-priority를 금지하지 않는다.
6. evidence text와 recorded fields의 역할이 분리되어 있다.
7. REMOVED에서 source_kind field가 허용된 경로에 포함된다.
8. KEPT에서 Q1이 동일 경로를 차단한다.
9. conflict는 select 또는 defer로 직접 매핑되지 않는다.
10. qualification select/defer controls가 모두 통과한다.
11. expected policy graph와 compiled policy graph가 일치한다.
12. target-critical policy family에 unknown이 없다.
13. 모든 semantic reviewer가 scope-specific capability gate를 통과한다.
14. 모든 reviewer가 freeze를 승인한다.
```

---

# 11. 최종 공통 렌더링

수정 후 관련 공통 블록은 다음과 같아야 한다.

```text
Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. The fact that this prompt does not prohibit
a decision basis is not itself a reason to select a type. A permitted basis
may affect the decision only through its application to the supplied evidence
items, including their recorded fields. The evidence-reading rule above
determines what ontology type an item's text supports; it does not by itself
prohibit evaluating the item's other recorded fields as source information.

Evidence may support different allowed types for the same concept/feature pair.
Your output should record whether, using only the packet, you judge the packet
to warrant selecting exactly one allowed type.

- After applying only the decision bases permitted by this prompt, choose
  select_type if exactly one allowed type is warranted.
- Choose defer if, after applying those permitted decision bases, neither
  allowed type is uniquely warranted.
- The presence of conflicting evidence does not by itself require either
  selection or deferral.
- Do not break ties using evidence item count or the order in which evidence
  items appear in the packet, unless the packet explicitly authorizes that
  basis.
- Do not use outside domain or ontology knowledge to supply facts about the
  concept-feature relation, and do not consult external sources.
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources.
```

KEPT에만 기존 Q1 절을 기존 위치와 바이트 그대로 삽입한다.

---

# 12. 데이터 및 실행 명령

```yaml
original_cohort:
  trials: 40
  status: completed_nonidentifying
  preserve: true

repaired_cohort:
  trials: 0
  status: not_frozen

execution:
  run_before_new_review: forbidden
  run_before_semantic_audit: forbidden
  rerun_both_arms: required
  pool_with_original: false
```

Q13 변경 후 기존 독립 리뷰 결과는 더 이상 freeze 승인으로 재사용하지 않는다. 표면이 변경되므로 전체 리뷰를 다시 실행한다.

---

# 13. 최종 명령

```yaml
D-H1a-13:
  Q13:
    decision: C
    remove_dangling_second_clause: true
    remove_experiment_arm_language: true

  Q13_1:
    source_order_policy:
      replace_with: evidence_item_presentation_order
    narrow_rendering: required

  Q13_2:
    evidence_scope:
      include_recorded_fields: true
      preserve_text_type_support_rule: true
      separate_text_support_from_source_evaluation: true

  Q13_3:
    independent_qualification_gate: required
    restore_old_anchor_cells: false
    same_modal_behavior_rule: withdrawn
    qualification_failure_not_null_effect: true

  Q13_4:
    register_L8: true
    add_source_metadata_to_fixture: false
    change_Q1_bytes: false

  Q13_5:
    reviewer_approval_is_not_absent_verified: true
    reviewer_capability_check: required
    target_critical_unknown_allowed: false

  Q13_6:
    bounded_semantic_compiler: required
    expected_graph_comparison: required
    compiler_assurance_ceiling: SEMANTIC_REVIEWED
    general_purpose_semantic_compiler: not_required

  freeze:
    status: blocked
    reopen_after:
      - prescribed sentence repair
      - policy schema update
      - qualification gate pass
      - semantic compiler capability pass
      - expected/observed graph match
      - independent review rerun
      - unanimous freeze approval
```
