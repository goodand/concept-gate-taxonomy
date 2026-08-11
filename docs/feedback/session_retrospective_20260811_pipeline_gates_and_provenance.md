# 세션 회고 — 파이프라인 게이트와 provenance (2026-08-10 ~ 08-11)

- 범위: 독립 검토 **12~19라운드**, Amendment 34~40, 커밋 `423e1d7` ~ `1f12e2f`
- 선행 회고: [`session_retrospective_20260810_primary_gates_and_s1_precision.md`](session_retrospective_20260810_primary_gates_and_s1_precision.md)
  (I57~I73). 이번은 **I74부터** 이어진다.
- 문서 종류: 운영 로그. 동결 아티팩트와 같은 커밋에 섞지 않는다.

> **이 세션의 한 문장**: 개별 결함을 8라운드 동안 하나씩 고쳤고, 그 방식이
> 틀렸다는 것을 사용자 지적으로 알았으며, 파이프라인 전체를 검증하는 도구를
> 만들었더니 **그 도구 자체가 같은 결함을 다시 냈다.**

---

## (1) 신규 이슈 I74~I112

### A. 선언과 기제의 괴리 (12라운드, Amendment 34)

| ID | 이슈 |
|---|---|
| I74 | Amendment 33이 "S1은 자동 지표가 아니다"라고 **선언만** 했고 `full_hard_gate = not codes`가 S1을 그대로 실패로 만들었다. 오탐이 안전한 셀을 죽이고 미탐이 unsafe 셀을 통과시켰다 |
| I75 | `"U1" in codes`가 **안전 모호**와 **사실 모호**를 뭉뚱그려, 사실 이중부정 하나가 셀을 "안전 검토 필요"로 표시하고 감사 분모를 양방향으로 틀리게 했다 |
| I76 | recall **1/12는 recall이 아니었다**. 6문장을 HD02·DS06 **양쪽에** 적용해 12를 만들었으나 9개는 negative이거나 무관한 예다. 정정값 **1/6**(HD02 0/3, DS06 1/3) |
| I77 | recall 테스트가 `total > 0`만 주장해 caught가 1→0이나 6으로 변해도 통과했다. **측정값을 보고만 하고 고정하지 않았다** |
| I78 | 교차항목 대조가 `test_protocol.py`에만 있었다. readiness는 pytest가 아니라 `calibration.json`을 읽으므로, `" ".join()`으로 되돌려도 calibration은 초록이었다 |
| I79 | 철회한 Amendment 32 gold를 삭제해, git history 없는 export에서 그 계기를 재현할 수 없게 됐다 |

### B. 감사가 판정 없이 통과시킬 수 있었다 (13라운드, Amendment 35)

| ID | 이슈 |
|---|---|
| I80 | 판정자에게 **빈 권위 문서**가 갔다. `cases.json`의 `handoff_path`는 **진입점**이지 권위가 아니고, 탐색 케이스(DS05·06·07)에서는 `null`이다 |
| I81 | `not_applicable`이 `adjudicated_full_hard_gate = True`를 반환했다 — **아무도 판정하지 않은 셀이 safety headline을 통과** |
| I82 | 같은 사람이 두 별칭으로 제출해 `n_reviewers: 2`, `single_reviewer_no_agreement_measure: false`, 판정 `safe` |
| I83 | 해시 결속이 result 하나뿐이라 key의 `index`/`action_index`를 고쳐 **다른 셀에 라벨을 적용**할 수 있었다 |
| I84 | trace 없는 행이 제외 목록으로 강등됐고, apply 단계는 그 목록을 **받지도 않아** 라벨 없는 행을 `not_applicable`로 처리했다. I81과 합쳐지면 **깨진 산출물이 통과하는 셀**이 된다 |
| I85 | 초과 label id(`R9999`)가 조용히 통과 — 다른 패킷용 라벨 파일이 받아들여진다는 뜻 |
| I86 | pytest가 `results/` artifact를 직접 썼다. **기댓값을 검사하는 그 실행이 기댓값을 갱신**했다 |
| I87 | handoff가 recall 1/12, calibration 58/58, 옛 필드명, "case ID를 가린다"를 가르쳤다 — **넷 다 현재 계약과 반대** |

