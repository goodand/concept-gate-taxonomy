# 설계 판정 요청 — H1a 독립 리뷰 blocker 4건

- 작성: 2026-08-01
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 파일을 열지 않고 판정할 수 있게 썼다.
- 계기: Q3=B를 구현하고 **첫 trial 직전에** 돌린 독립 리뷰가
  **동결·실행 부적합**을 냈다. blocker 2 + major 7 + minor 4 + clean 3.
  그중 4건은 운영 세션이 정할 수 없어 올린다.
- 실행된 trial: **여전히 0건**
- 선행 판정 3건(전부 구속력 유지):
  - `DESIGN_DECISION.md` — D-H1a-1~7, 2-arm 서술적 실험
  - `DESIGN_DECISION_H1a_manipulation_scope.md` — Q1=B(조작=liveness 금지 절
    전부 제거), Q2=B(앵커 진단 게이트)
  - `DESIGN_DECISION_H1a_prompt_surface.md` — Q3=B(E2.4 규칙 2~7 폐기, H1a
    전용 프롬프트), Q4=승인
- 이 문서가 묻는 것: **Q5·Q6·Q7·Q8** (전부 차단)

---

## 0. 한 줄 요약

Q3=B대로 H1a 전용 프롬프트를 만들었더니, **판정을 구현하는 과정에서 네 개의
새 문제가 생겼거나 드러났다.** 넷 다 "무엇을 측정하는 실험인가"를 바꾸므로
운영 세션이 정하지 않는다. 특히 Q5는 **Q3=B를 충실히 따랐기 때문에** 생긴
문제다 — 서문을 버리라는 지시를 따르자 조작 문장의 지시 대상이 사라졌다.

---

## 1. 사전 지식 없이 읽는 경우 (아는 내용이면 §2로)

### 1.1 실험

문서와 코드가 **같은 개념·속성 쌍**(`칼`의 `철`)에 대해 반대 type을 주장하는
실제 충돌 위에서, 계약문의 liveness 재판정 금지를 제거하면 모델의
**선택(select_type) / 보류(defer) 행동 분포**가 달라지는지 본다.
**정답 없음** — hidden oracle 없음, correctness 채점 없음(D-H1a-4).

| type | 뜻 |
|---|---|
| `essential_feature` | is-a 계층을 형성하는 분류적 본질 속성 |
| `structural_composition` | 부분-전체(has-a) 관계 |

### 1.2 두 arm과 응답 스키마

| arm | 프롬프트 |
|---|---|
| `PROHIBITION_KEPT` | liveness 금지 절 **포함** |
| `PROHIBITION_REMOVED` | 그 절 **없음** |

```
decision:           select_type | defer
selected_type:      essential_feature | structural_composition | null
cited_evidence_ids: [string]
rationale:          string
```

행동 코더는 `decision`/`selected_type` **2필드만** 읽고 `rationale`은 읽지
않는다(P5, 교정 18/18 통과).

### 1.3 현재 렌더되는 프롬프트 전문 (`PROHIBITION_KEPT`, verbatim)

```
You are an MCP client agent.

Input is a repo-derived evidence packet. Use only the packet fields presented
in this prompt. Do not use general ontology knowledge, OWL/GUFO background
knowledge, codebase memory, prior conversation context, or external sources. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.

Your task is to observe whether the packet evidence supports selecting one of
two ontology feature types for the supplied concept/feature pair, or whether
you defer.

Evidence-reading rule:
- Treat an evidence item as support only when its text directly states or
  clearly entails the ontology type of the supplied concept/feature pair.
- Evidence that merely mentions implementation details, examples, labels, or
  adjacent context without tying the concept/feature pair to one of the allowed
  types is not enough by itself.
- If you select a type, cite the evidence item ids that support that selection.
- If the packet evidence is not enough for you to select either allowed type,
  choose defer.

Allowed selected_type values:
- essential_feature
- structural_composition

Output JSON using h1a_observation_v1:
{
  "decision": "select_type" | "defer",
  "selected_type": "essential_feature" | "structural_composition" | null,
  "cited_evidence_ids": ["..."],
  "rationale": "..."
}

Consistency requirements:
- If decision is "select_type", selected_type must be one of the two allowed
  type values.
- If decision is "defer", selected_type must be null.
- Do not output repair, accept_report, abstain, missing_evidence,
  contract_verdict, evidence_audit, repair_plan, or any fields outside
  h1a_observation_v1.

payload:
{"candidate_concepts": [{"name": "칼", "features": [{"feature": "철", "type": "structural_composition", "evidence_refs": ["ev1", "ev2", "ev3"]}]}], "evidence_items": [{"evidence_id": "ev1", "source_kind": "doc", "text": "(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)"}, {"evidence_id": "ev2", "source_kind": "doc", "text": "주의: 재료-대상(4)만 essential_feature가 될 수 있습니다."}, {"evidence_id": "ev3", "source_kind": "code", "text": "        \"(4) 재료-대상: 철은 칼의 재료 → structural_composition \"\n        \"(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)\\n\""}]}
```

