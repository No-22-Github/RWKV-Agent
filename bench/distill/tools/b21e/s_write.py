"""Sub 5: compute then write a result CSV (8 cases, 32043-32050)."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c43():
    cols = [("订单号", ID("DD", 5, 70100)), ("区域", C(["华东", "华北", "华南", "西南", "东北"], [30, 22, 20, 15, 13])), ("下单日期", D(2026, 7, 9)), ("订单金额", M(30, 1500)), ("退款金额", F(lambda g, r: "0.00" if g.random() < 0.85 else "%.2f" % (float(r["订单金额"]) / 2)))]
    h, rows = gen_rows(32043, cols, 450)
    p, o = "报表/订单.csv", "报表/区域汇总.csv"
    calc = ('d = defaultdict(lambda: [0, 0.0])\nfor r in R:\n    d[r["区域"]][0] += 1\n    d[r["区域"]][1] += N(r["订单金额"])\n'
            'items = sorted(d.items(), key=lambda kv: -round(kv[1][1], 2))\nassert len({round(v[1], 2) for _, v in items}) == len(items)\n'
            'result = [["区域", "订单数", "订单金额合计"]] + [[k, str(v[0]), "%.2f" % v[1]] for k, v in items]')
    ref = ["head -3 " + p, "printf '区域,订单数,订单金额合计\\n' > %s" % o,
           "awk -F, 'NR>1 && NF{n[$%d]++; s[$%d]+=$%d} END{for(k in n) printf \"%%s,%%d,%%.2f\\n\", k, n[k], s[k]}' %s | sort -t, -k3,3 -rn >> %s" % (ci(h, "区域"), ci(h, "区域"), ci(h, "订单金额"), p, o), "cat " + o]
    make("tab-32043", sub="write", desc="Writes a per-region order count and amount summary CSV sorted by amount",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4, pol=None,
         notes_traps=["订单金额 vs 退款金额 adjacent; output must be sorted by total, descending"],
         turns=[T("把 报表/订单.csv 按区域汇总一下，结果写到 报表/区域汇总.csv：三列，表头依次是 区域,订单数,订单金额合计（用逗号分隔），每个区域一行，按订单金额合计从大到小排，金额保留两位小数。写好告诉我哪个区域最高。", calc, "files", ref, out=(o, ","))])


@reg
def c44():
    cols = [("txn_id", ID("X", 6, 1)), ("booked", D(2026, 4, 9)), ("category", C(["rent", "food", "travel", "tools", "misc"])), ("amount", M(5, 2800, 2, True)), ("account", C(["ops", "mkt", "dev"]))]
    h, rows = gen_rows(32044, cols, 400)
    p, o = "ledger/entries.csv", "ledger/monthly_totals.csv"
    calc = ('d = defaultdict(float)\nfor r in R:\n    d[r["booked"][:7]] += N(r["amount"])\n'
            'result = [["month", "total"]] + [[k, "%.2f" % d[k]] for k in sorted(d)]')
    ref = ["head -4 " + p, "printf 'month,total\\n' > %s" % o,
           "cat %s | %s | awk -F, 'NR>1 && NF{s[substr($%d,1,7)]+=$%d} END{for(k in s) printf \"%%s,%%.2f\\n\", k, s[k]}' | sort >> %s" % (p, SEDK, ci(h, "booked"), ci(h, "amount"), o), "cat " + o]
    make("tab-32044", sub="write", desc="Writes a monthly totals CSV from entries with quoted thousands amounts",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["amount quoted with thousands commas; months derived from a date"],
         turns=[T("From ledger/entries.csv build ledger/monthly_totals.csv: header month,total, one row per month (YYYY-MM) in ascending order, total is the sum of amount with 2 decimals and plain digits only (no grouping commas). Tell me which month is the biggest when you're done.", calc, "files", ref, out=(o, ","))])


@reg
def c45():
    cols = [("订单号", ID("DD", 5, 80100)), ("区域", C(["华东", "华北", "华南", "西南"])), ("品类", C(["数码", "家居", "服饰"])), ("金额", M(20, 900)), ("状态", C(["正常", "退款"], [86, 14]))]
    h, rows = gen_rows(32045, cols, 380)
    p, o1, o2 = "数据/订单.csv", "数据/退款明细.csv", "数据/退款按区域.csv"
    calc1 = 'result = [list(R[0].keys())] + [list(r.values()) for r in R if r["状态"] == "退款"]'
    calc2 = ('d = defaultdict(lambda: [0, 0.0])\nfor r in R:\n    if r["状态"] == "退款":\n        d[r["区域"]][0] += 1\n        d[r["区域"]][1] += N(r["金额"])\n'
             'items = sorted(d.items(), key=lambda kv: -round(kv[1][1], 2))\nassert len({round(v[1], 2) for _, v in items}) == len(items)\n'
             'result = [["区域", "退款单数", "退款金额"]] + [[k, str(v[0]), "%.2f" % v[1]] for k, v in items]')
    ref1 = ["head -3 " + p, "head -1 %s > %s" % (p, o1), "awk -F, 'NR>1 && NF && $%d==\"退款\"' %s >> %s" % (ci(h, "状态"), p, o1), "wc -l " + o1]
    ref2 = ["printf '区域,退款单数,退款金额\\n' > " + o2,
            "awk -F, 'NR>1 && NF && $%d==\"退款\"{n[$%d]++; s[$%d]+=$%d} END{for(k in n) printf \"%%s,%%d,%%.2f\\n\", k, n[k], s[k]}' %s | sort -t, -k3,3 -rn >> %s" % (ci(h, "状态"), ci(h, "区域"), ci(h, "区域"), ci(h, "金额"), p, o2), "cat " + o2]
    make("tab-32045", sub="write", desc="Extracts refunded orders to a new CSV, then writes a per-region refund summary",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=6,
         notes_traps=["first output keeps the original header and columns; second turn aggregates"],
         turns=[T("把 数据/订单.csv 里状态是“退款”的订单挑出来，原样（保留表头和全部列）存成 数据/退款明细.csv，原文件不要动。存好后告诉我一共挑出多少单。", calc1, "files", ref1, out=(o1, ",")),
                T("再按区域统计这些退款订单，写到 数据/退款按区域.csv：表头 区域,退款单数,退款金额，按退款金额从大到小排，金额两位小数。", calc2, "files", ref2, out=(o2, ","))])


@reg
def c46():
    cols = [("order", ID("S", 5, 100)), ("customer", C(["Alder", "Birch", "Cypress", "Dogwood", "Elm", "Fir", "Ginkgo", "Hazel", "Iris"], [9, 12, 5, 14, 8, 6, 11, 10, 7])), ("amount", M(20, 3500)), ("status", C(["paid", "void"], [92, 8]))]
    h, rows = gen_rows(32046, cols, 460)
    p, o = "sales/orders.csv", "sales/top3_customers.csv"
    calc = ('d = defaultdict(float)\nfor r in R:\n    if r["status"] == "paid":\n        d[r["customer"]] += N(r["amount"])\n'
            'items = sorted(d.items(), key=lambda kv: -round(kv[1], 2))\nassert round(items[2][1], 2) != round(items[3][1], 2)\n'
            'result = [["customer", "paid_total"]] + [[k, "%.2f" % v] for k, v in items[:3]]')
    ref = ["head -3 " + p, "printf 'customer,paid_total\\n' > " + o,
           "awk -F, 'NR>1 && NF && $%d==\"paid\"{s[$%d]+=$%d} END{for(k in s) printf \"%%s,%%.2f\\n\", k, s[k]}' %s | sort -t, -k2,2 -rn | head -n 3 >> %s" % (ci(h, "status"), ci(h, "customer"), ci(h, "amount"), p, o), "cat " + o]
    make("tab-32046", sub="write", desc="Writes the top 3 customers by paid total to a CSV, void orders excluded",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["void orders must not be counted"],
         turns=[T("Find the three customers with the largest total amount among paid orders in sales/orders.csv (leave out void ones) and save them to sales/top3_customers.csv with the header customer,paid_total, biggest first, totals to 2 decimals.", calc, "files", ref, out=(o, ","))])


@reg
def c47():
    cols = [("记录", ID("J", 5, 1)), ("城市", C(["北京", "上海", "广州", "成都", "武汉"])), ("用户", F(lambda g, r: "u%03d" % g.randint(1, 400))), ("订单数", I(1, 9)), ("日期", D(2026, 9, 9))]
    h, rows = gen_rows(320478, cols, 520)
    p, o = "运营/活跃.csv", "运营/城市活跃用户.csv"
    calc = ('d = defaultdict(set)\nfor r in R:\n    d[r["城市"]].add(r["用户"])\nitems = sorted(d.items(), key=lambda kv: (-len(kv[1]), kv[0]))\n'
            'assert len({len(v) for _, v in items}) == len(items)\nresult = [["城市", "不同用户数"]] + [[k, str(len(v))] for k, v in items]')
    ref = ["head -3 " + p, "printf '城市,不同用户数\\n' > " + o,
           "awk -F, 'NR>1 && NF{print $%d\",\"$%d}' %s | sort -u | cut -d, -f1 | uniq -c | awk '{print $2\",\"$1}' | sort -t, -k2,2 -rn >> %s" % (ci(h, "城市"), ci(h, "用户"), p, o), "cat " + o]
    make("tab-32047", sub="write", desc="Writes the number of different active users per city to a CSV",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, trail=1, ref_calls=4,
         notes_traps=["one user appears in many rows; must count users once per city, not rows"],
         turns=[T("运营/活跃.csv 里每一行是一次活跃记录，同一个用户会出现很多次。请统计每个城市有多少个不同的用户，写到 运营/城市活跃用户.csv：表头 城市,不同用户数，按人数从多到少排。", calc, "files", ref, out=(o, ","))])


@reg
def c48():
    cols = [("job", ID("J", 5, 3000)), ("queue", C(["batch", "gpu", "interactive"])), ("state", C(["done", "failed", "killed"], [82, 12, 6])), ("reason", F(lambda g, r: "-" if r["state"] == "done" else g.choices(["oom", "timeout", "disk full", "preempted"], [45, 28, 17, 10])[0])),
            ("runtime_s", I(5, 7200))]
    h, rows = gen_rows(320481, cols, 410)
    p, o1, o2 = "cluster/jobs.csv", "cluster/failed_jobs.csv", "cluster/failed_by_reason.csv"
    calc1 = 'result = [list(R[0].keys())] + [list(r.values()) for r in R if r["state"] == "failed"]'
    calc2 = ('d = Counter(r["reason"] for r in R if r["state"] == "failed")\nitems = sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))\n'
             'assert len({v for _, v in items}) == len(items)\nresult = [["reason", "jobs"]] + [[k, str(v)] for k, v in items]')
    ref1 = ["head -3 " + p, "head -1 %s > %s" % (p, o1), "awk -F, 'NR>1 && NF && $%d==\"failed\"' %s >> %s" % (ci(h, "state"), p, o1), "wc -l " + o1]
    ref2 = ["printf 'reason,jobs\\n' > " + o2, "awk -F, 'NR>1 && NF && $%d==\"failed\"{print $%d}' %s | sort | uniq -c | sort -rn | awk '{n=$1; $1=\"\"; sub(/^ /,\"\"); print $0\",\"n}' >> %s" % (ci(h, "state"), ci(h, "reason"), p, o2), "cat " + o2]
    make("tab-32048", sub="write", desc="Copies failed jobs to a new CSV, then writes failure counts by reason",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=6,
         notes_traps=["reason has a two word value 'disk full' (awk default splitting breaks it); killed jobs also have reasons but must be excluded"],
         turns=[T("Copy the rows of cluster/jobs.csv whose state is failed into cluster/failed_jobs.csv, keeping the header and all columns exactly as they are. Leave the original alone, and tell me how many rows you copied.", calc1, "files", ref1, out=(o1, ",")),
                T("Now count those failed jobs per reason and write cluster/failed_by_reason.csv with header reason,jobs, most frequent first.", calc2, "files", ref2, out=(o2, ","))])


@reg
def c49():
    cols = [("sample", ID("P", 4, 1)), ("plate", C(["A1", "A2", "B1", "B2"])), ("od600", M(0.05, 1.9, 3)), ("dilution", C(["1", "10", "100"])), ("operator", C(["mo", "ke", "ri"]))]
    h, rows = gen_rows(32049, cols, 300)
    p, o = "lab/od_readings.tsv", "lab/plate_means.csv"
    calc = ('d = defaultdict(list)\nfor r in R:\n    d[r["plate"]].append(N(r["od600"]))\n'
            'result = [["plate", "mean_od600"]] + [[k, "%.3f" % (sum(d[k]) / len(d[k]))] for k in sorted(d)]')
    ref = ["head -3 " + p, "printf 'plate,mean_od600\\n' > " + o,
           "awk -F'\\t' 'NR>1 && NF{s[$%d]+=$%d; n[$%d]++} END{for(k in s) printf \"%%s,%%.3f\\n\", k, s[k]/n[k]}' %s | sort >> %s" % (ci(h, "plate"), ci(h, "od600"), ci(h, "plate"), p, o), "cat " + o]
    make("tab-32049", sub="write", desc="Reads a tab separated file and writes a comma separated mean per plate",
         traps=["TR-DELIM"], path=p, header=h, rows=rows, delim="\t", ref_calls=4,
         notes_traps=["input is tab separated, output must be comma separated"],
         turns=[T("lab/od_readings.tsv holds plate readings. Write lab/plate_means.csv (comma separated, header plate,mean_od600) with the mean od600 per plate to 3 decimals, plates in alphabetical order.", calc, "files", ref, out=(o, ","))])


@reg
def c50():
    cols = [("编号", ID("B", 5, 1)), ("日期", D(2026, 8, 9)), ("科目", C(["办公", "差旅", "培训", "招待"])), ("预算", M(1000, 90000, 2, True)), ("实际", M(500, 95000, 2, True))]
    h, rows = gen_rows(32050, cols, 280)
    p, o = "预算/执行.csv", "预算/科目对比.csv"
    calc = ('b = defaultdict(float); a = defaultdict(float)\nfor r in R:\n    b[r["科目"]] += N(r["预算"]); a[r["科目"]] += N(r["实际"])\n'
            'result = [["科目", "预算合计", "实际合计", "差额"]] + [[k, "%.2f" % b[k], "%.2f" % a[k], "%.2f" % (a[k] - b[k])] for k in sorted(b)]')
    ref = ["head -4 " + p, "printf '科目,预算合计,实际合计,差额\\n' > " + o,
           "cat %s | %s | awk -F, 'NR>1 && NF{b[$%d]+=$%d; a[$%d]+=$%d} END{for(k in b) printf \"%%s,%%.2f,%%.2f,%%.2f\\n\", k, b[k], a[k], a[k]-b[k]}' | sort >> %s" % (p, SEDK, ci(h, "科目"), ci(h, "预算"), ci(h, "科目"), ci(h, "实际"), o), "cat " + o]
    make("tab-32050", sub="write", desc="Writes budget vs actual per category with quoted thousands numbers",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["预算 and 实际 both quoted with thousands commas; difference = actual minus budget"],
         turns=[T("预算/执行.csv 里预算和实际都是带千分位的金额。请按科目汇总，写到 预算/科目对比.csv：表头 科目,预算合计,实际合计,差额（差额=实际合计-预算合计），每个科目一行，按科目名排序，金额两位小数、不要千分位。", calc, "files", ref, out=(o, ","))])
