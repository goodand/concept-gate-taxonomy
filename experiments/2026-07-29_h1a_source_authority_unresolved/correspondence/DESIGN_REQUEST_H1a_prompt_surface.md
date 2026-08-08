# 설계 판정 요청 — H1a 모델 대면 프롬프트 표면

- 작성: 2026-07-31
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문과 실측은
  전부 본문에 embed했다. 파일을 열지 않고 판정할 수 있게 썼다.
- 선행 판정 2건:
  - `DESIGN_DECISION.md`(D-H1a-1~7, 2026-07-29) — H1a를 2-arm 서술적 실험으로 확정
  - `DESIGN_DECISION_H1a_manipulation_scope.md`(Q1=B·Q2=B, 2026-07-30) —
    조작을 "의미론적 금지 제거"로 재정의, anchor 진단 게이트 신설
- 계기: **Q1 판정을 구현해 첫 trial 프롬프트를 조립하다가, H1a의 모델 대면
  프롬프트 본문이 아직 한 번도 정해진 적이 없다는 것이 드러났다.**
- 이 문서가 묻는 것: **Q3 프롬프트 표면 구성**(차단) / **Q4 보조 조건 사후 승인**(비차단)

---

## 0. 한 줄 요약

지금까지 설계는 **두 arm이 무엇으로 다른가**(조작)만 규정했고 **프롬프트 본문**은
정한 적이 없다. 본문을 채우려고 보니 E2.4 계약문의 규칙 2~7이 H1a 응답 스키마와
맞물리지 않고, 특히 **규칙 3의 동률 조항이 이 fixture에서 답을 지정해 버릴
가능성**이 있다. 어느 쪽으로 채우든 연구 질문이 달라지므로 운영 세션이 정하지
않는다.

---

## 1. 사전 지식 없이 읽는 경우 (§3으로 건너뛰어도 됨)

### 1.1 실험

ConceptGate는 자연어에서 개념(concept)과 속성(feature)을 뽑아 온톨로지 계층을
만든다. 각 feature에 6개 type 중 하나가 붙는다. 이 문서에 나오는 둘:

| type | 뜻 |
|---|---|
| `essential_feature` | is-a 계층을 형성하는 분류적 본질 속성 |
| `structural_composition` | 부분-전체(has-a) 관계 |

H1a는 **같은 concept/feature 쌍에 대해 문서와 코드가 반대 type을 주장하는**
실제 충돌 위에서, 계약문의 liveness 재판정 금지를 제거하면 모델의
**선택/보류 행동 분포**가 달라지는지 본다. **정답이 없다** — hidden oracle
없음, correctness 채점 없음(D-H1a-4).

### 1.2 재료 (fixture, 독립 리뷰 반영 후 확정본)

| id | source_kind | 원문 | 주장 |
|---|---|---|---|
| `ev1` | `doc` | `(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)` | 철 = essential |
| `ev2` | `doc` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | 예외 명시(ev1 보강) |
| `ev3` | `code` | `"(4) 재료-대상: 철은 칼의 재료 → structural_composition "` + `"(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)\n"` | 철 = structural |

**ev1과 ev3은 문장 줄기가 동일하고 type만 반대다.** 둘 다 이 concept/feature
쌍을 명시적으로 지목한다. 모델이 받는 evidence 필드는
`evidence_id`/`source_kind`/`text` 3개뿐이다.

`candidate_concepts`에 기록된 anchor: **`칼`/`철` = `structural_composition`**
(저장소의 실제 강제 상태). concept 1개 / feature 1개.

**모델은 어느 쪽이 최신인지 모른다.** 문서가 코드보다 오래됐다는 사실은
하네스와 사람의 지식이고 모델에 전달되지 않는다.

### 1.3 두 arm

| arm | 계약문 |
|---|---|
| `PROHIBITION_KEPT` | liveness 금지 절 **포함** |
| `PROHIBITION_REMOVED` | liveness 금지 절 **전부 삭제**(Q1=B) |

두 arm은 같은 fixture·모델·파라미터·응답 스키마를 쓴다.

### 1.4 응답 스키마 `h1a_observation_v1` (현재 커밋된 그대로)

