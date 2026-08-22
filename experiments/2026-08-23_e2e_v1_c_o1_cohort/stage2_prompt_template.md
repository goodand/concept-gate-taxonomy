# Stage 2 (E2E-v1-C) trial prompt template — DRAFT (동결은 사전등록과 함께)

status: DRAFT. fixture manifest·constructor profile과 같은 커밋에서 동결된다
(D-E2E-v1-21). 이 초안의 방언 명세는 프로브 A/B(PROBE_o1_compiler_20260823.md)
가 실측으로 검증한 그 텍스트다 — 실측 없이 고치지 말 것.

아래 fenced block이 template 정본이다. `{sentence}` 슬롯 하나만 치환된다.
oracle 쪽 어휘(LF, expected, corpus명)는 등장하지 않는다 — 등장 여부는
`_stage2_cohort.py`의 누출 가드가 집행한다.

```template
Compile the meaning of the following English sentence into exactly one formula of the IR dialect specified below, and return it as a single JSON object.

SENTENCE: {sentence}

IR DIALECT (complete specification):
A formula is one JSON object. The allowed node kinds are exactly:
- {"kind": "forall", "var": <string>, "restriction": <formula>, "body": <formula>}
- {"kind": "exists", "var": <string>, "restriction": <formula>, "body": <formula>}
- {"kind": "and", "args": [<formula>, ...]}
- {"kind": "pred", "name": <string>, "args": [<term>, ...]}
and a term is exactly one of:
- {"kind": "var", "name": <string>}
- {"kind": "entity", "name": <string>}
A quantifier's "var" binds occurrences of that variable name in BOTH its restriction and its body. Predicate arguments must be terms, never formulas. Use lowercase predicate names taken from the sentence's content words. The formula must be closed: every variable occurrence bound by some enclosing quantifier.

OUTPUT: your entire final message must be that one JSON object and nothing else.
```
