"""E1 big logs, cases log-34401..34413."""
import datetime as dt
from common import *
from lg import *

B = []


def reg(f):
    B.append(f)
    return f


D = dt.datetime
OK_STATUS = [200] * 30 + [304] * 6 + [301] * 2 + [404] * 4 + [499]


def acc_gen(extra=None, bad=()):
    sts = [s for s in (extra or OK_STATUS) if s not in bad]

    def g(r, i, ts):
        return access_line(r, ts, status=pick(r, sts))
    return g


@reg
def c01():
    r = rng("c01"); n = 2600
    plants = {1388: lambda ts: access_line(r, ts, 502, "/api/orders"), 1760: lambda ts: access_line(r, ts, 502, "/api/pay"),
              2301: lambda ts: access_line(r, ts, 502, "/api/cart"), 640: lambda ts: access_line(r, ts, 500, "/api/orders"),
              905: lambda ts: access_line(r, ts, 503, "/api/search")}
    lines = build(r, n, D(2026, 9, 13, 6, 0, 0), 6 * 3600, acc_gen(bad=(502, 500, 503)), plants)
    f = {"logs/edge-proxy-0913.log": text(lines)}
    make("log-34401", sub="E1", task_type="locate_error", desc="Nginx access log, first 502 deep in the file, then total 502 count",
         files=f, shape="log", rc=4,
         turns=[T("logs/edge-proxy-0913.log 里第一次出现 502 状态码是几点几分几秒？"), T("那 502 一共出现了多少次？", "i")],
         truth="import re\nls = [l for l in files['logs/edge-proxy-0913.log'].split('\\n') if l]\nh = [l for l in ls if re.search(r'\" 502 ', l)]\nanswers = [[re.search(r':(\\d\\d:\\d\\d:\\d\\d) ', h[0]).group(1)], len(h)]\n",
         ref=[("wc -l logs/edge-proxy-0913.log; grep -n '\" 502 ' logs/edge-proxy-0913.log | head -1", lambda a: a[0][0]), ("grep -c '\" 502 ' logs/edge-proxy-0913.log", lambda a: str(a[1]))],
         notes={"traps": "First screen of logs/edge-proxy-0913.log shows only 200/304/404; the first 502 is at line 1389. 500 and 503 appear earlier and are not 502.",
                "steps": "wc -l / head to see format, grep -n '\" 502 ' | head -1, then grep -c.", "unique": "verify.py recomputes the first 502 time and the total from the fixture."})


@reg
def c02():
    r = rng("c02"); n = 3100
    base = acc_gen(OK_STATUS + [500] * 2)
    plants = {}
    for k in range(23):
        plants[1100 + k * 7] = (lambda ts: access_line(r, ts, 500))
    lines = build(r, n, D(2026, 9, 14, 8, 0, 0), 4 * 3600, base, plants)
    f = {"logs/storefront-nginx-0914.log": text(lines)}
    make("log-34402", sub="E1", task_type="count_events", desc="Count 500 responses inside a half hour window of a 3100-line access log",
         files=f, shape="log", rc=3,
         turns=[T("How many requests in logs/storefront-nginx-0914.log returned status 500 between 09:00:00 and 09:29:59 (inclusive)?", "i")],
         truth="import re\nls = [l for l in files['logs/storefront-nginx-0914.log'].split('\\n') if l]\nc = 0\nfor l in ls:\n    m = re.search(r'\\[[^:]+:(\\d\\d):(\\d\\d):\\d\\d [^\\]]*\\] \"[^\"]*\" (\\d+) ', l)\n    if m and m.group(3) == '500' and m.group(1) == '09' and int(m.group(2)) < 30:\n        c += 1\nanswers = [c]\n",
         ref=[("grep '\" 500 ' logs/storefront-nginx-0914.log | grep -c -E ':09:[0-2][0-9]:[0-9][0-9] '", lambda a: str(a[0]))],
         notes={"traps": "500 responses also appear outside the window; the file has 3100 lines so the first screen is useless.", "steps": "wc -l, head -3, grep 500 | grep -c time pattern.", "unique": "Count is recomputed from the fixture by verify.py."})


