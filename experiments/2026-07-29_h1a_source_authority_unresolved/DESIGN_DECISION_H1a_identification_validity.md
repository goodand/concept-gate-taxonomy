# 설계 결정 (동결) — H1a 표적 기제의 식별 타당성 (D-H1a-12)

- 결정일: 2026-08-05
- 결정 주체: 실험 설계 권한 (외부), 사용자 경유 전달
- 상태: **동결.** 이 문서는 결정 기록이다. 결과가 이 결정을 소급 수정하지
  못한다. 변경이 필요하면 새 amendment 문서로 남긴다.
- 요청 문서: [`correspondence/DESIGN_REQUEST_H1a_identification_validity.md`](correspondence/DESIGN_REQUEST_H1a_identification_validity.md)
  (Q12 / Q12.1 / Q12.2 / Q12.3 / Q12.4 + M7 / M8 / M4)
- 실행된 trial: 수선 코호트 **0건**. 이 판정은 **실행 전** 판정이다.
  최초 코호트 40건은 `completed_nonidentifying`으로 동결 보존
  (D-H1a-10 Q10.1, 해시는 `COHORT_STATUS_20260803_nonidentifying.md`).
- **선행 판정 개정**: 이 판정의 §3이 **D-H1a-10 §5를 개정**한다
  (`DESIGN_DECISION_H1a_residual_prohibition.md`). D-H1a-10의 나머지 조항과
  D-H1a-1~9, D-H1a-11은 구속력을 유지한다.
- 상태: **`FREEZE_BLOCKED` 유지.** 해제 조건 12개는 §16.

> **브랜치 주의 (배치상 사실, 판정과 무관)**
> 이 파일은 세션 격리 때문에 `codex/entailed-is-a-contract` 브랜치에서
> 저장됐다. 이 브랜치에는 인용 대상 `DESIGN_DECISION_H1a_allowed_rendering.md`
> (D-H1a-11)와 `PREREGISTRATION_REPAIRED_COHORT.md`가 없다 — h1 브랜치
> (`codex/h1-source-authority`)에만 있다. 이 커밋을 그 브랜치로
> **cherry-pick**해야 문서가 자기 이웃을 가리킨다. 손으로 복사하지 말 것
> (`CLAUDE.md` Project Structure).

**이하 본문은 수령한 판정문 전문이다. 운영 세션이 편집하지 않았다.**

---

# 설계 판정 — H1a 표적 기제의 식별 타당성

## 판정 식별자

**D-H1a-12**

| 질문    | 판정                                                   |
| ----- | ---------------------------------------------------- |
| Q12   | **F — `outside knowledge`를 두 정책 범주로 분리하고 H1a를 계속한다** |
| Q12.1 | **기존 불릿을 비방향적 결정 규칙으로 교체한다**                         |
| Q12.2 | **중립화 문장을 재문안한다**                                    |
| Q12.3 | **§10의 의미 검사를 우선하고 §5 문구를 재작성한다**                    |
| Q12.4 | **독립 golden contract를 도입해 assertion 9를 유효하게 만든다**    |
| M7    | 별도 한계 등록, freeze blocker 아님                          |
| M8    | 경로·매개효과 한계 등록, H1a outcome 대비의 blocker는 아님           |
| M4    | 기존 Q4에 의해 자동 복구 의무 발생, freeze blocker                |

---

## 1. 근거 상태

| 결론                                                 |                       상태 | source type                    |
| -------------------------------------------------- | -----------------------: | ------------------------------ |
| 현재 정책 블록은 양 arm에서 동일함                              |                supported | prompt-given                   |
| KEPT에만 Q1 절이 존재함                                   |                supported | prompt-given                   |
| payload에는 source priority를 직접 정하는 날짜·경로·커밋 정보가 없음  |                supported | prompt-given                   |
| evidence text는 source priority를 직접 진술하지 않음         |                supported | prompt-given                   |
| 현재 `outside knowledge` 금지 아래에서는 표적 경로가 양 arm에서 봉쇄됨 |                supported | prompt-given + model inference |
| 실제 저장소 바이트·테스트·커밋 상태                               |  `insufficient_evidence` | repo-grounded                  |
| 수선 코호트 결과                                          | `out_of_scope` — 0 trial | experiment-grounded            |

요청서에 embed된 측정이 실제 저장소 산출물과 일치한다는 조건 아래, 현재 설계의 표적 대비는 다음과 같다.

```text
KEPT    target mechanism allowed = false
REMOVED target mechanism allowed = false
```

따라서 현재 상태에서 trial을 실행해서는 안 된다.

