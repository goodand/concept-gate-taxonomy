# 활성 실험 디렉토리 정리 — 조사 결과 및 정정

- 작성: 2026-08-01 (초안) / **전면 정정: 2026-08-01** / **범위 재정정:
  2026-08-02** (§0.1 — 첫 정정 자체가 원본 결정을 과잉 일반화했다)
- 문서 종류: **설계 문서**(`WORKSPACE_NAVIGATION.md` §2)
- 계기: vault 정리 agent가 활성 실험 폴더만 정리하지 못한 것으로 보여
  "정리 설계"를 요청받았다.

---

## 0. 결론 — "이동 금지"가 아니라 "검증 없는 이동 금지"다

**활성 실험 폴더 재배치는 무조건 금지가 아니다.** 검증 조건을 충족하는
`git mv`는 허용된다. 아래 §0.1이 왜 이 문서의 첫 정정본이 틀렸는지 보인다.

### 0.1 두 번째 정정 (2026-08-02) — 첫 정정의 과잉 일반화

첫 정정(2026-08-01)은 `notes/audits/vault/symlink-vs-moc-2026-07-30.md`의
"Adopted hybrid" 1항 한 줄만 보고 "활성 실험 폴더 내 어떤 `git mv`도 금지"로
읽었다:

> 1. Keep repository and active experiment paths unchanged.

**그 문서를 처음부터 끝까지 다시 읽으면(2026-08-02), 이 1항이 실제로
막는 것은 훨씬 좁다.** 근거로 인용됐던 문장의 **전체 문맥**:

> Format-first canonical storage remains useful for newly ingested,
> vault-owned artifacts. **It is unsafe to impose physically on tracked
> repositories or active worktrees** because moving files can break imports,
> relative links, fixture locators, hashes, and Git provenance.

"format-first canonical storage"는 그 문서 §"Correction"이 평가한 **특정
대안 아키텍처**(`files/<format>/` 정본 저장 + 여러 분류 트리로의 relative
symlink 투영)를 가리키는 고유명사다 — 일반적인 `git mv` 재배치가 아니다.
문서가 실제로 우려한 건 **symlink 기반 뷰가 `rg` 기본 동작에 보이지 않고
Obsidian backlink를 만들지 않는다는 것**(§"READ"·"Analysis")이지, "파일을
하위 디렉토리로 옮기면 안 된다"는 일반 명제가 아니다.

**그리고 나열된 위험(imports·relative links·fixture locators·hashes·Git
provenance 파손)은 전부 구체적으로 검증 가능한 항목이다** — "이동하면 안
된다"의 근거가 아니라 "**이동 후 이것들을 확인하라**"는 체크리스트로 읽는
것이 원문에 더 충실하다.

**정정된 원칙**: 일반 `git mv` 재배치는 아래를 검증하면 허용된다.

1. 이동 대상을 로드하는 활성 코드 경로가 없다(grep + 실제 테스트 실행)
2. 내용이 바이트 동일하다(`git show --stat`에 `R100`만, 내용 diff 0)
3. `git mv`를 사용해 Git provenance(`--follow` 이력)를 보존한다
4. prose 안의 상대 경로 참조를 갱신한다(README·PREREGISTRATION 등)

**금지되는 것은 여전히 있다**: "format-first storage + symlink facet"
패턴 자체를 이 저장소에 이식하는 것(symlink가 backlink·`rg` 기본 검색에서
사라지는 정확한 그 문제 때문), 그리고 검증 없이 옮기는 것.

같은 문서 6항도 이 읽기를 뒷받침한다 — 이동 자체가 아니라 **권위의 소재**를
말하고 있다:

> 6. Treat neither MOCs nor symlinks as authority; resolve to the canonical
>    path before answering or editing.

**이 정정이 소급 적용하는 것**: `_h1a_diag*` 4파일을 `superseded/`로
옮긴 것(2026-08-02, Q6=A 은퇴 집행)은 위 4개 조건을 이미 충족한 상태로
실행됐다 — `git mv` 사용, 내용 바이트 동일, 이동 후 어떤 활성 `.py`도
그 경로를 로드하지 않음(전체 게이트 재통과로 확인), `WHY.md`로 이동 사유
기록. **되돌릴 필요가 없다.**

