"""32101-32112: count by several conditions, with a substring trap."""
import datetime as dt
from random import Random

from gen import PATHS, SVCS, g_level, g_path, g_status, g_svc, make_events
from lib import run_answers
from mk import make

B = []


def greps(fmt, conds):
    out = [g_status(fmt, conds["status"])]
    if "path" in conds:
        out.append(g_path(fmt, conds["path"]))
    if "svc" in conds:
        out.append(g_svc(fmt, conds["svc"]))
    if "level" in conds:
        out.append(g_level(fmt, conds["level"]))
    return out


def naive(text, conds):
    n = 0
    for ln in text.splitlines():
        if all(str(v) in ln for v in conds.values()):
            n += 1
    return n


def focus_of(c1, c2):
    f = {"path": [], "svc": []}
    for c in (c1, c2):
        if c:
            for k in f:
                if k in c:
                    f[k].append(c[k])
    return f


def count_case(i, *, fmt, vi, code, c1, c2, fpath, first, last, lang_zh, prompts, nocalc, ms=False, n=400):
    cid = "log-%d" % (32101 + i)

    def build():
        for tries in range(60):
            rng = Random(32101 * 31 + i * 7919 + tries)
            day = dt.datetime(2026, 9, 15, 8, 0, 0)
            evs = {fpath: make_events(rng, n, day, 9 * 3600, fmt, vi, code=code, code_rate=0.14, focus=focus_of(c1, c2))}
            specs = [dict(k="count", conds=c1, first=first, last=last, files=None)]
            if c2:
                specs.append(dict(k="count", conds=c2, first=first, last=last))
            try:
                # counts must be sizeable and the naive substring count different
                from common import write_files
                files = write_files(evs, fmt)
                toks = run_answers(files, fmt, specs)
            except IndexError:
                continue
            if all(int(t[0]) >= 12 for t in toks) and all(naive(files[fpath], s["conds"]) != int(t[0]) for s, t in zip(specs, toks)):
                break
        else:
            raise SystemExit("no seed for " + cid)
        text = files[fpath]
        decoys = {"TR-DECOY": str(naive(text, c1))}
        cmds = []
        for c in [c1] + ([c2] if c2 else []):
            base = "cat %s | " % fpath + " | ".join(greps(fmt, c))
            cmds.append([base + " | wc -l"] + ([base + " | head -1"] if first else []) + ([base + " | tail -1"] if last else []))
        make(cid, i, sub="count", fmt=fmt, evs=evs, specs=specs, prompts=prompts, refs=cmds,
             traps=["TR-DECOY"], decoys=decoys, nocalc=nocalc,
             desc="Counts log lines matching a status code plus another field where the code also appears inside other fields",
             notes_traps="- TR-DECOY: the status code %d also appears inside durations, byte counts and paths on other lines; a plain substring grep over-counts (%s lines)." % (code, decoys["TR-DECOY"]),
             notes_ref="cat %s | %s | wc -l  (exact field patterns, one grep per condition)." % (fpath, " | ".join(greps(fmt, c1))))
    B.append(build)


P = PATHS
S = SVCS
count_case(0, fmt="nginx", vi=0, code=404, c1=dict(status=404, path=P[0][1]), c2=dict(status=404, path=P[0][2]),
           fpath="logs/access.log", first=True, last=False, lang_zh=True, nocalc=False,
           prompts=["看一下 logs/access.log，返回 404 的请求里，访问 %s 的有多少条？最早的一条是几点几分几秒？" % P[0][1],
                    "那把路径换成 %s，同样的问题再答一遍。" % P[0][2]])
count_case(1, fmt="json", vi=1, code=503, c1=dict(status=503, svc=S[1][1]), c2=None,
           fpath="export/gw-20260915.jsonl", first=True, last=False, lang_zh=True, nocalc=True,
           prompts=["export/gw-20260915.jsonl 是网关导出的日志。status 为 503 并且服务是 %s 的记录一共有多少条？最早一条出现在几点？" % S[1][1]])
