"""33013-33024 compare_sources."""
from common import *


def cmp(cid, brand, a, b, p1, val, first=False, p2=None, val2=None, extra=None, pol=None, why="", level="L2"):
    """a, b: (url, title, date, content). val: the correct value (in the winning source)."""
    web = [fx(brand, x[0], x[1], x[3].split("\n")[0][:80], x[3], x[2]) for x in (a, b)]
    turns = [T(p1, req=["web_fetch"], inc=[val], first=[val] if first else [])]
    if p2:
        if extra:
            web.append(fx(brand, extra[0], extra[1], extra[3].split("\n")[0][:80], extra[3], extra[2]))
        turns.append(T(p2, req=["web_fetch"] if extra else [], inc=[val2]))
    mk(cid, tt="compare_sources", desc="Two sources disagree on a value for %s; the answer must pick the authoritative/newer one" % brand,
       web=web, turns=turns, traps=["TR-WEBSTALE", "TR-MULTISRC"], ref="两页都要打开比对来源与日期，按权威/较新者作答。",
       why=why or "Winning source is fixed by authority/date in the fixtures.", trap_notes=["两个来源数值不同，只看一个会错。"],
       policy=pol or WSF, level=level, ref_calls=4 if p2 else 3, sub="cmp")


def build():
    cmp("web-33013", "Kestrel Mail",
        ("https://kestrelmail.example/help/attachment-limit", "Attachment limits - Kestrel Mail Help", "2026-09-01", "# Attachment limits\n\nAs of September 2026 the maximum attachment size is 35 MB per message. Larger files are sent as download links."),
        ("https://mailtips-weekly.example/posts/kestrel-limits", "Kestrel Mail limits cheat sheet", "2025-11-14", "# Kestrel Mail cheat sheet\n\nAttachments max out at 25 MB per message, and 20 recipients per send."),
        "Kestrel Mail's help page and a tips blog disagree on the attachment size limit. Which one is the vendor's own page, which one is more recent, and what is the limit?", "35", first=True,
        why="Vendor help page dated 2026-09 beats the 2025 blog.")
    cmp("web-33014", "云麓出行",
        ("https://yunlu-go.example/notice/refund-2026", "退票规则调整公告 - 云麓出行", "2026-08-30", "# 退票规则调整\n\n自 9 月 1 日起，开车前 48 小时以上退票免手续费，48 小时内收取票价 20% 手续费。"),
        ("https://travelbbs.example/t/12877", "【干货】云麓出行退票怎么收费", "2026-09-20", "楼主整理：云麓出行开车前 24 小时以上免手续费，24 小时内收 10%（据旧版规则，未核实）。"),
        "云麓出行的退票手续费，官方公告和一个论坛帖子说的不一样。哪个是官方的、哪个更新？到底怎么收费？先给结论。", "20%", first=True,
        why="论坛帖更晚但注明未核实且依据旧规则；官方公告为准。")
    cmp("web-33015", "Brindle DB",
        ("https://brindledb.example/docs/limits", "Limits - Brindle DB docs (v7)", "2026-02-10", "# Limits\n\nMax connections per instance: 500."),
        ("https://brindledb.example/blog/7-3-release", "Brindle DB 7.3 released", "2026-09-05", "# 7.3 released\n\nStarting with 7.3 the default connection ceiling per instance is raised from 500 to 1200."),
        "Brindle DB 文档和 7.3 发布说明对最大连接数说法不同，都是厂商自己发的。现在的上限是多少，哪个页面更新？", "1200",
        why="Same vendor; the later release post supersedes the older docs page.")
    cmp("web-33016", "灯塔健身",
        ("https://dengta-fit.example/membership", "会员价格 - 灯塔健身", "2026-09-12", "# 会员价格\n\n月卡 258 元，季卡 688 元，年卡 1980 元（2026 年 9 月起执行）。"),
        ("https://dazhong-review.example/shop/9981", "灯塔健身 用户点评汇总", "2026-09-18", "多位用户反馈：月卡 238 元、年卡 1880 元，这是 6 月前的价格，现在已涨。"),
        "灯塔健身的月卡到底多少钱？官网和点评网站的数字对不上，帮我判断哪个可信，哪个更新。", "258", first=False,
        why="官网 9 月价格为准，点评站自己说明是 6 月前价格。", level="L2")
    cmp("web-33017", "Ostara Cloud",
        ("https://status.ostara-cloud.example/sla", "Service level agreement", "2026-07-01", "# SLA\n\nMonthly uptime commitment for Standard tier: 99.9%. Credits: 10% below 99.9%, 25% below 99.0%."),
        ("https://ostara-cloud.example/pricing/faq", "Pricing FAQ", "2026-03-04", "# Pricing FAQ\n\nStandard tier comes with a 99.5% uptime commitment."),
        "Ostara Cloud's SLA page and the pricing FAQ give different uptime numbers for the Standard tier. Which is the binding one and what's the figure?", "99.9",
        why="The SLA document is binding and newer than the FAQ.")
    cmp("web-33018", "稻香外卖",
        ("https://daoxiang-food.example/rider/pay-2026", "骑手结算说明 - 稻香外卖", "2026-09-03", "# 骑手结算\n\n基础单价 5.5 元/单，夜间（22:00 后）加 2 元，每周一结算上周收入。"),
        ("https://daoxiang-food.example/rider/pay-2025", "骑手结算说明（2025 版）- 稻香外卖", "2025-10-08", "# 骑手结算（2025 版，已被替代）\n\n基础单价 4.8 元/单，夜间加 1.5 元，每月 10 日结算。"),
        "稻香外卖骑手的基础单价是多少，结算周期多久？官网有两份说明，别拿错旧的。", "5.5",
        why="同站两页，2026 版为准。")
    cmp("web-33019", "Marlin Router",
        ("https://marlinrouter.example/support/fw-notes", "Firmware notes - Marlin Router", "2026-09-08", "# Firmware 4.8.1\n\nFixes the WPA3 reconnect bug. Recommended for all users."),
        ("https://wifi-nerds.example/marlin-4-9-beta", "Marlin Router 4.9 beta hands-on", "2026-09-16", "# Hands-on with 4.9 beta\n\nThe beta (not released by the vendor) adds mesh pairing; stable remains 4.8.1."),
        "现在该装 Marlin Router 的哪个固件版本？一页是厂商的，一页是体验博客，告诉我各是哪个。", "4.8.1",
        why="The blog is newer but about an unreleased beta; stable is 4.8.1.")
    cmp("web-33020", "紫藤药房",
        ("https://ziteng-pharm.example/service/delivery", "配送服务说明 - 紫藤药房", "2026-08-15", "# 配送服务\n\n订单满 59 元免配送费，不满收 6 元。配送时间 9:00–21:00。"),
        ("https://ziteng-pharm.example/promo/autumn", "秋季活动 - 紫藤药房", "2026-09-22", "# 秋季活动\n\n即日起至 10 月 31 日，订单满 29 元免配送费。"),
        "紫藤药房免配送费要满多少钱？他们的服务说明和活动页写得不一样，先说结论，再说为什么。", "29", first=True, why="活动页较新且标明活动期间，当前（9 月中下旬）满 29 免运费。", level="L2")
    cmp("web-33021", "Zephyr Editor",
        ("https://zephyr-editor.example/docs/shortcuts", "Keyboard shortcuts - Zephyr docs", "2026-05-20", "# Shortcuts\n\nCommand palette: Ctrl+Shift+P."),
        ("https://zephyr-editor.example/blog/keymap-change", "Keymap changes in 3.0", "2026-09-09", "# Keymap changes in 3.0\n\nThe command palette moves to Ctrl+K P to free up Ctrl+Shift+P for the terminal. The old docs page has not been updated yet."),
        "Zephyr Editor 当前版本里打开命令面板的快捷键是什么？文档和博客文章对不上，都是开发者自己发的。", "Ctrl+K P",
        why="The blog explicitly says the docs are stale.")
    cmp("web-33022", "北屿水务",
        ("https://beiyu-water.example/price/2026", "2026 年居民水价 - 北屿水务", "2026-01-05", "# 居民水价\n\n第一阶梯（年用水量 180 立方米以内）3.45 元/立方米。"),
        ("https://beiyu-gov.example/notice/water-adjust", "关于调整居民水价的通知 - 北屿市发改局", "2026-08-12", "# 关于调整居民水价的通知\n\n自 2026 年 10 月 1 日起，第一阶梯水价调整为 3.85 元/立方米。该通知由市发改局发布，水务公司网站将同步更新。"),
        "北屿现在居民第一阶梯水价是多少，10 月以后呢？水务公司网站和市发改局的通知哪个更权威、哪个更新？", "3.85", p2="那阶梯的分界线是多少立方米？", val2="180",
        why="发改局通知更新且更权威；分界线只在水务页。", level="L2")
    cmp("web-33023", "Nimbus Notes",
        ("https://nimbusnotes.example/pricing", "Pricing - Nimbus Notes", "2026-09-14", "# Pricing\n\nPro: 8 dollars per user per month billed annually. Team: 14 dollars."),
        ("https://saas-compare.example/nimbus-notes", "Nimbus Notes pricing breakdown", "2026-04-30", "# Nimbus Notes pricing\n\nPro costs 6 dollars per user per month; Team costs 12 dollars."),
        "What does Nimbus Notes Pro cost per user per month? The company site and a comparison site disagree - tell me which to trust.", "8", p2="And the Team plan on the company site?", val2="14",
        why="Vendor pricing page is newer and authoritative.")
    cmp("web-33024", "白沙渡轮",
        ("https://baisha-ferry.example/timetable", "航班时刻表 - 白沙渡轮", "2026-09-01", "# 时刻表（冬季班次自 9 月 1 日起）\n\n白沙—鹭岛：首班 7:10，末班 17:30。"),
        ("https://islandlife.example/guide/baisha", "鹭岛旅行指南", "2026-06-02", "# 鹭岛旅行指南\n\n白沙渡轮末班 19:00（夏季班次，冬季可能提前）。"),
        "去鹭岛的白沙渡轮现在末班几点？官方时刻表和旅游攻略写的不一样。", "17:30", p2="那首班呢？", val2="7:10",
        why="官方冬季时刻表为准，攻略为夏季班次。")
