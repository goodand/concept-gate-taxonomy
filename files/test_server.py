"""ConceptGate MCP 서버 단위 테스트.

두 레벨로 검증:
  PART 1. 함수 직접 호출 — server.run_pipeline([...]) 등 (MCP 프로토콜 우회)
  PART 2. FastMCP Client in-memory — 실제 MCP 프로토콜 레벨 (tools/resources/prompts)

실행: .venv/bin/python test_server.py
"""

import asyncio
import json
import sys

import server
from fastmcp import Client


passed = 0
failed = 0


def check(label, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        print(f"  ✗ {label}  {detail}")


# 표준 입력 데이터
DOG_CAT = [
    {"name": "개", "features": [{"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}]},
    {"name": "고양이", "features": [{"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}]},
]

SQUARE = [
    {"name": "사각형", "features": [
        {"feature": "4변", "type": "essential_feature", "evidence": "네 개의 변을 가짐"},
        {"feature": "4각", "type": "essential_feature", "evidence": "네 개의 꼭짓점"}]},
    {"name": "직사각형", "features": [
        {"feature": "4변", "type": "essential_feature", "evidence": "네 개의 변을 가짐"},
        {"feature": "4각", "type": "essential_feature", "evidence": "네 개의 꼭짓점"},
        {"feature": "직각", "type": "essential_feature", "evidence": "네 각이 모두 직각"}]},
    {"name": "마름모", "features": [
        {"feature": "4변", "type": "essential_feature", "evidence": "네 개의 변을 가짐"},
        {"feature": "4각", "type": "essential_feature", "evidence": "네 개의 꼭짓점"},
        {"feature": "등변", "type": "essential_feature", "evidence": "네 변의 길이가 같음"}]},
    {"name": "정사각형", "features": [
        {"feature": "4변", "type": "essential_feature", "evidence": "네 개의 변을 가짐"},
        {"feature": "4각", "type": "essential_feature", "evidence": "네 개의 꼭짓점"},
        {"feature": "직각", "type": "essential_feature", "evidence": "네 각이 모두 직각"},
        {"feature": "등변", "type": "essential_feature", "evidence": "네 변의 길이가 같음"}]},
]

TOMATO = [
    {"name": "토마토", "features": [
        {"feature": "생물", "type": "essential_feature", "evidence": "생명 활동을 하는 존재"},
        {"feature": "요리분류", "type": "essential_feature", "evidence": "요리에서 채소로 사용됨"}]},
]


# ═══════════════════════════════════════════════════════
# PART 1. 함수 직접 호출
# ═══════════════════════════════════════════════════════

def test_direct():
    print("\n[PART 1] 함수 직접 호출")

    # 1-1. run_pipeline 정상
    out = server.run_pipeline(DOG_CAT)
    check("1-1 개·고양이 → PASS_WITH_WARNING", out["status"] == "PASS_WITH_WARNING")
    check("1-2 expansion_actions 존재", len(out["expansion_actions"]) > 0)
    check("1-3 출력 JSON 직렬화 가능", _json_ok(out))

    # 1-4. ParseGate 경유 — 비정상 입력 거부
    bad = server.run_pipeline([{"name": "x", "features": [{"feature": "a", "type": "essential_feature", "evidence": 999}]}])
    check("1-4 evidence 비문자열 → FAIL", bad["status"] == "FAIL" and "errors" in bad)
    check("1-5 에러 구조화 (gate/message)",
          all("gate" in e and "message" in e for e in bad["errors"]))

    # 1-6. 정사각형 meet
    sq = server.run_pipeline(SQUARE)
    check("1-6 정사각형 → PASS", sq["status"] == "PASS")
    sq_def = sq["definitions"].get("정사각형", {})
    check("1-7 정사각형 is_meet + parents",
          sq_def.get("is_meet") and sorted(sq_def.get("parents", [])) == ["마름모", "직사각형"])

    # 1-8. aux_relations 직렬화 (tuple key → list)
    tom = server.run_pipeline(TOMATO)
    check("1-8 토마토 aux_relations는 list",
          isinstance(tom["aux_relations"], list))
    check("1-9 토마토 repairs 직렬화", _json_ok(tom) and isinstance(tom["repairs"], list))

    # 1-10. expand — 종차 추가 → 수렴
    exp = server.expand(DOG_CAT, [
        {"concept": "개", "new_features": [{"feature": "가축화", "type": "essential_feature", "evidence": "인간에 의해 가축화된 동물"}]},
        {"concept": "고양이", "new_features": [{"feature": "독립성", "type": "essential_feature", "evidence": "독립적 생활이 가능한 동물"}]},
    ])
    check("1-10 expand 종차 추가 → PASS", exp["status"] == "PASS", f"got {exp['status']}")

    # 1-11. expand — 스키마 위반
    bad_exp = server.expand(DOG_CAT, [{"concept": "개"}])  # new_features 없음
    check("1-11 expand new_features 누락 → PARSE_FAIL", bad_exp["status"] == "PARSE_FAIL")
    check("1-12 PARSE_FAIL 에러 구조화",
          "errors" in bad_exp and all("gate" in e for e in bad_exp["errors"]))

    # 1-13. classify_parents
    cp = server.classify_parents(SQUARE)
    check("1-13 정사각형 → [마름모, 직사각형]",
          cp["parent_candidates"].get("정사각형") == ["마름모", "직사각형"],
          f"got {cp['parent_candidates'].get('정사각형')}")

    # 1-14. export_graph 4종
    m = server.export_graph(SQUARE, "mermaid")
    check("1-14 export mermaid", m["format"] == "mermaid" and m["content"].startswith("graph TD"))
    j = server.export_graph(SQUARE, "json")
    check("1-15 export json (파싱 가능)", json.loads(j["content"]) is not None)
    g = server.export_graph(SQUARE, "graphml")
    check("1-16 export graphml", "graphml" in g["content"])
    s = server.export_graph(SQUARE, "summary")
    check("1-17 export summary (edge=4)", s["content"]["edge_count"] == 4)
    bad_fmt = server.export_graph(SQUARE, "xml")
    check("1-18 export 잘못된 format → error", "error" in bad_fmt)

    # 1-19. analyze_expansion
    an = server.analyze_expansion([
        {"round": 0, "status": "PASS_WITH_WARNING", "n_concepts": 3, "n_actions": 1},
        {"round": 1, "status": "PASS", "n_concepts": 3, "n_actions": 0},
    ])
    check("1-19 analyze → converged", an["verdict"] == "converged")

    # 1-20. lint_concepts — 정상 입력
    lint_ok = server.lint_concepts(DOG_CAT)
    check("1-20 lint_concepts 정상 입력 → LINT_PASS",
          lint_ok["status"] == "LINT_PASS", f"got {lint_ok['status']}")
    check("1-20b lint_concepts server_meta 포함",
          lint_ok["server_meta"]["input_stats"]["concept_count"] == 2
          and lint_ok["server_meta"]["timing_ms"] >= 0)

    # 1-21. lint_concepts — features 누락
    lint_missing = server.lint_concepts([{"name": "어텐션"}])
    check("1-21 lint_concepts features 누락 → LINT_ERROR",
          lint_missing["status"] == "LINT_ERROR"
          and any(i["code"] == "MISSING_FEATURES" for i in lint_missing["issues"]))

    # 1-22. lint_concepts — 약한 structural evidence
    lint_weak = server.lint_concepts([{"name": "트랜스포머", "features": [
        {"feature": "attention mechanisms",
         "type": "structural_composition",
         "evidence": "Transformer is based on attention mechanisms.",
         "relation_hint": "has_part"}
    ]}])
    check("1-22 lint_concepts weak structural evidence → LINT_WARNING",
          lint_weak["status"] == "LINT_WARNING"
          and any(i["code"] == "WEAK_STRUCTURAL_EVIDENCE" for i in lint_weak["issues"]))

    # 1-23. lint_concepts — 상속 placeholder 금지
    lint_placeholder = server.lint_concepts([{"name": "scaled_dot_product_attention", "features": [
        {"feature": "attention_function features",
         "type": "essential_feature",
         "evidence": "same as above"}
    ]}])
    check("1-23 lint_concepts placeholder feature → LINT_ERROR",
          lint_placeholder["status"] == "LINT_ERROR"
          and any(i["code"] == "PLACEHOLDER_FEATURE" for i in lint_placeholder["issues"]))

    # 1-24. lint_concepts — relation_hint/type 충돌
    lint_conflict = server.lint_concepts([{"name": "자동차", "features": [
        {"feature": "엔진",
         "type": "essential_feature",
         "evidence": "자동차는 엔진을 구성요소로 포함한다",
         "relation_hint": "component_of"}
    ]}])
    check("1-24 lint_concepts relation_hint/type 충돌 → LINT_ERROR",
          lint_conflict["status"] == "LINT_ERROR"
          and any(i["code"] == "RELATION_HINT_TYPE_CONFLICT" for i in lint_conflict["issues"]))

    # 1-25. lint_concepts — 모든 개념 쌍이 essential 라벨 비공유 → edge 0 예고
    lint_disjoint = server.lint_concepts([
        {"name": "어텐션", "features": [
            {"feature": "쿼리키값매핑함수", "type": "essential_feature",
             "evidence": "maps a query and key-value pairs to an output"}]},
        {"name": "멀티헤드어텐션", "features": [
            {"feature": "병렬어텐션수행", "type": "essential_feature",
             "evidence": "we perform the attention function in parallel"}]},
    ])
    check("1-25 lint_concepts 라벨 비공유 → NO_SHARED_ESSENTIAL_LABELS",
          lint_disjoint["status"] == "LINT_WARNING"
          and any(i["code"] == "NO_SHARED_ESSENTIAL_LABELS" for i in lint_disjoint["issues"]))

    # 1-26. lint_concepts — is-a 주장을 feature 문장으로 선언 (다른 개념명 참조)
    lint_isa_claim = server.lint_concepts([
        {"name": "어텐션", "features": [
            {"feature": "쿼리키값매핑함수", "type": "essential_feature",
             "evidence": "maps a query and key-value pairs to an output"}]},
        {"name": "스케일드닷프로덕트어텐션", "features": [
            {"feature": "어텐션이다", "type": "essential_feature",
             "evidence": "we call our particular attention Scaled Dot-Product Attention"}]},
    ])
    check("1-26 lint_concepts is-a 주장 feature → ISA_CLAIM_FEATURE",
          any(i["code"] == "ISA_CLAIM_FEATURE" for i in lint_isa_claim["issues"]))

    # 1-27. lint_concepts — 계약 준수 입력(라벨 verbatim 반복)은 교차 경고 없음
    lint_shared = server.lint_concepts([
        {"name": "어텐션", "features": [
            {"feature": "쿼리키값매핑", "type": "essential_feature",
             "evidence": "maps a query and key-value pairs to an output"}]},
        {"name": "셀프어텐션전용변형", "features": [
            {"feature": "쿼리키값매핑", "type": "essential_feature",
             "evidence": "maps a query and key-value pairs (inherited)"},
            {"feature": "동일시퀀스출처", "type": "essential_feature",
             "evidence": "keys, values and queries come from the same place"}]},
    ])
    cross_codes = {"NO_SHARED_ESSENTIAL_LABELS", "ISA_CLAIM_FEATURE"}
    check("1-27 lint_concepts 계약 준수 입력 → 교차 경고 없음",
          not any(i["code"] in cross_codes for i in lint_shared["issues"]),
          f"got {[i['code'] for i in lint_shared['issues']]}")

    # 1-28. run_pipeline — lint 자동 주입 (클라이언트가 lint_concepts를 건너뛴 경우)
    disjoint_input = [
        {"name": "어텐션", "features": [
            {"feature": "쿼리키값매핑함수", "type": "essential_feature",
             "evidence": "maps a query and key-value pairs to an output"}]},
        {"name": "멀티헤드어텐션", "features": [
            {"feature": "병렬어텐션수행", "type": "essential_feature",
             "evidence": "we perform the attention function in parallel"}]},
    ]
    injected = server.run_pipeline(disjoint_input)
    check("1-28 run_pipeline PASS + 빈 DAG → lint 주입됨",
          injected["status"] == "PASS"
          and not injected["dag"]
          and "lint" in injected
          and any(i["code"] == "NO_SHARED_ESSENTIAL_LABELS" for i in injected["lint"]["issues"]))

    # 1-29. run_pipeline — 깨끗한 입력에는 lint 필드를 붙이지 않음
    clean_out = server.run_pipeline(DOG_CAT)
    check("1-29 run_pipeline 깨끗한 입력 → lint 필드 없음",
          "lint" not in clean_out, f"got keys {sorted(clean_out.keys())}")
    check("1-29b run_pipeline server_meta 포함",
          clean_out["server_meta"]["input_stats"]["concept_count"] == 2
          and clean_out["server_meta"]["input_stats"]["pairwise_comparisons"] == 1
          and clean_out["server_meta"]["timing_ms"] >= 0)

    # 1-30. lint_concepts — 큰 pairwise 입력은 hosted timeout 위험 경고
    large_input = [
        {"name": f"c{i}", "features": [
            {"feature": f"f{i}", "type": "essential_feature", "evidence": "source backed feature"}
        ]}
        for i in range(101)
    ]
    lint_large = server.lint_concepts(large_input)
    check("1-30 lint_concepts 큰 pairwise 입력 → LARGE_PAIRWISE_INPUT",
          any(i["code"] == "LARGE_PAIRWISE_INPUT" for i in lint_large["issues"]))


def _json_ok(obj):
    try:
        json.dumps(obj, ensure_ascii=False)
        return True
    except (TypeError, ValueError):
        return False


# ═══════════════════════════════════════════════════════
# PART 2. FastMCP Client in-memory (실제 MCP 프로토콜)
# ═══════════════════════════════════════════════════════

async def test_mcp_protocol():
    print("\n[PART 2] FastMCP Client in-memory (MCP 프로토콜)")

    async with Client(server.mcp) as client:
        # 2-1. 도구 목록
        tools = await client.list_tools()
        tool_names = {t.name for t in tools}
        check("2-1 도구 6개 등록",
              {"lint_concepts", "run_pipeline", "expand", "classify_parents", "export_graph", "analyze_expansion"} <= tool_names,
              f"got {tool_names}")
        check("2-1b normalizer 도구 3개 등록",
              {"make_snapshot", "lookup_senses", "assemble_concepts"} <= tool_names,
              f"got {tool_names}")

        # 2-2. 리소스 목록
        resources = await client.list_resources()
        res_uris = {str(r.uri) for r in resources}
        check("2-2 리소스 3개 등록",
              {
                  "conceptgate://expansion-schema",
                  "conceptgate://pipeline-status-codes",
                  "conceptgate://client-guide",
              } <= res_uris,
              f"got {res_uris}")
        check("2-2b normalizer 리소스 2개 등록",
              {"normalizer://protocol/v1", "normalizer://relations/v1"} <= res_uris,
              f"got {res_uris}")

        # 2-3. 프롬프트 목록
        prompts = await client.list_prompts()
        prompt_names = {p.name for p in prompts}
        check("2-3 프롬프트 1개 등록", "expansion_prompt" in prompt_names, f"got {prompt_names}")

        # 2-4. run_pipeline 호출 (프로토콜 경유)
        result = await client.call_tool("run_pipeline", {"concepts": DOG_CAT})
        data = result.data
        check("2-4 run_pipeline 프로토콜 호출 → PASS_WITH_WARNING",
              data["status"] == "PASS_WITH_WARNING", f"got {data['status']}")

        # 2-5. expand 호출 (프로토콜 경유)
        result2 = await client.call_tool("expand", {
            "original_concepts": DOG_CAT,
            "expansions": [
                {"concept": "개", "new_features": [{"feature": "가축화", "type": "essential_feature", "evidence": "인간에 의해 가축화된 동물"}]},
                {"concept": "고양이", "new_features": [{"feature": "독립성", "type": "essential_feature", "evidence": "독립적 생활이 가능한 동물"}]},
            ],
        })
        check("2-5 expand 프로토콜 호출 → PASS", result2.data["status"] == "PASS", f"got {result2.data['status']}")

        # 2-6. classify_parents 호출
        result3 = await client.call_tool("classify_parents", {"concepts": SQUARE})
        check("2-6 classify_parents 프로토콜 → 정사각형 meet",
              result3.data["parent_candidates"].get("정사각형") == ["마름모", "직사각형"])

        # 2-7. export_graph 호출
        result4 = await client.call_tool("export_graph", {"concepts": SQUARE, "format": "mermaid"})
        check("2-7 export_graph 프로토콜 → mermaid",
              result4.data["content"].startswith("graph TD"))

        # 2-8. 리소스 읽기
        schema_res = await client.read_resource("conceptgate://expansion-schema")
        schema_text = schema_res[0].text
        check("2-8 expansion-schema 리소스 읽기",
              "expansions" in schema_text)

        status_res = await client.read_resource("conceptgate://pipeline-status-codes")
        check("2-9 pipeline-status-codes 리소스 읽기",
              "PASS_WITH_WARNING" in status_res[0].text)

        guide_res = await client.read_resource("conceptgate://client-guide")
        guide_text = guide_res[0].text
        check("2-10 client-guide 리소스 읽기",
              "source-grounded" in guide_text
              and "missing features" in guide_text
              and "diagnostic only" in guide_text
              and "structural_composition" in guide_text
              and "based on" in guide_text)

        # 2-10. 프롬프트 호출
        prompt_result = await client.get_prompt("expansion_prompt", {
            "action_type": "depth",
            "target_concepts": "개,고양이",
            "shared_attrs": "동물",
        })
        prompt_text = prompt_result.messages[0].content.text
        check("2-11 expansion_prompt 호출",
              "개" in prompt_text and "고양이" in prompt_text)

        # 2-11. 비정상 입력도 프로토콜 통해 FAIL 반환 (예외 아님)
        bad_result = await client.call_tool("run_pipeline", {
            "concepts": [{"name": "x", "features": [{"feature": "a", "type": "essential_feature", "evidence": 999}]}],
        })
        check("2-12 비정상 입력 → FAIL (예외 없이)",
              bad_result.data["status"] == "FAIL")

        # 2-13. lint_concepts 호출
        lint_result = await client.call_tool("lint_concepts", {
            "concepts": [{"name": "x"}],
        })
        check("2-13 lint_concepts 프로토콜 호출 → LINT_ERROR",
              lint_result.data["status"] == "LINT_ERROR"
              and lint_result.data["issues"][0]["code"] == "MISSING_FEATURES")

        # 2-14. run_pipeline 프로토콜 응답에 lint 자동 주입
        inject_result = await client.call_tool("run_pipeline", {
            "concepts": [
                {"name": "어텐션", "features": [
                    {"feature": "쿼리키값매핑함수", "type": "essential_feature",
                     "evidence": "maps a query and key-value pairs to an output"}]},
                {"name": "멀티헤드어텐션", "features": [
                    {"feature": "병렬어텐션수행", "type": "essential_feature",
                     "evidence": "we perform the attention function in parallel"}]},
            ],
        })
        check("2-14 run_pipeline 프로토콜 → lint 주입",
              inject_result.data["status"] == "PASS"
              and "lint" in inject_result.data
              and any(i["code"] == "NO_SHARED_ESSENTIAL_LABELS"
                      for i in inject_result.data["lint"]["issues"]))
        check("2-15 run_pipeline 프로토콜 → server_meta 포함",
              "server_meta" in inject_result.data
              and inject_result.data["server_meta"]["input_stats"]["concept_count"] == 2
              and inject_result.data["server_meta"]["timing_ms"] >= 0)


async def test_normalizer_protocol():
    print("\n[PART 3] Normalizer surface (자연어 → evidence-carrying concepts)")

    async with Client(server.mcp) as client:
        # 3-1. protocol resource 읽기
        proto = await client.read_resource("normalizer://protocol/v1")
        proto_text = proto[0].text
        check("3-1 protocol resource에 단계 순서 명시",
              "make_snapshot" in proto_text and "assemble_concepts" in proto_text)

        # 3-2. relation crosswalk resource — feature_activity는 unmapped
        rel = await client.read_resource("normalizer://relations/v1")
        rel_data = json.loads(rel[0].text)
        check("3-2 crosswalk: feature_activity → unmapped",
              rel_data["crosswalk"]["feature_activity"]["mapping_status"] == "unmapped")
        check("3-2b crosswalk: stuff_object → material_of / structural",
              rel_data["crosswalk"]["stuff_object"]["relation_hint"] == "material_of"
              and rel_data["crosswalk"]["stuff_object"]["feature_type"]
              == "structural_composition")

        # 3-3. make_snapshot → 결정론 해시
        snap = (await client.call_tool(
            "make_snapshot", {"text": "개는 갯과의 가축화된 동물이다."})).data
        check("3-3 make_snapshot → sha256 고정", snap["ok"] and
              len(snap["snapshot"]["sha256"]) == 64)

        # 3-4. lookup_senses → 다의어 후보
        senses = (await client.call_tool("lookup_senses", {"surface": "개"})).data
        check("3-4 lookup_senses: 개 → 2 sense 후보", len(senses["candidates"]) == 2)

        # 3-5. assemble_concepts happy-path → lint 통과 concepts
        t = snap["snapshot"]["text"]
        j = t.find("가축화된 동물이다")
        i = t.find("갯과의 가축화된")
        bundle = {"snapshot": snap["snapshot"], "concepts": [
            {"name": "동물", "features": [
                {"label": "동물", "relation": "is_a",
                 "evidence_span": {"start": j, "end": j + 9}}]},
            {"name": "개", "features": [
                {"label": "동물", "relation": "is_a",
                 "evidence_span": {"start": j, "end": j + 9}},
                {"label": "갯과", "relation": "is_a",
                 "evidence_span": {"start": i, "end": i + 8}}]},
        ]}
        asm = (await client.call_tool("assemble_concepts", {"bundle": bundle})).data
        check("3-5 assemble → complete + lint 통과",
              asm["ok"] and asm["stage"] == "complete", f"got {asm}")
        check("3-5b 모든 claim이 L1(source_span_verified)",
              all(c["verification_status"] == "source_span_verified"
                  for c in asm["claims"]))

        # 3-6. 조립 산출물이 run_pipeline을 통과 (end-to-end via MCP)
        gate = (await client.call_tool(
            "run_pipeline",
            {"concepts": asm["concepts_json"]["concepts"]})).data
        check("3-6 조립 concepts → run_pipeline PASS + is-a edge",
              gate["status"] == "PASS"
              and gate["dag"].get("동물") == ["개"], f"got {gate['status']}, {gate['dag']}")

        # 3-7. 위조된 span은 selection stage에서 거부 (원인 단계 식별)
        bad = {"snapshot": snap["snapshot"], "concepts": [
            {"name": "개", "features": [
                {"label": "동물", "relation": "is_a",
                 "evidence_span": {"start": 0, "end": 999999}}]}]}
        bad_res = (await client.call_tool("assemble_concepts", {"bundle": bad})).data
        check("3-7 위조 span → selection stage 거부",
              not bad_res["ok"] and bad_res["stage"] == "selection")

        # 3-8. feature_activity 관계는 crosswalk에서 거부
        fa = {"snapshot": snap["snapshot"], "concepts": [
            {"name": "쇼핑", "features": [
                {"label": "지불", "relation": "feature_activity",
                 "evidence_text": "지불은 쇼핑의 일부 활동이다"}]}]}
        fa_res = (await client.call_tool("assemble_concepts", {"bundle": fa})).data
        check("3-8 feature_activity → crosswalk 거부",
              not fa_res["ok"] and fa_res["stage"] == "crosswalk")


# ═══════════════════════════════════════════════════════
# 실행
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    test_direct()
    asyncio.run(test_mcp_protocol())
    asyncio.run(test_normalizer_protocol())

    total = passed + failed
    print(f"\n{'=' * 57}")
    print(f"  통과: {passed}/{total}")
    if failed:
        print(f"  실패: {failed}")
        print(f"{'=' * 57}")
        sys.exit(1)
    else:
        print(f"  전체 통과 ✓")
        print(f"{'=' * 57}")
        sys.exit(0)
