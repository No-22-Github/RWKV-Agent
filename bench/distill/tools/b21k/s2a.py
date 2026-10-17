"""write_structured / extract_items 33220-33229."""
from common import mk, WEBOFF
from s1a import T


def c20():
    f = {"会议/0911纪要.md": "# 周会纪要 9月11日\n\n【结论】接口改版推迟一周。\n【待办】张凯：整理合同（9月20日前）\n【已办】周敏：发出邀请函\n【待办】刘洋：更新报价单（9月18日前）\n【待办】张凯：预约会议室（9月17日前）\n【已办】刘洋：归档旧文档\n【备注】下次例会改在周四。\n"}

    def compute(files):
        out = ""
        for l in files["会议/0911纪要.md"].split("\n"):
            if l.startswith("【待办】"):
                who, rest = l[4:].split("：", 1)
                what, due = rest.rstrip("）").split("（")
                out += "- [ ] %s｜%s｜%s\n" % (what, who, due.replace("前", ""))
        return {"会议/待办清单.md": out}
    mk("doc-33220", sub="extract", ttype="extract_items", files=f, compute=compute,
       rules={"会议/待办清单.md": compute(f)["会议/待办清单.md"]}, traps=("TR-DECOY",),
       turns=[T("把 会议/0911纪要.md 里还没办的待办抽出来，写到 会议/待办清单.md。每条一行，格式“- [ ] 事项｜负责人｜日期”（竖线是全角｜），日期去掉“前”字，按原顺序，已办的不要。")],
       gist="Extract open to-dos from minutes into a checklist file.", steps="read; write.", why="3 open items; done items excluded.")


def c21():
    f = {"CHANGELOG.md": "# Changelog\n\n## 4.2.0\n- Add dark theme\n- BREAKING: drop Node 14 support\n- Fix typo in docs\n\n## 4.1.3\n- Fix memory leak in worker\n\n## 4.1.0\n- BREAKING: rename `--out` flag to `--output`\n- Add retry option\n\n## 4.0.0\n- BREAKING: config moves from `.apprc` to `app.toml`\n- Faster startup\n"}

    def compute(files):
        ver, rows = "", []
        for l in files["CHANGELOG.md"].split("\n"):
            if l.startswith("## "):
                ver = l[3:]
            elif "BREAKING:" in l:
                rows.append("| %s | %s |" % (ver, l.split("BREAKING:")[1].strip()))
        return {"breaking.md": "| Version | Change |\n|---|---|\n" + "\n".join(rows) + "\n"}
    mk("doc-33221", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"breaking.md": compute(f)["breaking.md"]},
       traps=("TR-HEADER",), never=WEBOFF,
       turns=[T("List only the breaking changes from CHANGELOG.md in a new file breaking.md as a markdown table with header `| Version | Change |`, a `|---|---|` separator, then one row per change in file order. Drop the BREAKING: prefix from the change text.")],
       gist="Breaking changes of a changelog as a table.", steps="read; write.", why="3 breaking entries.")


def c22():
    f = {"通讯录/内部.txt": "研发部\n  秦岚 13900010001\n  邹凯 13900010002\n市场部\n  叶青 13900010003\n行政部\n  金莉 13900010004\n  段林 13900010005\n"}

    def compute(files):
        dept, rows = "", []
        for l in files["通讯录/内部.txt"].split("\n"):
            if l and not l.startswith(" "):
                dept = l
            elif l:
                n, p = l.split()
                if dept != "市场部":
                    rows.append("%s,%s,%s" % (n, p, dept))
        return {"通讯录/联系人.csv": "姓名,电话,部门\n" + "\n".join(rows) + "\n"}
    mk("doc-33222", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"通讯录/联系人.csv": compute(f)["通讯录/联系人.csv"]},
       traps=("TR-HEADER",), ref_calls=5,
       turns=[T("把 通讯录/内部.txt 整理成 CSV 写到 通讯录/联系人.csv，表头“姓名,电话,部门”，每人一行，部门是他所在小节的标题。"),
              T("我只要研发部和行政部的，市场部的人去掉，文件还是这个。")],
       gist="Contacts csv then filter departments.", steps="read; write; rewrite.", why="Final csv has 4 rows.")
    return


