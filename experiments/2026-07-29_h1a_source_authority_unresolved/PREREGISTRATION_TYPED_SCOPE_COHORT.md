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
| 11 | 독립 의미 리뷰 재실행 | **기계 검사 불가** | ✅ 2026-08-16 (§8.3) |
| 12 | 리뷰어 전원 freeze 승인 | **기계 검사 불가** | ✅ 2026-08-16 (§8.3) |

조건 11·12는 코드로 검증할 수 없다. `pass-is-a-conjunction` 규율대로
**검사 불가 조건은 명명하고 담당을 배정한다** —
`_h1a_policy.py::INDEPENDENT_SEMANTIC_REVIEW_PASSED`이고
`assert_freezable()`이 그 값이 False인 동안 `FreezeGateBlocked`를 던진다.
리뷰 보고서를 커밋하는 **같은 커밋에서만** True로 바꾼다.

**2026-08-16 현재 `True`** — 그 조건은 §8.3에 기록됐다. 플래그를 지키는 규율은
사라지지 않았고 형태가 바뀌었다:
`test_the_review_flag_is_only_true_alongside_a_recorded_passing_review`가
플래그를 커밋된 보고서 파일에 결박하므로, 보고서 없이 True인 상태는 테스트가
거부한다.

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

> ⚠️ **아래 "두 control 중 하나라도 → cohort_freeze: blocked" 규칙은
> D-H1a-14/15(2026-08-16 수령)로 철회됐다.** 현행 규범은 **§5f**다.
> 이 절의 나머지(독립 control, 별도 trial, 비풀링, floor/ceiling 진단)는
> **그대로 유지**된다 — 판정문이 명시적으로 보존을 지시했다.
>
> 이력: 2026-08-15에 운영 세션이 **판정 없이** QF-DEFER만 강등했다가
> 적대 검토에서 철회했고(§5c), 그 뒤 재상신해 받은 것이 D-H1a-14/15다.
> 판정은 더 나아가 **두 control 모두** non-blocking으로 하고 freeze 권한
> 자체를 식별 계약으로 분리했다. **결론이 수렴했다고 절차가 정당화되지는
> 않는다** — §5c는 그 구분을 위해 남긴다.

두 control 중 하나라도 기준 미달이면(**철회됨 — §5f 참조**):

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

**QF-SELECT 5-trial 실행 완료 (2026-08-15)**: `_h1a_qualification_run.py`
신설(fixture→prompt 렌더 + manifest 동결/drift 검사 + F9식 덮어쓰기 거부를
갖춘 실행·영속 계층 — `_h1a_qualification.py` 자신은 여전히 fixture 없이도
테스트 가능한 순수 스코어러로 남긴다). `h1a-decider` trial subject로 5회
독립 실행, **5/5 `select_type`/`structural_composition`**(만장일치,
rate=1.0, `passes: true`). 산출물: `h1a_qualification_manifest.json`
(렌더된 prompt의 sha256 동결), `h1a_qualification_raw.json`(원시 5출력),
`h1a_qualification_score.json`. Arm 선택(`PROHIBITION_REMOVED`)은
D-H1a-13이 명시하지 않은 운영상 결정이며 근거는
`_h1a_qualification_run.py` 모듈 docstring에 기록.

**현재 진단 상태 (D-H1a-14/15 적용 후)**: QF-SELECT `passed`(5/5),
QF-DEFER `material_unavailable`. `cohort_freeze`는 이 모듈이 판정하지
않는다 — `{determined_by: identification_contract}`. QF-DEFER 미시행은
**L9로 등록**(§5e)되며 코호트를 막지 않는다. 기록은 `material_unavailable`과
`failed`를 구분해 유지한다(Q14.2) — 시행되지 않은 진단을 피험자가 실패한
것처럼 기록하지 않기 위해서다.

이력: 2026-08-15 score 파일은 무판정 강등 하의 `allowed`를(커밋 `3916ac2`),
철회 후에는 `blocked`를 기록했다. 원시 5출력(`h1a_qualification_raw.json`)은
그 사이 **한 번도 바뀌지 않았다** — 바뀐 것은 채점·해석 규칙뿐이다.
상세는 `OPERATIONS_LOG.md` §8·§9·§10.

### 5c. 2026-08-15 AMENDMENT — QF-DEFER 강등 — **철회됨 (2026-08-16)**

