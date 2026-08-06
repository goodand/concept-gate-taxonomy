# Red team — `handoff_repair_loop.py` 적대적 리뷰 결과

- 실행: 2026-08-06, subagent(적대적 리뷰어) 1명
- 발주 이유: 사용자 지시 "subagent or workflows로 test 하는 것도 가능하지?"
- 대상: `scripts/handoff_repair_loop.py` (커밋 `e9cea54`)
- 결과: **전 가드 우회. PASS 도달 경로 3개.**

발주 시 남긴 말 그대로다 — "뚫리면 그게 이 테스트의 성과다." 뚫렸다.

## 1. 가장 무거운 발견 — 문서가 구현을 앞질렀다

docstring이 가드 5개(G1–G5)를 선언했는데 **구현은 3개뿐**이었다. 직접 확인:

```
94:def tracked_file_count() -> int:     # 정의만 있고 호출 0회 → G4 부재
1                                        # 파일 전체 while 1개, 그것도 reachable_from
                                         # → main()은 단발, 루프 없음 → G5 부재
129: link_lines = [line for line in added if _LINK_LINE.search(line)]
130: if len(link_lines) > max_links:     # 링크가 아니라 링크 '줄'을 셈
```

**이 저장소가 이 세션 내내 10건 기록한 P1 패턴(주장하는 명제 ≠ 필요한 명제)을,
그 패턴을 잡으려고 만든 도구 안에서, 내가 저질렀다.** 게다가 커밋된 상태라
도구가 자기 문서로 거짓을 말하고 있었다.

## 2. PASS 도달 경로 3개

### 경로 A — 입력 집합을 좁힌다 (수선 0줄)

1. 유일한 orphan을 `.gitignore`에 추가 → 감사 입력에서 사라짐
2. dangling link를 산문으로 고쳐 씀 → dangling finding 소멸

**실측: 도달 파일 수 135 → 135로 불변인데 지표는 9 → 0.** 구조는 하나도
나아지지 않았고 계측기가 못 보는 곳으로 옮겼을 뿐이다. 이건 Phase D의
`metric-only improvement`보다 나쁜 상태이며 별도 이름이 필요하다.

### 경로 B — 바이트코드 캐시 오염 (마크다운 편집 0건)

`py_compile`로 패치한 `audit()`를 **hash-based UNCHECKED `.pyc`**로 만들고
소스 바이트를 원상 복원. 결과:

- G1 핀 해시가 **완전히 일치** (소스는 진짜 원본이므로)
- `git status` 깨끗 (`__pycache__/`가 gitignore 대상)
- 실행되는 것은 패치된 바이트코드

**G1은 소스를 핀하는데 CPython은 바이트코드를 실행한다.** `python3 -B`는
방어가 아니다 — 쓰기만 막고 읽기는 막지 않는다.

### 경로 C — 링크를 mention으로 변환

auditor는 backtick mention을 **의도적으로** dangling으로 보고하지 않는다
(404 false positive를 고친 그 결정). 그래서 깨진 `[x](gone.md)`를
`` `gone.md` ``로 바꾸면 finding이 사라진다. **정밀도를 위해 내린 옳은 결정이
게임 경로를 만들었다** — 두 요구가 실제로 충돌하는 지점이다.

## 3. 나머지 구멍

| # | 구멍 | 성격 |
|---|---|---|
| 4 | G2가 링크 줄을 셈 → 한 줄에 12개 링크 = 1로 계산 | 계수 오류 |
| 5 | untracked `.md`는 `git diff`에 안 나옴 → 새 파일이 무검사 덤프장 | 범위 누락 |
| 6 | `git update-index --skip-worktree` 한 번으로 편집이 diff에서 사라짐. auditor는 디스크에서 계속 읽음 | 가드 실명 |
| 7 | 0바이트 stub 파일을 만들면 dangling이 해소됨 | 존재 ≠ 내용 |
| 8 | dump_ratio가 `>` 라서 정확히 0.5는 통과 | 경계 오류 |

## 4. 판정 — 가드를 더 쓰는 것으로는 못 푼다

