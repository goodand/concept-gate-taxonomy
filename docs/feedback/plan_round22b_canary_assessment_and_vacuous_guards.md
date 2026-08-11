# 검증·재사용·의존성·구현 계획 — 22b라운드: canary 판정과 또 공허한 가드 2개

작성 2026-08-11. 대상 커밋 `186c058`. 판정: **canary 진행 가능, 단일 PASS 보고 금지.**

## 1. 주장 검증 — 6/6 확인

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| 1 | 3층 판정이 문서에만 있고 산출물 계약에 없다. 정상 canary도 `qualification.passed=false` | **CONFIRMED** | `"passed": phase_name == "pilot" and not qualification_failures` — canary는 **항상** false |
| 2 | 특권 함수 보호 AST 테스트가 조건의 **의미**를 검사하지 않는다 | **CONFIRMED — 오염 시험으로 재현** | 아래 §1-1 |
| 3 | ledger 테스트가 실제 기록값을 검증하지 않는다 | **CONFIRMED — 오염 시험으로 재현** | 아래 §1-1 |
| 4 | 정상 canary의 ledger 불변이 provider 의존으로 미뤄졌다 | **CONFIRMED** | 거부 경로만 검사한다 |
| 5 | release 로그가 의도된 음성 대조를 헤더보다 먼저 출력 | **CONFIRMED** | 첫 줄이 `refusing to build a packet: provenance: …` |
| 6 | 커밋 범위 보고가 한 커밋 짧다 | **CONFIRMED** | 라운드 22는 **5커밋**(`5e7dc06`…`186c058`). 내 보고는 `8257139`까지만 |

### 1-1. 내 새 가드 2개가 또 공허하다 — P1 10·11번째

**복사 트리에 위반 입력을 실제로 넣어 측정했다:**

```
#2  if phase_name == "primary":  →  if phase_name != "primary":
    (즉 canary가 primary attempt를 claim하도록 뒤집음)
    pytest -k "no_privileged_function or ledger_records"  →  2 passed   ← 통과

#3  "arms": arms, "case_ids": case_ids  →  "arms": [], "case_ids": []
    pytest 같은 선택                                      →  2 passed   ← 통과
```

**#2가 특히 나쁘다.** 뒤집힌 코드는 **canary가 primary attempt를 소모**한다 —
`--canary`의 계약 중 가장 중요한 조항이고, 그것을 "구조가 보장한다"고 커밋
메시지에 적었으며 "AST 테스트가 그 구조를 고정한다"고 주장했다. **고정하지
못한다.** 조건문을 `ast.unparse`해서 `"phase_name"`과 `"primary"`라는 **문자열이
들어 있는지**만 봤다.

그리고 이것은 **바로 직전 라운드에서 회고 §6에 "가드를 만들면 그 가드를
통과시키는 잘못된 입력을 실제로 만들어 본다"를 규칙으로 적은 세션**에서 났다.
규칙을 문서에 쓰는 것이 규칙을 적용하는 것이 아니라는 증거가 하나 더 늘었다 —
이 저장소가 P1을 기제로 옮긴 이유와 정확히 같다.

## 2. 재사용 후보 조사

| # | 선례 | 적용 |
|---|---|---|
| R5 | `HARNESS_KNOWHOW.md` B4 §163 — 가드가 **무엇을 주장하는지** 보라 / §178 위반 입력 기제화 | #2·#3. 문자열 존재가 아니라 **의미**를 검사해야 한다 |
| R3 | `DESIGN_DECISION_surface_separation.md` §231 trial manifest — 원본 밖에 별도 manifest | #1의 assessment sidecar. **원본 artifact를 고치지 않는다** |
| R7 | `OPERATIONS_PLAN.md` §7 — 이미 충족된 구조는 재설계하지 않는다 | #5를 지금 고치지 않는 근거 |
| R10 | `PROBLEM_1_sufficient_consistent.md` §318 — **작은 smoke가 설계 검토보다 먼저 실제 결함을 찾았다** | canary를 더 미루지 않는 근거. 리뷰어가 인용한 것과 같다 |
| **R11** | **spy/stub으로 호출 경계를 검증** — 모델 행동을 mock하는 것이 아니라 `_run_phase_body`만 성공 stub으로 두고 특권 함수를 감시 | #2·#4의 실행 의미 검증. 이것이 "in-process monkeypatch는 call site를 증명하지 못한다"에 걸리지 않는 이유는 §3에 |
| **R12** | 이 실험의 `KNOWN_UNPROVEN` 관행 + 새 `.py`가 표면 등록을 요구하지 않는다는 실측 | sidecar를 **closure 없이** 추가할 수 있다 |

**R11이 이번 라운드의 발견이다.** 21라운드가 거부한 것은 *"함수를 monkeypatch해
성공시키고 그것으로 call site의 존재를 주장하는 것"*이다. 여기서 하려는 것은
반대다 — **경계를 stub으로 만들고, 그 경계 밖에서 특권 함수가 호출되는지를
관측**한다. 관측 대상이 mock이 아니라 실제 `run_phase`의 제어 흐름이다.

## 3. 검증 방법 설계

### 이번 라운드의 규칙 — 문자열 검사를 실행 의미의 근거로 쓰지 않는다

| # | 지금(공허) | 바꿀 것 |
|---|---|---|
| #2 | 조건문을 `ast.unparse`해 `"primary"` 포함 여부 | **`run_phase(phase_name="canary")`를 실제로 성공 실행**하고 특권 함수 4종의 호출 횟수가 **0**임을 spy로 관측 |
| #3 | 소스에 `pilot["arms"]`가 없는지 | **임시 ledger에 `_record_qualification()`을 실제 실행**하고 기록된 `arms`·`case_ids`·`sha256`을 **값으로** 대조 |
| #4 | 거부 경로만 | 성공 경로에서도 두 ledger의 SHA-256 불변 |

