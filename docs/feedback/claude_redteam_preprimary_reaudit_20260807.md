---
aliases:
  - Claude Amendment 21 Pre-Primary Reaudit
tags:
  - doc/review
  - stage/handoff
  - status/pending-review
---

# Amendment 21 pre-primary re-audit — F1-F7 재검증

- 감사일: 2026-08-07
- 역할: 사전 맥락 없는 독립 red-team reviewer. **피험자 아님.** 기존 구현 세션의
  결론을 신뢰하지 않고 canonical 파일과 재현 결과만으로 판정했다.
- 실행하지 않은 것: primary, pilot, provider CLI, MCP, 네트워크, 유료 모델 호출
  **0건**. `--resume`/`--continue`/세션 재사용 0건.
- 읽지 않은 것: `hidden_gold/gold.json`, 홈 디렉터리 transcript·자격증명·세션 상태.
- 수정하지 않은 것: 코드·config·corpus·evaluator·result artifact·ledger·gold.
  **이 문서 1건만 신규.** `PRIMARY_AUTHORIZATION.json`을 만들지 않았다. 커밋하지 않았다.
- 실행한 것: `/private/tmp` 복사본에 대한 mutation/공격 스크립트 3종, 다중 프로세스
  lock 경합 시험 1종, 읽기 전용 hash/schema 검사, provider를 호출하지 않는 local
  pytest 107건.

**절차상 고지 —** `concept-gate-codex-mcp-wt`는 dirty worktree다. 워크스페이스 안전
게이트가 dirty worktree를 보호 대상(읽기·검색만)으로 규정하므로, 사용자가 명시
지시한 이 문서 외에는 어떤 파일도 만들거나 고치지 않았다. 모든 공격은 `/private/tmp`
복사본과 `live.RESULTS_DIR` monkeypatch 위에서만 수행했다.

---

## 0. 요약

| 공격 | 판정 | 한 줄 |
|---|---|---|
| **A1** matrix 축소 | **PASS** | 요구 matrix가 frozen primary config spec 소유로 이동했다. 축소 신고는 ledger를 함께 위조해도 거부된다 |
| **A2** 1글자 변조 | **PASS** | 외부 qualification ledger hash가 거부한다 |
| **A3** 6개 필드 위조 | **PASS** | 12개 조합(필드 6 × ledger 재결속 2) 전부 거부. spec 앵커가 ledger보다 먼저 잡는다 |
| **A4** 승인 파일 없는 primary | **PASS** | provider 호출·attempt ledger 생성 이전에 거부. ledger 파일 미생성 실측 |
| **A5** authorization 변조 6종 | **PASS** | 6/6 거부(+ `max_attempts=true` bool 우회도 거부) |
| **A6** output-name 반복 실행 | **PASS** | 두 번째 claim이 `attempt limit exhausted` |
| **A7** claim TOCTOU | **PASS** | 8 프로세스 × 5 trial 동시 경합에서 매번 정확히 1건 성공, ledger 1행 |
| **A8** frozen surface 포함 | **PASS** | `test_*.py` 5종·v7·surface v2 config 전부 포함(39 entry), calibration/red-team 2종 drift `[]` |
| **A9** qualification 필드 분리 | **PASS** | 두 artifact 모두 필수 필드 보유. Claude v2 outcome failure가 보존돼 있고 PASS로 재해석되지 않았다 |
| **A10** 승인·시도 파일 부재 | **PASS** | 두 파일 모두 부재(정확한 경로 `ls` 확인) |

**demonstrated defect: 0건.** F1-F7이 겨냥한 네 공격(축소·변조·약한 config·반복
실행)은 이번 표면에서 재현되지 않았다. 다만 아래 **잔여 위험 R1-R4**는 남아 있고,
그중 R1은 설계상 수용된 것이지 닫힌 것이 아니다.

---

## 재현 방법 (non-gold, 전부 local)

세 스크립트를 `$CLAUDE_JOB_DIR/tmp`에 작성해 `python3 -B`로 실행했다. 공통 골격:

```python
# 실제 artifact/ledger/calibration/red-team을 /private/tmp 로 복사한 뒤
live.RESULTS_DIR = Path("/private/tmp/reaudit-<tag>")   # 원본은 읽기만
live._assert_primary_qualifications(cfg)                # 또는 _assert_primary_authorization / _claim_primary_attempt
```

