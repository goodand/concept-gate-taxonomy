#!/usr/bin/env python3
"""cg_normalizer 타입 fuzz 하네스 — 모든 공개 진입점 × 변형 payload 행렬.

각 호출의 결과를 3분류로 보고한다:
  CRASH      unhandled exception (서버라면 ToolError로 비정상 노출)
  STRUCTURED {ok: False, stage, errors} 형태의 정상 거부
  ACCEPTED   ok=True (변형 입력이 통과 — 그 자체로 조사 대상)

사용: python3 fuzz_normalizer_types.py   → 표 + 요약 (CRASH>0이면 exit 1)
"""
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from conceptgate import cg_normalizer as N

SNAP = N.make_snapshot("개는 갯과의 가축화된 동물이다.")["snapshot"]

# 변형 값 팔레트: dict 자리에 넣어볼 것들
BAD = [None, 7, "문자열", [1, 2], True, 3.14]

CASES = []

def case(name, fn):
    CASES.append((name, fn))

# ── make_snapshot ──
for b in BAD:
    case(f"make_snapshot(text={type(b).__name__})",
         lambda b=b: N.make_snapshot(b))
case("make_snapshot(uri=list)", lambda: N.make_snapshot("텍스트입니다", uri=[1]))

# ── lookup_senses ──
for b in BAD:
    case(f"lookup_senses(surface={type(b).__name__})",
         lambda b=b: N.lookup_senses(b))

# ── validate_selection ──
for b in BAD:
    case(f"validate_selection(selection={type(b).__name__})",
         lambda b=b: N.validate_selection(b, [], SNAP))
    case(f"validate_selection(span={type(b).__name__})",
         lambda b=b: N.validate_selection(
             {"sense_id": "local:x:001", "evidence_span": b}, [], SNAP))
    case(f"validate_selection(candidates_item={type(b).__name__})",
         lambda b=b: N.validate_selection({"sense_id": "s"}, [b], SNAP))
case("validate_selection(snapshot=int)",
     lambda: N.validate_selection({"sense_id": "local:x:001"}, [], 7))

# ── assemble_concepts ──
for b in BAD:
    case(f"assemble(bundle={type(b).__name__})",
         lambda b=b: N.assemble_concepts(b))
    case(f"assemble(snapshot={type(b).__name__})",
         lambda b=b: N.assemble_concepts({"snapshot": b, "concepts": [
             {"name": "x", "features": []}]}))
    case(f"assemble(concept_item={type(b).__name__})",
         lambda b=b: N.assemble_concepts({"snapshot": SNAP, "concepts": [b]}))
    case(f"assemble(features={type(b).__name__})",
         lambda b=b: N.assemble_concepts({"snapshot": SNAP, "concepts": [
             {"name": "x", "features": b}]}))
    case(f"assemble(feature_item={type(b).__name__})",
         lambda b=b: N.assemble_concepts({"snapshot": SNAP, "concepts": [
             {"name": "x", "features": [b]}]}))
    case(f"assemble(span={type(b).__name__})",
         lambda b=b: N.assemble_concepts({"snapshot": SNAP, "concepts": [
             {"name": "x", "features": [
                 {"label": "y", "relation": "is_a", "evidence_span": b}]}]}))

# ── map_to_owl ──
for b in BAD:
    case(f"map_owl(bundle={type(b).__name__})",
         lambda b=b: N.map_to_owl(b))
    case(f"map_owl(snapshot={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": b, "concepts": [
             {"name": "x", "definition_kind": "primitive"}]}))
    case(f"map_owl(concept_item={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [b]}))
    case(f"map_owl(differentia={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "primitive", "differentia": b}]}))
    case(f"map_owl(diff_item={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "primitive",
              "differentia": [b]}]}))
    case(f"map_owl(span={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "primitive",
              "differentia": [{"property": "p", "restriction": "value",
                               "filler": True, "evidence_span": b}]}]}))
    case(f"map_owl(disjoint_with={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "primitive",
              "disjoint_with": b}]}))
    case(f"map_owl(stereotype={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "primitive",
              "stereotype": b}]}))
    case(f"map_owl(kind_rationale={type(b).__name__})",
         lambda b=b: N.map_to_owl({"snapshot": SNAP, "concepts": [
             {"name": "x", "definition_kind": "defined", "genus": None,
              "kind_rationale": b,
              "differentia": [{"property": "p", "restriction": "value",
                               "filler": True, "evidence_text": "근거근거"}]}]}))

