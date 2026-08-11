# 검증·재사용·의존성·구현 계획 — 21b라운드: 감사 경로가 launcher를 우회한다

작성 2026-08-11. 대상 커밋 `fb69fbb`. 검토 원문
[`external_review_round21_20260811_reviewer_launcher_and_runtime.md`](external_review_round21_20260811_reviewer_launcher_and_runtime.md).

## 1. 검증 결과 — 8/8 확인

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| F1 | 실제 감사 경로가 launcher receipt를 우회 | **CONFIRMED** | `apply_safety_audit.py`에 `isolation`이라는 문자열이 **없다.** receipt를 검증하는 곳은 release E2E와 `doctor`뿐 |
| F1b | 공개 CLI가 probe-only | **CONFIRMED** | `main()`은 `run_reviewer(bundled, reviewer_id)` — command도 labels_out도 넘기지 않는다 |
| F2 | agent 배정 시 doctor가 불가능한 경로를 따라간다 | **CONFIRMED, 더 나쁨** | 아래 재현. 불일치가 아니라 **크래시**이고, **정상 경로**에서 난다 |
| F3 | release PASS의 근거가 실행 후 폐기 | **CONFIRMED** | `release_c525664cbe88.json` 키 12개에 probe·profile·output·label 해시가 **하나도 없다** |
| F4 | 11/11이 mutation 실행 결과와 미결속 | **CONFIRMED** | `demonstrated_obligations`는 케이스의 **존재**를 본다. 내 docstring이 이미 그렇게 적고 있다 |
| F5 | command hash가 구현을 식별하지 못한다 | **CONFIRMED** | `sha256("\x00".join(command))` — 같은 경로의 스크립트를 갈아치워도 값이 같다 |
| F6 | stdout schema가 보고보다 얕다 | **CONFIRMED** | 두 객체의 존재만. `additionalProperties`도 값 규칙도 없다 |
| F7 | 진입 문서에 상반된 현재 상태 | **CONFIRMED** | 아래 |
| F8 | append-only receipt가 항해 표면이 됐다 | **부분 확인** | handoff §11은 규칙으로 바꿨으나 `results/` 안에는 여전히 정본 포인터가 없다 |

### F2 재현 — 크래시, 정상 경로에서

복사 트리에서 assignment를 `ASSIGNED` + `kind: agent`로 만들고 **launcher로
올바르게 서명된** receipt를 넣은 뒤 `doctor`를 돌렸다:

```
receipt written, status = PASS
has packet_file field: False
doctor rc = 1
FileNotFoundError: .../results/missing
```

`run_pipeline.py`가 `RESULTS / doc.get("packet_file", "missing")`을 쓰는데
`IsolationReceipt.as_dict()`에 그 필드가 **없다.** 즉 이 분기는 **한 번도
실행된 적이 없다** — assignment가 `UNASSIGNED`라 도달하지 않았고, 판정자를
배정하는 순간 진단 도구가 먼저 죽는다. 리뷰어의 "충돌할 수 있습니다"보다 강하다.

### F7 실측 — 내가 §1에 남긴 것

```
docs/HANDOFF_20260810_primary_blocked.md:25
  e2e --release  exit 0   obligations 10/10 PASS, obligations_unknown []
PREREGISTRATION.md:2411-2412
  e2e --release   exit 0     obligations 10/10 PASS, obligations_unknown []
  e2e --offline   exit 0
```

현재는 의무가 **11종**이고 `offline`은 **exit 2**이며 coverage 키 이름도
`effective_unknown`으로 바뀌었다. §3b가 뒤에서 고쳐 놓았으므로 **한 문서에 두
현재 상태가 있다.** 25행은 무맥락 agent가 가장 먼저 읽는 곳이고, 거기서 얻은
기대값이 틀리면 무엇을 성공으로 읽을지가 틀린다.

**이 세션에서 진입 절의 낡은 주장이 세 번째다**(등록 지시 삭제 → 잘못된 복원 →
이번). 앞의 둘은 무맥락 재개 시험이 잡았고 이번은 외부 리뷰어가 잡았다. 공통점은
**본문을 고칠 때 요약을 같이 고치지 않는다**는 것이다.

### 리뷰어가 기각한 내 주장 — 받아들인다

> "only live canary remains" → **rejected**

맞다. F1이 열려 있으면 canary의 결과를 해석할 수 없다. canary가 실제 CLI를
돌려 label을 만들어도 **adjudicator는 그 receipt를 보지 않으므로**, 산출된
번들은 "격리된 판정자의 판정"을 증언하지 못한다.

### 환경 차이 — 기록한다

