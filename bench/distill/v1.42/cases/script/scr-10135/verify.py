# DISTILL-CANARY-55301a63 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0f39e26fc0966368e4496d1a2bd7aa51d547a8abcd8f17660663b6d2283f32f1', "fixture changed"
import json, re


def parse(fmt, text, cols, sep, header, pattern):
    out = []
    rows = text.splitlines()
    if fmt == "csv":
        if header:
            assert rows[0].split(sep) == cols, rows[0]
            rows = rows[1:]
        for line in rows:
            parts = line.split(sep)
            assert len(parts) == len(cols), line
            out.append(dict(zip(cols, parts)))
    elif fmt == "jsonl":
        for line in rows:
            out.append(json.loads(line))
    elif fmt == "kv":
        for line in rows:
            out.append(dict(tok.split("=", 1) for tok in line.split(" ")))
    elif fmt == "re":
        for line in rows:
            m = re.fullmatch(pattern, line)
            assert m, line
            out.append(m.groupdict())
    else:
        raise ValueError(fmt)
    return out


def ev(expr, r):
    return eval(expr, {"int": int, "float": float, "len": len, "str": str, "any": any, "re": re, "r": r})


def agg(q, rows):
    sel = [r for r in rows if ev(q["pred"], r)]
    kind = q["agg"]
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(ev(q["val"], r)) for r in sel)
    if kind == "sumc":
        cents = sum(int(round(float(ev(q["val"], r)) * 100)) for r in sel)
        return "%d.%02d" % (cents // 100, cents % 100)
    if kind == "distinct":
        return len({str(ev(q["val"], r)) for r in sel})
    if kind == "top":
        tally = {}
        for r in sel:
            key = str(ev(q["key"], r))
            tally[key] = tally.get(key, 0) + (int(ev(q["val"], r)) if q.get("val") else 1)
        ranked = sorted(tally.items(), key=lambda kv: -kv[1])
        if len(ranked) < 2 or ranked[0][1] - ranked[1][1] < q.get("margin", 2):
            raise ValueError("no clear leader")
        return ranked[0][0]
    if kind == "last":
        if not sel:
            raise ValueError("empty")
        return str(ev(q["val"], sel[-1]))
    raise ValueError(kind)

W = {'fmt': 'csv', 'cols': ['工号', '日期', '类型', '小时'], 'pattern': None, 'sep': ',', 'header': True}
DATA = ['工时/研发一组.csv', '工时/研发二组.csv', '工时/测试组.csv', '工时/运维组.csv']
QS = [{'agg': 'sum', 'pred': 'r["类型"]=="加班"', 'val': 'r["小时"]'}]
CHECKS = {'工时/说明.md': '# 工时'}

ALL = []
for path in DATA:
    ALL += parse(W["fmt"], case["files"][path], W["cols"], W["sep"], W["header"], W["pattern"])
for path, start in CHECKS.items():
    assert case["files"][path].startswith(start), path
vals = [agg(q, ALL if q.get("scope") is None else [r for p in q["scope"] for r in parse(W["fmt"], case["files"][p], W["cols"], W["sep"], W["header"], W["pattern"])]) for q in QS]
anyset = []
for q, v in zip(QS, vals):
    if q["agg"] not in ("top", "last"):
        s = str(v)
        whole, _, frac = s.partition(".")
        g = format(int(whole), ",") + ("." + frac if frac else "")
        if g != s:
            anyset += [s, g]
out = {}
if anyset:
    out["expected_contains_any"] = anyset
elif QS[-1]["agg"] in ("top", "last"):
    out["expected_string"] = vals[-1]
else:
    out["expected_number"] = float(vals[-1]) if "." in str(vals[-1]) else int(vals[-1])
print(json.dumps(out, ensure_ascii=False))
