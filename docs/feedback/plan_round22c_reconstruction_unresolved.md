# 검증·재사용·의존성·구현 계획 — 22c라운드: Reconstruction은 FAIL이 아니라 UNRESOLVED

작성 2026-08-11. 대상 커밋 `57a164c`. 판정: **canary 재실행 불필요. 내 해석이 과했다.**

## 1. 주장 검증 — 5/5 확인, 그리고 내 오류가 리뷰어 지적보다 크다

| # | 지적 | 판정 | 실측 |
|---|---|---|---|
| 1 | Reconstruction FAIL은 의미 판정이 아니라 **lexical matcher** 실패 | **CONFIRMED** | `next_ok = _terms_hit(trace["next_action"], gold["next_action_terms"])`, `_terms_hit`은 그룹 OR·항 AND의 **부분문자열 포함** 검사 |
| 2 | Retrieval PASS가 "필요한 근거를 충분히 읽었다"는 뜻이 아니다 | **CONFIRMED** | 아래 §1-2 |
| 3 | `follow_link`의 출발 경로·결과가 trace에서 사라진다 | **CONFIRMED** | 응답에는 `from_path`·`result_paths`가 있는데 `self._record("follow_link", before)`는 액션명과 before만 남긴다 |
| 4 | assessment sidecar에 생성·검증 코드가 없다 | **CONFIRMED** | `grep -l canary-assessment *.py` → 0건 |
| 5 | 테스트 수는 실행 환경 한정 | **CONFIRMED** | 리뷰어 환경 298 passed / 30 failed. 30건은 Seatbelt 권한 |

### 1-1. 내 문서가 내부적으로 모순이었다

같은 커밋(`57a164c`)에서 이렇게 썼다:

> "실패는 `next_action` 하나다 — 즉 이것은 **하네스 결함이 아니라 subject에 대한
> 결과다**"

그리고 세 단락 뒤에:

> "**왜 `next_action`이 틀렸는지는 이 문서가 말하지 않는다.** … 격리된 judge에
> 위임할 항목"

**둘 다 참일 수 없다.** 원인을 확립하지 않았다면 "subject에 대한 결과"라고 단정할
수 없다. `P-자기보고과장`의 17번째이고, **자기모순을 한 문서 안에 남긴 첫 사례**다.

### 1-2. §2는 리뷰어보다 강하게 말할 수 있다 — subject가 스스로 말했다

artifact의 `uncertainties[0]`:

> "The specific chosen retired-fixtures destination **is not established**: the
> **fixed sequence ended** before `notes/audits/two-shapes-2026-06-11.md` could be
> read, so only the existence of the decision is verified, not its content."

그리고 `S_STATIC` 프롬프트(`run_live_phase_c.py:464-469`)가 **고정 시퀀스를
처방한다**:

> "static: use this fixed sequence: search the task query; expand candidates; …
> then use the host response's `static_next.path` for the required read; then
> finish. **Do not issue another follow or finish before that exact read.** …
> **Do not change the sequence in any other way.**"

관측된 8 action(`search → expand → read → follow_link → read → answer → read →
answer`)은 그 처방과 일치한다 — 두 번째 `answer`는 finish가 한 번 거부된 뒤
"observed candidate 하나를 더 읽고 재시도"라는 처방을 따른 흔적이다.

**즉 `next_action` 불일치의 가장 그럴듯한 기제는 subject의 이해 실패가 아니라
`S_STATIC`이 처방한 시퀀스가 결정 문서에 닿기 전에 끝났다는 것이다** — 그리고
그것은 **arm의 성질이고, 이 실험이 조작하는 바로 그 변수**다. 1칸 1 arm으로는
확립할 수 없다.

동시에 `critical_path_recall=1.0`·`exact_authority_hit=true`인데 그 audit을 읽지
않았다는 것은, **현 gold의 critical path 집합이 next action을 완성하는 데 필요한
read를 필수 근거로 연결하지 않았다**는 뜻이다. Retrieval PASS는 "**현 gold가
요구한 파일을 읽었다**"로 제한해야 한다.

## 2. 재사용 후보 조사

| # | 선례 | 적용 |
|---|---|---|
| R13 | `HANDOFF_REUSE_VALIDATION.md` §175 — **claim별 support path와 required action을 gold에 연결하는 범용 schema** | gold v2의 `support_paths`/`required_reads`. 리뷰어가 인용한 것과 같고, **이미 이식 가능한 표준으로 존재한다** |
| R14 | `EXPERIMENT_METHODOLOGY.md` §11 — **raw 결과와 해석을 별도 커밋·artifact로** | v1 sidecar를 지우지 않고 v2로 supersede하는 근거 |
| R3 | `DESIGN_DECISION_surface_separation.md` §29 — 제작 기록·qualification·모델 payload **물리 분리** | assessment를 원본 밖에 두는 지금 구조가 이미 이것 |
| R5 | `HARNESS_KNOWHOW.md` §151 — 가드의 **존재**가 아니라 위반 입력 차단을 검증 | #4의 sidecar schema 테스트, #3의 trace provenance 회귀 테스트 |
| R15 | 이 실험의 `invalid_run_policy: record-V1-and-do-not-replace` | v1 sidecar를 **덮어쓰지 않는다.** 잘못된 해석도 기록이다 |

**R13이 이번 라운드의 발견이다.** gold v2에 필요한 schema를 새로 설계할 필요가
없다 — `.vault-harness`의 이식 가능한 표준에 claim↔support_path↔required_action
연결이 이미 있다.

## 3. 검증 방법 설계

### 3층의 의미를 좁힌다 — 이름이 주장의 강도를 담아야 한다

