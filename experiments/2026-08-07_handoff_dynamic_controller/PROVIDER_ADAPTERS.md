# Provider adapters — Codex CLI vs Claude CLI

> Amendment 21 status: v6 Codex and Claude surface v1 qualifications are
> historical after the pre-primary gate revision. The next eligible surfaces
> are `phase_c_codex_mcp_v7_config.json` and
> `phase_c_claude_mcp_surface_v2_config.json`. Primary remains unapproved and
> additionally requires qualification and authorization ledgers.

- 작성: 2026-08-07, worktree `claude-provider-adapter`, 기준 커밋 `8b333bc`
- 역할: harness developer / red-team. **피험자가 아니다.**
- **outcome 실험·primary sweep 미실행.** live pilot도 실행하지 않았다.
  아래 "기계 프로브"만 유료 호출을 사용했다(총 4회, 약 $0.49).

## 1. 변경 파일

| 파일 | 성격 |
|---|---|
| `_providers.py` | **신규** — provider registry, Claude CLI adapter, Seatbelt v2, response schema 검증기, JSON 추출기 |
| `phase_c_claude_config.json` | **신규** — Claude provider 동결 설정 |
| `phase_c_codex_v2_config.json` | **신규** — Codex-v2 재-qualification 동결 설정 |
| `redteam_provider_isolation.py` | **신규** — 실제 Seatbelt 프로파일로 도는 red-team 프로브 |
| `test_live_phase_c_claude.py` | **신규** — adapter/경계 테스트 40건, 유료 호출 0 |
| `PROVIDER_ADAPTERS.md` | **신규** — 이 문서 |
| `run_live_phase_c.py` | provider 선택, v2 profile, compliance, qualification/primary gate 추가 |
| `_evaluator.py` | provider 실행 입력을 frozen surface에 포함하도록 목록 확장 |
| `results/calibration.json` | 재생성 — frozen surface 지문 갱신(아래 §6) |
| `results/redteam_provider_isolation.json` | **신규** — 프로브 결과 |

**변경하지 않은 실험 의미 표면**(테스트로 강제): `_contract.py`, `_runner.py`,
`build_corpus.py`, `build_live_public_bundle.py`, `live_subject_tool.py`,
두 응답 스키마, `phase_c_live_config.json`, `corpus_manifest.json`.
corpus·gold·evaluator·action set·BudgetGuard·four-key subagent 계약·public-only
bundle·host-owned action trace 모두 그대로다.

## 2. 두 adapter의 차이

| 축 | Codex CLI (`codex-cli`) | Claude CLI (`claude-cli`) |
|---|---|---|
| 호출 | `codex exec --ephemeral --json -` | `claude --print --output-format json` (프롬프트는 stdin) |
| 세션 비영속 | `--ephemeral` | `--no-session-persistence` + 매 cell 새 `--session-id` (uuid4) |
| 사용자 설정 차단 | `--ignore-user-config --ignore-rules` | `--setting-sources ""` (user/project/local 전부 미로드 → CLAUDE.md도 미로드) |
| MCP 차단 | (user config 무시로 함께 차단) | `--strict-mcp-config --mcp-config '{"mcpServers":{}}'` |
| 승인 우회 | `--dangerously-bypass-approvals-and-sandbox` | `--dangerously-skip-permissions` |
| **스키마 강제** | provider가 강제 (`--output-schema`) | CLI `--json-schema` native structured output + adapter 재검증. 위반은 **V1** |
| 최종 JSON 취득 | `--output-last-message` 파일 | envelope의 `structured_output` 우선, `result` 산문 추출은 호환 fallback |
| 도구 제한 | 프롬프트 지시 | 프롬프트 + **`--disallowedTools`로 하드 차단**(Read/Glob/Grep/WebFetch/WebSearch/Task/Agent/Edit/Write/NotebookEdit/TodoWrite), `--allowedTools Bash` |
| 턴 상한 | (미지정) | `--max-turns` |
| Seatbelt | config에 따라 **v1 또는 v2** | **v2** (§3) |
| 비용 관측 | 없음 | envelope의 `total_cost_usd`를 `provider_meta`에 기록 |

Claude는 `--tools Bash`와 deny list로 off-trace built-in tool을 닫는다. 두 provider
모두 native schema를 사용하지만 CLI와 envelope 형식은 다르므로 provider 결과를
자동으로 합치지 않는다.

