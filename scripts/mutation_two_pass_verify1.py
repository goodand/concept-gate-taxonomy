"""범위 한정 전수 뮤테이션 — `test_two_pass_verify1.py` 의 kill rate 측정기.

측정치를 산문으로만 남기면 코드가 바뀔 때 조용히 거짓이 된다(동료 검토 ④,
P4 형태) — 그래서 측정기를 저장소에 둔다. 게이트가 아니라 **측정 도구**다
(advisory): 수치의 정본은 실행 출력이지 docstring 이 아니다.

계보: scratchpad v1 은 통파일 exec 가 dataclass 에서 죽어 14/14 가
'exec 실패=kill' 로 오인된 공허한 100% 였다(검산으로 적발). v2 가 대상
함수만 추출해 실제 모듈 전역에서 exec 한다(무변이 대조군 내장). 도구
선례·mutatest 기각 사유: evidence-evaluator/docs/TOOL_SURVEY_MUTATION_20260817.md

    사용:  python3 scripts/mutation_two_pass_verify1.py
"""
import ast, copy, importlib, sys, types
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from conceptgate import cg_obligations as real

SRC = (REPO / "conceptgate" / "cg_obligations.py").read_text(encoding="utf-8")
TREE = ast.parse(SRC)
TARGETS = {"results_from_claim_anchoring", "stale_obligations"}
FUNCS = [n for n in ast.walk(TREE)
         if isinstance(n, ast.FunctionDef) and n.name in TARGETS]

CMP_FLIP = {ast.In: ast.NotIn, ast.NotIn: ast.In, ast.Eq: ast.NotEq,
            ast.NotEq: ast.Eq, ast.Is: ast.IsNot, ast.IsNot: ast.Is,
            ast.Lt: ast.GtE, ast.Gt: ast.LtE, ast.LtE: ast.Gt, ast.GtE: ast.Lt}
VERDICT_SWAP = {"UNKNOWN": "PASS", "PASS": "UNKNOWN", "FAIL": "PASS"}

class Mutator(ast.NodeTransformer):
    """target 번째 변이 지점만 바꾼다. target=-1 이면 세기만 한다."""
    def __init__(self, target):
        self.n = 0; self.t = target; self.label = None
    def hit(self, label, ln):
        i = self.n; self.n += 1
        if i == self.t: self.label = (label, ln); return True
        return False
    def generic_visit(self, node):
        node = super().generic_visit(node)
        ln = getattr(node, "lineno", 0)
        if isinstance(node, ast.Compare):
            for j, op in enumerate(node.ops):
                if type(op) in CMP_FLIP and self.hit(f"cmp:{type(op).__name__}", ln):
                    node.ops[j] = CMP_FLIP[type(op)]()
        elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
              and node.value.id == "Verdict" and node.attr in VERDICT_SWAP):
            if self.hit(f"verdict:{node.attr}", ln):
                node.attr = VERDICT_SWAP[node.attr]
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in ("any", "all")):
            if self.hit(f"anyall:{node.func.id}", ln):
                node.func.id = "all" if node.func.id == "any" else "any"
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            if self.hit("dropnot", ln):
                return node.operand
        elif isinstance(node, ast.If):
            if self.hit("if->True", ln): node.test = ast.Constant(True)
            if self.hit("if->False", ln): node.test = ast.Constant(False)
        elif isinstance(node, ast.Continue):
            if self.hit("continue->pass", ln): return ast.Pass()
        elif isinstance(node, (ast.comprehension,)):
            pass
        return node

def count_sites():
    m = Mutator(-1)
    m.visit(copy.deepcopy(ast.Module(body=[copy.deepcopy(f) for f in FUNCS],
                                     type_ignores=[])))
    return m.n

def build_mutant(idx):
    mod_ast = ast.Module(body=[copy.deepcopy(f) for f in FUNCS], type_ignores=[])
    m = Mutator(idx); m.visit(mod_ast); ast.fix_missing_locations(mod_ast)
    g = dict(real.__dict__)          # 실제 모듈 전역 공유(클래스 동일성 유지)
    exec(compile(mod_ast, "mutant", "exec"), g)
    return {n: g[n] for n in TARGETS}, m.label

def fresh_tests():
    if "test_two_pass_verify1" in sys.modules:
        return importlib.reload(sys.modules["test_two_pass_verify1"])
    import test_two_pass_verify1 as t
    return t

# 검산 0: 무변이 추출 함수로 8/8 초록인가 (러너 자체 건전성)
funcs, _ = build_mutant(-1)
t = fresh_tests()
t.results_from_claim_anchoring = funcs["results_from_claim_anchoring"]
t.stale_obligations = funcs["stale_obligations"]
base_red = [n for n in dir(t) if n.startswith("test_")
            and (lambda f: (lambda: [f()] and False)) and False]
base_red = []
for n in [x for x in dir(t) if x.startswith("test_")]:
    try: t.__dict__[n]()
    except Exception: base_red.append(n)
print(f"검산0 무변이 대조군: {len(base_red)} 빨강 {base_red}")
assert not base_red, "러너 자체가 병들었다 — 측정 중단"

N = count_sites()
killed, survived, execfail = [], [], []
for idx in range(N):
    try:
        funcs, label = build_mutant(idx)
    except Exception as e:
        execfail.append((idx, str(e)[:60])); continue
    t = fresh_tests()
    t.results_from_claim_anchoring = funcs["results_from_claim_anchoring"]
    t.stale_obligations = funcs["stale_obligations"]
    red = []
    for n in [x for x in dir(t) if x.startswith("test_")]:
        try: t.__dict__[n]()
        except Exception: red.append(n)
    (killed if red else survived).append((idx, label, len(red)))

print(f"뮤턴트 {N} | killed {len(killed)} | survived {len(survived)} | exec실패 {len(execfail)}")
if N: print(f"kill rate: {len(killed)/N*100:.0f}% (exec실패는 kill 로 세지 않음)")
print("killed 내역:", [(i, l, r) for i, l, r in killed])
print("SURVIVORS:", [(i, l) for i, l, _ in survived])
print("EXEC실패:", execfail)
