"""33001-33012 summarize_page."""
from common import *

S = "TR-SNIPPETVAGUE"


def one(cid, brand, url, title, date, body, p1, inc1, extra=None, p2=None, inc2=None, lang_note="", pol=None, extra_traps=()):
    web = [fx(brand, url, title, "页面概述，具体条目见正文。" if p1[0] > "一" else "Overview; details are in the page body.", body, date)]
    turns = [T(p1, req=["web_fetch"], inc=inc1)]
    if extra:
        web.append(extra)
        turns.append(T(p2, req=["web_fetch"], inc=inc2))
    mk(cid, tt="summarize_page", desc="Summarize a fictional site page whose snippet is vague (%s)" % brand, web=web, turns=turns,
       traps=[S] + list(extra_traps), ref="web_search -> web_fetch 正文 -> 列出要点" + ("；追问再 fetch 第二页" if extra else ""),
       why="Key figures exist only in the fetched page content.", trap_notes=["snippet 不含要点，必须 web_fetch。"],
       policy=pol or WSF, level="L2" if extra else "L1", ref_calls=4 if extra else 2, sub="sum")


def build():
    one("web-33001", "浮光云盘", "https://fuguang-drive.example/blog/2026-10-plan-update", "10 月套餐调整公告 - 浮光云盘", "2026-09-28",
        "# 10 月套餐调整公告\n\n自 2026 年 10 月 15 日起：\n- 个人版存储由 200 GB 提升到 500 GB，月费 12 元不变；\n- 团队版每席位月费由 38 元调整为 45 元，最低 5 席；\n- 分享链接最长有效期由 90 天缩短为 30 天。\n\n已购年付套餐的用户，价格在到期前不变。团队版迁移指引见 https://fuguang-drive.example/docs/team-migration 。\n\n页脚：隐私政策 | 使用条款 | 订阅周报",
        "浮光云盘最近发了个套餐调整公告，帮我看下说了啥，列一下要点。", ["500", "45"],
        extra=fx("浮光云盘", "https://fuguang-drive.example/docs/team-migration", "团队版迁移指引 - 浮光云盘", "团队版迁移步骤。",
                 "# 团队版迁移指引\n\n1. 管理员在后台「组织设置」点击「升级至新版」；\n2. 旧成员会收到邀请邮件，7 天内确认即可保留历史文件；\n3. 迁移窗口内可随时回退，窗口结束后旧版席位冻结为只读。", "2026-09-29"),
        p2="那团队版怎么迁移？他们好像有说明页，帮我看看。", inc2=["只读"])
    one("web-33002", "Halden Notes", "https://haldennotes.example/changelog/5-2", "Halden Notes 5.2 release notes", "2026-08-19",
        "# Halden Notes 5.2\n\nHighlights:\n- Offline mode now syncs up to 4000 notes per device (was 1500).\n- New markdown table editor with column drag.\n- The legacy plugin API v2 is read-only; plugins must move to API v3 by 5.4.\n- Fixed: sync conflicts duplicated attachments (HN-3321).\n\nUpgrade: auto-update rolls out in waves over two weeks.",
        "Can you read the Halden Notes 5.2 release notes and give me the main points?", ["4000", "v3"], pol=WSF)
    one("web-33003", "青禾租房", "https://qinghe-rent.example/help/deposit-rules", "押金与退租规则 - 青禾租房", "2026-07-11",
        "# 押金与退租规则\n\n- 押金为一个月租金，最高不超过 3000 元；\n- 退租时房屋验收在 3 个工作日内完成，验收通过后 7 个工作日内原路退回押金；\n- 因自然损耗产生的墙面、地板老化不扣押金；\n- 租客人为损坏的，按维修发票金额扣除，须提供照片和发票；\n- 提前退租需提前 30 天通知，否则扣除半个月租金。",
        "我想了解青禾租房的押金和退租规则，帮我总结一下重点。", ["30", "7"], pol=WSF)
    one("web-33004", "Tidewater CLI", "https://tidewater-cli.example/docs/migrate-v3", "Migrating to Tidewater CLI 3", "2026-09-02",
        "# Migrating to Tidewater CLI 3\n\nBreaking changes:\n1. The `--out` flag is renamed `--output-dir`.\n2. Config now lives in `tidewater.toml`; `.tidewaterrc` is ignored.\n3. Minimum Node version is 20.\n\nRun `tidewater doctor --fix` to convert an old config automatically. Windows ARM builds arrive in 3.1.",
        "Summarize the Tidewater CLI 3 migration guide for me, what do I have to change?", ["--output-dir", "tidewater.toml"])
    one("web-33005", "岚山医保", "https://lanshan-ins.example/news/outpatient-2026", "2026 年门诊报销新规 - 岚山医保", "2026-09-10",
        "# 2026 年门诊报销新规\n\n一、起付线由 800 元降到 500 元；\n二、一级医院报销比例 75%，二级 65%，三级 50%；\n三、慢性病门诊单次限额 1200 元，需先在 App 内备案；\n四、异地就医须在就诊前 3 日完成备案，否则比例下调 10 个百分点。",
        "帮我看看岚山医保 2026 年门诊报销的新规定讲了什么，要点就行。", ["500"], pol=WSF)
    one("web-33006", "Pinecrest Library", "https://pinecrest-lib.example/news/fine-free", "Pinecrest goes fine-free", "2026-06-05",
        "# Pinecrest Library goes fine-free\n\nFrom 1 July the library no longer charges late fees on any item. Items are still due after 21 days; after 60 days overdue the item is marked lost and a replacement fee of up to 25 dollars applies. Existing fines under 50 dollars were cleared. Borrowers can hold 15 items at once, up from 10.",
        "What did Pinecrest Library announce about late fees? Summarize the page.", ["60", "15"], pol=WSF,
        extra=fx("Pinecrest", "https://pinecrest-lib.example/help/lost-items", "Lost items - Pinecrest Library", "What happens to lost items.",
                 "# Lost items\n\nIf an item is marked lost you can return it within 90 days of the lost date to cancel the replacement fee. Damaged items are assessed case by case by branch staff.", "2026-06-06"),
        p2="And if an item gets marked lost, can I still fix that? Check their lost items page.", inc2=["90"])
    one("web-33007", "墨砚出版", "https://moyan-press.example/author/royalty-update", "稿酬标准更新 - 墨砚出版", "2026-05-22",
        "# 稿酬标准更新\n\n自 6 月 1 日起，千字稿酬统一上调：文学类 120 元，科普类 150 元，译作 180 元。电子版分成比例由 8% 提高到 12%。稿酬在稿件终审通过后 20 个工作日内支付，须先提交税务信息表。",
        "墨砚出版最近改了稿酬标准，帮我读一下页面，说说要点。", ["150", "12%"], pol=WSF)
    one("web-33008", "Quarry Maps", "https://quarrymaps.example/blog/offline-regions", "Offline regions explained", "2026-09-14",
        "# Offline regions explained\n\nDownload a region once and Quarry Maps keeps it for 30 days without a connection. Each region is capped at 1.2 GB; larger areas are split into tiles. Turn-by-turn works offline, but live traffic and transit times do not. Regions refresh automatically on Wi-Fi when charging.",
        "下个月要出门，帮我读一下 Quarry Maps 讲离线区域的那篇文章，告诉我关键限制（比如容量）。", ["1.2"])
    one("web-33009", "星桥班车", "https://xingqiao-bus.example/notice/line-adjust", "线路调整通知 - 星桥班车", "2026-09-30",
        "# 线路调整通知\n\n10 月 8 日起：\n- 3 号线延长至科创园，首班 6:20，末班 22:10；\n- 7 号线暂停途经老港路，改走滨河大道；\n- 夜班 N2 每晚 23:00 与 23:40 各发一班。\n\n票价不变，月卡持有人无需换卡。",
        "星桥班车发了个线路调整通知，帮我看看都变了什么。", ["科创园", "N2"], pol=WSF)
    one("web-33010", "Copperleaf Pay", "https://copperleaf-pay.example/legal/fees-2027", "Fee schedule effective January", "2026-09-25",
        "# Fee schedule\n\nDomestic card payments: 1.9% + 0.25 per transaction. International cards: 3.2%. Refunds no longer return the fixed fee. Payouts are weekly by default; instant payout costs 1%, capped at 10. Disputes cost 15 per case, refunded if won.",
        "Read the Copperleaf Pay fee schedule and give me a short summary of what it costs.", ["1.9", "3.2"],
        extra=fx("Copperleaf", "https://copperleaf-pay.example/help/disputes", "Disputes - Copperleaf Pay", "How disputes work.",
                 "# Disputes\n\nYou have 7 days to submit evidence after a dispute opens. Missing the deadline loses the case automatically.", "2026-09-26"),
        p2="What's the deadline if a customer disputes a payment? Their disputes page should say.", inc2=["7"])
    one("web-33011", "海盐读书会", "https://haiyan-club.example/join/rules", "入会须知 - 海盐读书会", "2026-04-18",
        "# 入会须知\n\n会费每年 180 元，学生 90 元。每月第二个周六下午 2 点线下读书会，地点在南湾图书馆三楼。每季度须至少参加 2 次活动，否则会籍自动转为旁听。书单由会员投票，得票最高的前 3 本进入当季书单。",
        "海盐读书会的入会须知帮我总结下，我想知道会费和参加要求。", ["180", "旁听"], pol=WSF)
    one("web-33012", "Vantor Drones", "https://vantor-drones.example/support/flight-limits", "Flight limits for the Skiff 2", "2026-08-02",
        "# Skiff 2 flight limits\n\nMaximum altitude 120 m by default; geofence unlocks require an account verified for 24 hours. Wind limit 10 m/s. Battery 31 minutes hover time, but the app warns at 25 percent. Return-to-home triggers at 20 percent or signal loss longer than 6 seconds.",
        "帮我看一下 Vantor Skiff 2 的飞行限制页面，总结一下重点。", ["120", "10"], pol=WSF)
