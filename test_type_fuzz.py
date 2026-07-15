#!/usr/bin/env python3
"""타입 fuzz 계약 테스트 — 어떤 진입점도 변형 입력에 crash하지 않는다.

배경: 2026-07-13 fuzz에서 116케이스 중 87건이 unhandled AttributeError/
TypeError로 crash (PR #1 리뷰 봇 + 이전 적대 리뷰 발견 6). 타입 가드 후
CRASH=0으로 고정한다. 하네스(fuzz_normalizer_types.CASES)가 단일 출처다 —
케이스를 추가하려면 하네스에 추가하라.

허용(ACCEPTED) 목록은 명시적이다: 새 케이스가 ok=True로 통과하면
이 테스트가 실패하고, 그 통과가 정당한지 사람이 판단해 목록에 넣어야 한다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import fuzz_normalizer_types as F

# 정당한 통과 — 전부 "None=미제공" 의미론이거나 올바른 str 타입
ACCEPTED_ALLOWLIST = {
    "make_snapshot(text=str)",          # 유효한 텍스트
    "lookup_senses(surface=str)",       # 유효한 표면형 (out_of_inventory)
    "validate_selection(span=NoneType)",  # span 미제공 → unverified
    "map_owl(snapshot=NoneType)",       # snapshot 미제공 → 빈 원문
    "map_owl(differentia=NoneType)",    # 목록 미제공 → 빈 목록
    "map_owl(disjoint_with=NoneType)",  # 목록 미제공 → 빈 목록
    "map_owl(kind_rationale=str)",      # rationale은 원래 str
    "owl.build(name=str)",              # 유효한 클래스명
    "owl.build(genus=NoneType)",        # genus 미제공 (primitive 허용)
    "map_owl(stereotype=NoneType)",     # stereotype 미제공 (gUFO meta-type 없음)
    "owl.build(stereotype=NoneType)",   # stereotype 미제공 (gUFO meta-type 없음)
    "owl.build(differentia=NoneType)",  # 목록 미제공 → 빈 목록
    "owl.build(disjoint_groups=NoneType)",  # 목록 미제공 → 빈 목록
    "owl.build(objprop_item=str)",      # property명은 원래 str
}


def test_no_entrypoint_crashes_and_accepted_is_allowlisted():
    crash, unexpected_ok, malformed = [], [], []
    for name, fn in F.CASES:
        try:
            r = fn()
        except Exception as exc:
            crash.append((name, f"{type(exc).__name__}: {exc}"))
            continue
        if not isinstance(r, dict):
            malformed.append((name, type(r).__name__))
        elif r.get("ok"):
            if name not in ACCEPTED_ALLOWLIST:
                unexpected_ok.append(name)
        elif not r.get("errors"):
            malformed.append((name, "ok=False인데 errors 없음"))
    assert not crash, f"unhandled crash {len(crash)}건: {crash[:5]}"
    assert not malformed, f"비정형 반환: {malformed[:5]}"
    assert not unexpected_ok, (
        f"허용목록 밖의 통과 {unexpected_ok} — 정당하면 ACCEPTED_ALLOWLIST에 "
        f"근거 주석과 함께 추가하라")


def test_every_error_carries_stage_and_code():
    """구조화 오류 계약: 거부는 반드시 원인 단계와 코드를 가진다."""
    for name, fn in F.CASES:
        try:
            r = fn()
        except Exception:
            continue  # 위 테스트가 잡음
        if isinstance(r, dict) and r.get("ok") is False:
            assert r.get("stage"), f"{name}: stage 누락"
            for e in r.get("errors", []):
                assert e.get("stage") and e.get("code"), f"{name}: {e}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
