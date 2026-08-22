# O1 Oracle Adapter 자격 (D-E2E-v1-21 Q21.4 — 7항목)

## 권위와 범위

- 근거 판정: **D-E2E-v1-21 Q21.4** — adapter 자격 5→7 승인, §20이 항목을
  명명("특히 마지막 둘은 aggregate 하나만 검사하지 말고 각 canonical test
  class에 대해 직접 음성 테스트"), §18 — Stage 2 준비상태 =
  Stage1측정PASS ∧ OracleAdapterQualified.
- 자격 대상: `conceptgate/cg_oracle_adapter.py` **그 코드 자체**(소스
  sha256으로 결박). oracle source가 무엇으로 정해지든(D-21 Q21.2 b*: 신규
  sentence-level source 자격 대기) 이 7항목은 그대로 필요하다 — 자격은
  source 무관, 코드 종속.
- **여기서 동결하지 않는 것**: constructor profile hash — D-21 Q21.3이
  fixture manifest와 **함께** 동결하라고 명령했고 manifest는 차단 중이다.
  이 실험은 adapter의 성질만 자격한다.

## 7항목 (D-21 §20 목록 그대로)

| # | item_id | 내용 | 음성 검사 |
|---|---|---|---|
| 1 | syntax_parse | 정식·인라인 형태 파싱 | 괄호 불균형·빈 입력 → AdapterSyntaxError |
| 2 | alpha_rename_invariance | 변수 개명이 canonical hash 불변 | 술어가 다르면 hash 달라짐(불변성이 공허하지 않음) |
| 3 | quantifier_reordering_negative_control | ∀∃ ≠ ∃∀ (BLOCKER 조건) | 항목 자체가 음성 대조 |
| 4 | binding_preservation | shadowing 하 이름 무관 동일 canonical | 같은 표면, 다른 결박 → hash 달라짐 |
| 5 | deterministic_replay | 같은 입력 → 동일 dict | (재실행 결정성은 양방향 게이트의 바이트 동일성이 겸함) |
| 6 | output_schema_validity | 성공 반환은 cg_ir 스키마 유효 | 람다-인자 술어 → AdapterUnsupported (G56/G57의 canonical class) |
| 7 | closed_form_preservation | 닫힌 LF → 자유변수 0 (**38e5d4b 반례 class 포함**: 서로 다른 binder 이름) | 열린 LF는 열린 채 보존(과잉 폐쇄 금지) |

## 규율

- 모든 입력 LF는 **발명 술어**(N-aD:florp / A-aN:quux / B-aN-b{A-aN}:mel /
  N-aD:tikk) — corpus 콘텐츠 0바이트(ORACLE-12). 계약 테스트의
  zorble/glim/prax와도 분리(자격이 계약의 복제가 아님을 이름으로 표시).
- H1a record_calibration 규율: 이 spec은 `results` 비우고 `qualification_
  state` 미설정인 채 **이 커밋에 동결**. 실행기가 기록하고, 결과는 별도
  커밋(방법론 §1: 동결/결과 분리). `test_protocol.py`는 결과 커밋에 추가.
- 실행 기록에 `provenance`(adapter·cg_ir 소스 sha256, python 버전)를 남기고,
  게이트가 **라이브 모듈 해시와 대조**한다 — adapter가 이후 변경되면 이
  자격은 자동 실효(FAIL)되어 재자격을 강제한다(D-21 §18의 기계화).

## 합격 조건

7항목 전 검사 match → `qualification_state: PASS`. 하나라도 어긋나면 FAIL —
부분 점수 없음(D-21 §20 `pass_rule: all_required`).
