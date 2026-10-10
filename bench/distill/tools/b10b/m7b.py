"""b10b M7 part B (v1.4 §3.7), 40 cases.
Unverified (official page fails, only a secondary page readable): web-8064..8077 (14), hyb-8033..8038 (6).
Preview vs stable (official page lists preview/rc/beta above stable): web-8078..8091 (14), hyb-8039..8044 (6).
Chinese: 21 of 40 (unverified web 7, hyb 4; preview web 7, hyb 3)."""
from m7b_lib import REV, unver, preview
REV.update({c: "S5：题面补一句「本地文件里没写，去厂家/上游查」——原题面只指向本地清单，老师查完本地就收尾，从不上网（0–1/3）。" for c in ['hyb-8033', 'hyb-8035', 'hyb-8036', 'hyb-8037', 'hyb-8038', 'hyb-8042', 'hyb-8044']})


def U(cid, zh, slug, brand, prompt, off, err, sec, value, answer, phrs, desc, **kw):
    o = dict(host=off[0], title=off[1], snip=off[2], date=off[3])
    s = dict(host=sec[0], title=sec[1], snip=sec[2], date=sec[3], body=sec[4])
    claim = value
    unver(cid, zh=zh, slug=slug, brand=brand, prompt=prompt, off=o, err=err, sec=s, value=value, claim=claim,
          answer=answer, phrs=phrs, desc=desc, **kw)


# ---------------------------------------------------------------- unverified, web
U("web-8064", True, "ferrypass", "青屿渡轮", "青屿渡轮的月票现在多少钱一张？",
  ("qingyu-ferry.gov.cn/fares", "青屿渡轮 票价公告", "青屿渡轮各类船票与月票价格。", "2026-09-02"), "HTTP 503 Service Unavailable",
  ("islandlife.cn/forum/ferry-pass", "岛上生活论坛：青屿渡轮月票涨价了", "有岛民说月票现在 468 元。", "2026-09-06",
   "# 青屿渡轮月票涨价了\n\n论坛帖子，2026-09-06。听售票窗口的人说，青屿渡轮月票从这个月起涨到 468 元一张，没见到正式公告。\n"),
  "468", "官方票价公告页打不开（503），没能核实。目前只在岛上生活论坛看到一个说法：青屿渡轮月票 468 元一张，发帖人也说没见到正式公告，这个数未经官方核实。",
  ["青屿渡轮 月票 价格", "青屿渡轮 票价公告", "青屿渡轮月票多少钱", "青屿渡轮 月票 涨价", "青屿渡轮 最新票价"],
  "Monthly pass price of a ferry line: the operator's fare page returns 503, a local forum post gives a figure that must be reported as unverified")

U("web-8065", False, "mailattach", "Halcyon Mail", "How many recipients can I put on a single Halcyon Mail message?",
  ("help.halcyonmail.com/limits", "Sending limits | Halcyon Mail Help", "Per-message and daily sending limits.", "2026-08-30"), "Request timed out after 30s",
  ("sysadmin-notes.net/halcyon-mail-limits", "Halcyon Mail limits cheat sheet", "A per-message cap of 450 recipients, according to a sysadmin.", "2026-07-14",
   "# Halcyon Mail limits cheat sheet\n\nPersonal notes from a sysadmin, 2026-07-14. Per message you can address up to 450 recipients (to+cc+bcc). Daily cap differs by plan; check the vendor docs.\n"),
  "450", "Halcyon Mail's own limits page timed out, so I couldn't verify this against the vendor. A sysadmin's notes say a single message can address up to 450 recipients, but that is unconfirmed until it is checked on the official help page.",
  ["Halcyon Mail recipients per message", "halcyon mail sending limits", "Halcyon Mail max recipients", "halcyon mail cc bcc limit", "Halcyon Mail help limits"],
  "Recipient cap per email: the vendor help page times out and only a sysadmin's notes give a number")

U("web-8066", True, "enrolquota", "湖滨大学", "湖滨大学今年硕士招生计划招多少人？",
  ("yz.hubin-univ.edu.cn/plan", "湖滨大学研究生招生计划", "2027 年硕士研究生招生计划与专业目录。", "2026-09-10"), "HTTP 502 Bad Gateway",
  ("kaoyan-circle.cn/hubin-plan", "湖滨大学 2027 硕士招生人数汇总", "考研圈整理：湖滨大学计划招收 320 人。", "2026-09-12",
   "# 湖滨大学 2027 硕士招生人数汇总\n\n考研圈整理，2026-09-12。据往年数据和院系透露，湖滨大学 2027 年硕士计划招收 320 人，最终以研招网公布为准。\n"),
  "320", "学校研招官网的招生计划页打不开（502），没能确认。考研圈整理的说法是计划招收 320 人，来源是往年数据和院系透露，未经官方核实，最终要以研招网公布的为准。",
  ["湖滨大学 硕士招生计划", "湖滨大学 研究生 招生人数", "湖滨大学 2027 招生计划", "湖滨大学 招多少人", "湖滨大学 研招"],
  "Planned master's intake of a university: the admissions office page returns 502, a prep-community summary gives a figure that has to be flagged unverified")

