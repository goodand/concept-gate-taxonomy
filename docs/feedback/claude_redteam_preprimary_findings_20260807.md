---
aliases:
  - Claude Red Team Pre-Primary Findings
tags:
  - doc/review
  - stage/handoff
  - status/pending-review
---

# Pre-Primary Gate Audit — findings

- 감사일: 2026-08-07
- 역할: 독립 red-team 리뷰어. **피험자 아님.**
- 실행하지 않은 것: primary, pilot, provider CLI, MCP, 네트워크, 유료 모델 호출 **0건**.
- 읽지 않은 것: `hidden_gold/gold.json` (지시된 hard boundary), 홈 디렉터리
  transcript·자격증명·타 에이전트 세션 상태.
- 수정하지 않은 것: 코드·config·corpus·evaluator·result artifact·gold. **이 문서 1건만 신규.**
- 실행한 것: 소견 확인용 in-process 시뮬레이션 1회. 파일 쓰기는 `/private/tmp`에만.
  provider를 호출하지 않는다.

**절차상 고지 —** `concept-gate-codex-mcp-wt`는 현재 dirty worktree다. 이
워크스페이스의 안전 게이트는 dirty worktree를 보호 대상(읽기·검색만)으로 규정하므로,
사용자가 명시 지시한 이 리뷰 문서 1건 외에는 어떤 파일도 만들거나 고치지 않았다.

---

## 0. 요약

| ID | 질문 | 심각도 | 판정 |
|---|---|---|---|
| **F1** | Q1 | **HIGH** | 합성 1-cell qualification artifact가 primary 게이트를 **통과한다(실행 확인)** |
| **F2** | Q1 | **HIGH** | qualification artifact 자체에 무결성 결속이 없다 |
| **F3** | Q5 | **HIGH** | `--primary` 기본 경로가 v1 surface·v1 sandbox를 겨냥한다. 현재의 거부는 규칙이 아니라 **우연** |
| **F4** | Q3 | **HIGH** | `R_STATIC` hard-gate 0.0이 통과한 qualification 안에 있고, 오용을 막는 것은 **문자열 하나뿐** |
| **F5** | Q6 | **HIGH** | 사용자 승인을 표현하는 장치가 **없다**. `run_only_after`는 어떤 코드도 읽지 않는다 |
| **F6** | Q2 | MED-HIGH | host-trace 결속은 pilot에서 **증명된 가드**지만, primary에서는 아무것도 게이팅하지 않는다 |
| **F7** | Q4 | MED | frozen surface는 넓지만 **테스트 파일과 result artifact를 덮지 않는다** |
| **F8** | Q5 | MED | `live_pilot_attempt2~9` 7건이 `kind: live-subject-primary`로 기록돼 있다 |
| **F9** | Q1 | LOW-MED | `passed=true`인 **1-run** artifact가 results/에 실재한다 |

**먼저 인정할 강점** — 이것들은 실제로 견고하고, 아래 지적은 이 위에서의 잔여
위험이다: host가 `actions`/`reads`/`stop_reason`을 소유한다(F6); frozen surface에
**게이트 파일 자신과 gold와 cases와 corpus와 모든 config가 들어 있다**(F7);
provider·sandbox_policy는 artifact가 아니라 **primary config 쪽 spec**에 고정돼 외부
앵커를 갖는다; 동일 이름 결과 덮어쓰기를 거부한다.

---

## F1 — matrix 완전성이 artifact의 **자기 신고**로 판정된다 (Q1, HIGH)

### 증거

`run_live_phase_c.py:713-725`

```python
pilot = artifact_config.get("pilot", {})      # ← artifact 자신이 선언한 값
expected_arms = pilot.get("arms", [])
expected_cases = pilot.get("case_ids", [])
if (not expected_arms or not expected_cases or
        artifact.get("n_runs") != len(expected_arms) * len(expected_cases)):
    raise LiveRunError(f"refusing primary: incomplete qualification matrix: ...")
per_arm = artifact.get("per_arm", {})
if set(per_arm) != set(expected_arms) or any(
        per_arm[arm].get("n") != len(expected_cases) for arm in expected_arms):
    raise LiveRunError(f"refusing primary: qualification arm coverage is incomplete: ...")
```

