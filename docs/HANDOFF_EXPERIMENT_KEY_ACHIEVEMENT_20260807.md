---
aliases:
  - Handoff Experiment Key Achievement
  - 가장 큰 성과 — 측정 가능한 안전 계약으로의 전환
tags:
  - doc/concept
  - stage/handoff
---

# 가장 큰 성과 — 검색 성능이 아니라 검증 가능한 계약으로의 전환

이 문서는 세션 종합이며 판정 권위가 아니다. 각 주장에 근거를 붙이고, 근거가
이 실험 자체의 결과인지 상위 설계 근거인지를 구분한다.

## 핵심 문장

> **가장 큰 성과는 검색 성능을 높인 것 자체가 아니라, Agent가 안전하게 작업을
> 이어갈 수 있는 조건을 측정 가능한 계약으로 바꾼 것이다.**

이전에는 "handoff를 잘 읽어라", "백링크를 따라가라", "근거가 충분한지
판단하라" 같은 **지침**이었다. 지금은 이를 검증 가능한 단계로 분리했다.

```
문서 발견
  → canonical 원문 직접 읽기
    → critical evidence 회수
      → 상태·다음 행동 해석
        → 근거가 부족하면 재검색 또는 보류
          → 독립 evaluator 판정
            → 사용자 승인 후 실행
```

이 파이프라인은 선언이 아니라 코드다: 각 화살표가
[[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|근거에 의해 제한되는 자율성]] §2-4가
가리키는 구현 지점(host-owned trace, hard gate 논리곱, primary 승인 게이트)에
대응한다.

## 구체적 성과 — 근거와 함께

### 1. Recall-first 검색 개선 0.688 → 0.812 → 0.958 → 1.000

**이 수치는 이 dynamic-controller 실험 자신의 live 결과가 아니라, 이 실험이
전제로 삼는 상위 설계 근거다.** `PREREGISTRATION.md:39`(DQ4 예측 근거)와
`:274`(Amendment 1, A1-8 static arm 서술 근거)가 인용하는 값으로, 워크스페이스
검색 규율(`CLAUDE.md:181`)에서 온 실측이다. 이 실험의 controller 설계가 그
결과를 **전제**로 세워졌다는 뜻이지, 이 실험의 `HD01 × 4` qualification pilot이
그 수치를 재생산했다는 뜻이 아니다. 두 개를 섞으면 상위 근거를 이 실험 자신의
outcome처럼 보이게 만든다.

### 2. critical claim coverage와 정확 경로 micro Recall — 부분만 100%

**정정** — "100%에 도달했다"를 그대로 옮기면 과장이다. 실측(두 qualification
artifact 8셀 전체):

| 지표 | 실측 |
|---|---|
| `claim_range_exposure_rate` | **8/8 셀 전부 1.0** — 답변한 claim은 전부 자기 read 범위 안에서 지지됐다 |
| `critical_path_recall` | **7/8 셀이 1.0**, Claude v2 `R_STATIC` 1셀은 **0.0** |
| `exact_authority_hit` | **7/8 셀이 True**, 같은 셀 1건 `False` |

즉 **claim exposure(인용 규율)는 100%를 달성**했고, **critical path recall은
전체 100%가 아니다.** 이 구분이 이 실험이 스스로 요구하는 것이다 —
[[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|근거에 의해 제한되는 자율성]] §5가 같은
셀을 `회수 미달성` / `권위 미달성`으로 이미 기록해 두었다. "100%에 도달했다"는
서술은 그 표와 정면으로 어긋나므로, 두 지표를 분리해 적었다.

### 3. 검색과 문맥 해석 분리 — 실패 원인 5종 구별

회수 실패, 권위 오판, 해석 실패, false absence, trace 위반을 구별할 수 있게
됐다. 근거: `_evaluator.py:124-185`의 코드 자체가 실패 코드를
`R1/R2`(회수), `C4/X1`(권위·범위), `state_ok/next_ok/stop_ok`(해석),
`A1`(false absence), `V1`(trace/protocol)로 서로 다른 변수에 담는다. 하나의
pass/fail로 합치지 않는다.

### 4. 폐쇄된 action 계약

grep 재검색(`reformulate_query`), graph walk(`follow_link`), candidate
expansion(`expand_candidates`), read(`read_candidate`), abstain을 여섯 개
행동으로 닫았다(`PREREGISTRATION.md:88-93`). 그 밖의 action은 `C2`.

### 5. host-owned trace

