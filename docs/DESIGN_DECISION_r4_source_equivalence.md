# DESIGN DECISION — D-E2E-v1-37 (R4는 기제 동일성이 아니라 measurand 비교가능성이다)

- 수신: 2026-08-30 · 발신: 외부 설계 담당(저장소 접근 없음, Wolfram 검증 명시)
- 요청서: [[DESIGN_REQUEST_r4_source_equivalence|Q37]]
- 사슬 항법: 이전 [[DESIGN_DECISION_independent_verifiability_constraint|D-36]] ·
  **D-37** · 색인 [[RULING_CHAIN_INDEX]] · 상태 정본
  [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 정본 규약: 아래 `VERBATIM-BEGIN`/`END` 사이가 수신 원문이고 그 바이트의
  sha256을 기록한다(D-30 이후 규약 — **마지막 개행 제외**).
- `VERBATIM_SHA256: 5274ece0a99ba4e482aa260c6c66899dc6488ded1d27fad762ba4861887015c9`

<!-- VERBATIM-BEGIN -->
## Q37 판정

**결론: R4의 기본 읽기는 B가 맞다. 다만 B를 `qualification 결과의 동일성`으로 정의하면 안 된다.**

즉,

> **R4는 동일한 annotation mechanism을 요구하는 것이 아니라, 서로 다른 표현 형식의 source가 동일한 measurand에 대해 상호 번역 가능한 방식으로 동등한 qualification을 제공함을 요구한다.**

그리고 이 qualification의 동등성은 **출력의 표면적 일치가 아니라, 먼저 독립적으로 규정된 measurand/qualification 기준에 대한 보존성**으로 입증되어야 한다.

따라서 A는 **필요 이상으로 강하고**, 단순한 B′("결과가 같아 보인다")는 **순환적**이다.

### Wolfram 검증이 확정하는 논리적 부분

두 source의 qualification을 각각 `QP`, `QF`, 독립 검증 가능성을 `R2P`, `R2F`라고 놓으면,

```text
R4B := QP ↔ QF
```

만으로

```text
R2P ∧ R2F
```

가 따라오지 않는다.

Wolfram의 만족가능성 분석에서도

```text
QP = True
QF = True
R2P = True
R2F = False
```

같은 모형이 존재하며, 양쪽 qualification이 같더라도 한쪽의 독립 검증 가능성은 실패할 수 있다. 즉 **R4와 R2는 논리적으로 독립인 축**이다.

또한 Wolfram의 정리 증명/Boolean equivalence 기능이 보여주듯, 서로 다른 표현은 조건부로 동등할 수 있지만 그 조건 자체가 별도로 주어져야 한다.

---

## (a) R4의 올바른 읽기

### A — 기제 동일성

```text
mechanism(PMB) = mechanism(FOLIO)
```

이는 **cross-source comparability의 충분조건에 가까운 강한 제약**이지만, measurand 자체의 정의에서 필수적인 조건은 아니다.

예를 들어 SBN과 FOL처럼 표현 형식이 다른 두 체계가 동일한 의미적 속성을 독립적으로 판정할 수 있다면, 형식이 다르다는 이유만으로 비교 가능성을 배제할 논리적 이유는 없다.

따라서:

```yaml
R4A:
  status: rejected_as_general_requirement
  reason: unnecessarily_strong
```

### B — measurand 동등 qualification

이쪽이 올바른 방향이다.

그러나 다음은 충분하지 않다.

```text
PMB output == FOLIO output
```

왜냐하면 **무엇을 동일하다고 볼 것인지가 이미 qualification 정의를 필요로 하기 때문**이다.

따라서 B를 정확히 쓰면:

```text
R4 =
  서로 다른 encoding을 허용하되,
  독립적으로 정의된 동일 measurand에 대해
  각 source의 qualification이 동등한 판정 기능을 보존한다.
```

즉 R4는 **mechanism equivalence가 아니라 qualification equivalence**다.

그리고 A/B 이분법 자체도 최종 ontology로 동결해서는 안 된다. 더 일반적으로는:

```text
R4 = cross-source measurand comparability
```

로 두고,

```text
mechanism identity
qualification equivalence
translation-preserving equivalence
```

를 그 comparability를 달성하는 서로 다른 가능 조건으로 취급하는 것이 더 안전하다.

---

## (b) "의미적으로 동등"은 무엇으로 입증하는가?

여기가 Q37의 핵심이다.

세 층을 다시 분리해야 한다.

| 층                    | 질문                                       |
| -------------------- | ---------------------------------------- |
| **L1 Encoding**      | source가 어떤 형식으로 표현하는가?                   |
| **L2 Correctness**   | 그 표현이 source의 annotation/논리 규약에 맞는가?     |
| **L3 Qualification** | 그 표현이 우리가 재려는 measurand를 실제로 qualify하는가? |

PMB의 `Name`, `ANA`와 FOLIO의 constant 같은 것은 우선 **L1의 증거**다.

그것이 정확한 annotation이라는 것은 L2 문제다.

그것이 `referentiality`라는 measurand를 qualify한다는 것은 **L3 문제**다.

따라서:

```text
L1 ≠ L2 ≠ L3
```

이고,

```text
PMB L1 ≈ FOLIO L1
```

또는

```text
PMB annotation = FOLIO annotation
```

을 보여주는 것만으로 L3을 얻을 수 없다.

### 동등성의 올바른 구조

B를 사용하려면 외부적으로 다음과 같은 기준이 먼저 존재해야 한다.

```text
M = 독립적으로 정의된 measurand

Q_PMB(x) = PMB의 증거가 M을 qualification하는가
Q_FOLIO(x) = FOLIO의 증거가 M을 qualification하는가

R4:
    Q_PMB ≡_M Q_FOLIO
```

여기서 `≡_M`은 **단순 syntactic equality가 아니라 M에 대해 보존되는 equivalence**다.

이것이 Q37에서 말하는 "의미적으로 동등"을 operational patch 없이 표현할 수 있는 최소 형태다.

그리고 바로 이 때문에 **현재 PMB/FOLIO 자료만으로 R4-B를 이미 충족했다고 선언할 수 없다.**

---

## (c) D-34가 FOLIO에 대해 이미 "같은 measurand를 qualify하지 않는다"고 판정했는가?

**아니다. Q37의 §4 연결은 한 단계 과장되어 있다.**

D-34가 실제로 배제한 것은:

```text
FOLIO constant
      ↓
referentiality
```

라는 **충분조건 추론**이다.

즉,

```text
constant ⇒ referential
```

을 semantic authority로 사용할 수 없다는 판정이다.

하지만 이것으로부터 곧바로

```text
FOLIO가 referentiality를 qualification할 수 없다
```

가 나오지는 않는다.

논리적으로:

```text
¬(A ⇒ B)
```

와

```text
¬B
```

는 전혀 다르다.

따라서 Q37 §4의

> "D-34의 문장은 이미 읽기 B의 질문에 대한 부정 답변이다"

라는 해석은 **기각**한다.

더 정확한 상태는:

```yaml
D34_effect_on_R4B:
  proves:
    - FOLIO_constant_is_not_sufficient_evidence_of_referentiality
  does_not_prove:
    - FOLIO_cannot_qualify_referentiality
    - PMB_and_FOLIO_measure_different_measurands
```

이다.

이 구분은 중요하다. 그렇지 않으면 D-34가 금지한 `representation → semantic class` 도약을 이번에는 역방향으로 반복하게 된다.

---

## (d) R4와 R2는 독립인가?

**그렇다. 그리고 이것은 순서 문제까지 해결해 준다.**

R4:

```text
두 source가 같은 measurand를 qualification하는가?
```

R2:

```text
각 qualification의 정확성을 apparatus 밖에서 독립적으로 검증할 수 있는가?
```

는 서로 다른 질문이다.

따라서 네 가지 조합이 원리적으로 가능하다.

| R4   | R2   | 의미                           |
| ---- | ---- | ---------------------------- |
| PASS | PASS | 가장 강한 상태                     |
| PASS | FAIL | 같은 것을 재지만 검증 근거 부족           |
| FAIL | PASS | 각자 검증 가능하지만 같은 measurand가 아님 |
| FAIL | FAIL | 양쪽 모두 미해소                    |

Wolfram의 반례 모형이 정확히 **R4 PASS / R2 FAIL**을 구성한다. 따라서 R4가 R2를 자동 충족한다는 주장은 성립하지 않는다.

반대로 R2도 R4를 보장하지 않는다. **검증 가능하다는 것과 서로 같은 것을 검증한다는 것은 별개**다.

따라서:

```yaml
R2:
  axis: independent_verifiability

R4:
  axis: cross_source_measurand_equivalence

independent: true
```

로 유지하는 것이 타당하다.

---

# 최종 판정

```yaml
D_E2E_v1_37:

  question:
    R4:
      mechanism_identity_or_measurand_equivalent_qualification:
        status: RESOLVED_AT_CONCEPTUAL_LEVEL

  R4:
    preferred_reading:
      cross_source_measurand_comparability: true

    mechanism_identity:
      required: false
      status: rejected_as_general_requirement

    qualification_equivalence:
      required: true
      but:
        syntactic_output_equality: insufficient
        corpus_encoding_conformity: insufficient

    equivalence_must_be:
      relative_to:
        independently_defined_measurand
      preserve:
        qualification_of_that_measurand

  D34_connection:
    constant_not_sufficient_for_referentiality: confirmed
    FOLIO_cannot_qualify_referentiality: not_established
    same_measurand_is_not_disproved_by_D34: true

  R2:
    independent_of_R4: true
    R4_does_not_imply_R2: confirmed
    R2_does_not_imply_R4: true

  operational_consequence:
    boundary_definition: still_unresolved
    immediate_projection: forbidden
    operational_patch: forbidden
    dispatch: blocked
```

### 한 문장

**R4는 "두 corpus가 같은 주석 기제를 써야 한다"가 아니라 "형식이 달라도 독립적으로 정의된 동일 measurand에 대해 동등한 qualification을 제공함을 입증해야 한다"이며, 그 동등성 자체는 R2의 독립 검증 가능성과 별개의 요건이다.**

따라서 **Q37은 R4의 개념을 정리하지만, 현재 PMB/FOLIO 자료로 referential ∃의 경계를 확정하거나 `O1_SCOPE_PROJECTION_V3`을 발동할 근거는 추가하지 않는다.**
<!-- VERBATIM-END -->

---

# 운영 세션의 수신 검증 (2026-08-30)

## 0. 결론 — **판정이 옳고, 내 추론이 기각됐다**

Q37 (c)로 내가 직접 물었던 항목이 **기각**으로 돌아왔다. 판정문이 인용한
문장은 내가 실제로 쓴 것이고(`DESIGN_REQUEST_r4_source_equivalence.md:77-79`),
그 추론은 타당하지 않다. 구제 경로를 찾아봤고 없었다(§2).

## 1. 인용 정확성 — 판정이 내가 쓴 것을 기각했는가

판정문이 인용한 문장:

> "D-34의 문장은 이미 읽기 B의 질문에 대한 부정 답변이다"

상신문 원문 `:77-79`:

> **우리 읽기(판정 요청 대상)**: D-34 의 그 문장은 이미 읽기 B 의 질문에 대한
> 부정 답변이다 — FOLIO 는 referentiality 라는 measurand 를 qualify 하지 **않고**,
> 그것과 상관될 수 있는 다른 것을 표기한다.

**일치.** 판정은 내가 쓴 것을 기각했지 오독하지 않았다.

## 2. 논리 판정의 타당성 — 구제 경로를 찾아봤고 없다

내 추론의 형식:

```text
전제  D-34: ¬(constant ⇒ referential)
결론  FOLIO 는 referentiality 를 qualify 할 수 없다   ← ¬B
```

이 추론이 **살아나는 유일한 길**은 D-34가 "FOLIO의 다른 자질도 referentiality를
qualify하지 못한다"를 별도로 확립한 경우다. 확인했다 — **그런 문장은 없다.**
오히려 반대다:

- `DESIGN_DECISION_referential_existential_qualification.md:447` — "다음 단계
  Q34 이후에 필요한 것은 … **독립적인 semantic qualification을 제공할 수 있는
  source/evidence가 무엇인지 결정하는 것**"
- 같은 문서 `:539` — "첫 항을 채울 **독립적인 semantic qualification 원천**이
  무엇인지 정해야 한다"

D-34는 source 결정을 **열어 뒀다.** 닫은 적이 없다. 판정 (c) 수용.

## 3. 이것이 단순 논리 오류가 아닌 이유 — **금지된 도약의 역방향**

D-34가 금지한 다리는 `representation → semantic class` 였다. 나는 그 다리를
**반대 방향으로 건넜다**:

```text
D-34 가 금지    representation ──▶ semantic class   (constant ⇒ referential)
내가 한 것      ¬(그 다리)      ──▶ ¬(semantic qualification 가능)
```

판정문이 이것을 정확히 지목했다 — "그렇지 않으면 D-34가 금지한
`representation → semantic class` 도약을 이번에는 역방향으로 반복하게 된다".

**금지된 추론의 반대편이 안전하다고 착각한 것**이고, 회고 패턴 원장에 올릴
새 형태다. 기존 P24(정정이 같은 결함을 실어 옴)와 가깝지만 다르다 — 이번엔
정정이 아니라 **금지 그 자체를 재료로 삼아** 같은 다리를 건넜다.

## 4. 대칭 결함 탐색 — **깨끗하다**

D-34는 양방향 부등식을 판정했다(`FOLIO constant ≠ referential` ·
`PMB existential binder ≠ genuine quantificational force`). PMB 쪽 대칭 위치에서
같은 역방향 도약을 했는지 찾았다:

| 위치 | 내용 | 판정 |
|---|---|---|
| `..._referential_existential_qualification.md:26-27` | "반대 방향도 함께 인정해야 한다 … 우리는 앞쪽만 정정했고 뒤쪽은 명시하지 않았다" | 지적을 받은 기록 |
| 같은 문서 `:463` | 뒤쪽 정정 반영 | 정정 완료 |
| 같은 문서 `:523` | 양방향 부등식을 함께 실었다 | 기록 정확 |

**PMB 쪽에서 같은 도약을 한 흔적 0건.** 결함은 이번 상신문 §4 하나다.

## 5. 선행 판정과의 정합성

| 검사 | 결과 |
|---|---|
| D-36 §4 삼층(L1/L2/L3) 정의 | D-37 (b)의 표와 **일치**. 새 어휘 아님 |
| 우리 문서가 `R4 ⇒ R2` 를 주장한 적 있는가 | **0건** |
| 금지 사항(`dispatch: blocked` · `operational_patch` · `immediate_projection` · V3 제작) | D-37이 **전부 유지**. 우리 상태와 충돌 0 |

**단, 재검토가 필요한 항목 1건.** `DESIGN_DECISION_independent_verifiability_constraint.md:307`
이 인용한 우리 Q36 주장:

> 다른 주석 corpus는 R1·R4를 채우고 R2에서 막힌다.

D-37이 R4를 **조인다**(단순 기제 동일성이 아니라 M 상대적 동등성). 조인 정의
아래에서 "다른 corpus가 R4를 채운다"가 여전히 성립하는지는 **재검토 대상**이다.
이것은 판정문의 결함이 아니라 우리 주장의 지위 변화다.

## 6. 가장 중요한 결과 — **R4 는 M 의 상류가 아니라 하류다**

D-37은 R4-B를 이렇게 정의한다:

```text
M = 독립적으로 정의된 measurand
R4:  Q_PMB ≡_M Q_FOLIO
```

즉 **R4는 M 없이는 평가 자체가 불가능하다.** 그런데 M은 D-34가 이미 이름
붙인 3항 사슬의 **첫 항**이고, 그 첫 항이 비어 있다는 것이 D-34의 결론이다
(`:536`):

```text
semantic definition  →  qualification evidence  →  measurement implementation
      ↑ 비어 있음
```

사슬을 거슬러 확인했다 — 같은 첫 항을 가리키는 판정이 둘이다:

| 판정 | 문장 |
|---|---|
| D-33 `:521` | "먼저 '어떤 ∃가 순수한 referential participant binder이고 …'를 **독립적인 qualification rule로 정의**해야 하는 문제" |
| D-34 `:447` | "**먼저 독립적인 semantic qualification을 제공할 수 있는 source/evidence가 무엇인지 결정하는 것**" |

**§9 의 적대적 검증이 이 절을 좁혔다.** D-35·D-36 을 실제로 읽으니 셋이
같은 항을 가리킨다는 그림은 **틀렸다.** D-35 `:510` 은 이렇게 말한다:

> 다음 단계는 normalization rule을 만드는 것이 아니라, **`Name`/`ANA`
> annotation의 의미와 정확성을 독립적으로 검증할 수 있는지**를 판정하는 쪽이 맞다

이것은 M 의 **정의**가 아니라 후보 원천의 **독립 검증 가능성**, 즉 R2 방향이다.
D-36 은 그 R2 를 병목으로 형식화했다. 사슬의 실제 궤적은 이렇다:

```text
D-33  M 을 정의해야 한다            ← 첫 항
D-34  M 을 줄 source 를 정해야 한다  ← 첫 항
D-35  그 후보를 독립 검증할 수 있나  ← R2 로 이동
D-36  R2 가 병목이다                ← R2
D-37  R4 는 별개 축이고 M 이 있어야 평가된다
```

**따라서 정정한다** — "사슬 전체가 같은 첫 항을 가리킨다"가 아니라
**"사슬은 D-35 부터 원천·검증(R2) 쪽을 파고들었고 첫 항 자체는 D-34 이후
아무도 채우지 않았다"** 가 실측에 맞는 서술이다. 결론(R4 는 M 의 하류)은
바뀌지 않지만 **근거가 달라졌다.**

**따라서 R4를 풀어 경계로 가려던 방향은 성립하지 않는다.** R4는 M이 생긴
뒤에야 평가되는 축이다. D-37의 `boundary_definition: still_unresolved` 가
이것과 일치한다.

## 7. 잘한 것 하나 — 한계 절이 작동했다

상신문 §7 한계 1항에 이렇게 적었다:

> **읽기 A/B 의 이분법은 우리가 만든 것이다.** 판정문은 두 가능성을 문장으로
> 적었을 뿐 이분법이라고 하지 않았다. 세 번째 읽기가 있을 수 있다.

판정문이 같은 것을 말했다 — "A/B 이분법 자체도 최종 ontology로 동결해서는
안 된다"며 `cross-source measurand comparability` 아래 세 가능 조건으로
재배치했다. **한계를 선언한 항목은 기각당하지 않았고, 선언하지 않고 단정한
항목(§4)이 기각당했다.**

## 8. 이 검증의 한계

- ~~적대적 검증을 거치지 않았다~~ → **§9 에서 복구했다**(2026-08-30, haiku
  조사 agent). 이 한계는 해소됐고 그 결과 §5·§6 이 정정됐다.
- **§5의 D-36 §307 재검토는 하지 않았다** — 항목을 열었을 뿐이다.
- **§6의 D-35·D-36 미확인**은 위에 적은 대로 grep 미검출이다.
- 전수 재실측은 여전히 불가능하다(`pmb_gold` 12,053건 소실, 2026-08-29).
  이 검증은 전부 저장소 문서 대조이므로 영향받지 않는다.


---

# 9. 건너뛴 단계의 복구 — 적대적 검증 (2026-08-30)

§8 이 자백한 대로 `설계의 적대적 검증` 을 건너뛰었다. 사용자 지시("프로토콜을
전수 진행하는 것을 Default로 두되, PASS할 때는 그 이유를 명시하도록 해라")에
따라 **건너뛴 단계를 사후 실행**했다. 근거 축을 다르게 준 haiku 조사 agent 가
§0~§8 을 공격했고, lead 가 판정을 뒤집을 수 있는 항목을 **직접 재실측**했다.

## 9.1 회신 요약과 lead 재실측

| # | 대상 | 회신 | lead 재실측 | 최종 |
|---|---|---|---|---|
| 1 | §1 인용 일치 | CONFIRMED | 재확인 불필요(§1 이 이미 원문 대조) | 유지 |
| 2 | §2 구제 경로 없음 | CONFIRMED (major) | 유지 | 유지 |
| 3 | §4 대칭 결함 0건 | **UNVERIFIABLE** — grep 만으로는 부재 증명 불가 | 회신이 옳다 | **"0건"에서 "grep 범위에서 미검출"로 격하** |
| 4 | §5 `R4⇒R2` 0건 | PARTIAL (major) | 원 출처 확인: 우리 상신문 `DESIGN_REQUEST_independent_verifiability_constraint.md:59` 이고 D-36 `:307` 은 그것의 인용이다 | 출처 보정, 재검토 항목 유지 |
| 5 | §6 "같은 첫 항" | PARTIAL (major) — 인용이 아니라 추론 | **회신이 옳고 내가 틀렸다.** §6 정정 완료 | **정정됨** |
| 6 | §6 D-35·D-36 미확인 | UNVERIFIABLE (major) | 실측함 — D-35 `:510` 은 **다른 것**(R2 방향)을 가리킨다 | **§6 재작성** |
| 7 | §7 한계 절 작동 | CONFIRMED | 유지 | 유지 |
| 8 | **§0~§8 이 판정문 자체의 논리 주장을 검증하지 않았다** | **CONFIRMED (blocker)** | **실측함 — §9.2** | **해소** |
| 9 | §3 새 패턴 | CONFIRMED | 유지 | 유지 |

## 9.2 blocker 해소 — 판정문의 논리 주장을 독립 검증했다

지적이 정확했다. §0~§8 은 **판정문 중 나에 관한 부분만** 검증하고 판정문
자체의 주장은 하나도 보지 않았다. 진리표로 전수 확인했다(4변수 16모형):

| 판정문 주장 | 검증 | 결과 |
|---|---|---|
| `R4B := QP↔QF` 만으로 `R2P ∧ R2F` 가 따라오지 않는다 | R4B 참인 8모형 중 결론 거짓인 **반례 6개** | **CONFIRMED** |
| 지목 모형 `QP=QF=T · R2P=T · R2F=F` 가 반례다 | 그 모형이 반례 집합에 속함 | **CONFIRMED** |
| R4×R2 네 조합이 원리적으로 가능하다 | 네 칸 전부 만족가능 | **CONFIRMED** |
| 역방향 `R2 ⊨ R4` 도 성립하지 않는다 | **반례 2개** | **CONFIRMED** |

**판정문의 논리 부분은 우리 손으로 재현된다.** 이제 "Wolfram 이 그랬다니까"가
아니라 우리가 확인한 것이다.

## 9.3 이 라운드가 드러낸 것 — 나는 **같은 오류를 두 번** 했다

Q37 §4 에서 기각당한 형태는 "추론을 관찰인 것처럼 단정"이었다.
그리고 그 기각을 검증하는 §6 에서 **같은 형태를 다시 했다** — D-33·D-34 두
문장을 읽고 "사슬 전체가 같은 첫 항을 가리킨다"로 일반화했는데, 확인하지 않은
D-35 가 다른 곳을 가리키고 있었다.

차이는 하나다. §4 는 **외부 판정**이 잡았고, §6 은 **적대적 검증**이 잡았다.
건너뛰었다면 §6 은 그대로 남았을 것이고, 다음 세션은 틀린 사슬 그림을 정본으로
읽었을 것이다. **이 절이 그 규약의 값을 실측한 사례다.**

## 9.4 아직 남은 것

- **§4 의 "0건"은 여전히 grep 범위 판정이다.** 회신 지적대로 부재 증명이
  아니다. Obsidian backlink 순회는 하지 않았다.
- ~~§5 의 재검토는 열려 있다~~ → **닫았다**(2026-08-30):
  [[H1A_PROBLEM_ANALYSIS]] §23. 답은 **성립하지 않는다**이고 예상보다 나쁘다 —
  R2 절반은 **D-36 §6 이 이미 정정했는데 우리가 패턴 원장에 전파하지 않았고**
  (6일, 게다가 상신문보다 강한 형태로), R4 절반은 D-37 아래서 **`FAIL` 이
  아니라 `BLOCKED`**(M 이 없어 평가 불가)다. 두 절반이 **같은 가정**에서
  무너졌다: "두 개를 가지면 요건이 자동 충족된다". 신규 G161~G163 · **P26 신설**.
- 회신이 스스로 밝힌 미확인 5건(D-35·D-36 전수 순회, backlink 그래프 등)은
  그대로 남는다.
