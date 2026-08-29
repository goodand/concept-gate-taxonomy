# 워크스페이스 정리 5라운드 — 삭제·병합 후보 (2026-08-29)

- 이전: [[WORKSPACE_CLEANUP_20260823]] · [[WORKSPACE_CLEANUP_20260824]] ·
  [[WORKSPACE_CLEANUP_20260824_ROUND3]] · [[WORKSPACE_CLEANUP_20260824_ROUND4]]
- 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- **이 라운드는 축이 하나 늘었다** — 사용자 지시로 **병합 후보**가 포함된다.

## 0. Safety Gate

worktree 8개 중 **DIRTY 1건**(`concept-gate-h1-wt` — 이 세션의 미커밋 작업),
나머지 7개 CLEAN. dirty worktree 는 보호 대상이나 이번엔 그것이 이 세션
자신이므로 내용을 안다.

## 1. **소실 1건** — 삭제 후보를 찾다 잃은 것을 찾았다

```text
scratchpad/pmb_gold   디렉터리 12,053개 그대로 · 파일 **0개**
                      (2026-08-26 실측: 12,053개 .sbn · 188M)
scratchpad/pmb_en · cohort · mrs · rehearsal · smoke    전부 파일 0개
```

이 세션이 **8/24~8/29에 걸쳐** 있었고 그 사이 macOS 가 `/private/tmp` 를
청소했다 — 파일만 지우고 빈 디렉터리는 남기는 형태다.

**저장소는 무사하다**: `.oracle_cache` 66항목, in-N **20/20 해석 가능**.
동결 실험이 필요로 하는 것은 전부 있다.

**잃은 것은 전수 재실측 능력이다.** Q34-B 의 12,053 문서 실사, D-36 수신
검증의 C1~C3, `Name ?` 394건 전수 — 전부 그 재료 기반이고 PMB 를 다시 받기
전에는 재현할 수 없다.

**그리고 남은 껍데기가 거짓 포인터다.** `freeze_stage2.py:57-58` 이 가리키는
경로가 **존재하지만 비어 있어** 부재보다 혼란스럽게 실패한다(경로 확인은
통과하고 glob 이 0건을 낸다).

> **예고돼 있었다.** D-36 저장 문서 §8 이 "gold 경로가 세션 범위다 — 다음
> 세션은 이 재실측을 재현할 수 없다"고 적었다. **다음 세션이 아니라 이 세션
> 안에서** 현실이 됐다. 세션 UUID 가 박힌 경로를 동결 스크립트가 들고 있는
> 것이 원인이다.

### 권고 (사용자 판단)

| 선택 | 내용 |
|---|---|
| **재취득** | PMB 4.0.0 을 다시 받아 **저장소 밖 영구 경로**(예: `~/corpora/pmb_gold`)에 두고 `CONCEPTGATE_PMB_GOLD` 같은 환경변수로 가리킨다. 동결 스크립트의 세션 UUID 경로는 그대로 두되(동결 표면) 러너가 환경변수를 우선한다 |
| **빈 껍데기 제거** | `scratchpad/pmb_gold` 의 빈 디렉터리 12,053개는 지금 **아무것도 아니면서 있는 것처럼 보인다**. 지우면 실패가 "경로 없음"으로 명확해진다 |
| **현상 유지** | in-N 20건은 캐시로 자족하므로 **동결 코호트 실행에는 지장이 없다**. 전수 실사만 못 한다 |

## 2. 삭제 후보 — 1차 판정 **0건**, §5 가 **뒤집었다**

> **이 절의 결론은 틀렸다.** 아래 표는 탐색 범위를 "git 이 추적하는 저장소
> 파일"로 잡았을 때의 결과다. §5 가 범위를 디스크 실측으로 넓히자 **46M 짜리
> 후보가 즉시 나왔다.** 표는 반증 기록으로 남긴다 — 지운 게 아니라 범위가
> 좁았다는 증거이기 때문이다.

| 후보 | 판정 | 근거 |
|---|---|---|
| `.DS_Store`(1건) | **해당 없음** | 추적되지 않고 `.gitignore` 에 있다. 저장소 문제가 아니다 |
| `qa_v6_3.py` · `concept_gate_v6_3.py` | **이미 등재됨** | `docs/LEGACY_REGISTER.md` 에 후계자와 함께 등재돼 있다. 참조 4·5건, 5개 worktree 공통. 새 발견이 아니다 |
| `scratchpad/*` 26항목 | **저장소 밖** | 이미 대부분 비었다(§1). 세션 범위 |
| `concept-gate-taxonomy/venv` 134M | **KEEP** | 방금 만든 게이트 실행 환경. `.gitignore` 대상이고 SRC 가 **빌려 쓴다**(worktree 마다 두지 않기 위해) |

