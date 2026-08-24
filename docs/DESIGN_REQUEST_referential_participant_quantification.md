# DESIGN REQUEST — 지시 표현을 oracle이 참여자 ∃로 인코딩하는 것은 measurand인가 (Q33)

- 발신: 2026-08-24, 운영 세션 · 수신: 외부 설계 담당
- 판정자 전제: **저장소 접근 없음.** 이 문서는 자기완결적이다 — 인용한 코드·서명·
  표는 전부 실물이고, 파일 경로 참조로 대체한 곳은 없다.
- 성격: **측정 계약 질문 1건.** D-31 Q31.4(제한식 비-머리 내용 = measurand
  오염)와 **같은 부류의 다른 축**이다. Q31.4는 제한식 *내부 내용*을 다뤘고,
  이것은 **결박자 개수 자체**를 다룬다.
- 상태: **코호트 dispatch 누계 0건**(control만 실행). 이 질문은 사전 개정으로만
  답할 수 있다 — 관측 후에는 post-hoc이 된다. 그래서 dispatch를 보류하고 상신한다.
- 관련: **D-E2E-v1-27**(대명사 ∃를 측정 어휘로 유지·control 2층 게이트) ·
  **D-E2E-v1-31** Q31.4(measurand 오염, `operational_patch: forbidden`) ·
  **D-E2E-v1-32**(비-scope 내용 opaque 붕괴)

## 1. 무엇이 문제인가 — 한 문장

PMB gold는 **고유명·대명사·지시사**를 참여자 ∃로 인코딩하고, 자연스러운 subject는
같은 것을 `entity` 항으로 쓴다. 그러면 **oracle 쪽에만 결박자가 하나 더 생겨**
scope 서명이 갈린다. 이것이 능력 결함인지 인코딩 관례 불일치인지 계약이 정하지
않았다.

방언은 두 표현을 모두 허용한다(D-19 이후 `entity`는 항의 두 종류 중 하나다).
subject는 어느 쪽이 채점상 유리한지 알 수 없다.

## 2. 실측 — control 실패 2건의 서명 대조 (전부 실물)

`O1_SCOPE_PROJECTION_V2` 서명이다. `('atom', ...)`은 비-scope 내용을 변수
incidence 튜플로 접은 것(D-32), 숫자는 결박 순서로 정규화된 변수 id다.

**"Nobody encouraged him."**

```text
oracle : ('not', ('exists', ('atom', ()), ('exists', ('atom', ()), ('atom', ((1,), (2,))))))
subject: ('not', ('exists', ('atom', ()), ('atom', ((1,),))))
```

subject의 `¬∃` 선택은 oracle과 **일치했다**. 갈린 것은 "him"뿐이다. gold 원문이
그것을 개념 노드로 둔다(실물 — 주석의 대괄호는 문자 구간이다):

```text
     NEGATION <1
person.n.01                                   % Nobody     [0-6]
encourage.v.02 Agent -1 Time +1 Recipient +2  % encouraged [7-17]
time.n.08      TPR now                        %
male.n.02                                     % him        [18-22]
```

`male.n.02`는 어댑터에서 결박자 하나가 된다. subject는 같은 자리에
`entity "him"`을 썼다 — 결박자 0개.

**"He is anything but a fool."**

```text
oracle : ('exists', ('atom', ()), ('carrier', (('atom', ((1,),)), ('not', ('exists', ('atom', ()), ('exists', ('atom', ()), ('atom', ((2,), (3,)))))))))
subject: ('not', ('atom', (('he',),)))
```

subject는 "He"를 `entity`로 써서 결박자를 0개 만들었다.

이 부류는 **세 번 연속 재현**됐다: V4 control(CTRL4-06·CTRL4-02, 2026-08-23),
V5 control(CTRL5-02·CTRL5-06, 2026-08-24). 우연이 아니다.

## 3. 실측 — 동결 코호트 PMB 15건 전수 (집계 대신 표를 낸다)

각 행의 마지막 칸은 **실제로 채점되는** oracle 결박자다(V1 전처리 후 — 사건
비계 ∃는 이미 제거됐고 제한식은 desugar로 body에 합쳐져 `True`가 된다).

