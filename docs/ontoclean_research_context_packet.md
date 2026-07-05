# OntoClean Meta-Property Research — Agent Context Packet

Date: 2026-07-05
Source: Deep research x2 (200 agents, 36 sources, 144 claims, 50 verified)
Target: ConceptGate v7 OntoCleanMetaGate 구현을 위한 사전 조사

---

## 1. 핵심 결론

OntoClean은 **2단계** 구조다:
1. **태깅** — 각 개념에 메타속성(R, I, U, D) 부여
2. **검증** — 태깅된 taxonomy에 결정론적 제약 규칙 적용

**2단계(검증)는 완전히 자동화 가능하다.** 규칙 기반이며 LLM이 필요 없다.
**1단계(태깅)가 병목이다.** 원전은 인간 전문가의 판단을 전제한다.

ConceptGate v7에 적용할 때의 핵심 질문:
> ConceptGate의 기존 FeatureType(ESSENTIAL/STRUCTURAL 등)에서 메타속성을 자동 추론할 수 있는가?

답: **부분적으로 가능하지만, 직접 매핑은 성립하지 않는다** (아래 "치명적 반증" 참조).

---

## 2. 검증된 사실 (Adversarial 3-vote, CONFIRMED)

### 2.1 OntoClean 제약 규칙 (자동화 가능한 부분)

| 규칙 | 내용 | 출처 | 투표 |
|------|------|------|------|
| **Rigidity 제약** | anti-rigid(~R)는 rigid(+R)를 subsume할 수 없다 | Guarino & Welty, CACM 2002 | 3-0 |
| **Dependence 제약** | dependent(+D) 클래스의 하위는 반드시 +D | Keet tutorial 2019 | 3-0 |
| **Identity 상속** | identity criterion을 carry/supply하는 속성은 계층을 따라 전파된다 | Guarino & Welty, ECAI 2000 | 2-0 |
| **Identity+Unity** | identity(동일성)와 unity(통일성)는 상보적이며 함께 individuality를 구성 | Guarino & Welty, ECAI 2000 | 3-0 |

### 2.2 기존 구현체

| 도구 | 방식 | 출처 | 투표 |
|------|------|------|------|
| **OntOWLClean** (Welty 2006) | OWL punning: TBox→ABox 변환 후 DL reasoner가 제약 위반 탐지 | Welty 2006, Keet tutorial | 3-0 |
| **OntOWL2Clean** | OWL 2 role chain 활용 (OntOWLClean 후속) | Keet tutorial | 3-0 |
| **OCIP** | Constraint Handling Rules (CHR/Prolog), forward+backward reasoning | CEUR-WS Vol-1442 | 3-0 |

### 2.3 Rigidity의 복잡성

| 사실 | 출처 | 투표 |
|------|------|------|
| 원전의 S5 modal logic rigidity 정의에 문제가 있어 커뮤니티가 여러 해결책 제안 | Semantic Scholar 2ed7aa91 | 3-0 |
| Rigidity는 단일 속성이 아니라 여러 종류로 분해된다 | 같은 논문 | 3-0 |
| actuality와 permanence라는 새 메타속성이 필요 (시간적/존재적 행동을 modal rigidity에서 분리) | 같은 논문 | 3-0 |

---

## 3. 치명적 반증 (REFUTED 0-3)

> **"essential_feature가 모든 인스턴스에 나타나면 rigid에 매핑된다"는 주장은 거짓이다.**

- Guarino의 "essential"은 S5 modal necessity — **모든 가능 세계에서** 성립해야 함
- ConceptGate의 `essential_feature`는 extensional(실제 관찰된 인스턴스)이지 modal이 아님
- "모든 인스턴스에 나타남" ≠ "모든 가능 세계에서 반드시 성립"
- 3명의 검증자가 전원 반박 (투표 0-3)

**ConceptGate 시사점**: FeatureType.ESSENTIAL을 OntoClean의 +R(rigid)로 직접 매핑하는 것은 이론적으로 정당화되지 않는다. 다만 실용적 근사(approximation)로 사용할 수는 있되, 이 한계를 명시해야 한다.

---

## 4. Scior/gUFO 확인 결과

### 4.1 gUFO 37개 추론 규칙 (가장 중요)

