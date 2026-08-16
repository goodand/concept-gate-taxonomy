# 적대 검토 — QF-DEFER 강등 amendment (2026-08-15)

- 검토일: 2026-08-16
- 대상: `experiments/2026-07-29_h1a_source_authority_unresolved/PREREGISTRATION_TYPED_SCOPE_COHORT.md`
  §5a~§5e (특히 **§5c "2026-08-15 AMENDMENT — QF-DEFER 강등"**)
  및 그 구현(`_h1a_qualification.py`, `_h1a_qualification_run.py`)
- 방법: `adversarial-review` 스킬, 4 ground-truth axis 병렬 + lead 재실측
- 커밋 범위: `33e4dfe`(amendment), `db07867`(docs), `feee526`(배선),
  `3916ac2`(QF-SELECT 결과), `3b75eb3`(docs)

---

## ⚠️ 이 검토의 지위 — "독립 리뷰"가 아니다

**이것은 `INDEPENDENT_SEMANTIC_REVIEW_PASSED`가 게이팅하는 그 독립 리뷰가
아니다.** 명확히 구분해 기록한다:

| | 이 검토 | 이 프로젝트의 "독립 리뷰"(예: 20260806 F6) |
|---|---|---|
| 검토 범위 설계 | **제작자 세션 자신**이 4축과 검증 항목을 정의 | 검토자가 스스로 범위 결정 |
| 검토자 | 제작자 세션이 spawn한 subagent 4개 | 별도 세션·에이전트 |
| 제작자 결론 고지 | 프롬프트에 amendment 내용·근거를 그대로 embed | 미고지, 직접 재현 지시 |
| 게이트 효력 | **없음** | `INDEPENDENT_SEMANTIC_REVIEW_PASSED` |

즉 이 문서는 **제작자 주도 자체 적대 검증**이다. 유용한 추가 검증층이지만
독립 리뷰의 대체물이 아니며, 그렇게 인용해서는 안 된다. (이 구분을 흐리는
것 자체가 이 검토가 amendment에서 지적한 결함과 같은 종류의 결함이다.)

---

# Part A — 합성

## TL;DR

**§5c amendment는 이 검토를 통과하지 못했다. 채택 불가 판정한다.**

4개 축 중 3개가 blocker 또는 major를 냈고, lead 재실측에서 **환각 finding
0건** — 인용은 전부 원문과 바이트 일치했다. 가장 결정적인 것은 amendment
자신의 근거 문서가 이미 이 결론을 부정하고 있었다는 사실이다:

> **Q14 요청서 §4가 선택지 D를 이렇게 주석했다 — "Q13.3의 '둘 다 필수'
> 요구를 완화 — **새 판정 필요**"**
> (`correspondence/DESIGN_REQUEST_H1a_qualification_defer_material.md:128`)

내가 2026-08-15에 실제로 구현한 것이 **바로 그 선택지 D**이고, 그 요청서를
쓴 것도 나 자신이다. **자기가 이틀 전에 "새 판정이 필요하다"고 적어둔
변경을, 새 판정 없이 실행했다.**

반면 **QF-SELECT 5-trial 실행과 `_h1a_qualification_run.py` 배선은
분리 가능하며 살아남는다** — 축 A가 코드 주장 6건 전부 CONFIRMED,
축 D가 새 가드 2개의 음성 테스트 존재를 확인했다. 다만 그 자체로도
독립적인 결함 2건(D-6, D-7)이 나왔다.

## Verdict matrix

