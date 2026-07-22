# runs/prompt_override/

**DEVIATION COHORT — 동결된 실행 조건과 다름.** `runs/preregistered/`가 30/30
markdown 코드펜스로 감싸진 것을 발견한 뒤, `--append-system-prompt`로
"코드펜스 없이 순수 JSON만 출력하라"는 지시를 추가해 동일한 30개 프롬프트를
재수집한 것이다. 프롬프트 원문(`prompt_sha256`)은 변경되지 않았지만, 실행
조건(system prompt)이 preregistered 조건과 다르므로 **이 코호트를 공식
E2.1 protocol-strict trial로 합치지 않는다.**

결과: 지시에도 불구하고 30/30 여전히 코드펜스 — 개입이 효과가 없었음을
확인. `analysis/exploratory_unfenced/`에서 preregistered 코호트와 나란히
비교했고, 두 코호트의 cell별 decision 분포가 완전히 동일함을 확인했다(재현
신호로는 유용하나 공식 결과는 아님).

파일 구성은 `runs/preregistered/README.md`와 동일. `trials.json`(이 코호트
전용, 저장소 루트의 공식 `trials.json`과 별개)도 이 폴더 안에 둔다.
