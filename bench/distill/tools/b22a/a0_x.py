"""34066-34078 A0 control: the answer is in the workspace (part 1)."""
from kit import *


def build():
    a0("web-34066", "latest_version", "星轨图表", "我们看板项目现在用的星轨图表是哪个版本？",
       {"package.json": "{\n  \"name\": \"sales-board\",\n  \"dependencies\": {\n    \"xinggui-chart\": \"4.9.8\"\n  }\n}\n", "README.md": "# 销售看板\n\n折线图用星轨图表绘制。\n"},
       [("https://xinggui-chart.example/releases", "版本发布 - 星轨图表", "2026-09-10", "星轨图表历史版本与发布说明。", "# 版本发布\n\n- 5.2.1（稳定版）2026-09-10\n- 5.2.0 2026-08-21\n")],
       val="4.9.8", exc=["5.2.1"], p2="那它官网上现在最新稳定版是多少？", val2="5.2.1")
    a0("hyb-34067", "local_first", "Ravenhill Mail", "In our mail-setup notes, what attachment limit did we write down for Ravenhill Mail?",
       {"notes/inbox-config.md": "# Mail setup\n\nShared inbox runs on Ravenhill Mail. Attachment limit we configured: 25 MB per message.\n", "notes/owners.txt": "Lena - inbox owner\n"},
       [("https://ravenhill-mail.example/help/limits", "Sending limits - Ravenhill Mail Help", "2026-08-14", "Limits for attachments.", "# Sending limits\n\nAttachment size: 35 MB per message.\n")],
       val="25 MB", exc=["35 MB"])
    a0("hyb-34068", "local_first", "砚池云盘", "咱们备份说明里写的砚池云盘免费版容量是多少？",
       {"运维/备份策略.md": "# 备份说明\n\n每周日凌晨把 /data 同步到砚池云盘。免费版容量按 15 GB 规划，超了再议。\n", "运维/负责人.txt": "账号归属：运维组\n"},
       [("https://yanchi-drive.example/pricing", "套餐与价格 - 砚池云盘", "2026-09-05", "套餐对比。", "# 套餐与价格\n\n免费版：20 GB。个人版：2 TB，每月 69 元。\n")],
       val="15 GB", exc=["20 GB"], p2="它们网站上现在写的是多少？", val2="20 GB")
    a0("web-34069", "deprecation", "Brasswick API", "Our README says when we planned to move off the Brasswick v1 endpoints — what's the date?",
       {"README.md": "# Billing sync\n\nCalls the Brasswick API (v1 endpoints) nightly. Migration to v3 planned for 2026-11-15.\n", "src/api_client.py": "BASE = 'https://api.brasswick.example/v1'\n"},
       [("https://brasswick.example/blog/v1-sunset", "Sunsetting API v1 - Brasswick", "2026-07-30", "Timeline for v1.", "# Sunsetting API v1\n\nv1 shuts down completely on 2027-04-30.\n")],
       val=None, dany=dates("2026-11-15"), exc=["2027-04-30", "April 30"])
    a0("hyb-34070", "local_first", "鹤唳打印", "仓库那台鹤唳打印 T8 标签机，我们设备表里记的固件版本是多少？",
       {"设备/设备台账.md": "# 标签机\n\n鹤唳打印 T8 x2，固件 2.12.4（上次升级 2026-03）。\n", "设备/采购记录.txt": "T8 标签机 x2\n"},
       [("https://heli-print.example/support/t8", "T8 固件下载 - 鹤唳打印", "2026-09-02", "T8 固件。", "# T8 固件\n\n当前固件：2.14.7（2026-09-02）。\n")],
       val="2.12.4", exc=["2.14.7"])
    a0("web-34071", "lookup_value", "Calder Transit", "What did my commute plan say a monthly Calder Transit pass costs?",
       {"commute/budget-plan.md": "# Commute plan\n\nCalder Transit line 4. Monthly pass budgeted at 88 dollars.\n", "commute/times.csv": "day,depart\nMon,08:10\n"},
       [("https://calder-transit.example/fares", "Fares - Calder Transit", "2026-09-01", "Fares.", "# Fares\n\nMonthly pass: 96 dollars.\n")],
       val="88", exc=["96"], p2="And what does their fare page say now?", val2="96")
    a0("hyb-34072", "local_first", "竹影课堂", "我们采购记录里，竹影课堂的会员退款期限写的是几天？",
       {"采购/续费合同.md": "# 续费记录\n\n竹影课堂年度会员，合同约定退款期限 30 天内。\n", "采购/票据.txt": "竹影课堂 年度会员\n"},
       [("https://zhuying-class.example/help/refund", "退款规则 - 竹影课堂", "2026-08-20", "退款说明。", "# 退款规则\n\n年度会员 14 天内可退。\n")],
       val="30 天", exc=["14 天"])
    a0("web-34073", "latest_version", "Stonebridge Runtime", "Which Stonebridge Runtime version does our Dockerfile install?",
       {"docker/Dockerfile": "FROM base:slim\nRUN install-stonebridge 7.1.5\nCOPY app /app\n", "docs/install.md": "Stonebridge Runtime is installed in the image build step.\n"},
       [("https://stonebridge.example/download", "Download - Stonebridge Runtime", "2026-09-14", "Installers.", "# Download\n\nStable: 7.4.2 (2026-09-14)\n")],
       val="7.1.5", exc=["7.4.2"])
    a0("hyb-34074", "local_first", "赤松邮政", "店铺发货流程里写的赤松邮政 1 公斤以内运费是多少？",
       {"店铺/运费规则.md": "# 发货流程\n\n快递默认走赤松邮政，1 公斤以内按 10 元收取，包装另计。\n", "店铺/备注.txt": "老客户优先发货\n"},
       [("https://chisong-post.example/rates", "国内资费 - 赤松邮政", "2026-09-08", "资费表。", "# 国内包裹资费\n\n1 公斤以内：12 元\n")],
       val="10 元", exc=["12 元"], p2="官网现在的价格呢？", val2="12 元")
    a0("web-34075", "lookup_value", "Ridgemoor Fitness", "What monthly price did we budget for the Ridgemoor Fitness membership?",
       {"budget/yearly.md": "# Budget\n\nGym: Ridgemoor Fitness membership, budgeted 35 dollars monthly.\n", "budget/memo.txt": "Ask about annual discount\n"},
       [("https://ridgemoor-fitness.example/join", "Join - Ridgemoor Fitness", "2026-09-11", "Membership options.", "# Join\n\nMonthly: 39 dollars.\n")],
       val="35", exc=["39"])
    a0("hyb-34076", "local_first", "霞谷温泉", "我们团建方案里写的霞谷温泉成人门票是多少钱？",
       {"团建/活动预算.md": "# 团建方案\n\n霞谷温泉：成人票按 140 元/人预算（团体价），共 12 人。\n", "团建/名单.csv": "姓名\n小王\n"},
       [("https://xiagu-spring.example/ticket", "门票 - 霞谷温泉", "2026-09-10", "门票。", "# 门票\n\n成人 158 元。\n")],
       val="140", exc=["158"], p2="官网现价是多少？", val2="158")
    a0("web-34077", "deprecation", "Sedgewick DB", "Which Sedgewick DB version does our inventory service actually run?",
       {"README.md": "# Inventory service\n\nStorage: Sedgewick DB 2.8.3 (self-hosted).\n", "ops/roadmap.md": "Q4: evaluate newer Sedgewick DB major.\n"},
       [("https://sedgewickdb.example/support-policy", "Support policy - Sedgewick DB", "2026-08-05", "Support.", "# Support policy\n\nSedgewick DB 3.x: supported. 2.x: end of life 2026-12-31.\n")],
       val="2.8.3", exc=["2026-12-31", "December 31"])
    a0("hyb-34078", "local_first", "听涛笔记", "我的软件清单里记的听涛笔记是哪个版本？",
       {"已装软件.md": "# 常用软件\n\n- 听涛笔记 6.5.0（Windows，已安装）\n- 7-Zip\n", "已装软件备注.txt": "每季度检查一次更新\n"},
       [("https://tingtao-notes.example/changelog/windows", "Windows 更新日志 - 听涛笔记", "2026-09-17", "更新日志。", "# Windows 更新日志\n\n6.8.1（2026-09-17）\n")],
       val="6.5.0", exc=["6.8.1"], p2="官网上现在最新是哪一版？", val2="6.8.1")
