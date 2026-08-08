---
aliases:
  - DS07 Independent Curator Protocol
tags:
  - doc/design-proposal
  - stage/handoff
  - status/awaiting-execution
---

# DS07 gate/gold 판정 — 독립 curator 프로토콜

**상태: 프로토콜 설계됨, 판정 미실행.** 사용자 결정
([[docs/feedback/claude_questions_for_source_session_20260807|질문 7 답변]]):
DS07을 primary matrix에 현재 상태 그대로 포함해 실행하지 않는다. primary 전에
반드시 판정하거나, 사전등록 amendment로 제외해야 한다.

## 이 세션은 판정자가 될 수 없다 — 자격 배제 고지

사용자가 명시한 판정자 조건은 다음이다.

> - handoff producer가 아닌 독립 curator/reviewer
> - **arm별 결과와 점수를 보지 않은 상태에서**
> - canonical source와 public question만 읽고 판정한다.

**이 세션은 이미 arm별 결과를 봤다.** Amendment 21 재감사 과정에서
`live_pilot_codex_mcp_v7.json`과 `live_pilot_claude_mcp_surface_v2.json`의
전체 `results`/`traces` 배열을 열어 셀별 `critical_path_recall`,
`exact_authority_hit`, `failure_codes`를 반복해서 읽었고, 그 값들을
`docs/EVIDENCE_BOUNDED_AGENCY_TARGETS.md` §5 표에 그대로 옮겨 적었다. 이
사실 자체가 사용자가 요구한 첫 번째와 두 번째 조건("arm별 결과와 점수를 보지
않은 상태")을 이 세션이 충족할 수 없다는 증거다.

따라서 **이 문서는 판정을 대신 내리지 않는다.** 판정을 내릴 수 있는
프로토콜만 설계하고, 실제 판정은 아직 arm 결과에 노출되지 않은 별도 세션 또는
사람에게 넘긴다.

## DS07 문제 재확인

`PREREGISTRATION.md:184` — DS07은 discovery 조건의 **false absence** 함정이다:
"존재하는데 안 보임. zero hit ≠ 부재." Amendment 1(`:292-295`)이 이 case를
열린 문제로 남겼다: 결정론적 scripted controller 4 arm 전부가 정답 문서로
직행해 DS07에서 `D0`(handoff read 누락)가 났다. 판정이 필요한 질문은 두
가지 중 하나다.

1. gold가 DS07에서 **handoff read 자체**를 critical path로 요구하는 것이
   정당한가 (그렇다면 현재 gate 유지, controller의 miss로 판정), 아니면
2. handoff read 요구가 **절차 과잉**인가 — canonical source에 직접 도달해
   모든 critical claim과 safety condition을 회수했다면, 특정 파일을
   경유했는지는 문제가 아닐 수 있다 (그렇다면 현재 DS07은 exploratory
   결과로 동결하고 gold를 새 held-out case에서 재평가).

## 프로토콜

### 판정자 자격

- handoff producer(이 실험을 설계·구현한 세션)가 아닌 독립 세션 또는 사람.
- **arm별 결과·점수를 아직 보지 않은 상태**여야 한다 — 이 조건은 세션
  단위로 검증 불가능하므로(과거 대화를 스스로 신고하는 것 외에 강제 수단이
  없다), 새 세션에서 이 판정을 **가장 먼저** 수행하고 그 전에
  `live_pilot_*` artifact나 재감사 문서를 열지 않도록 프롬프트 자체가
  순서를 강제해야 한다.

### 판정자가 읽을 것 (이 순서로, 이것만)

1. `PREREGISTRATION.md` §8 표(케이스 정의)와 §1(연구 질문) — DS07 행만.
2. DS07의 public question (case 파일 경로는 판정 프로토콜 실행 시점에
   `public_cases/cases.json`에서 DS07 항목만 추출해 제공).
3. DS07의 canonical source(정답 corpus 문서) — public corpus 경로에서.
4. **hidden_gold/gold.json은 열지 않는다** — gold의 요구사항 자체가 판정
   대상이므로, gold를 먼저 보면 판정이 gold를 정당화하는 방향으로 편향된다.
   대신 판정자에게 "이 질문에 답하려면 무엇을 읽어야 하는가"를 스스로
   재구성하게 한다.

### 판정 기준 (사용자 원문)

- handoff 자체에만 존재하는 critical state, stop condition, authority 정보가
  답변에 필요하면 handoff read 요구는 정당하다.
- agent가 canonical source에 직접 도달해 모든 critical claim과 safety
  condition을 회수할 수 있다면, "handoff 파일을 반드시 읽어야 한다"는 조건은
  process overconstraint일 수 있다.
- 특정 파일을 읽었는지가 아니라 **필요한 evidence가 실제 trace에 노출됐는지**를
  우선한다.

### 절차

1. 판정자가 DS07 public question과 canonical source만으로 "이 질문에 정확히
   답하려면 어떤 문서를 읽어야 하는가"를 스스로 답한다.
2. 그 답이 handoff 문서를 **반드시** 포함하면 → 판정 1 (gate 유지).
3. 포함하지 않아도 canonical source만으로 모든 critical claim이 지지되면 →
   판정 2 (DS07을 exploratory로 동결, gold를 새 held-out case에서 재평가).
4. 판정자는 gold를 결과를 본 뒤 조용히 완화하는 것과, 판정 2를 내리는 것의
   차이를 명시적으로 진술해야 한다 — 전자는 metric-fitting이고 금지된다,
   후자는 사전등록 amendment로 투명하게 기록된다.

### 판정 결과에 따른 조치

| 판정 | 조치 |
|---|---|
| 1. handoff read가 critical authority | 현재 DS07 gate 유지. primary matrix에 그대로 포함. |
| 2. handoff read가 절차 요구 | 현재 DS07을 exploratory 결과로 동결(수정하지 않음). PREREGISTRATION에 새 Amendment로 기록하고, 수정된 gold는 **새 held-out case**와 **새 version**에서만 평가. 기존 DS07 결과와 합치지 않는다. |

**판정 전에는 DS07을 arm 효과 추정에 사용하지 않는다.** 현재 primary matrix
(`phase_c_codex_mcp_v7_config.json` / `phase_c_claude_mcp_surface_v2_config.json`의
`primary.case_ids`)에 DS07이 포함돼 있으므로, 판정이 나기 전 primary를
실행한다면 DS07을 case 목록에서 제외하거나 사전등록 amendment로 명시적으로
빼야 한다 — 이 결정 자체도 사용자 승인 대상이다.

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/feedback/claude_questions_for_source_session_20260807|질문 7 — 사용자 판정 원문]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Preregistration — Amendment 1 "남긴 것", §8 DS07]]
