# Concept Gate Taxonomy v7

정규화-검증형 개념 격자 추론기입니다.
자연어 개념을 proof-carrying feature 구조로 정규화하고, Gate 검증을 통과한
`is_a` 관계만 DAG에 반영합니다. 용도, 장소, 기능, 사회적 취급 같은 맥락 관계는
기본 개념 계층에서 분리하여 보조 관계로 다룹니다.

**도메인 무관** — 코어는 특정 주제(예: 트랜스포머/어텐션)에 특화되지 않고
essential feature 라벨의 부분집합 포함이라는 형식 규칙으로만 동작합니다.
생물·기하·법·요리 등 임의 도메인에서 동일하게 작동함을 실험으로 검증했습니다
([experiments/](experiments/) 참조).

**is-a와 has-a의 분리**가 핵심 설계입니다:
- `essential_feature` (is-a) → DAG 간선 → 분류 계층 (DL concept axiom, C ⊑ D)
- `structural_composition` (has-a) → composition 그래프 → 부분-전체 관계 (DL role axiom, ∃R.C)

두 그래프는 독립적으로 추론되며, CompositionGate가 has-a 그래프에 mereology
공리(반대칭·비순환·is-a/has-a 배타)를, UFOAntiPatternGate가 UFO/OntoUML
안티패턴(MixRig·PartOver·WholeOver)을 적용해 혼동을 자동 감지합니다.

v7은 v6.3의 Gate/DAG 안정화 위에 expansion loop, sibling gate,
parent candidate classification, graph export, 그리고 Phase A/B/C
(UFO 판별 프롬프트 / STRUCTURAL 타입 / mereology 검증)를 추가한 버전입니다.
코어는 외부 라이브러리나 LLM API 없이 Python 3.10+ 표준 라이브러리만으로 실행됩니다.

## 파일 구성

```
concept-gate-taxonomy/
├── README.md              ← 이 파일
├── CLAUDE.md              ← 개발 지침 (Ponytail Rules, Subtree Registry)
├── qa_v7.py               ← v7 QA 스크립트 (101개 검증) ★ 최신
├── concept_gate_v7.py     ← v7 검증 대상 소스 (stdlib만 의존) ★ 최신
├── cg_partwhole.py        ← part-whole 어댑터 (vendor/obo-relations 조립) ★ 신규
├── cg_gufo.py             ← Scior/gUFO rule metadata adapter (stdlib, fallback 포함)
├── cg_input_linter.py     ← MCP 입력 JSON 사전 점검 linter (stdlib)
├── cg_graph_export.py     ← GraphExporter: JSON/Mermaid/GraphML (별도 모듈)
├── qa_v6_3.py             ← v6.3 QA (33개, 회귀 참고용)
├── concept_gate_v6_3.py   ← v6.3 소스 (회귀 참고용)
├── files/                 ← MCP 서버 배포 디렉토리 (files/README.md 참조)
│   ├── server.py          ← FastMCP 어댑터
│   ├── concept_gate_v7.py ← 배포 복사본 (루트와 동기화 유지)
│   ├── cg_partwhole.py    ← 배포 복사본
│   └── cg_input_linter.py ← 배포 복사본
├── vendor/
│   ├── obo-relations/     ← git subtree: OBO Relation Ontology (core.obo)
│   │                         part_of(BFO:0000050)/has_part(BFO:0000051) 표준 공리
│   └── scior/             ← git subtree: Scior gUFO rule reference
│                             RA02/R22, RU01 등 rule metadata 재사용
├── docs/                  ← Phase A/C 구현·설계 패킷
└── reference/
    ├── INTEGRATION_NOTES.md   ← TaxoAdapt 통합 계획 (계약 명세)
    ├── taxonomy.py            ← TaxoAdapt 원본 (참고용, 실행 안 함)
    ├── expansion.py           ← TaxoAdapt 원본 (참고용)
    ├── classification.py      ← TaxoAdapt 원본 (참고용)
    └── prompts.py             ← TaxoAdapt 원본 (참고용)
```

## 실행 방법

