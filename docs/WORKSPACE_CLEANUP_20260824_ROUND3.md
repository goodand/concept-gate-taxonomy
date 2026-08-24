# 삭제 후보 탐색 — 2026-08-24 (3차 라운드)

- 선행: [[WORKSPACE_CLEANUP_20260823|1차]](파일 5건 삭제) ·
  [[WORKSPACE_CLEANUP_20260824|2차]](`__pycache__` 1건, worktree 0 · vault 0)
- 방식: **현재 작업 범위를 lead가 먼저 실사** → 규모 실측으로 범위 3분할 →
  haiku subagent 위임 → **lead가 상위 후보 직접 재실측**
- Safety Gate: 등록 worktree 11개 **전부 clean**(dirty=0), 이 작업에서는 전부
  읽기 전용으로 취급

## 결론 — **삭제 0건.** 3라운드 누계 후보는 파일 6건·디렉터리 0건이다

| 범위 | 후보 | 처분 |
|---|---:|---|
| 현재 작업 범위(이번 세션 신규 22파일) | 0 | 전부 동결 commitment·계약·운영 로그·역사 증거 |
| A `concept-gate-taxonomy`(173M, 최초 조사) | 1 제안 → **기각** | 아래 §"유일한 후보" |
| B 데이터·캐시 중복 | 0 | 회수 가능 **0바이트** |
| C `archive/` + worktree 5개 내부 | 0 | FROZEN·INTENTIONAL_REPLICA·PROTECTED |

**이 탐색의 실제 산출은 공간 회수가 아니라 고아 탐지다.** 3라운드에서 나온
것은 삭제 대상이 아니라 **그래프에서 아무것도 가리키지 않는 문서**들이었다.

## 유일한 후보 — `concept-gate-taxonomy/diagrams/` (20파일 80K): **기각**

조사 A가 `SAFE_TO_REMOVE`로 올렸다. lead가 재실측했다.

**참조 축은 조사가 맞았다.** 20개 파일 전건의 stem을 workspace 전역에서
검색해 **외부 참조 0건**을 확인했다(`vendor`·`.git` 제외). 2차 라운드에서
틀렸던 구분도 확인했다 — vault의 분석 노트가 인용하는 것은 **루트**
`diagrams/`의 5개 파일(`01-architecture` … `05-adversarial-verification`)이고,
taxonomy의 20개와 **교집합이 0**이다. 즉 이번 후보는 2차의 반증 대상과
다른 디렉터리다.

**그런데도 기각한다.** 근거:

1. **재생성 불가한 손으로 그린 설계 기록이다.** 파일명이 그 성격을 드러낸다 —
   `design-change-output-contract-before-after` · `current-pipeline-equivalence-discarded` ·
   `r2-classify-three-pass-minimal-diff` · `problem-accidental-equivalence-hidden`.
   **기각된 대안**(`-discarded`)과 **변경 전후**(`before-after`)를 그린 것은
   왜 현재 구조가 이렇게 됐는지의 증거다. 생성기가 없으므로 지우면 끝이다.
2. **이 저장소의 규율이 그런 증거를 보존한다.** D-27 §18은 실패한 control을
   "historical qualification evidence"로 남기라고 판정했고, `archive/`는
   읽기 전용 역사 증거로 규정돼 있다. 참조가 없다는 것과 값이 없다는 것은
   다르다.
3. **회수량이 80K다.** 되돌리기 어려운 작업에 그 대가는 성립하지 않는다.

**실제 결함은 삭제 대상이 아니라 고아 상태다.** 고칠 것은 링크이지 파일이
아니다. 다만 그 수리는 `concept-gate-taxonomy`에서 작업하는 세션의 일이다 —
worktree를 가로질러 손으로 고치지 않는다(commit→merge 규율).

## 범위 B — 내 브리프가 틀린 디렉터리를 지목했다

`find`로 `third_party`를 찾아 7개 worktree 중복이라 보고 위임했다. 조사가
실측했다: **`third_party`는 4K·파일 1개**(`sources.lock.json`, 7곳 sha256
동일)다. 코퍼스 저장소가 아니라 해시 고정 메타데이터였다.

부피의 실체는 **`vendor/`(worktree마다 35M, 9곳)** 였고 내 브리프는 그 이름을
넣지 않았다. lead가 직접 재실측한 결과 **후보가 아니다**:

- git이 **566 파일을 추적**한다(9곳 내용해시 `740fe24d…` 동일 — 추적 내용이
  같은 커밋대에서 같은 것은 정상이다)
- 코드가 실제로 읽는다: `cg_owl` · `cg_gufo` · `cg_partwhole` ·
  `concept_gate_v7` · `test_guard_negative_coverage`
- worktree마다 체크아웃 사본이 있는 것은 **git worktree의 본질**이다.
  지우면 작업 트리가 깨지고, worktree 자체의 삭제는 2차 라운드가 0건으로
  종결했다

**교훈: 범위를 이름으로 나누지 말고 크기로 나눠라.** `du -sh`를 먼저 돌리면
브리프가 처음부터 `vendor`를 겨눴을 것이다.

## 범위 C — 후보 0건, 그러나 **병합 대기 4건**을 찾았다

`concept-gate-e2.2-wt/experiments/2026-07-29_h1a_source_authority_unresolved/`의
`_h1a_diag.py` · `_h1a_diag_score.py` + 각 전용 테스트가, 다른 4개 worktree의
`_h1a_score.py`/`_h1a_policy.py` 계열과 **같은 실험명 아래 다른 구현**이다.
판정은 `NEEDS_MERGE_FIRST` — 정본이 미결정이므로 삭제가 아니라 병합 결정이
선행한다. **이 라운드가 만든 유일한 후속 작업 항목이다.**

조사가 의도된 복제를 정확히 분류했다: `evaluate.py` 10 · `_cert_core.py` 6 ·
`_gen_prompts.py` 7(동결 규율 — 실험 간 `sys.modules` 선점 방지) ·
`vendor/**`·`conceptgate/data/**`(subtree·해시 고정).

## 이 라운드가 남기는 규율

1. **탐색 범위는 이름이 아니라 크기로 나눈다.** 내 브리프가 4K 디렉터리를
   "7곳 중복"으로 지목하고 35M×9를 놓쳤다.
2. **`.md` 참조는 확장자 없이 센다** — wikilink가 `[[NAME]]`이므로
   `NAME.md`로 검색하면 실제 참조를 놓친다. lead가 이번에 이 실수를 했고
   MCP backlink 실측과 어긋나서 잡았다.
3. **참조 0건 ≠ 값 0.** 손으로 그린 설계 기록·기각된 대안·변경 전후는
   생성기가 없으므로 지우면 복구 불가다. 참조가 없으면 **링크를 고쳐라.**
4. **부재 주장에는 반증 명령과 그 출력을 붙인다**(회고 §18의 규율). 이번
   조사 3건은 전부 그렇게 보고했고, 2차 라운드의 "참조 없음" 오류가
   재발하지 않았다.
