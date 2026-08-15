# 설계 판정 요청 — QF-DEFER 재료 부재 (Q14)

- 작성: 2026-08-15
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 원문·실측을
  전부 본문에 embed했다. 코드를 실행하거나 파일을 열 수 없다고 가정하고
  썼다 — 인용은 전부 실물 대조를 거쳤고, 열거는 재현 가능한 스크립트로
  수행했다.
- 계기: D-H1a-13 Q13.3이 명령한 qualification gate(QF-SELECT/QF-DEFER
  두 control)를 구현하려고 재료를 찾았다. **QF-SELECT 재료는 확보했으나
  QF-DEFER 재료가 이 저장소에 없다.**
- 실행된 trial: **이 코호트 0건.** 최초 40건은 `completed_nonidentifying`으로
  동결 보존.
- 선행 판정 9건(전부 구속력 유지): D-H1a-1~7 / Q1·Q2 / Q3·Q4 / Q5~Q8 /
  Q9 / D-H1a-10 / D-H1a-11 / D-H1a-12 / **D-H1a-13**(2026-08-06, Q13.3이
  이 gate를 명령).
- 이 문서가 묻는 것: **Q14 하나** (QF-DEFER 재료 부재 시 취할 조치)

---

## 0. 한 줄 요약

D-H1a-13 §6(Q13.3)은 QF-SELECT(한 type만 지지)와 QF-DEFER(두 type이 동등
지지, discriminator 없음) 두 fixture로 qualification gate를 두라고
명령했다. **QF-SELECT는 이 저장소의 실제 자격 있는 소스에서 찾았다
(§2). QF-DEFER는 전수 열거로도 안 나왔다(§3).** 지어내면 이 실험 전체의
증거 원칙(발췌는 실제 파일에서, 인스턴스 결박, 자기참조 배제)을 깬다.
따라서 진행 방식을 묻는다.

---

## 1. 배경 — 왜 QF-DEFER가 필요한가 (사전 지식 없이 읽는 경우)

H1a는 doc/code 출처 종류 충돌 시 liveness 재판정 금지 문장의 유무가
`select_type`/`defer` 행동 분포를 바꾸는지 보는 서술적 실험이다. 최초
40-trial 코호트는 D-H1a-10에 의해 **비식별**로 확정됐다 — 조작이 양 arm
모두를 여전히 금지해 대비 자체가 성립하지 않았다.

D-H1a-13 §6(Q13.3)은 이걸 다시 확인하기 전에, **본 코호트를 돌리는
trial subject가 애초에 명확한 경우에서 select/defer를 제대로 하는지**
먼저 검증하라고 명령했다:

> QF-SELECT: 한 allowed type만 명시적으로 지지되고 반대 근거가 없는 packet.
> 기대 행동: `select_type`.
> QF-DEFER: 두 allowed type이 동등하게 지지되고, 허용된 추가 discriminator가
> 없는 packet. 기대 행동: `defer`.
> ...
> `select_control`/`defer_control` 각각 5 trial, 요구 비율 0.80. **둘 다**
> 통과해야 gate 통과.

## 2. QF-SELECT — 확보 완료 (참고용, 판정 대상 아님)

`docs/phase_a_implementation_packet.md:99`와
`conceptgate/concept_gate_v7.py:1189`가 각각 독립적으로 다음을 진술한다:

```
(1) 구성요소-통합체: 엔진은 자동차의 구성요소 → structural_composition
```

두 발췌 모두:
- 인스턴스 결박(엔진/자동차, 일반 규칙 아님)
- 자기참조 아님(H1a 실험 자체를 서술하지 않음)
- enum 밖 type 미노출(`structural_composition` 외 타입명 없음)
- **doc·code 양쪽 다 같은 type** — 반대 근거 없음

바이트 검증:
```
doc:99   sha256=d14a1e729547be8d4244bd0d9da58cc3e7a45a35e56b5149aff62fc102972f19
code:1189 sha256=c139e237c2e7d1e05de9265251c8e1cc7350594e2dd995c38371b7a09e4b8d06
```

## 3. QF-DEFER — 부재 (판정 대상)

### 3.1 실측 방법

grep 단발 검색은 "없다"를 증명 못 한다(이 실험이 이미 겪은 실패 —
`H1A_PROBLEM_ANALYSIS.md` P5). 대신:

1. `docs/`, `conceptgate/`, `experiments/`(H1a 자기 폴더 제외) 전체에서
   `"X는 Y의 ... → type"` 형태(인스턴스 결박 + enum 내 타입 단언)를
   정규식으로 전수 추출
2. `(concept, feature)`로 그룹화
3. **`_h1a_surface.py::_eligibility_profile`을 그대로 재사용**해 각
   발췌의 자격을 판정(자기참조 문서 등을 코드가 이미 정의한 규칙으로
   배제 — 새 규칙을 만들지 않음)
4. 그룹별로 `source_kind`(doc/code/frozen) 내부에 서로 다른 type이
   있는지 확인 — 있으면 QF-DEFER 후보