> ⚠️ **이 절은 채택되지 않았다. 규범적 효력 없음 — 이력 보존이다.**
> 아래 원문은 삭제하지 않고 남긴다. §5(M4)를 F6 증거로 보존한 것과 같은
> 이유이며, 이 amendment는 **§5가 기록한 그 실패 모드의 재발 사례**라
> 보존 가치가 더 크다.
>
> **철회 사유 (적대 검토 4축 + lead 재실측,
> `docs/feedback/h1a_qf_defer_amendment_review_20260816.md`, blocker 4건)**:
>
> 1. **자기 요청서가 이미 부정하고 있었다.** Q14 요청서 §4 선택지 D —
>    "QF-DEFER를 보류하고 QF-SELECT만으로 gate를 부분 운영" — 에 요청서
>    자신이 **"Q13.3의 '둘 다 필수' 요구를 완화 — 새 판정 필요"**라고
>    주석했다. 실제로 구현된 것이 바로 그 선택지 D이고, 새 판정 없이
>    실행됐다.
> 2. **자기가 명시한 규율을 자기에게만 적용하지 않았다.** 아래 §5c 말미가
>    "요청받지 않은 범위 확장은 이 저장소가 경계하는 바로 그 실패 모드다"라며
>    Q15를 미결로 남기는데, §5c 자신이 Q14(재료를 무엇으로 할 것인가)에
>    대한 답이 아니라 **QF-DEFER의 지위 자체를 바꾼 범위 확장**이다.
> 3. **근거가 non-sequitur다.** `M_allowed = ¬Q1 ∧ ¬Q7`가 QF-DEFER를
>    언급하지 않는 것은 참이지만, Q13.3이 QF-DEFER를 `M_allowed`에서
>    연역한 적이 없다(D-H1a-10 작성 시점에 QF-* 는 존재하지도 않았다).
>    쟁점이 아니었던 것의 침묵을 근거로 삼았다. Q13.3의 목적은 식별가능성이
>    아니라 **null 결과 오독 방지**다.
> 4. **구조적 회귀다.** Q13.3의 존재 이유는 F6이 *해석 조건*을 불충분하다고
>    판정해 *하드 게이트*로 교체한 것이다. QF-DEFER를 L9 보고 문구로
>    강등한 것은 그 절반을 **다시 해석 조건으로** 되돌린 것이고, 그것도
>    운영 세션의 자기 재등록으로 — F6이 지적한 구조와 동형이다.
>
> 덧붙여 아래 근거 3번이 "그 보호는 결과가 실제로 null일 때만
> load-bearing"이라 **자인**해놓고, **trial 0건** 시점에 결과가 null일지
> 모르는 상태에서 사전에 무조건 껐다.
>
> **현행 규범은 §5a의 원안**(둘 다 통과 필수)이다. Q14는 Q15와 함께
> 외부 판정 채널로 **재상신**한다(`correspondence/DESIGN_REQUEST_H1a_qualification_gate_scope.md`).

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

### 5d. Q14·Q15 재상신 (2026-08-16) — **판정 도착**

Q14와 Q15를 **하나의 요청서에** 상신했다
(`correspondence/DESIGN_REQUEST_H1a_qualification_gate_scope.md`). 분리해서
묻는 것 자체가 적대 검토(축 C)가 지적한 결함이었기 때문이다 — 강등 근거가
두 control에 대칭 적용되므로 한쪽만 묻고 한쪽만 바꾸면 그 비대칭은 원리가
아니라 "무엇을 물었나"의 산물이 된다.

**판정 수령: `DESIGN_DECISION_H1a_qualification_gate_scope.md`(D-H1a-14/15).**
Q14=E(gate 재설계), Q15=G(둘 다 non-blocking). 내용은 §5f.

### 5e. L9 등록 (D-H1a-14/15)

> 2026-08-15에 L9를 등록했다가 철회한 적이 있다. 그때는 **무판정 강등의
> 부산물**이었고, 재료 부재를 "한계"로 등록하면 미해소 blocker를 잘못
> 표기하는 것이었다. 지금은 다르다 — 판정문이 "그 방향의 capability는
> 독립적으로 진단되지 않음을 **한계로 등록**한다"고 직접 명령했고,
> 동시에 그것이 blocker가 아님을 확정했다. 같은 번호, 다른 근거.

```text
L9 — Ceiling-direction capability not independently diagnosed

The QF-DEFER capability diagnostic was not administered: no repo-grounded,
same-source_kind conflicting-type material for it exists in this repository
(exhaustive eligibility-aware enumeration, 2026-08-15), and D-H1a-14/15 Q14.1
forbids manufacturing one by reusing the confirmatory 칼/철 fixture.

Accordingly the trial subject's deferral capability is recorded as UNKNOWN,
not as absent or failed. Q14.2: material_unavailable licenses no negative
conclusion about the subject. Per Q15=G this does not block the cohort;
freeze is determined by the identification contract alone.

Reporting consequence: a null or small confirmatory effect must not be
reported as ruling out an always-select (ceiling) saturation explanation.
A non-null effect is not affected by this limitation. Where the main cohort
itself shows both select_type and defer occurring across arms, that data
independently bears on the saturation question.
```

