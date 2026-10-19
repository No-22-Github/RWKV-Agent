"""E1 big logs, cases log-34414..34425."""
import datetime as dt
from common import *
from lg import *
from e1a import scatter, acc_gen, OK_STATUS

B = []


def reg(f):
    B.append(f)
    return f


D = dt.datetime
STEPS = ["checkout", "deps:fetch", "compile:core", "compile:api", "lint", "unit:core", "unit:api", "package", "scan:licenses", "publish:staging"]


def ci_line(ts, job, step, st, dur):
    return "%s [ci] job=build-%d step=%s status=%s dur=%ds" % (iso(ts), job, step, st, dur)


@reg
def c14():
    r = rng("c14"); n = 2800
    def g(r, i, ts):
        return ci_line(ts, 8000 + i // 10, STEPS[i % 10], pick(r, ["ok"] * 12 + ["cached"] * 3 + ["skipped"]), r.randint(1, 240))
    fails = {1470: "integration:payments", 1893: "unit:api", 2310: "integration:payments"}
    plants = {i: (lambda ts, s=s, i=i: ci_line(ts, 8000 + i // 10, s, "failed", r.randint(30, 300))) for i, s in fails.items()}
    lines = build(r, n, D(2026, 9, 21, 1, 0, 0), 10 * 3600, g, plants)
    f = {"ci.log": text(lines)}
    make("log-34414", sub="E1", task_type="locate_error", desc="CI log: first failed step and total number of failed steps",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("ci.log 里第一个失败（status=failed）的步骤叫什么？"), T("整个日志里一共失败了几个步骤？", "i")],
         truth="ls = [l for l in files['ci.log'].split('\\n') if 'status=failed' in l]\nimport re\nanswers = [[re.search(r'step=(\\S+)', ls[0]).group(1)], len(ls)]\n",
         ref=[("grep -n 'status=failed' ci.log | head -1", lambda a: a[0][0]), ("grep -c 'status=failed' ci.log", lambda a: str(a[1]))],
         notes={"traps": "Only skipped/cached/ok in the first screen; 'failed' appears for the first time at line 1471.", "steps": "grep -n failed | head -1; grep -c.", "unique": "integration:payments first, 3 failures."})


@reg
def c15():
    r = rng("c15"); n = 3000
    jobs = ["backup", "rotate", "cleanup", "report", "sync"]
    def line(ts, job, code, r=r):
        return "%s db01 cron-wrap[%d]: job=%s exit=%d dur=%ds" % (sysl(ts), r.randint(1000, 30000), job, code, r.randint(1, 900))
    g = lambda r, i, ts: line(ts, pick(r, jobs), 0)
    sc = scatter(r, n, {"backup": 17, "rotate": 25, "report": 6})
    plants = {i: (lambda ts, j=j: line(ts, j, pick(r, [1, 2, 137] if j != "rotate" else [1, 1, 2]))) for i, j in sc.items()}
    lines = build(r, n, D(2026, 9, 22, 0, 0, 0), 23 * 3600, g, plants)
    f = {"cron.log": text(lines)}
    make("log-34415", sub="E1", task_type="count_events", desc="Cron log: non-zero exits of one job, then of another",
         files=f, shape="log", rc=3, deep=False,
         turns=[T("How many times did the backup job in cron.log end with a non-zero exit code?", "i"), T("And the rotate job?", "i")],
         truth="ls = [l for l in files['cron.log'].split('\\n') if l]\nf = lambda j: len([l for l in ls if ' job=%s ' % j in l and ' exit=0 ' not in l])\nanswers = [f('backup'), f('rotate')]\n",
         ref=[("grep ' job=backup ' cron.log | grep -vc ' exit=0 '", lambda a: str(a[0])), ("grep ' job=rotate ' cron.log | grep -vc ' exit=0 '", lambda a: str(a[1]))],
         notes={"traps": "Counting 'exit=' lines or all failures mixes jobs; rotate has more failures than backup.", "steps": "grep job | grep -vc exit=0.", "unique": "Recomputed from fixture."})


@reg
def c16():
    r = rng("c16"); n = 3100; p = 2257
    seq = {p - 3: ("WARN", "mq", "retry 1/3 host=mq-b7 after timeout"), p - 2: ("WARN", "mq", "retry 2/3 host=mq-b7 after timeout"),
           p - 1: ("WARN", "mq", "retry 3/3 host=mq-b7 after timeout"), p: ("ERROR", "mq", "retry limit reached, giving up"),
           800: ("WARN", "mq", "retry 1/3 host=mq-a2 after timeout"), 2900: ("ERROR", "mq", "retry limit reached, giving up")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 23, 4, 0, 0), 15 * 3600, app_gen(["mq", "api", "cron", "cache"]), plants)
    f = {"mq.log": text(lines)}
    make("log-34416", sub="E1", task_type="root_cause", desc="Host that was being retried when the first retry limit error appeared",
         files=f, shape="log", rc=4,
         turns=[T("mq.log 里第一次 “retry limit reached” 之前，一直在重试的是哪台主机？", "s", req=("bash", "read_file"))],
         truth="ls = files['mq.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'retry limit reached' in l][0]\nimport re\nanswers = [[re.search(r'host=(\\S+)', ls[i - 1]).group(1)]]\n",
         ref=[("grep -n 'retry limit reached' mq.log | head -1", lambda a: "2258"), ("sed -n '2255,2258p' mq.log", lambda a: a[0][0])],
         notes={"traps": "mq-a2 retried once much earlier (decoy). The host is only on the lines before the error.", "steps": "grep -n -> 2258; read_file start_line=2254 end_line=2258.", "unique": "mq-b7."})


def ujl(ts, lvl, svc, user, msg, ms):
    return '{"ts":"%s","lvl":"%s","svc":"%s","user":"u%04d","msg":"%s","ms":%d}' % (isoz(ts), lvl, svc, user, msg, ms)


@reg
def c17():
    r = rng("c17"); n = 2600
    g = lambda r, i, ts: ujl(ts, pick(r, ["info"] * 9 + ["warn"]), pick(r, ["cart", "search", "billing", "profile"]), r.randint(1, 900), pick(r, ["ok", "served", "cached"]), r.randint(3, 400))
    lines = build(r, n, D(2026, 9, 24, 9, 0, 0), 6 * 3600, g, {})
    f = {"trace.jsonl": text(lines)}
    make("log-34417", sub="E1", task_type="aggregate_jsonl", desc="Total latency (ms field) of one service in a JSON lines trace",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("Add up the ms field over all trace.jsonl records whose svc is cart. What is the total in milliseconds?", "i")],
         truth="import json\nanswers = [sum(json.loads(l)['ms'] for l in files['trace.jsonl'].split('\\n') if l and json.loads(l)['svc'] == 'cart')]\n",
         ref=[("grep '\"svc\":\"cart\"' trace.jsonl | sed 's/.*\"ms\"://; s/}//' | awk '{s+=$1} END{print s}'", lambda a: str(a[0]))],
         notes={"traps": "ms is the last field; other services have the same field. Needs a full pass.", "steps": "grep svc cart | sed | awk sum.", "unique": "Recomputed from fixture."})


@reg
def c18():
    r = rng("c18"); n = 3000
    g = lambda r, i, ts: ujl(ts, pick(r, ["info"] * 12 + ["debug"] * 3), pick(r, ["cart", "search", "billing"]), r.randint(1, 600), pick(r, ["ok", "served"]), r.randint(3, 300))
    users = [r.randint(1, 600) for _ in range(23)]
    idx = r.sample(range(80, n), 61)
    plants = {j: (lambda ts, j=j: ujl(ts, "error", pick(r, ["cart", "billing"]), users[j % 23], pick(r, ["timeout", "bad request", "quota"]), r.randint(200, 3000))) for j in idx}
    lines = build(r, n, D(2026, 9, 25, 9, 0, 0), 8 * 3600, g, plants)
    f = {"api.jsonl": text(lines)}
    make("log-34418", sub="E1", task_type="aggregate_jsonl", desc="Distinct users who hit an error in a JSON lines log",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("api.jsonl 里有多少个不同的用户（user）遇到过 error 级别的记录？同一个用户多次只算一个。", "i")],
         truth="import json\nu = set(json.loads(l)['user'] for l in files['api.jsonl'].split('\\n') if l and json.loads(l)['lvl'] == 'error')\nanswers = [len(u)]\n",
         ref=[("grep '\"lvl\":\"error\"' api.jsonl | sed 's/.*\"user\":\"\\([^\"]*\\)\".*/\\1/' | sort -u | wc -l", lambda a: str(a[0]))],
         notes={"traps": "61 error lines but fewer distinct users; counting lines gives a wrong answer.", "steps": "grep error | sed user | sort -u | wc -l.", "unique": "Recomputed from fixture."})


