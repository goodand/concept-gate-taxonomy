# ConceptGate Taxonomy

Developer: 탁재현 (goodand/concept-gate-taxonomy)

## Code Philosophy: Ponytail Rules

Before writing any code, traverse this decision ladder top-down. Stop at the first rung that solves the problem.

1. **YAGNI**: Does this need to exist at all? If not, skip it.
2. **Codebase reuse**: Already in this codebase? Reuse it.
3. **Standard library**: stdlib solves it? Use stdlib.
4. **Native platform**: Native feature covers it? Use it.
5. **Installed dependency**: Already-installed dep solves it? Use it.
6. **One-liner**: Can it be one line? Make it one line.
7. **Minimum code**: Only then write the minimum code that works.

The ladder runs AFTER you understand the problem, not instead of it. Read the code fully and trace the real flow before picking a rung.

### Safety (never cut) — hard constraints
- Input validation at trust boundaries
- Error handling that prevents data loss
- Security
- Accessibility

### 규칙이 충돌할 때의 우선순위 (5단)

위 사다리와 아래 Principles, 그리고 저장소 고유 규칙이 서로 다른 답을 낼 때
이 순서로 판정한다. **이 절이 생기기 전에는 순서가 추론이었고, 추론은
사람마다 달랐다.**

1. **Hard safety constraints** — 바로 위 목록(security, data-loss 방지,
   trust-boundary 검증, accessibility)
2. **Explicit user request** — 단 1과 충돌하지 않는 범위에서만
3. **저장소 고유 불변식** — worktree 손복사 금지, 단일 정본, 동결 규율 등
   아래에 명시된 것들
4. **Ponytail decision ladder** — 위 7단
5. **General principles** — fewest files, shortest diff, no abstraction 등

**`Explicit user request`가 왜 Safety 목록에서 빠졌는가**: 예전에는 그
목록 안에 있었다. 그러면 "worktree에 그냥 복사해"라는 요청이 3번(손복사
금지 불변식)을 이긴다 — 이 저장소가 없애려고 만든 실패 모드가 요청 한 줄로
되살아난다. 사용자 요청은 여전히 강력하지만 **hard safety 아래, 불변식
위**다.

**"안전을 위해 불변식을 깨야 한다"는 주장의 처리**: hard safety가 최상위인
것은 맞지만, `safety`라는 말이 불변식 우회 면허가 되어서는 안 된다.

> 안전 목적을 만족하는 **불변식과 양립하는 방법이 있으면 그것을 먼저
> 쓴다.** 그런 방법이 없을 때만 최소 범위의 명시적 예외를 허용하고, 그
> 예외를 기록한다.

예: 데이터 보존이 목적이면 다른 worktree에 정본 사본을 만들 것이 아니라
`git commit`/`stash`/patch/외부 backup으로 해결된다 — 이 경우 안전과 손복사
금지는 **실제로 충돌하지 않는다.**

**충돌을 없애는 것이 목표가 아니다 — 먼저 상위 목적을 확인하라.** 두 규칙이
논리적으로 부딪혀 보여도 **같은 상위 목적을 서로 다른 각도에서 지키고 있다면
둘 다 남긴다.** 위 사다리는 그런 경우에 어느 쪽을 먼저 시도할지를 정할 뿐,
진 쪽을 삭제하라는 뜻이 아니다.

실제 사례가 이 문서 안에 있다:

- `Fewest files` / `Shortest diff`(5번) vs `Subtree Assembly`(3번) — subtree는
  파일과 diff를 크게 늘린다. 그러나 둘의 상위 목적은 같다: **검증되지 않은
  새 코드를 최소화한다.** 하나는 "적게 써서", 하나는 "이미 검증된 것을
  가져와서". 그래서 둘 다 유효하고, 사다리는 순서만 준다.
- `No abstraction`(5번) vs subtree를 wrapper로 감싸라(3번) — 상위 목적은
  **subtree 경계를 오염시키지 않는 것**이고, 그 wrapper는 장식이 아니라
  경계 자체다.

규칙을 지우는 것은 **상위 목적까지 같지 않다고 확인됐을 때**만 한다. 확인 없이
"모순이니 하나 빼자"로 가면, 이 저장소가 비싸게 배운 규율이 정리라는 이름으로
사라진다.

### Intentional simplifications
Mark with `ponytail:` comments that name the ceiling and upgrade path:
```python
# ponytail: O(n^2) scan; upgrade to index if n > 1000
```

