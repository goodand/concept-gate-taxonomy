# 실험 방법론 — 이 workspace의 기록 패턴

- 대상: `experiments/`에 새 실험을 설계·실행하는 모든 세션(메인 저장소 +
  `concept-gate-e2.*-wt` worktree 전부 포함).
- 핵심 원칙: **검증 안 된 것을 검증된 것과 못 섞이게, 계층을 물리적으로
  분리한다.** 아래 7개 규칙은 전부 이 원칙 하나에서 파생된다 — 새 규칙이
  필요하면 먼저 이 원칙에 비춰 판단할 것.

한 줄 요약: **동결로 잠그고, 운영은 따로 로그하고, 계약으로 검증하고,
worktree로 격리하고, 교훈은 승격한다.**

## 1. 2계층 분리 — 동결(pre-registration) vs 운영 로그

실험의 "설계"와 "그 설계를 실행하며 생긴 기록"은 절대 같은 커밋에 섞지
않는다. 결과가 설계를 소급 수정하지 못하게 하는 게 목적이다.

커밋 순서(각각 독립 커밋):
1. **설계 freeze** — 가설, arm, fixture 설계를 확정하고 커밋 (예:
   `experiment(e2.3): preregister global feature-type invariant
   generalization (freeze)`, 커밋 `4e1c53d`).
2. **manifest freeze** — 실제 실행할 프롬프트를 동결하고 커밋. **동결 후
   프롬프트 내용을 수정하지 않는다** — 수정이 필요하면 새 amendment
   커밋으로 명시(예: `experiment(e2.3): amend CONTROL replicate 10->2
   before Stage 1 execution (cost)`, 커밋 `ea4767d` — CONTROL 증분을
   줄인 정당한 사전 amendment 사례, "실행 전" + "이미 예측된 방향"이라는
   두 조건을 만족했기 때문에 p-hacking이 아니었다).
3. **results** — 원시 trial 결과(`trials.json`)를 있는 그대로 커밋.
   채점/해석은 여기 섞지 않는다.
4. **ops-docs** — `OPERATIONS_LOG.md`/`HANDOFF.md` 같은 운영 기록은 별도
   커밋. 결과 해석·다음 단계 판단이 여기 들어간다.

## 2. 실험 폴더 규약 — `experiments/<날짜>_<slug>/`

관찰된 표준 파일 세트(예: `experiments/2026-07-25_e2.2.3_directed_pc_ablation/`):

| 파일 | 역할 |
|---|---|
| `README.md` | 사전등록(가설, arm, N, threshold) |
| `fixture.json` | 실험 재료(입력 개념/증거) |
| `_gen_prompts.py` | manifest 생성 스크립트 |
| `_prompts.json` | 동결된 프롬프트 manifest (동결 이후 불변) |
| `evaluate.py` | **결정론적 채점기** — §3의 provenance 계약을 검사하고,
  안 맞으면 채점을 거부한다 |
| `test_protocol.py` | 프로토콜 자체의 자기검증(설계 문서와 코드가
  일치하는지) |
| `trials.json` | 원시 실행 결과 |
| `OPERATIONS_LOG.md` / `HANDOFF.md` | 운영 기록 — **별도 커밋** |

폴더명의 `<날짜>`는 설계 freeze 시점, `<slug>`는 실험을 한눈에 식별할
수 있는 이름(예: `directed_pc_ablation`, `global_invariant_generalization`).

## 3. Provenance 계약 — 채점기가 계약 위반이면 거부한다

`evaluate.py`는 다음을 실제로 검사한다(예:
`experiments/2026-07-25_e2.2.3_directed_pc_ablation/evaluate.py`):

- `design_commit`이 `trials.json`과 manifest 양쪽에서 일치하는가
  (`protocol.get("design_commit") != manifest["protocol"]["design_commit"]`
  이면 실패).
- 각 trial의 `prompt_sha256`이 manifest에 기록된 값과 일치하는가(다르면
  그 trial은 다른 프롬프트로 실행된 것 — 오염된 데이터).
- `validate_trial_set()`이 전체 provenance 오류를 모아 하나라도 있으면
  `PROVENANCE_FAIL`로 **채점 자체를 중단**한다. 통과해야만
  `EMPIRICAL_TRIAL_SET: provenance contract satisfied`를 출력하고 점수를
  낸다.

**계약이 깨지면 숫자를 믿지 않는다** — "그래도 대충 맞겠지"로 채점을
강행하지 않는다는 게 이 규칙의 핵심.

## 4. git worktree 격리

실험마다(또는 실험 계열마다) 브랜치+worktree를 분리해 `main`과 물리적으로
떨어뜨린다. 현재 이 원칙에 따른 worktree들:

```
concept-gate-taxonomy    claude/ontoclean-gufo-handoff-7cmq0v  (메인 저장소 자체)
concept-gate-e2.1-wt     codex/e2.1-haiku-results-20260723
concept-gate-e2.2-wt     codex/e2.4-contract-repo-design       (E2.2~E2.4 체인)
```
(`git worktree list`로 항상 실제 상태 재확인 — 위 표는 스냅샷이다.)

이유: 실험 중 실수로 `main`이나 다른 실험에 영향을 주는 걸 구조적으로
차단한다. 새 실험 계열을 시작할 때는 새 worktree를 만들지, 기존
worktree에 무관한 실험을 얹지 않는다.

## 5. 비-git 로컬 감사본

일부 기록은 **의도적으로 저장소에 넣지 않는다** — `Project_in_progress/`
바로 아래(모든 worktree의 부모 디렉터리)에 둔다:

- `Project_in_progress/e2.1-execution-audit/` — 실행 감사 기록
- `Project_in_progress/benchmark-references.md` — grep으로 직접 만든
  참조 색인(외부에서 받아온 미검증 요약과 구분하려고 별도 관리 — 참고:
  `docs/relation_backend_tool_survey.md`는 반대로 "이 세션이 직접
  검증하지 않은 외부 인용"이라고 스스로 명시하는 문서다. 이 둘을
  섞지 않는 게 이 규칙의 요점).

이 파일들은 repo 커밋 대상이 아니다 — 여러 worktree/실험을 가로지르는
개인 작업 기록이라 특정 브랜치에 속하지 않기 때문.

## 6. 교훈 승격 — skills-catalog로

반복되는(≥2회 확인된) 이슈나 노하우는
`goodand/skills-catalog`의
`skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/`로
승격한다. 미검증(1회성) 항목은 `candidate`로 hold, 반복 확인되면
`lesson`으로 promote — 파일명에 타임스탬프를 붙여 누적 재서술
(`recurring-agentic-failure-modes-lessons-at<timestamp>.md`,
`dynamic-workflow-experiment-design-knowhow-at<timestamp>.md`). 기존
파일을 덮어쓰지 않고 새 타임스탬프 버전을 추가하는 게 컨벤션이다.

## 7. 독립 재현 검증

보고된 숫자(trial 결과 요약, "N/N 통과" 같은 주장)를 그대로 믿지 않고,
**`evaluate.py`를 직접 재실행**해서 같은 숫자가 나오는지 재현 확인한다.
로그나 요약 텍스트가 아니라 실제 관측 경계(코드 실행 결과)에서 확인하는
것 — `docs/HANDOFF.md`(worktree판) §8에 적힌 "확인됐다고 말하기 전에
실제로 N-trial 재실행"과 같은 원칙의 연장.

## 8. 공통 지시문 감사 (D-OWL-1 §4.2 반영, 2026-08-05)

행동 실험(모델에게 판단을 시키고 그 분포를 재는 실험) 사전등록에 **의무**로
추가한다 — 문자열 검색이 아니라 문장별 정책 효과 분석이어야 한다.

```yaml
common_instruction_audit:
  target_behavior: required          # 무엇을 재려는가, 정확히
  target_mechanism: required          # 어떤 경로로 그 행동이 나오는가
  common_prompt_sentences_reviewed: required   # 모든 arm 공통 문장 전수
  direct_prohibition_found: true_or_false
  semantic_equivalent_prohibition_found: true_or_false   # 직접 문장이
    # 없어도 같은 효과를 내는 다른 표현이 있는가
  licensed_path_exists_per_arm: required   # 표적 행동이 실제로 발현될
    # 여지가 arm마다 있는가(구조상 항상 봉쇄돼 있지 않은가)
  independent_reviewer: required
```

**왜 필요한가**: 같은 실패 형태(공통 문장이 표적 행동 자체를 봉쇄해
arm 대비가 무의미해짐)가 이 workspace에서 **최소 3회** 나왔다 — H1a
D-H1a-10(잔여 liveness 금지), H1a D-H1a-12(`outside_domain_knowledge`가
표적 축을 포섭), OWL D-OWL-1(E-B의 anti-laundering 문장이 양 arm 공통).
세 번째 재발이 곧 이 항목을 신설한 계기다.

이 감사는 사전등록 단계(trial 실행 전)에 완료해야 하고, 결과를 본 뒤
소급 적용하는 것은 이 문서 §1의 원칙(결과가 설계를 소급 수정하지 못하게
한다)을 어긴다.

## 참고

- 각 규칙의 실제 사례는 `experiments/` 아래 각 폴더의 커밋 히스토리에서
  확인 가능(`git log --oneline -- experiments/<폴더>/`).
- Workflow 도구(`agent()`/`pipeline()`) 실행 메커니즘 자체의 노하우는
  이 문서가 아니라 skills-catalog의
  `dynamic-workflow-experiment-design-knowhow-at*.md`를 참조 — 이 문서는
  "무엇을 왜 분리하는가"이고, 그 문서는 "Workflow 도구를 어떻게
  돌리는가"라 성격이 다르다.
