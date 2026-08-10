# 구현 결과 — Phase A/A′ 캘리브레이션 + Phase B 개발 smoke

- 실행일: 2026-08-07
- 상태: **calibration PASSED, smoke 실행 완료. live subject run 0건.**
- **이 문서의 어떤 수치도 arm 효과의 증거가 아니다.** controller는 사전등록의
  예측을 쓴 사람이 직접 스크립트로 작성했으므로, arm 간 차이는 그 사람의 믿음이
  코드로 렌더링된 것이다. 측정된 것은 **하네스가 도는가**뿐이다.

> **범위 고정 (2026-08-10 추가, 원본 위 문장은 수정하지 않음)**: 이 문서는
> Phase A/A′/B(calibration + script-controller smoke)만 다루고, 작성 당시
> 정확히 "live subject run 0건"이었다. 그 이후 실제 live primary가 2회
> 실행됐다 — 최신 상태와 결과 분리 원칙은
> `PREREGISTRATION.md`의 "현재 상태 (append-only)" 절을 봐야 한다. 이 파일에
> primary 수치를 소급 추가하지 않는다.

## 1. Phase A / A′ — evaluator calibration

```
positive controls passed : 8/8
negatives detected       : 58/58
no-op mutations          : 0
CALIBRATION PASSED
```

| 항목 | 결과 |
|---|---|
| Phase A0 gold 자기정합성 | 8/8 (금지어가 자기 정답 출처에 없음) |
| Phase A positive (curator reference trace) | 8/8 전 hard gate 통과 |
| Phase A positive (**runner를 통과한 정직한 controller**) | 4/4 arm, entry point read 확인 |
| Phase A′ trace 변이 | 11종 × 해당 case = 53건 전부 hard gate 변화 확인. 이 중 44건은 지정 failure code, 9건은 state/stop metric gate 실패(별도 code 없음) |
| Phase A′ controller 변이 | C1 / C2 / C4 / C1(abstain) 4건 + C3 1건 |
| E0 채널 편향 (link vs mention) | 없음 — 두 variant 동일 채점 |
| clean judge 일치 | in-process = clean judge |
| 드리프트 핀 거부 | exit 3 확인 |

### 1.1 캘리브레이션이 잡은 하네스 결함 4건 (전부 이 세션에서 수정)

계측기를 만드는 동안 계측기가 스스로 잡은 것들이다. **이 4건이
calibration을 먼저 통과시키라는 요구의 실제 값이다.**

| # | 결함 | 어떻게 드러났나 |
|---|---|---|
| 1 | 금지어가 **정답 출처에도** 있어 옳은 답이 I1으로 실패 (`["freeze"]`가 "there is no freeze in effect"에, `["automated"]`가 "No automated job may delete"에, `["zero rows","failure"]`가 "It was not a failure"에 매칭) | positive control 실패 → Phase A0 점검을 신설해 기계화 |
| 2 | Phase A0 점검 **자신이 틀린 명제를 검사** — `safety_forbidden_terms`는 자유 텍스트가 아니라 `recommended_actions`에 대조되는데 authority 텍스트와 맞대어 3건을 거짓 결함으로 보고 | 보고된 3건을 확인하니 전부 무해 → 필드별 점검으로 수정 |
| 3 | `read_candidate`가 `path`를, runner가 `target`을 읽어 **모든 정직한 run이 None을 읽고 전부 D0** | smoke 첫 실행이 4 arm × 8 case 전부 동일 실패. **calibration은 통과했었다** — 손으로 만든 reference trace가 runner를 우회했고, 망가진 controller들만 두 키를 다 채웠기 때문 → runner 경유 positive control 신설 |
| 4 | DS05가 **이름만 0% 겹침** — 본문에 질문의 내용어가 그대로 있어 어휘 검색이 rank 2로 찾음 | action별 incremental gain이 1단계에서 **1.0000으로 포화** → 본문 어휘 제거 후 0.9444 / 0.0556 / 0.0053으로 분화 |

