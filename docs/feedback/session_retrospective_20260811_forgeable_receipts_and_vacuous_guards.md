# 세션 회고 — 위조 가능한 receipt와 공허한 가드 (21·21b·21c라운드)

작성 2026-08-11. 범위: 커밋 `bd64c21`(세션 시작) ~ `ddc3980`.
직전 로그 [`session_retrospective_20260811_pipeline_gates_and_provenance.md`](session_retrospective_20260811_pipeline_gates_and_provenance.md)가
**I112**에서 끝났고, Codex 로그는 별도 namespace(`C-I01~C-I09`)를 쓴다.
따라서 이 로그는 **I113부터** 이어진다.

이 세션은 독립 검토 3회(21 → 21b → 21c)를 받았다. 각 라운드는 **직전 라운드가
만든 방어를 반증**했다. 그 사실 자체가 이 회고의 주제다.

---

## (1) 신규 이슈 I113~I147

### A. 21라운드 — 서명 없는 receipt (리뷰어 8건 + 내가 찾은 2건)

| ID | 이슈 |
|---|---|
| I113 | **isolation receipt가 위조 가능했다.** `produced_by` 문자열 + 공개 `receipt_sha256`. 필드를 채우고 **같은 공개 함수**를 부르면 launcher를 한 번도 실행하지 않은 dict가 `PASS`로 검증됐다 — 재현 |
| I114 | **closure receipt도 위조 가능했다.** `{"frozen_surface_hashes": {...}}` 한 키가 valid closure였다. 생성기는 `kind`·digest·파일명 digest·`steps`·artifact 해시를 **쓰고** 검증기는 한 필드만 **읽었다** |
| I115 | `reviewer_runner`가 docstring에 Seatbelt **v2**를 인용하고 코드는 **v1**을 불렀다. v1은 repo와 control 두 subtree만 deny한다 |
| I116 | launcher가 `subprocess.run(...)`을 부르고 **결과를 버렸다.** release E2E는 command를 아예 넘기지 않았고, 그 안의 "reviewer label"은 E2E가 **답안 파일에서** 만든 것이었다 |
| I117 | `e2e --primary`가 "the 32-cell run"이라 안내하며 `_synthetic_primary()`를 돌렸다. release와 primary의 `RunSpec` **필드값이 동일**했다 — 두 모드가 이름만 다른 같은 프로그램 |
| I118 | 의무 10/10 PASS가 **소스 상수**였다. 한 실행이 `reviewer.isolation.enforced: PASS`와 `FAIL: reviewer isolation BLOCKED`를 **동시에** 출력했다 |
| I119 | 동결된 assignment 문서가 launcher 구현·closure 이후에도 "no sandboxed launcher exists yet"을 주장했다 |
| I120 | release 성공이 **artifact를 남기지 않았다.** 이 환경 exit 0, 리뷰어 환경 exit 1(isolation 2건 BLOCKED) — 어느 쪽도 기록되지 않아 사후 구별 불가 |
| **I121** | **금지 probe 4개 중 2개가 공허했다**(리뷰어 미지적, 내가 검증 중 발견). `results_dir`·`host_transcripts`가 **디렉터리**이고 `/bin/cat`은 디렉터리에 대해 sandbox와 무관하게 실패한다 → **deny가 0건인 `(allow default)`에서도 `ok`로 보고**됐다 |
| **I122** | **CLI 기본 경로가 상시 BLOCKED**(리뷰어 미지적). `main()`의 기본 out_dir이 프로파일이 deny하는 `HERE` 안이라 allowed probe가 항상 실패 → 문서가 안내하는 CLI는 **어떤 환경에서도 PASS를 낼 수 없었다** |

### B. 21라운드 구현 중 내가 만든 결함

| ID | 이슈 |
|---|---|
| I123 | `write_release_receipt`를 `run_pipeline()` 안에서 불러, **acceptance suite가 실행마다 커밋된 append-only `results/`에 파일을 남겼다.** receipt가 git commit·dirty를 기록하므로 clean/dirty가 **다른 문서**를 만들어, 하나를 커밋하면 다음 실행이 또 하나를 쓴다(무한) |
| I124 | `reviewer.labels.from-launcher` mutation이 **너무 넓었다**. `MENTION`→`UNRELATED`가 qualification 답안까지 바꿔 "자격 미달"이라는 **다른 의무의 신호**를 냈다 |
| I125 | stage 8이 adjudicator의 `SystemExit`에 죽어, **이름 붙일 수 있는 이유로 실패한 실행이 크래시로 보였다** |
| I126 | stage 6/7이 `labels[1]`을 참조해, launcher가 아무것도 못 만들면 `IndexError`로 죽었다 — mutation이 작동했는데 크래시로 보였다 |
| I127 | 도달성 결과를 **파이프의 exit code**(`tail`)로 읽고 "exit 0, orphans 0"이라 보고했다. 게다가 그 0은 `--ref` 범위의 값이고 전역은 302였다 |

