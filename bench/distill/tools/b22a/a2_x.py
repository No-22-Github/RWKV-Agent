"""34041-34053 A2: the prompt already says there is nothing local -> web first."""
from kit import *


def build():
    a2("web-34041", "lookup_value", "银杏健身", "我这边没存银杏健身的任何资料，你直接上网帮我查查它的私教课一节多少钱。",
       {"memo.txt": "周三例会改到下午\n"},
       [("https://yinxing-gym.example/coach", "私教课程 - 银杏健身", "2026-09-06", "私教课程价格。", "# 私教课程\n\n单节 260 元；10 节卡 2200 元；20 节卡 4000 元。\n")],
       val="260")
    a2("web-34042", "latest_version", "Foxglove Bundler", "Nothing about Foxglove Bundler is in my workspace. Look it up online: what's the current stable version?",
       {"build-cleanup-checklist.md": "- clean up the build folder\n"},
       [("https://foxglove-bundler.example/releases", "Releases - Foxglove Bundler", "2026-09-09", "Foxglove Bundler releases.", "# Releases\n\nStable: 4.12.0 (2026-09-09)\nBeta: 4.13.0-beta.1\n")],
       val="4.12.0")
    a2("hyb-34043", "local_first", "鹭岛渡轮", "鹭岛渡轮周日最后一班船是几点？这个我文件夹里肯定没有，去网上找吧。",
       {"出行/清单.txt": "防晒霜\n相机\n"},
       [("https://ludao-ferry.example/timetable", "时刻表 - 鹭岛渡轮", "2026-09-04", "渡轮时刻表。", "# 时刻表\n\n每日首班 7:00。周日末班 18:40，其余日末班 20:10。\n")],
       val="18:40", p2="那周一呢？", val2="20:10")
    a2("web-34044", "deprecation", "Tinderbox Cache", "I don't keep any docs on Tinderbox Cache. Can you search the web and tell me when version 5 reaches end of life?",
       {"notes/misc.txt": "buy coffee filters\n"},
       [("https://tinderbox-cache.example/eol", "End-of-life dates - Tinderbox Cache", "2026-08-12", "Version support windows.", "# End-of-life dates\n\nTinderbox Cache 5: end of life 2027-06-30.\nTinderbox Cache 6: supported until at least 2028.\n")],
       dany=dates("2027-06-30"))
    a2("hyb-34045", "local_first", "雾岭温泉", "帮我查一下雾岭温泉现在的门票，我没有它的任何资料。",
       {"周末/想去的地方.txt": "海边\n"},
       [("https://wuling-spring.example/ticket", "门票 - 雾岭温泉", "2026-09-10", "雾岭温泉门票价格。", "# 门票\n\n成人 158 元，儿童 88 元，夜场 118 元。\n")],
       val="158", p2="夜场呢？", val2="118")
    a2("web-34046", "lookup_value", "Sandpiper Telecom", "Look online: what's the data roaming daily pass price at Sandpiper Telecom? My workspace has nothing on them.",
       {"travel/packing.txt": "adapter\npassport\n"},
       [("https://sandpiper-telecom.example/roaming", "Roaming passes - Sandpiper Telecom", "2026-09-07", "Roaming day pass prices.", "# Roaming passes\n\nDaily pass: 8 dollars per 24 hours (500 MB). Weekly pass: 35 dollars.\n")],
       val="8")
    a2("web-34047", "error_meaning", "珊瑚数据库", "珊瑚数据库报了 E2207，我这里没有任何文档，上网查一下是什么意思。",
       {"测试环境说明-珊瑚库.txt": "测试环境\n"},
       [("https://shanhu-db.example/docs/E2207", "E2207 - 珊瑚数据库", "2026-07-02", "E2207 错误说明。", "# E2207\n\n表空间已满。请扩容数据文件或清理过期分区。\n")],
       val="表空间")
    a2("hyb-34048", "local_first", "Merrow Courier", "I haven't saved the shipping rates anywhere. Can you find out online what Merrow Courier charges for a 2 kg parcel within the country?",
       {"shop/orders.csv": "id,item\n1,mug\n"},
       [("https://merrow-courier.example/rates", "Domestic rates - Merrow Courier", "2026-09-02", "Domestic parcel rates.", "# Domestic rates\n\nUp to 1 kg: 5.20 dollars\n1-3 kg: 7.80 dollars\n3-10 kg: 12.50 dollars\n")],
       val="7.80", p2="and for 5 kg?", val2="12.50")
    a2("web-34049", "lookup_value", "橙子打印", "查一下橙子打印店 A3 彩打一张多少钱，我文件夹里没有这家的价格表。",
       {"杂项/记事.txt": "周五交报告\n"},
       [("https://chengzi-print.example/price", "价格表 - 橙子打印", "2026-09-05", "打印价格。", "# 价格表\n\nA4 黑白 0.3 元/张；A4 彩色 1.5 元/张；A3 彩色 4 元/张。\n")],
       val="4")
    a2("web-34050", "latest_version", "Glassfern Editor", "Can you check the Glassfern Editor website for the newest release? I've never written anything about it down.",
       {"readme.md": "# scratch\n"},
       [("https://glassfern-editor.example/download", "Download - Glassfern Editor", "2026-09-15", "Download Glassfern Editor.", "# Download\n\nGlassfern Editor 0.88.1 (2026-09-15) - stable. Since 0.87: new plugin API.\nInsiders build: 0.89.0-insiders.\n")],
       val="0.88.1", p2="what changed from 0.87?", val2="plugin", req2=())
    a2("hyb-34051", "local_first", "涵碧湖游船", "涵碧湖游船现在一圈多少钱，网上应该有，我本地没记。", 
       {"计划/国庆.md": "去杭州附近转转\n"},
       [("https://hanbihu-boat.example/price", "游船票价 - 涵碧湖", "2026-09-08", "涵碧湖游船价格。", "# 游船票价\n\n环湖一圈（约 40 分钟）：成人 60 元，儿童 30 元。包船 480 元/小时。\n")],
       val="60 元", p2="包船呢？", val2="480")
    a2("web-34052", "deprecation", "Lintel Forms", "Please search the web about Lintel Forms - I've got no notes on it - and tell me if the free plan is being discontinued.",
       {"vendor-callback-reminder.txt": "call vendor Monday\n"},
       [("https://lintel-forms.example/blog/free-plan", "Changes to the free plan - Lintel Forms", "2026-09-01", "Free plan update.", "# Changes to the free plan\n\nThe free plan is being retired on 1 December 2026. Existing forms stay readable for 90 days.\n")],
       dany=dates("2026-12-01"))
    a2("web-34053", "lookup_value", "知更鸟课堂", "知更鸟课堂的少儿编程班，一期课多少钱？这类资料我这边没有，上网看看。",
       {"孩子/兴趣班.txt": "周六画画\n"},
       [("https://zhigengniao-class.example/coding", "少儿编程班 - 知更鸟课堂", "2026-09-09", "少儿编程班课程与价格。", "# 少儿编程班\n\n一期 12 节课，2160 元；试听一节 39 元。\n")],
       val="2160")
