"""32141-32150: find the anomaly and say where it is (slowest requests,
first OOM and what came before it, first error after a deploy marker)."""
import datetime as dt
from random import Random

from common import write_files
from gen import PATHS, SVCS, cond_greps, make_events, plant
from lib import run_answers
from mk import make

B = []
D = dt.datetime
DUR_AWK = {"json": ("\"dur_ms\":[0-9]+", 9), "kv": ("dur_ms=[0-9]+", 7), "app": ("took=[0-9]+", 5)}
WARN_IDX = {"json": '"level":"WARN"', "kv": " level=warn ", "app": "] WARN "}
ERR_IDX = {"json": '"level":"ERROR"', "kv": " level=error ", "app": "] ERROR"}
OOM = "out of memory: OOM killer stopped worker"
DEPLOY = "deploy started for release"


def anom_case(i, *, kind, fmt, vi, paths, starts, span_h, nper, specs, prompts, nocalc, traps, decoy, plants=(), outliers=0, slow_path=None, desc, note):
    i += 40
    cid = "log-%d" % (32101 + i)

    def build():
        rng = Random(32101 * 19 + i * 5231)
        evs = {}
        for p, st in zip(paths, starts):
            es = make_events(rng, nper, st, int(span_h * 3600) - 1, fmt, vi, decoy=False)
            evs[p] = es
        if outliers:
            p = paths[-1]
            base = evs[p]
            ts = sorted(rng.sample([e.ts for e in base], outliers))
            durs = rng.sample(range(2300, 9000), outliers)
            evs[p] = plant(rng, base, [t + dt.timedelta(milliseconds=7) for t in ts], status=200, path=slow_path, durs=durs, level="INFO")
        for (pi, frac, msg, level, status, count) in plants:
            p = paths[pi]
            base = evs[p]
            t0 = base[0].ts + (base[-1].ts - base[0].ts) * frac
            inst = [t0 + dt.timedelta(minutes=31 * k, milliseconds=13 * k) for k in range(count)]
            evs[p] = plant(rng, base, inst, status=status, msg=msg, level=level)
        files = write_files(evs, fmt)
        toks = run_answers(files, fmt, specs)
        cmds = []
        for s in specs:
            used = [p for p in paths if s.get("files") is None or p in s["files"]]
            cat = "cat %s | " % " ".join(used)
            if s["k"] == "slowest":
                pat, k = DUR_AWK[fmt] if fmt != "nginx" else ("rt=[0-9.]+", 3)
                flt = (" | ".join(cond_greps(fmt, s["conds"])) + " | ") if s.get("conds") else ""
                if fmt == "nginx":
                    cmd = cat + flt + "awk 'match($0,/rt=[0-9.]+/){print substr($0,RSTART+3,RLENGTH-3), $0}' | sort -rn | head -n %d" % s["n"]
                else:
                    cmd = cat + flt + "awk 'match($0,/%s/){print substr($0,RSTART+%d,RLENGTH-%d), $0}' | sort -rn | head -n %d" % (pat, k, k, s["n"])
                cmds.append([cmd])
            elif s["k"] == "firstbefore":
                w = WARN_IDX[fmt]
                word = s["find"]["msg_has"]
                cmds.append([cat + "grep -F '%s' | head -1" % word,
                             cat + "awk '/%s/{exit} index($0,\"%s\"){l=$0} END{print l}'" % (word, w.replace('"', '\\"'))])
            else:
                lv = ERR_IDX[fmt] if s["then"]["level"] == "ERROR" else WARN_IDX[fmt]
                word = s["find"]["msg_has"]
                cmds.append([cat + "grep -F '%s' | head -1" % word,
                             cat + "awk '/%s/{f=1;next} f && index($0,\"%s\"){print; exit}'" % (word, lv.replace('"', '\\"'))])
        make(cid, i, sub="anomaly", fmt=fmt, evs=evs, specs=specs, prompts=prompts, refs=cmds,
             traps=traps, decoys={t: decoy for t in traps}, nocalc=nocalc, task_type="locate_error", axes=("OBS",),
             desc=desc, notes_traps=note, notes_ref="See the per-turn commands: awk/sort/head over the exact field, or an awk state flag for first-X-and-what-came-before.")
    B.append(build)