### C. 21b라운드 — 감사 경로가 launcher를 우회 (8건)

| ID | 이슈 |
|---|---|
| I128 | **실제 감사 경로가 receipt를 우회했다.** `apply_safety_audit.py`에 `isolation`이라는 **문자열조차 없었다.** 검증하는 곳은 release E2E와 `doctor`뿐이고, handoff가 사람에게 안내하는 수동 절차로 HMAC을 **통째로 우회**할 수 있었다 |
| I129 | 공개 CLI가 probe-only(`run_reviewer(bundled, reviewer_id)`)여서, 문서가 안내하는 진입점으로 reviewer를 **돌릴 수 없었다** |
| I130 | `doctor`가 receipt에 **없는** `packet_file` 필드로 경로를 지어내 **정상 경로에서 `FileNotFoundError`로 죽었다.** assignment가 `UNASSIGNED`라 그 분기는 **한 번도 실행된 적이 없었다** |
| I131 | release가 PASS의 근거를 폐기했다. `launcher_receipts`가 지역 변수뿐이고 probe 결과·profile 해시·output 해시가 최종 artifact에 없었다 |
| I132 | 12/12가 **현재 mutation 실행 결과가 아니다**(증거의 존재만 본다). docstring이 그 한계를 적었으나 release receipt는 `pass`만 남겼다 |
| I133 | `reviewer_command_sha256`이 **argv만** 해시했다. 같은 경로의 스크립트를 갈아치워도 값이 같다 |
| I134 | stdout schema가 보고보다 얕았다(두 객체의 존재만, `additionalProperties`·값 규칙 없음) |
| I135 | **진입 문서에 두 현재 상태가 있었다.** §1과 PREREGISTRATION이 `10/10` / `offline exit 0`인데 §3b가 뒤에서 고쳐 놓았다. §1이 먼저 읽힌다 |

### D. 21b라운드 구현 중 내가 만든 결함

| ID | 이슈 |
|---|---|
| I136 | isolation 게이트를 per-label 검사 **앞**에 두자 stage 6의 자격 미달 음성이 먼저 걸려 `refused=False`가 됐다 — **새 게이트가 기존 게이트의 커버리지를 조용히 없앴다** |
| I137 | `declared_by_id[...]`가 assignment 멤버십 mutation 하에서 `KeyError`를 내, **그 mutation의 신호를 크래시로 바꿨다**(I136과 같은 형태의 두 번째) |
| I138 | 내 CLI 테스트가 다시 `results/`에 receipt를 남겼다 — **I123과 같은 실패의 두 번째** |
| I139 | python 스크립트의 단언이 걸렸는데 `&&`로 묶지 않아 `git add`/`commit`이 그대로 실행됐다. **편집 없이 커밋**됐고 다음 커밋에서 정정 |

### E. 21c라운드 — 공허한 문서 가드 (5건)

| ID | 이슈 |
|---|---|
| **I140** | **F7을 고치며 만든 회귀 테스트가 공허했다.** 과거 문자열 3개의 부재만 보고, `n = len(DECLARED_OBLIGATIONS)`는 **오류 메시지에만** 쓰였다. docstring은 "선언된 수와 대조한다"고 적혀 있었다. 실측: 의무 수를 99로 바꾸고 돌리면 **1 passed** |
| I141 | 운영 절차가 label 수동 제출 + `--isolation-receipt` 없는 adjudicator 호출을 안내했다. `kind: agent`면 **코드가 그 절차를 거부한다** |
| I142 | handoff가 제거된 `produced_by` + 공개 `receipt_sha256`을 **현행처럼** 설명했다 |
| I143 | PREREGISTRATION이 release E2E를 **probe-only처럼** 설명했다(stub reviewer를 실행하기 시작한 뒤) |
| I144 | `status != "DENIED"`가 BLOCKED probe를 `reached`에 넣어, 통제 실패 host에서 **"reviewer가 answer key에 도달했다"**고 출력했다 — 도달한 것도 측정된 것도 없었다 |
| I145 | execution identity를 **실행 뒤에** 계산했다(실행 481행, identity 489행) → 실행 후 바이트를 증언할 수 있다. PATH 실행 파일(`claude`·`codex`·`python3`) 미해시. receipt는 opaque digest만 담아 **재현 불가** |
| I146 | release receipt의 `obligations: {name: "pass"}`가 **"이 release에서 mutation 12종이 통과"**로 읽힌다 |
| I147 | `sandbox_available`이 **바이너리 존재만** 기록해, 같은 커밋의 `/private/tmp` clean clone exit 1을 설명하지 못했다 |

