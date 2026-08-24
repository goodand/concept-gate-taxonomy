# DESIGN REQUEST — Q34 보충: 두 corpus 전수 실사 (Q34-B)

- 발신: 2026-08-24, 운영 세션 · 수신: 외부 설계 담당
- 판정자 전제: **저장소 접근 없음.** 자기완결적이다 — 수치·예시·사용한 닫힌
  목록을 전부 본문에 싣는다.
- **새 문항은 없다.** Q34가 §7에 스스로 적은 측정 한계 둘을 닫은 것이고,
  그 결과가 **Q34 §6의 선택지 (a)~(c)의 근거를 바꾼다.** 판정을 재촉하는
  것이 아니라 판정 재료를 교체하는 것이다.
- 여전히 **경계를 제안하지 않는다** — D-33 `operational_patch: forbidden`,
  D-33-V "(b) directionally_plausible_but_not_implementable".
- 상태: **코호트 dispatch 누계 0건** 유지.

## 1. Q34가 무엇을 못 쟀다고 적었고, 무엇을 쟀는가

| Q34 §7의 한계 | 이 문서 |
|---|---|
| "PMB 쪽 전수는 20건이다. gold 전체(12,053건) 비율은 재지 않았다" | **12,053 문서 전수 실측** (§2) |
| "FOLIO 상수 116건을 부류별로 분류하지 않았다" | **116건·상수 출현 160회 전수 관측** (§3) |

두 측정 모두 **닫힌 목록 밖은 "미결정"으로 남긴다.** 경계 분류기를 만들면
그것이 금지된 `operational_patch`이고, 실제로 우리는 그 분류기를 네 번 만들어
네 번 다르게 틀렸다(D-33 §B.4). 그래서 분포만 기술한다.

## 2. PMB gold 전수 — 후보 표면의 **96%가 미결정**이다

12,053 문서에서 지시 후보 부류 synset(`male`·`female`·`person`·`entity`·
`thing` + `.n.NN`)이 붙은 개념 노드 **15,810개**를 뽑아, gold 주석의 표면
토큰으로 분류했다.

사용한 **닫힌 양화 어휘**(이것이 전부다):

```text
every everyone everybody everything all each some someone somebody something
any anyone anybody anything no nobody "no one" none neither both few many
several most
```

| 버킷 | 건수 | 예 |
|---|---:|---|
| (A) 표면 토큰 없음 — 비계·암묵 | 222 (1%) | `entity.n.01←''` · `male.n.02←''` |
| (B) **닫힌 양화 어휘** — 양측이 모두 양화한다 | 395 (2%) | `person.n.01←'Everyone'` · `entity.n.01←'Both'` · `entity.n.01←'anything'` |
| (C) **미결정** | **15,193 (96%)** | `person.n.01←'You'` · `entity.n.01←'This'` · `person.n.01←'person'` · `entity.n.01←'and'` |

**닫힌 어휘가 해결하는 것은 2%뿐이다.** (C)의 예시가 혼재를 그대로 보인다 —
대명사(`You`) · 지시사(`This`) · 보통명사(`person`) · 그리고 **주석 자체의
파싱 잔여**(`and`).

즉 이 현상은 표본 20건의 성질이 아니고, **작은 닫힌 목록으로 처리되지 않는다.**

## 3. FOLIO 전수 — 상수도 깨끗한 집단이 아니다 (Q34 §1의 자기 정정)

적격 풀에서 상수를 쓰는 전제 **116건**, 상수 출현 **160회**. 관측 가능한
특성으로만 버킷했다(의미 판정 없음).

| 관측 특성 | 건수 | 예 |
|---|---:|---|
| (a) 기능어 — 파싱 잔여로 보인다 | 1 (0%) | `on` (598p4, "Ontario"의 잔여로 보인다) |
| (b) 숫자 포함 | 12 (7%) | `summer1972olympics` · `year1990` · `year1915` · `number98199` |
| (c) 대문자 포함 | 11 (6%) | `newYork` · `johnNash` · `lawtonPark` · `athensOhio` |
| (d) 긴 복합어(12자 이상) | 28 (17%) | `portlandwhigs` · `mongolregion` · **`widereciever`** |
| (e) **미결정** — 소문자 단일어 | **108 (67%)** | `berlinzoo` · `portland` · `john` · **`music`** · **`stonefish`** |

