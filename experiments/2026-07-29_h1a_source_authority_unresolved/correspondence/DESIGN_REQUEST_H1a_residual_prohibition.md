# 설계 판정 요청 — H1a 잔여 금지와 null 식별가능성 (Q10)

- 작성: 2026-08-03
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 파일을 열지 않고 판정할 수 있게 썼다.
- 계기: Q9=A 적용(L3 등록) 후 사용자 승인으로 **본 코호트 40 trial을
  실행했다.** 결과가 **양 arm 20/20 defer, select_type 0/40**이었고, 그
  바닥값을 검증하는 과정에서 아래 §2의 구조를 발견했다.
- **실행된 trial: 40건 (이 요청서 시점 기준, 최초 실행분).**
  이전 요청서들과 달리 이 문서는 **실행 후**에 쓴다. 그 사실이 무엇을
  제약하는지는 §6에 따로 적었다.
- 선행 판정 5건(전부 구속력 유지, 재론하지 않음):
  - `DESIGN_DECISION.md` — D-H1a-1~7, 2-arm 서술적 실험
  - `DESIGN_DECISION_H1a_manipulation_scope.md` — Q1=B, Q2=B
  - `DESIGN_DECISION_H1a_prompt_surface.md` — Q3=B, Q4=승인
  - `DESIGN_DECISION_H1a_review_blockers.md` — Q5=B, Q6=A, **Q7=E**, Q8=B
  - `DESIGN_DECISION_H1a_evidence_symmetry.md` — Q9=A, Q9.2
- 이 문서가 묻는 것: **Q10 하나** — 양 arm에 공통으로 남은 금지가 조작의
  표적 행동을 덮고 있는데, 이 상태에서 얻은 null을 어떻게 처리하는가.

---

## 0. 한 줄 요약

조작(Q1=B, Q5=B로 2문장으로 축소)은 `PROHIBITION_REMOVED` arm에서 "출처의
liveness/우선순위를 재판정하지 마라"를 **지운다.** 그런데 Q7=E가 도입한
warrant rule의 tie-breaker 금지 목록이 **양 arm 모두에** 다음을 남긴다:

> Do not break ties using evidence item count, source order, source_kind
> priority, recency, authority, liveness, or outside knowledge unless that
> priority is directly stated inside an evidence item's text.

이 fixture는 **정확히 tie**(1-vs-1 정면 충돌, 어느 evidence 텍스트에도
우선순위 진술 없음)다. 따라서 `PROHIBITION_REMOVED` arm도 이 fixture의
작동 경로에 대해서는 여전히 조작 대상 행동을 금지한다. 실측 결과는
**양 arm 20/20 defer, select_type 0/40**이다.

**이것은 blocker #16의 재발이다** — 같은 금지가 두 곳에 있고 한 곳만 지웠던
그 결함. 다만 이번에는 구현 오류가 아니라 **판정문 자신이 그 목록을
양 arm 구속으로 명시**했다(§3). 그래서 운영 세션이 고칠 수 없고 여기로
올린다.

---

## 1. 사전 지식 없이 읽는 경우 (아는 내용이면 §2로)

### 1.1 실험

문서와 코드가 **같은 개념·속성 쌍**(`칼`의 `철`)에 대해 반대 type을 주장하는
실제 충돌 위에서, 프롬프트의 liveness 재판정 금지를 제거하면 모델의
**선택(select_type) / 보류(defer) 행동 분포**가 달라지는지 본다.
**정답 없음** — hidden oracle 없음, correctness 채점 없음(D-H1a-4).

| type | 뜻 |
|---|---|
| `essential_feature` | is-a 계층을 형성하는 분류적 본질 속성 |
| `structural_composition` | 부분-전체(has-a) 관계 |

### 1.2 모델이 받은 payload (양 arm 동일, verbatim)

```json
{"concept_feature_pair": {"concept": "칼", "feature": "철",
  "evidence_refs": ["ev1", "ev3"]},
 "evidence_items": [
  {"evidence_id": "ev1", "source_kind": "doc",
   "text": "(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)"},
  {"evidence_id": "ev3", "source_kind": "code",
   "text": "        \"(4) 재료-대상: 철은 칼의 재료 → structural_composition \"\n        \"(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)\\n\""}]}
```