U("web-8067", False, "librarymember", "Alder Library", "What does Alder Library charge for a non-resident annual membership?",
  ("alderlibrary.org/membership", "Membership | Alder Public Library", "Library card and membership fees.", "2026-09-01"), "HTTP 404 Not Found",
  ("riverside-parents.org/alder-library-guide", "Riverside parents' guide to Alder Library", "Non-resident cards cost $112 a year, parents say.", "2026-05-19",
   "# Riverside parents' guide to Alder Library\n\nParent group notes, May 2026. Non-residents can buy an annual card for $112. Fees may have changed; ask the desk.\n"),
  "112", "The library's membership page returned 404, so I couldn't confirm the fee with Alder Library. A parents' guide from May says a non-resident annual card costs $112, but that is unverified and may have changed.",
  ["Alder Library non-resident membership fee", "alder public library card cost", "Alder Library annual membership", "alder library non resident card price", "Alder Library fees"],
  "Annual non-resident library card fee: the library's membership page 404s, only a parents' group guide has a figure")

U("web-8068", True, "ciquota", "云舟 CI", "云舟 CI 免费版每个月给多少构建分钟？",
  ("docs.yunzhou-ci.com/quota", "免费额度说明 - 云舟 CI 文档", "免费版与付费版的构建分钟与并发额度。", "2026-09-04"), "连接超时（30s）",
  ("devtalk.cn/t/yunzhou-ci-free", "云舟 CI 免费版够用吗？", "有人说免费版每月 750 分钟。", "2026-08-02",
   "# 云舟 CI 免费版够用吗？\n\n社区讨论，2026-08-02。楼主说看到免费版每月 750 构建分钟，并发 2；下面有人说去年还是别的数，官方文档为准。\n"),
  "750", "云舟 CI 官方的额度说明页访问超时，没能核实。社区帖子里有人说免费版每月 750 构建分钟，但下面也有人说和之前不一样，这个数未经官方确认，建议等文档能打开后再核对。",
  ["云舟 CI 免费版 构建分钟", "云舟 CI 免费额度", "云舟 CI 每月 构建 分钟", "云舟 CI 免费版 额度", "云舟 CI 文档 额度"],
  "Free build minutes per month of a CI service: docs page times out, a community thread gives a figure that should be flagged as unconfirmed")

U("web-8069", False, "airbaggage", "Brindle Air", "How much does Brindle Air charge for a second checked bag if I pay online?",
  ("brindleair.com/baggage-fees", "Baggage fees | Brindle Air", "Checked bag fees by route and purchase channel.", "2026-09-08"), "HTTP 503 Service Unavailable",
  ("frequentflyer-forum.net/brindle-bag", "Brindle Air second bag fee thread", "Members say it's $145 online.", "2026-09-03",
   "# Brindle Air second bag fee thread\n\nForum thread, Sept 2026. Booking online the second checked bag is $145 each way, a member reports; at the airport it is higher. No link to an official notice.\n"),
  "145", "Brindle Air's baggage fee page is returning an error right now, so I can't verify this officially. A frequent-flyer forum member reports $145 each way for the second checked bag when booked online, but that is unconfirmed.",
  ["Brindle Air second checked bag fee online", "brindle air baggage fees", "Brindle Air checked bag price", "brindle air second bag cost", "Brindle Air baggage"],
  "Second-bag fee of an airline: the airline's fee page returns 503, only a forum thread reports a price")

U("web-8070", True, "purifierfilter", "澜海", "澜海 AP-880 空气净化器配的滤芯是什么型号？",
  ("lanhai-home.com/support/ap880", "澜海 AP-880 配件与耗材", "AP-880 空气净化器滤芯与配件型号。", "2026-08-25"), "HTTP 503 Service Unavailable",
  ("jiadian-blog.cn/lanhai-ap880", "澜海 AP-880 使用三个月", "滤芯型号是 F-2231，自己换的。", "2026-07-28",
   "# 澜海 AP-880 使用三个月\n\n个人博客，2026-07-28。滤芯型号是 F-2231，网上买的，一百出头一片，自己换很简单。官方配件页没细看。\n"),
  "F-2231", "澜海官网的配件页现在打不开（503），没能核实。一篇个人博客里说 AP-880 用的滤芯是 F-2231，这是博主自己的使用记录，未经官方确认，买之前最好对照说明书或官网再确认一次。",
  ["澜海 AP-880 滤芯 型号", "澜海 空气净化器 滤芯", "澜海 AP-880 配件", "澜海 AP-880 耗材", "澜海 净化器 滤芯 型号是什么"],
  "Replacement filter model of an air purifier: the manufacturer's parts page fails, a personal blog gives a model number to report as unverified")

U("web-8071", False, "sdktimeout", "Quillbird", "What's the default request timeout in the Quillbird SDK?",
  ("quillbird.dev/docs/config", "Configuration | Quillbird SDK", "Client options and defaults.", "2026-09-05"), "Request timed out after 30s",
  ("stackhelp.example.org/q/quillbird-timeout", "Quillbird default timeout? (answered)", "Accepted answer: 120 seconds.", "2026-04-11",
   "# Quillbird default timeout?\n\nQ&A site, April 2026. Accepted answer: the client's default request timeout is 120 seconds; override with the timeout option. The answerer was on an older minor release.\n"),
  "120", "Quillbird's configuration docs timed out, so I couldn't verify the current default. A Q&A answer from April says 120 seconds, but the answerer was on an older release, so treat that as unconfirmed.",
  ["Quillbird SDK default timeout", "quillbird request timeout default", "Quillbird SDK config", "quillbird sdk timeout seconds", "Quillbird docs timeout option"],
  "Default SDK request timeout: the docs page times out, an older Q&A answer gives a number to report as unconfirmed")

