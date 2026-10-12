# DISTILL-CANARY-820efd75 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 1311
SEP = ','
COLS = ['时间', '传感器', '温度', '电量']
HEADER = True
DATA = ['传感器/readings.dat']
QS = [('r["传感器"]=="S-07" and float(r["温度"])>20', 'count', None), ('r["传感器"]=="S-07"', 'max', '温度')]
assert case["files"]['传感器/说明.md'].startswith('# 传感器读数说明')

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
