# H1a 설계 판정 — 수신 기록 (2026-07-29)

- 수신: 2026-07-29
- 판정자: **OpenAI Codex** (외부 workspace, 저장소 접근 없음)
- 요청서: [`DESIGN_REQUEST_PROMPT.md`](DESIGN_REQUEST_PROMPT.md) (자족형 프롬프트로 전달)
- 판정 범위: 요청한 7건 **전부 판정됨.** `deferred` 없음
- 결론: **재정의 필요** — 재료와 2-arm 대조는 유효하나, 정답·인증 프레이밍을
  서술적 행동 측정으로 바꾸고 사전등록을 마친 뒤에만 실행

이 파일은 **판정 원문의 보존본**이다. 해설이나 요약이 아니다. 아래 §1은
받은 그대로이고, §2·§3은 운영 세션이 붙인 실행 해석이므로 판정과 구분해 읽어라.

---

## 1. 판정 원문 (verbatim)

> 설계 판정은 "2-arm·서술적 탐색 실험"입니다. H1a는 정답률이나 인증 class를
> 측정하지 않고, 금지 문장 제거가 `보류/선택` 행동 분포에 미치는 영향만
> 측정해야 합니다.

```text
DESIGN DECISION — H1a source_authority_unresolved
decided_by: OpenAI Codex
date: 2026-07-29

D-H1a-4 (채점 극성): C
근거:
H1a에는 보류와 우열 판정 중 무엇이 규범적으로 옳은지에 대한 독립된
ground truth가 없다. 어느 쪽도 성공/실패로 정하지 않고 행동 분포로 기록한다.
E2.4의 합격 임계·인증 band는 사용하지 않는다.

D-H1a-6 (arm 개수): B
근거:
legacy CONTROL은 보류를 표현할 수 없어 핵심 종속변수를 구조적으로
검열한다. 동일한 H1a 스키마를 사용하는 "금지 유지"와 "금지 제거"
2개 arm만 비교한다.

D-H1a-1 (분기 위치): B
근거:
E2.4 동결 구현을 소급 변경하지 않는다. H1a 폴더에 실험 시점의
surface 구현을 고정한 전용 사본을 둔다. 모듈명 충돌을 방지하기 위해
고유 모듈명 또는 파일 경로 기반 로딩을 강제한다.

D-H1a-2 (판정 어휘): C
근거:
H1a 전용 스키마 파일을 둔다. E2.4 decision_schema.json과
evidence_contract_v1은 변경하지 않는다. H1a에는 correctness oracle이
아닌 중립적 관측 어휘를 정의한다.

권장 응답 구조:
  decision: select_type | defer
  selected_type: essential_feature | structural_composition | null
  cited_evidence_ids: [...]
  rationale: ...

후처리기가 이를 selection / deferral / invalid로 분류한다.
source_authority_unresolved를 hidden 정답으로 두지 않는다.

D-H1a-3 (arm별 채점): C
근거:
두 arm 모두 correctness 채점을 하지 않는다. 기존 규칙 #11도 H1a
주평가에는 적용하지 않는다. 동일한 arm-agnostic 행동 코더로 결과를
분류하고 arm은 집계 단계에서만 사용한다.

금지 유지 arm의 지시 준수 여부가 필요하면 별도의 manipulation-check
지표로 기록할 수 있으나, 성공률이나 인증 판정에는 합산하지 않는다.

D-H1a-5 (최소편집 절차): A
근거:
"모델은 출처의 liveness나 우선순위를 재판정하지 않는다." 문장만
금지 제거 arm에서 삭제한다. 앞 문장인 provenance/eligibility 검증
통과 문장은 양쪽에 유지한다.

두 프롬프트가 정확히 해당 문장 하나의 유무로만 다름을 byte-level
테스트로 고정하고, 각 rendered prompt hash를 동결한다.

D-H1a-7 (인과 귀속): A
근거:
현재 fixture는 source_kind와 원문 내부 표현을 함께 포함하므로,
선택 행동을 사전지식 의존이나 실제 liveness 판정으로 인과 귀속할
수 없다. "선택/보류 행동과 그 rationale이 관측됐다"까지만 결론낸다.

deferred:
  없음. 단, 아래 사전등록 항목이 확정되기 전에는 실행하지 않는다.

new_constraints:
  - H1a는 탐색적·서술적 실험이며 E2.4 인증 체계에 포함하지 않는다.
  - 두 arm은 같은 fixture, 모델, parameters, 응답 스키마를 사용한다.
  - arm 간 유일한 prompt 차이는 지정된 금지 문장 하나여야 한다.
  - hidden correctness oracle과 screened_PASS/FAIL band를 사용하지 않는다.
  - 실행 전 시행 수, randomization, parameters, 제외 기준을 사전등록한다.
  - 행동 코딩 규칙과 invalid-output 처리 규칙을 결과 확인 전에 동결한다.
  - 모델에게 liveness, supersession, qualification profile을 노출하지 않는다.
  - source_kind는 기존 허용 범위에서 동일하게 노출한다.
  - H1a 전용 구현·스키마·프롬프트·코더를 E2.4와 별도로 해시 고정한다.
  - 동일 fixture의 반복 시행 결과를 일반적인 모델 성향으로 일반화하지 않는다.
  - rationale은 행동 해석 자료일 뿐 판단 원인의 신뢰할 수 있는 자기보고로
    취급하지 않는다.

실험 중단 여부:
  재정의 필요

사유:
  재료와 2-arm 대조는 사용 가능하다. 다만 현재의 정답·인증 프레이밍을
  서술적 행동 측정으로 바꾸고 H1a 전용 스키마, 행동 코더, 종료 기준을
  사전등록한 뒤에만 실행을 계속한다.
```

