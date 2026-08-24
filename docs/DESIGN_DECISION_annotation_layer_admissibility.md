# DESIGN DECISION — D-E2E-v1-35 (role 주석 층의 적격성)

- 수신: 2026-08-24 · 발신: 외부 설계 담당(저장소 접근 없음)
- 사슬 항법: 이전 [[DESIGN_DECISION_referential_existential_qualification|D-34]] · **D-35** · 다음 (없음) · 색인 [[RULING_CHAIN_INDEX]]
- 원 상신: [[DESIGN_REQUEST_annotation_layer_admissibility|Q35]]
- `VERBATIM_SHA256: 618006dba12ec43c30ab53a1f8b9448a8a801a9ba54cee6c4fe1d62b95ffcb12`
  (범위: BEGIN 다음 개행 ~ END 직전 개행 **제외** — D-30 이후 규약)
- **판정자가 스스로 밝힌 한계**: Wolfram `Context` 조회가 **502로 실패**해
  "제공된 Q35 자료 + Wolfram Language 논리 검증"에 한정된 평가다. 이것을
  요약 첫 줄에 적는다 — 판정의 근거 범위가 좁혀졌다는 사실이 판정 내용의
  일부다.

## 판정 요약 (우리 요약 — 정본은 §A)

- **`Name`·`ANA`는 증거로는 적격, semantic authority로는 미확립.**
  `Name_ANA_as_evidence: admissible` / `as_semantic_authority: not_established`
  / `qualification_from_Name_ANA_alone: insufficient_evidence`.
- **FOLIO 상수와는 다른 종류**라고 우리 관찰이 인정됐다: 상수는 "수식에서
  어떤 항 형식을 썼는가"이고 `Name`·`ANA`는 "주석자가 기능을 표시했음"이다.
  그러나 `evidence`에서 `truth`로 가는 단계는 별개다.
- **남은 한 단계가 핵심**: "명명된 개체를 지시한다"와 "O1 scope measurand에서
  제거해야 한다"는 **서로 다른 명제**다. 동일시하면 경계 설정을 다시 corpus
  annotation에 위임하게 된다(D-33이 금지한 형태).
- **Q35의 진짜 발견은 `Name`/`ANA` 자체가 아니라 증거 계층의 발견**이다.
  기존은 `synset + surface → referentiality 추정`이었고 Q34에서 불안정했다.
  이제 `annotation evidence → qualification 후보 증거`가 추가됐다.
- **30% coverage가 결정적 제약**: `Name`/`ANA` 있음 → referential 쪽으로는
  갈 수 있으나 **없음 → non-referential은 불가**다. positive/negative
  비대칭이고 `absence_of_Name_ANA: means_unknown: true`가 증거에 충실하다.
  3값 구조(`QUALIFIED_REFERENTIAL`/`NOT_QUALIFIED`/`NEEDS_AUDIT`)가 자연스럽되
  **지금 채택하라는 뜻은 아니다.**
- **`ANA` 배제는 되돌리지 마라.** in-N이 동결돼 있고, Q35의 발견만으로
  모집단을 바꾸면 **측정 계약을 관측 결과에 맞춰 수정하는 모양**이 된다.
  증거층은 향후 qualification 재료로 보존하고 코호트는 사후 수정하지 않는다.
- **주석 정확성 감사가 qualification의 선행 조건**이다(`which singer` 사례).
  검증되지 않은 주석을 인증된 경계로 쓰는 것은 순환이다. 다만 그 감사가
  qualification을 완성하는 것은 아니다 — **증거원 신뢰성 검증 단계**다.
- `immediate_projection: forbidden` · `dispatch: blocked` ·
  `overall_status: insufficient_evidence` 유지. **`O1_SCOPE_PROJECTION_V3`을
  지금 만들면 안 된다.**
- **다음 단계**: normalization rule이 아니라 **`Name`/`ANA` 주석의 의미와
  정확성을 독립적으로 검증할 수 있는지**를 판정하는 것.

---

# A. 판정 verbatim

<!-- VERBATIM-BEGIN -->
## Q35 판정

