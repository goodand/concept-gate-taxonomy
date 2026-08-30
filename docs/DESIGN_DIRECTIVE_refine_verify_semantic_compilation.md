# DESIGN DIRECTIVE — Refine ↔ Verify Semantic Compilation Architecture (수정 지시)

- 수신: **2026-08-22**
- 도착 경로: 사용자가 외부 설계 담당의 설계 수정 지시를 전달. 동반 파일:
  [`semantic_oracle_set_handoff_v0.1.yaml`](semantic_oracle_set_handoff_v0.1.yaml)
  (같은 커밋으로 저장, `status: design-confirmed`)
- 지위: **구속력 있는 설계 지시.** D-H1a-* 채널과 같은 외부 설계 담당이 작성.
  단, H1a 실험이 아니라 **제품 아키텍처 수준**이므로 D-H1a 번호를 쓰지 않고
  `docs/`에 둔다 (선례: `DIRECTIVE_2026-07-29_operations_change.md`)
- 저장 방법: 이 세션 트랜스크립트에서 **verbatim 추출**(운영 세션이 옮겨 적지
  않음 — 전사 오류 방지, D-H1a-16 복원과 같은 방법). 본문 sha256: `df10eecffda4d3d7e07723efc81da22d4219a0c3c1b42d77c5993bba163f278e`
- 지시문 §35가 요구하는 7항목 응답과 구현 계획은 **별도 문서로 후속** —
  이 파일은 지시 원문의 정본 보존이다
- **선행 설계 (2026-08-30 연결 — 수신 당시 이 간선이 없었다)**: 이 지시가
  다루는 obligation·candidate·provenance 위의 **상태 갱신 대수**는 6주 먼저
  [[notes/research/logical-revision/mechanism_spec|Mechanism Spec]] 이 확정해
  두었다(feedback algebra 9종 · rollback frontier · obligation lifecycle ·
  **abstention** — 이 지시에는 없는 개념). 그 명세의 자산 배치는
  [[notes/research/logical-revision/atp-verifier-inferential-subtree-subflow-research.v4|ATP v4]]
  (기제 슬롯 S1~S14). 관계는 **상보적**이다 — 이 지시는 권한 경계(Refine/Verify/
  Certified/Kernel)를, Mechanism Spec 은 갱신 허용성(commitment/rollback/abstention)을
  다룬다. **주의: 두 문서가 각자 I1~I7/I11 을 매기며 내용이 다르다** —
  이쪽 I3 는 "Verify 는 graph 를 쓰지 않는다", 그쪽 I3 는 "verified-region
  protection". 인용할 때 계열을 밝혀라. 단절의 발견과 실측은
  [[REFINE_VERIFY_STAGE_SURVEY_20260830]] §10~§11.

## 운영 세션의 저장 전 검증 (2026-08-22)

지시문의 **사실 전제**를 커밋된 기준선(`KERNEL_INTEGRATION_SURVEY.md`)과 코드
실측으로 대조했다. 지시가 도착했기 때문에 옳다고 가정하지 않는다.

### 확인된 전제 (지시문이 옳게 딛고 있는 것)

| # | 지시문 전제 | 실측 |
|---|---|---|
| V1 | §27 BEFORE 파이프라인(snapshot/span/hash → concept JSON → essential DAG → CompositionGate → OWL → HermiT) | ✅ `cg_normalizer`(snapshot/span/sha256), `concept_gate_v7`(essential 78개소·CompositionGate 12개소), `cg_owl`(HermiT) 전부 실재 |
| V2 | I11(Verify는 patch를 반환하지 않는다)은 이미 충족 | ✅ `cg_obligations.ObligationResult`에 replace_with/auto_patch류 필드 0건 |
| V3 | I7(Oracle 격리)의 집행 선례 존재 | ✅ codex 실험의 `hidden_gold/` 분리, H1a mutation pack의 answer key 분리 반환 |
| V4 | 의미 그래프 cycle 검사는 존재 | ✅ `relation.acyclicity`(CompositionGate) |
| V5 | I9(정규화 ≠ 판정)의 기존 등가물 | ✅ `cg_obligations`의 세탁 차단(UNKNOWN이 PASS 차단, 필드 부재 ≠ 위반 0건) + H1a compiler의 fail-closed `proven_families` |

### 실측으로 확정된 진짜 delta (지시가 요구하고 코드에 없는 것)

| # | 항목 | 실측 |
|---|---|---|
| D1 | **I8: ERROR verdict** — `cg_obligations.Verdict`는 PASS/FAIL/UNKNOWN뿐. "판단 근거 부족"과 "도구 실패"가 현재 구별되지 않는다(`on_unavailable`이 흡수). 루트 게이트의 BLOCKED 어휘와의 매핑 결정 필요 | `grep ERROR cg_obligations.py` → 0건 |
| D2 | **§7: fingerprint/canonical hash primitive** — `conceptgate/`에 부재. 단 codex 라인 `_receipt.py::canonical_bytes`가 재사용 후보(survey §3 C1) | grep 0건 |
| D3 | **I10: certification dependency cycle 검사** — 어디에도 없음 | grep 0건 |
| D4 | **§11–13: Quantifier/Modal/LogicalOperator IR** — 부재 (P3로 명시된 것과 일치) | grep 0건 |
| D5 | **§4.2/§16: obligation ↔ graph revision 결박** — `ObligationResult.depends_on`은 있으나 revision 필드 없음 | 판독 |
| D6 | **§17: oscillation 검출** — 반복 루프 자체가 아직 없으므로 검출기도 없음 | — |
| D7 | **§15: CertificationProfile** — `min_assurance`(의무 단위)는 있으나 claim-kind 프로파일은 없음. registry seam이 부착 지점 | 판독 |

