"""32133-32140: counts and rankings that span rotated or per-day files."""
import datetime as dt
from random import Random

from common import write_files
from gen import PATHS, SVCS, cond_greps, extract, make_events
from lib import run_answers
from m_top import IPP
from mk import make

B = []
D = dt.datetime


def cross_case(i, *, fmt, vi, paths, starts, span_h, nper, specs, prompts, nocalc, code=None, focus=None, skew=None, traps=None):
    i += 32
    cid = "log-%d" % (32101 + i)

    def build():
        for tries in range(200):
            rng = Random(32101 * 11 + i * 7433 + tries)
            ips = IPP[vi % 3]
            evs = {}
            for p, st in zip(paths, starts):
                es = make_events(rng, nper, st, int(span_h * 3600) - 1, fmt, vi, code=code, code_rate=0.2 if code else 0.08,
                                 focus=focus, ips=ips)
                for e in es:
                    r = rng.random()
                    if skew == "ip":
                        e.ip = ips[int(r ** 2 * len(ips))]
                    elif skew in ("path", "svc"):
                        pool = PATHS[vi % 4] if skew == "path" else SVCS[vi % 4]
                        setattr(e, skew, pool[int(r ** 1.7 * len(pool))])
                evs[p] = es
            files = write_files(evs, fmt)
            try:
                toks = run_answers(files, fmt, specs)
                if specs[0]["k"] == "count" and not all(int(t[0]) >= 12 for t in toks):
                    continue
            except (AssertionError, IndexError):
                continue
            break
        else:
            raise SystemExit("no seed " + cid)
        cmds = []
        for s in specs:
            used = [p for p in paths if s.get("files") is None or p in s["files"]]
            cat = "cat %s | " % " ".join(used)
            flt = " | ".join(cond_greps(fmt, s["conds"]))
            if s["k"] == "count":
                tail = " | wc -l"
                c = [cat + flt + tail]
                if s.get("first"):
                    c.append(cat + flt + " | head -1")
                if s.get("last"):
                    c.append(cat + flt + " | tail -1")
            else:
                c = [cat + flt + " | " + extract(fmt, s["by"]) + " | sort | uniq -c | sort -rn | head -n %d" % s["n"]]
            cmds.append(c)
        make(cid, i, sub="cross", fmt=fmt, evs=evs, specs=specs, prompts=prompts, refs=cmds,
             traps=traps or ["TR-MULTISRC", "TR-DECOY"], decoys={"TR-MULTISRC": "answer from the newest file only", "TR-DECOY": "plain substring grep"},
             nocalc=nocalc, desc="Counts or ranks log events over several rotated or per-day files where one file alone gives a plausible partial answer",
             notes_traps="- TR-MULTISRC: the matching lines are spread over every file; any single file gives a partial count.\n- TR-DECOY: status codes also occur inside durations, byte counts and paths.",
             notes_ref="cat the files oldest first, filter with exact field patterns, then wc -l / sort | uniq -c | sort -rn | head.")
    B.append(build)


P, S = PATHS, SVCS
d = lambda day, h=8: D(2026, 9, day, h, 0, 0)
cross_case(0, fmt="app", vi=0, paths=["logs/app.log.2", "logs/app.log.1", "logs/app.log"], starts=[d(13), d(14), d(15)], span_h=10, nper=240,
           specs=[dict(k="count", conds=dict(level="ERROR", svc=S[0][1]), first=True)], focus={"svc": [S[0][1]]}, code=500, nocalc=False,
           prompts=["logs 目录下 app.log 已经轮转成了 app.log、app.log.1、app.log.2（数字越大越旧）。三个文件里一共有多少条 %s 组件的 ERROR？最早的一条是几点几分几秒？" % S[0][1]])
