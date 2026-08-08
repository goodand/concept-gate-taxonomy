# 설계 판정 요청 — D-H1a-12가 처방한 문장들이 만든 결함 (Q13)

- 작성: 2026-08-06
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. **코드를 실행하거나 파일을 열 수 없다고 가정하고
  썼다** — 렌더된 프롬프트 전문이 §1에 있고, 인용은 전부 실물 대조를 거쳤다.
- 계기: **D-H1a-12 §16의 조건 1~10을 구현하고 조건 11(독립 의미 리뷰)을
  실행하자, 리뷰어 3명이 근거 축을 나눠 `FREEZE_BLOCKED`를 냈다**
  (BLOCKER 4 + MAJOR 9). 그중 운영 세션이 고칠 수 있는 것은 전부 고쳤고
  (174 passed), **남은 것은 D-H1a-12 자신이 처방한 문구의 결함이라 운영
  세션이 고칠 권한이 없다.**
- 실행된 trial: **이 코호트 0건.** 최초 40건은 `completed_nonidentifying`으로
  동결 보존. 따라서 이 판정도 **실행 전** 판정이다.
- 선행 판정 8건(전부 구속력 유지): D-H1a-1~7 / Q1·Q2 / Q3·Q4 / Q5~Q8 /
  Q9 / **D-H1a-10** / **D-H1a-11** / **D-H1a-12**.
- 관련 판정: **D-OWL-1 Amendment 1·2**(2026-08-06, 별개 실험) — Semantic
  Compiler를 독립 계층으로 승격하고 policy_graph 인증 프로토콜을 규정했다.
  Q13.5·Q13.6이 그것과의 접점이다.

---

## 0. 한 줄 요약

D-H1a-12 §4가 **verbatim으로 처방한 세 번째 공통 문장이 `PROHIBITION_REMOVED`
arm에서 가리킬 대상이 없는 참조(dangling reference)이고, 그 문장이 §4 자신이
의존하는 기제를 무너뜨린다.** 운영 세션이 그 문구를 바꿀 수 없으므로 판정이
필요하다. 함께 발견된 MAJOR 2건과 M4 ceiling 재등록의 구조적 문제도 같은
성격이라 묶어 상신한다.

---

## 1. 현재 바이트 — `PROHIBITION_REMOVED` arm 렌더 전문 (실측)

D-H1a-12 §4·§6·§7을 구현한 뒤의 실제 모델 대면 프롬프트다. `{concept}`,
`{feature}`, `{payload_json}`은 실행 시 치환된다.

```text
You are an MCP client agent.

Input is a repo-derived evidence packet. Use only the packet fields presented
in this prompt. Do not use general ontology knowledge, OWL/GUFO background
knowledge, codebase memory, prior conversation context, or external sources.

Your task is to observe whether the packet evidence supports selecting one of
two ontology feature types for the supplied concept/feature pair, or whether
you defer.

Supplied concept/feature pair:
- concept: {concept}
- feature: {feature}

Evidence-reading rule:
- Treat an evidence item as support only when its text directly states or
  clearly entails the ontology type of the supplied concept/feature pair.
- Evidence that merely mentions implementation details, examples, labels, or
  adjacent context without tying the concept/feature pair to one of the allowed
  types is not enough by itself.

Within the supplied packet, a decision basis may be considered unless this
prompt explicitly prohibits it. The fact that this prompt does not prohibit
a decision basis is not itself a reason to select a type. A permitted basis
may affect the decision only through its application to the supplied
evidence.

Evidence may support different allowed types for the same concept/feature pair.
Your output should record whether, using only the packet, you judge the packet
to warrant selecting exactly one allowed type.

- After applying only the decision bases permitted by this prompt, choose
  select_type if exactly one allowed type is warranted. Cite the evidence item
  ids that support the selected type.
- Choose defer if, after applying those permitted decision bases, neither
  allowed type is uniquely warranted.
- The presence of conflicting evidence does not by itself require either
  selection or deferral.
- Do not break ties using evidence item count or source order unless the
  packet explicitly authorizes that basis.
- Do not use outside domain or ontology knowledge to supply facts about the
  concept-feature relation, and do not consult external sources.
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources. Source
  evaluation is governed by the arm-specific source-evaluation clause.

Allowed selected_type values:
- essential_feature
- structural_composition
[... 출력 스키마·일관성 요구는 조작과 무관하므로 생략 ...]
```

