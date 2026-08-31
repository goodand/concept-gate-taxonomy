#!/usr/bin/env python3
"""Discard adversarial-review findings whose cited evidence does not exist.

Why this exists (measured, not hypothetical)
---------------------------------------------
2026-08-24, Q33 상신서 적대검증: a finding reported "표 첫 행 case ID가
`PMB-p02-d2298` 오타" — the target document contains zero occurrences of
`p02`; the real string is `PMB-p00-d2298`. The finding's `evidence` field
quoted a citation that simply does not exist in the document it claimed to
quote. One `rg -c p02` refuted it, but only because a human happened to
re-verify; unverified, the correct document would have been "fixed" to match
a hallucination. The `adversarial-review` skill already states the rule this
gate mechanizes: "a finding without evidence is discarded immediately." This
script is that rule turned into a check that runs every time, not a new
policy.

What this gate does and does not do
------------------------------------
DOES: extract backtick- and quote-delimited citations from a finding's
`claim`/`evidence`/`note` fields and confirm each one actually occurs (under
a whitespace/ANSI/smart-quote-normalized comparison) in the target
documents. A finding citing a string absent from every target is
`EVIDENCE_NOT_FOUND` and gets discarded.

DOES NOT judge whether a finding is *correct*. A citation can be real and
the interpretation built on it can still be wrong: the same day, a D-33
검증설계 적대검증 blocker turned out to be a misreading that confused
판정문 §8 with §10 — the quoted text existed verbatim in both places, so no
citation check catches that class of error. Findings with zero citations are
therefore not discarded either (`NOT_CHECKABLE`, not `EVIDENCE_NOT_FOUND`) —
absence of a citation is not evidence of a false claim, and a lead still has
to read it.

Why short citations are never checked: this instrument mis-fired four times
in one session, every time on a plausible-looking short token that turned
out to be an ordinary word rather than a real quotation. A gate that cries
wolf gets ignored, so anything under `MIN_CITATION` characters is left
`NOT_CHECKABLE` instead of risking a false `EVIDENCE_NOT_FOUND`.

Stdlib only, per this repo's convention for tooling that must run anywhere.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

VERDICTS = ("CITATION_FOUND", "EVIDENCE_NOT_FOUND", "NOT_CHECKABLE")
MIN_CITATION = 6  # below this, a "citation" is more likely an ordinary word

_FIELDS = ("claim", "evidence", "note")

# One alternation, tried left-to-right at each position: backtick first (also
# spans newlines, for multi-line backtick blocks), then straight and smart
# quote pairs. Each alternative captures its own group; exactly one group is
# non-None per match.
_CITATION_RE = re.compile(
    r"`(.+?)`"
    r'|"(.+?)"'
    r"|'(.+?)'"
    r"|“(.+?)”"
    r"|‘(.+?)’",
    re.DOTALL,
)

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# 정적 파일에 있을 수 **없는** 인용 부류. 이것들을 EVIDENCE_NOT_FOUND 로 내면
# 도구가 늑대 소년이 된다 — 2026-08-31 실측: 스키마 강제 위임의 회신 12건 중
# 11건이 폐기됐고 폐기 사유 인용 37건을 전수 분류하니 아래 부류가 대부분이었다.
# 판별기는 **좁게** 만든다: 넓히면 환각한 파일 인용이 이 문으로 빠져나간다
# (G134 회귀 계약이 그것을 지킨다).
_UNCHECKABLE_KINDS = (
    # 예외·트레이스백: `TypeError: ...` `AttributeError: ...`
    ("execution_output", re.compile(r"^\s*\w*(?:Error|Exception|Warning):\s")),
    # REPL/실행 출력의 화살표 표기: `... -> pass` `... → UNKNOWN`
    ("execution_output", re.compile(r"(?:->|→)\s*\S")),
    # 셸 명령: 실행한 것이지 파일 내용이 아니다
    ("shell_command", re.compile(r"^\s*(?:grep|rg|git|python3?|pytest|find|sed)\s")),
    # 생략부호로 축약된 것은 **구성상** verbatim 인용이 아니다
    ("elided_paraphrase", re.compile(r"\.\.\.|…")),
)


def uncheckable_kind(citation: str) -> str | None:
    """이 인용이 정적 파일 대조로 판정할 수 **없는** 부류인가.

    반환값은 부류 이름 또는 None. 부류가 있으면 호출자는 그 인용을
    `EVIDENCE_NOT_FOUND` 의 근거로 쓰지 않는다 — "파일에 없다"가 참이지만
    그것이 finding 의 참·거짓과 무관하기 때문이다.
    """
    for kind, pattern in _UNCHECKABLE_KINDS:
        if pattern.search(citation):
            return kind
    return None


class AllTargetsUnreadable(Exception):
    """Raised by check() when every target failed to read.

    Reporting "not found" for a citation we never actually looked for is an
    absence claim we cannot back up, and this repo has been burned by exactly
    that failure mode before. So this is a hard error, not a NOT_CHECKABLE.
    """


def _normalize(s: str) -> str:
    """Strip ANSI escapes, collapse whitespace, fold smart quotes to ASCII.

    Case is deliberately preserved — identifiers and synsets in this repo
    (e.g. `male.n.02` vs a differently-cased token) mean different things.
    """
    s = _ANSI_RE.sub("", s)
    s = s.replace("“", '"').replace("”", '"')
    s = s.replace("‘", "'").replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    return s


def citations(finding: dict) -> list[str]:
    """Extract citation strings from a finding's claim/evidence/note fields.

    Backtick-delimited and quote-delimited (straight and smart, single and
    double) substrings count as citations. Anything shorter than
    MIN_CITATION is dropped. Duplicates are removed; first-appearance order
    is kept, scanning claim, then evidence, then note.
    """
    seen: dict[str, None] = {}
    for field in _FIELDS:
        text = finding.get(field)
        if not text:
            continue
        for match in _CITATION_RE.finditer(text):
            content = next(g for g in match.groups() if g is not None)
            if len(content) < MIN_CITATION:
                continue
            seen.setdefault(content, None)
    return list(seen)


def check(finding: dict, targets: list[Path]) -> dict:
    """Verify a finding's citations actually occur in one of the targets."""
    all_cites = citations(finding)
    # 정적 대조가 불가능한 부류는 검사 대상에서 뺀다(폐기 근거로 쓰지 않는다).
    unckd = {c: k for c in all_cites if (k := uncheckable_kind(c))}
    cites = [c for c in all_cites if c not in unckd]
    result = {"id": finding.get("id"), "citations": cites, "missing": [],
              "uncheckable": unckd}

    if not cites:
        # 검사 가능한 인용이 하나도 없다 — 부재의 증명이 아니라 미확인이다.
        result["verdict"] = "NOT_CHECKABLE"
        return result

    normalized_targets = []
    read_failures = 0
    for target in targets:
        try:
            text = Path(target).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            read_failures += 1
            continue
        normalized_targets.append(_normalize(text))

    if targets and read_failures == len(targets):
        raise AllTargetsUnreadable(
            f"all {len(targets)} target(s) failed to read; cannot report "
            "EVIDENCE_NOT_FOUND without having looked"
        )

    missing = [
        c for c in cites
        if not any(_normalize(c) in nt for nt in normalized_targets)
    ]

    if missing:
        result["verdict"] = "EVIDENCE_NOT_FOUND"
        result["missing"] = missing
    else:
        result["verdict"] = "CITATION_FOUND"
    return result


