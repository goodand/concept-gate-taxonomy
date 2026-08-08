# 하네스 개발자에게 — 반복 겪고 기제로 검증된 것

- 작성: 2026-08-07, owl-wt 세션
- 수신: `HANDOFF_REUSE_HARNESS_PREREGISTRATION.md` 작성자
- 원칙: **규율로 해결됐다고 주장하는 것은 뺐다.** 아래는 전부 (a) 2회 이상
  재발했고 (b) 기제로 옮긴 뒤 뮤테이션이나 외부 리뷰로 실효성이 확인된 것이다.
- 각 항목은 그쪽 문서의 **어느 절에 걸리는지**를 명시한다. 이미 반영된 것은
  "이미 있음"이라 적고 기제만 보탠다.

---

## K1. 긍정 테스트만으로는 정상 가드와 공허한 가드를 구별할 수 없다

**걸리는 곳: §4 Phase A, §8.1 evaluator release gate**

### 실측

`_h1a_policy.py`의 `assert_5`가 **완전히 공허한 채로** 긍정 테스트를 전부
통과했다. 잡은 것은 suite가 아니라 외부 리뷰어였다. 같은 패턴(주장하는 명제는
참이지만 필요한 명제가 아님)이 이 저장소에서 **11회** 기록됐다.

`docs/H1A_PROBLEM_ANALYSIS.md`가 6건까지 기록하고 `NEXT_SESSION_TRAPS.md` §7.3이
"일곱 번째가 없다고 가정하지 마라"고 **예고까지 했는데 일곱 번째가 났다.**
**"두 명제를 적어 대조하라"는 규율은 7/7 실패했다.**

### 기제

`test_guard_negative_coverage.py`(루트). AST로 `raise`하는 `assert_*`를 수집해
같은 이름이 어느 테스트의 `pytest.raises` 안에 최소 1회 등장하지 않으면
**실패시킨다.** import하지 않고 AST만 읽는다(K3 참조). core pytest가 이미
수집하므로 배선 없음.

### 권고

Phase A negative controls는 이 규율의 실험판이므로 방향이 옳다. 다만 **evaluator
소스에도 같은 AST 게이트를 걸어라** — mutation suite는 evaluator가 *무엇을
검출하는지* 시험하지만, evaluator 안에 새로 추가된 검사가 mutation suite에
대응 항목을 갖는지는 시험하지 않는다. 검사가 늘 때 suite가 자동으로 늘지 않으면
같은 자리에서 다시 벌어진다.

---

## K2. 음성 테스트 자체가 공허할 수 있다 — 뮤테이션으로 계측기를 계측하라

**걸리는 곳: §4 Phase A, §8.1 "지정 mutation detection: 100%"**

### 실측 (2026-08-06, 어제 밤)

red team이 내 도구에서 "정의됐지만 호출되지 않은 가드"를 찾았다. 나는 그것을
잡는 메타 테스트를 썼다. 뮤테이션으로 검증했다:

| 뮤테이션 | 기대 | 실제 |
|---|---|---|
| **가드 호출부 삭제 (= 원래 결함 재현)** | 실패 | **통과** ← 공허 |
| 플래그를 안 읽게 | 실패 | 실패 ✓ |
| 계수 로직 되돌림 | 실패 | 실패 ✓ |

원인: 메타 테스트가 함수 **이름의 존재**만 검사해서 `def` 한 줄이 조건을
만족시켰다. **"정의됐지만 호출되지 않음"을 잡으려고 쓴 테스트가 정확히 그
구분을 못 하는 검사를 썼다.** `ast.Call` 노드를 요구하도록 고쳤다.

### 권고 — Phase A에 3번째 단계가 필요하다

현재 §4 Phase A는 두 가지를 요구한다: positive control은 통과, mutation은 검출.
**세 번째가 빠져 있다 — mutation이 실제로 적용됐는지의 확인.**

문자열 치환 기반 뮤테이션은 대상이 76열로 줄바꿈돼 있거나 공백이 다르면
**조용히 no-op이 된다.** 이 세션에서 실제로 발생했다(M2 회귀 테스트가 무언의
no-op이었고 `DID NOT RAISE`로 드러났다). no-op 뮤테이션은 evaluator가 검출
못 했다는 사실을 **evaluator가 정상이라는 증거로 바꿔 놓는다** — 부호가 반대로
뒤집힌다.

