# `.vault-harness` handoff-reuse 하네스 — 변경 확인과 개발자 질의

- 확인 시각: 2026-08-06 (밤)
- 대상: `.vault-harness/vault-md-retrieval/` (**dirty worktree — 읽기만 했다**)
- 확인자: 이 세션(owl-wt). 파일 수정 없음.

## 1. 무엇이 바뀌었나

`.vault-harness`가 **git repo가 됐다**(계획 Part 1이 실행됨). 커밋 7개,
방법론 §1의 계층 분리를 따름:

```
aba056e chore: initial gitignore + held-out eval integrity hash
f46ee7b feat: source and contract layer (py, sh, schemas)
b5aa2f8 docs: contract, procedure, and record markdown
3e47169 results: evaluation and performance JSON
4312098 fix: surface terminal_reason in the search summary (not a new gate)
25bb209 feat: record index build timestamp; verify terminal_reason disclosure
a6b45c5 Merge worktree-vault-harness-t1t2t3
```

`4312098`는 계획 Part 3(비수렴을 complete로 보고하는 결함)에 대한 응답인데
**게이트가 아니라 노출로 처리**했다 — 커밋 메시지가 "not a new gate"라고
명시한다. 내가 계획한 `SEARCH_DID_NOT_CONVERGE` warning보다 약한 개입이고,
precision 사후 점검 부담이 없다는 점에서 더 보수적인 선택이다.

그리고 **오늘 22:03–23:27에 handoff-reuse 하네스 일습이 새로 생겼다**(전부
untracked):

| 파일 | 내용 |
|---|---|
| `HANDOFF_REUSE_HARNESS_PREREGISTRATION.md` | 455줄 프리레지스트레이션, Phase A–D |
| `handoff_reuse_evaluator.py` | case/gold/trace 검증 + `evaluate_trace` |
| `run_handoff_reuse_subject.py` / `evaluate_handoff_reuse_subject.py` | runner |
| `evaluate_handoff_reuse_phase_a.py` | Phase A 캘리브레이션 |
| `test_handoff_reuse_*.py` 3개 | 테스트 |
| `COLAB_SUBJECT_ISOLATION.md` | Colab을 subject 격리 transport로 쓸 때의 경계 |
| `handoff-reuse/` | 디렉터리 |

## 2. 내 도구가 어떻게 흡수됐나

프리레지스트레이션 **§1.1이 내 두 도구를 선행 근거로 직접 인용**한다:

- `handoff_reachability.py` → "링크 도달성만 결정론적으로 측정한다. 이는
  유용한 preflight지만 무맥락 agent의 이해나 재개 성공을 증명하지 않는다."
  §12-3에서 **read-only preflight adapter로 연결** 예정.
- `handoff_repair_loop.py` → "red-team은 `.gitignore`, link deletion, mention
  변환, bytecode cache 등으로 metric을 게임할 수 있음을 보였다."

즉 **red team이 뚫은 4경로가 그대로 설계 입력이 됐다.** J1 최소 조건에
"judge는 agent workspace의 Python import cache와 executable을 신뢰하지 않는다",
"`.gitignore`, index flags, symlink, bytecode cache가 바뀌어도 judge input set은
고정 manifest에서 계산한다"가 들어가 있다 — 내 G1/G4가 못 막은 것을
**아키텍처(clean subprocess + 고정 manifest)로 옮겨 푼다.** 가드를 더 쓰는
것으로는 못 푸는 문제였다는 판단이고, 나는 이 판단이 옳다고 본다.

## 3. 이 세션이 이 설계에 대해 확인한 것

- 4계층 분리(structural reachability / evidence retrieval / grounded
  continuation / evaluation integrity)와 "앞 계층 통과가 뒤 계층 통과를 뜻하지
  않는다"는 이 저장소의 패턴 8·10과 같은 규율이다.
- §11 해석 상한이 "reachability pass는 이해 가능성이나 safe continuation을
  증명하지 않는다"를 명시 — 내 auditor가 자기 리포트에 넣은 `does_not_measure`와
  같은 명제. 두 곳이 독립적으로 같은 결론에 도달했다.
- §8.1 evaluator release gate가 "unrelated mutation false positive: 0"을
  요구 — 내 auditor 첫 실행이 404 false positive를 냈던 그 축이다.

## 4. 개발자에게 물을 것 (§5 참조)

별도 절로 분리. 아래 5건은 내가 문서만 읽어서는 결정할 수 없고, 답에 따라
내 preflight adapter 연결 방식이 달라진다.

## 5. 질의 목록

### Q-HR1. RQ1과 preflight 게이팅이 충돌한다 (설계급)