---

## 2. Q12 판정

### F — `outside knowledge`를 두 정책 범주로 분리한다

현재 문제는 `outside knowledge`가 서로 다른 두 종류의 추론을 하나로 묶는 데서 발생했다.

#### 범주 1 — 외부 도메인 지식

```text
outside_domain_knowledge
```

예:

* 철이 본질 속성인가
* material-of가 essential_feature인가
* 일반 존재론에서 재료 관계가 어떻게 분류되는가
* 외부 문헌이나 ontology가 어떤 type을 지지하는가

이 범주는 **양 arm에서 계속 금지한다.**

#### 범주 2 — 출처 메타판단

```text
source_meta_reasoning
```

예:

* doc와 code 중 어느 쪽이 현재 구현을 더 잘 반영하는가
* source_kind가 판단에 어떤 의미를 갖는가
* recency, authority, liveness를 어떻게 평가하는가

이 범주는 **Q1 절만이 통제한다.**

| arm                 | source_meta_reasoning |
| ------------------- | --------------------: |
| PROHIBITION_KEPT    |      Q1에 의해 forbidden |
| PROHIBITION_REMOVED |   기본허용 규칙에 의해 allowed |

이 구분을 적용하면 형식 상태는 다음과 같이 바뀐다.

```text
Current:
  KEPT    = blocked
  REMOVED = blocked
  contrast = false

Typed-scope repair:
  KEPT    = blocked
  REMOVED = allowed
  contrast = true
```

연역 검사에서도 typed-scope repair 후에만 arm 간 표적 경로 대비가 성립했다.

---

## 3. D-H1a-10 §5의 개정 범위

D-H1a-10 §5의 다음 판단은 그대로 유지할 수 없다.

> outside knowledge는 조작과 무관하므로 양 arm에서 금지한다.

이 문장은 범위가 지나치게 넓었다. 다음으로 대체한다.

> 외부 도메인·존재론 지식은 조작과 무관하므로 양 arm에서 금지한다.
> 제공된 evidence item을 출처로서 평가하는 source-meta reasoning은 H1a의 직접적인 조작 대상이므로 Q1 절만이 통제한다.

이는 `outside knowledge` 금지를 전부 제거하는 Q12-B가 아니다.

```text
금지 유지:
  outside domain facts
  outside ontology facts
  external retrieval

Q1에 이관:
  source_kind evaluation
  recency evaluation
  authority evaluation
  liveness evaluation
```

따라서 일반 ontology 지식을 이용한 type 판정은 계속 봉쇄된다.

---

## 4. 공통 프롬프트 문구

공통 Q7을 하나의 불릿으로 유지하지 않는다. 서로 다른 정책을 별도 문장으로 분리한다.

### 공통 비표적 tie-breaker 규칙

```text
- Do not break ties using evidence item count or source order unless the
  packet explicitly authorizes that basis.
```

### 공통 도메인 지식 제한

```text
- Do not use outside domain or ontology knowledge to supply facts about the
  concept-feature relation, and do not consult external sources.
```

### 공통 범위 구분

```text
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources. Source
  evaluation is governed by the arm-specific source-evaluation clause.
```

이 세 번째 문장은 양 arm에서 byte-identical해야 한다.

그 결과:

* KEPT에서는 Q1이 source evaluation을 명시적으로 금지한다.
* REMOVED에서는 Q1이 없으므로 공통 기본허용 규칙이 적용된다.
* 일반 ontology 지식은 양 arm에서 계속 금지된다.
* REMOVED에만 target axis를 열거한 긍정 허용문을 넣지 않는다.

---

## 5. 정책 계약 개정

```yaml
policy_defaults:
  packet_internal_basis:
    state: allowed
    carrier: GLOBAL_DEFAULT_PERMISSION

decision_basis_policy:
  evidence_count:
    kept:
      state: forbidden
      carrier: Q7_NON_TARGET_TIEBREAKER
    removed:
      state: forbidden
      carrier: Q7_NON_TARGET_TIEBREAKER

  source_order:
    kept:
      state: forbidden
      carrier: Q7_NON_TARGET_TIEBREAKER
    removed:
      state: forbidden
      carrier: Q7_NON_TARGET_TIEBREAKER

  outside_domain_knowledge:
    kept:
      state: forbidden
      carrier: DOMAIN_KNOWLEDGE_BOUNDARY
    removed:
      state: forbidden
      carrier: DOMAIN_KNOWLEDGE_BOUNDARY

  external_source_retrieval:
    kept:
      state: forbidden
      carrier: DOMAIN_KNOWLEDGE_BOUNDARY
    removed:
      state: forbidden
      carrier: DOMAIN_KNOWLEDGE_BOUNDARY

  source_meta_reasoning:
    kept:
      state: forbidden
      carrier: Q1_LIVENESS_CLAUSE
    removed:
      state: allowed_by_default
      carrier: GLOBAL_DEFAULT_PERMISSION
```

