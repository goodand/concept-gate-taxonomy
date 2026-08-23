# Stage 2 V2 — adapter control 실행 기록 + 코호트 중지 판단 (2026-08-23)

- 문서 종류: **운영 로그** (결과 artifact와 같은 커밋, 동결 표면 무접촉)
- 절차: HANDOFF §3-2 — control 3건 선행, **3/3 통과가 본 코호트 해석 가능
  조건**. 사용자 승인: 커밋 + 코호트 실행 (2026-08-23) — 단 실행 승인은
  사전등록 절차 조건부다.
- 결론: **control 2/3 → 해석 가능 조건 미달 → 본 코호트 미실행(dispatch
  0건).** 원인 분해에서 상위 결함 2건이 추가 적발되어 상신(Q25) 준비.

## 1. control 실행 (실측)

dispatch: 세션 Workflow `wf_64740119-bb0`, `agentType: o1-compiler`,
model haiku, 봉투 schema(V2 profile 5종), 재시도 0 (mechanical retry는
인프라 실패 전용으로 배선했고 발동하지 않음). 산출은
`stage2_controls_{manifest,plan,results}.json` (plan은 oracle 무접촉 —
기존 격리 그대로).

| trial | case | 결과 | 차원 |
|---|---|---|---|
| CTRL-01 | FOLIO-1420p2 "All videos are visual." | **pass** | |
| CTRL-02 | FOLIO-175p1 "All monitors equipped in the lab are cheaper…" | fail | predicate_arguments |
| CTRL-03 | FOLIO-1377p0 "All humans eat." | **pass** | |

semantic retry는 D-19가 금지하므로 CTRL-02를 다시 던지지 않았다.

## 2. CTRL-02 분해 — F1: 라벨 span 미결정성

subject 출력은 oracle과 **구조 완전 동형**(∀·제한 1술어·본문 1술어·결박
정확)이고 차이는 라벨 span뿐:

| | oracle(codec 후) | subject |
|---|---|---|
| 제한 | `lab` | `equipped_in_lab` |
| 본문 | `cheaper` | `cheaper_than_original` |

도달성 불변식(D-24 Q24.2)은 "oracle 라벨이 문장에서 파생 가능"을
보증하지만 "subject가 같은 span을 고른다"는 보증하지 않는다 —
**derivable ≠ uniquely determined.** D-24 §16의 3분류(표기 잡음/숨은
어휘/의미 topology) 어디에도 정확히 안 들어가는 중간 사례다.

## 3. 파급 실측 — F2: in-N FOLIO 5건 중 4건이 같은 위험

oracle 라벨이 다중 토큰 join인 fixture (subject는 CTRL-02에서 밑줄 join을
발명했고, codec은 분절을 금지하므로 `can_catch` ≠ `cancatch`):

| case | 위험 라벨 |
|---|---|
| FOLIO-142p1 | cancatch |
| FOLIO-695p1 | universallanguage |
| FOLIO-404p0 | competitivesport, greyhoundracing, spectatorsbeton |
| FOLIO-598p4 | majorsettlementof |
| FOLIO-376p4 | (없음 — cat/pet 단일 토큰) |

template은 다중어 개념의 join 규약을 지시하지 않는다("content words"만).

## 4. F3 — PMB 15/15: oracle granularity가 subject 방언과 원리적 불일치

PMB 15건 전수 실측: oracle IR이 **SBN 사건 의미론**으로 인코딩돼 있다 —
role 술어(`Agent`, `Experiencer`, `Stimulus`, `Theme`, `Time`, `EQU`,
`TPR`, `Quantity`…)와 문장에 없는 암묵 개념(`time`, `person`), 사건·시간
변수용 추가 존재 양화.

실물 (PMB-p15-d0787, quantifier_negation_scope):

- 문장: "Not all children like apples."
- oracle: `¬∀x0 child(x0) → ∃x1∃x2∃x3 [like.v.03(x1) ∧ Experiencer(x1,·)
  ∧ … ∧ Time/EQU …]` — ¬∀ scope 골격은 있으나 그 위에 사건 구조가 얹힘
- template 준수 subject의 자연 출력: `not(forall(x, child(x),
  exists(y, apple(y), like(x,y))))` — 양화사 수(2 vs 4)·arity(like/2 vs
  like.v.03/1+roles)·어휘(role 술어는 content word가 아니라서 **지시상
  산출 금지**) 전부 불일치

→ DirectMatch가 구조 동일성을 요구하므로 **PMB 15건은 subject가
지시를 완벽히 따를수록 확실히 fail**한다. B1과 같은 부류(측정 계약이
fixture를 원천 실패시키는 pre-execution 결함)이며 층위만 다르다: B1은
라벨 표기, F3은 **의미 표상의 granularity**. V1부터 있었고 V2가 PMB를
불변 보존했으므로 그대로 존속한다.

### 왜 이제야 보였나 (정직한 회계)

- 사전 검증 23/23·S1은 **commitment 무결성**(캐시 왕복·재복호 해시)을
  검증했지 **subject-통과가능성**을 검증하지 않았다.
- 리허설·smoke의 live 재료는 전부 발명 FOL형 — PMB oracle에 대한
  "그럴법한 subject 출력 vs oracle" 대조는 **한 번도 없었다** (smoke
  설계의 구멍이기도 하다 — SMOKE 문서 §0의 S1 설명은 이 한계를 명시하지
  않았다).
- control이 정확히 제 역할을 했다: 해석 가능 조건이 코호트 앞에서 멈춰
  세웠고, 그 원인 분해가 상위 결함을 노출했다.

## 5. 처분

- 본 코호트 **미실행** (dispatch 0건, 결과 0건 관측 — amendment 전제 유지)
- Stage 2 상태: `BLOCKED_UNTIL_RULING(Q25)` — HANDOFF §0 갱신
- 상신: `docs/DESIGN_REQUEST_oracle_granularity.md` (Q25: F1 span 미결정·
  F2 join 규약 부재·F3 PMB granularity — 셋 다 측정 계약 vs oracle 표상의
  정합 문제로 통합 상신)
