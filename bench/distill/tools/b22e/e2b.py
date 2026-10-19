"""E2 big tables, cases tab-34434..34440."""
from common import *
from lg import pick
from e2a import pre, csv_text, money, wpick, day, D

B = []


def reg(f):
    B.append(f)
    return f


@reg
def t09():
    r = rng("t09"); n = 2700
    rows = [["order_id", "created", "customer", "total"]]
    for i in range(n):
        rows.append(["SO-%06d" % (520000 + i), day(r, 2026, 3, 8), "C%04d" % r.randint(1, 800), money(r, 10, 2500)])
    dups = r.sample(range(60, n - 1), 37)
    out = []
    for i, row in enumerate(rows):
        out.append(row)
        if i - 1 in dups and i > 0:
            out.append(list(row))
    f = {"export_orders.csv": csv_text(out)}
    make("tab-34434", sub="E2", task_type="filter_count", desc="Order ids that were exported twice (duplicate rows) in a 2700-row export",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("Some rows in export_orders.csv were exported twice. How many order_id values appear more than once?", "i")],
         truth=pre("export_orders.csv") + "c = collections.Counter(x['order_id'] for x in rows)\nanswers = [len([k for k, v in c.items() if v > 1])]\n",
         ref=[("tail -n +2 export_orders.csv | cut -d, -f1 | sort | uniq -d | wc -l", lambda a: str(a[0]))],
         notes={"traps": "The number of extra rows and the number of repeated ids coincide only if nobody appears three times; counting lines is not the same as counting ids.", "steps": "cut -f1 | sort | uniq -d | wc -l.", "unique": "Recomputed from the fixture."})


@reg
def t10():
    r = rng("t10"); n = 3300
    mw = [("2026-0%d" % m, w) for m, w in zip(range(1, 10), [9, 10, 11, 12, 13, 12, 14, 19, 11])]
    rows = [["id", "month", "store", "sales"]]
    for i in range(n):
        rows.append(["S%05d" % (i + 1), wpick(r, mw), pick(r, ["A01", "A02", "B07", "C03"]), money(r, 100, 3900)])
    f = {"monthly_sales.csv": csv_text(rows)}
    make("tab-34435", sub="E2", task_type="aggregate", desc="Month with the highest total sales, then that total",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("monthly_sales.csv 里哪个月的销售额（sales）合计最高？"), T("那个月合计多少？保留两位小数。", "f")],
         truth=pre("monthly_sales.csv") + "t = collections.Counter()\nfor x in rows:\n    t[x['month']] += cents(x['sales'])\nm, v = t.most_common(1)[0]\nanswers = [[m], v / 100.0]\n",
         ref=[("awk -F, 'NR>1{s[$2]+=$4} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' monthly_sales.csv | sort -k2 -nr | head -2", lambda a: a[0][0]),
              ("awk -F, 'NR>1{s[$2]+=$4} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' monthly_sales.csv | sort -k2 -nr | head -1", lambda a: "%.2f" % a[1])],
         notes={"traps": "Row order is random across months, so the first screen shows a mix; August is largest only after summing.", "steps": "awk group sum by month | sort.", "unique": "2026-08 is clearly ahead."})


@reg
def t11():
    r = rng("t11"); n = 2500
    notes = ["", "", "", "含税, 快递到付", "加急, 周末送达", "赠品: 杯垫, 贴纸", "", "备注: 无, 勿电话"]
    rows = []
    for i in range(n):
        note = pick(r, notes)
        rows.append(["P%05d" % (i + 1), day(r, 2026, 5, 9), "客户%03d" % r.randint(1, 120), ('"%s"' % note) if note else "", money(r, 30, 2200)])
    text = "单号,日期,客户,备注,金额\n" + csv_text(rows)
    f = {"客户订单.csv": text}
    make("tab-34436", sub="E2", task_type="aggregate", desc="Sum for one customer in a table whose note column has quoted commas",
         files=f, shape="csv", rc=5, deep=False,
         turns=[T("客户订单.csv 里“客户077”的金额一共是多少？保留两位小数。", "f")],
         truth="import csv, io\nrows = list(csv.reader(io.StringIO(files['客户订单.csv'])))[1:]\nanswers = [sum(round(float(x[4]) * 100) for x in rows if x[2] == '客户077') / 100.0]\n",
         ref=[("awk -F, 'NR>1 && $3==\"客户077\"{s+=$NF} END{printf \"%.2f\\n\", s}' 客户订单.csv", lambda a: "%.2f" % a[0])],
         notes={"traps": "The note column has quoted commas, so column positions shift for some rows; the amount is always the last field.", "steps": "head -5 to see quoting; awk -F, with $NF.", "unique": "Recomputed with python csv."})