**신규 35건. 그중 내가 구현 중 만든 것이 9건**(I123~I127, I136~I139), **리뷰어가
놓쳤고 내가 찾은 것이 2건**(I121, I122).

---

## (2) 재현 횟수가 증가한 반복 이슈

직전 로그의 누적값을 기준으로 한다.

| 패턴 | 이전 | 이번 증가 | 누적 |
|---|---|---|---|
| **P-문서가계약을가르침** | 4 | I115, I119, I132, I135, I140, I141, I142, I143 | **12** |
| **P-자기보고과장** | 10 | I120, I127, "남은 것은 canary 하나", "F7 완료", "F5 완료", "294 passed"(무한정) | **16** |
| **P-자기수정회귀** | 10 | I136, I137, I138, I140 | **14** |
| **P-계측기미검증** | 8 | I121, I130, I145 | **11** |
| **P-헬퍼는보고배선은안봄** | 8 | I128, I129 | **10** |
| **P1**(참이나 불필요한 명제 검사) | 22 | I114, I121, I134, I140 | **26** |
| **P-검증이증거를쓴다** | 1 (I86) | I123, I138 | **3** |
| **P-게이트가게이트를가림** (신규) | — | I136, I137 | **2** |

`CLAUDE.md`가 별도로 세는 **공허한 가드**(`assert_*` 계열 + 동형) 카운트는
**7 → 9**로 올랐다: I121(probe 2/4), I140(문서 가드).

### 이 세션의 지배 패턴은 P-문서가계약을가르침이다 (4 → 12)

8건이 한 세션에서 났고, **형태가 셋으로 갈린다**:

1. **docstring이 코드보다 강한 주장을 한다** — I115(v2 인용/v1 호출),
   I140("선언된 수와 대조한다"/오류 메시지에만 씀)
2. **동결 문서가 구현과 반대를 말한다** — I119, I142, I143
3. **한 문서 안에 두 현재 상태가 있다** — I135, I141

3번이 가장 위험하다. 이 실험은 **무맥락 agent가 `docs/HANDOFF.md`만 보고
재개할 수 있는지**를 측정하므로, 문서가 코드와 모순되면 **subject 실패가 검색
실패인지 문서 모순인지 구별되지 않는다.** 위생 문제가 아니라 **측정 타당성**
문제다.

### P-자기수정회귀가 14 — 그리고 I140이 최악의 형태다

I140은 **P-문서가계약을가르침(I135)을 고치기 위해 만든 가드가 그 자신
P-문서가계약을가르침이면서 P1이었다.** 두 패턴이 한 함수 안에서 겹쳤고, 고치려던
바로 그 실패였다.

---

## (3)(4) 해결 근거와 해결 유무

