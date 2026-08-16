# 설계 판정 요청 — 정본 정책 객체의 커버리지 공백 (Q16)

- 작성: 2026-08-16
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다.
- 계기: D-H1a-13 Q13.5/Q13.6이 명령한 독립 의미 리뷰를 **실제로 실행**했고,
  자격을 통과한 리뷰어 2명(R2·R4)이 **정본 정책 객체 자체의 구조적 공백**을
  독립적으로 지적했다. 운영 세션이 고칠 수 있는 사안이 아니다.
- 선행 판정: D-H1a-13(Q13.3~13.6), D-H1a-14/15(qualification gate 재설계)
- 실행된 trial: confirmatory 코호트 **0건** 유지
- 이 문서가 묻는 것: **Q16 하나** (하위 질문 Q16.1~16.3)

---

## 0. 한 줄 요약

Q13.5는 **target-critical policy family에 `unknown`을 허용하지 않는다**고
명령했다. 그런데 그 목록의 **6개 중 3개가 정본 typed policy DSL에 대응 항목이
없어**, Q13.6이 명령한 semantic compiler로는 **구조적으로 반증 불가능**하다.
현재는 리뷰어의 육안 독해로만 해소된다. 이 상태를 승인할지, 정본을 확장할지,
target-critical 정의를 조정할지를 묻는다.

---

## 1. 배경 — 무엇이 실행됐는가

D-H1a-13 §9(Q13.6)의 지시대로 독립 semantic compiler를 구현했다. 판정문이
정한 권위 방향:

> Policy DSL → Deterministic Renderer → Rendered Prompt → **Independent
> Semantic Compiler** → Observed Policy Graph → Expected Policy Graph와 비교
>
> Semantic Compiler는 정본을 생성하는 주체가 아니라, 렌더된 자연어가 정본
> 의미를 보존했는지 확인하는 **독립 drift auditor**다.

정본은 `_h1a_policy.py`의 `DECISION_BASIS_POLICY`(typed policy DSL) +
carrier registry + rendering contract다. Expected graph는 여기서 파생된다.

§9.6이 명령한 capability gate도 구현했다 — 탐지 능력이 입증되지 않은 family의
침묵은 `absent_verified`가 아니라 `unknown`을 반환한다.

Q13.5의 독립 리뷰도 **실제로 실행했다**: 범위를 선언한 리뷰어 5명이 blinded
mutation pack으로 자격을 검증받고(6/6 탐지, 오탐 0), 자격 통과자만 실물
아티팩트를 판정했다. 전원 승인, blocker·major 0건.

**그 리뷰에서 아래 공백이 나왔다.**

---

## 2. 실측 — 커버리지 공백

### 2.1 Q13.5가 정한 target-critical 목록

판정문 §8 원문:

> 다음 policy family에는 `unknown`을 허용하지 않는다.
> ```
> source_meta_reasoning prohibition
> outside-domain prohibition scope
> presentation-order prohibition
> conflict-to-defer mapping
> recorded-field access
> default permission applicability
> referential integrity
> ```
> 각 항목은 다음 둘 중 하나여야 한다: `present` / `absent_verified`

### 2.2 정본 DSL이 실제로 담고 있는 것

`DECISION_BASIS_POLICY`의 axis는 **5개뿐**이다(실측, 전문):

```python
AXES = (
    "evidence_count",
    "evidence_item_presentation_order",
    "outside_domain_knowledge",
    "external_source_retrieval",
    "source_meta_reasoning",
)
```

각 axis는 arm별로 `{state, carrier}`를 갖는다. 예:

```python
"source_meta_reasoning": {
    "kept":    {"state": EXPLICITLY_FORBIDDEN, "carrier": CARRIER_Q1},
    "removed": {"state": ALLOWED_BY_DEFAULT,   "carrier": CARRIER_DEFAULT},
},
```

### 2.3 대응 실측

