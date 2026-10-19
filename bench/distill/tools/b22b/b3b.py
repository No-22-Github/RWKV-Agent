"""B3 (web-34146..34150): URL plus a local file, part two."""
from common import *

REQ = ("web_fetch", "read_file")
POL = {"must_offer": ["web_fetch", "read_file", "write_file", "replace_lines", "append_file"]}


def c146(files, web):
    t = files["docs/support.md"].replace("Mon–Fri 09:00–17:00 CET", "Mon–Fri 08:00–18:00 CET")
    return {"docs/support.md": t}, []


def c147(files, web):
    return {}, []


def c148(files, web):
    return {}, []


def c149(files, web):
    t = files["finance/invoice_template.txt"].replace("服务费率：5%", "服务费率：4%")
    return {"finance/invoice_template.txt": t}, []


def build():
    mk("web-34146", sub="B3", tt="lookup_value", desc="Update support hours in a local doc from the vendor page",
       web=[fx("larkdesk", "https://larkdesk.example/support/contact", "Contact support - Larkdesk", "How to reach Larkdesk support.",
               "# Contact support\n\nSupport hours: Mon–Fri 08:00–18:00 CET.\nEmergency line (paid plans only): 24/7.\nEmail: help@larkdesk.example", "2026-09-02")],
       files={"docs/support.md": "# Support\n\nSupport hours: Mon–Fri 09:00–17:00 CET.\nEscalation: ask in #ops first.\n"},
       turns=[T("Our docs/support.md has outdated hours. Update the hours line to match https://larkdesk.example/support/contact and leave everything else alone.", req=REQ, forb=(), inc=[])],
       compute=c146, traps=["TR-MULTISRC"], policy=POL, ref="web_fetch -> 08:00–18:00; read_file; replace the hours line",
       why="Only the hours line changes.", trap_notes=["24/7 emergency line is for paid plans only."], rc=4)
    mk("web-34147", sub="B3", tt="compare_sources", desc="Local value in turn one, URL recommendation and difference in turn two",
       web=[fx("silverqueue", "https://docs.silverqueue.example/tuning/timeouts", "Timeout tuning - SilverQueue", "Recommended timeouts.",
               "# Timeout tuning\n\nRecommended connect timeout: 5 s.\nRecommended request timeout: 45 s.\nBatch jobs may use up to 300 s.", "2026-06-16")],
       files={"config/app.ini": "[server]\nport = 8080\nrequest_timeout = 30\nconnect_timeout = 5\n"},
       turns=[T("config/app.ini 里的 request_timeout 现在是多少？", req=("read_file",), forb=("web_fetch", "web_search"), inc=["30"], exc=[]),
              T("SilverQueue 文档 https://docs.silverqueue.example/tuning/timeouts 推荐的请求超时是多少？比我们现在的多多少秒？", req=("web_fetch",), forb=(), inc=["45", "15"])],
       compute=c147, derived=["15"], traps=["TR-MULTISRC"], policy=POL, ref="第一轮只读本地 30；第二轮 web_fetch -> 45，差 15 秒",
       why="45-30=15。", trap_notes=["第一轮是纯本地问题，不该上网。"], rc=3)
    mk("web-34148", sub="B3", tt="latest_version", desc="How far behind a pinned version is, using a registry page",
       web=[fx("kitchenjs", "https://registry.kitchenjs.example/package/kitchenjs", "kitchenjs - package registry", "kitchenjs package page.",
               "# kitchenjs\n\nLatest version: 4.7.0 (2026-09-08)\nPrevious: 4.6.2, 4.5.0, 4.4.1, 4.3.0, 4.2.1\n\nLicense: MIT.", "2026-09-08")],
       files={"package.json": "{\n  \"name\": \"demo-app\",\n  \"dependencies\": {\n    \"kitchenjs\": \"4.2.1\",\n    \"leftpad2\": \"1.0.3\"\n  }\n}\n"},
       turns=[T("package.json pins kitchenjs. Check https://registry.kitchenjs.example/package/kitchenjs and tell me if we're behind and by how many minor versions.", req=REQ, forb=(), inc=["4.7.0"],
                any=["5 minor", "five minor", "by 5", "5 versions", "5 个", "5 releases"])],
       compute=c148, traps=["TR-MULTISRC"], policy=POL, ref="read_file -> 4.2.1; web_fetch -> 4.7.0; 4.7-4.2 = 5 个小版本",
       why="4.2.1 -> 4.7.0 相差 5 个小版本。", trap_notes=["页面的“Previous”列表里有 4.6.2 等中间版本。"], rc=3)
    mk("web-34149", sub="B3", tt="lookup_value", desc="Fix a rate line in an invoice template from a fee page",
       web=[fx("云舟支付", "https://pay.yunzhou.example/fees/service", "服务费率 - 云舟支付", "平台服务费率说明。",
               "# 服务费率\n\n自 2026 年 9 月 1 日起，商户服务费率调整为 4%（原 5%）。\n提现手续费每笔 1 元，不变。", "2026-08-25")],
       files={"finance/invoice_template.txt": "发票模板\n服务费率：5%\n提现手续费：1 元/笔\n备注：按月结算\n", "finance/README.md": "模板由财务维护。\n"},
       turns=[T("按 https://pay.yunzhou.example/fees/service 上的新费率，把 finance/invoice_template.txt 里的服务费率改掉，别的行不动。", req=REQ, forb=(), inc=[])],
       compute=c149, traps=["TR-MULTISRC"], policy=POL, ref="web_fetch -> 4%; read_file; 只改服务费率行", why="服务费率 5% -> 4%。",
       trap_notes=["提现手续费 1 元不变，不能改。"], rc=4)
    mk("web-34150", sub="B3", tt="lookup_value", desc="Append a fact from a page to a note, accept the change, then verify",
       web=[fx("白鹭湖", "https://baihuhu-reserve.example/visit/boardwalk", "栈道开放信息 - 白鹭湖湿地", "栈道长度与开放时间。",
               "# 栈道开放信息\n\n栈道全长 3.2 公里，步行一圈约 70 分钟。\n开放时间：8:00–17:30，雨天关闭。", "2026-05-20")],
       files={"notes/reading.md": "# 出行笔记\n\n- 周六去湿地公园\n"},
       turns=[T("读一下 https://baihuhu-reserve.example/visit/boardwalk ，把栈道全长和开放时间追加到 notes/reading.md 末尾。", req=REQ, forb=(), inc=[]),
              T("改动我已经确认保存了。再看一下 notes/reading.md，现在里面记的栈道全长是多少？", req=("read_file",), forb=("web_fetch",), inc=["3.2"], review="accept", exc=[])],
       case_files={"notes/reading.md": {"contains": ["3.2", "17:30"]}}, traps=["TR-MULTISRC"], policy=POL,
       ref="web_fetch -> 3.2 公里、8:00–17:30；append_file；用户接受；第二轮 read_file 读回 3.2", why="追加后文件含 3.2 与 17:30。",
       trap_notes=["第二轮只读本地文件，不再抓网页。"], rc=4)
