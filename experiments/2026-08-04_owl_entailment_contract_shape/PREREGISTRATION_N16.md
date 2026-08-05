# PREREGISTRATION_N16 — E-A / E-B 사후 표본 확대 (N=8/arm → N=16/arm)

> ## 🔴 실행 금지 — D-OWL-1로 무효화됨 (2026-08-05)
>
> **이 사전등록의 trial을 실행하지 마라.** 외부 설계 판정
> `../DESIGN_DECISION_owl_EB_laundering_confound.md`(D-OWL-1) §5가
> "이 실험 안에서" 금지한 목록에 **"N=8/arm 추가 실행"**이 문면 그대로
> 있다 — 이 문서가 정확히 그것이다(N=8→16, 8 trial/arm 추가).
>
> 이 문서 §1.3이 스스로 목적을 "laundering 확증 아님, provenance_effect
> 정밀도 확인"으로 좁혀 둔 것은 사실이고 그 판단은 정직했다. 그러나 D-OWL-1
> §5의 금지는 목적 조건 없이 **추가 실행 자체**를 금지하며, 판정문은 이
> 좁힌 목적에 대한 예외를 명시하지 않는다. 운영 세션은 그 예외를 스스로
> 만들지 않는다 — 그건 "운영 세션이 임의로 정하지 않는다"는 이 실험의
> 반복된 규율을 어기는 것이다.
>
> 이 문서를 삭제하지 않고 보존하는 이유는 §1의 사후 공개 7항이 정직한
> 사전등록 규율의 실제 사례이기 때문이다 — 판단은 D-OWL-1에 의해
> **초과(overridden)**된 것이지 **틀렸던 것**이 아니다. 처분 경위 전문은
> `OPERATIONS_LOG.md` 2026-08-05 항목.

- 작성: 2026-08-05. 최초 코호트(N=8/arm, 32 trial) 실행·채점·`RESULTS.md`
  작성 **이후**.
- `PREREGISTRATION.md`는 이미 실행된 N=8 코호트의 동결 기록이므로 수정하지
  않는다. 이 문서는 그것을 대체하지 않고, 별도의 사후(post-result) 표본
  확대 코호트를 사전등록한다.
- 선례: `../2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_residual_prohibition.md`
  (D-H1a-10) §11의 "사후 발견에 따른 새 사전등록 조건" 7항 형식을 그대로
  따른다.

## 0. 왜 이 문서가 필요한가

`PREREGISTRATION.md` §6:

> 결과를 본 뒤 코딩 규칙이나 N을 바꾸지 않는다.

N=8 결과를 이미 보고한 뒤 N을 16으로 올려 재실행하는 것은 이 규칙의 문면을
벗어난다. 따라서 "같은 사전등록의 연장"이 아니라 **새 사전등록을 쓰는 별도
코호트**로 취급한다. 이 코호트를 최초 결과를 모르는 상태에서 설계된 실험인
것처럼 표현해서는 안 된다.

## 1. 사후 발견에 따른 새 사전등록 조건 (D-H1a-10 §11 형식)