| Q13.5 target-critical 항목 | 정본 DSL 대응 axis | 기대 상태 도출 |
|---|---|---|
| source_meta_reasoning prohibition | `source_meta_reasoning` | ✅ 가능 |
| outside-domain prohibition scope | `outside_domain_knowledge` | ✅ 가능 |
| presentation-order prohibition | `evidence_item_presentation_order` | ✅ 가능 |
| **conflict-to-defer mapping** | **없음** | ❌ **불가** |
| **recorded-field access** | **없음** | ❌ **불가** |
| **default permission applicability** | **없음**(carrier이지 axis 아님) | ❌ **불가** |
| referential integrity | 해당 없음(구조 항목) | 구조 검사로 처리 |

**target-critical 6개 policy family 중 3개가 정본에 기대값이 없다.**
compiler의 expected graph에서 이들은 `expected_state: null`로 나오고, 비교
단계는 `no_expected_counterpart`를 낼 뿐 **일치/불일치를 판정할 수 없다.**

### 2.4 왜 이것이 심각한가 — 리뷰어 R2의 지적

> "The expected_policy_graph makes GLOBAL_DEFAULT_PERMISSION the **SOLE
> carrier** of the removed arm's target-critical SOURCE_META_REASONING_PROHIBITION
> = absent_verified. The compiler therefore **declines to adjudicate the exact
> clause on which the target-critical absent_verified claim rests.** On
> compiler_diff alone that claim would be unsupported."

즉 REMOVED arm에서 표적 축이 "검증된 부재"라는 주장은 **default permission
절이 그 부재를 적극 담보한다**는 사실에 의존하는데, 바로 그 절이 정본에
기대값이 없어 compiler가 판정을 보류한다. R2가 육안 독해로 메웠다.

리뷰어 R4의 같은 취지 지적:

> "The canonical DSL declares my scope's three target-critical families
> without any expected state to check against, so they are **unfalsifiable by
> the compiler by construction** and can only be resolved by reviewer reading.
> That is a graph-side limitation, not a compiler error."

### 2.5 부수 실측 — 반대 방향 공백

`external_source_retrieval` axis는 정본에 있으나 **compiler family가 없다**.
현재는 `outside_domain_knowledge`와 carrier를 공유해 한 detector가 둘을
동시에 덮는다 — 등가가 아니라 감사 해상도의 한계다.

---

## 3. 운영 세션이 이미 해소한 것 (판정 대상 아님, 상태 보고)

리뷰어 지적 중 **구현으로 해소 가능했던 것은 전부 고쳤다**:

| 지적 | 조치 |
|---|---|
| 미입증 detector가 `agreed`에 계상돼 커버리지 과대 표시(R1·R2·R4·R5 독립 지적) | `agreed`(입증됨)와 `agreed_by_unproven_detector` 분리 |
| 조건부 carve-out("unless the packet explicitly authorizes that basis")이 상태를 payload 의존으로 만드는데 평면 `present`로 보고(R3) | claim에 `conditional`·`condition` 추가, audit이 `CONDITIONAL_STATE` finding 발행 |
| conflict→defer 하드 매핑 부재는 필요조건이지 충분조건 아님 — 분기 상보성 검사 수단 없음(R5) | `DECISION_BRANCH_PARTITION` 구조 검사 신설. 리터럴 상보 여부만 판정하고, 아니면 **리뷰어에게 라우팅**(의미 판단을 참칭하지 않음) |

**§2의 공백만 남았고, 그것은 정본의 범위 문제라 운영 세션이 정할 수 없다.**

---

## 4. Q16 — 선택지

### Q16 (본질) — target-critical인데 정본에 기대값이 없는 3개를 어떻게 할 것인가