P, S = PATHS, SVCS
d = lambda day, h=8: D(2026, 9, day, h, 0, 0)
anom_case(0, kind="slow", fmt="json", vi=0, paths=["logs/api.jsonl"], starts=[d(15)], span_h=10, nper=420, nocalc=True,
          specs=[dict(k="slowest", n=3)], outliers=6, traps=["TR-DECOY"], decoy="slowest by bytes instead of dur_ms",
          prompts=["logs/api.jsonl 里耗时（dur_ms）最长的三个请求是哪几个？告诉我它们的 req_id 和耗时。"],
          desc="Finds the three slowest requests in a JSON-lines log", note="- TR-DECOY: bytes and status fields also hold big numbers; only dur_ms ranks speed.")
anom_case(1, kind="slow", fmt="kv", vi=1, paths=["var/log/bill.log"], starts=[d(15)], span_h=10, nper=380, nocalc=False,
          specs=[dict(k="slowest", n=3), dict(k="slowest", n=2, conds=dict(method="POST"))], outliers=7, traps=["TR-DECOY"], decoy="slowest overall instead of slowest POST",
          prompts=["var/log/bill.log 里最慢的三个请求（看 dur_ms）是哪三个？给我请求 id 和耗时。",
                   "只看 POST 请求的话，最慢的两个是哪两个？"],
          desc="Finds the slowest requests in a key=value log, then restricts to one method", note="- TR-DECOY: the second turn filters by method; the overall slowest may be a GET.")
anom_case(2, kind="slow", fmt="app", vi=2, paths=["app/ledger.log"], starts=[d(15)], span_h=10, nper=400, nocalc=True,
          specs=[dict(k="slowest", n=2)], outliers=5, traps=["TR-DECOY"], decoy="largest status or request count",
          prompts=["In app/ledger.log, which two requests took the longest (the took=...ms value)? Give me the request ids and their times."],
          desc="Finds the two slowest requests in an application log", note="- TR-DECOY: status codes are also three-digit numbers; only took=..ms is the duration.")
anom_case(3, kind="slow", fmt="nginx", vi=3, paths=["srv/nginx/access.log"], starts=[d(15)], span_h=10, nper=450, nocalc=False,
          specs=[dict(k="slowest", n=3, rid_only=True)], outliers=6, traps=["TR-DECOY"], decoy="largest bytes column",
          prompts=["srv/nginx/access.log 的最后一列 rid 是请求编号，rt 是响应秒数。响应最慢的三个请求，编号分别是什么？"],
          desc="Finds the three slowest requests in an access log whose rt field is in seconds", note="- TR-DECOY: the bytes column is larger than rt; rt=4.231 means seconds.")
anom_case(4, kind="oom", fmt="json", vi=1, paths=["logs/pay.jsonl"], starts=[d(15)], span_h=10, nper=420, nocalc=False,
          specs=[dict(k="firstbefore", find=dict(msg_has="OOM"), before=dict(level="WARN"))],
          plants=[(0, 0.55, OOM, "ERROR", 500, 3)], traps=["TR-DECOY"], decoy="the last OOM line / the WARN before the last one",
          prompts=["In logs/pay.jsonl, when did the first OOM happen (give its req_id and time), and which WARN record came right ahead of it? I need that WARN's req_id."],
          desc="Locates the first OOM line and the last WARN line preceding it", note="- TR-DECOY: OOM appears three times; the question is about the first, and WARN lines continue after it.")
