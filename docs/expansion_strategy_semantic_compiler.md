# ConceptGate 확장 전략
## Evidence-Carrying Taxonomy Gate에서 Verifiable Semantic-to-OWL Compiler로
## 1. 기준선: 현재 ConceptGate가 이미 수행하는 것
현재 ConceptGate v7의 핵심 구조는 다음과 같다.
```text
자연어
→ agent가 sense·feature·relation 제안
→ snapshot/span/hash 검증
→ concepts JSON 조립 및 lint
→ essential-feature DAG
→ structural-composition graph
→ CompositionGate / UFO anti-pattern 검사
→ 선택적으로 OWL 2 DL 직렬화
→ HermiT 분류
```
현재 저장소는 `is-a`와 `has-a`를 처음부터 별도 그래프로 취급한다.
* `essential_feature`는 `is-a` DAG를 만든다.
* `structural_composition`은 part-whole composition graph를 만든다.
* CompositionGate는 반대칭, 비순환, `is-a`/`has-a` 배타성을 검사한다.
* UFOAntiPatternGate는 MixRig, PartOver, WholeOver 등을 탐지한다.
자연어 입력층도 이미 단일 호출이 아니라 다음 단계로 분리돼 있다.
```text
make_snapshot
→ lookup_senses
→ agent의 sense 선택·crosswalk
→ assemble_concepts
→ lint_concepts
→ run_pipeline
```
서버는 LLM을 직접 호출하지 않고, agent가 의미를 제안하면 normalizer가 span, hash, schema, 관계 제약처럼 기계적으로 확인할 수 있는 조건만 판정한다.
`cg_normalizer`는 confidence와 검증 상태를 분리한다. 현재 검증 사다리는 대략 다음과 같다.
```text
unverified
→ source_span_verified
→ relation_constraints_verified
→ entailment_verified
→ rejected
```
또한 snapshot의 원문과 SHA-256을 재계산하고, span 좌표와 quote가 실제 원문과 일치하는지 결정론적으로 검사한다.
OWL 계층에서는 이미 중요한 변화가 이루어졌다.
* `primitive`는 필요조건만 나타내는 `SubClassOf`로 직렬화된다.
* `defined`는 필요충분조건인 `EquivalentClasses` 계열로 직렬화된다.
* HermiT가 형식적 subsumption, equivalence, unsatisfiability를 판정한다.
* gUFO stereotype은 실제 gUFO 클래스에 punning으로 연결된다.
* 동치 클래스 그룹과 부모 유실 문제도 보정됐다.
즉 최신 ConceptGate는 더 이상 단순한 feature-set taxonomy만은 아니다. 다만 `definition_kind`, relation restriction, stereotype 같은 **OWL 입력의 의미적 정확성은 여전히 상류 agent가 제안한다.** `cg_owl`도 이 경계를 명시적으로 인정한다.
---
# 2. 현재 구조의 핵심 공백
현재 시스템이 강하게 검증하는 것은 다음이다.
```text
span이 원문에 존재하는가?
quote가 span과 같은가?
source hash가 맞는가?
입력 JSON이 schema에 맞는가?
relation_hint와 feature type이 충돌하지 않는가?
OWL 공리가 논리적으로 일관적인가?
어떤 subsumption이 모델에서 유도되는가?
```
하지만 다음은 아직 강하게 검증하지 못한다.
```text
그 span이 실제로 해당 claim을 지지하는가?
문장이 정의인지 단순 설명인지?
A is-a B인지 A uses B인지?
A가 B의 component인지 member인지?
조건이 필요조건인지 필요충분조건인지?
문서의 “가능하다”가 논리적 가능성인지 단순 불확실성인지?
생성된 OWL 공리가 원문 의미와 같은지?
```
따라서 현재 구조는 다음을 보장한다.
```text
formal model ⊨ inferred result
```
그러나 아직 다음을 직접 보장하지 않는다.
```text
document ⊨ formal model
```
확장의 중심은 HermiT 이후가 아니라 **HermiT 이전의 semantic compilation 과정**이어야 한다.
---
# 3. 메커니즘 핵심 아이디어
## 3.1 숫자 confidence가 아니라 proof obligation
확장 시스템은 LLM이 다음처럼 숫자를 제출하도록 하면 안 된다.
```json
{
  "is_a": 0.87,
  "part_of": 0.08,
  "possible": 0.72
}
```
LLM이 생성한 숫자는 검증된 확률이 아니며, threshold를 설정해도 판단 근거가 투명해지지 않는다.
대신 각 후보 공리에 대해 **타입이 있는 검증 의무**를 만든다.
```json
{
  "claim_id": "c42",
  "candidate": {
    "subject": "Square",
    "relation": "is_a",
    "object": "Rectangle"
  },
  "obligations": {
    "source_support": "PASS",
    "relation_type": "PASS",
    "generic_scope": "PASS",
    "necessity": "PASS",
    "sufficiency": "UNKNOWN",
    "role_phase_conflict": "PASS",
    "counterexample": "PASS",
    "owl_roundtrip": "PASS"
  },
  "decision": "PRIMITIVE_SUBCLASS"
}
```
각 obligation의 값은 다음처럼 제한한다.
```text
PASS
FAIL
UNKNOWN
NOT_APPLICABLE
```
숫자 score는 검색 순서나 후보 ranking에만 사용할 수 있다. 최종 승인에는 사용하지 않는다.
---
## 3.2 LLM은 proposer, verifier는 typed gate
새 구조에서 LLM은 다음만 수행한다.
* 원자 claim 후보 생성
* subject/relation/object 후보 생성
* 정의문 후보 생성
* obligation별 근거 span 제안
* 반례 후보 생성
* 실패한 obligation의 수정안 제안
LLM은 최종적으로 다음을 선언할 권한이 없다.
```text
entailed
consistent
defined
rigid
part-of verified
```
최종 상태 변경은 각각의 검증기가 수행한다.
```text
LLM proposes.
Typed gates decide.
HermiT classifies.
```
---
## 3.3 가능성을 두 종류로 분리
“가능성”은 하나의 개념으로 처리하면 안 된다.
### 문서적 가능성
문서가 다음처럼 표현하는가?
```text
may
might
can
possibly
could
is likely to
```
이것은 문장 factuality 또는 epistemic modality 문제다.
### 모델 가능성
공리 집합에 후보 공리를 추가했을 때 모델이 존재하는가?
```text
SAT(O ∪ {candidate axiom})
```
즉 다음과 같다.
```text
충돌 없이 해석 가능한 모델이 하나라도 존재
→ logical possibility
모든 모델에서 참
→ entailment / necessity relative to the ontology
후보 추가 시 ontology inconsistent
→ impossible relative to the ontology
```
현재 HermiT 계층은 두 번째 의미의 가능성 판정에 활용할 수 있다. 다만 OWL 2 DL consistency는 일반 양상논리의 모든 가능한 세계를 다루는 것이 아니라, **현재 OWL 공리 집합의 모델 존재 여부**를 판정한다.
새 시스템에서는 이를 명시적으로 구분한다.
```json
{
  "textual_modality": "POSSIBLE",
  "ontology_admissibility": "CONSISTENT",
  "ontology_entailment": "NOT_ENTAILED"
}
```
---
# 4. 새로운 전체 아키텍처
```text
┌────────────────────────────────────────────────────────┐
│ 1. Source Boundary                                     │
│ snapshot / SHA-256 / URI / version / span verification │
│ 현재 cg_normalizer 유지                                │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 2. Atomic Claim Compiler                               │
│ 문장을 작은 subject–predicate–object claim으로 분해    │
│ 정의·예시·관찰·가설·규칙 후보를 구분                   │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 3. Candidate Lattice                                   │
│ is-a / instance-of / component-of / member-of / uses   │
│ role-of / phase-of / no-relation 후보를 동시에 유지    │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 4. Proof-Obligation Gates                              │
│ evidence / relation / scope / definition / modal       │
│ type / counterexample / cross-document conflict        │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 5. Semantic IR                                         │
│ 검증된 claim과 미결 obligation을 분리 저장             │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 6. OWL Candidate Compiler                              │
│ primitive / defined / restriction / role axiom 생성    │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 7. OWL Round-Trip Gate                                 │
│ OWL → controlled language → 원 claim과 대조            │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 8. Model-Admissibility Gate                            │
│ HermiT consistency / satisfiability / subsumption      │
│ gUFO / SHACL / mereology                               │
└─────────────────────────┬──────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│ 9. Certified Graph                                     │
│ asserted / document-supported / entailed를 분리 출력   │
└────────────────────────────────────────────────────────┘
```
---
# 5. 기존 저장소와 대조되는 거시 변경 사항
## 5.1 feature 중심에서 claim 중심으로
### 현재
현재 핵심 taxonomy 경로에서는 자식이 부모의 essential feature 라벨을 verbatim으로 반복해야 `is-a` edge가 생성된다. 이름이나 자연어 문장만으로는 edge가 생기지 않는다.
```json
{
  "name": "Square",
  "features": [
    {"label": "four-sided polygon", "type": "essential"},
    {"label": "four right angles", "type": "essential"},
    {"label": "four equal sides", "type": "essential"}
  ]
}
```
### 확장
중심 단위를 feature가 아니라 **atomic semantic claim**으로 변경한다.
```json
{
  "claim_id": "claim:square:1",
  "subject": "Square",
  "predicate": "is_a",
  "object": "Rectangle",
  "source_spans": ["span:14"],
  "assertion_mode": "generic",
  "definition_force": {
    "necessary": "PASS",
    "sufficient": "UNKNOWN"
  }
}
```
feature는 제거하지 않는다. 다음과 같이 역할을 낮춘다.
```text
현재:
feature가 hierarchy의 의미적 권위
확장:
feature는 후보 검색·설명·legacy DAG를 위한 보조 표현
certified claim과 OWL entailment가 최종 권위
```
---
## 5.2 단일 concepts JSON에서 staged semantic state로
### 현재
normalizer가 검증된 concepts JSON을 조립하고 이후 pipeline이 한 번에 gate를 수행한다.
### 확장
다음 state store를 도입한다.
```json
{
  "claims": {},
  "relation_candidates": {},
  "obligations": {},
  "accepted_axioms": {},
  "rejected_axioms": {},
  "open_questions": {},
  "provenance": {},
  "rollback_frontiers": {}
}
```
실패 시 전체 문서를 재생성하지 않는다.
```text
relation obligation FAIL
→ 해당 relation candidate와 그에 의존하는 OWL axiom만 rollback
evidence obligation FAIL
→ 해당 claim 및 downstream entailment만 rollback
gUFO stereotype FAIL
→ stereotype과 그에 의존하는 rigidity inference만 rollback
```
이는 현재의 단계별 오류 보고를 **상태 수준의 선택적 rollback**으로 확장하는 것이다.
---
## 5.3 `run_pipeline`과 `classify_owl`의 권위를 명시적으로 분리
현재 저장소에는 실질적으로 두 종류의 hierarchy가 존재한다.
```text
essential-label inclusion hierarchy
OWL/HermiT entailed hierarchy
```
이를 출력 이름부터 분리한다.
```json
{
  "candidate_feature_hierarchy": {},
  "asserted_owl_hierarchy": {},
  "entailed_owl_hierarchy": {},
  "equivalence_groups": [],
  "rejected_relations": [],
  "open_obligations": []
}
```
권위 순서:
```text
candidate_feature_hierarchy
< source-supported assertions
< certified OWL axioms
< HermiT-entailments
```
legacy client를 위해 기존 `hierarchy`를 유지할 수 있으나, 새 API에서는 deprecated로 표시한다.
---
## 5.4 span 검증에서 evidence-group 검증으로
### 현재
span은 원문 내 문자 시작·끝 좌표다.
```json
{
  "start": 120,
  "end": 168
}
```
현재 normalizer는 다음을 확실히 검증한다.
* 좌표가 원문 범위 안인가
* span 길이가 제한을 넘지 않는가
* `text[start:end]`가 quote와 같은가
* source hash가 snapshot과 같은가
### 확장
span 하나가 claim 전체를 지지한다고 가정하지 않는다.
```json
{
  "evidence_group": {
    "spans": ["span:14", "span:17"],
    "coverage": {
      "subject": "span:14",
      "relation": "span:14",
      "necessary_condition": "span:17",
      "scope": "span:17"
    },
    "minimality": "VERIFIED",
    "full_support": "PASS"
  }
}
```
Minimal Evidence Group 연구는 claim 전체를 완전하게 지지하는 최소 증거 집합을 찾는 문제를 Set Cover와 유사한 문제로 정의한다. 이 접근은 단일 LLM prompting보다 WiCE와 SciFact에서 상당한 절대 개선을 보고했다.
ConceptGate에서는 논문의 score 모델을 그대로 가져오기보다 다음 계약만 차용한다.
```text
각 claim slot을 덮는 증거가 있는가?
불필요한 span을 제거해도 full support가 유지되는가?
한 span만으로 부족한 경우 복수 span이 함께 완전한 지지를 제공하는가?
```
---
## 5.5 양상 벡터가 아니라 양상 obligation record
UDS는 factuality, genericity, time, entity type, event structure 등의 의미 속성을 통합 그래프에 표현한다. 원래 UDS에서는 실수값 속성을 사용하지만, 그 핵심 아이디어는 복잡한 의미 판단을 여러 단순 질문으로 분해하는 것이다.
ConceptGate는 연속 벡터를 그대로 도입하지 않는다.
```json
{
  "modality_obligations": {
    "asserted_by_source": "PASS",
    "negated": "FAIL",
    "generic_kind_level": "PASS",
    "episodic_only": "FAIL",
    "hypothetical": "FAIL",
    "necessary_in_definition": "UNKNOWN",
    "sufficient_for_definition": "UNKNOWN",
    "temporally_scoped": "FAIL",
    "speaker_attributed": "PASS"
  }
}
```
이 결과는 embedding이 아니다.
* Word2Vec를 사용하지 않는다.
* LLM이 숫자 vector를 임의 생성하지 않는다.
* 각 축은 독립 질문과 evidence span을 갖는다.
* 최종값은 `PASS/FAIL/UNKNOWN`이다.
* 필요하면 별도의 classifier가 후보를 제안하지만 verifier 상태는 이산적이다.
UDS/Decomp는 코드 subtree보다 **질문 분해 방식과 평가 데이터**를 참조하는 것이 적절하다.
---
## 5.6 정의를 검색 결과 하나로 확정하지 않음
외부 검색은 다음 용도로만 사용한다.
```text
sense 후보 탐색
표준 용어 확인
기존 ontology identifier 확인
공신력 있는 정의문 후보 수집
문서 외부 반례 탐색
```
검색 결과는 자동으로 공리가 되지 않는다.
```text
retrieved definition
→ source snapshot 생성
→ claim 추출
→ source authority 기록
→ obligation 검증
→ 기존 문서와 충돌 검사
→ 채택 또는 보류
```
동일 개념에 여러 정의가 존재할 경우 다음처럼 분리한다.
```json
{
  "concept": "Bank",
  "senses": [
    {"id": "finance:bank", "definition_source": "..."},
    {"id": "geography:river_bank", "definition_source": "..."}
  ]
}
```
검색은 semantic authority가 아니라 **새 evidence source를 추가하는 ingestion subflow**다.
---
## 5.7 consistency를 possibility certificate로 승격
현재 `cg_owl`은 OWL 2 DL ontology를 만들고 HermiT로 classification한다. primitive와 defined를 구분하고, unsupported restriction이나 잘못된 참조를 직렬화 전에 거부한다.
확장에서는 후보 공리마다 sandbox world를 만든다.
```text
base ontology O
candidate axiom a
1. SAT(O)?
2. SAT(O ∪ {a})?
3. O ⊨ a?
4. O ∪ {a} ⊨ contradiction?
5. 어떤 기존 class가 새로 unsatisfiable이 되는가?
```
출력:
```json
{
  "candidate_axiom": "Square SubClassOf Rectangle",
  "base_consistent": true,
  "candidate_consistent": true,
  "already_entailed": false,
  "new_unsatisfiable_classes": [],
  "admissibility": "POSSIBLE_NOT_ENTAILED"
}
```
상태 어휘:
```text
ENTAILED
POSSIBLE_NOT_ENTAILED
INCONSISTENT
REDUNDANT
UNDERDETERMINED
```
이는 LLM의 “가능해 보인다”를 대체하는 결정론적 판정이다.
---
# 6. 신규 모듈 구조
```text
conceptgate/
├── concept_gate_v7.py              # 유지: legacy feature gate
├── cg_normalizer.py                # 유지·확장: source boundary
├── cg_input_linter.py              # 유지
├── cg_partwhole.py                 # 유지·확장
├── cg_gufo.py                      # 유지
├── cg_owl.py                       # 유지·확장
│
├── semantic/
│   ├── claim_ir.py                 # 신규: atomic claim schema
│   ├── claim_extractor.py          # 신규: schema-constrained 후보 추출
│   ├── candidate_lattice.py        # 신규: 경쟁 relation 후보 관리
│   ├── evidence_groups.py          # 신규: MEG-style evidence coverage
│   ├── obligations.py              # 신규: PASS/FAIL/UNKNOWN gate
│   ├── relation_gate.py            # 신규: is-a/part-of/uses 구분
│   ├── definition_gate.py          # 신규: necessary/sufficient 판정
│   ├── modality_gate.py            # 신규: textual modality 분해
│   ├── counterexample_gate.py      # 신규
│   └── provenance.py               # 신규
│
├── compiler/
│   ├── owl_candidate.py            # 신규: Semantic IR → OWL candidate
│   ├── owl_verbalizer.py           # 신규: OWL → controlled language
│   ├── roundtrip_gate.py           # 신규
│   ├── admissibility.py            # 신규: 후보별 sandbox reasoning
│   └── certifier.py                # 신규: 최종 승인·거부·abstain
│
└── server.py                       # 새 tool surface 추가
```
---
# 7. 새 MCP tool surface
기존 tool은 유지한다.
```text
make_snapshot
lookup_senses
assemble_concepts
lint_concepts
run_pipeline
classify_parents
map_to_owl
classify_owl
export_graph
```
신규 tool:
```text
extract_atomic_claims
propose_relation_candidates
verify_evidence_group
evaluate_relation_obligations
evaluate_definition_obligations
evaluate_modality_obligations
compile_owl_candidate
verbalize_owl_candidate
check_roundtrip
check_axiom_admissibility
certify_claim
```
권장 외부 호출 순서:
```text
make_snapshot
→ extract_atomic_claims
→ propose_relation_candidates
→ verify_evidence_group
→ evaluate_relation_obligations
→ evaluate_definition_obligations
→ evaluate_modality_obligations
→ compile_owl_candidate
→ verbalize_owl_candidate
→ check_roundtrip
→ check_axiom_admissibility
→ certify_claim
→ classify_owl
```
한 번에 전체를 실행하는 편의 도구도 제공할 수 있다.
```text
run_semantic_compiler
```
그러나 내부적으로는 각 stage를 분리하고, 각 단계 결과를 사용자가 검사할 수 있어야 한다.
---
# 8. 관계 gate 설계
## 8.1 `is-a`
다음을 모두 통과해야 한다.
```text
ISA-1  subject와 object가 class-level entity인가?
ISA-2  문장이 instance가 아니라 kind-level generalization인가?
ISA-3  A의 임의 instance가 B에 포함된다는 해석을 지지하는가?
ISA-4  role, phase, use, resemblance 표현이 아닌가?
ISA-5  반대 후보 part-of/uses/acts-as가 배제되는가?
ISA-6  evidence group이 relation과 scope를 모두 지지하는가?
ISA-7  OWL round-trip 문장이 원문 의미를 보존하는가?
ISA-8  후보 공리가 ontology와 일관적인가?
```
`ISA-8`만 HermiT가 판단한다. 나머지는 semantic compiler의 책임이다.
---
## 8.2 `part-of`
단일 relation으로 처리하지 않는다.
```text
component_of
member_of
subcollection_of
portion_of
subquantity_of
material_of
feature_of
```
검사:
```text
PART-1 subject와 whole의 entity type이 subtype에 맞는가?
PART-2 단순 uses/depends-on/located-in 관계가 아닌가?
PART-3 inverse hasPart와 일치하는가?
PART-4 antisymmetry를 위반하지 않는가?
PART-5 cycle을 만들지 않는가?
PART-6 is-a와 동시에 채택되지 않는가?
PART-7 subtype에서 transitivity를 허용할 수 있는가?
PART-8 evidence가 구조적 포함을 명시하는가?
```
현재 README도 `based on`, `uses`, `relies on`, `computed by` 같은 약한 표현으로 structural composition을 만들지 말라고 규정한다. 새 relation gate는 이 지침을 prompt 수준이 아니라 typed obligation으로 구현한다.
---
# 9. OWL round-trip gate
현재 시스템은 JSON을 OWL로 직렬화한 다음 논리적 결과를 얻지만, OWL 표현이 원문 의미와 같은지는 별도로 재검증하지 않는다.
확장:
```text
source claim
→ OWL candidate
→ controlled natural-language verbalization
→ source claim과 비교
```
예:
```text
원문:
Each encoder layer contains a feed-forward network.
잘못된 공리:
EncoderLayer SubClassOf FeedForwardNetwork
역언어화:
Every encoder layer is a feed-forward network.
결과:
ROUNDTRIP_RELATION_MISMATCH
```
올바른 공리:
```text
EncoderLayer SubClassOf hasPart some FeedForwardNetwork
```
역언어화:
```text
Every encoder layer has at least one feed-forward network as a part.
```
DeepOnto는 OWL API 기반 ontology processing에 reasoning, verbalisation, normalisation, taxonomy 기능을 추가한 패키지다. 이 중 전체 ontology stack이 아니라 **OWL expression parser와 verbalisation 아이디어**만 선별 도입하는 것이 적절하다.
---
# 10. 추천 조합
## 10.1 요약표
| 목적                    | Paper/Project            |                          도입 방식 |   권장도 |
| --------------------- | ------------------------ | -----------------------------: | ----: |
| 구조화된 claim 후보 추출      | SPIRES / OntoGPT         |    Subflow 또는 selective import |    높음 |
| 복수 evidence 완전성       | Minimal Evidence Groups  |                    논문 메커니즘 재구현 | 매우 높음 |
| 의미 질문 분해              | UDS / Decomp             |             Paper + dataset 참조 |    중간 |
| OWL 역언어화              | DeepOnto                 | selective import 또는 작은 subtree |    높음 |
| 최종 DL 판정              | 현재 `cg_owl` + HermiT     |                             유지 |    필수 |
| OntoClean/gUFO        | 현재 vendored gUFO/Scior   |                             유지 |    필수 |
| part-whole 표준 어휘      | 현재 OBO Relations subtree |                             유지 |    필수 |
| 관계 ML 분류기             | GLiREL/ReLiK 등           |            별도 optional subflow |   조건부 |
| modal theorem proving | 별도 modal prover          |           remote/local subflow |    장기 |
| ontology 평가           | OLLM 계열 metric           |          evaluation-only clone |    중간 |
---
# 11. Paper별 권장 사용법
## 11.1 SPIRES
**논문:** Structured Prompt Interrogation and Recursive Extraction of Semantics
SPIRES는 사용자 정의 schema를 기준으로 LLM이 중첩된 구조를 재귀적으로 추출하게 하고, 기존 ontology와 vocabulary에 grounding한다. 새로운 학습 데이터 없이 다양한 schema에 적용할 수 있다는 점이 ConceptGate의 agent boundary와 잘 맞는다.
### 가져올 핵심 아이디어
```text
자유 텍스트 JSON 생성
→ 금지
schema slot별 재귀 질의
→ 채택
각 slot마다 근거와 미결 상태 유지
→ 채택
ontology identifier grounding
→ 채택
```
### 도입 방식
**Subflow 권장**
OntoGPT 전체를 ConceptGate 내부에 넣지 않는다.
```text
ConceptGate MCP
→ optional OntoGPT/SPIRES extraction service
→ candidate claims 반환
→ ConceptGate가 검증
```
이유:
* OntoGPT는 LLM provider, grounding, LinkML 등 의존성이 크다.
* ConceptGate core의 stdlib-only 성격을 깨뜨린다.
* proposer와 verifier를 프로세스 수준에서도 분리하는 편이 낫다.
### Clone/import 판단
```text
개발·실험:
clone하여 adapter 개발
운영:
Python package optional dependency 또는 별도 service
git subtree:
비권장
```
---
## 11.2 Minimal Evidence Groups
**논문:** Minimal Evidence Group Identification for Claim Verification
이 논문은 claim을 완전히 지지하는 최소 evidence 집합을 찾는 문제를 형식화하고, full/partial entailment 판정과 Set Cover형 탐색을 결합한다.
### 가져올 핵심 아이디어
```text
한 span = 한 claim의 증명
```
을 폐기하고,
```text
여러 span이 claim slot 전체를 공동으로 덮는가?
```
를 검사한다.
### 도입 방식
**Paper mechanism 재구현**
논문 전체 구현을 subtree할 필요가 없다.
ConceptGate에 필요한 것은 다음뿐이다.
```python
coverage(claim_slot, span)
full_support(claim, span_group)
minimal(group)
enumerate_minimal_groups(candidate_spans)
```
### Clone/import 판단
```text
paper:
필수
repo:
참고용 clone 가능
subtree/import:
비권장
local reimplementation:
권장
```
이 메커니즘은 ConceptGate의 기존 span/hash 검증과 직접 결합된다.
---
## 11.3 UDS / Decomp
UDS는 factuality, genericity, time, entity type, event structure를 단일 semantic graph에 통합하고, 복잡한 의미 판단을 단순 질문으로 분해한다.
### 가져올 핵심 아이디어
* factuality와 necessity를 분리
* generic과 episodic을 분리
* event와 entity를 분리
* 여러 semantic axis를 독립 질문으로 분해
* annotation provenance 유지
### 가져오지 않을 것
* real-valued vector를 ConceptGate의 최종 상태로 사용
* UDS graph runtime 전체
* SPARQL layer
* 학습된 score를 logical confidence로 해석
### 도입 방식
**Paper + dataset/evaluation reference**
```text
production dependency:
없음
research benchmark:
UDS dataset 사용 가능
schema inspiration:
강하게 채택
```
### Clone/import 판단
```text
clone:
연구 분석 시 가능
import:
불필요
subtree:
비권장
```
---
## 11.4 DeepOnto
DeepOnto는 OWL ontology processing, reasoning, verbalisation, normalisation, taxonomy, alignment/completion 도구를 제공한다.
### 가져올 핵심 아이디어
* OWL class expression parsing
* expression tree
* controlled language verbalisation
* normal-form 처리
### 도입 방식 선택
#### 선택 A — optional import
```text
pip optional dependency
```
장점:
* upstream 업데이트 추적
* 라이선스와 provenance 관리가 쉬움
단점:
* JVM/OWLAPI 계층이 현재 owlready2와 중복
* 배포가 무거워짐
#### 선택 B — selective subtree
verbaliser와 필요한 parser만 필터링한 별도 vendor branch를 만든다.
```text
upstream DeepOnto
→ filter-repo
→ verbalisation 관련 코드만 유지
→ vendor/deeponto-verbaliser subtree
```
단, OWLAPI 객체 의존성이 강하면 사실상 분리가 어렵다.
#### 선택 C — local reimplementation
현재 `cg_owl`의 제한된 restriction vocabulary만 verbalise한다.
```text
some
only
exactly
min
max
value
subClassOf
```
현재 ConceptGate의 OWL surface가 작기 때문에, 초기에는 이 방식이 가장 단순하다.
### 최종 권장
```text
Phase 1:
local deterministic verbaliser
Phase 2:
DeepOnto를 oracle/test reference로 사용
Phase 3:
표현력이 확장될 때 optional import 검토
```
---
# 12. Subflow / Subtree / Clone / Import 결정
## 12.1 Subflow
프로세스 또는 서비스 경계를 유지해야 하는 기능:
| 대상                    | 이유                                    |
| --------------------- | ------------------------------------- |
| SPIRES/OntoGPT        | LLM proposer이며 의존성이 큼                 |
| 외부 검색·정의 조회           | 네트워크·source authority·rate limit 분리   |
| 대형 NLI/evidence model | GPU와 모델 dependency 분리                 |
| modal logic prover    | OWL/HermiT와 논리 체계가 다름                 |
| GLiREL/ReLiK 등 관계 모델  | optional ML scorer일 뿐 최종 verifier가 아님 |
원칙:
```text
실패해도 ConceptGate core는 실행 가능해야 함
```
---
## 12.2 Subtree
코드와 데이터가 작고, 결정론적이며, upstream provenance가 중요한 경우:
| 대상                               | 상태       |
| -------------------------------- | -------- |
| OBO Relations                    | 현재 방식 유지 |
| Scior/gUFO rule reference        | 현재 방식 유지 |
| 작게 필터링된 deterministic verbaliser | 조건부      |
| 작은 표준 relation vocabulary        | 가능       |
| 평가 fixture 또는 schema             | 가능       |
원칙:
```text
모델 코드, 대형 framework, provider SDK는 subtree하지 않음
```
---
## 12.3 Clone
개발·검증·비교를 위한 참조 저장소:
| 대상                               | 목적                      |
| -------------------------------- | ----------------------- |
| OntoGPT                          | SPIRES adapter 설계       |
| DeepOnto                         | verbalisation 결과 oracle |
| Decomp                           | schema 및 dataset 분석     |
| MEG 구현 repo                      | 알고리즘 재현                 |
| ontology-learning benchmark repo | 평가용                     |
Clone한 repo는 production import 경로에 넣지 않는다.
---
## 12.4 Import
명확한 API와 안정적인 라이선스, 제한된 의존성을 가진 경우에만:
| 대상                            | 권장                                            |
| ----------------------------- | --------------------------------------------- |
| owlready2                     | 현재 유지                                         |
| FastMCP                       | 현재 유지                                         |
| pySHACL                       | optional import, certification mode에서는 필수화 검토 |
| DeepOnto                      | 초기 비권장                                        |
| OntoGPT                       | core import 비권장                               |
| NLP embedding/model framework | core import 비권장                               |
---
# 13. 권장 최종 조합
## Core
```text
현재 ConceptGate v7
+ cg_normalizer
+ cg_input_linter
+ cg_partwhole
+ cg_gufo
+ cg_owl
+ HermiT
+ gUFO
+ OBO Relations
```
이 부분은 유지한다.
## 신규 deterministic layer
```text
Atomic Claim IR
+ Candidate Lattice
+ Evidence Group Gate
+ Relation Obligation Gate
+ Definition Obligation Gate
+ Modality Obligation Gate
+ OWL Candidate Compiler
+ Deterministic OWL Verbaliser
+ Round-Trip Gate
+ Candidate Admissibility Sandbox
+ Claim Certifier
```
이 부분은 ConceptGate 저장소 내부에 직접 구현한다.
## Optional proposer subflows
```text
SPIRES/OntoGPT
+ external dictionary/ontology lookup
+ optional relation classifier
+ optional evidence entailment model
```
이들은 후보만 제출한다.
## Research and evaluation
```text
MEG paper mechanism
UDS semantic decomposition schema
DeepOnto verbaliser oracle
relation confusion benchmark
metamorphic tests
```
---
# 14. 구현 우선순위
## Phase 1 — 출력 권위와 Semantic IR
신규:
```text
claim_ir.py
obligations.py
provenance.py
candidate_lattice.py
```
변경:
```text
hierarchy
→ candidate_feature_hierarchy
→ asserted_owl_hierarchy
→ entailed_owl_hierarchy
```
목표:
* 결과의 인식론적 등급 분리
* score 없는 `PASS/FAIL/UNKNOWN`
* claim 단위 provenance
---
## Phase 2 — Evidence Group Gate
현재 span/hash infrastructure 위에 추가한다.
```text
single span
→ candidate span set
→ slot coverage
→ minimal evidence group
→ full / partial / contradiction / insufficient
```
목표:
* `source_span_verified`와 `entailment_verified` 사이를 실제 메커니즘으로 연결
* evidence가 존재한다는 사실과 evidence가 claim을 지지한다는 사실 분리
---
## Phase 3 — Relation Gate
우선 관계:
```text
is_a
instance_of
component_of
member_of
uses
depends_on
located_in
role_of
phase_of
no_relation
```
목표:
* `is-a`와 `part-of` precision을 우선 향상
* weak lexical cue를 structural relation으로 승격하지 않음
* competing relation 후보를 명시적으로 반증
---
## Phase 4 — Definition and Modality Gate
```text
definition?
necessary?
sufficient?
generic?
episodic?
hypothetical?
role?
phase?
temporally scoped?
```
목표:
* `primitive`와 `defined`를 agent의 직접 선택에서 obligation 결과로 전환
* `actual`, `possible`, `entailed`, `consistent` 구분
---
## Phase 5 — Round-Trip and Admissibility
```text
Semantic claim
→ OWL candidate
→ controlled verbalisation
→ semantic comparison
→ sandbox HermiT
```
목표:
* relation swap 방지
* quantifier 손실 방지
* `is-a`와 restriction 혼동 방지
* 후보 공리 추가에 따른 부작용 보고
---
## Phase 6 — Optional proposer integration
SPIRES를 별도 subflow로 연결한다.
```text
document
→ SPIRES candidate extraction
→ ConceptGate proof obligations
```
목표:
* proposer 교체 가능
* 특정 LLM provider에 core가 종속되지 않음
* 동일 verifier로 여러 proposer 비교 가능
---
# 15. 주요 API 변경 예시
## 기존
```json
{
  "name": "EncoderLayer",
  "features": [
    {
      "label": "contains feed-forward network",
      "type": "structural_composition"
    }
  ]
}
```
## 확장
```json
{
  "claim_id": "claim:encoder-layer:has-ffn",
  "source": {
    "snapshot_sha256": "...",
    "evidence_group": [
      {"start": 1042, "end": 1108}
    ]
  },
  "subject": {
    "surface": "encoder layer",
    "sense_id": "local:encoder_layer"
  },
  "relation_candidates": [
    "component_of",
    "uses",
    "is_a",
    "no_relation"
  ],
  "selected_relation": "component_of",
  "obligations": {
    "evidence_full_support": "PASS",
    "subject_object_types": "PASS",
    "weak_use_only": "FAIL",
    "structural_inclusion": "PASS",
    "isa_interpretation": "FAIL",
    "cycle_free": "PASS",
    "roundtrip": "PASS"
  },
  "owl_candidate": {
    "axiom_type": "SubClassOf",
    "expression": {
      "property": "hasPart",
      "restriction": "some",
      "filler": "FeedForwardNetwork"
    }
  },
  "admissibility": "POSSIBLE_NOT_ENTAILED",
  "certification": "CERTIFIED"
}
```
여기서 `weak_use_only: FAIL`은 “검사를 실패했다”는 뜻으로 혼동될 수 있으므로 실제 구현에서는 질문형 이름보다 긍정형 obligation을 권장한다.
```json
{
  "structural_language_present": "PASS",
  "mere_use_language_only": "FAIL"
}
```
---
# 16. 성공 기준
`is-a 9/10`, `part-of 9/10`을 리뷰어 인상 점수가 아니라 테스트 계약으로 바꾼다.
## is-a
```text
is-a precision ≥ 0.95
instance-of → is-a 오류 ≤ 0.02
role → kind 오류 ≤ 0.03
uses/acts-as → is-a 오류 ≤ 0.02
primitive → defined 과승격 ≤ 0.02
```
## part-of
```text
part-of precision ≥ 0.95
uses → part-of 오류 ≤ 0.03
member/component subtype macro-F1 ≥ 0.90
is-a/part-of 동시 승인 = 0
cycle 누락 = 0
inverse 오류 ≤ 0.01
```
## evidence
```text
partial evidence를 full support로 승인 ≤ 0.03
contradiction 누락 ≤ 0.03
span/hash 위조 통과 = 0
근거 없는 certified axiom = 0
```
## compilation
```text
round-trip relation mismatch 통과 = 0
quantifier 손실 통과 = 0
candidate 추가 후 새 unsatisfiable class 미보고 = 0
```
---
# 17. 최종 거시 변화
현재 ConceptGate:
```text
evidence-carrying concept normalizer
+ feature taxonomy gate
+ composition gate
+ OWL reasoner
```
확장 후 ConceptGate:
```text
source-grounded semantic compiler
+ typed proof-obligation engine
+ relation and definition certifier
+ OWL round-trip compiler
+ candidate model-admissibility checker
+ provenance-aware ontology reasoner
```
가장 중요한 변화는 LLM의 성능을 높이는 것이 아니다.
```text
기존:
LLM이 좋은 concepts JSON을 만들기를 기대
확장:
LLM이 틀린 후보를 만들어도
어느 obligation이 실패했는지 확인하고
해당 하위 상태만 rollback
```
즉 핵심 연구 명제는 다음이다.
> **문서에서 OWL로 가는 변환을 한 번의 생성 문제로 취급하지 않고, 독립적으로 검사 가능한 작은 의미적 의무들의 상태 전이 문제로 바꾼다.**
---
# 18. 최종 도입 결정
## 직접 구현
```text
Semantic Claim IR
Proof Obligation Algebra
Evidence Group Gate
Relation Gate
Definition Gate
Modality Gate
OWL Candidate Sandbox
Deterministic Verbaliser
Round-Trip Gate
Certification State Machine
```
## Paper mechanism 채택
```text
SPIRES
Minimal Evidence Groups
UDS decompositional-question methodology
DeepOnto verbalisation/normalisation methodology
```
## Subflow
```text
OntoGPT/SPIRES
외부 검색 및 표준 정의 조회
대형 NLI·relation 모델
일반 modal theorem prover
```
## Subtree 유지
```text
OBO Relations
Scior/gUFO reference
작은 결정론적 표준 데이터와 rule metadata
```
## Clone only
```text
DeepOnto
Decomp
MEG reference implementation
ontology-learning benchmark repos
```
## Optional import
```text
pySHACL
필요한 경우 DeepOnto
외부 proposer client SDK
```
## 도입하지 않음
```text
LLM self-confidence를 최종 score로 사용
Word2Vec식 연속 modality vector를 verifier 상태로 사용
검색 결과를 자동 정의 공리로 채택
feature 문자열 포함 hierarchy를 최종 semantic authority로 유지
하나의 span을 claim 전체의 proof로 간주
```
## 최종 권장 조합
```text
현재 ConceptGate core
+ 로컬 proof-obligation semantic compiler
+ MEG-style evidence completeness
+ 로컬 deterministic OWL verbaliser
+ HermiT candidate-admissibility sandbox
+ SPIRES optional proposer subflow
+ UDS-inspired discrete semantic questions
+ DeepOnto test oracle
```
이 조합은 현재 저장소의 결정론적·도메인 독립적 구조를 유지하면서, 가장 취약한 구간인 다음 변환을 검증 가능한 상태 전이로 바꾼다.
```text
문서 의미
→ 관계 후보
→ 정의·양상 의무
→ 증거 완전성
→ OWL 후보
→ 의미 보존
→ 모델 가능성
→ 인증된 공리
```
