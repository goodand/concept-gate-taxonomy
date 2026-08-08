# 외부 비판 정리 — 의미적 정당화 계층 (semantic fidelity)

- 수신 일시: 2026-07-16 16:07 UTC
- 출처: 외부 워크스페이스 리뷰 (ConceptGate 메커니즘 한계 + 부분–전체/상위–하위 분류 능력 평가)
- 성격: 시스템의 **연구적 한계**에 대한 구조적 비판 + 개선 방향 + 정량 평가

> 이 문서는 외부 피드백을 **정리(Part A)** 하고 **전문을 보존(Part B)** 한다.
> Part A는 중심 명제·테마 묶음·이 세션 작업과의 교차참조·우선순위 로드맵을
> 담고, Part B는 원문을 헤딩 단위로 그대로 남긴다. 반영 여부는 별도 결정.

---

# Part A — 정리

## A.0 중심 명제 (한 줄)

> 시스템의 가장 큰 과제는 **더 강한 reasoner가 아니라, 문서와 형식 공리 사이의
> 의미적 정당화 계층**이다. 두 검증을 구분해야 한다:
> - `입력 형식 공리 ⊨ 분류 결과` — **현재 강함** (HermiT/OWL이 소유)
> - `문서의 실제 의미 ⊨ 추출된 주장` — **현재 약함** (상류 LLM 제안에 의존)

reasoner는 잘못된 공리에서도 "논리적으로 정확한" 결과를 낸다. 정확한 추론 +
잘못된 공리 = 일관되게 잘못된 결과. 그래서 최종 상태는 "문서 의미 검증 완료"가
아니라 **"출처가 연결된 형식 모델에 대한 내부 논리 검증 완료"** 로 표현해야 한다.

## A.1 12개 비판을 5개 테마로 묶음

| 테마 | 해당 항목 | 요지 |
|---|---|---|
| **T1. 인용 검증 ≠ 의미 검증** | 2.1, 2.12 | span/hash/quote 일치는 "그 문장이 feature/관계를 *의미*하는가"를 검증 안 함. `evidence-linked claim`이지 `proof-carrying`이 아님 |
| **T2. 상류 제안의 의미적 정확성 미검증** | 2.2, 2.3, 2.4, 2.7 | primitive/defined 선택, gUFO stereotype, is-a/has-a 매핑을 LLM이 제안하고 reasoner는 그걸 전제로만 계산. `kind_rationale` 존재 ≠ 타당 |
| **T3. hierarchy 표현·혼동** | 2.5, 2.6, 2.9 | legacy DAG는 surface-form 부분순서(의미적 subsumption 아님) · 두 종류 hierarchy 혼동 위험 · 동치 붕괴가 부모 정보 왜곡 |
| **T4. fail-open 위험** | 2.8 | SHACL 위반을 warning으로만 처리하면 심각한 모델링 오류(genus 없는 defined, parthood-only 정의, 우발적 동치 등)가 정상 결과처럼 통과 |
| **T5. 경계·E2E 공백** | 2.10, 2.11 | PDF fetch/추출 도구 부재(가장 어려운 해석 단계가 MCP 밖) · correction loop가 형식 모델만 고치고 원문 과일반화·조건절 누락은 못 잡음 |

## A.2 이 세션 작업과의 교차참조 (이미 반영 vs 열림)

