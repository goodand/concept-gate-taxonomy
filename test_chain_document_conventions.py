"""판정 사슬 문서의 네 규약 — 산문으로만 있던 것을 기제로 내린다 (P23).

## 왜 이것이 필요한가

이 세션에 나는 **내가 방금 쓴 문서 규약을 네 번 어겼다**(P23):

1. 외부로 나가는 요청서 최상단에 wikilink를 넣어 18개 문서를 손상했고, 규약을
   적은 뒤 **또 한 번** 같은 자리에 넣었다(G113·G124)
2. 사슬 접두어 4종 밖에 `CONFIRMATION_REQUEST_`를 새로 만들어 사용자가 다른
   파일인지 혼동했다(G122)
3. verbatim 해시 필드 형식을 어겨 정본 게이트가 그 문서를 못 읽었다
4. 새 문서를 백틱 경로로만 언급해 backlink 0의 고아로 만들었다

**규약을 아는 것이 규약을 지키게 하지 않는다.** 1~2는 산문으로만 있었고,
3은 이미 기제가 있어서 **잡혔다.** 그 차이가 이 파일의 근거다.

## 실측: 네 규약 모두 현재 위반 0건이다

게이트를 쓰기 전에 전수로 쟀다 — 요청서 wikilink 0 · 접두어 이탈 0 ·
`Q<n>.<n>` 참조 93종 전건 해결 · manifest `text_sha256` 중복 0(8개 파일).
즉 이 게이트는 **현재 상태를 잠그는 것**이고 새 규칙을 만드는 것이 아니다.

## 범위를 잘못 잡아 36건을 오보고할 뻔했다

Q참조 검사를 처음 `docs/DESIGN_DECISION_*.md`만으로 돌렸더니 Q3~Q18이 전부
"미해결"로 나왔다. 그 판정문들은 **실험 폴더**에 있다(H1a 사슬). 판정문은
저장소 전역에 34개 있고, 그중 16개가 `docs/` 밖이다. 그래서 이 검사는
**`rglob`으로 전역을 본다** — 좁은 범위에서 부재를 단정하는 것이 이 세션에
반복된 실패다(P12·P24).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

CHAIN_PREFIXES = ("DESIGN_REQUEST_", "DESIGN_DECISION_",
                  "RESEARCH_REQUEST_", "RESEARCH_RESULT_")
OUTBOUND_PREFIXES = ("DESIGN_REQUEST_", "RESEARCH_REQUEST_")
NAV_MARKER = "저장소 내부 항법"
WIKILINK = re.compile(r"\[\[")
# 끝의 `\b`를 쓰면 안 된다 — 한국어 조사가 붙은 `Q30.7이`에서 "7"과 "이"
# 사이에 단어 경계가 없어 **매치되지 않는다**(파이썬 `re`는 유니코드 문자를
# 단어 문자로 센다). 이 저장소는 조사를 붙여 쓰는 것이 정상이므로 첫 판은
# 검사가 조용히 과소 적용됐고, 음성 시험이 그것을 잡았다. 숫자·점이 더
# 이어지지 않는 것만 확인한다.
QREF = re.compile(r"\bQ\d+\.\d+(?![\d.])")


def _outbound() -> list[Path]:
    return sorted(p for p in DOCS.glob("*.md")
                  if p.name.startswith(OUTBOUND_PREFIXES))


def _all_decision_docs() -> list[Path]:
    """저장소 전역 — `docs/` 밖(실험 폴더)에도 판정문이 있다. 위 docstring 참조."""
    return sorted(p for p in ROOT.rglob("DESIGN_DECISION*.md")
                  if ".git" not in p.parts)


def _manifests() -> list[Path]:
    return sorted((ROOT / "experiments").rglob("stage2_*manifest*.json"))


# ---- ① 외부 요청서: 항법 줄은 본문 끝에 둔다 (G113·G124) ---------------

def test_there_are_outbound_request_docs_to_check():
    assert len(_outbound()) >= 10


@pytest.mark.parametrize("path", _outbound(), ids=lambda p: p.name)
def test_outbound_request_has_no_wikilink_above_the_nav_line(path: Path):
    """판정자는 저장소 접근이 없다 — wikilink는 그에게 무의미하고, 최상단에
    있으면 문서의 첫인상을 잡아먹는다. 실측 근거: 대량 삽입이 18개 문서의
    3행("판정자 전제" 위)을 손상했고, 규약을 적은 뒤 또 한 번 재발했다."""
    lines = path.read_text(encoding="utf-8").splitlines()
    nav = next((i for i, l in enumerate(lines) if NAV_MARKER in l), None)
    head = lines if nav is None else lines[:nav]
    offenders = [i + 1 for i, l in enumerate(head) if WIKILINK.search(l)]
    assert not offenders, (
        f"{path.name}: 항법 줄 앞 {offenders}행에 wikilink가 있다. "
        f"외부로 나가는 문서는 항법을 본문 끝('{NAV_MARKER}' 블록)에 둔다")


# ---- ② 사슬 접두어는 넷뿐이다 (G122) ----------------------------------

def test_no_new_chain_prefix_was_invented():
    """규모가 작아도 접두어를 바꾸지 않는다. 실측: 문항 1개짜리 확인을
    `CONFIRMATION_REQUEST_`로 만들었더니 사용자가 다른 파일인지 헷갈렸다.
    작은 상신은 접두어를 유지하고 **번호로 구별**한다(Q32의 후속 = Q32-C)."""
    suspicious = [p.name for p in DOCS.glob("*.md")
                  if re.search(r"_(REQUEST|DECISION|RESULT)_", p.name)
                  and not p.name.startswith(CHAIN_PREFIXES)]
    assert not suspicious, (
        f"사슬 접두어 4종 밖의 파일: {suspicious}. 사람도 zero-context agent도 "
        "그것이 무엇이고 사슬의 어디인지 알 수 없다")


# ---- ③ Q<n>.<n> 참조는 어느 판정문에서든 해결돼야 한다 (P4) ------------

def test_every_q_reference_resolves_to_some_decision():
    """발명된 하위 문항 번호를 잡는다. 인용한 번호가 어느 판정문에도 없으면
    그 인용은 근거가 아니다."""
    decisions = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                          for p in _all_decision_docs())
    refs = set()
    for p in ROOT.rglob("*.md"):
        if ".git" in p.parts:
            continue
        refs |= set(QREF.findall(p.read_text(encoding="utf-8", errors="replace")))
    assert len(refs) >= 50, "참조가 너무 적다 — 이 검사가 공허해졌는지 확인하라"
    dangling = sorted(q for q in refs if q not in decisions)
    assert not dangling, (
        f"어느 판정문에도 없는 Q참조: {dangling}. 판정문은 `docs/` 밖 실험 "
        "폴더에도 있으므로 전역을 본다(이 파일 docstring 참조)")


def test_the_q_reference_scope_includes_non_docs_decisions():
    """범위 오류 재발 방지 — 실험 폴더의 판정문이 실제로 포함되는가."""
    outside = [p for p in _all_decision_docs() if p.parent != DOCS]
    assert outside, "docs/ 밖 판정문이 0건이면 범위 확장이 무의미해졌다"


# ---- ④ manifest의 text_sha256은 유일하다 (E4 428건) --------------------

def test_there_are_manifests_to_check():
    assert len(_manifests()) >= 4


@pytest.mark.parametrize("path", _manifests(), ids=lambda p: p.name)
def test_manifest_text_hashes_are_unique(path: Path):
    """같은 문장이 두 fixture로 들어가면 시행이 독립이 아니다 — E4가 428건을
    바이트 동일 중복으로 배제한 것과 같은 근거다."""
    data = json.loads(path.read_text(encoding="utf-8"))
    seen: dict[str, str] = {}
    dups = []
    for block in ("entries", "folio_simple_controls", "pmb_projection_controls"):
        for e in data.get(block, []):
            h = e.get("text_sha256")
            if h is None:
                continue
            if h in seen:
                dups.append((seen[h], e.get("case_id"), h[:12]))
            else:
                seen[h] = e.get("case_id", "?")
    assert not dups, f"{path.name}: text_sha256 중복 {dups}"