### 3.2 결과 (자격 있는 소스만)

| (concept, feature) | code | doc | 동일 kind 내 충돌 |
|---|---|---|---|
| 자동차/엔진 | structural_composition | structural_composition | 없음(§2 QF-SELECT로 이미 사용) |
| 파이/조각 | structural_composition | structural_composition | 없음 |
| 칼/철 | structural_composition | essential_feature | **doc↔code 충돌 — 본 코호트 fixture 자체** |

**동일 `source_kind` 내부 충돌은 0건.** 유일한 충돌(칼/철)은 이미 본
코호트가 쓰고 있는 그 fixture이며, QF 용도로 다시 쓰면 qualification이
confirmatory와 **섞이는 것**이 되어 D-H1a-13 §6이 금지한
`pooled_with_main_cohort: false`를 어긴다.

### 3.3 왜 지어낼 수 없는가

이 실험의 fixture 원칙(`docs/H1A_ISSUE_REGISTER.md`, C2~C10 계열 판정이
누적해 확정)은:

- evidence text는 **실제 파일에서 발췌**해야 한다(`_excerpt_matches`가
  `start_line:end_line`을 원문과 바이트 대조)
- 인스턴스 결박이어야 한다(일반 규칙이 아니라 이 concept/feature 쌍을
  직접 지시)
- Q8.1: enum 밖 type 이름 노출 금지

QF-DEFER가 요구하는 "두 type이 동등 지지, discriminator 없음"을 만들려면
**doc과 code 양쪽에 같은 concept/feature를 서로 다른 type으로 진술하는
실제 텍스트**가 있어야 하는데, 이 저장소에 그런 텍스트는 칼/철(=본
fixture) 외에 없다. 지어내면 evidence를 저작하는 것이고, 이는 이
실험이 그동안 명시적으로 거부해 온 것과 같은 종류의 결함이다.

---

## 4. Q14 — 선택지

| 안 | 내용 | 위험/근거 |
|---|---|---|
| **A** | 칼/철 fixture를 QF-DEFER로도 **재사용**(별도 5-trial 실행, confirmatory와 풀링만 안 함) | Q13.3의 "pooled_with_main_cohort: false"는 지키나, **같은 재료로 같은 trial subject를 검증**하는 것이라 qualification의 독립성 취지(본 코호트와 다른 재료로 기본 능력을 검증)가 약해짐. 다만 D-H1a-13이 "confirmatory와 섞이지 않는 별도 실행"만 요구했지 "다른 재료"를 명시적으로 요구하진 않았다 |
| **B** | 다른 실험 폴더(`experiments/2026-07-24_e2.2.*`)의 trial 산출물(예: 돌체/바퀴, enum 밖 `functional` 포함)을 **enum 두 값만 남기도록 재구성**해 QF-DEFER로 씀 | 모델 출력을 evidence로 쓰는 것은 순환(자기가 만든 것을 검증 재료로 씀). 그리고 재구성 자체가 저작 행위 |
| **C** | 인스턴스를 새로 만들되 **실제 세계 사실**(저장소 밖, 예: "엔진은 자동차의 구성요소이자 자동차의 필수 정체성 조건이다"류 대중적으로 논쟁적인 사례)로 QF-DEFER를 구성 | 저장소 provenance 규율(발췌는 저장소 파일에서) 자체를 이 fixture에 한해 완화하는 것 — 새 예외 유형 |
| **D** | QF-DEFER를 **보류**하고 QF-SELECT만으로 gate를 부분 운영(defer_control은 `not_available`로 기록, select_control만 필수) | Q13.3의 "둘 다 필수" 요구를 완화 — 새 판정 필요 |
| **E** | 그 밖 |

**부수 질문**: A안을 택하면, 칼/철 fixture를 QF-DEFER 5-trial에 쓸 때
**분리 confirmatory에 다시 쓸 수 있는가**(같은 fixture, 다른 trial_id
prefix — Q10.1의 "병합 금지"가 실행 결과 병합을 막는 것이지 재료 재사용
자체를 막는 것은 아닐 수 있음), 아니면 confirmatory 전용으로 남겨야
하는가?

---

## 5. 넘을 수 없는 제약 (기존과 동일)

1. evidence text는 실제 파일 발췌, 인스턴스 결박, enum 내 타입만
2. Q8.1: enum 밖 type 이름 노출 금지(A안 제외 모든 안에서 유지)
3. `pooled_with_main_cohort: false`(D-H1a-13 §6)
4. hidden correctness oracle 없음(D-H1a-4)
5. 실행된 trial 0건 — 재동결 비용 없음

## 6. 회신 형식

```text
DESIGN DECISION — H1a qualification defer material
decided_by:
date:

Q14 (QF-DEFER 재료 부재):   <A|B|C|D|E>   근거:
  Q14.1 A안일 때, 칼/철 fixture를 confirmatory와 QF-DEFER 양쪽에
        재사용해도 Q10.1 위반이 아닌가:

deferred:
  <항목 ID>: <사유 / 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약>

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```
