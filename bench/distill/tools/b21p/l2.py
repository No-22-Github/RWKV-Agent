"""logs time_window 33745-33753."""
import datetime as dt
import re

from common import *

B = []


def reg(f):
    B.append(f)
    return f


def stamps(r, start, end, n):
    span = int((end - start).total_seconds())
    return sorted(start + dt.timedelta(seconds=r.randint(0, span)) for _ in range(n))


PATHS = ["/api/items", "/api/cart", "/login", "/static/app.js", "/api/search", "/health", "/api/orders"]


@reg
def w1():
    r = rng("w1")
    ts = stamps(r, dt.datetime(2026, 9, 14, 14, 0), dt.datetime(2026, 9, 14, 18, 30), 220)
    rows = []
    for t in ts:
        st = r.choice([200] * 14 + [301, 404, 404, 500, 502, 503])
        rows.append((t, st, "%s %s +0000 GET %s %d %dms" % (t.strftime("%d/%b/%Y:%H:%M:%S"), "", r.choice(PATHS), st, r.randint(3, 400))))
    lines = [x[2].replace("  ", " ", 1) for x in rows]
    lines = [re.sub(r"^(\S+) +\+0000", r"\1 +0000", l) for l in lines]
    lo, hi = dt.datetime(2026, 9, 14, 16, 0), dt.datetime(2026, 9, 14, 17, 0)
    n5 = sum(1 for t, st, _ in rows if lo <= t < hi and st >= 500)
    n4 = sum(1 for t, st, _ in rows if lo <= t < hi and 400 <= st < 500)
    assert n5 >= 3 and n4 >= 3
    f = {"access.log": "\n".join(lines) + "\n"}
    make("log-33745", sub="window", task_type="time_window", desc="Count 5xx within a Beijing-time hour on a log kept in UTC",
         files=f, turns=[T("access.log 里的时间都是 UTC（+0000）。北京时间 2026-09-15 00:00 到 01:00（不含 01:00）这一小时里，一共有多少个 5xx 响应？", [str(n5)], token=True, req=["bash"]),
                         T("同一个时间段里 4xx 的呢？", [str(n4)], token=True)],
         truth="import re\nrows=[l.split() for l in files['access.log'].splitlines()]\ndef inw(x): return x[0][:14]=='14/Sep/2026:16'\nanswers=[str(sum(1 for x in rows if inw(x) and int(x[4])>=500)), str(sum(1 for x in rows if inw(x) and 400<=int(x[4])<500))]",
         ref=[("awk '$1 ~ /^14\\/Sep\\/2026:16/ && $5>=500' access.log | wc -l", str(n5))],
         notes={"traps": "Beijing 00:00-01:00 on 09-15 is UTC 16:00-17:00 on 09-14 (previous day).", "steps": "convert window to UTC, awk prefix match.", "unique": "5xx=%d 4xx=%d" % (n5, n4)},
         traps=("TR-TZ", "TR-DATEFMT"), axes=("OBS",), rc=5)


def D(*a):
    return dt.datetime(*a)


