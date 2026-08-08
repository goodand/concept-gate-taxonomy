# E2.3 — Global Feature-Type Invariant Generalization (사전등록, 2-stage 스크리닝)

E2.2.3(OFAT ablation, N=60)의 결과는 결정적이고 비대칭적이었다:

```
A_ONLY (전역 일관성 규칙만) = 20/20 = 1.00
B_ONLY (complete-state 규칙만) = 1/20 = 0.05
C_ONLY (schema minItems만)    = 0/20 = 0.00
```

하지만 E2.2.1/E2.2.2/E2.2.3 전부가 **fixture 1개(dir1_directed)** 위에서만
실행됐다. A_ONLY의 "완전 충분"이 이 fixture의 특정 문장/구조에 우연히
들어맞은 효과인지, 아니면 repo 결합 전에 신뢰할 수 있는 reasoning
contract 메커니즘인지는 검증되지 않았다.

## 핵심 가설

> 동일 feature 이름은 모든 concept에서 같은 type이어야 한다는 전역
> 불변조건을 명시하면, 모델은 local evidence justification이 아니라
> global state normalization으로 repair한다 — 이는 특정 fixture의 문장
> 효과가 아니라 일반화 가능한 메커니즘이다.

## 설계 — 5개 arm-cell, 3개 새 fixture

| arm | fixture | 조건 | 목적 |
|---|---|---|---|
| CONTROL | baseline_directed | vocab only | 기존 실패 패턴이 새 fixture에서도 재현되는지 |
| A_ONLY | baseline_directed | vocab + E2.2.3와 동일한 규칙 문장 | A 효과가 dir1_directed 밖에서도 재현되는지 |
| A_PARAPHRASE | baseline_directed | vocab + 같은 의미, 다른 문장 | 특정 문구 암기가 아니라 의미 내용 효과인지 |
| A_TOPOLOGY | topology_directed (3 concept, 공유 feature 2개) | vocab + 동일 규칙 문장 | 2-concept/1-feature 밖으로 구조가 일반화되는지 |
| A_DECOY | decoy_directed (더 강한 유혹 evidence) | vocab + 동일 규칙 문장 | local evidence의 유혹에 저항하는지 |

세 fixture 모두 `_cert_core.run_and_certify`로 사전 검증됨(정확히
의도한 MixRig anti-pattern이 트리거되는지 확인 — 아래 "불변조건" 참조).

### baseline_directed
dir1_directed와 같은 형태(2 concept, 공유 feature 1개)지만 표면 어휘가
완전히 다르다(카페린/카페토/손잡이 — 돌체/돌체린/바퀴가 아님). 목적은
"같은 규칙이 새로운 어휘에도 통하는가"를 보는 것이지, 동일 fixture를
재사용해 결과를 부풀리는 게 아니다.

### topology_directed
3 concept, 서로 다른 2개의 공유 feature(구동축은 엔진박스/엔진박스보조만
공유, 냉각판은 엔진박스/엔진박스확장만 공유 — 3 concept 전부가 두
feature를 다 갖지는 않음). `evaluate.py`의 `classify_directed_repair`는
이 때문에 E2.2.x 계열의 단일-part_feature 버전에서 **일반화**됐다 —
`part_features` 리스트를 받아 각 feature를 원래 그 feature를 가졌던
concept들에 대해서만 검사한다(단일 feature 케이스에서는 기존과 동일하게
동작).

### decoy_directed
차체프레임신형의 고정핀 evidence가 E2.2.3의 어떤 fixture보다 강한
유혹이다 — 단순 functional이 아니라 **social_treatment**(고급 모델의
상징적 장치)로 읽히도록 설계됐다. 그럼에도 ground truth는 동일하게
structural_composition 통일이다(차체프레임 쪽 evidence가 명시적 부분-
전체 관계).

## 운영 프로토콜 — 2-stage 적응적 스크리닝

`docs/experiment_screening_protocol.md` 참조, 이 실험에 맞게 재확인:

- **Stage 1**: arm-cell당 N=10, threshold **0.90**.
  - 9~10/10 → `screened` (스크리닝 통과, 잠정)
  - 0~6/10 → `screened_out` (스크리닝 탈락, 잠정) — 그대로 NO_GO
  - 7~8/10 → `provisional_escalate` → **Stage 2로 자동 승격**
- **Stage 2**: 해당 arm만 10개 증분(누적 N=20), threshold **0.80**
  (E2.x confirmatory 계열과 정렬). 결과는 `candidate_gate_pass`/
  `candidate_gate_fail`.
- **"confirmed" 표현 금지** — Stage 1/2 결과 모두 screened/provisional/
  candidate gate 어휘만 사용한다. 이 실험은 정식 group-sequential
  유의성 검정이 아니라 descriptive escalation이다.

## 예상 (반증 가능하도록 명시)

- **CONTROL**: E2.2.1(vocab only, 0.15)과 비슷하게 낮을 것으로 예상 —
  기존 실패 패턴 재현.
- **A_ONLY**: 높을 것(≥0.90)으로 예상 — dir1_directed와 구조가 같으므로.
- **A_PARAPHRASE**: A_ONLY와 비슷하게 높을 것으로 예상 — 낮게 나오면
  E2.2.3의 효과가 특정 문구에 의존했다는 뜻.
- **A_TOPOLOGY**: A_ONLY보다 낮을 수 있음 — 3-concept/2-feature 구조가
  단순한 2-concept 케이스보다 어려울 수 있음.
- **A_DECOY**: A_ONLY보다 낮을 수 있음 — 더 강한 유혹 evidence가 규칙을
  압도할 수 있음.

낮은 결과가 나온 arm은 "실패"가 아니라 "어느 조건에서 일반화가 깨지는가"를
알려주는 정보다 — 진단적 목적.

## 불변조건

E2.1/E2.2/E2.2.1/E2.2.2/E2.2.3 파일 수정 금지. `_cert_core.py`는
E2.2.2에서 바이트 단위로 복사(변경 없음). trial 모델 = Haiku, 격리 =
`e2.2-decider`(`tools:[]`) agentType, schema-forced 구조화 출력 —
이전 라운드와 동일 vehicle. `_gen_prompts.py`는 설계 파일 전부가 커밋된
뒤에만 매니페스트 생성을 허용한다(사전등록 잠금). 세 fixture 모두
`run_and_certify`로 정확한 precondition(status/anti 개수)을 사전 확인함
(설계 시점 검증 로그는 세션 기록 참조 — fixture.json의 precondition
필드가 그 확인된 값).

## 이 실험 이후

통과(candidate gate pass, 특히 A_TOPOLOGY/A_DECOY)하면 다음 마일스톤은
repo/reasoner 결합 실험으로 넘어갈 근거가 생긴다. 실패하면 아직
integration 문제가 아니라 **contract specification 문제**(어떤 조건에서
규칙이 깨지는지)가 남아있다는 뜻 — `docs/obligation_layer_roadmap.md`의
"다음 실험(E2.3)" 문단에 결과를 반영한다.
