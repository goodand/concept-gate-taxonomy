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
import json

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


def fingerprint(kind: str, doc: dict) -> str:
    """`<kind>:<sha256>` — 정규화 표현의 identity. 진리값이 아니다(I9)."""
    if kind not in _FINGERPRINT_KINDS:
        raise ValueError(
            f"unknown fingerprint kind {kind!r}; add it to _FINGERPRINT_KINDS "
            f"deliberately rather than passing free-form strings -- two "
            f"callers inventing adjacent names is how one identity rule "
            f"becomes several")
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
