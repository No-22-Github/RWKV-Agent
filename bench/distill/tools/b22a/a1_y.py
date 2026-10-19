"""34011-34020 A1 (part 2)."""
from kit import *


def build():
    a1("hyb-34011", "local_first", "栖云笔记", "栖云笔记的 Windows 版最近一次更新是哪天发布的？",
       {"软件清单.md": "# 常用软件\n\n- 栖云笔记（Windows，同事推荐，还没装）\n- 7-Zip\n", "软件清单备注.txt": "装之前先看一下它最近有没有更新\n"},
       [("https://qiyun-notes.example/changelog/windows", "Windows 更新日志 - 栖云笔记", "2026-09-17", "栖云笔记 Windows 版更新日志。",
         "# Windows 更新日志\n\n6.8.1（2026-09-17）修复同步冲突。\n6.8.0（2026-08-29）新增表格块。\n")],
       dany=dates("2026-09-17"))
    a1("web-34012", "lookup_value", "Alder Cloud", "What's the free tier request limit on Alder Cloud functions now?",
       {"infra/overview.md": "# Infra overview\n\nSmall webhooks run as Alder Cloud functions to stay on the free tier. Watch the quota.\n", "infra/alerts.md": "Alert when usage > 80%.\n", "infra/owner.txt": "ops team\n"},
       [("https://alder-cloud.example/docs/free-tier", "Free tier - Alder Cloud docs", "2026-08-30", "What the free tier includes.",
         "# Free tier\n\nFunctions: 2 million requests per month, 400,000 GB-seconds of compute.\nBeyond that: 0.20 dollars per million requests.\n")],
       dany=["2 million","2,000,000","2M","200 万","200万","两百万"])
    a1("hyb-34013", "local_first", "岚山驿站", "岚山驿站的退房时间是几点？",
       {"旅行/行程.md": "# 周末行程\n\n周五晚入住岚山驿站，周日上午在山上走走再回。退房别太晚。\n", "旅行/清单.txt": "雨伞\n充电宝\n"},
       [("https://lanshan-inn.example/guest-info", "入住须知 - 岚山驿站", "2026-09-09", "入住、退房与早餐时间。",
         "# 入住须知\n\n入住 15:00 起，退房 11:30 前。早餐 7:30–9:30。\n延迟退房每小时加收 30 元。\n")],
       val="11:30", p2="延迟退房一小时多少钱？", val2="30")
    a1("web-34014", "deprecation", "Marrow DB", "Is Marrow DB 2.x still supported, and until when?",
       {"README.md": "# Inventory service\n\nStorage: Marrow DB 2.x (self-hosted). Upgrades are scheduled quarterly.\n", "ops/upgrade-plan.md": "Q4: evaluate newer Marrow DB major.\n"},
       [("https://marrowdb.example/support-policy", "Support policy - Marrow DB", "2026-08-05", "Supported versions and end-of-life dates.",
         "# Support policy\n\nMarrow DB 3.x: supported. Marrow DB 2.x: security fixes only until 2026-12-31, then end of life.\nMarrow DB 1.x: unsupported.\n")],
       dany=dates("2026-12-31"))
    a1("hyb-34015", "local_first", "芦苇社保代缴", "芦苇社保代缴每个月的服务费是多少？",
       {"行政/社保.md": "# 社保\n\n新入职的同事社保交给芦苇社保代缴办理，服务费另付。\n", "行政/联系人.txt": "行政：小周\n"},
       [("https://luwei-shebao.example/price", "服务价格 - 芦苇社保代缴", "2026-09-03", "代缴服务价格。",
         "# 服务价格\n\n单人单月 80 元；10 人以上团体每人每月 60 元。\n首月免服务费。\n")],
       val="80 元", fetch=True)
    a1("web-34016", "latest_version", "Pebbleshore CLI", "Which version of Pebbleshore CLI should I install today?",
       {"scripts/deploy.sh": "#!/bin/sh\n# needs the Pebbleshore CLI installed\npebbleshore push ./dist\n", "scripts/README.md": "Deploy script wraps the Pebbleshore CLI.\n"},
       [("https://pebbleshore.example/cli/install", "Install the CLI - Pebbleshore", "2026-09-16", "Install instructions.",
         "# Install\n\nThe installer fetches CLI 1.38.4 (current). Run `pebbleshore --version` to check.\nRelease candidates: 1.39.0-rc.1 (not recommended).\n")],
       val="1.38.4", p2="我装完后怎么确认版本？", val2="--version", req2=())
    a1("hyb-34017", "local_first", "云杉停车", "云杉停车的月卡现在多少钱一个月？",
       {"通勤/停车.md": "# 停车\n\n公司附近的云杉停车场打算办月卡，先别急着交钱。\n", "通勤/路线.txt": "地铁 2 号线换乘\n"},
       [("https://yunshan-parking.example/monthly", "月卡办理 - 云杉停车", "2026-09-12", "月卡价格与办理流程。",
         "# 月卡办理\n\n普通车位月卡 380 元；充电车位月卡 520 元。凭行驶证到管理处办理。\n")],
       val="380", rev=("通勤路线.txt 里写的是几号线换乘？", "2 号线"))
    a1("web-34018", "lookup_value", "Thistledown Bank", "What's the current savings rate on Thistledown Bank's basic account?",
       {"finance/accounts.md": "# Accounts\n\nSavings sit in the Thistledown Bank basic account. Rates change, so check before moving money.\n", "finance/todo.txt": "review insurance\n"},
       [("https://thistledown-bank.example/savings", "Basic savings account - Thistledown Bank", "2026-09-15", "Rates for savings accounts.",
         "# Basic savings\n\nVariable rate: 3.15% AER, effective 15 September 2026. Minimum balance: none.\n")],
       val="3.15")
    a1("hyb-34019", "local_first", "鹤鸣驾校", "鹤鸣驾校的 C1 班报名费现在是多少？",
       {"家庭/学车计划.md": "# 学车计划\n\n打算今年秋天去鹤鸣驾校报 C1，先看看价格。\n", "家庭/日程.txt": "周六试课\n"},
       [("https://heming-driving.example/c1", "C1 班报名 - 鹤鸣驾校", "2026-09-07", "C1 班费用与优惠。",
         "# C1 班\n\n普通班 4980 元；周末班 4680 元；学生优惠立减 300 元。\n")],
       val="4980", p2="周末班呢？", val2="4680", req2=())
    a1("web-34020", "error_meaning", "Tallowmere Gateway", "Tallowmere Gateway keeps returning error GW-4012 — what does that code mean?",
       {"logs/tallowmere-upstream-2026-09-16.log": "2026-09-16 09:12:44 WARN upstream call failed code=GW-4012\n2026-09-16 09:12:51 WARN upstream call failed code=GW-4012\n", "logs/log-source-note.txt": "Logs from the Tallowmere Gateway.\n"},
       [("https://tallowmere.example/docs/errors/GW-4012", "GW-4012 - Tallowmere Gateway errors", "2026-07-22", "Meaning of GW-4012.",
         "# GW-4012\n\nThe upstream certificate has expired. Renew the upstream TLS certificate and restart the route.\n")],
       dany=["certificate", "Certificate", "expired", "Expired", "证书"], p2="How do I fix it?", dany2=["restart", "Restart", "重启"], req2=())
