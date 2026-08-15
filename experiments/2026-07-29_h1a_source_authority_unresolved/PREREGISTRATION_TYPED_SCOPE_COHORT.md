# H1a 사전등록 — typed-scope 코호트 (D-H1a-12)

- 작성: 2026-08-05 / **갱신: 2026-08-15** — D-H1a-13 Q13/Q13.1/Q13.2 적용
  완료(commit `7624034`/`6b45d27`/`2a7913a`). §5 전체 **WITHDRAWN**(Q13.3이
  옛 ceiling 조건을 폐기, §5a의 qualification gate로 대체 — **미구현**),
  §5b에 L8 신규 등록(Q13.4, 완료). Q13.3(qualification gate 실제 배선)만
  남으면 §16 12조건 전부 충족 → 독립 리뷰 전면 재실행 → trial 착수.
  `freeze_status: FREEZE_BLOCKED` 유지, `repaired_cohort_trials: 0`.
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

## 5. M4 — ceiling 해석 조건 복구 (D-H1a-12 §14) — **§5 전체 WITHDRAWN (D-H1a-13 Q13.3, 2026-08-06)**

> ⚠️ **이 절 전체가 폐기됐다.** 독립 리뷰 20260806(축 c, F6·MAJOR)이 이
> 재등록 자체가 결함임을 발견했다 — ① 승인되지 않은 "MUST NOT be reported
> as null_effect" 문구를 추가했고, ② 발동 조건을 "네 진단 셀"(주 결과
> **밖**의 anchor×arm 대비)에서 "이 코호트의 두 arm"(주 결과 **자체**)으로
> 바꿔, 조건이 자신이 수식하는 것과 동어반복이 됐다 — 독립적인 ceiling
> 정보를 담지 않는다. **D-H1a-13 Q13.3이 명시적으로 "폐기한다"고 판정**:
> `same_modal_behavior_rule: withdrawn`, anchor×arm 네 셀도 부활시키지
> 않는다. 대신 **§5a**(아래)의 qualification gate로 대체한다.
>
> 아래 원문은 **이력 보존**이다. F6이 무엇을 잘못했는지 보여주는 실측
> 증거로 남긴다 — "재등록은 범위만 바꾸는 것 같아도 규범 내용을 조용히
> 바꿀 수 있다"는 교훈 자체가 재사용 가치가 있다(`H1A_PROBLEM_ANALYSIS.md`
> P4 계열).

### 5a. 대체 — Qualification gate (D-H1a-13 Q13.3)

옛 "네 셀 동일 모달 범주" 조건은 주 결과를 재진술할 뿐이었다. 대신
confirmatory cohort와 **분리된** floor/ceiling 검사를 둔다.

**QF-SELECT** — 한 allowed type만 명시적으로 지지되고 반대 근거가 없는
fixture. 기대 행동: `select_type`.

**QF-DEFER** — 두 allowed type이 동등하게 지지되고 허용된 추가
discriminator가 없는 fixture. 기대 행동: `defer`.

```yaml
qualification:
  confirmatory_sample: false
  pooled_with_main_cohort: false
  trials_per_control: 5
  select_control:
    required_rate: 0.80
  defer_control:
    required_rate: 0.80
```

> ⚠️ **2026-08-15 AMENDMENT — QF-DEFER 부분만 아래 §5c로 변경됐다.** 위
> yaml과 "두 control 중 하나라도" 문구는 **원안(2026-08-06) 그대로 이력
> 보존**한다. 실제 gate 동작은 §5c를 따른다: `cohort_freeze`는
> `select_control` 하나에만 의존하고, `defer_control`은 non-blocking
> 진단으로 강등됐다. QF-SELECT의 hard-gate 지위는 이 판정문 그대로
> **불변**이다.

두 control 중 하나라도 기준 미달이면(원안, §5c로 부분 대체됨):

```yaml
cohort_freeze: blocked
result_category: floor_or_ceiling_failure
```

