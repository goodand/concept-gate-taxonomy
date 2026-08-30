# Refine ↔ Verify · Graph Diff — 검증 단계와 구현 단계 감사 (2026-08-30)

- 성격: **저장소 내부 감사**. 외부 판정 채널(`DESIGN_REQUEST_`/`DESIGN_DECISION_`)도
  조사 채널(`RESEARCH_REQUEST_`)도 아니다 — 조사 채널은 **외부 자원 사실 확인**
  전용이므로 이 건에 쓰지 않았다. 선례: [[KERNEL_INTEGRATION_SURVEY]].
- 사슬 항법: 사양 [[DESIGN_DIRECTIVE_refine_verify_semantic_compilation]] ·
  판정 [[DESIGN_DECISION_refine_verify_v0_review]] ·
  구현 기록 [[DESIGN_IMPL_refine_verify_v0]] ·
  공백 분석 [[DESIGN_RESPONSE_refine_verify_gap_analysis]] ·
  그림 [[concept-gate-h1-wt/docs/diagrams/README|Z0~Z3]] ·
  색인 [[RULING_CHAIN_INDEX]] · 상태 [[concept-gate-h1-wt/HANDOFF|HANDOFF]]

## 0. 한 문장

**Verify 쪽은 지어졌고 배선까지 됐다. Refine 쪽은 없다. 그래서 아직 루프가
아니다.** 그리고 **Graph Diff 는 사양에도 코드에도 없다** — 가장 가까운
`graph_fingerprint` 는 프로덕션에서 한 번도 불리지 않는다.

## 1. 방법 — 근거 축 분할

같은 문서를 보는 agent 는 발견이 상관되므로 **대조 대상**으로 갈랐다.

| 축 | 근거 | 모델 | 금지 |
|---|---|---|---|
| A | 설계 문서만 | haiku | 코드·테스트 읽기 금지, 구현 여부 판단 금지 |
| B | 코드·테스트만 | sonnet | 설계 문서 읽기 금지 |

탐색 범위는 파일 목록이 아니라 **기간**으로 잡았다(규약: CLAUDE.md
"부재를 단정하기 전"). 관련 파일 7종의 최초 커밋이 전부 **2026-08-22** 였고,
채취 어휘 7종(`graph_fingerprint`·`stale_obligations`·`certification_cycle`·
`certified_projection`·`results_from_claim_anchoring`·`canonical_sha256`·
`CertificationProfile`)의 `git log -S` 최초 등장도 전부 2026-08-22 였다.
**그 앞은 없다.** 어휘는 지어내지 않고 진입점 테스트의 AST 에서 채취했다.

## 2. Graph Diff — **사양에도 코드에도 없다**

두 축이 **독립적으로** 같은 결론에 도달했다.

**축 A(사양)**: 정식 단계로 명세돼 있지 않다. fingerprint 의 여러 용도를
나열하는 자리에 "graph diff" 가 한 번 스쳐 지나갈 뿐이고, 입출력 계약을 가진
함수로 규정된 적이 없다.

**축 B(코드)**: 구조적 차이를 계산하는 코드가 없다. 있는 것은 둘뿐이다.

| 실물 | 위치 | 하는 일 | 배선 |
|---|---|---|---|
| `graph_fingerprint` | `conceptgate/cg_identity.py:102` | 그래프 dict **전체**를 한 덩어리로 해시. 어디가 바뀌었는지는 알 수 없다 | **없음 — 테스트에서만 호출** |
| `stale_obligations` | `conceptgate/cg_obligations.py:416` | `graph_revision` 이 현재와 다른 결과의 **이름 목록** 반환 | 있음(`certify_relation_claims:803`) |

lead 재실측(2026-08-30):

```text
graph_fingerprint( 호출처 전수 4건 — 전부 테스트
  test_e2e_v0_refine_verify.py:158,179,180 · test_cg_identity.py:41
프로덕션 0건   (양성 대조: certify( 프로덕션 호출 6건 — grep 자체는 작동)
```

`stale_obligations` 는 배선돼 있으나 **내용이 아니라 호출자가 넘긴 불투명한
revision 태그**를 비교한다. 즉 "무엇이 바뀌었나"도 "정말 바뀌었나"도 아니고
**"이 판정에 붙은 번호가 지금 번호와 다른가"** 다.

**부재 판정**(규약대로 명시): `graph_diff` · `GraphDiff` · `diff_graph` ·
`semantic_diff` · `graph_delta` — **다섯 철자 전부 `git log -S` 로도 0건.**
`grep -n "diff" conceptgate/cg_obligations.py conceptgate/cg_identity.py` 도
영어 단어 "different" 2건 외 0건.

## 3. Refine ↔ Verify — **↔ 가 아직 없다**

### 3.1 지어진 것 (Verify 쪽)

`certify_relation_claims`(`cg_obligations.py:729-822`)가 진입점이고 **MCP
표면까지 완전히 배선**돼 있다:

```text
conceptgate-mcp (콘솔 스크립트, pyproject.toml:12)
  → server.main() → mcp.run()
    → run_pipeline · expand · assemble_concepts · classify_owl
      · certify_claims · issue_claim_certificates      (@mcp.tool 6종)
        → cg_obligations
```

**테스트 105개 전부 통과**(lead 재현: `105 passed in 1.02s`). 9개 파일 —
`test_e2e_v0_refine_verify`(19) · `test_cg_obligations`(27) ·
`test_cg_identity`(10) · `test_execution_axis`(7) ·
`test_issue_claim_certificates`(5) · `test_obligation_certificates`(9) ·
`test_p1_legacy_e2e`(4) · `test_cg_evaluate`(14) ·
`test_guard_negative_coverage`(10).

### 3.2 없는 것 (Refine 쪽)

```text
grep -n "repair\|Repair" conceptgate/cg_obligations.py        → 0건
git log -S 'repair' --oneline -- conceptgate/cg_obligations.py → 0건
```

테스트 자신이 그렇게 적어 뒀다 — `test_e2e_v0_refine_verify.py:8`:
**"Refine 자리는 하드코딩된 stand-in 이다."** E2E 테스트의 "repair" 단계
(`:176-177`)는 테스트가 손으로 쓴 dict 이지 모듈 호출이 아니다.

**따라서 현재 구조는 루프가 아니라 단방향 verify 파이프라인이고, Refine 자리에
사람이 쓴 대역이 놓여 있다.** 사양이 요구한 것(Verify 의 obligation 을 Refine 이
입력으로 받아 새 revision 을 만든다)의 **되돌아오는 간선이 비어 있다.**

## 4. 사양 ∖ 구현 — 남은 것

축 A 가 뽑은 불변식은 **I1~I11** 이고 권한 분리가 핵심이다: **Refine 만
asserted graph 를 쓴다**(I2) · **Verify 는 graph 를 쓰지 않는다**(I3) ·
**Oracle 은 Refine·Verify 에 닿지 않는다**(I7) · **obligation 은 수리 힌트이지
답이 아니다**(I11, `replace_with` 금지).

I3·I7 은 코드로 강제돼 있다 — `test_cg_evaluate.py:138-164` 가 AST 로
**모듈 간 import 방향 자체**를 검사한다(evaluate 가 verify 어휘를 import 하지
않고, refine·verify 모듈이 evaluate 를 import 하지 않는다).

미구현으로 남은 것 중 이 감사가 확인한 것:

| 항목 | 상태 | 근거 |
|---|---|---|
| Refine / repair | **없음** | §3.2 |
| Graph Diff | **없음**(사양에도) | §2 |
| 무한 루프·진동 감지 | 없음 — v0 는 repair 1회 설계이고 그 1회도 대역이다 | §3.2 |
| `Verdict.ERROR` | 열거체에 있으나 **프로덕션이 한 번도 생성하지 않는다** | 축 B, 검사 3곳뿐 |
| `DeciderKind.HUMAN` · `Assurance.HUMAN_APPROVED` | **어디서도 생성되지 않는다** — 상한표 정의 1곳뿐 | 축 B |
| `DeciderKind.LLM` | 프로덕션 생성 0. 테스트에서 **상한이 거부하는지 보는 음성 사례**로만 등장 | 축 B |

마지막 셋은 결함이 아니라 **아직 안 쓰는 어휘**일 수 있다. 다만 "열거체에
있다"와 "생산된다"는 다르고, 그 구분이 기록되지 않으면 다음 세션이 있는 줄
안다.

## 5. 이미 닫힌 것 — 축 A 보고를 그대로 받았으면 틀렸을 뻔했다

축 A 의 최대 항목은 **W5 BLOCKER** 였다: `prior_verdicts` 가 인증되지 않아
호출자가 전부 `true` 로 넣으면 Verify 를 우회해 인증을 얻는다(판정문 표현으로
**deterministic laundering**), 따라서 `certify_claims: authority: diagnostic_only`.

**그 blocker 는 이미 해소돼 있다.** lead 재실측:

```text
conceptgate/cg_obligations.py:633  def issue_claim_certificate(
conceptgate/cg_obligations.py:663  def _assert_certificate_grants_verdicts(
conceptgate/cg_obligations.py:733      prior_certificates: List[...] | None = None
```

검사 순서가 계약이다(`:663` 이하) — authenticity → subject 결박 → revision
결박 → 행별 재검증. **순서가 뒤집히면 조작 진행도가 oracle 이 된다**(서명이
깨진 문서의 결박 오류를 먼저 알려주면 공격자가 어디까지 맞췄는지 알게 된다).

그리고 승급 규칙이 **fail-closed** 다: certificate 만이면 `certifying`,
raw 문자열이 **하나라도** 섞이면 `diagnostic_only` — 가장 약한 입력이 전체
지위를 정한다. 테스트 3곳이 이 불변식을 지킨다
(`test_e2e_v0_refine_verify.py:273-301` ·
`test_obligation_certificates.py:128-147` · `test_p1_legacy_e2e.py:142-151`).

**왜 축 A 가 열린 것으로 봤나 — 내 위임 설계의 결함이다.**
`DESIGN_IMPL_refine_verify_v0.md`(구현 기록, W5 해소가 §9.1 에 있다)를 축 A 의
읽기 목록에 넣지 않았고, 축 B 에게는 "설계 문서 금지"로 막았다. **두 축 어디에도
안 들어간 문서가 생겼다.** 회신을 그대로 받았다면 닫힌 blocker 를 열린 것으로
보고했을 것이다(P12).

같은 형태가 하나 더 있다. 축 A 는 D2(fingerprint primitive)를
"`conceptgate/` grep 0건"으로 보고했는데, 그것은 공백 표(`:49`)이고 **같은
문서 `:77` 이 해소책을 적어 뒀다** — "새 잎 모듈 `conceptgate/cg_identity.py`".
실제로 그 파일은 2026-08-22 에 들어왔다. **문서가 낡은 것이 아니라 축 A 가
표 한 칸만 읽었다.**

## 6. 프로토콜 준수 — 건너뛴 단계와 그 이유

규약(CLAUDE.md "외부 판정을 수신했을 때")은 `검증 설계 → 설계 적대적 검증 →
검증 → 저장` 이다. 이 감사는 외부 판정 수신이 아니라 내부 감사지만 같은 규율을
적용했다.

| 단계 | 상태 |
|---|---|
| 검증 설계 | 함 — 근거 축 2분할(§1) |
| **설계 적대적 검증** | **건너뜀** |
| 검증 | 함 — lead 재실측 3건(§2·§3.1·§5) |
| 저장 | 이 문서 |

**건너뛴 이유와 그 대가**: 두 축이 서로 다른 근거를 보므로 **교차 검증이
구조적으로 내장**돼 있다고 봤다(실제로 축 B 가 축 A 의 blocker 를 반박했다).
그러나 그것은 *발견*의 교차이지 *설계*의 검증이 아니다. **설계를 공격했다면
"두 축 어디에도 안 들어가는 문서가 있다"를 잡았을 것이다**(§5). 나는 그것을
기억으로 우연히 발견했다. 규약대로 이 사실을 명시하고 HANDOFF 복구 항목으로
올린다.

## 7. 이 감사가 확인하지 않은 것

- **다른 worktree 의 `cg_obligations.py` 판본** — 이 감사는 `concept-gate-h1-wt`
  범위다.
- **`experiments/` 하위 테스트** — `pytest.ini` 의 `norecursedirs` 로 core
  pytest 에서 제외되고 별도 인터프리터로 돈다. 실행하지 않았다.
- **`test_server.py` 전문** — 축 B 가 `verifier`/`obligations[` 로만 훑었다
  (0건). 다르게 표현된 간접 단언을 배제하지 못한다.
- **어댑터 내부 정합성** — `cg_normalizer`·`concept_gate_v7`·`cg_owl` 이
  `cg_obligations` 어댑터가 기대하는 모양을 실제로 내는지는 기존 테스트가
  단언하는 범위까지만 확인했다.
- 축 B 가 "NO TEST 5개"라 쓰고 같은 문단에서 6개로 자기 정정했다. **6개가
  맞다**(`SCHEMA_VERSION`·`VERIFIER`·`_EXECUTION_SEVERITY`·`_VERDICT_BY_VALUE`·
  `CERTIFICATE_DOMAIN`·`CERTIFICATE_SCHEMA`). 전부 상수·사설 배관이고 그것을
  **싣는 기제**는 검증돼 있다.

---

## 8. Refine 의 상위 목적 — 저장소 최초 기록 (2026-08-30)

§4 는 "Refine 의 존재 이유가 저장소 어디에도 없다"를 공백으로 남겼다. 그 공백을
채운다. **출처: 다른 workspace 세션의 설계 판정, 사용자가 전달.** 아래 계층과
경계는 그쪽 결정이고, 각 항에 붙은 **실측**은 이 세션이 코드에 대조한 것이다.

### 8.1 목적 계층

```text
상위 목적
└─ Source 의 의미를 Semantic Graph 로 표현하되,
   Verify 가 독립적으로 검증할 수 있는 상태까지 구성한다.
   ├─ 1. 의미 후보 구성 (entity/predicate/relation/quantifier/modality/scope)
   ├─ 2. canonical semantic structure 로 구성
   ├─ 3. 부족·불확실을 명시적으로 남긴다 (unknown/provisional/unresolved)
   ├─ 4. Verify 가 낸 obligation 을 해결하도록 graph 를 수정 (local repair)
   └─ 5. Verify 와 반복하며 certification 가능한 상태로 수렴시킨다
```

한 문장: **Source 에 대한 가능한 semantic interpretation 을 구성하고, 검증
결과에 따라 수정하여 Certified Projection 의 후보가 되는 Semantic Graph 를
수렴시키는 것.**

