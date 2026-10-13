# DISTILL-CANARY-69e3b30d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '024dd7d77501aff299bc8b81fa26a3e91ab12a7c91b44972572d6b3ed45c008c', "fixture changed"
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

W = {'fmt': 'csv', 'cols': ['工单号', '渠道', '类别', '状态', '处理人', '时长分钟'], 'pattern': None, 'sep': ',', 'header': True}
DATA = ['客服/工单导出/2026-W27.csv', '客服/工单导出/2026-W28.csv', '客服/工单导出/2026-W29.csv', '客服/工单导出/2026-W30.csv', '客服/工单导出/2026-W31.csv', '客服/工单导出/2026-W32.csv', '客服/工单导出/2026-W33.csv', '客服/工单导出/2026-W34.csv', '客服/工单导出/2026-W35.csv', '客服/工单导出/2026-W36.csv', '客服/工单导出/2026-W37.csv', '客服/工单导出/2026-W38.csv']
QS = [{'agg': 'top', 'pred': 'r["状态"]=="已升级"', 'key': 'r["处理人"]'}]
CHECKS = {'客服/工单导出/说明.md': '# 工单导出说明'}

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