```bash
# 저장소 루트에서 실행
cd concept-gate-taxonomy

# v7 QA 계약 검증 (101개)
python3 qa_v7.py

# 소스 자체 인라인 테스트 (60개)
python3 concept_gate_v7.py

# MCP 서버 테스트 (47개, fastmcp 필요)
python3 files/test_server.py

# GraphExporter 인라인 테스트 (12개)
python3 cg_graph_export.py

# v6.3 회귀 참고 (33개)
python3 qa_v6_3.py
```

종료 코드: 전체 통과 시 `0`, 하나라도 실패 시 `1`.

## MCP 로컬 설치

Codex CLI에서 ConceptGate MCP 서버를 로컬 stdio 서버로 쓰려면
[`files/LOCAL_INSTALL_GUIDE.md`](files/LOCAL_INSTALL_GUIDE.md)를 참고하세요.
전체 repo 대신 `files/`만 sparse checkout해서 설치하는 방법도 포함되어 있습니다.

MCP client는 `conceptgate://client-guide` resource를 읽어 source-grounded
feature 정규화 규칙을 확인할 수 있습니다. 이 guide는 개념명만 있는 입력,
`features` 누락/빈 배열, `status: FAIL` 처리 방식을 명시합니다.

권장 호출 순서:

```text
source evidence → atomic features → lint_concepts → run_pipeline
```

핵심 계약:

- **is-a edge는 essential feature 라벨의 '문자열 그대로' 부분집합 포함으로만
  생성된다.** "C is-a P"를 표현하려면 C가 P의 essential 라벨을 전부 verbatim으로
  반복(type도 essential 유지)하고 종차 라벨을 추가해야 한다. "X는 Y이다" 같은
  문장 feature나 개념명 자체는 edge를 만들지 않는다.
- 개념명만으로 is-a/has-a 결론을 내리지 않는다.
- `run_pipeline` 전에 `lint_concepts`를 호출해 missing features, placeholder,
  약한 structural evidence, relation_hint/type 충돌을 사전 점검한다.
  교차 개념 검사(`NO_SHARED_ESSENTIAL_LABELS`, `ISA_CLAIM_FEATURE`)가
  "edge가 생길 수 없는 입력"을 run_pipeline 전에 경고한다.
- feature가 없거나 비어 있어 `Parse Gate`가 실패하면, 출처 기반 feature discovery를
  수행하고 atomic feature로 정규화한 뒤 `run_pipeline`을 재호출한다.
- `status: FAIL`이면 반환된 `dag`, `composition`, `isolated`는 진단 부산물이며
  확정 결과로 보고하지 않는다.
- `structural_composition`은 evidence가 part/module/layer/component 같은 구조적
  포함을 명시할 때만 사용한다.
- `based on`, `uses`, `relies on`, `computed by`, `follows architecture` 같은 약한
  표현만으로는 has-a를 만들지 않는다.
- `classify_parents`는 보조 도구이며 실패한 `run_pipeline` 결과를 덮어쓰는
  최종 판정 도구가 아니다.

### Render/hosted MCP timeout 대응

Render 같은 hosted MCP에서는 cold start, 큰 payload, pairwise 비교량 때문에
첫 호출이 timeout될 수 있다. 서버는 원인 분리를 위해 `run_pipeline`과
`lint_concepts` 응답에 `server_meta`를 붙인다.

```json
{
  "server_meta": {
    "timing_ms": 12.345,
    "input_stats": {
      "concept_count": 10,
      "feature_count": 42,
      "pairwise_comparisons": 45
    }
  }
}
```

운영 권장:

- 첫 요청 timeout이면 `/health`로 wake-up 후 같은 입력을 재시도한다.
- `lint_concepts`에서 `LARGE_PAIRWISE_INPUT`이 나오면 taxonomy를 topic/root별로
  나눠 검증하고, 검증된 subgraph를 병합한다.
- client는 retry/backoff를 둔다. 예: 2-3회, 2s → 5s → 10s.
- `server_meta.timing_ms`가 작지만 client timeout이 나면 cold start/네트워크 문제,
  `timing_ms`가 크면 입력 크기/추론 비용 문제로 본다.

