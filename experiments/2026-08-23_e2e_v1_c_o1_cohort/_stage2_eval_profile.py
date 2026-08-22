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
