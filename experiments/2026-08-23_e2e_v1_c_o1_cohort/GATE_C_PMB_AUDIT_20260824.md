# Gate C 사람 감사 — PMB 기수·비례 (2026-08-24)

- 짝 문서: `GATE_C_MRS_AUDIT_20260824.md` (MRS 쪽 감사)
- 정본: [[concept-gate-h1-wt/docs/DESIGN_DECISION_mrs_fail_closed_and_rights|D-30]] · D-28 §G1
- **표면 원문을 인용한다.** PMB는 Tatoeba/**CC-BY**이므로 귀속과 함께 재배포
  가능하다 — WSJ와 다르다. Q30.4의 `sha256` 정책은 **WSJ/LDC 재료에 대한
  것**이고, 표면 공개 여부는 **source별**로 갈린다(전역 기본값이 아니다).
  이것이 `surface_display`에 기본값을 두지 않은 설계가 옳았던 두 번째 이유다.

## 1. V4 동결 fixture 중 cardinal 3 · proportional 1 — **4/4 기각**

manifest V4는 `cardinal: 3`, `proportional: 1`을 이미 배정하고 있었다.
D-28이 층 술어 결함(G1)을 고친 뒤 그 배정이 무효가 됐으나 **Gate C 표를
한 번도 돌리지 않았다.** 실물을 읽었다.

| case_id | 표면 | SBN 실물 | 판정 |
|---|---|---|---|
| PMB-p09-d2243 | The **most beautiful** flowers have the sharpest thorns. | `most.r.01`이 **부사**로 `beautiful.a.01`을 수식(`Degree`), 같은 술어가 `sharpest`용으로 한 번 더 | **REJECT — 최상급** |
| PMB-p69-d1730 | I met Tom **a few** months ago. | `month.n.01 Quantity -` | **REJECT — 수치 없음** |
| PMB-p36-d3354 | There are **few** passengers on this train. | `person.n.01 Quantity -` | **REJECT — 수치 없음** |
| PMB-p43-d3167 | Tom's essay had **many** typos. | `typo.n.01 Quantity +` | **REJECT — 수치 없음** |

비례 fixture는 **G1이 잡으려던 최상급 오탐 그 자체**였다. 기수 3건은 SBN이
수량을 **극성 표지 `Quantity -`/`+`**(막연한 소/다)로 인코딩하므로 우리
`count`의 `num: int`를 채울 값이 존재하지 않는다.

## 2. 그렇다면 PMB가 기수를 **공급할 수** 있는가 — 전수 실측

PMB gold en **12,053건**의 SBN에서 `Quantity` 표기를 전수 census했다.

`Quantity -1`/`+1`/`-2`는 SBN의 **상대 노드 참조**이고 `-`/`+`는 막연 표지다.
진짜 수사는 **부호 없는 정수**뿐이며 그것이 **106 occurrence**다. 전부 분류:

| 코드 | 유형 | 건수 | 실물 예 |
|---|---|---:|---|
| E0 | 측정·단위 | **67** | `I'm thirty.` → `measure.n.02 Quantity 30 Unit year.n.01` · `500 miles per hour` · `per annum` · `a head taller` |
| E6 | `both` | **19** | `I got slapped on both cheeks.` → `cheek.n.01 Quantity 2` + `entity.n.01 SubOf` |
| E10 | 다중 문장 record | **9** | `winning 25 of the 63 seats` (2문장 document) |
| E8 | 부분격 `N of the X` | **8** | `Three of the rooms face the street.` · `Two of them pleased me` |
| E9 | 분수/비례 수사 | **3** | `Two-thirds of the students came` · `Three-fourths of the town was destroyed` |
| E7 | 빈도 | (E0에 흡수) | `I've attempted suicide twice.` → `time.n.01 Quantity 2` (`Frequency` 역할) |
| — | **잔존 후보** | **0** | — |

**결론: PMB는 기수·비례를 원리적으로 공급하지 못한다.** 표본이 아니라 전수다.
따라서 MRS/Open SDP가 **유일한 공급원**이고, 그쪽 여유 0(기수 3·비례 1)이
그대로 하한을 결정한다.

## 3. 동결 commitment 재검증 (부수 확인)

PMB 15건 전부 **단일 문장**이고 **`text_sha256` 15/15 일치**. E10은 기존
fixture에 걸리지 않으며 V4 commitment는 온전하다.

## 4. 이 감사가 추가한 edge case

| 코드 | 정의 | 왜 필요한가 |
|---|---|---|
| **E7** | 빈도/횟수 수량(`twice` → `time.n.01 Quantity 2`) | 사건·시각을 세는 것이지 개체 영역의 기수가 아니다 |
| **E8** | 부분격 `N of the X` | 제한식이 **한정 집합**이고 우리 방언에 한정성이 없다. `both`와 같은 계열의 약한 형태 |
| **E9** | 분수/비례 수사(`two-thirds`) | 수사가 있으나 표현은 비례다. `prop.rel`은 v1에서 `most`뿐 |
| **E10** | 다중 문장 record | PMB 단위는 document다 — 문장 단위 1:1이 깨진다 |
| E0 확장 | 단위 명사를 `measure.n.02`에 한정하지 말 것 | `hour`·`mile`·`meter`·`dollar`·`size`·`annum`·`head`가 전부 단위로 쓰였다. 좁게 잡으면 35건이 후보로 새어 나온다 |

E0을 좁게 잡았을 때 후보가 35건으로 부풀었고, 그 35건을 **직접 읽어** 전부
단위/부분격/분수/다중문장임을 확인한 뒤 규칙을 넓혔다. **집계는 35건을
"후보"라고 말했고 READ가 0건이라고 말했다.**
