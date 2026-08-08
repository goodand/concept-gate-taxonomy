# `legacy_leaky` — 재인증에서 제외되는 기존 실측

DESIGN_DECISION_surface_separation.md §8: **기존 결과는 `legacy_leaky`로
보존하고 인증·통계에서 제외한다.** 이 파일이 그 보존 기록이다. 원본 서술은
`PROBLEM_1_sufficient_consistent.md`와 `PROBLEM_2_conflicting.md`에 그대로
남아 있고, 삭제하지 않는다 — 어떤 판단이 왜 내려졌는지가 그 안에 있다.

**용어 규율(§8)**: 새 실행은 기존 실행의 "재채점"도 "정밀 재현"도 아니다.
정확한 동일 prompt가 보존되지 않았으므로 두 숫자는 비교 대상이 아니다.
새 실행은 **clean rerun cohort**다.

## 제외되는 실측

| fixture | 기존 실측 | 원본 | 제외 사유 |
|---|---|---|---|
| E24-F-01 `sufficient_consistent` | **7/7** accept_report | PROBLEM_1 §7.4, §16 | 유출된 v1 payload |
| E24-F-02 `sufficient_repairable` | **5/5** repair | PROBLEM_1 §16 | 유출된 v1 payload |
| E24-F-03 `insufficient` | **5/5** abstain (`c2d0ce5`) | PROBLEM_1 §1 표 | 유출된 v1 payload |
| E24-F-04 `conflicting` | decision 5/5 abstain, verdict 4×insufficient / 1×conflicting | PROBLEM_2 §5.1 | 아래 별도 |

### E24-F-01 / F-02 / F-03 — 유출

세 fixture 모두 v1 `extraction_note`가 모델 payload와 같은 dict에 있었고,
그 안에 기대 판정이 평문으로 들어 있었다. 예: F-03의 `ev4`는
"should classify ... never `direct_support`", F-02의 `ev1`은
"supports `structural_composition`, not `essential_feature`". 즉 이 숫자들은
"모델이 계약을 지켰는가"가 아니라 "모델이 주어진 답을 읽었는가"를 측정한
것일 수 있다. 어느 쪽인지 사후에 분리할 방법이 없으므로 전부 제외한다.

한때 "나머지 3개 fixture는 clean"이라고 보고한 적이 있는데 **거짓이었다**.
grep으로 확인한 결과 네 개 전부 유출돼 있었다(`4a14fdd`에서 철회). 유출
문장 6개는 `test_surface.py`의 `KNOWN_LEAKS`에 positive control로 커밋돼
있다 — 다시 들어오면 테스트가 깨진다.

### E24-F-04 — 유출은 아니지만 여전히 제외

F-04의 N=5(PROBLEM_2 §5.1)는 유출 제거 **후에** 실행됐다. 그런데도 제외하는
이유는 셋이다.

1. **정본 builder를 거치지 않았다.** 손으로 고친 packet으로 돌렸고,
   `rendered_prompt_sha256`이 없다. 모델이 실제로 본 표면이 무엇이었는지
   지금 확정할 수 없다.
2. **계약 문구가 그 이후 바뀌었다.** §5의 5단계 판정 절차와
   `conflicts_with_evidence_ids`는 그 실행 이후에 들어왔다.
3. **fixture 자체가 종결됐다.** 이 저장소의 live·동등강도 evidence로는
   구성 불가로 확정(PROBLEM_2 §5.2). clean rerun cohort에서 제외되고,
   schema의 class는 유지된다.

**다만 §5.1의 관측은 폐기되지 않는다** — 그 실행이 계약 문구의 결함을
찾아냈고, 그 결함이 §5의 5단계 절차로 수정됐다. trial 4는 ev5/ev6를 둘 다
`conflict`로 분류해 `conflicting_evidence`를 냈으면서 같은 응답에서 "neither
provides direct_support"라고 적어 내적 모순을 드러냈다. 새 스키마에서는 이
응답을 **작성할 수 없다**: `conflict`가 admissibility enum에서 사라졌고,
4단계가 충돌을 `direct_support` 후보 사이의 동률로만 정의하며,
`conflicts_with_evidence_ids`가 대칭이어야 한다. 즉 §5.1은 제외되는 *결과*이자
채택된 *진단*이다.

## 인증 상태

재실행 전 **0 class**. 위 표의 어떤 숫자도 인증 근거가 아니다.
clean rerun cohort를 통과한 class만 다시 인증되며, F-04가 종결됐으므로
**최대 유효 커버리지는 3 class**다.
