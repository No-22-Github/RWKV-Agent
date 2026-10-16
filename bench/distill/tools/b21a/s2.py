"""b21a sub 2 (append, do not overwrite), cases 31021-31032."""
from common import L, make, RW, RA, RB, RLW

B = []


def reg(f):
    B.append(f)
    return f


def app(cid, files, path, new, turns, policy, desc, traps_note, ops_extra=None, task_type="write_structured", ref="append_file", lines=None):
    ops = [[("app", path, new)]]
    if ops_extra:
        ops = ops_extra
    newlines = [l for o in ops for op in o if op[0] == "app" for l in op[2].split("\n") if l.strip()]
    make(cid, sub="append", task_type=task_type, desc=desc, files=files, turns=turns, ops=ops, policy=policy, loose={path: lines or newlines},
         notes_ref={"traps": [traps_note], "steps": ["read_file %s to see the current end" % path, ref, "read back the tail"],
                    "unique": "The original text must remain verbatim and the new lines must be present (contains)."}, ref_calls=3)


@reg
def a1():
    f = {"CHANGELOG.md": L("# Changelog", "", "## 1.3.0 - 2026-08-02", "- 新增批量导出", "- 修复登录页闪烁", "", "## 1.2.4 - 2026-07-11", "- 修复时区偏移", "- 升级依赖 axios", "")}
    new = "\n## 1.3.1 - 2026-09-16\n- 修复导出文件名乱码\n"
    app("doc-31021", f, "CHANGELOG.md", new, [("把 1.3.1 这个版本记到 CHANGELOG.md 最后：日期 2026-09-16，内容只有一条“修复导出文件名乱码”。格式照前面的版本来。弄完告诉我现在文件一共有几个版本条目。", ["3"], None)],
        None, "Adds a release entry to the end of a changelog", "TR-DECOY: overwriting the file with only the new entry loses 1.3.0 and 1.2.4.")


@reg
def a2():
    f = {"todo.txt": L("[ ] 订机票", "[x] 续签证", "[ ] 买电池", "[x] 退租车", "[ ] 预约体检")}
    app("fs-31022", f, "todo.txt", "[ ] 给老张回电话\n", [("Add \"给老张回电话\" to the end of todo.txt as an unchecked item, same format as the others. Don't touch the existing items. How many unchecked items are there now?", ["4"], None)],
        RA, "Appends one unchecked todo item to a list", "TR-DECOY: write_file with just the new item destroys five existing items.", task_type="bulk_edit")


@reg
def a3():
    f = {"logs/ops-journal.log": L("2026-09-14 09:12 deploy api 1.8.0 ok", "2026-09-14 15:40 rollback worker 2.1.3 (queue stuck)", "2026-09-15 10:05 deploy worker 2.1.4 ok", "2026-09-15 22:30 db failover test ok")}
    new = "2026-09-16 09:50 deploy api 1.8.1 ok\n"
    app("fs-31023", f, "logs/ops-journal.log", new, [("运维日志 logs/ops-journal.log 补一条：2026-09-16 09:50 deploy api 1.8.1 ok，写在最后面，前面的记录原样留着。完成后告诉我日志现在最后两条是什么。", ["1.8.1", "failover"], None),
        ("再补一条：2026-09-16 10:20 rollback api 1.8.1 (latency spike)，同样写在最后。补完告诉我日志总共几条。", ["6"], None)],
        RLW, "Adds a dated entry to the end of an ops journal", "TR-DECOY: journal entries must not be rewritten.", task_type="bulk_edit", ref="append via append_file or bash >>",
        ops_extra=[[("app", "logs/ops-journal.log", new)], [("app", "logs/ops-journal.log", "2026-09-16 10:20 rollback api 1.8.1 (latency spike)\n")]], lines=[new.strip(), "2026-09-16 10:20 rollback api 1.8.1 (latency spike)"])


@reg
def a4():
    f = {"members.csv": L("id,name,team,joined", "101,Ada Chen,infra,2024-03-01", "102,Ben Ortiz,data,2024-05-17", "103,Chloe Park,infra,2025-01-09")}
    new = "104,Dev Rao,data,2026-09-01\n"
    app("tab-31024", f, "members.csv", new, [("Add a new member to members.csv: id 104, Dev Rao, team data, joined 2026-09-01. Keep the same column order and keep the current rows. Then tell me how many member rows the file has.", ["4"], None)],
        None, "Appends one csv row", "TR-DECOY: header and existing rows must stay; a rewrite with only the new row loses them.", task_type="write_summary")


@reg
def a5():
    f = {"docs/decisions.md": L("# 决策记录", "", "## D-001 使用 PostgreSQL", "原因：团队熟悉，事务支持完整。", "", "## D-002 日志统一 JSON", "原因：便于检索。", "")}
    new = "\n## D-003 接口默认分页 50 条\n原因：避免一次返回过多数据。\n"
    app("doc-31025", f, "docs/decisions.md", new, [("决策记录 docs/decisions.md 里加一条 D-003：标题“接口默认分页 50 条”，原因写“避免一次返回过多数据”，格式照前两条。加完告诉我现在有几条决策。", ["3"], None)],
        RW, "Adds a numbered decision to the end of a decisions doc", "TR-DECOY: D-001 and D-002 must stay.")


