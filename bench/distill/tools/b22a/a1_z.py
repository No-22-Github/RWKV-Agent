"""34021-34030 A1 (part 3)."""
from kit import *


def build():
    a1("web-34021", "lookup_value", "月白租房", "月白租房平台现在收中介费吗？比例多少？",
       {"租房/看房记录.md": "# 看房记录\n\n两套候选房都是在月白租房上找到的，平台规则变过几次，需要重新确认费用。\n", "租房/预算.txt": "月租上限 4500\n"},
       [("https://yuebai-rent.example/help/fee", "费用说明 - 月白租房", "2026-09-04", "平台收费说明。",
         "# 费用说明\n\n租客不再支付中介费（自 2026 年 9 月 1 日起）。房东侧收取成交月租 40% 的服务费。\n押金不得超过一个月租金。\n")],
       dany=["不再", "不收", "免", "免费", "no longer", "free of", "doesn't charge", "does not charge", "不用付", "无需"], p2="押金最多收多少？", val2="一个月", req2=())
    a1("hyb-34022", "local_first", "Larkspur Tickets", "When do Larkspur Tickets go on sale for the autumn concert series?",
       {"events/autumn.md": "# Autumn concerts\n\nWe want seats for the autumn series. Tickets are sold through Larkspur Tickets; on-sale date TBD.\n", "events/seats.txt": "4 seats, side block\n"},
       [("https://larkspur-tickets.example/autumn-series", "Autumn series on sale - Larkspur Tickets", "2026-09-10", "On-sale dates for the autumn series.",
         "# Autumn series\n\nPresale for members: 24 September 2026, 10:00.\nGeneral on-sale: 26 September 2026, 10:00.\n")],
       dany=dates("2026-09-26"), p2="And the member presale?", dany2=dates("2026-09-24"), req2=())
    a1("web-34023", "latest_version", "寒蝉输入法", "寒蝉输入法安卓版现在最新是哪个版本？",
       {"手机/应用.md": "# 手机应用\n\n输入法：寒蝉输入法（安卓）。偶尔有联想卡顿。\n", "手机/应用补充.txt": "更新前先备份词库\n"},
       [("https://hanchan-ime.example/android", "安卓版 - 寒蝉输入法", "2026-09-13", "寒蝉输入法安卓版下载。",
         "# 安卓版\n\n最新正式版 9.3.6（2026-09-13），优化联想速度。\n测试版 9.4.0-beta.2。\n")],
       val="9.3.6", rev=("应用.md 里写的是哪个输入法？", "寒蝉输入法"))
    a1("hyb-34024", "local_first", "沙棘快运", "沙棘快运寄冷链生鲜，一箱最多能装多重？",
       {"网店/发货.md": "# 发货\n\n生鲜走沙棘快运冷链，泡沫箱已备。重量限制待确认。\n", "网店/库存.csv": "item,qty\n蓝莓,40\n"},
       [("https://shaji-express.example/cold-chain", "冷链服务 - 沙棘快运", "2026-09-06", "冷链包裹规格与费用。",
         "# 冷链服务\n\n单箱重量上限 20 公斤，尺寸不超过 60×40×40 厘米。\n加急次日达加收 15 元。\n")],
       val="20 公斤", fetch=True)
    a1("web-34025", "deprecation", "Gorsefield Auth", "Are Gorsefield Auth's legacy API keys being removed? When?",
       {"config/auth.yaml": "provider: gorsefield\nmode: legacy_key\n", "config/NOTES.md": "Auth runs on Gorsefield Auth with the legacy key mode for now.\n"},
       [("https://gorsefield.example/changelog/keys", "Legacy API keys retirement - Gorsefield Auth", "2026-08-18", "Retirement schedule for legacy keys.",
         "# Legacy API keys retirement\n\nLegacy keys stop working on 2026-11-30. Use scoped tokens instead.\n")],
       dany=dates("2026-11-30"))
    a1("hyb-34026", "local_first", "朱砂医保", "朱砂医保个账里的钱，想给家人买药的话要先办什么手续？",
       {"家庭/医保.md": "# 医保\n\n爸妈的药想用我的朱砂医保个账买，不知道现在让不让。\n", "家庭/药品.txt": "降压药\n"},
       [("https://zhusha-yibao.example/notice/family", "家庭共济通知 - 朱砂医保", "2026-08-25", "个人账户家庭共济办理说明。",
         "# 家庭共济\n\n自 2026 年 7 月起，参保人可绑定配偶、父母、子女，使用个人账户余额为其支付药品和诊疗费用。\n需在 App 中完成亲属绑定。\n")],
       val="绑定", p2="能给哪些亲属用？", val2="父母", req2=())
    a1("web-34027", "lookup_value", "Nimbus Valley Library", "How many books can I borrow at once from Nimbus Valley Library?",
       {"study/library-loan-plan.md": "# Study plan\n\nBorrow reference books from Nimbus Valley Library. The loan limit changed this year, so check.\n", "study/reading-list-linear-algebra.txt": "Linear Algebra\n"},
       [("https://nimbusvalley-library.example/borrowing", "Borrowing - Nimbus Valley Library", "2026-09-02", "Loan limits and renewals.",
         "# Borrowing\n\nAdult members: up to 12 items at once for 28 days. Renewals: 2 times unless reserved.\n")],
       val="12")
    a1("hyb-34028", "local_first", "梧桐书房", "梧桐书房的自习座位怎么收费？包月多少？",
       {"学习/自习点.md": "# 自习点\n\n梧桐书房离家近，想包月。\n", "学习/备忘.txt": "带身份证\n"},
       [("https://wutong-study.example/seats", "座位价格 - 梧桐书房", "2026-09-09", "自习座位按时按月收费。",
         "# 座位价格\n\n按小时：8 元/小时。\n包月（不限时）：358 元。\n包季：960 元。\n")],
       val="358", p2="包季呢？", val2="960", req2=())
    a1("web-34029", "error_meaning", "Ironbark Queue", "What does exit status 78 mean when Ironbark Queue worker stops?",
       {"ops/runbook.md": "# Runbook\n\nIronbark Queue workers sometimes stop with a numeric exit status. Look the code up, don't guess.\n", "ops/pager.txt": "on-call: Dana\n"},
       [("https://ironbarkqueue.example/docs/exit-codes", "Worker exit codes - Ironbark Queue", "2026-07-11", "Exit status table for workers.",
         "# Exit codes\n\n0 - clean stop\n64 - bad arguments\n78 - invalid configuration file\n137 - killed by the OOM killer\n")],
       dany=["configuration", "Configuration", "config", "Config", "配置"])
    a1("hyb-34030", "local_first", "松露外卖", "松露外卖商家入驻要交保证金吗？多少？",
       {"创业/外卖计划.md": "# 外卖计划\n\n准备在松露外卖上开店，入驻成本还没摸清。\n", "创业/成本.csv": "项,金额\n设备,6000\n"},
       [("https://songlu-waimai.example/merchant/join", "商家入驻 - 松露外卖", "2026-09-14", "入驻条件、保证金和佣金。",
         "# 商家入驻\n\n保证金 2000 元，退出时无欠款可全额退还。\n佣金 6%。\n")],
       val="2000", fetch=True, p2="佣金是多少？", val2="6%", req2=())
