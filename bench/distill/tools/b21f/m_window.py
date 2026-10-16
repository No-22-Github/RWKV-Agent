"""32113-32122: counts inside a stated time window, edges written out."""
import datetime as dt
from random import Random

from common import write_files
from gen import PATHS, SVCS, date_grep, g_status, hms, make_events, plant, tod_awk
from lib import run_answers
from mk import make
from m_count import naive

B = []
D = dt.datetime


def window_case(i, *, fmt, vi, code, fpath, lo, hi, lo_incl, hi_incl, ev_conds, prompts, nocalc, narrow=None, path=None):
    """lo/hi are (h, m); narrow is a second (lo, hi) for turn 2."""
    i += 12
    cid = "log-%d" % (32101 + i)

    def build():
        rng = Random(32101 * 17 + i * 104729)
        day = D(2026, 9, 15, 8, 0, 0)
        prev = make_events(rng, 90, D(2026, 9, 14, 20, 0, 0), 4 * 3600 - 1, fmt, vi, code=code, code_rate=0.2)
        cur = make_events(rng, 520, day, 11 * 3600, fmt, vi, code=code, code_rate=0.2,
                          focus={"path": [path]} if path else None)
        edges = []
        for (a, b, li, hi_) in [(lo, hi, lo_incl, hi_incl)] + ([(narrow[0], narrow[1], True, False)] if narrow else []):
            edges += [D(2026, 9, 15, a[0], a[1], 0), D(2026, 9, 15, b[0], b[1], 0)]
            edges += [D(2026, 9, 15, b[0], b[1], 0) - dt.timedelta(milliseconds=1 if fmt != "nginx" else 1000)]
        edges = sorted(set(edges))
        cur = plant(rng, cur, edges, status=code, path=path, fmt=fmt)
        evs = {fpath: sorted(prev + cur, key=lambda e: e.ts)}
        files = write_files(evs, fmt)

        def spec(a, b, li, hi_):
            return dict(k="count", conds=dict(status=code, **({"path": path} if path else {})), first=True, last=False,
                        window=dict(lo=D(2026, 9, 15, a[0], a[1]).strftime("%Y-%m-%d %H:%M:%S.000"),
                                    hi=D(2026, 9, 15, b[0], b[1]).strftime("%Y-%m-%d %H:%M:%S.000"), lo_incl=li, hi_incl=hi_))
        specs = [spec(lo, hi, lo_incl, hi_incl)] + ([spec(narrow[0], narrow[1], True, False)] if narrow else [])
        toks = run_answers(files, fmt, specs)
        assert int(toks[0][0]) >= 8 and all(int(t[0]) >= 5 for t in toks), toks
        text = files[fpath]
        decoys = {"TR-DECOY": str(naive(text, specs[0]["conds"])), "TR-DEFN": "no date filter: %d" % sum(
            1 for ln in text.splitlines() if str(code) in ln)}
        cmds = []
        for s in specs:
            w = s["window"]
            lo_s, hi_s = w["lo"][11:], w["hi"][11:]
            if fmt == "nginx":
                lo_s, hi_s = lo_s[:8], hi_s[:8]
            lo_op = ">=" if w["lo_incl"] else ">"
            hi_op = "<=" if w["hi_incl"] else "<"
            greps = [date_grep(fmt, dt.date(2026, 9, 15)), g_status(fmt, code)]
            if path:
                from gen import g_path
                greps.append(g_path(fmt, path))
            cmds.append(["cat %s | %s | awk '{ %s; if (t%s\"%s\" && t%s\"%s\") { c++; if (!f) f=$0 } } END { print c+0; print f }'"
                         % (fpath, " | ".join(greps), tod_awk(fmt), lo_op, lo_s, hi_op, hi_s)])
        make(cid, i, sub="window", fmt=fmt, evs=evs, specs=specs, prompts=prompts, refs=cmds,
             traps=["TR-DEFN", "TR-DECOY"], decoys=decoys, nocalc=nocalc, task_type="time_window", axes=("OBS",),
             desc="Counts status-code hits inside a stated time window on one day of a log that also holds the previous evening",
             notes_traps="- TR-DEFN: the window edges (inclusive/exclusive) are spelled out and lines sit exactly on them (and 1 ms / 1 s inside the upper edge).\n- TR-DECOY: the status code also appears inside durations/bytes/paths; the file also holds the previous evening, so a time-of-day filter without the date over-counts.",
             notes_ref="Filter the day, the exact status field, then awk string-compare the time-of-day against the window edges.")
    B.append(build)