@reg
def c19():
    r = rng("c19"); n = 3400
    ips = ["203.0.113.45", "198.51.100.23", "203.0.113.9", "192.0.2.77", "198.51.100.140"]
    sc = scatter(r, n, {ips[0]: 29, ips[1]: 41, ips[2]: 17, ips[3]: 12, ips[4]: 8})
    fp = lambda ts, a: "%s web01 sshd[%d]: Failed password for %s from %s port %d ssh2" % (sysl(ts), r.randint(1000, 30000), pick(r, ["root", "admin", "deploy"]), a, r.randint(30000, 65000))
    plants = {i: (lambda ts, a=a: fp(ts, a)) for i, a in sc.items()}
    def g(r, i, ts):
        if r.randint(0, 3) == 0:
            return "%s web01 CRON[%d]: (root) CMD (/usr/local/bin/rotate.sh)" % (sysl(ts), r.randint(1000, 30000))
        return "%s web01 sshd[%d]: Connection closed by %s port %d" % (sysl(ts), r.randint(1000, 30000), ip(r), r.randint(30000, 65000))
    lines = build(r, n, D(2026, 9, 26, 0, 0, 0), 23 * 3600, g, plants)
    f = {"secure.log": text(lines)}
    make("log-34419", sub="E1", task_type="count_events", desc="Source address with the most failed SSH logins",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("Which IP address has the most 'Failed password' entries in secure.log, and how many does it have?")],
         truth="import collections\nc = collections.Counter(l.split(' from ')[1].split(' ')[0] for l in files['secure.log'].split('\\n') if 'Failed password' in l)\na, k = c.most_common(1)[0]\nanswers = [[a, str(k)]]\n",
         ref=[("grep 'Failed password' secure.log | awk '{print $11}' | sort | uniq -c | sort -rn | head -3", lambda a: a[0][1])],
         notes={"traps": "Five addresses with failures; Connection closed lines carry other IPs.", "steps": "grep Failed | awk field | sort | uniq -c | sort -rn.", "unique": "198.51.100.23 with 41."})