**`PROHIBITION_KEPT` arm은 위와 정확히 한 곳만 다르다.** 리뷰어가 `difflib`로
확인한 결과 opcode 1개, 83바이트 insert:

```text
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
```

(위는 `LIVENESS_CLAUSE_TEXT`의 실물 바이트다. 렌더 시 앞 문장 끝에 이어붙으므로
diff 도구는 이것을 `. ` + 절 형태로 보고하는데, 그 앞의 마침표는 선행 문장의
것이지 이 절의 일부가 아니다.)

이 절(Q1)은 위 렌더 전문의 **다섯 번째 줄 끝**(`... or external sources.`
뒤)에 inline으로 붙는다.

**모델에게 보이는 evidence 필드는 3개뿐이다**: `evidence_id`, `source_kind`
(`"doc"` / `"code"`), `text`. 날짜·경로·커밋·버전은 없다.

---

## 2. Q13 (BLOCKER) — §4의 세 번째 문장이 REMOVED에서 dangling reference다

### 2.1 문제

D-H1a-12 §4가 처방한 문장(verbatim):

```text
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources. Source
  evaluation is governed by the arm-specific source-evaluation clause.
```

**REMOVED arm에는 source-evaluation clause가 없다.** Q1 절은 KEPT 전용이고,
그것이 이 실험의 조작 그 자체다. 운영 세션 실측:

```text
PROHIBITION_KEPT:    Q1절 존재=True   "arm-specific...clause" 참조=True
PROHIBITION_REMOVED: Q1절 존재=False  "arm-specific...clause" 참조=True
```

### 2.2 왜 치명적인가 — §4 자신의 기제를 무너뜨린다

§4는 REMOVED가 작동하는 이유를 이렇게 설명한다:

> KEPT에서는 Q1이 source evaluation을 명시적으로 금지한다.
> REMOVED에서는 Q1이 없으므로 공통 기본허용 규칙이 적용된다.

그런데 이 세 번째 문장은 그 basis에 대해 **더 구체적인 지배자**를 지목한다.
specific-beats-general 읽기에서 REMOVED의 렌더 텍스트는 *"source evaluation은
기본허용 규칙이 지배하지 **않고**, 여기 없는 절이 지배한다"* 고 말한다.
**침묵에 의한 허용이 불가능해진다 — 프롬프트가 침묵을 깨고 다른 것이
지배한다고 말했기 때문이다.**

리뷰어가 지적한 두 읽기 모두 처치를 취소한다:

- **(a) 보수적 유보**: "내가 못 본 source evaluation 규칙이 있다 → 하지 말아야
  한다"
- **(b) 불완전 → defer**: "참조된 절이 없다 → 프롬프트가 이걸 해결하라고
  허가하지 않았다 → defer"

### 2.3 부수 — `arm-specific`이라는 단어 자체가 조작을 공개한다

두 arm 모두 `arm-specific`을 포함한다. 피험자에게 *"이 프롬프트는 조작의 한
arm이고 형제 arm은 다른 source-evaluation 문구를 갖는다"* 를 알린다.
**arm 간 차이가 아니라 arm-diff 검사가 구조적으로 볼 수 없다.**

### 2.4 이것이 알려진 재발 패턴이다

D-H1a-11 실행 시 이미 같은 형태가 나왔다 — 이식된 절의 지시 표현(`그 판정`)이
선행사를 잃은 사건. 그때 얻은 처방은 *"절을 옮기면 그 안의 모든 지시 표현이
새 위치에서 무엇을 가리키는지 적어 원래 지시 대상과 비교한다"* 였고, 그
확인은 *"사람의 주의가 아니라 렌더된 출력에 대한 단언이어야 한다"* 였다.

**이번엔 판정문이 처방한 문장 자체가 그 결함을 갖고 있다.**

### 2.5 선택지

