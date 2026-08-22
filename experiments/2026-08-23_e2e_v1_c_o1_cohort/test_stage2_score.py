"""Stage 2 채점 모듈의 TDD 계약 — RED 먼저 (준비물 ④).

지표 정의는 D-E2E-v1-19 verbatim (§UCR·§8·§9):
  UCR = PASS / N_preregistered            (primary)
  DirectMatch = DirectPASS / N
  CertificationCoverage = Certified / N
  CertifiedCorrectYield = (Certified ∧ OraclePASS) / N   ← 분모가 N이다
  P(PASS|Certified)                        (secondary diagnostic ONLY)
  2×2: A=Cert∧Correct, B=Cert∧Wrong(=certification false-positive),
       C=¬Cert∧Correct, D=¬Cert∧Wrong
수용(D-21 재확인): PASS≥16 ∧ 최종 ERROR=0 ∧ 예상 밖 UNSCORABLE=0.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import _stage2_score as S  # noqa: E402


def T(tid, result, certified=False, unscorable_expected=False):
    return {"trial_id": tid, "result": result, "certified": certified,
            "unscorable_expected": unscorable_expected}


def test_ruling_v2_counterexample_ucr_is_20_percent():
    """판정 검증표 V2의 산술 반례를 그대로: 조건부 100%가 아니라 UCR 20%."""
    trials = ([T(f"p{i}", "pass") for i in range(20)]
              + [T(f"u{i}", "unscorable", unscorable_expected=True)
                 for i in range(80)])
    out = S.score(trials, n_preregistered=100, pass_min=16)
    assert out["metrics"]["UCR"] == pytest.approx(0.20)


def test_metric_denominators_are_n_preregistered():
    """CertifiedCorrectYield 분모는 Certified 수가 아니라 N — D-19 §8 3식."""
    trials = [T("a", "pass", certified=True), T("b", "fail", certified=True),
              T("c", "pass"), T("d", "fail")]
    out = S.score(trials, n_preregistered=4, pass_min=1)
    m = out["metrics"]
    assert m["DirectMatch"] == pytest.approx(2 / 4)
    assert m["CertificationCoverage"] == pytest.approx(2 / 4)
    assert m["CertifiedCorrectYield"] == pytest.approx(1 / 4)
    assert m["P_pass_given_certified"] == pytest.approx(1 / 2)


def test_secondary_is_none_when_nothing_is_certified():
    out = S.score([T("a", "pass"), T("b", "fail")], n_preregistered=2,
                  pass_min=1)
    assert out["metrics"]["P_pass_given_certified"] is None


def test_two_by_two_partitions_all_trials():
    trials = [T("a", "pass", certified=True),      # A
              T("b", "fail", certified=True),       # B — false positive
              T("c", "unscorable", certified=True), # B (wrong = not pass)
              T("d", "pass"),                       # C
              T("e", "error"),                      # D
              T("f", "fail")]                       # D
    out = S.score(trials, n_preregistered=6, pass_min=1)
    q = out["two_by_two"]
    assert (q["A"], q["B"], q["C"], q["D"]) == (1, 2, 1, 2)
    assert q["A"] + q["B"] + q["C"] + q["D"] == 6
    assert out["certification_false_positive_ids"] == ["b", "c"]


def test_acceptance_all_three_conditions():
    base = [T(f"p{i}", "pass") for i in range(16)] + [
        T("f1", "fail"), T("f2", "fail"), T("f3", "fail"), T("f4", "fail")]
    ok = S.score(base, n_preregistered=20, pass_min=16)
    assert ok["acceptance"] == {"pass_min_met": True, "no_final_error": True,
                                "no_unexpected_unscorable": True,
                                "accepted": True}
    bad_err = base[:19] + [T("e", "error")]
    out = S.score(bad_err, n_preregistered=20, pass_min=16)
    assert out["acceptance"]["accepted"] is False
    assert out["acceptance"]["no_final_error"] is False
    bad_uns = base[:19] + [T("u", "unscorable")]  # unexpected (기본 False)
    out2 = S.score(bad_uns, n_preregistered=20, pass_min=16)
    assert out2["acceptance"]["no_unexpected_unscorable"] is False
    ok_uns = base[:19] + [T("u", "unscorable", unscorable_expected=True)]
    out3 = S.score(ok_uns, n_preregistered=20, pass_min=16)
    assert out3["acceptance"]["no_unexpected_unscorable"] is True
    assert out3["acceptance"]["pass_min_met"] is True


def test_expected_unscorable_still_lowers_ucr():
    """UNSCORABLE ≠ 의미 실패이지만 UCR 분모에서 빠지지도 않는다 —
    '측정 불완전성을 성공처럼 회계하지 않는다'가 UCR의 존재 이유."""
    trials = [T(f"p{i}", "pass") for i in range(10)] + [
        T(f"u{i}", "unscorable", unscorable_expected=True) for i in range(10)]
    out = S.score(trials, n_preregistered=20, pass_min=16)
    assert out["metrics"]["UCR"] == pytest.approx(0.5)
    assert out["acceptance"]["pass_min_met"] is False


def test_refuses_row_count_mismatch():
    """행 손실은 조용한 분모 조작이다 — 전수 아니면 거부."""
    with pytest.raises(ValueError):
        S.score([T("a", "pass")], n_preregistered=2, pass_min=1)
    with pytest.raises(ValueError):
        S.score([T("a", "pass"), T("a", "pass")], n_preregistered=2,
                pass_min=1)  # 중복 id도 거부


def test_refuses_unknown_result_vocabulary():
    with pytest.raises(ValueError):
        S._assert_trial_rows_wellformed(
            [T("a", "PASSED")], n_preregistered=1)


def test_score_is_pure_and_deterministic():
    trials = [T("a", "pass", certified=True), T("b", "fail")]
    assert S.score(trials, n_preregistered=2, pass_min=1) == \
           S.score(trials, n_preregistered=2, pass_min=1)


def test_report_records_its_own_parameters():
    out = S.score([T("a", "pass")], n_preregistered=1, pass_min=1)
    assert out["parameters"] == {"n_preregistered": 1, "pass_min": 1}
    assert out["counts"]["pass"] == 1


# ============================================================== ROUND 2 ====
# D-E2E-v1-22 §3·§16: 수용에 stratum floor 추가 — multi_quantifier N=5,
# PASS_min=4. 필요성의 반례(15 PMB PASS + multi 1/5 → 전체 16/20 PASS)는
# 판정 수신 검증 V2에서 이 모듈로 실측했다. 기존 시그니처의 무-floor 호출은
# 정확히 이전과 같아야 한다(ROUND 1 테스트 전부 불변).


def TS(tid, result, stratum=None, certified=False):
    return {"trial_id": tid, "result": result, "certified": certified,
            "unscorable_expected": False, "stratum": stratum}


def _mixed(multi_pass):
    """PMB 15 전부 PASS + multi 5건 중 multi_pass개 PASS."""
    rows = [TS(f"p{i}", "pass", "PMB") for i in range(15)]
    rows += [TS(f"m{i}", "pass", "multi_quantifier") for i in range(multi_pass)]
    rows += [TS(f"mf{i}", "fail", "multi_quantifier")
             for i in range(5 - multi_pass)]
    return rows


def test_ruling_counterexample_now_fails_with_stratum_floor():
    """D-22 §3의 반례 그대로: 전체 16/20인데 multi 1/5 → floor가 잡아야 한다."""
    out = S.score(_mixed(1), n_preregistered=20, pass_min=16,
                  stratum_floors={"multi_quantifier": (5, 4)})
    assert out["metrics"]["UCR"] == pytest.approx(16 / 20)
    assert out["acceptance"]["stratum_floors_met"] is False
    assert out["acceptance"]["accepted"] is False


def test_floor_met_at_four_of_five():
    out = S.score(_mixed(4), n_preregistered=20, pass_min=16,
                  stratum_floors={"multi_quantifier": (5, 4)})
    assert out["acceptance"]["stratum_floors_met"] is True
    assert out["acceptance"]["accepted"] is True
    assert out["strata"]["multi_quantifier"] == {"n": 5, "pass": 4}


def test_missing_stratum_rows_refused():
    """floor가 선언된 stratum의 행이 N_min보다 적으면 조용한 회피다 — 거부."""
    rows = [TS(f"p{i}", "pass", "PMB") for i in range(17)] + [
        TS(f"m{i}", "pass", "multi_quantifier") for i in range(3)]
    with pytest.raises(ValueError):
        S.score(rows, n_preregistered=20, pass_min=16,
                stratum_floors={"multi_quantifier": (5, 4)})


def test_no_floor_call_is_byte_identical_to_round_one_behaviour():
    rows = [TS("a", "pass"), TS("b", "fail")]
    out = S.score(rows, n_preregistered=2, pass_min=1)
    assert out["acceptance"] == {"pass_min_met": True, "no_final_error": True,
                                 "no_unexpected_unscorable": True,
                                 "accepted": True}, (
        "floor 미지정 호출의 acceptance 형태가 ROUND 1과 달라졌다")


def test_stratum_floor_parameters_are_recorded():
    out = S.score(_mixed(4), n_preregistered=20, pass_min=16,
                  stratum_floors={"multi_quantifier": (5, 4)})
    assert out["parameters"]["stratum_floors"] == {
        "multi_quantifier": [5, 4]} or out["parameters"]["stratum_floors"] == {
        "multi_quantifier": (5, 4)}
