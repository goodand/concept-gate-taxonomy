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
    """오탐 부류 — **실행 출력**은 정적 파일에 있을 수 없다 (2026-08-31).

    왜 생겼나: 스키마 강제 위임의 회신 12건을 태우니 11건이 폐기됐고, 폐기
    근거 인용 37건을 **전수 분류**하니 대부분이 실행 출력·셸 명령·생략부호
    축약이었다. 기존 14개 계약은 위음성(공백·ANSI·스마트쿼트)에 셋 이상을
    쓰면서 위양성에는 `MIN_CITATION` 하나뿐이었고, 그 비대칭이 이것을
    통과시켰다.

    이 계약은 초판에서 **결함을 기록**했고(현행 동작 = 폐기), 규칙 기반
    트러블슈팅으로 뒤집혔다 — docstring 이 예고한 그 방향이다."""
    target = tmp_path / "t.py"
    target.write_text("x = 1\n", encoding="utf-8")
    exec_output = {"id": 1, "claim": "실측: `TypeError: argument of type 'int' "
                                     "is not iterable` 로 죽는다"}
    r = vfc.check(exec_output, [target])
    assert r["verdict"] == "NOT_CHECKABLE"
    assert r["missing"] == []
    assert "execution_output" in r["uncheckable"].values()


def test_each_uncheckable_kind_is_recognized():
    """부류별 판별 — 오늘 코퍼스 37건에서 도출한 넷."""
    assert vfc.uncheckable_kind("TypeError: bad operand") == "execution_output"
    assert vfc.uncheckable_kind("call(x) -> pass") == "execution_output"
    assert vfc.uncheckable_kind('grep -rn "bytes" a.py') == "shell_command"
    assert vfc.uncheckable_kind("certify(... evidence ...)") == "elided_paraphrase"


def test_a_hallucinated_file_citation_cannot_escape_through_the_discriminator(tmp_path):
    """음성 증명 — 판별기가 도피구가 되면 안 된다.

    부류 판별을 넓히면 **환각한 파일 인용이 이 문으로 빠져나간다.** 평범한
    코드/문서 인용은 어느 부류에도 걸리지 않아야 하고, 없으면 폐기되어야
    한다. 이 계약이 없으면 "전부 NOT_CHECKABLE" 구현이 위 셋을 통과한다."""
    target = tmp_path / "t.py"
    target.write_text("real_symbol = 1\n", encoding="utf-8")
    for fake in ("`nonexistent_symbol_xyz`", "`def totally_absent_function`"):
        r = vfc.check({"id": 9, "claim": f"코드에 {fake} 가 있다"}, [target])
        assert r["verdict"] == "EVIDENCE_NOT_FOUND", fake
        assert r["uncheckable"] == {}, fake
    ok = vfc.check({"id": 10, "claim": "코드에 `real_symbol` 이 있다"}, [target])
    assert ok["verdict"] == "CITATION_FOUND"


def test_a_hallucination_disguised_as_uncheckable_is_not_grounded(tmp_path):
    """재생성 루프의 수락 기준 — Goodhart 방어 (2026-08-31 실측).

    부류 판별기(`uncheckable_kind`)는 정직하지만 **재생성 압력이 붙으면
    도피구가 된다**: 같은 환각 심볼을 트레이스백·화살표 출력·셸 명령·
    생략부호로 위장하니 넷 다 `NOT_CHECKABLE` 이었다. "폐기 안 됨"을
    재시도 수락 기준으로 쓰면 생성자는 그 포장을 학습하고, 환각 탐지기가
    환각 세탁기가 된다.

    그래서 수락 기준은 `is_grounded`(≥1 CITATION_FOUND)이지 `kept` 가
    아니다 — `NOT_CHECKABLE` 은 이 저장소 어휘로 `BLOCKED` 이고 자동
    허용이 아니다."""
    target = tmp_path / "t.py"
    target.write_text("real_symbol = 1\n", encoding="utf-8")
    disguises = [
        "실측: `AttributeError: nonexistent_symbol_xyz is missing` 로 죽는다",
        "실행: `nonexistent_symbol_xyz -> pass` 를 확인했다",
        "확인: `grep -n nonexistent_symbol_xyz t.py` 로 확인했다",
        "코드에 `nonexistent_symbol_xyz(...)` 가 있다",
    ]
    for d in disguises:
        f = {"id": 1, "claim": d}
        # 폐기되지 않는다 — 그래서 kept 를 수락 기준으로 쓰면 통과한다.
        assert vfc.check(f, [target])["verdict"] == "NOT_CHECKABLE", d
        assert f in vfc.partition([f], [target])["kept"], d
        # 그러나 근거가 없다 — 이것이 루프가 봐야 하는 신호다.
        assert not vfc.is_grounded(f, [target]), d
    # 짝: 실재하는 인용은 근거가 있다(없으면 "항상 False" 구현이 통과한다).
    assert vfc.is_grounded({"id": 2, "claim": "코드에 `real_symbol` 이 있다"},
                           [target])