@reg
def w2():
    r = rng("w2")
    ts = stamps(r, D(2026, 9, 12, 22, 0), D(2026, 9, 13, 2, 0), 230)
    kinds = ["approved"] * 8 + ["declined"] * 3 + ["timeout"] * 2
    ev = [(t, r.choice(kinds)) for t in ts]
    lines = ["%s %s order=%d %s" % (t.strftime("%Y-%m-%d %H:%M:%S"), "INFO" if k == "approved" else "WARN", 70000 + i, k) for i, (t, k) in enumerate(ev)]
    lo, hi = D(2026, 9, 12, 23, 30), D(2026, 9, 13, 0, 30)
    inw = [(t, k) for t, k in ev if lo <= t < hi and k == "declined"]
    n = len(inw); n2 = sum(1 for t, k in inw if t >= D(2026, 9, 13))
    assert n >= 5 and n2 >= 2 and n != n2
    f = {"payments.log": "\n".join(lines) + "\n"}
    make("log-33746", sub="window", task_type="time_window", desc="Count declined payments across midnight, then only those after midnight",
         files=f, turns=[T("In payments.log, how many payments were declined between 23:30 on 2026-09-12 and 00:30 on 2026-09-13?", [str(n)], token=True, req=["bash"]),
                         T("How many of those fall after midnight, on the 13th?", [str(n2)], token=True)],
         truth="rows=[l.split() for l in files['payments.log'].splitlines()]\nin1=[x for x in rows if x[-1]=='declined' and ((x[0]=='2026-09-12' and x[1]>='23:30:00') or (x[0]=='2026-09-13' and x[1]<'00:30:00'))]\nanswers=[str(len(in1)), str(len([x for x in in1 if x[0]=='2026-09-13']))]",
         ref=[("awk '$NF==\"declined\" && (($1==\"2026-09-12\" && $2>=\"23:30:00\") || ($1==\"2026-09-13\" && $2<\"00:30:00\"))' payments.log | wc -l", str(n))],
         notes={"traps": "Window straddles midnight; a simple time-of-day range finds nothing or too much.", "steps": "awk with two date conditions.", "unique": "%d declined, %d after midnight" % (n, n2)},
         traps=("TR-DATEFMT", "TR-DECOY"), axes=("OBS",), rc=5)


@reg
def w3():
    r = rng("w3")
    us = stamps(r, D(2026, 9, 14, 10, 30), D(2026, 9, 14, 14, 0), 110)
    cn = stamps(r, D(2026, 9, 14, 18, 30), D(2026, 9, 14, 22, 0), 110)
    mk_ = lambda t, z: "%s%s %s edge-%d %s" % (t.strftime("%Y-%m-%dT%H:%M:%S"), z, r.choice(["ERROR", "INFO", "INFO", "INFO", "WARN"]), r.randint(1, 4), r.choice(["cache miss ratio high", "request served", "origin fetch", "tls renegotiate"]))
    lu = [mk_(t, "Z") for t in us]; lc = [mk_(t, "+08:00") for t in cn]
    e_us = sum(1 for l, t in zip(lu, us) if D(2026, 9, 14, 12) <= t < D(2026, 9, 14, 13) and " ERROR " in l)
    e_cn = sum(1 for l, t in zip(lc, cn) if D(2026, 9, 14, 20) <= t < D(2026, 9, 14, 21) and " ERROR " in l)
    assert e_us != e_cn and e_us + e_cn >= 6
    f = {"edge-us.log": "\n".join(lu) + "\n", "edge-cn.log": "\n".join(lc) + "\n"}
    win = "edge-us" if e_us > e_cn else "edge-cn"
    make("log-33747", sub="window", task_type="time_window", desc="Same Beijing-time hour across two logs that use Z and +08:00 stamps",
         files=f, turns=[T("edge-us.log 的时间戳带 Z（UTC），edge-cn.log 带 +08:00（北京时间）。2026-09-14 北京时间 20:00 到 21:00 这一小时，两个文件里加起来有多少条 ERROR？", [str(e_us + e_cn)], token=True, req=["bash"]),
                         T("哪个文件里的 ERROR 更多？", [win])],
         truth="def cnt(f,lo,hi): return sum(1 for l in files[f].splitlines() if lo<=l[:19]<hi and ' ERROR ' in l)\na=cnt('edge-us.log','2026-09-14T12:00:00','2026-09-14T13:00:00')\nb=cnt('edge-cn.log','2026-09-14T20:00:00','2026-09-14T21:00:00')\nanswers=[str(a+b), 'edge-us' if a>b else 'edge-cn']",
         ref=[("cat edge-us.log | awk '$1>=\"2026-09-14T12:00:00\" && $1<\"2026-09-14T13:00:00\" && $2==\"ERROR\"' | wc -l", str(e_us)),
              ("awk '$1>=\"2026-09-14T20:00:00\" && $1<\"2026-09-14T21:00:00\" && $2==\"ERROR\"' edge-cn.log | wc -l", str(e_cn))],
         notes={"traps": "US file window is 12:00-13:00 UTC; one grep pattern for both files is wrong.", "steps": "per-file awk windows.", "unique": "us %d cn %d" % (e_us, e_cn)},
         traps=("TR-TZ", "TR-MULTISRC"), axes=("OBS", "CHN"), rc=5)


