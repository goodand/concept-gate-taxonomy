#!/usr/bin/env python3
"""D-E2E-v1-24 Q24.2: predicate_label_reachability — 술어 도달성 판정기.

판정 §4 동결 기계 규칙 구현 (codec 정규화 후 문장 후보 기반):
  · derive_candidates: 문장의 소문자 영숫자 토큰에서 연속 이음과 기계적 복수형 제거
  · label_reachable: 라벨이 후보 집합에 있는가 (RESERVED_LABELS는 oracle 구조 토큰)
  · path_a_labels / path_b_labels: 술어명 추출 (두 경로 합의 필수)
  · fixture_reachability: 종합 판정 (경로 불일치 = 부적격, 도달성 미판정)

이 규칙의 적격성 판정 용도에서 (ii) 복수형 제거가 codec의 lemma 금지와 모순
아니라는 점: codec은 **채점 비교층**에서 라벨을 바꾸는 장치라 어휘 변형이
금지되지만(D-24 §2), 이 규칙은 **적격성 판정**에서 후보 집합을 넓히는 장치
— oracle 라벨은 절대 변형되지 않는다.

V1 scan artifacts (folio_eligibility_scan.json) 동결 — 이 파일은 수정 금지.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from _stage2_eval_profile import normalize_folio_labels, RESERVED_LABELS  # noqa: E402
from conceptgate import cg_fol_adapter as fa  # noqa: E402


def derive_candidates(sentence: str) -> set[str]:
    """Extract candidate labels from a sentence using the frozen derivation rule.

    Algorithm:
      1. tokenize to [a-z0-9]+ in lowercase
      2. candidates = every contiguous join of 1..4 tokens
      3. + for each token w: w[:-1] if w ends with "s", w[:-2] if w ends with "es"

    Args:
        sentence: Natural language sentence.

    Returns:
        Set of candidate label strings.

    Raises:
        ValueError: if sentence is empty or whitespace-only.
    """
    if not sentence or not sentence.strip():
        raise ValueError("sentence cannot be empty or whitespace-only")

    # Extract lowercase alphanumeric tokens
    tokens = re.findall(r"[a-z0-9]+", sentence.lower())

    candidates = set()

    # (i) contiguous joins of 1..4 tokens
    n = len(tokens)
    for i in range(n):
        for length in range(1, 5):  # 1, 2, 3, 4
            if i + length <= n:
                join = "".join(tokens[i:i+length])
                candidates.add(join)

    # (ii) mechanical plural strip: for each token
    for w in tokens:
        if w.endswith("es") and len(w) > 2:
            candidates.add(w[:-2])
        elif w.endswith("s") and len(w) > 1:
            candidates.add(w[:-1])

    return candidates


def label_reachable(label: str, sentence: str) -> bool:
    """Test if a label is reachable (in derived candidates or RESERVED_LABELS).

    Structural tokens like "True" (neutral restriction markers) are always
    reachable. Oracle labels are tested via the codec (lowercase for FOLIO).

    Args:
        label: Predicate label (may be CamelCase).
        sentence: Natural language sentence.

    Returns:
        True if label is reachable.
    """
    # RESERVED_LABELS are structural, always reachable
    if label in RESERVED_LABELS:
        return True

    # Codec: FOLIO labels are lowercased (bare .lower() is fine)
    normalized = label if label in RESERVED_LABELS else label.lower()

    candidates = derive_candidates(sentence)
    return normalized in candidates


def path_a_labels(fol: str) -> set[str]:
    """Extract predicate names via the real adapter (Path A).

    Walk the IR returned by adapt_fol, collecting every {"kind":"pred"}
    name except names in RESERVED_LABELS.

    Args:
        fol: FOL string.

    Returns:
        Set of predicate names from the IR.
    """
    ir = fa.adapt_fol(fol)
    labels = set()

    def walk(node):
        if isinstance(node, dict):
            if node.get("kind") == "pred" and "name" in node:
                name = node["name"]
                if name not in RESERVED_LABELS:
                    labels.add(name)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(ir)
    return labels


def path_b_labels(fol: str) -> set[str]:
    """Extract predicate names via regex census (Path B).

    Independent of the adapter: regex FOL string for predicate applications
    with pattern ([A-Za-z][A-Za-z0-9_]*)\\( and return captured names.
    Arguments and quantified variables are never immediately followed by "("
    (quantifier syntax has whitespace, e.g., "∃y ("), so they are naturally
    excluded.

    Args:
        fol: FOL string.

    Returns:
        Set of predicate names matched by the pattern.
    """
    pattern = r"([A-Za-z][A-Za-z0-9_]*)\("
    matches = re.findall(pattern, fol)
    return set(matches)


def fixture_reachability(fol: str, sentence: str) -> dict:
    """Comprehensive reachability verdict: paths must agree.

    Contract:
      - paths_agree = path_a_labels(fol) == path_b_labels(fol)
      - if not paths_agree: reachable must be False, unreachable_labels = []
      - else: unreachable_labels = sorted(l for l in labels if not label_reachable(l, sentence))
              reachable = (unreachable_labels == [])

    Args:
        fol: FOL formula string.
        sentence: Natural language sentence.

    Returns:
        dict with keys:
          - "reachable" (bool): whether all labels are reachable
          - "paths_agree" (bool): whether Path A and Path B label sets match
          - "unreachable_labels" (list[str]): sorted labels not reachable ([] if paths disagree)
    """
    a_labels = path_a_labels(fol)
    b_labels = path_b_labels(fol)
    paths_agree = a_labels == b_labels

    if not paths_agree:
        return {
            "reachable": False,
            "paths_agree": False,
            "unreachable_labels": []
        }

    # Paths agree: check reachability
    unreachable = [
        l for l in a_labels
        if not label_reachable(l, sentence)
    ]
    unreachable_labels = sorted(unreachable)
    reachable = len(unreachable_labels) == 0

    return {
        "reachable": reachable,
        "paths_agree": True,
        "unreachable_labels": unreachable_labels
    }
