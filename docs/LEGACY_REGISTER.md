# LEGACY 등록부 — 무엇이 죽었고, 대신 무엇을 쓰는가

## 왜 이 문서가 있는가

**표기 없는 legacy는 재사용된다.** 2026-08-24 실측: 운영 세션이
`scripts/handoff_reachability.py`를 backlink 게이트로 **재사용하자고 추천**했다.
그 파일은 이미 legacy였고 목적에 맞는 MCP 도구가 따로 있었는데, 어디에도
"이건 죽었다"고 적혀 있지 않았다. 사용자가 지적해서 멈췄다(P21).

디스크 공간이 이 저장소의 문제였던 적은 없다(정리 3라운드 누계 삭제 6파일).
**실제 피해는 잘못된 재사용**이고, 그것을 막는 것은 삭제가 아니라 **표기**다.

## 이 표가 지키는 규칙 (게이트가 강제한다 — `test_legacy_register.py`)

1. 여기 적힌 `path`는 **실재**해야 한다. `status: REMOVED`인 경우만 예외이고,
   그때는 **복구 명령**이 있어야 한다.
2. 파일 상단에 `LEGACY` 표기를 넣었으면 **이 표에 행이 있어야** 한다.
   표기만 있고 등록이 없으면 그 표기는 검색으로만 발견된다.
3. 모든 행에 **`superseded_by`가 있어야** 한다. 후계자를 못 적으면 그것은
   legacy가 아니라 **미결정**이다. P21의 원인이 정확히 이것이었다 —
   "쓰지 마라"는 알았어도 "대신 무엇을"이 없었다.
4. 표는 비어 있을 수 없다(게이트 공허화 방지).

## 등록부

| path | 무엇인가 | superseded_by | status | 왜 이 상태인가 |
|---|---|---|---|---|
| `concept_gate_v6_3.py` | v6.3 추론기 본체 | `conceptgate/concept_gate_v7.py` | RETAINED | README가 "회귀 참고용"으로 지목한다. v7 거동이 의심될 때 대조 기준이 된다 — 테스트는 없다 |
| `qa_v6_3.py` | v6.3 QA 33건 | `qa_v7.py` | RETAINED | 위와 짝. `run_gates.py`는 v7만 돈다 |
| `docs/HANDOFF.md` | 2026-08-22 시점 handoff | `HANDOFF.md` (worktree 루트) | RETAINED | 스텁으로 남겨 리다이렉트한다. **지우면 안 된다** — `vault_search`가 이 경로를 반환하므로(2026-08-24 실측) 스텁이 없으면 검색자가 아무 안내도 못 받는다 |
| `scripts/handoff_reachability.py` | Obsidian 인덱스 기반 backlink 도달성 검사 | `vault_backlinks` MCP 도구 | REMOVED | 인덱스 의존이라 인덱스가 없으면 **"backlink 0건"이라는 조용한 오답**을 냈다. MCP는 `error`+`backend_used:"none"`으로 거부한다. 복구: `git show 0c903f3^:scripts/handoff_reachability.py` |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_fixture_manifest.json` | Stage 2 동결 V1 | `stage2_fixture_manifest_v5.json` | RETAINED | **감사 표면.** 게이트가 바이트 불변을 감시한다 — `V1–V4 = V1 semantics` 선언의 증인이라 지우면 그 선언이 검증 불가가 된다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_fixture_manifest_v2.json` | 동결 V2 | `stage2_fixture_manifest_v5.json` | RETAINED | 위와 같다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_fixture_manifest_v4.json` | 동결 V4 | `stage2_fixture_manifest_v5.json` | RETAINED | 위와 같다. `test_stage2_freeze_v5.py`가 바이트 해시를 pin한다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_controls_manifest_v5.json` | 재선별 전 control 6건 | `stage2_controls_manifest_v5_1.json` | RETAINED | D-27 §18: old controls → **historical qualification evidence**, 삭제 금지 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_controls_results_v5.json` | 그 실행 결과(2/6) | `stage2_controls_results_v5_1.json` | RETAINED | 위와 같다. 실패 기록이 재선별의 근거다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_controls_trials_raw_v5.json` | 그 실행의 원본 봉투 | `stage2_controls_trials_raw_v5_1.json` | RETAINED | 위와 같다. 원본 산출은 보존이 규율이다 |

