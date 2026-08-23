"""Stage 2 thin cohort 모듈의 TDD 계약 — RED 먼저 (준비물 ③).

_h1a_cohort의 세 규율을 패턴 재사용(직접 import 아님, 단일 arm):
freeze 거부 / 대상 표면 pin / dispatch-plan verbatim 바이트. 전부 발명
fixture로 계약한다 — manifest **내용**은 source 자격까지 차단이지만
**기제**는 source 무관이다(D-E2E-v1-21 §9).

핵심 격리(oracle manifest handoff checklist): oracle 정보(LF·expected IR·
그 해시)는 model-facing prompt와 dispatch plan의 trial 항목에 **절대**
실리지 않는다 — 이 계약의 누출 테스트가 그것을 집행한다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_cohort as C  # noqa: E402
from conceptgate import cg_ir_schema  # noqa: E402


def put(cache: Path, data: bytes) -> str:
    h = hashlib.sha256(data).hexdigest()
    (cache / h).write_bytes(data)
    return h


def entry(cache: Path, case_id: str, sentence: bytes, lf: bytes) -> dict:
    return {
        "case_id": case_id,
        "source_locator": {"corpus_id": "invented", "corpus_version": "v0",
                           "artifact": "made-up.txt", "record_locator": case_id,
                           "retrieval_urls": []},
        "text_sha256": put(cache, sentence),
        "lf_sha256": put(cache, lf),
        "adapter_version": "test-only",
        "adapter_code_sha256": "0" * 64,
        "canonicalization_profile_hash": "1" * 64,
        "expected_ir_sha256": "2" * 64,
    }


@pytest.fixture()
def world(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    entries = [entry(cache, f"O1-inv-{i:03d}",
                     f"Every zorble number {i} glims.".encode(),
                     f"(All (\\x1 N-aD:zorble{i} x1) (\\x1 A-aN:glim x1))".encode())
               for i in range(1, 4)]
    manifest = {"manifest_version": "test", "entries": entries}
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    spec = C.CohortSpec(
        manifest_path=mpath,
        cohort_path=tmp_path / "dispatch_plan.json",
        cache_dir=cache,
        order_seed="E2EV1C-test-order-v1",
        trial_id_prefix="E2EV1C-T",
        model="claude-haiku-4-5-20251001",
    )
    return spec


# ------------------------------------------------------------ build 축 -----

def test_build_produces_one_trial_per_manifest_entry(world):
    plan = C.build_cohort(world)
    assert len(plan["trials"]) == 3
    ids = [t["trial_id"] for t in plan["trials"]]
    assert len(set(ids)) == 3, ids  # 유일성
    assert all(t["trial_id"].startswith("E2EV1C-T-") for t in plan["trials"])


def test_prompt_is_template_with_sentence_and_only_the_sentence(world):
    plan = C.build_cohort(world)
    t0 = plan["trials"][0]
    assert "Every zorble number 1 glims." in t0["prompt"]
    assert "IR DIALECT (complete specification):" in t0["prompt"]
    assert "{sentence}" not in t0["prompt"]


def test_oracle_information_never_reaches_the_plan(world):
    """LF 바이트·expected_ir 해시·lf 해시가 plan 직렬화 어디에도 없다.
    trial 항목은 case_id와 text 쪽 참조만 갖는다."""
    plan = C.build_cohort(world)
    blob = json.dumps(plan, ensure_ascii=False)
    assert "N-aD:zorble" not in blob          # LF 바이트
    assert "2" * 64 not in blob                # expected_ir_sha256
    m = json.loads(world.manifest_path.read_text())
    for e in m["entries"]:
        assert e["lf_sha256"] not in blob      # lf 참조조차 불필요·미포함


def test_build_refuses_when_any_fixture_text_is_unavailable(world):
    m = json.loads(world.manifest_path.read_text())
    missing = m["entries"][1]["text_sha256"]
    (world.cache_dir / missing).unlink()
    with pytest.raises(C.MaterialUnavailable) as ei:
        C.build_cohort(world)
    assert "O1-inv-002" in str(ei.value)
    assert not world.cohort_path.exists(), "부분 자료로 plan을 쓰면 안 된다"


def test_build_refuses_tampered_cache(world):
    m = json.loads(world.manifest_path.read_text())
    h = m["entries"][0]["text_sha256"]
    (world.cache_dir / h).write_bytes(b"tampered sentence!")
    with pytest.raises(C.MaterialUnavailable):
        C.build_cohort(world)


def test_build_validates_every_manifest_entry(world):
    m = json.loads(world.manifest_path.read_text())
    del m["entries"][2]["expected_ir_sha256"]
    world.manifest_path.write_text(json.dumps(m))
    with pytest.raises(ValueError):
        C.build_cohort(world)


# ------------------------------------------------------- 표면 pin 축 -------

def test_plan_pins_subject_schema_and_template(world):
    plan = C.build_cohort(world)
    prov = plan["provenance"]
    subj = prov["trial_subject"]
    assert subj["name"] == "o1-compiler"
    raw = (Path.home() / ".claude" / "agents" / "o1-compiler.md").read_text()
    assert subj["definition_sha256"] == hashlib.sha256(raw.encode()).hexdigest()
    assert "tools: []" in raw
    # 2026-08-23 리허설 실측: API가 tool input_schema root의 조합자를
    # 불허해 dispatch는 {"formula": ...} 봉투를 강제한다 — plan에는 실제로
    # 강제되는 그 스키마(봉투)가 실린다.
    schema = cg_ir_schema.dispatch_envelope_schema()
    assert prov["output_schema"] == schema
    assert prov["output_schema_sha256"] == hashlib.sha256(
        json.dumps(schema, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert prov["constructor_profile"] == list(cg_ir_schema.V0_O1_CONSTRUCTORS)
    assert prov["prompt_template_sha256"] == hashlib.sha256(
        C.load_template().encode()).hexdigest()
    assert prov["model"] == "claude-haiku-4-5-20251001"


def test_template_loads_from_the_fenced_block_only():
    tpl = C.load_template()
    assert tpl.startswith("Compile the meaning")
    assert "{sentence}" in tpl
    assert "DRAFT" not in tpl and "동결" not in tpl, "fence 밖 산문이 섞였다"


# ------------------------------------------------------ 결정성·거부 축 -----

def test_plan_is_deterministic_across_builds(world):
    a, b = C.build_cohort(world), C.build_cohort(world)
    assert a == b


def test_trial_order_is_seeded_not_manifest_order(world):
    plan = C.build_cohort(world)
    case_order = [t["case_id"] for t in plan["trials"]]
    spec2 = world._replace(order_seed="E2EV1C-test-order-v2")
    case_order2 = [t["case_id"] for t in C.build_cohort(spec2)["trials"]]
    assert set(case_order) == set(case_order2)
    assert case_order != case_order2, "seed가 순서에 관여하지 않는다면 왜 있는가"


def test_write_refuses_overwrite(world):
    C.write_cohort(world)
    assert world.cohort_path.exists()
    with pytest.raises(C.CohortOverwriteRefused):
        C.write_cohort(world)


def test_written_plan_bytes_reproduce(world):
    C.write_cohort(world)
    on_disk = world.cohort_path.read_text(encoding="utf-8")
    rebuilt = json.dumps(C.build_cohort(world), ensure_ascii=False, indent=2) + "\n"
    assert on_disk == rebuilt, "verbatim 바이트 규율 — 재현이 곧 검증"


# ============================================================== ROUND 2 ====
# 동결 준비(2026-08-23): 양화-부정 fixture는 subject가 `not`을 내야 하므로
# profile이 O1_V1=(forall,exists,and,pred,not)로 동결된다. builder가 profile을
# 받아 스키마·provenance에 일관 반영해야 한다(기본값은 기존 거동 불변).


def test_constructor_profile_flows_into_schema_and_provenance(world):
    spec2 = world._replace(constructors=("forall", "exists", "and", "pred", "not"))
    plan = C.build_cohort(spec2)
    prov = plan["provenance"]
    assert prov["constructor_profile"] == ["forall", "exists", "and", "pred", "not"]
    assert prov["output_schema"] == cg_ir_schema.dispatch_envelope_schema(
        ("forall", "exists", "and", "pred", "not"))
    kinds = {b["properties"]["kind"]["const"]
             for b in prov["output_schema"]["$defs"]["formula"]["oneOf"]}
    assert "not" in kinds


def test_default_profile_unchanged(world):
    plan = C.build_cohort(world)
    assert plan["provenance"]["constructor_profile"] == list(
        cg_ir_schema.V0_O1_CONSTRUCTORS)


# ---- D-E2E-v1-26: V4 template (implies 방언) ----

def test_v4_template_adds_exactly_one_implies_line():
    """V4 template = V1 + implies constructor 1행, 그 외 diff 0 (D-26 §3 —
    semantic hint 금지). V1 파일은 바이트 불변."""
    v1 = C.load_template()
    v4 = C.load_template(HERE / "stage2_prompt_template_v4.md")
    assert '{"kind": "implies", "left": <formula>, "right": <formula>}' in v4
    assert '"implies"' not in v1
    diff = [l for l in v4.splitlines() if l not in v1.splitlines()]
    assert diff == ['- {"kind": "implies", "left": <formula>, "right": <formula>}']


def test_cohort_spec_template_file_flows_into_plan(world, tmp_path):
    """CohortSpec.template_file 지정 시 그 template로 렌더·pin — 미지정은 V1."""
    import hashlib as _h
    spec0 = world                     # 이 파일의 world는 spec 단일 반환
    m = spec0.manifest_path
    spec = C.CohortSpec(m, tmp_path / "p.json", spec0.cache_dir,
                        "RUN-v4t", "T4", "claude-haiku-4-5-20251001",
                        template_file=str(HERE / "stage2_prompt_template_v4.md"))
    plan = C.write_cohort(spec)
    tpl = C.load_template(HERE / "stage2_prompt_template_v4.md")
    assert plan["provenance"]["prompt_template_sha256"] == \
        _h.sha256(tpl.encode()).hexdigest()
    assert all('"implies"' in t["prompt"] for t in plan["trials"])
