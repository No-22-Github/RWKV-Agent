"""local-file combos part 1: itinerary -> weather, contract date -> days, bill -> calculation + result file."""
from common import mk, weather, L, WEBX

B = []


def b(f):
    B.append(f)
    return f


SUZHOU = [weather("苏州", "多云 25°C 体感 26°C 湿度 70% 风速 8 km/h",
                  [("2026-09-16", "多云", "22~28", "20%"), ("2026-09-17", "阴", "21~27", "35%"),
                   ("2026-09-18", "中雨", "20~24", "75%"), ("2026-09-19", "小雨", "19~23", "55%"), ("2026-09-20", "多云", "19~26", "20%")])]


@b
def f01():
    files = {"出差/行程.md": L("# 九月出差", "", "- 上一次出差：北京（8 月）", "- 本次目的地：苏州", "- 出发日期：2026-09-18", "- 返程：2026-09-20"),
             "出差/报销说明.md": L("# 报销说明", "", "出差票据请在返程后一周内提交。")}

    def compute(files, wx):
        d = [x for x in wx[0]["report"]["daily"] if x["date"] == "2026-09-18"][0]
        return {}, [[("all", [d["rain_chance"]])]]
    mk("hyb-33657", sub="files", task="local_first", desc="Read the itinerary file for city and date, then fetch that day's forecast", files=files, wx=SUZHOU,
       turns=[{"p": "看一下出差文件夹里的行程，出发那天目的地的天气怎么样？", "req": ["read_file", "get_weather"], "forb": WEBX}],
       compute=compute, must=["read_file", "list_files", "get_weather"], traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": "20%"}, rc=3,
       notes="1. list_files / read_file 出差/行程.md -> destination 苏州, departure 2026-09-18\n2. get_weather 苏州 days>=3\nAnswer: 09-18 中雨, 75%. Decoys: the previous trip city 北京, today's 20%.",
       alts=["行程里的目的地出发当天天气如何", "我出发那天去的城市会下雨吗", "按出差行程查目的地出发日的天气", "出差文件夹行程中目的地，出发日天气预报", "Check the destination weather on the departure day in my trip notes"])


@b
def f02():
    files = {"plan/trip.md": L("# 周末短途", "", "周五：在家加班", "周六：去苏州拙政园", "周日：返回上海")}

    def compute(files, wx):
        d = [x for x in wx[0]["report"]["daily"] if x["date"] == "2026-09-19"][0]
        return {}, [[("all", ["苏州"])], [("all", [d["rain_chance"]])]]
    mk("hyb-33658", sub="files", task="multi_turn", desc="Multi-turn: read the plan for Saturday's destination, then weather for that Saturday", files=files, wx=SUZHOU,
       turns=[{"p": "plan 文件夹里的周末安排，我周六要去哪个城市？", "req": ["read_file"]},
              {"p": "那边周六天气怎么样，要带伞吗？"}],
       compute=compute, must=["read_file", "get_weather"], traps=["TR-DECOY"], decoys={"TR-DECOY": "20%"}, rc=3,
       notes="Turn1: 苏州 (from the file). Turn2: get_weather 苏州 with days>=4 -> 09-19 小雨 55%.",
       alts=["周末计划里周六的目的地是哪", "我周六去哪个城市（看 plan/trip.md）", "周六目的地城市", "安排里周六去的地方在哪个城市", "Which city am I visiting on Saturday per plan/trip.md?"])


@b
def f03():
    files = {"trip/plan.md": L("# 出行", "", "目的地：苏州", "出发：2026-09-18（后天）"), "trip/notes.md": L("# 备忘", "", "记得带充电宝。")}

    def compute(files, wx):
        d = [x for x in wx[0]["report"]["daily"] if x["date"] == "2026-09-18"][0]
        assert int(d["rain_chance"].rstrip("%")) >= 50
        return {"trip/packing.md": ["伞"]}, [[("all", [d["rain_chance"]])], []]
    mk("hyb-33659", sub="files", task="tool_then_write", desc="Read the plan, check the forecast, then write a packing list that mentions an umbrella", files=files, wx=SUZHOU,
       turns=[{"p": "trip/plan.md 里的行程，出发那天目的地天气怎样？", "req": ["read_file", "get_weather"]},
              {"p": "根据这个天气，在 trip 文件夹里新建 packing.md，列一份带什么东西的清单。", "tools": None}],
       compute=compute, must=["read_file", "get_weather", "write_file"], traps=["TR-DECOY"], decoys={"TR-DECOY": "20%"}, rc=3,
       notes="Turn1: 75% rain on 09-18. Turn2: write trip/packing.md; since rain is likely it must mention 伞. Staged writes are fine.",
       alts=["看 trip/plan.md，出发日目的地的天气", "出发那天的目的地天气（计划文件里有）", "计划里的目的地后天天气预报", "按 trip/plan.md 查天气", "Weather at the destination in trip/plan.md on departure day?"])