def partition(findings: list[dict], targets: list[Path]) -> dict:
    """Split findings into kept/discarded by citation verdict.

    discarded = EVIDENCE_NOT_FOUND only. kept = CITATION_FOUND +
    NOT_CHECKABLE (no citation is not the same as a false claim). counts
    must sum to len(findings) — silently dropping a row here would be a
    silent pass exactly like the failure mode this gate exists to catch.
    """
    kept = []
    discarded = []
    counts: dict[str, int] = {}
    for finding in findings:
        verdict = check(finding, targets)["verdict"]
        counts[verdict] = counts.get(verdict, 0) + 1
        (discarded if verdict == "EVIDENCE_NOT_FOUND" else kept).append(finding)
    return {"kept": kept, "discarded": discarded, "counts": counts}


def is_grounded(finding: dict, targets: list[Path]) -> bool:
    """이 finding 이 **확인된 인용에 근거하는가** — `kept` 와 다른 질문이다.

    `partition` 의 `kept` 는 "폐기되지 않았다"이고 `NOT_CHECKABLE` 을 포함한다.
    그것을 성공으로 읽으면 안 된다 — 이 저장소의 3값 어휘에서 그것은 `BLOCKED`
    이고, `CLAUDE.md` 가 "BLOCKED 는 exit code 에 반영되지 않으므로 판정 보류이지
    자동 허용이 아니다"라고 못박은 바로 그 자리다.

    **재생성 루프를 붙일 때 이 함수가 수락 기준이어야 한다** (2026-08-31 실측).
    "폐기 안 됨"을 기준으로 재시도를 돌리면 생성자는 **인용을 검사 불가 부류로
    포장하도록 보상받는다** — 같은 환각 심볼을 트레이스백·화살표 출력·셸 명령·
    생략부호 넷으로 위장하니 전부 `NOT_CHECKABLE` 이었다(부류 판별기가 통째로
    도피구가 된다). 그러면 환각 탐지기가 환각 세탁기로 바뀐다.

    스키마 미충족 재생성(형태 층)은 도구가 이미 한다. 이것은 **의미 층**의
    수락 기준이고, 루프에는 `mechspec:I6`(explicit retry limit)과 abstention 이
    함께 와야 한다 — 수렴은 보장되지 않는다.

    **건전성의 범위 — 이름이 오해를 부르므로 못박는다.** 이 함수가 건전한
    대상은 "**이 문자열이 이 파일에 있다**"이고, "**이 finding 이 참이다**"가
    아니다. 실측(2026-08-31): `return a + b` 를 정확히 인용하면서 "두 인자를
    곱한다 — 곱셈 버그"라고 주장하는 finding 이 `CITATION_FOUND` ·
    `is_grounded=True` 로 통과한다. 해석은 규칙이 결정하지 못한다.

    그래서 재생성 루프의 수락 기준으로 이것을 쓸 때 얻는 것은 **"인용이
    실재한다"까지**다. finding 자체를 규칙으로 건전하게 수락하려면 명제를 더
    좁혀 **실행 가능한 것**으로 만들어야 한다(입력 → 관측된 판정). 오늘 채택한
    지적은 전부 그 형태의 probe 로 갈렸고, 인용 검사로 갈린 것은 하나도 없다.
    """
    return check(finding, targets)["verdict"] == "CITATION_FOUND"


