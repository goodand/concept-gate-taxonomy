# OWL ≡ 직렬화 설계 — concepts → OWL 2 DL (풀 reasoner가 계층을 *생성*하도록)

목표: 개념을 OWL 2 DL로 직렬화해, **풀 DL reasoner가 is-a 계층을 자동 분류**하게 한다. 이것이 리뷰 발견 2(집합 포함 ≠ 포섭)와 발견 5(개수 의존)의 근본 수정이다.

## 0. 핵심 결정 — primitive(⊑) vs defined(≡)

발견 2의 진짜 원인은 "feature 더 많음 = 자식"이다. 이를 고치는 건 "전부 ≡로 바꾸기"가 **아니다**. 오히려 반대다.

| 형태 | OWL | reasoner 동작 | 언제 |
|---|---|---|---|
| **primitive** | `C ⊑ E` (필요조건만) | X가 E를 만족해도 **X ⊑ C를 유도 안 함** | 자연종·열린 개념 (충분조건 불가) |
| **defined** | `C ≡ E` (필요충분) | X ⊑ E ⟺ **X ⊑ C 유도함** | 형식·규약 개념 (정의가 pin) |

**Bird/Airplane 반례가 여기서 갈린다:**
- 잘못된 현재: Bird={날개} ⊂ Airplane={날개,제트} → Bird⊑Airplane (틀림)
- `Bird ⊑ ∃hasPart.Wing` (**primitive**): Airplane도 `⊑ ∃hasPart.Wing`이지만 Bird가 primitive라 **reasoner는 Airplane⊑Bird를 유도하지 않음** ✓
- 반대로 `Square ≡ Rectangle ⊓ 등변` (**defined**): reasoner가 Square를 Rectangle과 Rhombus 아래로 **자동 배치**(meet) ✓ — 지금 시스템이 흉내만 내던 그 동작

### 결정 절차 (개념마다)
> "이 feature들을 **전부** 가지면서 C가 **아닌** 것이 있을 수 있나?"
- 있다 → **primitive** (⊑). 자연종(Bird, Dog)은 어떤 유한 feature 집합도 충분조건이 못 됨 → 관례상 primitive.
- 없다 (feature가 정확히 pin) → **defined** (≡). 형식개념(Square, Orphan, Parent).

gUFO stereotype이 기본값을 준다: `Kind`→보통 primitive / 종차로 정의된 subclass·형식개념→defined.

## 1. feature는 원자가 아니라 class expression이다

현재: `{"feature": "동물", "type": "essential_feature"}` — 불투명 문자열.
새로: feature = **제약(restriction)**. reasoner가 논리로 다루려면 구조가 있어야 한다.

```json
{
  "property": "hasEdge",       // object/data property
  "filler": "Edge",            // 채움 클래스 (또는 값)
  "restriction": "exactly",    // some | only | min | max | exactly | value | subClassOf
  "cardinality": 3,            // cardinality 계열일 때
  "role": "defining"           // defining(≡에 기여) | necessary(⊑에만 기여)
}
```

지원 형태 (OWL 2 DL):
| restriction | OWL | 예 |
|---|---|---|
| subClassOf(genus) | `⊑ Named` | `⊑ Animal` |
| some | `⊑ ∃P.F` | `⊑ ∃hasPart.Wing` |
| exactly | `⊑ =n P.F` | `⊑ =3 hasEdge.Edge` |
| min/max | `⊑ ≥n / ≤n P.F` | `⊑ ≥1 hasChild.Person` |
| only | `⊑ ∀P.F` | `⊑ ∀hasPart.Organic` (주의: 오용 쉬움) |
| value | `⊑ ∃P.{a}` | `⊑ ∃hasColor.{red}` |

## 2. concept 스키마 (직렬화 입력)

