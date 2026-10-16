"""Sub 2: generate files to an explicit format."""
from common import mk


def c21():
    f = {"客户/名单.csv": "id,name,signup\n7,陈晨,2026-03-05\n12,刘洋,2025-11-30\n3,黄河,2026-01-19\n"}

    def compute(files):
        out = "编号\t姓名\t注册日期\n"
        rows = [l.split(",") for l in files["客户/名单.csv"].strip().split("\n")[1:]]
        for i, n, d in sorted(rows, key=lambda r: int(r[0])):
            y, m, dd = d.split("-")
            out += "%04d\t%s\t%s/%s/%s\n" % (int(i), n, dd, m, y)
        return {"客户/名单.tsv": out}
    mk("tab-31121", sub="format", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-DATEFMT",),
       turns=[("把 客户/名单.csv 转成 客户/名单.tsv：用制表符分隔，表头改成“编号、姓名、注册日期”，编号补成 4 位数字（前面补 0），注册日期改成 日/月/年（两位日、两位月、四位年，用斜杠隔开），按编号从小到大排。", None)],
       gist="Convert CSV to TSV with padded ids and DD/MM/YYYY dates.", ref="read; write.", why="explicit.", ref_calls=2)


def c22():
    f = {"hr/people.json": '[{"name":"Ann","dept":"ops","age":31},{"name":"Ben","dept":"dev","age":45},{"name":"Cy","dept":"dev","age":28},{"name":"Di","dept":"ops","age":39}]\n'}

    def compute(files):
        import json
        d = json.loads(files["hr/people.json"])
        out = "dept,count,oldest\n"
        g = {}
        for p in d:
            g.setdefault(p["dept"], []).append(p)
        for k in sorted(g):
            out += "%s,%d,%s\n" % (k, len(g[k]), max(g[k], key=lambda p: p["age"])["name"])
        return {"hr/dept.csv": out}
    mk("tab-31122", sub="format", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("From hr/people.json build hr/dept.csv with columns dept,count,oldest (the name of the oldest person in the department). Departments in alphabetical order, header line first, no spaces after commas.", None)],
       gist="Department summary from JSON to CSV.", ref="read; write.", why="dev=2 Ben; ops=2 Di.", ref_calls=2)


def c23():
    f = {"待办/杂项.txt": "买牛奶\n给妈妈打电话\n交水电费\n预约牙医\n整理照片\n"}

    def compute(files):
        ls = files["待办/杂项.txt"].strip().split("\n")
        return {"待办/清单.md": "# 待办清单\n\n" + "".join("%d. [ ] %s\n" % (i + 1, l) for i, l in enumerate(ls))}
    mk("doc-31123", sub="format", scen_type=("docs", "write_structured"), files=f, compute=compute,
       turns=[("把 待办/杂项.txt 做成 待办/清单.md：第一行是“# 待办清单”，空一行，然后每条一行，写成“1. [ ] 买牛奶”这样带序号和复选框的形式，顺序不变。", None)],
       gist="Checklist Markdown with numbering.", ref="read; write.", why="explicit.", ref_calls=2)


def c24():
    f = {"配置/servers.txt": "web1 10.0.0.11 80\ndb1 10.0.0.21 5432\ncache1 10.0.0.31 6379\n"}

    def compute(files):
        out = "[servers]\n"
        for l in files["配置/servers.txt"].strip().split("\n"):
            n, ip, p = l.split()
            out += "%s ansible_host=%s ansible_port=%s\n" % (n, ip, p)
        return {"配置/inventory.ini": out}
    mk("cfg-31124", sub="format", scen_type=("config", "merge"), files=f, compute=compute, traps=("TR-DELIM",),
       turns=[("用 配置/servers.txt 生成 配置/inventory.ini：第一行 [servers]，然后每台机器一行，写成 “名字 ansible_host=IP ansible_port=端口”，顺序跟原文一样。", None)],
       gist="Generate an ansible inventory.", ref="read; write.", why="explicit.", ref_calls=2)


