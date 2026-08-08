# Red team — `handoff_repair_loop.py` 적대적 리뷰 결과

- 실행: 2026-08-06, subagent(적대적 리뷰어) 1명
- 발주 이유: 사용자 지시 "subagent or workflows로 test 하는 것도 가능하지?"
- 대상: `scripts/handoff_repair_loop.py` (커밋 `e9cea54`)
- 결과: **전 가드 우회. PASS 도달 경로 3개.**

발주 시 남긴 말 그대로다 — "뚫리면 그게 이 테스트의 성과다." 뚫렸다.

## 1. 가장 무거운 발견 — 문서가 구현을 앞질렀다

docstring이 가드 5개(G1–G5)를 선언했는데 **구현은 3개뿐**이었다. 직접 확인:

```
94:def tracked_file_count() -> int:     # 정의만 있고 호출 0회 → G4 부재
1                                        # 파일 전체 while 1개, 그것도 reachable_from
                                         # → main()은 단발, 루프 없음 → G5 부재
129: link_lines = [line for line in added if _LINK_LINE.search(line)]
130: if len(link_lines) > max_links:     # 링크가 아니라 링크 '줄'을 셈
```

**이 저장소가 이 세션 내내 10건 기록한 P1 패턴(주장하는 명제 ≠ 필요한 명제)을,
그 패턴을 잡으려고 만든 도구 안에서, 내가 저질렀다.** 게다가 커밋된 상태라
도구가 자기 문서로 거짓을 말하고 있었다.

## 2. PASS 도달 경로 3개

### 경로 A — 입력 집합을 좁힌다 (수선 0줄)

1. 유일한 orphan을 `.gitignore`에 추가 → 감사 입력에서 사라짐
2. dangling link를 산문으로 고쳐 씀 → dangling finding 소멸

**실측: 도달 파일 수 135 → 135로 불변인데 지표는 9 → 0.** 구조는 하나도
나아지지 않았고 계측기가 못 보는 곳으로 옮겼을 뿐이다. 이건 Phase D의
`metric-only improvement`보다 나쁜 상태이며 별도 이름이 필요하다.

### 경로 B — 바이트코드 캐시 오염 (마크다운 편집 0건)

`py_compile`로 패치한 `audit()`를 **hash-based UNCHECKED `.pyc`**로 만들고
소스 바이트를 원상 복원. 결과:

- G1 핀 해시가 **완전히 일치** (소스는 진짜 원본이므로)
- `git status` 깨끗 (`__pycache__/`가 gitignore 대상)
- 실행되는 것은 패치된 바이트코드

**G1은 소스를 핀하는데 CPython은 바이트코드를 실행한다.** `python3 -B`는
방어가 아니다 — 쓰기만 막고 읽기는 막지 않는다.

### 경로 C — 링크를 mention으로 변환

auditor는 backtick mention을 **의도적으로** dangling으로 보고하지 않는다
(404 false positive를 고친 그 결정). 그래서 깨진 `[x](gone.md)`를
`` `gone.md` ``로 바꾸면 finding이 사라진다. **정밀도를 위해 내린 옳은 결정이
게임 경로를 만들었다** — 두 요구가 실제로 충돌하는 지점이다.

## 3. 나머지 구멍

| # | 구멍 | 성격 |
|---|---|---|
| 4 | G2가 링크 줄을 셈 → 한 줄에 12개 링크 = 1로 계산 | 계수 오류 |
| 5 | untracked `.md`는 `git diff`에 안 나옴 → 새 파일이 무검사 덤프장 | 범위 누락 |
| 6 | `git update-index --skip-worktree` 한 번으로 편집이 diff에서 사라짐. auditor는 디스크에서 계속 읽음 | 가드 실명 |
| 7 | 0바이트 stub 파일을 만들면 dangling이 해소됨 | 존재 ≠ 내용 |
| 8 | dump_ratio가 `>` 라서 정확히 0.5는 통과 | 경계 오류 |

## 4. 판정 — 가드를 더 쓰는 것으로는 못 푼다

경로 B는 원리적으로 in-process 가드가 막을 수 없다. 채점기를 **import**하는 한,
채점기를 실행하는 프로세스가 이미 오염돼 있을 수 있다. 막으려면 clean
subprocess(`-B -E -P -I`, 캐시 제거/리다이렉트)에서 돌려야 하고, 그건 가드가
아니라 아키텍처다.

