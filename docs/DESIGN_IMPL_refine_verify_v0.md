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
cg_obligations (537행)    : import 7.2ms, 소비자(codex 브랜치) = run_pipeline.py
cg_identity → cg_obligations 방향 edge 금지 (kernel이 판정 계층을 모름)
cg_obligations → cg_identity 미도입 — v0에선 불필요, 도입 시 단방향만
```

**정정 (2026-08-22, 배선 재점검)**: 위 표의 이전 판은 "소비자(이 브랜치) =
server.py"라고 적었다. **부정확하다** — `server.py`는 `cg_obligations`의
**기존** 함수(`certify`, `results_from_pipeline` 등)를 소비하지, 이번에
추가한 D1/D3/D5/D7/anchoring 어느 것도 소비하지 않는다. 아래 §7에서
사실대로 고친다.

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

## 7. 배선 재점검 (2026-08-22, 사용자 지시: "작동 test하면서 배선에 누락된 것은 없는지 점검")

`test_e2e_v0_refine_verify.py`는 신규 primitive끼리의 관통이지 **실제 MCP
응답 경로 배선**이 아니다 — 파일 자체가 `server.py`를 import하지 않는다
(확인: `grep -n "^import\|^from" test_e2e_v0_refine_verify.py`에 server
없음). 이 구별을 놓치면 "테스트가 통과한다"를 "제품에 연결됐다"로 착각한다
— 이 세션이 반복 등재한 P9(정확한 구현이 실행 경로에 없다)의 형태 그대로다.

### 7.1 확인된 배선 결함 3건

| # | 결함 | 실측 | 심각도 |
|---|---|---|---|
| **W1** | D1(ERROR)·D3(cert-cycle)·D7(profile/projection)·anchoring 의무 **넷 다 `server.py`의 실제 obligation 생산 경로(`results_from_pipeline`/`results_from_isa`/`results_from_normalizer`/`results_from_classification`)에서 미사용** | `grep -rn "cg_identity\|LEGACY_RELATION_PROFILE\|certified_projection\|evidence_anchoring" conceptgate/server.py` → 0건 | 기대된 범위(§6 "v0 이후"가 이미 "Refine 수리 계약의 실배선"을 범위 밖으로 명시) — 그러나 §3 의존성 표가 이를 **감췄다**(위 정정) |
| **W2** | D1의 `Verdict.ERROR`를 실제로 내는 생산자가 없음 — 기존 4개 `results_from_*`는 전부 `on_unavailable=Verdict.UNKNOWN`만 씀 | `grep -n "Verdict.ERROR" conceptgate/cg_obligations.py` → 정의·검사부에만 등장, 생산부 0건 | ERROR 분기(`aggregate`의 FAIL>ERROR>PASS>UNKNOWN)는 **현재 프로덕션 트래픽으로 도달 불가.** 단위 테스트로만 존재 |
| **W3** | D3의 `certification_cycle()`을 실제로 발동시키는 `depends_on`을 채우는 생산자가 없음 | `grep -n "depends_on=" conceptgate/cg_obligations.py` → 0건(신규 코드 자체 제외) | `certify()`가 항상 빈 의존 그래프에서 순환 검사를 돎 — 검사는 정확하고 테스트됐지만 실전 입력으로는 아직 트리거될 수 없음 |

**W2·W3는 "결함이 있는 검사"가 아니라 "아직 아무도 쓰지 않는 검사"다** — 차이가
중요하다. 검사 자체는 §5의 뮤테이션(빈 그래프·비어있지 않은 순환 양쪽)으로
정밀도·재현율이 확인됐다. 없는 것은 **실전 호출자**다.

### 7.2 확인된 배선 결함 1건 — 게이트 사각지대 (더 심각, 즉시 수정함)

| # | 결함 | 실측 | 조치 |
|---|---|---|---|
| **W4** | 이번에 작성한 `fingerprint()` 내부 raise와 `CertificationProfile.__post_init__` 내부 raise가 **뮤테이션 강제 게이트(`test_guard_negative_coverage.py`)의 스캔 대상 밖**이었다 — 그 게이트는 `assert_`/`_assert_` prefix 함수만 AST로 훑는다 | `grep -rn "^def assert_\|^def _assert_" conceptgate/*.py` → **패키지 전체에서 0건**(신규 코드 이전). 즉 `conceptgate/`는 이 저장소의 대표 안전장치가 **한 번도 보지 않은 영역**이었다 | `_assert_known_fingerprint_kind`·`_assert_no_required_allowed_na_overlap`로 raise를 **분리 추출**해 즉시 편입. 직접 호출 음성 테스트 2건 추가(`test_the_guard_itself_fires_when_called_directly`, `test_the_overlap_guard_fires_when_called_directly`) — 공개 함수를 거쳐서만 검증하면 그 함수가 나중에 가드 호출을 빼먹어도 다른 경로로 우연히 통과할 수 있다 |

W4는 이번 구현이 만든 결함이 아니라 **저장소에 이미 있던 사각지대**를
신규 코드가 상속한 것이다. `conceptgate/` 나머지 기존 함수들
(`cg_normalizer._snapshot_integrity_errors` 등)은 여전히 이 컨벤션 밖이고,
**그 재명명은 이번 범위 밖**(기존 동작·호출부 변경 없이 이름만 바꾸는
리팩터는 별도 diff로 분리해야 blast radius가 명확해진다).

### 7.3 재검증

```
python3 -m pytest test_cg_identity.py test_e2e_v0_refine_verify.py \
    test_guard_negative_coverage.py -q
# 33 passed
python3 scripts/run_gates.py   # 8 passed / 0 failed / 1 blocked (불변)
```

AST 직접 확인 — 게이트가 이제 두 가드를 실제로 본다:

```
conceptgate/cg_identity.py     _assert_known_fingerprint_kind
conceptgate/cg_obligations.py  _assert_no_required_allowed_na_overlap
```

### 7.4 결론 — v0가 "완결"이 아니라 "primitive 계층"인 이유

W1~W3는 **§6이 이미 범위 밖으로 선언한 것과 같은 경계선**이다(Refine 수리
루프의 MCP 실배선, Certified-gate authority 전환은 별도 상신). 이번 점검이
추가한 것은: 그 경계선이 **의존성 표에 정직하게 반영되지 않았다는 사실**
자체다. W4는 경계선 문제가 아니라 **안전망 자체의 공백**이었고, 이번
회차에서 즉시 닫았다.

## 8. W1 배선 (2026-08-22, 사용자 지시로 진행)

§7이 열어둔 배선을 **가산적으로** 닫았다. 기존 도구 동작 변경 0.

| 층 | 내용 |
|---|---|
| 순수 본체 | `cg_obligations.certify_relation_claims()` — anchoring 계산 + 호출자 지참 `prior_verdicts` 병합 + profile 인증 + projection + fingerprint(`cg_identity` 단방향 import 도입) + stale 판정. **게이트를 재실행하지 않는다** — relation/source verdict는 이전 도구 응답의 certificate에서 호출자가 가져온다(같은 검사 재구현 = 검증된 기제 두 벌) |
| 신뢰 경계 | `_assert_prior_verdicts_are_well_formed` — enum 밖 문자열 거부. 관대 해석(→PASS)은 세탁, 침묵 강등(→UNKNOWN)은 디버깅 불가라 거부가 유일하게 안전. **뮤테이션 게이트가 이 가드의 음성 테스트 부재를 즉시 잡았다** — W4 수정이 작동한다는 실증 |
| MCP 표면 | `server.py`의 신규 `@mcp.tool certify_claims` — 얇은 위임 + 입력 형 검증 + ValueError→구조화 오류 변환({ok:False} 계약) |
| 검증 | tool 등록 실측(12개 중 존재), tool 함수 직접 호출 3경로(무prior=인증0·전prior=인증·오형=구조화오류), 신규 테스트 5건, 루트 게이트 불변 |

**Render 함의**: 이 tool이 배포되면 zero-context 원격 소비자가 PYTHONPATH
없이 v0 사슬을 사용할 수 있다(직전 질문의 답이 "배선 후 가능"에서 "배선
완료, 배포만 남음"으로 바뀜).

### 의도적으로 열어둔 것 (이번에 닫지 않은 이유)

| # | 항목 | 이유 |
|---|---|---|
| W2 | `Verdict.ERROR`의 프로덕션 생산자 | `REASONER_UNAVAILABLE`이 crash와 의존성 부재를 같은 except에서 잡음. ~~"Java 없음(기본 Render)"~~ **← 전제 오류로 정정됨** (실배포는 docker+JRE — 리뷰 판정 V2). 판정 회신: **W2=(a)-refined** — semantic_verdict × execution_status 두 축 분리, optional 부재=UNAVAILABLE / required 부재=ERROR / crash=ERROR. 별도 diff로 진행 |
| W3 | `depends_on` 생산자 | 자연스러운 의존이 아직 없다. 검출기를 발동시키려고 장식용 의존을 만들면 그게 P1이다. Refine 수리 루프가 실제 의존을 나를 때 함께 |
| — | Certified-gate 전환 | authority 변경 — 상신 대상 (gap 분석 §5, 불변) |

