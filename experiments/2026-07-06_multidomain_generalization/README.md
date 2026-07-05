# multidomain_generalization — 도메인 일반화 검증 (2026-07-06)

## 질문

tool_description_ab 실험은 트랜스포머/어텐션 한 도메인에서만 EDGE CONTRACT 효과를
확인했다. 이 계약과 linter가 **어텐션 밖의 임의 자연어 도메인에서도** 클라이언트
LLM이 올바른 is-a 입력을 만들게 하는가?

## 방법

- EDGE CONTRACT를 명시한 run_pipeline description(도메인 중립 worked example:
  사각형/직각)만 클라이언트에게 제공.
- **4개 도메인 × 3 trial = 12건**, 독립 클라이언트 LLM(Claude, effort=low)이
  concepts JSON 생성. 프롬프트는 부모/자식 개념명과 짧은 도메인 힌트만 주고,
  "edge를 만들라"는 방법 지시는 하지 않음 (계약 학습은 description의 몫).
  - biology: 포유류 → 고래 / 박쥐 / 사자
  - geometry: 사각형 → 직사각형 / 마름모 / 정사각형
  - law: 계약 → 매매계약 / 임대차계약 / 증여계약
  - cooking: 발효식품 → 김치 / 요구르트 / 치즈
- **채점**: 에이전트 자기보고 없이, 반환 JSON을 실제 `ConceptPipeline`에 통과시켜
  edge/isolated 계수 (`evaluate.py`).

## 결과

```
domain    trial status  edges  isolated cross-lint
biology   1     PASS    3      0        -
biology   2     PASS    3      0        -
biology   3     PASS    3      0        -
geometry  1     PASS    4      0        -
geometry  2     PASS    4      0        -
geometry  3     PASS    4      0        -
law       1     PASS    3      0        -
law       2     PASS    3      0        -
law       3     PASS    3      0        -
cooking   1     PASS    3      0        -
cooking   2     PASS    3      0        -
cooking   3     PASS    3      0        -

TOTAL: 12/12 trials formed the full is-a hierarchy
```

- **12/12** 전 도메인에서 root → 자식 3개의 올바른 is-a 계층 형성.
- **geometry는 4 edge** — 정사각형이 직사각형과 마름모 양쪽 essential 라벨을 모두
  포함해 두 부모를 갖는 lattice(다중 상속)까지 정확히 형성. FCA 부분집합 포함
  의미가 도메인 무관하게 작동함을 보여준다.
- **cross-lint 오탐 0/12** — 계약을 지킨 정상 입력에는 도메인 중립 linter가
  경고를 내지 않음.

## 결론

EDGE CONTRACT + 도메인 중립 linter는 어텐션에 특화되지 않는다. 클라이언트가
부모 essential 라벨을 verbatim 반복 + 종차 추가라는 계약만 지키면, 생물·기하·법·
요리 등 임의 도메인에서 동일하게 올바른 taxonomy가 생성된다.

## 재현

```bash
python3 experiments/2026-07-06_multidomain_generalization/evaluate.py
```

trials.json은 클라이언트 LLM 원시 출력 그대로이며 수정하지 않았다.
