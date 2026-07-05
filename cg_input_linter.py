"""ConceptGate input linter.

Client-side preflight for proof-carrying concept JSON. This module does not
build a DAG and does not replace ConceptGate gates. It catches common input
quality problems before MCP clients call run_pipeline.

stdlib only.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from cg_partwhole import hint_to_feature_type
except Exception:  # pragma: no cover - graceful fallback for copied files
    def hint_to_feature_type(relation_hint: Optional[str]) -> Optional[str]:
        fallback = {
            "is_a": "essential_feature",
            "has_part": "structural_composition",
            "part_of": "structural_composition",
            "component_of": "structural_composition",
            "member_of": "structural_composition",
            "subcollection_of": "structural_composition",
            "subquantity_of": "structural_composition",
            "material_of": "essential_feature",
            "phase_of": "contextual_usage",
            "located_in": "locational",
        }
        if not relation_hint or not isinstance(relation_hint, str):
            return None
        return fallback.get(relation_hint.strip().lower())


VALID_TYPES = frozenset({
    "essential_feature",
    "structural_composition",
    "contextual_usage",
    "locational",
    "functional",
    "social_treatment",
})

PARTWHOLE_HINTS = frozenset({
    "has_part",
    "part_of",
    "component_of",
    "member_of",
    "subcollection_of",
    "subquantity_of",
})

# 도메인 중립 placeholder 탐지: 실제 도메인 라벨에는 "feature"라는 단어
# 자체가 등장하지 않는다. 라벨이 메타 어휘(feature/features)를 담고 있으면
# "X features"류 상속 placeholder일 가능성이 높다.
PLACEHOLDER_PATTERNS = (
    "parent features",
    "same as above",
    "same features",
    " features",       # "<concept> features" 상속 placeholder (도메인 무관)
    "features from",
    "상위 feature",
    "상위 특징",
    "동일 feature",
    "위와 같음",
)

WEAK_STRUCTURAL_MARKERS = (
    "based on",
    "uses",
    "relies on",
    "computed by",
    "computed with",
    "implemented with",
    "follows architecture",
    "associated with",
    "기반",
    "사용",
    "의존",
    "계산",
    "따른다",
    "연관",
)

# is-a를 문장으로 주장할 때 나타나는 표지 (개념명 참조와 결합해서만 사용).
# 도메인 중립 유지: 단독으로 정당한 라벨에 흔한 단어("형태" 등)는 조사 결합형
# ("형태의")만 쓴다.
ISA_CLAIM_MARKERS = (
    "이다",
    "입니다",
    "일종",
    "종류",
    "형태의",
    "의 하나",
    " is a",
    " is an",
    "kind of",
    "type of",
    "variant of",
)

STRONG_STRUCTURAL_MARKERS = (
    "include",
    "includes",
    "included",
    "contain",
    "contains",
    "consist of",
    "consists of",
    "composed of",
    "component",
    "part",
    "module",
    "layer",
    "sublayer",
    "sub-layer",
    "stack",
    "member",
    "포함",
    "구성",
    "구성요소",
    "부품",
    "부분",
    "모듈",
    "레이어",
    "층",
    "스택",
    "멤버",
)


def _issue(
    severity: str,
    code: str,
    message: str,
    concept: Optional[str] = None,
    feature: Optional[str] = None,
    suggestion: Optional[str] = None,
) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "severity": severity,
        "code": code,
        "message": message,
    }
    if concept is not None:
        out["concept"] = concept
    if feature is not None:
        out["feature"] = feature
    if suggestion is not None:
        out["suggestion"] = suggestion
    return out


def _has_any(text: str, markers: tuple[str, ...]) -> bool:
    lower = text.lower()
    return any(marker in lower for marker in markers)


def _is_sentence_like(feature: str) -> bool:
    stripped = feature.strip()
    if len(stripped) > 80:
        return True
    if stripped.count(" ") >= 8:
        return True
    if stripped.endswith((".", "。", "다", "함", "한다")) and stripped.count(" ") >= 3:
        return True
    return False


def _expected_type_from_hint(relation_hint: Any) -> Optional[str]:
    if not isinstance(relation_hint, str):
        return None
    hint = relation_hint.strip().lower()
    if hint in PARTWHOLE_HINTS:
        return "structural_composition"
    return hint_to_feature_type(hint)


def lint_concepts(concepts: Any) -> Dict[str, Any]:
    """Lint normalized concept JSON before run_pipeline.

    Returns:
        {
          "status": "LINT_PASS" | "LINT_WARNING" | "LINT_ERROR",
          "issues": [...],
          "summary": {"errors": int, "warnings": int}
        }
    """
    issues: List[Dict[str, Any]] = []

    if not isinstance(concepts, list):
        issues.append(_issue(
            "error",
            "CONCEPTS_NOT_LIST",
            "concepts must be a list before calling run_pipeline.",
        ))
        return _finish(issues)

    for idx, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            issues.append(_issue(
                "error",
                "CONCEPT_NOT_OBJECT",
                f"concept at index {idx} must be an object.",
            ))
            continue

        name = concept.get("name")
        concept_name = name if isinstance(name, str) and name.strip() else f"<index:{idx}>"
        if not isinstance(name, str) or not name.strip():
            issues.append(_issue(
                "error",
                "MISSING_CONCEPT_NAME",
                f"concept at index {idx} needs a non-empty name.",
            ))

        features = concept.get("features")
        if "features" not in concept:
            issues.append(_issue(
                "error",
                "MISSING_FEATURES",
                "features is required. If only concept names are known, perform source-grounded feature discovery.",
                concept=concept_name,
                suggestion="Find source-backed atomic features, then retry lint_concepts and run_pipeline.",
            ))
            continue
        if not isinstance(features, list):
            issues.append(_issue(
                "error",
                "FEATURES_NOT_LIST",
                "features must be a list.",
                concept=concept_name,
            ))
            continue
        if not features:
            issues.append(_issue(
                "error",
                "EMPTY_FEATURES",
                "features is empty. ConceptGate cannot infer meaning from names alone.",
                concept=concept_name,
                suggestion="Add at least one source-backed essential_feature or justified non-essential feature.",
            ))
            continue

        for fidx, raw_feature in enumerate(features):
            if not isinstance(raw_feature, dict):
                issues.append(_issue(
                    "error",
                    "FEATURE_NOT_OBJECT",
                    f"feature at index {fidx} must be an object.",
                    concept=concept_name,
                ))
                continue
            _lint_feature(concept_name, raw_feature, issues)

    _lint_cross_concept(concepts, issues)

    return _finish(issues)


def _essential_labels(concepts: Any) -> Dict[str, set]:
    """개념별 essential feature 라벨 집합. malformed 항목은 건너뜀."""
    out: Dict[str, set] = {}
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        name = concept.get("name")
        features = concept.get("features")
        if not isinstance(name, str) or not name.strip() or not isinstance(features, list):
            continue
        labels = {
            f["feature"].strip()
            for f in features
            if isinstance(f, dict)
            and f.get("type") == "essential_feature"
            and isinstance(f.get("feature"), str)
            and f["feature"].strip()
        }
        if labels:
            out[name.strip()] = labels
    return out


def _lint_cross_concept(concepts: Any, issues: List[Dict[str, Any]]) -> None:
    """개념 간 검사. is-a DAG는 essential 라벨의 '문자열 그대로' 부분집합
    포함으로만 만들어지므로, 라벨 공유가 없으면 edge는 수학적으로 불가능하다.
    """
    labels_by_concept = _essential_labels(concepts)
    names = list(labels_by_concept.keys())

    # 1) 다른 개념명을 참조하는 is-a 주장형 feature
    #    예: 개념 "스케일드닷프로덕트어텐션"의 feature "트랜스포머의 어텐션이다"
    #    — 문장으로 is-a를 선언해도 edge는 생기지 않는다.
    #    오탐 방지: 개념명 포함 + (주장 표지 or 라벨==개념명)일 때만 발화.
    for name, labels in labels_by_concept.items():
        for label in labels:
            for other in names:
                if other == name or len(other) < 2:
                    continue
                if other not in label:
                    continue
                if label == other or _has_any(label, ISA_CLAIM_MARKERS):
                    issues.append(_issue(
                        "warning",
                        "ISA_CLAIM_FEATURE",
                        f"essential feature states an is-a claim about concept "
                        f"'{other}'. A claim sentence creates no DAG edge.",
                        concept=name,
                        feature=label,
                        suggestion=(
                            f"Remove this label and instead repeat ALL of '{other}' "
                            "essential feature labels verbatim, then add differentia."
                        ),
                    ))
                    break

    # 2) 모든 개념 쌍이 essential 라벨을 하나도 공유하지 않음 → edge 0 확정
    if len(names) >= 2:
        any_shared = any(
            labels_by_concept[a] & labels_by_concept[b]
            for i, a in enumerate(names)
            for b in names[i + 1:]
        )
        if not any_shared:
            issues.append(_issue(
                "warning",
                "NO_SHARED_ESSENTIAL_LABELS",
                "no pair of concepts shares any essential feature label, so the "
                "is-a DAG will be empty and every concept will be isolated.",
                suggestion=(
                    "If a hierarchy is intended: give the parent a small set of "
                    "atomic essential labels, and make each child repeat ALL parent "
                    "labels verbatim (character-identical) plus at least one new "
                    "differentia label."
                ),
            ))


def _lint_feature(concept_name: str, raw_feature: Dict[str, Any], issues: List[Dict[str, Any]]) -> None:
    feature = raw_feature.get("feature")
    feature_text = feature.strip() if isinstance(feature, str) else ""
    ftype = raw_feature.get("type")
    evidence = raw_feature.get("evidence")
    relation_hint = raw_feature.get("relation_hint")

    if not isinstance(feature, str) or not feature.strip():
        issues.append(_issue(
            "error",
            "MISSING_FEATURE_LABEL",
            "feature must be a non-empty string.",
            concept=concept_name,
        ))
    else:
        lower_feature = feature_text.lower()
        if any(pattern in lower_feature for pattern in PLACEHOLDER_PATTERNS):
            issues.append(_issue(
                "error",
                "PLACEHOLDER_FEATURE",
                "feature label contains a placeholder instead of explicit inherited features.",
                concept=concept_name,
                feature=feature_text,
                suggestion="Repeat the parent essential feature labels explicitly and add differentia.",
            ))
        if _is_sentence_like(feature_text):
            issues.append(_issue(
                "warning",
                "SENTENCE_LIKE_FEATURE",
                "feature label looks like prose. Normalize it to an atomic noun-like or predicate-like label.",
                concept=concept_name,
                feature=feature_text,
            ))

    if not isinstance(ftype, str) or not ftype.strip():
        issues.append(_issue(
            "error",
            "MISSING_FEATURE_TYPE",
            "feature type is required.",
            concept=concept_name,
            feature=feature_text or None,
        ))
    elif ftype not in VALID_TYPES:
        issues.append(_issue(
            "error",
            "UNKNOWN_FEATURE_TYPE",
            f"unknown feature type: {ftype}",
            concept=concept_name,
            feature=feature_text or None,
            suggestion=f"Use one of: {', '.join(sorted(VALID_TYPES))}.",
        ))

    if not isinstance(evidence, str) or len(evidence.strip()) < 4:
        issues.append(_issue(
            "error",
            "MISSING_EVIDENCE",
            "evidence must be a source-backed string with at least 4 characters.",
            concept=concept_name,
            feature=feature_text or None,
        ))

    if isinstance(relation_hint, str) and relation_hint.strip():
        expected = _expected_type_from_hint(relation_hint)
        if expected and isinstance(ftype, str) and ftype in VALID_TYPES and expected != ftype:
            issues.append(_issue(
                "error",
                "RELATION_HINT_TYPE_CONFLICT",
                f"relation_hint '{relation_hint}' implies type '{expected}', but feature type is '{ftype}'.",
                concept=concept_name,
                feature=feature_text or None,
                suggestion=f"Change type to '{expected}' or revise relation_hint.",
            ))

    if ftype == "structural_composition":
        if not isinstance(relation_hint, str) or not relation_hint.strip():
            issues.append(_issue(
                "warning",
                "MISSING_STRUCTURAL_RELATION_HINT",
                "structural_composition should include relation_hint such as has_part or component_of.",
                concept=concept_name,
                feature=feature_text or None,
            ))
        evidence_text = evidence if isinstance(evidence, str) else ""
        if _has_any(evidence_text, WEAK_STRUCTURAL_MARKERS) and not _has_any(evidence_text, STRONG_STRUCTURAL_MARKERS):
            issues.append(_issue(
                "warning",
                "WEAK_STRUCTURAL_EVIDENCE",
                "weak evidence alone does not justify structural_composition.",
                concept=concept_name,
                feature=feature_text or None,
                suggestion="Use functional/essential/contextual type unless the source states structural containment.",
            ))


def _finish(issues: List[Dict[str, Any]]) -> Dict[str, Any]:
    errors = sum(1 for issue in issues if issue["severity"] == "error")
    warnings = sum(1 for issue in issues if issue["severity"] == "warning")
    if errors:
        status = "LINT_ERROR"
    elif warnings:
        status = "LINT_WARNING"
    else:
        status = "LINT_PASS"
    return {
        "status": status,
        "issues": issues,
        "summary": {
            "errors": errors,
            "warnings": warnings,
        },
    }


if __name__ == "__main__":
    sample = [
        {"name": "x", "features": [
            {
                "feature": "based on y",
                "type": "structural_composition",
                "evidence": "x is based on y",
            }
        ]}
    ]
    import json
    print(json.dumps(lint_concepts(sample), ensure_ascii=False, indent=2))