| ID / 패턴 | 해결 근거(기제) | 상태 |
|---|---|---|
| I113 | `_receipt.sign/verify` HMAC + host-only key. 재현 스크립트가 이제 거부됨 | **해결** |
| I114 | `closure_receipt_defects()`가 생성기가 쓰는 **모든** 필드를 대조. 생성기가 자기 산출물을 같은 함수로 검증 | **해결** |
| I115 | `_providers.seatbelt_profile_v2` import + **v1 누출/v2 차단 대조 테스트** | **해결** |
| I116 | `_run_reviewer_process` + `_label_artifact` + mutation `reviewer.labels.from-launcher` | **해결** |
| I117 | `refuse_primary()` exit 2, `RunSpec.for_mode("primary")`가 raise. 테스트 2건 | **해결** |
| I118 | declared / demonstrated / current-run 3분할, current-run 우선. `certify(registry=...)`가 evidence 없는 PASS를 FAIL로 | **해결** |
| I119 I142 I143 | positive-contract 문서 테스트 4종(파싱 대조 + 토큰 요구 + 제거된 방식 금지) | **해결** |
| I120 I131 I147 | release receipt + `isolation.probe_states` + `allowed_probe_passed` | **해결** |
| I121 | `PERMISSIVE_PROFILE` 통제 probe. 통제 실패 = **BLOCKED**(ok 아님), 하나라도 BLOCKED면 실행 전체가 PASS 아님 | **해결** |
| I122 | `reviewer_workspace` / `assert_reachable_workspace` 단일 결정 + deny 교차 시 거부 + **직접 음성 테스트**(저장소 전역 가드 게이트가 요구) | **해결** |
| I123 I138 | `CG_RELEASE_RECEIPT_DIR` / `CG_ISOLATION_RECEIPT_DIR` 리다이렉트 + **양방향** 회귀 테스트(suite가 안 쓴다 + 리다이렉트가 기제를 끄지 않는다) | **해결(부분)** — §7 L5 참조 |
| I124 | mutation을 공백 한 칸으로 좁힘. JSON 유효·label·qualification 불변, **바이트만 변경** | **해결** |
| I125 I126 | stage 8이 `SystemExit`을 보고, stage 6/7이 launcher와 무관한 companion label 사용 | **해결** |
| I127 | 파이프 없이 측정하는 습관 + handoff §11에 `--ref` 의미와 파이프 함정 기록 | **부분** — §7 L6 |
| I128 | `_require_isolation`이 adjudicator 안에서 요구. CLI `--isolation-receipt`. stage 7c + mutation `audit.isolation.required` | **해결** |
| I129 | CLI `--command` / `--labels-out` + 테스트 | **해결** |
| I130 | `authenticate_isolation_receipt` / `verify_isolation_receipt` 분리. **분기에 도달하는** 복사 트리 테스트 2건 | **해결** |
| I132 I146 | `declared_proofs_present` + `what_this_is_not` | **명칭 해결, 결속은 미해결**(F4, 순환) |
| I133 I145 | `execution_manifest()` — `shutil.which` 해석, **실행 전** 계산, 실행 후 재대조, 파일 목록·한계 기록 | **해결** |
| I134 | — | **미해결(의도적 연기)**. 실제 CLI 출력을 보지 않고 schema를 좁히면 무엇을 좁혀야 하는지 모른다 |
| I135 I140 I141 | 문서에서 **숫자를 파싱해** 코드와 대조, offline exit는 **실제 실행**과 대조. **오염 시험으로 음성성 확인**(99 → 실패) | **해결** |
| I136 I137 | mutation 게이트가 둘 다 잡았다. `_require_isolation`을 per-label 검사 **뒤**로, `.get`으로 조회 | **해결(기제는 기존)** — §7 L4 |
| I139 | — | **미해결**. 습관에 의존 중. §7 L7 |
| I144 | `reached`(=`reachable`)와 `unmeasured`(=BLOCKED) 분리 + 테스트 | **해결** |

**35건 중 해결 28 / 부분 3 / 미해결 4**(I134·I139·F4 결속·L5 일반화).

---

## (5) 반복 O + 해결근거 O 인 이슈의 문제 정의

### 문제 1 — P-문서가계약을가르침(12): 산문은 코드와 **자동으로** 갈라진다

**정의**: 문서·주석·docstring이 만드는 주장 `D`와 코드가 참으로 만드는 명제 `C`가
있을 때, **`D`를 유지하는 힘이 없으면 `C`가 바뀔 때 `D`는 그대로 남는다.** 이것은
부주의가 아니라 **비대칭**이다 — 코드 변경은 테스트가 막지만 문서 변경은 아무도
막지 않는다.

이 세션이 준 새 사실: `D`가 **자기 자신을 검사하는 가드의 docstring**일 때가
가장 위험하다(I140). 그 문서를 읽는 사람은 "검사되고 있다"고 믿고 **더 이상
확인하지 않는다.**

### 문제 2 — P1 공허한 가드(26 / CLAUDE.md 기준 9): 가드의 **존재**는 증거가 아니다

**정의**: 가드 `g`가 참으로 만드는 명제 `P(g)`와 필요한 명제 `Q`가 있을 때,
`P(g) ⊂ Q`이면 `g`는 통과하면서 `Q`를 위반하는 입력이 존재한다. 긍정 입력만으로는
`P(g) = Q`인지 `P(g) ⊊ Q`인지 **관측 채널이 없다**.

이 세션의 세 형태:
- **부재만 검사**(I140) — 블랙리스트 3개. `99/99`는 목록에 없다
- **측정 불가를 통과로 읽음**(I121) — `rc != 0`을 "차단됨"으로
- **한 필드만 대조**(I114) — 생성기가 쓴 나머지는 아무도 안 읽는다

### 문제 3 — P-게이트가게이트를가림(신규, 2): 방어를 **추가**하는 것이 방어를 **줄인다**

