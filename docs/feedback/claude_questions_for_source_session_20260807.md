---
aliases:
  - Claude Questions For Source Session
  - 구현 세션에 보내는 요청·질문 프롬프트
tags:
  - doc/prompt
  - stage/handoff
  - status/active
---

# 구현 세션에 보내는 요청·질문 프롬프트

이 문서가 종합한 재감사·목적 계층·성과 문서들의 **출처는 이 세션이 아니라
`run_live_phase_c.py`, `PROVIDER_ADAPTERS.md`, qualification log를 만든 구현
세션**이다. 아래 프롬프트를 그 세션(또는 그 작업을 이어받는 새 세션)에
전달하기 위해 작성했다. 요청과 질문을 분리했다 — 요청은 구현 세션이 바로
착수할 수 있는 것이고, 질문은 이 세션이 판단할 권한이 없는 것이다.

```text
너는 handoff dynamic-controller 실험(run_live_phase_c.py,
PROVIDER_ADAPTERS.md, qualification log)의 원 구현 세션이거나 그 작업을
이어받는 세션이다. 독립 red-team 재감사(Amendment 21)와 그 후속 검토가
남긴 요청과 질문에 답하고, 요청 중 사용자가 승인한 것만 착수해라.

Workspace:
/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt

먼저 아래를 순서대로 읽어라. canonical 코드/artifact를 직접 열어 확인하고,
이 프롬프트의 서술을 신뢰하지 마라.

1. docs/feedback/codex_mcp_handoff_moc_20260807.md
2. docs/feedback/codex_mcp_handoff_qualification_log_20260807.md
3. docs/feedback/claude_redteam_preprimary_reaudit_20260807.md
4. docs/EVIDENCE_BOUNDED_AGENCY_TARGETS.md
5. docs/HANDOFF_EXPERIMENT_KEY_ACHIEVEMENT_20260807.md
6. docs/feedback/redteam_handoff_repair_loop_20260806.md
7. experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md
   (Amendment 1 "남긴 것", Amendment 21)
8. experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS.md
9. experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py
10. experiments/2026-08-07_handoff_dynamic_controller/_evaluator.py
11. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_codex_mcp_v7.json
12. experiments/2026-08-07_handoff_dynamic_controller/results/live_pilot_claude_mcp_surface_v2.json

절대 금지 (이번 세션 전체):
- primary, pilot, provider CLI, MCP, network, 유료 model call을 실행하지 마라.
- PRIMARY_AUTHORIZATION.json을 만들지 마라.
- qualification artifact, ledger, calibration, red-team 결과, gold, corpus를
  수정하지 마라.
- frozen surface(run_live_phase_c.py, _evaluator.py, test_*.py, config들,
  hidden_gold/gold.json 등)를 아래 "요청 A/B"의 명시 승인 없이 고치지 마라.
- 커밋하지 마라.

======================================================================
요청할 것 — 구현 세션이 실제로 착수할 수 있는 작업
======================================================================

요청 A. R1 수정 — 사용자 명시 승인 전에는 설계·재현·문서화만
--------------------------------------------------------------
재감사가 실제로 통과시킨 공격: qualification artifact의 outcome 지표(점수,
failure_codes)만 고치고 qualification_ledger.jsonl의 sha256을 재계산해
넣으면 primary 전제 검사를 통과한다. matrix/provider/config는 건드리지
않는다.

요청:
1. qualification_ledger.jsonl 행에 artifact 전체 hash뿐 아니라 셀별
   judged_payload_sha256과 full_hard_gate를 추가로 고정할지 설계해라.
2. 이미 artifact가 그 값을 들고 있으므로 새 계산은 필요 없다 — ledger
   append 시점에 셀 목록을 순회해 dict로 담으면 된다.
3. positive test(변경 없는 artifact가 여전히 통과)와 negative test(점수만
   바꾸고 ledger를 재결속해도 거부)를 먼저 짜라.
4. run_live_phase_c.py, _evaluator.py, test_preprimary_gates.py는 전부
   frozen surface다. 이 파일들을 고치면 현재 v7/surface-v2 qualification
   artifact가 즉시 stale가 되고, calibration/red-team 재실행만으로는
   부족하며 두 provider의 유료 live qualification pilot을 다시 실행해야
   primary 전제가 회복된다는 것을 설계 문서에 명시해라.
5. 위 1-4는 **설계와 코드 diff 초안까지만** 진행하고, 실제 코드/config/
   frozen-surface 파일을 수정하거나 재-qualification pilot을 실행하는
   것은 사용자의 명시 승인이 있을 때까지 하지 마라.

요청 B. R2 수정 — ledger의 matrix를 config 선언이 아니라 실행값에서 유도
--------------------------------------------------------------
_record_qualification()이 out["config"]["pilot"]에서 arms/case_ids를 읽어
ledger에 적는다. `--arm`/`--case-id`로 축소 실행해도 ledger에는 config가
선언한 전체 matrix가 그대로 기록된다. primary 게이트 자체는 이미 막지만
(n_runs/per_arm 불일치로 거부), ledger를 읽는 사람에게는 부분 실행이 완전
실행으로 보인다.

요청:
1. ledger의 arms/case_ids를 out["per_arm"]과 out["results"]에서 실제
   실행된 셀 집합으로부터 유도하도록 설계해라
   (예: sorted(out["per_arm"]), sorted({r["case_id"] for r in
   out["results"]})).
2. 축소 실행이 축소된 ledger 행을 남기는지(음성), 완전 실행이 4-arm 행을
   남기는지(양성) 짝 테스트를 설계해라.
3. 요청 A와 같은 frozen-surface 재-qualification 비용이 적용된다. 승인
   전에는 설계까지만 하라.

요청 C. attempt ledger에 종결 상태 기록 (frozen surface 변경 아님인지 먼저
확인)
--------------------------------------------------------------
_claim_primary_attempt()가 시작 시점에 {"status": "started"}만 append한다.
완료/실패/중단을 ledger만으로 구별할 수 없다.

요청:
1. run_phase()가 primary 실행을 마친 뒤(성공이든 실패든) 같은 authorization
   digest로 종결 레코드를 추가로 append할 수 있는지 설계해라. append-only
   불변식(기존 시작 레코드를 절대 덮어쓰지 않음)을 유지해라.
2. 이 변경이 run_live_phase_c.py를 건드리므로 frozen surface 재
   -qualification이 필요한지 스스로 판정하고 명시해라.
3. 코드 변경은 사용자 승인 후로 미뤄라.

요청 D. 문서 drift 정정 — 즉시 해도 되는 저위험 작업
--------------------------------------------------------------
frozen surface나 코드를 건드리지 않는 순수 문서 수정이므로 사용자 승인 없이
바로 해도 된다. 단 커밋은 하지 마라.

1. PROVIDER_ADAPTERS.md `:154`, `:190`의 "91 passed"를 현재 실측
   "107 passed"로 갱신해라. (실측: `python3 -m pytest -q test_preprimary_gates.py
   test_protocol.py test_live_phase_c.py test_live_phase_c_claude.py
   test_codex_mcp_provider.py` → 107 passed.)
2. PROVIDER_ADAPTERS.md §7(`:150-160`)의 권장 실행 순서가 아직
   phase_c_codex_v2_config.json / phase_c_claude_config.json qualification을
   가리킨다. 두 config는 primary spec 앵커가 없어 fail-closed다(재감사
   A1 전수 확인). 현재 순서는 PREREGISTRATION.md Amendment 21이 갖고
   있으므로 그쪽을 가리키도록 고쳐라.
3. codex_mcp_handoff_qualification_log_20260807.md "Files A Cold-Start Agent
   Must Read First" 목록에서 항목 번호 7, 8이 각각 두 번 나온다
   (`:407,409`와 `:411,412`). 번호를 순차로 다시 매겨라.
4. 같은 로그 `:36`의 F4 상태를 "Controlled"로 적고 있다. 현재는
   arm_effect_estimable=false / n_per_cell=1이 기계 필드로 강제되므로
   (재감사 A9), "Resolved: machine-enforced field" 수준으로 갱신할지
   검토해라 — "Controlled"가 실제보다 약하게 읽힌다.

======================================================================
질문할 것 — 이 세션이 판단할 권한이 없는 것
======================================================================

질문 1. R1/R2 착수 시점
R1/R2는 primary를 막고 있는 결함이 아니라 승인 이후에나 유효해지는 강화다.
지금 재-qualification 비용(두 provider 유료 pilot 재실행)을 들여 먼저
고칠지, 아니면 primary 승인·실행까지 미룬 뒤 다음 qualification
version(v8/surface-v3)에 함께 접어 넣을지 사용자가 정해야 한다. 어느 쪽을
원하는가?

질문 2. PRIMARY_AUTHORIZATION.json의 authorized_by
현재 스키마는 authorized_by를 비어 있지 않은 자유 문자열로만 검증한다
(신원 암호학적 증명 없음, 재감사 "PRIMARY_AUTHORIZATION.json의 한계" 절).
이 필드에 실제로 무엇을 적어야 하는지(이름, 이메일, 다른 식별자) 지정된
규칙이 있는가, 아니면 자유 문자열로 계속 둘 것인가?

질문 3. attempt ledger 종결 기록의 우선순위
요청 C(종결 상태 기록)를 primary 최초 실행 전에 반드시 넣어야 하는
전제조건으로 볼 것인가, 아니면 "started"만으로 현재는 충분하다고 볼 것인가?

질문 4. CLAUDE_CONFIG_DIR 격리
PROVIDER_ADAPTERS.md `:130-134`이 OAuth 인증에서는 CLAUDE_CONFIG_DIR
격리가 성립하지 않음을 실측했고, ANTHROPIC_API_KEY 인증이면 격리가 될
가능성이 있으나 검증하지 않았다고 적혀 있다. 이 잔여 노출(~/.claude.json
계정/설정 메타데이터)을 닫기 위해 API key 인증 경로를 추가로 검증할
가치가 있다고 보는가, 아니면 현재 상태를 영구 잔여 위험으로 받아들이는가?

질문 5. 열린 설계 문제 두 건의 재개 여부
redteam_handoff_repair_loop_20260806.md §7이 아래 두 항목을 판정 대기로
남겨 두었다.
  - 경로 C(`:49`, `:121`): mention 채널(백틱 인용 등)에 G2/G3 가드를
    적용할지, 아니면 mention을 도달성 계산에서 아예 뺄지. 정밀도와 게임
    방지가 충돌한다고 문서가 명시한다.
  - 구멍 7(`:123`): dangling 참조 해소 시 대상 파일의 최소 크기(0바이트
    stub 방지)를 요구할지.
이 두 판정을 지금 재개할 것인가, 아니면 현재 실험 완료 후로 미룰 것인가?

질문 6. AST 메타 테스트 재뮤테이션 검증
같은 문서 §6(`:118-119`)에 따르면 "G4 호출부 삭제" 뮤테이션이 원래 메타
테스트를 공허하게 통과시킨 결함을 ast.Call 검사로 고쳤지만, **교체본 자체의
재뮤테이션 검증은 사용자 중단으로 실행되지 않았다.** 이 검증을 지금
재개해도 되는가? (frozen surface에 걸리는 코드 변경이 아니라 기존 테스트를
그대로 재실행하는 것이라면 승인 없이도 가능한지 판단해 달라.)

질문 7. DS07 게이트/gold 판정
PREREGISTRATION.md `:292-295`에 discovery 조건 DS07이 스크립트 controller
4-arm 전부에서 D0가 나온 채 열려 있다. "게이트가 옳고 controller가
handoff read를 생략했다"인지 "gold가 과하게 엄격하다"인지 판정이 필요하다고
적혀 있다. 이 판정을 누가, 언제 내리는가? 이번 실험의 primary 실행 전에
반드시 닫아야 하는 전제조건인가, 아니면 별도 케이스로 분리해도 되는가?

======================================================================
기록 규칙
======================================================================
- 요청 A/B/C에 대한 사용자 답변과 착수 여부는
  docs/feedback/codex_mcp_handoff_qualification_log_20260807.md에
  이슈·해결 근거·해결 유무 형식으로 추가해라.
- 질문 1-7에 대한 답변은 이 문서 하단에 "## 답변" 절을 만들어 날짜와 함께
  누적 기록해라. 질문 문항을 지우거나 답변으로 바꿔쓰지 마라.
- 새로 만든 파일은 docs/feedback/codex_mcp_handoff_moc_20260807.md에
  wikilink로 추가해라.

======================================================================
작업 종료 보고에 포함할 것
======================================================================
- 요청 A/B/C 중 실제 착수한 것과 승인 상태
- 요청 D 문서 수정 적용 여부
- 질문 1-7에 대한 답변 또는 "미결" 표시
- primary/provider/network/paid call을 실행하지 않았다는 사실
- 커밋하지 않았다는 사실
```

