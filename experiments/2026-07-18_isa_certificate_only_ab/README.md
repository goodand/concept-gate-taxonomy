# isa_certificate_only_ab (E2) — relation.is_a certificate-only 신호 A/B

M1(relation.is_a, 커밋 9ce3544)이 만든 최초의 certificate-only 신호를 검증한다:
status PASS·lint 침묵·anti_patterns 0인데 `obligations.verdict=unknown`. E1(음성)은
"다른 신호가 전부 침묵하고 의무만 미충족인 fixture라야 arm이 갈린다"고 결론냈고,
E2가 그 fixture로 하는 재실험이다.

## 설계 이력 — 적대 리뷰 후 재설계

초안(선장/사람 2-arm)을 컨텍스트 격리 적대 리뷰가 공격해 치명 결함 3개를 찾았고
(전문 아래), 재설계로 수술했다:

1. **신호 번들링 → 신호 분해 3-arm**: 초안 ARM B는 certificate 구조 + 정답을
   불러주는 진단 문장을 함께 담아 "구조의 효과"와 "문장의 효과"를 구분 못 했다.
   → 단일 canonical 응답을 A(무신호)/C(평문 warning)/B(최소 certificate)로 투영.
   진단 문장(reason)은 C·B에 동일, 구조만 다르다. C−A=문장 효과, B−C=구조 효과.
2. **무신호 대조군의 동어반복 → nonce + 양성/음성 대조**: "문제를 말하면 반응한다"는
   자명을 피하려 개념명을 nonce(누멘/베스크)로 바꿔 교과서 회상을 차단하고,
   유효 is-a(음성 대조)·MixRig(양성 대조)를 추가했다.
3. **cert PASS를 semantic truth로 사용 → truth oracle**: 초안 1차 지표(repair율)는
   metadata_laundering(kind로 위장 — 기계 인증 통과·진실 거짓)을 성공으로 셌다.
   → fixture 외부 oracle이 safe_actions를 정의하고, 기계 인증과 진실 보존을
   분리(`mechanically_certified` vs `safe_effective`). laundering은 harm으로 별도 집계.

추가 반영: request_evidence 3번째 선택지(불확실성에 맞는 행동), 입력 스키마
(ontoclean 필드 포함)를 전 arm 동일 제공(affordance 은닉 제거), report 문자열의
신호 언급을 manipulation check로 계측.

## 방법

- **fixture 3종**(`fixture.json`, oracle manifest): nonce_role(role_not_kind,
  certificate-only 신호), nonce_valid_kind(valid_isa, overrepair 음성 대조),
  mixrig_positive(explicit_fail, 민감도 양성 대조). canonical 응답은
  `evaluate.run_and_certify()`로 생성(생산 배선과 동일 조합)해 arm으로 투영.
- **채점**(`evaluate.py`, 결정적): 자기보고 배제. repair는 실제 파이프라인 +
  `results_from_pipeline`+`results_from_isa`+`certify`에 재투입해 판정.
- **trial**: 콜드 Haiku(도구 0). cell당 2~3 replicate(세션 재시작으로 고르지 않음 —
  한계 참조). 계 13 trial.

## 결과

```
집계 (fixture × arm)
mixrig_positive  FULL n=2 | safe_effective 2/2 | unsafe_finalize 0/2 | signal_mentioned 0/2
nonce_role       A    n=2 | safe_effective 2/2 | unsafe_finalize 0/2 | signal_mentioned 0/2
nonce_role       B    n=2 | safe_effective 2/2 | unsafe_finalize 0/2 | signal_mentioned 2/2
nonce_role       C    n=3 | safe_effective 3/3 | unsafe_finalize 0/3 | signal_mentioned 3/3
nonce_valid_kind A    n=2 | safe_effective 2/2 | unsafe_finalize 0/2 | signal_mentioned 0/2
nonce_valid_kind B    n=2 | safe_effective 2/2 | unsafe_finalize 0/2 | signal_mentioned 1/2
laundering 0/13 · overrepair 0/13 전 cell
```

**천장 효과 재현 — 그러나 이번엔 원인이 규명된다.**

- **certificate의 행동 한계 효과 ≈ 0**: nonce_role에서 ARM A(무신호)도 B·C와
  똑같이 safe_effective 100%·unsafe_finalize 0. 잘못된 is-a를 확정 보고한 trial은
  전 arm 0건.
- **그러나 manipulation check가 E1과 다른 해석을 준다**: `signal_mentioned`가
  arm을 깨끗이 가른다 — A는 0/2(언급할 신호 없음), C는 3/3, B는 2/2가 응답의
  신호를 명시 인용한다. 즉 **신호는 읽혔다**. E1의 "읽혔는지조차 모름"과 달리,
  여기선 "읽혔으나 결과를 안 바꿨다"가 확정된다.
- **왜 안 바꿨나 — evidence 텍스트 누출**: nonce로 개념명 사전지식은 막았지만
  evidence 문장("임무가 끝나면 베스크가 아니게 된다")이 anti-rigidity를 평문으로
  노출해, ARM A조차 이것만으로 role임을 알아채고 수리·보류한다. baseline이
  침묵하지 않아 대비가 압축됐다(적대 리뷰 결함 6의 잔존 — 완전 해소 실패).
