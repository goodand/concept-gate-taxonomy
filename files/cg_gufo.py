"""gUFO/Scior adapter for ConceptGate.

The Scior subtree is kept as a read-only reference under vendor/scior. This
module extracts the small rule metadata ConceptGate needs without importing
Scior's runtime dependencies (rdflib/owlrl).
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


SCIOR_RULES_REL = os.path.join(
    "vendor", "scior", "documentation", "resources", "rules_implementation.tsv"
)


@dataclass(frozen=True)
class SciorRuleRef:
    base_rule: str
    group: str
    implementation_rule: str
    logic: str


_FALLBACK_RULES: Dict[str, SciorRuleRef] = {
    "RA02": SciorRuleRef(
        base_rule="R22",
        group="UFO All",
        implementation_rule="RA02",
        logic="RigidType(x) ^ subClassOf(x,y) -> ~AntiRigidType(y)",
    ),
    "RA03": SciorRuleRef(
        base_rule="R23",
        group="UFO All",
        implementation_rule="RA03",
        logic="SemiRigidType(x) ^ subClassOf(x,y) -> ~AntiRigidType(y)",
    ),
    "RU01": SciorRuleRef(
        base_rule="R28",
        group="UFO Unique",
        implementation_rule="RU01",
        logic="Sortal(x) -> E! y (subClassOf (x,y) ^ Kind(y))",
    ),
}


def _default_rules_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    for rel in (SCIOR_RULES_REL, os.path.join("..", SCIOR_RULES_REL)):
        path = os.path.join(here, rel)
        if os.path.exists(path):
            return path
    return os.path.join(here, SCIOR_RULES_REL)


def load_scior_rules(path: Optional[str] = None) -> Dict[str, SciorRuleRef]:
    """Load Scior implementation rules from the vendored TSV.

    Falls back to the minimal rules ConceptGate currently uses when the subtree
    is absent, which keeps files/-only MCP installs working.
    """
    rules_path = path or _default_rules_path()
    if not os.path.exists(rules_path):
        return dict(_FALLBACK_RULES)

    rules: Dict[str, SciorRuleRef] = {}
    with open(rules_path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for row in reader:
            impl = (row.get("Rule Code") or "").strip()
            if not impl:
                continue
            rules[impl] = SciorRuleRef(
                base_rule=(row.get("Base Rules") or "").strip(),
                group=(row.get("Group") or "").strip(),
                implementation_rule=impl,
                logic=(row.get("First-Order Logic") or "").strip(),
            )
    return rules or dict(_FALLBACK_RULES)


def rule_ref(rule_code: str) -> SciorRuleRef:
    rules = load_scior_rules()
    if rule_code not in rules:
        raise KeyError(f"unknown Scior rule: {rule_code}")
    return rules[rule_code]


def selected_rule_summary() -> List[Dict[str, str]]:
    """Small stable summary for docs/tests without exposing Scior internals."""
    rules = load_scior_rules()
    selected = []
    for code in ("RA02", "RA03", "RU01"):
        ref = rules.get(code, _FALLBACK_RULES[code])
        selected.append({
            "base_rule": ref.base_rule,
            "group": ref.group,
            "implementation_rule": ref.implementation_rule,
            "logic": ref.logic,
        })
    return selected
