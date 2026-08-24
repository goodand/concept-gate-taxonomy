# DESIGN REQUEST — referential ∃ 경계: 재료가 기록하는 증거의 실사 (Q34)

- 발신: 2026-08-24, 운영 세션 · 수신: 외부 설계 담당
- 판정자 전제: **저장소 접근 없음.** 자기완결적이다 — 인용한 코드·수치·표는
  전부 실물이고 경로 참조로 대체한 곳이 없다.
- 성격: **D-33이 명한 (b\*)의 선행 실사.** 판정은 "referential ∃ 경계를 먼저
  독립 정의하고 그 qualification 통과 후에만 `O1_SCOPE_PROJECTION_V3`"이라
  했고 `operational_patch: forbidden`이므로, **우리는 경계를 제안하지 않는다.**
  gold가 그 경계를 그을 **증거를 기록하는지**만 실사해 올린다.
- 상태: **코호트 dispatch 누계 0건** 유지.
- 관련: **D-E2E-v1-33**(이 실사를 명한 판정) · **D-E2E-v1-27**(대명사를 측정
  어휘로 유지, control 2층 게이트) · **D-E2E-v1-31** Q31.4(measurand 오염)

## 1. 이 문서가 새로 가져오는 것 — **두 source가 서로 반대로 인코딩한다**

Q33은 PMB만 보고 상신했다. D-33 수령 후 **FOLIO를 실사했더니 같은 현상을
반대로 인코딩한다.** 이것이 이 문서의 핵심이다.

| source | 지시 표현(고유명·대명사·지시사)을 어떻게 인코딩하나 | 결과 |
|---|---|---|
| **PMB gold (SBN)** | 개념 노드 → 어댑터가 **∃ 결박자** 생성 | oracle에만 결박자가 늘어 서명이 갈린다 |
| **FOLIO gold (FOL)** | **상수(constant)** → 어댑터가 `entity` 항 생성 | subject의 자연스러운 `entity`와 **일치한다** |

실물:

```text
PMB   "Nobody encouraged him."
      male.n.02                    % him   ← 개념 노드 → ∃y[male(y)]
FOLIO "People who can catch balls are good wide receivers."
      ∀x ∃y (CanCatch(x,y) ∧ Ball(y) → Good(x, widereciever))
                                              ↑ 상수
```

규모: FOLIO 적격 풀 **799건 중 116건(14%)** 이 상수를 쓴다. 표본이 아니라
전수다. 예: `summer1972olympics`(654p3) · `berlinzoo`(696p4) ·
`year1990`(393p1) · `widereciever`(142p1).

**따라서 현재 계약은 같은 언어 현상을 corpus에 따라 다르게 채점한다.**
"Tom이 무언가를 했다"가 PMB에서 오면 결박자 하나가 더 필요하고 FOLIO에서
오면 필요하지 않다. 이것은 우리가 정규화를 원한다는 주장이 아니라, **승인된
두 source가 이미 서로 다른 규약을 갖고 있고 측정이 그 불일치를 물려받았다**는
실측이다.

## 2. 동결 코호트 20건에서 문제의 분포

| source | 건수 | 지시 표현 문제 |
|---|---:|---|
| PMB | 15 | **있다** — 고유명·대명사·지시사가 전 층에 퍼져 있다(Q33의 전수 표) |
| FOLIO | 5 | **거의 없다** — 5건 중 상수를 쓰는 것은 `FOLIO-142p1` 하나(`widereciever`)이고, 나머지 4건은 상수 0 |

즉 이 문제는 **in-N의 3/4에 해당하고 한쪽 source에 국한**된다.

## 3. PMB 쪽 실사 — gold는 증거를 기록하지만 **이 corpus에서 synset alone은 부류를 식별하지 못한다**

PMB fixture 20건(in-N 15 + control 5)의 개념 노드 **93개 전수**.

gold는 각 개념 노드에 **표면 토큰을 주석으로 기록**한다:

```text
person.n.01                                  % Nobody     [0-6]
encourage.v.02 Agent -1 Time +1 Recipient +2 % encouraged [7-17]
male.n.02                                    % him        [18-22]
```

그래서 증거는 원리적으로 존재한다. 그러나 **synset 하나가 여러 부류에 걸친다**:

| synset | 양화 용법 | 지시 용법 | 보통명사 용법 |
|---|---|---|---|
| `person.n.01` | `Everyone` · `Some` · `Nobody` | `I` · `you` | `passengers` |
| `entity.n.01` | `everything` · `some` | — | — |