### Principles
- Deletion > Addition
- Boring > Clever
- Fewest files possible
- Shortest working diff wins
- No abstraction unless explicitly requested
- Bug fixes target root cause, not symptom

## Subtree Assembly

When writing code, prefer bringing in existing code as **git subtrees** and assembling from reusable parts.

- Before creating new modules, search for existing open-source implementations that can be added as subtrees
- When a feature maps to a well-known library/repo, `git subtree add` it rather than reimplementing
- Keep subtree boundaries clean: don't modify subtree code directly, wrap/adapt in project code
- Track subtree origins in this file under "Subtree Registry" below

### Subtree Registry

| Prefix | Remote | Branch | Purpose |
|--------|--------|--------|---------|
| `vendor/obo-relations` | oborel/obo-relations | master | part_of (BFO:0000050) / has_part (BFO:0000051) 표준 공리. Phase B `relation_hint` 검증. 핵심 파일: `core.obo` |

Subtree 갱신: `git subtree pull --prefix vendor/obo-relations https://github.com/oborel/obo-relations.git master --squash`

## Project Structure

**정본 소스는 `conceptgate/` 패키지 하나뿐이다. 배포 사본을 만들지 말 것.**
예전에는 루트와 `files/`에 같은 모듈이 두 벌 있었고, 한쪽만 고치면 다른 쪽 테스트가
옛 코드로 돌아 *거짓 통과*가 났다. 그 실패 모드를 없애려고 단일 패키지로 합쳤다.
새 모듈은 `conceptgate/`에 추가하면 wheel에 자동 포함된다(수동 목록 없음).

각 모듈이 무엇인지는 그 파일의 docstring이 말한다. `Dockerfile`이 JRE를
포함하는 이유만 여기 남긴다 — HermiT가 Java를 요구해서 Docker가 선택이 아니라
필수다. `conceptgate/data/gufo.owl`은 형식 변환 사본이고 해시가
`third_party/sources.lock.json`에 고정돼 있다.

**위 규칙은 `conceptgate/`만이 아니라 저장소 전역 자산 전부에 적용된다 —
worktree 사이로 파일을 손으로 복사하지 말 것.** worktree들은 **하나의 git
저장소를 공유**하므로 파일이 다른 worktree에 도달하는 정상 경로는 복사가 아니라
커밋 → 머지 → rebase다. 손으로 복사하면 위에서 없앤 그 실패 모드(사본 두 벌,
한쪽만 수정, 거짓 통과)를 정확히 되살린다. 2026-08-05 실측: repo 전역 게이트
([`test_guard_negative_coverage.py`](test_guard_negative_coverage.py))를 worktree마다 넣을 파일로 읽어 두 트리에
손으로 복사하려 했고, 세션 격리가 거부해서 분기가 생기지 않았다. 게이트·하네스
파일은 경로 독립으로 쓰고(`Path(__file__).parent`) **한 곳에 커밋해 전파시켜라.**
실험 폴더의 동명 모듈 중복은 동결 규율이 강제하는 예외이며, 새 파일에 그 예외를
확장 적용하지 않는다.

### 머지 게이트 — 단일 진입점

```bash
venv/bin/python scripts/run_gates.py  # exit 0 = FAIL 없음; 머지는 BLOCKED 없이 모든 gate가 PASS일 때만
```

**`exit 0`을 머지 조건으로 배선하지 마라.** exit code는 "FAIL이 있었는가"만
답한다 — BLOCKED는 exit code에 반영되지 않으므로(아래 PASS/FAIL/BLOCKED),
`exit 0`은 "머지해도 된다"가 아니라 "실패한 게이트는 없다"이다. 머지 판정은
출력의 BLOCKED 목록까지 읽어야 완성된다.

러너가 실행하는 것:

| 게이트 | 내용 |
|---|---|
| core pytest | `pytest -q` (루트, `experiments/` 제외) |
| experiment × N | `experiments/*/test_protocol.py`를 **실험마다 별도 프로세스**로 |
| test_server.py | MCP 서버 (fastmcp 필요) |
| qa_v7.py | 101/101 |
| concept_gate_v7 인라인 | 60/60 |
| fuzz_normalizer_types.py | 209, CRASH=0 |

