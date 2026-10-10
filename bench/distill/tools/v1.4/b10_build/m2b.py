"""M2 (v1.4 §3.2) pilot, part B: missing data, unreachable web source, partial answer."""
import random
from common import write_case

# ---------------------------------------------------------------- log-8001
rng = random.Random(80011)
lines = ["# payment-gw warn log, host gw-02, times Asia/Shanghai"]
events = []
def ts(h, m, s):
    return "2026-09-14T%02d:%02d:%02d+08:00" % (h, m, s)
minute = 2
while minute < 107:  # 00:02 .. 01:46
    h, m = divmod(minute, 60)
    if rng.random() < 0.45:
        events.append((h, m, rng.randint(0, 59), "WARN upstream timeout route=/v2/charge ms=5000"))
    else:
        events.append((h, m, rng.randint(0, 59), "INFO settle batch ok size=%d" % rng.randint(20, 90)))
    minute += rng.randint(2, 4)
events.append((1, 47, 5, "INFO collector: shipping paused for maintenance window"))
events.append((3, 41, 30, "INFO collector: shipping resumed; lines from 01:47 to 03:41 were not shipped and are not backfilled"))
minute = 223
while minute < 300:
    h, m = divmod(minute, 60)
    kind = "WARN upstream timeout route=/v2/refund ms=5000" if rng.random() < 0.3 else "INFO settle batch ok size=%d" % rng.randint(20, 90)
    events.append((h, m, rng.randint(0, 59), kind))
    minute += rng.randint(2, 5)
for h, m, s, msg in events:
    lines.append("%s %s" % (ts(h, m, s), msg))