### 저장소에 기록이 없는 전제 (모순 아님 — 기록 공백)

- §0 "현재 채택된 중심 구조: Source → Refine ↔ Verify → …" — **이 채택의
  저장소 내 기록이 없다** (`grep -rl Refine docs/` 0건, taxonomy 포함).
  채택은 설계 담당과의 저장소 밖 왕복에서 이뤄진 것으로 보이며, **이 파일이
  그 채택의 첫 저장소 내 기록**이 된다.

### 동반 yaml과의 어휘 불일치 1건 (설계 담당 확인 필요)

- 지시문 I8: `FAIL / UNKNOWN / ERROR`
- yaml `evaluation_protocol.v1.result_enum`: `PASS / FAIL / UNSCORABLE / ERROR`
- **`UNKNOWN`과 `UNSCORABLE`이 같은 상태인가?** 같다면 한 어휘로 통일해야
  하고(지시문 §1.1 정신: "판정 어휘를 새로 만들지 않는다"), 다르다면 그 구별이
  문서화돼야 한다. 구현 착수 전 확인 대상으로 등재.

### 검증하지 않은 것 (정직 고지) — **2026-08-22 저장 직후 C축 실측 완료, 아래로 대체**

### C축 출처 검증 (2026-08-22, haiku 감사 + 상위 finding 직접 재실측)

| id | 실체 | 제목 필드 |
|---|---|---|
| O1 | ✅ **확인** — 초록이 quantifier scope disambiguation 코퍼스임을 명시 (Rasmussen & Schuler, LREC 2020) | ⚠ **부정확** — 실제 제목은 "A Corpus of Encyclopedia Articles with Logical Forms" |
| | > **정정 (2026-08-22, corpus 확보 조사 후)**: 이 표의 최초 판은 O1을 ~~CC BY 4.0~~으로 적었다(Anthology 정책 가정). **논문 PDF 원문은 "licensed under CC-BY-NC"(ELRA)** — 로컬 PDF 스트림 추출로 실측. corpus 데이터 자체는 별도 LICENSE 부재. 재배포 조건은 미확정(RESEARCH_RESULT_o1_corpus_access.md) | |
| O2 | ✅ 확인 (Williamson et al. 2021) | ⚠ 실제: "Intensionalizing Abstract Meaning Representations: Non-Veridicality and Scope" |
| O3 | ✅ **확인** — 초록: "a controlled dataset of … syllogisms in propositional and modal logic"을 소개 (Wang & Shi, ACL 2025) | ⚠ 부정확 — yaml의 title은 설명어 |
| R1 | ✅ 확인 (Bentzen, arXiv 1910.01697) | ⚠ 실제: "A Henkin-style completeness proof for the modal logic S5" |
| R2 | ✅ 확인 | 부제 누락뿐 |
| G1/S1 | ✅ PMB 정상 운영 | — |
| O1-supp | ⛔ ISO 페이지 HTTP 403 — **검증 불가(BLOCKED)** | — |

haiku가 O1·O3를 REFUTED로 보고했으나 **직접 재실측으로 실체-확인/제목-부정확으로
정정**했다(제목 불일치 ≠ 자원 불일치). **설계 담당 확인 항목 2건 추가**:
① yaml의 `source_authority.title`들을 논문 **verbatim 제목**으로 교체할 것 —
yaml 자신의 `fixture_template.source_locator`가 source-faithful 표기를
요구하므로 설명어 제목은 fixture provenance를 감사 불가로 만든다.
② ISO 24617-12는 paywall 뒤라 fixture 저작 시 접근 수단 필요.

---

## 지시문 원문 (verbatim, 트랜스크립트 추출)

# 실험 운영 에이전트용 설계 수정 지시 — Refine ↔ Verify Semantic Compilation Architecture

## 0. 작업 성격

이 작업은 기존 시스템의 전면 재설계가 아니다.

현재 채택된 중심 구조:

```text
Source
   ↓
Refine ↔ Verify
   ↓
Certified Projection
   ↓
Reason / Derive
   ↓
Task / Evaluation
```

를 유지하면서, 다음 문제를 수정한다.

1. Shared Semantic Kernel의 책임 경계를 더 엄격하게 정의한다.
2. Refine과 Verify가 공유해도 되는 기능과 공유하면 안 되는 판단을 구분한다.
3. semantic graph의 stable identity와 canonical hashing을 공통 primitive로 추가한다.
4. quantifier/modal scope를 표현하기 위해 최소 IR primitive를 보완한다.
5. fixed-point뿐 아니라 oscillation을 검출한다.
6. obligation이 오래된 graph revision에 적용되는 문제를 막는다.
7. certification requirement를 claim 종류별로 선언적으로 정의할 수 있게 한다.
8. Shared Kernel이 semantic judge 또는 certification engine으로 팽창하지 못하도록 negative contract를 둔다.
9. Oracle, evaluator, reasoner의 authority가 Refine/Verify로 역류하지 않도록 한다.

