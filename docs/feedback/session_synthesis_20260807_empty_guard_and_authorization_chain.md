---
aliases:
  - Empty Guard And Approval Bypass Synthesis
  - 공허한 가드와 실행 승인 우회 체인
tags:
  - doc/knowhow
  - stage/handoff
  - status/verified
---

# 공허한 가드와 실행 승인 우회 체인 — 세션 종합 (2026-08-07)

이 문서는 판정 권위가 아니라 **종합**이다. 모든 주장의 근거는 아래 인용된
canonical 문서와 코드에 있고, 이 문서를 근거로 새 판정을 내리지 않는다.

## 1. 가장 많이 반복된 문제 — 공허한 가드 · 대리 명제

**"검사가 존재한다"는 사실을 "필요한 조건을 실제로 검사한다"는 사실로
착각한 것.** 참인 명제가 필요한 명제를 대신했다.

이 패턴은 11회 기록된 뒤 pre-primary 감사에서 같은 형태가 다시 발견되어
**총 12회**까지 반복됐다. "두 명제를 적어 비교한다" 같은 운영 규율은
**7/7 실패**했다.

근거:

- [`redteam_handoff_repair_loop_20260806.md:98`](redteam_handoff_repair_loop_20260806.md)
  — "P1 11번째" 절 제목이 11회 시점을 못박는다.
- [`claude_redteam_preprimary_findings_20260807.md:241`](claude_redteam_preprimary_findings_20260807.md)
  — "이 저장소가 12회 기록한 패턴 그대로다 — 참인 명제(문자열이 존재한다)가
  필요한 명제(오독이 불가능하다)를 대신하고 있다."
- [`TO_HARNESS_DEVELOPER_verified_knowhow_20260807.md:24`](TO_HARNESS_DEVELOPER_verified_knowhow_20260807.md)
  — "두 명제를 적어 대조하라"는 규율은 7/7 실패했다. 같은 문서 `:10`은
  수록 기준("규율로 해결됐다고 주장하는 것은 뺐다")이다.
  저장소 규율 문서 `CLAUDE.md:121`에도 같은 문장이 있다.

### 대표적인 재발

- 함수가 정의돼 있기만 하고 **호출되지 않았는데** 테스트가 통과했다.
- 가드 **이름이 소스에 존재한다**는 이유로 구현됐다고 판정했다.
- 뮤테이션 문자열이 실제 코드와 맞지 않아 변경이 **전혀 적용되지 않았는데**,
  이를 evaluator가 뮤테이션을 견뎠다는 증거로 해석했다.
- qualification artifact가 **자신이 축소한 matrix를 다시 기준으로 삼아**,
  4-arm 요구를 1-cell로 줄이고도 완전하다고 판정했다.
- `arm_effect_estimable=false` 같은 필요한 **기계 판정** 대신, "효과를
  주장하지 않는다"는 **설명 문자열**만 존재했다.

## 2. 핵심 노하우 — 사람의 규율을 실행 가능한 불변식으로, 그리고 불변식도 공격한다

1. 긍정 테스트만 두지 않는다. 가드가 **실제 위반을 거부하는 음성 테스트**를
   반드시 짝으로 둔다.
2. 함수 이름이나 정의가 아니라 `ast.Call`처럼 **실제 호출**을 검사한다.
3. 뮤테이션 **전후 바이트가 달라졌는지 먼저 확인**한다. 변하지 않았다면
   evaluator PASS가 아니라 **mutation no-op = 하네스 결함**으로 처리한다.
4. **가드 호출부를 삭제하는 뮤테이션**으로 음성 테스트 자체가 공허하지 않은지
   검사한다.
5. evaluator·테스트·config를 **함께 frozen surface에 포함**한다. 새 검사가
   추가됐는데 대응 음성 테스트가 없으면 게이트가 실패해야 한다.
6. import cache나 `.pyc` 오염 가능성이 있으면 in-process 검사로 해결하려 하지
   말고 **clean subprocess와 고정 manifest로 경계를 옮긴다**.

이 과정에서 실제로 **"G4 호출부 삭제" 뮤테이션이 통과**해 메타 테스트까지
공허하다는 사실이 드러났다. 원인은 메타 테스트가 함수 **이름의 존재**만
검사해서 `def` 한 줄이 조건을 만족시킨 것이다 — "정의됐지만 호출되지 않음"을
잡으려던 테스트가 정확히 그 구분을 못 하는 검사를 썼다.
재현: [`redteam_handoff_repair_loop_20260806.md:98-119`](redteam_handoff_repair_loop_20260806.md).