`.vault-harness`의 `HANDOFF_REUSE_HARNESS_PREREGISTRATION.md`(같은 날 저녁
작성)가 정확히 그 결론에 도달해 있다 — J1 최소 조건에 "judge는 agent workspace의
Python import cache와 executable을 신뢰하지 않는다", "`.gitignore`, index flags,
symlink, bytecode cache가 바뀌어도 judge input set은 고정 manifest에서 계산한다"가
들어 있고 §1.1이 이 red team 결과를 근거로 인용한다. **내 결함이 그쪽 설계
입력이 됐다.**

## 5. 이 세션에서 한 대응 (커밋 안 함, 작업 트리에만 있음)

`scripts/handoff_repair_loop.py`:

- docstring의 거짓 주장 정정 — G4/G5가 미구현이었다는 사실을 본문에 명시
- **경로 B를 `KNOWN UNCLOSED BYPASS` 절로 공개** — 안 고쳤으므로 고쳤다고
  쓰지 않는다. "green run은 문서에 대한 증거이지 채점기가 조작되지 않았다는
  증거가 아니다"라고 적었다
- G4 실구현: `assert_input_not_narrowed()` — tracked 수 감소 / 감사 입력 집합
  이탈 / skip-worktree 설정을 각각 위반으로 보고. `--emit-pins`가 해시뿐 아니라
  베이스라인 스냅샷도 함께 내도록 변경(한쪽만 잊는 것을 불가능하게)
- G5 실구현: `--require-progress PREV`
- G2: 링크 줄이 아니라 **링크 개수**를 셈, 비율은 `>=`
- untracked `.md`도 검사 대상에 포함(diff가 없으므로 전문을 added로 취급)
- `.gitignore`를 핀 대상에 추가

`test_handoff_repair_loop.py` 신규 — 전부 **공격을 재현하는 음성 테스트**.

## 6. 대응 도중 같은 결함을 한 번 더 저질렀다 (P1 11번째)

G4/G5 구현 후 뮤테이션으로 음성 테스트의 실효성을 검증했다:

| 뮤테이션 | 기대 | 실제 |
|---|---|---|
| G4 호출부 삭제 (= 원래 결함 재현) | 실패 | **통과** ← 공허 |
| G5 플래그를 안 읽게 | 실패 | 실패 ✓ |
| G2를 줄 세기로 되돌림 | 실패 | 실패 ✓ |
| 미공개 우회 문단 삭제 | 실패 | 실패 ✓ |

원인: 메타 테스트가 함수 **이름의 존재**만 검사해서 `def` 한 줄이 조건을
만족시켰다. **"정의됐지만 호출되지 않음"을 잡으려고 쓴 테스트가 정확히 그
구분을 못 하는 검사를 썼다.**

수정: `ast.walk`로 `ast.Call` 노드를 요구하도록 교체하고 테스트 docstring에
이 사고 자체를 기록.

**2026-08-07 재뮤테이션 검증 완료** (local-only, `/private/tmp/ast-remut`
격리 복사본, primary/provider/network/유료 호출 0건, 실제 워크트리
`scripts/handoff_repair_loop.py`/`test_handoff_repair_loop.py`는 미변경
— `git status --short`로 확인).

1. baseline(뮤테이션 전): `test_a_guard_documented_as_implemented_is_actually_CALLED`
   parametrize 2건 모두 PASS.
2. mutation 1 — `assert_input_not_narrowed(baseline_state)` 호출부를
   구문상 유효한 `pass  # mutated`로 치환(바이트 diff 15816→15819 확인,
   `ast.parse`로 여전히 파싱됨을 확인). 재실행 결과:
   `[G4-assert_input_not_narrowed] FAILED`, `[G4-tracked_file_count] PASSED`
   — 정확히 뮤테이션한 함수만 잡혔다.
3. 원본 복원(`diff`로 byte-identical 확인) 후 positive control 재확인:
   2 passed.
4. mutation 2 — `tracked_file_count()`의 두 호출부(`:178`, `:285`)를 모두
   `0  # mutated`로 치환. 재실행: `[G4-tracked_file_count] FAILED`,
   `[G4-assert_input_not_narrowed] PASSED`.
