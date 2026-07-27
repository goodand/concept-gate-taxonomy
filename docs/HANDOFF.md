# HANDOFF — ConceptGate 세션 인수인계 (E2 실험 체인)

- 갱신: 2026-07-27
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
E2.3(A_ONLY 일반화, screened PASS) → **E2.4(진행 중)**.

**E2.4의 현재 위치를 오해하지 마라**: 이 실험의 본 목적인 **3-arm 비교
(CONTROL_REPO vs A_REPO vs CONTRACT_REPO)는 아직 한 번도 실행되지 않았다.**
지금까지 끝난 것은 전부 **fixture 준비 단계**(Phase 0~3)다. 4개 semantic
class fixture를 실제 저장소 evidence로 만들고, 각각이 CONTRACT_REPO에서
의도한 판정을 내는지 검증하는 데 여러 세션이 소요됐다. 본 실험(Phase 4~6)이
다음 작업이다.

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
| **E2.4 (repo-grounded contract)** | fixture 4종 준비 완료, **본 실험 미실행** | **진행 중** |

## 4. E2.4 — fixture 4종 검증 현황

폴더: `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/`

가설: `evidence_contract_v1`(구조화 evidence-audit + sufficiency 판정 +
repair/abstain 계약)을 쓰는 CONTRACT_REPO가, 이 저장소 자체의 실제
코드/문서에서 추출한 evidence 위에서, legacy 3지선다 스키마보다 evidence
불충분/충돌을 더 잘 잡아내는지.

| class | 정답 | fixture 내용 | 검증 수준 |
|---|---|---|---|
| `sufficient_consistent` | accept_report | `카페린`/`손잡이`=structural_composition (E2.3 fixture 텍스트 + server.py docstring) | **7/7** ✅ |
| `sufficient_repairable` | repair | `돌체`/`바퀴`=essential_feature인데 evidence는 "구성 부분"이라 명시 (E2.2 동결 텍스트) | **5/5** ✅ |
| `insufficient` | abstain | `JSON추출유틸` — 설명 없는 유틸 함수 본문 | **5/5** ✅ |
| `conflicting` | abstain | E2.2.1/E2.2.2 커밋 메시지 충돌 쌍 | **1/1** ⚠️ **재검증 필요** |

### ⚠️ 최우선 미결: `conflicting`은 N=1로만 검증됐다

이건 이번 세션에 승격한 교훈이 그대로 적용되는 대상이다. `sufficient_repairable`도
초기에 **N=1 스모크 1회 통과로 "해결됨" 표시**됐다가, 나중에 강화된 기준
(instance-binding, self-citation 금지, N=5 하한)으로 재검사했더니 **실제 결함이
발견돼 두 번 재구축**해야 했다. `conflicting`은 같은 시기 같은 N=1 스모크에서
통과 표시된 뒤 한 번도 재검증되지 않았다.

추가로 `conflicting` fixture에는 이미 알려진 약점이 있다: 독립 리뷰가
"ev5/ev6의 충돌은 **인과관계 서술의 충돌**이지 **FeatureType 온톨로지 분류의
충돌**이 아니다"라고 지적했고, 이에 따라 기대 오라클이
"abstain(사유 불문 — insufficient/conflicting/out_of_scope 아무거나)"으로
**완화된 채로** 남아 있다. 즉 이 fixture는 `conflicting_evidence`라는 특정
판정을 검증하지 못한다.

→ **다음 세션 첫 작업**: §6 H1 참조.

## 5. 이번 세션(2026-07-27)에 한 일

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

### H1 — `conflicting` 재검증 (최우선, 저비용)

- **가설**: 현재 `conflicting` fixture는 N=5에서도 abstain을 안정적으로
  내는가? 그리고 `contract_verdict`가 실제로 `conflicting_evidence`로
  나오는가, 아니면 `insufficient_evidence`로 나오는가?
- **왜**: N=1 인증 + 완화된 오라클 + 강화된 기준 미적용 — `sufficient_repairable`이
  똑같은 조건에서 실제로 실패했던 전례가 있다.
- **방법**: 기존 3개 class와 동일 — 독립 리뷰(fresh non-fork agent) → N=5 스모크.
- **분기**: `conflicting_evidence`가 안 나오면, "온톨로지 분류의 충돌"을
  실제로 담는 evidence 쌍을 새로 찾아야 한다(현재 것은 서사적 충돌).
  이 저장소에서 그런 쌍이 존재하는지 자체가 불확실 — 없으면 class 재정의
  논의 필요(설계급 사안 → 사용자/설계 전문 agent에 에스컬레이션).

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

