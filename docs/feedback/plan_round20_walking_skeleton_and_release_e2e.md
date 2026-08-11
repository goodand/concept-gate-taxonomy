# 수정·검증 계획 — 20라운드: Walking Skeleton으로 전환

작성 2026-08-11. 대상 커밋 `1f12e2f` / `3f9c2f9`. **검증 완료, 미착수.**

## 검증 결과 (6/6 재현)

| # | 지적 | 실측 |
|---|---|---|
| 1 | stage 단위 coverage가 미보호 obligation을 숨김 | 미보호 stage `['packet.built','primary.synthetic-built','reviewer.qualification-scored']`, **그 밖에** `reviewer.assignment.frozen`이 stage covered라 숨음 |
| 2 | release E2E 없음, 테스트가 PARTIAL을 허용 | `in (0, 2)` 2곳, `release`/`offline-smoke` **0건** |
| 3 | reviewer isolation은 자기신고 boolean | launcher **부재**, 손으로 쓴 PASS JSON과 구별 불가 |
| 4 | closure가 명령이 아님 | 서브커맨드는 `doctor`, `e2e` 둘뿐 |
| 5 | provenance canonicalization 2벌 | `_receipt_sha256` 2개, 주석이 인용한 일치 테스트 **없음** |
| 6 | 한 커밋에 설계·코드·결과·운영문서 혼재 | `1f12e2f`가 6종을 함께 변경 |

## 진단 — 리뷰어의 전략 판단을 받아들인다

**#1과 #5는 제 커밋 메시지를 반증한다.** "one canonical for each thing"이라고
쓴 커밋에 canonicalization이 두 벌 있었고, "개수 비교를 집합 일치로 바꿨다"고
쓴 커밋의 **단위 자체가 틀렸다**(stage ≠ obligation). #5의 주석은 **존재하지
않는 테스트를 인용한다** — 이 세션이 세 번 기록한 "문서가 계약을 가르친다"의
다섯 번째다.

**그러나 개별 수정으로 대응하면 20라운드도 같은 모양이 된다.** 12~19라운드가
전부 그랬다. 리뷰어의 전략 판단이 맞다:

> 현재 가장 우선할 구현은 추가 reviewer가 아니라 **reviewer launcher와
> `e2e --release`**다.

