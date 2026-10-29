"""b23d D1 part a: 3-turn chains, ids 35201-35212."""
from common import mk, T, L, READ, WRITE

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c01():
    files = {"config/harborview-gateway.toml": L("[gateway]", 'name = "harborview"', "connect_timeout_s = 4", "read_timeout_s = 30", "max_retries = 2")}
    mk("hyb-35201", sub="D1", tt="multi", trap="TR-CLAIM", desc="Read two timeouts, double one, then recap every change with the old values", files=files,
       turns=[T("What are the connect and read timeouts in config/harborview-gateway.toml?", inc=["4", "30"]),
              T("Double the read timeout, and tell me the new value.", inc=["60"]),
              T("Now set max_retries to 5. Then give me a short recap of every change made today, with the value each setting had before.", inc=["30", "60", "2", "5"])],
       edits=[("config/harborview-gateway.toml", "read_timeout_s = 30", "read_timeout_s = 60"), ("config/harborview-gateway.toml", "max_retries = 2", "max_retries = 5")],
       must=["read_file", "replace_lines", "write_file"], rc=5, notes="read, replace_lines read_timeout, replace_lines max_retries; recap uses 30 from turn 1")


@reg
def c02():
    f = "配置/凯旋仓储-限流.ini"
    files = {f: L("[limits]", "rate_per_min = 120", "burst = 30", "whitelist_rate = 500")}
    mk("hyb-35202", sub="D1", tt="multi", trap="TR-CLAIM", desc="Chinese: read limits, change one, derive another from the pre-change value", files=files,
       turns=[T("看一下 配置/凯旋仓储-限流.ini，现在每分钟限流多少、突发上限多少？", inc=["120", "30"]),
              T("把每分钟限流调到 200，突发上限别动。", inc=["200"]),
              T("再把白名单限流改成调整前每分钟限流的 5 倍，最后说说今天一共改了哪几项、各从多少变成多少。", inc=["120", "200", "500", "600"])],
       edits=[(f, "rate_per_min = 120", "rate_per_min = 200"), (f, "whitelist_rate = 500", "whitelist_rate = 600")],
       must=["read_file", "replace_lines", "write_file"], rc=5, notes="5x the ORIGINAL 120 = 600 (not 5x200)")


@reg
def c03():
    s, p = "config/ledger-sync/staging.yaml", "config/ledger-sync/prod.yaml"
    files = {s: L("service: ledger-sync", "batch_size: 250", "flush_ms: 800"), p: L("service: ledger-sync", "batch_size: 1000", "flush_ms: 400")}
    mk("hyb-35203", sub="D1", tt="undo", trap="TR-CLAIM", desc="Edit staging, user corrects to prod: staging must be restored and prod changed", files=files,
       turns=[T("In config/ledger-sync/staging.yaml, what is batch_size?", inc=["250"]),
              T("Set it to 500.", inc=["500"]),
              T("Sorry, I meant the prod one, not staging. Put staging back the way it was and make the change in prod instead. Tell me the old values you restored or replaced.", inc=["250", "1000"])],
       edits=[(p, "batch_size: 1000", "batch_size: 500")], must=["read_file", "replace_lines", "write_file"], rc=6,
       notes="read staging, set 500, then restore staging to 250 and set prod 1000->500")


@reg
def c04():
    f = "文档/社区团购-价目.md"
    files = {f: L("| 品名 | 单价 | 单位 |", "| --- | --- | --- |", "| 土鸡蛋 | 18 | 盒 |", "| 五常大米 | 56 | 袋 |", "| 山茶油 | 128 | 瓶 |")}
    mk("hyb-35204", sub="D1", tt="multi", trap="TR-CLAIM", desc="Chinese price list: read a price, raise it 10 percent, lower another, recap old and new", files=files,
       turns=[T("社区团购-价目里五常大米现在多少钱一袋？文件在 文档 文件夹里。", inc=["56"]),
              T("涨价 10%，改完告诉我新价格。", inc=["61.6"]),
              T("再把山茶油降 8 块。最后告诉我这两样今天各改了多少，改之前分别是多少。", inc=["56", "61.6", "128", "120"])],
       edits=[(f, "| 五常大米 | 56 | 袋 |", "| 五常大米 | 61.6 | 袋 |"), (f, "| 山茶油 | 128 | 瓶 |", "| 山茶油 | 120 | 瓶 |")],
       must=["read_file", "replace_lines", "write_file", "calculator"], rc=5)