| 비판 | 상태 | 비고 |
|---|---|---|
| **2.9 동치 붕괴가 hierarchy 왜곡** | ✅ **이미 수리** | 이 세션에서 gUFO 부모 유실을 그룹 부모 합집합으로 복원 + `equivalence_groups` + `has_nontrivial_equivalences` 추가 (P9로 고정). 비판이 지적한 `equivalence groups`·`alias 복원`은 반영됨 |
| 2.9 잔여 (`deterministic representative`·`quotient hierarchy`) | ◐ 부분 | `representatives` 필드는 Round 2에서 "정책이라 이른 고정" 판단으로 보류 — 이 비판이 재검토 근거를 보탬 |
| **2.6 두 hierarchy 혼동** | ◐ 부분 | `equivalence_groups`로 축 분리는 했으나, `candidate_feature_hierarchy`(legacy DAG) vs `entailed_owl_hierarchy`(OWL) **명명 분리**는 아직 안 함 |
| 2.1 / 2.12 evidence-linked ≠ proof | ➖ 설계상 이미 인지 | `mechanism.md`·normalizer가 "evidence-carrying, proof-carrying 아님"·`verification_status`(L1~L3) 분리를 이미 명시. 이 비판은 숨은 결함이라기보다 **기존 설계 stance의 재확인** |
| 2.10 PDF URL 미지원 | ✅ 확인됨 | 외부 워크스페이스의 URL-입력 지적과 일치. 의도된 경계(서버는 fetch 안 함) |
| 2.2/2.3/2.4/2.7 상류 제안 정확성 | ❌ 열림 | 핵심 연구 과제. 아래 로드맵 R2 |
| 2.8 SHACL fail-open | ❌ 열림 | 정책 재검토 대상. 로드맵 R4 |

## A.3 제안된 개선 (Part 2 원문에서)

