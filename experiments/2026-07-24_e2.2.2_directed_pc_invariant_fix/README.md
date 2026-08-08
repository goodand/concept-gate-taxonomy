# E2.2.2 — directed PC 마이크로 보정 라운드 2 (사전등록)

E2.2.1(vocabulary 노출)이 0/10 → 3/20(0.15)로 소폭 개선했으나 임계치(0.80)
미달로 가설 기각. E2.2.1의 실제 trial report 텍스트를 근거로 근본 원인을
재분석한 결과, vocabulary 문제가 아니라 **명세되지 않은 두 구조 계약**이
원인이었다:

1. **전역 일관성 부재** (wrong_direction_repair 11/20, 55%): 동일 feature
   이름이 여러 concept에 나타날 때 모델은 각 concept의 evidence 문장을
   독립적으로 판단해 "다른 concept은 다른 type이어도 정당하다"고
   합리화했다 (E2.2.1 trial 3: "a structural component in 돌체 and a
   functional role in 돌체린").
2. **complete-state 계약 부재** (destructive_repair 6/20, 30%): 모델이
   충돌을 정확히 인지하고도(trial 9) 수정한 concept만 반환하고 나머지
   concept을 누락했다.

## 유일 가설 (B-C 아님, E2.2.1과 동일 성격)

위 두 계약을 (a) prompt에 명시적 규칙으로 서술하고 (b) 계약 2는 스키마
`minItems`로 구조적으로도 강제하면, directed PC 통과율이 0.80 이상으로
회복되는가?

## E2.2.1 대비 diff

- `decision_schema.json`: `repaired_concepts`에 `minItems: 2` 추가
  (dir1_directed의 정확한 concept 개수에 맞춘 fixture-specific 강제 —
  범용 스키마 아님).
- `_gen_prompts.py`의 프롬프트: E2.2.1의 vocabulary 문장에 두 문장 추가 —
  전역 일관성 규칙("다른 concept이 다른 type을 유지하는 것은 정당화되지
  않는다")과 complete-state 규칙("input_concepts의 모든 concept을 빠짐없이
  포함하라").
- 그 외 전부 동일: fixture, `_cert_core.py`, 실행 vehicle, 채점 함수
  (`classify_directed_repair`)는 E2.2/E2.2.1과 바이트 단위로 동일.

## 표본 크기 및 Go/No-go

N=20 (E2.2.1과 동일, 비교 가능하도록). `structural_composition_repair`
비율 ≥ 0.80 → GO. 미달 → NO_GO — 이 경우 vocabulary+명시적 규칙+스키마
강제까지 다 줘도 안 되는 것이므로, 문제는 프롬프트 명세 수준이 아니라
**모델이 스스로 "이게 하나의 feature 정체성이니 전체를 봐야 한다"는 추론을
자발적으로 하지 못하는, 더 깊은 계층**이라고 재분류해야 한다 (이 경우
다음 단계는 명세 추가가 아니라 다른 개입 — 예: repair 전 자기 점검 단계
분리, 또는 애초에 이 반례를 certificate가 직접 구조로 표현).

## 불변조건

E2.1/E2.2/E2.2.1 파일 수정 금지. trial 모델 = Haiku, 격리 = `e2.2-decider`,
schema-forced 구조화 출력. `_gen_prompts.py`는 설계 파일 전부가 커밋된
뒤에만 매니페스트 생성을 허용한다(사전등록 잠금).