**누계**(§5 이전): 1라운드 5 · 2라운드 1 · 3~5라운드 0 = **삭제 6건**.

여기서 "다섯 라운드가 확인한 것은 지울 것이 별로 없다는 것"이라고 적었다.
**그 문장이 이 라운드의 가장 값비싼 오류다.** 다섯 번 같은 답이 나온 것은
답이 옳다는 증거가 아니라 **다섯 번 같은 곳을 봤다는 증거**였다.

## 3. 병합·푸시 후보 — 이번 라운드의 실질

### 3.1 미push 커밋 (원격에 없어 잃을 수 있는 것)

| worktree | 브랜치 | 미push |
|---|---|---:|
| `concept-gate-h1-wt` (SRC) | `codex/h1-source-authority` | **44** |
| `concept-gate-e2.2-wt` | `codex/e2.4-contract-repo-design` | 6 |
| `concept-gate-h1a-scope-wt` | `codex/h1a-typed-scope-split` | 3 |
| `concept-gate-owl-wt` | `codex/entailed-is-a-contract` | 2 |
| `concept-gate-taxonomy` (DST) | `claude/ontoclean-...` | **1** |

**DST 의 1건은 이 세션 것이다** — `784e897`(실행·발행 가드 음성 검증).
origin 은 `eef02b8` 이고 그 위에 있다. **즉각 푸시 가능**(승인 대기).

SRC 의 44건은 이 세션의 작업 대부분이다. archive 의 두 worktree 는 미push 0.

### 3.2 `NEEDS_MERGE_FIRST` (3라운드가 남긴 유일한 후속)

`concept-gate-e2.2-wt` 의 `_h1a_diag*.py` 대 다른 worktree 의
`_h1a_score.py`/`_h1a_policy.py`. 정본이 미결정이라 삭제가 아니라 병합 결정이
선행한다. **조사 진행 중** — 결과는 §4 에 채운다.

### 3.3 브랜치 간 이관 (이 세션이 이미 처리)

| 이관 | 방식 | 근거 |
|---|---|---|
| 관계 구분 수리 | cherry-pick `17da1da` | 배포 이미지가 `conceptgate/` 만 COPY — 전체 머지는 검증 안 된 10파일을 넣는다 |
| `_check_token` fail-open | cherry-pick `1f72ab7` | 동일 |
| `norecursedirs` | **부분** cherry-pick `eef02b8` | 그 커밋의 4파일 중 `pytest.ini` 만 — 나머지는 DST 에 없는 파일을 요구한다 |

**전체 머지(SRC→DST)는 여전히 권고하지 않는다**: 494파일 · 7파일 충돌 ·
DST 고유 35커밋(규칙 재편·provider 격리)과 정면으로 만난다.

## 4. 조사 회신 (haiku 2건) — 회신 + lead 재실측

두 축 모두 haiku 로 돌렸다(모델 규약: 조사·탐색 = Haiku). 회신을 그대로 채택하지
않고 판정을 뒤집을 수 있는 주장만 직접 재실측했다.

### 4.1 축 B — 미push 커밋 분류

**회신**: 세 worktree 11건 전부 `SUPERSEDED`.

**재실측이 필요했던 이유**: 회신은 근거로 `CLAUDE.md` **1개 파일**만 대조했다.
e2.2-wt 의 6건이 실제로 바꾼 파일은 4개다 — 3개가 미대조였다. "이미 다른 곳에
있다"가 틀리면 작업을 잃으므로 12개 파일 전수를 원격 3개 브랜치와 바이트 대조했다.

| worktree | 변경 파일 | 원격에 동일본 | 판정 |
|---|---|---|---|
| e2.2-wt (6커밋) | 4 | 3 (`ontoclean`) | 아래 §4.1.1 |
| h1a-scope-wt (3커밋) | 7 | 6 (`ontoclean` 5 · `h1-source-authority` 1) | 아래 §4.1.2 |
| owl-wt (2커밋) | 1 | 1 (`ontoclean`) | **SUPERSEDED** — 회신 근거 그대로 성립 |

#### 4.1.1 e2.2-wt — 원격에 없던 1파일은 고유본이 아니라 **철회된 구본**이었다

