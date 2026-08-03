# H1a 운영 로그

`EXPERIMENT_METHODOLOGY.md` §1·§2가 요구하는 운영 기록. **설계(동결)와 같은
커밋에 섞지 않는다** — 결과가 설계를 소급 수정하지 못하게 하는 것이 목적이고,
이 파일에는 결과 해석과 다음 단계 판단이 들어간다.

사전등록·판정문은 이 파일이 아니라 `PREREGISTRATION.md`,
`DESIGN_DECISION*.md`에 있다. 이 파일은 **그것을 실행하며 생긴 기록**이다.

섹션은 **최신순**이다.

---

## 2026-08-03(2) — Q10 판정 도착·반입 (D-H1a-10)

판정문: `DESIGN_DECISION_H1a_residual_prohibition.md`.
**Q10=E / Q10.1=보존(비병합) / Q10.2=가드 상향 / Q10.3=L4 등록.**

### 1. 판정 요지

| 항목 | 판정 |
|---|---|
| 이번 40 trial | **무효화 아님.** 실행된 프롬프트 아래의 관측은 유효 |
| 그러나 | 의도한 H1a estimand를 **식별하지 않음**(`TargetMechanismContrast: False`) |
| 결론 표기 | `target_effect: insufficient_evidence` + `current_bundle_contrast: observed_zero`. **`null_effect` 아님** |
| 수선 | **B 방식** — 공통 Q7 목록에서 표적 축 4개만 제거(R1), **양 arm 재실행**(R2) |

판정문 §3이 형식 검사로 뒷받침한다 — `M_allowed = ¬Q1 ∧ ¬Q7`이므로 현재
설계는 KEPT·REMOVED 둘 다 `M_allowed=0`, 수선 후에는 REMOVED만 `1`이 된다.
A(그대로 종료)는 "표적을 허용했는데 변화 없음"과 "양 arm에서 금지돼 있었음"을
혼동시키므로 기각, C(Q7 전체 이동)는 비표적 축까지 함께 바꿔 복합 조작이
되므로 기각, D(2×2)는 정당하지만 최소 복구에 불필요해 후속으로 유보됐다.

### 2. 이번 세션이 반입·등록한 것 (문서·메타데이터만, 표면 무변경)

| # | 작업 | 파일 |
|---|---|---|
| 1 | 판정문 저장(평면, 기존 4건과 같은 자리) | `DESIGN_DECISION_H1a_residual_prohibition.md` |
| 2 | **L4 등재** — 영문 원문 + 한국어 기록문, 의역 없음. L1~L3와 성격이 다름을 표로 명시(외적 일반화 한계 vs 내적 식별 한계, `L3_subsumes_L4: false`) | `PREREGISTRATION.md` §0.1 |
| 3 | 헤더의 **"전부 trial 0건 시점이라 재동결 비용 없음" 정정** — 이제 거짓이다. 갱신 4·5 이력 추가 | `PREREGISTRATION.md` 헤더 |
| 4 | **코호트 상태 동결** — Q10.1의 YAML 상태값 + 산출물 11종 sha256 + 보고 규약(허용/금지 문구) | `COHORT_STATUS_20260803_nonidentifying.md`(신규) |

**상태값을 `h1a_cohort_score.json`에 넣지 않았다** — `_h1a_score.py::main()`이
`SCORE_PATH.write_text(...)`로 매 실행 덮어쓰므로(`_h1a_score.py:168-170`
실측) 손으로 넣으면 채점기 재실행 시 조용히 사라진다. 같은 이유로
`trials.json`도 재생성 대상이라, 상태 파일의 해시 표에 그 사실을 명시했다.

### 3. 실측으로 재검증한 것 (요청서 인용을 그대로 받지 않음)

판정문·요청서가 인용한 사실 3건을 **원본 파일에서** 직접 확인했다:

| 주장 | 검증 |
|---|---|
| 가드가 bare `liveness`를 의도적으로 제외했다 | `_h1a_contract.py:99-103`·`:126-130` 주석 실측 — 요청서 인용과 일치 |
| `test_guard_precision_the_clean_template_passes`가 clean 인증 | `test_h1a_contract.py:218` 존재 확인 |
| 채점기가 score json을 덮어쓴다 | `_h1a_score.py:161-171` 실측 |

### 4. 다음 단계 — Phase 3 이후는 승인 대상

