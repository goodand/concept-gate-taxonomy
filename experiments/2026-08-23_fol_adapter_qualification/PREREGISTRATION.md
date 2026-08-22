# FOL adapter 자격 (D-E2E-v1-23 §13 — 9항목)

- 근거: D-23 Q23.3 — 1~7은 기존 구조, **8 = FOL definitional lowering
  정확성**(∀(R→B)↔restricted / ∃φ→neutral / restricted∃→desugar 수렴),
  **9 = scope·순서 + 미지원 음성 판별**(∀∃≠∃∀, 무증명 crossing 금지,
  ∨/=/⊕/↔ 거부). §14의 뮤테이션 A·B·C는 계약 테스트로 이미 결박됐고
  (`test_cg_fol_adapter.py`), 이 자격은 그것을 **기록·코드결박** 층으로
  올린다.
- 대상: `conceptgate/cg_fol_adapter.py` + 비교층 `_stage2_canonical_core.py`
  (항목 8의 desugar 수렴이 후자를 경유하므로 둘 다 pin).
- 동결 규율: spec은 results 비운 채 이 커밋에, 실행·결과·게이트는 별도
  커밋. 모든 식은 발명 술어(ORACLE-12).
