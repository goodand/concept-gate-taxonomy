# OntoCleanMetaGate 설계 전략

Date: 2026-07-05
Status: DRAFT — Scior subtree 반영 후 adapter 중심 설계
Target: concept_gate_v7.py Phase D

---

## 0. 왜 필요한가

ConceptGate v7의 현재 약한 고리:

```
LLM → {type: "essential_feature" | "structural_composition"} → 파이프라인
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
       통계적 판단. 틀리면 is-a/has-a 전체가 오염됨.
```

현재 방어선:
- **사전 방어**: `build_expansion_prompt()`의 UFO 가이드 — LLM에게 "어떻게 분류하라"고 안내
- **사후 탐지**: UFOAntiPatternGate(MixRig/PartOver/WholeOver) + CompositionGate — 이미 오염된 후 증상 탐지

**빈 자리**: LLM 출력을 받은 직후, DAG에 반영하기 전에 "이 분류가 온톨로지적으로 올바른가"를 형식적으로 검증하는 gate가 없다.

OntoCleanMetaGate는 이 빈 자리를 채운다.

---

## 1. 설계 원칙

### 1.1 핵심 제약 (연구에서 도출)

**"essential_feature → rigid" 직접 매핑은 이론적으로 성립하지 않는다.**

Guarino의 rigid는 S5 modal necessity (모든 가능 세계에서 성립). ConceptGate의 ESSENTIAL은 extensional (관찰된 인스턴스에서 성립). 이 차이를 무시하면 gate가 이론적 정당성을 잃는다.

**해결**: 매핑을 근사(approximation)로 사용하되, 구조적 추론으로 보강한다. 단독으로 "이것은 rigid다"라고 단정하지 않고, DAG 구조에서 역추론한 제약과 교차 검증한다.

### 1.2 Code-Reuse First 원칙 적용

| 원칙 | 적용 |
|------|------|
| Code reuse first | Scior subtree의 rule 정의/fixture를 먼저 분석하고 adapter로 재사용 |
| YAGNI | 37개 rule 전부가 아니라 R22/RA02, RA03, RU01 같은 최소 subset부터 |
| stdlib only | Scior 런타임(rdflib/owlrl)은 import하지 않고 TSV/rule metadata만 읽음 |
| 기존 안전망 유지 | MixRig는 대체 검증이 안정화될 때까지 제거하지 않음 |
| 최소 코드 | 각 제약 규칙은 DAG 순회 1회로 구현 가능 |

---

## 2. 아키텍처: 파이프라인 삽입 위치

### 현재 흐름

```
ParseGate → SemanticTypeInference → ConceptGate
→ PreDAGSignatureGate
→ DAGReasoner (EdgeBuffer)                    ← is-a DAG 확정
→ PostDAGSiblingGate
→ CompositionGate                             ← has-a 검증
→ UFOAntiPatternGate                          ← MixRig/PartOver/WholeOver
→ ResultClassifier → ExpansionPlanner
```

### 실제/제안 흐름 (Phase D)

```
ParseGate
→ RelationDiscriminationGate                    ← type/relation_hint 자기모순 차단
→ SemanticTypeInference → ConceptGate
→ PreDAGSignatureGate
→ DAGReasoner (EdgeBuffer)                    ← is-a DAG 확정
→ PostDAGSiblingGate
→ OntoCleanMetaGate                           ← explicit ontoclean seed 기반 edge 검증
→ cg_gufo.py                                  ← Scior RA02/R22 등 rule metadata adapter
→ CompositionGate
→ UFOAntiPatternGate (MixRig/PartOver/WholeOver 유지)
→ ResultClassifier → ExpansionPlanner
```

**삽입 근거**: `relation_hint`와 `type`의 자기모순은 DAG 전에 차단해야 하고,
OntoClean/gUFO 제약은 seed가 있는 edge를 commit 전에 검증해야 한다. DAG 기반
역추론은 Scior rule subset 분석 후 별도 D-2로 둔다.

### 대안: PreDAG 삽입

```
→ PreDAGSignatureGate
→ OntoCleanMetaGate (PreDAG)                  ← DAG 전에 FeatureType만으로 검사
→ DAGReasoner
```

장점: DAG 오염 전에 차단. 단점: DAG 구조 없이는 역추론 불가능, 근사 태깅만 가능.

**결론**: PostDAG가 맞다. PreDAG에서는 FeatureType 기반 근사만 가능하고, 핵심 가치인 "구조적 역추론"을 활용할 수 없다.

---