## 3. Seatbelt v1 vs v2 — red-team이 만든 차이

v1은 `(allow default)` + 저장소 root deny + bundle `control/` deny. 실제
프로파일로 `/bin/cat`을 돌려 확인한 결과:

| 대상 | v1 | v2 |
|---|---|---|
| `hidden_gold/gold.json` | 차단 | 차단 |
| `results/live_pilot_attempt9.json` (이전 결과) | 차단 | 차단 |
| `PREREGISTRATION.md` | 차단 | 차단 |
| `control/corpus/**` (socket 우회) | 차단 | 차단 |
| `control/input_manifest.json` | 차단 | 차단 |
| `subject/task.json` (읽혀야 함) | 허용 | 허용 |
| **`~/.claude/projects/**.jsonl`** | **읽힘** | 차단 |
| **`~/.codex/`** | **읽힘** | 차단 |
| `~/.claude.json` | 읽힘 | **읽힘(의도적)** |

`~/.claude/projects`에는 이 워크스페이스에서 돌린 **모든 세션의 전체
transcript**가 있고, 그중에는 corpus 본문과 gold 구조를 출력한 세션이 있다.
shell을 가진 피험자는 `grep` 한 번으로 정답에 닿는다.

**이것은 Claude 전용 결함이 아니다.** `8b333bc`의 Codex pilot도 v1에서 돌았고
같은 도달 범위를 가졌다. v1을 고치지 않고 v2를 새로 만든 이유는, v1을 바꾸면
이미 실행된 pilot의 조건을 소급 변경하기 때문이다.

`~/.claude.json`을 열어 둔 것은 **의도**다. 이걸 막으면 CLI가 로그인 계정을
못 찾아 피험자가 시작조차 못 한다. 실측: 이 파일에 **prompt history 배열은
없다**(`history` 키 0개). 남는 노출은 설정·경로 메타데이터이며 잔여 위험으로
기록한다.

## 4. Red-team 5문항 — 결과

`python3 redteam_provider_isolation.py` → `results/redteam_provider_isolation.json`
(29 프로브). v1 historical leak 2건은 보존되며, hardened v2 unexpected leak은 0건이다.

| 질문 | 판정 | 근거 |
|---|---|---|
| **Q1** 피험자가 `Project_in_progress` / `hidden_gold` / 이전 결과를 읽는가 | **저장소 경로는 불가** / **홈 경로는 v1에서 가능** | 실제 프로파일 하 `/bin/cat` 프로브. v2에서 `~/.claude/projects`·`~/.codex` 차단 |
| **Q2** socket client를 우회해 corpus를 직접 읽는가 | **불가** | `control/corpus`·`control/input_manifest.json` 둘 다 v1·v2에서 차단. 추가로 Claude는 `Read/Glob/Grep`이 CLI 수준에서 차단 |
| **Q3** self-reported path/range로 host trace를 위조하는가 | **불가** | `_trace_from_subject`가 `actions`/`reads`/`stop_reason`을 `state.trace_fields()`(호스트)에서만 취한다. 실제 소켓을 구동하는 위조 테스트 3건으로 확인 — 안 읽은 경로 인용 → `C4`, 읽은 파일의 넓힌 범위 인용 → `X1`, guard가 수락 안 한 terminal 주장 → `V1` |
| **Q4** 세션/이력이 cell 사이에 재사용되는가 | **재사용 없음(코드 수준)**, 단 v1에서는 **읽기 가능했음** | adapter에 `--resume`/`--continue` 없음, `--no-session-persistence` + cell별 uuid4. 이력 파일 읽기는 v2가 차단 |
| **Q5** invalid run이 재시도로 선택 제거되는가 | **불가** | `retry_count=0`, `invalid_run_policy=record-V1-and-do-not-replace`, runner가 기존 결과 파일 덮어쓰기 거부. Claude config가 셋 다 승계 |

Q3은 OS 경계가 아니라 코드 성질이라 프로브가 아니라 단언으로 검사한다 —
그리고 **정직한 경로가 비어 있지 않은 trace를 만든다**는 precision 테스트를
함께 둔다. 없으면 "위조 실패"와 "하네스가 아무것도 기록 안 함"이 구별되지 않는다.

## 5. 기계 프로브 — live pilot 실행 가능성

case도 gold도 쓰지 않는 최소 확인 2회(유료).

