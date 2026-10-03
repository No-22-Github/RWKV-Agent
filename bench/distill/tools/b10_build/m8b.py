"""M8 (v1.4 §3.8) pilot, part B: read inputs from the workspace or web, then compute with the calculator."""
import json as _json
import random
from common import write_case

CALC = ["calculator"]

def sforms(x, nd=2):
    a = ("%.*f" % (nd, x)).rstrip("0").rstrip(".")
    b = "{:,.{}f}".format(x, nd).rstrip("0").rstrip(".")
    return sorted({a, b})

# ---------------------------------------------------------------- tab-8014
rng = random.Random(80314)
rows = []
for i in range(60):
    rows.append(("BX-%05d" % (91000 + i), rng.choice(["市场部", "销售部", "研发部"]), "%.2f" % rng.uniform(88, 2400)))
mk = round(sum(float(r[2]) for r in rows if r[1] == "市场部"), 2)
ded = round(mk * 0.94, 2)
write_case(
    "tab-8014",
    desc="Sum one department's travel claims and apply a non-deductible share stated in the README, then compute the deductible amount",
    task_type="policy_calc", family="fam-tab-b10-deductible-01", level="L1", ref_calls=3,
    traps=["TR-RULEFILE"], decoys={"TR-RULEFILE": "%.2f" % mk}, axes=["CHN"],
    files={"差旅/2026-09-报销.csv": "报销单号,部门,金额\n" + "".join(",".join(r) + "\n" for r in rows),
           "README.md": "# 差旅报销\n\n财务口径：每笔报销中 6% 视为不可抵扣部分（含个人消费与无票部分），可抵扣金额 = 报销金额 × 94%。\n"},
    turns=[{"prompt": "9 月市场部的差旅报销里，可抵扣的金额一共多少元？保留两位小数。",
            "expect": {"output_contains_any": sforms(ded), "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
assert "94%" in case["files"]["README.md"]
rows = list(csv.DictReader(io.StringIO(case["files"]["差旅/2026-09-报销.csv"])))
d = round(round(sum(float(r["金额"]) for r in rows if r["部门"] == "市场部"), 2) * 0.94, 2)
s = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % d), s("{:,.2f}".format(d))})}))
''',
    notes='''
## Traps
- TR-RULEFILE: 可抵扣比例只写在 README（报销金额 × 94%%）。不读 README 直接报市场部合计 %.2f 就错了。

## Reference solution
1. 读 README.md：可抵扣 = 报销金额 × 94%%。
2. data_query：差旅/2026-09-报销.csv，filter {"部门":"市场部"}，sum 金额 → %.2f。
3. calculator：%.2f * 0.94，precision 2 → %.2f。
终答一句话：市场部 9 月报销合计 %.2f 元，按 94%% 可抵扣口径为 %.2f 元。判据：包含 %.2f（可去尾零/带千分位），调用过 calculator。

## Why the answer is unique
部门过滤精确，比例由 README 给定。
''' % (mk, mk, mk, ded, mk, ded, ded),
)

# ---------------------------------------------------------------- tab-8015
fx = {"month": "2026-09", "EUR_CNY": 7.8342, "USD_CNY": 7.1186, "GBP_CNY": 9.3021}
inv = [("EU-2209", "EUR", "1840.00"), ("US-1187", "USD", "2310.50"), ("EU-2214", "EUR", "965.40"), ("EU-2231", "EUR", "3127.75"), ("UK-0412", "GBP", "780.00")]
eur = sum(float(r[2]) for r in inv if r[1] == "EUR")
cny = round(eur * fx["EUR_CNY"], 2)
write_case(
    "tab-8015",
    desc="Convert the EUR invoices of a month to CNY with the month's rate file and total them; the file also holds USD and GBP rates",
    task_type="policy_calc", family="fam-tab-b10-eurcny-01", level="L1", ref_calls=3,
    traps=["TR-DECOY"], decoys={"TR-DECOY": "%.2f" % round(eur * fx["USD_CNY"], 2)}, axes=["OBS"],
    files={"rates/fx-2026-09.json": _json.dumps(fx, indent=2) + "\n",
           "invoices/sept.csv": "invoice,currency,amount\n" + "".join(",".join(r) + "\n" for r in inv),
           "README.md": "Month-end FX: convert foreign invoices with that month's rates file (units of CNY per 1 unit of currency).\n"},
    turns=[{"prompt": "Convert our September euro invoices to CNY using the month's rates file and give me the CNY total.",
            "expect": {"output_contains_any": sforms(cny), "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
fx = json.loads(case["files"]["rates/fx-2026-09.json"])
rows = list(csv.DictReader(io.StringIO(case["files"]["invoices/sept.csv"])))
c = round(sum(float(r["amount"]) for r in rows if r["currency"] == "EUR") * fx["EUR_CNY"], 2)
s = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % c), s("{:,.2f}".format(c))})}))
''',
    notes='''
## Traps
- TR-DECOY: the rates file also has USD_CNY 7.1186 and GBP_CNY; using the USD rate on the euro total gives %.2f.

## Reference solution
1. Read invoices/sept.csv: EUR invoices EU-2209 1840.00, EU-2214 965.40, EU-2231 3127.75 (total %.2f EUR).
2. Read rates/fx-2026-09.json: EUR_CNY 7.8342.
3. calculator: (1840.00 + 965.40 + 3127.75) * 7.8342, precision 2 = %.2f.
Final answer, one sentence: the three September EUR invoices (EUR %.2f) come to CNY %.2f at 7.8342. Criteria: contains the CNY total (trailing zero and thousands separator optional); calculator used.

## Why the answer is unique
Three rows are EUR; the file gives one EUR_CNY rate for the month.
''' % (round(eur * fx["USD_CNY"], 2), eur, cny, eur, cny),
)