| 층 | 지금(과장) | 바꿀 것 |
|---|---|---|
| Retrieval | `PASS` | **`PASS (gold-defined)`** + `required_support_read_recall: not_measured` |
| Reconstruction | `FAIL` | **`UNRESOLVED_PENDING_ADJUDICATION`** + 보조 신호 `next_action_lexical_match: false` |

**`FAIL`이라는 단어를 쓰지 않는 이유**: 이 저장소의 3값 어휘에서 `FAIL`은 "돌았고
실패했다"이고 `BLOCKED`는 "판정을 얻지 못했다"다. lexical 불일치는 **판정을 얻지
못한 것**이므로 `FAIL`이 아니다. 같은 어휘를 산출물에도 적용한다.

### 격리 judge — 무엇을 판정하고, 왜 내가 지금 못 하는가

| 후보 판정 | 뜻 |
|---|---|
| `SUBJECT_SEMANTIC_MISS` | subject가 next action을 실제로 잘못 이해했다 |
| `LEXICAL_MATCHER_FALSE_NEGATIVE` | 의미는 맞는데 gold 항이 표면에 없었다 |
| `GOLD_AMBIGUOUS` | gold의 next_action_terms가 하나의 정답을 지정하지 않는다 |
| `WORKFLOW_EVIDENCE_INSUFFICIENT` | 처방된 시퀀스가 결정 근거에 닿지 못했다 (§1-2의 기제) |

**이 판정은 gold 대조가 필요하다.** 이 운영 맥락은 gold를 읽지 않는다 — 이 세션은
subject가 읽는 corpus·handoff를 저술해 왔으므로, 내가 gold를 읽으면 이후 저술이
오염된다. 따라서 **격리 judge(별도 세션 또는 격리 subagent)에 위임**해야 하고,
그것은 사용자 승인 사항이다. 승인 없이 내가 대신 판정하지 않는다.

### provider 없이 되는 것 / 안 되는 것

```
provider 불필요:  #3 trace provenance 회귀 테스트, #4 sidecar schema 테스트,
                  22b의 공허한 가드 2개
gold 필요      :  격리 judge 판정
provider 필요  :  1 case × 4 arms pilot
```

## 4. 의존성 분석

| 항목 | 파일 | 표면 | closure |
|---|---|---|---|
| v2 assessment sidecar | `results/…_v2.json` | — | 불필요 |
| handoff §3e 정정 | 문서 | — | 불필요 |
| #3 follow_link provenance | `run_live_phase_c.py` | **EXECUTION** | 필요 |
| #4 sidecar schema + 테스트 | 새 `.py` + 새 `test_*.py` | 미등록 가능 / 새 테스트는 EXECUTION 아님 | 사실상 불필요 |
| 22b 큐(공허한 가드 2개 등) | `test_live_phase_c.py` | **EXECUTION** | 필요 |

**#3과 22b를 한 closure에 묶는다.** 리뷰어의 6번과 같다. `run_live_phase_c.py`와
`test_live_phase_c.py`가 둘 다 EXECUTION이므로 따로 하면 closure가 두 번이다.

**gold v2는 이 묶음에 넣지 않는다.** gold 편집은 `hidden_gold/` 접촉이고, 이
맥락에서 금지된다. 격리 위임 항목이며, **기존 canary를 새 gold로 소급 채점하지
않는다**(리뷰어 4번, `record-V1-and-do-not-replace`와 같은 논리).

## 5. 구현 계획 — step by step

### 지금 (closure 불필요)

```
0. v2 assessment sidecar — Reconstruction UNRESOLVED_PENDING_ADJUDICATION,
   Retrieval PASS(gold-defined), v1을 supersede하되 삭제하지 않는다
1. handoff §3e 정정 — "subject에 대한 결과다" 삭제, §1-2의 기제를 후보로 기록
2. 테스트 수에 실행 환경 표기 (Claude host-capable lane)
3. 22c 큐를 handoff에 추가
```

### closure 1회에 묶어서 (22b + 22c)

```
4. 22b: 공허한 가드 2개를 spy/값 대조로, 오염 시험으로 재확인
5. 22b: canary artifact의 `qualification` 필드
6. 22b: release 로그 순서
7. 22c #3: follow_link trace에 target_path·result_paths·static_next_path.
   하나를 제거하면 회귀 테스트가 실패해야 한다
8. 22c #4: sidecar schema + 검증 함수 + 위반 입력 테스트
9. closure → release → commit
```

### 위임 (내가 하지 않는다)

```
10. 격리 judge — 4후보 중 하나 판정. gold 대조 필요
11. gold v2 — support_paths·required_reads (R13의 schema 재사용)
```

### 그 뒤

```
12. 1 case × 4 arms (= 기존 --pilot). 네 값을 따로 보고한다:
    Runtime validity / candidate recall / required-support-read recall /
    reconstruction adjudication
    **arm 효과는 여기서도 주장하지 않는다** (n_per_cell=1)
```

## 6. 낮춰야 할 내 주장

- **"하네스 결함이 아니라 subject에 대한 결과다"** — 확립되지 않았다. 같은 문서가
  세 단락 뒤에 "원인은 not_established"라고 적어 **자기모순**이었다.
- **"Reconstruction FAIL"** — lexical 항 불일치이며, 이 저장소 어휘로는 `FAIL`이
  아니라 판정을 얻지 못한 상태다.
- **"Retrieval PASS"** — "**현 gold가 요구한** 파일을 읽었다"로 좁혀야 한다.
  결정을 담은 audit은 후보로 발견됐고 **읽히지 않았으며**, subject가 그 사실을
  스스로 보고했다.
- **"328 passed"** — Claude host-capable lane 한정. 리뷰어 환경은 298/30이고
  30건은 Seatbelt 권한 부재다.
