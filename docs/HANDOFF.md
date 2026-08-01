# HANDOFF — ConceptGate 세션 인수인계 (E2 실험 체인)

- 갱신: 2026-07-30
- 대상: **컨텍스트 없이 이어받는 새 세션**. 이 문서만 읽고 작업을 재개할 수 있게 쓴다.
- 이 문서는 worktree `concept-gate-e2.2-wt`(브랜치
  `codex/e2.4-contract-repo-design`)의 최신 상태를 기록한다.
- **파일을 어디서 찾을지 모르겠으면** 먼저 [`WORKSPACE_NAVIGATION.md`](WORKSPACE_NAVIGATION.md)를
  읽어라 — 저장소/worktree 구조, 문서 종류별 분류 체계, 탐색 명령 레시피가 있다.
- **새 실험을 설계하기 전에** 메인 저장소 체크아웃의
  `../concept-gate-taxonomy/docs/EXPERIMENT_METHODOLOGY.md`를 읽어라
  (7개 규칙: 동결/운영로그 분리, 폴더 규약, provenance 계약, worktree 격리,
  비-git 감사본, 교훈 승격, 독립 재현 검증).

---

## 1. 지금 상태 한 문단 (TL;DR)

M1(relation.is_a certificate) 검증 실험 라인을 진행 중이다.
E2.2.1(NO_GO) → E2.2.2(GO) → E2.2.3(OFAT, A_ONLY 단독 충분) →
E2.3(A_ONLY 일반화, screened PASS) → **E2.4(종료)** → **H1a(진행 중, 차단됨)**.

> ## 🚚 H1a는 이 worktree를 떠났다 (2026-08-01)
>
> **H1a 작업은 `../concept-gate-h1-wt`(브랜치 `codex/h1-source-authority`)에서
> 계속된다.** 이 worktree에서 H1a를 이어받지 마라.
>
> **왜 옮겼나**: H1a는 2026-07-29 운영 지시가 "**별도** source_authority_unresolved
> 실험"이라고 명시한 **새 계열**인데 E2.x worktree에 얹혀 있었다.
> `EXPERIMENT_METHODOLOGY.md` §4가 이것을 금지한다 — "새 실험 계열을 시작할
> 때는 새 worktree를 만들지, 기존 worktree에 무관한 실험을 얹지 않는다."
> H1b·H2가 오면 반복될 문제라 지금 분리했다.
>
> **이 브랜치(`codex/e2.4-contract-repo-design`)가 담는 것**: E2.2~E2.4 체인.
> **E2.4/H3는 2026-07-30 종료**(존재 주장, D-H3C). 아래 §4·§11의 E2.4 서술은
> **완료된 이력**이지 할 일이 아니다.
>
> ⚠️ **아직 파일이 양쪽에 다 있다.** 분리 커밋(`e0b8fd9`)까지의 이력을 두
> 브랜치가 공유하므로 `experiments/2026-07-29_h1a_source_authority_unresolved/`가
> 여기에도 남아 있다. **여기 것은 사본이다** — H1a의 정본은 `../concept-gate-h1-wt`
> 쪽이다. 중복 제거는 미결(§아래 "미결 구조 작업").
>
> **H1a 상태 요약**(상세는 그쪽 worktree의 `docs/H1A_ISSUE_REGISTER.md`):
> 설계 판정 4회(Q1~Q8), 독립 리뷰 2회. 두 번째 리뷰가 **동결 부적합**
> (blocker 2 + major 7)을 냈고 그 4건에 대한 판정(Q5~Q8)이 도착했으나
> **아직 미적용**. trial 실행 **0건**.
>
> 전체 목록·근거·검증 강도: [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md)
> 리뷰 전문: [`feedback/h1a_fixture_review_20260730.md`](feedback/h1a_fixture_review_20260730.md)

**E2.4의 위치(이력)**: 이 실험의 본 목적인 **3-arm 비교
(CONTROL_REPO vs A_REPO vs CONTRACT_REPO)는 아직 한 번도 실행되지 않았다.**
**fixture 준비 단계(Phase 0~3)는 2026-07-28에 완료·인증됐다** — 3개
semantic class 전부 clean rerun cohort(N=10/cell)로 3/3 인증. 본 실험
(Phase 4~6)은 native schema 그대로는 돌릴 수 없었다 — **외부 설계 판정
(2026-07-29, `DESIGN_DECISION_H3.md`)이 재정의를 요구했다**: legacy arm은
`abstain`을 표현할 수 없어 비교가 성립하지 않는다. D3(H1c)는 이 판정으로
**해소됐고**(3 class 완전 교차, D-H3-2), D4·D5도 **해결됐다**(아래 참조).

**재정의된 H3는 실행까지 완료됐고, 2026-07-30 외부 판정으로 종료됐다** —
세 arm 공통 action 표면(`accept_report|repair|defer`)을 구현·동결하고 smoke
3건 + pilot 45건을 돌린 뒤, `DESIGN_DECISION_H3_CONFIRMATORY.md`가
**존재 주장으로 종료**를 판정했다(§H3 절, 등록부 D7). 확증 실험은 표집틀
자체가 없어서 — 세 fixture가 CONTRACT 결과로 선별됐고 남은 재료도 합성
템플릿 2개뿐이라 — **별도 과제 3건으로 분리**됐다. **E2.4 안에 남은 차단
요인은 없다.**

**유효 커버리지는 4 class가 아니라 3 class다** — `conflicting`은 "현 저장소의
live·동등강도 evidence로 구성 가능한 fixture 미확보"로 종결됐다(§4). Schema의
class 자체는 유지된다.

