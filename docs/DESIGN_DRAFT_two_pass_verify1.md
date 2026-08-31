# 설계 초안 — TWO_PASS_VERIFY1 하네스 (2026-08-31)

- 지위: **초안.** 계약(TDD)을 쓰기 전의 설계다. 구현 아님.
- 사다리: **L2**(document ⊨ formal model 의 기계 보증) — HANDOFF §0.5.
- 정본 근거: SURVEY §8.2~§8.3(경우 A/B) · `test_e2e_v0_refine_verify.py:186`
  (손으로 쓴 `all_pass`) · `cg_obligations.py:341`(`results_from_normalizer`,
  실제 생산자) · `:460`(`stale_obligations`).

## 1. 무엇을 증명하고, 무엇을 증명하지 않는가 — §8.2 표를 잇는다

```text
지금(경우 A)   G₀ → Verify₀ → FAIL(O₀) → repair → G₁ → STOP
목표(경우 B)   G₀ → Verify₀ → FAIL(O₀) → repair → G₁ → Verify₁
```

| 주장 | 이 하네스 후 |
|---|---|
| 1회 repair 가 그 obligation 을 **해결했다** | **예** — Verify₁ 이 같은 생산자로 재판정 |
| G₁ 이 G₀ 보다 나아졌다 | **예** — O₀ 항목에 한해 |
| 반복 수렴한다 / oscillation 없다 | **아니오. 여전히 불가** — repair 1회 설계(§8.2). **이 한계를 계약 docstring 에 명시한다** — 안 적으면 "v0 완료"가 "수렴 입증"으로 읽힌다 |

**[정정 — 계약 작성 전 More READ]** 초판은 `results_from_normalizer` 를
지목했으나 **형식이 안 맞는다**(그것은 normalizer 성공 응답 `resp["ok"]`·
`source.sha256` 을 요구하고, [5] 의 repair 산출은 claim dict 다). 그리고 [4] 의
O₀ 도 손으로 만든 것이었다 — **두 패스 모두** 계산으로 바꿔야 한다.

채택 생산자: **`results_from_claim_anchoring(claims, evidence_texts)`**(`:574`) —
claim 을 직접 받고, "인용 evidence 본문 없음 → UNKNOWN"(`:590`)이 정확히 O₀ 의
의미이며, `graph_revision` 을 실어 나른다. **검사기 신설 없음** — 어댑터도 불요.

## 2. 계약 목록 (KNOWHOW §D 적용)

| # | 계약 | 형태 |
|---|---|---|
| 1 | Verify₀ 가 `source.span_evidence` **UNKNOWN**(ev3 미인용)을 낸다 — 손이 아니라 계산으로 | D1(원문에서) |
| 2 | repair 후 Verify₁ 이 **같은 생산자**로 그 obligation 을 **PASS** 로 낸다 | 본체 |
| 3 | **음성 쌍**: obligation 을 해소하지 **않는** repair(무관 필드 수정) 후 Verify₁ 은 여전히 UNKNOWN | D-공통(음성 증명) — 이것이 없으면 "항상 PASS" 구현이 통과한다 |
| 4 | Verify₁ 은 graph 를 **수정하지 않는다** — G₁ fingerprint 전/후 동일 (`directive:I3`) | 층 격리 |
| 5 | O₀(r1 결박)는 G₁(r2) 대해 **stale** — `stale_obligations` 가 표시하고, Verify₁ 산출은 r2 결박 | 시점 결박 |
| 6 | Verify₁ 산출의 `invariant` 는 **None 그대로** — 값 채움은 별도 설계 판단(회고 2부 §미해결). 여기서 슬쩍 채우지 않는다 | 범위 절제 |
| 7 | 구 revision r1 은 불변 — repair 는 새 revision 을 만든다 (기존 [5] 단언 유지) | 기존 계승 |

## 3. 하지 않는 것 (PASS 사유 포함)

- **반복 루프·진동 감지** — repair 1회 설계. 트리거는 roadmap 이 관리.
- **invariant 값 채움** — 계약 6이 오히려 "안 채웠음"을 고정한다.
- **oracle 개입** — Verify 는 oracle 을 모른다(`directive:I7`).
- **8단(Sonnet 위임)** — 미정. 변경이 `test_e2e_v0_refine_verify.py` 한 파일의
  [6] 치환 + 계약 추가라 작으면 직접, 커지면 위임. 계약을 쓴 뒤 판단.

## 4. 위험 (More READ 로 좁힌 것)

- `results_from_normalizer` 는 **응답 dict 형식**을 요구한다 — [5] 의 repair 가
  만드는 G₁ 이 그 형식인지 먼저 확인해야 한다(아니면 어댑터 한 줄이 필요하고,
  그 어댑터가 **판정을 세탁하지 않는지**가 새 검증점이 된다).
- 손 `all_pass` 를 쓰는 **다른 소비자**가 [6] 외에 있는지 전수 확인 후 치환.

다음 단계: 7단(계약 적대검증, 금지문 2 포함) → 구현 → SURVEY §8.3 갱신(경우 B 도달).

## 5. 사후 기록 — 프로토콜 (나) 대조 (2026-08-31, 완료 후 감사)

사용자 지적("구현 및 수정은 프로토콜을 따라야 한다")로 작성. 규칙:
건너뛴 단계는 사실과 이유를 명시한다 — §3 이 8단을 "미정"으로 남겼으므로
여기서 확정한다.

| 단계 | 실행 여부 | 기록 |
|---:|---|---|
| 1 넓은 범위 분할 조사 | **부분 — 위반** | e2e·`cg_obligations` More READ 는 했으나 **분할·위임 없이 main 직접**. (다)1(subagent 먼저) 위반 재발 — CLAUDE.md 가 이미 기록한 그 패턴이다 |
| 2 Edge/Risk/Dirty More READ | **부분** | Risk More READ 는 §4(형식 불일치 발견 → 생산자 교체). **Dirty 는 시작 시점에 안 쟀다** — 사후 실측(완료 후): 등록 worktree 7개 전부 clean, 충돌 없었음. 결과가 무사한 것이지 절차가 맞았던 것이 아니다 |
| 3 의존성 분석 | 실행 | 손 `all_pass` 소비자 전수(test_e2e_v0 3곳 + test_cg_obligations:113 이름만) |
| 4 workspace 재사용 | **완료 — 조기 중지 발동점** | `results_from_claim_anchoring(:574)` 발견·채택. 검사기 신설 0, 어댑터 0 |
| 5 github subtree | **PASS** | 사유: 4단에서 완료 — 조기 중지 규칙(4→8 구간) |
| 6 TDD | 실행(변형) | 계약 8개 작성. 단 생산자가 실재해 **빨강 없이 초록** — 구현을 구속하는 TDD 가 아니라 경우 B 의 증거물. 이 성격은 테스트 docstring 이 명시 |
| 7 적대검증 | 실행 | agent 위임(금지문 2 포함) → MAJOR 2 채택·수정안 1 재실측 기각. 전문은 테스트 docstring |
| 8 Sonnet 구현 위임 | **PASS (§3 "미정"의 확정)** | 사유: 위임할 구현이 **없었다** — 4단 재사용으로 신규 코드 0줄, 수정도 테스트 파일 자신뿐. 위임 대상이 없는 위임은 공정이 아니다 |

**위반 요약**: (다)1(쿼리 생성 위임 먼저) 1건 · (나)2 Dirty 시점 미실측 1건.
둘 다 결과 무사였으나 절차 위반은 위반이다 — 다음 구현 진입 시 첫 행동을
"범위 분할 + subagent 위임"으로 시작할 것.