문서 등록(Phase 1~2)은 끝났다. 남은 것은 **동결 아티팩트를 실제로 바꾸는**
작업이라 별도 승인이 필요하다:

1. **R1 — Q7 부분 개정**: `h1a_prompt_template.md:50-52`에서 표적 축 4개
   (`source_kind priority`, `recency`, `authority`, `liveness`) 제거, 비표적
   3개(`evidence item count`, `source order`, `outside knowledge`) 유지.
   **동결 프롬프트 변경이다.**
2. **Q10.2 — 가드 상향**: `LIVENESS_PRIORITY_CLAUSES` + `RESIDUAL_TRIPWIRES_KO/EN`
   어휘 방식 → `decision_basis_policy` 타입 스키마 + 결정론적 렌더러 +
   구조 단언 6항 + 연역 검사. LLM 검사기는 **보조만**(단독 인증 게이트 금지).
3. **새 사전등록** — 판정문 §11의 post-result 공개 7항. 이 파일이 아니라
   **새 사전등록 문서**에 들어간다(기존 `PREREGISTRATION.md`는 최초 코호트의
   동결 기록으로 보존).
4. **독립 리뷰** — 표면이 바뀌므로 3차 리뷰(2026-08-02)는 **무효가 된다.**
   Q9 때 생략이 정당했던 근거("표면 불변")가 이제 성립하지 않는다.
5. **양 arm 40 trial 재실행** — 별도 승인.

### 5. Phase 3에서 확정해야 할 미결 설계 질문 (운영 세션이 임의로 정하지 않음)

**`removed: allowed`를 프롬프트에 어떻게 렌더링하는가?** 판정문의 정책
스키마는 표적 축을 REMOVED에서 `allowed`로 표기하지만, 그것이 프롬프트에
**명시적 허용 문장으로 렌더링되는지**, 아니면 **침묵(문장 없음)인지**를
판정하지 않았다.

- 침묵이면: REMOVED는 금지도 허용도 없는 상태. 모델이 관행적으로 출처
  속성을 안 쓸 가능성이 남는다.
- 명시적 허용이면: 이전에 없던 **새 문장**이 생기고, KEPT(금지 산문) 대
  REMOVED(허용 산문)의 비대칭이 새로 도입된다 — 조작 표면이 커진다.