## v7이 무엇인가

v6.3(개념 정규화 + Gate 검증 + DAG 생성)에 **확장(expansion) 기능**을 추가한 버전.
같은 essential 속성을 가진 개념들이 구분되지 않을 때, 종차(differentia)를 추가하여
계층을 정교화하는 루프를 구현했습니다.

### 파이프라인 흐름 (v7)

```
ParseGate
→ SemanticTypeInference
→ ConceptGate (type/evidence/contradiction/semantic)
→ PreDAGSignatureGate     ← essential 중복 탐지 (DAG 전)
→ DAGReasoner (EdgeBuffer로 staged commit)
   ├── is-a DAG (ESSENTIAL 피처)
   └── composition_view() ← has-a 그래프 (STRUCTURAL 피처, 독립)
→ PostDAGSiblingGate      ← 실제 sibling 종차 부족 탐지 (DAG 후)
→ CompositionGate         ← mereology 공리 검증 (반대칭·비순환·is-a/has-a 배타) ★ Phase C
→ UFOAntiPatternGate      ← MixRig/PartOver/WholeOver 감지 (WARNING) ★ Phase C
→ ResultClassifier
→ ExpansionPlanner        ← WARNING/NEEDS_CORRECTION → ExpansionAction (MixRig도 CORRECTION으로)
   (run_with_expansion 루프에서)
→ generator.generate()    ← 종차 생성 (LLM 또는 Static)
→ parse_expansion_response → 재진입
→ ParentCandidateClassifier  ← 최종 부모 후보 multi-label 판정
```

### Phase A/B/C: is-a vs has-a 판별 (v7 후반 추가)

- **Phase A** — `build_expansion_prompt()`에 UFO 기반 판별 가이드 삽입.
  LLM이 부분-전체 관계를 `structural_composition`으로 직접 출력하도록 지시
  (Winston 3차원 테스트 + UFO 타입 매핑 + 부분-전체 패턴 6종).
- **Phase B** — `FeatureType.STRUCTURAL` 추가. is-a DAG에는 불참(`ISA_ALLOWED_TYPES`
  는 ESSENTIAL만), `composition_view()`로 분리. `relation_hint` 필드(UFO 어휘)를
  스키마에 추가. 어휘 매핑은 `cg_partwhole.py`가 vendor/obo-relations subtree에서 조립.
- **Phase C** — `CompositionGate`(mereology 공리), `UFOAntiPatternGate`(안티패턴 3종),
  `relational_scaling()`(RCA existential scaling, ∃has_part.X 파생 — opt-in).

파이프라인 출력에 `composition`(has-a 그래프), `composition_issues`(공리 위반),
`anti_patterns`(안티패턴)가 추가됩니다. 기존 키는 변경 없음 (하위호환).

선택적으로 concept에 `ontoclean` 메타속성을 넣으면 `OntoCleanMetaGate`가
`is-a` edge commit 전에 rigidity, identity, unity, dependence, category 위반을
형식적으로 검사합니다. 메타가 없으면 기존 FCA feature-subsumption 동작을 유지합니다.

```json
{
  "name": "트랜스포머",
  "ontoclean": {
    "category": "model_architecture",
    "rigidity": "rigid",
    "identity": "supplies_identity",
    "unity": "unified_whole",
    "dependence": "independent"
  },
  "features": [
    {"feature": "시퀀스처리", "type": "essential_feature", "evidence": "시퀀스 입력을 처리한다"}
  ]
}
```

## 무엇을 검증하는가

PART A — v6.3 단독 동작 (13건): ParseGate 스키마, 상태 분류, WarningAction 분리.
PART B — TaxoAdapt get_siblings() 이식 (5건).
PART C — API 표면 계약 (14건): PipelineStatus/GateSeverity 5단계 + v7 클래스 존재 확인.
  - C8-C10: ExpansionPlanner, PostDAGSiblingGate, PreDAGSignatureGate 존재해야 함
  - C11-C13: ParentCandidateClassifier, ExpansionGeneratorBase, StaticExpansionGenerator 존재해야 함
  - C14: LLM 직접 호출 클래스는 없어야 함 (외부 주입 설계)
