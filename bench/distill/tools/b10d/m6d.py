"""M6 (v1.4 §3.6) b10d: mixed units (tab-8490..8519) and line location (log-8430..8444, code-8400..8414).

Unit-mix cases: one value column mixes unit spellings; the answer needs a
grouped look (data_query) or arithmetic (calculator) plus conversion. Every
verify.py re-parses case.json with its own unit table and recomputes.
Line-location cases: the answer is the line number of a unique definition /
event / key; decoys (comments, calls, older mentions, sibling-file twins) are
generated alongside. Everything is seeded, nothing iterates over a set.
"""
import csv as _csv
import io as _io
import random
import re
from decimal import Decimal
from common import revised
write_case = revised({"tab-%d" % n: "S5：去掉 required data_query / calculator（老师整读表后按单位换算求和是合理路径）；read_file 上限 1→2（README 写换算口径）；判据目标类别改为从题面取（tab-8508/8510/8512/8513/8516/8518 题面问的类别与判据算的类别不一致，三遍老师一致给出题面类别的正确值）；去掉题面里表中没有的时间限定（这个月 / 这周）。" for n in range(8490, 8520)})

MAXREAD = {"max_calls": {"read_file": 1}}
MAXREAD2 = {"max_calls": {"read_file": 2}}

# Shared by the generator and every verify.py (kept as source text).
UNIT_SRC = '''
import re
from decimal import Decimal

def parse(s, UT):
    s = s.strip()
    if s[0] == "\\u00a5":
        s = s[1:] + "\\u5143"
    elif s[0] == "$":
        s = s[1:] + " USD"
    m = re.match(r"^([0-9][0-9,]*(?:\\.[0-9]+)?)\\s*(.*)$", s)
    return Decimal(m.group(1).replace(",", "")) * UT[m.group(2).strip()]

def plain(d):
    return format(d.normalize(), "f")

def comma(s):
    a, _, b = s.partition(".")
    return "{:,}".format(int(a)) + ("." + b if b else "")

def forms(s, names):
    out = set([s, comma(s)]) if len(s.replace(".", "")) >= 4 else set()
    for nm in names:
        for v in (s, comma(s)):
            if nm in ("$", "\\u00a5"):
                out.add(nm + v)
            else:
                out.add(v + " " + nm)
                out.add(v + nm)
    return sorted(out)
'''
exec(UNIT_SRC)


def csvtext(header, rows):
    buf = _io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def _money_zh(r):
    return [lambda: "¥" + "{:,}".format(r.randrange(300, 3000, 50)),
            lambda: "%d元" % r.randrange(200, 2500, 10),
            lambda: "%.1f万元" % (r.randrange(6, 40) / 10)]


def _two(fa, fb):
    return lambda r: [lambda: fa(r), lambda: fb(r)]


# kind -> (unit table, style factory, ask options [(factor, names)])
KINDS = {
    "time": ({"ms": 1, "s": 1000}, _two(lambda r: "%dms" % r.randrange(120, 990, 10), lambda r: "%.1fs" % (r.randrange(10, 50) / 10)),
             [(1000, ["秒", "s", "seconds"]), (1, ["毫秒", "ms", "milliseconds"])]),
    "money_zh": ({"元": 1, "万元": 10000}, _money_zh, [(1, ["元", "¥"])]),
    "money_en": ({"USD": 1, "k USD": 1000},
                 lambda r: [lambda: "$" + "{:,}".format(r.randrange(300, 3000, 50)), lambda: "%d USD" % r.randrange(200, 2500, 10),
                            lambda: "%.1fk USD" % (r.randrange(6, 40) / 10)], [(1, ["USD", "$", "dollars"])]),
    "mass": ({"kg": 1000, "g": 1}, _two(lambda r: "%.1fkg" % (r.randrange(8, 60) / 10), lambda r: "%dg" % r.randrange(150, 950, 10)),
             [(1, ["g", "克", "grams"]), (1000, ["kg", "公斤", "千克", "kilograms"])]),
    "length": ({"cm": 10, "m": 1000}, _two(lambda r: "%dcm" % r.randrange(20, 190, 5), lambda r: "%.1fm" % (r.randrange(12, 60) / 10)),
                [(10, ["cm", "厘米", "centimeters"]), (1000, ["m", "米", "meters"])]),
    "size": ({"MB": 1, "GB": 1024}, _two(lambda r: "%dMB" % r.randrange(120, 980, 4), lambda r: "%.1fGB" % (r.randrange(10, 48) / 10)),
             [(1, ["MB"])]),
    "volume": ({"mL": 1, "L": 1000}, _two(lambda r: "%dmL" % r.randrange(100, 900, 25), lambda r: "%.1fL" % (r.randrange(10, 40) / 10)),
                [(1, ["mL", "毫升"]), (1000, ["L", "升", "liters"])]),
    "energy": ({"Wh": 1, "kWh": 1000}, _two(lambda r: "%dWh" % r.randrange(120, 950, 10), lambda r: "%.1fkWh" % (r.randrange(10, 45) / 10)),
               [(1, ["Wh", "瓦时"]), (1000, ["kWh", "度", "千瓦时"])]),
    "dose": ({"mg": 1, "g": 1000}, _two(lambda r: "%dmg" % r.randrange(100, 900, 25), lambda r: "%.1fg" % (r.randrange(10, 35) / 10)),
              [(1, ["mg", "毫克", "milligrams"])]),
    "dist": ({"m": 1, "km": 1000}, _two(lambda r: "%dm" % r.randrange(150, 950, 10), lambda r: "%.1fkm" % (r.randrange(10, 60) / 10)),
              [(1, ["m", "米", "meters"]), (1000, ["km", "公里", "kilometers"])]),
}