**보고 제한**: "the instrument was shown to be free of ceiling effects" 금지.
"defer capability was tested and failed" **금지**(시행되지 않았다).
"QF-SELECT passed, therefore both directions are sound" 금지 — QF-SELECT는
floor 방향만 진단한다.

**L1~L4·L8과의 관계**: 서로 다른 축이며 어느 것도 다른 것을 포섭하지 않는다.

### 5f. 현행 규범 — capability diagnostics (D-H1a-14/15)

**Q14=E / Q15=G.** qualification control은 **freeze 전제조건이 아니다.**
판정문의 근거: `IndependentDiagnostic ⇏ HardFreezePrerequisite` —
"독립적으로 측정한다"와 "통과 못 하면 본 실험을 실행할 수 없다"는 서로 다른
설계 결정이고, 식별가능성 C에 대해 `C → (S ∧ D)`는 tautology가 아니다.
또 두 control은 대칭이다(`Role(QF_SELECT) = Role(QF_DEFER)`) — 실패가 같은
포화 위험의 좌우 대칭이기 때문이다.

```yaml
capability_diagnostics:                 # Q13.3에서 보존된 부분
  independent_fixtures: true
  separate_trials: true
  pooled_with_main_cohort: false
  trials_per_control: 5
  required_rate: 0.80
  controls_are_freeze_prerequisites: false   # ← 철회된 부분

  qf_select: { probes: floor_saturation }
  qf_defer:  { probes: ceiling_saturation }

  status_taxonomy: [passed, failed, material_unavailable]
  # material_unavailable ≠ failed. 같은 category를 공유하지 않는다(Q14.2).

qualification_surface:                  # Q14.3
  name: QUALIFICATION_COMMON
  treatment_arm: none
  policy_role: treatment_invariant
  byte_source: COMMON_WITHOUT_Q1
  must_equal_current_removed_bytes: true

confirmatory_fixture_reused_as_capability_control: false   # Q14.1

freeze:
  determined_by: identification_contract
  capability_diagnostics_control_freeze: false
```

**해석 규약**:

| 진단 결과 | 결과 해석 |
|---|---|
| 둘 다 통과 | floor·ceiling 대안 설명이 모두 독립적으로 약화됨 |
| 하나 실패 | 코호트 실행 가능. **null/작은 효과**를 그 방향의 포화로 설명하는 것을 배제하지 못한다. **비-null 효과는 무효화되지 않는다** |
| 하나 미시행 | 코호트 실행 가능. 그 방향은 독립 진단되지 않음(unknown). **실패로 취급 금지** |

**Q14.3 재분류 — 기존 5건 재실행 불필요**: 판정문은 byte identity 검증을
조건으로 재사용을 허가했다. 실측 확인: `render_qualification_surface()`가
`render_arm(..., "PROHIBITION_REMOVED")`와 **바이트 동일**이고, 기존 5건이
실제로 받은 `rendered_prompt_sha256`(`fd793fc7…`)과 일치한다. 이 조건은
프로즈가 아니라 코드로 고정됐다
(`_h1a_qualification_run._assert_recorded_trials_match_the_qualification_surface`) —
한 바이트라도 달라지면 기존 5건은 historical diagnostic이 되고 재실행이
필요하므로, 사람이 알아채는 데 맡길 수 없다.

```yaml
surface:
  old_label: PROHIBITION_REMOVED
  reclassified_as: QUALIFICATION_COMMON
  byte_identity_verified: true
```

### 5h. D-H1a-17 — 검증 의무의 load-bearing 판별 (2026-08-17)

D-H1a-16(Q16=A, 정본 확장)을 **무효화하지 않고 적용 범위를 한정**한다.

```text
TargetCritical ⇒ CanonicalExpectedState        (D-H1a-16)
        ↓ 좁힘
CanonicalAuditCritical ⇒ CanonicalExpectedState (D-H1a-17)
```

**판별 기준(반사실)**: 그 검사를 빼면 잘못된 인과 결론이 통과하는가?
통과하면 load-bearing, 다른 독립 경로가 이미 같은 의미를 충분한 assurance로
확정하면 audit automation이다.

**분류**: 세 의미 명제는 전부 `causal_semantic_critical: true`이되
`canonical_audit_critical: false`다. **두 번째가 false인 이유는
canonicalization이 쓸모없어서가 아니라 독립 경로가 이미 존재하기 때문이며,
그 경로가 사라지면 다시 true가 된다.**

```yaml
semantic_status:
  conflict_to_defer_mapping:
    resolved: true
    certification_path: existing_guard_plus_independent_review
  recorded_field_access:
    resolved: true
    certification_path: rendered_surface_plus_independent_review
  default_permission_applicability:
    resolved: true
    certification_path: policy_invariants_plus_golden_contract_plus_review

canonical_automation:
  status: deferred
  freeze_blocker: false
```

