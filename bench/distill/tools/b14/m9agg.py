"""b14 M9a/M9c: cross-file and long-file aggregation, ids 10001-10066.

Sixteen table worlds, four cases each (the fourth has two turns: turn 2 narrows
or changes the filter), plus two extra single-turn cases. Every answer is one
number or one short name; each world's README states the counting rule and the
look-alike value that must not be counted. Data is past read_file's 64KB and
bash's 8KB output cap in every case, so a pipeline has to do the work.
"""
from aggcore import Q, agg_case

BUILDERS = []
NAMES_ZH = ["周敏", "李航", "王珂", "陈默", "赵一凡", "孙悦", "郑可", "冯岚"]


def builder(fn):
    BUILDERS.append(fn)
    return fn


def pick(rng, items, weights=None):
    return rng.choices(items, weights)[0] if weights else rng.choice(items)


# ------------------------------------------------------------------ worlds

W_TICKET = dict(
    fmt="csv", root="客服/工单导出", files=["2026-W%02d.csv" % w for w in range(27, 39)], rows=(115, 150),
    cols=["工单号", "渠道", "类别", "状态", "处理人", "时长分钟"], readme_name="说明.md", task_type="filter_count",
    readme=["# 工单导出说明", "", "每周一个文件，逗号分隔，第一行是表头。",
            "类别「退款」是客户实际发起的退款；「退款咨询」只是问政策，统计退款时不算。",
            "时长分钟 = 从首次响应到关闭的处理时长。"],
    gen=lambda rng, fi, i: {"工单号": "T%02d%04d" % (fi + 27, i), "渠道": pick(rng, ["电话", "在线", "邮件", "小程序"]),
                            "类别": pick(rng, ["退款", "退款咨询", "物流", "账号", "投诉", "发票"], [5, 4, 6, 3, 3, 3]),
                            "状态": pick(rng, ["已解决", "处理中", "已升级", "已关闭"], [6, 2, 1, 3]),
                            "处理人": pick(rng, NAMES_ZH[:6]), "时长分钟": rng.randint(3, 240)},
    unique="类别和状态都是精确字段；README 写明退款咨询不算退款，按字段精确匹配只有一个结果。", needs_readme=True)

W_ACCESS = dict(
    fmt="re", root="logs/edge", files=["access-2026-09-%02d.log" % d for d in range(8, 14)], rows=(260, 330),
    pattern=r'(?P<ip>\S+) - - \[(?P<ts>[^\]]+)\] "(?P<method>[A-Z]+) (?P<path>\S+) HTTP/1.1" (?P<status>\d{3}) (?P<bytes>\d+) (?P<ms>\d+)ms',
    template='{ip} - - [{ts}] "{method} {path} HTTP/1.1" {status} {bytes} {ms}ms', readme_name="README.md", task_type="count_events",
    readme=["# Edge access logs", "", "One file per day, nginx-style lines: ip, time, request, status, response bytes, latency.",
            "/api/v2/orders and /api/v2/orders/export are different endpoints; count only the exact path asked about."],
    gen=lambda rng, fi, i: {"ip": "10.%d.%d.%d" % (rng.randint(0, 3), rng.randint(0, 9), rng.randint(2, 60)),
                            "ts": "%02d/Sep/2026:%02d:%02d:%02d +0800" % (fi + 8, rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59)),
                            "method": pick(rng, ["GET", "GET", "GET", "POST", "DELETE"]),
                            "path": pick(rng, ["/api/v2/orders", "/api/v2/orders/export", "/api/v2/users", "/static/app.js", "/login", "/api/v2/cart"], [5, 2, 3, 4, 2, 3]),
                            "status": pick(rng, ["200", "200", "200", "201", "401", "404", "500", "502", "503"], [8, 8, 8, 2, 2, 3, 2, 1, 1]),
                            "bytes": str(rng.randint(120, 9000)), "ms": str(rng.randint(2, 900))},
    unique="Status and path are exact fields of each line; the README pins the endpoint, so one count results.", needs_readme=True)

W_PARCEL = dict(
    fmt="csv", root="快递/揽收", files=["%s.csv" % s for s in ["城东网点", "城西网点", "高新网点", "港口网点", "大学城网点", "机场网点", "老城网点", "开发区网点"]],
    rows=(150, 190), cols=["运单号", "收件城市", "重量kg", "件型", "状态"], readme_name="字段说明.txt", task_type="aggregate",
    readme=["字段说明（揽收导出）", "每个网点一个文件。重量kg 保留两位小数。",
            "件型「大件」指单件超过 20kg 的包裹；「大件拆分」是大件拆成的子包裹，按原单另计，不算大件。",
            "状态只有：已签收、运输中、退回。"],
    gen=lambda rng, fi, i: {"运单号": "YT%d%06d" % (fi, i), "收件城市": pick(rng, ["杭州", "宁波", "温州", "嘉兴", "绍兴", "金华", "台州", "湖州", "丽水", "衢州", "舟山"]),
                            "重量kg": "%.2f" % rng.uniform(0.3, 45), "件型": pick(rng, ["小件", "标准件", "大件", "大件拆分"], [5, 6, 2, 1]),
                            "状态": pick(rng, ["已签收", "运输中", "退回"], [7, 2, 1])},
    unique="件型和状态是精确字段；字段说明写明大件拆分不算大件。", needs_readme=True)

W_LOANS = dict(
    fmt="jsonl", root="library/loans", files=["2026-%02d.jsonl" % m for m in range(3, 9)], rows=(170, 220),
    readme_name="README.md", task_type="aggregate_jsonl",
    readme=["# Loan exports", "", "One JSON object per line, one file per month.",
            "branch \"Eastgate\" and \"Eastgate Annex\" are separate branches.",
            "overdue is true when the item came back late (or is still out past its due date)."],
    gen=lambda rng, fi, i: {"loan_id": "L%d-%04d" % (fi + 3, i), "member": "M%04d" % rng.randint(1, 900),
                            "branch": pick(rng, ["Eastgate", "Eastgate Annex", "Riverside", "Hillcrest", "Old Town"]),
                            "days": rng.randint(1, 42), "overdue": rng.random() < 0.18,
                            "format": pick(rng, ["book", "book", "dvd", "audiobook", "magazine"])},
    unique="branch is an exact string and overdue a boolean; the README separates Eastgate from Eastgate Annex.", needs_readme=True)
W_LOANS["cols"] = None

W_GATE = dict(
    fmt="kv", root="门禁/记录", files=["2026-09-%02d.log" % d for d in range(1, 11)], rows=(220, 260),
    cols=["时刻", "门", "卡号", "结果", "楼层"], readme_name="说明.md", task_type="count_events",
    readme=["# 门禁日志说明", "", "每天一个文件，每行是 键=值，用空格分隔。",
            "「北门」和「北门辅道」是两个不同的闸机，统计北门时不含北门辅道。",
            "结果只有三种：通过、拒绝、超时。"],
    gen=lambda rng, fi, i: {"时刻": "T%02d%02d%02d" % (rng.randint(6, 22), rng.randint(0, 59), rng.randint(0, 59)),
                            "门": pick(rng, ["北门", "北门辅道", "南门", "东门", "地库"], [4, 2, 4, 3, 2]),
                            "卡号": "C%05d" % rng.randint(1, 4000), "结果": pick(rng, ["通过", "拒绝", "超时"], [12, 2, 1]),
                            "楼层": "F%d" % rng.randint(1, 18)},
    unique="门和结果都是精确字段；北门辅道按说明单独算。", needs_readme=True)

