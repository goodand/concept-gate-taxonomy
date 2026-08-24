# DESIGN REQUEST — subject 방언 표현력과 FOLIO 다중 양화 topology (Q26)

- 상신: 2026-08-23, 운영 세션 (D-E2E-v1-25 구현 중, Measurement
  Satisfiability Gate 첫 전수 실행이 적발)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: V3 재동결이 차단된다(multi_quantifier 적격 풀 2 < 5). 코호트
  dispatch는 여전히 0건 — 결과에 조건화된 것 없음.

## 1. 배경 (필요한 최소한)

의미 컴파일 실험: subject(무도구 LLM)가 영어 문장을 IR로 컴파일하고,
oracle(외부 gold를 결정적 adapter로 IR화)과 비교해 채점한다.

- **subject 방언(동결)**: constructor 5종 — `forall(var, restriction,
  body)`, `exists(var, restriction, body)`, `and`, `pred`, `not`.
  **함의 constructor가 없다** — 함의는 `forall`의 제한식 형태로만 표현
  가능하다(∀x(R→B) ≡ forall(x, R, B)). 이는 초기 설계(D-19 프로브)부터의
  방언이고, constructor profile 확장은 명시적 외부 판정 사안이다(D-21 §16).
- **D-E2E-v1-24 Q24.4 / D-25 §7**: FOLIO gold의 양화/함의 topology는
  estimand의 일부 — 비교층에서 자연 독해 형태로 재작성 금지(유한 모델
  전수: `∀x∃y((A∧B)→C)` vs `∀x(A→∃y(B∧C))` 반례 104/256).
- **D-E2E-v1-25**: 측정 계약을 O1_SCOPE_PROJECTION_V1(scope-bearing 구조만
  비교, 라벨 어휘·사건 의미론 비계는 채점 밖)로 개정, freeze 전
  **Measurement Satisfiability Gate** 필수화 — "허용된 subject 언어 안에
  이 fixture를 PASS시키는 출력이 최소 1개 존재하는가"를 결정론 witness로
  검사, 실패는 INELIGIBLE.
- fixture 요건(D-22): N=20 중 FOLIO 다중 양화 **5건**(floor 4/5), PMB 15건.

## 2. 실측 사실 (게이트 전수 실행 — 코호트 dispatch 0건 상태)

D-25가 명한 projection·satisfiability gate를 구현(자격 P1~P6 통과, 조준
뮤테이션 3/3 적중)하고 전 풀에 실행한 결과:

| 대상 | SATISFIABLE |
|---|---|
| PMB 15건 (V2 선별분) | **15/15** — projection이 F3(사건 의미론 granularity)를 실제 해소. proportional·cardinal 포함 |
| FOLIO 단순 양화 control | 3/3 (+후보 표본 80 중 78) |
| **FOLIO multi_quantifier 후보 17건 전수** | **2/17** (695p1·598p4만) — 필요치 5 |

**원인 — 방언 표현력 공백**: FOLIO 다중 양화 gold의 지배 관용구는
`∀x ∃y ((A(x)∧B(y)) → C(x,y))` — **함의가 ∃의 scope 안**에 있다. subject
방언은 함의를 forall 제한식으로만 표현할 수 있으므로, **이 topology를
표현하는 subject 출력이 언어에 존재하지 않는다**. topology 재작성은
D-24/D-25가 금지했으므로 비교층이 이어줄 수도 없다. 즉 라벨(D-24)도
granularity(D-25)도 아닌 세 번째 층위: **estimand가 요구하는 구조를
subject 언어가 표현 불가**.

붕괴 사슬(전부 이 게이트가 freeze 전에 적발): witness 렌더 불가 →
MEASUREMENT_UNSATISFIABLE → multi 풀 17→2 → D-22 floor(5건, 4/5) 불충족
→ V3 동결 불가(BLOCKED).

**권고안 (a)의 가정 실측** — 방언에 `implies`를 추가(6종)하면:

| 대상 | 결과 |
|---|---|
| multi 17건 | **17/17 SATISFIABLE** |
| + D-24 라벨 도달성 병용 | 5건(695p1·376p4·598p4·404p0·142p1) = 정확히 필요치, 선별 자유도 0 |
| PMB 15건 | 15/15 유지 (무영향) |

