"""fixture commitment resolver의 TDD 계약 (D-E2E-v1-20 §Q20.4, D-21 §9) — RED 먼저.

기제만 다룬다 — fixture 내용 20건은 source 자격(D-21 Q21.2 b*) 전까지 차단.
캐시는 content-addressed(파일명 = 내용의 sha256 hex): 레코드 추출 규칙이
source 형식에 묶이지 않으므로 어떤 source가 자격을 통과하든 이 기제가 그대로
간다. D-20 조항의 기계화:
  - 캐시는 권위가 아니다 → 반환 전 바이트를 재해시해 파일명과 대조
  - 소진(miss)·불일치(tamper) → execution="unavailable" (ERROR 아님 — 예상
    가능한 부재), 불일치 시 데이터를 절대 반환하지 않는다
  - 정답 대체·재구성 금지 → 이 모듈은 fetch를 모른다(네트워크 import 금지)
모든 테스트 데이터는 발명 바이트 — corpus 콘텐츠 0(ORACLE-12).
"""
from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_fixture_resolver as fr


def put(cache: Path, data: bytes) -> str:
    """콘텐츠를 캐시에 넣고 주소(sha256 hex)를 돌려준다."""
    h = hashlib.sha256(data).hexdigest()
    (cache / h).write_bytes(data)
    return h


def entry(cache: Path, text=b"the florp glims", lf=b"(A-aN:glim florp)") -> dict:
    return {
        "source_locator": {"corpus_id": "invented-corpus", "corpus_version": "v9",
                           "artifact": "made-up.txt", "record_locator": "7",
                           "retrieval_urls": ["https://example.invalid/x"]},
        "text_sha256": put(cache, text),
        "lf_sha256": put(cache, lf),
        "adapter_version": "test-only",
        "adapter_code_sha256": "0" * 64,
        "canonicalization_profile_hash": "1" * 64,
        "expected_ir_sha256": "2" * 64,
    }


# ---------------------------------------------------------- commitment 계약 --

def test_commitment_fields_are_exactly_the_d20_set():
    assert set(fr.COMMITMENT_FIELDS) == {
        "source_locator", "text_sha256", "lf_sha256", "adapter_version",
        "adapter_code_sha256", "canonicalization_profile_hash",
        "expected_ir_sha256"}


def test_entry_guard_accepts_a_complete_entry(tmp_path):
    fr._assert_commitment_entry_complete(entry(tmp_path))


@pytest.mark.parametrize("missing", [
    "source_locator", "text_sha256", "lf_sha256", "adapter_version",
    "adapter_code_sha256", "canonicalization_profile_hash",
    "expected_ir_sha256"])
def test_entry_guard_rejects_each_missing_field(tmp_path, missing):
    e = entry(tmp_path); del e[missing]
    with pytest.raises(ValueError):
        fr._assert_commitment_entry_complete(e)


@pytest.mark.parametrize("sub", ["corpus_id", "corpus_version", "artifact",
                                 "record_locator"])
def test_entry_guard_rejects_missing_locator_subfield(tmp_path, sub):
    e = entry(tmp_path); del e["source_locator"][sub]
    with pytest.raises(ValueError):
        fr._assert_commitment_entry_complete(e)


def test_entry_guard_rejects_malformed_sha256(tmp_path):
    e = entry(tmp_path); e["text_sha256"] = "zz" * 32   # hex 아님, 길이만 맞음
    with pytest.raises(ValueError):
        fr._assert_commitment_entry_complete(e)
    e2 = entry(tmp_path); e2["lf_sha256"] = "ab12"      # 너무 짧음
    with pytest.raises(ValueError):
        fr._assert_commitment_entry_complete(e2)


# ------------------------------------------------------------- resolve 축 ---

def test_resolve_bytes_roundtrip(tmp_path):
    h = put(tmp_path, b"invented payload")
    out = fr.resolve_bytes(h, tmp_path)
    assert out == {"execution": "ok", "data": b"invented payload"}


