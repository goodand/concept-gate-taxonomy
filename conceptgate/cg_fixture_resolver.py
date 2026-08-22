"""Fixture commitment resolver — D-E2E-v1-20 §Q20.4, D-21 §9 규제 기계화.

캐시는 content-addressed(파일명 = 내용의 sha256 hex): 레코드 추출 규칙이
source 형식에 묶이지 않으므로 어떤 source가 자격을 통과하든 이 기제가 그대로
간다. D-20 조항의 기계화:

  - 캐시는 권위가 아니다 → 반환 전 바이트를 재해시해 파일명과 대조.
    miss/tamper 감지 후 해당 데이터를 절대 반환하지 않는다 (예방·정정 불가).
  - 소진(miss)·불일치(tamper) → execution="unavailable" (ERROR 아님 — 예상
    가능한 부재). 모듈이 fetch를 모르므로 사라진 데이터는 되돌릴 수 없다.
  - 정답 대체·재구성 금지 → 네트워크 import 정지(구조적 무능).
  - fixture 수집 all-or-nothing: text_sha256/lf_sha256 둘 다 이용 가능할 때만
    결과를 돌린다. 하나라도 빠지면 부분 성공도 실패도 아니라 unavailable.

모든 테스트 데이터는 발명 바이트 — corpus 콘텐츠 0(ORACLE-12).
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


# ── Commitment 축 ──
COMMITMENT_FIELDS = (
    "source_locator",
    "text_sha256",
    "lf_sha256",
    "adapter_version",
    "adapter_code_sha256",
    "canonicalization_profile_hash",
    "expected_ir_sha256",
)


def _is_valid_sha256(value: str) -> bool:
    """64-char lowercase hex string 검증 (엄격한 규칙)."""
    return len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def _assert_commitment_entry_complete(entry: dict) -> None:
    """Commitment entry 완전성 보증.

    Raises ValueError when:
      - 7개 필수 필드 중 하나라도 missing
      - source_locator가 corpus_id/corpus_version/artifact/record_locator 중
        하나라도 부재
      - *_sha256 필드가 64-char lowercase hex가 아님

    에러 메시지는 WHICH 필드가 잘못됐는지 명시.
    """
    # 최상위 필드 7개 검사
    for field in COMMITMENT_FIELDS:
        if field not in entry:
            raise ValueError(f"missing field: {field}")

    # source_locator 검사
    locator = entry["source_locator"]
    if not isinstance(locator, dict):
        raise ValueError("source_locator must be a dict")

    required_subfields = {"corpus_id", "corpus_version", "artifact", "record_locator"}
    for sub in required_subfields:
        if sub not in locator:
            raise ValueError(f"source_locator missing subfield: {sub}")

    # sha256 필드 검증 (4개: text_sha256, lf_sha256, adapter_code_sha256,
    # canonicalization_profile_hash, expected_ir_sha256)
    sha256_fields = [
        "text_sha256",
        "lf_sha256",
        "adapter_code_sha256",
        "canonicalization_profile_hash",
        "expected_ir_sha256",
    ]

    for field in sha256_fields:
        value = entry[field]
        if not _is_valid_sha256(value):
            raise ValueError(
                f"{field} must be 64-char lowercase hex; got {value!r}"
            )


# ── Resolve 축 ──


def resolve_bytes(sha256_hex: str, cache_dir: Any) -> dict:
    """Content-addressed cache lookup.

    cache_dir을 Path()로 정규화해 cache_dir/sha256_hex 읽기 시도.

    반환:
      - 파일 absent → {"execution": "unavailable", "reason": "...miss/absent..."}
      - 파일 present but re-hash mismatch → {"execution": "unavailable",
        "reason": "...mismatch..."} (바이트 절대 반환 안 함)
      - re-hash match → {"execution": "ok", "data": <bytes>} (정확히 이 키만)
    """
    cache_path = Path(cache_dir) / sha256_hex

    # Cache miss
    if not cache_path.exists():
        return {
            "execution": "unavailable",
            "reason": f"cache miss or absent: {sha256_hex}",
        }

    # Read and re-hash
    data = cache_path.read_bytes()
    computed = hashlib.sha256(data).hexdigest()

    if computed != sha256_hex:
        return {
            "execution": "unavailable",
            "reason": f"cache mismatch: filename {sha256_hex} but content hashes to {computed}",
        }

    return {"execution": "ok", "data": data}


def resolve_fixture(entry: dict, cache_dir: Any) -> dict:
    """Fixture 완전성 해결 (all-or-nothing).

    1. entry를 _assert_commitment_entry_complete로 검증
    2. entry["text_sha256"], entry["lf_sha256"]를 각각 resolve_bytes로 해결
    3. 결과:
       - 둘 다 ok → {"execution": "ok", "text": <bytes>, "lf": <bytes>}
       - 하나라도 unavailable → {"execution": "unavailable", "missing": [필드명들],
         ...} (text/lf 키 절대 없음 — 부분은 더 나쁨)
    """
    # Guard: entry 완전성 검증
    _assert_commitment_entry_complete(entry)

    # Resolve both
    text_result = resolve_bytes(entry["text_sha256"], cache_dir)
    lf_result = resolve_bytes(entry["lf_sha256"], cache_dir)

    # All-or-nothing: 둘 다 ok여야 성공
    if text_result["execution"] == "ok" and lf_result["execution"] == "ok":
        return {
            "execution": "ok",
            "text": text_result["data"],
            "lf": lf_result["data"],
        }

    # Any failure: collect missing fields
    missing = []
    if text_result["execution"] != "ok":
        missing.append("text_sha256")
    if lf_result["execution"] != "ok":
        missing.append("lf_sha256")

    return {
        "execution": "unavailable",
        "missing": missing,
    }
