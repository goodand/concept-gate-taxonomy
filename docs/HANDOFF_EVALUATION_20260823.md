# HANDOFF 평가 — zero-context 평가기 실측 (2026-08-23)

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 문서 종류: **운영 로그**(`WORKSPACE_NAVIGATION.md` §2). 동결 아티팩트와
  같은 커밋에 섞지 않는다
- 대상: 이 worktree 루트 `HANDOFF.md`(Stage 2 동결 직후판)
- 도구: `evidence-evaluator` handoff canary
  (`/Users/jaehyuntak/Desktop/Project_in_progress/evidence-evaluator`,
  `39f6715`) — subject는 **zero-context codex agent**(`codex-cli 0.147.0`,
  model `gpt-5.6-sol`, reasoning effort medium), 도구는 읽기 전용 vault MCP
  3종(`vault_search`/`vault_read`/`vault_backlinks`)만, 호출 상한 8회
- 요약: **결함 2건 발견 → 수리 → 3/3 accepted.** 발견된 결함 중 하나는
  handoff가 아니라 **정지 조건의 정본 부재**였다

## 1. 무엇을 측정했는가

subject에게 준 질문 전문(case):

> For project concept-gate-h1 (E2E-v1 Stage 2), recover the current state,
> next action, and stop conditions from the handoff and its authority source.

채점은 세 축이 섞이지 않는다(`assess_canary`):

| 축 | 항목 |
|---|---|
| runtime | 허용 도구만·상한 내·오류 0·provider trace 일치 |
| retrieval | handoff 발견 / 필수 read recall / authority 정확 적중 / navigation 발견 |
| reconstruction | state·next_action·stop 코드 **문자열 일치** / 인용이 실제 read 행 범위 안 / **모든 주장에 authority 인용 존재** |

`accepted`는 세 축 전부 만족일 때만 참이다. 코드 문자열 일치를 요구하므로
평가에 앞서 `HANDOFF.md` §0에 기계 판독 블록을 두었다(`3e9aa10`).

## 2. 발견된 결함 2건

### F-H1 — HANDOFF가 두 개였다 (이중 정본, P4)

1차 실행에서 subject의 검색이 루트 `HANDOFF.md`와 **`docs/HANDOFF.md`를
함께** 반환했다. 후자는 2026-08-22 H1a typed-scope 40 trial 시점 문서로
"40 TRIAL 실행·채점 완료. 다시 돌리지 마라"를 현재 상태로 서술한다. 즉
독립 독자가 어느 쪽을 정본으로 읽느냐에 따라 상태·다음 행동·정지 조건이
전부 달라진다.

**수리 — 삭제·이동이 아니라 능동 재유도**: 경로를 지우면 inbound wikilink가
깨지고, `superseded/`로 옮겨도 **검색에는 여전히 걸린다**(이 실측이 보여준
위험은 경로가 아니라 검색 표면이다). 그래서 사본은 남기되 본문을 정본
지목 stub으로 교체했다.

### F-H2 — 정지 조건 `NO_COHORT_WITHOUT_USER_APPROVAL`에 정본이 없었다

**3회 독립 실행이 전부 같은 지점에서 실패했다**(`authority_citation_present_
for_every_claim` = False). 실패한 주장은 매번 하나, 승인 정지조건뿐이었다:

| 주장 | 인용한 정본 | 판정 |
|---|---|---|
| current_state | HANDOFF + PREREGISTRATION_STAGE2 | ok |
| next_action | HANDOFF + PREREGISTRATION_STAGE2 | ok |
| stop: 동결 표면 수정 금지 | HANDOFF + PREREGISTRATION_STAGE2 | ok |
| **stop: 승인 없이 코호트 실행 금지** | **HANDOFF만** | **정본 없음** |

원인은 subject가 아니다. 사전등록서를 실측한 결과 `승인`·`approval`·
`execute` 어휘가 **한 번도 나오지 않는다**(§C 동결 절차까지 포함). 사전등록서는
*무엇을* 측정하는지의 정본이고 *언제 실행하는지*는 다루지 않는다. handoff는
자기 §2에서 스스로를 **포인터 문서**로 선언하므로, 이 정지 조건은 정본이
없는 상태로 handoff에만 존재했다 — **다음 세션이 근거를 못 찾고 폐기할 수
있는 정지 조건**이다.

