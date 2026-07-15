#!/usr/bin/env python3
"""cg_normalizer 단계별 테스트 — 각 stage의 성공/실패 경로를 모두 계약."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from conceptgate import cg_normalizer as N


TEXT = "개는 갯과의 가축화된 동물이다. 고양이는 고양잇과의 동물이다. 말은 초식 동물이다."


def _snap():
    r = N.make_snapshot(TEXT, uri="local:test")
    assert r["ok"]
    return r["snapshot"]


# ── stage: snapshot ──────────────────────────────────────

def test_snapshot_ok_and_hash_stable():
    a, b = N.make_snapshot(TEXT), N.make_snapshot(TEXT)
    assert a["ok"] and a["snapshot"]["sha256"] == b["snapshot"]["sha256"]


def test_snapshot_rejects_empty_and_oversize():
    assert N.make_snapshot("")["errors"][0]["code"] == "EMPTY_TEXT"
    big = "가" * (N.MAX_TEXT_CHARS + 1)
    assert N.make_snapshot(big)["errors"][0]["code"] == "TEXT_TOO_LARGE"


def test_snapshot_nfc_normalizes():
    # NFD 입력(자모 분리)도 NFC로 고정되어 같은 해시가 나와야 함
    import unicodedata
    nfd = unicodedata.normalize("NFD", "개")
    r1, r2 = N.make_snapshot(nfd), N.make_snapshot("개")
    assert r1["snapshot"]["sha256"] == r2["snapshot"]["sha256"]


# ── stage: lookup ────────────────────────────────────────

def test_lookup_known_surface_returns_candidates():
    r = N.lookup_senses("개")
    assert r["ok"] and len(r["candidates"]) == 2  # 동물/단위 두 sense
    assert not r["out_of_inventory"]


def test_lookup_unknown_surface_flags_out_of_inventory():
    r = N.lookup_senses("전혀없는말")
    assert r["ok"] and r["out_of_inventory"] and r["candidates"] == []


# ── stage: selection ─────────────────────────────────────

def test_selection_valid_sense_and_span():
    snap = _snap()
    cands = N.lookup_senses("개")["candidates"]
    sel = {"sense_id": cands[0]["sense_id"],
           "evidence_span": {"start": 0, "end": 15},
           "quote": snap["text"][0:15],
           "source_sha256": snap["sha256"]}
    r = N.validate_selection(sel, cands, snap)
    assert r["ok"] and r["verification_status"] == "source_span_verified"


def test_selection_rejects_fabricated_sense():
    snap = _snap()
    cands = N.lookup_senses("개")["candidates"]
    r = N.validate_selection({"sense_id": "memory:개:999"}, cands, snap)
    assert not r["ok"] and r["stage"] == "selection"
    assert r["errors"][0]["code"] == "SENSE_NOT_IN_CANDIDATES"


def test_selection_rejects_bad_span_and_wrong_quote_and_hash():
    snap = _snap()
    cands = N.lookup_senses("개")["candidates"]
    sid = cands[0]["sense_id"]
    r = N.validate_selection(
        {"sense_id": sid, "evidence_span": {"start": 5, "end": 99999}},
        cands, snap)
    assert r["errors"][0]["code"] == "SPAN_OUT_OF_BOUNDS"
    r = N.validate_selection(
        {"sense_id": sid, "evidence_span": {"start": 0, "end": 3},
         "quote": "다른내용"}, cands, snap)
    assert r["errors"][0]["code"] == "QUOTE_MISMATCH"
    r = N.validate_selection(
        {"sense_id": sid, "source_sha256": "deadbeef"}, cands, snap)
    assert r["errors"][0]["code"] == "SOURCE_HASH_MISMATCH"


def test_selection_allows_local_namespace():
    snap = _snap()
    r = N.validate_selection({"sense_id": "local:신조어:001"}, [], snap)
    assert r["ok"] and r["verification_status"] == "unverified"


# ── stage: crosswalk ─────────────────────────────────────

def test_crosswalk_exact_and_conditional():
    assert N.map_relation("stuff_object")["decision"]["relation_hint"] == "material_of"
    assert N.map_relation("stuff_object")["decision"]["feature_type"] == \
        "structural_composition"
    assert N.map_relation("place_area")["decision"]["mapping_status"] == "conditional"


def test_crosswalk_rejects_feature_activity_and_unknown():
    r = N.map_relation("feature_activity")
    assert not r["ok"] and r["errors"][0]["code"] == "UNMAPPED_RELATION"
    r = N.map_relation("owns")   # Winston이 meronymy에서 제외한 소유 관계
    assert not r["ok"] and r["errors"][0]["code"] == "UNKNOWN_RELATION_KIND"


# ── stage: assemble + lint (통합) ────────────────────────

def _span(text, phrase):
    i = text.find(phrase)
    assert i >= 0, f"fixture 문구 없음: {phrase}"
    return {"start": i, "end": i + len(phrase)}


def _dog_cat_horse_bundle(snap):
    t = snap["text"]
    def c(name, extra_label, extra_phrase):
        return {"name": name, "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")},
            {"label": extra_label, "relation": "is_a",
             "evidence_span": _span(t, extra_phrase)},
        ]}
    return {"snapshot": snap, "concepts": [
        # 부모 개념 — 이것이 없으면 subset 포함이 성립하지 않아 DAG가 비게 된다
        {"name": "동물", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")}]},
        c("개", "갯과", "갯과의 가축화된"),
        c("고양이", "고양잇과", "고양잇과의 동물"),
        c("말", "초식", "초식 동물이다"),
    ]}


def test_assemble_happy_path_lints_clean():
    snap = _snap()
    r = N.assemble_concepts(_dog_cat_horse_bundle(snap))
    assert r["ok"], r.get("errors")
    assert r["stage"] == "complete"
    assert len(r["concepts_json"]["concepts"]) == 4
    # 모든 claim이 L1(span 검증) 상태여야 함
    assert all(c["verification_status"] == "source_span_verified"
               for c in r["claims"])
    # snapshot 원문은 결과에 포함하지 않는다 (source 메타만)
    assert "text" not in r["source"]


def test_assembled_output_passes_concept_gate():
    """조립 산출물이 실제 concept-gate 파이프라인을 PASS해야 한다 (end-to-end)."""
    import json
    from conceptgate import concept_gate_v7 as cg
    snap = _snap()
    r = N.assemble_concepts(_dog_cat_horse_bundle(snap))
    assert r["ok"]
    concepts, rep = cg.ParseGate.parse(
        json.dumps(r["concepts_json"], ensure_ascii=False))
    assert rep.passed
    out = cg.ConceptPipeline().run([concepts])
    assert out["status"] == "PASS", out["status"]
    assert sorted(dict(out["result"]["dag"]).get("동물", [])) == \
        ["개", "고양이", "말"]


def test_assemble_reports_stage_of_failure():
    snap = _snap()
    # span 위조 → selection stage 오류로 분류되어야 함 (원인 파악)
    bundle = {"snapshot": snap, "concepts": [
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": {"start": 0, "end": 999999}}]}]}
    r = N.assemble_concepts(bundle)
    assert not r["ok"] and r["stage"] == "selection"
    assert r["errors"][0]["code"] == "SPAN_OUT_OF_BOUNDS"
    # 미지 relation → crosswalk stage
    bundle2 = {"snapshot": snap, "concepts": [
        {"name": "개", "features": [
            {"label": "동물", "relation": "owns",
             "evidence_text": "소유 관계라고 주장"}]}]}
    r2 = N.assemble_concepts(bundle2)
    assert not r2["ok"] and r2["stage"] == "crosswalk"


def test_assemble_rejects_evidence_free_feature():
    snap = _snap()
    bundle = {"snapshot": snap, "concepts": [
        {"name": "개", "features": [{"label": "동물", "relation": "is_a"}]}]}
    r = N.assemble_concepts(bundle)
    assert not r["ok"]
    assert any(e["code"] == "MISSING_EVIDENCE" for e in r["errors"])


def test_assemble_caps_bound_inputs():
    snap = _snap()
    many = {"snapshot": snap, "concepts": [
        {"name": f"c{i}", "features": []} for i in range(N.MAX_CONCEPTS + 1)]}
    r = N.assemble_concepts(many)
    assert not r["ok"] and r["errors"][0]["code"] == "TOO_MANY_CONCEPTS"


# ── claim 방향 (리뷰 발견 1b) ────────────────────────────
#
# 입력 규약(DISAMBIGUATION_PROTOCOL §4): "X는 Y의 일종"(is_a)
#   → concept X 가 label Y 를 is_a feature 로 갖는다. 즉 label 이 부모다.
# 따라서 is_a claim 은 subject=X(자식), object=Y(부모) 여야 한다.
#
# 반면 부분-전체 어휘는 전부 <feature> <hint> <concept> 로 읽힌다
#   (Winston: pedal component_of bike) → subject=label, object=name.
# 방향이 관계마다 다르므로 둘 다 고정한다.

def _claim_for(r, label):
    hits = [c for c in r["claims"] if label in (c["subject"], c["object"])]
    assert hits, f"claim 없음: {label}"
    return hits[0]


def test_is_a_claim_points_child_to_parent():
    """개는 동물의 일종 → (개 is_a 동물). 역전이면 계층이 뒤집힌다."""
    snap = _snap()
    t = snap["text"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")}]}]})
    assert r["ok"], r.get("errors")
    c = _claim_for(r, "동물")
    assert c["predicate"] == "is_a"
    assert c["subject"] == "개", f"주어가 자식이어야 한다: {c}"
    assert c["object"] == "동물", f"목적어가 부모여야 한다: {c}"


def test_partwhole_claim_points_part_to_whole():
    """자전거의 부품 페달 → (페달 component_of 자전거). is_a와 방향이 반대."""
    res = N.make_snapshot("자전거는 페달을 부품으로 가진다.", uri="local:pw")
    assert res["ok"]
    snap = res["snapshot"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "자전거", "features": [
            {"label": "페달", "relation": "component_integral",
             "evidence_span": _span(snap["text"], "페달을 부품으로")}]}]})
    assert r["ok"], r.get("errors")
    c = _claim_for(r, "페달")
    assert c["predicate"] == "component_of"
    assert c["subject"] == "페달", f"주어가 부분이어야 한다: {c}"
    assert c["object"] == "자전거", f"목적어가 전체여야 한다: {c}"


# ── selection 검증이 실제 경로에 배선돼 있는가 (리뷰 발견 6) ──
#
# validate_selection은 sense 후보 대조·span 길이 상한·quote 일치를 검사한다.
# 그러나 assemble/map_owl이 이를 호출하지 않고 자체 span 로직만 쓰고 있었다.
# 따라서 단위 테스트는 통과하는데 실제 도구 경로로는 위조가 통과했다.
# 아래는 "함수가 존재한다"가 아니라 "실제 경로가 막는다"를 계약한다.

def test_assemble_rejects_fabricated_sense_id():
    """후보에 없는 sense_id는 assemble에서 거부돼야 한다."""
    snap = _snap()
    t = snap["text"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "개", "sense_id": "memory:개:999",   # 인벤토리에 없는 sense
         "features": [{"label": "동물", "relation": "is_a",
                       "evidence_span": _span(t, "가축화된 동물이다")}]}]})
    assert not r["ok"]
    assert any(e["code"] == "SENSE_NOT_IN_CANDIDATES" for e in r["errors"]), r["errors"]


def test_assemble_allows_local_sense_id():
    """local: 네임스페이스는 사전 밖 신조어용으로 허용된다."""
    snap = _snap()
    t = snap["text"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "개", "sense_id": "local:개:001",
         "features": [{"label": "동물", "relation": "is_a",
                       "evidence_span": _span(t, "가축화된 동물이다")}]}]})
    assert r["ok"], r.get("errors")


def test_assemble_rejects_quote_mismatch():
    """quote가 span 내용과 다르면 거부 — evidence laundering 차단."""
    snap = _snap()
    t = snap["text"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다"),
             "quote": "전혀 다른 내용"}]}]})
    assert not r["ok"]
    assert any(e["code"] == "QUOTE_MISMATCH" for e in r["errors"]), r["errors"]


def test_assemble_rejects_oversized_span():
    """span 길이 상한(MAX_SPAN_CHARS)을 assemble도 강제해야 한다."""
    long_text = "개는 동물이다. " + ("가" * (N.MAX_SPAN_CHARS + 100))
    snap = N.make_snapshot(long_text)["snapshot"]
    r = N.assemble_concepts({"snapshot": snap, "concepts": [
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": {"start": 0, "end": N.MAX_SPAN_CHARS + 50}}]}]})
    assert not r["ok"]
    assert any(e["code"] == "SPAN_TOO_LONG" for e in r["errors"]), r["errors"]


def test_owlmap_rejects_quote_mismatch():
    """map_owl 경로도 동일하게 quote를 대조해야 한다."""
    snap = _geo_snap()
    b = _geo_bundle(snap)
    b["concepts"][1]["differentia"][0]["quote"] = "위조된 인용"
    r = N.map_to_owl(b)
    assert not r["ok"]
    assert any(e["code"] == "QUOTE_MISMATCH" for e in r["errors"]), r["errors"]


def test_owlmap_rejects_oversized_span():
    long_text = GEO + ("가" * (N.MAX_SPAN_CHARS + 100))
    snap = N.make_snapshot(long_text)["snapshot"]
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "평행사변형", "definition_kind": "primitive"},
        {"name": "직사각형", "definition_kind": "defined",
         "kind_rationale": "r", "genus": "평행사변형",
         "differentia": [
             {"property": "직각성", "restriction": "value", "filler": True,
              "evidence_span": {"start": 0, "end": N.MAX_SPAN_CHARS + 50}}]}]})
    assert not r["ok"]
    assert any(e["code"] == "SPAN_TOO_LONG" for e in r["errors"]), r["errors"]


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))


# ── stage: owl-map (typed 제안 → cg_owl 입력) ────────────

GEO = "평행사변형은 사각형이다. 직사각형은 네 각이 직각인 평행사변형이다. 정사각형은 네 변이 같고 네 각이 직각인 평행사변형이다."


def _geo_snap():
    return N.make_snapshot(GEO)["snapshot"]


def _geo_bundle(snap):
    t = snap["text"]
    def sp(p):
        i = t.find(p); return {"start": i, "end": i + len(p)}
    return {"snapshot": snap, "concepts": [
        {"name": "평행사변형", "definition_kind": "primitive"},
        {"name": "직사각형", "definition_kind": "defined",
         "kind_rationale": "직각 조건이 평행사변형 안에서 필요충분",
         "genus": "평행사변형",
         "differentia": [
             {"property": "직각성", "restriction": "value", "filler": True,
              "evidence_span": sp("네 각이 직각인 평행사변형")}]},
        {"name": "정사각형", "definition_kind": "defined",
         "kind_rationale": "등변+직각이 평행사변형 안에서 필요충분",
         "genus": "평행사변형",
         "differentia": [
             {"property": "직각성", "restriction": "value", "filler": True,
              "evidence_span": sp("네 각이 직각인 평행사변형")},
             {"property": "등변성", "restriction": "value", "filler": True,
              "evidence_span": sp("네 변이 같고")}]},
    ]}


def test_owlmap_happy_path():
    r = N.map_to_owl(_geo_bundle(_geo_snap()))
    assert r["ok"], r.get("errors")
    assert len(r["owl"]["concepts"]) == 3
    assert {d["name"] for d in r["owl"]["data_properties"]} == {"직각성", "등변성"}
    assert all(c["verification_status"] == "source_span_verified"
               for c in r["claims"])


def test_owlmap_defined_requires_rationale_and_definition():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "defined", "genus": None}]})
    assert not r["ok"]
    assert any(e["code"] == "MISSING_KIND_RATIONALE" for e in r["errors"])
    r2 = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "defined",
         "kind_rationale": "근거 있음"}]})
    assert any(e["code"] == "DEFINED_WITHOUT_DEFINITION" for e in r2["errors"])


def test_owlmap_rejects_bad_kind_and_unknown_restriction():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "vibes"}]})
    assert any(e["code"] == "BAD_DEFINITION_KIND" for e in r["errors"])
    r2 = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "primitive",
         "differentia": [{"property": "p", "restriction": "magic",
                          "filler": "Y", "evidence_text": "근거근거"}]}]})
    assert any(e["code"] == "UNKNOWN_OWL_RESTRICTION" for e in r2["errors"])


def test_owlmap_forged_span_is_selection_stage():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "primitive",
         "differentia": [{"property": "p", "restriction": "value",
                          "filler": True,
                          "evidence_span": {"start": 0, "end": 99999}}]}]})
    assert not r["ok"] and r["stage"] == "selection"


def test_owlmap_vocab_matches_cg_owl():
    """cg_normalizer의 제한 어휘가 cg_owl과 어긋나면 안 된다 (drift 방지)."""
    try:
        from conceptgate import cg_owl
    except ImportError:
        import pytest
        pytest.skip("owlready2 미설치")
    assert N.OWL_RESTRICTIONS == cg_owl.SUPPORTED_RESTRICTIONS
    assert N.OWL_STEREOTYPES == cg_owl.GUFO_STEREOTYPES


def test_owlmap_rejects_bad_stereotype():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "primitive", "stereotype": "wizard"}]})
    assert not r["ok"]
    assert any(e["code"] == "BAD_STEREOTYPE" for e in r["errors"])


def test_owlmap_rejects_unhashable_stereotype():
    """stereotype=[1,2] — genus와 같은 부류의 unhashable-in-frozenset crash
    (fuzz로 재현됨)."""
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "primitive", "stereotype": [1, 2]}]})
    assert not r["ok"]
    assert any(e["code"] == "BAD_STEREOTYPE" for e in r["errors"])


def test_owlmap_phase_requires_genus():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "X", "definition_kind": "primitive", "stereotype": "phase"}]})
    assert not r["ok"]
    assert any(e["code"] == "PHASE_WITHOUT_GENUS" for e in r["errors"])


def test_owlmap_stereotype_passes_through_to_owl_concepts():
    snap = _geo_snap()
    r = N.map_to_owl({"snapshot": snap, "concepts": [
        {"name": "평행사변형", "definition_kind": "primitive",
         "stereotype": "kind"},
        {"name": "X", "definition_kind": "primitive",
         "genus": "평행사변형", "stereotype": "phase"}]})
    assert r["ok"], r.get("errors")
    by_name = {c["name"]: c for c in r["owl"]["concepts"]}
    assert by_name["평행사변형"]["stereotype"] == "kind"
    assert by_name["X"]["stereotype"] == "phase"