| 안 | 내용 | 위험/근거 |
|---|---|---|
| **A** | **정본 DSL을 확장**해 template-level 규칙(conflict-to-defer mapping, recorded-field access, default-permission applicability)을 axis 또는 새 범주로 편입 | 정본이 커지고 `h1a_common_policy_block_v2.json` golden contract 재동결이 필요할 수 있다. 다만 "정본이 표적 축 부재를 담보하는 절을 담지 않는다"는 현 상태가 더 위험할 수 있다 |
| **B** | **리뷰어 독해를 정식 adjudication 경로로 승인**하고, 이 3개는 compiler 검증 대상이 아님을 명문화 | 구현 변경 없음. 그러나 Q13.5의 "target-critical에 unknown 불허"가 **사람의 육안에 의존**하게 되고, 이 실험이 F6·D-H1a-10에서 배운 "해석 조건은 조용히 변질된다"와 충돌할 소지 |
| **C** | **target-critical 목록을 조정** — 정본으로 반증 가능한 것만 target-critical로 두고 나머지는 별도 등급 | Q13.5 §8 목록의 개정. 목록 자체가 판정문 명령이라 새 판정 필요 |
| **D** | **정본을 확장하되 최소로** — `default permission applicability`만 편입(표적 축 부재를 담보하는 유일 carrier이므로), 나머지 2개는 B안 처리 | A와 B의 절충. "무엇이 표적 식별에 load-bearing한가"를 기준으로 가름 |
| **E** | 그 밖 |

**Q16.1**: `external_source_retrieval`(정본에 있으나 전용 compiler family 없음,
`outside_domain_knowledge`와 detector 공유)을 별도 family로 분리해야 하는가,
아니면 carrier 공유를 근거로 통합 감사를 승인하는가?

**Q16.2**: **조건부 규칙의 상태를 어떻게 정의하는가.** 현재 정본은 axis별로
`{state, carrier}`만 갖고 조건(`unless ...`)을 표현하지 못한다. 렌더된 문장은
"unless the packet explicitly authorizes that basis"라는 예외를 달고 있어
실효 상태가 payload 의존이다. 정본에 조건을 표현할 자리를 만들 것인가, 아니면
"예외 antecedent가 발동하지 않음"을 코호트 동결 조건으로 별도 검증할 것인가?

**Q16.3**: **리뷰어 독해의 assurance 등급.** §9.5는 compiler 산출의 상한을
`SEMANTIC_REVIEWED`로 정했다. 리뷰어가 육안으로 해소한 상태(§2.4의 3개)는
어떤 등급인가 — 같은 `SEMANTIC_REVIEWED`인가, 더 낮은가, 아니면 기계 검증이
없으므로 별도 표기가 필요한가?

---

## 5. 넘을 수 없는 제약

1. 정본은 typed policy DSL이다 — compiler는 정본을 생성하지 않는다(§9.4)
2. compiler는 `_h1a_policy`를 import하지 않는다(독립성, AST 테스트로 강제)
3. §9.6 fail-closed: 탐지 능력 미입증 시 `unknown`, `absent_verified` 아님
4. §9.5 assurance 상한 `SEMANTIC_REVIEWED`, 승격 금지
5. confirmatory trial 0건 — 재동결 비용 없음
6. D-H1a-14/15 거버넌스 규칙: `freeze_blocker` ↔ `diagnostic` 이동은 외부
   판정 전 실행 금지
7. `INDEPENDENT_SEMANTIC_REVIEW_PASSED`는 현재 `False` — 리뷰는 통과했으나
   플래그는 사람이 설정하며 아직 설정하지 않았다

## 6. 회신 형식

```text
DESIGN DECISION — H1a canonical policy coverage
decided_by:
date:

Q16 (정본에 기대값 없는 target-critical 3개):   <A|B|C|D|E>   근거:
  Q16.1 external_source_retrieval 분리 여부:
  Q16.2 조건부 규칙의 상태 표현:
  Q16.3 리뷰어 독해의 assurance 등급:

deferred:
  <항목 ID>: <사유 / 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약>

INDEPENDENT_SEMANTIC_REVIEW_PASSED 설정 가부:
  <이 공백이 해소되기 전에 설정해도 되는가 / 안 되는가>   사유:

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```