## 답변 — 2026-08-07

사용자가 요청 A/B/C/D와 질문 1-7 전체에 답했다. 원 요청/질문 문항은 위에
그대로 둔다.

### 요청 A/B/C 승인 범위

**설계·공격 재현 절차·짝 테스트 설계까지만 승인. frozen surface의 실제
코드·테스트·config 수정은 아직 미승인.** patch proposal 또는 별도 설계
문서는 작성 가능. primary/pilot/provider/MCP/network/유료 호출 금지.

→ 착수: [[docs/feedback/design_proposal_v8_v3_R1_R2_attempt_ledger_20260807|R1/R2/attempt-ledger 종결 기록 설계 제안]].
diff는 문서 안에만 있고 어떤 실제 파일에도 적용하지 않았다
(`git status --short`로 `run_live_phase_c.py`/`_evaluator.py`/
`test_preprimary_gates.py`/qualification artifact/ledger 미변경 확인).

### 요청 D — 즉시 문서 수정

승인대로 4건 모두 즉시 적용, 커밋하지 않음.

1. `PROVIDER_ADAPTERS.md` §7에 "2026-08-07 갱신" 안내 블록 추가 — "91
   passed"를 실측 "107 passed"로 갱신하고, 기존 §7 6단계는 Amendment 12
   시점 historical 기록으로 표시.