@reg
def c20():
    r = rng("c20"); n = 3600
    t0 = D(2026, 9, 23, 0, 0, 0)
    lines = build(r, n, t0, 3 * 86400 - 1, app_gen(["api", "worker", "scheduler", "store"]), {})
    quota = {"2026-09-23": 13, "2026-09-24": 22, "2026-09-25": 17}
    for d, q in quota.items():
        cand = [k for k, l in enumerate(lines) if l.startswith(d) and k > 60]
        for k in r.sample(cand, q):
            ts = D.strptime(lines[k][:19], "%Y-%m-%d %H:%M:%S")
            lines[k] = app_line(ts, "ERROR", pick(r, ["api", "worker"]), pick(r, ["request failed code=502", "task aborted: lock timeout", "queue full, dropping job"]))
    f = {"logs/批处理-三日合并.log": text(lines)}
    make("log-34420", sub="E1", task_type="time_window", desc="Which of three days in one log file has the most ERROR lines",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("logs/批处理-三日合并.log 这个文件里混着三天的日志，哪一天的 ERROR 最多？告诉我日期和条数。")],
         truth="import collections\nc = collections.Counter(l[:10] for l in files['logs/批处理-三日合并.log'].split('\\n') if ' ERROR ' in l)\nd, k = c.most_common(1)[0]\nanswers = [[d, str(k)]]\n",
         ref=[("grep ' ERROR ' logs/批处理-三日合并.log | cut -c1-10 | sort | uniq -c | sort -rn", lambda a: a[0][1])],
         notes={"traps": "The first screen only covers the first day's morning; per-day totals need the whole file.", "steps": "grep ERROR | cut -c1-10 | sort | uniq -c.", "unique": "2026-09-24 leads (22)."})


