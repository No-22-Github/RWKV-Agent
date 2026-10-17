"""write_structured / extract_items 33230-33238."""
from common import mk, WEBOFF
from s1a import T


def c30():
    f = {"客服/反馈汇总.txt": "O-1021 [咨询] 想问发货时间\nO-1034 [投诉] 包裹破损，要求补发\nO-1040 [表扬] 客服回复很快\nO-1052 [投诉] 同一订单重复扣款\nO-1066 [咨询] 能否开发票\nO-1071 [投诉] 配送延迟五天\n"}

    def compute(files):
        rows = []
        for l in files["客服/反馈汇总.txt"].strip().split("\n"):
            if "[投诉]" in l:
                rows.append("%s,%s" % (l.split(" ")[0], l.split("] ", 1)[1]))
        return {"客服/投诉.csv": "订单号,问题\n" + "".join(r + "\n" for r in rows)}
    mk("doc-33230", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"客服/投诉.csv": compute(f)["客服/投诉.csv"]},
       traps=("TR-DECOY",), ref_calls=3,
       turns=[T("把 客服/反馈汇总.txt 里标成投诉的挑出来，写 客服/投诉.csv，表头“订单号,问题”，问题写方括号后面的原话。")],
       gist="Complaints only to csv.", steps="read; write.", why="3 complaints.")


def c31():
    f = {"hr/policy-dates.md": "# Key dates\n\n- 2026-08-31: Q3 expense claims closed\n- 2026-09-30: Open enrolment ends\n- 2026-10-15: Annual review forms due\n- 2026-09-20: Fire drill (all sites)\n- 2026-12-01: Holiday rota published\n"}

    def compute(files):
        rows = []
        for l in files["hr/policy-dates.md"].split("\n"):
            if l.startswith("- 20"):
                d, t = l[2:].split(": ", 1)
                rows.append((d, t))
        rows = sorted(r for r in rows if r[0] >= "2026-09-16" and "Fire drill" not in r[1])
        return {"hr/upcoming.txt": "".join("%s %s\n" % r for r in rows)}
    mk("doc-33231", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"hr/upcoming.txt": compute(f)["hr/upcoming.txt"]},
       traps=("TR-DEFN",), never=WEBOFF, ref_calls=5,
       turns=[T("From hr/policy-dates.md, list the dates that are still ahead of us (today is 2026-09-16, and today itself counts as still ahead) in hr/upcoming.txt, earliest first, one per line as `2026-10-15 Annual review forms due`."),
              T("Also drop the fire drill line, it's handled elsewhere.")],
       gist="Upcoming dates sorted, then drop one line.", steps="read; filter; write; rewrite.", why="Four dates minus the drill: 3 lines.")


def c32():
    f = {"员工/生日.txt": "吴敏 3月8日\n郑强 10月3日\n蒋丽 10月21日\n冯远 5月30日\n韩雪 10月12日\n楚天 11月2日\n"}

    def compute(files):
        rows = []
        for l in files["员工/生日.txt"].strip().split("\n"):
            n, d = l.split(" ")
            m, day = d.split("月")
            if m == "10":
                rows.append((int(day.rstrip("日")), n, d))
        rows.sort()
        return {"员工/十月寿星.md": "".join("- %s：%s\n" % (n, d) for _, n, d in rows)}
    mk("doc-33232", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"员工/十月寿星.md": compute(f)["员工/十月寿星.md"]},
       traps=("TR-DECOY",), ref_calls=3,
       turns=[T("从 员工/生日.txt 找出 10 月过生日的人，按日期先后写到 员工/十月寿星.md，每行“- 姓名：10月3日”。")],
       gist="October birthdays sorted by day (11月 and 1x are decoys).", steps="read; sort; write.", why="3 people.")


