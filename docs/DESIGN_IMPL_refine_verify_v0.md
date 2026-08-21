# Refine ↔ Verify v0 — 검증·재사용·의존성·구현 기록

- 작성: 2026-08-22. 선행: 지시 원문(+검증 헤더) · gap 분석(§35 7항목) ·
  survey. 이 문서는 그 셋이 확정한 delta의 **P0 구현 기록**이다
- 게이트: 구현 후 루트 8 passed / 0 failed / 1 blocked, 신규 테스트 21건 포함

## 1. 설계 검증 (이번 회차 추가분)

- **C축 출처 검증 완료** — haiku 감사 + 상위 finding(REFUTED 2건) 직접
  재실측. 결과: **출처 실체는 8건 중 7건 확인, 1건(ISO) BLOCKED.** haiku의
  REFUTED 2건은 재실측으로 "실체 확인·제목 부정확"으로 정정 — yaml의
  `title` 필드가 논문 verbatim 제목이 아니라 설명어다(O1·O2·O3·R1).
  **설계 담당 확인 항목 2건 등재** (지시 저장 파일 헤더): title verbatim
  교체, ISO paywall 접근 수단. G32(UNKNOWN/UNSCORABLE)와 함께 확인 대기 3건.
- 구현 설계 자체의 검증은 **음성 테스트 우선**으로 대체했고, 그 규율이
  실제로 작동했다(§5의 공허한 순환 검출기).

## 2. 재사용 조사 (workspace → github subtree 순)

| 필요 | 후보 탐색 | 채택 | Ponytail 단 |
|---|---|---|---|
| registry seam | codex 커밋 `193d9a0`이 이미 구현 | **git 경로 checkout**으로 합류(손복사 아님 — 커밋 blob에서, 출처 sha 기록). 결과 바이트 = codex-mcp 판(`9ca99cf04298`)과 동일 → **G34(2버전) 해소, 이 브랜치 기준** | 2 (재사용) |
| canonical bytes/hash | codex `_receipt.py` (타 브랜치, in-repo 부재) | 함수 본문 **verbatim 이식** + provenance 주석. in-repo drift 핀은 브랜치 합류 전 불가 — 사유 기록 | 2 |
| 순환 검출 | github 후보 불필요 — **stdlib `graphlib`** | `TopologicalSorter`/`CycleError` | 3 (stdlib) |
| canonical JSON | github 후보 조사: RFC 8785(JCS) 구현체 | **불채택** — `canonical_bytes`(sort_keys)가 codex 라인에서 이미 검증됐고 요구를 충족. 새 의존성은 실행 중 사슬에 추가하지 않음 | 2 > 5 |
| profile/projection | 없음 (D7 신설) | dataclass + 순수 함수, `cg_obligations` 내 | 7 (최소) |
| 어휘 결박 검사 | H1a `_h1a_policy_audit` 패턴 참조 | 신규 `results_from_claim_anchoring` — 단 **semantic support가 아님을 이름과 docstring이 명시** | 7 |

**github subtree 결론: 신규 subtree 0건.** 필요물 전부가 workspace 기존
구현 또는 stdlib로 충족 — 조사했고 불필요가 결론임을 기록한다(CLAUDE.md
"모른다고 미해결로 쓰지 않는다"의 역방향 적용).

## 3. 의존성 분석 (실측)

```
cg_identity (신규 잎)     : import 3.2ms, 의존 {hashlib, json} — AST 테스트로 고정
cg_obligations (537행)    : import 7.2ms, 소비자(이 브랜치) = server.py, 테스트 2
                            소비자(codex 브랜치) = run_pipeline.py — **가산 변경만** 허용
cg_identity → cg_obligations 방향 edge 금지 (kernel이 판정 계층을 모름)
cg_obligations → cg_identity 미도입 — v0에선 불필요, 도입 시 단방향만
```

**가산성 검증**: Verdict에 ERROR 추가, ObligationResult 말미 defaulted 필드,
certify 오류 항목 추가 — 기존 호출 시그니처·직렬화 키 유지. 루트 게이트
전부 통과가 그 증거.

## 4. 구현 (step by step 실행 기록)

| step | 내용 | 검증 |
|---|---|---|
| 1 | registry seam 합류 (`git checkout 193d9a0 -- conceptgate/cg_obligations.py`) | sha `9ca99cf04298` 일치, core 107 passed |
| 2 | `cg_identity.py` — canonical_bytes/sha256 이식 + kind-도메인 분리 fingerprint 4종 + **§29 부정 계약을 AST 테스트로 집행** | 9 tests (키순서 불변·값순서 민감·None 통과·도메인 분리·자유형 kind 거부·판정 함수 부재·import 화이트리스트) |
| 3 | D1 ERROR verdict (+aggregate 우선순위 FAIL>ERROR>PASS>UNKNOWN, ERROR는 reason 필수) · D5 `graph_revision` + `stale_obligations()` · D3 `certification_cycle()`+certify 배선 · D7 `CertificationProfile`+`is_certified`+`certified_projection`+`LEGACY_RELATION_PROFILE`(§31-E) · `claim.evidence_anchoring` 의무+decider | 12 tests |
| 4 | **E2E-v0 trace** (`test_e2e_v0_refine_verify.py`) — §25의 9단계: snapshot→candidate(origin/lifecycle)→Verify(무수정)→obligation(revision 결박)→repair(새 revision, 구 revision 불변 fingerprint로 증명, stale 거부)→projection(view, 입력 무변경)→derived는 origin으로 구별. §31-F의 who-wrote/authority/provenance를 단계마다 단언 | 통과 |

### §5. 음성 테스트가 잡은 것 (이 회차의 P1 미수)

`certification_cycle` 첫 판이 `TopologicalSorter(graph).static_order()`를
**소비하지 않고** 호출했다 — generator라 CycleError가 영영 발생하지 않는
**완전히 공허한 검출기**였고, 순환 음성 테스트가 즉시 잡았다. `list()` 감싸기
+ 코드 주석으로 고정. **P1의 12회차가 될 뻔한 것을 게이트 규율이 커밋 전에
차단한 첫 사례** — 지금까지 P1은 전부 커밋 후 발견이었다.

## 5. 검증 방법 설계 (구현물에 적용된 것)

| 방법 | 적용 |
|---|---|
| 음성 테스트 (게이트 규율) | 순환·ERROR-무사유·profile 모순·자유형 kind·어휘부재≠FAIL — 전부 위반 입력이 실제 거부되는지 |
| 정밀도 짝 | 무순환 통과·None revision은 stale 아님·부재 검사≠통과 |
| §29 부정 계약 | **AST 집행** — kernel에 판정 함수명·판정 모듈 import가 생기면 실패 |
| 불변성 증명 | repair 후 구 revision의 fingerprint 불변을 단언 (I1/§6) |
| 가산성 | 기존 게이트 전체 재실행 (8/0/1) |

## 6. v0 이후 (이 회차 범위 밖, 근거 포함)

- **Refine 수리 계약의 실배선** — 프로덕션 Refine은 클라이언트 LLM. obligation
  을 입력으로 받는 재조립 경로는 MCP 표면 변경이라 별도 회차.
- **Certified-gate 전환** (cg_owl 입력을 Certified로 좁히기) — authority 변경,
  gap 분석 §5대로 **상신 대상**.
- semantic support의 LLM decider — decider 실물과 함께 registry 등록(YAGNI).
- guard 게이트 3버전 합류(G31) — 브랜치 합류 작업, 이 파일 수정과 별개.
- 진동 검출(D6)·Quantifier IR(D4)·capability registry(D8) — 지시 §33 P2/P3.