log_text = "\n".join(lines) + "\n"
hour1 = sum(1 for h, m, s, msg in events if h == 1 and "timeout" in msg)
assert hour1 % 10 != 0
write_case(
    "log-8001",
    desc="Asks how many upstream timeouts the payment gateway logged between 02:00 and 03:00; the log has a collector gap covering that hour, so the count is unknown, not zero",
    task_type="time_window", family="fam-log-b10-collectorgap-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "0"},
    axes=["DEC"],
    files={
        "logs/payment-gw/2026-09-14.log": log_text,
        "运维/日志采集说明.md": "# 日志采集说明\n\n网关日志由 collector 每分钟推送到 logs/。维护期间推送暂停，暂停时段的日志不会补传；原始日志只在网关本机 /var/log/gw/ 保留 7 天。\n",
        "README.md": "# 支付网关运维仓库\n\nlogs/ 下按服务、按天存放网关日志。\n",
    },
    turns=[{
        "prompt": "支付网关 9 月 14 日凌晨 2 点到 3 点之间一共出现了多少次上游超时？",
        "expect": {
            "output_contains_any": ["中断", "暂停", "维护", "没有采集", "没有推送", "没有日志", "缺失", "空白", "没有记录"],
            "output_excludes": ["0 次", "零次", "共 0", "为 0 次"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/payment-gw/2026-09-14.log"].splitlines()
assert log[0].startswith("# payment-gw warn log, host gw-02")
stamps = [re.match(r"2026-09-14T(\\d\\d):(\\d\\d)", l) for l in log[1:]]
minutes = [int(m.group(1)) * 60 + int(m.group(2)) for m in stamps]
# No line at all falls inside 02:00-03:00: the collector paused at 01:47 and resumed at 03:41.
assert not any(120 <= x < 180 for x in minutes)
assert any("shipping paused" in l for l in log) and any("not backfilled" in l for l in log)
words = ["中断", "暂停", "维护", "没有采集", "没有推送", "没有日志", "缺失", "空白", "没有记录"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: logs/payment-gw/2026-09-14.log 在 01:47 记录「collector: shipping paused for maintenance window」，03:41 记录「shipping resumed; lines from 01:47 to 03:41 were not shipped and are not backfilled」。2 点到 3 点之间一行都没有。把「没有超时行」读成「0 次超时」就是诱饵答案（0）。

## Reference solution
1. 读 logs/payment-gw/2026-09-14.log（或按 timeout 搜索后再看 01:47–03:41 前后的行），发现 01:47 到 03:41 没有日志，且 collector 说明这段不补传。
2. 读 运维/日志采集说明.md：暂停时段的日志不补传，原始日志只在网关本机 /var/log/gw/ 保留 7 天。
终答（2–4 句）：2 点到 3 点这一段日志是空的——collector 01:47 起因维护暂停推送、03:41 才恢复，这段不补传，所以没法统计超时次数，也不能当成 0 次；日志头写明主机是 gw-02，原始日志在本机 /var/log/gw/ 只保留 7 天，需要尽快去那台机器上取。（参考：1 点到 1 点 47 分有 %d 次超时。）判据：包含一个「中断/暂停/缺失」说法，不得说 0 次。

## Why the answer is unique
诱饵 0 错在把「没有记录」当成「没有发生」：日志自己写明 01:47–03:41 的行没有推送也不补传，采集说明也确认维护期间推送暂停。工作区里没有任何其他来源记录这一小时，所以次数无法确定，只能说明缺口并指向本机原始日志。
''' % hour1,
)

# ---------------------------------------------------------------- cfg-8002
write_case(
    "cfg-8002",
    desc="Asks the retry backoff of a worker in production; neither the base nor the production config sets it, the docs say the client library default applies, and a healthcheck retry interval is the decoy",
    task_type="read_effective", family="fam-cfg-b10-retrybackoff-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "30"},
    axes=["DEC", "OBS"],
    files={
        "config/ledger-sync.toml": "[worker]\nqueue = \"ledger-events\"\nbatch_size = 500\nmax_retries = 6\n\n[healthcheck]\npath = \"/healthz\"\nretry_interval_s = 30\n",
        "config/env/production.toml": "[worker]\nbatch_size = 2000\nmax_retries = 8\n",
        "docs/worker-config.md": "# ledger-sync worker settings\n\n- batch_size: events per commit.\n- max_retries: attempts before an event goes to the dead-letter queue.\n- retry_backoff_ms: delay between retries. When unset, the worker uses the backoff built into the ledgerkit client library, which has changed between ledgerkit releases. Pin it explicitly for production.\n- healthcheck.retry_interval_s: how often the orchestrator re-probes /healthz after a failed probe. Unrelated to event retries.\n",
        "README.md": "ledger-sync: consumes ledger events and writes them to the reporting store. Settings in config/ledger-sync.toml; per-environment overrides in config/env/.\n",
    },
    turns=[{
        "prompt": "We are tuning ledger-sync after last night's dead-letter spike. What retry backoff does the worker use in production?",
        "expect": {
            "output_contains": ["ledgerkit"],
            "output_contains_any": ["not set", "isn't set", "not configured", "isn't configured", "not defined", "doesn't set", "does not set", "no retry_backoff_ms", "unset", "neither"],
            "output_excludes": ["backoff is 30", "backoff of 30", "30 seconds between retries", "30-second backoff"],
            "required_tools": ["read_file"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].startswith("ledger-sync: consumes ledger events")
doc = files["docs/worker-config.md"].splitlines()
assert doc[0] == "# ledger-sync worker settings"
lib = [l for l in doc if l.startswith("- retry_backoff_ms:")][0].split("built into the ")[1].split(" ")[0]
for path in ("config/ledger-sync.toml", "config/env/production.toml"):
    assert "retry_backoff_ms" not in files[path]
print(json.dumps({"expected_string": lib}))
''',
    notes='''
## Traps
- TR-ABSENT: neither config/ledger-sync.toml nor config/env/production.toml sets retry_backoff_ms. docs/worker-config.md says the unset value falls back to the backoff built into the ledgerkit client library, which has changed between releases.
- TR-DECOY: config/ledger-sync.toml has `[healthcheck] retry_interval_s = 30`. Reporting a 30-second backoff is the decoy answer; the docs say that interval is how often /healthz is re-probed and is unrelated to event retries.

## Reference solution
1. Read config/ledger-sync.toml: no retry_backoff_ms; only the healthcheck retry_interval_s = 30.
2. Read config/env/production.toml: overrides batch_size and max_retries only.
3. Read docs/worker-config.md: unset backoff means the ledgerkit library default, which varies by release.
Final answer (2-4 sentences): retry_backoff_ms is not set in either the base config or the production override, so production runs on ledgerkit's built-in backoff, and the repo does not record what that is for the version you ship. The retry_interval_s = 30 in the file is the healthcheck re-probe interval, not the event retry backoff. Check the ledgerkit release you deploy, or pin retry_backoff_ms in config/env/production.toml as the docs recommend. Criteria: mentions ledgerkit and that the setting is not set; must not present 30 seconds as the backoff.

## Why the answer is unique
The only "retry" number in the configs belongs to the healthcheck block, and the docs state it is unrelated to event retries. The backoff key appears in neither file, so the effective value is the library default, which the workspace does not contain. Answering with any number would be invented.
''',
)

# ---------------------------------------------------------------- hyb-8001
fleet = [("澄浪1号", 1420, "在役"), ("澄浪2号", 1385, "在役"), ("澄浪3号", 1510, "在役"), ("澄浪5号", 980, "封存")]
gt = sum(t for n, t, s in fleet if s == "在役")
write_case(
    "hyb-8001",
    desc="Berth licence fee for in-service dredgers at the port authority's current-quarter rate; the authority's tariff page fails to load and the only other hit is a 2024 blog, so only the tonnage can be given",
    task_type="web_then_calc", family="fam-hyb-b10-berthfee-01", level="L2", ref_calls=4,
    traps=["TR-FETCHFAIL", "TR-WEBSTALE"], decoys={"TR-FETCHFAIL": "UNKNOWN", "TR-WEBSTALE": str(round(gt * 1.2))},
    axes=["ERR", "VER"],
    web=[
        {"query_match": "靠泊费", "url_match": "dongyu-port.gov.cn/tariff", "url": "https://www.dongyu-port.gov.cn/tariff/2026-q4",
         "title": "东屿港务局 2026 年第四季度港口收费标准", "snippet": "本季度靠泊许可费、引航费、拖轮费标准（按总吨计）。",
         "published_at": "2026-09-30", "error": "HTTP 503 Service Unavailable"},
        {"query_match": "靠泊费", "url_match": "haiyun-notes.cn/posts/berth-fee", "url": "https://haiyun-notes.cn/posts/berth-fee-2024",
         "title": "跑船笔记：东屿港靠泊费怎么算", "snippet": "2024 年东屿港靠泊许可费每总吨 1.2 元，疏浚船同标准。",
         "content": "# 东屿港靠泊费怎么算\n\n2024 年 3 月更新：东屿港靠泊许可费按每总吨 1.2 元收取，疏浚船、工程船同标准。以港务局公告为准。\n",
         "published_at": "2024-03-18"},
    ],
    files={
        "船队/疏浚船.csv": "船名,总吨,状态\n" + "".join("%s,%d,%s\n" % f for f in fleet),
        "README.md": "# 澄浪疏浚 船队台账\n\n船队/ 下按船型记录总吨与状态；封存船不办理靠泊许可。\n",
    },
    turns=[{
        "prompt": "按东屿港务局这个季度公布的靠泊费率，帮我算一下我们在役疏浚船这季度的靠泊许可费一共要交多少。",
        "expect": {
            "output_contains": [str(gt)],
            "output_contains_any": ["503", "打不开", "无法访问", "访问失败", "抓取失败", "获取失败", "没能获取", "没有获取", "无法获取", "没能打开"],
            "output_excludes": [str(round(gt * 1.2)), "{:,}".format(round(gt * 1.2))],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["船队/疏浚船.csv"])))
total = sum(int(r["总吨"]) for r in rows if r["状态"] == "在役")
official = [w for w in case["web_fixture"] if "dongyu-port.gov.cn" in w["url"]][0]
assert official.get("error")
print(json.dumps({"expected_number": total}))
''',
    notes='''
## Traps
- TR-FETCHFAIL: 港务局本季度收费标准页 https://www.dongyu-port.gov.cn/tariff/2026-q4 抓取返回 HTTP 503，拿不到本季度费率。
- TR-WEBSTALE: 搜索结果里另有一篇 2024 年的博客，写每总吨 1.2 元。用它算出 %d 元就是诱饵答案：那是两年前的标准，不是「这个季度公布的」费率，博客自己也写了以港务局公告为准。

## Reference solution
1. 读 船队/疏浚船.csv：在役三条（澄浪1号 1420、澄浪2号 1385、澄浪3号 1510）合计 %d 总吨，澄浪5号封存不计。
2. 搜索东屿港务局靠泊费：结果是港务局 2026 Q4 收费标准页和一篇 2024 年博客。
3. 抓取港务局页面：HTTP 503。
4. （可选）不采用博客的 2024 年费率。
终答（2–4 句）：在役三条疏浚船合计 %d 总吨；港务局本季度收费标准页打不开（503），所以这季度的费率拿不到，费用没有算；搜到的 1.2 元/总吨出自 2024 年的博客，不是本季度标准，不能拿来算。可以稍后再试，或者把港务局的费率通知发给我，我直接按 %d 总吨算。判据：包含 %d、一个「打不开/503」说法，不得给出按 1.2 元算出的金额。

## Why the answer is unique
题面限定「这个季度公布的」费率，唯一的官方来源抓取失败；博客发布于 2024 年 3 月，期间不符，且明说以公告为准，所以用它算出的金额不是用户要的数。总吨是本地台账里确定的，封存船按 README 不办理靠泊许可，因此能给出的确定部分只有 %d 总吨。

## Five alternative phrasings of the task
1. 东屿港务局 靠泊费 2026 第四季度
2. 东屿港 疏浚船 靠泊费 标准
3. 东屿港务局 靠泊费 收费标准 每总吨
4. 靠泊费 东屿港 本季度
5. 东屿港务局 港口收费 靠泊费率
''' % (round(gt * 1.2), gt, gt, gt, gt, gt),
)

# ---------------------------------------------------------------- web-8001
write_case(
    "web-8001",
    desc="Asks the per-request price of a geocoding API plan; the vendor pricing page times out and the vendor status page confirms the pricing pages are degraded",
    task_type="lookup_value", family="fam-web-b10-geocodeprice-01", level="L1", ref_calls=3,
    traps=["TR-FETCHFAIL"], decoys={"TR-FETCHFAIL": "UNKNOWN"},
    axes=["ERR"],
    web=[
        {"query_match": "lumenroute", "url_match": "lumenroute.io/pricing", "url": "https://lumenroute.io/pricing",
         "title": "Lumenroute pricing - Geocoding, Routing, Places", "snippet": "Compare the Starter, Standard and Scale plans for the Lumenroute geocoding and routing APIs.",
         "published_at": "2026-09-02", "error": "Connection timed out after 30000 ms"},
        {"query_match": "lumenroute", "url_match": "status.lumenroute.io", "url": "https://status.lumenroute.io/",
         "title": "Lumenroute Status", "snippet": "Current status of Lumenroute APIs and websites.",
         "content": "# Lumenroute Status\n\nAPIs: Operational.\n\nIncident (investigating, started 2026-09-16 08:40 UTC): the marketing site, including /pricing and /docs, is timing out for some regions. API traffic and the billing console at console.lumenroute.io are not affected.\n",
         "published_at": "2026-09-16"},
    ],
    files={},
    turns=[{
        "prompt": "Procurement wants the current per-request price for the Lumenroute geocoding API on the Standard plan. What is it?",
        "expect": {
            "output_contains": ["Standard"],
            "output_contains_any": ["timed out", "timing out", "time out", "timeout", "couldn't load", "could not load", "unable to load", "couldn't fetch", "could not fetch", "unable to fetch", "failed to load"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = {w["url"]: w for w in case["web_fixture"]}
assert pages["https://lumenroute.io/pricing"]["error"].startswith("Connection timed out")
status = pages["https://status.lumenroute.io/"]["content"]
assert "/pricing" in status and "console.lumenroute.io" in status
words = ["timed out", "timing out", "time out", "timeout", "couldn't load", "could not load",
         "unable to load", "couldn't fetch", "could not fetch", "unable to fetch", "failed to load"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- TR-FETCHFAIL: the only pricing source, https://lumenroute.io/pricing, fails with "Connection timed out after 30000 ms". No search snippet carries a price. The status page reports an incident: /pricing and /docs are timing out, while API traffic and the billing console at console.lumenroute.io are unaffected.

## Reference solution
1. Search for Lumenroute geocoding pricing: two hits, the pricing page and the status page.
2. Fetch https://lumenroute.io/pricing: connection timed out.
3. Fetch https://status.lumenroute.io/: incident says the pricing pages are timing out; the billing console works.
Final answer (2-4 sentences): the Standard-plan price could not be retrieved, because Lumenroute's pricing page timed out, and their status page confirms an ongoing incident with /pricing and /docs. No other source in the results states the price, so I have no figure to give. Procurement can read it from the billing console (console.lumenroute.io), which the incident does not affect, or I can try the pricing page again later. Criteria: mentions Standard and a timeout/could-not-fetch phrase; there is no price anywhere, so any number would be invented.

## Why the answer is unique
Neither the snippets nor any fetchable page contains a per-request price, so there is nothing to report but the failure. The status page explains the failure and points to a working source, which is the useful next step.

## Five alternative phrasings of the task
1. Lumenroute geocoding API Standard plan price per request
2. lumenroute pricing
3. Lumenroute Standard plan cost
4. how much does Lumenroute geocoding cost per request
5. Lumenroute geocoding pricing 2026
''',
)

# ---------------------------------------------------------------- tab-8002
rng = random.Random(80022)
def tickets(prefix, days, n):
    out = []
    for i in range(n):
        d = rng.choice(days)
        out.append(("%s-%04d" % (prefix, 3100 + i), "2026-08-%02d" % d, rng.choice(["空调", "冰箱", "洗衣机", "热水器"]), rng.choice(["已结单", "处理中", "已结单", "已结单"])))
    out.sort(key=lambda r: r[1])
    return out
north = tickets("HB", list(range(1, 32)), 47)
online = tickets("XS", list(range(1, 21)), 38)
csv_of = lambda rows: "工单号,受理日期,品类,状态\n" + "".join(",".join(r) + "\n" for r in rows)
write_case(
    "tab-8002",
    desc="August warranty tickets across a service station and online support; online support only exported through Aug 20 before a system migration, so only a partial total is certain",
    task_type="aggregate", family="fam-tab-b10-warrantytickets-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-MULTISRC"], decoys={"TR-ABSENT": str(len(north) + len(online)), "TR-MULTISRC": str(len(north))},
    axes=["DEC", "CHN"],
    files={
        "售后/华北服务站-8月.csv": csv_of(north),
        "售后/线上客服-8月.csv": csv_of(online),
        "售后/README.md": "# 售后保修工单导出\n\n华北服务站每月导出一次。线上客服工单 8 月 21 日起迁移到新工单系统，迁移期间（8 月 21 日以后）的工单尚未导出，预计 9 月底补录。\n",
    },
    turns=[{
        "prompt": "8 月份华北服务站和线上客服一共受理了多少张保修工单？",
        "expect": {
            "output_contains": [str(len(north))],
            "output_contains_any": ["补录", "迁移", "未导出", "没导出", "还没导出", "尚未导出", "没有导出"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
north = list(csv.DictReader(io.StringIO(files["售后/华北服务站-8月.csv"])))
online = list(csv.DictReader(io.StringIO(files["售后/线上客服-8月.csv"])))
assert north and set(north[0]) == {"工单号", "受理日期", "品类", "状态"}
assert max(r["受理日期"] for r in online) <= "2026-08-20"
print(json.dumps({"expected_number": len(north)}))
''',
    notes='''
## Traps
- TR-ABSENT: 售后/线上客服-8月.csv 只有 8 月 1 日到 20 日的 %d 张；售后/README.md 写明 8 月 21 日起迁移新系统，之后的工单尚未导出、预计 9 月底补录。把 %d + %d = %d 当成全月合计就是诱饵答案。
- TR-MULTISRC: 只看华北服务站一个文件会得到 %d，漏掉线上客服。

## Reference solution
1. 列出 售后/：两份 CSV 和 README。
2. 读（或 data_query 计数）华北服务站：%d 张，覆盖全月。
3. 读线上客服 CSV 与 README：只到 8 月 20 日，%d 张，之后待补录。
终答（2–4 句）：华北服务站 8 月受理 %d 张，这个数是全的；线上客服只导出到 8 月 20 日（%d 张），21 日以后的工单因为迁移新系统还没导出，预计 9 月底补录，所以全月合计现在给不出，目前能确定的是至少 %d 张。补录后我可以再合计一次。判据：包含 %d 和一个「迁移/补录/未导出」说法。

## Why the answer is unique
%d 只覆盖线上客服的前 20 天，README 明确后面的工单还没导出，把它报成全月合计是错的；%d 漏了线上客服。能确定的只有华北服务站的全月数和线上的截至 20 日数，所以正确回答是给出确定部分并点名缺口。
''' % (len(online), len(north), len(online), len(north) + len(online), len(north), len(north), len(online),
       len(north), len(online), len(north) + len(online), len(north), len(north) + len(online), len(north)),
)
