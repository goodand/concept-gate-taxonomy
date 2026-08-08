---
aliases:
  - Design Proposal — Codex v8 / Claude surface v3
  - R1/R2/attempt-ledger completion design (not applied)
tags:
  - doc/design-proposal
  - stage/handoff
  - status/design-only
---

# 설계 제안 — Codex v8 / Claude surface v3 (R1, R2, attempt-ledger 종결 기록)

**상태: 설계 승인, 구현 미승인.** 이 문서의 어떤 diff도 실제 코드/config/
frozen-surface 파일에 적용되지 않았다. `git status --short`로 이 세션 동안
`run_live_phase_c.py`, `_evaluator.py`, `test_preprimary_gates.py`,
qualification artifact, ledger가 전혀 변경되지 않았음을 확인했다. 이 설계는
사용자 승인([[docs/feedback/claude_questions_for_source_session_20260807|질문
1 답변]])에 따라 **R1, R2, attempt-ledger 종결 기록(요청 C) 셋을 하나의 새
qualification surface — Codex v8 / Claude surface v3 — 로 묶어 한 번만
재-qualification한다.**

## 왜 하나로 묶는가 (사용자 결정 근거)

1. 셋 다 같은 frozen surface(`run_live_phase_c.py`, `_evaluator.py`,
   `test_preprimary_gates.py`)를 수정한다.
2. 따로 적용하면 두 provider의 유료 qualification을 두 번 반복하게 된다.
3. 현재 primary는 `PRIMARY_AUTHORIZATION.json` 부재로 차단돼 있어 즉시 실행
   위험이 없다 — 급하게 하나씩 낼 이유가 없다.
4. R1은 "강한 결과 무결성"을 주장하기 전에 반드시 닫아야 하므로, primary
   승인 이전 어느 시점에는 반드시 처리된다.

## 실행 순서 (승인된 것은 1단계뿐 — 이 문서)

```
1. 설계 및 짝 테스트 작성          ← 이 문서. 승인됨. 완료
2. R1/R2/C를 하나의 새 frozen version으로 묶음   ← 다음 승인 대상
3. calibration
4. red-team
5. 전체 local test
6. Codex v8 qualification          ← 유료. 별도 승인 필요
7. Claude surface v3 qualification ← 유료. 별도 승인 필요
8. 독립 재감사
9. 그 뒤에만 primary 승인 여부 판단
```

**2단계부터는 이 문서만으로 착수하지 않는다.** 실제 코드 diff 적용, calibration
재실행, red-team 재실행, 유료 live qualification pilot 실행은 각각 별도
사용자 승인이 있어야 한다.

---

## R1 — qualification ledger에 셀별 결과 지문 고정

### 문제 재확인

재감사가 실제로 통과시킨 공격: `run_live_phase_c.py`의 `_assert_primary_qualifications`
(`:737-802`)는 artifact **전체 파일** SHA-256만 ledger와 대조한다
(`:790-800`). matrix(`config.pilot`)는 spec과 대조돼 보호되지만, **outcome
지표(`full_hard_gate`, `judged_payload_sha256` 등)는 ledger가 참조하지
않는다.** 따라서 matrix를 그대로 두고 점수만 고친 뒤 ledger의 `sha256`을
재계산해 넣으면 통과한다 — 재감사 §"R1 잔류 위험"의 실측 재현으로 확인됨.

### 설계

`_record_qualification`(`:870-881`)이 pilot 완료 시 ledger에 한 줄을
append한다. 현재:

```python
def _record_qualification(output_path: Path, out: dict[str, Any]) -> None:
    pilot = out["config"]["pilot"]
    _append_jsonl(RESULTS_DIR / QUALIFICATION_LEDGER_NAME, {
        "file": output_path.name,
        "sha256": _sha256_path(output_path),
        "config_file": out["config_file"],
        "config_sha256": out["config_sha256"],
        "arms": pilot["arms"],
        "case_ids": pilot["case_ids"],
        "qualification_passed": out["qualification"]["passed"],
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
```

제안 — 셀별 지문을 추가 필드로 append (artifact가 이미 들고 있는 값이므로
새 계산 없음):

```python
def _record_qualification(output_path: Path, out: dict[str, Any]) -> None:
    pilot = out["config"]["pilot"]
    cell_key = lambda r: f'{r["case_id"]}:{r["arm"]}'
    _append_jsonl(RESULTS_DIR / QUALIFICATION_LEDGER_NAME, {
        "file": output_path.name,
        "sha256": _sha256_path(output_path),
        "config_file": out["config_file"],
        "config_sha256": out["config_sha256"],
        "arms": pilot["arms"],
        "case_ids": pilot["case_ids"],
        "qualification_passed": out["qualification"]["passed"],
        # R1 — 점수만 고치고 파일 hash를 재계산해도 이 두 dict가 artifact와
        # 어긋나면 primary가 거부한다. append 시점에 이미 계산된 값을 옮길
        # 뿐이므로 새 채점 로직이 아니다.
        "judged_payload_sha256": {cell_key(r): r["judged_payload_sha256"]
                                  for r in out["results"]},
        "full_hard_gate": {cell_key(r): r["full_hard_gate"]
                           for r in out["results"]},
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
```