PART D — 회귀 불변식 (5건): finalize() 멱등성, EdgeBuffer rollback.
PART E — v7 Phase 1-3 (7건): PostDAG 탐지, ExpansionPlanner, run_with_expansion 수렴.
PART F — v7 Phase 4 (8건): ParentCandidateClassifier, generator 인터페이스, CORRECTION 자동 처리.
PART G — v7 Phase 5 (7건): HeuristicExpansionGenerator, ExpansionPlanner dedup, ExpansionHistoryAnalyzer.
PART H — GraphExporter (4건): JSON/Mermaid/GraphML 내보내기 + summary.
PART I — Phase A/B (7건): UFO 판별 가이드, relation_hint 스키마, STRUCTURAL 파싱, subtree 연결.
PART J — Phase C1/C2 (9건): CompositionGate 공리 4종 + UFO 안티패턴 3종 + ExpansionPlanner 연계.
PART K — Phase C3 (4건): relational_scaling 파생·멱등성·배선.
PART L — 구성 vs 구조 혼동 (5건): Transformer/Attention 실 도메인 시나리오.
  메커니즘을 부품으로 착각(MixRig), 개념 패밀리를 단일 부품으로(WholeOver),
  상속 부분 중복 선언(PartOver), is-a를 has-a로도 선언(배타 위반), 올바른 모델링 대조군.
PART M — OntoCleanMetaGate (5건): rigidity, identity, unity, dependence,
  category 메타속성 기반 is-a edge 형식 검증.

## LLM 연결 방법 (중요)

이 파일 자체는 LLM 없이 동작합니다. 확장 종차는 StaticExpansionGenerator로
주입합니다(사람 또는 다른 agent가 미리 작성). 실제 LLM을 연결하려면 두 가지 경로:

### 경로 1: claude.ai의 AI-Powered Apps (JSX artifact)
claude.ai에서 React artifact를 만들고 fetch("https://api.anthropic.com/v1/messages")로
Claude를 호출. build_expansion_prompt(action)으로 프롬프트를 만들고, 응답을
parse_expansion_response()에 넘깁니다.

### 경로 2: ExpansionGeneratorBase 상속
```python
class LLMExpansionGenerator(ExpansionGeneratorBase):
    def __init__(self, anthropic_client):
        self.client = anthropic_client

    def generate(self, action):
        prompt = build_expansion_prompt(action)   # v7 내장 함수
        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}])
        return response.content[0].text  # raw JSON string

# 사용
pipe.run_with_expansion(concepts, generator=LLMExpansionGenerator(client))
```

generate(action)이 raw JSON 문자열을 반환하기만 하면, 나머지(파싱/검증/재진입)는
파이프라인이 처리합니다.

## QA 에이전트를 위한 검토 지침

1. TaxoAdapt 통합 범위: taxonomy.py::get_siblings()의 부분 이식만 적용됨.
   reference/의 4개 파일은 pydantic/unidecode/LLM 호출부에 의존하므로
   import하면 실패합니다 — 정상입니다.

2. v7에 있어야 / 없어야 하는 것:
   - 있어야 함: ExpansionPlanner, PostDAGSiblingGate, PreDAGSignatureGate,
     ParentCandidateClassifier, ExpansionGeneratorBase, StaticExpansionGenerator,
     run_with_expansion, build_expansion_prompt, parse_expansion_response
   - 없어야 함: AnthropicExpansionGenerator, LLMExpansionGenerator
     (LLM은 외부에서 주입, 코어에 하드코딩 안 함)

3. 확장 루프 수렴 확인 (가장 중요):
   개·고양이·말이 모두 {동물} essential로 동일 → PASS_WITH_WARNING →
   StaticExpansionGenerator가 종차 추가 → 각자 다른 essential → PASS.
   이 수렴이 PART E E6에서 검증됩니다. 실패하면 expansion 루프 또는 ResultClassifier
   문제입니다.

4. ParentCandidateClassifier 다중 부모 (meet) 확인:
   정사각형 → [마름모, 직사각형] (PART F F2). indirect 조상(사각형)은 제외되어야 함.