@reg
def t12():
    r = rng("t12"); n = 3600
    rows = [["sensor", "ts", "temp_c", "humidity"]]
    for i in range(n):
        s = i * 24 * 3600 // n
        rows.append(["S-%02d" % r.randint(1, 18), "2026-08-14 %02d:%02d:%02d" % (s // 3600, s % 3600 // 60, s % 60), "%.1f" % (r.uniform(17, 38)), r.randint(30, 80)])
    rows[2650][2] = "58.7"
    f = {"readings.csv": csv_text(rows, ";")}
    make("tab-34437", sub="E2", task_type="rank", desc="Hottest reading in a semicolon separated sensor table: sensor and timestamp",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("readings.csv is semicolon separated. Which sensor reported the highest temp_c?"), T("At what timestamp (date and time) was that reading taken?")],
         truth=pre("readings.csv", ";") + "m = max(rows, key=lambda x: float(x['temp_c']))\nanswers = [[m['sensor']], [m['ts']]]\n",
         ref=[("awk -F';' 'NR>1{print $3, $1, $2}' readings.csv | sort -rn | head -2", lambda a: a[0][0]), ("awk -F';' 'NR>1{print $3, $1, $2}' readings.csv | sort -rn | head -1", lambda a: a[1][0])],
         notes={"traps": "Delimiter is a semicolon, so a comma-based cut finds one column; the maximum is at row 2652.", "steps": "head -3 shows ';'; awk -F';' | sort -rn.", "unique": "58.7 is far above the random range (17-38)."})


@reg
def t13():
    r = rng("t13"); n = 3000
    rows = [["txn_id", "date", "method", "state", "amount"]]
    for i in range(n):
        rows.append(["P-%06d" % (80000 + i), day(r, 2026, 8, 9), pick(r, ["card", "alipay", "wechat", "bank"]), wpick(r, [("success", 90), ("failed", 5), ("reversed", 2)]), money(r, 5, 900)])
    f = {"payments.csv": csv_text(rows)}
    make("tab-34438", sub="E2", task_type="filter_count", desc="Percentage of failed payments in a 3000-row table",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("payments.csv 里失败（failed）的支付占全部支付的百分之几？保留一位小数，只算 failed，不含 reversed。", "f", dp=1)],
         truth=pre("payments.csv") + "answers = [round(100.0 * len([x for x in rows if x['state'] == 'failed']) / len(rows), 1)]\n",
         ref=[("awk -F, 'NR>1{n++; if($4==\"failed\") f++} END{printf \"%.1f\\n\", 100*f/n}' payments.csv", lambda a: "%.1f" % a[0])],
         notes={"traps": "The denominator is the number of data rows (header excluded); reversed is not failed.", "steps": "awk counts failed and total, prints the ratio.", "unique": "Recomputed from the fixture."})


@reg
def t14():
    r = rng("t14"); n = 2300
    depts = [("eng", 1.35), ("ops", 0.95), ("sales", 1.05), ("hr", 0.9), ("legal", 1.2), ("design", 1.1)]
    rows = [["badge", "fullname", "unit", "monthly_pay"]]
    for i in range(n):
        d, k = pick(r, depts)
        rows.append(["E%05d" % (i + 1), "emp%d" % (i + 1), d, int(r.randint(5200, 9800) * k)])
    f = {"人事/部门薪资快照-2026h2.csv": csv_text(rows)}
    make("tab-34439", sub="E2", task_type="aggregate", desc="Department with the highest average salary, then the average",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("Which department has the highest average monthly_pay in 人事/部门薪资快照-2026h2.csv?"), T("And what is that average? Two decimals.", "f")],
         truth=pre("人事/部门薪资快照-2026h2.csv") + "s = collections.defaultdict(list)\nfor x in rows:\n    s[x['unit']].append(int(x['monthly_pay']))\na = {k: sum(v) / len(v) for k, v in s.items()}\nm = max(a, key=a.get)\nanswers = [[m], round(a[m], 2)]\n",
         ref=[("awk -F, 'NR>1{s[$3]+=$4;n[$3]++} END{for(k in s) printf \"%.2f %s\\n\", s[k]/n[k], k}' 人事/部门薪资快照-2026h2.csv | sort -rn | head -2", lambda a: a[0][0]),
              ("awk -F, 'NR>1{s[$3]+=$4;n[$3]++} END{for(k in s) printf \"%.2f %s\\n\", s[k]/n[k], k}' 人事/部门薪资快照-2026h2.csv | sort -rn | head -1", lambda a: "%.2f" % a[1])],
         notes={"traps": "Highest total is not the same as highest average when head counts differ.", "steps": "awk sum and count by dept, then divide and sort.", "unique": "eng leads by a wide margin."})


@reg
def t15():
    r = rng("t15"); n = 2100
    stores = [("徐汇店", 20), ("静安店", 24), ("浦东店", 27), ("闵行店", 18)]
    def mon(m, seed):
        g = rng(seed)
        rows = [["date", "store", "ticket", "amount"]]
        for i in range(n):
            rows.append(["2026-%02d-%02d" % (m, g.randint(1, 28)), wpick(g, stores), "T%06d" % (i + 1), money(g, 12, 460)])
        return csv_text(rows)
    f = {"门店流水/2026-07.csv": mon(7, "t15a"), "门店流水/2026-08.csv": mon(8, "t15b")}
    make("tab-34440", sub="E2", task_type="aggregate", desc="Store with the highest combined sales over two monthly files",
         files=f, shape="csv", rc=5, deep=False,
         turns=[T("门店流水目录下有 7 月和 8 月两个文件。两个月加起来，哪家门店的销售额（amount）最高？"), T("它两个月一共多少钱？保留两位小数。", "f")],
         truth="import csv, io, collections\nt = collections.Counter()\nfor p in sorted(files):\n    for x in csv.DictReader(io.StringIO(files[p])):\n        t[x['store']] += round(float(x['amount']) * 100)\nm, v = t.most_common(1)[0]\nanswers = [[m], v / 100.0]\n",
         ref=[("cat 门店流水/2026-07.csv 门店流水/2026-08.csv | awk -F, '$1 ~ /^2026/{s[$2]+=$4} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' | sort -k2 -nr | head -2", lambda a: a[0][0]),
              ("cat 门店流水/2026-07.csv 门店流水/2026-08.csv | awk -F, '$1 ~ /^2026/{s[$2]+=$4} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' | sort -k2 -nr | head -1", lambda a: "%.2f" % a[1])],
         notes={"traps": "Each month alone may rank differently; both files must be summed, header lines skipped.", "steps": "wc -l on both files, then cat + awk group sum.", "unique": "Margin checked in build."})