`_assert_primary_qualifications`(`:737-802`)에 대조 단계를 추가:

```python
# 기존 :790-800의 파일 해시 일치 검사 뒤에 추가
current_cells = {
    f'{r["case_id"]}:{r["arm"]}': (r["judged_payload_sha256"], r["full_hard_gate"])
    for r in artifact["results"]
}
ledger_cells = {
    k: (v, ledger_entry["full_hard_gate"][k])
    for k, v in ledger_entry.get("judged_payload_sha256", {}).items()
}
if current_cells != ledger_cells:
    raise LiveRunError(
        f"refusing primary: {path.name} outcome metrics do not match "
        f"the qualification ledger — score-only edit detected")
```

### 짝 테스트 설계

```python
def test_rewriting_only_outcome_metrics_is_refused_even_if_the_ledger_is_relinked(
        monkeypatch, tmp_path):
    """R1 재현 — 점수만 고치고 ledger sha256을 재계산한 artifact.
    수정 전 실측: 통과했다(재감사 2026-08-07)."""
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    path = tmp_path / "live_pilot_claude_mcp_surface_v2.json"
    artifact = json.loads(path.read_text())
    for r in artifact["results"]:
        r["full_hard_gate"] = True
        r["critical_path_recall"] = 1.0
        r["failure_codes"] = []
    path.write_text(json.dumps(artifact))
    led = tmp_path / live.QUALIFICATION_LEDGER_NAME
    lines = [json.loads(l) for l in led.read_text().splitlines() if l.strip()]
    for e in lines:
        if e["file"] == path.name:
            e["sha256"] = live._sha256_path(path)  # 공격자가 파일 해시만 재결속
    led.write_text("\n".join(json.dumps(e, sort_keys=True) for e in lines) + "\n")
    with pytest.raises(live.LiveRunError, match="outcome metrics do not match"):
        live._assert_primary_qualifications(CLAUDE_V2)


def test_an_untouched_artifact_still_matches_its_per_cell_ledger_entry(
        monkeypatch, tmp_path):
    """PRECISION — 거부만 하는 게이트는 primary를 영원히 막아 같은 관측을
    만든다. 수정하지 않은 artifact는 여전히 통과해야 한다."""
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    assert set(verified) == {
        "live_pilot_claude_mcp_surface_v2.json", "live_pilot_codex_mcp_v7.json"}
```

`_write_qualifications` 헬퍼(`test_preprimary_gates.py:39-51`)도 새
`judged_payload_sha256`/`full_hard_gate` 필드를 채우도록 갱신해야 한다.

---

## R2 — ledger의 matrix를 config 선언이 아니라 실행값에서 유도

### 문제 재확인

`_record_qualification`이 `out["config"]["pilot"]`(config 파일 선언)에서
`arms`/`case_ids`를 읽는다. `--arm`/`--case-id`로 축소 실행해도 ledger에는
config가 선언한 전체 matrix가 그대로 기록된다. **primary 게이트 자체는 이미
막는다**(`n_runs`/`per_arm` 불일치, 재감사 R2 실측 재현으로 확인). 문제는
ledger를 읽는 사람이 부분 실행을 완전 실행으로 오인할 수 있다는 라벨링
오류다.

### 설계

```python
def _record_qualification(output_path: Path, out: dict[str, Any]) -> None:
    executed_arms = sorted(out["per_arm"])
    executed_cases = sorted({r["case_id"] for r in out["results"]})
    _append_jsonl(RESULTS_DIR / QUALIFICATION_LEDGER_NAME, {
        ...,
        "arms": executed_arms,       # config 선언이 아니라 실행값
        "case_ids": executed_cases,  # 동일
        ...
    })
```

### 짝 테스트 설계

```python
def test_a_partial_pilot_run_leaves_a_partial_ledger_entry(monkeypatch, tmp_path):
    """축소 실행(--arm 하나)이 ledger에도 축소된 matrix로 남아야 한다."""
    # run_phase를 --arm S_DYNAMIC 하나로 호출하는 fake config로 실행
    # ledger 행의 arms == ["S_DYNAMIC"]

def test_a_complete_pilot_run_leaves_a_four_arm_ledger_entry(monkeypatch, tmp_path):
    """PRECISION — 완전 실행은 여전히 4-arm 행을 남긴다."""
```

---