Wolfram으로 **논리적 측면을 별도로 확인**했다. 다만 이번 Wolfram `Context` 조회는 502 오류로 실패했으므로, 아래 평가는 **사용자가 제공한 Q35 자료 + Wolfram Language 논리 검증**에 한정한다.

### 핵심 결론

**`Name`·`ANA`는 semantic qualification의 유력한 *증거(evidence)* 로는 인정할 수 있지만, 그 자체를 semantic authority 또는 충분조건으로 승격시키면 안 된다.**

따라서 Q35의 답은 대략 다음이다.

```yaml
Q35:
  Name_ANA_as_evidence: admissible
  Name_ANA_as_semantic_authority: not_established
  qualification_from_Name_ANA_alone: insufficient_evidence
  immediate_projection: forbidden
  dispatch: blocked
```

---

## 1. `Name`과 `ANA`는 FOLIO의 상수와 같은 종류인가?

**아니라고 보는 것이 더 정확하다.**

### FOLIO constant

FOLIO의

```text
widereciever
summer1972olympics
music
stonefish
```

같은 상수 사용은 **표현 방식**이다.

Q34에서 확인했듯이 상수가 있다고 해서 그 항이 반드시 referential participant라는 의미론적 결론은 나오지 않는다.

### PMB `Name` / `ANA`

반면 Q35가 제시한

```text
male.n.02   Name "Tom"
female.n.02 Name "Mary"

female.n.02 ANA -7
male.n.02   ANA -3
```

는 **주석자가 특정 기능을 표시한 메타데이터**다.

따라서 둘 사이에는 중요한 차이가 있다.

| 층                      | 무엇을 말해주는가                                     |
| ---------------------- | --------------------------------------------- |
| FOLIO constant         | 수식에서 어떤 항 형식을 사용했는가                           |
| PMB `Name`             | 주석자가 해당 노드를 명명된 개체로 표시했음                      |
| PMB `ANA`              | 주석자가 조응 관계를 표시했음                              |
| semantic qualification | 그것이 정말 measurand 밖의 referential participant인가 |

즉,

> `Name`/`ANA` → **semantic evidence**

는 가능하지만,

> `Name`/`ANA` → **semantic truth**

는 별도의 주장이다.

**판정: prompt-given + model inference**

---

## 2. 특히 `Name`은 상당히 강한 positive evidence다

Q35의 예:

```text
male.n.02    Name "Tom"
female.n.02  Name "Mary"
male.n.02    Name "Joe"
```

는 Q34에서 문제가 된

```text
Tom
Mary
Joe
```

와 직접 연결된다.

따라서 적어도 다음과 같이 말할 근거는 충분하다.

```text
Name
  ↓
referentiality에 관한 corpus annotation evidence
```

그러나

```text
Name
  ↓
O1 measurand 밖
```

까지는 아직 한 단계가 남는다.

왜냐하면 **"명명된 개체를 지시한다"**와 **"O1 scope measurand에서 제거해야 한다"**는 서로 다른 명제이기 때문이다.

이 둘을 동일시하면 D-33에서 경계 설정을 다시 corpus annotation에 위임하게 된다.

---

## 3. `ANA`는 더 강하지만 동시에 다른 문제를 갖는다

`ANA`는

```text
she
his
her
himself
```

등이 선행사를 되짚는다는 주석이다.

따라서 `ANA`는 단순한 표면 토큰보다 훨씬 좋은 증거다.

하지만 이것도 바로

```text
ANA ⇒ non-scope
```

가 되지는 않는다.

오히려 `ANA`가 있다는 것은 **조응 관계가 존재한다는 것**을 알려주는 것이지, 그 표현의 모든 scope 관련 의미가 제거된다는 것을 증명하지 않는다.

따라서:

```yaml
ANA:
  evidence_of_anaphoric_relation: strong
  evidence_of_referential_participant: potentially_strong
  proof_of_non_scope_measurand: insufficient
```

정도가 안전하다.

---

## 4. Wolfram 검증에서 중요한 논리적 제한도 그대로 유지된다

앞선 D-33의 핵심 논거를 다시 계산해 보면,

```text
∃x [P(x) ∧ B(x)]
```

를

```text
∃x B(x)
```