2. 같은 절의 권장 실행 순서를 Amendment 21 현재 v7/v2 절차로 교체(안내
   블록 안에 명시).
3. qualification log의 "Files A Cold-Start Agent Must Read First" 목록
   번호 중복(`7,8`이 두 번)을 `1-11` 순차로 재정렬.
4. F4 상태를 `Resolved: machine-enforced non-estimability fields`로 갱신
   하되 "retrieval 성능이나 arm 효과가 해결됐다는 뜻이 아니다"를 병기.

두 파일 모두 `_evaluator.py`의 `FROZEN_SURFACE_FILES`에 없음을 확인하고
수정했다 — drift 없음.

### 질문 1 — R1/R2 착수 시점

**결정: R1/R2/attempt-ledger 종결 기록(요청 C)을 Codex v8 / Claude
surface v3로 묶어 primary 전에 한 번만 처리.** 순서는 설계 → 묶음 →
calibration → red-team → 전체 local test → v8 qualification → v3
qualification → 독립 재감사 → 그 뒤에만 primary 승인 판단. 이번 답변은
새 버전 **설계 착수만** 승인하며 유료 재-qualification은 승인하지 않는다.
현재 v7/v2 상태에서는 primary를 실행하지 않는다.
→ 문서: [[docs/feedback/design_proposal_v8_v3_R1_R2_attempt_ledger_20260807]].