def c23():
    f = {"价格/报价.txt": "办公用品报价单\n签字笔 一盒12支 38元\n A4纸 一箱5包 160元\n 文件夹 单个 4元\n碎纸机 一台 520元\n订书机 单个 36元\n 激光打印机 一台 1850元\n"}

    def compute(files):
        rows = []
        for l in files["价格/报价.txt"].split("\n")[1:]:
            l = l.strip()
            if not l:
                continue
            p = int(l.rsplit(" ", 1)[1].rstrip("元"))
            if p > 100:
                rows.append("- %s：%d元" % (l.split()[0], p))
        return {"价格/贵重物品.md": "\n".join(rows) + "\n"}
    mk("doc-33223", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"价格/贵重物品.md": compute(f)["价格/贵重物品.md"]},
       traps=("TR-DEFN",),
       turns=[T("从 价格/报价.txt 里挑出价格超过 100 元的品目，写到 价格/贵重物品.md，每行“- 品名：价格元”（比如“- 碎纸机：520元”），顺序同原文。")],
       gist="Items over 100 yuan as a bullet file.", steps="read; write.", why="A4纸 160, 碎纸机 520, 激光打印机 1850.")


def c24():
    f = {"notes/standup.md": "# Standup 09-15\n\n- Dana: finished the billing API review; blocked on staging access (ask Omar) -- due 09-18\n- Omar: will grant staging access today\n- Lee: to write migration script -- due 09-22\n- Dana: to update runbook -- due 09-25\n- Lee: lunch with vendor (not work)\n"}

    def compute(files):
        rows = []
        for l in files["notes/standup.md"].split("\n"):
            if " -- due " in l:
                a = l[2:]
                who = a.split(":")[0]
                task = a.split(":")[1].split(" -- due ")[0].strip()
                rows.append((who, task, a.split(" -- due ")[1]))
        rows.sort(key=lambda r: r[2])
        return {"notes/actions.md": "| Owner | Task | Due |\n|---|---|---|\n" + "".join("| %s | %s | %s |\n" % r for r in rows)}
    exp = compute(f)["notes/actions.md"]
    mk("doc-33224", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"notes/actions.md": exp},
       traps=("TR-DECOY",), never=WEBOFF, ref_calls=5,
       turns=[T("Pull the action items (the lines with a due date) from notes/standup.md into notes/actions.md as a markdown table: header `| Owner | Task | Due |`, separator `|---|---|---|`, one row per item in the file's order."),
              T("Sort the rows by due date instead, earliest first. Keep the same table format.")],
       gist="Action table from standup notes then sort by date.", steps="read; write; rewrite.", why="Final rows sorted by due date.")


def c25():
    f = {"帮助/常见问题.md": "# 常见问题\n\n## 怎么修改绑定手机号？\n进入“设置-账号安全”，验证旧手机后即可更换。\n\n## 忘记密码怎么办？\n在登录页点“找回密码”，按提示验证。\n\n## 可以同时登录几台设备？\n最多 3 台。\n\n## 发票多久能开出？\n提交申请后 3 个工作日内。\n"}

    def compute(files):
        qs = [l[3:] for l in files["帮助/常见问题.md"].split("\n") if l.startswith("## ")]
        return {"帮助/问题目录.md": "".join("%d. %s\n" % (i + 1, q) for i, q in enumerate(qs))}
    mk("doc-33225", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"帮助/问题目录.md": compute(f)["帮助/问题目录.md"]},
       traps=("TR-HEADER",), ref_calls=3,
       turns=[T("把 帮助/常见问题.md 里所有的问题抽出来，编号列在新文件 帮助/问题目录.md 里，每行“1. 问题原文”，不要答案。")],
       gist="Numbered list of FAQ questions.", steps="read; write.", why="4 questions.")


def c26():
    f = {"论文/参考文献.txt": "[1] 刘强. 深度学习综述. 计算机学报, 2018.\n[2] 王芳. 大模型推理加速研究. 软件学报, 2023.\n[3] 陈静. 图神经网络进展. 自动化学报, 2020.\n[4] 赵磊. 分布式训练系统. 电子学报, 2016.\n[5] 孙悦. 检索增强生成综述. 计算机研究与发展, 2024.\n"}

    def compute(files):
        out = ""
        for l in files["论文/参考文献.txt"].strip().split("\n"):
            parts = l.split(". ")
            year = int(parts[-1].rstrip(".").split(", ")[-1])
            if year >= 2020:
                out += "%s,%d\n" % (parts[1], year)
        return {"论文/近五年.csv": "题目,年份\n" + out}
    mk("doc-33226", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"论文/近五年.csv": compute(f)["论文/近五年.csv"]},
       traps=("TR-DEFN",),
       turns=[T("把 论文/参考文献.txt 里 2020 年及以后的文献整理成 论文/近五年.csv，表头“题目,年份”，只要题目和年份，顺序同原文。")],
       gist="Recent references to csv.", steps="read; write.", why="2020, 2023, 2024 entries.")