def build_unit(n, e):
    """e: dict(kind, ask, mode 'dq'|'calc', op 'sum'|'max', slug, cols, cats, path, pref, readme, prompt, desc, zh)."""
    UT, factory, asks = KINDS[e["kind"]]
    askf, names = asks[e["ask"]]
    idc, catc, valc = e["cols"]
    dq = e["mode"] == "dq"
    for attempt in range(200):
        r = random.Random(n * 131 + attempt)
        styles = factory(r)
        if dq:
            pool = []
            for i in range(6):
                v = styles[i % len(styles)]()
                if v not in pool:
                    pool.append(v)
            if len(pool) < 5:
                continue
            N = r.randint(70, 130)
            vals = [r.choice(pool) for _ in range(N)]
        else:
            N = r.randint(18, 26)
            vals = [styles[i % len(styles)]() if r.random() < 0.5 else r.choice(styles)() for i in range(N)]
        cats = [r.choice(e["cats"]) for _ in range(N)]
        rows = [["%s%d" % (e["pref"], 1000 + 7 * i + r.randint(0, 6)), c, v] for i, (c, v) in enumerate(zip(cats, vals))]
        found = [c for c in e["cats"] if c in e["prompt"]]
        assert not dq or len(found) == 1, (n, found)
        tgt = found[0] if dq else None
        sel = [x for x in rows if tgt is None or x[1] == tgt]
        if len(sel) < 8:
            continue
        base = [(x[2], parse(x[2], UT)) for x in sel]
        numnaive = [(Decimal(re.match(r"[^0-9]*([0-9][0-9,]*(?:\.[0-9]+)?)", s).group(1).replace(",", "")), s) for s, _ in base]
        if e["op"] == "sum":
            ans = sum(b for _, b in base) / askf
            naive = sum(x for x, _ in numnaive) / 1
        else:
            top = max(b for _, b in base)
            if len({s for s, b in base if b == top}) != 1:
                continue
            ans = top / askf
            nmax = max(numnaive)[1]
            if nmax == [s for s, b in base if b == top][0]:
                continue
            naive = max(numnaive)[0]
        s = plain(ans)
        if len(s.partition(".")[2]) > 3 or ans == naive:
            continue
        break
    else:
        raise SystemExit("no seed for %d" % n)
    any_ = forms(s, names)
    cid = "tab-%d" % n
    tab = ",".join(str(x) for x in (UT,)) if False else repr(UT)
    write_case(
        cid, desc=e["desc"], task_type="aggregate", family="fam-tab-b10d-%s-01" % e["slug"], level="L1", ref_calls=3,
        traps=["TR-NUMFMT"], decoys={"TR-NUMFMT": plain(naive)}, axes=["OBS"], case_expect=MAXREAD2,
        files={e["path"]: csvtext([idc, catc, valc], rows), "README.md": e["readme"]},
        turns=[{"prompt": e["prompt"], "expect": {"output_contains_any": any_, "max_output_chars": 500}}],
        verify=UNITV % (repr(e["path"]), repr(valc), repr(catc), repr(tgt), repr(UT), askf, repr(names), repr(e["op"])),
        notes=UNITN % (e["valc_note"] if "valc_note" in e else valc, plain(naive), "data_query 按取值分组计数" if dq else "读一次文件后用计算器逐项换算", s, s),
    )
    return cid, s


UNITV = "import csv\nimport io\nimport json\n" + UNIT_SRC + '''
case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"][%s])))
VAL, CAT, TGT, UT, ASKF, NAMES, OP = %s, %s, %s, %s, %d, %s, %s
sel = [parse(r[VAL], UT) for r in rows if TGT is None or r[CAT] == TGT]
res = (sum(sel) if OP == "sum" else max(sel)) / ASKF
print(json.dumps({"expected_contains_any": forms(plain(res), NAMES)}))
'''

UNITN = '''
## Traps
- TR-NUMFMT: 列 %s 里同一个量混了几种单位写法，直接把数字去掉单位相加（或取最大）得到 %s，不是真值。

## Reference solution
1. %s，得到各种写法各出现几次（或各行取值）。
2. 用计算器按 README / 题面口径换算到题目要的单位后汇总。
终答 1-2 句：给出结果 %s，并写明换算口径（例如 1 s = 1000 ms、1 万元 = 10000 元）。判据：包含 %s 的任一写法；read_file 最多 2 次。

## Why the answer is unique
每个写法的单位明确，换算系数是常识或 README 给定，筛选条件为等值，因此结果唯一。
'''


def U(n, kind, ask, mode, op, slug, path, cols, cats, pref, readme, prompt, desc):
    return build_unit(n, dict(kind=kind, ask=ask, mode=mode, op=op, slug=slug, path=path, cols=cols, cats=cats,
                              pref=pref, readme=readme, prompt=prompt, desc=desc))


# ---- unit mix, Chinese (tab-8490..8504)
U(8490, "time", 0, "dq", "sum", "firstreply", "客服/首响耗时.csv", ("工单号", "渠道", "首响耗时"), ["电话", "在线", "邮件"], "TK-",
  "# 客服首响耗时\n\n新旧两套工单系统合并导出，首响耗时一套记毫秒、一套记秒。\n",
  "电话渠道的工单，首响耗时一共多少秒？数据在 客服/首响耗时.csv。",
  "Total the first-reply time of one channel in a ticket export whose duration column mixes ms and s spellings")
U(8491, "money_zh", 0, "dq", "sum", "travelexp", "财务/差旅报销.csv", ("单号", "类别", "金额"), ["住宿", "交通", "餐饮"], "BX-",
  "# 差旅报销\n\n各分公司自己填的金额，写法不统一：有的带 ¥ 和千分位，有的写「元」，有的写「万元」。\n",
  "住宿类的差旅报销一共多少元？明细在 财务/差旅报销.csv。",
  "Sum lodging expense claims whose amount column mixes yuan-sign, yuan and wan-yuan spellings")
U(8492, "mass", 1, "dq", "sum", "inboundfruit", "仓储/入库.csv", ("批次", "品类", "重量"), ["苹果", "梨", "柑橘", "葡萄"], "RK-",
  "# 果品入库\n\n称重来自两台秤：地磅记 kg，台秤记 g。\n",
  "苹果一共入库多少公斤？入库记录在 仓储/入库.csv。",
  "Total one fruit's inbound weight when the weight column mixes kg and g readings")
U(8493, "length", 1, "calc", "sum", "curtaincut", "车间/用布记录.csv", ("裁单", "款式", "用布"), ["遮光", "纱帘"], "CJ-",
  "# 窗帘裁剪用布\n\n裁剪师傅有人量米、有人量厘米，直接按各自习惯记的。\n",
  "这批窗帘裁剪一共用了多少米布？记录在 车间/用布记录.csv。",
  "Add up fabric used in a cutting log that mixes centimetre and metre entries")
U(8494, "size", 0, "dq", "max", "backupfile", "运维/备份清单.csv", ("任务", "类型", "大小"), ["数据库", "日志", "图片"], "BK-",
  "# 备份清单\n\n大小列是备份脚本直接打印的，小文件用 MB，大文件用 GB。1 GB 按 1024 MB 算。\n",
  "数据库类备份里，最大的一个文件有多少 MB？清单在 运维/备份清单.csv。",
  "Find the largest database backup in MB when sizes mix MB and GB strings")
U(8495, "volume", 1, "dq", "sum", "milkuse", "门店/牛奶领用.csv", ("领用单", "饮品", "用量"), ["拿铁", "卡布奇诺", "燕麦拿铁"], "LY-",
  "# 牛奶领用\n\n早班用量杯记 mL，晚班按整盒/整瓶记 L。\n",
  "拿铁一共领了多少升牛奶？领用记录在 门店/牛奶领用.csv。",
  "Total milk drawn for one drink when the usage column mixes mL and L")
U(8496, "energy", 1, "calc", "sum", "evcharge", "充电站/周充电量.csv", ("桩号", "时段", "电量"), ["白天", "夜间"], "ZH-",
  "# 周充电量\n\n不同品牌的桩上报单位不同：有的报 Wh，有的报 kWh。\n",
  "这个充电站一共充了多少度电？数据在 充电站/周充电量.csv。",
  "Total a week's charging energy from posts reporting Wh or kWh")
U(8497, "dose", 0, "dq", "sum", "pharmadose", "药房/配药记录.csv", ("处方", "药品", "剂量"), ["维C咀嚼片", "钙片", "鱼油"], "CF-",
  "# 配药记录\n\n剂量由两个终端录入，一个写 mg，一个写 g。\n",
  "维C咀嚼片这批处方一共配了多少毫克？记录在 药房/配药记录.csv。",
  "Sum dispensed milligrams of one supplement where the dose column mixes mg and g")