config 파일은 `HERE`에서 읽히므로 복사하지 않고 원본을 **읽기만** 했다. gold는
어떤 경로에서도 열지 않았다 — 모든 공격이 gold 없이 성립한다.

---

## A1 — PASS: matrix 축소가 primary gate를 통과하지 못한다

### 근거

요구 matrix의 소유자가 artifact에서 **frozen primary config spec**으로 이동했다.

- `run_live_phase_c.py:773-777` — `expected_arms = spec["arms"]`,
  `expected_cases = spec["case_ids"]`. spec은 `config["primary"]
  ["required_qualification_artifacts"]`의 항목이며 config 파일 자신이 frozen
  surface에 있다(`_evaluator.py:240`, `:233`).
- `run_live_phase_c.py:775-777` — artifact가 신고한 `config.pilot`이 spec과
  **다르면 그 자체로 거부**한다. F1 권고의 후반부가 그대로 구현됐다.
- `run_live_phase_c.py:778-785` — `n_runs`와 per-arm 커버리지를 spec 기준으로 재확인.
- `run_live_phase_c.py:749-752` — spec에 `config_file`/`provider`/`sandbox_policy`/
  `arms`/`case_ids`가 없으면 "external matrix/config anchor" 부재로 거부.

### 재현 결과

```
=== A1: artifact self-declares one-cell matrix ===
('REFUSED', 'refusing primary: live_pilot_claude_mcp_surface_v2.json
            qualification matrix declaration differs from spec')
A1b: also forge ledger entry to match the shrunken artifact
('REFUSED', ... 'matrix declaration differs from spec')
```

원본 F1 재현(실제 통과 artifact의 `config.pilot`을 `S_DYNAMIC × HD01`로 축소하고
`n_runs=1`, `per_arm` 1개만 남김)을 그대로 반복했고, **추가로** 외부 ledger 행의
`sha256`/`arms`/`case_ids`까지 축소본에 맞춰 재결속했다. 두 경우 모두 거부됐다 —
ledger가 아니라 **frozen config spec**이 먼저 잡기 때문이다.

또한 "약한 config 선택" 경로를 전수 확인했다. `ALLOWED_CONFIG_NAMES`
(`run_live_phase_c.py:50-63`) 12개 config 각각에 `_assert_primary_qualifications`를
먹였다:

```
phase_c_live_config.json                  -> refused: required_qualification_artifacts must be explicit
phase_c_codex_v2 / mcp_config / v2..v6    -> refused: qualification spec lacks an external matrix/config anchor
phase_c_claude_config / mcp_surface       -> refused: (동일)
phase_c_codex_mcp_v7_config.json          -> PASSES-QUAL-GATE
phase_c_claude_mcp_surface_v2_config.json -> PASSES-QUAL-GATE
```

**superseded config 10종이 전부 fail-closed다.** F3(약한 기본 경로)은 `--config`
required(`:1020`)와 이 spec 요구로 이중으로 닫혔다.

---

## A2 — PASS: harmless field 1글자 변조가 거부된다

### 근거

`run_live_phase_c.py:790-800` — 실제 파일 SHA-256을 계산해
`results/qualification_ledger.jsonl`의 행과 `file`/`sha256`/`config_sha256`/
`arms`/`case_ids` **5개 필드 동시 일치**를 요구하고, 일치 행이 **정확히 1건**이
아니면 거부한다(`len(matches) != 1`). 중복 append도 이 조건에 걸린다.

### 재현 결과

`live_pilot_codex_mcp_v7.json`의 `interpretation` 문자열에서
`"small pilot"` → `"smoll pilot"` 한 글자만 바꿨다(내부 정합성은 그대로).

```
bytes changed: True
('REFUSED', 'refusing primary: qualification ledger mismatch: live_pilot_codex_mcp_v7.json')
```

F2가 요구한 "외부 digest"가 실제로 동작한다.

---

## A3 — PASS: 6개 필드 독립 위조가 전부 거부된다

각 필드를 **단독으로** 위조하고, 각각에 대해 ledger 재결속 **없음/있음** 두 조건을
돌렸다(12 조합).