| case_id | 층 | 문장 | 채점되는 oracle 결박자 |
|---|---|---|---|
| `PMB-p00-d1657` | single_universal | Everybody except Joe went to the party. | forall · exists · exists |
| `PMB-p00-d1686` | single_universal | That story is a famous one that everyone knows. | exists · exists · exists · forall |
| `PMB-p00-d2298` | single_existential | I need some. | exists · exists |
| `PMB-p05-d1463` | single_existential | Some survived. | exists |
| `PMB-p06-d1718` | quantifier_negation_scope | Not everyone likes that book. | forall · exists |
| `PMB-p09-d2243` | proportional | The most beautiful flowers have the sharpest thorns. | exists ×6 |
| `PMB-p15-d0787` | quantifier_negation_scope | Not all children like apples. | forall · exists |
| `PMB-p36-d2853` | single_universal | Everyone smiled. | forall |
| `PMB-p36-d3354` | cardinal | There are few passengers on this train. | exists ×4 |
| `PMB-p43-d3167` | cardinal | Tom's essay had many typos. | exists · exists · exists |
| `PMB-p43-d3444` | single_universal | Is everything you own in that chest? | forall · exists · exists |
| `PMB-p69-d1730` | cardinal | I met Tom a few months ago. | exists · exists |
| `PMB-p76-d2248` | quantifier_negation_scope | Not everyone was happy. | forall · exists |
| `PMB-p87-d1860` | single_existential | Tom bought Mary some chocolates. | exists · exists · exists |
| `PMB-p93-d1717` | quantifier_negation_scope | Not everybody wins! | forall |

읽는 법의 예: **"Tom bought Mary some chocolates."** — oracle 결박자 3개
(Tom·Mary·chocolates). subject가 Tom·Mary를 `entity`로 쓰면 결박자 1개다.
scope 능력과 무관하게 서명이 갈린다.

대조로 **"Everyone smiled."**(결박자 1개, 지시 표현 없음)와
**"Some survived."**(1개)는 양측이 자연히 일치한다.

**규모를 단정하지 않는다.** subject가 실제로 어느 표현을 고를지는 dispatch
전에 알 수 없고, 우리가 만든 대리 지표는 두 번 정정해도 귀속이 흔들렸다
(양화 대명사 `everyone`과 지시 표현 `him`을 섞었고, 부정관사 ∃가 혼입했다).
**그래서 집계 대신 표를 낸다** — 판정자가 재료를 직접 보는 것이 낫다.
표를 보면 지시 표현이 있는 행이 다수이고, 그것이 PMB 전 층(단순보편·단순존재·
부정 scope·기수·비례)에 퍼져 있다는 것은 확실하다.

## 4. control 게이트는 이 위험을 인증할 수 없다 — 설계상 그렇다

2026-08-24에 D-27 §18의 승인대로 control을 재선별했고 **5/5 통과**했다(사슬 최초).
그러나 그 통과는 이 위험에 대해 **구조적으로 침묵**한다. 적격 술어가 지시
표현이 있는 문장을 배제하기 때문이다 — 실물 코드다.

```python
def has_excluded_participant(sentence: str) -> bool:
    """대명사(3종+재귀) 또는 고유명이 문장에 있는가 (D-27 Q27.2 표면 규칙)."""
    toks = _tokens(sentence)
    if any(t.lower() in EXCLUDED_PARTICIPANT_LEXICON for t in toks):
        return True
    return any(t[0].isupper() for t in toks[1:])   # 문두 제외 대문자 = 고유명 근사
```

`EXCLUDED_PARTICIPANT_LEXICON`은 인칭·소유·재귀·지시 대명사의 합집합이다.
그래서 통과한 control 5건은 전부 지시 표현이 없다: "All videos are visual." ·
"No one's watching." · "Some mechanical watches are automatic." ·
"Every vote counts." · "All humans eat."

**통과한 게이트가 배제한 위험을 보증한다고 읽으면 오독이다.** 이것을 인지한
것이 dispatch를 멈춘 이유다.

## 5. 왜 D-27이 이미 답한 것이 아닌가

