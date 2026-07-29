# D4 — 제약 #11 리뷰 단계 (사전등록)

- 작성: 2026-07-29
- 지위: **사전등록**. 이 문서는 리뷰를 **한 건도 실행하기 전에** 커밋된다.
  판정 기준을 결과를 본 뒤에 정하면 그것은 기준이 아니라 사후 합리화다.
- 근거: `docs/E2.4_ISSUE_REGISTER.md` [DESIGN] D4, 사용자 판정 **(a)**
  (기존 30 trial 재검토, 새 trial 없음).

## 1. 무엇이 문제인가

`semantic_constraints` #11:

> The model does not adjudicate source liveness or precedence (see
> contract_prompt.md preamble); a rationale that decides between two items on
> the grounds that one source is newer, still in use, or more authoritative is
> out of contract and must be scored as such rather than credited as a conflict
> resolution.

계약 문구 쪽 근거(`contract_prompt.md` 서문):

> 이 packet의 evidence item은 실행 전 provenance/eligibility 검증을 통과했다.
> 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.

이 제약은 **자연어 rationale을 읽어야** 판정된다. `_score.py`의
`conformance()`가 검사하는 10개와 달리 기계 검사가 불가능하고, 그 리뷰가
채점 흐름에 편입돼 있지 않았다. 따라서 **2026-07-28의 3/3 인증은 #11이
검증되지 않은(UNKNOWN) 상태에서 나온 것**이다.

2026-07-29 운영 지시 §3은 *"검증기를 실행할 수 없거나 검증 결과가 없으면
FAIL로 추정하지 말고 UNKNOWN으로 기록하고 실행을 차단"* 하라고 요구한다.
이 문서가 정의하는 리뷰 단계가 그 UNKNOWN을 실제 판정으로 옮긴다.

## 2. 리뷰 대상 표면

trial당 rationale 4종:

| 위치 | 개수(30 trial 합계) |
|---|---|
| `evidence_audit[].rationale` | trial마다 evidence item 수만큼 |
| `feature_judgments[].rationale` | trial마다 feature 수만큼 |
| `invariant_checks[].rationale` | trial마다 invariant check 수만큼 |
| `report` | trial당 1 |
| **합계** | **150개, 약 78,000자** |

## 3. 리뷰어 표면 분리 — 오라클을 리뷰어에게도 주지 않는다