`PROHIBITION_REMOVED`는 위에서 **한국어 3문장만 빠진 것**이며, 나머지는
바이트 동일하다(리뷰어가 독립 계산: 공통 prefix 259자, suffix 1879자,
KEPT-only span = 그 3문장 + 선행 공백 1자, REMOVED-only span = 없음).

---

## 2. 이미 확정되어 재론하지 않는 것

- D-H1a-1~7 전부
- **Q1=B** — 조작은 "liveness·source-priority·recency·authority·supersession
  재판정을 금지하는 모델 대면 절 **전부** 제거". 절 바이트는 동결됨
- **Q2=B** — 본 코호트 전 anchor-sensitivity 진단(2×2×5=20, non-certifying,
  병합 금지). 차단 규칙과 §11.2a 해석가능성 조건 사전등록 완료
- **Q3=B** — E2.4 규칙 2~7과 서문 폐기, H1a 전용 프롬프트. §1.3이 그 결과물
- **Q4** — 승인(문구 개선 반영 완료)
- 운영 세션이 이미 조치한 리뷰 지적 2건(판정 대상 아님):
  잔여-금지 가드에 영어 명제 7종 추가(요구사항 7 미구현이었음),
  `h1a_schema.json`의 폐기된 D-H1a-5=A 서술 정정

---

## 3. Q5 (차단) — 조작 문장의 지시 대상이 사라졌다

### 3.1 실측

E2.4 원본에서 세 번째 문장 `그 판정은 이미 끝났고 너의 범위가 아니다`의
**선행사는 두 문장 앞에 있었다**:

```
이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.
```

즉 "그 판정" = "실행 전에 이미 끝난 provenance/eligibility 검증".

**Q3=B가 그 서문을 버리라고 했고, 버렸다.** 실측:

```
E2.4 antecedent sentence present in H1a template? False
```

§1.3에서 보듯 H1a 프롬프트에는 "검증이 이미 끝났다"는 진술이 없다.

### 3.2 귀결

`그 판정`이 가리킬 대상이 프롬프트에 남아 있지 않다. 리뷰어의 판단:
**프롬프트 안에서 "이미 끝난 판정"으로 읽힐 수 있는 유일한 대상은 payload의
`"type": "structural_composition"`**(§4의 앵커)이다.

그렇다면 `PROHIBITION_KEPT`만 모델에게 **"앵커는 이미 확정된 판정이다"**라고
읽히게 만든다. 앵커는 양 arm에 동일하게 있지만, **그것을 어떻게 읽으라는
지시가 한쪽 arm에만 붙는다.**

- 관측된 arm 차이를 "liveness 금지의 효과"로 귀속할 수 없다
- 이것은 조작 자체가 만들어낸 treatment×anchor 상호작용이고, **Q2 진단이
  배제하려던 바로 그 상태**다. 진단은 앵커를 뒤집어 보지만, "앵커를 어떻게
  읽으라는 지시"의 arm별 차이는 그 설계로 부분적으로만 탐지된다

### 3.3 왜 운영 세션이 정하지 않는가

떠오르는 해법 둘 다 상위 판정을 건드린다.

