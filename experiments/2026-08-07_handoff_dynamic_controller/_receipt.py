#!/usr/bin/env python3
"""Canonical hash of a provenance receipt. One definition, no dependencies.

Amendment 41 (independent review round 20, finding #5). Commit `1f12e2f` was
titled "one canonical for each thing" and shipped `_receipt_sha256` twice --
once in the packet builder, once in the adjudicator -- with a comment citing a
test named `test_the_receipt_hash_is_computed_the_same_way_on_both_sides` that
did not exist. Two implementations of "are these the same receipt" can drift,
and the drift would be invisible: each side would agree with itself.

WHY A LEAF MODULE AND NOT `_provenance`
---------------------------------------
Measured before deciding:

    import apply_safety_audit               5,051 us
    import _provenance                     19,292 us   (pulls run_live_phase_c)

Putting this in `_provenance` and importing it from the adjudicator would
roughly quadruple that module's import cost, and -- the part that matters --
would make the adjudicator transitively depend on `run_live_phase_c` ->
`run_smoke`, `run_calibration`, `_providers`, `build_live_public_bundle`.
Development and orchestration modules would become dependencies of the audit
path, which is the layering inversion independent review round 14 already
named.

A leaf keeps one definition without creating that edge:

    _receipt.py            (imports nothing local)
       ^          ^                    ^
    _provenance  packet builder   adjudicator
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path


def receipt_sha256(receipt: dict | None) -> str | None:
    """Hash of a receipt in a form both sides compute identically.

    `sort_keys=True` is load-bearing: the packet writes the receipt with one
    key order and the adjudicator reads it back through JSON, which does not
    promise to preserve it. Without the sort the two sides could disagree
    about a receipt neither of them had changed.

    Returns None for None so callers can compare "no receipt" without a
    special case -- a packet built under a spec that does not require
    provenance carries `provenance: null`, and the key must record the same
    absence rather than a hash of the string "null".
    """
    if receipt is None:
        return None
    return hashlib.sha256(canonical_bytes(receipt)).hexdigest()


def canonical_bytes(doc: dict) -> bytes:
    """The one byte-form both a writer and a reader derive from a document."""
    return json.dumps(doc, sort_keys=True, ensure_ascii=False).encode("utf-8")


# ------------------------------------------------------ authentication ----
# Round 21, finding #1. A receipt whose integrity field is a PUBLIC hash of
# its own PUBLIC contents authenticates nothing: fill the fields in, call the
# same function, and the document verifies. That was measured -- a receipt
# claiming a passing sandbox probe was accepted with the launcher never having
# run. `produced_by: "reviewer_runner"` was a string anyone could type.
#
# WHAT SIGNING HERE DOES AND DOES NOT DEFEND AGAINST
# --------------------------------------------------
# Defends against:
#   * the reviewer -- an agent confined to a packet-only directory whose
#     Seatbelt profile denies the subtree holding the key. It cannot read the
#     key, so it cannot manufacture a receipt about its own confinement.
#   * a hand-authored document -- the failure this round actually found.
# Does NOT defend against:
#   * anyone with read access to this host's filesystem. The key is a file.
# That limit is stated in safety_audit_reviewer_assignment.json under
# NOT_machine_verified, and it must not be described as more than this.

KEY_BYTES = 32


def load_or_create_key(path: Path) -> bytes:
    """The host-only signing key, created on first use with mode 0600.

    O_EXCL, not `if not path.exists()`: two launchers starting together would
    otherwise both pass the check and the second would overwrite the key the
    first had already signed with, invalidating a receipt nobody edited.
    """
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        key = path.read_bytes()
        if len(key) != KEY_BYTES:
            raise ValueError(
                f"{path.name} is {len(key)} bytes, expected {KEY_BYTES}; "
                "refusing to sign with a truncated key") from None
        return key
    with os.fdopen(fd, "wb") as fh:
        key = secrets.token_bytes(KEY_BYTES)
        fh.write(key)
    return key


def sign(body: dict, key: bytes, *, domain: str) -> str:
    """HMAC-SHA256 over the canonical body, namespaced by `domain`.

    `domain` keeps an isolation receipt from ever validating as some other
    kind of receipt signed with the same key -- the two have different
    meanings and must not be substitutable.
    """
    msg = domain.encode("utf-8") + b"\x00" + canonical_bytes(body)
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def verify(doc: dict, key: bytes, *, domain: str, field: str = "signature") -> bool:
    """True when `doc[field]` is this key's signature over the rest of `doc`."""
    presented = doc.get(field)
    if not isinstance(presented, str):
        return False
    body = {k: v for k, v in doc.items() if k != field}
    return hmac.compare_digest(sign(body, key, domain=domain), presented)
