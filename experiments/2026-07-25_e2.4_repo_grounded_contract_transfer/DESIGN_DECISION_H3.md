# DESIGN DECISION — H3

## E2.4 3-arm comparison의 측정 불변성 회복

- decided_by: OpenAI Codex
- date: 2026-07-29
- input: `DESIGN_REQUEST_H3.md`
- status: **재정의 필요**

---

## 1. 판정문

```text
DESIGN DECISION — H3 (E2.4 3-arm comparison)
decided_by: OpenAI Codex
date: 2026-07-29

D-H3-1 (비교 성립 여부): other — 측정 불변형 3-arm으로 재정의

근거:
현재 설계는 arm마다 보류 가능성과 판정 어휘가 다르므로, 관측된 abstention
차이를 모델의 판단 차이와 출력 언어의 표현력 차이로 분해할 수 없다.
legacy에서 abstain이 관측되지 않았다는 사실은 abstain하지 않았다는 증거가
아니다. 따라서 현 상태의 3-arm 비교는 성립하지 않는다.

다만 legacy arm을 제거하지는 않는다. 세 arm 모두에 동일한 최소 공통
action 표면(accept_report | repair | defer)을 제공하고, 이것만 arm 간
1차 결과로 사용한다. CONTROL/A의 "legacy"는 E2.3 출력 스키마가 아니라
프롬프트 규칙의 계보를 뜻하도록 이름과 문서를 바꾼다.

CONTRACT 전용 audit/contract_verdict 필드는 arm 내부 진단용으로만 남길 수
있지만, 공통 action을 대체하거나 arm 간 1차 지표로 사용할 수 없다.

D-H3-6 (실험 정당성): B — 단, 비인증 pilot만 허용

근거:
기존 유일 관측은 N=1·오라클 유출·제외 fixture라는 이유로 H3의 경험적
근거가 될 수 없다. 작은 clean pilot으로 새 신호를 관측하는 것은 정당하지만,
그 pilot은 옛 관측을 소급 유효화하거나 superiority를 인증하지 않는다.

또한 현재 3개 fixture는 CONTRACT_REPO clean cohort의 통과 결과로 이미
선별·인증됐다. 이 재료에서 CONTRACT 우월성을 다시 검정하면 결과에 의한
시험재료 선택이 된다. 기존 fixture는 assay/pipeline pilot에만 사용한다.
확증적 비교에는 모델 결과와 독립적으로 선정한 held-out fixture가 필요하다.

D-H3-2 (커버리지): D — 3개 유효 class의 완전 교차 배치

근거:
conflicting의 빈자리를 다른 class로 채우지 않는다. 검증하지 못한
conflicting에 관한 주장은 보류한다.

pilot에서는 sufficient_consistent, sufficient_repairable, insufficient의
세 class를 세 arm 모두에 동일하게 배정한다. 즉 3 class × 3 arm의 완전
교차 설계다. insufficient가 1차 표적이고, 두 sufficient class는
CONTRACT가 단순히 항상 defer하는지를 검출하는 specificity control이다.

확증 단계에서는 같은 세 class의 held-out fixture를 사용한다. held-out을
확보하지 못하면 결론은 사용한 packet에 한정되며 class 일반화는 금지한다.

D-H3-3 (채점 지표): other — 공통 action의 직접 채점

근거:
사후 행동 코더를 1차 측정기로 두면 새 측정오차와 해석자 의존성이 생긴다.
세 arm에 공통 action 필드를 직접 요구하므로 1차 결과에는 코더가 필요 없다.

hidden oracle의 target action은 다음과 같다.
  sufficient_consistent  -> accept_report
  sufficient_repairable  -> repair
  insufficient           -> defer

1차 estimand:
  Δ_CONTROL =
    P(defer | insufficient, CONTRACT_REPO_H3)
    - P(defer | insufficient, CONTROL_REPO_H3)

  Δ_A =
    P(defer | insufficient, CONTRACT_REPO_H3)
    - P(defer | insufficient, A_REPO_H3)

필수 2차 지표:
  - sufficient class별 false-defer rate
  - 세 class macro action accuracy
  - invalid-output rate
  - repair 대상에서 repair 정확도
  - CONTRACT arm 내부의 action/contract_verdict 불일치율

자유서술 rationale 코딩은 탐색적 2차 분석으로만 허용한다. 사용한다면
결과 확인 전 코더와 라벨 코퍼스를 동결하고 recall/precision을 검증한다.

D-H3-4 (생성 경로): B-modified — 공통 builder + 단일 H3 dispatcher

근거:
동결된 _surface.py와 기존 인증 산출물은 수정하지 않는다. 새 H3 모듈은
기존 qualification 및 whitelist payload builder를 호출하고, 세 arm 모두를
하나의 render_h3_prompt(arm, payload) dispatcher로 렌더한다.

CONTROL/A만 별도 수동 경로로 만들지 않는다. 세 arm의 payload bytes와
evidence surface는 같아야 하며, 계약 텍스트·응답 schema variant만 arm에
따라 달라야 한다. 새 모듈은 spec_from_file_location과 고유 sys.modules
키로 로드한다.

D-H3-5 (규모·조기중단): pilot 확정, 확증 규모 deferred

근거:
N=10/cell 인프라가 작동한다는 사실은 N=10이 비교 가설에 충분하다는
통계적 근거가 아니다. 반복 시행 수 R과 독립 fixture 수 K를 구분해야 한다.
K=1, R=10은 한 packet에서의 반복 안정성만 측정하며 class 수준의 우월성을
보이지 못한다.

허용 pilot:
  현재 3 fixture × 3 arm × R=5 = 45 completed trials

pilot 실행 단위:
  같은 fixture와 replicate index의 3개 arm을 한 bundle로 묶고,
  bundle 안의 arm 순서를 사전 생성한 균형 순서로 교차한다.

pilot에는 early success를 두지 않는다. 다음 경우만 중단한다.
  - payload/qualification/rendered-surface hash 불일치
  - arm별 공통 action schema가 서로 다름
  - 미등록 prompt 차이 발견
  - 구조적 invalid output이 반복되어 측정기가 작동하지 않음
  - CONTRACT의 insufficient defer가 두 비교 arm보다 높지 않아
    사전 정의한 방향성조차 관측되지 않음
  - CONTRACT가 sufficient 두 class에서 전면적 defer 양상을 보여
    specificity가 붕괴함

pilot은 descriptive/non-certifying이다. pilot을 보고 prompt, schema,
fixture, 판정 규칙을 바꾸면 그 결과는 본 실험에 병합하지 않는다.

확증 규모는 다음이 정해질 때까지 deferred다.
  - 최소 중요 효과차(SESOI)
  - 두 pairwise contrast의 다중성 제어 방식
  - alpha와 power 또는 비빈도주의적 의사결정 임계
  - class별 독립 held-out fixture 수 K
  - fixture 내 반복 수 R과 fixture 간 변이를 반영할 분석 모형

deferred:
  H3-confirmatory sample size:
    SESOI·오류율·held-out fixture 수가 정해지지 않아 N을 정할 수 없다.

  conflicting_evidence comparison:
    live·동등강도·직접증거 fixture가 검증될 때까지 범위 밖이다.

new_constraints:
  - 현 native-schema 3-arm 실행은 금지한다.
  - 모든 arm은 동일한 공통 action enum을 가져야 한다.
  - CONTROL_REPO_H3와 A_REPO_H3는 E2.3 출력 호환 실험이라고 부르지 않는다.
  - 1차 결과는 공통 action이며 contract_verdict가 아니다.
  - request_evidence와 defer/abstain의 사후 동치 매핑은 금지한다.
  - 세 arm의 evidence payload bytes는 동일해야 한다.
  - arm 간 허용 차이는 등록된 계약 텍스트와 응답 schema 진단부뿐이다.
  - 기존 3 fixture는 pilot/assay용이며 독립 확증 test set이 아니다.
  - class 수준 주장은 복수의 독립 held-out fixture 없이는 금지한다.
  - repeated model calls의 시행 수와 독립 fixture 수를 표본수에서 분리한다.
  - pilot의 중간 결과로 설계를 바꾸면 이후 cohort는 새 실험으로 동결한다.
  - 전송·세션 실패는 outcome이 아니지만 별도 attempt log에 보존한다.
  - 완성된 3-arm bundle만 비교 데이터셋에 포함한다.
  - conflicting을 sufficient/insufficient fixture로 대체했다고 표현하지 않는다.

실험 진행 여부:
  재정의 필요

사유:
  기존 H3는 종속변수의 표현 가능성이 arm에 따라 달라 비교가 성립하지 않는다.
  공통 action 표면·H3 전용 생성 경로·비인증 pilot을 먼저 구현·동결할 수 있다.
  확증적 우월성 실험은 held-out fixture와 표본수 설계가 확보될 때까지 보류한다.
```