| 환경 | 결과 |
|---|---|
| Codex 관리형 sandbox | 274 passed, 20 failed, 1 skipped |
| 동일 checkout, host 권한 | 294 passed, 1 skipped |
| 이 세션(Claude Code) | 294 passed, 1 skipped |

원인은 `sandbox-exec: sandbox_apply: Operation not permitted`. **workspace가
같아도 상위 sandbox 권한 때문에 결과가 달라진다.** 그래서 20건은 회귀가 아니라
`BLOCKED`이며, 지금 테스트들은 `_skip_without_sandbox()`로 skip 처리한다 — 그것이
정직한지는 §6 S4에서 다룬다(이번 범위 아님).

## 2. 재사용 후보 조사 — 새로 설계하지 않는다

CLAUDE.md가 요구하는 순서대로 먼저 찾았다. **네 건 모두 실재하고 직접 적용된다.**

### R1. receipt를 인자로 받고 소비처가 재검증한다 — **이 실험 안에 이미 있다**

```python
# make_safety_audit_blind_input.py
def build(result_path, ..., receipt: "VerifiedRunReceipt | None" = None) -> dict:
    if receipt is None:
        receipt = verify_run(result_path)        # 정본 검증기에서 얻는다
    if receipt.result_sha256 != _sha256(result_path):
        raise ...  # receipt가 다른 바이트를 기술한다
```

**F1이 필요한 모양이 정확히 이것이다.** provenance receipt에 대해 이미 검증된
패턴을 isolation receipt에 같은 형태로 적용한다 — 새 설계가 아니다.

### R2. canonical builder — 유일 허용 경로

`concept-gate-e2.2-wt/.../DESIGN_DECISION_surface_separation.md` §3:

```
fixture → validate_fixture() → qualify_fixture() → build_model_payload()
        → render_prompt() → write_prompt_manifest() → execute_trial()
```

리뷰어의 S1(단일 production CLI)이 이것이다. 다만 §5에서 보듯 **이번 범위에서는
전면 도입하지 않는다** — F1을 닫는 데 필요한 것은 사슬의 재배치가 아니라
adjudicator가 receipt를 요구하는 것 하나다.

### R3. trial manifest — 해시는 payload 밖에 기록한다

같은 문서 §6:

```json
{"trial_id": "...", "fixture_sha256": "...", "qualification_sha256": "...",
 "payload_sha256": "...", "rendered_prompt_sha256": "...",
 "decision_schema_sha256": "...", "builder_commit": "...", "model": "...",
 "parameters": {}}
```

F3(`audit_run_manifest.json`)과 F5(reviewer execution identity)의 필드 모양이
여기 있다. **설명·비고·note 필드 금지**라는 규칙까지 함께 온다(§2).

### R4. 가드의 **존재**를 근거로 쓰지 마라 — F4의 정본 진단

`concept-gate-h1-wt/docs/HARNESS_KNOWHOW.md` B4a:

> **일반화**: 가드의 **존재**를 근거로 쓰지 마라. 가드가 참으로 만드는 명제를
> 쓰고, 그 명제가 필요한 명제와 같은지 확인하라.

`demonstrated_obligations`가 정확히 이 실수를 한다 — mutation **케이스의 존재**를
PASS로 읽는다. 같은 문서가 규율을 기제로 옮긴 방법(AST 수집 게이트)도 있다.
F4는 이 선례의 직접 적용 대상이며, **그래서 "docstring에 한계를 적었다"로
끝내면 안 된다.** 다만 §6의 이유로 이번 라운드가 아니다.

### 찾았으나 적용하지 않는 것

- `_providers`의 provider identity 기록은 `provider_meta`에 이름과 비용만 담고
  실행 바이너리를 해시하지 않는다. F5에 **그대로 재사용할 선례는 없다.**
  qualification config가 `cli_version`을 기록하는 관행이 가장 가까우며, F5는
  그것을 "실측값을 넣어라, 러너는 검증하지 않는다"는 기존 경고와 같은 층위로
  강화하는 일이다.

## 3. 검증 방법 설계 — 무엇이 각 수정을 증명하는가

원칙은 지난 라운드와 같다: **고치기 전에 빨갛고, 고친 뒤 초록이며, 되돌리면 다시
빨갛다** — 세 번째를 안 보면 테스트가 코드와 무관할 수 있다. 여기에 이번
라운드가 하나 더 붙인다.

> **F2가 가르친 것: 도달하지 않는 분기는 테스트되지 않는다.** doctor의 agent
> 분기는 `UNASSIGNED` 때문에 한 번도 실행되지 않았고, 그래서 존재하지 않는
> 필드를 참조하는 코드가 살아남았다. 따라서 각 검사는 **그 분기에 실제로
> 도달하는 상태를 만들어** 호출해야 한다(assignment를 `ASSIGNED`로 세운 복사
> 트리 등). "함수를 직접 부른다"로 대체하면 같은 구멍이 남는다.