→ 각 뮤테이션에 대해 **적용 후 바이트가 실제로 달라졌는지 assert**하고,
달라지지 않았으면 그 mutation case를 `E0`가 아니라 **하네스 결함**으로 보고하라.

---

## K3. 동명 모듈은 `sys.modules`를 선점한다 — 프로세스 분리가 유일한 확장 해법

**걸리는 곳: §12 구현 구조(`evaluator/`, `mutations/`, `fixtures/`), §3.1 bundle 3종**

### 실측

동결 규율상 실험 폴더들이 같은 모듈명을 중복 보유한다 — `_cert_core.py` **6개
바이트동일**, `evaluate.py` **10개**, `_gen_prompts.py` **7개**. 한 인터프리터에
모아 돌리면 먼저 로드된 쪽이 `sys.modules`를 선점해 **다른 실험이 남의
evaluator로 조용히 실행된다.** 실제로 발생한 결함이다.

추가 실측(F10): 두 번째 모듈 사본이 **lazy하게** 생성되는 경우가 있다.
`import`만으로는 안 생기고 특정 함수 호출 시점에 생긴다. 그래서 "import해 보니
하나뿐이더라"는 확인이 **거짓 음성**을 낸다. 이 결함은 **그 시점까지의 뮤테이션
테스트 결과 전부를 무효화**했다.

### 기제

`scripts/run_gates.py` — 실험마다 **별도 프로세스**로 돌린다. 새 실험은 아무
조치도 필요 없다(경로 스캔). 상세 근거는 그 파일 헤더 주석.

### 권고

bundle 3종 × case 8개 구조는 정확히 이 조건이다. evaluator를 in-process import로
여러 bundle에 재사용하지 마라. 그리고 **모듈 동일성 확인은 import 직후가 아니라
평가 1회를 완주한 뒤에 하라** — lazy 생성 때문이다.

---

## K4. BLOCKED와 FAIL을 분리하되, 경계를 메시지가 아니라 **실행 여부**로 그어라

**걸리는 곳: §4 Phase B의 `V1`(invalid-run), §9 실패 분류**

### 검증된 규칙

- 선택적 의존성 미설치로 게이트가 **시작조차 못 하면** BLOCKED. exit code에
  반영하지 않는다.
- 테스트가 **실행된 뒤** 실패한 것은, 실패 메시지가 모듈 누락을 언급해도 FAIL.

두 번째가 핵심이다. 이 구분을 메시지로 하면 **환경 의존 테스트 하나가 같은
suite의 실제 회귀를 가린다.**

### 권고 — `V1`을 1차 보고값으로 올려라

§7 primary outcomes에 `V1` 비율이 없다. 그런데 **긴 trace를 만드는 arm이 더 자주
죽는다.** Skill arm이 §6 trace 계약을 성실히 채우면 토큰이 늘고 timeout 확률이
오른다. `V1`을 조용히 버리면 **Skill arm에서 어려운 case가 선택적으로 사라져**
남은 표본이 쉬워지고, Skill 효과가 위로 편향된다.

→ arm별 `V1` 비율을 primary로 보고하고, arm 간 차이가 유의하면 성능 비교를
그 조건으로 한정하라. 이건 부수 지표가 아니라 **효과 추정치의 타당성 조건**이다.

---

## K5. 정밀도 실패는 계측기를 무용하게 만든다 — 한 번에

**걸리는 곳: §8.1 "unrelated mutation false positive: 0"**

### 실측

`handoff_reachability.py` 첫 실행이 **404개의 "dangling" finding**을 냈고 거의
전부 산문이었다. 원인: 파일명을 언급하는 산문(`` `_h1a_policy.py` ``)을 깨진
링크로 취급. 맨 파일명, glob(`experiments/*/test_protocol.py`), 다른 worktree
기준 상대경로가 전부 걸렸다.

**404개를 보면 사람은 목록 전체를 버린다.** 리포트를 읽지 않게 되는 것이지
개별 항목을 검토하지 않는 게 아니다.

### 기제

두 종류의 간선을 **자료구조에서** 분리했다:

- **LINK** `[t](p)` / `[[p]]` = 대상이 존재한다는 **약속**. 깨지면 보고한다.
- **MENTION** `` `p` `` = 산문. **도달성에는 계산하되 dangling으로는 절대
  보고하지 않는다.**

