# Stage 2 V5 — control 실행 기록 (2026-08-24)

- 문서 종류: **운영 로그** (결과 artifact와 같은 커밋)
- 승인: 사용자 "adapter control 3건 + 본 코호트 20건 dispatch — 별도 실행
  승인". 이 승인은 절차상 조건부다 — HANDOFF §3: **FOLIO adapter control
  3/3이 본 코호트 해석 가능 조건**. V4 실행(1/6 → 정지)과 같은 규율.
- dispatch: 6건(FOLIO adapter 3 + PMB projection 3), workflow
  `wf_999021b7-318`, `o1-compiler`/haiku, schema 강제, 프롬프트는
  `stage2_controls_plan_v5.json` verbatim(V4 plan과 6/6 바이트 동일 —
  바뀐 것은 채점 계약뿐). mechanical retry 0회.

## 1. 결과 (stage2_controls_results_v5.json) — **2/6, 코호트 정지 유지**

| trial | case | V4 | **V5** | 층 |
|---|---|---|---|---|
| CTRL5-05 | FOLIO-1377p0 "All humans eat." | pass | **pass** | adapter |
| CTRL5-03 | FOLIO-500p4 racehorse | fail(curry 변주) | **pass** — D-27 curry 정규화 + V2가 해소 | adapter |
| CTRL5-04 | FOLIO-175p1 monitors | fail | **fail** | adapter |
| CTRL5-06 | PMB-p11-d2268 "Nobody encouraged him." | fail | **fail** | projection |
| CTRL5-02 | PMB-p12-d2559 "anything but a fool" | fail | **fail** | projection |
| CTRL5-01 | PMB-p24-d2685 "few bookstores" | fail | **fail** | projection |

FOLIO adapter control **2/3** → 3/3 미충족 → **본 코호트 dispatch 0건 유지**
(누계 dispatch: control 6건뿐, in-N 0건). ERROR 0, 봉투 위반 0.

## 2. 실패 4건의 서명 대조 진단 (V2 signature 실측)

**전부 V4에서 이미 알려진 부류다 — V5(투영)가 새로 만든 실패는 0건이고,
V4 실패 하나(curry)를 V5가 해소했다.**

- **FOLIO-175p1**: oracle `∀(T; RSTR/BODY→atom{(1,)})` — gold FOL이 비교
  구문을 단항 술어들로 추상화해 V2 atom 하나로 접힘. subject는 충실 독해로
  가격 ∃ 2개를 도입 → scope 구조 자체가 다름. **V4 CTRL4-04와 동일 부류**
  (gold 추상화 vs 충실 독해 — scope가 정당하게 다르다).
- **PMB-p11-d2268**: oracle은 "him"을 참여자 ∃(male.n.01)로 인코딩해
  `¬∃∃`, subject는 entity 항이라 `¬∃` — **대명사 참여자 ∃ 관용구**(V4
  CTRL4-06·02와 동일 부류; D-27이 양화 대명사를 측정 어휘로 유지).
  subject의 ¬∃ 선택 자체는 이번에 oracle과 일치했다(V4의 ∀¬ 변주는 소멸).
- **PMB-p12-d2559 / p24-d2685**: "anything but"·"few" — **control 부적합
  선별**(D-27 §12가 적발한 V4 선별 계약 결함; few는 O1 constructor 부재).

## 3. 처분

1. **본 코호트 미실행.** 승인은 받았으나 해석 가능 조건(FOLIO 3/3) 미충족 —
   dispatch하면 결과가 해석 불가능하므로 실행하지 않는 것이 승인의 취지에
   맞다(V4 선례와 동일 판단).
2. 다음 경로는 **이미 판정돼 있다** — D-27 §18이 control 재선별을 승인했고
   (`old controls → historical / new eligibility profile → deterministic
   reselection → new controls → qualification rerun`, amendment 절차 재사용),
   그 적격 술어는 `_stage2_surface_filters.py`의
   `O1_CONTROL_ELIGIBILITY_V1`(2층: 표면 + projection 복잡도, 길이 상한 15)
   로 **이미 구현·계약 결박돼 있다**. 실행되지 않았을 뿐이다.
3. 남는 판단 항목: FOLIO-175p1류(gold 추상화 vs 충실 독해)와 PMB 대명사
   참여자 ∃는 재선별 술어가 **단순 재료를 뽑으면 control에서는 자연히
   배제**되지만, in-N 20건(특히 PMB 15건의 male/person 만연 — V4 기록)에는
   그대로 남는 **측정 대상 성질**이다. control 문제와 estimand 문제를
   섞지 않는다 — in-N에서 그것이 낮은 점수로 나타나면 그것이 측정 결과다.

## 4. V4→V5 비교의 의미 한계

V1↔V2 점수 직접 비교는 manifest가 금지한다
(`score_comparability.V1_to_V2.direct_numeric_comparison: false`). 위 표의
V4 열은 **실패 부류의 존속 여부** 추적이지 수치 비교가 아니다.

---

**후속**: 이 실행의 2/6이 control 선별 계약의 결함을 드러냈고, D-27 §18의
재선별을 실행해 [[CONTROLS_RUN_V5_1_20260824|V5.1에서 5/5]]를 얻었다. 그러나
그 통과가 코호트를 열지는 못했다 — 적격 술어가 배제한 성질이 in-N의 지배적
성질이기 때문이다([[DESIGN_DECISION_referential_participant_quantification|D-33]]).