`person.n.01` 하나가 세 부류다. D-33 §6("`male.n.02` 하나만 보고 제거하면 안
된다")이 실측으로 확인됐다.

## 4. 표면 규칙을 네 번 시도해 네 번 다르게 실패했다

경계를 만들려는 시도가 아니라 **규모를 재려는** 시도였는데도 그랬다.

| 시도 | 실패 형태 |
|---|---|
| 1 | 양화 대명사(`everyone` — 양측이 모두 양화)와 지시 표현(`him` — oracle만 양화)을 **섞었다** |
| 2 | 부정관사 ∃가 혼입했다 |
| 3 | SBN의 **ANSI 이스케이프**가 표면 토큰을 오염시켰다(`person.n.01 ← '\x1b'` ×7) |
| 4 | ANSI를 고치자 **문두 대문자**를 고유명으로 오분류했다(`'Not everyone'` → 지시). 이것은 우리 control 적격 술어에 **이미 문서화된 같은 누출**이다 |

그래서 **분류기 제작을 중단했다.** 계속하면 `operational_patch: forbidden`
위반이고, 도구 능력이 의미 경계를 정하게 된다.

**주장의 범위**: 말할 수 있는 것은 **"현재 시도한 표면·구문 proxy로는 경계를
안정적으로 추출할 수 있다는 증거가 없다"**이고, "원리적으로 불가능하다"가
아니다. (이 문단은 상신 후 D-33 재검증(D-33-V §7)의 요구로 범위를 좁힌 것이며,
상신 시점 본문의 주장을 철회하는 것이 아니라 강도를 정확히 한 것이다.)

## 5. 판정문 §5의 계약 필드에 대해 — **가/불가를 나누지 않고 증거만 보고한다**

D-33은 `REFERENTIAL_EXISTENTIAL_QUALIFICATION_V1`의 조건 5개를 제시했다.
그것을 "우리 도구가 판정 가능한가"로 읽으면 **정의/자동화 순서가 뒤집힌다**
(도구 능력이 의미 경계를 정하게 된다). 그래서 각 조건에 대해 **gold가 어떤
증거를 기록하는가**만 적는다.

| 조건 | gold가 기록하는 것 | 기록하지 않는 것 |
|---|---|---|
| `referent_introduction` | 표면 토큰(PMB 주석) · 상수 여부(FOLIO) | 그 토큰이 특정 참여자를 도입하는지의 판단 |
| `quantificational_force` | 표면 한정사 어휘(`every`·`some`·`no`) | `someone` 대 `him`처럼 **둘 다 사람을 가리키는** 경우의 force 차이 |
| `scope_bearing_role` | 어댑터가 만든 결박자 위치 | 그 결박자가 **의미상** scope를 만드는지 |
| `representation` | SBN role(`Agent`·`Recipient`) · FOL 항 종류 | — |
| `semantic_class` | synset(`male.n.02`·`person.n.01`) | **§3이 보인 대로 이 corpus에서 synset alone은 부류를 식별하지 못한다** |

## 6. 우리가 판정에 청하는 것

- **(a)** §1의 cross-source 불일치가 경계 정의의 근거가 되는가 — 즉 "FOLIO가
  지시 표현을 상수로 두므로 PMB의 대응물도 measurand 밖"이라고 읽어도 되는가.
  이것은 **의미론이 아니라 두 승인 source의 규약 비교**에 근거한 논거다.
- **(b)** 아니라면, 경계를 그을 증거로 무엇을 더 실사해야 하는가. §5 표의
  "기록하지 않는 것" 칸이 우리가 못 가진 것이다.
- **(c)** 경계 정의가 원리적으로 불가하다면 in-N의 PMB 15건을 어떻게 하는가 —
  D-33이 (d)(재료 제외)를 기각했으므로 대안이 필요하다.

**운영 세션은 (a)를 선호하지만 권고하지 않는다.** (a)가 채택되면 경계는
"어느 source의 규약을 정본으로 볼 것인가"의 문제가 되고, 그것을 우리가
정하면 `operational_patch`다. 그리고 §7의 한계 때문에 (a)의 근거 자체가
완전하지 않다.

## 7. 이 실사의 한계 (숨기지 않는다)

- **FOLIO 상수 사용은 잡음이 있다.** ~~116건을 부류별로 분류하지 않았다.~~
  **닫혔다(2026-08-24, 상신 후)**: 116건·상수 출현 160회를 전수 관측했고,
  분명히 지시적인 것은 **13%**(숫자 포함 7% + 대문자 포함 6%)이며
  **67%(108회)가 미결정 소문자 단일어**로 `music`(물질명사)·`stonefish`
  (보통명사)가 섞여 있다. **§1의 프레이밍을 정정한다** — FOLIO는 지시 표현이
  아닌 것에도 상수를 쓴다. 같은 감사 문서 참조.
- ~~**PMB 쪽 전수는 20건이다**~~ **닫혔다(2026-08-24, 상신 후)**: gold
  12,053 문서 전수를 실측했다 — 지시 후보 부류 노드 **15,810개**, 그중 닫힌
  양화 어휘가 해결하는 것은 **2%**이고 **96%(15,193)가 미결정**이다.
  `experiments/2026-08-23_e2e_v1_c_o1_cohort/REFERENTIAL_BOUNDARY_AUDIT_20260824.md`.
- **판정문 §3의 의미론 주장**(`someone`과 `him`의 quantificational force가
  다르다)은 우리 도구로 검증하지 못했다. 우리가 가진 것은 인코딩과 표면
  토큰이고 그것은 의미론의 증거이지 의미론이 아니다.
- FOLIO-175p1의 gold FOL이 `∀x (Lab(x) → Cheaper(x))`인 것을 실사 중
  발견했다 — "All monitors equipped in the lab are cheaper than their original
  prices"에서 비교 구문 전체가 사라진다. 이것은 Q33의 주제가 아니라 **gold
  추상화 대 충실 독해**의 별개 문제이고, control 실패 부류로 이미 기록돼
  있다. 여기 적는 것은 같은 fixture를 보는 판정자가 혼동하지 않게 하기
  위해서다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 이 실사를 명한 판정 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · 선행 상신 [[DESIGN_REQUEST_referential_participant_quantification|Q33]] · **보충** [[DESIGN_REQUEST_referential_boundary_corpus_scale|Q34-B]](§7 한계 둘을 닫았다)
- 관련 판정 [[DESIGN_DECISION_equivalence_idioms|D-27]] · [[DESIGN_DECISION_definite_scope_and_material_rules|D-31 Q31.4]]
