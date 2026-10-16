"""Sub 2: group sum / mean (12 cases, 32013-32024)."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def awk_mean(path, h, col, conds, F=",", skip=1, dp=2, clean=None):
    cond = (" && " + cond_str(h, conds)) if conds else ""
    prog = "awk -F'%s' 'NR>%d && NF%s{s+=$%d;n++} END{printf \"%%.%df\\n\", s/n}'" % (F, skip, cond, ci(h, col), dp)
    return ("cat %s | %s | %s" % (path, clean, prog)) if clean else "%s %s" % (prog, path)


@reg
def c13():
    cols = [("订单号", ID("DD", 5, 40100)), ("区域", C(["华东", "华北", "华南", "西南", "东北"])), ("商品金额", M(30, 1200)), ("退款金额", F(lambda g, r: "0.00" if g.random() < 0.85 else r["商品金额"])),
            ("月份", C(["2026-07", "2026-08", "2026-09"]))]
    h, rows = gen_rows(32013, cols, 400)
    p = "销售/订单.csv"
    make("tab-32013", sub="group", desc="Sums goods amount for one region in a 400-row file where an adjacent column is refund amount",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["商品金额 vs 退款金额 adjacent"],
         turns=[T("销售/订单.csv 里华南区的商品金额一共是多少？保留两位小数。", 'result = sum(N(r["商品金额"]) for r in R if r["区域"] == "华南")', "num",
                  ["head -3 " + p, awk_sum(p, h, "商品金额", [("区域", "==", "华南")])], dp=2)])


@reg
def c14():
    cols = [("emp_id", ID("E", 4, 700)), ("dept", C(["eng", "ops", "sales", "hr", "legal"])), ("base_salary", M(6000, 38000, 0, True)), ("bonus", M(0, 9000, 0, True)),
            ("level", C(["L3", "L4", "L5", "L6"]))]
    h, rows = gen_rows(32014, cols, 240)
    p = "hr/salaries.csv"
    make("tab-32014", sub="group", desc="Average base salary for one department; salary values have thousands separators",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["quoted numbers like \"12,500\" break naive column splitting; base_salary vs bonus"],
         turns=[T("What is the average base_salary in the sales department in hr/salaries.csv? Round to 2 decimals.", 'rs = [N(r["base_salary"]) for r in R if r["dept"] == "sales"]\nresult = sum(rs) / len(rs)', "num",
                  ["head -4 " + p, awk_mean(p, h, "base_salary", [("dept", "==", "sales")], clean=SEDK)], dp=2)])


@reg
def c15():
    cols = [("日期", D(2026, 8, 9)), ("门店", C(["徐汇店", "静安店", "浦东店", "闵行店"])), ("品类", C(["饮品", "甜点", "轻食"])), ("销售额", M(200, 6000)), ("客单数", I(10, 140))]
    h, rows = gen_rows(32015, cols, 360)
    p = "门店/日销售.csv"
    make("tab-32015", sub="group", desc="Sum of sales for one store and category pair",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["销售额 vs 客单数: both numeric, order 销售额 first"],
         turns=[T("门店/日销售.csv 里，浦东店的甜点销售额合计多少？保留两位小数。", 'result = sum(N(r["销售额"]) for r in R if r["门店"] == "浦东店" and r["品类"] == "甜点")', "num",
                  ["head -3 " + p, awk_sum(p, h, "销售额", [("门店", "==", "浦东店"), ("品类", "==", "甜点")])], dp=2),
                T("闵行店的轻食呢？", 'result = sum(N(r["销售额"]) for r in R if r["门店"] == "闵行店" and r["品类"] == "轻食")', "num",
                  [awk_sum(p, h, "销售额", [("门店", "==", "闵行店"), ("品类", "==", "轻食")])], dp=2)])


@reg
def c16():
    cols = [("request_id", ID("r", 6, 100000)), ("endpoint", C(["/login", "/search", "/cart", "/pay", "/profile"])), ("status", C(["200", "200", "200", "404", "500"])),
            ("latency_ms", I(20, 1800)), ("bytes", I(300, 90000))]
    h, rows = gen_rows(32016, cols, 580)
    p = "access_summary.csv"
    make("tab-32016", sub="group", desc="Mean latency of one endpoint, restricted to status 200",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["latency_ms vs bytes; status column is text of digits"],
         turns=[T("In access_summary.csv, what is the mean latency_ms of successful (status 200) requests to /search? One decimal place.", 'rs = [N(r["latency_ms"]) for r in R if r["endpoint"] == "/search" and r["status"] == "200"]\nresult = sum(rs) / len(rs)', "num",
                  ["head -3 " + p, awk_mean(p, h, "latency_ms", [("endpoint", "==", "/search"), ("status", "==", "200")], dp=1)], dp=1)])


@reg
def c17():
    cols = [("流水号", ID("F", 6, 1)), ("日期", D(2026, 7, 9)), ("科目", C(["差旅", "餐饮", "办公", "培训", "招待"])), ("摘要", C(["打车, 机场", "团建, 火锅", "文具", "课程费", "客户晚宴, 外滩", "高铁票"])),
            ("金额", M(20, 4800, 2, True)), ("经办人", C(["林", "周", "黄", "何"]))]
    h, rows = gen_rows(32017, cols, 330)
    p = "财务/报销.csv"
    make("tab-32017", sub="group", desc="Sum of one expense category where summaries contain commas and amounts have thousands separators",
         traps=["TR-DELIM", "TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=5,
         notes_traps=["摘要 may be quoted with comma", "金额 may be quoted with thousands comma; two sed passes needed"],
         turns=[T("财务/报销.csv 里科目是“招待”的报销金额合计多少？保留两位小数。", 'result = sum(N(r["金额"]) for r in R if r["科目"] == "招待")', "num",
                  ["head -4 " + p, "cat %s | %s | awk -F, 'NR>1 && NF && $%d==\"招待\"{s+=$%d} END{printf \"%%.2f\\n\", s}'" % (p, CLEAN_ALL, ci(h, "科目"), ci(h, "金额"))], dp=2)])


@reg
def c18():
    cols = [("meter_id", C(["M-101", "M-102", "M-103", "M-104", "M-105", "M-106"])), ("reading_date", D(2026, 7, 9)), ("kwh", M(2, 60, 1)), ("peak_kwh", M(0, 20, 1)), ("tariff", C(["resi", "comm"], [70, 30]))]
    h, rows = gen_rows(32018, cols, 500)
    p = "energy/readings.tsv"
    make("tab-32018", sub="group", desc="Total kwh for one meter in a tab separated readings file that has kwh and peak_kwh",
         traps=["TR-DELIM"], path=p, header=h, rows=rows, delim="\t", ref_calls=3,
         notes_traps=["tab separated; kwh vs peak_kwh"],
         turns=[T("What is the total kwh for meter M-104 in energy/readings.tsv? Give it with 1 decimal.", 'result = sum(N(r["kwh"]) for r in R if r["meter_id"] == "M-104")', "num",
                  ["head -3 " + p, awk_sum(p, h, "kwh", [("meter_id", "==", "M-104")], F="\\t", dp=1)], dp=1),
                T("Same for M-102, but only the peak_kwh column.", 'result = sum(N(r["peak_kwh"]) for r in R if r["meter_id"] == "M-102")', "num",
                  [awk_sum(p, h, "peak_kwh", [("meter_id", "==", "M-102")], F="\\t", dp=1)], dp=1)])


@reg
def c19():
    cols = [("学号", ID("20260", 3, 101)), ("班级", C(["初三1班", "初三2班", "初三3班"])), ("语文", I(50, 148)), ("数学", I(40, 150)), ("英语", I(45, 148)), ("总分", F(lambda g, r: str(int(r["语文"]) + int(r["数学"]) + int(r["英语"]))))]
    h, rows = gen_rows(32019, cols, 210)
    p = "教务/月考.csv"
    make("tab-32019", sub="group", desc="Average of one subject for one class; 总分 column is a decoy for the mean",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["总分 is a derived column next to the subjects"],
         turns=[T("教务/月考.csv 里初三2班的数学平均分是多少？保留一位小数。", 'rs = [int(r["数学"]) for r in R if r["班级"] == "初三2班"]\nresult = sum(rs) / len(rs)', "num",
                  ["head -3 " + p, awk_mean(p, h, "数学", [("班级", "==", "初三2班")], dp=1)], dp=1)])


@reg
def c20():
    cols = [("txn", ID("P", 6, 880001)), ("merchant", C(["Cafe Nero", "Metro Mart", "Fuel Plus", "Book Barn", "Pizza Hub"])), ("amount", M(3, 220)), ("amount_refunded", F(lambda g, r: "0.00" if g.random() < 0.9 else "%.2f" % (float(r["amount"]) / 2))),
            ("card", C(["visa", "master", "union"]))]
    h, rows = gen_rows(32020, cols, 470)
    p = "bank/card_txn.csv"
    make("tab-32020", sub="group", desc="Sum of amount (not amount_refunded) for one merchant",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["amount vs amount_refunded; a grep-based sum would take both"],
         turns=[T("Total up the amount column for Metro Mart in bank/card_txn.csv. Two decimals please.", 'result = sum(N(r["amount"]) for r in R if r["merchant"] == "Metro Mart")', "num",
                  ["head -3 " + p, awk_sum(p, h, "amount", [("merchant", "==", "Metro Mart")])], dp=2),
                T("And how much of Metro Mart's amount was refunded in total?", 'result = sum(N(r["amount_refunded"]) for r in R if r["merchant"] == "Metro Mart")', "num",
                  [awk_sum(p, h, "amount_refunded", [("merchant", "==", "Metro Mart")])], dp=2)])


@reg
def c21():
    cols = [("工单", ID("W", 5, 2000)), ("车间", C(["一车间", "二车间", "三车间", "四车间"])), ("产量", I(80, 900)), ("不良数", I(0, 40)), ("班次", C(["早", "中", "晚"]))]
    h, rows = gen_rows(32021, cols, 390)
    p = "生产/日报.csv"
    make("tab-32021", sub="group", desc="Total output of one workshop and shift in a file with a note line and empty trailing lines",
         traps=["TR-HEADER"], path=p, header=h, rows=rows, preamble=["# 生产日报汇总导出（勿手工修改）"], trail=3, ref_calls=4,
         notes_traps=["first line is a # comment; empty lines at end"],
         turns=[T("生产/日报.csv 里三车间晚班的产量一共多少？", 'result = sum(int(r["产量"]) for r in R if r["车间"] == "三车间" and r["班次"] == "晚")', "int",
                  ["head -3 " + p, "awk -F, 'NR>2 && NF && $%d==\"三车间\" && $%d==\"晚\"{s+=$%d} END{print s+0}' %s" % (ci(h, "车间"), ci(h, "班次"), ci(h, "产量"), p)])])


@reg
def c22():
    cols = [("campaign", C(["spring_a", "spring_b", "summer_a", "summer_b", "autumn_a"])), ("day", D(2026, 8, 9)), ("impressions", M(1000, 90000, 0, True)), ("clicks", I(20, 2500)), ("spend", M(50, 3000))]
    h, rows = gen_rows(32022, cols, 310)
    p = "ads/daily.csv"
    make("tab-32022", sub="group", desc="Click-through-style mean: average spend per row for one campaign with quoted impressions",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["impressions quoted with thousands comma shifts clicks and spend"],
         turns=[T("In ads/daily.csv, what is the average daily spend of campaign summer_b? Two decimals.", 'rs = [N(r["spend"]) for r in R if r["campaign"] == "summer_b"]\nresult = sum(rs) / len(rs)', "num",
                  ["head -4 " + p, awk_mean(p, h, "spend", [("campaign", "==", "summer_b")], clean=SEDK)], dp=2)])


@reg
def c23():
    cols = [("order", ID("A", 5, 9100)), ("city", C(["杭州", "宁波", "温州", "嘉兴"])), ("weight_kg", M(0.5, 60, 1)), ("freight", M(6, 220)), ("express", C(["标准", "加急"], [75, 25]))]
    h, rows = gen_rows(32023, cols, 360)
    p = "物流/运费.csv"
    make("tab-32023", sub="group", desc="Total freight for one city and service level, second turn another city",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["freight vs weight_kg; 加急 is a value not a column"],
         turns=[T("物流/运费.csv 里发往宁波的加急件，运费合计是多少？两位小数。", 'result = sum(N(r["freight"]) for r in R if r["city"] == "宁波" and r["express"] == "加急")', "num",
                  ["head -3 " + p, awk_sum(p, h, "freight", [("city", "==", "宁波"), ("express", "==", "加急")])], dp=2),
                T("温州的标准件平均每单运费呢？两位小数。", 'rs = [N(r["freight"]) for r in R if r["city"] == "温州" and r["express"] == "标准"]\nresult = sum(rs) / len(rs)', "num",
                  [awk_mean(p, h, "freight", [("city", "==", "温州"), ("express", "==", "标准")])], dp=2)])


@reg
def c24():
    cols = [("sample_id", ID("S", 4, 1)), ("lab", C(["north", "south", "east"])), ("ph", M(5.5, 8.5)), ("turbidity", M(0.1, 12)), ("tested_on", D(2026, 8, 9))]
    h, rows = gen_rows(32024, cols, 280)
    p = "water/samples.csv"
    make("tab-32024", sub="group", desc="Mean pH of one lab with trailing empty lines in the file",
         traps=["TR-HEADER"], path=p, header=h, rows=rows, trail=2, ref_calls=3,
         notes_traps=["file ends with two empty lines; a naive row count divides by the wrong n"],
         turns=[T("water/samples.csv 里 east 实验室所有样品的 ph 平均值是多少？保留两位小数。", 'rs = [N(r["ph"]) for r in R if r["lab"] == "east"]\nresult = sum(rs) / len(rs)', "num",
                  ["head -3 " + p, awk_mean(p, h, "ph", [("lab", "==", "east")])], dp=2)])
