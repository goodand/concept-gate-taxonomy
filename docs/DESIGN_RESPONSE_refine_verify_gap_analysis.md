# §35 응답 — Refine ↔ Verify 지시의 7항목 gap 분석

- 작성: 2026-08-22, 지시 원문
  [`DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md`](DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md)
  저장·검증 직후
- 방법: 전부 실측(file:line 근거). 지시문 §35의 명령 — "요청된 설계가
  추상적으로 더 깨끗하다는 이유만으로 코드를 확대하지 마라. 실제 코드에 이미
  동등한 invariant가 있으면 재구현하지 말고 재사용하라" — 를 기준으로 각
  항목에 **NO CHANGE REQUIRED**를 적극적으로 판정했다
- 기반 실측: [`KERNEL_INTEGRATION_SURVEY.md`](KERNEL_INTEGRATION_SURVEY.md)(worktree
  3개 대조) + 지시 저장 시 검증 헤더(전제 V1~V5, delta D1~D7)

---

## 1. 현재 구현이 BEFORE 중 어디에 해당하는가

**§27 BEFORE 사슬 전체가 실재하고, BEFORE 그림에 없는 층이 하나 더 있다.**

| BEFORE 단계 | 실재 위치 | 확인 |
|---|---|---|
| snapshot / span / hash | `cg_normalizer` (`_snapshot_integrity_errors`, `_span_evidence`) | ✅ |
| sense/feature/relation 표현 → concept JSON | `cg_normalizer.assemble_concepts` → `server.py` | ✅ |
| essential DAG | `concept_gate_v7` (essential 78개소) | ✅ |
| composition graph + CompositionGate | `concept_gate_v7` (12개소, `transitive_gate` 등) | ✅ |
| OWL → HermiT | `cg_owl.classify` | ✅ |

**BEFORE 그림에 없는 기존 층**: M0 obligation/certificate 층
(`cg_obligations.py` 345행 + `server.py:320-323, 734-736, 838-839` 배선).
모든 MCP 응답에 typed verdict certificate가 이미 붙는다.

**지시문이 지목한 공백(`Source ⊨ Generated Semantic Claim`)은 실측으로도
공백이 맞다**: 텍스트 수준(`source.span_evidence`)만 있고 의미 수준
support 판정은 제품에 없다. 로드맵의 "L2는 0%" 진단과 일치.

**Refine ↔ Verify 루프는 존재하지 않는다.** 생성은 MCP 클라이언트(LLM)가
하고, obligation은 응답에 실려 나가지만 **그것을 입력으로 받아 수리하는
경로가 계약으로 존재하지 않는다**. E1 실증(거울 obligation → 행동 변화 0)과
E2.2 실증(reasoning contract로 실으면 Δ+0.32)이 이 공백의 양면이다.
H1a의 `_h1a_semantic_compiler`/`_h1a_policy_audit`은 **Verify쪽 프로토타입**이
실험 폴더에 있는 상태다.

## 2. AFTER와 비교해 실제 필요한 delta

지시 저장 시 실측한 D1~D7에 이번 측정으로 D8을 추가한다.

| # | delta | 실측 근거 | 우선순위(§33) |
|---|---|---|---|
| D1 | `ERROR` verdict — 현재 UNKNOWN이 도구 실패까지 흡수 | `Verdict`에 3값뿐, `on_unavailable`이 흡수 | P0 |
| D2 | fingerprint/canonical hash primitive | `conceptgate/` grep 0건. **재사용 후보: codex `_receipt.canonical_bytes`** | P0 |
| D3 | certification dependency cycle 검사 | grep 0건 | P0(검사 골격만) |
| D4 | Quantifier/Modal/LogicalOperator IR | grep 0건 | **P3 — v0 아님** |
| D5 | obligation ↔ graph revision 결박 | `ObligationResult`에 revision 필드 없음 | P0 |
| D6 | oscillation 검출 | 반복 루프 자체가 없음 | v0 아님(§7 참조) |
| D7 | claim-kind CertificationProfile | `min_assurance`(의무 단위)만 존재. registry seam이 부착점 | P1 |
| D8 | 선언적 Relation/Operator Capability Registry | 관계 능력이 게이트·OWL 내부에 하드코딩(`transitive_gate` 등), 선언 객체 없음 | P2 |

## 3. 이미 구현된 항목 — **NO CHANGE REQUIRED**

