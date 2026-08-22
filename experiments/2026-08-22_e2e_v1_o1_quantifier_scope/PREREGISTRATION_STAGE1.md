# 사전등록 — E2E-v1 Stage 1 (E2E-v1-M, measurement qualification)

- 작성: 2026-08-22, **control 실행 전** (`stage1_controls.json`의 results가
  빈 채로 같은 커밋에 동결)
- 지배 판정: `docs/DESIGN_DECISION_e2e_v1_experiment_design.md` (D-E2E-v1-19)
- 범위: 판정 §11의 "governance는 estimand에 비례" — 이 문서는 Stage 1의
  측정 계약만 등록한다. H1a의 prompt-policy 감사 기계는 복제하지 않는다

## 1. 이 단계가 주장할 수 있는 것과 없는 것

Stage 1이 성립해도 말할 수 있는 것은 **"E2E measurement path가 성립했다"**
뿐이다. semantic compiler의 능력에 관한 어떤 주장도 하지 않는다
(capability_claim_allowed: false — 판정 원문).

## 2. 계측기와 control

- 계측기: `conceptgate/cg_evaluate.py::evaluate` (canonical structural match,
  어휘 PASS/FAIL/UNSCORABLE/ERROR — Verify의 Verdict와 분리, G32)
- control 8종: `stage1_controls.json` — 기대 분포 PASS 2 / FAIL 2 /
  UNSCORABLE 2 / ERROR 2. 전부 손으로 지은 합성 formula. ERROR는
  프로덕션 파괴가 아니라 evaluator 경계의 비정형 입력.

## 3. 합격 조건 (판정 stage_1.required 그대로)

```
8/8 expected outcome category
∧ oracle 격리 가드 PASS  (Evaluate↛Refine/Verify import — AST 테스트,
                          root test_cg_evaluate.py의 격리 2종)
∧ canonicalization 음성 control PASS  (test_cg_ir.py의 금지 재작성 4종:
                          quantifier 순서·교환법칙·modal scope·de re/de dicto)
∧ 예기치 않은 runtime failure 0
→ measurement_qualification: PASS
```

미달 시: 원인 수리 후 **control 재실행은 허용**(계측 자격이지 표본이
아니다 — 판정 stage_1은 능력 주장을 하지 않으므로 사후 교체 금지 규칙은
Stage 2 fixture에만 적용). 단 control의 **기대값 변경은 새 버전**으로만.

## 4. 결과 기록

`run_stage1_qualification.py`가 H1a `record_calibration` 패턴대로 결과를
같은 json에 기록하고 `qualification_state`를 갱신한다. 결과는 별도 커밋
(방법론 §1: 동결과 결과 분리).

## 5. Stage 2로의 게이트

`qualification_state: PASS`가 아닌 동안 O1 capability cohort(N=20 동결)를
착수하지 않는다. Stage 2의 사전등록은 별도 문서로, 판정 §11 목록
(fixture id+hash·expected IR·model/config·prompt hash·schema·정규화 profile·
평가 규칙·4치 매핑·retry·N=20·acceptance 16/20·direct/certified 지표·
oracle 격리·사후 교체/N증가 금지)을 그때 등록한다.
