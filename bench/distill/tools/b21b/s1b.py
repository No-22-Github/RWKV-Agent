"""Sub 1 (part b): more read-then-write summaries."""
from common import mk


def c11():
    f = {"考勤/9月.csv": "姓名,日期,状态\n张三,09-01,迟到\n李四,09-01,正常\n张三,09-02,正常\n王五,09-02,缺勤\n张三,09-03,迟到\n李四,09-03,迟到\n王五,09-04,缺勤\n"}

    def compute(files):
        d = {}
        for l in files["考勤/9月.csv"].strip().split("\n")[1:]:
            n, _, s = l.split(",")
            if s != "正常":
                d.setdefault(n, {"迟到": 0, "缺勤": 0})[s] += 1
        return {"考勤/异常名单.csv": "姓名,迟到,缺勤\n" + "".join("%s,%d,%d\n" % (n, d[n]["迟到"], d[n]["缺勤"]) for n in sorted(d, key=lambda n: (-(d[n]["迟到"] + d[n]["缺勤"]), n)))}
    mk("tab-31111", sub="summary", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 考勤/9月.csv 里有迟到或缺勤的人列出来，写到 考勤/异常名单.csv：表头“姓名,迟到,缺勤”，次数合计多的排前面，合计一样按姓名排。状态是“正常”的不用管。", None)],
       gist="Attendance anomalies per person.", ref="read; write.", why="counted.", ref_calls=2)