| 관측 | 결과 |
|---|---|
| Claude CLI가 Seatbelt v2 안에서 기동 | **성공** |
| Bash로 `python3 live_subject_tool.py` 실행 | **성공**, `permission_denials: []` |
| host가 action 기록 | **성공** (`reformulate_query` 1건) |
| 산문에서 JSON 추출 + 스키마 검증 | **성공** |
| 비용/턴 관측 | `total_cost_usd`, `num_turns` 기록됨 |

**전제였던 `loggedIn: false`는 사실이 아니다** — 이 PC의 Claude CLI는 이미
로그인돼 있다(`claude -p` 1회로 확인). 계획의 2단계(로그인)는 불필요하다.

## 6. 미해결 위험

1. **frozen surface 지문이 이동했다.** `run_live_phase_c.py`가 동결 표면에
   포함돼 있고 provider seam 때문에 바뀌었다. calibration을 재실행해
   재동결했고 **8/8, 58/58로 통과**했다. 그러나 이는 `8b333bc`의 Codex pilot이
   **다른 지문 아래에서 산출됐다**는 뜻이다. 브랜치 경계를 넘어 결과를
   합치려면 Codex 재-qualification이 필요하다.
2. **Codex pilot은 Seatbelt v1에서 돌았다.** 홈 transcript 채널이 열린 상태였다.
   그 pilot이 실제로 그 채널을 썼다는 증거는 없지만, **안 썼다는 증거도 없다** —
   v1에는 홈 경로 접근을 기록하는 장치가 없다. 교차 provider 비교 전에 v2에서
   Codex qualification을 다시 돌리기를 권한다.
3. **`~/.claude.json` 잔여 노출** (§3). 이력은 없으나 저장소 경로·모델 사용량이
   보인다. 닫으려면 `CLAUDE_CONFIG_DIR` 격리가 필요한데 —
4. **`CLAUDE_CONFIG_DIR` 격리는 OAuth와 양립하지 않는다(실측).** 빈 config dir,
   auth 키만 시딩한 dir, `projects`/`mcpServers`만 제거한 전체 복사본 — 셋 다
   `Not logged in`. Keychain 항목은 하나뿐이고(`Claude Code-credentials`)
   config dir 경로에 묶여 있다. **API key 인증(`ANTHROPIC_API_KEY`)이면 격리
   모드가 성립할 가능성이 있으나 검증하지 않았다.**
5. **피험자가 도구를 아예 안 부를 수 있다.** 약한 프롬프트로 돌린 1차 프로브에서
   Claude가 host client를 호출하지 않고 요구된 JSON만 반환했다(host actions 0건).
   채점상으로는 `D0`/`R1`이 되어 옳게 실패하지만, **retrieval 실패로 오독될 수
   있다.** 이제 qualification은 main host action 1건 이상과 R arm의 subagent host
   action 1건 이상을 **별도 compliance 조건**으로 강제한다.
6. **provider envelope는 비대칭이다.** Claude는 `structured_output`, Codex는 output
   file을 사용한다. 둘 다 native schema를 쓰지만 형식 실패율은 provider별로 별도
   보고한다. prose JSON 추출은 구버전 호환 fallback으로만 남긴다.
7. **process-separated이지 OS-isolated가 아니다** — clean judge 쪽 기존 한계 유지.

## 7. live pilot 실행 가능 여부

**기계적으로는 가능하다.** 로그인돼 있고, adapter가 Seatbelt v2 안에서 기동해
host client를 통해 trace를 남기고 스키마를 통과하는 것까지 확인했다.