anom_case(5, kind="oom", fmt="app", vi=2, paths=["logs/worker.log.1", "logs/worker.log"], starts=[d(14, 14), d(15, 8)], span_h=12, nper=300, nocalc=True,
          specs=[dict(k="firstbefore", find=dict(msg_has="OOM"), before=dict(level="WARN")),
                 dict(k="firstbefore", find=dict(msg_has="internal error"), before=dict(level="WARN"), files=["logs/worker.log"])],
          plants=[(0, 0.6, OOM, "ERROR", 500, 2)], traps=["TR-MULTISRC"], decoy="searching only the current file",
          prompts=["logs/worker.log 和旧的 logs/worker.log.1 里，第一次 OOM 是什么时候？给出它的请求 id 和几点几分几秒，再告诉我在它之前最近的一条 WARN 的请求 id。",
                   "只看当前的 logs/worker.log，第一次出现 internal error 是哪条请求、几点？它之前最近的一条 WARN 的请求 id 是什么？"],
          desc="Finds the first OOM across a rotated pair of files, then a different first-occurrence in the current file only", note="- TR-MULTISRC: the first OOM sits in the rotated file; the second question narrows to the current file.")
anom_case(6, kind="deploy", fmt="kv", vi=3, paths=["logs/edge.log"], starts=[d(15)], span_h=10, nper=400, nocalc=False,
          specs=[dict(k="firstafter", find=dict(msg_has="deploy started"), then=dict(level="ERROR"))],
          plants=[(0, 0.4, DEPLOY + " 2.14.3, deploy started", "INFO", 200, 1)], traps=["TR-DECOY"], decoy="the first ERROR in the whole file",
          prompts=["logs/edge.log 里有一条记录写着 deploy started。从那条之后，第一条 ERROR 是哪个请求、几点几分几秒？也告诉我 deploy started 那条的请求 id 和时间。"],
          desc="Finds the first ERROR after a deploy marker line", note="- TR-DECOY: ERROR lines also occur before the marker; only the first one after it counts.")
anom_case(7, kind="deploy", fmt="json", vi=2, paths=["export/ledger-0915.jsonl"], starts=[d(15)], span_h=10, nper=430, nocalc=True,
          specs=[dict(k="firstafter", find=dict(msg_has="deploy started"), then=dict(level="ERROR")),
                 dict(k="firstafter", find=dict(msg_has="deploy started"), then=dict(level="WARN"))],
          plants=[(0, 0.35, "deploy started for release 8.2.0", "INFO", 200, 1)], traps=["TR-DECOY"], decoy="the first match in the whole file",
          prompts=["In export/ledger-0915.jsonl, find the line saying deploy started, then tell me the first ERROR record after it: its req_id and time. Also give the req_id and time of the deploy line itself.",
                   "And the first WARN record after the deploy line instead?"],
          desc="Finds the first ERROR and then the first WARN after a deploy marker line", note="- TR-DECOY: ERROR/WARN lines occur before the marker too.")
anom_case(8, kind="slow", fmt="json", vi=3, paths=["data/jobs-0915.jsonl"], starts=[d(15)], span_h=10, nper=440, nocalc=False,
          specs=[dict(k="slowest", n=3, conds=dict(path=P[3][1]))], outliers=9, slow_path=P[3][1], traps=["TR-DECOY"], decoy="slowest across all paths",
          prompts=["data/jobs-0915.jsonl 里访问 %s 的请求中，最慢的三个是哪几个？要 req_id 和 dur_ms。" % P[3][1]],
          desc="Finds the slowest requests restricted to one path", note="- TR-DECOY: planted slow requests exist on other paths too (outliers are planted only on the target path, but ordinary slow requests exist everywhere).")
anom_case(9, kind="oom", fmt="kv", vi=0, paths=["logs/api-kv.log"], starts=[d(15)], span_h=10, nper=400, nocalc=False,
          specs=[dict(k="firstbefore", find=dict(msg_has="db connection reset"), before=dict(level="WARN"))],
          traps=["TR-DECOY"], decoy="the last db connection reset",
          prompts=["In logs/api-kv.log, when was the first db connection reset (req id and time), and which request id was the last WARN line ahead of it?"],
          desc="Locates the first db connection reset and the last WARN line preceding it", note="- TR-DECOY: db connection reset repeats all day; only the first counts.")
