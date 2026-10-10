"""M6 (v1.4 §3.6) pilot, part A: mixed date formats, time zones, filter + join."""
import json as _json
import random
from datetime import datetime, timedelta
from common import write_case

MAXREAD = {"max_calls": {"read_file": 1}}
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

import csv as _csv
import io as _io

def csvq(header, rows):
    buf = _io.StringIO()
    w = _csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()

def num(x):
    s = ("%.2f" % x).rstrip("0").rstrip(".")
    return s

# ---------------------------------------------------------------- tab-8008
rng = random.Random(80108)
rows, truth, decoy = [], 0, 0
for i in range(130):
    d = rng.randint(1, 31)
    fmt = rng.choice(["slash", "dmy", "mon", "iso"])
    if fmt == "slash":
        s = "2026/03/%02d" % d
    elif fmt == "dmy":
        s = "%02d-03-2026" % d
    elif fmt == "mon":
        s = "Mar %d, 2026" % d
    else:
        s = "2026-03-%02dT08:00:00Z" % d
    rows.append(("FH-%05d" % (31000 + i), s, rng.choice(["沙发", "餐桌", "床架", "书柜"]), str(rng.randint(1, 4))))
    if d <= 10:
        truth += 1
    # decoy: a dd-mm-yyyy date read as mm-dd-yyyy lands in month d (or is invalid) and drops out
    if d <= 10 and not (fmt == "dmy" and d != 3):
        decoy += 1