이 변경의 목적은:

```text
더 많은 pipeline stage 추가
```

가 아니라:

```text
기존 Refine / Verify / Shared Kernel의 contract를 더 정확하게 만들기
```

이다.

---

# 1. 반드시 유지해야 하는 기존 architecture invariants

다음 원칙은 수정 대상이 아니다.

## I1. Semantic Graph is state

```text
Semantic Graph is state;
Refine and Verify iteratively converge it.
```

Semantic Graph는 현재 시스템의 semantic interpretation 상태다.

별도의 normalize-result, resolve-result, verification-result graph들을 계속 증식시키지 않는다.

---

## I2. Refine만 asserted semantic graph를 수정한다

Refine의 authority:

```text
Read Source: YES
Read Semantic Graph: YES
Read Obligations: YES

Write candidate/asserted semantic graph: YES

Certify semantic claim: NO
Write reasoner entailment: NO
Write evaluator result: NO
```

Refine은 generator이자 repairer다.

그러나:

```text
Refine proposal
≠ truth
≠ certified assertion
```

이다.

---

## I3. Verify는 asserted graph를 수정하지 않는다

Verify authority:

```text
Read Source: YES
Read Semantic Graph: YES

Write asserted semantic graph: NO

Emit validation result: YES
Emit obligation: YES
Determine certification eligibility: YES

Write reasoner entailment: NO
```

Verify가 실패를 발견했다고 해서 graph를 직접 patch하면 안 된다.

---

## I4. Shared definitions are allowed; shared judgments are dangerous

공유 가능한 것:

```text
IR schema
graph traversal
canonicalization primitives
relation/operator definitions
constraint definitions
evidence lookup
source/span/hash access
```

공유하면 안 되는 것:

```text
candidate selection result
semantic-support judgment
PASS/FAIL semantic judgment
certification verdict
repair decision
Oracle answer
evaluation verdict
```

---

## I5. Open vocabulary, closed inference semantics

새 concept/relation은 표현할 수 있다.

예:

```text
provisional:catalytic_regulator
```

그러나 formal inference authority는 자동 부여하지 않는다.

```text
Representable
≠ Inferentially licensed
```

Reasoner는 capability registry에서 명시적으로 승인된 relation/operator만 이용한다.

---

## I6. Candidate / Certified / Entailed를 구분한다

개념적으로 반드시 구별한다.

```text
Candidate
= Refine proposal

Certified
= source + required verification을 통과한 asserted meaning

Entailed
= Certified representation으로부터 reasoner가 유도한 meaning
```

물리적인 DB를 3개 만들 필요는 없다.

projection/view로 구현할 수 있다.

---

## I7. Oracle은 evaluation-only다

절대 허용하지 않는다.

```text
Oracle → Refine
Oracle → Verify
```

허용되는 경로:

```text
Certified / Predicted Graph
          ↓
       Evaluate
          ↑
        Oracle
```

Oracle의 정답은 tested run의 generation/certification path에 들어가면 안 된다.

---

## I8. FAIL / UNKNOWN / ERROR를 구분한다

```text
FAIL
= semantic/formal requirement가 충족되지 않음

UNKNOWN
= 판단에 필요한 근거가 부족하거나 확인되지 않음

ERROR
= 실행기/프로세스/tool failure
```

예:

```text
ontology inconsistent
→ FAIL

HermiT timeout/crash
→ ERROR
```

---

# 2. 이번 수정에서 새로 추가하는 architecture invariants

기존 invariant에 다음을 추가한다.

## I9. Shared Kernel may normalize representations, but must never normalize uncertainty into truth

Shared Kernel은:

```text
∀x∃y R(x,y)
```

의 bound variable 이름을 canonical하게 바꿀 수 있다.

그러나:

```text
UNKNOWN semantic interpretation
```

을:

```text
canonicalized → PASS
```

처럼 변경해서는 안 된다.

즉:

```text
representation normalization
≠ semantic adjudication
```

이다.

---

## I10. Certification dependency must be acyclic

Semantic Graph 자체에는 cycle이 있을 수 있다.

예:

```text
A related_to B
B related_to A
```

는 허용될 수 있다.

그러나 certification/proof provenance에는 다음 cycle을 금지한다.

```text
claim C certified because D
D derived because C is certified
```

따라서:

```text
Semantic Graph cycle: MAY BE VALID

Certification Dependency cycle:
MUST BE INVALID
```

이다.

---

## I11. Verify obligation은 repair hint이지 정답 graph가 아니다

Verify가 다음처럼 반환해서는 안 된다.

### 금지

```json
{
  "status": "FAIL",
  "replace_with": {
    "quantifier": "forall",
    "scope": "..."
  }
}
```

이 구조에서는 Verify가 사실상 graph writer가 된다.

권장:

```json
{
  "target": "claim:c17",
  "check": "quantifier_scope",
  "status": "FAIL",
  "repairability": "repairable",
  "diagnostic": {
    "code": "BINDING_SCOPE_CONFLICT",
    "message": "bound variable escapes quantifier scope"
  }
}
```

Refine이 repair 방법을 결정해야 한다.

---

# 3. BEFORE → AFTER 요약

## 3.1 Shared Semantic Kernel

### BEFORE

