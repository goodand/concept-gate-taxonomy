# DESIGN REQUEST — 제한식 투영: 비-scope 내용의 지위 (Q32)

- 상신: 2026-08-24, 운영 세션 (D-31 Q31.4가 명한 후속 판정)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: **이것이 현재 유일한 설계 차단 요인**이다. 재료(기수 3·비례 1)와
  권리는 해소됐고 배제 규칙·중복 정책은 D-31이 확정했다. 본 코호트 dispatch는
  여전히 **누계 0건**.
- 선행 판정 D-31 Q31.4가 이 상신을 **명령**했다(실물 인용):
  > "이는 scorer projection 정의를 바꾸므로 `measurement contract change`입니다.
  > 따라서 별도 판정으로 올리는 것이 맞습니다. … `operational_patch: forbidden`"

  운영 세션은 그 금지를 지켰다 — 투영·비교층 변경 **0건**이다.

## 1. 배경 (필요한 최소한)

문장 단위 의미 컴파일 실험. subject(무도구 LLM)가 영어 문장을 IR로 컴파일하고,
oracle(외부 gold를 결정적 adapter로 IR화)과 비교해 채점한다.

**선언된 measurand**: quantifier scope 컴파일 능력. 층은
`[quantifier_scope, generalized_quantifier, cardinal_quantifier,
proportional_quantifier, multi_quantifier_scope]`.

**방언 8종**: `forall / exists / and / or / not / implies / pred` +
`count`(기수) · `prop`(비례). 항은 변수·개체뿐이다. **한정성·정의성을 표현할
구성자가 없다.**

**채점** `O1ScopeMatch`: 양측을 투영한 signature 사이 exact structural match.
투영의 현재 성질(선행 판정들이 확정):
- 술어 **라벨은 익명화**된다(WSD 잡음 배제 — 모든 `pred.name`이 하나의 slot 기호로).
- desugar가 `FORALL(x,R,B) → FORALL(x,True,implies(R,B))` 로 정규화한다. 즉
  **제한식 내용은 `implies.left`에 있다.**
- 사건 의미론 비계는 제거된다(사건 술어의 어휘 진리값을 버리고 참여자 결박
  incidence만 무라벨 slot으로 보존 — 동치를 주장하지 않는 측정 함수).
- 허용된 정규화는 **닫힌 열거 표**(현재 curry 1쌍)뿐이다.

**선행 판정들이 금지한 것**: 힘을 바꾸는 재작성, 양화 재배열, 경계를 넘는 함의
이동, 일반 정리-동치 정규화, 선언된 boundary의 조용한 축소, ambiguity를
uniqueness로 바꾸는 노드 제거.

## 2. 실측 사실

### F1 — scope-only 불변성이 깨진다 (D-31이 확인, 우리가 재현)

D-31이 요구한 불변성:

```text
scope topology 동일 + 비-scope 제한식 술어 내용만 다름 → O1ScopeMatch 동일
```

실측(투영 직접 호출):

| oracle | subject | signature 일치 |
|---|---|---|
| `count(eq,2,x, and(previous(x),exorcism(x)), fail(x))` | 형용사 포함 | **일치** |
| 같음 | **형용사 누락**(`exorcism(x)`만) | **불일치** |

즉 subject가 `two exorcisms`의 scope를 정확히 맞추고 수식어만 빠뜨리면 FAIL이고,
그 실패가 **scope 컴파일 능력으로 귀속**된다. `ScopeOnlyInvarianceViolated = True`.

라벨이 익명화되므로 채점되는 것은 어휘가 아니라 **제한식 노드의 개수·구조**다.

### F2 — 이것은 신규 결함이 아니다. **동결 코호트에 이미 있다**

동결된 V4 코호트의 PMB 15건을 adapter로 재생해 투영 후 (제한식, 본문) 채점
노드 수를 측정했다.

| case_id | 표면 (Tatoeba/CC-BY) | (제한식, 본문) |
|---|---|---|
| `PMB-p43-d3444` | Is everything you own in that chest? | **(2, 1)** — 관계절이 제한식에 |
| `PMB-p00-d1657` | Everybody except Joe went to the party. | **(2, 1)** — 예외구가 제한식에 |
| 나머지 13건 | — | 제한식 0 또는 1 |