**Refine 을 "semantic correctness 확보"라고 부르면 안 된다** — correctness 를
*판정*하는 권한은 Verify 에 있다. 정확히는
`Refine = semantic construction + revision` /
`Verify = semantic validation + certification eligibility` 이고, 둘을 묶은 상위가
`Semantic Compilation = Source → validated/certifiable semantic representation`
이다.

### 8.2 네 경계 질문 — 판정과 실측

**(a) Refine 성공의 단위** — 회차 단위로 보면 **FAIL 은 Refine 실패가 아니다.**
오히려 `FAIL + well-formed + 국소화 가능한 진단`은 loop 가 정상 작동했다는
증거다. 수락 기준:

```text
Refine Success = Graph Produced AND Well-Formed AND Verifiable
                 AND (if FAIL) Diagnostic Well-Formed AND Localizable
Cycle  Success = Refine Success AND Verify == PASS
```

→ **`Refine success ≠ semantic correctness` 를 명시적 불변식으로 둘 것.**
E2E 실험에서 Refine 성능과 semantic accuracy 를 한 PASS/FAIL 로 섞지 않기
위해서다. LLM 이 틀린 `is_a` 를 냈어도 Verify 가
`RELATION_ADMISSIBILITY / target: edge_17 / source evidence supports part_of`
를 정확히 냈다면 **그 회차 Refine 은 정상 기능한 것**이다.

**(b) unknown / provisional / unresolved 는 서로 다른 것에 붙는다** — 하나의
enum 으로 합치지 마라.

| 상태 | 붙는 대상 |
|---|---|
| `provisional` | candidate claim / relation / interpretation **자체** |
| `unknown` | 특정 semantic **property 의 값** |
| `unresolved` | 미해결 ambiguity 또는 semantic **decision** |

즉 assertion state / property state / verification state 를 **분리**한다.
**Refine 은 불확실성을 표현할 수 있어야 하지만 불확실성을 진실로 확정해서는
안 된다.**

**실측**: 현재 코드에는 claim `lifecycle` 이 `candidate`/`certified`/`rejected`
뿐이고 `UNKNOWN` 은 Verify 쪽 `Verdict` 에만 있다. 위 3층 분리는 **아직
그래프 쪽에 없다.**

**(c) canonicalization 은 둘로 갈린다** — 이 항은 그쪽 세션이 **자기 문장을
정정**한 것이다("서로 다른 surface 표현을 동일 표현으로 정리"는 너무 넓었다).

| 작업 | 권한 |
|---|---|
| `"사는 곳"` → `resides_in` 의미 해석 | **Refine** |
| alpha-renaming (`x`→`v0`), 결정적 node 정렬, alias 정규화, syntactic sugar 해제 | **Shared Kernel** |
| 두 표현이 실제로 같은 관계인지 판단 | Refine/Verify 의 semantic authority |
| 두 graph 의 논리적 동치 증명 | Reasoner/Verifier |

**Kernel 은 semantic interpretation 을 canonicalize 할 권한이 없다.**
그렇지 않으면 `canonicalization → interpretation → truth` 가 한 칸씩 미끄러져
**Shared Kernel 이 semantic authority 가 된다.** 이것은 I9(Kernel 은 표현은
정규화하되 불확실성을 진실로 바꾸지 마라)를 **한 단계 넓히는** 판정이다 —
I9 는 불확실성을, 이 판정은 **해석**을 금지한다.

**(d) v0 는 5항(수렴)에 대한 증거를 산출하지 않는다.** "수렴을 목표로 한다"와
"수렴했음을 관찰할 수 있다"는 다른 문제다.

| 주장 | v0 가 증거 산출? |
|---|---|
| Refine 이 Graph 를 생성한다 | 예 |
| Verify 가 FAIL/obligation 을 생성한다 | 예 |
| obligation 을 Refine 이 받아 수정한다 | 예 |
| 수정 전후 Graph 가 달라졌다 | 예 |
| 1회 repair 가 obligation 을 **해결했다** | **Verify₁ 이 있어야 예** |
| 반복적으로 수렴한다 / oscillation 이 없다 | **아니오** |

→ **"v0 가 5항을 검증한다"고 쓰면 과장이다. "5항을 향한 transition 을
관찰한다"가 정확하다.**

### 8.3 실측 — 우리 v0 는 **경우 A** 다

판정이 가른 두 경우:

```text
경우 A   G₀ → Verify → FAIL → O₀ → Refine → G₁ → STOP
         "1회 repair 가 수행됐다"는 증거만. G₁ 이 G₀ 보다 나아졌다는 것조차 미입증
경우 B   G₀ → Verify → FAIL → O₀ → Refine → G₁ → Verify
         "그 obligation 을 해결하는 방향으로 한 단계 수렴했다"는 증거
```

`test_e2e_v0_refine_verify.py:141-201` 실측:

| 단계 | 실제 | 판정 |
|---|---|---|
| `[5]` repair `:176-177` | 테스트가 손으로 쓴 dict | stand-in |
| repair 직후 | fingerprint 상이 · 옛 obligation 이 stale | **바뀌었다**만 증명 |
| **재검증** | **없음** | **경우 A** |
| `[6]` verdicts `:186` | `all_pass = {name: Verdict.PASS for name in ...required}` — **전부 손으로** | 계산 아님 |

즉 `[4]` 의 obligation(`source.span_evidence` UNKNOWN, "ev3 미인용")은 수리가
`ev3` 를 넣은 뒤에도 **한 번도 재검사되지 않는다.**

**그러나 2-pass 승격은 새 검사기 없이 가능하다.** `source.span_evidence` 는
실제 생산자가 있다 — `cg_obligations.py:327,332`(`results_from_normalizer`).
테스트가 인스턴스를 손으로 만들었을 뿐이다. (lead 자기정정: 처음엔 생산자도
없다고 볼 뻔했고, 측정이 그것을 막았다.)

### 8.4 다음 할 일 — 최소 2-pass 실험

판정의 권고: loop scheduler 와 oscillation detector 까지 만들어 **아키텍처를
키우기 전에**, 먼저

```text
G₀ → Verify → Obligation → Refine → G₁ → Verify
```

를 만들어 **obligation 이 실제로 다음 revision 의 개선을 유도하는지** 확인한다.
그 결과가 좋으면 그때 `G₀ → G₁ → … → PASS` 를 일반화하고 fingerprint 기반
oscillation/termination 관찰을 붙인다.

**우리 쪽 구체 작업**: `[6]` 의 `all_pass` 손작성을 걷어내고 `repaired` 에
`results_from_normalizer` 를 다시 돌려 `source.span_evidence` 가 UNKNOWN →
PASS 로 바뀌는지 단언한다. 이것 하나가 경우 A → 경우 B 전이다.

---

## 9. 정정 — §2 의 "Graph Diff 는 코드에도 없다" 는 **범위가 틀렸다** (2026-08-30)

§2 는 Graph Diff 가 사양에도 코드에도 없다고 썼다. **사양 쪽은 맞고 코드 쪽은
틀렸다.** 재사용 재료 조사(vault, haiku)가 낸 `git log -S 'graph diff'` 4건을
추적하다 나왔다.

### 9.1 이미 존재한다 — 다만 kernel 이 아니라 실험에

`docs/KERNEL_INTEGRATION_SURVEY.md:37` 이 **이미 기록해 두었다**:

```text
| semantic graph diff | ❌ | **H1a에만 존재** (`_h1a_policy_audit.py`) |
```

실물: `experiments/2026-07-29_h1a_source_authority_unresolved/_h1a_policy_audit.py`
(312행). docstring: **"Expected-vs-observed policy graph comparison"**.
공개 심볼 `expected_graph` · `compare` · `audit_arm`.

`compare(observed, expected)` 는 **해시 비교가 아니라 claim 단위 구조 비교**이고
타입 있는 finding 어휘를 낸다:

| finding kind | 뜻 |
|---|---|
| `NO_OBSERVED_COUNTERPART` | 기대한 family 에 대응하는 claim 이 관측 쪽에 없다 |
| `NO_EXPECTED_COUNTERPART` | 관측된 것에 대응하는 정본 축이 없다(템플릿 규칙) |
| `MIXED_EXPECTATION` | 접힌 축들이 불일치해 단일 기대 상태가 없다 |
| `UNRESOLVED` | **컴파일러가 결정하지 못했다** |
| `STATE_MISMATCH` | 산문이 정본과 다르게 말한다 — drift |
| `CONDITIONAL_STATE` | 예외절이 붙은 규칙은 무조건 그 상태가 아니다 |
| `STRUCTURAL_DEFECT` · `REQUIRES_REVIEWER_ADJUDICATION` | 구조 결함 · 판정자 회부 |

### 9.2 왜 §2 가 놓쳤나 — **내가 방금 성문화한 규약을 내가 어겼다**

`git log -S` 로 다섯 철자(`graph_diff`·`GraphDiff`·`diff_graph`·
`semantic_diff`·`graph_delta`)를 돌려 0건을 얻고 부재로 적었다. **그 다섯은 내가
지어낸 것**이다. 이 모듈은 그 어휘를 하나도 쓰지 않는다 — `compare` ·
`expected_graph` 를 쓴다.

CLAUDE.md §"부재를 단정하기 전" 이 명시한 절차는 **이웃에서 어휘를 채취하라**
였고, `KERNEL_INTEGRATION_SURVEY.md` 는 설계 문서에서 **1홉**이다. 그래프를
걸었다면 즉시 나왔다. **규약을 쓴 그 세션이 같은 날 그 규약을 어겼다**(P23).

축 B(코드)도 못 잡았는데, 내가 범위를 `conceptgate/cg_obligations.py` 와
그 테스트로 못박았기 때문이다 — `experiments/` 는 범위 밖이었다. **위임 범위가
곧 발견의 상한이다.**

### 9.3 그래서 §2 를 어떻게 고쳐 읽어야 하나

| 주장 | 판정 |
|---|---|
| 사양(DIRECTIVE)에 Graph Diff 가 정식 단계로 없다 | **유지** — 스쳐 지나가는 언급뿐 |
| `conceptgate/` 제품 코드에 없다 | **유지** — `KERNEL_INTEGRATION_SURVEY` 도 ❌ 로 적었다 |
| ~~저장소 어디에도 없다~~ | **정정** — H1a 실험에 **작동하는 구조 비교기**가 있다 |
| `graph_fingerprint` 가 프로덕션 미호출 | 유지(별개 사실) |

**대상이 다르다는 것은 함께 적어야 한다.** `_h1a_policy_audit` 는 *정책 DSL 에서
유도한 기대*와 *렌더된 산문에서 관측한 것*을 비교한다. 우리가 필요한 것은 *같은
의미 그래프의 revision t 대 t+1* 이다. **같은 것이 아니다.** 재사용 가능한 것은
비교 대상이 아니라 **기제**다 — claim 단위 대응, 타입 있는 finding, 그리고 아래.

### 9.4 재사용 가치가 높은 세 성질

1. **보고하되 판정하지 않는다.** docstring: "Reports rather than raises: this
   module is an auditor, and the freeze gate is what decides." → **I11 그 자체**
   (obligation 은 수리 힌트이지 답이 아니다)를 이미 구현한 선례다.
2. **다른 arm 끼리 비교를 거부한다.** `AuditContractError` — "comparing different
   arms would manufacture divergences that are not there". 비교 전제를 계약으로
   강제한다.
3. **증명된 검출기의 일치와 미증명 검출기의 일치를 섞지 않는다.**
   `agreed` 대 `agreed_by_unproven_detector` 를 별도 필드로 낸다. 2026-08-16
   리뷰어 R3 가 잡은 것 — 한 필드에 섞였을 때 독자가 **도구가 얻지 못한 coverage
   주장**을 읽게 됐다. `Refine success ≠ semantic correctness`(§8.2a)와 같은
   형태의 분리다.

그리고 `UNRESOLVED` 가 **first-class finding kind 로 이미 있다** — §8.2(b) 가
요구한 3층(provisional/unknown/unresolved) 중 하나가 실험 쪽에는 존재한다.

### 9.5 부수 발견 — **부재 기록이 그 부재의 측정을 파괴한다**

오늘 아침 다섯 철자는 각 **0건**이었다. 지금 다시 돌리면 각 **1건**이다.
늘어난 1건은 `REFINE_VERIFY_STAGE_SURVEY_20260830.md` 자신 — **부재를 증명하려고
철자를 나열한 이 문서가 pickaxe 에 걸린다.**

내일 같은 검사를 돌리는 사람은 1건을 보고 "존재한다"고 읽을 수 있다.
**부재 기록에는 측정 시각과 "이 기록 자체가 이후 hit 가 된다"를 함께 적어야
한다.** 이 절이 그 사례다(P25 계열 — 측정 도구가 조용히 다른 것을 쟀다).

---

## 10. 구현 재료 조사 — **재료는 있다. 없는 것은 연결이다** (2026-08-30)

사용자 질문: "구현을 하기 위한 재료들이 이 workspace 에 있나?" haiku 3축 위임
(재사용·subtree / logical-revision·Goedel-Prover / benchmark). lead 가 판정을
뒤집을 수 있는 주장을 직접 재실측했다.

### 10.1 가장 큰 발견 — **Refine 의 설계는 이미 있다**

`notes/research/logical-revision/mechanism_spec.md` (**680행**, 2026-07-12).
lead 실측한 절 구조:

```text
Core entities · Global loop · Internal state schema
Commitment/entailment/obligation interaction
Feedback algebra          ← 진단 어휘 9종
Update algebra and policy order
Rollback frontier and proof object boundary
Obligation lifecycle
Verified region and proof object locking
Invariant system          ← I1~I7
Convergence and termination  ← success / **abstention**
```

**이것이 Refine 이다.** §3.2 가 "Refine 은 없다"고 쓴 것은 **코드**에 대해서는
맞지만 **설계**에 대해서는 틀렸다. 설계는 6주 먼저 존재했다.

feedback 클래스 9종(원문):

| class | 갱신 대상 |
|---|---|
| Pass | candidate object |
| Syntax failure / Type failure | local (typed) segment |
| **Non-entailment** | unsupported claim or edge |
| **Contradiction** | conflict set |
| **Missing premise / Missing witness** | obligation set |
| Bad decomposition | decomposition graph |
| **Evidence insufficient** | retrieval layer **또는 abstention path** |

이것은 I11("obligation 은 수리 힌트이지 정답 graph 가 아니다")이 요구하는
진단 어휘의 **완성된 후보**다. 그리고 `Evidence insufficient → abstention` 은
DIRECTIVE 계열에 **아예 없는 개념**이다.

