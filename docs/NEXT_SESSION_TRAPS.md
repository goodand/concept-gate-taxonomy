# 다음 세션 실행 함정 — unknown unknown 줄이기

- 작성: 2026-08-02 (Q5~Q8 적용 + 3차 독립 리뷰 + Q9 상신·판정 도착 세션의 종료 시점)
- 문서 종류: **운영 로그**(`WORKSPACE_NAVIGATION.md` §2)
- 독자: **이 저장소에서 실제로 명령을 실행하려는 새 세션.** 상태를 알고
  싶으면 `HANDOFF.md`, 이슈 이력은 `H1A_ISSUE_REGISTER.md`, 패턴은
  `H1A_PROBLEM_ANALYSIS.md`, 재사용 노하우는 `HARNESS_KNOWHOW.md`다.

---

## 0. 이 문서를 만들면서 발견한 것 — 문제는 "없음"이 아니라 "닿지 않음"

이 문서를 쓰기 전에 "새 세션이 모를 것"을 나열한 뒤, **하나씩 기존 문서에
이미 있는지 검색했다**(그 규율 자체는 `CLAUDE.md`의 "설계 판정을 상신하기
전 — 아직 안 풀렸다고 단정하지 마라"에 있다). 결과:

| 내가 "새 세션은 모를 것"이라 적었던 것 | 실제 |
|---|---|
| 게이트의 `1 failed`가 정상이라는 것 | **이미 문서화됨** — `HANDOFF.md` §9 "검증 명령"에 30행짜리 상세 서술 |
| 가드가 참인데 틀린 명제를 검사한다는 패턴 | **이미 문서화됨** — `HARNESS_KNOWHOW.md` B4 |
| 제작자는 자기 결함을 못 본다 | **이미 문서화됨** — `HARNESS_KNOWHOW.md` B5 |
| `notes/` inbox를 확인해야 한다는 것 | **이미 문서화됨** — `DESIGN_workspace_file_placement.md` §6 검증 블록 |

**넷 다 이미 쓰여 있었는데, 그중 어느 것도 "필요한 순간에 보이는 자리"에
있지 않다.** `HANDOFF.md`는 920행이고 게이트 서술은 685행이다 — 새 세션이
5분째에 `run_gates.py`를 돌릴 때 아직 읽지 않았을 자리다. inbox 확인
명령은 설계 문서의 검증 절에 묻혀 있다.

> **그러므로 이 문서의 성격**: 새 사실을 쌓는 문서가 **아니다.** 실행
> 순간별로 "지금 이걸 하려는 참이면 이걸 먼저 알아야 한다"를 모으고,
> 전문이 어디 있는지 가리키는 **도달성 계층**이다. 이 문서와 원문이
> 어긋나면 **원문이 옳다.**

이것은 `H1A_PROBLEM_ANALYSIS.md` P5·P8의 세 번째 변종이다 — P5는 "못
찾음", P8은 "찾았는데 문맥 없이 읽음", 이것은 **"쓰여 있는데 그 순간에
읽지 않음"**이다. 세 가지 모두 "문서가 존재한다"가 "지식이 전달된다"를
의미하지 않는다는 같은 결론으로 간다.

---

## 1. 첫 10분 — 순서대로

### 1.1 `notes/` 루트에 새 판정문이 왔는지 **먼저** 본다

```bash
ls /Users/jaehyuntak/Desktop/Project_in_progress/notes/*.md
```

**외부 설계 판정은 알림 없이 파일로 도착한다.** 채팅으로 통지되지 않고,
저장소에도 자동 반입되지 않는다. 이번 세션은 Q9 판정이 도착한 것을
**Phase 6 잡무를 하다가 우연히** 발견했다 — 그 전 30분 동안 "판정 대기
중"이라고 여러 번 서술했는데 이미 도착해 있었다.

- `notes/` 루트에 있고 frontmatter가 없으면 = **미처리 신규 도착**
- `notes/projects/concept-gate/experiments/h1a/` 밑에 있고 frontmatter가
  있으면 = 정리 agent가 이미 처리한 것
- 2026-08-02 종료 시점 미처리분: `DESIGN_DECISION_H1A_REVIEW_BLOCKERS.md`
  (내용은 저장소에 반입 완료, notes 쪽만 미정리),
  `DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`(**Q9 — 저장소 반입 자체가
  미완**)

### 1.2 어느 worktree에 있는지 확인한다

```bash
git rev-parse --show-toplevel && git branch --show-current
```

기대값: `.../concept-gate-h1-wt` / `codex/h1-source-authority`.

`../concept-gate-e2.2-wt`에도 H1a 파일이 **25개 중복**돼 있다(분리 이전
이력 공유). 저쪽을 편집하면 **조용히 아무 효과가 없다** — 이쪽 테스트는
그대로 통과하고, 게이트도 그린이고, 바뀐 건 아무것도 없다. 실패가 아니라
무반응이라 알아채기 어렵다.

### 1.3 게이트를 돌리고 — `1 failed`를 **정상으로 읽는다**

```bash
python3 scripts/run_gates.py
```

기대값(2026-08-02 종료 시점):

```
[FAIL] core pytest        1 failed, 77 passed, 3 skipped
[ok  ] e2.4               118 passed          ← 이 숫자가 불변식
[ok  ] h1a                106 passed, 1 skipped
[-- ] test_server.py      optional dependency missing: fastmcp
  7 passed, 1 failed, 1 blocked
```

**그 `1 failed`는 `test_cg_obligations.py::test_registered_handlers_resolve`
이고, `owlready2` 미설치로 인한 기존 red다. 당신이 낸 게 아니다.** 이
저장소는 3곳에서 `pytest.importorskip("owlready2", ...)` 관례를 쓰는데 이
테스트만 예외라서 BLOCKED가 아니라 FAIL로 잡힌다 — **의도된 동작**이다
(게이트 러너는 "실행된 뒤 실패"를 FAIL로 분류한다. `CLAUDE.md` "PASS /
FAIL / BLOCKED" 참조).

전문: `HANDOFF.md` §9 "검증 명령"(`grep -n owlready2 docs/HANDOFF.md`).
core 테스트 파일이라 승인 없이 수정하지 않았다.

**내가 낸 것과 구별하는 법** — 이번 세션이 쓴 방법:

```bash
git stash -u && python3 scripts/run_gates.py; git stash pop
```

### 1.4 세 문서를 **다 읽는다** — 하나만 읽으면 그림이 틀린다

| 문서 | 담는 것 | 이것만 읽으면 놓치는 것 |
|---|---|---|
| `HANDOFF.md` | 지금 상태·다음 행동·읽을 문서 전수 목록 | 왜 그렇게 됐는지 |
| `H1A_ISSUE_REGISTER.md` | 시간순 이슈 + 검증 근거 | 반복 패턴 |
| `H1A_PROBLEM_ANALYSIS.md` | 패턴별 단면(P1~P8) | 언제 무엇이 있었나 |

---

## 2. 명령이 조용히 거짓말하는 지점 (이번 세션 실측)

### 2.1 `qualify_fixture`에 잘못된 `repo_root`를 주면 **예외가 아니라 `status: 'failed'`**

```python
m = surface.qualify_fixture(fx, '.', run_tests=False)   # 잘못된 repo_root
# → 예외 없음. m['status'] == 'failed'
# → 이어서 build_model_payload가 내는 말:
#    SurfaceError: qualification status is 'failed', not 'passed'
```

**이 메시지를 그대로 믿으면 fixture가 깨졌다고 결론 낸다.** 실제로는
evidence locator가 잘못된 경로 기준으로 해석돼 `locator_resolved: False`가
된 것뿐이다. 이번 세션이 프롬프트를 렌더해 보려다 정확히 여기에 걸렸다.

올바른 호출:

```python
REPO_ROOT = Path('.').resolve().parent.parent   # 실험 폴더 기준 2단계 위
m = surface.qualify_fixture(fx, REPO_ROOT, run_tests=False)
```

진단법: `m['evidence_checks'][0]['locator_resolved']`가 `False`면 fixture
문제가 아니라 **경로 문제**를 먼저 의심하라.

### 2.2 `git diff --stat`은 rename에도 삽입 줄 수를 보여준다 — `--numstat`을 써라

Phase 5에서 `git mv` 6건이 내용 변경 0인지 확인해야 했는데:

```bash
git diff --cached --stat      # "624 +++++..." 처럼 보인다 — 오해 유발
git diff --cached --numstat   # "0  0  {old => new}" ← 이것이 실제 증거
```

`git log --stat`의 `rename ... (100%)`도 같은 역할을 한다. **`--stat`만
보고 "내용이 바뀌었나?" 하고 되돌리지 마라.**

### 2.3 하위 디렉토리로 옮긴 테스트를 pytest가 수집하려 든다

`superseded/`로 옮긴 `test_h1a_diag*.py`는 `HERE / "_h1a_surface.py"`처럼
**자기 디렉토리 기준 상대 경로**로 형제 모듈을 로드한다. 옮기면 그 경로가
깨져 **수집 단계에서 에러**가 나고, 실험 전체 게이트가 FAIL이 된다.

해법은 `superseded/conftest.py`의 `collect_ignore`다(이미 있음).
**은퇴 파일의 내부 import를 고치지 마라** — 그러면 "한때 통과했던 역사적
아티팩트"라는 보존 목적 자체가 깨진다.

### 2.4 문자열 뮤테이션이 조용히 no-op일 수 있다

이전 세션 실측: `json.dumps` 기본 separator는 `": "`(콜론+공백)인데
`.replace('"type":"x"', ...)`로 공백 없이 찾아서 **아무것도 치환되지
않았고**, 그런데도 테스트는 통과했다. 뮤테이션 테스트를 쓸 땐 항상:

```python
assert rebuilt != original          # 치환이 실제로 일어났는가
assert text.count(needle) == 1      # 정확히 한 번인가
```

관련: `HARNESS_KNOWHOW.md` C절의 `__pycache__` 오염 항목 — 뮤테이션 검증
사이에 `rm -rf __pycache__`가 필요할 수 있다.

---

## 3. H1a 고유 함정

### 3.1 `DESIGN_DECISION_PATH`라는 상수 이름이 **거짓말한다**

```python
# _h1a_contract.py:72
DESIGN_DECISION_PATH = HERE / "h1a_prompt_template.md"
```

2026-08-02 이전에는 이 상수가 실제로 `DESIGN_DECISION_H1a_prompt_surface.md`
를 가리켰다. Q5·Q6.1·Q7이 template을 셋으로 나눠 수정해야 해서 template을
자기 파일로 분리했는데, **상수 이름은 그대로 뒀다.**

귀결 두 가지:

- 상수 이름으로 "어느 파일이 프롬프트 원본인가"를 판단하면 틀린다
- **`DESIGN_DECISION_H1a_prompt_surface.md`를 편집해도 이제 아무 효과가
  없다.** 예전 지식으로 판정문을 고쳐 프롬프트를 바꾸려 하면 조용히
  실패한다(테스트도 그대로 통과한다)

지금 어느 판정문이 코드 입력인지 확인하는 법(`WORKSPACE_NAVIGATION.md`
§3에도 등재):

```bash
grep -rn 'HERE / "DESIGN_DECISION\|Path([^)]*"DESIGN_DECISION' experiments/*/[_a-z]*.py
# 2026-08-02 현재: 빈 결과 = 판정문 중 코드 입력 없음
```

### 3.2 tripwire를 추가하면 **precision 비용**이 붙는다

`RESIDUAL_TRIPWIRES_EN`/`_KO`에 어구를 더할 때, 그 어구가 **깨끗한
template에 정상적으로 등장하지 않는지** 반드시 확인하라. 실측 사례 둘:

- `"outside"` — template의 `any fields outside h1a_observation_v1`에 정상
  등장. 그래서 맨 단어가 아니라 `"outside your scope"` 같은 구로만 매칭
- `"liveness"` — **Q7의 warrant 규칙 자체가** tie-breaker 금지 목록에서
  `...recency, authority, liveness, or outside knowledge...`라고 쓴다.
  양 arm 공통이므로 맨 단어로 잡으면 깨끗한 template이 실패한다. 그래서
  `"출처의 liveness"`(KO) / `"liveness of"`(EN)로 좁혔다

추가 후 즉시:

```bash
python3 -m pytest -q test_h1a_contract.py -k "precision or clean_template"
```

**그리고 알아야 할 한계**: 이 가드는 **닫힌 어구 열거**라 원리상 완전
봉쇄가 불가능하다. 3차 리뷰가 의역 3종으로 이를 실증했고, 그 사실을
`_h1a_contract.py` 주석에 명시해 뒀다. "가드 통과"는 "위험 없음"이 아니라
**"이 열거가 잡을 수 있는 범위 안엔 없음"**이다.

### 3.3 `E2.4 118`은 불변식이다

E2.4는 **종료된 실험**이고 그 테스트 수가 바뀌면 동결을 깬 것이다. H1a
작업 중 E2.4 숫자가 118이 아니게 되면 즉시 멈추고 원인을 찾아라. H1a가
E2.4의 `_surface.py`·`contract_prompt.md`를 **읽기 전용으로** 참조하기
때문에 실수로 건드릴 경로가 실재한다.

### 3.4 payload 형태가 2026-08-02에 바뀌었다

Q6=A 이후 모델이 보는 것은:

```json
{"concept_feature_pair": {"concept": "칼", "feature": "철",
                          "evidence_refs": ["ev1", "ev3"]},
 "evidence_items": [ ... ev1(doc), ev3(code) ... ]}
```

`candidate_concepts`도, `type` 필드도 **없다**. 예전 문서·예전 리뷰·예전
커밋 메시지에 나오는 `"type": "structural_composition"` 형태를 현재
상태로 착각하지 마라. `ev2`도 Q8=B로 제거됐다(현재 증거 2건).

---

## 4. 판정문을 저장소로 반입할 때 (Q9이 바로 이 작업이다)

이번 세션이 **하지 못하고 넘긴** 유일한 실행 항목이다. 절차:

1. **파일명 대소문자를 맞춘다.** `notes/`는 `H1A`(대문자), 저장소 관행은
   `H1a`(소문자 a). 형제 4개가 전부
   `DESIGN_DECISION_H1a_<scope>.md`이므로 Q9도
   `DESIGN_DECISION_H1a_evidence_symmetry.md`로 반입한다
2. **바이트 동일성을 확인한다.** 반입은 복사이지 편집이 아니다
   ```bash
   diff <(sed '/^---$/,/^---$/d' notes/원본.md) 저장소/사본.md   # frontmatter 제외 비교
   sha256sum 양쪽
   ```
   기존 미러들의 드리프트 실측치는 309~338바이트이고 **전부 frontmatter**
   였다 — 본문이 다르면 반입이 잘못된 것이다
3. **notes 원본은 지우지 않는다.** 미러 + `canonical:` 포인터가 의도된
   패턴이다(`DESIGN_workspace_file_placement.md` §1)
4. **판정문은 원문 보존 대상** — 반입 후 편집 금지. Q9.1이 준 L3 문구를
   `PREREGISTRATION.md`에 옮길 땐 **의역하지 말고 그대로** 넣는다(판정문이
   "exact limitation text"라고 명시)

---

## 5. 독립 리뷰를 다시 돌린다면 — 실측으로 효과가 있던 형태

3회 모두 실제 결함을 찾았다(1차 blocker 1, 2차 blocker 2, 3차 major 2 +
minor 1). 3회 모두 **그 시점에 제작자 테스트는 전부 통과 중**이었다.
효과가 있었던 요소:

| 요소 | 왜 |
|---|---|
| **별도 에이전트** | 같은 세션의 자체 점검으로는 3회 다 못 잡았다 |
| **제작자의 결론·걱정을 알려주지 않음** | 알려주면 그 프레임 안에서만 본다 |
| **"제작자의 테스트를 증거로 받지 마라"를 명시** | 3회 다 테스트는 통과 중이었다 |
| **읽지 말고 실행/렌더하라고 지시** | 3차는 실제로 프롬프트를 렌더하고 가드에 주입 공격을 했다. 코드를 읽기만 했다면 정확일치 버그를 못 봤을 것 |
| **찾은 것을 재현 가능한 형태로 보고하게 함** | "이 문장을 주입하니 통과했다"가 그대로 회귀 테스트가 됐다 |

**Q9 등록만 하는 경우엔 4차 리뷰가 필요한지 불명확하다** — 표면
(prompt/payload/fixture)이 바뀌지 않고 사전등록 문서에 한계 선언만 추가되기
때문이다. 운영 세션 의견은 "생략 가능"이지만 **사람이 판단할 사안**으로
남겼다(`HANDOFF.md` 배너).

---

## 6. 커밋·승인 규율

- **동결 아티팩트와 운영 로그를 같은 커밋에 섞지 않는다**(방법론 규칙 1).
  이번 세션은 `feat(h1a): apply Q5-Q8`(코드·fixture)과
  `docs(h1a): record Q5-Q8 applied`(등록부·HANDOFF)를 나눠 커밋했다
- **커밋·푸시는 매번 별도 승인**이다. 이번 세션은 커밋 승인을 받았고
  **푸시는 받지 않았다**
- 2026-08-02 종료 시점 미푸시: `concept-gate-h1-wt`는 upstream 자체가
  **없다**(오늘 만든 브랜치). `concept-gate-e2.2-wt`는 13커밋 미푸시.
  **H 계열 작업 전부가 로컬에만 있다**
- **본 코호트 40 trial 실행은 별도 승인 대상**이다. Agent/Workflow 디스패치가
  들어가므로 임의 실행 금지

---

## 7. 정직한 잔여 — 내가 알지만 어디에도 안 쓴 것, 그리고 내가 모르는 것

이 절이 이 문서의 핵심이다. 위 §1~§6은 "알려진 미지"이고, 여기는 그
경계다.

### 7.1 이 문서를 쓰다가 확인해서 **해소한 것** (기록 보존)

초안에는 아래 넷을 "확인 안 함"으로 적었다가, **명령 하나면 끝나는
것들이라 그 자리에서 확인했다.** 미지로 넘기는 것보다 재는 게 쌌다 —
넷 중 하나는 실제 결함이었다.

| 항목 | 확인 결과 |
|---|---|
| `notes/`에 `DESIGN_REQUEST` 미러가 있는가 | **없다.** `find notes -name "*DESIGN_REQUEST*"` → 0건. **판정문만 미러되고 요청서는 저장소에만 있다** — 미러 규약의 범위가 판정문 한정임을 확인 |
| `README.md`가 낡은 상태를 서술하는가 | **그렇다 — P4 재발.** "남은 게이트는 Q2의 anchor-sensitivity 진단, 이것이 통과되기 전에는 본 코호트를 동결·실행하지 않는다"가 그대로 남아 있었다. **Q6=A가 은퇴시킨 게이트다.** 다음 세션이 이걸 읽으면 존재하지 않는 20건 진단을 돌리려 했을 것이다 → **2026-08-02 수정함**(헤더 경고 + 로드맵 6·6a~6d행 재작성) |
| `concept-gate-e2.2-wt` 사본과의 드리프트 | **실측: 파일 6개 내용 상이 + 편측 존재 다수.** 저쪽에만: `_h1a_diag*` 4개, `h1a-decider.md`, `DESIGN_REQUEST*` 5개(이쪽은 `correspondence/`로 이동). 이쪽에만: `h1a_prompt_template.md`, `correspondence/`, `superseded/`. **양쪽이 이미 다른 실험 상태**다 — 저쪽을 참조하면 Q5~Q8 이전 설계를 보게 된다 |
| Q9 판정문 바이트 무결성 | **여전히 미확인.** 읽고 요지만 파악했다. §4 절차를 처음부터 밟아라 |

**교훈**: "확인 안 했다"고 문서에 적기 전에, 그게 명령 한 줄이면 그냥
확인하라. 이번엔 그 한 줄이 다음 세션을 없는 게이트로 보낼 뻔한 서술을
잡았다.

### 7.2 실행 이전이라 아무도 모르는 것

**trial이 0건이다.** 따라서 아래는 전부 미지다:

- 코더의 실제 invalid 비율 (교정 코퍼스 18/18은 합성 케이스다)
- 전송 실패·rate limit 패턴, 40건을 어떻게 배치할지의 실제 제약
- 모델이 `h1a_observation_v1` 형식을 실제로 지키는 비율
- warrant 규칙(Q7)이 실제로 해석 가능한지 — 문면상 대칭이라는 것만 확인했다

`PREREGISTRATION.md`의 P4(제외 기준)·P6(invalid 처리)이 이 미지에 대비한
것이지만, **대비가 맞는지는 실행해 봐야 안다.**

### 7.3 구조적으로 남아 있는 미지

- **잔여-금지 가드는 완전 봉쇄가 불가능하다**(§3.2). 다음 리뷰가 또 다른
  의역을 찾을 수 있고, 그건 결함이 아니라 이 방식의 한계다. 진짜로 닫으려면
  의미 기반 검사(LLM 리뷰어)가 필요한데 범위 밖으로 뒀다
- **3차 리뷰는 에이전트 1개였다.** 4차를 돌리면 또 나올 수 있다. "리뷰
  통과 = 결함 없음"이 아니라 "이 리뷰가 시도한 공격에는 안 걸림"이다
- **`notes/` 판정 도착 경로의 지연·통지 방식을 모른다.** 사용자가 어떻게
  넣는지 관측하지 못했으므로, "아직 안 왔다"와 "왔는데 못 봤다"를 구별하는
  유일한 방법은 §1.1의 `ls`다
- **P1(가드가 틀린 명제 검사)이 여섯 번 발생했다.** 여섯 번째까지 매번
  "이번엔 제대로 봤다"고 생각했다. **일곱 번째가 없다고 가정하지 마라** —
  가드를 새로 쓰거나 고칠 때마다 "이것이 참으로 만드는 명제"와 "내가 실제로
  보증해야 하는 명제"를 따로 적어 대조하라(`HARNESS_KNOWHOW.md` B4)

---

## 8. 이 문서 자체의 유지

- 이 문서는 **현재 상태에 강하게 결합**돼 있다(파일명·숫자·상수 이름).
  Q9 등록이 끝나면 §4가, trial이 돌면 §7.2가 낡는다
- 낡은 항목은 지우지 말고 **날짜와 함께 "해소됨"으로 표시**하라 — 어떤
  함정이 실제로 있었는지가 다음 사람에게 정보다
- **§0의 결론(문제는 없음이 아니라 닿지 않음)은 낡지 않는다.** 새 세션이
  "이건 아무도 안 써놨네"라고 느끼면, 쓰기 전에 먼저 검색하라
