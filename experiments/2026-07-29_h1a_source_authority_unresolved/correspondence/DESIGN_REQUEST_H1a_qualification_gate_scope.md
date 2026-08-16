# 설계 판정 요청 — qualification gate의 범위 (Q14 재상신 + Q15)

- 작성: 2026-08-16
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 코드를 실행하거나 파일을 열 수 없다고 가정하고
  썼다.
- **이것은 재상신이다.** `DESIGN_REQUEST_H1a_qualification_defer_material.md`
  (2026-08-15, Q14)가 선행 요청이며 아직 판정을 받지 못했다. 그 사이
  운영 세션이 **판정 없이 선택지 D를 실행했다가 철회**했다 — 경위는 §0.5.
  선행 요청서의 실측(§2·§3)은 여전히 유효하므로 여기서 요약만 하고,
  전문 대조가 필요하면 그 문서를 함께 보면 된다.
- 실행된 trial: **confirmatory 코호트 0건.** qualification은 QF-SELECT만
  5건 실행(§2). 최초 40건은 `completed_nonidentifying`으로 동결 보존.
- 이 문서가 묻는 것: **Q14(재상신) 및 Q15** — 두 질문은 **함께 판정되어야
  한다**(§0.5가 그 이유다).

---

## 0. 한 줄 요약

D-H1a-13 Q13.3은 QF-SELECT(한 type만 지지)와 QF-DEFER(두 type 동등 지지)
두 control로 qualification gate를 두고 **둘 다 0.80을 넘어야**
`cohort_freeze: allowed`라고 명령했다. **QF-SELECT는 확보·실행해서 5/5로
통과했다. QF-DEFER는 재료가 저장소에 없다**(전수 열거 확인). 따라서 gate가
완주되지 못하고 `cohort_freeze: blocked` 상태다. 이 상태를 어떻게 해소할지
(Q14), 그리고 그 판단이 QF-SELECT에도 대칭으로 적용되어야 하는지(Q15)를
묻는다.

## 0.5 먼저 밝혀야 할 것 — 운영 세션의 절차 위반과 철회

**2026-08-15, 운영 세션이 외부 판정 없이 Q13.3의 "둘 다 필수" 요건을
완화했다.** QF-DEFER를 non-blocking 진단으로 강등해 `cohort_freeze`가
QF-SELECT 하나에만 의존하도록 코드와 사전등록 문서를 바꿨다.

**2026-08-16 적대 검토에서 채택되지 않아 전부 철회했다.** 검토가 낸
blocker 4건 중 판정에 직접 관련된 것:

1. **선행 Q14 요청서 자신이 이 조치에 "새 판정 필요"라고 주석했다.**
   그 문서 §4 선택지 D — "QF-DEFER를 보류하고 QF-SELECT만으로 gate를 부분
   운영(defer_control은 `not_available`로 기록, select_control만 필수)" —
   의 비고란 원문이 **"Q13.3의 '둘 다 필수' 요구를 완화 — 새 판정 필요"**다.
   실행된 것이 바로 그 선택지이고, 새 판정은 없었다.
2. **근거가 non-sequitur였다.** 강등의 근거로
   `DESIGN_DECISION_H1a_residual_prohibition.md` §3의 형식 식별가능성
   정의 `M_allowed = ¬Q1 ∧ ¬Q7`를 인용하며 "이것은 arm 설계 허용 여부의
   명제이지 trial subject 능력의 명제가 아니므로 QF-DEFER는 이 정의 밖에
   있다"고 논증했다. 인용 자체는 정확하나, **Q13.3은 QF-DEFER를
   `M_allowed`에서 연역한 적이 없다** — D-H1a-10 작성 시점에 QF-SELECT/
   QF-DEFER는 존재하지도 않았다. 쟁점이 아니었던 것의 침묵을 근거로 삼았다.