### 10.2 두 계열이 서로를 모른다 — 그리고 **I 번호가 충돌한다**

lead 실측:

```text
DIRECTIVE 가 mechanism_spec 을 언급        : 0건
mechanism_spec 이 Refine/Verify 를 언급    : 1건
mechanism_spec 을 가리키는 문서 8개         : 전부 notes/ (MOC 6 + 프로젝트 HANDOFF 1 + v4)
                                            → concept-gate-h1-wt/docs/ 에서는 0건
```

**두 설계가 같은 부품을 두고 6주 간격으로 따로 쓰였고 서로를 모른다.**

그리고 **같은 `I` 라벨에 완전히 다른 내용이 들어 있다**:

| 번호 | `mechanism_spec` | `DESIGN_DIRECTIVE` |
|---|---|---|
| I1 | No active contradiction | Semantic Graph is state |
| I2 | Support or obligation | Refine 만 asserted graph 를 수정 |
| I3 | **Verified-region protection** | Verify 는 graph 를 수정하지 않는다 |
| I4 | Provenance requirement | Shared definitions 허용, shared judgments 위험 |
| I5 | **Minimal rollback** | Open vocabulary, closed inference |
| I6 | **Bounded correction**(retry 한도) | Candidate/Certified/Entailed 구분 |
| I7 | **Safe abstention** | Oracle 은 evaluation-only |

**"I3" 이라고만 쓰면 어느 계열인지 알 수 없다.** 이 SURVEY 를 포함해 오늘
커밋한 문서들이 `I2·I3·I7·I9·I11` 을 **DIRECTIVE 뜻으로** 인용했다. 앞으로
계열 접두를 붙여야 한다(예: `D-I3` / `M-I3`).

**둘은 모순이 아니라 다른 축이다.** `mechanism_spec` 은 **상태·갱신 허용성**
(모순 없음·지지 또는 의무·최소 롤백·재시도 한도·기권), DIRECTIVE 는 **권한
경계**(누가 무엇을 쓸 수 있는가). 합쳐야 하고, 합칠 때 번호를 정리해야 한다.

### 10.3 외부 재료 — 이미 실사가 끝나 있다

`atp-verifier-inferential-subtree-subflow-research` **v4**(기제 슬롯 S1~S14 ·
논문→슬롯 대응) / **v3**(841행, 파일 단위 vendoring 결정 · 라이선스 실사).

v4 §6 매트릭스의 결론(원문): **"현재 핵심은 theorem prover 하나를 더 붙이는
것이 아니라, mechanism core 를 직접 세우고 외부 repo 를 부품으로만 쓰는
것이다."** 외부 자산이 대신 못 하는 것 넷 —
**Commitment formation · Typed feedback translation · Rollback frontier
control · Obligation management**.

v3 의 vendoring 우선순위(라이선스 확인 완료):

| # | 대상 | 방식 | 라이선스 |
|---|---|---|---|
| 1 | `hanwenzhu/LeanArchitect` | git dependency 권장(subtree 가능) | Apache-2.0 |
| 2 | RobustPABench 결정론적 edit core | 필요한 함수만 `third_party/robust_pa/` 로 | MIT |
| 3 | Gödel's Poetry AST/hole extraction | PyPI 또는 별도 service(subtree 아님) | Apache-2.0 |
| 4 | LLMLean | Lean package git dependency(선택) | MIT |
| 5 | C2C `prompt.py` | subtree 대신 **50~100 LOC 자체 재구현** | MIT(1파일 공개) |

### 10.4 우리 저장소 안의 재료

- **Graph Diff 기제** — `_h1a_policy_audit.py` (§9). claim 단위 구조 비교 +
  타입 있는 finding + 보고/판정 분리.
- **Obligation 커널** — `cg_obligations.py`. 이미 배선·검증 완료(§3.1).
- **gUFO 규칙** — `vendor/scior` 이미 read-only subtree, `cg_gufo.py` 어댑터
  경유(lead 실측: 두 경로 다 실재).

### 10.5 재료가 **없는** 칸

| 필요 | 재료 |
|---|---|
| 양화·양상·scope IR | **없음.** 두 계열 모두 상위 정규화 층으로 미룬다 |
| 수렴의 **수학적** 증명 | **없음.** `mechanism_spec` 도 retry 예산 소진에 의한 **운영적** 종료다 |
| 진동 주입 벤치마크 | **없음.** v4 로드맵 Phase 5 로 예정만 |

### 10.6 오라클·벤치마크 (축 3 보고 — **lead 미재실측**)

승인 4종으로 보고됐다: **WikiSem v0.3**(OSU, ~5,046문장, typed lambda) ·
**PMB 5.1.0**(Gold 11,987문서, ODC-BY) · **FOLIO v0.0**(Yale-LILY,
CC-BY-SA-4.0, 양화≥2 가 86건) · **Redwoods DeepBank 1.1**(MRS, **WSJ 텍스트
권리 BLOCKED**). 탈락 7종은 대부분 **라이선스 미확정**이 사유다.

**이 절만 lead 재실측을 하지 않았다** — 기존 `RESEARCH_RESULT_*` 정본이
이미 있고 그것이 판정 사슬에 실려 있으므로, 재실측이 필요하면 그 정본을
직접 읽어야 한다. 이 절은 **포인터이지 근거가 아니다.**

### 10.7 답

**재료는 있다. 그것도 많다.** 부족한 것은 재료가 아니라 **연결**이다 —
Refine 의 설계가 6주 먼저 존재했는데 그것을 대체하려는 계열이 그 존재를
모른다. §9 가 Graph Diff 에서 겪은 것과 **같은 형태**이고, P26(정정이 정본까지
도달하지 않는다)의 더 큰 판이다.

**다음 작업 순서 제안** — 코드를 쓰기 전에 연결부터:

1. 두 불변식 체계를 **한 표로 합치고 번호 충돌을 해소**한다(`D-I*` / `M-I*`).
2. `mechanism_spec` 의 feedback 클래스 9종을 우리 obligation 어휘와 대조한다 —
   `OBLIGATION_REGISTRY` 9종과 **개수가 같다.** 우연인지 대응인지 확인해야 한다.
3. 그 뒤에 §8.4 의 **2-pass 실험**. 이것은 여전히 새 재료가 필요 없다.

---

## 11. 관계 그래프 점검 — **분류가 아니라 위치가 권위를 정하고 있었다** (2026-08-30)

사용자 지시: "분류 체계를 잡는 것도 중요하지만 **backlink 로 relation graph 를
점검하는 것이 더 먼저**다. 우리가 만드는 validator 와 마찬가지로 md 들도
graph 로 표현되고 있다."

§10.2 는 두 계열의 단절을 **grep 으로** 판정했다. grep 은 "어디 있나"에 답하지
관계를 보지 않는다. `evidence-vault-mcp` / `vault-retrieval` 로 다시 쟀다.

### 11.1 먼저 색인이 stale 이었고, 원인이 이 세션이었다

`index_freshness` 최초 호출: `freshness: stale` ·
**`negative_claims_supported: false`** · `NO_NEGATIVE_CONCLUSION` **blocking**.

미색인 2건 중 하나가 이 SURVEY, 해시 불일치 3건 중 둘이 오늘 고친
`HANDOFF.md`·`RULING_CHAIN_INDEX.md` 였다. **내 작업이 색인을 낡게 만들었고,
그 상태에서 §10 의 부재 주장을 했다.**