5. 원본 복원 후 전체 suite: **12 passed**.

**결론 — 이 메타 테스트는 실효적이다.** 두 guard 함수 각각에 대해 독립적으로
호출부 삭제를 검출했고, 원본 복원 시 항상 정상 통과했다. "미검증" 상태를
닫는다. 상세 근거: [[docs/feedback/claude_questions_for_source_session_20260807|질문 6 답변]].

## 6a. 결함 버전이 다른 worktree에 살아 있었다 (2026-08-07 발견·해소)

위 §6이 고친 것은 `codex/mcp-provider-isolation` 브랜치의 파일 하나였다.
그런데 **결함 버전의 바이트가 `concept-gate-redteam-wt`의 워킹 디렉토리에
untracked로 그대로 남아 있었다.** orphan 감사 중 worktree dirty 상태를
읽다가 발견했다.

**AST 기계 검증 결과** (파일명·docstring이 아니라 실제 호출 노드 검사):

| 가드 | docstring 주장 | 실제 |
|---|---|---|
| G1 checker immutability | hash-pinned | `assert_pins_intact` 호출됨 ✓ **단 `.pyc` 우회 미공개** — 수정본이 크게 경고하는 `KNOWN UNCLOSED BYPASS` 문단이 이 버전엔 **없다** |
| G2 no link dumps | 구현 | 호출됨 ✓ (단 링크가 아니라 링크 *줄* 을 셈 — I34) |
| G3 context required | 구현 | 호출됨 ✓ |
| **G4 no deletion to pass** | "Tracked-file count may not drop" | **`tracked_file_count()` 정의만, 호출 0회.** `audit_input_set`/`assert_input_not_narrowed`/`skip_worktree_paths` **전부 부재** |
| **G5 monotonic progress** | "Each iteration must strictly reduce findings" | **`--require-progress` 부재.** `main()` 안의 `for` 3개는 전부 print 루프이고 edit-audit-repeat 반복이 아니다 — single-shot |

즉 **선언 5개 중 2개가 공허하고 1개가 과장**인, I30이 기록한 그 상태 그대로다.

**출처 추적** — `git hash-object`로 확정:

```
blob 95e3fc3 = 결함 버전 = 커밋 e9cea54 "handoff 수리 루프 — 게이밍 방지 가드 5종"
blob 0293e55 = 수정 버전 = 커밋 df72d21, 현재 codex/mcp-provider-isolation
redteam-wt 워킹 사본 = 95e3fc3  ← e9cea54 시점에서 멈춘 stale 사본
```

`concept-gate-redteam-wt`의 브랜치 `codex/redteam-handoff-guards`는 이 파일을
**아예 추적하지 않는다**. 즉 자기 브랜치에 속하지 않는 순수 잔여물이었다.

**위험도 평가**: `scripts/run_gates.py`가 이 스크립트를 호출하지 않으므로
자동 게이트 경로에는 없었다(실측). `.pyc`도 없어 G1 우회의 재료도 없었다.
남은 위험은 **수동 실행**이다 — 그 worktree에서 이 파일을 돌리면 G4/G5가
보호한다고 믿으면서 실제로는 orphan 게임(파일 삭제·gitignore 추가로 지표만
낮추기)이 무방비로 통과한다.

**해소**: stale untracked 사본을 삭제해 worktree를 자기 브랜치 상태와
일치시켰다. `CLAUDE.md`가 금지하는 worktree 간 손 복사를 하지 않았다 —
수정본은 이미 `df72d21`에 커밋돼 있으므로 정상 전파 경로(commit → merge →
rebase)로 도달한다.

**복구 가능**(삭제 전·후 모두 검증):

```bash
git show e9cea54:scripts/handoff_repair_loop.py   # 바이트 동일, 9312 bytes
```

`e9cea54`는 `codex/mcp-provider-isolation`·`codex/entailed-is-a-contract`·
`claude-provider-adapter` 및 원격 브랜치에서 도달 가능하므로 blob은 영구
보존된다.

