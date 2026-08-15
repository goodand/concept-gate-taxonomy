# WORKSPACE NAVIGATION — 무엇이 어디 있고, 어떻게 찾는가

- 갱신: 2026-07-27
- 대상: 컨텍스트 없이 시작한 세션이 **파일을 찾고, 그 파일을 얼마나 믿을지
  판단**하기 위한 문서. "지금 무슨 작업 중인가"는 [`HANDOFF.md`](HANDOFF.md),
  "실험을 어떻게 설계·기록하는가"는
  `docs/EXPERIMENT_METHODOLOGY.md`.

---

## 0. 먼저 알아야 할 함정 4개

이 workspace에서 새 세션이 실제로 반복해서 빠진 함정들이다. 탐색을 시작하기
전에 읽어라.

1. **`docs/HANDOFF.md`가 두 개 있다.** 메인 체크아웃
   (`concept-gate-taxonomy`)의 것과 이 worktree의 것은 **다른 문서**다.
   메인 쪽은 OWL/gUFO 동치 보고 작업(2026-07-17)의 기록이고, "지금 뭘 하고
   있는가"의 답이 아니다. **활성 작업의 상태는 항상 그 작업이 진행 중인
   worktree의 HANDOFF.md**다.
2. **주석·docstring의 자기서술을 믿지 마라.** `cg_partwhole.py`의
   `RELATION_HINT_TYPE` 위 docstring은 "참조용 — 직접 import하지 않음"이라고
   적혀 있지만 **거짓(stale)**이다. 실제로는 두 모듈이 import해 라이브 경로에서
   쓴다. 이 잘못된 자기서술 하나 때문에 fixture 하나가 잘못 기각됐고, 그
   판정이 외부 skills-catalog의 lesson으로까지 승격됐다가 나중에 정정됐다.
   → §4의 liveness 확인 절차를 쓸 것.
3. **문서의 "해결됨/완료" 표시는 과거 시점의 평가지 파일의 속성이 아니다.**
   `sufficient_repairable`은 "해결됨"으로 표시된 채로 실제로는 결함이 있었다
   (N=1 인증 후 기준이 강화됐는데 재검사가 안 됨). 인증 문구를 보면 **언제,
   어떤 기준으로** 인증됐는지 함께 확인하라.

4. **검색이 조용한 것은 "없다"가 아니라 "이 어휘로는 못 찾았다"이다.**
   결정 문서의 제목이 네 질문의 어휘를 **하나도** 포함하지 않을 수 있다.
   2026-08-01 실측: 활성 실험 폴더 정리를 설계하면서 `rg`로 "디렉토리 정리 /
   DESIGN_DECISION / canonical"을 훑었으나, 이미 채택된 결정
   (`notes/audits/vault/symlink-vs-moc-2026-07-30.md`, `status: finished`,
   **"Keep repository and active experiment paths unchanged"**)이 걸리지
   않았다 — 그 문서 제목이 "Format storage, symlink views, and MOC
   validation"이라 교집합이 0이었다. **backlink 1홉**으로 나왔고, 그 사이
   작성된 설계 문서는 채택된 결정과 **정면으로 충돌**했다.
   같은 세션에서 **두 번** 걸렸다(두 번째는 skills-catalog를 "0건"이라
   단정했다가 전수 조사에서 PARTIAL로 정정). → §4.0의 graph 절차를 쓸 것.

## 1. Layer 0 — 물리적 위치 (어느 저장소/worktree인가)

```
Project_in_progress/
├── concept-gate-taxonomy/            메인 체크아웃 (claude/ontoclean-gufo-handoff-7cmq0v)
│   └── docs/EXPERIMENT_METHODOLOGY.md   ← 실험 방법론 7규칙 (2026-08-01 병합으로 worktree에도 있음)
├── concept-gate-h1-wt/               ★ H 계열: source authority (codex/h1-source-authority)
├── concept-gate-e2.2-wt/             E2.2~E2.4 체인 — 종료 (codex/e2.4-contract-repo-design)
├── .vault-harness/vault-md-retrieval/   검색 하네스 — AGENT_PROMPT.md에 절차 전문
├── notes/                            Obsidian vault (00-moc = 생성된 MOC facet)
├── archive/worktrees/                E2.1·publish-vault — read-only 역사 증거
├── e2.1-execution-audit/             비-git 감사 기록 (의도적으로 커밋 안 함)
└── benchmark-references.md           비-git 참조 색인
```