또는

```text
B(c)
```

로 바꾸는 것이 일반적인 논리적 동치가 아니다.

Wolfram Language에서도 두 식의 일반적 `Equivalent`가 성립하지 않으며, 반례가 존재하는 조건이 남는다.

즉:

> **"이것이 referential participant라는 증거가 있다"**

와

> **"그러므로 existential binder를 scope measurand에서 제거해도 된다"**

는 별개의 추론이다.

이것은 Q35에서도 그대로 적용된다.

**판정: Wolfram-grounded logical analysis**

---

# 5. 그래서 Q35의 가장 중요한 발견은 `Name/ANA` 자체가 아니다

제가 보기에는 더 중요한 것은 **증거 계층을 새로 발견했다는 것**이다.

현재 구조를 이렇게 분리해야 한다.

```text
PMB gold
 │
 ├─ surface token
 ├─ synset
 ├─ logical/adaptor structure
 │
 └─ role annotation
      ├─ Name
      └─ ANA
```

기존에는 사실상

```text
synset + surface
       ↓
referentiality 추정
```

을 시도했다.

Q34에서 그것이 불안정했다.

Q35에서는 처음으로

```text
annotation evidence
       ↓
referentiality qualification의 후보 증거
```

가 추가됐다.

따라서 **Q35는 qualification 자체를 해결한 것이 아니라 qualification을 위한 증거층을 발견한 것**으로 읽어야 한다.

---

## 6. 30% coverage는 결정적인 제약이다

Q35의 전수 결과:

* `Name`: 3,841
* `ANA`: 1,022
* 둘 다 아님: 10,548
* 전체 후보: 15,810

즉 `Name`/`ANA`가 있는 것은 약 **30%**다.

따라서 다음 추론은 불가능하다.

```text
Name/ANA가 붙어 있음
→ referential
```

에서 더 나아가

```text
Name/ANA가 없음
→ non-referential
```

이라고 할 수 없다.

이것은 **positive evidence와 negative evidence의 비대칭성**이다.

### 따라서 3값 처리가 자연스럽다

만약 향후 qualification에 사용한다면 최소한:

```text
QUALIFIED_REFERENTIAL
NOT_QUALIFIED_REFERENTIAL
NEEDS_AUDIT
```

같은 구조가 필요할 가능성이 높다.

하지만 여기서도 **지금 당장 이 schema를 채택하자는 의미는 아니다.**

Q35의 목적은 경계를 설계하는 것이 아니라 **증거의 적격성을 판정하는 것**이기 때문이다.

**판정: prompt-given + model inference**

---

## 7. 더 중요한 문제: `Name`/`ANA`가 없는 66%를 어떻게 해석하는가?

현재 자료만으로는 답할 수 없다.

특히

```text
둘 다 아님 = 10,548
```

을

```text
referential 아님
```

으로 읽으면 안 된다.

Q35가 이미 이것을 정확하게 보여준다.

따라서:

```yaml
absence_of_Name_ANA:
  means_non_referential: false
  means_unknown: true
```

가 현재 증거에 가장 충실하다.

이 점은 **"absence of evidence ≠ evidence of absence"**라는 프로젝트 규율과도 직접 맞는다.

---

## 8. `ANA` exclusion을 지금 되돌릴 필요는 없다

여기서는 **되돌리지 않는 쪽**이 맞다.

이유는 간단하다.

현재 in-N이 이미 동결되어 있기 때문이다.

```text
ANA를 다시 포함
      ↓
모집단 변경
      ↓
사전등록/코호트 계약 변경
```

이것을 Q35의 발견만으로 실행하면 측정 계약을 관측 결과에 맞춰 수정하는 모양이 된다.

대신 다음과 같이 기록하는 것이 정확하다.

```yaml
ANA_exclusion:
  current_cohort: retained
  reason: preregistered_population_constraint

future_qualification:
  ANA_evidence: available
  cohort_inclusion: separate decision
```

즉 **Q35에서 발견한 evidence layer를 향후 qualification 연구의 재료로 보존**하되, 현재 코호트를 사후 수정하지 않는다.

**판정: prompt-given contract + model inference**

---

