# 수정·검증 계획 — 19라운드 (Amendment 40 예정)

작성 2026-08-11. 대상 커밋 `98c604f`. **검증 완료.**

## 검증 결과 (7/7 재현)

| # | 지적 | 실측 |
|---|---|---|
| 1 | 커밋 상태의 artifact가 이미 stale | `PREREGISTRATION.md` = `4d53fccb`, calibration·red-team 2종 = `4eec976f`. doctor FAIL 원인이 보고한 qualification이 아니라 `PREREGISTRATION.md` |
| 2 | synthetic 표식이 최종 번들에 전파 안 됨 | packet 1회, key 0회, `safety_audit` 0회 |
| 3 | "개수 비교 폐기" 과장 | `assert covered >= 5` 잔존, stage↔obligation 대응표 없음 |
| 4 | active worktree의 production 파일 직접 변조 | `path.write_text(mutated)` |
| 5 | typed verdict 전환 부분적 | `if status not in (None, "PASS")` |
| 6 | doctor의 attempt 판정이 claim보다 약함 | `remaining_primary_attempts`에 체인 검증 0회 |
| 7 | "검증을 구현하지 않는다"도 부정확 | `_provenance.py`가 원장을 직접 읽고 hash 재비교 |

## 진단

**#1은 보고 무결성 실패다.** 게이트는 있었고 정확히 이걸 잡는다. 나는 그것을
**마지막에 돌리지 않았고**, 그러면서 이전 측정치를 커밋 상태의 것처럼 제시했다.
규율(“마지막에 다시 돌린다”)이 실패한 것이며, 이 저장소는 규율이 반복 실패하면
기제로 옮긴다.

**#2·#3·#5·#6·#7은 하나의 형태다: 정본이 둘로 갈라져 있다.**
provenance 정본이 packet에만 있고 번들에 없다. obligation 정본이 이름표는 생겼는데
집합 일치가 아니라 개수다. verdict 정본이 예외에는 있고 artifact에는 없다.
attempt 정본이 claim 게이트와 doctor에 각각 있다. 리뷰어의 정리가 정확하다 —
**필요한 것은 검사 추가가 아니라 정본을 하나로 유지하는 것**이다.

---

## 수정 계획 (단계별, 각 단계마다 검증)

### 단계 0 — Freeze Closure를 기제로 (#1)

**규율로 두지 않는다.** 다음을 추가한다:

- `test_frozen_artifacts_are_current` — calibration **과 red-team 2종** 모두의
  `frozen_surface_hashes`가 현재와 일치하는지. 지금은 calibration만 검사한다.
- `run_pipeline.py closure` — 커밋 직전 1회 실행. 재생성이 필요한 artifact를
  **순서대로** 나열하고, 하나라도 stale이면 `exit 1`.
- 순서를 문서가 아니라 스크립트가 안다:
  `calibration → redteam(codex) → redteam(provider) → 최종 drift 검사`

**보고 규칙도 같이 고친다**: 수치를 인용할 때는 **그 수치를 낸 명령과 커밋
상태가 같음**을 `closure`로 확인한 뒤에만 쓴다.

### 단계 1 — Provenance Envelope (#2)

`VerifiedRunReceipt`가 packet → key → 최종 번들까지 간다.

```
packet.provenance          = receipt.as_dict()
key.provenance_sha256      = sha256(canonical(receipt))
bundle.safety_audit.provenance = { mode, result_sha256,
                                   authorization_sha256, attempt_id,
                                   receipt_sha256 }
```

- adjudicator는 packet의 receipt를 **승격**한다. 원본 artifact의
  `synthetic: true` 자기신고에 의존하지 않는다.
- packet의 receipt를 고치면 key 대조에서 거부된다.
- **provenance 없는 번들은 headline을 낼 수 없다** — `adjudicated_full_hard_
  gate_rate`를 `None`으로 두고 이유를 적는다.

### 단계 2 — 단일 Provenance Verifier (#7)

**이미 부분 착수됨**(이번 세션에서 `verify_primary_attempt_artifacts`에
`results_dir`를 추가하고 `find_completed_attempt`·`read_attempt_ledger`를
추출했다). 남은 것:

- canonical/synthetic이 **같은 코드 경로**를 타고 차이는 storage와 `trust_mode`뿐
- `rg "_parse_ledger_lines"` 결과가 **1건**이어야 한다
- 감사 코드에 `json.loads(... ledger ...)`가 남아 있지 않아야 한다

### 단계 3 — Obligation Coverage Registry (#3)

개수를 **집합 일치**로 바꾼다.

```python
assert declared_stage_ids == observed_stage_ids
assert declared_obligations == mutated_obligations
assert uncovered == set()
```

- E2E의 각 stage에 **문자열 ID**를 부여하고 출력에 찍는다
  (`[3] packet.blinded  ...`)