## 명시적 **비**-legacy — 이름 때문에 오해되는 것들

버전 번호가 낮다고 legacy가 아니다. 아래는 **현재 살아 있고 지우면 깨진다.**

| path | 왜 살아 있는가 |
|---|---|
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/_stage2_scope_projection.py` | 이름이 V1이지만 **V2 채점의 전처리 단계**다(`_stage2_projection_pipeline_v2`가 import). desugar·국소 관용구 정규화·source별 granularity 다리가 여기 있다. 지우면 PMB 채점이 구조적으로 전멸한다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/freeze_stage2.py` | V1 동결 스크립트지만 `SEED`·층 술어·`order_key`·`put_cache`의 **정본**이고 V4·V5가 import한다 |
| `.oracle_cache/` | 240K 캐시지만 동결 게이트 2개가 `.oracle_cache/<sha256>`를 실제로 읽는다. 지우면 재취득이 PMB 982MB zip이다 |
| `vendor/` | worktree마다 35M 사본이 있으나 git이 566파일을 추적하고 `cg_owl`·`cg_gufo`·`cg_partwhole`·`concept_gate_v7`이 읽는다. 체크아웃 사본은 git worktree의 본질이다 |

## 삭제 후보 — 승인 대기 (이 저장소 밖 사안)

정리 3라운드가 실측한 것 중 **복구 가능하면서 용량이 큰** 것들이다. 이
worktree의 커밋으로 처리할 수 없으므로(다른 디렉터리) 기록만 한다.

| 대상 | 용량 | 복구 방법 | 상태 |
|---|---:|---|---|
| 완전 push된 worktree 디렉터리 4개 (아래 §참조 분류·§More READ 참고) | **190M** | `git worktree add <경로> <브랜치>` | **T1 2개 제거 완료(91M)** · T2 판정 아래 · T3 보류 |
| `.vault-harness/vault-md-retrieval/retrieval_index.sqlite3`(81.6M) + 평가 JSON 7건(~7.6M) | **~90M** | `build_retrieval_index.py` 재실행 | **사용자 판단 대기**(양측 권한 없음 — workspace CLAUDE.md가 `.vault-harness/` 수정·이동·삭제를 금지). **근거가 2026-08-24에 교체됐다** — 아래 §"동결 판본 소실" |

**총 회수 가능 추정 282M / workspace 1.5G.**

## 참조 분류 (2026-08-24) — **경로 의존 0건**

2차 라운드가 "외부 참조 27~92건"으로 보류했다. 그 참조를 **경로 존재에
의존하는 것**과 **역사·출처 언급**으로 갈랐다.

| worktree | 위치 | 크기 | 총 참조 | 경로 의존 | 역사·출처 언급 |
|---|---|---:|---:|---:|---:|
| ~~`concept-gate-codex-mcp-wt`~~ **제거 완료(소관 세션, 2026-08-24)** | workspace 루트 | 53M | 93 | **0** | 93. 그쪽이 `git worktree remove`로 제거하고 `~/.claude.json`의 `preEnterOriginalCwd`를 정정했다(백업 후). 브랜치 `codex/mcp-provider-isolation`=`2cc7b1b`은 origin 보존 |
| `concept-gate-redteam-wt` | workspace 루트 | 43M | 49 | **0** | 49 (notes 36 · md 5 · 스냅샷 8) |
| `claude-provider-adapter` | `concept-gate-taxonomy/.claude/worktrees/` | 46M | 30 | **0** | 30 (notes 15 · md 7 · 스냅샷 8) |
| `input-length-guard` | `concept-gate-taxonomy/.claude/worktrees/` | 48M | 30 | **0** | 30 (notes 15 · md 7 · 스냅샷 8) |

위험해 보였던 범주를 전건 실측했다.

- **`vault-backlinks-mcp/experiments/2026-08-08_tool_only_context/fixtures.json`**
  (+ `trials*.json`·`_prompts*.json`, 사본 포함 8건) — worktree 경로가 나오지만
  **동결된 서버 응답 스냅샷 안의 문자열**이다. 그것을 읽는
  `test_fixtures_are_real_server_output_shape`는 **스키마 키만** 검사하고
  파일시스템을 만지지 않는다. `test_protocol.py` 전체에 경로 실재 단정이 없다.