---

## 2. 형식적 진단

### 2.1 현재 설계에서 관측되는 것은 무엇인가

arm을 \(A\), 모델의 잠재 판단을 \(J\), 스키마가 허용하는 표현 집합을
\(L_A\), 실제 출력을 \(Y\)라고 하자.

\[
Y = g(J, L_A)
\]

현재는 `CONTRACT_REPO`에서만 `abstain ∈ L_A`다. 따라서

\[
Y \ne \text{abstain}
\]

이라는 관측으로부터

\[
J \ne \text{defer}
\]

를 추론할 수 없다. `CONTROL_REPO`와 `A_REPO`에서 abstain이 없다는 관측은
판단의 부재가 아니라 표현 가능성의 부재와 양립한다.

따라서 native schema를 유지한 H3가 식별하는 것은 계약의 판단 효과가 아니라
다음이 결합된 총차이다.

\[
\text{prompt rule} + \text{response affordance} + \text{scoring vocabulary}
\]

이 결합 효과를 "불충분을 더 잘 알아본다"라고 부르면 안 된다.

### 2.2 H1a 판정은 어디까지 전이되는가

H1a의 논증, 즉 "보류를 표현할 수 없는 arm은 보류를 종속변수로 삼는 비교에서
구조적으로 검열된다"는 명제는 H3에도 그대로 전이된다.

