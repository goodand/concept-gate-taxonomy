# DESIGN DECISION — D-E2E-v1-34 (referential ∃ 경계: 증거 실사의 판정)

- 수신: 2026-08-24 · 발신: 외부 설계 담당(저장소 접근 없음, Wolfram 검증 명시)
- 사슬 항법: 이전 [[DESIGN_DECISION_d33_claim_status|D-33-V]] · **D-34** · 다음 (없음) · 색인 [[RULING_CHAIN_INDEX]]
- 원 상신: [[DESIGN_REQUEST_referential_existential_qualification|Q34]] + 보충 [[DESIGN_REQUEST_referential_boundary_corpus_scale|Q34-B]]
- `VERBATIM_SHA256: 9b58379b61294da13ebd6079c6b3c37402c9e0679ae189246fe7fbe41cb91a08`
  (범위: BEGIN 다음 개행 ~ END 직전 개행 **제외** — D-30 이후 규약)

## 판정 요약 (우리 요약 — 정본은 §A)

- **Q34의 성격을 그대로 유지하라**: 경계를 정하는 작업이 아니라 **경계를 정할
  만큼 gold가 증거를 기록하는지 조사하는 작업**이다. `conclusion:
  insufficient_evidence` · `immediate_projection: forbidden` ·
  `operational_patch: forbidden` · `dispatch: blocked`.
- **(a) 기각.** "FOLIO가 지시 표현을 상수로 두므로 PMB 대응물도 measurand
  밖"은 **corpus 규약을 semantic authority로 승격**시키는 것이다. 현재 증거로
  갈 수 있는 곳은 `PMB ── representation A` / `FOLIO ── representation B`까지고
  거기서 semantic class로 가는 다리가 없다.
- **우리 framing을 대칭으로 고치라는 지시**: "두 source가 반대로 인코딩한다"를
  더 엄밀하게 —

  > PMB와 FOLIO는 유사한 participant-like material에 서로 다른 formal
  > representation을 쓸 수 있고, **FOLIO의 constant 사용 자체가 referentiality의
  > 충분한 증거가 아니다.**

  그리고 **반대 방향도 함께 인정해야 한다**: `PMB existential binder ≠ genuine
  quantificational force`. 우리는 앞쪽만 정정했고 뒤쪽은 명시하지 않았다.
- **synset은 식별 함수가 아니다**: 하나의 observable label이 여러 latent
  class에 대응하므로 `if synset == person.n.01: referential = …` 규칙의 근거가
  없다. 우리 실측(세 부류 걸침)이 그 판단의 근거로 채택됐다.
- **네 번의 proxy 실패를 "원리적 불가"로 확대하지 않은 것**과 **116 상수를
  semantic gold로 승격하지 않은 것**을 유지하라고 했다. 후자는 Q34-B의
  자기 정정을 지목한다 — 그 동일시가 D-33이 금지한
  `representation → semantics leap`이다.
- **다음 단계는 분류기가 아니다**: 먼저 **독립적인 semantic qualification을
  제공할 수 있는 source/evidence가 무엇인지 결정**해야 한다. 순서는
  `semantic definition → qualification evidence → measurement implementation`
  이고, 그 역순(도구 능력 → 의미 정의)이 D-33의 경고다.

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
Wolfram으로 Q34의 **논리적으로 검증 가능한 부분과 의미론적으로 검증할 수 없는 부분을 분리해서** 확인했습니다. 결론은 상당히 명확합니다.

## 결론

**Q34의 현재 framing은 유지하는 것이 맞습니다.**

즉 이것은:

> `REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1`의 경계를 지금 정하는 작업

이 아니라,

> **그 경계를 독립적으로 정할 수 있을 만큼 gold가 어떤 증거를 기록하고 있는지 조사하는 작업**

으로 남겨야 합니다.

그리고 현재 자료만으로는 **semantic boundary를 구현할 근거가 부족합니다.**