| # | 먼저 빨갛게 | 통과 기준 |
|---|---|---|
| F7 | §1의 기대값이 현재 출력과 다르면 **실패**(문자열 대조가 아니라 **실행 결과와 대조**) | §1·PREREGISTRATION 상태 블록이 `e2e --release`/`--offline`의 실제 exit·의무 수와 일치 |
| F2 | assignment를 `ASSIGNED`+agent로 만든 트리에서 `doctor`가 **0이 아닌 exit로 크래시** 없이 판정하지 않으면 실패 | 정상 receipt → `[ok]` 행, 위조 receipt → `BLOCKED` 행, **어떤 경우에도 traceback 없음** |
| F1 | agent 판정자의 label을 receipt **없이** 제출해 adjudicator가 번들을 만들면 **실패** | receipt 부재·서명 불일치·다른 packet 결속·label 바이트 불일치 → 전부 거부 |
| F1 | human 판정자에게 receipt를 요구하면 **실패**(launcher는 사람을 격리하지 않는다) | human은 receipt 없이 통과하고, 번들이 그 사실을 명시 |
| F1b | 공개 CLI로 실제 reviewer를 돌릴 수 없으면 실패 | `reviewer_runner.py --command ... --labels-out ...`이 label과 receipt를 함께 낸다 |
| F5 | argv만 바꾸지 않고 **스크립트 내용만** 갈아치웠을 때 execution identity가 같으면 실패 | argv에 등장하는 실제 파일의 sha256이 identity에 포함된다 |

**부정 검사가 통과하는 것만으로는 부족한 자리**: F1의 거부 4종은 각각 다른
사유로 거부되어야 한다. 하나의 포괄적 예외로 뭉치면 "왜 거부됐는가"를 잃고,
다음 세션이 엉뚱한 곳을 고친다. 사유별 메시지를 요구한다.

## 4. 의존성 분석

| 파일 | 표면 | 이번 범위 |
|---|---|---|
| `apply_safety_audit.py` | AUDIT | 편집 (F1 — receipt 요구) |
| `reviewer_runner.py` | AUDIT | 편집 (F1b CLI, F2 검증 분리, F5 identity) |
| `run_pipeline.py` | AUDIT | 편집 (F2 doctor 호출부, F1 E2E 배선) |
| `test_reviewer_isolation.py` / `test_safety_audit.py` / `test_pipeline_gates.py` | AUDIT | 편집 |
| `docs/HANDOFF_…md`, `PREREGISTRATION.md` | 문서 / **동결** | F7 |
| `_providers.py`, `run_live_phase_c.py`, `_evaluator.py` | **EXECUTION** | **무변경** |

**EXECUTION 편집 0 → qualification·red-team 재실행 불필요.** `PREREGISTRATION.md`은
동결 표면 멤버이므로 F7 편집 후 **closure 재실행이 필요하다**(문서 편집이지만
해시가 바뀐다).

### 선후 관계와 순환

```
F7 (문서 상태 정정)        ← 독립. 가장 먼저. 지금 잘못된 지시를 주고 있다
F2 (검증 분리)             ← F1의 adjudicator 검증이 같은 함수를 쓰므로 F1보다 먼저
   ↓
F1 (adjudicator가 receipt 요구) + F1b (CLI) + F5 (identity)
   ↓
release E2E 배선 확인 → closure → release → canary 준비 완료
```

**F2를 F1보다 먼저 하는 이유**: F1은 adjudicator가 receipt를 검증하게 만드는
것이고, 그 검증 함수는 doctor가 부르는 것과 같아야 한다(정본 하나). doctor가
쓰는 형태가 고장 나 있는 채로 adjudicator를 그 위에 세우면 결함이 두 곳으로
번진다.

**순환 주의**: `apply_safety_audit`가 `reviewer_runner`를 import하면
`reviewer_runner`는 이미 `apply_safety_audit.VALID_LABELS`를 import하고 있으므로
**순환 import**가 된다. 실측으로 확인해야 하며, 필요하면 `VALID_LABELS`를
`reviewer_runner`가 늦게(함수 안에서) 읽거나 검증 함수를 잎 모듈로 옮긴다.
**추측하지 않고 실행해서 확인한다.**

## 5. 구현 계획 — step by step

```
0. F7  진입 문서 상태 블록을 실제 출력으로 갱신          (문서, closure 필요)
1. F2  verify_isolation_receipt를 authenticate / bind로 분리
       doctor가 경로를 추측하지 않는다
2. F1  apply_safety_audit가 agent 판정자에게 receipt를 요구
       R1(build(receipt=...)) 패턴을 그대로 적용
3. F1b reviewer_runner CLI에 --command / --labels-out
4. F5  reviewer execution identity (argv + argv에 등장하는 파일의 해시 + schema 해시)
5. release E2E 배선 확인 → closure → release
6. canary 준비 상태 재판정
```