W_METER = dict(
    fmt="csv", root="物业/电表", files=["%s栋.csv" % b for b in "ABCDEF"], rows=(190, 240),
    cols=["日期", "房间", "用电kWh", "类型"], readme_name="README.md", task_type="aggregate",
    readme=["# 电表日读数", "", "每栋一个文件，每天每户一行（只导出了有读数的户）。",
            "类型：居民、商铺、公摊。公摊不算任何住户，也不算商铺。"],
    gen=lambda rng, fi, i: {"日期": "2026-09-%02d" % rng.randint(1, 30), "房间": "%s%d%02d" % ("ABCDEF"[fi], rng.randint(1, 18), rng.randint(1, 6)),
                            "用电kWh": str(rng.randint(2, 97)), "类型": pick(rng, ["居民", "居民", "居民", "商铺", "公摊"])},
    unique="类型是精确字段，公摊按 README 排除。", needs_readme=True)

W_GRADES = dict(
    fmt="csv", root="grades", files=["class-%s.csv" % c for c in ["7A", "7B", "7C", "8A", "8B", "8C", "9A", "9B"]], rows=(130, 170),
    cols=["student_id", "course", "score", "attempt", "term"], readme_name="README.txt", task_type="filter_count",
    readme=["Grade exports, one file per class.", "course MATH101 and MATH1010 are different courses (MATH1010 is the honours track).",
            "attempt 1 is the first sitting; 2 or more is a retake. Pass mark is 60."],
    gen=lambda rng, fi, i: {"student_id": "S%d%03d" % (fi, rng.randint(1, 60)), "course": pick(rng, ["MATH101", "MATH1010", "PHYS110", "CHEM120", "HIST100"]),
                            "score": str(rng.randint(22, 100)), "attempt": pick(rng, ["1", "1", "1", "2", "3"]), "term": pick(rng, ["2026S", "2025F"])},
    unique="course, attempt and term are exact fields; MATH1010 is a different course per the README.", needs_readme=True)

W_HIRE = dict(
    fmt="jsonl", root="招聘/投递", files=["第%02d周.jsonl" % w for w in range(30, 38)], rows=(150, 190),
    readme_name="口径.md", task_type="aggregate_jsonl",
    readme=["# 投递数据口径", "", "每周一个文件，一行一个 JSON。",
            "岗位「后端工程师」和「后端工程师（实习）」分开统计。",
            "阶段依次是：简历、初面、终面、offer、拒绝。"],
    gen=lambda rng, fi, i: {"候选人": "H%02d%04d" % (fi, i), "岗位": pick(rng, ["后端工程师", "后端工程师（实习）", "前端工程师", "测试工程师", "产品经理", "数据分析师"]),
                            "渠道": pick(rng, ["内推", "招聘网站", "校园", "猎头"]), "阶段": pick(rng, ["简历", "初面", "终面", "offer", "拒绝"], [8, 4, 2, 1, 5]),
                            "期望月薪": rng.randint(8, 60) * 1000 + 500},
    unique="岗位和阶段是精确字段，口径文件写明实习岗位单独统计。", needs_readme=True)
W_HIRE["cols"] = None

