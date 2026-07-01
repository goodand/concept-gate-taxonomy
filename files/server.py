"""ConceptGate MCP Server

FCA 개념 격자 추론기 v7을 MCP 도구로 노출하는 얇은 adapter.

핵심 원칙: 이 서버는 LLM을 호출하지 않는다.
MCP client(Codex CLI, Claude Desktop, Claude Code 등)가
expansion_actions를 해석하고 expand tool에 종차를 제공한다.

concept_gate_v7.py와 cg_graph_export.py는 import만 하며 수정하지 않는다.
"""

import json
import os
import sys

from fastmcp import FastMCP
from starlette.responses import JSONResponse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from concept_gate_v7 import (  # noqa: E402
    ConceptPipeline,
    ParseGate,
    ExpansionAction,
    ExpansionType,
    ParentCandidateClassifier,
    ExpansionHistoryAnalyzer,
    build_expansion_prompt,
    parse_expansion_response,
    EXPANSION_OUTPUT_SCHEMA,
)
from cg_graph_export import GraphExporter  # noqa: E402

mcp = FastMCP("ConceptGate")


# ═══════════════════════════════════════════════════════
# Bearer Token 인증 미들웨어 (Render 배포용)
# ═══════════════════════════════════════════════════════

from fastmcp.server.middleware import Middleware  # noqa: E402
from fastmcp.server.dependencies import get_http_headers  # noqa: E402
from fastmcp.exceptions import ToolError  # noqa: E402


class BearerTokenAuth(Middleware):
    """MCP_API_TOKEN이 설정되어 있으면 Bearer token을 검증.
    설정 안 되어 있으면 (로컬 개발) 인증 없이 통과."""

    async def on_call_tool(self, context, call_next):
        self._check_token()
        return await call_next(context)

    async def on_read_resource(self, context, call_next):
        self._check_token()
        return await call_next(context)

    async def on_get_prompt(self, context, call_next):
        self._check_token()
        return await call_next(context)

    def _check_token(self):
        expected = os.environ.get("MCP_API_TOKEN")
        if not expected:
            return  # 토큰 미설정 → 인증 안 함 (로컬 개발)
        try:
            headers = get_http_headers(include_all=True)
        except Exception:
            return  # stdio transport에서는 헤더 없음 → 통과
        auth = headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            raise ToolError("Unauthorized: missing Bearer token")
        token = auth.removeprefix("Bearer ").strip()
        if token != expected:
            raise ToolError("Unauthorized: invalid token")


mcp.add_middleware(BearerTokenAuth())


# Health check (Render 서비스 상태 확인)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    return JSONResponse({"status": "healthy", "service": "conceptgate-mcp"})


# ═══════════════════════════════════════════════════════
# 헬퍼: 입력 파싱 (반드시 ParseGate 경유)
# ═══════════════════════════════════════════════════════

def _parse_concepts_or_error(concepts_json):
    """ParseGate를 우회하지 않음. v7의 핵심 방어선 유지."""
    raw = json.dumps({"concepts": concepts_json}, ensure_ascii=False)
    parsed, report = ParseGate.parse(raw)
    if not report.passed:
        return None, {
            "status": "FAIL",
            "errors": [
                {"gate": f.gate_name, "message": f.message}
                for f in report.failures
            ],
        }
    return parsed, None


# ═══════════════════════════════════════════════════════
# 헬퍼: 출력 직렬화 (tuple key, dataclass, Enum 처리)
# ═══════════════════════════════════════════════════════

def _serialize_expansion_action(a):
    return {
        "action_type": a.action_type.value,
        "target_concepts": a.target_concepts,
        "shared_attrs": a.shared_attrs,
        "parent_name": a.parent_name,
        "reason": a.reason,
    }


def _serialize_repair(rp):
    return {
        "concept": rp.concept,
        "feature": rp.feature,
        "original_type": rp.original_type.value,
        "repaired_type": rp.repaired_type.value,
        "reason": rp.reason,
        "markers": rp.markers,
        "is_ambiguous": rp.is_ambiguous,
    }


def _serialize_warning(w):
    return {
        "concept": w.concept,
        "feature": w.feature,
        "original_type": w.original_type.value,
        "suggested_type": w.suggested_type.value,
        "reason": w.reason,
        "markers": w.markers,
    }


def _serialize_pipeline_output(out):
    """파이프라인 출력을 JSON-직렬화 가능한 형태로 변환."""
    r = out["result"]
    return {
        "status": out["status"],
        "dag": dict(r["dag"]),
        "levels": r["levels"],
        "definitions": r["definitions"],
        "isolated": r["isolated"],
        "aux_relations": [
            {"concept": c, "feature": f, "type": t}
            for (c, f), t in r.get("aux_relations", {}).items()
        ],
        "expansion_actions": [
            _serialize_expansion_action(a)
            for a in out.get("expansion_actions", [])
        ],
        "repairs": [_serialize_repair(rp) for rp in out.get("repairs", [])],
        "warnings": [_serialize_warning(w) for w in out.get("warnings", [])],
        "signature_issues": out.get("signature_issues", []),
        "post_dag_issues": out.get("post_dag_issues", []),
    }


# ═══════════════════════════════════════════════════════
# Tools (5개)
# ═══════════════════════════════════════════════════════

@mcp.tool
def run_pipeline(concepts: list[dict]) -> dict:
    """Validate normalized concepts and build a taxonomy DAG.

    Each concept needs a name and a list of features. Each feature needs
    feature (str), type (one of: essential_feature, contextual_usage,
    locational, functional, social_treatment), and evidence (str, min 4 chars).

    If status is PASS_WITH_WARNING or NEEDS_CORRECTION, inspect
    expansion_actions and call expand with new differentia to refine the DAG.
    """
    parsed, err = _parse_concepts_or_error(concepts)
    if err:
        return err
    pipe = ConceptPipeline()
    out = pipe.run([parsed])
    return _serialize_pipeline_output(out)