MRS 쪽 적격 4건도 같은 분포다: 크기 1이 3건, **크기 2가 1건**
(`Two previous exorcisms have failed.` — 형용사 + 미지어휘 명사).

**따라서 이 변경은 MRS 재료에 한정되지 않는다.** 투영을 고치면 동결된 20건의
채점 성질도 바뀌므로 **재동결 범위가 코호트 전체**다. 이것이 D-31이
"단순 bug fix가 아니다"라고 쓴 이유의 실측이다.

### F3 — 판정이 보존을 명한 쪽은 **이미 보존된다**

D-31은 붕괴 대상을 비-scope 내용으로 한정하고, 제한식 내부에 실제 양화 구조가
있으면(`a representative of every company`의 `every`) 그 topology는 지우지
말라고 명했다.

실측: 제한식에 중첩 `forall`을 가진 식과 평평한 2술어 식의 signature가
**구별된다**. 즉 **후속 투영이 만들어야 하는 것은 붕괴 절반뿐**이고 보존
절반은 현 투영에서 이미 성립한다.

단 이 확인은 **합성 입력**으로 했다 — 실물 재료에서 제한식 내부에 중첩 양화가
있는 사례를 아직 찾지 못했다(P15 관점에서 잠정).

### F4 — 동결 표면 영향

manifest V4의 `contract_hashes`에 `projection_module_sha256`이 **핀**돼 있다.
투영 모듈을 고치면 V4 동결이 실효되고, 그 실효를 **주장하는** 게이트가 이미
있다(`FREEZE_STATE`가 SUPERSEDED면 drift가 *존재해야* 통과한다 — 선언이 거짓일
수 없게). 현재 V4는 이미 `V4_SUPERSEDED_BY_D27_IMPLEMENTATION__V5_PENDING`이다.

### F5 — 본문(BODY) 쪽도 같은 구조다

같은 논거가 본문에도 적용된다. 본문의 비-scope 술어 내용 역시 채점되는데
선언된 measurand는 scope다. 다만 본문에는 **선행 판정이 이미 부분 처리**를
넣었다 — 사건 술어의 어휘 진리값을 버리고 참여자 incidence만 무라벨 slot으로
보존한다(그 판정의 근거: `∃e(Smile(e)∧Agent(e,x)) ≢ Smile(x)`이므로 재작성이
아니라 측정 함수여야 한다). 즉 제한식과 본문의 처리가 **비대칭**이다.

## 3. 판정 질문

### Q32.1 — 붕괴의 단위 ★

제한식의 비-scope 내용을 무엇으로 접는가. 라벨은 이미 익명화되므로 남는 자유도는
**개수와 구조**다.

- (a) **비-scope 내용 전체를 단일 opaque atom으로.**
  `and(previous(x), exorcism(x))` → `RESTRICTION_ATOM(x)`.
  결과: 수식어 유무가 채점에서 사라진다(F1 해소). 우려: 제한식이 **비어 있는
  경우**(bare `exists`)와 내용이 있는 경우를 구별할 수 있어야 하는데, atom
  하나로 접으면 "내용 있음/없음"만 남는다 — 그것으로 충분한가
- (b) 술어 **개수는 유지**하고 라벨만 익명화(현재 동작). F1이 그 결과다
- (c) **결박 변수 집합만** 유지 — `RESTRICTION(x)` 처럼 어떤 변수를 제한하는지만
  남기고 내용은 전부 접는다. (a)보다 강하다
- (d) 그 외

부수: (a)/(c)를 택하면 **비어 있는 제한식과 내용 있는 제한식의 구별**을 유지할
것인가. 유지하지 않으면 `exists(x, True, B)`와 `exists(x, dog(x), B)`가 같은
signature가 되고, 그것은 generalized_quantifier 층의 측정을 비운다.

### Q32.2 — `scope-bearing`의 정의

