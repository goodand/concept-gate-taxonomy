"""GATE_C_AUDIT_TABLE_V1 — Gate C 사람 감사용 3열 대조표 (D-E2E-v1-29 §17).

계약 전문은 `test_stage2_gate_c_table.py`의 docstring이 정본이다.

이 표는 **세 독립 신호의 교차 검사**다: 표면(사람이 읽는 것) · MRS 술어
(gold가 말하는 것) · 층 배정(우리가 주장하는 것). Q28의 실패(표면 `most`를
최상급과 구별 못 해 비례 층 오분류)는 세 신호 중 둘만 봤기 때문에 통과했다.

표가 전부 CONSISTENT여도 **자동 통과가 아니다** — Gate C는 정의상 사람
감사이고(D-27/D-28), 이 표는 감사자의 입력이지 감사자의 대체가 아니다.
"""
from __future__ import annotations

import hashlib

GATE_C_PROFILE_ID = "GATE_C_AUDIT_TABLE_V1"

SURFACE_DISPLAY_MODES = ("full", "sha256")

# 층을 결정하는 술어. 층 이름 → 그 층임을 증명하는 MRS 술어 판별.
_STRATUM_DECIDERS = {
    "cardinal": lambda p: p == "card",
    "proportional": lambda p: p == "_most_q",
}


def _decide(candidate: dict) -> str | None:
    """이 후보의 층을 **증명하는** MRS 술어. 없으면 None."""
    stratum = candidate["stratum"]
    test = _STRATUM_DECIDERS[stratum]
    for pred in candidate.get("mrs_preds", []):
        if test(pred):
            return pred
    return None


def _surface(candidate: dict, mode: str) -> tuple:
    if mode == "full":
        return candidate["surface"], False
    # 제한된 재료(예: WSJ/LDC) 경로 — 표면형을 커밋하지 않고도 표가 성립한다.
    digest = hashlib.sha256(candidate["surface"].encode("utf-8")).hexdigest()
    return digest, True


def audit_row(candidate: dict, *, surface_display: str) -> dict:
    """한 후보의 감사 행.

    `surface_display`는 키워드 전용이며 **기본값이 없다** — 제한된 재료의
    문장 원문을 저장소에 커밋할 수 있는지가 미결 판정 항목이므로, 호출자가
    매번 명시해야 한다.
    """
    if surface_display not in SURFACE_DISPLAY_MODES:
        raise ValueError(
            f"surface_display must be one of {SURFACE_DISPLAY_MODES}, "
            f"got {surface_display!r}")
    if candidate["stratum"] not in _STRATUM_DECIDERS:
        raise ValueError(
            f"unknown stratum {candidate['stratum']!r} — "
            f"알려진 층: {sorted(_STRATUM_DECIDERS)}. 미지의 층을 통과시키면 "
            f"교차 검사가 공허해진다")

    decider = _decide(candidate)
    reading, withheld = _surface(candidate, surface_display)
    return {
        "case_id": candidate["case_id"],
        "surface_reading": reading,
        "surface_withheld": withheld,
        "mrs_predicate": decider,
        "assigned_stratum": candidate["stratum"],
        "verdict": "CONSISTENT" if decider else "STRATUM_MRS_MISMATCH",
    }


def audit_table(candidates: list, *, surface_display: str) -> list:
    """후보 순서를 보존한다 — 정렬은 감사자가 읽는 순서를 바꾼다."""
    return [audit_row(c, surface_display=surface_display) for c in candidates]


_COLUMNS = ("case_id", "surface_reading", "mrs_predicate",
            "assigned_stratum", "verdict")


def render_markdown(rows: list) -> str:
    out = ["| " + " | ".join(_COLUMNS) + " |",
           "|" + "|".join(["---"] * len(_COLUMNS)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(
            str(r[c]) if r[c] is not None else "(없음)" for c in _COLUMNS) + " |")
    return "\n".join(out)


def audit_summary(rows: list) -> dict:
    mismatch = sum(1 for r in rows if r["verdict"] != "CONSISTENT")
    return {"profile": GATE_C_PROFILE_ID,
            "total": len(rows),
            "mismatch": mismatch,
            # 표가 초록이어도 사람 감사다 — 이 값은 상수다.
            "gate": "HUMAN_AUDIT_REQUIRED"}
