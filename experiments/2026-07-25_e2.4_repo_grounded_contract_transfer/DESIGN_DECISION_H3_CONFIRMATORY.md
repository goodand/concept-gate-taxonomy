# DESIGN DECISION — H3 confirmatory

- decided_by: OpenAI Codex
- date: 2026-07-30
- input: `DESIGN_REQUEST_H3_confirmatory.md`
- status: **존재 주장으로 종료, 전칭/우월성 확증은 별도 재료 확보 과제로 분리**

## 0. Source Grounding

| source type | used | scope |
|---|---:|---|
| prompt-given | yes | Current user request and requested policy: source-grounded first, separate assumptions/facts/inference |
| attached-file grounded | yes | `DESIGN_REQUEST_H3_confirmatory.md`, especially M1-M11 and D-H3C-1..6 |
| prior local artifact | yes | `DESIGN_DECISION_H3.md` from the current workspace |
| repository-grounded | partial | Only artifacts present in the workspace were inspected; embedded M1-M11 were not fully re-audited against an upstream repository |
| MCP-grounded | no | This is an experimental-design/estimand decision, not a taxonomy classification call |
| literature-grounded | no | No external literature was needed to resolve the internal estimand question |
| model inference | yes | Formal interpretation of probability space, independence, and measurement grammar |

This decision treats M1-M11 as supplied measurements unless explicitly marked otherwise. It does not certify the embedded repository measurements beyond the files available in this workspace.

## 1. 판정문