Q10.2의 렌더러 요구사항 5("렌더된 모든 정책 문장이 원래 policy ID로 추적
가능한가")는 `allowed` 상태도 문장을 낼 수 있음을 함의하는 것으로 읽히나,
단정할 수 없다. **P7의 "고칠 대상을 임의로 정하지 않는다"에 해당하므로
Q11로 상신하거나 사용자 판단을 받는다.**

---

## 2026-08-03 — Q9 반입, 동결, 본 코호트 40 trial 실행, Q10 상신

### 1. Q9=A 반입·적용 (trial 0건 시점)

- `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`를 저장소로 반입 →
  `DESIGN_DECISION_H1a_evidence_symmetry.md`(기존 명명 규칙, H1a 소문자 a).
  `diff` 무출력으로 byte-identical 확인. notes 원본은 원문 보존을 위해 그대로.
- `PREREGISTRATION.md` §0.1 신설 — L1·L2(등록부 [DECLARE] 표에서 인용)와
  **L3(판정문 Q9.1 원문 그대로, 의역 없음)** 를 같은 보고 층위에 등록.
- fixture·코드 무변경(Q9=A가 명시적으로 요구).
- 4차 독립 리뷰: **사용자 승인으로 생략.** 표면(prompt/payload/fixture)이
  바뀌지 않았다는 근거.

### 2. 신규 harness 2개

| 파일 | 역할 | 규율 |
|---|---|---|
| `_h1a_cohort.py` | 동결 — qualify → payload+가드 → 양 arm 렌더 → 40 trial manifest → bundle 순서 고정 → `cohort_prompts.json` | 기존 모듈을 재구현하지 않고 호출만 한다. bundle 순서는 E2.3 `sha256_blocked_sort` 패턴, seed `H1A-fixed-order-v1`(P2에 사전등록된 값) |
| `_h1a_score.py` | 채점 — P4 제외/P5 코딩/P7 Stage A 게이트 | **trial 출력을 읽기 전에 작성했다.** 결과를 본 뒤 만든 채점 규칙은 규칙이 아니라 사후 합리화(P7 §7.2). 코딩 로직은 한 줄도 새로 쓰지 않고 전부 `_coder.code()`에 위임 |

`_h1a_surface.py`는 E2.4 동결 사본이라 **손대지 않았다**(문서화된 3개 일탈을
테스트가 고정하고 있다).

### 3. 실행 전에 닫은 구멍 — trial subject 표면 미해싱

`trial_manifest()`는 fixture/payload/prompt/schema를 해싱하지만 **trial
subject의 system prompt는 해싱하지 않는다.** E2.4가 §11.1에서 정확히 이
구멍을 찾아 `system_prompt_sha256`을 추가했던 사안이 H1a에는 반영돼 있지
않았다.

`_h1a_surface.py`를 고치지 않고(동결 사본) `_h1a_cohort.py`에서 닫았다:

- `definition_sha256` + `system_prompt_sha256` 기록
- `tools: []`를 **정의 파일에서 직접 확인** — 하네스의 agent 목록은 이
  에이전트를 "All tools"로 표시하므로, P3의 `no_tools` 주장을 검증할 수 있는
  곳은 정의 파일뿐이다
- 음성 대조: `tools: [Read, Bash]`를 주입하니 **CAUGHT** — 잡지 못하는
  가드는 장식(skills-catalog 패턴 8)

### 4. 동결 검증

| 검사 | 결과 |
|---|---|
| 재실행 결정론 | 2회 실행 byte-identical |
| fixture qualification | `passed` |
| `assert_no_model_facing_type_anchor` (§11.0) | 통과 |
| `assert_no_residual_prohibition` | 통과 — **그러나 §6 참조. 이 통과가 무엇을 뜻하는지가 이번 발견의 핵심이다** |
| `diff_is_restricted_to_the_liveness_clause` | 통과(재구성 방식) |
| 렌더 직접 확인 | KEPT에 Q1 2문장 있음 / REMOVED에 없음. 길이 2680 vs 2597 |
| 워크플로 스크립트 임베딩 | `cohort_prompts.json`의 `rendered_prompts`와 round-trip byte-identical 확인 후에만 dispatch |
| 테스트 | H1a 106 passed/1 skipped, E2.4 118 불변 |

### 5. 실행

| 항목 | 값 |
|---|---|
| transport | Workflow tool, `parallel()` × 40, `agentType: h1a-decider`, forced schema |
| run id / task id | `wf_055b8173-3b1` / `wqfunuszs` |
| 결과 | 40 dispatched / **40 done** / 0 error / 0 empty |
| 토큰·시간 | 114,330 subagent tokens / 49.7s |
| 전송 실패(P4) | **0건** — 재실행 없음, 완주 bundle 20/20 |
| 코더 교정 | 실행 직전 재측정 **18/18 passed** |

`args`를 쓰지 않고 프롬프트·trial 목록·schema를 스크립트 리터럴로 임베드했다
(skills-catalog 2026-07-30: `args`는 문자열로 도착한다). trial 신원은
`.then()` 매핑으로 workflow 반환값에 실었다 — `journal.jsonl`은 content
hash로 키를 잡아 신원 복구에 못 쓴다.

**전송 실패 함정 확인**: `agents_done: 0` / 수십 ms는 아무것도 모델에
도달하지 않았다는 뜻이다. 이번 실행은 40/40·49.7s·114k 토큰이므로 실제 실행.

행동 분포(P5.2 기계 코딩, `rationale` 미열람):

| arm | selection | deferral | invalid |
|---|---|---|---|
| PROHIBITION_KEPT | 0 | **20** | 0 |
| PROHIBITION_REMOVED | 0 | **20** | 0 |

### 6. 발견 — Q10 상신 (이번 세션의 실질 산출물)

**0/40이라는 바닥값을 "조작이 효과 없었다"로 읽지 않고 검증한 결과**, Q7=E가
도입한 warrant rule의 tie-breaker 금지가 **양 arm에 남아 있다**는 것을
찾았다. 이 fixture가 정확히 그 tie이므로(1-vs-1, 양쪽 직접 type 진술, 어느
텍스트에도 우선순위 진술 없음 → `unless` 예외 안 열림) `PROHIBITION_REMOVED`
arm도 조작 대상 행동을 여전히 금지한다.

**blocker #16의 재발**이되, 구현 오류가 아니라 판정문 자신이 그 목록을 양 arm
구속으로 명시한 것이다. 그래서 운영 세션이 고치지 않고 상신했다 — "고칠
대상을 임의로 정하지 않는다"(P7).

잔여-금지 가드가 왜 못 잡았는지가 중요하다: **잡지 않도록 의도적으로
조정돼 있었다.** bare `liveness`를 tripwire에서 뺀 이유가 "Q7's warrant rule
legitimately uses [it] ... in BOTH arms"라고 코드 주석에 적혀 있고,
`test_guard_precision_the_clean_template_passes`가 현재 template을 clean으로
적극 인증한다.

| | 명제 |
|---|---|
| 가드가 검사한 것 | "Q1 절 바이트가 REMOVED에 없는가" |
| 필요했던 것 | "REMOVED에 **동등한 금지가 남아 있지 않은가**" |

**공정하게 기록**: select_type이 논리적으로 불가능하진 않았다. Q7이 막은 것은
동점을 *출처 속성*으로 깨는 것이고, `ev3`의 반박절(= L3 비대칭)을 merit로
읽어 고르는 것은 허용된다. 40/40이 그 경로를 택하지 않았을 뿐이다.

상신: `correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md`
(Q10, 선택지 A~E + Q10.1~10.3). 인용 전수 실측 대조 완료.

### 7. 결과 데이터의 독립 교차검증

두 방향으로 확인했다(패턴 9 — 위임된 경로의 all-clean 보고를 그대로 받지
않는다):

1. **코딩**: `_coder.code()`를 거치지 않는 독립 재집계 → 동일한 20/20·20/20
2. **원시 데이터**: `journal.jsonl`(하네스가 씀, `trials_raw.json`을 뽑아낸
   task-output 파일과 **다른 경로**)의 40개 result를 정규화해 집합 비교 →
   sha256 일치(`98f409c531c03a21…`). 상세는 `h1a_attempt_log.json`

40개 rationale이 전부 상이하므로 캐시·재생이 아닌 실제 독립 표본이다.

### 8. 산출물

| 파일 | 계층 |
|---|---|
| `cohort_prompts.json` | manifest freeze (동결 후 불변) |
| `trials_raw.json` | results — 원시 출력 `{trial_id: output}` |
| `trials.json` | results — manifest + 출력 + 코딩 |
| `h1a_cohort_score.json` | 채점 요약 |
| `h1a_attempt_log.json` | **P4 요구** 시도 이력 + 독립 교차검증 |
| `h1a_cohort_workflow.js.txt` | 실행 스크립트(운영 기록) |
| 이 파일 / `docs/HANDOFF.md` / `docs/H1A_ISSUE_REGISTER.md` §H | ops-docs |

### 9. 미결 — 다음 세션

> ⚠️ **아래 1번은 2026-08-03(2)에 해소됐다** — Q10 판정이 도착했다(D-H1a-10).
> 최신 상태는 이 파일 상단 섹션. 2·3번은 여전히 유효하다.

1. ~~**Q10 판정 대기.**~~ → **도착.** Q10=E. 이번 코호트는
   `completed_nonidentifying`으로 동결 보존되고 새 코호트와 병합하지 않는다.
   **"금지를 제거해도 행동은 변하지 않았다"로 인용하는 것은 여전히 금지**이며,
   허용 문구는 `COHORT_STATUS_20260803_nonidentifying.md` §4에 있다.
2. **커밋 안 함.** 전부 미커밋. 커밋할 때는 방법론 §1의 순서를 지킨다 —
   manifest freeze / results / ops-docs를 **각각 독립 커밋**으로.
3. `_h1a_cohort.py`·`_h1a_score.py`에 대한 `test_protocol.py`급 자기검증이
   없다. 다른 실험 폴더의 표준 파일 세트에는 있다. Q10 판정에 따라 이 harness가
   재사용될지가 갈리므로 그때 판단한다.

### 10. 환경 공백 (회귀 아님)

- `owlready2` 미설치 → `test_cg_obligations.py::test_registered_handlers_resolve`
  FAIL. `HANDOFF.md` §9·§10.1이 기록한 **기존 결함**이며 이번 변경분은
  `conceptgate/`를 건드리지 않았다(`git status`로 확인).
- `fastmcp` 미설치 → `test_server.py` BLOCKED(러너가 분리 보고).