`docs/DESIGN_workspace_file_placement.md` 만 원격 어디에도 동일본이 없었다
(e2.2-wt 185행 / 원격 246행). 처음엔 "유일한 고유 내용"으로 읽었다. **그 판정을
방향 측정이 뒤집었다.**

두 커밋은 **제목이 같고 해시만 다른 쌍둥이**다(`59a0478` vs `1522812`,
둘 다 2026-08-02). 원격 쪽이 **2차 정정본**이고 e2.2-wt 것이 1차 정정본이다.
원격에만 있는 §0.1:

> ### 0.1 두 번째 정정 (2026-08-02) — 첫 정정의 과잉 일반화
> 첫 정정(2026-08-01)은 … "Adopted hybrid" 1항 한 줄만 보고
> "활성 실험 폴더 내 어떤 `git mv` 도 금지"로 …

e2.2-wt 버전의 결론은 `## 0. 결론 — 정리 대상이 아니다`(이동 무조건 금지)이고,
원격 신본의 결론은 `## 0. 결론 — "이동 금지"가 아니라 "검증 없는 이동 금지"다`이다.

**따라서 이 6건을 push 하면 철회된 규칙이 되살아난다.** 새 내용을 잃는 문제가
아니라 **철회를 되돌리는** 문제다 — supersede 가 "덧붙임"이 아니라 "철회"를
뜻하는 사례이고, 이 워크스페이스에서 그 구분은 이미 알려진 함정이다.

판정: **SUPERSEDED — push 하지 않는다.**

#### 4.1.2 h1a-scope-wt — 원격에 없던 1파일은 낡은 인수인계 사본

`docs/HANDOFF.md`(1,137행, 최종 2026-08-08 `4b002b0`)만 고유했다. 정본은
`concept-gate-h1-wt/HANDOFF.md` 이고 그쪽 최종 수정은 2026-08-25 `eb69ac7`(오늘
이 세션이 다시 갱신했다). **21일 낡은 사본**이다.

판정: **SUPERSEDED — push 하지 않는다.**

### 4.2 축 A — `NEEDS_MERGE_FIRST` (3라운드 잔여) **해소**

**회신의 핵심 발견**: `_h1a_diag*.py` 와 `_h1a_score.py`/`_h1a_policy.py` 는
중복본이 아니라 **다른 일을 하는 모듈**이다.

| 모듈 | 하는 일 | 사전등록 근거절 |
|---|---|---|
| `_h1a_diag.py` · `_h1a_diag_score.py` | 앵커 민감도 **진단** | §11.2 · §11.2a |
| `_h1a_score.py` | 코호트 **점수** 계산 | P4~P7 |
| `_h1a_policy.py` | 축·부축 **정책** | D-H1a-11~13 |

3라운드가 `NEEDS_MERGE_FIRST` 를 건 전제는 "정본이 미결정"이었다. **그 전제가
틀렸다.** 정본은 이미 결정돼 있고 파일 배치가 그 결정을 담고 있다 — `Q6=A` 가
모델 대면 앵커를 제거해 진단의 측정 대상이 사라졌고, 진단 구현체는 은퇴했다.

lead 재실측(4 worktree × 활성/`superseded/` 계수):

| worktree | 활성 `_h1a_diag*` | `superseded/` |
|---|---:|---:|
| h1-wt | **0** | 2 |
| h1a-scope-wt | **0** | 2 |
| owl-wt | **0** | 2 |
| e2.2-wt | 2 | 0 |

세 worktree 가 이미 은퇴 결정을 반영했다. 아직 활성인 곳은 e2.2-wt 하나인데
**그 worktree 는 2026-07-30 종료된 E2.4 라인**이다(§4.1 과 같은 결론에 독립적으로
도달한다).

판정: **병합 불필요 · 삭제 불필요.** `superseded/` 보관은 동결 규율(실험 간
`sys.modules` 선점 방지)이 요구하는 것이지 정리 누락이 아니다. 3라운드의
`NEEDS_MERGE_FIRST` 는 여기서 닫는다.

### 4.3 회신이 확인하지 않았다고 스스로 밝힌 것

두 agent 모두 미확인 항목을 명시했다(그 자체는 좋은 신호다):

- 각 worktree 의 **uncommitted 변경** — 판정은 커밋된 미push 커밋만 대상
- 관련 모듈(`_h1a_contract.py`·`_h1a_surface.py`·`_h1a_cohort.py`) 간 API 호환성
- branch 계통(merge-base) 분석 · `superseded/WHY.md` 내용