- **`concept-gate-taxonomy/scripts/orphan_replica_audit.py`** — `codex-mcp-wt`가
  나오는 곳은 `SCRIPT_ROOT = Path(__file__).resolve().parent.parent` **옆
  주석**(원 위치 기록)이다. worktree 목록은 `discover_worktrees()`로 **동적
  탐색**하므로 없어진 worktree는 그냥 탐색되지 않는다.
- **`evidence_evaluator/contract.py`** — docstring의 출처 표기("extracted from …").
- **`vault-backlinks-mcp/tests/test_guard_witness.py`** — docstring 인용
  (`HARNESS_KNOWHOW.md` §B4a).
- **`evidence-evaluator-obsidian-wt/tests/test_schema_validator.py`** — 테스트
  데이터로 쓰인 경로 **문자열 리터럴**.
- **심볼릭 링크**: 이들을 가리키는 것 없음(`.claude/skills/vault-retrieval` 하나뿐).
- **worktree 개수를 단정하는 게이트**: 없음(`rg`로 확인).

제거 사전 점검: 4개 전부 `dirty=0` · `ahead=0` · `stash=0`.

**결론: 이 4개는 `git worktree remove`로 제거해도 깨지는 것이 없고, 필요하면
`git worktree add`로 되돌아온다.** 남는 참조는 전부 "그때 그 worktree에서
이런 일이 있었다"는 기록이고, 그 기록은 디렉터리가 없어도 유효하다.

## 제거 전 More READ (2026-08-24) — grep이 못 잡는 것을 읽어서 위험을 낮췄다

`ahead=0 · dirty=0 · stash=0`은 **추적된 것**만 말한다. `git status --short`는
**gitignore된 파일을 보여주지 않으므로**, 그것만으로 "제거해도 안전"이라고
말하면 미추적 로컬 산출물의 소실을 못 본다. `git clean -ndx`(모의 실행)로
읽었다.

| worktree | 제거 시 소실되는 미추적/무시 항목 |
|---|---|
| `concept-gate-codex-mcp-wt` | **2건** — `experiments/2026-08-07_handoff_dynamic_controller/.launcher_hmac_key`(32바이트) · 같은 폴더 `audit_workspace/` |
| `concept-gate-redteam-wt` | 0 |
| `claude-provider-adapter` | 0 |
| `input-length-guard` | 0 |

**grep 기반 분류로는 HMAC 키를 절대 못 잡았을 것이다.** 그것이 이 절이
존재하는 이유다.

그 2건을 다시 읽어 위험을 해소했다.

1. **키는 재생성된다.** `_receipt.py`가 `os.open(..., O_CREAT|O_EXCL)`로
   없으면 만들고 `secrets.token_bytes(KEY_BYTES)`를 쓴다. 고정 키가 아니다.
2. **저장된 영수증이 이 키에 묶여 있지 않다.** `verify(doc, key, domain=…)`가
   같은 키를 요구하므로 이것이 결정적 질문이었다 — 실험 폴더의 **JSON 115개를
   전수 스캔해 `signature`/`hmac`/`mac` 필드 보유 0개**를 확인했다.
   `reviewer_runner.py`는 한 실행 안에서 서명(152행)하고 검증(602행)한다 —
   런타임 전용이다.
3. **키 없이 스위트가 통과한다.** 키를 임시 이동한 뒤 실험 폴더 전체를
   돌려 **327 passed / 2 skipped**를 얻고 원위치 복원했다(32바이트 확인).
4. `audit_workspace/`는 **0바이트·파일 0개** — 빈 디렉터리다.

**결론: 4개 전부 제거해도 소실되는 증거가 없다.** 위험이 "미추적 암호 자료일
수 있음(불명)"에서 "재생성되는 임시 키 1개 + 빈 디렉터리 1개"로 내려갔다.

### 복구 명령 (제거 후 필요해지면)

