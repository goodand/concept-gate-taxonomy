# Kernel 통합 실측 조사 — 설계 변경안 수령 전 기준선

- 작성: 2026-08-22, D-H1a-18(H1a 종결, `next_program`: kernel 추출 → 인과 추론)
  직후, **설계 변경안 수령 직전**
- 목적: 곧 도착할 설계 변경안을 **기억이 아니라 커밋된 실측**과 대조하기 위한
  기준선. D-H1a-16 판정문이 저장소에 커밋되지 않아 인용 검증이 불가했던 사고의
  재발 방지 — 이번엔 판정문이 아니라 **변경안이 딛고 설 현재 상태**를 먼저 고정한다
- 방법: 전부 실측(파일 판독·sha256·AST 언급은 해당 문서 인용). 추정값 없음
- 문서 종류: 운영 로그. 동결 아티팩트 아님

---

## 1. 활성 worktree 지도 (2026-08-22 실측)

| worktree | 브랜치 | 최신 커밋 | 상태 |
|---|---|---|---|
| `concept-gate-taxonomy` | `claude/ontoclean-gufo-handoff-7cmq0v` | 08-08 `eef4821` | 정본 checkout |
| `concept-gate-h1-wt` | `codex/h1-source-authority` | 08-22 `e9b224e` | **H 계열 정본.** H1a 종결(D-H1a-18) |
| `concept-gate-codex-mcp-wt` | `codex/mcp-provider-isolation` | 08-11 `2cc7b1b` | retrieval controller 실험 + 검증 계층 round14~22c |
| 나머지 8개 | — | 08-08 일괄 문서 커밋 이후 휴면 | e2.2-wt의 H1a 파일은 **사본**(codex HANDOFF 명시: "저쪽은 사본이고 여기가 정본이다") |

h1-wt ↔ codex-mcp-wt 분기: **87 대 100 커밋** (`git rev-list --left-right --count`).

## 2. 핵심 발견 — kernel은 추출 대상이 아니라 **이미 존재**한다

`conceptgate/cg_obligations.py`(345행, stdlib-only)가 D-H1a-17 Q17.1이 규정한
kernel 표의 절반 이상을 구현하고 있고, **소비처도 이미 있다**:
`concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_pipeline.py:57`이
`from conceptgate.cg_obligations import …`로 `certify()`에 위임한다.

| D-H1a-17 kernel 항목 | 제품 구현 | 근거 |
|---|---|---|
| typed obligation graph | 부분 ✅ | `ObligationSpec`/`ObligationResult`/`OBLIGATION_REGISTRY` — 단 **의무 수준**이지 정책 텍스트의 의미 그래프가 아님 |
| fail-closed `unknown` | ✅ | `aggregate()` UNKNOWN이 PASS 차단; adapter가 "필드 부재 ≠ 위반 0건" 구별; `on_unavailable` |
| assurance ceiling | ✅ | `MAX_ASSURANCE` — LLM ≤ `SOURCE_ANCHORED`, 초과 시 `ASSURANCE_EXCEEDS_DECIDER_CAP` |
| structured feedback | ✅ | `certify()` 단일 진입점, PASS는 evidence 필수(`MISSING_EVIDENCE`) |
| semantic graph diff | ❌ | **H1a에만 존재** (`_h1a_policy_audit.py`) |
| mutation framework | 부분 | 양쪽에 서로 다른 형태로(§4) |

Codex round20 §1.1의 규범: "**판정 어휘를 새로 만들지 않는다** —
`cg_obligations.py`의 것을 그대로 쓴다", §3.2: "import 실패 시 로컬 enum으로
폴백하지 **않는다** — 못 쓰면 그 사실이 BLOCKED다".

`validate_result`/`certify`의 **`registry` seam**(codex-mcp 판에만 존재)은
정확히 외부 의무 집합을 위한 것이다 — docstring: "실험용 의무 10개를 이 도메인
레지스트리에 등록하면 개념 게이트 레지스트리가 오염되고, 규칙을 실험 쪽에 다시
구현하면 검증된 기제가 두 벌이 된다. 인자 하나가 둘 다 피한다."

## 3. 두 라인의 명제 단위 대조

### Codex 라인이 앞선 것 (h1-wt에 대응물 없음)

| # | 자산 | 내용 | 왜 중요한가 |
|---|---|---|---|
| C1 | `_receipt.py` (126행, 의존 0) | canonical bytes + **HMAC 서명**(도메인 분리, O_EXCL 키, 0600) | round21 실측 결함의 해법: "자기 공개 내용의 공개 해시는 아무것도 인증하지 않는다 — launcher가 돈 적 없는데 손으로 쓴 receipt가 수락됐다". **H1a의 provenance가 정확히 이 약점을 가진다**(우리는 "자기신고"라고 문서화하는 데서 멈췄고, 이쪽은 일부를 닫는 기제가 있다) |
| C2 | 관측 기반 격리 receipt | reviewer의 boolean을 읽지 않고 **launcher가 probe를 실행**해 receipt 생성, 결속 해시(`packet/assignment/sandbox_profile_sha256`) 검사 | 자기신고 배제의 실행형 |
| C3 | `pending_guard_negative_tests.py` | 착륙 불가한 음성 테스트(착륙이 재검정을 강제)를 **대장에 등재** | 조용한 생략의 대안 |
| C4 | 잎 모듈 원칙 + import 비용 실측 | `_provenance` 19,292us vs `apply_safety_audit` 5,051us → 계층 역전 회피 배치 결정 | 통합 시 모듈 배치의 선례 |