| 위조 필드 | 거부한 앵커 | 메시지 |
|---|---|---|
| `config_file` | frozen config 실파일 존재+해시 (`:766-771`) | `has wrong qualification config identity` |
| `config_sha256` | 동일 (`:769`) | `has wrong qualification config identity` |
| `provider` | spec 대조 (`:762-765`) | `has wrong provider` |
| `sandbox_policy` | spec 대조 (`:762-765`) | `has wrong sandbox_policy` |
| `case_ids` | spec 대조 (`:775-777`) | `matrix declaration differs from spec` |
| `arms` | spec 대조 (`:775-777`) | `matrix declaration differs from spec` |

**ledger 재결속은 어떤 필드에서도 도움이 되지 않았다** — 12/12 거부. 이유는
거부가 ledger 이전 단계(`:762-785`)에서 나기 때문이고, 그 단계의 대조 상대는
frozen surface 안의 config 파일이다. 즉 앵커가 **2겹**(frozen config spec + 외부
ledger)이며 서로 독립이다.

---

## A4 — PASS: authorization 없는 primary는 provider·ledger 이전에 거부된다

### 근거

`run_live_phase_c.py:905-922` 실행 순서:

1. `:905` `_assert_ready` (calibration/drift/red-team preflight)
2. `:908` `_assert_primary_qualifications`
3. `:909-910` `_assert_primary_authorization`
4. `:911-913` 기존 결과 덮어쓰기 거부
5. `:914-922` `_claim_primary_attempt`
6. `:923` `load()` → `:931-948` provider 호출

`_assert_primary_authorization`(`:805-833`)의 첫 문장이 `:809-811` 파일 부재 거부다.

### 재현 결과

실제 v7/surface v2 artifact와 실제 ledger 복사본을 쓰고 authorization만 없앴다.

```
qualification stage: PASSED ['live_pilot_claude_mcp_surface_v2.json','live_pilot_codex_mcp_v7.json']
authorization stage: ('REFUSED', 'refusing primary: explicit authorization file is missing')
attempt ledger created? False
```

**qualification은 통과하고 authorization에서 멈춘다** — 이것이 F5가 요구한 분리다.
attempt ledger 파일이 생성되지 않았음을 실측했다.

---

## A5 — PASS: authorization 변조 6종이 전부 거부된다

`/private/tmp` fixture에 well-formed authorization을 만든 뒤 각각 하나씩 변조했다.

| 변조 | 결과 | 근거 |
|---|---|---|
| well-formed (PRECISION 대조) | **PASSED-GATE** `(sha, max_attempts=1)` | `:816-824` |
| 다른 config hash | REFUSED `wrong config_sha256` | `:818,823` |
| 다른 qualification hash | REFUSED `wrong qualification_sha256` | `:819,823` |
| 축소된 matrix | REFUSED `wrong matrix` | `:820,823` |
| 빈 `authorized_by` (`"   "`) | REFUSED `lacks authorized_by` | `:825-826` |
| 빈 `authorized_at` (`""`) | REFUSED `lacks authorized_at` | `:827-828` |
| `max_attempts=0` | REFUSED `must be positive` | `:829-831` |
| `max_attempts=true` (bool 우회) | REFUSED `must be positive` | `:830` `isinstance(..., bool)` 배제 |

추가로 **required artifact 하나를 authorization에서 빼는** 변형도 시험했다 —
`qualification_sha256` dict 완전 일치를 요구하므로 거부된다.

> 주의 — 1차 시행에서 "다른 qualification hash"가 통과하는 것처럼 보였으나, 이는
> 내 fixture가 `qualification_sha256`으로 `verified` dict를 **같은 객체로 참조**해
> 양쪽을 동시에 변조한 오류였다. `copy.deepcopy`로 다시 돌려 거부를 확인했다.
> 공격 스크립트의 공유 참조는 게이트를 공허하게 보이게 만든다.

---

## A6 — PASS: output-name 변경으로 시도 제한을 우회할 수 없다

`_claim_primary_attempt`(`:836-867`)는 **authorization digest**로만 집계한다
(`:858-860`). output 이름은 record의 장식 필드일 뿐 카운트에 관여하지 않는다.

```
auth sha 2fce992af6b2 max_attempts 1
 claim#1 (live_primary_A): ('PASSED-GATE', None)
 claim#2 (live_primary_B): ('REFUSED', 'refusing primary: authorization attempt limit exhausted')
 ledger rows: 1
```