**정의**: 게이트 `A`(기존)와 `B`(신규)가 같은 입력 경로에 있고 `B`가 먼저
발동하면, `A`의 음성 테스트가 `A`를 더 이상 관측하지 않는다. **`A`의 커버리지가
코드 변경 없이 사라진다.** I137은 더 나쁘다 — `B`가 예외를 던져 `A`의 mutation
신호가 **크래시로 대체**됐다.

이것이 새로운 이유: 이전 패턴들은 "방어가 없다"였고 이것은 **"방어를 늘렸는데
관측이 줄었다"**다.

### 문제 4 — P-검증이증거를쓴다(3): 검증 행위가 증거 디렉터리를 변경한다

**정의**: 테스트가 `results/`에 쓰면 (a) append-only 규율을 위반하고 (b) 실행마다
상태가 달라져 **다음 실행의 입력이 이전 실행의 출력**이 된다. I123은 그 위에
git commit/dirty를 담아 **수렴하지 않는 루프**를 만들었다.

### 문제 5 — P-자기보고과장(16): 완료 판정이 관측보다 강하다

**정의**: 보고 `R`이 관측 `O`보다 강한 주장을 할 때, 다음 세션이 `R`을 근거로
행동하고 `O`를 다시 만들지 않는다. 이 세션의 형태는 **범위 누락**이 지배적이다 —
"F7 완료"(기제가 공허), "F5 완료"(부분), "orphans 0"(`--ref` 범위), "294
passed"(host 권한 환경).

---

## (6) 해결 유무 판단에 쓴 가설과 검증 방식

### 이 세션이 추가한 방법 — **오염 시험(poison test)**

> **가드를 만들면, 그 가드를 통과시키는 잘못된 입력을 실제로 만들어 본다.**

I140은 "테스트가 없다"가 아니라 **"테스트가 있고 공허하다"**였고, 그것을 확인한
방법은 **문서를 실제로 오염시켜 pytest를 돌린 것**이다:

```
handoff의 의무 수 12 → 99      pytest -k entry_block   →  1 passed   ← 공허
(수정 후) 의무 수 12 → 99       pytest -k operating_docs →  1 failed  ← 유효
(수정 후) offline exit 2 → 0    pytest -k operating_docs →  1 failed  ← 유효
```

**"음성 테스트를 썼다"로는 부족하다. 음성 테스트가 음성인지를 확인해야 한다.**
이 저장소에 이미 선례가 있었다 — `test_guard_negative_coverage.py:238`
`test_scanner_flags_a_guard_whose_test_only_feeds_valid_input`는 **스캐너 자신을
known-bad/known-good으로 검증한다.** 나는 그 선례를 알고도 내 새 가드에는 적용하지
않았다.

### 도달하는 상태를 만들어야 한다 — I130이 가르친 것

`doctor`의 agent 분기는 assignment가 `UNASSIGNED`라 **한 번도 실행되지 않았고**,
그래서 존재하지 않는 필드를 참조하는 코드가 네 라운드 살아남았다. 함수를 직접
부르는 테스트는 이것을 재현하지 못한다.

**규칙**: 가드된 분기의 테스트는 **그 분기에 도달하는 상태를 만들어야 한다**
(복사 트리 + `ASSIGNED` + `kind: agent` + 실제 서명 receipt).

### mutation의 applied-check를 한 층 더 — I124가 가르친 것

기존 규율: 소스가 안 바뀌면 HARNESS DEFECT. 이 세션이 추가: **mutation이 한 가지만
분리해야 한다.** `MENTION`→`UNRELATED`는 소스도 바뀌고 신호도 났지만 **다른 의무의
신호**였다. 좁힌 형태(공백 한 칸)는 JSON 유효·label·qualification 불변이고 **바이트만**
바뀐다.

### 통제 probe — I121이 가르친 것

측정 도구는 **자신이 무언가를 측정할 수 있는지**를 먼저 증명해야 한다. deny가
0건인 프로파일에서 도달 불가한 probe는 sandbox에 대해 아무것도 말하지 못한다.
그리고 **v1 누출 / v2 차단 대조**가 있어야 "v2를 쓴다"가 반증 가능해진다.

### 검증하지 않은 것 — 정직하게

- **12/12가 이 실행의 mutation 결과인지**: 아니다. `demonstrated`는 증거의 **존재**만
  본다. 결속은 순환(§7 L4 주석) 때문에 미해결이며 필드명을
  `declared_proofs_present`로 낮췄다.