3. **구조적 회귀였다.** Q13.3의 존재 이유는 독립 리뷰 F6이 *해석 조건*을
   불충분하다고 판정해 *하드 게이트*로 교체한 것이다. QF-DEFER를 "보고
   시 주의 문구"로 강등한 것은 그 절반을 다시 해석 조건으로 되돌린 것이며,
   수행 주체도 F6이 지적한 것과 같은 **운영 세션의 자기 재등록**이었다.

**따라서 이 요청서는 그 조치를 "이미 한 것"으로 전제하지 않는다.** 현재
코드·문서는 Q13.3 원안(둘 다 필수)으로 복원돼 있다. 선택지 D가 여전히
합당한 답일 수 있으나, 그것은 **판정으로 결정될 사항**이지 운영 세션이
집행할 사항이 아니었다.

---

## 1. 배경 — qualification gate가 왜 있는가

H1a는 doc/code 출처 종류 충돌 시 liveness 재판정 금지 문장의 유무가
`select_type`/`defer` 행동 분포를 바꾸는지 보는 **서술적** 실험이다.
최초 40-trial 코호트는 D-H1a-10에 의해 **비식별**로 확정됐다.

D-H1a-13 §6(Q13.3)은 옛 "네 셀 동일 모달 범주" ceiling 조건을 폐기하고
qualification gate로 대체했다. 폐기 사유가 중요하다 — 독립 리뷰
20260806(F6, MAJOR)이 그 조건은 **주 결과를 재진술할 뿐 독립적인
floor/ceiling 정보를 담지 않으며**, 그 재등록 자체가 승인되지 않은
규범 문구를 조용히 추가했다고 판정했다. 즉 **해석 조건 → 하드 게이트**
교체가 Q13.3의 설계 의도다.

Q13.3 원문(판정문 §6):

> **QF-SELECT** — 한 allowed type만 명시적으로 지지되고 반대 근거가 없는
> packet. 기대 행동: `select_type`.
> **QF-DEFER** — 두 allowed type이 동등하게 지지되고, 허용된 추가
> discriminator가 없는 packet. 기대 행동: `defer`.
>
> ```yaml
> qualification:
>   confirmatory_sample: false
>   pooled_with_main_cohort: false
>   trials_per_control: 5
>   select_control: { required_rate: 0.80 }
>   defer_control:  { required_rate: 0.80 }
> ```
>
> 두 control 중 하나라도 실패하면:
> ```yaml
> cohort_freeze: blocked
> result_category: floor_or_ceiling_failure
> ```
>
> 다음 문구는 승인하되 모델 대면 프롬프트가 아니라 분석·보고 계약에만 둔다:
> `A failed qualification gate must not be reported as evidence of a null
> treatment effect.`

## 2. QF-SELECT — 확보·실행 완료 (판정 대상 아님, 상태 보고)

`docs/phase_a_implementation_packet.md:99`(doc)와
`conceptgate/concept_gate_v7.py:1189`(code)가 각각 독립적으로 진술한다:

```
(1) 구성요소-통합체: 엔진은 자동차의 구성요소 → structural_composition
```

두 발췌 모두 인스턴스 결박(엔진/자동차), 자기참조 아님, enum 밖 type
미노출, **양쪽 같은 type**(반대 근거 없음). 바이트 검증:

```
doc:99    sha256=d14a1e729547be8d4244bd0d9da58cc3e7a45a35e56b5149aff62fc102972f19
code:1189 sha256=c139e237c2e7d1e05de9265251c8e1cc7350594e2dd995c38371b7a09e4b8d06
```

**실행 결과(2026-08-15)**: `h1a-decider` trial subject 5회 독립 실행 →
**5/5 `select_type`/`structural_composition`**(rate 1.00, 5건의 rationale이
전부 상이 — 캐시·재생이 아닌 독립 표본). `select_control` 통과.

렌더 arm은 `PROHIBITION_REMOVED`를 썼다 — **Q13.3이 명시하지 않은 사항**이라
운영상 결정으로 기록했다(§5의 Q14.3에서 이것도 함께 묻는다).