```text
git -C <아무 worktree> worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-codex-mcp-wt   codex/mcp-provider-isolation
git -C <아무 worktree> worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-redteam-wt     codex/redteam-handoff-guards
git -C <아무 worktree> worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-taxonomy/.claude/worktrees/claude-provider-adapter  claude-provider-adapter
git -C <아무 worktree> worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-taxonomy/.claude/worktrees/input-length-guard      worktree-input-length-guard
```

## More READ 2차 (2026-08-24) — 위험이 **계층으로 갈렸다**

1차 More READ는 "제거 시 무엇이 소실되나"만 읽었다. 아직 안 읽은 벡터 네 개를
더 읽었고, **4개를 균일하게 다루면 안 된다는 것**이 드러났다.

| worktree | 크기 | 미추적 | 살아 있는 프로세스 | 다른 세션의 상태에 걸림 | origin 실측 | 계층 |
|---|---:|---:|---|---|---|---|
| `concept-gate-redteam-wt` | 43M | 0 | 없음 | 없음 | ✓ `62fc7e576` 일치 | **T1 — 지금 안전** |
| `input-length-guard` | 48M | 0 | 없음 | 없음 | ✓ `385e34368` 일치 | **T1 — 지금 안전** |
| `concept-gate-codex-mcp-wt` | 53M | 2 | 없음 | **있음** — 아래 §2 | ✓ `2cc7b1bb3` 일치 | **T2 — 연성 위험** |
| `claude-provider-adapter` | 46M | 0 | **`claude bg-spare` PID가 cwd로 잡고 있다** | 없음 | ✓ `d7b588b45` 일치 | **T3 — 지금 건드리지 마라** |

### 1. origin 실측 — 네 개 전부 확인

`ahead=0`은 **로컬 원격추적 ref** 기준이라 fetch가 낡았으면 거짓일 수 있다.
`git ls-remote origin refs/heads/<브랜치>`로 **원격에 직접 물어** 네 개 모두
로컬 HEAD와 동일한 커밋임을 확인했다(위 표의 SHA).

### 2. `codex-mcp-wt`은 다른 세션의 복귀 경로다 (T2)

`~/.claude.json`을 **키 범위로만** 읽었다(비밀 블록은 열지 않았다).

```text
projects.<concept-gate-taxonomy>.activeWorktreeSession.preEnterOriginalCwd
  = …/concept-gate-codex-mcp-wt
```

세션 `cf591228…`이 worktree에 진입하기 전 원래 cwd가 여기다. 그 세션이
worktree를 나가면 이 경로로 복귀하려 한다 — 디렉터리가 없으면 그 복귀가
실패한다. `worktreePath` 자체는 다른 저장소(`evidence-evaluator`)를 가리키므로
**이 4개 중 어느 것도 활성 세션의 작업 디렉터리는 아니다.**

### 3. `claude-provider-adapter`에 살아 있는 프로세스가 있다 (T3)

```text
claude bg-spare  PID 55424  cwd → …/.claude/worktrees/claude-provider-adapter
```

Claude Code의 **예열된 예비 프로세스**가 이 디렉터리를 cwd로 잡고 있다.
제거하면 그 예비가 세션에 배정될 때 존재하지 않는 디렉터리에서 시작한다.
**핸들이 사라진 뒤에 다시 판정한다.**

### 4. 내 진단이 대상을 오염시켰고 원상복구했다

`codex-mcp-wt`의 미추적이 2 → **6**으로 늘어난 것을 발견했다. 시각을 읽으니
`.pytest_cache/`와 `__pycache__` 3건이 **18:26~18:27** — HMAC 키 검증을 위해
내가 그 안에서 pytest를 돌린 잔여물이다(원래 2건은 17:08·17:28). 그 4건만
정확히 지워 **미추적 2건 상태로 복구**했다(추적 파일 변경 0).

**진단은 대상을 진단 전 상태로 되돌려야 한다.** 그러지 않으면 다음 실측이
내 잔여물을 재료로 오독한다.

## 제거 실행 (2026-08-24) — T1 두 개, 91M 회수

강제 옵션 없이 `git worktree remove`로 제거했다. 각 제거 직전에
`dirty=0 · 미추적=0 · 핸들=0`을 다시 확인했고, 제거 후 저장소 게이트를
재확인했다(둘 다 **13 passed / 0 failed**). 등록 worktree 11 → **9**.
workspace 1.5G → **1.4G**.

