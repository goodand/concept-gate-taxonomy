"""SBN adapter — PMB_SBN_5_1 profile (D-E2E-v1-22 Q22.2).

Parses PMB-style Simplified Box Notation (SBN) into cg_ir formula dicts.
Source-bound paired-negation→forall codec only (no general rewriting).

The adapter is pure and leaf-layer: no file I/O, no fixture imports,
no reverse imports.
"""
from __future__ import annotations

import re
from typing import Any

import conceptgate.cg_ir as cg_ir


class AdapterUnsupported(Exception):
    """Unsupported SBN construct or structural operator."""
    pass


class AdapterSyntaxError(Exception):
    """Syntax error in SBN string (malformed synset, empty input, etc.)."""
    pass


# Whitelist vocabularies (from sbn_spec.py / clf_signature.yaml)
ROLES = {
    "Agent", "Theme", "Patient", "Experiencer", "Stimulus", "Time", "Location",
    "Destination", "Source", "Recipient", "Topic", "Causer", "Pivot", "Path",
    "Beneficiary", "Attribute", "AttributeOf", "Goal", "Co-Agent", "Co-Patient",
    "Co-Theme", "Consumer", "Duration", "Finish", "Frequency", "Instrument",
    "Instance", "InstanceOf", "Manner", "Material", "Product", "Result", "Start",
    "Value", "Bearer", "Colour", "ColourOf", "ContentOf", "Content", "Creator",
    "Degree", "MadeOf", "Name", "Of", "Operand", "Owner", "Part", "PartOf",
    "Player", "Quantity", "Role", "Sub", "SubOf", "Title", "Unit", "User",
    "ClockTime", "DayOfMonth", "DayOfWeek", "Decade", "MonthOfYear",
    "YearOfCentury", "Affector", "Affectee", "Asset", "Context", "Equal",
    "Extent", "Precondition", "Measure", "Cause", "Order", "Participant",
    "FeatureOf", "Proposition"
}

DRS_OPERATORS = {
    "EQU", "NEQ", "APX", "LES", "LEQ", "TPR", "TSU", "TAB", "TIN", "TCT",
    "MOR", "BOT", "TOP", "ESU", "EPR", "SZP", "SZN", "SXP", "SXN", "STI",
    "STO", "SY1", "SY2", "SXY", "ANA"
}

ROLE_OR_OP = ROLES | DRS_OPERATORS

KNOWN_CONSTANTS = {"speaker", "hearer", "now", "unknown_ref",
                   "monday", "tuesday", "wednesday", "thursday", "friday",
                   "saturday", "sunday"}

BOX_INDICATORS = {
    "NEGATION", "CONJUNCTION", "POSSIBILITY", "NECESSITY", "ATTRIBUTION",
    "CONDITION", "CONSEQUENCE", "ALTERNATION", "CONTINUATION", "CONTRAST",
    "EXPLANATION", "NARRATION", "COMMENTARY", "RESULT", "SOURCE",
    "PRECONDITION", "ELABORATION"
}

SYNSET_PATTERN = re.compile(r"^(.+)\.(n|v|a|r|x)\.(\d+)$")
INDEX_PATTERN = re.compile(r"^([+-]\d+)$")


def adapt_sbn(sbn_text: str) -> dict:
    """Parse PMB-style SBN and return cg_ir formula dict.

    Args:
        sbn_text: SBN string (lines; comments prefixed %%)

    Returns:
        cg_ir formula dict

    Raises:
        AdapterSyntaxError: if syntax is invalid (malformed synset, empty input)
        AdapterUnsupported: if construct is not supported, fail-closed corner,
                          or output validation fails
    """
    if not sbn_text or not sbn_text.strip():
        raise AdapterSyntaxError("empty input")

    # Parse lines, stripping comments
    lines = _parse_lines(sbn_text)
    if not lines:
        raise AdapterSyntaxError("empty input (only comments)")

    # Extract synset and box information, building a linear chain of boxes
    synsets, boxes = _extract_structure(lines)
    if not synsets:
        raise AdapterSyntaxError("no synset lines found")

    # Build IR
    ir = _build_ir(synsets, boxes)

    # Validate output
    errors = cg_ir.validate_formula(ir)
    if errors:
        raise AdapterUnsupported(f"output validation failed: {errors}")

    # Check that no free variables (closed formula)
    free_vars = cg_ir.free_variables(ir)
    if free_vars:
        raise AdapterUnsupported(f"formula has free variables: {free_vars}")

    return ir