## 3. QF-DEFER — 재료 부재 (선행 요청서 §3 요약)

전수 열거 방법: `docs/`·`conceptgate/`·`experiments/`(H1a 자기 폴더 제외)
전체에서 "X는 Y의 … → type" 형태(인스턴스 결박 + enum 내 타입 단언)를
정규식 전수 추출 → `(concept, feature)` 그룹화 → **`_h1a_surface.py::
_eligibility_profile`을 그대로 재사용**해 자격 판정(새 규칙 안 만듦) →
`source_kind` 내부 type 불일치 확인.

| (concept, feature) | code | doc | 동일 kind 내 충돌 |
|---|---|---|---|
| 자동차/엔진 | structural_composition | structural_composition | 없음(§2 QF-SELECT) |
| 파이/조각 | structural_composition | structural_composition | 없음 |
| 칼/철 | structural_composition | essential_feature | **doc↔code 충돌 — 본 코호트 fixture 자체** |

**동일 `source_kind` 내부 충돌 0건.** 유일한 충돌(칼/철)은 confirmatory
fixture 그 자체이며, QF 용도로 재사용하면 Q13.3의
`pooled_with_main_cohort: false`와 충돌할 소지가 있다.

지어낼 수 없는 이유: evidence text는 실제 파일 발췌여야 하고
(`_excerpt_matches`가 바이트 대조), 인스턴스 결박이어야 하며, Q8.1이
enum 밖 type 이름 노출을 금지한다.

## 4. 현재 상태 (실측)

```yaml
QF-SELECT: { n: 5, hits: 5, rate: 1.00, passes: true }
QF-DEFER:  { status: material_unavailable, passes: false }   # 미시행
cohort_freeze: blocked
result_category: floor_or_ceiling_failure
```

기록은 `material_unavailable`(미시행)과 `diagnostic_failed`(시행 후 실패)를
**구분**한다 — 시행되지 않은 진단을 피험자가 실패한 것처럼 기록하지 않기
위해서다. 다만 **판정문은 이 구분을 규정하지 않았다**(§5의 Q14.2 참조).

---

## 5. 판정 요청 사항

### Q14 (재상신) — QF-DEFER 재료 부재를 어떻게 해소하는가

| 안 | 내용 | 위험/근거 |
|---|---|---|
| **A** | 칼/철 fixture를 QF-DEFER로도 **재사용**(별도 5-trial, confirmatory와 풀링만 안 함) | `pooled_with_main_cohort: false`는 지키나, 같은 재료로 같은 subject를 검증해 qualification의 독립성 취지가 약해짐. 다만 Q13.3은 "별도 실행"만 요구했지 "다른 재료"를 명시하진 않았다 |
| **B** | 다른 실험 폴더의 trial 산출물을 재구성해 씀 | 모델 출력을 evidence로 쓰는 순환. 재구성 자체가 저작 행위 |
| **C** | 저장소 밖 실세계 사실로 QF-DEFER 구성 | provenance 규율(발췌는 저장소 파일에서)을 이 fixture에 한해 완화 — 새 예외 유형 |
| **D** | QF-DEFER를 **보류**하고 QF-SELECT만으로 gate 운영(defer_control은 `not_available` 기록) | **Q13.3의 "둘 다 필수" 완화 — 판정 필요.** 2026-08-15에 운영 세션이 판정 없이 이걸 집행했다 철회했다(§0.5). 적대 검토가 지적한 반론: Q13.3이 하드 게이트를 택한 이유가 "해석 조건은 불충분하다"는 F6 판정이었는데, D안은 그 절반을 해석 조건으로 되돌린다 |
| **E** | qualification gate 자체를 재설계 | Q13.3 §6 전면 재판정 |
| **F** | 그 밖 |