```text
Shared Semantic Kernel
├─ Graph Identify / Traverse
├─ Canonicalization
├─ Constraint Definitions
└─ Evidence / Provenance Access
```

문제:

* graph identity와 versioning이 명시되지 않음
* canonical hash가 ad-hoc하게 구현될 가능성
* relation/operator capability registry 위치가 불분명
* Kernel이 점차 validation engine으로 팽창할 위험
* O1/O2/O3 IR이 필요한 logical connective 정의가 부족

### AFTER

```text
Shared Semantic Kernel
├─ Core IR Types
├─ Stable Identity / Fingerprinting
├─ Graph Identify / Traverse
├─ Canonical Serialization / Hashing
├─ Restricted Canonicalization Primitives
├─ Constraint Definitions
├─ Relation / Operator Capability Registry
└─ Evidence / Provenance Access
```

Shared Kernel은 다음 기능을 **절대 제공하지 않는다**.

```text
choose_candidate()
semantic_support_verdict()
certify()
repair_semantics()
infer_entailment()
oracle_compare()
```

---

# 4. Refine / Verify contract 수정

## 4.1 Refine — BEFORE

```text
Refine(
    Source,
    Graph_t,
    Obligations_(t-1)
)
→ Graph_(t+1)
```

기능:

* atomic claim 제안
* relation 후보
* scope/binding 구성
* graph repair

위 구조 자체는 유지한다.

---

## 4.2 Refine — AFTER

함수 계약을 revision-aware하게 만든다.

```text
Refine(
    source_snapshot,
    graph_snapshot_t,
    obligations_for_graph_t
)
→ graph_revision_(t+1)
```

필수 조건:

```text
obligation.graph_revision
==
graph_snapshot_t.revision
```

이 아니면 obligation을 적용하지 않는다.

예:

```json
{
  "graph_revision": "g:17",
  "obligation_id": "o:42",
  "target": "claim:c17"
}
```

Refine은 stale obligation을 받으면:

```text
STALE_OBLIGATION
```

으로 무시하거나 재검증을 요청한다.

---

# 5. Verify — BEFORE / AFTER

## BEFORE

```text
Verify(
    Source,
    Graph_t
)
→ Obligations_t
```

## AFTER

```text
Verify(
    source_snapshot,
    graph_snapshot_t,
    certification_profile
)
→ VerificationReport_t
```

VerificationReport는:

```text
checks
+
obligations
+
certification eligibility
```

를 포함할 수 있다.

그러나 asserted graph patch는 포함하지 않는다.

---

# 6. Semantic Graph 수정

## BEFORE

Semantic Graph가 shared mutable state처럼 해석될 위험이 있었다.

## AFTER

논리적으로는 state이지만 각 iteration에서는 **immutable snapshot/revision**으로 취급한다.

예:

```yaml
SemanticGraphSnapshot:
  graph_id: "semantic-graph-01"
  revision: 17

  parent_revision: 16

  nodes: [...]
  edges: [...]
  claims: [...]

  canonical_hash: "sha256:..."
```

Refine은:

```text
revision 17
→ revision 18
```

을 만든다.

Verify는 revision 17을 수정하지 않는다.

---

# 7. Stable Identity / Fingerprint 추가

Shared Kernel에 다음 primitive를 추가한다.

```text
node_fingerprint(node)
claim_fingerprint(claim)
graph_fingerprint(graph)
obligation_target_fingerprint(target)
```

목적:

* fixed-point
* oscillation
* provenance
* graph diff
* stale obligation detection
* canonical comparison

을 하나의 identity 규칙으로 통일한다.

주의:

fingerprint가 semantic truth를 의미하지 않는다.

```text
same canonical fingerprint
→ same normalized representation

NOT
→ same empirical truth
```

---

# 8. Canonicalization 경계

Canonicalization은 Shared Kernel에 유지한다.

그러나 v0 범위를 제한한다.

## v0에서 허용

```text
alpha-renaming
deterministic node ordering
deterministic argument ordering
registered alias normalization
syntactic sugar expansion
stable source/evidence ordering
canonical serialization
```

예:

```text
∀x ∃y R(x,y)
```

와:

```text
∀a ∃b R(a,b)
```

를:

```text
FORALL v0
  EXISTS v1
    R(v0,v1)
```

로 normalize하는 것은 허용한다.

---

## v0에서 금지

```text
arbitrary beta reduction
eta equivalence
logical theorem equivalence
quantifier reordering
modal equivalence
arbitrary associativity rewriting
arbitrary commutativity rewriting
model equivalence
```

예:

```text
∀x∃y R(x,y)
```

를:

```text
∃y∀x R(x,y)
```

로 바꾸는 것은 normalization이 아니다.

semantic change다.

---

# 9. Constraint Definitions 수정

## BEFORE

```text
Shared Constraint Definitions
```

라는 이름이 너무 넓어서 checker까지 Kernel로 흡수될 가능성이 있다.

## AFTER

Shared Kernel은 오직 선언적 definition을 제공한다.

예:

```yaml
RelationDefinition:
  id: part_of
  status: canonical

  domain:
    - Entity

  range:
    - Entity

  capabilities:
    transitive: true
    inverse: has_part
    supports_owl: true
```

Kernel API:

```text
get_relation_definition(id)
get_operator_definition(id)
get_constraint_definition(id)
```

---

## Refine의 사용

```text
definition 조회
→ invalid candidate 생성 가능성 감소
```

