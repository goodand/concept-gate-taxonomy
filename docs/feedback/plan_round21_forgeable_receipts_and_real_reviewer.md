# 검증·의존성·수정 계획 — 21라운드: 위조 가능한 receipt와 실재하지 않는 reviewer

작성 2026-08-11. 대상 커밋 `b51473e`. **검증 완료, 9건 구현 완료**
(`c772d3b`/`193d9a0`/`96516cb`/`57d3a6e`). **#3(실제 reviewer adapter)까지 완료.** 남은 것은 §6 순서의 10번(live canary)뿐이다. 결과는 handoff §3b.

## 1. 검증 결과 — 8/8 재현, 그리고 리뷰어가 놓친 1건

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| 1 | isolation receipt를 손으로 위조 가능 | **CONFIRMED** | launcher를 한 번도 실행하지 않고 만든 dict가 `verify_isolation_receipt` → `PASS` |
| 2 | v2라고 문서화했지만 실제로는 v1 | **CONFIRMED, 더 나쁨** | `reviewer_runner.py:133` = `seatbelt_profile`(v1). 아래 §2 |
| 3 | launcher가 reviewer를 실행하지 않음 | **CONFIRMED** | `run_reviewer(command=None)`, release E2E는 command 미전달, label은 answer key에서 생성 |
| 4 | `e2e --primary`가 실제 primary가 아님 | **CONFIRMED** | 세 모드 모두 `_synthetic_primary()`. `RunSpec.for_mode`에서 release와 primary가 **동일 필드값** |
| 5 | obligation 10/10 PASS는 소스 상수 | **CONFIRMED** | `OBLIGATIONS` dict 리터럴, `PROVEN_BY`는 문자열 |
| 6 | closure receipt도 최소 JSON으로 위조 가능 | **CONFIRMED** | `{"frozen_surface_hashes": {...}}` 한 키만으로 valid closure 판정 |
| 7 | assignment 문서가 구현과 모순 | **CONFIRMED** | "no sandboxed launcher exists yet" |
| 8 | release 성공이 artifact로 남지 않음 | **CONFIRMED** | `results/`에 `closure_*` 1건 + red-team 2건뿐, isolation·release 기록 0건 |

재현 스크립트는 세션 tmp에 있고 §5의 테스트로 영구화한다.

검증 중 리뷰어가 지적하지 않은 결함 2건이 추가로 나왔다 — **#2a**(probe 2/4가
공허, §2)와 **#9**(CLI 기본 경로가 구조적으로 항상 BLOCKED, §2a).

## 2. #2는 리뷰어의 진단보다 나쁘다 — probe 2/4가 공허하다

리뷰어의 가설: *"상위 sandbox가 홈 접근을 대신 차단해서 성공한 것처럼 보인다."*
실제 원인은 그게 아니고, 더 단순하고 더 나쁘다.

```
PERMISSIVE profile = (version 1)(allow default)   ← deny 0건
  /bin/cat ~/.claude/projects   rc=1  "Is a directory"
  /bin/cat results              rc=1  "Is a directory"
  /bin/cat ...rubric_answers.json  rc=0
  /bin/cat PREREGISTRATION.md      rc=0
```

`_reachable()`은 `returncode == 0`을 도달성으로 읽는다. **`/bin/cat`은 디렉터리에
대해 sandbox와 무관하게 항상 실패한다.** 금지 probe 4개 중 `results_dir`와
`host_transcripts`는 디렉터리이므로, **deny가 하나도 없는 프로파일에서도 `ok`로
보고된다.** 두 probe는 sandbox를 전혀 측정하지 않는다.

v1/v2 대조 실측:

```
v1: 프로파일이 ~/.claude/projects를 deny = False;  cat rc=1  "Is a directory"
v2: 프로파일이 ~/.claude/projects를 deny = True;   cat rc=1  "Operation not permitted"
```

같은 rc, **다른 이유**. rc만 보면 v1과 v2가 구별되지 않는다.

이것은 이 저장소가 7회 기록한 P1(공허한 가드)의 **8번째**이고, 하필 "프로파일
문자열은 주장이고 probe가 증거다"라고 docstring에 쓴 모듈 안에서 났다. probe도
주장이었다. **rc≠0을 "차단됨"으로 읽은 것이 근본 원인**이며, 라운드 17이 닫은
fail-open(모두 거부됐는데 PASS)과 같은 모양의 한 층 아래다.

