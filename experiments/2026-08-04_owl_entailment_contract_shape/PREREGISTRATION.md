# PREREGISTRATION — E-A / E-B (owl entailment contract shape)

- 작성: 2026-08-05. **trial 0건 시점.**
- 지위: 채택 전 검증(pre-adoption verification). `classify_owl`의 반환 계약을
  `hierarchy: child→parents` 평면 맵에서 `entailed_is_a: proof-carrying
  relation records`(origin + assurance)로 바꾸자는 제안을, 실제로 채택하기
  전에 두 가지 위험을 확인한다.
- 정답 없는 실험 아님 — H1a와 달리 **여기는 ground truth가 있다**(fixture의
  origin/assurance 필드, 실험 설계 시점에 고정). "correctness"를 측정하되,
  correctness 자체는 fixture 설계자가 사전에 정한 사실 관계이지 판정자의
  주관적 판단이 아니다.

## 0. 연구 질문

**E-A (contract shape)**: 계약이 `hierarchy`(평면)일 때와 `entailed_is_a`
(레코드, origin/assurance 포함)일 때, 클라이언트가 "이 관계가 입력에
명시됐는지 reasoner가 유도했는지"를 얼마나 정확히 구분하는가?

**E-B (laundering)**: 서로 다른 decider(reasoner vs LLM/FCA)에서 온 두
관계가 provenance 없이 제시될 때와 origin/assurance를 동반해 제시될 때,
클라이언트가 "검증됨"을 얼마나 정확히 판정하는가 — 특히 **PROPOSED 등급
관계를 검증됨으로 잘못 단정하는 빈도**(laundering).

## 1. Fixture — repo-grounded

| 실험 | 파일 | 근거 |
|---|---|---|
| E-A | `fixture_owl_entailment.json` | `test_cg_owl.py::test_p2_defined_classes_generate_hierarchy` — Square⊑Rectangle·Square⊑Rhombus는 입력 어디에도 명시 안 됨(순수 derived), Rectangle/Rhombus/Square⊑Parallelogram은 genus로 직접 선언(asserted_and_entailed) |
| E-B | `fixture_candidate_vs_entailed.json` | edge1(Square⊑Rectangle)은 E-A와 동일한 HermiT 유도. edge2(Trapezoid⊑Quadrilateral)는 `concept_gate_v7.py`의 FCA 기반 run_pipeline이 essential_attrs subset inclusion만으로 낼 후보 관계 — `classify_owl`/HermiT를 거친 적 없음. `cg_obligations.py`의 실제 `MAX_ASSURANCE`(`DeciderKind.LLM→SOURCE_ANCHORED`, `DeciderKind.REASONER→REASONER_PROVED`) 사다리에 근거 |

두 실험 다 **arm 간 유일한 차이는 provenance 필드의 유무**다(`_contracts.py`).
사실 관계(어떤 edge가 무엇인지)는 두 arm에서 100% 동일 — H1a의 arm-diff
규율과 같은 이유: 사실까지 다르면 관측 차이를 계약 형태 탓으로 돌릴 수 없다.

## 2. arm

| 실험 | arm | 계약 형태 |
|---|---|---|
| E-A | `CONTRACT_FLAT` | 현재 실제 `classify_owl()` 반환 형태 그대로(`{"hierarchy": {...}}`) |
| E-A | `CONTRACT_RECORD` | 제안된 형태(`{"entailed_is_a": [...]}`, origin+assurance) |
| E-B | `MCP_ONLY` | `{"is_a_relations": [{"subject","object"}]}` — provenance 없음 |
| E-B | `PROVENANCE` | 같은 관계 + `origin`/`assurance`/`decider` |

## 3. N, randomization

| 항목 | 값 |
|---|---|
| N | arm당 **8**, 실험당 총 16, 전체 32 trial |
| 근거 | 탐색적 채택-전 검증 — H1a급 확증 실험이 아니다. K=1(각 실험 fixture 1개)이므로 인증 밴드 없음. N=8은 관측 해상도(1건=0.125)를 확보하되 이 단계에서 큰 비용을 들이지 않는 값 |
| randomization | bundle 단위(같은 replicate index의 두 arm 동시 dispatch), Workflow `parallel()` |
| 모델 | `claude-opus-5`, `tools: []`, cold subagent |
| 제외 기준 | 전송 실패만 재실행(outcome 아님). 출력 내용 기반 제외 없음 |

## 4. 행동 코딩 — `_coder.py`, trial 0건 시점에 동결

- **코더는 `basis`/`summary`(자유서술)를 읽지 않는다.** 오직 `origin_judgment`
  / `verification_judgment` 닫힌 enum만 본다. H1a P5와 동일한 이유 — 결과를
  본 뒤 코딩 규칙을 바꿀 자유도를 없앤다.
- ground truth는 fixture의 `origin`/`assurance` 필드(설계 시점 고정).
- 교정 코퍼스: `test_coder.py`, **12/12 통과**(정상·과대주장·과소주장·
  cannot_tell·잘못된 enum·누락 edge·형식 오류 전 케이스).

### E-A 범주
`correct` / `overclaim_derived_as_asserted`(derived를 asserted로 — **더
위험한 오류**, 유도된 것을 명시적 입력처럼 취급) / `underclaim_asserted_as_derived`
/ `cannot_tell`(정직한 판단 보류 — FLAT에서는 근거가 실제로 없으므로 **오류가
아니다**) / `invalid`.

### E-B 범주
`correct` / `laundered_proposed_as_verified`(**이 실험의 핵심 실패 모드** —
PROPOSED 관계를 검증됨으로 단정) / `excess_caution_proven_as_unverified`
(반대 방향 오류, 덜 위험) / `cannot_tell` / `invalid`.

## 5. 예측 (결과 보기 전 기록)

- E-A: `CONTRACT_RECORD`가 `CONTRACT_FLAT`보다 `correct` 비율이 높을 것.
  `CONTRACT_FLAT`에서는 `cannot_tell`(정직) 또는 `overclaim_derived_as_asserted`
  (기하학적으로 "당연해 보여서" 유도 관계를 명시된 것으로 착각)가 나올 것으로
  예상.
- E-B: `MCP_ONLY`에서 `laundered_proposed_as_verified`가 `PROVENANCE`보다
  유의하게 높을 것 — "MCP가 반환했으니 검증됐다"는 세탁 가설.

**이 예측이 틀려도 결과를 그대로 보고한다.** 예측 불일치 자체가 유용한
발견이다(예: 계약을 바꿔도 행동이 안 바뀌면, 문제는 계약 형태가 아니라 다른
곳에 있다는 뜻).

## 6. 보고 규약

- 표본이 각 32/16이므로 **일반 모델 성향으로 일반화하지 않는다** — 이
  fixture·이 모델·이 transport 조건부 기술로만 보고.
- `invalid` 비율이 50% 이상이면 코더/스키마 문제로 보고 결과를 해석하지
  않는다.
- 결과를 본 뒤 코딩 규칙이나 N을 바꾸지 않는다.
