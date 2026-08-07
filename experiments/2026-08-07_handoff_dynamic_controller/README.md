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

## Phase C live subject

```bash
python3 run_calibration.py
python3 -m pytest -q
python3 run_live_phase_c.py --pilot --output-name live_pilot_attemptN
```

`--output-name`은 기존 live artifact overwrite를 거부한다. 실행은 macOS에서만
지원한다. host가 `/private/tmp`에 disposable bundle을 만들고, Codex subject는
`subject/`의 public task와 socket client만 받는다. outer Seatbelt가 repository와
`control/corpus`를 차단하므로 Codex의 inner sandbox는 사용하지 않는다. final answer의
path/range는 model self-report가 아니라 host action log와 clean judge로 확인된다.

primary (`--primary`)는 pilot 결과와 별개로 비용이 드는 32-cell sweep이다. pilot
qualification을 arm-effect estimate로 해석하지 말고, primary 실행 여부를 명시적으로
결정한 뒤에만 호출한다.

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
| `build_live_public_bundle.py` | public subject / host-only corpus bundle + immutable-input manifest |
| `run_live_phase_c.py` | Seatbelt-isolated Codex subject, host action server, Phase C scoring |
| `test_live_phase_c.py` | bundle, guard, static recovery, schema, subagent exposure regression tests |

최종 Phase C qualification pilot은 `results/live_pilot_attempt9.json`에 기록되어 있다.
이 4-cell pilot으로 arm 효과를 주장하지 마라 — 이유는 `RESULTS.md` §7.