**분류를 말로 받지 않고 실측했다**(`test_h1a_criticality.py`). 반사실을
실행하는 과정에서 **첫 측정이 반증처럼 보였다가 위협 모델이 다름을 발견**한
것이 이 검증의 실질이다:

| 실패 모드 | compiler 없는 독립 경로 | 실측 |
|---|---|---|
| 정본/렌더러 드리프트(현실적) | `assert_9` golden contract | **탐지 O** |
| 렌더 후 문자열 변조 | 코호트 manifest `rendered_prompt_sha256` | **탐지 O** |
| (참고) 렌더 후 변조를 `assert_9`로 | 모듈에서 재렌더하므로 구조적으로 못 봄 | 탐지 X |

즉 두 실패 모드 각각에 **compiler와 무관한 경로**가 있다. semantic compiler도
둘 다 잡지만, 그것이 **유일 경로가 아니라는 것**이 audit_only 분류의 내용이다.

**부수 실측 — 판정문 논거보다 강한 사실**: `assert_freezable`이 정본 DSL을
직접 읽어 `removed_target_state_is_allowed_by_default: true`와
`removed_target_state_is_not_unspecified: true`를 산출한다. 즉 "침묵이 아니라
허가"라는 바로 그 명제가 semantic compiler 없이도 **기계 검증**된다 —
판정문이 대비한 "기계 vs 리뷰어"보다 유리한 상태다.

### 5i. `criticality` 이중 분류 (D-H1a-17)

`target-critical` 단일 enum이 두 개의 다른 주장을 나르고 있던 것이 구조적
문제였다. `_h1a_semantic_compiler.py`에서 분리:

- `CAUSAL_SEMANTIC_CRITICAL` — 이 명제가 거짓이면 인과 식별이 깨진다(6개)
- `CANONICAL_AUDIT_CRITICAL` — 정본→compiler 경로로도 인증해야 한다(**현재 0개**)
- `CERTIFICATION_PATH` — 각 family가 **어느 경로로** 확정됐는지 기록.
  경로를 적지 않은 `audit_only` 분류는 증거가 아니라 가정이므로 테스트가 강제한다

`TARGET_CRITICAL`은 `CAUSAL_SEMANTIC_CRITICAL`의 별칭으로 남겨 기존 호출자의
의미를 보존한다.

### 5g. 거버넌스 규칙 (D-H1a-14/15가 부과)

> **기존 판정에서 `freeze_blocker`인 조건을 `diagnostic`으로 낮추거나 그
> 반대로 승격하는 변경은 구현 변경이 아니라 estimand/governance 변경으로
> 취급하고, 외부 판정 전에는 실행하지 않는다.**

2026-08-15 위반에 대해 판정문이 부과한 유일한 새 제약이다. 판정문은 그
집행이 "결론의 옳고 그름과 별개로 절차 위반"이라는 기록을 **유지하라**고
명시했다 — 이 판정이 같은 방향으로 결론났다는 사실이 그때의 절차를
정당화하지 않는다.

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
- > ⚠️ **아래 규칙은 D-H1a-14/15(2026-08-16 수령)로 철회됐다** — §5a 본문과
  > 같은 이유다. 이 절이 갱신되지 않은 채 남아 있던 것을 2026-08-18에
  > 발견했다. **현행 규범은 §5f의 해석 규약 표다.** 이 문구는 원문 보존
  > 목적으로만 남긴다.
  >
  > ~~**(D-H1a-13 Q13.3로 갱신)** qualification gate(§5a)가 통과한 뒤에만
  > 본 코호트 결과를 해석한다. gate 미달이면
  > `result_category: floor_or_ceiling_failure`로 보고하고 **`null_effect`로
  > 보고하지 않는다.**~~ 두 arm이 동일 modal 범주라는 사실 자체는(옛 §5, 이제
  > withdrawn) 더 이상 독자적인 해석 근거가 아니다 — qualification gate가
  > 그 역할을 대신한다.
  >
  > **철회 이유**: `floor_or_ceiling_failure`는 2026-08-16에
  > `_h1a_qualification.py`에서 은퇴한 상수다(`# FLOOR_OR_CEILING_FAILURE
  > retired 2026-08-16`). D-H1a-14/15가 qualification control을 freeze
  > 전제조건에서 **비차단 capability diagnostic**으로 재분류했으므로, gate
  > 미달은 더 이상 결과 전체를 한 범주로 몰아넣는 사건이 아니다 — §5f 표대로
  > **방향별 해석 제한**이 된다.
  >
  > **이 정정의 시점이 중요하다**: 이 절 마지막 줄이 "결과를 본 뒤 이 문서의
  > 코딩 규칙이나 N을 바꾸지 않는다"고 못박고 있다. 40 trial 실행 **전**,
  > 관측을 한 건도 읽지 않은 상태에서 정정했다(`trials_typed_scope.json`
  > 부재로 확인 가능). 실행 후에 발견했다면 고칠 수 없는 항목이었다.

