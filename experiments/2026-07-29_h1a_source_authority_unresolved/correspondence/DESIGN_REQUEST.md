# 설계 판정 요청서 — H1a `source_authority_unresolved`

- 발신: E2.4/H1a 실험 운영 세션 (worktree `concept-gate-e2.2-wt`, 브랜치 `codex/e2.4-contract-repo-design`)
- 작성: 2026-07-29
- 요청: **설계 판정 7건.** 그중 **선행 2건**(D-H1a-4, D-H1a-6)이 나머지 범위를 결정한다
- 회신 형식: §7
- **이 문서는 자족적으로 설계됐다** — 판정에 필요한 실측을 전부 본문에 담았다.
  저장소를 조사하지 않아도 판정할 수 있고, 조사하고 싶다면 §6에 재현 명령이 있다

## 왜 판정이 필요한가 (30초 요약)

H1a는 "stale 문서와 live 코드가 **같은 인스턴스**에 대해 상충하는 type을
주장할 때, 클라이언트가 독단으로 해결하지 않고 보류하는가"를 측정하려는
실험이다. 재료는 확보됐고(칼/철, 인스턴스 정확 일치) 검증도 통과했다.

막힌 지점은 재료가 아니라 **실험을 어떻게 채점하고 어디에 구현하느냐**다.
특히 이 실험은 E2.4가 **금지 사항으로 규정한 행동**(모델이 출처 우열을
재판정하는 것)을 **측정 대상으로 바꾸려** 하기 때문에, 계약·스키마·채점기를
그대로 재사용할 수 없다.

