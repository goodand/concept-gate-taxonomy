# DESIGN REQUEST — PMB의 role 주석 층이 semantic qualification의 원천이 될 수 있는가 (Q35)

- 발신: 2026-08-24, 운영 세션 · 수신: 외부 설계 담당
- 판정자 전제: **저장소 접근 없음.** 자기완결적이다 — 수치·주석 실물·우리가
  쓴 목록을 전부 본문에 싣는다.
- 성격: **D-34가 명한 다음 단계의 첫 후보에 대한 적격성 질문.** 판정은
  "분류기를 만들지 말고 **독립적 semantic qualification을 줄 source/evidence가
  무엇인지 결정하라"고 했다. 후보가 하나 나왔고, 그것이 **우리가 이미 갖고
  있으면서 한 번도 보지 않은 층**이다.
- 우리는 그 층을 쓸지 **정하지 않는다.** 적격성 판단이 D-34 §9의 논거
  ("corpus 규약을 semantic authority로 승격시키지 마라")와 정면으로 만나므로
  판정 사안이다.
- 상태: **코호트 dispatch 누계 0건** 유지. `immediate_projection: forbidden` 준수.

## 1. 우리가 보지 않았던 것 — PMB는 지시 기능을 **별도 role 주석으로 기록한다**

Q34·Q34-B의 모든 측정은 **synset + 표면 토큰** 두 층만 봤다. PMB SBN에는
세 번째 층이 있다 — 개념 노드에 붙는 **role edge**다. 그중 둘이 지시 기능을
직접 표시한다.

실물(주석 열의 `%` 뒤는 표면 토큰과 문자 구간):

```text
male.n.02      Name "Tom"    % Tom
female.n.02    Name "Mary"   % Mary
male.n.02      Name "Joe"    % Joe

female.n.02    ANA -7        % she
male.n.02      ANA -3        % his
female.n.02    ANA -3        % her
male.n.02      ANA -3        % himself with
```

`Name`은 **그 노드가 명명된 개체를 가리킨다**는 주석자의 표시이고, `ANA`는
**그 노드가 선행사를 되짚는다**는 표시다(음수는 상대 인덱스).

## 2. 적용 범위 — 후보의 **30%**에 주석이 있다 (전수)

PMB gold **12,053 문서 전수**. 지시 후보 부류 synset(`male`·`female`·`person`·
`entity`·`thing` + `.n.NN`)이 붙은 개념 노드 **15,810개**를 role 주석으로
분류했다.

| 층 | 건수 | 예 |
|---|---:|---|
| **`Name`** (고유명 주석) | **3,841 (24%)** | `female.n.02←'Sam Beattie'` · `male.n.02←'Padalecki'` · `male.n.02←'Gerald'` |
| **`ANA`** (조응 주석) | **1,022 (6%)** | `female.n.02←'she'` · `male.n.02←'his'` · `male.n.02←'himself'` |
| `Name` + `ANA` 동시 | 4 (0%) | `male.n.02←'Kamel'` |
| 양화 어휘(닫힌 목록 24종, 주석 없음) | 395 (2%) | `person.n.01←'Everyone'` · `entity.n.01←'Both'` |
| **둘 다 아님** | **10,548 (66%)** | `person.n.01←'You'` · `entity.n.01←'This'` · `person.n.01←'person'` · `entity.n.01←'and'` |

**이 분류는 우리가 고른 목록이 아니다.** Q34-B가 쓴 대명사·지시사 목록은
우리 선택이었고(그래서 비율이 목록에 25배 민감했다 — Q34-B 정정 참조),
`Name`·`ANA`는 **주석자가 붙인 것**이다. 우리가 한 것은 그 태그를 센 것뿐이다.

## 3. 그런데 우리는 `ANA` 보유 문서를 **선별에서 배제했다**

동결 스크립트가 명시적으로 그렇게 한다:

```python
# freeze_stage2.py: 선별 모집단 = Path B 후보 중 ANA 토큰 무보유
if any("ANA" in l.split("%", 1)[0].split()
       for l in sbn_text.splitlines() if not l.startswith("%%%")):
    continue
```

