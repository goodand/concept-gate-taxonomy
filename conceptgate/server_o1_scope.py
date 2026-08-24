"""ConceptGate O1 Scope — 코호트 채점 사슬을 MCP 도구·CLI로 노출한다.

## 무엇을 노출하는가

이 저장소에서 **가장 깊게 배선되고 작동이 증명된 구조**는 Stage 2 코호트 채점
사슬이다:

```text
manifest_v5 (동결) + .oracle_cache
        ↓  derive_cohort_oracle       — 커밋 해시 검증, 불일치 → OracleDrift
        ↓  derive_acceptance_inputs   — strata·floors·pass_min 유도
        ↓  ingest_cohort              — plan trial 순회(출력 순회 아님)
        ↓  evaluate_scope_v2          — V1 전처리 → V2 signature 비교
        ↓  score                      — counts·metrics·acceptance
```

작동 근거: `experiments/2026-08-23_e2e_v1_c_o1_cohort/DRYRUN_20260824.md`
(오라클 20/20, 수락 게이트가 경계에서 뒤집힘), 실험 게이트 404 passed.

## 실패 철학 — 삼키지 않는다

이 서버는 **실패를 숨기지 않는다.** 모든 도구가 같은 형태를 돌려준다:

```json
{"ok": false, "error_type": "OracleDrift", "message": "...",
 "context": {"case_id": "...", ...}, "next": "무엇을 확인하면 되는가"}
```

목적은 Claude Desktop 쪽에서 **엣지 케이스를 발견하고 고칠 수 있게** 하는
것이다. 예외를 삼켜 `ok: true`를 내면 그 목적이 깨진다 — 이 저장소가
"침묵을 성공으로 읽지 않는다"를 게이트 어휘(PASS/FAIL/BLOCKED)로 만든 것과
같은 이유다.

## 계약 해시 게이트 — 어긋나면 서비스하지 않는다

`stage2_fixture_manifest_v5.json`의 `contract_hashes`가 투영·정규화·충족성·
평가 프로파일 모듈 6개를 바이트로 고정한다. 이 서버는 **시작 시 그것을
대조**하고 어긋나면 도구를 서비스하지 않는다. 동결 계약과 다른 코드로 답하면
그 답은 실험의 답이 아니다.

## 이 서버가 하지 않는 것

- **trial·코호트 디스패치를 하지 않는다.** 모델을 호출하는 경로가 없다.
  `dispatch: blocked`(D-36)은 유효하고, 실행 승인은 매번 사용자 몫이다.
- 동결 표면에 쓰지 않는다. 결과는 임시 경로에만 쓴다.
- 충족성 witness를 반환하지 않는다(기록은 sha256만 — Q30.4).

## 두 가지 진입점

- **MCP**: `python3 -m conceptgate.server_o1_scope` (stdio)
- **CLI**: `python3 -m conceptgate.server_o1_scope --cli <tool> [--arg k=v]`
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
EXP = REPO / "experiments" / "2026-08-23_e2e_v1_c_o1_cohort"
MANIFEST = EXP / "stage2_fixture_manifest_v5.json"
PLAN = EXP / "stage2_cohort_plan_v5.json"
CACHE = REPO / ".oracle_cache"

for p in (str(EXP), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

CONTRACT_FILES = {
    "projection_pipeline_module_sha256": "_stage2_projection_pipeline_v2.py",
    "projection_module_v2_sha256": "_stage2_scope_projection_v2.py",
    "projection_module_sha256": "_stage2_scope_projection.py",
    "canonicalization_core_sha256": "_stage2_canonical_core.py",
    "eval_profile_module_sha256": "_stage2_eval_profile.py",
    "satisfiability_module_sha256": "_stage2_satisfiability.py",
}


# --------------------------------------------------------------- 실패 형태 ---

def _fail(exc: BaseException, **context: Any) -> dict:
    """예외를 진단 가능한 형태로 바꾼다 — 삼키지 않고, 스택도 남긴다."""
    return {
        "ok": False,
        "error_type": type(exc).__name__,
        "message": str(exc),
        "context": context,
        "traceback": traceback.format_exc().splitlines()[-6:],
        "next": _next_hint(type(exc).__name__),
    }


def _next_hint(kind: str) -> str:
    return {
        "OracleDrift": "manifest의 expected_ir_sha256과 어댑터 산출이 어긋났다. "
                       "contract_status()로 계약 모듈 해시를 먼저 확인하라 — "
                       "어댑터가 바뀌면 오라클이 바뀐다.",
        "ValueError": "모집단·strata·trial_id 정합성 문제다. "
                      "acceptance_inputs()로 유도값을 직접 보라.",
        "ResultsOverwriteRefused": "결과 파일이 이미 있다. 이 서버는 임시 경로를 "
                                   "쓰므로 정상적으로는 나지 않는다 — 났다면 보고하라.",
        "FileNotFoundError": "동결 입력 또는 .oracle_cache 경로가 없다. "
                             "contract_status()의 paths를 확인하라.",
        "ContractDrift": "계약 모듈이 동결 해시와 다르다. 이 서버는 그 상태로 "
                         "답하지 않는다 — 어긋난 파일을 되돌리거나 새 freeze를 만들어라.",
    }.get(kind, "structured 결과의 context와 traceback을 함께 보고하라.")


class ContractDrift(RuntimeError):
    """계약 모듈이 동결 해시와 다르다."""


def _contract_report() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(f"동결 manifest 없음: {MANIFEST}")
    ch = json.loads(MANIFEST.read_text(encoding="utf-8"))["contract_hashes"]
    rows, drifted = [], []
    for key, fn in CONTRACT_FILES.items():
        p = EXP / fn
        cur = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        ok = cur == ch.get(key)
        rows.append({"module": fn, "pinned": ch.get(key), "current": cur, "match": ok})
        if not ok:
            drifted.append(fn)
    return {"modules": rows, "drifted": drifted}


def _require_contract() -> None:
    rep = _contract_report()
    if rep["drifted"]:
        raise ContractDrift(
            f"계약 모듈이 동결 해시와 다르다: {rep['drifted']}. "
            f"이 서버는 그 상태로 답하지 않는다")


# ------------------------------------------------------------------ 도구 ---

def contract_status() -> dict:
    """무슨 계약으로 답하는지 보여준다. 드리프트가 있어도 **보고한다**(막지 않는다)."""
    try:
        rep = _contract_report()
        frozen = _frozen_status()
        return {
            "ok": not rep["drifted"] and not frozen["changed"],
            "contract_modules": rep["modules"],
            "contract_drifted": rep["drifted"],
            "frozen_surfaces_changed": frozen["changed"],
            "paths": {"manifest": str(MANIFEST), "plan": str(PLAN),
                      "cache": str(CACHE), "cache_items": _count(CACHE)},
        }
    except Exception as e:                                   # noqa: BLE001
        return _fail(e)


def _count(p: Path) -> int | None:
    try:
        return len(list(p.iterdir()))
    except OSError:
        return None


def _frozen_status() -> dict:
    try:
        import test_frozen_surfaces as T
    except Exception:                                        # noqa: BLE001
        return {"changed": [], "note": "동결 표면 고정 테이블을 불러올 수 없다"}
    changed = []
    for name, pinned in T.FROZEN.items():
        p = EXP / name
        cur = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        if cur != pinned:
            changed.append({"file": name, "pinned": pinned[:16], "current": (cur or "없음")[:16]})
    return {"changed": changed}


def cohort_oracle() -> dict:
    """동결 manifest·캐시에서 오라클을 유도한다. 드리프트는 case_id와 함께 낸다."""
    try:
        _require_contract()
        import _stage2_run as R
        o = R.derive_cohort_oracle(MANIFEST, CACHE)
        return {"ok": True, "resolved": len(o), "case_ids": sorted(o)}
    except Exception as e:                                   # noqa: BLE001
        return _fail(e, manifest=str(MANIFEST), cache=str(CACHE))


def acceptance_inputs() -> dict:
    """수락 파라미터를 유도해 보여준다 — 무엇이 기준인지 감추지 않는다."""
    try:
        _require_contract()
        import _stage2_run as R
        a = R.derive_acceptance_inputs(MANIFEST, PLAN)
        sizes: dict[str, int] = {}
        for s in a["strata"].values():
            sizes[s] = sizes.get(s, 0) + 1
        return {"ok": True, "pass_min": a["pass_min"],
                "stratum_floors": {k: list(v) for k, v in a["stratum_floors"].items()},
                "strata_sizes": sizes, "n_trials": len(a["strata"]),
                "source": "PREREGISTRATION_STAGE2_V4.md — N=20 · PASS≥16 ∧ mq 4/5"}
    except Exception as e:                                   # noqa: BLE001
        return _fail(e)


def scope_compare(case_id: str, predicted: dict, oracle: dict) -> dict:
    """한 건을 동결 채점 계약으로 비교한다 — 실패 trial을 파고들 때 쓴다."""
    try:
        _require_contract()
        import _stage2_projection_pipeline_v2 as P
        from conceptgate.cg_identity import canonical_sha256
        verdict = P.evaluate_scope_v2(case_id, predicted, oracle)
        out = {"ok": True, "verdict": verdict,
               "profile": {"pre": P.PRE_PROJECTION_PROFILE_ID,
                           "projection": P.PROJECTION_PROFILE_ID}}
        for label, f in (("predicted", predicted), ("oracle", oracle)):
            try:
                sig = P.scope_signature_v2_for_case(case_id, f)
                js = P.signature_jsonable(sig)
                out[f"{label}_signature"] = js
                out[f"{label}_signature_sha256"] = canonical_sha256(js)
            except Exception as inner:                       # noqa: BLE001
                out[f"{label}_signature_error"] = f"{type(inner).__name__}: {inner}"
        return out
    except Exception as e:                                   # noqa: BLE001
        return _fail(e, case_id=case_id)


def score_cohort(outputs: list[dict]) -> dict:
    """모델 출력을 동결 계약으로 채점한다 — 코호트 채점의 유일한 진입점을 쓴다.

    `outputs`는 `[{"trial_id": "...", "ir": {...}}, ...]`. plan에 있는 trial의
    출력이 없으면 **ERROR 행으로 회계된다**(행 손실이 분모 조작이 되지 않게).
    """
    try:
        _require_contract()
        import _stage2_run as R
        with tempfile.TemporaryDirectory() as td:
            res = R.ingest_cohort(PLAN, outputs, manifest_path=MANIFEST,
                                  cache_dir=CACHE,
                                  results_path=Path(td) / "results.json")
        rep = res["report"]
        return {"ok": True, "counts": rep["counts"], "metrics": rep.get("metrics"),
                "acceptance": rep["acceptance"], "strata": rep.get("strata"),
                "trial_rows": res["trial_rows"]}
    except Exception as e:                                   # noqa: BLE001
        return _fail(e, n_outputs=len(outputs) if isinstance(outputs, list) else None)


def dryrun(n_fail: int = 0, n_missing: int = 0, mq_fail: int = 0) -> dict:
    """모델 없이 배관을 돌린다 — 엣지 케이스를 Desktop에서 직접 만들 수 있다.

    `n_fail` 건은 오라클을 부정으로 감싸 FAIL, `n_missing` 건은 출력을 빼서
    ERROR, `mq_fail` 건은 **multi_quantifier 층에서만** 실패시킨다(층 하한
    판별을 직접 확인할 때).
    """
    try:
        _require_contract()
        import copy
        import _stage2_run as R
        oracle = R.derive_cohort_oracle(MANIFEST, CACHE)
        a = R.derive_acceptance_inputs(MANIFEST, PLAN)
        trials = json.loads(PLAN.read_text(encoding="utf-8"))["trials"]
        mq = [t["trial_id"] for t in trials
              if a["strata"][t["trial_id"]] == "multi_quantifier"]
        fail_ids = set(mq[:mq_fail])
        others = [t["trial_id"] for t in trials if t["trial_id"] not in fail_ids]
        fail_ids |= set(others[:n_fail])
        skip = set(others[n_fail:n_fail + n_missing])
        outs = []
        for t in trials:
            if t["trial_id"] in skip:
                continue
            ir = copy.deepcopy(oracle[t["case_id"]])
            if t["trial_id"] in fail_ids:
                ir = {"op": "not", "arg": ir}
            outs.append({"trial_id": t["trial_id"], "ir": ir})
        res = score_cohort(outs)
        res["scenario"] = {"n_fail": n_fail, "n_missing": n_missing,
                           "mq_fail": mq_fail, "outputs_sent": len(outs)}
        return res
    except Exception as e:                                   # noqa: BLE001
        return _fail(e, n_fail=n_fail, n_missing=n_missing, mq_fail=mq_fail)


def self_test() -> dict:
    """배관이 이 환경에서 도는지 즉시 확인한다 — Desktop 첫 호출용."""
    scenarios = [
        ("all_correct", dict(), True),
        ("boundary_16pass", dict(n_fail=4), True),
        ("below_15pass", dict(n_fail=5), False),
        ("one_output_missing", dict(n_missing=1), False),
        ("floor_evasion_mq1of5", dict(mq_fail=4), False),
    ]
    rows, all_ok = [], True
    for name, kw, expect in scenarios:
        r = dryrun(**kw)
        if not r.get("ok"):
            rows.append({"scenario": name, "ok": False, "error": r.get("error_type"),
                         "message": r.get("message")})
            all_ok = False
            continue
        got = r["acceptance"]["accepted"]
        ok = got == expect
        all_ok &= ok
        rows.append({"scenario": name, "counts": r["counts"],
                     "accepted": got, "expected": expect, "as_expected": ok})
    return {"ok": all_ok, "scenarios": rows,
            "note": "as_expected가 False인 행이 엣지 케이스다 — 그 행의 counts와 "
                    "acceptance를 그대로 보고하라"}


TOOLS = {
    "contract_status": contract_status,
    "cohort_oracle": cohort_oracle,
    "acceptance_inputs": acceptance_inputs,
    "scope_compare": scope_compare,
    "score_cohort": score_cohort,
    "dryrun": dryrun,
    "self_test": self_test,
}


# -------------------------------------------------------------------- MCP ---

def build_mcp():
    from fastmcp import FastMCP
    mcp = FastMCP("ConceptGate O1 Scope")
    for name, fn in TOOLS.items():
        mcp.tool(name=name)(fn)
    return mcp


# -------------------------------------------------------------------- CLI ---

def _cli(argv: list[str]) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="conceptgate.server_o1_scope --cli")
    ap.add_argument("tool", choices=sorted(TOOLS))
    ap.add_argument("--arg", action="append", default=[],
                    metavar="k=v", help="JSON 값. 예: --arg n_fail=4")
    ns = ap.parse_args(argv)
    kwargs: dict[str, Any] = {}
    for item in ns.arg:
        k, _, v = item.partition("=")
        try:
            kwargs[k] = json.loads(v)
        except json.JSONDecodeError:
            kwargs[k] = v
    out = TOOLS[ns.tool](**kwargs)
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    if "--cli" in sys.argv:
        rest = [a for a in sys.argv[1:] if a != "--cli"]
        raise SystemExit(_cli(rest))
    # 배너를 끈다 — stderr가 MCP 로그로 가고, 배너가 실제 오류를 밀어낸다.
    # 이 서버의 목적이 "Desktop 쪽에서 실패를 발견하기"이므로 로그가 읽혀야 한다.
    try:
        build_mcp().run(show_banner=False)
    except TypeError:            # fastmcp 판이 그 인자를 모르면 그대로 띄운다
        build_mcp().run()
