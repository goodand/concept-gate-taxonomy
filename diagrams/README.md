# 이 폴더는 **제안 다이어그램**이다 — as-built가 아니다

- 20개 `.mmd`, 렌더(`.svg`) 없음. 마지막 커밋 `c0cb8f1` (2026-07-18).
- 표기 규약의 근거는 [`../docs/diagrams/README.md`](../docs/diagrams/README.md)
  "as-built 정직성" 절이다 — **"다이어그램이 코드보다 앞서 있었다"가 codex
  라인이 Amendment 36에서 겪은 실패 형태**이고, 표기가 그 재발 방지다.
  이 폴더에는 그 표기가 없었다. 이 파일이 그것이다.

## 실측 (2026-08-24) — 무엇이 코드에 있고 무엇이 없는가

| 다이어그램이 쓰는 이름 | `conceptgate/` 실측 | 판정 |
|---|---:|---|
| `cg_normalizer` · `cg_owl.build_ontology` · HermiT · `classify` | 실재 | **as-is 서술로 유효** |
| `equivalence` | 11건 | as-is |
| `lint` | 56건 | as-is |
| `classify_facts` | **0건** | **제안 — 미구현** |
| `thin_signal` | **0건** | **제안 — 미구현** |
| `accidental`(equivalence) | **0건** | **제안 — 미구현** |

즉 이 폴더는 **as-is 서술 몇 장과 미구현 제안 여러 장이 라벨 없이 섞여
있다.** `current-pipeline-equivalence-discarded.mmd`는 실제 파이프라인을
정확히 그리고, `r2-*`·`design-change-*`·`proposed-*`는 채택되지 않은 설계다.

## 읽는 사람이 지킬 것

- **`r2-*` · `design-change-*` · `proposed-*` 를 현재 코드의 서술로 읽지 마라.**
  위 표의 0건이 근거다.
- 이 파일들은 **git이 추적**하므로 지워도 `git show c0cb8f1:<path>`로 복구된다.
  그러나 **삭제 판정은 하지 않았다** — 채택되지 않은 것과 폐기된 것은 다르고,
  그 구분은 이 폴더의 증거만으로는 서지 않는다(참조 0·이름·나이는 이 저장소가
  삭제 근거로 기각한 것들이다: `docs/WORKSPACE_CLEANUP_20260824_ROUND4.md` §10).

## 왜 렌더가 없나

`docs/diagrams/README.md`의 현행 규약은 `.mmd`가 canonical source이고 `.svg`가
확인된 렌더다. 이 폴더는 렌더가 0개이므로 **잘못된 SVG가 존재하지 않는다** —
오용 위험은 렌더가 아니라 라벨 부재였고, 이 파일이 그것을 메운다.
