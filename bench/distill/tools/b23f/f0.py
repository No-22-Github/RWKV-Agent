"""F0: the same kind of task as F1/F2, but the proper tool IS offered (35436-35450)."""
import random
from decimal import ROUND_HALF_UP, Decimal

from common import mk, num, says


def lines(rows):
    return "".join(r + "\n" for r in rows)


def build():
    # ---- 35436 mortgage payment, calculator offered
    def t36(files):
        r, n, p = 0.0535 / 12, 300, 412500
        return {"numbers": [round(p * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)]}
    v = t36({})["numbers"][0]
    mk("nt-35436", sub="F0", lang="en", tt="policy_calc", desc="Mortgage payment with the calculator offered",
       turns=[num("What's the monthly payment on a 25-year mortgage of $412,500 at 5.35% APR, standard amortization? Two decimals.", v, 0.011, required=["calculator"])],
       must=["calculator"], never=["bash"], truth=t36, trap=None, ref_text="calculator: P*r*(1+r)^n/((1+r)^n-1) with r=0.0535/12, n=300 -> %.2f" % v,
       why="Six-figure principal, 300 periods: needs exact arithmetic.", ref_calls=1)

    # ---- 35437 zh compound growth, calculator offered
    def t37(files):
        return {"numbers": [round(268000 * 1.0415 ** 9, 2)]}
    v = t37({})["numbers"][0]
    mk("nt-35437", sub="F0", lang="zh", tt="policy_calc", desc="Compound deposit with the calculator offered",
       turns=[num("26.8 万元年利率 4.15%，每年复利一次，存 9 年，到期本息合计多少？保留两位小数。", v, 0.011, required=["calculator"])],
       must=["calculator"], never=["bash"], truth=t37, trap=None, ref_text="calculator: 268000*pow(1.0415,9) -> %.2f" % v, why="九次方，心算不可能准。", ref_calls=1)

    # ---- 35438 en two turns: region revenue with data_query
    rnd = random.Random(35438)
    regions = {"Brightwater": 77500, "Coldharbor": 93000, "Dunmore": 68000, "Ellsworth": 84500, "Fairhaven": 101000}
    rows = []
    for mo in range(1, 7):
        for rg, base in regions.items():
            units = int(base / 38 + rnd.randint(-55, 55))
            rows.append("2026-%02d,%s,%d,%d" % (mo, rg, units, int(units * 38 + rnd.randint(-800, 800))))
    f = {"sales/branch-roll-2026h1.csv": "month,region,units,revenue\n" + lines(rows)}

    def t38(files):
        rows = [l.split(",") for l in files["sales/branch-roll-2026h1.csv"].strip().split("\n")[1:]]
        tot = {}
        for r in rows:
            tot[r[1]] = tot.get(r[1], 0) + int(r[3])
        best = max(tot, key=tot.get)
        return {"numbers": [float(tot[best]), float(round(tot[best] / 6))], "strings": [best]}
    g = t38(f)
    mk("tab-35438", sub="F0", lang="en", tt="aggregate", desc="Group revenue by region over two turns with the table-query tool offered",
       turns=[num("Which region brought in the most revenue in sales/branch-roll-2026h1.csv, and what was its six-month total?", g["numbers"][0], 0.5, contains=g["strings"], required=["data_query"]),
              num("And what was that region's average monthly revenue, to the nearest dollar?", g["numbers"][1], 0.51)],
       files=f, must=["data_query", "read_file"], never=["bash"], truth=t38, trap="TR-DECOY", decoy="runner-up region total",
       ref_text="data_query sum revenue group_by region -> %s %d; turn 2 divides by 6." % (g["strings"][0], g["numbers"][0]),
       why="30 rows, 5 regions x 6 months.", ref_calls=1, axes=("DEC", "OBS"))

    # ---- 35439 zh average by grade with data_query
    rnd = random.Random(35439)
    names = "邓一鸣 白若溪 蔡子轩 董雅琴 方浩然 高亦凡 贺宁宁 江云帆 康锦程 雷思琪 马俊杰 倪晓雨 欧阳睿 彭嘉禾 邱诗雨 任泽宇 苏雨晴 唐子豪 万佳琪 夏明轩 姚欣然 于海洋 袁梓涵 张若楠".split()
    grades = ["S2", "S3", "S3", "S4", "S2", "S3", "S3", "S4", "S2", "S3", "S5", "S3", "S2", "S4", "S3", "S3", "S2", "S4", "S3", "S5", "S2", "S3", "S4", "S3"]
    base = {"S2": 14800, "S3": 20500, "S4": 29000, "S5": 40500}
    rows = ["%s,%s,%d,%d" % (n, g, base[g] + rnd.randint(-12, 12) * 100, rnd.randint(2016, 2025)) for n, g in zip(names, grades)]
    f = {"人事/产品部薪资明细-2026.csv": "姓名,职级,月薪,入职年份\n" + lines(rows)}

    def t39(files):
        rows = [l.split(",") for l in files["人事/产品部薪资明细-2026.csv"].strip().split("\n")[1:]]
        xs = [int(r[2]) for r in rows if r[1] == "S3"]
        return {"numbers": [round(sum(xs) / len(xs), 1)]}
    v = t39(f)["numbers"][0]
    mk("tab-35439", sub="F0", lang="zh", tt="aggregate", desc="Average for one grade with the table-query tool offered",
       turns=[num("产品部薪资明细-2026.csv 里职级是 S3 的人，平均月薪是多少？保留一位小数。", v, 0.06, required=["data_query"])],
       files=f, must=["data_query", "read_file"], never=["bash"], truth=t39, trap="TR-DECOY", decoy="other grades' average",
       ref_text="data_query avg field=月薪 filter {职级:S3} -> %.1f" % v, why="24 行，筛 S3 求平均。", ref_calls=1)

    # ---- 35440 en, count ERROR lines of one module with text search offered
    rnd = random.Random(35440)
    mods = ["router", "cache", "billing", "upstream", "auth", "router", "cache", "billing"]
    msgs = {"router": ["route table reloaded", "backend pool resized to %d", "request forwarded rid=%d", "billing header missing on probe rid=%d"],
            "cache": ["evicted %d keys", "hit ratio window closed", "warm start finished in %dms"],
            "billing": ["invoice batch %d queued", "usage rollup done", "meter sync lag %dms"],
            "upstream": ["connect retry %d", "pool member recovered", "tls handshake took %dms"],
            "auth": ["token refresh ok uid=%d", "session opened uid=%d", "key rotation scheduled"]}
    errs = {"router": "no healthy backend for rid=%d", "cache": "shard timeout after %dms", "billing": "ledger write rejected id=%d",
            "upstream": "connection reset by peer fd=%d", "auth": "token refresh failed uid=%d"}
    out = []
    sec = 13 * 3600 + 5 * 60
    for i in range(320):
        sec += rnd.randint(1, 9)
        m = rnd.choice(mods)
        r = rnd.random()
        lvl = "ERROR" if r < 0.13 else ("WARN" if r < 0.30 else "INFO")
        txt = errs[m] if lvl == "ERROR" else rnd.choice(msgs[m] if lvl == "INFO" else msgs[m][:1] + ["slow response %dms"])
        if "%d" in txt:
            txt = txt % rnd.randint(11, 9999)
        out.append("2026-09-21T%02d:%02d:%02dZ %s %s %s" % (sec // 3600, sec // 60 % 60, sec % 60, lvl, m, txt))
    f = {"logs/gateway-core-0921.log": lines(out)}

    def t40(files):
        n = 0
        for l in files["logs/gateway-core-0921.log"].strip().split("\n"):
            p = l.split(" ", 3)
            if p[1] == "ERROR" and p[2] == "billing":
                n += 1
        return {"numbers": [float(n)]}
    v = t40(f)["numbers"][0]
    mk("log-35440", sub="F0", lang="en", tt="count_events", desc="Count ERROR lines of one module in a 320-line log with text search offered",
       turns=[num("How many of the lines in logs/gateway-core-0921.log are ERROR entries from the billing module?", v, 0.5, required=["search_text"])],
       files=f, must=["search_text", "read_file", "bash"], truth=t40, trap="TR-DECOY", decoy="loose grep count",
       ref_text="search_text 'ERROR billing ' (or bash grep -c) -> %d" % v, why="Router lines that mention a billing header are decoys for a loose search.", ref_calls=1)

    # ---- 35441 en expense split with calculator offered
    f = {"trip/porto-expenses.txt": lines(["2026-09-12  Flights (4 x return): 1,118.40", "2026-09-12  Guesthouse Ribeira, 3 nights: 534.00",
                                             "2026-09-13  Dinner at Casa Antunes: 156.80", "2026-09-14  Douro valley boat tour: 212.00",
                                             "2026-09-14  Rental car, 2 days: 174.55", "2026-09-15  Farewell lunch: 83.90"])}

    def t41(files):
        import re
        vals = [float(m.replace(",", "")) for m in re.findall(r": ([\d,]+\.\d\d)$", files["trip/porto-expenses.txt"], re.M)]
        return {"numbers": [round(sum(vals) / 4, 2)]}
    v = t41(f)["numbers"][0]
    mk("hyb-35441", sub="F0", lang="en", tt="policy_calc", desc="Even split of a short expense list with the calculator offered",
       turns=[num("Add up everything in trip/porto-expenses.txt and split it evenly between the 4 of us. How much does each person owe, to the cent?", v, 0.011, required=["calculator"])],
       files=f, must=["calculator", "read_file"], never=["bash"], truth=t41, trap="TR-DECOY", decoy="sum without the flights line",
       ref_text="read_file the six lines, calculator on (1118.40+534+156.80+212+174.55+83.90)/4 -> %.2f" % v, why="Six amounts, one with a thousands comma.", ref_calls=2)

    # ---- 35442 zh electricity average with calculator offered
    el = [68.30, 61.75, 55.20, 63.90, 82.45, 87.10]
    gs = [26.80, 22.15, 17.60, 13.25, 12.40, 13.90]
    months = ["四月", "五月", "六月", "七月", "八月", "九月"]
    rows = []
    for m, e, g in zip(months, el, gs):
        rows.append("%s 电费 %d 度 %.2f 元" % (m, int(e * 1.9), e))
        rows.append("%s 燃气 %d 立方 %.2f 元" % (m, int(g / 3.2), g))
    f = {"家庭/水电气账单-2026.txt": lines(rows)}

    def t42(files):
        import re
        vals = [float(x) for x in re.findall(r"电费 \d+ 度 ([\d.]+) 元", files["家庭/水电气账单-2026.txt"])]
        return {"numbers": [round(sum(vals) / len(vals), 2)]}
    v = t42(f)["numbers"][0]
    mk("hyb-35442", sub="F0", lang="zh", tt="policy_calc", desc="Average of the electricity lines only with the calculator offered",
       turns=[num("家庭/水电气账单-2026.txt 里这六个月，我平均每月电费是多少？保留两位小数。", v, 0.011, required=["calculator"])],
       files=f, must=["calculator", "read_file"], never=["bash"], truth=t42, trap="TR-DECOY", decoy="gas lines",
       ref_text="read_file 后用 calculator 把六个电费相加除以 6 = %.2f" % v, why="燃气行格式相同，是干扰。", ref_calls=2)

    # ---- 35443 en two turns fuel log with data_query
    rnd = random.Random(35443)
    veh = ["TRK-21", "TRK-14", "VAN-05", "TRK-14", "TRK-21", "TRK-14", "VAN-05", "TRK-14", "TRK-21", "VAN-05", "TRK-14", "TRK-21",
           "TRK-14", "VAN-05", "TRK-21", "TRK-14", "VAN-05", "TRK-14"]
    rows = []
    for i, vh in enumerate(veh):
        lit = rnd.randint(300, 860) / 10
        rows.append("2026-%02d-%02d,%s,%.1f,%.2f" % (7 + i // 6, 3 + (i % 6) * 4 + i % 2, vh, lit, lit * rnd.randint(166, 181) / 100))
    f = {"fleet/fuel-log-q3b.csv": "date,vehicle,liters,cost\n" + lines(rows)}

    def t43(files):
        from decimal import Decimal, ROUND_HALF_UP
        rows = [l.split(",") for l in files["fleet/fuel-log-q3b.csv"].strip().split("\n")[1:] if l.split(",")[1] == "TRK-14"]
        c = sum(Decimal(r[3]) for r in rows)
        li = sum(Decimal(r[2]) for r in rows)
        return {"numbers": [float(c), float((c / li).quantize(Decimal("0.01"), ROUND_HALF_UP))]}
    a, b = t43(f)["numbers"]
    mk("tab-35443", sub="F0", lang="en", tt="aggregate", desc="Cost and cost per liter for one vehicle over two turns with table query offered",
       turns=[num("What's the total fuel cost for TRK-14 in fleet/fuel-log-q3b.csv?", a, 0.011, required=["data_query"]),
              num("And what did that truck pay per liter on average over the quarter? Two decimals.", b, 0.011)],
       files=f, must=["data_query", "calculator"], never=["bash"], truth=t43, trap="TR-DECOY", decoy="other vehicles",
       ref_text="data_query sum cost filter vehicle=TRK-14, sum liters, calculator for cost/liters -> %.2f %.2f" % (a, b), why="Second turn needs the liters sum too.", ref_calls=3)

    # ---- 35444 zh two turns stock with data_query
    rnd = random.Random(35444)
    parts = ["K-3318", "K-3320", "M-0771", "K-3318", "R-5502", "K-3318", "M-0771", "K-3320"]
    rows = []
    for i in range(40):
        rows.append("2026-09-%02d,%s,%s,%d" % (1 + i * 29 // 40, rnd.choice(parts), rnd.choice(["入", "入", "出"]), rnd.randint(2, 48) * 5))
    f = {"仓库/出入库流水-9月补.csv": "日期,品号,方向,数量\n" + lines(rows)}

    def t44(files):
        rows = [l.split(",") for l in files["仓库/出入库流水-9月补.csv"].strip().split("\n")[1:] if l.split(",")[1] == "K-3318"]
        i = sum(int(r[3]) for r in rows if r[2] == "入")
        o = sum(int(r[3]) for r in rows if r[2] == "出")
        return {"numbers": [float(i), float(i - o)]}
    a, b = t44(f)["numbers"]
    mk("tab-35444", sub="F0", lang="zh", tt="aggregate", desc="Inbound and net movement for one part over two turns with table query offered",
       turns=[num("仓库/出入库流水-9月补.csv 里，品号 K-3318 九月一共入库了多少件？", a, 0.5, required=["data_query"]),
              num("那它九月的净变化是多少件？（入库减出库，增加为正）", b, 0.5)],
       files=f, must=["data_query", "calculator"], never=["bash"], truth=t44, trap="TR-DECOY", decoy="other part numbers",
       ref_text="data_query sum 数量 filter 品号+方向 -> 入 %d，出库另查，净变化 %d" % (a, b), why="40 行流水，第二轮需要出库合计。", ref_calls=3)

    # ---- 35445 en change env value with replace_lines offered
    f = {"deploy/edge-tuning.env": lines(["# edge tuning, edited by ops", "WORKER_THREADS=8", "MAX_CONNECTIONS=250", "MAX_CONNECTIONS_PER_IP=250",
                                           "KEEPALIVE_SECONDS=30", "READ_TIMEOUT_MS=4000", "LOG_LEVEL=info", "ACCESS_LOG=/var/log/edge/access.log"])}

    def t45(files):
        p = "deploy/edge-tuning.env"
        return {"files": {p: files[p].replace("\nMAX_CONNECTIONS=250\n", "\nMAX_CONNECTIONS=400\n")}}
    fin = t45(f)["files"]
    mk("hyb-35445", sub="F0", lang="en", tt="edit_value", desc="Change one env value with the line-replace tool offered",
       turns=[{"prompt": "In deploy/edge-tuning.env, change MAX_CONNECTIONS from 250 to 400. Leave everything else exactly as it is.", "expect": {"required_tools": ["replace_lines"]}}],
       files=f, must=["replace_lines", "read_file"], never=["bash"], truth=t45, trap="TR-DECOY", decoy="MAX_CONNECTIONS_PER_IP line",
       case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref_text="read_file (line 3) -> replace_lines 3..3 with MAX_CONNECTIONS=400 -> read back.", why="The _PER_IP line shares the value and must stay.", ref_calls=2, axes=("CON", "VER"))

    # ---- 35446 zh change a date line with replace_lines offered
    f = {"文档/发布说明-2.6.md": lines(["# 版本 2.6 发布说明", "", "发布日期：2026-10-11", "", "## 变更", "- 新增导出模板", "- 修复同步失败", "",
                                          "## 注意", "- 2026-10-11 起主分支冻结，只收严重缺陷修复", "- 升级前请备份配置目录"])}

    def t46(files):
        p = "文档/发布说明-2.6.md"
        return {"files": {p: files[p].replace("发布日期：2026-10-11", "发布日期：2026-10-18")}}
    fin = t46(f)["files"]
    mk("hyb-35446", sub="F0", lang="zh", tt="edit_value", desc="Change one date line with the line-replace tool offered",
       turns=[{"prompt": "把 文档/发布说明-2.6.md 里的发布日期从 2026-10-11 改成 2026-10-18，其他内容不要动。", "expect": {"required_tools": ["replace_lines"]}}],
       files=f, must=["replace_lines", "read_file"], never=["bash"], truth=t46, trap="TR-DECOY", decoy="freeze note with the same date",
       case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref_text="read_file 看行号 -> replace_lines 第 3 行 -> 回读。", why="冻结说明里也有同一日期，不是发布日期。", ref_calls=2, axes=("CON", "VER"))

    # ---- 35447 en two turns: append a line, then a follow-up question
    f = {"notes/release-log-vector.txt": lines(["v5.1.0 - 2026-08-19 - new audit export", "v5.1.1 - 2026-09-02 - fixed timezone drift"])}

    def t47(files):
        p = "notes/release-log-vector.txt"
        return {"files": {p: files[p] + "v5.1.2 - 2026-09-23 - fixed duplicate webhook delivery\n"}}
    fin = t47(f)["files"]
    mk("hyb-35447", sub="F0", lang="en", tt="edit_value", desc="Append a line with the append tool offered, then a follow-up read-back",
       turns=[{"prompt": "Add this line at the end of notes/release-log-vector.txt: v5.1.2 - 2026-09-23 - fixed duplicate webhook delivery", "expect": {"required_tools": ["append_file"]}},
              says("How many releases does the file list now?", contains=["3"], token=True)],
       files=f, must=["append_file", "read_file"], never=["bash"], truth=t47, trap=None, case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref_text="append_file the line; turn 2 answers 3 (two earlier lines plus the new one), reading the file if needed.", why="End state is old text plus one line.", ref_calls=2, axes=("CON",))

    # ---- 35448 en count markdown with list_files offered
    names = ["docs/home-overview.md", "docs/guides/setup.md", "docs/guides/migrate.md", "docs/guides/restore.md", "docs/api/tokens.md", "docs/api/invoices.md",
             "docs/api/events.md", "docs/internal/runbook-pager.md", "docs/internal/postmortem-0903.md", "docs/internal/tone.md", "docs/internal/draft-notes.txt",
             "docs/assets/flow-sketch.txt", "docs/assets/export-sample.csv", "docs/api/spec.json", "docs/guides/glossary.markdown"]
    f = {n: "placeholder for %s\n" % n.rsplit("/", 1)[1] for n in names}

    def t48(files):
        return {"numbers": [float(sum(1 for n in files if n.endswith(".md")))]}
    v = t48(f)["numbers"][0]
    mk("hyb-35448", sub="F0", lang="en", tt="count_by_type", desc="Count markdown files under a folder tree with the directory-listing tool offered",
       turns=[num("How many Markdown (.md) files are there under docs/, subfolders included?", v, 0.5, required=["list_files"])],
       files=f, must=["list_files"], never=["bash"], truth=t48, trap="TR-DECOY", decoy=".markdown file",
       ref_text="list_files docs (recursive) -> count the .md entries = %d" % v, why="A .markdown file and other extensions are decoys.", ref_calls=1)

    # ---- 35449 en two turns: read a value, then change it with the proper tools offered
    f = {"service/relay.toml": lines(["[server]", "listen = \"0.0.0.0:9443\"", "workers = 6", "", "[timeouts]", "connect_timeout = 5", "idle_timeout = 450",
                                        "request_timeout = 45", "upstream_request_timeout = 120", "", "[logging]", "level = \"info\""])}

    def t49(files):
        p = "service/relay.toml"
        return {"files": {p: files[p].replace("\nrequest_timeout = 45\n", "\nrequest_timeout = 60\n")}}
    fin = t49(f)["files"]
    mk("hyb-35449", sub="F0", lang="en", tt="edit_value", desc="Read one config key, then change it, with the usual file tools offered",
       turns=[says("What is request_timeout set to in service/relay.toml?", contains=["45"], token=True, required=["read_file"]),
              {"prompt": "Raise it to 60, leave the other timeouts alone.", "expect": {"required_tools": ["replace_lines"]}}],
       files=f, must=["read_file", "replace_lines"], never=["bash"], truth=t49, trap="TR-DECOY", decoy="upstream_request_timeout",
       case_expect={"files": {p: {"equals": t} for p, t in fin.items()}},
       ref_text="read_file -> 45; replace_lines on the request_timeout line only -> 60.", why="idle_timeout=450 and upstream_request_timeout=120 are near-name decoys.", ref_calls=3, axes=("CON", "VER"))

    # ---- 35450 en date plus 100 days with datetime offered
    f = {"contracts/marlow-lease-terms.txt": lines(["Marlow Row unit 9A - lease terms", "Signed: 2026-03-02", "Lease start: 2026-04-09", "Lease end: 2027-04-08",
                                                      "Deposit: 2 months", "Notice period: 60 days before the end date"])}

    def t50(files):
        import datetime
        import re
        s = re.search(r"Lease start: (\d{4}-\d\d-\d\d)", files["contracts/marlow-lease-terms.txt"]).group(1)
        return {"strings": [(datetime.date.fromisoformat(s) + datetime.timedelta(days=100)).isoformat()]}
    ans = t50(f)["strings"][0]
    mk("hyb-35450", sub="F0", lang="en", tt="policy_calc", desc="Date plus 100 days from a file with the date tool offered",
       turns=[says("What date is 100 days after the lease start date in contracts/marlow-lease-terms.txt? Give it as YYYY-MM-DD.", contains=[ans], required=["datetime"])],
       files=f, must=["datetime", "read_file"], never=["bash"], truth=t50, trap="TR-DECOY", decoy="signed date and end date",
       ref_text="read_file -> start 2026-04-09; datetime add 2400h -> %s" % ans, why="Signed date and end date are decoys.", ref_calls=2)