def c27():
    f = {"采购/供应商条款.md": "# 供应商付款条款\n\n- 恒达电子：到货后 30 天内付清，逾期每日万分之五。\n- 晨光文具：月结，次月 15 日前付款。\n- 凯瑞包装：预付 50%，余款到货后 7 天内付清。\n- 蓝海物流：每季度结算一次，季末后 20 天内付款。\n"}

    rules = {"采购/付款期限.csv": ["供应商,期限", "恒达电子,", "30天", "晨光文具,", "次月15日前", "凯瑞包装,", "7天", "蓝海物流,", "20天", "远景科技,", "15天"]}
    mk("doc-33227", sub="extract", ttype="write_structured", files=f, facts=["供应商,期限", "恒达电子,", "30天", "晨光文具,", "次月15日前", "凯瑞包装,", "7天", "蓝海物流,", "20天", "远景科技,", "15天"],
       free=["供应商,期限", "恒达电子,", "晨光文具,", "次月15日前", "凯瑞包装,", "7天", "蓝海物流,", "20天", "远景科技,", "30天"],
       rules=rules, traps=("TR-DEFN",), ref_calls=5,
       turns=[T("从 采购/供应商条款.md 整理一个付款期限的 CSV，写到 采购/付款期限.csv，表头“供应商,期限”，期限用“到货后30天内”这种短写法（月结的写原文里的日期）。"),
              T("再加一行：新供应商 远景科技，期限写“到货后15天内”。")],
       gist="Payment terms csv then an added supplier row.", steps="read; write; append.", why="Short forms preset; added supplier row.")


def c28():
    f = {"README.md": "# Gateway\n\n## Configuration\n\nThe service reads these environment variables:\n\n- `GW_PORT` (default `8080`): listen port.\n- `GW_LOG_LEVEL` (default `info`): one of debug, info, warn.\n- `GW_TIMEOUT_MS` (default `3000`): upstream timeout.\n- `GW_TLS` (default `off`): enable TLS.\n\n## Notes\n\nSet `GW_DEBUG=1` only in development; it has no default and is not supported in production.\n"}

    def compute(files):
        rows = []
        for l in files["README.md"].split("\n"):
            if l.startswith("- `GW_"):
                name = l.split("`")[1]
                default = l.split("`")[3]
                rows.append("| %s | %s |" % (name, default))
        return {"env-vars.md": "| Name | Default |\n|---|---|\n" + "\n".join(rows) + "\n"}
    mk("doc-33228", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"env-vars.md": compute(f)["env-vars.md"]},
       traps=("TR-DECOY",), never=WEBOFF,
       turns=[T("Make env-vars.md with a markdown table of the environment variables that have a default, taken from README.md. Use the header `| Name | Default |` and the separator `|---|---|`, one row per variable in README order, name and default without backticks.")],
       gist="Env var table; undefaulted variable excluded.", steps="read; write.", why="Four variables with defaults.")


def c29():
    f = {"日程/本周.txt": "周一 09:00 晨会（A厅）\n周二 14:00 供应商来访（会客室）\n周三 10:00 预算评审（B座201）\n周三 15:30 新人面试（面试间2）\n周四 09:30 安全培训（大礼堂）\n周三 17:00 周中小结（A厅）\n周五 16:00 周五复盘（A厅）\n"}

    def compute(files):
        rows = [l.split(" ", 1)[1] for l in files["日程/本周.txt"].split("\n") if l.startswith("周三")]
        rows.sort()
        return {"日程/周三.md": "".join("- %s\n" % r for r in rows)}
    mk("doc-33229", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"日程/周三.md": compute(f)["日程/周三.md"]},
       traps=("TR-DECOY",), ref_calls=3,
       turns=[T("把周三的安排挑出来，按时间先后每行一条写到 日程/周三.md，格式“- 10:00 预算评审（B座201）”（去掉“周三”两个字），来源是 日程/本周.txt。")],
       gist="Wednesday agenda in time order (items not contiguous in the source).", steps="read; sort; write.", why="Three Wednesday items.")


BUILDERS = [c20, c21, c22, c23, c24, c25, c26, c27, c28, c29]