### 1.1 해석 경계 (판정문에 함께 온 것 — verbatim)

> 중요한 해석 경계가 하나 있습니다. 이 실험에서 모델은 실제 liveness 정보를
> 보지 않습니다. 따라서 H1a가 직접 측정하는 것은 "live 코드를 정확히
> 알아보는가"가 아니라, **문서·코드·테스트라는 출처 종류가 충돌하는 상황에서
> 금지 문장의 유무가 선택과 보류 행동에 어떤 차이를 만드는가**입니다.

**이 문단이 이 실험에서 가장 무거운 제약이다.** 결과를 서술할 때 "모델이
stale 문서를 알아봤다/못 알아봤다"는 표현을 쓰면 안 된다 — 모델은 무엇이
stale인지 알 수단을 받지 않는다. 관측 가능한 것은 `source_kind`가 다른 두
텍스트가 충돌할 때의 **선택/보류 행동**뿐이다.

---

## 2. 판정이 뒤집은 것 (운영 세션의 실행 해석 — 판정문 아님)

| 초안이 전제한 것 | 판정 후 |
|---|---|
| 3-arm (CONTROL_REPO 포함) | **2-arm.** legacy CONTROL은 "보류"를 표현할 수 없어 종속변수를 구조적으로 검열한다(D-H1a-6) |
| 정답이 있는 실험, `clean_rate`·밴드로 인증 | **정답 없음.** 행동 분포만 기록. E2.4 인증 체계에 포함하지 않는다(D-H1a-4) |
| verdict 어휘 `source_authority_unresolved`를 hidden oracle로 | **hidden oracle을 두지 않는다.** 중립 관측 어휘 + 후처리 분류(D-H1a-2) |
| E2.4 계약 스키마·채점기를 확장해 재사용 | **H1a 전용 스키마 파일 + 전용 사본.** E2.4 아티팩트 불변(D-H1a-1·2) |
| `semantic_constraints` #11을 arm별로 적용 | **양쪽 arm 모두 미적용.** 필요하면 manipulation-check로만 별도 기록(D-H1a-3) |
| "독단 해결 = 사전지식 의존" | **인과 귀속하지 않는다.** 관측 수준까지만(D-H1a-7) |

### 2.1 실험 이름과 측정 대상의 간극 (기록해 둘 것)

폴더명은 `source_authority_unresolved`이지만, §1.1에 따르면 실제 측정 대상은
**"출처 종류 충돌 상황에서 금지 문장 유무가 만드는 행동 차이"** 다. 이름이
측정보다 넓다. 이름을 바꾸지는 않되(지시문이 이 이름을 지정했다), **결과
서술에서 이름이 함의하는 것 이상을 주장하지 않는다.**

---

## 3. 실행 전 남은 사전등록 항목 (판정문 `new_constraints`에서 도출)

판정은 `deferred: 없음`이지만 **"아래 사전등록 항목이 확정되기 전에는 실행하지
않는다"** 는 단서가 붙었다. 확정해야 할 것:

| # | 항목 | 판정문 근거 |
|---|---|---|
| P1 | **시행 수(N)** | "실행 전 시행 수 ... 사전등록한다" |
| P2 | **randomization** | 동상 |
| P3 | **모델 parameters** (모델명, temperature 등) | 동상. 두 arm이 **동일**해야 함 |
| P4 | **제외 기준** | 동상 |
| P5 | **행동 코딩 규칙** — selection / deferral / invalid 판정 기준 | "행동 코딩 규칙과 invalid-output 처리 규칙을 **결과 확인 전에 동결**한다" |
| P6 | **invalid-output 처리 규칙** | 동상 |
| P7 | **종료 기준** — 인증 밴드를 안 쓰므로 "언제 끝나는가"를 따로 정의 | "종료 기준을 사전등록한 뒤에만 실행" |

**P5·P6이 특히 중요하다.** 정답이 없는 실험에서 유일한 판정 장치가 행동
코더이므로, 그것이 결과를 본 뒤에 정해지면 이 실험은 아무것도 측정하지 못한다.
E2.4가 채점기 결함으로 겪은 문제(등록부 [DONE] #13·#16)와 같은 자리다 —
코더에도 recall/precision 양방향 테스트가 필요하다.

## 4. 이 판정이 부과한 구현 제약

- H1a 폴더에 `_surface.py` **전용 사본**. 로딩은 `spec_from_file_location` +
  **고유 `sys.modules` 키**(등록부 [DONE] #6 재발 방지).
- H1a 전용 스키마 파일. E2.4의 `decision_schema.json`·`evidence_contract_v1`
  **불변**.
- 두 arm 프롬프트의 diff가 **정확히 지정된 한 문장**임을 byte-level 테스트로
  고정하고, 각 rendered prompt hash를 동결.
- 모델에게 liveness·supersession·qualification profile **미노출**.
  `source_kind`는 기존 허용 범위 그대로 노출(이미 `doc`/`code`/`test` 구분 제공).
- H1a 전용 구현·스키마·프롬프트·코더를 E2.4와 **별도로 해시 고정**.