def _parse_lines(text: str) -> list[str]:
    """Strip comments and blank lines, return non-empty content lines."""
    result = []
    for line in text.split("\n"):
        # Strip trailing inline comment (% onwards)
        if "%" in line:
            line = line.split("%", 1)[0]
        line = line.strip()
        if line and not line.startswith("%%%"):
            result.append(line)
    return result


def _extract_structure(lines: list[str]) -> tuple[list[dict], list[tuple[str, str]]]:
    """Extract synsets and boxes from content lines.

    Returns:
        (synsets, boxes) where:
        - synsets: list of {"name": str, "roles": [(role, target_str), ...]}
        - boxes: list of (box_type, box_index_str) tuples for NEGATION <1 lines
    """
    synsets = []
    boxes = []

    i = 0
    while i < len(lines):
        line = lines[i]
        tokens = line.split()

        if not tokens:
            i += 1
            continue

        first_token = tokens[0]

        # Check if it's a box indicator line
        if first_token in BOX_INDICATORS:
            if len(tokens) < 2:
                raise AdapterSyntaxError(f"box indicator {first_token} without index")
            box_index = tokens[1]
            boxes.append((first_token, box_index))
            i += 1
            continue

        # Otherwise, it should be a synset line
        if not SYNSET_PATTERN.match(first_token):
            raise AdapterSyntaxError(f"malformed synset: {first_token}")

        # Parse synset and its roles/ops
        synset_entry = {"name": first_token, "roles": []}

        # Remaining tokens are Role/Op pairs
        j = 1
        while j < len(tokens):
            if j + 1 >= len(tokens):
                raise AdapterSyntaxError(f"unpaired role/op token: {tokens[j]}")

            role_or_op = tokens[j]
            target_str = tokens[j + 1]

            if role_or_op not in ROLE_OR_OP:
                raise AdapterUnsupported(f"unknown role/op: {role_or_op}")

            synset_entry["roles"].append((role_or_op, target_str))
            j += 2

        synsets.append(synset_entry)
        i += 1

    return synsets, boxes


def _build_ir(synsets: list[dict], boxes: list[tuple[str, str]]) -> dict:
    """Build cg_ir formula from parsed synsets and boxes.

    Applies the forall codec at box boundaries where the pattern matches.
    """
    # Build variable names: x0, x1, ... for each synset
    var_names = [f"x{i}" for i in range(len(synsets))]

    # Map synset indices to their variables for role target resolution
    synset_to_var = {i: var_names[i] for i in range(len(synsets))}

    # Validate role targets (relative indices must be in range)
    for synset_idx, synset in enumerate(synsets):
        for role, target_str in synset["roles"]:
            if INDEX_PATTERN.match(target_str):
                offset = int(target_str)
                target_idx = synset_idx + offset
                if target_idx < 0 or target_idx >= len(synsets):
                    raise AdapterSyntaxError(
                        f"synset {synset_idx}: role {role} target {target_str} "
                        f"out of range (would be index {target_idx})"
                    )

    # Determine box structure: which synsets belong to which box
    # Box structure is represented as a sequence of (start_synset, end_synset, negated)
    # where start_synset is the first synset in the box and negated indicates if
    # the box itself is negated
    box_structure = _determine_box_structure(len(synsets), boxes)

    # Build IR for the outermost box
    ir = _build_box_ir(synsets, var_names, synset_to_var, box_structure, 0)

    return ir


