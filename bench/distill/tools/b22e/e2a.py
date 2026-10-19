"""E2 big tables, cases tab-34426..34433."""
import datetime as dt
from common import *
from lg import pick

B = []


def reg(f):
    B.append(f)
    return f


D = dt.date


def pre(path, delim=","):
    return ("import csv, io, collections\nrows = list(csv.DictReader(io.StringIO(files[%r]), delimiter=%r))\n"
            "cents = lambda x: round(float(x) * 100)\n" % (path, delim))


def csv_text(rows, sep=","):
    return "".join(sep.join(str(c) for c in row) + "\n" for row in rows)


def money(r, lo, hi):
    return "%.2f" % (r.randint(int(lo * 100), int(hi * 100)) / 100.0)


def wpick(r, pairs):
    tot = sum(w for _, w in pairs)
    x = r.uniform(0, tot)
    for v, w in pairs:
        x -= w
        if x <= 0:
            return v
    return pairs[-1][0]


def day(r, y, m1, m2):
    return D(y, r.randint(m1, m2), r.randint(1, 28)).isoformat()


@reg
def t01():
    r = rng("t01"); n = 3000
    regs = [("华东", 22), ("华北", 20), ("华南", 26), ("西南", 17), ("东北", 15)]
    rows = [["order_id", "date", "region", "category", "qty", "amount"]]
    for i in range(n):
        rows.append(["O-%d" % (100001 + i), day(r, 2026, 6, 9), wpick(r, regs), pick_c(r), r.randint(1, 9), money(r, 15, 980)])
    f = {"sales/orders.csv": csv_text(rows)}
    make("tab-34426", sub="E2", task_type="aggregate", desc="Region with the highest total amount in a 3000-row orders table, then that total",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("sales/orders.csv 里按区域汇总金额（amount），哪个区域最高？"), T("它的金额合计是多少？保留两位小数。", "f")],
         truth=pre("sales/orders.csv") + "t = collections.Counter()\nfor x in rows:\n    t[x['region']] += cents(x['amount'])\nm, v = t.most_common(1)[0]\nanswers = [[m], v / 100.0]\n",
         ref=[("head -3 sales/orders.csv; wc -l sales/orders.csv; awk -F, 'NR>1{s[$3]+=$6} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' sales/orders.csv | sort -k2 -nr", lambda a: a[0][0]),
              ("awk -F, 'NR>1{s[$3]+=$6} END{for(k in s) printf \"%s %.2f\\n\", k, s[k]}' sales/orders.csv | sort -k2 -nr | head -1", lambda a: "%.2f" % a[1])],
         notes={"traps": "Five regions with close totals; amount is the last column, qty is adjacent.", "steps": "head/wc -l, then awk group sum | sort.", "unique": "Recomputed from the fixture; the leader is ahead by several percent."})


def pick_c(r):
    return wpick(r, [("饮品", 30), ("甜点", 20), ("轻食", 25), ("套餐", 15), ("周边", 10)])