# 9. `Name` annotation 자체의 오류 가능성도 해결해야 한다

Q35의

```text
Name
  "which singer"
```

사례는 작아 보여도 중요하다.

왜냐하면 지금 우리가 하려는 것은

```text
Name
  ↓
semantic qualification
```

이기 때문이다.

그렇다면 최소한:

```text
annotation correctness
```

가 검증되지 않은 상태에서 `Name`을 **인증된 semantic boundary**로 사용하는 것은 순환적이다.

따라서 Q35(d)에 대해서는:

> **annotation accuracy audit은 qualification 전에 필요하다.**

다만 여기서도 주의할 점은:

```text
Name audit
```

가 곧

```text
referential ∃ qualification
```

을 완성한다는 뜻은 아니다.

그것은 단지 **증거원의 신뢰성을 검증하는 선행 단계**다.

---

# 최종 판정

제가 이 자료만으로 외부 설계 담당에게 회신한다면 다음처럼 판정하겠다.

```yaml
D_E2E_v1_35:

  question:
    PMB_role_annotations_as_semantic_qualification_evidence:

  Name:
    evidential_status: admissible_candidate
    semantic_authority: not_established
    sufficient_for_projection: false

  ANA:
    evidential_status: admissible_candidate
    semantic_authority: not_established
    sufficient_for_projection: false

  coverage:
    Name_plus_ANA: approximately_30_percent
    uncovered_cases:
      status: NEEDS_AUDIT
    absence_is_negative_evidence: false

  annotation_quality:
    status: unresolved
    prerequisite_for_authoritative_use: true

  ANA_exclusion:
    current_cohort_change: forbidden
    future_requalification: separate_decision

  immediate_projection:
    forbidden: true

  dispatch:
    blocked: true

  overall_status:
    insufficient_evidence
```

### 한 문장으로 압축하면

> **Q35는 `Name`·`ANA`가 단순 synset이나 표면 토큰보다 훨씬 좋은 referentiality 증거라는 점은 보여주지만, 그것들이 곧 semantic authority이거나 O1 measurand에서 existential binder를 제거할 충분조건이라는 것까지는 입증하지 못한다.**

따라서 **지금 `O1_SCOPE_PROJECTION_V3`을 만들면 안 된다.** 다음 단계는 normalization rule을 만드는 것이 아니라, **`Name`/`ANA` annotation의 의미와 정확성을 독립적으로 검증할 수 있는지**를 판정하는 쪽이 맞다.
<!-- VERBATIM-END -->

---

# B. 우리 수신 검증 (2026-08-24)

순서를 지켰다: 정본 저장 → 검증 설계 → **설계 적대검증** → 검증 → 저장.
그리고 **대상을 얼렸다** — 직전 라운드(D-34)에서 띄운 뒤 문서를 고쳐 검증자가
혼합 상태를 읽었고 내부 모순 하나가 통과했다. 이번엔 회신까지 정본·설계를
건드리지 않았다.

## B.1 설계 적대검증이 **blocker 4건**을 냈고 설계를 다시 썼다

"그대로 실행 불가" 판정이었다. 각 건을 lead가 판정했다.

| # | 지적 | 판정 |
|---|---|---|
| B1 | **V2가 불일치를 오류로 오독한다** — `Tom's`↔`Name "Tom"`은 정상 변형이고 오류가 아니다. 그런데 설계는 그 개수를 "감사 필요·가능성"의 증거로 썼다 | **수용.** 내 함정 절에 "불일치는 오류의 증거가 아니다"를 적고서 통과 기준에서 그것을 어겼다 — §B.2/§B.6 모순과 같은 형태다 |
| B2 | **§6 안전장치 없음** — V1이 >0이면 "3값 schema를 지금 채택"으로 읽힐 수 있는데 판정은 그것을 금지했다 | **수용.** 명시적 비함의 문장을 넣었다 |
| B3 | **§8 금지 미강제** — V3이 수치를 내지만 그것으로 코호트를 고치지 말라는 것이 통과 기준에 없다 | **부분 수용.** 함정 절에는 있었으나 V 항목에 없었다. blocker보다는 major로 본다 |
| B4 | **§9 순환 미해소** — V2가 주석을 권위로 쓰는 순환을 막지 못한다 | **수용**(B1의 귀결) |
| major | **V1이 순환이다** — "지시적이다"가 미정인데 내가 고른 목록으로 증인을 만든다. "비율이 아니라 존재만 본다"는 방어도 목록이 있어야 성립하므로 순환을 해소하지 못한다 | **수용 — 가장 날카롭다.** V1을 **비순환 설계로 다시 썼다**(§B.2) |
| major | **§5(증거 계층 발견이 진짜 성과) 검증 항목 없음** | **수용.** V6 신설(§B.5) |