사용자 승인을 받아 재구축: `freshness: fresh` · 검사 6종 전부 통과 ·
문서 **2,362** · 간선 **21,258** · referral target **2,343** ·
`negative_claims_supported: true`.

### 11.2 backlink 실측 — 단절은 사실이나 **형태가 달랐다**

`vault_backlinks` (색인 비의존 — Obsidian CLI/파일시스템 그래프, `exhaustive: true`):

| 노드 | inbound |
|---|---|
| `notes/research/logical-revision/mechanism_spec.md` | **8** — MOC 6 · 형제 `atp-v4` 1 · **이 SURVEY 1(오늘)** |
| `concept-gate-h1-wt/docs/DESIGN_DIRECTIVE_…` | **10** — MOC 7 · `gap_analysis` · `diagrams/README` · **이 SURVEY** |

**정정**: §10.2 는 "서로를 모른다"고 썼다. 그래프상으로는 **MOC 4개를
공유하므로 2홉에 도달 가능**하다(`concept-gate-architecture` ·
`evidence-provenance` · `logical-revision-atp` · `ontology-relations`).
**저자가 만든 간선이 없을 뿐이다.** 워크스페이스 규약이 그 차이를 이미 적어
뒀다 — **"Generated MOCs are navigation artifacts, not source authority."**

### 11.3 그 MOC 는 관계가 아니라 **동거**이고, 29% 가 죽어 있다

`notes/00-moc/by-topic/logical-revision-atp.md` 실측:

```text
총 링크 117 · 고유 basename 30      → 같은 문서가 평균 4번 (worktree 사본)
살아 있는 링크 83 · **죽은 링크 34 (29%)**
죽은 링크의 대상: concept-gate-codex-mcp-wt 18 · concept-gate-redteam-wt 16
                 → 둘 다 오늘 아침 제거를 확인한 worktree
```

그리고 DIRECTIVE 와 `mechanism_spec` 은 이 파일 안에서 **약 100행 떨어진 다른
섹션**(`## docs` 대 `## research`)에 있다. 이 MOC 는 "둘이 관련 있다"고 말하지
않는다 — **"둘 다 이 주제 태그를 받았다"**고 말할 뿐이다.

`index_freshness` 의 `DEAD_PATHS` 검사는 이것을 못 잡는다. 그 검사는 **색인된
경로가 디스크에 있는가**를 보지, **문서 안의 wikilink 가 어디를 가리키는가**를
보지 않는다.

### 11.4 기계적 원인 — **권위가 내용이 아니라 경로에서 나온다**

`vault_search`(색인 fresh) 가 붙인 분류:

| 문서 | `role` | `authority_class` |
|---|---|---|
| `notes/research/logical-revision/mechanism_spec.md` | **`spec`** | **`N0-navigation-note`** |
| `notes/research/…/atp-v4.md` | note | `N0-navigation-note` |
| `notes/00-moc/…` | note | `N0-navigation-view` |
| `concept-gate-h1-wt/docs/DESIGN_DIRECTIVE_…` | note | `P2-path-stable-worktree` |
| `concept-gate-taxonomy/docs/expansion_strategy_…` | note | `P2-canonical-authority` |
| `…/experiments/…` | — | `P0-active-experiment` |

**`authority_class` 는 경로를 따라간다.** `notes/` 아래면 내용이 무엇이든
`N0` 다. `role` 은 `spec` 으로 **옳게** 붙었는데 권위는 위치가 정했다.

즉 **Refine 의 설계 명세가 검색·순회에서 최하위 권위로 취급된다.** 저자 간선이
없는 것과 겹쳐서, DIRECTIVE 쪽에서 그래프를 걸어도 그것이 유의미한 가중치로
떠오르지 않는다. 6주간 아무도 못 본 것이 **부주의가 아니라 구조**였다.

### 11.5 사용자 지적이 옳았던 이유 — 이것은 우리 validator 와 **같은 문제**다

MOC 가 하는 일은 정확히 `graph_fingerprint` 가 하는 일이다 — **"뭔가 관련
있다"는 거친 신호를 주고 무엇이 어떻게 관련되는지는 말하지 않는다.**
`stale_obligations` 가 불투명한 revision 번호를 비교하듯, MOC 는 불투명한 주제
태그를 공유한다.

없는 것은 **타입 있는 간선**이다. 그리고 그것을 만드는 기제가 이미 우리
저장소에 있다 — `_h1a_policy_audit.compare()` 가 정책 그래프에 대해 내는
`STATE_MISMATCH` · `NO_OBSERVED_COUNTERPART` · `UNRESOLVED` … (§9).

```text
지금:  A --[같은 주제 태그]--> MOC <--[같은 주제 태그]-- B     (동거)
필요:  A --[supersedes | refines | conflicts-with | same-component]--> B  (관계)
```

**분류(어느 태그에 넣을까)보다 관계(둘이 무슨 사이인가)가 먼저**라는 지적은
이 실측에서 그대로 확인된다. 태그는 둘 다 옳게 붙어 있었고 — 그래서 못 봤다.

### 11.6 이 절이 바꾸는 것

1. §10.2 의 "서로를 모른다" → **"저자 간선이 없고 MOC 로만 2홉 연결된다"**로 정정.
2. **부재 주장 전에 `index_freshness` 를 먼저 호출한다.** 이 세션은 자기가 만든
   staleness 위에서 부재를 주장했다. CLAUDE.md §"부재를 단정하기 전"에 이
   단계가 빠져 있다.
3. **MOC 의 죽은 링크는 어떤 게이트도 잡지 않는다.** 등록부의 거짓말은
   `test_legacy_register.py` 가 막는데, **MOC 의 거짓말은 아무도 안 막는다.**
   29% 는 그냥 방치된 수치다.
4. `authority_class` 가 경로 파생이라는 것을 **알고 쓴다** — `notes/` 에 둔
   설계 문서는 검색에서 권위를 얻지 못한다. 정본으로 삼을 문서는 위치를
   옮기거나, 저자 간선으로 명시적으로 끌어와야 한다.

---

## 12. 간선 추가 — 두 계열이 이제 서로를 안다 (2026-08-30)

사용자 지시: "추가해야 할 backlink 를 추가하는 작업을 해라. 우리는 의미론적으로
두 가지 이상을 연결해야 하는 상황이다." §11 의 게이트는 **있는 링크가 죽었나**를
재지 **있어야 할 링크가 없나**는 못 잰다 — 후자는 의미론적 판단이라 손으로 했다.

### 12.1 간선 타입을 정하기 전에 관계를 실측했다

두 문서가 "같은 부품"(§10.2)이라는 내 서술은 **부정확**했다. 공유 어휘 실측:

| 어휘 | mechanism_spec | DIRECTIVE |
|---|---:|---:|
| `obligation` · `Candidate` · `provenance` | 35 · 13 · 14 | 38 · 15 · 17 |
| `commitment` · `rollback` · `abstention` | 31 · 17 · 8 | **0 · 0 · 0** |
| `Refine` · `Verify` · `Certified` · `canonical` | **0 · 1 · 0 · 0** | 41 · 45 · 31 · 31 |

