# 활성 실험 디렉토리 정리 — 조사 결과 및 정정

- 작성: 2026-08-01 (초안) / **전면 정정: 2026-08-01**
- 문서 종류: **설계 문서**(`WORKSPACE_NAVIGATION.md` §2)
- 계기: vault 정리 agent가 활성 실험 폴더만 정리하지 못한 것으로 보여
  "정리 설계"를 요청받았다.

---

## 0. 결론 — 정리 대상이 아니다. 이미 그렇게 결정돼 있었다

**활성 실험 폴더가 정리되지 않은 것은 누락이 아니라 채택된 결정이다.**

`notes/audits/vault/symlink-vs-moc-2026-07-30.md`(`status: finished`)의
"Adopted hybrid" 1항, verbatim:

> 1. Keep repository and active experiment paths unchanged.

같은 문서가 근거도 남겼다:

> Format-first canonical storage remains useful for newly ingested,
> vault-owned artifacts. **It is unsafe to impose physically on tracked
> repositories or active worktrees because moving files can break imports,
> relative links, fixture locators, hashes, and Git provenance.**

그리고 6항:

> 6. Treat neither MOCs nor symlinks as authority; resolve to the canonical
>    path before answering or editing.

**즉 분류는 파일시스템이 아니라 vault의 생성된 MOC 계층에서 일어난다.**
repo 디렉토리가 평면인 것은 방치가 아니라 설계다.

---

## 1. 이 문서의 초안이 틀렸던 지점 (기록 보존)

초안은 활성 실험 폴더 안에 `correspondence/`와 `superseded/`를 만들어
`git mv`하자고 제안했다. **채택된 결정 1항과 정면으로 충돌한다.**

| 초안 제안 | 실제 |
|---|---|
| `correspondence/`로 `DESIGN_REQUEST*` 이동 | ❌ "active experiment paths unchanged" 위반. 게다가 MOC wikilink 4건이 그 경로를 가리킴 |
| `superseded/`로 `_h1a_diag*` 이동 | ❌ 같은 위반. supersession은 **`by-status/` facet이 이미 담당**(active/blocked/deferred/finished/legacy) |
| `docs/EXTERNAL_RULINGS.md` 원장 신설 | ❌ 불필요. 미러의 `canonical:` frontmatter가 파일 단위로 같은 정보를 기계가독 형태로 이미 담는다 |
| "사본 2개는 drift 위험 → inbox를 비운다"(P-4) | ❌ 미러 + `canonical:` 포인터가 **의도된 패턴**이다. 실측 드리프트 309~338바이트는 전부 frontmatter이고, load-bearing인 template fence는 **바이트 동일** |
| 코드 분류 체계가 없다 | ❌ `by-code/` facet이 이미 존재: `active-protected` / `reuse-now` / `extract-later` / `historical-prototypes` / `provenance-snapshots` |

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

### 3.3 supersession은 **facet으로** 표시한다

Q6=A가 `_h1a_diag*`를 은퇴시킨다. 파일을 옮기지 않고:

- `.md` 아티팩트: frontmatter `status:`를 `finished`/`legacy`로 →
  `by-status/` facet이 자동 반영
- `.py`는 frontmatter를 가질 수 없다 → **모듈 docstring 상단에 은퇴 사유와
  대체물**을 적고, 실험 `README.md`·`PREREGISTRATION.md` §11에서 명시.
  vault 측 표현은 `by-code/historical-prototypes` facet
- **삭제하지 않는다.** `_h1a_diag_score.py`의 §11.2 채점 논리는 후속 설계가
  앵커를 재도입하면 다시 필요하다

---

## 4. 정리 agent 위임 범위 (수정)

| 대상 | 위임 | 근거 |
|---|---|---|
| `notes/` inbox 처리·frontmatter 부여 | ✅ | vault 소유 아티팩트. 채택된 결정 2·3항 |
| MOC 재생성 | ✅ | 생성 아티팩트. 결정 3항 |
| `experiments/**/__pycache__` | ✅ | gitignore 대상, 재생성됨 |
| **활성 실험 폴더 내 이동** | ❌ | **결정 1항이 금지.** "정리 못 한 것"이 아니라 "정리하지 않기로 한 것" |
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

---

## 6. 검증

```bash
# 채택된 결정 원문 확인
obsidian read path="notes/audits/vault/symlink-vs-moc-2026-07-30.md"

# 이 문서가 그 결정과 충돌하지 않는지: 활성 폴더 이동 제안이 없어야 한다
grep -n 'correspondence/\|superseded/\|git mv' docs/DESIGN_workspace_file_placement.md

# inbox 처리 여부
ls ../notes/DESIGN_DECISION*.md 2>/dev/null && echo 'inbox 미처리' || echo 'inbox clean'

# MOC가 최신인지 (커밋 후)
python3 ../.vault-harness/vault-md-retrieval/generate_vault_mocs.py
```

## 7. 범위 밖

- 활성 실험 폴더 재구조화 — **채택된 결정이 금지**. 되살리려면 감사 문서를
  뒤집는 별도 결정이 필요하다
- `archive/worktrees/` — read-only
- 실험 폴더 이름/위치 변경 — `DESIGN_FILES`가 영향받음