assert truth > 31
rng.shuffle(rows)
write_case(
    "tab-8008",
    desc="Count March 1-10 shipments in an export whose date column mixes four formats, one of them day-month-year",
    task_type="filter_count", family="fam-tab-b10-mixeddates-01", level="L1", ref_calls=2,
    traps=["TR-DATEFMT"], decoys={"TR-DATEFMT": decoy}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"物流/发货记录.csv": csvq(["发货单号", "发货日期", "品类", "件数"], rows),
           "README.md": "# 砚山家居 发货流水\n\n一行一单。发货日期来自三个系统，写法不统一：门店系统写 2026/03/02；仓库系统的短日期是「日-月-年」，07-03-2026 表示 2026 年 3 月 7 日；电商系统写 Mar 11, 2026 或 ISO 时间（UTC 08:00，即北京时间当天下午）。\n"},
    turns=[{
        "prompt": "砚山家居 3 月 1 日到 10 日（含）一共发了多少单？发货流水在 物流/发货记录.csv。",
        "expect": {"output_contains": [str(truth)], "output_contains_token": True, "required_tools": ["data_query"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json
import re

case = json.load(open("case.json"))
assert "日-月-年" in case["files"]["README.md"]
n = 0
for r in csv.DictReader(io.StringIO(case["files"]["物流/发货记录.csv"])):
    s = r["发货日期"]
    m = re.match(r"2026/03/(\\d\\d)$", s) or re.match(r"(\\d\\d)-03-2026$", s) or re.match(r"Mar (\\d+), 2026$", s) or re.match(r"2026-03-(\\d\\d)T", s)
    assert m, s
    n += int(m.group(1)) <= 10
print(json.dumps({"expected_number": n}))
''',
    notes='''
## Traps
- TR-DATEFMT: 发货日期列混了 2026/03/02、07-03-2026（日-月-年）、Mar 11, 2026、2026-03-05T08:00:00Z 四种写法。把 07-03-2026 这类读成「月-日-年」，3 月 1–10 日里这一类的单子会被算到别的月份，只剩 %d 单。

## Reference solution
1. data_query：path 物流/发货记录.csv，group_by 发货日期，operation count，拿到每个日期写法的单数。
2. 读 README.md（可在第 1 步之前）确认短日期是「日-月-年」。
3. 把各写法归一到 3 月几日，挑出 1–10 日的分组，用计算器把单数加起来：%d 单。
终答 1–2 句：3 月 1–10 日共发 %d 单；日期列有四种写法，其中 07-03-2026 这类按 README 是日-月-年，已归一后再计数。判据：包含 %d（独立词元），用过 data_query，read_file 最多 1 次。

## Why the answer is unique
README 规定了短日期的读法，ISO 时间是 UTC 08:00、落在北京时间同一天，所以每一行都能唯一归到 3 月某日；1–10 日（含）的计数唯一。
''' % (decoy, truth, truth, truth),
)

# ---------------------------------------------------------------- tab-8009
rng = random.Random(80109)
rows, truth, decoy = [], 0, 0
for i in range(160):
    d = rng.randint(1, 31)
    q = rng.choice(["billing", "billing", "shipping", "accounts"])
    fmt = rng.choice(["iso", "us", "mon", "dt"])
    s = {"iso": "2026-08-%02d" % d, "us": "08/%02d/2026" % d, "mon": "Aug %d, 2026" % d, "dt": "2026-08-%02d %02d:%02d" % (d, rng.randint(8, 18), rng.choice([0, 10, 15, 20, 30, 40, 45, 50]))}[fmt]
    rows.append(("TCK-%05d" % (88000 + i), s, q, rng.choice(["P2", "P3", "P3", "P1"])))
    if q == "billing" and d <= 14:
        truth += 1
    if q == "billing" and d <= 14 and fmt != "us":
        decoy += 1
assert truth > 31
rng.shuffle(rows)
write_case(
    "tab-8009",
    desc="Count billing-queue tickets opened August 1-14 when the opened column mixes ISO, US month/day, month-name and datetime forms",
    task_type="filter_count", family="fam-tab-b10-ticketweek-01", level="L1", ref_calls=2,
    traps=["TR-DATEFMT"], decoys={"TR-DATEFMT": decoy}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"support/tickets-2026-08.csv": csvq(["ticket", "opened", "queue", "priority"], rows),
           "support/README.md": "Ticket export for Fernhill Telecom. The opened column comes from three intake tools: the portal writes 2026-08-03 or 2026-08-03 14:22 (local time), the phone desk writes US-style 08/04/2026 (month/day/year), and email intake writes Aug 5, 2026.\n"},
    turns=[{
        "prompt": "How many billing-queue tickets were opened in the first two weeks of August, the 1st through the 14th?",
        "expect": {"output_contains": [str(truth)], "output_contains_token": True, "required_tools": ["data_query"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json
import re

case = json.load(open("case.json"))
assert "month/day/year" in case["files"]["support/README.md"]
n = 0
for r in csv.DictReader(io.StringIO(case["files"]["support/tickets-2026-08.csv"])):
    s = r["opened"]
    m = re.match(r"2026-08-(\\d\\d)", s) or re.match(r"08/(\\d\\d)/2026$", s) or re.match(r"Aug (\\d+), 2026$", s)
    assert m, s
    n += r["queue"] == "billing" and int(m.group(1)) <= 14
print(json.dumps({"expected_number": n}))
''',
    notes='''
## Traps
- TR-DATEFMT: the phone desk writes month/day/year (08/04/2026 is Aug 4). Reading those as day/month moves every such ticket out of the first two weeks of August, giving %d.

## Reference solution
1. data_query on support/tickets-2026-08.csv with filter {"queue": "billing"}, group_by opened, operation count.
2. Normalise each opened string to an August day using support/README.md (read once if needed); keep days 1-14 and add the counts with the calculator: %d.
Final answer, 1-2 sentences: %d billing tickets were opened Aug 1-14; the opened column mixes four formats and the phone desk's 08/04/2026 style is month/day. Criteria: contains %d as a whole token, data_query used, at most one read_file.

## Why the answer is unique
Every opened value parses to exactly one August day under the README's conventions; the queue filter is exact.
''' % (decoy, truth, truth, truth),
)

# ---------------------------------------------------------------- log-8006
rng = random.Random(80110)
t0 = datetime(2026, 9, 14, 12, 0, 0)
lines, t = [], t0
deploy_at = datetime(2026, 9, 14, 17, 2, 10)
first_err_after = datetime(2026, 9, 14, 17, 41, 7)
planted = False
while t < datetime(2026, 9, 15, 1, 0, 0):
    stamp = t.strftime("%Y-%m-%dT%H:%M:%SZ")
    if not planted and t >= first_err_after:
        lines.append("%s ERROR tide-gw route=/v3/quote upstream reset by peer" % first_err_after.strftime("%Y-%m-%dT%H:%M:%SZ"))
        planted = True
    elif datetime(2026, 9, 14, 17, 0, 0) <= t < datetime(2026, 9, 14, 17, 2, 10):
        pass
    elif t < deploy_at and rng.random() < 0.04:
        lines.append("%s ERROR tide-gw route=/v3/quote upstream timeout" % stamp)
    elif rng.random() < 0.1:
        lines.append("%s WARN tide-gw slow upstream %dms" % (stamp, rng.randint(900, 3000)))
    else:
        lines.append("%s INFO tide-gw route=/v3/%s 200" % (stamp, rng.choice(["quote", "book", "status"])))
    if t < deploy_at <= t + timedelta(seconds=90):
        lines.append("%s INFO deploy version=tide-gw-2.9.0 complete" % deploy_at.strftime("%Y-%m-%dT%H:%M:%SZ"))
    t += timedelta(seconds=rng.randint(40, 90))
log_text = "# tide-gw log, host tide-gw-01, times in UTC\n" + "\n".join(lines) + "\n"
assert sum(1 for l in lines if " ERROR " in l and l[:20] > "2026-09-14T17:02:10Z" and l[:20] < "2026-09-14T17:41:07Z") == 0
bj = (first_err_after + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
write_case(
    "log-8006",
    desc="Find the first ERROR after a deploy in a UTC log and report it in Beijing time, which crosses midnight; earlier ERRORs precede the deploy",
    task_type="locate_error", family="fam-log-b10-postdeployerror-01", level="L2", ref_calls=2,
    traps=["TR-TZ", "TR-DECOY"], decoys={"TR-TZ": "2026-09-14 17:41:07", "TR-DECOY": "pre-deploy ERROR"}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"logs/tide-gw.log": log_text, "README.md": "# 潮汐网关\n\n日志时间一律为 UTC。值班报告请用北京时间。\n"},
    turns=[{
        "prompt": "潮汐网关升级到 2.9.0 之后记录的第一条 ERROR 发生在北京时间什么时候？按 YYYY-MM-DD HH:MM:SS 给我。",
        "expect": {"output_contains": [bj], "max_output_chars": 400},
    }],
    verify='''
import json
from datetime import datetime, timedelta

case = json.load(open("case.json"))
assert "UTC" in case["files"]["README.md"]
lines = case["files"]["logs/tide-gw.log"].splitlines()
assert lines[0].startswith("# tide-gw log, host tide-gw-01")
dep = next(i for i, l in enumerate(lines) if "deploy version=tide-gw-2.9.0" in l)
err = next(l for l in lines[dep + 1:] if " ERROR " in l)
t = datetime.strptime(err.split()[0], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
print(json.dumps({"expected_string": t.strftime("%Y-%m-%d %H:%M:%S")}))
''',
    notes='''
## Traps
- TR-DECOY: 升级前（17:02:10Z 之前）就有若干条 ERROR（upstream timeout），第一条 ERROR 不是答案。
- TR-TZ: 日志是 UTC。升级后第一条 ERROR 是 2026-09-14T17:41:07Z，换成北京时间要 +8 小时并跨日到 %s；直接报 2026-09-14 17:41:07 就是诱饵。

## Reference solution
1. search_text 搜「deploy version=tide-gw-2.9.0」找到升级行（带行号）。
2. search_text 搜「ERROR」，取升级行之后的第一条：2026-09-14T17:41:07Z。换算北京时间 +8 小时得 %s（可心算，也可用 datetime add 8h 核对）。
终答 1–2 句：升级后第一条 ERROR 是北京时间 %s（日志原始时间 2026-09-14T17:41:07Z，UTC+8 跨到 15 日）。判据：包含 %s；read_file 最多 1 次。

## Why the answer is unique
升级行唯一，升级后到 17:41:07Z 之间没有别的 ERROR；README 说明日志为 UTC、报告用北京时间，换算结果唯一。
''' % (bj, bj, bj, bj),
)

# ---------------------------------------------------------------- log-8007
rng = random.Random(80111)
t = datetime(2026, 9, 14, 0, 30, 0)
lines = []
fails = {datetime(2026, 9, 14, 1, 13, 58): ("req-7f3a91c2", "harbourline-florists"),
         datetime(2026, 9, 14, 1, 16, 40): ("req-0b8e44d7", "ostler-bakery"),
         datetime(2026, 9, 14, 9, 15, 2): ("req-c4d2e019", "harbourline-florists"),
         datetime(2026, 9, 14, 0, 52, 31): ("req-91aa6b30", "kinmen-tea")}
merchants = ["harbourline-florists", "ostler-bakery", "kinmen-tea", "palmgrove-optics", "tanjong-books"]
while t < datetime(2026, 9, 14, 10, 0, 0):
    lines.append((t, "%s INFO checkout ok req-%08x merchant=%s" % (t.strftime("%Y-%m-%dT%H:%M:%SZ"), rng.getrandbits(32), rng.choice(merchants))))
    t += timedelta(seconds=rng.randint(45, 140))
for ft, (rid, m) in fails.items():
    lines.append((ft, "%s ERROR checkout failed %s merchant=%s card_declined_by_gateway" % (ft.strftime("%Y-%m-%dT%H:%M:%SZ"), rid, m)))
lines.sort()
write_case(
    "log-8007",
    desc="Match a customer-reported failure time given in Singapore time to the nearest failed checkout in a UTC API log; an unconverted reading matches a different request",
    task_type="time_window", family="fam-log-b10-sgtticket-01", level="L2", ref_calls=3, version=2,
    traps=["TR-TZ", "TR-MULTISRC"], decoys={"TR-TZ": "req-c4d2e019", "TR-MULTISRC": "req-0b8e44d7"}, axes=["OBS", "CHN"],
    case_expect={"max_calls": {"read_file": 2}},
    files={"logs/checkout-api-2026-09-14.log": "# checkout-api, region ap-southeast-1, UTC\n" + "\n".join(l for _, l in lines) + "\n",
           "support/T-4471.md": "# T-4471\n\nCustomer: Harbourline Florists (Singapore), merchant id harbourline-florists\nReported: card payment failed at checkout around 09:15 SGT on 14 Sep 2026.\nAgent note: customer tried once, did not retry.\n",
           "README.md": "Checkout API logs are in UTC. Support tickets record times as the customer gives them.\n"},
    turns=[{
        "prompt": "Support ticket T-4471 describes a failed checkout. Which request ID in the checkout API log is the customer's failed attempt?",
        "expect": {"output_contains": ["req-7f3a91c2"], "output_excludes": ["req-c4d2e019 is"], "max_output_chars": 400},
    }],
    verify='''
import json
from datetime import datetime, timedelta

case = json.load(open("case.json"))
f = case["files"]
assert "09:15 SGT" in f["support/T-4471.md"]
assert f["logs/checkout-api-2026-09-14.log"].startswith("# checkout-api, region ap-southeast-1")
target = datetime(2026, 9, 14, 9, 15) - timedelta(hours=8)
fails = []
for l in f["logs/checkout-api-2026-09-14.log"].splitlines():
    if " ERROR checkout failed " in l and "merchant=harbourline-florists" in l:
        t = datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ")
        fails.append((abs((t - target).total_seconds()), l.split()[4]))
print(json.dumps({"expected_string": min(fails)[1]}))
''',
    notes='''
## Traps
- TR-TZ: the ticket says 09:15 SGT (UTC+8) and the log is UTC, so the report corresponds to about 01:15Z. Matching 09:15 in the log without converting lands on req-c4d2e019 (09:15:02Z), which is the same merchant but at 17:15 SGT, a different checkout.
- TR-MULTISRC: the ticket names the merchant id; the log's merchant field is what ties a failure to this customer. req-0b8e44d7 also failed near 01:15Z (01:16:40Z) but belongs to ostler-bakery.

## Reference solution
1. Read support/T-4471.md: 09:15 SGT on 14 Sep, merchant id harbourline-florists, one attempt.
2. search_text "merchant=harbourline-florists card_declined" (or "checkout failed") in logs/checkout-api-2026-09-14.log.
3. Convert 09:15 SGT to 01:15Z: harbourline-florists failed at 01:13:58Z (req-7f3a91c2) and at 09:15:02Z (req-c4d2e019, i.e. 17:15 SGT).
Final answer, 1-2 sentences: req-7f3a91c2, Harbourline Florists' failed checkout at 01:13:58Z (09:13:58 SGT), which matches the ticket's 09:15 SGT; their 09:15:02Z failure is 17:15 Singapore time. Criteria: contains req-7f3a91c2; at most two read_file calls.

## Why the answer is unique
Only two failures carry the ticket's merchant id, and only one of them is near 09:15 SGT once converted.

## Changelog
- v2: added a merchant field to every log line and the merchant id to the ticket. In v1 two failures sat within 100 s of 01:15Z with nothing tying either to the customer, so "the nearest one" was a guess (the pilot solver flagged it). Raised the read_file budget from 1 to 2 so reading the ticket and README is allowed.
''',
)

# ---------------------------------------------------------------- tab-8010
rng = random.Random(80112)
depts = ["研发部"] * 9 + ["市场部"] * 7 + ["运营部"] * 8 + ["财务部"] * 5
roster = [("E%04d" % (1100 + i * 3), "员工%02d" % i, depts[i]) for i in range(len(depts))]
rng.shuffle(roster)
hours = []
for i in range(420):
    emp = rng.choice(roster)[0]
    kind = rng.choice(["正常", "正常", "正常", "加班"])
    h = 8 if kind == "正常" else rng.choice([1, 1.5, 2, 2.5, 3, 4])
    hours.append((emp, "2026-09-%02d" % rng.randint(1, 30), kind, ("%g" % h)))
rd = {r[0] for r in roster if r[2] == "研发部"}
total = sum(float(h[3]) for h in hours if h[0] in rd and h[2] == "加班")
all_ot = sum(float(h[3]) for h in hours if h[2] == "加班")
write_case(
    "tab-8010",
    desc="Sum one department's September overtime hours by joining a roster to an hours log that has no department column",
    task_type="join", family="fam-tab-b10-overtimejoin-01", level="L2", ref_calls=4,
    traps=["TR-MULTISRC", "TR-DEFN"], decoys={"TR-MULTISRC": num(all_ot), "TR-DEFN": num(sum(float(h[3]) for h in hours if h[0] in rd))}, axes=["CHN", "OBS"],
    case_expect=MAXREAD,
    files={"人事/花名册.csv": "工号,姓名,部门\n" + "".join(",".join(r) + "\n" for r in roster),
           "考勤/2026-09-工时.csv": "工号,日期,类型,小时\n" + "".join(",".join(h) + "\n" for h in hours),
           "README.md": "# 栖霞科技 考勤\n\n工时表按工号记录，不含部门；部门以花名册为准。\n"},
    turns=[{
        "prompt": "研发部 9 月一共加了多少小时的班？",
        "expect": {"output_contains": [num(total)], "output_contains_token": True, "required_tools": ["data_query"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
roster = list(csv.DictReader(io.StringIO(f["人事/花名册.csv"])))
rd = {r["工号"] for r in roster if r["部门"] == "研发部"}
hours = list(csv.DictReader(io.StringIO(f["考勤/2026-09-工时.csv"])))
print(json.dumps({"expected_number": sum(float(h["小时"]) for h in hours if h["工号"] in rd and h["类型"] == "加班")}))
''',
    notes='''
## Traps
- TR-MULTISRC: 工时表没有部门列，必须用花名册把工号映射到部门。不做映射、把全公司加班加起来是 %s。
- TR-DEFN: 问的是加班，类型列还有「正常」；把研发部全部工时加起来是 %s。

## Reference solution
1. data_query：人事/花名册.csv，filter {"部门":"研发部"}，select 工号 → 9 个工号。
2. data_query：考勤/2026-09-工时.csv，filter {"类型":"加班"}，group_by 工号，operation sum，field 小时。
3. 从分组结果里取这 9 个工号的值，用计算器求和：%s 小时。
4. （可选）读 README 确认部门以花名册为准。
终答 1–2 句：研发部 9 月加班合计 %s 小时（工时表按工号记录，已按花名册筛出研发部 9 人、只算类型为加班的记录）。判据：包含 %s（独立词元）；用过 data_query；read_file 最多 1 次。

## Why the answer is unique
工号唯一对应部门，类型列只有正常/加班两值，合计唯一。
''' % (num(all_ot), num(sum(float(h[3]) for h in hours if h[0] in rd)), num(total), num(total), num(total)),
)
