"""b23d D2 part b: 4-turn chains, ids 35248-35260."""
from common import mk, T, L

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c48():
    log, out = "logs/billing-cron-1021.log", "logs/billing-1021-summary.txt"
    files = {log: L("02:00 job=invoice-gen dur=38s", "02:05 job=reconcile dur=95s", "02:20 job=export dur=52s")}
    mk("hyb-35248", sub="D2", tt="write", trap="TR-CLAIM", desc="Summary file that is rewritten after a rerun and extended, ending with a time-saved figure", files=files,
       turns=[T("Which job took the longest in logs/billing-cron-1021.log, and how long?", inc=["reconcile", "95"]),
              T("Write one line 'Slowest: <job> (<seconds>s)' to logs/billing-1021-summary.txt."),
              T("The reconcile job was rerun and finished in 41s. Who is the slowest now? Update the summary line accordingly.", inc=["export"]),
              T("Add a second line 'Rerun: reconcile 41s' to the summary, and tell me how many seconds faster reconcile got compared with its first run.", inc=["54"])],
       adds=[(out, L("Slowest: export (52s)", "Rerun: reconcile 41s"))], exact=[out], vals=["54"], must=["read_file", "write_file", "append_file", "replace_lines", "calculator"], rc=7, dep="95-41=54 needs turn-1 duration")


@reg
def c49():
    f = "文档/任务板.md"
    files = {f: L("## 待办", "- 写接口文档", "- 压测", "## 进行中", "- 登录改版", "## 完成", "- 搭建CI")}
    old = L("- 写接口文档", "- 压测", "## 进行中", "- 登录改版", "## 完成", "- 搭建CI")
    new = L("- 写接口文档", "## 进行中", "- 压测", "## 完成", "- 搭建CI", "- 登录改版")
    mk("hyb-35249", sub="D2", tt="multi", trap="TR-CLAIM", desc="Move kanban items between sections over several turns, then recap sections and the original backlog size", files=files,
       turns=[T("任务板里“进行中”现在有什么？文件是 文档/任务板.md。", inc=["登录改版"]),
              T("把“压测”从待办移到进行中。"),
              T("“登录改版”做完了，移到完成里。"),
              T("现在三栏各有什么？另外最开始待办里有几项？", inc=["写接口文档", "压测", "登录改版", "搭建CI", "2"])],
       edits=[(f, old, new)], must=["read_file", "replace_lines", "write_file"], rc=6, dep="initial backlog 2 items from the fixture")


@reg
def c50():
    a, b, c = "config/svc-orders.toml", "config/svc-billing.toml", "config/svc-search.toml"
    files = {a: L("[cache]", 'cache_url = "redis-old-1.corp.local:6379"'), b: L("[cache]", 'cache_url = "redis-old-2.corp.local:6380"'), c: L("[cache]", 'cache_url = "redis-new.corp.local:6379"')}
    mk("hyb-35250", sub="D2", tt="comp", trap="TR-MULTISRC", desc="Find configs on an old host, migrate them, check the one already migrated, recap old hosts", files=files,
       turns=[T("Which files in config/ point cache_url at a host starting with redis-old?", inc=["svc-orders", "svc-billing"]),
              T("Point those at redis-new.corp.local and keep each file's port as it is."),
              T("What does svc-search point at? Does it need changing?", inc=["redis-new.corp.local"]),
              T("Recap which files changed and the old host of each.", inc=["svc-orders", "svc-billing", "redis-old-1", "redis-old-2"])],
       edits=[(a, "redis-old-1.corp.local:6379", "redis-new.corp.local:6379"), (b, "redis-old-2.corp.local:6380", "redis-new.corp.local:6380")],
       must=["search_text", "read_file", "replace_lines", "write_file"], rc=8)


@reg
def c51():
    a, b, out = "文档/报价-恒通.txt", "文档/报价-明辉.txt", "文档/采购单.txt"
    files = {a: L("供应商：恒通", "A4纸 每箱 168"), b: L("供应商：明辉", "A4纸 每箱 159")}
    mk("hyb-35251", sub="D2", tt="write", trap="TR-MULTISRC", desc="Pick the cheaper quote into an order file, switch supplier after a price drop, compute savings", files=files,
       turns=[T("两家的 A4 纸报价各是多少？文件在 文档 目录。", inc=["168", "159"]),
              T("选便宜的那家，写到 文档/采购单.txt，就一行，格式“供应商：单价”。"),
              T("恒通说可以降到每箱 150，那就改选恒通，更新采购单。", inc=["恒通"]),
              T("这次要买 20 箱，总价多少？比一开始选的那家省了多少钱？", any=["3000", "3,000"], inc=["180"])],
       adds=[(out, "恒通：150\n")], exact=[out], vals=["180"], must=["read_file", "write_file", "replace_lines", "calculator"], rc=6, dep="saving vs the first pick (明辉 159): 20*(159-150)=180")


