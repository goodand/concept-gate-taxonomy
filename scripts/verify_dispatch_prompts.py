#!/usr/bin/env python3
"""dispatch 인자의 프롬프트가 plan과 **바이트 동일**한지 확인한다.

## 왜 이것이 필요한가 (실측)

2026-08-24, 코호트 20건 dispatch 직전. plan에서 인자를 내보내는 대신 내가
template을 손으로 재구성해 Workflow에 넘기려 했다. 재구성본과 plan을 대조하니
**20건 전건 바이트 불일치**였다 -- 문장 뒤 개행이 하나 모자랐다. 정정한 뒤에야
20/20이 됐다.

그대로 dispatch했다면 **사전등록된 프롬프트가 아닌 것으로 코호트를 돌렸을
것이고**, 산출은 계약 밖 재료가 된다. `trials_raw`에는 프롬프트가 저장되지
않으므로 사후에 그 사실을 알아낼 방법도 없었다. 그래서 dispatch **전에**
기계로 막는다.

## 이 게이트는 정규화하지 않는다 -- 인용 검사기와 정반대다

`scripts/verify_finding_citations.py`는 공백·ANSI·인용부호를 정규화한다.
거기서는 오발이 비용이고 의미가 같으면 같은 것으로 봐야 한다.

**여기서는 정규화가 곧 결함 은닉이다.** 개행 하나 차이가 정확히 이 게이트가
잡아야 하는 것이고, 실제로 그것이 일어났다. 두 게이트가 같은 저장소에 있으면서
반대 규율을 갖는 이유를 여기 적어 둔다 -- 나중에 "일관성"을 이유로 한쪽에
맞추면 이 게이트가 죽는다. 문자열 비교는 `==`로만 한다: `strip()`·`split()`·
정규식 치환·대소문자 폴딩은 여기서 일절 쓰지 않는다.

두 게이트의 차이는 스타일이 아니라 **목표 정밀도**다. 정규화는 "구별하지 않을
세계를 늘리는 것"이고, 오라클의 세기는 곧 **배제하는 틀린 세계의 수**다. 인용
검사기에서는 그 약화가 이득이다(오발 비용이 크고 구별할 필요 없는 차이).
여기서는 그 약화가 **잡아야 할 유일한 것을 지운다** — 개행 하나가 사전등록
위반의 전부다. 그래서 "일관성"을 이유로 한쪽에 맞추자는 논거는 성립하지
않는다: 일관성은 코드 모양에 대한 것이고 **강도는 대상이 정한다**.

## 무엇을 검사하고 무엇을 못 하는가

**한다**: 넘길 인자(`{"trials":[{trial_id, prompt}...]}`)의 모든 프롬프트가
plan의 같은 `trial_id` 프롬프트와 바이트 동일한지. 누락·초과 trial도 잡는다.

**못 한다**: 내가 이 검사를 **부르지 않는 것**은 막지 못한다. 그래서 HANDOFF
§3의 dispatch 절차에 호출을 넣었다 -- 기제 하나가 규율 하나를 대체하지 못하고,
줄일 수 있는 것은 "잊었다"가 아니라 "몰랐다"뿐이다.

Stdlib only, per this repo's convention for tooling that must run anywhere.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

VERDICTS = ("ALL_VERBATIM", "MISMATCH", "INCOMPLETE")
NORMALIZES = False  # 이 게이트의 정체 -- 위 docstring 참조. 절대 True로 바꾸지 마라.


class PlanIntegrityError(Exception):
    """plan 자체가 자기모순이라 어느 프롬프트가 정본인지 알 수 없을 때."""


def load_plan_prompts(plan_path) -> dict[str, str]:
    """plan JSON의 trials에서 {trial_id: prompt}.

    trial_id 중복이면 PlanIntegrityError -- 중복은 어느 쪽이 정본인지
    plan 자신도 모른다는 뜻이라, 침묵하고 하나를 고르는 대신 거부한다.
    """
    data = json.loads(Path(plan_path).read_text(encoding="utf-8"))
    trials = data["trials"] if isinstance(data, dict) else data
    prompts: dict[str, str] = {}
    for t in trials:
        tid = t["trial_id"]
        if tid in prompts:
            raise PlanIntegrityError(
                f"duplicate trial_id in plan: {tid!r} -- 정본을 알 수 없다"
            )
        prompts[tid] = t["prompt"]
    return prompts


def _first_mismatch_context(a: str, b: str, width: int = 40) -> tuple[str, str, int]:
    """a, b가 처음으로 다른 문자 위치와 그 주변을 (a쪽, b쪽, 위치)로 반환."""
    n = min(len(a), len(b))
    pos = n
    for i in range(n):
        if a[i] != b[i]:
            pos = i
            break
    start = max(0, pos - width // 2)
    return a[start:pos + width // 2], b[start:pos + width // 2], pos


def verify(args: dict, plan_prompts: dict[str, str]) -> dict:
    """args의 프롬프트를 plan_prompts와 바이트 단위로 대조한다.

    반환: {"verdict", "checked", "mismatched", "missing", "extra"}

    판정 우선순위: mismatched가 있으면 MISMATCH (내용 오염이 누락보다
    조용하므로 우선한다) / 아니면 missing·extra가 있으면 INCOMPLETE / 아니면
    ALL_VERBATIM.
    """
    trials = args["trials"] if isinstance(args, dict) else args
    arg_prompts: dict[str, str] = {}
    for t in trials:
        arg_prompts[t["trial_id"]] = t["prompt"]

    plan_ids = set(plan_prompts)
    arg_ids = set(arg_prompts)
    common = plan_ids & arg_ids

    mismatched = sorted(
        tid for tid in common if plan_prompts[tid] != arg_prompts[tid]
    )
    missing = sorted(plan_ids - arg_ids)
    extra = sorted(arg_ids - plan_ids)

    if mismatched:
        verdict = "MISMATCH"
    elif missing or extra:
        verdict = "INCOMPLETE"
    else:
        verdict = "ALL_VERBATIM"

    return {
        "verdict": verdict,
        "checked": len(common),
        "mismatched": mismatched,
        "missing": missing,
        "extra": extra,
    }


def _visualize(s: str) -> str:
    return s.replace("\n", "\\n")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} <plan.json> <dispatch_args.json>", file=sys.stderr)
        return 2

    plan_path, args_path = argv[1], argv[2]
    plan_prompts = load_plan_prompts(plan_path)
    args = json.loads(Path(args_path).read_text(encoding="utf-8"))
    result = verify(args, plan_prompts)

    print(f"verdict: {result['verdict']}")
    print(f"checked: {result['checked']}")

    if result["mismatched"]:
        print(f"mismatched ({len(result['mismatched'])}): {result['mismatched']}")
        args_trials = args["trials"] if isinstance(args, dict) else args
        arg_prompts = {t["trial_id"]: t["prompt"] for t in args_trials}
        for tid in result["mismatched"]:
            plan_ctx, arg_ctx, pos = _first_mismatch_context(
                plan_prompts[tid], arg_prompts[tid]
            )
            print(f"  {tid}: first diff at char {pos}")
            print(f"    plan: ...{_visualize(plan_ctx)}...")
            print(f"    args: ...{_visualize(arg_ctx)}...")

    if result["missing"]:
        print(f"missing ({len(result['missing'])}): {result['missing']}")
    if result["extra"]:
        print(f"extra ({len(result['extra'])}): {result['extra']}")

    return 0 if result["verdict"] == "ALL_VERBATIM" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
