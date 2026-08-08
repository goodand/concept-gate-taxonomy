# H1a — `source_authority_unresolved` (설계 판정 5건, Q9 등록 대기)

> ⚠️ **이 README의 아래 본문 상당 부분은 2026-07-30 시점 서술이다.**
> Q3~Q9가 그 뒤에 왔고, 특히 **Q6=A가 anchor-sensitivity 진단을
> 은퇴시켰다** — 아래에서 "진단을 통과해야 본 코호트 진행"이라고 읽히는
> 서술은 **더 이상 유효하지 않다**. 현재 상태의 정본은
> [`../../docs/HANDOFF.md`](../../docs/HANDOFF.md)이고, 실행 함정은
> [`../../docs/NEXT_SESSION_TRAPS.md`](../../docs/NEXT_SESSION_TRAPS.md)다.

- 작성: 2026-07-29 (초안) / 재정의: 2026-07-29 설계 판정 반영 /
  갱신: 2026-07-30 조작 범위 재정의(Q1) + anchor 진단 게이트(Q2) /
  **갱신: 2026-08-02 Q3~Q8 적용 완료 + Q9 판정 도착**
- 지위: **설계 판정 5건, 독립 리뷰 3회, 실행된 trial 0건.**
  Q5~Q8 적용 완료(조작 2문장 축소, 모델 대면 type 앵커 제거, warrant 기반
  defer 정의, fixture 진짜 1-vs-1), 3차 독립 리뷰 blocker 0.
  **남은 게이트는 Q9=A의 L3 한계 문구를 `PREREGISTRATION.md`에 등록하는
  것뿐이다** — fixture·코드 변경은 없다. 그 뒤 동결 → 본 코호트 40 trial
  (별도 승인).
- **anchor-sensitivity 진단(Q2)은 은퇴했다** — Q6=A가 모델 대면 앵커를
  제거해 잴 대상이 사라졌다. 구현체 4파일은
  [`superseded/`](superseded/)에 있고 사유는
  [`superseded/WHY.md`](superseded/WHY.md). 대체물은
  `_h1a_surface.py::assert_no_model_facing_type_anchor`(구조적 가드).
