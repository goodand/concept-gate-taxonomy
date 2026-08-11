# 20라운드 — 검증 설계 · 의존성 분석 · 구현 계획

작성 2026-08-11. 대상 `1f12e2f`/`3f9c2f9`. 선행:
[`plan_round20_walking_skeleton_and_release_e2e.md`](plan_round20_walking_skeleton_and_release_e2e.md)
(검증 결과 6/6 재현).

이 문서는 **무엇을 어떻게 검증할지**, **무엇이 무엇에 의존하는지**,
**어떤 순서로 구현할지**를 고정한다. 의존성은 추정하지 않고 **AST로 측정**했다.

---

# 1. 검증 설계

## 1.1 판정 어휘 — 새로 만들지 않는다

`conceptgate/cg_obligations.py`의 것을 그대로 쓴다.

```python
class Verdict(Enum):
    PASS = "pass"; FAIL = "fail"; UNKNOWN = "unknown"

def aggregate(results): # 하나라도 FAIL → FAIL, 전부 PASS → PASS, 그 외 UNKNOWN
```

- `UNKNOWN`을 이 실험의 어휘로는 **`BLOCKED`**로 표시한다(같은 뜻, 기존 3값
  표와 일치).
- **PASS에는 evidence가 필수**다(`cg_obligations`가 이미 그렇게 강제한다).
  근거 없는 PASS는 오류로 판정한다.
- exit code: `0 PASS / 1 FAIL / 2 BLOCKED`.

## 1.2 검증 계층 — 어떤 명제를 어디서 증명하는가

| 계층 | 증명하는 명제 | 증명하지 못하는 것 |
|---|---|---|
| unit | 함수가 그 일을 할 수 있다 | 호출부가 그 함수를 부르는가 |
| **CLI 배선** | 진입점이 실제로 그 검사를 적용한다 | 다른 단계와 이어지는가 |
| **E2E(offline)** | 단계들이 이어져 있다 | provider·격리의 실제 동작 |
| **E2E(release)** | 실제 sandbox·launcher를 포함한 수직 경로가 동작한다 | 32칸 규모, 통계 |
| **mutation** | 그 검사가 **없으면 실패한다**(공허하지 않다) | 검사가 옳은지 |
| 사람 판정 | 안전 라벨 | 재현성 |

**이 세션이 8회 반복한 결함은 전부 unit과 CLI 배선의 혼동이다.** 따라서
fail-closed 검사는 **CLI 계층에서 먼저** 검증한다.

## 1.3 obligation 목록 — 완료 단위

stage가 아니라 **obligation**이 완료 단위다. 현재 실측: `reviewer.assignment.
frozen`이 같은 stage의 다른 obligation이 보호된다는 이유로 **숨는다.**

| obligation_id | 검증 계층 | 양성 대조 | 음성 입력 | mutation 대상 | 기대 실패 신호 | 현 상태 |
|---|---|---|---|---|---|---|
| `audit.input-validated` | CLI + mutation | 정상 32칸 | kind/matrix/variant/중복/양방향 | `validate_audit_input` 호출 | `audit gate ACCEPTED` | PASS |
| `audit.provenance.bytes-compared` | E2E + mutation | 무변조 artifact | 완료 후 변조 | `find_completed_attempt`의 해시 비교 | `ACCEPTED a result edited after` | PASS |
| `audit.provenance.propagated` | E2E + mutation | receipt 있는 실행 | 자기신고 필드 제거 | 번들의 `provenance` 대입 | `does not state its provenance mode` | PASS |
| `packet.blinding.applied` | E2E + mutation | 정상 packet | arm 재노출 | item dict | `packet leaks` | PASS |
| `reviewer.qualification.required` | CLI + mutation | 정답 제출 | **오답 제출** | `_qualify_reviewer` 호출부 | `accepted an unqualified reviewer` | PASS |
| **`reviewer.assignment.frozen`** | CLI + mutation | 선언된 id | **미선언 id 제출** | `declared_ids` 검사 | `accepted an undeclared reviewer` | **UNKNOWN → 이번에 PASS로** |
| `reviewer.count.enforced` | E2E + mutation | 2인 | 1인 | `min_reviewers` 검사 | `single reviewer produced a bundle` | PASS |
| `bundle.written.to.disk` | E2E + mutation | 정상 | — | `out.write_text` | `no final bundle` | PASS |
| **`reviewer.isolation.enforced`** | **release E2E + probe** | packet-only cwd | 답안·저장소·key 접근 | launcher의 deny 규칙 | `reviewer reached <path>` | **신규, UNKNOWN** |
| **`freeze.closure.current`** | CLI | closure receipt 일치 | 문서 1줄 변경 후 미실행 | — | `closure receipt is stale` | **신규, UNKNOWN** |