방어를 다 완성한 뒤 E2E가 아니라, **가장 얇은 실제 수직 경로를 먼저 끝까지
성공시키고 그 경로를 강화한다**(Walking Skeleton + Tracer Bullet + Outside-in
Acceptance TDD). workspace 선례도 같다 — 스모크·qualification·본 실행·재실행이
**동일 canonical builder**를 쓰고 그 경로 자체가 필수 통합 테스트다
(`DESIGN_DECISION_surface_separation.md` §3, 필수 테스트 #7).

**따라서 이번 라운드는 기능 동결이다.** 새 guard와 비차단 리팩터링을 멈춘다.

---

## 수정 계획

### 단계 A — 완료 단위를 obligation으로 (#1)

stage 차집합을 버린다.

```python
OBLIGATIONS: dict[str, Verdict] = {
    "audit.input-validated":            PASS,
    "audit.provenance.bytes-compared":  PASS,
    "audit.provenance.propagated":      PASS,
    "packet.blinding.applied":          PASS,
    "reviewer.qualification.required":  PASS,
    "reviewer.assignment.frozen":       UNKNOWN,   # ← 더 이상 숨지 않는다
    "reviewer.count.enforced":          PASS,
    "bundle.written.to.disk":           PASS,
}
overall = PASS only if every obligation is PASS
```

- `conceptgate/cg_obligations.py`의 `Verdict`/`aggregate()`를 **재사용**한다
  (PASS/FAIL/UNKNOWN, "전부 PASS일 때만 PASS"). 새 어휘를 만들지 않는다.
- `run_pipeline.py`의 자체 coverage 계산을 **제거**하고 집계 결과를 출력한다.
- `reviewer.assignment.frozen`은 E2E에 단계를 하나 추가해 실제로 보호한다 —
  **미선언 reviewer_id를 CLI로 제출**하고 거부를 요구한다(단계 6이
  자격 미달을 제출하는 것과 같은 형태).

### 단계 B — `e2e`를 세 모드로 (#2)

하나의 `run_pipeline(RunSpec)`을 세 진입점이 호출한다. **세 명령이 서로 다른
파이프라인을 가지면 안 된다.**

| 명령 | 성공 | 용도 |
|---|---|---|
| `e2e --offline-smoke` | 0 또는 2 | 빠른 연결 확인(현재 동작) |
| `e2e --release` | **오직 0** | 실제 launcher 포함. 여기서 PARTIAL은 실패 |
| `e2e --primary` | 0 | 32칸 정식. release 통과 후에만 허용 |

테스트도 나눈다: smoke 테스트는 `in (0, 2)`, **release 테스트는 `== 0`**.
지금처럼 하나의 테스트가 둘 다 허용하면 **프로그램이 영구히 PARTIAL이어도
초록**이다.

### 단계 C — Reviewer Launcher (#3) — **이번 라운드의 본체**

새로 설계하지 않는다. 두 선례를 조합한다.

```
public-only bundle          .vault-harness/vault-md-retrieval/
  (.git·hidden_gold·        build_handoff_reuse_public_bundle.py
   private_eval·results·      — 제외 목록 + symlink 거부
   runs 제외, symlink 거부)
        ↓
Seatbelt v2 profile         _providers.py:150
  (repo·transcript·           — /bin/cat 실제 probe로 v1 누출을 발견한 방식
   .codex·answers deny)
        ↓
allowed / forbidden probe   PROVIDER_ADAPTERS.md §55
        ↓
reviewer 실행 (packet-only cwd)
        ↓
host-owned receipt          ← reviewer가 제출한 boolean이 아니라
                              launcher가 관측해 서명한 것
```

**핵심 수정**: 현재는 reviewer가 낸 JSON의 boolean을 믿는다. receipt는
**launcher가 만들고** packet·assignment·profile 해시에 결속돼야 한다.

sandbox를 실행할 수 없는 환경이면 그 감사는 **BLOCKED**(skip 아님).

### 단계 D — `closure` 명령 (#4)

규율을 명령으로 옮긴다.

```bash
python3 run_pipeline.py closure
```

```
source freeze 확인 (git status)
→ calibration
→ Codex red-team
→ provider red-team
→ 전체 hash 재검사
→ closure receipt 생성 (results/closure_<sha>.json)
```

closure receipt가 없거나 현재 해시와 다르면 **`e2e --release`가 거부**한다.
"개발자가 순서대로 실행하는 규율"을 남겨두면 I106이 재발한다.

### 단계 E — canonicalization 1벌 (#5)

`_receipt_sha256`을 `_provenance.VerifiedRunReceipt.canonical_bytes()` /
모듈 함수 `receipt_sha256()`로 옮기고 두 소비처가 **import**한다.
주석이 인용한 존재하지 않는 테스트는 **실제로 만든다**(양쪽이 같은 함수를
쓰는지 AST로 확인).

### 단계 F — 커밋 분리 (#6)

`EXPERIMENT_METHODOLOGY.md` §1이 요구하는 대로 나눈다:

1. **설계 freeze** — PREREGISTRATION 개정
2. **구현** — 코드 + 테스트
3. **결과** — calibration / red-team artifact (closure가 생성)
4. **운영 문서** — handoff, plan, 회고

지금까지 한 커밋에 섞은 것이 리뷰 범위를 키웠다.

---

## 실행 순서

```
E(canonicalization 1벌) → A(obligation 단위) → B(모드 분리)
→ C(launcher) → D(closure 명령) → F(커밋 분리)
→ release E2E 통과 → 1 case × 1 arm live canary
→ 32칸 확장 → qualification 재실행 → primary
```

- **E를 먼저**: 가장 작고, A·B가 그 위에 선다.
- **C가 본체이고 가장 크다.** B의 `--release`가 C 없이는 의미가 없다.
- **D를 C 다음**: closure receipt를 release가 요구하므로 release가 먼저 존재해야
  한다.
- **F는 마지막이 아니라 방식이다** — 위 단계들을 4개 커밋으로 나눠 낸다.

## 검증 계획

각 단계는 실패 검사를 먼저 만든다(TDD 규칙 1).

| 단계 | 먼저 빨갛게 | 통과 기준 |
|---|---|---|
| E | `_receipt_sha256` 구현이 2개면 실패 | `def _receipt_sha256` **1건**, 양쪽이 같은 함수를 import |
| A | `reviewer.assignment.frozen`이 UNKNOWN인데 overall이 PASS면 실패 | 미선언 reviewer 제출이 CLI에서 거부, obligation 8종 전부 PASS일 때만 overall PASS |
| B | `--release`가 PARTIAL에서 0을 반환하면 실패 | smoke `in (0,2)`, release `== 0`, 세 모드가 **같은 `run_pipeline(RunSpec)`** 호출 |
| C | reviewer가 답안 파일·저장소·key에 **도달 가능**하면 실패 | `/bin/cat` 실제 probe. launcher-서명 receipt가 packet·assignment·profile 해시에 결속 |
| C | 손으로 쓴 PASS JSON → **거부** | receipt 서명 부재 시 BLOCKED |
| D | 문서 한 줄 고친 뒤 `closure` 미실행 → `--release` **거부** | closure receipt 해시가 현재와 일치 |
| F | — | 4개 커밋, 각각 독립적으로 리뷰 가능 |

**환경 표기**: `N passed (이 환경)` / `Seatbelt M건 BLOCKED (권한 없는 환경)`.
리뷰어 환경 실측 225/6, 이 환경 231/1skip.

## 리뷰 종료 조건 (리뷰어 제안 채택)

**반드시 수정**: release E2E 실패 또는 exit 2 / provenance가 최종 번들까지 미결속
/ hidden data가 reviewer에 도달 / 무효 실행이 유효로 집계 / 결과 의미나 headline이
뒤집힘 / 원본 evidence 손실·변조 미탐지.

**E2E 이후로 미룸**: private helper import, 파일 분리·naming, 중복 주석, 성능
무관 구조 개선, acceptance path가 이미 잡는 방어의 중복.

이 기준을 세션 계약으로 고정한다. 그러지 않으면 20라운드도 12~19라운드와 같은
모양이 된다.

## 낮춰야 할 주장

- **"미보호 stage 3"** — 커버리지 전부가 아니다. 미보호 **의무**는 최소 4건.
- **"one canonical for each thing"**(커밋 `1f12e2f` 제목) — canonicalization이
  두 벌이었다.
- **주석의 `test_the_receipt_hash_is_computed_the_same_way_on_both_sides`** —
  그런 테스트는 없다.