## 3. OntoCleanMetaGate 설계

### 3.1 2-Pass 구조

```
Pass 1: 태깅 (근사 + 구조적 추론)
  FeatureType → 초기 메타속성 근사
  + DAG 위치 기반 규칙으로 교정

Pass 2: 검증 (결정론적 제약)
  태깅된 메타속성으로 OntoClean 제약 규칙 적용
  위반 발견 시 issue 생성
```

### 3.2 Pass 1: 메타속성 태깅

#### 3.2.1 FeatureType 기반 초기 근사

| FeatureType | 초기 메타속성 | 근거 | 한계 |
|------------|------------|------|------|
| ESSENTIAL | +R (rigid 근사) | 개념의 본질적 속성 → 모든 인스턴스에 필수 | modal ≠ extensional |
| STRUCTURAL | has-a 마커 (rigidity 불적용) | 부분-전체 관계 | — |
| CONTEXTUAL | ~R (anti-rigid 근사) | 맥락에 따라 변화 가능 | 일부는 semi-rigid |
| FUNCTIONAL | ~R (anti-rigid 근사) | 기능은 변경 가능 | 일부 기능은 본질적 |
| LOCATIONAL | ~R (anti-rigid 근사) | 위치는 변경 가능 | — |
| SOCIAL | ~R (anti-rigid 근사) | 사회적 취급은 변경 가능 | — |

**개념 수준 메타속성**:
- 모든 feature가 ESSENTIAL → 개념은 +R 후보 (rigid type)
- ESSENTIAL + 비-ESSENTIAL 혼합 → 개념은 Semi-Rigid 후보
- 비-ESSENTIAL만 → 개념은 ~R 후보 (anti-rigid type)

#### 3.2.2 구조적 역추론 규칙 (DAG 위치 기반)

Scior/gUFO 규칙 중 ConceptGate에 적용 가능한 것 (원전 대조 완료, seed 필요):

**규칙 R22 / Scior RA02: Rigidity 상향 전파**
```python
# 하위가 +R이면 상위도 +R이어야 한다.
# 위반: anti-rigid 상위에 rigid 하위가 연결됨.
for child_name, parent_names in dag.items():
    if meta[child_name].rigidity == RIGID:
        for parent_name in parent_names:
            if meta[parent_name].rigidity == ANTI_RIGID:
                # 위반! anti-rigid가 rigid를 subsume
                issue(...)
```

**DAG 위치 힌트: Leaf vs Root 추론** (ConceptGate 독자 규칙)
```python
# DAG leaf (자식 없는 개념)는 가장 구체적 → Kind/SubKind 후보 (typically +R)
# DAG root (부모 없는 개념)는 가장 일반적 → Category/Mixin 후보
# 단, 이것은 힌트이지 결정이 아님.
```

**Single-Kind 제약** (Scior RU01 / 이론 R28)
```python
# 같은 DAG 경로 위의 모든 개념은 같은 Kind에 속해야 한다.
# 다른 Kind의 개념이 같은 경로에 있으면 → is-a가 아닌 다른 관계일 가능성.
```

**Seed 교정** (Pass 1.1 근사를 Pass 1.2에서 교정)
```python
# Pass 1.1의 근사를 Pass 1.2에서 교정:
# - CONTEXTUAL이지만 DAG에서 rigid 하위를 가진다 → semi-rigid로 승격
# - ESSENTIAL이지만 DAG에서 같은 경로의 형제가 anti-rigid → 검토 필요
```

### 3.3 Pass 2: 제약 검증

OntoClean 원전에서 검증된 결정론적 규칙:

| 규칙 | 조건 | 심각도 | 현재 커버리지 |
|------|------|--------|------------|
| **C1: Anti-rigid subsumption** | ~R가 +R를 subsume | ERROR | MixRig가 부분 커버 |
| **C2: Dependent subsumption** | +D 상위의 하위가 -D | WARNING | 미구현 |
| **C3: Identity 상속** | 상위의 identity criterion을 하위가 위반 | WARNING | 미구현 |
| **C4: Unity 일관성** | +U 상위의 하위가 -U | WARNING | 미구현 |

#### 3.3.1 C1 구현 아이디어 (핵심)

현재 MixRig는 "같은 feature명이 ESSENTIAL과 비-ESSENTIAL로 혼용"을 잡는다.
이것은 rigidity 위반의 **한 가지 증상**이지, 전체가 아니다.

OntoClean C1은 더 넓다: "DAG에서 anti-rigid 상위 아래에 rigid 하위가 있으면 안 된다."

