"""data_query part 1: grouped sums, filtered counts, averages over 150+ row tables."""
from common import mk, rng

B = []


def b(f):
    B.append(f)
    return f


def table(header, rows, sep=","):
    return "\n".join([sep.join(header)] + [sep.join(str(c) for c in r) for r in rows]) + "\n"


def cnt_alts(n):
    return ["%d个" % n, "%d 个" % n, "%d条" % n, "%d 条" % n, "%d张" % n, "%d 张" % n, "%d 单" % n, "%d单" % n, "%d 次" % n, "%d次" % n, "%d 人" % n, "%d人" % n]


@b
def q01():
    r = rng("q01")
    regs = ["华东", "华南", "华北", "西南", "东北"]
    rows = [(1000 + i, r.choice(regs), r.choice(["键盘", "鼠标", "显示器", "耳机"]), r.randint(1, 9), r.choice([59, 89, 129, 399, 1299])) for i in range(190)]
    files = {"data/orders.csv": table(["order_id", "region", "product", "qty", "unit_price"], rows)}
    wrong = sum(x[3] * x[4] for x in rows if x[1] == "华东")
    tot = sum(x[3] for x in rows if x[1] == "华东")

    def compute(files, wx):
        import csv
        import io
        rs = list(csv.DictReader(io.StringIO(files["data/orders.csv"])))
        return {}, [[("num", sum(int(x["qty"]) * int(x["unit_price"]) for x in rs if x["region"] == "华东"))]]
    mk("hyb-33643", sub="query", desc="Revenue (qty x unit price) of one region from a 190-row order table",
       files=files, turns=[{"p": "data 文件夹里的 orders.csv，华东区的总销售额是多少？销售额按数量乘单价算。", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DEFN"], decoys={"TR-DEFN": str(tot)}, rc=2,
       notes="data_query path=data/orders.csv filter {region: 华东} operation sum expression qty*unit_price. Decoy: summing qty only (%d)." % tot,
       alts=["orders.csv 华东区销售额合计", "华东的订单金额一共多少（数量×单价）", "统计 data/orders.csv 里华东地区的总收入", "华东区卖了多少钱", "Total revenue for region 华东 in data/orders.csv (qty x unit_price)?"])


@b
def q02():
    r = rng("q02")
    rows = [(5000 + i, r.choice(["P0", "P1", "P2", "P3"]), r.choice(["open", "closed", "pending"]), r.choice(["支付组", "账号组", "推荐组"])) for i in range(210)]
    files = {"tickets.csv": table(["id", "priority", "status", "team"], rows)}
    n = sum(1 for x in rows if x[1] == "P1" and x[2] == "open" and x[3] == "支付组")

    def compute(files, wx):
        import csv
        import io
        rs = list(csv.DictReader(io.StringIO(files["tickets.csv"])))
        n = sum(1 for x in rs if x["priority"] == "P1" and x["status"] == "open" and x["team"] == "支付组")
        return {}, [[("any", ["%d个" % n, "%d 个" % n, "%d条" % n, "%d 条" % n, "%d张" % n, "%d 张" % n, "%d 单" % n, "%d单" % n])]]
    mk("hyb-33644", sub="query", desc="Count tickets matching three filters in a 210-row table", files=files,
       turns=[{"p": "tickets.csv 里支付组还处于 open 状态的 P1 工单有多少张？", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": str(sum(1 for x in rows if x[1] == "P1"))}, rc=2,
       notes="Three filters at once: priority=P1, status=open, team=支付组.",
       alts=["支付组 open 的 P1 工单数量", "tickets.csv 中支付组、P1、open 的有几张", "数一下支付组未关闭（open）的 P1 工单", "P1 且 open 且属于支付组的工单个数", "How many open P1 tickets does 支付组 have in tickets.csv?"])


@b
def q03():
    r = rng("q03")
    names = ["林", "陈", "赵", "孙", "周", "吴", "郑", "王"]
    rows = [("%s%02d" % (r.choice(names), i), r.choice(["一班", "二班", "三班", "四班"]), r.randint(48, 100)) for i in range(165)]
    files = {"exam/scores.csv": table(["student", "class", "score"], rows)}

    def compute(files, wx):
        import csv
        import io
        rs = [x for x in csv.DictReader(io.StringIO(files["exam/scores.csv"])) if x["class"] == "三班"]
        return {}, [[("num", round(sum(int(x["score"]) for x in rs) / len(rs), 2))]]
    allavg = sum(x[2] for x in rows) / len(rows)
    mk("hyb-33645", sub="query", desc="Average score of one class from a 165-row score table", files=files,
       turns=[{"p": "exam/scores.csv 里三班的平均分是多少？保留两位小数。", "tol": 0.006, "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "%.2f" % allavg}, rc=2,
       notes="data_query filter {class: 三班} operation avg field score. Whole-table average is the decoy.",
       alts=["三班平均成绩", "exam/scores.csv 三班的均分（两位小数）", "算一下三班同学分数的平均值", "三班均分多少", "Average score of class 三班 in exam/scores.csv, two decimals?"])


@b
def q04():
    r = rng("q04")
    ppl = ["Mia", "Noah", "Zoe", "Liam", "Ava", "Ethan", "Ivy", "Owen"]
    rows = [(r.choice(ppl), r.choice(["Q1", "Q2", "Q3"]), r.randint(120, 980)) for _ in range(176)]
    files = {"sales_by_rep.csv": table(["rep", "quarter", "amount"], rows)}
    tot = {}
    for x in rows:
        if x[1] == "Q3":
            tot[x[0]] = tot.get(x[0], 0) + x[2]
    srt = sorted(tot.values())
    assert srt[-1] != srt[-2]

    def compute(files, wx):
        import csv
        import io
        t = {}
        for x in csv.DictReader(io.StringIO(files["sales_by_rep.csv"])):
            if x["quarter"] == "Q3":
                t[x["rep"]] = t.get(x["rep"], 0) + int(x["amount"])
        return {}, [[("all", [max(t, key=t.get)])]]
    best_all = {}
    for x in rows:
        best_all[x[0]] = best_all.get(x[0], 0) + x[2]
    mk("hyb-33646", sub="query", desc="Top rep by total amount in one quarter (grouped sum, English)", files=files,
       turns=[{"p": "In sales_by_rep.csv, which rep has the largest total amount in Q3?", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": max(best_all, key=best_all.get)}, rc=2,
       notes="group_by rep with filter quarter=Q3 and sum amount; whole-year leader (%s) is the decoy." % max(best_all, key=best_all.get),
       alts=["Who sold the most in Q3 according to sales_by_rep.csv?", "Top Q3 rep by total amount", "Rank reps by Q3 amount: who is first?", "Which salesperson leads in Q3 totals?", "sales_by_rep.csv 里 Q3 总金额最高的是谁"])


@b
def q05():
    r = rng("q05")
    rows = [(7000 + i, r.choice(["深圳", "广州", "东莞", "佛山"]), r.randint(30, 480)) for i in range(172)]
    files = {"sales/月度订单.csv": table(["order_id", "city", "amount"], rows)}

    def compute(files, wx):
        import csv
        import io
        rs = [x for x in csv.DictReader(io.StringIO(files["sales/月度订单.csv"])) if x["city"] == "深圳"]
        n = len(rs)
        return {}, [[("any", ["%d单" % n, "%d 单" % n, "%d个" % n, "%d 个" % n, "%d条" % n, "%d 条" % n, "%d笔" % n, "%d 笔" % n])],
                    [("num", round(sum(int(x["amount"]) for x in rs) / n, 2))]]
    mk("hyb-33647", sub="query", desc="Multi-turn: count rows for one city, then the average amount of those rows", files=files,
       turns=[{"p": "sales 文件夹里的月度订单.csv，深圳的订单有多少单？", "req": ["data_query"]},
              {"p": "这些深圳订单的平均金额是多少？保留两位小数。", "tol": 0.006}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "172"}, rc=3,
       notes="Turn1 count with filter city=深圳; turn2 avg amount with the same filter.",
       alts=["月度订单里深圳有几单", "深圳订单数量", "统计 sales/月度订单.csv 中城市为深圳的行数", "深圳一共多少笔订单", "How many orders are from 深圳 in sales/月度订单.csv?"])


@b
def q06():
    r = rng("q06")
    rows = [(r.randint(100, 160), r.choice(["/home", "/pricing", "/docs", "/blog"]), r.randint(80, 4000)) for _ in range(230)]
    files = {"logs/visits.csv": table(["user_id", "page", "ms"], rows)}
    n = len({x[0] for x in rows if x[1] == "/pricing"})

    def compute(files, wx):
        import csv
        import io
        n = len({x["user_id"] for x in csv.DictReader(io.StringIO(files["logs/visits.csv"])) if x["page"] == "/pricing"})
        return {}, [[("any", ["%d人" % n, "%d 人" % n, "%d个" % n, "%d 个" % n, "%d位" % n, "%d 位" % n, "%d users" % n, "%d unique" % n, "%d distinct" % n])]]
    mk("hyb-33648", sub="query", desc="Distinct users who visited a page (not row count)", files=files,
       turns=[{"p": "logs/visits.csv 里有多少个不同的用户访问过 /pricing 页面？", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DUPROW"], decoys={"TR-DUPROW": str(sum(1 for x in rows if x[1] == "/pricing"))}, rc=2,
       notes="distinct_count of user_id with filter page=/pricing. Row count of /pricing visits is the decoy.",
       alts=["访问 /pricing 的独立用户数", "有几个用户看过定价页（/pricing）", "pricing 页面的 UV 是多少", "/pricing 一共多少不同用户", "Unique visitors of /pricing in logs/visits.csv?"])


@b
def q07():
    r = rng("q07")
    rows = [("SKU%03d" % i, r.choice(["A", "B", "C"]), r.randint(0, 240), r.choice([4.5, 12.8, 19.9, 36.0, 59.5])) for i in range(158)]
    files = {"inventory.csv": table(["sku", "warehouse", "stock", "price"], rows)}

    def compute(files, wx):
        import csv
        import io
        v = sum(int(x["stock"]) * float(x["price"]) for x in csv.DictReader(io.StringIO(files["inventory.csv"])) if x["warehouse"] == "B")
        return {}, [[("num", round(v, 2))]]
    mk("hyb-33649", sub="query", desc="English: stock value (stock x price) of warehouse B", files=files,
       turns=[{"p": "What is the total stock value of warehouse B in inventory.csv? Value means stock times price, summed over its SKUs.", "tol": 0.006, "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DEFN"], decoys={"TR-DEFN": str(sum(x[2] for x in rows if x[1] == "B"))}, rc=2,
       notes="data_query filter warehouse=B, sum with expression stock*price. Summing stock only is the decoy.",
       alts=["Warehouse B inventory value from inventory.csv", "Sum of stock*price for warehouse B", "How much is the stock in warehouse B worth?", "inventory.csv: total worth of B warehouse stock", "B 仓库的库存总价值是多少（库存×单价）"])
