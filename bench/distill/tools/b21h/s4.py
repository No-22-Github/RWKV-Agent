"""b21h sub 4 (user words differ from data words): 32331-32338."""
import datetime

from common import make, csv, rng, L, NAMES, NOCALC, filler_keys

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c31():
    r = rng(31)
    st = ["success"] * 150 + ["error"] * 40 + ["timeout"] * 30 + ["aborted"] * 25
    r.shuffle(st)
    rows = [("job-%03d" % (i + 1), r.choice(["etl", "etl", "report", "sync"]), s) for i, s in enumerate(st)]
    f = {"jobs.csv": csv(["job", "kind", "status"], rows)}
    n = len(st) - st.count("success")
    make("tab-32331", sub="term", task_type="filter_count", desc="Count failed jobs where the data uses error/timeout/aborted and never the word failed",
         files=f, turns=[("jobs.csv 里失败的任务一共有多少个？", [str(n)], ["共 0", "为 0", "有 0 个", "没有失败"]),
                         ("其中 etl 类的失败了几个？", [str(sum(1 for x, s in zip(rows, st) if s != "success" and x[1] == "etl"))], None)],
         truth="ans = sum(1 for l in files['jobs.csv'].splitlines()[1:] if l.split(',')[2] != 'success')",
         ref=[("awk -F, 'NR>1&&$3!=\"success\"{n++}END{print n}' jobs.csv", str(n)),
              ("awk -F, 'NR>1&&$3!=\"success\"&&$2==\"etl\"{n++}END{print n}' jobs.csv", str(sum(1 for x, s in zip(rows, st) if s != "success" and x[1] == "etl")))],
         lazy=[("grep -c failed jobs.csv", "zero")],
         notes={"traps": "There is no status literally called failed.", "steps": "cut -d, -f3 | sort | uniq -c; count the non-success ones.", "unique": "error+timeout+aborted."})


@reg
def c32():
    r = rng(32)
    codes = ["BJ", "SH", "GZ", "CD"]
    cs = ["BJ"] * 85 + ["SH"] * 60 + ["GZ"] * 45 + ["CD"] * 30
    r.shuffle(cs)
    rows = [("N%04d" % (400 + i), c, r.randint(1, 5)) for i, c in enumerate(cs)]
    f = {"orders.csv": csv(["no", "city_code", "amount"], rows), "city_codes.csv": csv(["code", "name"], [("BJ", "北京"), ("SH", "上海"), ("GZ", "广州"), ("CD", "成都")])}
    n = cs.count("BJ")
    t = sum(x[2] for x in rows if x[1] == "BJ")
    make("tab-32332", sub="term", task_type="join", desc="Count orders of a city named in Chinese while the data uses city codes defined in a lookup file",
         files=f, turns=[("北京的订单有多少笔？", [str(n)], ["共 0", "为 0", "有 0 笔", "没有北京"]), ("这些订单的金额一共多少？", [str(t)], None)],
         truth="ans = sum(1 for l in files['orders.csv'].splitlines()[1:] if l.split(',')[1] == 'BJ')",
         ref=[("code=$(grep 北京 city_codes.csv | cut -d, -f1); awk -F, -v c=$code 'NR>1&&$2==c{n++}END{print n}' orders.csv", str(n)),
              ("awk -F, '$2==\"BJ\"{s+=$3}END{print s}' orders.csv", str(t))],
         lazy=[("grep -c 北京 orders.csv", "zero")],
         notes={"traps": "Orders use BJ; the mapping is in city_codes.csv.", "steps": "head both files; grep the code; count.", "unique": "17 BJ rows."})