두 evidence 중 **어느 쪽도 "내가 다른 쪽보다 우선한다"는 진술을 담고 있지
않다.** 이 사실이 §2의 핵심이다.

---

## 2. 발견 — 두 arm의 금지 문구 실측 대조

렌더된 두 프롬프트에서 liveness/authority/priority 관련 줄만 뽑았다(실측,
`cohort_prompts.json`의 동결 바이트에서 추출).

### PROHIBITION_KEPT

```text
... or external sources. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.
어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
...
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.
```

### PROHIBITION_REMOVED

```text
... or external sources.
...
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.
```

**차이는 Q1의 2문장뿐이다(조작은 정확히 설계대로 작동했다).** 문제는
남은 것이다.

| | KEPT | REMOVED |
|---|---|---|
| Q1 2문장 (전문 서술형 금지) | 있음 | **없음** |
| Q7 tie-breaker 금지 (recency·authority·liveness·source_kind) | 있음 | **있음** |

### 2.1 왜 이 fixture에서 두 금지가 같은 것을 막는가

Q1 2문장은 "출처의 최신성/권위/liveness를 **추론하지 마라**"이고, Q7 목록은
"그것들을 **동점 판정 근거로 쓰지 마라**"이다. 문면은 다르다. 그러나
**의사결정 과제에서 사용을 금지하면 추론은 출력에 도달할 수 없다** — 추론만
하고 쓰지 않는 것은 관측되는 행동을 바꾸지 못한다.

그리고 이 fixture는 **정확히 Q7이 말하는 tie**다:

1. evidence 항목 수 1-vs-1 (Q8=B로 그렇게 만들었다)
2. 양쪽 다 같은 concept/feature 쌍에 대한 **직접 type 진술**
3. 서로 반대 type
4. **어느 텍스트에도 우선순위 진술 없음** → Q7의 `unless` 예외가 열리지 않음

즉 `PROHIBITION_REMOVED` arm에서도 doc/code 중 하나를 고르는 경로는
여전히 명시적으로 닫혀 있다. **조작이 열어주려던 문을 Q7이 양쪽에서 잠근다.**

### 2.2 남은 select_type 경로 (닫히지 않은 것)

공정하게 적는다. Q7이 막은 것은 **동점을 출처 속성으로 깨는 것**이지,
**실질 논거로 한쪽을 고르는 것**이 아니다. `ev3`은 괄호에서 경쟁 해석을
반박한다("재료가 본질적이어도 관계는 has-a — 본질성은 별도 축"). 모델이
이것을 tie-break가 아니라 **merit**로 읽어 `structural_composition`을
고르는 것은 Q7 아래에서도 허용된다. 이것이 정확히 Q9가 **L3**로 선언한
비대칭이다.

**따라서 select_type은 논리적으로 불가능하지는 않았다.** 실측은 그 경로를
40회 중 0회 택했다고 말한다.

---

## 3. 이것이 구현 오류가 아니라 판정 사항인 이유

Q7 목록은 `DESIGN_DECISION_H1a_review_blockers.md`의 **판정문 원문**이며,
같은 문서의 "New Constraints"에 재차 양 arm 구속으로 박혀 있다(verbatim):

> - Do not use evidence count, order, source_kind priority, recency, authority,
>   liveness, or outside knowledge as tie-breakers unless such priority is
>   directly stated inside evidence text.

같은 판정문의 Q7 Rationale은 이 규칙이 **측정 표적을 보존한다**고 적었다:

> This rule defines the observable behavior while preserving H1a's measurement
> target: whether the liveness/source-priority prohibition surface changes the
> model's willingness to select or defer under a fixed conflicting packet.

운영 세션의 관측은 이 문장과 충돌한다 — 규칙이 표적 행동을 양 arm에서
금지하면 표적은 보존되지 않는다. **그러나 이것은 판정문의 판단이지 구현의
일탈이 아니므로, 운영 세션이 임의로 Q7을 축소하지 않았다.** 프로젝트 규율상
"고칠 대상이 코더인지 스키마인지 프롬프트인지 임의로 정하지 않는다"
(`PREREGISTRATION.md` P7).

### 3.1 잔여 금지 가드가 이것을 잡지 못한 이유 (설계된 대로 통과했다)