```
decision:           select_type | defer
selected_type:      essential_feature | structural_composition | null
cited_evidence_ids: [string]
rationale:          string
```

일관성 제약: `select_type`이면 `selected_type`은 두 값 중 하나,
`defer`면 `null`. 모순 조합은 **어느 쪽으로도 관대하게 해석하지 않고**
`invalid`로 코딩한다. 행동 코더는 `decision`/`selected_type` **2필드만**
읽고 `rationale`은 절대 읽지 않는다(P5, 교정 18/18 통과).

---

## 2. 이미 확정된 것 (판정 대상 아님)

- D-H1a-1~7: 2-arm / 정답·인증 밴드 폐기 / oracle 없음 / H1a 전용 스키마·
  surface 사본 / 제약 #11 양쪽 미적용 / 인과 귀속 금지
- Q1=B: 조작 = "liveness·source-priority·recency·authority·supersession
  재판정을 금지하는 **모델 대면 절 전부** 삭제, **그 밖의 packet-boundary와
  no-external-knowledge 제약은 보존**". 구현 완료(`_h1a_contract.py`, 11 tests)
- Q2=B: 본 코호트 전 anchor-sensitivity 진단(2×2×5=20, non-certifying, 병합 금지)
- 사전등록 P1~P7: N=20/arm, 출력 내용 기반 제외 없음, invalid는 제3의 행동
  범주로 분모 포함, 결과 방향에 따른 조기종료 없음
- fixture 재구성(독립 리뷰 C2~C10): ev3 교체, test evidence 제거,
  payload에서 `server_response` 제거, filler feature 제거

---

## 3. 실측 (N1~N8)

| # | 실측 | 확인 방법 |
|---|---|---|
| **N1** | E2.4 계약문 fenced block은 **113행**. 구조: L1-17 서문 / L18 `절대 규칙:` / L20 규칙1 / L27 규칙2 / L54 규칙3 / L69 규칙4 / L76 규칙5 / L91 규칙6 / L97 규칙7 / L109 스키마 지시 / L111-113 payload 슬롯 | 블록 파싱 후 행 번호 추출 |
| **N2** | 서문이 packet 내용을 `evidence_items, candidate_concepts, server_response만 포함한다`고 서술 — **H1a에서는 거짓.** C4 조치로 payload에서 `server_response`를 제거했다 | 원문 판독 + payload 키 대조 |
| **N3** | 서문 목표 문장이 `확정할 수 있는지, 보류해야 하는지, 또는 수리해야 하는지`로 3지선다 — H1a 스키마에 **repair 없음**(2지선다) | 원문 대조 |
| **N4** | 규칙 1의 둘째 불릿이 `evidence_items에 없는 정보가 필요하면 abstain해야 한다` — `abstain`은 E2.4 어휘, H1a는 `defer` | 원문 대조 |
| **N5** | 규칙 2는 evidence를 `direct_support`/`indirect_context`/`ambiguous`/`out_of_scope`로 분류하고 `conflicts_with_evidence_ids`를 요구 — **h1a_observation_v1에 해당 필드 없음** | 스키마 대조 |
| **N6** | 규칙 5·6·7은 `repair`/`abstain`/`accept_report` 결정과 `repair_plan`·`abstain.required`·`missing_evidence` 필드를 요구 — **h1a_observation_v1에 결정 자체가 없음** | 스키마 대조 |
| **N7** | 규칙 4(전역 feature-type invariant)는 "같은 feature 이름이 여러 concept에 있으면"을 다룸 — H1a는 concept 1 / feature 1이라 **공허** | fixture 대조 |
| **N8** | L109가 `출력은 decision_schema.json의 evidence_contract_v1 schema를 따른다.` — **틀린 스키마를 지시** | 원문 판독 |

### 3.1 선례 실측 (H3가 같은 문제를 어떻게 풀었는가)

같은 저장소의 선행 실험 H3도 **E2.4 계약문을 다른 스키마에 얹는** 문제를
겪었고, 이렇게 풀었다:

- 규칙 1~7을 **바이트 그대로** 가져온다. L109 anchor에서 잘라내고
  (anchor가 없으면 raise), 자기 스키마 지시 문장을 append
