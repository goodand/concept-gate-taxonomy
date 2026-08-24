# DESIGN DECISION — D-E2E-v1-36 (구속 조건은 R1이 아니라 R2다)

- 수신: 2026-08-24 · 발신: 외부 설계 담당(저장소 접근 없음, Wolfram 검증 명시)
- 요청서: [[DESIGN_REQUEST_independent_verifiability_constraint|Q36]]
- 사슬 항법: 이전 [[DESIGN_DECISION_annotation_layer_admissibility|D-35]] ·
  **D-36** · 색인 [[RULING_CHAIN_INDEX]] · 상태 정본
  [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 정본 규약: 아래 `VERBATIM-BEGIN`/`END` 사이가 수신 원문이고 그 바이트의
  sha256을 기록한다(D-30 이후 규약 — **마지막 개행 제외**).
- `VERBATIM_SHA256: ee8a01b9be124e8660581b628b622edadb5d45cea46fa5ac3493d52b08938367`

<!-- VERBATIM-BEGIN -->
## Q36 판정

이번 질문에서 **핵심 전환은 타당하다.** 다만 Q36의 R1~R4를 그대로 “필요충분한 요건”으로 확정하는 것은 아직 이르다.

Wolfram 검증에서도 중요한 점은 명확하다.

> **주석이 구조적으로 일관되게 사용된다는 사실과, 그 주석이 의미적으로 옳다는 사실은 논리적으로 별개의 명제다.**

따라서 현재 가장 방어 가능한 판정은:

```yaml
Q36:
  R2_is_relevant_constraint: yes
  R1_R2_R3_R4_as_complete_requirements: insufficient_evidence
  internal_consistency:
    status: partial_evidence_only
  sbn_spec_source:
    importance: material
    sufficient_for_semantic_authority: no
  second_corpus:
    useful_for_cross_validation: yes
    automatically_independent: no
  failure_to_establish_R2:
    means: boundary_not_established
    does_not_mean: boundary_impossible
  immediate_projection: forbidden
  dispatch: blocked
```

---

# 1. R2는 실제로 필요한가?

**그렇다고 보는 것이 맞다.**

Q33~Q35에서 이미 다음 문제가 반복됐다.

```text
corpus representation
        ↓
semantic boundary 추정
        ↓
measurand 변경
```

여기서 외부 evidence를 받아들인다면 최소한:

```text
"이 evidence가 실제로 주장하는 것을 정확하게 나타내는가?"
```

를 별도로 확인할 수 있어야 한다.

그렇지 않으면 다음과 같은 순환이 생긴다.

```text
PMB annotation
    ↓
PMB annotation의 의미를 우리 apparatus가 해석
    ↓
그 해석으로 semantic boundary 결정
    ↓
그 boundary를 이용해 apparatus를 정당화
```

따라서 **R2는 단순한 품질관리 조건이 아니라 authority를 measurement contract에 연결하기 위한 독립성 조건**이다.

**판정: model inference + Q35/Q36 supplied evidence**

---

# 2. 하지만 R1~R4를 “완전한 요건 목록”으로 확정하면 안 된다

Q36 자체가 이 부분을 정확히 경고한다.

현재:

* R1 = semantic class를 기록
* R2 = 그 기록을 독립 검증
* R3 = 미포함 범위 명시
* R4 = source 간 동일 기준

이라는 것은 **현재 발견된 failure modes를 정리한 decomposition**이다.

그것이 곧

> “semantic qualification authority가 되기 위한 필요충분조건은 정확히 R1~R4다”

라는 theorem은 아니다.

특히 R4는 흥미롭다.

PMB와 FOLIO가 반드시 같은 annotation mechanism을 가져야 하는지, 아니면 **동일한 measurand에 대해 의미적으로 동등한 qualification을 제공하면 되는지**가 아직 결정되지 않았다.

따라서:

```text
R1~R4 = 현재 검토해야 할 constraint set
```

이지

```text
R1~R4 = 완전한 certification theorem
```

은 아니다.

**판정: model inference**

---

# 3. §2의 `ANA` 구조적 일관성은 R2의 일부인가?

**예. 그러나 아주 제한적인 의미에서만 그렇다.**

Q36의 실측:

```text
ANA:
  node-edge position = 1,036 / 1,036

NEGATION:
  first-token box operator = 546 / 546
```

은 다음 명제를 지지한다.

```text
ANA annotation
    → 특정한 syntactic/structural position에 일관되게 사용됨
```

그리고

```text
male.n.02 + 'he'
    annotated: 82
    unannotated: 990
```

은

```text
annotation presence
≠
surface form 자체의 필연적 속성
```

이라는 점을 보여준다.

이것들은 **annotation system의 internal consistency**에 대한 좋은 증거다.

그러나:

```text
ANA가 일관된 위치에 있다
```

로부터

```text
ANA는 의미론적으로 anaphoric이다
```

를 논리적으로 도출할 수는 없다.

Wolfram으로도 이 구조를 형식화했을 때,

```text
ANA(x) ↔ NodeEdge(x)
```

같은 구조적 관계와

```text
Annotated(x) → Referential(x)
```

같은 의미론적 관계 사이의 함의는 나오지 않는다.

즉:

```text
internal consistency
        ≠
semantic correctness
```

이다.

**판정: Wolfram-grounded logical analysis**

---

# 4. 이것은 매우 중요한 구분이다

Q36의 현재 구조를 다음 세 단계로 분리하는 것이 좋다.

### Level 1 — Encoding consistency

```text
ANA가 어디에 기록되는가?
```

현재 상당히 강한 증거가 있다.

### Level 2 — Annotation correctness

```text
그 위치에 ANA를 붙인 것이 실제로 올바른가?
```

현재 미검증.

### Level 3 — Semantic qualification

```text
그 ANA가 나타내는 표현이
O1 scope measurand에서 제외되어야 할 referential participant인가?
```

현재 미검증.

따라서 현재 상태는:

```text
L1  ██████████  supported
L2  ░░░░░░░░░░  unresolved
L3  ░░░░░░░░░░  unresolved
```

에 가깝다.

**이 세 층을 합치지 않는 것이 Q36에서 가장 중요하다.**

---

# 5. `sbn_spec.py` 원천을 확보하는 것은 필요한가?

**R2의 전부는 아니지만, 중요한 선행 자료다.**

현재 상황은:

```text
우리 코드
   ↓
sbn_spec.py의 전사
   ↓
ANA의 의미를 설명
```

인데 원천 파일이 없다.

그러면 우리가 실제로 확인한 것은:

> “우리에게 전달된 사양의 전사가 이렇게 쓰여 있다.”

이지,

> “PMB/SBN의 원래 규약이 이렇게 정의되어 있다.”

가 아니다.

따라서 원천 사양을 확보할 수 있다면 **반드시 확보하는 편이 낫다.**

하지만 중요한 제한이 있다.

```text
original sbn_spec.py
        ↓
specification authenticity
```

는 강화하지만,

```text
specification
        ↓
semantic truth
```

까지 자동으로 보장하지 않는다.

즉 `sbn_spec.py`를 확보하면 **R2의 한 공백은 줄어들지만 R2가 완성되는 것은 아니다.**

---

# 6. 두 번째 annotation corpus는 R2를 자동으로 해결하지 않는다

Q36의 이 부분은 약간 수정하는 것이 좋다.

현재 문구:

> 다른 주석 corpus는 R1·R4를 채우고 R2에서 막힌다.

이것은 **가능한 경우의 하나**이지 일반 법칙은 아니다.

두 번째 corpus가 독립적으로 만들어졌고,

```text
annotation A
        ↕
independent annotation B
```

사이에 적절한 교차검증이 가능하다면 **R2에 기여할 수 있다.**

다만:

```text
Corpus A says X
Corpus B says X
```

만으로 의미론적 진리가 증명되는 것은 아니다.

두 corpus가 동일한 원천 규약이나 동일한 annotation error를 공유할 수 있기 때문이다.

따라서 더 정확한 표현은:

> **다른 corpus는 R2를 충족시키는 독립 검증의 후보가 될 수 있지만, 독립성 자체를 별도로 입증해야 한다.**

이다.

---

# 7. 사람 판정도 마찬가지다

Q36에서:

```text
R2 ← 사람 판정
```

이라고 한 것은 너무 강하다.

사람 판정자가 있다는 것만으로 독립 검증이 생기지 않는다.

예를 들어:

```text
판정자 A
  ↓
referential

판정자 B
  ↓
referential
```

라고 해도 A와 B가 같은 정의를 그대로 복제했다면 독립성이 약하다.

반대로,

```text
독립된 판정자
+ 사전 정의
+ blind annotation
+ disagreement analysis
+ adjudication 절차
```

가 있으면 R2의 증거가 훨씬 강해진다.

따라서 **R2는 “사람이 판단했다”가 아니라 “검증 절차가 독립적인가”의 문제**다.

---

# 8. R2가 실패하면 “경계가 원리적으로 불가능”한가?

**아니다.**

이것은 Q36에서 가장 중요한 결론 중 하나다.

논리적으로:

```text
현재 독립 검증 수단을 찾지 못함
```

과

```text
독립 검증 수단이 원리적으로 존재하지 않음
```

은 전혀 다른 명제다.

따라서:

```yaml
R2:
  established: false
```

에서 곧바로

```yaml
referential_boundary:
  impossible: true
```

를 추론하면 안 된다.

정확한 상태는:

```yaml
referential_boundary:
  status: unestablished
```

또는 프로젝트 규율에 따라

```text
insufficient_evidence
```

이다.

---

# 9. 따라서 동결된 PMB 15건을 폐기할 이유도 없다

R2가 아직 해결되지 않았다고 해서:

```text
PMB 15건
   ↓
invalid
```

가 되는 것은 아니다.

현재 더 정확한 상태는:

```text
PMB 15건
  ↓
fixture 자체는 동결
  ↓
scope measurement qualification unresolved
  ↓
dispatch blocked
```

이다.

즉 **재료의 무효화와 측정 계약의 미완성을 구분해야 한다.**

이 구분이 없으면 Q33~Q36의 investigation 자체가 사후적으로 모집단을 계속 변경하는 문제가 생긴다.

---

# 10. Q36에서 실제로 발견한 것은 “R2”보다 더 구조적인 것

저라면 운영 판정에서 이것을 강조하겠다.

현재까지의 chain은:

```text
Q33
  encoding mismatch 발견
        ↓
Q34
  surface/synset으로 경계 불가
        ↓
Q35
  Name/ANA 발견
        ↓
Q36
  annotation 자체의 독립 검증 문제가 다시 등장
```

이다.

따라서 문제는 더 이상 단순히

> “어떤 feature를 사용하면 되나?”

가 아니다.

실제 문제는:

> **“measurement apparatus가 의미론적 경계를 결정할 때, 그 경계를 제공하는 authority를 어떻게 독립적으로 인증할 것인가?”**

로 상승했다.

이것은 상당히 중요한 설계 전환이다.

---

# 최종 판정

제가 Q36을 정본화한다면 다음처럼 하는 것이 가장 안전하다.

```yaml
D_E2E_v1_36:

  central_question:
    independent_verifiability:
      status: genuine_constraint

  R1_R4:
    status: candidate_constraint_decomposition
    complete_or_necessary_sufficient: insufficient_evidence

  R1:
    semantic_record_exists:
      Name_ANA: supported_for_partial_domain

  R2:
    independent_verification:
      status: unresolved
      importance: gating

  internal_structural_consistency:
    ANA_position:
      supported: true
    evidential_role:
      supports: encoding_consistency
      does_not_prove: semantic_correctness

  sbn_spec:
    original_source:
      obtain_if_possible: true
    effect:
      strengthens_specification_provenance
      does_not_by_itself_certify_semantic_truth: true

  second_corpus:
    possible_role: independent_cross_validation
    automatic_R2_satisfaction: false

  failure_of_R2:
    boundary_impossible: false
    boundary_status: unestablished
    project_status: insufficient_evidence

  frozen_cohort:
    invalidate: false
    modify: false
    dispatch: blocked

  immediate_projection:
    forbidden: true
```

### 한 문장

**Q36의 방향은 맞다: R2는 실제 구속 조건이다. 그러나 `ANA`의 100% 구조적 일관성은 R2의 “부분 증거”일 뿐이며, 그것을 의미적 정확성으로 승격할 수 없다. 따라서 현재 필요한 것은 새로운 normalization rule이 아니라 `annotation provenance → independent correctness → semantic qualification`의 세 단계를 분리해서 검증할 수 있는가를 밝히는 것이다.**

그리고 **R2를 아직 충족시키지 못했다고 해서 referential ∃ 경계가 원리적으로 불가능하다고 판정해서는 안 된다. 현재 결론은 `insufficient_evidence`가 맞다.**
<!-- VERBATIM-END -->

---

# 운영 세션의 수신 검증 (2026-08-24)

절차: **검증 설계 → 설계의 적대적 검증 → 검증 실행 → 저장.** 설계를 먼저
동결(`cc822f73e0e217553b7d2e6cea30a015`)한 뒤 근거 축 4개에 넘겼다 — 이 세션이
"검토 중에 대상을 편집해 적대검증이 §B.2를 SOUND로 판정하면서 §B.6을 인용"한
사고를 겪었으므로, 대상 동결이 규율이 됐다.

## 0. 결론 — **판정문이 옳고, 내가 제안한 강화는 반박됐다**

| 항목 | 결과 |
|---|---|
| 판정문의 논리 주장 (§3 비함의 · §8 비함의) | **확증** — 반례모형으로 원문 근거보다 강하게 |
| 판정문이 인용한 우리 수치 | **1건 정확 · 2건 오차 · 1건 재현 불가** (§3) |
| 내가 제안한 §E1 (L2는 미검증보다 강하다) | **반박됨** — 판정문의 `L2 unresolved`가 맞다 (§4) |
| 선행 판정과의 충돌 | **0건** (§5) |
| 발효 중 금지 조항 위반 | **0건** (§6) |

## 1. 설계가 적대검증에서 네 곳 깨졌다

**축 B(형식 건전성)** — 가장 무거운 지적. `B1`(구조 쌍조건 ⊬ 의미 함의를
반례모형으로 확인)은 **실패할 수 없는 검사**다. 전제
`∀x(ANA(x)↔NodeEdge(x))`와 결론 `∀x(Annotated(x)→Referential(x))`가 비논리
어휘를 하나도 공유하지 않아 보간 논증으로 함의가 원리적으로 불가능하다.
반례모형이 즉시 나온다:

```text
M1: 도메인 D={a}. ANA={a}, NodeEdge={a}, Annotated={a}, Referential=∅.
    전제 참(쌍조건 양변 참) · 결론 거짓(Annotated(a) ∧ ¬Referential(a)). ∎
```

그러므로 B1은 검사가 아니라 **시연**이다. 유일한 기여는 판정문 §3의 근거를
"Wolfram이 도출하지 못했다"(증명 탐색 실패 — 불완전 탐색일 수 있다)에서
**"도출 불가능하다"(모형론적 증명)**로 격상하는 것이다. 이것을 "§3 검증됨"으로
적으면 **형식적 비함의(F)와 형식화 적합성(A)을 뒤섞는 동치어법**이 정본에
들어간다. 그래서 여기 분리해 적는다: **(F)는 확립됐고 (A)는 이 축의 범위 밖**
(저장소 재료가 필요하다).

`B2`는 목표를 못 덮었다 — 삼층 분리를 검증한다면서 모형은 L1-L2만 다룬다.
`L2 ⊬ L3` 반례가 별도로 필요하다:

```text
M2c (설계에 없었다): D={a}. Correct(a)=T, O1Excludable(a)=F.
    주석은 올바르되 O1 scope 제외 대상이 아니다. ∎
```

그리고 축 B가 내 §H를 **반박했다.** 나는 "판정문의 `insufficient_evidence`는
반증 불가"라고 적었다. 틀렸다 — 시점·코퍼스 상대적으로 읽으면 반증 경로가
둘이다: (i) **같은 코퍼스에서 간과된 결정적 증거 제시** · (ii) **질문이
선험적으로 결정 가능함을 증명**(R1~R4 충분성을 형식화해 증명 또는 반례).
반증 불가한 것은 "미래의 새 증거에 의한 반증"뿐이고 그것은 반증이 아니라
**대체(supersede)**다. 내 §H가 경로 (ii)를 스스로 봉쇄했다.

부수 지적 하나가 무겁다 — **대상 질문이 정말 형식적이라면 판정문의
`insufficient_evidence`는 범주 오류 후보다.** 부족한 것이 증거가 아니라
**형식화**일 수 있다. 이것은 판정 사안이므로 우리가 정하지 않고 기록한다.

**축 C(판정문 충실성)** — 내 `A3`의 프레이밍이 **부당**했다. 나는 "판정이
우리 유보를 못 보고 정정했다면 정정의 무게가 달라진다"를 반증 조건으로 삼았다.
그런데 §6·§7이 교정하는 것은 **유보 여부가 아니라 명제의 논리적 강도**다
(보편 대 가능 · 동치 오류). Q36이 "이 연결은 우리 판단이다"라고 유보했어도
"사람 판정 = 독립 검증"이라는 동치 자체가 틀렸으면 정정은 온전하다. **A3는
정정의 근거를 메타-인식적 쟁점으로 치환해 무게를 깎고 있었다.** 철회한다.

또 설계가 판정문의 두 항목을 **빠뜨렸다**: §2의 R4 재해석("PMB와 FOLIO가 같은
annotation mechanism을 가져야 하는가, 아니면 동일 measurand에 대해 의미적으로
동등한 qualification을 제공하면 되는가")과 §10의 "문제가 상승했다"는 재정의.
둘 다 판정문이 명시적으로 강조한 것이다 — §7에 반영한다.

## 2. 축 A의 부재 판정을 정정한다 — 그리고 내가 그것을 확증했다가 틀렸다

축 A는 C1~C3·E1을 **UNVERIFIABLE**로 판정했다: PMB gold 원문이 저장소에 없어
재실측 불가라는 것이다. **나는 직접 검색해 그것을 확증했다** — `find -iname
"*.sbn"` 0건, `*pmb*`는 문서와 스캔 스크립트뿐.

**둘 다 틀렸다.** 축 D가 경로 정본을 찾아냈다:

```python
# experiments/2026-08-23_e2e_v1_c_o1_cohort/freeze_stage2.py:57-58
SC = Path("/private/tmp/claude-501/-Users-jaehyuntak/<세션UUID>/scratchpad")
GOLD = SC / "pmb_gold"
```

실측: **12,053 문서 · 12,053개 `.sbn` · 188M 실재.** 내 검색이 0건을 낸 이유는
gold가 **워크스페이스 밖 세션 scratchpad**에 있고 내가 워크스페이스만 훑었기
때문이다. **같은 형태(틀린 범위에서 찾고 부재를 단정)가 이 세션 다섯 번째다.**

그리고 나는 그 잘못된 부재 판정 위에 결론까지 세웠다 — "판정문 §5가 말한
'전사만 있고 원천이 없다'가 **코퍼스 자체에도 적용된다**, 우리는 수치를 갖고
재료를 갖지 않았다"고 사용자에게 보고했다. **철회한다.** 재료는 있다.

**다만 좁힌 형태는 남는다.** `freeze_stage2.py`는 **동결 표면**인데 그 안에
**세션 UUID가 박힌 경로**를 담고 있다. 다음 세션의 scratchpad UUID는 다르므로
그 경로는 깨진다. 즉 재료는 존재하지만 **이 세션에서만 도달 가능**하고, 동결
스크립트가 세션 범위 경로에 의존한다. 이것이 실재하는 재현성 위험이고,
내가 과장했던 주장의 정확한 판본이다.

## 3. C1~C3 실행 결과 — **1건 정확 · 2건 오차 · 1건 재현 불가**

| ID | 판정문 인용 | 재실측 | 판정 |
|---|---|---|---|
| C1 | `ANA` 노드 간선 위치 **1,036 / 1,036** | **1036 / 1036** | **정확 일치** |
| C2 | `NEGATION` 행 첫 토큰 **546 / 546** | 비율 **1904/1904 = 100%** · 그러나 **546은 어떤 분모로도 재현 안 됨** | **수치 재현 불가** |
| C3 | `male.n.02 'he'` 주석 **82** / 무주석 **990** | 주석 **82**(정확) / 무주석 **982**(0.8% 차) | **부분 일치** |
| — | (Q35 §2) `Name` **5,760** · 후보 내 **3,841** | **5,759** · **3,845** | 오차 1·4건 |

**C2의 546을 설명하지 못한다.** 시도한 분모 전부: 전수 행 1904 · 전수 문서
1399 · Path-B 후보 행 583 · Path-B 후보 문서 382. **판정문 §3이 이 수치를
그대로 인용해 추론했다.** 다행히 그것이 지지하는 주장(`ANA`와 `NEGATION`의
위치가 완전히 분리된다)은 **더 큰 기반에서 성립한다**(546이 아니라 1904에서
100%). 그러므로 결론은 영향받지 않고 오히려 강해진다. 그러나 **우리가 외부
판정자에게 재현되지 않는 수치를 냈다**는 사실은 남는다.

**첫 실행에서 C3가 69/44로 나와 크게 틀렸다.** 원인은 gold 표면에 **ANSI
이스케이프**가 섞여 있는 것이었다(`% one \x1b[31mof\x1b[0m`). 정규화하니
82/982이 됐다. **내가 만든 인용 실재 게이트(`scripts/verify_finding_citations.py`)
가 정확히 ANSI를 정규화하는데, 새 계수 스크립트에 그 교훈을 적용하지 않았다.**

## 4. E1 — 증인은 실재하고, **그 해석이 반박됐다**

설계 E1은 "L2(주석 정확성)는 '미검증'이 아니라 관측된 반례가 있다"고 주장하며
Q35 §4(d)의 `person.n.01←'which singer'`(명명 주석 + 의문 표면)를 들었다.

**증인은 정확히 실재한다** (첫 시도의 0건도 ANSI 때문이었다):

```text
p00/d0240/en.drs.sbn    person.n.01 Name ? Role +1    % which singer
```

**그런데 그 행이 해석을 뒤집는다.** 값이 `?`다 — 이름이 아니라 자리표시자다.
이것은 **목록 없이, 경계 판단 없이 특성화 가능한 구조적 사실**이므로 전수를
셌다:

| `Name` 주석의 값 유형 | 전수 | 후보 부류 내 |
|---|---:|---:|
| `Name "이름"` (인용 문자열) | **5,365 (93%)** | 3,584 (93%) |
| **`Name ?` (자리표시자)** | **394 (7%)** | **261 (7%)** |
| 합 | 5,759 | 3,845 |

`Name ?`의 표면 예: `Who` · `Where` · `With whom` · `which singer`.

**그러므로 그 증인은 주석 오류가 아니다.** "이름이 물어지는 개체"를 표시하는
**별개 하위종**이고, `Name "X"` 대 `Name ?`라는 **값 형태로 기계적으로
분리된다.** 7%가 체계적으로 그렇게 표시돼 있다.

**결론: 내 §E1은 성립하지 않는다.** L2 위반의 유일한 증인이 위반이 아니었다.
판정문의 `L2: unresolved`가 맞다 — 그리고 이 측정은 오히려 **L1을 강화한다**
(값 형태가 하위종을 일관되게 구별한다).

**부수 소득 하나**: 이 `Name ?` 구별은 **비순환적**이다. referential 여부를
판정하지 않고, 닫힌 목록을 쓰지 않고, 주석자의 의미 판단을 신뢰하지도 않는다 —
값의 형태만 본다. Q34-B가 겪은 2%~51% 민감도가 여기엔 없다. 이것이 R2를
채우지는 않지만, **비순환 관측의 실례**로 기록할 값이 있다.

## 5. 선행 판정과의 정합성 — 충돌 0건

| ID | 검증 | 결과 |
|---|---|---|
| D1 | §6(다른 corpus가 R2에 기여 가능) vs **D-34 §9**(corpus 규약을 semantic authority로 승격 금지) | **충돌 아님.** D-34는 *authority 승격*을 금지하고, D-36은 *주석 정확성의 교차검증 후보*를 허용하며 **"독립성 자체를 별도로 입증해야 한다"**고 단서를 달았다(`automatically_independent: no`). 다른 역할이다 |
| D2 | `frozen_cohort: invalidate:false, modify:false` vs D-35 "`ANA` 배제 되돌리기 금지" | **정합.** 둘 다 동결 모집단 변경을 금지한다 |
| D3 | §9 "재료의 무효화와 측정 계약의 미완성을 구분" | 우리 기록이 이미 그 구분을 한다 — V5는 **잠정**(D-35가 V3 투영을 금지했으므로)이고 fixture 20건은 **동결 불변**이다 |
| D4 | `immediate_projection: forbidden` · `dispatch: blocked` | 유지. **코호트 dispatch 누계 0건** |

## 6. 실행 상태 준수 — 위반 0건

| ID | 확인 | 실측 |
|---|---|---|
| F1 | dispatch 누계 | **0** |
| F2 | `O1_SCOPE_PROJECTION_V3` 미존재 | **코드·manifest 0건** (`*.py`/`*.json`). `docs/*.md`·`HANDOFF.md`에는 **금지 조항으로서 문자열 존재** — 이 부재 주장은 **코드·manifest 범위**이고 "결정된 적 없다"로 확장하면 거짓이다(D-33이 V3을 예고했고 D-35가 금지했다) |
| F3 | manifest 불변 | **20건** (Tatoeba 15 + 5), `profile.id: O1_V5`, `scope_projection: O1_SCOPE_PROJECTION_V2` |
| — | in-N 20건 주석 사실 (`.oracle_cache` 66항목) | `ANA` **0문서/0회** · `Name` **4문서/5회**, 표면 `Tom`×3·`Mary`·`Joe` — **Q35 §3과 정확히 일치** |

축 D가 경계 조건 4개를 명시했고 전부 지켰다: E1을 그 한 쌍의 exact-match
조회에 한정 · gold 바이트를 repo로 가져오지 않음 · F2를 코드·manifest 범위로
유지 · 계수 스크립트를 scratchpad에 둠(게이트 AST 수집 대상 밖).

**명시 두 가지** (축 D 권고):
- **E1은 D-35가 명한 "주석 정확성 감사"의 착수가 아니다.** 감사는 주석자
  판단의 정확성이고 E1은 **우리 인용의 정확성**이다. 감사 본체를 수신 검증에
  끼워 넣는 것은 절차상 그르다(별도 범위·별도 상신 사안).
- 이 저장의 **커밋은 별도 승인 대기**다.

## 7. 판정문에서 우리가 아직 다루지 않은 것 (축 C가 지적한 누락)

- **§2의 R4 재해석**: PMB와 FOLIO가 같은 annotation mechanism을 가져야 하는가,
  아니면 **동일 measurand에 대해 의미적으로 동등한 qualification**을 제공하면
  되는가. 판정문이 "흥미롭다"고 강조했고 미결로 남겼다. **우리 설계는 이
  이분법을 다루지 않았다.** 후속 상신의 축이 될 수 있다.
- **§10의 재정의**: 문제가 "어떤 feature를 쓰면 되나"에서 **"measurement
  apparatus가 의미론적 경계를 결정할 때 그 경계를 제공하는 authority를 어떻게
  독립적으로 인증할 것인가"**로 상승했다. 이것을 §1 상태 요약에 반영한다.
- **L3 검증 방법**: 이 설계에 없다. 판정문의 결론이므로 검증 대상이 아니라
  미해결 항목이다.

## 8. 이 검증의 한계

- **(A) 형식화 적합성은 확인하지 못했다** — B1이 확립한 것은 (F) 형식적
  비함의뿐이다.
- **C2의 546을 설명하지 못한다.** 재현 불가로 기록하고 원인을 모른다.
- **C1~C3을 같은 계열 논리로 재실측했다.** 독립 구현이 아니므로 공통 결함은
  잡지 못한다 — 실제로 첫 실행이 ANSI 때문에 틀렸고 두 번째에 고쳤다.
- **gold 경로가 세션 범위다**(§2). 다음 세션은 이 재실측을 재현할 수 없다.