- 각 obligation은 stage ID를 참조한다
- `NO_SIGNAL_YET`이 비어 있지 않으면 **E2E 전체 결과가 `PARTIAL`**이고
  `exit 2`(BLOCKED)다. 지금처럼 PASS가 아니다 — `cg_obligations.aggregate()`가
  “전부 PASS일 때만 PASS”인 것과 같은 규칙.

### 단계 4 — 격리된 Mutation Workspace (#4)

active 파일을 건드리지 않는다.

- `git worktree add --detach <tmp> HEAD` 로 임시 트리를 만들고 거기서 변이
- subprocess의 cwd는 그 트리
- manifest에 `tree_sha`를 기록
- SIGKILL 후에도 active worktree가 clean해야 한다

worktree 생성이 불가능한 환경이면 그 테스트는 **BLOCKED**(skip 아님).

### 단계 5 — Typed Gate Report (#5·#6)

- persisted artifact의 `status`가 없거나 enum 밖이면 **BLOCKED**. `None`을
  하위 호환 PASS로 취급하지 않는다.
- `remaining_primary_attempts`가 claim 게이트와 **같은 검증**을 한다:
  `verify_ledger_chain`, legacy prefix pin, 이전 completed artifact 무결성.
  손상된 원장에서 doctor가 PASS를 표시하고 claim이 거부하는 상태를 없앤다.
- 가능하면 `GateResult(gate_id, verdict, evidence, reason_code)`로 통일하고
  doctor는 직렬화만 한다.

### 단계 6 — Reviewer Isolation (#7, 이전 라운드 #3)

**이번 범위에 넣지 않는다.** 단, 현재의 “파일 존재 여부” 검사가 빈 stub으로
PASS가 될 수 있다는 지적은 맞으므로, **PASS 조건을 artifact로 바꾼다**:

```json
{"status":"PASS","reviewer_id":"...","packet_sha256":"...",
 "sandbox_profile_sha256":"...","allowed_probe_passed":true,
 "forbidden_probe_passed":true,"answer_key_reachable":false,
 "repository_reachable":false}
```

이 artifact가 없으면 **BLOCKED**. launcher 구현은 다음 라운드이며, 그때
`_providers.py`의 Seatbelt v2 생성기와 `.vault-harness`의 public-only bundle을
재사용한다.

---

## 실행 순서

```
2(단일 verifier, 착수분 마무리) → 1(envelope) → 5(typed) → 3(registry)
→ 4(격리 mutation) → 6(reviewer PASS 조건) → 0(closure) → 재생성 → 커밋
```

**0을 마지막에 두는 것이 핵심이다.** closure는 “문서·코드 편집이 끝난 뒤”에만
의미가 있고, 이번 라운드의 결함이 정확히 그 순서를 어긴 것이다.

## 검증 계획

각 단계는 **실패하는 검사를 먼저** 만든다(TDD 규칙 1). 단계별 통과 기준:

| 단계 | 먼저 빨갛게 만들 것 | 통과 기준 |
|---|---|---|
| 2 | synthetic root에서 `verify_primary_attempt_artifacts`가 실제로 호출되는지 | `rg "_parse_ledger_lines"` = 1건, 감사 코드에 ledger 직접 읽기 0건 |
| 1 | top-level `synthetic` 필드를 **지운** artifact로 E2E → 최종 번들이 `synthetic-e2e` | packet receipt 변조 시 거부, provenance 없는 번들은 rate `None` |
| 5 | `status` 없는 red-team artifact → readiness **BLOCKED** | 손상된 원장에서 doctor와 claim이 **같은 판정** |
| 3 | stage 하나를 registry에 안 넣고 추가 → 집합 불일치로 실패 | `NO_SIGNAL_YET` 비어있지 않으면 e2e `exit 2` |
| 4 | mutation 중 SIGKILL → active worktree clean | 병렬 실행 가능, manifest에 `tree_sha` |
| 6 | 빈 `reviewer_runner.py` stub → 여전히 **BLOCKED** | probe artifact 없으면 PASS 불가 |
| 0 | 문서 한 줄 고친 뒤 `closure` → `exit 1` | clean checkout에서 drift 0, 전체 테스트 재생성 없이 통과 |

**환경 표기**: 결과는 `N passed (이 환경)` / `Seatbelt M건 BLOCKED (권한 없는
환경)`로 병기한다. 리뷰어 환경 실측은 213/7이었고 그중 1건은 결정론적이었다 —
그 1건이 #1이다.

## 이번 라운드에서 낮춰야 할 주장

- **“220 tests, calibration 8/8·60/60, red-team 2종 PASS”** — 그 수치는 커밋
  `98c604f`의 상태가 아니다. Amendment 39 추가 **이전** 측정이다.
- **“synthetic 표식이 최종 번들까지 따라간다”** — packet까지만 간다.
- **“개수 비교를 폐기하고 obligation 매핑으로 교체”** — 이름만 바뀌었고 검사는
  아직 개수다.
- **“`_provenance.py`는 검증을 구현하지 않는다”** — 원장을 직접 읽고 hash를
  다시 비교했다.