**이 미확인이 위 판정을 흔들지 않는다**: §4.1 은 "push 할 가치"에 대한 판정이고
커밋된 것만 대상으로 하면 충분하다. §4.2 는 파일 배치 실측으로 닫혔고 API
호환성은 병합을 할 때만 필요한데 병합을 하지 않기로 했다.

### 4.4 이 라운드의 순 결과

| 축 | 결과 |
|---|---|
| 삭제 후보 | **0건** (5라운드 연속) |
| push 후보 | **1건** — DST `784e897` (이 세션 것) |
| 병합 후보 | **0건** — `NEEDS_MERGE_FIRST` 해소 |
| 소실 | **1건** — `pmb_gold` 12,053 문서 (§1) |


## 5. 탐색 범위 확장 (사용자 지시 — "삭제 후보 더 READ해봐")

### 5.0 왜 5라운드가 전부 0 을 냈는가

1~5라운드의 탐색 단위는 **`git ls-files` 가 아는 저장소 파일**이었다. 그 범위
안에서 0 은 참이다. 범위를 **디스크 실측(`du`·`find`)**으로 바꾸자 결과가
바뀌었다. 워크스페이스 1.6G 중 5라운드가 세어 본 적 없는 영역이 남아 있었다.

`.vault-harness`(1.1G, 최대 항목)는 **다른 세션 소관이므로 이 라운드의 탐색
영역이 아니다**(사용자 지정). 그것을 뺀 **500M** 이 이 절의 범위다.

### 5.1 확정 후보 ①  중첩 worktree `claude-provider-adapter` — **46M**

경로: `concept-gate-taxonomy/.claude/worktrees/claude-provider-adapter`

**5라운드가 못 본 이유**: 워크스페이스 루트만 훑었고 이 경로는 **저장소 안의
`.claude/` 아래에 중첩**돼 있다. `git worktree list` 에는 정상 등재돼 있다.

소실 위험 직접 재실측:

| 검사 | 결과 |
|---|---|
| 미추적·수정 파일 | **0건** |
| HEAD `d7b588b` 를 포함하는 원격 브랜치 | **1개** (`origin/claude-provider-adapter`) |
| 무시된 파일(`--ignored`) | 3건 — **전부 `__pycache__`**(바이트코드 25개) |
| 비밀정보 패턴 스캔 | **0건** |
| 최종 커밋 | 2026-08-08 (21일 정체) |

**소실 0.** 브랜치와 커밋은 origin 에 있고 worktree 는 작업 사본일 뿐이다.

이 후보는 **새 발견이 아니라 이미 등재된 것이었다** — `docs/LEGACY_REGISTER.md`
가 4라운드(2026-08-24)에 4개 후보를 전건 실측해 크기·파일수·고유파일 **0**·
비밀정보 스캔·복원 명령까지 적어 두었다. 현재 실재 여부를 재측정한 결과:

| 등재 후보 | 현재 |
|---|---|
| `concept-gate-codex-mcp-wt` (53M) | 제거됨 |
| `concept-gate-redteam-wt` (43M) | 제거됨 |
| `input-length-guard` (48M) | 제거됨 |
| **`claude-provider-adapter` (46M)** | **실재 — 유일한 잔여** |

즉 4라운드가 이미 답을 적어 뒀는데 5라운드가 그 문서를 탐색 범위에 넣지 않았다.
복원 명령도 그 문서 `:137` 에 이미 있다:

```bash
git -C <아무 worktree> worktree add \
  <workspace>/concept-gate-taxonomy/.claude/worktrees/claude-provider-adapter \
  claude-provider-adapter
```

**제거 방법**: `git worktree remove`(평 `rm` 금지 — 워크스페이스 안전 게이트
4항). dirty 0 이므로 안전 게이트 3항의 보호 대상이 아니다.

### 5.2 확정 후보 ②  `__pycache__` — 557개 · **52M**

| 위치 | 크기 |
|---|---|
| `venv` 내부 | 45M |
| 저장소 내부 | 7M |

전부 `.gitignore` 대상이고 재생성된다(게이트 1회 실행으로 복구). 동결 표면과
무관하다 — `contract_hashes` 는 **소스 모듈**을 고정하지 태 바이트코드를 고정하지
않는다. `.pytest_cache` 5개도 같은 범주(<1M).

### 5.3 확정 후보 ③  `git gc` — 약 **23M**

`concept-gate-taxonomy`: 느슨한 object **3,875개 · 28.12 MiB**, 팩은 4.66 MiB.
느슨한 것을 팩으로 접으면 대부분 회수된다. 파괴적 작업이 아니다(도달 가능한
object 는 보존).

