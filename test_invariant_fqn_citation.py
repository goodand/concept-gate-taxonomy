"""불변식 맨 인용 래칫 — 교집합 구간의 새 맨 인용을 막는다 (2026-08-31).

## 무엇을 막나

교집합 구간의 불변식 번호는 **발행자가 셋**이다(등록부 §계열): 권한 경계의
`directive:I1`~`directive:I11` · `mechspec:I`(상태 계약, vault) · `h1a-scope:I`(`qa_v7.py`
검사 항목). 그래서 소유 문서 밖의 맨 표기는 지시 대상이 모호하다 — "Verify 가
어겼다"는 문장이 `directive:I3`(Verify 는 graph 를 쓰지 않는다)인지
`mechspec:I3`(verified-region protection)인지 말할 수 없다.

정본 규약은 `docs/IDENTIFIER_REGISTER.md:25` — 모호한 자리에서는
`directive:I3` 처럼 **문서군 접두**를 콜론으로 붙인다. (회고 §24 의 하이픈
제안 `D-I3` 는 규약 확정 전 표기다 — 정본은 `directive:I3`, SURVEY §11 정정 참조.)

## 왜 래칫인가 — append-only 규약 때문이다

등록부 `:31`: "**과거 인용은 건드리지 않는다.** 이 규약은 새 발행·새 인용부터
적용된다." 그러므로 기존 91건은 고치지 않고 `BASELINE` 으로 동결하며, 게이트는
**증가만** 막는다. 감소하면 baseline 갱신을 강제한다(`test_guard_negative_coverage.py`
의 staleness 검사와 같은 형태) — 그래야 면제 목록이 낡은 채 남지 않는다.

## 왜 필요함이 실측되었나 — 코퍼스가 스스로 자란다

이 게이트를 설계하는 동안 위반 코퍼스가 56→69 로 자랐고, +13 전부가 충돌을
**설명하는** 문서(SURVEY §14)였다. 언급에도 접두를 쓰지 않으면 이 문제에 대해
쓰는 모든 문서가 문제를 키운다. 언급 예외는 두지 않는다 — 메타 논의야말로
"계열이 모호한 자리"이고, 접두를 붙인 언급이 더 명확하다.

## 탐지기는 새로 만들지 않았다

`scripts/identifier_scan.py` 가 출현·종류(발행/인용/위양성)를 이미 가른다.
이 게이트는 그것의 **둘째 소비자**다(첫째는 게이트 범위 실측). 코드/mermaid/
절번호 위양성은 분류기의 `FALSE_POSITIVE_KINDS` 가 걸러 준다.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))

import identifier_scan as sc  # noqa: E402

# 발행처는 자기 계열을 맨 표기해도 된다(등록부 :28 "자기 문서군 안에서는 접두 불요").
OWNER_FILES = frozenset({
    "docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md",  # directive:I
    "docs/H1A_PROBLEM_ANALYSIS.md",                                 # retro:I
    "qa_v7.py",                                                     # h1a-scope:I
})

# 해소는 **토큰 단위**다: 같은 줄에 `<문서군>:<이 토큰>` 이 있어야 그 토큰이
# 해소된다. 처음에는 줄 단위(접두 하나가 줄 전체 면제)였는데 적대적 검증이
# 세탁을 실증했다 — 접두 하나가 같은 줄의 무관한 directive:I4·directive:I5
# 까지 함께 면제했다(재실측 확증, 2026-08-31). 괄호 병기 `directive:I3 (I3)` 는
# 같은 토큰이므로 토큰 단위에서도 해소된다.
FQN_GROUPS = ("directive", "mechspec", "retro", "ev-eval", "h1a-scope")

# 모호 구간 = 발행자가 둘 이상인 번호. 실측(2026-08-31, 적대적 검증이 잡음):
#   1~7  directive · mechspec · h1a-scope(qa_v7)   ← 셋
#   8~9  directive · h1a-scope   ← 둘 (qa_v7 은 h1a-scope:I9 까지 발행한다 —
#        처음 range(1,8) 은 등록부의 낡은 "~mechspec:I7" 기록을 믿었고 둘 다 틀렸다)
#   10~11  directive 뿐                            ← 유일 지시라 맨 표기 허용
AMBIGUOUS_RANGE = range(1, 10)

# 2026-08-31 동결(적대검증 반영 후 재산출: 토큰 단위 해소 + 구간 1~9).
# 등록부 :31 append-only — 과거 인용은 고치지 않는다.
# 증가는 실패, 감소는 "이 표를 줄여라" 실패. 0 이 된 파일은 행을 지운다.
BASELINE: dict[str, int] = {
    "conceptgate/cg_identity.py": 2,
    "conceptgate/cg_ir.py": 1,
    "conceptgate/cg_obligations.py": 4,
    "docs/DESIGN_IMPL_refine_verify_v0.md": 3,
    "docs/IDENTIFIER_REGISTER.md": 22,
    "docs/PROGRESS_REPORT_refine_verify_v0_for_design_agent.md": 9,
    "docs/REFINE_VERIFY_STAGE_SURVEY_20260830.md": 34,
    "docs/feedback/session_retrospective_20260806_h1a_typed_scope.md": 1,
    "experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/OPERATIONS_PLAN.md": 1,
    "experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/PROBLEM_1_sufficient_consistent.md": 4,
    "test_e2e_v0_refine_verify.py": 6,
    "test_identifier_register.py": 2,
    "test_p1_legacy_e2e.py": 2,
}


def bare_citations(root: Path) -> list[sc.Occurrence]:
    """`root` 아래에서 교집합 구간의 맨 인용을 모은다.

    맨 인용 = 인용 종류(CITATION_KINDS)로 분류된 I-토큰이면서, 같은 줄에
    **자기 토큰의** FQN(`<문서군>:<토큰>`)이 없고, 발행처 파일이 아니고,
    번호가 교집합 구간인 것.
    위양성(mermaid 노드·절 번호·파이썬 이름)은 분류기 단계에서 이미 걸러진다.
    """
    out = []
    for o in sc.scan_repo(root).all:
        if o.token[0] != "I" or o.kind not in sc.CITATION_KINDS:
            continue
        if o.path in OWNER_FILES:
            continue
        if any(f"{g}:{o.token}" in o.raw for g in FQN_GROUPS):
            continue
        # int() 방어 코드는 적대적 검증 지적을 **기각**한 자리다: 분류기의
        # IDENT_RE 가 `[A-Z]\d{1,3}` 를 보장하므로 여기서 ValueError 가 난다면
        # 분류기가 자기 계약을 깬 것이고, 그때는 조용히 continue 하는 것보다
        # 시끄럽게 죽는 것이 맞다(조용한 오답이 전임 도구들의 제거 사유였다).
        if int(o.token[1:]) not in AMBIGUOUS_RANGE:
            continue
        out.append(o)
    return out


# ---------------------------------------------------------------------------
# 수집기 자체의 계약 — tmp_path 에서 검증한다 (저장소 상태와 무관)
# ---------------------------------------------------------------------------

def test_collector_detects_a_bare_citation(tmp_path):
    (tmp_path / "a.md").write_text(
        "Verify 는 I3 을 어긴다\n")           # fixture 맨 표기 (directive:I3 로 해소)
    got = bare_citations(tmp_path)
    assert [(o.token, o.path) for o in got] \
        == [("I3", "a.md")]                   # 기대값의 맨 표기 (directive:I3 로 해소)


def test_collector_passes_a_fqn_line(tmp_path):
    """접두가 줄에 있으면 그 줄은 해소된 것이다 — `directive:I3 (I3)` 처럼
    괄호 병기가 흔한 문체라 토큰 단위가 아니라 줄 단위로 본다."""
    (tmp_path / "a.md").write_text("directive:I3 (I3) 을 어긴다\n")
    assert bare_citations(tmp_path) == []


def test_collector_exempts_an_owner_file(tmp_path):
    (tmp_path / "qa_v7.py").write_text(
        "# I1. STRUCTURAL check\n")          # fixture (h1a-scope:I1 발행 흉내)
    assert bare_citations(tmp_path) == []


def test_a_fqn_for_one_token_does_not_wash_its_neighbours(tmp_path):
    """적대적 검증이 실증한 세탁(2026-08-31): 줄 단위 해소에서는 접두 하나가
    같은 줄의 무관한 토큰까지 면제했다. 토큰 단위로 바꾼 뒤 이 계약이 지킨다."""
    (tmp_path / "a.md").write_text(
        "directive:I3 규약에도 불구하고 I4, I5 는 다른 뜻이다\n")  # (directive:I4·directive:I5 해소)
    assert sorted(o.token for o in bare_citations(tmp_path)) \
        == ["I4", "I5"]                       # (directive:I4·directive:I5 해소)


def test_collector_ignores_numbers_outside_the_shared_range(tmp_path):
    """directive 만 발행하는 번호대(10 이상)는 맨 표기도 유일 지시다.
    (h1a-scope:I9 도 발행되므로 9 는 이제 모호 구간이다 — 적대적 검증의 blocker.)"""
    (tmp_path / "a.md").write_text("I10 은 인증 무순환이다\n")
    assert bare_citations(tmp_path) == []
    (tmp_path / "a.md").write_text(
        "I9 는 정규화 세탁 금지다\n")            # fixture 맨 표기 (directive:I9 해소)
    assert [o.token for o in bare_citations(tmp_path)] \
        == ["I9"]                             # 기대값 맨 표기 (directive:I9 해소)


def test_collector_ignores_false_positives(tmp_path):
    (tmp_path / "a.md").write_text("```mermaid\nI3[verified region]\n```\n")
    assert bare_citations(tmp_path) == []


# ---------------------------------------------------------------------------
# 래칫 — 저장소 전체
# ---------------------------------------------------------------------------

def test_no_new_bare_citation_beyond_the_baseline():
    """새 맨 인용은 실패한다. 고치는 법은 접두를 붙이는 것이지 이 표를 늘리는
    것이 아니다 — 표를 늘리는 것은 append-only(과거 동결)가 아니라 규약 포기다."""
    by_file = Counter(o.path for o in bare_citations(HERE))
    over = {f: n for f, n in by_file.items() if n > BASELINE.get(f, 0)}
    if not over:
        return
    detail = []
    for o in bare_citations(HERE):
        if o.path in over:
            detail.append(f"  {o.path}:{o.line}  {o.token}  {o.raw.strip()[:70]}")
    raise AssertionError(
        "동결 시점 이후의 새 맨 인용이다 — 문서군 접두를 붙여라"
        "(정본 규약: docs/IDENTIFIER_REGISTER.md:25, 예: directive:I3):\n"
        + "\n".join(detail[:20]))


def test_the_baseline_is_not_stale():
    """실측이 baseline 보다 줄었으면 baseline 을 그만큼 줄여라. 낡은 면제는
    그 여유분만큼 새 위반을 조용히 통과시킨다 — 게이트가 스스로 무뎌지는 길이다."""
    by_file = Counter(o.path for o in bare_citations(HERE))
    stale = {f: (base, by_file.get(f, 0))
             for f, base in BASELINE.items() if by_file.get(f, 0) < base}
    assert not stale, (
        "BASELINE 이 실측보다 크다 — 표의 수를 실측으로 줄여라(0 이면 행 삭제): "
        + ", ".join(f"{f}: {b}→{n}" for f, (b, n) in sorted(stale.items())))
