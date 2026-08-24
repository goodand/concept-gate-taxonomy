"""dispatch 인자의 프롬프트가 plan과 **바이트 동일**한지 확인한다.

## 왜 이것이 필요한가 (실측)

2026-08-24, 코호트 20건 dispatch 직전. plan에서 인자를 내보내는 대신 내가
template을 손으로 재구성해 Workflow에 넘기려 했다. 재구성본과 plan을 대조하니
**20건 전건 바이트 불일치**였다 — 문장 뒤 개행이 하나 모자랐다. 정정한 뒤에야
20/20이 됐다.

그대로 dispatch했다면 **사전등록된 프롬프트가 아닌 것으로 코호트를 돌렸을
것이고**, 산출은 계약 밖 재료가 된다. `trials_raw`에는 프롬프트가 저장되지
않으므로 사후에 그 사실을 알아낼 방법도 없었다. 그래서 dispatch **전에**
기계로 막는다.

## 이 게이트는 정규화하지 않는다 — 인용 검사기와 정반대다

`scripts/verify_finding_citations.py`는 공백·ANSI·인용부호를 정규화한다.
거기서는 오발이 비용이고 의미가 같으면 같은 것으로 봐야 한다.

**여기서는 정규화가 곧 결함 은닉이다.** 개행 하나 차이가 정확히 이 게이트가
잡아야 하는 것이고, 실제로 그것이 일어났다. 두 게이트가 같은 저장소에 있으면서
반대 규율을 갖는 이유를 여기 적어 둔다 — 나중에 "일관성"을 이유로 한쪽에
맞추면 이 게이트가 죽는다.

## 무엇을 검사하고 무엇을 못 하는가

**한다**: 넘길 인자(`{"trials":[{trial_id, prompt}...]}`)의 모든 프롬프트가
plan의 같은 `trial_id` 프롬프트와 바이트 동일한지. 누락·초과 trial도 잡는다.

**못 한다**: 내가 이 검사를 **부르지 않는 것**은 막지 못한다. 그래서 HANDOFF
§3의 dispatch 절차에 호출을 넣었다 — 기제 하나가 규율 하나를 대체하지 못하고,
줄일 수 있는 것은 "잊었다"가 아니라 "몰랐다"뿐이다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import verify_dispatch_prompts as vdp  # noqa: E402


PLAN = {
    "cohort_version": "SEED-x",
    "provenance": {"model": "haiku"},
    "trials": [
        {"trial_id": "T-01", "case_id": "C1", "prompt": "SENTENCE: a.\n\nBODY"},
        {"trial_id": "T-02", "case_id": "C2", "prompt": "SENTENCE: b.\n\nBODY"},
    ],
}


def _plan_file(tmp_path: Path, plan=None) -> Path:
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(plan or PLAN, ensure_ascii=False), encoding="utf-8")
    return p


# ---- 계약 선언 ---------------------------------------------------------

def test_verdict_vocabulary_is_closed():
    assert vdp.VERDICTS == ("ALL_VERBATIM", "MISMATCH", "INCOMPLETE")


def test_the_module_declares_that_it_does_not_normalize():
    """정규화 금지가 이 게이트의 정체다 — 문서에 박아 둔다."""
    assert vdp.NORMALIZES is False


# ---- plan 로드 ---------------------------------------------------------

def test_plan_prompts_are_loaded_by_trial_id(tmp_path):
    got = vdp.load_plan_prompts(_plan_file(tmp_path))
    assert got == {"T-01": "SENTENCE: a.\n\nBODY",
                   "T-02": "SENTENCE: b.\n\nBODY"}


def test_duplicate_trial_ids_in_plan_are_refused(tmp_path):
    bad = {"trials": [{"trial_id": "T-01", "prompt": "x"},
                      {"trial_id": "T-01", "prompt": "y"}]}
    with pytest.raises(vdp.PlanIntegrityError):
        vdp.load_plan_prompts(_plan_file(tmp_path, bad))


# ---- 판정 --------------------------------------------------------------

def test_identical_prompts_pass(tmp_path):
    args = {"trials": [dict(t) for t in PLAN["trials"]]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "ALL_VERBATIM"
    assert out["checked"] == 2


def test_a_single_missing_newline_is_caught(tmp_path):
    """G130 그 자체 — 개행 하나가 20/20 불일치를 만들었다."""
    args = {"trials": [
        {"trial_id": "T-01", "prompt": "SENTENCE: a.\nBODY"},   # 개행 1개 부족
        {"trial_id": "T-02", "prompt": "SENTENCE: b.\n\nBODY"},
    ]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "MISMATCH"
    assert out["mismatched"] == ["T-01"]


def test_trailing_whitespace_is_a_mismatch_not_a_pass(tmp_path):
    """정규화하면 통과할 것 — 여기서는 실패해야 한다."""
    args = {"trials": [
        {"trial_id": "T-01", "prompt": "SENTENCE: a.\n\nBODY "},
        {"trial_id": "T-02", "prompt": "SENTENCE: b.\n\nBODY"},
    ]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "MISMATCH"


def test_missing_trial_is_incomplete(tmp_path):
    args = {"trials": [dict(PLAN["trials"][0])]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "INCOMPLETE"
    assert out["missing"] == ["T-02"]


def test_unknown_trial_id_is_incomplete(tmp_path):
    args = {"trials": [dict(PLAN["trials"][0]), dict(PLAN["trials"][1]),
                       {"trial_id": "T-99", "prompt": "invented"}]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "INCOMPLETE"
    assert out["extra"] == ["T-99"]


def test_mismatch_wins_over_incomplete_when_both(tmp_path):
    """둘 다면 더 위험한 쪽을 보고한다 — 내용 오염이 누락보다 조용하다."""
    args = {"trials": [{"trial_id": "T-01", "prompt": "다른 내용"}]}
    out = vdp.verify(args, vdp.load_plan_prompts(_plan_file(tmp_path)))
    assert out["verdict"] == "MISMATCH"
    assert out["missing"] == ["T-02"]


# ---- 실물 회귀 ---------------------------------------------------------

def test_the_real_cohort_plan_is_self_consistent():
    """동결된 코호트 plan을 자기 자신과 대조하면 통과해야 한다."""
    plan = (ROOT / "experiments" / "2026-08-23_e2e_v1_c_o1_cohort"
            / "stage2_cohort_plan_v5.json")
    if not plan.exists():
        pytest.skip("코호트 plan이 없는 체크아웃")
    prompts = vdp.load_plan_prompts(plan)
    assert len(prompts) == 20
    args = {"trials": [{"trial_id": k, "prompt": v} for k, v in prompts.items()]}
    assert vdp.verify(args, prompts)["verdict"] == "ALL_VERBATIM"


def test_the_hand_reconstructed_template_is_still_caught():
    """G130 실물 — 내가 손으로 만든 template(개행 1개 부족)을 실제 plan에 대고
    돌리면 20건 전건이 잡혀야 한다. 이 테스트가 그 실패를 영구 보존한다."""
    plan = (ROOT / "experiments" / "2026-08-23_e2e_v1_c_o1_cohort"
            / "stage2_cohort_plan_v5.json")
    if not plan.exists():
        pytest.skip("코호트 plan이 없는 체크아웃")
    prompts = vdp.load_plan_prompts(plan)
    # 당시의 오류를 재현한다: SENTENCE 줄 뒤 빈 줄 하나를 없앤다
    reconstructed = [
        {"trial_id": k, "prompt": v.replace("\n\nIR DIALECT", "\nIR DIALECT", 1)}
        for k, v in prompts.items()
    ]
    out = vdp.verify({"trials": reconstructed}, prompts)
    assert out["verdict"] == "MISMATCH"
    assert len(out["mismatched"]) == 20