W_ALARM = dict(
    fmt="kv", root="plant", files=["alarms.log"], rows=(1500, 1600), cols=["ts", "device", "sev", "code", "ack"],
    readme_name="NOTES.md", task_type="count_events",
    readme=["# Alarm log", "", "Appended in time order by the SCADA bridge; one line per alarm.",
            "pump-12 and pump-12b are different pumps (12b is the standby unit)."],
    gen=lambda rng, fi, i: {"ts": "2026-09-%02dT%02d%02d" % (1 + i // 55, (i // 3) % 24, rng.randint(0, 59)),
                            "device": pick(rng, ["pump-12", "pump-12b", "valve-3", "valve-31", "fan-7", "boiler-2"]),
                            "sev": pick(rng, ["info", "warning", "critical"], [10, 5, 2]), "code": "E%d" % rng.randint(100, 140),
                            "ack": pick(rng, ["yes", "yes", "no"])},
    unique="device, sev and ack are exact key=value fields; pump-12b is a different device.", needs_readme=True)

W_PAY = dict(
    fmt="csv", root="财务/支付流水", files=["2026-09-%02d.csv" % d for d in range(1, 11)], rows=(150, 190),
    cols=["流水号", "商户", "金额", "币种", "状态", "渠道"], readme_name="说明.txt", task_type="aggregate",
    readme=["支付流水说明", "每天一个文件，金额两位小数。",
            "商户「鲜果铺」和「鲜果铺二店」是两个独立商户号。", "状态：成功、失败、退款。"],
    gen=lambda rng, fi, i: {"流水号": "P%02d%05d" % (fi + 1, i), "商户": pick(rng, ["鲜果铺", "鲜果铺二店", "老张面馆", "晨光文具", "七号书店", "小林烘焙"]),
                            "金额": "%.2f" % rng.uniform(3, 480), "币种": pick(rng, ["CNY", "CNY", "CNY", "CNY", "HKD"]),
                            "状态": pick(rng, ["成功", "成功", "成功", "成功", "失败", "退款"]), "渠道": pick(rng, ["扫码", "刷卡", "小程序"])},
    unique="商户、币种、状态都是精确字段，鲜果铺二店按说明另算。", needs_readme=True)

W_WMS = dict(
    fmt="csv", sep="\t", root="wms/moves", files=["2026-%02d.tsv" % m for m in range(4, 10)], rows=(240, 300),
    cols=["date", "sku", "qty", "direction", "bin"], readme_name="README.md", task_type="aggregate",
    readme=["# Stock movements", "", "Tab-separated, one file per month, header on line 1.",
            "SKU AX-100 and AX-1000 are different items (AX-1000 is the pallet pack)."],
    gen=lambda rng, fi, i: {"date": "2026-%02d-%02d" % (fi + 4, rng.randint(1, 28)), "sku": pick(rng, ["AX-100", "AX-1000", "BR-220", "CQ-310", "DZ-045", "EL-777"]),
                            "qty": str(rng.randint(1, 96)), "direction": pick(rng, ["in", "out", "out"]), "bin": "%s-%02d" % (pick(rng, "PQRS"), rng.randint(1, 20))},
    unique="sku and direction are exact tab-separated fields.", needs_readme=True)

W_REVIEW = dict(
    fmt="jsonl", root="外卖/评价", files=["2026-09-%02d.jsonl" % d for d in range(5, 14)], rows=(160, 200),
    readme_name="说明.md", task_type="aggregate_jsonl",
    readme=["# 评价导出", "", "一行一条评价，每天一个文件。",
            "「老街面馆」和「老街面馆（新店）」是两家店，分开统计。", "评分 1–5 的整数；标签是数组，可能为空。"],
    gen=lambda rng, fi, i: {"订单": "O%02d%05d" % (fi, i), "店铺": pick(rng, ["老街面馆", "老街面馆（新店）", "阿香米线", "川味小厨", "轻食实验室"]),
                            "评分": pick(rng, [1, 2, 3, 4, 5], [1, 1, 2, 4, 6]), "标签": rng.sample(["量大", "偏咸", "送得快", "包装好", "凉了", "好吃"], rng.randint(0, 3)),
                            "有图": rng.random() < 0.3},
    unique="店铺是精确字符串，评分是整数；说明写明新店分开统计。", needs_readme=True)
W_REVIEW["cols"] = None

W_FLIGHT = dict(
    fmt="csv", root="ops/flights", files=["%s.csv" % a for a in ["PEK", "PVG", "CAN", "SZX", "CTU", "XIY", "KMG"]], rows=(170, 210),
    cols=["flight", "airline", "date", "delay_min", "status"], readme_name="README.md", task_type="filter_count",
    readme=["# Departure board exports", "", "One file per departure airport, September 2026.",
            "SkyLark and SkyLark Express are separate airlines with separate codes.", "status is one of: on_time, delayed, cancelled."],
    gen=lambda rng, fi, i: {"flight": "%s%d" % (pick(rng, ["SL", "SX", "MU", "CZ", "HU"]), rng.randint(100, 9999)),
                            "airline": pick(rng, ["SkyLark", "SkyLark Express", "Eastern Crane", "Southern Pearl", "Hainan Breeze"]),
                            "date": "2026-09-%02d" % rng.randint(1, 30), "delay_min": str(rng.randint(0, 240)),
                            "status": pick(rng, ["on_time", "on_time", "delayed", "cancelled"], [5, 5, 3, 1])},
    unique="airline and status are exact fields; SkyLark Express is a different airline.", needs_readme=True)

W_PARK = dict(
    fmt="kv", root="停车场", files=["进出记录.log"], rows=(1500, 1600), cols=["日期", "车牌", "入口", "停留分钟", "费用", "月卡"],
    readme_name="说明.md", task_type="count_events",
    readme=["# 进出记录说明", "", "收费系统按出场顺序追加，一行一次出场。",
            "月卡=是 的车辆不收费，费用记 0；入口「东1」和「东1临时」不是同一个入口。"],
    gen=lambda rng, fi, i: (lambda mon: {"日期": "2026-09-%02d" % (1 + i // 54), "车牌": "%s%s%04d" % (pick(rng, ["浙A", "浙B", "沪C", "苏E"]), pick(rng, "DFGHK"), rng.randint(0, 9999)),
                                         "入口": pick(rng, ["东1", "东1临时", "西2", "南3"]), "停留分钟": str(rng.randint(5, 900)),
                                         "费用": "0" if mon else str(rng.randint(1, 30) * 2), "月卡": "是" if mon else "否"})(rng.random() < 0.3),
    unique="入口、月卡是精确字段；记录按出场顺序追加。", needs_readme=True)

W_CI = dict(
    fmt="jsonl", root="ci", files=["builds.jsonl"], rows=(1450, 1550), readme_name="README.md", task_type="aggregate_jsonl",
    readme=["# CI build history", "", "One JSON object per build, appended as builds finish.",
            "branch \"main\" and \"main-backup\" are different branches."],
    gen=lambda rng, fi, i: {"build": 50000 + i * 3 + rng.randint(0, 2), "repo": pick(rng, ["api", "web", "worker", "infra", "mobile"]),
                            "branch": pick(rng, ["main", "main-backup", "release", "dev", "feature-x"], [5, 1, 2, 4, 2]),
                            "result": pick(rng, ["passed", "passed", "passed", "failed", "cancelled"]),
                            "duration_s": rng.randint(40, 1900), "tests_failed": rng.choice([0, 0, 0, 1, 2, 3, 5])},
    unique="branch and result are exact strings; the README separates main from main-backup.", needs_readme=True)
W_CI["cols"] = None

W_HEALTH = dict(
    fmt="csv", root="体检/2026", files=["%s.csv" % d for d in ["研发部", "市场部", "财务部", "运营部", "客服部", "行政部"]], rows=(220, 260),
    cols=["工号", "项目", "结果", "异常"], readme_name="说明.md", task_type="filter_count",
    readme=["# 体检结果导出", "", "每个部门一个文件，一人多项，每项一行。",
            "项目「血压」是首次测量；「血压复测」是复测记录，统计血压异常时不算复测。", "异常列只有 是 / 否。"],
    gen=lambda rng, fi, i: {"工号": "E%d%03d" % (fi, rng.randint(1, 90)), "项目": pick(rng, ["血压", "血压复测", "血糖", "视力", "心电图", "肝功能"]),
                            "结果": pick(rng, ["正常", "偏高", "偏低", "待复查"]), "异常": pick(rng, ["否", "否", "否", "是"])},
    unique="项目和异常是精确字段；说明写明复测不算。", needs_readme=True)


# ------------------------------------------------------------------ cases

CSV = "cat 客服/工单导出/*.csv | awk -F, "


def plan():
    """(id, world, sub, queries, desc, family) for every case, in id order."""
    out = []
    add = out.append
    # 1 ticket (zh)
    add(("tab-10001", W_TICKET, "M9a", [Q("count", 'r["类别"]=="退款" and r["状态"]=="已解决"',
         "第三季度这十二周的工单导出里，已经解决的退款工单一共有多少张？",
         CSV + "'$3==\"退款\" && $4==\"已解决\"' | wc -l", "已解决的退款工单共 {v} 张（类别精确等于「退款」，退款咨询不算）。",
         decoy={"pred": 'r["类别"].startswith("退款") and r["状态"]=="已解决"'}, decoy_note="counting 退款咨询 as refunds")],
         "Counts resolved refund tickets across twelve weekly exports where a look-alike category shares the prefix", "fam-tab-b14-ticketrefund-01"))
    add(("tab-10002", W_TICKET, "M9a", [Q("sum", 'r["渠道"]=="电话" and r["类别"]=="投诉"',
         "电话渠道进来的投诉工单，处理时长加起来一共多少分钟？周会要用这个数。",
         CSV + "'$2==\"电话\" && $3==\"投诉\" {s+=$6} END {print s}'", "电话渠道投诉工单的处理时长合计 {v} 分钟。", val='r["时长分钟"]',
         decoy={"pred": 'r["类别"]=="投诉"'}, decoy_note="summing complaints from every channel")],
         "Sums handling minutes for phone complaints across twelve weekly ticket exports", "fam-tab-b14-ticketminutes-01"))
    add(("tab-10003", W_TICKET, "M9a", [Q("top", 'r["状态"]=="已升级"',
         "这一季度谁手上被升级的工单最多？给我名字就行。",
         CSV + "'$4==\"已升级\" {print $5}' | sort | uniq -c | sort -rn | head -3", "被升级工单最多的是 {v}。", key='r["处理人"]',
         decoy={"pred": 'r["状态"]!="已解决" and r["状态"]!="已关闭"'}, decoy_note="counting 处理中 together with 已升级")],
         "Finds the agent with the most escalated tickets across weekly exports", "fam-tab-b14-ticketescalate-01"))
    add(("tab-10004", W_TICKET, "M9a", [
        Q("count", 'r["渠道"]=="小程序" and r["类别"]=="发票"', "小程序渠道的发票类工单这季度一共有多少张？",
          CSV + "'$2==\"小程序\" && $3==\"发票\"' | wc -l", "{v} 张。"),
        Q("count", 'r["渠道"]=="小程序" and r["类别"]=="发票" and r["状态"]=="处理中"', "其中现在还在处理中的有几张？",
          CSV + "'$2==\"小程序\" && $3==\"发票\" && $4==\"处理中\"' | wc -l", "小程序发票工单里仍在处理中的有 {v} 张。")],
         "Two turns: counts invoice tickets from one channel, then narrows to the ones still open", "fam-tab-b14-ticketinvoice-01"))
    add(("tab-10005", W_TICKET, "M9a", [Q("distinct", 'r["类别"]=="退款" and int(r["时长分钟"])>120',
         "处理时长超过两个小时的退款工单，一共涉及几个不同的工单号？",
         CSV + "'$3==\"退款\" && $6>120 {print $1}' | sort -u | wc -l", "超过 120 分钟的退款工单有 {v} 个不同工单号。", val='r["工单号"]',
         decoy={"pred": 'r["类别"].startswith("退款") and int(r["时长分钟"])>120'}, decoy_note="including 退款咨询")],
         "Counts distinct refund ticket ids with long handling time across weekly exports", "fam-tab-b14-ticketlong-01"))
    # 2 access log (en)
    A = "cat logs/edge/*.log | "
    add(("log-10006", W_ACCESS, "M9a", [Q("count", 'r["path"]=="/api/v2/orders" and r["status"].startswith("5")',
         "How many 5xx responses did the /api/v2/orders endpoint return across the six days of edge logs?",
         A + "awk '$7==\"/api/v2/orders\" && $9 ~ /^5/' | wc -l", "/api/v2/orders returned {v} 5xx responses over 8-13 September.",
         decoy={"pred": 'r["path"].startswith("/api/v2/orders") and r["status"].startswith("5")'}, decoy_note="prefix-matching /api/v2/orders/export too")],
         "Counts 5xx responses for one exact endpoint across six daily access logs with a longer look-alike path", "fam-log-b14-edge5xx-01"))
    add(("log-10007", W_ACCESS, "M9a", [Q("sum", 'r["path"]=="/static/app.js" and r["status"]=="200"',
         "What's the total number of response bytes we served for /static/app.js with status 200 across those edge logs?",
         A + "awk '$7==\"/static/app.js\" && $9==200 {s+=$10} END {print s}'", "{v} bytes in total for /static/app.js (status 200 only).", val='r["bytes"]',
         decoy={"pred": 'r["path"]=="/static/app.js"'}, decoy_note="summing every status")],
         "Sums response bytes for one static asset with status 200 across six daily access logs", "fam-log-b14-edgebytes-01"))
    add(("log-10008", W_ACCESS, "M9a", [Q("top", 'r["status"]=="404"',
         "Which request path produced the most 404s over the week in logs/edge?",
         A + "awk '$9==404 {print $7}' | sort | uniq -c | sort -rn | head -3", "{v} had the most 404s.", key='r["path"]',
         decoy={"pred": 'r["status"] in ("404", "401")'}, decoy_note="lumping 401s in with 404s")],
         "Finds the path with the most 404 responses across six daily access logs", "fam-log-b14-edge404-01"))
    add(("log-10009", W_ACCESS, "M9a", [
        Q("distinct", 'r["status"]=="401"', "How many different client IPs got a 401 in the edge logs from the 8th to the 13th?",
          A + "awk '$9==401 {print $1}' | sort -u | wc -l", "{v} distinct IPs.", val='r["ip"]'),
        Q("distinct", 'r["status"]=="401" and r["path"]=="/login"', "And how many of those were hitting /login specifically?",
          A + "awk '$9==401 && $7==\"/login\" {print $1}' | sort -u | wc -l", "{v} distinct IPs got a 401 on /login.", val='r["ip"]')],
         "Two turns: distinct client IPs with 401 responses, then only those on the login path", "fam-log-b14-edge401-01"))
    add(("log-10010", W_ACCESS, "M9a", [Q("count", 'r["method"]=="DELETE" and r["path"]=="/api/v2/cart" and r["status"] in ("200","201")',
         "Count the successful (200 or 201) DELETE calls to /api/v2/cart across the edge access logs.",
         A + "awk '$6==\"\\\"DELETE\" && $7==\"/api/v2/cart\" && ($9==200 || $9==201)' | wc -l", "{v} successful DELETEs on /api/v2/cart.",
         decoy={"pred": 'r["method"]=="DELETE" and r["path"]=="/api/v2/cart"'}, decoy_note="counting failed DELETEs too")],
         "Counts successful DELETE calls on one endpoint across six daily access logs", "fam-log-b14-edgedelete-01"))
    # 3 parcels (zh)
    P = "cat 快递/揽收/*.csv | awk -F, "
    add(("tab-10011", W_PARCEL, "M9a", [Q("sumc", 'r["件型"]=="大件" and r["状态"]=="已签收"',
         "八个网点已签收的大件，总重量是多少公斤？",
         P + "'$4==\"大件\" && $5==\"已签收\" {s+=$3} END {printf \"%.2f\\n\", s}'", "已签收大件总重 {v} kg（大件拆分不算）。", val='r["重量kg"]',
         decoy={"pred": 'r["件型"].startswith("大件") and r["状态"]=="已签收"'}, decoy_note="counting 大件拆分 as 大件")],
         "Sums signed-for heavy parcel weight across eight station exports with a split-parcel look-alike", "fam-tab-b14-parcelweight-01"))
    add(("tab-10012", W_PARCEL, "M9a", [Q("count", 'r["状态"]=="退回" and r["收件城市"]=="温州"',
         "寄往温州的件里，被退回的一共有多少件？",
         P + "'$2==\"温州\" && $5==\"退回\"' | wc -l", "寄往温州的退回件共 {v} 件。")],
         "Counts returned parcels to one city across eight station exports", "fam-tab-b14-parcelreturn-01"))
    add(("tab-10013", W_PARCEL, "M9a", [Q("top", 'r["状态"]=="运输中"',
         "现在还在路上的件，哪个收件城市最多？",
         P + "'$5==\"运输中\" {print $2}' | sort | uniq -c | sort -rn | head -3", "运输中的件以 {v} 最多。", key='r["收件城市"]')],
         "Finds the destination city with the most in-transit parcels across station exports", "fam-tab-b14-parcelcity-01"))
    add(("tab-10014", W_PARCEL, "M9a", [
        Q("count", 'r["件型"]=="大件"', "揽收数据里大件一共有多少件？", P + "'$4==\"大件\"' | wc -l", "{v} 件。",
          decoy={"pred": 'r["件型"].startswith("大件")'}, decoy_note="counting 大件拆分"),
        Q("count", 'r["件型"]=="大件" and float(r["重量kg"])>30', "其中超过 30 公斤的有几件？",
          P + "'$4==\"大件\" && $3>30' | wc -l", "超过 30kg 的大件有 {v} 件。")],
         "Two turns: counts heavy parcels, then those above a weight threshold", "fam-tab-b14-parcelheavy-01"))
    # 4 loans (en, jq)
    L = "cat library/loans/*.jsonl | jq -s "
    add(("log-10015", W_LOANS, "M9a", [Q("count", 'r["branch"]=="Eastgate" and r["overdue"]',
         "How many overdue loans did the Eastgate branch have from March through August?",
         L + "'map(select(.branch==\"Eastgate\" and .overdue)) | length'", "Eastgate had {v} overdue loans (Eastgate Annex not included).",
         decoy={"pred": 'r["branch"].startswith("Eastgate") and r["overdue"]'}, decoy_note="including Eastgate Annex")],
         "Counts overdue loans for one branch across six monthly JSONL exports with a look-alike branch name", "fam-log-b14-loanoverdue-01"))
    add(("log-10016", W_LOANS, "M9a", [Q("sum", 'r["format"]=="dvd" and r["branch"]=="Riverside"',
         "Add up the loan days for DVDs borrowed at Riverside over the six monthly exports.",
         L + "'map(select(.format==\"dvd\" and .branch==\"Riverside\") | .days) | add'", "{v} loan days for Riverside DVDs.", val='r["days"]',
         decoy={"pred": 'r["format"]=="dvd"'}, decoy_note="summing DVDs from every branch")],
         "Sums loan days for one format at one branch across monthly JSONL exports", "fam-log-b14-loandays-01"))
    add(("log-10017", W_LOANS, "M9a", [Q("top", 'r["overdue"]',
         "Which branch had the most overdue loans in these exports?",
         L + "'map(select(.overdue)) | group_by(.branch) | map({b: .[0].branch, n: length}) | sort_by(-.n) | .[0:3]'", "{v} had the most overdue loans.", key='r["branch"]')],
         "Finds the branch with the most overdue loans across monthly JSONL exports", "fam-log-b14-loanbranch-01"))
    add(("log-10018", W_LOANS, "M9a", [
        Q("distinct", 'r["overdue"] and r["format"]=="audiobook"', "How many different members returned an audiobook late?",
          L + "'map(select(.overdue and .format==\"audiobook\") | .member) | unique | length'", "{v} members.", val='r["member"]'),
        Q("distinct", 'r["overdue"] and r["format"]=="audiobook" and r["branch"]=="Hillcrest"', "Only counting Hillcrest, how many?",
          L + "'map(select(.overdue and .format==\"audiobook\" and .branch==\"Hillcrest\") | .member) | unique | length'", "{v} members at Hillcrest.", val='r["member"]')],
         "Two turns: distinct members with a late audiobook, then only at one branch", "fam-log-b14-loanmembers-01"))
    # 5 gate (zh, kv)
    G = "cat 门禁/记录/*.log | "
    add(("log-10019", W_GATE, "M9a", [Q("count", 'r["门"]=="北门" and r["结果"]=="拒绝"',
         "9 月 1 号到 10 号，北门一共拒绝了多少次刷卡？",
         G + "grep ' 门=北门 ' | grep -c ' 结果=拒绝 '", "北门共拒绝 {v} 次（北门辅道不算）。",
         decoy={"pred": 'r["门"].startswith("北门") and r["结果"]=="拒绝"'}, decoy_note="counting 北门辅道 too")],
         "Counts rejected swipes at one gate across ten daily access-control logs with a look-alike gate name", "fam-log-b14-gatereject-01"))
    add(("log-10020", W_GATE, "M9a", [Q("distinct", 'r["结果"]=="超时"',
         "这十天里有多少张不同的卡刷卡超时过？",
         G + "grep ' 结果=超时 ' | awk '{print $3}' | sort -u | wc -l", "共有 {v} 张不同的卡出现过超时。", val='r["卡号"]')],
         "Counts distinct cards with a timeout across ten daily access logs", "fam-log-b14-gatetimeout-01"))
    add(("log-10021", W_GATE, "M9a", [Q("top", 'r["结果"]=="拒绝"',
         "哪个门拒绝刷卡的次数最多？",
         G + "grep ' 结果=拒绝 ' | awk '{print $2}' | sort | uniq -c | sort -rn | head -3", "拒绝最多的是 {v}。", key='r["门"]')],
         "Finds the gate with the most rejected swipes across daily logs", "fam-log-b14-gatetop-01"))
    add(("log-10022", W_GATE, "M9a", [
        Q("count", 'r["门"]=="地库" and r["结果"]=="通过"', "地库闸机这十天一共放行了多少次？",
          G + "grep ' 门=地库 ' | grep -c ' 结果=通过 '", "{v} 次。"),
        Q("count", 'r["门"]=="地库" and r["结果"]=="通过" and r["楼层"] in ("F1","F2","F3")', "其中去 1 到 3 楼的有多少次？",
          G + "grep ' 门=地库 ' | grep ' 结果=通过 ' | grep -cE ' 楼层=F[123]$'", "去 1–3 楼的放行有 {v} 次。")],
         "Two turns: counts passes at the garage gate, then only those to the lowest floors", "fam-log-b14-gategarage-01"))
    # 6 meter (zh)
    M = "cat 物业/电表/*.csv | awk -F, "
    add(("tab-10023", W_METER, "M9a", [Q("sum", 'r["类型"]=="商铺"',
         "九月份商铺一共用了多少度电？六栋楼的读数都算上。",
         M + "'$4==\"商铺\" {s+=$3} END {print s}'", "九月商铺合计用电 {v} 度。", val='r["用电kWh"]',
         decoy={"pred": 'r["类型"]!="居民"'}, decoy_note="adding 公摊 to the shops")],
         "Sums shop electricity use across six building meter exports where shared-area rows must be excluded", "fam-tab-b14-metershop-01"))
    add(("tab-10024", W_METER, "M9a", [Q("distinct", 'r["类型"]=="居民" and int(r["用电kWh"])>=90',
         "有多少户居民出现过单日用电 90 度及以上？按房间号算。",
         M + "'$4==\"居民\" && $3>=90 {print $2}' | sort -u | wc -l", "有 {v} 户居民出现过单日 ≥90 度。", val='r["房间"]')],
         "Counts distinct households with a high single-day reading across building meter exports", "fam-tab-b14-meterhigh-01"))
    add(("tab-10025", W_METER, "M9a", [Q("top", 'r["类型"]=="居民"',
         "哪个房间九月份居民用电总量最高？", M + "'$4==\"居民\" {a[$2]+=$3} END {for (k in a) print a[k], k}' | sort -rn | head -3",
         "用电最多的是 {v}。", key='r["房间"]', val='r["用电kWh"]')],
         "Finds the household with the highest monthly total across building meter exports", "fam-tab-b14-metertop-01"))
    add(("tab-10026", W_METER, "M9a", [
        Q("sum", 'r["类型"]=="公摊"', "公摊这个月一共用了多少度？", M + "'$4==\"公摊\" {s+=$3} END {print s}'", "{v} 度。", val='r["用电kWh"]'),
        Q("sum", 'r["类型"]=="公摊" and r["日期"]>="2026-09-16"', "下半月（16 号起）的公摊是多少度？",
          M + "'$4==\"公摊\" && $1>=\"2026-09-16\" {s+=$3} END {print s}'", "16 号起的公摊用电 {v} 度。", val='r["用电kWh"]')],
         "Two turns: sums shared-area electricity, then only the second half of the month", "fam-tab-b14-metershared-01"))
    # 7 grades (en)
    GR = "cat grades/*.csv | awk -F, "
    add(("tab-10027", W_GRADES, "M9a", [Q("count", 'r["course"]=="MATH101" and r["attempt"]=="1" and int(r["score"])<60',
         "How many first-attempt MATH101 results were below the pass mark, across all eight class files?",
         GR + "'$2==\"MATH101\" && $4==1 && $3<60' | wc -l", "{v} first-attempt MATH101 results were below 60.",
         decoy={"pred": 'r["course"].startswith("MATH101") and r["attempt"]=="1" and int(r["score"])<60'}, decoy_note="counting MATH1010 too")],
         "Counts first-attempt fails in one course across eight class files with a look-alike course code", "fam-tab-b14-gradefail-01"))
    add(("tab-10028", W_GRADES, "M9a", [Q("top", 'int(r["score"])<60 and r["term"]=="2026S"',
         "In the 2026S term, which course had the most fails?", GR + "'$5==\"2026S\" && $3<60 {print $2}' | sort | uniq -c | sort -rn | head -3",
         "{v} had the most fails in 2026S.", key='r["course"]')],
         "Finds the course with the most fails in one term across class files", "fam-tab-b14-gradetop-01"))
    add(("tab-10029", W_GRADES, "M9a", [Q("distinct", 'int(r["attempt"])>=2 and r["course"]=="PHYS110"',
         "How many different students had to retake PHYS110?", GR + "'$2==\"PHYS110\" && $4>=2 {print $1}' | sort -u | wc -l",
         "{v} students retook PHYS110.", val='r["student_id"]')],
         "Counts distinct students retaking one course across class files", "fam-tab-b14-graderetake-01"))
    add(("tab-10030", W_GRADES, "M9a", [
        Q("count", 'int(r["score"])>=90 and r["term"]=="2026S"', "How many scores of 90 or above were recorded in 2026S?",
          GR + "'$5==\"2026S\" && $3>=90' | wc -l", "{v}."),
        Q("count", 'int(r["score"])>=90 and r["term"]=="2026S" and r["course"]=="CHEM120"', "Just CHEM120?",
          GR + "'$5==\"2026S\" && $3>=90 && $2==\"CHEM120\"' | wc -l", "{v} CHEM120 scores of 90+ in 2026S.")],
         "Two turns: counts top scores in a term, then only for one course", "fam-tab-b14-gradetop90-01"))
    # 8 hiring (zh, jq)
    H = "cat 招聘/投递/*.jsonl | jq -s "
    add(("log-10031", W_HIRE, "M9a", [Q("count", 'r["岗位"]=="后端工程师" and r["阶段"]=="终面"',
         "后端工程师这个岗位，现在走到终面的候选人有几个？", H + "'map(select(.[\"岗位\"]==\"后端工程师\" and .[\"阶段\"]==\"终面\")) | length'",
         "后端工程师进入终面的有 {v} 人（实习岗不算）。", decoy={"pred": 'r["岗位"].startswith("后端工程师") and r["阶段"]=="终面"'}, decoy_note="counting the intern posting")],
         "Counts final-round candidates for one role across weekly JSONL exports with an intern look-alike", "fam-log-b14-hirefinal-01"))
    add(("log-10032", W_HIRE, "M9a", [Q("top", 'r["阶段"]=="offer"',
         "拿到 offer 的人里，哪个渠道来的最多？", H + "'map(select(.[\"阶段\"]==\"offer\")) | group_by(.[\"渠道\"]) | map({c: .[0][\"渠道\"], n: length}) | sort_by(-.n) | .[0:3]'",
         "offer 最多的渠道是 {v}。", key='r["渠道"]')],
         "Finds the sourcing channel with the most offers across weekly JSONL exports", "fam-log-b14-hirechannel-01"))
    add(("log-10033", W_HIRE, "M9a", [Q("sum", 'r["阶段"]=="offer" and r["岗位"]=="数据分析师"',
         "数据分析师岗位拿到 offer 的人，期望月薪加起来是多少？我要估一下预算。",
         H + "'map(select(.[\"阶段\"]==\"offer\" and .[\"岗位\"]==\"数据分析师\") | .[\"期望月薪\"]) | add'", "合计 {v} 元/月。", val='r["期望月薪"]')],
         "Sums expected salaries of candidates with offers for one role across weekly exports", "fam-log-b14-hirebudget-01"))
    add(("log-10034", W_HIRE, "M9a", [
        Q("count", 'r["渠道"]=="内推"', "这八周内推来的简历一共多少份？", H + "'map(select(.[\"渠道\"]==\"内推\")) | length'", "{v} 份。"),
        Q("count", 'r["渠道"]=="内推" and r["阶段"]=="拒绝"', "内推里被拒的有多少？", H + "'map(select(.[\"渠道\"]==\"内推\" and .[\"阶段\"]==\"拒绝\")) | length'",
          "内推被拒的有 {v} 人。")],
         "Two turns: counts referral applications, then the rejected ones", "fam-log-b14-hirereferral-01"))
    # 9 alarms (en, long single file)
    AL = "plant/alarms.log"
    add(("log-10035", W_ALARM, "M9c", [Q("count", 'r["device"]=="pump-12" and r["sev"]=="critical" and r["ack"]=="no"',
         "How many critical alarms on pump-12 are still unacknowledged in the plant alarm log?",
         "grep ' device=pump-12 ' %s | grep ' sev=critical ' | grep -c ' ack=no$'" % AL, "{v} unacknowledged critical alarms on pump-12 (pump-12b excluded).",
         decoy={"pred": 'r["device"].startswith("pump-12") and r["sev"]=="critical" and r["ack"]=="no"'}, decoy_note="matching pump-12b as well")],
         "Counts unacknowledged critical alarms for one device in a long alarm log with a look-alike device", "fam-log-b14-alarmpump-01"))
    add(("log-10036", W_ALARM, "M9c", [Q("top", 'r["sev"]=="critical"',
         "Which device raised the most critical alarms?", "grep ' sev=critical ' %s | awk '{print $2}' | sort | uniq -c | sort -rn | head -3" % AL,
         "{v} raised the most critical alarms.", key='r["device"]')],
         "Finds the device with the most critical alarms in a long alarm log", "fam-log-b14-alarmtop-01"))
    add(("log-10037", W_ALARM, "M9c", [Q("distinct", 'r["sev"]!="info" and r["device"].startswith("valve-")',
         "How many different alarm codes did the valves raise at warning level or above?",
         "grep ' device=valve-' %s | grep -v ' sev=info ' | awk '{print $4}' | sort -u | wc -l" % AL, "{v} distinct codes.", val='r["code"]')],
         "Counts distinct alarm codes from valves above info level in a long alarm log", "fam-log-b14-alarmcodes-01"))
    add(("log-10038", W_ALARM, "M9c", [
        Q("count", 'r["device"]=="boiler-2" and r["sev"]=="warning"', "How many warnings has boiler-2 logged?",
          "grep ' device=boiler-2 ' %s | grep -c ' sev=warning '" % AL, "{v}."),
        Q("count", 'r["device"]=="boiler-2" and r["sev"]=="warning" and r["ts"]>="2026-09-20"', "And from the 20th onwards?",
          "grep ' device=boiler-2 ' %s | grep ' sev=warning ' | awk '$1 >= \"ts=2026-09-20\"' | wc -l" % AL, "{v} warnings on boiler-2 since 20 September.")],
         "Two turns: counts warnings for one device in a long log, then only the later part of the month", "fam-log-b14-alarmboiler-01"))
    # 10 payments (zh)
    PY = "cat 财务/支付流水/*.csv | awk -F, "
    add(("tab-10039", W_PAY, "M9a", [Q("sumc", 'r["商户"]=="鲜果铺" and r["币种"]=="CNY" and r["状态"]=="成功"',
         "鲜果铺 9 月 1 日到 10 日人民币成功收款一共多少钱？",
         PY + "'$2==\"鲜果铺\" && $4==\"CNY\" && $5==\"成功\" {s+=$3} END {printf \"%.2f\\n\", s}'", "鲜果铺人民币成功收款合计 {v} 元（二店不算）。", val='r["金额"]',
         decoy={"pred": 'r["商户"].startswith("鲜果铺") and r["币种"]=="CNY" and r["状态"]=="成功"'}, decoy_note="including 鲜果铺二店")],
         "Sums successful CNY payments for one merchant across ten daily exports with a look-alike merchant", "fam-tab-b14-paysum-01"))
    add(("tab-10040", W_PAY, "M9a", [Q("count", 'r["状态"]=="退款" and r["渠道"]=="小程序"',
         "小程序渠道这十天发生了多少笔退款？", PY + "'$5==\"退款\" && $6==\"小程序\"' | wc -l", "小程序退款 {v} 笔。")],
         "Counts refunds through one channel across ten daily payment exports", "fam-tab-b14-payrefund-01"))
    add(("tab-10041", W_PAY, "M9a", [Q("top", 'r["状态"]=="失败"',
         "哪个商户支付失败的笔数最多？", PY + "'$5==\"失败\" {print $2}' | sort | uniq -c | sort -rn | head -3", "失败最多的是 {v}。", key='r["商户"]')],
         "Finds the merchant with the most failed payments across daily exports", "fam-tab-b14-payfail-01"))
    add(("tab-10042", W_PAY, "M9a", [
        Q("count", 'r["币种"]=="HKD"', "流水里港币的交易有多少笔？", PY + "'$4==\"HKD\"' | wc -l", "{v} 笔。"),
        Q("sumc", 'r["币种"]=="HKD" and r["状态"]=="成功"', "成功的港币交易一共多少港币？",
          PY + "'$4==\"HKD\" && $5==\"成功\" {s+=$3} END {printf \"%.2f\\n\", s}'", "成功港币交易合计 {v} 港币。", val='r["金额"]')],
         "Two turns: counts HKD transactions, then sums the successful ones", "fam-tab-b14-payhkd-01"))
    # 11 wms (en, tsv)
    WM = "cat wms/moves/*.tsv | awk -F'\\t' "
    add(("tab-10043", W_WMS, "M9a", [Q("sum", 'r["sku"]=="AX-100" and r["direction"]=="out"',
         "How many units of AX-100 went out of the warehouse between April and September?",
         WM + "'$2==\"AX-100\" && $4==\"out\" {s+=$3} END {print s}'", "{v} units of AX-100 shipped out (AX-1000 excluded).", val='r["qty"]',
         decoy={"pred": 'r["sku"].startswith("AX-100") and r["direction"]=="out"'}, decoy_note="prefix-matching AX-1000")],
         "Sums outbound quantity for one SKU across monthly TSV exports with a look-alike SKU", "fam-tab-b14-wmsout-01"))
    add(("tab-10044", W_WMS, "M9a", [Q("top", 'r["direction"]=="in"',
         "Which bin received the most units in total?", WM + "'$4==\"in\" {a[$5]+=$3} END {for (k in a) print a[k], k}' | sort -rn | head -3",
         "Bin {v} received the most.", key='r["bin"]', val='r["qty"]', margin=3)],
         "Finds the bin with the largest inbound total across monthly TSV exports", "fam-tab-b14-wmsbin-01"))
    add(("tab-10045", W_WMS, "M9a", [Q("count", 'r["direction"]=="in" and int(r["qty"])>=80',
         "How many inbound movements were for 80 units or more?", WM + "'$4==\"in\" && $3>=80' | wc -l", "{v} inbound movements of 80+.")],
         "Counts large inbound movements across monthly TSV exports", "fam-tab-b14-wmsbig-01"))
    add(("tab-10046", W_WMS, "M9a", [
        Q("distinct", 'r["direction"]=="out" and r["date"]>="2026-09-01"', "How many different SKUs shipped out in September?",
          "awk -F'\\t' '$4==\"out\" {print $2}' wms/moves/2026-09.tsv | sort -u | wc -l", "{v}.", val='r["sku"]', scope=["2026-09.tsv"]),
        Q("sum", 'r["direction"]=="out" and r["sku"]=="DZ-045"', "Total units of DZ-045 out across all six months?",
          WM + "'$2==\"DZ-045\" && $4==\"out\" {s+=$3} END {print s}'", "{v} units of DZ-045 went out.", val='r["qty"]')],
         "Two turns: distinct SKUs shipped in one month, then the six-month outbound total for one SKU", "fam-tab-b14-wmsdz-01"))
    # 12 reviews (zh, jq)
    RV = "cat 外卖/评价/*.jsonl | jq -s "
    add(("log-10047", W_REVIEW, "M9a", [Q("count", 'r["店铺"]=="老街面馆" and r["评分"]<=2',
         "老街面馆这九天收到了多少条两星及以下的差评？", RV + "'map(select(.[\"店铺\"]==\"老街面馆\" and .[\"评分\"]<=2)) | length'",
         "老街面馆差评（≤2 星）{v} 条，新店不算。", decoy={"pred": 'r["店铺"].startswith("老街面馆") and r["评分"]<=2'}, decoy_note="counting the new branch")],
         "Counts low ratings for one shop across daily JSONL review exports with a look-alike shop", "fam-log-b14-reviewlow-01"))
    add(("log-10048", W_REVIEW, "M9a", [Q("sum", 'r["有图"]',
         "带图评价里一共打了多少个标签？", RV + "'map(select(.[\"有图\"]) | .[\"标签\"] | length) | add'", "带图评价的标签总数是 {v} 个。", val='len(r["标签"])')],
         "Sums tag-array lengths over reviews with photos across daily JSONL exports", "fam-log-b14-reviewtags-01"))
    add(("log-10049", W_REVIEW, "M9a", [Q("top", 'r["评分"]==5',
         "哪家店拿到的五星评价最多？", RV + "'map(select(.[\"评分\"]==5)) | group_by(.[\"店铺\"]) | map({s: .[0][\"店铺\"], n: length}) | sort_by(-.n) | .[0:3]'",
         "五星最多的是 {v}。", key='r["店铺"]')],
         "Finds the shop with the most five-star reviews across daily JSONL exports", "fam-log-b14-review5-01"))
    add(("log-10050", W_REVIEW, "M9a", [
        Q("count", '"凉了" in r["标签"]', "有多少条评价带了「凉了」这个标签？", RV + "'map(select(.[\"标签\"] | index(\"凉了\"))) | length'", "{v} 条。"),
        Q("count", '"凉了" in r["标签"] and r["店铺"]=="阿香米线"', "阿香米线的呢？", RV + "'map(select((.[\"标签\"] | index(\"凉了\")) and .[\"店铺\"]==\"阿香米线\")) | length'",
          "阿香米线带「凉了」标签的评价有 {v} 条。")],
         "Two turns: counts reviews carrying one tag, then only for one shop", "fam-log-b14-reviewcold-01"))
    # 13 flights (en)
    F = "cat ops/flights/*.csv | awk -F, "
    add(("tab-10051", W_FLIGHT, "M9a", [Q("count", 'r["airline"]=="SkyLark" and r["status"]=="cancelled"',
         "How many SkyLark departures were cancelled across the seven airport exports?",
         F + "'$2==\"SkyLark\" && $5==\"cancelled\"' | wc -l", "{v} SkyLark departures were cancelled (SkyLark Express not included).",
         decoy={"pred": 'r["airline"].startswith("SkyLark") and r["status"]=="cancelled"'}, decoy_note="counting SkyLark Express")],
         "Counts cancellations for one airline across seven airport exports with a look-alike airline", "fam-tab-b14-flightcancel-01"))
    add(("tab-10052", W_FLIGHT, "M9a", [Q("sum", 'r["status"]=="delayed" and r["airline"]=="Southern Pearl"',
         "Total delay minutes for Southern Pearl's delayed flights this September?",
         F + "'$2==\"Southern Pearl\" && $5==\"delayed\" {s+=$4} END {print s}'", "{v} minutes of delay.", val='r["delay_min"]')],
         "Sums delay minutes for one airline across airport exports", "fam-tab-b14-flightdelay-01"))
    add(("tab-10053", W_FLIGHT, "M9a", [Q("top", 'r["status"]=="delayed" and int(r["delay_min"])>120',
         "Which airline had the most departures delayed by over two hours?",
         F + "'$5==\"delayed\" && $4>120 {print $2}' | sort | uniq -c | sort -rn | head -3", "{v}.", key='r["airline"]')],
         "Finds the airline with the most long delays across airport exports", "fam-tab-b14-flightlong-01"))
    add(("tab-10054", W_FLIGHT, "M9a", [
        Q("count", 'r["status"]=="cancelled"', "How many cancellations in total across all seven airports?", F + "'$5==\"cancelled\"' | wc -l", "{v}."),
        Q("count", 'r["status"]=="cancelled"', "And just out of CTU?", "awk -F, '$5==\"cancelled\"' ops/flights/CTU.csv | wc -l",
          "{v} cancellations out of CTU.", scope=["CTU.csv"])],
         "Two turns: counts cancellations across airports, then for one airport", "fam-tab-b14-flightctu-01"))
    # 14 parking (zh, long single file)
    PK = "停车场/进出记录.log"
    add(("log-10055", W_PARK, "M9c", [Q("sum", 'r["入口"]=="东1" and r["月卡"]=="否"',
         "从东1入口进来的临停车，九月一共收了多少停车费？",
         "grep ' 入口=东1 ' %s | grep ' 月卡=否$' | awk '{split($5, a, \"=\"); s+=a[2]} END {print s}'" % PK, "东1入口临停车共收费 {v} 元（东1临时不算）。", val='r["费用"]',
         decoy={"pred": 'r["入口"].startswith("东1") and r["月卡"]=="否"'}, decoy_note="including 东1临时")],
         "Sums parking fees for one entrance in a long append-only log with a look-alike entrance", "fam-log-b14-parkfee-01"))
    add(("log-10056", W_PARK, "M9c", [Q("count", 'r["车牌"].startswith("沪C") and int(r["停留分钟"])>600',
         "沪C 牌照的车，停超过 10 个小时的有多少次？",
         "grep ' 车牌=沪C' %s | awk '{split($4, a, \"=\"); if (a[2] > 600) n++} END {print n}'" % PK, "沪C 车牌停留超过 600 分钟的有 {v} 次。")],
         "Counts long stays for one plate prefix in a long parking log", "fam-log-b14-parklong-01"))
    add(("log-10057", W_PARK, "M9c", [Q("top", 'r["月卡"]=="否"',
         "临停车里，哪个入口进来的最多？", "grep ' 月卡=否$' %s | awk '{print $3}' | sort | uniq -c | sort -rn | head -3" % PK, "{v}。", key='r["入口"]')],
         "Finds the busiest entrance for non-member cars in a long parking log", "fam-log-b14-parkentry-01"))
    add(("log-10058", W_PARK, "M9c", [
        Q("count", 'r["月卡"]=="是"', "九月月卡车一共出场多少次？", "grep -c ' 月卡=是$' %s" % PK, "{v} 次。"),
        Q("count", 'r["月卡"]=="是" and r["日期"]>="2026-09-21"', "21 号以后的呢？", "grep ' 月卡=是$' %s | awk '$1 >= \"日期=2026-09-21\"' | wc -l" % PK,
          "21 号起月卡车出场 {v} 次。")],
         "Two turns: counts member-card exits in a long log, then only the last part of the month", "fam-log-b14-parkmember-01"))
    # 15 ci (en, long jsonl)
    CI = "jq -s %s ci/builds.jsonl"
    add(("log-10059", W_CI, "M9c", [Q("count", 'r["branch"]=="main" and r["result"]=="failed"',
         "Count the failed runs on the main branch in our CI history.",
         CI % "'map(select(.branch==\"main\" and .result==\"failed\")) | length'", "{v} failed builds on main (main-backup excluded).",
         decoy={"pred": 'r["branch"].startswith("main") and r["result"]=="failed"'}, decoy_note="matching main-backup")],
         "Counts failed builds on one branch in a long JSONL history with a look-alike branch", "fam-log-b14-cimain-01"))
    add(("log-10060", W_CI, "M9c", [Q("sum", 'r["repo"]=="worker" and r["result"]=="failed"',
         "Add up the failed test counts across every failed worker build.",
         CI % "'map(select(.repo==\"worker\" and .result==\"failed\") | .tests_failed) | add'", "{v} failed tests across failed worker builds.", val='r["tests_failed"]')],
         "Sums failed-test counts for one repo's failed builds in a long JSONL history", "fam-log-b14-citests-01"))
    add(("log-10061", W_CI, "M9c", [Q("top", 'r["result"]=="cancelled"',
         "Which repo has the most cancelled builds?", CI % "'map(select(.result==\"cancelled\")) | group_by(.repo) | map({r: .[0].repo, n: length}) | sort_by(-.n) | .[0:3]'",
         "{v}.", key='r["repo"]')],
         "Finds the repo with the most cancelled builds in a long JSONL history", "fam-log-b14-cicancel-01"))
    add(("log-10062", W_CI, "M9c", [
        Q("count", 'r["repo"]=="infra" and r["duration_s"]>1200', "How many infra builds took longer than 20 minutes?",
          CI % "'map(select(.repo==\"infra\" and .duration_s>1200)) | length'", "{v}."),
        Q("count", 'r["repo"]=="infra" and r["duration_s"]>1200 and r["result"]=="passed"', "How many of those still passed?",
          CI % "'map(select(.repo==\"infra\" and .duration_s>1200 and .result==\"passed\")) | length'", "{v} of the slow infra builds passed.")],
         "Two turns: counts slow builds for one repo, then the slow ones that passed", "fam-log-b14-cislow-01"))
    # 16 health (zh)
    HC = "cat 体检/2026/*.csv | awk -F, "
    add(("tab-10063", W_HEALTH, "M9a", [Q("count", 'r["项目"]=="血压" and r["异常"]=="是"',
         "今年体检血压异常的记录一共有多少条？六个部门都要算。",
         HC + "'$2==\"血压\" && $4==\"是\"' | wc -l", "血压异常 {v} 条（不含血压复测）。",
         decoy={"pred": 'r["项目"].startswith("血压") and r["异常"]=="是"'}, decoy_note="counting 血压复测")],
         "Counts abnormal blood-pressure records across six department exports with a retest look-alike", "fam-tab-b14-healthbp-01"))
    add(("tab-10064", W_HEALTH, "M9a", [Q("distinct", 'r["异常"]=="是"',
         "有多少位员工至少有一项体检异常？按工号去重。", HC + "'$4==\"是\" {print $1}' | sort -u | wc -l", "有 {v} 位员工至少一项异常。", val='r["工号"]')],
         "Counts distinct employees with any abnormal item across department exports", "fam-tab-b14-healthany-01"))
    add(("tab-10065", W_HEALTH, "M9a", [Q("top", 'r["项目"]=="视力" and r["异常"]=="是"', "哪个部门视力异常的人次最多？",
         "for f in 体检/2026/*.csv; do printf '%s ' \"$f\"; awk -F, '$2==\"视力\" && $4==\"是\"' \"$f\" | wc -l; done | sort -k2 -rn | head -3",
         "视力异常最多的是 {v}。", key='r["部门"]')],
         "Finds the department with the most abnormal eyesight results across department exports", "fam-tab-b14-healtheye-01"))
    add(("tab-10066", W_HEALTH, "M9a", [
        Q("count", 'r["项目"]=="心电图" and r["结果"]=="待复查"', "心电图结果是待复查的有多少条？", HC + "'$2==\"心电图\" && $3==\"待复查\"' | wc -l", "{v} 条。"),
        Q("count", 'r["项目"]=="心电图" and r["结果"]=="待复查"', "研发部的有几条？", "awk -F, '$2==\"心电图\" && $3==\"待复查\"' 体检/2026/研发部.csv | wc -l",
          "研发部心电图待复查 {v} 条。", scope=["研发部.csv"])],
         "Two turns: counts ECG results awaiting review, then for one department", "fam-tab-b14-healthecg-01"))
    return out


def _make(entry, seed):
    cid, world, sub, queries, desc, family = entry

    def build():
        extra = {}
        if world is W_HEALTH and queries[0]["agg"] == "top":
            return _health_top(cid, queries, desc, family, seed)
        traps = ["TR-TRUNC"] + (["TR-DECOY"] if any(q.get("decoy") for q in queries) else []) if sub == "M9c" else None
        return agg_case(cid, world, queries, sub=sub, seed=seed, desc=desc, family=family, traps=traps,
                        axes=("LNG", "OBS") if sub == "M9c" else ("CHN", "OBS"), **extra)
    build.__name__ = cid.replace("-", "_")
    return build


def _health_top(cid, queries, desc, family, seed):
    """The department is the file name, not a column: tag rows with it."""
    world = dict(W_HEALTH)
    names = [f[:-4] for f in world["files"]]
    base = world["gen"]
    world["cols"] = world["cols"] + ["部门"]
    world["gen"] = lambda rng, fi, i: dict(base(rng, fi, i), 部门=names[fi])
    world["readme"] = world["readme"] + ["每行最后一列是部门名，与文件名一致。"]
    q = dict(queries[0])
    q["cmd"] = "cat 体检/2026/*.csv | awk -F, '$2==\"视力\" && $4==\"是\" {print $5}' | sort | uniq -c | sort -rn | head -3"
    return agg_case(cid, world, [q], sub="M9a", seed=seed, desc=desc, family=family, axes=("CHN", "OBS"))


for _i, _entry in enumerate(plan()):
    BUILDERS.append(_make(_entry, 14000 + _i))