- 항상 `git worktree list`로 실제 상태를 재확인하라. 위 표는 스냅샷이다.
- **비-git 자료가 존재한다**: `Project_in_progress/` 바로 아래의 감사 기록과
  참조 색인은 저장소에 없다. 여러 worktree를 가로지르는 개인 기록이라
  특정 브랜치에 속하지 않기 때문(방법론 규칙 5).
- **외부 저장소**: `goodand/skills-catalog` — 승격된 교훈/노하우.
  로컬 체크아웃 없이 `gh api`로 읽고 쓴다(§5.4).

## 2. Layer 1 — 문서 종류 분류 체계

파일을 열기 전에 **어떤 종류인지** 먼저 분류하라. 종류에 따라 신뢰도와
수정 가능 여부가 다르다.

| 종류 | 위치 패턴 | 성격 | 수정 규칙 |
|---|---|---|---|
| **정본 코드** | `conceptgate/*.py` | 실행되는 유일한 소스 | 실험 세션에서는 read-only |
| **테스트** | 루트의 `test_*.py`, `qa_v7.py`, `fuzz_*.py` | 동작 계약의 실행 가능한 명세. **evidence 소스로 인용 가능** | 코드 변경 시에만 |
| **설계 동결(frozen)** | `experiments/<날짜>_<slug>/README.md`, `fixture*.json`, `_prompts.json`, `*_schema.json`, `contract_prompt.md` | 사전등록된 설계. 결과가 설계를 소급 수정하지 못하게 하는 게 목적 | **동결 후 수정 금지** — 수정하려면 명시적 amendment 커밋 |
| **원시 결과** | `experiments/<...>/trials.json` | 실행 결과 원문 | 있는 그대로, 채점/해석 섞지 않음 |
| **채점기** | `experiments/<...>/evaluate.py` | 결정론적 채점 + provenance 계약 검사 | 실험별 |
| **프로토콜 자기검증** | `experiments/<...>/test_protocol.py` | fixture 무결성(구조/해시/재현성) | 실험별 |
| **운영 로그** | `OPERATIONS_PLAN.md`, `PROBLEM_*.md`, `HANDOFF.md` | 진행 상황·판단·미결 사항. **별도 커밋** | 계속 갱신 |
| **외부 설계 판정** | `experiments/<...>/DESIGN_DECISION*.md` (평면) | 외부 판정자의 회신. **구속력 있음**, 사전등록만큼 무겁다 | **원문 보존 — 수정 금지.** 판정이 바뀌면 새 요청→새 판정 파일 |
| **외부 설계 요청** | `experiments/<...>/correspondence/DESIGN_REQUEST*.md` | 운영 세션이 외부 판정자에게 보내는 자기완결형 질의서(저장소 접근 없이 판정 가능하게 원문·실측 embed) | 발송 전 인용 대조(citation-check) 필수. 발송 후엔 원문 보존 |
| **설계 문서** | `docs/*.md`(실험 폴더 밖) | 아키텍처/로드맵/스펙 | 해당 작업 시 |
| **세션 회고 / 프로세스 패턴** | **`../notes/projects/concept-gate/process/`**(vault, worktree 밖) | 에이전트 작업 과정의 결함과 반복 패턴. **실험 이슈가 아니다** | 신규는 vault에 쓴다 — 아래 경고 참조 |
| **승격된 교훈** | 외부 `skills-catalog/.../references/*-at<ts>.md` | 재사용 가능한 노하우 | 덮어쓰지 않고 새 타임스탬프 추가 |

> **⚠️ 세션 회고를 `docs/feedback/`에 새로 쓰지 마라(2026-08-15 규약 변경).**
> 그 경로는 git-tracked라 **브랜치별로 격리된다** — 실측: `codex-mcp-wt`에
> 회고 8개가 있는데 `h1-wt`에서는 2개만 보였고, 그래서 이슈 ID 최댓값을 git이
> 아니라 파일시스템 전수 검색으로 찾아야 했다(`I29`인 줄 알았으나 실제
> `I147`). 회고는 동결 규율 대상이 아닌 **프로세스 지식**이므로 브랜치에 묶일
> 이유가 없다. 정본 위치와 ID 채번 규약:
> `../notes/projects/concept-gate/process/retrospectives-index.md`,
> 패턴 누적값 정본: 같은 폴더 `patterns-ledger.md`.
> **기존 `docs/feedback/*.md`는 그대로 둔다**(git 이력이고 여러 문서가 인용).