부수 기록: 후보 풀에 `example_id`가 없는 record 1건 존재
(`FOLIO-Nonep1`) — 식별자 없는 commitment는 불성립이므로 선별에서 기계
제외 예정(적격성 조건에 명문화).

## 3. 판정 질문

### Q26.1 — 표현력 공백의 해소 방식

- (a) **subject 방언에 `implies` constructor 추가** (O1_V1 → 6종:
  `{"kind":"implies","left":F,"right":F}`) — 운영 세션 권고. 근거:
  (i) 실측대로 multi 풀 완전 회복, PMB 무영향; (ii) schema 생성기는
  implies 분지를 이미 지원(코드 기존 능력 — 새 발명 아님); (iii) V3
  재동결에서 template·schema·profile hash가 어차피 갱신된다; (iv)
  estimand(scope 구조) 불변 — 표현 수단이 gold의 topology를 따라잡는
  것뿐이고, D-24가 estimand로 선언한 그 topology를 비로소 측정 가능하게
  만든다
- (b) multi 층을 제한식-표현형 topology로 한정 — 풀 2 < 5이므로 floor/N
  개정(D-22 §16 판정 사안)이 연쇄로 필요. 운영 세션 비권고: 측정하려던
  대표 구분(∀∃ 상호작용)의 지배 관용구를 표본에서 배제하게 된다
- (c) 다중 양화 + 제한식형 topology를 공급하는 제3 source 조사 —
  왕복 비용 크고, (a)가 이미 실측으로 충분함이 확인된 상태
- (d) 그 외

### Q26.2 — (a) 채택 시 구속 조건 확인 4건

1. **template 개정 문안**: 허용 kind 목록에
   `- {"kind": "implies", "left": <formula>, "right": <formula>}` 1행 추가
   외 지시 불변 — 이 최소 문안으로 충분한가.
2. **subject의 implies 자유 사용**: subject가 함의를 임의 위치(제한식
   형태 대신 `forall(x, True, implies(R,B))` 등)에 쓸 수 있게 된다.
   비교층 desugar가 `forall(x,R,B)→forall(x,True,implies(R,B))`로 양측을
   같은 형태에 수렴시키므로 표기 자유는 중립이라고 보는데(D-23 §12의
   기존 desugar 그대로), 이 해석의 승인.
3. **자격 추가**: projection 자격에 P7(implies 왕복: ∃ 아래 함의가
   projection·witness 왕복에서 보존) + P8(implies 위치 구분: 제한식 형태와
   ∃-scope 형태가 desugar 후 정확히 구분 유지 — 104 반례 쌍으로) 추가
   예정 — 충분한가.
4. **경계 재확인**: `implies` 추가가 D-21 §16이 금지한 "실험 중 방언
   임의 확장"이 아니라 이 상신에 의한 판정 승인 경로임의 확인.

### Q26.3 — D-24 라벨 도달성 적격 불변식의 지위

D-25가 라벨 정체성을 채점에서 제거(진단 전용)했으므로, D-24 Q24.2의
적격 조건 `predicate_label_reachability`(라벨이 문장에서 파생 가능해야
적격)의 원 근거(라벨 채점 통과 가능성)는 소멸했다. 실측: (a) 가정에서
도달성을 **유지하면 multi 풀 5**(자유도 0 — 선별 조작 불가능성 최강),
**강등하면 17**(seed 순서 선별).

- (i) **유지** — 운영 세션 권고: 보수적이고, D-24 명문과 충돌하지 않으며,
  자유도 0은 outcome-conditioned selection 우려를 원천 제거. 부수 효과로
  진단 신호(라벨 일치율)의 해석도 깨끗해진다
- (ii) 진단 전용으로 강등(적격성에서 제외) — D-25 §15 취지의 연장이나
  D-24 명문 개정이 필요
- 판정을 청함.

## 4. 검증 재현

- 게이트·projection 구현: `experiments/2026-08-23_e2e_v1_c_o1_cohort/`
  `_stage2_scope_projection.py`(자격 계약 `test_stage2_scope_projection.py`
  P1~P6), `_stage2_satisfiability.py`(계약 `test_stage2_satisfiability.py`)
- §2 표 재현: V2 manifest 23건을 게이트에 관통 + FOLIO 후보 풀 17건 전수
  (스크립트 1분 내 재실행 가능, 결정론)
- (a) 가정 실측: 동일 게이트 논리에 schema만 6종으로 바꾼 시뮬레이션 —
  동결 표면 무변경

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
