"""Answer evaluator shared by build.py (to fix expect) and every verify.py."""
import json

from common import PARSE_SRC

ANSWER_SRC = r'''
HM = [False]
def hms(r, ms):
    if HM[0]: return r["ts"].strftime("%H:%M")
    s = r["ts"].strftime("%H:%M:%S")
    return s + (".%03d" % (r["ts"].microsecond // 1000) if ms else "")

def recs_of(spec):
    rs = [r for r in load() if spec.get("files") is None or r["file"] in spec["files"]]
    rs.sort(key=lambda r: r["ts"])
    return rs

def match(r, conds):
    for k, v in conds.items():
        if k == "dur_gt":
            if not r["dur"] > v: return False
        elif k == "msg_has":
            if v not in r["msg"]: return False
        elif r[k] != v:
            return False
    return True

def in_window(r, w):
    if not w: return True
    t = r["ts"].strftime("%Y-%m-%d %H:%M:%S.") + "%03d" % (r["ts"].microsecond // 1000)
    lo, hi = w["lo"], w["hi"]
    if not (t >= lo if w.get("lo_incl", True) else t > lo): return False
    return t <= hi if w.get("hi_incl", False) else t < hi

def answer(spec):
    HM[0] = bool(spec.get("hm"))
    k = spec["k"]
    rs = [r for r in recs_of(spec) if match(r, spec.get("conds", {})) and in_window(r, spec.get("window"))]
    ms = spec.get("ms", False)
    if k == "count":
        toks = [str(len(rs))]
        if spec.get("first"): toks.append(hms(rs[0], ms))
        if spec.get("last"): toks.append(hms(rs[-1], ms))
        return toks
    if k == "top":
        cnt = {}
        for r in rs:
            cnt[r[spec["by"]]] = cnt.get(r[spec["by"]], 0) + 1
        order = sorted(cnt.items(), key=lambda kv: -kv[1])
        n = spec["n"]
        assert len(order) > n and order[n - 1][1] > order[n][1], order[: n + 1]
        assert len({c for _, c in order[:n]}) == n, order[:n]
        toks = []
        for key, c in order[:n]:
            toks += [str(key), str(c)]
        return toks
    if k == "slowest":
        order = sorted(rs, key=lambda r: -r["dur"])
        n = spec["n"]
        assert order[n - 1]["dur"] > order[n]["dur"], [r["dur"] for r in order[: n + 1]]
        toks = []
        for r in order[:n]:
            toks += [r["rid"]] + ([] if spec.get("rid_only") else [str(r["dur"])])
        return toks
    if k == "firstafter":
        allr = recs_of(spec)
        mark = [r for r in allr if match(r, spec["find"])][0]
        then = [r for r in allr if r["ts"] > mark["ts"] and match(r, spec["then"])][0]
        return [mark["rid"], hms(mark, ms), then["rid"], hms(then, ms)]
    if k == "firstbefore":
        allr = recs_of(spec)
        find = [r for r in allr if match(r, spec["find"])]
        first = find[0]
        prev = [r for r in allr if r["ts"] < first["ts"] and match(r, spec["before"])]
        toks = [first["rid"], hms(first, ms), prev[-1]["rid"]]
        if spec.get("prev_time"): toks.append(hms(prev[-1], ms))
        return toks
    if k == "distinct":
        vals = sorted({r[spec["by"]] for r in rs})
        return [str(len(vals))] + ([vals[0]] if spec.get("first_val") else [])
    raise ValueError(k)
'''


def run_answers(files, fmt, specs):
    """Executes the verify-side evaluator on the fixture; returns token lists."""
    import re
    ns = {"re": re, "json": json, "case": {"files": files}, "FMT": fmt}
    exec(PARSE_SRC + ANSWER_SRC, ns)
    return [ns["answer"](s) for s in specs]


def verify_body(fmt, specs):
    return ("FMT = %r\nSPECS = %r\n" % (fmt, specs) + PARSE_SRC + ANSWER_SRC + '''
for i, spec in enumerate(SPECS):
    toks = answer(spec)
    have = case["turns"][i]["expect"]["output_contains"]
    assert toks == have, (i, toks, have)
print(json.dumps({"expected_string": answer(SPECS[0])[0]}, ensure_ascii=False))
''')