404 → 8. 양방향 테스트로 고정: `test_a_broken_link_is_reported_dangling`(recall),
`test_a_broken_mention_is_NOT_reported_dangling`(precision). 이 구분이 다시
합쳐지는 것을 테스트가 막는다.

### 다만 — 이 옳은 결정이 게임 경로를 만들었다

red team이 깨진 `[x](gone.md)`를 `` `gone.md` ``로 바꿔서 finding을 없앴다.
**정밀도와 게임 방지가 실제로 충돌한다.** mention에 G2/G3를 적용할지, mention을
도달성 계산에서 뺄지는 판정이 필요한 설계 문제이고 나는 아직 안 풀었다.
그쪽 §3.1 synthetic adversarial bundle에 **이 변환을 attack case로 넣기를 권한다.**

---

## K6. 검증 불가한 조건은 이름을 붙여 담당을 적는다 — 모킹으로 통과시키지 않는다

**걸리는 곳: §5 "매핑되지 않은 Skill 약속은 release gate에서 미검증으로 표시한다" (이미 있음)**

### 기제

이미 같은 결론이므로 기제만 보탠다. `KNOWN_UNPROVEN: dict[str, str]`에
**이유와 담당을 적고**, 별도 테스트가 **stale 항목**(이미 증명 가능해졌는데
남아 있는 것)을 실패시킨다. 안 그러면 면제 목록이 영구 면제가 된다.

**모킹 기반 음성 테스트는 게이트를 초록으로 만들면서 아무것도 증명하지 않는다.**
도달 불가한 raise 경로를 모킹으로 때우면 K1의 공허한 가드와 관측값이 같아진다.

### 실측 — 자기보고 준수율은 독립 측정이 필요하다

내가 프리레지스트레이션 §4에 **10개 조건이 "✅ 자동 검증됨"**이라고 썼다.
외부 리뷰어가 확인하니 **참인 것은 4개**였다. 나머지는 미구현이거나 서술이
과장이었다. 나쁜 의도가 아니라 **쓰는 시점과 구현하는 시점이 달라서** 생긴다.

→ §10 동결 순서 7번(evaluator source, mutation suite, manifest) 동결 시
"각 gate 항목 → 그것을 실행하는 코드 위치" 매핑을 **기계 생성**하고, 매핑
없는 항목을 동결 실패로 만들어라. 사람이 쓴 준수 선언을 그대로 믿지 마라.

---

## K7. grep은 "어디 있나"에 답하고 "이미 결정됐나"에 답하지 못한다

**걸리는 곳: §0 evidence retrieval 계층, §2 RQ, §3.1 case 설계**

### 실측

결정 문서의 **경로가 질문의 어휘를 하나도 포함하지 않을 수 있다.**
2026-08-01: "디렉토리 정리 / DESIGN_DECISION / canonical"로 파일명을 훑었으나
이미 채택된 결정(`notes/audits/vault/symlink-vs-moc-2026-07-30.md`)이 안 걸렸다.
재확인(08-02): `find notes -iname "*canonical*" -o -iname "*design_decision*"`가
이 파일을 반환하지 않는다. **본문에는 `canonical`이 8회** 등장하지만 같은
조건에 걸리는 파일이 7개라 순위를 매길 근거가 없었다.
**backlink 1홉으로는 정확히 2건(MOC + 그 감사 문서)이 나왔다.**

측정된 recall: 어휘 검색 **0.688** → pool refill 0.812 → graph walk 0.958 →
**1.000**.

### 권고

§3.1의 "최소 30%는 paraphrase" 조건이 이 현상을 겨냥한 것으로 읽히는데,
**paraphrase보다 강한 조건이 필요하다** — 위 실측은 어휘가 다른 게 아니라
**경로에 어휘가 아예 없는** 경우였다. case 최소 1개는 **정답 문서의 경로와
제목이 질문 어휘와 0% 겹치고 backlink로만 도달 가능**하게 설계하기를 권한다.
그래야 RQ가 "검색어를 바꾸면 되는가"와 "그래프를 따라가야 하는가"를 가른다.

`.vault-harness`의 `multiturn_retrieval.py --policy recall-first-v2`가 이미 이
절차를 구현하고 있으므로 subject의 참조 상한(reference trace)으로 쓸 수 있다.

---

## K8. in-process 가드로는 채점기 무결성을 지킬 수 없다

**걸리는 곳: §4 Phase C J1 최소 조건 (이미 있음)**