F5의 "선택적 보고" 경로(여러 번 돌리고 마음에 드는 것만 인용)가 닫혔다.

---

## A7 — PASS: 확인과 append가 하나의 exclusive lock 안에 있다

### 코드 검사

`run_live_phase_c.py:841-867`:

```python
with path.open("a+", encoding="utf-8") as handle:
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)   # :842
    handle.seek(0); ...                            # :843-857  읽기·집계
    if used >= max_attempts: raise ...             # :861-862  판정
    handle.seek(0, os.SEEK_END); handle.write(...) # :864-867  append + fsync
```

읽기·판정·쓰기가 **모두 lock 획득 이후, `with` 블록 종료(=lock 해제) 이전**에
있다. 락 해제 후 재확인하는 창이 없다. `a+` 모드라 append는 항상 파일 끝으로 간다.

### 다중 프로세스 실측

`multiprocessing`(spawn) 8 프로세스를 `Barrier`로 동시 출발시켜 같은 임시 ledger와
`max_attempts=1` authorization digest를 claim하게 했다. 5회 반복:

```
trial 0..4: procs=8 max_attempts=1 -> succeeded=1 ledger_rows=1
            outcomes=['OK','REFUSED','REFUSED','REFUSED','REFUSED','REFUSED','REFUSED','REFUSED']
```

**5/5 trial에서 정확히 하나만 성공했고 ledger 행도 1이었다.** flock은 advisory지만
이 경로의 유일한 writer가 같은 함수이므로 실효적이다(잔여 R3 참조).

---

## A8 — PASS: 테스트·config가 frozen surface에 있고 세 artifact가 같은 지문을 가리킨다

- `_evaluator.py:248-252` — `test_protocol.py`, `test_live_phase_c.py`,
  `test_live_phase_c_claude.py`, `test_codex_mcp_provider.py`,
  `test_preprimary_gates.py` 5종 전부 포함.
- `_evaluator.py:240` `phase_c_codex_mcp_v7_config.json`, `:233`
  `phase_c_claude_mcp_surface_v2_config.json` 포함.
- 기제 검사 `test_preprimary_gates.py:171-174` — `glob("test_*.py") ⊆
  FROZEN_SURFACE_FILES`. 규율이 아니라 게이트다(F7 권고 충족).
- 실측: `ALLOWED_CONFIG_NAMES` 12종 중 frozen에 빠진 것 **0건**, frozen 39 entry 중
  디스크에 없는 것 **0건**.

현재 표면 대비 `frozen_surface_drift()` 결과:

| artifact | drift |
|---|---|
| `results/calibration.json` | `[]` (failures `[]`) |
| `results/redteam_codex_mcp_isolation.json` | `[]` (`passed=true`, findings 8) |
| `results/redteam_provider_isolation.json` | `[]` (`n_probes=33`, `hardened_profile_leaks=[]`) |
| `results/live_pilot_codex_mcp_v7.json` | `[]` |
| `results/live_pilot_claude_mcp_surface_v2.json` | `[]` |

**calibration과 두 red-team artifact가 두 qualification artifact와 같은 현재 지문을
가리킨다.** provider isolation의 leak 2건은 v1 historical(`Q4/v1`, `Q1/v1`)이며
hardened v2 leak은 0이다 — v1 config는 A1에서 확인했듯 primary 자격이 없다.

local pytest(무과금, provider 호출 0): `107 passed`, `asyncio_mode` 경고 1건.
qualification log가 주장한 `107 passed`와 일치한다.

---

## A9 — PASS: 필수 필드가 있고 outcome failure가 보존돼 있다

두 artifact 실측:

| 필드 | codex v7 | claude surface v2 |
|---|---|---|
| `arm_effect_estimable` | `false` | `false` |
| `n_per_cell` | `1` | `1` |
| 셀별 `judged_payload_sha256` | 4/4 존재 (고유) | 4/4 존재 (고유) |
| `execution_failure_codes` | 4/4 `[]` | 4/4 `[]` |
| `host_action_compliance.passed` | 4/4 true | 4/4 true |

생성 경로: `run_live_phase_c.py:998-1000`(pilot 전용 플래그),
`:950-955`(셀별 compliance/`C5`/payload hash), `:963-966`(arm별 compliance rate와
`execution_noncompliance_count`).

