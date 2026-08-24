# 코호트 수락 무결성 — L0→L2 drill-down (2026-08-24)

- 대상: `experiments/2026-08-23_e2e_v1_c_o1_cohort/` 의 채점 진입점과 그것을
  지키는 게이트들. 기록 [[DRYRUN_20260824]] · 상태 정본
  [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 렌더러: 등록된 `mcp-kroki` MCP(`download_diagram`, graphviz → SVG).
  **`.dot`이 canonical source, `.svg`는 렌더 산출물.**
- 방법: 가장 추상화된 층부터 그리고, **각 층을 실제 코드와 대조해 정합성을
  평가한 뒤에만** 다음 층으로 내려갔다(사용자 지정 방식).

## 층

| 층 | 파일 | 레지스터 | 코드 정합성 |
|---|---|---|---|
| L0 | [`acceptance-integrity-L0.dot`](acceptance-integrity-L0.dot) → [svg](acceptance-integrity-L0.svg) | (0)불변 · (1)궁극 목적 재귀 · (2)expected_output · (3)조건 · (4)확실성 | **6/6** (2차) |
| L1 | [`acceptance-integrity-L1.dot`](acceptance-integrity-L1.dot) → [svg](acceptance-integrity-L1.svg) | 실제 함수·정지 지점·동결 입력 | **18/18** |
| L2 | [`acceptance-integrity-L2.dot`](acceptance-integrity-L2.dot) → [svg](acceptance-integrity-L2.svg) | 우회 경로의 호출자 계수 | **일치** |

왕복 검증: L1은 `.dot` 재렌더가 커밋 SVG와 **1434×638pt · 노드 16 · 간선 17**로
정확히 일치. L0·L2는 `.dot` 라벨이 SVG 텍스트에서 각각 16/17·12/12 확인.

## L0의 1차 판이 코드보다 앞서 있었다 — 이 저장소가 이미 이름을 붙인 실패

1차 L0은 `(2) expected_output`을 **"어떤 호출 경로도 부당하게 True를 낼 수
없다"**고 적었다. 코드 대조에서 거짓으로 드러났다 — `ingest_outputs`가 여전히
공개이고 `stratum_floors=None` 기본값이며, **이 저장소의 음성 대조 테스트가 그
우회가 통한다는 것을 증명하고 있었다.** 구멍을 문서화하는 테스트를 쓰고 나서
구멍이 닫혔다고 주장하는 그래프를 그렸다.

**이 실패에는 이미 이름과 선례가 있다.** 같은 폴더의
[`README.md`](README.md) "as-built 정직성" 절:

> Z0~Z2를 현재 코드의 서술로 읽으면 안 된다 — **"다이어그램이 코드보다 앞서
> 있었다"가 codex 라인이 Amendment 36에서 겪고 기록한 실패 형태**이고, 이
> 표기가 그 재발 방지다.

그 절이 처방한 것은 표기(target vs as-built)였다. 이번엔 표기로 넘기지 않고
**코드를 고쳐 주장을 참으로 만들었다**(아래 §2). 그리고 닫히지 않은 부분은
그래프에 **점선 우회 경로로 그려 두었다** — 지우지 않고 보이게 두는 것이
as-built 정직성의 형태다.

## 정합성 검증이 적발한 것 — 같은 결함의 2호

L0 대조에서 두 번째가 나왔다: `ingest_cohort`가 **층 하한은 유도하면서 오라클은
인자로 받고** 있었다. 즉 커밋 해시 검사(`OracleDrift`)를 호출자가 빼먹을 수
있었다 — 층 하한과 **같은 모양의 구멍이 같은 함수 안에** 하나 더 있었다.
서명에서 `expected_irs`를 없애 닫았다.

**층 하한 하나를 고치면서 같은 모양 둘을 남겼다**는 것이 이 drill-down의
실질 소득이다. 추상 층에서 명제로 적어야 반증 가능해진다.

## 이 저장소가 이미 쓰던 기제 — 인용

새로 발명한 것이 없다. 각 항목의 선례를 실측으로 확인해 인용한다.

| 이번에 쓴 것 | 이미 있던 선례 | 위치 |
|---|---|---|
| **유도로 면제 경로를 없앤다** (경고 강화 아님) | "인자를 빠뜨리면 초록이 되던 구멍 — manifest 유도로 면제 경로를 없앤다" | `evidence-evaluator` 커밋 `dbf6051` (2026-08-24) |
| **이유를 강제하는 allowlist** (`ALLOWED`) | `KNOWN_UNPROVEN: dict[str, str]` — 면제마다 이유 문자열 필수 | `test_guard_negative_coverage.py:54` |
| **낡은 등재 행 검출** | `vanished = sorted(name for name in KNOWN_UNPROVEN if name not in raising)` | `test_guard_negative_coverage.py:167` |
| **AST로 세기** (grep은 문맥을 못 본다) | `_can_raise(fn)` / `_called_name(call)` — 가드를 AST로 수집 | `test_guard_negative_coverage.py:72-78` |
| **후계자·이유 없는 등재 거부** | "superseded_by가 비어 있다 … 이것은 legacy가 아니라 미결정이다" | `test_legacy_register.py:92-93` |
| **음성 테스트는 실입력으로** (모킹 금지) | "모킹 기반 음성 테스트는 게이트를 초록으로 만들면서 아무것도 [증명하지 않는다]" | `docs/HARNESS_KNOWHOW.md:227,233` |
| **다이어그램이 코드보다 앞서는 실패** | "as-built 정직성" · codex Amendment 36 | [`README.md`](README.md) |

`ALLOWED`가 `KNOWN_UNPROVEN`의 형태를 그대로 따른다 — 면제 목록 + 이유 강제 +
낡은 행 검출 세 벌. 그 셋이 함께 있어야 등재가 느슨해지지 않는다는 것은
`test_guard_negative_coverage.py`가 이미 배운 것이다.

## 재렌더

```bash
# 등록된 mcp-kroki MCP: download_diagram(type="graphviz", content=<.dot 내용>)
```
