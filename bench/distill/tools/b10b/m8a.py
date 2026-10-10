"""b10b (v1.4 §3.8) M8: arithmetic goes to the calculator. 50 cases:
nt-8046..8065, tab-8058..8067, cfg-8054..8063, doc-8041..8050.

One helper C() builds each case. The answer is computed once from a `calc` snippet
that is also embedded in verify.py, so generator and verifier cannot drift.
"""
import csv
import io
import json
import re
import textwrap
from common import revised
write_case = revised({"tab-8062": "S5：题面去掉「一共开机多少小时」——同时问两个量又要求「只回数字」，三遍老师都回了两个数（83.4 11050.50），纯数字判据必挂。"})

CALC = ["calculator"]


def fmt(v, nd):
    if nd == 0:
        return sorted({"%d" % v, "{:,}".format(int(v))})
    s = {"%.*f" % (nd, v), "{:,.{}f}".format(v, nd)}
    s |= {x.rstrip("0").rstrip(".") for x in list(s)}
    return sorted(s)


FMT_SRC = '''
def fmt(v, nd):
    if nd == 0:
        return sorted({"%d" % v, "{:,}".format(int(v))})
    s = {"%.*f" % (nd, v), "{:,.{}f}".format(v, nd)}
    s |= {x.rstrip("0").rstrip(".") for x in list(s)}
    return sorted(s)
'''


def run_calc(calc, case):
    ns = {"case": case, "csv": csv, "io": io, "json": json, "re": re}
    exec(calc, ns)
    return ns["v"]


def C(cid, slug, desc, prompt, calc, nd, final, steps, why, checks, files=None, num=False,
      traps=(), decoy=None, ttype="unit_convert", level=None, calls=1, zh=True, maxc=400, suf=""):
    level = "L1" if traps else "L0"
    files = files or {}
    calc = textwrap.dedent(calc).strip("\n")
    case = {"files": files, "turns": [{"prompt": prompt}]}
    raw = run_calc(calc, case)
    assert abs((raw * 10 ** nd) % 1 - 0.5) > 1e-4, (cid, raw)
    v = round(raw, nd)
    pre = cid.split("-")[0]
    if pre == "cfg":
        ttype = "read_effective"
    if pre == "doc":
        ttype = "policy_lookup"
    forms = [f + suf for f in fmt(v, nd)]
    plain = "%.*f" % (nd, v) if nd else "%d" % v
    ex = final.replace("@V@", plain)
    if num:
        expect = {"expected_number": v, "tolerance": 0.5 * 10 ** -nd if nd else 0.01, "required_tools": CALC}
        assert "只回数字" in prompt or "number only" in prompt, cid
        crit = "expected_number %s，调用过 calculator" % plain if zh else "expected_number %s, calculator used" % plain
        pv = "{\"expected_number\": v}"
    else:
        expect = {"output_contains_any": forms, "required_tools": CALC, "max_output_chars": maxc}
        assert any(f in ex for f in forms), cid
        crit = "包含 %s（千分位 / 去尾零写法均可），调用过 calculator" % plain if zh else \
            "contains %s (thousands separator / trailing zeros optional), calculator used" % plain
        pv = "{\"expected_contains_any\": [f + SUF for f in fmt(v, ND)]}"
    assert v >= 100 or nd > 0, (cid, v)
    for k in checks:
        assert k in prompt + "".join(files.values()), (cid, k)
    dec = None
    if decoy:
        dec = round(run_calc(textwrap.dedent(decoy).strip("\n"), case), nd)
        assert dec != v
    verify = ('import csv\nimport io\nimport json\nimport re\n' + FMT_SRC +
              '\ncase = json.load(open("case.json"))\n'
              'text = case["turns"][0]["prompt"] + "".join(case["files"].values())\n'
              'for k in %r:\n    assert k in text\n' % (list(checks) + [next(l for l in t.splitlines() if l.strip()) for t in files.values()],) +
              'ND = %d\nSUF = %r\n' % (nd, suf) + calc + '\nv = round(v, ND)\nprint(json.dumps(%s))\n' % pv)
    trap_h = ("- " + "；".join(traps[1]) if zh else "- " + "; ".join(traps[1])) if traps else ("- None." if not zh else "- 无。")
    notes = ("\n## Traps\n%s\n\n## Reference solution\n%s\n%s：%s。判据：%s。\n\n## Why the answer is unique\n%s\n" %
             (trap_h, steps.replace("@V@", plain), "终答示例" if zh else "Final answer", ex, crit, why))
    write_case(
        cid, desc=desc, task_type=ttype, family="fam-%s-b10b-%s-01" % (pre, slug), level=level, ref_calls=calls,
        axes={"TR-RULEFILE": ["CHN"], "TR-DECOY": ["OBS"]}[traps[0]] if traps else [], files=files,
        traps=[traps[0]] if traps else [], decoys={traps[0]: fmt(dec, nd)[0]} if (traps and dec is not None) else {},
        turns=[{"prompt": prompt, "expect": expect}], verify=verify, notes=notes)


# ===================================================================== nt (20)
C("nt-8046", "containerlb", "Convert a container payload in tonnes to pounds with a non-integer factor, bare number",
  "一个货柜实际装了 24.8 吨货，换算成磅是多少？按 1 吨 = 2204.62 磅算，四舍五入取整，只回数字。",
  "v = 24.8 * 2204.62", 0, "@V@", "1. calculator：24.8 * 2204.62 → 取整。",
  "换算系数与取整方式由题面给定。", ["24.8 吨", "2204.62"], num=True)

C("nt-8047", "batterymj", "Convert a battery bank's stored energy from kWh to megajoules across 12 units",
  "A battery bank has 12 units that each store 6.4 kWh. How many megajoules is the whole bank, using 1 kWh = 3.6 MJ? Round to two decimals.",
  "v = 12 * 6.4 * 3.6", 2, "The bank holds @V@ MJ (12 x 6.4 kWh x 3.6).",
  "1. calculator: 12 * 6.4 * 3.6 = @V@.", "Count, per-unit energy and factor are all given.", ["12 units", "6.4 kWh"], zh=False)

C("nt-8048", "infusiondrops", "Convert an infusion pump rate from mL/h to drops per minute at 20 drops per mL",
  "输液泵设定流速是 125 mL/h，滴系数 20 滴/mL，折合每分钟多少滴？保留两位小数。",
  "v = 125 * 20 / 60", 2, "折合约 @V@ 滴/分钟（125 × 20 ÷ 60）。",
  "1. calculator：125 * 20 / 60，precision 2 → @V@。", "滴系数、小时到分钟的换算与保留位数都明确。", ["125 mL/h", "20 滴/mL"])

C("nt-8049", "tankliters", "Convert a fuel tank from US gallons to litres, bare number",
  "A tank holds 1,850 US gallons. How many litres is that if 1 US gallon = 3.78541 litres? Round to two decimals and reply with the number only.",
  "v = 1850 * 3.78541", 2, "@V@", "1. calculator: 1850 * 3.78541 = @V@.",
  "Factor and rounding are fixed by the prompt.", ["1,850 US gallons", "3.78541"], num=True, zh=False)

