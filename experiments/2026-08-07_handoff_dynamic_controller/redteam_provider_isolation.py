#!/usr/bin/env python3
"""Red-team the provider sandbox. Every probe runs the REAL Seatbelt profile.

WHY PROBE INSTEAD OF READ THE PROFILE
------------------------------------
`seatbelt_profile()` opens with `(allow default)` and then denies two subtrees.
Reading that and concluding "the subject is isolated" is the same shape of error
this repo keeps recording: the profile is a true statement about two paths and
says nothing about every other path on the machine. So each probe executes
`/bin/cat` (or `/bin/ls`) under the actual profile and reports what came back.

No probe here calls a paid model. The five questions this file answers:

  Q1  can the subject read Project_in_progress / hidden_gold / prior results?
  Q2  can it bypass the socket client and read the corpus directly?
  Q3  can it forge the host action trace with self-reported path/range?
  Q4  is Claude session state reused between cells?
  Q5  can an invalid run be selectively removed by retrying?

Q3-Q5 are answered by reading the host code paths and asserting on them, because
they are properties of the runner rather than of the OS boundary.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_live_public_bundle import build_bundle  # noqa: E402
from _evaluator import frozen_surface_hashes  # noqa: E402
from run_live_phase_c import seatbelt_profile  # noqa: E402

try:
    from _providers import seatbelt_profile_v2
except ImportError:                                   # probe before adapter lands
    seatbelt_profile_v2 = None

SANDBOX = Path("/usr/bin/sandbox-exec")
PROJECT_ROOT = HERE.parents[2]


def probe(profile: str, argv: list[str]) -> tuple[bool, str]:
    """Return (allowed, first line of output/stderr)."""
    proc = subprocess.run([str(SANDBOX), "-p", profile, *argv],
                          capture_output=True, text=True, timeout=30)
    blob = (proc.stdout or proc.stderr or "").strip().splitlines()
    return proc.returncode == 0, (blob[0][:110] if blob else "")


def main() -> int:
    if not SANDBOX.is_file():
        print("sandbox-exec unavailable; cannot probe", file=sys.stderr)
        return 2

    findings: list[dict] = []

    def record(qid: str, name: str, allowed: bool, expected_allowed: bool,
               detail: str = "") -> None:
        leaked = allowed and not expected_allowed
        findings.append({"q": qid, "probe": name, "reachable": allowed,
                         "expected_reachable": expected_allowed,
                         "leak": leaked, "detail": detail})
        mark = "LEAK" if leaked else ("ok" if allowed == expected_allowed else "blocked")
        print(f"  [{mark:>7}] {qid} {name}")

    with tempfile.TemporaryDirectory(prefix="rt-", dir="/private/tmp") as tmp:
        bundle = Path(tmp) / "b"
        build_bundle(bundle, "variant-L", "HD01")
        control = bundle / "control"
        profiles = {"v1 (current)": seatbelt_profile(PROJECT_ROOT, control)}
        if seatbelt_profile_v2 is not None:
            profiles["v2 (hardened)"] = seatbelt_profile_v2(PROJECT_ROOT, control)

        targets = [
            ("Q1", "experiment hidden_gold/gold.json",
             HERE / "hidden_gold" / "gold.json", False),
            ("Q1", "prior live results (live_pilot_attempt9.json)",
             HERE / "results" / "live_pilot_attempt9.json", False),
            ("Q1", "PREREGISTRATION.md", HERE / "PREREGISTRATION.md", False),
            ("Q2", "bundle control/corpus (socket bypass)",
             control / "corpus" / "docs" / "HANDOFF.md", False),
            ("Q2", "bundle control/input_manifest.json",
             control / "input_manifest.json", False),
            ("Q2", "subject-visible task.json (must stay readable)",
             bundle / "subject" / "task.json", True),
            # The channels a Claude subject has that a Codex subject does not.
            ("Q1", "~/.claude.json (account/config metadata; accepted residual)",
             Path.home() / ".claude.json", True),
            ("Q4", "~/.claude/projects transcripts of THIS workspace",
             Path.home() / ".claude" / "projects", False),
            ("Q1", "~/.codex history", Path.home() / ".codex", False),
        ]

        for label, profile in profiles.items():
            print(f"\n== Seatbelt {label} ==")
            for qid, name, path, expected in targets:
                if not path.exists():
                    print(f"  [   skip] {qid} {name} (absent)")
                    continue
                argv = (["/bin/ls", str(path)] if path.is_dir()
                        else ["/bin/cat", str(path)])
                allowed, detail = probe(profile, argv)
                record(f"{qid}/{label.split()[0]}", name, allowed, expected, detail)

    # ---- Q3: can a subject forge the host trace? -------------------------
    print("\n== Q3 host-trace forgery (code property, not OS) ==")
    src = (HERE / "run_live_phase_c.py").read_text(encoding="utf-8")
    trace_fn = src[src.index("def _trace_from_subject"):src.index("def _invalid_trace")]
    host_owned = "**fields" in trace_fn and "state.trace_fields()" in trace_fn
    model_reads = '"reads": response' in trace_fn or '"actions": response' in trace_fn
    findings.append({"q": "Q3", "probe": "reads/actions come from host state",
                     "reachable": model_reads, "expected_reachable": False,
                     "leak": model_reads,
                     "detail": "trace_fields() supplies actions/reads/stop_reason"})
    print(f"  [{'LEAK' if model_reads else 'ok':>7}] Q3 actions/reads sourced from host "
          f"state (host_owned={host_owned})")

    # ---- Q4: session reuse ------------------------------------------------
    print("\n== Q4 session/history reuse between cells ==")
    prov = (HERE / "_providers.py")
    text = prov.read_text(encoding="utf-8") if prov.is_file() else ""
    for flag, need in (("--no-session-persistence", True), ("--resume", False),
                       ("--continue", False)):
        present = flag in text
        bad = present is not need
        findings.append({"q": "Q4", "probe": f"claude adapter uses {flag}",
                         "reachable": present, "expected_reachable": need,
                         "leak": bad, "detail": ""})
        print(f"  [{'LEAK' if bad else 'ok':>7}] Q4 {flag} present={present} "
              f"(required={need})")

    # ---- Q5: selective removal of invalid runs ---------------------------
    print("\n== Q5 invalid-run retry / selective removal ==")
    refuses_overwrite = "refusing to overwrite an existing live result" in src
    q5_checks = [("runner refuses to overwrite an existing result file",
                  refuses_overwrite)]
    for filename in ("phase_c_live_config.json", "phase_c_codex_v2_config.json",
                     "phase_c_claude_config.json"):
        config = json.loads((HERE / filename).read_text(encoding="utf-8"))
        q5_checks.extend([
            (f"{filename}: retry_count == 0", config.get("retry_count") == 0),
            (f"{filename}: invalid-run record-and-do-not-replace",
             config.get("invalid_run_policy") == "record-V1-and-do-not-replace"),
        ])
    for name, ok in q5_checks:
        findings.append({"q": "Q5", "probe": name, "reachable": not ok,
                         "expected_reachable": False, "leak": not ok, "detail": ""})
        print(f"  [{'LEAK' if not ok else 'ok':>7}] Q5 {name}")

    leaks = [f for f in findings if f["leak"]]
    hardened_leaks = [f for f in leaks
                      if f["q"].endswith("/v2") or "/" not in f["q"]]
    out = {
        "n_probes": len(findings),
        "leaks": leaks,
        "hardened_profile_leaks": hardened_leaks,
        "hardened_profile_passed": not hardened_leaks,
        "frozen_surface_hashes": frozen_surface_hashes(),
        "findings": findings,
    }
    (HERE / "results" / "redteam_provider_isolation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\n{len(leaks)} historical/all-profile leak(s), "
          f"{len(hardened_leaks)} hardened leak(s) of {len(findings)} probes -> "
          f"results/redteam_provider_isolation.json")
    for f in leaks:
        print(f"  LEAK {f['q']} {f['probe']}")
    return 1 if hardened_leaks else 0


if __name__ == "__main__":
    raise SystemExit(main())