**핵심 구분**: 동결 아티팩트(설계)와 운영 로그(그 설계를 실행하며 생긴 기록)는
**절대 같은 커밋에 섞지 않는다**. 이게 방법론 규칙 1이고, 커밋 히스토리를
읽을 때도 이 구분으로 읽어야 한다.

## 3. Layer 2 — 파일명 읽는 법

| 패턴 | 의미 |
|---|---|
| `experiments/2026-07-25_e2.4_<slug>/` | 날짜 = **설계 freeze 시점**(실행 시점 아님), slug = 실험 식별자 |
| `_`로 시작하는 파일 (`_cert_core.py`, `_gen_prompts.py`, `_prompts.json`) | 헬퍼/생성물. `_cert_core.py`는 실험 간 **byte-identical 복사본**(드리프트 방지용, 원본 수정 금지) |
| `fixture_<class>.json` | E2.4식 — semantic class 하나당 파일 하나 |
| `fixture.json` (단수) | E2.2/E2.3식 — 한 파일에 `fixtures[]` 배열 |
| `PROBLEM_<n>_<slug>.md` | 정식 문제 정의서. 시도-실패 이력이 누적됨 |
| `*-at2026-07-28-14-02.md` | skills-catalog 컨벤션. **타임스탬프가 클수록 최신**, 이전 버전을 supersede하지만 파일은 남김. supersede는 "더 많아짐"이 아니라 **"앞의 것이 틀렸을 수 있음"** 을 포함한다 — 07-28 판 3건이 각각 이전 판의 지침을 정정했다 |
| `__pycache__/` | 무시 |

**⚠️ 외부 설계 판정문 중 하나가 코드 입력일 수 있다 — 확인 없이 "전부
순수 기록"이라 가정하지 마라.** H1a의 실제 이력: `_h1a_contract.py`가
2026-07-31~08-01엔 `DESIGN_DECISION_H1a_prompt_surface.md`의 fenced block을
프롬프트 template으로 **직접 로드**했다(판정문 원문 보존 규칙과 충돌하는
상태). 2026-08-02, template을 `h1a_prompt_template.md`(별도 파일)로 분리해
지금은 **네 판정문 전부 순수 기록**이다. 이 상태가 다음에도 유지된다는
보장은 없다 — 새 세션은 이렇게 확인한다:

```bash
# 서술적 인용("DESIGN_DECISION_X.md §4는...")이 아니라 실제 로드 지점만
grep -rn 'HERE / "DESIGN_DECISION\|Path([^)]*"DESIGN_DECISION' experiments/*/[_a-z]*.py
```

결과가 있으면, 그 판정문은 **문서가 아니라 실행 입력**이다 — 원문 보존
규칙과 충돌하므로 template 분리(H1a의 Q5~Q7 사례)가 필요할 수 있다.
(서술적 인용은 흔하고 정상이다 — 이 grep은 `HERE / "DESIGN_DECISION..."`
형태의 실제 경로 조립만 잡도록 좁혔다.)

## 4. 탐색 레시피 — "X를 알고 싶다" → 실행할 명령

> **아래 레시피는 전부 `grep` 기반이다.** 저장소 안에서 "무엇이 어디 있나"엔
> 충분하지만, **"이건 이미 결정됐나"엔 답하지 못한다**(§0 함정 4). 그 질문엔
> §4.0의 graph 절차를 쓴다.

### 4.0 vault graph 탐색 — 결정·선례를 찾을 때

**절차는 이미 작성·검증돼 있다. 다시 만들지 마라**:

```bash
# 전체 절차(Required Procedure / Prohibited Actions / Command Template)
cat ../.vault-harness/vault-md-retrieval/AGENT_PROMPT.md

# 패키지된 4턴 버전
python3 ../.vault-harness/vault-md-retrieval/multiturn_retrieval.py "QUERY" \
  --policy recall-first-v2 --max-turns 4
```

손으로 돌릴 때(Obsidian 앱이 떠 있어야 한다):