- **다른 host에서의 release**: 리뷰어가 `/private/tmp` clean clone에서 exit 1을
  재현했다. 이 환경의 exit 0은 **이 환경의 성질**이다.
- **실제 provider 호출**: 한 번도 하지 않았다. stub reviewer는 배관 확인이고
  판정에 대해 아무것도 말하지 않는다.

---

## (7) 문제의 해결 방법 — 구체적으로

사용자 질문: **"특정 상황에서 linter로 warning messages라도 뜨게 해야 하나"**

**답: 세 패턴은 linter/AST로 잡히고, 두 패턴은 런타임 기제가 맞고, 나머지는
의미론이라 잡히지 않는다.** 잡히지 않는 것에 lint를 억지로 붙이면 이 저장소가
싫어하는 것(초록인데 아무것도 증명하지 않는 게이트)이 하나 더 생긴다.

**모든 새 스캐너는 `test_guard_negative_coverage.py:238`의 선례대로 자기
자신에 대한 known-bad / known-good 테스트를 함께 낸다.** 그것이 없으면 스캐너가
I140이 된다.

### L1 — **판정에 쓰이지 않는 계산값** (I140을 직접 잡는다) · AST · 높은 가치

I140의 AST 형태는 정확하다:

```python
n = len(rp.DECLARED_OBLIGATIONS)      # Assign, 함수 지역
...
assert cond, f"... {n}"               # Assert.msg 안에서만 사용
```

**규칙**: `test_*.py`의 테스트 함수 안에서 지역 이름이 **호출식으로 대입**되고,
이후 모든 사용이 `ast.Assert`의 **`msg`** 하위 트리 안에만 있으면 실패시킨다.

```
FAIL: test_the_operating_docs_...: `n`을 계산했으나 판정에 쓰지 않는다
      (사용처 전부가 assert 메시지 안). 계산한 값으로 비교하라.
```

**프로토타입으로 실측했다**(제안이 아니다):

```
known-bad  (I140 형태)                    → [('test_thing', 'n')]   검출
known-good (수정본 `assert parse(text)==n`) → []                     통과
저장소 전역 test_*.py 스캔                 → total flagged: 0        오탐 0
```

- **왜 좁은가**: `msg`에만 쓰인 값은 정의상 판정에 기여하지 않는다. 전역 스캔
  오탐 0이므로 **경고가 아니라 실패로 넣어도 된다.**
- **구현 위치**: `test_guard_negative_coverage.py`와 같은 층(저장소 루트 게이트).
  core pytest가 이미 수집한다.
- **자기 검증**: known-bad → 검출, known-good → 통과 (위 실측).

### L2 — **부재만 검사하는 테스트** (블랙리스트 탐지) · AST · 중간 가치

**규칙**: 테스트 함수의 `assert`가 **전부** 부정 멤버십(`x not in y`)이거나
`not ...`이면 경고한다.

```
WARN: test_...: 판정이 전부 "없음"이다. 블랙리스트는 목록에 없는 값을 통과시킨다.
      존재/일치 검사를 하나 이상 추가하라.
```

- **경고이지 실패가 아니다**: "제거된 방식이 문서에 없다"처럼 부재가 **정확히**
  필요한 명제인 경우가 실재한다(I142의 가드). 그때는 `# blacklist-ok: <이유>`
  주석으로 억제하고, 그 주석이 **이유를 강제**한다.

### L3 — **문서 수치 대조를 일반화** (I135·I140의 재발 방지) · 이미 구현, 확장

지금은 의무 수와 offline exit만 본다. 확장 대상은 **코드가 선언하는 값**뿐이다:

| 문서의 주장 | 코드의 정본 |
|---|---|
| 의무 N/N | `len(DECLARED_OBLIGATIONS)` ✅ 구현 |
| `e2e --offline exit N` | 실제 실행 ✅ 구현 |
| calibration `8/8`·`60/60` | `run_calibration` 기대값 |
| `expected_cells` (32칸) | `safety_audit_spec.json` |
| `max_attempts` | `PRIMARY_AUTHORIZATION.json` |

**넣지 말 것**: 테스트 통과 수(환경 종속), 커밋 해시(즉시 낡음).

### L4 — **게이트가 게이트를 가림** — lint로 못 잡는다. mutation이 정본이다

I136·I137을 잡은 것은 **mutation 게이트**다(`expected_signal`이 안 나옴). lint는
"어느 게이트가 먼저 발동하는가"를 알 수 없다 — 실행 순서와 예외 흐름의 문제다.

