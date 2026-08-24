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

### 8.1 삭제 실행 — **복구 경로를 먼저 만든 뒤에** (사용자 승인 2026-08-24)

git 밖이므로 `git show`로 되돌릴 수 없다. 등록부 게이트
(`test_legacy_register.py` 불변식 1)가 "복구 방법 없는 REMOVED는 legacy 표기가
아니라 **소실**"이라고 명한다. 그래서 순서를 이렇게 했다:

```text
① 전문을 이 문서 부록 A에 원문 그대로 보존
② 보존본이 원본과 바이트 동일한지 sha256 대조   →  131ccc9f… = 131ccc9f…
③ 그때만 삭제
④ 보존본에서 재구성해 다시 sha256 대조         →  131ccc9f…  복구 가능 YES
```

**②를 통과하지 못했으면 삭제하지 않았다.** 실행 결과: 최상위 항목
16 → 15개. 공간 이득은 0(1,739바이트)이고 이득은 최상위 목록이 한 줄 짧아진
것뿐이다 — 그것이 이 작업의 실제 크기다.

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
| **4라운드** | **1** | **1** |
| 누계 | 7 | **7** |

**네 라운드에서 삭제한 것이 파일 7건이다.** 그리고 그 사실이 이 작업의
결론이다 — 이 워크스페이스에 지울 것이 별로 없다. 대신 네 라운드가 만든
것은 삭제가 아니라 **판정 기준**이다:

1. worktree 제거 기준: "main에 머지" (틀림) → "origin에 push" (2라운드)
   → **"origin에 push" + "그 자리의 목적이 검색이 아니다"** (4라운드 §6.1)
2. 중복은 삭제 근거가 아니다 — 동결 규율이 중복을 강제한다 (D)
3. 참조 0도 삭제 근거가 아니다 — 백틱·토큰 참조는 세어지지 않는다 (E, §8)
4. 이름도 삭제 근거가 아니다 — `_scratch`가 실질 내용이었다 (§8)
5. 남는 유일한 근거: **그 내용이 추적되는 문서에 있음을 출처에서 확인** (§8)


## 부록 A — 삭제된 `_scratch_coder_calibration_note/note.md` 전문 보존

삭제 전 sha256: `131ccc9f3f532aea8fb99045bc95e426e0eb3a371cd2f32915b644c8c07981cd` (1,739바이트)

**왜 전문을 보존하는가**: 이 파일은 git이 추적하지 않았으므로 삭제하면
`git show`로 되돌릴 수 없다. §8이 확인한 대로 내용의 모든 주장은 추적되는
19개 문서에 있으나, **인용을 붙인 이 종합 형태는 여기에만 있었다.** 등록부
규칙(`test_legacy_register.py` 불변식 1)이 "복구 방법 없는 REMOVED는 legacy
표기가 아니라 소실"이라고 명한다 — 그래서 지우기 전에 복구 경로를 만든다.

복구: 이 절을 그대로 되돌려 쓴다. git 이력으로는
`git show b514a5f..HEAD -- docs/WORKSPACE_CLEANUP_20260824_ROUND4.md`.

```markdown
# 코더/스코어러 자체 보정 실패 시 방침 (있음)

이 워크스페이스에는 이미 명시된 방침이 있다. 근거: `concept-gate-e2.2-wt/experiments/2026-07-29_h1a_source_authority_unresolved/PREREGISTRATION.md` §9 "코더 교정 코퍼스 규약".

**결론: 보정을 통과하지 못한 코더의 출력은 결과로 쓰지 않는다.** 채점을 강행하는 옵션은 없다 — "통과 전 사용 금지"가 규약 문구 그대로다. 절차는: 코더를 실제 trial에 돌리기 전, 손으로 작성한 합성 보정 코퍼스(축당 사례를 나눠 총 18건 등 규모는 실험마다 다를 수 있음)에 대해 `results`를 빈 배열로 커밋한 뒤 코더를 실행해 채운다. 전건 일치가 합격 조건이며, 하나라도 어긋나면 코더를 고쳐서 다시 돌린다 — 부분 통과나 "이 정도면 됐다"는 없다.

이 규율의 근거는 "계측기의 침묵은 그것이 말할 수 있음을 먼저 보인 뒤에만 의미가 있다"(patterns 문서의 `checker-recall-and-precision`, 패턴 8)이다. 즉 코더가 자체 보정에 실패한 상태에서는 "select 없음/변화 없음" 같은 결과가 진짜 신호인지 코더의 무능인지 구별할 수 없으므로, 그 상태의 출력을 신뢰할 수 없다는 논리다. 보정 코퍼스는 실제 모델 출력이 아니라 합성 사례로 만든다 — 실제 출력을 미리 보면 동결(freeze-before-run) 규율이 깨지기 때문이다.

참고로 정밀도(precision) 축이 가장 중요하게 다뤄진다: `decision=select_type`인데 rationale에 "확신할 수 없다" 같은 헤지 표현이 섞인 사례를 넣어, 코더가 산문에 흔들려 잘못 분류하지 않는지 시험한다.
```


