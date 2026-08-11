#!/usr/bin/env python3
"""One verifier for "is this result the artifact a real primary run produced?"

Amendment 39 (independent review round 18). The audit gate had its own
provenance check: it read the attempt ledger, matched `output_file` by NAME,
and stopped. Measured -- a completed row was written, the result's
`recommended_actions` were then edited, and the packet built anyway:

    accepted_after_mutation: true
    ledger_has_output_sha256: false

Meanwhile `run_live_phase_c.verify_primary_attempt_artifacts()` had compared
`output_sha256` for a month, as a gate on new attempt claims. The defect was
not a missing capability. It was a second, weaker implementation of a check
that already existed -- the same "helper exists, call site does not" shape
this experiment has now hit at four different layers.

So this module does not implement verification. It composes the existing
ledger machinery and returns a receipt; the audit code takes the receipt and
never reads a ledger itself.

Precedent, reused rather than re-derived:

  * E2.2.3's evaluator refuses to score at all when the result file's
    self-report disagrees with the frozen manifest (`PROVENANCE_FAIL`).
    Provenance failure stops the pipeline; it is not a warning attached to a
    number that gets reported anyway.
  * `DESIGN_DECISION_surface_separation.md` (2026-07-28) required one
    canonical path that smoke, the real run and re-runs all take.

WHY `mode` EXISTS. The offline E2E has no provider, so its artifact cannot
have a real attempt behind it. The previous answer was to let the CLI's
`--out-root` relocate the authorization and ledger, which made an arbitrary
directory the provenance authority -- a copied authorization and a
hand-written ledger became indistinguishable from the real ones. Now the
checks still RUN against that tree (a check switched off in every test is a
check nobody has seen work), but the receipt is stamped
`mode="synthetic-e2e"` and that stamp travels into the packet and the
adjudicated bundle. A synthetic run can no longer be mistaken for an audit.
"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_live_phase_c import (  # noqa: E402
    PRIMARY_ATTEMPT_LEDGER_NAME, _legacy_ledger_prefix_matches_known_hashes,
    find_completed_attempt, read_attempt_ledger, verify_ledger_chain,
    verify_primary_attempt_artifacts)

VERIFIED = "verified"
SYNTHETIC = "synthetic-e2e"


class ProvenanceError(Exception):
    """The result's origin could not be established. No packet is produced."""


@dataclass(frozen=True)
class VerifiedRunReceipt:
    """What the audit is allowed to know about where a result came from.

    The audit code receives this and nothing else -- it does not open the
    ledger, the authorization, or the config. One reader means one contract.
    """
    result_file: str
    result_sha256: str
    config_file: str
    config_sha256: str
    authorization_sha256: str
    attempt_id: str | None
    mode: str
    evidence: tuple[str, ...] = field(default_factory=tuple)

    def as_dict(self) -> dict:
        return {
            "result_file": self.result_file,
            "result_sha256": self.result_sha256,
            "config_file": self.config_file,
            "config_sha256": self.config_sha256,
            "authorization_sha256": self.authorization_sha256,
            "attempt_id": self.attempt_id,
            "mode": self.mode,
            "evidence": list(self.evidence),
        }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_run(result_path: Path, *, root: Path = HERE,
               mode: str = VERIFIED) -> VerifiedRunReceipt:
    """Establish that `result_path` is the artifact a recorded, completed
    primary attempt produced -- byte for byte.

    `root` locates the authorization and ledger. It is NOT an authority
    switch: `mode` records which tree was trusted, and a non-default root is
    only legitimate together with `mode=SYNTHETIC`.
    """
    if mode not in (VERIFIED, SYNTHETIC):
        raise ProvenanceError(f"unknown provenance mode {mode!r}")
    if mode == VERIFIED and root != HERE:
        raise ProvenanceError(
            "a verified receipt must come from the canonical results/ tree; "
            "an arbitrary root is an output location, not an authority")

    evidence: list[str] = []
    data = json.loads(result_path.read_text(encoding="utf-8"))
    result_sha = _sha256(result_path)

    auth_path = root / "results" / "PRIMARY_AUTHORIZATION.json"
    if not auth_path.is_file():
        raise ProvenanceError(f"no primary authorization at {auth_path}")
    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    auth_sha = _sha256(auth_path)
    evidence.append(f"authorization={auth_sha[:12]}")

    if data.get("config_file") != auth["config_file"]:
        raise ProvenanceError(
            f"no authorization covers this result: it names config "
            f"{data.get('config_file')!r}, the authorization covers "
            f"{auth['config_file']!r}")
    expected_config = auth.get("config_sha256")
    if expected_config and data.get("config_sha256") != expected_config:
        raise ProvenanceError(
            "config sha256 does not match the authorization -- the result was "
            "produced under a different config than the one authorized")
    evidence.append(f"config={auth['config_file']}")

    results_dir = root / "results"
    rows = read_attempt_ledger(results_dir)
    if not rows:
        raise ProvenanceError(
            f"attempt ledger is empty or missing: {results_dir}")
    if not verify_ledger_chain(rows):
        raise ProvenanceError(
            "attempt ledger hash chain does not verify -- the record of which "
            "attempts ran cannot be trusted")

    # The SAME pin the claim gate applies. Round 19, finding #6: the audit's
    # verifier checked the chain but not the git-committed anchor on the
    # pre-chain rows, so a ledger the runner would refuse still produced a
    # receipt. A self-hash chain has no anchor outside itself; the pin is
    # that anchor, and applying one without the other is applying neither.
    ledger_path = results_dir / PRIMARY_ATTEMPT_LEDGER_NAME
    with ledger_path.open(encoding="utf-8") as handle:
        if not _legacy_ledger_prefix_matches_known_hashes(handle, ledger_path):
            raise ProvenanceError(
                "the pre-chain legacy rows in this ledger no longer match "
                "their git-committed pin -- a recorded primary attempt was "
                "deleted or edited")
    evidence.append(f"ledger_rows={len(rows)}")

    # The same tamper-detection the runner applies before granting a NEW
    # attempt. Reused, not reimplemented: this is the check the audit gate
    # was missing while it sat one import away.
    # Storage differs between canonical and synthetic; the ALGORITHM does
    # not. Round 19: this function could not point the shared verifier at a
    # synthetic tree, so it re-implemented the hash comparison -- the second
    # copy that round 18 had just finished removing one layer down.
    unverifiable = verify_primary_attempt_artifacts(rows, auth_sha, results_dir)
    if unverifiable:
        raise ProvenanceError(
            f"completed attempts whose artifacts no longer verify: "
            f"{unverifiable}")

    match = find_completed_attempt(rows, auth_sha, result_sha)
    if match is None:
        completed = [r for r in rows
                     if r.get("authorization_sha256") == auth_sha
                     and r.get("status") == "completed"]
        raise ProvenanceError(
            f"no completed attempt recorded output_sha256={result_sha[:12]}; "
            "the file was edited after the run, or it is not the artifact the "
            "run produced (completed rows: "
            f"{[(r.get('output_file'), str(r.get('output_sha256'))[:12]) for r in completed]})")
    evidence.append(f"attempt={match.get('attempt_id')}")

    return VerifiedRunReceipt(
        result_file=result_path.name,
        result_sha256=result_sha,
        config_file=data["config_file"],
        config_sha256=data["config_sha256"],
        authorization_sha256=auth_sha,
        attempt_id=match.get("attempt_id"),
        mode=mode,
        evidence=tuple(evidence),
    )
