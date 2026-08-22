# PMB 15건 선별 규칙 — DRAFT (비구속, 동결은 사전등록과 함께)

status: DRAFT. D-22 §16이 PMB 몫의 현상 목록을 명령했고(single_quantifier /
quantifier_negation_scope / cardinal / proportional_if_available) 층별
건수는 사전등록 재량이다. 이 초안은 그 건수 제안과 **결정적 선별 절차**를
예고한다. 실행은 fixture 동결 커밋에서만.

## 모집단

Path A OK 671건 (`pmb_eligibility_scan_pathB.json` + adapter 자격 9/9의
그 코드로 재현). 동결 시 Path A/B 재실행 대조가 선행된다(D-21 §15 —
불일치 = FREEZE_BLOCKED).

## 층별 제안 (합 15)

| 층 | 건수 | 술어(기계 판정) |
|---|---|---|
| single_quantifier (보편) | 4 | IR root = forall, `not` 미포함 |
| quantifier_negation_scope | 4 | IR에 not·forall 공존 (양쪽 순서 포함 노력) |
| single_quantifier (존재·평문) | 3 | forall·not 미포함, 지시체 ≥2 |
| cardinal | 3 | Quantity role 또는 quantity.n.* + EQU/APX 수치 |
| proportional | 1 (**if_available**) | "most" 류 — 가용성 동결 시 실측, 0이면 cardinal +1 |

## 결정적 절차 (동결 시 실행)

1. 층 술어로 후보 분류 (adapter 산출 IR 기준 — Path A 코드 경로)
2. 층 내 순서 = sha256(f"{ORDER_SEED}:{doc_id}") 오름차순, 상위 k
3. 선택 항목마다 `.met` 확인 — subcorpus·source 기록, **Tatoeba(CC-BY
   확인됨) 우선**; 비-Tatoeba가 뽑히면 그 subcorpus 라이선스를 동결 전
   확인(회신의 R2 규율)
4. commitment 필드 산출(원문 0바이트): text_sha256·lf_sha256(=en.drs.sbn
   바이트)·adapter_version+code_sha256(자격 기록의 그 해시)·profile hash·
   expected_ir_sha256(=canonical_sha256(adapt_sbn(...)))
5. 사전등록 TBD 해소와 **한 커밋** 동결, Path A/B 대조 기록 동봉

ORDER_SEED: `[TBD-FREEZE-SEED]` — 동결 커밋에서 확정(선별 조작 불가능성의
증거는 seed가 스캔 결과 커밋 **이후** 정해졌다는 이력 자체다).