다음 네 축은 `source_meta_reasoning`의 하위 축으로 선언한다.

```yaml
source_meta_reasoning:
  subaxes:
    - source_kind_priority
    - recency
    - authority
    - liveness
```

이 구조에서는 `outside_domain_knowledge`와 `source_meta_reasoning`의 포섭 관계를 허용하지 않는다.

```text
source_meta_reasoning ⊄ outside_domain_knowledge
outside_domain_knowledge ⊄ source_meta_reasoning
```

둘은 형제 정책 범주다.

---

## 6. Q12.1 — 공통 defer 불릿

### 기존 문구는 제거한다

```text
Choose defer if the packet does not warrant selecting exactly one allowed
type, including cases where support is conflicting.
```

`including cases where support is conflicting`은 현재 fixture의 표면 형태를 defer와 직접 연결할 수 있다. Q3에서 제거한 hard mapping과 기능적으로 가까우므로 유지하지 않는다.

### 다음 비방향적 규칙으로 교체한다

```text
- After applying only the decision bases permitted by this prompt, choose
  select_type if exactly one allowed type is warranted.

- Choose defer if, after applying those permitted decision bases, neither
  allowed type is uniquely warranted.

- The presence of conflicting evidence does not by itself require either
  selection or deferral.
```

이 규칙은 conflict를 outcome으로 직접 매핑하지 않는다.

[
\text{conflict}
\not\Rightarrow
\text{defer}
]

[
\text{conflict}
\not\Rightarrow
\text{select}
]

결정은 허용된 근거를 적용한 뒤의 warrant 상태에 의해 정해진다.

---

## 7. Q12.2 — demand neutralizer

### 기존 문구

```text
Permission to consider a basis does not by itself warrant selecting a type
or favor either allowed type.
```

이 문장은 permission 자체와 permitted basis의 증거력을 혼동할 가능성이 있다.

### 교체 문구

```text
The fact that this prompt does not prohibit a decision basis is not itself
a reason to select a type. A permitted basis may affect the decision only
through its application to the supplied evidence.
```

첫 문장은 허용 상태 자체가 증거가 아님을 말한다.

두 번째 문장은 허용된 근거가 실제 evidence에 적용될 경우 warrant를 형성할 수 있음을 명시한다.

따라서 다음 두 명제가 함께 성립한다.

```text
permission status alone ≠ evidence
permitted basis applied to evidence = potentially relevant
```

---

## 8. Q12.3 — §5 문구와 assertion 12

### 판정

**§10의 의미 검사 목적을 우선한다.** 다만 문자열 금지 목록으로 구현하지 않는다.

기존 §5 문구의 다음 예외 조항은 제거한다.

```text
unless that priority is directly stated inside an evidence item's text
```

새 비표적 tie-breaker 규칙은 다음처럼 쓴다.

```text
unless the packet explicitly authorizes that basis
```

이로써 bare `priority` 충돌은 사라진다.

### assertion 12의 역할 변경

다음 검사를 인증 조건으로 사용하지 않는다.

```text
렌더 문자열에 priority, authority, liveness 등의 단어가 있는가
```

대신 다음을 검사한다.

```text
COMMON_Q7가 target-axis policy ID의 forbidden 상태를 생성하는가
```

허용되는 결과:

```text
COMMON_Q7:
  evidence_count -> forbidden
  source_order -> forbidden
  outside_domain_knowledge -> forbidden
```

금지되는 결과:

```text
COMMON_Q7:
  source_meta_reasoning -> forbidden
  source_kind_priority -> forbidden
  recency -> forbidden
  authority -> forbidden
  liveness -> forbidden
```

문자열 스캔은 semantic lint로 남길 수 있지만 certification gate가 되어서는 안 된다.

---

## 9. Q12.4 — assertion 9

### 선택: B

`render_policy_block()`이 비교 대상 상수를 직접 읽는 현재 구조에서 assertion 9는 독립된 검사가 아니다.

```text
producer source = GLOBAL_DEFAULT_PERMISSION_TEXT
assertion expected source = GLOBAL_DEFAULT_PERMISSION_TEXT
```

이는 자기동일성 검사다.

### 독립 golden contract 도입

정확한 공통 블록을 별도의 동결 artifact에 저장한다.