예:

```text
part_of range must be Entity
```

를 보고 후보를 만들 수 있다.

---

## Verify의 사용

Verify는 같은 definition을 읽되 별도의 judgment를 만든다.

```text
claim
+
constraint definition
→ PASS / FAIL / UNKNOWN / NA
```

핵심:

```text
shared definition
≠ shared verdict
```

---

# 10. Evidence / Provenance Access 수정

## Shared Kernel 책임

```text
evidence ID lookup
source snapshot lookup
span lookup
hash lookup
quote extraction
provenance traversal
```

예:

```text
get_evidence(evidence_id)
verify_span(evidence_ref)
get_source_snapshot(source_id)
```

---

## Verify 전용 책임

다음은 Kernel에 넣지 않는다.

```text
does_evidence_semantically_support_claim()
```

이것은 semantic judgment다.

즉:

```text
Evidence Resolver
→ Shared Kernel

Semantic Support Checker
→ Verify
```

---

# 11. 최소 Semantic IR 수정

기존 triple 중심 표현에 다음 최소 primitive를 추가한다.

## Term

```text
EntityRef
Variable
```

## Formula

```text
PredicateApplication
Quantifier
ModalOperator
LogicalOperator
```

## Supporting objects

```text
Claim
EvidenceRef
SourceRef
```

---

# 12. LogicalOperator 추가

이 primitive는 새로 추가한다.

이유:

다음을 구조적으로 구별해야 한다.

```text
□(P → Q)
```

vs

```text
P → □Q
```

따라서 최소:

```text
IMPLIES
AND
OR
NOT
```

을 표현할 수 있어야 한다.

LogicalOperator도 inference authority와 분리한다.

예:

```yaml
LogicalOperator:
  id: implies
  status: canonical
```

이 object가 있다고 해서 arbitrary theorem inference를 자동 실행하지 않는다.

---

# 13. Scope / Binding topology

`de_re`, `de_dicto`, `forall_exists` 같은 label을 primitive truth로 만들지 않는다.

예:

```text
EXISTS x
  BOX
    P(x)
```

와:

```text
BOX
  EXISTS x
    P(x)
```

의 graph topology에서 de re/de dicto를 파생한다.

마찬가지로:

```text
FORALL x
  EXISTS y
    R(x,y)
```

vs:

```text
EXISTS y
  FORALL x
    R(x,y)
```

를 nesting으로 표현한다.

---

# 14. Capability Registry 수정

open vocabulary / closed inference 원칙을 코드 계약으로 명시한다.

예:

```yaml
RelationCapability:
  relation_id: part_of

  lifecycle:
    canonical: true
    provisional: false

  inference:
    transitive: true
    inverse: has_part
    supports_owl: true
```

provisional relation:

```yaml
RelationCapability:
  relation_id: catalytic_relation#tmp

  lifecycle:
    canonical: false
    provisional: true

  inference: {}
```

Reasoner invariant:

```text
no explicit capability
→ no formal inference authority
```

---

# 15. CertificationProfile 추가

이것은 새 top-level module이 아니다.

Verify가 읽는 declarative profile이다.

## 문제

모든 claim에 다음을 요구하면 안 된다.

```text
source PASS
relation PASS
scope PASS
binding PASS
...
```

simple taxonomy claim과 quantified modal claim의 required checks는 다를 수 있다.

---

## AFTER

예:

```yaml
CertificationProfile:
  id: simple_source_relation_v0

  applies_to:
    claim_kind: relation_assertion

  required:
    - source_reference
    - source_integrity
    - semantic_support
    - relation_admissibility

  allowed_na:
    - quantifier_scope
    - modal_scope
```

quantified claim:

```yaml
CertificationProfile:
  id: quantified_semantic_claim_v0

  required:
    - source_reference
    - source_integrity
    - semantic_support
    - variable_binding
    - quantifier_scope
```

Certified Projection:

```text
claim is certified
iff
its CertificationProfile.required checks are PASS
```

---

# 16. Obligations — BEFORE / AFTER

## BEFORE

```json
{
  "claim_id": "c17",
  "checks": {
    "source_support": "PASS",
    "relation": "PASS",
    "scope": "UNKNOWN"
  }
}
```

## AFTER

atomic obligation을 기본으로 한다.

```yaml
Obligation:
  obligation_id: "o:42"

  graph_revision: 17

  target:
    kind: claim
    id: "c17"

  check: quantifier_scope

  status:
    UNKNOWN

  repairability:
    repairable

  evidence_refs:
    - ev13

  depends_on:
    - o:38

  diagnostic:
    code: QUANTIFIER_SCOPE_UNRESOLVED
    message: >
      Variable binding is well formed but the relative nesting
      of quantifier q1 and q2 is not established by the current graph.
```

---

## Obligation에 넣지 않을 것

```text
correct_graph
oracle_answer
replacement_claim
auto_patch
expected_semantics
```

---

# 17. Fixed-point detection — BEFORE / AFTER

## BEFORE

```text
hash(Graph_t) == hash(Graph_t+1)
AND
hash(Obligations_t) == hash(Obligations_t+1)
```

문제:

```text
G1 → G2 → G1 → G2
```

같은 oscillation을 잡지 못한다.

---

## AFTER

각 iteration에:

```text
state_key =
hash(
    canonical_graph,
    canonical_obligations
)
```

