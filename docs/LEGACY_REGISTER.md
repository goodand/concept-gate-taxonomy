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
| 완전 push된 worktree 디렉터리 4개 (아래 §참조 분류 참고) | **190M** | `git worktree remove <경로>` → 필요 시 `git worktree add <경로> <브랜치>`(전부 `ahead=0`이라 origin에 남아 있다) | **분류 완료 — 경로 의존 0건.** 삭제 실행은 승인 대기 |
| `.vault-harness/vault-md-retrieval/retrieval_index.sqlite3` + 평가 JSON 4건 | **92M** | `build_retrieval_index.py` 재실행 | 미승인. README가 "frozen local experiment"로 지목하므로 재현 가능성 검토가 선행돼야 한다 |

**총 회수 가능 추정 282M / workspace 1.5G.**

## 참조 분류 (2026-08-24) — **경로 의존 0건**

2차 라운드가 "외부 참조 27~92건"으로 보류했다. 그 참조를 **경로 존재에
의존하는 것**과 **역사·출처 언급**으로 갈랐다.

| worktree | 위치 | 크기 | 총 참조 | 경로 의존 | 역사·출처 언급 |
|---|---|---:|---:|---:|---:|
| `concept-gate-codex-mcp-wt` | workspace 루트 | 53M | 93 | **0** | 93 (notes 46 · md 28 · 코드 주석·스냅샷 19) |
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