count_case(2, fmt="kv", vi=2, code=500, c1=dict(status=500, path=P[2][1], level="ERROR"), c2=None,
           fpath="var/log/shop/edge.log", first=True, last=False, lang_zh=False, nocalc=False,
           prompts=["In var/log/shop/edge.log, how many requests to %s came back with status 500 at ERROR level? Also tell me the time of the earliest one." % P[2][1]])
count_case(3, fmt="app", vi=3, code=502, c1=dict(status=502, svc=S[3][1]), c2=dict(status=502, svc=S[3][2]),
           fpath="app/worker.log", first=False, last=True, lang_zh=True, nocalc=False,
           prompts=["app/worker.log 里，%s 这个组件报 status=502 的有多少次？最后一次是几点几分几秒？" % S[3][1],
                    "再看 %s 组件，同样是 502，次数和最后一次的时间呢？" % S[3][2]])
count_case(4, fmt="json", vi=0, code=429, c1=dict(status=429, path=P[0][3], level="WARN"), c2=dict(status=429, svc=S[0][2], level="WARN"),
           fpath="logs/api-0915.jsonl", first=True, last=False, lang_zh=False, nocalc=True,
           prompts=["Check logs/api-0915.jsonl: how many WARN records have status 429 on path %s, and what time was the first one?" % P[0][3],
                    "Now the same question for service %s instead of that path (still status 429 at WARN)." % S[0][2]])
count_case(5, fmt="kv", vi=1, code=404, c1=dict(status=404, svc=S[1][3], level="WARN"), c2=None,
           fpath="logs/session-edge.log", first=False, last=True, lang_zh=True, nocalc=False,
           prompts=["logs/session-edge.log 里服务 %s 级别 warn、status 是 404 的请求有多少个？最后一个是几点几分几秒出现的？" % S[1][3]])
count_case(6, fmt="nginx", vi=2, code=502, c1=dict(status=502, path=P[2][2]), c2=None,
           fpath="srv/nginx/access.log", first=True, last=False, lang_zh=False, nocalc=True,
           prompts=["srv/nginx/access.log: count the 502 responses for %s and give me the time of the first one." % P[2][2]])
count_case(7, fmt="app", vi=2, code=500, c1=dict(status=500, svc=S[2][4]), c2=None,
           fpath="logs/ledger-app.log", first=True, last=False, lang_zh=True, nocalc=False, ms=False,
           prompts=["logs/ledger-app.log 里 %s 的 status=500 一共出现几次？第一次是几点？" % S[2][4]])
count_case(8, fmt="json", vi=3, code=401, c1=dict(status=401, path=P[3][4]), c2=dict(status=401, path=P[3][0]),
           fpath="data/edge-0915.jsonl", first=True, last=False, lang_zh=True, nocalc=True,
           prompts=["data/edge-0915.jsonl 里访问 %s 且 status 为 401 的记录有多少条？最早的一条是几点？" % P[3][4],
                    "换成 %s 呢？" % P[3][0]])
count_case(9, fmt="kv", vi=3, code=429, c1=dict(status=429, svc=S[3][0]), c2=None,
           fpath="logs/rate.log", first=True, last=False, lang_zh=False, nocalc=False,
           prompts=["In logs/rate.log, how many lines are status 429 from the %s service? Tell me when the first one happened." % S[3][0]])
count_case(10, fmt="nginx", vi=1, code=500, c1=dict(status=500, path=P[1][1]), c2=dict(status=500, path=P[1][3]),
           fpath="www/log/access.log", first=False, last=True, lang_zh=True, nocalc=False,
           prompts=["www/log/access.log 中请求 %s 返回 500 的有多少条？最后一条是几点几分几秒？" % P[1][1],
                    "只看 %s 的话，是多少条，最后一条几点？" % P[1][3]])
count_case(11, fmt="app", vi=1, code=503, c1=dict(status=503, svc=S[1][0]), c2=dict(status=503, svc=S[1][2]),
           fpath="logs/gateway-app.log", first=True, last=False, lang_zh=False, nocalc=True,
           prompts=["In logs/gateway-app.log, how many entries from %s have status=503, and when was the first one?" % S[1][0],
                    "Same question for the %s component." % S[1][2]])
