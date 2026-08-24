# Gate C 사람 감사 — MRS 기수·비례 후보 (2026-08-24)

- 정본 관계: [[concept-gate-h1-wt/docs/DESIGN_DECISION_mrs_fail_closed_and_rights|D-E2E-v1-30]] Q30.6 · D-29 §17
- 감사 방식: **집계가 아니라 실물 READ**. 사용자 지시 "Gate C도 직접 READ해라".
- 표면 원문은 **이 문서에 넣지 않는다** — Q30.4(저장소에는 sha256만) + 사용자
  결정(외부 배포 없음). 문장은 로컬 캐시에서만 읽는다. 아래는 sha256과
  **구성 유형**뿐이고, 구성 유형은 재현이 아니라 분석이다.

## 감사 결과

| case_id | surface (sha256) | MRS 술어 | 양화 술어 | 층 | verdict |
|---|---|---|---|---|---|
| MRS-20413069 | `75236ada…` | card | `udef_q` | cardinal | **CONSISTENT** |
| MRS-20490024 | `89582732…` | card | `_all_q` | cardinal | **STRATUM_QUANTIFIER_MISMATCH** |
| MRS-20725062 | `534d173c…` | card | `udef_q` | cardinal | **CONSISTENT** |
| MRS-21603011 | `932d95d0…` | card | `_both_q` | cardinal | **STRATUM_QUANTIFIER_MISMATCH** |
| MRS-21618050 | `67e11e34…` | card | `udef_q` | cardinal | **CONSISTENT** |
| MRS-22111024 | `de23d56f…` | card | `_both_q` | cardinal | **STRATUM_QUANTIFIER_MISMATCH** |
| MRS-22141002 | `fcd84e7a…` | card | `_both_q` | cardinal | **STRATUM_QUANTIFIER_MISMATCH** |
| MRS-20214052 | `9965ba77…` | `_most_q` | `_most_q` | proportional | **CONSISTENT** |

`total: 8 · mismatch: 4 · gate: HUMAN_AUDIT_REQUIRED`

## 기각 사유 — `both`/`all N`은 기수 양화가 아니다

`_both_q + card(2)` 3건과 `_all_q + card(4)` 1건을 기각한다.

`both`는 "정확히 둘이 존재한다"가 아니라 **전제된 2원소 집합에 대한 한정·보편**
이다. `count(eq,2)`로 옮기면 존재 주장으로 바뀌고 한정성·보편성이 사라진다.
`all four`도 **보편 + 기수 주장의 결합**이고 `count`로는 보편이 소실된다.
둘 다 D-27/D-28이 금지한 **힘을 바꾸는 재작성**에 해당한다.

우리 방언 8종에는 한정성·보편+기수 결합을 표현할 구성자가 없다. 따라서
이 4건은 **재료가 아니라 방언 공백의 증거**다 — 층 재배정이나 방언 확장은
판정 사안이므로 여기서 결정하지 않는다.

## 표가 못 보던 것 (그리고 고친 것)

첫 실행에서 표는 **8/8 CONSISTENT**를 냈다. 층 결정 술어(`card`)의 **존재**만
대조했기 때문이다. 사람 READ가 4건을 기각했고, 그 차이가 `GATE_C_AUDIT_TABLE_V1`
의 공백을 지목했다 — **공기하는 양화 술어를 보지 않았다.**

`quantifier_predicate` 열과 `_STRATUM_QUANTIFIERS` 양립성 검사를 추가해
표의 mismatch 4건이 사람 판정과 **일치**하게 됐다(계약 8건 추가, 24/24 통과).
표는 여전히 **판정하지 않고 표시**한다 — `assigned_stratum`은 그대로 두고
verdict만 붙인다. 층 재배정은 판정 사안이다.

이것이 판정이 Gate C를 `HUMAN_AUDIT_REQUIRED`로 둔 이유의 실증이다:
표가 초록이어도 사람이 봐야 한다. 그리고 사람이 본 것을 **표에 되먹여야** 한다.

## 이번 감사가 만든 edge case 원장

전 코퍼스(37,060 파싱) 재스캔에 다음 배제 규칙을 적용했다.