- **스키마를 키웠다** — 규칙이 요구하는 감사 필드를 `contract_assessment`
  객체 아래에 그대로 담았다
- 연결은 **어휘 매핑 문장 한 줄**(verbatim):

> 출력의 action/repaired_concepts/cited_evidence_ids/report는
> decision_schema_h3.json의 h3_contract_action schema를 따른다. 위 규칙의
> decision 필드는 이제 action이다(accept_report/repair는 이름이 같고,
> abstain은 defer로 이름만 바뀐다). 위 규칙이 요구하는 contract_verdict/
> evidence_scope/evidence_audit/feature_judgments/invariant_checks/
> repair_plan/abstain은 전부 contract_assessment 객체 아래에 그대로 채운다.

- 스키마 JSON은 rendered prompt가 아니라 **agent 정의(system prompt)**로
  전달된다. `rendered_prompt_sha256`은 스키마를 덮지 않고,
  `system_prompt_sha256`·`presented_schema_sha256`이 따로 덮는다

---

## 4. Q3 (차단) — H1a의 모델 대면 프롬프트를 어떻게 구성하는가

### 4.1 문제의 핵심 — 규칙 3이 이 fixture에서 답을 지정할 수 있다

규칙 3 전문(L54-68, verbatim):

```
3. sufficiency를 먼저 판정하라. 아래 5단계를 순서대로 그대로 적용한다.
   1) direct_support로 분류한 evidence만 후보로 취한다. indirect_context,
      ambiguous, out_of_scope는 아무리 많아도 sufficiency를 만들지 못한다.
   2) 후보를 supported_type별로 묶고, 각 type이 도달한 최고 claim_strength를
      구한다. 강도 순서는 explicit > implicit > weak > none이다.
   3) 최고 강도에 도달한 type이 정확히 하나면 sufficient이고, selected_type은
      그 type이다.
   4) 양립 불가능한 둘 이상의 type이 최고 강도에서 동률이면 conflicting이다.
      이때 각 evidence의 conflicts_with_evidence_ids에 반대쪽 evidence의 id를
      적고, selected_type은 null로 둔다. 한쪽이 더 그럴듯하다는 이유로
      동률을 깨지 마라 — 강도가 같으면 충돌이다.
   5) direct_support 후보가 하나도 없으면 insufficient다.
   - 어느 단계에서도 "그나마 제일 가까운 type"을 고르지 마라. 3)에서 단독
     최고 강도가 나오지 않으면 4) 또는 5)로 간다.
```

**H1a fixture는 정확히 4)의 동률이다.** ev1(doc→essential)과
ev3(code→structural)이 같은 문장 줄기로 같은 쌍에 반대 type을 명시하고,
둘 다 explicit로 읽힐 것이다. 4)는 그 경우 `selected_type = null`을
지시한다 — H1a 어휘로는 **`defer`**.

해석이 두 갈래다:

| 해석 | 귀결 |
|---|---|
| **무해** | "그럴듯하다"(plausibility)와 "더 최신·권위"(recency/authority)는 다른 근거다. KEPT arm만 후자를 **추가로** 금지하므로, REMOVED arm은 recency 근거로 동률을 깰 수 있다. 규칙 3은 defer를 살아있는 선택지로 만들어 주는 **상수**이고 조작은 정상 작동 |
| **치명** | 모델이 "동률을 깨지 마라"를 **모든 근거에 대한 금지**로 읽으면 양 arm 모두 defer 천장. 조작 효과 0, 실험이 아무것도 측정 못 함 |

**이 해석 차이가 Q3 선택지 A의 성패를 가른다.**

### 4.2 왜 Q2 진단이 이 위험을 잡지 못하는가

Q2 판정의 차단 규칙은 **앵커를 뒤집었을 때 무엇이 바뀌는가**만 본다:

> Treat gross anchor sensitivity as present if flipping only the anchor
> changes the modal behavior category or modal selected type in either arm,
> or changes the selection/defer count by at least 2 out of 5 in either arm
> comparison.

규칙 3이 만든 천장은 **앵커가 아니라 프롬프트**가 만든 것이다. 네 셀이 전부
defer면 "앵커를 뒤집어도 바뀐 게 없다" → gross anchor sensitivity **부재** →
게이트 통과. 그 뒤 본 코호트의 null은 여전히 해석 불가다. **Q4가 이 구멍을
다룬다.**