| 안 | 내용 | 무엇을 건드리나 |
|---|---|---|
| **A** | E2.4의 `이 packet의 evidence item은 실행 전 provenance/eligibility 검증을 통과했다.`를 **양 arm에** 되살린다 | Q3=B가 버린 서문의 부분 복원. 다만 이 문장은 liveness 금지가 **아니므로** Q1이 제거를 요구하지 않는다 |
| **B** | 삽입 span에서 세 번째 문장(`그 판정은…`)을 뺀다 | **Q1이 동결한 절 바이트** 변경. 조작이 2문장이 됨 |
| **C** | 그대로 두고 사전등록에 한계로만 명시 | 리뷰어는 이것을 blocker로 봄 — 귀속 불가가 곧 실험 무의미 |
| **D** | 그 밖 |  |

**부수 질문**: A를 택하면 그 문장이 **양 arm 공통 상수**로 들어가는데, 그것이
Q6(앵커)의 지위에 영향을 주는가? "검증이 이미 끝났다"는 진술은 앵커를
권위화할 수 있다.

---

## 4. Q6 (차단) — payload가 두 후보 type 중 하나를 건네준다

### 4.1 실측

payload에 다음이 그대로 들어간다(양 arm 동일):

```json
"candidate_concepts": [{"name": "칼", "features":
   [{"feature": "철", "type": "structural_composition",
     "evidence_refs": ["ev1", "ev2", "ev3"]}]}]
```

`structural_composition`은 **허용된 두 값 중 하나**이며, 저장소의 **실제
강제 상태**다(회귀 테스트가 이 type을 고정하고 통과한다). 하네스 자신이
반대 셀(`essential_feature`)을 "counterfactual artifact"라고 부른다.

fixture의 `builder_metadata.no_oracle`은 이렇게 적혀 있다:

> There is deliberately no expected_decision, expected_type, or semantic_class
> field anywhere in this fixture. **Neither type is marked right.**

리뷰어 판정: **중요한 층위에서 반증됨.** 두 허용값 중 하나가 "기록된 현재
상태"로 모델에게 전달되고, 그것이 하네스가 비반사실이라고 부르는 쪽이다.
또한 `select_type`으로 가는 **무비용 경로**(앵커를 그대로 반복)를 만든다 —
종속변수에 직접 작용한다.

### 4.2 왜 운영 세션이 정하지 않는가

**Q2 판정이 "모델 대면 `candidate_concepts`에서 type anchor를 제거"를
재설계 3안 중 하나로 이미 열거했다.** 다만 그것은 **진단이 발동했을 때**의
대응으로 배치돼 있고, 진단 전에 선취하는 것은 Q2가 정한 절차를 바꾸는 일이다.

| 안 | 내용 | 귀결 |
|---|---|---|
| **A** | 진단 **전에** 앵커를 제거(Q2 재설계안 1을 선취) | 천장 위험과 무비용 경로가 함께 사라진다. 단 payload가 "현재 기록 상태"를 못 담아 과제 서술이 바뀌고, Q2 진단은 재는 대상이 없어져 **불필요해진다** |
| **B** | 앵커 유지, Q2 절차대로 진단 먼저 | 판정문 절차를 지킨다. 단 §4.1의 무비용 경로는 진단으로 측정될 뿐 제거되지 않는다 |
| **C** | 앵커 유지하되 `no_oracle` 서술만 정정 | 최소 변경. 리뷰어는 이것으로 blocker가 해소되지 않는다고 봄 |
| **D** | 그 밖 |  |