| 코드 | 정의 | 적발 | 근거 |
|---|---|---|---|
| E0 | 승수/측정 구문 — `card.LBL ≠ QEQ해소(RSTR)` | 6,185 | `$1.5 billion`에서 `card(1000000000)`이 자기 label에 혼자 있고 RSTR target에는 `times`·`_dollar_n_1`. 진짜 기수는 `card`가 **명사와 label을 공유**한다 |
| E1 | `unknown_rel` 보유 — ERG가 완전한 발화로 분석하지 못한 fallback | **4** | `Guaranteed minimum 6%.` 류 캡션 조각. gold 분석이 아니라 분석 실패 표지다 |
| E2 | 측정 명사 제한식(`_percent_n_of` 등) | 0 (E1이 선행 적발) | `count(eq,6,x,percent(x),…)` = "정확히 6개의 퍼센트가 존재한다"가 되어 틀린다 |
| E3 | 미사상 관계 수식어(`_minimum_a_1` 등)가 card와 label 공유 | 0 (E1이 선행) | "minimum 6%"는 `ge`인데 사상표에 없어 시제품이 **`eq`로 오배정**했다. 그대로면 틀린 oracle |
| E4 | 중복 item(MRS 바이트 동일) | 0 (E1이 선행) | `20056005`·`21771005`가 표면·MRS 완전 동일 — 별개 fixture로 세면 N이 부풀고 독립성이 깨진다 |
| E5 | 본문에 채점 가능한 내용 없음 | 0 | 투영 신호 게이트와 중복 방어 |
| E7~E10 | 빈도 · 부분격 · 분수 수사 · 다중 문장 record | — | PMB 감사(`GATE_C_PMB_AUDIT_20260824.md`)가 추가. MRS 쪽에도 적용해야 한다 |
| **E6** | **층과 양립하지 않는 양화**(`_both_q`·`_all_q` + card) | **4** | 이 감사가 발견. 위 기각 사유 참조 |

## 현재 재료 수량 (잠정 — 계약 결박 후 재산출이 정본)

| 층 | 하한 | 적격 | 여유 |
|---|---|---|---|
| cardinal | ≥3 | **3** | **0** |
| proportional | ≥1 | **1** | **0** |

PMB 쪽 전수 감사 결과 **PMB는 기수·비례를 원리적으로 공급하지 못한다**
(부호 없는 수사 106건 전부가 배제 사유). 따라서 MRS가 **유일한 공급원**이다.

**여유가 0이다.** 계약 구현 후 재스캔에서 한 건이라도 더 탈락하면 하한이
깨진다. `rel`은 3건 전부 `eq`이므로 `rel_coverage: {eq:3, ge:0, gt:0, le:0, lt:0}`
— "`count.rel` 전체를 검증했다"고 주장할 수 없다(D-30 Q30.3의 공개 요구).

---

# 추기 (같은 날) — 배제 규칙의 공허성 검사와 생존 4건 전문 READ

## A. 배제 규칙이 공허한지 — E1 없이 독립 실행

첫 재스캔에서 E2·E3·E4·E5가 전부 0건이었고 이유는 **E1이 먼저 잡았기 때문**
이었다. 저장소 규율("정상 가드와 공허한 가드의 관측값이 동일하다")에 걸리므로
각 규칙을 **cascade 없이** 독립으로 돌렸다.

| 규칙 | 독립 실행 결과 | 실물 예 |
|---|---:|---|
| E2 측정 명사가 `card`와 label 공유 | **9,758** | `_year_n_1`·`_percent_n_of`·`_point_n_of` |
| E3 관계 수식어가 `card`와 label 공유 | **297** | `_about_x_deg`·`_over_p`·`_at+least_x_deg` |
| E4 MRS 바이트 동일 중복 | **428** | `20052003`≡`20050002` 등 |
| E5 본문 내용 없음 | 미검사 | — |

**세 규칙은 공허하지 않다.** E4의 428건은 별개 문제도 만든다 — 중복을 제거
하지 않으면 **fixture 독립성이 깨진다**(같은 문장이 두 trial로 셈된다).

### A.1 E3의 정의 오류를 이 검사가 잡았다

E3을 "관계 수식어가 있으면 배제"로 돌리면 `_at+least_x_deg`도 배제된다.
그러나 그것은 **사상 대상**(`ge`)이고 배제 대상이 아니다(D-30 Q30.3).
E3의 정본 정의는 **"사상표에 없는 수식어"** 이며, 이 검사가 그 구분을 강제했다.

## B. `ge`/`gt` 재료의 전수 열거 — **0/78이 게이트를 통과한다**