**이 사건이 남기는 교훈 — P1의 새 국면**: 결함을 고쳐도 **그 결함의 사본이
다른 worktree에 살아 있으면 고쳐진 것이 아니다.** §6의 뮤테이션 검증은
파일 하나의 실효성만 증명했고, 같은 결함이 몇 벌 존재하는지는 묻지 않았다.
worktree가 11개인 이 워크스페이스에서 "고쳤다"는 주장은 **어느 사본을
고쳤는가**를 함께 말해야 한다.

## 6b. 워크스페이스 dirty 상태 정리 (2026-08-07, 사용자 승인)

§6a 발견이 "dirty worktree를 읽지도 않고 protected로만 취급하면 그 안의
결함을 못 본다"를 보였으므로, 등록된 worktree 11개 전부의 dirty 항목을
읽고 판정했다. 사용자가 삭제·교체를 명시 승인했다.

| 대상 | 판정 근거 | 조치 |
|---|---|---|
| `concept-gate-redteam-wt/scripts/handoff_repair_loop.py` | §6a — 결함 버전 stale 사본 | **삭제**(git blob으로 복구 가능) |
| `input-length-guard/scratch/` | 3줄 toy `assert_reasonable_length` + 테스트 4건. 브랜치 `worktree-input-length-guard` HEAD가 `main`과 **동일**(고유 커밋 0), 워크스페이스 어디에서도 **참조 0건**(grep 실측) | **삭제.** git에 없어 복구 불가이므로 전문을 아래 보존 |
| `concept-gate-taxonomy/.claude/worktrees/` | **삭제 불가** — `git worktree list`에 등록된 **live worktree 2개**(`claude-provider-adapter`, `input-length-guard`)를 담고 있다. 지우면 worktree가 파괴된다 | **`.git/info/exclude`에 추가.** tracked `.gitignore`를 수정하지 않고, 사용자 전역 ignore도 건드리지 않는 저장소 로컬 범위 |

**`.gitignore`가 아니라 `.git/info/exclude`를 쓴 이유**: 이 저장소의 red team이
`.gitignore` 추가로 orphan 지표를 낮춘 것을 게이밍으로 기록했고
(§"G4", `handoff_repair_loop.py`가 `.gitignore`를 PINNED에 넣은 이유),
tracked `.gitignore` 수정은 `?? ` 를 ` M ` 으로 바꿀 뿐 clean도 아니다.
`.claude/worktrees/`는 실험 증거가 아니라 Claude Code 런타임 디렉토리이며,
같은 성격인 `.claude/settings.local.json`이 이미 사용자 전역 ignore
(`~/.config/git/ignore:1`)로 제외되고 있는 것을 실측 확인했다.

**삭제한 scratch 전문 보존**(git에 없었으므로):

```python
# scratch/input_length_guard.py
def assert_reasonable_length(s: str, max_len: int = 200) -> None:
    if len(s) > max_len:
        raise ValueError(f"input length {len(s)} exceeds max_len {max_len}")
```

테스트는 `test_within_default_limit_ok` / `test_exceeds_default_limit_raises` /
`test_within_custom_limit_ok` / `test_exceeds_custom_limit_raises` 4건으로,
양성·음성이 짝을 이룬 이 저장소 규율에 맞는 형태였다. 다만 어디에도 통합되지
않았다.

**결과**: 등록된 worktree 11개 중 **10개 clean**. 남은 1개는 이 세션의 작업
worktree(`concept-gate-codex-mcp-wt`)이며 전부 이번 세션 산출물로 커밋 승인
대기 상태다.

**남은 선택지(미실행)**: `input-length-guard` worktree는 이제 clean이지만
브랜치에 고유 커밋이 0이라 사실상 유휴다. `git worktree remove`로 등록
해제할 수 있으나 구조 변경이므로 별도 판단에 맡긴다.

## 6c. Orphan을 replica-collapse로 다시 산출하는 감사기 (2026-08-08)

§6a가 남긴 질문("어느 사본을 고쳤는가")은 `handoff_repair_loop.py` 한
파일에만 답했다. 사용자가 지목한 6개 `DESIGN_REQUEST_*`/`DESIGN_DECISION_*`
파일도 같은 성격의 문제였다 — worktree마다 독립 vault 경로라 codex-mcp-wt
사본을 고쳐도 나머지 worktree의 byte-identical 사본은 여전히 orphan으로
보인다.