U(8498, "dist", 0, "dq", "max", "riderleg", "配送/骑手里程.csv", ("订单", "骑手", "里程"), ["阿浩", "小满", "老周"], "PS-",
  "# 骑手单程里程\n\n短途记米，长途记公里。\n",
  "阿浩跑过的单程里最远的一单是多少米？里程表在 配送/骑手里程.csv。",
  "Find one rider's longest single trip in metres from a column mixing m and km")
U(8499, "time", 1, "calc", "sum", "firstpaint", "前端/首屏耗时.csv", ("页面", "环境", "首屏"), ["线上", "灰度"], "PG-",
  "# 首屏耗时\n\n埋点 SDK 两个版本，老版本上报毫秒，新版本上报秒。\n",
  "这几个页面的首屏耗时加起来是多少毫秒？数据在 前端/首屏耗时.csv。",
  "Add up first-paint timings reported by two SDK versions in ms and s")
U(8500, "money_zh", 0, "calc", "sum", "teambuild", "行政/团建采购.csv", ("采购单", "事项", "金额"), ["饮料", "场地"], "TJ-",
  "# 团建采购\n\n各人垫付后自己填的金额，写法不一。\n",
  "团建这几笔采购合计多少元？明细在 行政/团建采购.csv。",
  "Sum small team-building purchases written with yuan sign, yuan and wan-yuan")
U(8501, "mass", 0, "dq", "max", "parcelheavy", "快递/站点包裹.csv", ("运单", "站点", "重量"), ["上海站", "杭州站", "苏州站"], "YD-",
  "# 站点包裹重量\n\n重量由扫描枪记 kg、手工称记 g。\n",
  "上海站收的包裹里最重的一件是多少克？数据在 快递/站点包裹.csv。",
  "Find the heaviest parcel at one station in grams from kg and g readings")
U(8502, "length", 0, "dq", "sum", "woodboard", "木工坊/板材.csv", ("料单", "木种", "长度"), ["橡木", "胡桃木", "白蜡木"], "BC-",
  "# 板材长度\n\n手写料单，有人写厘米，有人写米。\n",
  "橡木板材的长度加起来是多少厘米？料单在 木工坊/板材.csv。",
  "Total oak board length in cm from a list mixing cm and m")
U(8503, "volume", 0, "calc", "sum", "reagentuse", "实验室/试剂用量.csv", ("实验", "试剂", "用量"), ["甲醇", "乙醇"], "SJ-",
  "# 试剂用量\n\n学生记录：滴管量的写 mL，量筒量的写 L。\n",
  "这几次实验的试剂用量合计多少毫升？记录在 实验室/试剂用量.csv。",
  "Add up reagent volumes recorded as mL or L")
U(8504, "time", 0, "dq", "max", "buildslow", "ci/构建耗时.csv", ("构建号", "流水线", "耗时"), ["android", "ios", "web"], "BD-",
  "# 构建耗时\n\n耗时来自两个 CI 插件，一个写毫秒，一个写秒。\n",
  "android 流水线里耗时最长的一次构建是多少秒？数据在 ci/构建耗时.csv。",
  "Find the slowest build of one pipeline in seconds from ms and s strings")

# ---- unit mix, English (tab-8505..8519)
U(8505, "money_en", 0, "dq", "sum", "vendorinv", "finance/vendor-invoices.csv", ("invoice", "vendor", "amount"), ["Kestrel Print", "Lumen Cloud", "Harbor Courier"], "INV-",
  "# Vendor invoices\n\nAmounts were typed by three clerks: some write $1,200, some 1200 USD, some 1.2k USD. All are US dollars.\n",
  "What is the total we were invoiced by Kestrel Print, in US dollars? The ledger is finance/vendor-invoices.csv.",
  "Total one vendor's invoices where amounts mix dollar-sign, USD suffix and k USD")
U(8506, "time", 1, "dq", "sum", "apilatency", "metrics/api-latency.csv", ("request", "endpoint", "latency"), ["/search", "/login", "/cart"], "RQ-",
  "# API latency samples\n\nThe gateway logs latency as 940ms; the newer sidecar logs 1.6s.\n",
  "Add up the latency of all /search requests in milliseconds. Samples are in metrics/api-latency.csv.",
  "Total one endpoint's latency in ms from samples written as ms or s")
U(8507, "mass", 1, "calc", "sum", "bakeryflour", "bakery/flour-usage.csv", ("batch", "bread", "flour"), ["rye", "sourdough"], "BT-",
  "# Flour usage per batch\n\nBakers weigh on two scales: kitchen scale in g, sack scale in kg.\n",
  "How many kilograms of flour did these batches use in total? Usage log: bakery/flour-usage.csv.",
  "Add up flour weights logged in g or kg")
U(8508, "length", 1, "dq", "max", "cablerun", "install/cable-runs.csv", ("run", "floor", "length"), ["floor-2", "floor-3", "floor-4"], "CR-",
  "# Cable runs\n\nTechs note short runs in cm and long runs in m.\n",
  "What is the longest cable run on floor-3, in metres? See install/cable-runs.csv.",
  "Find the longest cable run on one floor in metres from cm and m values")
U(8509, "size", 0, "dq", "sum", "mediaarchive", "archive/asset-sizes.csv", ("asset", "type", "size"), ["video", "audio", "image"], "AS-",
  "# Asset sizes\n\nThe archiver prints sizes in MB or GB. Treat 1 GB as 1024 MB.\n",
  "How many MB of storage do the video assets take in total? Data: archive/asset-sizes.csv.",
  "Total video asset storage in MB from MB and GB strings")
U(8510, "volume", 1, "dq", "sum", "brewbatch", "brewery/fill-log.csv", ("fill", "beer", "volume"), ["pale ale", "stout", "lager"], "FL-",
  "# Fill log\n\nSmall test fills are logged in mL, tank fills in L.\n",
  "How many litres of stout did we fill in total? The fill log is brewery/fill-log.csv.",
  "Total stout filled in litres from mL and L entries")
U(8511, "energy", 0, "calc", "sum", "solararray", "energy/solar-daily.csv", ("day", "array", "yield"), ["north", "south"], "SY-",
  "# Daily solar yield\n\nOld inverters report Wh, new ones report kWh.\n",
  "What was the combined yield of these days in Wh? Logs are in energy/solar-daily.csv.",
  "Add up solar yield reported in Wh or kWh")
U(8512, "dose", 0, "dq", "max", "doseunits", "clinic/dosing.csv", ("order", "drug", "dose"), ["drug-A", "drug-B", "drug-C"], "OR-",
  "# Dosing orders\n\nOrders are written in mg or g depending on the prescriber.\n",
  "What is the largest single dose ordered for drug-B, in mg? Orders: clinic/dosing.csv.",
  "Find the largest single dose of one drug in mg from mg and g values")