def c12():
    f = {"logs/access.log": "10.0.0.1 GET /home 200\n10.0.0.2 GET /api 500\n10.0.0.1 POST /api 200\n10.0.0.3 GET /home 200\n10.0.0.2 GET /api 502\n10.0.0.2 GET /home 200\n10.0.0.3 GET /api 500\n"}

    def compute(files):
        d = {}
        for l in files["logs/access.log"].strip().split("\n"):
            ip, _, _, code = l.split()
            if code.startswith("5"):
                d[ip] = d.get(ip, 0) + 1
        return {"logs/5xx_by_ip.txt": "".join("%s %d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}
    mk("log-31112", sub="summary", scen_type=("logs", "count_events"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("In logs/access.log, count the 5xx responses per client IP and save them to logs/5xx_by_ip.txt, one line per IP as \"<ip> <count>\", highest count first, ties by IP. IPs with no 5xx are left out.", None)],
       gist="5xx counts per IP.", ref="read; write.", why="counted.", ref_calls=2)


def c13():
    f = {"服务/a.yaml": "name: 订单\nreplicas: 3\nport: 8001\n", "服务/b.yaml": "name: 支付\nreplicas: 2\nport: 8002\n", "服务/c.yaml": "name: 搜索\nreplicas: 5\nport: 8003\n"}

    def compute(files):
        rows = []
        for p in sorted(files):
            d = dict(l.split(": ") for l in files[p].strip().split("\n"))
            rows.append((d["name"], d["port"], d["replicas"]))
        return {"服务/清单.csv": "服务,端口,副本数\n" + "".join("%s,%s,%s\n" % r for r in rows)}
    mk("cfg-31113", sub="summary", scen_type=("config", "merge"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("读一下 服务 目录下三个 yaml，汇总成 服务/清单.csv，表头“服务,端口,副本数”，按文件名 a、b、c 的顺序一行一个服务。", None)],
       gist="Merge three yaml configs into one CSV.", ref="read three; write.", why="ordered by file.", ref_calls=4)


def c14():
    f = {"会议/0912.md": "# 周会 09-12\n\n- 决定：下周三发版\n- 待办：小林 补测试\n- 待办：阿杰 更新文档\n", "会议/0915.md": "# 周会 09-15\n\n- 决定：发版推迟到周五\n- 待办：小林 补测试\n- 待办：丽丽 联系客户\n"}

    def compute(files):
        items = []
        for p in sorted(files):
            for l in files[p].split("\n"):
                if l.startswith("- 待办："):
                    items.append(l[5:] + " (" + p.split("/")[1][:-3] + ")")
        return {"会议/待办汇总.txt": "".join(i + "\n" for i in items)}
    mk("doc-31114", sub="summary", scen_type=("docs", "extract_items"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("把两次周会纪要里所有“待办”收集起来，写进 会议/待办汇总.txt：一条一行，格式“负责人 事项 (会议日期)”，括号里是文件名里的四位日期，按文件日期先后排，同一份里保持原顺序。", None)],
       gist="Collect action items from two meeting notes.", ref="read two; write.", why="verbatim.", ref_calls=3)


def c15():
    f = {"price/list.csv": "item,price\npen,2.5\nbook,18\nbag,64\n", "price/discount.txt": "bag 20%\npen 10%\n"}

    def compute(files):
        d = {}
        for l in files["price/discount.txt"].strip().split("\n"):
            k, v = l.split()
            d[k] = int(v[:-1])
        out = "item,original,final\n"
        for l in files["price/list.csv"].strip().split("\n")[1:]:
            k, p = l.split(",")
            fin = float(p) * (100 - d.get(k, 0)) / 100
            out += "%s,%s,%.2f\n" % (k, p, fin)
        return {"price/final.csv": out}
    mk("tab-31115", sub="summary", scen_type=("tabular", "join"), files=f, compute=compute, traps=("TR-MISSING",),
       turns=[("Apply the discounts in price/discount.txt to price/list.csv and write price/final.csv with the header item,original,final. Keep the original price as written, give final to two decimals, and keep the list's row order. Items without a discount keep their price.", None)],
       gist="Join discounts onto a price list.", ref="read two; write.", why="pen 2.25 book 18.00 bag 51.20.", ref_calls=3)


def c16():
    f = {"报表/订单.jsonl": '{"id":1,"city":"上海","paid":true,"amt":300}\n{"id":2,"city":"北京","paid":false,"amt":120}\n{"id":3,"city":"上海","paid":true,"amt":80}\n{"id":4,"city":"广州","paid":true,"amt":260}\n{"id":5,"city":"北京","paid":true,"amt":90}\n{"id":6,"city":"广州","paid":false,"amt":40}\n'}

    def compute(files):
        import json
        d = {}
        for l in files["报表/订单.jsonl"].strip().split("\n"):
            r = json.loads(l)
            if r["paid"]:
                d[r["city"]] = d.get(r["city"], 0) + r["amt"]
        return {"报表/已付款.json": json.dumps(d, ensure_ascii=False, sort_keys=True, indent=2) + "\n"}
    mk("log-31116", sub="summary", scen_type=("logs", "aggregate_jsonl"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("统计 报表/订单.jsonl 里已付款订单每个城市的金额合计，写成 报表/已付款.json：一个 JSON 对象，键是城市名，值是合计金额（整数），键按字典序，缩进 2 个空格，文件末尾留一个换行。未付款的不计。", None)],
       gist="Paid totals per city as JSON.", ref="read; write.", why="paid only.", ref_calls=2)


def c17():
    f = {"readme/版本.md": "## v1.2.0\n- 修复登录闪退\n- 新增导出\n\n## v1.1.0\n- 优化启动速度\n\n## v1.0.0\n- 首个版本\n"}

    def compute(files):
        out = []
        for l in files["readme/版本.md"].split("\n"):
            if l.startswith("## "):
                out.append(l[3:] + "：")
                n = 0
            elif l.startswith("- "):
                n += 1
                out[-1] = out[-1].split("：")[0] + "：%d 项" % n
        return {"readme/版本统计.txt": "".join(o + "\n" for o in out)}
    mk("doc-31117", sub="summary", scen_type=("docs", "extract_items"), files=f, compute=compute,
       turns=[("数一数 readme/版本.md 里每个版本有几条更新，写到 readme/版本统计.txt，一个版本一行，格式“v1.2.0：2 项”，顺序和原文一致。", None)],
       gist="Count changelog entries per version.", ref="read; write.", why="2,1,1.", ref_calls=2)


def c18():
    f = {"成绩/一班.csv": "学号,姓名,分数\n101,赵一,88\n102,钱二,92\n103,孙三,75\n", "成绩/二班.csv": "学号,姓名,分数\n201,周四,95\n202,吴五,67\n203,郑六,88\n"}

    def compute(files):
        rows = []
        for p, cls in (("成绩/一班.csv", "一班"), ("成绩/二班.csv", "二班")):
            for l in files[p].strip().split("\n")[1:]:
                a, n, s = l.split(",")
                rows.append((cls, n, int(s)))
        rows.sort(key=lambda r: (-r[2], r[1]))
        return {"成绩/总榜.csv": "名次,班级,姓名,分数\n" + "".join("%d,%s,%s,%d\n" % (i + 1, r[0], r[1], r[2]) for i, r in enumerate(rows))}
    mk("tab-31118", sub="summary", scen_type=("tabular", "rank"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("把一班二班的成绩合起来排个总榜，写到 成绩/总榜.csv：表头“名次,班级,姓名,分数”，分数高的在前，同分按姓名排，名次从 1 连续编号（同分也不并列）。", None)],
       gist="Merge two classes into one ranking.", ref="read two; write.", why="no ties.", ref_calls=3)


def c19():
    f = {"env/prod.env": "DB_HOST=10.1.1.5\nDB_PORT=5432\nDB_PASS=s3cr3t\nAPI_KEY=abc123\nLOG_LEVEL=info\nTIMEOUT=30\n"}

    def compute(files):
        out = ""
        for l in files["env/prod.env"].strip().split("\n"):
            k, v = l.split("=", 1)
            out += "%s=%s\n" % (k, "***" if k in ("DB_PASS", "API_KEY") else v)
        return {"env/prod.sample.env": out}
    mk("cfg-31119", sub="summary", scen_type=("config", "edit_value"), files=f, compute=compute, traps=("TR-READONLY",),
       turns=[("Make a shareable copy of env/prod.env as env/prod.sample.env: same keys in the same order, but replace the value of every secret (the password and the API key) with ***. Leave the original alone.", None)],
       gist="Redacted copy of an env file.", ref="read; write sample.", why="two secrets.", ref_calls=2)


def c20():
    f = {"库/借阅.csv": "读者,书名,借出,归还\n甲,算法导论,09-01,09-10\n乙,编译原理,09-02,\n丙,算法导论,09-03,09-12\n甲,操作系统,09-05,\n"}

    def compute(files):
        out = []
        for l in files["库/借阅.csv"].strip().split("\n")[1:]:
            r, b, o, back = l.split(",")
            if not back:
                out.append("%s,%s,%s" % (b, r, o))
        return {"库/未还.csv": "书名,读者,借出\n" + "".join(x + "\n" for x in sorted(out))}
    mk("tab-31120", sub="summary", scen_type=("tabular", "filter_count"), files=f, compute=compute, traps=("TR-MISSING",),
       turns=[("从 库/借阅.csv 挑出还没归还的记录，写到 库/未还.csv，列改成“书名,读者,借出”，按书名排序（书名相同就按读者排）。", None)],
       gist="Unreturned loans list.", ref="read; write.", why="two rows.", ref_calls=2)


BUILDERS = [c11, c12, c13, c14, c15, c16, c17, c18, c19, c20]