**수리 경로 선택 — 사전등록서에 추가하지 않았다.** 그것은 정지 조건
`NO_FROZEN_SURFACE_EDITS`를 스스로 위반하는 재귀가 된다(동결 문서 편집).
승인 규칙은 실험 하나가 아니라 저장소 전역 운영 규칙이므로 비동결 정본인
`CLAUDE.md`에 `## 실행 승인` 절로 기록하고, `HANDOFF.md` §0에 **코드별
authority 근거절 매핑**을 넣어 독자가 어느 코드를 어느 정본으로 뒷받침해야
하는지 지목했다. 실험 폴더에 새 governance 파일을 만들지 않은 이유는
전역 규칙을 한 실험으로 복제하면 그것이 다시 이중 정본이 되기 때문이다.

## 3. 내 gold 설계의 오류 1건 (정정, 결함 아님)

`navigation_discovery_recall`이 5회 전부 0.0이었다. 원인은 handoff가 아니라
**내가 gold에 넣은 기대**다: navigation 대상으로 `docs/H1A_PROBLEM_ANALYSIS.md`
(패턴 원장)를 지정했는데, 이 case의 질문(state/next/stop)은 패턴 원장 발견을
요구하지 않는다. 8회 호출 상한 안에서 그것을 검색하지 않은 것은 정상 행동이다.

→ 이 case의 `navigation_paths`를 비웠다. **이 canary는 navigation 발견을
시험하지 않는다** — 통과가 아니라 명시된 한계다. navigation을 실제로
시험하려면 패턴 원장을 요구하는 별도 case가 필요하다(미작성).

## 4. 수리 후 재검증 (N=3, 전부 accepted)

```
run6: accepted=True runtime=True calls=8 handoff=True crit=1.00 auth_hit=True
      state=True next=True stop=True cite=True authcite=True
run7: accepted=True runtime=True calls=7 handoff=True crit=1.00 auth_hit=True
      state=True next=True stop=True cite=True authcite=True
run8: accepted=True runtime=True calls=6 handoff=True crit=1.00 auth_hit=True
      state=True next=True stop=True cite=True authcite=True
```

**채점기를 믿지 않고 의미 정합을 따로 확인했다.**
`authority_citation_present_for_every_claim`은 인용의 **경로 멤버십과 행
범위**만 보고 의미는 보지 않으므로, 아무 행이나 인용해도 통과할 수 있다.
3회 실행이 승인 정지조건에 붙인 인용을 직접 대조한 결과 전부 `CLAUDE.md`
285–294 — 새로 쓴 `## 실행 승인` 절(284–294) 안이었다. 허위 인용이 아니다.

## 5. 재발 방지 기제

`test_handoff_single_authority.py`(루트, core pytest가 자동 수집).
불변식은 "SUPERSEDED라고 써라"가 아니라 **"루트 밖의 HANDOFF는 머리에서
자신이 현재 상태가 아님을 선언한다"**다.

- 뮤테이션 확인: git 이력의 **실제** 결함 파일(`abe59e8:docs/HANDOFF.md`)을
  임시 트리에 심어 게이트가 잡는지 확인 — 잡았다. 발명한 테스트 데이터가
  저자의 가정을 공유하는 문제(P15)를 피하려 실물을 썼다
- 공허화 방지: 어휘 목록을 넓힌 뒤에도 "현재 상태처럼 읽히는 머리"를
  잡는 음성 테스트를 함께 넣었다
- 첫 실행에서 제3의 사본(종료된 E2.2 실험 `HANDOFF.md`)이 걸렸는데, 그
  문서는 이미 머리에 "완료됨(2026-07-24) … 기록으로 보존한다"를 달고 있어
  불변식을 충족한다 — 결함은 게이트의 표시 어휘가 영어 한 단어로 좁았던 것

게이트 전체: `python3 scripts/run_gates.py` = **13 passed / 0 failed /
1 blocked**(owlready2 — 무관). core pytest 341 → 347(신규 6건).

## 6. 재현 (verbatim 입력 + sha256)

도구 호출:

```
cd /Users/jaehyuntak/Desktop/Project_in_progress/evidence-evaluator
python3 -m evidence_evaluator.handoff_canary \
  --profile profile.json --case case.json --gold gold2.json \
  --model gpt-5.6-sol --reasoning-effort medium --max-calls 8 \
  --output result.json
```

