---
aliases:
  - Claude Continuation Prompt Reply
  - Handoff Review Corrections Prompt
tags:
  - doc/prompt
  - stage/handoff
  - status/active
---

# Claude Continuation Prompt Reply

Copy the prompt below into the Claude Code session that reviewed the current
continuation documents.

```text
검토 결과를 반영해라. 지적한 네 가지 문제를 사실로 인정하고, 이번 작업은
문서 정정으로 한정해라. 커밋하지 마라.

Workspace:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

수정 대상은 다음 두 파일뿐이다.
1. docs/feedback/claude_continuation_prompt_20260807.md
2. docs/feedback/codex_mcp_handoff_moc_20260807.md

먼저 두 파일과 아래 canonical 문서를 직접 읽어라.
- docs/feedback/claude_redteam_preprimary_reaudit_20260807.md
- docs/feedback/codex_mcp_handoff_qualification_log_20260807.md
- experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py
- experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py
- experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py
- experiments/2026-08-07_handoff_dynamic_controller/phase_c_claude_mcp_surface_v2_config.json
- experiments/2026-08-07_handoff_dynamic_controller/phase_c_codex_mcp_v7_config.json
- experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger.jsonl
- experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json
- experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json
- experiments/2026-08-07_handoff_dynamic_controller/results/redteam_provider_isolation.json

반드시 반영할 정정:

1. 경로를 실제 경로로 고쳐라.
   - `results/qualification_ledger.jsonl`가 아니라
     `experiments/2026-08-07_handoff_dynamic_controller/results/qualification_ledger.jsonl`
   - `results/live_pilot_codex_mcp_v7.json`가 아니라
     `experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json`
   - `results/live_pilot_claude_mcp_surface_v2.json`가 아니라
     `experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json`
   프롬프트의 읽기 목록에서 세 경로 모두를 수정하고, 존재 여부를 `test -f`로
   local-only 확인해라.

2. R1의 비용과 승인 경계를 명시해라.
   R1을 수정하는 `run_live_phase_c.py`, `_evaluator.py`,
   `test_preprimary_gates.py`는 frozen surface다. 이 중 한 줄이라도 변경하면
   현재 Codex v7과 Claude surface v2 qualification artifact가 stale 상태가
   된다. calibration/red-team만 다시 실행해서는 충분하지 않고, 두 provider의
   유료 live qualification을 다시 실행해야 primary 전제가 회복된다.
   따라서 R1은 작은 local patch로 즉시 수행할 작업이 아니다. 사용자 명시
   승인 전에는 재현·설계·문서화만 하고 코드/config/result/ledger를 수정하지
   마라. 승인 후에도 새 config version, calibration, red-team, 전체 local
   test, 두 provider 재-qualification이 필요한 변경으로 표시해라.

3. MOC Evidence에 Claude provider red-team을 추가해라.
   다음 wikilink를 Evidence에 추가하고 관계 이유를 한 문장으로 써라.
   `[[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/results/redteam_provider_isolation.json|Provider isolation red-team]]`
   이 artifact는 Claude surface v2의 `seatbelt-v2` preflight와
   `hardened_profile_passed`/drift 조건을 게이팅하므로, Codex MCP red-team과
   별개의 실행 근거다.

4. 중복 링크를 제거해라.
   MOC에서 `handoff_continuation_prompt_template`가 두 번 링크되는 현상을
   하나로 합쳐라. 남길 링크는 cross-workspace 재사용 템플릿이라는 설명을
   포함해야 한다.

5. discovery 상태와 trace 상태를 분리해라.
   Claude v2 R_STATIC은 `invalid_run=false`, exposure 1.0인 유효한 trace지만
   authority read가 충분하지 않은 partial discovery다. 이를 trace invalid로
   분류하지 마라.
   문서의 판정 용어를 아래처럼 분리해라.
   - `discovery incomplete / trace valid`: 문서 회수 또는 authority read가
     부족하지만 trace schema와 실행 기록은 유효함.
   - `discovery partial / trace invalid`: 일부 문서는 찾았지만 line_start,
     line_end, citation object 등 trace 계약을 위반함.
   - `retrieval/evaluator pass`: 위 두 상태와 별개로 evaluator hard gate까지
     통과한 경우에만 사용.

금지:
- primary 또는 provider CLI, MCP, network, 유료 model call을 실행하지 마라.
- PRIMARY_AUTHORIZATION.json을 만들지 마라.
- qualification artifact, ledger, gold, corpus, calibration, red-team 결과를
  수정하지 마라.
- frozen surface에 코드나 테스트 변경을 하지 마라.
- 커밋하지 마라.

검증:
- `test -f`로 위 세 경로와 provider red-team artifact가 실제 존재하는지
  확인해라.
- `git diff --check`를 실행해라.
- 두 문서 외에 변경된 파일이 없는지 `git status --short`로 확인해라.
- 실행 결과는 문서 수정 검증으로만 보고하고, qualification이나 primary
  승인으로 해석하지 마라.

작업 종료 보고에는 다음을 포함해라.
- 실제 수정한 두 문서
- 경로 정정 여부
- R1의 frozen-surface 및 두 provider 유료 재-qualification 비용을 명시했는지
- Claude provider red-team 링크 추가 여부
- discovery/trace 상태를 분리했는지
- 실행한 local-only 검증 결과
- primary/provider/network/paid call을 실행하지 않았다는 사실
```

## Entry Links

- [[docs/feedback/claude_continuation_prompt_20260807|Claude continuation prompt to correct]]
- [[docs/feedback/codex_mcp_handoff_moc_20260807|Current handoff MOC]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Review that triggered this reply]]