C("nt-8050", "paddyyield", "Estimate total rice harvest in tonnes from per-mu yield and area",
  "稻田一共 12.8 亩，平均亩产 462 公斤，总产量大概是多少吨？保留两位小数。",
  "v = 12.8 * 462 / 1000", 2, "总产量约 @V@ 吨（12.8 亩 × 462 公斤 ÷ 1000）。",
  "1. calculator：12.8 * 462 / 1000，precision 2 → @V@。", "面积、亩产和公斤到吨的换算都已给定。", ["12.8 亩", "462 公斤"])

C("nt-8051", "royaltyprint", "Royalty on net sales of a book at list price with a decimal royalty rate",
  "这本书定价 68 元，实际销售了 7360 册，版税率 7.5%，按定价算，作者能拿到多少版税？",
  "v = 7360 * 68 * 0.075", 0, "作者版税共 @V@ 元（7360 × 68 × 7.5%）。",
  "1. calculator：7360 * 68 * 0.075 = @V@。", "销量、定价、税率均已给定，版税基数为定价。", ["68 元", "7360 册", "7.5%"])

C("nt-8052", "foodcostpct", "Food cost as a percentage of sales to one decimal",
  "Last month our kitchen spent $14,820 on ingredients against $52,340 in food sales. What is the food cost percentage? Round to one decimal place.",
  "v = 14820 / 52340 * 100", 1, "Food cost was @V@% of sales (14,820 / 52,340).",
  "1. calculator: 14820 / 52340 * 100, precision 1 = @V@.", "Both amounts are given; the ratio is cost over sales.",
  ["$14,820", "$52,340"], zh=False, suf="%")

C("nt-8053", "ingredientrise", "Percentage rise in monthly ingredient spend, bare number",
  "食材月支出从 3.84 万元涨到了 4.31 万元，涨幅是百分之几？保留一位小数，只回数字，不带百分号。",
  "v = (4.31 - 3.84) / 3.84 * 100", 1, "@V@", "1. calculator：(4.31 - 3.84) / 3.84 * 100，precision 1 → @V@。",
  "涨幅 = 增量 ÷ 原值，保留一位由题面给定。", ["3.84 万元", "4.31 万元"], num=True)

C("nt-8054", "pueoverhead", "Share of facility power that is non-IT overhead, from total and IT load",
  "A data hall draws 1,842 kW in total, of which 1,316 kW is IT equipment. What percentage of the total is non-IT overhead? Round to two decimals.",
  "v = (1842 - 1316) / 1842 * 100", 2, "Overhead is @V@% of the total ((1,842 - 1,316) / 1,842).",
  "1. calculator: (1842 - 1316) / 1842 * 100, precision 2 = @V@.", "Overhead is total minus IT, divided by total.",
  ["1,842 kW", "1,316 kW"], zh=False)

C("nt-8055", "pvcapfactor", "Capacity factor of a solar plant from nameplate MW and annual GWh",
  "一座光伏电站装机 6.8 MW，去年发电 8.76 GWh，容量系数是多少？一年按 8760 小时，结果用百分数，保留一位小数。",
  "v = 8.76 * 1000 / (6.8 * 8760) * 100", 1, "容量系数约 @V@%（8.76 GWh ÷ (6.8 MW × 8760 h)）。",
  "1. calculator：8.76 * 1000 / (6.8 * 8760) * 100，precision 1 → @V@（先把 GWh 换成 MWh）。", "GWh 到 MWh 的换算与全年小时数都是确定的。",
  ["6.8 MW", "8.76 GWh"], suf="%")

C("nt-8056", "coldstoreprorate", "Prorate an annual cold-storage rent for a part-year on a 365-day basis",
  "冷库年租金 218,400 元，我们只租了 47 天，按一年 365 天折算，应付多少元？保留两位小数。",
  "v = 218400 * 47 / 365", 2, "按 47 天折算应付 @V@ 元（218400 × 47 ÷ 365）。",
  "1. calculator：218400 * 47 / 365，precision 2 → @V@。", "年租金、天数和 365 天口径都给定。", ["218,400 元", "47 天"])

C("nt-8057", "charterhire", "Charter hire pro rata for 9 days 14 hours, bare number",
  "A vessel is chartered at $18,750 per day, pro rata by the hour. We used it for 9 days and 14 hours. What do we owe in dollars? Round to two decimals and reply with the number only.",
  "v = 18750 * (9 + 14 / 24)", 2, "@V@", "1. calculator: 18750 * (9 + 14/24) = @V@.",
  "Daily rate and the 24-hour day are fixed; pro rata is stated.", ["$18,750", "9 days and 14 hours"], num=True, zh=False)

C("nt-8058", "scannerpower", "Monthly electricity cost of an imaging scanner from daily hours, kW and tariff",
  "一台 CT 机每天开机 7.5 小时，开机时平均功率 3.8 kW，电价 0.86 元/度，这个月开机 26 天，电费是多少元？保留两位小数。",
  "v = 7.5 * 3.8 * 0.86 * 26", 2, "本月电费约 @V@ 元（7.5 × 3.8 × 0.86 × 26）。",
  "1. calculator：7.5 * 3.8 * 0.86 * 26，precision 2 → @V@。", "时长、功率、电价、天数都由题面给定。", ["7.5 小时", "3.8 kW", "0.86 元"])

C("nt-8059", "craneshifts", "Crane rental hours across full days and half days at an hourly rate",
  "吊车按小时计费，每小时 385 元。这个月整天作业 9 天，每天 7.75 小时；另有 3 个半天，每个 4.25 小时。一共该付多少元？",
  "v = 385 * (9 * 7.75 + 3 * 4.25)", 2, "吊车费共 @V@ 元（385 × (9×7.75 + 3×4.25) = 385 × 82.5）。",
  "1. calculator：385 * (9 * 7.75 + 3 * 4.25) = @V@。", "总工时 82.5 小时，单价固定。", ["385 元", "7.75 小时", "4.25 小时"])

C("nt-8060", "dripwater", "Total drip-irrigation water over an 18-day run, converted to tonnes",
  "温室的滴灌系统有 24 个出水口，每个每小时出水 2.3 升，每天开 5.5 小时，连续开 18 天。一共用了多少吨水？按 1 吨 = 1000 升，保留两位小数。",
  "v = 24 * 2.3 * 5.5 * 18 / 1000", 2, "共用水约 @V@ 吨（24 × 2.3 × 5.5 × 18 ÷ 1000）。",
  "1. calculator：24 * 2.3 * 5.5 * 18 / 1000，precision 2 → @V@。", "出水口数、流量、时长、天数和换算系数均给定。", ["24 个出水口", "2.3 升"])

C("nt-8061", "printquote", "Print job quote: unit print cost, lamination, plates and freight summed",
  "Please total this print quote: 4,200 copies at $3.47 each, cover lamination at $0.18 per copy, a one-off plate fee of $640, and freight of $412.50. What is the grand total in dollars? Reply with the number only.",
  "v = 4200 * 3.47 + 4200 * 0.18 + 640 + 412.50", 2, "@V@", "1. calculator: 4200 * 3.47 + 4200 * 0.18 + 640 + 412.50 = @V@.",
  "All four cost items are listed.", ["4,200 copies", "$3.47", "$412.50"], num=True, zh=False)

C("nt-8062", "banquettotal", "Banquet bill with per-table food and drinks plus a 10% service charge, bare number",
  "周末婚宴 18 桌，每桌菜品 1288 元、酒水 236.5 元，另加 10% 服务费。账单一共多少元？只回数字。",
  "v = 18 * (1288 + 236.5) * 1.1", 2, "@V@", "1. calculator：18 * (1288 + 236.5) * 1.1 = @V@。",
  "服务费按菜品与酒水之和计，题面没有其他项目。", ["18 桌", "1288 元", "10% 服务费"], num=True)

