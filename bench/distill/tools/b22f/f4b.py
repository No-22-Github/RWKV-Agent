"""F4 long multi-turn sessions, cases 34571-34575: two long pages read in different turns, then a 12-month comparison."""
from common import T
from f2 import P, make_pages
from f4 import F4, money


def two_site(cid, lang, A, B, p1, p2, p3, p4, out, months=12, topics=None, tokens=3700):
    """A/B: dict(name, url, q, title, intro, date, monthly, setup, decoys=[(heading, text)], lead=[(heading, text)], plan_word)."""
    zh = lang == "zh"
    pages = []
    for s in (A, B):
        mf = ("%s月费 %d 元。" % (s["plan_word"], s["monthly"])) if zh else "The %s costs %d dollars per month." % (s["plan_word"], s["monthly"])
        sf = ("一次性开通费 %d 元。" % s["setup"]) if zh else "The one-off setup fee is %d dollars." % s["setup"]
        secs = [(h, [t]) for h, t in s["lead"]] + [("月费" if zh else "Monthly fees", [mf])] + [(h, [t]) for h, t in s["decoys"]] + [("开通与合同" if zh else "Setup and contract", [sf])]
        pages.append(P(lang, s["url"], s["q"], s["title"], topics, s["intro"], secs, tokens, s["date"], [mf.split("。")[0][-12:] if False else str(s["monthly"]), str(s["setup"])]))
    web = make_pages(cid, pages)
    ta, tb = months * A["monthly"] + A["setup"], months * B["monthly"] + B["setup"]
    better = A["name"] if ta < tb else B["name"]
    turns = [T(p1, inc=[str(A["monthly"])], req=["web_fetch"]),
             T(p2, inc=[str(B["monthly"])], req=["web_fetch"]),
             T(p3, inc=[str(x) for x in (A["setup"], B["setup"]) if x < 1000], any=sum([money(x) for x in (A["setup"], B["setup"]) if x >= 1000], []), anytok=True),
             T(p4, inc=[better], any=money(ta) + money(tb), anytok=True)]
    return F4(cid, lang, {}, web, turns, rules={out: [str(A["monthly"]), str(B["monthly"]), A["name"], B["name"]]},
              why="The last turn needs both monthly fees from turns 1 and 2 plus the setup fees: totals %d and %d, so %s is cheaper." % (ta, tb, better),
              steps_text="turn1 web_fetch A（长页面）并跳到月费章节；turn2 同样处理 B；turn3 回到两个存档读开通费（search_text .web）；turn4 算 12 个月总价并 write_file",
              must=("web_fetch", "read_file", "write_file", "search_text"), edits=1, calcs=1)