`C5`는 `host_action_compliance` 실패에서만 나오고 성능 코드(`D0/R1/R2/X1/I1/A1/S1/T1`)와
**다른 필드**에 들어간다(`:954`). F6이 요구한 execution/outcome 분리가 구현됐다.

### Claude surface v2 outcome failure — 지워지지 않았다

| arm | hard gate | invalid | codes | critical recall | authority hit |
|---|---|---|---|---|---|
| S_STATIC | true | false | `[]` | 1.0 | true |
| **R_STATIC** | **false** | false | **`R1,R2,T1`** | **0.0** | **false** |
| S_DYNAMIC | true | false | `[]` | 1.0 | true |
| **R_DYNAMIC** | **false** | false | **`A1`** | 1.0 | true |

지시된 두 항목이 **원문 그대로 artifact에 남아 있고**, `qualification.passed=true`는
이 값들을 근거로 계산되지 않는다. 판정 기준은 `:970-980`의
`invalid_run == false` + host action compliance 뿐이다.

### Protocol qualification ≠ retrieval/outcome performance

R_STATIC 셀을 host trace로 열어 보면 이 분리가 왜 필요한지가 그대로 보인다:

- host actions 6건, subagent host actions 17건, `invalid_run=false`,
  `stop_reason="answer"`, `claim_range_exposure_rate=1.0` — **프로토콜은 완전히 정상**.
- 그러나 host-owned `reads`는 `docs/HANDOFF.md 1-120`과
  `notes/audits/two-shapes-2026-06-11.md 1-120` 두 건뿐이고
  `exact_authority_hit=false`, `critical_path_recall=0.0`.
- `_evaluator.py:176-177` — `stop_reason=="answer"`인데 authority read가 없으면 `T1`.

즉 **문서를 찾아 읽고 인용 범위도 정확했지만 요구된 authority 경로에 닿지 못했다.**
이것은 지시된 표현으로 `partial discovery`이며, 발견·backlink 성공은 evaluator PASS가
아니라는 명제의 실물 사례다. 다만 여기서 `trace invalid`는 **아니다** —
`invalid_run=false`이고 trace schema는 통과했다. 두 개념을 구별해 기록한다.

---

## A10 — PASS: 승인/시도 파일이 실재하지 않는다

정확한 경로를 직접 확인했다(`rg` 단독 결론 아님):

```
$ ls -la experiments/2026-08-07_handoff_dynamic_controller/results/PRIMARY_AUTHORIZATION.json
ls: PRIMARY_AUTHORIZATION.json: No such file or directory
$ ls -la .../results/primary_attempt_ledger.jsonl
ls: primary_attempt_ledger.jsonl: No such file or directory
```

`results/qualification_ledger.jsonl`은 **정확히 2행**이며 두 행의 `sha256`이 현재
파일 해시와 일치한다:

- `live_pilot_codex_mcp_v7.json` → `b437305f4fab…54180` ✔
- `live_pilot_claude_mcp_surface_v2.json` → `da4b8648e144…a64cc` ✔

A4에서 확인한 대로 authorization 부재는 provider 호출 이전에 거부되므로, 두 파일의
부재는 **"아직 primary가 승인되지도 시도되지도 않았다"의 보조 근거**로 성립한다.
(부재만으로는 증명이 아니다 — 누군가 실행 후 지웠을 가능성은 이 감사가 배제하지
못한다. R4 참조.)

---

## 잔여 위험 — 닫히지 않은 것

demonstrated defect와 구별해 기록한다. 아래는 **이번 공격이 통과시킨 것이 아니라,
설계상 남겨진 표면**이다.

### R1 (MED-HIGH) — outcome 지표는 ledger로 보호되지 않는다: 2곳 동시 위조가 통과한다

`qualification_ledger.jsonl`은 artifact **전체 파일 해시**만 보관한다
(`:872-881`). 따라서 matrix/provider/config를 건드리지 않고 **점수만** 고친 뒤
ledger 행의 `sha256`을 재계산해 넣으면 gate를 통과한다. 실측:

```
=== R1 residual: rewrite OUTCOME metrics + relink ledger (matrix untouched) ===
('PASSED-GATE', {'live_pilot_claude_mcp_surface_v2.json': 'a5601015b325…',
                 'live_pilot_codex_mcp_v7.json': 'b437305f4fab…'})
```

