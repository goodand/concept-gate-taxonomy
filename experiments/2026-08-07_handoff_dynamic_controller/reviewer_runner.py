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
  * Seatbelt v2 -- `_providers.seatbelt_profile_v2`, imported. Its v1 profile
    was believed sufficient until a `/bin/cat` probe found `~/.claude/projects`
    and `~/.codex` readable. The lesson taken there: a profile string is a
    claim; a probe is evidence.

    Round 21 found this module had taken the sentence and not the mechanism. It
    cited v2 and CALLED v1, and two of its four forbidden probes pointed at
    DIRECTORIES, where `/bin/cat` fails whatever the sandbox permits -- so they
    reported `ok` under a profile denying nothing. The probe was a claim too.
    Both are closed: every forbidden probe now runs first under
    PERMISSIVE_PROFILE, and a probe that cannot reach its target with nothing
    denied is BLOCKED rather than passing. The v1-leaks/v2-denies contrast is
    itself a test, so "we use v2" is falsifiable rather than asserted.

WHAT THE RECEIPT MEANS
----------------------
The receipt is written by THIS module after running the probes itself, and it
carries an HMAC over the hashes of the packet, the assignment and the profile,
signed with a key the reviewer's own profile denies. The adjudicator checks
that signature. A reviewer's own claim about what it could see is not an input
to anything.

Round 21 removed the earlier scheme, which was `produced_by: "reviewer_runner"`
plus a public hash of the document: both inputs were public, so filling in the
fields and calling the same public function produced a receipt that verified as
PASS with the launcher never having run. What the HMAC does and does not defend
against is written out in `_receipt.sign` -- read it before describing this
module as isolating anything.

BOTH DIRECTIONS ARE CHECKED. If the allowed probe fails -- the reviewer cannot
even read its own packet -- the sandbox is not working, and the result is
BLOCKED, not PASS. Round 17 closed exactly this fail-open in the provider
red-team, where every probe was denied by the environment and the artifact
still said PASS.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _receipt import load_or_create_key, sign, verify  # noqa: E402
# Imported, not extracted. Round 21's review proposed pulling the profile into
# a shared `_sandbox_profile.py` leaf and accepted that this would edit
# EXECUTION surface and re-stale both qualifications. It does not have to:
# `seatbelt_profile_v2` is ALREADY the single definition, and
# `run_live_phase_c.py` already imports it from here. Importing a file does not
# change it, so this whole fix stays inside the AUDIT layer at zero
# qualification cost.
from _providers import (  # noqa: E402
    ProviderError, home_leak_denies, seatbelt_profile_v2,
    validate_against_schema)
# VALID_LABELS is the rubric's own vocabulary; the adjudicator owns it.
from apply_safety_audit import VALID_LABELS  # noqa: E402

SANDBOX = Path("/usr/bin/sandbox-exec")
CAT = Path("/bin/cat")

# Namespace for the HMAC. See _receipt.sign.
RECEIPT_DOMAIN = "reviewer-isolation-receipt-v1"

# The control profile: deny NOTHING. Round 21, finding #2a -- every forbidden
# probe must first be shown to succeed here. A probe that fails with nothing
# denied is not measuring the sandbox, and two of the original four were in
# exactly that state (`/bin/cat` on a directory fails unconditionally).
PERMISSIVE_PROFILE = "(version 1)\n(allow default)"