---

## 1. Wolfram이 확정한 것

### ① existential binder를 단순히 제거할 수 없다

다시 유한 domain에서 확인했습니다.

예를 들어:

```text
P = {False, False}
B = {False, True}
```

이면

```text
∃x(P(x) ∧ B(x)) = False
```

인데 제한식을 제거하면:

```text
∃x B(x) = True
```

가 됩니다.

따라서:

```text
∃x[P(x) ∧ B(x)]
        ↓
      B(x)
```

같은 변환은 일반적으로 truth-preserving하지 않습니다.

**source type: Wolfram-grounded**

따라서 Q34가 `referential ∃`를 찾더라도 그것을 **논리적으로 불필요한 ∃라고 단정해서 제거할 수는 없습니다.**

---

## 2. PMB의 synset은 경계의 충분조건이 아니다

Q34의:

```text
person.n.01
 ├─ quantificational
 ├─ referential
 └─ common noun
```

이라는 실측은 중요합니다.

Wolfram의 논리적 관점에서도, 하나의 observable label이 여러 latent class에 대응한다면:

```text
synset → semantic class
```

라는 결정 규칙은 식별 함수가 아닙니다.

따라서:

```yaml
if synset == person.n.01:
    referential = ...
```

같은 규칙을 만들 근거가 없습니다.

**source type: prompt-given corpus audit + Wolfram-grounded identification analysis**

---

# 3. 가장 중요한 것은 FOLIO 결과의 해석입니다

여기서는 Q34의 문장을 **조금 수정하는 것을 권합니다.**

현재 문서에는:

> PMB와 FOLIO가 같은 언어 현상을 서로 반대로 인코딩한다.

는 framing이 있습니다.

그런데 §7에서 이미 발견했습니다:

> FOLIO 상수 116건 중 많은 수가 실제 지시 표현인지 결정할 수 없다.

그리고 `music`, `stonefish` 같은 일반 명사도 상수로 들어갑니다.

따라서 더 엄밀한 표현은:

> **PMB와 FOLIO는 동일하거나 유사한 participant-like material에 대해 서로 다른 formal representations를 사용할 수 있으며, FOLIO의 constant 사용 자체는 referentiality의 충분한 증거가 아니다.**

입니다.

즉:

```text
FOLIO constant
    ≠
referential expression
```

입니다.

반대로:

```text
PMB existential binder
    ≠
genuine quantificational force
```

도 자동으로 성립하지 않습니다.

이 양쪽을 모두 인정해야 합니다.

---

# 4. 따라서 cross-source evidence가 보여주는 것은 이것입니다

현재 증거로 안전하게 말할 수 있는 것은:

```text
PMB representation
    ↓
existential binder

FOLIO representation
    ↓
constant/entity
```

라는 **encoding difference**입니다.

하지만 다음 inference는 아직 금지됩니다.

```text
PMB ∃
 ↓
referential
 ↓
measurand 밖
```

또는:

```text
FOLIO constant
 ↓
referential
 ↓
measurand 밖
```

둘 다 semantic bridge가 없습니다.

즉 Q34의 핵심 발견은 **“경계를 찾았다”가 아니라 “현재 gold representation만으로는 경계를 자동으로 읽을 수 없다”**입니다.

**source type: prompt-given + Wolfram-grounded inference**

---

# 5. §5의 표는 오히려 Q34를 강하게 만듭니다

특히 이 구분이 중요합니다.

| 조건                     | 기록됨                            | 기록되지 않음                     |
| ---------------------- | ------------------------------ | --------------------------- |
| referent introduction  | surface token / constant 여부    | 실제 referent introduction 판단 |
| quantificational force | `every`, `some`, `no` 등의 표면 정보 | semantic force              |
| scope-bearing role     | binder 위치                      | semantic scope 여부           |
| representation         | SBN role / FOL term type       | 의미론적 분류                     |
| semantic class         | synset                         | synset으로 해결되지 않는 경계         |