- **(D-H1a-14/15 현행)** capability diagnostics(§5f)는 freeze 전제조건이
  아니므로 통과 여부가 코호트 해석의 **전제조건이 아니다**. 진단 결과는 §5f
  해석 규약 표대로 **해당 방향의 대안 설명 배제 가능성만** 좌우한다:

  | 진단 결과 | 이 코호트 결과에 붙는 제한 |
  |---|---|
  | 둘 다 통과 | floor·ceiling 대안 설명 모두 독립적으로 약화됨 |
  | 하나 실패 | null/작은 효과를 그 방향 포화로 설명하는 것을 배제하지 못함. **비-null 효과는 무효화되지 않음** |
  | 하나 미시행 | 그 방향은 `unknown`. **실패로 취급 금지** |

  현재 진단 상태(§5a 실측): QF-SELECT `passed`(5/5), QF-DEFER
  `material_unavailable`. 즉 **ceiling 방향은 `unknown`**이므로, 결과가 null에
  가깝게 나오면 "ceiling 포화가 아니다"라고 주장할 수 없고, 비-null로 나오면
  그 사실이 결과를 무효화하지 않는다.

- 어떤 진단 결과에서도 다음 문장은 유지된다 —
  `_h1a_qualification.APPROVED_NULL_EFFECT_SENTENCE`에 상수로 고정된 승인
  문구이며, 재작성 금지(F6):
  > A failed qualification gate must not be reported as evidence of a null
  > treatment effect.
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

### 8.3 조건 11·12 충족 — 게이트 개방 (2026-08-17)

§8.1(전송 실패)·§8.2(FREEZE_BLOCKED)로 끝나 있던 이력의 결말이다. 위 두 절만
읽으면 조건 11·12가 여전히 미충족이고 trial이 0건이어야 한다고 결론하게 되므로
여기에 기록한다.

| 조건 | 상태 | 근거 |
|---|---|---|
| 11 (독립 의미 리뷰) | **충족** | `docs/feedback/h1a_independent_semantic_review_20260816.md` |
| 12 (리뷰어 자격) | **충족** | blinded mutation pack(`_h1a_mutation_pack.py`) 통과 리뷰어만 판정 계수 |

`_h1a_policy.INDEPENDENT_SEMANTIC_REVIEW_PASSED = True`(2026-08-16 커밋
`73b6682`). **플래그의 보호 장치는 삭제된 것이 아니라 이전됐다** —
`test_the_review_flag_is_only_true_alongside_a_recorded_passing_review`가
플래그를 커밋된 보고서 파일에 결박한다. 예전의 "함부로 뒤집지 마라" 테스트는
정당한 전환을 견딜 수 없는 형태였고, 그것을 대체한 것이다.

§8.2가 요구한 D-H1a-13 상신은 완료됐고, 그 뒤 D-H1a-14/15(qualification gate
범위), D-H1a-16(정본 확장), D-H1a-17(D-H1a-16 범위 한정)까지 수령·적용됐다.

**동결 완료**: `cohort_prompts_typed_scope.json`(40 trial, arm당 20),
sha256 `9c84ef93…`. 동결 인증 증명은
`cohort_prompts_typed_scope_freeze_proof.json`에 별도 기록(§7의
`licensed_source_evaluation_path` 항목별 요구를 충족).

**남은 것은 실행뿐이며, 실행은 사용자 승인 사항이다.**

### 8.4 이 문서 자체의 드리프트 (2026-08-18 발견)

동결 게이트가 열린 뒤 실행 직전에 이 문서를 재대조해 찾은 것이다. 셋 다 **관측을
한 건도 읽기 전에** 처리했다 — §7 마지막 줄이 결과를 본 뒤의 규칙 변경을 금지하므로
실행 후에는 고칠 수 없는 항목이었다.

| # | 결함 | 처리 |
|---|---|---|
| 1 | §7이 은퇴한 `floor_or_ceiling_failure`로 보고하라고 지시 | §7에 철회 표기 + D-H1a-14/15 현행 규범 표로 대체 |
| 2 | §8이 2026-08-06 FREEZE_BLOCKED에서 끝나 게이트가 아직 막힌 것처럼 읽힘 | §8.3 추가 |
| 3 | §7이 요구하는 `licensed_source_evaluation_path`가 동결 manifest에 없음 — `build_cohort()`이 `assert_freezable()`의 반환값을 버렸다 | 증명 sidecar 신설 + 채점 경로에 존재·결박 검사 배선 |