> gUFO/UFO 공리화에서 도출된 **37개 결정론적 추론 규칙**이 OWL 클래스의 온톨로지 카테고리(Kind, SubKind, Role, Phase, Category, Mixin 등)를 **taxonomy 구조(rdfs:subClassOf)와 초기 시드 분류만으로** 자동 추론할 수 있다.

확인 결과:
- 원전 논문과 GitHub 구현체가 확인됨.
- `https://purl.org/scior` → `https://github.com/unibz-core/Scior/`
- 현재 repo에는 `vendor/scior` subtree로 reference snapshot을 포함.
- Scior 런타임은 `rdflib/owlrl`에 의존하므로 ConceptGate core에서는 직접 import하지 않음.
- ConceptGate는 `cg_gufo.py` adapter로 Scior의 TSV rule metadata만 stdlib로 읽음.

출처: "Inferring Ontological Categories of OWL Classes Using Foundational Rules" (NEMO/UFES, 2023), Scior GitHub.

예시 규칙:
- 이론 규칙 **R22** / Scior 구현 규칙 **RA02**:
  `RigidType(x) AND subClassOf(x,y) → NOT AntiRigidType(y)`
- **Sortality 상속**: 상위가 Sortal이면 하위도 Sortal; 두 Kind가 상위를 공유하면 그 상위는 NonSortal
- **Single-Kind 제약**: 모든 Sortal은 정확히 하나의 Kind를 ultimate superclass로 가져야 한다

**ConceptGate 시사점**: 직접 구현보다 Scior code/rule module을 먼저 분석하고, 필요한 rule subset을 adapter로 재사용한다. 단, 초기 seed 없이 완전 자동 분류가 되는 것은 아니다. Scior도 initial classification을 전제한다.

### 4.2 LLM을 이용한 메타속성 태깅

> GPT-4가 OntoClean 메타속성 4종을 ~96% 정확도로 태깅할 수 있다 (2024 논문)
> 출처: arxiv.org/pdf/2403.15864

**ConceptGate 시사점**: ConceptGate의 현재 아키텍처(LLM이 MCP client에서 동작)와 일치하는 접근. 다만 "LLM 의존 최소화"라는 설계 원칙과 충돌.

### 4.3 LLM의 part-whole 한계

> LLM은 part-whole 관계에 대해 "quasi-semantic" 역량만 보유하며, antisymmetry 같은 깊은 추론 속성을 놓친다. 즉 LLM 기반 meronymy 분류는 온톨로지 추론에 근본적으로 불완전하다.

출처: ACL Anthology J06-1005

**ConceptGate 시사점**: 이것이 현재 ConceptGate의 "약한 고리"를 정당화한다 — LLM이 is-a/has-a를 잘못 분류하는 이유가 원론적으로 설명됨.

---

## 5. 기존 도구/프레임워크 비교

| 프레임워크 | is-a 검증 | has-a 검증 | 메타속성 태깅 | stdlib 가능 |
|-----------|----------|----------|------------|-----------|
| OntoClean (원전) | 제약 규칙 (결정론적) | 간접 (unity) | 인간 전문가 | 규칙만 가능 |
| OntOWLClean | OWL DL reasoner | - | 수동 | owlready2 필요 |
| OCIP | CHR/Prolog | - | 수동 | Prolog 필요 |
| gUFO 37 rules | 구조적 추론 | - | 구조에서 추론 | Python 구현 가능 |
| Winston 3차원 | - | 6종 분류 | 3차원 매핑 | Python 구현 가능 |
| ConceptGate v7 현재 | FCA subset, MixRig | CompositionGate | LLM (FeatureType) | stdlib only |

---

## 6. ConceptGate v7 구현 방향 제안

### 6.1 현실적 접근: 3단계 게이트

```
LLM 출력 (FeatureType + relation_hint)
    │
    ▼
[Stage 1] FeatureType 기반 근사 태깅
    - ESSENTIAL → +R 근사 (단, modal이 아닌 extensional 근사임을 명시)
    - STRUCTURAL → has-a 후보
    - CONTEXTUAL/FUNCTIONAL/SOCIAL → ~R (anti-rigid 후보)
    │
    ▼
[Stage 2] 구조적 추론 규칙 (Scior rule metadata 중 적용 가능한 것)
    - R22/RA02: rigid 하위가 있으면 상위는 anti-rigid일 수 없다
    - Sortality 전파: DAG 위치에서 sortal/non-sortal 추론
    - Single-Kind 제약: 같은 Kind 아래의 분류만 is-a로 허용
    │
    ▼
[Stage 3] OntoClean 제약 검증 (결정론적)
    - anti-rigid가 rigid을 subsume → REJECT
    - dependent가 independent를 subsume → REJECT
    - identity criterion 상속 위반 → WARNING
```