```bash
obsidian read      path="notes/audits/vault/symlink-vs-moc-2026-07-30.md"
obsidian backlinks path="notes/00-moc/by-topic/vault-architecture.md" counts format=json
obsidian links     path="<위에서 읽은 문서>"
obsidian tags      path="<...>" format=json
obsidian properties path="<...>" format=json
```

**`file=<basename>`를 쓰지 마라 — 반드시 `path=`.** 이 워크스페이스는 worktree
간 동명 파일이 많아(`HANDOFF.md`, `WORKSPACE_NAVIGATION.md`, `README.md` …)
basename은 조용히 다른 파일로 해석된다. CLI를 못 쓰면 backlink를 **추정하지
말고** "rg-only"라고 명시하라.

핵심 규율 4개:

- 검색이 빗나가도 **즉시 키워드를 바꾸지 말 것.** 후보 pool(최대 50)을 유지하고
  미방문 8개를 먼저 소진한다
- 새 키워드보다 **읽은 문서의 실제 backlink/link를 한 홉 더 따라가는 것**이
  recall을 더 올린다(실측: 0.688 → pool refill 0.812 → graph walk 0.958 → 1.000)
- **MOC는 길찾기 전용.** 답의 근거는 canonical 원문에서 확인한다
- 이미 읽은 path와 **동일 hash replica는 다시 읽지 않는다**
  (`notes/00-moc/by-source/duplicate-register.md`가 정본/replica를 지정한다)

### 4.1 지금 상태 / 다음 할 일

```bash
cat docs/HANDOFF.md                                  # 이 worktree의 활성 상태
cat docs/EXPERIMENT_METHODOLOGY.md                    # 방법론 7규칙(§4 worktree 격리 포함)
git log --oneline -15                                # 최근 작업 흐름
git log --oneline -- experiments/<폴더>/             # 특정 실험의 이력
python3 scripts/run_gates.py                         # 전체 머지 게이트 (단일 진입점)
```

**게이트는 단일 스크립트다.** 맨손 `pytest`는 코어만 돌고(`pytest.ini`가
`experiments/` 제외), 실험 self-check는 러너가 **실험마다 별도 프로세스**로
돌린다 — 실험 폴더들이 동결 규율상 같은 모듈명(`_cert_core.py` 등)을 중복
보유해서 한 인터프리터에 모으면 남의 모듈로 조용히 실행되기 때문이다.
러너는 PASS/FAIL과 별개로 **BLOCKED**(선택적 의존성 미설치로 게이트가
시작조차 못 함)를 분리 보고한다.

### 4.2 실험 하나를 이해하기

```bash
ls experiments/<폴더>/                   # 파일 세트로 진행 단계를 추정
cat experiments/<폴더>/README.md         # 사전등록된 설계(가설/arm/N/threshold)
cat experiments/<폴더>/OPERATIONS_PLAN.md # 실행 계획 + 실제 진행 기록
python3 -c "import json;d=json.load(open('experiments/<폴더>/trials.json'));print(len(d['results']))"
```

**진행 단계 추정법**: `README.md`만 있으면 설계만 됨 → `_prompts.json`이
있으면 매니페스트 동결됨 → `trials.json`이 있으면 실행됨 → `evaluate.py`
출력이 커밋돼 있으면 채점됨.

### 4.3 어떤 텍스트가 evidence로 쓸 만한지 검증 (C1~C4)

`evidence-trace-auditor`의
**`cited-source-text-evidence-rules-at2026-07-28-14-07.md`(v2)** 에 정식 규칙이
있고, 아래는 그 실행 명령이다. **네 체크는 독립이며 하나 통과가 다른 것을
보증하지 않는다.**

> ⚠️ **v1(`-at2026-07-27-16-15.md`)을 인용하지 마라.** v2가 v1의 Auditor Notes
> 두 항목을 **철회**했다 — "감사자는 노트를 무시하고 원문만으로 판정하라"는
> 규율 의존 지침이었고, 실제로 유출된 문장들이 정확히 그 지침이 **허용하는**
> 형태였다. C1~C4와 아래 명령은 v2에서도 그대로 유효하다.

**v2가 추가한 것** (아래 명령만으로는 안 되는 부분):

- **판정 주체와 시점** — C1(liveness)·C4(precedence)는 **실행 전 하네스**가
  판정하고, 그 **결과를 감사자에게 넘기지 않는다.** 감사자는 `consulted_by`
  같은 주장의 진위를 확인할 수 없으므로 그것을 주는 것은 또 하나의 오라클을
  추가하는 것이고, 출처 서열을 암시해 감사자가 그걸로 충돌을 해결하려 든다.