### 4.3 부수 실측 — 이 조항은 한 번도 발동된 적이 없다

E2.4는 `fixture_conflicting.json`(동률 사례)을 갖고 있으면서 H3 pilot에서
**의도적으로 제외**했다(코드 주석 verbatim: `# D-H3-2: conflicting (E24-F-04)
stays excluded, not replaced.`). **즉 이 프로젝트에서 규칙 3의 동률 조항이
실제 모델에게 발동된 적이 한 번도 없다.** H1a가 첫 사례가 된다.

이것은 A안을 지지하는 근거도, 반대하는 근거도 된다 — 아직 관측된 적 없는
조항의 효과를 예측으로 정하는 셈이기 때문이다.

### 4.4 선택지

| 안 | 내용 | 귀결 |
|---|---|---|
| **A** | 규칙 1~7 유지 + 스키마 확장(H3 선례 그대로) | 운영 세션 저작분 최소, Q1의 "기존 계약 표면 보존"에 가장 충실. 단 §4.1의 위험을 그대로 안고 가고, `h1a_schema.json`을 키워 재동결해야 한다 |
| **B** | 규칙 1만 유지 + 최소 task 지시 저작 | 동률 지시를 넣지 않아 §4.1 위험 소멸, 스키마 불변. 단 규칙 2~7이 담고 있던 **evidence 판독 규율**(구현 서술은 direct_support가 아니다 등)도 함께 사라지고, 운영 세션 저작분이 커진다 |
| **C** | 규칙 1~7 유지하되 **규칙 3의 4)를 조작에 포함**(양 arm에서 삭제) | 동률 조항을 상수에서 제거. 단 Q1이 확정한 "liveness 금지 절 전부"라는 조작 정의를 다시 넓히는 것이고, 4)를 지우면 3)·5)만 남아 절차가 불완전해진다 |
| **D** | 그 밖 | — |

### 4.5 함께 판정해 주면 좋은 부수 질문

1. **규칙 3의 4) "한쪽이 더 그럴듯하다는 이유로"가 recency/authority 근거까지
   포괄하는가?** 포괄하면 A안에서 양 arm defer 천장이 예상된다. 포괄하지
   않으면 A안이 성립한다. (모델의 실제 해석은 실측해야 알지만, **설계 의도**가
   무엇인지는 판정 가능하다.)
2. A안을 택할 경우 스키마를 어디까지 키우는가 — H3처럼 `contract_assessment`
   전체를 담는가, 아니면 규칙 3이 요구하는 최소 필드만 담는가?
3. B안을 택할 경우 규칙 2의 **evidence 판독 규율**(온톨로지적 성격을 명시하지
   않는 구현 서술은 direct_support가 아니다)을 보존하는가, 버리는가?

---

## 5. Q4 (비차단) — 사전등록한 보조 조건의 사후 승인 요청

§4.2의 구멍을 발견하고, **진단을 한 건도 돌리기 전에** 아래 문안을
`PREREGISTRATION.md` §11.2a에 등재했다. verbatim:

> If all four diagnostic cells fall into the same modal category, the
> diagnostic does not establish anchor noninterference. In that case, a null
> main result is uninterpretable with respect to anchor ceiling effects.
>
> This rule is not an additional trial, not a post-hoc exclusion, and not a
> new success criterion. It is a pre-freeze interpretability condition for
> the diagnostic gate.

**이것이 판정문 밖 항목임을 밝힌다.** 승인·수정·철회를 요청한다.

성질을 분명히 해 둔다:

- **새 합격 기준이 아니다.** §11.2의 차단 규칙을 대체하지 않고, 실행을 막지도
  않는다. 그 규칙이 **부재**를 반환했을 때 그 부재가 무엇을 의미하지 **않는지**를
  못박을 뿐이다
- 운영 세션의 최초 초안은 이것을 "네 셀이 동일하면 본 코호트를 막는다"는
  **차단 규칙**으로 썼다가 폐기했다. 그러면 외부 판정에 없는 합격선을 운영
  세션이 신설하는 셈이기 때문이다
