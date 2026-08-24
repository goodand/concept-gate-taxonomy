# 워크스페이스 정리 4라운드 — 범위 분할과 위임 (2026-08-24)

- 1~3라운드: [[WORKSPACE_CLEANUP_20260823]] · [[WORKSPACE_CLEANUP_20260824]] ·
  [[WORKSPACE_CLEANUP_20260824_ROUND3]]
- 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]

## 0. 이 라운드가 앞선 셋과 다른 점 — **분할 축을 크기에서 권위로 바꿨다**

1~3라운드는 **크기와 최신성**으로 범위를 나눴다("가장 큰 것부터", "오래된
것부터"). 그 축이 세 번 다 헛돌았다 — 누계 삭제가 파일 6건이다. 3라운드는
그 이유까지 적었다: 큰 것은 대개 **load-bearing이라서 크다**(`vendor/` 35M은
subtree이고, `.git` 34M은 저장소 자체다).

이번엔 **"무슨 시험을 통과해야 지울 수 있는가"**로 나눴다. 같은 크기의 두
파일이 전혀 다른 시험을 받는다면 그 둘은 다른 범위다.

| 범위 | 대상 | 이 범위의 권위 시험 | 담당 |
|---|---|---|---|
| **A** | git 밖 최상위 5디렉터리 (15파일 248K) | **복구 경로가 있는가** — git이 추적하지 않으므로 삭제가 되돌릴 수 없다 | lead 직접 |
| **B** | `archive/` 77M | **다른 곳에 이미 보존됐는가** — read-only 역사 증거로 지정돼 있어 "안 쓴다"는 근거가 안 된다 | haiku |
| **C** | trunk 127M 중 미설명 12M | **2026-07-16 이후 만들어졌고 커밋되지 못했는가** — trunk는 그날 멈췄다 | haiku |
| **D** | 형제 worktree 3개의 비-vendor 구간 | **실험 산출물이 아닌가** — 동결 규율이 중복을 강제하므로 중복은 삭제 근거가 아니다 | haiku |
| **E** | vault `notes/` 2.5M + 소규모 저장소 2 | **세 가지 참조 형태 전부 0인가** — 경로·wikilink·식별자 토큰 | haiku |

**이미 설명된 크기를 조사 범위에서 뺐다**: `vendor/` 35M×4 = 140M(subtree),
`.git` 34M, `.claude/worktrees` 46M(등록된 worktree). 합 220M이 워크스페이스
총량의 대부분이고, 전부 **판정이 이미 끝난 것**이다. 3라운드의 실패 원인이
"내 브리프가 틀린 디렉터리를 지목했다"였으므로, 이번 브리프는 **제외 목록을
먼저 명시**한다.

## 1. Safety Gate — worktree 8개 전부 CLEAN

```text
CLEAN  claude/ontoclean-gufo-handoff-7cmq0v    concept-gate-taxonomy
CLEAN  agent/publish-conversation-vault        archive/…/agent-publish-vault
CLEAN  codex/e2.1-haiku-results-20260723       archive/…/e2.1-wt
CLEAN  codex/e2.4-contract-repo-design         concept-gate-e2.2-wt
CLEAN  codex/h1-source-authority               concept-gate-h1-wt   ← 이 세션
CLEAN  codex/h1a-typed-scope-split             concept-gate-h1a-scope-wt
CLEAN  codex/entailed-is-a-contract            concept-gate-owl-wt
CLEAN  claude-provider-adapter                 …/.claude/worktrees/…
```

보호 대상(dirty) **0건**. 3라운드까지는 이 세션 자신이 dirty였다.

## 2. 범위 A (lead 직접) — 후보 **1건**

git 밖 최상위 디렉터리가 다섯 개 있고 파일 15개 248K다. **여기 파일은
git이 추적하지 않으므로 지우면 복구 경로가 없다** — 그래서 이 범위는
위임하지 않고 직접 실측했다.

| 경로 | 크기 | 최종수정 | 전체경로 참조 | 판정 |
|---|---:|---|---:|---|
| `_scratch_coder_calibration_note/note.md` | 4K | 2026-08-05 | **0** | **CANDIDATE** |
| `diagrams/*.mmd` (5파일) | 20K | 2026-07-12 | 2 | **KEEP** |
| `docs/feedback/vault_harness_reuse_contract_questions_20260809.md` | 12K | 2026-08-09 | 6 | KEEP |
| `e2.1-execution-audit/` (5파일) | 48K | 2026-07-23 | — | **PROTECTED** |
| `h1a-execution-audit/` (6파일) | 164K | 2026-08-03 | — | **PROTECTED** |

- **`_scratch_coder_calibration_note/`**: 이름이 `_scratch`이고 전체 경로
  참조가 0이다. 유일한 후보다.
- **`diagrams/*.mmd`는 KEEP** — 그리고 그 근거가 **이 worktree 자신**이다.
  `concept-gate-h1-wt/docs/diagrams/README.md`가 `diagrams/01-architecture.mmd`
  를 **input→task→output 레지스터의 실물 예시**로 인용한다. 즉 내가 쓴 규약이
  이 파일에 의존한다. (사용자 선호에 "legacy mermaid 삭제"가 있으나 그것은
  **worktree 안의 낡은 mermaid**를 뜻하고, 이 다섯은 규약의 참조 대상이다.
  선호를 근거로 참조 중인 파일을 지우면 규약이 깨진다.)
- **두 `*-execution-audit/`은 PROTECTED** — 워크스페이스 규칙이
  "active experiment artifact는 수정·이동·삭제·이름 변경하지 마라"고 명한다.
  이것들은 실험이 실제로 돌았다는 **실행 감사 기록**(`execution_log.jsonl`,
  `journal.jsonl`, `environment.txt`, `commands.txt`)이고, git 밖에 있으므로
  **지우면 실험의 실행 증거가 영구히 사라진다.** 크기 때문에 후보로 보였던
  164K가 가장 지우면 안 되는 것이었다.

## 3. 이 라운드가 나 자신에게서 잡은 결함 — **방금 쓴 점검을 방금 위반했다**

참조 수를 처음 셀 때 **stem**(`note`)으로 셌다. 결과가 이렇게 나왔다:

```text
stem "note"        기준   ref = 1050      → "널리 참조됨, KEEP"
전체 경로 기준            ref =    0      → 유일한 후보
```

**같은 파일에 대해 1050과 0이 나왔다.** 판정이 정반대로 뒤집힌다.

이것이 나쁜 이유는 계수기 결함이라서가 아니다. **회고 §21에서 내가 방금
신설한 점검 세 형태 중 하나가 정확히 이것이다** — "선택 의존형: 이 수치는
무엇의 함수인가". 그 점검을 쓴 같은 세션에서, 다음 측정에 적용하지 않았다.

이것은 P23(내가 방금 쓴 규약을 내가 위반한다)의 새 사례이고, 동시에
**P24**(정정이 그 정정 대상의 새 사례를 동반한다)이기도 하다 — 회고가 이
점검을 신설한 것 자체가 정정이었고, 그 정정의 다음 측정이 같은 결함을 냈다.

**기제로 내리지 않는다.** 참조 계수는 매번 다른 형태로 하므로(경로·wikilink·
토큰) 게이트로 고정하면 오탐이 난다. 대신 **위임 브리프에 명문화**했다 —
범위 B~E 브리프 네 개 전부에 "basename/stem으로 세지 마라, 실제로 `note`가
1050건 걸렸고 전체 경로로는 0건이었다"를 실측 수치와 함께 넣었다. 나 자신은
못 지켰지만 지시로는 전달된다.

## 4. 위임 브리프에 공통으로 넣은 다섯 가지

3라운드까지의 실패에서 뽑았다.

1. **제외 목록 먼저** — `vendor`·`.git`·`.claude/worktrees`는 판정이 끝났다.
   (3라운드 실패 원인: 브리프가 틀린 디렉터리를 지목)
2. **재고 없이 후보를 말하지 마라** — `du` 수치부터. (G146의 원인)
3. **전체 경로로 참조를 세라** — §3의 1050 대 0.
4. **`.oracle_cache`는 ignored지만 load-bearing이다** — 테스트가 실제로 읽는다.
   ignored 항목을 후보로 올리려면 그 경로를 읽는 코드가 없음을 `rg`로 보이고
   **그 명령을 보고에 적어라.** (2라운드에서 실제로 오분류했다)
5. **"내가 확인하지 않은 것" 절 필수** — 부재를 주장하려면 무엇을 어떤
   이름으로 찾았는지 적어야 한다. 이 세션이 부재를 단정하다 다섯 번 틀렸다.

그리고 각 브리프에 **"후보 0건이면 0건이라고 보고하라 — 억지 후보보다 정직한
0건이 낫다"**를 넣었다. 3라운드에서 한 agent가 억지 후보를 올렸고 lead
재실측이 기각했다.

## 5. 회신 대기

범위 B·C·D·E 네 건. 회신이 오면 lead가 **상위 후보를 직접 재실측한 뒤에만**
삭제를 제안한다(3라운드 규율: agent 보고를 그대로 실행하지 않는다).

## 6. 범위 B 회신 — 후보 **0건**, 그리고 **판정 기준이 하나 정교해졌다**

`archive/` 77M은 전부 등록된 worktree 둘이다(비-worktree 파일 0건).

| 경로 | 크기 | origin push | 참조 | 판정 |
|---|---:|---|---:|---|
| `archive/worktrees/concept-gate-agent-publish-vault` | 40M | **완전히 push됨**(2026-07-26) | 37 | KEEP |
| `archive/worktrees/concept-gate-e2.1-wt` | 37M | **완전히 push됨**(2026-07-23) | 29 | KEEP |

둘 다 `git log @{u}..HEAD`가 비어 있다. 둘 다 2026-07-30에 만들어진 MOC
(`notes/00-moc/by-source/archived-*.md`)로 색인돼 있다.

### 6.1 "origin에 push됐는가"는 **필요조건이지 충분조건이 아니다**

2라운드는 디렉터리 제거의 기준을 정정했다 — "main에 머지됐는가"(trunk가
2026-07-16에 멈췄으므로 무의미)가 아니라 **"origin에 완전히 push됐는가"**로.
이번에 두 worktree가 **그 시험을 통과한다.** 내용이 origin에 있으므로 지워도
데이터는 사라지지 않는다.

그런데도 KEEP이다. 이유는 **`archive/`의 존재 목적이 저장이 아니라 검색**이기
때문이다 — 워크스페이스 규칙이 그것을 "searchable, read-only historical
evidence"로 지정했다. origin에 있는 것은 `rg`로 찾을 수 없다. 디렉터리를
지우면 데이터는 남고 **도달성이 사라진다.**

그래서 기준을 이렇게 정정한다:

```text
2라운드 기준:  origin에 push됐다 → 제거해도 안전
4라운드 정정:  origin에 push됐다 → 데이터는 안 잃는다
               + 그 자리에 있는 목적이 검색이 아니다 → 그때만 제거 가능
```

이 구분이 필요한 이유는 이 워크스페이스가 **부재를 단정하다 여러 번 틀렸기**
때문이다. 검색 가능한 역사를 줄이면 그 실패 모드가 늘어난다. 77M은 그
대가로 싸다.

## 7. 범위 C·D·E 회신 — 전부 후보 **0건**

| 범위 | 실측 | 후보 |
|---|---|---|
| **C** trunk 12M | tracked 425파일 · **untracked 0 · ignored 0** | 0 |
| **D** 형제 worktree 3개 | non-vendor 9.9M+7.2M+6.4M · untracked 0 · ignored 0 · `__pycache__` 0 · 이름기반 잔여물 0 | 0 |
| **E** vault 2.5M + 저장소 2 | 동명 md는 `README.md` 2건뿐이고 `diff` 결과 **내용 다름** | 0 |

C가 부수적으로 확정한 것: trunk에만 있는 실험 2건
(`2026-08-04_owl_entailment_contract_shape` 324K,
`2026-08-07_handoff_dynamic_controller` 4.5M)은 **PROTECTED** —
다른 worktree에 사본이 없고 각각 5건·18건 참조된다.

### 7.1 lead 재실측 — **하나 확증, 하나 정정**

**D의 부재 주장을 음성 대조로 확증했다.** "untracked 0"은 부재 주장이고,
**틀린 명령이 낸 0과 진짜 0은 겉모습이 같다.** 그래서 같은 명령을 이 세션
worktree(내가 방금까지 작업한 곳)에 돌렸다:

```text
concept-gate-owl-wt         untracked=0  ignored=0  __pycache__=0  .oracle_cache=no
concept-gate-h1a-scope-wt   untracked=0  ignored=0  __pycache__=0  .oracle_cache=no
concept-gate-e2.2-wt        untracked=0  ignored=0  __pycache__=0  .oracle_cache=no
concept-gate-h1-wt (대조)   untracked=1  ignored=7  __pycache__=4  .oracle_cache=YES
```

대조군이 0이 아니므로 **명령이 실제로 탐지한다.** 형제 셋의 0은 진짜 0이다.
이것이 이 저장소의 음성 테스트 규율(`test_guard_negative_coverage.py`)을
조사 보고에 적용한 형태다 — 게이트든 조사든, 침묵은 말할 수 있음을 먼저
보인 뒤에만 의미가 있다.

**E의 MCP 등재 판정을 정정했다.** agent가 `vault-backlinks-mcp`를
"`.mcp.json`에 미등록 — 별도 설정 필요"라고 보고했다. 실측: **사용자 범위
`~/.claude.json`의 `mcpServers`에 등재돼 있다**(`goodantak-vault-retrieval`·
`mcp-kroki`·`vault-backlinks-mcp`·`vault-retrieval`·`wolfram` 5종). 이 세션의
도구 목록에 그 서버가 실제로 올라와 있다.

판정 자체는 양쪽 다 KEEP이라 결과가 바뀌지 않았다. 그러나 **근거가 틀렸고,
반대로 갔으면 실제 오류였다** — "미등록이니 안 쓰는 도구"로 이어질 수 있었다.
원인은 **설정 파일이 여럿인데 하나만 봤다**는 것이고, 이것이 이 세션이 반복해
겪은 P12(틀린 범위를 찾고 부재를 단정)의 또 한 사례다.

## 8. 유일한 후보 — 이름이 거짓말했고, 그 다음에 무해해졌다

`_scratch_coder_calibration_note/note.md` (1,739바이트, git 밖, 전체경로 참조 0).

**이름만 보면 즉시 삭제 후보다.** `_scratch`이고 참조가 0이고 git이 추적하지
않는다. 그런데 **읽으니 실질 내용이었다** — 코더 자체 보정 규약("보정을
통과하지 못한 코더의 출력은 결과로 쓰지 않는다"), 그 근거("계측기의 침묵은
그것이 말할 수 있음을 먼저 보인 뒤에만 의미가 있다"), 보정 코퍼스를 합성으로
만드는 이유(실제 출력을 미리 보면 freeze-before-run이 깨진다)를 출처 인용과
함께 담고 있다.

**이름이 유일한 "스크래치" 증거였고 그 이름이 틀렸다.** 참조 0건도 삭제
근거가 못 된다 — 이 워크스페이스는 "판정 문서 7건이 backlink 0이지만 전부
살아 있었다"를 이미 실측했다.

그래서 **노트가 자기 인용을 지키는지 검증했다**(내가 만든 인용 실재 게이트와
같은 방식):

| 노트의 인용 | 실측 | 결과 |
|---|---|---|
| `PREREGISTRATION.md` §9 "코더 교정 코퍼스 규약" | 300행에 절 제목, 312행 "통과 전 사용 금지", 318행 합성 코퍼스 근거 | **정확** |
| "계측기의 침묵은…" (patterns 패턴 8) | **19개 파일**에 존재 — 5개 worktree의 `HARNESS_KNOWHOW.md`·`H1A_ISSUE_REGISTER.md`·`PREREGISTRATION.md` | **정확** |

**결론: 이 노트의 모든 주장이 git이 추적하는 문서에 이미 기록돼 있다.**
5개 worktree에 복제돼 있으므로 한 곳이 사라져도 남는다. 그러므로 삭제는
**실질을 잃지 않는다** — 그리고 삭제 근거는 "이름이 scratch다"가 아니라
**"모든 주장을 출처에서 확인했다"**다. 근거가 바뀌면 같은 결론도 다른 것이다.

**삭제는 사용자 승인 대기.** git 밖이라 되돌릴 수 없고, 4KB이므로 공간
이득은 0이다. 이득은 워크스페이스 최상위 목록에서 항목 하나가 사라지는
것뿐이다.

## 9. 이 라운드가 나 자신에게서 잡은 결함 **둘**

§3의 stem 계수(1050 대 0) 외에 하나 더 났다.

`rg -rl "checker-recall-and-precision"`을 돌렸다. `-r`은 **replace**이고
`l`을 대체 문자열로 먹었다 — 즉 "매치를 `l`로 바꿔서 출력하라"가 됐다.
그래서 출력이 `patterns 문서의 `l``처럼 **원문이 훼손된 형태**로 나왔고,
"60건"이라는 수치도 그 훼손된 검색의 것이다.

결과에 영향은 없었다(두 번째 검색 `계측기의 침묵` 19건이 판정 근거다).
그러나 **훼손된 출력을 근거로 읽었다면 노트의 인용이 틀렸다고 판정했을
것이다** — 실제로 그 출력은 노트가 `checker-recall-and-precision` 대신 `l`을
인용한 것처럼 보였다.

두 결함의 공통 형태: **내 측정 도구가 조용히 다른 것을 재고 있었다.**
stem 계수는 다른 대상을, `-rl`은 다른 연산을. 둘 다 그럴듯한 숫자를 냈다.
회고 §21이 신설한 "선택 의존형" 점검이 정확히 이것을 겨냥했는데, 같은
세션에서 두 번 걸렸다.

## 10. 4라운드 총계

| | 후보 | 삭제 |
|---|---:|---:|
| 1라운드 | 5 | 5 |
| 2라운드 | 1 | 1 |
| 3라운드 | 0 | 0 |
| **4라운드** | **1 (승인 대기)** | **0** |
| 누계 | 7 | **6** |

**네 라운드에서 삭제한 것이 파일 6건이다.** 그리고 그 사실이 이 작업의
결론이다 — 이 워크스페이스에 지울 것이 별로 없다. 대신 네 라운드가 만든
것은 삭제가 아니라 **판정 기준**이다:

1. worktree 제거 기준: "main에 머지" (틀림) → "origin에 push" (2라운드)
   → **"origin에 push" + "그 자리의 목적이 검색이 아니다"** (4라운드 §6.1)
2. 중복은 삭제 근거가 아니다 — 동결 규율이 중복을 강제한다 (D)
3. 참조 0도 삭제 근거가 아니다 — 백틱·토큰 참조는 세어지지 않는다 (E, §8)
4. 이름도 삭제 근거가 아니다 — `_scratch`가 실질 내용이었다 (§8)
5. 남는 유일한 근거: **그 내용이 추적되는 문서에 있음을 출처에서 확인** (§8)

