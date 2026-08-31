"""적대검증 finding이 **존재하지 않는 인용**을 근거로 들면 자동 폐기한다.

## 왜 이것이 필요한가 (실측 2건)

`adversarial-review` 스킬은 "evidence 없는 finding은 즉시 폐기한다"를 환각
전파를 막는 핵심 장치로 규정한다. 그런데 **evidence가 있는 것처럼 보이면서
실재하지 않는** 경우를 사람이 잡아야 했다.

* 2026-08-24, Q33 상신서 적대검증: finding이 "표 첫 행 case ID가
  `PMB-p02-d2298` 오타"라고 보고했다. 그 문서에 `p02` 문자열은 **0건**이고,
  실제 표기는 `PMB-p00-d2298`이었다. evidence 필드는 존재하지 않는 인용을
  근거로 들었다. `rg -c p02` 한 번으로 반증됐지만 **내가 재실측하지
  않았다면 정확한 문서를 틀리게 고쳤을 것이다.**
* 같은 날 D-33 검증설계 적대검증: blocker 4건 중 1건이 판정문 §8과 §10을
  혼동한 오독이었다. 그것은 인용 존재 문제가 아니라 독해 문제라 이 게이트가
  잡지 못한다 — **이 게이트의 범위를 정직하게 좁히는 사례**로 여기 적는다.

## 이 게이트가 하는 것과 하지 않는 것

**한다**: finding이 백틱·인용부호로 감싼 문자열이 대상 문서에 **실재하는지**
확인하고, 없으면 `EVIDENCE_NOT_FOUND`로 표시한다. 스킬의 기존 규칙("evidence
없는 finding은 폐기")을 기계로 옮긴 것이지 새 정책이 아니다.

**하지 않는다**: finding이 옳은지 판단하지 않는다. 인용이 실재해도 해석이
틀릴 수 있고(위 두 번째 사례), 인용이 없어도 주장이 맞을 수 있다. 그래서
인용이 아예 없는 finding은 폐기하지 않고 `NOT_CHECKABLE`로 남긴다 — lead가
읽어야 한다는 뜻이다.

**짧은 인용은 검사하지 않는다.** 내 계측기가 이 세션에 네 번 오발했고 전부
"그럴듯한 오탐"이었다. `MIN_CITATION` 미만은 일반 단어일 가능성이 커서
`NOT_CHECKABLE`로 둔다 — 오발이 게이트의 신뢰를 깎고, 신뢰 잃은 게이트는
꺼진다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import verify_finding_citations as vfc  # noqa: E402


# ---- 계약 선언 ---------------------------------------------------------

def test_verdict_vocabulary_is_closed():
    assert vfc.VERDICTS == ("CITATION_FOUND", "EVIDENCE_NOT_FOUND",
                            "NOT_CHECKABLE")


def test_short_citations_are_not_checked():
    """오발 방지 — 짧은 문자열은 일반 단어일 수 있다."""
    assert vfc.MIN_CITATION >= 6


# ---- 인용 추출 ---------------------------------------------------------

def test_backtick_citations_are_extracted():
    f = {"claim": "표 첫 행 case ID가 `PMB-p02-d2298` 오타"}
    assert vfc.citations(f) == ["PMB-p02-d2298"]


def test_quoted_citations_are_extracted():
    f = {"claim": '문서가 "restriction 비-head content"라고 적는다'}
    assert "restriction 비-head content" in vfc.citations(f)


def test_short_tokens_are_dropped_from_citations():
    f = {"claim": "`a` 와 `bc` 는 인용으로 세지 않는다"}
    assert vfc.citations(f) == []


def test_evidence_field_is_also_scanned():
    f = {"claim": "무언가", "evidence": "`FORALL_RSTR_BODY` 상수를 본다"}
    assert "FORALL_RSTR_BODY" in vfc.citations(f)


# ---- 판정 --------------------------------------------------------------

def test_present_citation_is_found(tmp_path):
    t = tmp_path / "doc.md"
    t.write_text("표에 `PMB-p00-d2298` 행이 있다\n", encoding="utf-8")
    out = vfc.check({"id": 1, "claim": "case ID가 `PMB-p00-d2298`"}, [t])
    assert out["verdict"] == "CITATION_FOUND"


def test_absent_citation_is_evidence_not_found(tmp_path):
    """이것이 G134다 — 존재하지 않는 인용을 근거로 든 환각."""
    t = tmp_path / "doc.md"
    t.write_text("표에 `PMB-p00-d2298` 행이 있다\n", encoding="utf-8")
    out = vfc.check({"id": 1, "claim": "case ID가 `PMB-p02-d2298` 오타"}, [t])
    assert out["verdict"] == "EVIDENCE_NOT_FOUND"
    assert "PMB-p02-d2298" in out["missing"]


def test_finding_without_citation_is_not_discarded(tmp_path):
    """인용이 없다고 틀린 것은 아니다 — lead가 읽어야 한다."""
    t = tmp_path / "doc.md"
    t.write_text("본문\n", encoding="utf-8")
    out = vfc.check({"id": 1, "claim": "설계 순서가 뒤집혔다"}, [t])
    assert out["verdict"] == "NOT_CHECKABLE"


def test_whitespace_and_linebreaks_do_not_cause_false_negatives(tmp_path):
    """대상 문서가 줄바꿈으로 접힌 인용도 찾아야 한다 — 오발이 신뢰를 깎는다."""
    t = tmp_path / "doc.md"
    t.write_text("판정은 `operational_patch:\n  forbidden` 이다\n", encoding="utf-8")
    out = vfc.check({"id": 1, "claim": "`operational_patch: forbidden`"}, [t])
    assert out["verdict"] == "CITATION_FOUND"


def test_ansi_escapes_in_the_target_do_not_cause_false_negatives(tmp_path):
    """SBN 실물이 ANSI를 담는다 — 이 세션에 그것으로 계측기가 한 번 죽었다."""
    t = tmp_path / "doc.md"
    t.write_text("male.n.02 \x1b[31m% him\x1b[0m [18-22]\n", encoding="utf-8")
    out = vfc.check({"id": 1, "claim": "`male.n.02 % him [18-22]`"}, [t])
    assert out["verdict"] == "CITATION_FOUND"


# ---- 일괄 처리 ---------------------------------------------------------

def test_partition_separates_discarded_from_kept(tmp_path):
    t = tmp_path / "doc.md"
    t.write_text("`REAL_TOKEN_HERE` 가 있다\n", encoding="utf-8")
    findings = [
        {"id": 1, "claim": "`REAL_TOKEN_HERE` 를 본다"},
        {"id": 2, "claim": "`FAKE_TOKEN_HERE` 를 본다"},
        {"id": 3, "claim": "인용 없는 주장"},
    ]
    r = vfc.partition(findings, [t])
    assert [f["id"] for f in r["discarded"]] == [2]
    assert sorted(f["id"] for f in r["kept"]) == [1, 3]
    assert r["counts"] == {"CITATION_FOUND": 1, "EVIDENCE_NOT_FOUND": 1,
                           "NOT_CHECKABLE": 1}


def test_partition_accounting_is_exhaustive(tmp_path):
    """행 손실은 조용한 통과다 — 합이 맞아야 한다."""
    t = tmp_path / "doc.md"; t.write_text("x\n", encoding="utf-8")
    findings = [{"id": i, "claim": f"`TOKEN_{i}_LONG`"} for i in range(5)]
    r = vfc.partition(findings, [t])
    assert len(r["kept"]) + len(r["discarded"]) == 5
    assert sum(r["counts"].values()) == 5


# ---- 게이트가 공허하지 않다는 증거 -------------------------------------

def test_execution_output_is_not_judged_as_a_missing_file_citation(tmp_path):
    """오탐 부류 — **실행 출력**은 정적 파일에 있을 수 없다 (2026-08-31 실측).

    이 계약이 왜 생겼나: 스키마 강제 위임의 회신 12건을 이 도구에 태우니
    **11건이 `EVIDENCE_NOT_FOUND`** 였고 거의 전부 오탐이었다 — 폐기된
    "인용"이 `TypeError: ...` 같은 실행 출력과 산문 요약이었다. 대상 파일에
    없는 것이 당연하고, 그것은 finding 이 거짓이라는 뜻이 **아니다.**

    기존 14개 계약은 **위음성**(공백·ANSI·스마트쿼트)에 셋 이상을 쓰면서
    **위양성**에는 `MIN_CITATION` 하나뿐이었고, 그것도 과거 오탐 4건 뒤에
    생겼다. 이 비대칭이 오늘의 11/12 를 통과시켰다.

    **이 계약은 현행 동작을 고정하지 않는다 — 결함을 기록한다.** 아래
    단언은 도구가 지금 무엇을 하는지이고, 옳은 처리는 스키마가 인용의
    **종류**(파일 인용 vs 실행 출력)를 가르는 것이다. 그 설계가 들어오면
    이 계약이 뒤집혀야 하는 쪽이다."""
    target = tmp_path / "t.py"
    target.write_text("x = 1\n", encoding="utf-8")
    exec_output = {"id": 1, "claim": "실측: `TypeError: argument of type 'int' "
                                     "is not iterable` 로 죽는다"}
    verdict = vfc.check(exec_output, [target])["verdict"]
    # 현행: 실행 출력을 파일 인용으로 검사해 폐기한다(오탐).
    assert verdict == "EVIDENCE_NOT_FOUND"
    # 그리고 그것이 finding 의 참·거짓과 무관하다는 것이 이 계약의 요점이다 —
    # 같은 문장의 판정은 실행으로만 갈린다.


def test_the_g134_case_is_reproduced_against_the_real_document():
    """실물 회귀 — Q33 상신서에 `p02`가 없다는 것을 문서로 확인한다."""
    doc = ROOT / "docs" / "DESIGN_REQUEST_referential_participant_quantification.md"
    if not doc.exists():
        pytest.skip("Q33 상신서가 없는 체크아웃")
    hallucinated = {"id": 134, "claim": "표 첫 행 case ID가 `PMB-p02-d2298` 오타"}
    real = {"id": 0, "claim": "표에 `PMB-p00-d2298` 행이 있다"}
    assert vfc.check(hallucinated, [doc])["verdict"] == "EVIDENCE_NOT_FOUND"
    assert vfc.check(real, [doc])["verdict"] == "CITATION_FOUND"
