"""Sub 4: multi-condition filters (8 cases, 32035-32042)."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


def awk_line(p, expr, body, F=",", skip=1, end="print n+0", pre=None):
    prog = "awk -F'%s' 'NR>%d && NF && %s{%s} END{%s}'" % (F, skip, expr, body, end)
    return ("cat %s | %s | %s" % (p, pre, prog)) if pre else "%s %s" % (prog, p)


@reg
def c35():
    cols = [("订单号", ID("DD", 5, 61000)), ("区域", C(["华东", "华北", "华南", "西南"], [40, 20, 20, 20])), ("下单日期", D(2026, 7, 9)), ("订单金额", M(30, 1500)), ("退款状态", C(["无", "部分退款", "已退款"], [60, 15, 25])),
            ("渠道", C(["App", "小程序", "网页"]))]
    h, rows = gen_rows(32035, cols, 600)
    p = "电商/订单_q3.csv"
    r, d, s = ci(h, "区域"), ci(h, "下单日期"), ci(h, "退款状态")
    make("tab-32035", sub="multi", desc="Counts east-china September refunded orders, then sums their amount",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["month lives inside a date column; 退款状态 has 部分退款 and 已退款"],
         turns=[T("电商/订单_q3.csv 里，华东区、9 月下的单、并且退款状态是“已退款”的订单有多少单？", 'result = sum(1 for r in R if r["区域"] == "华东" and r["下单日期"].startswith("2026-09") and r["退款状态"] == "已退款")', "int",
                  ["head -3 " + p, awk_line(p, '$%d=="华东" && substr($%d,1,7)=="2026-09" && $%d=="已退款"' % (r, d, s), "n++")]),
                T("这些单的订单金额合计是多少？两位小数。", 'result = sum(N(r["订单金额"]) for r in R if r["区域"] == "华东" and r["下单日期"].startswith("2026-09") and r["退款状态"] == "已退款")', "num",
                  [awk_line(p, '$%d=="华东" && substr($%d,1,7)=="2026-09" && $%d=="已退款"' % (r, d, s), "s+=$%d" % ci(h, "订单金额"), end='printf "%.2f\\n", s')], dp=2)])


@reg
def c36():
    cols = [("ticket", ID("T", 5, 3000)), ("queue", C(["billing", "tech", "sales", "abuse"])), ("priority", C(["low", "normal", "high", "urgent"], [30, 40, 20, 10])),
            ("opened", D(2026, 8, 9)), ("hours_to_resolve", M(0.5, 96, 1)), ("channel", C(["email", "chat", "phone"]))]
    h, rows = gen_rows(32036, cols, 480)
    p = "support/tickets.csv"
    make("tab-32036", sub="multi", desc="Counts tech-queue high or urgent tickets resolved slowly",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["or-condition on priority combined with and-conditions"],
         turns=[T("In support/tickets.csv, how many tickets in the tech queue were high or urgent priority and took more than 48 hours to resolve?", 'result = sum(1 for r in R if r["queue"] == "tech" and r["priority"] in ("high", "urgent") and N(r["hours_to_resolve"]) > 48)', "int",
                  ["head -3 " + p, awk_line(p, '$%d=="tech" && ($%d=="high" || $%d=="urgent") && $%d>48' % (ci(h, "queue"), ci(h, "priority"), ci(h, "priority"), ci(h, "hours_to_resolve")), "n++")])])


@reg
def c37():
    cols = [("编号", ID("C", 4, 1)), ("学院", C(["理学院", "工学院", "商学院", "文学院"])), ("性别", C(["男", "女"])), ("身高cm", I(150, 195)), ("体重kg", M(42, 98, 1)), ("体测等级", C(["优秀", "良好", "及格", "不及格"], [10, 30, 30, 30]))]
    h, rows = gen_rows(32037, cols, 600)
    p = "体测/2026春.csv"
    make("tab-32037", sub="multi", desc="Counts women in one college who failed and are above a height",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["header 身高cm / 体重kg include units; 不及格 contains 及格"],
         turns=[T("体测/2026春.csv 里，工学院、女生、体测等级是“不及格”、身高超过 160 的有多少人？注意“不及格”和“及格”是两个不同的等级。", 'result = sum(1 for r in R if r["学院"] == "工学院" and r["性别"] == "女" and r["体测等级"] == "不及格" and int(r["身高cm"]) > 160)', "int",
                  ["head -3 " + p, awk_line(p, '$%d=="工学院" && $%d=="女" && $%d=="不及格" && $%d>160' % (ci(h, "学院"), ci(h, "性别"), ci(h, "体测等级"), ci(h, "身高cm")), "n++")])])


@reg
def c38():
    cols = [("id", ID("o", 5, 1)), ("date", D(2026, 7, 9, "%m/%d/%Y")), ("store", C(["N1", "N2", "S1", "S2", "W1"])), ("total", M(8, 480, 2, True)), ("payment", C(["cash", "card", "app"])), ("discount", C(["none", "member", "coupon"], [60, 25, 15]))]
    h, rows = gen_rows(32038, cols, 440)
    p = "pos/receipts.csv"
    make("tab-32038", sub="multi", desc="Sum of totals for August app payments with a coupon, dates written month/day/year and totals quoted",
         traps=["TR-DATEFMT", "TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=5,
         notes_traps=["dates are MM/DD/YYYY so the month is the first field", "total can be quoted with thousands comma"],
         turns=[T("Add up total in pos/receipts.csv for August receipts paid with the app and discounted by coupon. Two decimals.", 'result = sum(N(r["total"]) for r in R if r["date"].startswith("08/") and r["payment"] == "app" and r["discount"] == "coupon")', "num",
                  ["head -4 " + p, awk_line(p, 'substr($%d,1,2)=="08" && $%d=="app" && $%d=="coupon"' % (ci(h, "date"), ci(h, "payment"), ci(h, "discount")), "s+=$%d" % ci(h, "total"), end='printf "%.2f\\n", s', pre=SEDK)], dp=2)])


@reg
def c39():
    cols = [("flight", F(lambda g, r: "%s%d" % (g.choice(["MU", "CA", "CZ"]), g.randint(1000, 9999)))), ("date", D(2026, 8, 9)), ("origin", C(["PVG", "PEK", "CAN", "CTU"])), ("dest", C(["PVG", "PEK", "CAN", "CTU"])),
            ("delay_min", I(0, 240)), ("pax", I(80, 320))]
    h, rows = gen_rows(32039, cols, 590)
    rows = [r for r in rows if r[2] != r[3]]
    p = "air/flights.csv"
    make("tab-32039", sub="multi", desc="Counts delayed flights on one route and the passenger total of those flights",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["origin and dest use the same codes; PVG->PEK differs from PEK->PVG"],
         turns=[T("In air/flights.csv, how many flights from PVG to PEK were delayed by more than 60 minutes?", 'result = sum(1 for r in R if r["origin"] == "PVG" and r["dest"] == "PEK" and int(r["delay_min"]) > 60)', "int",
                  ["head -3 " + p, awk_line(p, '$%d=="PVG" && $%d=="PEK" && $%d>60' % (ci(h, "origin"), ci(h, "dest"), ci(h, "delay_min")), "n++")]),
                T("What is the combined pax on those delayed flights?", 'result = sum(int(r["pax"]) for r in R if r["origin"] == "PVG" and r["dest"] == "PEK" and int(r["delay_min"]) > 60)', "int",
                  [awk_line(p, '$%d=="PVG" && $%d=="PEK" && $%d>60' % (ci(h, "origin"), ci(h, "dest"), ci(h, "delay_min")), "s+=$%d" % ci(h, "pax"), end="print s+0")])])


@reg
def c40():
    cols = [("工号", ID("G", 4, 100)), ("姓名", C(["杜明", "江河", "秦岚", "石磊", "韩雪", "于洋", "邱凯", "彭飞"])), ("部门", C(["研发", "测试", "产品", "运维"])), ("请假类型", C(["年假", "病假", "事假", "调休"], [35, 20, 20, 25])),
            ("天数", M(0.5, 7, 1)), ("开始日期", D(2026, 5, 9))]
    h, rows = gen_rows(32040, cols, 360)
    p = "人事/请假.csv"
    make("tab-32040", sub="multi", desc="Sums sick leave days for one department in or after July",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, trail=1, ref_calls=4,
         notes_traps=["month filter ≥ 07 over a date column; fractional days; one trailing empty line"],
         turns=[T("人事/请假.csv 里，研发部 7 月及以后开始的病假一共请了多少天？保留一位小数。", 'result = sum(N(r["天数"]) for r in R if r["部门"] == "研发" and r["请假类型"] == "病假" and r["开始日期"] >= "2026-07-01")', "num",
                  ["head -3 " + p, awk_line(p, '$%d=="研发" && $%d=="病假" && $%d>="2026-07-01"' % (ci(h, "部门"), ci(h, "请假类型"), ci(h, "开始日期")), "s+=$%d" % ci(h, "天数"), end='printf "%.1f\\n", s')], dp=1)])


@reg
def c41():
    cols = [("run", ID("R", 4, 1)), ("model", C(["base", "lora-a", "lora-b", "full-ft"])), ("dataset", C(["news", "code", "chat", "math"])), ("seed", I(1, 5)), ("acc", M(0.3, 0.95, 3)), ("train_hours", M(0.5, 30, 1))]
    h, rows = gen_rows(32041, cols, 300)
    p = "ml/experiments.csv"
    make("tab-32041", sub="multi", desc="Mean accuracy for one model on one dataset with at least 3 seeds filter, three decimals",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["acc vs train_hours; seed filter is numeric"],
         turns=[T("In ml/experiments.csv, what is the mean acc of lora-b runs on the code dataset with seed 3 or higher? Three decimals.", 'rs = [N(r["acc"]) for r in R if r["model"] == "lora-b" and r["dataset"] == "code" and int(r["seed"]) >= 3]\nresult = sum(rs) / len(rs)', "num",
                  ["head -3 " + p, "awk -F, 'NR>1 && NF && $%d==\"lora-b\" && $%d==\"code\" && $%d>=3{s+=$%d;n++} END{printf \"%%.3f\\n\", s/n}' %s" % (ci(h, "model"), ci(h, "dataset"), ci(h, "seed"), ci(h, "acc"), p)], dp=3)])


@reg
def c42():
    cols = [("单号", ID("PO", 5, 7700)), ("供应商", C(["恒达", "鑫源", "同创", "宏远", "瑞丰"])), ("物料", C(["螺丝", "轴承", "线缆", "外壳", "电容"], [15, 35, 20, 15, 15])), ("数量", M(100, 20000, 0, True)),
            ("单价", M(0.2, 30)), ("交付状态", C(["已交付", "延期", "待交付"], [50, 30, 20]))]
    h, rows = gen_rows(32042, cols, 600)
    p = "采购/订单.csv"
    make("tab-32042", sub="multi", desc="Counts delayed bearing orders over 3000 pieces; 数量 quoted with thousands separators, then another supplier",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["数量 uses thousands separators and is quoted; 单价 follows it"],
         turns=[T("采购/订单.csv 里，物料是轴承、数量超过 3000、交付状态是“延期”的订单有多少个？", 'result = sum(1 for r in R if r["物料"] == "轴承" and N(r["数量"]) > 3000 and r["交付状态"] == "延期")', "int",
                  ["head -4 " + p, awk_line(p, '$%d=="轴承" && $%d>3000 && $%d=="延期"' % (ci(h, "物料"), ci(h, "数量"), ci(h, "交付状态")), "n++", pre=SEDK)]),
                T("同样条件，只看供应商恒达的呢？", 'result = sum(1 for r in R if r["物料"] == "轴承" and N(r["数量"]) > 3000 and r["交付状态"] == "延期" and r["供应商"] == "恒达")', "int",
                  [awk_line(p, '$%d=="轴承" && $%d>3000 && $%d=="延期" && $%d=="恒达"' % (ci(h, "物料"), ci(h, "数量"), ci(h, "交付状态"), ci(h, "供应商")), "n++", pre=SEDK)])])