```text
DESIGN DECISION — H3 confirmatory
decided_by: OpenAI Codex
date: 2026-07-30

D-H3C-1 (Delta의 확률 공간): A — 모델 샘플링만
  근거:
    현재 자료에서 독립적으로 정의된 packet 모집단이 없다. class당 K=1이고,
    세 fixture는 표집된 것이 아니라 목적에 맞게 제작되었으며, sufficient
    class의 핵심 evidence는 이전 합성 fixture 문장에서 왔다(M1-M7).

    따라서 현재 Delta는 다음 조건부 확률의 차이다.

      P(action=defer | fixed packet, fixed arm, fixed model, fixed parameters)

    R을 늘리면 이 고정 packet에서의 모델 샘플링 변동은 더 정밀하게 추정할 수
    있지만, insufficient packet 일반 또는 repo-derived packet 일반으로
    일반화되지는 않는다. C는 M6/M7 때문에 실행 불가이고, B는 모집단을
    "이 프로젝트가 만든 두 템플릿의 명사 치환 인스턴스"로 축소한다.

D-H3C-2 (존재 vs 전칭): ① + 조건부 ③
  근거:
    현재 pilot은 "이 고정 packet 조건에서 CONTRACT 인터페이스가 비교 arm과
    다른 defer 행동을 보인 사례가 있다"는 존재 수준의 관측으로 닫아야 한다.
    이 결론은 class 일반 우월성이나 insufficient 일반에 대한 전칭 명제가 아니다.

    프로젝트가 여전히 전칭 명제를 원한다면, H3를 계속 돌리는 것이 아니라
    독립 held-out 재료 확보와 라벨링 절차를 별도 과제로 분리해야 한다. 즉
    현재 H3C는 존재 주장으로 종료하고, 전칭 H3는 새 표집틀이 생긴 뒤 새
    preregistration으로 시작한다.

D-H3C-3 (템플릿 독립성): other — K_eff <= 2, 외적 일반화에서는 K=1 취급
  근거:
    남은 5문장을 문장 단위 K=5로 세는 것은 독립성 과대평가다. M3에 따르면
    이들은 두 템플릿의 명사 치환이며, 같은 템플릿 내 문장은 독립 fixture가
    아니라 템플릿 내 반복에 가깝다.

    템플릿 모집단 내부 분석의 클러스터 상한은 K=2다. 그러나 두 템플릿 모두
    같은 프로젝트, 같은 생성 절차, 같은 합성 도메인에서 나온 것이므로 실제
    저장소 산문이나 일반 온톨로지 evidence로의 외적 일반화에서는 하나의
    생성 family, 즉 K=1로 취급해야 한다.

    결론: held-out을 남은 5문장으로 만들더라도 확증용 독립 test set이 되지
    않는다. 사용한다면 renderer/scorer assay 또는 template-family pilot으로만
    사용한다.

D-H3C-4 (3x3 축약): ④ — defer의 조건부 적절성을 recall/precision 쌍으로 보고
  근거:
    M9는 arm 간 차이가 "defer의 양"이 아니라 "defer의 위치"임을 보여준다.
    따라서 P(defer | insufficient)의 단일 Delta만으로는 sufficient_consistent
    false-defer와 insufficient non-defer를 동시에 표현할 수 없다.

    다음 실행부터는 defer를 diagnostic positive로 보고, 최소한 다음 쌍을
    함께 1차 또는 공동 1차 지표로 둔다.

      recall_defer = P(defer | insufficient)
      precision_defer = P(insufficient | defer)

    balanced 3-class 설계에서는 sufficient class별 false-defer rate도 반드시
    병기한다. macro action accuracy는 전체 혼동행렬을 요약하는 보조 지표로
    유지한다.

    단, 이 변경은 pilot 결과를 본 뒤의 estimand 정정이므로 기존 45 trial에
    소급해 확증 채점으로 적용하지 않는다. 기존 pilot은 descriptive result로만
    남긴다.

D-H3C-5 (invalid 지위): ① — treatment의 일부로 확정, invalid rate 필수 병기
  근거:
    CONTRACT arm의 더 큰 응답 schema와 contract_assessment는 처치 자체의 일부다.
    따라서 invalid-output을 제거하거나 valid-only로 1차 Delta를 재계산하면
    처치의 사용 비용을 숨기게 된다.

    현행처럼 schema-invalid는 action-incorrect로 처리하고, invalid-output rate를
    별도 결과로 항상 보고한다. 필요하면 valid-only 분석을 sensitivity check로
    둘 수 있으나 1차 판정이나 인증 근거가 될 수 없다.

D-H3C-6 (라벨 결정가능성): ② — M10은 템플릿성 측정, 라벨링은 독립 인간 판단 유지
  근거:
    M10의 정규식 3/3 재현은 라벨 규칙의 일반적 결정가능성이 아니라 현재
    corpus가 두 템플릿으로 쓰였다는 사실을 재인식한 결과다. M7은 실제 저장소
    산문에 같은 규칙을 적용하려던 시도가 서로 다른 이유로 반복 기각됐음을
    보여준다.

    held-out fixture를 만들려면 사전등록된 코딩 규칙, 복수 독립 판정자,
    disagreement resolution, inter-rater agreement가 필요하다. 정규식 검출기는
    템플릿 누출 감지와 positive/negative control에는 쓸 수 있지만 oracle
    labeler로 쓰면 안 된다.

deferred:
  전칭 H3 확증 실험:
    target population, sampling frame, held-out fixture 생성/선정 절차,
    독립 라벨링 프로토콜, SESOI, alpha/power 또는 의사결정 임계, 다중성 제어,
    fixture 간 변이를 반영할 분석 모형이 필요하다.

  template-family follow-up:
    템플릿 인스턴스 모집단을 별도 대상으로 삼을지, 삼는다면 템플릿 생성 문법과
    명사 표집 규칙을 사전등록해야 한다.

  prompt/schema ablation:
    CONTRACT 효과를 계약 텍스트 효과와 큰 schema/diagnostic burden 효과로
    분해하려면 별도 factorial 또는 ablation 설계가 필요하다.

new_constraints:
  - 현재 H3C 자료로 class-general superiority, insufficient-general superiority,
    또는 repo-derived-general superiority를 주장하지 않는다.
  - 현재 pilot의 허용 결론은 fixed-packet, fixed-model, fixed-parameter 조건의
    descriptive/existence-level 관측이다.
  - R은 모델 샘플링 반복 수이고 K가 아니다.
  - 남은 5개 합성 문장을 독립 held-out K=5로 세지 않는다.
  - 남은 문장을 사용할 경우 template-family assay 또는 non-certifying pilot으로만
    표시한다.
  - "repo-derived"는 class별 출처 차이를 명시한다: insufficient는 실제 저장소
    산문/코드, sufficient는 이전 합성 fixture 문장이다.
  - 단일 Delta는 다음 실행의 1차 estimand로 쓰지 않는다. defer recall과 defer
    precision, sufficient class별 false-defer를 함께 보고한다.
  - pilot 결과를 보고 바꾼 지표는 기존 45 trial에 소급해 확증 판정으로 적용하지
    않는다.
  - invalid-output은 treatment burden의 일부이며 action-incorrect와 invalid rate
    병기를 유지한다.
  - 정규식 라벨러는 템플릿성 감지 도구일 뿐 독립 oracle이 아니다.
  - 전칭 H3를 재개하려면 먼저 독립 표집틀과 라벨링 프로토콜을 freeze-before-run
    산출물로 동결한다.

실험 진행 여부: 존재 주장으로 종료; 전칭/우월성 확증은 재료 확보를 별도 과제로 분리
사유:
  현재 자료에는 확증 실험의 표집틀이 없다. 그러므로 SESOI, power, K 산정은
  아직 미정인 것이 아니라 적용 대상이 없다. 현 pilot은 계약 인터페이스가
  특정 insufficient packet에서 비교 arm과 다른 defer 행동을 유도했다는
  존재 수준의 관측을 남길 수 있다. 그러나 class 일반 또는 repo-derived 일반
  우월성은 새 sampling frame과 독립 held-out fixture 없이는 형식적으로
  식별되지 않는다.
```