## 11. 동료 세션의 `.vault-harness` 수리 회신 — 실측 검증 (2026-08-24)

`amendment 21 red-team validation` 세션이 개발자 회신을 받아 권고를 구현했다고
알려 왔다. **보고를 그대로 받지 않고 전건 실측했다.**

### 11.1 확증된 것

| 주장 | 실측 |
|---|---|
| 검색 응답 끝에 3필드가 실린다 | ✅ `index_built_at: 2026-08-24T11:21:38…` · `index_sha256: 39a75d98…` · `index_state: "stale"` |
| `index_sha256`가 frozen 스냅샷 값 | ✅ `39a75d983062bd1f…` — 동료 인용값·`frozen/NOTE.md` 표·검색 응답 **삼중 일치** |
| stale이면 판정 표면까지 온다 | ✅ `status: review_required` + `INDEX_STALE` review_check, `required_action`이 "부재 판정 금지, 직접 읽기는 유효"를 명시 |
| 전체 판정 도구 존재 | ✅ `evidence-evaluator/selftest-harness/index_freshness.py` 567행, 계약 `index-freshness-result-v1` |
| 경로 재편 | ✅ `live/` 3항목 · `snapshots/frozen/` 4항목 · `snapshots/20260824_pre_rebuild/` 4항목 |
| 과거 평가 비교 불가 명기 | ✅ `frozen/NOTE.md`: "이를 과거 평가와 비교 가능한 snapshot이라고 부르면 안 됩니다" |
| 커밋 4건 | ✅ `d8a8de4`(하네스) · `880fe5c`·`dbf6051`·`dfff4b3`(evidence-evaluator, `index-freshness-preflight`) |
| push 안 함 | ✅ **동료가 맞고 내가 틀렸다** — §11.3 |

### 11.2 다르게 측정된 것 **둘**

**① `--db`는 생략할 수 없다.** 동료는 "`--db`는 생략해도 됩니다(기본값이
`live/` 경로)"라고 적었다. 실측:

```text
usage: index_freshness.py [-h] --vault-root VAULT_ROOT --db DB [--manifest MANIFEST]
index_freshness.py: error: the following arguments are required: --db
```

`--manifest`만 선택적이고 DB 옆에서 유도된다. 동료의 §5 자기보고가 정확히
"인자 생략으로 면제에 도달하던 구멍을 manifest 유도로 없앴다"였는데, 그
수리가 만든 것은 `--manifest` 선택성이고 `--db` 선택성이 아니다. **자기
수리의 범위를 한 칸 넓게 적었다.**

**② 사용자 판단 대기 대상은 82M이 아니라 1.2G다.**

```text
.venv-neural                     853M   ← 지배적 소비자 (가상환경)
snapshots/                       165M   (frozen 82M + 20260824_pre_rebuild 82M)
live/                             82M   ← 동료가 말한 그 82M
mcp-runtime/                      40M   (런처가 `uv sync --project`로 재생성)
.git                              50M
```

> **§11.5 — 이 표가 쓰인 지 몇 분 만에 낡았다.** 동료 세션이
> `20260824_pre_rebuild` 83M을 삭제했다(아래 §11.5). 현재값: `snapshots/` 82M,
> 총 **1.1G**. 표는 **삭제 시점 이전의 측정으로서 유효**하므로 지우지 않고
> 이 주석을 붙인다 — 시점 없는 수치가 낡은 수치보다 나쁘다.

색인 데이터만 세도 **세 벌 247M**이다. 재편이 스냅샷 둘을 만들면서 색인
발자국이 3배가 됐다. **"82M"은 실제 결정 대상의 3%**이고, 가장 큰 것은 색인이
아니라 가상환경이다.

이것이 중요한 이유: 사용자가 판단해야 할 양이 14배 다르면 그것은 다른
결정이다. (`.vault-harness`는 수정·이동·삭제 금지 대상이므로 **보고만 한다.**)

### 11.3 내 직전 보고를 정정한다 — 같은 결함의 **세 번째**

사용자에게 "`evidence-evaluator` … origin에 전부 push됨"이라고 보고했다.
근거가 무효였다:

```text
git rev-parse --abbrev-ref @{u}
  → fatal: no upstream configured for branch 'index-freshness-preflight'
git log @{u}..HEAD | wc -l
  → 0     ← 오류로 stdout이 비었을 뿐, "미push 0건"이 아니다
```

**upstream이 없으므로 push 여부를 그 명령으로는 알 수 없다.** 동료의
"push는 안 했습니다"가 맞다.

이번 라운드에서 같은 형태가 **세 번** 났다 — stem 계수(다른 대상), `rg -r`
(다른 연산), 그리고 이것(**오류를 데이터로**). §9가 적은 대로 셋 다 그럴듯한
숫자를 냈다. 그리고 §9에서 그 형태를 명시적으로 경고한 **직후에** 세 번째가
났다.

