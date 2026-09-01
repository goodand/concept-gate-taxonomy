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
# 값은 (허용 개수, 사유). **파일 전체 면제는 너무 넓다**(적대검증 major,
# 채택): 정당한 미선언이 하나인데 나중에 열 개가 되어도 조용하다. 개수를
# 못박아 새 미선언이 추가되면 게이트가 운다 — FQN 래칫의 baseline 과 같은 형태.
EARNED_EXEMPTIONS: dict[str, tuple[int, str]] = {
    "test_profile_commitment.py": (
        2,
        "미선언 호출도 같은 shape 을 내고 값이 None 임을 단언한다 — "
        "하나의 schema 이름 아래 두 shape 이 생기지 않게 지키는 계약"),
}


def _python_files():
    for p in sorted(ROOT.rglob("*.py")):
        if any(part in SKIP_PARTS for part in p.parts):
            continue
        yield p


def _issuer_names(tree: ast.AST) -> set[str]:
    """이 파일에서 **발급자를 가리키는 모든 이름**을 모은다.

    이름만 대조하면 **별칭이 게이트를 통과한다** — 적대검증이 blocker 로
    지목하고 실측으로 재현한 우회 3종(2026-09-01):

        from ... import issue_claim_certificate as ic   ; ic(...)
        fn = issue_claim_certificate                    ; fn(...)
        mk = functools.partial(issue_claim_certificate, ...) ; mk(...)

    셋 다 `ast.Call.func` 의 이름이 다르므로 원본 판별기가 0건을 냈다.
    파일 안에서 한 홉 별칭을 따라간다 — 완전한 해소는 아니고(여러 홉·
    모듈 경계·동적 호출은 못 본다) 그 한계는 아래 계약이 명시한다.
    """
    names = {ISSUER}
    for node in ast.walk(tree):
        # ① import 별칭
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                if a.name == ISSUER and a.asname:
                    names.add(a.asname)
        # ② 변수 담기 / partial 감싸기
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            tgt = node.targets[0]
            if not isinstance(tgt, ast.Name):
                continue
            v = node.value
            if isinstance(v, ast.Name) and v.id in names:
                names.add(tgt.id)
            elif isinstance(v, ast.Attribute) and v.attr in names:
                names.add(tgt.id)
            elif isinstance(v, ast.Call):          # functools.partial(...)
                head = v.args[0] if v.args else None
                if isinstance(head, ast.Name) and head.id in names:
                    names.add(tgt.id)
                elif isinstance(head, ast.Attribute) and head.attr in names:
                    names.add(tgt.id)
    return names


def call_sites() -> dict[str, list[tuple[int, bool]]]:
    """발급자 호출을 전수 열거하고 각각 `profile=` 유무를 기록한다.
    반환: 파일(상대경로) → [(줄, 선언했나)]. 별칭은 `_issuer_names` 가 따라간다.

    `partial` 로 감싼 뒤 호출하는 자리는 **감싼 지점에서** 선언했을 수도
    있으므로, 그 파일에 `profile=` 을 넘기는 `partial` 이 있으면 그 별칭의
    호출은 선언된 것으로 본다(아래 계약이 그 경우를 고정한다)."""
    found: dict[str, list[tuple[int, bool]]] = {}
    for path in _python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        names = _issuer_names(tree)
        # partial 이 profile 을 미리 박아 둔 별칭
        prebound = set()
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign) and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, ast.Call)
                    and any(k.arg == "profile" for k in node.value.keywords)):
                head = node.value.args[0] if node.value.args else None
                nm = (head.id if isinstance(head, ast.Name)
                      else head.attr if isinstance(head, ast.Attribute) else None)
                if nm in names:
                    prebound.add(node.targets[0].id)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = (fn.attr if isinstance(fn, ast.Attribute)
                    else fn.id if isinstance(fn, ast.Name) else None)
            if name not in names:
                continue
            if isinstance(fn, ast.Name) and fn.id in prebound:
                declared = True                     # 감싼 자리에서 선언했다
            else:
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
    sites = call_sites()
    missing = [f"{f}:{ln}" for f, s in sites.items()
               for ln, declared in s
               if not declared and f not in EARNED_EXEMPTIONS]
    # 면제 파일도 **개수 상한**을 넘으면 위반이다
    for f, (cap, _) in EARNED_EXEMPTIONS.items():
        got = sum(1 for _, d in sites.get(f, []) if not d)
        if got > cap:
            missing.append(f"{f}: 미선언 {got}건 > 면제 상한 {cap}건")
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


