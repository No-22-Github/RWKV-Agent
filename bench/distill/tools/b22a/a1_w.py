"""34031-34040 A1 (part 4)."""
from kit import *


def build():
    a1("web-34031", "latest_version", "墨竹绘图", "墨竹绘图现在的正式版是多少？我装的是 3.6。",
       {"设计/工具.md": "# 设计工具\n\n画流程图用墨竹绘图，当前装的 3.6，不知道落后多少。\n", "设计/图.txt": "流程图 v2\n"},
       [("https://mozhu-draw.example/download", "下载中心 - 墨竹绘图", "2026-09-15", "墨竹绘图各平台安装包。",
         "# 下载中心\n\n正式版 4.1.2（2026-09-15）。长期支持版 3.9.7。预览版 4.2.0-preview 仅限邀请。\n")],
       val="4.1.2", p2="长期支持版是哪个？", val2="3.9.7", req2=())
    a1("hyb-34032", "local_first", "睡莲面包房", "睡莲面包房周末几点开门？",
       {"生活/早餐.md": "# 早餐计划\n\n周末想去睡莲面包房买早餐，时间要查一下。\n", "生活/地址.txt": "河边路 18 号\n"},
       [("https://shuilian-bakery.example/hours", "营业时间 - 睡莲面包房", "2026-09-01", "门店营业时间。",
         "# 营业时间\n\n周一至周五 7:00–19:00；周六、周日 8:30–17:00。\n每月第一个周一休息。\n")],
       val="8:30")
    a1("web-34033", "lookup_value", "Kestrel Fibre", "What's the monthly price of Kestrel Fibre's 500 Mbps plan?",
       {"home/internet.md": "# Home internet\n\nThinking of switching to Kestrel Fibre. Need the 500 Mbps price.\n", "home/contract.txt": "current provider contract ends in March\n"},
       [("https://kestrel-fibre.example/plans", "Plans - Kestrel Fibre", "2026-09-12", "Home fibre plans and prices.",
         "# Plans\n\n300 Mbps: 29 dollars per month.\n500 Mbps: 39 dollars per month.\n1 Gbps: 55 dollars per month.\nInstallation is free in September.\n")],
       val="39")
    a1("hyb-34034", "local_first", "紫藤公证处", "办一份房产委托公证，紫藤公证处收费多少？",
       {"家事/委托.md": "# 委托办理\n\n需要办一份房产委托公证，已选定紫藤公证处，费用待确认。\n", "家事/证件.txt": "身份证、房产证\n"},
       [("https://ziteng-notary.example/fees", "收费标准 - 紫藤公证处", "2026-08-31", "公证事项收费标准。",
         "# 收费标准\n\n委托公证：200 元/份（不涉及财产处分）；涉及房产处分的委托公证按标的额 0.3% 收取，不低于 300 元。\n")],
       dany=["300", "0.3%", "0.3 %", "千分之三"], fetch=True)
    a1("web-34035", "deprecation", "Wrenwood Notifier", "Is the SMS channel in Wrenwood Notifier going away? What replaces it?",
       {"alerts/config.json": "{\n  \"notifier\": \"wrenwood\",\n  \"channels\": [\"sms\", \"email\"]\n}\n", "alerts/README.md": "Alerts go out through Wrenwood Notifier on SMS and email.\n"},
       [("https://wrenwood.example/notices/sms", "SMS channel notice - Wrenwood Notifier", "2026-09-08", "Changes to SMS delivery.",
         "# SMS channel notice\n\nThe SMS channel is deprecated and will be removed on 2027-03-31. Use the push channel instead.\n")],
       dany=dates("2027-03-31"), p2="So which channel do I switch to?", dany2=["push", "Push"], req2=())
    a1("hyb-34036", "local_first", "青禾社区医院", "青禾社区医院今年的流感疫苗多少钱一针？",
       {"家庭/疫苗.md": "# 疫苗\n\n全家秋季打流感疫苗，青禾社区医院就近。价格没查。\n", "家庭/名单.txt": "爸、妈、我\n"},
       [("https://qinghe-clinic.example/vaccine", "疫苗接种 - 青禾社区医院", "2026-09-10", "秋季流感疫苗价格与预约。",
         "# 秋季流感疫苗\n\n四价流感疫苗 128 元/针，60 岁以上老人免费。\n需提前一天线上预约。\n")],
       val="128", p2="老人也要交钱吗？", dany2=["免费", "free", "Free", "不用"], req2=())
    a1("web-34037", "lookup_value", "云梯招聘", "云梯招聘上发一个职位，现在怎么收费？",
       {"hr/招聘.md": "# 招聘\n\n在云梯招聘上发职位，价格经常变，别按去年的算。\n", "hr/岗位.csv": "岗位,人数\n前端,2\n"},
       [("https://yunti-job.example/pricing", "企业服务价格 - 云梯招聘", "2026-09-03", "职位发布价格。",
         "# 企业服务价格\n\n单个职位 30 天：299 元。\n三个职位套餐：699 元。\n新企业首个职位免费。\n")],
       val="299", rev=("岗位.csv 里前端招几个人？", "2"))
    a1("hyb-34038", "local_first", "Cinderford Council", "How much is a garden waste permit from Cinderford Council this year?",
       {"house/garden.md": "# Garden\n\nNeed the Cinderford Council garden waste permit before the autumn clear-up.\n", "house/bins.txt": "green bin Tuesdays\n"},
       [("https://cinderford-council.example/garden-waste", "Garden waste permits - Cinderford Council", "2026-09-05", "Permit prices and renewals.",
         "# Garden waste permits\n\nAnnual permit: 54 pounds, valid 1 October 2026 to 30 September 2027.\nSecond bin: 30 pounds.\n")],
       val="54")
    a1("web-34039", "latest_version", "荷塘记账", "荷塘记账 iOS 版商店里现在最新是多少版本？",
       {"理财/App.md": "# 理财\n\n记账用荷塘记账（iOS）。听说新版支持自动导入账单。\n", "理财/日记.txt": "月底对账\n"},
       [("https://hetang-ledger.example/ios", "iOS 版 - 荷塘记账", "2026-09-18", "荷塘记账 iOS 版更新。",
         "# iOS 版\n\n当前版本 7.0.3（2026-09-18），新增银行账单自动导入。\n上一版 6.9.5。\n")],
       val="7.0.3", p2="自动导入是新版才有的吗？", dany2=["7.0", "新增", "新版", "新功能"], req2=())
    a1("hyb-34040", "local_first", "栗林露营地", "栗林露营地一晚帐篷位多少钱？要提前几天订？",
       {"周末/露营.md": "# 露营\n\n国庆去栗林露营地，价格和订位规则还没看。\n", "周末/装备.txt": "帐篷\n睡袋\n"},
       [("https://lilin-camp.example/book", "订位须知 - 栗林露营地", "2026-09-11", "营位价格与预订规则。",
         "# 订位须知\n\n普通帐篷位 120 元/晚；景观位 180 元/晚。\n国庆期间需至少提前 7 天预订。\n")],
       val="120", p2="国庆要提前几天？", val2="7", req2=())
