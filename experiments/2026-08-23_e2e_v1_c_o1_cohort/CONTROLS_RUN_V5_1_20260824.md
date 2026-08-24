# Stage 2 V5.1 — 재선별 control 실행 기록 (2026-08-24)

- 문서 종류: **운영 로그** (결과 artifact와 짝)
- 선행: [[CONTROLS_RUN_V5_20260824|V5 실행(2/6 → 정지)]] · 재선별 근거는
  D-27 §18(이미 승인된 경로) · 판정 후속은
  [[DESIGN_DECISION_referential_participant_quantification|D-33]]
- 이 로그가 늦게 만들어진 이유: zero-context 복원 시험(2026-08-24)이
  **"V5.1 5/5의 실행 기록이 없다"**를 적발했다. 결과 JSON만 커밋하고 운영
  로그를 빠뜨렸다 — 방법론은 둘을 짝으로 요구한다. 그 적발 자체가
  handoff 시험의 산출이므로 숨기지 않고 여기 적는다.

## 1. 무엇이 달라졌나 — 재료만 바뀌었다

| 축 | V5 | **V5.1** |
|---|---|---|
| 프롬프트 template 해시 | `dfc0aacb…` | **동일** |
| subject 정의 해시 | `891dd0d6…` | **동일** |
| 채점 계약 | `O1_SCOPE_PROJECTION_V2` 파이프라인 | **동일** |
| control 재료 | V4 계승(6건) | **재선별 5건**(D-27 §18) |

즉 이 실행은 **재료 교체의 효과만** 본다. 도구를 바꿔서 점수가 오른 것이
아니라는 것이 이 표의 요점이다.

## 2. 선별 (결정론 — seed·order_key·적격 술어가 전부 코드)

적격 술어 `O1_CONTROL_ELIGIBILITY_V1` 2층(표면 단순성 + oracle projection
복잡도, 길이 상한 15). 풀: FOLIO forall **233** · exists **35** · PMB forall
**1** · exists **10** — `selection_inputs.control_eligibility_pools`에 기록.
**PMB 보편은 656 후보 중 1건뿐이라 선택의 자유도가 0**이다(자유도를 숨기지
않는다).

| 층 | case | 문장 |
|---|---|---|
| folio_universal | FOLIO-1420p2 · FOLIO-1377p0 | All videos are visual. · All humans eat. |
| folio_existential | FOLIO-901p2 | Some mechanical watches are automatic. |
| pmb_universal | PMB-p70-d1927 | Every vote counts. |
| pmb_existential | PMB-p98-d2753 | No one's watching. |

## 3. 결과 — **5/5**, 사슬 최초

dispatch: workflow `wf_5b9508fc-22d`, `o1-compiler`/haiku, schema 강제,
프롬프트는 `stage2_controls_plan_v5_1.json` verbatim. **mechanical retry 0 ·
ERROR 0 · 봉투 위반 0.**

| trial | case | 결과 |
|---|---|---|
| CTRL51-01 | FOLIO-1420p2 | pass |
| CTRL51-02 | PMB-p98-d2753 | pass |
| CTRL51-03 | FOLIO-901p2 | pass |
| CTRL51-04 | PMB-p70-d1927 | pass |
| CTRL51-05 | FOLIO-1377p0 | pass |

O1ScopeMatch 1.0 · UCR 1.0 · `accepted: true`. 사슬 추이: V4 1/6 → V5 2/6 →
**V5.1 5/5**.

건전성 신호: 단순 보편 3건(FOLIO 2 + PMB 1)의 V2 서명이 **source를 가로질러
동일**하다(`24f6aef2…`) — 라벨 소거와 granularity 다리가 의도대로 작동한다.

## 4. 5/5는 위양성 의심을 먼저 배제해야 하는 결과다

투영이 전부 붕괴시켜도 5/5가 나온다. 그래서 변조를 넣었다.

| 변조 | 결과 |
|---|---|
| 양화 교환(∀↔∃) | **5/5 fail** — 적발 |
| 부정 추가 | **5/5 fail** — 적발 |
| 제한식 제거 | 존재 양화 2건 **pass** |

마지막 항을 처음엔 결함으로 의심했으나 **내 변조가 오조준**이었다:
`∃x[R]B ≡ ∃x(R∧B)`로 desugar된 뒤 R과 B의 변수 incidence가 같으면 D-32가
**버리라고 명한 차원**(술어 라벨·개수)만 다르다. 내용 변조이고 측정 대상은
scope다. 계약이 버리는 차원을 겨눈 변조는 게이트의 결함이 아니다(P16 재발).

in-N 쪽에서 축퇴 의심이 있던 7건에도 scope 변조를 가해 **양화 교환 7/7 ·
부정 이동 4/4 적발**을 확인했다.

## 5. 이 5/5가 보증하지 않는 것 — 이것이 코호트를 막았다

적격 술어 `has_excluded_participant`가 대명사·고유명 문장을 **배제**하므로
통과한 5건에는 지시 표현이 하나도 없다. 그런데 PMB gold는 고유명·대명사·
지시사를 **참여자 ∃로 인코딩**하고 자연스러운 subject는 `entity` 항을 쓴다 —
oracle 쪽에만 결박자가 하나 더 생겨 서명이 갈린다. 이 부류는 control에서
**네 번 재현**됐다(V4 2건, V5 2건).

D-33 §9가 이 판단을 형식화했다:

```text
control eligibility excludes X
control PASS therefore says nothing about X
```

그래서 5/5를 받고도 **코호트를 dispatch하지 않았다.** 판정은
`dispatch: blocked` · `operational_patch: forbidden`이고, 다음 행동은
referential ∃ 경계 실사를 Q34로 상신하는 것이다.

## 6. artifact

`stage2_controls_manifest_v5_1.json` · `stage2_controls_plan_v5_1.json` ·
`stage2_controls_trials_raw_v5_1.json`(원본 봉투 보존) ·
`stage2_controls_results_v5_1.json` · 계약 `test_stage2_controls_v5_1.py`(8종).
커밋 `3125d8d`(재선별) · `e5ef159`(결과).