@reg
def w4():
    r = rng("w4")
    base = int((D(2026, 9, 10, 13, 0) - D(1970, 1, 1)).total_seconds())
    ts = sorted(base + r.randint(0, 3 * 3600) for _ in range(190))
    kinds = ["ok"] * 6 + ["retry"] * 2 + ["fail"]
    ev = [(t, r.choice(kinds)) for t in ts]
    lines = ["%d %s job=%d" % (t, k, 500 + i) for i, (t, k) in enumerate(ev)]
    lo = int((D(2026, 9, 10, 14, 0) - D(1970, 1, 1)).total_seconds()); hi = lo + 1800
    n = sum(1 for t, k in ev if lo <= t < hi and k == "retry")
    assert n >= 4
    f = {"worker.log": "\n".join(lines) + "\n"}
    make("log-33748", sub="window", task_type="time_window", desc="Epoch-second log, window given in readable UTC time",
         files=f, turns=[T("Each line of worker.log starts with a Unix timestamp in seconds. How many retry events happened between 14:00:00 and 14:30:00 UTC on 2026-09-10 (end not included)?", [str(n)], token=True, req=["bash"])],
         truth="lo=1789048800\nassert lo==%d\nanswers=[str(sum(1 for l in files['worker.log'].splitlines() if lo<=int(l.split()[0])<lo+1800 and l.split()[1]=='retry'))]" % lo,
         ref=[("awk '$1>=%d && $1<%d && $2==\"retry\"' worker.log | wc -l" % (lo, hi), str(n))],
         notes={"traps": "Epoch seconds; awk strftime is not available in the sandbox so the window bounds must be converted (date -d works).", "steps": "date -u -d '2026-09-10 14:00:00' +%s; awk range.", "unique": "%d retries" % n},
         traps=("TR-TZ", "TR-DATEFMT"), axes=("OBS",), rc=5)


@reg
def w5():
    r = rng("w5")
    hours = {8: 22, 9: 31, 10: 47, 11: 29, 12: 18, 13: 24, 14: 36}
    ev = []
    for h, c in hours.items():
        for _ in range(c):
            ev.append(D(2026, 9, 14, h, r.randint(0, 59), r.randint(0, 59)))
    ev.sort()
    lines = ["%s host1 gw[%d]: request %s from 10.0.%d.%d" % (t.strftime("%b %d %H:%M:%S"), 100 + i % 7, r.choice(["accepted", "accepted", "queued"]), r.randint(0, 9), r.randint(1, 250)) for i, t in enumerate(ev)]
    f = {"syslog.txt": "\n".join(lines) + "\n"}
    make("log-33749", sub="window", task_type="time_window", desc="Busiest hour of a syslog-style file; follow-up asks that hour's count",
         files=f, turns=[T("syslog.txt 里请求最多的是哪个小时？回答形如 10:00。", [], any_=["10:00", "10点", "10 点", "10时", "10:00-11:00", "10-11"]),
                         T("那个小时里一共有多少条请求？", ["47"], token=True)],
         truth="import collections\nc=collections.Counter(l.split()[2][:2] for l in files['syslog.txt'].splitlines())\nh,n=c.most_common(1)[0]\nanswers=[h+':00', str(n)]",
         ref=[("awk '{print substr($3,1,2)}' syslog.txt | sort | uniq -c | sort -rn | head -2", "47 10")],
         notes={"traps": "No date year in lines; the hour is $3 substring.", "steps": "awk hour histogram.", "unique": "10:00 has 47."},
         traps=("TR-DECOY",), axes=("OBS",), rc=4)