C("nt-8063", "feederkwh", "Three feeder readings summed and priced per kWh",
  "Feeder readings this month: A 12,480.5 kWh, B 9,962.25 kWh, C 14,031.75 kWh. At $0.1137 per kWh, what is the total energy cost? Round to two decimals.",
  "v = (12480.5 + 9962.25 + 14031.75) * 0.1137", 2, "The three feeders cost $@V@ in total (36,474.5 kWh x $0.1137).",
  "1. calculator: (12480.5 + 9962.25 + 14031.75) * 0.1137 = @V@.", "Three readings and one tariff.", ["12,480.5", "9,962.25", "0.1137"], zh=False)

C("nt-8064", "supplybundle", "Medical supply order with a stackable spend-and-save discount per 1500 yuan",
  "科室要采购导管 36 支，每支 48.5 元；敷料 120 片，每片 6.35 元；手套 15 盒，每盒 42.8 元。供应商活动是每满 1500 元减 100 元，可以叠加。实付多少元？",
  "gross = 36 * 48.5 + 120 * 6.35 + 15 * 42.8\nv = gross - (gross // 1500) * 100", 2,
  "原价合计 3150 元，满 1500 减 100 叠加两次，实付 @V@ 元。",
  "1. calculator：36 * 48.5 + 120 * 6.35 + 15 * 42.8 = 3150。\n2. 3150 里有两个 1500，减 200 → @V@。", "叠加规则明确：按 floor(原价/1500) 次减免。",
  ["36 支", "120 片", "每满 1500 元减 100 元"], decoy="v = 36 * 48.5 + 120 * 6.35 + 15 * 42.8 - 100")

C("nt-8065", "palletfreight", "Freight by weight for three pallets plus a percentage fuel surcharge on freight",
  "Three pallets weigh 412.5 kg, 388.75 kg and 455.2 kg. Freight is $0.62 per kg and a fuel surcharge of 8.5% applies to the freight charge. What is the total? Round to two decimals.",
  "v = (412.5 + 388.75 + 455.2) * 0.62 * 1.085", 2, "The total is $@V@ (1,256.45 kg at $0.62 plus 8.5% fuel surcharge).",
  "1. calculator: (412.5 + 388.75 + 455.2) * 0.62 * 1.085 = @V@.", "Surcharge applies to freight only, and there are no other charges.",
  ["412.5 kg", "$0.62", "8.5%"], zh=False)

# ===================================================================== tab (10)
import random  # noqa: E402


def table(header, rows):
    return ",".join(header) + "\n" + "".join(",".join(str(c) for c in r) + "\n" for r in rows)


rng = random.Random(805801)
rows = [("CT%05d" % (40100 + i), rng.choice(["HX-2611", "HX-2612", "HX-2613"]), rng.randrange(18000, 61000, 10) + rng.choice([0, 5]))
        for i in range(36)]
C("tab-8058", "portgross", "Sum one voyage's container gross weights in pounds and convert to kilograms",
  "码头记录里 HX-2612 这个船次的集装箱一共有多重？按 1 磅 = 0.45359237 公斤换成公斤，保留一位小数。记录在 堆场/过磅记录.csv。",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["堆场/过磅记录.csv"])))
  v = sum(int(r["毛重(磅)"]) for r in rows if r["船次"] == "HX-2612") * 0.45359237
  ''', 1, "HX-2612 船次集装箱总重约 @V@ 公斤（磅数合计 × 0.45359237）。",
  "1. data_query：堆场/过磅记录.csv，filter 船次=HX-2612，sum 毛重(磅)。\n2. calculator：合计 × 0.45359237，precision 1 → @V@。",
  "船次过滤精确，换算系数与位数由题面给定。", ["HX-2612", "0.45359237"],
  files={"堆场/过磅记录.csv": table(["箱号", "船次", "毛重(磅)"], rows)}, ttype="policy_calc", level="L1", calls=3, maxc=400)

rng = random.Random(805901)
rows = [("2026-09-%02d" % (d + 1), site, "%.2f" % rng.uniform(210, 560)) for d in range(30) for site in ("North", "South")]
C("tab-8059", "solarmj", "Sum one site's September solar output in kWh and convert to megajoules, bare number",
  "In pv/daily-output.csv, how much energy did the North array produce in September in megajoules? Use 1 kWh = 3.6 MJ, round to one decimal, number only.",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["pv/daily-output.csv"])))
  v = sum(float(r["kwh"]) for r in rows if r["site"] == "North") * 3.6
  ''', 1, "@V@", "1. data_query: pv/daily-output.csv, filter site=North, sum kwh.\n2. calculator: total * 3.6, precision 1 = @V@.",
  "One site, one month, one factor.", ["North", "3.6 MJ"], files={"pv/daily-output.csv": table(["date", "site", "kwh"], rows)},
  num=True, ttype="policy_calc", level="L1", calls=3, zh=False)

rng = random.Random(806001)
titles = ["潮汐笔记", "山海旧事", "云上食堂", "玻璃花园", "夜航船", "纸上星图"]
rows = []
for t in titles:
    for dealer in ("北辰书店", "知行图书"):
        sent = rng.randrange(800, 3200, 20)
        rows.append((t, dealer, sent, int(sent * rng.uniform(0.04, 0.19))))
C("tab-8060", "returnrate", "Overall return rate for one distributor: total returns over total shipped, in percent",
  "发行台账 发行/退货统计.csv 里，知行图书 这家经销商整体的退货率是多少？用退货总册数除以发货总册数，保留一位小数，用百分数。",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["发行/退货统计.csv"])))
  s = [r for r in rows if r["经销商"] == "知行图书"]
  v = sum(int(r["退货册数"]) for r in s) / sum(int(r["发货册数"]) for r in s) * 100
  ''', 1, "知行图书整体退货率约 @V@%（退货总册数 ÷ 发货总册数）。",
  "1. data_query：filter 经销商=知行图书，sum 发货册数 与 退货册数。\n2. calculator：退货合计 / 发货合计 * 100，precision 1 → @V@。",
  "口径是总量比总量，不是各书退货率平均。", ["知行图书", "退货总册数除以发货总册数"],
  files={"发行/退货统计.csv": table(["书名", "经销商", "发货册数", "退货册数"], rows)}, ttype="policy_calc", level="L1", calls=3,
  decoy='''
  rows = list(csv.DictReader(io.StringIO(case["files"]["发行/退货统计.csv"])))
  s = [r for r in rows if r["经销商"] == "知行图书"]
  v = sum(int(r["退货册数"]) / int(r["发货册数"]) for r in s) / len(s) * 100
  ''', traps=("TR-DECOY", ["各书退货率求平均会得到另一个数"]), suf="%")

rng = random.Random(806101)
rows = []
for lot in ("A", "B", "C", "D"):
    for k in range(3):
        n = rng.randrange(900, 2400, 10)
        rows.append(("LOT-%s%d" % (lot, k + 1), n, int(n * rng.uniform(0.006, 0.031))))
C("tab-8061", "syringereject", "Reject rate across all lots of one syringe line, from a lot table",
  "In qc/lot-results.csv, lots whose IDs start with LOT-C are the 3 mL syringe line. What is that line's overall reject rate (total rejected over total inspected), in percent, to two decimals?",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["qc/lot-results.csv"])))
  s = [r for r in rows if r["lot"].startswith("LOT-C")]
  v = sum(int(r["rejected"]) for r in s) / sum(int(r["inspected"]) for r in s) * 100
  ''', 2, "The LOT-C line rejected @V@% of inspected units (rejected total / inspected total).",
  "1. data_query: filter lot starts with LOT-C, sum inspected and rejected.\n2. calculator: rejected / inspected * 100, precision 2 = @V@.",
  "Pooled rate over the three LOT-C lots.", ["LOT-C", "qc/lot-results.csv"],
  files={"qc/lot-results.csv": table(["lot", "inspected", "rejected"], rows)}, ttype="policy_calc", calls=3, zh=False, suf="%")

