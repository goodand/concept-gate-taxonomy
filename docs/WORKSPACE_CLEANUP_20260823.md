# Workspace 정리 실행 기록 — 2026-08-23

branch push·삭제는 어떤 커밋 diff에도 남지 않는 workspace 상태 변경이라
여기 기록한다. 근거 조사: Sonnet(xhigh) 전수 조사 + lead 재실측 6/6 일치
(뒤집힌 주장 0 — 이 workspace 조사 중 처음).

## 실행된 것

| # | 행위 | 대상 | 근거 |
|---|---|---|---|
| ① | **백업 push** (유실 위험 해소) | `codex/mcp-provider-isolation`(+231), `codex/redteam-handoff-guards`(+153), `claude-provider-adapter`, `worktree-input-length-guard` | 4개 모두 origin에 tracking·head 부재였음 — 로컬 디스크 단일 사본. push 후 `ls-remote` 4/4 확인 |
| ② | **remote 삭제** | `fix/ontoclean-gufo-alignment` | PR#1 MERGED + origin/main의 ancestor 실측 |
| ② | **remote 삭제** | `codex/e2-provenance` | 미병합이나 20커밋 전부가 origin의 `e2.1-haiku-results`·(당시) `e2.2-structure-bvsc` 두 브랜치에 ancestor로 포함 — 삭제 전 커밋 목록 일람 완료 |
| ② | **remote+local 삭제** | `codex/e2.2-structure-bvsc-20260723` (was `d9d99f5`) | origin의 `e2.4-contract-repo-design`에 ancestor로 완전 포함 |
| ③ | **파일 삭제** | workspace 루트 `label_type.md`(0B)·`user-prompts.json`(9.8KB, 2026-07-13 세션 export, 삭제 전 일람)·`.DS_Store` 6곳 | 전부 repo 밖 또는 미추적 — worktree dirty 0 유지 확인 |

제외(보호): `codex/e2.2.1-…`(PR#4 열림), archive/ 2건(draft PR#5 포함),
vault, 별개 프로젝트 3개(evidence-evaluator·vault-backlinks-mcp·.vault-harness).

## ④ 게이트 통합 — 실측 후 **무행동 판정**

조사는 `test_guard_negative_coverage.py`의 3계보(268L/276L/326L)를 통합
후보로 냈으나, lead 실측이 판정을 정정한다:

- 원장(`KNOWN_UNPROVEN` dict 리터럴 + 주석)을 걷어낸 **기제 코드는 전
  tree 동일**(잔여 차이는 `_PENDING` 상수 문자열뿐). "같은 이름, 다른
  게이트 의미" 위험은 실재하지 않는다.
- 분기 내용은 브랜치별 원장이다 — codex-mcp의 entry 3개는 그 브랜치에만
  존재하는 가드(`_assert_provider_preflight` 등)를 가리킨다. 지금 합집합
  파일을 만들면 그 가드가 없는 브랜치에서
  `test_known_unproven_entries_are_not_stale`이 **역으로 실패**한다.
- 지금 손으로 전파하면 같은-메시지-다른-해시 계보를 4번째로 만든다(이
  파일이 겪은 바로 그 반패턴).

따라서 통합은 **브랜치 합류 시점에** git이 dict 충돌로 강제할 때 원장을
사람이 합치는 것이 정답이다. e2.2-wt의 게이트 부재와 낡은
WORKSPACE_NAVIGATION/EXPERIMENT_METHODOLOGY도 같은 경로로 해소한다.
합류 담당자를 위한 표식: **원장 합집합 + 각 entry의 가드 실재 확인**이
충돌 해소 규칙이다.

## 남는 사실

- trunk `main`은 `4d2c110`(2026-07-16) 이후 정지 — 모든 작업이 미병합
  feature 브랜치에 있다. worktree 통합 후보 0건(쌍별 ancestor 검사, 전부
  병행 독립 작업).
- skills(`adversarial-review`·`verify-conceptgate`)와 `scripts/run_gates.py`
  는 존재하는 모든 tree에서 바이트 동일 — 위험 없음.