### H1a 라인이 앞선 것 (어디에도 대응물 없음)

| # | 자산 | 내용 | 로드맵 접점 |
|---|---|---|---|
| H1 | `_h1a_semantic_compiler.py` | 프롬프트 **바이트 → 관측 정책 그래프** 독립 재유도(§9.6 능력 게이트, `proven_families`는 픽스처에서 **계산**) | M1 재설계("certificate = 불변조건을 운반하는 reasoning contract")의 검사기 후보 |
| H2 | `_h1a_policy_audit.py` | **expected vs observed 의미 그래프 diff.** round20의 obligation 10종은 전부 배선·provenance 명제 — 의미론 명제는 0 | 동일 |
| H3 | `_h1a_mutation_pack.py` + 조건 11/12 | **blinded mutation pack으로 리뷰어 자격을 측정**(심어진 결함을 찾는가) — codex의 `reviewer.qualification.required`(정답 대조)보다 강한 명제 | round20 §1.4 mutation 규칙과 상보 |
| H4 | `SHARED_PROVENANCE_KEYS` + arm별 프롬프트 해시 계약 | raw가 자기 provenance 선언 + manifest 바이트 결박 | C1과 결합 대상 |

## 4. 측정된 분기 (통합 전 반드시 합류해야 하는 것)

| 파일 | taxonomy | h1-wt | codex-mcp | 판정 |
|---|---|---|---|---|
| `conceptgate/cg_obligations.py` | `8723f4c827c7` | `8723f4c827c7` (동일) | `9ca99cf04298` | codex-mcp만 registry seam 앞섬. **가산적·하위호환** — diff 실측: `validate_result`/`certify` 시그니처 확장뿐 |
| `test_guard_negative_coverage.py` | `169da3c69bdc` | `35fa647d7aea` | `bbd9fd9a5010` | **세 worktree 세 버전.** h1-wt는 `_assert_` prefix 지원, codex-mcp는 frozen-surface 면제 사유(08-08) 각자 추가. **뮤테이션을 강제하는 게이트 자체가 갈라짐** |
| `docs/obligation_layer_roadmap.md` | `78731601dbfe` | 동일 | 동일 | 분기 없음. 단 E2.2.3(07-25)에서 멈춰 있어 E2.4·H1a 미반영 |

**어휘 fork**: H1a가 로컬 상태 어휘(`DIAGNOSTIC_PASSED`/`FAILED`/
`MATERIAL_UNAVAILABLE`, assurance 문자열)를 새로 만들었다 — registry seam이
막으려던 바로 그 형태. 실험 격리 규율(AST가 `_h1a_semantic_compiler`의 import를
`re`로 제한) 때문에 컴파일러 안에서는 정당했으나, **감사·채점 계층은 제품
어휘를 쓸 수 있었다.**

## 5. 로드맵 접점

kernel 통합은 새 마일스톤이 아니라 **M1의 "핵심 실증 완료 + 재설계 대기" 칸**이다.
M1 재해석(E2.2.1~E2.2.3): certificate는 경고 신호가 아니라 **불변조건을 운반하는
reasoning contract**이고, 실증된 레버는 자연어 불변조건(A_ONLY 20/20)이지 스키마
강제(C_ONLY 0/20)가 아니다. H1a의 typed expected-state가 "불변조건을 contract
필드로 표현"하는 방법이고, H2가 그 준수를 바이트에서 재유도해 검사하는 방법이다.

D-H1a-18 `next_program.priority` = ① reusable_feedback_kernel
② LLM_output_based_causal_inference — 이 조사와 정렬.

## 6. 침범 금지 경계

Codex 라인의 미결 큐(round22c §"지금"·"closure 1회"·"위임": 0~11번 + 4-arm
pilot)는 **그 라인의 것**이다. 통합 작업이 `experiments/2026-08-07_*`의
frozen surface를 건드리면 그쪽 provider qualification(살아있는 모델 실행 8회)이
무효화된다 — codex guard 게이트의 08-08 면제 사유가 그 비용을 실측으로 기록해
뒀다("재실행은 재현 불가능한 fresh experiment").

## 7. 설계 변경안 평가 시 이 문서의 사용법

1. 변경안이 **§2~§4의 실측과 모순되는 전제**를 딛고 있으면 그 지점을 인용해
   되물을 것 (예: "kernel을 새로 만든다" — §2가 반증)
2. 변경안이 §4의 분기를 다루지 않으면 **통합 순서 결정이 빠진 것** — guard
   게이트 3버전 합류 없이 그 위에 쌓는 설계는 갈라진 토대 위에 짓는 것
3. 변경안이 §6 경계를 넘으면 codex 라인 재검정 비용을 명시해야 한다
4. 손 복사 금지 — worktree 간 전파는 commit/merge/rebase로만