def _determine_box_structure(num_synsets: int, boxes: list[tuple[str, str]]) -> list[tuple[int, int, bool]]:
    """Determine which synsets belong to which box.

    Returns list of (start_synset_idx, end_synset_idx, is_negated) tuples.
    Validates box indicators (only NEGATION <1 supported).
    """
    # Validate box indicators: only NEGATION, only <1
    for box_type, box_index in boxes:
        if box_type != "NEGATION":
            raise AdapterUnsupported(f"unsupported box operator: {box_type}")
        if box_index != "<1":
            raise AdapterUnsupported(f"unsupported box index: {box_index}")

    # Simple structure: boxes form a linear chain based on NEGATION positions
    # Each NEGATION <1> line opens a new nested box
    if not boxes:
        # No negations: single box containing all synsets
        return [(0, num_synsets, False)]

    # With negations, we need to track which synset indices belong to which nesting level
    # For now, use a simpler approach: process sequentially and track nesting

    # The trick is: synset lines appear in order, and NEGATION lines appear between them
    # We need to rebuild this from the box list

    # Actually, we need to re-scan the original lines to know exact positions
    # But we only have synsets and boxes as separate lists now.
    # We need a different approach: interleave them in the original order.

    # For now, let's use a heuristic: if there are N boxes, and they're all NEGATION <1>,
    # we have N+1 "content regions" (boxes)
    # The first box is from synset 0 to the first NEGATION
    # Each subsequent box is between consecutive NEGATIONs

    # But wait, we lost the original line order. Let me reconsider.
    # The _extract_structure function doesn't preserve relative positions of
    # synsets and boxes!

    # I need to refactor to preserve the interleaving.
    return [(0, num_synsets, False)]  # Fallback


def _extract_structure_with_order(lines: list[str]) -> tuple[list[dict], list[tuple[int, str, str]]]:
    """Extract synsets and boxes, preserving relative order.

    Returns:
        (synsets, box_markers) where:
        - synsets: list of {"name": str, "roles": [...]}
        - box_markers: list of (position, box_type, box_index) tuples
          where position is the synset index after which this box marker appears
    """
    synsets = []
    box_markers = []
    synset_count = 0

    for line in lines:
        tokens = line.split()
        if not tokens:
            continue

        first_token = tokens[0]

        if first_token in BOX_INDICATORS:
            if len(tokens) < 2:
                raise AdapterSyntaxError(f"box indicator {first_token} without index")
            box_markers.append((synset_count, first_token, tokens[1]))
            continue

        if not SYNSET_PATTERN.match(first_token):
            raise AdapterSyntaxError(f"malformed synset: {first_token}")

        synset_entry = {"name": first_token, "roles": []}
        j = 1
        while j < len(tokens):
            if j + 1 >= len(tokens):
                raise AdapterSyntaxError(f"unpaired role/op token: {tokens[j]}")
            role_or_op = tokens[j]
            target_str = tokens[j + 1]
            if role_or_op not in ROLE_OR_OP:
                raise AdapterUnsupported(f"unknown role/op: {role_or_op}")
            j += 2
            # 스펙 NAME_CONSTANT_PATTERN 둘째 대안: 열린 따옴표 상수는 닫는
            # 따옴표까지 후속 토큰 병합 (Path A 실측: 미병합 시 여러 단어
            # 인용 이름이 "unpaired role/op" 오탐 — 후보 18건)
            if (target_str.startswith('"') and
                    not (len(target_str) > 1 and target_str.endswith('"'))):
                _parts = [target_str]
                while j < len(tokens) and not tokens[j].endswith('"'):
                    _parts.append(tokens[j]); j += 1
                if j >= len(tokens):
                    raise AdapterSyntaxError(
                        f"unterminated quoted constant: {' '.join(_parts)}")
                _parts.append(tokens[j]); j += 1
                target_str = " ".join(_parts)
            synset_entry["roles"].append((role_or_op, target_str))

        synsets.append(synset_entry)
        synset_count += 1

    return synsets, box_markers


