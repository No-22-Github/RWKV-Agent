"""M5 (v1.4 §3.5) pilot, part B: value from another source, new report files, refuse to write on missing info."""
import random
from common import write_case

# ---------------------------------------------------------------- cfg-8009
req = "fastapi==0.115.2\nhttpx==0.26.0\npydantic==2.8.2\nuvicorn==0.30.6\n"
lock = '''[[package]]
name = "httpcore"
version = "1.0.5"

[[package]]
name = "httpx"
version = "0.27.2"

[[package]]
name = "pydantic"
version = "2.8.2"
'''
write_case(
    "cfg-8009",
    desc="Align one requirements pin with the version locked in poetry.lock; a neighbouring package with a similar name has a different version",
    task_type="edit_value", family="fam-cfg-b10-lockpin-01", level="L1", ref_calls=4,
    traps=["TR-DECOY"], decoys={"TR-DECOY": None}, axes=["OBS"],
    files={"requirements.txt": req, "poetry.lock": lock, "README.md": "Deploy installs from requirements.txt; poetry.lock is the source of truth for versions.\n"},
    case_expect={"files": {"requirements.txt": {"equals": req.replace("httpx==0.26.0", "httpx==0.27.2")}}},
    turns=[{
        "prompt": "requirements.txt has httpx pinned to an older version than poetry.lock. Update the httpx pin to match the lock file. When finished, reply DONE.",
        "expect": {"output_contains": ["DONE", "0.27.2"], "max_output_chars": 300},
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
lock = case["files"]["poetry.lock"]
ver = re.search(r'name = "httpx"\\nversion = "([^"]+)"', lock).group(1)
req = case["files"]["requirements.txt"]
assert req.startswith("fastapi==")
print(json.dumps({"files": {"requirements.txt": re.sub(r"^httpx==.*$", "httpx==" + ver, req, flags=re.M)}}))
''',
    notes='''
## Traps
- TR-DECOY: poetry.lock lists httpcore 1.0.5 right above httpx; reading the wrong block gives a wrong pin.

## Reference solution
1. Read poetry.lock: httpx is 0.27.2.
2. Read requirements.txt: httpx==0.26.0 on line 2.
3. replace_lines line 2 with `httpx==0.27.2`.
4. Read requirements.txt back.
Final answer: one sentence (requirements.txt now pins httpx==0.27.2 to match poetry.lock), then DONE on its own line. Criteria: exact file content; output contains DONE and 0.27.2.

## Why the answer is unique
The lock has exactly one httpx block; the other pins already match or are not mentioned.
''',
)

# ---------------------------------------------------------------- hyb-8003
docker = "FROM ghcr.io/tidewater/runtime:5.3.1\nWORKDIR /srv\nCOPY . .\nCMD [\"tidewater\", \"serve\", \"--port\", \"8080\"]\n"
write_case(
    "hyb-8003",
    desc="Bump a Dockerfile base image to the newest patch of the current minor series according to the project's releases page; a release candidate of the next minor and an older blog post are decoys",
    task_type="web_then_edit", family="fam-hyb-b10-runtimepatch-01", level="L2", ref_calls=5, version=2,
    traps=["TR-WEBSTALE", "TR-DECOY"], decoys={"TR-WEBSTALE": None, "TR-DECOY": None}, axes=["VER", "OBS"],
    web=[
        {"query_match": "tidewater", "url_match": "tidewater.dev/releases", "url": "https://tidewater.dev/releases",
         "title": "Tidewater runtime releases", "snippet": "Release history for the Tidewater runtime images.",
         "content": "# Tidewater runtime releases\n\n| Version | Channel | Date |\n|---|---|---|\n| 5.4.0-rc1 | preview | 2026-09-08 |\n| 5.3.4 | stable | 2026-09-02 |\n| 5.3.3 | stable | 2026-08-05 |\n| 5.3.2 | stable | 2026-07-01 |\n| 5.3.1 | stable | 2026-06-10 |\n\nImages: ghcr.io/tidewater/runtime:<version>\n",
         "published_at": "2026-09-08"},
        {"query_match": "tidewater", "url_match": "blog.shipyardnotes.io/tidewater-5-3", "url": "https://blog.shipyardnotes.io/tidewater-5-3",
         "title": "Upgrading to Tidewater 5.3.2", "snippet": "We moved all services to Tidewater 5.3.2, the newest 5.3 patch.",
         "content": "# Upgrading to Tidewater 5.3.2\n\nJuly 2026. We moved all services to runtime 5.3.2, the newest 5.3 patch at the time.\n",
         "published_at": "2026-07-04"},
    ],
    files={"Dockerfile": docker, "README.md": "Gateway service image. Stay on the 5.3 series until the 5.4 migration is planned.\n"},
    case_expect={"files": {"Dockerfile": {"equals": docker.replace("runtime:5.3.1", "runtime:5.3.4")}}},
    turns=[{
        "prompt": "Bump the Tidewater runtime base image in our Dockerfile to the newest 5.3 patch release.",
        "expect": {"output_contains": ["5.3.4"], "output_excludes": ["5.4.0-rc1 is the"], "required_tools": ["web_fetch"], "max_output_chars": 600},
    }],
    verify='''
import json
import re

case = json.load(open("case.json"))
page = [w for w in case["web_fixture"] if w["url"] == "https://tidewater.dev/releases"][0]["content"]
stable = [m.group(1) for m in re.finditer(r"\\| (5\\.3\\.\\d+) \\| stable \\|", page)]
best = max(stable, key=lambda v: int(v.split(".")[2]))
assert case["files"]["README.md"].startswith("Gateway service image. Stay on the 5.3 series")
src = case["files"]["Dockerfile"]
assert src.startswith("FROM ghcr.io/tidewater/runtime:5.3.")
new = re.sub(r"runtime:5\\.3\\.\\d+", "runtime:" + best, src, count=1)
print(json.dumps({"files": {"Dockerfile": new}}))
''',
    notes='''
## Traps
- TR-WEBSTALE: a July 2026 blog post calls 5.3.2 "the newest 5.3 patch"; it is two patches behind.
- TR-DECOY: the releases page lists 5.4.0-rc1 above 5.3.4; it is a preview of the next minor, and the README says to stay on 5.3.

## Reference solution
1. Read Dockerfile: FROM ghcr.io/tidewater/runtime:5.3.1 (line 1).
2. Search "tidewater runtime releases": the official releases page and a blog post.
3. Fetch https://tidewater.dev/releases: newest stable 5.3 patch is 5.3.4 (2026-09-02).
4. replace_lines line 1 with `FROM ghcr.io/tidewater/runtime:5.3.4`.
5. Read Dockerfile back.
Final answer, one sentence: the Dockerfile now uses runtime 5.3.4, the newest 5.3 patch on the official releases page (5.4.0-rc1 is a preview of 5.4). Criteria: exact Dockerfile; output contains 5.3.4.

## Why the answer is unique
Among 5.3.x stable entries on the official page, 5.3.4 is the highest; the blog predates it and the rc is a different minor series.

## Changelog
- v2: max_output_chars raised to 600, the §4.2 limit; the pilot answer (309 chars) was correct and within the spec limit but over the stricter limit this case had set.

## Five alternative phrasings of the task
1. tidewater runtime releases
2. tidewater runtime 5.3 latest patch
3. tidewater 5.3.4
4. ghcr.io tidewater runtime image versions
5. tidewater runtime changelog
''',
)

# ---------------------------------------------------------------- tab-8007
rng = random.Random(80088)
branches = ["城东分馆", "城西分馆", "南湖分馆", "北苑分馆", "中心馆"]
while True:
    rows = [("JY-%05d" % (50000 + i), "2026-09-%02d" % rng.randint(1, 30), rng.choice(branches), str(rng.randint(1, 6))) for i in range(150)]
    tot = {b: sum(int(r[3]) for r in rows if r[2] == b) for b in branches}
    if len(set(tot.values())) == len(branches):
        break
order = sorted(branches, key=lambda b: -tot[b])
report = "分馆,册数\n" + "\n".join("%s,%d" % (b, tot[b]) for b in order)
write_case(
    "tab-8007",
    desc="Sum September loans per branch and write them to a new CSV report with a given header, sorted by count descending",
    task_type="write_summary", family="fam-tab-b10-libraryloans-01", level="L0", ref_calls=3,
    axes=[],
    files={"借阅/2026-09.csv": "借阅单号,日期,分馆,册数\n" + "".join(",".join(r) + "\n" for r in rows),
           "报表/.keep": "", "README.md": "# 市图书馆借阅明细\n\n一行一张借阅单，册数为该单借出的册数。\n"},
    case_expect={"files": {"报表/9月借阅汇总.csv": {"contains": [report]}}},
    turns=[{
        "prompt": "把 9 月各分馆借出的册数汇总一下，写进 报表/9月借阅汇总.csv，表头用「分馆,册数」，按册数从多到少排。",
        "expect": {"output_contains_any": ["报表/9月借阅汇总.csv", "9月借阅汇总.csv"], "max_output_chars": 300},
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["借阅/2026-09.csv"])))
tot = {}
for r in rows:
    tot[r["分馆"]] = tot.get(r["分馆"], 0) + int(r["册数"])
body = "\\n".join("%s,%d" % (b, n) for b, n in sorted(tot.items(), key=lambda x: -x[1]))
print(json.dumps({"files": {"报表/9月借阅汇总.csv": "分馆,册数\\n" + body + "\\n"}}, ensure_ascii=False))
''',
    notes='''
## Traps
- None.

## Reference solution
1. data_query：path 借阅/2026-09.csv，group_by 分馆，operation sum，field 册数。结果：%s。
2. write_file 报表/9月借阅汇总.csv，内容为表头「分馆,册数」加按册数降序的五行。
3. 回读 报表/9月借阅汇总.csv 确认内容。
终答一句话：已把 9 月各分馆借阅册数写到 报表/9月借阅汇总.csv（五个分馆，%s 最多）。回复里不重复表格内容。判据：文件包含期望的表头与五行（顺序一致）；终答提到文件名。

## Why the answer is unique
五个分馆的合计互不相同，降序唯一；表头由题面指定。
''' % ("、".join("%s %d" % (b, tot[b]) for b in order), order[0]),
)

# ---------------------------------------------------------------- log-8005
rng = random.Random(80099)
log = []
t = 13 * 3600 + 30 * 60
errs = []
while t < 14 * 3600 + 40 * 60:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    stamp = "2026-09-15T%02d:%02d:%02dZ" % (h, m, s)
    if 14 * 3600 + 2 * 60 <= t <= 14 * 3600 + 20 * 60 and rng.random() < 0.5:
        log.append("%s ERROR pay-api charge failed: upstream ledger 503" % stamp)
        errs.append(stamp)
    elif rng.random() < 0.15:
        log.append("%s WARN pay-api slow upstream ledger %dms" % (stamp, rng.randint(800, 2400)))
    else:
        log.append("%s INFO pay-api charge ok" % stamp)
    t += rng.randint(20, 75)
lines3 = ["start: " + errs[0], "end: " + errs[-1], "errors: %d" % len(errs)]
write_case(
    "log-8005",
    desc="Write a three-line incident summary file with the first and last ERROR timestamps and the ERROR count from a service log",
    task_type="time_window", family="fam-log-b10-incidentsummary-01", level="L0", ref_calls=3,
    axes=[],
    files={"logs/pay-api-2026-09-15.log": "\n".join(log) + "\n", "incidents/.keep": "",
           "README.md": "pay-api logs, UTC timestamps. Incident notes go under incidents/.\n"},
    case_expect={"files": {"incidents/2026-09-15-pay-api.md": {"contains": lines3}}},
    turns=[{
        "prompt": "Create incidents/2026-09-15-pay-api.md with three lines: `start: <timestamp of the first ERROR>`, `end: <timestamp of the last ERROR>`, `errors: <number of ERROR lines>`, using timestamps exactly as they appear in the pay-api log for that day.",
        "expect": {"output_contains_any": ["incidents/2026-09-15-pay-api.md"], "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("pay-api logs, UTC timestamps.")
lines = case["files"]["logs/pay-api-2026-09-15.log"].splitlines()
assert lines[0].startswith("2026-09-15T13:30:00Z")
errs = [l.split()[0] for l in lines if " ERROR " in l]
body = "start: %s\\nend: %s\\nerrors: %d\\n" % (errs[0], errs[-1], len(errs))
print(json.dumps({"files": {"incidents/2026-09-15-pay-api.md": body}}))
''',
    notes='''
## Traps
- None. The log has %d lines; WARN lines about slow upstream are not ERRORs.

## Reference solution
1. Search "ERROR" in logs/pay-api-2026-09-15.log: %d matches, first %s, last %s.
2. write_file incidents/2026-09-15-pay-api.md with the three lines `%s`, `%s`, `%s`.
3. Read the new file back.
Final answer, one sentence: wrote incidents/2026-09-15-pay-api.md (errors ran from %s to %s, %d in total). Criteria: the file contains the three lines; the answer names the file.

## Why the answer is unique
ERROR lines are marked by level; timestamps are copied verbatim, so the three lines are fixed.
''' % (len(log), len(errs), errs[0], errs[-1], lines3[0], lines3[1], lines3[2], errs[0], errs[-1], len(errs)),
)

# ---------------------------------------------------------------- cfg-8010
dbcfg = "订单库:\n  主库地址: pg-orders-01.internal:5432\n  从库地址: pg-orders-02.internal:5432\n  连接池: 40\n"
write_case(
    "cfg-8010",
    desc="A change ticket asks to switch the primary database address but the new address is still pending DBA confirmation, so nothing should be written and DONE must not be claimed",
    task_type="edit_value", family="fam-cfg-b10-pendingaddr-01", level="L1", ref_calls=2,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": None}, axes=["DEC"],
    files={"配置/数据库.yaml": dbcfg,
           "工单/GD-0815.txt": "变更项: 订单库 主库地址\n新值: 待 DBA 确认（预计 2026-09-18 给出）\n原因: 主库迁移到新机房\n申请: 交易组 祁若溪\n",
           "README.md": "交易系统配置，改动须有工单且新值明确。\n"},
    case_expect={"files": {"配置/数据库.yaml": {"unchanged": True}}},
    turns=[{
        "prompt": "照 工单/GD-0815.txt 把 配置/数据库.yaml 的主库地址改了，改完回复 DONE。",
        "expect": {"output_contains_any": ["DBA", "待确认", "没有给出", "未给出", "还没给", "没有新地址", "缺少新地址"],
                   "output_excludes": ["DONE"], "forbidden_tools": ["write_file", "replace_lines", "append_file"], "max_output_chars": 400},
    }],
    verify='''
import json

case = json.load(open("case.json"))
t = dict(l.split(": ", 1) for l in case["files"]["工单/GD-0815.txt"].splitlines() if ": " in l)
assert t["变更项"] == "订单库 主库地址"
assert t["新值"].startswith("待 DBA 确认")
assert case["files"]["README.md"].startswith("交易系统配置")
words = ["DBA", "待确认", "没有给出", "未给出", "还没给", "没有新地址", "缺少新地址"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 工单/GD-0815.txt 的「新值」是「待 DBA 确认（预计 2026-09-18 给出）」，没有可写的地址。写任何值、或不写却回复 DONE，都是错的。

## Reference solution
1. 读 工单/GD-0815.txt：新主库地址待 DBA 确认。
2. （可选）读 配置/数据库.yaml 确认当前主库是 pg-orders-01.internal:5432。
不调用写工具。终答 2–3 句：工单里新主库地址还是「待 DBA 确认」（预计 9 月 18 日给出），没有可写的值，所以 配置/数据库.yaml 没改，现在仍是 pg-orders-01.internal:5432；拿到 DBA 给的新地址后告诉我，我再改。不写 DONE。判据：文件不变、不调写工具、终答含 DBA 等说明、不含 DONE。

## Why the answer is unique
工单只有一个变更项且新值缺失；README 要求新值明确才改，所以唯一正确的处理是不写并说明缺什么。
''',
)