를 만든다.

최근 revision history에 동일 state_key가 이미 있으면:

```text
termination = OSCILLATION
result = UNRESOLVED
```

로 끝낸다.

---

## hard termination conditions

```text
A. required obligations all PASS
→ CERTIFIED

B. irreparable FAIL
→ REJECTED

C. repeated canonical state
→ UNRESOLVED / OSCILLATION

D. iteration budget exceeded
→ UNRESOLVED / BUDGET_EXHAUSTED

E. adjacent state unchanged
→ UNRESOLVED / FIXED_POINT
```

---

# 18. Progress metric

다음 metric은 diagnostic으로만 사용할 수 있다.

```text
#FAIL
#UNKNOWN
#unmapped
```

예:

```text
(1, 4, 2)
→
(0, 3, 1)
```

은 진전으로 볼 수 있다.

그러나 이 metric을 hard monotonic invariant로 만들지 않는다.

올바른 decomposition이 일시적으로:

```text
UNKNOWN 1
→ FAIL 2
```

를 만들 수 있기 때문이다.

---

# 19. Reasoner boundary

Reasoner가 inconsistency를 발견해도 graph를 직접 repair하지 않는다.

## 금지

```text
HermiT inconsistency
→ automatically rewrite Semantic Graph
```

## 허용

```text
formal checker
→ Verify
→ formal obligation
→ Refine repair
```

예:

```yaml
Obligation:
  target: graph
  check: owl_consistency
  status: FAIL

  diagnostic:
    code: FORMAL_INCONSISTENCY
```

다만 Reasoner가 정답 patch를 반환하지 않는다.

---

# 20. 같은 reasoner implementation의 두 authority

같은 HermiT를 사용할 수 있다.

하지만 호출 역할은 분리한다.

## Verify-side

```yaml
mode: admissibility_check
authority: certification_check
```

질문:

```text
이 asserted representation을 Certified로 허용할 수 있는가?
```

---

## Derive-side

```yaml
mode: derive
authority: entailment
```

질문:

```text
Certified representation으로부터 무엇이 추가로 entail되는가?
```

같은 implementation이어도 origin/provenance를 분리한다.

---

# 21. Oracle leakage 방지

API 수준에서 차단한다.

Refine signature에는 Oracle 입력이 없어야 한다.

```text
Refine(
  Source,
  Graph,
  Obligations
)
```

Verify signature에도 Oracle이 없어야 한다.

```text
Verify(
  Source,
  Graph,
  CertificationProfile
)
```

Oracle은 오직:

```text
Evaluate(
  PredictedCanonicalIR,
  OracleCanonicalIR
)
```

에서 사용한다.

---

# 22. Oracle Adapter와 Shared Kernel 관계

Oracle Adapter는 Shared Kernel의:

```text
IR type
canonical serialization
alpha-renaming
```

같은 **표현 primitive**를 재사용할 수 있다.

그러나 production semantic compiler의:

```text
candidate selection
semantic support result
certification result
```

는 재사용하지 않는다.

그렇지 않으면 predicted representation과 Oracle representation이 같은 judgment machinery로 만들어져 평가 독립성이 약해진다.

---

# 23. Candidate / Certified / Entailed provenance

모든 claim에는 최소한 다음 provenance를 유지한다.

```yaml
claim:
  id: c17

  origin:
    asserted | derived

  lifecycle:
    candidate | certified | rejected

  asserted_by:
    refine_revision: 17

  validation:
    profile: quantified_claim_v0

  derived:
    reasoner: null
    derived_from: []
```

derived claim:

```yaml
claim:
  id: d31

  origin: derived

  derived:
    reasoner: HermiT
    derived_from:
      - c17
      - c18
```

`derived`를 무조건 lifecycle status로 만들 필요는 없다.

origin으로 분리할 수 있다.

---

# 24. Certification provenance DAG

별도 DB를 만들 필요는 없다.

그러나 dependency edge type을 구분한다.

```text
semantic_relation
certification_dependency
derivation_dependency
evidence_dependency
```

Certification dependency graph만큼은 cycle 검사한다.

예:

```text
c17 certification
→ depends on c18 certification
→ depends on c17 certification
```

이면:

```text
CERTIFICATION_CYCLE
```

로 FAIL 또는 UNKNOWN 처리한다.

---

# 25. 최소 E2E 구현 순서

전체 semantic Oracle부터 구현하지 않는다.

먼저 기존 ConceptGate 자산을 새 authority contract 아래에서 끝까지 관통시킨다.

## E2E-v0

### Input

기존 relation fixture:

```text
concept
feature
evidence
```

### Step 1 — Source snapshot

기존 snapshot/span/hash 기능 재사용.

### Step 2 — Refine

```text
Candidate relation claim 생성
```

예:

```text
engine
--structural_composition-->
car
```

### Step 3 — Verify

검사:

```text
source reference
span/hash
semantic support
relation admissibility
```

### Step 4 — Obligation

문제가 있으면 Refine에 구조화된 obligation 반환.

### Step 5 — one repair iteration

Refine이 graph revision을 새로 생성.

### Step 6 — Certified Projection

required checks PASS인 claim만 certified view에 포함.

### Step 7 — 기존 subsystem 재사용

```text
Certified taxonomy relation
→ essential DAG

Certified composition relation
→ CompositionGate
```

