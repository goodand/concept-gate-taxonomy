#!/usr/bin/env python3
"""PMB 5.1.0 en-gold의 O1 적격성 사전 스캔 — Path B (adapter 독립 스캐너).

D-E2E-v1-21 §15의 2경로 dual-check 중 독립 경로. Path A(adapter 능력 스캔)는
SBN adapter가 판정(Q22) 후에 생기므로 freeze 시점에 재실행해 이 결과와
대조한다 — 불일치는 FREEZE_BLOCKED.

입력: 로컬 캐시의 PMB en/gold 전개본 (repo 밖 — D-20 §Q20.4).
출력: 집계 counts + 후보 문서 ID 목록(corpus 텍스트 0바이트 — ID·해시만).

분류 규칙(전부 이 파일이 정본):
- BOX_OPS: SBN의 box/담화 연산자. 비교·시제 role 연산자(EQU/TPR/APX…)와
  구별한다 — 후자는 문장 내부 구조라 배제 사유가 아니다(첫 census가 이 둘을
  합쳐 오판했던 실측이 이 구별의 근거).
- 후보 = 양화 한정사 보유 ∧ box-op ⊆ {NEGATION} ∧ 내부 문장 경계 없음
  ∧ 전 층위 gold. 담화 연산자 필터가 다문장 문제를 흡수한다(다문장은
  SDRT 담화 연산자를 동반 — wikisem의 InAnaphorSet과 같은 지위).
- NEGATION 개수 census: 2(짝) = ¬∃¬ 보편양화 인코딩(Bos, variable-free DRS
  §4 — 정본이 명시한 인코딩), 1 = 단순 부정, 3 = 부정된 보편.
"""
from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
from pathlib import Path

BOX_OPS = frozenset({
    "NEGATION", "POSSIBILITY", "NECESSITY", "ATTRIBUTION", "CONDITION",
    "CONSEQUENCE", "ALTERNATION", "CONTINUATION", "CONTRAST", "EXPLANATION",
    "NARRATION", "COMMENTARY", "RESULT", "SOURCE", "PRECONDITION",
    "CONJUNCTION", "ANA"})
DET = re.compile(r"\b(every|each|all|everyone|everybody|everything|no one|"
                 r"nobody|nothing|none|most|both|some|any|anyone|anything|"
                 r"few|many|several)\b", re.I)
UNIV = re.compile(r"\b(every|each|all|everyone|everybody|everything)\b", re.I)


def box_ops_of(sbn: str) -> frozenset:
    ops = set()
    for line in sbn.splitlines():
        if line.startswith("%%%"):
            continue
        for tok in line.split("%", 1)[0].split():
            if tok in BOX_OPS:
                ops.add(tok)
    return frozenset(ops)


def scan(gold_root: Path) -> dict:
    docs = sorted(gold_root.glob("p*/d*"))
    out = {"population_doc_dirs": len(docs), "counts": {}, "candidates": []}
    det_n = univ_n = 0
    neg_hist = collections.Counter()
    sub_census = collections.Counter()
    for d in docs:
        raw = (d / "en.raw").read_text(encoding="utf-8", errors="replace").strip()
        if not DET.search(raw):
            continue
        det_n += 1
        ops = box_ops_of((d / "en.drs.sbn").read_text(encoding="utf-8",
                                                      errors="replace"))
        if not ops <= {"NEGATION"}:
            continue
        if re.search(r"[.!?]\s+[A-Z]", raw):      # 내부 문장 경계
            continue
        status = dict(l.split("\t") for l in
                      (d / "en.status").read_text().splitlines() if "\t" in l)
        if any(v != "gold" for v in status.values()):
            continue
        met = (d / "en.met").read_text(encoding="utf-8", errors="replace")
        m = re.search(r"subcorpus:\s*(.+)", met)
        sub = m.group(1).strip() if m else "?"
        sub_census[sub] += 1
        sbn_txt = (d / "en.drs.sbn").read_text(encoding="utf-8",
                                               errors="replace")
        negs = sum(1 for l in sbn_txt.splitlines()
                   if not l.startswith("%%%")
                   and "NEGATION" in l.split("%", 1)[0].split())
        neg_hist[negs] += 1
        if UNIV.search(raw):
            univ_n += 1
        out["candidates"].append({
            "doc": str(d.relative_to(gold_root)),
            "subcorpus": sub,
            "negation_lines": negs,
            "universal_lexicon": bool(UNIV.search(raw)),
            "text_sha256": hashlib.sha256(raw.encode()).hexdigest(),
            "sbn_sha256": hashlib.sha256(sbn_txt.encode()).hexdigest(),
        })
    out["counts"] = {
        "determiner_bearing": det_n,
        "eligible_candidates": len(out["candidates"]),
        "universal_lexicon": univ_n,
        "negation_line_histogram": dict(sorted(neg_hist.items())),
        "subcorpus": dict(sub_census.most_common()),
    }
    return out


if __name__ == "__main__":
    root = Path(sys.argv[1])
    result = scan(root)
    print(json.dumps(result["counts"], ensure_ascii=False, indent=2))
    outp = Path(__file__).parent / "pmb_eligibility_scan_pathB.json"
    outp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print(f"written: {outp.name}, {len(result['candidates'])} candidates")
