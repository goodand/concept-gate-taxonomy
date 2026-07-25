# HANDOFF — ConceptGate 세션 인수인계 (E2 실험 체인)

- 작성: 2026-07-25
- 대상: **컨텍스트 없이 이어받는 새 세션**. 이 문서만 읽고 작업을 재개할 수 있게 쓴다.
- 이 문서는 이 worktree(`concept-gate-e2.2-wt`, 브랜치
  `codex/e2.4-contract-repo-design`)의 최신 상태를 기록한다. **메인 저장소
  체크아웃**(`concept-gate-taxonomy`, 브랜치
  `claude/ontoclean-gufo-handoff-7cmq0v`)의 `docs/HANDOFF.md`는 별도
  문서이며 그쪽은 OWL/gUFO 동치 보고 작업(2026-07-17) 이후 갱신되지 않았다
  — 그 작업의 최신 상태는 그 문서를 그대로 신뢰해도 되지만, "지금 뭘 하고
  있는가"에 대한 답은 **이 문서**다.
- **새 실험을 시작하기 전에** 메인 저장소 체크아웃의
  `docs/EXPERIMENT_METHODOLOGY.md`를 읽어라 (이 worktree 브랜치엔 아직
  없음 — `../concept-gate-taxonomy/docs/EXPERIMENT_METHODOLOGY.md`로
  직접 접근). 동결/운영로그 분리, 실험 폴더 규약, provenance 계약,
  worktree 격리, 비-git 감사본, 교훈 승격, 독립 재현 검증 7개 규칙.
  이 worktree의 `experiments/` 구조(§3~§4)는 그 규약을 실제로 따른
  사례다.

---

## 1. 지금 상태 한 문단 (TL;DR)

`docs/obligation_layer_roadmap.md`(메인 저장소)가 정의한 M0~M5 마일스톤
체인 중 **M1(relation.is_a certificate) 검증 실험 라인**을 진행 중이다.
E2.2.1(NO_GO) → E2.2.2(GO) → E2.2.3(OFAT ablation, A_ONLY 단독 충분 확인)
→ E2.3(A_ONLY 규칙이 새 어휘/paraphrase/topology/decoy 전반에 일반화됨,
screened PASS) → **E2.4(현재 진행 중, repo-grounded evidence 위에서
CONTRACT_REPO 메커니즘 검증)**. E2.4는 문제 2(evidence-type 혼동)를
해결·5/5 검증 완료했고, 문제 1(`sufficient_consistent` fixture 재료
부족)은 **세 번째 시도까지 전부 실패**했으며 네 번째 시도(docs 재탐색,
후보 A) 재료를 막 찾은 상태에서 이 handoff가 작성됐다.

## 2. 프로젝트 목적 (변경 없음)

**"LLM이 제안하고, 결정론이 판정한다."** 자연어를 evidence-carrying 개념으로
고정한 뒤, is-a 계층은 결정론적 게이트/reasoner가 판정한다. 정본 소스는
`conceptgate/` 패키지 하나뿐(메인 저장소). 이 worktree는 실험
(`experiments/`)만 다루고 `conceptgate/` 코드를 수정하지 않는다.

## 3. E2 실험 체인 — 각 단계 상태와 위치

| 실험 | 브랜치 | 핵심 결과 | 상태 |
|---|---|---|---|
| E2.2 (B-C 구조 확인) | `codex/e2.2-structure-bvsc-20260723` | Δ_BC=+0.32, NO_GO | 종료 |
| E2.2.1 (directed-PC 어휘 수정) | `codex/e2.2.1-directed-pc-vocab-fix-20260724` | rate=0.15, **NO_GO** | 종료 |
| E2.2.2 (directed-PC invariant 수정) | 〃 (같은 브랜치, 후속 커밋) | rate=1.00, **GO** | 종료 |
| E2.2.3 (OFAT ablation) | 〃 | A_ONLY=20/20, B_ONLY=1/20, C_ONLY=0/20 — **A_ONLY 단독 충분** | 종료 |
| E2.3 (전역 invariant 일반화) | 〃 (커밋 `157c021`) | A_ONLY/PARAPHRASE/TOPOLOGY/DECOY 전부 screened PASS | 종료, 푸시됨 |
| **E2.4 (repo-grounded contract)** | **`codex/e2.4-contract-repo-design`**(현재 브랜치, `157c021` 기반) | 아래 §4 | **진행 중** |

