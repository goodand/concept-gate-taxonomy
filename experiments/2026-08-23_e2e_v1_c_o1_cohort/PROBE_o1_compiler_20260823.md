# o1-compiler 배선 프로브 기록 — 2026-08-23

## 준비물 ① (agent 정의)의 검증. 두 프로브, 하나는 이월.

**정의**: `~/.claude/agents/o1-compiler.md` (이 폴더의 `o1-compiler.md`와
바이트 동일, sha256 `891dd0d6c2cfc8f7…`). h1a-decider 격리 껍데기 계보 —
정의는 격리·출력 규율만 담고, 과제 의미론(IR 방언·문장)은 전부 프롬프트가
담는다. 정적 검사: frontmatter 3필드, 금지 어휘 0(corpus명·oracle·gold·
quantifier 등 미등장), 격리 조항 5/5.

## 프로브 A — agentType 레지스트리 (BLOCKED, 세션 재시작으로 이월)

`agentType: "o1-compiler"` dispatch가 "not found"로 거부됨 — 레지스트리는
세션 시작 시 적재되고 이 정의는 세션 중 생성됐다. **부재가 아니라 적재
시점 문제**(사용 가능 목록에 기존 decider 8종은 전부 보임). 다음 세션
첫 작업으로 재실행한다.

## 프로브 B — 의미 등가 프로브 (zero-context haiku, 정의 본문 인라인)

발명 문장 `Every zorble glims.` + 방언 명세 전문 제시. corpus 0바이트.

결과 (verbatim):
- 산출 구조: `forall(x, restriction=pred(zorble,[x]), body=pred(glims,[x]))`
  — **커널 판정: validate_formula 오류 0, 자유변수 0(닫힘), GQ-restriction
  형태 정확.** zero-context 최소 티어가 이 방언을 다룰 수 있다는 신호.
- **출력 규율 위반 1건**: 전체 메시지를 ```json fence로 감쌌다 — 정의의
  "no markdown fence"를 어겼다.

## 판정과 파급

구조 능력: 신호 긍정. 출력 규율: **프롬프트 규율만으로는 불충분** — D-19가
trial subject를 "schema-forced"로 명령한 이유가 이 프로브로 실증됐다.
따라서 코호트 dispatch는 반드시 스키마 강제(StructuredOutput) 경로를 쓴다
(준비물 ②의 재귀 JSON 스키마가 그 강제 장치다). fence 파싱 관용
(lenient strip)은 도입하지 않는다 — 규율 위반을 흡수하는 파서는 위반을
비가시화한다.

주의: 프로브 B는 의미 등가물(정의 본문을 전문에 인라인)이지 레지스트리
경유가 아니다. 정의 파일 자체의 라이브 결박은 프로브 A 재실행 + 코호트의
definition_sha256 pin(준비물 ③)이 담당한다.