이미 반영돼 있으므로 **실측 하나만** 보탠다. 왜 소스 해시가 부족한지의
구체적 재현이다.

G1은 채점기 **소스 바이트**를 SHA256으로 핀했다. red team은:

1. 패치한 `audit()`를 `py_compile`로 **hash-based UNCHECKED `.pyc`**로 컴파일
2. 소스를 바이트 단위로 원상 복원

결과: **핀 해시 완전 일치, `git status` 깨끗**(`__pycache__/`가 gitignore),
실행되는 것은 패치된 바이트코드. `python3 -B`는 방어가 아니다 — **쓰기만 막고
읽기는 막지 않는다.**

→ §8.1의 "evaluator source hash 일치"가 **더러운 프로세스 안에서** 돌면 같은
우회가 성립한다. 해시 검증 자체가 clean subprocess **안**에서, `-B -E -P -I` +
캐시 제거/리다이렉트 상태로 돌아야 한다. **순서가 결정적이다.**

---

## K9. worktree 사이로 파일을 손으로 복사하지 마라

**걸리는 곳: §4 Phase D "isolated worktree에서 patch proposal"**

### 실측

정본 소스가 두 벌 있던 시절 한쪽만 고쳐 **거짓 통과**가 났다. 단일 패키지로
합쳐 그 실패 모드를 없앴다. 2026-08-05: repo 전역 게이트를 worktree마다 넣을
파일로 읽어 두 트리에 손으로 복사하려 했고, **세션 격리가 거부해서** 분기가
생기지 않았다.

worktree들은 **하나의 git 저장소를 공유**하므로 파일이 다른 worktree에 도달하는
정상 경로는 복사가 아니라 **커밋 → 머지 → cherry-pick**이다.

### 권고

Phase D의 repair agent가 isolated worktree에서 patch를 만드는 설계는 옳다.
여기에 하나 더: **게이트·하네스 파일은 경로 독립으로 써라**(`Path(__file__).parent`).
worktree마다 다른 사본이 필요해지는 순간 위 실패 모드가 되살아난다.

---

## 요약 — 그쪽 설계에 대한 순 권고 6개

1. **§4 Phase A에 "뮤테이션이 실제로 적용됐는지" 확인 단계 추가** (K2) —
   no-op 뮤테이션은 evaluator 정상의 *증거로* 뒤집힌다. 가장 값싸고 효과 큼.
2. **§7 primary outcomes에 arm별 `V1` 비율 추가** (K4) — 타당성 조건이지
   부수 지표가 아니다.
3. **§8.1 hash 검증을 clean subprocess 안으로** (K8) — 순서 문제.
4. **§10 동결 시 gate 항목 → 코드 위치 매핑을 기계 생성** (K6) — 자기보고
   준수율 10 주장 vs 4 실제.
5. **§3.1에 "경로·제목이 질문 어휘와 0% 겹치는" case 최소 1개** (K7) —
   paraphrase보다 강한 조건.
6. **§3.1 adversarial bundle에 "링크 → backtick mention 변환" attack 추가** (K5)
   — 정밀도를 위한 옳은 결정이 만든 게임 경로.

## 첨부 — 근거 위치

| 항목 | 위치 |
|---|---|
| K1 기제 | `concept-gate-owl-wt/test_guard_negative_coverage.py` |
| K1 이력 | `docs/H1A_PROBLEM_ANALYSIS.md` (P1 6건), `docs/NEXT_SESSION_TRAPS.md` §7.3 |
| K2 실측 | `docs/feedback/redteam_handoff_repair_loop_20260806.md` §6 |
| K3 기제 | `scripts/run_gates.py` 헤더 주석 |
| K4 규칙 | `concept-gate-owl-wt/CLAUDE.md` "PASS / FAIL / BLOCKED" |
| K5 기제 | `scripts/handoff_reachability.py`, `test_handoff_reachability.py` |
| K6 기제 | `docs/HARNESS_KNOWHOW.md` §B4a |
| K7 실측 | `docs/H1A_PROBLEM_ANALYSIS.md` §4 W-B, `docs/WORKSPACE_NAVIGATION.md` §0 |
| K8 실측 | `docs/feedback/redteam_handoff_repair_loop_20260806.md` §2 경로 B |
| K9 규칙 | `concept-gate-owl-wt/CLAUDE.md` "Project Structure" |