- **양성/음성 대조는 성립**: mixrig(explicit_fail)는 전 trial repair(민감도 확인 —
  null이 도구 무감도가 아님), valid_kind는 전 trial report_done(overrepair 0 —
  certificate 존재가 유효 간선까지 수리하게 만들지 않음).
- **질적 신호 효과는 있다(safe-rate와 별개)**: 신호가 수리 *방식*을 바꾼다. ARM A는
  feature 강등(edge_removed)으로 기울고, C·B는 reason의 "role/phase" 어휘를 받아
  ontoclean role 부여(role_honest)로 기운다. 안전율은 천장이라 같지만 경로가 다르다.
- **laundering 0/13**: Haiku는 kind 위장으로 인증을 세탁하지 않았다(단 N 작음).

### 판정

- 사전 등록 규칙(실증 주장은 arm 간 ≥3/5 격차)상 **B>A·C>A 행동 효과는 실증되지
  않았다**(격차 0). certificate를 "수리 행동 유발"로 정당화하는 근거는 E2에서도
  나오지 않았다 — E1과 일치.
- 그러나 E2는 E1이 못 한 것을 했다: manipulation check로 **신호가 읽혔음을 확인**하고,
  양성 대조로 **도구 감도를 확인**했다. 따라서 null의 해석이 "신호가 전달 안 됨"이
  아니라 "이 fixture에선 baseline이 이미 천장(evidence 누출)이라 한계 효과가 잴 수
  없음"으로 좁혀진다.
- **certificate의 정당화는 여전히 행동이 아니다** — assurance 감사(결정론 세탁 방지,
  M0에서 코드로 검증됨)와, evidence가 침묵하는 경우의 신호 전달이다. 후자를 재려면
  다음 실험이 필요하다.

## 다음 실험 요구 (E2 후속)

evidence 텍스트에서 임시성 단서를 제거한 fixture라야 baseline이 진짜 침묵해
한계 효과를 잰다. 그런 fixture에서는 결정론 규칙도 role을 못 잡으므로 relation.is_a는
UNKNOWN에 머물고(M1 설계대로), ARM A는 근거가 없어 report_done으로 기울 것이다 —
그때 B·C의 신호가 실제로 갈라놓는지가 진짜 검정이다. 이는 M2(evidence 기반 진실성)
설계와 맞물린다.

## 알려진 한계

- **소표본·불균형**: cell당 2~3 replicate(세션 재시작으로 계획 5에서 축소). 통계
  검정 아님 — 방향성 관측. 격차 0은 표본이 커도 유지될 것으로 보이나 단정 불가.
- **evidence 누출 잔존**: nonce가 개념명 회상은 막았으나 evidence 문장의 임시성
  단서를 남겼다(위 참조). 완전 침묵 baseline은 미달성.
- **ARM B는 생산 응답과 다름**: 신호 분해를 위해 relation.is_a 1건만 담은 최소
  certificate를 썼다(4-pass·길이 교란 제거). 생산 `run_pipeline`은 obligation 전체를
  담으므로, 실제 배포 응답의 효과는 이 결과와 다를 수 있다.
- **Haiku 단일·temperature 미제어**: 생성 파라미터를 제어하지 못했다. 콜드 컨텍스트
  독립 trial이나 T 미기재.
- **1-shot 선언**: 실제 MCP 클라이언트의 재제출 루프가 아니라 단발 JSON 결정을
  측정한다. "수리 의향"이지 "수리 능력"이 아니다.

## 적대 리뷰 전문 (Step 0, 컨텍스트 격리 subagent)

초안 설계를 정당화 없이 공격시킨 결과. 12개 결함 중 1·2·3이 치명(설계 무효화),
나머지는 방법론 개선. 재설계가 반영한 것과 잔존 한계를 위에서 구분했다.

> 요약: 초안에서 B>A는 "경고 문장이 있으면 반응한다"(자명), B=A는 원인 미상, B<A는
> 판정 불능 — 세 결과 모두 표제 질문에 답 못 함. 최소 수술 3: (1) 신호 분해 arm,
> (2) 1차 지표를 honest effective repair로 교체하고 laundering을 harm으로, (3) nonce
> fixture + 양성 대조로 "신호 침묵" 전제와 도구 감도를 실제로 성립.

(결함 1 신호 번들링 / 2 무신호 대조군 동어반복 / 3 laundering을 성공 집계 /
4 정직 수리 affordance 은닉 / 5 간선제거 vandalism 미구분 / 6 fixture 사전지식·
evidence 누출 / 7 양성 대조·manipulation check 부재 / 8 프롬프트 demand
characteristics / 9 최소 certificate 미사용으로 모순·안심 교란 / 10 판정 규칙
미비 / 11 생성 파라미터 미명세 / 12 1-shot이 행동 아님. — 1·2·3·4·5·7·9·10은
재설계 반영, 6·11·12는 잔존 한계로 기록.)

## 재현

```bash
venv/bin/python experiments/2026-07-18_isa_certificate_only_ab/evaluate.py
# fixture/프롬프트 재생성: _gen_prompts.py (canonical→A/C/B 투영 로직 포함)
```

trials.json은 콜드 Haiku 원시 출력 그대로다(무수정). fixture.json은 입력+oracle만
저장하고 canonical 응답은 evaluate가 생성한다(이중 저장 drift 방지).
