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
