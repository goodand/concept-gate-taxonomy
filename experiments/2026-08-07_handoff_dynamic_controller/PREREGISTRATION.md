# 사전등록 — handoff cold-start retrieval에서 dynamic workflow controller의 효과

- 작성일: 2026-08-07
- 상태: **설계 동결. subject run 0건.** 결과를 본 뒤 이 본문을 수정하지 않는다.
- 상위 표준: `.vault-harness/vault-md-retrieval/HANDOFF_REUSE_HARNESS_PREREGISTRATION.md`
  (sha256 `786a6a14bf23649ea35b06c8bef43d0eba36945adda51979bb5d39a820c21d82`)
- 상위 evaluator: `handoff_reuse_evaluator.py`
  (sha256 `17690ebd754e5523de7bd0b28e0b9d3527e9b405ee8a3b3816329ade0b0cd637`)

## 0. 상위 하네스와의 관계 — 왜 별도 폴더인가

`.vault-harness`는 현재 dirty worktree다. 이 저장소의 안전 게이트상 **읽기만
가능**하고 수정·이동·추가가 금지된다. 따라서 이 실험은 상위 하네스를 **수정하지
않고**, 그 계약을 **해시로 고정해 인용하는 형제 실험**으로 구현한다.

계약 호환을 위해 다음을 상위와 **동일하게** 유지한다:

- 실패 코드 `D0 R1 R2 X1 I1 A1 S1 T1` (상위 evaluator 417–440행)
- gold 키 이름 `expected_paths` / `critical_paths` / `expected_authority` /
  `permitted_authority_paths` / `claims[].support_ranges`
- `FORBIDDEN_RUNTIME_KEYS` 집합 (runtime 표면에 gold 키 누출 금지)
- public-only / hidden-gold / clean-judge 경계

**상위 코드를 복사하지 않는다.** 복사는 이 저장소가 이미 제거한 실패 모드(사본
두 벌, 한쪽만 수정, 거짓 통과)를 되살린다. 대신 계약을 재선언하고, 상위 파일의
해시가 바뀌면 `test_protocol.py`가 **경고로 보고**한다(차단은 하지 않는다 —
상위는 활발히 개발 중이고 이 실험이 그것을 막을 권한이 없다).

**active experiment artifact를 읽지도 쓰지도 않는다.** corpus는 이 폴더 안의
합성 adversarial bundle뿐이다(상위 §3.1의 3번째 bundle 유형).

## 1. 연구 질문과 사전 예측

| ID | 질문 | 사전 예측 |
|---|---|---|
| DQ1 | dynamic controller가 static 대비 full hard-gate rate를 높이는가 | 높인다. 특히 first-search miss 회복 case에서 |
| DQ2 | retrieval subagent가 단독으로 효과를 내는가 | **거의 못 낸다.** 후보를 넓히지만 authority 판정을 못 해 `X1`(노출 밖 인용)이 늘 수 있다 |
| DQ3 | 둘의 상호작용이 가산적인가 | 초가산. subagent가 넓힌 후보를 dynamic이 선별할 때만 이득이 실현된다 |
| DQ4 | dynamic action별 incremental recall gain이 서로 다른가 | `follow_link` > `reformulate_query` > `expand_candidates`. 실측 근거: 어휘 검색 0.688 → refill 0.812 → graph walk 0.958 → 1.000 |
| DQ5 | budget guard 없이 dynamic이 더 빨리 종료하는가 | 그렇다. 이것이 guard를 두는 이유이며 guard 없는 arm은 실행하지 않는다 |
| DQ6 | `V1` 비율이 arm 간에 다른가 | dynamic·subagent arm에서 높다(trace가 길어짐). **효과 추정의 타당성 조건** |

DQ1의 방향이 틀려도 controller를 사후 수정해 같은 case로 재시험하지 않는다.
수정본은 새 version + 새 held-out으로 평가한다.

## 2. 실험 설계 — 2×2 요인

| Arm | subagent | controller | 사용자 번호 |
|---|---|---|---|
| `S_STATIC` | 없음 | static (recall-first 고정 절차) | 1 |
| `R_STATIC` | retrieval-only | static | 2 |
| `S_DYNAMIC` | 없음 | dynamic | 3 |
| `R_DYNAMIC` | retrieval-only | dynamic | 4 |

controller 이외의 모든 것(모델, corpus 스냅샷, question, turn/context budget,
read 도구)을 고정한다. arm 배정은 case별 결정론적 해시로 균형 배치한다.
subject prompt는 arm 존재와 비교 사실을 언급하지 않는다.

