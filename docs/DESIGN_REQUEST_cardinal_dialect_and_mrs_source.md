# DESIGN REQUEST — 기수 표현의 방언 지위와 MRS source 채택 (Q29)

- 상신: 2026-08-24, 운영 세션 (2차 source 조사 회신 검증 완료 후)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: full O1 재동결이 차단된다(기수 층 3건·비례 층 1건의 재료 부재).
  본 코호트 dispatch는 여전히 **0건**.

## 1. 배경 (필요한 최소한)

문장 단위 의미 컴파일 실험. subject(무도구 LLM)가 영어 문장을 IR로 컴파일
하고, oracle(외부 gold를 결정적 adapter로 IR화)과 비교해 채점한다.

**현재 확정된 계약**:
- subject 방언 6종: `forall / exists / and / pred / not / implies`,
  항은 변수·개체뿐. **수치 상수·비교자·집합 크기 연산이 없다.**
- 채점은 `O1ScopeMatch` — 양측을 투영(scope 구조만 남기고 사건 의미론
  비계·라벨 어휘 제거)한 signature 사이 exact structural match.
- O1의 선언된 semantic boundary(실물 인용):
  `[quantifier_scope, generalized_quantifier, cardinal_quantifier,
  proportional_quantifier, multi_quantifier_scope]`
- 사용자 결정: **full O1 유지**(기수·비례를 boundary에서 빼지 않는다).
  선행 판정이 두 갈래를 제시했고 그중 이쪽을 택했다.
- 선행 판정 D-E2E-v1-28: 기수 constructor 추가는 **declared boundary 확대가
  아니라 coverage 복구**다(이미 boundary에 있으므로). 단 그 형태는 미정이며,
  당시의 기수 후보 3건(several/many/how many)이 성격이 서로 달라 그 근거가
  되지 못한다고 판정했다.
- 선행 판정들이 금지한 것: 사건 논리식→참여자 논리식 **재작성**,
  양화 경계를 넘는 함의 이동, 양화 재배열, 일반 정리-동치 정규화.
  허용된 정규화는 **닫힌 열거 표**(현재 curry 1쌍)뿐이다.

## 2. 실측 사실 (2차 조사 회신 + 우리 검증)

### F1 — 기수를 MR에 보존하는 source는 전부 우리 방언 밖이다

| source | 기수 인코딩 | 방언 |
|---|---|---|
| QuantML(ISO 24617-12) | `<cardinality numRel="greater_or_equal" num="3"/>`, semantics `\|Y\|≥3` | 밖 (집합 크기+부등호) |
| Overnight(Lambda DCS) | `SW.filter(… >= (number 3 assist))` | 밖 (비교자+수치) |
| ATIS(후대 Lambda) | `( > ( stops $0 ) 3:i )` | 밖 (수치 비교) |
| AMR 3.0 | `:quant 4` | 밖 (수치 role) + 정본이 quantifier scope 비표상 명시 |
| GeoQuery(Prolog) | `at least one`이 **존재 구조로 환원**, `50 capitals`의 50은 LF에서 소실 | 안 — 그러나 수치가 없어 기수 측정이 아님 |
| FraCaS | 형식 표상 없음(gold = 함의 라벨) | 오라클 불가 |

### F2 — 기수를 지우고 쓸 수도 없다 (조사가 정본 근거로 답한 것)

- **QuantML**: `<scoping>`은 `<cardinality>`와 별도 객체지만
  `entity/@involvement`가 cardinality를 참조하므로 숫자 노드만 지우면
  dangling reference가 된다. **`at least three papers` → `∃(papers…)`의
  자동 환원 규칙은 정본에 없다.**
- **Overnight / ATIS**: comparator+number가 filter·비교식 **자체**다.
  숫자만 지우면 식이 불완전하고, 조건 전체를 지우면 base set은 남아도
  기수 NP의 **독립 binder가 남지 않는다**.

### F3 — 예외: ERG/MRS는 기수 EP와 양화 EP가 **분리**돼 있다

`Three dogs bark …`의 MRS(조사 인용):

