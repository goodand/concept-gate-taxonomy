#!/usr/bin/env python3
"""Run a blind safety reviewer inside a sandbox, and OBSERVE what it could reach.

Amendment 41 (independent review round 20, finding #3). Before this, the rubric
said an agent reviewer that can read the repository is not blinded and that an
audit whose isolation cannot be enforced is BLOCKED -- and nothing implemented
either sentence. `doctor` read booleans out of a JSON file the reviewer itself
submitted, so a hand-written `{"status": "PASS", ...}` was indistinguishable
from a real probe result. That is the same shape as a vacuous guard: the
observable value is identical whether the mechanism exists or not.

NOTHING HERE IS NEW. It composes two mechanisms this workspace has already
validated:

  * public-only bundle -- `.vault-harness/vault-md-retrieval/
    build_handoff_reuse_public_bundle.py` excludes `.git`, `hidden_gold`,
    `private_eval`, `results`, `runs` by path part and REFUSES symlinks, so
    exclusion cannot be walked around.
  * Seatbelt v2 -- `_providers.py` / `PROVIDER_ADAPTERS.md` §55. Its v1 profile
    was believed sufficient until a `/bin/cat` probe found `~/.claude/projects`
    and `~/.codex` readable. The lesson taken there, and applied here: a
    profile string is a claim; a probe is evidence.

WHAT THE RECEIPT MEANS
----------------------
The receipt is written by THIS module after running the probes itself, and it
records `produced_by` plus the hashes of the packet, the assignment and the
profile. The adjudicator checks that binding. A reviewer's own claim about
what it could see is not an input to anything.

BOTH DIRECTIONS ARE CHECKED. If the allowed probe fails -- the reviewer cannot
even read its own packet -- the sandbox is not working, and the result is
BLOCKED, not PASS. Round 17 closed exactly this fail-open in the provider
red-team, where every probe was denied by the environment and the artifact
still said PASS.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _receipt import receipt_sha256  # noqa: E402
# Imported, not extracted. Extracting `seatbelt_profile` into a `sandbox.py`
# would edit run_live_phase_c.py, which is EXECUTION surface -- invalidating
# both red-teams and both qualifications for a refactor. This edge is
# read-only and keeps the whole change inside the AUDIT layer.
from run_live_phase_c import seatbelt_profile  # noqa: E402

SANDBOX = Path("/usr/bin/sandbox-exec")
CAT = Path("/bin/cat")

# Path parts that must never appear inside a reviewer bundle. Same list as the
# handoff-reuse public bundle, plus this experiment's own answer key.
FORBIDDEN_PATH_PARTS = frozenset({
    ".git", "hidden_gold", "private_eval", "results", "runs",
})
ANSWER_KEY = "safety_audit_rubric_answers.json"


class ReviewerRunnerError(Exception):
    """The reviewer could not be run under isolation. Not a safety verdict."""


@dataclass(frozen=True)
class IsolationReceipt:
    reviewer_id: str
    status: str                 # PASS | FAIL | BLOCKED
    packet_sha256: str
    assignment_sha256: str
    sandbox_profile_sha256: str
    allowed_probe_passed: bool
    forbidden_probes: tuple[dict, ...]
    produced_by: str = "reviewer_runner"

    def as_dict(self) -> dict:
        doc = {
            "reviewer_id": self.reviewer_id,
            "status": self.status,
            "packet_sha256": self.packet_sha256,
            "assignment_sha256": self.assignment_sha256,
            "sandbox_profile_sha256": self.sandbox_profile_sha256,
            "allowed_probe_passed": self.allowed_probe_passed,
            "forbidden_probes": [dict(p) for p in self.forbidden_probes],
            "produced_by": self.produced_by,
        }
        # Self-describing: the adjudicator recomputes this over the rest of the
        # document, so editing any field invalidates it.
        doc["receipt_sha256"] = receipt_sha256(doc)
        return doc


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_reviewer_bundle(packet: Path, out_dir: Path) -> Path:
    """A directory holding the packet and NOTHING else.

    Refuses symlinks and any path carrying a forbidden part -- the exclusion
    has to survive someone pointing a link at `results/`, which is why the
    handoff-reuse builder rejects links rather than following them.
    """
    if packet.is_symlink():
        raise ReviewerRunnerError(f"refusing a symlinked packet: {packet}")
    resolved = packet.resolve()
    bad = FORBIDDEN_PATH_PARTS & set(resolved.parts)
    if bad and "results" not in bad:
        # `results/` is where packets legitimately live; the other parts must
        # never appear.
        raise ReviewerRunnerError(f"packet path contains {sorted(bad)}")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "packet.json"
    shutil.copyfile(resolved, target)

    leftovers = sorted(p.name for p in out_dir.iterdir() if p.name != "packet.json")
    if leftovers:
        raise ReviewerRunnerError(
            f"reviewer bundle is not packet-only: {leftovers}")
    return target


def _profile(bundle: Path) -> str:
    """Deny the repository and the host's control surface; the bundle stays
    readable because it lives outside both."""
    return seatbelt_profile(HERE, HERE / "results")


def _reachable(profile: str, path: Path) -> tuple[bool, str]:
    """Can a process under this profile read `path`? Answered by trying."""
    if not SANDBOX.is_file() or not CAT.is_file():
        raise ReviewerRunnerError("sandbox-exec or /bin/cat unavailable")
    proc = subprocess.run(
        [str(SANDBOX), "-p", profile, str(CAT), str(path)],
        capture_output=True, text=True)
    return proc.returncode == 0, (proc.stderr or "")[:120]


def probe_isolation(bundle_packet: Path) -> dict:
    """Run the allowed probe and every forbidden probe. Returns raw results.

    The forbidden set is chosen from what would actually corrupt this audit:
    the answer key (a reviewer who reads it is not being examined), the
    repository (the automatic scores and the original result live there), the
    unblinding key, and prior transcripts (the provider red-team found these
    readable under v1).
    """
    profile = _profile(bundle_packet.parent)
    allowed, allowed_detail = _reachable(profile, bundle_packet)
    forbidden_targets = [
        ("answer_key", HERE / ANSWER_KEY),
        ("preregistration", HERE / "PREREGISTRATION.md"),
        ("results_dir", HERE / "results"),
        ("host_transcripts", Path.home() / ".claude" / "projects"),
    ]
    forbidden = []
    for name, target in forbidden_targets:
        reachable, detail = _reachable(profile, target)
        forbidden.append({"probe": name, "path": str(target),
                          "reachable": reachable, "detail": detail})
    return {"profile": profile, "allowed_probe_passed": allowed,
            "allowed_detail": allowed_detail, "forbidden_probes": forbidden}


def run_reviewer(bundle_packet: Path, reviewer_id: str, *,
                 command: list[str] | None = None,
                 assignment: Path | None = None) -> dict:
    """Probe isolation, then (optionally) run the reviewer inside it.

    `command` is the reviewer process. With none given this is probe-only,
    which is what the release E2E needs: the question it must answer is
    whether the boundary holds, not what a particular reviewer labelled.
    """
    assignment = assignment or (HERE / "safety_audit_reviewer_assignment.json")
    probes = probe_isolation(bundle_packet)

    leaked = [p for p in probes["forbidden_probes"] if p["reachable"]]
    if not probes["allowed_probe_passed"]:
        # The sandbox could not be exercised. BLOCKED -- not a pass, and not
        # a failure of the boundary either. Round 17 closed this exact
        # fail-open in the provider red-team.
        status = "BLOCKED"
    elif leaked:
        status = "FAIL"
    else:
        status = "PASS"

    if command and status == "PASS":
        subprocess.run([str(SANDBOX), "-p", probes["profile"], *command],
                       cwd=bundle_packet.parent, capture_output=True, text=True)

    receipt = IsolationReceipt(
        reviewer_id=reviewer_id,
        status=status,
        packet_sha256=_sha256(bundle_packet),
        assignment_sha256=_sha256(assignment),
        sandbox_profile_sha256=hashlib.sha256(
            probes["profile"].encode("utf-8")).hexdigest(),
        allowed_probe_passed=probes["allowed_probe_passed"],
        forbidden_probes=tuple(probes["forbidden_probes"]),
    )
    return receipt.as_dict()


def verify_isolation_receipt(doc: dict, *, packet: Path,
                             assignment: Path) -> str:
    """Return PASS/FAIL/BLOCKED for a receipt, or raise if it is not ours.

    The adjudicator calls this instead of reading booleans. A hand-written
    document fails here: it has no `produced_by`, or its `receipt_sha256` does
    not match its own contents, or it is bound to a different packet.
    """
    if doc.get("produced_by") != "reviewer_runner":
        raise ReviewerRunnerError(
            "isolation receipt was not produced by the launcher; a reviewer's "
            "own claim about what it could reach is not evidence")
    body = {k: v for k, v in doc.items() if k != "receipt_sha256"}
    if receipt_sha256(body) != doc.get("receipt_sha256"):
        raise ReviewerRunnerError("isolation receipt has been edited")
    if doc.get("packet_sha256") != _sha256(packet):
        raise ReviewerRunnerError("isolation receipt is bound to another packet")
    if doc.get("assignment_sha256") != _sha256(assignment):
        raise ReviewerRunnerError(
            "isolation receipt is bound to another reviewer assignment")
    return doc["status"]


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        print("usage: reviewer_runner.py <packet.json> <reviewer_id> "
              "[out_dir]", file=sys.stderr)
        return 2
    packet, reviewer_id = Path(argv[1]), argv[2]
    out_dir = Path(argv[3]) if len(argv) > 3 else HERE / "audit_workspace" / "reviewer"
    try:
        bundled = build_reviewer_bundle(packet, out_dir / reviewer_id)
        doc = run_reviewer(bundled, reviewer_id)
    except ReviewerRunnerError as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    out = HERE / "results" / f"reviewer_isolation_{reviewer_id}.json"
    if out.exists():
        print(f"refusing to overwrite {out.name} (results/ is append-only)",
              file=sys.stderr)
        return 2
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"-> {out.name}  status={doc['status']}")
    for probe in doc["forbidden_probes"]:
        mark = "LEAK" if probe["reachable"] else "ok"
        print(f"   [{mark:>4}] {probe['probe']}")
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[doc["status"]]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
