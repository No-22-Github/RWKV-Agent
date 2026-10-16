"""Sub 1: count by condition (12 cases, 32001-32012)."""
from common import *

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c1():
    cols = [("订单号", ID("DD", 5, 20100)), ("下单日期", D(2026, 7, 9)), ("实付金额", M(20, 900)), ("退款金额", F(lambda g, r: "0.00" if g.random() < 0.8 else "%.2f" % (float(r["实付金额"]) * g.choice([0.3, 0.5, 1]) ))),
            ("区域", C(["华东", "华北", "华南", "西南"])), ("状态", C(["已完成", "已退款", "待发货", "已取消"], [60, 12, 15, 13]))]
    h, rows = gen_rows(32001, cols, 380)
    s, rf = ci(h, "状态"), ci(h, "退款金额")
    make("tab-32001", sub="count", desc="Counts refunded orders in a 380-row order export with similarly named amount columns",
         traps=["TR-DECOY"], path="data/订单明细.csv", header=h, rows=rows, ref_calls=3,
         notes_traps=["实付金额/退款金额 adjacent columns; 状态 is column 6, not 5"],
         turns=[T("data/订单明细.csv 是三季度的订单导出。状态是“已退款”的订单一共有多少单？", 'result = sum(1 for r in R if r["状态"] == "已退款")', "int",
                  ["head -3 data/订单明细.csv", "awk -F, -v c=%d 'NR>1 && $c==\"已退款\"{n++} END{print n+0}' data/订单明细.csv" % s])])


@reg
def c2():
    cols = [("ticket_id", ID("TK-", 4, 1001)), ("opened", D(2026, 6, 9)), ("priority", C(["P1", "P2", "P3"], [30, 35, 35])), ("assignee", C(["lin", "omar", "dana", "kofi", "wei"])),
            ("status", C(["open", "closed", "pending"], [25, 55, 20])), ("status_note", C(["", "waiting on customer", "escalated", "duplicate of earlier"], [55, 20, 15, 10]))]
    h, rows = gen_rows(32002, cols, 400)
    make("tab-32002", sub="count", desc="Counts open tickets where status_note also looks like a status",
         traps=["TR-DECOY"], path="exports/tickets_q3.csv", header=h, rows=rows, ref_calls=3,
         notes_traps=["status vs status_note: grep for 'open' would also hit nothing wrong but column choice matters for 'escalated'"],
         turns=[T("In exports/tickets_q3.csv, how many P1 tickets are still open?", 'result = sum(1 for r in R if r["priority"] == "P1" and r["status"] == "open")', "int",
                  ["head -3 exports/tickets_q3.csv", "awk -F, -v p=%d -v s=%d 'NR>1 && $p==\"P1\" && $s==\"open\"{n++} END{print n+0}' exports/tickets_q3.csv" % (ci(h, "priority"), ci(h, "status"))])])


@reg
def c3():
    cols = [("工号", ID("E", 4, 3001)), ("姓名", C(["张伟", "李娜", "王强", "刘洋", "陈静", "杨帆", "赵磊", "周敏", "吴昊", "郑凯"])), ("部门", C(["研发", "市场", "财务", "客服", "运营"])),
            ("入职地点", C(["上海, 浦东", "北京, 海淀", "深圳, 南山", "成都, 高新", "杭州, 滨江"])), ("迟到次数", I(0, 9)), ("月份", C(["2026-07", "2026-08", "2026-09"]))]
    h, rows = gen_rows(32003, cols, 300)
    m = ci(h, "月份")
    make("tab-32003", sub="count", desc="Counts late-arrival rows in a month where a quoted field contains a comma",
         traps=["TR-DELIM"], path="hr/考勤月报.csv", header=h, rows=rows, ref_calls=4,
         notes_traps=["入职地点 is quoted and contains a comma, shifting naive awk columns after it"],
         turns=[T("hr/考勤月报.csv 里，2026-09 这个月迟到次数大于等于 5 的记录有多少条？", 'result = sum(1 for r in R if r["月份"] == "2026-09" and int(r["迟到次数"]) >= 5)', "int",
                  ["head -4 hr/考勤月报.csv", "sed -E 's/\"[^\",]*,[^\"]*\"/Q/g' hr/考勤月报.csv | awk -F, 'NR>1 && $6==\"2026-09\" && $5>=5{n++} END{print n+0}'"])])


@reg
def c4():
    cols = [("trip_id", ID("T", 5, 70001)), ("pickup_date", D(2026, 7, 9)), ("distance_km", M(1, 40, 1)), ("fare_cny", M(8, 160)), ("payment", C(["wechat", "alipay", "cash", "card"], [40, 35, 15, 10])),
            ("tip_cny", F(lambda g, r: "%.2f" % (g.choice([0, 0, 0, 2, 5, 10]))))]
    h, rows = gen_rows(32004, cols, 450)
    p = "logs/taxi_trips.tsv"
    make("tab-32004", sub="count", desc="Counts card-paid trips with a tip in a 450-row tab separated trip file",
         traps=["TR-DELIM"], path=p, header=h, rows=rows, delim="\t", ref_calls=3,
         notes_traps=["file is tab separated; awk -F, finds one column"],
         turns=[T("How many trips in logs/taxi_trips.tsv were paid by card and got a tip above 0?", 'result = sum(1 for r in R if r["payment"] == "card" and N(r["tip_cny"]) > 0)', "int",
                  ["head -3 " + p, awk_count(p, h, [("payment", "==", "card"), ("tip_cny", ">", 0)], F="\\t")])])