### 11.4 부수 확인 — 내 삭제가 도구에 보인다

전체 판정이 `dead_paths: 1`을 내고 그 경로가
`_scratch_coder_calibration_note/note.md`다 — **§8에서 내가 지운 파일**이다.
색인은 삭제 전에 만들어졌으므로 정상이고, 도구가 실제로 디스크를 본다는
증거다(동료 보고 시점 `dead 0`에서 내 작업으로 1이 됐다).

현재값: `index 2581 / disk 2591 · dead 1 · unindexed 11 · changed 6 · stale`.
동료 보고 시점은 `dead 0 · unindexed 5 · changed 5`였다 — 차이는 이 세션의
작업이다.


## 12. 동료 세션의 삭제 실행 — 전건 확증, 그리고 **남은 것이 더 크다**

동료가 사용자 승인으로 삭제를 실행했다고 알려 왔다. 전건 실측했다.

| 주장 | 실측 |
|---|---|
| `snapshots/20260824_pre_rebuild/` 삭제 | ✅ 디렉터리 없음 |
| 빈 sqlite 2개 삭제 | ✅ 0건 남음 |
| `live/`·`frozen/` 유지 | ✅ 각 82M |
| live와 frozen이 바이트 동일 | ✅ 둘 다 `39a75d983062bd1f…` — 동료 주장·`NOTE.md` 표·검색 응답 **4중 일치** |
| 커밋 `e9230a0` | ✅ "재생성 직전 스냅샷과 빈 sqlite 2개 삭제 — 83M 회수" |
| 내 등록부에 죽은 참조 | ✅ **동료가 맞다** — `LEGACY_REGISTER.md:293` |

### 12.1 `frozen` 보존 판단은 옳고, 전제를 실측으로 확인했다

동료의 논거: "지금 live와 해시가 같으니 중복처럼 보이지만, 지우면 다음
재생성에서 live가 바뀌는 순간 검색 결과가 싣는 `index_sha256`의 원본이
없어진다 — 8월 2일 평가가 `22be923f…`를 인용하는데 그 DB가 없는 상태를
재현한다."

전제(바이트 동일)를 직접 대조했고 맞다. 그리고 이 논거는 **§6.1에서 내가
`archive/`에 대해 도달한 것과 같은 형태**다 — "데이터가 다른 곳에 있다"와
"그 자리에 있어야 하는 목적이 남아 있다"는 다른 질문이다. 여기서는 목적이
검색이 아니라 **인용 가능성**이다.

### 12.2 그러나 남은 것이 지운 것보다 **10배 크다**

동료는 "그쪽 원래 관찰(82M이 최대 후보)은 여전히 유효"라고 적었다.
**내 실측은 그것과 다르다.** 삭제 후 재측정:

| | 크기 | 상태 |
|---|---:|---|
| `.venv-neural` | **853M** | **한 번도 후보로 올라오지 않았다** |
| `live/` | 82M | 삭제 불가 확정(쓰는 중) |
| `snapshots/frozen/` | 82M | 보존 확정(인용 원본) |
| `mcp-runtime/` | 40M | 런처가 `uv sync --project`로 재생성 |
| `.git` | 50M | — |
| **총** | **1.1G** | |

회수된 83M은 총량의 **7%**다. 삭제 논의 전체가 82M~165M 구간에서 이뤄졌고
**853M 가상환경은 양 세션 어느 쪽도 후보로 올린 적이 없다.**

이것이 이 라운드의 §10-3(참조 0이 삭제 근거가 못 된다)과 짝을 이루는 반대
방향의 교훈이다: **논의된 것이 가장 큰 것이라고 가정하지 마라.** 우리는 82M을
놓고 여러 왕복을 했고, 그 옆의 853M은 이름이 거론되지 않았다. `.vault-harness`는
수정·이동·삭제 금지 대상이므로 **보고만 한다** — 그러나 사용자가 판단할
대상이 무엇인지는 정확해야 한다.

### 12.3 내 문서가 쓰인 지 몇 분 만에 낡았다

§11.2의 표를 쓴 직후 그 대상이 삭제됐다. 세 문서(`HANDOFF.md` ·
`LEGACY_REGISTER.md` · 이 문서)가 동시에 낡았다.

**고친 방식**: 낡은 문장을 지우지 않고 **갱신 블록을 붙였다.** 이유는
`LEGACY_REGISTER.md:293`이 좋은 예다 — 그 문단은 "`e5c03f2c…`가 내가 이전에
실측한 값과 일치한다"고 적었고, 그 대조는 **삭제 전에 수행됐으므로 기록으로
유효하다.** 문장을 지우면 대조가 있었다는 사실이 사라진다. 대신 "그 파일은
없다, 경로로 열려 하지 마라"를 덧붙였다.

이것이 동료 세션이 하네스에 넣은 것과 같은 문제다 — **낡음을 감추지 않고
표면에 실어 보내는 것.** 문서에서는 `index_state: stale`에 해당하는 것이
갱신 블록이다.
