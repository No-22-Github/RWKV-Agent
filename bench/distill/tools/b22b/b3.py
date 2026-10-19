"""B3 (web-34141..34145): URL plus a local file."""
from common import *

REQ = ("web_fetch", "read_file")
POL = {"must_offer": ["web_fetch", "read_file", "write_file", "replace_lines"]}


def nofiles(files, web):
    return {}, []


def build():
    mk("web-34141", sub="B3", tt="compare_sources", desc="Check a local limits file against a limits page",
       web=[fx("stratoscale", "https://dev.stratoscale.example/docs/limits", "Service limits - Stratoscale", "Hard limits for the gateway.",
               "# Service limits\n\n- Maximum request body: 10 MB\n- Maximum concurrent connections: 200\n- Maximum requests per minute: 1200\n\nThese limits apply from 2026-10-01.", "2026-09-10")],
       files={"config/limits.yaml": "max_body_mb: 25\nmax_connections: 150\nrate_per_min: 1500\nidle_timeout_s: 60\n", "config/README.md": "Gateway limits live in limits.yaml.\n"},
       turns=[T("按 https://dev.stratoscale.example/docs/limits 上的新规，检查一下 config/limits.yaml 有没有超标的项。", req=REQ, forb=(), inc=["max_body_mb", "rate_per_min"])],
       compute=nofiles, traps=["TR-MULTISRC"], policy=POL, ref="web_fetch + read_file -> body 25>10、rate 1500>1200 超标，connections 150<200 正常",
       why="两项超标：max_body_mb、rate_per_min。", trap_notes=["必须同时读网页和本地文件，只看一边答不全。"], rc=3)
    mk("web-34142", sub="B3", tt="lookup_value", desc="Bump a pinned dependency to the fixed version named in an advisory",
       web=[fx("pyfern", "https://advisories.pyfern.example/PF-2026-031", "PF-2026-031 - tablekit path traversal", "Security advisory for tablekit.",
               "# PF-2026-031\n\nAffected: tablekit < 2.8.4\nFixed in: tablekit 2.8.4\n\nUpgrade to 2.8.4 or later. Versions 2.9.x are not affected.", "2026-09-05")],
       files={"requirements.txt": "flasklet==1.4.0\ntablekit==2.7.1\nzipwise==0.9.3\n"},
       turns=[T("https://advisories.pyfern.example/PF-2026-031 这个安全公告说 tablekit 要升到哪个版本？照着改 requirements.txt，其他行别动。", req=REQ + (), forb=(), inc=["2.8.4"])],
       compute=c142, traps=["TR-MULTISRC"], policy=POL, ref="web_fetch -> 2.8.4; read_file requirements.txt; 改 tablekit 一行",
       why="Fixed in 2.8.4。", trap_notes=["只改 tablekit 一行。"], rc=4)
    mk("web-34143", sub="B3", tt="compare_sources", desc="Difference between an assumed price in notes and the price on a page",
       web=[fx("tokenbay", "https://tokenbay.example/pricing/api", "API pricing - TokenBay", "Per-token prices.",
               "# API pricing\n\n- Standard model: $1.10 per 1M input tokens\n- Mini model: $0.30 per 1M input tokens\n\nPrices updated 2026-09-01.", "2026-09-01")],
       files={"docs/pricing-notes.md": "# Pricing assumptions\n\nAssumed API price (standard model): $0.80 per 1M input tokens.\nVolume: 400M tokens per month.\n"},
       turns=[T("Our assumption is in docs/pricing-notes.md. How far off is it from the standard model price on https://tokenbay.example/pricing/api ?", req=REQ, forb=(), inc=["1.10"], any=["0.30", "$0.3 ", "30 cents", "0.3 dollars"])],
       compute=nofiles, traps=["TR-MULTISRC"], policy=POL, ref="read_file notes ($0.80) + web_fetch ($1.10) -> 0.30 higher",
       why="1.10-0.80=0.30。", trap_notes=["Mini 的 $0.30 与差值同数，须说明是标准版差价。"], rc=3)
    mk("web-34144", sub="B3", tt="lookup_value", desc="Read a price from a URL, then write it into a local note in turn two",
       web=[fx("青禾健身", "https://www.qinghe-fit.example/membership", "会员价格 - 青禾健身", "月卡、季卡、年卡价格。",
               "# 会员价格\n\n- 月卡 188 元\n- 季卡 498 元\n- 年卡 1680 元\n\n学生凭证享 8 折。", "2026-08-22")],
       files={"notes/budget.md": "# 本月预算\n\n- 房租 2400 元\n- 健身年卡 1500 元（待确认）\n- 交通 260 元\n"},
       turns=[T("青禾健身 https://www.qinghe-fit.example/membership 的年卡多少钱？", forb=("read_file",), inc=["1680"]),
              T("好，把 notes/budget.md 里健身年卡那一行的金额改成这个价格，去掉“待确认”。", req=("read_file",), forb=(), inc=[])],
       compute=c144, traps=["TR-MULTISRC"], policy=POL, ref="第一轮 web_fetch -> 1680；第二轮 read_file + 改一行",
       why="年卡 1680 元，写回预算行。", trap_notes=["第二轮不必再抓网页。"], rc=4)
    mk("web-34145", sub="B3", tt="compare_sources", desc="Which required documents are still missing from a checklist",
       web=[fx("市民服务中心", "https://service.lanxi-hall.example/apply/materials", "申请材料清单 - 兰溪市民服务中心", "居住证申请所需材料。",
               "# 居住证申请材料\n\n1. 身份证复印件\n2. 一寸照片 2 张\n3. 学历证明\n4. 无犯罪记录证明\n5. 体检表\n\n材料需一次性提交，缺一不予受理。", "2026-07-01")],
       files={"todo/apply.md": "# 居住证准备情况\n\n- [x] 身份证复印件\n- [x] 一寸照片 2 张\n- [x] 体检表\n- [ ] 预约窗口时间\n"},
       turns=[T("我在 todo/apply.md 里记了准备情况，对照 https://service.lanxi-hall.example/apply/materials 看看还缺哪些材料？", req=REQ, forb=(), inc=["学历证明", "无犯罪记录证明"])],
       compute=nofiles, traps=["TR-MULTISRC"], policy=POL, ref="web_fetch 清单 5 项 vs 本地已备 3 项 -> 缺学历证明、无犯罪记录证明",
       why="清单五项，已备三项。", trap_notes=["待办里的“预约窗口时间”不是材料。"], rc=3)


def c142(files, web):
    t = files["requirements.txt"].replace("tablekit==2.7.1", "tablekit==2.8.4")
    return {"requirements.txt": t}, []


def c144(files, web):
    t = files["notes/budget.md"].replace("健身年卡 1500 元（待确认）", "健身年卡 1680 元")
    return {"notes/budget.md": t}, []
