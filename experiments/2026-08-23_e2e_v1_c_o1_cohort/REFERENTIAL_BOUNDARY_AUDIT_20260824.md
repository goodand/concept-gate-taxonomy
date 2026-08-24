# referential ∃ 경계 — Q34가 선언한 두 측정 한계를 닫는다 (2026-08-24)

- 성격: **재료 실사.** 경계를 제안하지 않는다 — D-33이
  `operational_patch: forbidden`이고 D-33-V가 "(b) directionally_plausible_but
  _**not_implementable**"로 재확인했다. 우리가 경계를 정하면 위반이다.
- 근거 문서: [[DESIGN_REQUEST_referential_existential_qualification|Q34]] §7이
  스스로 적은 한계 둘 — PMB 전수가 20건뿐 · FOLIO 상수 116건 미분류.
- 방법: 두 측정 모두 **닫힌 목록 밖은 "미결정"으로 남긴다.** 이 세션에 경계
  분류기를 네 번 만들어 네 번 다르게 틀렸으므로(D-33 §B.4), 분포를 기술하되
  판정하지 않는다.

## 1. PMB 전수 — 문제의 후보 표면은 **96%가 미결정**이다

gold **12,053 문서 전수**. 지시 후보 부류 synset(`male`·`female`·`person`·
`entity`·`thing`)이 붙은 개념 노드 **15,810개**의 표면 토큰 분포:

| 버킷 | 건수 | 예 |
|---|---:|---|
| (A) 표면 토큰 없음 — 비계·암묵 | 222 (1%) | `entity.n.01←''` · `male.n.02←''` |
| (B) **닫힌 양화 어휘** — 양측이 모두 양화한다 | 395 (2%) | `person.n.01←'Everyone'` · `entity.n.01←'Both'` · `entity.n.01←'anything'` |
| (C) **미결정** — 닫힌 목록 밖 | **15,193 (96%)** | `person.n.01←'You'` · `entity.n.01←'This'` · `person.n.01←'person'` · `entity.n.01←'and'` |

**닫힌 어휘가 해결하는 것은 2%뿐이다.** (C) 안에 고유명·대명사·지시사·보통명사가
섞여 있고, 그것을 가르는 것이 바로 D-33이 미정이라 한 경계다. 예시가 혼재를
그대로 보여준다 — `'You'`(대명사) · `'This'`(지시사) · `'person'`(보통명사) ·
`'and'`(**파싱 잔여**).

**Q34의 한계 ①이 닫혔다**: 이 현상은 표본 20건의 성질이 아니라 gold 전체에
걸친 15,810 노드의 성질이고, 작은 닫힌 목록으로는 2%만 처리된다.

## 2. FOLIO 전수 — 상수도 **깨끗한 집단이 아니다** (Q34 §1의 자기 정정)

적격 풀에서 상수를 쓰는 전제 **116건 전수**, 상수 출현 **160회**.

| 관측 특성 | 건수 | 예 |
|---|---:|---|
| (a) 기능어 — 파싱 잔여로 보인다 | 1 (0%) | `on`(598p4, "Ontario"의 잔여로 보인다) |
| (b) 숫자 포함 — 연도·대회명 | 12 (7%) | `summer1972olympics` · `year1990` · `year1915` · `number98199` |
| (c) 대문자 포함 | 11 (6%) | `newYork` · `johnNash` · `lawtonPark` · `athensOhio` |
| (d) 긴 복합어 | 28 (17%) | `portlandwhigs` · `mongolregion` · **`widereciever`** |
| (e) **미결정** — 소문자 단일어 | **108 (67%)** | `berlinzoo` · `portland` · `john` · **`music`** · **`stonefish`** |

**Q34 §1의 프레이밍을 정정한다.** 나는 "FOLIO gold는 지시 표현을 상수로
인코딩한다"고 썼다. 방향은 맞지만 집단이 깨끗하지 않다 — (b)(c)는 분명히
지시적이나 (d)에 `widereciever`(오타 난 보통명사)가 있고 (e) 67%에
`music`(물질명사)·`stonefish`(보통명사)가 섞여 있다. **FOLIO는 지시 표현이
아닌 것에도 상수를 쓴다.**

## 3. 이 실사가 D-34에 주는 것 — 경계는 **양쪽 corpus에서 다 미정의**다

Q34는 "두 source가 반대로 인코딩한다"를 핵심 논거로 냈다. 전수 실사는 그것을
**더 정확하게** 만든다:

```text
PMB    지시 표현 → ∃ 결박자        (과양화)   그러나 후보의 96%가 미결정
FOLIO  지시 표현 → 상수            (과소양화) 그러나 상수의 67%가 미결정
                                              그리고 보통명사·물질명사도 상수다
```

즉 두 규약은 **서로 반대 방향으로 어긋나 있고, 어느 쪽도 의미론적 경계를
따라가지 않는다.** "어느 source의 규약을 정본으로 볼 것인가"(Q34 §6(a))는
**두 규약 다 그 경계의 대리물이 아니라는 것**으로 답이 좁혀진다.

이것은 (a)를 강화하지도 약화하지도 않는다 — 다르게 만든다. 판정이 (a)를
택하면 "FOLIO 규약을 정본으로" 채택하는 것이 아니라 **새 경계를 세우고 두
corpus를 그것에 사상**해야 한다.

## 4. 한계 (숨기지 않는다)

- **버킷 (C)·(e)를 더 쪼개지 않았다.** 쪼개려면 분류기가 필요하고 그것이
  금지된 `operational_patch`다. 관측 특성(숫자·대문자·길이·닫힌 어휘)만 썼다.
- **(d)의 "고유명 결합으로 보인다"는 관찰이지 판정이 아니다.**
  `widereciever`가 반례로 그 안에 있다.
- 표면 토큰은 gold 주석에서 왔다. **주석이 정확하다는 것을 검증하지 않았다** —
  `entity.n.01←'and'`는 주석 자체가 잔여를 담고 있음을 시사한다.
- PMB 측정은 **synset 부류로 후보를 좁혔다.** 그 부류 밖에서 지시 표현이
  인코딩되는 경로가 있으면 15,810은 하한이다.

---

- 사슬 색인 [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX|RULING_CHAIN_INDEX]] ·
  판정 [[concept-gate-h1-wt/docs/DESIGN_DECISION_referential_participant_quantification|D-33]] ·
  재검증 [[concept-gate-h1-wt/docs/DESIGN_DECISION_d33_claim_status|D-33-V]] ·
  상신 [[concept-gate-h1-wt/docs/DESIGN_REQUEST_referential_existential_qualification|Q34]]