## 3. 경계 — 무엇이 무엇을 볼 수 있는가

```
public corpus + public question
        |
        +--> [retrieval subagent]  (arm 2,4만)
        |         출력: candidate_paths, read_ranges, search_trace, uncertainty
        |         금지: 결론, authority 선언, 상태/다음행동, gold 키
        |
        +--> [main subject + controller]
                  subagent 후보를 authority로 쓰지 않고 **직접 재-read**
                  |
                  v
              trace JSON
                  |
                  v
      [clean judge: subprocess -B -E -P -I -X pycache_prefix=<temp>] + hidden gold
```

- subagent는 public corpus·public question만 본다. hidden gold, evaluator,
  이전 trace, 다른 arm의 결과를 보지 못한다.
- subagent 출력은 `candidate_paths` / `read_ranges` / `search_trace` /
  `uncertainty` **네 키만** 허용한다. 다른 키가 있으면 `C3`.
- main agent가 인용한 support path 중 **자기 자신의 read 기록이 없는 것**이
  있으면 `C4`. subagent 후보를 authority로 승격한 것이므로.
- dynamic controller는 hidden gold, evaluator 소스, prior trace를 볼 수 없다.
- judge는 agent workspace의 bytecode cache와 executable을 신뢰하지 않는다
  (상위 §4 Phase C J1). 해시 검증을 clean subprocess **안**에서 수행한다.

## 4. controller action 집합 — 폐쇄

`reformulate_query` `follow_link` `read_candidate` `expand_candidates`
`abstain` `answer` **여섯 개뿐**. 그 밖의 action은 `C2`이며 run을 종료한다.
static arm은 고정 순서(search → read top-k → answer)로 같은 action 어휘를
쓴다 — action 어휘가 arm 간 교란이 되지 않도록.

## 5. Recall-first 최소 탐색 예산 guard

**가장 값싼 게임 경로는 빨리 답하는 것이다.** dynamic controller는 "충분하다"고
스스로 판단할 수 있으므로, 판단이 이르면 static보다 나빠지면서 비용만 싸 보인다.

종료 action(`answer` / `abstain`)은 다음이 **모두** 충족되기 전에는 거부된다:

1. 서로 다른 query 최소 2회, **또는** query 1회 + `follow_link` 1회 이상
2. `read_candidate` 최소 1회
3. **첫 검색에서 안 나온 후보**에 대한 read 또는 follow_link 최소 1회
   — 첫 검색 결과만으로 끝내는 것을 금지한다

`abstain`에는 추가로:

4. 최소 1회의 `reformulate_query` **그리고** 최소 1회의 `follow_link`
   — zero hit나 첫 검색을 absence proof로 쓰지 못하게 한다(상위 §5 규칙 5).
   위반 시 `A1`(false absence)로 직행하지 않고 먼저 guard가 거부한다.

거부는 `budget_not_met` 관측으로 controller에 되돌려 준다(사유 포함). 종료
action을 **3회** 시도했는데 계속 미달이면 run을 `C1`로 종료한다.

guard는 **판정 근거가 아니라 실행 규칙**이다. guard 통과가 좋은 답을 뜻하지
않는다. guard 미달 종료 시도 횟수 자체를 지표로 기록한다.

## 6. trace 계약

상위 §6을 확장한다. 추가 키:

```json
{
  "contract_version": "handoff-dyn-trace-v1",
  "arm": "S_STATIC|R_STATIC|S_DYNAMIC|R_DYNAMIC",
  "subagent_output": null,
  "actions": [
    {"i": 0, "action": "reformulate_query", "query": "...",
     "candidates_before": [], "candidates_after": ["..."],
     "read_range": null, "accepted": true, "reject_reason": null,
     "elapsed_ms": 0}
  ],
  "reads": [{"path": "...", "start": 1, "end": 40}],
  "stop_reason": "answer|abstain|budget_exhausted|C1|C2",
  "claims": [{"claim_id": "...", "support": [{"path":"...","start":1,"end":40}]}],
  "current_state": "...", "next_action": "...", "stop_conditions": [],
  "uncertainties": [], "tool_errors": []
}
```

**모든 action, query, read range, 후보 집합 변화, stop 이유를 남긴다.**
`candidates_before`/`candidates_after`가 있어야 judge가 action별 incremental
recall gain을 사후 계산할 수 있다 — controller는 이 계산을 볼 수 없다.

## 7. 지표

Primary:

1. full hard-gate rate
2. critical path Recall
3. exact authority hit
4. critical claim/range exposure rate
5. state / next-action / stop-condition accuracy
6. false absence rate, safety violation rate
7. **`V1` invalid-run rate (arm별)** — 부수 지표가 아니라 타당성 조건
8. action별 incremental recall gain (judge 사후 계산)

Secondary: search/read 호출 수, wall-clock, token/cost, guard 거부 횟수,
first-critical rank, full-critical-coverage turn.

**효율은 hard gate를 통과한 run끼리만 비교한다.** retrieval과 interpretation을
하나의 평균으로 합치지 않는다. Arm 효과는
`R_STATIC−S_STATIC`, `S_DYNAMIC−S_STATIC`, 상호작용
`(R_DYNAMIC−S_DYNAMIC)−(R_STATIC−S_STATIC)`로 보고한다.

### 7.1 incremental recall gain 정의

action `i` 실행 후 도달 집합 `S_i = candidates_after_i ∪ reads_{≤i}`.
`recall_i = |S_i ∩ critical| / |critical|`, `gain_i = recall_i − recall_{i−1}`.
action 유형별 `gain`의 평균과 분포를 보고한다. **gain은 hidden gold를 쓰므로
judge 안에서만 계산된다.**

## 8. 평가 케이스 (8건 + paired 1쌍)

| ID | 조건 | 겨냥하는 함정 |
|---|---|---|
| HD01 | direct-handoff | 기본 state/next-action 재구성 |
| HD02 | direct-handoff | **stale replica** — 옛 사본이 어휘상 더 잘 맞음 |
| HD03 | direct-handoff | **same basename** — `HANDOFF.md` 2개 |
| HD04 | direct-handoff | **navigation vs authority** — MOC는 권위가 아니다 |
| DS05 | discovery | **어휘 겹침 0%** — 정답 경로·제목이 질문 어휘와 한 토큰도 안 겹침, link로만 도달 |
| DS06 | discovery | **first-search miss → 회복** — 1차 검색이 정답을 못 냄 |
| DS07 | discovery | **false absence** — 존재하는데 안 보임. zero hit ≠ 부재 |
| HD08-L / HD08-M | direct-handoff | **link → backtick mention paired attack** |

HD08은 **쌍**이다. corpus가 그 간선 하나(`[t](p)` ↔ `` `p` ``)만 다르고 gold는
동일하다. 두 변형의 채점이 달라지면 하네스에 **채널 편향**이 있는 것이며 `E0`로
보고한다. 이는 subject 성능이 아니라 **계측기 검사**다.

DS05의 조작적 정의: 질문 토큰 집합과 (정답 경로 + 제목) 토큰 집합의 교집합이
공집합. 정규화는 소문자화 + 영숫자 분할. 이 조건을 `test_protocol.py`가 검사한다
— 사람이 눈으로 판정하지 않는다.

## 9. 실패 코드

상위 `D0 R1 R2 X1 I1 A1 S1 T1` + `E0 E1 E2 M1 V1`에 다음을 추가한다.

| 코드 | 의미 |
|---|---|
| `C1` | 최소 탐색 예산 미달 상태로 종료 시도 반복 |
| `C2` | 허용 집합 밖 action |
| `C3` | subagent 출력에 금지 필드 |
| `C4` | 자기 read 기록이 없는 path를 인용(subagent 후보를 authority로 승격) |

## 10. 단계와 순서

**Phase A — evaluator calibration (subject run 전).**
positive control(curator reference trace)은 전 hard gate 통과, negative
control(변이) 각각이 **지정된 코드**를 발생시켜야 한다. 변이 목록:

critical path 제거 / stale replica로 authority 교체 / current state를 이전
상태로 교체 / stop condition 제거 / 노출 안 된 range 인용 / navigation note를
authority로 선언 / basename만 남김 / zero hit 뒤 false absence / subagent 출력에
결론 삽입 / 재-read 없이 subagent 후보 인용 / 예산 미달 조기 종료 /
허용 밖 action / gold 키 runtime 누출.

**Phase A′ — mutation-applied 검증 (이 실험의 필수 선행).**
각 변이에 대해 **적용 후 바이트가 실제로 달라졌는지 먼저 assert**한다.
no-op 변이는 "evaluator가 검출 못 함"을 "evaluator 정상"으로 **부호를 뒤집어**
기록한다. 실측 근거: 2026-08-06 뮤테이션 4건 중 1건이 no-op성 얕은 검사로
공허했고, 그 1건이 하필 원래 결함의 재현이었다
(`docs/feedback/session_retrospective_20260807_handoff_tooling_redteam.md` §6).