`provider`와 `sandbox_policy`는 `spec`(= primary config)과 대조되지만(`:711-714`),
**arms와 case_ids는 대조 상대가 artifact 자신**이다. 즉 이 검사는 완전성이 아니라
**내적 정합성**을 본다.

### 재현 (gold 미사용, /private/tmp에서만 실행)

실제 통과 artifact `live_pilot_claude_mcp_surface_v1.json`을 복사해
`config.pilot`을 `{"arms":["S_DYNAMIC"],"case_ids":["HD01"]}`로 바꾸고
`n_runs=1`, `per_arm={"S_DYNAMIC":{...,"n":1}}`만 남긴 뒤
`_assert_primary_qualifications`에 먹였다. `frozen_surface_hashes()`는 현재값을
그대로 넣었다(공격자는 하네스를 고치지 않는다).

```
>>> 통과함: 1-cell 합성 artifact가 primary 전제를 만족한다
```

**4-arm 요구가 1-arm 신고로 축소되고 게이트는 아무 말도 하지 않는다.**
`R_STATIC`이 통째로 빠져도 통과한다 — 하필 F4에서 hard-gate 0.0이 나온 그 arm이다.

### 최소 수정

요구 matrix를 **primary config의 spec에** 적고 거기서만 읽는다.

```python
required_arms = spec.get("arms") or config["primary"]["arms"]
required_cases = spec.get("case_ids") or config["primary"]["case_ids"]
if set(per_arm) != set(required_arms):
    raise LiveRunError(f"refusing primary: {path.name} lacks arms "
                       f"{sorted(set(required_arms) - set(per_arm))}")
if artifact.get("n_runs") != len(required_arms) * len(required_cases):
    raise LiveRunError(...)
```
그리고 artifact가 신고한 `config.pilot`이 spec과 **불일치하면 그 자체로 거부**한다
(축소 신고를 오류로 만들기 위해).

### 짝 회귀 테스트

```python
def test_a_qualification_that_declares_a_smaller_matrix_is_refused(tmp_path):
    """자기 신고로 축소된 matrix는 완전성 검사를 무력화한다 — 실측으로 통과했다."""
    forged = _load_passing_artifact()
    forged["config"]["pilot"] = {"arms": ["S_DYNAMIC"], "case_ids": ["HD01"]}
    forged["n_runs"] = 1
    forged["per_arm"] = {"S_DYNAMIC": {"n": 1}}
    with pytest.raises(LiveRunError, match="lacks arms"):
        _assert_with(forged, required_arms=ARMS, required_cases=["HD01"])

def test_a_complete_qualification_still_passes(tmp_path):
    """PRECISION — 거부만 하는 게이트는 primary를 영원히 막아 같은 관측을 만든다."""
    _assert_with(_load_passing_artifact(), required_arms=ARMS, required_cases=["HD01"])
```

---

## F2 — qualification artifact에 무결성 결속이 없다 (Q1, HIGH)

### 증거

`_assert_primary_qualifications`(`:694-729`)가 검사하는 것은 artifact **내용의
자기 정합성**과 `frozen_surface_drift(artifact["frozen_surface_hashes"])`
(`:726-729`)뿐이다. `frozen_surface_drift`는 `_evaluator.py:218-249`의 하네스
파일 30종을 본다 — **`results/` 아래 artifact는 그 목록에 없다.**

따라서:
- artifact 파일 자체의 해시·서명이 없다.
- artifact를 만든 프로세스와 artifact 파일을 잇는 증거가 없다(raw provider 로그
  해시가 trace에 없다).
- `frozen_surface_hashes` 필드는 artifact 안에 있으므로 **artifact와 함께 위조된다**
  (F1 재현에서 실제로 현재값을 그대로 써넣었다).

### 공격

