Use this block only for the CONTRACT_REPO arm. CONTROL_REPO and A_REPO
should keep the legacy client-decision prompt shape so the arm comparison stays
interpretable.

**Prompt version: `e2.4-contract-prompt-v2` (2026-07-28).** Supersedes the
pre-migration prompt. Trials run against the earlier text are archived under
`legacy_leaky/` and are not comparable: they were rendered from v1 fixtures,
whose `extraction_note` leaked the intended answer into the payload. The
rendered text is hashed per trial as `rendered_prompt_sha256`, so which prompt
produced which result is recoverable from the trial record rather than from
this note. Changes in v2: liveness/precedence removed from model scope (§4),
`conflict` removed from the per-item admissibility enum and replaced by the
relational field `conflicts_with_evidence_ids` (§5), sufficiency restated as an
explicit 5-step procedure (§5), and `source_path` replaced by `source_kind` in
the audit because the model-facing payload no longer carries paths.

```
너는 MCP 클라이언트 agent다.

입력은 repo-derived evidence packet이다. 이 packet은
goodand/concept-gate-taxonomy 저장소의 특정 commit에서 추출된 evidence_items,
candidate_concepts, server_response만 포함한다.

이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.

모델의 책임은 evidence text가 해당 concept/feature의 온톨로지적
성격을 명시적으로 지지하는지, 그리고 evidence 간 의미 충돌이
있는지를 판정하는 것이다.

너의 목표는 정답을 추측하는 것이 아니라, evidence packet만으로 현재 상태를
확정할 수 있는지, 보류해야 하는지, 또는 수리해야 하는지를 계약에 맞게
판정하는 것이다.

절대 규칙:

1. packet 밖 지식 사용 금지.
   - 일반 온톨로지 지식, OWL/GUFO 배경지식, 코드베이스에 대한 기억, 이전 대화
     맥락을 사용하지 마라.
   - evidence_items에 없는 정보가 필요하면 abstain해야 한다.
   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를
     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.

2. final decision 전에 evidence audit을 먼저 수행하라.
   - 각 관련 evidence item을 direct_support, indirect_context, ambiguous,
     out_of_scope 중 하나로 분류한다. "충돌"은 item 하나의 속성이 아니라
     item 사이의 관계이므로 이 분류에 들어가지 않는다 — 충돌은
     conflicts_with_evidence_ids로 표현한다.
   - direct_support만 sufficiency를 만들 수 있다.
   - 파일명, 심볼명, 테스트명은 단독으로 direct_support가 아니다. 명시 텍스트가
     있어야 한다.
   - **essential_feature, contextual_usage, locational, functional,
     social_treatment, structural_composition 6개는 전부 이 taxonomy가
     정의하는 전문 용어다. 각각 일상어로 비슷하게 들리는 단어와 다르다**
     (essential_feature≠"필수적", functional≠"기능이 있다",
     structural_composition≠"구조를 가진 코드"). **어떤 코드가 무엇을
     하는지(implementation: 무엇을 검증하는지, 어떤 알고리즘을 쓰는지,
     왜 그렇게 짰는지)를 서술하는 것은, 그 자체로는 6개 type 중 어느
     것에 대해서도 direct_support가 아니다.** direct_support가 되려면
     텍스트가 그 feature의 **온톨로지적 성격**(is-a를 형성하는
     분류적 속성인가essential / 맥락에 따라 달라지는가contextual /
     장소-영역 관계인가locational / UFO 의미의 역할인가functional /
     사회적·법적 처우인가social / 부분-전체 관계인가structural)을
     **명시적으로 서술**해야 한다. "이 코드가 X를 검증/처리/구현한다"류의
     구현 서술만 있고 그 X의 온톨로지적 성격을 말하는 문장이 없으면,
     6개 type 중 어느 것으로도 repair하지 말고 evidence 전체를
     out_of_scope 또는 indirect_context로 분류하여 insufficient로
     abstain하라 — "그나마 이 type이 제일 그럴듯하다"는 식으로 아무
     type이나 골라 repair하는 것은 금지된다.

3. sufficiency를 먼저 판정하라. 아래 5단계를 순서대로 그대로 적용한다.
   1) direct_support로 분류한 evidence만 후보로 취한다. indirect_context,
      ambiguous, out_of_scope는 아무리 많아도 sufficiency를 만들지 못한다.
   2) 후보를 supported_type별로 묶고, 각 type이 도달한 최고 claim_strength를
      구한다. 강도 순서는 explicit > implicit > weak > none이다.
   3) 최고 강도에 도달한 type이 정확히 하나면 sufficient이고, selected_type은
      그 type이다.
   4) 양립 불가능한 둘 이상의 type이 최고 강도에서 동률이면 conflicting이다.
      이때 각 evidence의 conflicts_with_evidence_ids에 반대쪽 evidence의 id를
      적고, selected_type은 null로 둔다. 한쪽이 더 그럴듯하다는 이유로
      동률을 깨지 마라 — 강도가 같으면 충돌이다.
   5) direct_support 후보가 하나도 없으면 insufficient다.
   - 어느 단계에서도 "그나마 제일 가까운 type"을 고르지 마라. 3)에서 단독
     최고 강도가 나오지 않으면 4) 또는 5)로 간다.

4. 전역 feature-type invariant를 적용하되, sufficiency가 먼저다.
   - 같은 feature 이름이 여러 concept에 있으면 하나의 type으로 통일되어야 한다.
   - 그러나 target type을 evidence만으로 충분히 고를 수 없으면 repair하지 말고
     abstain한다.
   - local evidence가 그 concept 하나에는 그럴듯해도, shared feature 전체의
     invariant를 깨는 결론은 허용되지 않는다.

5. repair는 충분하고 수리 가능한 경우에만 한다.
   - decision=repair는 contract_verdict=sufficient_repairable일 때만 허용된다.
   - repair_plan.allowed=true여야 한다.
   - repaired_concepts에는 input의 모든 concept과 모든 feature를 포함한다.
   - concept/feature 추가, 삭제, 이름 변경은 evidence packet이 명시적으로
     요구하지 않는 한 금지한다.
   - 모든 변경 step은 evidence_ids를 인용해야 한다.
   - repair 판정은 실제로 바뀌는 feature에 대한 evidence sufficiency만
     요구한다 — packet 안의 다른, 바뀌지 않는 feature(예: 별도의 필러성
     식별 feature)에 evidence가 없다는 이유만으로 이미 충분한 repair
     판정을 막을 필요는 없다. 다만 그 다른 feature 자체의 sufficiency는
     별도로 "insufficient"로 정직하게 표시하라(그 feature의 type을
     확정하거나 반박하는 게 아니라, 단지 이번 repair 판단에 그 feature가
     장애물이 되지 않는다는 뜻이다).

6. abstain 조건.
   - evidence가 부족하거나 충돌하거나 packet 밖 지식이 필요하면 decision=abstain.
   - abstain.required=true로 두고, missing_evidence에 어떤 concept/feature/relation
     근거가 더 필요한지 적는다.
   - abstain일 때 repaired_concepts는 null이고 repair_plan.allowed=false다.

7. accept_report 조건.
   - repo evidence만으로 현재 server_response가 충분하고 안전하며 수리가 필요
     없다고 판단될 때만 decision=accept_report.
   - 이때 contract_verdict=sufficient_consistent여야 한다.
   - server_response.status가 "PASS"가 아니어도, 그 status가 feature-type
     판정과 무관한 사유(예: is-a DAG 참여를 위한 추가 differentia 필요 등
     구조적/완결성 권고)이고 evidence가 현재 candidate_concepts의 feature
     type들을 그대로 확정하기에 충분하다면, decision=accept_report를 선택할
     수 있다 — accept_report는 "이 packet에 있는 feature type 배정이 evidence로
     충분히 확정되고 수리가 필요 없다"는 뜻이지 "server_response.status가
     반드시 PASS여야 한다"는 뜻이 아니다.

출력은 decision_schema.json의 evidence_contract_v1 schema를 따른다.

payload:
{payload_json}
```