## B.2 V1 재설계 — 내 판단을 쓰지 않는 **corpus 내부 일관성** 논거

원 설계는 "주석 없는 노드 중 표면이 대명사인 것"을 찾으려 했다. 그것은 내가
"대명사는 지시적"이라고 전제해야 성립한다 — **바로 미정인 것을 전제**한다.

재설계: **같은 `(synset, 표면 토큰)` 쌍이 주석과 함께도, 주석 없이도
나타나는가.** 나타나면 주석 부재는 표현의 성질이 아니라 **주석 범위**다.
이 논거는 "무엇이 지시적인가"를 내가 판정하지 않고 성립한다.

PMB gold 12,053 전수, `(synset, 표면)` 쌍 **2,342종**:

| | 종 수 |
|---|---:|
| 주석 있는 것만 나타남 | 1,020 |
| 주석 없는 것만 나타남 | 1,284 |
| **양쪽에 나타남** | **38** |

38종이 차지하는 노드는 **주석 1,097 · 무주석 3,155**이고, 그 38종은 정확히
고빈도 대명사다:

```text
male.n.02    'he'      주석  82 · 무주석 990
female.n.02  'she'     주석  39 · 무주석 705
male.n.02    'his'     주석 444 · 무주석 167
female.n.02  'her'     주석 182 · 무주석 199
person.n.01  'we'      주석   1 · 무주석 312
entity.n.01  'it'      주석  71 · 무주석 226
```

**판정 §6·§7의 비대칭 주장이 확인됐다** — `absence_of_Name_ANA:
means_unknown: true`. 같은 표현이 양쪽에 있으므로 주석 부재를 비지시성으로
읽을 수 없다.

**REFUTE 경로가 실질적이었다**: 2,342종이 전부 한쪽에만 있었다면 주석 부재가
표현별로 일관되고 비대칭 주장이 약해졌을 것이다. 그렇지 않았다.

## B.3 V2(축소) — **감사 범위**만 보고한다. 오류 개수가 아니다

`Name` 주석 **5,365건**의 주석값 대 표면 토큰:

| 관계 | 건수 | 예 |
|---|---:|---|
| 완전 일치 | 3,044 | `'Sam Beattie'←'Sam Beattie'` |
| 표면이 값을 포함 (소유격·구두점 — **정상**) | 1,719 | `'China'←"China's"` · `'China'←'China.'` |
| 값이 표면 안에 (관사·전치사 — **정상**) | 308 | `'Grameen Bank'←'the Grameen Bank'` |
| **포함 관계 없음 — 감사 대상** | **294** | `'japan'←'Japanese'` · `'olympic games'←'the 2008'` · `'Sichuan'←'province.'` |

**294건은 오류 개수가 아니라 감사 범위다.** 오류 판정에는 주석 권위가
필요하고 우리에게 없다 — 그것이 판정 §9가 말한 "독립 검증"의 내용이다.
적대검증의 B1 지적대로, 원 설계는 이 수를 "감사 가능성"의 증거로 쓰려 했고
그것은 잘못이었다. **"감사 가능성" 판정은 이 검증의 범위 밖**이다.

## B.4 V3 — ANA 배제 규모. **수치만 낸다**

Path B 후보 **709건** 중 `ANA` 때문에 제외된 것 **14건(1%)**.

**이 수치로 코호트를 고치지 않는다.** 판정 §8이 금지했다 — "Q35의 발견만으로
모집단을 바꾸면 측정 계약을 관측 결과에 맞춰 수정하는 모양이 된다."
`ANA_exclusion: current_cohort: retained`를 그대로 따른다. 이 수치는
**향후 qualification 연구의 재료로 보존**하기 위한 것이다.