---

## 1. 이 문서의 초안이 틀렸던 지점 (기록 보존)

초안은 활성 실험 폴더 안에 `correspondence/`와 `superseded/`를 만들어
`git mv`하자고 제안했다. **채택된 결정 1항과 정면으로 충돌한다.**

| 초안 제안 | 실제 |
|---|---|
| `correspondence/`로 `DESIGN_REQUEST*` 이동 | ⚠️ **2026-08-01 정정 당시엔 ❌였으나 §0.1(2026-08-02)이 그 자체를 뒤집었다.** 검증 4조건(§0.1)을 충족하면 허용 — MOC wikilink는 이동 후 재생성으로 갱신(§3.2). 첫 정정이 "이동은 전부 금지"라고 과잉 일반화한 것이 이 행의 원래 오류였다 |
| `superseded/`로 `_h1a_diag*` 이동 | ⚠️ 같은 재정정. **이미 실행되고 검증까지 끝났다**(§0.1 마지막 문단). supersession 표시는 `by-status/` facet **또는** 검증된 `git mv` 둘 다 가능 — 배타적이지 않다 |
| `docs/EXTERNAL_RULINGS.md` 원장 신설 | ❌ 여전히 불필요. 미러의 `canonical:` frontmatter가 파일 단위로 같은 정보를 기계가독 형태로 이미 담는다 |
| "사본 2개는 drift 위험 → inbox를 비운다"(P-4) | ❌ 여전히 틀림. 미러 + `canonical:` 포인터가 **의도된 패턴**이다. 실측 드리프트 309~338바이트는 전부 frontmatter이고, load-bearing인 template fence는 **바이트 동일** |
| 코드 분류 체계가 없다 | ❌ 여전히 불필요. `by-code/` facet이 이미 존재: `active-protected` / `reuse-now` / `extract-later` / `historical-prototypes` / `provenance-snapshots` |

**이 표 자체가 교훈이다**: 첫 두 행은 2026-08-01엔 맞다고 확신했다가
2026-08-02에 뒤집혔다. 나머지 세 행은 두 번째 재검토에서도 그대로 유지된다
— "이전에 틀렸던 문서"라고 해서 **전부** 다시 뒤집히는 것은 아니다. 매
항목을 원본 근거에 개별적으로 다시 대조해야 한다(이번엔 실제로 그렇게
했다 — §0.1 전체가 원본 문서 재독의 결과다).

**왜 놓쳤나 — 검색 방법의 문제였다.** 초안 조사는 `rg`/`find`/`grep`으로
**파일명**만 훑었다(`DESIGN_DECISION`, `canonical`). 위 감사 문서는 제목이
"Format storage, symlink views, and MOC validation"이라 그 키워드에 걸리지
않는다. **backlink 한 번**으로 나왔다:

```
obsidian backlinks path="notes/00-moc/by-topic/vault-architecture.md"
→ notes/audits/vault/symlink-vs-moc-2026-07-30.md
```

사용자가 제공한 검증된 retrieval workflow(초기 검색 Recall 0.688 →
graph walk 후 1.000)가 정확히 이 격차를 예측한다. **lexical 검색만으로는
"이미 결정돼 있는가"를 답할 수 없다.**

---

## 2. 초안 조사에서 살아남는 것 — 채택된 결정을 **뒷받침하는 실측**

초안의 제안은 틀렸지만 제약 분석은 유효하고, 감사 문서가 추상적으로 말한
"moving files can break imports, relative links, fixture locators, hashes"의
**구체적 실측**이 된다.