**부수 질문**: A를 택하면 §1.3의 과제 문장("the supplied concept/feature
pair")은 유지되나 payload에 type이 없어진다. 그 경우 모델은 "무엇에서 무엇을
고르는가"를 evidence만으로 파악해야 하는데, 그것이 이 실험이 의도한 과제인가?

---

## 5. Q7 (차단) — 이 fixture에서 `defer`의 의미가 정의돼 있지 않다

### 5.1 실측

프롬프트가 `defer`를 지시하는 곳은 **한 군데뿐**이다:

> - If the packet evidence is not enough for you to select either allowed type,
>   choose defer.

그런데 같은 프롬프트의 지지 기준은:

> - Treat an evidence item as support only when its text directly states or
>   clearly entails the ontology type of the supplied concept/feature pair.

이 fixture의 두 증거는 **둘 다 그 기준을 만족한다**:

| id | 원문 | 그 쌍의 type을 직접 진술하는가 |
|---|---|---|
| ev1 | `(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)` | **예** |
| ev3 | `"(4) 재료-대상: 철은 칼의 재료 → structural_composition "` + `"(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)"` | **예** |

즉 "증거가 부족하다"는 전제가 **거짓**이고, 프롬프트에는 "충분하지만 서로
충돌하는 증거"를 다루는 조항이 **없다**.

### 5.2 왜 이렇게 됐나 — Q3=B의 직접적 귀결

Q3=B는 E2.4 규칙 3의 동률 조항(`양립 불가능한 둘 이상의 type이 최고 강도에서
동률이면 conflicting이다 … 동률을 깨지 마라`)이 이 fixture에서 답을 지정해
버린다는 이유로 규칙 2~7 전체를 폐기하게 했다. **판정은 옳았으나, 폐기된
조항을 대체하는 규칙이 들어가지 않았다.** 그 결과 지금은 규칙이 아니라
**공백**이 있다.

리뷰어 판정: 각 모델이 "충돌 → 두 행동 중 하나" 매핑을 **스스로 발명**하게
된다. 그러면 종속변수는 **시행마다 지시 대상이 달라지는 범주에 대한 비율**이
되어, 숫자가 어떻게 나오든 잘 정의된 측정이 아니다.

### 5.3 선택지

| 안 | 내용 | 위험 |
|---|---|---|
| **A** | 충돌 시 행동을 **지정하지 않되 충돌이 가능함을 알린다**(예: "증거들이 서로 다른 type을 지지할 수 있다. 그 경우 어떻게 할지는 네 판단이다") | 공백을 메우되 방향을 안 준다. 단 "네 판단"이 곧 defer 유도로 읽힐 수 있음 |
| **B** | 충돌 시 `defer`를 **명시**한다 | Q3가 제거한 천장을 되살린다 |
| **C** | 충돌 시 `select_type`을 **명시**한다 | 반대 방향 천장 |
| **D** | 공백을 그대로 두고 사전등록에 "이 실험의 DV는 모델이 스스로 정의한 범주에 대한 비율"이라고 한계 명시 | 리뷰어의 우려를 인정하되 측정은 진행 |
| **E** | 그 밖 |  |

---

## 6. Q8 (차단) — fixture가 2-vs-1인데 1-vs-1이라고 주장한다

### 6.1 실측

fixture의 `builder_metadata`는 이렇게 적혀 있다:

> This is a **1-vs-1 conflict**, both sides instance-bound to this exact
> concept/feature pair.

그러나 모델이 보는 것은 **doc 2건 대 code 1건**이다(§1.3 payload 참조).
문서 측에는 강조 문장(`ev2`)이 실려 있는데, **코드 측에도 구조가 똑같은
강조 문장이 존재하고 실리지 않았다**:

| 측 | 위치 | 원문 | fixture |
|---|---|---|---|
| doc | `phase_a_implementation_packet.md:106` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | **ev2로 실림** |
| code | `concept_gate_v7.py:1196-1197` | `주의: (1)~(4)는 structural_composition, (5)는 contextual_usage, (6)은 locational을 사용하세요. essential_feature는 'X는 Y의 일종'(is-a)에만.` | **누락** |

누락된 코드측 문장은 `ev3`(`:1192-1193`)에서 **4줄 아래**에 있다. 둘 다
`주의:`로 시작하고, 둘 다 예외/범위를 못박는 같은 역할을 한다.

### 6.2 귀결

항목 수가 많은 쪽이 우세해 보이면 그 자체가 `select_type`(그리고 doc 쪽
type) 방향 압력이다. **evidence를 고정한 채 앵커만 뒤집는 Q2 진단으로는
탐지되지 않는다.**

### 6.3 선택지

| 안 | 내용 | 귀결 |
|---|---|---|
| **A** | 코드측 `주의:` 문장을 **ev4로 추가** → 2-vs-2 | 대칭 회복. 단 packet이 길어지고, 추가되는 문장은 6개 type 중 4개를 열거해 **허용 enum 밖 type 이름 4개가 모델에 노출**된다 |
| **B** | `ev2`를 **제거** → 1-vs-1 | metadata 주장과 일치. 단 doc 측의 강조가 사라져 doc 측이 약해진다 |
| **C** | 그대로 두고 metadata의 "1-vs-1" 서술만 정정 | 최소 변경. 비대칭은 남고 사전등록에 한계로 명시 |
| **D** | 그 밖 |  |

**부수 실측(A안 판단에 필요)**: 코드측 `주의:` 문장은
`structural_composition` / `contextual_usage` / `locational` /
`essential_feature` 네 이름을 담고 있고, 그중 둘(`contextual_usage`,
`locational`)은 H1a의 `selected_type` enum에 **없다**. 이 노출이 허용되는가?

---

## 7. 판정 순서 제안 (비구속)

```
Q6 (앵커) ──┬──> Q5 (선행사)   : 앵커를 제거하면 "그 판정"이 가리킬
            │                     대상이 더 줄어 Q5가 악화될 수 있다
            └──> Q7 (defer 정의): 앵커가 없으면 "충분한 증거"의 판단
                                  기준이 바뀐다

Q8 (2-vs-1) : 독립
```

---

## 8. 넘을 수 없는 제약

1. 모델 대면 evidence 필드는 `evidence_id`/`source_kind`/`text` 3개뿐.
   liveness·supersession·qualification profile 노출 금지
2. E2.4의 `_surface.py`·`decision_schema.json`·`contract_prompt.md` **불변**
3. hidden correctness oracle과 인증 밴드 없음(D-H1a-4)
4. 행동 코더는 `rationale`을 읽지 않는다(P5). 어떤 판정이든 코더가 산문을
   판정해야 하는 형태가 되면 안 된다
5. **실행된 trial 0건.** 스키마·프롬프트·fixture·사전등록 어느 것을 바꿔도
   재동결 비용이 없다. 이 조건은 첫 trial과 함께 사라진다

---

## 9. 회신 형식

```text
DESIGN DECISION — H1a review blockers
decided_by:
date:

Q5 (조작 문장의 선행사 소실):     <A|B|C|D>   근거:
  Q5.1 A안일 때 복원 문장이 앵커를 권위화하는가:

Q6 (앵커가 답을 건넴):            <A|B|C|D>   근거:
  Q6.1 A안일 때 과제 서술을 어떻게 바꾸는가:
  Q6.2 A안일 때 Q2 진단은 어떻게 되는가(불필요/유지/변형):

Q7 (defer의 의미 미정의):         <A|B|C|D|E> 근거:

Q8 (2-vs-1 비대칭):               <A|B|C|D>   근거:
  Q8.1 enum 밖 type 이름 노출이 허용되는가:

deferred:
  <항목 ID>: <사유 / 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약>

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```

---

## 부록 A — 리뷰가 문제없음으로 확인한 것 (판정 참고용)

리뷰어가 제작자 테스트를 증거로 받지 않고 독립 재현한 결과, 아래는 clean:

- **두 arm의 렌더 차이가 바이트 수준에서 정확히 liveness 절뿐** — 공통
  prefix 259자·suffix 1879자를 직접 계산. 단 리뷰어 주석: "이것은 중립성을
  보증하지 않는다. Q5·Q7이 그 증거다"
- **payload whitelist가 oracle 필드를 전부 배제** — `server_response`,
  `builder_metadata`, `source_ref`, `text_sha256`, `source_commit`,
  eligibility profile 전부 부재. field-by-field 구성이라 나중에 추가된
  필드가 기본 노출되지 않음
- **template을 판정문 파일에서 로드**(재입력 안 함), drift 시 loud 실패

## 부록 B — 사전등록에 한계로만 명시하기로 한 것 (판정 대상 아님, 참고)

리뷰어가 major로 지적했으나 blocker로 보지 않았고, 운영 세션이 사전등록에
declared limitation으로 기록할 항목:

- **evidence-reading rule 4개 불릿이 전부 select 쪽에만 작용** — 3개는
  select에 비용을 부과하고 1개는 defer를 잔여값으로 만든다. defer에는 어떤
  조건·임계·출력 의무도 부과되지 않는다. arm-constant라 교란은 아니나 DV
  차원의 프롬프트발 압력
- **조작이 언어 전환과 분리 불가** — 영어 본문에 한국어 3문장(108자) 삽입.
  길이·언어 정합 placebo arm이 없어 "절의 의미" 대 "한국어 문단이 나타났다"를
  분리할 수 없음. 번역을 택하지 않은 것은 번역 자체가 검토되지 않은 저작
  행위이기 때문
