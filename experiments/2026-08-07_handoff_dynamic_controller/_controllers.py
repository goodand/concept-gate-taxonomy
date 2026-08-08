#!/usr/bin/env python3
"""Scripted controllers for development smoke, and the deliberately broken ones
the calibration suite needs.

WHAT A SCRIPTED CONTROLLER CAN AND CANNOT SHOW
----------------------------------------------
These are written by the same person who wrote the preregistration's
predictions, so they encode those predictions. Running them measures whether
the HARNESS works end to end -- boundaries hold, guard fires, judge scores,
codes decompose. It measures NOTHING about the research questions, and the
smoke report says so in those words.

The interpretation layer is deliberately a pass-through: the subject reports
what it actually read, verbatim. So term-matching gates reduce to "did it read
the right document", which is precisely the axis the arms differ on and
precisely the axis a scripted controller can honestly exercise. Interpretation
quality needs a live subject and is out of scope here.

STATIC IS RECALL-FIRST, NOT NAIVE
---------------------------------
Arm 1 is "the existing recall-first procedure". Recall-first already includes
pool refill and a graph walk -- that is what took measured recall 0.688 -> 1.000.
If static were a bare search-then-answer it would fail the exploration guard by
construction and every static run would be C1, which would manufacture the
result rather than measure it. So static runs the FULL fixed pipeline every
time; dynamic differs by CHOOSING when to stop and where to go, not by being
the only arm allowed to explore.
"""

from __future__ import annotations

# Signals a document is not the authority. These are visible in the corpus to
# any reader -- no gold is consulted.
NOT_AUTHORITY = ("not a source of authority", "not an authority",
                 "superseded", "proposal. not adopted", "a plan, not a decision",
                 "is not the authority", "wrong handoff.md")


def _claim(reads):
    return [{"claim_id": "c1", "support": [dict(r) for r in reads]}]


def _payload(action, reads, text):
    """Pass-through interpretation: report what was actually read."""
    return {
        "action": action, "answer_text": text, "claims": _claim(reads),
        "current_state": text, "next_action": text, "stop_conditions": [text],
        "uncertainties": [],
    }


class StaticRecallFirst:
    """Fixed recall-first pipeline. Identical steps every case, no adaptation.

    search -> refill -> read the pool -> one graph hop -> read what the hop
    surfaced -> answer. The hop and the post-hop read are what satisfy the
    exploration guard; without them a static arm would be structurally C1 and
    the comparison would be manufactured rather than measured.
    """

    def __init__(self):
        self.step = 0
        self.reads: list[dict] = []
        self.text = ""
        self.pool: list[str] = []
        self.seen: set[str] = set()

    def __call__(self, obs):
        if obs.get("last_result") and isinstance(obs["last_result"], str):
            self.text += "\n" + obs["last_result"]
        self.step += 1
        cands = obs["candidates"]
        if self.step == 1:
            return {"action": "reformulate_query", "query": obs["query"]}
        if self.step == 2:
            return {"action": "expand_candidates"}
        if self.step == 3:
            self.pool = list(cands[:4])
        if self.pool:
            return self._read(self.pool.pop(0))
        if self.step == 7:
            return {"action": "follow_link", "target": cands[0]}
        if self.step == 8:
            target = next((c for c in reversed(cands) if c not in self.seen), cands[-1])
            return self._read(target)
        return _payload("answer", self.reads, self.text)

    def _read(self, target):
        self.seen.add(target)
        rng = {"path": target, "start": 1, "end": 40}
        self.reads.append(rng)
        return {"action": "read_candidate", "target": target, **rng}


