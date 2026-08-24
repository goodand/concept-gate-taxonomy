# handoff 복원 시험 — 2026-08-24 (D-33 이후 상태)

- 선행: [[HANDOFF_EVALUATION_20260823|1차 시험(3/3 + 결함 2건 수리)]]
- 대상: [[concept-gate-h1-wt/HANDOFF|worktree 루트 HANDOFF]] (§0~§6)
- 시험 둘: ① `evidence-evaluator` MCP로 **그래프 도달성** ② **zero-context
  subagent**의 상태 복원
- 이 시험의 목적은 **결함을 찾는 것**이다. 통과율을 좋게 만들려고 시험을
  약화시키면 시험이 무의미해진다(대기열 규율에 그렇게 적어 뒀다).

## 1. zero-context 복원 — 9/9, 막힌 지점 0건

무맥락 agent(haiku)에게 HANDOFF 경로 하나만 주고 9문항을 물었다. 추측 금지,
근거 파일·행 필수, 못 찾으면 "복원 불가"를 쓰라고 지시했다.

| 문항 | 복원 |
|---|---|
| 다음 행동 한 가지와 그 이유 | ✅ Q34 상신 · `operational_patch: forbidden`이 근거 |
| 무엇이 막고 있고 누가 풀 수 있나 | ✅ D-33 · **외부 판정자**가 풀 수 있음 |
| trial 누계 | ✅ **0건**(세 곳에서 교차 인용) |
| 절대 금지 3가지 | ✅ 동결 표면 · adapter 코드 · **프롬프트 손 재구성** |
| 채점이 무엇을 재는가·계약 정본 | ✅ 파이프라인 모듈 + 계약 테스트 |
| control 점수와 그 보증 범위 | ✅ 5/5 · **배제한 성질은 인증 안 됨** |
| 최신 동결과 최종/잠정 | ✅ V5 · **잠정**(V3 예고) |
| 코드 수정 전 규율 | ✅ dispatch 매번 별도 승인 |
| 다시 하면 안 되는 작업 | ✅ V5 재동결 · control 4라운드 · plan 생성 |

**막힌 지점 0건.** 1차 시험(3/3)보다 문항을 3배로 늘렸는데 헤맨 곳이 없었다 —
§2 정본 지도와 사슬 색인이 작동한다.

## 2. 시험이 찾은 결함 — **운영 로그 누락 1건**

agent가 "V5.1 5/5"와 `CONTROLS_RUN_V5_20260824.md`(2/6)의 관계를 물었다.
모순이 아니라 순차 진행이라고 스스로 정정했지만, 지적의 실체는 이것이다:

> **V5.1 실행(5/5)의 운영 로그가 없었다.** 결과 JSON만 커밋했다.

방법론은 결과 artifact와 운영 로그를 **짝으로** 요구한다(V4·V5는 있다).
수리했다 — [[CONTROLS_RUN_V5_1_20260824]] 신설 + V5 문서에 후속 링크.

이 결함은 **사람도 놓쳤다**(내가 만들고 커밋했다). 시험이 없었으면
"control 로그는 V5까지만 있다"는 상태로 이어졌을 것이다.

## 3. 그래프 도달성 — 고아 1건 적발·수리

`vault_backlinks`(live, Obsidian CLI)로 이번 세션 신규 문서를 전수 확인했다.

| 문서 | backlink | 판정 |
|---|---:|---|
| D-33 판정문 | 3 | D-32-C · 색인 · HANDOFF |
| Q33 상신서 | 2 | D-33 · 색인 |
| `CONTROLS_RUN_V5_20260824` | 1 | Q33이 지목 |
| `CONTROLS_RUN_V5_1_20260824` | 1 | V5 문서(신설분) |
| **`WORKSPACE_CLEANUP_20260824`** | **0 → 2** | **고아였다.** HANDOFF §6이 백틱 경로로만 언급 → wikilink로 수리 |

원인은 이미 원장에 있는 형태다: **파일이 있는 것과 그래프에 있는 것은 다르다.**
백틱 경로·식별자 토큰으로만 언급하면 zero-context agent가 graph traversal로
도달할 수 없다. 내가 만든 규약을 내가 또 어겼다(P23 4회째).

## 4. MCP 도구의 fail-closed가 실제로 작동했다

`vault_id`를 `Project_in_progress`로 잘못 넣었더니 도구가 이렇게 답했다:

```json
{"backend_used": "none", "backlinks": null, "total": 0,
 "error": "vault_id 'Project_in_progress' is not in the registry allowlist",
 "error_code": "REGISTRY_ERROR"}
```

**빈 목록으로 위장하지 않았다.** Obsidian 인덱스에 의존하는 스크립트라면
"backlink 0건"이라는 조용한 오답을 냈을 것이고, 나는 그것을 고아 노트로
오판했을 것이다. 이것이 `handoff_reachability.py`를 지우고 MCP 도구를 쓰는
근거의 실증이다(사용자 지적: "backlink 게이트는 Obsidian 인덱스에 의존해서는
안 된다").

## 5. 시험이 찾은 두 번째 결함 — **검색 진입점이 정본에 닿지 못한다**

workspace CLAUDE.md는 **`vault_search`를 첫 진입점**으로 규정한다. 그것으로
"코호트 실행이 막힌 이유와 다음에 상신해야 하는 것"을 물었다.

| 반환된 것 | 문제 |
|---|---|
| `concept-gate-h1-wt/**docs/**HANDOFF.md` | **정본이 아니다**(SUPERSEDED 스텁) |
| 다른 worktree의 `HANDOFF.md` 3건 · archive 1건 | 동명 파일 혼입 |
| **루트 `concept-gate-h1-wt/HANDOFF.md`** | **반환되지 않았다** |
| **D-33 · Q33** | **반환되지 않았다** |

`terminal_reason: turn-budget-exhausted`. 즉 규정된 첫 진입점으로는 **현재
차단 요인에 도달하지 못한다.** 이것은 이미 알려진 성질의 재확인이다 —
질문의 어휘가 파일명에 없으면 lexical 경로가 실패한다.

방어는 있었다: `docs/HANDOFF.md`가 SUPERSEDED 스텁이고 루트로 리다이렉트한다.
다만 리다이렉트가 **마크다운 상대 링크**여서 그래프 순회에는 보이지 않았다 —
wikilink를 추가하고, 그 스텁에 "vault_search로는 D-33에 도달하지 못한다"는
실측 사실과 사슬 색인 링크를 심었다.

**남는 권고**: 새 세션은 `vault_search`가 아니라 **HANDOFF §0에서 시작**해야
한다. 이 사실이 workspace CLAUDE.md의 Retrieval Order와 긴장 관계에 있으므로
그 문서의 개정이 필요할 수 있다(이 worktree 밖 사안이라 하지 않았다).

## 6. 한계

- zero-context 시험은 **agent 1개·haiku 1회**다. 다른 모델·다른 문항 집합에서
  같은 결과가 나오는지는 재지 않았다.
- 9문항은 내가 골랐다. 내가 답할 수 있게 써 둔 것만 물었을 가능성이 있다 —
  다만 시험이 내가 몰랐던 결함(§2)을 찾았으므로 완전히 자기확인적이지는 않다.
- `vault_search` 시험은 **질의 1건**이다. 다른 어휘로는 도달할 수도 있다.
