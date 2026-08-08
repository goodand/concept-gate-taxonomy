---
aliases:
  - Phase C Artifact Manifest
tags:
  - doc/manifest
  - stage/handoff
---

# Phase C Artifact Manifest — config·pilot·probe classification

이 문서는 `DESIGN_DECISION_orphan_taxonomy_and_worktree_qualified_links_20260807`
Q1의 "individual classification manifest + selective navigation linking"을
적용한 결과다. 38개 config/JSON artifact를 **각각 직접 읽어**(내용을 프로그램으로
추출, 파일명 추측 아님) 분류했다. `navigation_policy: direct_link`인 항목만
MOC에서 직접 링크한다 — 나머지는 이 manifest가 유일한 진입점이다.

```
개별 분류 필요 ≠ 개별 Markdown wikilink 필요
```

원본 파일은 이 정리로 이동·이름 변경하지 않았다. `git status --short`로
`results/*.json`, `phase_c_*.json` 무변경 확인.

## 그룹 A — 현재 유효 qualification (canonical, direct_link)

| path | classification | navigation_reason |
|---|---|---|
| `phase_c_codex_mcp_v7_config.json` | canonical | 현재 Codex qualification config |
| `phase_c_claude_mcp_surface_v2_config.json` | canonical | 현재 Claude qualification config |
| `results/live_pilot_codex_mcp_v7.json` | canonical | 현재 Codex qualification artifact, `qualification.passed=true` |
| `results/live_pilot_claude_mcp_surface_v2.json` | canonical | 현재 Claude qualification artifact, `qualification.passed=true`, `R_STATIC`/`R_DYNAMIC` outcome failure 보존 |

## 그룹 B — 이미 개별 인용된 historical artifact (direct_link, Q1.2 예외)

MOC 본문이 이미 서사적으로 이 파일들을 개별 인용하고 있다 —
링크 개수의 대칭성이 아니라 **link reason의 존재**가 기준이므로 유지한다.

```yaml
- path: results/live_pilot_codex_mcp_v5.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v7.json
  navigation_policy: direct_link
  navigation_reason: R_STATIC failure evidence (post-follow ambiguity that motivated v6)
  classification_basis: kind=live-subject-pilot, R_STATIC 셀만 V1로 실패, 나머지 3셀 valid — Amendment 20의 원인 사례

- path: results/live_pilot_codex_mcp_v5_vehicle.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v6.json
  navigation_policy: direct_link
  navigation_reason: proves the MCP tool reached the host but is intentionally incomplete (one-cell vehicle probe)
  classification_basis: kind=live-subject-pilot, n_runs=1, qualification.passed=true (vehicle probe only, not full matrix)

- path: results/live_pilot_codex_mcp_v6.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v7.json
  navigation_policy: direct_link
  navigation_reason: passes the stated Codex qualification matrix; direct predecessor to v7
  classification_basis: kind=live-subject-pilot, n_runs=4, qualification.passed=true

- path: results/live_pilot_claude_mcp_surface_v1.json
  classification: archive
  provenance_group: claude_mcp_surface_pilot_series
  superseded_by: results/live_pilot_claude_mcp_surface_v2.json
  navigation_policy: direct_link
  navigation_reason: passes the same HD01 x 4 boundary after Codex v6; direct predecessor to v2
  classification_basis: kind=live-subject-pilot, n_runs=4, qualification.passed=true, config_file=phase_c_claude_mcp_surface_config.json

- path: results/redteam_provider_isolation.json
  classification: canonical
  provenance_group: n/a (diagnostic, not a pilot attempt)
  navigation_policy: direct_link
  navigation_reason: Claude surface v2의 seatbelt-v2 preflight를 게이팅하는 실행 전제(run_live_phase_c.py _assert_provider_preflight) — frequently needed diagnostic artifact
  classification_basis: n_probes=33, hardened_profile_leaks=[], hardened_profile_passed=true, v1 historical leak 2건 보존
```

## 그룹 C — Codex MCP live-pilot 시리즈 (archive, manifest_only)

Q1.1의 허용 예("Codex MCP live-pilot history v1→v7")에 해당한다 — 동일 실행
계보를 공유하고 관계가 명시적이다. `v7`은 그룹 A로 이미 direct_link.

```yaml
- path: results/live_pilot_codex_mcp_v1.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v2.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, qualification.passed=false, n_runs=4.
    Amendment 16 — 4/4 V1, MCP call이 approval policy로 취소됨(model 호출 전 단계).

- path: results/live_pilot_codex_mcp_v2.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v3.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, qualification.passed=false.
    Amendment 17 — model 호출 전 V1, --ask-for-approval이 codex exec subcommand
    option이 아니라 parser exit 2.

- path: results/live_pilot_codex_mcp_v3.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v4_vehicle.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, qualification.passed=false.
    Amendment 18 — valid config override 사용했지만 MCP call이 여전히
    user-cancelled로 종료.

- path: results/live_pilot_codex_mcp_v4_vehicle.json
  classification: archive
  provenance_group: codex_mcp_live_pilot_series
  superseded_by: results/live_pilot_codex_mcp_v5_vehicle.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, n_runs=1, qualification.passed=false.
    Amendment 19 — --sandbox와 --approve-for-me 동시 사용 불가로 model 호출
    전 parser exit 2.
```