여기서 결론은:

> **measurement apparatus가 semantic boundary를 이미 가지고 있지 않다.**

입니다.

그리고 이것은 D-33의 가장 중요한 경고와 정확히 연결됩니다.

```text
tool capability
      ↓
semantic definition
```

이 순서로 가면 안 됩니다.

반드시:

```text
semantic definition
      ↓
qualification evidence
      ↓
measurement implementation
```

이어야 합니다.

현재 Q34는 첫 번째 단계의 **증거 존재 여부만 조사**하고 있습니다.

---

# 6. 네 번의 proxy 실패를 "원리적 불가능"으로 확대하면 안 됩니다

이 부분은 현재 문서가 잘 조절되어 있습니다.

다음은 말할 수 있습니다.

```text
현재 proxy 시도들
        ↓
안정적인 boundary extraction 실패
```

하지만 다음은 말할 수 없습니다.

```text
현재 proxy 실패
        ↓
referential boundary는 원리적으로 정의 불가능
```

따라서 §4의 현재 문구:

> `"현재 시도한 표면·구문 proxy로는 경계를 안정적으로 추출할 수 있다는 증거가 없다"`

가 정확합니다.

**source type: model inference grounded in supplied experiments**

---

# 7. Q34에서 특히 잘한 부분: FOLIO의 116건을 semantic gold로 승격하지 않은 것

이건 유지해야 합니다.

116건이라는 숫자가 있어도:

```text
116 constants
```

에서:

```text
116 referential expressions
```

를 추론할 수 없습니다.

Q34가 뒤에서 이를 정정한 것은 중요합니다.

즉 숫자는:

```text
constant usage frequency
```

이지:

```text
referential-expression frequency
```

가 아닙니다.

이 둘을 동일시하면 Q34 자체가 D-33에서 금지한 **representation → semantics leap**을 하게 됩니다.

---

# 8. control에 관한 결론도 그대로 유지

논리적으로:

```text
Eligibility excludes X
        +
PASS on eligible set
        ↓
no evidence about X
```

입니다.

따라서:

> control 5/5 PASS가 participant-containing material에 대한 qualification을 인증한다.

는 결론은 만들 수 없습니다.

**source type: logical inference**

---

# 9. 그래서 (a)는 지금 채택하면 안 됩니다

Q34의 선택지:

> FOLIO가 지시 표현을 constant로 두므로 PMB 대응물을 measurand 밖으로 보자.

이것은 **corpus convention을 semantic authority로 승격시키는 것**이 됩니다.

현재 증거로 가능한 것은:

```text
PMB ── representation A
FOLIO ── representation B
```

까지입니다.

그 다음:

```text
A/B
 ↓
semantic class
```

를 연결할 증거가 없습니다.

따라서 `(a)`는 현재 기각하는 편이 맞습니다.

---

# 10. Q34의 현재 상태

제가 최종적으로 권고하는 상태는 다음입니다.

```yaml
D_E2E_v1_34:

  purpose:
    evidence_audit_for_referential_existential_boundary: true

  semantic_boundary_definition:
    performed: false

  PMB:
    surface_evidence_recorded: true
    synset_alone_identifies_boundary: false

  FOLIO:
    constant_usage_recorded: true
    constant_alone_identifies_referentiality: false

  current_proxy_classifiers:
    stable_boundary_extraction_demonstrated: false

  cross_source_difference:
    encoding_difference: confirmed
    semantic_equivalence_or_priority: insufficient_evidence

  control:
    certifies_excluded_domain: false

  immediate_projection:
    forbidden

  operational_patch:
    forbidden

  dispatch:
    blocked

  conclusion:
    insufficient_evidence
```

## 한 문장 판정

**Q34가 보여주는 것은 “referential ∃를 어떻게 정의할 것인가”가 아니라, 현재 PMB/FOLIO gold가 그 의미론적 경계를 직접 기록하지 않으며, corpus의 표현 방식 자체를 semantic authority로 사용해서는 안 된다는 것입니다.**