def scatter(r, n, counts, lo=60):
    """distinct indices for each key: returns {idx: key}."""
    total = sum(counts.values())
    idxs = r.sample(range(lo, n), total)
    out, k = {}, 0
    for key, c in counts.items():
        for _ in range(c):
            out[idxs[k]] = key
            k += 1
    return out


@reg
def c03():
    r = rng("c03"); n = 2900
    errs = {"connection reset by peer": 27, "upstream timeout after 30s": 41, "disk quota exceeded on /data": 12,
            "tls handshake failed": 19, "invalid session token": 8}
    sc = scatter(r, n, errs)
    plants = {i: (lambda ts, m=m: app_line(ts, "ERROR", pick(r, ["gateway", "worker"]), m)) for i, m in sc.items()}
    lines = build(r, n, D(2026, 9, 11, 7, 0, 0), 9 * 3600, app_gen(["gateway", "worker", "scheduler", "store"]), plants)
    f = {"logs/mesh-sidecar-0911.log": text(lines)}
    make("log-34403", sub="E1", task_type="count_events", desc="Most frequent ERROR message across a 2900-line service log",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("logs/mesh-sidecar-0911.log 里 ERROR 级别的报错有好几种，哪一种出现次数最多？告诉我报错内容和出现了多少次。", "s")],
         truth="import collections\nls = [l for l in files['logs/mesh-sidecar-0911.log'].split('\\n') if ' ERROR ' in l]\nc = collections.Counter(l.split(': ', 1)[1] for l in ls)\nm, k = c.most_common(1)[0]\nanswers = [[m, str(k)]]\n",
         ref=[("grep ' ERROR ' logs/mesh-sidecar-0911.log | sed 's/^[^:]*:[^:]*:[^:]*: //' | sort | uniq -c | sort -rn | head -3", lambda a: a[0][1])],
         notes={"traps": "Five ERROR messages with close counts; the first screen shows a different one first. Needs a full-file count.", "steps": "head to see format; grep ' ERROR ' | sed | sort | uniq -c | sort -rn.", "unique": "Counts are separated by at least 8."})


@reg
def c04():
    r = rng("c04"); n = 3300
    pos = 2124

    def mk(job):
        def p(k):
            return lambda ts: app_line(ts, *k)
        return p
    seq = {pos - 4: ("INFO", "etl", "import job imp-4471 started rows=1200000"), pos - 3: ("WARN", "etl", "heap usage 88%"),
           pos - 2: ("WARN", "etl", "heap usage 96%"), pos - 1: ("INFO", "etl", "spilling partition p17 to disk"),
           pos: ("ERROR", "etl", "java.lang.OutOfMemoryError: Java heap space"),
           pos + 700: ("ERROR", "etl", "java.lang.OutOfMemoryError: Java heap space"),
           pos - 900: ("INFO", "etl", "import job imp-3309 started rows=88000"), pos - 880: ("INFO", "etl", "import job imp-3309 finished in 41s")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 9, 1, 0, 0), 20 * 3600, app_gen(["etl", "api", "cron", "store"]), plants)
    f = {"etl.log": text(lines)}
    make("log-34404", sub="E1", task_type="root_cause", desc="Find the first OutOfMemoryError by grep -n and read the lines around it to name the import job",
         files=f, shape="log", rc=4,
         turns=[T("etl.log 里第一次 OutOfMemoryError 是在哪个导入任务运行时发生的？给我任务编号。", "s", req=("bash", "read_file"))],
         truth="ls = files['etl.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'OutOfMemoryError' in l][0]\nj = [k for k in range(i - 1, -1, -1) if 'import job' in ls[k] and 'started' in ls[k]][0]\nimport re\nanswers = [[re.search(r'imp-\\d+', ls[j]).group(0)]]\n",
         ref=[("grep -n OutOfMemoryError etl.log | head -1", lambda a: "2125"), ("sed -n '2120,2125p' etl.log", lambda a: a[0][0])],
         notes={"traps": "An earlier, finished job imp-3309 is a decoy; the job running at the OOM is imp-4471, started four lines earlier.", "steps": "grep -n OutOfMemoryError | head -1 -> line 2125; read_file path=etl.log start_line=2118 end_line=2126.", "unique": "The job started right before the first OOM is imp-4471."})