D-27은 "PMB 대명사를 표면 필터에서 제외하되 **양화 대명사는 측정 어휘라
제외하지 않는다**"를 정했다. 그것은 **control 선별 규칙**이다 — 어떤 재료를
control로 쓸지의 문제다.

지금 묻는 것은 다르다: **in-N 코호트에서 그 불일치를 오답으로 셀 것인가.**
in-N은 필터로 빼지 않는다(모집단이므로). D-27은 그 경우를 다루지 않았다.

## 6. 왜 D-32가 이미 답한 것이 아닌가

D-32는 비-scope 내용을 opaque atom으로 접어 술어 라벨·개수를 버렸다. 그러나
**결박자는 scope 구조 자체**이므로 붕괴 대상이 아니다 — 접으면 측정 대상이
사라진다. 즉 D-32의 도구로는 이 문제에 손댈 수 없다. 그것이 이 질문이 별개인
이유다.

## 7. 묻는 것

- **(a) 오답으로 센다** — gold의 인코딩 관례를 맞추는 것까지 O1 능력에
  포함한다. 계약은 이미 그렇게 작동하므로 구현 변경 0. 대신 O1ScopeMatch는
  "scope 컴파일 + PMB 인코딩 관례 적중"의 합성 지표가 되고, 선언된
  scope-only measurand와 불일치한다(Q31.4가 위반이라 판정한 형태와 동형).
- **(b) 오염으로 보고 투영에서 대칭화한다** — 예: `entity` 항과 "제한식이
  지시 부류 술어 하나뿐인 ∃ 결박"을 서명에서 같게 만든다. scope-only
  measurand는 회복되지만 **결박자 개수를 정규화하는 첫 규칙**이 되고, 그
  경계를 우리가 임의로 그을 수 없다(어느 술어 부류까지가 "지시"인가 —
  `male.n.02`·`person.n.01`·`entity.n.01`·고유명 `Name` role·한정 기술까지?).
- **(c) 층별로 다르게 정한다** — 예: 부정 scope 층에서는 결박자 개수를
  세고, 기수 층에서는 세지 않는다.
- **(d) 재료를 바꾼다** — 지시 표현이 있는 fixture를 in-N에서 제외한다.
  비용: 사전등록이 **N=20 · PASS≥16**을 동결했으므로 fixture를 빼면 분모가
  바뀌고, 그것은 acceptance 규칙의 개정이다. 층 구성도
  `{단순보편 4, 부정scope 4, 단순존재 3, 기수 3, 비례 1, 다중양화 5}`로
  동결돼 있다(명시된 floor는 `multi_quantifier` 4/5 하나뿐이지만 구성 자체가
  commitment다). 그리고 이것은 **모집단을 측정 도구에 맞춰 깎는 것**이다.
- (e) 그 외

**운영 세션은 (b)를 선호하지만 권고하지 않는다.** (b)는 경계 설정이 필요한데
그 경계는 판정 사안이고, 우리가 정하면 D-31 Q31.4가 금지한
`operational_patch`가 된다. 우리 손으로 대칭화 규칙을 만들면 **측정 도구를
결과가 좋아지는 방향으로 고치는 것**과 외형이 같아진다 — dispatch 0건인
지금도 그렇다.

## 8. 함께 결정해 주시면 좋은 것

이 질문의 답이 (a)든 (b)든, **control 적격 술어가 in-N의 지배적 성질을
배제하고 있다**는 구조는 남는다. control은 capability benchmark가 아니라
measurement-chain sanity check라고 D-27 §17이 정했으므로 그 자체가 결함은
아니다. 다만 "control 통과"가 무엇을 보증하고 무엇을 보증하지 않는지를
계약에 명시할 필요가 있어 보인다 — 우리가 오독할 뻔했다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 직전 판정 [[DESIGN_DECISION_q_rstr_body_position|D-32-C]] · 같은 부류의 선행 판정 [[DESIGN_DECISION_definite_scope_and_material_rules|D-31 Q31.4]] · [[DESIGN_DECISION_equivalence_idioms|D-27]]
- 이 질문을 만든 실행 기록 [[concept-gate-h1-wt/experiments/2026-08-23_e2e_v1_c_o1_cohort/CONTROLS_RUN_V5_20260824|CONTROLS_RUN_V5_20260824]]
