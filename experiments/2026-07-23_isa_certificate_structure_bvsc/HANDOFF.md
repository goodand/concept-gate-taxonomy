# E2.2 인계 문서 (HANDOFF)

> **완료됨 (2026-07-24)**: 아래 §4 블로커는 새 세션에서 해소됐고 154 trial
> 완주·채점까지 끝났다. 결과: Δ_BC=+0.32, p=0.00055, CI[0.16,0.48], **NO_GO**
> (c6 directed PC 0/10만 실패, c1~c5 통과). 결과 커밋 `6d2c250`.
> 상세 완결 타임라인은 `OPERATIONS_LOG.md` §5. 이 문서 §4~§5는 당시 인계
> 지침이며 기록으로 보존한다.

다른 세션/사람이 E2.2를 이어받아 완료하기 위한 문서. 설계는 동결됐고
(`49f030b`), 본 실행 직전 **tool 격리 블로커**에서 멈춰 있다. 이 블로커는
**새 세션 시작으로 해소**된다(아래 §4).

## 1. 목표와 현재 위치

- **주가설(유일)**: 동일 내용을 담을 때 구조화 certificate(B)가 평문
  warning(C)보다 무근거 `report_done`을 더 억제한다. Δ_BC = P(Y=1|B) −
  P(Y=1|C) > 0. 양측 α=0.05, MDES 20%p. (상세: `README.md`, `power_analysis.md`)
- **현재 Phase**: Phase 0(사전등록) 완료·동결. Phase 1(transport
  qualification) 진행 중 — schema transport는 통과, **tool 격리에서 막힘**.
- **운영 타임라인·발견 상세**: `OPERATIONS_LOG.md`.

## 2. 저장소 상태

- worktree: `/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-e2.2-wt`
- 브랜치: `codex/e2.2-structure-bvsc-20260723` (base `codex/e2-provenance@c0cddee`)
- 동결 커밋: **`49f030b`** "experiment(e2.2): preregister B-C structure
  confirmatory design (freeze)" — 설계 9파일. **push 안 됨**(로컬만).
- 미커밋 로컬 파일(운영 기록, 동결 대상 아님): `OPERATIONS_LOG.md`, 이 `HANDOFF.md`.
- E2.1(`experiments/2026-07-19_isa_certificate_only_ab_clean_baseline/`)은
  **수정 금지** — E2.2는 `_cert_core.py`로 코어를 복사만 함.

## 3. 완료된 것 (검증됨)

- fixture 15종 precondition 15/15 결정론 통과(`build_fixtures.py` exit 0).
  위험 10(simple 6/chain 2/multi_child 2) + neg 2 + detection PC 2 + directed PC 1.
- `test_protocol.py` 5/5 GREEN (B/C 내용동등, manifest/trial 검증+변조탐지,
  순열 결정성, precondition, 역할 채점).
- `evaluate.py`: 주검정 B−C + fixture 순열검정 + bootstrap CI + simple/complex
  이질성 진단 + Go/No-go 6기준 + provenance 게이트. 합성데이터 동작 확인.
- `_gen_prompts.build_manifest()`: 154 prompt(risk B=50/C=50) 생성 확인.
  (단, `_prompts.json`은 아직 **생성 안 함** — qualification 통과 후 동결.)
- schema 강제 출력이 E2.1의 코드펜스 문제를 제거함을 qualification v1에서 확인
  (valid_structured 4/4).

## 4. 블로커와 해소 (핵심)

**블로커**: dynamic workflow 에이전트가 세션 tool 허용목록을 상속 →
qualification v1에서 더미 에이전트가 실제 repo 소스(`cg_obligations.py` 등)를
읽고 정답 의미론을 조회. 사전등록 `tool_access=schema_only` 위반.

**수정 방향(사용자 승인)**: 옵션2 — tool 없는 커스텀 agentType(`tools:[]`,
default-deny). 에이전트 정의 작성 완료:
`~/.claude/agents/e2.2-decider.md` (`tools: []`).

**왜 아직 안 됨**: qualification v2에서 `agentType:'e2.2-decider'`가
"agent type not found"로 실패. workflow는 **세션 시작 시 등록된 에이전트만**
인식하는데, 그 파일을 세션 도중 만들어 이번 세션 레지스트리에 없었다.

**해소**: 에이전트 파일이 이미 `~/.claude/agents/`에 있으므로 **새 세션을
시작하면 레지스트리에 자동 등록**된다. 새 세션에서 §5를 이어가면 된다.
(확인: 새 세션의 "Available agent types"에 `e2.2-decider`가 보여야 함.)

## 5. 남은 단계 (새 세션에서)

1. **에이전트 등록 확인**: 새 세션에서 `e2.2-decider`가 agent 레지스트리에
   있는지 확인(없으면 `.claude/agents/`로 위치 변경 후 재시작, 또는
   `--agents` JSON으로 세션 시작).
2. **qualification 재실행** (Workflow, 더미 4개, `agent(d,{schema, model:'haiku',
   agentType:'e2.2-decider'})`). **합격 기준: valid_structured 4/4 AND
   tool_uses=0.** (스크립트: `OPERATIONS_LOG.md`/과거 run 참고, 또는 아래 §6.)
3. **manifest 동결**: worktree에서
   `python3 experiments/2026-07-23_isa_certificate_structure_bvsc/_gen_prompts.py`
   → `_prompts.json` 생성(design_commit `49f030b` 기록). 커밋해 동결.
4. **본 실행** (Workflow, 154 trial): 동결 `_prompts.json`의 prompts 배열을
   `args`로 전달, `pipeline(args.trials, t => agent(t.prompt, {schema, model:'haiku',
   agentType:'e2.2-decider', label:...}))`. 런타임 관리 → bash 타임아웃 없음.
   `Large workflow` 경고(>25 agent) 예상 — 권고성.
5. **trials.json 조립**: 각 결과를 capture_template에 채움. execution 라벨은
   `context_isolation="workflow_cold_subagent"`, `tool_access="schema_only"`,
   provider/model/started_at/completed_at/context_id/temperature(null) 기록.
   raw_response=결정 JSON 직렬화, output=검증된 decision, parse_error=null.
6. **채점**:
   `python3 experiments/2026-07-23_isa_certificate_structure_bvsc/evaluate.py`.
   provenance 게이트 통과해야 채점 출력. Go/No-go 6기준 자동 판정.
7. **결과 커밋**: 동결 커밋과 **분리된** 결과 커밋(`experiment(e2.2): record...`).
   push 여부는 사용자 확인.

## 6. 실행 시 지켜야 할 불변조건

- 동결 설계(fixture/scorer/schema/manifest) **결과 보고 수정 금지**.
- trial 모델 = Haiku(`claude-haiku-4-5`), 오케스트레이션 = 세션 모델. 전 trial
  provider/model/temperature 동일.
- qualification에서 **tool_uses=0을 확인하기 전에는 본 실행 금지**(격리 계약).
- control 실패(특히 directed PC)는 **별도 해석 제한**이지 주효과 자동 무효화
  아님. 분석 단위는 fixture(순열/부트스트랩).
- schema 강제 출력이 B·C에 동일 적용되므로 B−C 대비는 transport에 불변.

## 7. 참고 파일

- `README.md` — 사전등록 문서(가설/Y/N/arm/Go-No-go/불주장).
- `power_analysis.md` — MDES·N·클러스터 power 한계·Go-No-go 6기준.
- `OPERATIONS_LOG.md` — 운영 타임라인·qualification 결과·블로커 상세.
- `~/.claude/agents/e2.2-decider.md` — tool 없는 trial 에이전트 정의.
