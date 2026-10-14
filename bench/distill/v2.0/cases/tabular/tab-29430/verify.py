# DISTILL-CANARY-2fa26d24 : distillation case
import json
case = json.load(open("case.json"))
assert sum(len(t.splitlines()) for t in case["files"].values()) == 1196
SEP = ' '
COLS = ['序号', '部门', '科目', '金额', '摘要']
HEADER = False
DATA = ['账本/流水.txt']
QS = [{'agg': 'between_sum', 'nth': 2, 'col': '金额', 'start': 'r["部门"]=="段" and r["科目"]=="第二季度开始"', 'end': 'r["部门"]=="段" and r["科目"]=="第二季度结束"', 'pred': 'r["部门"]=="财务部"', 'sep': ' '}]
assert case["files"]['账本/说明.md'].startswith('# 费用流水说明')

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
    if kind == "between_sum":
        k, state, tot, cnt = 0, 0, 0, 0
        for n, r in rows:
            if state == 0:
                if ev(q["start"], r):
                    k += 1
                    state = 1 if k == q.get("nth", 1) else 0
            elif ev(q["end"], r):
                state = 2
                break
            elif ev(q["pred"], r):
                tot += int(r[q["col"]])
                cnt += 1
        if state != 2 or cnt == 0:
            raise ValueError("no window")
        return tot
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
    if kind == "nth_line":
        if len(sel) < q["nth"] + 2:
            raise ValueError("too few")
        return sel[q["nth"] - 1][0]
    if kind == "longest_line":
        ranked = sorted(((len(q["sep"].join(r.values())), n) for n, r in sel), reverse=True)
        if len(ranked) < 2 or ranked[0][0] == ranked[1][0]:
            raise ValueError("tie")
        return ranked[0][1]
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
vals = [agg(q["agg"], q, ALL) for q in QS]
out = {}
sums = []
for q, val in zip(QS, vals):
    if q["agg"] in ("sum", "between_sum"):
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
elif QS[-1]["agg"] not in ("sum", "between_sum"):
    out["expected_number"] = int(last) if isinstance(last, float) and last == int(last) else last
print(json.dumps(out, ensure_ascii=False))