**왜 단일 스크립트인가**: 실험 폴더들은 동결 규율상 `_cert_core.py`(6개
바이트동일)·`evaluate.py`(10개)·`_gen_prompts.py`(7개)를 같은 모듈명으로
중복 보유한다. 이걸 한 인터프리터에 모아 돌리면 먼저 로드된 쪽이
`sys.modules`를 선점해 **다른 실험이 남의 evaluator로 조용히 실행된다**
(실제로 발생했던 결함). 실험별 프로세스 분리가 유일하게 확장 가능한
해법이고, 새 실험은 아무 조치도 필요 없다. 상세 근거는
[`scripts/run_gates.py`](scripts/run_gates.py) 헤더 주석.

**PASS / FAIL / BLOCKED** — 정확한 계약은 `scripts/run_gates.py` 헤더가 정본:

| 상태 | 뜻 | exit code 기여 | 머지 |
|---|---|---|---|
| PASS | 게이트가 돌았고 통과 | 0 | 허용 조건 |
| FAIL | 게이트가 돌았고 실패. **결과를 못 낸 것도 FAIL**(모듈 누락으로 실패 메시지가 나도 마찬가지 — 침묵을 성공으로 읽지 않기 위해) | **1** | 차단 |
| BLOCKED | 게이트가 **시작조차 못 함**(`fastmcp`·`owlready2` 등 선택적 의존성 부재) | **없음** | **판정 보류 — 자동 허용 아님** |

`BLOCKED`는 "검증하지 못함"이지 "실패함"도 "성공함"도 아니다 — exit code에
반영 안 되므로 실행된 뒤 실패한 것과 섞으면 환경 의존 테스트 하나가 같은
suite의 실제 회귀를 가린다. 이 3값 구분은 이 저장소가 게이트 신뢰를 유지하는
방식이며, **검색 계층에도 같은 어휘를 쓴다**(아래 "무언가를 찾을 때" 절의
`rg-only`).

### 가드를 쓰면 음성 테스트가 함께 온다 — 이건 규율이 아니라 게이트다

`assert_*` 가드를 새로 쓰거나 고치면 **위반 입력을 `pytest.raises` 안에서
먹이는 테스트를 같은 변경에 넣어라.** 긍정 테스트만 있으면 정상 가드와 공허한
가드의 **관측값이 동일**해서 구별이 불가능하다 — `_h1a_policy.py`의 `assert_5`가
완전히 공허한 채로 긍정 테스트를 통과했고, 잡은 것은 suite가 아니라 외부
리뷰어였다.

[`docs/H1A_PROBLEM_ANALYSIS.md`](docs/H1A_PROBLEM_ANALYSIS.md)가 이 패턴(P1)을
**6건** 기록하고 [`docs/NEXT_SESSION_TRAPS.md`](docs/NEXT_SESSION_TRAPS.md)
§7.3이 "일곱 번째가 없다고 가정하지 마라"고 예고했는데 일곱 번째가 났다.
**"두 명제를 적어 대조하라"는 규율은 7/7 실패했다.** 그래서 기제로 옮겼다 —
`test_guard_negative_coverage.py`(루트)가 AST로 가드를 수집해 음성 테스트
없는 것을 실패시킨다. core pytest가 이미 수집하므로 배선은 없다.

도달 불가한 raise 경로처럼 음성 테스트를 정직하게 쓸 수 없는 경우가 있다.
그때 **모킹으로 통과시키지 말고** `KNOWN_UNPROVEN`에 이유와 담당을 적어라 —
모킹 기반 음성 테스트는 게이트를 초록으로 만들면서 아무것도 증명하지 않는다.
근거와 실측은 [`docs/HARNESS_KNOWHOW.md`](docs/HARNESS_KNOWHOW.md) §B4a.

## 설계 판정을 상신하기 전 — "아직 안 풀렸다"고 단정하지 마라

이 프로젝트는 형식과학에 가깝다(OWL/OntoClean 계열 검증, 실험 프로토콜
설계) 그리고 관행상 기존 구현·논문·저장소의 아이디어를 재사용해 개발한다
(위 Subtree Assembly). 이 둘을 합치면 새 설계 문제를 만났을 때 지켜야 할
규율이 하나 나온다: **모르는 것을 "미해결"로 단정하고 바로 새로 풀지 않는다.**

수학 오픈 문제 데이터베이스류 페이지들이 공유하는 관행이 이 규율의 원형이다
— 문제를 던지기 전에 "이미 누가 무엇을 풀었는지, 무엇이 아직 안 풀렸는지"를
먼저 밝히고, "여기 없는 관련 결과를 알면 덧붙여라"라고 명시적으로 청한다.
그 형식을 낳은 이유는 하나다: **모델(또는 사람)이 이미 있는 결과를 모른 채
재발명하거나, 모른다는 이유만으로 "안 풀린다"고 잘못 단정하는 것을 막는다.**
전문은 [`notes/research/prompt-design/open-problem-database-prompt-style.md`](../notes/research/prompt-design/open-problem-database-prompt-style.md).