3번이 이 중 유일한 코드 결함이고, 형태가 반복이다: **정책 층이 존재하지만 실행
경로에 없었다**(2026-08-06 blocker와 동형). 이번엔 "검사는 실행됐지만 그 결과가
디스크에 도달하지 않았다"는 변종이므로, 문구가 아니라 코드로 고정했다 —
`_h1a_score._assert_the_freeze_proof_is_recorded`가 증명 부재와 manifest 불일치
양쪽에서 채점을 거부한다.


---

## 9. 결과 (2026-08-22 실행) — §7 규약에 따른 보고

§6·§7이 요구한 형식으로 보고한다. **§7 마지막 줄대로, 이 결과를 본 뒤 이
문서의 코딩 규칙이나 N을 바꾸지 않았다** — 규칙 정정은 전부 §8.4에 기록된
2026-08-18, 관측 0건 시점에 끝났다(`trials_typed_scope.json` 부재로 확인
가능했던 시점).

### 9.1 관측

| arm | selection | deferral | invalid | n |
|---|---|---|---|---|
| PROHIBITION_KEPT | 0 | 20 | 0 | 20 |
| PROHIBITION_REMOVED | **2** | 18 | 0 | 20 |

40/40 기록, 전송 실패 0건, 완주 replicate 20/20, Stage A invalid-rate 게이트
양 arm 통과(각 0.00).

**D-H1a-18 Q18.3이 함께 제시하라고 지정한 항목** (descriptive count/proportion
으로만 보고하며, p-value를 primary verdict로 승격시키지 않는다):

```text
2/20 = 10%      (PROHIBITION_REMOVED)
0/20 = 0%       (PROHIBITION_KEPT)
N fixed ex ante
no post-result extension
```

> 표본이 작아 arm 간 probability difference에 대한 정밀한 추론을 지원하지
> 않는다. 양측 Fisher exact comparison은 p≈0.487이었다.

**D-H1a-18 Q18.1=(b)가 지정한 주 보고 문구**:

> 이 코호트에서 `PROHIBITION_REMOVED` arm에서만 `select_type`이 관측되었다
> (2/20 vs 0/20).

확장형:

> 관측 빈도는 REMOVED에서 2/20, KEPT에서 0/20이었다. 이 고정 fixture의 현
> 코호트에서는 REMOVED에서만 selection이 발생했지만, 표본이 작고 QF-DEFER가
> 미시행이므로 이를 안정적인 분포 차이나 Q1 제거의 인과 효과로 해석하지 않는다.

⚠️ **"분포가 달라졌다"를 주 보고 문구로 쓰지 않는다** — 판정문이 그 문장이
population-level inference로 읽히기 쉽다는 이유로 (a)를 기각했다. 연구 질문이
"달라지는가"로 쓰여 있다는 사실이 그 문형의 사용을 허가하지 않는다.

### 9.2 §7이 요구한 `licensed_source_evaluation_path` 항목별 값

"대비가 성립한 근거가 무엇이었는지 사후에 재구성 가능해야 한다"에 대한 기록.
`h1a_cohort_score_typed_scope.json`과 `cohort_prompts_typed_scope_freeze_proof.json`
양쪽에 있고, 후자는 `cohort_manifest_sha256`로 동결 바이트에 결박돼 있다.

| 항목 | PROHIBITION_KEPT | PROHIBITION_REMOVED |
|---|---|---|
| `source_attributes_visible` | true | true |
| `source_meta_allowed` | **false** | **true** |
| `domain_ban_subsumes_source_meta` | false | false |
| `hard_defer_mapping` | false | false |
| `residual_prohibition` | false | false |
| **`licensed_path`** | **false** | **true** |

정확히 한 arm만 경로가 열려 있다. 둘 다 또는 어느 쪽도 아니었다면 D-H1a-12
§10의 대체 술어가 성립하지 않으므로 동결이 인증되지 말았어야 한다.

### 9.3 §5f 해석 규약 적용 — 이 결과에 붙는 제한

진단 상태: QF-SELECT `passed`(5/5), QF-DEFER **`material_unavailable`**.
§5f 표의 "하나 미시행" 행에 해당한다.

- **ceiling 방향은 `unknown`이다.** 따라서 이 near-null 결과를 **"ceiling
  포화가 아니다"로 보고하지 않는다.** 패킷 자체가 금지 여부와 무관하게
  deferral을 유도하는 가능성은 측정된 어떤 것으로도 배제되지 않았다.
