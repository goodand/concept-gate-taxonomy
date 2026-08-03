# 설계 판정 요청 — `removed: allowed`의 렌더링과 KEPT 금지의 담지자 (Q11)

- 작성: 2026-08-03
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 파일을 열지 않고 판정할 수 있게 썼다.
- 계기: **D-H1a-10(Q10=E) 반입 완료.** R1이 명령한 "공통 Q7 목록에서 표적 축
  4개 제거"를 구현하려 하자, 판정문이 **정하지 않은 것**이 하나 드러났다.
- 실행된 trial: **최초 코호트 40건**(`completed_nonidentifying`으로 동결 보존,
  Q10.1). **수선 코호트는 0건** — 이 요청서 시점에 아직 재동결하지 않았다.
  따라서 이 판정은 **실행 전** 판정이다.
- 선행 판정 6건(전부 구속력 유지, 재론하지 않음): `DESIGN_DECISION.md`
  (D-H1a-1~7) / `_manipulation_scope`(Q1=B, Q2=B) / `_prompt_surface`
  (Q3=B, Q4) / `_review_blockers`(Q5=B, Q6=A, Q7=E, Q8=B) /
  `_evidence_symmetry`(Q9=A, Q9.2) / **`_residual_prohibition`(D-H1a-10,
  Q10=E, R1·R2, Q10.1~10.3)**
