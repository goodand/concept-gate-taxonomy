# 검증·재사용·의존성·구현 계획 — 22라운드: canary 실행 계약

작성 2026-08-11. 대상 커밋 `efea0f2`. 검토 제안: `--canary` 모드를 먼저 고정한 뒤
HD01 × S_STATIC 실행.

**구현 완료 — 라운드 22는 5커밋이다**: `5e7dc06` · `65da9fc` · `8726df8` ·
`8257139` · `186c058`. 최초 보고에서 마지막(검증 receipt)이 빠졌다.
후속 검토와 잔여 항목은
[`plan_round22b_canary_assessment_and_vacuous_guards.md`](plan_round22b_canary_assessment_and_vacuous_guards.md).

## 1. 주장 검증 — 6/6 확인, 그중 하나는 더 나쁘고 하나는 더 약하다

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| A | CLI가 `--pilot`/`--primary`뿐 | **CONFIRMED** | `add_mutually_exclusive_group(required=True)`에 그 둘만 |
| B | 1×1을 `--pilot`으로 돌리면 qualification artifact가 된다 | **CONFIRMED** | `if phase_name == "pilot": _record_qualification(...)` — 무조건 |
| C | qualification ledger가 override가 아니라 **config의 전체 arms/cases**를 기록 | **CONFIRMED** | `_record_qualification`이 `out["config"]["pilot"]["arms"]`를 읽는다. `run_phase`가 받은 실제 `arms`를 쓰지 않는다 |
| D | 따라서 1×1 canary가 1×4 qualification처럼 기록될 수 있다 | **부분 확인 — 기록 결함이지 게이트 우회는 아니다** | 아래 §1-1 |
| E | `--primary`는 stale qualification·authorization에 정상 차단 | **CONFIRMED** | doctor exit 1이 그 상태 |
| F | handoff가 canary 모드와 32칸의 artifact 종류를 명시하지 않는다 | **CONFIRMED** | §5 절차 2·3행에 모드도 kind도 없다 |
| G | handoff가 두 canary를 혼합한다 | **CONFIRMED, 내 결함** | 아래 §1-2 |

### 1-1. D는 정확히 나눠야 한다 — ledger는 거짓말하지만 게이트는 막는다

실측:

```
phase_c_claude_mcp_surface_v3_config.json 의 pilot 행렬
  case_ids = ['HD01']
  arms     = ['S_STATIC','R_STATIC','S_DYNAMIC','R_DYNAMIC']

--pilot --case-id HD01 --arm S_STATIC 로 1칸만 돌렸을 때
ledger에 기록될 내용:
  arms     = ['S_STATIC','R_STATIC','S_DYNAMIC','R_DYNAMIC']   ← 1개만 돌았는데 4개
  case_ids = ['HD01']
```

**그러나 `_assert_primary_qualifications`는 ledger만 보지 않는다.** artifact
자체에 대해 세 가지를 더 대조한다(전부 소스에 존재 확인):

```
artifact["n_runs"] != len(expected_arms) * len(expected_cases)     → 거부
set(per_arm) != set(expected_arms)                                  → 거부
per_arm[arm]["n"] != len(expected_cases)                            → 거부
```

1×1 artifact는 `n_runs=1`, `per_arm`에 1개 arm뿐이므로 **`incomplete
qualification matrix`로 거부된다.** 따라서:

- **틀린 것**: "1×1 canary가 qualification으로 통과할 수 있다" — 통과하지 못한다.
- **맞는 것**: **append-only ledger에 영구적인 거짓 행렬 선언이 남는다.** `doctor`와
  사람이 읽는 기록에 canary가 4-arm qualification으로 보인다. `results/`는 지울 수
  없으므로 그 거짓은 되돌릴 수 없다.

severity를 이렇게 낮추되 **고치는 결정은 유지한다** — 이유는 §4의 비용 분석이다.

### 1-2. G는 내가 21c에서 만든 것이다

`docs/HANDOFF_20260810_primary_blocked.md:762`:

> **live canary — 1 case × 1 arm 실제 provider 호출.** 다음 할 일. `command`에
> 실제 CLI를 넘기는 자리는 이제 있다 — `_stub_reviewer_script`가 …

`--command`와 `_stub_reviewer_script`는 **reviewer isolation** 경로다. retrieval
subject canary는 `run_live_phase_c.py`이고 그 둘은 아무 관계가 없다. 무맥락
agent가 이 항목을 읽으면 **엉뚱한 프로그램을 실행한다.** 21c에서 "다음은 canary"를
적으면서 직전에 만든 기제를 그 자리에 끼워 넣었다 —
**P-문서가계약을가르침의 13번째**이고, 내가 그 패턴을 회고에 지배 패턴으로 적은
바로 그 세션에서 났다.

### 1-3. 리뷰어가 지적하지 않은 위험 — `kind`가 삼항식이다

```python
"kind": "live-subject-pilot" if phase_name == "pilot" else "live-subject-primary",
```

`phase_name`이 `"pilot"`이 아니면 **무엇이든** `live-subject-primary`가 된다.
`--canary`를 단순히 새 `phase_name`으로 추가하면 **canary artifact가 primary라고
자기를 선언한다.** 그리고 `make_safety_audit_blind_input`은
`live-subject-primary`를 받아들인다(`kind` 검사가 그 값을 요구한다).

즉 **1칸 canary가 감사 파이프라인에 primary 결과로 들어갈 수 있다** — 21라운드에
`run_pipeline --primary`에서 닫은 오염 경로와 **정확히 같은 형태**다. 같은 줄에
`interpretation`도 삼항식이라 canary가 "descriptive one-replicate live-subject
run"이라고 주장한다.

**따라서 `kind`/`interpretation`/`arm_effect_estimable`을 삼항식이 아니라
phase별 매핑으로 바꾸고, 미등록 phase는 예외로 만든다.**

## 2. 재사용 후보 조사

| # | 선례 | 적용 |
|---|---|---|
| R2 | `DESIGN_DECISION_surface_separation.md` §3 canonical builder — smoke·qualification·본 실행·재실행이 **동일 builder** | **별도 `run_live_canary.py`를 만들지 않는 근거.** `run_phase`/`_run_phase_body`에 phase 하나를 더한다 |
| R3 | 같은 문서 §6 trial manifest — 해시를 payload 밖에 목록으로 | Step 7의 실패 실행 보존 필드. **이미 대부분 있다**: `config_sha256`, `judge_pins`, `frozen_surface_hashes`, `raw`, `traces` |
| R5 | `HARNESS_KNOWHOW.md` §163 "가드가 무엇을 주장하는지" / §178 위반 입력 기반 음성 커버리지 | Step 2의 음성 테스트 8종. **ledger 검증은 실행 전후 SHA-256 비교**이지 함수 호출 여부가 아니다 |
| R7 | `OPERATIONS_PLAN.md` §9 "이미 충족된 원칙은 재구조화하지 않는다" | F3/F4/F6/F8을 이 단계에 넣지 않는 근거 |
| **R8** | `run_phase`의 **기존 구조** — 모든 특권 동작이 `if phase_name == "primary"`로 묶여 있고 `_record_qualification`은 `== "pilot"` | **새 phase는 자동으로 아무 특권도 얻지 않는다.** 이것이 이 변경을 작게 만드는 핵심이고, 새로 설계할 것이 없다는 뜻이다 |
| **R9** | 이 실험의 `--output-name` + "refusing to overwrite an existing live result" | Step 7의 `attempt1`/`attempt2` 보존이 **이미 강제된다**. 새 기제 불필요 |

**R8·R9가 이번 라운드의 발견이다.** 리뷰어의 8단계 계획 중 Step 7(실패 보존)은
이미 구현돼 있고, Step 1의 "특권 함수를 부르지 않아야 한다"는 **구조가 이미 보장**한다.
남는 실제 작업은 (a) 1×1 강제, (b) `kind` 매핑, (c) ledger가 실제 override를 기록,
(d) 음성 테스트, (e) 명칭 정리다.

## 3. 검증 방법 설계

