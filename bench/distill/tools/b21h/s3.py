"""b21h sub 3 (wrong file picked): 32323-32330."""
from common import make, csv, rng, L, NAMES, NOCALC, filler_keys

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c23():
    r = rng(23)
    amts = [r.randint(1, 5) for _ in range(180)]
    rows = [("A%04d" % (600 + i), r.choice(NAMES), a) for i, a in enumerate(amts)]
    f = {"orders.csv": "order_id,customer,amount\n", "orders_2026-09.csv": csv(["order_id", "customer", "amount"], rows),
         "README.md": L("# data folder", "orders.csv is only the empty template kept for the importer.", "Live orders are exported monthly: orders_2026-09.csv for this month.")}
    t = sum(amts)
    make("tab-32323", sub="file", task_type="aggregate", desc="Total orders where the obvious file only has a header and the real month file is named in the readme",
         files=f, turns=[("订单一共有多少笔，总金额是多少？", [str(len(rows)), str(t)], ["共 0", "没有订单", "为 0", "0 笔", "还没有订单"])],
         truth="ans = len(files['orders_2026-09.csv'].splitlines()) - 1",
         ref=[("awk -F, 'NR>1{n++;s+=$3}END{print n, s}' orders_2026-09.csv", "%d %d" % (len(rows), t))],
         lazy=[("awk 'END{print NR-1}' orders.csv", "zero")],
         notes={"traps": "orders.csv only has the header; README names the real file.", "steps": "ls; cat README.md; use orders_2026-09.csv.", "unique": "180 rows."})


@reg
def c24():
    r = rng(24)
    lv = ["INFO"] * 240 + ["ERROR"] * 84 + ["WARN"] * 42
    r.shuffle(lv)
    lines = ["2026-09-14 %02d:%02d:%02d %s checkout %s" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), l, r.choice(["order saved", "stock low", "card declined"])) for l in lv]
    f = {"app.log": "", "app.log.1": "\n".join(lines) + "\n"}
    n = lv.count("ERROR")
    make("log-32324", sub="file", task_type="count_events", desc="Count errors where app.log was just rotated and is empty",
         files=f, turns=[("How many ERROR lines did the app log yesterday? The log is app.log in this folder.", [str(n)], ["is 0", " 0 ERROR", "no errors", "no ERROR", "zero errors"])],
         truth="ans = sum(1 for l in files['app.log.1'].splitlines() if ' ERROR ' in l)",
         ref=[("grep -c ' ERROR ' app.log.1", str(n))], lazy=[("grep -c ERROR app.log", "zero")],
         notes={"traps": "app.log is empty after rotation; the data are in app.log.1.", "steps": "ls -l; use app.log.1.", "unique": "ERROR lines in app.log.1."}, policy=NOCALC)


@reg
def c25():
    r = rng(25)
    rows = [("T%03d" % (i + 1), r.choice(["华东", "华北", "华南"]), r.randint(1, 4)) for i in range(220)]
    f = {"sales_2026Q3.csv": csv(["tid", "region", "units"], rows)}
    t = sum(x[2] for x in rows)
    make("tab-32325", sub="file", task_type="aggregate", desc="Sum units from a file that the user calls by a wrong name",
         files=f, turns=[("帮我算一下 sales.csv 里 units 的总和。", [str(t)], ["总和为 0", "总和是 0", "共 0"])],
         truth="ans = sum(int(l.split(',')[2]) for l in files['sales_2026Q3.csv'].splitlines()[1:])",
         ref=[("ls; awk -F, 'NR>1{s+=$3}END{print s}' sales_2026Q3.csv", str(t))],
         lazy=[("awk -F, 'NR>1{s+=$3}END{print s}' sales.csv", "err")],
         notes={"traps": "sales.csv does not exist; the only candidate is sales_2026Q3.csv.", "steps": "ls, then sum.", "unique": "One csv exists."})


@reg
def c26():
    r = rng(26)
    lv = ["INFO"] * 228 + ["ERROR"] * 114 + ["WARN"] * 36
    r.shuffle(lv)
    lines = ["%02d:%02d:%02d %s %s" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), l, r.choice(["batch ok", "disk 91%", "peer lost"])) for l in lv]
    f = {"logs/app-2026-09-15.log": "\n".join(lines) + "\n", "logs/app-2026-09-16.log": "00:00:01 INFO rotated\n"}
    n = lv.count("ERROR")
    make("log-32326", sub="file", task_type="count_events", desc="Count errors of yesterday where the user guesses a plain app.log name",
         files=f, turns=[("昨天的日志里有多少条 ERROR？日志在 logs 目录下。", [str(n)], ["共 0", "为 0", "有 0 条", "没有 ERROR", "没有找到日志"])],
         truth="ans = sum(1 for l in files['logs/app-2026-09-15.log'].splitlines() if ' ERROR ' in l)",
         ref=[("grep -c ' ERROR ' logs/app-2026-09-15.log", str(n))], lazy=[("grep -c ERROR logs/app.log", "err")],
         notes={"traps": "Daily files; today is 2026-09-16 so yesterday is the 15th.", "steps": "ls logs; grep the 15th file.", "unique": "ERROR lines on the 15th."})