def test_cache_miss_is_unavailable_not_an_exception(tmp_path):
    out = fr.resolve_bytes("a" * 64, tmp_path)
    assert out["execution"] == "unavailable"
    assert "data" not in out
    assert "miss" in out["reason"] or "absent" in out["reason"]


def test_tampered_cache_is_unavailable_and_never_returns_bytes(tmp_path):
    """캐시는 권위가 아니다: 파일명이 주장하는 해시와 바이트가 다르면 그
    바이트는 존재하지 않는 것과 같다 — 반환은 위조 통과가 된다."""
    h = put(tmp_path, b"original bytes")
    (tmp_path / h).write_bytes(b"tampered bytes!!")
    out = fr.resolve_bytes(h, tmp_path)
    assert out["execution"] == "unavailable"
    assert "data" not in out
    assert "mismatch" in out["reason"]


def test_resolve_fixture_ok(tmp_path):
    out = fr.resolve_fixture(entry(tmp_path), tmp_path)
    assert out["execution"] == "ok"
    assert out["text"] == b"the florp glims"
    assert out["lf"] == b"(A-aN:glim florp)"


def test_resolve_fixture_partial_cache_names_what_is_missing(tmp_path):
    e = entry(tmp_path)
    (tmp_path / e["lf_sha256"]).unlink()
    out = fr.resolve_fixture(e, tmp_path)
    assert out["execution"] == "unavailable"
    assert "text" not in out and "lf" not in out, (
        "부분 성공을 반환하면 호출자가 반쪽 fixture로 진행한다 — 전부 아니면 무")
    assert "lf_sha256" in out["missing"]


def test_resolve_fixture_is_deterministic(tmp_path):
    e = entry(tmp_path)
    assert fr.resolve_fixture(e, tmp_path) == fr.resolve_fixture(e, tmp_path)


def test_unavailable_vocabulary_aligns_with_execution_axis():
    """문자열이지만 어휘는 ExecutionStatus와 정렬 — 테스트에서만 대조한다.
    프로덕션 import는 금지(아래 분리 테스트): resolver가 Verify 축 모듈을
    끌면 ORACLE-08/10 분리가 무너진다."""
    from conceptgate.cg_obligations import ExecutionStatus
    assert ExecutionStatus.UNAVAILABLE.value == "unavailable"
    assert ExecutionStatus.OK.value == "ok"


# --------------------------------------------- 분리·순수성 (AST 집행) --------

def test_resolver_imports_stay_offline_and_leaf():
    """fetch를 모르는 모듈이어야 한다 — 네트워크 import가 없으면 '캐시 소진
    시 조용히 다시 받아오기'류 우회가 구조적으로 불가능하다(ORACLE-08)."""
    tree = ast.parse(Path(inspect.getfile(fr)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing", "hashlib", "pathlib"}, imported


def test_resolver_is_not_imported_by_refine_or_verify_modules():
    root = Path(inspect.getfile(fr)).parent
    for name in ("server.py", "cg_obligations.py", "cg_normalizer.py",
                 "concept_gate_v7.py", "cg_ir.py", "cg_identity.py",
                 "cg_evaluate.py", "cg_oracle_adapter.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "cg_fixture_resolver" not in src, f"{name} imports the resolver"


def test_resolve_fixture_refuses_an_incomplete_entry_before_touching_cache(tmp_path):
    """가드가 존재하는 것과 resolve_fixture가 가드를 **경유**하는 것은 다른
    명제다 — 직접 호출 테스트만 있으면 배선을 끊는 뮤테이션이 잡히지 않는다
    (lead 뮤테이션 M4가 실측: 가드 호출을 pass로 바꿔도 전 테스트 통과였다)."""
    e = entry(tmp_path); del e["expected_ir_sha256"]
    with pytest.raises(ValueError):
        fr.resolve_fixture(e, tmp_path)
