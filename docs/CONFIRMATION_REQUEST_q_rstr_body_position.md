# 확인 요청 — `Q_RSTR_BODY`를 provenance가 아니라 **위치**로 정의해도 되는가

- 발신: 2026-08-24, 운영 세션 · 수신: 외부 설계 담당
- 성격: **새 판정 질문이 아니라 D-32 문면의 재해석 확인 1건.** 판정을 뒤집자는
  것이 아니고, 문면대로는 구현 불가인 지점의 대체 정의가 판정 의도에 부합하는지
  묻는다. 구현은 이 정의로 진행하며 확인 후 필요하면 뒤집는다.
- 관련: [[DESIGN_DECISION_restriction_projection|D-32]] §Q32.2 · §B.3

## 1. 판정이 명한 것 (실물 인용)

```yaml
implies_generated_by_forall_desugar:
  preserve_as: Q_RSTR_BODY
implies_source:
  if_no_scope_descendant: collapse
  if_scope_descendant: SCOPE_BRANCH
```
> "여기는 provenance가 필요합니다."

## 2. 문면대로는 구현 불가다 (실측)

desugar가 `FORALL(x,R,B) → FORALL(x,True,implies(R,B))`로 정규화한다. 따라서
아래 둘은 desugar 후 **바이트 동일**하다.

```text
(생성) forall(x, dog(x), bark(x))
(원본) forall(x, True, implies(dog(x), bark(x)))
```

투영에 provenance 정보가 도달하지 않으므로 두 분기를 가를 근거가 없다.

## 3. 태깅 경로의 부작용

desugar가 자기 산출에 표지를 남기면 구별은 가능해진다. 그러나 그 순간
**위 두 형태가 서로 다른 signature를 갖게 된다** — 현재는 동일하다.

그것은 subject가 고른 **인코딩**(제한식 형태 vs implies 형태)을 채점하는 것이고,
D-32가 방금 제거한 교란(비-scope 세부가 scope 능력으로 귀속되는 것)과 **같은
부류**다. 방언은 D-26이 `implies`를 추가한 이후 두 형태를 모두 허용하며,
subject는 어느 쪽이 채점상 유리한지 알 수 없다.

## 4. 제안하는 대체 정의 — 위치

> 제한식이 `True`인 양화의 **직접 body**에 있는 `implies`는 provenance와
> 무관하게 `Q_RSTR_BODY`로 읽는다.

근거: **그 위치의 `implies`는 역할이 RSTR/BODY다.** 원본이 썼든 desugar가
만들었든 의미론적 역할이 같으므로 provenance를 물을 필요가 없다. 결정적이고,
태깅이 불필요하며, §3의 부작용이 발생하지 않는다.

실측: 이 정의로 판정의 qualification 8종을 **8/8 동시 통과**시켰다(방향 보존
test 7 포함). 시제품 기준이며 계약 결박 구현에서 재확인한다.

## 5. 확인을 청하는 것

- (a) 위치 정의가 D-32의 의도에 부합하는가 — 즉 `implies_generated_by_forall_desugar`를
  `implies_in_quantifier_body_position_with_empty_restriction`으로 읽어도 되는가
- (b) 아니라면 태깅 경로를 택하고 §3의 부작용(인코딩 선택이 채점됨)을 감수하는가
- (c) 그 외

운영 세션은 (a)를 구현하고 있으며 **권고하지 않는다** — 재해석은 범위를 넓히는
방향일 수 있고, 그런 제안이 기각된 이력이 있다(D-31 Q31.1). 계약에
`REINTERPRETATION` 상수로 이 사실을 들고 있어 판정이 (b)를 택하면 그 테스트가
뒤집힌다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
