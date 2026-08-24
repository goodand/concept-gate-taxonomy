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

---

## 7. §5의 **가설이 반증됐다** (2026-08-24, 동료 세션 검토 + lead 재실측)

§5에서 나는 "질문의 어휘가 파일명에 없어 lexical 경로가 실패했다"고 추정했다.
`.vault-harness` 소관 세션(`amendment 21 red-team validation`)에 검토를
요청했고, **그 추정이 틀렸다**. 내가 색인을 직접 조회해 확인했다.

```text
색인 문서 수                                     3163
concept-gate-h1-wt/HANDOFF.md   (정본)           ★ 색인에 없음
concept-gate-h1-wt/docs/HANDOFF.md (스텁)        있음
%RULING_CHAIN%                                   0건
%referential_participant%                        0건
%HANDOFF_EVALUATION%                             0건
실재하지 않는 경로                               854 / 3163 = 26%
```

**반환되지 않은 것이 아니라 검색 대상에 존재하지 않았다.** 어떤 어휘로 물어도
나올 수 없었고 그래프 순회도 불가능하다 — 노드가 없다. 색인은 2026-08-14에
만들어졌고 D-33·Q33·Q34는 그 뒤에 생겼다. 그리고 worktree 제거로 경로 26%가
죽었다.

내 스텁 wikilink 완화는 **우연히 유효했다** — 스텁이 색인에 있는 유일한
노드였으므로 실질적으로 그것만이 작동하는 경로였다. 근본 조치는 색인
재생성이고, 그것은 `.vault-harness` 쓰기라 양쪽 세션 모두 권한이 없다.

## 8. 내 쪽 과오 둘 — 회신을 **부분만 읽고** 결론을 냈다

동료 세션은 "예산 소진 disclosure가 요약 텍스트 첫 블록에 무조건 실리므로
이미 받았을 것"이라고 했다. 저장된 회신을 다시 읽었다.

```text
"do not treat this search as exhaustive"   → 0건
"Stopped on …"                             → 0건
index_metadata / built_at                  → 없음
저장된 파일의 첫 바이트                    → {"contract_version":"vault-search-result-v1", …
```

**저장된 것은 JSON뿐이다.** 결과가 토큰 상한을 넘어 파일로 저장되는 경로에서
`TextContent` 블록이 사라졌다. 즉 그 disclosure는 **결과가 클 때 정확히
사라진다** — 과잉 해석이 가장 일어나기 쉬운 조건에서 가드가 없어진다.
이것은 내 우려("`review_required`가 fail-open이다")도 아니고 동료의
주장("이미 받았다")도 아닌 **제3의 결함**이다.

그리고 **내 과오가 둘 있다.**

1. **선택한 필드만 읽고 전체를 판정했다.** 나는 `status`·`review_required`·
   `terminal_reason`·`retrieved_paths`·`review_checks`·`agent_comment`만
   뽑았고 `next_action`·`turns`·`candidates`는 읽지 않았다. 부분을 읽고
   전체를 결론한 것은 이 세션에서 계측기 실패로 네 번 겪은 것과 같은 형태다.
2. **회신이 준 절차 지시를 따르지 않았다.** `next_action`이
   `"Call vault_read for the strongest canonical authority paths before
   answering."` 였고 나는 `vault_read`를 부르지 않았다. 이번엔 불렀어도
   결과가 같았겠지만(정본이 색인에 없다) **절차를 건너뛴 것은 사실이다.**

## 9. 남는 제안 (권한 밖 — 사용자 판단)

동료 세션의 판단: 예산 소진을 review check로 만드는 것은 **144회 실측으로
기각**됐다(`sufficiency-accepted`가 이 정책에서 도달 불가이므로 항상 켜지는
공허한 가드가 된다). 그 논거는 이 저장소의 "공허한 가드" 규율과 같은 방향이라
받아들인다.

대신 **비어 있는 자리는 색인 신선도**다: 26% 죽은 경로가 어떤 필드에도
나타나지 않는다. 드물게 켜지고 조치가 명확하며(재생성) 실측 가능하므로
공허하지 않은 가드가 된다. 여기에 **내 발견을 하나 더한다** — 그런 가드를
만들어도 `TextContent`에만 실으면 큰 결과에서 사라진다. **JSON 계약 필드로
넣어야 한다.**