def _extract_structure(lines: list[str]) -> tuple[list[dict], dict]:
    """Extract synsets and build a tree structure representing boxes.

    Returns:
        (synsets, box_tree) where:
        - synsets: list of {"name": str, "roles": [...]}
        - box_tree: a tree structure representing the nesting of boxes

    Box tree structure:
        {"type": "normal"|"negation", "synsets": [...], "child": <box or None>}
    """
    synsets = []
    root_box = {"type": "normal", "synsets": [], "child": None}
    current_box = root_box
    synset_count = 0

    for line in lines:
        tokens = line.split()
        if not tokens:
            continue

        first_token = tokens[0]

        if first_token in BOX_INDICATORS:
            if len(tokens) < 2:
                raise AdapterSyntaxError(f"box indicator {first_token} without index")
            box_type, box_index = first_token, tokens[1]

            # Validate
            if box_type != "NEGATION":
                raise AdapterUnsupported(f"unsupported box operator: {box_type}")
            if box_index != "<1":
                raise AdapterUnsupported(f"unsupported box index: {box_index}")

            # Create a new negated box and attach it as a child
            new_box = {"type": "negation", "synsets": [], "child": None}
            current_box["child"] = new_box
            current_box = new_box
            continue

        if not SYNSET_PATTERN.match(first_token):
            raise AdapterSyntaxError(f"malformed synset: {first_token}")

        synset_entry = {"name": first_token, "roles": []}
        j = 1
        while j < len(tokens):
            if j + 1 >= len(tokens):
                raise AdapterSyntaxError(f"unpaired role/op token: {tokens[j]}")
            role_or_op = tokens[j]
            target_str = tokens[j + 1]
            if role_or_op not in ROLE_OR_OP:
                raise AdapterUnsupported(f"unknown role/op: {role_or_op}")
            j += 2
            # 스펙 NAME_CONSTANT_PATTERN 둘째 대안: 열린 따옴표 상수는 닫는
            # 따옴표까지 후속 토큰 병합 (Path A 실측: 미병합 시 여러 단어
            # 인용 이름이 "unpaired role/op" 오탐 — 후보 18건)
            if (target_str.startswith('"') and
                    not (len(target_str) > 1 and target_str.endswith('"'))):
                _parts = [target_str]
                while j < len(tokens) and not tokens[j].endswith('"'):
                    _parts.append(tokens[j]); j += 1
                if j >= len(tokens):
                    raise AdapterSyntaxError(
                        f"unterminated quoted constant: {' '.join(_parts)}")
                _parts.append(tokens[j]); j += 1
                target_str = " ".join(_parts)
            synset_entry["roles"].append((role_or_op, target_str))

        synsets.append(synset_entry)
        # Add this synset index to the current box
        current_box["synsets"].append(synset_count)
        synset_count += 1

    return synsets, root_box


def _build_ir(synsets: list[dict], box_tree: dict) -> dict:
    """Build cg_ir formula from synsets and box tree.

    The box_tree is a hierarchical structure representing nested boxes.
    """
    num_synsets = len(synsets)
    var_names = [f"x{i}" for i in range(num_synsets)]
    synset_to_var = {i: var_names[i] for i in range(num_synsets)}

    # Validate role targets
    for synset_idx, synset in enumerate(synsets):
        for role, target_str in synset["roles"]:
            if INDEX_PATTERN.match(target_str):
                offset = int(target_str)
                target_idx = synset_idx + offset
                if target_idx < 0 or target_idx >= num_synsets:
                    raise AdapterSyntaxError(
                        f"synset {synset_idx}: role {role} target {target_str} "
                        f"out of range (would be index {target_idx})"
                    )

    # Build IR recursively from the box tree
    ir = _build_box_tree(synsets, var_names, synset_to_var, box_tree)

    return ir