P, S = PATHS, SVCS
window_case(0, fmt="json", vi=0, code=503, fpath="logs/api.jsonl", lo=(14, 0), hi=(16, 0), lo_incl=True, hi_incl=False, ev_conds=None, nocalc=False,
            prompts=["logs/api.jsonl 里 9 月 15 日 14:00 到 16:00 之间，status 是 503 的请求有多少条？14:00:00 整算在内，16:00:00 整不算。再告诉我窗口里第一条是几点几分几秒。"])
window_case(1, fmt="nginx", vi=1, code=502, fpath="logs/nginx/access.log", lo=(10, 30), hi=(12, 0), lo_incl=True, hi_incl=True, ev_conds=None, nocalc=True,
            prompts=["Using logs/nginx/access.log, how many 502 responses were there on Sep 15 between 10:30:00 and 12:00:00, counting both of those exact seconds? Also give the time of the first one in that window."])
window_case(2, fmt="kv", vi=2, code=500, fpath="srv/edge/edge.log", lo=(9, 0), hi=(11, 0), lo_incl=False, hi_incl=False, ev_conds=None, nocalc=False,
            narrow=((9, 30), (10, 30)),
            prompts=["srv/edge/edge.log 里 9 月 15 日 9 点到 11 点之间 status=500 的有多少条？9:00:00 整不算，11:00:00 整也不算。窗口里最早一条几点？",
                     "把窗口缩小到 9:30:00（含）到 10:30:00（不含），同样的问题。"])
window_case(3, fmt="app", vi=3, code=504, fpath="logs/worker.log", lo=(13, 0), hi=(15, 30), lo_incl=True, hi_incl=False, ev_conds=None, nocalc=True,
            prompts=["In logs/worker.log, count entries on 2026-09-15 with status=504 from 13:00:00 up to but excluding 15:30:00, and tell me the time of the first one."])
window_case(4, fmt="json", vi=1, code=401, fpath="data/auth-edge.jsonl", lo=(16, 0), hi=(18, 0), lo_incl=True, hi_incl=True, ev_conds=None, nocalc=False,
            path=P[1][4],
            prompts=["data/auth-edge.jsonl 里，9 月 15 日 16:00:00 到 18:00:00（两端都算）访问 %s 并且 status 是 401 的有几条？最早一条是几点？" % P[1][4]])
window_case(5, fmt="nginx", vi=3, code=404, fpath="var/log/site/access.log", lo=(12, 0), hi=(14, 0), lo_incl=True, hi_incl=False, ev_conds=None, nocalc=False,
            narrow=((13, 0), (14, 0)),
            prompts=["看 var/log/site/access.log，9 月 15 日中午 12:00:00 起、到 14:00:00 之前（14:00:00 整不算），返回 404 的请求有多少条？这个窗口里最早的一条是几点几分几秒？",
                     "只看 13:00:00（含）到 14:00:00（不含）呢？"])
window_case(6, fmt="kv", vi=0, code=429, fpath="logs/limit.log", lo=(15, 0), hi=(17, 0), lo_incl=True, hi_incl=False, ev_conds=None, nocalc=True,
            prompts=["How many status=429 lines are in logs/limit.log between 15:00:00 (included) and 17:00:00 (excluded) on 15 Sep 2026? Give the first one's time as well."])
window_case(7, fmt="app", vi=2, code=500, fpath="app/ledger.log", lo=(8, 30), hi=(10, 0), lo_incl=True, hi_incl=True, ev_conds=None, nocalc=False,
            narrow=((9, 0), (10, 0)),
            prompts=["app/ledger.log 里 9 月 15 日 8:30:00 到 10:00:00（含两端）status=500 的有多少次？最早一次是几点几分几秒？",
                     "再缩到 9:00:00 起、到 10:00:00 之前呢？"])
window_case(8, fmt="json", vi=2, code=502, fpath="logs/gw.jsonl", lo=(17, 0), hi=(19, 0), lo_incl=False, hi_incl=True, ev_conds=None, nocalc=True,
            path=P[2][1],
            prompts=["In logs/gw.jsonl, on Sep 15, how many %s requests returned 502 after 17:00:00 (not including that second) up to and including 19:00:00? When was the first one in that range?" % P[2][1]])
window_case(9, fmt="nginx", vi=0, code=503, fpath="logs/shop-access.log", lo=(11, 0), hi=(13, 0), lo_incl=True, hi_incl=False, ev_conds=None, nocalc=False,
            prompts=["logs/shop-access.log 里 9 月 15 日 11:00:00（含）到 13:00:00（不含）之间返回 503 的请求有多少条？第一条是几点几分几秒？"])
