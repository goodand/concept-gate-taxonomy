"""Stage 1 게이트 — 계측 자격이 PASS 상태로 기록돼 있고 재현되는지.

H1a `_assert_instrument_speaks` 규율: 계측기의 교정이 통과 상태가 아니면
그 계측기의 어떤 출력도 데이터가 아니다. 이 테스트는 (1) 기록된 자격
상태와 (2) 지금 재실행한 자격이 모두 PASS인지 본다 — 기록만 보면 계측기
드리프트를, 재실행만 보면 미기록(사전등록 위반)을 놓친다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_stage1_qualification import CONTROLS_PATH, run_qualification


def test_controls_are_eight_with_expected_distribution():
    corpus = json.loads(CONTROLS_PATH.read_text(encoding="utf-8"))
    from collections import Counter
    dist = Counter(c["expected"] for c in corpus["controls"])
    assert dist == {"pass": 2, "fail": 2, "unscorable": 2, "error": 2}


def test_measurement_qualification_reproduces_as_pass():
    outcome = run_qualification()
    assert outcome["state"] == "passed", outcome["mismatches"]


def test_recorded_state_is_pass_and_results_are_recorded():
    corpus = json.loads(CONTROLS_PATH.read_text(encoding="utf-8"))
    assert corpus["qualification_state"] == "PASS", (
        "Stage 1이 아직 실행·기록되지 않았거나 실패 상태다 — Stage 2 착수 금지")
    assert len(corpus["results"]) == 8
