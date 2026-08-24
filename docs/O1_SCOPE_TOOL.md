# O1 Scope 도구 — Claude Desktop·CLI에서 코호트 채점 사슬 쓰기

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본
  [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]] · 배관 근거
  [[DRYRUN_20260824]] · 그래프 [[README_acceptance_integrity]]
- 구현 `conceptgate/server_o1_scope.py` · 런처 `scripts/run_o1_scope_mcp.sh`
  · 게이트 `test_server_o1_scope.py` (19건)

## 무엇을 노출하는가 — 가장 깊게 배선되고 작동이 증명된 것

```text
manifest_v5 (동결) + .oracle_cache
        ↓  derive_cohort_oracle       커밋 해시 검증 → 불일치면 OracleDrift
        ↓  derive_acceptance_inputs   strata·floors·pass_min 유도
        ↓  ingest_cohort              plan trial 순회(출력 순회 아님)
        ↓  evaluate_scope_v2          V1 전처리 → V2 signature 비교
        ↓  score                      counts·metrics·acceptance
```

이 사슬은 드라이런 5종과 실험 게이트 404건으로 작동이 확인됐다. **모델을
호출하는 경로가 없다** — `dispatch: blocked`(D-36)은 유효하고 실행 승인은
매번 사용자 몫이다.

## 등재 (완료됨, 2026-08-24)

`~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{ "mcpServers": { "o1-scope": {
    "command": ".../concept-gate-h1-wt/scripts/run_o1_scope_mcp.sh" } } }
```

**Desktop을 재시작해야 뜬다.** 확인: `initialize`가
`{"name": "ConceptGate O1 Scope"}`를 돌려준다(실측).

인터프리터를 런처가 고정한다 — `/usr/bin/python3`은 3.9이고 fastmcp가 없다.
homebrew `python@3.13`에 fastmcp 3.4.6이 있다. fastmcp가 없으면 런처가
**exit 127로 이유를 말하고 죽는다**(조용히 죽으면 Desktop에서 원인 불명이 된다).

## 도구 7개 — 무엇부터 부를까

| 도구 | 언제 | 무엇을 답하나 |
|---|---|---|
| **`self_test`** | **첫 호출** | 이 환경에서 배관이 도는가. 5 시나리오의 수락 판정이 예상과 같은지 표로 준다 |
| `contract_status` | 답을 의심할 때 | 무슨 계약으로 답하는가 — 계약 모듈 6개·동결 표면 11개의 해시 대조 |
| `acceptance_inputs` | 기준이 뭔지 볼 때 | `pass_min` 16 · `multi_quantifier` (5,4) · strata 분포. 사전등록 출처 명시 |
| `cohort_oracle` | 재료 확인 | 20건 오라클 유도 성공 여부 |
| `dryrun` | **엣지 케이스 만들기** | `n_fail`·`n_missing`·`mq_fail`을 직접 줘서 경계를 흔들어 본다 |
| `score_cohort` | 실제 출력 채점 | `[{"trial_id","ir"}]`를 주면 counts·metrics·acceptance·trial_rows |
| `scope_compare` | 실패 1건 파기 | `case_id`·predicted·oracle → 판정 + 양쪽 signature + sha256 |

CLI도 같은 도구를 쓴다:

```bash
scripts/run_o1_scope_mcp.sh --cli self_test
scripts/run_o1_scope_mcp.sh --cli dryrun --arg mq_fail=4
```

## 무엇이 유용한지 판단하는 기준 — 이 도구가 답하는 질문

1. **"이 두 논리형은 양화 scope 구조가 같은가?"** (`scope_compare`) — 동결
   채점 계약으로 답한다. 표면 어휘·alpha-renaming·설탕 표기 차이를 걷어낸
   뒤의 구조 비교다.
2. **"이 채점 결과를 믿을 수 있는가?"** (`contract_status`) — 계약 모듈이
   드리프트했으면 `ok: false`로 말한다.
3. **"이 수락 판정은 어떤 조건에서 뒤집히나?"** (`dryrun`) — 경계를 직접
   흔들 수 있다. 16→수락, 15→거부, 출력 1건 누락→거부, mq 1/5→거부.

## 실패를 만나면 — 삼키지 않게 만들어 뒀다

