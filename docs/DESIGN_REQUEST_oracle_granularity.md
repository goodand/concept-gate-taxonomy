# DESIGN REQUEST — oracle 표상 granularity와 측정 계약의 정합 (Q25)

- 상신: 2026-08-23, 운영 세션 (V2 재동결 후, adapter control 실행에서 적발)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: control 2/3(해석 가능 조건 3/3 미달)로 본 코호트는 **미실행**
  (dispatch 0건 — 결과에 조건화된 것 없음). 이 판정 전까지 코호트 차단.

## 1. 배경 (필요한 최소한)

의미 컴파일 실험: subject(무도구 LLM)가 영어 문장 1개를 IR(forall/exists/
and/pred/not; term=var|entity)로 컴파일하고, oracle(외부 gold 논리식을
결정적 adapter로 IR화)과 정규화 후 **구조 동일성**(DirectMatch)으로 채점.
template은 subject에게 "Use lowercase predicate names taken from the
sentence's content words"를 지시한다. fixture 20 = PMB 15(SBN gold) +
FOLIO 5(FOL gold, 다중 양화 전담) + FOLIO control 3(N 밖, **3/3 통과가
코호트 해석 가능 조건**).

선행 판정 사슬: Q22.3 — PMB synset 술어(`happy.a.01`)의 WSD를 estimand
밖으로(lemma 정규화, PMB 한정). **D-E2E-v1-24** — (i) FOLIO 라벨 대소문자
잡음을 source-bound codec(`FOLIO_LABEL_LOWERCASE_V1`, 소문자화만·분절
금지)으로 중립화, (ii) 문장에서 파생 불가한 oracle 어휘는 fixture 부적격
(`predicate_label_reachability` — 동결 기계 규칙: 연속 1~4토큰 무구분
이어붙임 + 기계적 복수형 절단), (iii) 원 동결 V1은 불변 보존·V2 재동결,
(iv) FOLIO gold의 양화/함의 topology는 estimand — 비교층 재작성 금지.
D-24 §16이 준 3분류: 표기 잡음→정규화 / 숨은 어휘→부적격 / 의미 topology→
측정. 이후 재동결·재검증(smoke 3단, V1↔V2 diff 게이트) 전부 통과 후
control을 실행했다.

## 2. 실측 사실 3건 (전부 코호트 밖 — control 3건과 동결 fixture 정적 분석)

### F1 — control 2/3: 라벨 span 미결정성

CTRL-02 "All monitors equipped in the lab are cheaper than their original
prices." / oracle `∀x (Lab(x) → Cheaper(x))`. subject 출력은 **구조 완전
동형**(∀·제한 1술어·본문 1술어·결박 정확)이나 라벨만 다름:
`equipped_in_lab` vs `lab`, `cheaper_than_original` vs `cheaper`.
도달성 불변식은 "oracle 라벨이 문장에서 파생 가능"을 보증하지만 "subject가
같은 span을 선택"은 보증하지 않는다 — **derivable ≠ uniquely determined**.
(나머지 2건은 pass: video/visual, human/eat — 단일 토큰 라벨.)

### F2 — in-N FOLIO 5건 중 4건: 다중 토큰 join 규약 부재

oracle 라벨 `cancatch`, `universallanguage`, `spectatorsbeton`,
`greyhoundracing`, `majorsettlementof` 등은 연속 토큰의 **무구분
이어붙임**이다. subject는 CTRL-02에서 밑줄 join(`equipped_in_lab`)을
발명했고 template은 다중어 개념의 join 규약을 지시하지 않는다. codec은
분절을 금지하므로 `can_catch` ≠ `cancatch`.

### F3 — PMB 15/15: oracle이 사건 의미론 granularity로 인코딩

PMB 전수 실측: oracle IR이 neo-Davidsonian 구조다 — role 술어(`Agent`,
`Experiencer`, `Stimulus`, `Theme`, `Time`, `EQU`, `TPR`, `Quantity`…),
문장에 없는 암묵 개념(`time`, `person`), 사건·시간 변수용 추가 ∃.

실물: "Not all children like apples." →
oracle = `¬∀x0 child(x0) → ∃x1∃x2∃x3 [like.v.03(x1) ∧ Experiencer(x1,x0)
∧ Stimulus(x1,x2) ∧ apple(x2) ∧ time(x3) ∧ …]`
template 준수 subject의 자연 출력 = `¬∀x child(x) → ∃y apple(y) ∧
like(x,y)` — 양화사 수(2 vs 4), arity(like/2 vs like.v.03/1+roles),
어휘(role 술어는 content word가 아니라 **지시상 산출 금지**) 전부 불일치.
**subject가 지시를 완벽히 따를수록 확실히 fail한다.** ¬∀/∀¬ scope
골격(estimand)은 oracle 안에 실재하나 사건 구조 아래 묻혀 있다.

