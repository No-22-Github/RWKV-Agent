"""data_query part 2: jsonl/tsv sources, max-by-date, multi-turn."""
import json

from common import mk, rng
from q1 import table

B = []


def b(f):
    B.append(f)
    return f


@b
def q08():
    r = rng("q08")
    rows = []
    for i in range(60):
        for c in ["昆明", "拉萨", "三亚"]:
            rows.append(("2026-07-%02d" % (i % 31 + 1) if i < 31 else "2026-08-%02d" % (i - 30), c, r.randint(14, 31) if c != "三亚" else r.randint(30, 36)))
    # unique max for 三亚
    rows = [x for x in rows if x[1] == "三亚" or True]
    files = {"climate/highs.csv": table(["date", "city", "high"], rows)}
    sy = [x for x in rows if x[1] == "三亚"]
    mx = max(x[2] for x in sy)
    top = [x for x in sy if x[2] == mx]
    if len(top) > 1:
        i = rows.index(top[0])
        rows[i] = (rows[i][0], rows[i][1], mx + 1)
        files = {"climate/highs.csv": table(["date", "city", "high"], rows)}

    def compute(files, wx):
        import csv
        import io
        sy = [x for x in csv.DictReader(io.StringIO(files["climate/highs.csv"])) if x["city"] == "三亚"]
        m = max(int(x["high"]) for x in sy)
        d = [x["date"] for x in sy if int(x["high"]) == m]
        assert len(d) == 1
        y, mo, da = d[0].split("-")
        return {}, [[("any", [d[0], "%d月%d日" % (int(mo), int(da)), "%d月%d号" % (int(mo), int(da)), "%s-%s" % (mo, da), "%d/%d" % (int(mo), int(da)), "%s月%s日" % (mo, da)])]]
    mk("hyb-33650", sub="query", desc="Which date had the highest temperature for one city in a 180-row table", files=files,
       turns=[{"p": "climate/highs.csv 里三亚哪一天的最高气温最高？", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "2026-07-01"}, rc=3,
       notes="Filter city=三亚, max high, then find its date (select rows). Hottest overall row belongs to 三亚 uniquely.",
       alts=["三亚最热是哪天", "highs.csv 中三亚气温峰值的日期", "三亚最高温出现在几月几日", "找出三亚最高气温那天", "On which date was 三亚 hottest in climate/highs.csv?"])


@b
def q09():
    r = rng("q09")
    cats = ["图书", "文具", "数码", "食品", "家居", "运动"]
    rows = [(r.choice(cats), r.randint(20, 640)) for _ in range(178)]
    files = {"orders/categories.csv": table(["category", "amount"], rows)}
    tot = {}
    for c, a in rows:
        tot[c] = tot.get(c, 0) + a

    def compute(files, wx):
        import csv
        import io
        t = {}
        for x in csv.DictReader(io.StringIO(files["orders/categories.csv"])):
            t[x["category"]] = t.get(x["category"], 0) + int(x["amount"])
        n = sum(1 for v in t.values() if v > 11000)
        return {}, [[("num", t["图书"])], [("any", ["%d个" % n, "%d 个" % n, "%d类" % n, "%d 类" % n, "%d种" % n, "%d 种" % n, "%d 个品类" % n])]]
    n = sum(1 for v in tot.values() if v > 11000)
    assert 1 <= n <= 5
    mk("hyb-33651", sub="query", desc="Multi-turn: one category's total, then how many categories exceed a threshold", files=files,
       turns=[{"p": "orders/categories.csv 里图书这一类的订单金额合计是多少？", "req": ["data_query"]},
              {"p": "那所有品类里，合计超过 11000 的有几个？"}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": str(len(rows))}, rc=3,
       notes="Turn1 sum with filter category=图书; turn2 group_by category sum and count the groups above 11000.",
       alts=["图书类订单总额", "统计图书类别的金额之和", "categories.csv 图书合计多少钱", "图书这个品类一共卖了多少", "Total amount for the 图书 category in orders/categories.csv?"])


@b
def q10():
    r = rng("q10")
    rows = [{"ts": "2026-09-%02d" % (1 + i % 15), "service": r.choice(["api", "web", "worker"]), "level": r.choice(["info", "warn", "error", "info"]), "ms": r.randint(5, 900)} for i in range(205)]
    files = {"events.jsonl": "".join(json.dumps(x) + "\n" for x in rows)}
    n = sum(1 for x in rows if x["service"] == "api" and x["level"] == "error")

    def compute(files, wx):
        import json as j
        rs = [j.loads(l) for l in files["events.jsonl"].splitlines() if l.strip()]
        n = sum(1 for x in rs if x["service"] == "api" and x["level"] == "error")
        return {}, [[("any", ["%d条" % n, "%d 条" % n, "%d次" % n, "%d 次" % n, "%d个" % n, "%d 个" % n, "%d errors" % n, "%d error" % n])]]
    mk("hyb-33652", sub="query", desc="Count api-service error events in a 205-line jsonl file", files=files,
       turns=[{"p": "events.jsonl 里 api 服务的 error 级别事件有多少条？", "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": str(sum(1 for x in rows if x["level"] == "error"))}, rc=2,
       notes="data_query supports .jsonl: filter service=api, level=error, count. All-service error count is the decoy.",
       alts=["api 服务报错事件数", "events.jsonl 里 api 的 error 条数", "统计 api 服务 error 级别日志条数", "api 的错误事件一共多少", "How many error events does the api service have in events.jsonl?"])


@b
def q11():
    r = rng("q11")
    rows = [("SF%05d" % (i + 1), r.choice(["顺丰", "中通", "圆通"]), round(r.uniform(0.3, 18.0), 1), r.choice(["已签收", "运输中"])) for i in range(166)]
    files = {"物流/shipments.tsv": table(["no", "carrier", "weight_kg", "state"], rows, "\t")}

    def compute(files, wx):
        ls = files["物流/shipments.tsv"].strip().split("\n")[1:]
        v = sum(float(l.split("\t")[2]) for l in ls if l.split("\t")[1] == "顺丰")
        return {}, [[("num", round(v, 1))]]
    mk("hyb-33653", sub="query", desc="Sum of weights for one carrier in a tab-separated table", files=files,
       turns=[{"p": "物流文件夹里的 shipments.tsv，顺丰承运的包裹总重量是多少公斤？", "tol": 0.06, "req": ["data_query"]}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DELIM"], decoys={"TR-DELIM": "0"}, rc=2,
       notes="The file is tab-separated; data_query reads .tsv natively. Filter carrier=顺丰, sum weight_kg.",
       alts=["顺丰包裹总重多少公斤", "shipments.tsv 顺丰的重量合计", "统计顺丰承运货物总重量", "顺丰一共运了多少公斤", "Total weight in kg shipped by 顺丰 in 物流/shipments.tsv?"])


@b
def q12():
    r = rng("q12")
    rows = [("E%03d" % i, r.choice(["Eng", "Ops", "Sales"]), r.randint(52, 168) * 1000) for i in range(154)]
    files = {"hr/employees.csv": table(["id", "dept", "salary"], rows)}

    def compute(files, wx):
        import csv
        import io
        eng = [int(x["salary"]) for x in csv.DictReader(io.StringIO(files["hr/employees.csv"])) if x["dept"] == "Eng"]
        n = sum(1 for s in eng if s > 100000)
        return {}, [[("num", round(sum(eng) / len(eng), 2))], [("any", ["%d people" % n, "%d employees" % n, "%d engineers" % n, "%d of them" % n, "%d人" % n, "%d 人" % n, "%d staff" % n])]]
    mk("hyb-33654", sub="query", desc="English multi-turn: department average salary, then how many exceed 100000", files=files,
       turns=[{"p": "What is the average salary in the Eng department in hr/employees.csv? Two decimals please.", "tol": 0.006, "req": ["data_query"]},
              {"p": "And how many people in Eng earn more than 100000?"}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "%.2f" % (sum(x[2] for x in rows) / len(rows))}, rc=3,
       notes="Turn1 data_query avg salary filter dept=Eng. Turn2 needs a threshold filter: bash awk or select + count.",
       alts=["Eng average pay from hr/employees.csv", "Mean salary of the Eng team, 2 decimals", "Average Eng salary?", "hr/employees.csv: Eng mean salary", "Eng 部门平均工资是多少"])


@b
def q13():
    r = rng("q13")
    rows = [(r.choice(["北区", "南区", "东区", "西区"]), r.randint(1, 12), r.randint(8, 95)) for _ in range(188)]
    files = {"门店客流.csv": table(["zone", "month", "visitors"], rows)}

    def compute(files, wx):
        import csv
        import io
        rs = list(csv.DictReader(io.StringIO(files["门店客流.csv"])))
        v = [int(x["visitors"]) for x in rs if x["zone"] == "东区" and x["month"] == "8"]
        t = [int(x["visitors"]) for x in rs]
        return {}, [[("num", round(sum(v) / len(v), 2))], [("num", round(sum(t) / len(t) - sum(v) / len(v), 2))]]
    v = [x[2] for x in rows if x[0] == "东区" and x[1] == 8]
    assert len(v) > 2
    mk("hyb-33655", sub="query", desc="Multi-turn: zone-and-month average, then the gap to the overall average", files=files,
       turns=[{"p": "门店客流.csv 里东区 8 月份的平均客流是多少？保留两位小数。", "tol": 0.006, "req": ["data_query"]},
              {"p": "整张表所有行的平均客流比这个数高还是低？差多少？两位小数。", "tol": 0.006}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "%.2f" % (sum(x[2] for x in rows) / len(rows))}, rc=3,
       notes="Turn1 avg with two filters; turn2 overall avg minus turn1 (absolute figure in the answer; sign stated in words).",
       alts=["东区八月平均客流", "8 月东区每行平均客流多少", "门店客流 东区 8 月均值", "计算东区 8 月份客流的平均值", "Average visitors for 东区 in month 8?"])


@b
def q14():
    r = rng("q14")
    rows = [("A%04d" % i, r.choice(["华北", "华南"]), r.randint(25, 520)) for i in range(160)]
    files = {"data/客单价.csv": table(["id", "area", "amount"], rows)}
    n = len([x for x in rows if x[1] == "华南"])

    def compute(files, wx):
        import csv
        import io
        rs = list(csv.DictReader(io.StringIO(files["data/客单价.csv"])))
        nn = [int(x["amount"]) for x in rs if x["area"] == "华南"]
        bb = [int(x["amount"]) for x in rs if x["area"] == "华北"]
        return {}, [[("num", round(sum(nn) / len(nn), 2))], [("num", round(abs(sum(nn) / len(nn) - sum(bb) / len(bb)), 2))]]
    mk("hyb-33656", sub="query", desc="Multi-turn: average ticket for one area, then absolute gap to the other area", files=files,
       turns=[{"p": "data/客单价.csv 里华南的平均客单价是多少？两位小数。", "tol": 0.006, "req": ["data_query"]},
              {"p": "华北的呢？它们相差多少？两位小数，相差只要绝对值。", "tol": 0.006}],
       compute=compute, must=["data_query", "bash"], traps=["TR-DECOY"], decoys={"TR-DECOY": "%.2f" % (sum(x[2] for x in rows) / len(rows))}, rc=3,
       notes="Turn1 avg for 华南; turn2 avg for 华北 and absolute difference (the number in the answer is the difference).",
       alts=["华南客单价均值", "客单价.csv 华南的平均值", "华南地区平均每单多少钱", "算华南的平均订单金额", "Average order amount for 华南 in data/客单价.csv?"])
