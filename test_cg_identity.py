"""cg_identity 검증 — 결정성·도메인 분리·§29 부정 계약(AST 집행)."""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_identity as ci


def test_canonical_bytes_is_key_order_invariant():
    a = {"b": 1, "a": {"y": 2, "x": [3, 1]}}
    b = {"a": {"x": [3, 1], "y": 2}, "b": 1}
    assert ci.canonical_bytes(a) == ci.canonical_bytes(b)


def test_canonical_bytes_is_value_order_sensitive():
    """리스트 순서는 의미다 — 정규화가 지우면 안 된다(§8: deterministic
    ordering은 노드/인자 수준이지 임의 재배열이 아니다)."""
    assert ci.canonical_bytes({"a": [1, 2]}) != ci.canonical_bytes({"a": [2, 1]})


def test_canonical_sha256_none_passthrough():
    assert ci.canonical_sha256(None) is None
    assert ci.canonical_sha256({}) is not None


def test_one_character_change_changes_the_hash():
    base = {"text": "forall x exists y R(x,y)"}
    edit = {"text": "forall x exists y R(y,x)"}
    assert ci.canonical_sha256(base) != ci.canonical_sha256(edit)


def test_fingerprint_kinds_are_domain_separated():
    """같은 내용, 다른 kind → 다른 fingerprint. node가 claim으로 검증되는
    대체 가능성을 구조적으로 차단(_receipt.sign의 domain과 같은 이유)."""
    doc = {"id": "c17"}
    prints = {ci.node_fingerprint(doc), ci.claim_fingerprint(doc),
              ci.graph_fingerprint(doc), ci.obligation_target_fingerprint(doc)}
    assert len(prints) == 4
    for p in prints:
        kind, _, digest = p.partition(":")
        assert kind in ci._FINGERPRINT_KINDS and len(digest) == 64


def test_free_form_fingerprint_kind_is_refused():
    with pytest.raises(ValueError, match="unknown fingerprint kind"):
        ci.fingerprint("verdict", {"id": "c17"})


def test_the_guard_itself_fires_when_called_directly():
    """뮤테이션 게이트가 요구하는 직접 호출. `fingerprint()`를 거쳐서만
    검증하면, `fingerprint()`가 미래에 `_assert_known_fingerprint_kind`
    호출을 빼먹어도 이 테스트가 여전히 fingerprint() 자체의 다른 경로에서
    우연히 통과할 수 있다 — 가드를 직접 겨눈다."""
    with pytest.raises(ValueError, match="unknown fingerprint kind"):
        ci._assert_known_fingerprint_kind("verdict")


def test_unicode_is_stable():
    assert ci.canonical_sha256({"k": "칼의 재료는 철"}) == ci.canonical_sha256(
        {"k": "칼의 재료는 철"})


# ------------------------------------------------------- §29 negative -----

FORBIDDEN_NAME_PARTS = (
    "select", "choose", "judge", "certif", "repair", "infer",
    "entail", "verdict", "score", "support", "oracle",
)


def test_kernel_module_defines_no_judgment_functions():
    """§29 negative contract, AST로 집행. 이 테스트가 실패하면 Kernel이
    semantic judge로 팽창하기 시작한 것이다 — 함수를 Verify쪽으로 옮겨라."""
    tree = ast.parse(Path(inspect.getfile(ci)).read_text(encoding="utf-8"))
    offenders = [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and any(part in node.name.lower() for part in FORBIDDEN_NAME_PARTS)
    ]
    assert not offenders, f"§29 위반 후보: {offenders}"


def test_kernel_module_imports_no_judgment_modules():
    """cg_identity는 잎이다 — cg_obligations(판정 계층)를 import하는 순간
    표현과 판단의 경계가 무너진다."""
    tree = ast.parse(Path(inspect.getfile(ci)).read_text(encoding="utf-8"))
    imported = {
        name.name for node in ast.walk(tree)
        if isinstance(node, ast.Import) for name in node.names
    } | {
        node.module for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    # W5 수정으로 서명 primitive가 이식되며 hmac/os/secrets/pathlib 추가 —
    # 전부 stdlib이고 판정 모듈은 여전히 금지.
    assert imported <= {"hashlib", "json", "hmac", "os", "secrets",
                        "pathlib", "__future__"}, imported
