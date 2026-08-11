# 검증·재사용·의존성·구현 계획 — 21c라운드: 공허한 문서 테스트와 부분 해결

작성 2026-08-11. 대상 커밋 `3a28132`.

## 1. 검증 결과 — 5/5 확인

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| 1 | F7은 부분 해결. 운영 절차가 코드와 모순 + **회귀 테스트가 공허** | **CONFIRMED, 가장 나쁨** | 아래 |
| 2 | F5 부분 해결 — PATH 실행 파일 미해시, **측정 시점이 실행 뒤** | **CONFIRMED** | identity는 489행, 실행은 481행. `_execution_identity(['python3',...])`는 `python3`를 해시하지 않는다 |
| 3 | BLOCKED를 LEAK처럼 보고 | **CONFIRMED** | `reviewer_runner.py:476` `p["status"] != "DENIED"` — BLOCKED가 `reached` 목록에 들어간다 |
| 4 | 12/12는 현재 mutation 실행 결과가 아니다 | **CONFIRMED** | release receipt의 `obligations`는 값이 `"pass"`뿐이라 "이 release에서 mutation 12종이 통과"로 읽힌다 |
| 5 | release 성공이 물리 경로·상위 권한에 종속 | **CONFIRMED** | `sandbox_available`은 **바이너리 존재**만 기록해 `/private/tmp` clean clone의 exit 1을 설명하지 못한다 |

### 1-1. 내 F7 테스트는 공허하다 — 실측

```
handoff의 "의무 11/11"·"의무 12/12"를 "의무 99/99"로 바꾼 뒤
  pytest -k entry_block  →  1 passed
```

`test_the_handoff_entry_block_matches_what_the_commands_actually_print`는 **과거
문자열 3개의 부재**만 본다. `n = len(rp.DECLARED_OBLIGATIONS)`는 **오류 메시지에만**
쓰인다. 그런데 그 docstring은 이렇게 쓰여 있다:

> "Compared against the DECLARED COUNT and the real coverage key, not prose
> against prose"

**거짓이다.** 이 저장소가 8번 기록한 P1(공허한 가드)의 **9번째**이고, 하필 F7
— "문서가 코드와 다른 것" — 을 고치면서 만든 가드가 그 자신 공허하며 docstring이
코드가 구현하지 않는 계약을 가르친다. 이 세션이 반복해서 기록한 두 실패 형태가
한 함수 안에서 겹쳤다.

### 1-2. 절차 모순 — handoff가 **평가 corpus**라는 점이 결정적이다

| 위치 | 무엇 |
|---|---|
| `HANDOFF…md:555-560` | 판정자가 label을 수동 제출하고 `--isolation-receipt` **없이** adjudicator를 호출하라고 안내한다. `kind: agent`면 **현재 코드가 그 절차를 거부한다** |
| `HANDOFF…md:459` | `produced_by`와 공개 `receipt_sha256`을 **현행처럼** 설명한다. 21라운드가 제거한 방식이다 |
| `PREREGISTRATION.md:2358` | probe-only를 설명하며 "release E2E가 묻는 것은 경계가 성립하는지다"라고 해, release가 probe-only인 것처럼 읽힌다. 지금은 stub reviewer를 실행한다 |

이 실험은 **무맥락 agent가 `docs/HANDOFF.md`만 보고 재개할 수 있는지**를 측정한다.
문서가 코드와 모순되면 **subject 실패가 검색 실패인지 문서 모순인지 구별되지
않는다.** 즉 이것은 문서 위생 문제가 아니라 **측정 타당성** 문제다. 리뷰어의
"handoff가 canary 입력이면 먼저 동결·정정하라"를 받아들인다.

### 1-3. 리뷰어가 재현한 것 — 받아들인다

- 커밋 6개 `ba50236..3a28132`, F1/F1b/F2, stage 7c, 310 passed, release 0 /
  offline 2 / doctor 1: **전부 재현됨**.