@reg
def c5():
    cols = [("借阅号", ID("L", 5, 8000)), ("读者", C(["赵一", "钱二", "孙三", "李四", "周五", "吴六", "郑七", "王八", "冯九", "陈十"])), ("书名", C(["三体", "活着", "百年孤独", "围城", "平凡的世界", "解忧杂货店", "人类简史", "额尔古纳河右岸"])),
            ("借出日", D(2026, 6, 9)), ("应还日", D(2026, 7, 10)), ("状态", C(["已还", "未还", "逾期未还"], [60, 15, 25]))]
    h, rows = gen_rows(32005, cols, 340)
    p = "图书馆/借阅记录.csv"
    make("tab-32005", sub="count", desc="Counts overdue loans where one status value contains another",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["状态 value 逾期未还 contains 未还; grep 未还 over-counts"],
         turns=[T("图书馆/借阅记录.csv 里“未还”的记录有多少条？注意只算状态正好是“未还”的，“逾期未还”是另一种情况，不算在内。", 'result = sum(1 for r in R if r["状态"] == "未还")', "int",
                  ["head -3 " + p, awk_count(p, h, [("状态", "==", "未还")])]),
                T("那“逾期未还”的呢？", 'result = sum(1 for r in R if r["状态"] == "逾期未还")', "int",
                  [awk_count(p, h, [("状态", "==", "逾期未还")])])])


@reg
def c6():
    cols = [("sku", ID("SKU-", 4, 500)), ("warehouse", C(["SH-01", "SH-02", "BJ-01", "GZ-01"])), ("on_hand", I(0, 400)), ("reorder_level", I(20, 120)), ("category", C(["cable", "adapter", "charger", "case", "stand"]))]
    h, rows = gen_rows(32006, cols, 320)
    p = "stock/inventory_0916.csv"
    make("tab-32006", sub="count", desc="Counts SKUs below reorder level in one warehouse (comparison of two columns)",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["on_hand vs reorder_level columns adjacent and both numeric"],
         turns=[T("In stock/inventory_0916.csv, for warehouse SH-02, how many SKUs have on_hand below their reorder_level?", 'result = sum(1 for r in R if r["warehouse"] == "SH-02" and int(r["on_hand"]) < int(r["reorder_level"]))', "int",
                  ["head -3 " + p, "awk -F, 'NR>1 && NF && $%d==\"SH-02\" && $%d<$%d{n++} END{print n+0}' %s" % (ci(h, "warehouse"), ci(h, "on_hand"), ci(h, "reorder_level"), p)])])


@reg
def c7():
    cols = [("order_no", ID("SO", 5, 31000)), ("customer", C(["Acme Retail", "Blue Harbor", "Cedar & Co", "Delta Foods", "Evergreen", "Fjord Labs"])), ("order_total", M(300, 25000, 2, True)),
            ("region", C(["East", "West", "North", "South"])), ("order_date", D(2026, 7, 9))]
    h, rows = gen_rows(32007, cols, 280)
    p = "sales/orders_h2.csv"
    make("tab-32007", sub="count", desc="Counts orders above 10000 where totals carry thousands separators and are quoted",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["order_total like \"12,345.60\" is quoted; naive awk reads 12 and shifts later columns"],
         turns=[T("How many orders in sales/orders_h2.csv have an order_total over 10000?", 'result = sum(1 for r in R if N(r["order_total"]) > 10000)', "int",
                  ["head -4 " + p, "cat %s | %s | awk -F, 'NR>1 && NF && $%d>10000{n++} END{print n+0}'" % (p, SEDK, ci(h, "order_total"))])])


@reg
def c8():
    cols = [("编号", ID("S", 4, 1)), ("日期", D(2026, 8, 9)), ("设备", C(["A-01", "A-02", "B-07", "B-08", "C-11"])), ("温度", M(18, 42, 1)), ("告警", C(["无", "高温", "断线"], [80, 15, 5]))]
    h, rows = gen_rows(32008, cols, 420)
    p = "监控/温度采样.csv"
    make("tab-32008", sub="count", desc="Counts alert rows in a file with a comment line above the header and trailing empty lines",
         traps=["TR-HEADER"], path=p, header=h, rows=rows, preamble=["# 导出时间 2026-09-15 23:40 来源 monitor-db"], trail=2, ref_calls=4,
         notes_traps=["line 1 is a comment, the real header is line 2; file ends with empty lines"],
         turns=[T("监控/温度采样.csv 里告警为“高温”的采样点有多少个？", 'result = sum(1 for r in R if r["告警"] == "高温")', "int",
                  ["head -3 " + p, awk_count(p, h, [("告警", "==", "高温")], skip=2)])])