### H3 — E2.4 본 실험 (Phase 4~6, 이 실험의 실제 목적)

- **가설**(README.md 원문): CONTRACT_REPO가 CONTROL_REPO/A_REPO보다 evidence
  불충분·충돌을 더 잘 잡아낸다.
- **현재까지의 유일한 arm 비교 실측**(1회, 초기 스모크): `conflicting`
  fixture에서 CONTROL_REPO/A_REPO는 **둘 다 abstain 없이 스스로 "ev6가 ev5를
  대체"라 판단하고 조용히 repair**했고, CONTRACT_REPO만 두 근거를 `conflict`로
  분류하고 정확히 abstain했다. 가설을 뒷받침하는 첫 신호이나 N=1이다.
- **규모**: 8 cell × N=10 = 80 trial (CONTRACT_REPO 4 class + CONTROL_REPO/
  A_REPO 각 2 class). `OPERATIONS_PLAN.md` Phase 5 참조.
- **선행 작업**: Phase 4의 `_gen_prompts.py`(매니페스트 생성 스크립트)가
  **아직 존재하지 않는다** — CONTROL_REPO/A_REPO용 legacy 프롬프트 템플릿을
  새로 작성해야 한다. 이건 엔지니어링 작업이라 별도 스코핑 필요.
- **도구**: 사용자가 `Workflow`(dynamic workflow) 사용을 승인했다. 80 trial
  규모에서는 resumability(`runId` 캐시)와 토큰 예산 추적 이점이 실재한다.
  다만 매니페스트를 먼저 보여주고 진행하는 게 이 프로젝트 관례
  ("qualify before scale").

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

`goodand/skills-catalog`의
`skills/Skills-Create-Project/` 아래 두 skill에 성격을 나눠 반영했다.
**새 세션에서 유사 작업을 시작하기 전에 두 파일의 최신 타임스탬프 버전을
읽어라.**

- **`evidence-to-knowledge-promoter/references/recurring-agentic-failure-modes-lessons-at2026-07-27-16-11.md`**
  (update 8) — 서사·재발 이력·promotion 등급. 신규 lesson 5개:
  instance-binding 비전이(4/4), self-citation 4회 재발(고치면 다른 위치에서
  재발 → 기계적 체크 필요), 차단 조건의 decision-type 의존성, 프롬프트 드리프트
  (frozen 파일 미반영 시 재현 불가), 기준 강화 시 기존 인증 재검증.
  candidate 4개: extraction_note 메타 서술 오염, 결정론 게이트 우회가 의미
  레이어에 만든 새 실패, 평가 목표 교체 전략, review 전용 agent에 write 권한
  주지 말 것.
- **`evidence-trace-auditor/references/cited-source-text-evidence-rules-at2026-07-27-16-15.md`**
  — 기계적 판정 절차. evidence가 "저장소 텍스트 인용" 형태일 때의 4개
  **독립** 체크(C1 liveness / C2 instance-binding / C3 non-circularity /
  C4 precedence)와 결합 상태 규칙. `SKILL.md` References + 허브
  `evidence-status-rules` Notes에 상호 연결 완료.

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
- 최신 커밋: `6bbd704` (E2.4 sufficient_repairable 해결 + 정리 항목 반영), 푸시됨.

## 9. 검증 명령

```bash
# 이 worktree에서 (E2.4 fixture 무결성 — 구조/해시/서버응답 재현/repair 전후 상태)
python3 -m pytest -q experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/test_protocol.py   # 4 passed

# conceptgate/ 코드를 건드렸을 때만 (메인 저장소 venv 필요)
venv/bin/python -m pytest -q                    # 86
venv/bin/python test_server.py                  # 73/73  ※ 이 worktree엔 fastmcp 미설치라 실패함(환경 이슈)
venv/bin/python qa_v7.py                        # 101/101
venv/bin/python -m conceptgate.concept_gate_v7  # 60/60
venv/bin/python fuzz_normalizer_types.py        # 209, CRASH=0
python3 -m pytest -q test_semantic_regressions.py  # 8 (R6/R6b 포함)
```
