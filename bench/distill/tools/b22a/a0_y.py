"""34079-34090 A0 control (part 2)."""
from kit import *


def build():
    a0("hyb-34079", "local_first", "琥珀速递", "我们发货表里记的琥珀速递 2 公斤以内的运费是多少？",
       {"物流/运费表.md": "# 运费表\n\n琥珀速递：2 公斤以内 14 元，2–5 公斤 22 元。上次核对 2026-08。\n", "物流/备注.txt": "偏远地区加 6 元\n"},
       [("https://hupo-express.example/rates", "资费 - 琥珀速递", "2026-09-13", "琥珀速递资费。", "# 资费\n\n2 公斤以内 16 元；2–5 公斤 25 元。\n")],
       val="14 元", exc=["16 元"], p2="官网现在是多少？", val2="16 元")
    a0("web-34080", "latest_version", "Tidewater ORM", "Which Tidewater ORM version is pinned in our lockfile?",
       {"requirements.lock": "tidewater-orm==2.6.1\nclickrunner==8.1.0\n", "docs/stack.md": "Data layer: Tidewater ORM.\n"},
       [("https://tidewater-orm.example/releases", "Releases - Tidewater ORM", "2026-09-09", "Releases.", "# Releases\n\n2.9.0 (stable, 2026-09-09)\n2.8.4\n")],
       val="2.6.1", exc=["2.9.0"])
    a0("web-34081", "lookup_value", "樱桃停车场", "我们物业公告里写的樱桃停车场月租多少钱？",
       {"物业/公告.md": "# 物业公告\n\n樱桃停车场月租 300 元，每季度结算一次。\n", "物业/联系人.txt": "物业电话见门口\n"},
       [("https://yingtao-parking.example/monthly", "月租价格 - 樱桃停车场", "2026-09-10", "月租。", "# 月租价格\n\n月租 360 元。\n")],
       val="300 元", exc=["360 元"], p2="停车场自己网站上现在写多少？", val2="360 元")
    a0("hyb-34082", "local_first", "Greywell Telecom", "What does the internal wiki page say our Greywell Telecom contract rate is?",
       {"wiki/vendors.md": "# Vendors\n\nGreywell Telecom: contracted rate 42 dollars per line per month until 2027-02.\n", "wiki/contacts.txt": "account rep: Priya\n"},
       [("https://greywell-telecom.example/business", "Business plans - Greywell Telecom", "2026-09-04", "Business plan rates.", "# Business plans\n\nStandard rate: 55 dollars per line per month.\n")],
       val="42", exc=["55 dollars"])
    a0("web-34083", "deprecation", "松萝文档", "咱们项目文档里写的松萝文档计划什么时候迁移走？",
       {"docs/迁移计划.md": "# 迁移计划\n\n松萝文档将在 2026-12-01 前完成迁出，之后只读。\n", "docs/负责人.txt": "迁移负责人：阿杰\n"},
       [("https://songluo-docs.example/notice", "服务公告 - 松萝文档", "2026-09-01", "松萝文档公告。", "# 服务公告\n\n松萝文档将于 2027-03-31 停止服务。\n")],
       dany=dates("2026-12-01"), val=None, exc=["2027-03-31"])
    a0("hyb-34084", "local_first", "Dunlin Hosting", "In our infra notes, what plan are we on with Dunlin Hosting?",
       {"infra/hosting.md": "# Hosting\n\nWe are on the Dunlin Hosting 'Team 8' plan (8 GB RAM).\n", "infra/costs.csv": "item,cost\nhosting,48\n"},
       [("https://dunlin-hosting.example/plans", "Plans - Dunlin Hosting", "2026-09-12", "Hosting plans.", "# Plans\n\nTeam 8: 8 GB RAM, 48 dollars. Team 16: 16 GB RAM, 90 dollars. Team 8 is renamed 'Growth' from October.\n")],
       val="Team 8", exc=["Growth"], p2="Does their site say anything about renaming?", val2="Growth")
    a0("web-34085", "lookup_value", "银河电影院", "我们公司福利表里写的银河电影院团体票是多少钱一张？",
       {"福利/权益.md": "# 福利权益\n\n银河电影院团体票：每张 29 元，需提前一周预约。\n", "福利/申请.txt": "找行政\n"},
       [("https://yinhe-cinema.example/group", "团体票 - 银河电影院", "2026-09-07", "团体票价格。", "# 团体票\n\n每张 35 元，20 张起订。\n")],
       val="29 元", exc=["35 元"])
    a0("hyb-34086", "local_first", "Ptarmigan Cloud", "According to our runbook, what's the Ptarmigan Cloud API rate limit we agreed?",
       {"runbook/limits.md": "# Limits\n\nPtarmigan Cloud API: our agreed limit is 600 requests per minute.\n", "runbook/alerts.txt": "page at 90%\n"},
       [("https://ptarmigan-cloud.example/docs/limits", "Rate limits - Ptarmigan Cloud", "2026-09-05", "API rate limits.", "# Rate limits\n\nDefault: 300 requests per minute.\n")],
       val="600", exc=["300 requests"], p2="and the default on their docs?", val2="300")
    a0("web-34087", "latest_version", "琴岛输入法", "我手机应用清单里记的琴岛输入法是什么版本？",
       {"手机/应用清单.md": "# 应用清单\n\n- 琴岛输入法 8.2.4\n- 天气 App 3.0\n", "手机/说明.txt": "半年更新一次\n"},
       [("https://qindao-ime.example/android", "安卓版 - 琴岛输入法", "2026-09-13", "安卓版。", "# 安卓版\n\n最新版本 9.1.0。\n")],
       val="8.2.4", exc=["9.1.0"])
    a0("hyb-34088", "local_first", "Corrie Water", "What did the council letter in our folder say the Corrie Water bill is per quarter?",
       {"house/water-letter.txt": "Corrie Water: quarterly bill for your address is 87.40 pounds.\n", "house/other.txt": "meter read in October\n"},
       [("https://corrie-water.example/tariffs", "Tariffs - Corrie Water", "2026-09-01", "Tariffs.", "# Tariffs\n\nAverage household quarterly bill: 96.10 pounds.\n")],
       val="87.40", exc=["96.10"])
    a0("web-34089", "lookup_value", "潮汐健康", "我们体检套餐文件里，潮汐健康的基础套餐价格是多少？",
       {"体检/套餐.md": "# 体检套餐\n\n潮汐健康 基础套餐 398 元，含血常规与心电图。\n", "体检/预约.txt": "周六上午\n"},
       [("https://chaoxi-health.example/packages", "套餐 - 潮汐健康", "2026-09-11", "套餐价格。", "# 套餐\n\n基础套餐 428 元。\n")],
       val="398", exc=["428"], p2="官网上基础套餐现在多少？", val2="428")
    a0("hyb-34090", "local_first", "Larch Conferencing", "Which Larch Conferencing seat count did we buy, per the invoice file?",
       {"finance/larch-invoice.txt": "Larch Conferencing - 25 seats - annual - paid 2026-02\n", "finance/other.txt": "misc\n"},
       [("https://larch-conferencing.example/pricing", "Pricing - Larch Conferencing", "2026-09-10", "Seat pricing.", "# Pricing\n\nTeams of 30 seats and above get a discount.\n")],
       val="25", exc=["30 seats"])