§12-3은 `handoff_reachability.py`를 **preflight**로 연결한다. §2 RQ1은
"structural reachability가 critical evidence retrieval을 예측하는가"를 묻는다.

preflight가 reachability 실패 bundle의 subject run을 **막으면**, RQ1의 낮은 쪽
데이터가 구조적으로 생기지 않아 RQ1은 답할 수 없다(전 표본이 reachability
pass). preflight가 **막지 않고 기록만** 하면 RQ1은 답할 수 있지만 "preflight"라는
이름값이 없다.

→ preflight는 **차단인가 계측인가?** RQ1을 살리려면 후자여야 하고, 그러면
reachability는 gate가 아니라 **공변량**으로 §7에 들어가야 한다.

### Q-HR2. `metric-only`와 `metric-fake`를 구분하는가

§4 Phase D-6은 "structural score만 개선되면 `metric-only improvement`로 분류"
한다. 그런데 red team 실측은 그보다 나쁜 상태를 만들었다 — **reachability
실측치는 135 → 135로 불변인데 metric은 9 → 0**이 됐다(dangling link를 산문으로
지우거나 backtick mention으로 바꿔서). 이건 구조가 개선된 게 아니라 **계측기가
못 보는 곳으로 옮긴 것**이다.

→ `M1`이 이 둘을 한 코드로 묶으면, 진짜 구조 개선(도달성 상승, 이해도 불변)과
계측 회피(도달성 불변, 지표만 하락)가 같은 라벨을 받는다. **도달 파일 수 델타를
분류 기준에 넣으면** 기계적으로 갈린다.

### Q-HR3. hash 검증의 실행 순서 — 내 G1이 정확히 여기서 뚫렸다

§8.1은 "evaluator source 및 input manifest hash 일치"를 요구하고, J1은 clean
subprocess를 요구한다. 두 요구의 **순서**가 결과를 가른다.

내 G1은 소스 바이트를 해시했는데 CPython은 **바이트코드를 실행**한다. red team은
패치한 `audit()`을 hash-based UNCHECKED `.pyc`로 컴파일하고 소스를 바이트 단위로
복원해서, 핀이 완전히 일치하고 `git status`가 깨끗한 채 PASS를 받았다.
`python3 -B`는 방어가 아니다(쓰기만 막는다).

→ hash 검증이 **더러운 프로세스 안에서** 돌면 같은 우회가 성립한다. 검증은
clean subprocess **안**에서, `-B -E -P -I` + 캐시 제거/리다이렉트 상태로
돌아야 한다. 이 순서가 어디에 고정돼 있는가?

### Q-HR4. curator가 producer와 분리되는가 — 이 워크스페이스에서 실현 가능한가

§3.2: "handoff producer가 gold를 단독 확정하지 않는다. curator가 원문과
deterministic command를 직접 확인한다."

이 워크스페이스에서 producer도 curator도 실질적으로 같은 사람 또는 같은 모델
계열이다. 조항은 옳지만 **어떻게 만족시키는지가 안 적혀 있다** — 별도 세션이면
conversation memory만 분리될 뿐 모델 사전지식은 공유된다.

→ 분리의 조작적 정의가 필요하다. "다른 세션"인가, "다른 모델"인가, "gold를
쓴 사람이 그 case의 subject run 결과를 보기 전에 동결"인가? 셋째가 가장 싸고
검증 가능해 보인다.

### Q-HR5. `V1`(invalid-run) 비율이 arm 간에 다르면 그 자체가 결과다

§4 Phase B는 API/timeout/tool unavailable을 `invalid-run`으로 분리하고 성능
0점과 섞지 않는다 — 옳다. 이 세션에서도 독립 리뷰가 API session limit으로 죽었고
pass로 세지 않았다.

그런데 **긴 trace를 만드는 arm이 더 자주 죽는다.** Skill arm이 trace 계약(§6)을
성실히 채우면 토큰이 늘고 timeout 확률이 오른다. `V1`을 조용히 버리면 **Skill
arm에서 어려운 case가 선택적으로 사라져** 남은 표본이 쉬워진다.

→ `V1` 비율을 arm별 **1차 보고값**으로 올려야 한다. 현재 §7 primary outcomes에
없다.

## 6. 이 세션이 하지 않은 것

- `.vault-harness` 파일을 하나도 수정하지 않았다(dirty = protected).
- `handoff-reuse/` 내부와 `handoff_reuse_evaluator.py`의 `evaluate_trace`
  본문은 구조만 훑었고 줄 단위 검증을 하지 않았다. 위 질의는 프리레지스트레이션
  본문과 커밋 로그에 근거한다.