- 추가 호출 0건. 이미 사전등록된 20건을 다르게 **읽는** 조항이다

같은 커밋에 배치 규약도 등재했다(전송 한도 대응): 20건을 **arm 단위로**
10+10으로 나눈다. §11.2의 비교가 전부 **arm 내부** 앵커 대비이므로 arm 단위
배치는 각 대비를 한 배치 안에 온전히 담는다. arm이 배치와 교란되지만 진단은
arm 간 비교를 판정 근거로 쓰지 않는다. **배치 1의 결과를 보고 배치 2를 바꾸지
않는다**도 함께 등재했다.

---

## 6. 넘을 수 없는 제약

1. 모델에게 전달 가능한 evidence 필드는 `evidence_id`/`source_kind`/`text`
   3개뿐이다. liveness·supersession·qualification profile을 모델에 노출하면
   조작 변수가 오염된다
2. E2.4의 `_surface.py`·`decision_schema.json`·`contract_prompt.md`는
   **불변**(D-H1a-1=B). H1a는 전용 사본으로만 작업한다
3. hidden correctness oracle과 인증 밴드를 두지 않는다(D-H1a-4=C)
4. 행동 코더는 `rationale`을 읽지 않는다(P5). 어떤 안을 택하든 코더가 산문을
   판정해야 하는 형태가 되면 안 된다
5. 현재 **실행된 trial 0건.** 스키마·프롬프트·사전등록 어느 것을 바꿔도
   재동결 비용이 없다. 이 조건은 판정 후 첫 trial과 함께 사라진다

---

## 7. 회신 형식

```text
DESIGN DECISION — H1a prompt surface
decided_by:
date:

Q3 (프롬프트 표면 구성):   <A|B|C|D>   근거:

  Q3.1 규칙 3의 "그럴듯하다"가 recency/authority를 포괄하는가:  <예|아니오|판정 보류>
  Q3.2 (A안일 때) 스키마 확장 범위:
  Q3.3 (B안일 때) 규칙 2의 evidence 판독 규율 보존 여부:

Q4 (보조 해석가능성 조건):  <승인|수정|철회>   근거:
  (수정이면 대체 문안을 그대로 적어 주십시오)

deferred:
  <항목 ID>: <사유 / 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약>

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```

---

## 부록 A — embed된 원문 (판정 근거)

### A.1 서문 (block L1-17, verbatim)

```
너는 MCP 클라이언트 agent다.

입력은 repo-derived evidence packet이다. 이 packet은
goodand/concept-gate-taxonomy 저장소의 특정 commit에서 추출된 evidence_items,
candidate_concepts, server_response만 포함한다.

이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.

모델의 책임은 evidence text가 해당 concept/feature의 온톨로지적
성격을 명시적으로 지지하는지, 그리고 evidence 간 의미 충돌이
있는지를 판정하는 것이다.

너의 목표는 정답을 추측하는 것이 아니라, evidence packet만으로 현재 상태를
확정할 수 있는지, 보류해야 하는지, 또는 수리해야 하는지를 계약에 맞게
판정하는 것이다.
```

### A.2 규칙 1 (block L20-26, verbatim) — Q1이 지정한 조작 대상 포함

```
1. packet 밖 지식 사용 금지.
   - 일반 온톨로지 지식, OWL/GUFO 배경지식, 코드베이스에 대한 기억, 이전 대화
     맥락을 사용하지 마라.
   - evidence_items에 없는 정보가 필요하면 abstain해야 한다.
   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를
     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.
```

Q1=B에 따라 **마지막 불릿 2줄 전체**와 서문의
`모델은 출처의 liveness나 우선순위를 재판정하지 않는다.`가 REMOVED arm에서
삭제된다. 나머지는 양 arm 공통.

### A.3 규칙 3 (block L54-68, verbatim)

§4.1에 전문을 인용했다.

### A.4 꼬리 (block L109-113, verbatim)

```
출력은 decision_schema.json의 evidence_contract_v1 schema를 따른다.

payload:
{payload_json}
```

`{payload_json}` 자리에 whitelist 빌더가 만든 payload가 들어간다. H1a payload는
`candidate_concepts`와 `evidence_items` **2키뿐**이다(`server_response` 제거됨).