@reg
def c05():
    f = "oncall/2026-q4-rota.txt"
    files = {f: L("Week 44: Priya Nair", "Week 45: Tomasz Wrona", "Week 46: Dana Whitfield", "Week 47: Lena Okafor", "Week 48: Marcus Hale")}
    mk("hyb-35205", sub="D1", tt="multi", trap="TR-CLAIM", desc="Swap two on-call weeks and then ask who was originally on week 45", files=files,
       turns=[T("Who is on call in week 45 according to oncall/2026-q4-rota.txt?", inc=["Tomasz Wrona"]),
              T("Tomasz is out sick that week. Swap him with whoever has week 47 and tell me the two names affected.", inc=["Lena Okafor", "Tomasz Wrona"]),
              T("Now who covers week 45 and who covers week 47? And remind me who was originally on week 45.", inc=["Lena Okafor", "Tomasz Wrona"])],
       edits=[(f, "Week 45: Tomasz Wrona", "Week 45: Lena Okafor"), (f, "Week 47: Lena Okafor", "Week 47: Tomasz Wrona")],
       must=["read_file", "replace_lines", "write_file"], rc=4)


@reg
def c06():
    log = "日志/打包线-0928.log"
    files = {log: L("08:02 INFO 开机自检通过", "08:41 WARN 封箱机温度 72", "09:15 ERROR 贴标机卡纸 工位3", "10:30 INFO 贴标机恢复", "11:05 ERROR 传送带过载 工位1")}
    out = "日志/故障摘要-0928.md"
    mk("hyb-35206", sub="D1", tt="write", trap="TR-CLAIM", desc="Chinese: count errors, write a summary file, fix one entry, ask for the first fault", files=files,
       turns=[T("日志/打包线-0928.log 里一共有几条 ERROR？分别是什么时候？", inc=["09:15", "11:05"], any=["2", "两", "二"]),
              T("把这几条 ERROR 的时间和工位整理成一个文件 日志/故障摘要-0928.md，一行一条。", req=["write_file"]),
              T("11:05 那条的工位我看错了，应该是工位2，请在摘要里改过来。再告诉我，今天第一次出故障是几点、在哪个工位。", inc=["09:15", "工位3"])],
       writes={out: ["09:15", "工位3", "11:05", "工位2"]}, must=["read_file", "write_file", "replace_lines"], rc=4)


@reg
def c07():
    f = "pkg/lumen-agent/Cargo.toml"
    files = {f: L("[package]", 'name = "lumen-agent"', 'version = "0.8.3"', 'edition = "2021"')}
    mk("hyb-35207", sub="D1", tt="undo", trap="TR-CLAIM", desc="Patch bump replaced by minor bump after user changes mind", files=files,
       turns=[T("What version is lumen-agent at, per its Cargo.toml in pkg/lumen-agent?", inc=["0.8.3"]),
              T("Bump the patch number and tell me the new version.", inc=["0.8.4"]),
              T("Actually this is a feature release, so make it the next minor instead (patch back to 0). Then list the three versions we've talked about.", inc=["0.8.3", "0.8.4", "0.9.0"])],
       edits=[(f, 'version = "0.8.3"', 'version = "0.9.0"')], vals=["0.8.4"], must=["read_file", "replace_lines", "write_file"], rc=5)


@reg
def c08():
    f = "文档/春游预算.md"
    files = {f: L("- 大巴：2400", "- 午餐：1800", "- 门票：1500", "- 保险：300")}
    mk("hyb-35208", sub="D1", tt="comp", trap="TR-CLAIM", desc="Chinese budget: total, raise one item, then cut another to stay under a cap", files=files,
       turns=[T("文档/春游预算.md 里的总预算是多少？", any=["6000", "6,000"]),
              T("门票改成 1650，其他不变，再告诉我新总额。", any=["6150", "6,150"]),
              T("老板说总额不能超过 6000，把午餐压缩来补，改好后告诉我午餐的新金额，以及它原来是多少。", inc=["1650", "1800"])],
       edits=[(f, "- 门票：1500", "- 门票：1650"), (f, "- 午餐：1800", "- 午餐：1650")],
       must=["read_file", "replace_lines", "write_file", "calculator"], rc=5, notes="6150-6000=150 over; lunch 1800->1650",
       dep="old lunch value 1800 is in the fixture")