U(8513, "dist", 1, "dq", "sum", "deliverykm", "fleet/trips.csv", ("trip", "van", "distance"), ["van-1", "van-2", "van-3"], "TR-",
  "# Van trips\n\nThe dashcam logs short hops in m; the odometer logs longer trips in km.\n",
  "How many kilometres did van-2 cover in total? Trip data: fleet/trips.csv.",
  "Total one van's distance in km from m and km entries")
U(8514, "money_en", 0, "calc", "sum", "eventspend", "events/spend.csv", ("item", "area", "cost"), ["catering", "venue"], "EX-",
  "# Event spend\n\nCosts typed by hand in dollars: $1,200, 1200 USD or 1.2k USD.\n",
  "What did the event cost in total, in USD? Spend sheet: events/spend.csv.",
  "Add up event costs typed as dollar-sign, USD and k USD")
U(8515, "time", 0, "dq", "max", "batchjob", "jobs/runtimes.csv", ("job", "queue", "runtime"), ["nightly", "hourly", "adhoc"], "JB-",
  "# Job runtimes\n\nRuntime is written by two schedulers: 940ms style or 1.6s style.\n",
  "Which run was the longest in the nightly queue, and how many seconds did it take? Table: jobs/runtimes.csv.",
  "Find the longest nightly job runtime in seconds from ms and s strings")
U(8516, "money_en", 0, "dq", "max", "refunds", "support/refunds.csv", ("refund", "region", "amount"), ["EMEA", "APAC", "AMER"], "RF-",
  "# Refunds\n\nFinance exports mix $1,200, 1200 USD and 1.2k USD forms.\n",
  "What is the biggest single refund issued in APAC, in USD? Refund list: support/refunds.csv.",
  "Find the biggest APAC refund in USD from mixed currency spellings")
U(8517, "mass", 0, "calc", "sum", "scrapmetal", "yard/scrap-weights.csv", ("load", "metal", "weight"), ["copper", "steel"], "SC-",
  "# Scrap loads\n\nThe weighbridge prints kg; the hand scale prints g.\n",
  "What is the total weight of these loads in grams? Loads: yard/scrap-weights.csv.",
  "Add up scrap loads weighed in kg or g")
U(8518, "length", 0, "dq", "sum", "tilecut", "site/tile-lengths.csv", ("cut", "room", "length"), ["kitchen", "bath", "hall"], "TL-",
  "# Tile cuts\n\nFitters note lengths in cm or m.\n",
  "How many centimetres of tile were cut for the bath in total? Cut list: site/tile-lengths.csv.",
  "Total bathroom tile cuts in cm from cm and m entries")
U(8519, "size", 0, "calc", "sum", "logbundle", "ops/log-sizes.csv", ("file", "host", "size"), ["web", "db"], "LG-",
  "# Log file sizes\n\nSizes come straight from ls output converted by hand: MB or GB. Use 1 GB = 1024 MB.\n",
  "What is the combined size of these log files in MB? List: ops/log-sizes.csv.",
  "Add up log sizes written in MB or GB")


# ---------------------------------------------------------------- line location
LINE_SRC = '''
def lineforms(n):
    n = str(n)
    return sorted(["\\u7b2c %s \\u884c" % n, "\\u7b2c%s\\u884c" % n, "%s \\u884c" % n, "%s\\u884c" % n, "line %s" % n, "Line %s" % n, "L%s" % n])
'''
exec(LINE_SRC)


def _safe(n, others):
    s = str(n)
    for m in others:
        t = str(m)
        if m != n and (t.startswith(s) or t.endswith(s) or s.startswith(t) or s.endswith(t)):
            return False
    return True


