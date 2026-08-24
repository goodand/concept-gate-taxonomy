"""배제 규칙이 **공허하지 않다**는 것을 증거로 요구한다.

저장소 규율의 확장이다. 루트 `test_guard_negative_coverage.py`가 코드 가드에
음성 테스트를 강제하는 이유와 같다 — **정상 규칙과 공허한 규칙의 관측값이
동일**하기 때문이다. 배제 규칙(데이터 규칙)도 같은 병에 걸린다.

2026-08-24 실측이 그 병을 보여줬다. cascade에서 앞 규칙이 먼저 잡으면 뒤 규칙은
0건이 되고, 그 상태로는 규칙이 실체가 있는지 알 수 없다. E2·E3·E4·E5가 전부
0건이었고 E1이 먼저 잡았기 때문이었다. cascade 없이 **독립 실행**하니 E2 9,758 ·
E3 297 · E4 428이 나왔다. 그리고 그 검사가 **E3의 정의 오류까지 잡았다** —
관계 수식어를 일괄 배제하면 사상 대상인 `_at+least_x_deg`도 버린다.

그래서 이 게이트가 요구하는 것은 규칙마다 **최소 하나의 증인(witness)** 이다.
증인은 이 파일 안에 실물 구조로 적는다 — 코퍼스 파일에 의존하면 게이트가
로컬 캐시 없이는 돌지 않고, 그러면 CI에서 조용히 건너뛰어진다.

**증인이 없는 규칙은 원장에서 지우거나 이유를 적어라.** 후자가 필요하면
`KNOWN_UNWITNESSED`에 이유와 담당을 적는다 — 루트 게이트의 `KNOWN_UNPROVEN`과
같은 관용구다. 모킹으로 초록을 만드는 것과 이유를 적는 것은 다르다.
"""
from __future__ import annotations

import pytest

import _stage2_dedup as dd
import _stage2_mrs_count_projection as mcp
import _stage2_numeric_designator as nd

# 증인을 쓸 수 없는 규칙과 그 이유. 비어 있는 것이 정상이다.
KNOWN_UNWITNESSED: dict[str, str] = {
    "E5_empty_body": (
        "투영 신호 게이트(PROJECTION_SIGNAL_V1)와 중복 방어다. 그 게이트가 이미 "
        "본문 내용 부재를 fail-closed로 잡으므로 별도 배제 규칙의 증인을 "
        "만들면 같은 것을 두 번 세게 된다. 2026-08-24 전수 실측에서도 0건이었다. "
        "담당: 이 규칙을 원장에 남길지 여부는 Q32 판정 후 재검토."),
}


def _ep(pred, lbl="h8", **args):
    return {"pred": pred, "lbl": lbl, "args": dict(args)}


def _mrs(eps, hcons=()):
    return {"top": "h1", "eps": list(eps), "hcons": [tuple(h) for h in hcons]}


# ---- 각 규칙의 증인 ------------------------------------------------------
#
# 증인은 **그 규칙만** 발동시켜야 한다. 다른 규칙이 먼저 잡으면 그 증인은
# 아무것도 증명하지 못한다 — cascade 오염이 바로 이 게이트가 막는 것이다.