- `material_unavailable`은 `failed`가 **아니다**(Q14.2). 진단을 실패로
  서술하지 않으며, 실패 게이트에 관한 승인 문구
  (`APPROVED_NULL_EFFECT_SENTENCE`)는 이 경우에 적용되지 않는다 — 적용되는
  것은 "그 방향은 독립 진단되지 않음(unknown), **실패로 취급 금지**"다.
- floor 방향은 QF-SELECT 통과로 독립 진단됐으므로, "REMOVED가 select를 전혀
  못 하는 주체였다"는 대안 설명은 약화된다.

### 9.4 K=1·축별 보고 제한 (§7)

- 서술적·패킷 조건부만. 이 하나의 fixture(칼/철), 이 동결 프롬프트 쌍, 이
  trial subject, 이 전송에서의 분포다. §0이 다른 패킷·일반 source-authority
  상황·어느 type이 옳다는 주장으로의 일반화를 금지한다.
- **D-H1a-7이 인과 귀속을 금지한다.** 0→2를 "금지 절 제거가 selection을
  야기했다"로 쓰지 않는다.
- **L8**: 표적 네 축 중 `source_kind`만 독립 관측됐으므로 recency·authority·
  liveness 각각에 대한 개별 효과를 주장하지 않는다.
- **L3**: code측 증거의 반박·일반화 절(내용 비대칭, Q9=A)이 주는 수사적
  우위를 code 권위의 증거로 읽지 않는다.

### 9.5 보존 코호트와의 대비 — 무엇을 말하고 무엇을 말하지 않는가

| 코호트 | KEPT selection | REMOVED selection |
|---|---|---|
| `h1a-original-20260803` | 0 / 20 | 0 / 20 |
| `h1a-typed-scope-20260817` | 0 / 20 | **2 / 20** |

> ⚠️ **2026-08-22 정정 (D-H1a-18 Q18.2=c 적용).** 아래 취소선 문장은 이 판정
> 수령 **전에** 쓴 것이고, 판정의 조건 3(`0→2가 redesign 때문에 발생했다고 쓰지
> 않는다`)과 `causal_redesign_attribution: forbidden`에 걸린다. "그 진단이
> 옳았다는 방향의 관측"은 표현이 약할 뿐 **변화를 재설계의 증거로 쓰는 것**이므로
> 같은 금지 대상이다. 원문은 무엇이 철회됐는지 남기기 위해 보존한다.
>
> ~~2026-08-03 세션은 0/40이라는 바닥값을 "조작 무효"로 읽지 않고, Q7=E의
> tie-breaker 금지가 양 arm에 남아 있음을 찾아 Q10을 상신했다. typed-scope
> 재설계(D-H1a-12 Q12=F)가 겨눈 것이 그 절이며, REMOVED가 0에서 2로 움직인 것은
> 그 진단이 옳았다는 방향의 관측이다.~~

**허용 표현 — D-H1a-18이 직접 제시한 문구를 그대로 쓴다** (운영 세션이 다시
저작하지 않는다):

> "이전 비식별 표면에서는 양 arm 모두 0/20이었고, 수선된 별도 표면에서는 KEPT 0/20, REMOVED 2/20이 관측됐다. 두 코호트는 병합하지 않으며, 표면 차이가 복수이므로 이 변화 자체를 특정 수정의 효과로 귀속하지 않는다."

D-H1a-18 Q18.2가 부과한 5개 조건:

| # | 조건 | 이 문서의 준수 |
|---|---|---|
| 1 | 병합하지 않는다 | 별도 파일·별도 `cohort_id`·별도 채점 산출 경로. 코드가 강제 |
| 2 | 하나의 effect estimate로 계산하지 않는다 | 두 코호트를 합산한 값은 어디에도 없다 |
| 3 | "0→2가 redesign 때문"이라고 쓰지 않는다 | 위 정정으로 해소 |
| 4 | 표면이 여러 곳 다름을 같은 표/문장에 표시 | §9.5 표 아래 문단에 명시 |
| 5 | 두 코호트의 **지위를 다르게 유지** | 아래 표에 명시 |

| 코호트 | 지위 (D-H1a-18 조건 5) |
|---|---|
| `h1a-original-20260803` | `completed_nonidentifying` |
| `h1a-typed-scope-20260817` | repaired-surface observation |

2026-08-03 세션이 0/40을 "조작 무효"로 읽지 않고 Q7=E의 tie-breaker 금지가 양
arm에 남아 있음을 찾아 Q10을 상신했다는 **이력 자체**는 사실 기록으로 남긴다.
그것과 §9.1의 관측을 인과적으로 연결하지 않는 것이 위 조건 3이다.