@reg
def c27():
    r = rng(27)
    fl = lambda n: ["  %s: %d" % (k, r.randint(1, 900)) for k in filler_keys(r, n, avoid=("port",))]
    f = {"config.yaml": L("# defaults moved, see conf.d/ (loaded in name order)", "app: shop", "defaults:", *fl(85)),
         "conf.d/10-db.yaml": L("db:", "  host: pg-main.internal", "  port: 6432", "  pool: 20", *fl(25)),
         "conf.d/20-cache.yaml": L("cache:", "  host: redis-1.internal", "  port: 7379", *fl(25)),
         "conf.d/30-queue.yaml": L("queue:", "  broker: mq-1.internal", *fl(30))}
    make("cfg-32327", sub="file", task_type="read_effective", desc="Find the database port that the top-level config only points to",
         files=f, turns=[("这个项目里数据库的端口配的是多少？", ["6432"], None),
                         ("缓存那边的呢？", ["7379"], None)],
         truth="ans = '6432'",
         ref=[("grep -rn port conf.d", "6432"), ("grep -rn port conf.d", "7379")], lazy=[("grep -n port config.yaml", "empty")],
         notes={"traps": "config.yaml has no port; the comment points to conf.d.", "steps": "cat config.yaml; ls conf.d; grep.", "unique": "db 6432, cache 7379."}, policy=NOCALC)


@reg
def c28():
    r = rng(28)
    amts = [r.randint(1, 6) for _ in range(150)]
    rows = [("W%02d" % (i + 1), r.choice(["north", "south", "east"]), a) for i, a in enumerate(amts)]
    f = {"report.csv": "week,region,units\n", "exports/2026-09/report_wk2.csv": csv(["week", "region", "units"], rows),
         "exports/NOTE.txt": "report.csv in the top folder is cleared after every upload. Look in exports/<month>/ for the data.\n"}
    t = sum(amts)
    make("tab-32328", sub="file", task_type="aggregate", desc="Sum units where the top-level report is cleared and the data live in an exports folder",
         files=f, turns=[("What is the total of units in the report?", [str(t)], ["is 0", "total of 0", "no data", "empty report", "nothing in the report"])],
         truth="ans = sum(int(l.split(',')[2]) for l in files['exports/2026-09/report_wk2.csv'].splitlines()[1:])",
         ref=[("awk -F, 'FNR>1{s+=$3}END{print s}' exports/2026-09/report_wk2.csv", str(t))],
         lazy=[("awk -F, 'NR>1{s+=$3}END{print s+0}' report.csv", "zero")],
         notes={"traps": "report.csv only holds the header.", "steps": "find / ls -R; read NOTE.txt; sum the exports file.", "unique": "150 rows."})


@reg
def c29():
    r = rng(29)
    lines = ["2026-09-15 %02d:%02d %s %s" % (r.randint(0, 23), r.randint(0, 59), r.choice(["E1042", "E2001", "E1042", "E3310"]), r.choice(["timeout", "refused", "bad token"])) for _ in range(300)]
    n = sum(1 for l in lines if " E1042 " in l)
    f = {"error.log": "", "app.err": "\n".join(lines) + "\n", "README.txt": "Since the 3.2 upgrade errors go to app.err; error.log is kept for old scripts.\n"}
    make("log-32329", sub="file", task_type="count_events", desc="Count an error code in the new error file when error.log is empty",
         files=f, turns=[("错误日志里 E1042 出现了多少次？", [str(n)], ["共 0", "为 0", "有 0 次", "没有 E1042", "没有出现"])],
         truth="ans = sum(1 for l in files['app.err'].splitlines() if ' E1042 ' in l)",
         ref=[("grep -c ' E1042 ' app.err", str(n))], lazy=[("grep -c E1042 error.log", "zero")],
         notes={"traps": "error.log is empty; app.err has the data.", "steps": "ls -l, README.", "unique": "count of E1042 in app.err."})


@reg
def c30():
    r = rng(30)
    fl = lambda n: ["%s = %d" % (k, r.randint(1, 900)) for k in filler_keys(r, n, avoid=("port", "pool"))]
    f = {"settings.ini": L("[db]", "host = pg-1.internal", "; port comes from local.ini, do not set it here", "pool = 12", *fl(12), "", "[web]", *fl(30), "", "[include]", "file = local.ini", "", "[misc]", *fl(45)),
         "local.ini": L("[db]", "port = 6432", "pool = 30", *fl(12), "", "[web]", *fl(14))}
    make("cfg-32330", sub="file", task_type="read_effective", desc="Find the effective db port and pool where settings.ini only includes another file",
         files=f, turns=[("What is the database port, and what pool size is actually used?", ["6432", "30"], ["no port", "not set", "not configured", "port is missing"])],
         truth="ans = '6432'",
         ref=[("cat settings.ini local.ini", "6432"), ("cat settings.ini local.ini", "pool = 30")],
         lazy=[("grep -E '^port' settings.ini", "empty")],
         notes={"traps": "port is only in the included file; pool is overridden there.", "steps": "cat both files.", "unique": "port 6432, pool 30."})