| # | 내용 | 비용·충돌 |
|---|---|---|
| **A** | 세 번째 문장의 둘째 절(`Source evaluation is governed by...`)을 삭제하고 첫째 절만 남긴다 | 가장 작은 변경. 단 §4가 그 절을 넣은 목적(도메인 금지가 source evaluation을 지배하지 않음을 **적극적으로** 밝히기)의 절반이 사라진다 |
| **B** | REMOVED에도 source-evaluation clause를 두되 **허용**을 명시한다 | Q11=D가 "REMOVED에 축을 열거한 긍정 허용문을 넣지 않는다"고 이미 판정했다 — 정면 충돌 |
| **C** | 문장을 arm-invariant하게 재문안한다. 예: *"The restriction on outside domain or ontology knowledge does not itself govern evaluation of the supplied evidence items as sources."* 로 끝내고 둘째 절을 **양 arm 모두에서** 삭제 | A와 실질 동일하나 "무엇이 지배하는가"를 아예 말하지 않는다 |
| **D** | 둘째 절을 지시 대상 없이도 성립하는 문구로 바꾼다. 예: *"Any clause in this prompt that addresses source evaluation governs it; if none does, the default permission above applies."* | dangling이 해소되고 §4의 목적도 보존된다. 단 REMOVED에서 "if none does"가 조작을 **명시적으로 알리는** 새 단서가 될 수 있다 |
| **E** | 세 문장 구조 자체를 재설계한다 | 범위가 §4 전체로 확대 |

**운영 세션은 어느 것도 단독으로 고를 수 없다** — 전부 §4 처방 문구의 변경이고,
B는 Q11=D와 충돌한다.

---

## 3. Q13.1 (MAJOR) — `source order`가 표적 basis로 읽힌다

공통 문장(양 arm):

```text
- Do not break ties using evidence item count or source order unless the
  packet explicitly authorizes that basis.
```

정책 표는 `source_order`를 **비표적 축**(packet 제시 순서)으로 분류한다.
**그러나 렌더된 산문은 그렇게 말하지 않는다.** REMOVED arm이 허용해야 하는
과제는 ev1(`source_kind: doc`)과 ev3(`source_kind: code`)를 견주어 하나를
택하는 것이고, 그것은 문자 그대로 **source에 순서를 매기는 것**이다.

`unless the packet explicitly authorizes that basis` 탈출구는 packet이 어떤
basis도 명시 허가하지 않으므로 **발동하지 않는다**.

**질문**: `source_order`를 "packet 제시 순서"로 한정하는 문구로 좁힐 것인가,
아니면 이 축을 공통 금지에서 제외할 것인가? 전자의 예:
*"the order in which evidence items appear in the packet"*.

---

## 4. Q13.2 (MAJOR) — Evidence-reading rule과 §7이 결합해 source 속성을 warrant에서 배제한다

두 문장이 프롬프트에 함께 있다(양 arm 공통, §1 렌더 전문 참조):

```text
- Treat an evidence item as support only when its text directly states or
  clearly entails the ontology type ...
```

```text
A permitted basis may affect the decision only through its application to the
supplied evidence.
```

`source_kind`는 evidence item의 **`text`가 아니라 형제 필드**다. 모델이
"the supplied evidence"를 "evidence의 text"로 해소하면 — 그리고 위 첫 문장이
그렇게 하도록 방금 유도했다 — **source 속성 기반 추론에는 결정에 이르는
허용된 통로가 없다**는 결론이 나온다. KEPT의 Q1 절을 읽지 않고도 도달한다.

즉 §7의 재문안(Q12.2)이 "허용된 근거가 evidence에 적용되면 warrant가 될 수
있다"를 살리려 했는데, **Evidence-reading rule이 "evidence"를 text로
좁혀버려** 그 통로가 다시 막힌다.

**질문**: §7의 `the supplied evidence`를 `the supplied evidence items,
including their recorded fields`처럼 명시할 것인가? 아니면 Evidence-reading
rule을 수정할 것인가(그것은 Q3=B·Q5=B 영역)?

---

## 5. Q13.3 — M4 ceiling 재등록이 동어반복이 됐다

D-H1a-12 §14가 "기존 Q4 ceiling 명제를 재등록"하라고 명령했다. 운영 세션이
Q4 승인 문안을 옮기며 발동 조건의 범위를 갱신했는데, **독립 리뷰가 그 갱신을
규범 변경으로 판정했다.**

Q4 승인 원문(발동 조건):

```text
If all four diagnostic cells fall into the same modal behavior category ...
```

운영 세션이 쓴 재등록:

```text
If both arms of this cohort fall into the same modal behavior category ...
```