```yaml
artifact:
  name: h1a_common_policy_block_v2
  sha256: <frozen digest>
  source: repaired preregistration
```

테스트는 다음 순서로 수행한다.

```text
1. KEPT 전체 프롬프트 렌더
2. REMOVED 전체 프롬프트 렌더
3. 양쪽에서 common block 추출
4. 각 block이 정확히 1회 존재하는지 검사
5. 두 block이 byte-identical한지 검사
6. 각 block의 sha256이 frozen golden digest와 같은지 검사
```

비교 대상은 renderer 모듈의 상수가 아니라 독립된 동결 artifact다.

### 음성 테스트

다음 변형이 각각 실패해야 한다.

```text
공통 블록 삭제
공통 블록 중복
KEPT 한 글자 변경
REMOVED 한 글자 변경
양 arm을 동일하게 잘못 변경
```

마지막 사례가 중요하다. 양 arm이 서로 같더라도 golden digest와 다르면 실패해야 한다.

`KNOWN_UNPROVEN` 상태는 이 구현이 완료될 때까지만 허용한다. 영구 승인하지 않는다.

---

## 10. 표적 기제 가드의 새 명제

기존 `target_mechanism_contrast`는 target axis의 상태만 검사해 필요한 명제를 보장하지 못했다.

다음으로 교체한다.

```text
licensed_source_evaluation_path(arm)
```

필수 조건:

```text
1. model-visible evidence source attributes exist
2. source_meta_reasoning is allowed in the arm
3. source_meta_reasoning is not captured by outside_domain_knowledge
4. no common rule maps the fixture's conflict shape directly to defer
5. no other carrier prohibits source_meta_reasoning
```

형식화:

[
L(a)=
V
\land S(a)
\land \neg D_S
\land \neg H
\land \neg R(a)
]

여기서:

* (V): source attribute가 모델에게 보임
* (S(a)): 해당 arm에서 source-meta reasoning이 허용됨
* (D_S): domain-knowledge 금지가 source-meta reasoning까지 포섭함
* (H): conflict shape를 defer로 직접 매핑하는 공통 규칙
* (R(a)): 다른 잔여 금지

수선 후 기대값:

| 조건                          |  KEPT | REMOVED |
| --------------------------- | ----: | ------: |
| source attributes visible   |     1 |       1 |
| source-meta allowed         |     0 |       1 |
| domain ban이 source-meta를 포섭 |     0 |       0 |
| hard defer mapping          |     0 |       0 |
| residual prohibition        |     0 |       0 |
| **licensed path**           | **0** |   **1** |

freeze 조건:

```text
licensed_source_evaluation_path(KEPT) = false
licensed_source_evaluation_path(REMOVED) = true
```

---

## 11. A–E를 채택하지 않은 이유

### A — payload에 날짜·경로·커밋 추가

기각한다.

이는 source priority의 직접적인 모델 대면 anchor가 될 수 있고 Q3 및 oracle-leakage 통제와 충돌한다.

### B — outside knowledge 금지 전체 제거

기각한다.

도메인·ontology 지식까지 열어 type 판정의 원인이 통제되지 않는다.

### C — evidence text에 priority 진술 추가

기각한다.

이 경우 측정 대상이 background source evaluation에서 in-text instruction following으로 이동한다.

### D — 가설 재정의

기각한다.

현재 H1a를 유지할 수 있는 더 작은 정책 범주 수정이 존재한다.

### E — H1a 종료

현 단계에서는 기각한다.

표적 기제가 본질적으로 측정 불가능한 것이 아니라, 정책 범주가 잘못 합쳐져 있었기 때문이다. typed-scope repair로 대비를 복구할 수 있다.

---

## 12. M7 — mention-vs-prohibition 교란

### 판정

독립된 설계 blocker는 아니다. 별도 한계로 등록한다.

공통 문구에서 양 arm 모두 다음 범주를 언급한다.

```text
evaluation of supplied evidence items as sources
```

따라서 source evaluation이라는 상위 범주의 존재는 양 arm에 공통으로 노출된다.

다만 구체적인 네 축은 KEPT의 Q1 절에만 나타난다. 이는 완전히 제거되지 않는 표면 차이다.

### L6

```text
L6 — Mention/prohibition surface coupling

The KEPT arm explicitly names source liveness, priority, recency, and
authority, while the REMOVED arm omits the prohibitory clause. Therefore,
the manipulation combines policy-state change with an unavoidable difference
in the wording that names the prohibited bases.

The experiment estimates the effect of the frozen prohibition surface, not
a wording-free latent permission variable.
```