**공유하는 것은 obligation·candidate·provenance 셋뿐이고 나머지는 상보적이다.**
mechanism_spec 은 상태 갱신 대수, DIRECTIVE 는 권한 경계 — **같은 obligation 위에
세운 두 층**이다. 그래서 간선 타입은 `supersedes` 가 아니라 **`complements`** 다.

그리고 `atp-v4` 헤더가 이렇게 적어 뒀다: "**현재 확정된** `mechanism_spec.md` 를
기준으로". 초안이 아니라 **확정 기준**이었고, DIRECTIVE 는 그것을 모른 채 6주 뒤
쓰였다.

### 12.2 넣은 간선 — 세 결절점, 양방향

| 어디에 | 무엇을 | 타입 |
|---|---|---|
| `DIRECTIVE` 헤더 | → `mechanism_spec` · `atp-v4` · 이 SURVEY | 선행 설계(상보) |
| `mechanism_spec` frontmatter + 본문 인용 블록 | → `DIRECTIVE` · `DESIGN_IMPL_v0` · 이 SURVEY | `complemented_by` · `implemented_in` |
| `obligation_layer_roadmap` 헤더 | → `mechanism_spec` · `DIRECTIVE` | L3 갱신 대수의 정본 |

세 곳 모두에 **I 번호 충돌 경고**를 함께 적었다 — 이쪽 I3 ≠ 그쪽 I3. 이것을 안
적으면 연결이 오히려 오독을 만든다.

`obligation_layer_roadmap` 은 5 worktree 에 동일 사본(sha `78731601`)이다. **h1-wt
것만 고쳤다** — 규약(worktree 간 손복사 금지, commit→merge 만). 나머지 넷은
머지로 받는다.

### 12.3 검증 — 도구로, grep 이 아니라

- **색인 재구축** → fresh, 간선 **21,258 → 21,269**(+11). 넣은 wikilink 가 그래프에
  실제로 들어갔다.
- **`vault_search`** "DIRECTIVE 의 obligation 갱신 대수 선행 설계" → `mechanism_spec`
  이 **2위**, preview 첫 줄이 새 관계 블록. `roadmap` 6위.
- **`vault_backlinks(mechanism_spec)`** → concept-gate 저자 간선 **0 → 2**
  (DIRECTIVE · SURVEY).
- 게이트 43/43 · 전체 14/0/0. 새 간선은 저장소 밖이므로 `EXTERNAL` 로 옳게 분류.

### 12.4 부수 발견 둘 — 둘 다 결판났다

**① `vault_backlinks` 가 사본을 오인한다.** `mechanism_spec` 의 backlink 에
`concept-gate-e2.2-wt/docs/obligation_layer_roadmap.md` 가 잡혔는데 그 파일에는
문자열이 **0건**(양성 대조 `obligation` 12건). 내가 고친 것은 **h1-wt** 사본이다.
도구가 basename 으로 해소해 사본을 오인한 것 — DIRECTIVE(사본 1개)에서는 재현되지
않으므로 확정. 이것이 `10fb68f` 가 "세는 방법 자체가 틀렸다"고 한 그 문제이고,
§11 의 게이트가 `AMBIGUOUS` 를 별도 판정으로 둔 이유다.

**② DIRECTIVE 헤더의 `본문 sha256: df10ee…` 는 내 절단으로 재현되지 않는다.**
편집 전 HEAD 와 현재의 본문(`# 실험 운영 에이전트용…` 이후)이 같은 `9453da…` 이므로
**본문 무변경은 확정**이고(diff 도 순수 삽입 19행), 기록된 값은 트랜스크립트 추출
시점의 다른 절단이다. 어느 절단인지 헤더가 적지 않아 **재현 불가한 해시**로 남아
있다 — 사슬 문서의 `VERBATIM-BEGIN/END` 규약이 이 문서에는 없다.

### 12.5 아직 안 한 것

- `notes/projects/concept-gate/HANDOFF.md:45` 는 `mechanism_spec.md` 를 **백틱
  산문**으로만 언급한다 — grep 은 잡고 backlink 는 안 잡는다(CLAUDE.md 가 기록한
  그 함정). 그 문서는 다른 세션 소관으로 보여 건드리지 않았다.
- 두 불변식 체계의 **통합 표**(§10.7 의 1순위)는 이 절이 아니다 — 이 절은 서로를
  가리키게만 했다. 합치는 것은 별도 작업이다.

### 12.6 zero-context 검증 — haiku 가 도구로 찾는가 (사용자 지시)

§12.3 의 `vault_search` 검증은 **내가 답을 알고 쿼리를 짠 것**이라 진짜 검증이
아니다. 연결의 목적이 "다음 세션이 찾을 수 있게"이므로 그 세션을 흉내 냈다 —
zero-context haiku 에게 문서명·경로·`mechanism_spec`·`abstention`·I 번호를 **전부
빼고 개념만** 줬다("no safe update exists 에 대한 정의된 결과가 있나").

| 질문 | 결과 | 도달 경로 |
|---|---|---|
| 갱신·롤백·기권 규칙은 무엇이 정하나 | `mechanism_spec` §4~7 을 `path:line` 인용 | **`obligation_layer_roadmap` 헤더 → 1홉** |
| 권위 문서가 둘인가, 상충하나 | 양방향 포인터 텍스트를 **둘 다** 인용, **I3 충돌**까지 정확 | DIRECTIVE 헤더 |
| handoff 첫 지시 | `RULING_CHAIN_INDEX` 진입점 | HANDOFF 직접 |

**통과.** 그리고 haiku 가 스스로 적은 한 문장이 이 절의 결론이다:

> "No direct `vault_search` queries were needed — the documents chain from each
> other through explicit wikilinks."

즉 **검색이 아니라 저자 간선으로 갔다.** 첫 도달은 세 결절점 중 마지막에 넣은
`obligation_layer_roadmap` 이었다 — 새 세션이 "obligation 시스템 구현"으로 들어오면
그 로드맵부터 읽기 때문이다. **§11.4 의 우려(`N0` 권위가 검색 순위를 깎는다)는
저자 간선이 있으면 무력화된다** — 검색 순위를 탈 필요 없이 링크로 닿는다.

haiku 의 인용 행 번호 4건(`:10` · `:348` · `:545-547` · DIRECTIVE `:14`)을 재실측했다.
**전부 실제 내용과 일치** — 회신이 정직했다.

### 12.7 두 가지 정정 — 커밋 직후 실측

**① "양방향 연결"의 한 방향은 버전 관리 밖이다.** `notes/` 는 git 미추적이다
(workspace 루트도 git 아님). 즉 `mechanism_spec.md` 에 넣은 역방향 간선
(`complemented_by` · `implemented_in` · 본문 관계 블록)은 **파일시스템과 검색
색인에만 존재**하고 어느 커밋에도 없다. `ec992f6` 이 "양방향"이라 적은 것은
그래프상 참이지 저장소상 참이 아니다. vault 쪽은 그 자체 규율(MOC 재생성·
`generate_vault_mocs.py`)로 관리되므로 이 문서는 그 사실을 **적는 것**으로
그친다 — `notes/` 를 git 에 넣는 것은 이 세션의 결정이 아니다.

**② `vault_backlinks` 의 사본 오인은 새 결함이 아니다.** evidence-evaluator
쪽 `docs/HANDOFF.md:289` 가 이미 **D1a** 로 등재했다 — "바이트 동일 사본 9벌 중
**worktree 사본**이 정본 슬롯을 가져간다". §12.4① 은 그 문제의 backlink 판이다.
도구 소관 세션의 것이라 그쪽 문서는 건드리지 않고 여기 참조만 남긴다:
`evidence-evaluator/docs/HANDOFF.md:289-290 (D1a·D1b)`.