**재사용, 재구현 아님.** `.vault-harness/vault-md-retrieval/`는 이미
`collapse_replicas()`(sha256로 그룹핑) + `precedence()`(safety_class ·
lifecycle · path 3축 정렬) + `safety_class()`(P0 dirty/active-experiment >
P1 direct-precedent > P2 path-stable > L0 archived > N0 notes)를 검색
랭킹에 쓰고 있었다. 이 하네스는 protected dirty worktree라 수정할 수
없으므로, 새 감사기
[`scripts/orphan_replica_audit.py`](../../scripts/orphan_replica_audit.py)를
`concept-gate-codex-mcp-wt/scripts/`에 신설하고 `vault_md_harness.discover_worktrees`/
`safety_class`, `advanced_retrieval.collapse_replicas`/`precedence`를
**import로 재사용**했다(파일 복사 아님 — `CLAUDE.md`의 재사용 원칙 준수).
Obsidian IPC 실패는 `unknown`으로 별도 보고하고 orphan 0건으로 뭉개지 않는다
(`PROVIDER_ADAPTERS.md`가 provider 오류를 다루는 것과 같은 규율).

**실행 결과** (`DESIGN_REQUEST*.md` + `DESIGN_DECISION*.md`, vault 전체):

```
physical files     : 157
logical documents  : 27  (replica-collapse 후)
orphan canonicals  : 2   (수정 전) → 0   (수정 후)
```

지목된 6개는 전부 이미 codex-mcp-wt README에 linked인 canonical의 replica라
0건이었다. 그러나 감사기가 **진짜 orphan 2건**을 새로 찾았다 — replica가
아니라 **내용이 실제로 분기된** 문서였다:

| 파일 | 발견 |
|---|---|
| `concept-gate-h1-wt/.../DESIGN_DECISION_H1a_identification_validity.md` | codex-mcp-wt 사본과 sha256이 다르다. h1-wt/h1a-scope-wt 두 곳에만 있는 2026-08-05 "해소" 문단(owl-wt 커밋을 cherry-pick으로 반입) 포함 — **더 최신 상태**이지 stale이 아니다 |
| `concept-gate-h1-wt/.../DESIGN_DECISION_H1a_allowed_rendering.md`(D-H1a-11) | codex-mcp-wt엔 파일 자체가 **없다**. h1-wt/h1a-scope-wt에만 존재하는 판정이고 자기 worktree README에서도 한 번도 링크된 적 없었다 |

**조치**: h1-wt는 clean이었으므로(사전 확인) 그 worktree의 자기 README
14줄을 추가해 두 판정과 대응 요청서를 링크했다 — codex-mcp-wt로 손 복사하지
않았다(내용이 진짜 분기라 손 복사하면 §6a와 같은 실패를 반복한다). 재실행
결과 `orphan canonicals: 0`. h1a-scope-wt/owl-wt/redteam-wt/claude-provider-adapter
등 나머지 worktree는 replica(sha256 동일)이므로 개별 링크가 불필요 —
`orphan-classification-methodology-2026-08-07.md`의 taxonomy가 이미
규정한 대로다.

**전파 정책 확인**: h1-wt의 이 진전을 codex-mcp-wt로 손으로 옮기지 않았다.
`CLAUDE.md`의 유일한 정상 경로(commit → merge → rebase)를 따른다 — 이
문서가 `.git/info/exclude`와 stale-사본 삭제에 적용한 것과 같은 규율이다.

### 6c-1. "raw orphans는 아직 55건" — 재현하고 전수 검증했다 (2026-08-08)

수정 후에도 `obsidian orphans vault="Project_in_progress"`(vault 전체
6,063건)를 `DESIGN_REQUEST`/`DESIGN_DECISION`으로 필터링하면 **여전히
55건**이 나온다. **이건 이 감사기의 결함이 아니라 두 도구가 다른 것을 센다는
사실이다** — `obsidian orphans`는 파일 하나하나가 개별 backlink를 가졌는지
세고, 이 감사기는 채택된 taxonomy(`orphan-classification-methodology-2026-08-07.md`
§1 — "개별 분류 필요 ≠ 개별 Markdown wikilink 필요")대로 **canonical 하나만
링크되면 나머지 replica는 의도적으로 링크가 없어도 된다**고 센다. 두 숫자가
동시에 참일 수 있고, 설명 없이 나란히 두면 모순으로 보인다.

