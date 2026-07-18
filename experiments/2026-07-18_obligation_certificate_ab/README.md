# obligation_certificate_ab — certificate 한계 효과 실험 (2026-07-18)

## 배경 (배선 커밋 cc0e4b3)

`run_pipeline`·`expand`·`classify_owl` 응답에 obligation certificate를 배선했다
(`verdict` × `assurance` 이중 기록, decider별 판정). 배선의 정당화 근거 중
하나로 "certificate가 클라이언트의 수리 행동을 바꾼다"를 걸었다. 이 실험은 그
근거가 실제로 성립하는지 검증한다.

`tool_description_ab`(2026-07-06)에서 관측된 실패 모드와 동형: `status=PASS`인데
사실상 실패한 응답을 클라이언트가 "형식 통과"로 완료 보고하는 문제. certificate는
같은 실행을 `obligations.verdict: fail`로 명시한다.

## 가설

aggregate `verdict: fail` + per-obligation `reason`이 있으면(ARM B), 클라이언트
LLM은 완료 보고 대신 입력을 수리한다. certificate가 없으면(ARM A) WARNING을
비차단 신호로 읽고 완료 보고하는 비율이 높다.

## 방법

- **고정 fixture**: MixRig 유발 — `개.꼬리=essential_feature` vs
  `고양이.꼬리=functional`. 실측 응답: `status=PASS_WITH_WARNING`,
  `anti_patterns=1`, (ARM B에서만) `obligations.verdict=fail`.
- **ARM A**: 응답에서 `obligations` 필드만 **제거**. 나머지(status·anti_patterns·
  lint)는 그대로 — 즉 이 실험은 certificate의 **한계 효과(marginal effect)**를
  기존 신호 위에서 측정한다.
- **ARM B**: `obligations` certificate 포함 전체 응답.
- 두 arm 동일 과제 프롬프트: "너는 MCP 클라이언트다. 이 응답을 받았다. 다음
  행동을 JSON으로 결정하라." certificate 의미는 **설명하지 않는다** — 응답 필드가
  스스로 가르쳐야 한다(tool_description_ab와 동일 원칙).
- 각 arm **5 trial**, 독립 클라이언트 LLM(Claude Haiku, 매 trial 콜드 컨텍스트).
  전 trial `tool_uses=0` — 순수하게 응답 JSON만 보고 판단.
- **채점**: 자기보고 배제. `decision`은 출력 JSON 구조로, 수리 효과는 수리본을
  실제 `ConceptPipeline` + `cg_obligations.certify`에 통과시켜 판정(`evaluate.py`).

## 결과

```
arm trial decision    post_status         post_anti post_verdict effective
A   1     repair      PASS                0         pass         True
A   2     repair      PASS                0         pass         True
A   3     repair      PASS                0         pass         True
A   4     repair      PASS                0         pass         True
A   5     repair      PASS                0         pass         True
B   1     repair      PASS                0         pass         True
B   2     repair      PASS                0         pass         True
B   3     repair      PASS                0         pass         True
B   4     repair      PASS                0         pass         True
B   5     repair      PASS                0         pass         True

ARM A: repair 5/5 | effective repair 5/5 | false-done 0/5
ARM B: repair 5/5 | effective repair 5/5 | false-done 0/5
```

**천장 효과 — certificate의 행동 변화 한계 효과는 검출되지 않았다.**

- 양 arm 모두 5/5 repair, 5/5 effective, false-done 0.
- 이유: MixRig는 `anti_patterns`와 `lint`(NO_SHARED_ESSENTIAL_LABELS)에서 이미
  충분히 시끄럽다. certificate를 제거해도(ARM A) 클라이언트는 그 신호만으로
  수리한다. certificate는 이 실패 모드에서 **같은 정보의 타입 재표현**이라
  한계 정보량이 0이다.

### 이것이 말해주는 것 (음성 결과의 값)

1. **certificate를 "행동 변화"로 정당화하지 마라.** 현재 배선된 4개 obligation은
   전부 기존 필드(`composition_issues`·`anti_patterns`)를 거울처럼 재표현한다.
   행동을 이미 그 필드들이 유발한다.
2. **certificate의 실제 값은 두 곳에 있다** — 이 실험이 건드리지 않은 축:
   - **assurance 등급**: "누가 PASS를 발급했나"의 감사 추적(결정론 세탁 방지).
     행동이 아니라 신뢰성의 문제라 repair-rate로는 측정되지 않는다.
   - **certificate-only 신호**: status·anti_patterns·lint가 전부 침묵하는데
     의무만 미충족인 경우. 현재 배선엔 그런 obligation이 없다 — 전부 기존 신호의
     사본이기 때문. 그런 obligation은 **semantic obligation 신규 4종**
     (`evidence.full_support`·`relation.is_a`·`relation.part_of`·
     `definition.sufficient`)에서 처음 생긴다.
3. **다음 실험 설계 요구**: semantic obligation을 검증하려면 fixture가
   "다른 모든 신호는 깨끗한데 의무만 UNKNOWN/FAIL"이어야 한다. 그때 비로소
   ARM A/B가 갈린다. 이 실험은 그 대조군을 만들 수 없음을 확인했다(현재 obligation은
   전부 거울).

## 관측 2 — reasoner per-call 지연

`classify_owl`(HermiT subprocess) 소형 온톨로지 10회 (`measure_latency.py`):

```
min=475  median=498  p95=539  max=539  (ms)
60s 예산 소진 ≈ 120회/세션 (median 기준)
```

- 검토 때 실측한 611~1638ms와 같은 규모(호출당 수백 ms, 콜드 편차 있음).
- warm JVM gateway 트리거를 정량화: median 498ms면 60s 예산에 ~120회. 기존 검토가
  건 "세션당 >20회" 트리거는 보수적 — 실측 예산은 그 6배. **단일 사용자 간헐
  사용에선 per-call HermiT로 충분**하다는 이전 결론을 지지한다.

## 반영된 변경

**소스 변경 없음.** 이 실험은 배선(cc0e4b3)의 정당화 근거를 검증했고, 결과는:

- certificate를 "행동 변화" 근거로 홍보하지 않는다(음성).
- certificate는 assurance 감사 + 미래 semantic obligation의 certificate-only
  신호로 정당화한다.
- semantic obligation 4종 구현 시 **certificate-only fixture**로 A/B를 다시 한다.

## 재현

```bash
# repo 루트에서
venv/bin/python experiments/2026-07-18_obligation_certificate_ab/evaluate.py
venv/bin/python experiments/2026-07-18_obligation_certificate_ab/measure_latency.py
```

trials.json은 클라이언트 LLM 원시 출력 그대로이며 수정하지 않았다.
fixture.json은 배선된 서버가 생성한 실제 응답(입력·stripped·full)이다.
