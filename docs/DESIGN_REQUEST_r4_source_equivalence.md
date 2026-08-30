# DESIGN REQUEST — R4는 같은 **기제**를 요구하는가, 같은 **measurand의 동등한 qualification**을 요구하는가 (Q37)

- 발신: 2026-08-30, 운영 세션 · 수신: 외부 설계 담당
- 판정자 전제: **저장소 접근 없음.** 자기완결적이다 — 인용·수치·우리 판단을
  전부 본문에 싣는다.
- 성격: **D-36 §2가 명시적으로 열어 둔 질문 하나만** 묻는다. D-36은 R1~R4를
  "완전한 요건 목록"으로 확정하지 말라고 하면서 **R4를 특히 지목**했다.
  그 지목을 그대로 받아 상신한다.
- 범위를 좁혔다. D-36 §6·§7이 만든 다른 질문(두 번째 corpus·사람 판정이 R2
  후보가 되는가)은 **이 상신에 싣지 않는다** — 이 판정 결과를 보고 필요하면
  별건으로 낸다. 한 번에 하나만 묻는다.
- 여전히 경계를 제안하지 않는다 — `operational_patch: forbidden` ·
  `immediate_projection: forbidden` 준수. 코호트 dispatch 누계 **0건**.

## 1. 판정문이 열어 둔 문장 (원문)

D-36 §2 "하지만 R1~R4를 '완전한 요건 목록'으로 확정하면 안 된다":

> 특히 R4는 흥미롭다.
>
> PMB와 FOLIO가 반드시 같은 annotation mechanism을 가져야 하는지, 아니면
> **동일한 measurand에 대해 의미적으로 동등한 qualification을 제공하면
> 되는지**가 아직 결정되지 않았다.

우리가 R4를 도출할 때 쓴 문구는 `R4 = source 간 동일 기준`이었다. 판정문은
그것이 **두 가지로 읽힌다**고 지적한 것이다. 우리는 그 두 읽기를 구분하지
않았고, 구분하지 않은 채로 후보를 걸렀다.

## 2. 두 읽기가 서로 다른 것을 요구한다

```text
읽기 A — 기제 동일성
  두 source 가 같은 annotation mechanism 을 써야 한다
  (같은 규약·같은 주석 절차·같은 산출 형식)

읽기 B — measurand 동등성
  두 source 가 형식이 달라도 무방하다.
  같은 measurand 를 재고, 그 qualification 이 의미적으로 동등하면 된다
```

읽기 A 아래에서 **서로 다른 형식을 쓰는 두 corpus 는 원리적으로 짝이 될 수
없다.** 읽기 B 아래에서는 형식 차이가 무관해지고, 대신 **"같은 measurand 를
재는가"** 라는 별도 입증 부담이 생긴다.

## 3. 이것이 우리에게 결정적인 이유 — 우리 쌍은 형식이 다르다

우리가 가진 두 재료의 형식은 다르다.

| | PMB | FOLIO |
|---|---|---|
| 산출 형식 | SBN(box notation) — DRS 계열 | 일차 술어 논리식 |
| 주석 단위 | 노드·간선·role 어휘(우리 실측 200종) | 상수·술어·양화사 |
| 우리 보유 | 규약 사양 `sbn_spec.py` **전사만**, 원천 없음 | 공개 데이터셋 |

읽기 A 라면 이 쌍은 **더 볼 것 없이 R4 실패**다. 읽기 B 라면 형식 차이는
장애가 아니고 질문이 "둘이 같은 measurand 를 재는가" 로 옮겨간다.

## 4. 그런데 읽기 B 로 가면 선행 판정과 정면으로 만난다

D-34 는 우리가 FOLIO 규약을 semantic authority 로 쓰려 한 것을 기각하면서
이렇게 판정했다(원문):

> **PMB와 FOLIO는 동일하거나 유사한 participant-like material에 대해 서로 다른
> formal representations를 사용할 수 있으며, FOLIO의 constant 사용 자체는
> referentiality의 충분한 증거가 아니다.**

그리고:

```text
FOLIO constant  ≠  referential expression
```

기각의 이유는 형식이 달라서가 아니라 **`representation → semantic class` 다리가
없어서**였다. D-34 의 표현으로는 "corpus 규약을 semantic authority 로 승격"하는
것이었다.

**우리 읽기(판정 요청 대상)**: D-34 의 그 문장은 이미 읽기 B 의 질문에 대한
부정 답변이다 — FOLIO 는 referentiality 라는 measurand 를 qualify 하지 **않고**,
그것과 상관될 수 있는 다른 것을 표기한다. 그렇다면 이 쌍은 **읽기 A 로도
읽기 B 로도 R4 를 통과하지 못한다.** 다만 실패의 의미가 다르다:

