# DESIGN REQUEST — 한정사의 scope 지위 · 배제 규칙 확정 · 중복 처리 (Q31)

- 상신: 2026-08-24, 운영 세션 (D-30 구현 착수 전, Gate C 사람 감사 완료 후)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: full O1 재동결(V5)이 차단돼 있다. 본 코호트 dispatch는 **누계 0건**
- **이 요청서는 D-30을 실물에 적용한 결과다.** 판정이 틀렸다는 주장이 아니라,
  D-30이 정의한 절차의 한 단계("BODY 후보가 될 수 없는 label 제거")가 실물에서
  **어디까지를 뜻하는지** 미정이라는 보고다.

## 1. 배경 (필요한 최소한)

문장 단위 의미 컴파일 실험. subject(무도구 LLM)가 영어 문장을 IR로 컴파일하고,
oracle(외부 gold를 결정적 adapter로 IR화)과 비교해 채점한다.

**확정된 계약**
- subject 방언 8종: `forall / exists / and / or / not / implies / pred` +
  `count`(기수)·`prop`(비례). 항은 변수·개체뿐이고 **한정성·정의성을 표현할
  구성자가 없다.** `count = {rel∈{eq,ge,le,gt,lt}, num:int, var, restriction, body}`,
  `prop = {rel∈{most}, var, restriction, body}`. 둘 다 자체 결박자.
- 채점은 `O1ScopeMatch` — 양측을 투영(라벨 어휘·사건 의미론 비계 제거)한
  signature의 exact structural match. `rel`·`num`은 채점 대상.
- 적격 하한: **기수 ≥3, 비례 ≥1.**
- 선행 판정 **D-30 Q30.1**: `BODY_resolved(q) iff |AdmissibleBodyTargets(q)| = 1`.
  raw label count는 정의가 아니라 fast path. 절차는
  `RSTR 해소 → 제한식 내부 및 BODY 후보가 될 수 없는 label 제거 →
   scope topology와 모순되는 후보 제거 → admissible 계산 → 1이면 통과, 0·2+면 거부`.
  **외부 scope solver는 요구하지 않는다**(결정적 local completion만 허용).
- 선행 판정들이 금지한 것: 힘을 바꾸는 재작성, 양화 재배열, 경계를 넘는 함의
  이동, 선언된 boundary의 조용한 축소, 실패가 예정된 계약의 실행.
- 재료 출처: MRS(ERG/Redwoods 계열, Open SDP 1.2 배포본). 권리는 사용자 결정으로
  해소(개인 연구·외부 배포 없음). 저장소에는 표면 원문을 넣지 않는다.

## 2. 실측 사실 (전부 이 세션 실측, 37,060 record 파싱 기준)

### F1 — D-30 구현 후 적격 재료가 **하한과 정확히 같다(여유 0)**

Gate C **사람 감사**(집계가 아니라 실물 READ)를 거친 결과:

| 층 | 하한 | 적격 | 여유 |
|---|---:|---:|---:|
| cardinal | ≥3 | **3** | **0** |
| proportional | ≥1 | **1** | **0** |

감사에서 기각된 것: `_both_q + card(2)` 3건 · `_all_q + card(4)` 1건
(`both`는 "정확히 둘이 존재한다"가 아니라 전제된 2원소 집합에 대한 한정·보편이고
`count(eq,2)`로 옮기면 힘이 바뀐다) · `unknown_rel` 4건(ERG가 완전한 발화로
분석하지 못한 fallback) · 승수/측정 구문 6,181건 · 선언/범위 기수 · 수치 지정자.

### F2 — 제2 source(PMB)는 기수·비례를 **원리적으로** 공급하지 못한다

PMB gold en **12,053건** 전수. SBN은 수량을 극성 표지 `Quantity -`/`+`(막연한
소/다)로 인코딩하고, 진짜 수사(부호 없는 정수)는 **106 occurrence**뿐이며 전부
배제 사유다: 측정·단위 67 · `both` 19 · 다중 문장 record 9 · 부분격 `N of the X` 8
· 분수 수사 3 · **잔존 0**. 따라서 MRS가 **유일한 공급원**이고 F1의 여유 0이
그대로 하한을 결정한다.