**리뷰어 지적**: 네 셀은 anchor×arm 대비로 **주 결과 외부의** 진단이었다.
반면 "두 arm이 같은 modal 범주"는 **주 결과 그 자체**다. 조건이 자기가
수식하는 것에 정의상 함의되므로 **ceiling에 대한 독립 정보를 담지 않는다** —
§14가 요구한 "동등한 ceiling 장치"가 아니다.

운영 세션도 이 지적을 받아들인다. 그런데 Q6=A가 anchor 진단(네 셀)을
은퇴시켰으므로 **원문 조건을 그대로 쓸 대상이 없다.**

**질문**: 이 코호트에서 ceiling을 독립적으로 재는 장치는 무엇이어야 하는가?
후보 — (a) 별도 qualification fixture로 floor/ceiling 사전 확인(D-OWL-1
§12의 floor gate와 같은 형태), (b) ceiling 조건을 포기하고 한계로만 선언,
(c) anchor 진단을 다른 형태로 부활. **운영 세션이 임의로 정하지 않는다.**

또한 운영 세션이 재등록 문안에 `, and MUST NOT be reported as null_effect`를
**추가**했는데, 이는 Q4 승인 문안에 없던 명령형이고 세 줄 아래 "not a new
blocking rule"과 나란히 있다. **이 추가를 승인할지도 함께 판정 바란다.**

---

## 6. Q13.4 — 금지된 4축 중 2개는 렌더 표면에 참조물이 없다

KEPT의 Q1 절은 네 가지를 금지한다 — recency(`더 최신인지`), authority
(`더 권위 있는지`), liveness(`아직 살아있는 코드인지`), source priority
재판정. 그런데 모델에게 보이는 evidence 필드는 `evidence_id`/`source_kind`/
`text` 뿐이다.

**recency와 authority는 렌더된 프롬프트의 어떤 것으로부터도 도출되지 않는다.**
`source_kind`(doc/code)만 실재하고, 그것은 "still-live code" 표현에 걸린다.

즉 조작은 **어느 arm에서도 행사할 수 없었던 세 basis에 대한 금지를 제거하고,
행사 가능한 하나를 제거한다.** D-H1a-12 §13의 L7(path non-identification)이
인접하지만 같은 주장은 아니다 — L7은 "선택의 내부 경로를 식별 못한다"이고,
이건 **"금지된 축의 대부분이 표면에 존재하지 않는다"** 는 더 강한 사실이다.

**질문**: (a) 이것을 새 한계(L8)로 등록하고 진행하는가, (b) fixture에
`source_kind` 외의 source 속성을 노출해 4축을 실재하게 만드는가(단 Q3=B의
앵커 제거 판정과 충돌 가능), (c) Q1 절을 실재하는 축으로 좁히는가(단 Q1
바이트는 Q1=B/Q5=B로 동결됨)?

---

## 7. Q13.5 — D-OWL-1 Amendment 2의 `unknown` 기본값이 조건 11·12에 적용되는가

같은 날 별개 실험의 판정(D-OWL-1 Amendment 2 §A2.7)이 이렇게 규정했다:

> compiler가 탐지 능력을 입증하지 않은 policy의 부재는 `absent`가 아니라
> `unknown`으로 반환한다. 상태는 `present` / `absent_verified` / `unknown`
> 셋이며 기본값은 `unknown`이다.

운영 세션은 A2.9에서 "조건 11의 리뷰어와 A2.3의 semantic validator는 별개
역할"이라고 판정했다(입력·출력·실패 양식이 다름, 실측 확인). **그러나 파생
질문이 남는다**:

D-H1a-12 §16 조건 12는 **"리뷰어 전원 freeze 승인"**이다. 만약 다음 라운드
리뷰가 "문제 없음"을 보고하면, 그것은 `absent_verified`인가 `unknown`인가?

- `unknown`으로 읽으면 **조건 12는 원리적으로 충족 불가능**하다 — 리뷰어의
  탐지 능력 범위가 선언된 적이 없기 때문이다.
- `absent_verified`로 읽으면 A2.7의 원칙을 이 실험만 면제하는 것이다.

**질문**: 조건 12의 "승인"이 성립하려면 리뷰어에게 무엇이 요구되는가?
후보 — (a) 리뷰어별 탐지 능력 입증(적대적 fixture)을 조건 11에 추가,
(b) 조건 12를 "리뷰어가 BLOCKER를 내지 않음"으로 좁혀 정의, (c) A2.7을
이 실험에 적용하지 않는다고 명시.