qualification을 한 번 통과시킨 뒤, 실패한 셀만 골라 `per_arm`·`results`를
손으로 고친다. 하네스는 한 바이트도 건드리지 않으므로 drift 0이고 게이트는 통과한다.

### 최소 수정

pilot 종료 시 artifact를 정규화 직렬화해 해시하고, **artifact 밖**(예:
`results/qualification_ledger.jsonl`, append-only)에 `{file, sha256, config_sha256,
utc, matrix}`를 한 줄 추가한다. primary는 ledger의 해시와 실제 파일 해시가
일치할 때만 진행한다. ledger 자체를 위조할 수는 있으나, **위조 지점이 두 곳으로
늘고 append-only 이력이 남는다** — 지금은 한 곳이고 흔적이 없다.

### 짝 회귀 테스트

```python
def test_an_edited_qualification_artifact_is_refused():
    """내용 한 글자만 바꿔도 ledger 해시와 어긋나야 한다."""
def test_an_unedited_artifact_matches_its_ledger_entry():
    """PRECISION."""
```

---

## F3 — `--primary` 기본 경로가 v1 surface를 겨냥한다 (Q5, HIGH)

### 증거

- `run_live_phase_c.py:48` `CONFIG_PATH = HERE / "phase_c_live_config.json"`
- `:842` `parser.add_argument("--config", default=CONFIG_PATH.name, ...)`
- `phase_c_live_config.json`: `provider=codex-cli`,
  `sandbox_policy=macos-seatbelt-deny-project-root-control-plus-codex-bypass...`(**v1**),
  `primary.required_qualification_artifacts = null`, `result_names` 없음
- `:695-699` spec 기본값 → `{"file": "live_pilot.json", provider/sandbox = config의 것}`

즉 `python3 run_live_phase_c.py --primary` (인자 없음)은 **v1 Codex config + v1
Seatbelt**를 선택하고, 전제로 **`live_pilot.json`**(최초 파일럿 산출물)을 본다.
v1 Seatbelt는 이 저장소의 red-team이 `~/.claude/projects`와 `~/.codex`를 읽을 수
있다고 실측한 바로 그 프로파일이다(`PROVIDER_ADAPTERS.md` §3).

### 왜 "지금은 안전"이 근거가 못 되는가

오늘 이 경로는 거부된다 — `live_pilot.json`에 `qualification` 블록이 없어
`.get("qualification", {}).get("passed") is not True`가 참이기 때문이다.
**규칙이 v1을 막는 것이 아니라, 옛 파일에 새 필드가 없어서 막힌다.**
누군가 v1 config로 pilot을 한 번 돌리면 `live_pilot.json`이 `qualification.passed`를
갖게 되고, 그 순간 기본 경로가 열린다.

### 최소 수정

1. `--config`에서 default를 없애고 **required**로 만든다. 어떤 surface에서
   도는지를 매번 명시하게 한다.
2. `phase_c_live_config.json`의 `primary`에
   `"blocked_reason": "v1 sandbox is superseded; not eligible for primary"`를 넣고
   runner가 이 키를 만나면 provider 호출 전에 종료한다.
3. spec 기본값(`or [{...live_pilot.json...}]`)을 제거한다 —
   `required_qualification_artifacts`가 없으면 **거부**가 옳다.

### 짝 회귀 테스트

```python
def test_primary_requires_an_explicit_config():
    """기본값이 가장 약한 surface를 가리키면 안 된다."""
def test_a_config_without_required_artifacts_refuses_instead_of_defaulting():
def test_the_v1_config_is_ineligible_for_primary():
def test_the_current_configs_are_still_eligible():   # PRECISION
```

---

## F4 — `R_STATIC` hard-gate 0.0이 통과한 qualification 안에 있다 (Q3, HIGH)

### 증거

`results/live_pilot_claude_mcp_surface_v1.json`, `qualification.passed = true`:

| arm | full_hard_gate_rate | invalid_run | host_action_compliance |
|---|---|---|---|
| `S_STATIC` | 1.0 | 0.0 | 1.0 |
| **`R_STATIC`** | **0.0** | 0.0 | 1.0 |
| `S_DYNAMIC` | 1.0 | 0.0 | 1.0 |
| `R_DYNAMIC` | 1.0 | 0.0 | 1.0 |

`run_live_phase_c.py:797-806`:

```python
qualification_failures = [... if row["invalid_run"] or not row["host_action_compliance"]["passed"]]
qualification = {"passed": phase_name == "pilot" and not qualification_failures,
                 "criteria": ["invalid_run == false", "main host actions >= 1",
                              "retrieval-subagent host actions >= 1 for R arms"], ...}
```

**설계는 옳다** — qualification은 프로토콜 준비도이지 성능이 아니고, hard gate는
기준에 없다. 문제는 그 다음이다.

### 오용 여지

1. artifact가 **arm별 hard-gate rate를 그대로 노출**한다. 4셀 중 하나만 0.0인
   표는 "R_STATIC이 나쁘다"로 읽히기에 최적의 형태다.
2. 이를 막는 것은 `interpretation` **문자열 하나**
   (`"qualification-only; this small pilot must not be used to estimate arm effects"`)뿐이다.
   기계가 강제하는 것은 없다.
3. n=1/arm이다. 0.0과 1.0의 차이가 **단일 시행**에서 나온 것이며 신뢰구간이 없다.
4. 이 저장소가 12회 기록한 패턴 그대로다 — **참인 명제(문자열이 존재한다)가
   필요한 명제(오독이 불가능하다)를 대신하고 있다.**

### 최소 수정

- pilot artifact에서 **arm별 성능 지표를 아예 빼거나**, 빼지 않는다면
  `"arm_effect_estimable": false`와 `"n_per_cell": 1`을 형제 키로 **같은 깊이에**
  둔다. 표를 읽는 도구가 rate만 집어가는 것을 어렵게 만든다.
- `R_STATIC` hard-gate 0.0의 **원인 코드를 artifact에 명시**한다(현재 failure_codes는
  집계돼 있으나 arm별 서술이 없다). "왜 0인가"가 없으면 "성능이 나쁘다"가 기본 해석이 된다.
- pilot artifact를 입력으로 받아 arm 비교표를 만드는 코드 경로를 금지하는 테스트를 둔다.

### 짝 회귀 테스트

```python
def test_a_pilot_artifact_declares_that_arm_effects_are_not_estimable():
    art = _load("live_pilot_claude_mcp_surface_v1.json")
    assert art["arm_effect_estimable"] is False
    assert art["n_per_cell"] == 1

def test_a_primary_artifact_does_not_carry_that_flag():
    """PRECISION — 모든 artifact에 붙는 플래그는 아무것도 구별하지 못한다."""
```

---

## F5 — primary 실행 권한이 사용자 의사와 연결돼 있지 않다 (Q6, HIGH, **거버넌스 공백**)

### 증거

- `run_live_phase_c.py:836-838` — `--pilot` / `--primary`는 단순 상호배타 플래그다.
- `:751` — `if phase_name == "primary": _assert_primary_qualifications(config)`.
  즉 **primary의 유일한 전제는 artifact 검증 통과**다.
- `grep -n "run_only_after" *.py` → **0건**. `phase_c_live_config.json`의
  `primary.run_only_after` 문자열은 **어떤 코드도 읽지 않는다.** 두 현행 config
  (`phase_c_claude_mcp_surface_config.json`, `phase_c_codex_mcp_v6_config.json`)에는
  그 키가 아예 없다.
- `:841` `--output-name` — 이름만 바꾸면 **primary를 몇 번이든 새로 돌릴 수 있다.**
  `:749-750`의 덮어쓰기 거부는 같은 이름만 막는다. 시도 이력을 적는 ledger가 없다.

### 판정