@reg
def a6():
    f = {"requirements.txt": L("flask==3.0.2", "gunicorn==21.2.0", "redis==5.0.1")}
    app("cfg-31026", f, "requirements.txt", "sentry-sdk==1.40.0\n", [("requirements.txt 里加上 sentry-sdk==1.40.0，其他依赖保持不变。加完告诉我现在一共几个依赖。", ["4"], None)],
        RB, "Appends one dependency line", "TR-DECOY: whole-file rewrite risk with only three lines.", task_type="edit_value")


@reg
def a7():
    f = {"meeting/2026-09-weekly.md": L("# 9 月周会纪要", "", "## 09-02", "- 确认预算", "- 小李负责排期", "", "## 09-09", "- 评审了新方案", "- 下周开始联调", "")}
    new = "\n## 09-16\n- 联调完成 70%\n- 小王负责压测\n"
    app("doc-31027", f, "meeting/2026-09-weekly.md", new, [("今天的周会纪要要加到 meeting/2026-09-weekly.md 末尾，小标题用“## 09-16”，两条：联调完成 70%、小王负责压测。前面两周的别动。加完后告诉我文件里现在有几周的纪要。", ["3"], None),
        ("还要补一条到刚加的 09-16 里：“下周三评审排期”。补完后只回复这一周现在有哪几条。", ["下周三评审排期", "压测"], None)],
        None, "Appends a section then adds a bullet to it", "TR-DECOY: second turn must add under the new section at the end; older weeks stay.",
        ops_extra=[[("app", "meeting/2026-09-weekly.md", new)], [("app", "meeting/2026-09-weekly.md", "- 下周三评审排期\n")]])


@reg
def a8():
    f = {".gitignore": L("node_modules/", "dist/", "*.log", ".env")}
    app("fs-31028", f, ".gitignore", ".cache/\ncoverage/\n", [("Please make git skip the .cache/ and coverage/ folders too. The current entries must stay. Tell me the full list of entries afterwards.", [".env", "coverage/"], None)],
        RW, "Appends two ignore rules to a short gitignore", "TR-DECOY: writing only the two new lines would drop four rules.", task_type="bulk_edit")


@reg
def a9():
    f = {"data/visitors.csv": L("date,visitors,source", "2026-09-10,1204,organic", "2026-09-11,1311,organic", "2026-09-12,980,ads", "2026-09-13,1022,ads", "2026-09-14,1450,organic")}
    new = "2026-09-15,1388,ads\n2026-09-16,1502,organic\n"
    app("tab-31029", f, "data/visitors.csv", new, [("data/visitors.csv 追加两天的数据：2026-09-15 1388 ads，2026-09-16 1502 organic。列顺序和前面一致，旧数据保留。追加完成后，告诉我 organic 来源现在一共有几行。", ["3"], None),
        ("发现 09-15 的访问量记错了，应该是 1398。帮我改掉，其他不变。改完回复新的那一行。", ["1398"], None)],
        RB, "Appends two csv rows then corrects one of them", "TR-DECOY: turn 2 edits the appended row, other rows must remain.", task_type="write_summary",
        ops_extra=[[("app", "data/visitors.csv", new)], [("sub", "data/visitors.csv", "2026-09-15,1388,ads\n", "2026-09-15,1398,ads\n")]],
        lines=["2026-09-15,1398,ads", "2026-09-16,1502,organic"])


@reg
def a10():
    f = {"notes/ideas.txt": L("1. 做一个离线模式", "2. 支持夜间主题", "3. 导出 PDF")}
    app("doc-31030", f, "notes/ideas.txt", "4. 接入日历提醒\n", [("在 notes/ideas.txt 的想法清单后面接着写第 4 条“接入日历提醒”，编号接着前面排。前三条留着。写好告诉我清单现在有几条。", ["4"], None)],
        None, "Appends the fourth numbered item", "TR-DECOY: numbering must continue at 4.")


@reg
def a11():
    f = {"release/notes-2026.txt": L("== 2026-07 ==", "ship: search v2", "fix: cart rounding", "", "== 2026-08 ==", "ship: dark mode", "fix: login redirect", "")}
    new = "\n== 2026-09 ==\nship: export center\nfix: timezone drift\n"
    app("doc-31031", f, "release/notes-2026.txt", new, [("release/notes-2026.txt 末尾新开一段 2026-09，写两条：ship: export center、fix: timezone drift，段头格式和 7、8 月一样。之前的月份不动。告诉我现在文件有几个月份段。", ["3"], None)],
        RA, "Adds a new month block to a release-notes file", "TR-DECOY: a rewrite that keeps only September loses two months.")


@reg
def a12():
    f = {"data/errors.jsonl": L('{"ts":"2026-09-15T08:00:00","code":500,"path":"/api/pay"}', '{"ts":"2026-09-15T09:30:00","code":404,"path":"/api/ship"}')}
    new = '{"ts":"2026-09-16T08:30:00","code":502,"path":"/api/pay"}\n'
    app("tab-31032", f, "data/errors.jsonl", new, [("data/errors.jsonl 追加一行记录，每行一个 JSON：ts 是 2026-09-16T08:30:00，code 502，path /api/pay。字段顺序同前面。追加后告诉我文件现在有几行记录。", ["3"], None)],
        None, "Appends one JSON line to a jsonl file", "TR-DECOY: JSON lines must stay one per line, existing lines kept.", task_type="write_summary")
