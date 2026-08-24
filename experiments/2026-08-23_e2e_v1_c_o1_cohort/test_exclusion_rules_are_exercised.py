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
    # `span`을 포함해 실물 파서(`cg_mrs_reader`) 산출과 형태를 맞춘다 —
    # 적대 검증 Finding 3: 형태가 어긋나면 증인이 GREEN이어도 실물에서
    # 규칙이 죽을 수 있다(지금은 span 미사용이지만 형태 드리프트를 막는다).
    return {"pred": pred, "span": (0, 1), "lbl": lbl, "args": dict(args)}


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

def _witness_string_constants() -> set:
    """**증인 테스트 함수 본문 안의** 문자열 상수만 수집한다.

    적대 검증(2026-08-24, Haiku red team)이 이전 판을 뚫었다: 이전 검사는
    모듈 소스 전체에 대한 부분 문자열 검색이어서 **주석·docstring·
    KNOWN_UNWITNESSED 등재**가 전부 증인으로 세어졌다 — 면제와 증인이
    구별되지 않았고, 그것은 이 게이트가 잡으려던 결함 부류("코드가 참으로
    만들지 않는 명제를 주장")를 게이트 자신이 저지른 것이다.

    AST로 좁힌다: `test_*` 함수의 **본문**(docstring 제외)에 등장하는 문자열
    상수만. 주석은 AST에 없고, KNOWN_UNWITNESSED는 함수가 아니며,
    docstring은 첫 문장으로 식별해 제외한다.
    """
    import ast, inspect
    tree = ast.parse(inspect.getsource(
        inspect.getmodule(_witness_string_constants)))
    got: set = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        body = node.body
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            body = body[1:]                      # docstring 제외
        for stmt in body:
            for sub in ast.walk(stmt):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    got.add(sub.value)
    return got


def test_every_reject_code_has_a_witness_test():
    """`REJECT_CODES`의 코드마다 **증인 테스트** 또는 **명시적 면제**가 있어야 한다.

    두 경로를 구별한다(적대 검증이 요구한 수리):
    (a) 증인 — test_ 함수 본문의 문자열 상수로 그 코드가 등장한다
    (b) 면제 — `KNOWN_UNWITNESSED`의 **키**다. 면제는 조용히 통과되지 않고
        아래 단언 메시지에 이름이 찍힌다.
    """
    witnessed = _witness_string_constants()
    exempt = set(KNOWN_UNWITNESSED)
    missing = [c for c in mcp.REJECT_CODES
               if c not in witnessed and c not in exempt]
    assert not missing, (
        f"증인 테스트가 없는 reject 코드: {missing}. "
        f"증인을 쓰거나 KNOWN_UNWITNESSED에 이유와 담당을 적어라 "
        f"(현재 면제: {sorted(exempt)})")


def test_comment_or_exemption_mention_is_not_a_witness():
    """음성 테스트 — red team의 우회 경로가 닫혔다는 증거.

    (1) 주석·docstring 언급은 AST에 없거나 제외되므로 증인이 아니다.
    (2) KNOWN_UNWITNESSED 등재는 exempt이지 witnessed가 아니다.
    """
    witnessed = _witness_string_constants()
    # 프로브 문자열을 **런타임 결합**으로 만든다 — 통짜 리터럴로 적으면 이
    # 단언 자체가 test_ 함수 본문의 상수라 수집돼 자기모순이 된다(이 수리의
    # 첫 판이 정확히 그렇게 실패했고, 음성 테스트가 그것을 잡았다).
    probe = "fake_code_" + "only_in_a_comment"   # 주석에는 통짜로 적혀 있다:
    # fake_code_only_in_a_comment  ← 주석은 AST에 없으므로 수집되지 않는다
    assert probe not in witnessed
    for exempt_key in KNOWN_UNWITNESSED:
        # 면제 키가 우연히 어떤 증인 테스트 본문에 나타나면 그건 증인이
        # 생겼다는 뜻이므로 면제를 지워야 한다 — 둘 다면 회계가 모호해진다.
        assert exempt_key not in witnessed, (
            f"{exempt_key}: 면제로 등재됐는데 증인도 있다 — 면제를 지워라")


def test_known_unwitnessed_entries_carry_a_reason_and_owner():
    """형식 검사는 **tripwire이지 증명이 아니다** (정직한 한계 명시).

    적대 검증이 보인 대로 무의미한 채움 텍스트("aaa…담당: someone")도 이
    형식을 통과한다. 형식 검사가 막는 것은 **빈 면제**(이유 없음)뿐이고,
    이유의 **의미**는 사람 리뷰와 git diff의 몫이다 — 면제 추가는 이 파일의
    diff로 반드시 드러난다. Codex 라인의 repair_loop이 G1 우회 가능성을
    문서화한 것과 같은 태도다: 가드의 한계를 숨기지 않고 적는다.
    """
    for rule, reason in KNOWN_UNWITNESSED.items():
        assert len(reason) > 60, f"{rule}: 이유가 너무 짧다"
        assert "담당" in reason, f"{rule}: 담당이 없다"