| 제약 | 실측 |
|---|---|
| **평면 디렉토리 가정** | 모든 모듈이 형제를 `HERE / "이름"`으로 해석. **25개 호출 지점** |
| **판정문 하나가 코드 입력** | `_h1a_contract.py:56`이 `DESIGN_DECISION_H1a_prompt_surface.md`의 fenced block을 프롬프트 template으로 로드. 형제 판정문들은 순수 기록인데 **이름·위치로 구분 불가** |
| **동결 규율** | `DESIGN_FILES`가 `HERE.relative_to(REPO_ROOT)`로 만들어져 폴더 이동이 동결 게이트에 영향 |
| **MOC 링크 결합** | worktree 내부를 가리키는 MOC wikilink **264건**(H1a 폴더로 17건) |

`_h1a_contract.py:56`은 특히 기록해 둘 가치가 있다 — **판정문이 문서가
아니라 실행 입력인 사례**이고, 감사 문서의 "fixture locators"가 실제로
어떤 모습인지 보여준다.

---

## 3. 그렇다면 실제로 남은 작업

정리가 아니라 **vault 계층 유지보수**다. 셋뿐이다.

### 3.1 inbox 처리 (vault 측)

`notes/` **루트**의 `DESIGN_DECISION_H1A_REVIEW_BLOCKERS.md`가 아직 정리
agent를 안 거쳤다 — frontmatter 없음, `projects/concept-gate/experiments/h1a/`
밑도 아님. 기존 미러들과 같은 형태로 처리하면 된다:

```yaml
type: decision
status: active
source: notes
experiment: h1a
canonical: "[[concept-gate-e2.2-wt/.../DESIGN_DECISION_H1a_review_blockers]]"
tags: [doc/decision, source/notes, experiment/h1a, …]
```

**주의**: `canonical:`이 가리킬 repo 파일이 아직 없다. 판정문을 repo에
들이는 것이 선행한다(정본 이름은 폴더명을 따라 `h1a` 소문자).

### 3.2 신규 파일 반영 후 MOC 재생성

이번 작업으로 repo에 새 파일이 여럿 생겼다(`_h1a_contract.py`,
`_h1a_diag*.py`, 판정문·요청서 4건, 리뷰 2건 등). 생성기가 있다:

```bash
python3 .vault-harness/vault-md-retrieval/generate_vault_mocs.py
```

**커밋 이후에 돌린다** — 커밋 전 상태를 인덱싱하면 MOC가 실재하지 않는
중간 상태를 가리킨다.

### 3.3 supersession — facet **과** 검증된 이동, 둘 다 쓴다

**2026-08-02 갱신(§0.1)**: 아래는 "파일을 옮기지 않고"를 원칙으로 썼던
첫 정정본의 문구다. §0.1이 밝혔듯 그 원칙 자체가 원본 결정의 과잉
일반화였다. `_h1a_diag*` 4파일은 이미 §0.1의 검증 4조건을 충족하며
`superseded/`로 이동됐다 — vault facet 표시와 파일시스템 이동은
**양자택일이 아니라 병행**한다.

Q6=A가 `_h1a_diag*`를 은퇴시켰을 때 실제로 한 일:

- `.py` 4개 + `h1a-decider.md`를 `git mv`로 `superseded/`에 이동,
  `superseded/WHY.md`에 은퇴 사유·대체물 기록(§0.1 조건 1·2·3 충족)
- `PREREGISTRATION.md` §11에 이력 텍스트로 표시(조건 4 — prose 참조 갱신)
- **삭제하지 않았다.** `_h1a_diag_score.py`의 §11.2 채점 논리는 후속
  설계가 앵커를 재도입하면 다시 필요하다
- vault 측에서는 이 이동을 `by-code/historical-prototypes` facet으로,
  `.md` 미러는 `status:`를 `finished`/`legacy`로 표시해 병행 반영한다
  (아직 미실행 — §3.2의 MOC 재생성과 함께 처리)

---

## 4. 정리 agent 위임 범위 (수정)