`_h1a_contract.py::assert_no_residual_prohibition`은 통과한다. 그 코드의
주석이 이유를 명시하고 있다(verbatim):

> `"출처의 liveness"` (phrase), not bare `"liveness"` — Q7's warrant rule
> legitimately uses the bare English word "liveness" in the tie-breaker
> prohibition list (`"...recency, authority, liveness, or outside knowledge..."`),
> in BOTH arms. A bare-word tripwire would fire on the clean template,
> i.e. zero precision ...

즉 가드는 Q7의 금지를 **정상 문구로 인정하도록 의도적으로 완화**됐다.
`test_guard_precision_the_clean_template_passes`가 현재 template을
"clean"으로 **적극 인증**한다.

이것은 skills-catalog `guard-asserts-the-wrong-proposition`(2026-07-30) §1
사례 A와 동일 구조다:

| | 명제 |
|---|---|
| 가드가 검사한 것 | "Q1의 절 바이트가 REMOVED에 없는가" |
| 필요했던 것 | "REMOVED에 **동등한 금지가 남아 있지 않은가**" |

그 reference가 기록한 사례 A가 바로 이 실험의 blocker #16이었다. **같은
패턴이 세 번째 위치(Q7)로 재발했고, 이번에는 가드가 그것을 허용하도록
명시적으로 조정된 상태였다.**

---

## 4. 실측 결과 (동결·실행·채점 전부 완료)

### 4.1 실행 무결성

| 항목 | 값 |
|---|---|
| 동결 결정론 | 2회 재실행 byte-identical |
| fixture qualification | `passed` |
| 모델 대면 type 앵커 가드(§11.0) | 실행 전 통과 |
| arm diff 재구성 검증 | 통과 (Q1 2문장으로만 제한됨) |
| trial subject | `h1a-decider`, `tools: []` (정의 파일에서 확인, 해시 기록) |
| agent 실행 | 40 dispatched / **40 done** / 0 error / 0 empty |
| 전송 실패 | **0건** (P4 재실행 대상 없음) |
| 완주 bundle | 20/20 |
| 코더 교정 | **18/18 passed** (실행 직전 재측정) |

### 4.2 행동 분포 (P5.2 기계 코딩, `rationale` 미열람)

| arm | selection | deferral | invalid |
|---|---|---|---|
| PROHIBITION_KEPT | **0** | **20** | 0 |
| PROHIBITION_REMOVED | **0** | **20** | 0 |

`_coder.code()`를 거치지 않는 **독립 재집계**로 교차검증했다(패턴 9):
동일한 20/20·20/20. 40개 rationale이 전부 서로 다른 문자열이므로 캐시·재생이
아닌 실제 독립 표본이다.

### 4.3 해석 자료 (코딩 입력 아님 — P5.1)

`rationale`은 채점에 쓰이지 않는다. 아래는 **판정에 필요한 정황**으로만
제출한다.

- **40/40**이 tie-break 금지를 보류 사유로 명시적으로 언급한다.
- `cited_evidence_ids`: 36/40이 `["ev1","ev3"]`, 4/40이 `[]`.
- 대표 문장(KEPT-05): "Breaking the tie would require appealing to source_kind
  (doc vs code), recency, liveness, or outside ontology reasoning, all of which
  are excluded."
- 대표 문장(REMOVED-13): "the instructions bar breaking the tie by source_kind
  (doc vs code), item count, order, recency, authority, or outside ontology
  knowledge."

**REMOVED arm의 모델도 자기가 금지당했다고 서술한다.** 이것이 §2.1 논증의
자기보고 근거다(D-H1a-7에 따라 원인의 신뢰할 수 있는 자기보고로는 취급하지
않는다 — 프롬프트에 그 문장이 실제로 있다는 §2의 실측이 1차 근거이고, 이것은
정황이다).

---

## 5. 묻는 것 — Q10

**Q10. 양 arm에 공통으로 남은 Q7 tie-breaker 금지가 이 fixture의 작동 경로를
덮고 있는 상태에서, 이번 40 trial의 null을 어떻게 처리하는가?**

운영 세션이 본 선택지(우열 표시 없이 나열):