H1a의 estimand를 **프롬프트 표면 제거 효과**로 제한하면 허용 가능한 한계다.

---

## 13. M8 — 경로 정보 소실

### 판정

H1a의 select/defer 분포 대비에는 blocker가 아니다. 그러나 source-authority가 실제 내부 경로였다는 주장은 할 수 없다.

현재 `ev3`의 merit 논거와 source-meta 논거는 모두 `structural_composition` 선택으로 이어질 수 있다.

따라서 관측 가능한 것은 다음뿐이다.

```text
Q1 surface removal changed or did not change select/defer behavior
```

관측할 수 없는 것:

```text
the model selected specifically because it used authority/liveness reasoning
```

rationale이나 새 `decision_basis_used` 필드는 자기보고이므로 이를 인증하지 못한다.

### L7

```text
L7 — Path non-identification

The behavioral outcome identifies selection versus deferral but does not
identify whether a selection was reached through evidence-merit reasoning,
source-meta reasoning, or another permitted internal route.

Rationales may be inspected descriptively but are not treated as certified
mechanism reports.
```

내부 경로의 인과적 식별이 필요하다면 별도 교차 fixture가 필요하다.

```text
evidence merit direction × source-meta direction
```

이는 H1a 수선 코호트의 필수 변경이 아니라 후속 실험이다.

---

## 14. M4 — ceiling 장치

### 판정

별도 설계 선택이 필요하지 않다. 기존 Q4가 여전히 구속력을 가지므로 동등한 ceiling 장치를 복원해야 한다.

현재 배너가 기존 ceiling 문서를 무효화했고 대체물이 없다면 freeze blocker다.

필수 조치:

```text
1. 기존 Q4 ceiling 명제를 식별
2. repaired preregistration에 동일 명제를 재등록
3. 새 prompt surface 전체를 적용 대상으로 명시
4. golden artifact 또는 구조 검사에 배선
5. 독립 리뷰에서 실제 freeze boundary까지 확인
```

Q12가 해결되어도 M4는 자동으로 해소되지 않는다. 구현 완료가 필요하다.

---

## 15. 실행 및 데이터 처리

수선 코호트가 아직 0 trial이므로 폐기할 신규 데이터는 없다.

기존 40 trial:

```yaml
status: completed_nonidentifying
preserve: true
merge_with_repaired_cohort: false
reuse_arm: false
```

새 코호트:

```yaml
status: not_frozen
both_arms_rerun: required
post_result_amendment_disclosure: required
```

새 사전등록에는 다음을 명시한다.

```text
최초 코호트 결과를 확인한 뒤,
1. 공통 잔여 금지,
2. default permission의 범위,
3. outside knowledge의 범주 포섭,
4. conflict→defer 문구
가 순차적으로 발견되어 설계를 개정했다.
```

---

## 16. freeze 해제 조건

다음 조건을 모두 충족하기 전까지 `FREEZE_BLOCKED`를 유지한다.

```text
1. outside_domain_knowledge와 source_meta_reasoning 분리
2. 공통 Q7 재작성
3. defer 규칙 비방향화
4. demand neutralizer 재문안
5. semantic policy assertion 통과
6. golden common-block contract 통과
7. assertion 9 음성 테스트 통과
8. licensed-source-evaluation-path truth table 통과
9. M4 ceiling 복구
10. repaired preregistration 갱신
11. 독립 의미 리뷰 재실행
12. 리뷰어 전원 freeze 승인
```

---

## 17. 최종 명령

```yaml
D-H1a-12:
  Q12:
    decision: F_TYPED_SCOPE_SPLIT
    continue_H1a: true
    freeze_status: blocked

    policy_split:
      outside_domain_knowledge:
        kept: forbidden
        removed: forbidden

      source_meta_reasoning:
        kept: forbidden
        removed: allowed_by_default

  Q12_1:
    remove_conflict_to_defer_mapping: true
    use_post_permission_warrant_rule: true

  Q12_2:
    rewrite_demand_neutralizer: true

  Q12_3:
    rewrite_common_Q7: true
    semantic_policy_check_required: true
    lexical_alias_check:
      role: lint_only

  Q12_4:
    independent_golden_contract: required
    permanent_known_unproven: forbidden

  limitations:
    L6_mention_prohibition_coupling: required
    L7_path_non_identification: required

  M4:
    ceiling_restoration: required
    independent_new_decision: false
    freeze_blocker: true

  execution:
    repaired_trials_before_freeze: 0
    rerun_both_arms: true
    pool_with_original_cohort: false
```
