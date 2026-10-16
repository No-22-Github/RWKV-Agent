"""Sub 1 (part a): read files, write a new summary file."""
from common import mk, WEBOFF


def c01():
    f = {"数据/门店销售.csv": "门店,品类,金额\n东门,饮料,120\n西门,零食,80\n东门,零食,45\n北门,饮料,60\n西门,饮料,95\n东门,饮料,30\n北门,零食,25\n"}

    def compute(files):
        rows = [l.split(",") for l in files["数据/门店销售.csv"].strip().split("\n")[1:]]
        tot = {}
        for s, _, a in rows:
            tot[s] = tot.get(s, 0) + int(a)
        return {"数据/门店汇总.csv": "门店,总金额\n" + "".join("%s,%d\n" % (k, tot[k]) for k in sorted(tot, key=lambda k: (-tot[k], k)))}
    mk("tab-31101", sub="summary", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 数据/门店销售.csv 按门店汇总金额，写到 数据/门店汇总.csv：表头是“门店,总金额”，每店一行，总金额从高到低排，金额相同的按门店名排。", None)],
       gist="Summarize store sales by store into a new CSV sorted by total descending.",
       ref="read_file 数据/门店销售.csv; write_file 数据/门店汇总.csv.", why="Totals computed from the fixture; sort is fully specified.", ref_calls=2)


def c02():
    f = {"日志/app.log": "2026-09-10 08:01:12 INFO start\n2026-09-10 08:03:40 ERROR db timeout\n2026-09-10 09:15:02 WARN slow query\n2026-09-10 09:20:11 ERROR db timeout\n2026-09-10 10:02:55 ERROR disk full\n2026-09-10 10:30:00 INFO tick\n2026-09-10 11:45:09 WARN slow query\n2026-09-10 12:00:01 ERROR db timeout\n"}

    def compute(files):
        c = {}
        for l in files["日志/app.log"].strip().split("\n"):
            p = l.split(" ", 3)
            if p[2] == "ERROR":
                c[p[3]] = c.get(p[3], 0) + 1
        return {"日志/错误统计.txt": "".join("%s: %d\n" % (k, c[k]) for k in sorted(c, key=lambda k: (-c[k], k)))}
    mk("log-31102", sub="summary", scen_type=("logs", "count_events"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("看一下 日志/app.log，把 ERROR 级别的消息按出现次数统计，写进 日志/错误统计.txt，每行格式“消息: 次数”，次数多的在前，次数一样按消息字母序。WARN 的不算。", None)],
       gist="Count ERROR messages in the log into a text file.", ref="read_file log; write_file stats.", why="Only ERROR lines counted.", ref_calls=2)


def c03():
    f = {"配置/dev.env": "HOST=dev.local\nPORT=8080\nDEBUG=true\nCACHE=off\n", "配置/prod.env": "HOST=api.example.com\nPORT=443\nDEBUG=false\nCACHE=on\nREGION=cn-east\n"}

    def compute(files):
        def parse(t):
            return dict(l.split("=", 1) for l in t.strip().split("\n"))
        a, b = parse(files["配置/dev.env"]), parse(files["配置/prod.env"])
        keys = sorted(set(a) | set(b))
        out = "| 键 | dev | prod |\n|---|---|---|\n"
        for k in keys:
            out += "| %s | %s | %s |\n" % (k, a.get(k, "-"), b.get(k, "-"))
        return {"配置/对比.md": out}
    mk("cfg-31103", sub="summary", scen_type=("config", "merge"), files=f, compute=compute, traps=("TR-MISSING",),
       turns=[("把 配置/dev.env 和 配置/prod.env 做个对比表写到 配置/对比.md：Markdown 表格，列是 键、dev、prod，键按字母序，某个环境没有这个键就填 -。", None)],
       gist="Write a Markdown comparison table of two env files.", ref="read both; write_file md.", why="Keys union sorted.", ref_calls=3)