@reg
def c21():
    r = rng("c21"); n = 2500; p = 1844
    seq = {p: ("ERROR", "tls", "certificate expired for CN=api.internal"), p + 1: ("WARN", "tls", "disabling endpoint host=api-eu-3 until renewal"),
           p + 2: ("INFO", "tls", "renewal ticket opened id=CRT-88"), 300: ("WARN", "tls", "certificate expires in 14 days for CN=api.internal"),
           2300: ("ERROR", "tls", "certificate expired for CN=pay.internal"), 2301: ("WARN", "tls", "disabling endpoint host=pay-us-1 until renewal")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 27, 6, 0, 0), 12 * 3600, app_gen(["tls", "api", "cron", "cache"]), plants)
    f = {"edge.log": text(lines)}
    make("log-34421", sub="E1", task_type="root_cause", desc="Host disabled right after the first certificate expiry",
         files=f, shape="log", rc=4,
         turns=[T("Look at edge.log: right after the first 'certificate expired' error, which host was disabled?", "s", req=("bash", "read_file"))],
         truth="ls = files['edge.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'certificate expired' in l][0]\nimport re\nanswers = [[re.search(r'host=(\\S+)', ls[i + 1]).group(1)]]\n",
         ref=[("grep -n 'certificate expired' edge.log | head -1", lambda a: "1845"), ("sed -n '1845,1847p' edge.log", lambda a: a[0][0])],
         notes={"traps": "A later expiry disables pay-us-1 (decoy); a 14-days warning near the top contains similar words.", "steps": "grep -n -> 1845; read_file start_line=1845 end_line=1848.", "unique": "api-eu-3."})


@reg
def c22():
    r = rng("c22"); n = 3500
    seq = {600: ("WARN", "kernel", "oom-killer invoked by java (cgroup limit 2G)"), 601: ("ERROR", "svc", "service restarted by supervisor"),
           1900: ("ERROR", "kernel", "segfault in libssl at 0x7f3a"), 1901: ("ERROR", "svc", "service restarted by supervisor"),
           3170: ("WARN", "kernel", "watchdog: no heartbeat for 60s"), 3171: ("ERROR", "svc", "service restarted by supervisor"),
           3340: ("INFO", "svc", "restart count reset")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 28, 0, 0, 0), 23 * 3600, app_gen(["svc", "api", "cron", "cache"]), plants)
    f = {"supervisor.log": text(lines)}
    make("log-34422", sub="E1", task_type="root_cause", desc="Reason logged right before the last service restart",
         files=f, shape="log", rc=4,
         turns=[T("supervisor.log 里服务最近一次被重启，是因为什么？看重启前一条日志。", "s", req=("bash", "read_file"))],
         truth="ls = files['supervisor.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'service restarted' in l][-1]\nanswers = [[ls[i - 1].split(': ', 1)[1].split(':')[0]]]\n",
         ref=[("grep -n 'service restarted' supervisor.log | tail -1", lambda a: "3172"), ("sed -n '3171,3172p' supervisor.log", lambda a: "watchdog")],
         notes={"traps": "Three restarts with different causes; the earlier ones are in the first half of the file.", "steps": "grep -n 'service restarted' | tail -1 -> 3172; read_file start_line=3170 end_line=3173.", "unique": "watchdog (no heartbeat for 60s)."})