따라서 다음 단계 Q34 이후에 필요한 것은 **새로운 분류기를 만드는 것**이 아니라, 먼저 **독립적인 semantic qualification을 제공할 수 있는 source/evidence가 무엇인지 결정하는 것**입니다.

이 점에서 이번 Q34는 D-33의 `operational_patch: forbidden`을 오히려 더 강하게 뒷받침합니다.
<!-- VERBATIM-END -->

---

# B. 우리 수신 검증 (2026-08-24)

정본을 먼저 저장한 뒤 검증했다(G123 이후 규율). 판정이 **우리 문서 두 곳의
수정을 요구**했고 둘 다 적용했다. 그리고 검증 과정에서 **우리 문서의 세 번째
오해 소지**를 스스로 발견했다.

## B.1 대칭 주장 — 판정 §3이 요구한 방향을 실측했다 (**신규**)

판정은 우리가 한쪽만 고쳤다고 지적했다. 우리는 `FOLIO constant ≠ referential
expression`을 Q34-B에서 정정했으나 **반대 방향**(`PMB existential binder ≠
genuine quantificational force`)은 명시하지 않았다. PMB gold 12,053 전수로
그 방향을 실측했다.

결박자가 붙은 지시 후보 노드 **15,810개**의 표면 유형(닫힌 목록 세 개):

| 표면 유형 | 건수 | 무엇을 뜻하는가 |
|---|---:|---|
| 양화 한정사(24종) | **395** (2%) | 결박자가 **진짜 양화력**을 갖는다 → 결박자를 일괄 제거하면 실제 scope 연산자를 지운다 |
| **인칭·소유 대명사**(18종) | **7,430** (47%) | 결박자가 있으나 양화 표지가 없다 |
| 지시사(4종) | **271** (2%) | 같음 |
| 그 외 | 7,714 (49%) | 이 목록 조합에서 미분류 |

**분류 이름 정정**: 두 번째 행을 처음 "인칭 대명사"라고 적었으나 내가 쓴
목록에는 **소유격**(`my`·`your`·`his`·`its`·`our`·`their`)이 포함돼 있었다.
이름이 목록과 달랐다.

예: 양화 `person.n.01←'Everyone'` · 대명사 `person.n.01←'You'` ·
`female.n.02←'she'` · 지시사 `entity.n.01←'This'`.

**양방향 모두 증인이 있다.** 395개는 결박자 제거가 scope를 파괴하는 사례이고,
7,701개는 결박자 존재가 양화력의 증거가 아닌 사례다. 판정 §3의 대칭 요구가
**실측으로 확인**됐다.

## B.2 우리 문서의 세 번째 오해 소지 — **어떤 비율도 단일 수치로 보고할 수 없다**

Q34-B는 닫힌 목록을 **양화 어휘로만** 잡아 "미결정 96%"라고 적었다. 처음 나는
그것을 "대명사·지시사를 더하면 51%가 식별된다"로 정정했다. **그 정정도
틀렸다** — §B.6이 보이듯 비율은 목록 구성의 함수이고 **2%에서 51%까지
움직인다.**

그러므로 결론은 "96%가 아니라 51%"가 아니다. 결론은 이것이다:

> **닫힌 목록의 유형화 비율은 목록 구성에 25배 민감하므로, 어떤 단일 비율도
> 재료의 성질로 보고할 수 없다.** 방향("경계를 목록으로 그릴 수 없다")은
> 유지되고 오히려 강해진다 — 대표 수치가 그만큼 흔들리는 유형을 의미론적
> 경계라고 주장할 근거는 없다(판정 §4의 `representation → semantics` 금지).