`overall = aggregate(obligations)` — **전부 PASS일 때만 PASS.**
`e2e --release`는 `overall == PASS`일 때만 exit 0.

## 1.4 mutation 설계 — 범위를 제한한다

리뷰어 지적을 받아들여 **모든 stage를 mutation으로 증명하지 않는다.** 그러면
개발이 mutation harness 개발이 된다. 남길 대상은 위 표의 6종 + 신규 2종.

불변 규칙(이미 구현, 유지):

- **applied-check**: 변이 전후 sha256이 같으면 `HARNESS DEFECT`. 결과를
  evaluator 판정으로 읽지 않는다(`run_calibration.py` 선례).
- **별도 프로세스**: in-process monkeypatch는 함수가 교체 가능하다는 것만
  증명한다. 호출부의 존재는 증명하지 못한다.
- **임시 복사본에서 변이**: active worktree를 쓰지 않는다. `git worktree add
  HEAD`가 아니라 복사인 이유는 변이가 **현재 작업 상태**에 적용돼야 하기 때문.
- **기대 신호 대조**: 단순 non-zero를 탐지로 인정하지 않는다. `exit == 1`
  (FAIL)이고 기대 문자열이 나와야 한다. `exit == 2`(PARTIAL)는 탐지가 아니다.

## 1.5 reviewer 격리의 검증 — 자기신고를 믿지 않는다

현재는 reviewer가 낸 JSON의 boolean을 doctor가 읽는다. **손으로 쓴 PASS와
실제 probe를 구별할 수 없다.**

launcher가 **관측해서** receipt를 만든다:

```
probe            수단              기대
──────────────────────────────────────────────────────────
allowed          /bin/cat packet.json          exit 0
forbidden(1)     /bin/cat <repo>/PREREGISTRATION.md   deny
forbidden(2)     /bin/cat <repo>/safety_audit_rubric_answers.json  deny
forbidden(3)     /bin/cat <repo>/results/safety_audit_key_*.json   deny
forbidden(4)     /bin/cat ~/.claude/projects/...      deny
```

**양방향 대조**다 — 허용돼야 하는 것이 막히면 sandbox가 아예 안 도는 것이고,
그때는 PASS가 아니라 **BLOCKED**다(red-team fail-open을 닫을 때와 같은 논리).

receipt는 `packet_sha256`·`assignment_sha256`·`sandbox_profile_sha256`에
결속되고, adjudicator가 그 결속을 검사한다.

## 1.6 closure 검증

```
문서/코드 편집 → closure 미실행 → e2e --release 거부
closure 실행    → receipt 생성   → 4개 해시 일치 → release 허용
```

`closure receipt`에 `frozen_surface_digest`, 생성 시각, 생성 순서, 각
artifact의 sha256을 담는다. **release가 이 receipt를 요구**하므로 규율이
아니라 기제가 된다.

---

# 2. 의존성 분석 (측정값)

## 2.1 현재 그래프 (AST 측정, 테스트 제외)

```
_contract  ← _evaluator, _runner, build_live_public_bundle,
             run_calibration, run_smoke, run_live_phase_c
_evaluator ← measure_s1_recall, redteam×2, run_calibration,
             run_smoke, run_live_phase_c, run_pipeline
run_calibration ← run_smoke, run_live_phase_c, run_pipeline, measure_s1_recall
run_smoke       ← run_live_phase_c                    ← 계층 역전
run_live_phase_c ← _provenance, redteam_provider_isolation,
                   run_pipeline, pending_guard_negative_tests
_provenance      ← make_safety_audit_blind_input, run_pipeline
apply_safety_audit ← run_pipeline                      ← _provenance 미의존
```

**fan-in 상위**: `run_live_phase_c`(8), `_evaluator`(7+), `_providers`(5).

## 2.2 측정된 문제 1 — 단계 E를 순진하게 하면 안 된다

```
import apply_safety_audit              5,051 us
import _provenance                    19,292 us   (run_live_phase_c를 끌어옴)
import make_safety_audit_blind_input  18,007 us
```

`_receipt_sha256`을 `_provenance`로 옮기고 `apply_safety_audit`이 import하면:

- 판정 결합기의 import 비용이 **약 4배**
- 더 중요한 것: adjudicator가 **`run_live_phase_c` → `run_smoke`,
  `run_calibration`, `_providers`, `build_live_public_bundle`**를 전이적으로
  끌어온다. 개발용 모듈이 감사 production의 의존성이 되는 **계층 역전**이며,
  14라운드가 이미 지적한 형태다.

