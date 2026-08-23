# Stage 2 (E2E-v1-C) trial prompt template — DRAFT (동결은 사전등록과 함께)  (V4 — D-E2E-v1-26: implies 1행 추가, 그 외 무변경)

status: **FROZEN** (2026-08-23 동결 커밋 — fixture manifest·profile과 동시).
방언 명세는 프로브 A/B가 실측 검증한 텍스트에 `not` 구성자 1행을 추가한 것
(O1_V1 profile — 양화-부정 scope fixture가 subject에게 부정 표현을 요구하므로,
동결 직전 점검에서 발견·보강. 추가 후 발명 문장 프로브로 재검증).

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
- {"kind": "not", "body": <formula>}
- {"kind": "implies", "left": <formula>, "right": <formula>}
- {"kind": "pred", "name": <string>, "args": [<term>, ...]}
and a term is exactly one of:
- {"kind": "var", "name": <string>}
- {"kind": "entity", "name": <string>}
A quantifier's "var" binds occurrences of that variable name in BOTH its restriction and its body. Predicate arguments must be terms, never formulas. Use lowercase predicate names taken from the sentence's content words. The formula must be closed: every variable occurrence bound by some enclosing quantifier.

OUTPUT: your entire final message must be that one JSON object and nothing else.
```