def c33():
    f = {"设备/清单.csv": "设备,编号,保修到期\n笔记本,NB-017,2026-11-30\n投影仪,PJ-003,2027-03-15\n打印机,PR-009,2026-10-05\n服务器,SV-001,2026-12-31\n路由器,RT-022,2027-01-20\n"}

    def compute(files):
        rows = [l.split(",") for l in files["设备/清单.csv"].strip().split("\n")[1:]]
        rows = [r for r in rows if r[2] <= "2026-12-31"]
        rows.sort(key=lambda r: r[2])
        return {"设备/即将到期.csv": "设备,编号,保修到期,状态\n" + "".join("%s,%s,%s,待续保\n" % tuple(r) for r in rows)}
    mk("doc-33233", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"设备/即将到期.csv": compute(f)["设备/即将到期.csv"]},
       traps=("TR-DEFN",), ref_calls=5,
       turns=[T("从 设备/清单.csv 找出保修在 2026 年底（含 12月31日当天）前到期的设备，按到期日从早到晚写到 设备/即将到期.csv，列保持原样。"),
              T("再加一列“状态”，每行都填“待续保”。")],
       gist="Warranty expiring by year end sorted, then add a status column.", steps="read; write; rewrite.", why="Include boundary 2026-12-31.")


def c34():
    f = {"RELEASES.md": "## 3.1.2\n- fix: crash on empty config (#201)\n- fix: wrong exit code (#205)\n- chore: bump deps\n\n## 3.1.1\n- fix: locale bug (#188)\n\n## 3.0.9\n- fix: legacy path handling (#150)\n\n## 3.1.0\n- feat: plugin API\n- fix: race in scheduler (#193)\n- fix: memory spike (#195)\n"}

    def compute(files):
        ver, nums = "", []
        for l in files["RELEASES.md"].split("\n"):
            if l.startswith("## "):
                ver = l[3:]
            elif l.startswith("- fix:") and ver.startswith("3.1."):
                nums.append(l.split("(#")[1].rstrip(")"))
        return {"fixed-3.1.txt": "".join(n + "\n" for n in sorted(nums, key=int))}
    mk("doc-33234", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"fixed-3.1.txt": compute(f)["fixed-3.1.txt"]},
       traps=("TR-DECOY",), never=WEBOFF, ref_calls=3,
       turns=[T("Collect the issue numbers fixed in the 3.1.x releases (3.1.0, 3.1.1, 3.1.2 only) from RELEASES.md and write them to fixed-3.1.txt: one number per line without the #, ascending.")],
       gist="Issue numbers fixed in 3.1.x only.", steps="read; sort; write.", why="188,193,195,201,205.")


def c35():
    f = {"合同/服务合同.txt": "第二条 服务费用：本合同总价为人民币 48000 元。\n第五条 付款方式：首付款 30%，验收后付 60%，质保金 10% 在一年后支付。\n第七条 违约责任：逾期交付按每日 0.1% 支付违约金。\n第九条 保证金：乙方应缴纳履约保证金 5000 元。\n第十一条 备注：本合同一式两份。\n"}

    def compute(files):
        return {"合同/金额条款.csv": "条款,内容\n第二条,总价48000元\n第五条,首付款30%，验收后60%，质保金10%\n第九条,履约保证金5000元\n"}
    mk("doc-33235", sub="extract", ttype="write_structured", files=f, facts=["条款,内容", "第二条", "48000", "第五条", "30%", "60%", "10%", "第九条", "5000"],
       rules={"合同/金额条款.csv": ["条款,内容", "第二条", "48000", "第五条", "30%", "60%", "10%", "第九条", "5000"]},
       traps=("TR-DEFN",), ref_calls=3,
       turns=[T("把 合同/服务合同.txt 里跟钱有关的条款（总价、付款比例、保证金）抽成 合同/金额条款.csv，表头“条款,内容”，违约金那条不用放。")],
       gist="Money clauses to csv.", steps="read; write.", why="Three clauses.")


