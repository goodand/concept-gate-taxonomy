# 독립 리뷰 5차 — D-H1a-12 typed-scope 구현분 (2026-08-06)

- 지위: D-H1a-12 §16 **조건 11**(독립 의미 리뷰)로 실행. 결과 **FREEZE_BLOCKED**.
- 리뷰어: 별도 에이전트 3명, 근거 축 분할(정책 계약 / **렌더된 프롬프트** /
  사전등록·게이트). 세 명 모두 제작 세션 결론 미고지 + "제작자 테스트를 증거로
  받지 말고 직접 재현하라" 지시.
- 이 문서는 **렌더된 프롬프트 축**의 보고다. 나머지 두 축은 실행 중.
- 1차 시도(2026-08-05)는 세 명 전원 API 세션 한도로 조기 종료 —
  `PREREGISTRATION_TYPED_SCOPE_COHORT.md` §8.1 참조.

---

## BLOCKER — §4의 세 번째 문장이 REMOVED arm에서 dangling reference가 된다

판정문 §4가 처방한 공통 세 번째 문장(verbatim, 판정문 line 189-191):

```text
- The restriction on outside domain or ontology knowledge does not itself
  govern evaluation of the supplied evidence items as sources. Source
  evaluation is governed by the arm-specific source-evaluation clause.
```

**REMOVED arm에는 source-evaluation clause가 없다.** Q1절은 KEPT 전용이므로
설계상 당연하다. 제작 세션이 실측으로 확인:

```
PROHIBITION_KEPT:    Q1절 존재=True   "arm-specific...clause" 참조=True
PROHIBITION_REMOVED: Q1절 존재=False  "arm-specific...clause" 참조=True
```

리뷰어가 지적한 두 읽기 모두 처치를 취소한다:

- **(a) 보수적 유보**: "내가 못 본 source evaluation 규칙이 있다 → 하지 말아야
  한다."
- **(b) 불완전 → defer**: "참조된 절이 없다 → 프롬프트가 이걸 해결하라고
  허가하지 않았다 → defer."

**더 나쁜 것**: 이 문장이 §4가 의존하는 기제를 스스로 무너뜨린다. §4는 REMOVED가
작동하는 이유를 "Q1이 없으므로 공통 기본허용 규칙이 적용된다"로 설명한다.
그런데 이 문장은 그 basis에 대해 **더 구체적인** 지배자를 지목한다. specific
beats general 읽기에서 REMOVED의 렌더 텍스트는 "source evaluation은 기본허용
규칙이 지배하지 **않고**, 여기 없는 절이 지배한다"고 말한다. 침묵에 의한 허용이
불가능해진다 — 프롬프트가 침묵을 깨고 다른 것이 지배한다고 말했기 때문이다.

부수: 단어 **"arm-specific"** 자체가 양 arm에 있어, 피험자에게 "이 프롬프트는
조작의 한 arm이고 형제 arm은 다른 source-evaluation 문구를 갖는다"를 공개한다.
arm 간 차이가 아니라 arm-diff 검사가 볼 수 없다.

### 이것이 알려진 재발 패턴이다

`evidence-to-knowledge-promoter`의 2026-08-01 로그가 기록한 D-H1a-11 결함 1번
("A deictic clause lost its referent" — `그 판정`의 선행사가 삭제됨)과 **같은
형태**다. 그때 얻은 처방은 *"절을 옮기면 그 안의 모든 지시 표현이 새 위치에서
무엇을 가리키는지 적어 원래 지시 대상과 비교한다"* 였고, 그 확인은 *"사람의
주의가 아니라 렌더된 출력에 대한 단언이어야 한다"* 였다.

**이번엔 판정문이 처방한 문장 자체가 그 결함을 갖고 있다.** 운영 세션이
§4 문구를 임의로 바꿀 수 없으므로 설계 판정이 필요하다.

---

## MAJOR 4건 (요약 — 전문은 리뷰어 보고)

1. **`source order`가 표적 basis로 읽힌다.** 정책 표는 이걸 비표적(packet 제시
   순서)으로 분류하지만 **렌더된 산문은 그렇게 말하지 않는다.** REMOVED가
   허용해야 하는 과제가 "ev1(doc)과 ev3(code)에 순서를 매겨 하나를 택하는 것"
   이고, 그건 문자 그대로 source를 ordering하는 것이다. `unless the packet
   explicitly authorizes` 탈출구는 packet이 아무 basis도 명시 허가하지 않으므로
   발동하지 않는다.
2. **Evidence-reading rule + §7 두 번째 문장이 결합해 "source 속성은 유효한
   warrant가 아니다"로 읽힌다.** `source_kind`는 item의 *text*가 아니라 형제
   필드인데, "Treat an evidence item as support only when **its text**..."가
   먼저 나오고 §7이 "may affect the decision only through its application to
   **the supplied evidence**"라고 한다. 양 arm 공통이라 arm-diff에 안 걸린다.
3. **§6 defer 규칙은 직접 매핑은 없으나 함의로 살아남는다.** 위 1·2와 결합하면
   REMOVED에서도 판별자가 허용되지 않아 `conflict ⇒ defer`가 양 arm에서
   성립한다.
4. **금지된 4축 중 3개가 렌더 표면에 참조물이 없다.** payload에 날짜·경로·커밋이
   없어 recency·authority는 어느 arm에서도 행사 불가. `source_kind`(doc/code)
   하나만 실재한다. L7(path non-identification)이 인접하지만 같은 주장은 아니다 —
   이건 더 강한 사실이다.

## MINOR 3건

- KEPT의 Q1절이 line 5에 inline 추가되어 **218컬럼**(다른 모든 줄 ≤79). 레이아웃
  자체가 arm 단서가 될 수 있다.
- KEPT만 지시문 본문에서 언어가 전환된다(영어→한국어, "출처의 liveness나"처럼
  영어 차용어 포함). §12/L6은 mention/prohibition coupling만 등재하고
  language-of-instruction은 등재하지 않았다.
- KEPT에서 Q1절이 outside-knowledge 문장 끝에 붙어 있어, 14줄 뒤에 "그 제한은
  source evaluation을 지배하지 않는다"고 말하는 그 문장 **안에** 실제 지배자가
  물리적으로 들어가 있다.

## CONFIRMED-OK

- arm diff가 기계적으로 정확히 Q1절 83바이트 insert 하나뿐(difflib 1 opcode).
- §4 세 문장 전부 양 arm에 byte-identical 존재.
- 정책 슬롯 4개 pair 양 arm 동일. 순서 artifact 없음. 미치환 placeholder 없음.
- 렌더 재현이 쉬움.

---

## 판정

**FREEZE_BLOCKED.** BLOCKER는 판정문 §4의 처방 문구 자체에 있으므로 운영
세션이 고칠 수 없다 — **D-H1a-13 상신이 필요하다.** MAJOR 1·2도 공통 템플릿
문장이라 같은 성격이다(§4·§7 문구 변경 필요).

리뷰어의 마지막 문장이 이 실험의 구조적 사실을 정확히 짚는다: 세 발견 전부
**공통** 템플릿에 있어서 arm-diff 증명과 잔여-금지 tripwire가 **구조적으로
볼 수 없다** — `_h1a_contract.py`의 KNOWN LIMITATION 주석이 예고한 그대로다.
