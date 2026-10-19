"""B1 (web-34111..34120)."""
from common import *


def build():
    mk("web-34111", sub="B1", tt="lookup_value", desc="URL alone on the first line, ticket prices",
       web=[fx("天湖景区", "https://park.tianhu-scenic.example/ticket/price.html", "门票价格 - 天湖景区", "天湖景区门票与优惠政策。",
               "# 门票价格\n\n- 成人票：86 元\n- 学生票（凭学生证）：43 元\n- 1.2 米以下儿童：免票\n- 60 岁以上老人：半价\n\n旺季（7–8 月）不加价。", "2026-06-03")],
       turns=[T("https://park.tianhu-scenic.example/ticket/price.html\n这个页面上的成人票和学生票各多少钱？", inc=["86", "43"]),
              T("那 60 岁以上的老人呢？", req=(), any=["半价", "50%", "一半", "half"])],
       traps=["TR-DECOY"], ref="web_fetch -> 成人 86、学生 43", why="两个价格都在页面列表里。", trap_notes=["老人半价、儿童免票是干扰项。"])
    mk("web-34112", sub="B1", tt="lookup_value", desc="URL with page query and fragment in the middle of an English sentence",
       web=[fx("nimbusdb", "https://forum.nimbusdb.example/t/upgrade-guide?page=2", "Upgrade guide (page 2) - NimbusDB forum", "Step-by-step upgrade notes.",
               "# Upgrade guide, page 2\n\n**post #14:** Before upgrading to 6.0, make sure the data volume has at least 40 GB of free disk space; the migration writes a full copy of the catalog.\n\n**post #15:** On clusters with more than 3 nodes, upgrade replicas first.\n\n**post #16:** Memory: 16 GB RAM recommended.", "2026-07-30"),
            fx("nimbusdb", "https://forum.nimbusdb.example/t/upgrade-guide?page=1", "Upgrade guide (page 1) - NimbusDB forum", "Start here.",
               "# Upgrade guide, page 1\n\nBackup first. Disk space needs are covered later in the thread.\n", "2026-07-30")],
       turns=[T("I'm reading https://forum.nimbusdb.example/t/upgrade-guide?page=2#post-14 and it mentions a minimum amount of free disk. How much is it?", any=["40 GB", "40GB", "40 gigabytes"])],
       traps=["TR-DECOY"], ref="web_fetch(page=2) -> 40 GB", why="post 14 says 40 GB; RAM figure 16 GB is a decoy.", trap_notes=["page=1 与 page=2 是同路径不同查询串；必须带上 ?page=2。"])
    mk("web-34113", sub="B1", tt="latest_version", desc="Changelog URL in fullwidth parentheses, stable vs beta",
       web=[fx("快印", "https://dl.kuaiyin.example/changelog", "更新日志 - 快印", "快印桌面版更新记录。",
               "# 更新日志\n\n## 7.5.0-beta（测试版，2026-09-12）\n- 新增云端模板库（测试中）\n\n## 7.4.0（稳定版，2026-08-28）\n- 打印队列支持暂停与恢复\n- 修复 macOS 上的字体缺失\n\n## 7.3.9（2026-07-30）\n- 修复若干崩溃", "2026-09-12")],
       turns=[T("快印桌面版现在的稳定版是哪个版本（更新日志在 https://dl.kuaiyin.example/changelog ）？", inc=["7.4.0"])],
       traps=["TR-WEBSTALE"], ref="web_fetch -> 稳定版 7.4.0（beta 7.5.0 不算）", why="稳定版标注在 7.4.0。", trap_notes=["最上面一条是测试版。"])
    mk("web-34114", sub="B1", tt="lookup_value", desc="Pricing page URL at the end; annual price per seat",
       web=[fx("tidyboard", "https://tidyboard.example/pricing", "Pricing - Tidyboard", "Plans and per-seat prices.",
               "# Pricing\n\n| Plan | Monthly billing | Annual billing |\n| --- | --- | --- |\n| Solo | $6 / seat | $60 / seat |\n| Team | $12 / seat | $120 / seat |\n| Business | $20 / seat | $200 / seat |\n\nAnnual billing is charged once per year. Prices exclude tax.", "2026-09-01"),
            fx("tidyboard", "https://saas-compare.example/tidyboard-review", "Tidyboard review - SaaS Compare", "A third-party review with prices.",
               "# Tidyboard review\n\nWe saw Team at $144 per seat per year in 2025.\n", "2025-06-10")],
       turns=[T("How much per seat per year is the Team plan on annual billing? Here's the page: https://tidyboard.example/pricing", any=["$120", "120 dollars", "120/seat", "120 / seat", "USD 120"],
                exc=NOWEB + ["$144", "144 dollars"])],
       traps=["TR-DECOY"], policy=WFS, ref="web_fetch -> Team annual = $120", why="Team annual is $120; monthly $12 and the third-party $144 are decoys.", trap_notes=["搜索里有第三方 2025 年旧价。"])
    mk("web-34115", sub="B1", tt="compare_sources", desc="Two URLs in one message; which plan has more data",
       web=[fx("云帆通信", "https://yunfan-mobile.example/plans/basic", "基础套餐 - 云帆通信", "云帆通信基础套餐资费。",
               "# 基础套餐\n\n月费 39 元，含流量 100 GB，通话 200 分钟。", "2026-08-01"),
            fx("海岸移动", "https://haian-telecom.example/plans/lite", "轻享套餐 - 海岸移动", "海岸移动轻享套餐资费。",
               "# 轻享套餐\n\n月费 39 元，含流量 150 GB，通话 100 分钟。", "2026-08-15")],
       turns=[T("帮我对比这两个套餐：https://yunfan-mobile.example/plans/basic 和 https://haian-telecom.example/plans/lite ，哪个流量更多？", inc=["150", "100"])],
       traps=["TR-DECOY"], ref="两次 web_fetch -> 海岸 150 GB > 云帆 100 GB", why="两个页面各给一个流量值。", trap_notes=["月费相同，只有流量不同。"], rc=2)
    mk("web-34116", sub="B1", tt="lookup_value", desc="http URL first, English requirement question",
       web=[fx("quartzdb", "http://docs.quartzdb.example/install/requirements", "Requirements - QuartzDB", "System requirements for QuartzDB 3.",
               "# Requirements\n\n- Java 17 or newer (Java 11 is no longer supported).\n- Linux kernel 5.4+ or macOS 13+.\n- 8 GB RAM minimum.", "2026-04-20")],
       turns=[T("http://docs.quartzdb.example/install/requirements — which minimum Java version does it require?", inc=["17"]),
              T("And the minimum RAM?", req=(), any=["8 GB", "8GB", "8 gigabytes"])],
       traps=["TR-DECOY"], ref="web_fetch -> Java 17", why="Java 17+; 11 is explicitly dropped.", trap_notes=["页面里点名了已不支持的 11。"])
    mk("web-34117", sub="B1", tt="lookup_value", desc="Chinese page, anchor named after a section",
       web=[fx("小鱼快递", "https://help.xiaoyu-express.example/rules/weight", "重量与体积规则 - 小鱼快递", "超重、超大件的计费规则。",
               "# 重量与体积规则\n\n## 标准件\n单件 20 kg 以内按首重 + 续重计费。\n\n## 超重件 {#overweight}\n超过 20 kg 的部分，每公斤加收 3.5 元，单件上限 50 kg。\n\n## 超大件 {#oversize}\n三边之和超过 150 cm 的包裹按体积重计费，每 6000 立方厘米折 1 kg。", "2026-05-18")],
       turns=[T("https://help.xiaoyu-express.example/rules/weight#overweight 里写的超重附加费怎么算？", inc=["3.5"], any=["20 kg", "20kg", "20 公斤", "20公斤"])],
       traps=["TR-DECOY"], ref="web_fetch -> 超过 20 kg 部分每公斤 3.5 元", why="超重件一节写明。", trap_notes=["同页超大件规则（150 cm、6000）是邻近规则。"])
    mk("web-34118", sub="B1", tt="error_meaning", desc="Error-code doc URL at the end of an English question",
       web=[fx("stackhaven", "https://support.stackhaven.example/errors/err-quota-7", "ERR_QUOTA_7 - StackHaven support", "What ERR_QUOTA_7 means.",
               "# ERR_QUOTA_7\n\nThe workspace has exceeded its storage quota of 5 GB. Uploads are blocked until you delete files or upgrade to a larger plan.\n\nRelated: ERR_QUOTA_3 (seat limit reached).", "2026-02-09")],
       turns=[T("What does the error ERR_QUOTA_7 mean? Docs are at https://support.stackhaven.example/errors/err-quota-7", any=["5 GB", "5GB", "5 gigabytes"])],
       traps=["TR-DECOY"], ref="web_fetch -> storage quota 5 GB exceeded", why="Page states the 5 GB storage quota.", trap_notes=["ERR_QUOTA_3 是邻近错误码。"])
    mk("web-34119", sub="B1", tt="lookup_value", desc="Government notice URL in the middle; effective date vs publish date",
       web=[fx("清河市", "https://gov.qinghe-city.example/notice/2026/parking", "关于调整中心城区停车收费的通知 - 清河市", "停车收费新规通知。",
               "# 关于调整中心城区停车收费的通知\n\n发布日期：2026 年 8 月 28 日\n\n公示期：2026 年 8 月 28 日至 9 月 15 日。\n\n新规自 2026 年 10 月 1 日起执行：路内停车首小时 6 元，之后每小时 4 元。", "2026-08-28")],
       turns=[T("这个通知 https://gov.qinghe-city.example/notice/2026/parking 里说停车新规从哪天开始执行？", any=dates("2026-10-01"))],
       traps=["TR-DECOY"], ref="web_fetch -> 10 月 1 日起执行", why="执行日期 10 月 1 日；发布日和公示期是干扰项。", trap_notes=["发布日期 8 月 28 日、公示期截止 9 月 15 日。"])
    mk("web-34120", sub="B1", tt="lookup_value", desc="Three-turn conversation: two URLs, then a comparison without refetching",
       web=[fx("lumina", "https://shop.lumina-optics.example/lens/50mm-f18", "50mm f/1.8 - Lumina Optics", "Lumina 50mm f/1.8 lens.",
               "# Lumina 50mm f/1.8\n\nPrice: $349. Weight: 186 g. Filter size: 49 mm.", "2026-08-10"),
            fx("lumina", "https://shop.lumina-optics.example/lens/35mm-f20", "35mm f/2.0 - Lumina Optics", "Lumina 35mm f/2.0 lens.",
               "# Lumina 35mm f/2.0\n\nPrice: $299. Weight: 205 g. Filter size: 52 mm.", "2026-08-10")],
       turns=[T("What's the price of the lens at https://shop.lumina-optics.example/lens/50mm-f18 ?", inc=["349"]),
              T("Now the same for https://shop.lumina-optics.example/lens/35mm-f20", inc=["299"]),
              T("Which of the two is lighter, and by how many grams?", req=(), inc=["19"], any=["50mm", "50 mm", "f/1.8"])],
       traps=["TR-DECOY"], ref="fetch 50mm -> 349; fetch 35mm -> 299; 186 g vs 205 g -> 50mm lighter by 19 g", derived=["19"], why="Weights 186 and 205 give 19 g.", trap_notes=["第三轮需要记住前两页的重量。"], rc=2)
