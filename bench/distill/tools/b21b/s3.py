"""Sub 3: multi-turn feedback edits (first turn writes, later turns revise)."""
from common import mk


def c33():
    f = {"员工/名单.csv": "姓名,部门,工资\n林强,研发,18000\n何敏,市场,12000\n郭亮,研发,21000\n宋佳,财务,15000\n"}

    def compute(files):
        rows = [l.split(",") for l in files["员工/名单.csv"].strip().split("\n")[1:]]
        rows.sort(key=lambda r: -int(r[2]))
        return {"员工/公示.csv": "姓名,部门\n" + "".join("%s,%s\n" % (r[0], r[1]) for r in rows)}
    mk("tab-31133", sub="revise", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 员工/名单.csv 整理成 员工/公示.csv，列保持原样，按工资从高到低排。", None),
              ("不对，工资不能公开，把工资那一列去掉，其它不变，顺序还是按原来的工资高低。", None)],
       gist="Write a roster file then drop the salary column keeping salary order.", ref="read; write; rewrite.", why="final 2 cols.", ref_calls=4)


def c34():
    f = {"销量/月度.csv": "月份,产品,件数\n7月,甲,120\n7月,乙,80\n8月,甲,150\n8月,乙,60\n9月,甲,90\n9月,乙,110\n"}

    def compute(files):
        d = {}
        for l in files["销量/月度.csv"].strip().split("\n")[1:]:
            m, p, n = l.split(",")
            d[p] = d.get(p, 0) + int(n)
        return {"销量/产品合计.csv": "产品,Total\n" + "".join("%s,%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}
    mk("tab-31134", sub="revise", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("汇总 销量/月度.csv 里每个产品三个月的总件数，写到 销量/产品合计.csv，表头“产品,合计”，按产品名排。", None),
              ("改一下：表头换成英文“产品,Total”不要变，只把“合计”改成 Total；然后行改成按总件数从多到少排，一样多的按产品名。", None)],
       gist="Product totals then rename header and re-sort.", ref="write; rewrite.", why="甲360 乙250.", ref_calls=4)


def c35():
    f = {"日报/原始.txt": "09-14 修复支付超时\n09-14 评审接口文档\n09-15 上线灰度\n09-15 处理客诉\n09-16 复盘\n"}

    def compute(files):
        ls = [l.split(" ", 1) for l in files["日报/原始.txt"].strip().split("\n")]
        keep = [l for l in ls if l[0] != "09-14"]
        return {"日报/汇报.md": "# 汇报\n\n" + "".join("- %s：%s\n" % (a, b) for a, b in keep)}
    mk("doc-31135", sub="revise", scen_type=("docs", "draft_document"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("把 日报/原始.txt 整理成 日报/汇报.md：第一行“# 汇报”，空一行，每条写成“- 09-14：修复支付超时”这样，顺序不变。", None),
              ("领导说 14 号的内容已经汇报过了，把 14 号的条目都拿掉，其余保持。", None)],
       gist="Report file then remove one day's entries.", ref="write; rewrite.", why="3 bullets.", ref_calls=4)


def c36():
    f = {"设置/默认.ini": "theme=light\nlang=zh\nfont=14\nautosave=on\n"}

    def compute(files):
        return {"设置/我的.ini": "theme=dark\nlang=zh\nfont=18\nautosave=on\nproxy=off\n"}
    mk("cfg-31136", sub="revise", scen_type=("config", "edit_value"), files=f, compute=compute, traps=("TR-READONLY",),
       turns=[("以 设置/默认.ini 为底，复制一份到 设置/我的.ini，把主题改成 dark，字号改成 16。默认那份别动。", None),
              ("再加一行 proxy=off 放在最后，字号还是太小，改成 18 吧。", None)],
       gist="Copy ini then adjust twice.", ref="write; rewrite.", why="font 18 wait", ref_calls=4)


def c37():
    f = {"采购/需求.csv": "品名,数量,单价\n签字笔,50,2\n笔记本,30,8\n文件夹,20,5\n订书机,5,25\n"}

    def compute(files):
        out = "品名,数量,单价,小计\n"
        tot = 0
        for l in files["采购/需求.csv"].strip().split("\n")[1:]:
            n, q, p = l.split(",")
            out += "%s,%s,%s,%d\n" % (n, q, p, int(q) * int(p))
            tot += int(q) * int(p)
        return {"采购/清单.csv": out + "合计,,,%d\n" % tot}
    mk("tab-31137", sub="revise", scen_type=("tabular", "policy_calc"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("基于 采购/需求.csv 生成 采购/清单.csv，在后面加一列“小计”（数量×单价），表头“品名,数量,单价,小计”。", None),
              ("再在最后加一行合计：品名写“合计”，数量和单价留空，小计是所有小计之和。", None)],
       gist="Add subtotal column then total row.", ref="write; rewrite.", why="100+240+100+125=565.", ref_calls=4)


def c38():
    f = {"访客/记录.log": "2026-09-14 张三 来访\n2026-09-14 李四 来访\n2026-09-15 张三 来访\n2026-09-16 王五 来访\n"}

    def compute(files):
        d = {}
        for l in files["访客/记录.log"].strip().split("\n"):
            _, n, _ = l.split()
            d[n] = d.get(n, 0) + 1
        return {"访客/统计.txt": "".join("%s=%d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}
    mk("log-31138", sub="revise", scen_type=("logs", "count_events"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("统计 访客/记录.log 里每个人来访几次，写到 访客/统计.txt，每行“姓名: 次数”，按姓名排。", None),
              ("格式我想换一下：冒号改成等号，两边不要空格，写成“张三=2”，顺序改成次数多的在前，一样多按姓名。", None)],
       gist="Visitor counts then format change.", ref="write; rewrite.", why="张三=2.", ref_calls=4)


def c39():
    f = {"成员/组.md": "# 小组\n\n- 周杰 / 前端\n- 吴迪 / 后端\n- 郑爽 / 测试\n- 孙宁 / 前端\n"}

    def compute(files):
        rows = [l[2:].split(" / ") for l in files["成员/组.md"].split("\n") if l.startswith("- ")]
        out = "| Name | Role |\n|---|---|\n" + "".join("| %s | %s |\n" % tuple(r) for r in rows if r[1] != "前端")
        return {"成员/表.md": out}
    mk("doc-31139", sub="revise", scen_type=("docs", "write_structured"), files=f, compute=compute,
       turns=[("Turn the list in 成员/组.md into a Markdown table in 成员/表.md, header | Name | Role |, one row per person in the original order.", None),
              ("Actually the front-end people are handled elsewhere. Remove them from the table. Keep the original list file as it was.", None)],
       gist="Table of members then remove one role.", ref="write; rewrite.", why="3? 2 rows", ref_calls=4)


def c40():
    f = {"路线/站点.txt": "起点 0\n超市 2.5\n学校 4\n医院 7.5\n终点 10\n"}

    def compute(files):
        ls = [l.split() for l in files["路线/站点.txt"].strip().split("\n")]
        out = "站点,距离(公里),距上一站\n"
        prev = 0.0
        for n, d in ls:
            out += "%s,%s,%.1f\n" % (n, d, float(d) - prev)
            prev = float(d)
        return {"路线/分段.csv": out}
    mk("tab-31140", sub="revise", scen_type=("tabular", "policy_calc"), files=f, compute=compute, traps=("TR-NUMFMT",),
       turns=[("把 路线/站点.txt 做成 路线/分段.csv，表头“站点,距离(公里)”，距离照原样写。", None),
              ("加上第三列“距上一站”，起点是 0，其余是和上一站的差，都保留一位小数（距离那列仍照原样）。", None)],
       gist="Stops csv then add delta column.", ref="write; rewrite.", why="0.0 2.5 1.5 3.5 2.5 2.5", ref_calls=4)


def c41():
    f = {"食谱/原料.txt": "面粉 500g\n鸡蛋 3个\n牛奶 250ml\n白糖 80g\n黄油 50g\n"}

    def compute(files):
        ls = [l for l in files["食谱/原料.txt"].strip().split("\n") if not l.startswith("白糖")]
        return {"食谱/购物单.md": "# 购物单\n\n" + "".join("- [ ] %s\n" % l for l in sorted(ls))}
    mk("doc-31141", sub="revise", scen_type=("docs", "draft_document"), files=f, compute=compute, traps=("TR-DECOY",),
       turns=[("用 食谱/原料.txt 列个购物单 食谱/购物单.md：标题“# 购物单”，空一行，每样一行“- [ ] 面粉 500g”，保持原来的顺序。", None),
              ("家里白糖有，划掉不用买（直接删掉那行）。另外按名字的拼音顺序重排太麻烦了，就按文字的 Unicode 字典序排吧。", None)],
       gist="Shopping list then remove an item and sort.", ref="write; rewrite.", why="sorted codepoints.", ref_calls=4)


def c42():
    f = {"账号/users.csv": "id,name,role\n1,ann,admin\n2,bob,user\n3,cat,user\n4,dan,guest\n"}

    def compute(files):
        rows = [l.split(",") for l in files["账号/users.csv"].strip().split("\n")[1:]]
        rows = [r for r in rows if r[2] != "guest"]
        return {"账号/active.csv": "id,name,role\n" + "".join("%s,%s,%s\n" % (r[0], r[1].upper(), r[2]) for r in rows)}
    mk("tab-31142", sub="revise", scen_type=("tabular", "filter_count"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("Copy 账号/users.csv to 账号/active.csv but leave out the guest accounts.", None),
              ("Also make the name column uppercase in that new file.", None)],
       gist="Filter then uppercase names.", ref="write; rewrite.", why="3 rows.", ref_calls=4)


def c43():
    f = {"版本/发布.md": "v2.3 2026-08-01 修复内存泄漏\nv2.4 2026-08-20 新增导出\nv2.5 2026-09-10 性能优化\n"}

    def compute(files):
        import json
        out = []
        for l in files["版本/发布.md"].strip().split("\n"):
            v, d, t = l.split(" ", 2)
            out.append({"version": v, "date": d, "note": t})
        out = out[::-1]
        return {"版本/发布.json": json.dumps(out, ensure_ascii=False, indent=2) + "\n"}
    mk("doc-31143", sub="revise", scen_type=("docs", "write_structured"), files=f, compute=compute, traps=("TR-DATEFMT",),
       turns=[("把 版本/发布.md 转成 版本/发布.json，一个数组，对象键是 version、date、note，缩进 2 个空格、末尾换行，顺序照原文。", None),
              ("新的放前面比较好，把数组倒过来，别的都不变。", None)],
       gist="Release notes to json then reverse order.", ref="write; rewrite.", why="reverse.", ref_calls=4)


def c44():
    f = {"问卷/回答.csv": "编号,满意度,建议\n1,5,很好\n2,3,太慢\n3,4,\n4,2,界面乱\n5,5,\n"}

    def compute(files):
        rows = [l.split(",") for l in files["问卷/回答.csv"].strip().split("\n")[1:]]
        low = [r for r in rows if int(r[1]) <= 3]
        return {"问卷/跟进.csv": "编号,满意度,建议\n" + "".join(",".join(r) + "\n" for r in sorted(low, key=lambda r: (int(r[1]), int(r[0]))))}
    mk("tab-31144", sub="revise", scen_type=("tabular", "filter_count"), files=f, compute=compute, traps=("TR-MISSING",),
       turns=[("从 问卷/回答.csv 里挑出满意度低于 4 的回答，写到 问卷/跟进.csv，列不变，按编号排。", None),
              ("再调整成满意度最低的排最前面，满意度一样的按编号。我之前说的“低于 4”是对的，范围别变。", None)],
       gist="Low satisfaction filter then re-sort.", ref="write; rewrite.", why="4,2 then 2,3.", ref_calls=4)


def c45():
    f = {"部署/版本.env": "APP=shop\nVER=1.8.2\nENV=staging\nREPLICAS=2\n"}

    def compute(files):
        return {"部署/发布单.txt": "应用: shop\n版本: 1.8.2\n环境: production\n副本: 4\n"}
    mk("cfg-31145", sub="revise", scen_type=("config", "edit_value"), files=f, compute=compute, traps=("TR-READONLY",),
       turns=[("读 部署/版本.env，写一份 部署/发布单.txt，四行：应用、版本、环境、副本，格式“应用: shop”（冒号后一个空格），值照抄。", None),
              ("这是要上生产的，把环境改成 production，副本数改成 4。env 文件本身不要改。", None)],
       gist="Release sheet then change env and replicas.", ref="write; rewrite.", why="explicit.", ref_calls=4)


def c46():
    f = {"赛事/比分.csv": "主队,客队,主,客\n红,蓝,2,1\n绿,红,0,0\n蓝,绿,3,2\n红,黄,1,2\n黄,蓝,1,1\n"}

    def compute(files):
        pts = {}
        for l in files["赛事/比分.csv"].strip().split("\n")[1:]:
            h, a, hs, as_ = l.split(",")
            hs, as_ = int(hs), int(as_)
            for t in (h, a):
                pts.setdefault(t, [0, 0])
            if hs > as_:
                pts[h][0] += 3
            elif hs < as_:
                pts[a][0] += 3
            else:
                pts[h][0] += 1
                pts[a][0] += 1
            pts[h][1] += hs - as_
            pts[a][1] += as_ - hs
        order = sorted(pts, key=lambda t: (-pts[t][0], -pts[t][1], t))
        return {"赛事/积分榜.csv": "排名,球队,积分,净胜球\n" + "".join("%d,%s,%d,%d\n" % (i + 1, t, pts[t][0], pts[t][1]) for i, t in enumerate(order))}
    mk("tab-31146", sub="revise", scen_type=("tabular", "rank"), files=f, compute=compute, traps=("TR-SIGN", "TR-DEFN"), ref_calls=4,
       turns=[("按 赛事/比分.csv 算积分榜写到 赛事/积分榜.csv：胜 3 分、平 1 分、负 0 分，列是“排名,球队,积分”，积分高的在前，同分按球队名。", None),
              ("再加一列“净胜球”放最后（进球减失球，可以是负数，写成 -1 这样），排序规则改成积分相同先看净胜球多的，再看球队名。", None)],
       gist="League table then add goal difference.", ref="write; rewrite.", why="computed.")


def c47():
    f = {"故障/事件.log": "03:10 DB 连接超时 持续12分钟\n05:42 缓存 命中率下降 持续5分钟\n09:15 DB 慢查询 持续20分钟\n13:00 网关 502 持续3分钟\n"}

    def compute(files):
        ls = [l.split(" ", 3) for l in files["故障/事件.log"].strip().split("\n")]
        db = [l for l in ls if l[1] == "DB"]
        mins = sum(int(l[3][2:-2]) for l in db)
        return {"故障/复盘.md": "# 故障复盘\n\n## DB 相关\n" + "".join("- %s %s\n" % (l[0], l[2]) for l in db) + "\n共 %d 分钟\n" % mins}
    mk("log-31147", sub="revise", scen_type=("logs", "time_window"), files=f, compute=compute, traps=("TR-DECOY", "TR-DEFN"), ref_calls=4,
       turns=[("看 故障/事件.log，把所有 DB 相关的事件写进 故障/复盘.md：标题“# 故障复盘”，空一行，“## DB 相关”，然后每条一行“- 时间 描述”。", None),
              ("末尾空一行再补一句“共 N 分钟”，N 是这些 DB 事件持续时间加起来的分钟数。", None)],
       gist="Postmortem for DB events then add total minutes.", ref="write; rewrite.", why="32.")


def c48():
    f = {"备忘/清单.txt": "牙膏\n纸巾\n洗衣液\n电池\n"}

    def compute(files):
        return {"备忘/清单.md": "# 采购\n\n- 牙膏\n- 纸巾\n- 洗衣液\n- 电池\n- 垃圾袋\n"}
    mk("doc-31148", sub="revise", scen_type=("docs", "draft_document"), files=f, compute=compute, ref_calls=3,
       turns=[("把 备忘/清单.txt 改成 Markdown 版放在 备忘/清单.md：开头“# 采购”，空一行，每样一条“- ”列表。", None),
              ("再加一项垃圾袋，放最后。", None),
              ("好，就这样，谢谢。", {"tools": [], "require_active_no_call": True, "output_contains_any": ["不客气", "好的", "没问题", "随时", "welcome", "Welcome", "glad", "Glad", "OK", "ok", "Sure", "sure"]})],
       gist="Checklist to md, add one item, then thank-you turn needs no tool.", ref="write; rewrite; reply.", why="explicit.")


def c49():
    f = {"客户/档案.csv": "id,公司,城市\n1,星河,上海\n2,云帆,深圳\n3,启明,上海\n4,海岳,杭州\n"}

    def compute(files):
        rows = [l.split(",") for l in files["客户/档案.csv"].strip().split("\n")[1:]]
        sh = [r for r in rows if r[2] == "上海"]
        return {"客户/上海.csv": "id,公司\n" + "".join("%s,%s\n" % (r[0], r[1]) for r in sh), "客户/其他.csv": "id,公司,城市\n" + "".join(",".join(r) + "\n" for r in rows if r[2] != "上海")}
    mk("tab-31149", sub="revise", scen_type=("tabular", "filter_count"), files=f, compute=compute, traps=("TR-HEADER",),
       turns=[("把 客户/档案.csv 里上海的客户挑出来写到 客户/上海.csv，列保持不变。", None),
              ("上海那份不需要城市列了（都是上海），去掉；另外把非上海的客户写到 客户/其他.csv，三列都保留。", None)],
       gist="Split customers by city after a revision.", ref="write; rewrite; write.", why="two files.", ref_calls=5)


def c50():
    f = {"值班/排班.csv": "周,值班人\n1,阿明\n2,小红\n3,阿明\n4,大伟\n"}

    def compute(files):
        rows = [l.split(",") for l in files["值班/排班.csv"].strip().split("\n")[1:]]
        d = {}
        for w, n in rows:
            d[n] = d.get(n, 0) + 1
        return {"值班/次数.txt": "".join("%s %d\n" % (k, d[k]) for k in sorted(d, key=lambda k: (-d[k], k)))}
    mk("tab-31150", sub="revise", scen_type=("tabular", "write_summary"), files=f, compute=compute, traps=("TR-DUPROW",),
       turns=[("看看 值班/排班.csv，每个人排了几周，写到 值班/次数.txt，一人一行“姓名 次数”。顺序随意。", None),
              ("我想要次数多的排前面，同样多的按姓名排，请改一下文件。", None)],
       gist="Duty counts then sort.", ref="write; rewrite.", why="阿明 2.", ref_calls=4)


BUILDERS = [c33, c34, c35, c36, c37, c38, c39, c40, c41, c42, c43, c44, c45, c46, c47, c48, c49, c50]