cross_case(1, fmt="json", vi=1, paths=["export/gw-0913.jsonl", "export/gw-0914.jsonl", "export/gw-0915.jsonl"], starts=[d(13), d(14), d(15)], span_h=9, nper=200,
           specs=[dict(k="count", conds=dict(status=503), first=True), dict(k="count", conds=dict(status=503), first=True, files=["export/gw-0914.jsonl", "export/gw-0915.jsonl"])],
           code=503, nocalc=True,
           prompts=["export has one JSONL file per day (gw-0913 to gw-0915). How many records with status 503 are there in total, and when was the earliest one?",
                    "Leave out the 13th and answer again."])
cross_case(2, fmt="kv", vi=2, paths=["var/log/pay.log.1", "var/log/pay.log"], starts=[d(14, 14), d(15, 8)], span_h=14, nper=300,
           specs=[dict(k="count", conds=dict(status=500, path=P[2][1]), last=True)], code=500, focus={"path": [P[2][1]]}, nocalc=False,
           prompts=["var/log/pay.log 轮转过一次，旧的在 pay.log.1。两个文件里访问 %s 且 status=500 的请求一共多少条？最后一条是几点几分几秒？" % P[2][1]])
cross_case(3, fmt="nginx", vi=3, paths=["logs/access-0913.log", "logs/access-0914.log", "logs/access-0915.log"], starts=[d(13), d(14), d(15)], span_h=10, nper=220,
           specs=[dict(k="count", conds=dict(status=404, path=P[3][1]), first=True), dict(k="count", conds=dict(status=404, path=P[3][1]), first=True, files=["logs/access-0913.log", "logs/access-0915.log"])],
           code=404, focus={"path": [P[3][1]]}, nocalc=False,
           prompts=["logs 目录里按天放了三个 access 日志（13、14、15 号）。三天加起来，访问 %s 返回 404 的有多少条？最早一条是几点几分几秒？" % P[3][1],
                    "不算 14 号，只看 13 号和 15 号，结果是多少？最早的一条呢？"])
cross_case(4, fmt="json", vi=2, paths=["data/shop.jsonl.1", "data/shop.jsonl"], starts=[d(14, 12), d(15, 8)], span_h=14, nper=320,
           specs=[dict(k="top", conds=dict(level="ERROR"), by="path", n=3)], skew="path", nocalc=True, traps=["TR-MULTISRC"],
           prompts=["data/shop.jsonl 和轮转出来的 data/shop.jsonl.1 一起看，ERROR 记录里出错最多的前三个路径是什么？各多少条？"])
cross_case(5, fmt="app", vi=3, paths=["logs/svc.log.2", "logs/svc.log.1", "logs/svc.log"], starts=[d(13), d(14), d(15)], span_h=9, nper=210,
           specs=[dict(k="top", conds=dict(level="ERROR"), by="msg", n=2), dict(k="top", conds=dict(level="ERROR"), by="msg", n=2, files=["logs/svc.log"])],
           nocalc=False, traps=["TR-MULTISRC"],
           prompts=["The service log was rotated into svc.log, svc.log.1 and svc.log.2 under logs/. Across the three files, which two ERROR messages are most frequent, and how many times does each occur?",
                    "Same question, but only for the current svc.log."])
cross_case(6, fmt="kv", vi=0, paths=["logs/api-0912.log", "logs/api-0913.log", "logs/api-0914.log", "logs/api-0915.log"], starts=[d(12), d(13), d(14), d(15)], span_h=8, nper=170,
           specs=[dict(k="count", conds=dict(status=429), last=True)], code=429, nocalc=True,
           prompts=["There are four daily files in logs/ (api-0912.log through api-0915.log). How many status=429 lines are there in total? What time was the last one?"])
cross_case(7, fmt="nginx", vi=1, paths=["srv/access.log.1", "srv/access.log"], starts=[d(14, 10), d(15, 8)], span_h=13, nper=300,
           specs=[dict(k="top", conds=dict(status=502), by="ip", n=3), dict(k="top", conds=dict(status=500), by="ip", n=3)],
           code=502, skew="ip", nocalc=False,
           prompts=["srv/access.log 和 srv/access.log.1 两个文件里，返回 502 的请求来自哪三个 IP 最多？各多少次？",
                    "换成 500 呢？"])