@reg
def c33():
    r = rng(33)
    pl = ["FREE-1"] * 90 + ["PRO-2"] * 70 + ["ENT-A"] * 40 + ["ENT-B"] * 35
    r.shuffle(pl)
    rows = [("acct-%03d" % (i + 1), p, r.randint(1, 40)) for i, p in enumerate(pl)]
    f = {"accounts.csv": csv(["account", "plan", "seats"], rows), "plans.txt": L("FREE-1 = free tier", "PRO-2 = professional", "ENT-A = enterprise (standard)", "ENT-B = enterprise (dedicated)")}
    n = sum(1 for p in pl if p.startswith("ENT"))
    make("tab-32333", sub="term", task_type="join", desc="Count enterprise accounts when plans are coded and described in a text file",
         files=f, turns=[("How many enterprise accounts are in accounts.csv?", [str(n)], ["is 0", "no enterprise", "none are enterprise", " 0 enterprise"])],
         truth="ans = sum(1 for l in files['accounts.csv'].splitlines()[1:] if l.split(',')[1].startswith('ENT'))",
         ref=[("awk -F, 'NR>1&&$2 ~ /^ENT/{n++}END{print n}' accounts.csv", str(n))],
         lazy=[("grep -ci enterprise accounts.csv", "zero")],
         notes={"traps": "Plan codes ENT-A/ENT-B; plans.txt explains.", "steps": "cat plans.txt; count both ENT codes.", "unique": "15 accounts."})


@reg
def c34():
    r = rng(34)
    msgs = ["upstream ETIMEDOUT 10.1.0.4", "rpc deadline exceeded", "cache hit", "request served", "ETIMEDOUT while reading", "pool refill done"]
    ws = [1, 1, 1, 1, 1, 1]
    lines = []
    cnt = 0
    for i in range(300):
        m = r.choice(msgs)
        lines.append("2026-09-15 %02d:%02d:%02d %s" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), m))
        if "ETIMEDOUT" in m or "deadline exceeded" in m:
            cnt += 1
    f = {"gateway.log": "\n".join(lines) + "\n"}
    make("log-32334", sub="term", task_type="count_events", desc="Count timeouts when the log says ETIMEDOUT or deadline exceeded",
         files=f, turns=[("gateway.log 里超时的请求有多少条？", [str(cnt)], ["共 0", "为 0", "有 0 条", "没有超时"]),
                         ("其中带 ETIMEDOUT 的有几条？", [str(sum(1 for l in lines if "ETIMEDOUT" in l))], None)],
         truth="ans = sum(1 for l in files['gateway.log'].splitlines() if 'ETIMEDOUT' in l or 'deadline exceeded' in l)",
         ref=[("grep -cE 'ETIMEDOUT|deadline exceeded' gateway.log", str(cnt)), ("grep -c ETIMEDOUT gateway.log", str(sum(1 for l in lines if "ETIMEDOUT" in l)))],
         lazy=[("grep -c 超时 gateway.log", "zero"), ("grep -ci timeout gateway.log", "zero")],
         notes={"traps": "Timeouts are logged as ETIMEDOUT or deadline exceeded.", "steps": "sample the messages; grep -E.", "unique": "both forms counted."})


@reg
def c35():
    r = rng(35)
    ev = ["panic: nil map write", "OOM-killed pid 4121", "SIGSEGV in worker", "started", "health ok", "drain complete", "SIGSEGV in worker", "config reloaded"]
    lines = ["2026-09-1%d %02d:%02d host-%d %s" % (r.randint(2, 5), r.randint(0, 23), r.randint(0, 59), r.randint(1, 3), r.choice(ev)) for _ in range(300)]
    n = sum(1 for l in lines if any(k in l for k in ("panic:", "OOM-killed", "SIGSEGV")))
    f = {"hosts.log": "\n".join(lines) + "\n"}
    make("log-32335", sub="term", task_type="count_events", desc="Count crashes when the log never uses the word crash",
         files=f, turns=[("How many times did our services crash according to hosts.log?", [str(n)], ["is 0", "no crash", "never crashed", "zero crash", " 0 crash"])],
         truth="ans = sum(1 for l in files['hosts.log'].splitlines() if any(k in l for k in ('panic:', 'OOM-killed', 'SIGSEGV')))",
         ref=[("grep -cE 'panic:|OOM-killed|SIGSEGV' hosts.log", str(n))],
         lazy=[("grep -ci crash hosts.log", "zero")],
         notes={"traps": "Crashes appear as panic, OOM-killed and SIGSEGV.", "steps": "view distinct messages; count the three kinds.", "unique": "panic+OOM+SIGSEGV."}, policy=NOCALC)