def build():
    two_site("hyb-34571", "zh",
             dict(name="云砚托管", url="https://yunyan-hosting.example/plans/colocation", q="云砚托管", title="云砚托管机柜托管套餐", intro="云砚托管 · 价目更新于 2026-10-06", date="2026-10-06",
                  monthly=380, setup=1500, plan_word="标准 1U 托管套餐", lead=[("机房介绍", "云砚的机房位于郊区的数据园区，配有双路市电和柴油发电机。")],
                  decoys=[("增值服务", "远程重启服务每次 20 元，带宽升级到 100M 每月加收 120 元。")]),
             dict(name="澜海数据", url="https://lanhai-idc.example/price/rack-1u", q="澜海数据", title="澜海数据 IDC 机架价格", intro="澜海数据 · 2026 年价格表", date="2026-09-29",
                  monthly=450, setup=600, plan_word="1U 托管套餐", lead=[("公司简介", "澜海数据成立于十年前，在三个城市运营机房，客户以中小企业为主。")],
                  decoys=[("附加项", "额外 IP 每个每月 15 元，上门上架服务每次 100 元。")]),
             "我们想把一台服务器托管出去，先看云砚托管的页面 https://yunyan-hosting.example/plans/colocation ，标准 1U 托管套餐每月多少钱？",
             "再看澜海数据 https://lanhai-idc.example/price/rack-1u ，他们的 1U 托管套餐每月多少钱？",
             "两家的一次性开通费分别是多少？",
             "按用满 12 个月算，把两家的总费用算出来，选便宜的那家，对比写到 托管方案对比.md。", "托管方案对比.md",
             topics=["机柜", "带宽", "电力", "运维", "合同", "机房"])
    two_site("hyb-34572", "en",
             dict(name="BrightNest", url="https://brightnest-clean.example/pricing", q="BrightNest", title="BrightNest office cleaning pricing", intro="BrightNest Cleaning · prices effective 2026-10-03", date="2026-10-03",
                  monthly=420, setup=250, plan_word="weekly office cleaning plan", lead=[("Our approach", "BrightNest teams use fragrance-free products and carry out a checklist-based clean on every visit.")],
                  decoys=[("Extras", "Window cleaning is 60 dollars per visit and carpet shampooing 90 dollars per room.")]),
             dict(name="Marigold Services", url="https://marigold-services.example/office/rates", q="Marigold", title="Marigold Services office rates", intro="Marigold Services · rate card 2026", date="2026-08-22",
                  monthly=395, setup=480, plan_word="weekly office cleaning plan", lead=[("About Marigold", "Marigold Services is a family-run company that has cleaned offices in the region for years.")],
                  decoys=[("Optional services", "Deep cleaning is 150 dollars per session and waste removal 35 dollars per week.")]),
             "Let's price office cleaning. On BrightNest's page https://brightnest-clean.example/pricing , how much is the weekly office cleaning plan per month?",
             "And on Marigold's rate card https://marigold-services.example/office/rates , what is their weekly office cleaning plan per month?",
             "What does each of them charge as a one-off setup fee?",
             "Assume 12 months. Work out the total for both, pick the cheaper one and write the comparison to cleaning-quotes.md.", "cleaning-quotes.md",
             topics=["cleaning", "supplies", "schedules", "insurance", "contracts", "staff"])
    two_site("hyb-34573", "zh",
             dict(name="拾码", url="https://shima-dev.example/pricing/team", q="拾码", title="拾码代码托管团队版价格", intro="拾码 · 价格页 · 2026-10-14 更新", date="2026-10-14",
                  monthly=290, setup=800, plan_word="团队版（20 人）", lead=[("产品简介", "拾码提供代码托管、流水线和制品库，数据存放在国内机房。")],
                  decoys=[("流水线", "额外流水线并发数每增加 5 个，每月加收 60 元。")]),
             dict(name="枫桥", url="https://fengqiao-code.example/plans", q="枫桥", title="枫桥代码平台套餐", intro="枫桥代码平台 · 2026 年套餐", date="2026-07-30",
                  monthly=340, setup=300, plan_word="团队版（20 人）", lead=[("平台概览", "枫桥以代码审查和安全扫描见长，提供本地部署选项。")],
                  decoys=[("安全扫描", "高级安全扫描模块每月 150 元，按仓库数量不限。")]),
             "团队想选代码托管。先看拾码 https://shima-dev.example/pricing/team ，团队版（20 人）每月多少钱？",
             "枫桥的套餐在 https://fengqiao-code.example/plans ，同样是团队版（20 人），每月多少钱？",
             "两家各有一次性开通费吗？分别是多少？",
             "按一年 12 个月算，两家总共各多少钱，选更省的那家，写进 代码平台选型.md。", "代码平台选型.md",
             topics=["代码托管", "流水线", "权限", "制品库", "审计", "迁移"])
    two_site("hyb-34574", "zh",
             dict(name="仓联", url="https://cangtong-wh.example/rent/east-zone", q="仓联", title="仓联仓储东区租赁价目", intro="仓联仓储 · 东区租赁价目 · 2026-10-08", date="2026-10-08",
                  monthly=620, setup=900, plan_word="100 平方米标准库位", lead=[("园区位置", "东区靠近物流环线，货车可全天通行，库区配备月台和叉车。")],
                  decoys=[("增值服务", "分拣打包每单 2 元，库内盘点每次 300 元。")]),
             dict(name="盛运", url="https://shengyun-store.example/space/pricing", q="盛运", title="盛运仓配库位价格", intro="盛运仓配 · 价格说明 · 2026-09-17", date="2026-09-17",
                  monthly=580, setup=1300, plan_word="100 平方米标准库位", lead=[("服务简介", "盛运提供仓储加配送一体化服务，库区实行恒温管理。")],
                  decoys=[("配送", "同城配送每单 8 元起，大件另计。")]),
             "我们想租一个仓库，先看仓联东区的价目 https://cangtong-wh.example/rent/east-zone ，100 平方米标准库位每月租金是多少？",
             "盛运的价目在 https://shengyun-store.example/space/pricing ，同样规格每月多少钱？",
             "两家的一次性开通费（押金之外的）分别是多少？",
             "按租满 12 个月算，两家总共各要多少钱？选更划算的，写到 仓储租赁对比.md。", "仓储租赁对比.md",
             topics=["库位", "月台", "消防", "装卸", "盘点", "出入库"])
    two_site("hyb-34575", "en",
             dict(name="Noteflow", url="https://noteflow-app.example/plans/team", q="Noteflow", title="Noteflow team plan pricing", intro="Noteflow · team plan pricing · 2026-10-10", date="2026-10-10",
                  monthly=145, setup=200, plan_word="Team plan for 15 members", lead=[("What you get", "Noteflow combines shared notes, tasks and a lightweight wiki in a single workspace.")],
                  decoys=[("Add-ons", "Guest seats are 4 dollars each per month and priority support is 60 dollars per month.")]),
             dict(name="Pagewright", url="https://pagewright.example/pricing/teams", q="Pagewright", title="Pagewright team pricing", intro="Pagewright · pricing for teams · 2026-09-05", date="2026-09-05",
                  monthly=130, setup=420, plan_word="Team plan for 15 members", lead=[("About Pagewright", "Pagewright is a documentation tool with strong version history and an offline mode.")],
                  decoys=[("Optional extras", "Single sign-on is 40 dollars per month and the audit pack is 55 dollars per month.")]),
             "We are choosing a notes tool for the team. On https://noteflow-app.example/plans/team , how much is the Team plan for 15 members per month?",
             "Now https://pagewright.example/pricing/teams : what does their Team plan for 15 members cost per month?",
             "Do they charge one-off setup fees? What are the amounts?",
             "Over 12 months, what do the two cost in total? Pick the cheaper one and write the comparison to notes-tool-choice.md.", "notes-tool-choice.md",
             topics=["notes", "workspace", "permissions", "templates", "search", "exports"])