- **표면 분리가 C1~C4의 전제조건** — 인용자 노트가 감사자에게 도달하면 판정이
  무의미하다. builder fixture / qualification manifest / audit payload 3면으로
  나누고, payload는 **커밋된 화이트리스트 빌더** 하나가 만든다.
- **구조화 `source_ref`** — 자유 텍스트 locator 금지(산문은 힌트가 숨는 곳).
  `file_lines` / `symbol` / `test` / `commit` / `json_pointer` tagged union.
- **qualification** — 매 실행마다 모든 ref를 해소해 인용문을 원본과 바이트
  단위로 대조하고, 어긋나면 payload 생성을 **거부**한다.
- **여러 item의 결합** — 충돌은 item 속성이 아니라 **관계**다. `admissibility`
  enum에 `conflict`를 두지 말고 `conflicts_with_evidence_ids`로. 결합 판정은
  5단계이며 **scope별로** 계산한다(전역 1회 계산은 계약을 지킨 판정을 위반으로
  잡는다 — 이 프로젝트에서 실제로 발생).

```bash
# C1 liveness — 실제로 소비되는 경로인가 (주석 자기서술 금지!)
grep -rn "SYMBOL" conceptgate/ *.py | grep -v __pycache__   # import 지점
grep -rn "def CALLER" conceptgate/                          # 호출자 한 단계 추적
python3 -m pytest -q test_semantic_regressions.py           # 검증 테스트 통과 확인

# C2 instance binding — 판정 대상 엔티티 이름이 텍스트에 실제로 있는가
grep -rn "구체엔티티명" conceptgate/ docs/ experiments/ *.py

# C3 non-circularity — 검증 대상 아티팩트 자신에서 온 텍스트는 아닌가
python3 -c "
import json;d=json.load(open('<fixture>.json'))
ev={e['text'] for e in d['evidence_items']}
inp={f['evidence'] for c in d['run_pipeline_input'] for f in c['features']}
print('CIRCULAR:', ev & inp)     # 비어 있어야 정상
"

# C4 precedence — 대상 아티팩트보다 먼저, 독립적으로 존재했는가
git log --oneline -- <evidence 원본 파일>
git blame -L <시작>,<끝> <파일>
git show <커밋>:<경로> | diff - <파일>    # 그 시점 이후 안 바뀌었는지
```

### 4.4 어떤 값/개념이 저장소 어디서 쓰이는지

```bash
grep -rn "개념명" --include="*.py" --include="*.json" --include="*.md" . | grep -v __pycache__
```

이번 세션 실사용 예: `grep -rn "완제품유닛"` → fixture 자신과 그 fixture를
논하는 문서에만 존재 = **순수 합성 개념**임을 확인. 반대로 `돌체`/`바퀴`는
E2.2/E2.2.1 fixture에 이미 동결돼 있어 **독립 evidence로 사용 가능**했다.
"저장소에 있다"와 "이 아티팩트와 독립적으로 먼저 있었다"는 다른 주장이다(C4).

### 4.5 승격된 교훈 읽기 (외부, 로컬 체크아웃 없음)

```bash
REPO=goodand/skills-catalog
DIR=skills/Skills-Create-Project/evidence-to-knowledge-promoter/references
gh api repos/$REPO/contents/$DIR --jq '.[].name' | sort   # 최신 타임스탬프 확인
gh api repos/$REPO/contents/$DIR/<파일명> --jq '.content' | base64 -d
```

**항상 최신 타임스탬프 버전을 읽어라.** 이전 버전은 superseded이며, 실제로
정정된 내용이 있다(예: dead-code lesson은 update 7에서 사실관계가 뒤집혔다).

주요 위치 (전부 `skills/Skills-Create-Project/` 아래):

