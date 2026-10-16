# DISTILL-CANARY-abf2dbfd : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c78a9ac45021e410acee1c8c2d6c892a196d9cf606b3f9daf117324e659769e9', "fixture changed"
FMT = 'json'
SPECS = [{'k': 'count', 'conds': {'status': 502, 'path': '/shop/buy'}, 'first': True, 'last': False, 'window': {'lo': '2026-09-15 17:00:00.000', 'hi': '2026-09-15 19:00:00.000', 'lo_incl': False, 'hi_incl': True}, 'hm': True}]

MONS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
def parse(line, fmt):
    import datetime as dt
    if fmt == "nginx":
        m = re.match(r'^(\S+) - - \[(\d+)/(\w+)/(\d+):(\d+):(\d+):(\d+) \+0800\] "(\w+) (\S+) HTTP/1.1" (\d+) (\d+) "-" "([^"]*)" rt=([\d.]+) rid=(\S+)$', line)
        ip, d, mo, y, H, M, S, meth, path, st, sz, ua, rt, rid = m.groups()
        return dict(ts=dt.datetime(int(y), MONS.index(mo) + 1, int(d), int(H), int(M), int(S)), ip=ip, method=meth, path=path,
                    status=int(st), size=int(sz), dur=round(float(rt) * 1000), rid=rid, level="", svc="", msg="")
    if fmt == "json":
        o = json.loads(line)
        t = dt.datetime.strptime(o["ts"][:23], "%Y-%m-%dT%H:%M:%S.%f")
        return dict(ts=t, level=o["level"], svc=o["svc"], method=o["method"], path=o["path"], status=o["status"],
                    dur=o["dur_ms"], size=o["bytes"], rid=o["req_id"], msg=o["msg"], ip="")
    if fmt == "kv":
        m = re.match(r'^ts=(\S+) level=(\w+) svc=(\S+) method=(\w+) path=(\S+) status=(\d+) dur_ms=(\d+) bytes=(\d+) req=(\S+) msg="(.*)"$', line)
        ts, lv, svc, meth, path, st, dur, sz, rq, msg = m.groups()
        return dict(ts=dt.datetime.strptime(ts[:23], "%Y-%m-%dT%H:%M:%S.%f"), level=lv.upper(), svc=svc, method=meth, path=path,
                    status=int(st), dur=int(dur), size=int(sz), rid=rq, msg=msg, ip="")
    if fmt == "app":
        m = re.match(r'^(\S+ \S+) \[(\S+)\] (\w+)\s+(\S+) - (.*) \(req=(\S+) status=(\d+) took=(\d+)ms\)$', line)
        ts, th, lv, svc, msg, rq, st, dur = m.groups()
        return dict(ts=dt.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.%f"), level=lv, svc=svc, msg=msg, rid=rq, status=int(st),
                    dur=int(dur), method="", path="", size=0, ip="")
    raise ValueError(fmt)

def load(path_prefix_filter=None):
    out = []
    for p, text in case["files"].items():
        if p.endswith(".md") or p.endswith(".txt"):
            continue
        fmt = FMT[p] if isinstance(FMT, dict) else FMT
        for ln in text.splitlines():
            if ln.strip():
                ev = parse(ln, fmt); ev["file"] = p; out.append(ev)
    return out

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

for i, spec in enumerate(SPECS):
    toks = answer(spec)
    have = case["turns"][i]["expect"]["output_contains"]
    assert toks == have, (i, toks, have)
print(json.dumps({"expected_string": answer(SPECS[0])[0]}, ensure_ascii=False))