def c36():
    f = {"值班/排班.txt": "9月21日 邱桐\n9月22日 沈岚\n9月23日 邱桐\n9月24日 魏东\n9月25日 沈岚\n9月26日 邱桐\n"}

    def compute(files):
        d = {}
        for l in files["值班/排班.txt"].strip().split("\n"):
            day, n = l.split(" ")
            d.setdefault(n, []).append(day)
        names = sorted(d, key=lambda n: (-len(d[n]), n))
        return {"值班/按人.md": "".join("%s（%d次）：%s\n" % (n, len(d[n]), "、".join(d[n])) for n in names)}
    mk("doc-33236", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"值班/按人.md": compute(f)["值班/按人.md"]},
       traps=("TR-HEADER",), ref_calls=5,
       turns=[T("把 值班/排班.txt 按人整理到 值班/按人.md，每人一行，格式“邱桐：9月21日、9月23日”，人按名字在排班里首次出现的顺序。"),
              T("改成“邱桐（3次）：9月21日、9月23日、9月26日”这样带上次数，并且按次数多的在前，次数一样的按名字首次出现的顺序。")],
       gist="Duty roster grouped by person then with counts and re-sorted.", steps="read; write; rewrite.",
       why="邱桐 3, 沈岚 2, 魏东 1.")


def c37():
    f = {"refs/links.txt": "Intro to Rust - https://doc.example.org/rust-intro\nSlides (internal) - http://intranet.local/slides/rust\nBorrow checker notes - https://blog.example.net/borrow\nOld wiki page - http://wiki.example.org/old-rust\nCargo guide - https://doc.example.org/cargo\n"}

    def compute(files):
        rows = [l for l in files["refs/links.txt"].strip().split("\n") if " - https://" in l]
        return {"refs/https-only.md": "".join("- [%s](%s)\n" % tuple(l.split(" - ")) for l in rows)}
    mk("doc-33237", sub="extract", ttype="extract_items", files=f, compute=compute, rules={"refs/https-only.md": compute(f)["refs/https-only.md"]},
       traps=("TR-DEFN",), never=WEBOFF, ref_calls=3,
       turns=[T("From refs/links.txt keep only the secure links (https) and write them to refs/https-only.md as markdown bullets like `- [Intro to Rust](https://doc.example.org/rust-intro)`, same order as the source.")],
       gist="HTTPS-only link list as markdown bullets.", steps="read; write.", why="3 https lines.")


def c38():
    f = {"食谱/周计划.md": "# 本周两道菜\n\n## 番茄炒蛋\n- 鸡蛋 4个\n- 番茄 300g\n- 盐 3g\n\n## 蛋炒饭\n- 鸡蛋 2个\n- 米饭 400g\n- 盐 2g\n- 葱 20g\n"}

    def compute(files):
        d, order = {}, []
        for l in files["食谱/周计划.md"].split("\n"):
            if l.startswith("- "):
                n, q = l[2:].split(" ")
                num = int("".join(c for c in q if c.isdigit()))
                unit = "".join(c for c in q if not c.isdigit())
                if n not in d:
                    order.append(n)
                    d[n] = [0, unit]
                d[n][0] += num
        return {"食谱/购物清单.md": "".join("- %s %d%s\n" % (n, d[n][0], d[n][1]) for n in order)}
    mk("doc-33238", sub="extract", ttype="write_structured", files=f, compute=compute, rules={"食谱/购物清单.md": compute(f)["食谱/购物清单.md"]},
       traps=("TR-DUPROW",), ref_calls=3,
       turns=[T("把 食谱/周计划.md 里两道菜的食材合并成一份购物清单写到 食谱/购物清单.md，同一种食材加在一起，每行“- 鸡蛋 6个”这种写法，顺序按第一次出现。")],
       gist="Merge duplicate ingredients across recipes.", steps="read; sum; write.", why="鸡蛋 6个 番茄 300g 盐 5g 米饭 400g 葱 20g.")


BUILDERS = [c30, c31, c32, c33, c34, c35, c36, c37, c38]