로 처리한다. **`A failed qualification gate must not be reported as
evidence of a null treatment effect.`**(판정문 승인 문구 — 모델 대면
프롬프트가 아니라 이 분석·보고 계약에만 둔다.)

**구현 상태 (2026-08-15 갱신)**: QF-SELECT fixture 확보·동결
(`fixture_qf_select.json`), `_h1a_qualification.py` 스코어러 구현 완료.
QF-DEFER fixture는 §5c의 사유로 **의도적으로 미구성** — "아직 못 만든
미구현"이 아니라 "저장소에 재료가 없음을 전수 확인하고 gate를 그에 맞게
재설계한 것"이다.

### 5c. 2026-08-15 AMENDMENT — QF-DEFER 강등 (non-blocking diagnostic)

**계기**: D-H1a-13 Q13.3의 명령대로 QF-DEFER fixture를 만들려 했으나,
`docs/`, `conceptgate/`, `experiments/`(H1a 자기 폴더 제외) 전체를 인스턴스
결박 + enum 내 타입 단언 기준으로 전수 열거하고 `_h1a_surface.py`의 실제
`_eligibility_profile`로 자격을 걸러본 결과, **같은 `source_kind` 내부에서
서로 다른 type을 진술하는 자격 있는 소스 쌍이 이 저장소에 없다** — 유일한
충돌(칼/철)은 이미 confirmatory cohort의 fixture 그 자체였다
(`correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md`, Q14
전문 및 실측 표 §3.2 참조). 그걸 QF-DEFER로 재사용하면
`pooled_with_main_cohort: false`(Q13.3 원문)를 어기게 된다.

**판정 경로**: 이 강등은 D-H1a-1~13류의 **외부 판정 채널을 거치지 않았다**
— Q14 요청서를 외부 설계 상담에 공유해 받은 분석(1차: Q14=E "material
unavailable" 권고 → 사용자의 두 명확화 질문 답변 이후 2차: QF-DEFER의
실제 역할이 "ceiling diagnostic"이지 "freeze 전제조건"이 아니라는 재분석)
과, 그 결론을 이 실험 자신의 근거 문서에 직접 대조 검증한 결과다. 따라서
`D-H1a-14`처럼 새 판정 번호를 붙이지 않는다 — 그렇게 부르면 실제로 거치지
않은 외부 판정 채널을 거친 것처럼 기록을 왜곡하게 된다.

**근거 (직접 인용 대조 완료)**:

1. `README.md` §2 — H1a의 연구 질문은 순수 서술적이다("계약 서문에서
   liveness 재판정 금지 문장을 제거했을 때, 선택/보류 행동 분포가
   달라지는가?"). 인과 귀속 금지(D-H1a-7), 단일 K=1 fixture 밖 일반화
   금지가 명시돼 있을 뿐, "trial subject가 defer 능력을 입증해야
   KEPT/REMOVED 대비가 증거가 된다"는 요구는 이 정의 어디에도 없다.
2. `DESIGN_DECISION_H1a_residual_prohibition.md` §3의 형식 식별가능성
   정의: `M_allowed = ¬Q1 ∧ ¬Q7`. 이것은 **조작(arm 설계)의 허용 여부에
   관한 명제**이지 trial subject의 select/defer 능력에 관한 명제가
   아니다. QF-SELECT/QF-DEFER는 이 형식 정의 밖에 있다 — Q13.3이 둘을
   대칭 쌍으로 묶은 것은 "defer 능력이 왜 반드시 hard precondition이어야
   하는가"에 대한 별도 논증 없이 이뤄졌다.
3. Qualification gate 자신의 명시된 목적(Q13.3 rationale)은 null/동일
   modal 범주 결과를 "치료 효과 없음"으로 **오독**하는 것을 막는 것이다.
   그 보호는 confirmatory 결과가 실제로 null/ceiling-suspicious일 때만
   load-bearing이다. 뚜렷한 KEPT/REMOVED 대비는 QF-DEFER와 무관하게
   그 자체로 증거력을 갖는다.
4. 사용자가 직접 답한 두 명확화 질문(2026-08-15): "H1a의 치료 효과
   판단이 QF-DEFER를 요구하는가?" → **아니오**. "QF-DEFER 없이도 큰
   KEPT/REMOVED 차이가 H1a 증거로 인정되는가?" → **예**. 이 두 답이
   위 1·2·3의 문서 근거와 일치한다.

**변경 내용**:

```yaml
qualification:
  select_control:
    required_rate: 0.80
    blocking: true          # 변경 없음 — 여전히 hard gate
  defer_control:
    required_rate: 0.80
    blocking: false          # 2026-08-15 AMENDMENT
    on_unavailable: recorded_as_limitation_L9   # freeze를 막지 않음
```

`cohort_freeze`는 `select_control["passes"]` **하나에만** 의존한다.
`defer_control`은 다음 세 상태 중 하나로 기록되지만(`_h1a_qualification.py`
`DEFER_MATERIAL_UNAVAILABLE`/`DEFER_DIAGNOSTIC_PASSED`/
`DEFER_DIAGNOSTIC_FAILED`), 어느 값도 `cohort_freeze`를 바꾸지 않는다.
`material_unavailable`(현재 실제 상태) 또는 `diagnostic_failed`인 경우
결과에 `defer_ceiling_diagnostic_limitation: true`와 L9 보고 문구가
동반된다(§5d).

**변경되지 않은 것 — 명시적으로 litigate하지 않은 것**: QF-SELECT의
hard-gate 지위는 그대로다. "always select" ceiling도 QF-DEFER가 막으려는
것과 대칭적인 spurious-null 실패 모드를 만들 수 있으므로 QF-SELECT도
같은 논리로 non-blocking화해야 하는가는 **별도의 열린 질문**이며, 이
문서는 그 질문을 **결정하지 않고 다음 항에 남긴다** — 요청받지 않은
범위 확장은 이 저장소가 경계하는 바로 그 실패 모드다.

### 5d. 열린 질문 (결정되지 않음)

**Q15 (가칭, 아직 상신 안 됨)**: QF-SELECT도 §5c와 같은 논리로
non-blocking으로 강등해야 하는가? — 아직 아무도 묻지 않았다. §5c는
QF-DEFER에 대해서만 litigate됐다. 다음 세션이 이 질문을 다룰 때는 새
DESIGN_REQUEST로 상신하거나, 최소한 이 문서에 "결정 보류" 상태로 명시적
등록부터 할 것.

### 5e. L9 등록

```text
L9 — QF-DEFER ceiling diagnostic unavailable

No same-source_kind conflicting-type material for QF-DEFER exists in this
repository (exhaustive eligibility-aware enumeration, 2026-08-15;
correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md sec 3).
The QF-DEFER control is therefore recorded as material_unavailable and does
not gate cohort_freeze (sec 5c amendment).

Accordingly, a null or same-modal-category confirmatory result cannot be
ruled out as a defer-side floor/ceiling artifact via this gate. A clear
KEPT/REMOVED contrast is unaffected by this limitation and remains
evidential per README.md sec 2.
```

**보고 제한**: "QF-SELECT passed, so the instrument is free of select/defer
ceiling effects"는 금지 — QF-SELECT는 select 방향만 검사한다. "a null main
result rules out a defer-side ceiling artifact"도 금지. 뚜렷한 KEPT/REMOVED
대비를 보고하는 것은 L9와 무관하게 허용된다.

**L1~L4·L8과의 관계**: L9는 이들 중 어느 것도 포섭하지 않고 포섭되지도
않는다 — 서로 다른 축(defer 방향 진단 능력)의 선언적 한계다.

### 5b. L8 등록 (D-H1a-13 Q13.4)

fixture에 날짜·경로·커밋·권위 등급을 추가하지 않는다. Q1의 동결 바이트도
수정하지 않는다. 대신 한계를 등록한다(판정문 §7 원문 그대로):

```text
L8 — Partial observability of the named source-evaluation axes

The frozen Q1 clause names source priority, recency, authority, and liveness.
In the repaired fixture, source_kind is the only explicit model-visible source
attribute. Liveness may be inferred from the doc/code distinction only through
source evaluation; recency and authority are not independently instantiated
as payload fields.

Accordingly, the repaired cohort estimates the effect of removing the frozen
Q1 prohibition surface in this fixture. It does not identify separate effects
for recency, authority, liveness, and source-kind priority.
```

**보고 제한**: "removing the frozen source-evaluation prohibition changed or
did not change behavior in this fixture"는 허용. "recency permission had no
effect" / "authority permission had no effect" / "all four source axes were
behaviorally tested"는 금지.

**L1~L4와의 관계**: L8은 이 코호트에도 승계된다 — L1·L2·L3(Q9=A)·L4(Q10.3)와
같은 자리, 같은 급의 선언적 한계다. `L3_subsumes_L8: false`,
`L4_subsumes_L8: false` — 넷 다 서로 다른 축의 한계를 진술하며 어느 것도
다른 것을 포섭하지 않는다.

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
- **(D-H1a-13 Q13.3로 갱신)** qualification gate(§5a)가 통과한 뒤에만
  본 코호트 결과를 해석한다. gate 미달이면
  `result_category: floor_or_ceiling_failure`로 보고하고 **`null_effect`로
  보고하지 않는다.** 두 arm이 동일 modal 범주라는 사실 자체는(옛 §5, 이제
  withdrawn) 더 이상 독자적인 해석 근거가 아니다 — qualification gate가
  그 역할을 대신한다.
- **L8(§5b)에 명시된 보고 제한을 지킨다** — 표적 네 축 중 `source_kind`만
  독립 관측되므로, recency·authority·liveness 각각에 대해 개별 효과를
  주장하지 않는다.
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

### 8.2 조건 11 재실행 결과 — FREEZE_BLOCKED (2026-08-06)

한도 리셋 후 세 축을 그대로 재실행했다. **렌더된 프롬프트 축이
`FREEZE_BLOCKED`를 냈다** — 전문은
`../../docs/feedback/h1a_typed_scope_review_20260806.md`.

**BLOCKER: §4의 세 번째 문장이 REMOVED arm에서 dangling reference다.**
"Source evaluation is governed by the arm-specific source-evaluation clause."
인데 REMOVED에는 그 절이 없다(Q1은 KEPT 전용). 제작 세션이 실측 확인:

```
PROHIBITION_KEPT:    Q1절=True   "arm-specific...clause" 참조=True
PROHIBITION_REMOVED: Q1절=False  "arm-specific...clause" 참조=True
```

이 문장은 §4가 의존하는 기제를 스스로 무너뜨린다 — §4는 REMOVED가 작동하는
이유를 "Q1이 없으므로 공통 기본허용 규칙이 적용된다"로 설명하는데, 이 문장이
그 basis에 대해 **더 구체적인** 지배자를 지목하므로 specific-beats-general
읽기에서 기본허용이 적용되지 않는다.

**이 문장은 판정문 §4(line 189-191)가 verbatim으로 처방한 것이다.** 따라서
운영 세션이 고칠 수 없다 — §4 문구 변경은 설계 판정이다. MAJOR 1·2(`source
order`가 표적으로 읽힘, Evidence-reading rule + §7이 결합해 source 속성을
warrant에서 배제)도 공통 템플릿 문장이라 같은 성격이다.

**조치**: **D-H1a-13 상신 필요.** 그때까지 조건 11·12 미충족,
`INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지, trial 0건 유지.

이것이 D-H1a-11에서 이미 한 번 나온 "이식된 절이 선행사를 잃는다" 패턴의
재발이며(`evidence-to-knowledge-promoter` 2026-08-01 로그 결함 1번), 이번엔
판정문이 처방한 문장 자체가 그 결함을 갖고 있다는 점이 다르다.