### F3 — 한정사가 admissible BODY 경쟁자로 남아 있다

`_most_q` 보유 record는 대부분 admissible이 4~18개다. 그러나 admissible이
**정확히 2개**인 근접 사례가 6건이고, **6/6의 동반 양화가 `_the_q` 하나**다.
실물 표면:

- `The dollar gained against most foreign currencies.`
- `The practice is, however, legal in most cases.`
- `Most sleep on the floor.`

한정사·고유명·대명사 양화(`_the_q`·`proper_q`·`pronoun_q`·`def_explicit_q`)를
admissible BODY 경쟁자에서 제외하면:

| 층 | 현재 | 한정사 제외 시 |
|---|---:|---:|
| proportional | **1** | **7** (+6) |
| cardinal | 11(사람 감사 전) | **104** (+93, 감사 전) |

**+93은 Gate C 감사를 거치지 않은 수다.** 확실한 것은 후보 풀이 11이 아니라
**100 규모**라는 것이고, 여유 0이 해소될 수 있다는 것이다.

### F4 — 관계 다양성과 BODY 유일성이 같은 재료에서 충돌한다

사상 가능 수식어(`_at+least_x_deg`·`_more+than_p`)가 `card`와 label을 공유하는
경우 **78건**. label 일치 78/78 통과, **BODY 유일성 0/78**(전부 다중 양화).
실물이 이유를 말한다 — `at least N`은 긴 문장에만 나타난다:

- `The plan calls for closing at least nine plants and eliminating about 3,600 jobs.`

따라서 현재 `rel_coverage`는 전수 확정값으로 `{eq:3, ge:0, gt:0, le:0, lt:0}`이다.
F3의 한정사 판정이 이 수치도 바꿀 가능성이 있다(미측정).

### F5 — 운영 세션이 만든 배제 규칙 15종 중 3종이 판정 없이 확정 불가

전수 실측으로 규모가 확인된 것(공허하지 않음): 측정 명사 label 공유 9,758 ·
사상표 밖 관계 수식어 297 · **MRS 바이트 동일 중복 428**.

판정이 필요한 것은 아래 세 종이다(§3).

### F6 — 기존 코호트가 이미 머리명사를 넘는 제한식을 채점한다

`20413069`("Two previous exorcisms have failed.")의 제한식은 형용사+명사로
채점 크기 2다. 기각 여부가 하한을 좌우하므로 동결 V4의 PMB 15건을 adapter로
재생해 측정했더니 **이미 2건이 크기 2**였다(관계절 `Is everything you own in
that chest?` · 예외구 `Everybody except Joe went to the party.`). 따라서
`20413069`을 기각하지 않았다. **이것은 보고이고 질문이 아니다** — 다만 그
설계가 의도된 것인지는 §3.4에 부수 확인으로 올린다.

## 3. 판정 질문

### Q31.1 — 한정사는 admissible BODY 경쟁자인가 ★최우선

D-30 Q30.1의 절차 2단계는 "**BODY 후보가 될 수 없는 label 제거**"다. 한정사가
그 범주에 드는가가 미정이다.

- (a) **한정사·고유명·대명사 양화를 경쟁자에서 제외한다.** 근거: 한정사는
  scope 경쟁에서 의미상 불활성(항상 최광역)이고, 우리 방언에 **한정성을 표현할
  구성자가 없으므로** 그 양화는 어차피 measurand가 아니다. 결과: 비례 1→7,
  기수 후보 11→104. **운영 세션은 권고하지 않는다** — 이 방향은 재료를 늘리는
  쪽이고, 그런 제안이 3연속 기각된 이력이 있다
- (b) 유지한다(모든 양화 EP가 경쟁자). 결과: 여유 0이 유지되고, MRS가 유일
  공급원이므로 한 건만 더 탈락하면 하한이 깨진다
- (c) 한정사를 **경쟁자에서는 제외하되 fixture 자체를 배제**한다(한정사가 있는
  문장을 쓰지 않는다). 결과: 근접 6건 전부 탈락, 여유 0 유지
- (d) 그 외