### Step 8 — optional OWL/HermiT

```text
Certified
→ OWL
→ HermiT
→ Derived
```

### Step 9 — provenance 검증

반드시 다음을 구별할 수 있어야 한다.

```text
Candidate
Certified asserted
Reasoner-derived
```

---

# 26. E2E-v1 이후 O1/O2/O3 확장

v0가 통과한 뒤 다음 IR capability를 활성화한다.

```text
Quantifier
Variable
Binding
ModalOperator
LogicalOperator
Scope
PredicateApplication
```

중요:

새 top-level stage를 만들지 않는다.

다음처럼 하지 않는다.

### 금지

```text
QuantifierProcessor
→ ModalProcessor
→ DeReProcessor
→ ScopeResolver
→ SemanticVerifier
```

대신:

```text
Refine plugins
+
Verify checks
+
Shared IR primitives
```

로 넣는다.

---

# 27. BEFORE / AFTER — 전체 architecture

## BEFORE

```text
Natural Language
   ↓
snapshot / span / hash
   ↓
sense / feature / relation representation
   ↓
concept JSON
   ↓
essential DAG
   ↓
composition graph
   ↓
CompositionGate
   ↓
OWL
   ↓
HermiT
```

주요 공백:

```text
Source
  ⊨ ?
Generated Semantic Claim
```

---

## AFTER

```text
                     ┌──────────────────────┐
                     │                      │
                     ▼                      │
Source ───────→ Refine ─────→ Semantic Graph
                 ▲                 │
                 │                 ▼
                 └── Obligations ← Verify
                                   │
                                   ▼
                         Certified Projection
                                   │
                      ┌────────────┴────────────┐
                      ▼                         ▼
               Reason / Derive              Task / Output
                      │                         │
                      ▼                         ▼
                  Entailed                  Evaluation
                                                ▲
                                                │
                                             Oracle
```

Shared Kernel은 Refine/Verify 아래에 위치한다.

```text
Shared Semantic Kernel
├─ Core IR Types
├─ Stable Identity
├─ Graph Traverse
├─ Canonical Serialization / Hash
├─ Restricted Canonicalization
├─ Constraint Definitions
├─ Relation / Operator Capability Registry
└─ Evidence / Provenance Access
```

---

# 28. Authority matrix — 최종 기준

| Component            |           Read Source |     Read Graph | Write Asserted Graph |         Emit Obligations | Certify Eligibility | Write Entailment | Read Oracle |
| -------------------- | --------------------: | -------------: | -------------------: | -----------------------: | ------------------: | ---------------: | ----------: |
| Refine               |                   YES |            YES |              **YES** |                       NO |                  NO |               NO |      **NO** |
| Verify               |                   YES |            YES |               **NO** |                  **YES** |             **YES** |               NO |      **NO** |
| Shared Kernel        |              indirect |            YES |                   NO |                       NO |                  NO |               NO |          NO |
| Certified Projection |                    NO |            YES |                   NO |                       NO |     projection only |               NO |          NO |
| Reason/Derive        |                    NO | Certified only |                   NO | optional diagnostic only |                  NO |          **YES** |          NO |
| Evaluate             |              optional |            YES |                   NO |                       NO |                  NO |               NO |     **YES** |
| Oracle Adapter       | published source only | Oracle IR only |                   NO |                       NO |                  NO |               NO |         YES |

이 표와 충돌하는 구현은 architecture deviation으로 취급한다.

---

# 29. Shared Kernel negative contract

다음 함수 또는 실질적으로 동일한 기능을 Shared Kernel에 추가하지 않는다.

```text
select_best_relation()
choose_semantic_parse()
judge_source_support()
semantic_truth_score()
certify_claim()
auto_repair_claim()
oracle_match_verdict()
derive_entailment()
```

embedding similarity / confidence scoring도 Kernel truth interface로 만들지 않는다.

허용:

```text
candidate lookup
alias lookup
dense retrieval
similarity retrieval
```

단 결과는 candidate일 뿐이다.

---

# 30. 리뷰 시 반드시 확인할 것

구현 후 다음 질문에 답하라.

## R1

Shared Kernel 함수 중:

```text
PASS
FAIL
UNKNOWN
certified
correct
supported
preferred
```

같은 semantic judgment를 직접 반환하는 것이 있는가?

있다면 왜 Kernel에 있어야 하는지 정당화하라.

기본값은 이동 대상이다.

---

## R2

Verify 결과가 exact graph patch를 포함하는가?

포함하면 self-certification/indirect graph-write 위험으로 BLOCKER 처리한다.

---

## R3

Refine이 자신의 이전 confidence/rationale을 Verify의 semantic evidence로 사용하게 하는 경로가 있는가?

있으면 BLOCKER.

---

## R4

Oracle 정보가 Refine 또는 Verify input에 도달할 수 있는가?

있으면 experiment leakage BLOCKER.

---

## R5

provisional relation에 inference capability가 자동 부여되는가?

있으면 BLOCKER.

---

## R6

Certified assertion과 reasoner-derived assertion이 provenance에서 구별되는가?

구별 안 되면 deterministic laundering 위험.

---

## R7

semantic graph cycle과 certification dependency cycle이 구별되는가?

구별 안 되면 BLOCKER.

---

## R8

Graph revision과 Obligation revision이 결박돼 있는가?