U("web-8072", True, "parkticket", "栖霞岭", "栖霞岭景区冬季门票多少钱？",
  ("qixialing-scenic.cn/ticket", "栖霞岭景区 购票须知", "景区门票价格与优惠政策。", "2026-09-09"), "HTTP 404 Not Found",
  ("travelnotes.cn/qixialing-winter", "栖霞岭冬季游玩攻略", "冬季门票 240 元，攻略作者去年去的。", "2026-01-20",
   "# 栖霞岭冬季游玩攻略\n\n游记，2026-01-20。冬季门票 240 元（含索道往返），我们是上个冬天去的，今年有没有调价不清楚。\n"),
  "240", "栖霞岭景区官网的购票页打不开（404），没能核实今年的价格。去年冬天去过的游记里写的是 240 元（含索道往返），今年有没有调整无法确认，出发前最好再看一下景区公告。",
  ["栖霞岭景区 冬季门票", "栖霞岭 门票 价格", "栖霞岭景区 门票多少钱", "栖霞岭 冬季 票价", "栖霞岭 购票"],
  "Winter ticket price of a scenic area: official ticket page 404s, only last winter's travel note has a price")

U("web-8073", False, "coopshare", "Ostrander Co-op", "How much is a member share at Ostrander Co-op?",
  ("ostrandercoop.org/join", "Become a member | Ostrander Co-op", "Member share price and benefits.", "2026-08-20"), "HTTP 503 Service Unavailable",
  ("neighborhoodnews.example.com/ostrander-coop", "Ostrander Co-op opens second store", "News story mentions $310 shares.", "2026-06-02",
   "# Ostrander Co-op opens second store\n\nLocal news, June 2026. The co-op, whose member shares cost $310, opened a second location on Elm Street.\n"),
  "310", "The co-op's membership page returned an error, so I couldn't verify the price with Ostrander. A local news story from June mentions member shares costing $310 in passing; treat that as unconfirmed.",
  ["Ostrander Co-op member share price", "ostrander coop membership", "Ostrander Co-op join", "ostrander co-op share cost", "Ostrander Co-op"],
  "Member share price of a co-op: join page fails, a news story mentions a figure in passing")

U("web-8074", True, "marathonfee", "岚山马拉松", "岚山马拉松全程的报名费是多少？",
  ("lanshan-marathon.org/signup", "岚山马拉松 报名须知", "报名时间、名额与费用。", "2026-09-11"), "连接超时（30s）",
  ("runnerclub.cn/lanshan-2026", "岚山马拉松报名经验贴", "跑友：全程报名费 260 元。", "2026-09-13",
   "# 岚山马拉松报名经验贴\n\n跑友分享，2026-09-13。今年全程报名费 260 元，半马便宜些。我是从群里听来的，官网一直进不去。\n"),
  "260", "岚山马拉松官网的报名页访问超时，没能核实。跑友经验贴里写全程报名费是 260 元，但作者也说是群里听来的、没在官网看到，这个数未经官方确认。",
  ["岚山马拉松 全程 报名费", "岚山马拉松 报名", "岚山马拉松 报名费多少", "岚山马拉松 费用", "岚山马拉松 全马 报名费"],
  "Full-marathon entry fee: the race site times out, a runners' post passes on a figure heard in a chat group")

U("web-8075", False, "routerclients", "Corvid R7", "How many devices can the Corvid R7 router handle at once?",
  ("corvidnet.com/r7/specs", "Corvid R7 specifications", "Hardware specs and client limits.", "2026-09-07"), "HTTP 502 Bad Gateway",
  ("homelab-wiki.org/Corvid_R7", "Corvid R7 - Homelab wiki", "Community wiki: 128 simultaneous clients.", "2026-03-15",
   "# Corvid R7\n\nCommunity wiki, last edited 2026-03-15. Reported to handle about 128 simultaneous clients before throughput drops. Spec sheet not linked.\n"),
  "128", "Corvid's spec page is down (502), so I couldn't verify this. A community wiki says the R7 handles about 128 simultaneous clients, but it doesn't link a spec sheet, so that figure is unverified.",
  ["Corvid R7 router max devices", "corvid r7 specs clients", "Corvid R7 simultaneous clients", "corvid r7 how many devices", "Corvid R7"],
  "Client limit of a router: spec sheet page 502s, a community wiki gives a number with no source")

U("web-8076", True, "notebooks", "笔迹", "笔迹笔记软件免费版最多能建多少个笔记本？",
  ("bijinotes.com/pricing", "定价 - 笔迹", "免费版与专业版功能对比。", "2026-09-03"), "HTTP 503 Service Unavailable",
  ("sspai-like.cn/biji-review", "笔迹笔记软件评测", "评测：免费版最多 250 个笔记本。", "2026-02-27",
   "# 笔迹笔记软件评测\n\n评测文章，2026-02-27。免费版最多可以建 250 个笔记本，同步设备不限。写稿时官网定价页就改过一次，以官网为准。\n"),
  "250", "笔迹官网的定价页现在打不开（503），没能核实。2 月的一篇评测里写免费版最多 250 个笔记本，但文章自己也说官网定价页改过，所以这个数未经官方确认。",
  ["笔迹 笔记 免费版 笔记本数量", "笔迹 定价", "笔迹笔记软件 免费版 限制", "笔迹 免费版 最多 笔记本", "笔迹 笔记软件 评测"],
  "Notebook cap of a note app's free tier: pricing page 503s, a February review gives a number that predates a pricing change")

