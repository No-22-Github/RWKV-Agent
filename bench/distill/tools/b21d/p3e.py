"""31421-31430: controls, the answer is an outside, time-sensitive fact and the fixture search has it."""
from p3 import ext, reg, fx


@reg
def c31421():
    web = [fx("zentro", "https://zentro.example/releases", "Zentro releases", "Zentro 6.4.2 is the current stable release, published 2026-09-10.\n", "2026-09-10")]
    ext("web-31421", files={"notes/todo.md": "# 待办\n- 周五前提交预算\n"}, q="Zentro 现在的稳定版是多少？", web=web, ans="6.4.2", localval=None,
        desc="Asks the current stable version of an outside tool; fixture has it, workspace is unrelated", ref="web_search zentro -> 6.4.2。")


@reg
def c31422():
    web = [fx("quillbase", "https://docs.quillbase.example/pricing", "Quillbase pricing", "Quillbase Team plan costs 18 USD per seat per month as of September 2026.\n", "2026-09-05")]
    ext("web-31422", files={"README.md": "# 采购笔记\n"}, q="Quillbase 团队版每个席位每月多少美元？", web=web, ans="18 USD", localval=None,
        desc="Asks a vendor's current seat price; only the web fixture has it", ref="搜索得 18 USD / seat / month。")


@reg
def c31423():
    web = [fx("northwind ferry", "https://northwind-ferry.example/timetable", "Northwind Ferry timetable", "From 2026-09-14 the last ferry departs at 21:40 on weekdays.\n", "2026-09-12")]
    ext("web-31423", files={"travel/ferry-note.md": "# 渡轮笔记（2025 年夏）\n末班船 20:30。\n"}, q="Northwind 渡轮现在工作日末班是几点？", web=web, ans="21:40", localval="20:30", trap="TR-DECOY",
        desc="Asks the weekday last ferry time; the workspace note is from last summer and differs", ref="web_search 得 21:40；本地 2025 笔记的 20:30 已过时。")


@reg
def c31424():
    web = [fx("mapleforge", "https://mapleforge.example/security", "MapleForge security bulletin", "MapleForge 3.9.1 fixes CVE-2026-4417; all users should upgrade to 3.9.1.\n", "2026-09-11")]
    ext("web-31424", files={"deps/pins.txt": "mapleforge==3.8.0\n", "deps/notes.md": "# 依赖笔记\n3.8.0 是当时的推荐版本。\n"}, q="Which MapleForge version fixes the newest security issue?", web=web, ans="3.9.1", localval="3.8.0", trap="TR-DECOY",
        desc="Asks which version fixes the security issue; the pinned local version is older", ref="web_search 得 3.9.1；pins.txt 的 3.8.0 只是当前锁定版本。")


@reg
def c31425():
    web = [fx("海河电力 电价", "https://haihe-power.example/tariff", "海河电力居民电价", "海河电力 2026 年 9 月起居民阶梯电价第一档为 0.57 元/度。\n", "2026-09-02")]
    ext("web-31425", files={"home/账单笔记.md": "# 账单笔记\n去年电价：0.52 元/度。\n"}, q="海河电力现在居民第一档电价是多少？", web=web, ans="0.57", localval="0.52", trap="TR-DECOY",
        desc="Asks the current first-tier residential electricity price; a local note records last year's price", ref="web_search 得 0.57 元/度，不用去年的 0.52。")


@reg
def c31426():
    web = [fx("skylark airlines baggage", "https://skylark.example/baggage", "Skylark baggage rules", "Skylark Airlines allows a 23 kg checked bag on economy fares since 2026-08-01.\n", "2026-08-01")]
    ext("web-31426", files={"trips/packing.md": "# Packing\nCarry-on only this time.\n"}, q="How heavy can my checked bag be on Skylark Airlines economy?", web=web, ans="23 kg", localval=None,
        desc="Asks an airline's checked bag weight limit; the fixture has it", ref="web_search 得 23 kg。")


@reg
def c31427():
    web = [fx("fernlang", "https://fernlang.example/news", "Fernlang 2.0 release", "Fernlang 2.0 was released on 2026-09-08 and drops support for Python 3.8 style imports.\n", "2026-09-08")]
    ext("web-31427", files={"proj/NOTES.md": "# Notes\nFernlang 1.9 is what we use; 2.0 is not out yet.\n"}, q="Fernlang 2.0 出了吗，是哪天发布的？", web=web, ans="2026-09-08", localval=None, trap="TR-DECOY", decoy="2.0 is not out yet",
        desc="Asks whether a tool's 2.0 is out and when; a local note says it is not out yet", ref="web_search 得 2026-09-08 已发布；本地笔记过时。")


@reg
def c31428():
    web = [fx("东岸物流 运费", "https://dongan-express.example/rates", "东岸物流运费表", "东岸物流同城件 1 公斤以内 12 元，2026-09-01 起生效。\n", "2026-09-01")]
    ext("web-31428", files={"ops/物流.md": "# 物流\n同城件 10 元（旧价）。\n"}, q="东岸物流同城 1 公斤以内现在收多少钱？", web=web, ans="12 元", localval="10 元", trap="TR-DECOY",
        desc="Asks the current same-city rate of a courier; the local note has an old price", ref="web_search 得 12 元，旧笔记的 10 元作废。")


@reg
def c31429():
    web = [fx("lumen camera firmware", "https://lumen.example/support/firmware", "Lumen firmware", "Lumen X2 firmware 1.8.5 adds night mode and fixes the Wi-Fi drop bug.\n", "2026-09-09")]
    ext("web-31429", files={"gear/lumen.md": "# Lumen X2\nFirmware installed: 1.7.0\n"}, q="What's the current Lumen X2 firmware, and what does it fix?", web=web, ans="1.8.5", localval=None,
        desc="Asks the current camera firmware version and its fixes; the workspace only records the installed one", ref="web_search 得 1.8.5，修复 Wi-Fi 掉线。")


@reg
def c31430():
    web = [fx("云麓 体育馆 开放时间", "https://yunlu-gym.example/hours", "云麓体育馆开放时间", "云麓体育馆自 2026-09-15 起周末开放时间调整为 8:00-22:00。\n", "2026-09-14")]
    ext("web-31430", files={"life/健身.md": "# 健身\n云麓体育馆周末 9:00-20:00（老时间）。\n"}, q="云麓体育馆周末现在几点开门到几点关门？", web=web, ans="8:00-22:00", localval="9:00-20:00", trap="TR-DECOY",
        desc="Asks the gym's current weekend hours; the local note lists the old hours", ref="web_search 得 8:00-22:00。")