부수 질문: (a)라면 제외 목록을 **닫힌 열거**로 두는가(`_the_q`·`proper_q`·
`pronoun_q`·`def_explicit_q`·`def_implicit_q`), 아니면 "RSTR가 유일 개체를
지시하는 양화"라는 **성질**로 정의하는가. 후자는 판정에 새 판별 부담을 만든다.

### Q31.2 — 배제 규칙 3종의 확정

다음은 운영 세션이 실물 READ에서 만든 규칙이다. 계약으로 승인하는가.

```yaml
E13_disjunctive_or_range_cardinal:
  trigger: 같은 결박 변수에 card EP가 둘이고 _or_c / _and_c_btwn 로 결합
  예: "two or three bottles" · "between three and six judges"
  근거: 우리 count는 단일 num만 갖는다
  운영 세션 처리: REJECT (D-30 Q30.2의 변수별 규칙에도 걸린다)

E14_numeric_designator:
  trigger: 수사가 개수가 아니라 명칭
  예: "Intel 286 and 386 microprocessors"
  근거: 기수 양화가 아니다
  운영 세션 처리: REJECT

E15_non_entity_bound_variable:
  trigger: card.ARG1 이 개체 변수(x)가 아니다
  실측: 8,220건 전부 이 사유 (i 8,189 · e 31). 개체 변수인데 양화 0/2+는 0건
  예: "$1.5 billion" 의 card 는 ARG1=i (측정 구문의 미명세 개체)
  운영 세션 처리: REJECT
```

`E15`는 특히 술어 하나로 8,220건을 정리하며 승수/측정 판별자보다 단순하다.
**정본으로 채택할 만한가, 아니면 승수 판별을 label 공유로만 해야 하는가.**

### Q31.3 — MRS 바이트 동일 중복 428건의 처리

같은 문장·같은 MRS가 서로 다른 item id로 **428건** 존재한다(예: `20056005`와
`21771005`가 완전 동일). 선별이 중복을 제거하지 않으면 같은 문장이 두 trial로
셈되어 **fixture 독립성이 깨진다**.

- (a) **MRS 바이트 해시로 dedup**하고 잔존 대표 1건만 후보로 둔다
- (b) 표면 텍스트 해시로 dedup(MRS가 달라도 문장이 같으면 배제)
- (c) 중복을 허용하고 보고에만 표시
- (d) 그 외

부수: 선별 단위 튜플에 `mrs_sha256`을 넣어야 하는가(현재는 `text_sha256`·
`lf_sha256`).

### Q31.4 — 부수 확인: 제한식의 비-머리 내용은 measurand인가

F6이 보고한 사실 — 동결 코호트가 이미 관계절·예외구를 제한식에 담아 채점한다.
그 경우 subject가 scope를 정확히 맞추고도 수식어를 빠뜨리면 `O1ScopeMatch`가
FAIL이 되고, 그 실패가 **scope 컴파일 능력으로 귀속**된다.

의도된 설계인지 확인만 청한다(동결 표면이므로 운영 세션은 고치지 않았다).
의도가 아니라면 D-28의 event-incidence처럼 **비-머리 제한식 내용을 비계로
다루는** 후속 판정이 필요하다.

## 4. 검증 재현

- 실물 READ 기록: `experiments/2026-08-23_e2e_v1_c_o1_cohort/READ_LOG_20260824.md`
  (R1~R23, 측정기 오류 2건 포함)
- Gate C 감사: 같은 폴더 `GATE_C_MRS_AUDIT_20260824.md` · `GATE_C_PMB_AUDIT_20260824.md`
- 계약: `test_stage2_mrs_count_projection.py`(14) ·
  `test_cg_mrs_reader.py`(17) · `test_stage2_gate_c_table.py`(24)
- 게이트: 13 passed / 0 failed / 1 blocked(선택 의존성 부재)
- 이 세션이 정정한 자기 오류: `card` record 수(6,154→13,470) · "`rel` 재료
  부재" 주장(표본 n=3 일반화) · 측정기 2건(census 정규식·제한식 필드).
  전부 기록에 남겼다 — 요청서가 자기 오류를 숨기면 판정자가 같은 수치를 쓴다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
