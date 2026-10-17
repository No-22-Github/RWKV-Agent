"""b21l sub comp: one request, two things to finish (33349-33364)."""
from common import mk, page, L, rng, WEB

B = []
BR = WEB + ["read_file", "write_file"]


def reg(f):
    B.append(f)
    return f


@reg
def c49():
    web = [page("Quartz", "https://quartznotes.app/changelog", "Quartz 更新日志", "Quartz 笔记的版本更新。",
                "# 更新日志\n\n当前版本：6.3.1（2026-09-09）\n上一版本：6.2.4\n", "2026-09-09")]
    files = {"笔记/待办.md": L("# 待办", "- [x] 买墨水", "- [ ] 预约牙医", "- [ ] 续订域名", "- [x] 交水费", "- [ ] 整理照片", "- [ ] 回复房东", "- [x] 寄快递")}

    def compute(files, web):
        import re
        n = sum(1 for l in files["笔记/待办.md"].splitlines() if l.startswith("- [ ]"))
        v = re.search(r"当前版本：(\S+?)（", [w for w in web if "quartznotes" in w["url"]][0]["content"]).group(1)
        return {}, [[str(n), v]]
    mk("hyb-33349", sub="comp", desc="Count unchecked todo items and read the current app version off its changelog page", files=files, web=web,
       turns=[{"p": "帮我数一下 笔记/待办.md 里还有几项没打勾，顺便查查 Quartz 笔记软件现在的版本号是多少。", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file"], traps=["TR-MULTISRC"], notes="4 open items ; 6.3.1")


@reg
def c50():
    web = [page("Fennel", "https://fennelhq.com/pricing", "Fennel pricing", "Plans and prices.",
                "# Plans\n\nStarter: $9 per user per month\nTeam: $19 per user per month\nBusiness: $39 per user per month\n", "2026-09-06")]
    files = {"notes/todo.md": L("# Todo", "- [ ] renew passport", "- [x] file taxes", "- [ ] book dentist", "- [ ] call landlord")}

    def compute(files, web):
        import re
        pg = [w for w in web if "fennelhq" in w["url"]][0]["content"]
        pr = dict(re.findall(r"(\w+): \$(\d+) per user", pg))
        n = sum(1 for l in files["notes/todo.md"].splitlines() if l.startswith("- [ ]"))
        t = files["notes/todo.md"].replace("- [ ] renew passport", "- [x] renew passport")
        return {"notes/todo.md": t}, [[str(n), pr["Starter"]], [pr["Team"]]]
    mk("hyb-33350", sub="comp", desc="Count open todos and read the Starter price; then tick the first item and read the Team price", files=files, web=web,
       turns=[{"p": "How many open items are left in notes/todo.md, and what does Fennel's Starter plan cost per user per month?", "req": ["web_fetch"]},
              {"p": "Tick off the first open item in the todo list, and tell me what the Team plan costs per user."}],
       compute=compute, must=BR, traps=["TR-MULTISRC"], rc=6, notes="3 open ; 9 ; edit first; 19")


@reg
def c51():
    web = [page("Ledgerly", "https://ledgerly.dev/download", "Ledgerly 下载", "最新版本下载。", "# 下载 Ledgerly\n\n当前稳定版：1.9.0\n", "2026-09-01")]
    files = {"CHANGELOG.md": L("# 变更记录", "", "## 1.8.2 (2026-07-14)", "- 修复导出乱码", "", "## 1.8.1 (2026-06-01)", "- 性能优化")}

    def compute(files, web):
        import re
        loc = re.search(r"## (\d+\.\d+\.\d+)", files["CHANGELOG.md"]).group(1)
        new = re.search(r"当前稳定版：(\S+)", [w for w in web if "ledgerly" in w["url"]][0]["content"]).group(1)
        return {"升级提示.txt": "本地=%s\n最新=%s\n" % (loc, new)}, [[loc, new]]
    mk("hyb-33351", sub="comp", desc="Compare the local changelog version with the published one and record both in a note", files=files, web=web,
       turns=[{"p": "我们本地 CHANGELOG.md 里最新一条是哪个版本？Ledgerly 官网现在是哪个版本？把两个都写进 升级提示.txt，格式两行：“本地=…”“最新=…”，也说给我听。", "req": ["web_fetch"]}],
       compute=compute, must=BR, traps=["TR-WEBSTALE"], loose=["升级提示.txt"], notes="top changelog entry is 1.8.2")


@reg
def c52():
    web = [page("Cinder", "https://status.cinderhost.net", "Cinder Host status", "Current system status.",
                "# Cinder Host status\n\nAll systems operational. No open incidents.\nLast incident: 2026-08-29 (resolved)\n", "2026-09-16"),
           page("Cinder", "https://status.cinderhost.net/maintenance", "Cinder Host maintenance", "Scheduled work.",
                "# Scheduled maintenance\n\n2026-09-23 01:00-03:00 UTC: network upgrade (EU region)\n", "2026-09-12")]
    files = {"app.ini": L("[server]", "port = 8080", "timeout = 30", "workers = 4"), "ops.md": "ops notes\n"}

    def compute(files, web):
        return {"app.ini": files["app.ini"].replace("timeout = 30", "timeout = 45")}, [["operational", "Operational", "no incident", "No incident", "no open incident", "No open incident", "no active incident", "no current incident", "No current incident", "no ongoing"], ["2026-09-23", "September 23", "Sept 23", "Sep 23", "23 September", "23 Sep", "9/23", "09-23"]]
    mk("hyb-33352", sub="comp", desc="Raise a timeout in app.ini and report whether the host status page shows an incident, then the next maintenance", files=files, web=web,
       turns=[{"p": "Set timeout to 45 in app.ini, and while you're at it check whether Cinder Host's status page shows any incident right now.", "req": ["web_fetch"], "any": True},
              {"p": "Also, is any maintenance scheduled? Check their maintenance page and give me the date.", "any": True}],
       compute=compute, must=BR, traps=["TR-MULTISRC"], rc=6, notes="no incident; maintenance 2026-09-23")


@reg
def c53():
    files = {"部署/a.cfg": L("name=gateway", "listen_port=9443", "tls=on"), "部署/b.cfg": L("name=ledger", "host=db-prod-07.internal", "pool=20"), "部署/c.cfg": L("host=db-test-01.internal", "listen_port=9000")}

    def compute(files, web):
        import re
        p = re.search(r"listen_port=(\d+)", files["部署/a.cfg"]).group(1)
        h = re.search(r"host=(\S+)", files["部署/b.cfg"]).group(1)
        return {"部署/target.txt": "%s:%s\n" % (h, p)}, [[h, p]]
    mk("hyb-33353", sub="comp", desc="Read the port from one config and the host from another and join them into host:port in a new file", files=files, web=[],
       turns=[{"p": "把 部署/a.cfg 里的监听端口和 部署/b.cfg 里的主机名读出来，拼成“主机:端口”写进 部署/target.txt，再告诉我拼出来是什么。"}],
       compute=compute, must=["read_file", "write_file"], traps=["TR-MULTISRC"], loose=["部署/target.txt"], notes="c.cfg is a decoy")


@reg
def c54():
    web = [page("季度目标", "https://intra.oriental-trade.cn/targets/2026q3", "2026 Q3 区域销售目标", "各大区本季度目标。",
                "# 2026 Q3 区域销售目标\n\n华东：480 万元\n华南：360 万元\n华北：300 万元\n", "2026-07-01")]
    r = rng(54)
    rows = ["大区,客户,金额_万元"]
    for i in range(160):
        rows.append("%s,客户%03d,%d" % (r.choice(["华东", "华南", "华北"]), i, r.randint(1, 6)))
    files = {"销售/q3.csv": "\n".join(rows) + "\n"}

    def compute(files, web):
        import re
        pg = [w for w in web if "oriental-trade" in w["url"]][0]["content"]
        tgt = {k: int(v) for k, v in re.findall(r"(华.)：(\d+) 万元", pg)}
        s = {}
        for l in files["销售/q3.csv"].splitlines()[1:]:
            a = l.split(",")
            s[a[0]] = s.get(a[0], 0) + int(a[2])
        return {}, [[str(s["华东"]), str(tgt["华东"])], [str(s["华南"]), str(int(round(s["华南"] * 100.0 / tgt["华南"])))]]
    mk("hyb-33354", sub="comp", desc="East region sales total and its published target, then the same two numbers plus completion percent for the south", files=files, web=web,
       turns=[{"p": "销售/q3.csv 里华东大区这个季度的销售总额是多少万元？再对一下内网目标页上华东的目标是多少。", "req": ["web_fetch"]},
              {"p": "华南也一样：销售总额，加上完成了目标的百分之几（四舍五入取整数）。"}],
       compute=compute, must=WEB + ["read_file", "bash"], traps=["TR-MULTISRC"], rc=6, notes="sum by region ; target from page")


@reg
def c55():
    web = [page("CDN error codes", "https://edgeshield.example.com/docs/errors", "EdgeShield error codes", "Meaning of 52x errors.",
                "# EdgeShield error codes\n\n520: origin returned an empty or unknown response\n522: connection to origin timed out\n524: origin took too long to answer; a timeout occurred after the connection was made\n", "2026-05-14")]
    r = rng(55)
    rows = []
    for i in range(215):
        rows.append("2026-09-15T%02d:%02d:%02d %s %s" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), r.choice(["GET", "POST"]), r.choice(["upstream ok", "upstream ok", "cache hit", "upstream timeout", "client reset"])))
    files = {"logs/edge.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        n = sum(1 for l in files["logs/edge.log"].splitlines() if "upstream timeout" in l)
        return {}, [[str(n), "timeout"]]
    mk("hyb-33355", sub="comp", desc="Count 'upstream timeout' log lines and explain error 524 from the CDN docs", files=files, web=web,
       turns=[{"p": "Count how many lines in logs/edge.log say 'upstream timeout', and also look up on EdgeShield's error-code docs what a 524 means.", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "bash"], traps=["TR-MULTISRC"], notes="count lines ; 524 = origin timeout after connection")


@reg
def c56():
    web = [page("Basalt", "https://basalt-ide.dev/requirements", "Basalt 系统要求", "各平台最低系统要求。",
                "# 系统要求\n\n| 平台 | 最低版本 | 内存 |\n|---|---|---|\n| macOS | 13 | 8 GB |\n| Windows | 10 (22H2) | 8 GB |\n| Linux | glibc 2.31 | 4 GB |\n", "2026-08-19")]
    files = {"README.md": L("# 内部工具链", "", "开发机要求：macOS 12 或更新。", "编辑器：Basalt")}

    def compute(files, web):
        return {}, [["macOS 12"], ["10 (22H2)"]]
    mk("hyb-33356", sub="comp", desc="Quote the platform requirement in the README and compare with the vendor's requirements page; then switch to Windows", files=files, web=web,
       turns=[{"p": "README.md 里写的开发机系统要求是什么？Basalt 官网上 macOS 的最低版本又是多少？我们的要求够不够？", "req": ["web_fetch"]},
              {"p": "补充一下，有几个同事用 Windows。Basalt 对 Windows 的最低版本要求是什么？"}],
       compute=compute, must=WEB + ["read_file"], traps=["TR-MULTISRC"], rc=5, notes="README says macOS 12; page says 13 (README too low)")


@reg
def c57():
    web = [page("汇率", "https://rates.jinxin-bank.cn/cny", "锦信银行 本月结汇价", "本月美元结汇价。", "# 本月结汇价\n\n美元/人民币：7.10（2026年9月）\n", "2026-09-01")]
    files = {"财务/invoice_us.txt": L("发票号：US-2209", "金额：2400 美元", "付款期限：2026-10-15")}

    def compute(files, web):
        import re
        rate = float(re.search(r"美元/人民币：([\d.]+)", web[0]["content"]).group(1))
        usd = int(re.search(r"金额：(\d+) 美元", files["财务/invoice_us.txt"]).group(1))
        v = round(usd * rate, 2)
        return {"财务/折算.txt": "折算金额=%d\n" % round(v)}, [[str(int(round(v))), "{:,}".format(int(round(v)))]]
    mk("hyb-33357", sub="comp", desc="Convert a dollar invoice at the bank's rate and save the yuan amount in a note", files=files, web=web,
       turns=[{"p": "财务/invoice_us.txt 这张美元发票按锦信银行页面上本月的美元结汇价折合多少人民币？把结果写到 财务/折算.txt，一行“折算金额=数字”，数字不带逗号。", "any": True, "req": ["web_fetch"]}],
       compute=compute, must=BR + ["calculator"], traps=["TR-DIRMAP"], loose=["财务/折算.txt"], notes="2400 * 7.10 = 17040")


@reg
def c58():
    web = [page("Basil DB", "https://basildb.org/docs/tuning", "Basil DB tuning guide", "Recommended settings for production.",
                "# Production tuning\n\nmax_connections: 200 for servers with 16 GB RAM or more\nshared_buffers: 4GB\nwork_mem: 32MB\n", "2026-06-22")]
    files = {"db.conf": L("# basil db", "max_connections = 80", "shared_buffers = 4GB", "work_mem = 32MB")}

    def compute(files, web):
        return {"db.conf": files["db.conf"].replace("max_connections = 80", "max_connections = 200")}, [["80", "200"], ["200"]]
    mk("hyb-33358", sub="comp", desc="Report current max_connections and the guide's recommendation, then apply it", files=files, web=web,
       turns=[{"p": "What is max_connections set to in db.conf, and what does Basil DB's tuning guide recommend for a 16 GB server?", "req": ["web_fetch"]},
              {"p": "OK, apply the recommended value in db.conf and tell me which value you replaced."}],
       compute=compute, must=BR, traps=["TR-MULTISRC"], rc=6, notes="80 -> 200")


@reg
def c59():
    web = [page("Granite", "https://granitejs.dev/migrate/v5", "Granite v5 migration", "What replaces removed APIs.",
                "# Migrating to v5\n\n`oldQuery()` was removed. Use `query()` with the `legacy: false` option.\n`bind()` is unchanged.\n", "2026-07-28")]
    files = {"docs/setup.md": "Call oldQuery() first (deprecated).\n", "docs/usage.md": "Use bind() freely.\n", "docs/faq.md": "oldQuery is deprecated since v4.\n", "docs/intro.md": "Welcome.\n"}

    def compute(files, web):
        hits = sorted(p for p, t in files.items() if "deprecated" in t)
        return {}, [["docs/setup.md", "docs/faq.md", "query()"]]
    mk("hyb-33359", sub="comp", desc="List docs that call something deprecated and name its replacement from the migration page", files=files, web=web,
       turns=[{"p": "Which files under docs/ mention 'deprecated', and what does Granite's v5 migration page say to use instead of oldQuery()?", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["search_text", "read_file"], traps=["TR-MULTISRC"], notes="setup.md and faq.md ; query()")


@reg
def c60():
    web = [page("文具", "https://www.mingzhi-stationery.cn/shop/price", "铭智文具 官网价目", "文具官网零售价。",
                "# 官网零售价\n\n中性笔（12支盒）：18.5 元\n A4 复印纸（箱）：148 元\n 回形针（盒）：6 元\n", "2026-09-10")]
    files = {"采购/价目.csv": L("品名,我们的价格", "中性笔（12支盒）,21", "A4 复印纸（箱）,139", "回形针（盒）,6")}

    def compute(files, web):
        return {}, [["21", "18.5"], ["139", "148"]]
    mk("hyb-33360", sub="comp", desc="Compare our price for one item with the shop's price, then another row", files=files, web=web,
       turns=[{"p": "我们价目表里中性笔一盒多少钱？铭智文具官网上同款现在卖多少？", "req": ["web_fetch"]},
              {"p": "A4 复印纸也对一下，我们的价和官网价分别是多少？"}],
       compute=compute, must=WEB + ["read_file"], traps=["TR-MULTISRC"], rc=5, notes="21 vs 18.5 ; 139 vs 148")


@reg
def c61():
    web = [page("云栈", "https://status.yunzhan-cloud.cn/today", "云栈云 服务状态", "今日服务状态与维护公告。",
                "# 服务状态（2026-09-16）\n\n对象存储：正常\n云数据库：计划维护 22:00-23:30\n负载均衡：正常\n", "2026-09-16")]
    r = rng(61)
    rows = []
    last = ""
    for d in range(1, 16):
        for h in (2, 14):
            ok = r.random() > 0.2
            rows.append("2026-09-%02d %02d:00 %s" % (d, h, "成功" if ok else "失败"))
            if ok:
                last = "2026-09-%02d %02d:00" % (d, h)
    files = {"运维/backup.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        ok = [l[:16] for l in files["运维/backup.log"].splitlines() if l.endswith("成功")]
        return {}, [[ok[-1], "22:00"]]
    mk("hyb-33361", sub="comp", desc="Last successful backup time from a log and the database maintenance slot on the status page", files=files, web=web,
       turns=[{"p": "运维/backup.log 里最近一次成功的备份是什么时候（照日志里的写法给我日期和时间）？另外云栈今天的状态页上，云数据库有没有计划维护，几点开始？", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "bash"], traps=["TR-MULTISRC"], notes="last success line ; 22:00")


@reg
def c62():
    web = [page("http status", "https://httpref.example.dev/status", "HTTP status reference", "Meaning of common status codes.",
                "# Status codes\n\n429 Too Many Requests: the client sent too many requests in a given time window; slow down and retry later.\n503 Service Unavailable: the server cannot handle the request right now, often due to overload or maintenance.\n", "2026-04-02")]
    r = rng(62)
    rows = []
    for i in range(210):
        rows.append("%s %s request %d" % ("2026-09-15", r.choice(["INFO", "INFO", "INFO", "WARN", "ERROR"]), i))
    files = {"logs/app.log": "\n".join(rows) + "\n"}

    def compute(files, web):
        ls = files["logs/app.log"].splitlines()
        e = sum(1 for l in ls if " ERROR " in l)
        w = sum(1 for l in ls if " WARN " in l)
        return {}, [[str(e), "Too Many Requests"], [str(w), "Service Unavailable"]]
    mk("hyb-33362", sub="comp", desc="Count ERROR lines and look up 429; then WARN lines and 503", files=files, web=web,
       turns=[{"p": "How many ERROR lines are in logs/app.log, and what does the HTTP status reference at httpref.example.dev say 429 means?", "req": ["web_fetch"]},
              {"p": "Same for WARN lines, and what does 503 mean on that reference?"}],
       compute=compute, must=WEB + ["read_file", "bash"], traps=["TR-MULTISRC"], rc=6, notes="count levels ; names from page")


@reg
def c63():
    web = [page("教育局", "https://jyj.lakeview-district.cn/notice/2026-fall", "湖景区教育局 秋季学期通知", "开学时间安排。",
                "# 2026 秋季学期安排\n\n开学报到：2026年9月1日\n正式上课：2026年9月2日\n国庆放假：10月1日至10月7日\n", "2026-08-10")]
    r = rng(63)
    rows = ["姓名,班级"]
    for i in range(172):
        rows.append("生%03d,%s" % (i, r.choice(["初一1班", "初一2班", "初一3班"])))
    files = {"学校/学生名单.csv": "\n".join(rows) + "\n", "学校/日程.md": L("# 秋季日程", "", "- 8月28日 教师返校")}

    def compute(files, web):
        import re
        n = len(files["学校/学生名单.csv"].splitlines()) - 1
        d = re.search(r"正式上课：(\S+)", web[0]["content"]).group(1)
        return {"学校/日程.md": files["学校/日程.md"] + "- 正式上课：%s\n" % d}, [[str(n), d]]
    mk("hyb-33363", sub="comp", desc="Count students in a roster and append the official first-class date from the district notice to the schedule", files=files, web=web,
       turns=[{"p": "学校/学生名单.csv 一共多少个学生？再从教育局的通知里找到正式上课的日期，加到 学校/日程.md 最后一行，格式“- 正式上课：<日期>”。", "req": ["web_fetch"]}],
       compute=compute, must=BR + ["bash"], traps=["TR-DECOY"], loose=["学校/日程.md"], notes="172 ; 2026年9月2日 (not 报到 date)")


@reg
def c64():
    web = [page("Willow Parts", "https://willowparts.example.com/", "Willow Parts - industrial fasteners", "Family-run fastener supplier since 1974.",
                "# Willow Parts\n\nFasteners for people who build things.\nFree shipping on orders over $250.\n", "2026-08-30")]
    entries = ["{\"name\": \"vendor%02d\", \"active\": %s}" % (i, "true" if i % 3 else "false") for i in range(1, 18)]
    files = {"procurement/vendors.json": "[\n  " + ",\n  ".join(entries) + "\n]\n"}

    def compute(files, web):
        import json
        v = json.loads(files["procurement/vendors.json"])
        n = sum(1 for x in v if x["active"])
        return {}, [[str(len(v)), str(n), "250"]]
    mk("hyb-33364", sub="comp", desc="Count vendors and active vendors in a json file and read the free-shipping threshold off a supplier site", files=files, web=web,
       turns=[{"p": "How many vendors are in procurement/vendors.json, how many of them are marked active, and at what order value does Willow Parts offer free shipping (see their homepage)?", "req": ["web_fetch"]}],
       compute=compute, must=WEB + ["read_file", "bash"], traps=["TR-MULTISRC"], notes="17 ; 12 ; $250")