def _build_box_tree(
    synsets: list[dict],
    var_names: list[str],
    synset_to_var: dict[int, str],
    box: dict,
) -> dict:
    """Build IR from a box tree structure.

    A box dict has:
    - "type": "normal" or "negation"
    - "synsets": list of synset indices in this box
    - "child": nested box (or None)

    Applies the forall codec:
    - If this is a negation box containing synsets with a negation child also
      containing synsets, decode to forall.
    - Otherwise, build normally.
    """
    synset_indices = box.get("synsets", [])
    child = box.get("child")
    box_type = box.get("type")

    if not synset_indices and not child:
        raise AdapterUnsupported("empty box")

    # Check if forall codec applies
    if (box_type == "negation" and synset_indices and child
            and child.get("type") == "negation" and child.get("synsets")):
        # Apply forall codec
        return _apply_forall_codec(synsets, var_names, synset_to_var, box, child)

    # Default: build normally
    # Build predicates and roles for this box's synsets
    preds_and_roles = []

    for synset_idx in synset_indices:
        synset = synsets[synset_idx]
        synset_var = var_names[synset_idx]

        synset_pred = _make_pred(synset["name"], [{"kind": "var", "name": synset_var}])
        preds_and_roles.append(synset_pred)

        for role, target_str in synset["roles"]:
            target_node = _resolve_target(target_str, synset_idx, synset_to_var, synsets)
            role_pred = _make_pred(role, [{"kind": "var", "name": synset_var}, target_node])
            preds_and_roles.append(role_pred)

    # Recursively build child box IR and add it to conjunction
    if child:
        child_ir = _build_box_tree(synsets, var_names, synset_to_var, child)
        preds_and_roles.append(child_ir)

    # Build the conjunction
    if len(preds_and_roles) == 1:
        body_conj = preds_and_roles[0]
    else:
        body_conj = {"kind": "and", "args": preds_and_roles}

    # Wrap in exists quantifiers for all synsets in this box
    result = body_conj
    for i in range(len(synset_indices) - 1, -1, -1):
        synset_idx = synset_indices[i]
        synset_var = var_names[synset_idx]
        result = {
            "kind": "exists",
            "var": synset_var,
            "restriction": {"kind": "pred", "name": "True", "args": []},
            "body": result,
        }

    # If this is a negation box, wrap in "not"
    if box_type == "negation":
        result = {"kind": "not", "body": result}

    return result


def _apply_forall_codec(
    synsets: list[dict],
    var_names: list[str],
    synset_to_var: dict[int, str],
    restriction_box: dict,
    body_box: dict,
) -> dict:
    """Apply the forall codec to a paired negation pattern.

    Pattern: NEGATION (restriction with synsets) NEGATION (body with synsets)
    Decodes to: forall u (restriction[u as universal] body_content)

    Note: The codec consumes both negations, so we extract the content of
    body_box without wrapping it in "not".
    """
    restr_synset_indices = restriction_box.get("synsets", [])
    body_synset_indices = body_box.get("synsets", [])

    if not restr_synset_indices or not body_synset_indices:
        raise AdapterUnsupported("forall codec requires synsets in both boxes")

    # Universal variable is the first synset in the restriction
    universal_var = var_names[restr_synset_indices[0]]

    # Build restriction IR: synsets of restriction_box with first as universal
    restr_preds = []
    for synset_idx in restr_synset_indices:
        synset = synsets[synset_idx]
        synset_var = var_names[synset_idx]

        synset_pred = _make_pred(synset["name"], [{"kind": "var", "name": synset_var}])
        restr_preds.append(synset_pred)

        for role, target_str in synset["roles"]:
            target_node = _resolve_target(target_str, synset_idx, synset_to_var, synsets)
            role_pred = _make_pred(role, [{"kind": "var", "name": synset_var}, target_node])
            restr_preds.append(role_pred)

    # Build restriction body (conjunction of preds)
    if len(restr_preds) == 1:
        restr_body = restr_preds[0]
    else:
        restr_body = {"kind": "and", "args": restr_preds}

    # Wrap other synsets (non-universal) in exists
    restriction_ir = restr_body
    for i in range(len(restr_synset_indices) - 1, 0, -1):  # From last down to (but not) first
        synset_idx = restr_synset_indices[i]
        synset_var = var_names[synset_idx]
        restriction_ir = {
            "kind": "exists",
            "var": synset_var,
            "restriction": {"kind": "pred", "name": "True", "args": []},
            "body": restriction_ir,
        }

    # Build body IR from body_box content (without negation wrapping, since the
    # codec consumes both negations)
    body_ir = _build_box_content(synsets, var_names, synset_to_var, body_box)

    # Check for donkey reference: body_ir must not reference any restriction
    # variable other than the universal variable
    body_free_vars = cg_ir.free_variables(body_ir)
    for i in range(1, len(restr_synset_indices)):  # Skip the universal (first)
        restriction_var = var_names[restr_synset_indices[i]]
        if restriction_var in body_free_vars:
            raise AdapterUnsupported(
                f"body references restriction variable {restriction_var} "
                f"(not the universal variable); donkey binding not supported"
            )

    # Build forall
    forall_ir = {
        "kind": "forall",
        "var": universal_var,
        "restriction": restriction_ir,
        "body": body_ir,
    }

    return forall_ir