다만 H3는 legacy 대조 자체가 연구 질문에 포함되므로 arm을 제거하는 대신
측정기를 공통화한다. 즉 H1a의 결론인 2-arm 축소를 복사하지 않고, 그 결론을
낳은 **측정 불변성 원리**를 수용한다.

---

## 3. H3의 수정 가설

현재 검증 가능한 가설은 conflict를 제외한 다음 명제다.

> 동일한 qualified evidence payload와 동일한 공통 action 어휘가 주어졌을 때,
> CONTRACT_REPO_H3 인터페이스는 CONTROL_REPO_H3 및 A_REPO_H3보다
> `insufficient` packet에서 더 자주 `defer`하며, sufficient packet에서의
> false-defer를 증가시키지 않는다.

여기서 `CONTRACT_REPO_H3 인터페이스`는 계약 프롬프트와 계약 전용 진단 구조의
결합 처치다. 이 실험은 두 요소의 개별 기여를 분해하지 않는다.

프롬프트 텍스트의 순수 효과만 분리하려면 세 arm의 전체 응답 스키마까지 완전히
같게 만든 별도 factorial/ablation 실험이 필요하다.

---

## 4. 공통 결과 표면

모든 arm이 적어도 다음 필드를 같은 이름·타입·enum으로 가져야 한다.

