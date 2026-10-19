"""34054-34065 A2 (part 2)."""
from kit import *


def build():
    a2("web-34054", "lookup_value", "Ashgrove Dental", "None of Ashgrove Dental's info is on my machine. What are their Saturday opening hours? Check the web please.",
       {"admin/todo.txt": "renew parking permit\n"},
       [("https://ashgrove-dental.example/contact", "Contact & hours - Ashgrove Dental", "2026-09-03", "Opening hours and booking.", "# Contact & hours\n\nMon-Fri 8:00-17:30. Saturday 9:00-13:00. Closed Sunday.\n")],
       val="13:00")
    a2("hyb-34055", "local_first", "朔风航空", "朔风航空托运行李现在最多能带多少公斤？我没存过它的规定，网上查吧。",
       {"出差/机票.txt": "周四 08:45\n"},
       [("https://shuofeng-air.example/baggage", "行李规定 - 朔风航空", "2026-09-10", "托运与手提行李规定。", "# 行李规定\n\n经济舱托运额度 20 公斤；手提 7 公斤。超重每公斤收 30 元。\n")],
       val="20 公斤", p2="超重怎么收费？", val2="30 元")
    a2("web-34056", "latest_version", "Plumeria SDK", "I have no Plumeria SDK files here at all. Search online for its current stable version.",
       {"scratch/sdk-eval-greeting.txt": "hello\n"},
       [("https://plumeria-sdk.example/changelog", "Changelog - Plumeria SDK", "2026-09-11", "Plumeria SDK changelog.", "# Changelog\n\n## 12.3.1 (stable, 2026-09-11)\n## 12.4.0-rc.1 (pre-release)\n## 12.3.0 (2026-08-20)\n")],
       val="12.3.1")
    a2("web-34057", "deprecation", "夜航船", "夜航船这个服务是不是要停了？我这里没有它的公告，帮我上网搜一下，停服时间也要。",
       {"备忘.txt": "周一发周报\n"},
       [("https://yehangchuan.example/notice/sunset", "服务调整公告 - 夜航船", "2026-09-12", "夜航船停止运营安排。", "# 服务调整公告\n\n夜航船将于 2026 年 12 月 31 日停止运营，用户可在此前导出数据。\n")],
       dany=dates("2026-12-31"))
    a2("hyb-34058", "local_first", "Skerry Ferries", "Can you find out on the web how much a car costs on Skerry Ferries? I wrote nothing about them in my notes.",
       {"trip/ferry-packing-list.txt": "pack rain gear\n"},
       [("https://skerry-ferries.example/fares", "Fares - Skerry Ferries", "2026-09-06", "Car and passenger fares.", "# Fares\n\nCar and driver: 46 pounds one way.\nFoot passenger: 9 pounds.\n")],
       val="46", p2="and a foot passenger?", val2="9 pounds")
    a2("web-34059", "lookup_value", "麦穗超市", "麦穗超市的会员日是每月几号？这个我没记过，去网上看看。",
       {"采购/清单.txt": "牛奶\n鸡蛋\n"},
       [("https://maisui-mart.example/member-day", "会员日 - 麦穗超市", "2026-09-01", "会员日活动说明。", "# 会员日\n\n每月 8 日、18 日、28 日为会员日，全场 95 折。\n")],
       val="18")
    a2("web-34060", "error_meaning", "Quillon Proxy", "Quillon Proxy logs show 'tunnel reset 52'. I have no docs for it here; search the web for what that means.",
       {"logs/old.log": "started\n"},
       [("https://quillon-proxy.example/kb/tunnel-reset-52", "tunnel reset 52 - Quillon Proxy KB", "2026-06-18", "Explains reset reason 52.", "# tunnel reset 52\n\nReset reason 52 means the peer idle timeout (300 s) was reached. Increase keepalive or the idle timeout.\n")],
       dany=["idle", "Idle", "timeout", "Timeout", "空闲", "超时"])
    a2("hyb-34061", "local_first", "岩松考试中心", "岩松考试中心下一次计算机等级考试什么时候报名截止？我手头没有简章，帮我上网找。",
       {"学习/复习.txt": "刷真题\n"},
       [("https://yansong-exam.example/notice/autumn", "秋季考试报名公告 - 岩松考试中心", "2026-09-08", "秋季场报名时间。", "# 秋季考试报名公告\n\n报名时间：2026 年 9 月 15 日至 9 月 28 日，考试日期 11 月 14 日。\n")],
       dany=dates("2026-09-28"), p2="考试是哪天？", dany2=dates("2026-11-14"))
    a2("web-34062", "latest_version", "Orchard Notes", "My folder doesn't mention Orchard Notes anywhere. Can you check its site for the latest macOS version number?",
       {"misc/notes-folder-index.txt": "notes folder\n"},
       [("https://orchard-notes.example/mac", "macOS - Orchard Notes", "2026-09-14", "Orchard Notes for macOS.", "# macOS\n\nCurrent version: 3.21.0 (requires macOS 13+).\nPrevious: 3.20.4.\n")],
       val="3.21.0", p2="What macOS does it need?", val2="macOS 13", req2=())
    a2("web-34063", "lookup_value", "燕麦咖啡馆", "燕麦咖啡馆有没有学生折扣？我这里没存它们的菜单，帮我查查网上的信息。",
       {"生活/记账.txt": "咖啡 22\n"},
       [("https://yanmai-cafe.example/promo", "优惠活动 - 燕麦咖啡馆", "2026-09-02", "咖啡馆优惠。", "# 优惠活动\n\n出示学生证饮品 8 折（每日 14:00 前不适用）。\n第二杯半价仅限周三。\n")],
       dany=["8 折","8折","八折"])
    a2("hyb-34064", "local_first", "Wicker & Finch", "Wicker & Finch's return window — I never saved their policy. Look it up for me, how many days do I have?",
       {"shopping/receipts.txt": "Wicker & Finch lamp 59.00\n"},
       [("https://wickerandfinch.example/returns", "Returns - Wicker & Finch", "2026-08-28", "Returns policy.", "# Returns\n\nItems can be returned within 45 days of delivery if unused. Sale items: 14 days.\n")],
       val="45", p2="and what about sale items?", val2="14 days", req2=())
    a2("web-34065", "lookup_value", "霜降驾考", "霜降驾考预约平台的科目二考试费现在多少钱？这方面的资料我一点没存，直接搜。",
       {"杂/清单.txt": "体检表\n"},
       [("https://shuangjiang-drive.example/fees", "收费标准 - 霜降驾考", "2026-09-09", "考试费用标准。", "# 收费标准\n\n科目二考试费 150 元；补考每次 100 元。\n")],
       val="150")