**대신 규율을 하나 고정한다**(문서가 아니라 mutation 명세에):

> 새 per-label 게이트를 추가하면 **기존 게이트의 mutation을 먼저 돌려라.**
> `expected_signal`이 유지되지 않으면 새 게이트의 **위치**가 틀렸다.

이건 이미 자동이다 — `pytest test_e2e_acceptance.py`가 12종을 다 돌린다. 필요한
것은 "새 게이트를 넣었으면 그 suite를 돌린다"이고, 그건 core pytest가 강제한다.

**F4(mutation 결과 결속)를 닫으면 더 강해진다.** 지금은 순환 때문에 미해결:
mutation 하네스가 자기 workspace에서 `closure`와 release를 다시 돌리므로,
`closure`가 증거 artifact를 만들면 재귀하고 mutated workspace의 release는 증거
부재를 읽어 **모든 mutation이 엉뚱한 이유로 "검출됨"**이 된다. 설계 아이디어:
증거 생성을 `closure` **밖의 별도 lane**에 두고, 그 lane이 자기 실행을
`CG_IN_MUTATION` 유무로 구별한다.

### L5 — **검증이 증거를 쓴다** — lint보다 **런타임 fixture**가 맞다 · 높은 가치

I123·I138·I86은 **쓰는 방법이 매번 달랐다**(`write_text`, CLI `main()`,
subprocess). AST로 경로 표현식을 추적하면 오탐·미탐이 둘 다 난다.

**대신 `conftest.py`(19행, 픽스처 없음)에 세션 스코프 픽스처 하나**:

```python
@pytest.fixture(scope="session", autouse=True)
def results_dirs_are_read_only_during_tests():
    """테스트는 증거를 만들지 않는다. I86·I123·I138이 같은 실패의 3회다."""
    roots = sorted(Path(".").glob("experiments/*/results"))
    before = {r: {p.name: p.stat().st_mtime_ns for p in r.iterdir()}
              for r in roots}
    yield
    changed = {str(r): sorted(set(now) ^ set(before[r]))
               for r in roots
               if (now := {p.name: p.stat().st_mtime_ns for p in r.iterdir()})
               and (set(now) != set(before[r])
                    or any(now[k] != before[r][k] for k in before[r] if k in now))}
    assert not changed, f"테스트가 results/를 변경했다: {changed}"
```

**실측이 이 설계의 결함을 하나 잡았다.** 처음 쓴 판은 `st_mtime_ns`를
비교했고, 현재 트리에서 **FAIL**했다:

```
mtime 기준 : changed = ['redteam_provider_isolation.json']   → FAIL
내용 기준  : changed = none, added = none                    → PASS
```

`test_doctor_does_not_render_a_failed_redteam_as_ok`가 그 파일에 FAIL 상태를
주입한 뒤 `finally`에서 **바이트 동일하게 복원**한다. 정당한 테스트이고, mtime만
바뀐다. 따라서 **비교 기준은 `st_mtime_ns`가 아니라 내용 해시여야 한다** —
그러지 않으면 이 픽스처 자체가 오탐을 내는 게이트가 된다.

```python
snap = lambda r: {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in r.iterdir()}
```

- **쓰는 방법과 무관하게** 잡는다. subprocess도, CLI `main()`도 잡힌다.
- **선례**: I86 때 도입한 `--out-root`와 같은 목적이지만, 그때는 **호출자마다**
  걸었고 이번엔 **경계에 한 번** 건다.
- 주의: `closure`/`release`를 의도적으로 돌리는 테스트가 있으면 그 테스트가
  리다이렉트 환경변수를 세우도록 강제된다 — 지금 둘 다 이미 그렇게 한다.
- **이 실측 자체가 §6의 오염 시험이다**: 픽스처를 제안만 하지 않고 현재 트리에
  대고 돌려, 통과할 줄 알았던 것이 실패했고 그 이유가 설계 결함이었다.

### L6 — **파이프가 exit code를 먹는다**(I127) — 도구가 스스로 말하게

lint 불가(shell 습관). 대신 **도구가 최종 줄에 exit code를 찍는다**:

```
EXIT=1  (orphans=6, --fail-on=orphans)
```

`handoff_reachability.py`·`run_pipeline.py`·`run_gates.py` 세 곳. 파이프로 읽어도
보이고, `$?`를 잘못 읽어도 출력이 정정한다. **비용 3줄, 재발 차단 1건.**

### L7 — **단언 실패 후에도 커밋됨**(I139) — 셸이 아니라 도구로