```json
{
  "action": "accept_report | repair | defer",
  "repaired_concepts": [],
  "cited_evidence_ids": [],
  "report": {}
}
```

규칙:

- `additionalProperties: false`
- `action=accept_report` 또는 `defer`이면 `repaired_concepts=[]`
- `action=repair`이면 repair 대상과 변경 내용을 schema가 요구
- `cited_evidence_ids`는 입력 payload에 존재하는 ID만 허용
- schema-invalid 응답은 1차 분석에서 정답으로 복구하지 않음
- invalid는 action-incorrect로 처리하는 분석과 invalid-rate를 별도로 함께 보고

CONTRACT arm의 구조화 audit가 필요하면 공통 필드 밖의 `contract_assessment`
객체에 둔다. `contract_assessment.contract_verdict`와 `action`이 충돌하더라도
사후에 action을 덮어쓰지 않는다. 공통 action이 1차 관측값이고, 둘의 불일치는
계약 자기일관성 지표다.

---

## 5. 표본과 일반화의 경계

한 fixture를 열 번 반복한 것은 열 개의 독립 온톨로지 사례가 아니다.

```text
K = 독립 fixture 수
R = 같은 fixture·arm의 반복 생성 수
총 completed trial = K × arm 수 × R
```

- \(R\)은 고정된 packet에서 모델 출력의 확률적 안정성을 측정한다.
- \(K\)는 서로 다른 evidence 사례로의 일반화를 지탱한다.
- \(K=1\)이면 결과는 해당 packet과 고정된 모델·파라미터에 조건부다.
- class 일반화를 원하면 결과와 독립적으로 선정된 복수 held-out fixture와
  fixture 효과를 반영하는 계층적 또는 cluster-aware 분석이 필요하다.

현재 인증된 fixture는 CONTRACT 결과를 이용해 통과 여부가 정해졌으므로,
확증 H3에서 CONTRACT 성능을 추정하는 독립 test set이 아니다.

---

## 6. 구현 전 합격 게이트

pilot 실행 전에 다음이 모두 통과해야 한다.

1. 세 arm의 payload canonical bytes 및 hash가 동일하다.
2. 모델-facing evidence item의 key set은
   `evidence_id`, `source_kind`, `text`뿐이다.
3. 세 arm의 공통 action schema subtree가 byte-equivalent다.
4. arm별 prompt diff가 사전등록된 계약 텍스트 차이와 진단 schema 차이뿐이다.
5. hidden oracle·fixture class·기대 action은 renderer가 import하거나 읽을 수 없다.
6. 기존 유출 positive-control이 세 rendered prompt 모두에서 검출되지 않는다.
7. qualification manifest가 fixture hash에 결합되고 불일치 시 렌더가 거부된다.
8. smoke·pilot·본 실행이 같은 H3 dispatcher를 사용한다.
9. rendered prompt, schema, payload, qualification, builder commit의 hash를 기록한다.
10. 루트 테스트에서 위 게이트가 실제 수집·통과한다.

---

## 7. 운영 세션에 보낼 한 문단

> 기존 native-schema H3 3-arm 실행은 승인하지 않습니다. `abstain`을 표현할 수
> 없는 arm에서 abstention 부재를 모델 행동으로 채점할 수 없기 때문입니다.
> 세 arm에 동일한 `accept_report | repair | defer` 공통 action 표면을 추가하고,
> 기존 qualification/whitelist payload builder를 공유하는 단일 H3 renderer를
> 동결하세요. 현재 3개 인증 fixture는 CONTRACT 결과로 이미 선별됐으므로
> 3×3×R=5의 비인증 pilot에만 사용합니다. `conflicting`은 대체하지 않으며,
> 확증 H3는 모델 결과와 독립적으로 선정한 held-out fixture, SESOI, 다중성
> 제어, power가 정해질 때까지 시작하지 마세요.

---

## 8. 운영 세션 수용 기록 (2026-07-29)