rng = random.Random(806201)
rows = [("EQ-%02d" % e, "2026-09-%02d" % d, "%.1f" % rng.choice([3.5, 4.0, 4.5, 6.25, 7.75, 8.0, 9.5])) for e in (3, 7, 9) for d in range(1, 15)]
C("tab-8062", "rentalhours", "Hourly rental fee for one scanner over a fortnight, summed from a log, bare number",
  "设备台账 设备/开机时长.csv 里 EQ-07 在 9 月 1 日到 14 日的开机时长按每小时 132.5 元计租金，租金总共多少元？只回数字。",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["设备/开机时长.csv"])))
  v = sum(float(r["开机小时"]) for r in rows if r["设备"] == "EQ-07") * 132.5
  ''', 2, "@V@", "1. data_query：设备=EQ-07 求 开机小时 之和。\n2. calculator：合计 × 132.5，precision 2 → @V@。",
  "表内每台设备正好 14 天，设备编号精确。", ["EQ-07", "132.5 元"], files={"设备/开机时长.csv": table(["设备", "日期", "开机小时"], rows)},
  num=True, ttype="policy_calc", calls=3)

rng = random.Random(806301)
rows = [("Z%s" % z, "2026-09-%02d" % d, rng.randrange(35, 190), "%.1f" % rng.uniform(8.5, 14.5)) for z in "ABC" for d in range(1, 11)]
C("tab-8063", "zonewater", "Total irrigation water for one zone: minutes times flow, converted to cubic metres",
  "From irrigation/log.csv, how many cubic metres of water did zone ZB use in total? Each row gives minutes run and flow in litres per minute; 1 m3 = 1000 L. Round to two decimals.",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["irrigation/log.csv"])))
  v = sum(int(r["minutes"]) * float(r["l_per_min"]) for r in rows if r["zone"] == "ZB") / 1000
  ''', 2, "Zone ZB used @V@ m3 (sum of minutes x L/min, divided by 1000).",
  "1. read_file irrigation/log.csv (30 rows) or data_query with an expression for minutes*l_per_min on zone ZB.\n2. calculator: sum of products / 1000, precision 2 = @V@.",
  "Each row is a separate run with its own flow rate, so products are summed row by row.", ["zone ZB", "1 m3 = 1000 L"],
  files={"irrigation/log.csv": table(["zone", "date", "minutes", "l_per_min"], rows)}, ttype="policy_calc", calls=3, zh=False)

rng = random.Random(806401)
cats = {"水产": [("基围虾", 38.5), ("鲈鱼", 26.8), ("扇贝", 41.2)], "干货": [("香菇", 72.0), ("木耳", 88.5)], "蔬菜": [("西兰花", 9.6), ("娃娃菜", 5.8)]}
rows = []
for i in range(14):
    c = rng.choice(list(cats))
    n, p = rng.choice(cats[c])
    rows.append(("2026-09-%02d" % (i + 2), c, n, "%.1f" % rng.uniform(4, 26), p))
C("tab-8064", "seafoodpo", "Total cost of one category in a purchase log: kg times unit price per kg, summed",
  "后厨采购单 采购/9月进货.csv 里，水产类这个月一共花了多少钱？数量是公斤数，单价是元/公斤，保留两位小数。",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["采购/9月进货.csv"])))
  v = sum(float(r["数量(kg)"]) * float(r["单价(元/kg)"]) for r in rows if r["类别"] == "水产")
  ''', 2, "水产类 9 月进货合计 @V@ 元（逐行 数量 × 单价 再求和）。",
  "1. data_query：filter 类别=水产，逐行 数量×单价 求和（或读表后 calculator 逐行相乘相加）。\n2. calculator 得 @V@。",
  "类别过滤精确，金额逐行相乘再加总。", ["水产类", "元/公斤"],
  files={"采购/9月进货.csv": table(["日期", "类别", "品名", "数量(kg)", "单价(元/kg)"], rows)}, ttype="policy_calc", calls=3)

rng = random.Random(806501)
rows = [(t, f, rng.randrange(300, 2600, 10), "%.2f" % rng.choice([16.9, 24.5, 29.0, 38.0, 45.5])) for t in ("T-101", "T-102", "T-103") for f in ("hardcover", "paperback")]
C("tab-8065", "royaltyrate", "Royalty on hardcover sales where the README defines royalty as a share of a share of list price",
  "Using sales/q3.csv and the README in that folder, how much royalty do we owe on hardcover copies this quarter? Give dollars, two decimals.",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["sales/q3.csv"])))
  v = sum(int(r["copies"]) * float(r["list_price"]) for r in rows if r["format"] == "hardcover") * 0.55 * 0.12
  ''', 2, "Hardcover royalty is $@V@: list-price revenue x 55% net receipts x 12%.",
  "1. Read sales/README.md: net receipts = 55% of list; royalty = 12% of net receipts.\n2. data_query: hardcover rows, sum copies*list_price.\n3. calculator: sum * 0.55 * 0.12, precision 2 = @V@.",
  "README fixes both percentages; hardcover filter is exact.", ["hardcover", "README"],
  files={"sales/q3.csv": table(["title", "format", "copies", "list_price"], rows),
         "sales/README.md": "# Q3 royalty basis\n\nNet receipts = 55% of list price. Royalty = 12% of net receipts, paid on every format.\n"},
  ttype="policy_calc", calls=4, zh=False, traps=("TR-RULEFILE", ["the 55% and 12% appear only in the README; list-price revenue alone is the wrong base"]),
  decoy='''
  rows = list(csv.DictReader(io.StringIO(case["files"]["sales/q3.csv"])))
  v = sum(int(r["copies"]) * float(r["list_price"]) for r in rows if r["format"] == "hardcover")
  ''')