**적용 — 새 설계 문제를 만들거나 DESIGN_REQUEST를 쓰기 전에:**

1. **먼저 확인**: 이 저장소에 이미 있는 구현(`conceptgate/`, `vendor/*`
   subtree), 과거 `DESIGN_DECISION*.md` 판정,
   [`docs/H1A_ISSUE_REGISTER.md`](docs/H1A_ISSUE_REGISTER.md) /
   `docs/H1A_PROBLEM_ANALYSIS.md` 같은 패턴 기록, skills-catalog에 이미 승격된
   knowhow가 같은 문제나 그 일부를 이미 다뤘는지부터 찾는다. `grep`만으로
   끝내지 말 것 — 위 섹션대로 backlink까지 따라간다.
2. **모른다고 "미해결"이라 쓰지 않는다.** DESIGN_REQUEST에 "이 문제는
   아직 다뤄지지 않았다"고 쓰려면, 무엇을 어떻게 찾아봤는지(검색어·읽은
   문서·확인한 판정 목록)를 먼저 적는다. 찾아보지 않고 단정하면, 이미 있는
   해법을 모르는 채 다시 만들거나 이미 내려진 판정과 충돌하는 새 설계를
   쓰게 된다 — 이 워크스페이스에서 실제로 두 번 일어났다(위 grep 섹션의
   실측 사례, 그리고 skills-catalog 얕은 검색이 이미 있던 패턴을 "0건"으로
   잘못 결론낸 사례).
3. **외부 판정자에게 미리 알려진 것을 다시 청하지 않는다.** 선행 판정
   (D-H1a-1~7, Q1~Q8 등)을 인용 형식으로 요청서에 embed하는 지금 관행이
   이미 이 규율을 부분 구현한다 — 계속 유지한다.
4. **찾은 뒤 새로 발견한 관련 자료가 있으면 요청서/등록부에 남긴다** — 그
   자료가 문제를 부분적으로든 완전히든 이미 풀었을 수 있다는 가능성 자체를
   기록에 남기는 것이 핵심이지, 반드시 새 자료를 찾아내야 한다는 뜻은 아니다.

## 외부 판정을 수신했을 때 — 프로토콜 전수 진행이 기본값이다

외부 설계 담당의 판정(`DESIGN_DECISION_*`)이나 조사 회신(`RESEARCH_RESULT_*`)이
도착하면 다음 네 단계를 **순서대로 전부** 밟는다:

```text
검증 설계  →  검증 설계의 적대적 검증  →  검증  →  저장
```

- **검증 설계**: 판정문의 주장 중 무엇을 어떤 근거(file:line·실측·논리)로
  확인할지 항목화한다. 판정이 우리 주장을 기각했다면 "우리가 실제로 그렇게
  썼는가"와 "구제 경로가 있는가"를 반드시 항목에 넣는다.
- **설계의 적대적 검증**: 그 항목 목록 자체를 **다른 관점**(haiku 조사 agent,
  또는 `adversarial-review` 스킬의 근거 축 분할)이 공격한다 — 빠진 항목,
  판정을 우리 쪽에 유리하게 읽은 항목, "없다"를 "안 찾아졌다" 대신 쓴 항목.
- **검증**: 항목대로 재실측한다. 부재 판정은 음성 대조 없이 쓰지 않는다.
- **저장**: verbatim + `VERBATIM_SHA256`(D-30 이후: 끝 개행 제외) + 우리 수신
  검증 절 + 색인 행 + HANDOFF §0 갱신. 그래프 연결은 만들 때 한다.

**단계를 건너뛸(PASS) 수 있다. 단, 건너뛴 사실과 이유를 그 문서에 명시한다.**
"시간이 없어서"는 이유가 아니다. 이유의 예: 판정이 우리 주장을 하나도 기각하지
않았고 사실 확인 항목이 0건이다 / 동일 판정문의 재발송(sha256 일치)이다.
명시 없이 건너뛴 것은 **안 한 것**으로 간주하고 HANDOFF `next_action_code` 에
복구 항목으로 올린다.