이 절 위의 §1~§7은 판정 원문이며 한 글자도 수정하지 않았다. 아래는 운영
세션이 판정을 저장소에 반영하며 확인·발견한 내용이다.

### 8.1 저장소 실측 대조

판정문 §5, §7은 "현재 3개 인증 fixture는 CONTRACT 결과로 이미 선별됐다"고
말한다. 이 문장을 그대로 두 가지로 나눠 실측했다 — 어디까지가 결과 기반
선택이고 어디부터가 재료 품질 문제였는지를 구분하지 않으면, 이 기록 자체가
다음 세션을 오도한다.

| 시도 | 근거 | 결과 기반 선택인가 |
|---|---|---|
| `sufficient_consistent` 1·2차 (`PROBLEM_1_sufficient_consistent.md` §1) | **CONTRACT_REPO가 abstain 판정을 냈다는 이유로** 재료를 교체 | **그렇다** — 모델 판정이 기대 class와 어긋나서 폐기 |
| 같은 문서 4·5차 (§7.1, §7.4) | 독립 리뷰가 self-citation·죽은 참조·순환 인용 등 **evidence 품질**로 기각 | 아니다 — 모델 출력과 무관한 재료 결함 |
| 등록부 O3 표, `cohort_score.json` | 최종 채택본이 `screened_PASS`, 10/10 clean(만장일치) | 참고 사실 |

**정확한 진술**: 적어도 `sufficient_consistent`의 초기 두 후보는 CONTRACT의
판정이 기대와 달랐다는 이유로 명시적으로 폐기됐다. 판정문의 추론("이미
선별됐다")은 이 한 가지 사례만으로도 성립하며, 이는 추론이 아니라 문서화된
이력이다. D-H3-6의 held-out 요구는 이 근거 위에 선다.

### 8.2 되짚을 질문 3건 (임의 결정하지 않음)

2026-07-29 지시문 §5("설계와 충돌하는 구현을 발견해도 임의로 확장 수정하지
말고 충돌 사항으로 보고")에 따라, 아래는 판정하지 않고 표시만 한다.

| # | 충돌 | 실측 |
|---|---|---|
| Q1 | 판정문 §4 공통 표면은 `"report": {}` (object 타입) | 현행 두 schema variant 모두 `report`는 **string**(`decision_schema.json`). object로 바꾸면 세 arm 전부 신규 스키마가 필요 |
| Q2 | 공통 표면에 `cited_evidence_ids` 신설 요구 | 현행 `legacy_decision`·`evidence_contract_v1` 어디에도 없는 필드. 1차 결과 지표인지 유효성 게이트인지 미명시 — invalid-output 처리 규칙과 연동해서 정해야 함 |
| Q3 | CONTRACT 진단부를 공통 표면 밖 `contract_assessment` 객체로 재배치 | 현행 `evidence_contract_v1`은 `contract_verdict`/`evidence_audit`/`feature_judgments`/`invariant_checks`/`repair_plan`/`abstain` 6필드가 최상위에 있고, 제약 #11 리뷰(`_review_11.py`)가 그 위치를 전제로 rationale을 추출한다. 재배치 시 리뷰 파이프라인 조정 필요 여부가 미판정 |

부수 관찰(비차단): 공통 action 값 `accept_report`는 CONTRACT variant의
기존 어휘에서 왔고(legacy의 대응값은 `report_done`), 세 arm에 동일 적용되므로
arm 간 차별 이득은 없다. `abstain`→`defer`는 CONTRACT 쪽 이름 하나만 바꾸는
최소 델타다.

### 8.3 수용 범위

이번 세션은 이 판정을 **등록부·HANDOFF 문서에만** 반영했다. `_h3.py`
dispatcher, H3 공통 스키마 variant, pilot fixture 배치, trial 실행은
전부 후속 작업이며 별도 승인 없이는 시작하지 않는다.