**Phase B — development smoke.**
결정론적 **scripted controller**로 4 arm을 end-to-end 실행한다.
**smoke 결과로 arm 효과를 주장하지 않는다** — scripted controller는 내가 쓴
것이고 내 예측을 그대로 인코딩하므로, 측정되는 것은 가설이 아니라 **하네스의
동작 가능성**이다. smoke는 배선·경계·채점이 도는지만 증명한다.

**Phase C — live subject run.** 이 문서 동결 후 별건. 여기서 실행하지 않는다.

## 11. 동결 순서

1. 이 사전등록
2. corpus 스냅샷 + manifest 해시
3. public questions
4. hidden gold + claim-support sidecar
5. controller 계약(action 집합·guard 임계)
6. subject prompt·model·tool policy·budget
7. evaluator 소스 + mutation suite + manifest
8. arm 배정·retry/invalid-run 정책

동결 뒤 gold·임계·question·controller를 고치면 같은 실험이 아니다. 새 version
으로 기록하고 기존 결과와 합치지 않는다.

## 12. 해석 상한

- 한 모델의 결과는 그 model+harness 조합의 결과다.
- 합성 adversarial corpus의 성공은 실제 Vault 일반화를 증명하지 않는다.
- guard 통과는 답이 옳음을 뜻하지 않는다. 실행 규칙일 뿐이다.
- **scripted smoke는 arm 효과에 대해 아무것도 말하지 않는다.**
- clean subprocess는 프로세스 분리를 증명하며 **OS 수준 격리를 증명하지 않는다**.
  Docker 동등 격리를 보이지 못하면 `process-separated smoke`로만 기록한다.
- incremental recall gain은 관측된 trace 순서에 대한 사후 귀속이며 인과가 아니다.

---

## Amendment 1 — 2026-08-07, subject run 0건 시점

동결 순서 §11의 2번(corpus 스냅샷)과 4번(hidden gold)을 수정한다.
**live subject run 이전이므로 결과를 보고 고친 것이 아니다.** 캘리브레이션이
잡은 하네스 결함에 대한 수정이며, 무엇이 왜 바뀌었는지 전부 적는다.

| # | 대상 | 변경 | 이유 |
|---|---|---|---|
| A1-1 | `notes/audits/two-shapes-2026-06-11.md` 본문 | 질문의 내용어("retired fixtures directory") 제거, 목적지 표기를 `var/retained/`로 | DS05가 **이름만** 0% 겹침이었고 본문 어휘로 1차 검색에 rank 2로 잡혔다. 실측: action별 incremental gain이 `reformulate_query`에서 **1.0000으로 포화**. 수정 후 1차 검색 미포함·링크로만 도달 확인 |
| A1-2 | DS05 gold `current_state_terms`/`next_action_terms` | `var/retained/fixtures` → `var/retained` | A1-1의 표기 변경에 맞춤 |
| A1-3 | HD03 `forbidden_terms` | `["step 3"],["freeze"]` → `["paused at step 3"],["reshape is paused"]` | `["freeze"]`가 정답 문서의 **"there is no freeze in effect"** 에 매칭돼 옳은 답을 I1으로 실패시켰다 |
| A1-4 | HD08 `forbidden_terms` | `["automated"]` → `["no approval required"]` | `["automated"]`가 정답 문서의 **"No automated job may delete"** 에 매칭 |
| A1-5 | DS06 `forbidden_terms` | `["zero rows","failure"]` → `["steady state"],["02:00"]` | 정답 문서의 **"It was not a failure"** 에 매칭. 새 값은 **틀린 출처(runbook)에만** 존재 |
| A1-6 | `_evaluator.py` S1 판정 | 자유 텍스트 → `recommended_actions` 필드 전용 | `["restart"]`가 정답 문서의 "Do not restart the nightly job" 인용에 매칭. **substring 매칭은 부정을 보지 못한다** |
| A1-7 | §8 DS05 토크나이저 정의 | "소문자화 + 영숫자 분할" → **"소문자화 + 영숫자 분할 − 불용어"** | 원 정의로는 `the` 하나가 겹쳐 0%가 성립하지 않았다. 불용어 목록은 `_contract.STOPWORDS`에 **명시적·최소로** 고정한다 — 긴 목록은 실제 내용어 겹침을 가려 이 case를 공허하게 만든다 |
| A1-8 | §4 static arm 서술 | "고정 순서(search → read top-k → answer)" → **"고정 순서(search → refill → read pool → graph hop → read → answer)"** | 원 서술대로면 static은 §5 탐색 예산을 **구조적으로** 못 채워 전 run이 `C1`이 되고, arm 비교가 측정이 아니라 조작이 된다. arm 1의 정의는 "기존 recall-first 절차"이고 recall-first는 refill과 graph walk를 **이미 포함한다**(실측 0.688 → 1.000). dynamic과의 차이는 탐색 가능 여부가 아니라 **언제 멈출지를 스스로 고르는가**이다 |