@reg
def t02():
    r = rng("t02"); n = 2800
    rows = [["txn_id", "ts", "account", "type", "amount", "status"]]
    for i in range(n):
        rows.append(["TX%06d" % (400000 + i * 3 + r.randint(0, 2)), "2026-07-%02d %02d:%02d:%02d" % (1 + i * 28 // n, r.randint(0, 23), r.randint(0, 59), r.randint(0, 59)),
                     "AC%04d" % r.randint(1, 400), wpick(r, [("deposit", 3), ("withdraw", 4), ("transfer", 3), ("fee", 1)]), money(r, 5, 4800), wpick(r, [("ok", 40), ("pending", 3), ("failed", 2)])])
    rows[2411][4] = "91874.50"
    rows[2411][3] = "transfer"
    f = {"transactions.csv": csv_text(rows)}
    make("tab-34427", sub="E2", task_type="rank", desc="Largest single transaction in a 2800-row ledger, then its amount",
         files=f, shape="csv", rc=3, deep=False,
         turns=[T("Which transaction in transactions.csv has the biggest amount? Give its txn_id."), T("What is that amount?", "f")],
         truth=pre("transactions.csv") + "m = max(rows, key=lambda x: cents(x['amount']))\nanswers = [[m['txn_id']], float(m['amount'])]\n",
         ref=[("sort -t, -k5 -nr transactions.csv | head -2", lambda a: a[0][0]), ("sort -t, -k5 -nr transactions.csv | head -1", lambda a: "%.2f" % a[1])],
         notes={"traps": "The header line must not be treated as data; the maximum is at row 2412, far below the first screen.", "steps": "head -3; sort -t, -k5 -nr | head -2.", "unique": "The maximum is a planted amount far above the random range."})


@reg
def t03():
    r = rng("t03"); n = 2600
    rows = [["ticket_no", "visit_day", "member_no", "outlet", "basket_value"]]
    pool = ["C%04d" % r.randint(1, 9999) for _ in range(430)]
    for i in range(n):
        rows.append(["V%05d" % (i + 1), day(r, 2026, 5, 8), pick(r, pool), pick(r, ["徐汇", "静安", "浦东", "闵行"]), money(r, 8, 260)])
    f = {"会员/门店到访明细-0508.csv": csv_text(rows)}
    make("tab-34428", sub="E2", task_type="filter_count", desc="Distinct customer ids in a 2600-visit table",
         files=f, shape="csv", rc=3, deep=False,
         turns=[T("会员/门店到访明细-0508.csv 里一共有多少位不同的会员（member_no）来过？同一个人多次到店只算一位。", "i")],
         truth=pre("会员/门店到访明细-0508.csv") + "answers = [len(set(x['member_no'] for x in rows))]\n",
         ref=[("tail -n +2 会员/门店到访明细-0508.csv | cut -d, -f3 | sort -u | wc -l", lambda a: str(a[0]))],
         notes={"traps": "Row count (2600) is not the distinct count; header must be excluded.", "steps": "wc -l, head; cut -f3 | sort -u | wc -l.", "unique": "Recomputed from the fixture."})


@reg
def t04():
    r = rng("t04"); n = 3400
    cats = [("laptop", 8), ("monitor", 12), ("dock", 14), ("cable", 30), ("headset", 16), ("keyboard", 20)]
    rows = [["id", "date", "category", "units", "revenue"]]
    for i in range(n):
        rows.append(["R%05d" % (i + 1), day(r, 2026, 6, 9), wpick(r, cats), r.randint(1, 12), money(r, 9, 1900)])
    f = {"revenue.csv": csv_text(rows)}
    make("tab-34429", sub="E2", task_type="aggregate", desc="Revenue of one category in one month of a 3400-row table",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("Total revenue of the monitor category in August 2026 according to revenue.csv? Two decimals please.", "f")],
         truth=pre("revenue.csv") + "answers = [sum(cents(x['revenue']) for x in rows if x['category'] == 'monitor' and x['date'].startswith('2026-08')) / 100.0]\n",
         ref=[("awk -F, 'NR>1 && $3==\"monitor\" && substr($2,1,7)==\"2026-08\"{s+=$5} END{printf \"%.2f\\n\", s}' revenue.csv", lambda a: "%.2f" % a[0])],
         notes={"traps": "Revenue is the last column, units is adjacent; the table covers four months.", "steps": "head -3, wc -l, awk with two conditions.", "unique": "Recomputed from the fixture."})


@reg
def t05():
    r = rng("t05"); n = 2400
    rows = [["sku", "name", "warehouse", "stock", "status"]]
    names = ["保温杯", "折叠椅", "充电宝", "雨伞", "台灯", "收纳盒", "耳机", "键盘", "鼠标垫", "水壶"]
    for i in range(n):
        rows.append(["SKU%05d" % (i + 1), "%s%02d型" % (pick(r, names), r.randint(1, 60)), pick(r, ["WH-A", "WH-B", "WH-C"]), r.randint(12, 900), wpick(r, [("active", 14), ("retired", 4)])])
    rows[2077][3] = "1"; rows[2077][4] = "active"
    rows[130][3] = "0"; rows[130][4] = "retired"
    f = {"inventory.csv": csv_text(rows)}
    make("tab-34430", sub="E2", task_type="rank", desc="Lowest stock among active SKUs; a retired SKU has an even lower stock",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("inventory.csv 里状态是 active 的商品中，库存（stock）最少的是哪个？给我它的 sku。", "s")],
         truth=pre("inventory.csv") + "a = [x for x in rows if x['status'] == 'active']\nm = min(a, key=lambda x: int(x['stock']))\nanswers = [[m['sku']]]\n",
         ref=[("awk -F, 'NR>1 && $5==\"active\"' inventory.csv | sort -t, -k4 -n | head -2", lambda a: a[0][0])],
         notes={"traps": "A retired SKU near the top has stock 0; the active minimum is at row 2078 with stock 1.", "steps": "awk filter active | sort -k4 -n | head.", "unique": "SKU02078 with stock 1; the only active row with stock below 12."})