## 2a. #9 — CLI 기본 출력 경로는 PASS를 낼 수 없다 (canonical path 위반)

`main()`의 기본 `out_dir`은 `HERE / "audit_workspace" / "reviewer"`다. 그런데
프로파일은 `HERE` 전체를 deny한다. 즉 **bundle이 금지 subtree 안에 놓인다.**

```
CLI default bundle: audit_workspace/reviewer/<rid>/packet.json
  is under project_root (denied subtree): True
  allowed probe under v1: rc=1  "cat: /Users/.../Project_in_progress"
  allowed probe under v2: rc=1  (동일)
```

allowed probe가 실패하면 `run_reviewer`는 `status="BLOCKED"`를 낸다. 따라서
docstring이 안내하는 `reviewer_runner.py <packet.json> <reviewer_id>`는
**어떤 환경에서도 PASS를 낼 수 없다.** PASS가 관측된 유일한 경로는 임시
디렉터리를 쓰는 release E2E다.

이것은 2026-07-28에 동결한 canonical path 원칙 위반이다 — 스모크·본 실행·재실행이
같은 builder를 통과해야 하는 이유가 정확히 이것이고, 여기서는 **CLI와 E2E가 서로
다른 경로를 타며 그중 하나가 구조적으로 고장 나 있다.** 리뷰어가 전략 #6에서
*"canonical path 원칙은 함수 하나를 공유한다는 뜻이 아니라 실제 실행 재료가 동일
builder를 통과한다는 의미"*라고 쓴 것의 실증 사례다.

수정: bundle 위치를 정하는 곳을 하나로 만들고, 그 위치가 프로파일의 deny 집합과
교차하면 **거부한다**(BLOCKED으로 조용히 넘어가지 않는다). deny 대상 안에 bundle을
두는 것은 환경 문제가 아니라 호출자의 오류다.

## 3. 리뷰어 개선 전략에서 수정할 3가지

### C1. `_sandbox_profile.py` 추출은 불필요하다 — qualification 재실행 비용 0으로 가능

리뷰어 전략 #1은 leaf module 추출을 제안하며 *"execution surface가 바뀌어
qualification이 다시 stale해지는 비용은 발생하지만"*을 받아들인다. **그 비용은
발생하지 않아도 된다.**

- `seatbelt_profile_v2`의 정본은 이미 하나다 — `_providers.py:163`.
- `run_live_phase_c.py:48`이 이미 그것을 import한다. 정의가 두 벌인 상황이 아니다.
- 따라서 필요한 것은 추출이 아니라 `reviewer_runner.py`의 **import 한 줄 교체**다.

`reviewer_runner.py`는 AUDIT 표면이고 `_providers.py`를 **읽기만** 한다. 표면
파일을 import하는 것은 그 파일을 바꾸지 않는다. 추출은 EXECUTION 파일 2개를
편집해 red-team 2건 + qualification 2건을 무효화한다 — **얻는 것 없이.**

### C2. closure receipt에 release 결과를 넣으면 순환이다

리뷰어 전략 #5는 closure receipt에 `release_exit`, `release_output_sha256`,
`pytest_summary`를 넣자고 한다. 그런데 `e2e --release`는 **현재 표면을 기술하는
closure receipt가 있어야만 실행된다**(`spec.require_closure`). closure가 release
결과를 기록하려면 release가 먼저 있어야 하고, release는 closure가 먼저 있어야
한다. **구현 불가.**

분리한다:

```
closure receipt   = 동결 표면과 재생성된 artifact에 대한 사실   (release의 전제)
release receipt   = 이 환경에서 release가 무엇을 관측했는지     (release의 산출)
                    ← #8이 요구하는 것이 정확히 이것
```

release receipt가 자신이 소비한 closure digest를 기록하면 사슬은 한 방향으로
닫힌다.

### C3. `certify()`를 그대로 정본으로 쓸 수 없다 — seam이 필요하다