def sshd_gen(r, i, ts):
    u = pick(r, ["alice", "bob", "carol", "deploy", "ops", "backup"])
    k = r.randint(0, 9)
    if k < 6:
        return "%s web01 sshd[%d]: Connection closed by %s port %d" % (sysl(ts), r.randint(1000, 30000), ip(r), r.randint(30000, 65000))
    if k < 8:
        return "%s web01 CRON[%d]: (%s) CMD (/usr/local/bin/rotate.sh)" % (sysl(ts), r.randint(1000, 30000), u)
    return "%s web01 sshd[%d]: Failed password for invalid user %s from %s" % (sysl(ts), r.randint(1000, 30000), pick(r, ["test", "admin", "guest"]), ip(r))


@reg
def c05():
    r = rng("c05"); n = 3400
    acc = lambda u: (lambda ts: "%s web01 sshd[%d]: Accepted publickey for %s from 10.20.%d.%d port %d ssh2" % (sysl(ts), r.randint(1000, 30000), u, r.randint(0, 9), r.randint(2, 250), r.randint(30000, 65000)))
    plants = {300: acc("alice"), 910: acc("ops"), 1655: acc("deploy"), 2240: acc("deploy"), 3010: acc("bob")}
    lines = build(r, n, D(2026, 9, 6, 0, 5, 0), 23 * 3600, sshd_gen, plants)
    f = {"auth.log": text(lines)}
    make("log-34405", sub="E1", task_type="locate_error", desc="Time of the first publickey login of user deploy in a syslog-style auth log",
         files=f, shape="log", rc=3, deep=False,
         turns=[T("At what time (HH:MM:SS) did user deploy first log in with a public key according to auth.log?"),
                T("And how many successful public-key logins are there in the whole file, for all users?", "i")],
         truth="ls = [l for l in files['auth.log'].split('\\n') if l]\nh = [l for l in ls if 'Accepted publickey for deploy' in l]\nanswers = [[h[0].split()[2]], len([l for l in ls if 'Accepted publickey' in l])]\n",
         ref=[("grep -n 'Accepted publickey for deploy' auth.log | head -1", lambda a: a[0][0]), ("grep -c 'Accepted publickey' auth.log", lambda a: str(a[1]))],
         notes={"traps": "Other users logged in earlier; Failed password lines dominate the first screen.", "steps": "grep -n for the user, head -1; grep -c for all.", "unique": "deploy first logs in around line 1656."})


@reg
def c06():
    r = rng("c06"); n = 2700
    gen = jsonl_gen(["cart", "search", "billing", "profile"])
    pl = lambda svc, msg: (lambda ts: jsonl_line(ts, "error", svc, msg, ',"ms":%d' % r.randint(900, 5000)))
    plants = {1503: pl("billing", "ledger write rejected: duplicate key"), 1720: pl("cart", "stock service unavailable"),
              2200: pl("billing", "ledger write rejected: duplicate key")}
    lines = build(r, n, D(2026, 9, 12, 12, 0, 0), 5 * 3600, gen, plants)
    f = {"events.jsonl": text(lines)}
    make("log-34406", sub="E1", task_type="aggregate_jsonl", desc="JSON lines log: first lvl=error line number and its service and message",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("events.jsonl 每行是一条 JSON。level 为 error 的第一条在第几行？", "s"), T("它是哪个服务（svc）报的，消息是什么？")],
         truth="import json\nls = [l for l in files['events.jsonl'].split('\\n') if l]\ni = [k for k, l in enumerate(ls) if json.loads(l)['lvl'] == 'error'][0]\nd = json.loads(ls[i])\nanswers = [[str(i + 1)], [d['svc'], d['msg']]]\n",
         ref=[("grep -n '\"lvl\":\"error\"' events.jsonl | head -1", lambda a: a[0][0]), ],
         notes={"traps": "Warn lines also look alarming; the first error is at line 1504.", "steps": "grep -n '\"lvl\":\"error\"' | head -1.", "unique": "Single first error line."})