### 6.2 Ponytail 원칙 적용

- 외부 라이브러리(OWL reasoner, Prolog) 불필요 — Scior subtree를 먼저 분석하고,
  필요한 rule metadata/fixture를 adapter로 재사용
- 기존 UFOAntiPatternGate의 MixRig가 이미 rigidity 특수 케이스 → 일반화
- Stage 1의 근사 태깅은 현재 FeatureType 인프라를 재사용
- Stage 2/3은 DAGReasoner의 기존 구조를 확장

### 6.3 구현 우선순위

1. **Scior subtree 분석** — rule TSV, Python module, test fixture 중 재사용 가능 부분 분리
2. **R22/RA02(rigidity 상향 전파) adapter 연결** — 가장 즉시 적용 가능한 규칙
3. **Single-Kind 제약 구현** — is-a/has-a 혼동 방지에 직결
4. **OntoClean 제약 검증** — Stage 3 전체를 OntoCleanMetaGate로 구현

---

## 7. 참고 문헌 (검증 통과 소스)

### 원전
1. Guarino & Welty, "Evaluating Ontological Decisions with OntoClean", CACM 2002
   https://cacm.acm.org/research/evaluating-ontological-decisions-with-ontoclean/
2. Guarino & Welty, "Identity, Unity, and Individuality", ECAI 2000
   https://www.researchgate.net/publication/2625760
3. Guarino & Welty, "Towards OntoClean 2.0: A Framework for Rigidity"
   https://www.semanticscholar.org/paper/2ed7aa91e8ae4f35d5726a928b254c5bec220a72

### 구현/도구
4. Mahlaza & Keet, "OntoClean in OWL with a DL Reasoner — Tutorial", 2019
   https://people.cs.uct.ac.za/~mkeet/OEbook/ontocleantutorialOE19.pdf
5. OCIP: CHR-based OntoClean Implementation
   https://ceur-ws.org/Vol-1442/paper_16.pdf
6. Welty, "OntOWLClean: Cleaning OWL Ontologies with OWL", 2006
   https://www.semanticscholar.org/paper/087c35bf4234aebb453745471a462be3d506e48a

### 추가 확인 대상
7. "Inferring Ontological Categories of OWL Classes Using Foundational Rules", 2023
   https://nemo.inf.ufes.br/wp-content/papercite-data/pdf/inferring_ontological_categories_of_owl_classes_using_foundational_rules_2023.pdf
8. LLM-based OntoClean automation (~96% accuracy)
   https://arxiv.org/pdf/2403.15864

---

## 8. ConceptGate v7 현재 상태 (이 연구와의 관계)

| 현재 구현 | OntoClean 대응 | 갭 |
|----------|---------------|-----|
| UFOAntiPatternGate.MixRig | Rigidity 혼합 탐지 | 상향 전파 없음, anti-rigid→rigid subsumption 미검사 |
| UFOAntiPatternGate.PartOver | Unity 관련 (부분 중복) | OntoClean unity 제약과 직접 연결 안 됨 |
| UFOAntiPatternGate.WholeOver | Unity 관련 (전체 중복) | 같음 |
| CompositionGate | Mereology 공리 (비순환, 반대칭) | OntoClean과 독립적 (보완적) |
| FeatureType.ESSENTIAL | Rigidity 근사 | modal ≠ extensional (치명적 반증 참조) |
| FeatureType.STRUCTURAL | has-a 분리 | OntoClean은 has-a 직접 다루지 않음 (보완적) |
| cg_gufo.py + vendor/scior | Scior RA02/R22 등 rule metadata 재사용 | runtime은 import하지 않고 adapter로 격리 |

---

## 변경 이력
- 2026-07-05: Scior GitHub/source 확인 및 `vendor/scior` subtree 반영, RA02/R22 표기 정리
- 2026-07-05: 초기 작성 (deep-research x2 결과 종합)