```json
{
  "name": "Square",
  "iri": "cg:Square",
  "stereotype": "kind|subkind|phase|role|category|defined_class",
  "definition_kind": "defined",         // primitive | defined  ← §0 결정
  "genus": "cg:Rectangle",              // 명명된 상위 (Aristotle genus, 선택)
  "differentia": [                       // C를 구분하는 조건 (defining)
    {"property": "hasSide", "restriction": "exactly", "cardinality": 4, "filler": "cg:Side", "role": "defining"},
    {"property": "cg:hasEqualSides", "restriction": "value", "filler": "true", "role": "defining"}
  ],
  "necessary_only": [                    // defined여도 ≡에 안 넣는 순수 필요조건 (⊑)
    {"property": "cg:isPlanar", "restriction": "value", "filler": "true", "role": "necessary"}
  ],
  "evidence_refs": [ ... ]              // 각 축이 어느 span에서 왔는지 (evidence-carrying 유지)
}
```

## 3. OWL 방출 규칙

- **defined**: `EquivalentClasses(C  ObjectIntersectionOf(genus, differentia...))`
  추가 필요조건은 별도 `SubClassOf(C  necessary_only...)`.
- **primitive**: `SubClassOf(C  ObjectIntersectionOf(genus, differentia..., necessary_only...))`.
- property·filler는 선언(`Declaration`)하고, disjointness/domain/range는 gUFO에서 상속하거나 명시.
- 출력 포맷: **Turtle** (Protégé·reasoner 공통). gUFO를 `owl:imports`.

### Aristotle genus+differentia가 핵심
`Square ≡ Rectangle ⊓ 등변`처럼 **명명된 genus + 구별 조건**으로 쓰면 reasoner가 다중 부모(meet)를 자동으로 찾는다. 이게 defined의 가치.

## 4. 이 설계가 고치는 것

| 리뷰 발견 | 어떻게 |
|---|---|
| **2** 집합 포함≠포섭 | primitive/defined 구분 → 자연종은 spurious subsumption 차단, 형식개념만 ≡로 분류 |
| **5** 개수 의존 | feature가 typed 제약(cardinality 포함) → "가축화된 포유류 갯과"를 1개 vs 3개로 쪼개도 논리적 함의는 동일. coverage 세기 자체가 사라짐 |
| **3** 전역규칙 | gUFO를 `owl:imports`하면 reasoner가 gUFO의 disjointness·stereotype 공리를 네이티브로 적용 (손코딩 행렬 제거) |

## 5. 한계 (정직하게 — 도구가 천장만 올림)

1. **"필연" 판단은 여전히 상류.** `definition_kind`(primitive/defined)와 `role`(defining/necessary)은 **모델링 입력**이다. reasoner는 이걸 전파·검증할 뿐 originate 못 함. → modality-tag가 제안, 근거와 함께.
2. **직렬화가 틀리면 garbage-in.** 잘못된 ≡는 잘못된 분류를 *보장*한다. 그래서 ≡ 선언마다 evidence_ref와 "충분조건 판단 근거"를 남긴다.
3. **only(∀) 오용 주의.** `∀hasPart.Organic`은 "부품이 있다면 전부 유기물"이라 부품 없어도 참 — 직관과 어긋남. defining에는 되도록 some/exactly를 쓰고 only는 명시적 근거 있을 때만.

## 6. 검증 계획 (설계 증명)

풀 DL reasoner(HermiT via owlready2)로 다음을 **행동으로 증명**한다:
1. **Bird primitive → Airplane⊑Bird 유도 안 됨** (발견 2 차단 증명)
2. **Square defined ≡ Rectangle⊓등변, Rhombus defined ≡ Parallelogram⊓등변 → reasoner가 Square를 Rectangle·Rhombus 양쪽 아래로 분류** (defined의 자동 계층 생성 증명)
3. **모순 개념**(예: Kind인데 disjoint 두 genus) → reasoner가 unsatisfiable로 탐지

통과하면 이 설계가 성립. `owl_serializer.py` + `test_owl_serializer.py`로 구현.
