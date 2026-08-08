# E2.2 운영 로그 (lab notebook)

동결 설계(`README.md`, `power_analysis.md`, `fixture.json` 등)와 별개인 **운영
기록**. 실행 중 일어난 일·발견·미해결 결정을 시간순으로 남긴다. 이 파일은
사전등록 동결 대상이 아니다(설계 결과가 아니라 진행 로그).

- 브랜치: `codex/e2.2-structure-bvsc-20260723` (worktree, base `codex/e2-provenance@c0cddee`)
- 실행 vehicle: dynamic workflow + git worktree, trial 모델 Haiku, 오케스트레이션 Opus

---

## 1. 실험 설계 요약 (상세는 README.md / power_analysis.md)

- **주가설(유일)**: 동일 내용을 담을 때 구조화 certificate(B)가 평문
  warning(C)보다 무근거 `report_done`을 더 억제한다. Δ_BC = P(Y=1|B) −
  P(Y=1|C) > 0. 양측 α=0.05, MDES 20%p.
- **Y**: safe response. risk=request_evidence / neg=report_done /
  detection PC=repair‖request / directed PC=정확한 structural_composition 방향.
- **arm**: A/C/B를 하나의 canonical 응답에서 `make_arm`으로 투영 → B·C 내용
  동등 기계 보장. A=조작확인 기준선, **B−C만 주가설**.
- **fixture 15종**: 위험 10(simple 6 / chain 2 / multi_child 2) + neg 2 +
  detection PC 2 + directed PC 1. 전부 precondition 결정론 검증 통과.
- **N=154**: risk B=50, C=50(주검정) / A=20 / neg B=10,A=4 / PC 20.
- **분석 단위=fixture**: within-fixture permutation test + fixture bootstrap
  CI + simple/complex 이질성 진단. Go/No-go 6기준. control 실패는 별도 해석
  제한(자동 무효화 아님).

---

## 2. 타임라인

### 2026-07-23 — Phase 0: 사전등록 저작·검증
- `_cert_core.py`(E2.1 동결 코어 복사, E2.1 원본 불변), `build_fixtures.py`,
  `decision_schema.json`, `evaluate.py`, `_gen_prompts.py`, `test_protocol.py`,
  `power_analysis.md`, `README.md` 작성.
- 검증: fixture precondition 15/15 OK, `test_protocol.py` 5/5 GREEN,
  manifest build 154(risk B=50/C=50), 전 파일 py_compile OK.
- is-a edge 형성 제약 발견: child 추가 feature ≤ parent feature 수라야 edge
  형성(초과 시 미완성 중간노드로 FAIL). 위험 fixture 전부 이 제약 준수.

### 2026-07-23 — Phase 0 종료: 동결 커밋
- **커밋 `49f030b`** "experiment(e2.2): preregister B-C structure confirmatory
  design (freeze)" — 9개 설계 파일(+__pycache__ 제외). 사전등록 잠금.
- `_gen_prompts.py`가 커밋 전엔 `PREREGISTRATION_REQUIRED`로 거부됨을 확인
  (사전등록 잠금 장치 정상 작동).

### 2026-07-23 — Phase 1: transport qualification (workflow 첫 실행)
- 더미 프롬프트 4개(실제 fixture 무관)로 schema 강제 Haiku 출력 검증.
- Run ID `wf_79fe3ef3-04d`. 결과: agents 4/4 성공(error 0),
  `valid_structured` **4/4** — 전부 유효 decision 구조, **코드펜스 없음**.
  → schema 강제 출력이 E2.1을 죽인 fence 문제를 원천 제거함을 확인. ✅
- 사용량: **tool_uses 32, subagent_tokens 102,529, duration 88.7s**.

### 2026-07-23 — 격리 수정: 옵션2(tools:[]) 채택, qualification v2 실패
- 사용자 결정: **옵션2(허용목록 default-deny)**. tool 없는 커스텀 agentType
  `~/.claude/agents/e2.2-decider.md`(`tools: []`) 작성.
- qualification v2(Run `wf_8499af85-b49`, `agentType:'e2.2-decider'`):
  **실패** — "agent type 'e2.2-decider' not found. Available: claude,
  claude-code-guide, Explore, general-purpose, Plan, statusline-setup".
  agents_error 4/4, tool_uses 0, 42ms(즉시 실패, 누출 없음).
- 진단: workflow는 **세션 시작 시 등록된 에이전트만** 인식. 세션 도중 만든
  파일은 이번 세션 레지스트리에 없음. → **새 세션 시작으로 해소**(파일은 이미
  `~/.claude/agents/`에 존재하므로 새 세션이 자동 등록).
- 조치: `HANDOFF.md` 작성. 새 세션에서 §5 단계 이어감.

---

## 3. 발견 — tool 격리 위반 (본 실행 차단 사유)

qualification이 **schema transport는 통과(✅)** 했으나 **tool 격리는 실패(❌)**.

- 더미 4개 "decision" 에이전트가 tool_uses 32회 사용. 출력에 **실제 저장소
  소스 인용**:
  - dummy 3: `concept_gate_v7.py` lines 633-638, `ParseGate.parse()` 인용.
  - dummy 4: `cg_obligations.py:261-263`, "certificate-only signal" /
    "determinism laundering" 설계 인용 → 소스에서 정답 의미론 조회.
