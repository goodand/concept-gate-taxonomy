# Stage 2 V4 — control 실행 기록 + 코호트 정지 판단 (2026-08-23)

- 문서 종류: **운영 로그** (결과 artifact와 같은 커밋)
- 조건부 승인: "control 통과 시 smoke 통과 후 본 코호트 20건 승인" —
  **control 1/6로 미충족 → 본 코호트 dispatch 0건 유지.**
- dispatch: 6건(FOLIO 3 + PMB projection 3), V4 template·6종 schema.
  CTRL4-06은 하네스 안전 분류기 차단 2회 후 사용자 명시 재승인
  ("CTRL4-06 재실행 승인")으로 수행 — D-19 mechanical retry 회계
  (생성 전 인프라 실패, semantic retry 아님).

## 1. 결과 (stage2_controls_results_v4.json)

| trial | case | 결과 | projected 골격 대조 (oracle vs subject) |
|---|---|---|---|
| CTRL4-05 | FOLIO-1377p0 "All humans eat." | **pass** | 동일 F(T;(p→p)) |
| CTRL4-03 | FOLIO-500p4 racehorse | fail | `(p∧p→p)` vs `(p→(p→p))` — **curry 변주** (논리 동치, 양화 경계 무관) |
| CTRL4-04 | FOLIO-175p1 monitors | fail | ∀ 1개(gold 추상화 Lab/Cheaper) vs ∀ 2개(subject 충실 독해 — 비교 대상 y 양화) |
| CTRL4-06 | PMB-p11-d2268 "Nobody encouraged him." | fail | oracle `¬∃(∃ …)` vs subject `∀(p→¬…)` — **¬∃/∀¬ 동치 변주** + 대명사 ∃ 관용구 |
| CTRL4-02 | PMB-p12-d2559 "anything but a fool" | fail | oracle ∃(male)…¬∃(fool) vs subject `¬fool(he-entity)` — **대명사 참여자 ∃ vs entity 항** |
| CTRL4-01 | PMB-p24-d2685 "few bookstores" | fail | "few"는 O1 constructor 부재 재료 — **control 부적합 선별** |

O1ScopeMatch 1/6. ERROR 0, 봉투 위반 0 — 파이프라인·기제는 전부 정상 작동.

## 2. 원인 3계급 (라벨·granularity 잡음은 소멸 — 전부 그 다음 층)

1. **동치 관용구 변주**: curry↔conjunctive antecedent(500p4), ¬∃↔∀¬
   (p11). 논리적으로 동치이나 구조 상이 — D-26 §6이
   `theorem_equivalence` 정규화를 금지했으므로 현 계약은 "gold의 관용구
   선택 적중"까지 측정한다. satisfiability는 통과한다(그 관용구를 쓴
   출력이 존재하므로) — **measurement satisfiable ≠ naturally reachable**
   간극이 실측됐다.
2. **PMB 대명사/개체 관용구**: gold는 "him"/"he"를 참여자 ∃(male.n)로
   인코딩, subject는 entity 항 사용 — PARTICIPANT ∃라 projection이
   유지하고 구조가 갈린다. **in-N PMB 15건에도 만연 위험** (사전 실측:
   15건 술어 노출표에 male/person 다수).
3. **control 선별 규칙의 역할 인코딩 부재** (freeze_v4의 운영 세션 설계
   결함): control의 역할은 "정답이 파이프라인을 통과할 수 있음"의 확인
   이므로 단순·관용구-무의존 재료여야 하는데, PMB control 풀에 단순성
   제약을 두지 않아 "few"·"anything but" 류가 뽑혔다.

## 3. 처분

- 본 코호트 미실행 (승인 조건 미충족; dispatch 0건 유지)
- 상신 Q27 준비: `docs/DESIGN_REQUEST_equivalence_idioms.md` — 동치 변주의
  지위(notation noise vs estimand), 대명사 ∃ 관용구, satisfiable↔naturally-
  reachable 간극, control 선별 규칙