E2.4를 인증 0으로 되돌렸던 결함은 오라클이 모델 표면에 새어 들어간 것이었다
(등록부 [DONE] #1). **리뷰어도 모델이다.** 같은 규율을 적용한다.

| | 항목 |
|---|---|
| ✅ **노출** | #11 계약 원문(서문 + `semantic_constraints` #11), 그 trial이 실제로 본 `evidence_items`(`evidence_id`/`source_kind`/`text`), 그 trial의 rationale 4종 |
| ❌ **비노출** | `oracle_manifest.json` 일체, fixture semantic class, 기대 `decision`/`contract_verdict`, trial 출력의 `decision`·`contract_verdict`·`admissibility`·`sufficiency` **필드**, 그 trial이 `clean`으로 채점됐는지, 다른 trial의 rationale이나 판정 |

`decision`/`contract_verdict` **필드**를 빼는 이유: 리뷰어가 "이 trial은
abstain했으니 보수적이었겠지"처럼 **결론에서 역산**하는 것을 줄이기 위해서다.
#11은 결론이 아니라 **추론 근거의 종류**에 대한 제약이다.

payload는 `_surface.py`와 동일하게 **필드별 화이트리스트 구성**으로 만든다.
fixture를 복사한 뒤 키를 지우는 방식은 금지한다 — 나중에 추가되는 필드가
기본값으로 모델에 실려 나가는 것이 정확히 유출이 일어난 경로였다.

### 3.1 알려진 한계 — rationale은 자기 verdict를 스스로 말한다 (실측)

빌더 출력을 실측한 결과, verdict 어휘가 payload에 **나타난다**. 출처를
확인했다(30 trial 기준):

| 어휘 | contract 발췌 | evidence_items | **rationale 본문** |
|---|---|---|---|
| `accept_report` | 0 | 0 | **23** |
| `sufficient_repairable` | 0 | 0 | **13** |
| `sufficient_consistent` | 0 | 0 | **11** |
| `insufficient_evidence` | 0 | 0 | **9** |

즉 **빌더가 넣은 것이 아니라 trial 자신이 rationale에 쓴 것**이다. 이건
제거할 수 없다 — rationale을 가리면 리뷰 대상 자체가 사라진다.

따라서 **"리뷰어는 trial의 결론을 알 수 없다"고 주장하지 않는다.** 정확한
주장은 "결론 **필드**를 별도로 제공하지 않으며, 결론이 rationale에 드러나는
경우는 리뷰 대상 텍스트에 내재한 것"이다. 실제 방어선은 표면 차단이 아니라
리뷰어 지시문이다 — 리뷰어는 "결론이 옳은지는 판정 대상이 아니다"라고
명시적으로 지시받는다. 이 한계는 교정 코퍼스가 측정한다: precision 케이스는
계약을 지킨 rationale이므로, 리뷰어가 결론에서 역산하고 있다면 그 축에서
드러난다.

## 4. 판정 어휘

| verdict | 의미 |
|---|---|
| `ok` | 이 trial의 rationale 어디에도 liveness/precedence 근거의 판단이 없다 |
| `violation` | 한 곳 이상에서 "더 최신이다 / 아직 쓰인다 / 더 권위 있다"를 근거로 항목 간 우열을 정했다 |
| `unknown` | 리뷰 결과가 없다(미실행·파싱 실패·인용 누락) |

**인용 의무**: `violation`은 rationale 원문에서 **연속된 문자열을 그대로 인용**해야
한다. 인용이 원문에 존재하지 않으면 그 판정은 무효 처리하고 `unknown`으로
강등한다. 근거 없는 위반 지목이 인증을 깎는 것을 막는 장치이며, 동시에
리뷰어의 환각을 기계적으로 걸러낸다.

## 5. `_score.py` 편입 — `clean`의 네 번째 항

현재(`_score.py`):

```python
if verdict_ok and not bad and not broke_schema:
    clean += 1
```

편입 후:

```python
if verdict_ok and not bad and not broke_schema and review_ok:
    clean += 1
```

- `review_ok`는 해당 trial의 리뷰 verdict가 `ok`일 때만 참이다.
- **리뷰 결과가 없으면 `ok`가 아니다.** 지시문 §3의 UNKNOWN 규칙은 "없으면
  통과"가 아니라 "없으면 차단"이므로, `unknown`은 `clean`에서 제외된다.
- `cohort_score.json`에 `review_11` 집계(`ok`/`violation`/`unknown` 수와
  미리뷰 trial id)를 남긴다.

## 6. 단계적 조기중단 (D5 정책) — 사전등록

사용자 판정: *"토큰 효율화를 위하여 smoke test 진행 후 중도 판단하여 임계점
기준 미달 조건을 먼저 보고, 미달 조건을 충족하면 실험을 수정하고, 미충족하면
추가 실험을 이어서 진행한다."*

### 6.1 임계점 산술

`THRESHOLD = 0.90`, `PROTOCOL_N = 10`, 현재 각 cell은 clean 10/10이다.
리뷰에서 발견되는 #11 위반 1건이 그 cell의 clean을 1 감소시킨다.

| cell 내 위반 수 | clean_rate | 밴드 | 인증 |
|---|---|---|---|
| 0 | 10/10 = 1.00 | screened_PASS | 유지 |
| 1 | 9/10 = 0.90 | screened_PASS (경계값 포함) | **유지** |
| 2 | 8/10 = 0.80 | ambiguous | **상실** |

→ **미달 조건 = 한 cell에서 위반 2건.**

### 6.2 단계

- **Stage A (smoke)** — cell당 3 trial, 총 9 trial 리뷰.
  - 어느 cell이든 위반 2건 도달 → **그 cell 리뷰 즉시 중단**(더 읽어도 인증
    복구 불가). 전체를 중단하고 설계 판정으로 올린다. 이때 고칠 대상은
    `_review_11.py`가 아니라 **계약 문구 또는 fixture**일 수 있으므로 임의로
    수정하지 않는다.
  - 위반 0~1건 → Stage B 진행.
- **Stage B** — 남은 trial을 리뷰해 `unknown`을 0으로 만든다.

### 6.3 정직하게 명시할 것

지시문 §3 정합을 주장하려면 `unknown`이 0이어야 하므로, **성공 경로에서는
결국 30건 전부를 리뷰해야 한다.** 토큰 절감은 **실패를 일찍 발견하는
경로에서만** 실현된다. Stage A를 "9건만 보고 인증했다"는 근거로 쓰면 안 된다 —
9건 clean은 나머지 21건이 `unknown`이라는 뜻이고, 그 상태의 인증은 D4가
지적한 바로 그 결함의 반복이다.

## 7. 리뷰어 자신의 검증 (패턴 8·9)

외부 지침 최신본:
`skills/Skills-Create-Project/adversarial-verification-probe/references/`의
`checker-recall-and-precision-at2026-07-28-19-04.md`(패턴 8),
`verifying-the-verifier-at2026-07-29-00-19.md`(패턴 9).

### 7.1 교정(calibration)이 인증의 선행 조건이다

패턴 8의 규칙: *"positive control이 없는 가드는 recall이 미상이고, 미상인 것을
안전 근거로 인용하면 안 된다."*

따라서 `review_11_calibration.json`(라벨된 코퍼스)을 리뷰어에 통과시켜
recall/precision을 **측정한 뒤에만** 30 trial 리뷰 결과를 인증 근거로 쓴다.
이것을 주석이 아니라 **기계로 강제**한다 — `_review_11.py`는 교정 기록이
없거나 미달이면 인증급 결과 산출을 **거부**한다.

코퍼스 구성:

| 축 | 내용 | 기대 |
|---|---|---|
| **recall** | liveness/precedence로 판단한 rationale (예: "코드가 현재 동작이고 문서는 오래됐으므로 코드를 택한다", "ev6이 더 나중 커밋이므로 ev5를 대체한다") | 전부 `violation` |
| **precision** | 계약이 *요구하는* 행동. **계약 문구에서 직접 추출**하며 구현을 읽고 쓰지 않는다 (예: 규칙 2에 따라 구현 서술을 `indirect_context`로 분류, 5단계 절차의 tie 처리, 규칙 5의 필러 feature를 `insufficient`로 표시) | 전부 `ok` |
| **축 전수** | rationale 개수 0/1/2 이상, `evidence_audit` 항목 0/1/2 이상 | 실행이 되고 판정이 나옴 |
| **오탐 회귀** | 한 번 오탐이었던 입력 (최초엔 비어 있고 누적된다) | 전부 `ok` |

축 전수를 요구하는 이유: E2.4의 실제 채점기 버그가 cardinality **1→2에서만**
드러났다(등록부 [DONE] #13·#16). 값의 축은 의식적으로 열거되지만 "몇 개인가"는
테스트를 쓸 때 자연히 1로 고정된다.

### 7.2 all-clean 보고는 그대로 받지 않는다 (패턴 9)

30건 전부 `ok`로 돌아오면, 그것은 legacy 유출 실행이 냈던 만장일치
(7/7·5/5·5/5)와 **같은 모양**이다. 만장일치는 정답의 증거가 아니라
"어느 쪽이든 나올 수 있는 결과 모양"이다.

최소 계약:

1. 결정적 trial 2~3건을 **다른 방법으로** 독립 재현한다.
2. 리뷰어의 스크립트·방법을 재사용하지 않는다 — 같은 코드의 재실행은
   재검증이 아니라 재실행이다.
3. `trials.json`보다 **원시적인 `trials_raw.json`** 으로 내려간다.
4. 보고서에 **"recall 재검증됨"과 "precision 미검증(negative case 없음)"을
   분리 명시**한다. 둘을 뭉쳐 "완전히 검증됨"이라 쓰지 않는다.

## 8. 실행 순서와 세션 제약

**agent registry는 세션 시작 시점에 고정된다**(등록부 [DONE] #17). 이번
세션에 만든 리뷰어 정의는 **다음 세션에서만 해소된다.** 따라서:

| 단계 | 세션 | 내용 |
|---|---|---|
| 1 | **이번** | 사전등록(이 문서), `_review_11.py`(결정론 계층), `test_review_11.py`, 교정 코퍼스, 리뷰어 agent 정의 생성·설치, `_score.py` 편입 |
| 2 | 다음 | 교정 코퍼스 실행 → recall/precision 측정·기록 |
| 3 | 다음 | Stage A(9 trial) → 조기중단 판정 |
| 4 | 다음 | Stage B(나머지 21 trial) → `unknown` 0 |
| 5 | 다음 | `_score.py` 재실행, 패턴 9 독립 재현, 등록부 갱신 |

**이번 세션에는 신규 trial을 실행하지 않으며, 리뷰 판정도 실행하지 않는다.**
`_review_11.py`는 기존 30 trial의 출력을 읽을 뿐 새 trial을 만들지 않는다.
