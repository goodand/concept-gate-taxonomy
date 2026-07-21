"""trial 프롬프트 30건 생성 (fixture × arm × 5 replicate).

각 프롬프트는 자기완결적 — subagent는 도구 없이 응답 JSON만 보고 결정한다.
arm view는 make_arm으로 단일 canonical에서 투영(진단 내용 동일, 표현만 다름).
출력: _prompts.json (수집 스크립트가 읽음).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import evaluate as E  # noqa: E402

N_REPLICATE = 5

SCHEMA_DOC = """\
run_pipeline 입력 스키마(참고):
- concepts: [{ "name": str, "features": [ {feature: str, type: str, evidence: str} ], "ontoclean"?: {category, rigidity, identity, unity, dependence} }]
- feature.type 값: essential_feature(is-a DAG 참여) | structural_composition | contextual_usage | locational | functional | social_treatment
- ontoclean.category 예: kind, subkind, role, phase, category. rigidity: rigid | anti_rigid | non_rigid
- is-a 간선은 부모의 essential_feature 라벨 집합이 자식의 진부분집합일 때 형성된다."""

TASK = """\
너는 개념 온톨로지를 다루는 클라이언트 agent다. 한 agent가 아래 [입력]을 개념 검증
도구 run_pipeline에 보냈고, 도구가 아래 [응답]을 돌려줬다. 다음 행동 하나를 선택하라.

선택지(셋 다 동등하게 고려하라):
- report_done: 결과가 신뢰할 만하니 그대로 사용자에게 보고한다.
- repair: 입력을 고쳐 재제출한다. 이때 repaired_concepts에 재제출할 concepts 전체를 넣어라.
- request_evidence: 판정을 확정하기 부족해 추가 근거/메타데이터를 요청한다. request에 무엇이 필요한지 한 줄.

출력은 JSON 하나만, 다른 텍스트 없이:
{"decision": "report_done" | "repair" | "request_evidence",
 "repaired_concepts": [...] 또는 null,
 "request": "..." 또는 null,
 "report": "판단 근거 한 줄"}

%s

[입력]
%s

[응답]
%s
""" % (SCHEMA_DOC, "%s", "%s")


def build():
    data = json.load(open(os.path.join(HERE, "fixture.json"), encoding="utf-8"))
    prompts = []
    for fx in data["fixtures"]:
        _, canon = E.run_and_certify(fx["input_concepts"])
        inp = json.dumps(fx["input_concepts"], ensure_ascii=False, indent=1)
        for arm in fx["arms"]:
            view = E.make_arm(canon, arm)
            resp = json.dumps(view, ensure_ascii=False, indent=1)
            prompt = TASK % (inp, resp)
            for tr in range(1, N_REPLICATE + 1):
                prompts.append({"fixture": fx["id"], "arm": arm,
                                "trial": tr, "prompt": prompt})
    out = os.path.join(HERE, "_prompts.json")
    json.dump({"n": len(prompts), "prompts": prompts},
              open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(prompts)} prompts → {out}")
    # arm별 카운트
    from collections import Counter
    c = Counter((p["fixture"], p["arm"]) for p in prompts)
    for k, v in sorted(c.items()):
        print(f"  {k}: {v}")


if __name__ == "__main__":
    build()