## 2. 형식적 요약

현재 H3C의 관측값을 다음처럼 쓰자.

```text
Y = model_output_action
A = arm
P = fixed packet
M = fixed model and parameters
```

현재 추정 가능한 값은:

```text
Pr(Y = defer | A, P, M)
```

이다. H3C가 원래 원하는 값은 대략:

```text
Pr(Y = defer | A, class = insufficient, population = repo-derived packets)
```

이다. 두 식 사이에는 packet 모집단과 표집 절차가 필요하다. 현재 문서의 M1-M7은
그 절차가 없고, fixture가 결과와 설계 목적에 맞추어 제작되었음을 보인다.

따라서 여기서 power를 계산하는 것은 표본수를 작게 잡는 문제가 아니라, 표본이
무엇의 표본인지 말하지 않은 상태에서 확률문을 쓰는 문제다.

## 3. 운영 세션 전달문

> H3C 확증 실험은 현 자료로 진행하지 않습니다. 현재 pilot은 fixed packet에서
> CONTRACT가 비교 arm과 다른 defer 행동을 보인 존재 수준의 서술 결과로 종료합니다.
> 남은 5개 합성 문장은 독립 held-out K=5가 아니라 최대 두 템플릿, 외적 일반화
> 관점에서는 하나의 생성 family입니다. 전칭 또는 우월성 주장을 원하면 새
> sampling frame, 독립 held-out fixture, 독립 라벨링 프로토콜, SESOI/power/분석
> 모형을 별도 과제로 동결한 뒤 새 cohort로 시작하세요. 기존 45 trial은
> non-certifying descriptive pilot으로 보존하고, pilot 결과를 본 뒤 수정한
> 지표를 소급해 인증 근거로 쓰지 마세요.

---

## 4. 운영 세션 수용 기록 (2026-07-30)

§0~§3은 판정 원문이며 한 글자도 수정하지 않았다. 아래는 운영 세션이 판정을
저장소에 반영한 기록이다.

### 4.1 수용 — 6항목 전부 이의 없음

D-H3C-1(A) · D-H3C-2(①+조건부③) · D-H3C-3(K_eff≤2, 외적으로 K=1) ·
D-H3C-4(④ recall/precision 쌍) · D-H3C-5(① treatment 일부) ·
D-H3C-6(② 정규식은 oracle 아님) 전부 수용한다.

특히 D-H3C-1의 진술 — *"여기서 power를 계산하는 것은 표본수를 작게 잡는
문제가 아니라, 표본이 무엇의 표본인지 말하지 않은 상태에서 확률문을 쓰는
문제다"*(§2) — 이 D-H3-5의 deferred 5항목이 왜 "아직 미정"이 아니라
"적용 대상이 없음"인지를 정확히 짚는다.

