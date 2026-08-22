#!/usr/bin/env python3
"""cg_identity — Shared Semantic Kernel의 표현 primitive (잎 모듈, 의존 0).

Refine/Verify 지시(§3.1 AFTER, §7)의 Stable Identity / Canonical
Serialization 층이다. gap 분석 D2의 구현.

REUSED, NOT HAND-WRITTEN
------------------------
`canonical_bytes`와 `canonical_sha256`(구 `receipt_sha256`)은
`codex/mcp-provider-isolation` 브랜치의
`experiments/2026-08-07_handoff_dynamic_controller/_receipt.py`(커밋
`193d9a0` 계열)에서 **본문 그대로** 가져왔다. 그 모듈이 잎(의존 0)으로
설계된 이유 — adjudicator가 개발용 모듈을 전이 의존하게 만드는 계층 역전을
막는다, import 비용 실측 근거 포함 — 가 여기에도 그대로 적용된다.
그 브랜치가 이 브랜치에 없어 in-repo drift 핀은 불가능하다. 브랜치 합류 시
`inspect.getsource` 핀을 추가할 것 (survey §4의 3버전 분기 재발 방지).

NEGATIVE CONTRACT (지시 §29 — 이 모듈이 절대 하지 않는 것)
----------------------------------------------------------
판단을 제공하지 않는다: select/choose/judge/certify/repair/infer/score 류
함수를 이 모듈에 추가하지 마라. fingerprint가 같다는 것은 **정규화된 표현이
같다**는 뜻이지 참이라는 뜻이 아니다(I9: representation normalization ≠
semantic adjudication). 이 계약은 `test_cg_identity.py`의 AST 검사가
집행한다 — 규율이 아니라 게이트다.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path

SCHEMA_VERSION = "0.1.0"


def canonical_bytes(doc: dict) -> bytes:
    """The one byte-form both a writer and a reader derive from a document.

    `sort_keys=True` is load-bearing: a writer emits one key order and a
    reader gets JSON's, which does not promise to preserve it. Without the
    sort the two sides could disagree about a document neither had changed.
    (verbatim from _receipt.py)
    """
    return json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")


def canonical_sha256(doc: dict | None) -> str | None:
    """Hash of a document in a form both sides compute identically.

    Returns None for None so callers can compare "no document" without a
    special case -- an absent field must record the same absence rather than
    a hash of the string "null". (semantics verbatim from
    _receipt.receipt_sha256)
    """
    if doc is None:
        return None
    return hashlib.sha256(canonical_bytes(doc)).hexdigest()


# ---------------------------------------------------------------- identity --
# 지시 §7: node/claim/graph/obligation-target을 하나의 identity 규칙으로.
# kind를 도메인 분리자로 앞세우는 이유는 _receipt.sign의 domain과 같다 --
# node fingerprint가 우연히 claim fingerprint로 검증되는 대체 가능성을
# 구조적으로 없앤다. 같은 내용이라도 kind가 다르면 fingerprint가 다르다.

_FINGERPRINT_KINDS = ("node", "claim", "graph", "obligation_target")


def _assert_known_fingerprint_kind(kind: str) -> None:
    """가드를 별도 함수로 뽑은 이유: 이 저장소의 뮤테이션 강제 게이트
    (test_guard_negative_coverage.py)가 `assert_`/`_assert_` prefix로
    함수를 스캔한다. `fingerprint()` 안에 raise를 두면 게이트가 보지 못하는
    사각지대가 된다 — 실측(2026-08-22): `conceptgate/`에는 이 컨벤션을 쓰는
    함수가 이전까지 0개였다(패키지 전체가 게이트 사각지대). 신규 코드부터
    바로잡는다."""
    if kind not in _FINGERPRINT_KINDS:
        raise ValueError(
            f"unknown fingerprint kind {kind!r}; add it to _FINGERPRINT_KINDS "
            f"deliberately rather than passing free-form strings -- two "
            f"callers inventing adjacent names is how one identity rule "
            f"becomes several")


def fingerprint(kind: str, doc: dict) -> str:
    """`<kind>:<sha256>` — 정규화 표현의 identity. 진리값이 아니다(I9)."""
    _assert_known_fingerprint_kind(kind)
    digest = hashlib.sha256(
        kind.encode("utf-8") + b"\x00" + canonical_bytes(doc)).hexdigest()
    return f"{kind}:{digest}"


def node_fingerprint(node: dict) -> str:
    return fingerprint("node", node)


def claim_fingerprint(claim: dict) -> str:
    return fingerprint("claim", claim)


def graph_fingerprint(graph: dict) -> str:
    return fingerprint("graph", graph)


def obligation_target_fingerprint(target: dict) -> str:
    return fingerprint("obligation_target", target)


# ------------------------------------------------------ authentication ----
# W5 수정 (설계 리뷰 2026-08-22). 아래 세 함수는 codex 라인 `_receipt.py`
# (round 21, finding #1)에서 **본문 그대로** 가져왔다 — 그 라운드가 실측한
# 결함("자기 공개 내용의 공개 해시는 아무것도 인증하지 않는다 — 손으로 쓴
# receipt가 수락됐다")이 정확히 W5의 형태였고, 해법도 이미 검증돼 있었다.
#
# 서명이 막는 것과 못 막는 것 (원본의 정직 고지 유지):
#   막는다 — 키를 읽을 수 없는 호출자(MCP client/LLM)의 certificate 조작,
#            손으로 쓴 문서, 서명 후 편집.
#   못 막는다 — 이 호스트 파일시스템에 읽기 접근이 있는 주체. 키는 파일이다.
# 이 한계를 실제보다 강하게 서술하지 마라.

KEY_BYTES = 32


def default_key_path() -> Path:
    """host-only 서명 키의 기본 위치. 테스트·배포는 key_path 인자/환경변수로
    주입한다(codex 선례: reviewer_runner.py:598-604 "key_path exists so a
    test can present a different key")."""
    env = os.environ.get("CONCEPTGATE_KEY_PATH")
    if env:
        return Path(env)
    return Path.home() / ".conceptgate" / "host.key"


def load_or_create_key(path: Path) -> bytes:
    """The host-only signing key, created on first use with mode 0600.

    O_EXCL, not `if not path.exists()`: two launchers starting together would
    otherwise both pass the check and the second would overwrite the key the
    first had already signed with, invalidating a receipt nobody edited.
    (verbatim from _receipt.py)
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        key = path.read_bytes()
        if len(key) != KEY_BYTES:
            raise ValueError(
                f"{path.name} is {len(key)} bytes, expected {KEY_BYTES}; "
                "refusing to sign with a truncated key") from None
        return key
    with os.fdopen(fd, "wb") as fh:
        key = secrets.token_bytes(KEY_BYTES)
        fh.write(key)
    return key


def sign(body: dict, key: bytes, *, domain: str) -> str:
    """HMAC-SHA256 over the canonical body, namespaced by `domain`.

    `domain` keeps an isolation receipt from ever validating as some other
    kind of receipt signed with the same key -- the two have different
    meanings and must not be substitutable. (verbatim from _receipt.py)
    """
    msg = domain.encode("utf-8") + b"\x00" + canonical_bytes(body)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify_signature(doc: dict, key: bytes, *, domain: str,
                     field: str = "signature") -> bool:
    """True when `doc[field]` is this key's signature over the rest of `doc`.

    (원본 이름 `verify`에서 개명 — 이 모듈의 §29 AST 부정 계약이 판단형
    이름을 금지하는데 `verify` 단독은 판정으로 오독될 여지가 있어,
    서명 검증임이 이름에 드러나게 했다. 본문은 verbatim.)
    """
    presented = doc.get(field)
    if not isinstance(presented, str):
        return False
    body = {k: v for k, v in doc.items() if k != field}
    return hmac.compare_digest(sign(body, key, domain=domain), presented)