**기술적으로 사용자 의사를 증명할 방법이 현재 없다.** qualification 통과와
primary 실행 사이에 사람의 결정이 들어갈 자리가 코드에 존재하지 않는다.
추가로 `--output-name` + ledger 부재는 **선택적 보고**를 가능하게 한다:
primary를 여러 번 돌리고 마음에 드는 artifact만 인용해도, 나머지가 존재했다는
흔적이 저장소에 남지 않는다. 이는 `retry_count=0`과
`invalid_run_policy=record-V1-and-do-not-replace`가 **셀 단위**로 막은 것을
**실행 단위**에서 되살린다.

### 최소 수정

```
results/PRIMARY_AUTHORIZATION.json   # 사람이 만든다. runner는 소비만 한다.
{
  "authorized_by": "<user>",
  "utc": "...",
  "config_sha256": "...",            # 어떤 surface를 승인했는지
  "qualification_sha256": {"live_pilot_claude_mcp_surface_v1.json": "...", ...},
  "matrix": {"case_ids": [...8건...], "arms": [...4개...]},
  "max_attempts": 1
}
```
runner는 `--primary`에서 이 파일을 요구하고, config 해시·artifact 해시·matrix가
전부 일치할 때만 진행하며, 실행 후 ledger에 시도를 append한다.
`max_attempts` 초과 시 거부한다.

이것이 사용자 의사를 **증명**하지는 못한다(파일은 누구나 쓸 수 있다). 그러나
**"게이트가 통과했으므로 돌렸다"와 "승인이 있었으므로 돌렸다"를 사후에 구별
가능하게** 만들고, 승인 대상이 무엇이었는지를 해시로 못박는다. 지금은 둘이
구별 불가능하다.

### 짝 회귀 테스트

```python
def test_primary_refuses_without_an_authorization_file():
def test_primary_refuses_when_the_authorization_names_a_different_config():
def test_primary_refuses_when_attempts_exceed_max_attempts():
def test_primary_proceeds_with_a_matching_authorization():   # PRECISION
```

---

## F6 — host-trace 결속: pilot에서는 증명된 가드, primary에서는 비활성 (Q2, MED-HIGH)

### 증명된 부분 (강점)

`_host_action_compliance`(`:675-691`)는 `trace["actions"]`와
`details["subagent"]["host_actions"]`를 센다. 둘 다 **host가 소유**한다
(`state.trace_fields()` / host state). 모델 payload에서 오지 않는다.
그리고 `:797-801`이 compliance 실패 셀을 qualification 실패로 만든다.
따라서 "provider가 실행됐지만 host action이 0"인 구조적으로 유효한 artifact는
**pilot에서 통과할 수 없다.** 이는 관행이 아니라 가드다.

### 잔여 1 — primary에서는 아무것도 게이팅하지 않는다

`:803` `"passed": phase_name == "pilot" and not qualification_failures`.
primary에서는 `qualification.passed`가 **정의상 항상 False**이고, compliance는
행별로 계산·기록되지만(`:783`, `:792-794`) 실행을 중단시키지 않는다.
결과적으로 primary의 "host action 0" 셀은 **D0/R1(검색 실패)** 로 채점된다 —
실제로는 피험자가 도구를 한 번도 부르지 않은 **compliance 실패**인데,
성능 실패와 같은 칸에 들어간다. `PROVIDER_ADAPTERS.md` §6-5가 예고한 오독이
primary에서 그대로 남아 있다.

### 잔여 2 — 저장된 artifact와 채점 입력의 결속이 없다

`_score`(`:731-744`)는 in-process로 만든 payload를 clean judge에 넘긴다.
artifact는 그 뒤 별도로 직렬화된다. **저장된 trace가 judge가 실제로 본 것과
같다는 증거가 artifact 안에 없다.** F2와 합치면 사후 편집이 무흔적이다.

### 최소 수정

- primary에서도 compliance 실패 셀을 `V1`과 **별개 코드**(예: `C5`)로 기록하고,
  `per_arm`에 성능 지표와 분리해 보고한다. 실행 중단까지는 불필요하다 —
  분류만 분리해도 오독이 사라진다.
- `_score`가 넘긴 payload의 정규화 해시를 artifact에 `judged_payload_sha256`으로
  기록한다.

### 짝 회귀 테스트