- 이 문서가 묻는 것: **Q11 + Q11.1 + Q11.2.** 셋 다 R1을 구현하는 순간
  결정해야 하고, 셋 다 조작 표면의 크기·형태를 바꾼다. P7("고칠 대상을
  임의로 정하지 않는다")에 따라 운영 세션이 정하지 않았다.

---

## 0. 한 줄 요약

R1은 **무엇을 제거하는지**를 정확히 정했지만, 제거한 자리에 **무엇을 남기는지**
는 정하지 않았다. `decision_basis_policy`에서 표적 축이 REMOVED에서
`allowed`가 될 때, 그것이 프롬프트에 **명시적 허용 문장으로 렌더링되는지
침묵인지**가 미정이다. 그리고 그 선택에 따라 **KEPT 쪽 금지의 담지자**도
달라진다.

---

## 1. R1이 정한 것 (재론 대상 아님)

D-H1a-10-R1 원문의 정책 표:

| 판단 근거 | KEPT | REMOVED |
|---|---:|---:|
| evidence count | 금지 | 금지 |
| source order | 금지 | 금지 |
| outside knowledge | 금지 | 금지 |
| source_kind priority | Q1에 의해 금지 | **허용** |
| recency | Q1에 의해 금지 | **허용** |
| authority | Q1에 의해 금지 | **허용** |
| liveness | Q1에 의해 금지 | **허용** |

그리고 Q10.2가 요구한 정책 계약:

```yaml
decision_basis_policy:
  evidence_count:        {kept: forbidden, removed: forbidden}
  source_order:          {kept: forbidden, removed: forbidden}
  outside_knowledge:     {kept: forbidden, removed: forbidden}
  source_kind_priority:  {kept: forbidden, removed: allowed}
  recency:               {kept: forbidden, removed: allowed}
  authority:             {kept: forbidden, removed: allowed}
  liveness:              {kept: forbidden, removed: allowed}
```

> 그다음 프롬프트를 이 정책 객체에서 생성해야 한다.

**"생성해야 한다"까지는 구속력이 명확하다. `allowed`가 무엇을 생성하는지가
비어 있다.**

---

## 2. 현재 바이트 (실측, 수선 전)

### 2.1 양 arm 공통 — Q7 warrant rule의 tie-breaker 금지

`h1a_prompt_template.md` 46-52행, verbatim:

```text
- Choose select_type only if the packet warrants selecting one allowed type
  over the other. Cite the evidence item ids that support the selected type.
- Choose defer if the packet does not warrant selecting exactly one allowed
  type, including cases where support is conflicting, ambiguous, or insufficient.
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.
```

세 번째 불릿이 R1의 수선 대상이다.

### 2.2 KEPT에만 삽입되는 절 (Q1, Q5=B로 2문장)

`_h1a_contract.py::LIVENESS_CLAUSE_TEXT`, 실측 출력:

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

삽입 위치는 template의 유일한 packet-boundary 문장 `"...or external
sources."` 직후다.

### 2.3 현재 arm 간 차이 (실측)

```text
PROHIBITION_KEPT     rendered length = 2318
PROHIBITION_REMOVED  rendered length = 2235
delta                = 83 characters (= §2.2의 절, 공백 정규화 후)
```

(payload 치환 전 template 렌더 길이다. 차이 83은 §2.2의 절 하나뿐이며
`diff_is_restricted_to_the_liveness_clause`가 재구성으로 증명한다.)

### 2.4 R1 적용 후 공통 목록이 되는 것

표적 축 4개를 빼면 세 번째 불릿은 이렇게 된다(운영 세션의 최소 편집안, 판정
대상):

```text
- Do not break ties using evidence item count, source order, or outside
  knowledge unless that priority is directly stated inside an evidence item's
  text.
```

**여기까지는 R1이 결정한다. 아래부터가 미정이다.**

---

## 3. Q11 — `removed: allowed`는 무엇을 렌더링하는가

### 3.1 선택지 (우열 표시 없이 나열)

**A — 침묵.** `allowed`는 아무 문장도 내지 않는다. REMOVED 프롬프트는 표적 축에
대해 금지도 허용도 말하지 않는다. KEPT는 §2.2의 Q1 절을 받는다.

- arm 간 차이는 여전히 "Q1 절의 유무" 하나 → Q1=B·Q5=B의 조작 정의가 그대로 유지.
- 새로 저작하는 문장이 **없다.** 검토되지 않은 텍스트가 실험에 들어가지 않는다.
- **위험**: 지시 준수 맥락에서 **금지의 부재는 허용과 같지 않다.** 프롬프트는
  양 arm 모두에 "Use only the packet fields presented in this prompt. Do not
  use general ontology knowledge, ... or external sources."를 유지한다. 모델이
  `source_kind`를 근거로 쓰는 것을 그 문장 아래에서 기본적으로 범위 밖으로
  읽으면, REMOVED는 형식적으로 `M_allowed=1`이면서 행동적으로는 0에 가까울 수
  있다. **그러면 Q10이 방금 진단한 비식별이 더 미묘한 형태로 재발한다.**

**B — 명시적 허용.** `allowed`가 긍정 문장을 낸다. 예(문안 자체도 판정 대상):

```text
- If the packet's own evidence texts differ in source_kind, recency,
  authority, or liveness, you may take that difference into account when
  judging warrant.
```

- REMOVED의 표적 경로가 **관측 가능하게** 열린다. Q11의 위험 A가 제거된다.
- **위험**: 없던 문장이 생긴다. 긍정 허용문은 "그렇게 하는 것이 기대된다"는
  **요구 특성(demand characteristics)** 으로 읽혀 `select_type`을 인공적으로
  만들 수 있다. A의 거짓 null과 **반대 방향의 타당도 위협**이다.
- arm 간 차이가 "Q1 절 유무"에서 "Q1 금지문 ↔ 허용문 교체"로 바뀐다 —
  Q1=B·Q5=B 조작 정의의 실질 변경 여부를 판정자가 확인해야 한다.

**C — 양 arm 형식 대칭, 서술어만 반대.** 두 arm 모두 표적 축을 열거하는 문장을
받고, KEPT는 금지·REMOVED는 허용으로만 갈린다.

- "텍스트 존재 여부"라는 교란이 사라진다(길이·문장 수 대칭).
- **L2를 부분적으로 해소할 수 있다** — 현재 L2는 "조작이 언어 전환과 분리
  불가(영어 본문 + 한국어 2문장)"인데, 양쪽을 같은 언어로 저작하면 그 교란이
  사라진다. **다만 그러려면 Q1의 동결된 한국어 절을 영어로 재저작해야 하고,
  이는 Q1=B·Q5=B가 동결한 바이트의 변경이다.**
- **위험**: B의 요구 특성 위험을 그대로 가지며, 저작량이 가장 많다.

**D — 위 어느 것도 아님(판정자 제시).**

### 3.2 두 위험이 대칭이 아닐 수 있다는 점

운영 세션이 판정자에게 특히 확인받고 싶은 지점이다.

| 선택 | 실패 시 나타나는 결과 | 그 결과를 사후에 진단할 수 있는가 |
|---|---|---|
| A | 양 arm 다시 defer 쏠림 = **거짓 null** | **어렵다.** Q10과 같은 모양이라 "또 무언가가 막고 있었나"를 다시 뒤져야 한다 |
| B/C | REMOVED에서 select_type 급증 = **거짓 양성** | 상대적으로 낫다 — rationale이 허용문을 인용하는지 볼 수 있고, 그것이 요구 특성의 표지가 된다 |

즉 두 오류의 **진단 가능성**이 비대칭이다. 다만 이것이 B/C를 택할 근거가
되는지는 판정자의 판단이다 — 거짓 양성이 더 잘 보인다는 것이 그것이 덜 나쁘다는
뜻은 아니다.

---

## 4. Q11.1 — R1은 KEPT 쪽 금지도 약화시킨다. 그대로 두는가

이것을 별도 질문으로 올리는 이유: **R1의 표는 KEPT를 "Q1에 의해 금지"로
적었지만, 수선 전 KEPT는 Q1과 Q7 두 곳에서 금지받고 있었다.**

| | 수선 전 KEPT | 수선 후 KEPT (R1만 적용) |
|---|---|---|
| Q1 절(산문, "추론하지 마라") | 있음 | 있음 |
| Q7 목록(의사결정 규칙, "tie-break에 쓰지 마라") | **있음** | **없음** |

D-H1a-10 §12(Wittgenstein식 사용 규칙)는 이 둘이 **이 fixture에서 기능적으로
중복**이라고 판정했다. 그 판정이 참이면 KEPT의 금지 강도는 변하지 않고 Q11.1은
공허하다.

**그런데 그 판정이 참이라는 것이 바로 Q10의 근거였다.** 같은 전제를 반대
방향으로 쓰면: 산문 금지와 의사결정 규칙 금지가 **같은 것**이라면, 하나를
지워도 KEPT는 그대로다. 두 형식이 **다른 강도**라면, R1은 REMOVED를 열면서
**KEPT도 함께 약화**시킨다 — 그러면 수선 후 대비는 "금지 유무"가 아니라
"강한 금지 vs 없음"에서 "약한 금지 vs 없음"으로 옮겨간 것이다.

선택지:

- **Q11.1-A — 그대로.** R1 표를 문면대로 따른다. §12의 기능적 중복 판정을
  신뢰하고, KEPT는 Q1 산문만으로 금지한다.
- **Q11.1-B — KEPT에 의사결정 규칙 형태를 복원.** 표적 축을 KEPT의
  tie-breaker 목록에 다시 넣는다(REMOVED엔 안 넣는다). 그러면 Q7 목록 자체가
  arm에 따라 달라진다 — 즉 조작 위치가 Q1 절에서 **Q1 절 + Q7 목록 둘 다**로
  넓어진다. Q10이 C를 기각한 사유("Q7 전체 이동은 복합 조작")와 다른가를
  판정자가 확인해야 한다.
- **Q11.1-C — 판정자 제시.**

**R2(양 arm 재실행)가 이 문제를 완전히 덮지는 못한다.** R2는 기존 KEPT와 새
KEPT를 비교하지 못하게 만들어 **오염된 비교를 막지만**, 새 KEPT의 금지 강도가
의도한 것인지는 R2가 답하지 않는다.

---

## 5. Q11.2 — 정책의 `carrier`를 사전등록에 동결하는가

Q10.2의 하드 가드 요구사항 4가 이것을 요구하는 것으로 읽힌다:

> 4. 동일 policy ID를 금지하는 중복 규칙이 다른 섹션에 없는가

이 검사가 성립하려면 정책 객체가 각 축의 **상태**(forbidden/allowed)뿐 아니라
그 상태를 **어느 섹션이 표현하는가**(담지자)를 알아야 한다. 운영 세션의
구현안은 축마다 `carrier`를 두는 것이다:

```yaml
source_kind_priority:
  kept: forbidden
  removed: allowed
  carrier: Q1_LIVENESS_CLAUSE     # KEPT의 금지를 담지하는 섹션
evidence_count:
  kept: forbidden
  removed: forbidden
  carrier: Q7_TIEBREAKER_LIST
```

그리고 요구사항 4는 "한 축의 금지를 담지하는 섹션이 **정확히 하나**"로
구현된다 — 이것이 blocker #16과 Q10의 결함을 **구조적으로** 불가능하게 만드는
지점이다.

질문: `carrier` 매핑이 **사전등록에 동결되는 판정 장치**인가, 아니면 구현
세부인가?

- **Q11.2-A — 동결한다.** 사전등록에 축×arm×담지자 표를 싣고, 표와 렌더 결과의
  일치를 테스트로 고정. 담지자를 바꾸는 것은 amendment가 된다.
- **Q11.2-B — 구현 세부.** 정책 상태만 동결하고 담지자는 렌더러 내부에 둔다.
- **Q11.2-C — 판정자 제시.**

---

## 6. 판정 전까지 운영 세션이 하는 것 / 하지 않는 것

**한다**:

- 정책 계약 스키마·구조 단언 6항·연역 검사·테스트를 **Q11과 무관한 부분까지**
  구현한다. 정책 객체와 검사는 렌더링 선택과 독립이다.
- R1의 **결정된 부분**(공통 목록에서 표적 축 4개 제거)을 구현한다.
- `REMOVED_ALLOWED_RENDERING`을 **미정 상태로 명시**하고, 그 값이 미정인 동안
  **동결(freeze)을 거부하는 fail-closed 가드**를 둔다. 판정 없이 프롬프트가
  동결되는 경로를 코드가 막는다.

**하지 않는다**:

- 프롬프트 동결, trial 실행, 새 사전등록 확정.
- Q11·Q11.1·Q11.2를 운영 세션 판단으로 채우기. 세 질문 전부 조작 표면의
  크기·형태를 바꾸므로 P7 대상이다.
- 독립 리뷰 실행 — 리뷰할 표면이 확정되지 않았다. (Q9 때 리뷰를 생략한 근거가
  "표면 불변"이었고, 이번엔 **"표면 미확정"** 이라 같은 이유로 아직 이르다.
  판정 후 표면이 확정되면 리뷰는 **필수**다 — 3차 리뷰(2026-08-02)는 R1이
  적용되는 순간 무효가 된다.)

---

## 7. 이 요청서의 지위

- **실행 전 판정 요청이다.** 수선 코호트는 0 trial이므로 재동결 비용이 없다.
- 다만 **최초 코호트 40건의 결과를 아는 상태에서 쓰였다.** D-H1a-10 §11이
  요구한 post-result 공개 대상이며, 새 사전등록에 그 사실을 명시한다.
- §2의 바이트·길이는 전부 실측이고 결과와 무관하게 성립한다. §3.2의 위험
  비대칭 논증만 최초 코호트 결과를 참조하며, 그 사실을 그 자리에 표시했다.

---

## 8. 운영 세션 의견 (판정 아님)

- **Q11**: A(침묵)가 저작을 최소화한다는 점에서 매력적이지만, §3.2의 진단
  가능성 비대칭이 걱정된다. A로 갔다가 또 defer 쏠림이 나오면 "이번엔 정말
  효과가 없었나, 아니면 침묵이 허용으로 읽히지 않았나"를 다시 분해해야 하고,
  그것을 분해할 대조군이 코호트 안에 없다. Q10이 방금 그 자리에서 왔다.
- **Q11.1**: §12의 기능적 중복 판정을 신뢰하면 A(그대로)가 맞다. 다만 그
  판정이 "이 fixture에서"라는 한정을 달고 있다는 점은 지적해 둔다.
- **Q11.2**: A(동결)를 권한다. 요구사항 4가 검사하려는 명제 자체가 담지자에
  관한 것이므로, 담지자가 동결되지 않으면 그 검사가 무엇을 보증하는지 불분명해
  진다.
- 세 질문 전부 **설계 담당의 것**이다. 위는 구현하며 본 것을 적은 것이고
  판정이 아니다.