**그래서 55건을 하나도 빼지 않고 재검증했다** — 개별 확인이 아니라 각 파일의
sha256을 계산해 이미 확인된 27개 canonical 그룹의 해시 집합과 대조하는
스크립트로:

```
raw orphan matching DESIGN_* family : 55
unaccounted-for (진짜 미해결)         : 0
```

**55건 = 18개 canonical 그룹(전부 linked)의 replica.** 그중 둘은 이 대조로
새로 실제 검증했다 — owl-wt의 `DESIGN_DECISION_H1a_prescribed_sentence_defects.md`
(byte-identical, `diff` exit 0)와 `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`
(byte-identical, codex-mcp-wt 반입본과 sha256 동일 — README가 예전에
"저장소 미반입"이라 부르던 그 원본이다).

**감사기 자체의 진짜 gap도 하나 나왔다.** `notes/`는 `git worktree list`에
등록된 worktree가 아니라서 `discover_worktrees()`가 아예 보지 못한다 —
`notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`가 처음엔 스캔 범위 밖이었다.
`safety_class()`가 이미 `lifecycle == "notes"` 분기(N0, 최저 우선순위)를
갖고 있었으므로, 감사기에 `VAULT_ROOT/notes/`를 별도로 스캔해 `lifecycle="notes"`로
편입하는 코드를 추가했다 — N0는 어떤 worktree 사본보다도 precedence가 낮아
기존 canonical 선택을 절대 뒤집지 않는다. 재스캔 결과 `notes/`에서 물리
파일 6개, 논리 그룹 4개가 추가로 잡혔고 **전부 이미 linked**였다(2건은
기존 그룹의 replica, 2건은 이번 세션이 만든 taxonomy 판정문 자신, 2건은
`notes/projects/concept-gate/experiments/h1a/`의 vault mirror 사본 —
`DESIGN_workspace_file_placement.md`가 기록한 "미러 + `canonical:` 포인터"
패턴 그대로).

**최종**: `physical files: 163`, `logical documents: 31`, `orphan
canonicals: 0`. raw `obsidian orphans`의 55건과 감사기의 `0건`은 **모순이
아니라 서로 다른 정의**이고, 그 정의 차이를 숨기지 않고 both 숫자를 나란히
기록한다.

## 7. 남은 것

- [x] 메타 테스트 AST 교체본의 뮤테이션 재검증 — 2026-08-07 완료, 실효성 확인
      (위 §6)
- [x] 결함 버전 stale 사본(`concept-gate-redteam-wt`) 제거 — 2026-08-07
      완료(위 §6a)
- [x] **전 worktree 사본 전수 확인** — 2026-08-07. `find` + `git hash-object`로
      워크스페이스 전역의 `handoff_repair_loop.py` 사본을 blob 단위 대조:
      남은 3개(`concept-gate-codex-mcp-wt`, `concept-gate-owl-wt`,
      `concept-gate-taxonomy/.claude/worktrees/claude-provider-adapter`)
      **전부 수정본 `0293e55`**, 결함 버전 `95e3fc3` **0개**. §6a가 제기한
      "어느 사본을 고쳤는가" 질문에 대한 답을 파일명이 아니라 **내용 해시**로
      확정했다
- [x] **replica-collapse 감사기로 DESIGN_REQUEST/DESIGN_DECISION 계열 orphan
      전수 해소** — 2026-08-08 완료(위 §6c). `notes/` 스캔 추가 후 최종
      163개 물리 파일 → 31개 논리 문서, canonical orphan 2 → 0. raw
      `obsidian orphans`의 잔여 55건은 전부 이 31개 canonical의 replica임을
      해시 대조로 전수 검증(§6c-1) — 미해결 0건
- [ ] 경로 B: clean subprocess 채점으로 전환 (아키텍처 변경, 미착수)
- [ ] 경로 C: mention 채널에 G2/G3를 적용할지, mention을 도달성 계산에서 뺄지
      — 정밀도와 게임 방지가 충돌하므로 **판정이 필요한 설계 문제**
- [ ] 구멍 7(0바이트 stub): dangling 해소 시 대상 파일 크기 하한 요구
- [ ] 위 작업 트리 변경 전부 **커밋 안 됨** (커밋 승인 대기)
