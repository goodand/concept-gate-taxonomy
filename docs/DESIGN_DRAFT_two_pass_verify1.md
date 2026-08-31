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