| 지시 항목 | 기존 등가물 | 판정 |
|---|---|---|
| I11 Verify는 patch 반환 금지 | `ObligationResult`에 replace/patch류 필드 0건. diagnostic code+reason 구조 이미 일치 | **NO CHANGE** |
| I9 정규화 ≠ 판정 / §32-12 UNKNOWN→false 금지 | `aggregate()` UNKNOWN이 PASS 차단, "필드 부재 ≠ 위반 0건"(`results_from_pipeline` docstring), D-H1a-18 §10.1 | **NO CHANGE** |
| I5/I8 부분 — PASS는 evidence 필수, decider 상한 | `MISSING_EVIDENCE`, `MAX_ASSURANCE`/`ASSURANCE_EXCEEDS_DECIDER_CAP` | **NO CHANGE** |
| I4 공유 정의 | `OBLIGATION_REGISTRY`(선언), decider는 기존 위치에서 실행 — "실행 결합 없음" 설계가 이미 §9의 정의/판정 분리 | **NO CHANGE** |
| §29 negative contract의 절반 | `cg_obligations` 자체가 semantic judge를 갖지 않음(어댑터는 "옮길 뿐 재검사하지 않는다") | 테스트로 고정만 필요 |
| I7 Oracle 격리 선례 | codex `hidden_gold/` 분리, H1a mutation pack answer-key 분리 반환 | 제품에 oracle 자체가 없음 — v0 무관 |
| §17 fixed-point의 절반 | H1a `_h1a_qualification_run`의 state-hash 규율, codex `state_key` 개념 | 루프 도입 시 이식 |
| §32 금지 목록 대부분 | 해당 기능이 애초에 없음 (LLM confidence를 인증에 쓰는 경로 0건 — `confidence ≠ verification_status` 분리가 설계 원칙으로 명문화) | **NO CHANGE** |

## 4. 새 top-level module 없이 흡수 가능한 항목

§26의 금지는 **새 top-level pipeline stage**다. 파일 추가 자체는 stage가 아니다.

| delta | 흡수 위치 | 방법 |
|---|---|---|
| D1 ERROR | `cg_obligations.Verdict` 확장 | enum 값 1개 + `aggregate` 규칙 1줄 + 루트 게이트 BLOCKED와의 매핑 문서화 |
| D2 fingerprint | **새 잎 모듈** `conceptgate/cg_identity.py` (codex `_receipt.py`의 배치 결정 재사용 — import 비용 실측이 그 선례) | `canonical_bytes` verbatim 이식 + `inspect.getsource` 드리프트 핀(survey §4의 3버전 분기 재발 방지) |
| D3 cert-cycle 검사 | `certify()` 내부 | `depends_on` edge에 kind가 생기면 DFS 1개 |
| D5 revision 결박 | `ObligationResult` 필드 추가 + `validate_result` 검사 1개 | 가산적 |
| D7 CertificationProfile | **registry seam** (`validate_result(registry=…)`/`certify(registry=…)`) — codex-mcp 판에만 있는 그 seam | seam 합류가 선행 조건(§4 분기) |
| D8 capability registry | `cg_obligations`와 같은 선언 패턴(`RelationCapability` dataclass) | P2로 보류 |
| §29 negative contract | AST 테스트 (선례: `test_guard_negative_coverage.py`) | Kernel 모듈에 금지 함수명·의미 판정 반환이 생기면 실패 |
| §16 atomic obligation | `ObligationResult`가 이미 atomic — `checks:{...}` 뭉치 형태를 쓰는 곳 없음 | **NO CHANGE** |

**흡수 불가(새 구조 필요)**: D4(IR primitive — P3), Certified Projection
view(§6 — 새 stage가 아니라 filter 함수지만 소비처 변경 수반, §5 참조).

## 5. 구현하면 authority boundary가 바뀌는 항목

**정확히 하나 있다. 조용히 구현하면 안 된다.**

- **Certified Projection이 Reason/Derive를 gate하게 만드는 것** (§25 step 6→8).
  현재 `classify_owl`은 조립된 concept JSON을 **인증과 무관하게** 받는다
  (`server.py:754` — obligations는 응답에 붙을 뿐 입력 조건이 아님).
  AFTER의 authority matrix는 Reason/Derive의 Read Graph를 **Certified only**로
  좁힌다. 이것은 `cg_owl` 소비 계약의 변경이며, **E2E-v0 step 8이 "optional"인
  이유가 바로 이것**이라고 판단한다 — v0에서는 projection을 만들되 기존
  경로를 끊지 않고, gate 전환은 별도 결정으로 상신한다.
- 나머지는 authority 신설이 아니라 **기존 암묵 경계의 명문화**다: Verify의
  certification eligibility는 `certify()`가 이미 하는 일이고, Refine의 graph
  쓰기 독점은 현재 클라이언트-LLM 생성 구조와 일치한다.