@reg
def c07():
    r = rng("c07"); n = 3600
    msgs = ["订单 {n} 创建成功", "库存同步完成，耗时 {ms}ms", "缓存命中 key=商品:{n}", "支付回调已处理 流水 {n}", "用户 {n} 登录", "定时任务 {w} 已执行"]
    comps = ["订单服务", "库存服务", "支付服务", "网关"]
    base = zh_gen(comps, msgs)
    err = lambda ts: "%s [错误] %s: %s" % (iso(ts), pick(r, comps), pick(r, ["支付回调验签失败", "库存扣减冲突", "下游接口超时", "数据库连接池耗尽"]))
    idx = r.sample(range(100, n), 61)
    lines = build(r, n, D(2026, 9, 15, 9, 0, 0), 8 * 3600, base, {i: err for i in idx})
    f = {"logs/订单中台-0915.log": text(lines)}
    make("log-34407", sub="E1", task_type="time_window", desc="Chinese-level log, count error lines within one clock hour",
         files=f, shape="log", rc=3, deep=False,
         turns=[T("logs/订单中台-0915.log 里 14:00 到 14:59 这一个小时内，级别是“错误”的日志有多少条？", "i")],
         truth="ls = [l for l in files['logs/订单中台-0915.log'].split('\\n') if l]\nanswers = [len([l for l in ls if ' [错误] ' in l and l[11:13] == '14'])]\n",
         ref=[("grep ' \\[错误\\] ' logs/订单中台-0915.log | grep -c -E '^2026-09-15 14:'", lambda a: str(a[0]))],
         notes={"traps": "Level is written in Chinese in brackets; errors exist in all hours.", "steps": "head -3 to see the format; grep 错误 | grep -c '^date 14:'.", "unique": "Recomputed from the fixture."})


@reg
def c08():
    r = rng("c08"); n = 2400
    def g(r, i, ts):
        return "%s [db] query=q-%d duration=%dms rows=%d" % (iso(ts), r.randint(10000, 99999), r.randint(3, 480), r.randint(0, 900))
    slow = lambda ms: (lambda ts: "%s [db] query=q-%d duration=%dms rows=%d" % (iso(ts), r.randint(10000, 99999), ms, r.randint(0, 900)))
    plants = {412: slow(1930), 1180: slow(3470), 1731: slow(8215), 2012: slow(5090)}
    lines = build(r, n, D(2026, 9, 16, 2, 0, 0), 6 * 3600, g, plants)
    f = {"slowquery.log": text(lines)}
    make("log-34408", sub="E1", task_type="aggregate_jsonl", desc="Slowest query in a 2400-line db log",
         files=f, shape="log", rc=3, deep=False,
         turns=[T("Which query in slowquery.log took the longest, and how many milliseconds did it take? Give the query id and the duration.")],
         truth="import re\nbest = max(((int(re.search(r'duration=(\\d+)ms', l).group(1)), re.search(r'query=(q-\\d+)', l).group(1)) for l in files['slowquery.log'].split('\\n') if l))\nanswers = [[best[1], str(best[0])]]\n",
         ref=[("sed 's/.*query=\\(q-[0-9]*\\) duration=\\([0-9]*\\)ms.*/\\2 \\1/' slowquery.log | sort -rn | head -2", lambda a: a[0][0])],
         notes={"traps": "Several slow queries; only a full scan finds the maximum, and it is not the first slow one.", "steps": "sed/awk extract duration, sort -rn | head.", "unique": "Single maximum duration."})


def sep_lines(r, n, t0, span, comps, plants, fmt=None):
    return build(r, n, t0, span, app_gen(comps), plants)