**말하지 않는 것**: 두 코호트는 fixture는 같지만 프롬프트 표면이 **여럿**
다르다(typed-scope 재설계 전체). 표면이 하나만 다른 대비가 아니므로 0→2를
특정 절 하나에 귀속시킬 수 없다. D-H1a-10 Q10.1이 두 코호트의 병합·재사용을
금지하므로 **풀링하거나 하나의 실험으로 보고하지 않는다** — 나란히 두는 것은
설계 진단의 방향 확인이지 통계적 비교가 아니다.

### 9.6 실행 provenance (§6 실행 규약 충족 증거)

§6이 요구한 "trial 실행 전 `assert_freezable()` + `assert_licensed_path_contrast(V, H)`
통과, V·H 명시 전달"은 `_h1a_cohort._certify_freezable()`에서 충족되며
(`source_attributes_visible=True`, `hard_defer_mapping=False`, 기본값 없음),
그 결과가 §9.2의 표다.

| 항목 | 값 |
|---|---|
| `cohort_manifest_sha256` | `9c84ef93…` |
| rendered prompt | KEPT `6d945f4e…` / REMOVED `856c3124…` |
| agent 정의 | `c22287cb…` (발송 직전 live 대조 일치) |
| `dispatch_script_sha256` | `31ad7b69…` |
| 스키마 적합 | 40/40 검증, 위반 0 (E2.4 검증기 verbatim, 핀 고정) |
| trial_id 매핑 | 내용 지문 대조로 **전단사 확인**, 발송 순서 추론 아님 |

**확정되지 않은 것**: 전송 계층이 모델 오버라이드를 준수했는지. per-agent meta
40개가 `model: opus`를 기록하지만 이는 요청의 기록이며, 준수 자체는 어떤
아티팩트로도 증명되지 않는다. `parameters.sampling`이 숫자가 아니라
`transport_default_unspecified`인 것이 같은 이유다.

### 9.7 이 결과로 정하지 않는 것

종결 보고 / QF-DEFER 재료 확보 후 해석 강화 / 상위 목적 이행 중 무엇을 할지는
**estimand·범위 문제이므로 외부 판정 채널 상신 대상**이다. §5g의 거버넌스 규칙
(조건을 `freeze_blocker`↔`diagnostic` 사이로 옮기는 것은 외부 판정 필요)과 같은
성격이고, 운영 세션이 정하지 않는다.

---

## 10. 종결 (D-H1a-18, 2026-08-22)

**Q18 = F = A(서술적 종결) + C(상위 목적 전환).** H1a는 §9를 서술적 보고로
남기고 종결한다. 추가 주 trial 0건.

판정문이 지정한 최종 기록을 **그대로** 옮긴다 (요약·재작성하지 않는다):

```yaml
QF_DEFER:
  status: material_unavailable
  executed: false

ceiling_diagnostic:
  status: unknown

experiment_closure:
  blocked_by_QF_DEFER: false
```

```yaml
D-H1a-18:
  H1a:
    close: true
    additional_main_trials: 0
    current_cohort:
      report: true
      causal_attribution: forbidden
      generalization: forbidden
  next_program:
    priority:
      - reusable_feedback_kernel
      - LLM_output_based_causal_inference
    H1a_third_cohort:
      status: deferred_as_separate_future_experiment
```

### 10.1 `unknown`을 `false`로 바꾸지 않는다

판정문이 이것만 따로 강조했다. 종결 기록은

> "ceiling이 없었다"

가 **아니라**

> **"ceiling 가능성은 독립적으로 진단되지 않았다."**

로 영구 보존한다. `QF-DEFER`가 미시행인 것은 실패가 아니고(Q14.2), 실패가
아니라는 사실이 "천장이 없었다"를 함의하지도 않는다. 이 구별이 무너지면
§9.3의 R1 제한 전체가 무의미해진다.

### 10.2 종결이 소급 변경하지 않는 것

- **D-H1a-7 / R3(인과 귀속 금지)은 유지된다.** 판정문이 명시했다. 장래에
  component-ablation 실험(요청서 선택지 D)을 별도 설계하면 그 실험의 estimand와
  귀속 규칙을 새로 판정받을 수 있으나, **현재 H1a의 R3을 소급 변경하지 않는다.**
- L1~L3·L8·R4~R7 전부 유지.
- §9.5의 두 코호트 병기는 Q18.2=c의 5개 조건 아래에서만 허용된다.

### 10.3 종결 후 이 문서를 읽는 사람에게

§9가 보고 정본이고 §10이 종결 기록이다. 숫자만 인용하면 틀린다 — **2/20은
`unknown`인 천장 방향과 p≈0.487을 달고 다녀야 하는 값**이다. 이 실험이 남긴
재사용 자산은 그 숫자가 아니라 §4·§5의 의무 구조·의미 감사·뮤테이션 규율이며,
판정문의 `next_program`이 그것을 다음 프로그램의 우선순위로 지정했다.