- 읽기 A 의 실패는 **형식이 달라서** — 이 쌍만의 문제이고 다른 쌍은 가능하다
- 읽기 B 의 실패는 **measurand 가 달라서** — 대체 source 가 무엇을 갖춰야
  하는지를 알려 준다

## 5. 그래서 이 질문의 실제 값은 PMB/FOLIO 쌍이 아니다

이 쌍은 어느 쪽이든 떨어진다. **값은 다음 source 를 찾을 때의 수락 기준에
있다.** 읽기 A 가 옳으면 우리는 "PMB 와 같은 기제를 쓰는 두 번째 corpus" 를
찾아야 하고, 읽기 B 가 옳으면 "형식은 무엇이든 referentiality 를 직접 qualify
하는 source" 를 찾아야 한다. **찾는 대상이 완전히 다르다.**

지금 우리는 어느 쪽을 찾아야 하는지 모르는 채로 재료를 뒤지고 있다.

## 6. 묻는 것

- **(a) R4 의 올바른 읽기는 A 인가 B 인가, 아니면 둘 다 아닌가?** D-36 §2 가
  "아직 결정되지 않았다"고 한 그 결정을 청한다.
- **(b) 읽기 B 라면, "의미적으로 동등한 qualification" 의 동등성은 무엇으로
  입증하는가?** 우리가 아는 수단은 두 source 의 산출을 대조하는 것뿐인데,
  그 대조 자체가 "무엇이 같음인가" 를 이미 전제한다. 이것이 D-36 §4 가 나눈
  삼층(L1 encoding / L2 correctness / L3 qualification) 중 어디에 속하는가?
- **(c) §4 의 우리 읽기가 맞는가?** 즉 D-34 의 판정이 이미 "FOLIO 는 같은
  measurand 를 qualify 하지 않는다" 를 함의하는가, 아니면 D-34 는 다른 것을
  말했고 우리가 R4 질문에 끌어다 쓴 것인가.
- **(d) R4 가 어느 읽기든, 그것이 R2 와 독립인가?** R4 를 만족하는 쌍이
  R2(독립 검증 가능성)를 자동으로 채우지 않는다는 것이 D-36 §6 의 판정이라고
  이해하는데, 그렇다면 R4 를 먼저 푸는 것이 순서상 의미가 있는가.

**운영 세션은 어느 것도 권고하지 않는다.** (a)가 축이다.

## 7. 한계 — 이 문서가 확신하지 못하는 것

- **읽기 A/B 의 이분법은 우리가 만든 것이다.** 판정문은 두 가능성을 문장으로
  적었을 뿐 이분법이라고 하지 않았다. 세 번째 읽기가 있을 수 있다.
- **§4 의 연결은 우리 판단이다.** D-34 는 R4 를 논하지 않았다 — R4 는 D-36 에서
  나온 어휘다. 우리가 두 판정을 잇는 것이 정당한지가 (c) 의 내용이다.
- **PMB 측 사실에 공백이 있다.** 규약 사양 `sbn_spec.py` 의 **원천을 갖고 있지
  않고 전사만 갖고 있다**(D-36 §5 가 이를 다뤘다). 주석자 간 일치도(IAA)
  공표 여부도 여전히 모른다 — 찾지 않은 것이지 없다고 확인한 것이 아니다.
- **role 어휘 200종 중 우리가 검토한 것은 `Name`·`ANA` 둘이다.** 미검토가
  198종이고 그중 `EQU` 만 12,501건이다. 그 안에 §4 의 판단을 뒤집는 것이
  있을 수 있다.
- **전수 재실측이 현재 불가능하다.** 우리가 보유하던 PMB 문서 12,053건이
  세션 간 임시 저장소 정리로 소실됐다(2026-08-29 확인). 동결된 in-N 재료와
  캐시는 무사하므로 **이 문서의 인용·수치는 영향받지 않으나**, 판정이 새로운
  전수 실측을 요구하면 재취득이 선행돼야 한다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 이 질문을 만든 판정 [[DESIGN_DECISION_independent_verifiability_constraint|D-36]] §2
- §4 가 인용한 판정 [[DESIGN_DECISION_referential_existential_qualification|D-34]]
- 선행 [[DESIGN_DECISION_annotation_layer_admissibility|D-35]] · [[DESIGN_DECISION_referential_participant_quantification|D-33]]
- 직전 상신 [[DESIGN_REQUEST_independent_verifiability_constraint|Q36]]
- 고리 그림 [[README_referential_circularity]] (Z0→Z2)
