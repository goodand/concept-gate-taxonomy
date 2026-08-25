# 배포 브랜치로 수리 이관 — cherry-pick 기록 (2026-08-25)

- 성격: **운영 로그.** 측정 계약을 바꾸지 않는다.
- 수리 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]] 계열 커밋
  `2c8df63` → 배포 브랜치 `claude/ontoclean-gufo-handoff-7cmq0v` 의 `17da1da`
- 관계 구분 결함의 내용은 그 커밋 메시지가 정본이다.

## 1. 왜 전체 머지가 아니라 cherry-pick 인가

subagent 4축(haiku 2 · sonnet 2, 1축은 지출 한도로 실패 후 haiku 재투입)과
lead 재실측으로 정한 것이다.

| 축 | 결정적 수치 |
|---|---|
| 분기 | SRC가 DST보다 **251커밋** 앞서고 **DST가 35커밋** 앞선다. 전체 diff **494파일 · +118,409/−84,111** |
| 배포 범위 | Dockerfile COPY 는 `conceptgate/`·`vendor/`·`requirements.txt`·`THIRD_PARTY_NOTICES.md`·`licenses/` 뿐 — **`experiments/`·`docs/`·`test_*.py` 는 이미지에 안 들어간다** |
| 전체 머지 충돌 | **7파일** — `CLAUDE.md`·`docs/HANDOFF.md`·`docs/H1A_ISSUE_REGISTER.md`·`test_guard_negative_coverage.py` + H1a 실험 3파일 |
| 전체 머지가 이미지에 넣을 것 | SRC에만 있는 `conceptgate/` **10파일 3,332행**(`cg_sbn_adapter`·`cg_fol_adapter`·`cg_oracle_adapter`·`server_o1_scope` 등) — 배포에서 **검증된 적 없는** 코드 |
| cherry-pick | 수리 4파일이 `2c8df63^` 과 DST 에서 **바이트 동일** → 충돌 0(세 방법 독립 확인) |

**결정적 근거 한 줄**: 배포 이미지는 `conceptgate/` 만 먹는데 수리는 그 안의
3파일이다. 3파일을 옮기려고 494파일을 움직일 이유가 없고, 전체 머지는
**이미지에서 작동할 수 없는 `server_o1_scope.py`**(그것이 의존하는
`experiments/` 가 COPY 되지 않는다)까지 실어 보낸다.

## 2. cherry-pick 이 안전한 전제 — 전부 확인했다

- 수리 4파일이 `2c8df63^`↔DST **바이트 동일**(sha256 4쌍 일치)
- `RELATION_CROSSWALK` 가 두 브랜치에서 동일 → 유도되는 `HINT_TO_RELATION` 동일
- 헬퍼 `_err`·`map_relation`·`_span_evidence` 가 같은 서명으로 존재
- **행 수 중립 제약 성립**: `concept_gate_v7.py` 가 양쪽 **2426행**이고,
  H1a 실험 fixture 의 `ev3` 가 DST 에서도 같은 파일 **1192–1193행**을 인용한다.
  이 파일 편집이 행 수를 바꾸면 그 실험이 깨진다(SRC 에서 실제로 54건 깨뜨렸다).

## 3. push 는 이미지에 무엇을 바꾸는가 — **제 수리뿐이다**

`origin` 의 그 브랜치는 `c1b6af2`(2026-07-25)에 있었고 로컬이 **143커밋**
앞서 있었다. 즉 push 는 144커밋을 올린다. 그러나 그 144커밋의 파일 분포는:

```text
experiments 281 · docs 38 · scripts 4 · conceptgate 3 · 루트 테스트 2
```

**`conceptgate/` 변경 3파일이 정확히 이 수리의 파일들이다.** 나머지는 전부
COPY 범위 밖이므로 **이미지에 닿는 변경은 수리뿐**이다. 도구 표면도 일관된다
(origin/DST 11 · 로컬 DST 11 · 배포본 실측 11).

## 4. DST 의 게이트가 붉은 이유 — **수리 때문이 아니다**

cherry-pick 후 DST 에서 `run_gates.py` 가 `core pytest 15 failed` 를 냈다.
분해하면:

| 실패 | 원인 | 수리와 관계 |
|---|---|---|
| 2건 | `owlready2` 부재 · `test_guard_negative_coverage` | **cherry-pick 이전에도 실패**(별도 트리에서 `2 failed, 116 passed` 확인) |
| 2건 | 위 둘의 중첩 worktree 사본 | 동일 |
| **11건** | **중첩 worktree 그림자** | **가짜 실패** |

**11건의 정체**: `concept-gate-taxonomy/.claude/worktrees/claude-provider-adapter/`
가 자기 `conceptgate/` 와 `test_cg_normalizer.py` 를 갖고 있는데 DST 의
`pytest.ini` `norecursedirs` 가 `vendor .git __pycache__ experiments` 만
제외하고 **`.claude` 를 제외하지 않는다.** 그래서 수집 시 어느 쪽이 먼저
로드되느냐에 따라 `sys.modules` 가 선점된다.

