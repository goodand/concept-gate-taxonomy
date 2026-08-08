# E2.2.1 — directed PC 마이크로 보정 (사전등록)

E2.2 결과(`experiments/2026-07-23_isa_certificate_structure_bvsc/`)에서
directed positive control(`dir1_directed`)이 0/10으로 실패했다. 원인 후보:
프롬프트/스키마가 `structural_composition`이라는 repair vocabulary를 모델에게
**한 번도 노출한 적이 없었다** — 모델이 본 `type` 값은 입력 전체에서
`essential_feature`/`functional` 두 가지뿐이었고, `repaired_concepts`의
`features[].type` 스키마도 무제약 `object`였다.

## 유일 가설 (B-C 아님)

`structural_composition`을 포함한 전체 6종 FeatureType vocabulary를 prompt와
schema에 명시적으로 노출하면, directed PC 통과율이 임계치(0.80, E2.2의
c6 기준과 동일) 이상으로 회복되는가?

**이것은 control affordance 하나만 확인하는 단일 arm 체크다.** E2.2의 B-C
본가설(구조화 certificate vs 평문 warning)은 여기서 재사용하지 않는다 — arm은
`FULL` 하나뿐이고 대조군이 없다.

## 변경한 것 (E2.2 대비 diff)

- `decision_schema.json`: `repaired_concepts[].features[].type`을 무제약
  `object`에서 6종 enum(`essential_feature, contextual_usage, locational,
  functional, social_treatment, structural_composition`)으로 제약.
- `_gen_prompts.py`의 프롬프트: `repair` 선택지 설명에 위 6종 vocabulary와
  "구성 부분이다" 류 증거 → `structural_composition` 사용 규칙을 한 문장 추가.
- 그 외 전부 동일: `dir1_directed`의 input_concepts/oracle, `_cert_core.py`,
  실행 vehicle(schema-forced + `e2.2-decider` agentType), 채점 함수
  (`classify_directed_repair`)는 E2.2 evaluate.py에서 **바이트 단위로 그대로
  복사**했다 — 통과/실패 정의 자체는 바뀌지 않았다.

## 표본 크기

N=20 (fixture 1개 × arm 1개 × trial 20). 10~30 범위 내 중간값. B-C 같은
클러스터 검정이 필요 없는 단일 비율(rate) 추정이므로 permutation/bootstrap
불필요 — `evaluate.py`가 단순 rate ≥ 0.80 여부만 판정한다.

## Go/No-go (유일 기준)

`structural_composition_repair` 비율 ≥ 0.80 → GO(affordance 가설 지지).
미달 → NO_GO(vocabulary 노출만으로는 부족 — 더 깊은 추론 실패로 재분류).

## 불변조건

- E2.1/E2.2 파일 수정 금지 (모두 frozen).
- trial 모델 = Haiku, 격리 = `e2.2-decider`(`tools:[]`) agentType, schema-forced
  구조화 출력. E2.2에서 검증된 것과 동일한 vehicle 재사용.
- `_gen_prompts.py`는 설계 파일 전부가 커밋된 뒤에만 매니페스트 생성을 허용한다
  (사전등록 잠금, E2.1/E2.2와 동일한 메커니즘).
