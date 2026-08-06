# H1a 사전등록 — typed-scope 코호트 (D-H1a-12)

- 작성: 2026-08-05
- 지위: **사전등록.** 이 코호트 trial **0건 시점**에 작성된다.
- 왜 또 새 문서인가: `PREREGISTRATION.md`는 최초 40-trial 코호트의 동결
  기록이고, `PREREGISTRATION_REPAIRED_COHORT.md`는 D-H1a-10/11 수선분의
  동결 기록이다. 둘 다 실행됐거나(전자) 독립 리뷰 3명 전원에게
  `FREEZE_BLOCKED` 판정을 받았다(후자). 방법론 §1이 결과가 설계를 소급
  수정하지 못하게 하라고 요구하므로 그 문서들을 고쳐 쓰지 않는다.
- 근거 판정: `DESIGN_DECISION_H1a_identification_validity.md`(**D-H1a-12**,
  Q12=F typed-scope split). 선행 판정 D-H1a-1~11 전부 구속력 유지.
- 구현 브랜치: `codex/h1a-typed-scope-split`(worktree 격리, 방법론 §4).

---

## 0. 사후 발견에 따른 새 사전등록 조건 (D-H1a-10 §11 형식, D-H1a-12 §15 요구)

D-H1a-12 §15가 명시적으로 요구한 문안을 등재한다.

```text
최초 코호트 결과를 확인한 뒤,
1. 공통 잔여 금지,
2. default permission의 범위,
3. outside knowledge의 범주 포섭,
4. conflict→defer 문구
가 순차적으로 발견되어 설계를 개정했다.
```

**이 코호트를 최초 코호트와 같은 의미의 사전등록이나 독립 복제라고 부르지
않는다.** 최초 40 trial 및 수선 코호트와 **병합하지 않는다**(D-H1a-12 §13).

---

## 1. 승계 — 변경 없이 가져오는 것

| 항목 | 출처 | 상태 |
|---|---|---|
| 가설·arm 정의 | `PREREGISTRATION.md` P1~P3 | 불변 |
| 행동 코더 | `_coder.py` | **불변**(교정 18/18, D-H1a-12 §13이 재사용 명령) |
| fixture | `fixture_source_authority.json` | 불변(Q9=A, L3 한계 유지) |
| Q1 절 바이트 | `_h1a_contract.py::LIVENESS_CLAUSE_TEXT` | 불변(Q1=B/Q5=B 동결) |
| 허용 결론 상한 | `PREREGISTRATION.md` §0 | 불변 — K=1, N을 늘려도 상한은 안 올라간다 |

---

## 2. 동결되는 정책 계약 (D-H1a-12 §5)

`_h1a_policy.py::DECISION_BASIS_POLICY`가 정본이다. 축이 7개에서 5개로
재구성됐고, 옛 표적 축 4개는 `source_meta_reasoning`의 **하위 축**이다.

| 축 | KEPT | REMOVED | 담지자 |
|---|---|---|---|
| `evidence_count` | forbidden | forbidden | `Q7_NON_TARGET_TIEBREAKER` |
| `source_order` | forbidden | forbidden | `Q7_NON_TARGET_TIEBREAKER` |
| `outside_domain_knowledge` | forbidden | forbidden | `DOMAIN_KNOWLEDGE_BOUNDARY` |
| `external_source_retrieval` | forbidden | forbidden | `DOMAIN_KNOWLEDGE_BOUNDARY` |
| **`source_meta_reasoning`** | **forbidden** | **allowed_by_default** | **`Q1_LIVENESS_CLAUSE` / `GLOBAL_DEFAULT_PERMISSION`** |

`source_meta_reasoning`의 하위 축: `source_kind_priority`, `recency`,
`authority`, `liveness`.

**비포섭 명제(Q12=F의 핵심)**: `source_meta_reasoning ⊄ outside_domain_knowledge`
이고 그 역도 성립한다. 둘은 형제 범주다. 이 명제는
`test_domain_knowledge_and_source_meta_are_siblings_not_nested`가 고정한다 —
그것이 깨지면 직전 코호트를 비식별로 만든 포섭이 돌아온 것이다.

---

## 3. 동결되는 공통 프롬프트 (D-H1a-12 §4, 3문장)

세 문장 모두 **양 arm에서 byte-identical**하며, 앞의 두 개는 담지자가 있고
세 번째는 담지자가 아니다(축을 forbidden으로 뒤집지 않으므로
`SCOPE_CONSTRAINTS`에 등록).