| 제거 | 크기 | 복구 명령 |
|---|---:|---|
| `concept-gate-redteam-wt` | 43M | `git -C concept-gate-h1-wt worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-redteam-wt codex/redteam-handoff-guards` |
| `concept-gate-taxonomy/.claude/worktrees/input-length-guard` | 48M | `git -C concept-gate-h1-wt worktree add /Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-taxonomy/.claude/worktrees/input-length-guard worktree-input-length-guard` |

첫 시도는 **상대 경로가 거부**됐다(`fatal: … is not a working tree`) — 절대
경로가 필요하다. 거부가 정상 동작이므로 강제하지 않고 경로를 고쳤다.

## T2 `concept-gate-codex-mcp-wt` — 같은 저장소의 legacy 작업 (확인)

사용자 관찰이 맞았다: 이름의 `concept-gate` 접두어대로 **같은
`concept-gate-taxonomy` 저장소의 worktree**다(동일 `CLAUDE.md`, 동일
개발자 줄). 브랜치 `codex/mcp-provider-isolation`, **마지막 커밋 2026-08-11**
(2주 전), origin에 `2cc7b1bb3` 동일 커밋 존재.

**다만 단순 legacy가 아니라 살아 있는 도구의 조상이다.** 이 worktree의
`experiments/2026-08-07_handoff_dynamic_controller/_contract.py`가 독립 프로젝트
`evidence-evaluator/`로 **추출**됐고(그 파일 docstring이 출처를 그렇게 적는다),
그 계열이 지금 이 세션이 쓰는 `vault_backlinks`·`vault_search` MCP다. 실험
14개를 들고 있고 그중 4개(`h1a_source_authority_unresolved` ·
`owl_entailment_contract_shape` · `handoff_dynamic_controller` ·
`e2.4_repo_grounded_contract_transfer`)는 다른 worktree에도 있다.

그럼에도 **디렉터리 제거는 아무것도 잃지 않는다**: 추출분은 이미 독립
프로젝트에 있고, 나머지는 origin의 `2cc7b1bb3`에 있으며, 이 worktree를
가리키는 참조 93건은 전부 역사·출처 언급으로 실측됐다(경로 의존 0).

**남은 단 하나의 걸림돌**은 `~/.claude.json`의
`activeWorktreeSession.preEnterOriginalCwd`다 — 세션 `cf591228…`이 worktree를
나갈 때 이 경로로 복귀한다. 없으면 그 복귀가 실패한다. 데이터 소실이 아니라
**다른 세션의 편의**가 깨지는 것이고, 그 세션의 작업 디렉터리는 다른
저장소(`evidence-evaluator`)다. 미추적 2건(재생성되는 HMAC 키·빈 디렉터리)은
1차 More READ에서 무해 판정했다.

## 동결 판본 소실 — 92M 항목의 근거가 교체됐다 (2026-08-24)

처음 판정할 때 나와 소관 세션이 합의한 근거는 **"재생성하면 144회 recall
측정을 재현 불가로 만든다"**였다. 개발자 회신이 평가 기록에 `index_sha256`이
있다고 알려 대조가 이뤄졌고, **그 근거가 이미 사라진 것이었다.** 내가 독립으로
재확인했다.

```text
기록된 해시  (performance_v1_codex_guard_replay_summary_20260802.json)
  22be923fb2f42d2252089fcb8e3536d33b334e12ecaa6fb089a19dd26a7f0a04

현재 retrieval_index.sqlite3 (81.6M)
  e5c03f2c9db0489f4f9897882e4c6bbd74f8ae7f88d2ff3041a6ecaa362c29e9
                                                        → 불일치

하네스 안의 모든 sqlite:
  e5c03f2c…  81.6M  retrieval_index.sqlite3              ← built_at 2026-08-14
  df0f1b3c…   3.0M  instances/perfect-structure-goodantak/…
  e3b0c442…   0.0M  vault_index.sqlite    ← 빈 문자열 해시(0바이트)
  e3b0c442…   0.0M  vault-index.sqlite    ← 같음
```