U("web-8077", False, "parkpermit", "Larkfield", "How much is an annual residential parking permit in Larkfield?",
  ("larkfield.gov/parking/permits", "Residential parking permits | City of Larkfield", "Permit zones, fees, and renewals.", "2026-09-01"), "HTTP 404 Not Found",
  ("larkfield-gazette.example.com/parking-permits", "Larkfield Gazette: What to know about parking permits", "Annual permit costs $215, Gazette says.", "2026-02-09",
   "# What to know about parking permits\n\nLarkfield Gazette, Feb 2026. An annual residential permit costs $215. The council is reviewing fees this fall.\n"),
  "215", "The city's permit page returned 404, so I couldn't verify the current fee. The Larkfield Gazette reported $215 for an annual residential permit back in February, and noted the council is reviewing fees, so that figure is unconfirmed.",
  ["Larkfield residential parking permit fee", "larkfield parking permits", "Larkfield annual parking permit cost", "larkfield city parking permit price", "Larkfield parking"],
  "Annual parking permit fee in a city: the city page 404s, a February news article gives a figure while fees are under review")


# ---------------------------------------------------------------- preview vs stable, web
def P(cid, zh, slug, style, brand, host, name, stable, sdate, prev, ptag, pdate, old, prompt, phrs, desc, blog=None, **kw):
    preview(cid, zh=zh, slug=slug, style=style, brand=brand, host=host, name=name, stable=stable, sdate=sdate, prev=prev,
            ptag=ptag, pdate=pdate, old=old, prompt=prompt, blog=blog, phrs=phrs, desc=desc, **kw)


P("web-8078", True, "dbchannel", 0, "砚台DB", "yantaidb.org/releases", "砚台DB", "3.7.2", "2026-09-02", "4.0.0-rc.3", "rc", "2026-09-10", "3.7.1",
  "我们要给客户部署砚台DB，现在能放心用的最新版本是哪个？",
  ["砚台DB 最新版本", "砚台DB 发布记录", "砚台DB 4.0", "砚台DB stable 版本", "砚台DB 生产环境 版本"],
  "Latest production-ready release of a database: the official page lists a 4.0 rc above the 3.7 stable line",
  blog=("dbweekly.cn/yantai-4", "砚台DB 4.0 抢先体验", "砚台DB 4.0.0-rc.3 已经很稳了，我们团队直接上了生产。"))
P("web-8079", False, "routerstable", 1, "Larkspur Router", "github.com/larkspur-go/router/releases", "larkspur-go/router", "v1.12.0", "2026-08-21",
  "v2.0.0-beta.2", "pre-release", "2026-09-09", "v1.11.4",
  "Which Larkspur Router version should we ship to customers right now?",
  ["Larkspur Router releases", "larkspur router latest stable", "Larkspur Router v2", "larkspur go router version for production", "Larkspur Router changelog"],
  "Version to ship to customers: GitHub releases list a v2 beta pre-release above the latest v1.12.0",
  blog=("gopher-notes.example.com/larkspur-v2", "Larkspur Router v2 first impressions", "v2.0.0-beta.2 is fast and the new API is great, we already switched."))
P("web-8080", True, "mqdownload", 2, "苇渡", "weidu-mq.io/download", "苇渡消息队列", "5.4.1", "2026-08-28", "5.5.0-beta.1", "beta", "2026-09-12", "5.4.0",
  "客户那边要装苇渡消息队列，下载页上给生产环境推荐的是哪个版本？",
  ["苇渡 消息队列 下载", "苇渡消息队列 最新版本", "苇渡 5.5", "苇渡 生产环境 推荐版本", "苇渡 消息队列 版本"],
  "Version recommended for production on a download page that also advertises a beta")
P("web-8081", False, "uikit", 3, "Mosaic CMS", "mosaic-cms.org/channels", "Mosaic CMS", "7.3.5", "2026-09-04", "7.4.0-rc.1", "release candidate", "2026-09-11", "7.3.4",
  "Which Mosaic CMS release can a customer safely install on a live site today?",
  ["Mosaic CMS releases", "Mosaic CMS latest stable", "Mosaic CMS 7.4", "mosaic cms release channels", "Mosaic CMS version live site"],
  "Newest installable release for a live site when the channels page lists a 7.4 release candidate")
P("web-8082", True, "monitorver", 1, "灯塔监控", "lighthouse-monitor.cn/changelog", "灯塔监控", "2.18.3", "2026-08-30", "2.19.0-preview.2", "preview", "2026-09-08", "2.18.2",
  "灯塔监控现在正式版最新是多少？客户生产环境想升级。",
  ["灯塔监控 最新版本", "灯塔监控 changelog", "灯塔监控 2.19", "灯塔监控 正式版", "灯塔监控 升级 生产环境"],
  "Latest stable of a monitoring product while a 2.19 preview heads the changelog",
  blog=("opsnotes.cn/lighthouse-219", "灯塔监控 2.19 预览版体验", "2.19.0-preview.2 的新告警引擎值得马上升级。"))
P("web-8083", False, "ormver", 0, "Quartzite ORM", "quartzite.dev/versions", "Quartzite ORM", "4.9.2", "2026-08-12", "5.0.0-alpha.4", "alpha", "2026-09-07", "4.9.1",
  "For a customer project that goes live next week, which Quartzite ORM version do we use?",
  ["Quartzite ORM versions", "quartzite orm latest stable", "Quartzite ORM 5.0", "quartzite orm production version", "Quartzite ORM release"],
  "Pick a version for a go-live next week: official table lists a 5.0 alpha first and 4.9.2 as stable")
P("web-8084", True, "pdfengine", 2, "竹简", "zhujian-doc.com/download", "竹简文档引擎", "6.2.0", "2026-09-01", "6.3.0-rc.2", "rc", "2026-09-13", "6.1.5",
  "竹简文档引擎，给客户交付的话用哪个版本？",
  ["竹简 文档引擎 版本", "竹简文档引擎 下载", "竹简 6.3", "竹简 文档引擎 推荐版本", "竹简文档引擎 最新稳定版"],
  "Delivery version of a document engine whose download page puts an rc under the recommended one")
