"""O1_PMB_LEMMA_NO_SENSE_V1 평가 profile — synset 술어명 정규화.

D-E2E-v1-22 Q22.3(a*): WSD를 estimand 밖으로 — synset 술어명을
lemma·소문자로 정규화하되 **occurrence 정체·arity·argument topology·scope
위치 보존, 동일 lemma 노드 병합 금지, 커널 전역 정규화 금지**(§9-§10).

위치는 실험 폴더 — 커널이 아니다. 다른 실험에선 WSD가 estimand일 수 있다.
이 profile은 end-to-end 리허설이 실측한 실패(표면형 vs 어간 불일치만으로
3/3 FAIL)를 죽이기 위해 쓰인다.

§9 규칙: sense 구별 무시 ≠ occurrence 정체 붕괴 — 병합 금지.
§10 규칙: 이 정규화는 절대 커널 모듈에 들어가지 않는다. 커널이 이 파일을
모르고, 커널 코드 어디도 "LEMMA_NO_SENSE"를 언급하지 않아야 한다.

**입력 변이 금지 사유**: normalized oracle IR을 expected_ir에 다시 쓰면
expected_ir 해싱이 오염되어 다른 실험의 oracle 검증이 거짓 통과할 수 있다.
따라서 항상 deep copy를 기초로 작업하고 원본은 불변이어야 한다.
"""
from __future__ import annotations

import copy
import re
from typing import Any


PROFILE_ID = "O1_PMB_LEMMA_NO_SENSE_V1"
FOLIO_PROFILE_ID = "FOLIO_LABEL_LOWERCASE_V1"

# desugar (_stage2_canonical_core.py) identifies neutral restrictions
# by the literal name "True"; the codec must never touch it.
RESERVED_LABELS = ("True",)

# WordNet synset pattern: lemma.pos.number
# e.g., "Zorble.n.01", "glim.a.02", "zorble_krell.n.03"
SYNSET_PATTERN = re.compile(r"^(.+)\.(n|v|a|r|x)\.(\d+)$")


def normalize_predicate_labels(formula: dict) -> dict:
    """Return a new formula where synset predicate names are replaced by lowercased lemmas.

    The input is never mutated. All structural elements (quantifiers, args, arity,
    topology) are preserved. Same-lemma collisions do not merge nodes.

    Idempotent: normalize(normalize(x)) == normalize(x).
    """
    # Deep copy to ensure input is never mutated
    result = copy.deepcopy(formula)
    _normalize_in_place(result)
    return result


def _normalize_in_place(node: Any) -> None:
    """Recursively normalize a node tree (already copied)."""
    if not isinstance(node, dict):
        return

    # Handle predicate nodes
    if node.get("kind") == "pred" and "name" in node:
        match = SYNSET_PATTERN.match(node["name"])
        if match:
            # Extract group(1) (the lemma) and lowercase it
            lemma = match.group(1).lower()
            node["name"] = lemma

    # Recursively process all dict and list values
    for key, value in node.items():
        if isinstance(value, dict):
            _normalize_in_place(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _normalize_in_place(item)


def normalize_folio_labels(formula: dict) -> dict:
    """Return a new formula where all predicate names are lowercased, except reserved tokens.

    D-E2E-v1-24 Q24.1: FOLIO oracle 술어는 대문자/CamelCase로 남는데 template의
    subject가 소문자를 강제하므로 라벨 불일치만으로 실패한다. FOLIO 한정으로
    소문자화 codec만 허용한다 (분절·동의어·lemma·병합 금지).

    The input is never mutated. All structural elements (quantifiers, args, arity,
    topology) are preserved. Lowercasing collisions do not merge nodes.

    Idempotent: normalize(normalize(x)) == normalize(x).
    """
    # Deep copy to ensure input is never mutated
    result = copy.deepcopy(formula)
    _normalize_folio_in_place(result)
    return result


def _normalize_folio_in_place(node: Any) -> None:
    """Recursively lowercase predicate names (already copied), except reserved labels."""
    if not isinstance(node, dict):
        return

    # Handle predicate nodes
    if node.get("kind") == "pred" and "name" in node:
        if node["name"] not in RESERVED_LABELS:
            node["name"] = node["name"].lower()

    # Recursively process all dict and list values
    for key, value in node.items():
        if isinstance(value, dict):
            _normalize_folio_in_place(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _normalize_folio_in_place(item)


def normalize_labels_for_case(case_id: str, formula: dict) -> dict:
    """Dispatch to the appropriate codec based on the case_id prefix.

    D-E2E-v1-24: 비교층의 source별 codec dispatch 단일 진입점. PMB와 FOLIO
    codec은 절대 조용히 교차 적용되지 않는다.

    Args:
        case_id: source-bound case identifier (e.g., "PMB-p09-d2243", "FOLIO-175p1")
        formula: normalized IR formula dict

    Returns:
        Formula with labels normalized according to source codec.

    Raises:
        ValueError: if case_id prefix is not recognized (fail-closed).
    """
    if case_id.startswith("PMB-"):
        return normalize_predicate_labels(formula)
    elif case_id.startswith("FOLIO-"):
        return normalize_folio_labels(formula)
    else:
        raise ValueError(f"Unknown case_id prefix: {case_id}")