**왜 이렇게까지 하나.** 2026-08-30 D-37 수신 때 `설계의 적대적 검증` 을
건너뛰고 설계→검증으로 갔다. 그 판정은 우리 상신문 §4 의 추론을 **기각**한
것이었다 — 즉 우리가 스스로 못 본 방식으로 우리가 틀렸다는 것을 보여준
판정이었고, 그 판정에 대한 우리 검증을 단일 관점으로 둔 것은 **정확히 잘못된
자리에서 아낀 것**이다. 건너뛴 사실은 정본 §8 이 자백했고 HANDOFF 가 복구
항목으로 올렸다. 그 뒤 사용자 지시: "프로토콜을 전수 진행하는 것을 Default로
두되, PASS할 때는 그 이유를 명시하도록 해라."

## 무언가를 찾을 때 — grep으로 끝내지 마라

**`rg`/`grep`은 "무엇이 어디 있나"엔 충분하지만 "이건 이미 결정됐나"엔 답하지
못한다.** 결정 문서의 **경로(파일명)**가 네 질문의 어휘를 하나도 포함하지
않을 수 있기 때문이다. 2026-08-01 실측: 활성 폴더 정리를 설계하며 "디렉토리
정리 / DESIGN_DECISION / canonical"로 **파일명**을 훑었으나 이미 채택된 결정
([`notes/audits/vault/symlink-vs-moc-2026-07-30.md`](../notes/audits/vault/symlink-vs-moc-2026-07-30.md))이 안 걸렸다 — 그 파일의
**경로**가 저 키워드를 하나도 포함하지 않기 때문이다(2026-08-02 재확인:
`find notes -iname "*canonical*" -o -iname "*design_decision*"`가 이 파일을
반환하지 않음). **본문**에는 `canonical`이 8회 등장한다 — 본문 grep이었다면
후보로는 걸렸을 것이나, 같은 조건에 걸리는 파일이 7개라 여전히 순위를 매길
근거가 없었을 것이다. 그 사이 쓴 설계는 채택된 결정과 정면 충돌했다.
**backlink 1홉(정확히 2건: MOC 자신 + 이 감사 문서)으로 나왔다.** 상세 재현:
`docs/H1A_PROBLEM_ANALYSIS.md` §4 W-B.

검색이 빗나가면 **키워드를 바꾸지 말고 그래프를 따라가라**(실측 recall:
0.688 → pool refill 0.812 → graph walk 0.958 → 1.000):

```bash
obsidian read      path="notes/…/문서.md"     # 반드시 path=, file=<basename> 금지
obsidian backlinks path="…" counts format=json
obsidian links     path="…"
```

`file=<basename>`는 worktree 간 동명 파일(`HANDOFF.md` 등)을 조용히 잘못
해석한다. CLI를 못 쓰면 backlink를 **추정하지 말고** "rg-only"라고 명시하라.

**`rg-only`의 종단 상태는 `BLOCKED`다** — 머지 게이트와 같은 어휘를 쓴다
(위 PASS/FAIL/BLOCKED 표). backlink traversal이 필요한 판정에서 CLI가
unavailable이면 그 검증은 실패한 것도 성공한 것도 아니라 **얻지 못한** 것이다.

```
CLI 가능   → graph traversal → PASS
           → "이미 결정됐다/안 됐다" 완결 판정 허용

CLI 불가   → rg-only → BLOCKED
           → 잠정 분석은 계속해도 된다
           → **"미해결", "기존 결정 없음", "새 설계가 필요함" 같은
             완결적 부재 판정은 내리지 않는다**
```

부재 판정만 막고 작업 자체는 막지 않는 이유는 위 §"규칙이 충돌할 때의
우선순위"와 같다 — 도구 하나가 없다고 전부 멈추는 것이 목적이 아니라,
**확인하지 못한 것을 확인한 것처럼 말하지 않는 것**이 목적이다.

절차 전문은 이미 있고 검증됐다. 다시 만들지 마라 —
`../.vault-harness/vault-md-retrieval/AGENT_PROMPT.md`(Required Procedure),
`multiturn_retrieval.py "QUERY" --policy recall-first-v2 --max-turns 4`.
탐색 레시피와 함정 4개는 [`docs/WORKSPACE_NAVIGATION.md`](docs/WORKSPACE_NAVIGATION.md).


## md 문서를 만들 때 — 그래프에 연결해서 만들어라

위 "무언가를 찾을 때" 절은 **읽는 쪽** 규율이다. 이 절은 **쓰는 쪽**이다:
backlink traversal로 찾을 수 있게 만드는 책임은 문서를 만든 사람에게 있다.

