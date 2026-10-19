"""34001-34020 A1: local search comes back empty -> go online (part 1)."""
from kit import *


def build():
    a1("web-34001", "latest_version", "雾灯图表", "雾灯图表现在最新的稳定版是哪个版本？",
       {"看板说明-销售部.md": "# 销售看板\n\n折线图用雾灯图表绘制。升级前要先确认和现有页面是否兼容。\n", "看板待办清单.md": "- [ ] 看板加载慢\n- [ ] 雾灯图表的主题色统一\n"},
       [("https://wudeng-chart.example/releases", "版本发布 - 雾灯图表", "2026-09-10", "雾灯图表历史版本与发布说明。",
         "# 版本发布\n\n- 5.3.0-rc.1（预发布）2026-09-12\n- 5.2.1（稳定版）2026-09-10\n- 5.2.0 2026-08-21\n- 4.9.8（长期支持）2026-05-03\n")],
       val="5.2.1")
    a1("web-34002", "lookup_value", "Fernwick Mail", "What is the maximum attachment size Fernwick Mail currently allows per message?",
       {"notes/mail-setup.md": "# Mail setup\n\nThe team shared inbox runs on Fernwick Mail. Large files should go through the shared drive instead.\n", "notes/people.txt": "Lena - inbox owner\nTomas - backup\n"},
       [("https://fernwick-mail.example/help/limits", "Sending limits - Fernwick Mail Help", "2026-08-14", "Limits for attachments, recipients and daily sends.",
         "# Sending limits\n\nAttachment size: 35 MB per message (raised from 25 MB in July 2026).\nRecipients per message: 150.\nDaily sends: 1,000 per user.\n")],
       val="35")
    a1("hyb-34003", "local_first", "苔原云盘", "我们团队备份用的苔原云盘，免费版现在有多少容量？",
       {"运维/备份说明.md": "# 备份说明\n\n每周日凌晨把 /data 同步到苔原云盘。目前没有付费，先用免费版。\n", "运维/账号.txt": "账号归属：运维组\n"},
       [("https://taiyuan-drive.example/pricing", "套餐与价格 - 苔原云盘", "2026-09-05", "苔原云盘免费版与付费套餐对比。",
         "# 套餐与价格\n\n免费版：20 GB，单文件上限 2 GB。\n个人版：2 TB，每月 69 元。\n团队版：每人 5 TB，每月 148 元。\n")],
       val="20 GB", p2="那它个人版一个月多少钱？", val2="69")
    a1("web-34004", "deprecation", "Quartzline API", "When does Quartzline stop supporting the v1 REST endpoints?",
       {"README.md": "# Billing sync\n\nCalls the Quartzline API (v1 endpoints) nightly to pull invoices.\n", "src/client.py": "BASE = 'https://api.quartzline.example/v1'\n\ndef pull():\n    return BASE + '/invoices'\n"},
       [("https://quartzline.example/blog/v1-sunset", "Sunsetting API v1 - Quartzline", "2026-07-30", "Timeline for retiring the v1 REST endpoints.",
         "# Sunsetting API v1\n\nv1 endpoints enter read-only mode on 2027-01-15 and shut down completely on 2027-04-30. Migrate to v3 using the guide below.\n")],
       dany=dates("2027-04-30"))
    a1("hyb-34005", "local_first", "鸮羽打印", "鸮羽打印的 T8 标签机，最新固件是哪一版？",
       {"设备/标签机.md": "# 标签机\n\n仓库里用的是鸮羽打印 T8，偶尔卡纸。固件没升过级。\n", "设备/采购单.txt": "T8 标签机 x2\n"},
       [("https://xiaoyu-print.example/support/t8", "T8 固件下载 - 鸮羽打印", "2026-09-02", "T8 标签机固件与驱动。",
         "# T8 固件\n\n当前固件：2.14.7（2026-09-02）。更新内容：修复连续打印卡纸误报。\n历史固件：2.13.0、2.12.4。\n")],
       val="2.14.7", p2="这一版修了什么问题？", val2="卡纸", req2=())
    a1("web-34006", "lookup_value", "Brindle Transit", "How much is a monthly pass on Brindle Transit these days?",
       {"commute/monthly-pass-plan.md": "# Commute plan\n\nTake the Brindle Transit line 4 from Eastgate to the office. Check the fare before renewing.\n", "commute/line4-departures.csv": "day,depart\nMon,08:10\nTue,08:10\n"},
       [("https://brindle-transit.example/fares", "Fares - Brindle Transit", "2026-09-01", "Single, day and monthly fares.",
         "# Fares\n\nSingle ride: 2.75 dollars.\nDay pass: 7 dollars.\nMonthly pass: 96 dollars (from 1 September 2026).\n")],
       val="96")
    a1("hyb-34007", "local_first", "松烟课堂", "松烟课堂的会员退款，要在购买后几天内申请？",
       {"采购/会员续费.md": "# 续费记录\n\n松烟课堂年度会员，续费后发现课程不合适，考虑退款。\n", "采购/发票.txt": "松烟课堂 年度会员\n"},
       [("https://songyan-class.example/help/refund", "退款规则 - 松烟课堂", "2026-08-20", "会员与单课退款说明。",
         "# 退款规则\n\n年度会员：购买后 14 天内、学习时长不超过 2 小时可申请全额退款。\n单课：7 天内可退。\n")],
       val="14 天", fetch=True)
    a1("web-34008", "latest_version", "Cobbleway Runtime", "Which Cobbleway Runtime release is the current stable one?",
       {"docker/Dockerfile": "FROM base:slim\n# TODO: install the Cobbleway Runtime here\nCOPY app /app\n", "docs/setup.md": "Cobbleway Runtime is installed in the image build step.\n"},
       [("https://cobbleway.example/download", "Download - Cobbleway Runtime", "2026-09-14", "Installers and release channels.",
         "# Download\n\nStable: 7.4.2 (2026-09-14)\nBeta: 7.5.0-beta.3\nSecurity fixes: 7.4 and 7.3 lines only. Nightly builds are unsupported.\n")],
       val="7.4.2", p2="And which older line still gets security fixes?", val2="7.3", req2=())
    a1("hyb-34009", "local_first", "青檐邮政", "青檐邮政寄 1 公斤的国内包裹现在多少钱？",
       {"店铺/发货流程.md": "# 发货流程\n\n快递默认走青檐邮政。运费要在包裹单上手写，请先确认价格。\n", "店铺/客户.txt": "老客户优先发货\n"},
       [("https://qingyan-post.example/rates", "国内资费 - 青檐邮政", "2026-09-08", "国内包裹资费表。",
         "# 国内包裹资费\n\n1 公斤以内：12 元\n1–2 公斤：16 元\n2–5 公斤：24 元\n")],
       val="12 元")
    a1("web-34010", "lookup_value", "Hollowpine Fitness", "What is the monthly membership price at Hollowpine Fitness right now?",
       {"budget/gym-membership-2026.md": "# Budget\n\nGym: Hollowpine Fitness membership, monthly. Compare options before January.\n", "budget/annual-discount-question.txt": "Ask about annual discount\n"},
       [("https://hollowpine-fitness.example/join", "Join - Hollowpine Fitness", "2026-09-11", "Membership options and fees.",
         "# Join\n\nMonthly: 39 dollars. No joining fee until 31 October 2026, then 49 dollars.\nAnnual: 399 dollars.\n")],
       val="39")
