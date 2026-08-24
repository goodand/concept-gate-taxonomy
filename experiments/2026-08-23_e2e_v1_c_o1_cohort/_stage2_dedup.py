"""FIXTURE_DEDUP_V1 — Stage2 fixture 후보 분할 (D-E2E-v1-31 Q31.3 계약 구현).

같은 표면(text_sha256) 안에서 gold_sha256이 전원 같으면 실제로 같은 trial이라
하나만 남기고(exact_duplicate) 나머지를 collapse한다. 하나라도 다르면 채점
기준이 둘인 것이므로, 어느 gold를 고르는 순간 선별 단계가 oracle의 모호성을
대신 해결해 버린다 — 그 판단은 선별의 권한이 아니라서 그룹 전원을
oracle_collision으로 부적격 처리하고 대표자를 고르지 않는다. 섞인 그룹(exact
쌍 + 상이 gold)도 gold 종류가 2개 이상이면 전체가 충돌이라 취급한다(일부만
collapse하면 남은 대표자 선택이 임의가 된다).
"""
from __future__ import annotations

DEDUP_PROFILE_ID = "FIXTURE_DEDUP_V1"

_REQUIRED_KEYS = ("item_id", "text_sha256", "gold_sha256")


def _validate(items: list) -> None:
    # 입력 계약 위반은 조용히 넘기지 않는다: 필수 키 누락이나 item_id 중복은
    # 그 자체로 신원이 깨진 것이라 이후 대표자 선택이 무의미해진다.
    seen_ids: set = set()
    for it in items:
        if any(k not in it for k in _REQUIRED_KEYS):
            raise ValueError(f"필수 키 누락: {_REQUIRED_KEYS}")
        if it["item_id"] in seen_ids:
            raise ValueError(f"중복 item_id: {it['item_id']}")
        seen_ids.add(it["item_id"])


def partition(items: list) -> dict:
    _validate(items)

    # 표면 텍스트로 묶는다. dict 삽입 순서로 최초 등장 순서를 보존해
    # 유일한 표면 항목이 입력 순서대로 eligible에 나오게 한다.
    groups: dict = {}
    for it in items:
        groups.setdefault(it["text_sha256"], []).append(it)

    eligible: list = []
    collapsed: list = []
    collisions: list = []

    for group in groups.values():
        golds = {g["gold_sha256"] for g in group}
        if len(group) == 1:
            eligible.append(dict(group[0]))
        elif len(golds) == 1:
            # Case A: 동일 표면 + 동일 gold → 대표자는 결정적 규칙(최소
            # item_id)으로 고른다. 입력 순서에 의존하지 않기 위해서다.
            rep = min(group, key=lambda g: g["item_id"])
            eligible.append(dict(rep))
            for g in group:
                if g["item_id"] != rep["item_id"]:
                    c = dict(g)
                    c["represented_by"] = rep["item_id"]
                    c["reason"] = "exact_duplicate"
                    collapsed.append(c)
        else:
            # Case B: gold가 2종 이상 섞인 그룹은 전체가 oracle 충돌이다.
            # exact 쌍이 섞여 있어도 대표자를 고르지 않는다 — 하나를 남기면
            # 그 선택이 곧 oracle의 모호성을 임의로 해소하는 셈이 된다.
            for g in group:
                c = dict(g)
                c["reason"] = "oracle_collision"
                collisions.append(c)

    return {"eligible": eligible, "collapsed": collapsed, "collisions": collisions}


def summary(partition_result: dict) -> dict:
    e = len(partition_result["eligible"])
    c = len(partition_result["collapsed"])
    x = len(partition_result["collisions"])
    return {
        "profile": DEDUP_PROFILE_ID,
        "input": e + c + x,  # 회계 불변식: 입력 전체의 분할이므로 합으로 역산
        "eligible": e,
        "collapsed": c,
        "collisions": x,
    }