class DynamicController:
    """Chooses each action from what it has actually read.

    1. search once;
    2. read the best unread candidate;
    3. if that document disclaims authority (superseded / generated index /
       "a plan, not a decision"), walk its links instead of answering from it;
    4. once something that did NOT disclaim authority has been read, try to
       answer -- and if the guard refuses, do exactly what the refusal named;
    5. abstain only after a reformulation and a graph walk have both happened.

    Step 4 is the whole point of the arm: it stops when it judges the evidence
    sufficient, rather than running a fixed script to the end.
    """

    def __init__(self):
        self.reads: list[dict] = []
        self.text = ""
        self.authority_text = ""
        self.read_paths: set[str] = set()
        self.followed: set[str] = set()
        self.searched = False
        self.pending: str | None = None

    def __call__(self, obs):
        if self.pending and isinstance(obs.get("last_result"), str):
            body = obs["last_result"]
            self.text += "\n" + body
            if not any(s in body.lower() for s in NOT_AUTHORITY):
                self.authority_text += "\n" + body
            self.pending = None

        if not self.searched:
            self.searched = True
            return {"action": "reformulate_query", "query": obs["query"]}

        cands = obs["candidates"]
        reason = obs.get("reject_reason") or ""

        # 4b. obey the refusal, most specific clause first
        if "first search did not surface" in reason:
            target = next((c for c in reversed(cands) if c not in self.read_paths), None)
            if target:
                return self._read(target)
        if "follow_link" in reason:
            target = next((c for c in cands if c not in self.followed), None)
            if target:
                self.followed.add(target)
                return {"action": "follow_link", "target": target}
        if "distinct queries" in reason:
            return {"action": "reformulate_query",
                    "query": obs["query"] + " decision authority"}
        if "read_candidate" in reason:
            target = next((c for c in cands if c not in self.read_paths), None)
            if target:
                return self._read(target)

        # 3. the document disclaimed authority -> walk rather than answer
        if self.text and not self.authority_text:
            target = next((c for c in cands if c not in self.followed), None)
            if target:
                self.followed.add(target)
                return {"action": "follow_link", "target": target}

        # 4a. enough to try
        if self.authority_text:
            return _payload("answer", self.reads, self.authority_text)

        # 2. keep reading
        target = next((c for c in cands if c not in self.read_paths), None)
        if target:
            return self._read(target)
        return _payload("abstain", self.reads, self.text)

    def _read(self, target):
        self.read_paths.add(target)
        self.pending = target
        rng = {"path": target, "start": 1, "end": 40}
        self.reads.append(rng)
        return {"action": "read_candidate", "target": target, **rng}


def make(arm: str):
    return DynamicController() if arm.endswith("DYNAMIC") else StaticRecallFirst()


# --------------------------------------------------------------------------
# broken controllers -- calibration negative controls
# --------------------------------------------------------------------------
class AnswersImmediately:
    """Tries to terminate before exploring. Must be refused, then C1."""
    def __call__(self, obs):
        return _payload("answer", [], "the answer is obviously yes")


class UsesIllegalAction:
    """C2."""
    def __call__(self, obs):
        return {"action": "call_a_friend"}


class CitesWithoutReading:
    """C4 -- cites a candidate it never opened itself.

    It must clear the exploration guard first, or the run stops at C1 and C4 is
    never reached: a negative control that trips a DIFFERENT guard proves
    nothing about the one under test. Measured -- the first version of this
    class kept re-following first-search hits, never satisfied the
    "beyond first search" clause, and reported C1 for three rounds.

    So it reads the MOST RECENTLY discovered candidate (the one a follow_link
    just surfaced, which by construction the first search did not), then cites
    a different path it never opened.
    """

    def __init__(self):
        self.n = 0
        self.read: list[str] = []

    def __call__(self, obs):
        self.n += 1
        cands = obs["candidates"]
        if self.n == 1:
            return {"action": "reformulate_query", "query": obs["query"]}
        if self.n == 2:
            return {"action": "follow_link", "target": cands[0]}
        if self.n == 3:
            target = cands[-1]          # newly surfaced by the follow
            self.read.append(target)
            return {"action": "read_candidate", "path": target, "target": target,
                    "start": 1, "end": 40}
        borrowed = next((c for c in cands if c not in self.read), cands[0])
        return {"action": "answer", "answer_text": "per the retrieval agent",
                "claims": [{"claim_id": "borrowed",
                            "support": [{"path": borrowed, "start": 1, "end": 40}]}],
                "current_state": "per the retrieval agent",
                "next_action": "per the retrieval agent",
                "stop_conditions": ["per the retrieval agent"],
                "recommended_actions": [], "uncertainties": []}


class DeclaresAbsenceEarly:
    """Abstains after a thin search. The guard must refuse; if it somehow got
    through, gold.is_absent=False makes it A1."""
    def __init__(self):
        self.n = 0

    def __call__(self, obs):
        self.n += 1
        if self.n == 1:
            return {"action": "reformulate_query", "query": obs["query"]}
        return {"action": "abstain", "answer_text": "not documented anywhere",
                "claims": [], "current_state": "not documented",
                "next_action": "not documented", "stop_conditions": ["not documented"],
                "uncertainties": ["searched once"]}


def leaky_subagent(corpus, case):
    """C3 -- a retrieval-only component returning a conclusion and a gold key."""
    return {"contract_version": "handoff-dyn-subagent-v1",
            "candidate_paths": ["docs/HANDOFF.md"], "read_ranges": [],
            "search_trace": [], "uncertainty": "none",
            "conclusion": "the answer is docs/HANDOFF.md",
            "critical_paths": ["docs/HANDOFF.md"]}