동결 바이트는 `h1a_common_policy_block_v2.json`(sha256 고정)에 있다 —
`assert_9`가 렌더 결과를 그 아티팩트와 대조한다.

---

## 4. 동결 게이트 (D-H1a-12 §16, 12조건)

| # | 조건 | 검사 지점 | 상태 |
|---|---|---|---|
| 1 | outside_domain_knowledge / source_meta_reasoning 분리 | 구조 단언 1~8 + 비포섭 테스트 | ✅ 자동 |
| 2 | 공통 Q7 재작성(3문장) | `render_policy_block` + contract 테스트 | ✅ 자동 |
| 3 | defer 규칙 비방향화 | `h1a_prompt_template.md` + contract 테스트 | ✅ 자동 |
| 4 | demand neutralizer 재문안 | `GLOBAL_DEFAULT_PERMISSION_TEXT` + golden artifact | ✅ 자동 |
| 5 | semantic policy assertion | `assert_12`(의미 검사) | ✅ 자동 |
| 6 | golden common-block contract | `assert_9` + golden artifact | ✅ 자동 |
| 7 | assertion 9 음성 테스트 5종 | `test_assert_9_fires_*` | ✅ 자동 |
| 8 | licensed-source-evaluation-path 진리표 | `assert_licensed_path_contrast` | ✅ 자동 |
| 9 | M4 ceiling 복구 | §5 아래 | ✅ 이 문서로 |
| 10 | repaired preregistration 갱신 | 이 문서 | ✅ |
| 11 | 독립 의미 리뷰 재실행 | **기계 검사 불가** | ⬜ |
| 12 | 리뷰어 전원 freeze 승인 | **기계 검사 불가** | ⬜ |

조건 11·12는 코드로 검증할 수 없다. `pass-is-a-conjunction` 규율대로
**검사 불가 조건은 명명하고 담당을 배정한다** —
`_h1a_policy.py::INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`이고
`assert_freezable()`이 그 값이 False인 동안 `FreezeGateBlocked`를 던진다.
리뷰 보고서를 커밋하는 **같은 커밋에서만** True로 바꾼다.

---

## 5. M4 — ceiling 해석 조건 복구 (D-H1a-12 §14)

**왜 복구가 필요한가 (2026-08-05 조사 결과)**: `PREREGISTRATION.md` §11
전체(§11.2a의 Q4=승인 ceiling 해석 조건 포함)가 2026-08-01 Q6=A로
superseded됐고, 그 대체(§11.0 `assert_no_model_facing_type_anchor`)는
**앵커가 payload에 주입되는 것을 구조적으로 막을 뿐, "결과가 null로 보여도
ceiling 때문일 수 있다"는 해석 조건은 어디에도 재등록되지 않았다.** M4의
지적이 정확하다.

**Q4는 여전히 구속력을 가진다.** 따라서 새 설계 판정 없이, 그 승인된 문안을
이 코호트에 맞게 범위만 갱신해 재등록한다. 원문(`PREREGISTRATION.md`
§11.2a의 외부 판정 최종판, verbatim):

> If all four diagnostic cells fall into the same modal behavior category
> (`select_type` or `defer`), the diagnostic does not establish that the anchor
> and prompt surface are free of ceiling effects. In that case, a null main
> result is uninterpretable with respect to anchor or prompt-surface ceiling
> effects.
>
> This rule is not an additional trial, not a post-hoc exclusion, not a new
> blocking rule, and not a new success criterion. It is a pre-freeze
> interpretability condition for reading the diagnostic gate.

**이 코호트에 맞춘 재등록 (범위 갱신, 규범적 내용 불변)**:

> If both arms of this cohort fall into the same modal behavior category
> (`select_type` or `defer`), this cohort does not establish that the prompt
> surface — including the three common sentences frozen in
> `h1a_common_policy_block_v2.json` — is free of ceiling effects. In that
> case, a null main result is uninterpretable with respect to prompt-surface
> ceiling effects, and MUST NOT be reported as `null_effect`.
>
> This rule is not an additional trial, not a post-hoc exclusion, not a new
> blocking rule, and not a new success criterion. It is a pre-freeze
> interpretability condition for reading this cohort's outcome.

