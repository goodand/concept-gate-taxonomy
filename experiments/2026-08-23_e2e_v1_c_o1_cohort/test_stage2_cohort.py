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
    schema = cg_ir_schema.formula_json_schema()
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