이 결함은 V1부터 있었고(V2는 PMB를 불변 보존) 이제야 보인 이유: 모든
사전 검증은 commitment 무결성(해시 왕복)을 검증했지 **subject-통과
가능성**은 어떤 게이트도 검증하지 않았다. 리허설·smoke의 live 재료가
전부 발명 FOL형이어서 PMB oracle에 대한 대조가 한 번도 없었다.

## 3. 판정 질문

### Q25.1 — F3의 처리: 측정 계약과 PMB oracle의 정합 경로

- (a) **비교층에 scope-골격 투영(projection) profile 추가**: PMB oracle을
  양화-scope 골격(개념 술어 + 양화 구조)으로 투영 — role 술어·사건/시간
  ∃ 제거. 우려: 사건·시간 ∃ 제거는 **양화사 수를 바꾸므로** D-24가 금지한
  "topology 재작성"과의 경계 판정이 필요하다(scope-무관 ∃만 제거한다는
  기계 판별 기준 포함). subject 방언·template은 불변
- (b) **subject 방언을 사건 의미론으로 확장**(template이 role 술어·사건
  변수 지시) — 운영 세션 비권고: estimand가 "scope 컴파일"에서 "SBN 재현"
  으로 팽창, D-24의 hidden-vocabulary 원칙과 충돌(role 어휘는 문장에 없음)
- (c) **PMB를 O1-v1 source에서 부적격 처리** — 적격성에 "oracle 표상이
  subject 방언과 granularity 정합"을 추가하면 PMB gold 전체가 탈락할
  가능성. governance 파급: D-21의 "유일 수용 source 금지"로 제2 source
  체제가 무너짐(FOLIO 단독)
- (d) 그 외

### Q25.2 — F1·F2의 처리: 라벨 span·join 미결정성

- (a) **template에 명명 규약 명시**(동결 template 개정 = amendment 사안):
  "다중어 개념은 공백 없이 이어붙인다(separator 금지)" + "제한식 술어는
  head noun 하나로" 류의 결정 규칙 — subject가 규약을 알면 도달 가능.
  잔여 위험: span 선택(`lab` vs `equipped_in_lab`)은 규약으로도 완전
  결정되지 않을 수 있음 — 어느 수준까지 지시가 허용되는가(oracle 유출
  경계)의 판정 포함
- (b) 적격성 강화: 단일 토큰 라벨 fixture만 적격 — 실측 파급: multi 풀
  17→**1**(376p4만) → BLOCKED, 제2 source 재조사 필요
- (c) 비교층 라벨 완화(예: oracle 라벨이 subject 라벨의 부분열이면 인정)
  — 운영 세션 비권고: D-24 §2의 명시 금지(semantic aliasing) 방향
- (d) 그 외

### Q25.3 — control 게이트의 회계와 재실행 규칙

이번 control 2/3은 (i) 유효한 게이트 작동(해석 불가 판정)인가 (ii) 측정
계약 결함의 증상이므로 계약 수리 후 **control 재실행이 semantic retry
금지에 저촉되지 않는가**. 운영 세션 의견: (ii) — retry 금지는 "같은 측정
계약에서 결과가 마음에 안 들어 다시 던지기"를 막는 것이고, 계약 자체가
판정으로 바뀌면 새 측정이다. 단 이 해석의 승인 필요.

### Q25.4 — 신규 게이트: subject-통과가능성 사전 검증

향후 동결 전에 "oracle 술어 ⊆ template 허용 어휘(+규약) ∧ 양화 구조가
subject 방언으로 표현 가능"을 기계 검증하는 게이트를 적격성에 추가할지.
F3이 23/23 검증을 통과한 근본 원인이 이 게이트의 부재다.

## 4. 검증 재현

- control 실행 기록: `experiments/2026-08-23_e2e_v1_c_o1_cohort/CONTROLS_RUN_20260823.md`
  (+ `stage2_controls_{manifest,plan,results}.json`)
- F3 1줄 재현: manifest_v2의 아무 PMB entry나 캐시 LF를
  `cg_sbn_adapter.adapt_sbn`으로 IR화해 술어 목록을 문장과 대조
- F1: control results의 CTRL-02 행 + 본문 §2 대조표