### 질문 2 — authorized_by 규칙

**결정:** 자유 문자열 방치 대신 최소 형식 `authorized_by: "user:jaehyuntak"`
사용. 이 값은 신원의 암호학적 증명이 아니라 자기신고 식별자이며, 문서·코드
어디에서도 `verified identity`라고 부르지 않는다. 가능하면 후속 스키마에
`authorization_id`(재사용 불가 결정 ID), `authorized_at`(timezone 포함),
`decision_record`(승인 근거 문서 canonical path), `decision_record_sha256`,
`config_sha256`, `qualification_sha256`, `matrix`, `max_attempts`를 추가한다.
이메일·API credential을 identity로 쓰지 않는다. 외부 서명 또는 Git
signature 도입 전까지 `authorized_by`는 감사용 표시일 뿐 신원 증명이
아니다. — **이 스키마 확장은 요청 C(attempt ledger 종결 기록)와 같은
frozen-surface 변경이므로 v8/v3 설계에 포함**시켜 별도로 재-qualification을
반복하지 않는다.

### 질문 3 — attempt ledger 종결 기록

**primary 최초 실행 전 필수 조건.** append-only로 `attempt_started` /
`attempt_completed` / `attempt_failed` / `attempt_interrupted` 이벤트를
같은 `authorization_sha256`+`attempt_id`로 구별해 기록한다. 기존 started
행은 절대 수정·덮어쓰기 하지 않는다. `run_live_phase_c.py`를 건드리므로
frozen-surface 변경 — R1/R2와 함께 v8/surface-v3에 묶어 한 번만
재-qualification한다.
→ 설계: [[docs/feedback/design_proposal_v8_v3_R1_R2_attempt_ledger_20260807]]
"요청 C" 절.

### 질문 4 — CLAUDE_CONFIG_DIR 격리