각 실험 폴더는 `experiments/<날짜>_<이름>/`에 있고, `README.md`(설계) +
`*_manifest.json`(동결된 프롬프트) + `trials.json`(결과) 3종 세트가
기본 패턴이다. 재현 규율: **동결 후 절대 프롬프트 수정 금지**, 수정하려면
새 커밋으로 명시적 amendment.

## 4. E2.4 — 지금 정확히 어디까지 왔는가

폴더: `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/`

**가설**: `evidence_contract_v1`(구조화 evidence-audit + sufficiency
판정 + repair/abstain 계약)을 쓰는 CONTRACT_REPO 조건이, 이 저장소 자체의
실제 코드/문서에서 추출한 evidence 위에서, legacy 3지선다 스키마보다
evidence 불충분/충돌을 더 잘 잡아내는지 검증한다. 3-arm: CONTROL_REPO
(legacy 프롬프트), A_REPO(legacy + 전역 invariant 규칙), CONTRACT_REPO.
4개 semantic class: `sufficient_consistent`(accept_report가 정답),
`sufficient_repairable`(repair), `insufficient`(abstain),
`conflicting`(abstain).

### 완료된 것

- 설계 패킷(`README.md`, `evidence_packet_schema.json`,
  `decision_schema.json`, `contract_prompt.md`) — 커밋 `d581d53`.
- 운영 계획(`OPERATIONS_PLAN.md`) — 커밋 `bf27cfa`, 이후 확장 `a10c9ad`.
- **`$schema` 스키마 버그 수정**: `decision_schema.json`의
  `evidence_contract_v1`에 최상위 `"$schema"` 키가 있으면
  `agent({schema})`가 전부 실패한다(`$defs`/`$ref`는 문제없음). 제거 후
  재실행 성공. 커밋 `a10c9ad`.
- **`sufficient_repairable`, `conflicting` fixture**: 스모크 테스트에서
  의도대로 동작 확인(각각 repair, abstain/conflicting_evidence).
- **문제 2 해결·검증 완료**: `insufficient` fixture에서 CONTRACT_REPO가
  "구현 필요성(implementation necessity)"을 온톨로지적 분류로 오인해
  `essential_feature`가 아닌 **다른** type(functional,
  structural_composition)으로 제멋대로 repair하는 결함을 발견. 첫
  수정(essential_feature만 배제)은 3trial 중 2trial이 실패 유형만 바꿔
  재현 — **좁은 수정은 실패를 다른 곳으로 옮길 뿐**이라는 교훈. 6개 type
  전부에 대해 "구현 서술은 어느 type의 direct_support도 아니다"로
  일반화한 뒤 5/5 재검증 통과. 커밋 `c2d0ce5`.

### 미해결 — 문제 1: `sufficient_consistent` fixture

정식 문제 정의서: `PROBLEM_1_sufficient_consistent.md`(아직 커밋 안 됨,
이 handoff와 같이 커밋됨).

**세 번의 시도가 전부 실패**, 매번 다른 이유:

1. **1차**(enum 정의 인용) — 독립 리뷰에서 실행 전 순환논리로 기각.
2. **2차**(`SemanticTypeInference.infer()`의 절차적 fallback 규칙) —
   실제 CONTRACT_REPO 실행에서 `insufficient_evidence`로 abstain.
   "일반 알고리즘이 어떻게 판단하는가"와 "이 특정 feature가 그 알고리즘을
   통해 실제로 이 type이 됐다"는 서술 사이 추론적 공백 때문.
3. **3차**(`RELATION_HINT_TYPE["component_of"]` 선언적 매핑 테이블) —
   독립 리뷰에서 기각, **더 나쁜 이유로**: 이 테이블 바로 위 docstring이
   "참조용 — concept_gate_v7.py에서 직접 import하지 않음"이라고 명시한다.
   즉 **죽은 참조용 코드**를 근거로 쓴 것이라 실사용 파이프라인과 무관.

**근본 원인**: 이 저장소의 코드/주석은 압도적으로 절차적(어떻게
판단하는가)이지 선언적(X는 Y다를 직접 단언)이 아니다. 유일하게 선언적인
`RELATION_HINT_TYPE`조차 죽은 코드였다.

**4차 시도 재료(찾았으나 아직 fixture로 안 만듦)**: `docs/MCP_SERVER.md`
93-109행 — **살아있는(server.py와 같은 커밋에서 갱신된) `run_pipeline`
MCP 도구의 실제 입력 형식 문서**. 워크드 예제
`{"name": "개", "features": [{"feature": "동물", "type":
"essential_feature", "evidence": "살아있는 생명체"}]}`가 있고,
`docs/LOCAL_INSTALL_GUIDE.md:148`이 같은 예제를 독립적으로 재확인한다.
또한 `conceptgate/server.py`의 `run_pipeline` 자체 docstring(354-386행)이
"essential_feature participates in the is-a DAG" 등 **6개 type의 온톨로지적
역할을 직접 명시**하며, 이건 실제로 노출된 `@mcp.tool`의 살아있는 계약
문서라 candidate B(죽은 테이블)와 근본적으로 다르다. **아직 fixture
JSON으로 조립하지 않았고, 독립 리뷰도 아직 안 거쳤다** — 다음 세션의
첫 작업.

