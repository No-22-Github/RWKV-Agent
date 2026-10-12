# DISTILL-CANARY-a78b346e : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 707
SEP = '\t'
COLS = ['时间', '卡号', '窗口', '金额']
HEADER = True
DATA = ['食堂/周一.txt', '食堂/周二.txt', '食堂/周三.txt']
QS = [('r["窗口"]=="3号窗口"', 'sum', '金额')]
assert case["files"]['食堂/说明.md'].startswith('# 食堂刷卡记录说明')

def table(path):
    out = []
    for n, line in enumerate(case["files"][path].splitlines(), 1):
        parts = line.split(SEP)
        if HEADER and n == 1:
            assert parts == COLS, path
            continue
        assert len(parts) == len(COLS), (path, n, line)
        out.append((n, dict(zip(COLS, parts))))
    return out

ALL = [x for p in DATA for x in table(p)]

def agg(kind, col, pred):
    sel = [(n, r) for n, r in ALL if eval(pred, {"int": int, "float": float}, {"r": r})]
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(r[col]) for _, r in sel)
    if kind == "max":
        return max(float(r[col]) for _, r in sel)
    if kind == "distinct":
        return len({r[col] for _, r in sel})
    if kind == "first_line":
        return min(n for n, _ in sel)
    return max(n for n, _ in sel)

vals = [agg(k, col, p) for p, k, col in QS]
out = {}
anyv = []
for (p, k, col), val in zip(QS, vals):
    if k == "sum":
        anyv += [str(val)] + ([format(val, ",")] if val >= 1000 else [])
if anyv:
    out["expected_contains_any"] = anyv
nums = [val for (p, k, col), val in zip(QS, vals) if k != "sum"]
if nums:
    v = nums[-1]
    out["expected_number"] = int(v) if isinstance(v, float) and v == int(v) else v
print(json.dumps(out))