@reg
def w6():
    r = rng("w6")
    ts = stamps(r, D(2026, 9, 16, 9, 0), D(2026, 9, 16, 9, 59, 59), 210)
    ts = [t for t in ts if t.strftime("%H:%M:%S") not in ("09:45:00", "10:00:00")]
    kinds = ["INFO disk usage ok"] * 5 + ["INFO heartbeat"] * 5 + ["WARN disk usage high"] * 2 + ["WARN slow response"] * 2
    ev = [(t, r.choice(kinds)) for t in ts]
    lines = ["%s +0800 %s" % (t.strftime("%Y-%m-%d %H:%M:%S"), k) for t, k in ev]
    n = sum(1 for t, k in ev if t >= D(2026, 9, 16, 9, 45) and "disk usage high" in k)
    assert n >= 3
    f = {"monitor.log": "\n".join(lines) + "\n"}
    make("log-33750", sub="window", task_type="time_window", desc="Count warnings in the 15 minutes before the current time (fixed clock 10:00)",
         files=f, turns=[T("monitor.log shows disk usage warnings. How many 'disk usage high' warnings were logged in the last 15 minutes, counting back from right now?", [str(n)], token=True, req=["bash"])],
         truth="answers=[str(sum(1 for l in files['monitor.log'].splitlines() if l[11:19]>='09:45:00' and 'disk usage high' in l))]",
         ref=[("awk '$2>=\"09:45:00\" && /disk usage high/' monitor.log | wc -l", str(n))],
         notes={"traps": "Needs the current time (fixed clock 2026-09-16 10:00 +0800) to define the window; other WARN type is a decoy.", "steps": "datetime, then awk.", "unique": "%d" % n},
         traps=("TR-DEFN", "TR-DECOY"), policy={"must_offer": ["bash", "datetime"]}, axes=("OBS",), rc=5)


@reg
def w7():
    r = rng("w7")
    ts = stamps(r, D(2026, 9, 15, 19, 0), D(2026, 9, 16, 9, 0), 230)
    kinds = ["OK"] * 8 + ["ERROR"] * 2 + ["WARN"] * 2
    ev = [(t, r.choice(kinds)) for t in ts]
    lines = ["%s [%s] sync batch %d" % (t.strftime("%Y-%m-%d %H:%M:%S"), k, 3000 + i) for i, (t, k) in enumerate(ev)]
    n = sum(1 for t, k in ev if D(2026, 9, 15, 22) <= t < D(2026, 9, 16, 6) and k == "ERROR")
    nw = sum(1 for t, k in ev if D(2026, 9, 15, 22) <= t < D(2026, 9, 16, 6) and k == "WARN")
    assert n != nw and n > 5
    f = {"sync.log": "\n".join(lines) + "\n"}
    make("log-33751", sub="window", task_type="time_window", desc="Last night 22:00 to this morning 06:00 relative to the fixed date",
         files=f, turns=[T("今天是 2026-09-16。sync.log 里昨晚 22:00 到今天早上 06:00 之间一共有多少条 ERROR？", [str(n)], token=True, req=["bash"]),
                         T("WARN 呢？", [str(nw)], token=True)],
         truth="rows=[l for l in files['sync.log'].splitlines() if '2026-09-15 22:00:00'<=l[:19]<'2026-09-16 06:00:00']\nanswers=[str(sum(1 for l in rows if '[ERROR]' in l)), str(sum(1 for l in rows if '[WARN]' in l))]",
         ref=[("awk '($1==\"2026-09-15\" && $2>=\"22:00:00\") || ($1==\"2026-09-16\" && $2<\"06:00:00\")' sync.log | grep -c ERROR", str(n))],
         notes={"traps": "Crosses a date boundary; evening events before 22:00 and morning events after 06:00 must be excluded.", "steps": "awk two-date window.", "unique": "ERROR %d WARN %d" % (n, nw)},
         traps=("TR-DATEFMT", "TR-DECOY"), axes=("OBS",), rc=5)


