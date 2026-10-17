"""logs count_events 33762-33770."""
from common import *
from lg import *

B = []


def reg(f):
    B.append(f)
    return f


def hhmm(r, i, n, a=8 * 3600, b=18 * 3600):
    return tstr(a + (b - a) * i // n + r.randint(0, 40))


@reg
def n1():
    r = rng("n1"); n = 200
    users = ["alice", "bob", "carol", "dave", "erin"]
    lines, cnt = [], 0
    for i in range(n):
        u = r.choice(users); ev = r.choice(["LOGIN_OK"] * 7 + ["LOGIN_FAIL"] * 2 + ["LOGOUT"] * 3)
        if ev == "LOGIN_FAIL" and u == "carol":
            cnt += 1
        lines.append("%s %s %s" % (hhmm(r, i, n), ev, u))
    lines[50] = "08:00:00 LOGIN_FAIL Carol"
    lines[51] = "08:00:01 login_fail carol"
    cnt = sum(1 for l in lines if l.split()[1] == "LOGIN_FAIL" and l.split()[2] == "carol")
    cnt_ci = sum(1 for l in lines if l.split()[1].lower() == "login_fail" and l.split()[2].lower() == "carol")
    assert cnt_ci > cnt
    f = {"auth.log": "\n".join(lines) + "\n"}
    make("log-33762", sub="count", task_type="count_events", desc="Failed logins of one user, where a few lines spell event and name in other cases",
         files=f, turns=[T("auth.log 里 carol 一共登录失败了多少次？（用户名和事件名偶尔大小写不一致，都算）", [str(cnt_ci)], token=True, req=["bash"]),
                         T("那 bob 呢？", [str(sum(1 for l in lines if l.split()[1].lower() == "login_fail" and l.split()[2].lower() == "bob"))], token=True)],
         truth="rows=[l.split() for l in files['auth.log'].splitlines()]\nf=lambda u: sum(1 for x in rows if x[1].lower()=='login_fail' and x[2].lower()==u)\nanswers=[str(f('carol')), str(f('bob'))]",
         ref=[("awk 'tolower($2)==\"login_fail\" && tolower($3)==\"carol\"' auth.log | wc -l", str(cnt_ci))],
         notes={"traps": "Two lines use Carol / login_fail; exact-case grep undercounts (%d vs %d)." % (cnt, cnt_ci), "steps": "awk tolower.", "unique": "carol %d" % cnt_ci},
         traps=("TR-DECOY", "TR-DEFN"), axes=("OBS",), rc=5)


@reg
def n2():
    r = rng("n2"); n = 220
    ips = ["10.1.4.%d" % i for i in range(11, 19)]
    lines, rows = [], []
    for i in range(n):
        ip = r.choice(ips); st = r.choice([200] * 10 + [403] * 2 + [404])
        rows.append((ip, st)); lines.append("%s %s GET /r/%d %d" % (hhmm(r, i, n), ip, r.randint(1, 60), st))
    d = len({ip for ip, st in rows if st == 403}); c = sum(1 for ip, st in rows if st == 403)
    assert d != c
    f = {"edge.log": "\n".join(lines) + "\n"}
    make("log-33763", sub="count", task_type="count_events", desc="Distinct client IPs among 403 responses, then total 403 lines",
         files=f, turns=[T("How many distinct client IPs received a 403 in edge.log?", [str(d)], token=True, req=["bash"]),
                         T("And how many 403 responses in total?", [str(c)], token=True)],
         truth="rows=[l.split() for l in files['edge.log'].splitlines()]\nanswers=[str(len({x[1] for x in rows if x[4]=='403'})), str(sum(1 for x in rows if x[4]=='403'))]",
         ref=[("awk '$5==403{print $2}' edge.log | sort -u | wc -l", str(d))],
         notes={"traps": "Distinct vs total.", "steps": "awk | sort -u | wc -l.", "unique": "distinct %d, total %d" % (d, c)},
         traps=("TR-DEFN",), axes=("OBS",), rc=5)


@reg
def n3():
    r = rng("n3"); n = 210
    msgs = ["upload ok", "upload ok", "upload ok", "upload timeout", "UPLOAD TIMEOUT", "upload timed out", "upload retry", "download ok"]
    lines = ["%s %s" % (hhmm(r, i, n), r.choice(msgs)) for i in range(n)]
    c = sum(1 for l in lines if "timeout" in l.lower() or "timed out" in l.lower())
    c1 = sum(1 for l in lines if l.endswith("upload timeout"))
    assert c > c1 + 5
    f = {"uploads.log": "\n".join(lines) + "\n"}
    make("log-33764", sub="count", task_type="count_events", desc="Timeouts written in three spellings",
         files=f, turns=[T("uploads.log 里上传超时一共出现了多少次？（超时有几种写法：timeout、TIMEOUT、timed out，都算）", [str(c)], token=True, req=["bash"])],
         truth="answers=[str(sum(1 for l in files['uploads.log'].splitlines() if 'timeout' in l.lower() or 'timed out' in l.lower()))]",
         ref=[("grep -ciE 'timeout|timed out' uploads.log", str(c))],
         notes={"traps": "Plain grep timeout gets %d." % c1, "steps": "grep -ciE.", "unique": "%d" % c},
         traps=("TR-DECOY", "TR-DEFN"), axes=("OBS",), rc=4)


@reg
def n4():
    r = rng("n4"); n = 180
    msgs = ["heartbeat ok"] * 9 + ["service starting up", "service started", "config reloaded"]
    lines = []
    for i in range(n):
        lines.append("%s %s" % (hhmm(r, i, n, 0, 86000), r.choice(msgs)))
    st = [l for l in lines if l.endswith("service started")]
    assert 3 <= len(st) <= 14, len(st)
    last = st[-1].split()[0]
    f = {"daemon.log": "\n".join(lines) + "\n"}
    make("log-33765", sub="count", task_type="count_events", desc="Restarts counted by 'service started', with 'service starting up' as a decoy",
         files=f, turns=[T("How many times did the service come up in daemon.log? Count only lines that say 'service started'.", [str(len(st))], token=True, req=["bash"]),
                         T("At what time was the last of those?", [last], token=True)],
         truth="ls=[l for l in files['daemon.log'].splitlines() if l.endswith('service started')]\nanswers=[str(len(ls)), ls[-1].split()[0]]",
         ref=[("grep -c 'service started' daemon.log", str(len(st)))],
         notes={"traps": "'service starting up' resembles it.", "steps": "grep -c 'service started'; tail last.", "unique": "%d, last %s" % (len(st), last)},
         traps=("TR-DECOY",), axes=("OBS",), rc=4)


@reg
def n5():
    r = rng("n5"); n = 230
    codes = ["E101", "E204", "E204", "E317", "E317", "E317", "E450", "E101", "E204"]
    lines = ["%s ERR code=%s unit=%d" % (hhmm(r, i, n), r.choice(codes), r.randint(1, 9)) for i in range(n)]
    import collections
    c = collections.Counter(l.split()[2][5:] for l in lines)
    (top, k), (_, k2) = c.most_common(2)
    assert k > k2
    f = {"errors.log": "\n".join(lines) + "\n"}
    make("log-33766", sub="count", task_type="count_events", desc="Most frequent error code and its count",
         files=f, turns=[T("errors.log 里出现最多的错误码是哪个？出现了多少次？", [top, str(k)], token=True, req=["bash"])],
         truth="import collections\nc=collections.Counter(l.split()[2].split('=')[1] for l in files['errors.log'].splitlines())\nanswers=[c.most_common(1)[0][0]]",
         ref=[("awk '{print $3}' errors.log | sort | uniq -c | sort -rn | head -2", str(k))],
         notes={"traps": "Several codes close in frequency.", "steps": "awk | sort | uniq -c | sort -rn.", "unique": "%s %d" % (top, k)},
         traps=("TR-DECOY",), axes=("OBS",), rc=4)


@reg
def n6():
    r = rng("n6"); n = 240
    paths = ["/pay", "/pay/status", "/cart", "/search", "/pay"]
    lines = []
    for i in range(n):
        lines.append("%s POST %s %d" % (hhmm(r, i, n), r.choice(paths), r.choice([200] * 8 + [500, 502, 504, 404])))
    c = sum(1 for l in lines if l.split()[2] == "/pay" and int(l.split()[3]) >= 500)
    call = sum(1 for l in lines if "/pay" in l and int(l.split()[3]) >= 500)
    assert c != call and c >= 3
    f = {"gateway.log": "\n".join(lines) + "\n"}
    make("log-33767", sub="count", task_type="count_events", desc="5xx on exactly /pay, not /pay/status",
         files=f, turns=[T("gateway.log 里请求路径恰好是 /pay（不含 /pay/status）的 5xx 响应有多少条？", [str(c)], token=True, req=["bash"])],
         truth="answers=[str(sum(1 for l in files['gateway.log'].splitlines() if l.split()[2]=='/pay' and int(l.split()[3])>=500))]",
         ref=[("awk '$3==\"/pay\" && $4>=500' gateway.log | wc -l", str(c))],
         notes={"traps": "grep /pay also matches /pay/status (%d)." % call, "steps": "awk exact field.", "unique": "%d" % c},
         traps=("TR-DECOY", "TR-NEARNAME"), axes=("OBS", "ERR"), rc=4)


@reg
def n7():
    r = rng("n7"); n = 200
    us = ["ann", "ben", "cy", "dee", "eli", "fay"]
    lines = ["ts,user,action"]
    rows = []
    for i in range(n):
        u = r.choice(us); a = r.choice(["view", "view", "view", "download", "upload", "share"])
        rows.append((u, a)); lines.append("%s,%s,%s" % (hhmm(r, i, n), u, a))
    d = sum(1 for u, a in rows if u == "ben" and a == "download")
    du = len({u for u, a in rows if a == "download"})
    f = {"activity.csv": "\n".join(lines) + "\n"}
    make("log-33768", sub="count", task_type="count_events", desc="Downloads by one user from a CSV event log, then distinct downloaders",
         files=f, turns=[T("activity.csv 记录了用户操作。ben 下载（download）了多少次？", [str(d)], token=True, req=["bash"]),
                         T("一共有几个不同的用户下载过东西？", [str(du)], token=True)],
         truth="import csv,io\nrows=list(csv.DictReader(io.StringIO(files['activity.csv'])))\nanswers=[str(sum(1 for x in rows if x['user']=='ben' and x['action']=='download')), str(len({x['user'] for x in rows if x['action']=='download'}))]",
         ref=[("awk -F, '$2==\"ben\" && $3==\"download\"' activity.csv | wc -l", str(d)), ("awk -F, '$3==\"download\"{print $2}' activity.csv | sort -u | wc -l", str(du))],
         notes={"traps": "Header row; distinct count.", "steps": "awk -F, ... sort -u.", "unique": "ben %d, distinct %d" % (d, du)},
         traps=("TR-DEFN",), axes=("OBS",), rc=5)


@reg
def n8():
    r = rng("n8"); n = 215
    kinds = ["heartbeat"] * 9 + ["sync done", "disk warn", "reconnect"]
    lines = ["%s node7 %s" % (hhmm(r, i, n), r.choice(kinds)) for i in range(n)]
    nh = sum(1 for l in lines if not l.endswith("heartbeat"))
    rc = sum(1 for l in lines if l.endswith("reconnect"))
    f = {"node.log": "\n".join(lines) + "\n"}
    make("log-33769", sub="count", task_type="count_events", desc="Count lines that are not heartbeats, then reconnects",
         files=f, turns=[T("In node.log, how many lines are NOT heartbeat lines?", [str(nh)], token=True, req=["bash"]),
                         T("Of those, how many are reconnects?", [str(rc)], token=True)],
         truth="ls=files['node.log'].splitlines()\nanswers=[str(sum(1 for l in ls if not l.endswith('heartbeat'))), str(sum(1 for l in ls if l.endswith('reconnect')))]",
         ref=[("grep -vc heartbeat node.log", str(nh)), ("grep -c reconnect node.log", str(rc))],
         notes={"traps": "Inverse match.", "steps": "grep -vc.", "unique": "non-heartbeat %d, reconnect %d" % (nh, rc)},
         traps=("TR-DEFN",), axes=("OBS",), rc=4)


@reg
def n9():
    r = rng("n9"); n = 205
    lines = []
    durs = []
    for i in range(n):
        dms = r.choice([r.randint(20, 300)] * 4 + [r.randint(300, 900)])
        durs.append(dms)
        lines.append("%s query %d dur=%dms" % (hhmm(r, i, n), 4000 + i, dms))
    slow = sum(1 for x in durs if x > 500)
    mx = max(durs)
    assert durs.count(mx) == 1 and slow >= 5
    f = {"db.log": "\n".join(lines) + "\n"}
    make("log-33770", sub="count", task_type="count_events", desc="Queries slower than 500ms in a numeric field, then the slowest one",
         files=f, turns=[T("db.log 里耗时超过 500ms（严格大于）的查询有多少条？", [str(slow)], token=True, req=["bash"]),
                         T("最慢的那条是哪个查询编号，耗时多少？", [str(4000 + durs.index(mx)), str(mx)], token=True)],
         truth="import re\nd=[int(re.search(r'dur=(\\d+)ms', l).group(1)) for l in files['db.log'].splitlines()]\nanswers=[str(sum(1 for x in d if x>500)), str(4000+d.index(max(d)))]",
         ref=[("sed 's/.*dur=//; s/ms//' db.log | awk '$1>500' | wc -l", str(slow))],
         notes={"traps": "Number sits in key=valuems form; string sort would be wrong.", "steps": "sed/awk numeric compare.", "unique": "%d slow; max %d" % (slow, mx)},
         traps=("TR-DEFN",), axes=("OBS",), rc=5)