- **관계 확정 절차 강제**: `자연어 문장 → 관계 후보 → argument type → 철학적
  조건 → 반례 검사 → 확정/보류`. is-a/part-of/role-of/phase-of별 **반례 검사
  질문**을 입력 계약 + feedback으로 제공 (예 is-a: "모든 A가 B인가? 상황이
  바뀌어도 유지되는가?"). 약한 표현(based on/uses/relies on)에선 **abstain**.
- **양상논리는 별도 계층**: OWL 2는 SROIQ description logic이라 □/◇/K/O/반사실
  연산자가 없음. ConceptGate는 그 계층의 **ontology typing·consistency checker**
  로 쓰되, modal theorem prover로 오해하면 안 됨.

## A.4 정량 평가 (Part 2 §5 — 리뷰어 채점)

| 능력 | 점수 |
|---|---|
| 정규화된 is-a 판정 | 8/10 |
| 정규화된 part-of 검사 | 8/10 |
| raw 문서에서 두 관계 자동 분류 | 5/10 |
| 분석철학 관계 규율 보조 | 7/10 |
| 양상논리 단독 추론 | 3/10 |
| 일반 철학 추론기 | 3/10 |

역할 배분 권고: **LLM**=자연어 해석·철학적 가설 제안 / **ConceptGate**=개념
유형·is-a·part-of·Role·Phase·동치·모순·정의구조 검증 / **별도 논리 엔진**=양상·
시간·인식·의무·반사실 추론.

## A.5 우선순위 로드맵 (수신 정리자 종합 — 실행은 별도 승인)

| # | 항목 | 근거 | 비용/성격 |
|---|---|---|---|
| R1 | **hierarchy 명명 분리** — `candidate_feature_hierarchy`(run_pipeline) vs `entailed_owl_hierarchy`(classify_owl) | 2.6 | 저비용, 오해 방지. 문서·필드명만 |
| R2 | **관계 반례 검사 질문**을 client-guide/feedback에 추가 (is-a/part-of/role/phase별) | 2.7 + Part2 §3.1 | 중간. 상류 규율 강화, 입력 계약 확장 |
| R3 | **representatives / quotient hierarchy 완성** | 2.9 잔여 | 저~중간. 이미 절반 완료(equivalence_groups) |
| R4 | **SHACL fail-open 정책 옵션** — 심각 위반(genus 없는 defined, parthood-only 정의)은 error 승격 선택지 | 2.8 | 중간. `validate_gufo` 계약 확장 |
| R5 | (연구) **의미적 정당화 계층** — 문서 의미 ⊨ claim 검증(과일반화·조건절 누락·가능성→필연 탐지) | T1·T2·2.11 | 대형 연구 과제. 별도 설계 |

> 주의: R1·R3는 이 세션 흐름의 자연스러운 후속(저비용). R2·R4는 계약 변경.
> R5는 프로젝트의 장기 연구 방향으로, "더 강한 reasoner"가 아니라 "상류 변환의
> 의미 충실도 검증"이 핵심이라는 비판의 요지와 직결.

---

# Part B — 전문 보존

## B-1. ConceptGate 메커니즘의 핵심 한계

### 1. 두 시스템의 차이

**문서의 의미를 검증하는 시스템** — 문서에서 추출한 주장 자체가 원문에 의해
정당화되는지를 검증한다. 판단 대상:
- 원문이 실제로 `A는 B의 하위 개념이다`라고 말하는가
- 원문이 필요조건만 제시했는가, 필요충분조건을 제시했는가
- 특정 구현의 특성을 개념의 본질적 정의로 잘못 일반화하지 않았는가
- `uses`, `based on`, `contains`를 `is-a`나 `has-part`로 과도하게 해석하지 않았는가
- 부정, 조건, 가능성, 예외, 적용 범위를 보존했는가
- 인용한 문장이 추출된 claim을 실제로 함의하는가

검증 관계: `문서의 실제 의미 ⊨ 추출된 주장`

**형식 모델의 내부 논리적 결과를 검증하는 시스템** — 이미 만들어진 형식 모델을
참이라 가정하고, 그 모델 내부에서 어떤 결과가 논리적으로 따라오는지 검증한다.
판단 대상: ontology 일관성 / 불만족 클래스 / `A ⊑ B` 유도 / 동치 / 다중 부모 /
OntoClean·gUFO 제약 충돌. 검증 관계: `입력된 형식 공리 집합 ⊨ 분류 결과`.

두 번째 시스템은 입력 공리가 원문을 올바르게 표현하는지 판정하지 않는다. 잘못된
공리를 넣어도 reasoner는 그 잘못된 공리에서 올바른 논리적 결과를 계산한다.

### 2. 핵심 비판

**2.1 인용 검증이 의미 검증은 아니다** — hash/span/quote/출처 연결은 검증하나
"해당 문장이 feature 또는 관계를 실제로 의미하는가"는 검증 안 함. `The system is
based on attention mechanisms.`의 span이 정확해도 `System hasPart
AttentionMechanism`은 자동 정당화 안 됨. 현재는 `evidence-linked claim`에 가깝지
`proof-carrying claim`이 아니다.

**2.2 잘못된 형식화는 더 강하게 고정될 수 있다** — `Transformer ≡
AttentionMechanism`을 입력하면 reasoner는 의심 없이 동치·포섭·모순을 계산.
정확한 추론 + 잘못된 공리 = 일관되게 잘못된 결과. Reasoner는 잘못된 의미 모델을
교정하는 장치가 아니라 주어진 의미 모델을 전개하는 장치.

**2.3 primitive와 defined 판단이 상류에 남아 있다** — 어떤 개념을 defined로
선언할지는 LLM/모델러가 제안. 문서가 실제로 충분조건을 제공했는지는 판정 안 함.
`문서: A는 일반적으로 B의 특성을 가진다 / 잘못된 형식화: A ≡ B의 특성 / 결과: B의
특성을 가진 모든 것이 A로 분류됨`. `kind_rationale` 존재 ≠ 논리적 타당.

**2.4 OntoClean·gUFO stereotype도 입력 제안에 의존** — Kind/Role/Phase/SubKind
부여, rigid/anti-rigid, identity criterion 제공 여부 판단은 reasoner 외부. 잘못된
stereotype이 들어가면 gUFO는 그 입력을 전제로 계산. gUFO는 철학적 범주를
자연어에서 발견하지 않고 제안된 범주 사이의 정합성을 검사.

**2.5 legacy DAG는 의미적 subsumption이 아니다** — `parent feature labels ⊂
child feature labels`. 동의어를 다른 feature로 취급, 표현 변형 미인식, 문자열
공유가 is-a를 보장 안 함, feature 분해 수준에 결과 의존, 상위 feature를 자식에
문자 그대로 반복해야 함. semantic subsumption이 아니라 입력 표면형 부분순서.

**2.6 두 종류의 hierarchy가 혼동될 위험** — (1) exact feature-label inclusion
DAG, (2) OWL 2 DL reasoner 유도 hierarchy. 둘 다 `hierarchy`/`taxonomy`로
표현되면 동일 검증 수준으로 오해. `candidate_feature_hierarchy`와
`entailed_owl_hierarchy`로 명시 분리 필요.

**2.7 is-a와 has-a 분리는 여전히 상류 해석에 의존** — 그래프는 분리하나 어느
관계로 매핑할지는 상류 제안. 위험 표현: based on/uses/relies on/implemented
with/consists of/contains/includes/performs. `uses attention`→`hasPart
Attention`, `hasPart AttentionHead`→`MultiHeadAttention is-a Attention`은 오류.
그래프 분리만으론 관계 선택의 의미적 정확성 미보장.

**2.8 SHACL fail-open은 심각한 모델링 오류를 통과시킬 수 있다** — 위반을 warning
으로만 반환하고 reasoner를 계속하면, genus 없는 defined class / parthood만으로
구성된 필요충분 정의 / Role·Phase 오배치 / rigid·anti-rigid 위반 / 우발적 동치 /
동일 differentia 복제로 인한 클래스 붕괴가 정상 결과처럼 반환될 수 있음.

**2.9 동치 클래스 출력이 hierarchy를 왜곡할 수 있다** — HermiT가 동치 클래스를
대표 노드로 접으면 비대표 멤버 부모 정보가 비어 보임. `Encoder ≡ Decoder / Decoder
⊑ Block` → `Encoder: [] / Decoder: [Block]`. 단순 hierarchy만 읽으면 Encoder를
고립 클래스로 오판. equivalence groups / deterministic representative / quotient
hierarchy / alias 복원 규칙이 함께 필요. hierarchy와 equivalence_groups를
클라이언트가 직접 조합하는 계약은 오판 가능성.

**2.10 PDF URL을 직접 입력받는 end-to-end 시스템이 아니다** — PDF 다운로드/추출/
구조 분석/주장 발견/근거 선택/의미 해석을 자체 수행 안 함. 외부 client가 PDF를
가져와 텍스트와 구조화된 제안을 생성해야. 문서 해석에서 가장 어려운 단계가 MCP
외부에 남음.

**2.11 피드백이 문서 해석을 직접 교정하지 않는다** — 현재 피드백은 schema 오류/
feature type/relation hint 충돌/missing feature/inconsistency/unsatisfiable/
equivalence collapse/taxonomy refinement를 다룸. 그러나 "원문 과일반화 / 조건절
누락 / 가능성→필연 / 구현 특성을 본질 정의로 오해 / 실험 결과를 보편 속성으로 /
저자 주장과 독자 추론 혼합" 피드백은 제한적. correction loop가 형식 모델을 주로
수정하며 원문 의미 해석 자체를 반증·갱신하는 구조는 약함.

**2.12 검증 성공이 문서 충실도를 의미하지 않는다** — snapshot/span/schema/SHACL/
HermiT/일관성 검증이 모두 성공해도 형식 모델이 원문 의미를 잘못 표현할 수 있음.
"문서 의미 검증 완료"가 아니라 "출처가 연결된 형식 모델에 대한 내부 논리 검증
완료"로 표현해야 함.

### 3. 비판의 핵심 요약

핵심 한계는 reasoner의 논리 능력 부족이 아니라, reasoner 진입 전 변환
(`자연어 문서 → claim → essential property → relation type → primitive/defined →
OWL axiom`)이 문서 의미에 충실한지 검증하는 독립 계층이 부족하다는 것. 시스템은
`형식 모델이 주어졌을 때 결과가 논리적으로 따라오는가`는 강하게 검증하나 `그 형식
모델이 원문이 실제로 의미한 바인가`는 충분히 검증 안 함. 가장 큰 과제는 더 강한
reasoner가 아니라 **문서와 형식 공리 사이의 의미적 정당화 계층**.

## B-2. 실제로 도울 수 있는 방식 + 관계 분류 평가

### 3.1 관계 확정 절차

"자연어 표현과 관계의 완전한 1대1 대응"을 목표로 하지 말고 절차 강제:
`자연어 문장 → 관계 후보 → 관계의 argument type → 철학적 조건 → 반례 검사 → 확정/보류`

- **is-a**: 모든 A가 B인가? A는 B의 한 종류인가? A의 개체는 동시에 B의 개체인가?
  시간/상황이 바뀌어도 분류가 유지되는가?
- **part-of**: A와 B는 서로 다른 개체인가? A가 B의 구성에 참여하는가? A를 제거하면
  B의 동일성/기능에 영향이 있는가? component/member/portion/material 중 무엇인가?
- **role-of**: 동일 개체가 이 속성을 잃어도 계속 존재하는가? 다른 개체/상황에
  의존하는가?
- **phase-of**: 동일 개체가 시간에 따라 이 상태에 들어가고 나올 수 있는가? 역할이
  아니라 내재적 상태 변화인가?

이 질문을 입력 계약·feedback으로 제공하면 LLM 관계 선택 정확도를 상당히 높일 수 있음.

### 3.2 양상논리 한계

OntoClean rigidity는 양상적 직관(Person은 모든 가능세계에서 Person인가? Student는
Student가 아닐 수 있는가?)을 쓰나, 범용 가능세계 의미론 modal reasoner와 동일하지
않음. □P/◇P/K_a P/O(P)/P□→Q 연산자 없음 → 필연/가능/지식/의무/반사실 직접 추론
불가. OWL 2 직접 의미론은 SROIQ description logic 기반. object property를 임의의
alethic·epistemic·deontic accessibility relation으로 간주하면 안 됨. 양상논리
본격 지원엔 별도 계층(possible-world/situation 모델, modal operator, accessibility
relation, time/agent index, de re/de dicto scope, modal proof obligation) 필요.
ConceptGate는 그 계층의 ontology typing·consistency checker로는 유용하나 그 자체가
modal theorem prover는 아님.

### 4. 부분–전체와 상위–하위 관계를 잘 분류할까 — 조건부로 그렇다

정규화된 입력을 받은 뒤 두 관계가 섞였는지 검사하는 능력은 강하나, 원문에서 어느
관계인지 최초 결정하는 능력은 외부 LLM 품질에 의존.

**4.1 형식 모델 단계** — 구분 명확: SubClassOf / EquivalentClasses / hasPart /
partOf / `A ⊑ ∃hasPart.B`. `Wheel part-of Car`에서 `Wheel is-a Car`/`Car is-a
Wheel` 미유도. is-a와 composition을 별도 그래프로 처리하는 것이 유효.

**4.2 원문 해석 단계** — 명확하면 잘 작동. 강한 part-of(consists of/is a component
of/contains), 강한 is-a(square is a quadrilateral/whale is a mammal/bachelor is
an unmarried adult man). 애매: uses attention/based on graph theory/includes
reasoning/incorporates semantics. linter가 based on/uses/relies on/computed by
같은 약한 표현으로 structural composition 만들지 말라 지시 — 좋은 방어선이나 완전한
의미 판정기는 아님.

**4.3 legacy DAG 주의** — `parent features ⊂ child features`는 입력 계약 검사엔
유효하나 의미적 포섭의 완전한 판정은 아님(자식이 부모 label을 문자 그대로 반복해야
edge 생성). 권고: `run_pipeline`=후보 관계·입력 품질 검사, `map_owl+classify_owl`=
형식화된 ontology의 semantic subsumption 판정.

### 5. 최종 판정

**최소 목표(부분–전체와 상위–하위 분리)는 충분히 달성 가능** — 조건: 원문 근거
명시 / 관계를 후보로 제출(즉시 확정 금지) / is-a·component-of·member-of·portion-of·
material-of 분리 / 약한 표현에서 abstain / legacy label DAG를 semantic authority로
안 씀 / OWL reasoner 결과를 최종 형식 판정으로 / 관계마다 반례 질문.

**분석철학·양상논리**: 독립 추론기로는 부족하나 LLM 관계 규율 장치로는 유용. 역할
배분: LLM(자연어 해석·철학적 가설) / ConceptGate(개념 유형·is-a·part-of·Role·Phase·
동치·모순·정의구조 검증) / 별도 논리 엔진(양상·시간·인식·의무·반사실).

정량 평가: is-a 판정 8/10 · part-of 검사 8/10 · raw 문서 자동 분류 5/10 · 분석철학
관계 규율 보조 7/10 · 양상논리 단독 3/10 · 일반 철학 추론기 3/10.
