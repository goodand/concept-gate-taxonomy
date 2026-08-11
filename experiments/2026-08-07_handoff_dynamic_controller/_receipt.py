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
import json


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
    return hashlib.sha256(
        json.dumps(receipt, sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
