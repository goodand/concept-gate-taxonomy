---
aliases:
  - Design Decision — Mention Channel And Stub Floor
tags:
  - doc/design-decision
  - stage/handoff
  - status/deferred
---

# 설계 판정 — mention 채널과 0바이트 stub (경로 C, 구멍 7)

**상태: 판정됨, 구현 보류.** 이 판정은 사용자가
[[docs/feedback/claude_questions_for_source_session_20260807|질문 5]]에서
직접 내렸다. 대상은 `scripts/handoff_repair_loop.py`(별도 repair-loop
harness)이며, **현재 dynamic-controller 실험(`experiments/2026-08-07_handoff_dynamic_controller/`)의
frozen surface에는 섞지 않는다.** handoff repair/evaluation harness의 다음
버전에서 별도로 구현한다.

원 미결 항목: `redteam_handoff_repair_loop_20260806.md:49,121,123`
(경로 C, 구멍 7).

## 판정 1 — mention 채널 (경로 C)

backtick mention(`` `path` ``, 링크가 아닌 단순 텍스트 인용)의 취급을
`redteam_handoff_repair_loop_20260806.md:49` "경로 C — 링크를 mention으로
변환"이 열어 둔 문제였다: 링크를 mention으로만 바꿔도 finding이 사라지는
현상을 게임으로 볼 것인가, mention 자체가 정당한 도달 경로인가.

**판정:**

1. backtick mention은 **structural reachability edge로 인정하지 않는다.**
2. 검색 reformulation에 사용할 수 있는 **referral hint로만 분류한다.**
3. mention을 canonical link나 source authority로 **승격하지 않는다.**
4. G2/G3를 Markdown link와 **동일하게 적용하지 않는다.**
5. link → mention 변환으로 finding만 감소한 경우 `metric-fake` 또는
   `representation-only change`로 기록한다 — 실제 수리가 아니라 채점기를
   속인 변경이라는 뜻이다.

### 구현 시 필요한 최소 변경 (미착수)

- `handoff_repair_loop.py`의 도달성 계산 경로에서 mention 매칭과 link 매칭을
  **별도 카운터**로 분리한다.
- link → mention 변환만으로 orphan 수가 줄면 `metric-fake`로 태그하는
  검출기를 추가한다(예: 커밋 전후 diff에서 링크 마크업이 mention으로
  바뀌었는데 대상 파일 집합은 그대로인 패턴).
- 짝 테스트: mention만 있는 파일은 여전히 orphan으로 잡힘(양성) / 실제 링크가
  있는 파일은 orphan에서 빠짐(PRECISION).

## 판정 2 — 0바이트 stub (구멍 7)

단순 최소 byte 크기 요구는 **채택하지 않는다** — 공백이나 임의 문자열로
쉽게 게임할 수 있기 때문이다.

**판정:**

dangling 해소로 인정하려면 target이 다음을 **모두** 만족해야 한다.

1. 고정 manifest에 포함됨
2. non-empty semantic content **또는** 명시적인 canonical pointer를 가짐
3. content hash가 검증 가능함
4. authority class가 지정됨
5. parse 가능함(대상 형식으로 유효하게 파싱됨 — 예: Markdown이면 최소한
   frontmatter나 heading 구조를 가짐)

### 구현 시 필요한 최소 변경 (미착수)

- dangling 해소 검사 함수에 위 5개 조건의 논리곱을 추가한다.
- 짝 테스트: 공백/임의 문자열로 채운 stub은 여전히 dangling으로 거부(양성) /
  실제 의미 있는 최소 문서(frontmatter + 한 문단)는 통과(PRECISION).

## 이 판정이 dynamic-controller 실험에 영향을 주지 않는 이유

`experiments/2026-08-07_handoff_dynamic_controller/`의 corpus·gold·evaluator는
`scripts/handoff_repair_loop.py`와 별개 코드베이스다
(`PREREGISTRATION.md` §0 — "상위 코드를 복사하지 않는다"). 이 판정을 반영하려면
`scripts/handoff_repair_loop.py`와 그 테스트만 고치면 되고, dynamic-controller
쪽 `FROZEN_SURFACE_FILES`/qualification artifact는 영향받지 않는다 —
`FROZEN_SURFACE_FILES`(`_evaluator.py:218-256`)에 `scripts/handoff_repair_loop.py`가
없음을 확인했다.

```
$ python3 -B -c "
import sys; sys.path.insert(0,'experiments/2026-08-07_handoff_dynamic_controller')
from _evaluator import FROZEN_SURFACE_FILES
print('handoff_repair_loop.py' in str(FROZEN_SURFACE_FILES))"
False
```

## Obsidian Backlink

- [[docs/feedback/codex_mcp_handoff_moc_20260807|Codex MCP Handoff MOC]]
- [[docs/feedback/redteam_handoff_repair_loop_20260806|원 미결 항목 — 경로 C, 구멍 7]]
- [[docs/feedback/claude_questions_for_source_session_20260807|질문 5 — 사용자 판정 원문]]