2026-08-24 실측: 판정 사슬 D-27·D-28·D-29, 조사 회신 3건, 방금 상신한 요청서
— **7건이 backlink 0**이었다. 전부 실재하고 전부 인용되고 있었지만, 참조가
백틱 경로(`` `docs/X.md` ``)나 식별자 토큰("D-29")뿐이어서 **다른 파일에서의
언급이 0**이었다. zero-context agent가 handoff에서 graph를 걸어 나오면 그
문서들에 **도달하지 못한다.** 파일이 있는 것과 그래프에 있는 것은 다르다.

새 md를 만들 때 세 가지를 한다:

1. **진입점에서 1홉으로 도달 가능하게 한다.** 계열 문서는 색인 노트를
   두고(`docs/RULING_CHAIN_INDEX.md`가 그 예) 거기에 행을 추가한다.
2. **인접 링크를 잇는다** — 헤더에 `이전`/`다음`. 색인만 있으면 색인이
   사라질 때 사슬이 끊기고, 인접 링크만 있으면 중간부터 읽는 사람이 전체를
   못 본다. 둘 다 둔다.
3. **동명 파일은 반드시 경로 한정형으로 링크한다.**
   이 vault의 실측: `HANDOFF` **46개**, `H1A_PROBLEM_ANALYSIS` **9개**.
   `[[HANDOFF]]`는 조용히 다른 worktree를 가리킨다 —
   `[[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]` 형태로 쓴다.
   링크를 넣기 전에 `find . -name "<name>.md" | wc -l`로 세라.

**외부로 나가는 문서는 항법 줄을 본문 끝에 둔다.** 요청서(설계 판정자·조사
agent가 받는다)는 "저장소 접근 없음"을 전제로 쓰인다 — 그 문서 최상단에
`[[wikilink]]`를 넣으면 수신자가 **열 수 없는 링크**가 첫 화면을 차지한다.
2026-08-24 실측: 일괄 삽입이 Q30 상신서의 3행에 항법 줄을 넣어 "판정자 전제:
저장소 접근 없음" 바로 위에 놓였다(요청서 18건 동일). 본문 끝으로 옮겨
그래프 도달성은 유지하고 수신자의 진입점은 깨끗하게 뒀다.
**규약을 적용할 때 문서의 수신자를 먼저 보라** — 그래프 편의가 문서의 용도를
이기면 안 된다.

**verbatim 정본이 있는 문서에 링크를 넣을 때**: `VERBATIM-BEGIN`/`END`
**경계 바깥**(헤더)에만 삽입하고, 삽입 후 `VERBATIM_SHA256`을 재계산해
기록값과 같은지 확인한다. 구 규약 문서(D-19~D-23)의 "본문 sha256"은 파일이
아니라 **수신 원문**의 해시이므로 헤더 편집이 무효화하지 않는다 — 그러나
그것도 확인한 뒤에 편집하는 것이 순서다.

**evidence-evaluator MCP(zero-context 평가기)는 handoff 시점의 도구다.**
문서를 만들 때마다 돌리지 않는다 — 인계하는 그 시점에 한 번, 제대로 돌린다
(실측 근거: `docs/HANDOFF_EVALUATION_20260823.md`, 결함 2건 적발).

**위임 구현의 모델**: Agent tool은 `model`만 받고 `effort`가 없다. 프로토콜이
`(Haiku, xhigh)`를 명해도 effort를 실을 수 없으므로, **구현 위임은 Sonnet 5**
를 쓴다(조사·탐색은 Haiku로 충분하다는 것이 지금까지의 실측이다).

## Git

- Do NOT commit without explicit permission

## 실행 승인 — trial/코호트 디스패치는 매번 별도 승인

**동결된 사전등록이 존재해도 그것이 실행 허가는 아니다.** trial·코호트·
adapter control의 Agent/Workflow 디스패치는 커밋과 동일하게 **매번 명시적
사용자 승인**을 받는다. 사전등록서는 *무엇을* 측정하는지의 정본이고, *언제
실행하는지*는 정본이 아니다 — 이 규칙이 그 공백의 정본이다.

근거(실측, 2026-08-23): Stage 2 handoff를 zero-context 평가기로 3회 검증한
결과, "사용자 승인 없이 코호트 실행 금지"라는 정지 조건이 **handoff에만
있고 어떤 정본에도 없어서** 독립 독자가 3/3 근거를 찾지 못했다. 정지 조건에
정본이 없으면 다음 세션이 그것을 폐기할 수 있다.