P("web-8085", False, "pdfkit", 3, "Vellum PDF", "vellum-pdf.io/channels", "Vellum PDF", "9.1.1", "2026-07-30", "9.2.0-beta.3", "beta", "2026-09-10", "9.1.0",
  "Our customers need the highest Vellum PDF toolkit version that is officially supported. Which one is that?",
  ["Vellum PDF toolkit versions", "vellum pdf release channels", "Vellum PDF 9.2", "vellum pdf supported version", "Vellum PDF latest"],
  "Latest officially supported toolkit version when a 9.2 beta is listed above it",
  blog=("devblog.example.net/vellum-9-2", "Vellum PDF 9.2 is here", "9.2.0-beta.3 renders tables twice as fast; upgrade now."))
P("web-8086", True, "cliver", 0, "栈桥", "zhanqiao.dev/releases", "栈桥 CLI", "1.28.4", "2026-09-05", "1.29.0-next.5", "next", "2026-09-12", "1.28.3",
  "栈桥 CLI 的稳定版现在到哪个版本了？准备给客户的流水线固定下来。",
  ["栈桥 CLI 稳定版", "栈桥 CLI 版本", "栈桥 1.29", "栈桥 CLI releases", "栈桥 CLI 固定版本"],
  "Stable version to pin in a customer pipeline; the releases table has a next-channel build above it")
P("web-8087", False, "linterver", 1, "Basalt Linter", "basalt-lint.org/changelog", "Basalt Linter", "0.42.3", "2026-08-18", "0.43.0-rc.1", "release candidate", "2026-09-06", "0.42.2",
  "Which Basalt Linter version is the current stable one that we can roll out to customer repos?",
  ["Basalt Linter changelog", "basalt linter stable version", "Basalt Linter 0.43", "basalt lint latest release", "Basalt Linter rollout version"],
  "Current stable linter version to roll out; the changelog starts with a 0.43 release candidate")
P("web-8088", True, "uilib", 3, "松针UI", "songzhen-ui.cn/channels", "松针 UI 组件库", "8.6.0", "2026-08-26", "9.0.0-beta.4", "beta", "2026-09-09", "8.5.2",
  "松针UI组件库，客户项目现在能用的最新正式版是哪个？",
  ["松针UI 最新版本", "松针 UI 组件库 版本", "松针UI 9.0", "松针UI 正式版", "松针UI 发布通道"],
  "Newest official release of a UI library while 9.0 is still in beta",
  blog=("fe-daily.cn/songzhen-9", "松针UI 9.0 beta 实测", "9.0.0-beta.4 的组件体积小了三成，建议马上换。"))
P("web-8089", False, "queuever", 2, "Cinder Queue", "cinder-queue.dev/download", "Cinder Queue", "3.2.6", "2026-09-03", "3.3.0-preview.1", "preview", "2026-09-12", "3.2.5",
  "What version of Cinder Queue does the vendor recommend for production deployments?",
  ["Cinder Queue download", "cinder queue recommended version", "Cinder Queue 3.3", "cinder queue production version", "Cinder Queue latest"],
  "Vendor-recommended production version when the download page also advertises a 3.3 preview")
P("web-8090", True, "pyplot", 0, "星轨", "xingguiplot.org/releases", "星轨绘图库", "0.19.2", "2026-08-08", "0.20.0-rc.1", "rc", "2026-09-05", "0.19.1",
  "客户的数据报表要用星轨绘图库，该装哪个版本？",
  ["星轨绘图库 版本", "星轨 绘图库 最新", "星轨 0.20", "星轨绘图库 稳定版", "星轨 绘图库 安装"],
  "Which plotting-library version to install for a customer reporting job; rc listed above stable")
P("web-8091", False, "authlib", 1, "Heron Auth", "heron-auth.dev/changelog", "Heron Auth", "6.0.4", "2026-08-05", "6.1.0-beta.1", "pre-release", "2026-09-11", "6.0.3",
  "A client wants to adopt Heron Auth this month. Which release is the stable one to take?",
  ["Heron Auth changelog", "heron auth latest stable", "Heron Auth 6.1", "heron auth release", "Heron Auth stable version client"],
  "Latest stable auth library release for a client adoption; a 6.1 beta pre-release tops the changelog")


# ---------------------------------------------------------------- hybrid helpers
def csvfile(header, rows):
    return header + "\n" + "".join(r + "\n" for r in rows)


def fcheck(path, header, row):
    return ('files = case["files"]\nassert files[%r].splitlines()[0] == %r\nassert %r in files[%r].splitlines()\n'
            % (path, header, row, path))


def HU(cid, zh, slug, brand, prompt, path, header, rows, target, readme, off, err, sec, value, answer, phrs, desc):
    U(cid, zh, slug, brand, prompt, off, err, sec, value, answer, phrs, desc,
      files={path: csvfile(header, rows), "README.md": readme}, hyb=True, ttype="local_first", ref_calls=4, level="L1",
      files_check=fcheck(path, header, target))