| 스킬 / 파일 | 무엇을 볼 때 |
|---|---|
| `evidence-to-knowledge-promoter/.../recurring-agentic-failure-modes-lessons-at*.md` | 실패 서사·재발 판정 |
| 〃 `/dynamic-workflow-experiment-design-knowhow-at*.md` | Workflow 도구로 trial 대량 실행 — **전송 계층 ceiling 3개 포함** |
| `evidence-trace-auditor/.../cited-source-text-evidence-rules-at*.md` | evidence 검증 기계적 절차(C1~C4 + v2 추가분) |
| `agent-task-packet/.../packet-surface-closure-at*.md` | subagent에게 넘기는 packet의 표면 폐쇄 |
| `adversarial-verification-probe/.../checker-recall-and-precision-at*.md` | **검사기를 만들 때** — recall/precision 양방향 테스트, 분기 축 전수화 |
| `doc-code-sync-checker/.../generate-instead-of-detect-at*.md` | 같은 규칙이 두 곳에 있을 때 — 탐지 vs 생성 판정 |
| `measurement-evaluation-orchestrator/.../bands-are-a-function-of-n-at*.md` | N과 판정 밴드를 고정할 때 |
| `baseline-diff-lab/.../surface-change-invalidates-the-baseline-at*.md` | before/after 비교 전 전제 확인 |
| `claim-verifier/.../self-authored-claims-at*.md` | "X는 clean하다"류 자기 요약을 쓰기 전에 |
| `verification-decision-gate/.../pass-is-a-conjunction-at*.md` | 합격 판정을 설계할 때 |

카탈로그 저장소 자체의 통합 게이트에 **subflow 5**(skill 테스트를 skill마다
별도 프로세스로)가 추가돼 있다 — 이 프로젝트의 `scripts/run_gates.py`와 같은
설계이며, 근거는 `skills/integration-gate/README.md`.

### 4.6 과거 세션에서 뭘 했는지 (대화 로그)

```bash
ls ~/.claude/projects/<프로젝트-경로-슬러그>/*.jsonl
ls ~/.claude/sessions/*.json          # 세션 메타(pid, cwd, name, status)
```

`.jsonl`은 대화 원문이라 매우 크다 — `grep -n`으로 위치를 먼저 찾고 `sed -n`으로
해당 구간만 잘라 읽어라. 이번 세션에서 "candidate D가 실제로 검토됐는가"를
이 방법으로 확인했고, 결과는 "선언만 하고 실제로는 안 했음"이었다.

## 5. 판단 체계 — 찾은 문서를 얼마나 믿을 것인가

| 신호 | 신뢰도 | 이유 |
|---|---|---|
| 통과 중인 테스트가 검증하는 동작 | 최상 | 실행되는 계약 |
| `git blame`으로 확인한 커밋된 텍스트 | 상 | 시점·저자 확정 |
| 동결(frozen) fixture/manifest | 상 | 사전등록, 소급 수정 금지 |
| 커밋 메시지 | 중상 | 이 저장소는 실패 이력까지 상세히 남기는 관행 |
| 운영 로그의 "해결됨" 표시 | **중** | 인증 시점 기준으로만 유효(§0-3) |
| 코드 주석·docstring의 자기서술 | **하** | stale 전례 있음(§0-2) |
| agent/LLM 자기보고 요약 | **하** | 원 출력·실제 파일로 교차 확인 필요 |

**교차 확인 원칙**: 어떤 주장이든 실제 관측 경계(코드 실행, 파일 내용,
git 이력)에서 재확인한다. 로그나 요약 텍스트는 근거가 아니다.

## 6. 새 세션 시작 체크리스트

1. `git worktree list` + `git status` + `git log --oneline -10` — 물리적 현재 위치
2. 그 worktree의 `docs/HANDOFF.md` — 활성 상태와 다음 할 일
3. **`docs/E2.4_ISSUE_REGISTER.md`** — 미결 전체 목록. HANDOFF가 진입점이고
   이 등록부가 상세다. **`[GATE]` 항목이 있으면 그것부터** — 그게 진행을 막는
   유일한 것이라는 뜻이다
4. 이 문서(`WORKSPACE_NAVIGATION.md`) §0 함정 4개
5. 새 실험이면 `../concept-gate-taxonomy/docs/EXPERIMENT_METHODOLOGY.md`
6. Workflow/trial 대량 실행이면 skills-catalog의 최신 knowhow 파일(§4.5)
7. evidence fixture를 다룬다면 `cited-source-text-evidence-rules-at*.md`의
   C1~C4 — **v1이 아니라 최신본**(§4.3의 경고 참조)
8. 검사기·채점기를 만들거나 고친다면 `checker-recall-and-precision-at*.md` —
   통과 케이스만 테스트한 검사기는 recall이 미상이다