```
현재 MixRig가 잡는 것:
  "어텐션" → ESSENTIAL(in 신경망) + STRUCTURAL(in 트랜스포머)
  = 같은 이름이 다른 type으로 사용됨

OntoClean C1이 추가로 잡는 것:
  트랜스포머(contextual features만) → anti-rigid 근사
    └── 인코더(essential features) → rigid 근사
  = DAG 구조적으로 anti-rigid가 rigid를 subsume
```

**합치기**: MixRig를 C1의 특수 케이스로 흡수하고, C1을 DAG 구조 기반으로 일반화.

#### 3.3.2 C2-C4 구현 아이디어

**C2 (Dependence)**: ConceptGate에는 dependence 정보가 없다. `relation_hint`의 일부 값(member_of → dependent)에서 근사할 수 있지만, 현 시점에서는 YAGNI.

**C3 (Identity)**: 같은 DAG 경로 위의 개념들이 같은 "종류"인지 — 현재 FeatureType 분포의 유사성으로 근사 가능. 예: 부모의 essential_attrs가 {동물, 척추동물}인데 자식의 essential_attrs가 {빨간색, 크다}이면 identity criterion이 다르다는 신호.

**C4 (Unity)**: STRUCTURAL feature 보유 여부로 근사. +U(부분들이 전체를 구성) 상위의 하위도 같은 unity를 가져야 한다. 현재 CompositionGate가 이미 관련 검사를 수행.

---

## 4. 구현 전략: 점진적 확장

### Phase D-1: RelationDiscriminationGate + explicit OntoClean seed 검증

**범위**:
- `relation_hint`와 `type`의 자기모순을 DAG 전에 차단
- explicit `ontoclean` metadata가 있는 is-a edge에 OntoCleanMetaGate 적용
- Scior RA02/R22 rule reference를 `cg_gufo.py` adapter로 연결
- MixRig는 제거하지 않고 기존 안전망으로 유지

```python
class OntoCleanMetaGate:
    """OntoClean 메타속성 기반 subsumption 검증.

    Phase D-1 이후: Scior rule metadata를 참고해 seed 기반 제약을 확장.
    FeatureType 기반 근사 태깅은 warning/debug hint로만 사용.
    """

    @staticmethod
    def _infer_rigidity(concept, dag, all_concepts) -> str:
        """개념의 rigidity를 FeatureType + DAG 위치에서 추론.
        반환: '+R' | '~R' | '?R' (불확실)
        """
        ...

    @staticmethod
    def detect(reasoner, concepts) -> Tuple[GateReport, List[Dict]]:
        """DAG에서 OntoClean rigidity 제약 위반 탐지."""
        ...
```

**기존 MixRig와의 관계**:

```
MixRig 현재:
  feature_types[feat_name]에 ESSENTIAL + 비-ESSENTIAL 공존 → WARNING

Phase D-1 후:
  1. relation_hint/type 모순은 RelationDiscriminationGate가 차단
  2. explicit ontoclean seed가 있는 edge는 OntoCleanMetaGate가 차단
  3. 같은 feature의 type 혼용은 기존 MixRig가 계속 탐지
  4. Scior 기반 구조 역추론은 D-2에서 adapter rule subset으로 추가
```

### Phase D-2: Identity 근사 (다음)

**범위**: C3 규칙. essential_attrs의 "종류 일관성" 검사.
**조건**: D-1 완료 후, 실제 사용에서 false positive 비율 확인 후 진행 여부 결정.

아이디어: essential_attrs의 의미적 클러스터가 DAG 경로를 따라 일관되는지.

```python
# 부모 essential_attrs = {동물, 척추동물, 포유류}
# 자식 essential_attrs = {동물, 척추동물, 포유류, 네발} ← 일관 (확장)
# 자식 essential_attrs = {동물, 빨간색}               ← 불일치 (identity 변경?)
```

단, "의미적 클러스터"를 어떻게 정의할 것인가가 문제. FeatureType은 이미 의미적 분류를 제공하지만 granularity가 부족. 이것은 LLM 없이는 해결이 어려울 수 있다 — D-2를 YAGNI로 보류할 근거.

### Phase D-3: Unity + Dependence (미래)

**조건**: D-1, D-2의 실전 검증 후. 현재는 설계만.

---

## 5. 데이터 모델 확장

### 5.1 MetaProperty 표현