**Q34 §1의 프레이밍을 정정한다.** 그 문서는 "FOLIO gold는 지시 표현을 상수로
인코딩한다"고 적었다. 방향은 맞지만 **집단이 깨끗하지 않다**: (b)(c)는 분명히
지시적이나 (d)에 `widereciever`(오타 난 보통명사)가 있고, (e) 67%에
`music`(물질명사)·`stonefish`(보통명사)가 섞여 있다. **FOLIO는 지시 표현이
아닌 것에도 상수를 쓴다** — 증인 셋을 위에 들었다.

## 4. 이것이 Q34 §6의 선택지에 하는 일

Q34는 "두 source가 반대로 인코딩한다"를 (a)의 근거로 냈다. 전수 실사는 그
논거를 **바꾼다**.

```text
PMB    지시 표현 → ∃ 결박자     그러나 후보 15,810개 중 96%가 미결정
FOLIO  지시 표현 → 상수         그러나 상수 160회 중 67%가 미결정
                                 그리고 보통명사·물질명사·파싱 잔여도 상수다
```

**관측되는 것은 이것이다**: 각 규약의 집단 안에, 다른 규약이라면 다르게
다룰 항목과 **어느 쪽 기준으로도 지시 표현이 아닌 항목**이 함께 들어 있다
(`music`·`stonefish`·`and`·`on`). 두 집단은 서로의 여집합이 아니고 각자
잡음을 포함한다.

*(우리가 말하지 않는 것*: "두 규약이 의미론적 경계를 따라가지 않는다"는
문장은 쓰지 않는다. 그것은 경계가 알려져 있어야 성립하는 후건이고, 그 전건이
바로 미정이다. 위 문단은 **관측된 잡음의 존재**만 주장한다.*)*

그래서 **(a)의 형태가 달라진다.** (a)를 "FOLIO 규약을 정본으로 채택한다"로
읽으면 잡음까지 채택한다. (a)가 성립하려면 **새 경계를 세우고 두 corpus를
그것에 사상**하는 형태여야 한다 — 그것은 (a)가 아니라 D-33이 명한
`REFERENTIAL_EXISTENTIAL_QUALIFICATION`의 내용이다.

**(c)(경계 정의가 원리적으로 불가하면 in-N PMB 15건을 어떻게 하는가)의 무게가
늘었다**: 이제 그 질문은 15건이 아니라 gold 전체 규모의 성질에 관한 것이다.

## 5. 이 실사의 한계

- **(C)·(e)를 더 쪼개지 않았다.** 쪼개려면 분류기가 필요하고 그것이 금지된
  `operational_patch`다. 관측 특성(닫힌 어휘·숫자·대문자·길이)만 썼다.
- **(d)의 "고유명 결합으로 보인다"는 관찰이지 판정이 아니다** —
  `widereciever`가 그 안의 반례다.
- **표면 토큰은 gold 주석에서 왔고, 주석의 정확성을 검증하지 않았다.**
  `entity.n.01←'and'`는 주석 자체가 잔여를 담고 있음을 시사한다.
- **PMB 측정은 synset 부류로 후보를 좁혔다.** 그 부류 밖에서 지시 표현이
  인코딩되는 경로가 있으면 15,810은 **하한**이다.
- FOLIO 측정은 **적격 풀**(799건 중 상수 사용 116건)이고 FOLIO 전체가 아니다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 본 상신 [[DESIGN_REQUEST_referential_existential_qualification|Q34]] · 판정 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · 재검증 [[DESIGN_DECISION_d33_claim_status|D-33-V]]
- 실사 원본 [[concept-gate-h1-wt/experiments/2026-08-23_e2e_v1_c_o1_cohort/REFERENTIAL_BOUNDARY_AUDIT_20260824|REFERENTIAL_BOUNDARY_AUDIT_20260824]]