`index_sha256`은 `hashlib.sha256(db_path.read_bytes())` — **파일 바이트
전체**다(`multiturn_retrieval.py:1524`). 다르면 다른 파일이고, `22be923f`는
어디에도 없다.

**정정된 상태**

| | 실제 |
|---|---|
| 현재 81.6M 파일의 정체 | **동결 자산이 아니다.** 2026-08-14 재생성분이고 그 뒤 vault가 또 변해 경로 26%가 죽었다 |
| 동결 판본 `22be923f` | **보존돼 있지 않다 — 소실** |
| 그 위에서 측정된 144회 수치 | **이미 재현 불가.** 삭제 여부와 무관하다 |
| "동결 선언을 운영 편의로 뒤집는다"는 우려 | **뒤집을 동결이 남아 있지 않다** |

**그래도 결론은 "지워도 된다"가 아니다 — 이유가 바뀐다.** 이것은 이제
`DEFAULT_DB`이고 workspace CLAUDE.md가 규정한 1차 진입점의 실체다. 지우면
규정된 검색 경로가 끊긴다. **"동결이라 못 지운다"가 아니라 "쓰는 중이라 못
지운다"**다. 양측 권한 없음은 불변이다.

**새로 생긴 것**: 재생성은 이제 **잃을 것이 없는 조치**다. 재현성 논거가
사라졌으므로 26% 죽은 경로와 10일 노후를 고치는 데 반대 근거가 없다. 실행은
`.vault-harness/` 쓰기라 사용자 승인 사안이다.

## 색인 재생성 완료 (2026-08-24) — 검색 실패의 원인이 제거됐다

소관 세션이 사용자 승인을 받아 `.vault-harness` 색인을 재생성했다. **내가
독립 확인했다**:

| | 재생성 전 | 재생성 후 |
|---|---|---|
| 해시 | `e5c03f2c…` | **`39a75d98…`** |
| 문서 수 | 3163 | 2581 |
| 죽은 경로 | 854 (26%) | **0** |
| `built_at` | 2026-08-14 | **2026-08-24T11:21:38** |
| `concept-gate-h1-wt/HANDOFF.md`(정본) | **색인에 없음** | **있음** |
| `%RULING_CHAIN%` / `%referential_participant%` | 0 / 0 | 1 / 2 |

방금 만든 `ADOPTION_REGISTER`까지 색인돼 있다(1건). 재생성 전 상태는
`snapshots/20260824_pre_rebuild/`에 보존됐고 그 DB 해시가 `e5c03f2c…`로
**내가 이전에 실측한 값과 일치**했다 — 바이트 보존이 확인됐다.

> **2026-08-24 갱신 — 그 스냅샷은 삭제됐다**(동료 세션이 사용자 승인으로,
> 커밋 `e9230a0`, 83M 회수). 위 문단의 `e5c03f2c…` 대조는 **삭제 전에
> 수행됐으므로 기록으로 유효**하다. 삭제 근거는 어떤 평가 기록도 그 해시를
> 인용하지 않는다는 것(전수 `rg` 0건)이고, 그 DB가 담고 있던 결함(죽은 경로
> 854/3163 · 정본 HANDOFF 미색인)은 **수치로 양쪽 기록에 남아 파일 없이도
> 인용 가능하다.** 파일 경로로 그것을 다시 열려 하지 마라 — 없다.

**색인 삭제 판정은 종결됐다(2026-08-24).** `live/` 82M은 **삭제 불가 확정**
이고 사유는 "동결"이 아니라 **"쓰는 중"**이다(`DEFAULT_DB`). `snapshots/frozen/`
82M은 지금 live와 **바이트 동일**(`39a75d98…`, 실측 대조)이지만 그것이 남겨야
하는 이유다 — 지우면 다음 재생성 때 검색 결과가 실어 내보내는 `index_sha256`의
원본이 사라지고, 8월 2일 평가가 `22be923f…`를 인용하는데 그 DB가 없는 상태를
재현한다. **중복으로 보이는 것이 중복이 아닌 경우다.**

하네스 코드 변경은 **완료됐다**(결과에 3필드 · freshness 검사) — 실측 검증은
[[WORKSPACE_CLEANUP_20260824_ROUND4]] §11.
