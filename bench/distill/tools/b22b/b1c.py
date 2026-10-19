"""B1 (web-34121..34130)."""
from common import *


def build():
    mk("web-34121", sub="B1", tt="summarize_page", desc="Summarize a blog post given by URL at the end",
       web=[fx("知微", "https://blog.zhiwei-dev.example/posts/cache-pitfalls", "缓存三大坑 - 知微博客", "缓存击穿、雪崩、穿透的区别与对策。",
               "# 缓存三大坑\n\n## 缓存击穿\n某个热点 key 过期的瞬间，大量请求同时打到数据库。对策：热点 key 加互斥锁或永不过期。\n\n## 缓存雪崩\n大批 key 在同一时刻过期。对策：给 TTL 加 10% 左右的随机抖动。\n\n## 缓存穿透\n查询根本不存在的数据，每次都落库。对策：布隆过滤器，或缓存空值 60 秒。", "2026-07-09")],
       turns=[T("把这篇文章总结成三点：https://blog.zhiwei-dev.example/posts/cache-pitfalls", inc=["击穿", "雪崩", "穿透"])],
       traps=["TR-DECOY"], ref="web_fetch -> 三个小节各一句", why="三种问题名称都在页面小节标题里。", trap_notes=["三个概念易混。"], rc=1)
    mk("web-34122", sub="B1", tt="lookup_value", desc="Refund window by URL, then a follow-up about subscriptions",
       web=[fx("coralpay", "https://legal.coralpay.example/terms/refunds", "Refund terms - CoralPay", "Refund windows by product.",
               "# Refund terms\n\n## One-time purchases\nRefund requests are accepted within 14 days of purchase.\n\n## Subscriptions\nMonthly and annual subscriptions can be refunded within 48 hours of a renewal charge.\n\n## Chargebacks\nOpening a chargeback voids any pending refund request.", "2026-08-05")],
       turns=[T("Read https://legal.coralpay.example/terms/refunds and tell me the refund window for one-time purchases.", inc=["14"], any=["14 days", "14-day", "fourteen"]),
              T("Does the same window apply to subscriptions?", req=(), any=["48 hours", "48-hour", "48 hour", "48h"])],
       traps=["TR-DECOY"], ref="web_fetch -> 14 days; follow-up -> subscriptions 48 hours", why="Two different windows on the same page.", trap_notes=["订阅窗口不同，不能照搬 14 天。"])
    mk("web-34123", sub="B1", tt="lookup_value", desc="URL with capital letters in host and path",
       web=[fx("睿翼", "http://docs.ruiyi-soft.example/api/quota.html", "接口配额 - 睿翼软件", "各套餐的每日接口调用额度。",
               "# 接口配额\n\n| 套餐 | 每日调用次数 |\n| --- | --- |\n| 免费版 | 500 |\n| 标准版 | 5000 |\n| 企业版 | 50000 |\n\n超出额度后返回 429，次日 0 点重置。", "2026-04-02")],
       turns=[T("睿翼软件标准版每天能调多少次接口？文档在 http://Docs.Ruiyi-Soft.example/API/Quota.html", any=["5000", "5,000", "5 千", "五千"])],
       traps=["TR-DECOY"], ref="web_fetch(大小写不敏感匹配) -> 标准版 5000", why="标准版 5000；免费 500、企业 50000 为邻行。", trap_notes=["网址大小写混用。"])
    mk("web-34124", sub="B1", tt="lookup_value", desc="Release page URL; breaking change then release date",
       web=[fx("driftline", "https://code.driftline.example/acme/relay/releases/tag/v2.14.0", "v2.14.0 - acme/relay", "Release notes for relay v2.14.0.",
               "# v2.14.0\n\nReleased 2026-09-03.\n\n## Breaking changes\n- The config key `timeout` was renamed to `timeout_ms` and now takes milliseconds.\n\n## Features\n- Added `--dry-run` to `relay sync`.\n\n## Fixes\n- Fixed a deadlock when two syncs start at once.", "2026-09-03")],
       turns=[T("What's the breaking change in https://code.driftline.example/acme/relay/releases/tag/v2.14.0 ?", inc=["timeout_ms"]),
              T("And when was that release published?", req=(), any=dates("2026-09-03"))],
       traps=["TR-DECOY"], ref="web_fetch -> breaking: timeout -> timeout_ms; date 2026-09-03", why="Breaking changes section.", trap_notes=["Features / Fixes 里的内容不是 breaking。"])
    mk("web-34125", sub="B1", tt="lookup_value", desc="Recipe URL with a servings query parameter",
       web=[fx("小厨", "https://recipes.xiaochu.example/r/hongshao-rou?serves=4", "红烧肉（4 人份）- 小厨食谱", "红烧肉 4 人份用量。",
               "# 红烧肉（4 人份）\n\n- 五花肉 600 g\n- 冰糖 30 g\n- 生抽 2 汤匙\n\n步骤：五花肉切块，冷水焯 3 分钟；小火炒糖色；加水没过肉，炖 50 分钟。", "2026-03-14"),
            fx("小厨", "https://recipes.xiaochu.example/r/hongshao-rou?serves=2", "红烧肉（2 人份）- 小厨食谱", "红烧肉 2 人份用量。",
               "# 红烧肉（2 人份）\n\n- 五花肉 300 g\n- 冰糖 15 g\n- 生抽 1 汤匙\n", "2026-03-14")],
       turns=[T("这个菜谱 https://recipes.xiaochu.example/r/hongshao-rou?serves=4 要用多少克五花肉？炖多久？", inc=["600"], any=["50 分钟", "50分钟", "五十分钟"])],
       traps=["TR-DECOY"], ref="web_fetch(serves=4) -> 600 g、炖 50 分钟", why="serves=4 页面 600 g；serves=2 是 300 g。", trap_notes=["同路径不同查询串，4 人份与 2 人份用量不同。"])
    mk("web-34126", sub="B1", tt="lookup_value", desc="Bare domain without scheme; SMTP port then a follow-up",
       web=[fx("sparrowmail", "https://www.sparrowmail.example/help/smtp-settings", "SMTP settings - SparrowMail help", "Server names and ports.",
               "# SMTP settings\n\nServer: smtp.sparrowmail.example\n\n- STARTTLS: port 587\n- SSL/TLS: port 465\n- Plain (not recommended): port 25\n\nUse your full e-mail address as the user name.", "2026-06-24")],
       turns=[T("Check www.sparrowmail.example/help/smtp-settings and tell me the port for STARTTLS.", inc=["587"]),
              T("And for SSL/TLS?", req=(), inc=["465"])],
       traps=["TR-DECOY"], ref="web_fetch(补全 https://) -> STARTTLS 587；追问 SSL/TLS 465", why="页面列出三个端口。", trap_notes=["网址没有协议头，需要自己补全。"])
    mk("web-34127", sub="B1", tt="lookup_value", desc="Bank fee page with a fragment; credit card annual fee",
       web=[fx("华鹭银行", "https://www.hualu-bank.example/rules/fee.html", "收费标准 - 华鹭银行", "借记卡与信用卡收费标准。",
               "# 收费标准\n\n## 借记卡 {#debit}\n年费 10 元，账户余额日均 3000 元以上免收。\n\n## 信用卡 {#card}\n年费 200 元；一个年度内刷卡满 6 次可免次年年费。\n\n## 转账手续费 {#transfer}\n跨行转账 5 万元以内每笔 2 元。", "2026-01-08")],
       turns=[T("https://www.hualu-bank.example/rules/fee.html#card 信用卡年费怎么收？", inc=["200"], any=["6 次", "6次", "六次"])],
       traps=["TR-DECOY"], ref="web_fetch -> 信用卡年费 200 元，刷满 6 次免", why="信用卡一节；借记卡年费 10 元为干扰。", trap_notes=["借记卡与转账手续费在同页。"])
    mk("web-34128", sub="B1", tt="lookup_value", desc="Moved page: the URL only holds a pointer to the real page",
       web=[fx("ledgerly", "https://docs.ledgerly.example/v1/auth", "Authentication (moved) - Ledgerly docs", "This page has moved.",
               "# Authentication\n\nThis page has moved to https://docs.ledgerly.example/v2/auth. The v1 documentation is no longer maintained.", "2025-12-01"),
            fx("ledgerly", "https://docs.ledgerly.example/v2/auth", "Authentication - Ledgerly docs", "Token lifetime and refresh.",
               "# Authentication\n\nAccess tokens are valid for 24 hours. Refresh tokens are valid for 30 days. Rotate client secrets at least every 90 days.", "2026-08-20")],
       turns=[T("How long is an access token valid? https://docs.ledgerly.example/v1/auth", inc=[], any=["24 hours", "24 hour", "24-hour", "24h", "24 小时"])],
       traps=["TR-WEBSTALE"], ref="web_fetch v1 -> 页面说已搬到 v2 -> web_fetch v2 -> 24 小时", why="v1 页面只有指针，答案在 v2。",
       trap_notes=["v1 页面没有答案，须跟随页面里给的新网址。"], rc=2)
    mk("web-34129", sub="B1", tt="lookup_value", desc="Timetable URL, then a follow-up on the last service",
       web=[fx("江南公交", "http://bus.jiangnan-transit.example/line/37", "37 路 - 江南公交", "37 路线路信息。",
               "# 37 路\n\n运营时间：首班 5:40，末班 22:30。\n高峰期（7:00–9:00，17:00–19:00）发车间隔 6 分钟，平峰 12 分钟。\n途经：火车站、文化宫、大学城、东湖公园。", "2026-02-17")],
       turns=[T("37 路公交的首班车是几点？线路页在 http://bus.jiangnan-transit.example/line/37", any=["5:40", "5：40", "05:40", "5 点 40", "5点40"]),
              T("末班呢？", req=(), any=["22:30", "22：30", "10:30 pm", "10:30 PM", "22 点 30", "22点30"])],
       traps=["TR-DECOY"], ref="web_fetch -> 首班 5:40；追问末班 22:30", why="运营时间一行给出首末班。", trap_notes=["发车间隔是邻近数字。"])
    mk("web-34130", sub="B1", tt="lookup_value", desc="URL followed by a full stop; forum post author and points",
       web=[fx("cinderyard", "https://news.cinderyard.example/item?id=48213", "Why we moved off microservices | Cinderyard News", "312 points by marlowe_k",
               "# Why we moved off microservices\n\n312 points by marlowe_k, 5 hours ago | 148 comments\n\nWe collapsed 41 services back into 6. Deploy time fell from 40 minutes to 7.\n\n---\n**top comment** by tessa_r (96 points): we did the same thing last year.", "2026-09-14"),
            fx("cinderyard", "https://news.cinderyard.example/item?id=48120", "Show: a tiny queue in Go | Cinderyard News", "88 points by oddvar",
               "# Show: a tiny queue in Go\n\n88 points by oddvar, 1 day ago | 21 comments\n", "2026-09-13")],
       turns=[T("Got this link from a colleague, see https://news.cinderyard.example/item?id=48213. Who posted it and how many points does it have?", inc=["marlowe_k", "312"])],
       traps=["TR-DECOY"], ref="web_fetch(id=48213) -> marlowe_k, 312", why="Header line of the item.", trap_notes=["网址末尾带句号；另一个 id 的帖子是干扰。"])