`python3 - <<'PY' ... PY` 다음에 `git commit`을 **같은 명령줄에 이어 쓰지
않는다.** 그리고 반복 편집에는 헬퍼를 쓴다:

```python
def edit_once(path: Path, old: str, new: str) -> None:
    """정확히 1회 치환. 0회면 예외 — `str.replace`의 조용한 미적용을 막는다."""
    s = path.read_text(encoding="utf-8")
    n = s.count(old)
    if n != 1:
        raise AssertionError(f"{path.name}: {n}회 일치 (1회여야 한다)")
    path.write_text(s.replace(old, new), encoding="utf-8")
```

이 세션에서 그 단언 자체는 **제 일을 했다**(I140 정정 중 두 번 걸림). 실패한
것은 `&&` 하나다.

### L8 — 넣지 않을 것 (판단 근거를 남긴다)

- **"docstring이 코드보다 강한 주장을 하는가"** 일반 탐지 — 자연어 판정이다.
  L1·L3처럼 **기계가 대조할 수 있는 형태로 좁힐 때만** 가치가 있다.
- **schema 심화(I134)** — 실제 CLI 출력을 보기 전에 좁히면 무엇을 좁혀야 하는지
  모르고 좁힌다. canary 이후.
- **receipt 정본 포인터(F8)** — append-only와 긴장 관계이고 지금 항해를 막지
  않는다. handoff는 `_closure_receipt()`를 물어보는 명령으로 대체했다.

### 우선순위와 비용

| 순위 | 항목 | 비용 | 막는 것 |
|---|---|---|---|
| 1 | **L5** conftest 픽스처 | ~15행 + 자기 검증 | I86·I123·I138 계열 (누적 3) |
| 2 | **L1** 판정 미사용 계산값 | ~40행 + 자기 검증 | I140 계열 (P1 26의 한 형태) |
| 3 | **L6** `EXIT=` 출력 | 3행 | I127 |
| 4 | **L3** 문서 수치 대조 확장 | ~30행 | I135·I140 재발 |
| 5 | **L2** 블랙리스트 경고 | ~35행 + 억제 주석 규약 | 미래의 I140 |
| — | **L7** `edit_once` | ~8행 | I139 |

**1~3만 해도 이 세션 신규 35건 중 5건의 재발 경로가 기계로 막힌다.** 4~5는
canary 이후로 미뤄도 된다 — 지금 코드는 그 두 검사를 이미 통과한다.

**세 항목 모두 실측으로 근거가 있다**: L1은 오탐 0(전역 스캔), L5는 현재 트리에서
통과(단, 내용 해시 기준일 때만 — mtime 기준은 오탐), L6는 3줄. **미구현이다** —
이 회고는 근거를 남기고, 도입은 canary 다음 작업으로 남긴다. 지금 넣으면 canary
직전에 AUDIT 표면을 또 바꿔 closure를 다시 돌려야 하고, 그것이 이 세션이 네 번
반복한 일이다.

---

## 이 회고가 남기는 방법론적 사실

1. **세 라운드가 연속으로 직전 라운드의 방어를 반증했다.** 21이 20의 receipt를,
   21b가 21의 배선을, 21c가 21b의 문서 가드를. **방어를 추가하는 작업 자체가
   결함의 주요 원천**이며(내가 만든 9건), 그래서 리뷰가 아니라 **기제**가 필요하다.
2. **가장 위험한 문서는 가드의 docstring이다.** 읽는 사람이 "검사된다"고 믿고
   확인을 멈춘다. I140이 그것이었다.
3. **오염 시험이 없으면 음성 테스트도 주장이다.** 이 저장소는 스캐너에 대해
   이미 그것을 했고(`:238`), 나는 그 선례를 알고도 새 가드에 적용하지 않았다.
4. **방어를 늘리는 것이 관측을 줄일 수 있다**(P-게이트가게이트를가림, 신규).
   새 게이트를 넣으면 **기존 게이트의 mutation을 돌려 신호가 유지되는지** 본다.
5. **리뷰어가 놓치는 것이 있다.** I121·I122는 내가 검증 중에 찾았고, I121은 이
   라운드에서 가장 나쁜 결함이었다. **검토를 받는 것과 검증하는 것은 다르다.**

## 남은 것

- **live canary — 1 case × 1 arm 실제 provider 호출.** host 권한 환경에서.
- F3(manifest 확장) · **F4(mutation 결과 결속 — 순환 해소 설계 필요)** ·
  I134(schema) · F8(포인터) · 권한 lane 분리.
- 위 L5·L1·L6 (기제 3건).