`certify()` → `validate_result()` → `OBLIGATION_REGISTRY.get(name)`이고, 이
레지스트리는 `source.snapshot_hash`, `relation.acyclicity`, `owl.consistent` 등
**개념 게이트 도메인 의무만** 담는다. `audit.input-validated` 같은 이름은 없으므로
전부 `UNKNOWN_OBLIGATION`이 되어 `certify()`는 무조건 **FAIL**을 낸다. 지금 코드에
꽂으면 동작하지 않는다.

그런데 **정작 필요한 규칙은 이미 그 안에 있다**:

```python
if result.verdict is Verdict.PASS:
    if not result.evidence:
        errors.append({"code": "MISSING_EVIDENCE",
                       "detail": "PASS는 evidence 필수 (근거 없는 판정 폐기)"})
```

**이 한 줄이 지적 #5를 정확히 잡는다.** 필요한 것은 레지스트리 등록도, 규칙
재구현도 아니라 `validate_result(result, registry=...)` **선택 인자 하나**다
(기본값은 현재 전역). 실험이 자기 레지스트리를 공급하고, 도메인 레지스트리는
오염되지 않는다. `conceptgate/cg_obligations.py`는 어느 동결 표면 목록에도 없으므로
qualification 비용도 없다. 다만 저장소 전역 코어이므로 **음성 테스트 동반이
게이트로 강제된다**(`test_guard_negative_coverage.py`).

## 4. 의존성 분석 — 결론: EXECUTION 표면 편집 0, qualification 재실행 0

