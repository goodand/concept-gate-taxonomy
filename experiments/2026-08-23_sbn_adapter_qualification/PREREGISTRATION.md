# SBN adapter 자격 (D-E2E-v1-22 §5-§6 — 9항목)

- 근거: D-22 Q22.2 — wikisem판 7항목(D-21 Q21.4)에 **8: source-정의 보편
  복호, 9: 복호 왕복+음성 판별**을 추가해 9항목. pass_rule: all_required.
- 대상: `conceptgate/cg_sbn_adapter.py` 그 코드(소스 sha256 결박 — 변경 시
  자격 자동 실효, wikisem판과 같은 기제).
- 왕복(9)의 참조 재인코더는 **자격 하네스의 장비**다(runner 내 함수) —
  adapter는 복호 전용을 유지한다(ORACLE-10 분리). 재인코더는 spec의 발명
  형태 class만 다루면 되고, 그 제한도 여기 명시한다.
- 모든 SBN 조각은 발명 synset(zorble/krell/prax/tikk/glim) — corpus
  0바이트(ORACLE-12). 동결 규율: 이 spec은 results 비운 채 이 커밋에 동결,
  실행기가 기록, 결과·test_protocol은 별도 커밋(방법론 §1).

| # | item_id | 음성 |
|---|---|---|
| 1 | syntax_parse | 빈 입력·비정형 synset 거부 |
| 2 | comment_invariance (α-불변의 SBN판: 변수가 위치적이라 개명 축이 주석·공백) | 구조 다르면 hash 다름 |
| 3 | quantifier_reordering_negative_control | ∀(∃ body) ≠ ∃(∀ body) |
| 4 | binding_preservation | role 표적 -1 vs -2가 다른 hash |
| 5 | deterministic_replay | — |
| 6 | output_schema_validity | 미등재 role은 방출이 아니라 거부 |
| 7 | closed_form_preservation | donkey(열림 유발) 거부 |
| 8 | documented_universal_pattern_decode | 단일 NEG→not, 빈-restriction 이중 NEG→not(not) — ∀ 오인 금지 |
| 9 | decode_reencode_round_trip_and_negative_controls | 왕복 fp 동일 + 무관 NOT/EXISTS 패턴 비복호 |
