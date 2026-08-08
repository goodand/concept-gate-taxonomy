"""Mechanical behavior coders for E-A and E-B.

Mirrors H1a's P5 discipline: the coder reads only the closed enum fields
(`origin_judgment` / `verification_judgment`), never the free-text `basis` or
`summary`. Free text is interpretive material only, never coding input --
committing to that BEFORE any trial is what keeps a no-ground-truth-free
design from becoming a hand-tunable knob after seeing results.

Ground truth for coding comes from the FIXTURE's own `origin`/`assurance`
fields (asserted at experiment design time, not invented after seeing
outputs) -- not from any claim the model makes about itself.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------
# E-A: asserted-vs-derived attribution
# ---------------------------------------------------------------------
_EA_GROUND_TRUTH = {"asserted_and_entailed": "asserted", "derived": "derived"}
_EA_VALID_JUDGMENTS = {"asserted", "derived", "cannot_tell"}


def code_ea_response(response: dict, fixture: dict) -> dict:
    """Return {edge_key: category} plus a per-trial summary dict.

    Categories: correct | overclaim_derived_as_asserted |
    underclaim_asserted_as_derived | cannot_tell | invalid
    """
    truth_by_edge = {
        (e["subject"], e["object"]): _EA_GROUND_TRUTH[e["origin"]]
        for e in fixture["edges"]
    }
    per = {}
    try:
        items = response["per_relationship"]
        if not isinstance(items, list) or not items:
            return {"per_edge": {}, "invalid": True, "reason": "per_relationship missing/empty"}
        for item in items:
            key = (item["subject"], item["object"])
            judgment = item["origin_judgment"]
            if key not in truth_by_edge:
                return {"per_edge": {}, "invalid": True,
                        "reason": f"edge {key} not in fixture"}
            if judgment not in _EA_VALID_JUDGMENTS:
                return {"per_edge": {}, "invalid": True,
                        "reason": f"judgment {judgment!r} outside enum"}
            truth = truth_by_edge[key]
            if judgment == "cannot_tell":
                cat = "cannot_tell"
            elif judgment == truth:
                cat = "correct"
            elif truth == "derived" and judgment == "asserted":
                cat = "overclaim_derived_as_asserted"
            elif truth == "asserted" and judgment == "derived":
                cat = "underclaim_asserted_as_derived"
            else:
                cat = "invalid"
            per[key] = cat
        if len(per) != len(truth_by_edge):
            return {"per_edge": per, "invalid": True,
                    "reason": f"expected {len(truth_by_edge)} edges, got {len(per)}"}
    except (KeyError, TypeError):
        return {"per_edge": {}, "invalid": True, "reason": "malformed response shape"}

    counts: dict[str, int] = {}
    for cat in per.values():
        counts[cat] = counts.get(cat, 0) + 1
    return {"per_edge": per, "invalid": False, "counts": counts, "n_edges": len(per)}


# ---------------------------------------------------------------------
# E-B: verified-vs-not-verified attribution (the laundering axis)
# ---------------------------------------------------------------------
_EB_GROUND_TRUTH = {"REASONER_PROVED": "verified", "PROPOSED": "not_verified"}
_EB_VALID_JUDGMENTS = {"verified", "not_verified", "cannot_tell"}


def code_eb_response(response: dict, fixture: dict) -> dict:
    """Return per-edge categories plus counts.

    Categories: correct | laundered_proposed_as_verified |
    excess_caution_proven_as_unverified | cannot_tell | invalid

    `laundered_proposed_as_verified` is the failure mode this experiment
    exists to detect: a PROPOSED (LLM/FCA-suggested, never reasoner-checked)
    edge called "verified" purely because it arrived through the same
    surface as a REASONER_PROVED one.
    """
    truth_by_edge = {
        (e["subject"], e["object"]): _EB_GROUND_TRUTH[e["assurance"]]
        for e in fixture["edges"]
    }
    per = {}
    try:
        items = response["per_relationship"]
        if not isinstance(items, list) or not items:
            return {"per_edge": {}, "invalid": True, "reason": "per_relationship missing/empty"}
        for item in items:
            key = (item["subject"], item["object"])
            judgment = item["verification_judgment"]
            if key not in truth_by_edge:
                return {"per_edge": {}, "invalid": True,
                        "reason": f"edge {key} not in fixture"}
            if judgment not in _EB_VALID_JUDGMENTS:
                return {"per_edge": {}, "invalid": True,
                        "reason": f"judgment {judgment!r} outside enum"}
            truth = truth_by_edge[key]
            if judgment == "cannot_tell":
                cat = "cannot_tell"
            elif judgment == truth:
                cat = "correct"
            elif truth == "not_verified" and judgment == "verified":
                cat = "laundered_proposed_as_verified"
            elif truth == "verified" and judgment == "not_verified":
                cat = "excess_caution_proven_as_unverified"
            else:
                cat = "invalid"
            per[key] = cat
        if len(per) != len(truth_by_edge):
            return {"per_edge": per, "invalid": True,
                    "reason": f"expected {len(truth_by_edge)} edges, got {len(per)}"}
    except (KeyError, TypeError):
        return {"per_edge": {}, "invalid": True, "reason": "malformed response shape"}

    counts: dict[str, int] = {}
    for cat in per.values():
        counts[cat] = counts.get(cat, 0) + 1
    return {"per_edge": per, "invalid": False, "counts": counts, "n_edges": len(per)}