- 설계 판정 원문: [`DESIGN_DECISION.md`](DESIGN_DECISION.md)(D-H1a-1~7),
  [`DESIGN_DECISION_H1a_manipulation_scope.md`](DESIGN_DECISION_H1a_manipulation_scope.md)(Q1·Q2),
  [`DESIGN_DECISION_H1a_prompt_surface.md`](DESIGN_DECISION_H1a_prompt_surface.md)(Q3·Q4),
  [`DESIGN_DECISION_H1a_review_blockers.md`](DESIGN_DECISION_H1a_review_blockers.md)(Q5~Q8),
  [`DESIGN_DECISION_H1a_evidence_symmetry.md`](DESIGN_DECISION_H1a_evidence_symmetry.md)(Q9,
  2026-08-02 — **정정 2026-08-07: 이미 저장소에 반입돼 있다.** 이 줄이
  이전엔 `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`를 "저장소
  미반입"으로 가리켰으나, 그 판정은 실제로 이 실험 폴더에 이 파일명으로
  이미 들어와 있었다 — 링크만 갱신되지 않았다),
  [`DESIGN_DECISION_H1a_residual_prohibition.md`](DESIGN_DECISION_H1a_residual_prohibition.md)(D-H1a-10,
  Q10 — 잔여 금지와 null 식별가능성),
  [`DESIGN_DECISION_H1a_prescribed_sentence_defects.md`](DESIGN_DECISION_H1a_prescribed_sentence_defects.md)(D-H1a-13,
  2026-08-06 — 가장 최근 판정. D-H1a-12 §4·§6·§7 처방 문구와 §14 ceiling,
  §16 freeze 조건을 개정하고 기존 독립 리뷰를 무효화함
  — `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지 중)
  — 판정자: OpenAI Codex, 외부.
- 요청서 원문(각 판정이 응답한 질문의 정확한 문구·embed된 근거) —
  2026-08-07 orphan 감사로 개별 연결:
  [`correspondence/DESIGN_REQUEST.md`](correspondence/DESIGN_REQUEST.md) →
  `DESIGN_DECISION.md`,
  [`correspondence/DESIGN_REQUEST_H1a_manipulation_scope.md`](correspondence/DESIGN_REQUEST_H1a_manipulation_scope.md) →
  `DESIGN_DECISION_H1a_manipulation_scope.md`,
  [`correspondence/DESIGN_REQUEST_H1a_prompt_surface.md`](correspondence/DESIGN_REQUEST_H1a_prompt_surface.md) →
  `DESIGN_DECISION_H1a_prompt_surface.md`,
  [`correspondence/DESIGN_REQUEST_H1a_review_blockers.md`](correspondence/DESIGN_REQUEST_H1a_review_blockers.md) →
  `DESIGN_DECISION_H1a_review_blockers.md`,
  [`correspondence/DESIGN_REQUEST_H1a_evidence_symmetry.md`](correspondence/DESIGN_REQUEST_H1a_evidence_symmetry.md) →
  `DESIGN_DECISION_H1a_evidence_symmetry.md`,
  [`correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md`](correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md) →
  `DESIGN_DECISION_H1a_residual_prohibition.md`.
  [`correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md`](correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md)는
  **이 worktree에 답변 판정문이 없다** — `review_required`로 남긴다, 임의로
  다른 판정에 흡수시키지 않는다.
- 모델 대면 프롬프트 template: [`h1a_prompt_template.md`](h1a_prompt_template.md)
  **(판정문이 아니다 — 2026-08-02 분리)**
- 적대 검증 보고: [`../../docs/feedback/h1a_source_authority_unresolved_review_20260729.md`](../../docs/feedback/h1a_source_authority_unresolved_review_20260729.md)(설계 초안 리뷰),
  [`../../docs/feedback/h1a_fixture_review_20260730.md`](../../docs/feedback/h1a_fixture_review_20260730.md)(fixture 리뷰, blocker #16 발견)
- 분기 출처: 2026-07-29 운영 지시 §3(네 번째 항목) — 원문
  [`docs/DIRECTIVE_2026-07-29_operations_change.md`](../../docs/DIRECTIVE_2026-07-29_operations_change.md)

> ## ⚠️ 이 실험이 측정하는 것 — 먼저 읽어라
>
> **모델은 무엇이 stale인지 알 수단을 받지 않는다.** liveness·supersession·
> qualification profile은 모델에게 전달되지 않는다(하네스가 실행 전에 확정하고
> 넘기지 않는다).
>
> 따라서 H1a가 직접 측정하는 것은 "모델이 live 코드를 알아보는가"가 **아니다.**
> 측정 대상은:
>
> > **`doc` / `code` / `test`라는 출처 종류가 충돌하는 상황에서, 금지 문장의
> > 유무가 선택과 보류 행동에 어떤 차이를 만드는가.**
>
> 결과를 서술할 때 "모델이 stale 문서를 알아봤다/못 알아봤다"는 표현을 쓰면
> 안 된다. 폴더명 `source_authority_unresolved`는 지시문이 지정한 이름이지만
> **이름이 측정보다 넓다** — 이름이 함의하는 것 이상을 주장하지 않는다.

## 1. 왜 별도 실험인가

E2.4의 `conflicting` class는 **동등강도 direct evidence가 양립 불가능한 type을
지지하는** 경우를 다뤘고, 그런 fixture는 확보되지 않아 종결됐다
(`PROBLEM_2_conflicting.md` §5.2).

H1a가 다루는 것은 다른 상황이다: 충돌이 "동등강도"가 아니라 **출처 종류가
다른** 경우. E2.4는 이 축을 모델 범위 밖으로 밀어냈다. `contract_prompt.md` 서문:

> 이 packet의 evidence item은 실행 전 provenance/eligibility 검증을 통과했다.
> 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.

그리고 `semantic_constraints` #11이 그 위반을 **오답으로 채점**한다.
**즉 E2.4에서 이 행동은 "측정 대상"이 아니라 "금지 사항"이다.** H1a는 그
금지 문장을 조작 변수로 삼는다.

## 2. 연구 질문 (재정의됨)

**정답을 두지 않는 서술적·탐색적 실험이다.** 판정 D-H1a-4(C).

> 계약 서문에서 **"모델은 출처의 liveness나 우선순위를 재판정하지 않는다"
> 한 문장을 제거**했을 때, 출처 종류가 충돌하는 동일 fixture에 대한
> **선택(select_type) / 보류(defer) 행동 분포가 달라지는가?**

- **정답률·인증 class를 측정하지 않는다.** E2.4의 합격 임계(0.90)와
  `screened_PASS`/`ambiguous`/`screened_FAIL` 밴드를 **사용하지 않는다.**
- **hidden correctness oracle을 두지 않는다.** 어느 행동도 성공/실패로 표시하지
  않는다.
- **인과 귀속을 하지 않는다**(판정 D-H1a-7). 현재 fixture는 `source_kind`와
  원문 내부 표현(문서의 `주의:` 강조, 테스트 인용)을 함께 담고 있어, 관측된
  선택을 "사전지식 의존" 또는 "실제 liveness 판정"으로 귀속할 수단이 없다.
  결론은 **"선택/보류 행동과 그 rationale이 관측됐다"까지**다.
- **rationale은 행동 해석 자료일 뿐** 판단 원인의 신뢰할 수 있는 자기보고로
  취급하지 않는다.
- 동일 fixture 반복 시행 결과를 **일반적인 모델 성향으로 일반화하지 않는다.**

## 3. 재료 — 실측 확인 완료

인스턴스가 `칼`/`철`로 **정확히 일치**하는 실제 충돌이다. 합성이 아니다.
독립 리뷰어가 전수 확인했다. **2026-07-30 독립 리뷰 C2·C3(#7·#8·#10) 반영:**
아래 표는 재구성 후 상태다 — code측 증거를 칼/철 미명명 일반 규칙에서
칼/철을 명명하고 문장 줄기가 같은 코드로 교체했고, ev3와 한 저작 행위였던
테스트 인용(ev4)은 제거해 정직한 1-vs-1로 만들었다. 옛 표는
`docs/H1A_ISSUE_REGISTER.md` C2·C3에 근거와 함께 보존.

| 측 | 위치 | 텍스트 | 주장 |
|---|---|---|---|
| **문서**(`source_kind: doc`) | `docs/phase_a_implementation_packet.md:102` | `(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)` | 철 = `essential_feature` |
| 〃 보강 | 〃 `:106` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | 예외를 명시 |
| **코드**(`source_kind: code`) | `conceptgate/concept_gate_v7.py:1192-1193` | `(4) 재료-대상: 철은 칼의 재료 → structural_composition (재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)` | 철 = `structural_composition` — 문서와 **같은 문장 줄기, type만 반대** |

문서 쪽 이력: 마지막 변경은 `cf58c8c`(패키지 단일화 리팩터)로 상단에 경고
배너만 추가했고 **본문 주장은 미수정**. 내용은 `4e0214c` 시점 그대로다.

> **주의**: 위 "문서가 낡았다"는 서술은 **하네스와 이 문서를 읽는 사람의
> 지식**이다. **모델에게는 전달되지 않는다.** 모델이 받는 것은 `source_kind`와
> `text`뿐이다(§5).

C1~C4: C2(인스턴스 결박) 충족, C3(비순환) 충족, C4(선행성) `git log`로 확인.
**C1(liveness)은 하네스가 확정하고 모델에 넘기지 않는다** — 넘기면 이 실험의
조작 변수가 오염된다.

## 4. arm — 2개 (판정 D-H1a-6 = B)

| arm | 프롬프트 표면(Q3=B, 2026-07-31 재정의) | 스키마 |
|---|---|---|
| `PROHIBITION_KEPT` | H1a 전용 template + Q1 liveness 절 포함 | H1a 전용 스키마 (동일) |
| `PROHIBITION_REMOVED` | H1a 전용 template, liveness 절 없음 | H1a 전용 스키마 (동일) |

**"E2.4 서문 그대로"는 폐기됐다** — §4.1 참조.

**legacy CONTROL arm은 제외됐다.** 판정 근거: legacy 스키마의 `decision` enum은
`report_done`/`repair`/`request_evidence`뿐이라 **"보류"를 표현할 수 없고**,
이 실험의 핵심 종속변수를 **구조적으로 검열**한다.

두 arm은 **같은 fixture, 같은 모델, 같은 parameters, 같은 응답 스키마**를 쓴다.
**arm 간 유일한 차이는 지정된 금지 문장 하나여야 한다.**

### 4.1 프롬프트 표면 (판정 D-H1a-5, **2026-07-30 재정의, 2026-07-31 재재정의**)

> ⚠️⚠️ **2026-07-31 갱신 — 아래 "재정의"도 그대로 실행하면 blocker다.**
> 2026-07-30 재정의는 "E2.4 계약문 113행 전체를 재사용하고 두 절만 지운다"는
> 방식이었다. 실제로 첫 trial 프롬프트를 조립해 보니 E2.4 규칙 2~7이
> `h1a_observation_v1`과 맞물리지 않았고, 특히 **규칙 3의 동률 조항이 H1a
> fixture의 정확한 모양을 무조건 `defer`로 매핑**해 조작과 무관한 천장을
> 만들 위험이 드러났다(등록부 G2·G3). 외부 설계 판정
> [`DESIGN_DECISION_H1a_prompt_surface.md`](DESIGN_DECISION_H1a_prompt_surface.md)
> (Q3=B)가 프롬프트 표면 자체를 다시 정의했다: **E2.4 규칙 2~7과 서문을
> 버리고, H1a 전용 task 지시문으로 교체한다.** 아래 §4.1.1이 최신이다.

#### 4.1.0 2026-07-30 재정의 (폐기 — 이력 보존용)

원래 초안은 계약 서문 문장 하나만 지우면 조작이 성립한다고 봤다. 독립
리뷰(2026-07-30) blocker #16이 발견한 것: 절대 규칙 1에 **논리적으로
동등하고 더 명시적인** 두 번째 금지가 그대로 남아 있어, 그 초안대로
지운 `PROHIBITION_REMOVED` arm은 **여전히 liveness 재판정을 금지한다.**
조작이 무효화된다는 뜻이다. 외부 설계 판정
[`DESIGN_DECISION_H1a_manipulation_scope.md`](DESIGN_DECISION_H1a_manipulation_scope.md)
(Q1=B)가 D-H1a-5를 재정의했다 — **이 절 삭제 판정 자체는 여전히 유효하다**,
다만 "무엇 위에 적용하는가"가 §4.1.1로 바뀌었다.

> ⚠️ **아래는 폐기된 초안이다 — 그대로 실행하면 blocker다.**
> 원래 초안은 계약 서문 문장 하나만 지우면 조작이 성립한다고 봤다. 독립
> 리뷰(2026-07-30) blocker #16이 발견한 것: 절대 규칙 1에 **논리적으로
> 동등하고 더 명시적인** 두 번째 금지가 그대로 남아 있어, 그 초안대로
> 지운 `PROHIBITION_REMOVED` arm은 **여전히 liveness 재판정을 금지한다.**
> 조작이 무효화된다는 뜻이다. 외부 설계 판정
> [`DESIGN_DECISION_H1a_manipulation_scope.md`](DESIGN_DECISION_H1a_manipulation_scope.md)
> (Q1=B)가 D-H1a-5를 재정의했다.

대상 계약문에는 liveness/우선순위/최신성/권위를 금지하는 절이 **두 곳**에
있다(2026-07-30 전수 스캔으로 확인 — 다른 곳에는 없음):

```
이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.   ← block L8
```

```
   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를
     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.       ← block L24-25
```

**재정의된 규칙(2026-07-30, 여전히 유효)**: "한 문장을 지운다"가 아니라
**"liveness·source-priority·recency·authority·supersession 재판정을 금지하는
모델 대면 절을 전부 지운다."** 지울 대상은 여전히 L8 + L24-25 두 절이다.

#### 4.1.1 2026-07-31 재정의 — 프롬프트 표면 자체를 H1a 전용으로 (최신, Q3=B)

**Q3.1 부수 판정("그럴듯하다"가 recency/authority를 포괄하는가) = "예,
기능적으로."** 규칙 3은 알고리즘적이라 동률이면 근거 종류와 무관하게 무조건
null(=defer)을 요구한다 — "치명" 해석이 맞았다는 뜻이고, 이것이 규칙 2~7
전체를 버리는 결정적 근거였다.

**무엇이 남고 무엇이 사라지는가**:

| E2.4 원본 | H1a 처리 |
|---|---|
| 서문(packet 설명, "모델의 책임은…", "목표는…") | **삭제.** H1a 전용 task 지시문으로 교체 |
| 절대 규칙 1(packet 밖 지식 금지 + liveness 절 2개) | **실질만 유지**, 판정문 자신의 영어 문구로 재작성. liveness 절 2개는 여전히 §4.1의 규칙대로 KEPT에만 삽입 |
| 규칙 2~7(evidence audit·sufficiency·repair·abstain·accept_report) | **전부 삭제.** `h1a_observation_v1`과 맞물리지 않고, 규칙 3(동률→null)이 조작과 무관한 천장을 만들 위험이 있었다 |
| 마지막 줄(스키마 지시) | **삭제.** 새 template이 `h1a_observation_v1`을 프롬프트 안에 직접 보여준다 |

구현은 `_h1a_contract.py` 전면 재작성 — H1a 전용 template을
`DESIGN_DECISION_H1a_prompt_surface.md` 자신의 fenced block에서 **로드**하고
(재입력 없음), Q1의 두 절을 정규화해 template의 유일한 packet-boundary
문장("...or external sources.") 뒤에 `PROHIBITION_KEPT`에만 삽입한다.
`test_h1a_contract.py` 18 passed, 뮤테이션 4종 CAUGHT. 상세는
`PREREGISTRATION.md` §P0.1.

**독립 리뷰 우선 점검 대상으로 문서에 명시해 둔 것**: template은 영어, Q1의
절은 한국어라 `PROHIBITION_KEPT`는 두 언어가 섞인 문단이 된다. 번역하지 않고
원문 그대로 삽입한 것은 의도적 선택이다(번역 자체가 새로운, 검토되지 않은
저작 행위이므로).

## 5. 응답 스키마와 행동 코딩 (판정 D-H1a-2 = C, D-H1a-3 = C)

### 5.1 응답 스키마 — 중립 관측 어휘

**H1a 전용 스키마 파일**을 둔다. E2.4의 `decision_schema.json`과
`evidence_contract_v1`은 **변경하지 않는다.**

```
decision:           select_type | defer
selected_type:      essential_feature | structural_composition | null
cited_evidence_ids: [...]
rationale:          ...
```

**`source_authority_unresolved`를 hidden 정답으로 두지 않는다.** 이 어휘는
실험 이름일 뿐 채점 대상이 아니다.

### 5.2 행동 코더 — arm-agnostic

후처리기가 각 응답을 **`selection` / `deferral` / `invalid`** 로 분류한다.

- **동일한 코더를 두 arm에 똑같이 적용한다.** arm은 **집계 단계에서만** 쓴다.
- **양쪽 arm 모두 correctness 채점을 하지 않는다.** `semantic_constraints` #11도
  H1a 주평가에는 **적용하지 않는다.**
- `PROHIBITION_KEPT` arm의 지시 준수 여부가 필요하면 **manipulation-check
  지표로 별도 기록**할 수 있으나, **성공률이나 인증 판정에 합산하지 않는다.**

## 6. E2.4 아티팩트 보호 (판정 D-H1a-1 = B)

**E2.4 동결 구현을 소급 변경하지 않는다.** H1a 폴더에 실행 시점의 surface
구현을 고정한 **전용 사본**을 둔다.

- 모듈 로딩은 `spec_from_file_location` + **고유 `sys.modules` 키**를 강제한다.
  이 저장소는 실험 폴더들이 같은 모듈명을 중복 보유해 **한 실험이 남의 코드로
  조용히 실행된 사고**를 겪었다(등록부 [DONE] #6).
- H1a 전용 구현·스키마·프롬프트·코더를 **E2.4와 별도로 해시 고정**한다.
- E2.4의 `_surface.py`·`decision_schema.json`·`contract_prompt.md`는 **불변**.

## 7. 실행 전 확정해야 할 사전등록 항목 — **현재 미완**

판정문은 `deferred: 없음`이지만 **"아래 사전등록 항목이 확정되기 전에는
실행하지 않는다"** 는 단서를 달았다.

**→ 2026-07-30 전부 확정됨.** 전문은
[`PREREGISTRATION.md`](PREREGISTRATION.md), trial 실행 전 커밋.

| # | 항목 | 확정 내용 |
|---|---|---|
| **P1** | 시행 수(N) | **arm당 20, 총 40.** 인증 밴드가 없으므로 N은 합격선이 아니라 관측 해상도로만 정함(trial 1건 = 0.05) |
| **P2** | randomization | 같은 replicate의 두 arm을 **bundle**로 묶어 동시 실행(cold subagent라 arm 순서 효과 없음). bundle 간 순서는 `sha256_blocked_sort`, seed `H1A-fixed-order-v1` |
| **P3** | 모델 parameters | `claude-opus-5`, `tools: []`, cold subagent. **temperature는 이 transport에서 설정 불가** → 모른다는 사실을 기록하고, 절대 수준 대신 arm 간 대비만 보고 |
| **P4** | 제외 기준 | **출력 내용 기반 제외 없음.** 전송·세션 실패만 재실행(outcome 아님), 미완성 bundle만 제외. 스키마 위반은 제외 대상이 **아님** |
| **P5** | **행동 코딩 규칙** | **코더는 `rationale`을 읽지 않는다.** 구조 필드만으로 3분류. 헤지된 선택은 `selection`, 확신에 찬 보류는 `deferral`, 모순 조합은 `invalid`(관대한 해석 금지) |
| **P6** | **invalid 처리** | 제3의 **행동 범주**. 분모에 포함(유효분모는 깨진 출력을 낸 arm을 보상 — E2.4 실측), `invalid_rate` 병기, 재실행·복구 금지 |
| **P7** | **종료 기준** | **결과 방향에 따른 조기 종료 없음.** Stage A(10)는 하네스 4항만 점검하고 select/defer 분포를 보지 않음 → Stage B(30) |

**§0에서 먼저 못박은 것**: H1a는 K=1이라 D-H3C-1이 판정한 구조와 같다 —
추정 가능한 값은 `P(행동 | 고정 packet, 고정 arm, 고정 모델·파라미터)`뿐이고,
**N을 늘려도 이 상한은 올라가지 않는다.** 허용 결론을 결과 보기 전에 고정했다.

> **P5·P6이 가장 중요하다.** 정답이 없는 실험에서 유일한 판정 장치가 행동
> 코더다. 그것이 **결과를 본 뒤에** 정해지면 이 실험은 아무것도 측정하지 못한다.
> E2.4가 채점기 결함으로 겪은 자리와 같다(등록부 [DONE] #13·#16) — 코더에도
> **recall/precision 양방향 테스트**가 필요하다. 판정문도 "결과 확인 전에
> 동결"을 명시했다.

## 8. 다음 행동

| # | 내용 | 상태 |
|---|---|---|
| 1 | **P1~P7 사전등록 확정** | ✅ `PREREGISTRATION.md` |
| 2 | 전용 스키마 `h1a_schema.json` | ✅ 두 arm 동일 variant, 닫힌 enum |
| 3 | 행동 코더 + 양방향 테스트 + 동결 | ✅ `_coder.py`, `test_h1a_coder.py` 38 passed. **교정 18/18 통과** |
| 4a | H1a 전용 `_h1a_surface.py` 사본 + fixture 제작 (칼/철) | ✅ `20f7102` |
| 4b | **독립 리뷰 (제작자와 분리)** | ✅ **완료 — blocker 1 + major 5 발견, 동결 부적합 판정.** `docs/feedback/h1a_fixture_review_20260730.md` |
| 4c | 리뷰 C2~C10 기계적 수정 반영 (fixture 재구성) | ✅ 완료, 커밋 대기. `test_h1a_fixture.py` 23 passed |
| 4d | Q1·Q2 외부 설계 요청 및 판정 | ✅ `DESIGN_DECISION_H1a_manipulation_scope.md` 도착·반영. Q1=B(조작 재정의), Q2=B(진단 게이트) |
| 5 | Q1 반영 — 절 기반 arm 렌더러 + 구조 가드 | ✅ `_h1a_contract.py`, `test_h1a_contract.py` 11 passed |
| 6 | ~~Q2 반영 — anchor-sensitivity 진단(2×2×5=20) 설계·구현·실행~~ | ⛔ **은퇴(2026-08-02, Q6=A).** 구현·테스트까지 완료했으나 앵커 제거로 잴 대상이 사라졌다. 구현체는 `superseded/`, 사유는 `superseded/WHY.md`. 대체: 구조적 no-anchor 가드 |
| 6a | Q3·Q4 반영 — H1a 전용 프롬프트 표면 | ✅ 완료. `h1a_prompt_template.md`로 분리(판정문에서 떼어냄) |
| 6b | Q5~Q8 반영 — 조작 2문장 / 앵커 제거 / warrant defer / ev2 제거 | ✅ 완료 2026-08-02. 게이트 그린(H1a 106 passed) |
| 6c | **3차 독립 리뷰** (Q5~Q8 적용분 재검증) | ✅ **blocker 0.** major 2 + minor 1 즉시 수정·회귀 테스트 고정 |
| 6d | **Q9=A 반영 — L3 한계 문구를 `PREREGISTRATION.md`에 등록** | ⛔ **다음 단계, 미완.** 판정 도착했으나 저장소 반입·등록 미완. fixture·코드 변경 **없음** |
| 7 | 두 arm 최종 프롬프트 렌더링 + `rendered_prompt_sha256` 동결 | 6d 후 |
| 8 | trial subject agent 정의·설치 | 7 후 |
| 9 | **trial 실행** Stage A(10) → 하네스 점검 5항 → Stage B(30) | 8 후, **별도 승인** |

> [DONE] #17의 "agent registry가 세션 시작에 고정" 서술은 **이번 세션에서
> 반증됐다** — E2.4 H3의 trial subject 3종을 세션 중간에 설치해 즉시
> 사용했다. 7번을 새 세션으로 미룰 이유가 없다.

## 9. 초안에서 폐기된 것 (재론 방지용 기록)

| 초안 | 판정 후 | 근거 |
|---|---|---|
| 3-arm (legacy CONTROL 포함) | **2-arm** | legacy가 "보류"를 표현 못 해 종속변수 검열 |
| 정답 있는 실험, `clean_rate`·밴드 인증 | **정답 없음, 행동 분포만** | 규범적 ground truth 부재 |
| `source_authority_unresolved`를 hidden oracle로 | **oracle 없음, 중립 어휘 + 후처리 분류** | correctness 프레이밍 폐기 |
| E2.4 스키마·채점기 확장 재사용 | **H1a 전용 사본·스키마** | 동결 아티팩트 불변 |
| #11을 arm별로 적용 | **양쪽 미적용**, 필요시 manipulation-check | correctness 채점 안 함 |
| "독단 해결 = 사전지식 의존" | **인과 귀속 안 함** | fixture가 두 원인을 분리하지 못함 |

또한 **최초 초안의 "유출 딜레마"(실험 성립 불가 가능성)는 적대 검증에서
반증됐다** — eligibility profile은 모델 payload에 도달하지 않고(실측),
`source_kind`로 `doc`/`code` 구분은 이미 제공된다. 이 프레이밍으로 되돌아가지
말 것. 상세는 `docs/feedback/h1a_source_authority_unresolved_review_20260729.md`.