@reg
def w8():
    r = rng("w8")
    ts = stamps(r, D(2026, 9, 9, 11, 40), D(2026, 9, 9, 12, 50), 190)
    ts += [D(2026, 9, 9, 12, 0, 0), D(2026, 9, 9, 12, 0, 0), D(2026, 9, 9, 12, 30, 0), D(2026, 9, 9, 12, 30, 0), D(2026, 9, 9, 12, 29, 59)]
    ts.sort()
    kinds = ["login ok"] * 6 + ["login failed"] * 2 + ["logout"] * 2
    ev = [(t, r.choice(kinds)) for t in ts]
    for i, t in enumerate(ts):
        if t in (D(2026, 9, 9, 12, 0, 0), D(2026, 9, 9, 12, 30, 0), D(2026, 9, 9, 12, 29, 59)):
            ev[i] = (t, "login failed")
    lines = ["%s %s user=u%d" % (t.strftime("%H:%M:%S"), k.replace(" ", "_"), r.randint(100, 999)) for t, k in ev]
    lo, hi = D(2026, 9, 9, 12, 0), D(2026, 9, 9, 12, 30)
    n = sum(1 for t, k in ev if lo <= t < hi and k == "login failed")
    n2 = sum(1 for t, k in ev if lo <= t <= hi and k == "login failed")
    assert n2 > n
    f = {"auth.log": "\n".join(lines) + "\n"}
    make("log-33752", sub="window", task_type="time_window", desc="Half-open window with events exactly on both boundaries",
         files=f, turns=[T("Count the login_failed events in auth.log from 12:00:00 up to but not including 12:30:00.", [str(n)], token=True, req=["bash"])],
         truth="answers=[str(sum(1 for l in files['auth.log'].splitlines() if '12:00:00'<=l.split()[0]<'12:30:00' and l.split()[1]=='login_failed'))]",
         ref=[("awk '$1>=\"12:00:00\" && $1<\"12:30:00\" && $2==\"login_failed\"' auth.log | wc -l", str(n))],
         notes={"traps": "An event at exactly 12:30:00 must be excluded and 12:00:00 included; closed interval gives %d." % n2, "steps": "awk half-open range.", "unique": "%d" % n},
         traps=("TR-DEFN", "TR-DECOY"), axes=("OBS",), rc=4)


@reg
def w9():
    r = rng("w9")
    ev = []
    for day, c in ((13, 38), (14, 52), (15, 31)):
        for _ in range(c):
            ev.append((D(2026, 9, day, r.randint(0, 23), r.randint(0, 59), r.randint(0, 59)), r.choice(["ERROR", "ERROR", "ERROR", "INFO", "INFO", "INFO", "INFO", "WARN"])))
    ev.sort()
    lines = ["%s %s [%s] job %s" % (t.strftime("%d/%m/%Y"), t.strftime("%H:%M:%S"), k, r.choice(["export", "import", "cleanup", "sync"])) for t, k in ev]
    c14 = sum(1 for t, k in ev if t.day == 14 and k == "ERROR"); c15 = sum(1 for t, k in ev if t.day == 15 and k == "ERROR")
    assert c14 != c15
    f = {"jobs.log": "\n".join(lines) + "\n"}
    diff = abs(c14 - c15)
    make("log-33753", sub="window", task_type="time_window", desc="Per-day ERROR counts in dd/mm/yyyy dates and their difference",
         files=f, turns=[T("jobs.log 里 9 月 14 号一共有多少条 ERROR？（日期格式是 日/月/年）", [str(c14)], token=True, req=["bash"]),
                         T("15 号的呢？比 14 号多还是少，差几条？", [str(c15), str(diff)], token=True)],
         truth="a=sum(1 for l in files['jobs.log'].splitlines() if l.startswith('14/09/2026') and '[ERROR]' in l)\nb=sum(1 for l in files['jobs.log'].splitlines() if l.startswith('15/09/2026') and '[ERROR]' in l)\nanswers=[str(a), str(b)]",
         ref=[("grep '^14/09/2026' jobs.log | grep -c ERROR", str(c14))],
         notes={"traps": "dd/mm/yyyy; 14/09 vs 09/14 confusion; three days present.", "steps": "grep per day.", "unique": "14th %d, 15th %d" % (c14, c15)},
         traps=("TR-DATEFMT", "TR-DECOY"), axes=("OBS",), rc=5)