5. 추가 hard-case 제안:
   - 3단계 이상 깊이의 확장 (현재 테스트는 1회 확장)
   - 확장 후에도 여전히 WARNING인 경우 (max_expansion_rounds 도달)
   - CORRECTION action 다단계 시나리오 (현재 1회 자동 처리, 다단계는 미검증)
   - 확장 generator가 잘못된 JSON 반환 시 PARSE_FAIL 경로

## 미구현 (다음 마일스톤)

- 실제 LLM generator 구현체 (경로 2의 LLMExpansionGenerator)
- LLMs4OL TaskB/C 데이터셋 벤치마크 (Gate 정확도 정량 평가)
- corpus 기반 expansion 트리거 (TaxoAdapt의 빈도 분석)

## 최근 변경

- **Phase A/B/C 설계 비정합 해결**: Phase A 프롬프트가 has-a를 `functional`로
  지시하던 것을 `structural_composition` 직접 출력으로 수정. Phase B의
  hint→type 후교정 로직 삭제 (프롬프트-교정 모순 제거, 삭제 > 추가).
  anti_context_gate에서 STRUCTURAL 제외 ("자동차 has 엔진"이
  "전기차 is-a 자동차"를 차단하지 않도록). 한국어 STRUCTURAL 마커는
  정확 일치로 전환 ("부품" ⊂ "일부품목" 오탐 방지).
- PART L 추가: Transformer/Attention 도메인의 구성 vs 구조 혼동 시나리오 5종.
- PART M 추가: OntoClean 메타속성 기반 `is-a` edge 검증.
- PART N 추가: Scior/gUFO subtree의 rule metadata를 `cg_gufo.py` adapter로 재사용.
- Relation Discrimination Gate 추가: `relation_hint`와 `type`이 모순이면 DAG 전에
  `NEEDS_CORRECTION`으로 격리.
- MCP `lint_concepts` 추가: `run_pipeline` 전 입력 JSON의 missing/empty feature,
  placeholder, weak structural evidence, relation_hint/type 충돌을 경고/오류로 보고.
- **is-a edge 계약을 tool description에 명시 + linter 교차 개념 검사 추가**:
  GPTs류 클라이언트는 resource(client-guide)를 읽지 않고 tool description만 보므로,
  `run_pipeline` docstring에 EDGE CONTRACT(라벨 verbatim 반복 + 종차 + type 유지)를
  직접 기술. linter에 `NO_SHARED_ESSENTIAL_LABELS`(모든 쌍이 essential 라벨 비공유
  → DAG 공집합 예고)와 `ISA_CLAIM_FEATURE`(다른 개념명 + 주장 표지 → 문장형 is-a
  선언 감지) 추가. A/B 실험(클라이언트 LLM, 각 5회): 구 description 0/5 → 신
  description 4/5가 올바른 계층(root→자식 3)을 형성했고, 실패 1건은 반복 라벨의
  type 불일치(Anti-Context Gate 정상 차단)로 description에 type 유지 문구를 반영.
- CORRECTION action 자동 처리: non-sparse same signature → NEEDS_CORRECTION →
  generator가 종차 추가 → 재진입 → PASS 수렴. DEPTH/WIDTH/CORRECTION 전부 처리됨.

## 버전 메타

- 검증 대상: concept_gate_v7.py + cg_partwhole.py + cg_gufo.py + cg_input_linter.py + cg_graph_export.py
- 의존성: Python 3.10+ 표준 라이브러리만 (MCP 서버만 fastmcp 필요)
- 외부 패키지: 코어 없음. vendor/obo-relations와 vendor/scior는 git subtree
  (읽기 전용 reference). Scior의 rdflib/owlrl 런타임은 import하지 않음.
- LLM API: 코어는 불필요. 확장은 generator로 주입 (Static 또는 LLM).
- 인라인 테스트: 60건 (concept_gate_v7.py) + 12건 (cg_graph_export.py)
- QA 검증: 101건 (`python3 qa_v7.py` 실행, PART A-N)
- MCP 서버 테스트: 47건 (`python3 files/test_server.py`)