- **`/private/tmp` clean clone에서 같은 커밋이 exit 1** — probe 4종 BLOCKED.
  "이 환경" 한정은 맞았으나 **receipt가 그 차이를 설명하지 못한다**(#5).

## 2. 재사용 후보 조사

| # | 선례 | 적용 |
|---|---|---|
| R5 | `HARNESS_KNOWHOW.md` B4 §163 — *"가드가 통과하는데도 결함이 남을 수 있다: 가드가 **무엇을 주장하는지** 보라"* / §178 B4a — 규율을 AST 기제로 옮김 | #1. 블랙리스트를 **positive contract**로 바꾼다. 필요한 명제를 직접 검사한다 |
| R6 | `DESIGN_DECISION_surface_separation.md` §233 trial manifest — payload 밖에 fixture·prompt·schema·builder·model 해시를 **목록으로** 기록 | #2. execution identity를 opaque digest 하나가 아니라 **입력 manifest + digest**로 |
| R7 | `OPERATIONS_PLAN.md` §9 — *"이미 이 프로젝트 관례가 충족하고 있는 원칙은 재구조화하지 않고 한 줄만 확인한다"* | #5의 범위 결정. F3/F4/F6/F8을 canary 뒤로 미루는 근거 |
| R1 | (21b에서 확인) `build(receipt=...)` 패턴 | 이미 적용됨 |

**새로 만들 것이 없다.** #1은 R5의 직접 적용, #2는 R6의 필드 모양, 범위는 R7.

## 3. 검증 방법 설계

이번 라운드의 검증 규칙은 **하나가 추가된다**:

> **가드를 만들면, 그 가드를 통과시키는 잘못된 입력을 실제로 만들어 본다.**
> 21c가 잡은 것은 "테스트가 없다"가 아니라 **"테스트가 있고 공허하다"**였고,
> 그것을 발견한 방법은 문서를 실제로 오염시켜 테스트를 돌린 것이다. 음성 테스트를
> 쓰는 것만으로는 부족하다 — **음성 테스트가 음성인지**를 확인해야 한다.

| # | 먼저 빨갛게 | 통과 기준 |
|---|---|---|
| 1a | `의무 99/99`로 오염된 handoff가 통과하면 **실패** | 문서의 의무 수를 **파싱해** `len(DECLARED_OBLIGATIONS)`와 대조 |
| 1b | agent 절차에 `--isolation-receipt`가 없으면 **실패** | 문서에 `reviewer_runner.py … --command … --labels-out`과 `apply_safety_audit.py … --isolation-receipt`가 **둘 다** 있다 |
| 1c | 제거된 `produced_by` 방식을 현행처럼 설명하면 **실패** | 문서에서 그 서술이 사라지고 HMAC 서술로 교체 |
| 1d | offline exit 값이 실제와 다르면 **실패** | 문서에서 파싱한 값 == 실제 실행 exit |
| 2 | identity를 실행 **뒤에** 계산하면 실패 / PATH 실행 파일이 빠지면 실패 | 실행 **전** 계산, `shutil.which` 해석, 실행 후 **재대조**, receipt에 파일 목록 기록 |
| 3 | control 실패 probe가 `reached`에 들어가면 실패 | `reached`는 `reachable=True`만. `unmeasured`를 별도로 출력 |
| 4 | release receipt가 `obligations`라는 이름으로 pass를 남기면 실패 | 필드명이 주장의 강도와 일치(`declared_proofs_present`) |
| 5 | receipt가 바이너리 존재만 기록하면 실패 | allowed control과 각 deny probe 상태를 기록 |

**1a와 1d가 핵심이다.** 문자열 부재가 아니라 **문서에서 값을 파싱해 실행 결과와
대조**해야 하고, 그래야 "99/99로 바꾸면 실패한다"가 성립한다.

## 4. 의존성 분석

| 파일 | 표면 | 범위 |
|---|---|---|
| `test_pipeline_gates.py` | AUDIT | #1 positive contract |
| `docs/HANDOFF_…md` | 문서(**canary 입력**) | #1 절차 분리·정정 |
| `PREREGISTRATION.md` | **동결** | #1 probe-only 서술 정정 → closure 필요 |
| `reviewer_runner.py` | AUDIT | #2 identity, #3 reached/unmeasured |
| `run_pipeline.py` | AUDIT | #4 필드명, #5 probe 상태 기록 |
| `test_reviewer_isolation.py` | AUDIT | #2 #3 테스트 |
| EXECUTION 41개 | — | **무변경** |

**EXECUTION 편집 0 → qualification 재실행 불필요.** `PREREGISTRATION.md` 편집으로
closure는 다시 필요하다.

순서와 이유:

```
1. #1 positive contract 테스트  ← 먼저. 이것이 없으면 문서 수정이 다시 썩는다
2. #1 문서 수정                 ← 1이 강제한다
3. #3 reached/unmeasured        ← 진단 정확성. 작고 독립
4. #2 identity(실행 전 + 재대조 + manifest)
5. #4 #5 receipt 필드
6. closure → release → canary 준비
```

**#1을 문서 수정보다 먼저 하는 이유**: 지금 문서를 고치고 테스트를 나중에 만들면,
이번에 고친 내용이 다음 라운드에 다시 낡는다. 21c 자체가 그 증거다 — 21b에서
문서를 고쳤고 테스트가 공허해서 새 모순이 그대로 들어왔다.

## 5. 미루는 것 (R7 근거)

F3(manifest 확장)·F4(mutation 결과 결속)·F6(schema 심화)·F8(receipt 포인터).
리뷰어와 나의 판정이 일치한다: **retrieval canary를 막지 않는다.** F4의 순환
문제는 21b 계획 §6에 기록돼 있다.

## 6. 낮춰야 할 내 주장

- **"F7 완료"** — 부분 해결이었다. 회귀 기제가 공허했고 운영 절차 3곳이 코드와
  모순이었다.
- **"F5 완료"** — argv 안의 파일 수준 부분 해결. PATH 실행 파일을 식별하지 못하고,
  측정이 실행 **뒤**여서 실행된 바이트가 아닐 수 있다.
- **`test_..._matches_what_the_commands_actually_print`의 docstring** — 선언된 수와
  대조한다고 썼으나 그 값은 오류 메시지에만 쓰였다. **P1의 9번째.**
- **release receipt의 `obligations`** — "이 release에서 mutation 12종이 통과"로
  읽힌다. 실제로는 "증거가 선언되고 존재한다"다.
