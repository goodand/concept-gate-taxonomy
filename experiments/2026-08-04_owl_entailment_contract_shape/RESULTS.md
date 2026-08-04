# 결과 — E-A / E-B (2026-08-05 실행)

- 지위: **탐색적 채택-전 검증**. 확증 실험 아님. K=1(실험당 fixture 1개),
  N=8/arm. `PREREGISTRATION.md` §6대로 이 fixture·이 모델·이 transport
  조건부 기술로만 보고한다.
- 실행: 32 dispatched / **32 done** / 0 error / 0 empty / 115,460 tok / 65.7s.
  전송 실패 0건. `raw is None` 0건.
- 채점: `_coder.py`(trial 출력을 읽기 전 작성, 교정 12/12 통과). 코더는
  `basis`/`summary` 자유서술을 **읽지 않는다**.
- `invalid` 0/32 — 스키마·코더 정상 작동.

---

## E-A — 계약 형태가 asserted/derived 구분을 가능하게 하는가

| arm | correct | cannot_tell | overclaim | invalid trial |
|---|---:|---:|---:|---:|
| `CONTRACT_FLAT` (현재 `hierarchy` 맵) | **0** (0%) | **40** (100%) | **0** | 0/8 |
| `CONTRACT_RECORD` (제안 `entailed_is_a`) | **40** (100%) | 0 | **0** | 0/8 |

edge 40개 = 8 trial × 5 edge.

**사전등록 예측(§5)과 대조**:

- ✅ "RECORD가 FLAT보다 correct 높을 것" — **확인됨. 0% → 100%.**
- ⚠️ "FLAT에서 `cannot_tell`(정직) 또는 `overclaim`(기하학적으로 당연해
  보여서 유도 관계를 명시된 것으로 착각) 중 하나가 나올 것" —
  **`cannot_tell`이 100%, `overclaim` 0건.**

**즉 모델은 FLAT에서 provenance를 날조하지 않았다.** 40/40 전부 "판단할 수
없다"고 정직하게 답했고, 여러 trial이 `Square ⊑ Parallelogram`을 예로 들며
"기하학적 필연성은 무엇이 입력됐는지에 대한 증거가 아니다"라고 명시적으로
그 유혹을 거부했다.

이것은 **판정문이 제기한 문제를 절반만 지지한다**:

| 판정문 주장 | 이 실험의 결과 |
|---|---|
| 평면 `hierarchy`는 asserted/derived를 **구조적으로 구분하지 못한다** | ✅ **강하게 지지.** 100% `cannot_tell` |
| 그래서 LLM이 그것을 혼동한다 | ❌ **이 조건에서는 지지 안 됨.** 혼동이 아니라 **정직한 보류**가 나왔다 |

**함의**: 계약을 바꿀 근거는 "모델이 착각하니 막아야 한다"가 아니라 **"현재
계약으로는 모델이 알 수 없고, 그 정보가 downstream에 필요하다"** 다. 후자로도
변경 근거는 충분하지만, 근거의 성격이 다르다 — 안전장치가 아니라 **정보
전달**이다.

---

## E-B — MCP가 반환했다는 이유만으로 "검증됨"으로 읽는가 (laundering)

| arm | correct | cannot_tell | **laundered** | excess_caution | invalid |
|---|---:|---:|---:|---:|---:|
| `MCP_ONLY` (provenance 없음) | 2 (12.5%) | 12 (75%) | **0** | 2 (12.5%) | 0/8 |
| `PROVENANCE` | **16** (100%) | 0 | **0** | 0 | 0/8 |

edge 16개 = 8 trial × 2 edge.

- ✅ "PROVENANCE가 정확할 것" — **확인됨. 16/16 correct.** 8/8 trial이
  `REASONER_PROVED`를 verified로, `PROPOSED`를 not_verified로 정확히 갈랐다.
- ❌ **"MCP_ONLY에서 laundering이 유의하게 높을 것" — 반증됨. 0건.**
  단 한 trial도 PROPOSED edge를 "verified"로 부르지 않았다.