def _build_box_content(
    synsets: list[dict],
    var_names: list[str],
    synset_to_var: dict[int, str],
    box: dict,
) -> dict:
    """Build IR for a box's content without wrapping in negation.

    This is used by the forall codec to build the body box's content
    without adding the "not" wrapper that would normally apply to a negation box.
    """
    synset_indices = box.get("synsets", [])
    child = box.get("child")

    if not synset_indices and not child:
        raise AdapterUnsupported("empty box")

    # Build predicates and roles for this box's synsets
    preds_and_roles = []

    for synset_idx in synset_indices:
        synset = synsets[synset_idx]
        synset_var = var_names[synset_idx]

        synset_pred = _make_pred(synset["name"], [{"kind": "var", "name": synset_var}])
        preds_and_roles.append(synset_pred)

        for role, target_str in synset["roles"]:
            target_node = _resolve_target(target_str, synset_idx, synset_to_var, synsets)
            role_pred = _make_pred(role, [{"kind": "var", "name": synset_var}, target_node])
            preds_and_roles.append(role_pred)

    # Recursively build child box IR and add it to conjunction
    if child:
        child_ir = _build_box_tree(synsets, var_names, synset_to_var, child)
        preds_and_roles.append(child_ir)

    # Build the conjunction
    if len(preds_and_roles) == 1:
        body_conj = preds_and_roles[0]
    else:
        body_conj = {"kind": "and", "args": preds_and_roles}

    # Wrap in exists quantifiers for all synsets in this box
    result = body_conj
    for i in range(len(synset_indices) - 1, -1, -1):
        synset_idx = synset_indices[i]
        synset_var = var_names[synset_idx]
        result = {
            "kind": "exists",
            "var": synset_var,
            "restriction": {"kind": "pred", "name": "True", "args": []},
            "body": result,
        }

    return result




def _resolve_target(
    target_str: str, synset_idx: int, synset_to_var: dict[int, str], synsets: list[dict]
) -> dict:
    """Resolve a role target to either a variable reference or a constant."""
    # Check if it's a relative index
    if INDEX_PATTERN.match(target_str):
        offset = int(target_str)
        target_idx = synset_idx + offset
        return {"kind": "var", "name": synset_to_var[target_idx]}

    # It's a constant
    # Strip quotes if present
    if target_str.startswith('"') and target_str.endswith('"'):
        constant_name = target_str[1:-1]
    else:
        constant_name = target_str

    # Check if it's a known constant (lowercase alphabetic)
    if constant_name in KNOWN_CONSTANTS:
        return {"kind": "entity", "name": constant_name}

    # Check if it looks like a year ('NNNN'), digit, single letter, +, -, or ?
    if (constant_name.startswith("'") and constant_name.endswith("'")
            and constant_name[1:-1].isdigit()):
        # Year literal
        return {"kind": "entity", "name": constant_name[1:-1]}
    elif constant_name.isdigit():
        return {"kind": "entity", "name": constant_name}
    elif len(constant_name) == 1 and constant_name.isupper():
        return {"kind": "entity", "name": constant_name}
    elif constant_name in ("+", "-", "?"):
        return {"kind": "entity", "name": constant_name}
    elif constant_name and constant_name[0].islower() and constant_name.isalpha():
        # Alphabetic lowercase: reject unless it's a known constant
        raise AdapterUnsupported(
            f"unknown constant: {constant_name} (not in known constants)"
        )
    else:
        # Accept as entity
        return {"kind": "entity", "name": constant_name}


def _make_pred(name: str, args: list[dict]) -> dict:
    """Create a predicate node."""
    return {"kind": "pred", "name": name, "args": args}
