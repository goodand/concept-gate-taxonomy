#!/usr/bin/env python3
"""cg_owl 입력 경계 가드 회귀 테스트 — 아키텍처 분석 §7.5 fixture 고정.

test_cg_owl.py(P1-P4)와 달리 reasoner를 실행하지 않으므로 Java가 없어도
돈다 — build 단계 가드는 skip 없이 항상 검증된다.

배경: fuzz는 normalizer 표면만 덮었고, classify_owl 경계는
concepts=[7] → TypeError, differentia=[7] → AttributeError로
unhandled crash했다. 모든 crash는 SerializationError(→ 서버에서
stage='owl-serialize' 구조화 오류)로 바뀌어야 한다.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

pytest.importorskip("owlready2", reason="owlready2 미설치 (선택 의존성)")

from conceptgate import cg_owl


def _build(**kw):
    args = dict(concepts=[], object_properties=[], data_properties=[],
                disjoint_groups=[])
    args.update(kw)
    return cg_owl.build_ontology(**args)


# ── §7.5 원 crash fixture 2건 ────────────────────────────────────────

def test_concept_item_int_is_structured_error():
    """concepts=[7] — TypeError('int' not subscriptable)로 crash했던 입력."""
    with pytest.raises(cg_owl.SerializationError, match="concepts\\[0\\]"):
        _build(concepts=[7])


def test_differentia_item_int_is_structured_error():
    """differentia=[7] — AttributeError('int' has no 'get')로 crash했던 입력."""
    with pytest.raises(cg_owl.SerializationError, match="differentia\\[0\\]"):
        _build(concepts=[{"name": "X", "definition_kind": "defined",
                          "differentia": [7]}])


# ── 나머지 경계 ─────────────────────────────────────────────────────

def test_concepts_must_be_list():
    with pytest.raises(cg_owl.SerializationError, match="must be list"):
        _build(concepts="문자열")


def test_name_required_nonempty_str():
    for bad in (None, 7, "", [1]):
        with pytest.raises(cg_owl.SerializationError, match="name"):
            _build(concepts=[{"name": bad}])


def test_genus_unhashable_is_structured_error():
    """genus=[1,2] — classes.get(unhashable) TypeError였던 표면."""
    with pytest.raises(cg_owl.SerializationError, match="genus"):
        _build(concepts=[{"name": "X", "genus": [1, 2]}])


def test_filler_and_property_must_be_str():
    with pytest.raises(cg_owl.SerializationError, match="filler"):
        _build(concepts=[{"name": "X", "differentia": [
            {"property": "p", "restriction": "some", "filler": [1]}]}],
            object_properties=["p"])
    with pytest.raises(cg_owl.SerializationError, match="property"):
        _build(concepts=[{"name": "X", "differentia": [
            {"property": None, "restriction": "some", "filler": "X"}]}])


def test_value_filler_must_be_literal():
    with pytest.raises(cg_owl.SerializationError, match="value filler"):
        _build(concepts=[{"name": "X", "differentia": [
            {"property": "p", "restriction": "value", "filler": {"a": 1}}]}],
            data_properties=[{"name": "p"}])


def test_data_property_item_must_be_dict_with_name():
    with pytest.raises(cg_owl.SerializationError, match="data_properties"):
        _build(data_properties=[7])
    with pytest.raises(cg_owl.SerializationError, match="name"):
        _build(data_properties=[{"functional": True}])


def test_disjoint_group_unknown_class_is_structured_error():
    """classes[n] KeyError였던 표면 — 미선언 클래스 참조."""
    with pytest.raises(cg_owl.SerializationError, match="Ghost"):
        _build(concepts=[{"name": "X"}], disjoint_groups=[["X", "Ghost"]])


def test_disjoint_group_shapes():
    with pytest.raises(cg_owl.SerializationError):
        _build(disjoint_groups="문자열")
    with pytest.raises(cg_owl.SerializationError):
        _build(disjoint_groups=[7])
    with pytest.raises(cg_owl.SerializationError):
        _build(concepts=[{"name": "X"}], disjoint_groups=[[7]])


def test_none_collections_mean_absent():
    """None은 '미제공' 의미론 — 빈 목록과 동일하게 통과해야 한다."""
    world, onto, classes = _build(concepts=[
        {"name": "X", "differentia": None, "necessary_only": None}])
    assert "X" in classes


def test_valid_build_still_works():
    """가드가 정상 경로를 깨지 않는다 — P1 Bird/Airplane 입력 그대로."""
    world, onto, classes = _build(
        concepts=[
            {"name": "Wing", "definition_kind": "primitive"},
            {"name": "Bird", "definition_kind": "primitive",
             "differentia": [{"property": "hasPart", "restriction": "some",
                              "filler": "Wing"}]},
        ],
        object_properties=["hasPart"])
    assert set(classes) == {"Wing", "Bird"}


def test_is_subclass_of_nonstr_names():
    world, onto, _ = _build(concepts=[{"name": "X"}])
    with pytest.raises(cg_owl.SerializationError, match="must be str"):
        cg_owl.is_subclass_of(onto, 7, "X")


# ── stereotype (리뷰 발견 4) ──────────────────────────────────────────

def test_unknown_stereotype_is_structured_error():
    with pytest.raises(cg_owl.SerializationError, match="stereotype"):
        _build(concepts=[{"name": "X", "stereotype": "wizard"}])


def test_stereotype_unhashable_is_structured_error():
    """stereotype=[1,2] — genus와 같은 부류의 unhashable-in-frozenset crash
    (fuzz로 재현됨: `not in GUFO_STEREOTYPES` 앞에 isinstance 가드 없었음)."""
    with pytest.raises(cg_owl.SerializationError, match="stereotype"):
        _build(concepts=[{"name": "X", "stereotype": [1, 2]}])


def test_no_stereotype_build_unaffected():
    """stereotype을 안 쓰는 기존 호출은 마커가 생기지 않는다."""
    world, onto, classes = _build(
        concepts=[{"name": "Wing", "definition_kind": "primitive"}])
    assert set(classes) == {"Wing"}
    assert onto["_GUFOPhase"] is None


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