그 결정은 이전 적대검증 라운드에서 나왔다(조응 해소가 O1 능력과 무관한 부담을
더한다는 이유). 결과:

| | in-N PMB 15건 | gold 전수 |
|---|---:|---:|
| `ANA` 주석 | **0** | 1,022 |
| `Name` 주석 | 5 (4 fixture) | 3,841 |

즉 **corpus가 지시성을 명시한 재료 중 조응 쪽을 우리가 모집단에서 뺐다.**
남은 `Name` 5건은 `Tom`×3 · `Mary` · `Joe`이고, 그 넷이 정확히 Q33이 문제로
제기한 fixture다(`PMB-p87-d1860` "Tom bought Mary some chocolates." 등).

**우리는 문제를 제기하면서 그 문제에 대한 corpus의 주석을 보지 않고 있었다.**

## 4. 묻는 것

- **(a)** `Name`·`ANA`는 D-34 §9가 금지한 "corpus 규약"과 **같은 지위인가,
  다른 지위인가?**

  우리가 보는 차이는 이것이다 — FOLIO의 상수 사용은 **수식을 어떻게 썼는지의
  부산물**이고(그래서 `music`·`stonefish`도 상수가 된다), `Name`·`ANA`는
  **주석자가 지시 기능에 대해 내린 명시적 판단**이다. 전자를 semantic
  authority로 쓰지 말라는 논거가 후자에도 그대로 적용되는지 우리는 모른다.

- **(b)** 적격하다면 **범위를 어떻게 선언하는가?** 주석은 후보의 30%만
  덮는다. 나머지 66%(주석 없음·양화 어휘 아님)를 어떻게 다루는가 —
  `NEEDS_AUDIT` 같은 3값 처리인가, 아니면 30%만으로는 경계가 성립하지
  않는다고 보는가?

- **(c)** `ANA` 배제 결정을 **되돌려야 하는가?** 되돌리면 모집단이 바뀌고
  그것은 사전등록 개정이다(현재 in-N 20은 동결돼 있다). 되돌리지 않으면
  corpus가 명시한 증거의 6%를 계속 보지 않는다.

- **(d)** 주석 층에도 잡음이 있다. `Name` 버킷에서 표면이
  `person.n.01←'which singer'`인 항목이 나왔다 — 명명 주석이 붙었으나 표면이
  의문 표현이다. 주석 정확성을 우리가 검증하지 않았고, 그 검증이 이 적격성
  판단의 선행 조건인지 묻는다.

**운영 세션은 어느 것도 권고하지 않는다.** (a)가 이 질문의 축이고, 그 답이
D-34 §9의 논거를 어디까지 확장하는지를 정한다. 우리가 정하면
`operational_patch`다.

## 5. 한계

- 후보 모집단을 **synset 부류로 좁혔다**(`male`·`female`·`person`·`entity`·
  `thing`). 그 밖의 synset에 `Name`·`ANA`가 붙은 경우는 세지 않았다 —
  15,810과 30%는 **그 좁힌 모집단 안의 수치**다.
- `EQU`(12,501건)도 동일성 표시라 지시성과 관계될 수 있으나 **보지 않았다.**
  role 어휘 상위 20에 `Time` 13,323 · `EQU` 12,501 · `Theme` 7,252 ·
  `Name` 5,760 · `Agent` 5,268이 있고, 우리가 검토한 것은 `Name`·`ANA`뿐이다.
- FOLIO에는 대응 층이 **없다**(FOL은 항 종류만 구별한다). 이 후보는 PMB
  전용이고, 두 source를 같은 기준으로 다루는 문제는 해소되지 않는다.
- 주석 정확성 미검증(§4(d)).

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 이 단계를 명한 판정 [[DESIGN_DECISION_referential_existential_qualification|D-34]] · 선행 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · [[DESIGN_DECISION_d33_claim_status|D-33-V]]
- 선행 상신 [[DESIGN_REQUEST_referential_existential_qualification|Q34]] · [[DESIGN_REQUEST_referential_boundary_corpus_scale|Q34-B]]