경로 B는 원리적으로 in-process 가드가 막을 수 없다. 채점기를 **import**하는 한,
채점기를 실행하는 프로세스가 이미 오염돼 있을 수 있다. 막으려면 clean
subprocess(`-B -E -P -I`, 캐시 제거/리다이렉트)에서 돌려야 하고, 그건 가드가
아니라 아키텍처다.

`.vault-harness`의 `HANDOFF_REUSE_HARNESS_PREREGISTRATION.md`(같은 날 저녁
작성)가 정확히 그 결론에 도달해 있다 — J1 최소 조건에 "judge는 agent workspace의
Python import cache와 executable을 신뢰하지 않는다", "`.gitignore`, index flags,
symlink, bytecode cache가 바뀌어도 judge input set은 고정 manifest에서 계산한다"가
들어 있고 §1.1이 이 red team 결과를 근거로 인용한다. **내 결함이 그쪽 설계
입력이 됐다.**

## 5. 이 세션에서 한 대응 (커밋 안 함, 작업 트리에만 있음)

`scripts/handoff_repair_loop.py`:

- docstring의 거짓 주장 정정 — G4/G5가 미구현이었다는 사실을 본문에 명시
- **경로 B를 `KNOWN UNCLOSED BYPASS` 절로 공개** — 안 고쳤으므로 고쳤다고
  쓰지 않는다. "green run은 문서에 대한 증거이지 채점기가 조작되지 않았다는
  증거가 아니다"라고 적었다
- G4 실구현: `assert_input_not_narrowed()` — tracked 수 감소 / 감사 입력 집합
  이탈 / skip-worktree 설정을 각각 위반으로 보고. `--emit-pins`가 해시뿐 아니라
  베이스라인 스냅샷도 함께 내도록 변경(한쪽만 잊는 것을 불가능하게)
- G5 실구현: `--require-progress PREV`
- G2: 링크 줄이 아니라 **링크 개수**를 셈, 비율은 `>=`
- untracked `.md`도 검사 대상에 포함(diff가 없으므로 전문을 added로 취급)
- `.gitignore`를 핀 대상에 추가

`test_handoff_repair_loop.py` 신규 — 전부 **공격을 재현하는 음성 테스트**.

## 6. 대응 도중 같은 결함을 한 번 더 저질렀다 (P1 11번째)

G4/G5 구현 후 뮤테이션으로 음성 테스트의 실효성을 검증했다:

| 뮤테이션 | 기대 | 실제 |
|---|---|---|
| G4 호출부 삭제 (= 원래 결함 재현) | 실패 | **통과** ← 공허 |
| G5 플래그를 안 읽게 | 실패 | 실패 ✓ |
| G2를 줄 세기로 되돌림 | 실패 | 실패 ✓ |
| 미공개 우회 문단 삭제 | 실패 | 실패 ✓ |

원인: 메타 테스트가 함수 **이름의 존재**만 검사해서 `def` 한 줄이 조건을
만족시켰다. **"정의됐지만 호출되지 않음"을 잡으려고 쓴 테스트가 정확히 그
구분을 못 하는 검사를 썼다.**

수정: `ast.walk`로 `ast.Call` 노드를 요구하도록 교체하고 테스트 docstring에
이 사고 자체를 기록. **교체 후 재뮤테이션 검증은 사용자 중단으로 미실행** —
따라서 현재 이 메타 테스트가 실효적이라는 주장은 **미검증**이다.

## 7. 남은 것

- [ ] 메타 테스트 AST 교체본의 뮤테이션 재검증 (위 §6 — 미실행)
- [ ] 경로 B: clean subprocess 채점으로 전환 (아키텍처 변경, 미착수)
- [ ] 경로 C: mention 채널에 G2/G3를 적용할지, mention을 도달성 계산에서 뺄지
      — 정밀도와 게임 방지가 충돌하므로 **판정이 필요한 설계 문제**
- [ ] 구멍 7(0바이트 stub): dangling 해소 시 대상 파일 크기 하한 요구
- [ ] 위 작업 트리 변경 전부 **커밋 안 됨** (커밋 승인 대기)
