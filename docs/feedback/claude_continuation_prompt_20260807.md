---
aliases:
  - Claude Code Current Handoff Prompt
  - Amendment 21 Continuation Prompt
tags:
  - doc/prompt
  - stage/handoff
  - status/active
---

# Claude Code Continuation Prompt

Copy the prompt below into a new Claude Code session to continue the current
work. It is intentionally specific to this workspace and current experiment
state.

```text
현재 진행 중인 handoff dynamic-controller 실험을 이어서 수행해라.

Workspace:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

이번 세션의 목표:
Amendment 21 재감사에서 남은 R1-R4 잔여 위험을 검토하고, 사용자가 명시한
범위 안에서 다음 작업을 설계하거나 구현해라. 우선 R1(score-only rewrite),
그 다음 R2(ledger matrix provenance)를 조사하라. R3/R4는 현재 설계 한계로
분류되어 있으므로 강한 보장이 필요한지 근거를 먼저 제시해라.

작업을 시작하기 전에 아래 문서를 순서대로 읽어라:
1. docs/feedback/codex_mcp_handoff_moc_20260807.md
2. docs/feedback/codex_mcp_handoff_qualification_log_20260807.md
3. docs/feedback/claude_redteam_preprimary_findings_20260807.md
4. docs/feedback/claude_redteam_preprimary_reaudit_20260807.md
5. experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md
6. experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py
7. experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py
8. experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py
9. experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger.jsonl
10. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json
11. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json
12. experiments/2026-08-07_handoff_dynamic_controller/results/redteam_provider_isolation.json

권위 규칙:
- MOC, tag, backlink, symlink, generated view는 탐색용이다. 주장 전에는
  canonical code와 result artifact를 직접 읽어라.
- hidden_gold/gold.json은 읽거나 검색하거나 출력하거나 추론에 사용하지 마라.
- 현재 qualification은 protocol readiness만 증명한다. arm 효과나 retrieval
  성능을 증명하지 않는다.
- Claude v2의 R_STATIC recall 0 (`R1/R2/T1`)과 R_DYNAMIC `A1`은 그대로
  실패 근거로 유지하라. 이를 qualification PASS로 재해석하지 마라.
- discovery 상태와 trace 상태는 별개다. 문서를 찾았다는 사실은 evaluator
  PASS가 아니며, 발견 실패를 trace 위반으로 뭉뚱그리지 마라. 다음 세 라벨을
  구별해 쓴다:
  - `discovery incomplete / trace valid` — trace schema와 실행 기록은 유효한데
    문서 회수 또는 authority read가 부족한 경우. Claude v2 `R_STATIC`이 이
    상태다(`invalid_run=false`, `claim_range_exposure_rate=1.0`이지만
    `exact_authority_hit=false`, critical recall 0). **이것을 trace invalid로
    분류하지 마라.**
  - `discovery partial / trace invalid` — 일부 문서는 찾았으나 line_start,
    line_end, citation object 등 trace 계약을 위반한 경우.
  - `retrieval/evaluator pass` — 위 두 상태와 별개로 evaluator hard gate까지
    통과한 경우에만 쓴다.

절대 금지:
- primary, provider CLI, MCP, network, 또는 유료 model call을 실행하지 마라.
- PRIMARY_AUTHORIZATION.json을 만들지 마라.
- primary_attempt_ledger.jsonl을 만들거나 qualification artifact를 덮어쓰지 마라.
- live_pilot_*.json, qualification_ledger.jsonl, calibration.json,
  red-team artifact, gold, corpus를 수정하지 마라.
- 기존 결과를 삭제·이름 변경·병합하지 마라.
- 커밋하지 마라.

R1 비용 경계 — 착수 전에 반드시 읽어라:
R1을 수정하는 `run_live_phase_c.py`, `_evaluator.py`,
`test_preprimary_gates.py`는 **셋 다 frozen surface**다
(`_evaluator.py`의 `FROZEN_SURFACE_FILES`). 이 중 한 줄이라도 바꾸면
`frozen_surface_drift`가 즉시 현재 Codex v7과 Claude surface v2 qualification
artifact를 **stale**로 만든다(`run_live_phase_c.py`의
`_assert_primary_qualifications` drift 검사). calibration과 red-team만 다시
실행해서는 회복되지 않는다 — **두 provider의 유료 live qualification pilot을
다시 실행해야** primary 전제가 회복된다.

따라서 R1은 작은 local patch로 즉시 수행할 작업이 아니다. R1은 primary를 막고
있는 결함이 아니라 승인 이후에나 유효해지는 강화이며, 착수 여부 자체가 사용자
결정 사항이다. 사용자의 명시 승인 전에는 **재현·설계·문서화만** 하고
코드/config/result/ledger를 수정하지 마라. 승인 후에도 새 config version,
calibration, red-team, 전체 local test, 두 provider 재-qualification이 필요한
변경으로 표시하라.

R1 작업 규칙:
1. 먼저 reaudit가 실제로 통과시킨 score-only rewrite를 재현하라.
2. 수정 전 가설을 `R1 hypothesis`로 기록하라.
3. ledger가 artifact 전체 hash뿐 아니라 cell별
   `judged_payload_sha256`와 `full_hard_gate`를 외부에 고정해야 하는지
   판단하라.
4. positive test는 변경하지 않은 artifact가 통과하는 경우다.
5. negative test는 outcome score만 바꾸고 ledger를 재결속해도 거부되는 경우다.
6. ledger 자체의 rewrite를 완전히 막을 수 없는 한계를 숨기지 마라. append-only가
   규율인지 기제인지 구분하라.

R2 작업 규칙:
1. qualification ledger의 arms/case_ids가 config 선언값이 아니라 실제
   `results`/executed cell 집합에서 유도되는지 검사하라.
2. 축소된 pilot 실행이 완전한 matrix로 기록되는지 private temporary fixture로
   검증하라.
3. primary가 이미 spec matrix를 별도로 검사한다는 점과 ledger labeling 오류를
   분리하라.

수정이 필요하다고 판단하면:
- 코드 변경 전에 정확한 file:line 근거와 falsifiable hypothesis를 제시하라.
- positive/negative 짝 회귀 테스트를 먼저 설계하라.
- frozen surface를 바꾸면 새 config version을 만들고 calibration, red-team,
  전체 local test를 다시 수행해야 한다.
- live qualification은 사용자에게 먼저 보고하고 승인받은 뒤에만 실행하라.

기록 규칙:
- 새 이슈는 docs/feedback/codex_mcp_handoff_qualification_log_20260807.md에
  (1) 이슈, (2) 반복 여부, (3) 해결 근거, (4) 해결 유무, (5) 문제 정의,
  (6) 가설과 검증 방식, (7) 구체적 해결 방법 순서로 기록하라.
- 새 code/config/result/log 파일은
  docs/feedback/codex_mcp_handoff_moc_20260807.md에 Obsidian wikilink로
  추가하고 링크 관계를 한 문장으로 설명하라.
- 다른 workspace handoff를 읽었을 때도 discovery 성공과 trace/evaluator 성공을
  별도 상태로 기록하라.

작업 종료 보고에는 다음을 포함하라:
- 변경 파일
- 실행한 local-only test와 그 결과
- R1/R2/R3/R4 상태
- primary를 실행하지 않았다는 사실
- 다음 단계에 사용자 승인이 필요한지 여부
```

## Entry Links

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Current Handoff MOC]]
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Current Qualification Log]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Latest Reaudit]]
- [[docs/feedback/handoff_continuation_prompt_template|Cross-Workspace Template]]