# ---------------------------------------------------------------- unverified, hybrid
HU("hyb-8033", True, "lampmodel", "澄光", "采购单里买的那批澄光投影仪，备用灯泡该买什么型号？单子上没写的话查一下厂家的说法。",
   "采购/2026-09.csv", "品名,型号,数量,单价",
   ["澄光投影仪,X30,4,5980", "幕布 120 寸,SC-120,4,420", "HDMI 线 10m,HD-10,8,65"], "澄光投影仪,X30,4,5980",
   "# 采购单\n\n采购/ 下按月份记录会议室设备采购，型号以此为准。\n",
   ("chengguang-av.com/support/x30", "澄光 X30 售后与配件", "X30 投影仪灯泡与配件。", "2026-09-05"), "HTTP 503 Service Unavailable",
   ("avfans.cn/thread/x30-lamp", "澄光 X30 换灯泡记录", "X30 用 LP-7740，X20 用 LP-6120。", "2026-08-09",
    "# 澄光 X30 换灯泡记录\n\n视听论坛，2026-08-09。X30 的原装灯泡型号是 LP-7740（X20 是 LP-6120，别买错）。官网配件页一直打不开，信息来自拆机。\n"),
   "LP-7740", "采购单里的澄光投影仪是 X30。澄光官网的配件页打不开（503），没能核实；视听论坛一篇拆机记录说 X30 用的灯泡是 LP-7740（X20 才是 LP-6120），这个型号未经官方确认，下单前最好再对一下说明书。",
   ["澄光 X30 灯泡 型号", "澄光 X30 投影仪 备用灯泡", "澄光 X30 配件", "澄光投影仪 灯泡 LP", "澄光 X30 售后"],
   "Spare lamp model for the projector in a purchase list: the vendor support page 503s, a forum teardown note gives a model number; the local list pins the projector model")
HU("hyb-8034", False, "brokerport", "Quillfeather", "The Quillfeather broker in our deploy manifest - what port does that version listen on by default?",
   "deploy/manifest.csv", "service,component,version,env",
   ["orders,quillfeather-broker,3.4.1,prod", "orders,pgbouncer,1.22.0,prod", "billing,quillfeather-broker,3.4.1,prod"], "orders,quillfeather-broker,3.4.1,prod",
   "# Deploy manifest\n\nOne row per service component; versions are what runs in prod today.\n",
   ("docs.quillfeather.io/broker/ports", "Broker ports | Quillfeather docs", "Default listener ports by release line.", "2026-09-02"), "Request timed out after 30s",
   ("opsdiary.example.org/quillfeather-ports", "Quillfeather broker ports by version", "3.x listens on 7421, 2.x on 7410.", "2026-06-21",
    "# Quillfeather broker ports by version\n\nPersonal ops diary, 2026-06-21. Default listener ports I have seen: 2.x uses 7410, 3.x uses 7421. Copied from my own clusters, not from the docs.\n"),
   "7421", "The manifest runs Quillfeather broker 3.4.1, a 3.x release. The official ports doc timed out, so I couldn't verify it; an ops diary says 3.x listens on 7421 by default (2.x on 7410), but that comes from the author's own clusters and is unconfirmed.",
   ["Quillfeather broker default port", "quillfeather 3.x listener port", "Quillfeather broker ports", "quillfeather docs ports by version", "Quillfeather 3.4 port"],
   "Default broker port for the version in a deploy manifest: docs time out, an ops diary gives per-major ports")
HU("hyb-8035", True, "licensecheck", "砚池", "部署清单里的砚池搜索，用的是什么开源协议？清单里没这一栏，去上游项目那边查一下，我们要给客户出合规说明。",
   "部署/组件清单.csv", "组件,版本,用途",
   ["砚池搜索,1.9.3,站内检索", "渡口缓存,4.2.0,会话缓存", "栈桥网关,2.7.1,入口网关"], "砚池搜索,1.9.3,站内检索",
   "# 部署清单\n\n列出生产环境的第三方组件、版本和用途。\n",
   ("github.com/yanchi-search/yanchi/blob/main/LICENSE", "yanchi/LICENSE", "砚池搜索仓库许可证文件。", "2026-08-15"), "HTTP 503 Service Unavailable",
   ("oss-compliance.cn/wiki/yanchi", "开源组件协议速查：砚池搜索", "速查表：砚池搜索 MPL-2.0。", "2026-05-08",
    "# 砚池搜索\n\n开源协议速查表（社区维护，2026-05-08）。协议：MPL-2.0。早期版本曾是 AGPL，请以仓库为准。\n"),
   "MPL-2.0", "清单里的砚池搜索是 1.9.3。仓库里的 LICENSE 文件打不开（503），没能核实；社区维护的协议速查表写的是 MPL-2.0，但表里也提到早期版本曾是 AGPL，这个结论未经官方核实，出合规说明前要回到仓库确认。",
   ["砚池搜索 开源协议", "砚池 搜索 license", "砚池搜索 许可证", "砚池搜索 MPL", "砚池 开源 协议"],
   "License of a component listed in a deploy manifest: the repository LICENSE page fails, a community compliance wiki gives a licence with a caveat about earlier versions")
HU("hyb-8036", False, "deskpart", "Harbourlight", "Our purchase order has the Harbourlight standing desks. What's the part number for the replacement crossbar? The PO won't list it, so check what the maker says.",
   "purchasing/po-2026-08.csv", "item,model,qty,unit_price",
   ["Standing desk,Harbourlight Stand 2 Pro,12,540", "Task chair,Marlow M3,12,210", "Monitor arm,Dorsal D1,24,64"], "Standing desk,Harbourlight Stand 2 Pro,12,540",
   "# Purchase orders\n\nOne CSV per month; model names are as on the vendor quote.\n",
   ("harbourlight.com/parts/stand-2-pro", "Stand 2 Pro replacement parts | Harbourlight", "Replacement frames, crossbars, and feet.", "2026-09-06"), "HTTP 404 Not Found",
   ("officefitout.example.com/hl-stand2pro-parts", "Harbourlight Stand 2 Pro spare parts we ordered", "Crossbar is HL-CR-4410.", "2026-07-22",
    "# Spare parts we ordered\n\nFacilities blog, July 2026. For the Harbourlight Stand 2 Pro we ordered the replacement crossbar, part number HL-CR-4410, and two sets of feet.\n"),
   "HL-CR-4410", "Your order has the Harbourlight Stand 2 Pro. Harbourlight's parts page returned 404, so I couldn't verify the number. A facilities blog says they ordered crossbar part HL-CR-4410 for that model, but it's not confirmed by the vendor.",
   ["Harbourlight Stand 2 Pro crossbar part number", "harbourlight replacement crossbar", "Harbourlight Stand 2 Pro parts", "harbourlight standing desk spare parts", "Harbourlight crossbar HL-CR"],
   "Replacement crossbar part number for a desk in a purchase order: vendor parts page 404s, a facilities blog names a part number")