def c25():
    f = {"销售/订单.csv": "order,customer,total\nA-1,绿洲,1280.5\nA-2,晨光,860\nA-3,绿洲,420.25\n"}

    def compute(files):
        import json
        out = []
        for l in files["销售/订单.csv"].strip().split("\n")[1:]:
            o, c, t = l.split(",")
            out.append({"order": o, "customer": c, "total": float(t)})
        return {"销售/订单.json": json.dumps(out, ensure_ascii=False, indent=2) + "\n"}
    mk("tab-31125", sub="format", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-NUMFMT",),
       turns=[("把 销售/订单.csv 转成 销售/订单.json：一个数组，每行一个对象，键是 order、customer、total，total 用数字不要加引号，缩进 2 个空格，文件末尾换行。", None)],
       gist="CSV to JSON array of objects.", ref="read; write.", why="json.dumps indent 2.", ref_calls=2,
       loose=())


def c26():
    f = {"公告/周报.md": "# 周报\n\n本周完成：登录改版、支付对账。\n下周计划：压测、灰度。\n风险：测试机不足。\n"}

    def compute(files):
        d = {}
        for l in files["公告/周报.md"].split("\n"):
            if "：" in l:
                k, v = l.split("：", 1)
                d[k] = v
        out = "## 本周完成\n"
        out += "".join("- %s\n" % x for x in d["本周完成"].rstrip("。").split("、"))
        out += "\n## 下周计划\n" + "".join("- %s\n" % x for x in d["下周计划"].rstrip("。").split("、"))
        out += "\n## 风险\n- %s\n" % d["风险"].rstrip("。")
        return {"公告/周报_条目.md": out}
    mk("doc-31126", sub="format", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 公告/周报.md 拆成条目版，存为 公告/周报_条目.md：用三个二级标题“## 本周完成”“## 下周计划”“## 风险”，每个事项单独一行以“- ”开头，去掉句末的句号，标题之间空一行，不要保留原来的一级标题。", None)],
       gist="Split a weekly report into bullet sections.", ref="read; write.", why="explicit.", ref_calls=2)


def c27():
    f = {"日志/events.log": "09-16T01:02:03 login alice\n09-16T01:05:44 logout alice\n09-16T02:10:00 login bob\n09-16T02:11:30 login carol\n"}

    def compute(files):
        out = "time,event,user\n"
        for l in files["日志/events.log"].strip().split("\n"):
            t, e, u = l.split()
            out += "%s,%s,%s\n" % (t.split("T")[1], e.upper(), u.capitalize())
        return {"日志/events.csv": out}
    mk("log-31127", sub="format", scen_type=("logs", "count_events"), files=f, compute=compute, traps=("TR-DATEFMT",),
       turns=[("Convert 日志/events.log to 日志/events.csv. Columns time,event,user; keep only the clock part of the timestamp (HH:MM:SS, drop the date), write the event in UPPERCASE and capitalise the first letter of each user name. Same row order.", None)],
       gist="Log to CSV with case conversions.", ref="read; write.", why="explicit.", ref_calls=2)


def c28():
    f = {"财务/流水.csv": "日期,摘要,收入,支出\n09-01,工资,8000,\n09-02,房租,,2500\n09-05,餐饮,,320\n09-08,兼职,600,\n"}

    def compute(files):
        bal = 0
        out = "日期,摘要,金额,余额\n"
        for l in files["财务/流水.csv"].strip().split("\n")[1:]:
            d, s, i, o = l.split(",")
            a = int(i) if i else -int(o)
            bal += a
            out += "%s,%s,%+d,%d\n" % (d, s, a, bal)
        return {"财务/余额表.csv": out}
    mk("tab-31128", sub="format", scen_type=("tabular", "policy_calc"), files=f, compute=compute, traps=("TR-SIGN",),
       turns=[("根据 财务/流水.csv 生成 财务/余额表.csv：表头“日期,摘要,金额,余额”，金额一列收入写成 +数字、支出写成 -数字，余额是从第一行起的累计（起始为 0），按原顺序。", None)],
       gist="Running balance table with signed amounts.", ref="read; write.", why="8000,5500,5180,5780.", ref_calls=2)