**판정 없이 진행하면**: fixture를 만들 수는 있으나 무엇을 성공으로 볼지가
사전에 고정되지 않아, 어떤 결과가 나오든 사후 합리화가 가능해진다. 이
프로젝트가 이미 겪은 실패 유형이다(등록부 [DONE] #2, #10, #11).

---

## 1. 실험 요지

### 1.1 가설

stale 문서와 live 코드가 같은 인스턴스에 대해 상충하는 feature type을 주장할
때, 클라이언트는 어느 쪽이 더 권위 있는지를 **스스로 판정하지 않고 보류**하는가?

### 1.2 왜 E2.4에서 분리됐나

2026-07-29 외부 운영 지시 §3(네 번째 항목). 원문은 저장소에 커밋돼 있다
(`docs/DIRECTIVE_2026-07-29_operations_change.md`):

> stale source와 live source의 권위 충돌은 E2.4 conflicting_evidence로
> 처리하지 않습니다. 이는 향후 별도 source_authority_unresolved 실험
> 대상입니다.

### 1.3 구조적 긴장 — 이 요청서의 근원

E2.4의 계약 서문(`contract_prompt.md:24-25`)은 모델에게 이렇게 지시한다:

> 이 packet의 evidence item은 실행 전 provenance/eligibility 검증을 통과했다.
> **모델은 출처의 liveness나 우선순위를 재판정하지 않는다.**

그리고 `semantic_constraints` #11이 그 위반을 **오답으로 채점**한다:

> The model does not adjudicate source liveness or precedence (see
> contract_prompt.md preamble); a rationale that decides between two items on
> the grounds that one source is newer, still in use, or more authoritative is
> out of contract and **must be scored as such** rather than credited as a
> conflict resolution.

**즉 E2.4에서 이 행동은 "측정 대상"이 아니라 "금지 사항"이다.** H1a는 같은
행동을 측정하려 하므로 계약을 그대로 쓸 수 없고, 어디까지 바꿀 것인가가
판정 대상이다.

### 1.4 재료 (검증 완료)

인스턴스가 `칼`/`철`로 **정확히 일치**하는 실제 충돌이다. 합성이 아니다.

| 측 | 위치 | 텍스트(원문) | 주장 |
|---|---|---|---|
| stale 문서 | `docs/phase_a_implementation_packet.md:102` | `(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)` | 철 = `essential_feature` |
| 〃 보강 | 〃 `:106` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | 예외를 명시적으로 못박음 |
| live 코드 | `conceptgate/cg_partwhole.py:36` | `"material_of": "structural_composition",  # Winston stuff-object (has-a)` | 철 = `structural_composition` |
| 통과 중 테스트 | `test_semantic_regressions.py:135` `test_r6b_material_feature_not_in_isa_dag` | concept `칼`, feature `철`, type `structural_composition`, `relation_hint="material_of"` | live 쪽을 회귀로 고정 |

**문서가 superseded임의 근거**: 마지막 변경은 `cf58c8c`(패키지 단일화 리팩터)로
문서 상단에 경고 배너만 추가했고 **본문 주장은 미수정**. 내용은 `4e0214c`
시점 그대로이며 이후 코드가 반대 방향으로 확정됐다.

**검증 상태**: 위 4행과 이력 주장을 독립 reviewer가 전수 확인했고,
R6b 테스트는 **실제로 실행해 통과**를 확인했다(10건 중 9건 CONFIRMED,
1건은 §2에서 처리됨).

---

## 2. 이미 확정된 것 — 재논의 불필요

### 2.1 최초 초안의 "유출 딜레마"는 반증됐다

초안은 D-H1a-1에서 *"새 eligibility profile을 만들면 (a) 모델에 보일 때
오라클 유출이고 (b) 숨기면 모델이 두 텍스트를 구분할 수 없어 실험이 성립하지
않는다"* 고 주장했다. **두 갈래 모두 사실이 아니었다.**

| 최초 주장 | 실측 결과 |
|---|---|
| (a) profile이 모델에 보이면 유출 | **틀림.** profile은 qualification manifest에만 존재하고 payload에 도달하지 않는다. 4종 문자열 전부 payload에 부재 (M1) |
| (b) 숨기면 구분 불가 | **틀림.** `source_kind`가 모델 화이트리스트에 있고 `doc`/`code`가 별개 값이다. 출처 **종류** 구분은 이미 제공된다 (M2) |

**이 프레이밍으로 되돌아가지 마시라.** 잘못된 전제 위에서 판정이 내려지는
것을 막기 위해 오류 경위를 그대로 남긴다. 상세는
`docs/feedback/h1a_source_authority_unresolved_review_20260729.md`.

### 2.2 적대 검증에서 제기된 blocker 2건은 기각됐다

4축 적대 검증(코드 실측 / 실험설계 이론 / 외부 지침 / 프로젝트 제약)에서
blocker 2건이 제기됐고, lead가 직접 재실측해 **둘 다 기각**했다.

| 제기된 blocker | 재실측 결과 |
|---|---|
| "profile 확장이 E2.4 동결 해시를 깬다" | **기각.** `docs/` 분기 주입 후 3 fixture의 rendered/payload/qualification 해시가 전부 불변이고 동결본과 일치 (M3) |
| "지시문 §3 인용이 틀렸다" | **기각.** 인용은 정확(§3의 네 번째 항목). 제기자가 등록부 요약만 보고 원문을 못 봤다. 단 "원문이 저장소에 없다"는 부수 지적은 타당해 원문을 커밋함 |

---

## 3. 판정 요청 항목

각 항목은 **질문 → 왜 결정 사항인가 → 선택지 → 실측 제약 → 권고 → 미판정 시
귀결** 순서로 쓴다. **권고 블록은 비구속이며 앵커링을 피하려고 분리해 두었다.**

---

### D-H1a-4 【최우선】 채점 극성 — 독단 해결은 정답인가 오답인가

#### 질문
liveness 조항을 제거한 arm에서 모델이 "코드가 살아 있으니 코드를 택한다"고
판단했을 때, 그 trial을 **성공으로 채점하는가 실패로 채점하는가?**

#### 왜 결정 사항인가
E2.4는 이 행동의 극성이 명확하다 — #11이 "위반 = 오답"이라고 못박았다.
H1a는 같은 행동을 **측정 대상**으로 바꾸는데, 그러면 극성이 자동으로
정해지지 않는다. 초안 §2는 "독단 해결 = 나쁜 신호(사전지식 의존)"로 읽히지만
어떤 스키마·채점기에도 고정돼 있지 않다.

**결과 해석 기준이 사전에 없으면 무엇이 관측되든 설명이 가능해진다.** 이
프로젝트는 이미 그 실패를 겪었다(등록부 [DONE] #2 "나머지 3개는 clean이라는
거짓 보고", #10·#11의 "근거 수치가 legacy_leaky").

#### 선택지

| 안 | 채점 규칙 | 이 실험이 답하는 질문 | 비용·위험 |
|---|---|---|---|
| **(A) 보류=정답** | 보류(abstain류)만 clean. 독단 해결은 실패 | "계약이 없어도 모델이 스스로 자제하는가" | 금지 조항을 뺀 arm에서 자제를 요구하는 것이 공정한가? 지시 없이 자제를 기대하는 셈 |
| **(B) 보류=오답** | 우열 판정을 하되 **근거를 evidence에서 대는 것**만 clean | "우열 판정을 시켰을 때 근거 있게 하는가" | E2.4 #11과 정면 배치. 같은 저장소 안에 반대 극성 두 개가 공존 |
| **(C) 극성 없음 — 서술적 측정** | 정답/오답을 두지 않고 **행동 분포**만 기록(보류율 / 우열판정율 / 근거유형 분포) | "무엇이 일어나는가" (탐색적) | 인증(screened_PASS) 개념을 쓸 수 없음. threshold·밴드 체계가 적용 불가 |
| **(D) arm별 극성 분리** | SILENT arm은 보류=정답(#11 유지), OPEN arm은 (C)로 서술적 | 두 질문을 한 실험에서 | 채점기가 arm별로 다른 규칙 → D-H1a-3와 결합 |

#### 실측 제약

- **M9**: `semantic_constraints`는 arm 조건이 없는 **전역 배열**이고,
  `_score.py`의 `conformance()`는 arm 인자를 받지 않는다. (A)·(B)를 arm별로
  다르게 적용하려면 채점기 구조 변경이 필요하다.
- 현행 인증 체계는 `clean_rate ≥ 0.90`(threshold)과 3구간 밴드
  (`screened_PASS` / `ambiguous` / `screened_FAIL`)에 의존한다. (C)를 택하면
  **이 체계를 쓸 수 없고** 사전등록 문서에 별도 판정 기준이 필요하다.
- E2.4 cohort는 현재 #11 리뷰(D4) 진행 중이다. (B)를 택하면 같은 저장소에서
  #11이 한쪽에선 오답, 다른 쪽에선 정답이 되므로 **문서에 그 이유가 명시돼야**
  후속 세션이 혼동하지 않는다.

#### 권고 (비구속 — 앵커링 주의)

> **(C) 또는 (D)를 권한다.** 이유: H1a는 아직 "무엇이 옳은 행동인가"에 대한
> 사전 지식이 없는 상태다. E2.4는 옳은 행동을 계약으로 **정의한 뒤** 준수를
> 측정했지만, H1a는 그 정의 자체가 열려 있다. 극성을 지금 못박으면 그것은
> 측정이 아니라 가정이 된다.
>
> 다만 (C)는 인증 체계를 못 쓰므로 "이 실험은 무엇으로 종료되는가"를 따로
> 정의해야 한다. 그 부담을 피하려면 (D)가 절충이다.
>
> *이 권고는 판정 권한이 없으며, 반대 결론이 나와도 그대로 따른다.*

#### 미판정 시 귀결
D-H1a-2(verdict 어휘)와 D-H1a-3(arm별 제약)이 **결정 불가**다. verdict 어휘는
극성을 표현하는 수단이고, arm별 제약 필요 여부는 극성이 arm마다 다른지에
달렸기 때문이다.

---

### D-H1a-6 【선행】 arm 개수 — 3-arm 유지 vs 2-arm 축소

#### 질문
`CONTROL_REPO`(legacy 프롬프트) arm을 유지하는가, `CONTRACT_REPO_SILENT` /
`CONTRACT_REPO_OPEN` 2-arm으로 축소하는가?

#### 왜 결정 사항인가
초안 §4는 3-arm을 제안했으나 필요성을 논증하지 않았다. CLAUDE.md의 Ponytail
Rules 1번은 **YAGNI — "이게 존재할 필요가 있는가?"** 이고, "No abstraction
unless explicitly requested"가 명시돼 있다.

#### 선택지

| 안 | 구성 | 분리되는 변수 | 비용 |
|---|---|---|---|
| **(A) 3-arm 유지** | CONTROL(legacy) + SILENT + OPEN | 계약 유무 + 금지조항 유무 | cell 수 1.5배. CONTROL 해석에 M5 문제 |
| **(B) 2-arm 축소** | SILENT + OPEN | 금지조항 유무만 | §2 가설에 직접 답함. 기저선 없음 |
| **(C) 3-arm이되 CONTROL을 legacy가 아닌 계약-무 arm으로** | CONTRACT 스키마 + 계약 문구 없는 프롬프트 | 계약 유무를 같은 스키마 위에서 | 새 프롬프트 작성 필요 |

#### 실측 제약

- **M5 (결정적)**: legacy 스키마의 `decision` enum은
  `["report_done", "repair", "request_evidence"]` 로 **`abstain` 어휘가
  아예 없다.** H1a의 핵심 관측이 "보류하는가"인데, CONTROL arm은
  **보류를 표현할 수단이 구조적으로 없다.** 이 arm에서 "보류하지 않았다"는
  관측은 모델의 행동이 아니라 스키마의 제약일 수 있다.
- 같은 문제를 E2.4가 이미 기록했다 (`docs/HANDOFF.md`): *"legacy 스키마의
  선택지는 `report_done`/`repair`/`request_evidence`로 `abstain` 어휘 자체가
  없어 유출 문구가 그들의 선택지에 직접 매핑되지도 않는다."*
- **M4**: `arm_schema_map`이 이미 존재하므로 arm을 추가·제거하는 것 자체는
  기존 구조 안에서 가능하다. 새 추상화가 아니다.

#### 권고 (비구속 — 앵커링 주의)

> **(B) 2-arm 축소를 권한다.** M5가 결정적이다 — CONTROL arm에서 나온
> "보류하지 않음"은 해석 불가능한 관측이다. §2 가설("보류하는가")은
> SILENT vs OPEN 대조로 직접 답할 수 있고, 그것이 YAGNI 사다리의 첫 단이다.
>
> 기저선이 꼭 필요하다면 (C)가 (A)보다 낫다 — 같은 스키마 위에서 계약 유무만
> 바뀌므로 교란이 적다.
>
> *비구속.*

#### 미판정 시 귀결
D-H1a-3(arm별 제약 집합)과 D-H1a-5(최소편집 절차)의 **범위가 확정되지 않는다.**
2-arm이면 두 항목 모두 훨씬 작아지거나 소멸할 수 있다.

---

### D-H1a-1 profile 분기를 어디에 넣는가

#### 질문
`docs/` 경로를 받아들이는 eligibility profile 분기를 **E2.4의 동결
`_surface.py`에 추가**하는가, **H1a 전용 사본**을 두는가?

#### 왜 결정 사항인가
현재 `_eligibility_profile()`은 `docs/` 경로에 대해 예외를 던진다:

```
docs/phase_a_implementation_packet.md -> SurfaceError: no eligibility profile applies.
    Sources must be live package code, a test, a frozen experiment artifact,
    or a commit record.
```

이건 버그가 아니라 E2.4의 **의도된 제약**이다(liveness를 모델 이전에
확정하려고 소스를 좁혔다). H1a는 superseded 문서를 써야 하므로 분기가 필요하다.

여기서 두 규칙이 충돌한다:
- **방법론 규칙 1** — 동결 아티팩트는 실험별로 고정되고 소급 수정하지 않는다
- **CLAUDE.md Ponytail 2번** — "Codebase reuse: 이미 이 코드베이스에 있으면 재사용하라"

#### 선택지

| 안 | 내용 | 결과 | 비용 |
|---|---|---|---|
| **(A) E2.4 `_surface.py` 직접 수정** | `superseded_document` profile 추가 | 한 벌만 유지 | E2.4 동결본을 소급 수정. 방법론 규칙 1 위반 소지 |
| **(B) H1a 폴더에 `_surface.py` 사본** | 복사 후 분기 추가 | E2.4 불변 | 코드 중복. 이후 두 벌이 드리프트 |
| **(C) E2.4 `_surface.py`를 import해 H1a에서 확장** | H1a가 얇은 래퍼로 profile만 주입 | 중복 없음, E2.4 불변 | 실험 간 코드 의존 발생 — 이 저장소가 지금까지 피해온 형태 |

#### 실측 제약

- **M3**: `docs/` 분기를 넣어도 E2.4의 동결 해시는 **전부 불변**이다.
  실측(3 fixture 전부):
  ```
  E24-F-01  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
  E24-F-02  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
  E24-F-03  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
  ```
  기존 E2.4 fixture 중 `docs/` 경로를 쓰는 것이 없어 profile 산출이 바뀌지
  않고, profile은 payload에도 들어가지 않기 때문이다(M1). **즉 (A)는
  기술적으로는 안전하다.** 남는 것은 규율 문제다.
- **등록부 [DONE] #6**: 실험 폴더들이 같은 모듈명(`_cert_core.py` 6개,
  `evaluate.py` 10개)을 중복 보유해 한 인터프리터에서 **남의 모듈로 조용히
  실행된 사고**가 실제로 있었다. (B)를 택하면 이 위험이 재발할 수 있으므로,
  로딩은 반드시 `spec_from_file_location` + **고유 `sys.modules` 키**를 써야
  한다(E2.4가 `e24_surface_cohort`/`e24_surface_review`/`e24_surface_protocol`로
  이미 쓰는 패턴).
- **중복은 이 저장소에서 버그가 아니라 동결 규율의 산물**이다 —
  `scripts/run_gates.py`가 실험별 프로세스 격리로 대응하고 있다.

#### 권고 (비구속 — 앵커링 주의)

> **(B) 사본을 권한다.** M3가 (A)의 기술적 안전성을 보였지만, 이 저장소의
> 동결 규율은 "기술적으로 안 깨지니까 괜찮다"가 아니라 "결과가 설계를 소급
> 수정하지 못하게 한다"는 원칙이다. E2.4는 지금 D4 인증 절차가 진행 중이라
> 특히 그렇다.
>
> (C)는 중복을 없애지만 실험 간 의존을 만든다 — E2.4를 고치면 H1a가 조용히
> 바뀌는 구조이고, 그것이 [DONE] #6이 경고한 것과 같은 종류의 결합이다.
>
> *비구속.*

#### 미판정 시 귀결
fixture를 만들 수 없다. `qualify_fixture()`가 재료를 거부한다.

---

### D-H1a-2 verdict 어휘를 어디에 정의하는가

#### 질문
H1a의 판정 어휘(가칭 `source_authority_unresolved`)를 **`evidence_contract_v1`
enum 확장** / **새 variant 신설** / **기존 어휘 재사용** 중 무엇으로 하는가?

#### 왜 결정 사항인가
지시문 §3이 `conflicting_evidence` 사용을 금지했으므로 기존 어휘를 그대로 쓸
수 없다. 그런데 `decision_schema.json`은 E2.4 cohort가 해시로 고정한 파일이다.

#### 선택지

| 안 | 내용 | 결과 |
|---|---|---|
| **(A) v1 enum에 값 추가** | `contract_verdict` enum에 추가 | **하드 브레이크** (아래 M6) |
| **(B) 새 variant + `arm_schema_map` 항목** | `evidence_contract_v2_h1a` 신설 | 안전 (M7). `arm_schema_map`이 이미 있는 패턴 |
| **(C) H1a 전용 스키마 파일 분리** | H1a 폴더에 별도 `decision_schema.json` | E2.4 파일 완전 불변. 중복 |

#### 실측 제약

- **M6 — (A)는 하드 브레이크**: `evidence_contract_v1` **본체**를 수정하면
  `_cohort.py`의 `transport_schema()` 산출이 바뀌고 → 커밋된
  `e2.4-contract-decider.md`가 stale이 되어 →
  `test_protocol.py::test_trial_subject_definition_matches_the_decision_schema`가
  **실패**하고 `_cohort.py freeze`가 **거부**한다. E2.4 재동결이 강제된다.
- **M7 — (B)는 안전**: 새 variant 추가나 `arm_schema_map` 항목 추가는
  `transport_schema()`(= v1 본체만 추출)를 바꾸지 않으므로 agent 파일이 stale이
  되지 않고 테스트가 통과한다. 실측:
  ```
  시나리오 B: presented_schema_sha256 여전히 일치 = True
  ```
- **M8 — 단, 파일 전체 해시는 어느 안이든 바뀐다**: `decision_schema_sha256`은
  파일 전체를 해싱하므로 (B)에서도 동결 기록값과 불일치하게 된다.
  **그러나 이 값을 재검증하는 코드가 없다** — `record()`는
  `rendered_prompt_sha256`만 대조하고, `test_surface.py:307-310`은 길이가 64인지만
  단언한다. 따라서 런타임 실패는 없고 **provenance 주장만 약해진다.**
  이 약화를 감수할지, (C)로 회피할지가 판정 사항이다.
- **M4**: `arm_schema_map`은 이미
  `{"CONTROL_REPO": "legacy_decision", "A_REPO": "legacy_decision",
  "CONTRACT_REPO": "evidence_contract_v1"}` 로 존재한다. arm별 스키마 선택은
  **새 추상화가 아니라 기존 개념**이다.

#### 권고 (비구속 — 앵커링 주의)

> **D-H1a-1의 판정과 묶어서 결정하기를 권한다.** (B)와 (C)는 각각 D-H1a-1의
> (A)/(C)와 (B)에 대응한다 — 코드와 스키마가 같은 곳에 있어야 실험 폴더가
> 자족적이다. 둘을 따로 정하면 "코드는 사본인데 스키마는 공유" 같은 어중간한
> 상태가 나온다.
>
> M8의 provenance 약화는 (C)를 택하면 전부 사라진다.
>
> *비구속.*

#### 미판정 시 귀결
fixture의 hidden oracle을 쓸 수 없다(어떤 verdict를 기대값으로 적을지 미정).

---

### D-H1a-3 arm별 제약 집합을 만드는가

#### 질문
`semantic_constraints` #11을 **arm에 따라 켜고 끄는 구조**를 도입하는가?

#### 왜 결정 사항인가
`CONTRACT_REPO_OPEN` arm은 계약 서문에서 liveness 조항을 빼는 arm이다. 그러면
그 arm에서는 #11("모델은 출처 우열을 재판정하지 않는다")이 **적용되지 않아야**
한다 — 하지 않기로 한 지시를 어겼다고 채점할 수 없기 때문이다.

#### 선택지

| 안 | 내용 | 비용 |
|---|---|---|
| **(A) 제약 집합을 arm별로 분기** | `conformance(out, payload, arm)` 로 확장 | 채점기에 새 조건부 경로. YAGNI 저촉 소지 |
| **(B) arm마다 별도 제약 배열** | variant마다 `semantic_constraints`를 따로 둠 | 스키마 구조 변경. 다만 `arm_schema_map`이 이미 arm별 분기를 하고 있음(M4) |
| **(C) OPEN arm은 conformance 채점을 하지 않음** | 서술적 측정만(D-H1a-4의 (C)와 결합) | 구조 변경 없음. 대신 그 arm은 인증 불가 |

#### 실측 제약

- **M9**: `semantic_constraints`는 `decision_schema.json` **최상위의 평평한
  배열**이고 arm 조건이 없다. `_score.py`의 `conformance(out, payload)`는
  arm 인자를 받지 않는다. 신규 `_review_11.py`도 #11을 코호트 전체에 대해
  하나의 상수로 다룬다.
- **M4**: 다만 `arm_schema_map`이 이미 arm별 분기를 수행하므로, arm 조건부
  자체는 이 파일이 낯설어하는 개념이 아니다.
- **CLAUDE.md**: "No abstraction unless explicitly requested" — (A)는 새
  추상화다. 명시적 요청(=이 판정)이 있으면 정당화된다.

#### 권고 (비구속 — 앵커링 주의)

> **D-H1a-4가 (C) 서술적 측정으로 판정되면 이 항목은 (C)로 자동 해소된다** —
> 채점하지 않는 arm에는 제약 집합이 필요 없다. D-H1a-4를 먼저 정하시라.
>
> D-H1a-6이 2-arm 축소로 판정되면 이 항목의 범위도 줄어든다.
>
> *비구속.*

#### 미판정 시 귀결
OPEN arm의 결과를 채점할 수 없다.

---

### D-H1a-5 SILENT/OPEN 최소편집 절차

#### 질문
두 arm의 차이를 "liveness 조항 유무" **하나로** 격리하는 절차와 그 기계적
검증을 어떻게 정의하는가?

#### 왜 결정 사항인가
서문을 통째로 들어내는지 해당 문장만 지우는지에 따라 프롬프트 길이, 주변
문맥, 다른 지시문과의 상대적 강조가 달라진다. 그러면 관측된 차이를 liveness
조항에 귀속시킬 수 없다(교란).

#### 선택지

| 안 | 내용 | 검증 방법 |
|---|---|---|
| **(A) 해당 문장 1줄만 삭제** | 나머지 서문 바이트 동일 | 두 프롬프트의 diff가 정확히 그 줄 하나인지 테스트로 고정 |
| **(B) 문장을 중립 문장으로 치환** | 길이 변화 최소화 | diff + 길이 차 상한 단언 |
| **(C) 두 프롬프트를 각각 독립 작성** | 자연스러움 우선 | 검증 불가 — 교란 통제 포기 |

#### 실측 제약
- 해당 문장은 `contract_prompt.md:24-25`의 2줄이다:
  ```
  이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
  통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.
  ```
  앞 문장("검증을 통과했다")과 뒤 문장("재판정하지 않는다")이 한 문단에
  붙어 있다. **앞 문장은 남기고 뒤 문장만 지울 것인지**가 실질적 선택이다 —
  앞 문장까지 지우면 "검증이 끝났다"는 사실 자체가 사라져 다른 변수가 바뀐다.
- E2.4는 `rendered_prompt_sha256`으로 프롬프트를 고정하는 관례가 있어,
  두 arm의 해시를 각각 기록하고 diff를 테스트로 고정하는 것이 기존 패턴과 맞다.

#### 권고 (비구속 — 앵커링 주의)

> **(A), 단 "재판정하지 않는다" 문장만 삭제하고 "검증을 통과했다"는 남긴다.**
> 그리고 두 프롬프트의 diff가 정확히 그 문장 하나임을 단언하는 테스트를
> 사전등록에 포함한다. *비구속.*

#### 미판정 시 귀결
SILENT/OPEN 차이를 liveness 조항에 귀속시킬 수 없어 실험의 핵심 대조가 무의미해진다.

---

### D-H1a-7 §2의 인과 귀속을 어떻게 다루는가

#### 질문
"독단 해결 = 모델의 사전 지식 의존"이라는 초안의 귀속을 유지하는가, 약화하는가,
검증 수단을 추가하는가?

#### 왜 결정 사항인가
적대 검증 지적: 이 귀속은 **검증 불가능한 단정**이다. 모델이 사전 지식이 아니라
**evidence 텍스트 내부의 신호**로 판단했을 가능성과 구분할 수단이 없다.
구체적으로 재료에 이미 신호가 섞여 있다:
- 문서 쪽: `주의: 재료-대상(4)만 ...` — 단정적 강조 어투
- 코드 쪽: 통과 중인 테스트가 인용됨 (`source_kind: "test"`)

#### 선택지

| 안 | 내용 | 비용 |
|---|---|---|
| **(A) 주장을 관측 수준으로 낮춤** | "독단 해결이 관측됐다"까지만 기록, 원인 귀속 안 함 | 결론이 약해짐. 대신 방어 가능 |
| **(B) 사후 프로빙 추가** | 모델에게 판단 근거를 되묻는 2단계 | trial 비용 증가. 자기보고 신뢰도 문제 |
| **(C) 신호 제거 fixture 변종** | 강조 어투·테스트 표시를 제거한 대조 fixture | fixture 제작 비용. 원문 훼손(C4 위반 소지) |

#### 실측 제약
- (C)는 evidence 원문을 변형하는 것이라 `qualify_fixture()`의 **바이트 단위
  원문 대조를 통과할 수 없다.** `_excerpt_matches()`가 발췌를 원본과 정확히
  비교하고, 불일치하면 payload 생성을 거부한다. 즉 **(C)는 현행 하네스에서
  실행 불가**다.
- (B)의 자기보고는 이 프로젝트가 이미 불신하는 근거 등급이다
  (`WORKSPACE_NAVIGATION.md` §5: "agent/LLM 자기보고 요약 — 신뢰도 하").

#### 권고 (비구속 — 앵커링 주의)

> **(A)를 권한다.** (C)는 하네스가 거부하고, (B)는 이 프로젝트가 신뢰하지 않는
> 근거 등급을 실험 결론의 축으로 삼는다. 관측 수준으로 낮추면 결론은 약해지지만
> 방어 가능하고, 후속 실험에서 원인을 분리하면 된다. *비구속.*

#### 미판정 시 귀결
실험은 돌아가지만 결론이 반증 가능한 형태로 서술되지 않는다.

---

## 4. 판정 간 의존 관계

```
D-H1a-4 (채점 극성) ──┬──> D-H1a-2 (verdict 어휘)
                      └──> D-H1a-3 (arm별 제약)

D-H1a-6 (arm 개수) ───┬──> D-H1a-3 (범위 축소 가능)
                      └──> D-H1a-5 (범위 축소 가능)

D-H1a-1 (profile 위치) ────> D-H1a-2 (같이 정하는 것을 권함)

D-H1a-7 (인과 귀속) : 독립
```

**4와 6을 먼저 판정하면 나머지 5건의 범위가 크게 줄어든다.** 특히:
- 4가 (C)면 → 3이 자동 해소
- 6이 (B)면 → 3·5의 범위 축소

## 5. 비협상 제약 — 판정이 넘을 수 없는 선

1. **2026-07-29 지시문 §2** — 모델-facing evidence item의 허용 필드는
   `evidence_id` / `source_kind` / `text` **3개뿐**이다. 금지 필드에
   **"liveness·authority·supersession 정보"가 명시**돼 있다.
   → **H1a의 목적과 정면으로 긴장한다.** 어떤 판정이든 이 금지를 우회해
   supersession을 모델에 직접 알려주는 형태가 되어서는 안 된다. (§2.1에서
   확인했듯 `source_kind`의 `doc`/`code` 구분은 **이미 허용된 필드**이므로
   그 범위 안에서 설계해야 한다.)
2. **방법론 규칙 1** — 동결 아티팩트(설계)와 운영 로그를 같은 커밋에 섞지 않는다.
3. **E2.4 cohort 보호** — 현재 D4(#11 리뷰) 절차가 진행 중이다. 그 표면
   (`cohort_prompts.json`의 해시들, `e2.4-contract-decider.md`)을 깨는 변경은
   E2.4 재동결을 강제한다.
4. **agent registry는 세션 시작 시점에 고정** (등록부 [DONE] #17) — 신규 trial
   subject가 필요하면 정의 설치와 실행 사이에 **최소 1회 세션 경계**가 강제된다.
5. **모듈 로딩** — 새 파일은 `spec_from_file_location` + 고유 `sys.modules` 키.
   평범한 `import _surface`는 [DONE] #6(남의 모듈로 조용히 실행)을 재발시킨다.
6. **fixture evidence는 원문과 바이트 일치해야 한다** — `qualify_fixture()`가
   강제하며, 불일치 시 payload 생성을 거부한다.

## 6. 재현 명령 (이 문서의 주장을 믿지 말고 확인하시라)

교차 확인 원칙(`WORKSPACE_NAVIGATION.md` §5): 어떤 주장이든 실제 관측 경계에서
재확인한다. 아래는 전부 읽기 전용이다.

```bash
cd /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-e2.2-wt/experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

# M1 · M2 — profile이 payload에 도달하는가 / source_kind가 노출되는가
python3 -c "
import importlib.util,sys,json
spec=importlib.util.spec_from_file_location('s','_surface.py'); s=importlib.util.module_from_spec(spec); sys.modules['s']=s; spec.loader.exec_module(s)
print('모델이 보는 evidence 필드:', s.MODEL_EVIDENCE_KEYS)
print('source_kind 가능 값:', sorted(s.SOURCE_KINDS))
f=json.load(open('fixture_sufficient_consistent.json'))
m=s.qualify_fixture(f,'../..',run_tests=False); p=s.build_model_payload(f,m)
print('manifest의 profile:', [c['eligibility_profile'] for c in m['evidence_checks']])
blob=json.dumps(p,ensure_ascii=False)
print('payload에 profile 문자열 존재:', {x: x in blob for x in sorted(s.ELIGIBILITY_PROFILES)})
"

# D-H1a-1 — docs/ 가 실제로 거부되는가
python3 -c "
import importlib.util,sys
spec=importlib.util.spec_from_file_location('s','_surface.py'); s=importlib.util.module_from_spec(spec); sys.modules['s']=s; spec.loader.exec_module(s)
try: s._eligibility_profile({'kind':'file_lines','path':'docs/phase_a_implementation_packet.md','start_line':102,'end_line':102},'doc')
except s.SurfaceError as e: print('REFUSED ->', e)
"

# M4 · M5 — arm_schema_map과 legacy enum
python3 -c "
import json; d=json.load(open('decision_schema.json'))
print('arm_schema_map:', d['arm_schema_map'])
print('legacy decision enum:', d['variants']['legacy_decision']['schema']['properties']['decision']['enum'])
print('v1 contract_verdict enum:', d['variants']['evidence_contract_v1']['schema']['properties']['contract_verdict']['enum'])
"

# M8 — decision_schema_sha256을 재검증하는 코드가 있는가
grep -rn "decision_schema_sha256" --include="*.py" . | grep -v __pycache__

# M9 — semantic_constraints는 arm 조건이 있는가 / conformance는 arm을 받는가
python3 -c "import json; print(len(json.load(open('decision_schema.json'))['semantic_constraints']), '개, 최상위 평평한 배열')"
grep -n "def conformance" _score.py

# 재료 (§1.4)
sed -n '102p;106p' ../../docs/phase_a_implementation_packet.md
sed -n '36p' ../../conceptgate/cg_partwhole.py
cd ../.. && python3 -m pytest -q "test_semantic_regressions.py::test_r6b_material_feature_not_in_isa_dag"
```

## 7. 회신 형식

아래 블록을 채워 회신해 주십시오. 판정하지 않는 항목은 `deferred`에
사유와 함께 적어 주시면 그 항목은 진행하지 않습니다.

```text
DESIGN DECISION — H1a source_authority_unresolved
decided_by:
date:

D-H1a-4 (채점 극성):        <A|B|C|D|other>
  근거:
D-H1a-6 (arm 개수):          <A|B|C|other>
  근거:
D-H1a-1 (profile 위치):      <A|B|C|other>
  근거:
D-H1a-2 (verdict 어휘):      <A|B|C|other>
  근거:
D-H1a-3 (arm별 제약):        <A|B|C|other>
  근거:
D-H1a-5 (최소편집 절차):     <A|B|C|other>
  근거:
D-H1a-7 (인과 귀속):         <A|B|C|other>
  근거:

deferred:
  <항목 ID>: <사유>

new_constraints:
  <이 판정이 새로 부과하는 제약 — 후속 세션이 지켜야 할 것>

실험 중단 여부:
  <계속 | 재정의 필요 | 중단>  / 사유:
```

## 8. 부록

### 8.1 참조 파일 (전부 읽기 전용)

| 파일 | 무엇 |
|---|---|
| `experiments/2026-07-29_h1a_source_authority_unresolved/README.md` | H1a 설계 초안(이 요청서의 대상) |
| `docs/feedback/h1a_source_authority_unresolved_review_20260729.md` | 4축 적대 검증 합성 보고 |
| `docs/DIRECTIVE_2026-07-29_operations_change.md` | 운영 지시 원문 |
| `docs/E2.4_ISSUE_REGISTER.md` | E2.4 미결 전체 목록 + [DONE] 24건 |
| `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/_surface.py` | 표면 파이프라인(빌더·qualification) |
| 〃 `decision_schema.json` | arm_schema_map, variants, semantic_constraints |
| 〃 `contract_prompt.md` | 계약 문구(서문 24-25행이 쟁점) |
| 〃 `_score.py` | 채점기(`conformance`, 밴드) |
| 〃 `DESIGN_D4_constraint_11_review.md` | #11 리뷰 사전등록(진행 중인 D4) |
| `../concept-gate-taxonomy/docs/EXPERIMENT_METHODOLOGY.md` | 방법론 7규칙 |

### 8.2 용어

| 용어 | 뜻 |
|---|---|
| **clean rerun cohort** | 유출 제거 후 화이트리스트 빌더를 거쳐 새로 실행한 코호트. "재채점"도 "재현"도 아니다 |
| **screened_PASS / ambiguous / screened_FAIL** | 사전등록 3구간 밴드(≥0.90 / ≥0.70 / 그 미만). 중간 구간은 실패가 아니라 Stage 2 증분 지시 |
| **qualification** | 실행 전 단계. 모든 evidence의 locator를 해소해 원문과 바이트 대조하고, 실패 시 payload 생성을 거부 |
| **hidden oracle** | 기대 판정. `oracle_manifest.json`에 있고 빌더는 이 파일에 접근하지 않는다 |
| **clean** | 기대 verdict에 **스키마를 지키고 계약을 어기지 않고** 도달한 것. D4로 **#11 리뷰**가 네 번째 항으로 추가되는 중 |
| **legacy_leaky** | 오라클 유출 상태에서 얻은 구 결과. 삭제하지 않되 인증·통계에서 제외 |