# ── cg_owl.build_ontology (Java 불필요 — build 단계만, reasoner 미실행) ──
# 배경: classify_owl 경계는 이전 fuzz 범위 밖이었고 concepts=[7] 등이
# unhandled TypeError로 crash했다 (아키텍처 분석 §7.5).
try:
    from conceptgate import cg_owl as OWL
except ImportError:
    OWL = None
    print("[skip] owlready2 미설치 — cg_owl 표면 fuzz 생략", file=sys.stderr)

if OWL is not None:
    def owlcase(name, fn):
        """SerializationError → 구조화 오류로 정규화 (서버 계약과 동일)."""
        def wrapped(fn=fn):
            try:
                fn()
            except OWL.SerializationError as exc:
                return {"ok": False, "stage": "owl-serialize",
                        "errors": [{"stage": "owl-serialize",
                                    "code": "SERIALIZATION_ERROR",
                                    "detail": str(exc)}]}
            return {"ok": True}
        case(name, wrapped)

    def _build(**kw):
        args = dict(concepts=[], object_properties=[], data_properties=[],
                    disjoint_groups=[])
        args.update(kw)
        return OWL.build_ontology(**args)

    for b in BAD:
        owlcase(f"owl.build(concepts={type(b).__name__})",
                lambda b=b: _build(concepts=b))
        owlcase(f"owl.build(concept_item={type(b).__name__})",
                lambda b=b: _build(concepts=[b]))
        owlcase(f"owl.build(name={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": b}]))
        owlcase(f"owl.build(genus={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X", "genus": b}]))
        owlcase(f"owl.build(stereotype={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X", "stereotype": b}]))
        owlcase(f"owl.build(differentia={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X", "differentia": b}]))
        owlcase(f"owl.build(diff_item={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X",
                                              "differentia": [b]}]))
        owlcase(f"owl.build(filler={type(b).__name__})",
                lambda b=b: _build(
                    concepts=[{"name": "X", "differentia": [
                        {"property": "p", "restriction": "some",
                         "filler": b}]}],
                    object_properties=["p"]))
        owlcase(f"owl.build(property={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X", "differentia": [
                    {"property": b, "restriction": "some", "filler": "X"}]}]))
        owlcase(f"owl.build(objprop_item={type(b).__name__})",
                lambda b=b: _build(object_properties=[b]))
        owlcase(f"owl.build(dataprop_item={type(b).__name__})",
                lambda b=b: _build(data_properties=[b]))
        owlcase(f"owl.build(disjoint_groups={type(b).__name__})",
                lambda b=b: _build(disjoint_groups=b))
        owlcase(f"owl.build(disjoint_group_item={type(b).__name__})",
                lambda b=b: _build(disjoint_groups=[b]))
        owlcase(f"owl.build(disjoint_name={type(b).__name__})",
                lambda b=b: _build(concepts=[{"name": "X"}],
                                   disjoint_groups=[[b]]))
    owlcase("owl.build(value_filler=dict)",
            lambda: _build(
                concepts=[{"name": "X", "differentia": [
                    {"property": "p", "restriction": "value",
                     "filler": {"a": 1}}]}],
                data_properties=[{"name": "p"}]))
    owlcase("owl.build(unknown_disjoint_class)",
            lambda: _build(concepts=[{"name": "X"}],
                           disjoint_groups=[["X", "Ghost"]]))
    owlcase("owl.build(necessary_only=str)",
            lambda: _build(concepts=[{"name": "X",
                                      "necessary_only": "문자열"}]))


def run():
    crash, structured, accepted = [], [], []
    for name, fn in CASES:
        try:
            r = fn()
        except Exception as exc:
            crash.append((name, f"{type(exc).__name__}: {exc}"))
            continue
        if isinstance(r, dict) and r.get("ok") is False and r.get("errors"):
            structured.append(name)
        elif isinstance(r, dict) and r.get("ok"):
            accepted.append(name)
        else:
            crash.append((name, f"비정형 반환: {type(r).__name__}"))
    print(f"total={len(CASES)}  CRASH={len(crash)}  "
          f"STRUCTURED={len(structured)}  ACCEPTED={len(accepted)}")
    if crash:
        print("\n[CRASH] — unhandled, 서버에서 ToolError로 노출됨:")
        for n, e in crash:
            print(f"  ✗ {n}\n      {e[:110]}")
    if accepted:
        print("\n[ACCEPTED] — 변형 입력이 통과 (조사 필요):")
        for n in accepted:
            print(f"  ? {n}")
    return 1 if crash else 0

if __name__ == "__main__":
    sys.exit(run())
