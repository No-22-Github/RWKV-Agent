"""B1 (web-34101..34110): the user pastes a URL; read it with web_fetch."""
from common import *


def build():
    # 34101 zh, URL at the end, near-miss duration on the same page + a search-only older page
    mk("web-34101", sub="B1", tt="lookup_value", desc="User pastes a returns-policy URL at the end of the message",
       web=[fx("兰灯书店", "https://shop.lantern-books.example/help/returns", "退货与退款 - 兰灯书店", "兰灯书店的退货期限与退款到账时间。",
               "# 退货与退款\n\n自收货之日起 7 天内可无理由退货（图书类 15 天内）。商品需保持完好、附件齐全。\n\n## 退款到账\n原路退回：银行卡 3–5 个工作日，支付宝或微信 1 个工作日内。\n\n## 不支持退货的商品\n定制类商品、已拆封的电子书兑换码。", "2026-08-12"),
            fx("兰灯书店", "https://shop.lantern-books.example/help/returns-2023", "退货说明（2023 版）- 兰灯书店", "2023 年的旧版退货说明。",
               "# 退货说明（2023 版）\n\n自收货之日起 30 天内可退货。\n", "2023-04-02")],
       turns=[T("帮我看看这个页面里普通商品的退货期限是几天：https://shop.lantern-books.example/help/returns", any=["7 天", "7天", "七天", "7 days"],
                exc=NOWEB + ["30 天", "30天"]),
              T("退款多久能到账？", req=(), any=["3–5", "3-5", "3 到 5", "3到5", "三到五", "3～5", "3~5"])],
       traps=["TR-DECOY"], policy=WFS, ref="web_fetch(shop.lantern-books.example/help/returns) -> 读 7 天 -> 作答",
       why="普通商品 7 天，图书类 15 天，旧版 30 天只在搜索页里。", trap_notes=["同页有图书类 15 天的近似值；搜索可得旧版 30 天页面。"])
    # 34102 en, URL at the start, plan table
    mk("web-34102", sub="B1", tt="lookup_value", desc="URL first, question after the dash; rate-limit table",
       web=[fx("brightloop", "https://docs.brightloop.example/api/rate-limits", "Rate limits - BrightLoop API", "Per-minute request limits for each plan.",
               "# Rate limits\n\n| Plan | Requests per minute | Burst |\n| --- | --- | --- |\n| Free | 60 | 2x for 10 s |\n| Pro | 600 | 2x for 10 s |\n| Team | 3000 | 1.5x for 30 s |\n\nLimits are applied per API key. Exceeding them returns HTTP 429 with a Retry-After header.", "2026-09-04"),
            fx("brightloop", "https://docs.brightloop.example/v1/limits-archive", "Rate limits (v1, archived) - BrightLoop API", "Archived v1 limits.",
               "# Rate limits (v1, archived)\n\nPro: 450 requests per minute.\n", "2024-11-02")],
       turns=[T("https://docs.brightloop.example/api/rate-limits — what's the per-minute request limit for the Pro plan?", inc=["600"],
                exc=NOWEB + ["450 requests", "450/min"])],
       traps=["TR-DECOY"], policy=WFS, ref="web_fetch -> table row Pro = 600", why="Pro row says 600; Team 3000 and archived 450 are decoys.",
       trap_notes=["表格里相邻的 Team 行；搜索可得 archived v1 页面（450）。"])
    # 34103 zh, anchor, URL in the middle
    mk("web-34103", sub="B1", tt="lookup_value", desc="URL with #section anchor in the middle of the sentence",
       web=[fx("清风实验室", "https://wiki.qingfeng-lab.example/guide/safety", "实验室安全手册 - 清风实验室", "实验室安全规定。",
               "# 实验室安全手册\n\n## 第 1 节 门禁\n工作日 8:00–20:00 刷卡进入，周末须提前登记。\n\n## 第 2 节 化学品\n试剂开封后须在 30 天内用完或回收。\n\n## 第 3 节 数据与样品\n实验记录与样品标签须保留 90 天，之后方可清理。\n\n## 第 4 节 事故报告\n事故发生后 24 小时内提交书面报告。", "2026-07-21")],
       turns=[T("我在看 https://wiki.qingfeng-lab.example/guide/safety#section-3 这一页，第 3 节要求的记录保留时间是多久？", any=["90 天", "90天", "九十天", "90 days"])],
       traps=["TR-DECOY"], ref="web_fetch(去掉锚点也能抓) -> 第 3 节 90 天", why="第 3 节写 90 天；第 2 节 30 天、第 4 节 24 小时是邻近数值。",
       trap_notes=["锚点 #section-3 被抓取时丢掉，需自己在正文里定位到第 3 节。"])
    # 34104 en, http, own line, multi-turn follow up on same page
    mk("web-34104", sub="B1", tt="lookup_value", desc="http:// URL on its own line, then a follow-up on the same page",
       web=[fx("harborferry", "http://www.harborferry.example/timetable/summer.html", "Summer timetable - Harbor Ferry", "Ferry times for the summer season.",
               "# Summer timetable\n\nFirst sailing 06:30 every day.\n\n- Weekdays: last sailing 21:30\n- Weekends: last sailing 22:15\n- Public holidays: last sailing 23:00\n\nBicycles travel free; cars must be booked 24 hours ahead.", "2026-05-30")],
       turns=[T("Can you open this and tell me the last sailing on weekends?\nhttp://www.harborferry.example/timetable/summer.html", inc=["22:15"]),
              T("And what do I need to do to bring a car?", req=(), any=["24 hours", "booked", "book", "24 小时"])],
       traps=["TR-DECOY"], ref="web_fetch -> weekends 22:15; follow-up answered from the same page", why="Weekend row is 22:15.",
       trap_notes=["weekday / holiday rows are near misses."], rc=2)
    # 34105 zh query params, error meaning
    mk("web-34105", sub="B1", tt="error_meaning", desc="URL with query parameters first, error code meaning",
       web=[fx("mintpay", "https://api.mintpay.example/v2/errors?code=E4021&lang=zh", "错误码 E4021 - MintPay", "E4021 的含义与处理建议。",
               "# 错误码 E4021\n\n含义：账户可用余额不足，无法完成本次扣款。\n\n处理建议：提示用户充值后重试，不要自动重复提交。\n\n相关错误码：E4012（签名无效）、E4030（超出单笔限额）。", "2026-06-18"),
            fx("mintpay", "https://api.mintpay.example/v2/errors?code=E4012&lang=zh", "错误码 E4012 - MintPay", "E4012 的含义。",
               "# 错误码 E4012\n\n含义：请求签名无效。\n", "2026-06-18")],
       turns=[T("https://api.mintpay.example/v2/errors?code=E4021&lang=zh 这个错误码是什么意思？", any=["余额不足", "余额"])],
       traps=["TR-DECOY"], ref="web_fetch -> E4021 = 余额不足", why="E4021 页面写明余额不足；E4012 是另一个码。", trap_notes=["同站另一个错误码页面，查询串不同。"])
    # 34106 en markdown link, summarize
    mk("web-34106", sub="B1", tt="summarize_page", desc="Markdown link in the message; summarize a changelog page",
       web=[fx("pixelforge", "https://changelog.pixelforge.example/2026/09", "September 2026 - PixelForge changelog", "What shipped in September.",
               "# PixelForge changelog: September 2026\n\n## 3.8.0 (2026-09-09)\n- Added batch export for up to 200 images.\n- Fixed a crash when opening files larger than 2 GB.\n- Plugin API now requires version 4.\n\n## 3.7.2 (2026-09-02)\n- Fixed colour banding in gradient exports.\n", "2026-09-09")],
       turns=[T("Summarize [this changelog](https://changelog.pixelforge.example/2026/09) in two or three bullets.", inc=["3.8.0"],
                any=["batch export", "Batch export", "batch exports", "Batch exports"])],
       traps=[], ref="web_fetch -> 3.8.0 batch export, crash fix", why="Newest entry 3.8.0 with batch export.", trap_notes=["无陷阱，直读摘要。"], rc=1)
    # 34107 zh port, multi-turn follow-up
    mk("web-34107", sub="B1", tt="lookup_value", desc="URL with a port, in the middle; follow-up on a second date",
       web=[fx("书院", "http://notice.shuyuan.example:8080/exam/2026-final", "期末考试安排 - 校内通知", "2026-2027 学年第一学期期末考试安排。",
               "# 期末考试安排\n\n考试时间：2027 年 1 月 6 日至 1 月 9 日，共 4 天。\n补考时间：2027 年 2 月 24 日。\n成绩公布：1 月 20 日起可在教务系统查询。", "2026-12-15")],
       turns=[T("校内通知页在 http://notice.shuyuan.example:8080/exam/2026-final 这里，帮我查一下期末考试哪天开始。", any=["1月6日", "1 月 6 日", "2027-01-06", "1月6号", "1 月 6 号"]),
              T("那补考是哪天？", req=(), any=["2月24日", "2 月 24 日", "2027-02-24", "2月24号"])],
       traps=["TR-DECOY"], ref="web_fetch -> 1 月 6 日；追问补考 2 月 24 日", why="页面写明。", trap_notes=["成绩公布日是近似日期。"])
    # 34108 en angle brackets
    mk("web-34108", sub="B1", tt="lookup_value", desc="URL wrapped in angle brackets inside a sentence",
       web=[fx("northwind hostel", "https://policies.northwind-hostel.example/cancellation", "Cancellation policy - Northwind Hostel", "How cancellations are charged.",
               "# Cancellation policy\n\n- More than 48 hours before check-in: free cancellation.\n- 48 to 24 hours before: 50% of the first night.\n- Less than 24 hours or no-show: full first night.\n\nGroup bookings of 8 or more follow a separate 14-day rule.", "2026-03-11")],
       turns=[T("Per <https://policies.northwind-hostel.example/cancellation>, how many hours ahead of check-in can I cancel for free?", inc=["48"])],
       traps=["TR-DECOY"], ref="web_fetch -> 48 hours", why="Free cancellation up to 48 h before.", trap_notes=["24 小时与 14 天规则是近似值。"])
    # 34109 zh latest version, trailing slash; follow-up second URL
    mk("web-34109", sub="B1", tt="latest_version", desc="Release page URL with trailing slash, then a second URL in turn two",
       web=[fx("mochi sdk", "https://releases.mochi-sdk.example/stable/", "稳定版发布 - Mochi SDK", "Mochi SDK 当前稳定版。",
               "# Mochi SDK 稳定版\n\n当前稳定版：5.2.1（2026-09-10）\n\n5.1.x 已停止维护，请升级到 5.2.x。", "2026-09-10"),
            fx("mochi sdk", "https://releases.mochi-sdk.example/lts/", "长期支持版 - Mochi SDK", "Mochi SDK 长期支持版本。",
               "# Mochi SDK 长期支持版\n\n当前长期支持版：4.9.7（2026-08-01），安全补丁维护至 2027-08。", "2026-08-01"),
            fx("mochi sdk", "https://blog.mochi-sdk.example/posts/5-0-launch", "5.0 发布纪实 - Mochi 博客", "5.0.3 的发布记录。",
               "# 5.0 发布纪实\n\n当时的稳定版是 5.0.3。\n", "2025-10-01")],
       turns=[T("看一下 https://releases.mochi-sdk.example/stable/ 现在的稳定版本号是多少？", inc=["5.2.1"], exc=NOWEB + ["5.0.3"]),
              T("那长期支持版呢？https://releases.mochi-sdk.example/lts/", inc=["4.9.7"])],
       traps=["TR-WEBSTALE"], policy=WFS, ref="web_fetch stable -> 5.2.1；第二轮 web_fetch lts -> 4.9.7", why="两个页面各有一个版本号。",
       trap_notes=["搜索里有 5.0.3 的旧博客。"], rc=2)
    # 34110 en parens, deprecation
    mk("web-34110", sub="B1", tt="deprecation", desc="URL in parentheses at the end; deprecation date",
       web=[fx("relaypost", "https://docs.relaypost.example/webhooks/deprecations", "Deprecations - RelayPost", "Deprecated webhook endpoints.",
               "# Deprecations\n\n## v1 webhook endpoint\nThe v1 endpoint (`/hooks/v1`) is deprecated and will be removed on 2027-03-31. Migrate to `/hooks/v2`, which signs payloads with HMAC-SHA256.\n\n## Legacy SMTP relay\nRemoval date: 2027-09-30.", "2026-08-25")],
       turns=[T("Is the v1 webhook endpoint going away? (https://docs.relaypost.example/webhooks/deprecations)", any=dates("2027-03-31"))],
       traps=["TR-DECOY"], ref="web_fetch -> v1 removed 2027-03-31", why="v1 removal 2027-03-31; SMTP relay 2027-09-30 is a decoy.", trap_notes=["同页另一个下线日期。"])