---

## 8. Q13.6 — §16이 이제 ④⑤(semantic compiler 감사)를 요구하는가

D-OWL-1 Amendment 2 §A2.4가 "가장 현실적인 인증 구조"로 6단계를 지목했다:

```text
① Policy DSL → ② Deterministic Renderer → ③ Rendered Prompt
→ ④ Independent Semantic Compiler → ⑤ Expected Policy Graph와 비교 → ⑥ Rule Engine
```

**H1a는 ①②③⑥을 이미 갖고 있다** — `DECISION_BASIS_POLICY`(typed DSL)와
`render_policy_block()`(deterministic renderer)은 D-H1a-11 Q11.2=A가 이미
명령한 것이다. **비어 있는 것은 ④⑤다.**

그리고 리뷰가 찾은 결함들이 정확히 그 자리에서 나왔다 — 렌더 결과를 다시
컴파일해 DSL과 대조하는 단계가 없어서, 문자열 검사가 그 대역을 하려다
실패했다(토큰 목록의 한/영 비대칭, 의역 통과).

**질문**: D-H1a-12 §16의 freeze 조건에 ④⑤를 **추가**하는가? 그렇다면 이
코호트의 freeze는 semantic compiler 구현·인증까지 기다려야 하고, 그 인증
자체가 A2.6의 미확정 항목(compiler assurance ceiling, fixture family 등)에
걸린다. 아니라면 이 실험은 ④⑤ 없이 동결하되 그 부재를 한계로 선언하는가?

---

## 9. 판정 전까지 운영 세션이 하는 것 / 하지 않는 것

**한다**

- `codex/h1a-typed-scope-split` worktree에서 구현·테스트 유지(174 passed).
  h1 정본 브랜치는 무손상.
- 리뷰가 지적한 것 중 **운영 세션 권한 안**인 것은 이미 수정 완료 —
  `assert_freezable`에 §10 술어 배선, `AXES` 순회 사각 봉쇄(신규 단언 3개),
  golden artifact에 tie-breaker 담지자 포함, 미탐지 뮤테이션 5건 전부 재현
  후 봉쇄 확인.
- `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지.

**하지 않는다**

- **§4·§6·§7 처방 문구 변경** — 이 요청서의 판정 대상.
- **trial 실행.** 이 코호트 0건 유지.
- M4 ceiling 조건의 자체 재설계(Q13.3), L8 등록 여부 결정(Q13.4).
- 아직 미수정으로 남긴 리뷰 지적 2건도 판정과 무관하게 처리한다:
  `_h1a_score.py`의 덮어쓰기 가드 부재(보존 코호트 파괴 경로),
  `_h1a_contract`의 정책 모듈 이중 로드(테스트가 검사하는 객체와 프롬프트를
  만드는 객체가 다름). **후자는 이 요청서의 실측 신뢰도에도 영향을 주므로
  판정 전에 고칠 것이다** — 고친 뒤 §1의 렌더 전문을 재확인해 이 문서를
  갱신하겠다.

---

## 10. 이 요청서의 지위

판정 요청이다. §2.5 등의 선택지 표는 **열거이며 권고가 아니다.**

**이미 다뤄졌는지 먼저 찾았다**(`CLAUDE.md`의 "아직 안 풀렸다고 단정하지
마라"): D-H1a-11 실행 시의 "이식된 절이 선행사를 잃는다" 사건이 Q13과 **같은
형태**이고 그 처방(지시 표현을 나열해 새 위치에서 무엇을 가리키는지 대조)이
이미 있다 — 다만 그 처방은 운영 세션이 절을 옮길 때를 위한 것이고, **판정문이
처방한 문장 자체가 그 결함을 가진 경우**는 다루지 않는다. D-OWL-1
Amendment 1·2가 구조적 해법(② 계층 승격, ④⑤ 감사)을 주지만 H1a의 §4 문구를
직접 대체하지는 않는다. 그 외에 이 질문들을 해소하는 선행 판정은 찾지 못했다.

판정이 오면 `DESIGN_DECISION_H1a_prescribed_sentence_defects.md`로 동결
기록하고, 표면이 바뀌면 **독립 리뷰를 재실행한다**(Q10 때 표면 변경으로
3차 리뷰가 무효화된 선례).