```text
bare_div_q_rel(… x …)   RSTR …  BODY …     ← 양화 EP
card_rel(… x …)         CARG 3             ← 기수 EP (별개)
_dog_n(… x …)
```

즉 `card_rel(CARG 3)`과 RSTR/BODY 양화 구조가 **동일 노드가 아니다**.
비례도 직접 존재한다: `_most_q(x, hRestrictor, hBody)` — restrictor/body
handle을 갖는 명사구 양화자이며 최상급 `most`와 구별된다.

gold treebank: **LinGO Redwoods** — annotator가 ERG 후보 분석 중 의도한
reading을 선택한 hand-annotated 영어 treebank, 배포 metadata 권리 표기
**GPL**, Ninth Growth 약 85,400 utterances 보고.

### F4 — 비례 재료의 현황

| 후보 | 비례 표상 | 차단 |
|---|---|---|
| QuantML Bank | `<relativeSize pred="most"/>` + 별도 `scoping` — 정의에 정확히 부합 | 데이터 라이선스·item provenance **BLOCKED**, 방언 밖 |
| ERG/MRS | `_most_q(x,h,h)` | Redwoods release 내 **proportional item locator BLOCKED** |
| Overnight/ATIS | 검사 split에서 `most`는 최상급, `majority`는 `count > 2` | 비례 부재는 BLOCKED(전수 아님) |
| AMR 3.0 | 비례 GQ 정본 실물 미확인 | scope 비표상 |
| QuRe·GQG·GQNLI·UDepLambda·QALD | 양화 annotation은 있으나 **문장 단위 full formal MR 근거 미확보** | 오라클 불가 또는 BLOCKED |

**적격 하한(기수 ≥3, 비례 ≥1)을 충족하는 후보는 현재 0건이다.**

### F5 — 우리 쪽 실패 이력 (같은 것을 다시 청하지 않기 위해)

조사가 유력 후보로 제시한 **Wikisem(Simple English Wikipedia →
typed lambda)** 은 선행 판정 D-E2E-v1-21이 이미 부적격 처리한 source다
(단위=기사, `Coverage(v0, article-LF)=0`, `0/121`). 우리 로컬 캐시 재실측:
record 131건이 각각 여러 문장을 담은 단일 거대 LOGIC 식이고,
`InAnaphorSet` 1690회·`Equal` 1297회(방언 밖 담화 구성자), 조사가 인용한
`ratio=`·`count=`·`Most`는 배포본에 **0회**, `most` 54회 중 48회가 최상급
형용사였다. 즉 그 후보는 이 판정의 선택지가 아니다.

## 3. 판정 질문

### Q29.1 — 기수 표현의 방언 지위

D-28은 기수 constructor 추가가 boundary 확대가 아니라 coverage 복구라고
정리했으나 형태는 미정이다. F1~F2가 확정한 것: **기수를 버리는 경로는
닫혔다**(지우면 양화 구조가 무너진다). 따라서 형태를 정해야 한다.

- (a) **`count` constructor 최소 도입**:
  `{"kind":"count","rel":"eq|ge|le","num":<int>,"var":<string>,
  "restriction":<F>,"body":<F>}` — 양화자 자리에 오는 노드로, 기존
  forall/exists와 같은 결박 구조를 갖고 `rel`+`num`만 추가. 투영에서는
  `rel`·`num`을 **채점 대상으로 유지**(기수가 estimand이므로).
  운영 세션 권고. 근거: QuantML의 `numRel`+`num`, Overnight의
  comparator+number, MRS의 `CARG` 모두 이 형태로 사상 가능하고, 방언에
  자유 수치 항(term)을 도입하지 않아 항 문법(var|entity)이 불변이다
- (b) 수치를 **항(term)** 으로 도입(`{"kind":"num","value":3}`)하고 기존
  `pred`로 비교를 표현 — 우려: 항 문법이 바뀌어 모든 adapter·투영·schema
  계약이 영향받고, `pred("ge", num, var)` 류의 임의 술어 규약이 생긴다