```python
class Rigidity(Enum):
    RIGID      = "+R"    # 모든 인스턴스에 본질적
    SEMI_RIGID = "~R"    # 일부 인스턴스에 본질적
    ANTI_RIGID = "-R"    # 어떤 인스턴스에도 본질적이지 않음
    UNKNOWN    = "?R"    # 추론 불가

@dataclass
class ConceptMeta:
    name: str
    rigidity: Rigidity
    source: str  # "featuretype_approx" | "dag_inferred" | "corrected"
```

### 5.2 NormalizedConcept 확장?

NormalizedConcept에 meta 필드를 추가하지 **않는다**. MetaProperty는 gate 내부의 중간 산출물이며, 파이프라인 출력에 포함되지만 데이터 모델을 오염시키지 않는다.

이유: Ponytail 원칙. meta를 NormalizedConcept에 넣으면 모든 하류 코드가 영향 받음. gate가 issue list를 반환하는 현재 패턴을 유지.

### 5.3 출력 형식

```python
# 파이프라인 run() 결과 dict에 추가:
"ontoclean_issues": [
    {
        "rule": "C1_rigidity_subsumption",
        "parent": "학생",           # ~R (anti-rigid)
        "child": "사람",            # +R (rigid)
        "parent_rigidity": "-R",
        "child_rigidity": "+R",
        "source": "dag_inferred",   # 어떻게 추론했는지
        "detail": "anti-rigid '학생'이 rigid '사람'을 subsume — OntoClean C1 위반"
    }
],
"ontoclean_meta": {
    "사람": {"rigidity": "+R", "source": "featuretype_approx"},
    "학생": {"rigidity": "-R", "source": "dag_inferred"},
}
```

---

## 6. 기존 코드와의 상호작용

### 6.1 UFOAntiPatternGate 변경

| 현재 | Phase D 후 |
|------|-----------|
| MixRig (UFOAntiPatternGate 내) | OntoCleanMetaGate C1으로 흡수, 삭제 |
| PartOver (UFOAntiPatternGate 내) | 유지 (OntoClean과 별개, mereology 영역) |
| WholeOver (UFOAntiPatternGate 내) | 유지 |

MixRig 삭제 후 UFOAntiPatternGate에 PartOver + WholeOver만 남는다. 이름이 여전히 적절한가? — 적절하다. UFO 안티패턴은 MixRig만이 아니므로.

### 6.2 ExpansionPlanner 변경

현재:
```python
# MixRig → CORRECTION action
for iss in ap_iss:
    if iss.get("pattern") == "MixRig":
        actions.append(ExpansionAction(ExpansionType.CORRECTION, ...))
```

Phase D 후:
```python
# OntoClean C1 위반 → CORRECTION action (MixRig 대체)
for iss in ontoclean_iss:
    if iss.get("rule") == "C1_rigidity_subsumption":
        actions.append(ExpansionAction(ExpansionType.CORRECTION, ...))
```

### 6.3 validate_hierarchy 변경

```python
# 현재: 8-tuple 반환
return all_reps, all_repairs, all_warnings, reasoner, sig_iss, post_iss, comp_iss, ap_iss

# Phase D 후: 9-tuple (또는 dict로 전환)
return all_reps, all_repairs, all_warnings, reasoner, sig_iss, post_iss, oc_iss, comp_iss, ap_iss
```

**대안**: 반환값이 9-tuple이 되면 가독성이 나빠진다. dict 전환을 고려.

```python
return {
    "reports": all_reps,
    "repairs": all_repairs,
    "warnings": all_warnings,
    "reasoner": reasoner,
    "signature_issues": sig_iss,
    "post_dag_issues": post_iss,
    "ontoclean_issues": oc_iss,
    "composition_issues": comp_iss,
    "anti_patterns": ap_iss,
}
```

장점: 키 추가가 하위호환, 순서 무관. 
단점: 기존 코드 전부 수정 필요 (run(), run_with_expansion(), QA 테스트).
판단: Phase D와 함께 하면 "한 번에 두 가지 변경"이 되어 리스크 증가. **별도 리팩토링**으로 분리하거나, D-1에서는 tuple을 유지하고 D-2에서 dict로 전환.

### 6.4 CompositionGate._reachable 재사용

OntoCleanMetaGate에서 DAG 순회가 필요하다. CompositionGate._reachable은 이미 static method로 존재. 직접 호출하여 재사용.

```python
class OntoCleanMetaGate:
    @staticmethod
    def _infer_rigidity(concept, reasoner, all_concepts):
        # CompositionGate._reachable을 재사용하여 DAG 자손 탐색
        descendants = CompositionGate._reachable(dict(reasoner.dag), concept.name)
        ...
```