아니면 stale-repair 위험.

---

## R9

fixed-point detector가 2-cycle 이상 oscillation을 잡을 수 있는가?

아니면 최소 bounded-history detector를 추가한다.

---

## R10

Canonicalizer가 semantic equivalence theorem prover 역할을 시작했는가?

v0에서는 금지한다.

---

# 31. 구현 산출물 요청

운영 세션은 다음을 산출하라.

## A. Architecture delta

```text
Before
After
Changed
Unchanged
Deferred
```

형식으로 작성한다.

---

## B. Authority diff

각 component별:

```text
authority_before
authority_after
```

를 비교한다.

원칙적으로 이번 수정으로 semantic authority가 새 모듈에 추가되어서는 안 된다.

---

## C. Shared Kernel v0 API

실제 또는 pseudo API를 제시한다.

최소:

```text
IR type
identity
traverse
canonicalize
canonical_hash
constraint lookup
capability lookup
evidence lookup
```

---

## D. Obligation schema

graph revision 포함.

---

## E. CertificationProfile schema

최소 하나의 legacy relation claim profile을 제시한다.

---

## F. E2E-v0 trace

최소 하나의 실제 기존 fixture를 사용하여:

```text
Source
→ Candidate
→ Verify
→ Obligation
→ Repair
→ Certified
→ existing ConceptGate projection
→ optional Derived
```

전 과정을 trace한다.

각 transition마다:

```text
who wrote state?
what authority?
what provenance?
```

를 표시한다.

---

# 32. 이번 수정에서 하지 말 것

다음은 하지 않는다.

1. 전체 pipeline 재작성
2. 기존 essential DAG 제거
3. existing CompositionGate 제거
4. 기존 OWL/HermiT 폐기
5. 별도 Quantifier subsystem 생성
6. 별도 Modal subsystem 생성
7. 별도 DeRe subsystem 생성
8. 별도 Certified database를 성급히 도입
9. Oracle answer를 Refine/Verify에 연결
10. LLM confidence를 certification score로 사용
11. embedding similarity를 semantic truth로 사용
12. UNKNOWN을 false로 강제 변환
13. Verify가 graph를 직접 수정
14. Reasoner가 asserted graph를 자동 repair
15. evaluator failure를 same-run repair trigger로 연결

---

# 33. 구현 우선순위

## P0 — architecture integrity

먼저 구현:

```text
immutable graph revision
stable identity/hash
obligation graph binding
Shared Kernel negative boundary
candidate/certified/derived provenance
```

## P1 — legacy E2E

```text
essential_feature
structural_composition
source support
CompositionGate
Certified projection
```

## P2 — inference

```text
relation capability
OWL
HermiT
derived provenance
```

## P3 — compositional semantic IR

```text
Quantifier
Variable
Binding
ModalOperator
LogicalOperator
Scope
```

## P4 — Oracle evaluation

```text
O1
O2
O3
```

이 순서를 기본으로 한다.

Oracle 기능 때문에 P0/P1 architecture를 다시 설계하지 않는다.

---

# 34. 최종 설계 원칙

이번 변경 후에도 시스템의 핵심은 다음 네 줄이어야 한다.

```text
Refine proposes.
Verify challenges.
Certified Projection admits.
Reasoner derives.
```

그리고:

```text
Evaluate measures.
Oracle judges only at evaluation boundary.
```

Shared Kernel은 이 판단들을 통합하는 엔진이 아니다.

Shared Kernel의 역할은:

```text
같은 언어
같은 identity
같은 graph vocabulary
같은 canonical representation
같은 constraint definitions
같은 evidence addressing
```

을 Refine과 Verify에 제공하는 것이다.

최종 경계:

```text
SHARED REPRESENTATION
+
SHARED DEFINITIONS
+
SEPARATE JUDGMENTS
+
SEPARATE AUTHORITIES
```

이다.

---

# 35. 운영 세션에 대한 최종 요청

위 수정안을 기존 설계와 대조하여 검토하고 구현 계획을 제시하라.

반드시 먼저 다음을 출력하라.

```text
1. 현재 구현이 BEFORE 중 어디에 해당하는가
2. AFTER와 비교해 실제 필요한 delta가 무엇인가
3. 이미 구현된 항목은 무엇인가
4. 새 top-level module 없이 흡수 가능한 항목은 무엇인가
5. 구현하면 authority boundary가 바뀌는 항목이 있는가
6. 현재 코드에서 circularity/self-certification 위험이 실제 존재하는가
7. 최소 E2E-v0까지 필요한 변경만 무엇인가
```

그 다음 구현 순서를 제안하라.

중요:

**요청된 설계가 추상적으로 더 깨끗하다는 이유만으로 코드를 확대하지 마라.**

실제 코드에 이미 동등한 invariant가 있으면 재구현하지 말고 재사용하라.

새 abstraction은 다음을 만족할 때만 추가한다.

```text
실제 중복 제거
OR
authority ambiguity 제거
OR
certification integrity 개선
OR
E2E semantic evaluation에 필수
```

그렇지 않으면:

```text
NO CHANGE REQUIRED
```

라고 명시하라.

최우선 목표는 architecture 완성도가 아니라:

```text
기존 ConceptGate 자산을 보존하면서
Refine ↔ Verify semantic compilation cycle을
실제 E2E에서 작동시키는 것
```

이다.