def c29():
    f = {"词表/words.txt": "banana\napple\ncherry\napple\ndate\nbanana\n"}

    def compute(files):
        d = {}
        for w in files["词表/words.txt"].strip().split("\n"):
            d[w] = d.get(w, 0) + 1
        return {"词表/频次.txt": "".join("%s\t%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}
    mk("doc-31129", sub="format", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-DUPROW",),
       turns=[("Write the word frequencies of 词表/words.txt to 词表/频次.txt, one word per line as \"word<TAB>count\" (a real tab character), most frequent first, equal counts in alphabetical order.", None)],
       gist="Word frequency list tab separated.", ref="read; write.", why="apple2 banana2 cherry1 date1.", ref_calls=2)


def c30():
    f = {"课表/周一.txt": "08:00 数学\n09:00 语文\n10:30 英语\n", "课表/周二.txt": "08:00 物理\n09:30 化学\n"}

    def compute(files):
        out = "星期,时间,课程\n"
        for p, d in (("课表/周一.txt", "周一"), ("课表/周二.txt", "周二")):
            for l in files[p].strip().split("\n"):
                t, c = l.split()
                out += "%s,%s,%s\n" % (d, t, c)
        return {"课表/总课表.csv": out}
    mk("doc-31130", sub="format", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("把周一、周二两份课表合并成 课表/总课表.csv，表头“星期,时间,课程”，先周一后周二，每天内部按时间顺序。", None)],
       gist="Merge two day schedules.", ref="read two; write.", why="5 rows.", ref_calls=3)


def c31():
    f = {"商品/库存.csv": "code,name,stock\n5,耳机,12\n17,键盘,0\n102,鼠标,34\n"}

    def compute(files):
        out = "| 编码 | 名称 | 库存 |\n| ---: | :--- | ---: |\n"
        for l in files["商品/库存.csv"].strip().split("\n")[1:]:
            c, n, s = l.split(",")
            out += "| %s | %s | %s |\n" % (c.zfill(5), n, s)
        return {"商品/库存.md": out}
    mk("tab-31131", sub="format", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 商品/库存.csv 做成 商品/库存.md 里的 Markdown 表：表头“| 编码 | 名称 | 库存 |”，分隔行写成“| ---: | :--- | ---: |”（编码和库存右对齐，名称左对齐），编码补成 5 位带前导 0，行顺序不变。", None)],
       gist="Markdown table with alignment row and zero padded codes.", ref="read; write.", why="explicit.", ref_calls=2)


def c32():
    f = {"通讯/contacts.txt": "Zhang San,13800001111\nLi Si,13900002222\nWang Wu,13700003333\n"}

    def compute(files):
        out = "BEGIN\n"
        out = ""
        for l in files["通讯/contacts.txt"].strip().split("\n"):
            n, p = l.split(",")
            out += "BEGIN:VCARD\nFN:%s\nTEL:%s\nEND:VCARD\n" % (n, p)
        return {"通讯/contacts.vcf": out}
    mk("doc-31132", sub="format", scen_type=("docs", "write_structured"), files=f, compute=compute,
       turns=[("Create 通讯/contacts.vcf from 通讯/contacts.txt. For every person write four lines: BEGIN:VCARD, FN:<name>, TEL:<phone>, END:VCARD (nothing between cards), in the original order.", None)],
       gist="vCard file from contact list.", ref="read; write.", why="explicit.", ref_calls=2)


BUILDERS = [c21, c22, c23, c24, c25, c26, c27, c28, c29, c30, c31, c32]