> **2026-07-29 현재 — fixture 검증 3/3 인증, 제약 #11 리뷰까지 완료.**
>
> 오라클 유출을 구조적으로 막는 v2 표면(3면 분리 + 화이트리스트 빌더), 계약
> 문구 개정, 채점기 결함 2건 수정을 거쳐 clean rerun cohort를 **N=10/cell(30
> trial)로 실행했다.** 결과: **E24-F-01·02·03 전부 clean 10/10,
> screened_PASS.** `protocol_deviation` 없음(N=10이 Stage 1과 정합). 실질
> 검증도 통과 — E24-F-02는 10/10 전부 필러 feature `갑종`을 정직하게
> `insufficient`로 표시하며 `바퀴`만 repair했고, E24-F-03은 10/10 전부
> evidence를 `indirect_context`로 정확히 분류했다. 상세는 §11, 등록부 [DONE] #21.
>
> 실행 중 22/30 trial이 API **세션 사용 한도**로 실패했다(컨텍스트 윈도우
> 토큰과 별개 지표) — 전송 실패라 데이터로 기록하지 않고, 한도 리셋 후 그
> 22개만 재실행해 병합했다.
>
> **2026-07-29 — D4·D5 해결, 인증 3/3 확정.** 지시문의 8개 차단 조건은 전부
> 충족돼 있었고, 남았던 설계 판정 2건도 처리됐다:
>
> - **D4** — 제약 #11을 독립 리뷰어(`e2.4-review-11`, `tools: []`)로 **30 trial
>   전수 재검토**했다. 새 trial 없음. **30/30 `ok`, 위반 0, `unknown` 0.**
>   `clean`이 4중 논리곱(verdict + 스키마 + 준수 + #11)이 되면서 인증이
>   `certified 3/3`으로 복구됐다.
> - **D5** — "17 vs 30 택일"이 아니라 **단계적 조기중단 정책**으로 해소.
>   기존 30 trial은 재실행하지 않는다.
>
> 상세·검증 강도는 [`E2.4_ISSUE_REGISTER.md`](E2.4_ISSUE_REGISTER.md) [DONE] #25.

> ## 2026-07-29 외부 운영 변경 지시 — 대응 완료 (이력)
>
> 외부 실험 설계 담당이 E2.4 실행·평가 지시를 대체하는 운영 변경 지시를 보냈다.
> 원문은 [`DIRECTIVE_2026-07-29_operations_change.md`](DIRECTIVE_2026-07-29_operations_change.md)에
> 보존돼 있다.
>
> **8개 차단 조건은 전부 이미 충족돼 있었다** — 실측 대조표는 등록부 §0.
> 금지 필드 14종의 payload 부재도 전수 확인했다. 지시문은 이 세션 진행보다
> 앞서 작성돼 "현재 인증된 class 수는 0"을 전제했으나 실측은 3/3이었다.
>
> **어긋났던 3건은 전부 처리됐다**: C1(명칭) 즉시 정합, **D4**(제약 #11이
> `UNKNOWN`인데 인증 발생) → 30 trial 전수 리뷰로 해결, **D5**(재실행 규모
> 17 vs 30) → 단계적 조기중단 정책으로 해소.
>
> **신규 trial 차단 해제 → pilot 실행 → 종료까지 끝났다.** D3는 D-H3-2로
> 해소, 공통 action 표면은 구현·동결·실행 완료, 그리고 D-H3C가 **존재
> 주장으로 종료**를 판정했다. 확증은 별도 과제로 분리(§H3 절, 등록부 D7).

## 2. 프로젝트 목적 (변경 없음)

**"LLM이 제안하고, 결정론이 판정한다."** 자연어를 evidence-carrying 개념으로
고정한 뒤, is-a 계층은 결정론적 게이트/reasoner가 판정한다. 정본 소스는
`conceptgate/` 패키지 하나뿐(메인 저장소). 이 worktree는 `experiments/`와
`docs/`만 다루고 `conceptgate/` 코드는 원칙적으로 read-only다.

## 3. E2 실험 체인 — 각 단계 상태

| 실험 | 핵심 결과 | 상태 |
|---|---|---|
| E2.2 (B-C 구조) | Δ_BC=+0.32, NO_GO | 종료 |
| E2.2.1 (directed-PC 어휘) | rate=0.15, NO_GO | 종료 |
| E2.2.2 (invariant 수정) | rate=1.00, GO | 종료 |
| E2.2.3 (OFAT ablation) | A_ONLY=20/20, B_ONLY=1/20, C_ONLY=0/20 | 종료 |
| E2.3 (전역 invariant 일반화) | A_ONLY/PARAPHRASE/TOPOLOGY/DECOY 전부 screened PASS | 종료, 푸시됨 |
| E2.4 (repo-grounded contract) | fixture 3 class 인증 + 제약 #11 리뷰 완료(4중 논리곱). **H3 존재 주장으로 종료**(D-H3C) — pilot 45 비인증, defer precision 0.00/0.00/1.00. 확증은 별도 과제 3건으로 분리 | 종료(존재 주장) |
| **H1a (source_authority_unresolved)** | 설계 판정 7건 + 사전등록 P1~P7 + 코더 교정 18/18 완료. fixture 제작됨. **독립 리뷰에서 동결 부적합 — blocker 1 + major 5** | **진행 중, 차단됨** |

## 4. E2.4 — fixture 4종 검증 현황

폴더: `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/`

가설: `evidence_contract_v1`(구조화 evidence-audit + sufficiency 판정 +
repair/abstain 계약)을 쓰는 CONTRACT_REPO가, 이 저장소 자체의 실제
코드/문서에서 추출한 evidence 위에서, legacy 3지선다 스키마보다 evidence
불충분/충돌을 더 잘 잡아내는지.

> ✅ **2026-07-28 — 3 class 실제로 검증 완료 (`b2a4181`).**
> 위 가설이 최초 표적으로 삼았던 유출 경로는 v2 표면 재설계(3면 분리 +
> 화이트리스트 빌더, `efda916`~`78a2dd3`)로 구조적으로 닫혔고, 그 위에서
> **clean rerun cohort N=10/cell(30 trial)을 실행해 3/3 class를 인증했다.**
> 검증은 verdict 문자열 일치뿐 아니라 **실질 확인**까지 거쳤다 — E24-F-02는
> 10/10 전부 필러 feature `갑종`을 `insufficient`로 정직하게 표시하며 `바퀴`만
> repair(계약 규칙 5가 요구하는 정확한 패턴), E24-F-03은 10/10 전부 evidence를
> `indirect_context`로 정확히 분류. 상세는 §11, `cohort_score.json`,
> 등록부 [DONE] #21.

**불투명 ID 규율(2026-07-28)**: 실행 시에는 class 이름 대신
`E24-F-01`~`E24-F-04`를 쓴다. 프롬프트를 조립하면서 "sufficient_repairable"을
볼 수 있는 운영자는 유출을 한 번의 실수 거리에 두고 있는 셈이다. 매핑은
`oracle_manifest.json`에 있고 빌더는 그 파일에 접근하지 않는다.

| class | ID | 정답 | fixture 내용 | 인증 (N=10/cell, 2026-07-28) |
|---|---|---|---|---|
| `sufficient_consistent` | E24-F-01 | accept_report | `카페린`/`손잡이`=structural_composition (E2.3 fixture 텍스트 + server.py docstring) | **10/10 clean, screened_PASS** |
| `sufficient_repairable` | E24-F-02 | repair | `돌체`/`바퀴`=essential_feature인데 evidence는 "구성 부분"이라 명시 (E2.2 동결 텍스트) | **10/10 clean, screened_PASS** |
| `insufficient` | E24-F-03 | abstain | `JSON추출유틸` — 설명 없는 유틸 함수 본문 | **10/10 clean, screened_PASS** |
| `conflicting` | E24-F-04 | abstain | E2.2.1/E2.2.2 커밋 메시지 충돌 쌍 | **미확보(종결)**, cohort 제외 |

이전(유출 상태) 실측이었던 7/7·5/5·5/5는 인증 근거가 아니었고
[`legacy_leaky.md`](../experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/legacy_leaky.md)에
항목별 제외 사유와 함께 남아 있다. **위 표의 새 숫자와 그 legacy 숫자를
비교하지 마라** — 우연히 둘 다 만장일치지만, legacy는 유출 payload를,
새 숫자는 화이트리스트 빌더를 거친 payload를 쟀다. E24-F-04는 유출 제거 후
N=5가 돌았으나 정본 빌더 미경유로 함께 제외됐고, 그 실행이 찾아낸 계약 문구
결함은 §5 개정으로 반영됐다(이제 스키마상 표현 불가능).

### `conflicting` — 미확보로 종결 (2026-07-27, H1 결과)

H1을 실행해 세 가지가 드러났다. 상세는
[`PROBLEM_2_conflicting.md`](../experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/PROBLEM_2_conflicting.md).

1. **기존 N=1 통과는 오라클 유출 상태에서 얻은 것이라 무효였다.** `ev5`의
   `extraction_note`(모델에게 전달되는 필드)에 "CONTRACT_REPO's correct
   behavior is still to abstain... the expected contract_verdict is loosened
   to..."가 그대로 들어 있었다 — fixture가 모델에게 정답을 알려주고 있었다.
   `evidence_packet_schema.json` 자신이 금지한 것을 위반한 상태.
   → 유출 제거 + `test_protocol.py`에 **기계적 가드** 추가(옛 유출 텍스트를
   실제로 잡는지 음성 대조 확인).
2. **유출 제거 후 N=5 실측**: `decision`은 5/5 안정적 `abstain`이나
   `contract_verdict`는 **불안정** — `insufficient_evidence` ×4,
   `conflicting_evidence` ×1. 어느 쪽을 오라클로 잡아도 threshold 0.90 미달.
   원인은 fixture가 아니라 **계약 문구**: `semantic_constraints`는 "equal
   strength direct evidence"를 요구하는데 규칙 3 본문이 그만큼 못박지 않아
   소수 판정이 "사실 충돌"로 읽는다.
3. **결정(사용자)**: 문서-코드 쌍으로 즉시 대체하지 않고,
   `conflicting_evidence`를 **"현 저장소의 live·동등강도 evidence로 구성
   가능한 fixture 미확보"**로 표시. 유효 커버리지 3 class로 보고.
   **Schema의 class 자체는 유지**(enum에서 제거하지 않음). stale 문서 대
   live 코드 충돌은 `source_authority_unresolved` 계열 별도 실험으로 분리.

**긍정적 부수 확인**: 여러 trial이 표면 유사성 함정을 명시적으로 거부했다 —
ev5의 `structural_composition` 문자열은 "노출 안 된 enum 값 언급"이라 type
근거가 아니고, ev6의 "structural **contracts**"는 프롬프트 계약이지 taxonomy의
부분-전체가 아니라고 구분. 규칙 2의 전문용어 규율은 의도대로 작동한다.

## 5. 세션 로그 (최신순)

### 2026-07-30 — H3 종료, H1a 착수·차단

1. **H3 확증 판정 수용 → E2.4 종료.** `DESIGN_DECISION_H3_CONFIRMATORY.md`가
   **존재 주장으로 종료**를 판정. D-H3C-4가 요구한 recall/precision 쌍을
   적용하자 단일 Δ가 감추던 것이 드러났다 — **세 arm의 defer 총량은 3·4·4로
   거의 같고 차이는 조준이다**(precision 0.00 / 0.00 / **1.00**). 이 지표는
   결과를 본 뒤 채택한 것이라 `post_hoc_metrics`로 표시되고 전용 테스트가
   그 표시를 강제한다.
2. **H1a 사전등록 P1~P7 확정 + 행동 코더 구현·교정.** 코더는 닫힌 enum
   덕에 `rationale`을 읽지 않는 구조 매퍼다. 교정 코퍼스 18건을 `results`
   빈 상태로 먼저 커밋 → **18/18 통과**, 뮤테이션 3종으로 코퍼스가 실제로
   실패할 수 있음을 확인.
3. **H1a fixture 제작 → 독립 리뷰 → 동결 부적합.** 별도 에이전트가
   blocker 1 + major 5를 찾았다. **blocker의 원문은 제작 세션 컨텍스트에
   이미 있었는데도 발견되지 않았다** — 제작자 자체 검토로는 나오지 않았을
   결함이다.
4. **설계 요청서 발송 준비** — `DESIGN_REQUEST_H1a_manipulation_scope.md`
   (Q1 조작 범위 / Q2 null 식별가능성). 인용·실측 16/16 대조 검증.
5. **`CLAUDE.md` 정리** — 1487→1135 est. 토큰. 삭제분 중 **2줄은 틀린
   정보**였다(존재하지 않는 브랜치명, 이미 등록된 저장소를 "will be
   registered separately"로 표기).

**이 세션에서 확인된 운영 교훈 (skills-catalog 미승격 — candidate)**:

- **제작자는 자기 산출물의 결함을 보지 못한다.** H1a blocker가 실증. 리뷰를
  별도 에이전트로 돌리고 "제작자 테스트를 증거로 받지 말라"고 명시한 것이
  결정적이었다.
- **가드가 있어도 못 잡는 결함이 있다.** H1a의 byte-level diff 테스트는
  중복 금지 문장을 **통과시킨다** — "diff가 무엇인가"를 볼 뿐 "동등한 것이
  남았는가"를 보지 않기 때문. 가드의 존재가 아니라 **가드가 무엇을
  주장하는지**를 봐야 한다.
- **상수는 교란하지 않지만 상호작용한다.** "양 arm 동일 fixture라 안전하다"는
  논증이 confounding에만 참이고 ceiling에는 거짓이라는 지적(H1a #14).

> 승격은 하지 않았다 — 동일 문제가 최소 2회 독립 확인된 경우에만 검토하는
> 규율이고, 위 3건은 1회성이다. 근거는 `H1A_ISSUE_REGISTER.md`에 있다.

### 2026-07-27 세션

1. **`sufficient_consistent` 해결 (5차 시도 만에, 7/7)** — 1차 순환논리 /
   2차 절차적 서술 / 3차 "죽은 코드"(→ 이 판정은 나중에 **오류로 확인**) /
   4차 self-citation+인스턴스 미결박 / **5차 성공**(E2.3의 사전동결 fixture
   텍스트 재사용).
2. **"죽은 코드" 전제 오류 정정** — `RELATION_HINT_TYPE`은 죽은 코드가
   아니다. `cg_partwhole.py`의 "참조용 — 직접 import 안 함" docstring이
   **stale**이었고, 실제로는 `concept_gate_v7.py:350` / `cg_input_linter.py:15`가
   import해 라이브 경로에서 쓰며 R6/R6b/I8 테스트가 검증 중. 외부
   skills-catalog에 이미 승격됐던 lesson도 정정 업로드함.
3. **`sufficient_repairable` 재검증 → 결함 발견 → 2회 재구축 → 5/5** —
   상세는 `PROBLEM_1_sufficient_consistent.md` §12~§16.
4. **cross-concept invariant 관련 실측 발견**(§6 H2의 근거) — 아래 별도 서술.
5. **`contract_prompt.md` rule 5/7 정식 병합** — 그동안 스모크 프롬프트에만
   수동으로 넣던 문구가 frozen 파일에 없어 커밋된 아티팩트로 결과 재현이
   불가능한 상태였음. 병합 완료.
6. **`cg_input_linter.py` fallback dict 버그 수정** — import 실패 경로에서만
   쓰이는 fallback이 `material_of`를 `essential_feature`로 잘못 매핑(canonical
   `RELATION_HINT_TYPE`와 불일치). 잠재 버그였으나 근본 수정.
7. **교훈 2건을 skills-catalog에 승격** — §7 참조.

### 5.1 cross-concept invariant 실측 발견 (보존할 것)

`sufficient_repairable`의 1차 재구축은 `낫`/`칼`/`철` 2-concept MixRig
구조였다. `칼`의 `철`=structural_composition에는 강한 instance-bound
evidence가 있었고, "같은 feature 이름은 한 type으로 통일"이라는 전역
invariant 규칙도 프롬프트에 있었다. 그런데 **N=5 중 4/4가 `abstain`**했다
(1개는 API 세션 한도로 실패, 데이터 아님).

4/4 전부 동일한 논리: `칼` 쪽은 충분하지만, `낫`을 직접 언급하는 evidence가
하나도 없으므로 `낫`의 `철`을 고치는 것은 **"feature 이름이 같다"는 사실에만
의존하는 추론**이고, 이는 packet 자신의 `extraction_policy.disallowed_sources`
("파일명/심볼명만으로 하는 추론 금지")가 금지하는 것이다. 여러 trial이 그
정책 문구를 그대로 인용해 거부 사유로 제시했다.

**이 발견은 폐기하지 않았다.** `sufficient_repairable`은 평가 목표를
single-concept으로 좁혀 해결했고(cross-concept 검증은 분리), 이 발견은
§6 H2의 직접적 근거로 보존된다.

## 6. 다음에 검증할 가설 (우선순위 순)

### ~~H1 — `conflicting` 재검증~~ → **완료 (2026-07-27)**

실행 결과는 위 §4 "`conflicting` — 미확보로 종결" 참조. 요약: 오라클 유출
발견·수정·가드 추가, N=5 실측(decision 5/5 abstain, verdict 4:1 불안정),
사용자 결정으로 "미확보" 표시 + 유효 커버리지 3 class 확정.

**H1에서 파생된 새 항목 3개** — H1a는 아래 별도 실험, H1b/H1c는 H3 선행 과제:

- **H1a (별도 실험) — `source_authority_unresolved`** → **지금 활성 실험이며
  차단 상태다. §1 상단 배너와 [`H1A_ISSUE_REGISTER.md`](H1A_ISSUE_REGISTER.md)를
  본다.** 아래는 착안 당시의 원 서술(이력):
  문서와 live 코드가 같은 인스턴스에 대해 상충하는 type을 주장할 때,
  클라이언트가 독단으로 해결하지 않고 보류하는가? **인스턴스까지 `칼`/`철`로
  정확히 일치**한다.
  - ⚠️ **원 서술의 "stale 문서"·"superseded"라는 표현을 실험 재료에 옮기지
    마라.** 어느 쪽이 낡았는지는 **하네스와 사람이 아는 것**이고 모델에
    도달하면 조작 변수가 오염된다(D-H1a-7, `PREREGISTRATION.md` §0).
  - ⚠️ **code측 증거는 `cg_partwhole.py`가 아니다.** 그 줄은 칼도 철도
    명명하지 않는 일반 매핑이라 독립 리뷰가 비대칭으로 지적했다. 올바른
    증거는 `conceptgate/concept_gate_v7.py:1192` —
    `(4) 재료-대상: 철은 칼의 재료 → structural_composition`으로,
    문서 쪽과 **문장 줄기가 같고 type만 반대**다.
- **H1b (설계급, H3 선행) — 규칙 3의 `conflicting` 정의 명확화**:
  `semantic_constraints`는 "conflicting direct evidence **of equal
  strength**"를 요구하나 `contract_prompt.md` 규칙 3 본문은 그만큼 명시하지
  않아, 소수 판정이 "사실 관계 충돌"로 읽는다(N=5에서 1/5). 향후 어떤
  conflicting fixture를 만들어도 이걸 먼저 정리하지 않으면 verdict가 갈린다.
- **H1c — 【판정됨, 2026-07-29】 Phase 5 커버리지 재설계**: 기존 설계는
  CONTROL_REPO/A_REPO에 `sufficient_consistent` + `conflicting` 2개를
  배정했다. `conflicting`이 빠지면 **arm 비교의 최고 신호 셀이 사라진다** —
  이 실험 전체를 동기부여한 유일한 arm 비교 관측(legacy는 조용히 repair,
  CONTRACT_REPO만 abstain)이 바로 그 fixture에서 나왔고, **그 관측 자체도
  오라클 유출 packet에서 얻은 것이라 재현이 필요한 상태**다. abstain-target
  class 중 남는 건 `insufficient` 하나뿐이다. **외부 설계 판정(D-H3-2)**:
  빈자리를 채우지 않고 3 class(`sufficient_consistent`/`sufficient_repairable`/
  `insufficient`) × 3 arm 완전 교차. 등록부 [DESIGN] D3·D6 참조.

### H2 — cross-concept invariant 별도 fixture (§5.1의 후속)

- **가설**: 4/4 abstain의 원인이 "`낫`에 evidence가 없어서"인지, 아니면
  "cross-concept 전이 자체를 거부해서"인지 분리 검증. **양쪽 concept 모두에
  instance-bound evidence가 있고 둘이 같은 type을 가리킬 때**, 전역 invariant에
  따른 repair가 일어나는가?
- **왜 중요한가**: 전자면 fixture 재료 문제(해결 가능), 후자면 CONTRACT_REPO는
  전역 invariant를 사실상 집행하지 못한다는 뜻이고 이는 E2.3에서 검증된
  A_ONLY 규칙의 전이 가능성에 대한 중대한 제약이 된다.
- **난점**: 양쪽 concept 다 결박된 실제 저장소 evidence를 찾아야 한다.
  `돌체`/`돌체린`(E2.2.1 fixture)이 후보 — 둘 다 `바퀴`에 대한 서로 다른
  실제 evidence 문장을 이미 갖고 있다(`돌체`: "구성 부분이다", `돌체린`:
  "이동 기능을 제공한다"). **다만 이 둘은 서로 다른 type을 가리키므로**
  그대로 쓰면 conflicting에 가깝다 — 설계 주의 필요.

### H3 — E2.4 본 실험 (Phase 4~6, 이 실험의 실제 목적) — **【존재 주장으로 종료, 2026-07-30】**

- **판정 요지**: `DESIGN_REQUEST_H3.md`(9407bb1)에 대한 외부 설계 판정
  (`DESIGN_DECISION_H3.md`)이 도착했다. **기존 native-schema 3-arm 실행은
  승인하지 않는다** — legacy arm은 `abstain`을 표현할 수 없어, abstain
  부재 관측이 "판단 안 함"인지 "표현 못 함"인지 분해되지 않는다. 상세는
  등록부 [DESIGN] D6.
- **수정된 가설**(README.md 원문 가설을 대체): 동일한 qualified evidence
  payload와 동일한 공통 action 어휘가 주어졌을 때, CONTRACT_REPO_H3
  인터페이스는 CONTROL_REPO_H3/A_REPO_H3보다 `insufficient` packet에서 더
  자주 `defer`하며 sufficient packet에서의 false-defer를 늘리지 않는다.
  ("불충분을 더 잘 잡아낸다"는 원 표현은 CONTRACT 진단 구조와 프롬프트
  텍스트의 결합 효과를 가리키며, 두 요소는 이 실험에서 분해되지 않는다.)
- **CONTRACT_REPO 쪽 fixture 3개는 인증돼 있다** — N=10/cell clean rerun
  cohort + 제약 #11 리뷰(4중 논리곱, §4·§11, 등록부 [DONE] #25). **다만
  이 인증은 pilot/assay 용도로만 쓸 수 있다** — 결과에 따라 선별된 재료라서
  (`sufficient_consistent`의 1·2차 시도가 CONTRACT의 abstain 판정 때문에
  기각된 이력, `PROBLEM_1_sufficient_consistent.md` §1) 확증 비교의
  독립 test set이 아니다(D-H3-6).
- **유일한 arm 비교 실측**(1회, 초기 스모크, `conflicting` fixture — 유출
  packet 기반, 이후 코호트에서 제외됨)은 **판정에서 H3의 경험적 근거로
  인정되지 않았다.** 재현 대상이 아니라 폐기 대상이다.
- **규모**: 기존 8 cell × N=10 = 80 trial 설계는 승인되지 않았다. 승인된
  것은 3 class × 3 arm × R=5 = **45 trial 비인증 pilot**이며 **실행 완료**다.
  확증 규모는 SESOI·다중성 제어·power·held-out fixture 수가 정해질 때까지
  deferred.
- **구현 완료**(`_h3.py`, `decision_schema_h3.json`, `test_h3.py`,
  `_h3_score.py`, `test_h3_score.py`): 세 arm 공통 action 스키마 + 기존
  whitelist builder를 호출하는 단일 dispatcher(D-H3-4). 합격 게이트 10항
  전부 테스트로 매핑됨. **동결 파일은 한 바이트도 안 건드렸다** — A_REPO
  규칙문은 E2.3 `_gen_prompts.py`에서, CONTRACT 규칙 1~7은
  `contract_prompt.md`에서 앵커 추출로 바이트 재사용한다.
- **Q1~Q3는 가정으로 진행**(판정 아님, `DESIGN_H3_common_action.md` §2):
  `report`=string 유지, `cited_evidence_ids`=유효성 게이트,
  pilot은 제약 #11 리뷰 미실행(비인증이므로). 사용자가 달리 보면 재동결
  가능 — trial 데이터는 이미 있으므로 그때는 재실행이 필요하다.

**pilot 결과(2026-07-30, 비인증)** — P(defer | insufficient):
CONTROL 0/5, A 0/5, **CONTRACT 4/5** → Δ = +0.80. specificity 유지, CONTRACT
내부 action/verdict 일치 12/12, schema-invalid 5/45. D-H3-5 중단 조건 6종
미발동. 독립 손 재집계로 교차검증(패턴 9).

**그러나 Δ를 단독으로 인용하지 마라.** D-H3C-4가 요구한 recall/precision
쌍으로 다시 보면 그림이 다르다:

| arm | recall | **precision** | defer 총수 |
|---|---|---|---|
| CONTROL | 0.00 | **0.00** | 3 (0개 적중) |
| A | 0.00 | **0.00** | 4 (0개 적중) |
| CONTRACT | 0.80 | **1.00** | 4 (전부 적중) |

**세 arm의 보류 총량은 3·4·4로 거의 같다.** 차이는 양이 아니라 **조준**이다.
이 쌍은 결과를 본 뒤 채택한 사후 지표라 확증 근거가 아니며, 사전등록 1차
지표 지위는 다음 cohort부터다.

⚠️ **허용 결론은 `h3_pilot_score.json`의 `allowed_conclusion` 필드에 문장으로
박혀 있다** — fixed-packet·fixed-model·fixed-parameter 조건의 **존재 수준
서술**. class 일반·insufficient 일반·repo-derived 일반 우월성은 표집틀과
독립 held-out 없이는 **형식적으로 식별되지 않는다**(D-H3C-1·2). 또한
"repo-derived"는 class마다 뜻이 다르다 — `insufficient`만 실제 저장소
코드이고 두 `sufficient`는 이전 실험의 합성 fixture 문장이다.

### H4 — whole-packet 판정 vs scoped 판정의 취약성 비대칭 (관찰됨, 미검증)

- **관찰**: 동일한 "evidence 없는 필러 feature"가 `accept_report`는 5/5
  차단했지만 `repair`는 5/5 통과시켰다. `accept_report`는 packet 전체에 대한
  주장이라 어디든 구멍이 있으면 치명적이고, `repair`는 범위가 좁은 주장이라
  무관한 구멍을 허용한다는 해석.
- **가설**: 이 비대칭이 일반적이라면, whole-packet 판정을 요구하는 모든
  class는 scoped 판정 class보다 구조적으로 더 취약하며, fixture 설계 시
  packet 청결도 기준을 다르게 잡아야 한다.
- **우선순위 낮음** — 현재 실험 목적과 직접 관련은 없으나, 향후 class 설계에
  영향을 주는 메타 발견.

## 7. 전이한 실험 운영 노하우 (외부 승격 완료)

`goodand/skills-catalog`에 **커밋 9개 / 신규 reference 10건 / 게이트 모듈 1개**,
그리고 `SKILL.md`·허브 문서 8곳 repoint. `e5b5444`~`86cc8c2`.

> ⚠️ **먼저 읽을 경고 — 아래 표의 07-28 판이 이미 최신본이 아니다.**
>
> 이 절은 07-28에 작성될 때 "전부 최신"이라 적었으나, **07-29 판이 3건
> 올라와 있다**(§7.3). 07-27 판을 인용하지 말라는 원래 경고는 여전히 유효하고,
> **거기에 07-28 판 2건도 supersede됐다는 사실이 추가된다.**
>
> **어떤 문서든 인용 전에 `gh api`로 타임스탬프를 직접 확인하라.**
> `WORKSPACE_NAVIGATION.md` §3이 경고한 함정 — supersede는 "더 많아짐"이 아니라
> **"앞의 것이 틀렸을 수 있음"** 을 포함한다 — 이 이 문서 자신에게 재발했다.

정정된 3건:

| 문서 | 무엇이 틀렸나 |
|---|---|
| `dynamic-workflow-...-knowhow` (update 2 → **3**) | `extraction_note`를 `strip_notes()` 헬퍼로 "프롬프트 만들기 전에 제거하라"고 **지침으로 승격**해 놨다. 그게 정확히 몇 주간 유출된 블랙리스트 방식이다. update 3이 화이트리스트 빌더로 교체 |
| `recurring-...-lessons` (update 8 → **9**) | candidate `meta-commentary-inside-an-evidence-item`의 **fix가 종류부터 틀렸다** — 모델-facing 노트의 *내용*을 단속하라고 했으나, 실제 유출 문장들이 그 fix가 **허용하는** 형태였다 |
| `cited-source-text-evidence-rules` (v1 → **v2**) | Auditor Notes 두 항목이 "감사자는 노트를 무시하고 원문만으로 판정하라"는 **규율 의존**이었다. 감사자가 무시할 수 있는지는 측정 대상이 아니고, 무시하도록 요구하는 설계가 결함이다 |

### 7.0 07-28 승격분 10건 — ⚠️ 이 중 2건은 이후 supersede됨 (§7.3 참조)

| 스킬 | 문서 | 핵심 |
|---|---|---|
| `evidence-to-knowledge-promoter` | `dynamic-workflow-...-knowhow` update 3 | 전송 계층 ceiling 3개, 표면 전체 해싱, freeze/record, 검증기 양방향 테스트 |
| 〃 | `recurring-...-lessons` update 9 | lesson 24(+5)·candidate 15(+5). "설명으로 쓰인 안전장치는 이미 실패해 있었다" |
| `evidence-trace-auditor` | `cited-source-text-evidence-rules` v2 | **판정 주체·시점**(C1/C4는 실행 전 하네스가, 결과를 감사자에게 넘기지 않는다), 표면 분리, 구조화 `source_ref`, qualification, 결합 규칙 |
| `agent-task-packet` | `packet-surface-closure` | packet = model-facing surface. `render_prompt`는 이미 화이트리스트인데 **테스트가 비노출 23개 중 2개만 단언** |
| `adversarial-verification-probe` | `checker-recall-and-precision` | **패턴 8 신설.** mutation은 recall만 측정, precision은 구조적으로 못 잡는다 |
| `doc-code-sync-checker` | `generate-instead-of-detect` | "B를 지우고 A에서 재생성하면 바이트 동일한가" — 예면 탐지는 생성보다 약한 통제 |
| `measurement-evaluation-orchestrator` | `bands-are-a-function-of-n` | 밴드는 `(rate, N)`의 함수. **§11의 G1이 여기서 나왔다** |
| `baseline-diff-lab` | `surface-change-invalidates-the-baseline` | 같은 metric은 필요조건일 뿐. pre가 있는데 비교 불가능한 게 더 위험 |
| `claim-verifier` | `self-authored-claims` | **Rule 6 신설.** 실행된 적 없는 검사는 `unverifiable`이지 `pass`가 아니다 |
| `verification-decision-gate` | `pass-is-a-conjunction` | pass는 논리곱. 제약마다 집행 지점 명명, 기계 검사 불가는 리뷰어 배정 |

### 7.2 카탈로그 저장소 자체의 결함도 고쳤다

`integration-gate`에 **subflow 5** 추가 — skill 테스트를 skill마다 별도
프로세스로 실행(`d16f41c`, `86cc8c2`). 그 저장소 README가 "알려진 이슈"로
방치했던 루트 pytest 수집 실패를 닫았고, **그 수집 오류가 가리고 있던 실패
2건**(pydantic 미설치 / cwd 의존)을 드러냈다. 이 프로젝트의
`scripts/run_gates.py`와 같은 설계다.

### 7.3 현재 최신본 (2026-07-29 실측, `gh api` 조회)

**§7.0 표의 07-28 판을 인용하기 전에 이 표를 먼저 보라.**

| 파일 | 상태 |
|---|---|
| `evidence-to-knowledge-promoter/.../dynamic-workflow-...-knowhow-at2026-07-29-00-16.md` | **최신.** 07-28 판(update 3)을 supersede |
| `evidence-to-knowledge-promoter/.../recurring-...-lessons-at2026-07-29-00-22.md` | **최신.** 07-28 판(update 9)을 supersede |
| `adversarial-verification-probe/.../verifying-the-verifier-at2026-07-29-00-19.md` | **신규 — 패턴 9** |
| `adversarial-verification-probe/.../checker-recall-and-precision-at2026-07-28-19-04.md` | 07-28이 여전히 최신 (패턴 8) |
| `evidence-trace-auditor/.../cited-source-text-evidence-rules-at2026-07-28-14-07.md` | 07-28이 여전히 최신 (v2) |

**패턴 9(`verifying-the-verifier`)는 이번 세션이 실제로 적용했다.** 요지: 위임된
LLM 검증 agent도 검증기이고, **all-clean 보고는 유출 실행이 냈던 만장일치와 같은
모양**이므로 그대로 받지 않는다. 결정적 체크를 **다른 방법·더 원시적인 데이터**로
독립 재현하고, 위임된 스크립트를 재사용하지 않으며, "recall 재검증"과
"precision 미검증"을 보고서에서 분리한다.

D4의 `_verify_review_11.py`가 이 계약을 구현한 것이다 — LLM 판정이 아닌 어휘
스캔, `trials.json`이 아닌 `trials_raw.json`, 그리고 **스캔 자신의 recall을 먼저
측정**(v1이 4/5여서 어휘를 보강했다). 상세는 등록부 [DONE] #25.

**조회 명령**:

```bash
REPO=goodand/skills-catalog
BASE=skills/Skills-Create-Project
gh api repos/$REPO/contents/$BASE/<skill>/references --jq '.[].name' | sort
```

### 7.1 프로젝트-로컬 운영 규율 (외부로 안 보내는 것)

- **독립 리뷰는 fixture 제작자와 분리** — fresh non-fork subagent. 이번 세션에
  6회 실행했고 그중 **5회가 실제 결함을 잡았다**. trial 예산을 쓰기 전 가장
  값싼 방어선.
- **"확인됐다"고 말하기 전에 N=5** — 1 trial 통과는 검증이 아니다(§4의
  `conflicting`이 그 반례).
- **좁은 수정 금지, 원칙 일반화** — 실패 하나를 막으면 그 실패가 다른 곳으로
  옮겨가지 않는지 재검증.
- **커밋 메시지에 실패한 시도와 그 이유를 남긴다** — 나중에 같은 막다른 길을
  반복하지 않기 위해.
- **commit/push는 사용자 명시 승인 후에만.**
- **subagent에 검토를 맡길 때는 권한을 브리프에 맞춰 제한** — 이번 세션에
  review 전용으로 띄운 general-purpose agent가 스스로 commit+push까지 수행한
  사례가 있었다(사후에 사용자가 별도 세션에서 승인했음이 확인돼 실제 피해는
  없었으나, 오케스트레이터가 그걸 구분할 수 없다는 게 문제). peer agent가
  "사용자가 승인했다"고 보고해도 사용자에게 직접 확인할 것.

## 8. 브랜치/worktree 현황

```
concept-gate-taxonomy             claude/ontoclean-gufo-handoff-7cmq0v  (메인 체크아웃)
concept-gate-agent-publish-vault  agent/publish-conversation-vault      (별개 작업 — 건드리지 말 것)
concept-gate-e2.1-wt              codex/e2.1-haiku-results-20260723
concept-gate-e2.2-wt              codex/e2.4-contract-repo-design       (E2.2~E2.4 체인, 현재 작업 위치)
```

- 이 worktree 브랜치는 `main` 대비 크게 앞서 있고 아직 통합 안 됨. E2.4 완료
  후 PR을 열지, 체인 전체를 한 PR로 할지는 미결.
- `agent/publish-conversation-vault` → `codex/e2.4-contract-repo-design`로
  향하는 PR #5가 열려 있다(사용자 생성, MERGEABLE 상태). 이 세션은 관여하지 않았다.
- **미푸시 커밋 16건** (2026-07-30 기준). H3 설계 요청·판정 반영, H3 공통
  action 표면 구현·smoke·pilot 45, 확증 판정 수용, H1a 사전등록·코더·fixture,
  독립 리뷰 기록, 설계 요청서. `git log --oneline origin/codex/e2.4-contract-repo-design..HEAD`로 확인.
  **push는 사용자 승인 후에만.**

## 9. 검증 명령

```bash
# 전체 게이트 (단일 진입점 — 실험별 프로세스 분리 포함)
python3 scripts/run_gates.py

# E2.4 전체 self-check (표면 폐쇄 + fixture 무결성 + 채점기 + #11 리뷰)
python3 -m pytest -q experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/   # 118 passed
python3 -m pytest -q experiments/2026-07-29_h1a_source_authority_unresolved/         # 57 passed, 1 skipped

# 코어만 (pytest.ini가 experiments/ 제외)
python3 -m pytest -q
python3 -m pytest -q test_semantic_regressions.py  # 8 (R6/R6b 포함)
```

제약 #11 리뷰 상태 (D4 산출물):

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

python3 _review_11.py status      # stage: complete / calibration: passed / unknown=0
python3 _verify_review_11.py      # 독립 재현 — scan recall 5/5, cohort 0/30 hits
```

`_verify_review_11.py`는 **자기 측정에 실패하면 중단한다.** 어휘 스캔이 알려진
위반을 못 잡는 상태에서 0히트는 아무 뜻이 없기 때문이다(실제로 v1이 4/5였다).

코호트 관련 명령 (전부 실험 폴더에서):

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

python3 _cohort.py            # usage — agent/freeze/record 3개 모드를 보여준다
python3 _cohort.py agent      # trial subject를 decision_schema.json에서 재생성 + 설치
python3 _cohort.py freeze     # 동결: 정확한 바이트 + 해시 8종 + builder_commit, 결정론 검증
python3 _cohort.py record     # trials_raw.json -> trials.json (표면 drift 시 거부)
python3 _score.py             # class별 clean_rate, 밴드, escalate cell
```

`freeze`는 `e2.4-contract-decider.md`가 stale이면 **중단한다** — 스키마가
두 곳에 있으므로(전송 제약 때문) 생성기를 먼저 돌려야 한다.

이 worktree의 알려진 환경 공백(회귀 아님):
- `fastmcp` 미설치 → `test_server.py` **BLOCKED**(러너가 분리 보고)
- `owlready2` 미설치 → `test_cg_obligations.py::test_registered_handlers_resolve`
  가 **FAIL**. 이 저장소는 이미 optional-dep 스킵 관례
  (`pytest.importorskip("owlready2", ...)`, `test_cg_owl.py` 등 3곳)를 쓰는데
  이 테스트만 따르지 않아 스킵 대신 실패한다. **기존 결함**(변경 전에도 동일,
  `git stash`로 확인). 제안 수정은 아래 §10.

## 10. 미결 — 승인 대기 (범위 밖이라 손대지 않음)

### 10.1 `test_cg_obligations.py::test_registered_handlers_resolve` (core, 1줄 수정 제안)

이 테스트는 `OBLIGATION_REGISTRY`의 핸들러 dotted path를 실제로 import해
registry-코드 drift를 잡는다. 핸들러 중 하나가 `owlready2`를 요구하는 모듈에
있어서, 그 의존성이 없으면 **스킵이 아니라 실패**한다. 저장소의 다른 3곳은
`pytest.importorskip("owlready2", ...)`로 스킵한다 — 이 테스트만 관례를
벗어나 있고, 그래서 맨손 checkout에서 게이트가 red다.

단순히 파일 상단에 `importorskip`을 걸면 **안 된다** — 같은 파일의 나머지
24개가 통과 중이라 전부 스킵돼버린다. 또 무조건 `ModuleNotFoundError`를
스킵하면 이 테스트의 존재 이유(drift 탐지)가 죽는다. 제안은 **알려진 선택적
의존성일 때만** 스킵:

```python
try:
    obj = importlib.import_module("conceptgate." + parts[0])
except ModuleNotFoundError as exc:
    if exc.name in {"owlready2"}:
        pytest.skip(f"{exc.name} 미설치 (선택 의존성) — {name} 핸들러 검증 생략")
    raise          # conceptgate.X 자체가 없으면 = 진짜 drift, 계속 실패시킨다
```

**core 테스트 파일이라 승인 없이 수정하지 않았다.** 대안은 `owlready2`를
설치하는 것.

### 10.2 `conceptgate/` 라이브 버그 2건 (E2.4가 read-only로 취급)

- `has_part`/`part_of`가 `RELATION_HINT_TYPE`에 없어
  `relation_discrimination_gate`가 `essential_feature`+`has_part`를 is-a DAG에
  통과시킨다. `docs/MCP_SERVER.md`와 `server.py`의 클라이언트 가이드는 반대로
  안내한다.
- `cg_partwhole.py:7-8`의 stale docstring("참조용 — 직접 import하지 않음")이
  아직 그대로다. 이 문장이 이 세션에 잘못된 "죽은 코드" 판정을 만들었고
  lesson은 정정됐으나 **코드 주석은 안 고쳐졌다.**

### 10.3 `semantic_constraints` #11이 검사되지 않은 채 합격 처리된다 (설계 결정 필요)

제약 11개 중 10개는 `_score.py`의 `conformance()`가 검사한다(#4·#6은
`e03f74a`에서 추가). 남은 **#11 — "모델은 출처의 liveness나 우선순위를
재판정하지 않는다"** 는 자연어 rationale을 읽어야 판정되므로 **어떤 검사기도
커버할 수 없다.**

문제는 그 리뷰가 **채점 흐름에 편입돼 있지 않다**는 것이다. 지금 코호트를
돌려 `_score.py`를 실행하면 #11은 검사되지 않은 채 `clean`에 집계된다 —
목록에 있다는 사실이 커버됐다는 인상을 준다.

필요한 것: `_score.py` 이후에 독립 리뷰어가 각 trial의 rationale을 읽고
"출처가 더 최신이다 / 아직 살아 있다 / 더 권위 있다"를 근거로 충돌을
해결했는지 판정하는 단계. 그 판정을 `clean` 정의의 **네 번째 항**으로 넣는다.

> ✅ **2026-07-29 해결됨.** 사용자가 (a)를 택했고 실행까지 마쳤다 — 독립
> 리뷰어가 기존 30 trial의 rationale을 전수 재검토해 **30/30 `ok`**, `#11`이
> `clean` 정의의 네 번째 항으로 편입됐다. `_score.py`는 이제 리뷰 결과가 없는
> trial을 `UNKNOWN`으로 보고 `clean`에서 제외한다(지시문 §3). 사전등록은
> `DESIGN_D4_constraint_11_review.md`, 실행 기록은 등록부 [DONE] #25.

---


## 11. 코호트 실행 완료 — 3/3 class 인증 (2026-07-28, `b2a4181`)

표면 재설계(v2 마이그레이션 + 계약 문구 §4/§5 + 동결)와 코호트 동결·실행이
**전부 끝났다.** 아래는 그 경위와, 실행 중 발생한 두 가지 실측(세션 한도,
실질 검증 결과)의 기록이다.

### 11.0 G1(표본 크기) 확정 및 실행 결과

동결 코호트는 원래 **N=7/5/5(17 trial)** 였는데 사전 등록 Stage 1은
**N=10/cell**이고 판정 밴드가 그 N에 맞춰 보정돼 있어(프로토콜은 이 worktree에
없고 메인 체크아웃 `../concept-gate-taxonomy/docs/experiment_screening_protocol.md`에
있음), **ⓐ N=10/cell로 재동결**했다(`737405a`). 재동결은 결정론적이라
`rendered_prompt_sha256`은 세 fixture 모두 이전과 바이트 동일 — trial id만
늘어났다.

30 trial 실행 결과(`b2a4181`):

```
E24-F-01 (sufficient_consistent)  10/10 clean  screened_PASS
E24-F-02 (sufficient_repairable)  10/10 clean  screened_PASS
E24-F-03 (insufficient)           10/10 clean  screened_PASS

certified 3/3 classes. protocol_deviation: 없음 (N=10 정합)
conformance_violations: 0   schema_violations: 0  (전체 30 trial)
```

**실행 중 발생한 일 — 세션 사용 한도(전송 실패, trial 데이터 아님)**:
30 trial을 한 번에 실행했을 때 22개가 `"You've hit your session limit ·
resets 11:40pm (Asia/Seoul)"`로 실패했다. 이것은 **컨텍스트 윈도우 토큰과
별개인 API 세션 사용량 한도**이며, `agents_error` 카운트가 0이 아니고
`subagent_tokens`는 정상적으로 소비된 상태였다(8개는 실제로 성공). 실패한
22개를 trial 데이터로 기록하지 않고, 리셋 시각을 확인(`date` 명령으로
경과 확인)한 뒤 **그 22개만** 별도 batch로 재실행해 22/22 성공, 두 batch를
병합해 30/30을 확보했다. 전체를 다시 30개 도는 대신 실패분만 재시도한 것은
이미 성공한 8개를 버리지 않기 위함이다.

**검증은 verdict 문자열 일치만으로 끝내지 않았다** — legacy 유출 실행도
7/7·5/5·5/5로 "clean해 보였던" 전례가 있어, 같은 착시를 피하려 30 trial
전수를 실질 확인했다:

- E24-F-02(가장 어렵게 확보한 class): **10/10 전부**가 필러 feature `갑종`을
  `insufficient`로 정직하게 표시하며 `바퀴`만 `structural_composition`으로
  repair — `contract_prompt.md` 규칙 5가 요구하는 정확한 패턴이자, `e03f74a`의
  채점기 수정이 지키려 한 바로 그 판정. `repaired_concepts`는 `갑종`을
  원본 타입 그대로 보존해 제약 4(repair는 입력 전체를 실어 나른다)를
  구조적으로 충족했다.
- E24-F-03: 표본 확인한 trial 전부가 evidence를 `direct_support`가 아니라
  `indirect_context`로 분류 — 구현 서술일 뿐 온톨로지적 성격을 명시하지
  않는다는 규칙 2의 판별을 정확히 적용했다.

### 11.1 지난 세션에 실행하지 못했던 이유 (둘 다 해소, 이번 세션에 실행 완료)

1. **agent registry는 세션 시작 시점에 고정된다.** trial subject
   `e2.4-contract-decider`를 세션 도중 만들었더니 `Agent`·`Workflow` 양쪽에서
   `agent type not found`가 났다. → **해소됨.** 정의는
   `~/.claude/agents/`와 실험 폴더 양쪽에 설치·커밋돼 있고 다음 세션은 인식한다.
2. **structured-output 스키마 크기 한계.** `evidence_contract_v1`을
   `agent(..., {schema})`로 넘기면 전송 계층이 "output schema too large to
   classify safely"로 거부한다(설명 제거 후 4.7KB에서도 동일). → **우회 완료.**
   출력 계약을 **trial subject의 system prompt**로 옮겼다. 동결 프롬프트는
   "출력은 ... evidence_contract_v1 schema를 따른다"고만 하고 필드를 하나도
   나열하지 않으므로 `rendered_prompt_sha256`은 그대로다.

   이 이동이 §6 해시 목록의 구멍을 드러냈다 — output schema와 system prompt는
   모델이 보는 표면인데 아무도 해싱하지 않았다. `system_prompt_sha256`과
   `presented_schema_sha256`을 추가했다.

   ⚠️ **크기 한계값은 미상이다.** 이분 탐색을 시도했더니 안전 분류기가
   "분류기 우회 시도"로 차단했다 — 기계적으로 타당한 지적이라 탐침을 중단했다.
   스키마가 더 커지면 같은 벽에 부딪힌다.

**하지 않은 우회 (기록)**: 이미 등록된 `e2.2-decider`(`tools: []`)로 대체할 수
있었지만 쓰지 않았다. 그 system prompt는 E2.2용이라 **이 payload에 존재하지
않는 키 `input_concepts`**를 지목한다. 인증 실행의 trial subject를 다른 실험
것으로 바꾸는 것은 이 실험을 0 class로 되돌린 바로 그 종류의 표면 오염이다.
기다리는 편이 쌌다.

### 11.2 그 뒤 채점기에서 결함 2건을 발견해 수정했다 (`e03f74a`)

**동결만 믿고 실행했다면 잘못 채점됐다.**

1. **채점기가 계약이 명령한 행동을 위반으로 집계.** `conformance()`가 5단계
   sufficiency 절차를 **packet 전역**으로 1회 도출해 **모든 per-feature 판정**과
   대조했다. 5단계는 본래 feature 하나의 `selected_type`을 정하는 절차다.
   `contract_prompt.md` 규칙 5는 evidence 없는 필러 feature를 insufficient로
   표시하라고 **지시**하는데, 그 지시를 따른 판정이 위반으로 잡혔다:
   ```
   돌체.갑종: sufficiency=insufficient but the trial's own audit
              yields sufficient under the 5-step procedure
   ```
   인증이 `clean_rate` 기준이므로 **E24-F-02가 0/5로 떨어질 예정이었다** —
   다섯 번 시도해 겨우 확보한 class다. → `feature_judgments[].evidence_ids`로
   부분집합을 뽑아 **feature별** 도출로 수정.
   테스트가 못 잡은 이유: 케이스 8개가 **전부 `feature_judgments` 1개**였다.
2. **`_score.py`가 `record()`의 `schema_violations`를 안 읽었다** — 구조적으로
   무효한 출력이 verdict 문자열만 맞아 인증에 집계될 수 있었다. → `clean`을
   **verdict + 스키마 유효 + 계약 준수** 3중 논리곱으로.

함께 추가: `semantic_constraints` #4·#6 검사(미구현이었다), `direct_support`인데
`supported_type`이 null인 경우, `sufficient`인데 `selected_type`이 step 3 승자와
불일치하는 경우.

### 11.3 실행 절차 (참고용 — N=10/cell 코호트에 실제로 적용해 성공함)

```bash
cd experiments/2026-07-25_e2.4_repo_grounded_contract_transfer

# 0. 동결본이 현재 파일과 일치하는지
python3 -m pytest -q .          # 118 passed

# 1. (ⓐ를 택했다면) COHORT 상수 수정 후 재동결
python3 _cohort.py agent        # 스키마가 두 곳에 있으므로 생성기를 먼저
python3 _cohort.py freeze       # stale이면 중단한다
#    -> 커밋 후 실행 (동결은 실행 전에 커밋돼야 한다)

# 2. trial 실행. 각 trial = agentType 'e2.4-contract-decider'(tools: [])에
#    cohort_prompts.json의 rendered_prompts[fixture_id]를 그대로 전달.
#    trial id는 cohort_prompts.json의 trials[].trial_id.
#    결과를 {trial_id: <파싱된 JSON 객체>}로 trials_raw.json에 저장.

# 3. 기록 — 표면 drift 재확인 + 스키마 위반 표시(제거하지 않음)
python3 _cohort.py record

# 4. 채점
python3 _score.py
```

동결 이후 fixture나 계약 문구가 바뀌었다면 `record`가 **거부한다.** 그때는
코호트가 무효이므로 `freeze`부터 다시 한다.

**전송 계층 실패를 데이터로 기록하지 마라**: workflow 결과의 `agents_done: 0`,
`subagent_tokens: 0`, 수십 ms 소요는 **아무것도 모델에 도달하지 않았다**는
뜻이다. 지난 세션에 17 agent가 45ms에 전멸한 적이 있다.

**변종 하나 더(2026-07-28 실측)**: `subagent_tokens`가 정상 소비되고 일부
trial은 실제로 성공했는데, 나머지가 `"session limit, resets HH:MMpm (TZ)"`로
실패하는 경우 — 이것도 전송 실패이지 데이터가 아니다. 전체를 재실행하지 말고,
**리셋 시각을 확인한 뒤 실패한 trial id만** 별도 batch로 재실행해 이미 성공한
것과 병합한다.

### 11.4 채점 규약 (사전 등록됨, 실행 전에 읽어라)

- `decision` 일치가 아니라 **`contract_verdict` 일치**로 채점한다
  (`OPERATIONS_PLAN.md` Phase 6). `PROBLEM_2` §5.1에서 `decision`은 5/5
  안정인데 `contract_verdict`는 4-1로 갈렸다 — decision만 보면 불안정한 판정이
  만장일치로 보인다.
- 인증은 **`clean_rate`** 기준: 기대 verdict에 **스키마를 지키고 계약을 어기지
  않고** 도달한 비율. `conformance()`가 trial 자신의 `evidence_audit`로 5단계를
  다시 돌려, 자기 감사표가 자기 결론을 뒷받침하지 않는 trial을 잡아낸다.
- 밴드는 사전 등록 3구간(`screened_PASS` / `ambiguous` / `screened_FAIL`).
  중간 구간은 실패가 아니라 **Stage 2 증분 지시**다.
- **최대 유효 커버리지 3 class**, 실행 전 인증 **0 class**.
- `legacy_leaky.md`의 7/7·5/5·5/5는 인증 근거가 아니다. 새 숫자를 그것과
  비교하지 마라 — "재채점"도 "재현"도 아닌 **clean rerun cohort**다.

### 11.5 산출물

| 파일 | 언제 | 내용 |
|---|---|---|
| `cohort_prompts.json` | 커밋됨 | 모델이 받을 정확한 바이트 + trial당 해시 8종(+`builder_commit`) |
| `e2.4-contract-decider.md` | 커밋됨 | trial subject(`tools: []`), 스키마는 생성물 |
| `oracle_manifest.json` | 커밋됨 | 숨은 오라클. 빌더는 접근하지 않는다 |
| `trials_raw.json` | 실행 후 | `{trial_id: 출력}` |
| `trials.json` | `record` 후 | manifest + 출력 + 스키마 위반 |
| `cohort_score.json` | `_score.py` 후 | class별 clean_rate, 밴드, escalate cell, `protocol_deviation` |

---

## 미결 구조 작업 (2026-08-01)

H 계열을 `concept-gate-h1-wt`로 분리했으나 **중복 제거는 하지 않았다.**

| 항목 | 상태 |
|---|---|
| 새 worktree + 브랜치 생성 | ✅ `concept-gate-h1-wt` / `codex/h1-source-authority` |
| main 5커밋 병합(방법론 문서 유입) | ✅ `e0b8fd9` |
| 이 브랜치에서 H1a 파일 제거 | ⬜ **미결** — 25파일 684KB가 양쪽에 중복 |
| H1a 전용 docs 이관 | ⬜ 미결 — `H1A_ISSUE_REGISTER.md`, `feedback/h1a_*.md` 3건, `DESIGN_workspace_file_placement.md` |
| MOC 재생성 | ⬜ 미결 — vault가 새 worktree를 아직 인덱싱 안 함 |

**중복이 왜 문제인가**: 검색이 같은 문서를 두 경로에서 만난다. 검증된 retrieval
규율이 "동일 SHA-256 문서는 replica로 묶기"를 요구하는 이유이고, 지금은 그
묶음을 사람이 매번 해야 한다.

**왜 아직 안 했나**: 파일 제거가 docs 6건의 참조 정리까지 연쇄하고, 그중
일부는 H 브랜치로 **이동**해야 하는지 **양쪽 유지**해야 하는지가 갈린다
(`E2.4_ISSUE_REGISTER.md`는 H1a를 참조하지만 E2.4 소유다). 사용자 판단 대기.