## B.5 V6(신규) — 증거 계층을 **다 본 것이 아니다**

판정 §5는 "Q35의 진짜 성과는 증거 계층의 발견"이라고 했다. 그렇다면 그 계층을
얼마나 봤는지가 중요하다.

PMB SBN의 role 어휘는 **200종**이고 우리가 검토한 것은 **2종(`Name`·`ANA`)**
뿐이다. 빈도 상위만 봐도 미검토가 대부분이다:

```text
Time  13,323 ←미검토   EQU  12,501 ←미검토   Theme 7,252 ←미검토
TPR    6,033 ←미검토   Name  5,760 (검토)    Agent 5,268 ←미검토
```

**`EQU`(12,501건)는 동일성 표시라 지시성과 직접 관계될 수 있는데 보지 않았다.**
Q35 §5의 한계에 그것을 적었으나 규모는 이번에 처음 쟀다. 즉 "증거 계층을
발견했다"는 판정의 평가는 맞지만 **우리는 그 계층의 1%를 봤다.**

## B.6 명시적 비함의 — 이 검증이 **하지 않는** 주장 (적대검증 B2·B3 반영)

- **3값 schema를 채택하자는 것이 아니다.** §B.2가 >0을 얻었지만 판정 §6은
  "지금 당장 이 schema를 채택하자는 의미는 아니다"라고 명시했다. 이 검증
  결과는 그 채택의 근거가 **아니다**.
- **`ANA` 배제를 되돌리자는 것이 아니다.** §B.4의 14건은 보존 목적이고 코호트
  개정 근거가 아니다.
- **`Name`/`ANA`를 경계로 쓰자는 것이 아니다.** 판정은 `semantic_authority:
  not_established`다. §B.2는 **주석 부재의 해석**에 관한 것이고 주석 존재의
  권위에 관한 것이 아니다.
- **주석이 틀렸다고 주장하지 않는다.** §B.3의 294건은 감사 범위다.

## B.7 재실측하지 않고 인용한 것

- 논리 주장(`∃x[P∧B]` ≠ `∃x B` / `B(c)`): D-33 §B.2에 도메인 2 전수 반례
  5·10건이 있다. 판정이 Wolfram Language로 같은 결론에 도달했다.
- **판정자의 502 한계**: 적대검증이 판정문을 훑어 **Wolfram이 실제로 쓰인
  곳은 §4뿐**(논리 비동치)이고 §5~§9는 제공 자료 + 논리 추론임을 확인했다.
  `Context` 조회 실패는 **문헌 확인** 쪽이므로 논리 결론에는 영향이 없다.
  다만 §1의 "FOLIO 상수와 다른 종류다"는 개념 분석이고 Wolfram 근거가 아니다 —
  우리 관찰을 채택한 것이다.

## B.8 상태

`immediate_projection: forbidden` · `dispatch: blocked` ·
`insufficient_evidence` 유지. **`O1_SCOPE_PROJECTION_V3`을 만들지 않는다.**

**다음 행동**: 판정 말미가 명한 대로 **`Name`/`ANA` 주석의 의미와 정확성을
독립적으로 검증할 수 있는지**를 판정받는 것이다. §B.3(감사 범위 294건)과
§B.5(role 어휘 200종 중 2종만 검토)가 그 상신의 재료다.

## B.9 한계

- §B.2의 38종은 **종 수로는 2%**다(2,342종 중). 토큰으로는 4,252 노드다.
  종·토큰 어느 쪽으로 읽어야 하는지 우리가 정하지 않았다.
- §B.3의 관계 분류(포함·공백·대소문자)는 **문자열 관계**이고 언어학적 판단이
  아니다. `'japan'←'Japanese'`가 오류인지 파생 표기인지 우리는 모른다.
- §B.5는 role **빈도**만 쟀다. 어느 role이 지시성과 관계되는지는 보지 않았다 —
  그것을 보려면 각 role의 정의가 필요하고 그것이 다음 상신의 내용이다.