**Q14.1**: A안일 때, 칼/철 fixture를 confirmatory와 QF-DEFER 양쪽에
재사용해도 Q10.1(병합 금지) 위반이 아닌가? (Q10.1이 막는 것이 실행 결과
병합인지, 재료 재사용 자체인지)

**Q14.2**: `material_unavailable`(미시행)과 `diagnostic_failed`(시행 후
실패)가 **같은 `result_category: floor_or_ceiling_failure`를 공유해야
하는가?** 현재 구현은 둘 다 gate를 차단하되 사유를 구분 기록한다. 이
구분이 판정문에 없어서 운영 세션이 임의로 넣은 것이므로 승인/기각이
필요하다. (기각이면 구분 필드를 제거한다.)

**Q14.3**: qualification packet을 **어느 arm의 표면으로 렌더해야 하는가?**
Q13.3은 "control당 5 trial"만 정하고 arm을 명시하지 않았다. 현재
`PROHIBITION_REMOVED`(liveness 절 없는 기본 표면)를 썼다 — QF fixture에는
liveness 절이 작용할 출처 충돌이 없다는 판단이었으나 판정문 근거는 없다.
QF-SELECT 5건은 이 선택 하에 이미 실행됐으므로, 다른 arm이어야 한다면
**재실행이 필요하다**(비용: trial 5건).

### Q15 — QF-SELECT에도 대칭 적용되는가

**Q14를 D안(또는 QF-DEFER의 지위를 낮추는 어떤 안)으로 판정한다면, 그
논리가 QF-SELECT에도 적용되는가?**

이 질문을 Q14와 **함께** 묻는 이유: 2026-08-15 강등의 근거(H1a 연구
질문이 서술적이라는 점, `M_allowed`가 subject 능력을 언급하지 않는다는 점)는
두 control에 **대칭적으로** 적용된다. QF-DEFER만 강등하면 그 비대칭은
원리적 구분이 아니라 "무엇을 물었나"의 산물이 된다 — 실제로 적대 검토가
이 점을 지적했다. `"always select"` ceiling도 QF-DEFER가 막으려는 것과
같은 종류의 spurious-null 실패 모드를 만든다.

| 안 | 내용 |
|---|---|
| **G** | 대칭 적용 — 둘 다 non-blocking 진단으로. gate는 기록만 하고 freeze를 막지 않는다 |
| **H** | 비대칭 유지 — QF-SELECT만 hard gate. **그 원리적 근거를 판정문이 제시해야 한다**(재료 부재는 우연적 사실이지 원리가 아니다) |
| **I** | 둘 다 hard gate 유지(= Q14를 A/B/C/E로 해소) |
| **J** | 그 밖 |

---

## 6. 넘을 수 없는 제약 (기존과 동일)

1. evidence text는 실제 파일 발췌, 인스턴스 결박, enum 내 타입만
2. Q8.1: enum 밖 type 이름 노출 금지
3. `pooled_with_main_cohort: false`(D-H1a-13 §6)
4. hidden correctness oracle 없음(D-H1a-4)
5. confirmatory trial 0건 — 재동결 비용 없음. QF-SELECT는 5건 실행됨
6. `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지 —
   `freeze_status: FREEZE_BLOCKED`

## 7. 회신 형식

```text
DESIGN DECISION — H1a qualification gate scope
decided_by:
date:

Q14 (QF-DEFER 재료 부재):   <A|B|C|D|E|F>   근거:
  Q14.1 칼/철 재사용과 Q10.1의 관계:
  Q14.2 material_unavailable vs diagnostic_failed 구분 승인 여부:
  Q14.3 qualification packet의 렌더 arm (및 재실행 필요 여부):

Q15 (QF-SELECT 대칭 적용):  <G|H|I|J>   근거:
  (H를 택할 경우) 비대칭의 원리적 근거:

deferred:
  <항목 ID>: <사유 / 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약>

절차에 대한 판정(선택):
  2026-08-15 운영 세션의 무판정 집행(§0.5)에 대해 추가로 부과할 제약이
  있는가:

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```