@reg
def c23():
    r = rng("c23"); n = 3200
    codes = ["E-%d" % c for c in (101, 102, 207, 311, 318, 404, 409, 500, 503, 612, 705, 811, 903)]
    def g(r, i, ts):
        if r.randint(0, 7) == 0:
            return app_line(ts, "ERROR", pick(r, ["api", "worker"]), "request rejected code=%s" % pick(r, codes))
        return app_gen(["api", "worker", "store"])(r, i, ts)
    lines = build(r, n, D(2026, 9, 29, 8, 0, 0), 10 * 3600, g, {})
    f = {"errors.log": text(lines)}
    make("log-34423", sub="E1", task_type="count_events", desc="Number of distinct error codes in a 3200-line log",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("How many different error codes (the code=E-… values) appear in errors.log? Each distinct code counts once.", "i")],
         truth="import re\nanswers = [len(set(re.findall(r'code=(E-\\d+)', files['errors.log'])))]\n",
         ref=[("grep -o 'code=E-[0-9]*' errors.log | sort -u | wc -l", lambda a: str(a[0]))],
         notes={"traps": "The first screen shows only part of the code set; counting lines instead of distinct codes is wrong.", "steps": "grep -o 'code=E-[0-9]*' | sort -u | wc -l.", "unique": "Thirteen codes are possible; the exact number is recomputed."})


@reg
def c24():
    r = rng("c24"); n = 2900; p = 2038
    seq = {p - 2: ("INFO", "migrate", "applying migration 0042_add_index table=invoices"), p - 1: ("INFO", "migrate", "building index idx_invoices_customer"),
           p: ("ERROR", "migrate", "migration failed: lock wait timeout"), p + 1: ("WARN", "migrate", "rolled back to 0041"),
           300: ("INFO", "migrate", "applying migration 0039_add_column table=users"), 301: ("INFO", "migrate", "migration 0039 applied")}
    plants = {i: (lambda ts, k=k: app_line(ts, *k)) for i, k in seq.items()}
    lines = build(r, n, D(2026, 9, 30, 1, 0, 0), 9 * 3600, app_gen(["migrate", "api", "cron"]), plants)
    f = {"deploy.log": text(lines)}
    make("log-34424", sub="E1", task_type="root_cause", desc="Which table the first failed migration was working on",
         files=f, shape="log", rc=4,
         turns=[T("deploy.log 里第一次 “migration failed” 的时候，正在处理的是哪张表？前两行有线索。", "s", req=("bash", "read_file")),
                T("那次失败之后回滚到了哪个版本？")],
         truth="ls = files['deploy.log'].split('\\n')\ni = [k for k, l in enumerate(ls) if 'migration failed' in l][0]\nimport re\nanswers = [[re.search(r'table=(\\S+)', ls[i - 2]).group(1)], [re.search(r'rolled back to (\\d+)', ls[i + 1]).group(1)]]\n",
         ref=[("grep -n 'migration failed' deploy.log | head -1", lambda a: "2039"), ("sed -n '2037,2040p' deploy.log", lambda a: a[0][0])],
         notes={"traps": "Migration 0039 (table users) appears early and succeeded, a decoy.", "steps": "grep -n -> 2039; read_file start_line=2037 end_line=2041.", "unique": "invoices; rolled back to 0041."})


@reg
def c25():
    r = rng("c25"); n = 2100
    mk = lambda day, seed: build(rng(seed), n, D(2026, 9, day, 0, 0, 0), 86000, acc_gen())
    f = {"logs/shop-front.log": text(mk(30, "c25a")), "logs/shop-front.log.1": text(mk(29, "c25b"))}
    make("log-34425", sub="E1", task_type="count_events", desc="404 count over a current and a rotated access log",
         files=f, shape="log", rc=4, deep=False,
         turns=[T("The rotated file logs/shop-front.log.1 is yesterday's log and logs/shop-front.log is today's. How many 404 responses are there in both files together?", "i"),
                T("How many of them are in today's file?", "i")],
         truth="ls = lambda p: [l for l in files[p].split('\\n') if '\" 404 ' in l]\nanswers = [len(ls('logs/shop-front.log')) + len(ls('logs/shop-front.log.1')), len(ls('logs/shop-front.log'))]\n",
         ref=[("cat logs/shop-front.log logs/shop-front.log.1 | grep -c '\" 404 '", lambda a: str(a[0])), ("grep -c '\" 404 ' logs/shop-front.log", lambda a: str(a[1]))],
         notes={"traps": "Two files; reading only logs/shop-front.log gives the second turn's number for the first question.", "steps": "ls/wc -l to see both files, then grep -c on each or on the cat.", "unique": "Recomputed from the fixtures."})