### C. 게이트가 배선되지 않았다 (15라운드, Amendment 36)

| ID | 이슈 |
|---|---|
| I88 | `expected_cells`가 **선택 인자**였고 CLI는 넘기지 않았다. 1셀 비-primary artifact가 정상 packet이 됐다(`accepted_cells: 1`) |
| I89 | result↔trace 검사가 **단방향**이라 추가 trace가 무시됐다 |
| I90 | rubric이 `"조건부는 ENDORSE가 아니다"`라고 가르쳤다. 조건이 **금지 상태 그 자체**면 그것은 직접 권고다 — **두 판정자가 같은 잘못된 규칙을 쓰면 높은 합의율로 같은 오답**을 낸다 |
| I91 | rubric의 apply 명령에 packet 인자가 없어 **그대로 실행하면 usage로 떨어졌다** |
| I92 | 동결면 2층 분리를 도입했으나 **실제 변경 단위에서 이득이 0**이었다. 목록이 `_evaluator.py`에, 감사 테스트가 `test_protocol.py`에 있어 둘 다 execution surface |

### D. 진단 도구가 판정을 복제했다 (17라운드, Amendment 38)

| ID | 이슈 |
|---|---|
| I93 | `doctor`가 readiness를 **재구현**하고 qualification 게이트를 아예 빼먹었다. production은 `REFUSED`, doctor는 `0 fail, exit 0`, `_assert_*` 호출 **0건** |
| I94 | `BLOCKED is not a pass`를 **출력하면서 exit 0**을 반환했다 — 사람은 읽고 기계는 못 읽는다 |
| I95 | `status=FAIL` artifact가 `[ok  ] red-team: provider isolation   FAIL`로 렌더됐다. doctor가 `conclusive`만 읽고 `status`를 무시 |
| I96 | offline E2E가 primary를 직접 합성하고, adjudication을 헬퍼로 부르고, 번들을 메모리에서 끝냈다. **"production E2E"라는 주장이 과했다** |
| I97 | 감사 게이트가 **모양만** 검증했다. authorization·완료 시도·config 해시 미검사 → 손으로 만든 32칸이 통과 |
| I98 | red-team이 **v7/surface-v2를 하드코딩**했고 대상은 v9/surface-v3였다. artifact에 config identity가 없어, **한 번도 보지 않은 config**에 대해 PASS artifact가 만들어졌다 |
| I99 | red-team **fail-open**: `leak = reachable and not expected_reachable`이라 도달 가능해야 하는 probe가 막힌 경우가 실패로 계산되지 않았다. sandbox가 아예 안 도는 환경에서 leak 0으로 PASS |

### E. 두 번째, 더 약한 구현 (18~19라운드, Amendment 39~40)

| ID | 이슈 |
|---|---|
| I100 | 완료 후 변조된 결과가 통과했다(`accepted_after_mutation: true`). 감사가 `output_file`을 **이름으로** 대조. **`verify_primary_attempt_artifacts()`는 한 달 전부터 `output_sha256`을 대조 중이었다** |
| I101 | mutation gate가 **adjudicator의 qualification 호출부 제거**를 못 잡았다(`e2e_passed_with_adjudicator_qualification_disabled: True`). E2E가 정답만 제출했기 때문 |
| I102 | mutation이 **active worktree의 production 파일을 직접 변조**하고 `finally`로 복원했다 — 정상 종료에서만 안전 |
| I103 | receipt가 **packet에서 멈췄다**(`key_mode: null`, `bundle_audit_mode: null`). 최종 JSON만 읽어서는 합성과 실제 감사를 구별 못 함 |
| I104 | `status not in (None, "PASS")`가 **typed verdict 없는 구형 artifact를 PASS와 같은 문**으로 통과시켰다 |
| I105 | `remaining_primary_attempts`가 `started` 행만 셌다. 실제 claim은 체인·legacy pin·이전 artifact 무결성까지 본다 → **손상된 원장에서 doctor는 "여유 있음", claim은 거부** |
| I106 | **커밋된 상태의 artifact가 이미 stale**. Amendment 39를 덧붙인 뒤 재생성하지 않았고, 내가 보고한 수치는 그 커밋의 것이 아니었다 |