@reg
def c09():
    r = rng("c09"); n = 3000; p = 1987
    seq = {p: ("ERROR", "store", "write failed: No space left on device (/var/lib/app)"), p + 1: ("WARN", "store", "emergency cleanup started"),
           p + 2: ("INFO", "store", "removed 214 files from /var/lib/app/tmp-spool"), p + 3: ("INFO", "store", "cleanup finished, freed 3.1GB"),
           700: ("INFO", "store", "removed 12 files from /var/lib/app/old-exports"), 2600: ("ERROR", "store", "write failed: No space left on device (/var/lib/app)")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 10, 3, 0, 0), 14 * 3600, app_gen(["store", "api", "cron", "queue"]), plants)
    f = {"store.log": text(lines)}
    make("log-34409", sub="E1", task_type="root_cause", desc="After the first disk-full error, which directory did the emergency cleanup clear",
         files=f, shape="log", rc=4,
         turns=[T("store.log 第一次出现磁盘写满（No space left on device）之后，紧接着的清理动作清掉的是哪个目录？", "s", req=("bash", "read_file"))],
         truth="ls = files['store.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'No space left' in l][0]\nj = [k for k in range(i, i + 6) if 'removed' in ls[k]][0]\nanswers = [[ls[j].split(' from ')[1].split(' ')[0].rsplit('/', 1)[1]]]\n",
         ref=[("grep -n 'No space left' store.log | head -1", lambda a: "1988"), ("sed -n '1988,1992p' store.log", lambda a: a[0][0])],
         notes={"traps": "An older cleanup of old-exports (line 701) is a decoy; the cleanup after the first error removed tmp-spool.", "steps": "grep -n -> line 1988, read_file start_line=1988 to see the next lines.", "unique": "tmp-spool."})


@reg
def c10():
    r = rng("c10"); n = 3200
    sc = scatter(r, n, {"/api/v1/export": 46, "/favicon.ico": 31, "/wp-login.php": 22, "/api/v1/legacy/sync": 14})
    plants = {i: (lambda ts, p=p: access_line(r, ts, 404, p, "GET")) for i, p in sc.items()}
    lines = build(r, n, D(2026, 9, 17, 10, 0, 0), 5 * 3600, acc_gen([s for s in OK_STATUS if s != 404]), plants)
    f = {"logs/cdn-origin-0917.log": text(lines)}
    make("log-34410", sub="E1", task_type="count_events", desc="Path with the most 404 responses, then the total 404 count",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("看看 logs/cdn-origin-0917.log，被请求了却找不到（404）次数最多的是哪个路径？", "s"), T("这类找不到的请求，整个文件里总共有多少条？", "i")],
         truth="import re, collections\nh = [re.search(r'\"[A-Z]+ (\\S+) HTTP', l).group(1) for l in files['logs/cdn-origin-0917.log'].split('\\n') if '\" 404 ' in l]\nm = collections.Counter(h).most_common(1)[0][0]\nanswers = [[m], len(h)]\n",
         ref=[("grep '\" 404 ' logs/cdn-origin-0917.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -3", lambda a: a[0][0]), ("grep -c '\" 404 ' logs/cdn-origin-0917.log", lambda a: str(a[1]))],
         notes={"traps": "Three near-equal 404 paths; first screen has no 404 at all.", "steps": "grep 404 | awk '{print $7}' | sort | uniq -c | sort -rn.", "unique": "/api/v1/export leads clearly."})


@reg
def c11():
    r = rng("c11"); n = 3300
    hours = {7: 6, 8: 9, 9: 11, 10: 14, 11: 8, 12: 31, 13: 12, 14: 9, 15: 7}
    t0 = D(2026, 9, 18, 7, 0, 0)
    lines = build(r, n, t0, 9 * 3600 - 1, app_gen(["api", "worker", "scheduler", "store"]), {})
    out, per = [], {}
    for k, l in enumerate(lines):
        out.append(l)
    # turn some existing lines into ERROR lines according to the per-hour quota
    for h, q in hours.items():
        cand = [k for k, l in enumerate(out) if l[11:13] == "%02d" % h and k > 60 and " ERROR " not in l]
        for k in r.sample(cand, q):
            ts = D.strptime(out[k][:19], "%Y-%m-%d %H:%M:%S")
            out[k] = app_line(ts, "ERROR", pick(r, ["api", "worker", "store"]), pick(r, ["request failed code=%d" % r.randint(500, 504), "task aborted: lock timeout", "write rejected: read-only replica"]))
    f = {"logs/ledger-worker-0918.log": text(out)}
    make("log-34411", sub="E1", task_type="time_window", desc="Which hour of the day has the most ERROR lines",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("In logs/ledger-worker-0918.log, which hour of the day had the most ERROR lines? Answer in the form HH:00 and tell me the count.")],
         truth="import collections\nc = collections.Counter(l[11:13] for l in files['logs/ledger-worker-0918.log'].split('\\n') if ' ERROR ' in l)\nh, k = c.most_common(1)[0]\nanswers = [[h + ':00', str(k)]]\n",
         ref=[("grep ' ERROR ' logs/ledger-worker-0918.log | cut -c12-13 | sort | uniq -c | sort -rn | head -3", lambda a: a[0][1])],
         notes={"traps": "Error counts per hour are close except hour 12; per-hour totals need a full pass.", "steps": "grep ERROR | cut -c12-13 | sort | uniq -c | sort -rn.", "unique": "Hour 12 clearly leads."})