원칙은 21c에서 추가한 것을 그대로 쓴다: **가드를 만들면 그 가드를 통과시키는
잘못된 입력을 실제로 만들어 본다.** 여기에 이번 라운드의 제약이 붙는다 —
**provider를 부르지 않고 검증할 수 있는 것과 없는 것을 분리한다.**

| # | 먼저 빨갛게 | 방법 | provider 필요 |
|---|---|---|---|
| N1 | case 2개 → 거부 | `run_phase(["HD01","HD02"], ["S_STATIC"], phase_name="canary")` | 아니오 (게이트가 먼저) |
| N2 | arm 2개 → 거부 | 같은 형태 | 아니오 |
| N3 | 기존 output 이름 → 거부 | 기존 `results/` 파일 이름 | 아니오 (기존 기제) |
| N4 | canary 후 **qualification ledger SHA-256 불변** | 실행 전후 `_sha256_path` 비교 | **예** |
| N5 | canary 후 **primary attempt ledger SHA-256 불변** | 같음 | **예** |
| N6 | artifact `kind == "live-subject-canary"` | 아래 §5 대체 검증 | **예** |
| N7 | host action 0개인데 valid로 기록되면 실패 | 기존 `_assert_redteam_covers_config`류가 아니라 trace 검사 | **예** |
| N8 | subject context에 gold/evaluator/prior trace 노출 | 기존 red-team이 이미 검사 | 아니오 |

**N4~N7이 provider를 요구한다는 점이 문제다.** provider 호출 없이 그 4개를
검증하려면 **`_run_phase_body`를 monkeypatch해야 하고, 그러면 21라운드가 거부한
"in-process monkeypatch는 call site의 존재를 증명하지 못한다"에 걸린다.**

**해결**: N4·N5는 **provider 호출 없이도 성립하도록 게이트 앞에 둔다.** 즉
`run_phase(phase_name="canary")`가 N1/N2로 거부되는 경로에서도 두 ledger의
SHA-256이 불변임을 확인한다 — 거부 경로에서 ledger가 오염되지 않는 것도 필요한
명제다. 그리고 **N4~N7의 완전한 형태는 실제 canary 실행 자체가 검증한다**(Step 5
직후 ledger 해시를 비교한다). 그것을 **실행 절차의 일부로 문서에 고정**한다.

**이 분리를 명시하는 이유**: "8개 음성 테스트를 넣었다"고 보고하면서 실제로는
4개가 mock 기반이면 그것이 P1이다. **provider가 필요한 검증은 테스트가 아니라
실행 체크리스트로 남긴다.**

## 4. 의존성 분석

| 파일 | 표면 | 이번 범위 |
|---|---|---|
| `run_live_phase_c.py` | **EXECUTION** | 편집 — `--canary`, `kind` 매핑, ledger가 실제 override 기록 |
| `test_live_phase_c.py` | **EXECUTION** | 음성 테스트 N1~N3, N8. *(초안에 AUDIT이라 적었다 — 틀렸다. 실측으로 EXECUTION이며, 결론(closure 1회)은 같지만 사실이 달랐다)* |
| `docs/HANDOFF_…md` | 문서(canary 입력) | 명칭 분리, 절차에 모드·kind 명시 |
| `PREREGISTRATION.md` | **동결** | canary 계약 amendment |
| `_evaluator.py`, `_providers.py` | EXECUTION | **무변경** |

### EXECUTION 편집의 비용 — 지금은 0이다

`run_live_phase_c.py`를 고치면 calibration·red-team 2종·**qualification 2종**이
stale이 된다. 앞선 세 라운드가 이 편집을 피한 이유가 그것이다.

**그런데 qualification 2종은 이미 stale이다.** `doctor`가 그것을 보고하고 있고,
handoff §5 단계 4가 **새 config로 재-qualification**을 이미 예정한다. 따라서:

```
지금 EXECUTION을 고치는 비용 = calibration 1회 + red-team 2회  (= closure 1회)
                             + qualification 재실행 0회 (이미 빚이다)
```