@reg
def t06():
    r = rng("t06"); n = 3100
    agents = ["mia", "noah", "liu", "omar", "pia", "quinn", "ravi"]
    rows = [["call_id", "date", "agent", "queue", "duration_s", "resolved"]]
    for i in range(n):
        rows.append(["CL%05d" % (i + 1), day(r, 2026, 7, 9), pick(r, agents), pick(r, ["billing", "tech", "sales"]), r.randint(30, 1500), pick(r, ["yes", "yes", "no"])])
    f = {"support/calls.csv": csv_text(rows)}
    make("tab-34431", sub="E2", task_type="aggregate", desc="Average call duration of one agent over a 3100-row call table",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("What is the average duration_s of the calls handled by agent ravi in support/calls.csv? Round to two decimals.", "f")],
         truth=pre("support/calls.csv") + "d = [int(x['duration_s']) for x in rows if x['agent'] == 'ravi']\nanswers = [round(sum(d) / len(d), 2)]\n",
         ref=[("awk -F, 'NR>1 && $3==\"ravi\"{s+=$5;n++} END{printf \"%.2f\\n\", s/n}' support/calls.csv", lambda a: "%.2f" % a[0])],
         notes={"traps": "Average needs both the sum and the count of the filtered rows, not the whole table.", "steps": "head -3, wc -l, awk sum/count with agent filter.", "unique": "Recomputed from the fixture."})


@reg
def t07():
    r = rng("t07"); n = 3500
    rows = [["ref_no", "booked_on", "buyer", "settle_state", "gross"]]
    for i in range(n):
        rows.append(["N%06d" % (710000 + i), day(r, 2026, 4, 9), "cust%03d" % r.randint(1, 300), wpick(r, [("paid", 60), ("refunded", 8), ("cancelled", 6), ("pending", 4)]), money(r, 20, 1400)])
    f = {"售后/退款对账明细-q2.csv": csv_text(rows)}
    make("tab-34432", sub="E2", task_type="filter_count", desc="Refunded orders above 500, then the sum of all refunded orders",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("售后/退款对账明细-q2.csv 里结算状态（settle_state）为 refunded 且 gross 大于 500 的订单有多少笔？", "i"), T("所有 refunded 订单的 gross 合计是多少？保留两位小数。", "f")],
         truth=pre("售后/退款对账明细-q2.csv") + "rf = [x for x in rows if x['settle_state'] == 'refunded']\nanswers = [len([x for x in rf if float(x['gross']) > 500]), sum(cents(x['gross']) for x in rf) / 100.0]\n",
         ref=[("awk -F, 'NR>1 && $4==\"refunded\" && $5>500' 售后/退款对账明细-q2.csv | wc -l", lambda a: str(a[0])), ("awk -F, 'NR>1 && $4==\"refunded\"{s+=$5} END{printf \"%.2f\\n\", s}' 售后/退款对账明细-q2.csv", lambda a: "%.2f" % a[1])],
         notes={"traps": "Two different filters over the same status; 'greater than 500' excludes exactly 500.00 rows (if any).", "steps": "awk with status and amount conditions.", "unique": "Recomputed from the fixture."})


@reg
def t08():
    r = rng("t08"); n = 2900
    prods = {"燕麦拿铁": 30, "冰美式": 26, "芝士蛋糕": 12, "可颂": 18, "抹茶千层": 9, "肉桂卷": 14, "气泡水": 22, "司康": 8}
    items = [(k, v) for k, v in prods.items()]
    rows = [["line_id", "date", "product", "qty", "price"]]
    for i in range(n):
        rows.append(["L%05d" % (i + 1), day(r, 2026, 8, 9), wpick(r, items), r.randint(1, 6), money(r, 8, 48)])
    f = {"pos/lines.csv": csv_text(rows)}
    make("tab-34433", sub="E2", task_type="rank", desc="Top three products by total quantity in a 2900-row POS table",
         files=f, shape="csv", rc=4, deep=False,
         turns=[T("pos/lines.csv 里按 qty 总数算，卖得最多的前三个商品是哪些？按从多到少列出来。", "s")],
         truth=pre("pos/lines.csv") + "t = collections.Counter()\nfor x in rows:\n    t[x['product']] += int(x['qty'])\nmc = t.most_common(4)\nassert mc[2][1] != mc[3][1]\nanswers = [[k for k, _ in mc[:3]]]\n",
         ref=[("awk -F, 'NR>1{s[$3]+=$4} END{for(k in s) print s[k], k}' pos/lines.csv | sort -rn | head -4", lambda a: a[0][0])],
         notes={"traps": "Ranking is by summed qty, not by row count or by price; the header row must be skipped.", "steps": "awk sum by product | sort -rn | head.", "unique": "Fourth place is strictly behind third."})