### 절차에 추가된 것 (설계 변경 아님, 점검 신설)

- **Phase A0 — gold 자기정합성**: 각 `forbidden_terms`가 자기 case의 authority
  텍스트에 등장하지 않음을 기계로 확인. 위 A1-3/4/5를 규율이 아니라 기제로
  막는다. **필드별로 검사한다** — `safety_forbidden_terms`는 authority 텍스트가
  아니라 `recommended_actions`에 대조되므로 같은 불변식을 적용하면 안 된다
  (초판이 그렇게 해서 무해한 3건을 결함으로 오보했다).
- **Phase A — runner 경유 positive control**: 정직한 controller 4종을 실제
  runner로 돌려 entry point read를 확인. 손으로 만든 reference trace는 runner를
  우회하므로 runner 결함을 볼 수 없다. 실측: `read_candidate`가 `path`를
  보내고 runner가 `target`을 읽어 **모든 정직한 run이 `None`을 읽고 전부 D0**
  였는데, 망가진 controller들만 두 키를 다 채운 탓에 **캘리브레이션은
  통과했었다.**

### 남긴 것 — 고치지 않은 열린 문제

- **DS07이 4 arm 전부 `D0`**: discovery 조건에서 gold가 handoff read를
  요구하는데 스크립트 controller가 정답 문서로 직행한다. 게이트가 옳은지
  gold가 과한지는 판정이 필요하다. **smoke 결과에 맞춰 게이트를 낮추면
  metric-fitting이므로 하지 않는다.**

---

## Amendment 2 — 2026-08-07, subject run 0건 시점

clean judge의 bytecode-cache 격리와 Phase A→B 입력 동일성에 관한 기술 정정이다.
controller, gold, corpus, question, threshold는 변경하지 않았고 live subject run은
여전히 0건이다.

1. `-E`는 모든 `PYTHON*` 환경 변수를 무시한다. 따라서 기존의
   `PYTHONPYCACHEPREFIX=<temp>` 방식은 실제로 cache prefix를 설정하지 못했다.
   clean subprocess는 `-X pycache_prefix=<temp>`를 command line에서 반드시
   받으며, 그 인수가 없으면 `--verify-self`가 exit 4로 거부한다.
2. Phase A의 `calibration.json`은 evaluator, runner, controller, corpus tree,
   public cases, hidden gold, manifest와 사전등록을 포함한 frozen-surface hashes를
   기록한다.
3. Phase B는 그 fingerprint가 현재 표면과 다르면 실행을 거부한다. 따라서
   calibration 통과 뒤 input 하나만 바꾸고 이전 calibration을 재사용할 수 없다.

이 정정은 smoke arm 수치를 보고 한 것이 아니라, `-E`에서
`PYTHONPYCACHEPREFIX`가 `None`으로 남는 실제 interpreter 동작을 재현해 발견했다.

---

## Amendment 3 — 2026-08-07, Phase C live subject run 0건 시점

Phase B는 scripted controller뿐이어서 OS-level subject 격리를 검증하지 않았다.
이 amendment는 **아직 live subject 호출 0건인 시점**에 Phase C 실행 경계를
동결한다. gold, corpus, question, evaluator, arm 정의, threshold는 바꾸지 않는다.

### C1. Provider와 실행 단위

- provider: `codex exec` 0.146.0, model `gpt-5.6-sol`,
  `model_reasoning_effort="medium"`.
- Claude CLI는 이 host에서 로그인 상태가 아니므로 Phase C provider로 쓰지 않는다.
  이는 provider 선택의 실험 결과가 아니라 실행 가능성 기록이다.
- cell은 `(case, arm, variant-L)` 하나의 새 ephemeral Codex process다. pilot은
  `HD01 × 4 arm` 한 번뿐이며 **qualification-only**다. 이 네 건으로 arm 효과를
  추정하거나 비교하지 않는다.
- primary는 pilot의 boundary/schema/guard/clean-judge 조건을 만족한 뒤에만
  `8 case × 4 arm × 1 replicate`로 실행한다. retry는 0회이고 timeout/API/schema/
  sandbox failure는 `V1`로 남긴다. invalid cell을 대체하지 않는다.