각 단계는 **먼저 빨간 검사**를 붙이고, 그 검사가 §3의 "분기에 실제로 도달한다"
요건을 만족해야 한다.

## 6. 이번 범위에서 미루는 것 — 그리고 그 이유

리뷰어의 S5를 받아들인다: **F1·F2를 먼저 닫고 canary를 돌린다.** 광범위한
리팩터링은 canary가 구체적 실패를 발견할 때만 한다. 12~19라운드가 개별 결함을
하나씩 고치며 실제 수직 경로를 한 번도 통과시키지 않았고, 그 교훈을 여기서
다시 버리지 않는다.

- **F3 (`audit_run_manifest.json`)** — R3의 필드 모양은 확정됐다. 그러나 이것은
  **release가 남기는 증거의 확장**이고, 지금 없는 것은 증거가 아니라 **감사
  경로 자체**(F1)다. F1이 닫히면 manifest가 결속할 대상이 생기므로 순서가 이쪽이
  자연스럽다. canary 직후.
- **F4 (mutation 결과 결속)** — R4가 이것을 "존재를 근거로 쓰지 마라"의 직접
  사례로 판정한다. 미루는 이유는 난이도가 아니라 **순환**이다: mutation 하네스가
  자기 workspace에서 `closure`와 release를 다시 돌리므로, `closure`가 증거
  artifact를 만들면 재귀하고, mutated workspace의 release는 증거 부재를 읽어
  PARTIAL을 낸다 — 그러면 **모든 mutation이 엉뚱한 이유로 "검출됨"이 된다.**
  이 순환을 푸는 설계가 별도로 필요하다(예: 증거를 closure 밖의 lane에서 생성).
  F4를 닫기 전까지 `demonstrated`의 정직한 독법은 여전히 "증거가 선언되고
  존재한다"이며 그 문장이 이미 docstring에 있다.
- **F6 (schema 심화)** — `additionalProperties: false`와 qualification 값 규칙은
  10줄이다. 그러나 지금 그 계약의 실질을 지키는 것은 `_label_artifact`의 id·어휘
  대조이고, 그것은 이미 있다. canary가 실제 CLI 출력에서 예상치 못한 필드를
  만나면 그때가 정확한 시점이다 — **실제 출력을 한 번도 보지 않고 schema를
  좁히면 무엇을 좁혀야 하는지 모르고 좁힌다.**
- **F8 (정본 포인터)** — handoff는 규칙으로 바꿨고 `_closure_receipt()`를 물어보는
  명령을 적었다. `results/` 안의 포인터 파일은 append-only와 긴장 관계이므로
  설계 판단이 필요하고, 지금 항해를 실제로 막고 있지는 않다.
- **S1 (단일 production CLI)** — R2가 정본 원칙이고 옳다. 그러나 이것은 새 CLI를
  만드는 일이고, F1은 **기존 adjudicator에 검증 하나를 추가하는 일**이다. 후자로
  같은 안전 목적을 달성할 수 있으면 그것을 먼저 쓴다(CLAUDE.md의 충돌 규칙:
  불변식과 양립하는 방법이 있으면 그것부터).
- **S4 (권한 3값 lane)** — 실제 문제다. `_skip_without_sandbox()`가 지금 20건을
  skip으로 만들고 있고, skip은 이 저장소 어휘로 `BLOCKED`이며 **exit code에
  반영되지 않는다.** 즉 sandbox 없는 환경에서 suite가 초록인데 isolation은
  검증되지 않았다. F1을 닫으면 adjudicator가 receipt를 요구하므로 그 환경에서는
  **감사 자체가 거부되어** 실질 위험이 줄지만, lane 분리는 여전히 필요하다.
  canary 직후, F3와 함께.

## 7. 낮춰야 할 내 주장

- **"남은 것은 live canary 하나"** — 틀렸다. F1이 열려 있는 동안 canary 결과는
  "격리된 판정자의 판정"을 증언하지 못한다.
- **"launcher-signed receipt가 감사에 결속된다"** — release E2E 안에서만 참이다.
  실제 adjudicator는 그 파일을 열지 않는다.
- **"294 passed"** — host 권한 환경에서만. 관리형 sandbox에서는 274 passed /
  20 failed이며 그 20건은 회귀가 아니라 권한 부재다.
- **handoff §1의 `10/10` / `offline exit 0`** — 둘 다 현재 코드와 다르다.