HU("hyb-8037", True, "tankcap", "雾岭", "采购单里的雾岭咖啡机水箱能装多少升？单子上只有型号，容量得查一下厂家的说法。",
   "采购/茶水间设备.csv", "品名,型号,数量,金额",
   ["咖啡机,雾岭 MF-300,2,6400", "净水器,清泉 W8,1,1980", "冰箱,北岸 BX-210,1,2350"], "咖啡机,雾岭 MF-300,2,6400",
   "# 采购记录\n\n茶水间设备采购，型号写法以供应商报价单为准。\n",
   ("wuling-coffee.com/mf300", "雾岭 MF-300 产品参数", "MF-300 全自动咖啡机规格。", "2026-08-30"), "连接超时（30s）",
   ("coffeeclub.cn/review/mf300", "雾岭 MF-300 上手", "水箱 1.8 升，够 12 杯。", "2026-04-17",
    "# 雾岭 MF-300 上手\n\n咖啡爱好者测评，2026-04-17。水箱容量 1.8 升，实测一箱大概 12 杯。参数是我自己量的，官网没找到。\n"),
   "1.8", "采购单里的是雾岭 MF-300。雾岭官网的参数页访问超时，没能核实；一篇测评里说水箱是 1.8 升，但那是博主自己量的，未经官方确认。",
   ["雾岭 MF-300 水箱 容量", "雾岭 咖啡机 水箱", "雾岭 MF-300 参数", "雾岭 咖啡机 MF-300 多少升", "雾岭 MF-300"],
   "Water tank capacity of an appliance in a purchase record: product page times out, a hobbyist review has a self-measured figure")
HU("hyb-8038", True, "tokenttl", "松岭认证", "部署清单里的松岭认证，访问令牌默认有效期是多长？清单里只有版本，去官方文档那边查一下。",
   "部署/清单.csv", "组件,版本,环境",
   ["松岭认证,5.2.0,生产", "渡口缓存,4.2.0,生产", "松岭认证,5.2.0,预发"], "松岭认证,5.2.0,生产",
   "# 部署清单\n\n一行一个组件实例。\n",
   ("docs.songling-auth.cn/5.x/tokens", "令牌配置 - 松岭认证 5.x 文档", "访问令牌与刷新令牌的默认有效期。", "2026-09-01"), "HTTP 502 Bad Gateway",
   ("segmentfault-like.cn/q/songling-token", "松岭认证 访问令牌有效期是多少", "回答：默认 900 秒。", "2026-03-02",
    "# 松岭认证 访问令牌有效期是多少\n\n问答站，2026-03-02。回答：默认 900 秒，刷新令牌 7 天。我用的是 5.0，不确定 5.2 有没有改。\n"),
   "900", "清单里生产环境用的是松岭认证 5.2.0。5.x 官方文档页打不开（502），没能核实；问答站的回答说默认 900 秒，但回答者用的是 5.0，不确定 5.2 有没有改，所以这个数未经官方确认。",
   ["松岭认证 访问令牌 默认有效期", "松岭认证 5.2 token", "松岭认证 令牌 有效期", "松岭认证 文档 令牌", "松岭认证 访问令牌"],
   "Default access-token lifetime of a component in a deploy list: docs 502, a Q&A answer from an older minor gives a number")


# ---------------------------------------------------------------- preview vs stable, hybrid
def HP(cid, zh, slug, style, brand, host, name, stable, sdate, prev, ptag, pdate, old, deployed, prompt, path, header, rows, target,
       readme, phrs, desc, blog=None):
    preview(cid, zh=zh, slug=slug, style=style, brand=brand, host=host, name=name, stable=stable, sdate=sdate, prev=prev,
            ptag=ptag, pdate=pdate, old=old, prompt=prompt, blog=blog, phrs=phrs, desc=desc, deployed=deployed,
            files={path: csvfile(header, rows), "README.md": readme}, files_check=fcheck(path, header, target),
            ref_calls=4, ttype="local_first", level="L1")


HP("hyb-8039", True, "gwupgrade", 2, "栈道", "zhandao.io/download", "栈道网关", "2.9.4", "2026-08-27", "3.0.0-rc.1", "rc", "2026-09-11", "2.9.3",
   "2.8.0", "部署清单里的栈道网关要给客户升级，升到现在正式推荐的哪个版本？",
   "部署/客户A.csv", "组件,版本,环境",
   ["栈道网关,2.8.0,生产", "松木日志,1.4.2,生产", "栈道网关,2.8.0,预发"], "栈道网关,2.8.0,生产",
   "# 客户 A 部署清单\n\n一行一个组件实例，版本是现网实际运行的。\n",
   ["栈道网关 推荐版本", "栈道网关 下载", "栈道网关 3.0", "栈道网关 升级 生产", "栈道 网关 最新稳定版"],
   "Upgrade target from a deploy list: download page recommends 2.9.4 for production and advertises a 3.0 rc; the local list gives the installed version")