@reg
def c52():
    f = "docs/onboarding/day-one.md"
    files = {f: L("- 09:00 Welcome", "- 10:00 Laptop setup", "- 13:00 Security training")}
    mk("hyb-35252", sub="D2", tt="undo", trap="TR-CLAIM", desc="Move two items, accept, then undo only the first and ask for the original time", files=files,
       turns=[T("When is laptop setup in docs/onboarding/day-one.md?", inc=["10:00"]),
              T("Move it to 10:30."),
              T("I accepted that edit. Also push security training to 14:00, then read the file back and confirm both lines.", inc=["10:30", "14:00"], review="accept"),
              T("My manager wants the laptop move undone, but the training stays at 14:00. Do that, then give me the final schedule and say what the laptop time was originally.", inc=["10:00", "14:00", "09:00"])],
       edits=[(f, "- 13:00 Security training", "- 14:00 Security training")], must=["read_file", "replace_lines", "write_file"], rc=7)


@reg
def c53():
    e, w, s, out = "数据/门店-东.txt", "数据/门店-西.txt", "数据/门店-南.txt", "数据/销量汇总.txt"
    files = {e: "销量：120\n", w: "销量：95\n", s: "销量：143\n"}
    mk("hyb-35253", sub="D2", tt="write", trap="TR-MULTISRC", desc="Aggregate three store files into a summary, correct one store, compare totals", files=files,
       turns=[T("东、西、南三家店的销量各是多少？", inc=["120", "95", "143"]),
              T("汇总写入 数据/销量汇总.txt，每店一行，格式“东店：120”，最后一行“合计：总数”。"),
              T("西店的数据录错了，实际是 105，更新汇总文件。", inc=["105"]),
              T("现在合计多少？比原来多了多少？西店原来录的是多少？", inc=["368", "95"])],
       adds=[(out, L("东店：120", "西店：105", "南店：143", "合计：368"))], exact=[out], vals=["368"], must=["read_file", "write_file", "replace_lines", "calculator"], rc=7)


@reg
def c54():
    src, tst, faq = "src/payments/limits.py", "tests/test_limits.py", "docs/limits-faq.md"
    files = {src: L("MAX_AMOUNT = 5000", "MIN_AMOUNT = 1"), tst: L("from payments.limits import MAX_AMOUNT", "", "def test_cap():", "    assert MAX_AMOUNT == 5000"),
             faq: L("# Limits FAQ", "The cap is 5000 per transaction.")}
    mk("hyb-35254", sub="D2", tt="comp", trap="TR-MULTISRC", desc="Change a constant and its test, then search for leftover mentions that the user did not ask to change", files=files,
       turns=[T("Where is the 5000 limit defined and where is it tested?", inc=["limits.py", "test_limits.py"]),
              T("Raise the limit to 7500 in the source."),
              T("Update the test to match."),
              T("Search the repo for any other place still mentioning 5000, and tell me the old and new limit.", inc=["limits-faq", "5000", "7500"])],
       edits=[(src, "MAX_AMOUNT = 5000", "MAX_AMOUNT = 7500"), (tst, "assert MAX_AMOUNT == 5000", "assert MAX_AMOUNT == 7500")],
       must=["search_text", "read_file", "replace_lines", "write_file"], rc=7)


@reg
def c55():
    f = "文档/项目里程碑.txt"
    files = {f: L("需求冻结：2026-11-02", "开发完成：2026-11-20", "上线：2026-12-01")}
    mk("hyb-35255", sub="D2", tt="comp", trap="TR-CLAIM", desc="Shift two milestones by 7 days, compute the gap, recall the original launch date", files=files,
       turns=[T("项目上线日期是哪天？文件是 文档/项目里程碑.txt。", inc=["2026-12-01"]),
              T("上线推迟 7 天，改一下，告诉我新日期。", inc=["2026-12-08"]),
              T("开发完成也推迟 7 天。", inc=["2026-11-27"]),
              T("现在从开发完成到上线隔几天？另外上线最初定在哪天？", any=["11 天", "11天", "十一天", "11 days"], inc=["2026-12-01"])],
       edits=[(f, "开发完成：2026-11-20", "开发完成：2026-11-27"), (f, "上线：2026-12-01", "上线：2026-12-08")], vals=["2026-12-08", "2026-11-27"],
       must=["read_file", "replace_lines", "write_file", "datetime", "calculator"], rc=6)