def test_grounded_is_sound_about_citations_not_about_findings(tmp_path):
    """건전성의 범위 — `is_grounded` 의 이름이 부르는 오해를 막는다.

    실측(2026-08-31): 코드를 **정확히 인용하면서** 완전히 틀린 해석을 붙인
    finding 이 통과한다. 규칙이 결정할 수 있는 명제는 "이 문자열이 이 파일에
    있다"이고 "이 코드가 결함이다"가 아니다.

    이 계약이 없으면 `is_grounded` 가 수락 기준으로 쓰일 때 "규칙 기반으로
    맞는 것만 통과시킨다"는 성질이 있다고 잘못 읽힌다 — 그 성질을 얻으려면
    명제를 **실행 가능한 것**으로 좁혀야 한다."""
    target = tmp_path / "t.py"
    target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    false_but_cited = {"id": 1,
                       "claim": "`return a + b` 는 두 인자를 곱한다 — 곱셈 버그",
                       "evidence": "t.py:2 `return a + b`"}
    assert vfc.check(false_but_cited, [target])["verdict"] == "CITATION_FOUND"
    assert vfc.is_grounded(false_but_cited, [target]) is True   # 그리고 틀렸다


def test_the_g134_case_is_reproduced_against_the_real_document():
    """실물 회귀 — Q33 상신서에 `p02`가 없다는 것을 문서로 확인한다.

    **이 계약이 판별기의 상한이다**: G134 의 환각 인용은 `claim` 필드에
    있었으므로 `claim` 스캔을 끄면 이 catch 가 죽는다. 그래서 남은 오탐
    (산문 요약이 `claim` 에 인용부호로 들어오는 것)은 규칙으로 못 가른다 —
    `claim` 은 본디 요약이 들어오는 자리다. 그것은 **스키마 문제**이고
    (파일 인용 전용 필드 분리), 모델이 그 구분을 지키는지는 arm 설계가
    필요한 실험이다.

    규칙으로 못 가르는 것 둘 더(2026-08-31 실측, 미수리):
    - **낡은 인용**: 회신이 읽은 시점엔 실재했는데 그 뒤 내가 그 줄을
      고쳤다(`cited = [t for t in ...]`, 커밋 f748d87). 환각과 구별 불가 —
      가르려면 인용을 revision 에 결박해야 한다(`stale_obligations` 와 같은
      형태). `git log -S` 로 확인 가능하나 도구가 아직 안 한다.
    - **문자열 연결 경계**: f-string 이 두 줄로 쪼갠 문장은 공백 정규화로도
      못 찾는다(`검사할 어휘 없음 — …` 실측)."""
    doc = ROOT / "docs" / "DESIGN_REQUEST_referential_participant_quantification.md"
    if not doc.exists():
        pytest.skip("Q33 상신서가 없는 체크아웃")
    hallucinated = {"id": 134, "claim": "표 첫 행 case ID가 `PMB-p02-d2298` 오타"}
    real = {"id": 0, "claim": "표에 `PMB-p00-d2298` 행이 있다"}
    assert vfc.check(hallucinated, [doc])["verdict"] == "EVIDENCE_NOT_FOUND"
    assert vfc.check(real, [doc])["verdict"] == "CITATION_FOUND"
