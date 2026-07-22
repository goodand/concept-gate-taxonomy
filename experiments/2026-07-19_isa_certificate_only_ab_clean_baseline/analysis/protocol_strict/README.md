# analysis/protocol_strict/

`runs/preregistered/`로 조립한 공식 `trials.json`에 대해 **동결된**
`evaluate.py`(수정 없음)를 그대로 실행한 출력. `output.txt` 참조.

## 결론

```
EMPIRICAL_TRIAL_SET: provenance contract satisfied
전 cell: invalid 5/5 (markdown 코드펜스로 인한 파싱 실패)
interpretation: INCONCLUSIVE_POSITIVE_CONTROL
```

Provenance 계약(설계 커밋·manifest 해시·실행순서·raw/output 일치)은 전부
통과했다. 그러나 **E2.1의 공식 결과는 출력 운반 형식 불일치로 해석 불가**다
— 30/30 응답이 모델의 실제 판단과 무관하게 markdown 코드펜스 때문에
`INVALID`로 채점됐다.

방향성 신호는 있으나(→ `../exploratory_unfenced/`), 사전등록된
positive-control gate가 실패했으므로 확인적 증거로 채택하지 않는다.