```python
def test_a_primary_cell_with_zero_host_actions_is_classified_as_compliance_not_performance():
def test_a_compliant_primary_cell_carries_no_compliance_code():   # PRECISION
def test_the_artifact_records_the_hash_of_what_the_judge_scored():
```

---

## F7 — frozen surface가 덮지 않는 것 (Q4, MED)

### 강점부터

`_evaluator.py:218-249`의 30항목은 **게이트 파일 자신(`run_live_phase_c.py`),
`hidden_gold/gold.json`, `public_cases/cases.json`, `corpus_manifest.json`,
`_providers.py`, `live_subject_mcp.py`, red-team 스크립트 2종, config 11종**을
포함하고, `public_corpus/variant-{L,M}/`는 트리 해시로 들어간다(`:266-275`).
각 artifact가 자기 시점 지문을 들고 있고 primary가 현재값과 대조하므로
(`:726-729`), **Q4의 핵심 질문 "frozen surface 변경이 한쪽 provider의
qualification을 무효화했는데 primary가 못 잡는가"의 답은 30항목에 대해 '아니오'다.**
새 config를 추가하려면 `_evaluator.py`(자기도 pinned)를 고쳐야 하므로 surface가
바뀌고 재-calibration이 강제된다 — 이건 잘 설계돼 있다.

### 누락

목록에 없는 실험 파일: `test_protocol.py`, `test_live_phase_c.py`,
`test_live_phase_c_claude.py`, `test_codex_mcp_provider.py`.
그리고 `results/` 전체(F2), `README.md`, `RESULTS.md`, `PROVIDER_ADAPTERS.md`.

게이트가 테스트를 실행하지는 않으므로 직접적 우회는 아니다. 그러나
`PROVIDER_ADAPTERS.md` §7이 "91 passed"를 실행 가능 근거로 인용하는데,
**그 91건이 어떤 surface에 대한 91건인지 못박히지 않는다.** 테스트를 약화시킨
채 문서의 숫자만 남길 수 있다.

### 최소 수정

`FROZEN_SURFACE_FILES`에 `test_*.py` 4종을 추가하고, calibration artifact에
`pytest` 통과 수와 그 시점 surface 지문을 함께 기록한다.

### 짝 회귀 테스트

```python
def test_every_test_module_is_in_the_frozen_surface():
def test_frozen_surface_drift_fires_when_a_test_file_changes(tmp_path):
def test_frozen_surface_drift_is_silent_on_an_unchanged_tree():   # PRECISION
```

---

## F8 — 과거 artifact의 이름·kind drift (Q5, MED)

### 증거 (`results/` 실측)

| 파일 | `kind` | `qualification.passed` | n_runs |
|---|---|---|---|
| `live_pilot.json` | live-subject-pilot | (없음) | 4 |
| `live_pilot_attempt2~9` (7건) | **live-subject-primary** | (없음) | 4 |
| `live_pilot_claude_attempt3.json` | live-subject-pilot | **true** | 4 |
| `live_pilot_claude_mcp_surface_v1.json` | live-subject-pilot | true | 4 |
| `live_pilot_codex_mcp_v5_vehicle.json` | live-subject-pilot | **true** | **1** |
| `live_pilot_codex_mcp_v6.json` | live-subject-pilot | true | 4 |

- **`attempt2~9` 7건이 `kind: live-subject-primary`다.** 파일명은 pilot,
  내용은 primary. `_assert_primary_qualifications`의 `kind != "live-subject-pilot"`
  검사가 이들을 전제로 쓰는 것은 막지만(`:705-706`), **결과 폴더를 읽는 사람에게는
  "primary가 이미 8번 돌았다"로 보인다.** 이 저장소가 이미 겪은 "생성물이 스스로를
  잘못 라벨링" 계열이다.
- **`live_pilot_claude_attempt3.json`이 `passed=true`인 채 남아 있다.**
  `live_pilot_claude_mcp_surface_v1.json`으로 대체됐으나 **superseded 표시가 없다.**
  두 개의 통과한 Claude qualification이 동시에 유효해 보인다.