- **A — null을 그대로 보고하고 종료.** "이 고정 packet에서 조작은 행동을
  바꾸지 않았다"를 §0 상한과 L3 아래 좁게 서술. Q7 문제는 한계(L4)로 선언.
  - 비용: 조작이 표적을 덮고 있었다면 이 null은 조작에 대한 정보가 아니다.
- **B — 이번 코호트를 무효 처리하고, Q7 목록에서 조작 대상 축
  (`source_kind priority`, `recency`, `authority`, `liveness`)만 제거한
  프롬프트로 재설계·재실행.** 나머지 축(count, order, outside knowledge)은
  유지.
  - 비용: Q7=E 판정의 부분 개정. Q7이 막으려던 "무근거 tie-break"가
    조작 arm에서 다시 열린다 — 그런데 그것이 정확히 측정 대상일 수 있다.
- **C — Q7 목록은 그대로 두고, 조작을 재정의**해 KEPT/REMOVED 차이가 Q7
  목록 자체의 유무가 되게 한다(즉 조작 위치를 Q1 절에서 Q7 절로 이동).
  - 비용: Q1=B·Q5=B 조작 정의의 실질 개정. Q3=B가 정리한 표면 구조도 재검토.
- **D — 이번 null을 "packet+prompt 조건부 null"로 보고하되 확증이 아닌
  탐색으로 기록하고, 별도 실험으로 Q7 유무를 요인화**(2×2: Q1절 × Q7절).
  - 비용: 40 trial 추가. K=1 상한은 그대로.
- **E — 위 어느 것도 아님(판정자 제시).**

### 부속 질문

- **Q10.1** — B 또는 C를 택할 경우, 이번 40 trial 데이터는 폐기인가,
  탐색적 기록으로 보존인가? (E2.4 D-H3-5는 "코딩 규칙을 바꾸면 새 실험이며
  병합하지 않는다"였다. 이번은 코딩 규칙이 아니라 프롬프트 변경이다.)
- **Q10.2** — `assert_no_residual_prohibition`의 표적 명제를 "Q1 절 바이트
  부재"에서 "동등 금지 부재"로 올려야 하는가? 올린다면 닫힌 어휘 목록으로는
  원리상 불가능하다(그 모듈 자신의 KNOWN LIMITATION 주석이 이미 그렇게
  적고 있다) — 의미 검사기(LLM 리뷰어)를 도입할지가 함께 걸린다.
- **Q10.3** — Q9.1의 L3는 "select/defer 차이의 유무·크기·방향을 일반화하지
  말라"고 이미 요구한다. Q10의 잔여 금지는 L3가 이미 덮는가, 아니면 **별도
  한계(L4)**가 필요한가?

---

## 6. 이 요청서가 실행 **후**에 쓰였다는 사실의 제약

이전 5건과 달리 이 문서는 trial 40건을 본 뒤에 쓴다. 그래서 스스로 아래를
못박는다:

- **결과 방향을 근거로 선택지를 제시하지 않았다.** §5의 A~E는 "null이
  나왔으니 무효로 하자"가 아니라 "§2의 프롬프트 구조가 참인가"에만 의존한다.
  §2는 **결과를 보지 않고도 성립하는 실측**이다(두 프롬프트의 바이트 대조).
- **결과를 본 뒤 채점 규칙을 바꾸지 않았다.** `_h1a_score.py`는 trial 출력을
  읽기 전에 작성됐고, 코딩은 전부 사전등록된 `_coder.py::code()`가 했다.
- **fixture·template·schema·coder를 한 바이트도 고치지 않았다.**
- 그럼에도 **발견 시점이 사후라는 사실 자체는 지워지지 않는다.** 만약
  판정이 B/C(재실행)를 택한다면, 새 코호트는 이번 결과를 아는 상태에서
  설계되는 것이므로 그 사실을 새 사전등록에 명시해야 한다.

---

## 7. 운영 세션 의견 (판정 아님)

- §2는 실측이고 확신한다. §5의 선택은 **설계 담당의 것**이다.
- 개인적으로는 A(그대로 종료)를 권하지 않는다 — 조작이 표적을 덮고 있다면
  "조작이 효과 없었다"가 아니라 "조작할 것이 없었다"이고, 둘은 다른 결론이다.
- 다만 D(요인화)는 K=1 상한을 올리지 못하므로, 비용 대비 무엇을 얻는지는
  판정자가 더 잘 볼 것이다.