모든 도구가 실패 시 같은 형태를 돌려준다:

```json
{"ok": false, "error_type": "OracleDrift", "message": "...",
 "context": {"case_id": "..."}, "traceback": ["마지막 6행"],
 "next": "무엇을 확인하면 되는가"}
```

`next`가 고칠 방향을 말한다. **엣지 케이스를 보고할 때 이 객체를 그대로
붙여 주면 된다** — `error_type`·`context`·`traceback`이 재현에 필요한 전부다.

`self_test`의 `as_expected: false` 행도 같은 용도다 — 그 행의 `counts`와
`acceptance`가 엣지 케이스의 정의다.

**예외를 삼켜 `ok: true`를 내지 않는다.** 그렇게 하면 이 도구의 목적(발견하고
고치기)이 사라지므로, `test_server_o1_scope.py`가 실패 형태의 균일성과
구조화를 게이트로 지킨다.

## 하지 않는 것

- trial·코호트 디스패치 (모델 호출 경로 없음 — 게이트가 소스를 검사한다)
- 동결 표면 쓰기 (결과는 임시 경로에만)
- 충족성 witness 반환 (기록은 sha256만 — Q30.4)

## 알려진 한계

- **`.oracle_cache`(66항목)와 동결 manifest에 의존한다.** 다른 저장소·다른
  코호트에는 그대로 쓸 수 없다 — 이것은 범용 논리 도구가 아니라 **이 실험의
  계측기를 노출한 것**이다.
- `scope_compare`의 `case_id`가 투영 정책을 고른다(미지 접두어는 fail-closed).
  코호트 밖 `case_id`로는 의미 있는 답이 안 나온다.
- 계약 모듈 드리프트 시 `contract_status`만 답하고 나머지는 거부한다 —
  진단 도구가 먼저 죽으면 무엇이 틀렸는지 알 수 없기 때문이다.

## 실측 함정 — Desktop은 `~/Desktop` 아래 스크립트를 실행할 수 없다

첫 등재는 저장소 안의 런처를 가리켰고 **Desktop이 띄우지 못했다.**
`~/Library/Logs/Claude/mcp-server-o1-scope.log`:

```text
/bin/sh: .../concept-gate-h1-wt/scripts/run_o1_scope_mcp.sh: Operation not permitted
Server transport closed unexpectedly, this is likely due to the process exiting early
```

**`Operation not permitted`(EPERM)이고 `Permission denied`(EACCES)가 아니다** —
파일 권한 문제가 아니라 macOS 샌드박스다. 두 사실이 그것을 확정한다:

- 같은 시각 `evidence-vault-mcp`(런처가 `~/.claude/scripts/`)는
  `Server started and connected successfully` + 실제 결과 응답(id=0..3).
- 두 스크립트 다 일반 셸에서는 실행된다(`-x` 확인).

즉 차이는 **런처의 위치**다. 그리고 자식 프로세스가 `~/Desktop`을 **읽는**
것은 된다 — evidence 서버가 그 경로의 vault를 실제로 서비스한다. 막히는 것은
`exec`뿐이다.

**그래서 Desktop 진입점은 `~/.claude/scripts/run_o1_scope_mcp.sh`다.**
저장소 안의 `scripts/run_o1_scope_mcp.sh`는 **CLI 전용**으로 남는다(같은 모듈).
두 런처가 갈라지지 않게 `test_server_o1_scope.py`가 인터프리터 고정값을
대조한다.

**다음 세션에 주는 경고**: Desktop 설정을 저장소 경로로 "정리"하지 마라 —
그러면 조용히 다시 안 뜬다. 로그가 이유를 말해 주지만, 그 로그를 읽기 전에는
"서버가 죽었다"로만 보인다.

## 로그 어디를 보나

```text
~/Library/Logs/Claude/mcp-server-o1-scope.log    이 서버 전용
~/Library/Logs/Claude/mcp.log                     MCP 전반
```

fastmcp 시작 배너는 **끄도록 해 뒀다**(`show_banner=False`) — stderr가 이
로그로 가므로 배너가 실제 오류를 밀어낸다. 이 서버의 목적이 실패를 보이는
것이므로 로그가 읽혀야 한다.