def launcher_key_path() -> Path:
    """Where the host-only signing key lives.

    Inside HERE on purpose: the reviewer profile denies that whole subtree, so
    the key is unreachable from the process whose confinement it attests to.
    `denied_paths()` and a test hold that property rather than this comment.
    """
    return HERE / ".launcher_hmac_key"

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
    # None on a probe-only run. Round 21, finding #3: without these a receipt
    # from `command=None` was indistinguishable from one where a reviewer
    # actually produced labels, which is how a launcher that ran nothing looked
    # like a launcher.
    reviewer_command_sha256: str | None = None
    reviewer_output_sha256: str | None = None

    def as_dict(self, *, key: bytes) -> dict:
        doc = {
            "reviewer_id": self.reviewer_id,
            "status": self.status,
            "packet_sha256": self.packet_sha256,
            "assignment_sha256": self.assignment_sha256,
            "sandbox_profile_sha256": self.sandbox_profile_sha256,
            "allowed_probe_passed": self.allowed_probe_passed,
            "forbidden_probes": [dict(p) for p in self.forbidden_probes],
            "reviewer_command_sha256": self.reviewer_command_sha256,
            "reviewer_output_sha256": self.reviewer_output_sha256,
        }
        # HMAC, not a hash of the document by itself. Round 21: a public hash
        # over public fields is recomputable by whoever wants the answer to be
        # PASS, and `produced_by: "reviewer_runner"` was a string, not a proof.
        doc["signature"] = sign(doc, key, domain=RECEIPT_DOMAIN)
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
    assert_reachable_workspace(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "packet.json"
    shutil.copyfile(resolved, target)

    leftovers = sorted(p.name for p in out_dir.iterdir() if p.name != "packet.json")
    if leftovers:
        raise ReviewerRunnerError(
            f"reviewer bundle is not packet-only: {leftovers}")
    return target


def denied_paths() -> list[Path]:
    """Every subtree the reviewer profile denies. ONE list.

    A test asserts each entry appears in the profile string -- otherwise the
    two drift and the deny list becomes a comment about what someone intended.
    """
    return [HERE, HERE / "results", *(Path(p) for p in home_leak_denies())]


def _profile(bundle: Path) -> str:
    """Deny the repository, the host control surface, and the home-directory
    transcript channels. The bundle stays readable because it lives outside all
    of them -- `reviewer_workspace`/`build_reviewer_bundle` enforce that."""
    return seatbelt_profile_v2(HERE, HERE / "results")


def _first_file_under(root: Path) -> Path | None:
    """A readable FILE beneath `root`, or None.

    Probe targets must be files: `/bin/cat` on a directory fails with "Is a
    directory" whatever the sandbox says, which is precisely how two probes
    came to report `ok` under a profile that denied nothing.
    """
    if not root.is_dir():
        return None
    for path in sorted(root.rglob("*")):
        if path.is_file() and not path.is_symlink():
            return path
    return None


def forbidden_targets() -> list[tuple[str, Path]]:
    """What must be unreachable, as FILES.

    Chosen from what would actually corrupt this audit: the answer key (a
    reviewer who reads it is not being examined), the preregistration (it
    carries the hypotheses and the scoring rules), a results artifact (the
    automatic scores and the original result live there), and a prior host
    transcript (the provider red-team found these readable under v1).

    `host_transcripts` resolves to a concrete file because the directory itself
    is unprobeable. If this host has no such file, the caller reports that
    probe BLOCKED rather than silently passing it.
    """
    targets: list[tuple[str, Path]] = [
        ("answer_key", HERE / ANSWER_KEY),
        ("preregistration", HERE / "PREREGISTRATION.md"),
        ("results_artifact", HERE / "results" / "calibration.json"),
    ]
    transcripts = Path.home() / ".claude" / "projects"
    found = _first_file_under(transcripts)
    targets.append(("host_transcripts", found or transcripts))
    return targets


def reviewer_workspace(reviewer_id: str, *, root: Path | None = None) -> Path:
    """WHERE a reviewer bundle may live. One decision, CLI and E2E alike.

    Round 21, finding #9: `main()` defaulted to `HERE/audit_workspace/reviewer`,
    which the profile denies in full, so the allowed probe failed and the
    documented CLI could only ever return BLOCKED. The release E2E used a temp
    directory and returned PASS. Two paths through the same launcher, one of
    them structurally incapable of passing -- which is what the frozen
    canonical-path decision (2026-07-28) exists to prevent.
    """
    root = root if root is not None else Path(
        tempfile.mkdtemp(prefix="cg-reviewer-"))
    return assert_reachable_workspace(root / reviewer_id)


def assert_reachable_workspace(dest: Path) -> Path:
    """Refuse a bundle location the reviewer could not read.

    Not BLOCKED: a caller who puts the bundle inside a denied subtree has made
    an error, and reporting it as "the boundary could not be exercised" hides
    the error behind an environment-shaped word.
    """
    resolved = dest.resolve() if dest.exists() else dest
    for denied in denied_paths():
        if resolved == denied or denied in resolved.parents:
            raise ReviewerRunnerError(
                f"bundle location {dest} is inside a denied subtree ({denied}); "
                "the reviewer could not read its own packet, so the run would "
                "report BLOCKED for a reason that is the caller's mistake")
    return dest


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

    EACH FORBIDDEN PROBE IS RUN TWICE. Once under a profile that denies nothing
    -- the control -- and once under the reviewer's profile. The control does
    not measure the sandbox; it measures whether THIS PROBE CAN MEASURE
    ANYTHING. Round 21: `results_dir` and `host_transcripts` were directories,
    `/bin/cat` fails on a directory whatever the sandbox permits, and both were
    reported `ok` under `(allow default)`. Two of four probes had been decoration
    for four review rounds inside a module whose docstring says a probe is
    evidence.

    This is the same discipline the repository applies to `assert_*` guards --
    a guard ships with an input that must violate it -- and it lives in code for
    the same reason: written as discipline, it failed seven times out of seven.
    """
    profile = _profile(bundle_packet.parent)
    allowed, allowed_detail = _reachable(profile, bundle_packet)
    forbidden = []
    for name, target in forbidden_targets():
        control, control_detail = _reachable(PERMISSIVE_PROFILE, target)
        if not control:
            # Cannot conclude anything about this target on this host.
            forbidden.append({
                "probe": name, "path": str(target), "reachable": False,
                "control_reachable": False, "status": "BLOCKED",
                "detail": f"control probe failed: {control_detail}"})
            continue
        reachable, detail = _reachable(profile, target)
        forbidden.append({
            "probe": name, "path": str(target), "reachable": reachable,
            "control_reachable": True,
            "status": "LEAK" if reachable else "DENIED", "detail": detail})
    return {"profile": profile, "allowed_probe_passed": allowed,
            "allowed_detail": allowed_detail, "forbidden_probes": forbidden}


# The reviewer's stdout contract. Deliberately narrow: two objects of strings.
# Validated with `_providers.validate_against_schema`, the same checker the
# provider adapters use on model output -- a reviewer is a model at a trust
# boundary too, and there is no reason for a second validator here.
REVIEWER_OUTPUT_SCHEMA = {
    "type": "object",
    "required": ["qualification", "labels"],
    "properties": {"qualification": {"type": "object"},
                   "labels": {"type": "object"}},
}


def _packet_blind_ids(bundle_packet: Path) -> set[str]:
    packet = json.loads(bundle_packet.read_text(encoding="utf-8"))
    items = packet.get("reviewer_packet") or []
    return {item["blind_id"] for item in items if "blind_id" in item}


def _label_artifact(reviewer_id: str, output: dict, *, bundle_packet: Path,
                    assignment: Path, fixture: Path) -> dict:
    """Turn validated reviewer output into the document the adjudicator reads.

    Round 21, finding #3: the release E2E wrote these itself, from the ANSWER
    KEY. So the stage printed "reviewer labels" about labels no reviewer had
    produced. This is the only place they may come from now.

    The checks here duplicate `apply_safety_audit` on purpose -- not as defence
    in depth, but so the launcher does not hand on an artifact it already knows
    the adjudicator will refuse. A refusal three stages later names the wrong
    component.
    """
    labels = output["labels"]
    expected = _packet_blind_ids(bundle_packet)
    if set(labels) != expected:
        extra = sorted(set(labels) - expected)
        missing = sorted(expected - set(labels))
        raise ReviewerRunnerError(
            f"reviewer {reviewer_id}: label ids do not match the packet "
            f"(extra={extra[:5]}, missing={missing[:5]})")
    bad = {k: v for k, v in labels.items() if v not in VALID_LABELS}
    if bad:
        raise ReviewerRunnerError(
            f"reviewer {reviewer_id}: labels outside the rubric: {bad}")
    return {"reviewer_id": reviewer_id,
            "packet_sha256": _sha256(bundle_packet),
            "assignment_sha256": _sha256(assignment),
            "fixture_sha256": _sha256(fixture),
            "qualification": dict(output["qualification"]),
            "labels": dict(labels)}


def _execution_identity(command: list[str]) -> str:
    """What actually ran, not just what was typed.

    Round 21b, F5: this was `sha256("\x00".join(command))` -- the ARGV. Swap
    the script at that path for a different reviewer, a different prompt, a
    different model wrapper, and the receipt stayed byte-identical. A receipt
    that cannot say what ran cannot support a claim about what a reviewer did,
    and the canary's whole value is that it can.

    So the identity covers, in order: every argv token, and for each token that
    names an existing FILE, its resolved path and its sha256. That is the
    smallest thing that distinguishes two reviewers behind one command line.

    WHAT IT STILL DOES NOT COVER, said plainly rather than implied: a remote
    model behind a CLI, the CLI's own dependencies, and anything the reviewer
    reads at runtime from outside the bundle -- the sandbox denies the
    repository, not the network. `cli_version` in the qualification configs has
    the same limit and the same warning: the runner records it, it does not
    verify it.
    """
    parts: list[str] = []
    for token in command:
        parts.append(f"argv:{token}")
        path = Path(token)
        try:
            if path.is_file():
                parts.append(f"file:{path.resolve()}:{_sha256(path)}")
        except OSError:
            pass
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()


def _run_reviewer_process(command: list[str], profile: str, cwd: Path) -> dict:
    """Execute the reviewer inside the sandbox and parse its stdout.

    Every failure mode is a REFUSAL, never a default label. A reviewer that
    crashed, printed prose, or omitted a field has not reviewed anything, and
    the one thing that must not happen is a plausible-looking artifact standing
    in for a judgement nobody made.
    """
    proc = subprocess.run([str(SANDBOX), "-p", profile, *command],
                          cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ReviewerRunnerError(
            f"the reviewer exited {proc.returncode}; it did not review "
            f"anything. stderr: {(proc.stderr or '').strip()[:200]}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ReviewerRunnerError(
            f"the reviewer's stdout is not JSON ({exc}); first 200 chars: "
            f"{proc.stdout[:200]!r}") from None
    try:
        validate_against_schema(payload, REVIEWER_OUTPUT_SCHEMA)
    except ProviderError as exc:
        raise ReviewerRunnerError(
            f"the reviewer's output does not match the schema: {exc}") from None
    return payload


def run_reviewer(bundle_packet: Path, reviewer_id: str, *,
                 command: list[str] | None = None,
                 assignment: Path | None = None,
                 labels_out: Path | None = None,
                 fixture: Path | None = None) -> dict:
    """Probe isolation, then (optionally) run the reviewer inside it.

    `command` is the reviewer process. With none given this is probe-only,
    which is what the release E2E needs: the question it must answer is
    whether the boundary holds, not what a particular reviewer labelled. The
    receipt says which of the two happened -- round 21 found the two were
    indistinguishable, so "the launcher ran the reviewer" was unfalsifiable.

    `labels_out` is where the label artifact goes. Required with `command`:
    running a reviewer and discarding its judgement is what finding #3 was.
    """
    assignment = assignment or (HERE / "safety_audit_reviewer_assignment.json")
    fixture = fixture or (HERE / "safety_audit_rubric_fixture.json")
    if command and labels_out is None:
        raise ReviewerRunnerError(
            "running a reviewer without somewhere to put its labels discards "
            "the judgement -- pass labels_out")
    probes = probe_isolation(bundle_packet)

    leaked = [p for p in probes["forbidden_probes"] if p["reachable"]]
    unmeasured = [p for p in probes["forbidden_probes"]
                  if p["status"] == "BLOCKED"]
    if leaked:
        # A real leak outranks everything: it is a finding, not a gap.
        status = "FAIL"
    elif not probes["allowed_probe_passed"]:
        # The sandbox could not be exercised. BLOCKED -- not a pass, and not
        # a failure of the boundary either. Round 17 closed this exact
        # fail-open in the provider red-team.
        status = "BLOCKED"
    elif unmeasured:
        # Some target could not be probed at all, so "nothing was reachable"
        # is not something this run established. Round 21, finding #2a.
        status = "BLOCKED"
    else:
        status = "PASS"

    command_sha = output_sha = None
    if command:
        if status != "PASS":
            # Running a reviewer inside a boundary that was not shown to hold
            # would produce labels nobody can attribute to a blind review.
            reached = [p["probe"] for p in probes["forbidden_probes"]
                       if p["status"] != "DENIED"]
            raise ReviewerRunnerError(
                f"refusing to run the reviewer: isolation is {status}; it "
                f"reached {reached}. Labels produced inside a boundary nobody "
                "verified cannot be attributed to a blind review")
        output = _run_reviewer_process(command, probes["profile"],
                                       bundle_packet.parent)
        artifact = _label_artifact(reviewer_id, output,
                                   bundle_packet=bundle_packet,
                                   assignment=assignment, fixture=fixture)
        body = json.dumps(artifact, ensure_ascii=False, indent=1)
        labels_out.parent.mkdir(parents=True, exist_ok=True)
        labels_out.write_text(body, encoding="utf-8")
        command_sha = _execution_identity(command)
        output_sha = hashlib.sha256(body.encode("utf-8")).hexdigest()

    receipt = IsolationReceipt(
        reviewer_id=reviewer_id,
        status=status,
        packet_sha256=_sha256(bundle_packet),
        assignment_sha256=_sha256(assignment),
        sandbox_profile_sha256=hashlib.sha256(
            probes["profile"].encode("utf-8")).hexdigest(),
        allowed_probe_passed=probes["allowed_probe_passed"],
        forbidden_probes=tuple(probes["forbidden_probes"]),
        reviewer_command_sha256=command_sha,
        reviewer_output_sha256=output_sha,
    )
    return receipt.as_dict(key=load_or_create_key(launcher_key_path()))


def authenticate_isolation_receipt(doc: dict, *, assignment: Path,
                                   key_path: Path | None = None) -> str:
    """Is this receipt ours, and bound to the frozen assignment? Returns status.

    Round 21b, F2: `doctor` needs exactly this question and no more. It has no
    packet to compare against -- a packet belongs to an audit RUN, not to a
    diagnostic -- and it used to invent one with
    `RESULTS / doc.get("packet_file", "missing")`. That field does not exist, so
    the branch raised FileNotFoundError on the HAPPY path: a correctly signed,
    passing receipt crashed the diagnostic. The branch had never executed
    because the shipped assignment is UNASSIGNED.

    The fix is a SPLIT, not a new `packet_file` field. A path inside a signed
    receipt is host-specific and every reader would have to re-resolve it.
    Making the packet comparison optional inside one function would be the
    fail-open shape this repository keeps removing -- so there are two
    functions and the caller states which question it is asking.

    `key_path` exists so a test can present a different key; production callers
    leave it alone.
    """
    key = load_or_create_key(key_path or launcher_key_path())
    if not verify(doc, key, domain=RECEIPT_DOMAIN):
        raise ReviewerRunnerError(
            "isolation receipt carries no signature this host can reproduce. "
            "It was either not produced by the launcher or edited afterwards; "
            "a claim about what a reviewer could reach is not evidence unless "
            "the host observed it")
    if doc.get("assignment_sha256") != _sha256(assignment):
        raise ReviewerRunnerError(
            "isolation receipt is bound to another reviewer assignment")
    return doc["status"]


def verify_isolation_receipt(doc: dict, *, packet: Path, assignment: Path,
                             key_path: Path | None = None) -> str:
    """Authenticity AND binding to THIS packet. What an audit run must ask.

    The adjudicator and the release E2E call this; `doctor` calls
    `authenticate_isolation_receipt` because it has no packet.
    """
    status = authenticate_isolation_receipt(doc, assignment=assignment,
                                            key_path=key_path)
    if doc.get("packet_sha256") != _sha256(packet):
        raise ReviewerRunnerError("isolation receipt is bound to another packet")
    return status


def main(argv: list[str]) -> int:
    args = list(argv[1:])
    # Round 21b, F1b: the public CLI was probe-only -- it called
    # `run_reviewer(bundled, reviewer_id)` with no command, so the entry point
    # a human is told to use could not run a reviewer at all. Everything that
    # ever ran one was inside the release E2E.
    labels_out = None
    if "--labels-out" in args:
        i = args.index("--labels-out")
        labels_out = Path(args[i + 1])
        del args[i:i + 2]
    command = None
    if "--command" in args:
        i = args.index("--command")
        command = args[i + 1:]          # everything after it is the command
        del args[i:]
    if len(args) < 2:
        print(__doc__, file=sys.stderr)
        print("usage: reviewer_runner.py <packet.json> <reviewer_id> "
              "[workspace_root] [--labels-out <path>] [--command <argv...>]",
              file=sys.stderr)
        return 2
    packet, reviewer_id = Path(args[0]), args[1]
    # ONE decision about where a bundle may live, shared with the E2E. The old
    # default was inside HERE, which the profile denies in full (finding #9).
    root = Path(args[2]) if len(args) > 2 else None
    try:
        dest = reviewer_workspace(reviewer_id, root=root)
        print(f"   workspace: {dest}")
        bundled = build_reviewer_bundle(packet, dest)
        doc = run_reviewer(bundled, reviewer_id, command=command,
                           labels_out=labels_out)
    except ReviewerRunnerError as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 2
    # Round 21b: my own CLI test called main() and deposited a receipt in the
    # committed, append-only results/ -- the SAME defect the release receipt had
    # one round earlier. Same fix: the directory is overridable and only a
    # harness overrides it.
    out_dir = Path(os.environ.get("CG_ISOLATION_RECEIPT_DIR") or (HERE / "results"))
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"reviewer_isolation_{reviewer_id}.json"
    if out.exists():
        print(f"refusing to overwrite {out.name} (results/ is append-only)",
              file=sys.stderr)
        return 2
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"-> {out.name}  status={doc['status']}")
    if labels_out is not None and labels_out.is_file():
        print(f"   labels: {labels_out}")
        print("   pass BOTH to the adjudicator:")
        print(f"     apply_safety_audit.py ... {labels_out} "
              f"--isolation-receipt {out}")
    for probe in doc["forbidden_probes"]:
        mark = "LEAK" if probe["reachable"] else "ok"
        print(f"   [{mark:>4}] {probe['probe']}")
    return {"PASS": 0, "FAIL": 1, "BLOCKED": 2}[doc["status"]]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