**반대로 canary 이후에 고치면**: canary → (여기서 편집) → 재-qualification.
그러면 canary가 **고치기 전 코드**로 돌아간 결과가 되고, 그 artifact는 이후 코드와
`frozen_surface_hashes`가 다르다. **canary를 다시 돌려야 한다.**

**결론: 편집은 canary 전에, 한 번에 끝내야 한다.** 리뷰어의 Step 3과 같고, 근거는
비용이 아니라 **canary artifact의 표면 일치**다.

### 순환 주의

`closure`는 calibration + red-team 2종을 돌린다. red-team은
`_assert_redteam_covers_config`로 config 목록을 검사한다. `--canary`가 새 config를
요구하지 않으므로(surface_v3 재사용) **순환은 없다.** 새 config를 만들면
`frozen_surface_execution.json` + `ALLOWED_CONFIG_NAMES` 이중 등록이 필요해지므로
**이번 라운드에서는 만들지 않는다.**

## 5. 구현 계획 — step by step

```
0. 문서 명칭 분리 + 절차에 모드·kind 명시      ← 지금 잘못된 지시를 주고 있다
1. kind/interpretation을 phase 매핑으로        ← §1-3, 가장 위험한 것
2. --canary: 1×1 강제, 특권 함수 미호출
3. _record_qualification이 실제 override 기록   ← §1-1
4. 음성 테스트 N1~N3, N8 (+ 거부 경로 ledger 불변)
5. 전체 suite → calibration → red-team 2종 → frozen 재검사 → closure  (한 번)
6. clean commit
7. preflight: doctor + e2e --release            ← 실행 세션에서
8. HD01 × S_STATIC canary + ledger 해시 전후 비교
9. 3층 판정(Runtime / Retrieval / Reconstruction)
```

**0을 먼저 하는 이유**: 21c가 가르친 것이다. 코드를 고치고 문서를 나중에 고치면
그 사이에 새 모순이 들어온다. 그리고 §1-2의 결함은 **지금 무맥락 agent를 잘못된
프로그램으로 보낸다.**

**1을 2보다 먼저 하는 이유**: `--canary`를 먼저 넣으면 그 순간부터 canary artifact가
`live-subject-primary`로 기록된다. 위험한 상태를 한 커밋이라도 남기지 않는다.

**5를 한 번만 하는 이유**: calibration 후에 코드를 다시 고치면 다시 stale이다.
이 세션이 네 번 반복한 일이다.

### 이번 범위에서 제외 — 근거와 함께

- **F3/F4/F6/F8** — R7. canary를 막지 않는다. 특히 F4는 순환 해소 설계가 별도로
  필요하다(21b 계획 §6).
- **회고 §7의 기제 3종(L1·L5·L6)** — AUDIT 표면을 바꿔 closure를 한 번 더
  요구한다. canary 이후.
- **새 config / 재-qualification** — canary는 authorization을 요구하지 않으므로
  불필요하다. 1×4 이후.
- **1×4** — 리뷰어의 Step 8. 주의: surface_v3의 pilot 행렬이 **정확히 HD01 × 4
  arms**이므로, "1×4"는 새 모드가 아니라 **기존 `--pilot` 그 자체**다. 별도
  설계가 필요 없고, 그때 `--pilot`을 override 없이 돌리면 된다.

## 6. 낮춰야 할 주장

- 리뷰어의 **"1×1 canary가 1×4 qualification처럼 기록될 수 있다"** — 기록은 그렇게
  되지만 **게이트는 막는다**(`n_runs`·`per_arm`). 영구적 거짓 기록이 문제이고
  authorization 우회는 아니다.
- 리뷰어의 **Step 7(실패 실행 보존)** — 새로 만들 것이 거의 없다.
  `--output-name` + overwrite 거부 + `config_sha256`/`judge_pins`/
  `frozen_surface_hashes`/`raw`/`traces`가 이미 있다. 빠진 것은 `rendered prompt
  sha256`과 `환경 capability` 두 필드뿐이다.
- 내 handoff의 **"다음 할 일: live canary"** — 그 항목이 **다른 canary**를
  설명하고 있었다(§1-2).
