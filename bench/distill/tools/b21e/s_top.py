"""Sub 3: distinct count and top-N (10 cases, 32025-32034)."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def top_count(col, n, cond=None):
    flt = ("if %s" % cond) if cond else ""
    return ('c = Counter(r[%r] for r in R %s)\nitems = sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))\n'
            'assert items[%d - 1][1] != items[%d][1]\nresult = [k for k, _ in items[:%d]]' % (col, flt, n, n, n))


def top_sum(col, val, n, cond=None):
    flt = ("if %s" % cond) if cond else ""
    return ('c = defaultdict(float)\nfor r in R:\n    if %s:\n        c[r[%r]] += N(r[%r])\n'
            'items = sorted(c.items(), key=lambda kv: (-round(kv[1], 2), kv[0]))\n'
            'assert round(items[%d - 1][1], 2) != round(items[%d][1], 2)\nresult = [k for k, _ in items[:%d]]' % (cond or "True", col, val, n, n, n))


def ref_top_count(p, h, col, n, F=",", skip=1, pre=None, cond=""):
    src = "cat %s | %s |" % (p, pre) if pre else ""
    f = "" if pre else " " + p
    return ("%s awk -F'%s' 'NR>%d && NF%s{print $%d}'%s | sort | uniq -c | sort -rn | head -n %d" % (src, F, skip, cond, ci(h, col), f, n)).strip()


def ref_top_sum(p, h, col, val, n, F=",", skip=1, pre=None, cond=""):
    src = "cat %s | %s |" % (p, pre) if pre else ""
    f = "" if pre else " " + p
    return ("%s awk -F'%s' 'NR>%d && NF%s{s[$%d]+=$%d} END{for(k in s) printf \"%%.2f %%s\\n\", s[k], k}'%s | sort -rn | head -n %d" % (src, F, skip, cond, ci(h, col), ci(h, val), f, n)).strip()


@reg
def c25():
    cols = [("订单号", ID("DD", 5, 51000)), ("商品", C(["保温杯", "蓝牙耳机", "键盘", "鼠标垫", "充电宝", "台灯", "水杯刷", "手机支架", "小风扇", "收纳盒"], [14, 12, 9, 7, 16, 11, 4, 8, 13, 6])), ("数量", I(1, 4)), ("金额", M(15, 400)), ("日期", D(2026, 8, 9))]
    h, rows = gen_rows(32025, cols, 420)
    p = "电商/订单行.csv"
    make("tab-32025", sub="topn", desc="Top 3 products by number of order lines in a 420-row file",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["数量 and 金额 are numeric decoys; the ranking is by number of lines, not quantity"],
         turns=[T("电商/订单行.csv 里，按订单行数（出现次数）算，卖得最多的前三个商品是哪些？按从多到少列出名字。", top_count("商品", 3), "names",
                  ["head -3 " + p, ref_top_count(p, h, "商品", 3)])])


@reg
def c26():
    cols = [("invoice", ID("INV-", 5, 7000)), ("customer", C(["Acme Retail", "Blue Harbor", "Cedar and Co", "Delta Foods", "Evergreen Ltd", "Fjord Labs", "Granite Works", "Harbor Light"])),
            ("net_total", M(200, 22000, 2, True)), ("tax", M(10, 3000, 2, True)), ("issued", D(2026, 7, 9))]
    h, rows = gen_rows(32026, cols, 300)
    p = "billing/invoices.csv"
    make("tab-32026", sub="topn", desc="Top 3 customers by total net_total with quoted thousands numbers",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["net_total and tax both quoted with thousands commas"],
         turns=[T("Which three customers have the largest total net_total in billing/invoices.csv? List the names, biggest first.", top_sum("customer", "net_total", 3), "names",
                  ["head -4 " + p, ref_top_sum(p, h, "customer", "net_total", 3, pre=SEDK)])])


@reg
def c27():
    cols = [("访问ID", ID("V", 6, 1)), ("用户", F(lambda g, r: "u%03d" % g.randint(1, 85))), ("页面", C(["首页", "详情", "购物车", "结算"], [40, 35, 15, 10])), ("停留秒", I(1, 300)), ("日期", D(2026, 9, 9))]
    h, rows = gen_rows(32027, cols, 540)
    p = "埋点/访问.csv"
    make("tab-32027", sub="topn", desc="Number of different users who visited the checkout page",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["访问ID vs 用户; counting rows instead of different users over-counts"],
         turns=[T("埋点/访问.csv 里，访问过“结算”页面的用户一共有多少个不同的人？", 'result = len({r["用户"] for r in R if r["页面"] == "结算"})', "int",
                  ["head -3 " + p, "awk -F, 'NR>1 && NF && $%d==\"结算\"{print $%d}' %s | sort -u | wc -l" % (ci(h, "页面"), ci(h, "用户"), p)]),
                T("“购物车”页面呢？", 'result = len({r["用户"] for r in R if r["页面"] == "购物车"})', "int",
                  ["awk -F, 'NR>1 && NF && $%d==\"购物车\"{print $%d}' %s | sort -u | wc -l" % (ci(h, "页面"), ci(h, "用户"), p)])])


@reg
def c28():
    cols = [("device", F(lambda g, r: "dev-%02d" % g.randint(1, 60))), ("ts", D(2026, 9, 9)), ("fw", C(["1.4.2", "1.4.3", "1.5.0", "2.0.1"], [20, 30, 35, 15])), ("note", C(["", "", "reboot, manual", "ok", "sensor swap, rev B"])),
            ("battery", I(5, 100))]
    h, rows = gen_rows(32028, cols, 380)
    p = "iot/heartbeat.csv"
    make("tab-32028", sub="topn", desc="Number of different devices running firmware 1.5.0, note field quoted with comma",
         traps=["TR-DELIM"], path=p, header=h, rows=rows, trail=1, ref_calls=4,
         notes_traps=["note is quoted and may contain a comma; trailing empty line"],
         turns=[T("In iot/heartbeat.csv, how many different devices have reported firmware 1.5.0?", 'result = len({r["device"] for r in R if r["fw"] == "1.5.0"})', "int",
                  ["head -4 " + p, "cat %s | %s | awk -F, 'NR>1 && NF && $%d==\"1.5.0\"{print $%d}' | sort -u | wc -l" % (p, SEDQ, ci(h, "fw"), ci(h, "device"))])])


@reg
def c29():
    cols = [("Order ID", ID("Z", 5, 1000)), ("Sales Rep", C(["Ava Chen", "Ben Ortiz", "Cara Singh", "Dev Patel", "Eli Novak", "Fay Lin", "Gus Weber"], [9, 14, 6, 11, 5, 12, 8])), ("Unit Price", M(5, 300)),
            ("Qty Sold", I(1, 12)), ("Close Date", D(2026, 8, 9))]
    h, rows = gen_rows(32029, cols, 350)
    p = "crm/closed_deals.csv"
    make("tab-32029", sub="topn", desc="Top 2 sales reps by deal count; headers contain spaces",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["header names contain spaces (Sales Rep, Order ID)"],
         turns=[T("Looking at crm/closed_deals.csv, which two sales reps closed the most deals (rows)? Names only, most first.", top_count("Sales Rep", 2), "names",
                  ["head -3 " + p, ref_top_count(p, h, "Sales Rep", 2)])])


@reg
def c30():
    cols = [("ts", D(2026, 9, 9)), ("host", C(["web-1", "web-2", "web-3", "db-1"])), ("error_code", C(["E101", "E204", "E307", "E412", "E500", "E618", "E777", "OK"], [5, 9, 12, 7, 15, 3, 2, 120])),
            ("latency_ms", I(5, 900))]
    h, rows = gen_rows(32030, cols, 560)
    p = "ops/errors.tsv"
    make("tab-32030", sub="topn", desc="Top 3 error codes excluding OK in a tab separated file",
         traps=["TR-DELIM"], path=p, header=h, rows=rows, delim="\t", ref_calls=3,
         notes_traps=["tab separated; OK rows dominate the raw count"],
         turns=[T("In ops/errors.tsv, which three error codes appear most often, not counting OK? List them from most to least frequent.", top_count("error_code", 3, 'r["error_code"] != "OK"'), "names",
                  ["head -3 " + p, ref_top_count(p, h, "error_code", 3, F="\\t", cond=' && $%d!="OK"' % ci(h, "error_code"))])])


@reg
def c31():
    cols = [("学号", ID("S", 4, 1001)), ("社团", C(["篮球社", "动漫社", "摄影社", "编程社", "戏剧社", "街舞社", "烘焙社"], [12, 20, 8, 15, 6, 17, 9])), ("学院", C(["理学院", "文学院", "工学院", "商学院"])), ("年级", C(["大一", "大二", "大三", "大四"]))]
    h, rows = gen_rows(32232, cols, 450)
    p = "校园/社团报名.csv"
    make("tab-32031", sub="topn", desc="Top 3 clubs among one college then among another",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["学院 filter must be applied before ranking"],
         turns=[T("校园/社团报名.csv 里，工学院的学生报名最多的前三个社团是哪三个？从多到少。", top_count("社团", 3, 'r["学院"] == "工学院"'), "names",
                  ["head -3 " + p, ref_top_count(p, h, "社团", 3, cond=' && $%d=="工学院"' % ci(h, "学院"))]),
                T("文学院的呢？", top_count("社团", 3, 'r["学院"] == "文学院"'), "names",
                  [ref_top_count(p, h, "社团", 3, cond=' && $%d=="文学院"' % ci(h, "学院"))])])


@reg
def c32():
    cols = [("line", ID("L", 5, 1)), ("supplier", C(["Norte SA", "Kestrel GmbH", "Lumen Co", "Pacific Trade", "Orion Parts", "Quanta Ltd", "Rhone SARL"], [8, 11, 15, 6, 13, 9, 10])), ("amount_usd", M(100, 18000, 2, True)),
            ("po_date", D(2026, 8, 9)), ("late", C(["Y", "N"], [25, 75]))]
    h, rows = gen_rows(32032, cols, 330)
    p = "procure/po_lines.csv"
    make("tab-32032", sub="topn", desc="Top 3 suppliers by spend where amounts are quoted with thousands separators",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["amount_usd quoted with thousands commas"],
         turns=[T("From procure/po_lines.csv, which three suppliers did we spend the most with (sum of amount_usd)? Names, biggest first.", top_sum("supplier", "amount_usd", 3), "names",
                  ["head -4 " + p, ref_top_sum(p, h, "supplier", "amount_usd", 3, pre=SEDK)]),
                T("Now only counting lines flagged late, which three?", top_sum("supplier", "amount_usd", 3, 'r["late"] == "Y"'), "names",
                  [ref_top_sum(p, h, "supplier", "amount_usd", 3, pre=SEDK, cond=' && $%d=="Y"' % ci(h, "late"))])])


@reg
def c33():
    cols = [("记录", ID("R", 5, 1)), ("车牌", F(lambda g, r: "沪A%s%03d" % (g.choice("DEFGH"), g.randint(1, 70)))), ("入场", D(2026, 9, 9)), ("时长分钟", I(10, 600)), ("停车场", C(["东区", "西区", "地下一层"]))]
    h, rows = gen_rows(32033, cols, 480)
    p = "停车/入场记录.csv"
    make("tab-32033", sub="topn", desc="Number of different plates seen in one lot, with trailing empty lines",
         traps=["TR-HEADER"], path=p, header=h, rows=rows, trail=2, ref_calls=3,
         notes_traps=["empty lines at end of file"],
         turns=[T("停车/入场记录.csv 里，“地下一层”停车场一共进来过多少辆不同的车（按车牌算）？", 'result = len({r["车牌"] for r in R if r["停车场"] == "地下一层"})', "int",
                  ["head -3 " + p, "awk -F, 'NR>1 && NF && $%d==\"地下一层\"{print $%d}' %s | sort -u | wc -l" % (ci(h, "停车场"), ci(h, "车牌"), p)])])


@reg
def c34():
    cols = [("book_id", ID("B", 4, 1)), ("genre", C(["fantasy", "history", "mystery", "science", "poetry", "travel"], [14, 9, 18, 11, 4, 7])), ("title", F(lambda g, r: "Vol %d" % g.randint(1, 400))),
            ("copies", I(1, 9)), ("price", M(5, 80))]
    h, rows = gen_rows(32034, cols, 270)
    p = "library/catalog.csv"
    make("tab-32034", sub="topn", desc="Top 3 genres by total copies, not by number of titles",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["copies vs row count give different rankings"],
         turns=[T("library/catalog.csv 里，按 copies 列求和，馆藏册数最多的三个 genre 是哪三个？只要名字，从多到少。", top_sum("genre", "copies", 3), "names",
                  ["head -3 " + p, ref_top_sum(p, h, "genre", "copies", 3)])])