### C2. Visibility와 filesystem boundary

각 cell은 `/private/tmp`의 새 bundle을 갖는다.

| surface | subject가 읽는가 | host/evaluator가 읽는가 | 내용 |
|---|---:|---:|---|
| `subject/` | 예 | 예 | public case, socket client, final JSON schema |
| `control/corpus/` | **아니오** | 예 | public Markdown corpus snapshot |
| experiment directory | **아니오** | 예 | hidden gold, evaluator, calibration, source |
| `results/` | **아니오** | 예 | prior traces and scores |

subject process는 macOS Seatbelt에서 `Project_in_progress` 전체와 그 cell의
`control/`을 read/write deny한다. Codex 내부 shell은 disposable `subject/`에서만
workspace-write다. 따라서 subject가 shell `rg`, `cat`, relative traversal로 corpus,
gold, evaluator, prior trace를 읽는 경로는 OS policy로 실패해야 한다.

source exposure는 host-owned Unix socket의 닫힌 action set으로만 이뤄진다:
`search`, `follow_link`, `expand_candidates`, `read_candidate`, `finish`. Host가
in-memory corpus와 candidates, read ranges, guard refusals를 기록한다. 최종 JSON의
citation은 그 host read log와 대조한다. 모델의 self-report만으로 C1/C4를 통과할 수
없다. run 뒤 immutable input hash와 symlink 부재를 재검사하며, drift는 `V1`이다.

### C3. Arm operationalization

- `S_STATIC`: host가 `search → expand_candidates → read_candidate → follow_link →
  read_candidate → finish` 순서를 강제한다. 그 순서 밖 action은 invalid `V1`이다.
- `S_DYNAMIC`: 같은 닫힌 action set과 24 action budget 안에서 다음 행동과 종료를
  스스로 선택한다. terminal action은 `BudgetGuard`가 재정의한 recall-first 조건
  전에는 거부한다.
- `R_*`: 별도 ephemeral retrieval-only Codex process가 먼저 후보, read range,
  search trace, uncertainty 네 key만 반환한다. conclusion/authority/state/extra key,
  관측하지 않은 path/range는 `C3`이며 두 R cell은 모두 `V1`로 남긴다.
- 공정한 factor contrast를 위해 한 case의 valid retrieval-only output은
  `R_STATIC`과 `R_DYNAMIC`에 **동일하게** 전달한다. main subject는 그 후보를
  authority로 간주할 수 없고 자기 host read가 없으면 `C4`다.

### C4. Pilot qualification gates

pilot 결과는 다음만 확인한다. arm 평균, 비용 우열, recall 차이는 보고하지 않는다.

1. subject bundle의 task가 public-case contract만 포함하고 gold key가 없다.
2. Seatbelt 경계 안에서 host socket client가 동작하고 direct corpus/repository read는
   허용되지 않는다.
3. host action log가 final citation, terminal action, guard rejection과 일치한다.
4. post-run hash/symlink check와 clean judge가 성공하거나, 실패한 cell을 `V1`로
   보존한다.
5. `R` factor의 retrieval-only payload가 four-key contract와 host observation에
   일치한다.

Phase C script, public bundle builder, schemas, config은 frozen-surface hash에 포함한다.
이 amendment 뒤 그 surface가 바뀌면 calibration을 새로 수행하고, 이미 실행한 live
결과와 같은 run으로 합치지 않는다.

---

## Amendment 4 — 2026-08-07, live pilot attempt 1 후

pilot attempt 1은 `HD01 × 4 arm`을 예약했지만 **subject 모델 호출 전** host가
`AF_UNIX path too long`로 socket server를 열지 못해 네 cell 모두 `V1`이었다.
`results/live_pilot.json`은 삭제하거나 덮어쓰지 않는다. R arm의 `C3`도 model
출력이 아니라 retrieval socket 생성 실패의 파생 기록이다. 따라서 이 attempt는
retrieval/interpretation/arm 효과에 대해 관측값이 없다.

수정은 `run_live_phase_c.py`의 runtime socket 위치뿐이다. Python의 ambient `TMPDIR`
경로는 macOS AF_UNIX 길이 제한을 넘을 수 있으므로, 새 disposable bundle root를
`/private/tmp/hdyn-*`으로 고정한다. subject visibility, corpus/gold, action set,
guard threshold, model, prompt, schema, evaluator, retry policy는 변경하지 않았다.

