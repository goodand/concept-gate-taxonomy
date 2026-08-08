"""Contract-shape renderers for E-A and E-B.

Both experiments render the SAME underlying facts two ways -- the arms
differ only in whether the payload exposes provenance (origin/assurance),
never in the facts themselves. This is the analogue of H1a's arm-diff
discipline: if the underlying facts differed too, an observed behavior
difference could not be attributed to contract shape alone.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_fixture(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------------
# E-A: does contract shape let a client distinguish asserted vs derived?
# ---------------------------------------------------------------------
def render_ea_flat(fixture: dict) -> dict:
    """Today's actual classify_owl() return shape -- a plain child->parents
    map, unchanged from conceptgate/cg_owl.py::classify. No origin field
    anywhere; asserted and purely-derived edges are byte-identical."""
    return {"hierarchy": fixture["classify_owl_result"]["hierarchy"]}


def render_ea_record(fixture: dict) -> dict:
    """The proposed replacement: entailed_is_a records carrying origin and
    assurance per edge, per the classify_owl output-contract proposal."""
    return {"entailed_is_a": fixture["edges"]}


# ---------------------------------------------------------------------
# E-B: does contract shape prevent "MCP said so, therefore verified"?
# ---------------------------------------------------------------------
def render_eb_mcp_only(fixture: dict) -> dict:
    """Two is-a claims from two different deciders, rendered with NO
    provenance markers -- structurally identical regardless of whether a
    reasoner proved them or an LLM merely proposed them."""
    return {
        "is_a_relations": [
            {"subject": e["subject"], "object": e["object"]}
            for e in fixture["edges"]
        ]
    }


def render_eb_provenance(fixture: dict) -> dict:
    """Same two claims, each carrying its real origin/assurance/decider."""
    return {
        "is_a_relations": [
            {
                "subject": e["subject"], "object": e["object"],
                "origin": e["origin"], "assurance": e["assurance"],
                "decider": e["decider"],
            }
            for e in fixture["edges"]
        ]
    }


EA_ARMS = {"CONTRACT_FLAT": render_ea_flat, "CONTRACT_RECORD": render_ea_record}
EB_ARMS = {"MCP_ONLY": render_eb_mcp_only, "PROVENANCE": render_eb_provenance}
