#!/usr/bin/env python3
"""H3 dispatcher: one common action surface across three arms.

  python3 _h3.py agent   -> regenerates + installs the 3 trial subjects
  python3 _h3.py smoke   -> writes h3_smoke_prompts.json  (3 trials: one per
                            arm, same fixture -- the bundle DESIGN_H3_common_
                            action.md §5 pre-registers)
  python3 _h3.py freeze  -> writes h3_pilot_prompts.json  (45 trials, D-H3-5)
  python3 _h3.py record <manifest.json> <raw.json> <out.json>
                         -> attach raw outputs, recompute hashes

Why this file exists rather than editing _cohort.py
-----------------------------------------------------
DESIGN_DECISION_H3.md (external design ruling, decided_by: OpenAI Codex,
2026-07-29) rejected native-schema 3-arm execution: CONTROL_REPO and A_REPO
cannot express abstain, so the absence of it there is indistinguishable from
"didn't judge" versus "couldn't say it." The ruling required (D-H3-1) a common
action surface (accept_report|repair|defer) across all three arms and
(D-H3-4) a single dispatcher over the existing whitelist builder, with
_surface.py, _cohort.py, contract_prompt.md, decision_schema.json, and the
certified fixtures left untouched. This module adds the H3 surface without
modifying any of them -- see DESIGN_H3_common_action.md, frozen before this
file existed.

No model call happens in this file. `agent`/`smoke`/`freeze` only write
files and compute hashes; running an actual trial (feeding a rendered prompt
to `e2.4-h3-*-decider` through the Agent tool) is a separate, later step.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
E23_DIR = HERE.parent / "2026-07-25_e2.3_global_invariant_generalization"

MODEL = "claude-opus-5"


def _load(name: str, path: Path):
    """Load a sibling module by path under a unique sys.modules name.

    Required, not cosmetic: this repo's gate runner exists precisely because
    same-named modules loaded under the interpreter's default name collide
    across experiments (docs/HANDOFF.md [DONE] #6). A unique name per loader
    keeps _h3.py from re-creating that failure mode.
    """
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("e24_surface_h3", HERE / "_surface.py")
cohort = _load("e24_cohort_h3", HERE / "_cohort.py")  # reuse schema_errors/strip_descriptions


# ---------------------------------------------------------------------------
# preregistration guard (E2.3 _gen_prompts.py pattern, reused)
# ---------------------------------------------------------------------------

EXPERIMENT_REL = HERE.relative_to(REPO_ROOT)
DESIGN_FILES = [
    str(EXPERIMENT_REL / name)
    for name in ("DESIGN_H3_common_action.md", "decision_schema_h3.json", "_h3.py")
]


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO_ROOT), *args], text=True).strip()


def preregistered_design_commit() -> str:
    """Refuse to freeze until every H3 design file is committed.

    Same discipline as E2.3's _gen_prompts.py: a design frozen after seeing a
    trial result is not a precommitment, it is a rationalization.
    """
    dirty = _git("status", "--porcelain", "--", *DESIGN_FILES)
    if dirty:
        raise SystemExit(
            "PREREGISTRATION_REQUIRED: commit all H3 design files before "
            "freezing.\n" + dirty
        )
    return _git("log", "-1", "--format=%H", "--", *DESIGN_FILES)


# ---------------------------------------------------------------------------
# schema
# ---------------------------------------------------------------------------

H3_SCHEMA_PATH = HERE / "decision_schema_h3.json"
H3_ARMS = ("CONTROL_REPO_H3", "A_REPO_H3", "CONTRACT_REPO_H3")

# D-H3-2: conflicting (E24-F-04) stays excluded, not replaced.
H3_FIXTURES = ("E24-F-01", "E24-F-02", "E24-F-03")


def h3_schema() -> dict:
    return json.loads(H3_SCHEMA_PATH.read_text(encoding="utf-8"))


def h3_variant_schema(arm: str) -> dict:
    schema = h3_schema()
    variant_name = schema["arm_schema_map"][arm]
    return schema["variants"][variant_name]["schema"]


def h3_transport_schema(arm: str) -> dict:
    return cohort.strip_descriptions(h3_variant_schema(arm))


# ---------------------------------------------------------------------------
# E2.3 rule-text reuse -- byte-identical, without executing E2.3's module
# ---------------------------------------------------------------------------

def _e23_constant(name: str) -> str:
    """Extract a top-level string constant from E2.3's _gen_prompts.py by name.

    Not imported directly: that file's `from _cert_core import run_and_certify`
    only resolves when E2.3's own directory is on sys.path, which it is not
    when _h3.py runs from here. AST extraction avoids the dependency and
    still fails loudly (not silently) if the constant is ever renamed or
    removed -- the same anchor-over-hardcoded-copy discipline _review_11.py
    uses for contract_prompt.md.
    """
    tree = ast.parse((E23_DIR / "_gen_prompts.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return ast.literal_eval(node.value)
    raise surface.SurfaceError(
        f"{name}: not found as a top-level assignment in E2.3's _gen_prompts.py; "
        f"it may have been renamed or removed -- update _e23_constant's caller"
    )


VOCAB_HINT = _e23_constant("VOCAB_HINT")
GLOBAL_CONSISTENCY_RULE = _e23_constant("GLOBAL_CONSISTENCY_RULE")


# ---------------------------------------------------------------------------
# contract_prompt.md reuse -- anchor extraction, not a hand copy
# ---------------------------------------------------------------------------

CONTRACT_PROMPT_PATH = HERE / "contract_prompt.md"
CONTRACT_OUTPUT_ANCHOR = "출력은 decision_schema.json의 evidence_contract_v1 schema를 따른다."


def contract_rule_text() -> str:
    """Rules 1-7 of contract_prompt.md, byte-identical, ending before the
    trailing schema-pointer sentence (which H3 replaces with its own).

    Anchored on that sentence's exact text: if contract_prompt.md's ending
    is ever reworded, this raises instead of quietly reviewing H3 CONTRACT
    trials against stale rule text.
    """
    full = surface.load_contract_prompt(CONTRACT_PROMPT_PATH)
    idx = full.find(CONTRACT_OUTPUT_ANCHOR)
    if idx == -1:
        raise surface.SurfaceError(
            "CONTRACT_OUTPUT_ANCHOR not found in contract_prompt.md; "
            "the contract text moved, update the anchor before reusing it"
        )
    return full[:idx].rstrip()


# ---------------------------------------------------------------------------
# prompt composition -- one common action block, three arm rule texts
# ---------------------------------------------------------------------------

COMMON_ACTION_BLOCK = (
    "\n\n추가로, 이 실험은 서로 다른 세 client 조건을 동일한 최종 행동 어휘로 "
    "비교한다. 최종 결정은 다음 중 하나의 action이어야 한다.\n"
    "- accept_report: 현재 상태가 안전하며 추가 조치가 필요 없다.\n"
    "- repair: 근거가 있는 concept/feature 수정이 필요하다. repaired_concepts에 "
    "input의 모든 concept과 feature를 포함해 채운다.\n"
    "- defer: 이 packet만으로는 판단을 확정할 수 없어 보류한다. 이때 "
    "repaired_concepts는 null이다.\n\n"
    "cited_evidence_ids에는 이번 판단에 실제로 근거로 쓴 evidence_id만 적는다. "
    "payload에 없는 id를 적으면 안 된다. report에 판단 근거를 자유 서술로 "
    "요약한다.\n"
)

_PACKET_PREAMBLE = (
    "너는 MCP 클라이언트 agent다.\n\n"
    "입력은 repo-derived evidence packet이다. 이 packet은 "
    "goodand/concept-gate-taxonomy 저장소의 특정 commit에서 추출된 "
    "evidence_items, candidate_concepts, server_response만 포함한다.\n"
)


def _control_rule_text() -> str:
    return _PACKET_PREAMBLE + "\n" + VOCAB_HINT + "\n"


def _a_rule_text() -> str:
    return _control_rule_text() + "\n" + GLOBAL_CONSISTENCY_RULE + "\n"


def _contract_rule_text() -> str:
    return (
        contract_rule_text()
        + "\n\n출력의 action/repaired_concepts/cited_evidence_ids/report는 "
        "decision_schema_h3.json의 h3_contract_action schema를 따른다. 위 "
        "규칙의 decision 필드는 이제 action이다(accept_report/repair는 이름이 "
        "같고, abstain은 defer로 이름만 바뀐다). 위 규칙이 요구하는 "
        "contract_verdict/evidence_scope/evidence_audit/feature_judgments/"
        "invariant_checks/repair_plan/abstain은 전부 contract_assessment 객체 "
        "아래에 그대로 채운다."
    )


ARM_RULE_TEXT = {
    "CONTROL_REPO_H3": _control_rule_text,
    "A_REPO_H3": _a_rule_text,
    "CONTRACT_REPO_H3": _contract_rule_text,
}


def arm_rule_template(arm: str) -> str:
    """Per-arm rule text ending in the unsubstituted {payload_json} slot.

    Shaped exactly like _surface.load_contract_prompt's output so
    surface.render_prompt can be reused unmodified for the substitution step.
    """
    if arm not in ARM_RULE_TEXT:
        raise surface.SurfaceError(f"unknown H3 arm {arm!r}")
    return (
        ARM_RULE_TEXT[arm]().rstrip()
        + COMMON_ACTION_BLOCK
        + "\npayload:\n{payload_json}\n"
    )


def render_h3_prompt(arm: str, payload: dict) -> str:
    """The single entrypoint (gate 8): smoke, pilot, and any future full run
    all produce rendered prompts by calling this and nothing else."""
    return surface.render_prompt(arm_rule_template(arm), payload)


# ---------------------------------------------------------------------------
# fixture -> qualification -> payload (unchanged _surface.py path)
# ---------------------------------------------------------------------------

def build_h3_payload(fixture_id: str):
    fixture = json.loads((HERE / cohort.FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=True)
    if manifest["status"] != "passed":
        raise SystemExit(f"{fixture_id}: qualification failed, refusing to build")
    payload = surface.build_model_payload(fixture, manifest)
    return fixture, manifest, payload


# ---------------------------------------------------------------------------
# trial subject agents
# ---------------------------------------------------------------------------

AGENT_NAMES = {
    "CONTROL_REPO_H3": "e2.4-h3-control-decider",
    "A_REPO_H3": "e2.4-h3-a-decider",
    "CONTRACT_REPO_H3": "e2.4-h3-contract-decider",
}
AGENT_INSTALL_DIR = Path.home() / ".claude" / "agents"

AGENT_TEMPLATE = """---
name: {name}
description: E2.4 H3 {arm} trial subject. Applies the {arm} prompt rules to one repo-derived evidence packet and returns a common-action H3 decision. No tools, by design.
tools: []
---

You are the trial subject for one E2.4 H3 {arm} trial.

The prompt you receive is the complete and only input. Follow it exactly as
written; these instructions add nothing to it and override nothing in it.

You have NO tools. Do not attempt to read files, search, run commands, browse
a repository, or consult any external source. In particular, do not try to
look up the repository the evidence was drawn from, and do not rely on any
memory of it. The packet's evidence items are the entire world for this
decision.

Reason only from the packet, then return your decision.

## Output

Your entire final message must be one JSON object conforming to the schema
below, and nothing else -- no prose before or after, no markdown fence. Every
listed property is required and no other property is allowed.

{schema_json}
"""


def h3_agent_definition(arm: str) -> str:
    return AGENT_TEMPLATE.format(
        name=AGENT_NAMES[arm],
        arm=arm,
        schema_json=json.dumps(h3_transport_schema(arm), ensure_ascii=False, indent=2),
    )


def install_agents() -> int:
    AGENT_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    for arm, name in AGENT_NAMES.items():
        text = h3_agent_definition(arm)
        (HERE / f"{name}.md").write_text(text, encoding="utf-8")
        (AGENT_INSTALL_DIR / f"{name}.md").write_text(text, encoding="utf-8")
        print(f"  wrote {name}.md and installed to {AGENT_INSTALL_DIR}")
    # _cohort.py's install_agent() claims a mid-session definition is not
    # resolvable until a new session. Register [DONE] #17 found that claim
    # false at least once this session (e2.4-review-11 was installed and
    # used immediately). Don't repeat the stale claim here -- try using the
    # agent immediately; an unresolvable name is the actual fallback signal.
    return 0


# ---------------------------------------------------------------------------
# freeze -- smoke and pilot share this, per gate 8
# ---------------------------------------------------------------------------

PILOT_REPLICATES = 5
PILOT_BUNDLE = [
    (fixture_id, arm, replicate)
    for fixture_id in H3_FIXTURES
    for arm in H3_ARMS
    for replicate in range(1, PILOT_REPLICATES + 1)
]  # 3 fixtures x 3 arms x 5 = 45, D-H3-5

SMOKE_FIXTURE = "E24-F-03"  # insufficient -- D-H3-2's primary target class
SMOKE_BUNDLE = [(SMOKE_FIXTURE, arm, 1) for arm in H3_ARMS]  # 3 trials, one per arm


def _freeze_bundle(bundle, out_name: str, label: str) -> int:
    builder_commit = preregistered_design_commit()
    schema_full = h3_schema()
    fixtures_cache: dict[str, tuple] = {}
    trials: list[dict] = []
    prompts: dict[str, str] = {}

    for fixture_id, arm, replicate in bundle:
        if fixture_id not in fixtures_cache:
            fixtures_cache[fixture_id] = build_h3_payload(fixture_id)
        fixture, manifest, payload = fixtures_cache[fixture_id]

        contract_prompt = arm_rule_template(arm)
        rendered = surface.render_prompt(contract_prompt, payload)
        decision_schema = schema_full["variants"][schema_full["arm_schema_map"][arm]]["schema"]
        trial_id = f"E24-H3-{fixture_id[-2:]}-{arm}-{replicate:02d}"
        prompts[trial_id] = rendered
        system_prompt = h3_agent_definition(arm)

        trials.append({
            **surface.trial_manifest(
                trial_id=trial_id,
                fixture=fixture,
                qualification_manifest=manifest,
                model_payload=payload,
                contract_prompt=contract_prompt,
                rendered_prompt=rendered,
                decision_schema=decision_schema,
                builder_commit=builder_commit,
                model=MODEL,
                parameters={
                    "fixture_id": fixture_id, "replicate": replicate, "arm": arm,
                    "tool_access": "no_tools", "agent_type": AGENT_NAMES[arm],
                },
            ),
            "system_prompt_sha256": surface.sha256_of(system_prompt),
            "presented_schema_sha256": surface.sha256_of(h3_transport_schema(arm)),
        })

    # Determinism: same fixture+arm must render byte-identical prompts across
    # replicates (mirrors _cohort.py.freeze's check).
    for fixture_id in {t["parameters"]["fixture_id"] for t in trials}:
        for arm in H3_ARMS:
            hashes = {
                t["rendered_prompt_sha256"] for t in trials
                if t["parameters"]["fixture_id"] == fixture_id and t["parameters"]["arm"] == arm
            }
            if len(hashes) > 1:
                raise SystemExit(f"{fixture_id}/{arm}: builder is not deterministic {hashes}")

    (HERE / out_name).write_text(
        json.dumps(
            {
                "manifest_version": "e2.4-h3-v1",
                "label": label,
                "note": "Frozen model-facing surface, committed before any trial "
                        "ran. No model call happened while writing this file.",
                "builder_commit": builder_commit,
                "rendered_prompts": prompts,
                "trials": trials,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"  froze {len(trials)} trials ({label}) -> {out_name}")
    return 0


def smoke() -> int:
    return _freeze_bundle(SMOKE_BUNDLE, "h3_smoke_prompts.json", "smoke")


def freeze() -> int:
    return _freeze_bundle(PILOT_BUNDLE, "h3_pilot_prompts.json", "pilot")


# ---------------------------------------------------------------------------
# record -- attach raw outputs to an already-frozen manifest
# ---------------------------------------------------------------------------

def record(manifest_path: Path, raw_path: Path, out_path: Path) -> int:
    frozen = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    by_id = {t["trial_id"]: t for t in frozen["trials"]}
    missing = sorted(set(by_id) - set(raw))
    extra = sorted(set(raw) - set(by_id))
    if missing or extra:
        raise SystemExit(f"trial id mismatch  missing={missing}  extra={extra}")

    schema_full = h3_schema()
    records, malformed = [], {}
    for trial_id, manifest in sorted(by_id.items()):
        arm = manifest["parameters"]["arm"]
        fixture_id = manifest["parameters"]["fixture_id"]
        _, _, payload = build_h3_payload(fixture_id)
        rendered = surface.render_prompt(arm_rule_template(arm), payload)
        if surface.sha256_of(rendered) != manifest["rendered_prompt_sha256"]:
            raise SystemExit(
                f"{trial_id}: rendered prompt changed since freeze ({fixture_id}/{arm}); "
                f"the frozen manifest is void, re-freeze and re-run"
            )
        decision_schema = h3_transport_schema(arm)
        errs = cohort.schema_errors(raw[trial_id], decision_schema)
        if errs:
            malformed[trial_id] = errs
        records.append({**manifest, "output": raw[trial_id], "schema_violations": errs})

    out_path.write_text(
        json.dumps({"trials": records}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"  recorded {len(records)} trials -> {out_path.name}")
    if malformed:
        print(f"  {len(malformed)} with schema violations (kept, not dropped):")
        for tid, errs in malformed.items():
            for e in errs[:3]:
                print(f"    {tid}: {e}")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "agent":
        return install_agents()
    if mode == "smoke":
        return smoke()
    if mode == "freeze":
        return freeze()
    if mode == "record":
        if len(sys.argv) != 5:
            raise SystemExit("usage: _h3.py record <manifest.json> <raw.json> <out.json>")
        return record(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
