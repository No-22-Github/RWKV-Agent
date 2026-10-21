"""b21f (v2.1: logs counted with bash) shared framework.

Events are generated structurally, rendered in one of four log formats, and the
answer is computed from the structure. verify.py re-parses the fixture text with
regexes (a different path) and pins the fixture hash. Every case also registers
a bash reference that build.py replays in the just-bash sidecar.
"""
import datetime as dt
import hashlib
import json
import os
import re
import sys
from random import Random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from casegen import Batch, Sidecar, check_reference, lines  # noqa: E402,F401

BATCH = Batch(salt="b21f", author="llm:claude-sonnet-b21f", version="v2.1", tool_catalog="agent-tool-v2.0")
EXTRA = {"batch": "b21f"}
META = {}
REFS = {}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
NOCALC = ["calculator", "data_query"]
READERS = ["read_file", "read_lines", "search_text"]


def is_zh(text):
    return len(re.findall(r"[一-鿿]", text)) >= 4


def level_for(n_traps, ref_calls, n_files, multi):
    allowed = []
    if n_traps == 0 and ref_calls <= 3:
        allowed.append("L0")
    if n_traps == 1 and ref_calls <= 4:
        allowed.append("L1")
    if n_traps == 2 or (n_traps == 1 and (n_files >= 3 or ref_calls >= 5)):
        allowed.append("L2")
    if n_traps >= 3 or (multi and n_traps >= 1) or ref_calls >= 8:
        allowed.append("L3")
    return allowed[0]


_VOCAB = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "workbank", "tag-vocab.json")))
TRAP_AXIS = {k: v.get("axis") for k, v in _VOCAB["traps"].items()}


def pin(files):
    d = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return ("import hashlib, json, re\n"
            "case = json.load(open(\"case.json\"))\n"
            "_pin = hashlib.sha256(json.dumps(case[\"files\"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()\n"
            "assert _pin == %r, \"fixture changed\"\n" % d)


# ---------------------------------------------------------------- events

class Ev:
    __slots__ = ("ts", "level", "svc", "path", "method", "status", "dur", "size", "rid", "ip", "msg", "extra")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))


def gen_times(rng, n, start, span_s):
    """n sorted timestamps (ms precision) inside [start, start+span_s)."""
    ms = sorted(rng.sample(range(span_s * 1000), n))
    return [start + dt.timedelta(milliseconds=m) for m in ms]


def rid(rng, prefix="r"):
    return "%s-%s" % (prefix, "".join(rng.choice("0123456789abcdef") for _ in range(6)))


def ipaddr(rng, pool=None):
    if pool:
        return rng.choice(pool)
    return "%d.%d.%d.%d" % (rng.choice([10, 172, 192, 203]), rng.randint(0, 255), rng.randint(0, 255), rng.randint(2, 250))


# ---------------------------------------------------------------- rendering

def r_nginx(e):
    t = e.ts
    return '%s - - [%02d/%s/%d:%02d:%02d:%02d +0800] "%s %s HTTP/1.1" %d %d "-" "%s" rt=%.3f rid=%s' % (
        e.ip, t.day, MON[t.month - 1], t.year, t.hour, t.minute, t.second, e.method, e.path, e.status, e.size,
        e.extra or "curl/8.1", e.dur / 1000.0, e.rid)


def r_json(e):
    t = e.ts
    return ('{"ts":"%s.%03d+08:00","level":"%s","svc":"%s","method":"%s","path":"%s","status":%d,"dur_ms":%d,"bytes":%d,"req_id":"%s","msg":"%s"}'
            % (t.strftime("%Y-%m-%dT%H:%M:%S"), t.microsecond // 1000, e.level, e.svc, e.method, e.path, e.status, e.dur, e.size, e.rid, e.msg))


def r_kv(e):
    t = e.ts
    return 'ts=%s.%03d level=%s svc=%s method=%s path=%s status=%d dur_ms=%d bytes=%d req=%s msg="%s"' % (
        t.strftime("%Y-%m-%dT%H:%M:%S"), t.microsecond // 1000, e.level.lower(), e.svc, e.method, e.path, e.status, e.dur, e.size, e.rid, e.msg)


def r_app(e):
    t = e.ts
    return "%s.%03d [%s] %-5s %s - %s (req=%s status=%d took=%dms)" % (
        t.strftime("%Y-%m-%d %H:%M:%S"), t.microsecond // 1000, e.extra or "worker-1", e.level, e.svc, e.msg, e.rid, e.status, e.dur)


RENDER = {"nginx": r_nginx, "json": r_json, "kv": r_kv, "app": r_app}

# regexes verify.py uses to parse each format back (shipped in verify source)
PARSE_SRC = r'''
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
'''


def write_files(events_by_file, fmt):
    return {p: lines([RENDER[fmt](e) for e in evs]) for p, evs in events_by_file.items()}


# ---------------------------------------------------------------- writing

def case(cid, *, sub, desc, task_type, family, ref_calls, files, turns, verify_body, notes, traps, decoys,
         axes=(), policy=None, refs=None):
    multi = len(turns) > 1
    level = level_for(len(traps), ref_calls, len(files), multi)
    ax = list(dict.fromkeys(list(axes) + [TRAP_AXIS[t] for t in traps]))
    BATCH.write_case(cid, desc=desc, task_type=task_type, family=family, level=level, ref_calls=ref_calls,
                     files=files, turns=turns, verify=pin(files) + verify_body.strip("\n") + "\n", notes=notes,
                     traps=traps, decoys=decoys, axes=ax, tool_policy=policy, extra_tags=EXTRA)
    if refs:
        REFS[cid] = (files, refs)   # refs: one list of bash commands per turn
    META[cid] = {"sub": sub, "lang": "zh" if is_zh(" ".join(t["prompt"] for t in turns)) else "en",
                 "turns": len(turns), "policy": policy, "level": level}


def policy(i, nocalc):
    p = {"must_offer": ["bash", READERS[i % 3]]}
    if nocalc:
        p["never_offer"] = list(NOCALC)
    return p


def turn(prompt, contains, token=True):
    ex = {"required_tools": ["bash"], "output_contains": list(contains)}
    if token:
        ex["output_contains_token"] = True
    return {"prompt": prompt, "expect": ex}


def has(*needles):
    def chk(out, _root):
        return None if all(str(n) in out for n in needles) else "ref stdout %r lacks %s" % (out[:300], needles)
    return chk
