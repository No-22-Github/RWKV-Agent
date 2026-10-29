"""F1: the natural tool is not offered, a workaround with the remaining tools exists (35401-35420)."""
import random
from decimal import ROUND_HALF_UP, Decimal

from common import file_eq, has, mk, num, says


def lines(rows):
    return "".join(r + "\n" for r in rows)


def q2(x):
    return float(Decimal(str(x)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def build():
    # ---- 35401 invoice total with tax, no calculator, shell available
    rnd = random.Random(35401)
    items = [("HX-1042", "Torque driver set", 3, 48.90), ("HX-2210", "Cable duct 2m", 40, 3.75), ("HX-0987", "Safety goggles", 25, 6.40),
             ("HX-3315", "LED work lamp", 6, 27.15), ("HX-1180", "Anchor bolts M10", 120, 0.62), ("HX-4402", "Nitrile gloves box", 18, 9.95),
             ("HX-2761", "Tape measure 8m", 12, 11.30), ("HX-5023", "Cordless drill", 2, 139.00), ("HX-0634", "Marker pens 12pk", 9, 5.85),
             ("HX-3908", "Respirator filters", 30, 4.20), ("HX-1555", "Step ladder 3-tread", 4, 52.50), ("HX-2096", "Zip ties 500pc", 15, 7.45),
             ("HX-4871", "Extension lead 5m", 10, 14.60), ("HX-0312", "Spirit level 60cm", 5, 16.80)]
    f = {"billing/inv-halden-0924.csv": "sku,description,qty,unit_price\n" + lines("%s,%s,%d,%.2f" % r for r in items)}

    def t1(files):
        rows = [l.split(",") for l in files["billing/inv-halden-0924.csv"].strip().split("\n")[1:]]
        from decimal import Decimal, ROUND_HALF_UP
        s = sum(Decimal(r[2]) * Decimal(r[3]) for r in rows) * Decimal("1.0825")
        return {"numbers": [float(s.quantize(Decimal("0.01"), ROUND_HALF_UP))]}
    v = t1(f)["numbers"][0]
    mk("tab-35401", sub="F1", lang="en", tt="policy_calc", desc="Invoice total with sales tax when no calculator is offered (shell awk)",
       turns=[num("Can you total up the invoice in billing/inv-halden-0924.csv? Add 8.25% sales tax on top of the subtotal and give me the grand total to the cent.", v, 0.015)],
       files=f, must=["bash", "read_file"], never=["calculator"], truth=t1,
       ref=(["awk -F, 'NR>1{s+=$3*$4} END{printf \"%.2f\\n\", s*1.0825}' billing/inv-halden-0924.csv"], has("%.2f" % v)),
       ref_text="bash: awk -F, 'NR>1{s+=$3*$4} END{printf \"%%.2f\\n\", s*1.0825}' billing/inv-halden-0924.csv -> %.2f" % v,
       why="14 lines, qty*unit_price summed, times 1.0825. The answer is recomputed from the fixture in verify.py.", ref_calls=1)

    # ---- 35402 zh stationery order with 92 percent
    z = [("复印纸A4", 40, 23.5), ("中性笔", 120, 1.8), ("便利贴", 60, 3.2), ("订书钉", 30, 2.6), ("文件袋", 80, 1.15),
         ("白板笔", 36, 4.5), ("打孔机", 5, 28.0), ("回形针", 50, 1.4), ("计算器贴纸", 10, 6.75), ("档案盒", 24, 9.9)]
    f = {"采购/2026q3-办公耗材申购.csv": "品名,数量,单价\n" + lines("%s,%d,%s" % r for r in z)}

    def t2(files):
        rows = [l.split(",") for l in files["采购/2026q3-办公耗材申购.csv"].strip().split("\n")[1:]]
        from decimal import Decimal, ROUND_HALF_UP
        s = sum(Decimal(r[1]) * Decimal(r[2]) for r in rows) * Decimal("0.92")
        return {"numbers": [float(s.quantize(Decimal("0.01"), ROUND_HALF_UP))]}
    v = t2(f)["numbers"][0]
    mk("tab-35402", sub="F1", lang="zh", tt="policy_calc", desc="Order total with a 92% discount when no calculator is offered",
       turns=[num("把 采购/2026q3-办公耗材申购.csv 里每一项的金额（数量乘单价）加起来，再打 92 折，应付多少钱？保留两位小数。", v, 0.015)],
       files=f, must=["bash", "read_file"], never=["calculator"], truth=t2,
       ref=(["awk -F, 'NR>1{s+=$2*$3} END{printf \"%.2f\\n\", s*0.92}' 采购/2026q3-办公耗材申购.csv"], has("%.2f" % v)),
       ref_text="bash: awk -F, 'NR>1{s+=$2*$3} END{printf \"%%.2f\\n\", s*0.92}' 采购/2026q3-办公耗材申购.csv -> %.2f" % v,
       why="10 行，数量乘单价求和再乘 0.92，verify 从 fixture 重算。", ref_calls=1)

    # ---- 35403 en, two turns, no data_query: group by region
    rnd = random.Random(35403)
    regions = {"Northgate": 82000, "Eastmere": 91500, "Southfork": 70500, "Westbrook": 99000, "Highland": 64500}
    rows = []
    for mo in range(1, 7):
        for rg, base in regions.items():
            units = int(base / 41 + rnd.randint(-60, 60))
            rows.append("2026-%02d,%s,%d,%d" % (mo, rg, units, int(units * 41 + rnd.randint(-900, 900))))
    f = {"sales/regional-roll-2026h1.csv": "month,region,units,revenue\n" + lines(rows)}

    def t3(files):
        rows = [l.split(",") for l in files["sales/regional-roll-2026h1.csv"].strip().split("\n")[1:]]
        tot = {}
        for r in rows:
            tot[r[1]] = tot.get(r[1], 0) + int(r[3])
        best = max(tot, key=tot.get)
        return {"numbers": [float(tot[best]), float(round(tot[best] / 6))], "strings": [best]}
    g = t3(f)
    best, total = g["strings"][0], g["numbers"][0]
    t_1 = num("Which region brought in the most revenue in sales/regional-roll-2026h1.csv, and what was its six-month total?", total, 0.5, contains=[best])
    t_2 = num("And what was that region's average monthly revenue, to the nearest dollar?", g["numbers"][1], 0.51)
    mk("tab-35403", sub="F1", lang="en", tt="aggregate", desc="Group revenue by region over two turns when no table-query tool is offered (shell awk)",
       turns=[t_1, t_2], files=f, must=["bash"], never=["data_query"], truth=t3,
       ref=(["awk -F, 'NR>1{a[$2]+=$4} END{for(k in a) print k, a[k]}' sales/regional-roll-2026h1.csv"], has("%s %d" % (best, total))),
       ref_text="bash: awk -F, 'NR>1{a[$2]+=$4} END{for(k in a) print k, a[k]}' ... -> pick the max (%s, %d); turn 2 divides by 6." % (best, total),
       why="30 rows, 5 regions x 6 months; revenue summed per region in verify.py. Turn 2 depends on turn 1's region.", ref_calls=2,
       axes=("DEC", "OBS"))

    # ---- 35404 zh average salary for one grade, no data_query
    rnd = random.Random(35404)
    names = "陈思远 李沐阳 王若曦 赵子墨 刘雨桐 周景行 吴嘉怡 郑书航 孙晓彤 钱明哲 冯天宇 蒋梦琪 沈亦舟 韩晨曦 杨知远 朱可欣 秦牧之 许念安 何清扬 吕星辰 施文博 孔令仪 曹诗涵 严若水".split()
    grades = ["P5", "P6", "P6", "P7", "P5", "P6", "P6", "P7", "P5", "P6", "P8", "P6", "P5", "P7", "P6", "P6", "P5", "P7", "P6", "P8", "P5", "P6", "P7", "P6"]
    base = {"P5": 16500, "P6": 22000, "P7": 31000, "P8": 43000}
    rows = ["%s,%s,%d,%d" % (n, g, base[g] + rnd.randint(-14, 14) * 100, rnd.randint(2016, 2025)) for n, g in zip(names, grades)]
    f = {"人事/技术部薪资明细-2026.csv": "姓名,职级,月薪,入职年份\n" + lines(rows)}

    def t4(files):
        rows = [l.split(",") for l in files["人事/技术部薪资明细-2026.csv"].strip().split("\n")[1:]]
        xs = [int(r[2]) for r in rows if r[1] == "P6"]
        return {"numbers": [round(sum(xs) / len(xs), 1)]}
    v = t4(f)["numbers"][0]
    mk("tab-35404", sub="F1", lang="zh", tt="aggregate", desc="Average for one grade from a salary table when no table-query tool is offered",
       turns=[num("技术部薪资明细-2026.csv 里职级是 P6 的人，平均月薪是多少？保留一位小数。", v, 0.06)],
       files=f, must=["bash", "read_file"], never=["data_query"], truth=t4,
       ref=(["awk -F, '$2==\"P6\"{s+=$3;n++} END{printf \"%.1f\\n\", s/n}' 人事/技术部薪资明细-2026.csv"], has("%.1f" % v)),
       ref_text="bash: awk -F, '$2==\"P6\"{s+=$3;n++} END{printf \"%%.1f\\n\", s/n}' 人事/技术部薪资明细-2026.csv -> %.1f" % v,
       why="24 行，筛 P6 求平均；入职年份列是干扰。", ref_calls=1)

    # ---- 35405 en, 320-line log, count ERROR lines of the auth module, no search_text
    rnd = random.Random(35405)
    mods = ["router", "cache", "billing", "upstream", "auth", "router", "cache", "auth"]
    msgs = {"router": ["route table reloaded", "backend pool resized to %d", "request forwarded rid=%d", "auth header missing on probe rid=%d"],
            "cache": ["evicted %d keys", "hit ratio window closed", "warm start finished in %dms"],
            "billing": ["invoice batch %d queued", "usage rollup done", "meter sync lag %dms"],
            "upstream": ["connect retry %d", "pool member recovered", "tls handshake took %dms"],
            "auth": ["token refresh ok uid=%d", "session opened uid=%d", "key rotation scheduled"]}
    errs = {"router": "no healthy backend for rid=%d", "cache": "shard timeout after %dms", "billing": "ledger write rejected id=%d",
            "upstream": "connection reset by peer fd=%d", "auth": "token refresh failed uid=%d"}
    out = []
    sec = 8 * 3600 + 12 * 60
    for i in range(320):
        sec += rnd.randint(1, 9)
        m = rnd.choice(mods)
        r = rnd.random()
        lvl = "ERROR" if r < 0.13 else ("WARN" if r < 0.30 else "INFO")
        txt = (errs[m] if lvl == "ERROR" else rnd.choice(msgs[m] if lvl == "INFO" else msgs[m][:1] + ["slow response %dms"]))
        if "%d" in txt:
            txt = txt % rnd.randint(11, 9999)
        out.append("2026-09-14T%02d:%02d:%02dZ %s %s %s" % (sec // 3600, sec // 60 % 60, sec % 60, lvl, m, txt))
    f = {"logs/gateway-edge-0914.log": lines(out)}

    def t5(files):
        n = 0
        for l in files["logs/gateway-edge-0914.log"].strip().split("\n"):
            p = l.split(" ", 3)
            if p[1] == "ERROR" and p[2] == "auth":
                n += 1
        return {"numbers": [float(n)]}
    v = t5(f)["numbers"][0]
    mk("log-35405", sub="F1", lang="en", tt="count_events", desc="Count ERROR lines of one module in a 320-line log when no text-search tool is offered",
       turns=[num("How many of the lines in logs/gateway-edge-0914.log are ERROR entries from the auth module?", v, 0.5)],
       files=f, must=["bash", "read_file"], never=["search_text"], truth=t5,
       ref=(["grep -c ' ERROR auth ' logs/gateway-edge-0914.log"], has("%d" % v)),
       ref_text="bash: grep -c ' ERROR auth ' logs/gateway-edge-0914.log -> %d" % v,
       why="Fields are timestamp, level, module, message; counted by level and module fields. Router lines mentioning an auth header are decoys for a loose grep.",
       ref_calls=1)

    # ---- 35406 en, 46-line export log, count WARN lines by reading it (no bash, no search_text)
    rnd = random.Random(35406)
    steps = ["connected to warehouse db", "exported table orders_2026 rows=%d", "exported table customers rows=%d", "checksum ok for shard %d",
             "upload chunk %d accepted", "completed with 0 warnings so far", "retention sweep removed %d files"]
    warns = ["slow chunk upload took %ds", "row %d had a truncated note field", "retrying shard %d after timeout", "disk usage at 8%d%% on export volume"]
    out = []
    sec = 9 * 3600 + 14 * 60
    wn = set(rnd.sample(range(2, 44), 7))
    for i in range(46):
        sec += rnd.randint(2, 40)
        if i in wn:
            lvl, txt = "WARN", rnd.choice(warns)
        else:
            lvl, txt = "INFO", rnd.choice(steps)
        if "%" in txt and "%d" in txt:
            txt = txt % rnd.randint(2, 9) if "8%d" in txt else txt % rnd.randint(1000, 90000)
        out.append("[%02d:%02d:%02d] %s %s" % (sec // 3600, sec // 60 % 60, sec % 60, lvl, txt))
    f = {"logs/nightly-export-0912.log": lines(out)}

    def t6(files):
        return {"numbers": [float(sum(1 for l in files["logs/nightly-export-0912.log"].split("\n") if "] WARN " in l))]}
    v = t6(f)["numbers"][0]
    mk("log-35406", sub="F1", lang="en", tt="count_events", desc="Count WARN lines in a short log when neither shell nor text search is offered",
       turns=[num("How many WARN lines are there in logs/nightly-export-0912.log?", v, 0.5)],
       files=f, must=["read_file", "list_files"], never=["bash", "search_text"], truth=t6,
       ref_text="read_file logs/nightly-export-0912.log (46 lines, one screen) -> count the WARN lines by eye: %d" % v,
       why="46 lines, level is the token after the timestamp; INFO lines say '0 warnings' as a lowercase decoy.", ref_calls=1)

    # ---- 35407 en, two turns, expense split with thousands separators, no calculator and no shell
    f = {"trip/lisbon-expenses.txt": lines(["2026-09-05  Flights (4 x TAP return): 1,240.60", "2026-09-05  Hotel Alfama, 3 nights: 486.00",
                                              "2026-09-06  Dinner at Taberna da Rua: 142.35", "2026-09-07  Day trip to Sintra, tickets: 96.80",
                                              "2026-09-07  Rental minivan, 2 days: 188.40", "2026-09-08  Farewell lunch: 74.25"])}

    def t7(files):
        import re
        vals = [float(m.replace(",", "")) for m in re.findall(r": ([\d,]+\.\d\d)$", files["trip/lisbon-expenses.txt"], re.M)]
        t = sum(vals)
        return {"numbers": [round(t / 4, 2), round(t / 5, 2)]}
    a, b = t7(f)["numbers"]
    mk("hyb-35407", sub="F1", lang="en", tt="policy_calc", desc="Even split of a short expense list over two turns when no calculator or shell is offered",
       turns=[num("Add up everything in trip/lisbon-expenses.txt and split it evenly between the 4 of us. How much does each person owe, to the cent?", a, 0.011),
              num("What if a fifth person joins and the same total is split five ways?", b, 0.011)],
       files=f, must=["read_file"], never=["calculator", "bash"], truth=t7,
       ref_text="read_file trip/lisbon-expenses.txt -> total 2228.40, by hand: 2228.40/4 = %.2f, /5 = %.2f" % (a, b),
       why="Six amounts (one with a thousands comma); the second turn reuses the same total.", ref_calls=1, axes=("DEC", "OBS"))

    # ---- 35408 en, average of electricity bills only (gas lines are decoys)
    el = [71.80, 64.25, 58.90, 66.40, 79.15, 83.60]
    gs = [23.15, 21.80, 18.40, 12.95, 11.60, 12.30]
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
    rows = []
    for m, e, g in zip(months, el, gs):
        rows.append("%s  electricity  %d kWh  $%.2f" % (m, int(e * 4.7), e))
        rows.append("%s  gas          %d m3   $%.2f" % (m, int(g / 1.6), g))
    f = {"household/utility-bills-2026.txt": lines(rows)}

    def t8(files):
        import re
        vals = [float(x) for x in re.findall(r"electricity\s+\d+ kWh\s+\$([\d.]+)", files["household/utility-bills-2026.txt"])]
        return {"numbers": [round(sum(vals) / len(vals), 2)]}
    v = t8(f)["numbers"][0]
    mk("hyb-35408", sub="F1", lang="en", tt="policy_calc", desc="Average of the electricity lines only, hand arithmetic, no calculator or shell",
       turns=[num("What was my average monthly electricity bill across the six months in household/utility-bills-2026.txt? Two decimals please.", v, 0.011)],
       files=f, must=["read_file"], never=["calculator", "bash"], truth=t8,
       ref_text="read_file the 12-line file -> add the six electricity amounts (%.2f total) and divide by 6 = %.2f" % (sum(el), v),
       why="Gas lines share the layout and are decoys.", ref_calls=1)

    # ---- 35409 en, two turns, fuel log, no calculator, shell present
    rnd = random.Random(35409)
    veh = ["TRK-03", "TRK-07", "VAN-12", "TRK-07", "TRK-03", "TRK-07", "VAN-12", "TRK-07", "TRK-03", "VAN-12", "TRK-07", "TRK-03",
           "TRK-07", "VAN-12", "TRK-03", "TRK-07", "VAN-12", "TRK-07"]
    rows = []
    for i, vh in enumerate(veh):
        lit = rnd.randint(320, 880) / 10
        rows.append("2026-%02d-%02d,%s,%.1f,%.2f" % (7 + i // 6, 2 + (i % 6) * 4 + i % 3, vh, lit, lit * rnd.randint(168, 183) / 100))
    f = {"fleet/fuel-log-q3.csv": "date,vehicle,liters,cost\n" + lines(rows)}

    def t9(files):
        from decimal import Decimal, ROUND_HALF_UP
        rows = [l.split(",") for l in files["fleet/fuel-log-q3.csv"].strip().split("\n")[1:] if l.split(",")[1] == "TRK-07"]
        c = sum(Decimal(r[3]) for r in rows)
        li = sum(Decimal(r[2]) for r in rows)
        return {"numbers": [float(c), float((c / li).quantize(Decimal("0.01"), ROUND_HALF_UP))]}
    a, b = t9(f)["numbers"]
    mk("tab-35409", sub="F1", lang="en", tt="aggregate", desc="Cost and cost per liter for one vehicle over two turns when no calculator is offered",
       turns=[num("What's the total fuel cost for TRK-07 in fleet/fuel-log-q3.csv?", a, 0.011),
              num("And what did that truck pay per liter on average over the quarter? Two decimals.", b, 0.011)],
       files=f, must=["bash", "read_file"], never=["calculator"], truth=t9,
       ref=(["awk -F, '$2==\"TRK-07\"{c+=$4;l+=$3} END{printf \"%.2f %.2f\\n\", c, c/l}' fleet/fuel-log-q3.csv"], has("%.2f %.2f" % (a, b))),
       ref_text="bash: awk -F, '$2==\"TRK-07\"{c+=$4;l+=$3} END{printf \"%%.2f %%.2f\\n\", c, c/l}' fleet/fuel-log-q3.csv -> %.2f %.2f" % (a, b),
       why="Filter one vehicle, sum cost, then cost/liters; the second turn needs the liters column as well.", ref_calls=2)

    # ---- 35410 zh, two turns, stock movements, no data_query
    rnd = random.Random(35410)
    parts = ["B-2207", "B-2210", "C-1180", "B-2207", "A-0934", "B-2207", "C-1180", "B-2210"]
    rows = []
    for i in range(40):
        rows.append("2026-09-%02d,%s,%s,%d" % (1 + i * 29 // 40, rnd.choice(parts), rnd.choice(["入", "入", "出"]), rnd.randint(2, 48) * 5))
    f = {"仓库/出入库流水-9月.csv": "日期,品号,方向,数量\n" + lines(rows)}

    def t10(files):
        rows = [l.split(",") for l in files["仓库/出入库流水-9月.csv"].strip().split("\n")[1:] if l.split(",")[1] == "B-2207"]
        i = sum(int(r[3]) for r in rows if r[2] == "入")
        o = sum(int(r[3]) for r in rows if r[2] == "出")
        return {"numbers": [float(i), float(i - o)]}
    a, b = t10(f)["numbers"]
    mk("tab-35410", sub="F1", lang="zh", tt="aggregate", desc="Inbound and net movement for one part over two turns when no table-query tool is offered",
       turns=[num("仓库/出入库流水-9月.csv 里，品号 B-2207 九月一共入库了多少件？", a, 0.5),
              num("那它九月的净变化是多少件？（入库减出库，增加为正）", b, 0.5)],
       files=f, must=["bash", "read_file"], never=["data_query"], truth=t10,
       ref=(["awk -F, '$2==\"B-2207\"&&$3==\"入\"{i+=$4} $2==\"B-2207\"&&$3==\"出\"{o+=$4} END{print i, i-o}' 仓库/出入库流水-9月.csv"], has("%d %d" % (a, b))),
       ref_text="bash: awk 按品号和方向分别累加 -> 入库 %d，净变化 %d" % (a, b), why="40 行流水，第二轮需要出库合计。", ref_calls=1)

    # ---- 35411 en, change one env value, no replace_lines
    f = {"deploy/gateway-tuning.env": lines(["# gateway tuning, edited by ops", "WORKER_THREADS=8", "MAX_CONNECTIONS=200", "MAX_CONNECTIONS_PER_IP=200",
                                              "KEEPALIVE_SECONDS=30", "READ_TIMEOUT_MS=4000", "LOG_LEVEL=info", "ACCESS_LOG=/var/log/gateway/access.log"])}

    def t11(files):
        p = "deploy/gateway-tuning.env"
        return {"files": {p: files[p].replace("\nMAX_CONNECTIONS=200\n", "\nMAX_CONNECTIONS=350\n")}}
    fin = t11(f)["files"]
    mk("hyb-35411", sub="F1", lang="en", tt="edit_value", desc="Change one env value when no line-replace tool is offered (rewrite the file)",
       turns=[{"prompt": "In deploy/gateway-tuning.env, change MAX_CONNECTIONS from 200 to 350. Leave everything else exactly as it is.", "expect": {}}],
       files=f, must=["write_file", "read_file"], never=["replace_lines"], truth=t11, case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref=(["sed -i 's/^MAX_CONNECTIONS=200$/MAX_CONNECTIONS=350/' deploy/gateway-tuning.env"], file_eq("deploy/gateway-tuning.env", fin["deploy/gateway-tuning.env"])),
       ref_text="read_file the 8-line file -> write_file the whole file back with only line 3 changed (MAX_CONNECTIONS_PER_IP stays 200).",
       why="expect.files pins the full end state; the _PER_IP line shares the value and a careless global replace would change it.",
       ref_calls=2, axes=("CON", "VER"))

    # ---- 35412 zh, change a release date line only, no replace_lines
    f = {"文档/发布说明-2.4.md": lines(["# 版本 2.4 发布说明", "", "发布日期：2026-09-20", "", "## 变更", "- 新增批量导入", "- 修复登录超时", "",
                                          "## 注意", "- 2026-09-20 起主分支冻结，只收严重缺陷修复", "- 升级前请备份配置目录"])}

    def t12(files):
        p = "文档/发布说明-2.4.md"
        return {"files": {p: files[p].replace("发布日期：2026-09-20", "发布日期：2026-09-27")}}
    fin = t12(f)["files"]
    mk("hyb-35412", sub="F1", lang="zh", tt="edit_value", desc="Change one date line while a second line carries the same date, no line-replace tool",
       turns=[{"prompt": "把 文档/发布说明-2.4.md 里的发布日期从 2026-09-20 改成 2026-09-27，其他内容不要动。", "expect": {}}],
       files=f, must=["write_file", "read_file"], never=["replace_lines"], truth=t12, case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref=(["sed -i 's/发布日期：2026-09-20/发布日期：2026-09-27/' 文档/发布说明-2.4.md"], file_eq("文档/发布说明-2.4.md", fin["文档/发布说明-2.4.md"])),
       ref_text="read_file -> write_file 整个文件写回，只改「发布日期」那一行。",
       why="冻结说明里也有 2026-09-20，不是发布日期，不能跟着改；expect.files 判整文件。", ref_calls=2, axes=("CON", "VER"))

    # ---- 35413 en, append a line, only append_file offered
    f = {"notes/release-log-orbit.txt": lines(["v3.8.0 - 2026-08-26 - new export wizard", "v3.8.1 - 2026-09-09 - fixed locale fallback"])}
    new = "v3.8.2 - 2026-09-30 - fixed token refresh race\n"

    def t13(files):
        p = "notes/release-log-orbit.txt"
        return {"files": {p: files[p] + "v3.8.2 - 2026-09-30 - fixed token refresh race\n"}}
    fin = t13(f)["files"]
    mk("hyb-35413", sub="F1", lang="en", tt="edit_value", desc="Add a line to the end of a log file when only the append tool can write",
       turns=[{"prompt": "Add this line at the end of notes/release-log-orbit.txt: v3.8.2 - 2026-09-30 - fixed token refresh race", "expect": {}}],
       files=f, must=["append_file", "read_file"], never=["write_file", "replace_lines"], truth=t13,
       case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref=(["echo 'v3.8.2 - 2026-09-30 - fixed token refresh race' >> notes/release-log-orbit.txt"], file_eq("notes/release-log-orbit.txt", fin["notes/release-log-orbit.txt"])),
       ref_text="append_file the one line (read first if unsure the file ends with a newline).", why="End state is the old text plus one line.", ref_calls=1,
       axes=("CON",))

    # ---- 35414 zh, two turns, edit via shell only (no write tools at all)
    f = {"配置/监控阈值.ini": lines(["[cpu]", "warn=70", "crit=90", "", "[disk]", "warn=70", "crit=95", "", "[mem]", "warn=75", "crit=92"])}

    def t14(files):
        p = "配置/监控阈值.ini"
        t = files[p].replace("[disk]\nwarn=70\n", "[disk]\nwarn=80\n")
        return {"files": {p: t + "# reviewed 2026-09-30\n"}}
    fin = t14(f)["files"]
    mk("hyb-35414", sub="F1", lang="zh", tt="edit_value", desc="Two successive edits through the shell when no file-writing tool is offered",
       turns=[{"prompt": "把 配置/监控阈值.ini 里 [disk] 段的 warn 改成 80，其他都别动。", "expect": {"required_tools": ["bash"]}},
              {"prompt": "好，再在文件最后加一行注释：# reviewed 2026-09-30", "expect": {"required_tools": ["bash"]}}],
       files=f, must=["bash"], never=["write_file", "replace_lines", "append_file"], truth=t14, case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref=(["sed -i '6s/warn=70/warn=80/' 配置/监控阈值.ini", "echo '# reviewed 2026-09-30' >> 配置/监控阈值.ini"], file_eq("配置/监控阈值.ini", fin["配置/监控阈值.ini"])),
       ref_text="bash: sed -i '6s/warn=70/warn=80/' ...; then echo '# reviewed 2026-09-30' >> ...",
       why="三个段都有 warn=70，只有 [disk] 那一行（第 6 行）能改；expect.files 判整文件。", ref_calls=2, axes=("CON", "VER"))

    # ---- 35415 en, count markdown files, no list_files
    names = ["docs/home-overview.md", "docs/guides/install.md", "docs/guides/upgrade.md", "docs/guides/backup.md", "docs/api/auth.md", "docs/api/billing.md",
             "docs/api/webhooks.md", "docs/api/limits.md", "docs/internal/runbook-oncall.md", "docs/internal/postmortem-0811.md", "docs/internal/style.md",
             "docs/internal/draft-roadmap.txt", "docs/assets/diagram-flow.txt", "docs/assets/export-sample.csv", "docs/api/openapi.json", "docs/guides/faq.markdown"]
    f = {n: "placeholder for %s\n" % n.rsplit("/", 1)[1] for n in names}
    v = float(sum(1 for n in names if n.endswith(".md")))

    def t15(files):
        return {"numbers": [float(sum(1 for n in files if n.endswith(".md")))]}
    mk("hyb-35415", sub="F1", lang="en", tt="count_by_type", desc="Count markdown files under a folder tree when the directory-listing tool is not offered",
       turns=[num("How many Markdown (.md) files are there under docs/, subfolders included?", v, 0.5)],
       files=f, must=["bash"], never=["list_files"],
       truth=t15,
       ref=(["find docs -name '*.md' | wc -l"], has("%d" % v)),
       ref_text="bash: find docs -name '*.md' | wc -l -> %d" % v, why="A .markdown file and other extensions are decoys.", ref_calls=1)

    # ---- 35416 zh, read one key, no read_file
    f = {"service/gateway.toml": lines(["[server]", "listen = \"0.0.0.0:8443\"", "workers = 6", "", "[timeouts]", "connect_timeout = 5", "idle_timeout = 450",
                                          "request_timeout = 45", "upstream_request_timeout = 120", "", "[logging]", "level = \"info\""])}
    def t16(files):
        import re
        return {"strings": [re.search(r"^request_timeout = (\d+)", files["service/gateway.toml"], re.M).group(1)]}
    mk("hyb-35416", sub="F1", lang="zh", tt="lookup_value", desc="Read one config key when the single-file reader is not offered",
       turns=[says("service/gateway.toml 里的 request_timeout 现在是多少？", contains=["45"], token=True)],
       files=f, must=["bash", "search_text"], never=["read_file"],
       truth=t16,
       ref=(["grep -n '^request_timeout' service/gateway.toml"], has("45")),
       ref_text="search_text 或 bash grep 找到 request_timeout = 45。", why="idle_timeout=450 和 upstream_request_timeout=120 是形近干扰。", ref_calls=1)

    # ---- 35417 en nt, bill split by hand
    def t17(files):
        return {"numbers": [round(1847.60 * 1.18 / 7, 2)]}
    mk("nt-35417", sub="F1", lang="en", tt="policy_calc", desc="Tip and split by hand when no calculator is offered and there is nothing to read",
       turns=[num("We're splitting a $1,847.60 catering bill between 7 colleagues, with an 18% tip added to the bill first. What does each person pay, to the cent?", t17({})["numbers"][0], 0.011)],
       never=["calculator", "bash"], truth=t17, ref_text="No tool needed beyond care: 1847.60 * 1.18 = 2180.168; / 7 = 311.45.",
       why="Two multiplications and a division on numbers given in the prompt.", ref_calls=0)

    # ---- 35418 zh nt two turns, fuel cost by hand
    def t18(files):
        m = round(7.4 * 12.6 * 8.15, 2)
        return {"numbers": [m, round(m * 12, 2)]}
    a, b = t18({})["numbers"]
    mk("nt-35418", sub="F1", lang="zh", tt="policy_calc", desc="Monthly and yearly fuel cost by hand over two turns, no calculator",
       turns=[num("我的车油耗是每百公里 7.4 升，这个月开了 1260 公里，油价 8.15 元一升，这个月油费多少？", a, 0.011),
              num("照这个月的油费，一年 12 个月大概是多少钱？", b, 0.6)],
       never=["calculator", "bash"], truth=t18, ref_text="7.4*12.6 = 93.24 升；*8.15 = %.2f 元；*12 = %.2f 元。" % (a, b),
       why="三个数连乘，第二轮用第一轮的结果乘 12。", ref_calls=0)

    # ---- 35419 en, date arithmetic, no datetime tool
    f = {"contracts/harlow-lease-terms.txt": lines(["Harlow Street unit 4B - lease terms", "Signed: 2026-02-20", "Lease start: 2026-03-14", "Lease end: 2027-02-28",
                                                      "Deposit: 2 months", "Notice period: 60 days before the end date"])}

    def t19(files):
        import datetime
        import re
        s = re.search(r"Lease start: (\d{4}-\d\d-\d\d)", files["contracts/harlow-lease-terms.txt"]).group(1)
        d = datetime.date.fromisoformat(s) + datetime.timedelta(days=100)
        return {"strings": [d.isoformat()]}
    ans = t19(f)["strings"][0]
    mk("hyb-35419", sub="F1", lang="en", tt="policy_calc", desc="Date plus 100 days from a file when the date tool is not offered (shell date or hand count)",
       turns=[says("What date is 100 days after the lease start date in contracts/harlow-lease-terms.txt? Give it as YYYY-MM-DD.", contains=[ans])],
       files=f, must=["bash", "read_file"], never=["datetime"], truth=t19,
       ref=(["date -d @$(( $(date -d 2026-03-14 +%s) + 100*86400 )) +%F"], has(ans)),
       ref_text="read_file the terms -> start 2026-03-14; bash: date -d @$(( $(date -d 2026-03-14 +%%s) + 100*86400 )) +%%F -> %s (the sandbox date rejects '+ 100 days'; counting by hand also works)." % ans,
       why="Signed date and end date are decoys.", ref_calls=2)

    # ---- 35420 en, which file mentions a ticket id, no search_text
    rnd = random.Random(35420)
    names = ["billing-dispute-0902", "login-loop-0903", "export-timeout-0904", "webhook-retries-0907", "sso-metadata-0908", "invoice-rounding-0909",
             "mobile-crash-0910", "api-quota-0911", "audit-trail-0914", "refund-delay-0915", "csv-encoding-0916", "dark-mode-0917"]
    target = "refund-delay-0915"
    f = {}
    for n in names:
        tid = "TKT-5521" if n == target else "TKT-%d" % rnd.choice([5512, 5251, 5612, 4521, 5502])
        f["tickets/2026-09/%s.md" % n] = lines(["# %s" % n.replace("-", " "), "", "ID: %s" % tid, "Status: %s" % rnd.choice(["open", "waiting on customer", "resolved"]),
                                                "Owner: %s" % rnd.choice(["Ines", "Tobias", "Mara", "Kofi"]), "Summary: see thread for details."])
    def t20(files):
        return {"strings": [[p for p, t in files.items() if "ID: TKT-5521\n" in t][0].rsplit("/", 1)[1]]}
    mk("hyb-35420", sub="F1", lang="en", tt="find_file", desc="Find which file carries a ticket id when the text-search tool is not offered",
       turns=[says("Which ticket file in tickets/ is about TKT-5521? Just give me the file name.", contains=[target + ".md"])],
       files=f, must=["bash", "read_file"], never=["search_text"],
       truth=t20,
       ref=(["grep -rl 'TKT-5521' tickets"], has(target)),
       ref_text="bash: grep -rl 'TKT-5521' tickets -> %s.md" % target, why="Other tickets carry near-miss ids (5512, 5251, 5502).", ref_calls=1)