**무엇이 갱신됐는가**: Q6=A가 anchor 진단을 은퇴시켰으므로 발동 조건이
"네 진단 셀"에서 **"이 코호트의 두 arm"**으로 바뀌었고, 범위가 anchor를
빼고 **prompt surface**로 좁혀졌다(앵커는 이제 구조적으로 주입되지 않으므로
ceiling 원인이 될 수 없다 — §11.0). 규범적 내용("동일 modal 범주면 null은
해석 불가")은 Q4 승인 문안 그대로다.

**배선**: 이 조건은 결과를 본 뒤 적용되는 해석 규약이므로 구조 검사로
자동화되지 않는다. `_h1a_score.py`가 두 arm의 modal 범주를 계산해 동일하면
보고서에 `prompt_surface_ceiling: uninterpretable`을 강제 기록하도록
채점 단계에서 배선한다(§7의 보고 규약과 함께).

---

## 6. 실행 규약

- 양 arm **전체 재실행**(D-H1a-12 §13 `new_trials: required`). 기존 KEPT
  재사용 금지.
- 코더·fixture 불변. `cohort_id`·출력 파일은 기존 코호트와 분리.
- trial 실행 전 `assert_freezable()` + `assert_licensed_path_contrast(V, H)`가
  통과해야 한다. V·H는 fixture 검토 결과를 명시적으로 넘긴다 — 기본값에
  기대지 않는다.

## 7. 보고 규약

- K=1 상한 유지. 일반 모델 성향으로 일반화하지 않는다.
- 두 arm이 동일 modal 범주면 §5의 ceiling 조건에 따라
  `null_effect`로 보고하지 않는다.
- `licensed_source_evaluation_path`의 항목별 값을 결과와 함께 기록한다 —
  대비가 성립한 근거가 무엇이었는지 사후에 재구성 가능해야 한다.
- 결과를 본 뒤 이 문서의 코딩 규칙이나 N을 바꾸지 않는다.

## 8. 미해결 (이 문서 시점)

**조건 1~10 전부 구현·통과.** 남은 것은 조건 11·12(독립 의미 리뷰 재실행 +
리뷰어 전원 freeze 승인)뿐이고, 그 둘은 기계 검사 불가라
`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False`가 게이트를 계속 막는다.

조건 3·4를 구현하면서 golden artifact를 **한 번 재동결**했다
(`h1a_common_policy_block_v2.json`의 `amendment_history`에 이유와
`at_trials: 0` 기록). `assert_9`가 그 drift를 즉시 잡았고 에러 메시지가
"의도된 변경이면 별도 커밋으로 재동결하고 이유를 밝혀라"라고 지시한 대로
따랐다 — golden contract가 설계대로 작동한 실측이다.

표면이 더 바뀌면 리뷰가 다시 무효가 되므로(Q10 때 실제로 그랬다), 조건
11·12 실행 전까지 프롬프트 표면·정책 계약을 더 건드리지 않는다.

### 8.1 조건 11 첫 시도 — 전송 실패로 미완료 (2026-08-05)

독립 리뷰어 **3명을 근거 축 분할로 실제 실행했다** — (a) 정책 계약과 구조
단언, (b) 렌더된 모델 대면 프롬프트, (c) 사전등록과 freeze 게이트. 세 명 모두
제작 세션의 결론을 고지받지 않았고, "제작자의 테스트를 증거로 받지 말고 직접
재현하라"는 지시를 받았다.

**세 명 전원이 API 세션 사용 한도로 조기 종료됐다**(`You've hit your session
limit · resets 1am (Asia/Seoul)`). 이것은 **전송 실패이지 리뷰 결과가 아니다** —
E2.4가 30 trial 중 22개를 같은 이유로 잃었을 때 적용한 판정과 동일하게, 세션
한도는 데이터가 아니므로 리뷰 결과로 기록하지 않는다.

**따라서 조건 11은 여전히 미충족이다.** 특히 다음을 혼동하지 말 것:

- 리뷰어가 "문제 없음"을 보고한 것이 **아니다.** 아무 보고도 받지 못했다.
- 조기 종료를 근거로 `INDEPENDENT_SEMANTIC_REVIEW_PASSED`를 True로 바꾸는
  것은 **금지**다. 그것이 정확히 `pass-is-a-conjunction`이 막는 실패
  (검사되지 않은 조건을 통과로 집계)다.

재시도 시 위 세 축을 그대로 쓴다 — 축 분할과 지시문은 유효했고 실패 원인은
용량이었다. 한도 리셋 후 재실행할 것.