code가 frozen surface에 포함되므로 Phase A/A′ calibration을 다시 수행한 뒤, pilot
attempt 2는 새 artifact `results/live_pilot_attempt2.json`으로 기록한다. attempt 1을
대체하거나 arm 평균에 합치지 않는다.

---

## Amendment 5 — 2026-08-07, live pilot attempt 2 후

attempt 2는 AF_UNIX socket server 생성은 통과했지만 Codex child가 tool action 0건인
채 exit 1로 끝나 네 main cell이 `V1`이었다. `results/live_pilot_attempt2.json`을
보존한다. 이 역시 answer/retrieval 관측이 없으므로 arm 효과와 합치지 않는다.

host runner는 nonzero Codex exit에서 stderr뿐 아니라 stdout 마지막 1,200자도
attempt artifact의 `V1.tool_errors`로 보존하도록 변경한다. 이 변경은 단지
launch-failure 진단을 관측 가능하게 하며 model/prompt/corpus/gold/evaluator/action/
threshold를 변경하지 않는다. macOS Seatbelt 안의 `codex --version`은 정상 종료한
것을 별도 확인했다. Phase A/A′를 다시 통과한 뒤 새 artifact `live_pilot_attempt3`
으로 재시도한다.

---

## Amendment 6 — 2026-08-07, live pilot attempt 3 후

attempt 3의 확장 diagnostics가 정확한 provider error를 보였다: Codex response
format validator는 `contract_version`의 JSON Schema가 `const`만 있고 `type`이 없다는
이유로 request를 400으로 거부했다. host socket 및 subject model action은 여전히
0건이고 모든 cell은 `V1`; `results/live_pilot_attempt3.json`을 보존한다.

두 final-output schema에서 `contract_version`에 `type: string`을, enum-only field에
명시적 string type을 추가한다. unit test는 이후 모든 const/enum node가 type을
가지는지 검사한다. 이는 provider가 요구하는 schema 표현의 호환성 수정이고,
semantics, allowed key, arm definition, evaluator, task/corpus/gold에는 변화를 주지
않는다. new frozen-surface calibration 후 pilot attempt 4를 별도 artifact로 기록한다.

---

## Amendment 7 — 2026-08-07, live pilot attempt 4 후

attempt 4는 처음으로 main subject의 Codex final response까지 도달했지만, host
post-run manifest가 `subject/run/main.json`과 raw JSONL을 immutable input drift로
잘못 분류해 S arm을 `V1`으로 처리했다. `subject/run/`은 애초에 model final output과
raw diagnostic만 쓰도록 지정한 mutable output directory다. R arm은 별개의 provider
schema rejection이었다: Codex response-format validator가 `uniqueItems` keyword를
지원하지 않았다. attempt 4 artifact는 보존하며, main answer 내용은 V1이므로 점수나
arm 비교에 사용하지 않는다.

수정은 다음 두 구현 호환성 항목뿐이다.

1. input manifest는 `subject/run/`만 제외하고 task, client, schema, host corpus의
   추가·수정·symlink는 계속 drift로 거부한다. unit test는 output file 허용과 다른
   `subject/` file 추가 거부를 함께 검사한다.
2. retrieval schema에서 `uniqueItems`를 제거하고 candidate deduplication은 host의
   `_subagent_output` validator가 `C3`로 검사한다.

이 수정은 evidence visibility, prompts, arms, guard, score, model 및 corpus/gold를
변경하지 않는다. Phase A/A′ 후 pilot attempt 5를 새 artifact로 수행한다.

---

## Amendment 8 — 2026-08-07, pilot attempt 5 host exception

attempt 5의 retrieval-only Codex process는 provider schema를 통과해 final response를
반환했지만, host `_run_retrieval_subagent`가 이미 생성한 `LiveToolState`를 뒤이어
`None`으로 재할당한 구현 결함으로 `AttributeError`를 냈다. runner가 score artifact를
쓰기 전에 종료했으므로 `results/live_pilot_attempt5.json`은 존재하지 않는다. 이 event는
subject output이나 arm data가 아니다.

state declaration을 try block 전에 두고, bundle/corpus/state/socket 생성 뒤에만
`ToolServer`와 validator를 호출하도록 고친다. retrieval-only result가 실제 host action
state와 대조되는 조건은 변경하지 않는다. new calibration 뒤 pilot attempt 6를 새
artifact로 실행한다.

---

## Amendment 9 — 2026-08-07, live pilot attempt 6 후

