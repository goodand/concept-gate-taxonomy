# tool_description_ab — run_pipeline 설명문 A/B 실험 (2026-07-06)

## 배경 (관측된 실패)

GPTs 웹 클라이언트가 ConceptGate MCP로 "트랜스포머의 어텐션"을 정의하는 테스트에서,
4개 개념(어텐션 / 스케일드 닷프로덕트 / 셀프 / 멀티헤드)을 넣었는데 **DAG edge 0개,
전원 isolated인데 status는 PASS·경고 0** 이 반환됐다. 클라이언트는 이를 "형식 통과"로
보고했고, is-a 계층은 전혀 만들어지지 않았다.

로컬 재현으로 원인 확정:

1. is-a edge는 `parent.essential_attrs < child.essential_attrs`
   (essential feature **라벨 문자열의 엄격한 부분집합 포함**)으로만 생성된다.
2. 클라이언트가 각 개념에 서로 다른 산문형 feature를 쓰면 공유 라벨이 0 →
   edge가 수학적으로 불가능 → 전원 고립인데 PASS.
3. `"트랜스포머의 어텐션이다"` 같은 is-a 주장 문장을 essential feature로 넣어도
   edge는 생기지 않는다 (개념명은 edge를 만들지 않음).
4. 이 계약은 `conceptgate://client-guide` resource에는 있었지만, GPTs류 클라이언트는
   resource를 읽지 않고 **tool description만 본다**. 당시 description은
   "essential_feature creates is-a DAG edges"라고만 말해 "type만 맞추면 edge가
   생긴다"는 오해를 유도했다.

## 가설

run_pipeline tool description에 EDGE CONTRACT(라벨 verbatim 반복 + 종차 추가)를
직접 기술하면, description만 보는 클라이언트 LLM도 올바른 계층 입력을 만든다.

## 방법

- **과제**: "Attention Is All You Need" 3.2절 발췌(고정 evidence)만으로 위 4개 개념의
  run_pipeline 입력 JSON 생성. 프롬프트는 "edge를 만들라"고 말하지 않음 —
  그것을 가르치는 것은 description의 몫.
- **ARM A**: 당시 운영 중이던 description 원문.
- **ARM B**: EDGE CONTRACT 문단을 추가한 description.
- 각 arm 5 trial, 독립 클라이언트 LLM(Claude, effort=low)이 JSON 생성.
- **채점**: 에이전트 자기보고 없이, 반환된 JSON을 실제 `ConceptPipeline`에 통과시켜
  edge/isolated 계수 (`evaluate.py`).

## 결과

```
arm trial status              edges  isolated cross-lint
A   1     PASS                0      4        ISA_CLAIM_FEATURE,NO_SHARED_ESSENTIAL_LABELS
A   2     PASS_WITH_WARNING   0      4        ISA_CLAIM_FEATURE
A   3     PASS                0      4        ISA_CLAIM_FEATURE,NO_SHARED_ESSENTIAL_LABELS
A   4     PASS                0      4        ISA_CLAIM_FEATURE,NO_SHARED_ESSENTIAL_LABELS
A   5     PASS                0      4        ISA_CLAIM_FEATURE,NO_SHARED_ESSENTIAL_LABELS
B   1     PASS                3      0        -
B   2     FAIL                0      4        -
B   3     PASS                3      0        -
B   4     PASS                3      0        -
B   5     PASS                3      0        -

ARM A: full-hierarchy(3+ edges) 0/5 | mean edges 0.0
ARM B: full-hierarchy(3+ edges) 4/5 | mean edges 2.4
```

- **ARM A 0/5** — GPTs 실패 모드를 그대로 재현 (전 trial 0 edge).
- **ARM B 4/5** — root(어텐션) → 자식 3개의 올바른 계층.
- **B-2 FAIL 분석**: 부모 라벨을 반복했지만 자식에서 type을 `functional`로 둠 →
  Anti-Context Gate가 정상 차단. → description에 "반복 라벨은 자식에서도
  essential_feature type 유지" 문구 추가로 대응.
- **linter 교차 검사 검증**: 신설 `ISA_CLAIM_FEATURE` + `NO_SHARED_ESSENTIAL_LABELS`가
  ARM A 불량 입력 5/5에서 발화, ARM B 정상 입력 5/5에서 오탐 0.

## 반영된 변경

1. `files/server.py` — run_pipeline docstring에 EDGE CONTRACT 명시
   (verbatim 라벨 반복 + 종차 + type 유지 + worked example).
2. `cg_input_linter.py` — 교차 개념 검사 2종 추가:
   - `NO_SHARED_ESSENTIAL_LABELS`: 모든 개념 쌍이 essential 라벨 비공유 → DAG 공집합 예고
   - `ISA_CLAIM_FEATURE`: 다른 개념명 + 주장 표지(이다/일종/is a 등) → 문장형 is-a 선언 감지
3. `files/server.py` — **lint 자동 주입**: run_pipeline 응답에 lint 이슈가 있으면
   `lint` 필드로 첨부. 클라이언트가 lint_concepts를 건너뛰어도 경고가 도달한다
   (깨끗한 입력에는 붙이지 않음).

## 재현

```bash
# repo 루트에서
python3 experiments/2026-07-06_tool_description_ab/evaluate.py
```

trials.json은 클라이언트 LLM이 생성한 원시 출력 그대로이며 수정하지 않았다.