@reg
def c9():
    cols = [("id", ID("U", 5, 100)), ("signup", D(2026, 5, 9)), ("plan", C(["free", "basic", "pro", "team"], [35, 25, 22, 18])), ("country", C(["CN", "US", "DE", "JP", "BR", "IN"])),
            ("churned", C(["yes", "no"], [22, 78]))]
    h, rows = gen_rows(32009, cols, 600)
    p = "users.csv"
    make("tab-32009", sub="count", desc="Counts churned paying users in a 520-row export, then a second plan",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["plan column holds free as well; 'paying' means not free"],
         turns=[T("In users.csv, how many users on the pro plan have churned?", 'result = sum(1 for r in R if r["plan"] == "pro" and r["churned"] == "yes")', "int",
                  ["head -3 " + p, awk_count(p, h, [("plan", "==", "pro"), ("churned", "==", "yes")])]),
                T("And how many churned users are on the team plan?", 'result = sum(1 for r in R if r["plan"] == "team" and r["churned"] == "yes")', "int",
                  [awk_count(p, h, [("plan", "==", "team"), ("churned", "==", "yes")])])])


@reg
def c10():
    cols = [("考号", ID("K", 4, 2001)), ("班级", C(["高二(1)班", "高二(2)班", "高二(3)班", "高二(4)班"])), ("语文", I(40, 150)), ("数学", I(30, 150)), ("英语", I(40, 150)), ("备注", C(["", "", "", "转学生", "借读"]))]
    h, rows = gen_rows(32010, cols, 420)
    p = "成绩/期中.csv"
    make("tab-32010", sub="count", desc="Counts students above 120 in math within one class; column order differs from subject order habit",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["subject columns 语文,数学,英语 adjacent; a guess of 数学 as column 3 is wrong"],
         turns=[T("成绩/期中.csv 里，高二(3)班数学成绩超过 120 分的有多少人？", 'result = sum(1 for r in R if r["班级"] == "高二(3)班" and int(r["数学"]) > 120)', "int",
                  ["head -3 " + p, awk_count(p, h, [("班级", "==", "高二(3)班"), ("数学", ">", 120)])]),
                T("英语超过 120 的呢（同样只看高二(3)班）？", 'result = sum(1 for r in R if r["班级"] == "高二(3)班" and int(r["英语"]) > 120)', "int",
                  [awk_count(p, h, [("班级", "==", "高二(3)班"), ("英语", ">", 120)])])])


@reg
def c11():
    cols = [("shipment", ID("SH", 5, 4400)), ("carrier", C(["SF", "ZTO", "YTO", "JD", "EMS"])), ("dest", C(["Beijing", "Shanghai", "Chengdu", "Wuhan", "Xian"])),
            ("days", I(1, 9)), ("weight_kg", M(0.2, 30, 1)), ("signed", C(["Y", "N"], [93, 7]))]
    h, rows = gen_rows(32011, cols, 600)
    p = "ship/deliveries.csv"
    make("tab-32011", sub="count", desc="Counts slow deliveries by one carrier in a 600-row delivery file",
         traps=["TR-DECOY"], path=p, header=h, rows=rows, ref_calls=3,
         notes_traps=["days vs weight_kg; ZTO vs YTO look alike"],
         turns=[T("ship/deliveries.csv 里，ZTO 的快件有多少单花了 5 天或更久才送到？", 'result = sum(1 for r in R if r["carrier"] == "ZTO" and int(r["days"]) >= 5)', "int",
                  ["head -3 " + p, awk_count(p, h, [("carrier", "==", "ZTO"), ("days", ">=", 5)])])])


@reg
def c12():
    cols = [("会员号", ID("M", 5, 60000)), ("昵称", C(["小鹿", "阿杰", "木子", "老K", "团团", "Lily", "大壮"])), ("积分", M(0, 20000, 0, True)), ("等级", C(["银卡", "金卡", "白金"], [60, 30, 10])),
            ("最近消费", D(2026, 5, 9))]
    h, rows = gen_rows(32012, cols, 360)
    p = "crm/会员.csv"
    make("tab-32012", sub="count", desc="Counts members whose points exceed 5000 when points use thousands separators",
         traps=["TR-NUMFMT"], path=p, header=h, rows=rows, ref_calls=4,
         notes_traps=["积分 like \"12,345\" quoted with comma"],
         turns=[T("crm/会员.csv 里积分超过 5000 的会员有多少个？", 'result = sum(1 for r in R if N(r["积分"]) > 5000)', "int",
                  ["head -4 " + p, "cat %s | %s | awk -F, 'NR>1 && NF && $%d>5000{n++} END{print n+0}'" % (p, SEDK, ci(h, "积分"))]),
                T("其中白金会员有多少个？", 'result = sum(1 for r in R if N(r["积分"]) > 5000 and r["等级"] == "白金")', "int",
                  ["cat %s | %s | awk -F, 'NR>1 && NF && $%d>5000 && $%d==\"白金\"{n++} END{print n+0}'" % (p, SEDK, ci(h, "积分"), ci(h, "等级"))])])