def test_e15_type_mismatch_has_a_witness():
    """`$1.5 billion`의 card는 ARG1이 `i`(측정 구문의 미명세 개체)다."""
    m = _mrs([_ep("udef_q", "h4", ARG0="i25", RSTR="h6", BODY="h7"),
              _ep("card", "h8", ARG0="e9", ARG1="i25", CARG="1000000000"),
              _ep("_dollar_n_1", "h8", ARG0="i25")],
             hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "type_mismatch"


def test_e13_compound_cardinal_has_a_witness():
    """`two or three bottles` — 같은 변수에 card가 둘."""
    m = _mrs([_ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
              _ep("card", "h8", ARG0="e9", ARG1="x5", CARG="2"),
              _ep("card", "h9", ARG0="e10", ARG1="x5", CARG="3"),
              _ep("_bottle_n_of", "h8", ARG0="x5")],
             hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["reject"] == "unsupported_compound_cardinal_mapping_v1"
    assert out["intrinsically_unexpressible"] is False


def test_e14_numeric_designator_has_a_witness():
    """`Intel 286 microprocessors` — 수사가 명칭의 일부다."""
    m = _mrs([_ep("card", "h8", ARG1="x5", CARG="286"),
              _ep("compound", "h8", ARG1="x5", ARG2="x11"),
              _ep("named", "h15", ARG0="x11", CARG="Intel"),
              _ep("_microprocessor_n_1", "h8", ARG0="x5")])
    assert nd.classify(m, "x5")["verdict"] == "DESIGNATOR"


def test_e14_needs_audit_has_a_witness():
    """3값 계약의 세 번째 값도 증인이 필요하다 — 없으면 2값과 구별 불가다."""
    m = _mrs([_ep("card", "h8", ARG1="x5", CARG="3")])
    assert nd.classify(m, "x5")["verdict"] == "NEEDS_AUDIT"


def test_unresolved_handle_has_a_witness():
    """실물 MRS는 최외곽 양화의 BODY를 HCONS에 넣지 않는다."""
    m = _mrs([_ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
              _ep("card", "h8", ARG0="e9", ARG1="x5", CARG="2"),
              _ep("_irony_n_1", "h8", ARG0="x5")],
             hcons=[("h6", "QEQ", "h8")])
    assert mcp.package_count(m)["reject"] == "unresolved_handle_constraint"


def test_variable_disagreement_has_a_witness():
    m = _mrs([_ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
              _ep("card", "h8", ARG0="e9", ARG1="x99", CARG="2"),
              _ep("_irony_n_1", "h8", ARG0="x5")],
             hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "card_and_quantifier_variable_disagree"


def test_attachment_ambiguity_has_a_witness():
    m = _mrs([_ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
              _ep("_the_q", "h10", ARG0="x5", RSTR="h11", BODY="h12"),
              _ep("card", "h8", ARG0="e9", ARG1="x5", CARG="2"),
              _ep("_irony_n_1", "h8", ARG0="x5")],
             hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2"),
                    ("h11", "QEQ", "h8"), ("h12", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "numeric_scope_attachment_ambiguous"


def test_unsupported_numeric_relation_has_a_witness():
    m = _mrs([_ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
              _ep("card", "h8", ARG0="e9", ARG1="x5", CARG="a few"),
              _ep("_irony_n_1", "h8", ARG0="x5")],
             hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "unsupported_numeric_relation"


def test_e4_exact_duplicate_has_a_witness():
    out = dd.partition([{"item_id": "a", "text_sha256": "T", "gold_sha256": "M"},
                        {"item_id": "b", "text_sha256": "T", "gold_sha256": "M"}])
    assert len(out["collapsed"]) == 1


def test_oracle_collision_has_a_witness():
    out = dd.partition([{"item_id": "a", "text_sha256": "T", "gold_sha256": "M1"},
                        {"item_id": "b", "text_sha256": "T", "gold_sha256": "M2"}])
    assert len(out["collisions"]) == 2 and out["eligible"] == []


# ---- 원장 대조: 모든 reject 코드에 증인이 있는가 -----------------------

def test_every_reject_code_has_a_witness_test():
    """`REJECT_CODES`에 코드를 추가하면 증인 테스트도 추가해야 한다.

    이 게이트의 핵심이다. 코드만 늘리고 증인을 안 만들면 그 코드는
    **도달 불가일 수 있고**, 도달 불가한 배제 규칙은 공허한 가드와 같다.
    """
    import inspect
    src = inspect.getsource(inspect.getmodule(test_every_reject_code_has_a_witness_test))
    missing = [c for c in mcp.REJECT_CODES if f'"{c}"' not in src]
    assert not missing, (
        f"증인 테스트가 없는 reject 코드: {missing}. "
        "증인을 쓰거나 KNOWN_UNWITNESSED에 이유와 담당을 적어라")


def test_known_unwitnessed_entries_carry_a_reason_and_owner():
    for rule, reason in KNOWN_UNWITNESSED.items():
        assert len(reason) > 60, f"{rule}: 이유가 너무 짧다"
        assert "담당" in reason, f"{rule}: 담당이 없다"