def c04():
    f = {"docs/team.md": "# Team\n\n- Alice Wong — backend — alice@corp.test\n- Bob Lee — design — bob@corp.test\n- Carol Diaz — backend — carol@corp.test\n- Dan Kim — QA — dan@corp.test\n"}

    def compute(files):
        rows = []
        for l in files["docs/team.md"].split("\n"):
            if l.startswith("- "):
                n, r, e = [x.strip() for x in l[2:].split("—")]
                rows.append((n, r, e))
        out = "name,role,email\n" + "".join("%s,%s,%s\n" % t for t in sorted(rows, key=lambda t: t[0].split()[-1]))
        return {"docs/team.csv": out}
    mk("doc-31104", sub="summary", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-DELIM",),
       turns=[("Turn the people list in docs/team.md into docs/team.csv with the header name,role,email. Sort the rows by last name, one person per line, no extra columns.", None)],
       gist="Convert a bullet list of people into a CSV sorted by last name.", ref="read; write csv.", why="Last-name sort.", ref_calls=2)


def c05():
    f = {"账本/9月.csv": "日期,类别,金额\n2026-09-01,餐饮,36.5\n2026-09-02,交通,12\n2026-09-03,餐饮,48.5\n2026-09-05,购物,199\n2026-09-07,交通,8\n2026-09-09,餐饮,25\n"}

    def compute(files):
        t = {}
        for l in files["账本/9月.csv"].strip().split("\n")[1:]:
            d, c, a = l.split(",")
            t[c] = t.get(c, 0) + float(a)
        def fmt(x):
            return ("%.2f" % x)
        out = "类别,合计\n" + "".join("%s,%s\n" % (k, fmt(t[k])) for k in sorted(t)) + "总计,%s\n" % fmt(sum(t.values()))
        return {"账本/9月汇总.csv": out}
    mk("tab-31105", sub="summary", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-NUMFMT",),
       turns=[("根据 账本/9月.csv 做一份按类别的合计，写到 账本/9月汇总.csv。表头“类别,合计”，类别按拼音/字典序排好，金额统一保留两位小数，最后加一行“总计”。", None)],
       gist="Category totals with two decimals and a total row.", ref="read; write.", why="Deterministic.", ref_calls=2)


