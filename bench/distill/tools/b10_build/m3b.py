"""M3 (v1.4 §3.3) pilot, part B: single-turn explicit ban, and ask-for-the-missing-parameter."""
import random
from common import write_case

NOCALL = {"tools": [], "require_active_no_call": True}

# ---------------------------------------------------------------- nt-8001
write_case(
    "nt-8001",
    desc="User has proxy configs in the workspace but explicitly says not to open them and asks the difference between HTTP 502 and 504",
    task_type="concept", family="fam-nt-b10-gatewaycodes-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={
        "nginx/conf.d/upstream.conf": "upstream orders_api {\n    server 10.0.4.21:8080;\n    server 10.0.4.22:8080;\n}\nproxy_read_timeout 15s;\n",
        "README.md": "边缘代理配置。改动后执行 nginx -t 再 reload。\n",
    },
    turns=[{
        "prompt": "不用翻配置文件，直接跟我讲一下 HTTP 502 和 504 有什么区别？",
        "expect": dict(NOCALL, output_contains=["502", "504"], output_contains_any=["超时"], max_output_chars=600),
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("边缘代理配置")
assert "proxy_read_timeout" in case["files"]["nginx/conf.d/upstream.conf"]
print(json.dumps({"expected_contains_any": ["超时"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 工作区里有代理配置，但用户明确说不用翻文件，问的是通用概念。

## Reference solution
不调用任何工具，直接回答（2–3 句）：502 Bad Gateway 是网关/代理从上游拿到了无效响应（上游崩溃、连接被拒、返回内容不合法）；504 Gateway Timeout 是网关在规定时间内没等到上游响应，即超时。可补一句排查方向：502 先看上游进程和端口，504 先看上游耗时和代理的超时设置。判据：零调用，包含 502、504 和「超时」。

## Why the answer is unique
这是 HTTP 标准里的稳定定义，与工作区内容无关；用户显式要求不翻文件，所以任何工具调用都是违背指令。
''',
)

# ---------------------------------------------------------------- nt-8002
write_case(
    "nt-8002",
    desc="User asks a two-step stock arithmetic question and explicitly says not to use any tools",
    task_type="unit_convert", family="fam-nt-b10-receivingloss-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": "不用调工具，直接帮我算：一批货 18 箱、每箱 24 件，抽检损耗按 2.5% 算，实际能入库多少件？",
        "expect": dict(NOCALL, output_contains=["421"], max_output_chars=400),
    }],
    verify='''
import json

case = json.load(open("case.json"))
prompt = case["turns"][0]["prompt"]
assert "18 箱" in prompt and "24 件" in prompt and "2.5%" in prompt
good = 18 * 24 * (1 - 0.025)
print(json.dumps({"expected_number": int(good)}))
''',
    notes='''
## Traps
- None. 用户明确说不用调工具；计算器虽然在工具清单里，这一题也不该调用。

## Reference solution
不调用任何工具：18 × 24 = 432 件，432 × (1 − 2.5%) = 421.2 件，按整件算能入库 421 件。终答 1–2 句，写出算式。判据：零调用，包含 421。

## Why the answer is unique
两步乘法没有歧义；421.2 件不可能拆出 0.2 件，按整件取 421。
''',
)

# ---------------------------------------------------------------- nt-8003
write_case(
    "nt-8003",
    desc="User asks what a five-field cron expression means and says there is no need to open any files",
    task_type="concept", family="fam-nt-b10-cronread-01", level="L0", ref_calls=0,
    axes=["DEC"],
    files={},
    turns=[{
        "prompt": "No need to open anything for this one: what schedule does the cron expression `30 2 * * 1-5` describe?",
        "expect": dict(NOCALL, output_contains=["2:30"], output_contains_any=["Monday through Friday", "Monday to Friday", "Monday-Friday", "weekday", "Mon-Fri", "Mon–Fri", "Monday–Friday"], max_output_chars=400),
    }],
    verify='''
import json

case = json.load(open("case.json"))
expr = case["turns"][0]["prompt"].split("`")[1].split()
minute, hour, dom, month, dow = expr
assert (minute, hour, dom, month, dow) == ("30", "2", "*", "*", "1-5")
words = ["Monday through Friday", "Monday to Friday", "Monday-Friday", "weekday", "Mon-Fri", "Mon\\u2013Fri", "Monday\\u2013Friday"]
print(json.dumps({"expected_contains_any": words}))
''',
    notes='''
## Traps
- None. A stable-fact question; the user says no files are needed.

## Reference solution
No tool call. Answer in 1-2 sentences: it runs at 02:30 (2:30 AM, in the cron daemon's timezone) every Monday through Friday; fields are minute 30, hour 2, any day of month, any month, days of week 1-5. Criteria: zero calls, contains 2:30 and a Monday-to-Friday phrase.

## Why the answer is unique
Standard five-field cron syntax: minute, hour, day of month, month, day of week, where 1-5 is Monday to Friday.
''',
)

# ---------------------------------------------------------------- tab-8004
rng = random.Random(80044)
def diff_rows(n, seed_shift):
    r = random.Random(80044 + seed_shift)
    out = []
    for i in range(n):
        kind = r.choice(["盘亏", "盘盈", "盘亏", "一致"])
        amt = "0.00" if kind == "一致" else "%.2f" % r.uniform(15, 980)
        out.append(("SKU-%05d" % (21000 + i * 7), r.choice(["A区", "B区", "C区"]), kind, amt))
    return out
final = diff_rows(86, 1)
first = diff_rows(86, 2)
q2 = diff_rows(70, 3)
loss = round(sum(float(r[3]) for r in final if r[2] == "盘亏"), 2)
csvf = lambda rows: "SKU,库区,差异类型,差异金额\n" + "".join(",".join(x) + "\n" for x in rows)
write_case(
    "tab-8004",
    desc="Turn 1 asks for a stocktake loss total but says the user will name which of several difference sheets to use and the assistant must ask first; turn 2 names the file",
    task_type="aggregate", family="fam-tab-b10-stocktakeloss-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "盘点/2026Q3-差异.csv": csvf(final),
        "盘点/2026Q3-差异-初盘.csv": csvf(first),
        "盘点/2026Q2-差异.csv": csvf(q2),
        "盘点/说明.md": "差异金额为正数，方向看「差异类型」列。初盘表是复盘前的版本。\n",
    },
    turns=[
        {"prompt": "帮我算一下这次盘点的盘亏总金额。差异表有好几版，用哪一份我来告诉你——你先问我，别自己去翻。",
         "expect": dict(NOCALL, output_contains_any=["哪一份", "哪份", "哪个文件", "哪一个文件", "文件名", "路径"], max_output_chars=300)},
        {"prompt": "用 盘点/2026Q3-差异.csv，这是复盘后的终版。",
         "expect": {"output_contains_any": [("%.2f" % loss).rstrip("0").rstrip("."), "{:,.2f}".format(loss).rstrip("0").rstrip(".")], "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
for path in ("盘点/2026Q2-差异.csv", "盘点/2026Q3-差异-初盘.csv", "盘点/2026Q3-差异.csv"):
    assert case["files"][path].startswith("SKU,库区,差异类型,差异金额"), path
rows = list(csv.DictReader(io.StringIO(case["files"]["盘点/2026Q3-差异.csv"])))
loss = round(sum(float(r["差异金额"]) for r in rows if r["差异类型"] == "盘亏"), 2)
forms = [("%.2f" % loss).rstrip("0").rstrip("."), "{:,.2f}".format(loss).rstrip("0").rstrip(".")]
ask = ["哪一份", "哪份", "哪个文件", "哪一个文件", "文件名", "路径"]
print(json.dumps({"expected_contains_any": ask + forms}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户说明会指定文件、要求先问；第 2 轮给出文件后正常计算。

## Reference solution
第 1 轮不调用工具，一句问句点名缺的参数，例如「要用哪一份差异表？请给我文件名或路径。」
第 2 轮：用 data_query 对 盘点/2026Q3-差异.csv 按 差异类型=盘亏 求和 差异金额，得 %s 元。终答一句话：终版差异表里盘亏合计 %s 元（差异金额按「盘亏」类型汇总）。判据：第 1 轮零调用并问到文件；第 2 轮包含 %s。

## Why the answer is unique
第 2 轮指定了终版表；金额列为正数、方向由 差异类型 决定，盘亏行求和即为答案。初盘表和 Q2 表是别的版本。
''' % ("%.2f" % loss, "%.2f" % loss, "%.2f" % loss),
)

# ---------------------------------------------------------------- log-8003
rng = random.Random(80055)
lines = []
t = 8 * 3600
fivexx = 0
while t < 11 * 3600:
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    status = rng.choice([200, 200, 200, 200, 201, 304, 404, 500, 502, 503, 200, 200])
    path = rng.choice(["/v1/orders", "/v1/items", "/v1/cart", "/v1/login"])
    lines.append("2026-09-15 %02d:%02d:%02d +0800 GET %s %d %dms" % (h, m, s, path, status, rng.randint(8, 900)))
    if h == 9 and status >= 500:
        fivexx += 1
    t += rng.randint(60, 200)
write_case(
    "log-8003",
    desc="Turn 1 asks to count 5xx responses but says the time range will be given and to ask first without calling tools; turn 2 gives 09:00-10:00",
    task_type="count_events", family="fam-log-b10-fivexxwindow-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "logs/api-gw/2026-09-15.log": "\n".join(lines) + "\n",
        "README.md": "API 网关访问日志，时间为北京时间，字段：日期 时间 时区 方法 路径 状态码 耗时。\n",
    },
    turns=[
        {"prompt": "帮我数一下 9 月 15 日 API 网关日志里 5xx 的次数。具体统计哪个时间段我还没定，你先问我，先别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["时间段", "几点", "起止", "时间范围", "哪段时间", "从几点"], max_output_chars=300)},
        {"prompt": "就统计上午 9 点到 10 点，含 9 点整，不含 10 点。",
         "expect": {"output_contains": [str(fivexx)], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
n = 0
for line in case["files"]["logs/api-gw/2026-09-15.log"].splitlines():
    assert re.match(r"^2026-09-15 \\d\\d:\\d\\d:\\d\\d \\+0800 GET /v1/", line), line
    parts = line.split()
    if parts[1].startswith("09:") and parts[5].startswith("5"):
        n += 1
print(json.dumps({"expected_number": n}))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问时间段、不调用工具。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要统计哪个时间段？请给我起止时间。」
第 2 轮：读 logs/api-gw/2026-09-15.log（或按状态码搜索），统计 09:00:00–09:59:59 之间状态码为 5xx（500/502/503）的行：%d 次。终答一句话写明时间段和次数。判据：第 1 轮零调用并问到时间段；第 2 轮包含 %d。

## Why the answer is unique
时间段在第 2 轮给定为 [09:00, 10:00)，状态码字段固定在第 7 列，5xx 只有 500、502、503 三种取值，计数唯一。
''' % (fivexx, fivexx),
)

# ---------------------------------------------------------------- cfg-8004
envs = {"dev": 8, "staging": 24, "production": 64, "dr": 16}
files = {"config/database.yaml": "database:\n  driver: postgres\n  pool_size: 10\n  statement_timeout_ms: 30000\n",
         "README.md": "Shared defaults live in config/database.yaml; config/env/<name>.yaml overrides them per environment.\n"}
for name, size in envs.items():
    files["config/env/%s.yaml" % name] = "database:\n  host: pg-%s.internal\n  pool_size: %d\n" % (name, size)
write_case(
    "cfg-8004",
    desc="Turn 1 asks for pool sizes of two environments but says the user will name them and the assistant should ask first; turn 2 names staging and dr",
    task_type="read_effective", family="fam-cfg-b10-poolsizepair-01", level="L0", ref_calls=2,
    axes=["DEC"],
    files=files,
    turns=[
        {"prompt": "I need the database connection pool sizes for two of our environments side by side. I'll tell you which two; ask me first and hold off on looking anything up.",
         "expect": dict(NOCALL, output_contains_any=["which two", "Which two", "which environments", "Which environments", "which environment", "Which environment"], max_output_chars=300)},
        {"prompt": "Staging and dr.",
         "expect": {"output_contains": ["24", "16"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("Shared defaults live in config/database.yaml")
sizes = {}
for env in ("staging", "dr"):
    sizes[env] = int(re.search(r"pool_size: (\\d+)", f["config/env/%s.yaml" % env]).group(1))
print(json.dumps({"expected_number": sizes["staging"]}))
''',
    notes='''
## Traps
- None. Turn 1 asks the assistant to wait for the environment names.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two environments should I compare?"
Turn 2: read config/env/staging.yaml and config/env/dr.yaml: pool_size 24 and 16, both overriding the shared default of 10. Final answer in one sentence: staging uses 24 connections and dr uses 16. Criteria: turn 1 zero-call and asks which environments; turn 2 contains 24 and 16 as whole tokens.

## Why the answer is unique
Both environment files set pool_size explicitly, so the shared default 10 does not apply; the values are 24 (staging) and 16 (dr).
''',
)