### 4.2 D-H3C-4 적용 결과 — 단일 Δ가 감추고 있던 것

판정대로 defer를 diagnostic positive로 놓고 recall/precision을 쌍으로
계산했다(`_h3_score.py: defer_diagnostics`). 기존 45 trial에 **서술적으로만**
적용했다.

| arm | recall = P(defer\|insufficient) | precision = P(insufficient\|defer) | defer 총수 |
|---|---|---|---|
| CONTROL_REPO_H3 | 0.00 | **0.00** | 3 (0개 적중) |
| A_REPO_H3 | 0.00 | **0.00** | 4 (0개 적중) |
| CONTRACT_REPO_H3 | 0.80 | **1.00** | 4 (4개 전부 적중) |

**단일 Δ=+0.80은 "CONTRACT가 더 많이 보류한다"로 읽혔으나, 실제로는 세 arm의
보류 총량이 3·4·4로 거의 같다.** 차이는 양이 아니라 조준이다 — 비교 arm의
보류는 **한 건도** 표적에 맞지 않았고 CONTRACT는 전부 맞혔다. D-H3C-4의
논거("차이는 defer의 양이 아니라 위치")가 실측으로 확인됐다.

**이 수치는 확증 근거가 아니다.** 지표를 결과를 본 뒤 채택했으므로
`h3_pilot_score.json`의 `post_hoc_metrics`에 그 사실을 명시했고,
`test_h3_score.py::test_defer_diagnostics_are_marked_post_hoc`가 그 표시를
강제한다. 사전등록 1차 지표로서의 지위는 **다음 cohort부터**다.

### 4.3 new_constraints 11항 반영 위치

| 제약 | 반영 |
|---|---|
| class-general/insufficient-general/repo-derived-general 우월성 주장 금지 | `h3_pilot_score.json.allowed_conclusion`(신설), 등록부 D6, HANDOFF §H3 |
| 허용 결론은 fixed-packet·fixed-model·fixed-parameter 조건의 존재 수준 서술 | 같은 필드에 그대로 문장화 |
| R은 샘플링 반복이고 K가 아니다 | `sampling_units` 필드(신설)에 R/K와 그 의미를 분리 기재 |
| 남은 5문장을 K=5로 세지 않는다 | 등록부 D6, 요청서 §3.1 |
| 남은 문장 사용 시 template-family assay 또는 비인증 pilot으로만 표시 | 등록부 D6 |
| "repo-derived"는 class별 출처 차이 명시 | `repo_derived_provenance` 필드(신설) — insufficient=실제 코드, 두 sufficient=이전 합성 fixture 문장 |
| 단일 Δ는 다음 실행의 1차 estimand가 아니다 | `defer_diagnostics` 신설 + `post_hoc_metrics` 표시 |
| 소급 확증 적용 금지 | 같은 표시 + 전용 테스트 |
| invalid는 treatment 일부, action-incorrect + rate 병기 | 기존 구현 유지(`rate()`가 전체 분모, `invalid_output_rate` 병기) |
| 정규식 라벨러는 oracle이 아니다 | 4.4 참조 |
| 전칭 H3 재개 시 표집틀·라벨링 프로토콜을 freeze-before-run으로 동결 | 등록부 "다음 세션 첫 행동" |

### 4.4 정규식 검출기의 지위 (D-H3C-6)

M10의 검출기는 **저장소에 커밋되지 않았다** — 측정용 일회성 스크립트로만
실행했고 파일로 남기지 않았다. 판정이 "oracle labeler로 쓰면 안 된다"고
했으므로 이 상태를 유지한다. 다시 필요해지면 **템플릿 누출 감지 / positive·
negative control** 용도로만, 그 용도를 이름과 docstring에 박아서 만든다.

### 4.5 E2.4의 상태

H3는 **존재 주장으로 종료**한다. 남은 것은 E2.4 내부 과제가 아니라 별도
과제 3건이다(판정문 `deferred`): 전칭 H3 확증 실험(표집틀 확보 선행),
template-family follow-up, prompt/schema ablation. 셋 다 새 preregistration이
필요하며 이번 세션 범위 밖이다.