### 최소 수정

`results/SUPERSEDED.json`(또는 각 artifact에 `"superseded_by"` 키)로 대체 관계를
명시하고, primary 게이트가 `superseded_by`를 가진 artifact를 거부한다.
`kind`가 파일명과 어긋나는 기존 7건은 **고치지 말고**(불변 결과물) 대체 관계
문서에 "라벨 오류, 파일럿 시도임"을 기록한다.

### 짝 회귀 테스트

```python
def test_a_superseded_artifact_cannot_satisfy_the_primary_gate():
def test_the_current_artifact_is_not_marked_superseded():   # PRECISION
```

---

## F9 — `passed=true`인 1-run artifact가 실재한다 (Q1, LOW-MED)

`results/live_pilot_codex_mcp_v5_vehicle.json`:
`qualification.passed=true`, `n_runs=1`, `per_arm`에 `S_DYNAMIC` 하나뿐인데
자기 `config.pilot.arms`는 4개를 선언한다. 그래서 오늘은 matrix 검사
(`n_runs 1 != 4`)에 걸려 **거부된다.**

그러나 이것은 F1이 말하는 바로 그 상황의 실물 견본이다 — `config.pilot`을
한 줄 고치면 통과한다. "vehicle"(운반체) 성격의 부분 실행에
`qualification.passed=true`를 부여하는 관행 자체가 위험하다.

### 최소 수정

부분 실행에는 `"kind": "live-subject-vehicle"`처럼 **다른 kind**를 부여해
qualification 후보에서 타입 수준으로 배제한다.

---

## 종합 판정

**현재 상태로 primary를 승인해서는 안 된다.** 다만 이유는 격리나 채점의 결함이
아니다 — 그 둘은 이 감사에서 견고했다(F6 강점, F7 강점). 이유는 세 가지다.

1. **전제 검증이 전제 자신의 신고에 기대고 있다**(F1 실행 확인, F2).
   축소된 qualification이 통과한다.
2. **가장 값싼 실행 경로가 가장 약한 surface를 가리킨다**(F3). 지금의 거부는
   규칙이 아니라 옛 파일의 필드 부재라는 우연이다.
3. **qualification 통과와 사용자 승인 사이가 비어 있다**(F5). `run_only_after`는
   어떤 코드도 읽지 않고, `--output-name`은 시도 이력 없이 반복 실행을 허용한다.

그리고 **F4는 primary 실행 여부와 무관하게 지금 조치해야 한다.**
`R_STATIC` hard-gate 0.0은 이미 통과한 artifact 안에 기록돼 있고, 그것이 성능
주장으로 새어 나가는 것을 막는 것은 현재 문자열 하나뿐이다.

### 권고 순서

1. F5 승인 파일 + ledger (거버넌스 공백을 먼저 닫는다 — 나머지 수정 중에도
   실수로 primary가 도는 것을 막는다)
2. F1 spec 기반 matrix + F2 artifact 해시 ledger
3. F3 `--config` required + v1 config primary 금지
4. F4 pilot artifact의 arm 지표 표기 변경
5. F6 primary compliance 분류 분리, F7 테스트 파일 pinning, F8 supersede 표기

각 항목은 위에 짝 회귀 테스트를 함께 적었다. 이 저장소의 기록상 **양성 테스트만
있는 가드와 공허한 가드는 관측값이 같으므로**, 수정마다 위반 입력을 먹이는
테스트가 함께 와야 한다.

## 이 감사가 하지 않은 것

- live run·provider 호출·유료 모델 호출 0건.
- `hidden_gold/gold.json` 미열람. 모든 재현은 gold 없이 성립한다.
- 채점 정확도, arm 효과, 모델 성능에 대한 판단 없음 — 감사 범위 밖이다.
- `results/`의 기존 artifact를 하나도 수정하지 않았다.
- MOC와 qualification log는 정본 코드·계약·결과의 **위치를 찾는 데만** 썼고
  권위로 인용하지 않았다.