Claude v2의 4개 셀 전부 `full_hard_gate=True`, `critical_path_recall=1.0`,
`failure_codes=[]`로 고쳐 놓고 ledger를 재결속한 상태가 **통과했다.**

이것은 F2의 최소 수정이 명시적으로 수용한 상한이다("위조 지점이 두 곳으로 늘고
append-only 이력이 남는다"). 그러나 두 조건이 그 상한을 실제보다 약하게 만든다:

1. `qualification_ledger.jsonl`이 **frozen surface에 없다**(`_evaluator.py:218-256`
   목록에 부재 — 의도적으로 `results/`를 제외). 따라서 ledger 변조는 drift로 잡히지
   않는다.
2. append-only는 **관행이지 기제가 아니다** — 파일 권한·서명·외부 사본이 없다.
   `len(matches) != 1`이 중복 append는 잡지만 **행 재작성(rewrite)은 못 잡는다.**

**최소 수정** — ledger 행에 셀 단위 지문을 함께 못박아 "점수만 고치기"를 위조
대상에 포함시킨다. 이미 artifact가 그 값을 들고 있으므로 새 계산이 없다:

```python
def _record_qualification(output_path, out):
    pilot = out["config"]["pilot"]
    _append_jsonl(RESULTS_DIR / QUALIFICATION_LEDGER_NAME, {
        ...,
        "judged_payload_sha256": {r["case_id"] + ":" + r["arm"]: r["judged_payload_sha256"]
                                  for r in out["results"]},
        "full_hard_gate": {r["case_id"] + ":" + r["arm"]: r["full_hard_gate"]
                           for r in out["results"]},
    })
```
그리고 `_assert_primary_qualifications`가 ledger 행의 이 두 dict를 artifact 현재
값과 대조한다.

**짝 회귀 테스트**
```python
def test_rewriting_only_outcome_metrics_is_refused_even_if_the_ledger_is_relinked():
    """점수만 고치고 ledger sha를 재계산한 artifact — 실측으로 통과했다."""
    # per-cell full_hard_gate/judged_payload_sha256 불일치로 LiveRunError

def test_an_untouched_artifact_still_matches_its_per_cell_ledger_entry():
    """PRECISION — 거부만 하는 게이트는 primary를 영원히 막아 같은 관측을 만든다."""
```

### R2 (LOW-MED) — ledger 행의 matrix가 "실행한 것"이 아니라 "config가 선언한 것"이다

`run_live_phase_c.py:871-881`의 `pilot = out["config"]["pilot"]`는 **config 선언값**을
쓴다. `--arm`/`--case-id` 로 축소 실행한 pilot도 ledger에는 4-arm으로 기록된다.
실측(가짜 `out`으로 `_record_qualification`만 호출):

```
artifact actually covered: n_runs=1 per_arm=['S_DYNAMIC']
ledger row claims      : arms=['S_STATIC','R_STATIC','S_DYNAMIC','R_DYNAMIC'] case_ids=['HD01']
primary gate: REFUSED -> refusing primary: incomplete qualification matrix
```

**primary는 여전히 막힌다**(`n_runs`/`per_arm`이 spec과 안 맞음). 그러나 ledger를
읽는 사람에게는 부분 실행이 완전 실행으로 보인다 — 이 저장소가 반복 기록한
"생성물이 스스로를 잘못 라벨링" 계열이다. **최소 수정**: `"arms": sorted(out["per_arm"])`,
`"case_ids": sorted({r["case_id"] for r in out["results"]})`로 실행값에서 파생.
**짝 테스트**: 축소 실행이 축소된 ledger 행을 남기는지(음성) / 완전 실행이 4-arm 행을
남기는지(양성).

### R3 (LOW) — flock은 advisory이며 로컬 파일시스템 가정이다

A7은 같은 함수를 쓰는 writer들 사이에서만 상호배제를 증명한다. `results/`를 직접
편집하는 다른 도구, 또는 NFS류 마운트는 이 보장 밖이다. 실행 위험은 낮으므로
수정 권고 없이 한계로만 기록한다.

### R4 (LOW) — attempt ledger 자체가 사후 삭제·재작성될 수 있다

`primary_attempt_ledger.jsonl`도 `results/` 아래이고 frozen surface 밖이다. A10의
"파일이 없다"는 "아직 안 돌았다"의 **보조** 근거이지 증명이 아니다. 외부(예: git
커밋, 별도 append-only 저장소)로 내보내지 않는 한 이 상한은 남는다.

---

## documentation drift — 코드 결함 아님

1. `PROVIDER_ADAPTERS.md:154` 이하 §7이 여전히 `91 passed`를 실행 가능 근거로
   인용한다. 현재는 `107 passed`다. 문서 상단(`:3-7`)에 Amendment 21 상태 주석이
   있으므로 오도 위험은 낮으나 숫자는 낡았다.
2. `PROVIDER_ADAPTERS.md:150-160`의 권장 순서가 아직 `phase_c_codex_v2_config.json` /
   `phase_c_claude_config.json` qualification을 지시한다. 두 config는 A1 전수 확인에서
   **primary fail-closed**다. 현행 순서는 PREREGISTRATION Amendment 21(`:766`)이 갖고 있다.
3. `codex_mcp_handoff_qualification_log_20260807.md:318-332`의 "먼저 읽을 파일" 목록에
   번호 `7`, `8`이 각각 두 번 나온다(항목 중복 번호). 내용 오류는 아니다.
4. 같은 로그 `:36` F4를 "Controlled"로 적었는데, 이번 감사 기준으로 F4는 기계 필드
   (`arm_effect_estimable`, `n_per_cell`)로 **강제**됐다(A9). 실제보다 약하게 적혀 있다.

### 보고 명료성 한 건 (drift도 defect도 아님, 관측 사실)

`live_pilot_codex_mcp_v7.json`의 `S_DYNAMIC` 셀은 `full_hard_gate=False`인데
`failure_codes=[]`다. `_evaluator.py:179-185`의 hard gate가 `state_ok/next_ok/stop_ok`를
포함하는데 이 셋은 **failure code를 만들지 않기** 때문이다(해당 셀은
`next_action_accuracy=False`). `failure_codes`만 훑는 독자에게는 "깨끗한 셀"로 보인다.
표를 만들 때 `full_hard_gate`와 세 accuracy 필드를 함께 읽어야 한다.

---

## 네 축 판정

| 축 | 판정 | 근거 |
|---|---|---|
| **1. Qualification artifact integrity** | **조건부 통과** | A1/A2/A3 12+2조합 전부 거부. 단 R1(점수만 고친 뒤 ledger 재결속)이 통과한다 — 위조에 2곳이 필요할 뿐 불가능하지 않다 |
| **2. Protocol/trace compliance** | **통과** | 두 artifact 8셀 전부 `invalid_run=false`, host compliance 통과, `C5` 0건, 셀별 `judged_payload_sha256` 존재. host가 `actions`/`reads`/`stop_reason` 소유(`:544-558`, `:343-355`) |
| **3. Retrieval/outcome performance** | **통과하지 않았고, 통과 여부를 판정할 자격도 없다** | Claude v2 `R_STATIC` = partial discovery(recall 0, `R1/R2/T1`), `R_DYNAMIC` = `A1`. 게다가 `n_per_cell=1`, `arm_effect_estimable=false`이므로 이 값들로 arm 효과·성능 우열을 **말할 수 없다** |
| **4. Human primary authorization** | **부재** | `PRIMARY_AUTHORIZATION.json` 없음(A10), `primary_attempt_ledger.jsonl` 없음. gate는 준비됐고 승인은 없다 |

---

## `PRIMARY_AUTHORIZATION.json`의 한계 — 명시

이 파일은 **감사 가능한 승인 기록일 뿐 인간 신원을 암호학적으로 증명하지 않는다.**
- 파일을 쓸 수 있는 어떤 프로세스(에이전트 포함)도 만들 수 있다. 서명·2인 승인·
  외부 신뢰 기점이 없다.
- `authorized_by`는 검증되지 않는 자유 문자열이다(`:825-826`은 **비어 있지 않음**만 본다).
- `authorized_at`도 형식·시각 검증이 없다(`:827-828`).
- 따라서 이 파일이 보장하는 것은 **"게이트가 통과해서 돌았다"와 "이 정확한 config·
  qualification 해시·matrix에 대한 승인이 존재한 상태에서 돌았다"를 사후에 구별
  가능하게 만드는 것**뿐이다. 그 구별은 실제로 가치가 있지만, 사용자 의사의 증명이
  아니다. 승인은 이 파일이 아니라 **사람의 명시적 지시**에서 나와야 한다.

---

## 해결이 확인된 것 / 남은 것

**해결 확인 (재현으로)**

- F1 matrix 축소 → A1. spec 소유 + `config.pilot` 불일치 자체를 거부.
- F2 artifact 변조 → A2. 외부 ledger 해시.
- F3 약한 config 기본 경로 → A1 전수. `--config` required, superseded 10종 fail-closed.
- F4 arm-effect 오용 → A9. `arm_effect_estimable=false`/`n_per_cell=1`이 기계 필드.
- F5 승인 공백 + output-name 반복 → A4/A5/A6/A7. 승인 파일 요구 + digest 기반 원자적
  attempt claim.
- F6 compliance/성능 혼동 → A9. `C5`와 `judged_payload_sha256` 분리 기록.
- F7 테스트 drift → A8. `test_*.py` 5종 frozen + 기제 검사.

**남은 것**: R1(점수 위조 2곳), R2(ledger matrix 출처), R3(advisory lock), R4(attempt
ledger 자체의 사후 변경). 그리고 축 3 — retrieval/outcome 성능은 아직 아무것도
확립되지 않았다.

**테스트가 통과했다는 이유만으로 이 시스템이 안전하다고 주장하지 않는다.** 107건은
내가 짠 공격이 아니라 구현자가 짠 대조군이고, 이번 감사가 새로 시도한 공격 중
R1은 실제로 통과했다. 게이트가 막은 것은 "내가 시도한 것"이지 "가능한 전부"가 아니다.

---

## 최종 판정

**현재 상태에서 primary를 실행할 수 있는가 — 기술적 선행조건은 갖춰졌으나 사용자의
명시적 승인이 없으므로 실행해서는 안 된다.**

---

## Cold-Start Entry

Start from [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
and then read [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|the continuation log]]. For a new workspace, use
[[docs/feedback/handoff_continuation_prompt_template|the cross-workspace handoff template]]; for this workspace, use
[[docs/feedback/codex_handoff_continuation_prompt_20260807|the rendered Codex continuation prompt]]. These are navigation/operating instructions, not
experimental authority; re-read the canonical code and artifacts before making
a claim.

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Qualification log]]
- [[docs/feedback/claude_redteam_preprimary_findings_20260807|선행 F1-F9 findings]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_prompt_20260807|이 재감사 지시서]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Preregistration (Amendment 21)]]
- [[experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS|Provider adapters]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py|Live runner / primary gates]]
- [[experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py|Evaluator / frozen surface]]
- [[experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py|Pre-primary regression tests]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/phase_c_codex_mcp_v7_config.json|Codex v7 config]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/phase_c_claude_mcp_surface_v2_config.json|Claude surface v2 config]]
- [[experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger|Qualification ledger]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json|Codex v7 qualification artifact]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json|Claude surface v2 qualification artifact]]
- [[experiments/2026-08-07_handoff_dynamic_controller/results/calibration|Calibration]]
- [[experiments/2026-08-07_handoff_dynamic_controller/results/redteam_codex_mcp_isolation|Codex MCP red-team]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/redteam_provider_isolation.json|Provider isolation red-team]]

## 이 감사가 하지 않은 것

- live run·provider CLI·MCP·네트워크·유료 모델 호출 **0건**.
- `hidden_gold/gold.json` 미열람. 모든 재현이 gold 없이 성립한다.
- 홈 디렉터리 transcript·자격증명·세션 상태 미열람. `--resume`/`--continue` 미사용.
- `results/`의 어떤 artifact, ledger, config, 코드도 수정하지 않았다.
  모든 mutation은 `/private/tmp` 복사본에서만 수행했다.
- `PRIMARY_AUTHORIZATION.json`을 만들지 않았다. 커밋하지 않았다.
- arm 효과·모델 성능·채점 정확도에 대한 판단 없음 — 감사 범위 밖이다.
- MOC와 qualification log는 canonical 파일의 **위치를 찾는 데만** 썼고 권위로
  인용하지 않았다. 모든 판정 근거는 코드 `file:line`과 실제 artifact다.