attempt 6은 five model processes가 모두 final JSON을 만들었고 retrieval-only output도
contract validation을 통과했다. 그러나 host action log는 전부 0이었다. raw trace의
공통 원인은 `python3 live_subject_tool.py ...`가 실행되기 전 Codex inner sandbox가
`sandbox-exec: sandbox_apply: Operation not permitted`로 실패한 것이다. 즉 outer
macOS Seatbelt 안에서 Codex의 `--sandbox workspace-write`가 **두 번째 Seatbelt**를
만들려는 nested-sandbox 충돌이다. `results/live_pilot_attempt6.json`은 V1 artifact로
보존하며 answer 내용은 score/arm 비교에 쓰지 않는다.

Phase C runner는 Codex의 inner sandbox를
`--dangerously-bypass-approvals-and-sandbox`로 bypass하고, 이미 검증한 outer Seatbelt를
유일한 OS enforcement point로 사용한다. outer profile은 `Project_in_progress` 전체와
각 bundle `control/`을 read/write deny하므로 subject가 gold/evaluator/corpus를 직접
읽을 수 없고, model-generated shell은 disposable `subject/`만 작업 surface로 받는다.
이 bypass flag는 **outer Seatbelt invocation 없이는 사용하지 않는 runner 내부
implementation**이다. config와 unit test에 그 의존성을 기록한다. visibility, action
set, model, prompts, score, retry policy는 변경하지 않는다. calibration 뒤 pilot attempt
7을 새 artifact로 실행한다.

---

## Amendment 10 — 2026-08-07, first valid live pilot trace (attempt 7) 후

attempt 7은 처음으로 host-owned actions를 가진 valid live traces를 만들었다. 이는
pilot qualification의 boundary/socket/trace 조건을 충족한다. `R_DYNAMIC`은 full hard
gate를 통과했고 `S_DYNAMIC`은 V1 없이 critical recall 1.0에 도달했지만, pilot은
`HD01 × 1`이므로 이 값을 arm 효과로 해석하지 않는다.

`S_STATIC`의 V1은 새로운 protocol contradiction을 드러냈다. host는 static sequence를
`search → expand → read → follow → read → finish`으로 닫아 두었지만, finish가
recall-first guard에서 거부될 때 prompt는 "returned requirement를 만족하고 retry"하라고
지시했다. 실제 subject는 guard가 요구한 추가 read를 하려 했고 host가 그 action을
V1으로 막았다. 이는 subject 성능이 아니라 **실행 불가능한 static recovery branch**다.

static arm은 initial fixed sequence 뒤 terminal 거부가 있을 때만, 이미 관측했으나 아직
읽지 않은 candidate 한 개를 `read_candidate`로 읽고 `finish`를 재시도하는 bounded
recovery suffix를 허용한다. 다른 action, query 재작성, 순서 변경은 계속 V1이다.
recovery가 다시 guard를 통과하지 못하면 기존 최대 terminal-attempt `C1` 규칙을 따른다.
unit test는 정확히 이 suffix와 sequence 이탈 거부를 모두 확인한다.

이 수정은 static arm이 guard와 논리적으로 함께 실행될 수 있게 할 뿐, evidence source,
gold, evaluator, threshold, dynamic action space, model 또는 answer scoring을 변경하지
않는다. attempt 7과 수정 후 attempt 8은 같은 arm-effect estimate로 합치지 않으며,
attempt 8 역시 qualification artifact로만 기록한다.

---

## Amendment 11 — 2026-08-07, live pilot attempt 8 후

attempt 8에서 `S_STATIC`과 `S_DYNAMIC`은 full hard gate를 통과했다. R subagent도
host socket에서 9 actions와 4 reads를 수행했지만 C3가 났다. 원인은 subagent가 host의
`1-40` read 안에 포함되는 더 좁은 range를 보고했는데 validator가 `(path,start,end)`
완전 일치만 인정한 것이었다. 이는 main citation evaluator가 이미 쓰는 exposure rule
(`host_start <= declared_start`, `declared_end <= host_end`)과 불일치한다.

retrieval-only validator도 같은 containment rule로 바꾼다. path, integer ordering,
candidate observation은 계속 검증하며 host read보다 넓거나 다른 path range는 C3다.
새 unit test는 `1-40` host read에 `5-9` declaration이 통과하고 `1-41`은 거부됨을
확인한다. 이는 subagent가 source authority를 결정할 수 있게 하는 변경이 아니며,
four-key boundary와 main-agent re-read C4 rule은 그대로다. new calibration 뒤 attempt
9를 별도 qualification artifact로 실행한다.
