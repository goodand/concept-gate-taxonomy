#!/usr/bin/env python3
"""cg_signing — Ed25519 비대칭 서명 primitive (잎 모듈).

계약은 `test_cg_signing.py`(정본). 배포면(Render)이 발급한 인증서를 로컬
`cg_store`가 거부한 사고(HMAC 발급 키 != 검증 키, D16: 대칭 키 영수증은
자기동일성과 검증 불가 사이만 오간다)를 닫는다. 프록시·중계 없이 **서버
개인키 서명 + 공개키 리소스 노출**로 — 발급자와 검증자가 다른 호스트여도
공개키 바이트만으로 검증에 도달한다.

WHY THIS MODULE IS SEPARATE FROM cg_identity
----------------------------------------------
`cg_identity`는 잎(의존 0)이고 `test_cg_identity.py:100`이 그 모듈의 import를
AST 화이트리스트(`hashlib/json/hmac/os/secrets/pathlib/__future__`)로 강제한다.
`cryptography`를 그 화이트리스트에 넣으면 이 저장소가 지금까지 지켜온
"표현 계층은 무거워지지 않는다" 불변식이 깨진다. 그래서 비대칭 서명 primitive는
**새 잎 모듈**로 분리했다 — 이 모듈의 최상위 import는 stdlib(`hashlib`)와
`conceptgate.cg_identity`뿐이고, `cryptography`는 아래 각 함수 **안에서만**
지연 import 한다(`test_cg_signing.py`의 계약 ①이 AST로 최상위 import 부재를
검사한다). `cg_signing`을 import하는 비용이 곧바로 `cryptography` 로딩 비용을
끌고 오지 않는다 — cg_signing을 import만 하고 서명·검증을 한 번도 안 하는
호출자(예: 스키마만 읽는 코드)는 그 비용을 내지 않는다.

NEGATIVE CONTRACT (cg_identity §29 와 같은 정신)
--------------------------------------------------
select/choose/judge/certify/repair/infer/score 류 판정형 이름을 이 모듈에
추가하지 마라. `verify()`는 "이 공개키의 유효한 서명인가"만 답하고, 그
서명이 무엇을 **허가하는지**는 판단하지 않는다 — 그 판단은 `cg_obligations`
(`_assert_certificate_grants_verdicts`)의 몫이다.
"""
from __future__ import annotations

import hashlib

from conceptgate import cg_identity

SEED_BYTES = 32
PUBLIC_KEY_BYTES = 32
SIGNATURE_BYTES = 64

_CRYPTOGRAPHY_HINT = (
    "cryptography 패키지가 필요합니다 -- requirements.txt/pyproject.toml의 "
    "선언을 확인하세요 (pip install cryptography==50.0.1)"
)


def _ed25519():
    """`cryptography`의 Ed25519 프리미티브를 지연 import 한다.

    부재 시 어디를 봐야 하는지(requirements 선언)를 가리키는 명확한
    ImportError로 다시 던진다 -- 배포 이미지가 requirements.txt만 설치하므로
    이 메시지가 나오면 선언 누락이 원인이다."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey, Ed25519PublicKey)
        from cryptography.hazmat.primitives import serialization
    except ImportError as exc:
        raise ImportError(f"{_CRYPTOGRAPHY_HINT} ({exc})") from exc
    return Ed25519PrivateKey, Ed25519PublicKey, serialization


def public_key_bytes(seed: bytes) -> bytes:
    """32바이트 Ed25519 seed(개인키) → raw 32바이트 공개키.

    seed 길이가 틀리면(공격이 아니라 호출 실수의 신호) ValueError -- False로
    삼키면 "서명이 안 맞다"와 "키 형태가 틀렸다"가 구별 불가해진다.
    """
    if len(seed) != SEED_BYTES:
        raise ValueError(f"seed is {len(seed)} bytes, expected {SEED_BYTES}")
    Ed25519PrivateKey, _, serialization = _ed25519()
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    return priv.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw)


def key_id(pub: bytes) -> str:
    """공개키만의 함수 -- 문서·서명과 무관하게 결정된다(호스트 정체성 식별자)."""
    return hashlib.sha256(pub).hexdigest()


def sign(body: dict, seed: bytes, *, domain: str) -> str:
    """Ed25519 서명, hex. 메시지 형태는 `cg_identity.sign`과 같은 도메인
    분리(`domain.encode() + b"\\x00" + canonical_bytes(body)`) -- 같은 키로
    서명한 다른 종류의 문서가 서로 대체되지 않게 한다."""
    if len(seed) != SEED_BYTES:
        raise ValueError(f"seed is {len(seed)} bytes, expected {SEED_BYTES}")
    Ed25519PrivateKey, _, _ = _ed25519()
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    msg = domain.encode("utf-8") + b"\x00" + cg_identity.canonical_bytes(body)
    return priv.sign(msg).hex()


def verify(doc: dict, pub: bytes, *, domain: str, field: str = "signature") -> bool:
    """`doc[field]`가 `pub`의 이 문서에 대한 유효한 서명인지.

    공개키 길이 오류만 ValueError(호출자 실수) -- 그 외 모든 검증 실패
    (서명 부재·non-str·hex 아님·길이 오류·암호학적 불일치)는 **False**다.
    형식 오류를 예외로 올리면 호출자가 `except`를 빠뜨렸을 때 fail-open이
    되므로, 검증 실패의 한 종류로 통일한다.
    """
    if len(pub) != PUBLIC_KEY_BYTES:
        raise ValueError(f"public key is {len(pub)} bytes, expected {PUBLIC_KEY_BYTES}")
    presented = doc.get(field)
    if not isinstance(presented, str):
        return False
    try:
        sig_bytes = bytes.fromhex(presented)
    except ValueError:
        return False
    if len(sig_bytes) != SIGNATURE_BYTES:
        return False
    _, Ed25519PublicKey, _ = _ed25519()
    from cryptography.exceptions import InvalidSignature
    public_key = Ed25519PublicKey.from_public_bytes(pub)
    body = {k: v for k, v in doc.items() if k != field}
    msg = domain.encode("utf-8") + b"\x00" + cg_identity.canonical_bytes(body)
    try:
        public_key.verify(sig_bytes, msg)
    except InvalidSignature:
        return False
    return True