@reg
def c56():
    f = "settings/editor-prefs.json"
    files = {f: '{\n  "tabSize": 4,\n  "wordWrap": "on",\n  "theme": "solarized"\n}\n'}
    mk("hyb-35256", sub="D2", tt="multi", trap="TR-CLAIM", desc="Two JSON edits over two turns and a recap of before and after", files=files,
       turns=[T("What are tabSize and wordWrap in settings/editor-prefs.json?", inc=["4", "on"]),
              T("Set tabSize to 2.", inc=["2"]),
              T("Turn wordWrap off.", inc=["off"]),
              T("Give me a before/after list for everything I had you change today.", inc=["4", "2", "on", "off"])],
       edits=[(f, '"tabSize": 4', '"tabSize": 2'), (f, '"wordWrap": "on"', '"wordWrap": "off"')], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c57():
    f = "文档/客户名单.txt"
    files = {f: L("张伟", "李娜", "黄涛", "周梅", "吴刚")}
    mk("hyb-35257", sub="D2", tt="undo", trap="TR-CLAIM", desc="Delete a name, restore it in place after the user realises the mistake, rename another", files=files,
       turns=[T("客户名单里有几个人？文件是 文档/客户名单.txt。", inc=["5"]),
              T("把“黄涛”删掉。"),
              T("糟了，黄涛是我误删的，请恢复到他原来的位置。并告诉我名单里谁排在他后面。", inc=["周梅"]),
              T("再把“周梅”改成“周美”。告诉我名单现在的完整内容和人数。", inc=["张伟", "李娜", "黄涛", "周美", "吴刚", "5"])],
       edits=[(f, "周梅", "周美")], must=["read_file", "replace_lines", "write_file"], rc=6)


@reg
def c58():
    f = "reports/subscriptions-oct.csv"
    files = {f: L("plan,subs,price", "Basic,120,9", "Pro,45,29", "Team,18,99")}
    mk("hyb-35258", sub="D2", tt="comp", trap="TR-CLAIM", desc="Monthly recurring revenue from a table, after a price change and churn, compared with the start", files=files,
       turns=[T("What is the total monthly recurring revenue (subs times price) in reports/subscriptions-oct.csv?", any=["4167", "4,167"]),
              T("Raise the Pro price to 32 and tell me the new total.", any=["4302", "4,302"]),
              T("Team lost 3 subscribers, so update that row and give me the new total.", any=["4005", "4,005"]),
              T("How much did the total change from where we started?", any=["162"])],
       edits=[(f, "Pro,45,29", "Pro,45,32"), (f, "Team,18,99", "Team,15,99")], vals=["162"], must=["read_file", "replace_lines", "write_file", "calculator", "bash", "data_query"], rc=7, dep="4167 -> 4005 = -162")


@reg
def c59():
    t, out = "数据/本周工单.csv", "文档/周报-第42周.md"
    files = {t: L("编号,状态", "T-301,已解决", "T-302,已解决", "T-303,已解决", "T-304,未解决", "T-305,已解决", "T-306,已解决", "T-307,未解决", "T-308,未解决"),
             "文档/周报-第41周.md": L("已解决 4 个，未解决 2 个")}
    mk("hyb-35259", sub="D2", tt="write", trap="TR-CLAIM", desc="Weekly report built from a ticket table, extended, then corrected after one ticket is resolved", files=files,
       turns=[T("本周工单里有几个已解决？表在 数据/本周工单.csv。", inc=["5"]),
              T("照上周周报的格式，写一份 文档/周报-第42周.md，一行：已解决 n 个，未解决 m 个。"),
              T("再追加一行：“未解决编号：”后面跟编号，用顿号隔开。"),
              T("T-307 其实已经解决了，把周报改对。然后告诉我现在已解决几个、原来几个。", inc=["6", "5"])],
       writes={out: ["已解决 6 个", "未解决 2 个", "T-304", "T-308"]}, must=["read_file", "write_file", "append_file", "replace_lines", "search_text"], rc=7)


@reg
def c60():
    v, n = "pkg/version.txt", "docs/release-notes-draft.md"
    files = {v: "2.7.1\n", n: L("## 2.7.1 (draft)", "", "- Added CSV export")}
    mk("hyb-35260", sub="D2", tt="comp", trap="TR-MULTISRC", desc="Bump a version in two files, append a bullet, recall the previous version and heading", files=files,
       turns=[T("What version does pkg/version.txt say, and does the heading in docs/release-notes-draft.md match it?", inc=["2.7.1"]),
              T("Bump both to 2.8.0.", inc=["2.8.0"]),
              T("Append the bullet '- Fixed timezone parsing' to the very end of the release notes draft."),
              T("Tell me the version and heading as they stand now, and what they said before.", inc=["2.7.1", "2.8.0"])],
       edits=[(v, "2.7.1", "2.8.0"), (n, "## 2.7.1 (draft)", "## 2.8.0 (draft)")], adds=[(n, "- Fixed timezone parsing\n")], must=["read_file", "replace_lines", "write_file", "append_file"], rc=7)