> **2026-08-07 갱신 — Amendment 21 이후 현재 순서.** 아래 §7 원문은 Amendment 12
> 시점(v2 config)의 기록으로 보존한다. **현재 실행 가능한 유일한 순서는
> `PREREGISTRATION.md` Amendment 21이다** — `phase_c_codex_v2_config.json`과
> `phase_c_claude_config.json`은 primary spec 앵커가 없어 fail-closed다(재감사
> A1 전수 확인). 현재 순서:
> 1. local test 전체 (`test_preprimary_gates.py`, `test_protocol.py`,
>    `test_live_phase_c.py`, `test_live_phase_c_claude.py`,
>    `test_codex_mcp_provider.py`) → **107 passed** (실측, 이 문서 §7의 옛 "91
>    passed"를 대체)
> 2. `python3 run_calibration.py`
> 3. `python3 redteam_codex_mcp_isolation.py`와
>    `python3 redteam_provider_isolation.py` 둘 다
> 4. Codex v7 qualification: `--config phase_c_codex_mcp_v7_config.json`
> 5. Claude surface v2 qualification: `--config
>    phase_c_claude_mcp_surface_v2_config.json`
> 6. 두 artifact가 `qualification_ledger.jsonl`과 해시 일치할 때만
>    `PRIMARY_AUTHORIZATION.json`을 사람이 작성 — primary는 그 뒤에도 여전히
>    미승인이다.

실행 전 권장 순서 (Amendment 12 시점 기록, historical):

1. `python3 run_calibration.py` (Amendment 12 surface로 재통과)
2. `python3 -m pytest -q test_protocol.py test_live_phase_c.py test_live_phase_c_claude.py`
   → 91 passed (Amendment 12 시점 수치. 현재는 위 갱신 안내 참조)
3. `python3 redteam_provider_isolation.py` → historical v1 leak 2, hardened v2 leak 0
4. Codex-v2 qualification:
   `python3 run_live_phase_c.py --pilot --config phase_c_codex_v2_config.json`
5. Claude-v2 qualification:
   `python3 run_live_phase_c.py --pilot --config phase_c_claude_config.json`
6. 두 artifact의 `qualification.passed=true`일 때만 Claude primary 실행

runner가 위 순서를 강제한다. passing artifact가 없거나 frozen hash가 다르면 primary는
provider 호출 전에 종료한다. **이 6단계는 v2 config를 가리키는 historical 기록이며
현재 실행 경로가 아니다** — 현재는 위 갱신 안내의 Amendment 21 순서를 따른다.

**Codex 결과와 합치지 말 것.** provider, sandbox 버전, 스키마 강제 지점,
frozen surface 지문이 모두 다르다. `phase_c_claude_config.json`의
`pilot.interpretation`에 그 문장을 넣었고 테스트가 강제한다.

## 8. 이 세션이 사용한 유료 호출

| # | 목적 | 비용 |
|---|---|---|
| 1 | 로그인 상태 확인 (`ping`) | $0.304 |
| 2 | `CLAUDE_CONFIG_DIR` 격리 시도 | $0 (Not logged in) |
| 3 | 기계 프로브 1 (도구 미호출) | $0.119 |
| 4 | 기계 프로브 2 (도구 호출 확인) | $0.071 |

합계 약 **$0.49**. case·gold를 쓴 실험 실행은 0건이다.

## 9. Amendment 12 후 독립 검토

초기 provider 작업의 "실행 가능"은 adapter 단위 기계 프로브 기준이었다. 전체 CLI
entrypoint에서는 Claude config 선택 경로가 없고, adapter/config가 calibration hash 밖에
있었으며, compliance와 primary 선행조건도 문서에만 있었다. Amendment 12에서 이 세
조건을 실행 gate로 옮겼다.

무과금 검증 결과:

- calibration positive `8/8`, negative `58/58`
- provider test 포함 `91 passed`
- 실제 Seatbelt `29` probes: v1 historical leaks `2`, hardened v2 leaks `0`
- Claude config dry-run은 해당 config를 로드한 뒤 unknown case에서 종료
- Claude primary dry-run은 `live_pilot_claude.json` 부재로 provider 호출 전 종료

따라서 현재 막힌 조건은 구현 결함이 아니라 아직 실행하지 않은 두 유료 qualification
pilot(Codex-v2, Claude-v2)이다.

## 10. Provider-v2 attempt 1 결과

- Codex-v2: binary/OAuth가 deny된 provider launch failure. credential file 예외 허용은
  Bash에서 token을 읽게 하므로 금지한다.
- Claude-v2: native `--json-schema`를 사용하지 않은 adapter 오류와 invalid trace가
  실제 host state를 지우는 관측 오류를 확인했다.
- 두 결과 모두 4/4 `V1`이며 검색 성능 자료가 아니다.
- 수정 후 Claude는 `live_pilot_claude_attempt2.json`으로만 재검증한다. Codex-v2는
  credential과 subject tool 권한을 분리하기 전까지 재실행하지 않는다.

## 11. Claude-v2 qualification 최종 결과

`live_pilot_claude_attempt2.json`은 `$schema` draft URI를 Claude CLI가 거부해 모델
호출 전에 실패했다. CLI 전달용 schema에서 메타 키만 제거한 뒤 새 artifact
`live_pilot_claude_attempt3.json`을 실행했다.

attempt 3 qualification은 통과했다.

| arm | invalid | host compliance | critical recall | full hard gate | actions | reads |
|---|---:|---:|---:|---:|---:|---:|
| S_STATIC | 0 | 1.0 | 1.0 | 1.0 | 8 | 3 |
| R_STATIC | 0 | 1.0 | 1.0 | 1.0 | 8 | 3 |
| S_DYNAMIC | 0 | 1.0 | 1.0 | 1.0 | 18 | 12 |
| R_DYNAMIC | 0 | 1.0 | 1.0 | 1.0 | 15 | 10 |

공용 retrieval-only process는 host action 18건을 남겼다. 모든 Claude envelope는 native
`structured_output`을 사용했다. main 4회와 중복 제외 subagent 1회의 총 관측 비용은
`$1.837515`다. 이는 `HD01 × 1` qualification이므로 arm 성능 우열로 해석하지 않는다.

Claude primary는 의도대로 아직 거부된다. Claude qualification은 통과했지만
`live_pilot_codex_v2.json`이 provider launch `V1`이기 때문이다. Codex OAuth token을
subject Bash에 노출하는 예외 허용으로 이 gate를 우회하지 않는다.

## 12. Codex MCP-only adapter (new qualification surface)

`codex-mcp-cli`는 Codex parent가 기존 OAuth state를 읽게 두되, evaluated model에는
`handoff_action` stdio MCP tool 하나만 준다. 이 분리는 OAuth token file을 subject Bash에
예외 허용하는 방식보다 좁다. native shell/file/network/browser/app capability는 feature
disable flags로 닫고 `--dangerously-bypass-approvals-and-sandbox`는 사용하지 않는다.

`live_subject_mcp.py`는 corpus나 gold를 읽지 않는다. action payload를 host socket으로
전달할 뿐이며 host가 action validation, evidence response, trace를 권위 있게 기록한다.
MCP child process에는 dynamic socket path를 `mcp_servers.handoff.env`로 명시 전달한다.
이 경로는 local FastMCP stdio smoke에서 tool listing `['handoff_action']`와 host search
action 기록으로 확인했다.

새 run은 `results/redteam_codex_mcp_isolation.json`이 frozen surface와 일치하고 통과해야
시작한다. raw provider event에서 `command_execution` 또는 non-handoff MCP tool은 즉시
거부한다. 이 adapter의 `HD01 × 4`는 qualification-only이며, primary는 실행하지 않는다.

첫 `live_pilot_codex_mcp_v1.json`은 Codex default approval policy가 모든 MCP call을
`user cancelled MCP tool call`로 취소해 4/4 invalid였다. event는 `handoff_action`만 보였고
다른 native tool, session/thread ID 노출은 없었다. `phase_c_codex_mcp_v2_config.json`은
`--ask-for-approval never`로 이 대기만 닫는다. bypass flag는 계속 금지하며 v2 결과는 v1과
pooling하지 않는다.

v2는 `--ask-for-approval`가 `codex exec` option이 아니라 parser exit 2로 끝났다. v3는
valid config override `-c approval_policy="never"`를 사용한다. parser smoke를 통과한 이
새 config도 별도 qualification surface이며, primary 실행 권한은 주지 않는다.

v4는 `--approve-for-me`를 추가하되 bypass flag는 계속 금지한다. 먼저 one-cell vehicle
probe에서 MCP action이 host trace에 실제 기록되는지만 본다. primary gate는 passing pilot
artifact가 config의 전체 arm × case matrix를 포함하는지도 확인하므로 probe는 qualification을
대체할 수 없다.

v4 vehicle probe는 `--sandbox`와 `--approve-for-me`를 동시에 받을 수 없다는 Codex parser
exit 2로 끝났다. v5는 automatic-review mode에서 explicit sandbox flag를 제거한다. 이 모드는
workspace-write review를 사용하지만 model shell/unified exec/native discovery feature는 계속
disable되고 working root는 disposable subject bundle이다. bypass flag는 계속 금지한다.

v5 full qualification은 transport를 통과했지만 `R_STATIC`가 linkless freeze policy를 follow한
뒤 두 번째 follow를 시도해 `V1`이 됐다. v6 host response는 `static_next.path`로 follow 후
정확히 읽을 path를 결정한다. static model은 그 path를 read해야 하며, source path/target 중
임의 선택을 다시 하지 않는다. v6 is a fresh qualification surface; v5 remains failed evidence.