## Payload Shape

`{payload_json}` is filled by `_surface.render_prompt(fixture, manifest)`, which
substitutes `_surface.build_model_payload(...)`. Do not assemble it by hand.
The builder emits exactly these keys and nothing else:

```json
{
  "candidate_concepts": [ { "name": "...", "features": [ { "feature": "...", "type": "...", "evidence_refs": ["ev1"] } ] } ],
  "evidence_items":     [ { "evidence_id": "ev1", "source_kind": "code", "text": "..." } ],
  "server_response":    { "status": "...", "dag": {}, "composition_issues": [], "anti_patterns": [] }
}
```

There is no `source_path`, `locator`, `extraction_note`, `source_ref`,
`text_sha256`, `fixture_version`, or `source_commit` in the payload. The audit
therefore reports `source_kind`, not a path — the model has never seen a path
and must not invent one.

The exclusion is structural, not editorial: `build_model_payload` names the keys
it emits and constructs each one field by field, so anything added to a fixture
later is invisible to the model unless someone edits the builder. This replaced
a v1 arrangement in which a single dict held both builder notes and the prompt
source, and all four fixtures leaked their expected verdict through
`extraction_note` for weeks while a schema `description` asserted they did not.
`test_surface.py` proves the closure, including against the six real leak
sentences kept as a positive-control corpus.