### F. 내가 만든 이슈

| ID | 이슈 |
|---|---|
| I107 | rubric 편집이 **조용히 미적용**됐다(`str.replace` 미매치는 예외 없이 원문 반환). 확인 없이 "갱신했다"고 보고 |
| I108 | handoff를 "개선"하면서 `ALLOWED_CONFIG_NAMES` 등록 지시를 **삭제**했다. 그 handoff를 따르면 실행이 안 된다 |
| I109 | "canonical path 원칙을 적용했다"고 썼으나 **정반대**를 했다(판정 복제) |
| I110 | 설계 판정(동결면 분리) 전에 **vault를 검색하지 않았다**. 나중에 검색하니 `DESIGN_DECISION_surface_separation.md`(2026-07-28, 동결)가 나왔다 |
| I111 | qualification 재실행을 반복해서 **"유료"**라고 썼다. 사용자 정정: workflows로 대체 가능 — 비용이 아니라 시간·순서 문제 |
| I112 | obligation 커버리지가 **개수 비교**(`covered >= 5`)였다. 개수는 **어느** stage가 미보호인지 말하지 못하고, 실제로 둘이 미보호였다 |

---

## (2) 재현 횟수가 증가한 반복 이슈

| 패턴 | 이전 | 이번 증가 | 누적 |
|---|---|---|---|
| **P-헬퍼는보고배선은안봄** | 2 | I88, I93, I100, I101, I105, 자격검사(17R #5) | **8** |
| **P-자기보고과장** | 5 | I96, I103, I106, I109, I111 | **10** |
| **P-자기수정회귀** | 5 | I92, I96, I103, I107, I108 | **10** |
| **P-계측기미검증** | 6 | I99, I104 | **8** |
| **P1**(참이나 불필요한 명제 검사) | 19 | I77, I112, launcher-존재검사(출시 전 차단) | **22** |
| **P-문서가계약을가르침**(신규) | — | I87, I90, I91, I107 | **4** |
| **P-두번째구현**(신규) | — | I93, I100, I105 | **3** |

### P-헬퍼는보고배선은안봄이 2 → 8. 이 세션의 지배적 패턴이다

이전 회고에서 **2건**이었던 것이 8건이 됐다. 형태가 매번 같다:

```
기능을 헬퍼에 넣는다
→ 헬퍼를 직접 부르는 테스트를 쓴다        ← 여기서 구현을 보고 쓴다
→ 초록
→ 호출부는 그 인자를 넘기지 않는다
```

**I88이 가장 선명하다.** `build(rp, expected_cells=32)`로 테스트하면서 `main()`은
`build(result_path)`를 불렀다. 테스트가 **구현을 보며 작성돼 구현의 구멍을 그대로
물려받았다.**

**I100은 더 나쁜 변종이다.** 헬퍼가 없어서가 아니라 **이미 있는데 안 부르고 더
약한 두 번째 구현을 썼다.** `verify_primary_attempt_artifacts()`는 한 달 전부터
`output_sha256`을 대조했고, 감사는 한 import 거리에서 `output_file` 이름만 봤다.

### P-자기수정회귀가 5 → 10. **결함을 끝내려고 만든 도구가 같은 결함을 냈다**

- I96: 반복을 끝내려고 만든 E2E가 "production E2E"라 주장하며 실제로는 하류만
  덮었다
- I103: Amendment 39가 "표식이 최종 번들까지 간다"고 쓴 바로 그 커밋에서 표식이
  packet에서 멈췄다
- I92: 동결면 분리를 도입한 변경이, 목록을 execution surface에 두는 바람에
  **이득을 0으로 만들었다**
- I107·I108: 문서 편집 자체가 조용히 실패하거나 지시를 삭제했다

### P-자기보고과장이 5 → 10. I106이 질적으로 다르다

이전 5건은 "고쳤다"의 강도 과장이었다. **I106은 수치가 커밋 상태를 설명하지
않았다** — 검증 가능한 사실을 틀리게 보고했다. Amendment 39를 덧붙인 뒤 artifact를
재생성하지 않았고, 그것을 잡는 **결정론적 테스트가 이미 실패하고 있었다.**

---

## (3)(4) 해결 근거와 해결 유무

| ID | 해결 | 근거의 강도 |
|---|---|---|
| I74, I75 | 해결 | 이름 변경(fail-loud) + 기원별 분리, 소비처 전수 조사 |
| I76, I77 | 해결 | 케이스별 fixture + **벡터 핀**, 산출물 분리 |
| I78 | 해결 | calibration에 Phase A'' 추가, 58/58 → **60/60** |
| I79 | 해결 | withdrawn 사본 + sidecar, glob 부재를 테스트가 고정 |
| I80 | 해결 | 동결 manifest, fail-closed. 실측 DS06 3문서 1,984자 |
| I81, I84 | 해결 | `None` 반환 + fail-closed, 음성 테스트 |
| I82 | **부분** | 배정 동결·해시 결속·고유 id 강제. **같은 사람이 두 계정을 쓰는 것은 막지 못한다 — 그렇게 명시** |
| I83 | 해결 | result→packet→key→labels + rubric/manifest/spec, 위치 재유도 |
| I85 | 해결 | 정확한 집합 일치 |
| I86 | 해결 | `measure_s1_recall.py` 분리, 테스트는 대조만 |
| I87, I91 | 해결 | handoff 갱신 + **rubric drift 테스트**(명령 인자 수를 CLI와 대조) |
| I88, I89 | 해결 | 단일 `validate_audit_input` + **CLI 배선 테스트**, `expected_cells=None` 선택지 제거 |
| I90 | 해결 | 3단 판정 순서 + **판정자 자격 fixture**(Q1/Q2·Q6/Q7 판별쌍) |
| I92 | 해결 | 목록을 데이터 파일로, 감사 테스트 분리. 실측 `execution drift: []` |
| I93, I95 | 해결 | doctor를 **위임**으로. #95는 구조적으로 소멸 |
| I94 | 해결 | exit code 3값(0/1/2), doctor·red-team 2종 |
| I96 | **부분** | 주장을 `offline downstream E2E`로 낮추고 범위 확대(CLI 판정·번들 재읽기·음성 7). **provider 실행·qualification·authorization·claim은 여전히 우회** |
| I97, I100 | 해결 | `_provenance.py`가 기존 검증기 조합, 파서 1개·직접 읽기 0건 |
| I98 | 해결 | authorization에서 대상 config를 읽고 `checked_configs` 기록, readiness가 요구 |
| I99, I104 | 해결 | `conclusive`/`status`, `status=None` → BLOCKED |
| I101, I112 | 해결 | 소스 변이 + 별도 프로세스 + applied-check + **집합 일치** |
| I102 | 해결 | 실험 디렉터리 임시 복사에서 변이 |
| I103 | 해결 | packet→key→번들 전파, 자기신고 필드 **제거**하고도 통과 |
| I105 | 해결 | claim과 같은 3검사 적용 |
| I106 | 해결 | 게이트를 red-team 2종까지 확장 + closure를 마지막에. 실측 4해시 일치 |
| I107 | 해결 | `assert`로 편집 적용 강제 + drift 테스트 |
| I108 | 해결 | 무맥락 subagent 2회가 잡음 |
| I109, I111 | 해결 | 주장 정정, Amendment에 기록 |
| I110 | **부분** | 사후 검색으로 선례 발견·인용. **사전 검색 규율은 여전히 규율** |
| **미해결(명시)** | — | reviewer launcher 부재, red-team이 실행 환경에 미결속, E2E 미보호 stage 3 |

**I82의 처리가 이 세션의 대표적 판단이다.** 기계화 가능한 것을 최대화하고,
**기계가 보장하지 못하는 것을 산출물에 문자열로 박았다**:

```json
"independence": "distinct reviewer ids (machine-verified);
                 physical independence is procedural and NOT machine-verified"
```

"고쳤다"가 아니라 **"여기까지가 기계가 말할 수 있는 것"**이다.

---

## (5) 반복 O + 해결근거 O 인 이슈의 문제 정의

### 문제 1 — 테스트를 **구현을 보며** 쓰면 구현의 구멍을 물려받는다 (8회)

**정의**: 기능을 헬퍼에 넣고 그 헬퍼를 직접 부르는 테스트를 쓰면, 테스트는
"헬퍼가 그 일을 할 수 있는가"를 증명한다. **"production이 그 일을 하는가"는
증명하지 않는다.** 두 명제의 관측값이 같아서 구별이 불가능하다.

**왜 재발하는가**: 수정 → 테스트 순서에서는 테스트를 쓸 때 **구현이 이미
눈앞에 있다.** 헬퍼가 보이니 헬퍼를 부른다.

**I100 변종**: 헬퍼가 **이미 있는데** 안 부르고 더 약한 두 번째 구현을 쓴다.
이때는 배선 테스트도 초록이다 — 두 번째 구현이 실제로 호출되기 때문이다.

### 문제 2 — 선언은 관측값을 바꾸지 않는다 (P-자기수정회귀 10회의 뿌리)

**정의**: 문서에 "X는 더 이상 지표가 아니다"를 쓰는 것과 코드가 X를 지표에서
빼는 것은 다른 일이다. **관측값은 문서가 아니라 기제를 따른다.**

I74가 원형이고, I92·I96·I103이 같은 형태의 재발이다 — **선언을 담은 그 변경이
기제를 완성하지 못했다.**

### 문제 3 — 진단 도구가 판정을 소유하면 진단과 production이 갈라진다 (3회)

**정의**: doctor가 readiness를 다시 계산하면 doctor 초록과 production 거부가
**동시에 성립**할 수 있다. 진단은 안심시키는 것이 목적이 아니라 **상태를
말하는 것**이 목적인데, 자기 판정을 가지면 다른 상태를 말하게 된다.

I93·I95·I105가 같은 뿌리다.

### 문제 4 — 3값 어휘를 **출력에만** 적용하고 반환값에 적용하지 않았다 (2회)

**정의**: `BLOCKED is not a pass`를 출력하면서 `exit 0`을 반환하면 **사람은 읽고
기계는 못 읽는다.** 이 저장소는 `run_gates.py`에서 같은 문제를 만나 **문서
경고**를 택했고, 그 선택이 doctor에서 반복됐다(I94). artifact 계약에서도
같은 형태로 재발했다(I104: `status=None`을 PASS와 같은 문으로).

### 문제 5 — 커버리지를 **개수**로 세면 무엇이 빠졌는지 알 수 없다 (2회)

**정의**: `covered >= 5`는 5개가 덮였다고만 말하고 **어느 것이 안 덮였는지**
말하지 못한다. I77(`total > 0`)과 I112가 같다. 집합 일치만이 이름을 말한다.

### 문제 6 — 문서가 계약을 가르치면 문서 drift는 **실행 drift**다 (4회)

**정의**: rubric의 명령을 그대로 실행하면 실패하고(I91), 의미를 따르면 잘못된
결과를 기록한다(I87·I90). 특히 I90은 **두 판정자가 같은 잘못된 규칙을 따르면
합의율이 높게 나온다** — 해시 결속도 블라인딩도 잡지 못하는 유일한 계열이다.

---

## (6) 해결 유무 판단에 쓴 가설과 검증 방식

### 규칙 A — 고치기 전에 **재현한다**. 재현 없이 수정하지 않았다

19라운드 전부에서 지적을 받으면 먼저 실행해 수치를 냈다.

```
F1  build() with no expected_cells -> {'accepted_cells': 1}
F3  extra trace -> {'extra_trace_was_ignored': True}
F4  같은 사람 두 별칭 -> {'n_reviewers': 2, 'verdict': 'safe'}
    accepted_after_mutation: true, ledger_has_output_sha256: false
    e2e_passed_with_adjudicator_qualification_disabled: True
```

**재현이 실패하면 그 지적은 채택하지 않았다.** 이번에는 그런 경우가 없었다 —
7/7, 6/6, 9/9로 전부 재현됐다.

### 규칙 B — mutation만이 공허한 검사를 구별한다

긍정 테스트는 **정상 가드와 공허한 가드의 관측값이 같다.** 이 세션에서 mutation이
잡은 것:

| 대상 | 결과 |
|---|---|
| S1 교차항목 fixture | 호출부를 `" ".join()`으로 되돌려도 초록 → 재작성 |
| E2E acceptance (1차) | 하네스를 변이 → 하네스가 깨진다는 것만 증명 → 폐기 |
| E2E acceptance (2차) | **production 소스**를 변이 → 6종 전부 탐지 |
| provenance 전파 | `"provenance": (None if True else {` → `does not state its provenance mode` |

**applied-check를 재사용했다**(`run_calibration.py`): 변이 전후 sha256이 같으면
HARNESS DEFECT이지 evaluator 결과가 아니다.

### 규칙 C — 배선은 **가장 바깥 호출 가능 지점**에서 검사한다

`main()`을 구동하는 테스트. 헬퍼 테스트는 이 구멍을 못 본다.
`test_cli_wiring_coverage.py`가 AST로 이걸 강제하며, **즉시 2건을 찾았다** —
`apply_safety_audit.py`(안전 headline을 만드는 CLI)와 `measure_s1_recall.py`가
테스트에서 한 번도 실행된 적 없었다.

### 규칙 D — 무맥락 subagent가 handoff를 읽는다

fork가 아닌 새 agent에 경로 하나만 주고 2라운드. **I108을 이 방법이 잡았다** —
제작자는 자기가 삭제한 문장을 보지 못한다.

### 규칙 E — 층 분리의 이득은 **현실적 변경 번들**로 측정한다

이상화된 1파일 변경이 아니라 실제 번들(rubric + 감사 테스트 + 감사 목록):

```
execution drift: []
audit drift    : [SAFETY_AUDIT_RUBRIC.md, frozen_surface_audit.json,
                  test_safety_audit.py]
provider red-team 유효: True
```

**I92는 이 측정 방식이 없었으면 "고쳤다"로 남았을 것이다.**

### 규칙 F — closure 해시 4개가 일치해야 수치를 인용한다

I106 이후 도입. 문서 편집 **이후** calibration → codex red-team → provider
red-team 순으로 재생성하고 네 해시를 대조한다.

```
PREREGISTRATION.md   17529190
calibration          17529190
redteam × 2          17529190
```

---

## (7) 문제의 해결 방법 — 구체적으로

### 문제 1(배선) → `test_cli_wiring_coverage.py` (AST 게이트)

**규칙**: `main()`이 있고 fail-closed로 거부하는 모듈은 `main()`을 실제로
호출하는 테스트가 있어야 한다.

```python
def _module_facts(path):        # AST로 판정
    has_main = any(isinstance(n, ast.FunctionDef) and n.name == "main" ...)
    refuses  = raise AuditInputError | _fail(...) | SystemExit("refusing...")
def _main_calls_in_tests():     # 테스트에서 <module>.main( 호출 수집
```

- 탈출구 `KNOWN_UNPROVEN`은 **사유 25자 이상 + 파일 존재 + `main()` 존재**를
  별도 테스트가 검사한다
- **모킹 금지**를 명시했다 — 모킹된 진입점은 모킹된 음성 테스트와 같은 이유로
  아무것도 증명하지 않는다

**I100 변종에는 이것만으로 부족하다.** 추가로: `_parse_ledger_lines` 구현이
**1개**이고 감사 코드의 원장 직접 읽기가 **0건**임을 테스트가 고정한다.

### 문제 2(선언≠기제) → 이름을 바꿔 fail-loud로

의미를 제자리에서 바꾸지 않았다. 기존 소비처는 전부 옛 이름으로 오염된 수를
계산 중이었으므로 **`KeyError`가 의도된 결과**다.

| 옛 | 새 |
|---|---|
| `full_hard_gate` | `retrieval_hard_gate` |
| `safety_violation` | `s1_candidate_flagged` |
| `confirmed_safety_violation_rate` | `s1_candidate_rate_among_auto_decidable` |
| `valid_run_full_hard_gate_rate` | `valid_run_retrieval_hard_gate_rate` |

그리고 **문서 편집은 `assert`로 적용을 강제**한다(I107 이후). `str.replace`
미매치가 예외 없이 원문을 반환하는 것이 두 번 사고를 냈다.

### 문제 3(진단이 판정 소유) → doctor를 **위임**으로

```python
row, config = _delegate("readiness",
                        lambda: live._assert_ready(config_name))
row, quals  = _delegate("qualification artifacts",
                        lambda: live._assert_primary_qualifications(config))
row, auth   = _delegate("primary authorization", _auth)
```

- doctor가 자체 판정하는 것은 **production 함수가 없는 것뿐**(판정자 배정,
  CLI 존재)
- `_claim_primary_attempt`는 **부르지 않는다**(시도 소모)
- `--config` 기본값은 **authorization이 가리키는 config**
- 평가되지 않은 게이트는 **BLOCKED로 계상**한다(조용히 빼지 않는다)

### 문제 4(3값을 반환값에) → exit code와 예외 타입

```
0 PASS  판정을 냈고 전부 통과
1 FAIL  판정을 냈고 실패
2 BLOCKED 판정을 내지 못함
```

- `doctor`, red-team 2종, `e2e --offline` 전부
- 예외에도 타입으로: `LiveRunError.verdict = "FAIL"`,
  `LiveRunBlocked.verdict = "BLOCKED"` — 문자열 검색(`"BLOCKED" in msg`) 제거
- artifact 계약에도: `status`가 없으면 **BLOCKED**, grandfathering 없음

### 문제 5(개수→집합) → obligation registry

```python
assert declared - guarded == UNGUARDED_STAGES     # 집합 일치
```

- E2E 8단계에 문자열 ID(`[4] packet.blinded`)
- obligation이 `stage_id`를 참조
- **미보호가 하나라도 있으면 `PARTIAL` / exit 2** — `cg_obligations.aggregate()`의
  "전부 PASS일 때만 PASS"와 같은 규칙
- machine-readable coverage manifest 출력
- mutation은 **실험 디렉터리 임시 복사**에서(active worktree 무변조),
  `git worktree add HEAD`가 아니라 복사인 이유는 변이가 **현재 작업 상태**에
  적용돼야 하기 때문(HEAD worktree는 아무도 실행하지 않는 커밋을 검사한다)

### 문제 6(문서 drift) → 기계가 문서를 읽는다

```python
calls = re.findall(r"python3 apply_safety_audit\.py(.*?)```", rubric, re.S)
assert len(paths) >= 4        # CLI가 요구하는 인자 수와 대조
assert "safe/not_applicable" not in rubric      # 코드와 반대인 의미 금지
assert "assignment_sha256" in rubric            # 필수 계약 요소 존재
```

**I90(의미 오류)에는 문서 테스트로 부족하다.** 별도로:

- 판정 순서를 3단으로 교체: 권고인가 → 조건이 **허용되는** 조건인가 →
  아니면 `ENDORSE`
- **판정자 자격 fixture** — 본 감사 전에 10문항을 맞혀야 라벨이 수락된다.
  Q1/Q2·Q6/Q7이 **문법 형태가 같고 라벨이 반대인 판별쌍**이라, "조건부는
  MENTION" 규칙을 쓰는 판정자는 정확히 그 둘에서만 틀린다
- **정답을 별도 파일로 분리** — 문항만 판정자에게 간다

### 문제 6b(freeze closure) → 게이트 확장 + 순서를 스크립트가 안다

`test_every_frozen_artifact_is_current`가 calibration **과 red-team 2종**을
검사하고, 실패 메시지가 재생성 순서를 말한다. **closure는 문서 편집 이후에
실행한다** — 이번 라운드의 결함이 정확히 그 순서를 어긴 것이다.

---

## 이 회고가 남기는 방법론적 사실

1. **개별 결함을 8라운드 동안 하나씩 고친 것이 틀린 접근이었다.** 같은 형태가
   반복되면 그것은 개별 결함이 아니라 **전 경로를 실행하는 것이 없다는 신호**다.
   사용자 지적으로 알았고, 그때 만든 `e2e --offline`은 **첫 실행에서 바로**
   공백을 찾았다(참조 trace에 `recommended_actions`가 없어 32칸 전부
   `not_applicable`, 최종 번들에 안전 판정 부재).

2. **선례를 먼저 찾았어야 했다.** `DESIGN_DECISION_surface_separation.md`
   (2026-07-28, 동결)가 §3에서 **canonical builder — 유일 허용 경로**를 이미
   정했고 필수 테스트 #7이 "스모크·본 실행·재실행이 동일 builder를 사용"을
   요구한다. 내가 만든 CLI 배선 테스트는 **그 원칙의 부분 재발명**이었다.
   web search는 불필요했다 — workspace에 있었다.

3. **TDD를 전면 적용하지 않고 3규칙으로 좁혔다.** 이 저장소는 규율이 반복
   실패하면 기제로 옮기며(`HARNESS_KNOWHOW` B4a: 7회 처방·7회 실패), TDD도
   규율이다. 그래서 규칙 1(fail-closed 검사는 CLI 수준 테스트 먼저)만
   **AST 게이트**로 만들었다. 탐색적 측정(S1 recall)에는 적용하지 않는다 —
   답을 모르고 재는 것이라 먼저 쓸 테스트가 없고, 흉내내면 원하는 값을
   assert하게 된다(그것이 P1 #19였다).

4. **"고쳤다"와 "여기까지가 기계가 말할 수 있는 것"을 구별했다.** I82의
   `independence` 문자열, `NOT_machine_verified` 목록, `NO_SIGNAL_YET`,
   `UNGUARDED_STAGES`가 전부 같은 장치다. **보장하지 못하는 것을 보장하는 척하지
   않는 것**이 이 세션에서 가장 여러 번 반복한 수정이다.

5. **도구가 자기 자신에게 같은 결함을 냈다.** 반복을 끝내려고 만든 E2E가
   "production E2E"라 과장했고(I96), provenance 표식이 packet에서 멈췄으며
   (I103), acceptance gate 1차는 하네스를 변이해 아무것도 증명하지 않았다.
   **메타 계층은 면제되지 않는다.**

---

## 남은 것

| 항목 | 상태 |
|---|---|
| reviewer launcher (Seatbelt 격리) | **미구현.** PASS 조건만 probe artifact로 바꿔 빈 stub 차단 |
| red-team의 실행 환경 결속 | **미구현.** 현재 PASS는 "어떤 환경에서 통과"이지 "지금 세션에서 검증" 아님 |
| E2E 미보호 stage 3 | `UNGUARDED_STAGES`에 사유와 함께. e2e는 **PARTIAL / exit 2** |
| 이중부정 polarity | U1로 라우팅, 미해결 |
| qualification 2종 | **stale.** doctor가 `exit 1`로 그렇게 말한다 |
| `metrics.py`·`experiment_data.py`·`sandbox.py` 추출 | primary 이후로 예약(동작 불변) |

**다음 세션의 첫 행동**: `python3 run_pipeline.py doctor` 그리고
`python3 run_pipeline.py e2e --offline`. 둘 다 0.0초이고, 무엇이 막혀 있는지
한 화면으로 말한다.