def _load_findings(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("findings", [])
    return data


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "usage: verify_finding_citations.py <findings.json> <target> [target...]",
            file=sys.stderr,
        )
        return 2

    findings = _load_findings(Path(argv[0]))
    targets = [Path(p) for p in argv[1:]]

    result = partition(findings, targets)

    for verdict in VERDICTS:
        n = result["counts"].get(verdict, 0)
        print(f"{verdict}: {n}")

    for finding in result["discarded"]:
        check_result = check(finding, targets)
        print(f"  DISCARDED id={finding.get('id')} missing={check_result['missing']}")

    # 판단불가는 삼키지 않고 **그대로 낸다**. 규칙이 결정하지 못한 것을 조용히
    # 통과시키면 그것이 이 도구가 막으려는 실패 모드 자체다 — `BLOCKED` 는
    # 자동 허용이 아니고(`CLAUDE.md` 3값 어휘), 사람에게 보이거나 생성자에게
    # 되먹여지는 것이 그 종단 상태다.
    ungrounded = []
    for finding in result["kept"]:
        r = check(finding, targets)
        if r["verdict"] == "NOT_CHECKABLE":
            kinds = sorted(set(r["uncheckable"].values())) or ["no_citation"]
            print(f"  UNDECIDED  id={finding.get('id')} 사유={kinds} "
                  f"— 규칙으로 판정 못 함. 사람이 읽거나 생성자에게 되먹여라")
            ungrounded.append(finding.get("id"))
    if ungrounded:
        print(f"판정 보류 {len(ungrounded)}건 (id={ungrounded}) — 수락 아님. "
              f"수락 기준은 is_grounded(≥1 CITATION_FOUND) 다")

    return 1 if result["discarded"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
