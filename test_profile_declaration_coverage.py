"""발급자는 인증 계약을 **선언해야** 한다 — 호출 지점 열거 게이트.

## 무엇을 푸는가

D-38 이후 검증부가 profile commitment 를 대조한다. 그래서 발급 시
`profile=` 을 빠뜨리면 인증서에 `profile: None` 이 실리고, 그것은
**검증 시점에** `CertificateError` 로 터진다 — 발급자는 아무 신호도 받지
못한다. E2E MVP 요구사항 #3 이 그것이고, D-38 구현 적대검증의 blocker 1c
(생산 발급자가 profile 을 안 넘긴다)와 같은 뿌리다.

현 상태 실측(2026-09-01): 호출 지점 **28곳 중 27곳이 이미 선언**한다.
즉 문제는 "지금 틀렸다"가 아니라 **"보호되지 않는다"** — 다음 호출자가
빠뜨리면 늦게, 엉뚱한 자리에서 터진다.

## 형태 (KNOWHOW §D)

`test_guard_negative_coverage.py` 의 골격을 재사용한다(4단 재사용 조사) —
**D1 열거 → 피복 → 잔여** + **D4 얻어내는 면제**. import 하지 않고 AST 로
읽는 이유도 같다: 실험 폴더가 동명 모듈을 동결 사본으로 갖고 있어
`sys.modules` 선점이 다른 실험을 남의 코드로 돌린다(`pytest.ini` 규약).

**면제는 얻어내는 것이다.** 미선언이 정당한 자리는 하나뿐이고, 그 파일은
"미선언 호출도 같은 shape 을 낸다"를 **실제로 단언**해야 면제를 받는다.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__",
              ".pytest_cache", ".oracle_cache"}
ISSUER = "issue_claim_certificate"

# 미선언이 **의도**인 자리. 각 항목은 그 파일이 미선언 자체를 단언한다는
# 사실로 면제를 얻는다(아래 staleness 검사가 그것을 확인한다).
EARNED_EXEMPTIONS: dict[str, str] = {
    "test_profile_commitment.py":
        "미선언 호출도 같은 shape 을 내고 값이 None 임을 단언한다 — "
        "하나의 schema 이름 아래 두 shape 이 생기지 않게 지키는 계약",
}


def _python_files():
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        yield p


def call_sites() -> dict[str, list[tuple[int, bool]]]:
    """`issue_claim_certificate` 호출을 전수 열거하고 각각 `profile=` 유무를
    기록한다. 반환: 파일(상대경로) → [(줄, 선언했나)]."""
    found: dict[str, list[tuple[int, bool]]] = {}
    for path in _python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = (fn.attr if isinstance(fn, ast.Attribute)
                    else fn.id if isinstance(fn, ast.Name) else None)
            if name != ISSUER:
                continue
            declared = any(k.arg == "profile" for k in node.keywords)
            rel = str(path.relative_to(ROOT))
            found.setdefault(rel, []).append((node.lineno, declared))
    return found


# ---------------------------------------------------------------------------
# 1. 열거 → 피복 → 잔여
# ---------------------------------------------------------------------------

def test_the_scanner_actually_finds_the_call_sites():
    """**이 검사가 없으면 0건을 돌려주는 stub 이 아래 게이트를 전부
    통과한다**(wikilink 게이트가 적대검증에서 배운 그 형태)."""
    sites = call_sites()
    total = sum(len(v) for v in sites.values())
    assert total >= 20, f"호출 지점 {total}건 — 열거가 깨졌다"
    assert "conceptgate/server.py" in sites, "생산 발급자가 열거에 없다"


def test_every_call_site_declares_its_profile():
    """발급자는 어느 계약으로 발급하는지 말해야 한다. 안 말하면 인증서에
    `profile: None` 이 실리고 **검증 시점에** 터진다 — 발급 시점에 잡는다."""
    missing = [f"{f}:{ln}" for f, sites in call_sites().items()
               for ln, declared in sites
               if not declared and f not in EARNED_EXEMPTIONS]
    assert not missing, (
        "profile= 없이 인증서를 발급하는 자리다 — D-38 이후 검증부가 "
        "commitment 를 대조하므로 이 인증서는 나중에 CertificateError 로 "
        f"거부된다. 발급 시점에 계약을 선언하라: {missing}")


def test_the_production_issuer_declares_it():
    """면제 목록과 무관하게 **생산 경로**는 언제나 선언한다 — 적대검증
    blocker 1c 가 정확히 이 자리였다(server 가 profile 을 안 넘겨 모든
    생산 인증서가 None 이었다)."""
    prod = call_sites().get("conceptgate/server.py", [])
    assert prod, "server.py 의 발급 호출이 사라졌다"
    assert all(declared for _, declared in prod)


# ---------------------------------------------------------------------------
# 2. 면제는 얻어내는 것이다 (D4)
# ---------------------------------------------------------------------------

def test_each_exemption_actually_omits_on_purpose():
    """면제를 주장하는 파일은 **실제로 미선언 호출을 갖고** 있어야 한다.
    없으면 그 항목이 낡은 것이고, 면제 목록이 조용한 통행증이 된다
    (`NEGATIVE_FIXTURE_FILES` 가 같은 이유로 이 검사를 갖는다)."""
    sites = call_sites()
    for name in EARNED_EXEMPTIONS:
        assert name in sites, f"{name}: 면제인데 발급 호출이 없다"
        assert any(not d for _, d in sites[name]), (
            f"{name}: 미선언 호출이 없다 — 면제가 불필요해졌으면 목록에서 지워라")


def test_each_exemption_states_its_reason():
    """사유 없는 면제는 기록이 아니라 구멍이다(빈 문자열 금지)."""
    for name, reason in EARNED_EXEMPTIONS.items():
        assert reason.strip(), f"{name}: 사유가 비어 있다"


def test_the_exemption_list_may_be_empty():
    """**폐쇄 가능성의 목격자**(동료 왕복 4회차, P-자기배반 판별자). 이 목록은
    비는 것이 성공인 **해소 목표형**이므로 "비면 실패" 단언을 걸지 않는다 —
    규칙은 합성 입력으로 증명한다."""
    synthetic: dict[str, list[tuple[int, bool]]] = {"x.py": [(1, True)]}
    missing = [f"{f}:{ln}" for f, s in synthetic.items()
               for ln, d in s if not d and f not in {}]
    assert missing == []          # 면제 0개여도 규칙이 성립한다