## 5. 다음에 할 일 (순서대로)

1. `docs/MCP_SERVER.md` + `conceptgate/server.py` docstring 조합으로
   `fixture_sufficient_consistent.json` 4차 재구성 (excerpt+juxtapose,
   사용자 이미 승인된 방식).
2. **독립 리뷰**(fresh subagent, fixture 제작자와 무관) — 이번엔 특히
   "이 문서가 실제로 소비되는 경로인가"를 반드시 확인하게 할 것(3차 시도가
   이걸 놓쳐서 실패했음).
3. 리뷰 통과하면 스모크 테스트(N≥3~5, 문제 2와 동일한 재검증 강도로
   "정말 해결됐는지" 확인 — 1trial로 끝내지 말 것).
4. 4개 semantic class 전부 검증되면 `OPERATIONS_PLAN.md` Phase 3(설계
   동결) → Phase 4(manifest 생성) → Phase 5(N=10 Stage-1 screening,
   CONTRACT_REPO 4클래스 + CONTROL_REPO/A_REPO 2클래스 = 8 cell, 80
   trial) → Phase 6(채점) → Phase 7(결과 커밋, push는 명시적 승인 후).

## 6. 브랜치/PR 정리 — 마이그레이션 체크리스트

여러 브랜치에 완료된 작업이 쌓여 있고 아직 `main`으로 통합 안 됨. **이
worktree 세션은 실행하지 않는다** — 다음 세션 또는 사용자가 결정할 것:

| 브랜치 | 위치 | 상태 | 필요 조치 |
|---|---|---|---|
| `codex/e2.4-contract-repo-design` | 이 worktree | `main` 대비 42 커밋 앞섬(E2.2~E2.4 체인 전체 포함) | E2.4 완료 후 PR, 또는 체인 전체를 한 PR로 |
| `claude/ontoclean-gufo-handoff-7cmq0v` | 메인 저장소 체크아웃 | origin 대비 로컬 2 커밋 앞섬(로드맵+스크리닝 프로토콜 문서) | push 먼저, 이후 PR 여부 결정 |
| `codex/e2.1-haiku-results-20260723` | 별도 worktree(e2.1) | origin과 동기화됨 | 그대로 두거나 PR |
| `codex/e2.2-structure-bvsc-20260723` | — | origin과 동기화됨(NO_GO 종료) | 참고용, 통합 불필요 가능성 |

**중요**: `main`에는 `conceptgate/` 패키지 코드가 있고, 이 실험 브랜치들은
`experiments/`와 `docs/`만 건드린다 — 코드 충돌 위험은 낮지만, PR 순서는
날짜순(E2.2 → E2.2.1 → ... → E2.4)으로 하는 게 리뷰하기 쉽다.

## 7. 테스트 (메인 저장소에서, 코드 변경 시에만 필요 — 이 worktree는 코드 미변경)

```bash
venv/bin/python -m pytest -q                        # 86
venv/bin/python test_server.py                      # 73/73
venv/bin/python qa_v7.py                             # 101/101
venv/bin/python -m conceptgate.concept_gate_v7      # 60/60
venv/bin/python fuzz_normalizer_types.py             # 209, CRASH=0
```

## 8. 작업 스타일 (사용자 선호 — 중요)

- **좁은 수정 금지, 원칙 일반화**: 실패를 하나 막으면 그 실패가 다른
  곳으로 옮겨가지 않는지 재검증(문제 2가 정확한 예시).
- **"확인됐다"고 말하기 전에 실제로 N-trial 재실행**: 1trial 통과는
  검증이 아니다.
- **독립 리뷰는 fixture 제작자와 분리**(fresh subagent, hidden-oracle
  라벨 모름) — 실행 전 값싸게 결함을 잡는 1차 방어선.
- **커밋 규칙**: 매우 상세한 멀티라인. 실패한 시도와 그 실패 이유도
  커밋 메시지에 남긴다(이 저장소의 관행 — 나중에 같은 실수를 반복하지
  않기 위해서).
- push는 사용자가 명시적으로 요청했을 때만.