모델이 주장한 trace가 아니라 **host가 실제 search/read/action을 기록**한다.
`LiveToolState.actions`/`reads`/`stop_reason`이 dispatch 시점에 host 쪽에서만
채워진다(`run_live_phase_c.py:176-355`). 재감사가 자기 read 기록 없는 인용,
확장된 범위 인용, guard가 안 받은 terminal 주장 3건을 실제 소켓으로 위조해
각각 `C4`/`X1`/거부됨을 확인했다(`PROVIDER_ADAPTERS.md` §4 Q3).

### 6. gold·evaluator 격리와 clean judge

subject는 gold와 evaluator 소스를 볼 수 없고, 채점은 `-E -X pycache_prefix`
clean subprocess에서 수행된다(`_evaluator.py:293-` 이하). **상한 — 이것은
process 분리를 증명하며 OS 수준 격리를 증명하지 않는다**
(`PREREGISTRATION.md:253`).

### 7. 실제 red-team으로 발견한 공격 5종

forged one-cell qualification, artifact 변조, 약한 config 선택, 승인 없는
primary, output-name 반복 실행 — 전부 원래 F1/F2/F3/F5 공격으로 실행 확인됨
([[docs/feedback/claude_redteam_preprimary_findings_20260807|F1-F9 findings]]).

### 8. Amendment 21 재감사 — A1-A10 전부 차단, F1-F7 재현 0건

[[docs/feedback/claude_redteam_preprimary_reaudit_20260807|재감사]]가 12개
위조 조합, authorization 변조 6종+bool 우회, 8-프로세스 동시 claim 5회 반복
전부 거부를 실측으로 확인했다. **정정할 과장 없음** — 재감사 자신이 이미
"demonstrated defect 0건"과 "잔여 위험 R1-R4"를 분리해 적어 두었고, 이 문서는
그 구분을 그대로 유지한다. R1(score-only rewrite + ledger 재결속)은 여전히
통과한다.

### 9. Codex/Claude 공유 계약

두 provider가 같은 `contract_version`(`handoff-dyn-trace-v1`)과 같은 4-arm
`HD01` qualification 구조를 쓴다(`_contract.py:28`,
`phase_c_codex_mcp_v7_config.json`/`phase_c_claude_mcp_surface_v2_config.json`의
`primary.required_qualification_artifacts`가 서로를 상호 요구). **provider별
결과는 여전히 pool하지 않는다** — `PROVIDER_ADAPTERS.md`가 이를 테스트로
강제한다(`test_claude_results_are_not_poolable_with_codex_results`).

### 10. 발견 성공과 evaluator 통과의 분리

"찾았으니 성공"이라는 오판을 막았다. Claude v2 `R_STATIC`이 실물 사례다 —
`invalid_run=false`, exposure 1.0으로 trace는 유효했으나 authority read가
부족해 hard gate는 실패했다. `discovery incomplete / trace valid`로 분류한다.

## 전체를 한 문장으로

> LLM의 검색과 해석을 신뢰하는 시스템에서, **LLM의 행동을 관측하고 근거·권위·
> 승인을 독립적으로 검증하는 시스템**으로 전환했다.

## 아직 확립되지 않은 것 — 과장 방지

dynamic controller가 static보다 실제로 우수하다는 **성능 효과는 확립되지
않았다.** 지금까지 실행된 것은 두 provider의 `HD01 × 4` qualification
pilot뿐이고, 둘 다 `arm_effect_estimable=false`·`n_per_cell=1`을 기계 필드로
갖는다. 이것은 "성능 우열이 아직 없다"이지 "controller가 효과가 없다"가 아니다
— primary(`8 case × 4 arm`)를 실행하기 전에는 어느 쪽도 말할 수 없다.

이 기반이 Recall 1.0 자체보다 큰 성과라는 판단의 근거는, 성능 수치가 아직
`n=1`이라 신뢰구간이 없는 반면, **오염 없이 그 수치를 측정할 수 있는 조건**
(R1을 제외하면)은 재감사로 검증됐다는 데 있다.

## 근거

- `experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json`
- `experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json`
- `experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md:39,88-93,253,274`
- `experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py:124-185`
- `experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py:176-355`
- `CLAUDE.md:181`
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 재감사]]
- [[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|근거에 의해 제한되는 자율성]]

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/HANDOFF_EXPERIMENT_PURPOSE_HIERARCHY|실험 목적 계층]]
- [[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|근거에 의해 제한되는 자율성]]
- [[docs/feedback/session_synthesis_20260807_empty_guard_and_authorization_chain|공허한 가드·승인 우회 종합]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 재감사]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Phase C 사전등록]]