# ---------------------------------------------------------------- hyb-8005
adj = round(4860 * 1.023, 2)
write_case(
    "hyb-8005",
    desc="Inflate last year's average purchase price by the official year-over-year CPI from the statistics bureau page, then compute with the calculator",
    task_type="web_then_calc", family="fam-hyb-b10-cpiadjust-01", level="L0", ref_calls=3, axes=[], version=2,
    web=[{"query_match": "cpi", "url_match": "stats.example.gov.cn/cpi/2026-08", "url": "https://stats.example.gov.cn/cpi/2026-08",
          "title": "2026 年 8 月居民消费价格指数（CPI）", "snippet": "8 月全国居民消费价格同比上涨 2.3%。",
          "content": "# 2026 年 8 月居民消费价格指数\n\n发布日期 2026-09-09。8 月份，全国居民消费价格同比上涨 2.3%，环比上涨 0.2%。\n", "published_at": "2026-09-09"}],
    files={"采购/均价.md": "2025 年 8 月 办公耗材采购均价：4860 元/批。\n\n（按批次加权，含税。）\n"},
    turns=[{"prompt": "把 2025 年 8 月的办公耗材采购均价按 2026 年 8 月 CPI 的同比涨幅调整一下，换算到今年 8 月的水平是多少元？保留两位小数。",
            "expect": {"output_contains_any": sforms(adj), "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import json
import re

case = json.load(open("case.json"))
base = float(re.search(r"(\\d+) 元/批", case["files"]["采购/均价.md"]).group(1))
cpi = float(re.search(r"同比上涨 ([\\d.]+)%", case["web_fixture"][0]["content"]).group(1))
v = round(base * (1 + cpi / 100), 2)
s = lambda x: x.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({s("%.2f" % v), s("{:,.2f}".format(v))})}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. 读 采购/均价.md：2025 年 8 月均价 4860 元/批。
2. 搜索并抓取统计局 2026 年 8 月 CPI 页面：同比上涨 2.3%%。
3. calculator：4860 * 1.023，precision 2 → %.2f。
终答一句话：按 8 月 CPI 同比 2.3%% 调整后约 %.2f 元/批（4860 × 1.023）。判据：包含 %.2f（可去尾零），调用过 calculator。官方统计页的搜索摘要已经给出同比 2.3%%，直接用摘要也可以，不强制抓取全文。

## Why the answer is unique
基数与涨幅各只有一个来源。

## Changelog
- v2：去掉 required_tools 里的 web_fetch。本题考的是计算器（M8），官方统计页的搜索摘要已写明同比 2.3%%，试跑里解题者凭摘要计算是合理路径。

## Five alternative phrasings of the task
1. 2026 年 8 月 CPI 同比
2. 国家统计局 8 月 CPI 2026
3. CPI 同比涨幅 2026年8月
4. 2026 August China CPI year on year
5. 居民消费价格指数 CPI 8 月
''' % (adj, adj, adj),
)

# ---------------------------------------------------------------- log-8009
from datetime import datetime, timedelta
rng = random.Random(80319)
t = datetime(2026, 9, 15, 3, 0, 0)
lines = ["%s INFO ingest job start source=s3://tidal-raw/2026-09-15/" % t.strftime("%Y-%m-%dT%H:%M:%SZ")]
events = 0
for i in range(18):
    t += timedelta(seconds=rng.randint(95, 180))
    n = rng.randint(8000, 16000)
    events += n
    lines.append("%s INFO batch %02d done events=%d" % (t.strftime("%Y-%m-%dT%H:%M:%SZ"), i + 1, n))
    if rng.random() < 0.3:
        lines.append("%s WARN slow partition p%d lag=%ds" % (t.strftime("%Y-%m-%dT%H:%M:%SZ"), rng.randint(0, 15), rng.randint(5, 40)))
dur = (t - datetime(2026, 9, 15, 3, 0, 0)).total_seconds()
eps = round(events / dur, 2)
write_case(
    "log-8009",
    desc="Average ingest throughput: total events over all batches divided by the seconds from job start to the last batch, rounded to two decimals",
    task_type="aggregate_jsonl", family="fam-log-b10-ingestrate-01", level="L0", ref_calls=3, axes=[],
    files={"logs/ingest-2026-09-15.log": "\n".join(lines) + "\n", "README.md": "Tidal ingest worker logs (UTC).\n"},
    turns=[{"prompt": "For the ingest run in logs/ingest-2026-09-15.log, what was the average throughput in events per second, counting from the job start to the last batch finishing? Round to two decimals.",
            "expect": {"output_contains": ["%.2f" % eps], "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import json
import re
from datetime import datetime

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Tidal ingest worker logs")
lines = case["files"]["logs/ingest-2026-09-15.log"].splitlines()
ts = lambda l: datetime.strptime(l.split()[0], "%Y-%m-%dT%H:%M:%SZ")
start = ts([l for l in lines if "job start" in l][0])
batches = [l for l in lines if " done events=" in l]
ev = sum(int(re.search(r"events=(\\d+)", l).group(1)) for l in batches)
print(json.dumps({"expected_number": round(ev / (ts(batches[-1]) - start).total_seconds(), 2)}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. Read logs/ingest-2026-09-15.log: job start 03:00:00Z, 18 batches, last at %s.
2. calculator: sum of the 18 events counts = %d.
3. calculator: %d / %d seconds, precision 2 = %.2f.
Final answer, one sentence: about %.2f events/s (%d events over %d s from job start to batch 18). Criteria: contains %.2f; calculator used.

## Why the answer is unique
The prompt fixes both endpoints of the interval and the event total is the sum of the batch counts.
''' % (t.strftime("%H:%M:%SZ"), events, events, dur, eps, eps, events, dur, eps),
)

# ---------------------------------------------------------------- cfg-8011
usable = round(12 * 8 * 7.68 / 3 * (1 - 0.15), 1)
write_case(
    "cfg-8011",
    desc="Usable capacity of a storage cluster from node, disk, replica and reserve settings, rounded to one decimal TB",
    task_type="read_effective", family="fam-cfg-b10-usablecapacity-01", level="L0", ref_calls=2, axes=[],
    files={"配置/存储集群.yaml": "集群: 澄江对象存储\n节点数: 12\n每节点盘数: 8\n单盘容量TB: 7.68\n副本数: 3\n预留比例: 0.15   # 留给重建与扩容的空间\n",
           "README.md": "可用容量 = 节点数 × 每节点盘数 × 单盘容量 ÷ 副本数 × (1 − 预留比例)。\n"},
    turns=[{"prompt": "按 配置/存储集群.yaml 的设置，这个集群扣掉预留以后的可用容量是多少 TB？保留一位小数。",
            "expect": {"output_contains": ["%.1f" % usable], "required_tools": CALC, "max_output_chars": 300}}],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("可用容量")
c = {}
for l in case["files"]["配置/存储集群.yaml"].splitlines():
    k, v = l.split(":", 1)
    c[k.strip()] = v.split("#")[0].strip()
assert c["集群"] == "澄江对象存储"
v = int(c["节点数"]) * int(c["每节点盘数"]) * float(c["单盘容量TB"]) / int(c["副本数"]) * (1 - float(c["预留比例"]))
print(json.dumps({"expected_number": round(v, 1)}))
''',
    notes='''
## Traps
- None.

## Reference solution
1. 读 配置/存储集群.yaml：12 节点 × 8 盘 × 7.68 TB，3 副本，预留 0.15。
2. calculator：12 * 8 * 7.68 / 3 * (1 - 0.15)，precision 1 → %.1f。
终答一句话：可用容量约 %.1f TB（裸容量 737.28 TB ÷ 3 副本，再扣 15%% 预留）。判据：包含 %.1f，调用过 calculator。

## Why the answer is unique
公式在 README 给出，参数都在配置里。
''' % (usable, usable, usable),
)