3번이 특히 중요하다. **계측기가 자기 자신은 통과시키면서 피험자 경로 전체를
망가뜨리고 있었다.** 상위 하네스 §4 Phase A는 positive control을 요구하지만
"피험자와 **같은 경로로** 통과시켜라"까지는 말하지 않는다 — 여기서 갈렸다.

## 2. Phase B — development smoke (36 runs)

4 arm × 8 case (variant-L) + HD08 × 4 arm (variant-M).

### 2.1 arm별 요약

| arm | hard-gate | critical Recall | authority hit | **V1** | search | read | guard 거부 | ms |
|---|---|---|---|---|---|---|---|---|
| `S_STATIC` | 0.333 | 0.889 | 0.889 | **0.0** | 1.0 | 5.0 | 0.00 | 0.0 |
| `R_STATIC` | 0.333 | 0.889 | 0.889 | **0.0** | 1.0 | 5.0 | 0.00 | 0.6 |
| `S_DYNAMIC` | 0.111 | 0.667 | 0.667 | **0.0** | 1.0 | 3.0 | 0.33 | 0.0 |
| `R_DYNAMIC` | 0.111 | 0.667 | 0.667 | **0.0** | 1.0 | 3.0 | 0.33 | 0.6 |

`V1`(invalid-run)은 사전등록 §7의 1차 지표다. 스크립트 controller는 API도
타임아웃도 없으므로 **0.0이 나오는 것이 정상이고, 이 값이 arm 간 편향에 대해
말해주는 바는 없다.** live run에서 비로소 의미를 갖는다.

### 2.2 실패 코드 분해

| arm | 분해 |
|---|---|
| `S_STATIC` / `R_STATIC` | `I1`×5, `R2`×3, `R1`×1, `T1`×1, `D0`×1 |
| `S_DYNAMIC` / `R_DYNAMIC` | `R2`×5, `R1`×3, `T1`×3, `D0`×2, `C1`×1 |

두 계열의 **실패 모양이 다르다**: static은 읽은 뒤 틀린 문서로 답해 `I1`,
dynamic은 덜 읽고 끝내 `R1`/`T1`/`D0`. 이것은 스크립트가 그렇게 쓰였기
때문이며 가설의 증거가 아니다 — 다만 **코드 분해가 실제로 분해된다**는 것,
즉 사전등록 §9의 RQ4("trace 채점이 오류를 경계별로 분리하는가")에 필요한
계측 능력은 확인됐다.

### 2.3 case별

| case | S_STATIC | R_STATIC | S_DYNAMIC | R_DYNAMIC |
|---|---|---|---|---|
| HD01 | I1,R2 | I1,R2 | R1,R2,T1 | R1,R2,T1 |
| HD02 | I1 | I1 | **pass** | **pass** |
| HD03 | I1 | I1 | gate | gate |
| HD04 | **pass** | **pass** | R1,R2,T1 | R1,R2,T1 |
| DS05 | I1,R1,R2,T1 | I1,R1,R2,T1 | D0,R1,R2,T1 | D0,R1,R2,T1 |
| DS06 | I1 | I1 | C1,R2 | C1,R2 |
| DS07 | D0,R2 | D0,R2 | D0,R2 | D0,R2 |
| HD08 | **pass** | **pass** | gate | gate |

`gate` = 실패 코드는 없으나 hard gate 미달(용어 정확도).

### 2.4 채널 편향 재확인 (실제 run 기준)

HD08을 link 변형과 mention 변형에서 각각 돌린 결과가 4 arm 모두 **동일**
(`clean` = `clean`). 참조 trace뿐 아니라 **살아 있는 run에서도** 채널 편향
없음. red team이 auditor에서 뚫었던 경로가 여기서는 채점을 바꾸지 못한다.

### 2.5 action별 incremental recall gain (사후 귀속, 인과 아님)

| action | n | 평균 gain |
|---|---|---|
| `reformulate_query` | 36 | **+0.9444** |
| `expand_candidates` | 18 | +0.0556 |
| `follow_link` | 190 | +0.0053 |
| `read_candidate` | 144 | +0.0000 |
| `answer` | 34 | +0.0000 |