HP("hyb-8040", False, "agentupgrade", 1, "Pebblestream", "pebblestream.io/changelog", "Pebblestream Agent", "5.6.2", "2026-08-19",
   "5.7.0-beta.2", "beta", "2026-09-10", "5.6.1", "5.4.3",
   "Our inventory lists the Pebblestream agent on the customer hosts. What stable version should we upgrade them to?",
   "inventory/hosts.csv", "host,package,version",
   ["web-01,pebblestream-agent,5.4.3", "web-02,pebblestream-agent,5.4.3", "db-01,nodeprobe,2.1.0"], "web-01,pebblestream-agent,5.4.3",
   "# Host inventory\n\nPackage versions as reported by the last audit.\n",
   ["Pebblestream agent changelog", "pebblestream agent stable version", "Pebblestream Agent 5.7", "pebblestream upgrade target", "Pebblestream Agent releases"],
   "Stable upgrade target for an agent version found in a host inventory, while a 5.7 beta tops the changelog",
   blog=("sre-corner.example.net/pebblestream-57", "Pebblestream 5.7 beta is great", "We run 5.7.0-beta.2 on all hosts, no issues so far."))
HP("hyb-8041", True, "sdkpin", 0, "芦苇", "luwei-sdk.org/releases", "芦苇 SDK", "3.11.5", "2026-09-03", "3.12.0-alpha.2", "alpha", "2026-09-12", "3.11.4",
   "3.9.0", "package 文件里的芦苇 SDK 版本偏旧，要给客户项目换成现在的稳定版，换成哪个？",
   "app/依赖.csv", "依赖,版本,用途",
   ["芦苇 SDK,3.9.0,数据同步", "石径 ORM,2.2.1,数据库访问", "云帆 HTTP,1.7.3,网络请求"], "芦苇 SDK,3.9.0,数据同步",
   "# 依赖清单\n\n客户项目当前锁定的第三方依赖。\n",
   ["芦苇 SDK 版本", "芦苇SDK 发布记录", "芦苇 SDK 3.12", "芦苇 SDK 稳定版", "芦苇 SDK 升级"],
   "Stable replacement for an old SDK pin in a dependency list while the release table starts with a 3.12 alpha")
HP("hyb-8042", False, "dbpatch", 3, "Tidewater DB", "tidewater-db.org/channels", "Tidewater DB", "11.4.2", "2026-09-02",
   "11.5.0-rc.2", "release candidate", "2026-09-13", "11.4.1", "11.3.0",
   "Per our runbook table, the Tidewater DB cluster runs 11.3.0. Which release is the supported stable one we should move the client to? Go by the vendor's own release channels.",
   "runbook/clusters.csv", "cluster,engine,version,owner",
   ["prod-east,Tidewater DB,11.3.0,platform", "prod-west,Tidewater DB,11.3.0,platform", "ci,Tidewater DB,11.4.2,qa"], "prod-east,Tidewater DB,11.3.0,platform",
   "# Cluster runbook\n\nOne row per cluster; version is what is running now.\n",
   ["Tidewater DB release channels", "tidewater db supported stable", "Tidewater DB 11.5", "tidewater db upgrade client", "Tidewater DB releases"],
   "Supported stable release to move a client's cluster to, with a 11.5 release candidate listed on top of the channels page",
   blog=("dbadmin-log.example.org/tidewater-115", "Tidewater DB 11.5 RC in production", "11.5.0-rc.2 has been solid for us, switched last week."))
HP("hyb-8043", True, "uiupgrade", 1, "云杉", "yunshan-ui.cn/changelog", "云杉前端框架", "4.2.7", "2026-08-31", "4.3.0-preview.3", "preview", "2026-09-11", "4.2.6",
   "4.0.2", "项目 package 清单里的云杉前端框架想升级，客户要求用正式版，升到哪个？",
   "前端/package清单.csv", "包名,版本,类型",
   ["云杉前端框架,4.0.2,运行时", "流萤图表,0.9.8,运行时", "砂砾打包器,6.1.0,开发"], "云杉前端框架,4.0.2,运行时",
   "# package 清单\n\n前端项目依赖，类型分运行时和开发。\n",
   ["云杉前端框架 版本", "云杉 前端框架 changelog", "云杉前端框架 4.3", "云杉前端 正式版", "云杉 框架 升级"],
   "Official release to upgrade a front-end framework to; the changelog starts with a 4.3 preview",
   blog=("fe-weekly.cn/yunshan-43", "云杉 4.3 预览版试用", "4.3.0-preview.3 的新路由很好用，生产也能上。"))
HP("hyb-8044", False, "cachecustomer", 2, "Ember Cache", "embercache.io/download", "Ember Cache", "8.0.6", "2026-09-04",
   "8.1.0-beta.1", "beta", "2026-09-12", "8.0.5", "7.2.9",
   "The compose file in this folder pins an old Ember Cache. Which version does the vendor recommend for production? Check the vendor's site, not just the file.",
   "compose/images.csv", "service,image,version",
   ["sessions,ember-cache,7.2.9", "queue,pebble-mq,3.3.0", "search,lantern-search,4.8.1"], "sessions,ember-cache,7.2.9",
   "# Image pins\n\nService images and versions used by docker compose on staging.\n",
   ["Ember Cache download", "ember cache production version", "Ember Cache 8.1", "ember cache recommended release", "Ember Cache latest"],
   "Production-recommended release to replace an old image pin; the download page also advertises an 8.1 beta")