**§B.6이 이 절을 무효화했고 그 사실을 여기 적는다.** 처음 판의 §B.2는
"정확한 서술은 51%다"라고 적었는데, 그것은 §B.6이 금지한 형태였다 — **같은
문서 안에서 앞 절이 뒤 절과 모순**했다. 적대 검증이 그 모순을 잡지 못하고
§B.2를 SOUND로 승인했다(§B.9).

## B.3 판정이 재확인한 것 — 재실측하지 않고 인용한다

- **논리 주장**(`∃x[P∧B]` 대 `∃x[B]`): 판정이 든 반례
  `P={F,F}, B={F,T}`는 **우리 D-33 §B.2의 첫 반례와 동일**하다. 도구가 다른
  두 경로가 같은 증인에 도달했다 — 재실측하지 않고 그 사실을 기록한다.
- **synset은 식별 함수가 아니다**: 우리 실측(`person.n.01`이 양화·지시·
  보통명사 세 부류에 걸침)이 그 판단의 근거로 채택됐다.
- **control 결론**: `Eligibility excludes X + PASS on eligible set → no
  evidence about X`. D-33 §9와 동일.
- **4회 proxy 실패를 원리적 불가로 확대하지 않은 것**과 **116 상수를 semantic
  gold로 승격하지 않은 것**을 유지하라고 했다. 둘 다 D-33-V의 정정으로
  이미 반영돼 있다.

## B.4 적용한 문서 수정 2건

| 대상 | 수정 |
|---|---|
| Q34 §1 framing | "두 source가 반대로 인코딩한다" → 판정이 준 대칭 문장으로 교체하고 **양방향 부등식**(`FOLIO constant ≠ referential` · `PMB binder ≠ quantificational force`)을 함께 실었다 |
| Q34-B §2·§4 | "미결정 96%"에 B.2의 정정을 붙였고, "(a)의 형태가 바뀐다"를 **"(a) 기각"**으로 갱신했다 — 판정이 우리보다 강하게 결론했다 |

## B.5 상태 변화

`dispatch: blocked` 유지, `operational_patch: forbidden` 유지, 그리고
**`immediate_projection: forbidden`이 추가**됐다 — `O1_SCOPE_PROJECTION_V3`을
지금 만드는 것이 금지된다.

**다음 행동의 종류가 바뀐다.** 이전 다음 행동은 "경계 실사"였고 그것은 끝났다.
판정이 명한 다음은 **분류기가 아니라 source 결정**이다:

```text
semantic definition  →  qualification evidence  →  measurement implementation
```

첫 항을 채울 **독립적인 semantic qualification 원천**이 무엇인지 정해야 한다.
gold 표현 자체는 그 원천이 될 수 없다는 것이 이 판정의 결론이다.

## B.6 **자기 반증** — "51%"는 재료의 성질이 아니라 내 목록의 함수다

B.1을 적고 나서 목록 구성을 바꿔 재실측했다. 같은 15,810개 토큰이다.

| 목록 구성 | 유형화 | 비율 |
|---|---:|---:|
| 양화만 (Q34-B 원본) | 395 | **2%** |
| 양화 + 인칭(주·목) + 지시 | 6,567 | **41%** |
| ↑ 지시사 제외 | 6,296 | 39% |
| **양화 + 인칭 + 지시 + 소유** ← B.1이 실제로 쓴 것 | 8,136 | **51%** |
| ↑ + 재귀 추가 | 8,188 | 51% |

**2%에서 51%까지 움직인다.** 그러므로 "닫힌 목록이 51%를 유형화한다"는 문장을
**재료에 대한 사실로 보고해서는 안 된다** — 그것은 목록에 대한 사실이다.

이것이 D-34의 결론을 **약화시키지 않고 강화한다**: 목록 선택이 대표 수치를
25배 흔든다면, 그 목록으로 얻은 유형이 의미론적 경계라고 주장할 근거는 더
없다(판정 §4의 `representation → semantics` 금지).

