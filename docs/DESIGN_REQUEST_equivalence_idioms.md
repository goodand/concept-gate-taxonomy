# DESIGN REQUEST — 동치 관용구 변주와 측정 경계 (Q27)

- 상신: 2026-08-23, 운영 세션 (V4 control 실행 1/6이 노출)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: 본 코호트는 미실행(dispatch 0건 — 사용자 승인이 "control
  통과 시"로 조건화돼 있었고 미충족). 이 판정 전까지 코호트 차단.

## 1. 배경 (필요한 최소한)

의미 컴파일 실험 V4: subject(무도구 LLM)가 영어 문장을 IR 6종
(forall/exists/and/pred/not/implies; 항=var|entity)로 컴파일. 채점 =
**O1ScopeMatch**: 양측을 `O1_SCOPE_PROJECTION_V1`(사건 의미론 비계·라벨
어휘 제거, scope 구조 유지)로 투영한 signature 사이 exact structural
match. 선행 판정 사슬이 확정한 것:

- 라벨 정체성·WSD·사건 granularity는 **채점 밖**(진단 전용) — D-24/D-25
- 양화 종류·순서·부정 위치·함의 위치는 **estimand** — 재작성 금지.
  특히 `theorem_equivalence` 정규화가 명시 금지 목록에 있다(D-26 §6)
- freeze 전 **Measurement Satisfiability Gate**: "subject 언어 안에 PASS
  가능한 출력이 최소 1개 존재"를 결정론 witness로 검사(D-25 §20-26)
- control(N 밖): 통과가 본 코호트 해석 가능 조건

## 2. 실측 사실 — V4 control 6건 (FOLIO 3 + PMB 3) 실행 결과 1/6

라벨·granularity 잡음은 V4에서 실제로 소멸했다(별도 smoke에서 확인).
실패 5건은 전부 **그 다음 층**이며 3계급으로 분해된다 (projected 골격
verbatim 대조 완료):

### 계급 1 — 논리 동치 관용구 변주 (양화 능력과 무관한 표기 선택)

| 재료 | gold 골격 | subject 골격 | 관계 |
|---|---|---|---|
| "A horse is a racehorse if it is in a race." | `∀x((horse∧racing)→racehorse)` | `∀x(horse→(in_race→racehorse))` | **curry** — 논리 동치, 양화 경계 무관 |
| "Nobody encouraged him." | `¬∃x(person∧…)` | `∀x(person→¬…)` | **¬∃ ↔ ∀¬** — 논리 동치, 양화 종류가 바뀜 |

D-26 §6이 동치 정규화를 금지했으므로 현 계약은 "subject가 gold의 관용구
선택을 적중했는가"까지 측정한다. 중요: 이 재료들은 satisfiability를
**통과했다** — gold 관용구를 쓴 출력이 언어에 존재하므로. 즉
**measurement satisfiable ≠ naturally reachable** 간극이 실측됐다.

### 계급 2 — PMB 대명사/개체 관용구

gold는 "him"/"he"를 참여자 ∃(male.n.* synset)로 인코딩하고, subject는
entity 항을 쓴다. projection의 PMB 정책은 명사 synset 용법 변수를
PARTICIPANT로 유지하므로 ∃ 개수가 갈린다. 실물: "He is anything but a
fool" gold `∃x(male∧¬∃y(fool…))` vs subject `¬fool(he-entity)`.
**in-N PMB 15건에 만연 위험** — 사전 노출표에 male/person 술어 다수.

### 계급 3 — control 선별 규칙의 역할 인코딩 부재 (운영 세션 설계 결함)

PMB control 풀에 단순성 제약이 없어 "few bookstores"(O1 constructor 부재
재료), "anything but"(관용구) 류가 control로 뽑혔다. control의 역할
(정답이 파이프라인을 통과할 수 있음의 확인)에 맞는 재료 제약이 필요하다.

참고: FOLIO-175p1("monitors… cheaper than original prices")의 실패는
별개 — gold의 추상화(1항 Lab/Cheaper, ∀ 1개) vs subject의 충실 독해
(비교 대상 y를 양화, ∀ 2개). 이는 D-24 Q24.4가 이미 "known
source-specific challenge"로 판정한 부류의 발현으로 보이나, **control
재료로서의 적합성**은 계급 3의 문제다.

## 3. 판정 질문

### Q27.1 — 동치 관용구 변주의 지위

- (a) **동결 목록 기반 국소 동치 정규화 허용**: 비교층(투영 전 또는 후)에
  적용할 재작성을 **열거된 쌍으로만** 허용하고, 각 쌍은 유한 모델 전수
  검증(동치 증명)과 함께 동결. 후보 2쌍: (i) curry —
  `(A∧B)→C ↔ A→(B→C)` (양화 경계 무관·국소), (ii) 부정-양화 결합 —
  `¬∃x(R∧B) ↔ ∀x(R→¬B)` (양화 종류가 바뀌나 ¬와 결합된 국소 쌍이며
  D-24의 104-반례 부류(비동치 topology)와 무관함을 전수 증명 가능).
  prenex화·양화 재배열·일반 정리 동치는 계속 금지. 운영 세션 권고 —
  근거: 이 두 변주는 "어느 동치형을 쓰는가"라는 표기 취향이지 scope
  이해가 아니며, D-25 §16의 3분류에서 notation noise 쪽이다
- (b) 현행 유지(gold 관용구 적중이 estimand) — 우려: quantifier_negation
  stratum이 부분적으로 관용구 복권 측정이 된다
- (c) 그 외 (예: (a)를 (i) curry만으로 한정 — ¬∃/∀¬는 estimand 유지)

### Q27.2 — PMB 대명사/개체 참여자 ∃의 처리

- (a) **projection PMB 정책에 동결 절첩 규칙 추가**: 용법이 대명사류
  synset 한정 목록(`male.n.*`, `female.n.*`, `person.n.*` — 목록 동결)에
  국한되고 문장 쪽 상응이 대명사/고유명인 참여자 ∃를 entity-등가로
  절첩. 우려: "문장 쪽 상응" 판정의 기계화가 관건 — 문장 무참조 구조
  규칙(용법 synset 목록만)으로 근사하면 실명 명사("a man")까지 절첩될
  수 있음. 경계 확정을 청함
- (b) 해당 fixture를 적격성에서 배제 — "naturally reachable" 판정은 기계
  술어로 만들 수 없어(모델 자연 독해의 예측이므로) gate화 불가. 대신
  **대명사 보유 문장 제외** 같은 표면 술어로 근사 가능(기계적) — 풀 파급
  재실측 필요
- (c) estimand로 수용(subject가 PMB 인코딩 관행을 알아야 통과)
  — 운영 세션 반대: D-25가 사건 의미론 재현을 estimand 밖으로 판정한
  것과 동형의 hidden-idiom guessing이다

### Q27.3 — control 선별 규칙의 정본화

control 재료의 동결 기계 술어를 청함 — 운영 세션 초안: 양화 한정사
정확히 1개(overt: all/every/some/no) ∧ 대명사·고유명 부재 ∧ 관용구
부정("anything but" 류) 부재 ∧ 문장 길이 상한. FOLIO·PMB 공통 적용,
현행 control 6건은 이 술어로 재선별.

### Q27.4 — gate 지위의 명문화

Measurement Satisfiability는 **필요조건**이지 자연 도달성의 충분조건이
아님을 사전등록에 명시(이번 실측이 그 간극의 첫 증거). "control이
그 간극의 실측기"라는 역할 규정 포함.

## 4. 검증 재현

- control 결과: `experiments/2026-08-23_e2e_v1_c_o1_cohort/`
  `stage2_controls_results_v4.json` + `CONTROLS_RUN_V4_20260823.md`
  (projected 골격 대조표 포함)
- 계급 1 동치성: 두 쌍 모두 유한 모델 전수로 즉시 검증 가능(우리가
  D-23/24 검증에 쓴 기법 그대로)
- dispatch 이력: 6건 중 1건은 하네스 차단 2회 후 사용자 명시 재승인으로
  수행 — mechanical retry 회계, semantic retry 0