@reg
def c36():
    r = rng(36)
    lv = ["L2"] * 100 + ["L4"] * 50 + ["L5"] * 40 + ["L6"] * 25
    r.shuffle(lv)
    rows = [("U%03d" % (i + 1), r.choice(NAMES), l) for i, l in enumerate(lv)]
    f = {"members.csv": csv(["uid", "name", "level"], rows), "README.md": L("level: L1..L6. VIP means level 5 and above (L5, L6).")}
    n = sum(1 for l in lv if l in ("L5", "L6"))
    make("tab-32336", sub="term", task_type="filter_count", desc="Count VIP members where VIP is defined as level L5 and above in the readme",
         files=f, turns=[("members.csv 里有多少 VIP 会员？", [str(n)], ["共 0", "为 0", "有 0 位", "没有 VIP", "没有 vip"])],
         truth="ans = sum(1 for l in files['members.csv'].splitlines()[1:] if l.split(',')[2] in ('L5','L6'))",
         ref=[("grep -cE ',L[56]$' members.csv", str(n))], lazy=[("grep -ci vip members.csv", "zero")],
         notes={"traps": "VIP is not a column value; README defines it.", "steps": "cat README.md; count L5/L6.", "unique": "13 rows."})


@reg
def c37():
    r = rng(37)
    fk = ["%s = %d" % (k, r.randint(1, 900)) for k in filler_keys(r, 80, avoid=("ssl", "tls", "pool"))]
    f = {"db.conf": L("host = pg-2.internal", "port = 5432", *fk[:30], "ssl_mode = require", "ssl_ca = /etc/pki/ca.pem", *fk[30:60], "pool = 18", *fk[60:])}
    make("cfg-32337", sub="term", task_type="read_effective", desc="Say whether TLS is enabled when the config only has ssl_mode",
         files=f, turns=[("db.conf 里数据库连接有没有启用 TLS 加密？", ["require"], None),
                         ("连接池大小是多少？", ["18"], None)],
         truth="ans = 'require'",
         ref=[("grep -i ssl db.conf", "require"), ("grep pool db.conf", "18")],
         lazy=[("grep -i tls db.conf", "empty")],
         notes={"traps": "The word TLS never appears; ssl_mode = require is the setting.", "steps": "grep -i ssl.", "unique": "ssl_mode require."}, policy=NOCALC)


@reg
def c38():
    r = rng(38)
    ds = [datetime.date(2026, 8, 1) + datetime.timedelta(days=r.randint(0, 30)) for _ in range(250)]
    rows = [("W-%04d" % (900 + i), d.isoformat(), r.randint(15, 80)) for i, d in enumerate(ds)]
    f = {"orders_aug.csv": csv(["order", "date", "amount"], rows)}
    n = sum(1 for d in ds if d.isoweekday() >= 6)
    make("tab-32338", sub="term", task_type="filter_count", desc="Count weekend orders from dates only",
         files=f, turns=[("How many weekend orders are there in orders_aug.csv?", [str(n)], ["is 0", "no weekend", "zero weekend", " 0 weekend", "no column"])],
         truth="import datetime\nans = sum(1 for l in files['orders_aug.csv'].splitlines()[1:] if datetime.date.fromisoformat(l.split(',')[1]).isoweekday() >= 6)",
         ref=[("tail -n +2 orders_aug.csv | cut -d, -f2 | while read d; do date -d $d +%u; done | grep -cE '^[67]$'", str(n))],
         lazy=[("grep -ci weekend orders_aug.csv", "zero")],
         notes={"traps": "No weekend column; derive from dates.", "steps": "loop date -d over the dates.", "unique": "Saturdays/Sundays."})
