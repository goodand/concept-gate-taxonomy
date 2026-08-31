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

## 6. (나)1 사후 실행 — 선례 지도 (2026-08-31, subagent 2건 위임 + lead 재실측)

사용자 지적("workspace 에서 기존에 이 문제를 다룬 적이 있는지 탐색은 한 거야?")
로 실행. **답: 안 했었고, 사후에 하니 선례가 있었다.** 세 계열이고, lead 가
각 대표 실물을 재실측했다.

| 계열 | 실물 (재실측 확인) | 우리 하네스와의 관계 |
|---|---|---|
| **실행 선례** (2026-07-18~19) | `archive/worktrees/concept-gate-agent-publish-vault/experiments/2026-07-18_obligation_certificate_ab/evaluate.py` — "수리본을 파이프라인+certify 에 통과시켜 post-repair verdict 를 계산(자기보고 배제)". 후속 실험이 `mechanically_certified` 로 사전등록까지 | **같은 개념, 다른 층.** 그쪽은 실험 채점기의 재투입, 우리는 conceptgate 계약 층의 같은-생산자 재판정 + 음성 쌍 + stale 결박(그쪽에 없음) |
| **설계 명세 선례** | `notes/research/logical-revision/mechanism_spec.md:553~715` — verify→repair→재검증 고정점 루프, retry limit(mechspec:I6), abstention 종료 | **정합.** §8.2 의 "수렴은 증명 밖" 경계는 이 명세의 루프를 아직 안 만들었다는 말과 일치. v4 U4("국소 repair 가 전역 모순 은닉")·U6("pass 의 의미가 충분히 강한가")는 후속 위험 목록으로 유효 |
| **반대 방향 판정** | e2.2-wt `…/PROBLEM_1_sufficient_consistent.md:571-588` — E2.4 채점은 repair 재투입 검증을 **요구하지 않음**을 명시하고 범위 밖 처리(후에 §15 가 단일 repair 회귀 테스트로 부분 복구) | **충돌 아님.** E2.4 계약 채점의 범위 결정이지 conceptgate 층 금지가 아니다 |

추가 확인 둘:

- **production 층은 의도적 non-re-checking 이다** — 우리 트리
  `cg_obligations.py:291`("옮길 뿐 재검사하지 않는다") ·
  `docs/mechanism.md:126`. 우리 하네스는 이것을 **어기지 않는다** — gate 이관
  판정을 재검사하는 것이 아니라 새 revision 에 생산자를 다시 돌리는 것이다.
- **라벨 어휘의 부재가 실증됐다**: `two_pass`·`Verify1`·`경우 B` 는 workspace
  전체 0건(git log -S 로도 08-31 이전 0건). 선례는 전부 **다른 이름**
  (`post_verdict`·`mechanically_certified`·`재투입`·`fixed point`)으로 존재했다
  — CLAUDE.md "어휘는 채취한다" 규율이 없었으면 이 탐색도 0건으로 끝났다.

**판정**: 완성된 하네스와 충돌하는 선례 없음 — 재작업 불요. 그러나 4단을
제때 했다면 07-18 채점기의 재투입 패턴을 처음부터 인용·계승했을 것이다.
잔여(subagent 자기보고): `*-execution-audit/` 2곳·`재검증` 히트 다수 미열람.

## 7. 측정기 (2026-08-31, 동료 검토 ④ 채택)

하네스의 kill rate 는 `scripts/mutation_two_pass_verify1.py` 로 잰다 —
대상 함수 2개 범위 한정 전수 뮤테이션, 무변이 대조군 내장. 산문에 적힌
수치는 그 시점의 측정 기록일 뿐이고 **정본은 실행 출력**이다. 마지막 측정:
2026-08-31, 지점 21, kill 21/21 (동료 검토 채택 반영 후).