```text
1. 최초 코호트 결과: E-A는 CONTRACT_FLAT 0/40 correct(100% cannot_tell) ->
   CONTRACT_RECORD 40/40 correct. E-B는 MCP_ONLY 2/16 correct(전부
   edge-무관 blanket 판정, 판별 아님) -> PROVENANCE 16/16 correct.
   laundered_proposed_as_verified는 양 arm 다 0건.
2. 최초 결과 확인 후 발견된 사실: 두 실험의 프롬프트에 양 arm 공통으로
   표적 행동을 직접 금지하는 문장이 있다(E-B: "Do not assume a relationship
   is verified merely because it was returned by a tool call.", E-A의
   유사 문장은 RESULTS.md 참조). RESULTS.md는 이 때문에 E-B의
   laundering_hypothesis를 `null_effect`가 아니라 `insufficient_evidence`로
   표기했다 — H1a Q10의 비식별 코호트와 구조적으로 같은 결함.
3. 재설계(N 확대) 사유는 결과의 방향이 아니라 관측 해상도다 — N=8이 탐색
   단계에 적합한 값이었다는 최초 사전등록의 근거(§3)를 확증 단계 표본으로
   올리는 것뿐, E-A/E-B 어느 쪽 결과가 마음에 안 들어서가 아니다. **다만
   정직하게 명시한다: N을 16으로 올려도 E-B의 insufficient_evidence는
   해소되지 않는다.** 이것은 표본 크기 문제가 아니라 식별(identification)
   문제다 — 양 arm에 공통으로 들어간 금지 문장이 laundering이라는 표적
   행동 자체의 관측 경로를 차단했으므로, 같은 프롬프트로 시행 수만 늘리면
   같은 차단이 16배로 반복될 뿐이다. RESULTS.md의 결론을 그대로 인용한다:
   "수선안: laundering을 재검증하려면 그 금지 문장을 제거한 arm이
   필요하다. 그런데 그러면 '금지 문장 유무'가 두 번째 조작 변수로 끼어들어
   2×2가 된다... 운영 세션이 임의로 정하지 않고 후속 과제로 분리한다."
   이 코호트는 그 후속 과제를 수행하지 않는다 — 프롬프트는 N=8 원본과
   byte-identical이다(`prompt_sha256`으로 확인 가능). 따라서 E-B 다리의
   목적은 "laundering 여부를 확증한다"가 아니라 "provenance_effect(구별
   능력)가 N=8 표본에서 우연이 아니었는지 정밀도를 높인다"로 좁힌다. E-A
   다리는 이런 식별 결함이 보고되지 않았으므로 confirmatory 정밀도 확대로
   읽을 수 있다.
4. 기존 `_coder.py`의 outcome 정의(범주 5종, ground truth 규칙)는 전혀
   바꾸지 않는다. `_contracts.py`(arm renderer)와 두 fixture도
   byte-identical로 재사용한다(`_owl_cohort_n16.py`가 동일 모듈을 import).
5. 기존 코호트(N=8, 32 trial: `trials.json`, `cohort_score.json`,
   `RESULTS.md`)와 이 코호트를 병합하지 않는다. 새 `cohort_id`
   (`owl_ea_eb_n16_confirmatory_20260805`)를 부여하고, 출력은
   `trials_n16.json` / `cohort_score_n16.json`처럼 별도 파일에 쓴다.
6. 양 실험(E-A, E-B) 모두 동일 arm 정의·동일 fixture·동일 프롬프트로
   N=16/arm 재실행한다 — 실험당 32 trial, 총 64 trial.
7. 이 코호트는 post-result sample-size increase임을 `RESULTS_N16.md`
   (채점 후 작성 시)에 명시한다. 최초 N=8 코호트와 동일한 의미의 최초
   사전등록이나 독립 복제(independent replication)로 부르지 않는다.
```

## 2. 변경/불변 요약

| 항목 | N=8 원본 | N=16 코호트 |
|---|---|---|
| N/arm | 8 | **16** |
| 총 trial | 32 | **64** |
| arm 정의 | `_contracts.py` | 동일(불변) |
| fixture | `fixture_owl_entailment.json`, `fixture_candidate_vs_entailed.json` | 동일(불변, byte-identical) |
| 프롬프트 템플릿 | `prompt_templates.md` | 동일(불변) — `prompt_sha256`으로 검증 가능 |
| coder | `_coder.py` | 동일(불변) |
| schema | `schemas.json` | 동일(불변) |
| 모델/transport | `claude-opus-5`, `tools: []`, cold subagent | 동일 |
| trial_id 네임스페이스 | `EA-*`/`EB-*` | `N16-EA-*`/`N16-EB-*` (충돌 없음) |
| cohort_id | (없음, 단일 코호트였음) | `owl_ea_eb_n16_confirmatory_20260805` |
| 출력 파일 | `trials.json`, `cohort_score.json`, `RESULTS.md` | `trials_n16.json`, `cohort_score_n16.json`, `RESULTS_N16.md` (별도) |
| 매니페스트 생성기 | `_owl_cohort.py` | `_owl_cohort_n16.py` |
| workflow 스크립트 | `owl_cohort_workflow.js` | `owl_cohort_workflow_n16.js` |

## 3. 보고 규약 (원본 §6 계승 + 추가)

- 표본은 여전히 K=1(실험당 fixture 1개)이다. 일반 모델 성향으로
  일반화하지 않는다.
- `invalid` 비율이 50% 이상이면 코더/스키마 문제로 보고 결과를 해석하지
  않는다.
- **E-B 결과를 laundering 가설의 확증/반증으로 보고하지 않는다** — §1-3에
  기록한 식별 결함이 이 코호트에도 그대로 있다. E-B는 provenance_effect
  (구별 능력) 정밀도 확인으로만 보고한다.
- 결과를 본 뒤 이 문서의 코딩 규칙이나 N을 다시 바꾸지 않는다.