## 6. 순환/자기인증 위험이 현재 코드에 실제 존재하는가

**현재는 없다 — 구조적으로 존재할 수 없는 상태다. 단 E2E-v0가 그 조건을
만든다.**

실측 3건:

1. **인증→유도 사슬이 없다.** `certify()` 출력은 응답 필드(`server.py:323`)로
   나갈 뿐, 어떤 하류(`cg_owl.classify` 포함)도 인증을 입력 조건으로 받지
   않는다. certification dependency cycle(I10)은 **사슬이 생겨야 가능**하다.
   → 위험은 v0 step 6~8이 projection을 만들 때 태어난다. D3를 그 전에 넣는
   이유.
2. **어댑터는 in-process 신뢰다.** `results_from_pipeline(serialized)`는 같은
   함수 스코프에서 방금 계산된 dict를 받는다(`server.py:320`). 게이트 판정을
   "옮길 뿐 재검사하지 않는다"는 신뢰는 프로세스 내에서는 정당하다. **그러나
   v0가 Refine(revision 쓰기)과 Verify(읽기)를 아티팩트 경계로 분리하는 순간,
   이것이 codex round21이 실측한 위조 가능 receipt 문제가 된다**("자기 공개
   내용의 공개 해시는 아무것도 인증하지 않는다"). → 경계에 D2(canonical
   hash 결박)와, 격리가 필요해지면 `_receipt`의 HMAC까지.
3. **R3(자기 rationale을 검증 근거로) 경로 없음.** `confidence ≠
   verification_status` 분리가 설계 원칙으로 명문화돼 있고(`cg_obligations.py:7`),
   LLM confidence가 인증에 들어가는 경로 grep 0건. H1a에서 같은 형태(F10,
   값을 자기와 비교)가 두 번 나왔고 두 번 다 실측으로 잡혔다 — 위험의
   **형태**는 이 저장소가 이미 알고, 게이트(뮤테이션 강제)가 지킨다.

## 7. 최소 E2E-v0까지 필요한 변경만

§25의 9 step에 대해, **변경 필요분만**:

| step | 기존 자산 | 필요한 변경 |
|---|---|---|
| 1 snapshot | `cg_normalizer` | 없음 |
| 2 Refine(candidate) | 클라이언트 LLM + `assemble_concepts` | claim에 `origin/lifecycle` provenance 필드(§23 최소형) |
| 3 Verify | 게이트 4종 + obligations | **의미 support 검사 1종 신설**(L2 진입 — H1a `_h1a_policy_audit`의 expected-vs-observed 패턴이 프로토타입) |
| 4 obligation | `ObligationResult` | D5(revision 결박) + D1(ERROR) |
| 5 repair 1회 | 없음 | **obligation을 입력으로 받는 재조립 계약 1개** — 새 stage가 아니라 기존 `assemble_concepts` 재호출에 obligation 전달 |
| 6 Certified Projection | 없음 | D7 profile 1개(legacy relation claim) + **filter 함수**(view, DB 아님) |
| 7 기존 subsystem 재사용 | essential DAG·CompositionGate | 없음 (projection이 입력을 좁힐 뿐) |
| 8 OWL/HermiT | `cg_owl` | 없음 — **기존 경로를 끊지 않는다**(§5의 authority 변경은 별도 상신) |
| 9 provenance 구별 | 없음 | step 2의 필드로 충족 + `origin: derived` 기록 |

**v0에 넣지 않는 것** (지시 §33·§35 근거): D4(Quantifier IR — P3),
D6(oscillation — v0는 수리 1회라 루프가 없다; unbounded 루프 도입 시
codex `state_key` + bounded-history로), D8(capability registry — v0는 legacy
관계 2종만 쓴다), HMAC receipt(프로세스 경계가 생길 때).

**선행 조건 1건** (v0 코드보다 먼저): survey §4의 분기 합류 — registry
seam(codex-mcp에만 존재)을 commit 경로로 가져오고, guard 게이트 3버전을
조정한다. **갈라진 토대 위에 v0를 짓지 않는다.**

---

## 요약 — 지시문 §35의 마지막 질문에 대한 답

델타는 지시문의 외형(35개 절)보다 훨씬 작다. **재사용이 원칙이고 신설은
예외다**: 신설 코드는 ① `cg_identity.py` 잎 모듈(그마저 codex 이식),
② 의미 support 검사 1종, ③ profile filter 1개, ④ enum·필드·검사 소폭
확장이 전부다. 나머지는 이미 있거나(§3), v0 범위 밖이거나(§33), authority
변경이라 별도 상신 대상이다(§5).
