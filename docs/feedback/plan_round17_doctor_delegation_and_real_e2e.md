# 수정·검증 계획 — 17라운드 (Amendment 38 예정)

작성 2026-08-11. **검증 완료, 미착수.** 대상 커밋 `523db5a` 이후.

## 검증 결과 — 7/7 재현

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| 1 | doctor가 production readiness를 재구현하며 qualification gate 누락 | **확인** | production `_assert_primary_qualifications` → `REFUSED: qualification artifact is stale`. doctor → `7 pass, 0 fail, exit 0`. `_assert_*` 호출 **0건** |
| 2 | BLOCKED가 exit 0 | **확인** | `return 1 if fails else 0` (doctor), `return 1 if hardened_leaks else 0` (red-team) |
| 3 | doctor가 red-team의 `status`/`passed`를 무시 | **확인** | `status=FAIL`, `hardened_profile_passed=false` artifact 주입 → `[ok  ] red-team: provider isolation  FAIL`, `0 fail`, `exit 0` |
| 4 | offline E2E가 production pipeline이 아님 | **확인** | `_synthetic_primary()`가 직접 합성, adjudication은 `asa.adjudicate()` 헬퍼 호출, 번들은 메모리에서 종료 |
| 5 | #2·#3 미해결을 E2E가 정상 통과시킴 | **확인** | `authorization`/`attempt_ledger`/`config_sha256`/`qualification` = 두 감사 스크립트에 **0건**. `_qualify_reviewer`는 `run_pipeline.py`에만 존재 |
| 6 | red-team이 최신 config를 검사 안 함 | **확인** | codex red-team은 `v7`, provider red-team은 `v7`/`surface-v2`까지. 대상은 v9/surface-v3 |
| 7 | E2E에 독립 mutation 검사 없음 | **확인** | 테스트는 `assert run_pipeline.e2e_offline() == 0` 한 줄 |

**#6은 15라운드에서 이미 제기됐는데(당시 #5) 제 미해결 목록에서 빠졌습니다.** 그 누락 자체가 이번 라운드에 다시 잡혔습니다.

## 진단 — 무엇이 근본 원인인가

