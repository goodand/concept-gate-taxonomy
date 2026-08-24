# 삭제 후보 탐색 — 2026-08-24 (2차 라운드)

- 선행: [[WORKSPACE_CLEANUP_20260823|1차 라운드(2026-08-23)]] — 백업 push 4건,
  remote 브랜치 삭제 2건, 파일 삭제 5건. **그 결정을 재제안하지 않았다.**
- 방식: 탐색 범위 3분할 위임(worktree / 이 worktree의 파일 / vault 쪽) →
  **lead가 상위 판정을 직접 재실측**(P12).
- 승인 범위: 사용자가 삭제·커밋·**push까지** 승인했다. 그럼에도 실제 삭제는
  **근거 3항이 붙은 `SAFE_TO_REMOVE`에만** 적용했다 — 되돌리기 어려운 작업이다.

## 결론 — 실제 삭제는 1건뿐이다

| 축 | 후보 | 처분 |
|---|---:|---|
| worktree 11개 | **0** | 전부 보류 또는 KEEP |
| 이 worktree 파일 | **1** | `__pycache__`(840K, gitignore — 커밋 불요, 완료) |
| vault 쪽 | **0** | 재청구 회신 수령·확정 |

**후보가 거의 없는 것이 이 저장소의 성질이다**: 동결 표면·단일 정본·참조
규율 때문에 대부분의 파일이 하중을 진다. 1차 라운드가 이미 정리를 했다는 것도
이유다.

## worktree 축 — 조사의 **기준이 틀렸다**

조사는 "미병합 커밋"을 `main` 기준으로 셌다. 그러나 **trunk main은 2026-07-16에
정지**했고 모든 작업이 feature 브랜치에 있으므로, 모든 브랜치가 자명하게 큰
미병합 수를 갖는다. 그 수는 삭제 안전성과 무관하다.

**worktree 디렉터리 제거의 옳은 기준은 "origin에 push돼 있는가"** 다. 그것으로
재측정한 결과:

| 상태 | worktree |
|---|---|
| **완전 push**(ahead 0) — 디렉터리 제거로 잃는 것 없음 | `agent-publish-vault` · `e2.1-wt` · `codex-mcp-wt`(231) · `redteam-wt`(153) · `claude-provider-adapter`(158) · `input-length-guard`(166) |
| **로컬 미push 커밋 있음** — 제거 시 소실 | `taxonomy`(143) · `e2.2-wt`(6) · `h1a-scope-wt`(3) · `owl-wt`(2) |
| 활성 | `h1-wt`(24 ahead) |

조사가 뒤 4개를 `NEEDS_MERGE_FIRST`로 분류한 것은 **틀렸다** — 이미 완전
push 상태다(1차 라운드의 백업 push가 그것이다).

그럼에도 **삭제하지 않았다**: 외부 참조가 상당하다 — `redteam-wt` **48파일** ·
`claude-provider-adapter` **28** · `input-length-guard` **27** · `codex-mcp-wt`
**92**. 조사가 앞 셋을 "참조 없음"이라 보고한 것도 틀렸다.

참조의 성격은 둘로 갈린다: `notes/…/patterns-ledger.md`·`retrospectives-index.md`·
MOC의 언급은 **역사 기록**(경로 존재 의존이 아님)이고,
`vault-backlinks-mcp/experiments/…/fixtures.json`은 **경로를 실제로 쓸 수 있다**.
그 구분에는 참조 27~92건의 건별 분류가 필요하고, 되돌릴 수 없는 작업에 그
비용을 지금 들일 이유가 없다고 판단했다.

## 파일 축 — lead가 정정한 판정 2건

| 대상 | 조사 판정 | lead 재실측 |
|---|---|---|
| `concept_gate_v6_3.py` + `qa_v6_3.py` | REFERENCED("서로를 참조") | **근거가 순환이다** — 죽은 두 파일의 상호 참조는 어느 쪽도 살리지 못한다. 실제 근거는 **`README.md`가 참조**한다는 것. 결론은 같고 이유가 달랐다 |
| `.oracle_cache` (240K) | REGENERABLE_BUT_COSTLY | **하중 자산이다** — `test_stage2_freeze_v2/v4.py`와 신원 테스트 3건이 `.oracle_cache/<lf_sha256>`를 실제로 읽는다. 지우면 **테스트가 깨진다**. 240K를 아끼려 982MB PMB zip 재취득이 필요한 비용 비대칭 |

그 밖: 대체된 문서 **0건**(요청서 15·조사 요청 6이 각각 대응 판정/회신을 갖고
2건 이상에서 참조됨) · P21 부류 **0건** · 실험 폴더 죽은 파일 **0건**
(`_verify_review_11.py`·`scan_pmb_eligibility.py`처럼 import 0이어도 문서가
수동 실행 스크립트로 지목한다).

## vault 축 — 재청구 회신 확정, 0건

조사 C의 1차 회신은 꼬리(`diagrams/` 절)만 전달돼 네 표를 못 받았다. 재청구하며
전제 오류 2건을 함께 통지했다:

- "루트 `diagrams/`의 동명 파일이 `concept-gate-h1-wt/docs/diagrams/`에도 존재"
  → **거짓**. 그 디렉터리에는 `README.md`와 `refine-verify-Z*`만 있다
- "루트 `diagrams/`로의 참조 0건" → **거짓**.
  `notes/projects/concept-gate/concept-gate-diagrams-architecture-analysis.md`
  (81·83·1040·1042행)과 `docs/diagrams/README.md:66`이 가리키며, 후자는
  **input-task-output 레지스터의 실물 예시**로 지목한다 → `REFERENCED`

2차 회신에서 네 표 전부 수령했다. 결론은 전부 후보 아님:

| 항목 | 판정 | 근거 |
|---|---|---|
| `notes/00-moc/`(48파일) | `REGENERABLE_BUT_COSTLY` | 생성기(`generate_vault_mocs.py`) 있음, 그러나 39파일에서 backlink — SAFE 아님 |
| `.vault-harness/vault-md-retrieval/retrieval_index.sqlite3`(82M) 등 | `REGENERABLE_BUT_COSTLY` | 재생성 스크립트 존재하나 README가 "frozen local experiment"로 지목 — 임의 삭제 대상 아님 |
| `evidence-evaluator/results/`(1.8M) | `REGENERABLE_BUT_COSTLY` | 동일 실험 재실행으로 재생성 가능하나 기록 가치 있음 |
| 고아 노트 | **0건** | `notes/*.md` 110파일 전부 backlink 1+ (Obsidian CLI 전수 확인) |
| 중복 하네스 2개(`vault-md-retrieval` vs `evidence-evaluator/…/retrieval`) | 후보 아님 | 하나는 동결된 재현 시험, 하나는 유지 관리되는 재사용 코드 — 역할이 다르다. `.mcp.json`에 둘 다 배선돼 있다 |

`SAFE_TO_REMOVE`: **0건.**

## 이 라운드가 남기는 규율

1. **worktree 삭제 안전성의 기준은 병합이 아니라 push다.** trunk가 정지한
   저장소에서 "미병합 N건"은 정보가 아니다.
2. **상호 참조는 참조가 아니다.** 닫힌 고리는 둘 다 후보다 — 외부 참조를 봐라.
3. **캐시라도 테스트가 읽으면 하중 자산이다.** 크기와 재취득 비용의 비대칭을
   함께 보라.
4. 조사 3건 모두에서 **참조 수를 0으로 단정한 판정이 실측과 달랐다**(P12).
   `rg -l`로 세는 것은 비용이 거의 0이므로 lead가 반드시 재실측한다.