| 대상 | 위임 | 근거 |
|---|---|---|
| `notes/` inbox 처리·frontmatter 부여 | ✅ | vault 소유 아티팩트. 채택된 결정 2·3항 |
| MOC 재생성 | ✅ | 생성 아티팩트. 결정 3항 |
| `experiments/**/__pycache__` | ✅ | gitignore 대상, 재생성됨 |
| **활성 실험 폴더 내 `git mv`** | ✅ (조건부) | **§0.1(2026-08-02) 재정정.** §0.1의 검증 4조건(코드 로드 없음·바이트 동일·`git mv`·prose 갱신)을 충족하면 허용. 조건 미충족 시에만 ❌ |
| format-first storage + symlink facet 패턴 이식 | ❌ | 결정 1항이 실제로 막는 것은 이것뿐(§0.1) — symlink가 backlink·`rg` 기본 검색에서 사라지는 문제 |
| `archive/worktrees/` | ❌ | 워크스페이스 규칙상 read-only 역사 증거 |

---

## 5. 이 조사가 남긴 방법론 교훈

**"이미 결정돼 있는가"는 lexical 검색으로 답할 수 없다.** 결정 문서의 제목이
질문의 어휘를 포함하지 않을 수 있기 때문이다. 이번 사례에서 감사 문서 제목은
"Format storage, symlink views, and MOC validation"이었고, 내 질문의 어휘는
"디렉토리 정리 / 파일 배치"였다. 교집합이 0이다.

**절차**: 설계를 쓰기 전에 관련 topic MOC를 찾아 **backlink를 한 번 따라간다.**
비용은 명령 2개, 이번에 막은 것은 채택된 결정과 정면 충돌하는 설계 문서다.

이것은 `adversarial-verification-probe` 패턴 10(가드가 주장하는 명제를
읽어라)의 검색판이다 — **"검색이 조용하다"는 "없다"가 아니라 "이 어휘로는
못 찾았다"이다.**

**두 번째 교훈(2026-08-02, §0.1): 찾아낸 문서를 발췌 인용해도 틀릴 수
있다.** 첫 정정은 backlink로 원본 문서를 정확히 찾아냈다 — 검색은
성공했다. 그런데도 그 문서의 **핵심 근거 문장 한 줄**("It is unsafe to
impose physically...")을 앞뒤 문맥("Format-first canonical storage") 없이
읽어 범위를 넓게 잘못 해석했다. 문서를 찾는 것과 그 문서의 **주장 범위를
정확히 읽는 것**은 별개의 실패 지점이다 — 전자를 고쳤다고 후자가 저절로
맞는 게 아니다. 인용할 땐 그 문장이 무엇의 정의/명명인지(여기선
"format-first canonical storage"라는 고유명사)까지 확인해야 한다.

---

## 6. 검증

```bash
# 채택된 결정 원문 확인 — "format-first canonical storage"가 어떤 아키텍처를
# 가리키는지 문맥 전체를 읽을 것 (§0.1의 실패는 이 문맥을 생략한 것이었다)
obsidian read path="notes/audits/vault/symlink-vs-moc-2026-07-30.md"

# 활성 실험 폴더에서 git mv를 실행했다면, §0.1의 검증 4조건을 확인
git -C ../.. show --stat <commit>              # R100(rename)만, 내용 diff 0
grep -rn "<옮긴 파일명>" --include="*.py" .    # 활성 코드가 그 경로를 로드하지 않음
python3 ../scripts/run_gates.py                 # 이동 후에도 게이트 전부 통과

# inbox 처리 여부
ls ../notes/DESIGN_DECISION*.md 2>/dev/null && echo 'inbox 미처리' || echo 'inbox clean'

# MOC가 최신인지 (커밋 후)
python3 ../.vault-harness/vault-md-retrieval/generate_vault_mocs.py
```

## 7. 범위 밖

- format-first storage + symlink facet 패턴을 이 저장소에 이식하는 것 —
  **채택된 결정이 금지**(§0.1). 검증된 `git mv` 자체는 범위 안(§0.1)
- `archive/worktrees/` — read-only
- 실험 폴더 이름/위치 변경 — `DESIGN_FILES`가 영향받음(단 `DESIGN_FILES`는
  이제 `superseded/_h1a_diag.py` 안에서만 쓰이고, 그 모듈은 은퇴 상태라
  활성 게이트에 영향 없음 — 2026-08-02 실측)
