# runs/preregistered/

30 raw responses collected under the exact preregistered E2.1 conditions
(`_prompts.json`의 프롬프트 원문, 수정 없음): `claude -p --model haiku`
(Claude Code CLI, OAuth), isolated subprocess per trial, no CLAUDE.md/`.claude`
in cwd, `--disallowedTools`로 전체 내장 도구 차단, system prompt 수정 없음.

이 코호트가 E2.1의 **공식(protocol-strict) trial**이다 — 저장소 루트의
`trials.json`은 이 코호트로 조립됐다.

파일: `{execution_order:02d}.json`(claude -p의 `--output-format json` 원문
그대로, `result` 필드가 raw_response로 쓰였다) + `_timestamps.log`(started_at/
completed_at, UTC).

결과: 30/30 응답이 markdown 코드펜스(` ```json `)로 감싸여 있어 동결된
`evaluate.parse_raw_response()`(순수 `json.loads`)로 30/30 파싱 실패 —
`analysis/protocol_strict/` 참조.