### 5.4 정리 후보 ④  worktree 없는 로컬 브랜치 4개 (디스크 이득 없음)

| 브랜치 | 원격 |
|---|---|
| `codex/mcp-provider-isolation` | `origin/codex/mcp-provider-isolation` |
| `codex/redteam-handoff-guards` | `origin/codex/redteam-handoff-guards` |
| `main` | `origin/main` |
| `worktree-input-length-guard` | `origin/worktree-input-length-guard` |

**4개 모두 원격에 있다** — 로컬에서 지워도 소실 0. 다만 디스크 이득이 없고
`main` 은 지우면 안 된다. 실익이 낮아 **권고하지 않는다**(기록만).

### 5.5 아직 안 본 영역 (다음 라운드 몫)

| 영역 | 크기 | 왜 이번에 안 봤나 |
|---|---|---|
| `.vault-harness/` | 1.1G | **다른 세션 소관** (사용자 지정) |
| `archive/worktrees/` | 77M | 워크스페이스 규칙상 **읽기 전용 역사 증거** |
| `evidence-evaluator/` | 11M | 별도 저장소(`.git` 보유)·중첩 worktree 존재. 소관 미확인 |
| `vault-backlinks-mcp/` | 1.3M | 위와 동일 계열 |
| `notes/` | 2.5M | vault 본체 |
| `h1a-execution-audit/` · `e2.1-execution-audit/` · `evidence-evaluator-obsidian-wt/` | 460K 합 | 소액 |

### 5.6 이 절의 순 결과

| 항목 | 회수 가능 |
|---|---|
| `claude-provider-adapter` worktree | 46M |
| `__pycache__` + `.pytest_cache` | 52M |
| `git gc` (taxonomy) | ~23M |
| **합** | **~121M** (탐색 영역 500M 의 24%) |

**삭제 후보 누계 갱신**: 6건 → **7건**(worktree 1) + 캐시·gc 3범주.
"5라운드 연속 0건"은 취소한다.


## 6. 실행 (2026-08-29, 사용자 "삭제 승인")

§5 의 세 후보를 실행했다. `.vault-harness`(다른 세션 소관)와 `archive/`
(규칙상 읽기 전용 역사 증거)는 **제외**했고, 제외가 실제로 걸렸는지 삭제 전에
확인했다(둘 다 대상 목록에 0건).

| # | 작업 | 방법 | 회수 |
|---|---|---|---:|
| ① | `claude-provider-adapter` worktree 제거 | `git worktree remove` (평 `rm` 금지 — 안전 게이트 4항) | **46M** |
| ② | `__pycache__`·`.pytest_cache` 559개 | `rm -rf` (gitignore 대상·재생성 가능) | **52M** |
| ③ | `git gc` (taxonomy) | 기본 gc — 도달 가능 object 보존 | **23M** |

**실측 결과**

```text
워크스페이스   1.6G → 1.5G
taxonomy       264M → 148M      (116M 회수)
  .git          34M →  11M      느슨한 object 3,875 → 0
  worktree       8개 →  7개
.vault-harness 1.1G → 1.1G      손대지 않음
archive          77M →  77M      손대지 않음
```

**소실 0 확인**

- 브랜치 `claude-provider-adapter` = `d7b588b4` **보존**(origin 에도 있음)
- `git fsck` — dangling object 만 보고. **손상 오류 0**(gc 직후 정상)
- SRC 게이트 **14 passed / 0 failed / 0 blocked**
- DST 게이트 **11 passed / 0 failed / 0 blocked**

**부수 발견 — ② 의 회수는 되돌아오지 않는다.**
게이트를 다시 돌린 뒤에도 `__pycache__` 는 **0개**였다. 처음엔 측정 오류를
의심했고(P25), 세 방법으로 대조해 확인했다: `find` 0 · `ls` no matches ·
그리고 원인은 `scripts/run_gates.py:101` 이 `PYTHONDONTWRITEBYTECODE=1` 을
**명시적으로 설정**하기 때문이다. 즉 52M 은 게이트가 아니라 **다른 경로**
(직접 `pytest` 호출 등)로 쌓인 역사적 축적이었고, 게이트 실행으로는 재생성되지
않는다.

**미실행(권고하지 않음)**: §5.4 의 로컬 브랜치 4개 — 전부 원격에 있어 안전하지만
디스크 이득이 0 이고 `main` 이 포함돼 실익이 없다.