@b
def f04():
    files = {"合同/租赁合同.md": L("# 办公室租赁合同", "", "签订日期：2025-02-01", "起租日期：2025-02-15", "到期日期：2027-01-31", "月租金：18600 元"),
             "合同/备忘.md": L("续约谈判请在到期前两个月启动。")}

    def compute(files, wx):
        import datetime
        n = (datetime.date(2027, 1, 31) - datetime.date(2026, 9, 16)).days
        return {}, [[("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])]]
    mk("hyb-33660", sub="files", task="local_first", desc="Days from today to the lease expiry date stored in a contract file", files=files,
       turns=[{"p": "合同文件夹里的租赁合同，离到期还有多少天？", "req": ["read_file", "datetime"]}],
       compute=compute, must=["read_file", "list_files", "datetime", "calculator"], traps=["TR-DECOY"], decoys={"TR-DECOY": "2025-02-01"}, rc=3,
       notes="Read 合同/租赁合同.md: 到期日期 2027-01-31 (not 签订日期 or 起租日期). 09-16 -> 2027-01-31 = 137 days.",
       alts=["租赁合同还有多少天到期", "距离租约到期日剩几天", "合同什么时候到期，还剩多少天", "到期日期到今天还有几天", "How many days remain on the lease in 合同/租赁合同.md?"])


@b
def f05():
    files = {"合同/服务协议.md": L("# 软件服务协议", "", "生效日期：2026-03-01", "终止日期：2026-12-31", "续约通知期：终止日前 45 天")}

    def compute(files, wx):
        import datetime
        e = datetime.date(2026, 12, 31)
        n = (e - datetime.date(2026, 9, 16)).days
        d = e - datetime.timedelta(days=45)
        return {}, [[("any", ["%d天" % n, "%d 天" % n, "%d days" % n, "%d day" % n])],
                    [("any", ["%d月%d日" % (d.month, d.day), "%d月%d号" % (d.month, d.day), d.isoformat(), "%d/%d" % (d.month, d.day), "%02d-%02d" % (d.month, d.day)])]]
    mk("hyb-33661", sub="files", task="multi_turn", desc="Multi-turn: days to the termination date in a file, then the notice deadline 45 days earlier", files=files,
       turns=[{"p": "服务协议的终止日期离今天还有多少天？文件在合同文件夹。", "req": ["read_file"]},
              {"p": "协议里写的续约通知期是终止日前多少天？那最晚哪天要发通知？"}],
       compute=compute, must=["read_file", "datetime"], traps=["TR-DECOY"], decoys={"TR-DECOY": "2026-03-01"}, rc=3,
       notes="Termination 2026-12-31 -> 106 days from 09-16. Turn 2: 45 days before = 2026-11-16.",
       alts=["协议终止日距今几天", "服务协议还有多久终止", "合同终止日期还剩几天", "到终止日期还有多少天（看合同文件夹）", "Days until the service agreement ends?"])


@b
def f06():
    files = {"bills/9月水电.csv": "item,amount\n水费,86.40\n电费,213.75\n燃气,67.30\n物业,150.00\n宽带,99.00\n"}

    def compute(files, wx):
        rows = [l.split(",") for l in files["bills/9月水电.csv"].strip().split("\n")[1:]]
        t = round(sum(float(x[1]) for x in rows), 2)
        return {"bills/汇总.txt": ["合计：%.2f" % t]}, [[("num", t)]]
    mk("hyb-33662", sub="files", task="tool_then_write", desc="Sum a small bill file and write the total to a result file in a fixed format", files=files,
       turns=[{"p": "把 bills/9月水电.csv 里所有费用加起来，结果写到 bills/汇总.txt，只写一行，格式是“合计：金额”，金额保留两位小数，不带千分位。", "tol": 0.006}],
       compute=compute, must=["read_file", "calculator", "write_file"], traps=["TR-NUMFMT"], decoys={"TR-NUMFMT": "合计：616.45"}, rc=3,
       notes="Sum = 86.40+213.75+67.30+150.00+99.00 = 616.45; file bills/汇总.txt must contain the line 合计：616.45 (staged).",
       alts=["汇总 9 月水电账单，写进汇总.txt", "合计账单金额并写入 bills/汇总.txt（合计：金额）", "把 csv 里的钱加总写到汇总文件", "算出九月账单总额，写成一行存到 汇总.txt", "Total the bills csv and write 合计：amount to bills/汇总.txt"])


@b
def f07():
    files = {"报销/差旅.csv": "date,item,amount\n2026-09-02,高铁,553.50\n2026-09-02,住宿,418.00\n2026-09-03,餐饮,126.80\n2026-09-03,打车,64.20\n2026-09-04,高铁,553.50\n"}

    def compute(files, wx):
        rows = [l.split(",") for l in files["报销/差旅.csv"].strip().split("\n")[1:]]
        t = round(sum(float(x[2]) for x in rows), 2)
        tr = round(sum(float(x[2]) for x in rows if x[1] == "高铁"), 2)
        return {"报销/总额.txt": ["%.2f" % t]}, [[("num", tr)], [("num", t)]]
    mk("hyb-33663", sub="files", task="tool_then_write", desc="Multi-turn: sum one item type from a reimbursement csv, then total everything into a file", files=files,
       turns=[{"p": "报销/差旅.csv 里高铁票一共花了多少钱？", "tol": 0.006, "req": ["read_file"]},
              {"p": "再算上所有项目的总额，把总额数字写进 报销/总额.txt。", "tol": 0.006}],
       compute=compute, must=["read_file", "calculator", "write_file"], traps=["TR-DECOY"], decoys={"TR-DECOY": "553.50"}, rc=4,
       notes="Turn1: 553.50*2 = 1107.00. Turn2: total 1716.00 -> file contains 1716.00.",
       alts=["差旅表里高铁票合计", "高铁一共多少钱（报销/差旅.csv）", "统计高铁票总花费", "报销单中高铁这一项加起来是多少", "Total spent on high-speed rail in 报销/差旅.csv?"])