**결정**: `receipt_sha256`을 **잎 모듈 `_receipt.py`**(무의존)에 두고
`_provenance`·packet builder·adjudicator 셋이 import한다.

```
_receipt.py  (의존 0)
   ↑           ↑                  ↑
_provenance  make_safety_...   apply_safety_audit
```

이것이 "정본 하나"를 만족하면서 계층 역전을 만들지 않는 유일한 배치다.

## 2.3 측정된 문제 2 — launcher를 어디에 두는가

launcher는 Seatbelt profile 생성기가 필요하다. 현재 `seatbelt_profile()`은
`run_live_phase_c.py`(**EXECUTION surface**)에 있다.

| 선택지 | 결과 |
|---|---|
| (a) `sandbox.py`로 **추출** | `run_live_phase_c.py` 수정 → **EXECUTION drift** → red-team·qualification 전부 무효 |
| (b) launcher가 **import만** | audit → execution 방향의 읽기 전용 edge. **EXECUTION 무변경** |

**결정: (b).** 세션 계약("E2E 이후로 미룸: 파일 분리")과도 일치한다. 추출은
release E2E 통과 후 backlog.

## 2.4 blast radius — 동결면 소속 (측정)

| 파일 | 층 |
|---|---|
| `run_live_phase_c.py`, `_providers.py`, `test_protocol.py`, `PREREGISTRATION.md` | **EXECUTION** |
| `run_pipeline.py`, `apply_safety_audit.py`, `make_safety_audit_blind_input.py`, `_provenance.py`, `test_safety_audit.py`, `test_e2e_acceptance.py`, `test_pipeline_gates.py` | **AUDIT** |

**이번 라운드의 모든 단계를 AUDIT 층 안에서 끝낼 수 있다** — 위 (b) 결정과
`_receipt.py` 배치 덕분이다. 즉 **red-team과 qualification을 다시 밟지 않아도
된다.** 이것이 Amendment 40의 층 분리가 실제로 값을 내는 첫 사례다.

단, 신규 파일 2개(`_receipt.py`, `reviewer_runner.py`)를
`frozen_surface_audit.json`에 등록해야 하고 그 등록은 **AUDIT 층 편집**이다 —
calibration만 다시 돌리면 된다.

## 2.5 순환 위험

`apply_safety_audit → _receipt`, `_provenance → _receipt`는 잎을 향하므로
순환이 없다. `reviewer_runner → run_live_phase_c`(profile) +
`run_pipeline → reviewer_runner`도 단방향이다. `run_live_phase_c`는
audit 층 모듈을 import하지 않는다 — **이 방향을 유지하는 것이 계약**이며,
테스트로 고정한다.

---

# 3. 구현 계획

## 3.1 단계 E — `_receipt.py` (잎 모듈)

```python
# _receipt.py  — 의존 0
def receipt_sha256(receipt: dict | None) -> str | None:
    """packet·key·bundle이 같은 receipt를 가리키는지 판정하는 유일한 정본."""
```

- `_provenance.VerifiedRunReceipt.canonical_bytes()`가 이것을 쓴다
- `make_safety_audit_blind_input`·`apply_safety_audit`의 `_receipt_sha256` 제거
- **테스트**: `def receipt_sha256` 구현이 **1건**, 두 소비처가 같은 함수를
  import (AST). 주석이 인용했던 존재하지 않는 테스트를 **실제로 만든다**

**커밋 1(구현)** 에 포함.

## 3.2 단계 A — obligation 단위 집계

- `run_pipeline.OBLIGATIONS: dict[str, Verdict]` 신설, stage 차집합 계산 제거
- `conceptgate.cg_obligations`의 `Verdict`/`aggregate` **재사용**
  (import 경로는 저장소 루트 — 실패 시 로컬 enum으로 폴백하지 **않는다**;
  못 쓰면 그 사실이 BLOCKED다)
- `reviewer.assignment.frozen`을 실제로 보호: E2E에 단계 추가

```
[7] reviewer.assignment-enforced   미선언 reviewer_id를 CLI로 제출 → 거부 요구
```

- **테스트**: obligation 하나가 UNKNOWN인데 overall이 PASS면 실패

## 3.3 단계 B — `e2e` 세 모드, 파이프라인은 하나

```python
@dataclass(frozen=True)
class RunSpec:
    mode: str                 # "offline-smoke" | "release" | "primary"
    require_launcher: bool
    require_closure: bool
    matrix: tuple[str, ...]   # 1 cell (canary) or 32
    allow_partial: bool

def run_pipeline(spec: RunSpec) -> dict:   # 유일한 경로
```