@reg
def c12():
    r = rng("c12"); n = 3800
    rid = "req-7f3a91"
    seq = {2390: ("INFO", "gw", "%s received POST /api/pay user=u-5521" % rid), 2391: ("INFO", "pay", "%s card auth requested amount=12900" % rid),
           2396: ("WARN", "pay", "%s auth gateway slow 4210ms" % rid), 2402: ("ERROR", "pay", "%s card auth declined code=E-402 reason=insufficient funds" % rid),
           2403: ("INFO", "gw", "%s responded 402 in 4630ms" % rid)}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    plants[900] = lambda ts: app_line(ts, "ERROR", "pay", "req-7f3a90 card auth declined code=E-510 reason=issuer unavailable")
    lines = build(r, n, D(2026, 9, 19, 0, 0, 0), 23 * 3600, app_gen(["gw", "pay", "cart", "auth"]), plants)
    f = {"gateway.log": text(lines)}
    make("log-34412", sub="E1", task_type="root_cause", desc="Follow a request id through a 3800-line log to find the error code and reason",
         files=f, shape="log", rc=5, deep=False,
         turns=[T("gateway.log 里请求 req-7f3a91 最后失败的原因是什么？给出错误码和原因。", "s", req=("bash", "read_file"))],
         truth="ls = [l for l in files['gateway.log'].split('\\n') if 'req-7f3a91 card auth declined' in l]\nimport re\nm = re.search(r'code=(E-\\d+) reason=(.*)$', ls[0])\nanswers = [[m.group(1), m.group(2)]]\n",
         ref=[("grep -n 'req-7f3a91' gateway.log", lambda a: a[0][0]), ("sed -n '2400,2404p' gateway.log", lambda a: a[0][1])],
         notes={"traps": "Neighbouring id req-7f3a90 failed too with a different code (E-510) near the top; only grep for the exact id.", "steps": "grep -n req-7f3a91 -> lines 2391-2404; optionally read_file around them.", "unique": "E-402 insufficient funds."})


@reg
def c13():
    r = rng("c13"); n = 2900; p = 1716
    seq = {p: ("ERROR", "db", "deadlock detected on table orders"), p + 1: ("ERROR", "db", "victim transaction tx-90417 rolled back"),
           p + 2: ("INFO", "db", "tx-90417 retry scheduled in 200ms"), p + 3: ("INFO", "db", "tx-90418 committed"),
           400: ("WARN", "db", "lock wait 1800ms on table orders"), 2500: ("ERROR", "db", "deadlock detected on table payments"),
           2501: ("ERROR", "db", "victim transaction tx-91204 rolled back")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 20, 5, 0, 0), 12 * 3600, app_gen(["db", "api", "cron", "cache"]), plants)
    f = {"db.log": text(lines)}
    make("log-34413", sub="E1", task_type="root_cause", desc="First deadlock: name the table and the rolled back transaction on the next line",
         files=f, shape="log", rc=4,
         turns=[T("db.log 里第一次死锁（deadlock）是哪张表？被回滚的是哪个事务？", "s", req=("bash", "read_file"))],
         truth="ls = files['db.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'deadlock detected' in l][0]\nimport re\nanswers = [[ls[i].rsplit(' ', 1)[1], re.search(r'tx-\\d+', ls[i + 1]).group(0)]]\n",
         ref=[("grep -n 'deadlock detected' db.log | head -1", lambda a: "1717"), ("sed -n '1717,1719p' db.log", lambda a: a[0][1])],
         notes={"traps": "A second deadlock on payments appears later; the victim is on the line after the first one.", "steps": "grep -n 'deadlock' | head -1 -> 1717; read_file start_line=1717 end_line=1720.", "unique": "orders / tx-90417."})