@reg
def c09():
    f = "data/q3-regional-bookings.csv"
    files = {"reports/q2-highlights.txt": L("North: 401", "South: 372", "East: 466", "West: 310"), f: L("region,bookings,churned", "North,420,31", "South,388,45", "East,512,28", "West,297,52")}
    mk("hyb-35209", sub="D1", tt="write", trap="TR-CLAIM", desc="Find the top region, write a report file, add a gap line derived from turn-1 facts", files=files,
       turns=[T("Which region had the most bookings in data/q3-regional-bookings.csv, and how many?", inc=["East", "512"]),
              T("Create reports/q3-highlights.txt with one line per region in the form 'Region: bookings'.", req=["write_file"]),
              T("Add one last line starting with 'Gap:' with the bookings gap between the top region and the region with the highest churn. Tell me that number.", inc=["215"])],
       writes={"reports/q3-highlights.txt": ["North: 420", "South: 388", "East: 512", "West: 297", "Gap: 215"]},
       must=["read_file", "write_file", "append_file", "calculator"], rc=5, vals=["215"], dep="512 (top, turn 1) minus 297 (West, top churn 52) = 215")


@reg
def c10():
    f = "清单/办公室补货.txt"
    files = {f: L("打印纸 x5", "墨盒 x2", "订书钉 x6", "便签 x10")}
    mk("hyb-35210", sub="D1", tt="undo", trap="TR-CLAIM", desc="Staged append is rejected by the user, then redone with two lines; ask about the first attempt", files=files,
       turns=[T("在 清单/办公室补货.txt 最后加一行“白板笔 x10”。"),
              T("我拒绝了刚才那次改动，没有保存。现在清单里一共有几项？", inc=["4"], review="reject"),
              T("那就把“白板笔 x10”和“电池 x8”两行都加上，然后告诉我现在一共几项，以及你第一次想加的是哪一项。", inc=["6", "白板笔"])],
       adds=[(f, "白板笔 x10\n电池 x8\n")], loose=[f], must=["read_file", "append_file", "write_file"], rc=6)


@reg
def c11():
    f = "conf/orbit-collector.ini"
    files = {f: L("[collector]", "port = 9410", "", "[logging]", "level = info", "file = /var/log/orbit.log")}
    mk("hyb-35211", sub="D1", tt="multi", trap="TR-CLAIM", desc="Append a key, user accepts, then edit another key and describe before and after", files=files,
       turns=[T("Add a line 'retention_days = 45' at the end of the [logging] section in conf/orbit-collector.ini."),
              T("I accepted that. Now read the file again and tell me the retention setting and the other keys under [logging].", inc=["45", "level", "file"], review="accept"),
              T("Change level from info to warn. Then describe in one sentence what the [logging] section looked like at the very beginning versus now.", inc=["warn", "info", "45"])],
       edits=[(f, "level = info", "level = warn")], adds=[(f, "retention_days = 45\n")], must=["read_file", "replace_lines", "append_file", "write_file"], rc=6)


@reg
def c12():
    a, b, out = "名单/A组.txt", "名单/B组.txt", "名单/春季参赛名单.txt"
    files = {a: L("周明", "刘芳", "赵志强", "孙晓雯"), b: L("陈思远", "吴浩", "郑雅琪")}
    mk("hyb-35212", sub="D1", tt="write", trap="TR-CLAIM", desc="Merge two name lists into a new file, then drop one name and ask for the original size of group A", files=files,
       turns=[T("名单/A组.txt 里有几个人？", inc=["4"]),
              T("把A组和B组合在一起，先A组后B组，每人一行、不要空行，写到 名单/春季参赛名单.txt。"),
              T("B组的陈思远退赛了，从合并名单里去掉。然后告诉我现在名单有几个人，A组原来是几个人。", inc=["6", "4"])],
       adds=[(out, L("周明", "刘芳", "赵志强", "孙晓雯", "吴浩", "郑雅琪"))], exact=[out], must=["read_file", "write_file", "replace_lines"], rc=5, dep="group A size 4 counted in turn 1")