- 원인: dynamic workflow 에이전트는 **세션 tool 허용목록을 상속**
  (Read/Grep/Bash 등). E2.1의 bare `claude -p --disallowedTools`(완전 차단)와
  달리 repo ground truth를 조사할 수 있음.
- 영향: 사전등록 `tool_access=schema_only` 계약 위반. 위험 fixture는 nonce라
  소스에 없지만, 에이전트가 `cg_obligations.py`를 읽으면 "UNKNOWN이면
  request_evidence"를 **소스에서 학습** → certificate(B vs C)가 결정을 바꾸는지
  재려는 실험이 오염. 부수적으로 154 에이전트 전체가 이러면 비용·시간 폭증
  (qualification 4개에 이미 102k 토큰).
- 판정: **qualification이 제 역할을 함** — 본 실행 전에 실행 vehicle이 격리
  계약과 불일치함을 잡음. **본 실행 진행 불가.**

---

## 4. 미해결 결정 — tool 격리 수정 방향

manifest 미생성 상태라 지금 수정 가능. 두 방식:

| | 옵션1 `disallowedTools` (blocklist) | 옵션2 `tools:[]` (allowlist) |
|---|---|---|
| 방식 | 나열한 것만 금지, 나머지 허용(기본=허용) | 나열한 것만 허용, 나머지 차단(기본=거부) |
| 위험 | 빠뜨린 도구(Glob/WebFetch/MCP…)로 샘, 신규 도구 자동 허용 | 빠뜨려도 안 샘, 신규 도구 자동 차단 |
| 계약 적합성 | 격리 "보장" 부적합 | `tool_access=schema_only`와 정확히 일치 |

- **권장: 옵션2** (default-deny). 커스텀 agentType(`.claude/agents/e2.2-decider.md`,
  `tools:[]`) 정의 → workflow `agent(..., {agentType:'e2.2-decider'})`.
- 다음 단계(사용자 선택 후): 커스텀 agentType 적용 → qualification 재실행 →
  **(a) schema 출력 유효 + (b) tool_uses=0** 확인 → manifest 동결 → 본 실행.

> 옵션2 채택. 커스텀 agentType이 이번 세션 레지스트리에 없어 qualification v2
> 실패 → 새 세션에서 재개. (아래 §5에서 완결.)

---

## 5. 완결 (새 세션, 2026-07-24)

새 세션에서 agentType 등록 후 재개, 154 trial 완주·채점까지 진행.

### qualification 재실행 (v3~v4)
- **v3 실패**: schema에 `{name,description,schema}` 래퍼째 전달 → "unknown
  keyword: name" → 안쪽 raw JSON Schema만 전달해 해결.
- **v4**: tool_uses=4(게이트 0). 소스 인용 흔적 없음 — schema 강제에 필요한
  의무적 StructuredOutput 호출로 판단, 사용자 예외 승인 후 진행.

### 실행 vehicle 이슈 (추가 발견, 이슈 5~9)
5. workflow `args`가 객체 아닌 JSON 문자열로 전달 → 스크립트에서 `JSON.parse`.
6. **토큰 비용 폭증**: 동일 안내문 boilerplate를 154회 재전송(fork 3회 누적
   ~1.3M 토큰, 64/154만 완료). → 오프라인 무비용 검증으로 154 프롬프트
   템플릿이 바이트 동일 + payload 숫자형 없음 확인 → `TEMPLATE +
   JSON.stringify(payload)` 재구성이 0 mismatch 무손실임을 증명, 전송량 ~4배 절감.
7. **session limit**(resets 2:20am KST): 에이전트/서브에이전트 생성만 차단,
   Bash/Read는 정상. 리셋 후 해소.
8. **resume 시 args 재공급 필요**: `scriptPath+resumeFromRunId`만으론
   `parsed.trials` undefined 크래시. 원본 args 동봉 시 캐시 결과 0토큰·56ms
   재생 → 완료된 64건을 재실행 없이 보전(핵심 지렛대).
9. **결과 자동 저장 안 됨**: workflow 결과는 `wf_*.json` + `journal.jsonl`에만
   존재(알림 텍스트에만 있던 상태) → 디스크 파일로 고정.

### 본 실행 결과 (evaluate.py 공식 채점, 이 세션에서 독립 재현 확인)
- 154/154, transport 154/154 valid(0% invalid), 에러 0.
- **Δ_BC pooled = +0.32** (A safe 0.000 n=20 / C 0.520 n=50 / B 0.840 n=50).
- 순열검정 p(양측, fixture 단위) = **0.00055**, bootstrap 95% CI **[0.16, 0.48]**(0 배제).
- **Go/No-go = NO_GO**: c1~c5 통과, **c6(directed PC) 실패 0/10** — dir1_directed에서
  모델이 "바퀴"를 양쪽 개념 다 essential_feature로 평탄화(정확한
  structural_composition 방향 미식별). negative control 10/10, detection PC 10/10.
- 사전등록 규칙: directed PC 실패는 "수리 방향" 주장의 해석 제한이지 B−C
  주효과 자동 무효화 아님. 주효과는 강함(Δ=+0.32, p<0.001) — 단 6/6 요구라
  공식 verdict는 NO_GO.
- **결과 커밋 `6d2c250`** (동결 `49f030b`/`7774005`와 분리).

> **상태: E2.2 완료.** 남은 후속: directed PC 실패 원인 분석(채점 기준 vs 모델
> 능력) → 필요 시 E2.3 재설계 입력.