@mcp.tool
def expand(original_concepts: list[dict], expansions: list[dict]) -> dict:
    """Merge new differentia into existing concepts and re-run the pipeline.

    Use this after generating expansions based on expansion_actions from
    run_pipeline. Each expansion needs concept (str, must match an existing
    concept name) and new_features (list, same shape as run_pipeline features).

    Returns the same structure as run_pipeline, or a PARSE_FAIL with
    structured errors if the expansions don't conform to the schema.
    """
    originals, err = _parse_concepts_or_error(original_concepts)
    if err:
        return err
    raw_json = json.dumps({"expansions": expansions}, ensure_ascii=False)
    merged, parse_report = parse_expansion_response(raw_json, originals)
    if not parse_report.passed:
        return {
            "status": "PARSE_FAIL",
            "errors": [
                {"gate": f.gate_name, "message": f.message}
                for f in parse_report.failures
            ],
        }
    pipe = ConceptPipeline()
    out = pipe.run([merged])
    return _serialize_pipeline_output(out)


@mcp.tool
def classify_parents(concepts: list[dict]) -> dict:
    """Classify parent candidates for each concept.

    Uses essential attribute inclusion to find direct parents (indirect
    ancestors are removed). Returns multi-label results: a concept can have
    multiple parents when it is a meet (e.g. 정사각형 -> [마름모, 직사각형]).
    """
    parsed, err = _parse_concepts_or_error(concepts)
    if err:
        return err
    # classify each concept against the full list. classify_all expects
    # disjoint existing/new sets, so we call classify directly to avoid
    # double-counting when the same list plays both roles.
    result = {
        c.name: ParentCandidateClassifier.classify(c, parsed)
        for c in parsed
    }
    return {"parent_candidates": result}


@mcp.tool
def export_graph(concepts: list[dict], format: str = "mermaid") -> dict:
    """Export the pipeline result as a graph.

    format: one of mermaid, json, graphml, summary.
    Runs the pipeline internally — no cached state required.
    """
    parsed, err = _parse_concepts_or_error(concepts)
    if err:
        return err
    pipe = ConceptPipeline()
    out = pipe.run([parsed])
    if format == "mermaid":
        return {"format": "mermaid", "content": GraphExporter.to_mermaid(out)}
    elif format == "json":
        return {"format": "json", "content": GraphExporter.to_json(out)}
    elif format == "graphml":
        return {"format": "graphml", "content": GraphExporter.to_graphml(out)}
    elif format == "summary":
        return {"format": "summary", "content": GraphExporter.summary(out)}
    else:
        return {
            "error": f"unknown format: {format}",
            "valid_formats": ["mermaid", "json", "graphml", "summary"],
        }


@mcp.tool
def analyze_expansion(history: list[dict]) -> dict:
    """Analyze expansion loop history for convergence, stalling, or oscillation.

    Pass an array of round records, each with round (int), status (str),
    n_concepts (int), and optionally n_actions (int). Returns a verdict:
    converged, stalled, oscillating, parse_fail, or no_op.
    """
    return ExpansionHistoryAnalyzer.analyze(history)


# ═══════════════════════════════════════════════════════
# Resources (2개)
# ═══════════════════════════════════════════════════════

@mcp.resource("conceptgate://expansion-schema")
def expansion_schema() -> dict:
    """JSON schema for expansion output.

    LLM clients should generate differentia conforming to this schema
    before calling expand.
    """
    return EXPANSION_OUTPUT_SCHEMA


@mcp.resource("conceptgate://pipeline-status-codes")
def pipeline_status_codes() -> dict:
    """Pipeline status codes and recommended client actions."""
    return {
        "PASS": "All gates passed. DAG complete. No action needed.",
        "PASS_WITH_REPAIR": "Auto-repaired (type demotion etc). Check repairs.",
        "PASS_WITH_WARNING": (
            "Warnings only. Check expansion_actions, "
            "add differentia via expand."
        ),
        "NEEDS_CORRECTION": (
            "Manual intervention needed. "
            "Execute CORRECTION expansion_actions."
        ),
        "FAIL": "Hard error. Fix input data.",
    }


# ═══════════════════════════════════════════════════════
# Prompts (1개)
# ═══════════════════════════════════════════════════════

@mcp.prompt
def expansion_prompt(
    action_type: str, target_concepts: str, shared_attrs: str = ""
) -> str:
    """Generate a structured prompt for differentia creation.

    Optional helper — clients may generate differentia directly from
    expansion_actions. action_type is one of: depth, width, correction.
    target_concepts and shared_attrs are comma-separated.
    """
    action = ExpansionAction(
        action_type=ExpansionType(action_type),
        target_concepts=[c.strip() for c in target_concepts.split(",")],
        shared_attrs=(
            [a.strip() for a in shared_attrs.split(",")] if shared_attrs else []
        ),
    )
    return build_expansion_prompt(action)


# ═══════════════════════════════════════════════════════
# 실행 (stdio 기본)
# ═══════════════════════════════════════════════════════

def main():
    transport = os.environ.get("MCP_TRANSPORT", "stdio")
    if transport == "http":
        port = int(os.environ.get("PORT", 8000))
        mcp.run(transport="http", host="0.0.0.0", port=port)
    else:
        mcp.run()  # stdio (로컬 개발, Codex CLI, Claude Desktop 직접 연결)


if __name__ == "__main__":
    main()