> **항목 2에 대한 미검증 고지 — 이 문서에서 가장 중요한 단서.**
> `ast.Call` 교체본 자체의 **재뮤테이션 검증은 실행되지 않았다**(사용자 중단,
> `redteam_handoff_repair_loop_20260806.md:118-119`, §7 미해결 목록 첫 항목).
> 따라서 "AST 메타 테스트가 실효적이다"는 **아직 검증되지 않은 주장**이다.
> 이 고지를 빼고 항목 2를 노하우로 옮기면, 그 행위 자체가 이 문서가 경고하는
> 바로 그 패턴(수정이 존재한다 → 수정이 작동한다)의 13번째 사례가 된다.

## 3. 가장 위험했던 문제 — 단일 버그가 아니라 실행 승인 우회 **체인**

```
축소·변조된 qualification artifact
  → artifact 자신의 신고를 기준으로 qualification 통과
  → 사용자 승인 없이 primary 실행 가능
  → output 이름을 바꿔 여러 번 실행
  → 유리한 결과만 선택적으로 보고
```

실제로 4-arm qualification을 1-cell로 축소한 **위조 artifact가 primary 전제
검사를 통과했다**. 동시에 qualification 통과와 사용자 승인 사이에는 실행
가능한 승인 장치가 **없었다**.

근거: [`claude_redteam_preprimary_findings_20260807.md:49`](claude_redteam_preprimary_findings_20260807.md)
(F1 — matrix 완전성이 artifact의 자기 신고로 판정된다),
같은 문서 [`:267`](claude_redteam_preprimary_findings_20260807.md)
(F5 — primary 실행 권한이 사용자 의사와 연결돼 있지 않다, **거버넌스 공백**).

## 4. 안전하게 만든 방법 — 강한 가드 하나가 아니라 **독립 앵커의 중첩**

- 요구 matrix의 **소유자를 artifact에서 frozen config spec으로 이동**했다.
- artifact의 `config.pilot` 신고가 spec과 다르면 **즉시 거부**한다.
- qualification artifact 전체 SHA-256을 **외부 ledger에 고정**했다.
- primary 실행에는 별도의 `PRIMARY_AUTHORIZATION.json`이 필요하다.
- 승인은 config hash, qualification hashes, **정확한 matrix**, 최대 실행
  횟수에 결속된다.
- 실행 횟수는 output 이름이 아니라 **authorization digest**로 계산한다.
- 확인·횟수 판정·ledger append를 **하나의 exclusive lock 안에서** 수행한다.
- 테스트와 현재 provider config까지 frozen surface에 넣었다.
- trace의 `actions`/`reads`/`stop_reason`은 모델 출력이 아니라 **host가
  소유**하게 했다.
- 약한 구버전 config **10종을 모두 fail-closed** 처리했다.

## 5. 독립 재감사에서 확인된 것

- 축소 matrix는 **ledger까지 함께 위조해도** 거부
- 6개 필드 × ledger 재결속 여부, 총 **12개 위조 조합 모두** 거부
- authorization 변조 6종과 **boolean 우회**까지 모두 거부
- output 이름을 바꾼 두 번째 실행 거부
- 8개 프로세스 동시 시도 실험을 5회 반복해 **매번 정확히 1개만** 성공
- frozen surface **39개 항목 drift 없음**
- **A1–A10 전체 PASS**, 기존 F1–F7 공격 재현 **0건**

상세 근거: [`claude_redteam_preprimary_reaudit_20260807.md:67`](claude_redteam_preprimary_reaudit_20260807.md)
이하 A1–A10 절.

## 6. 재사용할 핵심 원칙

> **중요한 조건은 문서·문자열·자기 신고로 증명하지 않는다.**
> 독립된 권위 소스에 고정하고, 정상 입력과 공격 입력을 함께 실행해 검증하며,
> **검사기 자체가 실제로 변조됐는지도 확인한다.**

## 7. 과장 금지 — 남은 것

완전 해결로 과장하면 안 된다.

- **R1**: score만 고치고 외부 ledger를 다시 결속하는 공격은 **아직 통과한다**.
- **R4**: attempt ledger도 외부 서명이나 불변 저장소가 없다.
- 항목 2(AST 메타 테스트)의 실효성은 §2 고지대로 **미검증**이다.

현재 상태는 **기존 F1–F7 공격에 대해 안전해진 pre-primary gate**이지, 모든
위조 가능성이 제거됐거나 retrieval 성능이 증명된 상태가 아니다. primary는
여전히 승인되지 않았다.

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/feedback/TO_HARNESS_DEVELOPER_verified_knowhow_20260807|검증된 노하우 (상위 하네스 개발자 수신)]]
- [[docs/feedback/redteam_handoff_repair_loop_20260806|G4 호출부 삭제 뮤테이션 재현]]
- [[docs/feedback/claude_redteam_preprimary_findings_20260807|F1-F9 pre-primary findings]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 재감사 (A1-A10, R1-R4)]]
- [[docs/feedback/codex_mcp_handoff_qualification_log_20260807|Qualification log]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Preregistration (Amendment 21)]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py|Live runner / primary gates]]
- [[experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py|Pre-primary regression tests]]
