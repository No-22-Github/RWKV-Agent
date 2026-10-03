"""M6 (v1.4 §3.6) pilot, part B: join, threshold, mixed units, line location."""
import random
from common import write_case

MAXREAD = {"max_calls": {"read_file": 1}}

def money_forms(x):
    # data_query prints 1234.5 for 1234.50, so the trailing zero is optional;
    # the stripped form is a substring of the padded one.
    a = ("%.2f" % x).rstrip("0").rstrip(".")
    b = "{:,.2f}".format(x).rstrip("0").rstrip(".")
    return sorted({a, b})

# ---------------------------------------------------------------- tab-8011
rng = random.Random(80211)
cats = ["Accessories", "Bikes", "Clothing", "Components"]
items = []
for i in range(48):
    c = cats[i % 4]
    items.append(("SKU-%04d" % (3100 + i * 7), c, "%.2f" % rng.uniform(6, 90 if c == "Accessories" else 900)))
stock = []
for i in range(150):
    it = rng.choice(items)
    stock.append((it[0], rng.choice(["Leeds", "Bristol", "Glasgow"]), str(rng.randint(0, 60))))
price = {s: float(p) for s, c, p in items if c == "Accessories"}
total = round(sum(price[s] * int(q) for s, w, q in stock if s in price), 2)
qty_only = sum(int(q) for s, w, q in stock if s in price)
write_case(
    "tab-8011",
    desc="Value one category's stock at list price by joining a stock table (sku, warehouse, qty) to an item table (sku, category, price)",
    task_type="join", family="fam-tab-b10-stockvalue-01", level="L1", ref_calls=4,
    traps=["TR-MULTISRC"], decoys={"TR-MULTISRC": str(qty_only)}, axes=["CHN"],
    case_expect=MAXREAD,
    files={"catalog/items.csv": "sku,category,list_price\n" + "".join(",".join(r) + "\n" for r in items),
           "inventory/stock.csv": "sku,warehouse,qty\n" + "".join(",".join(r) + "\n" for r in stock),
           "README.md": "Pedalworks UK inventory. A SKU can appear once per warehouse in stock.csv; prices are in GBP.\n"},
    turns=[{
        "prompt": "What is the total list-price value of our Accessories stock across all warehouses, in GBP?",
        "expect": {"output_contains_any": money_forms(total), "required_tools": ["data_query"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
price = {r["sku"]: float(r["list_price"]) for r in csv.DictReader(io.StringIO(f["catalog/items.csv"])) if r["category"] == "Accessories"}
total = round(sum(price[r["sku"]] * int(r["qty"]) for r in csv.DictReader(io.StringIO(f["inventory/stock.csv"])) if r["sku"] in price), 2)
strip = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({strip("%.2f" % total), strip("{:,.2f}".format(total))})}))
''',
    notes='''
## Traps
- TR-MULTISRC: stock.csv has no category or price, catalog/items.csv has no quantities; using one file alone cannot give the value (summing Accessories quantities alone gives %d units, not money).

## Reference solution
1. data_query catalog/items.csv with filter {"category": "Accessories"}, select sku,list_price: 12 SKUs.
2. data_query inventory/stock.csv grouped by sku, operation sum, field qty.
3. calculator: sum of qty x list_price over the 12 Accessories SKUs = %s.
4. (Optional) README for currency.
Final answer, 1-2 sentences: Accessories stock is worth GBP %s at list price across Leeds, Bristol and Glasgow (quantities from inventory/stock.csv times prices from catalog/items.csv). Criteria: contains the total in either plain or comma form; data_query used; at most one read_file.

## Why the answer is unique
Each SKU has one price and one category; summing qty x price over the Accessories SKUs gives a single total.
''' % (qty_only, "%.2f" % total, "{:,.2f}".format(total)),
)

# ---------------------------------------------------------------- tab-8012
rng = random.Random(80212)
po = []
for i in range(160):
    q = rng.randint(1, 40)
    p = rng.choice([12.5, 18.8, 23.6, 36.4, 41.9, 58.2])
    po.append(("CG-%05d" % (72000 + i), rng.choice(["恒信五金", "明川包装", "锦泰化工", "南溪纸业"]), str(q), "%.1f" % p, "%.2f" % (q * p)))
ge20 = round(sum(float(r[4]) for r in po if int(r[2]) >= 20), 2)
gt20 = round(sum(float(r[4]) for r in po if int(r[2]) > 20), 2)
write_case(
    "tab-8012",
    desc="Sum the amount of September purchase orders whose quantity is at least 20; the boundary value 20 is included",
    task_type="filter_count", family="fam-tab-b10-bulkpo-01", level="L1", ref_calls=2,
    traps=["TR-DEFN"], decoys={"TR-DEFN": "%.2f" % gt20}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"采购/2026-09-采购单.csv": "单号,供应商,数量,单价,金额\n" + "".join(",".join(r) + "\n" for r in po),
           "README.md": "# 采购单明细\n\n金额 = 数量 × 单价，单位元。\n"},
    turns=[{
        "prompt": "9 月单笔采购数量不少于 20 件的采购单，金额一共是多少元？",
        "expect": {"output_contains_any": money_forms(ge20), "required_tools": ["data_query"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
rows = list(csv.DictReader(io.StringIO(case["files"]["采购/2026-09-采购单.csv"])))
s = round(sum(float(r["金额"]) for r in rows if int(r["数量"]) >= 20), 2)
strip = lambda v: v.rstrip("0").rstrip(".")
print(json.dumps({"expected_contains_any": sorted({strip("%.2f" % s), strip("{:,.2f}".format(s))})}))
''',
    notes='''
## Traps
- TR-DEFN: 「不少于 20 件」含 20。按「多于 20」算会漏掉数量正好 20 的单，得 %.2f。

## Reference solution
1. data_query：path 采购/2026-09-采购单.csv，group_by 数量，operation sum，field 金额（data_query 只能按等值过滤，按数量分组后再挑 ≥20 的组）。
2. 用计算器把数量 20–40 各组的金额加起来：%.2f 元。
终答 1–2 句：数量不少于 20 件（含 20）的采购单金额合计 %.2f 元。判据：包含该金额（带或不带千分位）；用过 data_query；read_file 最多 1 次。

## Why the answer is unique
金额列已按数量×单价给出，按数量 ≥20 过滤后求和唯一。
''' % (gt20, ge20, ge20),
)

# ---------------------------------------------------------------- tab-8013
rng = random.Random(80213)
runs = []
secs = []
for i in range(34):
    v = rng.choice([rng.randint(420, 990), round(rng.uniform(1.0, 4.8), 1)])
    if isinstance(v, int):
        runs.append(("exp-%03d" % (500 + i), "2026-09-%02d" % rng.randint(1, 30), "%dms" % v)); secs.append(v / 1000)
    else:
        runs.append(("exp-%03d" % (500 + i), "2026-09-%02d" % rng.randint(1, 30), "%.1fs" % v)); secs.append(v)
avg = round(sum(secs) / len(secs), 2)
naive = round(sum(float(r[2].rstrip("ms").rstrip("s")) for r in runs) / len(runs), 2)
write_case(
    "tab-8013",
    desc="Average the elapsed time of export runs when the column mixes millisecond and second values with unit suffixes",
    task_type="aggregate", family="fam-tab-b10-elapsedunits-01", level="L1", ref_calls=3,
    traps=["TR-NUMFMT"], decoys={"TR-NUMFMT": "%.2f" % naive}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"jobs/export-runs.csv": "run_id,date,elapsed\n" + "".join(",".join(r) + "\n" for r in runs),
           "README.md": "Nightly export runs for Corvane Analytics. The runner logs elapsed as written by two different versions of the exporter.\n"},
    turns=[{
        "prompt": "What was the average elapsed time of the September export runs, in seconds rounded to two decimals?",
        "expect": {"output_contains": ["%.2f" % avg], "required_tools": ["calculator"], "max_output_chars": 400},
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Nightly export runs for Corvane Analytics")
vals = []
for r in csv.DictReader(io.StringIO(case["files"]["jobs/export-runs.csv"])):
    e = r["elapsed"]
    vals.append(float(e[:-2]) / 1000 if e.endswith("ms") else float(e[:-1]))
print(json.dumps({"expected_number": round(sum(vals) / len(vals), 2)}))
''',
    notes='''
## Traps
- TR-NUMFMT: elapsed mixes "940ms" and "1.6s". data_query cannot average these strings (it errors on non-numeric values), and stripping the suffixes without converting gives %.2f.

## Reference solution
1. data_query on jobs/export-runs.csv selecting elapsed (34 rows), or one read_file.
2. Convert ms values to seconds and sum with the calculator, then divide by 34: %.2f s.
3. (A failed data_query avg with the "not numeric" error is an acceptable first step.)
Final answer, 1-2 sentences: average %.2f seconds over 34 runs, after converting the millisecond entries to seconds. Criteria: contains %.2f; calculator used; at most one read_file.

## Why the answer is unique
Every value has an explicit unit; converting to seconds and averaging the 34 runs gives one number.
''' % (naive, avg, avg, avg),
)

# ---------------------------------------------------------------- code-8003
rng = random.Random(80214)
src = ['"""Tariff tables for the regional freight calculator."""', "", "import csv", "import io", "", "", "# load_tariff_table 的旧实现已迁到 legacy/tariff_v1.py，这里保留新版。", ""]
names = ["zone_code", "weight_band", "fuel_surcharge", "remote_fee", "pallet_rate", "volumetric_weight", "minimum_charge", "holiday_factor",
         "customs_fee", "insurance_rate", "cold_chain_fee", "oversize_fee", "return_rate", "cod_fee", "dangerous_goods_fee"]
target_line = None
for i in range(60):
    n = names[i % len(names)] + "_%02d" % i
    if i == 37:
        src += ["", "", "def load_tariff_table(text):"]
        target_line = len(src)
        src += ['    """Parse a tariff CSV into {(zone, band): rate}."""', "    table = {}", "    for row in csv.DictReader(io.StringIO(text)):",
                "        table[(row[\"zone\"], row[\"band\"])] = float(row[\"rate\"])", "    return table"]
    src += ["", "", "def %s(value, rate=%.3f):" % (n, rng.uniform(0.5, 3)), "    if value is None:", "        return 0.0",
            "    base = float(value) * rate", "    if base < %d:" % rng.randint(1, 30), "        return round(base, 2)", "    return round(base * %.2f, 2)" % rng.uniform(0.8, 1.2)]
src += ["", "", "def quote(text, zone, band):", "    return load_tariff_table(text)[(zone, band)]", ""]
code = "\n".join(src)
write_case(
    "code-8003",
    desc="Report the line number where a function is defined in a long module; a comment and a call site mention the same name",
    task_type="locate_definition", family="fam-code-b10-tariffdef-01", level="L1", ref_calls=1,
    traps=["TR-DECOY"], decoys={"TR-DECOY": 7}, axes=["OBS"],
    case_expect=MAXREAD,
    files={"billing/tariff.py": code, "README.md": "区域货运报价服务。\n"},
    turns=[{
        "prompt": "load_tariff_table 这个函数是在 billing/tariff.py 第几行定义的？",
        "expect": {"output_contains": [str(target_line)], "output_contains_token": True, "max_output_chars": 300},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("区域货运报价服务")
lines = case["files"]["billing/tariff.py"].splitlines()
print(json.dumps({"expected_number": [i + 1 for i, l in enumerate(lines) if l.startswith("def load_tariff_table(")][0]}))
''',
    notes='''
## Traps
- TR-DECOY: 第 7 行是提到 load_tariff_table 的注释，文件末尾 quote() 里还有一处调用；都不是定义。

## Reference solution
1. search_text 搜「def load_tariff_table」（path billing/tariff.py），结果带行号：第 %d 行。
终答一句话：load_tariff_table 定义在 billing/tariff.py 第 %d 行（第 7 行的注释和 quote() 里的调用都不是定义）。判据：包含 %d（独立词元）；read_file 最多 1 次。

## Why the answer is unique
文件里只有一行以 def load_tariff_table( 开头。
''' % (target_line, target_line, target_line),
)

# ---------------------------------------------------------------- log-8008
rng = random.Random(80215)
lines = []
first = None
for i in range(1500):
    hh, mm, ss = divmod(i * 23, 3600)[0] % 24, (i * 23 // 60) % 60, (i * 23) % 60
    stamp = "2026-09-15T%02d:%02d:%02dZ" % (2 + hh, mm, ss)
    if i in (911, 1204, 1377):
        f = {911: "warehouse/exports/sku-feed-0915.parquet", 1204: "warehouse/exports/price-feed-0915.parquet", 1377: "warehouse/exports/sku-feed-0915.parquet"}[i]
        lines.append("%s ERROR sync-worker checksum mismatch file=%s expected=%08x got=%08x" % (stamp, f, rng.getrandbits(32), rng.getrandbits(32)))
        if first is None:
            first = (i + 1, f)
    elif i == 402:
        lines.append("%s WARN sync-worker checksum retry scheduled file=warehouse/exports/stock-feed-0915.parquet" % stamp)
    else:
        lines.append("%s INFO sync-worker copied file=warehouse/exports/part-%05d.parquet bytes=%d" % (stamp, i, rng.randint(10000, 900000)))
text = "\n".join(lines) + "\n"
assert len(text.encode()) > 65536
write_case(
    "log-8008",
    desc="Give the line number and file of the first checksum mismatch in a sync log larger than read_file's limit; a WARN line mentions checksums earlier",
    task_type="locate_error", family="fam-log-b10-checksumline-01", level="L2", ref_calls=1,
    traps=["TR-TRUNC", "TR-DECOY"], decoys={"TR-TRUNC": "UNKNOWN", "TR-DECOY": 403}, axes=["LNG", "OBS"],
    case_expect=MAXREAD,
    files={"logs/sync-worker.log": text, "README.md": "Warehouse export sync worker. One log per day.\n"},
    turns=[{
        "prompt": "On which line of logs/sync-worker.log does the first checksum mismatch appear, and which file did it involve?",
        "expect": {"output_contains": [str(first[0]), first[1]], "output_contains_token": True, "max_output_chars": 400},
    }],
    verify='''
import json

case = json.load(open("case.json"))
assert case["files"]["README.md"].startswith("Warehouse export sync worker")
lines = case["files"]["logs/sync-worker.log"].splitlines()
n = next(i + 1 for i, l in enumerate(lines) if "checksum mismatch" in l)
print(json.dumps({"expected_number": n}))
''',
    notes='''
## Traps
- TR-TRUNC: the log is about 110 KB, beyond read_file's 64 KiB, so a single read stops before line %d.
- TR-DECOY: line 403 is a WARN about a checksum retry, not a mismatch.

## Reference solution
1. search_text for "checksum mismatch" in logs/sync-worker.log: matches at lines %d, 1205 and 1378.
Final answer, one sentence: the first checksum mismatch is on line %d and involves %s. Criteria: contains %d (whole token) and the file path; at most one read_file.

## Why the answer is unique
"checksum mismatch" first appears on that line; the earlier checksum line is a retry WARN.
''' % (first[0], first[0], first[0], first[1], first[0]),
)
