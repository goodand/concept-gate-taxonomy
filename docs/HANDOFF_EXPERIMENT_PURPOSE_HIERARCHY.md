---
aliases:
  - Handoff Experiment Purpose Hierarchy
  - 실험 목적 계층
tags:
  - doc/concept
  - stage/handoff
---

# 실험 목적 계층 — dynamic workflow controller가 무엇의 특수화인가

현재 진행 중인 실험의 목적은 3단계로 올라간다. **다만 문서가 이 관계를 OWL
클래스처럼 형식적으로 선언한 것은 아니다.** 아래 계층은 사전등록과 상위 표준에
나타난 관계를 `is-a` / `part-of` / `depends-on`으로 구분해 **재구성**한 것이다.
이 문서는 판정 권위가 아니라 개념 지도이며, 인용된 원문이 권위다.

```
신뢰할 수 있는 증거 기반 Agent 연속성
  └─ evaluated-by → Cold-start Handoff Reuse Validation
       └─ instantiated-by → Handoff Reuse Harness
            └─ specialized-by → Dynamic Workflow Controller Experiment
```

## 1. 직접 목적

> 무맥락 agent가 handoff를 찾고 읽는 과정에서, 고정된 검색 절차보다 검색 행동을
> 동적으로 선택하는 controller가 더 높은 회수율과 안전한 답변을 만드는가?

두 요인을 분리한 **2×2 실험**이다.

- 검색 전용 subagent 유무: `S_*` 대 `R_*`
- 검색 행동 controller 유형: `*_STATIC` 대 `*_DYNAMIC`

Dynamic controller가 고르는 행동은 닫힌 여섯 개다: `reformulate_query`,
`follow_link`, `read_candidate`, `expand_candidates`, `abstain`, `answer`
(`PREREGISTRATION.md:88-93`, §4 — 그 밖의 action은 `C2`이며 run을 종료한다).

측정 대상은 단순 Recall만이 아니다. full hard-gate rate, critical path Recall,
exact authority hit, critical claim/range exposure rate,
state·next-action·stop-condition accuracy, false absence rate, safety violation
rate, arm별 `V1` invalid-run rate, action별 incremental recall gain까지 포함한다.
근거: [`PREREGISTRATION.md:146-157`](../experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md) §7 지표.

`V1` invalid-run rate는 **부수 지표가 아니라 타당성 조건**이라고 같은 절
(`:156`)이 명시한다.

즉 이 실험은 다음 개념의 특수화다.

```
DynamicWorkflowControllerExperiment
    is-a          ControlledRetrievalExperiment
    evaluates     ControllerPolicy
    compares      StaticPolicy vs DynamicPolicy
    optionally-has RetrievalOnlySubagent
```

## 2. 상위 목적 — handoff의 실제 재사용 가능성

> 이전 대화를 모르는 새 agent가 필요한 원본을 찾아서, 권위를 구분하고, 현재
> 상태와 안전한 다음 행동을 재구성할 수 있는가?

상위 표준이 이 문제를 **네 계층**으로 분해한다
(`.vault-harness/vault-md-retrieval/HANDOFF_REUSE_HARNESS_PREREGISTRATION.md:32-37`):

1. **StructuralReachability** — entry point에서 필요한 파일로 갈 수 있는가
2. **EvidenceRetrieval** — 제한된 budget 안에서 필요한 source와 range를 찾는가
3. **GroundedContinuation** — 상태·blocker·다음 행동·금지 행동을 재구성하는가
4. **EvaluationIntegrity** — agent가 judge·gold·input set을 게임할 수 없는가

**이 넷은 상속 관계가 아니라 필요 구성요소, 즉 `part-of` 관계다.**

```
HandoffReuseSuccess
    has-part StructuralReachability
    has-part EvidenceRetrieval
    has-part GroundedContinuation
    has-part EvaluationIntegrity
```

StructuralReachability가 통과했다고 GroundedContinuation도 통과하는 것은 아니다.
파일을 찾았지만 잘못 해석할 수 있고, 답이 맞더라도 gold가 노출된 결과일 수 있다.
원문이 같은 판단을 직접 적고 있다 — **"하나의 pass/fail로 네 계층을 합치지
않는다. 앞 계층의 통과는 뒤 계층의 통과를 뜻하지 않는다"**
(같은 문서 `:39-40`). 즉 이 `part-of` 재구성은 해석이 아니라 원문 문장의 형식화다.

## 3. 상위 목적의 상위 목적 — 증거 기반 Agent 작업 환경

> LLM의 기억이나 이전 transcript에 의존하지 않고, canonical source와 검증 가능한
> trace를 통해 새로운 agent가 기존 작업을 안전하게 이어갈 수 있게 한다.

이것은 ConceptGate 프로젝트가 채택했던 원칙의 **agent-workflow 버전**이다.

> **"LLM이 제안하고, 결정론이 판정한다."**
> — `archive/worktrees/concept-gate-e2.1-wt/docs/HANDOFF.md:22-26` §2 프로젝트 목적.
> 원문: 자연어를 evidence-carrying 개념으로 고정한 뒤 is-a 계층은 풀 OWL 2 DL
> reasoner(HermiT)가 생성하며, LLM의 is-a 환각을 "제안 vs 판정" 분리로 차단한다.

