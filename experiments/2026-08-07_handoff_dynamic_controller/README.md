# handoff cold-start retrieval — dynamic workflow controller 실험

상위 표준 `.vault-harness/vault-md-retrieval/HANDOFF_REUSE_HARNESS_PREREGISTRATION.md`의
형제 실험. 상위는 dirty worktree라 **읽기만** 했고 수정·복사하지 않았다.
계약 이름과 실패 코드는 상위와 동일하게 유지해 결과를 나중에 합칠 수 있게 했다.

## 무엇을 재는가

2×2 요인: retrieval subagent(없음/있음) × controller(static/dynamic).
`S_STATIC` `R_STATIC` `S_DYNAMIC` `R_DYNAMIC`.

## 경계

```
public corpus + public question
   |-> [retrieval subagent]  후보/범위/검색기록/불확실성 네 키만
   |-> [main subject + controller]  후보를 authority로 쓰지 않고 직접 재-read
             |
             v  trace JSON
   [clean judge: subprocess -B -E -P -I -X pycache_prefix=<temp>] + hidden gold
```

controller action은 6개로 폐쇄: `reformulate_query` `follow_link`
`read_candidate` `expand_candidates` `abstain` `answer`.
종료는 recall-first 최소 탐색 예산을 채우기 전까지 거부된다.

## 실행

```bash
python3 build_corpus.py        # 결정론적 corpus/cases/gold 생성
python3 run_calibration.py     # Phase A/A' — 통과해야 다음이 의미를 가진다
python3 run_smoke.py           # Phase B — calibration 실패 시 실행 거부
python3 -m pytest -q test_protocol.py
```

`run_smoke.py`는 calibration 결과가 현재 evaluator, controller, corpus, cases,
hidden gold, manifest와 정확히 같은 frozen surface에서 나온 경우에만 실행한다.

## 파일

| 파일 | 역할 |
|---|---|
| `PREREGISTRATION.md` | 설계 동결본 + Amendment 1 |
| `RESULTS.md` | 캘리브레이션·smoke 결과와 한계 |
| `_contract.py` | 계약(스키마·실패코드·금지키·토크나이저) |
| `_runner.py` | corpus, 예산 guard, run 루프 |
| `_controllers.py` | static/dynamic 스크립트 + 캘리브레이션용 고장 controller |
| `_evaluator.py` | 채점 + clean judge |
| `build_corpus.py` | 합성 adversarial bundle 생성 |
| `run_calibration.py` / `run_smoke.py` | Phase A/A′ / Phase B |
| `test_protocol.py` | 프로토콜 게이트(양방향) |

**live subject run은 0건이다.** smoke 수치로 arm 효과를 주장하지 마라 —
이유는 `RESULTS.md` §5.