- (c) 기수 층만 **별도 IR profile**로 분리(O1 본 코호트는 5종 유지,
  기수는 부속 코호트) — 우려: 같은 estimand를 두 계약으로 쪼개고 N·임계값
  회계가 복잡해진다
- (d) 그 외

부수 질문: (a) 채택 시 **비례**도 같은 형태로 다루는가
(`{"kind":"prop","rel":"most|half|ratio","value":…}`), 아니면 비례는
`count`의 `rel` 확장으로 흡수하는가(예: `rel:"most"`는 수치 없음)?

### Q29.2 — ERG/MRS(Redwoods) source 채택

F3이 유일한 구조적 예외다 — 기수 EP와 양화 EP가 분리돼 있어, **기수 EP를
비계로 다루고 양화 구조만 측정**하는 선행 투영 논리(D-25/D-28)를 그대로
재사용할 수 있다. 동시에 `_most_q`로 비례도 공급한다.

- (a) **조건부 채택**: Redwoods를 제3 source로 자격 심사에 올린다.
  선행 조건: (i) proportional item locator 확보(3차 조사 진행 중),
  (ii) component별 권리 확인(Redwoods는 여러 출처 corpora 포함),
  (iii) MRS→IR adapter 신설 + 자격(기존 SBN/FOL adapter와 같은 9항목),
  (iv) 기수 EP 비계 처리 규칙의 fail-closed 조건. 운영 세션 권고
- (b) QuantML을 우선하고 라이선스 BLOCKED 해소를 조사에 재위임 — 비례
  정의에 가장 정확히 부합하나(`relativeSize`) 데이터 라이선스가 미확인이고
  Bank가 예제 모음이라 규모 신호가 없다
- (c) 기수·비례 층을 **채우지 못한 상태로 재동결**하고 그 두 층을
  UNSCORABLE로 사전 선언 — 운영 세션 반대: D-25가 "실패가 예정된 계약을
  실행하는 것"을 금지한 것과 동형이다
- (d) 그 외

### Q29.3 — MRS 채택 시 기수 EP의 지위 (Q29.1과 결합)

F3의 구조에서 두 갈래가 가능하다:
- (i) **기수 EP를 비계로 제거**하고 양화 구조만 측정 → 기수 constructor
  불필요, 그러나 그 fixture는 `cardinal_quantifier`를 측정하지 않게 된다
  (D-28이 금지한 "boundary 조용한 축소"에 해당하는가?)
- (ii) **기수 EP를 채점 유지** → Q29.1(a)의 constructor가 필요하고,
  subject가 `card` 노드를 산출해야 한다
운영 세션 권고: **(ii)** — full O1 유지 결정과 정합한다. (i)은 층 이름만
남기고 측정을 비우는 것이다. 확인을 청한다.

### Q29.4 — 조사 채널에 선행 판정을 전달하는 절차

F5의 Wikisem 재제안은 **우리 요청서 결함**이었다(선행 배제 판정을 조사에
알리지 않았다 — 같은 오류 2회째). 저장소 규율은 "외부 판정자에게 미리
알려진 것을 다시 청하지 않는다"이고 설계 채널에는 적용해 왔으나 **조사
채널에는 적용하지 않았다**. 조사 요청서에 **배제된 source 목록과 그 근거**를
필수 절로 넣는 것을 절차로 확정할지 청한다(Gate C·D-27 §22와 같은 급의
절차 항목).

## 4. 검증 재현

- F1·F2·F4: `docs/RESEARCH_RESULT_cardinal_proportional_round2.md`
  (회신 verbatim + 우리 검증 기록, sha256 수록)
- F3: 같은 문서 §A-3/§C-1-4의 MRS 실물 인용
- F5: 같은 문서 수신 검증 V1 — 로컬 캐시 `wikisemC6.logic.txt` 재실측표
  (record 131 / InAnaphorSet 1690 / ratio=·count=·Most 0회 / most 54 중 48
  최상급)
- 방언·투영·채점 계약: 실험 폴더의 계약 테스트 195건이 전부 통과 상태

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