rng = random.Random(806601)
rows = [("2026-09-%02d" % d, int(rng.uniform(900, 1500) * (1.0 if d <= 7 else 1.07))) for d in range(1, 15)]
C("tab-8066", "inverterweek", "Week-over-week growth of inverter output between two weeks in a daily log, bare number",
  "逆变器日志 电站/日发电量.csv 里，9 月 8 日到 14 日这一周的发电量比 9 月 1 日到 7 日增长了百分之几？保留一位小数，只回数字，不带百分号。",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["电站/日发电量.csv"])))
  a = sum(int(r["发电量kWh"]) for r in rows[:7])
  b = sum(int(r["发电量kWh"]) for r in rows[7:14])
  v = (b - a) / a * 100
  ''', 1, "@V@", "1. 读表（或 data_query）分别求 9/1–9/7 与 9/8–9/14 的发电量合计。\n2. calculator：(后一周 - 前一周) / 前一周 * 100，precision 1 → @V@。",
  "两周各 7 天，增长率以前一周为基数。", ["9 月 8 日到 14 日", "只回数字"],
  files={"电站/日发电量.csv": table(["日期", "发电量kWh"], rows)}, num=True, ttype="policy_calc", calls=3)

rng = random.Random(806702)
rows = [("SHP-%04d" % (3100 + i), rng.choice(["SZX-LAX", "SZX-RTM", "NGB-HAM"]), rng.randrange(260, 980)) for i in range(24)]
C("tab-8067", "transitdays", "Average transit time in days for one lane from hours in a shipment table",
  "In freight/transit.csv the transit column is in hours. What is the average transit time for lane NGB-HAM in days (24 hours per day)? Round to two decimals.",
  '''
  rows = list(csv.DictReader(io.StringIO(case["files"]["freight/transit.csv"])))
  s = [int(r["transit_hours"]) for r in rows if r["lane"] == "NGB-HAM"]
  v = sum(s) / len(s) / 24
  ''', 2, "NGB-HAM shipments average @V@ days of transit (mean hours / 24).",
  "1. data_query: lane=NGB-HAM, avg transit_hours (or sum and count).\n2. calculator: mean / 24, precision 2 = @V@.",
  "Mean over the lane's rows, then hours to days.", ["NGB-HAM", "24 hours per day"],
  files={"freight/transit.csv": table(["shipment", "lane", "transit_hours"], rows)}, ttype="policy_calc", calls=3, zh=False)

# ===================================================================== cfg (10)
C("cfg-8054", "granaryfans", "Total air volume of grain-store ventilation fans from the per-fan flow, fan count and run hours in a config",
  "粮仓通风系统每次开机连续跑 7.2 小时，配置在 粮仓/通风.yaml。按配置里的风机台数和单台风量，这一次一共送风多少万立方米？保留两位小数。",
  '''
  t = case["files"]["粮仓/通风.yaml"]
  n = int(re.search(r"fan_count:\\s*(\\d+)", t).group(1))
  f = float(re.search(r"flow_m3_per_h:\\s*([\\d.]+)", t).group(1))
  v = n * f * 7.2 / 10000
  ''', 2, "一次开机共送风约 @V@ 万立方米（3 台 × 18500 m³/h × 7.2 h ÷ 10000）。",
  "1. read_file 粮仓/通风.yaml：fan_count 3，flow_m3_per_h 18500。\n2. calculator：3 * 18500 * 7.2 / 10000，precision 2 → @V@。",
  "台数和单台风量都在配置里，开机时长在题面。", ["7.2 小时", "粮仓/通风.yaml"],
  files={"粮仓/通风.yaml": "# 3 号仓通风\nfan_count: 3\nflow_m3_per_h: 18500\nmax_run_h: 12\nauto_stop_humidity_pct: 62\n"},
  ttype="policy_calc", calls=2)

C("cfg-8055", "cardfee", "Card processing fee with basis points and a fixed fee from a config",
  "Per payments/fees.toml, what is the total processing fee on one $482.60 card payment? Give dollars, two decimals.",
  '''
  t = case["files"]["payments/fees.toml"]
  bps = float(re.search(r"card_fee_bps\\s*=\\s*([\\d.]+)", t).group(1))
  fx = float(re.search(r"card_fixed_fee_usd\\s*=\\s*([\\d.]+)", t).group(1))
  v = 482.60 * bps / 10000 + fx
  ''', 2, "The fee is $@V@ (482.60 x 135 bps + $0.30 fixed).",
  "1. read_file payments/fees.toml: card_fee_bps = 135, card_fixed_fee_usd = 0.30.\n2. calculator: 482.60 * 135 / 10000 + 0.30 = @V@.",
  "Basis points are 1/10000; the fixed fee is added once per payment.", ["$482.60", "payments/fees.toml"],
  files={"payments/fees.toml": "[fees]\ncard_fee_bps = 135\ncard_fixed_fee_usd = 0.30\ntransfer_fee_bps = 25\nrefund_fee_usd = 0.00\n"},
  ttype="policy_calc", calls=2, zh=False)

C("cfg-8056", "defrostheat", "Monthly defrost-heater energy from daily cycle count, minutes per cycle and heater power in a config, bare number",
  "冷库的化霜参数在 冷库/化霜.ini。按配置里的每天次数、每次分钟数和加热功率，30 天一共耗多少度电？保留一位小数，只回数字。",
  '''
  t = case["files"]["冷库/化霜.ini"]
  n = int(re.search(r"cycles_per_day\\s*=\\s*(\\d+)", t).group(1))
  m = int(re.search(r"minutes_per_cycle\\s*=\\s*(\\d+)", t).group(1))
  kw = float(re.search(r"heater_kw\\s*=\\s*([\\d.]+)", t).group(1))
  v = n * m * 30 / 60 * kw
  ''', 1, "@V@", "1. read_file 冷库/化霜.ini：4 次/天，38 分钟/次，2.35 kW。\n2. calculator：4 * 38 * 30 / 60 * 2.35 = @V@。",
  "三项参数都在配置里，天数在题面。", ["30 天", "冷库/化霜.ini"],
  files={"冷库/化霜.ini": "[defrost]\ncycles_per_day = 4\nminutes_per_cycle = 38\nheater_kw = 2.35\nterminate_temp_c = 8\n"},
  num=True, ttype="policy_calc", calls=2)

C("cfg-8057", "solararray", "Total DC capacity of a solar plant from per-string panel counts and wattages in a config",
  "What is the plant's total DC capacity in kW according to solar/array.yaml? Each string lists its panel count and the watt rating of each panel. Round to two decimals.",
  '''
  t = case["files"]["solar/array.yaml"]
  pairs = re.findall(r"panels:\\s*(\\d+),\\s*watts:\\s*(\\d+)", t)
  v = sum(int(a) * int(b) for a, b in pairs) / 1000
  ''', 2, "The plant's DC capacity is @V@ kW (sum of panels x watts over the three strings, divided by 1000).",
  "1. read_file solar/array.yaml: strings (18, 545), (20, 550), (22, 540).\n2. calculator: (18*545 + 20*550 + 22*540) / 1000 = @V@.",
  "Three strings, all listed; the inverter limit line is not part of the DC sum.", ["solar/array.yaml", "kW"],
  files={"solar/array.yaml": "plant: ridge-2\nstrings:\n  - {id: S1, panels: 18, watts: 545}\n  - {id: S2, panels: 20, watts: 550}\n  - {id: S3, panels: 22, watts: 540}\ninverter_ac_limit_kw: 25\n"},
  ttype="policy_calc", calls=2, zh=False)

C("cfg-8058", "autoclavef", "Convert an autoclave sterilisation temperature from Fahrenheit in a config to Celsius",
  "灭菌锅的设定温度写在 灭菌/锅炉参数.yaml 里，是华氏度。换算成摄氏度是多少？保留一位小数。",
  '''
  t = case["files"]["灭菌/锅炉参数.yaml"]
  f = float(re.search(r"hold_temp_f:\\s*([\\d.]+)", t).group(1))
  v = (f - 32) * 5 / 9
  ''', 1, "保温温度 273 °F，折合约 @V@ °C（(273 − 32) × 5 ÷ 9）。",
  "1. read_file 灭菌/锅炉参数.yaml：hold_temp_f: 273。\n2. calculator：(273 - 32) * 5 / 9，precision 1 → @V@。",
  "配置里只有 hold_temp_f 一个温度字段需要换算。", ["华氏度", "灭菌/锅炉参数.yaml"],
  files={"灭菌/锅炉参数.yaml": "program: B-class\nhold_temp_f: 273\nhold_minutes: 4\ndry_minutes: 15\n"}, ttype="policy_calc", calls=2)

C("cfg-8059", "cranelb", "Convert a gantry crane's lift capacity from pounds in a config to metric tonnes, bare number",
  "Convert the lift capacity in port/crane.cfg to metric tonnes (1 lb = 0.45359237 kg). Round to two decimals and give the number only.",
  '''
  t = case["files"]["port/crane.cfg"]
  v = float(re.search(r"lift_capacity_lb\\s*=\\s*([\\d.]+)", t).group(1)) * 0.45359237 / 1000
  ''', 2, "@V@", "1. read_file port/crane.cfg: lift_capacity_lb = 88000.\n2. calculator: 88000 * 0.45359237 / 1000 = @V@.",
  "Only lift_capacity_lb is a mass in pounds; the spreader weight line is in kg and not used.", ["metric tonnes", "port/crane.cfg"],
  files={"port/crane.cfg": "lift_capacity_lb = 88000\nspreader_weight_kg = 9800\nboom_length_m = 42\n"}, num=True, calls=2, zh=False)

C("cfg-8060", "sheetwaste", "Total press sheets needed with a waste allowance percentage from a config",
  "这批书订单 18650 册，每册 7.5 个印张。印刷机的放数比例配置在 印刷/开机参数.yaml 里，按配置放数后一共要印多少印张？取整数。",
  '''
  t = case["files"]["印刷/开机参数.yaml"]
  w = float(re.search(r"waste_allowance_pct:\\s*([\\d.]+)", t).group(1))
  v = 18650 * 7.5 * (1 + w / 100)
  ''', 0, "按 3.5% 放数，一共要印 @V@ 印张（18650 × 7.5 × 1.035）。",
  "1. read_file 印刷/开机参数.yaml：waste_allowance_pct: 3.5。\n2. calculator：18650 * 7.5 * 1.035 → 取整 @V@。",
  "放数比例只在配置里，取整方式由题面指定。", ["18650 册", "7.5 个印张"],
  files={"印刷/开机参数.yaml": "waste_allowance_pct: 3.5\nmake_ready_sheets: 400\nmax_speed_sph: 9000\n"},
  traps=("TR-RULEFILE", ["放数比例只在配置里；不读配置直接乘 18650 × 7.5 会漏掉放数"]), decoy="v = 18650 * 7.5", calls=2)

C("cfg-8061", "genfuelcost", "Generator fuel cost for 30 days from burn rate and daily hours in a config and a price in the prompt",
  "The diesel generator settings are in site/genset.yaml. Using its fuel burn rate and daily run hours, what does fuel cost over 30 days at $1.38 per litre? Round to two decimals.",
  '''
  t = case["files"]["site/genset.yaml"]
  b = float(re.search(r"fuel_burn_lph:\\s*([\\d.]+)", t).group(1))
  h = float(re.search(r"daily_run_hours:\\s*([\\d.]+)", t).group(1))
  v = b * h * 30 * 1.38
  ''', 2, "Fuel over 30 days costs $@V@ (14.6 L/h x 9.5 h x 30 x $1.38).",
  "1. read_file site/genset.yaml: fuel_burn_lph 14.6, daily_run_hours 9.5.\n2. calculator: 14.6 * 9.5 * 30 * 1.38 = @V@.",
  "Both parameters are in the config; price and days are in the prompt.", ["site/genset.yaml", "$1.38"],
  files={"site/genset.yaml": "fuel_burn_lph: 14.6\ndaily_run_hours: 9.5\ntank_litres: 2000\nservice_interval_h: 250\n"}, calls=2, zh=False)

C("cfg-8062", "sterilefee", "Sterilisation service bill from batch sizes and a per-piece rate and base fee in a config, bare number",
  "供应室这个月送去外包灭菌的三批器械分别是 320 件、450 件、275 件。收费标准在 灭菌/外包费率.yaml，按配置里的单价和每批起步费算，应付多少元？只回数字。",
  '''
  t = case["files"]["灭菌/外包费率.yaml"]
  p = float(re.search(r"per_piece_yuan:\\s*([\\d.]+)", t).group(1))
  b = float(re.search(r"base_fee_per_batch_yuan:\\s*([\\d.]+)", t).group(1))
  v = (320 + 450 + 275) * p + 3 * b
  ''', 2, "@V@", "1. read_file 灭菌/外包费率.yaml：per_piece_yuan 0.85，base_fee_per_batch_yuan 120。\n2. calculator：(320 + 450 + 275) * 0.85 + 3 * 120 = @V@。",
  "起步费按批次收，单价按件收，三批三次。", ["320 件", "只回数字"],
  files={"灭菌/外包费率.yaml": "per_piece_yuan: 0.85\nbase_fee_per_batch_yuan: 120\nrush_surcharge_pct: 20\n"},
  num=True, calls=2, traps=("TR-RULEFILE", ["费率只在配置里；急件加价 20% 题面没提，不用"]), decoy="v = (320 + 450 + 275) * 0.85")

C("cfg-8063", "airfreightrate", "Air freight total with additive fuel and peak surcharges in a config",
  "运价表配置在 航空/运价.yaml。一票货 840 公斤，按配置的基础单价加上附加费，总运费是多少元？保留两位小数。",
  '''
  t = case["files"]["航空/运价.yaml"]
  r = float(re.search(r"base_rate_per_kg:\\s*([\\d.]+)", t).group(1))
  f = float(re.search(r"fuel_surcharge_pct:\\s*([\\d.]+)", t).group(1))
  k = float(re.search(r"peak_surcharge_pct:\\s*([\\d.]+)", t).group(1))
  v = 840 * r * (1 + (f + k) / 100)
  ''', 2, "总运费 @V@ 元：840 kg × 2.45 元/kg，再加 11.5% 燃油与 6% 旺季附加费（均按基础运费计，合计 +17.5%）。",
  "1. read_file 航空/运价.yaml：基础 2.45 元/kg，燃油 11.5%，旺季 6%，注释说明附加费相加后统一乘在基础运费上。\n2. calculator：840 * 2.45 * 1.175 = @V@。",
  "配置注释明确两项附加费相加（不是连乘）。", ["840 公斤", "航空/运价.yaml"],
  files={"航空/运价.yaml": "# 附加费均按基础运费计，两项相加后一并加收\nbase_rate_per_kg: 2.45\nfuel_surcharge_pct: 11.5\npeak_surcharge_pct: 6\nmin_charge: 180\n"},
  calls=2, traps=("TR-RULEFILE", ["附加费计法只在配置注释里；连乘 1.115×1.06 会得到不同的数"]), decoy="v = 840 * 2.45 * 1.115 * 1.06")

# ===================================================================== doc (10)
C("doc-8041", "franchisefee", "Franchise monthly fee: management fee plus brand fund as percentages of turnover from the contract text",
  "按 加盟/合同要点.md，本月门店营业额 182,600 元，应向总部缴纳的管理费和品牌基金一共多少元？保留两位小数。",
  '''
  t = case["files"]["加盟/合同要点.md"]
  a = float(re.search(r"管理费[^\\d]*([\\d.]+)%", t).group(1))
  b = float(re.search(r"品牌基金[^\\d]*([\\d.]+)%", t).group(1))
  v = 182600 * (a + b) / 100
  ''', 2, "本月应缴 @V@ 元：管理费 4.5% 加品牌基金 1.2%，共 5.7%，基数是营业额 182,600 元。",
  "1. read_file 加盟/合同要点.md：管理费 4.5%，品牌基金 1.2%，均以当月营业额为基数。\n2. calculator：182600 * (4.5 + 1.2) / 100 = @V@。",
  "两项比例都在合同要点里，基数相同。", ["182,600 元", "加盟/合同要点.md"],
  files={"加盟/合同要点.md": "# 加盟合同要点\n\n- 管理费：按当月营业额的 4.5% 收取。\n- 品牌基金：按当月营业额的 1.2% 收取，用于统一广告投放。\n- 装修翻新金：每三年一次，另行约定。\n"},
  ttype="policy_calc", calls=2, traps=("TR-RULEFILE", ["比例只在合同要点里；只算管理费会漏掉品牌基金"]), decoy="v = 182600 * 4.5 / 100")

C("doc-8042", "palletstorage", "Warehouse storage bill with a free period stated in the contract: pallets times billable days times rate",
  "Per contracts/warehouse-terms.md, what do we owe for storing 140 pallets for 23 days? Give dollars, two decimals.",
  '''
  t = case["files"]["contracts/warehouse-terms.md"]
  r = float(re.search(r"\\$([\\d.]+) per pallet per day", t).group(1))
  fr = int(re.search(r"first (\\d+) days", t).group(1))
  v = 140 * (23 - fr) * r
  ''', 2, "You owe $@V@: 140 pallets x (23 - 5 free days) x $0.85.",
  "1. read_file contracts/warehouse-terms.md: $0.85 per pallet per day, first 5 days free.\n2. calculator: 140 * (23 - 5) * 0.85 = @V@.",
  "The free period is stated in the terms; billable days are 18.", ["140 pallets", "23 days"],
  files={"contracts/warehouse-terms.md": "# Warehouse terms\n\nStorage is charged at $0.85 per pallet per day. The first 5 days of each stay are free of charge.\nHandling in and out is invoiced separately.\n"},
  ttype="policy_calc", calls=2, zh=False, traps=("TR-RULEFILE", ["the 5 free days are only in the terms; charging 23 days gives a different total"]), decoy="v = 140 * 23 * 0.85")

C("doc-8043", "scannerlease", "Equipment lease with a daily rate pro-rated by hour for the partial day, bare number",
  "租赁合同摘要在 租赁/超声设备合同.md。这台设备我们从周一用到下周日，共 6 天 19 小时，按合同的计费方式应付租金多少元？保留两位小数，只回数字。",
  '''
  t = case["files"]["租赁/超声设备合同.md"]
  d = float(re.search(r"日租金\\s*([\\d.]+)\\s*元", t).group(1))
  v = d * (6 + 19 / 24)
  ''', 2, "@V@", "1. read_file 租赁/超声设备合同.md：日租金 515 元，不足一天按小时折算（日租金 ÷ 24 × 小时数）。\n2. calculator：515 * (6 + 19/24) = @V@。",
  "不足一天部分按日租金 ÷ 24 逐小时计。", ["6 天 19 小时", "只回数字"],
  files={"租赁/超声设备合同.md": "# 超声设备租赁合同（摘要）\n\n- 日租金 515 元。\n- 不足一天的部分按小时折算：日租金 ÷ 24 × 实际小时数。\n- 押金 5000 元，归还验收后退还。\n"},
  num=True, ttype="policy_calc", calls=2, traps=("TR-RULEFILE", ["小时折算方式只在合同里；整天计 7 天会多收"]), decoy="v = 515 * 7")

C("doc-8044", "ppaescalate", "Power purchase cost: price per MWh with compounding annual escalation, consumption given in kWh",
  "Using ppa/summary.md, what is the cost of the 482,600 kWh we consumed in 2026? Round to two decimals, in dollars.",
  '''
  t = case["files"]["ppa/summary.md"]
  p = float(re.search(r"\\$([\\d.]+) per MWh", t).group(1))
  e = float(re.search(r"([\\d.]+)% per year", t).group(1))
  v = p * (1 + e / 100) ** 2 * 482600 / 1000
  ''', 2, "The 2026 cost is $@V@: $63.40/MWh escalated twice at 2.5% (2025, 2026), times 482.6 MWh.",
  "1. read_file ppa/summary.md: $63.40 per MWh in 2024, escalating 2.5% per year, compounding.\n2. calculator: 63.40 * 1.025^2 * 482.6 = @V@.",
  "Base year 2024, so 2026 has two compounding escalations; kWh to MWh divides by 1000.", ["482,600 kWh", "2026"],
  files={"ppa/summary.md": "# PPA summary\n\nEnergy price is $63.40 per MWh for calendar year 2024. The price escalates 2.5% per year, compounding, starting 1 January each year.\nCapacity charges are not covered here.\n"},
  ttype="policy_calc", calls=2, zh=False, traps=("TR-RULEFILE", ["price base year and compounding are only in the summary; using $63.40 flat is wrong"]), decoy="v = 63.40 * 482600 / 1000")

C("doc-8045", "propertybill", "Monthly property-management bill from per-square-metre rates and per-lift fees in a contract",
  "物业合同在 物业/服务合同.md。我们楼面积 12,480 平方米，有 2 台电梯，按合同这个月物业费一共多少元？",
  '''
  t = case["files"]["物业/服务合同.md"]
  a = float(re.search(r"基础服务费\\s*([\\d.]+)\\s*元", t).group(1))
  g = float(re.search(r"绿化养护\\s*([\\d.]+)\\s*元", t).group(1))
  e = float(re.search(r"电梯维保\\s*([\\d.]+)\\s*元", t).group(1))
  v = 12480 * (a + g) + 2 * e
  ''', 2, "本月物业费 @V@ 元：12,480 ㎡ × (8.6 + 0.9) + 2 台 × 2,150 元。",
  "1. read_file 物业/服务合同.md：基础服务费 8.6 元/㎡·月，绿化养护 0.9 元/㎡·月，电梯维保 2150 元/台·月。\n2. calculator：12480 * (8.6 + 0.9) + 2 * 2150 = @V@。",
  "三项收费口径在合同里，面积与台数在题面。", ["12,480 平方米", "2 台电梯"],
  files={"物业/服务合同.md": "# 物业服务合同（收费条款）\n\n1. 基础服务费 8.6 元/平方米·月。\n2. 绿化养护 0.9 元/平方米·月。\n3. 电梯维保 2150 元/台·月。\n4. 车位管理费另行约定，不计入本合同。\n"},
  ttype="policy_calc", calls=2, traps=("TR-RULEFILE", ["费率只在合同里；漏掉绿化或电梯会少算"]), decoy="v = 12480 * 8.6 + 2 * 2150")

C("doc-8046", "tieredroyalty", "Tiered author royalty on list price: 10 / 12.5 / 15 percent bands from the contract",
  "Per contracts/author-agreement.md, the book sold 11,800 copies at a list price of $24.95. What total royalty do we owe the author? Give dollars, two decimals.",
  '''
  t = case["files"]["contracts/author-agreement.md"]
  v = (5000 * 0.10 + 5000 * 0.125 + (11800 - 10000) * 0.15) * 24.95
  assert "10%" in t and "12.5%" in t and "15%" in t
  ''', 2, "The royalty is $@V@: (5,000 x 10% + 5,000 x 12.5% + 1,800 x 15%) x $24.95 list price.",
  "1. read_file contracts/author-agreement.md: 10% on copies 1-5,000; 12.5% on 5,001-10,000; 15% beyond 10,000, all on list price.\n2. calculator: (5000*0.10 + 5000*0.125 + 1800*0.15) * 24.95 = @V@.",
  "Bands are marginal (each rate applies only within its band) and the base is list price.", ["11,800 copies", "$24.95"],
  files={"contracts/author-agreement.md": "# Author agreement - royalties\n\nRoyalty is calculated on list price, in bands by cumulative copies sold:\n\n- 10% on copies 1 to 5,000\n- 12.5% on copies 5,001 to 10,000\n- 15% on copies above 10,000\n"},
  ttype="policy_calc", calls=2, zh=False, traps=("TR-RULEFILE", ["bands are marginal; applying 15% to all copies would overstate"]), decoy="v = 11800 * 24.95 * 0.15")

C("doc-8047", "overtimepay", "Overtime pay with different multipliers by day type and an hourly wage derived from monthly salary",
  "按 人事/加班规定.md，月薪 9860 元的员工这个月工作日加班 12 小时、休息日加班 8 小时，加班费一共多少元？保留两位小数。",
  '''
  t = case["files"]["人事/加班规定.md"]
  d = float(re.search(r"月薪\\s*÷\\s*([\\d.]+)\\s*÷\\s*8", t).group(1))
  v = 9860 / d / 8 * (12 * 1.5 + 8 * 2)
  ''', 2, "加班费共 @V@ 元：时薪 9860 ÷ 21.75 ÷ 8，工作日 1.5 倍 12 小时，休息日 2 倍 8 小时。",
  "1. read_file 人事/加班规定.md：时薪 = 月薪 ÷ 21.75 ÷ 8；工作日 1.5 倍，休息日 2 倍，法定假日 3 倍。\n2. calculator：9860 / 21.75 / 8 * (12*1.5 + 8*2) = @V@。",
  "折算天数与倍数都在规定里；没有法定假日加班。", ["9860 元", "休息日加班 8 小时"],
  files={"人事/加班规定.md": "# 加班费计算规定\n\n- 小时工资 = 月薪 ÷ 21.75 ÷ 8。\n- 工作日延时加班：1.5 倍小时工资。\n- 休息日加班：2 倍小时工资。\n- 法定节假日加班：3 倍小时工资。\n"},
  ttype="policy_calc", calls=2, traps=("TR-RULEFILE", ["21.75 天的折算口径只在规定里；按 30 天或 22 天折算会得到别的数"]), decoy="v = 9860 / 22 / 8 * (12 * 1.5 + 8 * 2)")

C("doc-8048", "reamweight", "Weight of paper reams from sheet size and basis weight in a printing spec, bare number",
  "印制规范在 印务/纸张规格.md。按规范里的整张纸尺寸、克重和每令张数，3 令纸一共多重，多少公斤？保留两位小数，只回数字。",
  '''
  t = case["files"]["印务/纸张规格.md"]
  w = float(re.search(r"(\\d+)\\s*×\\s*(\\d+)\\s*mm", t).group(1))
  h = float(re.search(r"(\\d+)\\s*×\\s*(\\d+)\\s*mm", t).group(2))
  g = float(re.search(r"(\\d+)\\s*g/㎡", t).group(1))
  n = int(re.search(r"每令\\s*(\\d+)\\s*张", t).group(1))
  v = 3 * n * (w / 1000) * (h / 1000) * g / 1000
  ''', 2, "@V@", "1. read_file 印务/纸张规格.md：整张 880 × 1230 mm，80 g/㎡，每令 500 张。\n2. calculator：3 * 500 * 0.88 * 1.23 * 80 / 1000 = @V@。",
  "面积（㎡）× 克重得单张克数，再乘张数换算成公斤。", ["3 令纸", "只回数字"],
  files={"印务/纸张规格.md": "# 正文纸规格\n\n- 整张尺寸 880 × 1230 mm。\n- 定量 80 g/㎡。\n- 每令 500 张。\n- 纤维方向：长纹。\n"},
  num=True, ttype="policy_calc", calls=2)

C("doc-8049", "demurrage", "Demurrage under a charter: hours over laytime, paid pro rata at a daily rate stated in the charter summary",
  "Charter summary is in charter/terms.md. The vessel spent 5 days 9 hours in port after notice of readiness. What demurrage do we owe? Give dollars, one decimal.",
  '''
  t = case["files"]["charter/terms.md"]
  lay = int(re.search(r"[Ll]aytime of (\\d+) hours", t).group(1))
  d = float(re.search(r"\\$([\\d,]+) per day", t).group(1).replace(",", ""))
  v = (5 * 24 + 9 - lay) * d / 24
  ''', 1, "Demurrage is $@V@: 57 hours over the 72-hour laytime, pro rata at $22,500 per day.",
  "1. read_file charter/terms.md: laytime of 72 hours, demurrage $22,500 per day pro rata.\n2. calculator: (5*24 + 9 - 72) * 22500 / 24 = @V@.",
  "Only time beyond laytime counts; pro rata means hourly proration.", ["5 days 9 hours", "charter/terms.md"],
  files={"charter/terms.md": "# Charter summary\n\nLaytime of 72 hours from notice of readiness. Demurrage is $22,500 per day, pro rata for part of a day, for time used beyond laytime.\nDespatch is not applicable on this voyage.\n"},
  ttype="policy_calc", calls=2, zh=False, traps=("TR-RULEFILE", ["laytime is only in the summary; charging all 129 hours gives a different number"]), decoy="v = (5 * 24 + 9) * 22500 / 24")

C("doc-8050", "mealfx", "Overseas meal allowance in USD per day converted at the monthly rate, first and last days at half",
  "出差补贴制度在 财务/差旅补贴.md。我这次出差 9 天，按制度算餐补，折合人民币是多少元？保留两位小数。",
  '''
  t = case["files"]["财务/差旅补贴.md"]
  u = float(re.search(r"(\\d+)\\s*美元/天", t).group(1))
  r = float(re.search(r"汇率\\s*([\\d.]+)", t).group(1))
  v = u * (7 + 2 * 0.5) * r
  ''', 2, "餐补合计 @V@ 元：45 美元/天 × (7 天 + 首尾两天各按一半 = 8 天) × 7.1862。",
  "1. read_file 财务/差旅补贴.md：餐补 45 美元/天，首尾两天按 50%，按当月汇率 7.1862 折人民币。\n2. calculator：45 * (7 + 2*0.5) * 7.1862 = @V@。",
  "9 天里 7 天足额、首尾 2 天各半，等效 8 天。", ["出差 9 天", "财务/差旅补贴.md"],
  files={"财务/差旅补贴.md": "# 境外差旅补贴\n\n- 餐补 45 美元/天；出发日与返回日只发 50%。\n- 折算汇率取当月财务公布汇率 7.1862（人民币/美元）。\n- 住宿凭票实报实销。\n"},
  ttype="policy_calc", calls=2, traps=("TR-RULEFILE", ["首尾半天与汇率只在制度里；9 天全额会多算"]), decoy="v = 45 * 9 * 7.1862")