| 파일 | 표면 | 이번 라운드에서 |
|---|---|---|
| `reviewer_runner.py` | AUDIT | 편집 (#1 #2 #2a #3) |
| `run_pipeline.py` | AUDIT | 편집 (#4 #5 #6 #8) |
| `_receipt.py` | AUDIT | 편집 (#1, HMAC 추가) |
| `apply_safety_audit.py` | AUDIT | 편집 (#1 소비처) |
| `safety_audit_reviewer_assignment.json` | AUDIT | 편집 (#7) |
| `test_reviewer_isolation.py` / `test_e2e_acceptance.py` | AUDIT | 편집 |
| `_providers.py` | **EXECUTION** | **import만** (`seatbelt_profile_v2`) |
| `run_live_phase_c.py` | **EXECUTION** | **import만** (기존 v1 import는 제거) |
| `_evaluator.py` | **EXECUTION** | 무변경 |
| `conceptgate/cg_obligations.py` | 표면 아님 | `validate_result`에 선택 인자 1개 |

**EXECUTION 41개 파일 중 편집 대상 0.** 따라서:

- red-team 2건 **재실행 불필요**
- qualification 2건 **재실행 불필요.** `doctor`가 보고하는 stale 2종은 이번 수정과
  무관한 별개 사유다 — 기존 qualification artifact가 `surface-v2`로 만들어졌고
  authorization이 `surface-v3`를 가리키기 때문이며, 그것은 새 config로 다시 돌려야
  풀린다(handoff §5 단계 4). 이번 라운드가 그것을 더 낡게 만들지는 않는다.
- `closure` 재실행 **필요** (AUDIT 파일 해시가 바뀌므로 closure receipt가 낡는다)

이 결론이 실행 순서를 결정한다. C1을 따르지 않으면 이 표가 무너진다.

### 순환·선후 관계

```
_receipt.py (HMAC)          ← 아무것도 의존하지 않음. 가장 먼저.
    ↓
reviewer_runner.py (#1 서명, #2 v2, #2a probe 비공허성)
    ↓
apply_safety_audit.py (#1 검증 소비처)
    ↓
run_pipeline.py (#6 closure 대칭 검증, #8 release receipt, #5 obligation 3분할)
    ↓
closure 재실행 → e2e --release → release receipt 최초 생성

#4(--primary fail-closed)와 #7(assignment 문서)은 위 사슬과 독립 — 먼저 내도 된다.
#3(실제 reviewer adapter)은 위 전부가 선다는 전제에서만 의미가 있다. 마지막.
```

**#4를 가장 먼저 낸다.** 지금 `--primary`는 "32-cell run"이라 안내하면서 실제
provider를 부르지 않는다. 남겨두면 다른 세션이 그것을 primary로 오인해 실행하고
합성 결과를 본 실행으로 기록할 수 있다. 이건 코드 품질이 아니라 **결과 오염
경로**이므로, 큰 수정을 기다릴 이유가 없다.

## 5. 검증 설계 — 각 수정은 먼저 빨갛게

TDD 규칙대로 실패하는 검사를 먼저 만든다. **핵심은 "고쳤다"가 아니라 "고치기 전에
빨갛고, 고친 뒤 초록이며, 되돌리면 다시 빨갛다"를 셋 다 관측하는 것이다** — 세
번째를 안 보면 테스트가 코드와 무관할 수 있다.

| # | 먼저 빨갛게 만들 검사 | 통과 기준 |
|---|---|---|
| 1 | `produced_by`를 채우고 공개 함수로 `receipt_sha256`을 재계산한 위조 receipt가 PASS를 받으면 **실패** | HMAC 부재 → `ReviewerRunnerError`. 기존 약한 위조 테스트(`produced_by` 생략)는 **유지**하고 강한 것을 추가 |
| 2 | 프로파일 문자열에 `home_leak_denies()`의 각 경로가 없으면 **실패** | reviewer 프로파일 = `seatbelt_profile_v2` 산출과 바이트 동일 |
| 2a | **각 금지 probe가 `(allow default)` 프로파일에서 `reachable=True`가 아니면 실패** | probe 대상은 전부 **파일**. 통제 probe가 도달 불가면 그 probe는 **BLOCKED**(ok 아님) |
| 2a′ | v1 프로파일로 probe를 돌렸을 때 `host_transcripts`가 `ok`로 나오면 **실패** | v1 대조군이 실제로 LEAK를 보고해야 v2 통과가 의미를 갖는다 |
| 3 | reviewer command 없이 label artifact가 생기면 **실패** | command 실행 → stdout JSON schema 검증 → label artifact. `command=None`은 probe-only임을 **CLI가 명시** |
| 4 | `e2e --primary`가 provider 없이 0을 반환하면 **실패** | `BLOCKED: primary mode is not implemented; no attempt was claimed`, exit 2 |
| 5 | `current_run`이 BLOCKED인데 overall이 pass면 **실패** | declared/proof/current-run 3분할. proof는 **artifact에서 읽는다**. evidence 없는 PASS는 `MISSING_EVIDENCE` |
| 6 | `{"frozen_surface_hashes": ...}` 최소 JSON이 valid closure로 받아들여지면 **실패** | `kind`·파일명 digest·digest 재계산·`steps`·artifact 집합·artifact 현재 SHA-256 전부 대조 |
| 7 | assignment 문서가 launcher 부재를 주장하면 **실패**(문자열 검사) | 문서와 구현이 같은 것을 말함 |
| 8 | release 성공 후 `results/`에 release receipt가 없으면 **실패** | git commit·python·os·sandbox 가용성·exit·closure digest·pytest 요약 기록 |
| 9 | bundle 위치가 프로파일 deny 집합과 교차하는데 BLOCKED로 넘어가면 **실패** | 교차 시 `ReviewerRunnerError`. CLI와 E2E가 **같은** bundle 위치 결정 함수를 호출 |

### #2a의 설계 — 공허하지 않음을 기제로 강제한다

probe를 고치는 것으로 끝내면 다음에 또 디렉터리를 넣는다. **probe 목록 자체를
검증한다**:

```
각 금지 target t 에 대해
    control = _reachable((allow default), t)      ← deny 0건
    if not control:  probe t 는 BLOCKED           ← "ok"로 세지 않는다
    actual  = _reachable(reviewer_profile, t)
    LEAK if actual else ok
```

통제 probe는 sandbox를 측정하지 않는다 — **probe가 무언가를 측정할 수 있는지**를
측정한다. 이것이 `assert_*` 가드에 음성 테스트를 요구하는 것과 같은 규율이며,
같은 이유로 규율이 아니라 코드에 둔다.

### #1의 위협 모형 — 무엇을 막고 무엇을 못 막는지 먼저 쓴다

순수 해시 방식은 원리상 위조 가능하다(공개 함수 + 공개 입력). 인증에는 비밀이나
관측이 필요하다. 이 감사의 실제 위협은 두 개다:

1. **reviewer** — packet-only sandbox에 갇힌 agent. 저장소를 읽을 수 없다.
2. **손으로 그럴듯한 JSON을 쓰는 미래의 나** — 이번 라운드가 잡은 그 실패.

reviewer가 도달할 수 없는 경로의 host-only key로 HMAC하면 **둘 다** 막힌다.
막지 못하는 것: host 파일시스템 접근 권한을 가진 주체. **receipt 문서와
docstring에 그 한계를 명시하고, 그 이상을 주장하지 않는다.** `produced_by`
문자열은 아무것도 증명하지 않으므로 제거한다.

key는 커밋하지 않는다(`audit_workspace/` 하위, 0600, gitignore 확인 필요 —
현재 `git check-ignore`가 무반응이므로 **추가해야 한다**).

### 환경 표기

리뷰어 환경 246 passed / 10 failed, `--release` exit 1(isolation 2건 BLOCKED).
이 환경 256 passed / 2 skipped, `--release` exit 0. **리뷰어의 지적이 맞다** —
exit 0은 이 환경의 성질이고 커밋의 이식 가능한 성질이 아니다. #8이 그것을
artifact에 기록해 다음 세션이 재판정 없이 구별할 수 있게 만든다. 그때까지 모든
수치는 `N (이 환경)`으로 쓴다.

## 6. 실행 순서

```
0. #4  --primary fail-closed          ← 결과 오염 경로. 가장 먼저, 가장 작다
1. #7  assignment 문서 정정            ← 독립, 1줄
2. #1  _receipt HMAC + reviewer_runner 서명 + apply_safety_audit 검증
3. #2  v2 프로파일 import 교체          ← C1: AUDIT-only
4. #2a probe 비공허성 통제 + 대상을 파일로
4b. #9  bundle 위치 결정을 한 곳으로, deny 교차 시 거부  ← #2a와 같은 파일, 같은 커밋
5. #6  closure 검증기를 생성기와 대칭으로
6. #8  release receipt
7. #5  obligation 3분할 (+ cg_obligations validate_result seam, 음성 테스트 동반)
8. closure 재실행 → e2e --release → release receipt 최초 기록
9. #3  실제 reviewer adapter
10. 1 case × 1 arm live canary
```

**live canary는 리뷰어 판정대로 지금 실행하지 않는다.** 다만 리뷰어가 "먼저
수정할 4개"로 든 것에 **#2a를 추가한다** — probe가 공허한 상태로 v2로 바꾸면
"v2를 쓴다"는 주장은 참이 되지만 그 주장을 **확인한 적은 여전히 없다.** #2만
고치고 canary로 가면 이번 라운드가 잡은 것을 다시 놓친다.

커밋은 `EXPERIMENT_METHODOLOGY.md` §1대로 나눈다: (0·1) 즉시 차단, (2~7) 구현,
(8) 결과 artifact, (9~) 별도.

## 7. 미룬다 — 그리고 미루는 이유

- `metrics.py` / `experiment_data.py` / `sandbox.py` 추출 — EXECUTION 표면을
  건드려 qualification을 무효화한다. primary 이후.
- `_provenance` / `apply_safety_audit` import 비용 정리 — 성능 무관.
- `PROVEN_BY`의 mutation 결과를 artifact로 옮기는 것은 #5에 **포함**한다(미룸 아님).
  이것을 미루면 #5는 문자열을 다른 문자열로 바꾼 것에 그친다.

## 8. 낮춰야 할 내 주장

- **"위조 receipt 모두 거부"** — 거짓. `produced_by`를 생략한 약한 위조만 거부했다.
- **"Seatbelt v2 재사용"**(`reviewer_runner.py` docstring) — v1이었다.
- **"프로파일 문자열은 주장이고 probe가 증거다"** — 같은 모듈에서 probe 4개 중
  2개가 sandbox를 측정하지 않았다. probe도 주장이었다.
- **"obligations 10/10 PASS"** — 실행 증거가 아니라 소스 상수. 같은 실행에서
  `reviewer.isolation.enforced: PASS`와 `FAIL: reviewer isolation BLOCKED`가
  동시에 출력될 수 있다.
- **"e2e --release exit 0"** — 이 환경에서만. 커밋의 성질이 아니다.