같은 원칙이 이렇게 변환됐다.

| | 제안 | 고정 형식 | 판정 |
|---|---|---|---|
| 기존 ConceptGate | LLM 제안 | evidence-carrying **concept** | deterministic **reasoner** |
| 현재 Handoff Harness | Agent 탐색·해석 | evidence-carrying **trace** | deterministic **evaluator** |

따라서 가장 높은 개념적 부모는 다음과 같다.

```
EvidenceGroundedAgentSystem
    inherits principle from
        ProposalJudgmentSeparation
        SourceAuthority
        EvidenceProvenance
        DeterministicVerification
```

## 4. 개념 종속 관계

| 현재 개념 | 상위 개념 | 관계 |
|---|---|---|
| `DynamicController` | `ControllerPolicy` | is-a |
| `StaticController` | `ControllerPolicy` | is-a |
| `RetrievalOnlySubagent` | `EvidenceRetriever` | is-a |
| `MainSubject` | `GroundedContinuationAgent` | is-a |
| `HandoffReuseHarness` | `AgentEvaluationHarness` | is-a |
| `DynamicControllerExperiment` | `ControlledFactorialExperiment` | is-a |
| `Discovery` | `HandoffReuseSuccess` | part-of |
| `Exposure` | `HandoffReuseSuccess` | part-of |
| `Interpretation` | `HandoffReuseSuccess` | part-of |
| `SafeContinuation` | `HandoffReuseSuccess` | part-of |
| `BudgetGuard` | `ControllerPolicy` | constrains |
| `TraceContract` | `EvaluationIntegrity` | supports |
| `SourceAuthority` | `EvidenceProvenance` | is-a에 가까운 특수화 |
| MOC, backlink, tag | `NavigationArtifact` | is-a |
| `NavigationArtifact` | `SourceAuthority` | **상속 관계 아님** |
| `ProtocolQualification` | `MeasurementReadiness` | is-a |
| `RetrievalPerformance` | `TaskPerformance` | is-a |
| `ProtocolQualification` | `RetrievalPerformance` | **상속 관계 아님** |

### 마지막 두 줄이 특히 중요하다

지금까지 통과한 Codex v7·Claude surface v2 qualification은 **측정 도구와 실행
경로가 작동한다**는 readiness 개념이다. 이것은 retrieval 성능이나 dynamic
controller 효과의 하위 개념이 **아니며, 성능 증거로 상속시킬 수 없다.**

이 구분은 문서 규율이 아니라 **기계 필드**로 강제돼 있다 — 두 qualification
artifact가 `arm_effect_estimable=false`, `n_per_cell=1`을 들고 있고, host-action
미준수는 outcome failure와 분리된 `C5` execution code로 기록된다
([[docs/feedback/claude_redteam_preprimary_reaudit_20260807|재감사]] A9).
실물 사례도 있다: Claude v2 `R_STATIC`은 `invalid_run=false`·exposure 1.0으로
**프로토콜은 정상**이지만 authority read에 닿지 못해 critical recall 0이다
(`discovery incomplete / trace valid`).

`NavigationArtifact`가 `SourceAuthority`를 상속하지 않는다는 줄도 같은 성격이다
— MOC·backlink·tag는 탐색용이며, 이 저장소의 검색 규율(`CLAUDE.md`)과 MOC 자신의
Rules 절이 그렇게 못박는다.

## 가장 정확한 한 문장

> **"LLM은 탐색 행동과 해석을 제안하고, host-owned trace와 hidden deterministic
> judge가 근거·권위·안전성을 판정한다"는 상위 원칙을, 무맥락 handoff 재사용
> 문제에 적용한 2×2 검색-controller 실험이다.**

계보:

```
제안과 판정의 분리
  → 증거 기반 Agent 시스템
    → 안전한 cross-session continuation
      → cold-start handoff reuse 평가
        → retrieval/interpretation 분리
          → static/dynamic controller × retrieval subagent 실험
```

## 인용 원문 (권위 순서)

1. `experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION.md`
   — §4 action 집합 `:88-93`, §7 지표 `:146-157`
2. `.vault-harness/vault-md-retrieval/HANDOFF_REUSE_HARNESS_PREREGISTRATION.md`
   — §0 문제 추상화와 네 계층 `:32-40` (읽기 전용 dirty worktree)
3. `archive/worktrees/concept-gate-e2.1-wt/docs/HANDOFF.md`
   — §2 프로젝트 목적 `:22-26` (읽기 전용 아카이브)

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/PREREGISTRATION|Phase C 사전등록]]
- [[experiments/2026-08-07_handoff_dynamic_controller/PROVIDER_ADAPTERS|Provider adapters]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 재감사]]
- [[docs/feedback/session_synthesis_20260807_empty_guard_and_authorization_chain|공허한 가드·승인 우회 종합]]
- [[docs/EXPERIMENT_METHODOLOGY|실험 방법론]]