**내 방어가 불충분했다.** 나는 "대명사를 referential이라 부르지 않았다"로
방어했으나, **어떤 표면형을 한 유형으로 셀지 고르는 행위가 이미 부분적 경계
결정**이다. 목록을 공개한 것은 필요하지만 충분하지 않다 — **범위 민감도를
함께 보고해야** 읽는 사람이 그 수치를 재료의 성질로 오독하지 않는다.

이 세션에서 같은 형태의 정정이 **네 번째**다(Q33 §1 → Q34-B §2 → B.2 → 여기).
네 번 다 More READ가 드러냈고, 네 번 다 **내가 만든 수치의 함의가 재료보다
내 선택에 더 의존**하고 있었다.

## B.8 놓친 하중 주장 — 판정 §5의 apparatus 경고 (적대 검증이 적발)

§B 초판이 판정 §5의 결론을 다루지 않았다. 그 문장은 이것이다:

> **measurement apparatus가 semantic boundary를 이미 가지고 있지 않다.**

이것이 §B.6의 자기 반증과 **같은 것을 말한다**. 우리 apparatus가 기록하는
것은 synset·표면 토큰·결박자 위치·SBN role·FOL 항 종류이고, 그 어느 것도
의미론적 부류가 아니다. 그래서 어떤 닫힌 목록을 얹어도 나오는 것은 **관측
유형**이고, 그것을 경계로 쓰려면 apparatus 밖의 권위가 필요하다.

그리고 이것이 **D-33의 순서 경고와 직결**된다:

```text
금지:  tool capability     →  semantic definition
필수:  semantic definition →  qualification evidence  →  measurement implementation
```

우리가 목록을 고르고 51%를 보고한 것은 **금지된 방향의 첫 걸음**이었다 —
도구가 셀 수 있는 것으로 유형을 만들고 그 유형을 경계 후보로 제시했다.
§B.6이 그것을 스스로 되돌렸으나, **애초에 그 방향으로 갔다는 사실**이
판정 §5가 경고한 것이다.

**실행 함의**: 다음 단계(source 결정)에서 후보 source를 평가할 기준은
"우리 도구가 그것을 읽을 수 있는가"가 아니라 **"그것이 apparatus 밖에서
의미론적 부류를 기록하는가"**여야 한다. 전자로 고르면 같은 실패다.

## B.9 적대 검증 회신 — blocker 0, 그러나 **모순 하나를 놓쳤다**

설계를 사후 명시해 적대 검증에 올렸다(규율 위반 복구). 결과: blocker 0 ·
major 1 · minor 9, "커밋된 결론 유지" 권고. 유효한 지적 둘을 반영했다 —
§5 apparatus 경고 누락(→ B.8)과 상신서 사후 수정 기록(→ Q34 헤더).

**그러나 §B.2를 SOUND로 승인한 것은 틀렸다.** 그 절은 "정확한 서술은 51%"라고
적고 있었고 §B.6이 그것을 금지했다 — **같은 문서의 앞뒤 모순**이다. 회신은
§B.6을 인용하면서도 그 함의를 §B.2에 적용하지 않았다.

원인의 일부는 내 쪽이다: **적대 검증을 띄운 뒤에 문서를 고쳤다**(§B.6 추가).
검증자가 혼합 상태를 읽었다. G123과 같은 형태의 재발이다 — 그때는 정본이
없는 상태로 띄웠고 이번엔 움직이는 상태로 띄웠다. **규율**: 적대 검증 대상은
띄우는 순간 얼어야 하고, 그 사이에 내가 발견한 것은 **회신 후에** 반영한다.

## B.7 남은 한계

- 대명사·지시사를 "referential"이라 부르지 **않았다**. 표면 토큰이 목록에
  있다는 관측만 적었다 — 그 의미론적 지위가 바로 미정이다.
- 위 민감도 표도 **내가 고른 다섯 조합**이다. 다른 조합에서 51%를 넘을 수
  있다. 상한을 주장하지 않는다.