def c06():
    f = {"监控/请求.jsonl": '{"path":"/a","ms":120,"code":200}\n{"path":"/b","ms":340,"code":500}\n{"path":"/a","ms":80,"code":200}\n{"path":"/c","ms":50,"code":404}\n{"path":"/b","ms":410,"code":200}\n{"path":"/a","ms":100,"code":200}\n'}

    def compute(files):
        import json
        d = {}
        for l in files["监控/请求.jsonl"].strip().split("\n"):
            r = json.loads(l)
            d.setdefault(r["path"], []).append(r["ms"])
        return {"监控/耗时.json": json.dumps({k: {"count": len(v), "avg_ms": sum(v) // len(v)} for k, v in sorted(d.items())}, indent=2) + "\n"}
    mk("log-31106", sub="summary", scen_type=("logs", "aggregate_jsonl"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("Read 监控/请求.jsonl and write 监控/耗时.json: a JSON object keyed by path (sorted), each value {\"count\": n, \"avg_ms\": average as an integer (they all divide evenly)}. Indent with 2 spaces and end the file with a newline.", None)],
       gist="Aggregate JSONL requests per path into a JSON file.", ref="read; write_file json.", why="avg computed.", ref_calls=2, loose=())


def c07():
    f = {"项目/任务.md": "# 任务\n\n- [x] 写需求文档 @李雷\n- [ ] 评审原型 @韩梅梅\n- [ ] 接口联调 @李雷\n- [x] 压测 @王芳\n- [ ] 上线检查 @韩梅梅\n"}

    def compute(files):
        d = {}
        for l in files["项目/任务.md"].split("\n"):
            if l.startswith("- [ ] "):
                t, who = l[6:].rsplit(" @", 1)
                d.setdefault(who, []).append(t)
        out = ""
        for who in sorted(d):
            out += "%s\n" % who + "".join("- %s\n" % t for t in d[who])
        return {"项目/待办清单.txt": out}
    mk("doc-31107", sub="summary", scen_type=("docs", "extract_items"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("从 项目/任务.md 里把还没完成的任务按负责人整理成 项目/待办清单.txt：先一行负责人名字，下面每个任务一行，以“- ”开头；负责人按名字排序，任务保持原顺序，已完成的不要。", None)],
       gist="List unfinished tasks grouped by owner.", ref="read; write.", why="Unchecked only.", ref_calls=2)


def c08():
    f = {"库存/入库.csv": "sku,qty\nA1,10\nB2,5\nA1,7\nC3,2\nB2,8\n", "库存/出库.csv": "sku,qty\nA1,4\nB2,13\nC3,2\nA1,3\n"}

    def compute(files):
        s = {}
        for fn, sg in (("库存/入库.csv", 1), ("库存/出库.csv", -1)):
            for l in files[fn].strip().split("\n")[1:]:
                k, q = l.split(",")
                s[k] = s.get(k, 0) + sg * int(q)
        return {"库存/结存.csv": "sku,结存\n" + "".join("%s,%d\n" % (k, s[k]) for k in sorted(s))}
    mk("tab-31108", sub="summary", scen_type=("tabular", "reconcile"), files=f, compute=compute, traps=("TR-MULTISRC",),
       turns=[("用 库存/入库.csv 减去 库存/出库.csv，算出每个 sku 的结存数量，写成 库存/结存.csv（表头 sku,结存，sku 按字母序）。", None)],
       gist="Compute stock balance per sku from two files.", ref="read both; write.", why="in-out.", ref_calls=3)


def c09():
    f = {"notes/books.txt": "The Pragmatic Programmer | 1999 | Hunt\nClean Code | 2008 | Martin\nSICP | 1985 | Abelson\nRefactoring | 1999 | Fowler\nDesign Patterns | 1994 | Gamma\n"}

    def compute(files):
        rows = [[x.strip() for x in l.split("|")] for l in files["notes/books.txt"].strip().split("\n")]
        rows.sort(key=lambda r: (int(r[1]), r[0]))
        return {"notes/books.md": "| Title | Year | Author |\n|---|---|---|\n" + "".join("| %s | %s | %s |\n" % tuple(r) for r in rows)}
    mk("doc-31109", sub="summary", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("Make notes/books.md out of notes/books.txt: a Markdown table with columns Title, Year, Author, oldest book first (same year: alphabetical by title).", None)],
       gist="Books list to Markdown table sorted by year.", ref="read; write.", why="sorted.", ref_calls=2)


def c10():
    f = {"设备/温度.csv": "时间,机房,温度\n08:00,A,22.5\n08:00,B,25.1\n09:00,A,23.0\n09:00,B,27.4\n10:00,A,24.5\n10:00,B,26.0\n"}

    def compute(files):
        d = {}
        for l in files["设备/温度.csv"].strip().split("\n")[1:]:
            _, r, t = l.split(",")
            d.setdefault(r, []).append(float(t))
        out = "机房,最高,最低,平均\n"
        for r in sorted(d):
            v = d[r]
            out += "%s,%.1f,%.1f,%.1f\n" % (r, max(v), min(v), sum(v) / len(v))
        return {"设备/机房统计.csv": out}
    mk("tab-31110", sub="summary", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("统计一下 设备/温度.csv 里每个机房的最高、最低、平均温度，写到 设备/机房统计.csv，表头“机房,最高,最低,平均”，都保留一位小数。", None)],
       gist="Per-room max/min/avg temperature to CSV.", ref="read; write.", why="avg 1 decimal.", ref_calls=2)


BUILDERS = [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10]
