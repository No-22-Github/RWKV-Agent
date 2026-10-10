"""M3 (v1.4 §3.3) pilot, part A: two-turn recap, turn 2 forbids tools."""
from common import write_case

NOCALL = {"tools": [], "require_active_no_call": True}

# ---------------------------------------------------------------- fs-8002
write_case(
    "fs-8002",
    desc="Turn 1 reads an equipment ledger for a freezer's room; turn 2 forbids tools and asks the next calibration date from the same ledger",
    task_type="find_file", family="fam-fs-b10-labledger-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "实验室/设备台账.md": "# 实验室设备台账（2026-09 更新）\n\n| 设备 | 编号 | 房间 | 上次校准 | 下次校准 | 责任人 |\n|---|---|---|---|---|---|\n| 超低温冰箱 -80℃ | EQ-0412 | B214 | 2026-04-09 | 2026-10-09 | 骆文清 |\n| 二氧化碳培养箱 | EQ-0388 | B210 | 2026-06-21 | 2026-12-21 | 骆文清 |\n| 离心机 | EQ-0275 | B207 | 2026-03-14 | 2027-03-14 | 韦嘉 |\n| 生物安全柜 | EQ-0331 | B210 | 2026-07-02 | 2027-01-02 | 韦嘉 |\n",
        "实验室/借用登记.md": "# 借用登记\n\n- EQ-0275 离心机：2026-09-10 至 09-12 借给细胞组。\n",
        "README.md": "实验平台共享资料。设备以 实验室/设备台账.md 为准。\n",
    },
    turns=[
        {"prompt": "帮我看看 实验室/设备台账.md 里那台 -80℃ 超低温冰箱放在哪个房间？",
         "expect": {"output_contains": ["B214"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "别再调用工具了，就用刚才读到的台账：那台冰箱下次校准是哪天？",
         "expect": dict(NOCALL, output_contains_any=["2026-10-09", "10 月 9 日", "10月9日", "10 月 9 号", "10月9号"], max_output_chars=300)},
    ],
    verify='''
import json

case = json.load(open("case.json"))
text = case["files"]["实验室/设备台账.md"]
row = [l for l in text.splitlines() if "超低温冰箱" in l][0].split("|")
room, nxt = row[3].strip(), row[5].strip()
assert nxt == "2026-10-09"
assert case["files"]["README.md"].startswith("实验平台共享资料")
print(json.dumps({"expected_string": room}))
''',
    notes='''
## Traps
- None. 第 2 轮考的是用户明确说「别再调用工具」时，直接用第 1 轮读到的台账作答。

## Reference solution
1. 第 1 轮读 实验室/设备台账.md：-80℃ 超低温冰箱 EQ-0412 在 B214。终答一句话：在 B214（台账编号 EQ-0412）。
第 2 轮不调用任何工具：同一行的下次校准是 2026-10-09。终答一句话，例如「台账里那台冰箱下次校准是 2026-10-09，责任人骆文清。」判据：第 1 轮包含 B214；第 2 轮零调用并给出 2026-10-09（任一写法）。

## Why the answer is unique
台账里只有一台超低温冰箱，房间和下次校准日期都在同一行；第 2 轮需要的信息已经在第 1 轮的工具结果里，用户又明确禁止再调工具，所以第 2 轮唯一正确的做法是直接回答 2026-10-09。
''',
)

# ---------------------------------------------------------------- cfg-8003
write_case(
    "cfg-8003",
    desc="Turn 1 reads a gateway rate-limit file for one route's limit; turn 2 forbids tools and asks the rejection status configured in the same file",
    task_type="read_effective", family="fam-cfg-b10-ratelimit-01", level="L0", ref_calls=2, version=2,
    axes=["DEC"],
    files={
        "网关/限流.yaml": "默认:\n  每秒放行: 300\n  超限返回: 429\n路由:\n  /orders:\n    每秒放行: 1200\n    突发容量: 200\n    超限返回: 503\n    重试提示秒: 2\n  /reports:\n    每秒放行: 40\n",
        "网关/README.md": "限流按路由配置；路由里没写的项继承「默认」。\n",
        "网关/变更记录.md": "- 2026-09-02 /orders 每秒放行 800 -> 1200（大促扩容）\n",
    },
    turns=[
        {"prompt": "网关上 /orders 接口每秒最多放行多少个请求？",
         "expect": {"output_contains": ["1200"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "不用再查文件了，就按你刚才看到的配置说：/orders 超限以后返回什么状态码？",
         "expect": dict(NOCALL, output_contains=["503"], max_output_chars=300)},
    ],
    verify='''
import json

case = json.load(open("case.json"))
lines = case["files"]["网关/限流.yaml"].splitlines()
assert lines[0] == "默认:"
i = lines.index("  /orders:")
block = {}
for l in lines[i + 1:]:
    if not l.startswith("    "):
        break
    k, v = l.strip().split(":", 1)
    block[k] = v.strip()
assert block["超限返回"] == "503"
print(json.dumps({"expected_number": int(block["每秒放行"])}))
''',
    notes='''
## Traps
- None. 第 2 轮要用第 1 轮读到的 /orders 配置（超限返回 503），不能再调工具；「默认」块里的 429 是继承值，/orders 自己写了 503。

## Reference solution
1. 第 1 轮列出 网关/ 并读 网关/限流.yaml：/orders 每秒放行 1200（9 月 2 日由 800 扩到 1200）。终答一句话给出 1200 和依据。
第 2 轮零调用：/orders 块里「超限返回: 503」，并有「重试提示秒: 2」。终答一句话：超限返回 503。判据：第 1 轮含 1200；第 2 轮零调用、含 503。

## Changelog
- v2：去掉第 2 轮对 429 的排除。试跑里解题者答「/orders 单独配了 503，不走默认的 429」是正确的解释，被排除词误判；503 已是必含项，足以排除只答 429 的错误答案。

## Why the answer is unique
/orders 自己配置了超限返回 503，按 README 只有路由里没写的项才继承默认的 429，所以答案是 503；信息已在第 1 轮的读取结果里，用户禁止再调工具。
''',
)

# ---------------------------------------------------------------- log-8002
backup_log = """2026-09-15T23:30:00Z INFO backup-runner start job=nightly host=db-archive-03
2026-09-15T23:30:04Z INFO snapshot schema=billing tables=42
2026-09-15T23:52:41Z WARN table billing.audit_tmp skipped: locked by session 8812
2026-09-16T00:14:09Z INFO snapshot schema=inventory tables=31
2026-09-16T00:37:55Z WARN table inventory.sync_queue skipped: locked by session 9020
2026-09-16T00:38:12Z WARN table inventory.sync_queue_dlq skipped: locked by session 9020
2026-09-16T01:02:30Z INFO upload s3://ops-backups/db-archive-03/2026-09-15/ parts=118
2026-09-16T01:19:47Z INFO backup-runner done job=nightly status=completed_with_warnings tables_ok=70 tables_skipped=3 duration=1h49m47s
2026-09-16T01:20:02Z INFO retention pruned 2026-08-16
"""
write_case(
    "log-8002",
    desc="Turn 1 reads a nightly backup log for the finish time; turn 2 forbids tools and asks how many tables the same run skipped",
    task_type="time_window", family="fam-log-b10-nightlybackup-01", level="L0", ref_calls=2, version=2,
    axes=["DEC"],
    files={
        "logs/db-archive-03/backup-2026-09-15.log": backup_log,
        "logs/db-archive-03/backup-2026-09-14.log": "2026-09-14T23:30:00Z INFO backup-runner start job=nightly host=db-archive-03\n2026-09-15T01:11:20Z INFO backup-runner done job=nightly status=completed tables_ok=73 tables_skipped=0 duration=1h41m20s\n",
        "README.md": "Ops logs. Timestamps are UTC. One backup log per night, named by the date the job started.\n",
    },
    turns=[
        {"prompt": "When did last night's nightly backup on db-archive-03 finish? The job started on September 15.",
         "expect": {"output_contains_any": ["01:19:47", "01:19"], "required_tools": ["read_file"], "max_output_chars": 300}},
        {"prompt": "Don't open the logs again, just go by what you already read: how many tables did that same run skip?",
         "expect": dict(NOCALL, output_contains_any=["3", "three", "Three"], max_output_chars=300)},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
log = case["files"]["logs/db-archive-03/backup-2026-09-15.log"]
done = [l for l in log.splitlines() if "backup-runner done" in l][0]
skipped = int(re.search(r"tables_skipped=(\\d+)", done).group(1))
assert skipped == len([l for l in log.splitlines() if " skipped: " in l]) == 3
assert case["files"]["logs/db-archive-03/backup-2026-09-14.log"].startswith("2026-09-14T23:30:00Z INFO backup-runner start")
finish = done.split()[0][11:19]
print(json.dumps({"expected_contains_any": [finish, finish[:5], str(skipped), "three", "Three"]}))
''',
    notes='''
## Traps
- None. Turn 2 must be answered from the turn-1 read without a tool call.

## Reference solution
1. Turn 1: read logs/db-archive-03/backup-2026-09-15.log (the job that started Sep 15). The done line is 2026-09-16T01:19:47Z, status completed_with_warnings. Final answer: it finished at 01:19:47 UTC on Sep 16, with warnings.
Turn 2, no tool call: the same done line says tables_skipped=3 (billing.audit_tmp, inventory.sync_queue, inventory.sync_queue_dlq, all locked). Final answer in one sentence: 3 tables were skipped. Criteria: turn 1 gives 01:19(:47); turn 2 is zero-call and says 3 (digit or word).

## Changelog
- v2: turn 2 accepts "three"/"Three" as well as 3; the pilot solver's "Three tables were skipped" was correct.

## Why the answer is unique
The done line and the three WARN lines agree on 3 skipped tables. The Sep 14 log is the previous night's run (0 skipped) and is not the run in question. Turn 2 forbids reopening the logs, and turn 1 already read this file.
''',
)

# ---------------------------------------------------------------- tab-8003
import random
rng = random.Random(80033)
stores = ["静安店", "徐汇店", "浦东店", "闵行店"]
rows = []
for i in range(120):
    rows.append(("POS-%05d" % (40000 + i), "2026-09-%02d" % rng.randint(1, 30), stores[i % 4] if i % 5 else rng.choice(stores), "%.2f" % rng.uniform(80, 2600)))
rows.sort(key=lambda r: r[1])
jingan = round(sum(float(r[3]) for r in rows if r[1] and r[2] == "静安店"), 2)
wan = "%.2f" % (jingan / 10000)
write_case(
    "tab-8003",
    desc="Turn 1 totals one store's September sales; turn 2 forbids tools and asks the same total expressed in units of ten thousand yuan",
    task_type="aggregate", family="fam-tab-b10-storesales-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files={
        "销售/9月门店流水.csv": "流水号,日期,门店,金额\n" + "".join(",".join(r) + "\n" for r in rows),
        "README.md": "# 栖木咖啡 门店流水\n\n金额单位为元，已含税。\n",
    },
    turns=[
        {"prompt": "统计一下静安店 9 月的销售额是多少元？",
         "expect": {"output_contains_any": [("%.2f" % jingan).rstrip("0"), "{:,.2f}".format(jingan).rstrip("0")], "max_output_chars": 300}},
        {"prompt": "先别调工具，就刚才那个数，换算成万元、保留两位小数是多少？",
         "expect": dict(NOCALL, output_contains=[wan], max_output_chars=300)},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["销售/9月门店流水.csv"])))
total = round(sum(float(r["金额"]) for r in rows if r["门店"] == "静安店"), 2)
print(json.dumps({"expected_number": round(total / 10000, 2)}))
''',
    notes='''
## Traps
- None. 第 2 轮是对第 1 轮结果做一步换算，用户明确要求不调工具。

## Reference solution
1. 第 1 轮用 data_query 对 销售/9月门店流水.csv 按 门店=静安店 求和 金额（或整读后合计）：%s 元。终答一句话给出金额与口径（含税）。
第 2 轮零调用：%s ÷ 10000 = %s 万元。终答一句话。判据：第 1 轮含 %s；第 2 轮零调用并含 %s。

## Why the answer is unique
金额只有一个口径（元、含税），静安店的行由门店列唯一确定；第 2 轮只是把同一个数除以一万并保留两位。
''' % ("%.2f" % jingan, "%.2f" % jingan, wan, "%.2f" % jingan, wan),
)