붕괴에서 **보존**할 연산자 집합을 확정해야 한다.

- `forall`·`exists`·`count`·`prop`은 명백히 scope-bearing이다.
- **`not`은?** 선행 판정이 `quantifier_negation_scope`를 **독립 층**으로 두었고
  부정은 양화와 상호작용하는 scope를 갖는다. 제한식 내부의 `not`을 접으면 그
  층의 측정이 훼손될 수 있다.
- **`implies`는?** desugar가 만들어내는 것이므로 구조적 산물이다. 그러나 원문에
서 온 `implies`(FOLIO 계열)도 있다. 둘을 구별해야 하는가.
- `and`/`or`는 scope-bearing이 아니지만 **`or`는 논리 구조**다. 제한식 안의
  `or`를 접으면 `dog(x) or cat(x)`와 `dog(x)`가 같아진다.

닫힌 열거로 확정해 주기를 청한다.

### Q32.3 — 동결 코호트 2건의 처리

F2의 `PMB-p43-d3444`(관계절)·`PMB-p00-d1657`(예외구)은 새 투영에서 채점 성질이
바뀐다. 두 건은 `single_universal` 층에 배정돼 있다.

- (a) 그대로 둔다 — 새 투영이 적용되면 제한식 내용이 접히고, 그 fixture는
  "보편 양화의 scope"만 측정하게 된다. 층 배정은 유효하다
- (b) 층을 재배정한다(관계절·예외구가 있는 것은 별도 층 또는 배제)
- (c) 배제한다 — 그러면 `single_universal`이 4건에서 2건으로 줄고 층 하한을
  다시 봐야 한다
- (d) 그 외

### Q32.4 — 동결 개정 절차

투영 모듈 해시가 `contract_hashes`에 핀돼 있으므로 이 변경은 V4 동결을 다시
실효시킨다(이미 SUPERSEDED 상태다). V5 재동결 시 이 변경을 어떻게 기록하는가 —
D-24가 만든 `PRE_EXECUTION_FREEZE_AMENDMENT_V1` 절차를 재사용하는가, 아니면
투영 profile 자체의 버전을 올려(`O1_SCOPE_PROJECTION_V2`) 신규 profile로 두는가.

후자라면 **V1~V4의 채점 성질과 V5의 채점 성질이 다르다**는 것을 어디에
선언하는가.

### Q32.5 — 본문 쪽 비대칭은 의도된 것인가 (부수 확인)

F5의 비대칭 — 본문은 사건 술어 어휘를 버리는 부분 처리가 있고 제한식은 없다.
Q32.1이 제한식을 접으면 비대칭이 반대로 커진다(제한식은 atom, 본문은 술어 개수
유지). 의도인지, 아니면 본문에도 같은 붕괴를 적용해야 하는지 확인을 청한다.

**주의**: 본문을 전부 접으면 선행 판정이 해소한 결함이 되살아날 수 있다 —
사건 술어를 비계로 제거해 oracle 본문이 `True`로 붕괴하고 단순보편 4건이 전부
같은 골격이 된 그 결함이다(그때의 해법이 F5의 incidence slot 보존이었다).

## 4. 검증 재현

- F1·F3: 투영 직접 호출(합성 입력, 4쌍)
- F2: 동결 manifest V4의 PMB 15건을 adapter로 재생 → 투영 → `implies.left`의
  채점 노드 수 측정. **주의**: `restriction` 필드로 세면 15/15가 0이 나온다 —
  desugar가 제한식을 `implies.left`로 옮기기 때문이고, 운영 세션이 그 오측정을
  한 번 했다가 "이질적 fixture 15개가 전부 0인 것은 불가능"이라는 판단으로
  잡았다(기록: `READ_LOG_20260824.md` §5)
- F4: `stage2_fixture_manifest_v4.json`의 `contract_hashes` ·
  `test_stage2_freeze_v4.py`의 `FREEZE_STATE`
- 게이트: 13 passed / 0 failed / 1 blocked(선택 의존성 부재)
- D-31 준수: 투영·비교층 변경 0건(부작위 검증)

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