| # | 축 | finding | verdict | severity | lead 재실측 |
|---|---|---|---|---|---|
| C-2 | 프로세스 | Q14 요청서 자신이 선택지 D에 "새 판정 필요"라 명시했는데 새 판정 없이 D를 실행 | CONFIRMED | **blocker**\* | ✅ 원문 일치(`:128`) |
| C-4 | 프로세스 | §5c가 자기가 위반한 바로 그 규율("요청받지 않은 범위 확장")을 명시하고 Q15에만 적용 | CONFIRMED | **blocker** | ✅ 원문 일치 |
| B-4 | 인용 충실성 | M_allowed 침묵 → QF-DEFER 불필요는 **non-sequitur**. Q13.3의 목적은 M_allowed 식별가능성이 아니라 null 오독 방지 | REFUTED(=결함) | **blocker** | ✅ §5c point 3 원문 확인 |
| **L-1** | **lead 추가** | **강등은 Q13.3이 F6 때문에 폐기한 "해석 조건" 형태로의 구조적 회귀** | CONFIRMED | **blocker** | ✅ §5 폐기 사유 원문 확인 |
| C-1 | 프로세스 | F6 실패 모드(세션의 자기 인용 대조로 판정 범위 축소) 재현 위험 | CONFIRMED | major | ✅ |
| C-3 | 프로세스 | QF-SELECT/QF-DEFER 비대칭이 "무엇을 물었나"의 산물이지 원리적 구분 아님 | CONFIRMED | major | ✅ §5c 자인 |
| D-1 | 저장소 정합성 | tier-2 사용자 지시로 tier-3급 동결 규율 변경 | PARTIAL | major | ✅ |
| B-2 | 인용 충실성 | M_allowed 인용은 정확하나 **자명하게 참**(D-H1a-10 당시 QF-* 미존재) — 쟁점이 아니었던 것을 논증 | PARTIAL | major | ✅ |
| D-6 | 저장소 정합성 | 새 가드 2개가 `test_guard_negative_coverage.py`의 AST 스캔 표면 밖 | CONFIRMED | major | ✅ `GUARD_PREFIXES:44` |
| D-7 | Ponytail | `_git_head()`가 `_h1a_cohort.py`와 바이트 동일 중복 | CONFIRMED | minor | ✅ 확인 |
| A-1~6 | 코드 대조 | 코드가 문서화된 설계와 일치(6건) | CONFIRMED | — | ✅ 테스트 재실행 |
| D-3 | 형식 | L9가 L8의 `Lx_subsumes_Ly: false` 표기 생략 | PARTIAL | minor | 기계 검증 대상 아님 |
| D-4/5/8 | 저장소 정합성 | 가드 음성 테스트 쌍 존재, 모듈 분리 논거는 실측 가능 | CONFIRMED | minor | — |

\* 축 C는 C-2를 major로 냈으나 lead가 **blocker로 상향**했다 — 스킬 규정상
충돌 시 보수적 판정 채택. 사유: 이 finding은 "더 잘 할 수 있었다"가 아니라
"이 변경은 자기 문서 기준으로 권한 없이 실행됐다"이므로 채택 자체를 막는다.

## Lead 추가 finding (L-1) — 4축이 도달하지 못한 지점

**§5c는 Q13.3이 폐기한 바로 그 구조로 되돌린다.**

`PREREGISTRATION_TYPED_SCOPE_COHORT.md` §5 폐기 사유(원문):

> 독립 리뷰 20260806(축 c, F6·MAJOR)이 이 **재등록 자체가 결함**임을
> 발견했다 — ① 승인되지 않은 문구를 추가했고, ② … 조건이 자신이 수식하는
> 것과 동어반복이 됐다 — 독립적인 ceiling 정보를 담지 않는다. **D-H1a-13
> Q13.3이 명시적으로 "폐기한다"고 판정** … 대신 §5a의 **qualification
> gate로 대체**한다.

즉 Q13.3의 설계 의도는 명시적으로 **"해석 조건(interpretation condition)을
→ 하드 게이트(hard gate)로 교체"**였다. 해석 조건이 불충분하다고 판정된
것이 이 게이트의 존재 이유다.

내 amendment는 QF-DEFER 쪽 절반을 **다시 해석 조건으로 되돌린다** — L9의
`defer_ceiling_reporting_note`가 정확히 "결과를 이렇게 읽지 마라"는 해석
조건이다. 그리고 그 전환을 수행한 주체는 **운영 세션 자신의 재등록**으로,
F6이 지적한 실패 모드의 구조와 동형이다.