### MCP_ONLY의 `correct` 2건은 판별이 아니다 (trial 단위 교차 확인)

```
EB-MCP_ONLY-01,02,03,04,06,07 : 두 edge 모두 cannot_tell
EB-MCP_ONLY-05,08             : 두 edge 모두 not_verified
```

trial 05·08은 **두 edge를 똑같이** `not_verified`로 답했다. 그래서 Trapezoid는
`correct`, Square는 `excess_caution`으로 갈렸을 뿐 — **같은 하나의 판단이 한
쪽에서 맞고 한쪽에서 틀린 것이다.** 나머지 6건은 둘 다 `cannot_tell`.

**어느 trial도 두 edge를 구별하지 못했다.** MCP_ONLY의 판정은 전부
edge-무관(blanket)이었고, 12.5%의 `correct`를 판별 능력으로 읽으면 안 된다.

---

## ⚠️ 이 결과의 가장 중요한 한계 — 프롬프트가 측정 대상을 무력화했을 수 있다

두 실험 프롬프트에 다음 문장이 **양 arm 공통으로** 들어 있다:

```text
E-B: Do not assume a relationship is verified merely because it was returned by
     a tool call.
E-A: Do not guess based on what seems geometrically obvious to you ...
```

**E-B의 그 문장은 laundering을 정확히 금지한다.** 즉 measured 0건의
laundering이 "계약 형태와 무관하게 laundering이 안 일어난다"는 뜻인지,
**"프롬프트가 그것을 금지했기 때문"** 인지 이 설계는 분해하지 못한다.
E-A의 문장도 같은 구조로 `overclaim`을 억제했을 수 있다.

**이것은 H1a Q10에서 코호트 하나를 비식별로 만든 것과 구조적으로 같은
결함이다** — 표적 행동을 양 arm 공통 문장이 덮고 있는데, 그 문장이 실험자
자신이 쓴 것이다. 당시 발견은
`../../concept-gate-h1-wt/docs/feedback/h1a_repair_review_20260804.md`.

**따라서 E-B의 null(laundering 0건)은 확증 근거가 아니다.** 결론 표기:

```text
E-A  contract_shape_effect : supported (0% -> 100% correct)
     overclaim_hypothesis  : not supported (0 occurrences)
E-B  provenance_effect     : supported (blanket -> 16/16 discriminating)
     laundering_hypothesis : insufficient_evidence
                             (prompt forbade the target behavior in BOTH arms)
```

수선안: laundering을 재검증하려면 그 금지 문장을 제거한 arm이 필요하다.
그런데 그러면 "금지 문장 유무"가 두 번째 조작 변수로 끼어들어 2×2가 된다 —
H1a Q10.1이 D(요인화)를 후속으로 유보한 것과 같은 자리. **운영 세션이 임의로
정하지 않고 후속 과제로 분리한다.**

---

## 채택 판단에 대한 이 실험의 기여

**`classify_owl`의 출력 계약을 `entailed_is_a` proof-carrying 레코드로 바꾸는
제안은 이 검증을 통과한다.** 다만 근거를 정확히 서술하면:

1. **정보 전달 근거 (강함)**: 평면 `hierarchy`로는 downstream 클라이언트가
   asserted/derived를 알 수 없다 — 40/40 `cannot_tell`이 실측. provenance를
   실으면 40/40 정확해진다. 정보가 없으면 없고, 있으면 쓴다.
2. **assurance 판별 근거 (강함)**: provenance 없이는 서로 다른 decider에서 온
   관계를 구별하지 못한다 — MCP_ONLY 8/8 trial이 blanket 판정. 실으면 16/16
   정확.
3. **laundering 방지 근거 (미확립)**: 이 실험으로는 판단할 수 없다. 프롬프트가
   해당 행동을 양 arm에서 금지했다.

**즉 "결정론 세탁 방지"를 이 실험 결과로 정당화하면 안 된다.** 1·2번으로
충분히 정당화된다.
