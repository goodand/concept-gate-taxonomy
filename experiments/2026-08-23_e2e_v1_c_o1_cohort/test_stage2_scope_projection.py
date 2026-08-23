"""D-E2E-v1-25 Q25.1: O1_SCOPE_PROJECTION_V1 — RED 먼저.

projection은 formula 재작성기가 아니라 **측정 함수**다: oracle·subject
양측에 같은 함수를 적용해 scope signature를 얻고, signature끼리 exact
structural match(기존 커널 evaluate 그대로)로 비교한다. full formula
동치를 주장하지 않는다(판정 §3).

signature는 **IR 형태의 트리**로 남긴다 — 커널이 projection을 모른 채
(§29 경계) 기존 canonicalize/evaluate를 재사용하기 위해서다.

동결 규칙 (이 계약이 정본):
- 입력은 내부에서 desugar(idempotent)를 먼저 통과한다. 라벨 codec에
  의존하지 않는다(라벨은 어차피 익명화).
- source별 정책 dispatch: `project_scope_for_case(case_id, formula)` —
  PMB-/FOLIO- 외 접두어는 ValueError (fail-closed).
- **변수 분류** (PMB 정책의 핵심 — 15 fixture 73개 양화 변수 전수 실측으로
  잔여 0 확인된 규칙): 술어 하나의 "scaffold 용법" = 이름이 (i) 대문자
  시작 비-synset(ROLE: Agent, EQU, …) 또는 (ii) 동사 synset `*.v.NN` 또는
  (iii) 시간 명사 synset(`time.n.*`, `month.n.*`). 변수의 용법 전부가
  scaffold 용법이면 그 변수는 SCAFFOLD, 아니면 PARTICIPANT. subject의
  평범한 소문자 술어는 어느 scaffold 조건에도 안 걸리므로 subject 변수는
  자연히 PARTICIPANT다 — 같은 함수가 양측에 안전하게 적용된다.
- **PMB 정책**: SCAFFOLD 변수의 ∃ 노드는 제거(본문 승격). 술어 제거:
  SCAFFOLD 변수를 만지는 것 / ROLE·동사 synset·시간 synset 이름인 것 /
  **arity ≥ 2인 것**(사건 매개 관계와 직접 관계의 granularity 교량 —
  양측 대칭 적용). 남는 것: PARTICIPANT 변수 위 1항 술어를 익명 slot으로.
- **FOLIO 정책**: 모든 양화 유지, 모든 술어 유지(arity·인자 결박 순서
  포함 — P(x,y) ≠ P(y,x)), 라벨만 익명화.
- 라벨 익명화: 술어 이름 → "□". 단 **"True"는 보존**(desugar의 중립
  제한식 식별 토큰 — 익명화하면 비교 의미가 깨진다).
- AND 정리: 제거로 빈 AND는 소거, 단일 인자 AND는 그 인자로 붕괴,
  **남는 인자 순서는 보존**(기존 계약과 동일하게 순서 민감 — 새 완화 없음).
- projection은 idempotent이고 입력을 변이하지 않는다.
- witness는 이 모듈의 산출물이 아니다: satisfiability 모듈이 subject
  방언 렌더러로 만들고, 이 projection을 왕복시켜 검증한다(판정 §22).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_scope_projection as proj  # noqa: E402
from conceptgate import cg_evaluate  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
E = lambda n: {"kind": "entity", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
FA = lambda v, r, b: {"kind": "forall", "var": v, "restriction": r, "body": b}
EX = lambda v, r, b: {"kind": "exists", "var": v, "restriction": r, "body": b}
AND = lambda *a: {"kind": "and", "args": list(a)}
NOT = lambda b: {"kind": "not", "body": b}
T = P("True")


def same(a, b) -> bool:
    """projection 결과 비교 = 기존 커널 evaluate 그대로 (α-rename 후 구조 동일)."""
    return cg_evaluate.evaluate(a, b)["result"] == "pass"


def test_profile_identity():
    assert proj.PROJECTION_PROFILE_ID == "O1_SCOPE_PROJECTION_V1"


# ---- 자격 P1 — nuisance 불변 (판정 §28) ----

def test_p1_event_time_role_scaffolding_is_invisible():
    plain = NOT(FA("x", P("child.n.01", V("x")),
                   EX("y", T, AND(P("apple.n.01", V("y")),
                                  P("like", V("x"), V("y"))))))
    davids = NOT(FA("x", P("child.n.01", V("x")),
                    EX("y", T, AND(P("apple.n.01", V("y")),
                       EX("e", T, AND(P("like.v.03", V("e")),
                          P("Experiencer", V("e"), V("x")),
                          P("Stimulus", V("e"), V("y")),
                          EX("t", T, AND(P("time.n.08", V("t")),
                             P("Time", V("e"), V("t"))))))))))
    a = proj.project_scope_for_case("PMB-p00-t1", plain)
    b = proj.project_scope_for_case("PMB-p00-t1", davids)
    assert same(a, b)


def test_p1_subject_side_gets_the_same_function():
    """같은 PMB 정책이 subject IR에도 적용된다 — 평범한 소문자 술어는
    전부 PARTICIPANT이고, arity≥2 술어(like)는 양측 대칭으로 빠진다."""
    subject = NOT(FA("x", P("child", V("x")),
                     EX("y", P("apple", V("y")), P("like", V("x"), V("y")))))
    oracle = NOT(FA("x0", P("child.n.01", V("x0")),
                    EX("x2", T, AND(P("apple.n.01", V("x2")),
                       EX("x1", T, AND(P("like.v.03", V("x1")),
                          P("Experiencer", V("x1"), V("x0")),
                          P("Stimulus", V("x1"), V("x2"))))))))
    assert same(proj.project_scope_for_case("PMB-p15-t2", subject),
                proj.project_scope_for_case("PMB-p15-t2", oracle))


# ---- 자격 P2 — 양화 교환은 잡는다 ----

def test_p2_quantifier_swap_fails():
    fa_ex = FA("x", P("a.n.01", V("x")), EX("y", P("b.n.01", V("y")), T))
    ex_fa = EX("x", P("a.n.01", V("x")), FA("y", P("b.n.01", V("y")), T))
    assert not same(proj.project_scope_for_case("PMB-p1-t", fa_ex),
                    proj.project_scope_for_case("PMB-p1-t", ex_fa))


# ---- 자격 P3 — 부정 이동은 잡는다 ----

def test_p3_negation_movement_fails():
    neg_out = NOT(FA("x", P("a.n.01", V("x")), P("b.n.01", V("x"))))
    neg_in = FA("x", P("a.n.01", V("x")), NOT(P("b.n.01", V("x"))))
    assert not same(proj.project_scope_for_case("PMB-p2-t", neg_out),
                    proj.project_scope_for_case("PMB-p2-t", neg_in))


# ---- 자격 P4 — FOLIO topology (D-24 유지: 104 반례 실측 쌍) ----

def test_p4_folio_implication_topology_fails():
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    f1 = FA("x", T, EX("y", T, IMP(AND(P("A", V("x")), P("B", V("y"))),
                                   P("C", V("x"), V("y")))))
    f2 = FA("x", T, IMP(P("A", V("x")),
                        EX("y", T, AND(P("B", V("y")), P("C", V("x"), V("y"))))))
    assert not same(proj.project_scope_for_case("FOLIO-1t", f1),
                    proj.project_scope_for_case("FOLIO-1t", f2))


# ---- 자격 P5 — 라벨만 다르면 통과 (F1의 회귀 계약) ----

def test_p5_label_only_variation_passes_folio():
    a = FA("m", P("Lab", V("m")), P("Cheaper", V("m")))
    b = FA("m", P("equipped_in_lab", V("m")), P("cheaper_than_original", V("m")))
    assert same(proj.project_scope_for_case("FOLIO-175t", a),
                proj.project_scope_for_case("FOLIO-175t", b))


# ---- 자격 P6 — target 양화 삭제는 잡는다 ----

def test_p6_target_quantifier_deletion_fails():
    two = FA("x", P("a.n.01", V("x")), EX("y", P("b.n.01", V("y")), T))
    one = FA("x", P("a.n.01", V("x")), P("b.n.01", V("x")))
    assert not same(proj.project_scope_for_case("PMB-p3-t", two),
                    proj.project_scope_for_case("PMB-p3-t", one))


# ---- FOLIO 정책: 결박 topology는 채점 유지 ----

def test_folio_argument_incidence_order_still_scored():
    a = FA("x", T, EX("y", T, P("r", V("x"), V("y"))))
    b = FA("x", T, EX("y", T, P("r", V("y"), V("x"))))
    assert not same(proj.project_scope_for_case("FOLIO-2t", a),
                    proj.project_scope_for_case("FOLIO-2t", b))


def test_folio_keeps_all_quantifiers_and_pred_occurrences():
    f = FA("x", P("Zorble", V("x")),
           AND(P("Glims", V("x")), P("Praxes", V("x"))))
    out = proj.project_scope_for_case("FOLIO-3t", f)
    s = json.dumps(out, ensure_ascii=False)  # 기본 ensure_ascii는 □를 \u25a1로 바꾼다
                                             # (첫 위임 구현이 이걸 전역 monkey-patch로
                                             # 우회하려다 거부된 이력 — 버그는 테스트 쪽이었다)
    assert s.count('"pred"') >= 3 + 1  # 술어 3 + desugar True 최소 1
    assert '"□"' in s and '"Zorble"' not in s


# ---- 공통 불변식 ----

def test_true_token_survives_projection():
    out = proj.project_scope_for_case("FOLIO-4t", FA("x", T, P("Glims", V("x"))))
    assert '"True"' in json.dumps(out, ensure_ascii=False)


def test_projection_is_pure_and_idempotent():
    f = NOT(FA("x", P("child.n.01", V("x")), EX("e", T, P("run.v.01", V("e")))))
    snap = copy.deepcopy(f)
    once = proj.project_scope_for_case("PMB-p4-t", f)
    assert f == snap
    assert proj.project_scope_for_case("PMB-p4-t", once) == once


def test_dispatch_unknown_prefix_refuses():
    with pytest.raises(ValueError):
        proj.project_scope_for_case("SMOKE-01", FA("x", T, P("a", V("x"))))


def test_empty_and_is_pruned_not_left_dangling():
    """제거로 비어버린 AND가 signature에 남아 위양성 mismatch를 만들면 안 된다."""
    only_scaffold = FA("x", P("a.n.01", V("x")),
                       EX("e", T, AND(P("run.v.01", V("e")),
                                      P("Agent", V("e"), V("x")))))
    bare = FA("x", P("a.n.01", V("x")), T)
    assert same(proj.project_scope_for_case("PMB-p5-t", only_scaffold),
                proj.project_scope_for_case("PMB-p5-t", bare))


# witness 관련 주의: signature는 desugar를 통과하므로 implies를 포함할 수
# 있고 subject schema 밖이다 — 이는 설계다(비교는 커널 evaluate가 하므로
# 무방). subject 방언 witness는 satisfiability 모듈의 결정론 렌더러가
# 만들고 project(witness)==project(oracle) 왕복으로 검증한다. 초판 계약이
# 두 역할을 한 산출물에 요구해 위임 구현이 undesugar hack으로 우회했던
# 이력이 있다 — 그 요구는 여기서 제거됐다.


# ---- D-E2E-v1-26 자격 P7·P8 (implies 방언 확장 후) ----

def test_p7_implication_under_exists_roundtrips():
    """P7: ∃ 아래 함의가 projection→witness→재projection 왕복에서 같은
    위치에 남는다 (D-26 §7 — 6종 방언에서 witness는 signature 그대로)."""
    import _stage2_satisfiability as sat
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    f = FA("x", T, EX("y", T, IMP(P("A", V("x")), P("B", V("y")))))
    sig = proj.project_scope_for_case("FOLIO-p7t", f)
    w = sat.render_witness(sig)
    assert '"implies"' in json.dumps(w)                      # 위치 보존(소실 금지)
    assert same(proj.project_scope_for_case("FOLIO-p7t", w), sig)


def test_p8_implication_position_discriminated():
    """P8: ∀→∃→→ 와 ∀→→→∃ 는 왕복 후에도 다른 signature (104 반례 쌍)."""
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    folio_form = FA("x", T, EX("y", T, IMP(AND(P("a", V("x")), P("b", V("y"))),
                                           P("c", V("x"), V("y")))))
    natural = FA("x", P("a", V("x")),
                 EX("y", P("b", V("y")), P("c", V("x"), V("y"))))
    assert not same(proj.project_scope_for_case("FOLIO-p8t", folio_form),
                    proj.project_scope_for_case("FOLIO-p8t", natural))


# ---- D-E2E-v1-27 Q27.1(c): O1_LOCAL_IDIOM_NORMALIZATION_V1 (curry만) ----

def test_curry_normalization_profile_identity():
    assert proj.IDIOM_NORMALIZATION_ID == "O1_LOCAL_IDIOM_NORMALIZATION_V1"


def test_curry_pair_converges_after_normalization():
    """판정 §3-4: `(A∧B)→C` ↔ `A→(B→C)`, 정본형은 uncurried.
    구현 전 실측에서 이 쌍의 signature가 불일치였다(D-27 검증 기록 V3a) —
    이 계약이 그 회귀를 고정한다."""
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    unc = FA("x", T, IMP(AND(P("a", V("x")), P("b", V("x"))), P("c", V("x"))))
    cur = FA("x", T, IMP(P("a", V("x")), IMP(P("b", V("x")), P("c", V("x")))))
    assert same(proj.project_scope_for_case("FOLIO-c1", unc),
                proj.project_scope_for_case("FOLIO-c1", cur))


def test_curry_normalization_reaches_uncurried_canonical_form():
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    out = proj.normalize_local_idioms(
        IMP(P("a", V("x")), IMP(P("b", V("x")), P("c", V("x")))))
    assert out["kind"] == "implies"
    assert out["left"]["kind"] == "and"                 # 정본 = uncurried
    assert [a["name"] for a in out["left"]["args"]] == ["a", "b"]
    assert out["right"]["name"] == "c"


def test_curry_normalization_is_idempotent_and_pure():
    import copy
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    f = IMP(P("a", V("x")), IMP(P("b", V("x")), IMP(P("c", V("x")), P("d", V("x")))))
    snap = copy.deepcopy(f)
    once = proj.normalize_local_idioms(f)
    assert f == snap
    assert proj.normalize_local_idioms(once) == once
    assert [a["name"] for a in once["left"]["args"]] == ["a", "b", "c"]


def test_curry_does_not_cross_quantifier_boundary():
    """판정 §3: 양화 경계 교차 금지 — 함의 오른쪽이 양화면 접지 않는다."""
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    f = IMP(P("a", V("x")), EX("y", T, IMP(P("b", V("y")), P("c", V("y")))))
    out = proj.normalize_local_idioms(f)
    assert out["left"]["kind"] == "pred"        # and로 합쳐지지 않았다
    assert out["right"]["kind"] == "exists"


def test_curry_does_not_cross_negation_boundary():
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    f = IMP(P("a", V("x")), NOT(IMP(P("b", V("x")), P("c", V("x")))))
    out = proj.normalize_local_idioms(f)
    assert out["left"]["kind"] == "pred"
    assert out["right"]["kind"] == "not"


def test_neg_exists_vs_forall_neg_still_distinct():
    """판정 §5: `¬∃ ↔ ∀¬`는 **불허** — scored 양화 종류를 바꾸므로
    정규화가 이 둘을 합치면 안 된다(음성 계약)."""
    a = NOT(EX("x", P("r", V("x")), P("b", V("x"))))
    b = FA("x", P("r", V("x")), NOT(P("b", V("x"))))
    assert not same(proj.project_scope_for_case("PMB-n1", a),
                    proj.project_scope_for_case("PMB-n1", b))


def test_folio_control_500p4_shape_now_converges():
    """실측 회귀: CTRL4-03이 fail한 형태(gold 연접 전제 vs subject curried)."""
    IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}
    gold = FA("x", T, IMP(AND(P("Horse", V("x")), P("Racing", V("x"))),
                          P("Racehorse", V("x"))))
    subj = FA("x", P("horse", V("x")),
              IMP(P("in_race", V("x")), P("racehorse", V("x"))))
    assert same(proj.project_scope_for_case("FOLIO-500p4", gold),
                proj.project_scope_for_case("FOLIO-500p4", subj))
