# H1a — `source_authority_unresolved` (설계 판정 반영, freeze 전)

- 작성: 2026-07-29 (초안) / **재정의: 2026-07-29 설계 판정 반영**
- 지위: **설계 판정 완료, 사전등록 미완.** 판정 7건은 전부 내려졌으나
  판정문이 "**재정의 필요**"와 함께 **사전등록 7항목(§7)** 을 실행 조건으로
  달았다. 그것이 확정되기 전에는 fixture를 만들지 않고 trial도 돌리지 않는다.
- 설계 판정 원문: [`DESIGN_DECISION.md`](DESIGN_DECISION.md) (판정자: OpenAI Codex, 외부)
- 적대 검증 보고: [`../../docs/feedback/h1a_source_authority_unresolved_review_20260729.md`](../../docs/feedback/h1a_source_authority_unresolved_review_20260729.md)
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
독립 리뷰어가 전수 확인했고 R6b 테스트는 실제로 실행해 통과를 확인했다.

| 측 | 위치 | 텍스트 | 주장 |
|---|---|---|---|
| **문서**(`source_kind: doc`) | `docs/phase_a_implementation_packet.md:102` | `(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)` | 철 = `essential_feature` |
| 〃 보강 | 〃 `:106` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | 예외를 명시 |
| **코드**(`source_kind: code`) | `conceptgate/cg_partwhole.py:36` | `"material_of": "structural_composition",  # Winston stuff-object (has-a)` | 철 = `structural_composition` |
| **테스트**(`source_kind: test`) | `test_semantic_regressions.py::test_r6b_material_feature_not_in_isa_dag` | concept `칼`, feature `철`, type `structural_composition`, `relation_hint="material_of"` | 코드 쪽을 회귀로 고정 |

문서 쪽 이력: 마지막 변경은 `cf58c8c`(패키지 단일화 리팩터)로 상단에 경고
배너만 추가했고 **본문 주장은 미수정**. 내용은 `4e0214c` 시점 그대로다.

> **주의**: 위 "문서가 낡았다"는 서술은 **하네스와 이 문서를 읽는 사람의
> 지식**이다. **모델에게는 전달되지 않는다.** 모델이 받는 것은 `source_kind`와
> `text`뿐이다(§5).

C1~C4: C2(인스턴스 결박) 충족, C3(비순환) 충족, C4(선행성) `git log`로 확인.
**C1(liveness)은 하네스가 확정하고 모델에 넘기지 않는다** — 넘기면 이 실험의
조작 변수가 오염된다.

## 4. arm — 2개 (판정 D-H1a-6 = B)

| arm | 계약 서문 | 스키마 |
|---|---|---|
| `PROHIBITION_KEPT` | E2.4 서문 그대로 (금지 문장 **포함**) | H1a 전용 스키마 (동일) |
| `PROHIBITION_REMOVED` | 지정된 한 문장만 **삭제** | H1a 전용 스키마 (동일) |

**legacy CONTROL arm은 제외됐다.** 판정 근거: legacy 스키마의 `decision` enum은
`report_done`/`repair`/`request_evidence`뿐이라 **"보류"를 표현할 수 없고**,
이 실험의 핵심 종속변수를 **구조적으로 검열**한다.

두 arm은 **같은 fixture, 같은 모델, 같은 parameters, 같은 응답 스키마**를 쓴다.
**arm 간 유일한 차이는 지정된 금지 문장 하나여야 한다.**

### 4.1 최소편집 절차 (판정 D-H1a-5 = A)

대상 문단은 두 문장이 붙어 있다:

```
이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.
```

- **삭제**: `모델은 출처의 liveness나 우선순위를 재판정하지 않는다.` — 이 문장만
- **유지(양쪽 arm 공통)**: `이 packet의 evidence item은 실행 전
  provenance/eligibility 검증을 통과했다.`

앞 문장까지 지우면 "검증이 끝났다"는 사실 자체가 사라져 **다른 변수가 함께
바뀐다.** 두 프롬프트가 **정확히 그 한 문장의 유무로만** 다름을 **byte-level
테스트로 고정**하고, 각 `rendered_prompt_sha256`을 동결한다.

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

| # | 항목 | 상태 |
|---|---|---|
| **P1** | 시행 수(N) | 미정 |
| **P2** | randomization | 미정 |
| **P3** | 모델 parameters (모델명·temperature 등, 두 arm 동일) | 미정 |
| **P4** | 제외 기준 | 미정 |
| **P5** | **행동 코딩 규칙** (selection/deferral/invalid 판정 기준) | 미정 |
| **P6** | **invalid-output 처리 규칙** | 미정 |
| **P7** | **종료 기준** (인증 밴드를 안 쓰므로 별도 정의 필요) | 미정 |

> **P5·P6이 가장 중요하다.** 정답이 없는 실험에서 유일한 판정 장치가 행동
> 코더다. 그것이 **결과를 본 뒤에** 정해지면 이 실험은 아무것도 측정하지 못한다.
> E2.4가 채점기 결함으로 겪은 자리와 같다(등록부 [DONE] #13·#16) — 코더에도
> **recall/precision 양방향 테스트**가 필요하다. 판정문도 "결과 확인 전에
> 동결"을 명시했다.

## 8. 다음 행동

| # | 내용 | 세션 |
|---|---|---|
| 1 | **P1~P7 사전등록 확정** — 특히 P5·P6 행동 코딩 규칙 | 지금 |
| 2 | H1a 전용 `_surface.py` 사본 + 전용 스키마 파일 작성 | P1~P7 후 |
| 3 | fixture 제작 (칼/철) → **독립 리뷰(제작자와 분리)** | 2 후 |
| 4 | 두 arm 프롬프트 생성 + byte-level diff 테스트 + 해시 동결 | 3 후 |
| 5 | 행동 코더 구현 + **양방향 테스트** + 동결 | 3과 병행 가능 |
| 6 | trial subject agent 정의·설치 | 4·5 후 |
| 7 | **trial 실행** | **6 이후 새 세션** (agent registry가 세션 시작에 고정, 등록부 [DONE] #17) |

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