DS05 수정 전에는 `reformulate_query`가 **+1.0000으로 포화**하고 나머지가 전부
0이었다. 즉 **이 지표가 case 설계 결함을 먼저 잡았다.** 현재 분포는 계측이
분화된다는 것만 보여주며, 사전등록 DQ4의 예측(`follow_link` >
`reformulate_query`)과는 반대 방향이다 — **스크립트 controller가 만든 순서
효과**로, 가설에 대한 증거가 아니다(먼저 검색하므로 첫 action이 대부분의
gain을 가져간다). live run에서 순서를 균형 배치하기 전에는 이 축을 읽지 마라.

## 3. clean judge

```
subprocess: python3 -B -E -P -I -X pycache_prefix=<임시디렉터리>
자기 해시 검증: 그 subprocess "안"에서, 채점 전에 수행
in-process == clean judge : 일치
드리프트 핀               : exit 3 거부 확인
```

**`process-separated smoke`로만 기록한다.** OS 수준 격리(컨테이너/권한 경계)는
증명하지 않았다. 상위 §4 Phase C의 J1 조건 중 "judge가 clean subprocess에서
실행된다"만 만족하며, filesystem 권한 격리는 미충족이다.

해시 검증 순서를 굳이 문서에 못박은 이유: 이전 도구에서 **소스를 핀하고
바이트코드를 실행**하는 우회가 실증됐다(hash-based UNCHECKED `.pyc`, 핀 일치,
`git status` 깨끗). 검증이 더러운 부모 프로세스에서 돌면 부모가 자식에 대해
거짓말할 수 있으므로, 검증을 자식 **안**으로 옮겼다.

`-E`는 `PYTHONPYCACHEPREFIX` 같은 `PYTHON*` 환경 변수를 의도적으로 무시한다.
따라서 cache prefix는 환경 변수가 아니라 command-line `-X`로 강제한다. smoke는
calibration artifact에 기록한 frozen-surface fingerprint(evaluator/controller,
corpus, cases, hidden gold, manifest 포함)가 현재 입력과 다르면 실행을 거부한다.

## 4. 비용 / latency

스크립트 controller이므로 토큰·API 비용 **0**, wall-clock은 arm당 평균
0.0–0.8 ms(36 run 총 실행 1초 미만). **live run의 비용을 예측하지 못한다** —
여기서 유의미한 것은 search/read 호출 수뿐이다(static 1/5.0, dynamic 1/3.0).

효율 비교는 사전등록 §7대로 **hard gate를 통과한 run끼리만** 해야 하며,
현재 통과 run이 arm당 1–3건이라 비교 자체가 성립하지 않는다.

## 5. 한계 — 읽는 사람이 반드시 알아야 할 것

1. **arm 효과에 대해 아무것도 말하지 않는다.** controller가 스크립트다.
2. **subagent arm이 no-subagent arm과 동일한 결과를 냈다**(`R_*` = `S_*`).
   스크립트 controller가 subagent 후보를 자기 검색 결과와 같은 방식으로만
   쓰기 때문이다. 즉 **R-vs-S 대비는 smoke에서 시험되지 않았다.** live
   subject라야 subagent를 다르게 쓴다.
3. **해석 계층이 pass-through다.** 피험자는 읽은 것을 그대로 보고하므로
   용어 게이트는 사실상 "옳은 문서를 읽었는가"로 축약된다. 해석 품질은
   측정되지 않았다.
4. **합성 corpus 12파일.** 실제 Vault 일반화를 증명하지 않는다.
5. **process-separated이지 OS-isolated가 아니다.**
6. **incremental gain은 관측 순서에 대한 사후 귀속**이며 인과가 아니다.
   현재 값은 "첫 action이 이득을 독식한다"는 순서 효과에 지배된다.
7. **DS07이 4 arm 전부 `D0`로 실패한다.** discovery 조건에서 gold가 handoff
   read를 요구하는데 스크립트 controller가 정답 문서로 직행한다. 게이트가
   옳은지(entry point를 반드시 거쳐야 하는가) 아니면 gold가 과한지는
   **판정이 필요한 열린 문제**로 남긴다 — smoke 결과에 맞춰 게이트를 낮추는
   것은 metric-fitting이므로 하지 않았다.