`profile.json` (sha256 `834ac6fd78b94a1932d4758b1f08c102ebf2da04d11413c19affc31fad879667`):

```json
{
  "root": "/Users/jaehyuntak/Desktop/Project_in_progress/concept-gate-h1-wt",
  "vault_name": "concept-gate-h1-wt",
  "obsidian_enabled": false,
  "authority_prefixes": ["docs", "experiments"],
  "aliases": {"handoff": ["handover", "인수인계"], "freeze": ["동결"]},
  "excluded_globs": []
}
```

`authority_prefixes`는 색인 필터가 아니라 **순위 신호**다
(`evidence_evaluator/retrieval/profile.py:135`) — 루트 `CLAUDE.md`도 검색
대상이며 순위만 낮다. 실제로 3회 모두 발견·열독됐다.

`case.json` (sha256 `61ec63b37761e59a5d8a926755c6f099bc88fa2d3d14833a00f0ffc4532bfee0`):

```json
{
  "contract_version": "handoff-mcp-canary-case-v1",
  "id": "CGH1-FREEZE-01",
  "project_id": "concept-gate-h1 (E2E-v1 Stage 2)",
  "question": "For project concept-gate-h1 (E2E-v1 Stage 2), recover the current state, next action, and stop conditions from the handoff and its authority source."
}
```

`gold2.json` (sha256 `bce8e7c1d10d91ebb8ed0f1d47f043cffc73a571dbb784e725bb2de1baaff794`;
정정 전 `gold.json` = `515a143e0f3f34547294474e2737deeb141acfcb2834f1b76cf6afe7eff4badc`):

```json
{
  "contract_version": "handoff-mcp-canary-gold-v1",
  "case_id": "CGH1-FREEZE-01",
  "handoff_path": "HANDOFF.md",
  "authority_paths": [
    "experiments/2026-08-23_e2e_v1_c_o1_cohort/PREREGISTRATION_STAGE2.md",
    "CLAUDE.md"
  ],
  "navigation_paths": [],
  "required_read_paths": [
    "HANDOFF.md",
    "experiments/2026-08-23_e2e_v1_c_o1_cohort/PREREGISTRATION_STAGE2.md",
    "CLAUDE.md"
  ],
  "state_code": "FROZEN_AWAITING_EXECUTION_APPROVAL",
  "next_action_code": "DISPATCH_FOLIO_ADAPTER_CONTROLS",
  "stop_condition_codes": [
    "NO_COHORT_WITHOUT_USER_APPROVAL",
    "NO_FROZEN_SURFACE_EDITS"
  ]
}
```

결과 파일 sha256(로컬 scratchpad, 저장소 미포함 — subject 출력 전문 포함):

| 실행 | gold | accepted | sha256 |
|---|---|---|---|
| 1차 | gold | False (F-H1, F-H2) | `6ab04f75369e7ed140d4977db8fc47923266e4a28779379df60c92c3e1baa156` |
| 3차 | gold | False (F-H2) | `a6e681c716d262a25d1dc0abdf6aebe103ef3cb484b40187bde579a9e04b5e82` |
| 6차 | gold2 | **True** | `1e5b36146294a3da5d4e05a09731cdf389fc6f689582adc47985b23468d78705` |
| 7차 | gold2 | **True** | `d9ad8e34245dd4e519e29c343003ffc64345560c264ec21ed450a244ca670e3a` |
| 8차 | gold2 | **True** | `1d06a6c6b8fb932b8e993912cd4d138bf885f0983c9688847631e39980303fd4` |

## 7. 남은 한계 (정직한 잔여)

1. **navigation 축 미시험** — §3. 별도 case 미작성
2. **authority 인용은 경로 수준 검사** — 의미 정합은 이번엔 사람이 손으로
   확인했다(§4). 채점기 자체는 허위 인용을 통과시킬 수 있다
3. **단일 subject 모델** — `gpt-5.6-sol` 1종. handoff가 다른 모델·다른
   검색 계층에서도 복원 가능한지는 미측정. 동결 코호트가 haiku를
   floor model로 잡은 것과 같은 논리를 여기에 적용하지 않았다
4. **`accepted`는 handoff 품질의 상한이 아니다** — 이 canary는 "zero-context
   독자가 상태 3종을 근거와 함께 복원할 수 있는가"만 본다