**현재 실험의 선행조건으로 추가하지 않는다.** hardened v2가 transcript·
프로젝트 세션 노출을 이미 차단했고, 남은 `~/.claude.json` 노출은 계정·설정
메타데이터 수준으로 기록돼 있다. API key 인증 도입은 credential 취급과
provider 조건을 바꿔 현재 실험의 독립변수에 새 혼입을 만든다. 조치:

- 현재 실험에서는 documented residual risk로 유지(`PROVIDER_ADAPTERS.md`
  §6 그대로 둔다).
- primary 결과를 보안 격리 증명으로 주장하지 않는다.
- 다중 사용자·적대적 코드 실행 환경 배포 전에는 별도 security experiment로
  disposable OS account/container + API-key isolation을 검증한다.
- 지금 API key/credential을 복사·출력하지 않는다 — 이 세션에서 그런 시도
  없음.

### 질문 5 — mention 채널과 0바이트 stub

**현재 dynamic-controller primary의 frozen surface에는 섞지 않는다.**
handoff repair/evaluation harness의 다음 버전에서 별도 판정한다. mention은
structural reachability edge로 인정하지 않고 referral hint로만 분류하며,
G2/G3를 링크와 동일하게 적용하지 않는다. link→mention 변환으로 finding만
감소하면 `metric-fake`/`representation-only change`로 기록한다. 0바이트
stub은 단순 크기 하한 대신 manifest 포함 + non-empty content-or-canonical-pointer
+ content hash + authority class + parse 가능 여부의 논리곱을 요구한다.
→ 설계: [[docs/feedback/design_decision_mention_channel_and_stub_floor_20260807]].

### 질문 6 — AST 메타 테스트 재뮤테이션

**즉시 재개 승인 — 이번 답변에서 실행 완료.** `/private/tmp/ast-remut`에
`scripts/handoff_repair_loop.py` + `test_handoff_repair_loop.py` 격리
복사본을 만들어 실행했다(실제 워크트리 파일은 미변경, `git status --short`
확인). 결과:

1. baseline(뮤테이션 전): 2 passed.
2. `assert_input_not_narrowed(baseline_state)` 호출부를 구문상 유효한
   `pass`로 치환(byte diff 확인, `ast.parse` 재확인) → 재실행:
   `[G4-assert_input_not_narrowed] FAILED`, `[G4-tracked_file_count] PASSED`.
3. 원본 복원(byte-identical `diff` 확인) → 2 passed.
4. `tracked_file_count()`의 두 호출부(`:178`,`:285`) 모두 제거 → 재실행:
   `[G4-tracked_file_count] FAILED`, `[G4-assert_input_not_narrowed] PASSED`.
5. 원본 복원 → 전체 suite **12 passed**.

**결론: 이 메타 테스트는 실효적이다.** 두 guard 함수 각각을 독립적으로
검출했고, 원본 복원 시 항상 정상 통과했다. "미검증" 상태를 닫는다.
`redteam_handoff_repair_loop_20260806.md` §6-7을 갱신해 반영했다.

### 질문 7 — DS07 gate/gold 판정

**primary 전에 반드시 판정하거나 사전등록 amendment로 명시 제외해야 하는
전제조건.** 판정자는 handoff producer가 아닌 독립 curator이며 arm별
결과·점수를 보지 않은 상태에서 canonical source와 public question만 읽고
판정한다. **이 세션은 이미 arm별 결과(재감사 과정에서 두 qualification
artifact의 `results`/`traces`를 전부 읽었음)를 봤으므로 판정 자격이
없다** — 이 자격 배제를 명시적으로 기록했다. 판정 프로토콜만 설계했고
실제 판정은 아직 arm 결과에 노출되지 않은 별도 세션/사람에게 넘긴다.
판정 전에는 DS07을 arm 효과 추정에 쓰지 않는다.
→ 설계: [[docs/feedback/ds07_independent_curator_protocol_20260807]].

## Entry Links

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Current handoff MOC]]
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Qualification log — record answers here]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 reaudit — source of requests A/B]]
- [[docs/feedback/redteam_handoff_repair_loop_20260806|Source of open design questions 5-6]]
- [[docs/EVIDENCE_BOUNDED_AGENCY_TARGETS|Evidence-bounded agency targets — source of request C rationale]]
- [[docs/HANDOFF_EXPERIMENT_KEY_ACHIEVEMENT_20260807|Key achievement synthesis]]
