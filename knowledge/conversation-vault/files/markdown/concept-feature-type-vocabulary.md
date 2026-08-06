---
id: concept-feature-type-vocabulary
type: concept
title: Six-Type FeatureType Vocabulary
status: active
project: ontology-reasoner-mcp
summary: ConceptGate repair 계약에서 사용하는 여섯 FeatureType 값과 structural_composition의 명시적 노출.
keywords:
  - FeatureType
  - essential_feature
  - contextual_usage
  - locational
  - functional
  - social_treatment
  - structural_composition
---

# Six-Type FeatureType Vocabulary

실험 스키마가 사용하는 값은 다음 여섯 가지다.

- `essential_feature`
- `contextual_usage`
- `locational`
- `functional`
- `social_treatment`
- `structural_composition`

E2.2.1은 `structural_composition`을 포함한 전체 vocabulary 노출만으로 directed repair가 충분히 회복되는지 시험했다.

## Relations

- `part_of` → [[project-ontology-reasoner-mcp]]
- `refines` → [[concept-is-a-vs-part-of]]
