# DISTILL-CANARY-3a2436d6 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 1347
SEP = ' '
COLS = ['时间', '大棚', '设备', '事件', '备注']
HEADER = False
DATA = ['温室/记录.txt']
QS = [{'agg': 'distinct', 'col': '设备', 'pred': 'r["大棚"]=="3号" and r["事件"]=="告警"', 'minus': None}, {'agg': 'distinct', 'col': '设备', 'pred': 'r["大棚"]=="3号" and r["事件"]=="维护"', 'minus': None}]
assert case["files"]['温室/说明.md'].startswith('# 温室传感器记录说明')

def agg(kind, q, rows):
    ev = lambda p, r: eval(p, {"int": int, "float": float}, {"r": r})
    if kind == "between":
        k, state, out = 0, 0, []
        for n, r in rows:
            if state == 0:
                if ev(q["start"], r):
                    k += 1
                    state = 1 if k == q.get("nth", 1) else 0
            elif ev(q["end"], r):
                state = 2
                break
            elif ev(q["pred"], r):
                out.append(n)
        if state != 2:
            raise ValueError("no window")
        return len(out)
    sel = [(n, r) for n, r in rows if ev(q["pred"], r)]
    if not sel:
        raise ValueError("empty")
    col = q.get("col")
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(r[col]) for _, r in sel)
    if kind == "max":
        return max(float(r[col]) for _, r in sel)
    if kind == "min":
        return min(float(r[col]) for _, r in sel)
    if kind == "distinct":
        return len({r[col] for _, r in sel})
    if kind == "first_line":
        return min(n for n, _ in sel)
    if kind == "last_line":
        return max(n for n, _ in sel)
    if kind == "top":
        tot = {}
        for _, r in sel:
            tot[r[q["group"]]] = tot.get(r[q["group"]], 0) + (int(r[col]) if col else 1)
        ranked = sorted(tot.items(), key=lambda kv: -kv[1] if q.get("extreme", "max") == "max" else kv[1])
        if len(ranked) < 2 or abs(ranked[0][1] - ranked[1][1]) < q.get("margin", 1):
            raise ValueError("no clear leader")
        return ranked[0][0]
    if kind == "top_n":
        tot = {}
        for _, r in sel:
            tot[r[q["group"]]] = tot.get(r[q["group"]], 0) + (int(r[col]) if col else 1)
        return max(tot.values()) if q.get("extreme", "max") == "max" else min(tot.values())
    if kind in ("argtie", "argtie_first", "argtie_n"):
        pick = max if q.get("extreme", "max") == "max" else min
        best = pick(float(r[col]) for _, r in sel)
        cands = [(n, r) for n, r in sel if float(r[col]) == best]
        if len(cands) < 2 or len({r[q["ret"]] for _, r in cands}) < 2:
            raise ValueError("no tie")
        if kind == "argtie_first":
            return cands[0][1][q["ret"]]
        if kind == "argtie_n":
            return len(sel)
        tp = min if q.get("tie_pick", "min") == "min" else max
        tv = tp(r[q["tie_col"]] for _, r in cands)
        win = [r for _, r in cands if r[q["tie_col"]] == tv]
        if len(win) != 1:
            raise ValueError("tie rule not decisive")
        return win[0][q["ret"]]
    raise ValueError(kind)


def agg2(q, over, rows, prev):
    # over: extra keys (decoy) merged into q; a "minus" index makes the answer the absolute gap to that earlier turn's answer
    qq = {**q, **over}
    base = agg(qq["agg"], qq, rows)
    if q.get("minus") is not None:
        return abs(base - prev[q["minus"]])
    return base

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
vals = []
for q in QS:
    vals.append(agg2(q, {}, ALL, vals))
out = {}
sums = []
for q, val in zip(QS, vals):
    if q["agg"] == "sum" and q.get("minus") is None:
        sums += [str(val)] + ([format(val, ",")] if val >= 1000 else [])
if sums:
    out["expected_contains_any"] = sums
last = vals[-1]
if isinstance(last, str):
    out["expected_string"] = last
    extra = agg(QS[-1]["agg"] + "_n", QS[-1], ALL)
    if extra >= 1000:
        out["expected_contains_any"] = [str(extra), format(extra, ",")]
    else:
        out["expected_number"] = extra
elif QS[-1]["agg"] != "sum" or QS[-1].get("minus") is not None:
    out["expected_number"] = int(last) if isinstance(last, float) and last == int(last) else last
print(json.dumps(out, ensure_ascii=False))