## 요청 C — attempt ledger에 종결 상태 기록

### 사용자 요구 사양 (그대로 인용)

`started`만 기록하면 provider 호출 전 실패, 실행 중 중단, 정상 완료,
evaluator 실패, 사용자 취소, 프로세스 crash를 구별할 수 없다. append-only
구조를 유지해 다음 이벤트를 별도 행으로 추가한다: `attempt_started`,
`attempt_completed`, `attempt_failed`, `attempt_interrupted`. 각 종결 행은
같은 `authorization_sha256`과 `attempt_id`를 가져야 한다. 기존 `started` 행은
수정하거나 덮어쓰지 않는다.

### 설계

현재 `_claim_primary_attempt`(`:836-867`)는 시작 시점에 한 행만 append한다.
제안 — `attempt_id`를 시작 시점에 발급하고, `run_phase`가 primary 실행을
마친 뒤(성공/실패 어느 쪽이든) **새 행**으로 종결 이벤트를 append하는 별도
함수를 둔다.

```python
def _claim_primary_attempt(authorization_sha256, max_attempts, record):
    ...  # 기존 원자적 확인·카운트 로직은 그대로
    attempt_id = hashlib.sha256(
        f"{authorization_sha256}:{time.time_ns()}".encode()).hexdigest()[:16]
    entry = {**record, "authorization_sha256": authorization_sha256,
             "attempt_id": attempt_id, "event": "attempt_started"}
    handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    ...
    return attempt_id  # run_phase가 종결 기록에 재사용


def _record_primary_attempt_outcome(attempt_id: str, event: str,
                                    detail: dict[str, Any]) -> None:
    """event: attempt_completed | attempt_failed | attempt_interrupted.
    기존 started 행을 절대 수정·삭제하지 않는다 — 새 행만 append."""
    path = RESULTS_DIR / PRIMARY_ATTEMPT_LEDGER_NAME
    _append_jsonl(path, {"attempt_id": attempt_id, "event": event, **detail,
                         "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                       time.gmtime())})
```

`run_phase`의 primary 분기(`:914-948`)에 `try/except/finally`로 감싸
`attempt_completed`(정상 종료) 또는 `attempt_failed`(예외)를 기록한다.
`attempt_interrupted`(SIGINT/SIGTERM 등)는 시그널 핸들러나 프로세스 종료
훅으로 별도 검토가 필요하다 — 이 설계 단계에서는 정상/예외 두 경로만
구체화하고, interrupted 처리는 구현 단계에서 결정한다.

### 짝 테스트 설계

```python
def test_a_completed_primary_run_appends_a_completed_event_without_touching_started():
    """started 행이 그대로 있고, completed 행이 같은 attempt_id로 추가된다."""

def test_a_failed_primary_run_appends_a_failed_event_with_the_same_attempt_id():
    """provider 예외 발생 시 failed 이벤트가 남는다."""

def test_reading_only_the_started_event_undercounts_terminal_state():
    """PRECISION의 반대 — started만 읽으면 완료 여부를 알 수 없다는 것
    자체를 회귀로 고정해, 이 설계가 실제로 정보를 추가했음을 증명한다."""
```

### frozen-surface 판정

이 변경은 `run_live_phase_c.py`를 수정하므로 **frozen-surface 변경이다.**
사용자 결정에 따라 R1/R2와 함께 v8/surface-v3에 묶어 한 번만
재-qualification한다.

---

## 다음 단계 (승인 대기)

1. 위 세 설계에 대한 실제 코드 diff와 새 pytest 케이스를
   `run_live_phase_c.py`, `_evaluator.py`(필요 시), `test_preprimary_gates.py`에
   적용 — **미승인**.
2. `phase_c_codex_mcp_v8_config.json` / `phase_c_claude_mcp_surface_v3_config.json`
   신설, `FROZEN_SURFACE_FILES`/`ALLOWED_CONFIG_NAMES`에 추가 — **미승인**.
3. calibration, 두 red-team, 전체 local test 재실행 — **미승인**.
4. Codex v8 / Claude surface v3 유료 qualification pilot 실행 — **미승인**.
5. 독립 재감사 — v8/v3 완료 후.
6. primary 승인 여부 판단 — 5단계 완료 후에만.

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/feedback/claude_redteam_preprimary_reaudit_20260807|Amendment 21 재감사 — R1/R2 원 발견]]
- [[docs/feedback/claude_questions_for_source_session_20260807|질문 1 답변 — 묶음 순서 승인 근거]]
- [[concept-gate-codex-mcp-wt/experiments/2026-08-07_handoff_dynamic_controller/run_live_phase_c.py|현재 v7/v2 구현]]
- [[experiments/2026-08-07_handoff_dynamic_controller/test_preprimary_gates.py|현재 pre-primary 테스트]]