def build_log(n, slug, path, svc, fills, key, decoys, mode, nlines, prompt, desc, readme, level="ERROR"):
    """fills: INFO message templates ({r} 4-digit, {h} hex, {i} counter); decoys: (level, msg) near-misses."""
    for attempt in range(100):
        r = random.Random(n * 977 + attempt)
        k = 1 if mode == "unique" else 3
        npos = k + 2 * len(decoys)
        pos = sorted(r.sample(range(30, nlines - 15), npos))
        r.shuffle(pos)
        tpos = sorted(pos[:k])
        dpos = pos[k:]
        want = tpos[0] if mode == "first" else tpos[-1] if mode == "last" else tpos[0]
        if not _safe(want + 1, [p + 1 for p in pos]):
            continue
        break
    else:
        raise SystemExit("no layout for %d" % n)
    place = {p: (level, key + (" attempt=%d" % (j + 1) if k > 1 else "")) for j, p in enumerate(tpos)}
    for j, p in enumerate(dpos):
        place[p] = decoys[j % len(decoys)]
    out = []
    sec = 8 * 3600 + r.randint(0, 3000)
    for i in range(nlines):
        sec += r.randint(1, 9)
        ts = "2026-10-%02d %02d:%02d:%02d" % (3 + sec // 86400, (sec // 3600) % 24, (sec // 60) % 60, sec % 60)
        if i in place:
            lv, msg = place[i]
        else:
            lv = "WARN" if r.random() < 0.04 else "INFO"
            msg = r.choice(fills).format(r=r.randint(1000, 9999), h="%06x" % r.getrandbits(24), i=i)
            if lv == "WARN":
                msg = "slow response from peer after %dms: %s" % (r.randint(800, 2900), msg)
        out.append("%s %-5s %s %s" % (ts, lv, svc, msg))
    text = "\n".join(out) + "\n"
    hits = [i + 1 for i, l in enumerate(out) if key in l]
    assert len(hits) == k and hits[0] == tpos[0] + 1, (n, hits)
    ans = hits[0] if mode != "last" else hits[-1]
    forms_ = lineforms(ans)
    big = len(text.encode()) > 65536
    cid = "log-%d" % n
    write_case(
        cid, desc=desc, task_type="locate_error", family="fam-log-b10d-%s-01" % slug, level="L2" if big else "L1", ref_calls=1,
        traps=["TR-DECOY"] + (["TR-TRUNC"] if big else []),
        decoys=dict({"TR-DECOY": [p + 1 for p in dpos][:3]}, **({"TR-TRUNC": "UNKNOWN"} if big else {})),
        axes=["LNG", "OBS"] if big else ["OBS"], case_expect=MAXREAD,
        files={path: text, "README.md": readme},
        turns=[{"prompt": prompt, "expect": {"output_contains_any": forms_, "required_tools": ["search_text"], "max_output_chars": 400}}],
        verify=LOGV.replace("@R@", repr(readme.split()[0])).replace("@P@", repr(path)).replace("@K@", repr(key)).replace("@M@", repr(mode)),
        notes=LOGN % (key, mode, ans, ans, ans),
    )
    return cid, ans


LOGV = "import json\n" + LINE_SRC + '''
case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith(@R@)
lines = case["files"][@P@].splitlines()
KEY, MODE = @K@, @M@
hits = [i + 1 for i, l in enumerate(lines) if KEY in l]
n = hits[-1] if MODE == "last" else hits[0]
assert (len(hits) == 1) == (MODE == "unique")
print(json.dumps({"expected_contains_any": lineforms(n)}))
'''

LOGN = '''
## Traps
- 日志里有只差一两个词的相似行（别的对象、别的状态、检查/重试类提及），按关键词模糊找容易落到它们头上；目标短语是 `%s`（模式 %s）。
- 文件大多超过 read_file 的 64 KiB 上限，整读不完整，也不该靠数行。

## Reference solution
1. search_text 搜完整短语，结果自带行号；按题面要求取最先（或最后、唯一）一处：第 %d 行。
终答一句话：目标事件在第 %d 行。判据：任一行号写法（第 N 行 / N 行 / line N 等）；用过 search_text；read_file 最多 1 次。
答案 %d。

## Why the answer is unique
完整短语只出现在预期的那几行，题面指定取第一次 / 最后一次 / 唯一一次，因此行号唯一。
'''


# ---- log locating (log-8430..8444)
L = build_log
L(8430, "paygwfailover", "logs/payment-gw.log", "payment-gw",
  ["accepted charge id={h} amount={r}", "heartbeat ok peer=acq-{r}", "settled batch {i} items={r}"],
  "switched traffic to standby acquirer acq-b", [("WARN", "failover threshold reached for acquirer acq-a count=3"), ("INFO", "standby acquirer acq-b health check passed"), ("INFO", "switched traffic back to primary acquirer acq-a")],
  "unique", 1250, "支付网关日志 logs/payment-gw.log 里，把流量切到备用收单行 acq-b 的那条记录在第几行？", "Locate the single failover-switch line in a payment gateway log among similar health-check and switch-back lines",
  "支付网关日志，一天一个文件。\n")
L(8431, "greenhousefan", "logs/greenhouse-ctl.log", "greenhouse-ctl",
  ["zone {r} temperature {r} sample stored", "irrigation valve v{r} idle", "sensor {h} calibrated"],
  "emergency vent opened zone=C4", [("WARN", "emergency vent threshold near zone=C4"), ("INFO", "emergency vent opened zone=C3"), ("INFO", "emergency vent closed zone=C4")],
  "first", 900, "In logs/greenhouse-ctl.log, on which line does the emergency vent open for zone C4 for the first time?", "Find the first emergency-vent opening for one zone where other zones and a close event look similar",
  "Greenhouse controller log.\n")
L(8432, "edgepurge", "logs/cdn-edge.log", "cdn-edge",
  ["served /asset/{h}.js status=200 bytes={r}", "cache hit key={h}", "origin fetch /img/{h}.png ms={r}"],
  "purge job 7731 finished", [("INFO", "purge job 7731 started"), ("INFO", "purge job 7730 finished"), ("WARN", "purge job 7731 queue depth high")],
  "unique", 1700, "CDN 边缘节点日志 logs/cdn-edge.log 里，清缓存任务 7731 结束（finished）的那一行是第几行？", "Locate the finish line of one purge job when its start and neighbouring-job lines look alike",
  "CDN 边缘节点日志。\n")
L(8433, "hl7ack", "logs/hl7-interface.log", "hl7-bridge",
  ["ADT^A01 forwarded msgid={h}", "ORU^R01 queued msgid={h}", "ack received msgid={h} code=AA"],
  "NACK from lab system msgid=5F21A9", [("INFO", "ack received msgid=5F21A9 code=AA"), ("WARN", "NACK from radiology system msgid=5F21A9"), ("ERROR", "NACK from lab system msgid=5F21A8")],
  "unique", 780, "Which line of logs/hl7-interface.log records the NACK from the lab system for message 5F21A9?", "Locate a NACK line for one message id where a different system and a neighbouring id also NACK",
  "Hospital HL7 interface engine log.\n")
L(8434, "scannerjam", "logs/sorter-scan.log", "sorter-12",
  ["parcel {h} scanned gate={r}", "belt speed {r}mm/s stable", "label read ok code={h}"],
  "belt jam detected at lane 6", [("WARN", "belt jam suspected at lane 6"), ("INFO", "belt jam cleared at lane 6"), ("ERROR", "belt jam detected at lane 5")],
  "last", 1500, "分拣线日志 logs/sorter-scan.log 里，6 号道最后一次检测到卡带（belt jam detected）是在第几行？", "Find the last jam-detected line for lane 6 among warnings, clears and another lane",
  "分拣机扫描日志。\n")
L(8435, "gamematch", "logs/match-server.log", "match-svc",
  ["player {h} joined queue region=eu", "lobby {r} filled in {r}ms", "player {h} left lobby {r}"],
  "season rollover applied season=14", [("INFO", "season rollover scheduled season=14"), ("INFO", "season rollover applied season=13"), ("WARN", "season rollover lock wait season=14")],
  "unique", 2000, "In logs/match-server.log, where is the line saying the season 14 rollover was applied?", "Locate the applied-rollover line for a given season among scheduled, older-season and lock-wait lines",
  "Matchmaking server log.\n")
L(8436, "metervoltage", "logs/meter-gateway.log", "meter-gw",
  ["meter {h} reading {r}kWh uploaded", "concentrator c{r} sync ok", "tariff table v{r} loaded"],
  "meter 00A7F2 over-voltage alarm cleared", [("ERROR", "meter 00A7F2 over-voltage alarm raised"), ("INFO", "meter 00A7F3 over-voltage alarm cleared"), ("WARN", "meter 00A7F2 voltage drift")],
  "unique", 640, "智能电表网关日志 logs/meter-gateway.log 里，00A7F2 号电表过压告警解除（cleared）的记录在第几行？", "Locate the alarm-cleared line of one smart meter beside raised and neighbour-meter lines",
  "智能电表集中器网关日志。\n")
L(8437, "libraryhold", "logs/library-circ.log", "circ-desk",
  ["checkout item={h} patron={r}", "return item={h} shelf={r}", "renewal ok item={h}"],
  "hold expired for item B-20417", [("INFO", "hold placed for item B-20417"), ("INFO", "hold expired for item B-20471"), ("WARN", "hold expiry soon for item B-20417")],
  "unique", 450, "Which line of logs/library-circ.log shows that the hold on item B-20417 expired?", "Locate the hold-expired line for one item with placed, near-id and warning lines around it",
  "Library circulation desk log.\n")
L(8438, "ridedispatch", "logs/dispatch.log", "dispatch",
  ["driver {h} location update zone={r}", "order {r} matched driver {h}", "surge multiplier zone={r} 1.{r}"],
  "driver pool exhausted zone=Z9", [("WARN", "driver pool low zone=Z9"), ("WARN", "driver pool exhausted zone=Z8"), ("INFO", "driver pool replenished zone=Z9")],
  "first", 1100, "网约车调度日志 logs/dispatch.log 里，Z9 区第一次出现运力耗尽（driver pool exhausted）是在第几行？", "Find the first pool-exhausted line for zone Z9 among low, replenished and other-zone lines",
  "网约车调度服务日志。\n")
L(8439, "transcodefail", "logs/transcoder.log", "transcode",
  ["segment {r} encoded bitrate={r}k", "job {h} progress {r}/9999", "thumbnail {h} written"],
  "job 9c41aa failed: codec init error", [("WARN", "job 9c41aa retry scheduled after codec warning"), ("ERROR", "job 9c41ab failed: codec init error"), ("INFO", "job 9c41aa completed after retry")],
  "unique", 1400, "In logs/transcoder.log, which line reports that job 9c41aa failed with a codec init error?", "Locate the failure line of one transcoding job among retry, completion and neighbour-job failures",
  "Video transcoder log.\n")
L(8440, "timetablepub", "logs/timetable.log", "timetable",
  ["room {r} slot assigned teacher={h}", "conflict check pass class={r}", "export page {r} ok"],
  "timetable v12 published", [("INFO", "timetable v12 draft saved"), ("INFO", "timetable v11 published"), ("WARN", "timetable v12 publish blocked by conflict")],
  "last", 520, "排课系统日志 logs/timetable.log 里，v12 课表最后一次发布成功（published）是在第几行？", "Find the last publish line of timetable v12 among drafts, blocked attempts and the older version",
  "排课系统日志。\n")
L(8441, "checkinqueue", "logs/checkin-kiosk.log", "kiosk",
  ["passenger {h} checked in seat={r}", "boarding pass {h} printed", "bag tag {h} issued"],
  "kiosk K07 offline", [("WARN", "kiosk K07 paper low"), ("ERROR", "kiosk K70 offline"), ("INFO", "kiosk K07 online")],
  "last", 1850, "Which line is the last time kiosk K07 went offline in logs/checkin-kiosk.log?", "Find the last offline line of one check-in kiosk among paper warnings, online messages and a similarly named kiosk",
  "Airport check-in kiosk log.\n")
L(8442, "indexrebuild", "logs/search-indexer.log", "indexer",
  ["doc {h} indexed shard={r}", "segment merge {r} done", "refresh took {r}ms"],
  "full reindex completed index=products_v3", [("INFO", "full reindex started index=products_v3"), ("INFO", "full reindex completed index=products_v2"), ("WARN", "full reindex slow index=products_v3")],
  "unique", 330, "搜索索引服务日志 logs/search-indexer.log 里，products_v3 全量重建完成（completed）是哪一行？", "Locate the completed line of a full reindex for one index among started, older-index and slow lines",
  "搜索索引服务日志。\n")
L(8443, "irrigationvalve", "logs/irrigation.log", "irrig-ctl",
  ["valve {r} status closed", "soil moisture {r} reading stored", "pump p{r} rpm stable"],
  "pump p3 dry-run protection tripped", [("WARN", "pump p3 dry-run risk detected"), ("ERROR", "pump p2 dry-run protection tripped"), ("INFO", "pump p3 dry-run protection reset")],
  "first", 1000, "灌溉控制器日志 logs/irrigation.log 里，3 号泵第一次触发干转保护（dry-run protection tripped）在第几行？", "Find the first dry-run trip of pump p3 among risk warnings, resets and another pump",
  "灌溉控制器日志。\n")
L(8444, "nightbatch", "logs/batch-runner.log", "batch",
  ["step {i} processed rows={r}", "checkpoint {h} written", "file part-{r}.dat merged"],
  "job eod-settlement exited code=137", [("INFO", "job eod-settlement started"), ("ERROR", "job eod-reconcile exited code=137"), ("WARN", "job eod-settlement memory high")],
  "unique", 1600, "夜间批处理日志 logs/batch-runner.log 里，eod-settlement 任务以退出码 137 结束的那一行是第几行？", "Locate the exit-137 line of the settlement batch job beside a sibling job with the same code",
  "夜间批处理日志。\n")


# ---------------------------------------------------------------- code / config locating
STEMS = ["norm", "scale", "clamp", "blend", "decay", "round", "bucket", "shift", "weight", "trim", "pad", "merge", "split", "probe", "tally"]
CAMEL = lambda s: "".join(w.capitalize() for w in s.split("_"))
# lang -> dict(pfx: definition-line prefix, fill(ident,k,g): block, old(ident): deprecated twin, call(ident, wrapper): call site,
#              ident(stem, nn): filler identifier, head/foot: file frame, cmt: comment marker)
LANGS = {
    "py": dict(pfx="def %s(", ident=lambda st, nn: "%s_%02d" % (st, nn), cmt="#",
               fill=lambda f, k, g: ["", "", "def %s(value, rate=1.%d):" % (f, k), "    if value is None:", "        return 0.0", "    base = float(value) * rate", "    if base < %d:" % (k + 3), "        return round(base, 2)", "    return round(base * %.2f, 2)" % g],
               old=lambda nm: ["", "", "def %s_v1(value):" % nm, "    # deprecated, kept for old callers", "    return float(value or 0)"],
               call=lambda nm, w: ["", "", "def %s(row):" % w, "    return %s(row[\"value\"])" % nm], head=['"""Helpers."""', "", "import math", ""], foot=[]),
    "go": dict(pfx="func %s(", ident=lambda st, nn: "%s%02d" % (st.capitalize(), nn), cmt="//",
               fill=lambda f, k, g: ["", "func %s(v float64) float64 {" % f, "\tif v < %d {" % (k + 3), "\t\treturn v", "\t}", "\treturn v * %.2f" % g, "}"],
               old=lambda nm: ["", "// Deprecated: use the new version.", "func %sOld(v float64) float64 {" % nm, "\treturn v", "}"],
               call=lambda nm, w: ["", "func %s(v float64) float64 {" % w, "\treturn %s(v)" % nm, "}"], head=["package pricing", "", 'import "math"', "", "var _ = math.Floor"], foot=[]),
    "ts": dict(pfx="export function %s(", ident=lambda st, nn: "%s%02d" % (st, nn), cmt="//",
               fill=lambda f, k, g: ["", "export function %s(v: number): number {" % f, "  if (v < %d) {" % (k + 3), "    return v;", "  }", "  return Math.round(v * %.2f);" % g, "}"],
               old=lambda nm: ["", "/** @deprecated use the new version */", "export function %sLegacy(v: number): number {" % nm, "  return v;", "}"],
               call=lambda nm, w: ["", "export function %s(v: number): number {" % w, "  return %s(v);" % nm, "}"], head=["import { clamp } from './util';", ""], foot=[]),
    "java": dict(pfx="    static int %s(", ident=lambda st, nn: "%s%02d" % (st, nn), cmt="    //",
                 fill=lambda f, k, g: ["", "    static int %s(int v) {" % f, "        if (v < %d) {" % (k + 3), "            return v;", "        }", "        return (int) (v * %.2f);" % g, "    }"],
                 old=lambda nm: ["", "    @Deprecated", "    static int %sOld(int v) {" % nm, "        return v;", "    }"],
                 call=lambda nm, w: ["", "    static int %s(int v) {" % w, "        return %s(v);" % nm, "    }"], head=["package com.shop.pricing;", "", "public class Rules {"], foot=["}"]),
}


def _mk_filler(L_, r, st_i):
    st = STEMS[st_i[0] % len(STEMS)]
    st_i[0] += 1
    return L_["fill"](L_["ident"](st, st_i[0]), r.randint(1, 9), r.uniform(0.8, 1.9))


def _verify_code(path, pfx, name, RD):
    return CODEV.replace("@R@", repr(RD[0])).replace("@P@", repr(path)).replace("@X@", repr(pfx % name)).replace("@N@", repr(name))


def build_code(n, slug, lang, path, sibling, name, nlines, comments, wrappers, prompt, desc, readme):
    L_ = LANGS[lang]
    for attempt in range(100):
        r = random.Random(n * 7919 + attempt)
        st_i = [attempt]
        blocks = []
        total = len(L_["head"]) + len(L_["foot"])
        while total < nlines:
            b = _mk_filler(L_, r, st_i)
            blocks.append(b)
            total += len(b)
        idx = r.sample(range(2, len(blocks) - 2), 7)
        tb, lb, c1, c2, w1, w2 = idx[:6]
        blocks[tb] = L_["fill"](name, 3, 1.25)
        blocks[lb] = L_["old"](name)
        for ci, text in ((c1, comments[0]), (c2, comments[1])):
            blocks[ci] = blocks[ci][:1] + [L_["cmt"] + " " + text] + blocks[ci][1:]
        for wi, w in ((w1, wrappers[0]), (w2, wrappers[1])):
            blocks[wi] = L_["call"](name, w)
        lines = list(L_["head"])
        for b in blocks:
            lines += b
        lines += L_["foot"]
        hit = [i + 1 for i, l in enumerate(lines) if name in l]
        defs = [i + 1 for i, l in enumerate(lines) if l.startswith(L_["pfx"] % name)]
        if len(defs) == 1 and _safe(defs[0], hit):
            break
    else:
        raise SystemExit("no layout for %d" % n)
    text = "\n".join(lines) + "\n"
    sib = list(L_["head"]) + L_["fill"](name, 5, 1.1) + [""] + L_["fill"](_unused(L_), 2, 1.3) + L_["foot"]
    ans = defs[0]
    big = len(text.encode()) > 65536
    write_case(
        "code-%d" % n, desc=desc, task_type="locate_definition", family="fam-code-b10d-%s-01" % slug, level="L2" if big else "L1", ref_calls=1,
        traps=["TR-DECOY"] + (["TR-TRUNC"] if big else []),
        decoys=dict({"TR-DECOY": [h for h in hit if h != ans][:3]}, **({"TR-TRUNC": "UNKNOWN"} if big else {})),
        axes=["LNG", "OBS"] if big else ["OBS"], case_expect=MAXREAD,
        files={path: text, sibling: "\n".join(sib) + "\n", "README.md": readme},
        turns=[{"prompt": prompt, "expect": {"output_contains_any": lineforms(ans), "required_tools": ["search_text"], "max_output_chars": 400}}],
        verify=_verify_code(path, L_["pfx"], name, readme.split()),
        notes=CODEN % (name, ans, ans, ans),
    )
    return ans


def _unused(L_):
    return L_["ident"]("spare", 99)


CODEV = "import json\n" + LINE_SRC + '''
case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith(@R@)
lines = case["files"][@P@].splitlines()
d = [i + 1 for i, l in enumerate(lines) if l.startswith(@X@)]
assert len(d) == 1
print(json.dumps({"expected_contains_any": lineforms(d[0])}))
'''

CODEN = '''
## Traps
- `%s` 在同一文件里还有注释提及、调用处和带 v1 / Old / Legacy 后缀的弃用旧实现；兄弟文件里还有一个同名函数。只有主文件里那一行以完整签名开头。

## Reference solution
1. search_text 搜 `<定义关键字> <函数名>(`（限定题面给的文件路径），结果自带行号：第 %d 行。
终答一句话：定义在第 %d 行（注释、调用处、旧实现和兄弟文件的同名函数都不是）。判据：任一行号写法；用过 search_text；read_file 最多 1 次。答案 %d。

## Why the answer is unique
题面限定了文件，文件内只有一行以完整定义签名开头。
'''


C = build_code
# ---- code locating (code-8400..8409, 8413, 8414); config keys are code-8410..8412 below
C(8400, "latefee", "py", "billing/fees.py", "billing/legacy_fees.py", "compute_late_fee", 780,
  ["TODO: compute_late_fee should honour the grace days", "see compute_late_fee for the rounding rule"], ["quote_row", "preview_row"],
  "billing/fees.py 里 compute_late_fee 这个函数是从第几行开始定义的？", "Locate the current definition of a late-fee function beside a v1 twin, comments, callers and a sibling-file twin", "图书馆滞纳金计费模块。\n")
C(8401, "rotatekey", "py", "security/keys.py", "security/keys_old.py", "rotate_signing_key", 1350,
  ["rotate_signing_key must run before the nightly export", "rotate_signing_key is idempotent per day"], ["nightly_job", "manual_job"],
  "On which line of security/keys.py is rotate_signing_key defined?", "Locate a key-rotation function definition beside comments, wrappers, a deprecated v1 and a sibling-file twin", "Signing key management helpers.\n")
C(8402, "resolveshard", "go", "router/shard.go", "router/shard_legacy.go", "ResolveShard", 920,
  ["ResolveShard falls back to shard 0 when the tenant is unknown", "callers should cache the result of ResolveShard"], ["RouteA", "RouteB"],
  "In router/shard.go, which line defines the ResolveShard function?", "Locate a Go shard-resolver function beside an Old twin, comments, wrappers and a sibling-file twin", "Tenant shard router.\n")
C(8403, "cartsummary", "ts", "web/cart.ts", "web/cart-v1.ts", "buildCartSummary", 640,
  ["buildCartSummary skips gift-wrap rows", "TODO: buildCartSummary should include shipping"], ["renderCart", "renderMini"],
  "购物车前端 web/cart.ts 里，buildCartSummary 函数定义在第几行？", "Locate a TypeScript cart-summary function beside a Legacy twin, comments, wrappers and a sibling-file twin", "购物车前端模块。\n")
C(8404, "bulkdiscount", "java", "src/Rules.java", "src/RulesTest.java", "applyBulkDiscount", 1100,
  ["applyBulkDiscount only applies above 50 units", "note: applyBulkDiscount replaced the old tier table"], ["quoteA", "quoteB"],
  "Which line of src/Rules.java is applyBulkDiscount defined on?", "Locate a Java discount method beside an Old twin, comments, wrappers and a test-file twin", "Pricing rules class.\n")
C(8405, "waybillcode", "py", "express/waybill.py", "express/waybill_compat.py", "parse_waybill_code", 1800,
  ["parse_waybill_code returns None for test codes", "字段含义见 parse_waybill_code 的实现"], ["handle_scan", "handle_batch"],
  "快递面单模块 express/waybill.py 里，parse_waybill_code 的定义在第几行？", "Locate a waybill parser definition beside a v1 twin, comments, wrappers and a compat-file twin", "快递面单解析。\n")
C(8406, "debouncesearch", "ts", "ui/search.ts", "ui/search.test.ts", "debounceSearch", 410,
  ["debounceSearch waits 250ms by default", "TODO: debounceSearch needs a cancel handle"], ["onInput", "onPaste"],
  "Where in ui/search.ts is debounceSearch defined? Give the line number.", "Locate a debounce helper beside a Legacy twin, comments, wrappers and a test-file twin", "Search box helpers.\n")
C(8407, "normalizesku", "go", "catalog/sku.go", "catalog/sku_import.go", "NormalizeSku", 1550,
  ["NormalizeSku upper-cases and trims the code", "迁移完成后删掉旧的 NormalizeSku 调用"], ["ImportA", "ImportB"],
  "商品目录 catalog/sku.go 里 NormalizeSku 函数从第几行开始？", "Locate a SKU normaliser beside an Old twin, comments, wrappers and an import-file twin", "商品目录工具。\n")
C(8408, "mergeroster", "py", "hr/roster.py", "hr/roster_export.py", "merge_roster_rows", 330,
  ["merge_roster_rows keeps the latest team field", "merge_roster_rows assumes sorted input"], ["load_a", "load_b"],
  "On which line is merge_roster_rows defined in hr/roster.py?", "Locate a roster merge function beside a v1 twin, comments, wrappers and an export-file twin", "HR roster helpers.\n")
C(8409, "roundtip", "java", "src/TipRules.java", "src/TipRulesTest.java", "roundTipAmount", 2000,
  ["roundTipAmount rounds half up to the cent", "餐厅小费规则：先调用 roundTipAmount 再分摊"], ["splitA", "splitB"],
  "餐厅小费规则 src/TipRules.java 里，roundTipAmount 方法定义在第几行？", "Locate a Java tip-rounding method beside an Old twin, comments, wrappers and a test-file twin", "小费分摊规则。\n")
C(8413, "escalateticket", "py", "helpdesk/escalate.py", "helpdesk/escalate_sla.py", "escalate_ticket", 560,
  ["escalate_ticket pages the on-call after 3 attempts", "工单升级走 escalate_ticket，不要手工改状态"], ["tick_a", "tick_b"],
  "工单系统 helpdesk/escalate.py 里 escalate_ticket 的 def 在第几行？", "Locate a ticket-escalation function beside a v1 twin, comments, wrappers and an SLA-file twin", "工单升级模块。\n")
C(8414, "leaseterm", "ts", "lease/terms.ts", "lease/terms.spec.ts", "formatLeaseTerm", 1250,
  ["formatLeaseTerm prints months below 24, years above", "TODO: formatLeaseTerm should localise units"], ["showA", "showB"],
  "What line is formatLeaseTerm defined on in lease/terms.ts?", "Locate a lease-term formatter beside a Legacy twin, comments, wrappers and a spec-file twin", "Lease term display helpers.\n")


def build_ini(n, slug, path, sibling, key, val, nlines, comments, prompt, desc, readme, zhsec):
    for attempt in range(100):
        r = random.Random(n * 4441 + attempt)
        lines = ["# service settings", ""]
        sec = 0
        while len(lines) < nlines:
            sec += 1
            lines += ["[%s_%02d]" % (zhsec, sec)]
            for j in range(r.randint(4, 8)):
                lines.append("%s_%02d = %s" % (r.choice(STEMS), sec * 10 + j, r.choice(["on", "off", str(r.randint(1, 900)), "%d.%d" % (r.randint(0, 9), r.randint(0, 9))])))
            lines.append("")
        idx = r.sample(range(5, len(lines) - 5), 4)
        tgt = idx[0]
        for ci, text in ((idx[1], comments[0]), (idx[2], comments[1])):
            lines[ci] = "# " + text
        lines[idx[3]] = "%s_legacy = 3" % key
        lines[tgt] = "%s = %s" % (key, val)
        hit = [i + 1 for i, l in enumerate(lines) if key in l]
        if lines.count(lines[tgt]) == 1 and _safe(tgt + 1, hit):
            break
    else:
        raise SystemExit("no layout for %d" % n)
    text = "\n".join(lines) + "\n"
    sib = "# dev overrides\n\n[%s_01]\n%s = %s\n" % (zhsec, key, "1")
    ans = tgt + 1
    big = len(text.encode()) > 65536
    write_case(
        "code-%d" % n, desc=desc, task_type="locate_definition", family="fam-code-b10d-%s-01" % slug, level="L2" if big else "L1", ref_calls=1,
        traps=["TR-DECOY"] + (["TR-TRUNC"] if big else []),
        decoys=dict({"TR-DECOY": [h for h in hit if h != ans][:3]}, **({"TR-TRUNC": "UNKNOWN"} if big else {})),
        axes=["LNG", "OBS"] if big else ["OBS"], case_expect=MAXREAD,
        files={path: text, sibling: sib, "README.md": readme},
        turns=[{"prompt": prompt, "expect": {"output_contains_any": lineforms(ans), "required_tools": ["search_text"], "max_output_chars": 400}}],
        verify=CODEV.replace("@R@", repr(readme.split()[0])).replace("@P@", repr(path)).replace("@X@", repr("%s = " % key)),
        notes=CODEN.replace("`%s` 在同一文件里还有注释提及、调用处和带 v1 / Old / Legacy 后缀的弃用旧实现；兄弟文件里还有一个同名函数。只有主文件里那一行以完整签名开头。",
                            "`%s` 在同一文件里还有注释提及和 `%s_legacy` 旧键；兄弟配置文件里还有同名键。只有主文件里那一行以 `%s = ` 开头。") % (key, key, key, ans, ans, ans)
        if False else CODEN2 % (key, key, key, ans, ans, ans),
    )
    return ans


CODEN2 = '''
## Traps
- `%s` 在同一文件里还有注释提及和 `%s_legacy` 旧键；兄弟配置文件里还有同名键。只有主文件里一行以 `%s = ` 开头。

## Reference solution
1. search_text 搜 `<键名> =`（限定题面给的文件路径），结果自带行号：第 %d 行。
终答一句话：配置项在第 %d 行。判据：任一行号写法；用过 search_text；read_file 最多 1 次。答案 %d。

## Why the answer is unique
题面限定了文件，文件内只有一行以 `键名 = ` 开头。
'''

I = build_ini
I(8410, "retrybudget", "conf/gateway.ini", "conf/gateway.dev.ini", "retry_budget", "7", 1450,
  ["retry_budget was 3 before the October change", "raise retry_budget only together with the timeout"],
  "In conf/gateway.ini, on which line is the retry_budget setting?", "Locate one config key in a long ini file beside a legacy key, comments and a dev-override twin", "Gateway settings.\n", "route")
I(8411, "maxuploadmb", "配置/站点.ini", "配置/站点.测试.ini", "max_upload_mb", "256", 880,
  ["max_upload_mb 以前是 64，十月调整过", "改 max_upload_mb 之前先通知存储组"],
  "站点配置 配置/站点.ini 里，max_upload_mb 这个配置项在第几行？", "Locate an upload-limit key in a long ini file beside a legacy key, comments and a test-override twin", "站点配置文件。\n", "site")
I(8412, "sessionttl", "配置/会话.ini", "配置/会话.预发.ini", "session_ttl_min", "45", 2000,
  ["session_ttl_min 默认 30，安全评审后改成现在的值", "不要在这里临时调大 session_ttl_min"],
  "会话服务配置 配置/会话.ini 里，session_ttl_min 设在第几行？", "Locate a session TTL key in a very long ini file beside a legacy key, comments and a staging-override twin", "会话服务配置。\n", "sess")