**공허하지 않음을 다시 오염 시험으로 확인한다** — #2는 `!=`로 뒤집고, #3은 빈
리스트로 바꿔, **둘 다 실패해야** 한다. 이번에는 그 확인을 하기 전에 "고쳤다"고
쓰지 않는다.

### provider 없이 어디까지 되는가 — 정직하게

```
provider 불필요:  #2 #3 #4 (성공 경로 배선), #6
provider 필요  :  canary artifact의 실제 kind, host action ≥ 1,
                  3층 판정의 Retrieval·Reconstruction 층
```

`_run_phase_body`를 성공 stub으로 두면 **배선**은 검증되지만 **provider가 실제로
무엇을 했는지**는 검증되지 않는다. 그 구분을 보고에 유지한다.

## 4. 의존성 분석 — 그리고 지금 EXECUTION을 고치지 않는 결정

| 항목 | 파일 | 표면 | closure 필요 |
|---|---|---|---|
| #2 #3 #4 테스트 강화 | `test_live_phase_c.py` | **EXECUTION** | 예 |
| #1 `qualification` 필드 의미 | `run_live_phase_c.py` | **EXECUTION** | 예 |
| #1 assessment sidecar | 새 `.py` | **미등록 가능** | **아니오** |
| #5 로그 순서 | `run_pipeline.py` | AUDIT | 예 |
| #6 보고 정정 | 문서 | — | 아니오 |
| 3층 판정 절차 | `docs/HANDOFF…md` | — | 아니오 |

**canary artifact는 표면 신선도에 게이트되지 않는다.** 22라운드에 "편집을 canary
전에 끝내야 한다"고 판단한 근거는 **qualification** artifact가
`_assert_primary_qualifications`에서 surface drift로 거부되기 때문이었다.
canary는 그 게이트를 통과하지 않으므로 **같은 논리가 적용되지 않는다.** canary
artifact는 자기가 돌던 시점의 `frozen_surface_hashes`를 기록하며, 그것이 기록의
목적이다.

따라서 리뷰어의 순서가 맞다:

```
지금:      문서 2건(#6 정정, 3층 판정 절차)  ← closure 불필요
그 다음:   ★ live canary (실제 provider 호출 — 사용자 확인 필요)
직후:      #2 #3 #4 테스트 강화 + #1 sidecar + #5  → closure 1회
그 다음:   1 case × 4 arms (= 기존 --pilot)
```

**지금 EXECUTION을 고치면 이 세션에서 다섯 번째로 "한 번만 더 고치고"가 된다.**
현재 코드는 **옳다**(가드가 `==`임을 확인했다). 약한 것은 회귀 방지이고, 그것은
이번 canary 실행의 결과를 바꾸지 않는다.

## 5. 구현 계획 — step by step

### 지금 (이 턴)

```
0. #6  라운드22 커밋 범위 정정 (5커밋, 186c058 포함)
1. 3층 판정 절차를 handoff에 실제 필드명으로 고정
2. 22b 미해결 큐를 handoff에 기록 (canary 직후 처리)
```

**필드명은 실측으로 확인했다** — 산문이 아니라 존재하는 키다:

| 층 | 판정 근거 (실존 필드) |
|---|---|
| Runtime | artifact 존재 · `raw` 보존 · 행별 `invalid_run == false` |
| Retrieval | 행별 `host_action_compliance.passed == true` · `read` 액션 ≥ 1 · `critical_path_recall` |
| Reconstruction | `state_accuracy` · `next_action_accuracy` · `stop_condition_accuracy` |

**`qualification.passed`는 canary 판정에 쓰지 않는다.** 정상 canary도 항상
`false`이며 그것은 "자격 미달"이 아니라 "자격 심사가 아님"이다.

### canary 직후 (closure 1회에 묶어서)

```
3. #2  성공 경로 spy 테스트 — 특권 함수 4종 호출 0회
4. #3  _record_qualification을 임시 ledger에 실제 실행해 값 대조
5. #4  성공 경로 ledger SHA-256 불변
6. 각 항목을 오염 시험으로 재확인 (== → !=, 값 → 빈 리스트)
7. #1  canary artifact에서 `qualification`을 제거하거나 `phase_assessment`로 대체
       + assessment sidecar (원본 불변, R3)
8. #5  release 로그 순서
9. closure → release → commit
```

### 미루는 것

F3·F4·F6·F8, 회고 §7의 기제 3종(L1·L5·L6). R7 근거. F4의 순환 문제는 21b 계획
§6에 있다.

## 6. 낮춰야 할 내 주장

- **"AST 테스트가 그 구조를 고정한다"**(커밋 `8726df8`) — 고정하지 못한다.
  조건을 `!=`로 뒤집어 canary가 attempt를 claim하게 만들어도 통과한다.
- **"ledger가 실제 실행을 기록한다"의 회귀 방지** — 빈 리스트를 기록해도 통과한다.
  현재 동작은 옳지만 테스트가 그것을 고정하지 않는다.
- **"커밋 5e7dc06~8257139"** — 라운드 22는 5커밋이고 `186c058`이 빠졌다.
- **"음성 테스트 8종"**(커밋 `8726df8`) — 그중 2종이 의미를 검사하지 않는다.
  숫자는 맞고 강도가 과장됐다.