증명:

```text
전체 수집            15 failed, 233 passed
--ignore=.claude      2 failed, 128 passed     ← 내 11건 전부 통과
단독 실행             1 passed                  ← 같은 테스트
직접 import           conceptgate/cg_normalizer.py (올바른 파일, 수리 포함)
```

**이 저장소 `CLAUDE.md` 가 실험 폴더에 대해 기록한 그 실패 모드와 같다** —
"먼저 로드된 쪽이 `sys.modules` 를 선점해 다른 실험이 남의 evaluator 로 조용히
실행된다". 거기서는 실험별 프로세스 분리로 풀었고, 여기서는 중첩 worktree 가
같은 일을 한다.

**남은 부채**: DST 의 `pytest.ini` `norecursedirs` 에 `.claude` 를 추가하면
그 브랜치의 게이트가 읽을 수 있게 된다. 이번 범위 밖이라 하지 않았다 —
승인받은 것은 수리 이관이었다.

## 5. 배포 반영 확인 방법

`render.yaml` 에 `autoDeploy` 가 없고 `.github/workflows` 도 없다 — **Render
대시보드 설정이 정본**이다.

**실측(2026-08-25): 자동배포가 켜져 있다.** push 직후에는 옛 동작이었고 몇 분
뒤 재확인하니 반영됐다. 즉 **저장소에 흔적이 없다는 것과 꺼져 있다는 것은
다르다** — 조사에서 "autoDeploy 흔적 0건"까지가 확인 가능한 전부였고, 켜짐
여부는 대시보드 또는 **실제 배포본 관찰**로만 알 수 있다.

확인 호출(세션 3단: `initialize` → `notifications/initialized` → `tools/call`,
응답은 SSE `data:` 접두):

```json
assemble_concepts {"bundle":{"concepts":[{"name":"dog","features":[
  {"label":"tail","relation_hint":"component_of","evidence_text":"A dog has a tail."}]}]}}
```

| 판정 | 기준 |
|---|---|
| **반영됨** | `type == "structural_composition"` **그리고** claim 이 `tail --component_of--> dog` |
| 아직 | `type == "essential_feature"` **그리고** `dog --is_a--> tail` |

**2026-08-25 실측 결과 — 반영 확인**:

```text
type=structural_composition · claim=tail --component_of--> dog   ← 수리 반영
relation_hint="has_part"    → ok=False, UNKNOWN_RELATION_HINT     ← 침묵 붕괴 차단
```

두 번째 줄이 중요하다 — 표에 없는 hint 가 **조용히 is_a 가 되지 않고 허용
목록을 알려주며 정지**한다. 배포본에서 그 경로가 닫혔다.

방향까지 보는 이유: 부분-전체는 **feature 가 주어**다(Winston: pedal
component_of bike). 방향이 뒤집히면 다른 결함이다.

## 6. 별건 — 배포본이 토큰 없이 열려 있다

`render.yaml` 이 `MCP_API_TOKEN` 을 `generateValue: true` 로 만들고
`conceptgate/server.py:194` 가 "설정돼 있으면 Bearer 검증"이라고 하는데,
**Authorization 헤더 없이 `initialize`·`tools/call` 이 HTTP 200 으로 통과한다**(실측).

**원인 확정(2026-08-25): 코드가 아니라 배포 서비스의 환경변수 부재다.**
로컬에서 `MCP_TRANSPORT=http PORT=8931 MCP_API_TOKEN=secret-test-token` 으로
띄우고 실측했다:

```text
인증 없이 tools/list  → {"error":{"message":"Unauthorized: missing Bearer token"}}
올바른 토큰으로       → 도구 13개
```

**미들웨어는 정상 작동한다.** `render.yaml` 의 `MCP_API_TOKEN:
generateValue: true` 는 **그 blueprint 로 서비스를 생성할 때만** 적용되는데,
`concept-gate-taxonomy-docker` 는 대시보드에서 Docker 런타임으로 만들어졌으므로
그 변수가 생성된 적이 없다.

**수리**: Render 대시보드 → 그 서비스 → Environment 에 `MCP_API_TOKEN` 추가.
그 뒤 클라이언트는 `Authorization: Bearer <값>` 을 보내야 한다. 현재 Desktop 에
등재된 것은 로컬 `o1-scope` 와 `evidence-vault-mcp` 뿐이라 이 배포본을 쓰는
클라이언트는 없다 — 지금 켜는 것이 가장 싸다.

**부수로 발견한 코드 결함(잠복)**: `_check_token` 의 docstring 은
"fail-closed: HTTP 요청인데 헤더를 못 읽으면 거부"라고 하는데 실제 코드는
예외 시 `return` 한다 — 즉 **통과**시킨다. HTTP 에서 헤더 읽기가 실패하는
경로가 지금은 안 나타나므로(위 실측) 당장 문제는 아니나, **주석이 코드와
반대**다. 고치려면 transport 를 보고 HTTP 일 때만 거부해야 한다.