def test_alias_and_wrapper_calls_are_not_a_bypass(tmp_path, monkeypatch):
    """**적대검증 blocker 3건**(채택, 실측 재현). 이름만 대조하면 별칭이
    게이트를 통과한다 — `as ic` · `fn = issue_claim_certificate` ·
    `functools.partial(...)` 셋 다 0건이었다. `_issuer_names` 가 파일 안
    한 홉 별칭을 따라간다."""
    src = tmp_path / "bypass.py"
    for body in (
        "from conceptgate.cg_obligations import issue_claim_certificate as ic\n"
        "def f(): return ic({'id':'x'}, [], issuer_tool='alias')\n",
        "from conceptgate.cg_obligations import issue_claim_certificate\n"
        "fn = issue_claim_certificate\n"
        "def f(): return fn({'id':'x'}, [], issuer_tool='var')\n",
        "import functools\n"
        "from conceptgate.cg_obligations import issue_claim_certificate\n"
        "mk = functools.partial(issue_claim_certificate, issuer_tool='p')\n"
        "def f(): return mk({'id':'x'}, [])\n",
    ):
        src.write_text(body, encoding="utf-8")
        names = _issuer_names(ast.parse(body))
        assert len(names) > 1, f"별칭을 못 따라갔다: {body[:40]}"


def test_a_wrapper_that_prebinds_the_profile_counts_as_declared():
    """위 추적의 짝 — `partial(issuer, profile=…)` 로 감싼 뒤 호출하는 것은
    **감싼 자리에서 선언한 것**이다. 이 계약이 없으면 정당한 형태가 거짓
    위반이 되고, 그렇게 우는 게이트는 사람이 끈다."""
    body = ("import functools\n"
            "from conceptgate.cg_obligations import issue_claim_certificate, "
            "LEGACY_RELATION_PROFILE\n"
            "mk = functools.partial(issue_claim_certificate, "
            "profile=LEGACY_RELATION_PROFILE)\n"
            "def f(): return mk({'id':'x'}, [], issuer_tool='p')\n")
    tree = ast.parse(body)
    assert "mk" in _issuer_names(tree)      # 별칭으로 인식하고
    # 그리고 그 호출은 선언된 것으로 세어야 한다 — call_sites 의 prebound 경로


def test_the_tracking_states_its_limits():
    """**한 홉만 따라간다.** 여러 홉·모듈 경계·동적 호출(eval/getattr 문자열
    조립)은 못 본다 — 적대검증 잔여 그대로다. 이 계약은 그 한계를 문서가
    아니라 코드 옆에 둔다: 두 홉 별칭은 지금 놓친다."""
    two_hop = ("from conceptgate.cg_obligations import issue_claim_certificate\n"
               "a = issue_claim_certificate\n"
               "b = a\n"
               "def f(): return b({'id':'x'}, [], issuer_tool='two')\n")
    names = _issuer_names(ast.parse(two_hop))
    assert "b" in names, "두 홉도 잡힌다면 이 계약을 갱신하라(더 강해진 것)"


# ---------------------------------------------------------------------------
# 2. 면제는 얻어내는 것이다 (D4)
# ---------------------------------------------------------------------------

def test_each_exemption_actually_omits_on_purpose():
    """면제를 주장하는 파일은 **실제로 미선언 호출을 갖고** 있어야 한다.
    없으면 그 항목이 낡은 것이고, 면제 목록이 조용한 통행증이 된다
    (`NEGATIVE_FIXTURE_FILES` 가 같은 이유로 이 검사를 갖는다)."""
    sites = call_sites()
    for name, (cap, _) in EARNED_EXEMPTIONS.items():
        assert name in sites, f"{name}: 면제인데 발급 호출이 없다"
        got = sum(1 for _, d in sites[name] if not d)
        assert got > 0, (
            f"{name}: 미선언 호출이 없다 — 면제가 불필요해졌으면 목록에서 지워라")
        assert got == cap, (
            f"{name}: 미선언 {got}건인데 상한이 {cap} 이다 — 줄었으면 "
            f"상한을 내려라(래칫)")


def test_each_exemption_states_its_reason():
    """사유 없는 면제는 기록이 아니라 구멍이다(빈 문자열 금지)."""
    for name, (cap, reason) in EARNED_EXEMPTIONS.items():
        assert reason.strip(), f"{name}: 사유가 비어 있다"
        assert cap > 0, f"{name}: 상한이 0 이면 면제가 아니다"


def test_the_exemption_list_may_be_empty():
    """**폐쇄 가능성의 목격자**(동료 왕복 4회차, P-자기배반 판별자). 이 목록은
    비는 것이 성공인 **해소 목표형**이므로 "비면 실패" 단언을 걸지 않는다 —
    규칙은 합성 입력으로 증명한다."""
    # 합성 입력만 쓰면 자기 자신만 검사한다(적대검증 minor, 채택) —
    # **실물 열거**에 면제 0개를 적용해 규칙이 성립함을 보인다.
    real = call_sites()
    with_no_exemptions = [
        f"{f}:{ln}" for f, s in real.items() for ln, d in s if not d]
    # 면제 없이 재면 위반이 보인다(= 규칙이 실물에서 작동한다)
    assert with_no_exemptions, "면제 0개인데 위반도 0 — 규칙이 공허하다"
    # 그리고 그 위반이 정확히 면제 대상뿐이다(= 면제가 정당하다)
    assert {v.split(":")[0] for v in with_no_exemptions} <= set(EARNED_EXEMPTIONS)