사상 가능 수식어(`_at+least_x_deg`·`_more+than_p`)가 `card`와 label을 공유하는
경우는 **78건**이다. label 일치는 78/78 통과하지만 **BODY 유일성은 0/78**이다.
사유는 전부 `BODY 모호`(다중 양화)다. 표면을 읽으면 원인이 명확하다:

- `The plan calls for closing at least nine plants and eliminating about 3,600 jobs.`
- `The warnings, issued to at least 100 criminal defense attorneys in several major cities …`

**구조적 긴장이 측정됐다**: `BODY_resolved`(유일 해소)는 우리를 **단일 양화
문장**으로 제한하는데, 관계 다양성(`at least N`)은 **다중 양화 문장에만**
나타난다. 두 요구가 같은 재료에서 동시에 만족되지 않는다.

따라서 `rel_coverage: {eq:3, ge:0, gt:0, le:0, lt:0}`은 표본 추정이 아니라
**전수 열거로 확정된 값**이다. D-30 Q30.3의 공개 요구를 이 형태로 이행한다.

## C. 생존 4건 MRS 전문 READ

| item | 채점 제한식 | 본문 | 특기 사항 |
|---|---|---|---|
| `21618050` | `card(2)`+`_irony_n_1` (크기 1) | `_intrude_v_1` | 가장 깨끗함 |
| `20725062` | `card(5)`+`generic_entity` (크기 1) | `_interested_a_in` | 표면에 **인용부호** 포함 — 프롬프트 텍스트에 그대로 들어간다 |
| `20214052` | `generic_entity` (크기 1) | `_trim_a_1` | Q30.6으로 적격 확정 |
| `20413069` | `card(2)`+**`_previous_a_1`**+**`_exorcisms/NNS_u_unknown`** (크기 **2**) | `_fail_v_1` | 아래 C.1 |

### C.1 `20413069`의 제한식 크기 2 — 기각하지 않는다

투영 실측: subject가 형용사를 **포함하면 일치**, **빼면 불일치**다. 즉 이
fixture는 "수식어를 제한식에 넣었는가"를 함께 채점한다.

기각 여부를 정하려면 **그것이 신규 결함인지 기존 코호트의 성질인지**가 갈린다.
동결된 V4의 PMB 15건을 adapter로 재생해 투영 후 크기를 측정했다:

| fixture | 표면 | (제한식, 본문) |
|---|---|---|
| `PMB-p43-d3444` | Is everything you own in that chest? | **(2, 1)** — 관계절 |
| `PMB-p00-d1657` | Everybody except Joe went to the party. | **(2, 1)** — 예외구 |
| 나머지 13건 | — | 제한식 0 또는 1 |

**다중 술어 제한식은 이미 동결 코호트에 있다.** `20413069`은 크기가 같고
종류로는 관계절·예외구보다 온건하다(형용사 1개). 따라서 **기각 사유가 아니며
기수는 3건을 유지한다.**

단 이것은 **기존 설계의 교란을 기록해 둔다**: 코호트는 이미 머리명사를 넘는
제한식 내용(관계절·예외구)을 채점하고 있고, 거기서의 실패가 `O1ScopeMatch`
= scope 컴파일 능력으로 귀속된다. 동결 표면이므로 고치지 않고 기록한다.

### C.2 신규 표지 2건

- **E12 `_u_unknown`** — ERG가 어휘를 미지로 처리했다는 표지(`_exorcisms/NNS_u_unknown`).
  E1(`unknown_rel`, 발화 전체 분석 실패)보다 약하고 구조는 온전히 분석돼
  있으며 라벨은 익명화되므로 **기각하지 않되 Gate C에 표시**한다.
- **인용부호 표면** — `20725062`의 원문에 `"`가 포함된다. 프롬프트에 그대로
  들어가므로 subject가 인용 표지를 의미로 옮기려 할 수 있다.

## D. 이 추기가 만든 측정 교훈

측정기가 **두 번 틀렸고 두 번 다 잡혔다**. 두 번째: PMB 15건의 제한식 크기를
`restriction` 필드로 셌더니 **15/15가 0**이었다 — desugar가 제한식을
`implies.left`로 옮기므로 그 필드는 `True`다. 15개 이질적 fixture가 전부 0인
것이 불가능하다는 판단으로 재측정했다.

**규칙**: 이질적 입력에서 균일한 결과가 나오면 측정기를 먼저 의심한다.
0건은 발견이 아니라 **측정기 점검 신호**다.