---

## 13. 식별자 사전 — A~Z 전수 조사와 등록부 게이트 (2026-08-31)

사용자: "A-Z까지 전수조사 해야 하나" → "분류체계를 위해서 진짜 사전(dictionary)를
만들어야겠네." 회고 §24 는 P·W·I 셋을 **눈에 띈 것**으로 봤을 뿐 체계적으로 고른
게 아니었다.

### 13.1 전수 결과 — 다섯이 아니라 열넷

A~Z × 6 문서군 정규식 전수: **17글자**가 2개 이상 문서군에 걸친다(안전한 것은
A·H·T·U 넷). 그러나 "겹침"은 충돌의 필요조건일 뿐이다 — `G` 는 회고가 발행하고
판정문은 인용만 하니 겹쳐도 충돌이 아니다. 문맥을 읽어야 하므로 haiku 2축(7+7글자)에
위임했다:

| 판정 | 글자 |
|---|---|
| **COLLIDES** (같은 번호, 다른 뜻) | **B C D F I M P R V W** — 10 |
| CITES_ONLY (한 곳 발행, 나머지 인용) | E G O Q — 4 |
| 단일 소유 | L S Z — 3 |

lead 재실측 표본 4건: `W1` 충돌 확정(회고 "브랜치 갈라짐" vs 판정 "E2E 가 MCP 배선
미증명") · `O` 인용만 확정 · **M 다섯째 계열 기각**(축 A 가 회고 M8 을 별도 계열로
셌으나 M1~M19 방법표 안이다 — 이중 계수) · **I 범위 정정**(내 §24.6 은 I186~ 이라
했으나 한 파일만 본 것, 전체는 **I136~I231**).

**feedback 9종 vs `OBLIGATION_REGISTRY` 9종은 우연**(§10.7 의 2순위 닫음) — 한쪽은
실패 분류, 다른 쪽은 검사 이름. 축이 다르다.

### 13.2 사전의 형태 — 한 글자 한 행이면 문제가 그대로 남는다

`docs/IDENTIFIER_REGISTER.md`: 키는 **(글자, 문서군) 쌍**이다. `P` 는 네 행(회고
패턴 / DIRECTIVE 단계 / vault 등급 / ev-eval). 열: 뜻 · 정의 위치 · **발행 형식** ·
인용 접두 · 상태(`OWNER`/`CITES_ONLY`/`COLLIDES`/`EXTERNAL`, 닫힘).
`ADOPTION_REGISTER` 의 골격을 그대로 물려받았다. 41행.

### 13.3 게이트가 등록부의 오류를 즉시 잡았다 — 이것이 게이트의 값

`test_identifier_register.py`(24 테스트, TDD)를 먼저 쓰고 등록부를 채웠다. 첫 실행:

- **정의 위치 행 번호 27건 중 22건이 틀렸다** — haiku 회신의 `~200`·`~550` 같은
  근사치를 그대로 옮겨 적었다. 실측으로 전부 교체(W@retro 200→188, C@retro 176→1224 …).
- **표 셀 안의 정규식은 `|` 를 품을 수 없다** — `\|` 도 `[|]` 도 markdown 이 셀
  구분자로 자른다. 계약을 바꿨다: 등록부는 **셀 내부 모양만** 적고(`\*{0,2}G(\d+)…`),
  표 첫 셀 골격 `^\| … \|` 는 게이트가 붙인다.
- **회고 G 의 발행 형식이 시간에 따라 바뀌었다** — G1~G8 은 `| G1 |`, 이후 `| **G9** |`,
  일부 `| **G66 BLOCKER** |`. 하나로 강제하면 초기 24개가 위반이 된다. 정규식을
  관행에 맞춰 넓히되(굵기 선택·수식어 허용) **표 첫 셀**이라는 핵심은 유지 — G164
  산문·P24~P26 괄호형이 그것을 벗어난 것이다.
- **인벤토리 검사가 haiku 2축이 놓친 계열을 잡았다** — `V@rulings` **87행**: 우리 판정문 수신 검증 절이 매번 `V1·V2…` 를 매기는데 15개 이상 판정문에 각각 독립 발행된다. 회고 V(동결 버전)·DIRECTIVE V(저장 전 검증)와 다른 **셋째 뜻**. 사람이 읽어도 놓치고 기계가 세면 나온다.
- **P24·P25·P26 은 표 행 없이 발행됐다** — 셋 다 이 세션이 만들었고, `**P25**(설명)`
  꼴이라 순수 표셀 추출기가 놓친다. 게이트가 잡았다.

### 13.4 안 한 것

- 형식이 적힌 계열은 다섯(G·P·M·W·R 의 retro 행). 나머지는 `—` 로 검사 제외 —
  verbatim 문서는 우리가 형식을 정할 수 없고, 나머지는 표·산문 혼재.
- haiku 판정 14건 중 lead 재실측은 표본 4건. 나머지는 회신 그대로.
- **충돌은 하나도 없애지 않았다.** 처방은 인용 접두이고 등록부가 그것을 적었다.

### 13.5 역방향 — 한 뜻에 여러 글자 (사용자 질문이 잡은 누락)

사용자: "A-Z에서 의미 대응 관계도 매핑한거지? P같은 것도 중복이 많으니까 problem
pattern 등 있고." **반만 했다.** 등록부는 (글자, 문서군) → 뜻의 **순방향**만 담았다.
뜻 → 글자의 **역방향**을 등록부의 뜻 열에서 개념 어휘를 채취해 실측했다:

| 개념 | 글자 수 | 글자 | 발행 행 |
|---|---:|---|---:|
| **문제/결함**(issue·finding·defect) | **7** | B D F G I R W | 8 |
| **검증 항목/방법**(check·method) | **6** | B C D F M V | 9 |
| **등급/레벨**(class·level) | **5** | L M P S Z | 6 |
| 규칙/배제 | 2 | D E | 3 |
| 단계/마일스톤 | 2 | M P | 2 |
| 출처/참조 · 요건/질문 | 2 · 2 | O R · Q R | 2 · 2 |
| 불변식 · 버전/동결 · 패턴 | 1 · 1 · 1 | I · V · P | 2 · 2 · 1 |

**문제의 진짜 형태는 등록부가 본 것과 반대다.** 순방향 충돌(`P` 4중)은 *같은 글자가
다른 것을 뜻함* — 독자가 오독한다. 역방향 중복(문제 7글자)은 *같은 것이 다른 글자로
불림* — 검색·집계가 불가하다. "저장소 전체에서 발견된 결함이 몇 개인가"에 답하려면
G·I·W·R·B·D·F 일곱 계열을 합쳐야 하고, 그 합산 규칙은 어디에도 없다.

앞선 haiku 감사 2축은 이 축을 **아예 묻지 않았다** — 질문이 "같은 번호가 다른 뜻인가"
였다. 사용자 질문이 잡았다.

**패턴(P@retro)은 실제로는 중복이 적다** — 역방향에서 패턴을 뜻하는 글자는 P 하나다.
"P 가 중복이 많다"의 실체는 순방향(P 가 4뜻)이지 역방향이 아니다.
