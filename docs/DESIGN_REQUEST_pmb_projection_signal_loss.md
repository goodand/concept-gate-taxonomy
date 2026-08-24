# DESIGN REQUEST — projection의 신호 소실과 층 술어 결함 (Q28)

- 상신: 2026-08-23, 운영 세션 (V5 구현 중, **fixture 실물을 처음 읽어** 적발)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: V5 동결 정지. 본 코호트 dispatch는 여전히 **0건**.

## 1. 배경 (필요한 최소한)

문장 단위 양화 scope 컴파일 실험. subject(무도구 LLM)가 영어 문장을 IR
6종(forall/exists/and/pred/not/implies)으로 컴파일하고, oracle(외부 gold를
결정적 adapter로 IR화)과 비교한다. 채점은 **O1ScopeMatch**: 양측을
`O1_SCOPE_PROJECTION_V1`로 투영한 signature 사이 exact structural match.

투영 규칙(선행 판정 D-25가 명령): PMB의 neo-Davidsonian 비계 — 사건/시간
변수와 그 존재양화, 의미역 술어(Agent/Experiencer/Time/EQU…), **동사
synset(`*.v.NN`)** — 를 채점에서 제외하고 scope 구조만 남긴다. 이것이
"PMB oracle이 사건 의미론 granularity라 full-IR 비교로는 15/15
구조적 실패"라는 결함(F3)의 해소책이었다.

fixture 20 = PMB 15(층 5종: 비례 1·양화부정 4·단순보편 4·기수 3·단순존재 3)
+ FOLIO 5. 층 배정은 동결 술어 `pmb_stratum`(정규식·구조 규칙)이 한다.

선행 판정 D-27이 방금 확정한 구분: **Measurement Satisfiability(형식적
가능성, 결정론 witness)는 필요조건이며 자연 도달성의 충분조건이 아니다.**
control이 그 간극의 경험적 측정기다.

## 2. 실측 사실 — fixture 실물 15문장을 처음 읽어 발견

지금까지의 모든 검증(동결 전 23/23, 자격 게이트, smoke S1~S3, V2↔V4 diff,
satisfiability 전수)은 **해시·구조 무결성**을 검증했고 **재료의 내용을 읽지
않았다**. 실물을 읽자 3건이 즉시 드러났고 전부 기계 확인했다.

### G3 (최중대) — projection이 PMB oracle의 **본문을 비운다**

"Everyone smiled." (단순보편 층)

| | 투영 골격 |
|---|---|
| oracle | `∀(T;(□→T))` |
| subject의 자연 출력 `∀x(everyone(x)→smiled(x))` | `∀(T;(□→□))` |
| 채점 | **fail** |

원인: PMB는 동사를 사건 술어(`smile.v.01` + Agent role)로 인코딩하고
투영 규칙은 그것을 비계로 제거하므로 **oracle 본문이 `True`로 붕괴**한다.
subject는 동사를 술어로 내므로 구조가 항상 갈린다.

**단순보편 층 4건이 전부 동일 골격 `∀(T;(□→T))`** 다("Everyone smiled" /
"Everyone screamed" / "Everybody jumped" / "Everybody wants to win").
즉 (i) 측정 신호가 사실상 없고(∀ 1개 + 제한식 술어 1개 이상의 정보 부재),
(ii) 구조적 실패가 예정돼 있다.

**satisfiability는 통과한다** — witness가 "본문 True" 형태를 그대로
재현하므로. 그러나 그 형태(동사를 빼먹은 컴파일)를 subject가 낼 이유가
없다. D-27이 인정한 satisfiable ⇏ naturally reachable의 **대량 사례**다.

### G1 — 층 술어의 최상급 오분류 (운영 세션 설계 결함, V1부터 존속)

비례 층의 유일 항목: "The **most beautiful** flowers have the sharpest
thorns." — 동결 술어가 `\bmost\b` 정규식으로 잡았으나 이는 **최상급**이고
비례 양화가 아니다. 투영 골격은 `∃(T;∃(T;∃(T;∃(T;∃(T;∃(T;□∧□∧□∧□∧□∧□))))))`
— 양화 scope 구조가 아니라 사건 참여자 나열이다. **V1~V4 네 번의 동결이
모두 이 항목을 통과시켰다.**

### G2 — 기수 층이 방언으로 표현 불가

기수 층 3건: "Several children are playing in the sand." / "Many a quarrel
comes about through a misunderstanding." / "How many grams in an ounce?"
(의문문). 투영 골격은 각각 `∃(T;∃(T;□∧□))`, 동형, `∃(T;∃(T;∃(T;□∧□∧□)))`
— **기수 정보가 골격에 전혀 남지 않는다**(O1 방언에 기수 constructor 부재).
또한 several/many는 운영 세션이 control 술어에서 "미지원 한정사"로 배제한
어휘인데 in-N에는 들어와 있다(층 술어에 그 제약이 없었다).

## 3. 판정 질문

### Q28.1 — G3: PMB 본문 소실의 처리