## 그룹 D — Codex/Claude non-MCP 초기 adapter 시리즈 (archive, manifest_only)

MCP-only 분리(Amendment 15) 이전, Seatbelt-v2 기반 초기 adapter 시도.

```yaml
- path: results/live_pilot_codex_v2.json
  classification: archive
  provenance_group: pre_mcp_adapter_series
  superseded_by: results/live_pilot_codex_mcp_v1.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, provider=codex-cli(non-MCP), qualification.passed=false.
    v2 profile이 ~/.codex 전체를 deny해 OAuth binary/token까지 막혀 provider
    launch가 exit 71로 실패(Amendment 13). MCP-only adapter로 대체됨.

- path: results/live_pilot_claude.json
  classification: archive
  provenance_group: pre_mcp_adapter_series
  superseded_by: results/live_pilot_claude_attempt2.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, config_file=phase_c_claude_config.json,
    qualification.passed=false. adapter schema validation 실패(main
    answer_text, retrieval-only contract_version 누락).

- path: results/live_pilot_claude_attempt2.json
  classification: archive
  provenance_group: pre_mcp_adapter_series
  superseded_by: results/live_pilot_claude_attempt3.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, qualification.passed=false. Claude CLI
    --json-schema parser가 $schema draft URI를 몰라 모델 호출 전 거부
    (Amendment 14).

- path: results/live_pilot_claude_attempt3.json
  classification: archive
  provenance_group: pre_mcp_adapter_series
  superseded_by: results/live_pilot_claude_mcp_surface_v1.json
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, qualification.passed=**true**, n_runs=4.
    F8(pre-primary findings) — 두 개의 통과한 Claude qualification이 동시에
    유효해 보이는 문제의 실물 사례; superseded 표시 없이 남아 있었음. MCP
    surface 분리로 v1이 그 자리를 대체함.
```

## 그룹 E — 레거시 v1 실험(provider adapter 이전) pilot/primary attempt (archive, manifest_only)

```yaml
- path: results/live_pilot.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-pilot, provider=codex-cli, n_runs=4. 최초 v1 pilot,
    Amendment 4가 기록한 소켓 경로 수정 이전의 원본 시도.

- path: results/live_pilot_attempt2.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 — 라벨 오류, 실제로는 pilot attempt).
    n_runs=4. AF_UNIX socket 경로 수정 뒤에도 Codex child가 tool action
    0건인 채 exit 1(Amendment 5).

- path: results/live_pilot_attempt3.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. response-format
    validator가 contract_version schema에 type 누락으로 400 거부
    (Amendment 6).

- path: results/live_pilot_attempt4.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. main subject Codex
    final response까지 처음 도달했으나 input manifest가 mutable output
    directory를 drift로 오분류(Amendment 7).

- path: results/live_pilot_attempt6.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. Codex inner sandbox가
    outer Seatbelt 안에서 nested-sandbox 충돌로 실패(Amendment 9).

- path: results/live_pilot_attempt7.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. 최초로 host-owned
    action을 가진 valid live trace(Amendment 10) — qualification boundary는
    충족했으나 static arm V1으로 후속 amendment 유발.

- path: results/live_pilot_attempt8.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. S_STATIC/S_DYNAMIC
    full hard gate 통과, R subagent가 read-range containment 불일치로 C3
    (Amendment 11).

- path: results/live_pilot_attempt9.json
  classification: archive
  provenance_group: legacy_v1_pilot_and_primary_attempts
  navigation_policy: manifest_only
  classification_basis: >
    kind=live-subject-primary (F8 라벨 오류). n_runs=4. containment rule
    수정 후 attempt — v2 provider-isolation red-team 착수 직전 마지막 v1
    surface 기록.
```

**F8 라벨 오류 고지**(`claude_redteam_preprimary_findings_20260807.md` §F8):
`attempt2~9` 7건 전부 `kind: live-subject-primary`이지만 내용은 pilot
attempt다. 이 manifest는 그 오류를 **고치지 않고**(불변 결과물 원칙)
`classification_basis`에 매번 명시해 라벨과 실제 역할을 분리했다.

## 그룹 F — 하네스 smoke/calibration 중간 산출물 (archive, manifest_only)