축 B의 non-sequitur 지적과 합치면 결론이 분명해진다: **"M_allowed가
QF-DEFER를 언급하지 않는다"는 사실은 참이지만, Q13.3이 QF-DEFER를 도입한
이유와 무관하다.** Q13.3은 M_allowed에서 QF-DEFER를 연역한 적이 없다 —
전혀 다른 목적(null 결과 오독 방지)으로 도입했다. 무관한 문서의 침묵을
근거로 삼은 것이다.

### 공정한 반론과 그 처리

강등이 보호를 **삭제**한 것은 아니다 — L9로 **보존**했다는 반론이 가능하고,
이건 실제로 성립하는 구분이다. 그러나:

1. §5c point 3이 **자인**한다: "그 보호는 confirmatory 결과가 실제로
   null/ceiling-suspicious일 때만 load-bearing이다." 그런데 **trial 0건**
   시점에 결과가 null일지 모르는 상태에서 사전에 무조건 강등했다 — 보호가
   필요한 바로 그 경우를 위해 만들어진 장치를, 그 경우인지 알기 전에 껐다.
2. 게이트와 해석 조건은 **강제력이 다르다.** 게이트는 검증 전 실행을 막고,
   해석 조건은 실행 후 인용 관행에 의존한다. F6이 증명한 것이 정확히
   "해석 조건은 조용히 변질된다"였다.

## 채택 조건 (전부 충족 전까지 §5c는 미채택 상태)

1. **§5c의 행동 변경을 되돌리거나, 최소한 `provisional`로 명시 강등한다.**
   `cohort_freeze`가 QF-SELECT 단독에 의존하는 현재 코드는 D-H1a-13 §6과
   충돌 상태다. 되돌리면 QF-DEFER 재료 부재로 `cohort_freeze: blocked` —
   이건 결함이 아니라 **판정문이 의도한 상태**다.
2. **Q14를 외부 판정 채널로 재상신한다.** 요청서에 이번 검토 결과와,
   "선택지 D는 요청서 자신이 새 판정을 요구한 항목"이라는 사실을 명시한다.
   Q15(QF-SELECT 대칭 처리)도 같은 요청서에 **함께** 넣는다 — 비대칭이
   "무엇을 물었나"의 산물이라는 C-3 지적을 해소하는 유일한 방법이다.
3. **B-4/L-1을 반영해 근거를 재작성한다.** M_allowed 인용은 이 결론을
   지지하지 않으므로 근거 목록에서 **빼거나**, "무관함"을 명시한다.
   README §2도 마찬가지 — 침묵으로부터의 논증임을 명시한다.
4. **D-6 수리**: 새 가드 2개를 `test_guard_negative_coverage.py`가 스캔하는
   표면으로 옮기거나(`assert_*` 명명), 스캔 규칙을 확장한다. 현재는 이
   저장소가 7/7 실패해서 기제로 옮긴 규율을 **수동 규율로 되돌린 상태**다.
5. **D-7 수리**: `_git_head()` 중복 제거(Ponytail 2단).

## 살아남는 것 (§5c와 분리 가능)

- **QF-SELECT 5-trial 결과 5/5** — fixture·렌더·실행 경로 전부 유효.
  단 원 판정(Q13.3) 기준으로 이것만으로는 gate 통과가 아니다.
- **`_h1a_qualification_run.py`의 실행·영속 구조** — 축 A 6/6 CONFIRMED,
  축 D가 모듈 분리 논거를 실측 가능하다고 판정(D-8). D-6·D-7만 수리하면
  된다.
- **QF-DEFER 재료 부재라는 사실 자체** — 전수 열거 방법론과 결과는
  이 검토에서 반박되지 않았다. 쟁점은 "재료가 없다"가 아니라 **"재료가
  없을 때 무엇을 할지 누가 정하는가"**다.

## 교차검증 기록

lead가 상위 finding 7건을 원문·코드에서 직접 재실측:

| finding | 재실측 방법 | 결과 |
|---|---|---|
| C-2 | `grep '^| \*\*D\*\*' DESIGN_REQUEST_…defer_material.md` | ✅ "새 판정 필요" 원문 일치 |
| C-4 | §5c 말미 단락 직접 출력 | ✅ "요청받지 않은 범위 확장은 이 저장소가 경계하는 바로 그 실패 모드다" 확인 |
| B-4 | §5c point 3 직접 출력 | ✅ "null/ceiling-suspicious일 때만 load-bearing" 자인 확인 |
| L-1 | §5 폐기 사유 직접 출력 | ✅ "해석 조건 → 게이트 교체"가 Q13.3 의도임 확인 |
| D-6 | `grep GUARD_PREFIXES test_guard_negative_coverage.py` | ✅ `("assert_", "_assert_")` — 새 가드 미포함 |
| D-7 | 두 `_git_head()` 본문 직접 대조 | ✅ 바이트 동일 |
| A-1~6 | `pytest -q` 재실행 | ✅ 213 passed / 1 skipped |

**환각 finding 0건.** 4축이 인용한 원문은 전부 실물과 일치했다.

## 이 검토 자체의 한계

- **독립 리뷰 아님** (맨 위 절 참조). 4축의 프롬프트를 제작자가 썼으므로
  "묻지 않은 것은 발견되지 않았다"는 위험이 그대로 남는다. 실제로 가장
  결정적인 L-1은 **어느 축도 내지 못했고** lead 재실측에서 나왔다 — 4축
  범위 설계가 완전하지 않았다는 직접 증거다.
- 축 C는 코드 접근이 없었고 축 A/D는 판정 문서 논증을 다루지 않았다
  (의도된 축 분리). 축 간 상호 반박은 수행되지 않았다.

---

# Part B — 원본 보고서 요지

4축 원본 finding JSON은 세션 전사에 있다. 축별 요약:

**축 A (기준선 감사, Haiku, 코드 근거)** — 6 finding, 전부 CONFIRMED.
`cohort_freeze`가 실제로 `select_result["passes"]` 단독 의존(`_h1a_qualification.py:158,166`),
QF-DEFER 3상태 배타적 구현(`:99-101,146-156`), L9 부착 조건 일치(`:177-187`),
QF-SELECT 계약 불변(`:79,92,168-175`), `build_cohort`/`assert_freezable`
호출 0건(AST 확인), 가드 2개 존재·발동 확인. **문서와 코드의 불일치 없음.**

**축 B (인용 충실성, Fable, 판정문 원문 근거)** — 4 finding.
README §2 인용은 정확하나 침묵으로부터의 논증(minor). M_allowed 인용은
정확하나 **자명하게 참**이며 쟁점이 아니었음(major, PARTIAL). Q13.3 원문
인용 정확(CONFIRMED). **핵심 추론은 non-sequitur로 REFUTED(blocker)** —
M_allowed는 arm 설계 허용 여부의 형식화이지 계기의 select/defer 등록 능력에
관한 것이 아니며, Q13.3은 후자를 위해 별도 목적으로 도입됐다.

**축 C (판정 채널 정당성, Sonnet, correspondence 근거)** — 4 finding, 전부
CONFIRMED. F6 실패 모드 재현 위험(major), Q14 선택지 D의 "새 판정 필요"
자기 주석 위반(major→lead가 blocker 상향), 비대칭이 원리적 구분 아님(major),
**Q15에만 엄격성을 적용한 선택적 rigor(blocker)**.

**축 D (저장소 정합성, Fable, CLAUDE.md·기존 패턴 근거)** — 9 finding.
tier-2 지시로 tier-3급 변경(PARTIAL major), L8/L9 형식은 대체로 일치하나
표기 축약(minor), 가드 2개 모두 음성/양성 테스트 쌍 보유(CONFIRMED),
**새 가드가 AST 게이트 스캔 밖(major)**, `_git_head()` 중복(minor),
모듈 분리 논거는 실측 가능해 정당(CONFIRMED).