- (a) **투영 규칙 개정**: 동사 synset을 무조건 비계로 보지 않고, **사건
  변수의 주술어(main event predicate)는 유지**하되 role 술어·시간·중간
  ∃만 제거한다. 그러면 "Everyone smiled" oracle이 `∀(T;(□→□))`가 되어
  subject의 자연 출력과 정합한다. 우려: 주술어를 남기면 arity 문제가
  돌아온다 — oracle의 `smile.v.01(e)`는 사건 1항, subject의
  `smiled(x)`는 개체 1항이고 **결박 대상이 다르다**(e vs x). 즉 단순
  유지로는 부족하고 "사건 술어를 그 유일 참여자에 재결박"하는 규칙이
  필요한데, 그것이 D-25가 금지한 formula 재작성인지 판정 필요
- (b) **PMB 단순보편·단순존재 층을 O1-v1에서 배제**하고 FOLIO형(직접
  술어 논리) source로만 in-N을 구성 — governance 파급: D-21의 "유일 수용
  source 금지"가 역전되어 FOLIO 단독이 된다(§Q28.3과 결합)
- (c) 채점 차원에서 "본문 비어 있음"을 UNSCORABLE로 회계하고 그 fixture를
  분모에서 제외 — 운영 세션 반대: 사전등록된 N이 실행 중 줄어드는 것은
  D-19가 금지한 형태에 가깝다
- (d) 그 외

### Q28.2 — G1·G2: 층 술어와 층 구성

- (a) **층 술어 정정 + 층 구성 축소**: 최상급 `most`를 비례에서 배제
  (`most of`·`most N` 형태만 인정), 기수 층은 **O1 방언에 기수
  constructor가 없으므로 삭제**하고 그 3건을 양화-부정·단순존재로 재배분.
  N=20 유지. 운영 세션 권고
- (b) 기수 constructor를 방언에 추가 — 운영 세션 비권고: D-26에서 implies를
  추가한 것과 달리, 기수는 **새 의미 현상**(수량 비교)이므로 estimand 확장
  이다(D-26 §2의 구분 기준을 그대로 적용하면 불허 쪽)
- (c) 그 외

### Q28.3 — 근본: PMB의 O1-v1 source 적합성 재판정

실측 사슬이 한 방향을 가리킨다: PMB gold는 **사건 의미론 표상**이고 O1은
**문장 단위 양화 scope**를 측정한다. F3(full-IR 불가) → D-25 projection
(비계 제거) → G3(본문까지 소실). 즉 비계를 남기면 측정 불가, 제거하면
신호 소실이다. 중간 지점이 존재하는지가 Q28.1이지만, 존재하지 않는다면
PMB는 이 estimand의 source로 부적합할 수 있다.

- (a) Q28.1(a)가 성립하면 PMB 유지
- (b) 성립하지 않으면 **PMB를 O1-v1에서 제외**하고 D-21 §7-8의 "유일 수용
  source 금지"를 이 경우에 대해 재판정(제2 source 재조사 vs 단독 허용)
- 판정을 청함. 어느 쪽이든 **PMB 15건의 성적을 관측한 적이 없으므로**
  outcome-conditioned 결정이 아니다(dispatch 0건).

### Q28.4 — 절차: 재료 내용 검사의 게이트화

이 결함들이 4번의 동결과 수십 개 게이트를 통과한 원인은 하나다: **모든
검증이 해시·구조·형식이었고 fixture의 실제 문장과 투영 골격을 사람이
읽는 단계가 없었다.** G1은 문장 한 줄만 읽으면 즉시 보인다.

- 제안: 동결 전 필수 산출물로 **"fixture 실물 대조표"**(문장 + oracle 투영
  골격 + 층 배정 + 예상 subject 형태)를 만들고, 운영 세션이 항목별로
  읽었음을 기록하는 것을 절차에 넣는다. D-27의 Gate A/B에 이어
  **Gate C(재료 내용 검토, 사람)**로 명명할지 판정을 청함.
- 부수: 이 게이트가 있었다면 G1·G2는 V1 동결 전에, G3는 D-25 적용 직후에
  잡혔다.

## 4. 검증 재현

- 15문장 실물 + 투영 골격: 캐시된 PMB gold에서 `pmb_stratum` 층 배정과
  `project_scope_for_case`를 순차 적용하면 §2의 표가 그대로 재현된다
- G3 1줄 재현: "Everyone smiled." oracle 투영 = `∀(T;(□→T))` vs
  `∀x(everyone(x)→smiled(x))` 투영 = `∀(T;(□→□))` → evaluate = fail
- 부수 기록(이번 세션의 다른 실측): D-27 Q27.2 표면 필터 재census 결과
  층별 충족(양화 대명사를 제외 목록에서 빼야 함 — 운영 세션의 첫 lexicon이
  범위를 초과해 quantifier_negation_scope를 1/4로 붕괴시켰다), 문두 고유명
  누출 29건은 SBN `Name` role 병용으로 봉합. curry 정규화(D-27 Q27.1)는
  구현·계약 완료(뮤테이션 3/3 적중).

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