```yaml
- path: results/smoke.json
  classification: archive
  provenance_group: harness_smoke_and_payload_intermediates
  navigation_policy: manifest_only
  classification_basis: kind=development-smoke, n_runs=36. Phase B scripted-controller smoke, arm 효과 주장에 쓰지 않음.

- path: results/smoke_traces.json
  classification: archive
  provenance_group: harness_smoke_and_payload_intermediates
  navigation_policy: manifest_only
  classification_basis: raw trace list(36 items), smoke.json이 요약하는 원본.

- path: results/_smoke_payload.json
  classification: archive
  provenance_group: harness_smoke_and_payload_intermediates
  navigation_policy: manifest_only
  classification_basis: clean-judge 입력 payload list(36 items), smoke run의 중간 산출물.

- path: results/_calibration_payload.json
  classification: archive
  provenance_group: harness_smoke_and_payload_intermediates
  navigation_policy: manifest_only
  classification_basis: >
    trace/gold/case 키를 가진 clean-judge 입력 payload — calibration.json(이미
    linked)이 요약하는 원본. calibration.json이 사실상 이 파일의 canonical
    reference 역할을 한다.
```

## 그룹 G — superseded config 10종 (archive, manifest_only)

`phase_c_codex_mcp_v7_config.json`, `phase_c_claude_mcp_surface_v2_config.json`은
그룹 A에서 이미 direct_link.

```yaml
- path: phase_c_live_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v7_config.json
  navigation_policy: manifest_only
  classification_basis: >
    provider=codex-cli, sandbox=v1 profile. 재감사 A1에서 primary spec 앵커
    부재로 fail-closed 확인됨 — CLI 기본 config였으나 이제 무자격.

- path: phase_c_codex_v2_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_config.json
  navigation_policy: manifest_only
  classification_basis: provider=codex-cli, seatbelt-v2. ~/.codex 전체 deny로 OAuth 실패(Amendment 15), MCP-only adapter로 대체.

- path: phase_c_codex_mcp_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v2_config.json
  navigation_policy: manifest_only
  classification_basis: provider=codex-mcp-cli v1. approval policy가 MCP call을 취소.

- path: phase_c_codex_mcp_v2_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v3_config.json
  navigation_policy: manifest_only
  classification_basis: v1 MCP call이 approval-cancelled, --ask-for-approval이 유효 subcommand option 아님.

- path: phase_c_codex_mcp_v3_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v4_config.json
  navigation_policy: manifest_only
  classification_basis: valid config override 사용, 그러나 여전히 approval-cancelled.

- path: phase_c_codex_mcp_v4_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v5_config.json
  navigation_policy: manifest_only
  classification_basis: one-cell vehicle probe로 host action 기록 확인 시도, --sandbox+--approve-for-me 조합 불가로 parser exit 2.

- path: phase_c_codex_mcp_v5_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v6_config.json
  navigation_policy: manifest_only
  classification_basis: auto-approval 모드로 transport 통과, R_STATIC만 post-follow 모호성으로 V1.

- path: phase_c_codex_mcp_v6_config.json
  classification: archive
  provenance_group: codex_config_series
  superseded_by: phase_c_codex_mcp_v7_config.json
  navigation_policy: manifest_only
  classification_basis: static_next 결정론적 전이로 R_STATIC 해결, pre-primary 재감사(Amendment 21) 이전 표면.

- path: phase_c_claude_config.json
  classification: archive
  provenance_group: claude_config_series
  superseded_by: phase_c_claude_mcp_surface_config.json
  navigation_policy: manifest_only
  classification_basis: provider=claude-cli, seatbelt-v2, non-MCP. Amendment 15 이후 MCP-surface로 대체.

- path: phase_c_claude_mcp_surface_config.json
  classification: archive
  provenance_group: claude_config_series
  superseded_by: phase_c_claude_mcp_surface_v2_config.json
  navigation_policy: manifest_only
  classification_basis: Codex v6 재-qualification 이후 공유 frozen surface로 재-qualify한 v1 표면. Amendment 21로 v2에 자리 넘김.
```

## 요약

| 그룹 | 건수 | navigation_policy |
|---|---:|---|
| A — 현재 canonical | 4 | direct_link |
| B — 개별 인용 historical | 5 | direct_link |
| C — Codex MCP live-pilot 계보 | 4 | manifest_only |
| D — pre-MCP adapter 계보 | 4 | manifest_only |
| E — legacy v1 실험 계보 | 8 | manifest_only |
| F — smoke/calibration 중간산출물 | 4 | manifest_only |
| G — superseded config | 10 | manifest_only |
| **합계** | **39*** | — |

\* 요청서의 "38건" 재확인 결과 실제로는 39건(config 12 + results 27, `redteam_provider_isolation.json` 포함)이었다 — 요청서 집계 당시 이 파일을 별도로 세지 않았을 가능성이 있다. 이 차이는 D2(vault 전체 재산출)의 관측이 아니라 이번 개별 확인으로 밝혀진 것이며, 최종 개별 분류 39건에는 영향을 주지 않는다.

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Handoff MOC — direct_link 대상만 여기서 진입]]
- [[notes/audits/vault/DESIGN_DECISION_orphan_taxonomy_and_worktree_qualified_links_20260807|이 manifest가 적용하는 판정]]
- [[docs/feedback/claude_redteam_preprimary_findings_20260807|F8 — attempt2-9 라벨 오류 원 발견]]