8. **live run 0건.** Phase C는 이 문서 동결 후 별건이다.

## 6. 재현

```bash
cd experiments/2026-08-07_handoff_dynamic_controller
python3 build_corpus.py        # corpus + cases + gold (결정론적)
python3 run_calibration.py     # Phase A/A′ — 반드시 먼저, 통과해야 함
python3 run_smoke.py           # Phase B — calibration 실패 시 실행 거부
python3 -m pytest -q test_protocol.py    # 30 passed
```

산출물: `results/calibration.json`, `results/smoke.json`,
`results/smoke_traces.json`(arm별 전체 trace), `corpus_manifest.json`.

## 7. Phase C live-subject pilot

최종 qualification artifact: `results/live_pilot_attempt9.json`.
provider는 `codex exec` 0.146.0, `gpt-5.6-sol`, reasoning effort `medium`이며,
`HD01 × 4 arm × 1`만 실행했다. 이는 pilot이므로 arm effect, 비용 우열, 일반화 성능을
추정하지 않는다.

| arm | valid (`V1` 없음) | critical Recall | hard gate | 관측된 예외 |
|---|---:|---:|---:|---|
| `S_STATIC` | 예 | 1.0 | 통과 | guard refusal 1회 뒤 bounded recovery read |
| `R_STATIC` | 예 | 1.0 | 미통과 | `next_action_accuracy=false`, failure code 없음 |
| `S_DYNAMIC` | 예 | 1.0 | 통과 | 잘못된 read range 1회는 host가 거부, 최종 trace는 유효 |
| `R_DYNAMIC` | 예 | 1.0 | 통과 | guard refusal 1회 뒤 reformulation/re-read |

qualification으로 확인된 것:

1. subject는 `subject/`의 public task와 socket client만 보았고, direct `control/corpus`
   read는 macOS Seatbelt에서 `Operation not permitted`로 차단됐다.
2. host가 search/read/finish 및 range exposure를 기록했고, final citation은 subject의
   own-read trace와 clean judge로 대조됐다.
3. retrieval-only process는 candidate/range/trace/uncertainty contract를 지키며 두 R
   arm에 같은 hint를 제공했고, main subject는 그 hint를 다시 읽어야 했다.
4. post-run immutable-input hash/symlink check와 clean judge가 성공했다.

### 7.1 보존한 invalid attempts

초기 attempt를 삭제하거나 최종 pilot에 합치지 않았다. 각각은 하네스 결함을 발견한
`V1`/pre-score artifact이며 arm data가 아니다.

| artifact | 원인 | 해결 |
|---|---|---|
| `live_pilot.json` | ambient `TMPDIR`가 AF_UNIX socket 길이 제한 초과 | socket root를 `/private/tmp/hdyn-*`으로 고정 |
| `live_pilot_attempt2.json` | launch diagnostics 부족 상태의 Codex exit 1 | stdout/stderr tail을 V1 artifact에 기록 |
| `live_pilot_attempt3.json` | `const`만 가진 JSON Schema를 provider가 거부 | enum/const field에 explicit type 추가 |
| `live_pilot_attempt4.json` | `subject/run/` output을 immutable input drift로 오판, subagent `uniqueItems` 미지원 | run directory 제외, uniqueness를 host validator로 이동 |
| attempt 5 | host가 retrieval state를 `None`으로 재할당해 artifact 전 score exception | state lifecycle 수정; artifact 없음 |
| `live_pilot_attempt6.json` | nested Seatbelt가 client 실행 전 실패 | outer Seatbelt만 enforcement로 사용 |
| `live_pilot_attempt7.json` | static finish-recovery branch가 host protocol에 없음 | bounded `read_candidate → finish` recovery suffix |
| `live_pilot_attempt8.json` | subagent narrower read range를 exact equality로 C3 | containment-based range validation |

attempt 9만 현재 frozen implementation의 qualification 결과다. 다음 primary sweep은
`8 case × 4 arm × 1`이지만, one-replicate descriptive run이고 synthetic corpus의
외부 일반화나 causal arm effect를 주장할 수 없다.
