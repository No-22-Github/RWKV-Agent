"""32123-32132: group by a field and rank the top N."""
import datetime as dt
from random import Random

from common import write_files
from gen import PATHS, SVCS, cond_greps, extract, ipaddr, make_events
from lib import run_answers
from mk import make

B = []
IPP = [["198.51.100.%d" % k for k in (7, 23, 41, 58, 77, 90, 112, 140, 163, 201)],
       ["203.0.113.%d" % k for k in (4, 19, 36, 52, 68, 85, 99, 130, 177, 220)],
       ["192.0.2.%d" % k for k in (11, 29, 33, 64, 80, 105, 121, 149, 188, 240)]]


def top_case(i, *, fmt, vi, fpath, conds, by, n, prompts, nocalc, conds2=None, by2=None, n2=None, nlines=480, code=None):
    i += 22
    cid = "log-%d" % (32101 + i)

    def build():
        for tries in range(200):
            rng = Random(32101 * 13 + i * 6151 + tries)
            ips = IPP[vi % 3]
            ip_w = [ips[int(rng.random() ** 2 * len(ips))] for _ in range(4000)]
            evs = make_events(rng, nlines, dt.datetime(2026, 9, 15, 8, 0, 0), 9 * 3600, fmt, vi, code=code,
                              code_rate=0.2 if code else 0.08, ips=ips)
            for e in evs:     # skew the field distribution so ranks are separated
                r = rng.random()
                if by == "ip":
                    e.ip = ips[int(r ** 2 * len(ips))]
                if by in ("path", "svc"):
                    pool = PATHS[vi % 4] if by == "path" else SVCS[vi % 4]
                    setattr(e, by, pool[int(r ** 1.7 * len(pool))])
                if by == "msg":
                    pass
            specs = [dict(k="top", conds=conds, by=by, n=n)]
            if conds2:
                specs.append(dict(k="top", conds=conds2, by=by2 or by, n=n2 or n))
            files = write_files({fpath: evs}, fmt)
            try:
                toks = run_answers(files, fmt, specs)
            except AssertionError:
                continue
            break
        else:
            raise SystemExit("no seed " + cid)
        decoy = "unfiltered ranking"
        cmds = []
        for s in specs:
            cmds.append(["cat %s | %s | %s | sort | uniq -c | sort -rn | head -n %d"
                         % (fpath, " | ".join(cond_greps(fmt, s["conds"])), extract(fmt, s["by"]), s["n"])])
        make(cid, i, sub="topn", fmt=fmt, evs={fpath: evs}, specs=specs, prompts=prompts, refs=cmds,
             traps=["TR-DECOY"], decoys={"TR-DECOY": decoy}, nocalc=nocalc, task_type="aggregate_jsonl" if fmt == "json" else "count_events",
             desc="Ranks the top values of one log field among lines filtered by another field",
             notes_traps="- TR-DECOY: the ranking changes when the filter is dropped or applied as a substring; only exact field filters give the stated ranking.",
             notes_ref="cat file | exact-field greps | extract the grouped field | sort | uniq -c | sort -rn | head -n N.")
    B.append(build)


P, S = PATHS, SVCS
top_case(0, fmt="nginx", vi=0, fpath="logs/access.log", conds=dict(status=404), by="ip", n=3, nocalc=False, code=404,
         prompts=["logs/access.log 里返回 404 最多的前三个客户端 IP 是哪几个？各有多少次？"])
top_case(1, fmt="json", vi=1, fpath="export/svc-0915.jsonl", conds=dict(level="ERROR"), by="path", n=3, nocalc=True,
         prompts=["export/svc-0915.jsonl 里 level 为 ERROR 的记录，按 path 统计，出错最多的前三个路径是哪些？各多少条？"])
top_case(2, fmt="kv", vi=2, fpath="logs/edge-kv.log", conds=dict(level="ERROR"), by="svc", n=3, nocalc=False,
         conds2=dict(level="WARN"), by2="svc", n2=3,
         prompts=["Which three services have the most ERROR lines in logs/edge-kv.log? Give each service and its count.",
                  "Now do the same for WARN lines."])
top_case(3, fmt="app", vi=3, fpath="app/server.log", conds=dict(level="WARN"), by="svc", n=3, nocalc=True,
         prompts=["app/server.log 里 WARN 级别的日志，哪三个组件出现得最多？各出现几次？"])
top_case(4, fmt="json", vi=0, fpath="logs/api-0915.jsonl", conds=dict(level="ERROR"), by="msg", n=2, nocalc=False,
         prompts=["logs/api-0915.jsonl 中 ERROR 记录里最常见的两种 msg 是什么？各出现多少次？"])
top_case(5, fmt="kv", vi=1, fpath="var/log/bill/bill.log", conds=dict(status=404), by="path", n=3, nocalc=False, code=404,
         conds2=dict(status=404, method="POST"), by2="path", n2=2,
         prompts=["In var/log/bill/bill.log, which three paths return 404 most often? Show counts.",
                  "Only counting POST requests, which two paths are top for 404?"])
top_case(6, fmt="nginx", vi=2, fpath="srv/log/access.log", conds=dict(status=500), by="path", n=3, nocalc=True, code=500,
         prompts=["srv/log/access.log 里返回 500 的请求，哪三个路径最多？分别有几次？"])
top_case(7, fmt="app", vi=0, fpath="logs/orders-app.log", conds=dict(level="ERROR"), by="msg", n=2, nocalc=False,
         conds2=dict(level="WARN"), by2="msg", n2=2,
         prompts=["logs/orders-app.log 里 ERROR 日志最常见的两条消息是什么？各多少次？",
                  "WARN 级别的话，最常见的两条消息和次数呢？"])
top_case(8, fmt="kv", vi=3, fpath="logs/mailer.log", conds=dict(status=429), by="svc", n=2, nocalc=False, code=429,
         prompts=["In logs/mailer.log, which two services get status 429 most often, and how many times each?"])
top_case(9, fmt="nginx", vi=1, fpath="www/access.log", conds=dict(status=502), by="ip", n=2, nocalc=True, code=502,
         prompts=["www/access.log 里返回 502 次数最多的两个 IP 是谁？分别多少次？"])
