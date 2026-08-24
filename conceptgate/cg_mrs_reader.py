"""MRS 텍스트 형식 → 파이썬 구조. 두 변종(LTOP/TOP, _rel 접미사)을 정규화."""
import re

class MrsSyntaxError(Exception):
    """MRS 형식이 유효하지 않음."""
    pass

class MrsUnsupported(Exception):
    """지원하지 않는 MRS 구성."""
    pass

def read_mrs(text: str) -> dict:
    """MRS 텍스트 → {top, index, eps, hcons}."""
    text = text.strip()
    if not text:
        raise MrsSyntaxError("empty input")
    if text[0] != '[' or text[-1] != ']':
        raise MrsSyntaxError("must start with [ and end with ]")
    # 괄호 균형 확인
    d = 0
    for i, c in enumerate(text):
        d += 1 if c == '[' else (-1 if c == ']' else 0)
        if d < 0 or (d == 0 and i < len(text) - 1):
            raise MrsSyntaxError("unbalanced brackets")
    if d != 0:
        raise MrsSyntaxError("unbalanced brackets")
    body = text[1:-1]
    top = _extract_field(body, ('LTOP', 'TOP'))
    index = _extract_field(body, 'INDEX')
    rels = _extract_rels(body)
    hcons = _extract_hcons(body)
    if not rels:
        raise MrsSyntaxError("missing RELS section")
    return {"top": top, "index": index, "eps": rels, "hcons": hcons}

def _extract_field(body: str, names):
    for name in (names if isinstance(names, tuple) else (names,)):
        m = re.search(name + r':\s*(\w+)', body)
        if m: return m.group(1)

def _extract_rels(body: str) -> list:
    """RELS: < [ ... ] [ ... ] ... > 파싱. <>와 <span> 구분."""
    m = re.search(r'RELS:\s*<', body)
    if not m: return []
    i = m.end()
    ad, sd = 1, 0  # angle_depth, square_depth
    # RELS: < 뒤의 대응하는 > 찾기
    while i < len(body) and ad > 0:
        if body[i] == '<' and sd == 0: ad += 1
        elif body[i] == '>' and sd == 0: ad -= 1
        elif body[i] == '[': sd += 1
        elif body[i] == ']': sd -= 1
        i += 1
    rels_str = body[m.end():i-1].strip()
    eps, j = [], 0
    while j < len(rels_str):
        if rels_str[j] == '[':
            d, k = 1, j + 1
            while k < len(rels_str) and d > 0:
                d += 1 if rels_str[k] == '[' else (-1 if rels_str[k] == ']' else 0)
                k += 1
            ep = _parse_ep(rels_str[j:k])
            if ep: eps.append(ep)
            j = k
        else: j += 1
    return eps

def _parse_ep(ep_str: str) -> dict:
    """[ pred<span> LBL: l ARG0: v ... ] 파싱."""
    parts = ep_str.strip()[1:-1].split(None, 1)  # [ ... ] 제거
    if not parts: return None
    pred, span = _parse_pred(parts[0])
    lbl, args = _parse_args(parts[1] if len(parts) > 1 else "")
    return {"pred": pred, "span": span, "lbl": lbl, "args": args}

def _parse_pred(s: str) -> tuple:
    m = re.match(r'(.+?)<(\d+):(\d+)>', s)
    if m:
        pred_raw, span = m.group(1), (int(m.group(2)), int(m.group(3)))
    else:
        pred_raw, span = s, None
    pred = pred_raw.strip('"')
    if pred.endswith('_rel'): pred = pred[:-4]  # _rel 접미사 제거
    return pred, span

def _parse_args(rest: str) -> tuple:
    """'LBL: h4 ARG0: x5 [ ... ] RSTR: h6' → (lbl, {args})."""
    lbl, args, tokens = None, {}, rest.split()
    i = 0
    while i < len(tokens):
        if tokens[i] == 'LBL:' and i + 1 < len(tokens):
            lbl, i = tokens[i + 1], i + 2
        elif tokens[i].endswith(':') and i + 1 < len(tokens):
            key, val = tokens[i][:-1], tokens[i + 1]
            if not val.startswith('['):
                # CARG 따옴표 제거
                if val.startswith('"') and val.endswith('"'): val = val[1:-1]
                args[key], i = val, i + 2
                # 값 다음에 [ 가 있으면 ] 까지 스킵
                if i < len(tokens) and tokens[i] == '[':
                    d = 1
                    for i in range(i + 1, len(tokens)):
                        d += 1 if tokens[i] == '[' else (-1 if tokens[i] == ']' else 0)
                        if d == 0: break
                    i += 1
            else: i += 2
        else: i += 1
    return lbl, args

def _extract_hcons(body: str) -> list:
    """HCONS: < h6 QEQ h8 h1 QEQ h2 > 파싱."""
    m = re.search(r'HCONS:\s*<(.+?)>', body, re.DOTALL)
    if not m: return []
    tokens, hcons, i = m.group(1).strip().split(), [], 0
    while i + 2 < len(tokens):
        if tokens[i + 1] != 'QEQ':
            raise MrsUnsupported(f"unsupported HCONS relation: {tokens[i + 1]}")
        hcons.append((tokens[i], tokens[i + 1], tokens[i + 2]))
        i += 3
    return hcons