---

## 7. 테스트 전략

### 7.1 PART M: OntoClean 시나리오

```
PART M. OntoClean 메타속성 검증 (N건)
  M1. anti-rigid → rigid subsumption (C1 기본)
      학생(~R) subsumes 사람(+R) → ERROR
  M2. rigid → rigid (정상)
      동물(+R) subsumes 포유류(+R) → PASS
  M3. 기존 MixRig 시나리오가 C1으로 잡히는지
      어텐션 E/S 혼용 → C1 또는 MixRig 호환 WARNING
  M4. DAG 구조 역추론
      contextual-only 상위에 essential-only 하위 → ~R subsumes +R → ERROR
  M5. Semi-rigid 중립
      ESSENTIAL + CONTEXTUAL 혼합 개념 → semi-rigid → 상하 모두 가능
  M6. 올바른 taxonomy
      동물(+R) → 척추동물(+R) → 포유류(+R) → 개(+R) → PASS
```

### 7.2 회귀 보장

- 기존 89개 QA 전부 통과해야 함
- MixRig 관련 테스트(PART J, PART L)가 OntoCleanMetaGate로 이동 후에도 동일한 결과

---

## 8. 리스크 및 완화

| 리스크 | 영향 | 완화 |
|--------|------|------|
| FeatureType 근사의 false positive | 정상 taxonomy를 ERROR로 판정 | Pass 1의 UNKNOWN 카테고리: 확신 없으면 검사하지 않음 |
| 기존 MixRig 삭제 시 회귀 | PART J/L 실패 | MixRig 로직을 C1에 정확히 매핑, 테스트 단위로 검증 |
| validate_hierarchy 반환값 변경 | run(), QA 코드 전수 수정 | Phase D-1에서는 tuple 유지, ontoclean_iss를 ap_iss에 병합 |
| gUFO seed 없이 전파 불가 | FeatureType 근사 seed의 품질이 전파 정확도 결정 | D-1은 seed 없이 edge 제약만 검증(Stage 3). seed+전파(Stage 1-2)는 D-2 이후 |

---

## 9. 구현 순서 요약

```
D-0: gUFO 37 rules 논문 원전 확인 (연구) ★ 완료 — R22 확인, seed 전제 확인
     + Scior GitHub 확인 및 vendor/scior subtree 추가
     ↓
D-1: Code-reuse first 최소 반영
     - cg_gufo.py: Scior rule TSV adapter (stdlib, fallback 포함)
     - RelationDiscriminationGate: type/relation_hint 모순을 DAG 전에 차단
     - OntoCleanMetaGate: explicit seed edge 검증 + Scior RA02/R22 reference 연결
     - UFOAntiPatternGate의 MixRig 유지
     - PART I/M/N 테스트 + 101 QA 회귀
     ↓
D-1.1: server/files 동기화
     - files/concept_gate_v7.py, files/cg_gufo.py 동기화
     - MCP 출력은 기존 schema 유지
     ↓
D-2: Scior rule subset 확대 (조건부)
     - RA03, RU01, sortal/non-sortal seed rule 검토
     - FeatureType 기반 automatic rigidity는 hard gate로 쓰지 않음
     - seed 품질/false positive 확인 후 확장
     ↓
D-3: validate_hierarchy dict 전환 (리팩토링)
     - 8/9-tuple → dict
     - QA 테스트 일괄 수정
```

---

## 10. 미결정 사항

1. **D-1에서 MixRig를 즉시 삭제할 것인가, 병행 운영 후 삭제할 것인가?**
   - 즉시 삭제: Ponytail (삭제 > 추가), 코드 중복 제거
   - 병행: 안전하지만 MixRig와 C1이 같은 케이스를 중복 탐지할 위험

2. **C1 위반의 severity를 ERROR로 할 것인가, WARNING으로 할 것인가?**
   - ERROR: subsumption 차단 (DAG에서 해당 간선 제거)
   - WARNING: 정보 제공만 (현재 MixRig와 동일)
   - 제안: NEEDS_CORRECTION (ExpansionPlanner가 CORRECTION action 생성)

3. **ontoclean_meta를 파이프라인 출력에 포함할 것인가?**
   - 포함: 투명성 (왜 이 개념이 rigid/anti-rigid로 판정됐는지 추적 가능)
   - 미포함: 중간 산출물이 API 표면을 오염
   - 제안: 포함 (debug 정보로서 가치 있음, 하위호환 — 새 키 추가일 뿐)
