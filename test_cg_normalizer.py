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