**#1·#3·#4는 한 원인의 세 얼굴입니다: doctor와 e2e가 production 판정을 *복제*했습니다.**
저는 "canonical path 원칙을 적용했다"고 썼는데, 실제로 한 것은 정반대였습니다 —
readiness를 다시 계산하고, primary를 직접 합성하고, adjudication을 헬퍼로 불렀습니다.
선례(`DESIGN_DECISION_surface_separation.md` 필수 테스트 #7)의 요구는
*"동일 함수를 쓴다"*이지 *"같은 판정을 다시 구현한다"*가 아닙니다.
**진단 도구가 판정을 소유하면, 진단이 초록인데 production이 거부하는 상태가 생깁니다 — 정확히 지금 상태입니다.**

**#2는 3값 어휘를 출력 문자열에만 적용하고 exit code에 적용하지 않은 것입니다.**
`BLOCKED is not a pass`를 출력하면서 `exit 0`을 반환하면, 사람은 읽고 기계는 못 읽습니다.
이 저장소는 `run_gates.py`에서 이미 같은 문제를 겪었고, 거기서는
*"exit 0을 머지 조건으로 배선하지 마라"*로 **문서 경고**를 택했습니다.
그 선택이 지금 doctor에서 반복됐으므로, 이번엔 exit code 자체를 3값으로 만듭니다.

**#5·#6은 미해결 항목이 "다음에"로 밀린 것이고, #7은 그 밀림을 막을 장치가 없다는 것입니다.**

---

## 수정 계획

### 단계 1 — doctor는 판정하지 않고 **위임**한다 (#1·#3)

`doctor`의 각 검사를 production 함수 호출로 바꾼다.

| 검사 | 지금 (복제) | 바꿀 것 (위임) |
|---|---|---|
| qualification | 없음 | `_assert_primary_qualifications(config)`를 try/except로 |
| readiness 전체 | 해시 직접 비교 | `_assert_ready(config_path)` |
| red-team | `conclusive` + drift만 | 위 두 함수가 이미 검사 — 그 예외 메시지를 그대로 표시 |

**doctor가 자체로 판정하는 것은 production 함수가 존재하지 않는 것만**:
판정자 배정 상태, CLI 존재 여부. 그 외에는 `LiveRunError` 메시지를 렌더링만 한다.

부수 효과로 #3이 사라진다 — `status`/`passed`를 doctor가 따로 읽지 않고
red-team artifact를 검사하는 production 코드가 판정하므로, 두 곳이 어긋날 수 없다.
단, production 쪽이 `hardened_profile_passed`만 보고 `status`는 안 보므로
**그 검사를 `run_live_phase_c.py`에 추가**한다(판정의 정본은 거기다).

**config 인자**: doctor는 `--config`를 받고, 기본값은
`PRIMARY_AUTHORIZATION.json`의 `config_file`. 승인이 가리키는 것과 다른 config를
점검하는 실수를 없앤다.

### 단계 2 — exit code를 3값으로 (#2)

```
0 = PASS      모든 게이트가 판정을 냈고 전부 통과
1 = FAIL      판정을 냈고 실패한 게이트가 있음
2 = BLOCKED   판정을 내지 못한 게이트가 있음 (실행 불가·미배정)
```

`run_pipeline.py doctor`, `redteam_provider_isolation.py`,
`redteam_codex_mcp_isolation.py`에 동일 적용. `run_gates.py`의 3값 표와 같은
어휘이며, 차이는 **exit code에도 반영한다**는 점뿐이다.
`README`와 handoff에 `2`의 의미를 적는다.

### 단계 3 — E2E의 주장을 실제 범위로 낮추고, 범위를 넓힌다 (#4)

두 가지를 **동시에** 한다. 하나만 하면 과장이 남거나 비용이 폭발한다.

**(a) 주장 정정** — 현재 커버리지를 출력에 명시:

```
covers: synthetic artifact -> audit gate -> packet CLI -> adjudication CLI -> bundle file
does NOT cover: provider execution, qualification, authorization, attempt claim
```

`e2e --offline`이라는 이름 자체가 provider 부재를 말하지만, **qualification과
authorization을 우회한다는 사실은 이름에 없다.** 출력에 적는다.

**(b) 범위 확대** — 우회 중인 것 중 provider 없이 실행 가능한 것을 넣는다:

- adjudication을 `asa.main(["--out-root", tmp])`로 — **CLI 경유**(이미 `--out-root` 있음)
- 최종 번들을 **파일로** 쓰고 다시 읽어 검증(메모리 종료 금지)
- `_assert_primary_authorization`을 **소비 없이** 호출해 승인 검증 경로 포함
- attempt ledger는 **claim하지 않고** 원장 형식·해시 체인 검증 함수만 호출

`run_phase()` 자체는 provider를 호출하므로 offline에서 부를 수 없다. **그 경계를
출력에 적는 것이 정직한 답이고, 지우려 하면 offline이 아니게 된다.**

### 단계 4 — 감사 입력에 **출처** 결속 (#5, 15라운드 #2 미해결)

`safety_audit_spec.json`에 추가:

```json
"require_provenance": true,
"provenance": {
  "authorization_file": "results/PRIMARY_AUTHORIZATION.json",
  "attempt_ledger": "results/primary_attempt_ledger.jsonl",
  "require_completed_attempt": true
}
```

`validate_audit_input()`이 추가로 검사:

- artifact의 `config_file`·`config_sha256`이 authorization의 것과 일치
- artifact가 attempt ledger에 **완료된 시도**로 기록돼 있음
- artifact의 `frozen_surface_hashes`가 execution layer에서 drift 없음

**spec은 matrix 권위일 뿐 결과 출처 권위가 아니다**는 지적을 이것으로 닫는다.

### 단계 5 — 판정자 자격을 **apply gate에 연결** (#5, 15라운드 #3 미해결)

`_qualify_reviewer`를 `run_pipeline.py`에서 꺼내 `apply_safety_audit.py`로 옮긴다.

- 판정자는 `qualification` 블록을 label 파일에 포함:
  `{"reviewer_id", "packet_sha256", "assignment_sha256", "fixture_sha256", "qualification": {...}}`
- `adjudicate()`가 채점해 **틀리면 그 판정자의 라벨을 거부**
- 정답이 fixture 파일에 함께 있는 문제(15라운드 #3 후반)는
  **정답을 `safety_audit_rubric_answers.json`으로 분리**하고, 그 파일은 판정자
  워크스페이스에 넣지 않는다. fixture(문항)만 packet과 함께 나간다

### 단계 6 — red-team을 **최신 config identity에 결속** (#6)

- 두 red-team이 검사한 config 파일명과 sha256을 artifact에 기록
  (`checked_configs: [{file, sha256}]`)
- 검사 대상을 **하드코딩하지 않고** authorization의 `config_file` + spec에서 읽음
- readiness가 **"승인이 가리키는 config가 red-team이 검사한 목록에 있는가"**를 검사

이것이 없으면 최신 config를 한 번도 안 본 red-team이 현재 surface hash로 PASS
artifact를 만든다 — 지금 상태다.

### 단계 7 — E2E에 **외부 acceptance test** (#7)

E2E가 자기 단계와 기대값을 함께 소유하는 문제를 mutation으로 닫는다.
`test_e2e_acceptance.py`(audit surface):

- `run_pipeline.py`의 **단계 블록을 제거한 변형**을 만들어 e2e가 **실패하는지** 확인
  (판정자 자격 블록 삭제, 음성 대조 삭제, provenance 단계 삭제 각 1건)
- 구현은 `test_guard_negative_coverage.py`와 같은 발상: AST로 단계 함수 호출을
  찾아 하나씩 제거한 소스를 임시 모듈로 실행

**이것이 이번 라운드의 재발 방지 장치다.** 단계 1~6은 결함 수정이고, 7만이
"다음에 단계를 빠뜨리면 잡힌다"를 보장한다.

---

## 실행 순서와 이유

```
2 (exit code) → 1 (doctor 위임) → 6 (red-team 결속) → 4 (provenance)
              → 5 (자격 연결) → 3 (E2E 범위·주장) → 7 (acceptance)
              → calibration 1회 → red-team 2종 → qualification 2종
              → 새 authorization → primary
```

- **2를 먼저**: 이후 모든 단계의 검증이 exit code로 자동화된다. 지금은
  초록/빨강을 사람이 읽어야 한다.
- **1을 2 다음**: doctor가 위임하면 4·5·6의 효과가 doctor에 자동 반영된다.
- **6을 4보다 먼저**: provenance 검사가 red-team artifact의 config identity를
  참조하므로 그 필드가 먼저 있어야 한다.
- **3을 5 다음**: E2E 범위 확대가 4·5에서 만든 경로를 포함해야 한다.
- **7을 마지막**: 앞 단계가 만든 단계들을 mutation 대상으로 삼는다.
- **calibration은 모든 편집 뒤 1회.** 이번에도 순서를 어겨 red-team을 두 번
  돌렸다(codex를 고치니 provider가 stale).

## 검증 계획

각 단계는 **실패하는 검사를 먼저 만들고** 통과시킨다(TDD 3규칙 중 1번 적용 대상).

| 단계 | 실패해야 하는 것 (먼저 작성) | 통과 기준 |
|---|---|---|
| 2 | BLOCKED 상황에서 `exit == 2` | 3값 exit이 doctor·red-team 2종에서 일관 |
| 1 | qualification stale일 때 doctor `exit != 0` | doctor 판정 = production 판정, 두 곳이 어긋날 수 없음 |
| 1 | `status=FAIL` artifact 주입 시 `[ok]` 출력 금지 | 주입 재현 스크립트가 FAIL을 표시 |
| 6 | authorization의 config가 red-team `checked_configs`에 없으면 거부 | v9/surface-v3가 목록에 실제로 있음 |
| 4 | authorization/ledger 없는 32칸 artifact가 **거부** | 현재 `accepted=32` → 거부로 전환 |
| 4 | config_sha256 불일치 artifact 거부 | — |
| 5 | 자격 미제출·오답 판정자의 라벨 **거부** | 정답 파일이 판정자 워크스페이스에 **부재** |
| 3 | 최종 번들이 **파일로** 존재하고 재읽기 가능 | 출력에 커버리지·비커버리지 명시 |
| 7 | 단계 블록 3종 각각 제거 시 e2e **실패** | acceptance test가 red로 시작 |
| 전체 | — | calibration 8/8·60/60, `doctor exit 0`, `e2e exit 0`, repo 게이트 |

**환경 표기**: 테스트 수는 `N passed (이 환경)` / `N-6 passed + 6 Seatbelt BLOCKED
(소켓 권한 없는 환경)`로 병기한다. 리뷰어 환경은 187/6, 이 환경은 199다.

## 이번 라운드에서 낮춰야 할 주장

- **"production E2E"** → `offline downstream E2E`. provider 실행·qualification·
  authorization·attempt claim을 우회한다.
- **"canonical path 원칙을 적용했다"** → 적용하지 못했다. doctor와 e2e가 판정을
  **복제**했고, 그래서 doctor 초록·production 거부가 동시에 성립했다.
- **doctor `0 fail`** → qualification을 보지 않은 `0 fail`이었다.

## 범위 밖

리뷰어가 이전 라운드에 제안한 6모듈 분해는 이번에도 넣지 않는다. 단계 1이
doctor의 중복 판정을 제거하므로 결합도 문제의 실질 부분은 완화된다.