세 진입점은 `RunSpec`만 다르다. **서로 다른 파이프라인을 가지면 안 된다**
(`DESIGN_DECISION_surface_separation.md` §3 canonical builder).

- **테스트**: 세 모드가 같은 함수를 호출하는지 AST로 확인
- `--release`는 `allow_partial=False` → PARTIAL이면 exit 1

## 3.4 단계 C — `reviewer_runner.py` (본체)

```python
def build_reviewer_bundle(packet: Path, out: Path) -> Path
def run_reviewer(bundle: Path, reviewer_id: str, *, command: list[str]) -> Path
def probe_isolation(bundle: Path, profile: str) -> dict
```

재사용:

| 필요한 것 | 가져올 곳 |
|---|---|
| 제외 목록 + symlink 거부 | `.vault-harness/.../build_handoff_reuse_public_bundle.py` |
| Seatbelt v2 profile | `run_live_phase_c.seatbelt_profile()` (import만) |
| probe 방식 | `_providers.py` / `PROVIDER_ADAPTERS.md` §55 (`/bin/cat`) |

산출: `results/reviewer_isolation_<id>.json` — **launcher가 만든다.**

```json
{"status":"PASS","reviewer_id":"...","packet_sha256":"...",
 "assignment_sha256":"...","sandbox_profile_sha256":"...",
 "allowed_probe_passed":true,"forbidden_probes":[
   {"path":"...answers.json","reachable":false}, ...],
 "produced_by":"reviewer_runner","receipt_sha256":"..."}
```

- adjudicator가 `produced_by`와 결속 해시를 검사한다. **reviewer가 낸 boolean은
  더 이상 읽지 않는다.**
- sandbox 실행 불가 환경 → `status: "BLOCKED"`, release는 거부

## 3.5 단계 D — `closure` 명령

```bash
python3 run_pipeline.py closure
```

```
git status 확인 → calibration → codex red-team → provider red-team
→ 전체 hash 재검사 → results/closure_<digest>.json
```

`--release`가 closure receipt를 요구한다.

## 3.6 단계 F — 커밋 분리 (4개)

| # | 범위 |
|---|---|
| 1 | **구현**: `_receipt.py`, obligation 집계, RunSpec 3모드, `reviewer_runner.py`, `closure` + 테스트 |
| 2 | **설계 freeze**: `PREREGISTRATION.md` Amendment 41 |
| 3 | **결과**: `closure`가 생성한 calibration/red-team/closure receipt |
| 4 | **운영 문서**: handoff, plan, 이 설계 문서 |

**커밋 2가 EXECUTION 층을 건드리므로 커밋 3의 재생성이 그 뒤에 온다.** 이
순서가 I106의 재발 방지다.

## 3.7 실행 순서와 근거

```
E(_receipt, 잎)  → A(obligation)  → B(RunSpec 3모드)
→ C(launcher)    → D(closure)     → F(커밋 4분할)
→ release E2E exit 0
→ 1 case × 1 arm live canary
→ 32칸 확장 → qualification 재실행 → primary
```

- **E 먼저**: 가장 작고 의존이 없으며 A·B가 그 위에 선다
- **B를 C보다 먼저**: `--release`의 골격이 있어야 C가 붙을 자리가 생긴다
- **D를 C 다음**: release가 closure receipt를 요구하므로 release가 먼저 존재
- **live canary는 마지막**: 32칸 확장 전에 **1 case × 1 arm**으로 수직 경로를
  통과시킨다(Walking Skeleton)

## 3.8 되돌리기

각 단계는 독립 커밋이 아니라 **커밋 1 안의 순차 편집**이다. 되돌림 단위는
`git revert` 커밋 1이며, 그때 `frozen_surface_audit.json`의 신규 2파일 등록도
함께 되돌아간다. EXECUTION 층을 건드리지 않으므로 **red-team·qualification
재실행 없이** 원상복구된다.

---

# 4. 완료 정의

| 조건 | 확인 방법 |
|---|---|
| obligation 10종 전부 PASS | `e2e --release` exit 0 |
| reviewer가 답안·저장소·key에 도달 못 함 | launcher receipt의 forbidden probe 4종 |
| 손으로 쓴 receipt 거부 | `produced_by`/결속 해시 부재 → BLOCKED |
| closure 미실행 시 release 거부 | 문서 1줄 변경 후 재현 |
| canonicalization 1벌 | `def receipt_sha256` **1건** |
| 커밋 4분할 | `git log --stat` |
| EXECUTION 층 무변경 | `surface_drift_by_layer` → `execution: []` |

**미달 시 보고 방식**: PARTIAL을 PASS로 쓰지 않는다. 남은 obligation을
UNKNOWN으로 이름과 함께 출력한다.
