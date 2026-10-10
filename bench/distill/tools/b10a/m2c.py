"""M2 (v1.4 §3.2) b10a batch: target absent with a near-match decoy, 26 cases.

Scaled from the b10 pilot (bench/distill/tools/b10/m2a.py, m2b.py); case shape,
fixture layout, verify style and NOTES format follow tab-8001 / web-8001 /
code-8001. Themes: zh -- flower wholesale markets and bridge upkeep; en --
e-bike sharing. Run: cd bench/distill/tools/b10a && python3 m2c.py
"""
import random

from common import revised

write_case = revised({'web-8017': '题面补上品牌名 Velofleet：原题面没有任何能命中网页 fixture 的名字，三遍老师都搜不到，题目缺陷。', 'web-8019': '题面补上品牌名 Saddleline：原题面搜不到网页 fixture，题目缺陷。'})

NEG_ZH = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没"]
NEG_EN = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
          "not in the", "not on the", "no row", "missing", "not covered"]

TAB_VERIFY_TMPL = '''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
assert files[@L@].splitlines()[0] == @HDR@
assert files[@S@].splitlines()[0] == @SHDR@
ledger = list(csv.DictReader(io.StringIO(files[@L@])))
status = list(csv.DictReader(io.StringIO(files[@S@])))
assert ledger and set(ledger[0]) == set(@HDR@.split(","))
assert not any(r[@GC@] == @T@ for r in ledger)
codes = {r[@NC@]: r for r in status}
row = codes[@T@]
assert row[@SC@] == @SV@ and @EV@ in row[@NT@]
decoy = sum(float(r[@VC@]) for r in ledger if r[@GC@] == @D@)
exp = case["turns"][0]["expect"]["output_excludes"]
@SPELL@
assert all(w in exp for w in want)
print(json.dumps({"expected_contains_any": @WORDS@}, ensure_ascii=False))
'''

CODE_VERIFY_TMPL = '''
import json
import re

case = json.load(open("case.json"))
files = case["files"]
assert files["README.md"].splitlines()[0].startswith(@RP@)
assert files[@DP@].splitlines()[0] == @DF@
defs = set()
for path, text in files.items():
    if path.endswith(".py"):
        defs.update(re.findall(r"^def (\\w+)\\(", text, re.M))
        defs.update(re.findall(r"^class (\\w+)", text, re.M))
assert @T@ not in defs
assert @D@ in defs
print(json.dumps({"expected_contains_any": @WORDS@}, ensure_ascii=False))
'''


def money_rows(rng, prefix, n, groups, lo, hi):
    rows = []
    for i in range(n):
        day = rng.randint(1, 30)
        g = groups[i % len(groups)] if i % 7 else rng.choice(groups)
        rows.append(("%s-%04d" % (prefix, 9100 + i), "2026-09-%02d" % day, g,
                     "%.2f" % round(rng.uniform(lo, hi), 2)))
    rows.sort(key=lambda r: r[1])
    return rows


def count_rows(rng, groups, lo, hi):
    rows = []
    for d in range(1, 31):
        for g in groups:
            rows.append(("2026-09-%02d" % d, g, str(rng.randint(lo, hi))))
    return rows


def daily_money_rows(rng, groups, lo, hi):
    rows = []
    for d in range(1, 31):
        for g in groups:
            rows.append(("2026-09-%02d" % d, g, "%.2f" % round(rng.uniform(lo, hi), 2)))
    return rows


def ledger_csv(header, rows):
    return header + "\n" + "".join(",".join(r) + "\n" for r in rows)


def tab_verify(ledger_path, header, status_path, status_header, group_col, name_col, target,
               status_col, status_value, note_col, evidence, decoy_group, value_col, money,
               words):
    if money:
        spell = 'want = ["%.2f" % decoy, "{:,.2f}".format(decoy)]'
    else:
        spell = 'n = int(round(decoy))\nwant = [str(n), "{:,}".format(n)]'
    out = TAB_VERIFY_TMPL
    for key, value in (("@L@", ledger_path), ("@HDR@", header), ("@S@", status_path),
                       ("@SHDR@", status_header), ("@GC@", group_col), ("@T@", target),
                       ("@NC@", name_col), ("@SC@", status_col), ("@SV@", status_value),
                       ("@NT@", note_col), ("@EV@", evidence), ("@VC@", value_col),
                       ("@D@", decoy_group)):
        out = out.replace(key, repr(value))
    return out.replace("@SPELL@", spell).replace("@WORDS@", repr(words))


def code_verify(readme_prefix, doc_path, doc_first, target, decoy, words):
    out = CODE_VERIFY_TMPL
    for key, value in (("@DP@", doc_path), ("@RP@", readme_prefix), ("@DF@", doc_first),
                       ("@T@", target), ("@D@", decoy)):
        out = out.replace(key, repr(value))
    return out.replace("@WORDS@", repr(words))


def assert_clean(files, values):
    blob = "\n".join(files.values())
    for v in values:
        assert v not in blob, v


# ---------------------------------------------------------------- tab-8016
rng = random.Random(8016)
STALLS = ["玫瑰阁", "兰花坊", "菊苑", "竹里馆"]
rows = money_rows(rng, "TZ", 64, STALLS, 1200, 9800)
decoy = round(sum(float(r[3]) for r in rows if r[2] == "兰花坊"), 2)
out_csv = ledger_csv("订单号,日期,摊位,金额", rows)
codes_csv = ("编码,摊位,状态,说明\n"
             "MG1,玫瑰阁,在役,2026-09-01 起接收原兰花阁订单与库存\n"
             "LF2,兰花阁,撤销,2026-08-31 起撤销，订单与库存并入 玫瑰阁\n"
             "LF1,兰花坊,在役,\n"
             "JY1,菊苑,在役,\n"
             "ZL1,竹里馆,在役,\n")
readme = "# 晨露花卉批发市场 摊位流水台账\n\n台账/ 按月一个文件，金额单位为元。摊位名以 摊位/编码表.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_ZH + ["撤销", "并入", "合并"]
write_case(
    "tab-8016",
    desc="Asks September stall sales for a flower-market stall that was wound up in August; "
         "the code table says its orders merged into another stall and the ledger has a "
         "similarly named active stall",
    task_type="aggregate", family="fam-tab-b10-petalstall-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "台账/2026-09.csv": out_csv,
        "摊位/编码表.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "财务要核对晨露花卉批发市场兰花阁摊位 9 月的销售额，帮我算一下合计是多少。",
        "expect": {
            "output_contains": ["兰花阁"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("台账/2026-09.csv", "订单号,日期,摊位,金额", "摊位/编码表.csv",
                      "编码,摊位,状态,说明", "摊位", "摊位", "兰花阁", "状态", "撤销", "说明",
                      "玫瑰阁", "兰花坊", "金额", True, words),
    notes='''
## Traps
- TR-ABSENT: 台账/2026-09.csv 里没有「兰花阁」的行。摊位/编码表.csv 写明兰花阁 2026-08-31 起撤销，订单与库存并入 玫瑰阁。
- TR-DECOY: 台账里有名字相近的「兰花坊」，9 月合计 %s 元；把它当成兰花阁的销售额就是诱饵答案。

## Reference solution
1. 列出工作区：台账/2026-09.csv、摊位/编码表.csv、README.md。
2. 读（或按摊位分组）台账/2026-09.csv，摊位列只有玫瑰阁、兰花坊、菊苑、竹里馆。
3. 读 摊位/编码表.csv：兰花阁 8 月底撤销、并入玫瑰阁；兰花坊是另一个在役摊位。
终答（2–4 句）：9 月台账里没有兰花阁，因为它 8 月 31 日已撤销、订单与库存并入玫瑰阁，所以没有兰花阁 9 月的销售额可算；名字相近的兰花坊是另一个在役摊位，它的合计不是兰花阁的数。如果财务要的是原兰花阁那部分业务，可以改核玫瑰阁 9 月的数，要的话我来算。判据：包含「兰花阁」和一个撤销/并入说法，不得出现兰花坊的合计 %s。

## Why the answer is unique
兰花坊在编码表里是独立的在役摊位（LF1），和撤销的兰花阁（LF2）是两行，名字相近不是同一个摊位。编码表说明兰花阁在 9 月之前已撤销，台账里也确实没有它的行，所以「兰花阁 9 月销售额」在数据里不存在，只能说明原因并给出改核玫瑰阁的下一步。
''' % ("%.2f" % decoy, "%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8017
rng = random.Random(8017)
POINTS = ["中央配送点", "城西配送点", "东郊配送点"]
rows = count_rows(rng, POINTS, 45, 85)
decoy = sum(int(r[2]) for r in rows if r[1] == "城西配送点")
out_csv = ledger_csv("日期,配送点,件数", rows)
codes_csv = ("编码,配送点,状态,说明\n"
             "CP1,城西配送点,在役,\n"
             "CP2,城南配送点,停用,2026-08-31 起停用，配送任务并入 中央配送点\n"
             "CP3,中央配送点,在役,2026-09-01 起接收原城南配送点任务\n"
             "CP4,东郊配送点,在役,\n")
readme = "# 兰亭花卉市场 配送台账\n\n配送/ 按月一个文件，件数为鲜花包装件。配送点以 配送点/名录.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             [str(decoy), "{:,}".format(decoy)])
words = NEG_ZH + ["停用", "并入", "合并"]
write_case(
    "tab-8017",
    desc="Asks September parcel counts for a flower-market delivery point that was closed in "
         "August; the register says its rounds merged into the central point and the ledger has "
         "a similarly named active point",
    task_type="aggregate", family="fam-tab-b10-stemdrop-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(decoy)},
    axes=["DEC", "OBS"],
    files={
        "配送/2026-09.csv": out_csv,
        "配送点/名录.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "兰亭花卉市场 9 月城南配送点的配送件数合计是多少？月底结算要用。",
        "expect": {
            "output_contains": ["城南配送点"],
            "output_contains_any": words,
            "output_excludes": [str(decoy), "{:,}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("配送/2026-09.csv", "日期,配送点,件数", "配送点/名录.csv",
                      "编码,配送点,状态,说明", "配送点", "配送点", "城南配送点", "状态", "停用",
                      "说明", "中央配送点", "城西配送点", "件数", False, words),
    notes='''
## Traps
- TR-ABSENT: 配送/2026-09.csv 里没有「城南配送点」的行。配送点/名录.csv 写明城南配送点 2026-08-31 起停用，配送任务并入 中央配送点。
- TR-DECOY: 台账里有名字相近的「城西配送点」，9 月合计 %s 件；把它当成城南配送点的件数就是诱饵答案。

## Reference solution
1. 列出工作区：配送/2026-09.csv、配送点/名录.csv、README.md。
2. 读（或按配送点分组）配送/2026-09.csv，配送点列只有中央配送点、城西配送点、东郊配送点。
3. 读 配送点/名录.csv：城南配送点 8 月底停用、并入中央配送点；城西配送点是另一个在役配送点。
终答（2–4 句）：9 月配送台账里没有城南配送点，因为它 8 月 31 日已停用、配送任务并入中央配送点，所以没有城南配送点 9 月的件数可算；名字相近的城西配送点是另一个在役配送点，它的合计不是城南的数。月底结算要原城南业务的话，可以改核中央配送点 9 月的数，要的话我来算。判据：包含「城南配送点」和一个停用/并入说法，不得出现城西配送点的合计 %s。

## Why the answer is unique
城西配送点在名录里是独立的在役配送点（CP1），和停用的城南配送点（CP2）是两行，名字相近不是同一个点。名录说明城南配送点在 9 月之前已停用，台账里也确实没有它的行，所以「城南配送点 9 月件数」在数据里不存在，只能说明原因并给出改核中央配送点的下一步。
''' % (str(decoy), str(decoy)),
)

# ---------------------------------------------------------------- tab-8018
rng = random.Random(8018)
STORES = ["1号冷库", "13号冷库", "5号冷库"]
rows = count_rows(rng, STORES, 45, 150)
decoy = sum(int(r[2]) for r in rows if r[1] == "13号冷库")
out_csv = ledger_csv("日期,冷库,扎数", rows)
codes_csv = ("编码,冷库,状态,说明\n"
             "LK1,1号冷库,在役,2026-09-01 起接收原 3号冷库 周转库位\n"
             "LK3,3号冷库,停用,2026-08-25 起停用拆除，周转库位并入 1号冷库\n"
             "LK13,13号冷库,在役,\n"
             "LK5,5号冷库,在役,\n")
readme = "# 荷风花卉批发市场 冷链入库台账\n\n入库/ 按月一个文件，扎数为鲜切花标准扎。冷库以 冷库/编码表.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             [str(decoy), "{:,}".format(decoy)])
words = NEG_ZH + ["停用", "拆除", "并入"]
write_case(
    "tab-8018",
    desc="Asks September intake for a flower-market cold store that was demolished in August; "
         "the code table says its bays merged into another store and the ledger has a similarly "
         "numbered active store",
    task_type="aggregate", family="fam-tab-b10-coldbay-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(decoy)},
    axes=["DEC", "OBS"],
    files={
        "入库/2026-09.csv": out_csv,
        "冷库/编码表.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "荷风花卉批发市场 3号冷库 9 月的入库合计是多少扎？",
        "expect": {
            "output_contains": ["3号冷库"],
            "output_contains_any": words,
            "output_excludes": [str(decoy), "{:,}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("入库/2026-09.csv", "日期,冷库,扎数", "冷库/编码表.csv",
                      "编码,冷库,状态,说明", "冷库", "冷库", "3号冷库", "状态", "停用",
                      "说明", "1号冷库", "13号冷库", "扎数", False, words),
    notes='''
## Traps
- TR-ABSENT: 入库/2026-09.csv 里没有「3号冷库」的行。冷库/编码表.csv 写明 3号冷库 2026-08-25 起停用拆除，周转库位并入 1号冷库。
- TR-DECOY: 台账里有编号相近的「13号冷库」，9 月合计 %s 扎；把它当成 3号冷库的入库就是诱饵答案。

## Reference solution
1. 列出工作区：入库/2026-09.csv、冷库/编码表.csv、README.md。
2. 读（或按冷库分组）入库/2026-09.csv，冷库列只有 1号冷库、13号冷库、5号冷库。
3. 读 冷库/编码表.csv：3号冷库 8 月底停用拆除、库位并入 1号冷库；13号冷库是另一座在役冷库。
终答（2–4 句）：9 月入库台账里没有 3号冷库，因为它 8 月 25 日起停用拆除、周转库位并入 1号冷库，所以没有 3号冷库 9 月的入库可算；编号相近的 13号冷库是另一座在役冷库，它的扎数不是 3号冷库的数。要原 3号冷库存量的话可以改核 1号冷库，需要我来算就说一声。判据：包含「3号冷库」和一个停用/拆除/并入说法，不得出现 13号冷库的合计 %s。

## Why the answer is unique
13号冷库在编码表里是独立的在役冷库（LK13），和停用的 3号冷库（LK3）是两行，编号相近不是同一座库。编码表说明 3号冷库在 9 月之前已停用拆除，台账里也确实没有它的行，所以「3号冷库 9 月入库」在数据里不存在，只能说明原因并给出改核 1号冷库的下一步。
''' % (str(decoy), str(decoy)),
)

# ---------------------------------------------------------------- tab-8019
rng = random.Random(8019)
BRIDGES = ["滨江桥", "青石二桥", "白鹭桥"]
rows = money_rows(rng, "YH", 66, BRIDGES, 800, 6500)
decoy = round(sum(float(r[3]) for r in rows if r[2] == "青石二桥"), 2)
out_csv = ledger_csv("工单号,日期,桥梁,费用", rows)
codes_csv = ("编码,桥梁,状态,说明\n"
             "BJ1,滨江桥,在役,2026-09-01 起接收原青石桥日常养护工单\n"
             "QS1,青石桥,停用,2026-08-31 起移交市桥隧中心，日常养护工单并入 滨江桥\n"
             "QS2,青石二桥,在役,\n"
             "BL1,白鹭桥,在役,\n")
readme = "# 临江市市政设施 养护工单台账\n\n养护/ 按月一个文件，费用单位为元。桥梁名以 桥梁/编码表.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_ZH + ["停用", "移交", "并入"]
write_case(
    "tab-8019",
    desc="Asks September upkeep spend for a city bridge that was handed over in August; the "
         "code table says its work orders merged into another bridge and the ledger has a "
         "similarly named bridge",
    task_type="aggregate", family="fam-tab-b10-spanwork-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "养护/2026-09.csv": out_csv,
        "桥梁/编码表.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "临江市 9 月青石桥的日常养护费用合计是多少？",
        "expect": {
            "output_contains": ["青石桥"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("养护/2026-09.csv", "工单号,日期,桥梁,费用", "桥梁/编码表.csv",
                      "编码,桥梁,状态,说明", "桥梁", "桥梁", "青石桥", "状态", "停用", "说明",
                      "滨江桥", "青石二桥", "费用", True, words),
    notes='''
## Traps
- TR-ABSENT: 养护/2026-09.csv 里没有「青石桥」的工单。桥梁/编码表.csv 写明青石桥 2026-08-31 起移交市桥隧中心，日常养护工单并入 滨江桥。
- TR-DECOY: 台账里有名字相近的「青石二桥」，9 月合计 %s 元；把它当成青石桥的养护费就是诱饵答案。

## Reference solution
1. 列出工作区：养护/2026-09.csv、桥梁/编码表.csv、README.md。
2. 读（或按桥梁分组）养护/2026-09.csv，桥梁列只有滨江桥、青石二桥、白鹭桥。
3. 读 桥梁/编码表.csv：青石桥 8 月底停用移交、工单并入滨江桥；青石二桥是另一座在役桥。
终答（2–4 句）：9 月养护台账里没有青石桥的工单，因为它 8 月 31 日已停用移交市桥隧中心、日常养护工单并入滨江桥，所以没有青石桥 9 月的养护费可算；名字相近的青石二桥是另一座在役桥，它的费用不是青石桥的数。要原青石桥业务的话可以改核滨江桥 9 月的数，需要的话我来算。判据：包含「青石桥」和一个停用/移交/并入说法，不得出现青石二桥的合计 %s。

## Why the answer is unique
青石二桥在编码表里是独立的在役桥（QS2），和停用的青石桥（QS1）是两行，名字相近不是同一座桥。编码表说明青石桥在 9 月之前已移交，台账里也确实没有它的工单，所以「青石桥 9 月养护费」在数据里不存在，只能说明原因并给出改核滨江桥的下一步。
''' % ("%.2f" % decoy, "%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8020
rng = random.Random(8020)
BRIDGES = ["汇津大桥", "望江大桥", "龙爪桥"]
rows = money_rows(rng, "JC", 60, BRIDGES, 12000, 88000)
decoy = round(sum(float(r[3]) for r in rows if r[2] == "望江大桥"), 2)
out_csv = ledger_csv("单号,日期,桥梁,费用", rows)
codes_csv = ("编码,桥梁,状态,说明\n"
             "HJ1,汇津大桥,启用,2026-09-01 起接续原望江桥检测计划\n"
             "WJ1,望江桥,停用,2026-08-20 起拆除封桥，检测计划转入 汇津大桥\n"
             "WJ2,望江大桥,启用,\n"
             "LZ1,龙爪桥,启用,\n")
readme = "# 泸川市桥梁定期检测费用台账\n\n检测/ 按月一个文件，费用单位为元。桥梁名以 桥梁/编码表.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_ZH + ["停用", "拆除", "转入"]
write_case(
    "tab-8020",
    desc="Asks September inspection fees for a city bridge that was demolished in August; the "
         "code table says its schedule moved to a new bridge and the ledger has a similarly "
         "named bridge",
    task_type="aggregate", family="fam-tab-b10-girderfee-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "检测/2026-09.csv": out_csv,
        "桥梁/编码表.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "泸川市望江桥 9 月的定期检测费用合计是多少？",
        "expect": {
            "output_contains": ["望江桥"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("检测/2026-09.csv", "单号,日期,桥梁,费用", "桥梁/编码表.csv",
                      "编码,桥梁,状态,说明", "桥梁", "桥梁", "望江桥", "状态", "停用", "说明",
                      "汇津大桥", "望江大桥", "费用", True, words),
    notes='''
## Traps
- TR-ABSENT: 检测/2026-09.csv 里没有「望江桥」的记录。桥梁/编码表.csv 写明望江桥 2026-08-20 起拆除封桥，检测计划转入 汇津大桥。
- TR-DECOY: 台账里有名字相近的「望江大桥」，9 月合计 %s 元；把它当成望江桥的检测费就是诱饵答案。

## Reference solution
1. 列出工作区：检测/2026-09.csv、桥梁/编码表.csv、README.md。
2. 读（或按桥梁分组）检测/2026-09.csv，桥梁列只有汇津大桥、望江大桥、龙爪桥。
3. 读 桥梁/编码表.csv：望江桥 8 月 20 日起拆除封桥、检测计划转入汇津大桥；望江大桥是另一座在役桥。
终答（2–4 句）：9 月检测台账里没有望江桥的记录，因为它 8 月 20 日起拆除封桥、检测计划转入新建的汇津大桥，所以没有望江桥 9 月的检测费可算；名字相近的望江大桥是另一座在役桥，它的费用不是望江桥的数。要核对接续后的检测费用可以改核汇津大桥，需要的话我来算。判据：包含「望江桥」和一个停用/拆除/转入说法，不得出现望江大桥的合计 %s。

## Why the answer is unique
望江大桥在编码表里是独立的在役桥（WJ2），和拆除的望江桥（WJ1）是两行；接续检测计划的是汇津大桥（HJ1），编码表写明转入对象。台账里也确实没有望江桥的行，所以「望江桥 9 月检测费」在数据里不存在，只能说明原因并给出改核汇津大桥的下一步。
''' % ("%.2f" % decoy, "%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8021
rng = random.Random(8021)
BRIDGES = ["通济小桥", "洛水桥", "云溪桥"]
rows = money_rows(rng, "GZ", 60, BRIDGES, 600, 5200)
decoy = round(sum(float(r[3]) for r in rows if r[2] == "通济小桥"), 2)
out_csv = ledger_csv("工单号,日期,桥梁,费用", rows)
codes_csv = ("编码,桥梁,状态,说明\n"
             "TJ1,通济桥,封闭施工,2026-08-25 起全桥封闭施工，日常养护暂停，完工时间另行通知\n"
             "TJ2,通济小桥,在役,\n"
             "LS1,洛水桥,在役,\n"
             "YX1,云溪桥,在役,\n")
readme = "# 石门市桥梁养护工单台账\n\n养护/ 按月一个文件，费用单位为元。桥梁名以 桥梁/编码表.csv 为准。\n"
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_ZH + ["封闭", "暂停", "施工"]
write_case(
    "tab-8021",
    desc="Asks September upkeep spend for a city bridge closed for reconstruction; the code "
         "table says routine upkeep is suspended and the ledger has a similarly named small "
         "bridge",
    task_type="aggregate", family="fam-tab-b10-spanhalt-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "养护/2026-09.csv": out_csv,
        "桥梁/编码表.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "石门市通济桥 9 月的日常养护费用合计是多少？",
        "expect": {
            "output_contains": ["通济桥"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("养护/2026-09.csv", "工单号,日期,桥梁,费用", "桥梁/编码表.csv",
                      "编码,桥梁,状态,说明", "桥梁", "桥梁", "通济桥", "状态", "封闭施工",
                      "说明", "暂停", "通济小桥", "费用", True, words),
    notes='''
## Traps
- TR-ABSENT: 养护/2026-09.csv 里没有「通济桥」的工单。桥梁/编码表.csv 写明通济桥 2026-08-25 起全桥封闭施工，日常养护暂停，完工时间另行通知。
- TR-DECOY: 台账里有名字相近的「通济小桥」，9 月合计 %s 元；把它当成通济桥的养护费就是诱饵答案。

## Reference solution
1. 列出工作区：养护/2026-09.csv、桥梁/编码表.csv、README.md。
2. 读（或按桥梁分组）养护/2026-09.csv，桥梁列只有通济小桥、洛水桥、云溪桥。
3. 读 桥梁/编码表.csv：通济桥 8 月底起封闭施工、日常养护暂停；通济小桥是另一座在役桥。
终答（2–4 句）：9 月养护台账里没有通济桥的工单，因为它 8 月 25 日起全桥封闭施工、日常养护暂停，完工时间另行通知，所以没有通济桥 9 月的养护费可算；名字相近的通济小桥是另一座在役桥，它的费用不是通济桥的数。等通济桥恢复养护后我再帮你合计，或者先向施工方确认封闭期间的养护安排。判据：包含「通济桥」和一个封闭/暂停说法，不得出现通济小桥的合计 %s。

## Why the answer is unique
通济小桥在编码表里是独立的在役桥（TJ2），和封闭施工的通济桥（TJ1）是两行，名字相近不是同一座桥。编码表说明通济桥 9 月处于封闭施工、养护暂停状态，台账里也确实没有它的工单，所以「通济桥 9 月养护费」在数据里不存在，只能说明原因并给出恢复后再算或问施工方的下一步。
''' % ("%.2f" % decoy, "%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8022
rng = random.Random(8022)
STATIONS = ["Cannery Wharf North", "Old Harbour Steps", "Canal Street"]
rows = count_rows(rng, STATIONS, 35, 60)
decoy = sum(int(r[2]) for r in rows if r[1] == "Cannery Wharf North")
out_csv = ledger_csv("date,station,rides", rows)
codes_csv = ("station_id,station,status,note\n"
             "CW1,Cannery Wharf,removed,2026-08-31 taken out of service; docks redistributed "
             "to Cannery Wharf North and Canal Street\n"
             "CW2,Cannery Wharf North,active,\n"
             "CS1,Canal Street,active,\n"
             "OH1,Old Harbour Steps,active,\n")
readme = ("# Veloblitz harbour district ride log\n\n"
          "rides/ holds daily ride counts per station. Station names follow "
          "stations/stations.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             [str(decoy), "{:,}".format(decoy)])
words = NEG_EN + ["removed", "redistributed", "taken out of service", "decommissioned"]
write_case(
    "tab-8022",
    desc="Asks September ride counts for a bike-share station that was removed in August; the "
         "station register says its docks were redistributed and the ledger has a similarly "
         "named active station",
    task_type="aggregate", family="fam-tab-b10-dockrides-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(decoy)},
    axes=["DEC", "OBS"],
    files={
        "rides/2026-09.csv": out_csv,
        "stations/stations.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "Finance is reconciling September dock activity for the Cannery Wharf "
                  "station. How many rides started there in September?",
        "expect": {
            "output_contains": ["Cannery Wharf"],
            "output_contains_any": words,
            "output_excludes": [str(decoy), "{:,}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("rides/2026-09.csv", "date,station,rides", "stations/stations.csv",
                      "station_id,station,status,note", "station", "station", "Cannery Wharf",
                      "status", "removed", "note", "Cannery Wharf North", "Cannery Wharf North",
                      "rides", False, words),
    notes='''
## Traps
- TR-ABSENT: rides/2026-09.csv has no rows for Cannery Wharf. stations/stations.csv marks it removed on 2026-08-31, with docks redistributed to Cannery Wharf North and Canal Street.
- TR-DECOY: the ledger has the similarly named Cannery Wharf North with %s September rides; reporting that count as Cannery Wharf's is the decoy answer.

## Reference solution
1. List the workspace: rides/2026-09.csv, stations/stations.csv, README.md.
2. Read (or group) rides/2026-09.csv: stations are Cannery Wharf North, Canal Street and Old Harbour Steps only.
3. Read stations/stations.csv: Cannery Wharf was removed on August 31; Cannery Wharf North is a different, active station.
Final answer (2-4 sentences): The September ride log has no rides starting at Cannery Wharf: the station register marks it removed on August 31, with its docks redistributed to Cannery Wharf North and Canal Street. Cannery Wharf North is a different, active station, so its count is not the Cannery Wharf figure. If finance wants the relocated business, I can total Cannery Wharf North's September rides instead. Criteria: mentions Cannery Wharf and a removed/redistributed phrase; must not give Cannery Wharf North's count.

## Why the answer is unique
Cannery Wharf North is a separate active station (CW2) and the register lists the removed Cannery Wharf (CW1) as its own row, so the similar name is not the same station. The register dates the removal before September and the ledger has no Cannery Wharf rows, so the September count for Cannery Wharf does not exist in the data; the only defensible reply explains that and offers the successor station instead.
''' % str(decoy),
)

# ---------------------------------------------------------------- tab-8023
rng = random.Random(8023)
ZONES = ["Alder Park", "Birchfield", "Crane Meadow"]
rows = daily_money_rows(rng, ZONES, 40, 150)
decoy = round(sum(float(r[2]) for r in rows if r[1] == "Alder Park"), 2)
out_csv = ledger_csv("date,zone,revenue_eur", rows)
codes_csv = ("zone_id,zone,status,note\n"
             "AP1,Alder Park,active,receiving Alder Walk rides since 2026-09-01\n"
             "AW1,Alder Walk,merged,zones redrawn 2026-08-31; Alder Walk folded into Alder Park\n"
             "BZ1,Birchfield,active,\n"
             "CM1,Crane Meadow,active,\n")
readme = ("# Spokefield September ride revenue\n\n"
          "rides/ holds daily revenue per zone. Zone names follow zones/zones.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_EN + ["merged", "redrawn", "folded"]
write_case(
    "tab-8023",
    desc="Asks September ride revenue for a bike-share zone that was folded into another zone "
         "in August; the zone register records the redraw and the ledger has the successor zone",
    task_type="aggregate", family="fam-tab-b10-zonerev-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "rides/2026-09.csv": out_csv,
        "zones/zones.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "The zoning team is rebuilding the September ride report and asked for the "
                  "Alder Walk zone's ride revenue. What was it?",
        "expect": {
            "output_contains": ["Alder Walk"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("rides/2026-09.csv", "date,zone,revenue_eur", "zones/zones.csv",
                      "zone_id,zone,status,note", "zone", "zone", "Alder Walk", "status",
                      "merged", "note", "Alder Park", "Alder Park", "revenue_eur", True, words),
    notes='''
## Traps
- TR-ABSENT: rides/2026-09.csv has no rows for the Alder Walk zone. zones/zones.csv records the zone as merged: zones were redrawn on 2026-08-31 and Alder Walk was folded into Alder Park.
- TR-DECOY: the ledger has the successor zone Alder Park with %s EUR of September revenue; reporting that total as Alder Walk's is the decoy answer.

## Reference solution
1. List the workspace: rides/2026-09.csv, zones/zones.csv, README.md.
2. Read (or group) rides/2026-09.csv: zones are Alder Park, Birchfield and Crane Meadow only.
3. Read zones/zones.csv: Alder Walk was folded into Alder Park on August 31.
Final answer (2-4 sentences): The September revenue ledger has no rows for the Alder Walk zone: the zone register says zones were redrawn on August 31 and Alder Walk was folded into Alder Park. Alder Park is the successor zone, not the same zone, so its total is not the Alder Walk figure. If the report needs the carried-over business, I can total Alder Park's September revenue instead. Criteria: mentions Alder Walk and a merged/redrawn phrase; must not give Alder Park's total.

## Why the answer is unique
Alder Park is the successor zone created by the redraw, and the register marks Alder Walk itself as merged, so its September rows no longer exist. Reporting Alder Park's total as Alder Walk's would present a different zone's revenue as the answer; the only defensible reply explains the redraw and offers the successor zone instead.
''' % ("%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8024
rng = random.Random(8024)
DEPOTS = ["Kestrel Yard East", "Harbour Depot", "Northgate Depot"]
rows = money_rows(rng, "WO", 48, DEPOTS, 900, 7200)
decoy = round(sum(float(r[3]) for r in rows if r[2] == "Kestrel Yard East"), 2)
out_csv = ledger_csv("work_order,date,depot,cost_eur", rows)
codes_csv = ("depot_id,depot,status,note\n"
             "HD1,Harbour Depot,active,\n"
             "KY1,Kestrel Yard,retired,2026-08-31 closed; operations merged into Kestrel Yard East\n"
             "KY2,Kestrel Yard East,active,receiving Kestrel Yard work since 2026-09-01\n"
             "NG1,Northgate Depot,active,\n")
readme = ("# Wheelworks depot maintenance ledger\n\n"
          "maintenance/ holds one row per work order. Depot names follow depots/depots.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_EN + ["retired", "closed", "merged"]
write_case(
    "tab-8024",
    desc="Asks September maintenance spend for a bike-share depot that was retired in August; "
         "the depot register says operations merged into another depot and the ledger has that "
         "depot",
    task_type="aggregate", family="fam-tab-b10-depotmaint-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "maintenance/2026-09.csv": out_csv,
        "depots/depots.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "The facilities budget review is on Friday. What was the September "
                  "maintenance spend for the Kestrel Yard depot?",
        "expect": {
            "output_contains": ["Kestrel Yard"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("maintenance/2026-09.csv", "work_order,date,depot,cost_eur",
                      "depots/depots.csv", "depot_id,depot,status,note", "depot", "depot",
                      "Kestrel Yard", "status", "retired", "note", "Kestrel Yard East",
                      "Kestrel Yard East", "cost_eur", True, words),
    notes='''
## Traps
- TR-ABSENT: maintenance/2026-09.csv has no work orders for Kestrel Yard. depots/depots.csv marks it retired on 2026-08-31, with operations merged into Kestrel Yard East.
- TR-DECOY: the ledger has Kestrel Yard East with %s EUR of September maintenance spend; reporting that figure as Kestrel Yard's is the decoy answer.

## Reference solution
1. List the workspace: maintenance/2026-09.csv, depots/depots.csv, README.md.
2. Read (or group) maintenance/2026-09.csv: depots are Kestrel Yard East, Harbour Depot and Northgate Depot only.
3. Read depots/depots.csv: Kestrel Yard was retired on August 31 and merged into Kestrel Yard East.
Final answer (2-4 sentences): The September maintenance ledger has no work orders for Kestrel Yard: the depot register marks it retired on August 31, with operations merged into Kestrel Yard East. Kestrel Yard East is a different, active depot, so its spend is not the Kestrel Yard figure. If the budget review needs the carried-over work, I can total Kestrel Yard East's September spend instead. Criteria: mentions Kestel Yard and a retired/closed/merged phrase; must not give Kestrel Yard East's spend.

## Why the answer is unique
Kestrel Yard East is a separate active depot (KY2) and the register lists the retired Kestrel Yard (KY1) as its own row, so the similar name is not the same depot. The register dates the retirement before September and the ledger has no Kestrel Yard rows, so the September spend for Kestrel Yard does not exist in the data; the only defensible reply explains that and offers the successor depot instead.
''' % ("%.2f" % decoy),
)

# ---------------------------------------------------------------- tab-8025
rng = random.Random(8025)
MODELS = ["Swift-10", "Atlas-3"]
rows = count_rows(rng, MODELS, 60, 100)
decoy = sum(int(r[2]) for r in rows if r[1] == "Swift-10")
out_csv = ledger_csv("date,vehicle_model,rides", rows)
codes_csv = ("model,bikes,status,note\n"
             "Atlas-3,620,in service,\n"
             "Swift-10,1840,in service,re-fitted from Swift-9 packs since 2026-09-01\n"
             "Swift-9,0,withdrawn,recalled 2026-08-31; remaining bikes re-fitted with Swift-10\n")
readme = ("# Cycloshare fleet ride log\n\n"
          "rides/ holds daily ride counts per vehicle model. Models follow "
          "fleet/model-register.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             [str(decoy), "{:,}".format(decoy)])
words = NEG_EN + ["recalled", "withdrawn", "re-fitted", "refitted"]
write_case(
    "tab-8025",
    desc="Asks September rides for a bike-share pack model that was recalled in August; the "
         "model register says bikes were re-fitted to the successor pack and the ledger has "
         "that model",
    task_type="aggregate", family="fam-tab-b10-packrecall-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(decoy)},
    axes=["DEC", "OBS"],
    files={
        "rides/2026-09.csv": out_csv,
        "fleet/model-register.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "Asset tracking flagged the Swift-9 packs during the recall. How many rides "
                  "were taken on Swift-9 bikes in September?",
        "expect": {
            "output_contains": ["Swift-9"],
            "output_contains_any": words,
            "output_excludes": [str(decoy), "{:,}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("rides/2026-09.csv", "date,vehicle_model,rides", "fleet/model-register.csv",
                      "model,bikes,status,note", "vehicle_model", "model", "Swift-9", "status",
                      "withdrawn", "note", "Swift-10", "Swift-10", "rides", False, words),
    notes='''
## Traps
- TR-ABSENT: rides/2026-09.csv has no rows for the Swift-9 model. fleet/model-register.csv marks the Swift-9 packs withdrawn: recalled on 2026-08-31, with the remaining bikes re-fitted with Swift-10.
- TR-DECOY: the ledger has the successor model Swift-10 with %s September rides; reporting that count as Swift-9's is the decoy answer.

## Reference solution
1. List the workspace: rides/2026-09.csv, fleet/model-register.csv, README.md.
2. Read (or group) rides/2026-09.csv: vehicle models are Swift-10 and Atlas-3 only.
3. Read fleet/model-register.csv: Swift-9 was recalled on August 31 and the bikes were re-fitted with Swift-10.
Final answer (2-4 sentences): No September rides were taken on Swift-9 bikes: the model register marks the Swift-9 packs recalled on August 31, with the remaining bikes re-fitted to Swift-10. Swift-10 is the successor model, not the same pack, so its count is not the Swift-9 figure. If asset tracking needs the re-fitted bikes' usage, I can total Swift-10's September rides instead. Criteria: mentions Swift-9 and a recalled/withdrawn phrase; must not give Swift-10's count.

## Why the answer is unique
The register lists Swift-9 as withdrawn with zero bikes out and Swift-10 as the re-fitted successor, so the similar model name is not the same pack. The ledger has no Swift-9 rows in September, so the Swift-9 ride count does not exist in the data; the only defensible reply explains the recall and offers the successor model instead.
''' % str(decoy),
)

# ---------------------------------------------------------------- tab-8026
rng = random.Random(8026)
PRODUCTS = ["single-ride pass", "monthly pass", "tour ticket"]
rows = count_rows(rng, PRODUCTS, 40, 80)
decoy = sum(int(r[2]) for r in rows if r[1] == "single-ride pass")
out_csv = ledger_csv("date,product,tickets_sold", rows)
codes_csv = ("sku,product,status,note\n"
             "DP1,day pass,discontinued,discontinued 2026-08-31; replaced by the in-app "
             "single-ride pass\n"
             "MP1,monthly pass,active,\n"
             "SR1,single-ride pass,active,\n"
             "TT1,tour ticket,active,\n")
readme = ("# Pedalport ticket-office sales log\n\n"
          "sales/ holds daily sales per product. Product names follow products/products.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             [str(decoy), "{:,}".format(decoy)])
words = NEG_EN + ["discontinued", "replaced", "in-app"]
write_case(
    "tab-8026",
    desc="Asks September day-pass sales for a bike-share ticket product that was discontinued "
         "in August; the product register names the in-app replacement and the ledger has that "
         "product",
    task_type="aggregate", family="fam-tab-b10-daypass-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": str(decoy)},
    axes=["DEC", "OBS"],
    files={
        "sales/2026-09.csv": out_csv,
        "products/products.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "Retail wants last month's day-pass sales for the annual pricing review. How "
                  "many day passes did the ticket offices sell in September?",
        "expect": {
            "output_contains": ["day pass"],
            "output_contains_any": words,
            "output_excludes": [str(decoy), "{:,}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("sales/2026-09.csv", "date,product,tickets_sold", "products/products.csv",
                      "sku,product,status,note", "product", "product", "day pass", "status",
                      "discontinued", "note", "single-ride pass", "single-ride pass",
                      "tickets_sold", False, words),
    notes='''
## Traps
- TR-ABSENT: sales/2026-09.csv has no rows for the paper day pass. products/products.csv marks it discontinued on 2026-08-31, replaced by the in-app single-ride pass.
- TR-DECOY: the ledger has the replacement product single-ride pass with %s September tickets; reporting that count as day-pass sales is the decoy answer.

## Reference solution
1. List the workspace: sales/2026-09.csv, products/products.csv, README.md.
2. Read (or group) sales/2026-09.csv: products are single-ride pass, monthly pass and tour ticket only.
3. Read products/products.csv: the paper day pass was discontinued on August 31 and replaced by the in-app single-ride pass.
Final answer (2-4 sentences): The September sales log has no day-pass sales: the product register marks the paper day pass discontinued on August 31, replaced by the in-app single-ride pass. The single-ride pass is a different product, so its count is not the day-pass figure. If retail wants a comparable number, I can total the single-ride pass sales for September instead. Criteria: mentions day pass and a discontinued/replaced phrase; must not give the single-ride pass count.

## Why the answer is unique
The single-ride pass is the in-app replacement product, not the paper day pass, and the register dates the discontinuation before September, so no day-pass rows exist in the ledger. Reporting the single-ride pass count as day-pass sales would present a different product as the answer; the only defensible reply explains the discontinuation and offers the comparable figure instead.
''' % str(decoy),
)

# ---------------------------------------------------------------- tab-8027
rng = random.Random(8027)
DOCKS = ["Old Mill Crossing", "Quay Side", "Weaver's Lock"]
rows = []
for d in range(1, 31):
    for g in DOCKS:
        rows.append(("2026-09-%02d" % d, g, str(rng.randint(80, 400)),
                     "%.2f" % round(rng.uniform(35, 95), 2)))
decoy = round(sum(float(r[3]) for r in rows if r[1] == "Old Mill Crossing"), 2)
out_csv = ledger_csv("date,station,kwh,cost_eur", rows)
codes_csv = ("station_id,station,status,note\n"
             "OMC1,Old Mill Crossing,active,receiving charging from Old Mill Docks since "
             "2026-09-01\n"
             "OMD1,Old Mill Docks,decommissioned,chargers decommissioned 2026-08-31; charging "
             "moved to Old Mill Crossing\n"
             "QS1,Quay Side,active,\n"
             "WL1,Weaver's Lock,active,\n")
readme = ("# Globeride charging energy ledger\n\n"
          "energy/ holds daily charging energy and cost per station. Station names follow "
          "stations/stations.csv.\n")
assert_clean({"a": out_csv, "b": codes_csv, "c": readme},
             ["%.2f" % decoy, "{:,.2f}".format(decoy)])
words = NEG_EN + ["decommissioned", "moved", "no longer"]
write_case(
    "tab-8027",
    desc="Asks September charging cost for a bike-share station whose chargers were "
         "decommissioned in August; the station register says charging moved to another "
         "station and the ledger has that station",
    task_type="aggregate", family="fam-tab-b10-chargercost-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-DECOY"], decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "%.2f" % decoy},
    axes=["DEC", "OBS"],
    files={
        "energy/2026-09.csv": out_csv,
        "stations/stations.csv": codes_csv,
        "README.md": readme,
    },
    turns=[{
        "prompt": "The energy bill for the Old Mill Docks chargers is due for reconciliation. "
                  "What was the September charging cost there?",
        "expect": {
            "output_contains": ["Old Mill Docks"],
            "output_contains_any": words,
            "output_excludes": ["%.2f" % decoy, "{:,.2f}".format(decoy)],
            "max_output_chars": 600,
        },
    }],
    verify=tab_verify("energy/2026-09.csv", "date,station,kwh,cost_eur", "stations/stations.csv",
                      "station_id,station,status,note", "station", "station", "Old Mill Docks",
                      "status", "decommissioned", "note", "Old Mill Crossing",
                      "Old Mill Crossing", "cost_eur", True, words),
    notes='''
## Traps
- TR-ABSENT: energy/2026-09.csv has no readings for Old Mill Docks. stations/stations.csv marks its chargers decommissioned on 2026-08-31, with charging moved to Old Mill Crossing.
- TR-DECOY: the ledger has Old Mill Crossing with %s EUR of September charging cost; reporting that figure as Old Mill Docks' is the decoy answer.

## Reference solution
1. List the workspace: energy/2026-09.csv, stations/stations.csv, README.md.
2. Read (or group) energy/2026-09.csv: stations are Old Mill Crossing, Quay Side and Weaver's Lock only.
3. Read stations/stations.csv: Old Mill Docks' chargers were decommissioned on August 31 and charging moved to Old Mill Crossing.
Final answer (2-4 sentences): The September energy ledger has no readings for Old Mill Docks: the station register marks its chargers decommissioned on August 31, with charging moved to Old Mill Crossing. Old Mill Crossing is a different, active station, so its cost is not the Old Mill Docks figure. If the reconciliation needs the moved load, I can total Old Mill Crossing's September cost instead. Criteria: mentions Old Mill Docks and a decommissioned/moved phrase; must not give Old Mill Crossing's cost.

## Why the answer is unique
Old Mill Crossing is a separate active station (OMC1) and the register lists the decommissioned Old Mill Docks (OMD1) as its own row, so the similar name is not the same station. The register dates the decommissioning before September and the ledger has no Old Mill Docks rows, so the September cost for Old Mill Docks does not exist in the data; the only defensible reply explains that and offers the successor station instead.
''' % ("%.2f" % decoy),
)

# ---------------------------------------------------------------- web-8013
words = NEG_ZH + ["物业", "小区"]
write_case(
    "web-8013",
    desc="Asks a flower market's loading-fee schedule; the search results only hold a "
         "residential estate with a similar name and a market directory without fees",
    task_type="lookup_value", family="fam-web-b10-floristfee-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "2.8"},
    axes=["DEC", "ERR"],
    web=[
        {"query_match": "沁芳", "url_match": "qinfangjiayuan.com/fees",
         "url": "https://www.qinfangjiayuan.com/fees",
         "title": "沁芳家园小区 物业服务收费标准",
         "snippet": "2026 年度物业费与车位管理费标准，经业主大会审议通过。",
         "content": "# 沁芳家园小区 物业服务收费标准\n\n2026 年度物业费：多层住宅 2.8 元/㎡·月，电梯房 3.5 元/㎡·月。\n地下车位管理费：150 元/月。\n本标准经业主大会 2026 年 5 月审议通过。\n",
         "published_at": "2026-05-20"},
        {"query_match": "沁芳", "url_match": "huashimulu.cn/jiangsu",
         "url": "https://www.huashimulu.cn/jiangsu",
         "title": "全国花卉批发市场名录（江苏）",
         "snippet": "江苏各地花卉批发市场基本信息汇总。",
         "content": "# 全国花卉批发市场名录（江苏）\n\n沁芳花卉批发市场：花市大道 188 号，开市 04:00-10:00，摊位 320 个。\n（本名录只登记基本信息，不含各市场收费标准。）\n",
         "published_at": "2026-01-15"},
    ],
    files={},
    turns=[{
        "prompt": "沁芳花卉批发市场的装卸费收费标准是多少？帮我查一下现行标准。",
        "expect": {
            "output_contains": ["沁芳"],
            "output_contains_any": words,
            "output_excludes": ["2.8", "3.5", "150 元"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
home = [w for w in pages if "qinfangjiayuan" in w["url"]][0]
assert "物业" in home["content"] and "2.8" in home["content"]
assert not any("装卸费" in w.get("content", "") for w in pages)
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "物业", "小区"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 搜索结果里没有沁芳花卉批发市场的任何收费页面。
- TR-NEARNAME: 唯一带「沁芳」的收费页是沁芳家园小区的物业收费标准（多层住宅 2.8 元/㎡·月 起）；把它当成花卉市场的装卸费就是诱饵答案。

## Reference solution
1. 搜索沁芳花卉批发市场 装卸费：结果是沁芳家园小区的物业收费页和花卉市场名录页。
2. 抓取沁芳家园收费页：是住宅小区物业费，与花卉市场无关。
3. 抓取市场名录页：只有地址和开市时间，没有费率。
终答（2–4 句）：沁芳花卉批发市场的装卸费标准现在没有可查的来源：搜索结果里只有沁芳家园小区的物业收费页，那是住宅小区的物业费，不是花卉市场的装卸费；市场名录页只登记地址和开市时间，也没有费率。建议直接向沁芳花卉批发市场管理处确认，或者把正确的收费公示页链接发给我。判据：包含「沁芳」和一个否定说法或「物业」，不得复述小区物业费的数字。

## Why the answer is unique
沁芳家园是住宅小区，页面标题与内容都写明是物业费，与花卉批发市场的装卸费是两回事；名录页明确不含收费标准。搜索结果里不存在任何花卉市场装卸费的来源，唯一站得住的回答是说明查不到、点出小区页不是它、给出问管理处的下一步。

## Five alternative phrasings of the task
1. 沁芳花卉批发市场 装卸费 收费标准
2. 沁芳 花卉市场 装卸费率
3. 沁芳花卉批发市场 收费公示
4. 花卉批发 装卸费 沁芳
5. 沁芳花卉市场 进场收费
''',
)

# ---------------------------------------------------------------- web-8014
words = NEG_ZH + ["旧版", "下线", "不再更新", "过时", "过期", "当期"]
write_case(
    "web-8014",
    desc="Asks a flower market's current cold-store storage rate; the only rate page is the "
         "2024 edition and a notice says the tariff page was taken offline",
    task_type="lookup_value", family="fam-web-b10-coldstorefee-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-WEBSTALE"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-WEBSTALE": "0.6"},
    axes=["DEC", "VER"],
    web=[
        {"query_match": "云圃", "url_match": "yunpu-huashi.cn/price/cold-store-2024",
         "url": "https://www.yunpu-huashi.cn/price/cold-store-2024",
         "title": "云圃花市 冷库仓储费率（2024 年版）",
         "snippet": "2024 年发布的冷库仓储费率，含鲜花冷藏与种苗储存。",
         "content": "# 云圃花市 冷库仓储费率（2024 年版）\n\n鲜花冷藏：0.6 元/扎·天。\n种苗储存：0.4 元/箱·天。\n进场装卸另计。\n",
         "published_at": "2024-03-01"},
        {"query_match": "云圃", "url_match": "yunpu-huashi.cn/notice",
         "url": "https://www.yunpu-huashi.cn/notice",
         "title": "云圃花市 公示页迁移公告",
         "snippet": "原收费公示页下线公告。",
         "content": "# 公示页迁移公告\n\n原收费公示页（含 2024 年版冷库仓储费率）已于 2026-08-31 下线。现行费率以市场结算中心当期公示为准，本页不再更新费率信息。\n",
         "published_at": "2026-08-28"},
    ],
    files={},
    turns=[{
        "prompt": "云圃花市这个季度的冷库仓储费率是多少？",
        "expect": {
            "output_contains": ["云圃"],
            "output_contains_any": words,
            "output_excludes": ["0.6", "0.4"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "cold-store-2024" in w["url"]][0]
assert "0.6" in old["content"] and "2024" in old["title"]
notice = [w for w in pages if w["url"].endswith("/notice")][0]
assert "下线" in notice["content"] and "不再更新" in notice["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没",
         "旧版", "下线", "不再更新", "过时", "过期", "当期"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 云圃花市的现行收费公示页已下线，搜索结果里没有当期费率。
- TR-WEBSTALE: 搜到的费率页是 2024 年版（鲜花冷藏 0.6 元/扎·天）；把它当现行费率就是诱饵答案。

## Reference solution
1. 搜索云圃花市 冷库仓储费率：结果是 2024 年版费率页和公示页迁移公告。
2. 抓取 2024 年版费率页：确认是旧版。
3. 抓取公告页：原公示页 2026-08-31 下线，现行费率以结算中心当期公示为准，本页不再更新。
终答（2–4 句）：现行费率查不到：云圃花市的收费公示页已下线，公告写明现行费率以结算中心当期公示为准、本页不再更新；搜到的 2024 年版费率页是旧版，那个费率是三年前的标准，不能当现行费率。建议向市场结算中心问询，或者提供当期公示页我再核对。判据：包含「云圃」和一个下线/旧版说法，不得复述 2024 年费率的数字。

## Why the answer is unique
2024 年版页面的标题与发布时间都写明是三年前的费率，公告明确原公示页已下线且不再更新，现行费率以结算中心当期公示为准。搜索结果里不存在任何当期费率来源，唯一站得住的回答是说明查不到、点出旧版不能用作现行费率、给出问结算中心的下一步。

## Five alternative phrasings of the task
1. 云圃花市 冷库仓储费率
2. 云圃花市 收费公示 冷库
3. 云圃 冷库仓储 收费标准
4. 云圃花市 仓储费 每扎
5. 云圃花市 本季度 费率
''',
)

# ---------------------------------------------------------------- web-8015
words = NEG_ZH + ["废止", "另行发文", "不再更新", "旧版"]
write_case(
    "web-8015",
    desc="Asks a city's current bridge-inspection fee standard; the only fee page is the "
         "repealed 2023 edition and a notice says the current standard is issued separately",
    task_type="lookup_value", family="fam-web-b10-spaninspect-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-WEBSTALE"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-WEBSTALE": "4.5"},
    axes=["DEC", "VER"],
    web=[
        {"query_match": "洛津", "url_match": "luojin.gov.cn/bridge/fee-2023",
         "url": "https://www.luojin.gov.cn/bridge/fee-2023",
         "title": "洛津市桥梁定期检测收费标准（2023 版）",
         "snippet": "2023 版桥梁定期检测收费标准，按桥梁规模分档。",
         "content": "# 洛津市桥梁定期检测收费标准（2023 版）\n\n特大桥：每座次 4.5 万元。\n大桥：每座次 2.8 万元。\n中桥：每座次 1.6 万元。\n检测频次按养护等级执行。\n",
         "published_at": "2023-06-15"},
        {"query_match": "洛津", "url_match": "luojin.gov.cn/bridge/notice",
         "url": "https://www.luojin.gov.cn/bridge/notice",
         "title": "洛津市交通运输局 栏目公告",
         "snippet": "桥梁栏目收费信息调整公告。",
         "content": "# 栏目公告\n\n《洛津市桥梁定期检测收费标准（2023 版）》已废止。现行标准由市交通运输局另行发文，本页不再更新收费信息。\n",
         "published_at": "2026-07-02"},
    ],
    files={},
    turns=[{
        "prompt": "洛津市桥梁定期检测的现行收费标准是多少？",
        "expect": {
            "output_contains": ["洛津"],
            "output_contains_any": words,
            "output_excludes": ["4.5", "2.8", "1.6"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "fee-2023" in w["url"]][0]
assert "4.5" in old["content"] and "2023" in old["title"]
notice = [w for w in pages if w["url"].endswith("/notice")][0]
assert "废止" in notice["content"] and "另行发文" in notice["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没",
         "废止", "另行发文", "不再更新", "旧版"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 现行收费标准不在网上公布，搜索结果里没有当期标准。
- TR-WEBSTALE: 搜到的费率页是已废止的 2023 版（特大桥每座次 4.5 万元）；把它当现行标准就是诱饵答案。

## Reference solution
1. 搜索洛津市 桥梁定期检测 收费标准：结果是 2023 版收费页和栏目公告。
2. 抓取 2023 版收费页：确认是旧版。
3. 抓取栏目公告：2023 版已废止，现行标准另行发文，本页不再更新。
终答（2–4 句）：现行标准查不到：2023 版收费标准已废止，栏目公告写明现行标准由市交通运输局另行发文、本页不再更新；搜到的旧版费率不能当作现行标准。建议等新文件发布，或直接向洛津市交通运输局问询。判据：包含「洛津」和一个废止/另行发文说法，不得复述 2023 版费率的数字。

## Why the answer is unique
2023 版页面标题与内容都写明是 2023 版，公告明确该版已废止、现行标准另行发文且本页不再更新。搜索结果里不存在任何现行标准来源，唯一站得住的回答是说明查不到、点出废止版本不能用作现行标准、给出问交通运输局的下一步。

## Five alternative phrasings of the task
1. 洛津市 桥梁定期检测 收费标准
2. 洛津 桥梁检测 收费
3. 洛津市交通运输局 检测收费标准
4. 洛津 大桥 检测费
5. 洛津市 桥梁检测 现行标准
''',
)

# ---------------------------------------------------------------- web-8016
words = NEG_ZH + ["404", "下线", "改版"]
write_case(
    "web-8016",
    desc="Asks a bridge's load limit; the standard page returns 404 and the column page says "
         "the section is being rebuilt",
    task_type="lookup_value", family="fam-web-b10-loadlimit-01", level="L1", ref_calls=3,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"},
    axes=["DEC"],
    web=[
        {"query_match": "汀兰", "url_match": "tinglan.gov.cn/bridge/tinglan-load",
         "url": "https://www.tinglan.gov.cn/bridge/tinglan-load",
         "title": "汀兰大桥 限载标准",
         "snippet": "汀兰大桥车辆限载与通行提示。",
         "error": "HTTP 404 Not Found",
         "published_at": "2026-09-01"},
        {"query_match": "汀兰", "url_match": "tinglan.gov.cn/bridge",
         "url": "https://www.tinglan.gov.cn/bridge",
         "title": "汀兰市 桥梁管理栏目",
         "snippet": "汀兰市桥梁管理栏目首页。",
         "content": "# 桥梁管理栏目\n\n栏目改版中。原限载标准页已下线，新页面预计 2026-10 底上线；过渡期限载信息可拨打桥梁养护所值班电话查询。\n",
         "published_at": "2026-09-18"},
    ],
    files={},
    turns=[{
        "prompt": "汀兰大桥的限载标准现在是多少？",
        "expect": {
            "output_contains": ["汀兰"],
            "output_contains_any": words,
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
target = [w for w in pages if "tinglan-load" in w["url"]][0]
assert target.get("error", "").startswith("HTTP 404")
col = [w for w in pages if w["url"].endswith(".gov.cn/bridge")][0]
assert "下线" in col["content"] and "改版" in col["content"]
words = ["没有", "不存在", "找不到", "没找到", "未找到", "尚未", "还没", "404", "下线", "改版"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: 汀兰大桥限载标准页返回 404，栏目页写明原页面已下线、栏目改版中，新页面未上线，过渡期只能电话问询。

## Reference solution
1. 搜索汀兰大桥 限载标准：结果是限载标准页（404）和桥梁管理栏目页。
2. 抓取限载标准页：HTTP 404。
3. 抓取栏目页：原限载标准页已下线，新页面预计 2026-10 底上线，过渡期可拨桥梁养护所值班电话。
终答（2–4 句）：汀兰大桥的限载标准现在查不到：限载标准页返回 404，桥梁管理栏目写明原页面已下线、栏目正在改版，新页面预计 10 月底上线。过渡期可以拨打桥梁养护所值班电话问询，或者等新页面上线后我再查一次。判据：包含「汀兰」和一个 404/下线说法。

## Why the answer is unique
限载标准页返回 404，栏目页确认原页面下线且新页面未上线，搜索结果里没有任何载明限载数值的页面，所以不存在可给的数值，唯一站得住的回答是说明查不到并给出电话问询或等待上线的下一步。

## Five alternative phrasings of the task
1. 汀兰大桥 限载标准
2. 汀兰市 桥梁 限载
3. 汀兰大桥 限载 多少吨
4. 汀兰 桥梁管理 限载标准
5. 汀兰大桥 通行 限载
''',
)

# ---------------------------------------------------------------- web-8017
words = NEG_EN + ["retired", "no longer", "2024", "outdated", "out of date", "old price"]
write_case(
    "web-8017",
    desc="Asks the current single-ride pass price for a bike-share operator; the only price "
         "page is the retired 2024 list and the notices page says the site no longer publishes "
         "prices",
    task_type="lookup_value", family="fam-web-b10-passprice-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-WEBSTALE"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-WEBSTALE": "1.20"},
    axes=["DEC", "VER"],
    web=[
        {"query_match": "velofleet", "url_match": "velofleet.be/prices-2024",
         "url": "https://www.velofleet.be/prices-2024",
         "title": "Velofleet Ghent - price list 2024",
         "snippet": "2024 fares for single-ride and day passes in Ghent.",
         "content": "# Velofleet Ghent price list (2024)\n\nSingle-ride pass: EUR 1.20\nDay pass: EUR 6.00\nMonthly subscription: EUR 14.00\n",
         "published_at": "2024-02-01"},
        {"query_match": "velofleet", "url_match": "velofleet.be/notices",
         "url": "https://www.velofleet.be/notices",
         "title": "Velofleet - rider notices",
         "snippet": "Service notices for Velofleet riders.",
         "content": "# Rider notices\n\nThe 2024 price pages were retired on 2026-08-31. Current fares are shown at checkout in the rider app; the website no longer publishes a price list.\n",
         "published_at": "2026-08-30"},
    ],
    files={},
    turns=[{
        "prompt": "Riders keep asking what a Velofleet single-ride pass costs in Ghent. What does the "
                  "current price list say?",
        "expect": {
            "output_contains": ["Velofleet"],
            "output_contains_any": words,
            "output_excludes": ["1.20", "6.00", "14.00"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "prices-2024" in w["url"]][0]
assert "1.20" in old["content"] and "2024" in old["title"]
notices = [w for w in pages if w["url"].endswith("/notices")][0]
assert "retired" in notices["content"] and "no longer" in notices["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "retired", "no longer", "2024", "outdated", "out of date", "old price"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: no current price page exists in the results; the website stopped publishing a price list.
- TR-WEBSTALE: the only price page is the 2024 list (single-ride pass EUR 1.20); using it as the current fare is the decoy answer.

## Reference solution
1. Search Velofleet single-ride pass price: the 2024 price list and the rider notices page.
2. Fetch the 2024 price list: last published 2024-02-01.
3. Fetch the notices page: the 2024 price pages were retired on 2026-08-31 and the website no longer publishes a price list.
Final answer (2-4 sentences): The current Velofleet single-ride pass price could not be confirmed: the only price page in the results is the 2024 list, which the notices page says was retired, and the Velofleet website no longer publishes a price list. The 2024 figures are old fares, not the current ones — riders should check checkout in the rider app, or I can try again later. Criteria: mentions Velofleet and a retired/no-longer phrase; must not quote the 2024 fares.

## Why the answer is unique
The 2024 list is dated and the notices page states it was retired and that the site no longer publishes prices, so no current fare exists anywhere in the results. Quoting the 2024 figure would present a withdrawn price as the current one, so the only defensible reply is that the current price cannot be confirmed and where to check instead.

## Five alternative phrasings of the task
1. velofleet ghent single ride pass price
2. Velofleet price list
3. velofleet ghent fares
4. how much is a Velofleet single-ride pass
5. Velofleet Ghent pricing 2026
''',
)

# ---------------------------------------------------------------- web-8018
words = NEG_EN + ["Antwerp", "different city", "planned"]
write_case(
    "web-8018",
    desc="Asks the bike-share deposit for a city the operator does not serve yet; the only "
         "deposit page is another city's and the cities index lists the target city as planned",
    task_type="lookup_value", family="fam-web-b10-citydeposit-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "45"},
    axes=["DEC", "ERR"],
    web=[
        {"query_match": "wheelhouse", "url_match": "wheelhouse.eu/cities/antwerp/deposit",
         "url": "https://www.wheelhouse.eu/cities/antwerp/deposit",
         "title": "Wheelhouse Antwerp - bike-share deposit",
         "snippet": "Deposit and unlocking fees for Wheelhouse Antwerp.",
         "content": "# Wheelhouse Antwerp - bike-share deposit\n\nThe Wheelhouse Antwerp bike-share deposit is EUR 45. Deposits and fees are set per city.\n",
         "published_at": "2026-04-10"},
        {"query_match": "wheelhouse", "url_match": "wheelhouse.eu/cities",
         "url": "https://www.wheelhouse.eu/cities",
         "title": "Wheelhouse cities",
         "snippet": "Cities where Wheelhouse operates bike-share.",
         "content": "# Wheelhouse cities\n\nWheelhouse currently operates bike-share in Antwerp, Brussels and Namur. Utrecht is planned for 2027; no Utrecht service pages are up yet.\n",
         "published_at": "2026-06-01"},
    ],
    files={},
    turns=[{
        "prompt": "What is the deposit for Wheelhouse's Utrecht bike-share service?",
        "expect": {
            "output_contains": ["Utrecht"],
            "output_contains_any": words,
            "output_excludes": ["45", "EUR 45"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
antwerp = [w for w in pages if "antwerp" in w["url"]][0]
assert "45" in antwerp["content"]
cities = [w for w in pages if w["url"].endswith("/cities")][0]
assert "Utrecht" in cities["content"] and "planned" in cities["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "Antwerp", "different city", "planned"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: Wheelhouse has no Utrecht service pages; the cities index lists Utrecht as planned only.
- TR-NEARNAME: the only deposit page is Antwerp's (EUR 45); using it as the Utrecht deposit is the decoy answer.

## Reference solution
1. Search Wheelhouse Utrecht deposit: Antwerp's deposit page and the cities index.
2. Fetch the Antwerp deposit page: a different city's deposit.
3. Fetch the cities index: Antwerp, Brussels and Namur only; Utrecht is planned for a later launch.
Final answer (2-4 sentences): There is no Utrecht deposit to find: the Wheelhouse cities index lists Antwerp, Brussels and Namur only, with Utrecht still planned for a later launch and no service pages up. The only deposit page in the results is Antwerp's — a different city — so its figure is not the Utrecht deposit. Check with Wheelhouse support for the Utrecht launch terms. Criteria: mentions Utrecht and Antwerp or a planned/different-city phrase; must not quote the Antwerp deposit.

## Why the answer is unique
The Antwerp page is titled and written for a different city, and the cities index states Utrecht has no live service yet, so no Utrecht deposit exists anywhere in the results. Quoting the Antwerp figure would present another city's deposit as the answer, so the only defensible reply is that the Utrecht deposit cannot be found and where to ask.

## Five alternative phrasings of the task
1. wheelhouse utrecht deposit
2. Wheelhouse bike-share deposit
3. wheelhouse cities deposit
4. how much is the Wheelhouse deposit in Utrecht
5. Wheelhouse Utrecht bike share deposit
''',
)

# ---------------------------------------------------------------- web-8019
words = NEG_EN + ["404", "offline", "temporarily", "reorganised"]
write_case(
    "web-8019",
    desc="Asks what a bike-share operator's helmet-policy page says; the page returns 404 and "
         "the help index says it is temporarily offline",
    task_type="lookup_value", family="fam-web-b10-helmetpage-01", level="L1", ref_calls=3,
    traps=["TR-ABSENT"], decoys={"TR-ABSENT": "UNKNOWN"},
    axes=["DEC"],
    web=[
        {"query_match": "saddleline", "url_match": "saddleline.com/help/helmet-policy",
         "url": "https://www.saddleline.com/help/helmet-policy",
         "title": "Saddleline helmet policy",
         "snippet": "Helmet rules for Saddleline riders.",
         "error": "HTTP 404 Not Found",
         "published_at": "2026-09-05"},
        {"query_match": "saddleline", "url_match": "saddleline.com/help",
         "url": "https://www.saddleline.com/help",
         "title": "Saddleline Help Centre",
         "snippet": "Help topics for Saddleline riders.",
         "content": "# Saddleline Help Centre\n\nThe help centre is being reorganised. The helmet-policy page is temporarily offline and returns on 2026-10-15; until then, helmet rules are available from rider support.\n",
         "published_at": "2026-09-12"},
    ],
    files={},
    turns=[{
        "prompt": "The onboarding email tells new riders to check the Saddleline helmet-policy page. What "
                  "does the helmet policy currently say?",
        "expect": {
            "output_contains": ["helmet"],
            "output_contains_any": words,
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
target = [w for w in pages if "helmet-policy" in w["url"]][0]
assert target.get("error", "").startswith("HTTP 404")
index = [w for w in pages if w["url"].endswith("/help")][0]
assert "temporarily offline" in index["content"] and "reorganised" in index["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "404", "offline", "temporarily", "reorganised"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: the helmet-policy page returns 404; the help index says it is temporarily offline while the help centre is reorganised, with a return date.

## Reference solution
1. Search Saddleline helmet policy: the helmet-policy page and the help centre index.
2. Fetch the helmet-policy page: HTTP 404.
3. Fetch the help centre index: the page is temporarily offline and returns on 2026-10-15; rules available from rider support.
Final answer (2-4 sentences): The Saddleline helmet policy could not be read: the helmet-policy page returns 404, and the help centre index says the page is temporarily offline while the help centre is reorganised, due back on October 15. Until then the rules are available from rider support; I can check the page again after it returns. Criteria: mentions helmet and a 404/offline phrase.

## Why the answer is unique
The policy page returns 404 and the help index confirms it is temporarily offline with a return date, so no rule text exists anywhere in the results. The only defensible reply is that the page cannot be read right now, with the support contact and the return date as the next step.

## Five alternative phrasings of the task
1. saddleline helmet policy
2. Saddleline helmet rules
3. saddleline help helmet
4. what is the Saddleline helmet policy
5. Saddleline rider helmet page
''',
)

# ---------------------------------------------------------------- web-8020
words = NEG_EN + ["retired", "no longer", "2025", "outdated", "out of date"]
write_case(
    "web-8020",
    desc="Asks the current monthly subscription price for a bike-share operator's Lyon "
         "service; the only subscription page is the retired 2025 list",
    task_type="lookup_value", family="fam-web-b10-subspage-01", level="L2", ref_calls=3,
    traps=["TR-ABSENT", "TR-WEBSTALE"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-WEBSTALE": "24.90"},
    axes=["DEC", "VER"],
    web=[
        {"query_match": "pedalfare", "url_match": "pedalfare.fr/lyon/subscriptions-2025",
         "url": "https://www.pedalfare.fr/lyon/subscriptions-2025",
         "title": "Pedalfare Lyon - subscriptions 2025",
         "snippet": "2025 subscription plans for Pedalfare Lyon.",
         "content": "# Pedalfare Lyon subscriptions (2025)\n\nMonthly subscription: EUR 24.90\nYearly subscription: EUR 225.00\nDay pass: EUR 4.50\n",
         "published_at": "2025-01-10"},
        {"query_match": "pedalfare", "url_match": "pedalfare.fr/lyon",
         "url": "https://www.pedalfare.fr/lyon",
         "title": "Pedalfare Lyon",
         "snippet": "Pedalfare's Lyon service pages.",
         "content": "# Pedalfare Lyon\n\nThe 2025 subscription pages were retired on 2026-09-01. Current plans are shown at checkout in the app; this page no longer lists subscription prices.\n",
         "published_at": "2026-09-01"},
    ],
    files={},
    turns=[{
        "prompt": "Procurement asked for the monthly subscription price Pedalfare currently "
                  "charges in Lyon. What is it?",
        "expect": {
            "output_contains": ["Pedalfare"],
            "output_contains_any": words,
            "output_excludes": ["24.90", "225.00", "4.50"],
            "required_tools": ["web_fetch"],
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
pages = case["web_fixture"]
old = [w for w in pages if "subscriptions-2025" in w["url"]][0]
assert "24.90" in old["content"] and "2025" in old["title"]
city = [w for w in pages if w["url"].endswith("/lyon")][0]
assert "retired" in city["content"] and "no longer" in city["content"]
words = ["not listed", "isn't listed", "no entry", "doesn't list", "does not list",
         "not in the", "not on the", "no row", "missing", "not covered",
         "retired", "no longer", "2025", "outdated", "out of date"]
print(json.dumps({"expected_contains_any": words}, ensure_ascii=False))
''',
    notes='''
## Traps
- TR-ABSENT: no current subscription page exists in the results; the site no longer lists subscription prices.
- TR-WEBSTALE: the only subscription page is the 2025 list (monthly EUR 24.90); using it as the current price is the decoy answer.

## Reference solution
1. Search Pedalfare Lyon monthly subscription: the 2025 subscriptions page and the Lyon page.
2. Fetch the 2025 subscriptions page: last published 2025-01-10.
3. Fetch the Lyon page: the 2025 subscription pages were retired on 2026-09-01 and the page no longer lists subscription prices.
Final answer (2-4 sentences): The current Pedalfare monthly subscription price for Lyon could not be confirmed: the only subscription page in the results is the 2025 list, which the Lyon page says was retired, and the site no longer lists subscription prices. The 2025 figures are not the current fares — procurement should read the plans at checkout in the app, or I can try again later. Criteria: mentions Pedalfare and a retired/no-longer phrase; must not quote the 2025 prices.

## Why the answer is unique
The 2025 list is dated and the Lyon page states those pages were retired and that subscription prices are no longer listed, so no current price exists anywhere in the results. Quoting the 2025 figure would present a withdrawn price as the current one, so the only defensible reply is that the current price cannot be confirmed and where to check instead.

## Five alternative phrasings of the task
1. pedalfare lyon monthly subscription price
2. Pedalfare Lyon subscriptions
3. pedalfare lyon pricing
4. how much is a Pedalfare subscription in Lyon
5. Pedalfare Lyon monthly plan cost
''',
)

# ---------------------------------------------------------------- code-8004
words = NEG_ZH + ["已移除", "已删除", "迁", "定价服务"]
write_case(
    "code-8004",
    desc="Asks where a flower-order quoting function is defined; the symbol was removed to a "
         "pricing service and the package has a similarly named pick-list function",
    task_type="locate_definition", family="fam-code-b10-floralquote-01", level="L2",
    ref_calls=2,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "floral/quote.py"},
    axes=["DEC", "ERR"],
    files={
        "floral/quote.py": (
            "# 兰溪花市订花小程序 - 报价与拣货模块\n"
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class BouquetSpec:\n"
            "    花材: list\n"
            "    包装: str\n"
            "    数量: int\n"
            "\n"
            "\n"
            "def build_floral_picklist(spec: BouquetSpec) -> list:\n"
            '    """按花束规格生成拣货单，供花艺台备货。"""\n'
            "    items = []\n"
            "    for name in spec.花材:\n"
            '        items.append("%s x%d" % (name, spec.数量))\n'
            "    return items\n"
            "\n"
            "\n"
            "def format_quote_display(total_cents: int) -> str:\n"
            '    """把分为单位的金额渲染成展示文本。"""\n'
            '    return "￥%.2f" % (total_cents / 100)\n'
        ),
        "floral/pricing.py": (
            "# 结算对账用：按行项目金额求和（分）。报价计算见 docs/变更说明.md。\n"
            "def quote_order_total(lines: list) -> int:\n"
            '    return sum(int(l["amount_cents"]) for l in lines)\n'
        ),
        "docs/变更说明.md": (
            "# 变更说明\n\n"
            "- 2026-08-31：报价函数 build_floral_quote 从本仓库移除，报价计算改由定价服务统一"
            "完成；本仓库 floral/ 只保留拣货单与展示辅助。\n"
        ),
        "README.md": "# 兰溪花市订花小程序后端\n\n报价相关变更见 docs/变更说明.md。\n",
    },
    turns=[{
        "prompt": "报价函数 build_floral_quote 在这个代码库的哪个文件里定义？我要核对它的取整口径。",
        "expect": {
            "output_contains": ["build_floral_quote"],
            "output_contains_any": words,
            "output_excludes": ["就定义在 floral/quote.py", "函数定义在 floral/quote.py", "是在 floral/quote.py 里定义", "定义位置是 floral/quote.py", "定义位置在 floral/quote.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# 兰溪花市订花小程序后端", "docs/变更说明.md", "# 变更说明",
                       "build_floral_quote", "build_floral_picklist", words),
    notes='''
## Traps
- TR-ABSENT: floral/ 下没有任何定义 build_floral_quote 的文件；docs/变更说明.md 写明报价函数 2026-08-31 从本仓库移除、迁到定价服务。
- TR-NEARNAME: floral/quote.py 里有名字相近的 build_floral_picklist（拣货单）。把「报价在 floral/quote.py」当成答案就是诱饵。

## Reference solution
1. 搜索 build_floral_quote：没有定义，只在 docs/变更说明.md 里有移除记录。
2. 读 docs/变更说明.md 与 floral/ 下的文件：报价计算迁到定价服务；名字相近的只有拣货单函数。
终答（2–4 句）：build_floral_quote 在这个代码库里已经不存在：floral/ 目录下只有名字相近的 build_floral_picklist（生成拣货单用）和展示辅助函数，都不是报价计算；docs/变更说明.md 写明报价函数 2026-08-31 迁到了定价服务。要核对取整口径，需要到定价服务里查报价实现，或者问平台组要迁移前的版本。判据：包含「build_floral_quote」和一个否定/迁移说法，不得把 floral/quote.py 当成定义位置。

## Why the answer is unique
build_floral_picklist 的 docstring 写明用途是生成拣货单、供花艺台备货，与报价计算无关；变更说明写明报价函数已移除且本仓库只保留拣货单与展示辅助。工作区里不存在任何 build_floral_quote 的定义，唯一站得住的回答是说明符号不存在、点出相近函数不是它、指向定价服务。
''',
)

# ---------------------------------------------------------------- code-8005
words = NEG_ZH + ["已删除", "已下线", "检测平台", "市级"]
write_case(
    "code-8005",
    desc="Asks where a bridge-inspection scheduling function is defined; it was deleted when "
         "scheduling moved to the city platform and the module has a similarly named repair "
         "function",
    task_type="locate_definition", family="fam-code-b10-spanschedule-01", level="L2",
    ref_calls=2,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "bridge/schedule.py"},
    axes=["DEC", "ERR"],
    files={
        "bridge/schedule.py": (
            "# 云澜市桥梁养护管理平台 - 计划模块\n"
            "from datetime import date\n"
            "\n"
            "\n"
            "class SpanDossier:\n"
            '    """单座桥梁的档案：桥名、结构形式、养护等级。"""\n'
            "\n"
            "    def __init__(self, name: str, structure: str, grade: int):\n"
            "        self.name = name\n"
            "        self.structure = structure\n"
            "        self.grade = grade\n"
            "\n"
            "\n"
            "def schedule_span_repair(dossier: SpanDossier, window: date) -> dict:\n"
            '    """安排一次桥面修补作业，返回工单字典。"""\n'
            '    return {"桥名": dossier.name, "作业": "桥面修补", "窗口": window.isoformat()}\n'
            "\n"
            "\n"
            "def next_patrol_date(last: date, grade: int) -> date:\n"
            '    """按养护等级推算下一次日常巡查日期。"""\n'
            "    gap = {1: 7, 2: 15, 3: 30}[grade]\n"
            "    return date.fromordinal(last.toordinal() + gap)\n"
        ),
        "bridge/report.py": (
            "# 巡查报表导出\n"
            "def export_patrol_rows(rows: list) -> str:\n"
            '    return "\\n".join(",".join(str(v) for v in r) for r in rows)\n'
        ),
        "docs/迁移说明.md": (
            "# 迁移说明\n\n"
            "- 2026-08-31：定期检测计划功能下线，检测任务改由市级检测平台统一排期，"
            "schedule_span_inspection 已从本仓库删除。\n"
        ),
        "README.md": "# 云澜市桥梁养护管理平台\n\n功能范围变更见 docs/迁移说明.md。\n",
    },
    turns=[{
        "prompt": "定期检测排期函数 schedule_span_inspection 定义在哪个文件里？我要确认检测周期的取值。",
        "expect": {
            "output_contains": ["schedule_span_inspection"],
            "output_contains_any": words,
            "output_excludes": ["就定义在 bridge/schedule.py", "函数定义在 bridge/schedule.py", "是在 bridge/schedule.py 里定义", "定义位置是 bridge/schedule.py", "定义位置在 bridge/schedule.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# 云澜市桥梁养护管理平台", "docs/迁移说明.md", "# 迁移说明",
                       "schedule_span_inspection", "schedule_span_repair", words),
    notes='''
## Traps
- TR-ABSENT: bridge/ 下没有任何定义 schedule_span_inspection 的文件；docs/迁移说明.md 写明定期检测计划 2026-08-31 下线、schedule_span_inspection 已删除。
- TR-NEARNAME: bridge/schedule.py 里有名字相近的 schedule_span_repair（桥面修补排期）。把「检测排期在 bridge/schedule.py」当成答案就是诱饵。

## Reference solution
1. 搜索 schedule_span_inspection：没有定义，只在 docs/迁移说明.md 里有删除记录。
2. 读 docs/迁移说明.md 与 bridge/ 下的文件：检测任务改由市级检测平台排期；名字相近的只有桥面修补函数。
终答（2–4 句）：schedule_span_inspection 在代码库里已经不存在：bridge/ 目录下只有名字相近的 schedule_span_repair，那是桥面修补作业排期，不是检测排期；docs/迁移说明.md 写明定期检测计划 2026-08-31 已下线，检测任务改由市级检测平台统一排期。检测周期取值要到市级检测平台确认，或者找迁移前的仓库版本。判据：包含「schedule_span_inspection」和一个否定/下线说法，不得把 bridge/schedule.py 当成定义位置。

## Why the answer is unique
schedule_span_repair 的 docstring 与函数名都写明它处理的是桥面修补作业，和定期检测排期是两件事；迁移说明写明检测排期功能已下线并移出本仓库。工作区里不存在任何 schedule_span_inspection 的定义，唯一站得住的回答是说明符号不存在、点出相近函数不是它、指向市级检测平台。
''',
)

# ---------------------------------------------------------------- code-8006
words = NEG_EN + ["removed", "rewrite", "different interface", "not a rename"]
write_case(
    "code-8006",
    desc="Asks where the DockAllocator class is defined; the v1 class was removed and the "
         "package defines a separately rewritten V2 allocator",
    task_type="locate_definition", family="fam-code-b10-dockalloc-01", level="L2", ref_calls=2,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "fleet/allocator.py"},
    axes=["DEC", "OBS"],
    files={
        "fleet/allocator.py": (
            '"""Dock allocation for the Spokecraft rider app."""\n'
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class Dock:\n"
            "    dock_id: str\n"
            "    station: str\n"
            "    slots: int\n"
            "\n"
            "\n"
            "class DockAllocatorV2:\n"
            '    """Rebalanced allocator: picks the dock with the most free slots."""\n'
            "\n"
            "    def __init__(self, docks):\n"
            "        self.docks = list(docks)\n"
            "\n"
            "    def best_dock(self, station: str) -> Dock:\n"
            "        candidates = [d for d in self.docks if d.station == station and d.slots > 0]\n"
            "        if not candidates:\n"
            "            raise LookupError(station)\n"
            "        return max(candidates, key=lambda d: d.slots)\n"
        ),
        "fleet/trips.py": (
            '"""Trip bookkeeping helpers for the fleet service."""\n'
            "\n"
            "\n"
            "def close_trip(trip: dict, ended_at: str) -> dict:\n"
            '    trip["ended_at"] = ended_at\n'
            "    return trip\n"
        ),
        "CHANGELOG.md": (
            "# Changelog\n\n"
            "## 2026-08-31\n"
            "- Removed the v1 DockAllocator class. Dock allocation now runs on DockAllocatorV2, "
            "a separate rewrite with a different interface; it is not a rename of the old "
            "class.\n"
        ),
        "README.md": ("# Spokecraft fleet service\n\nDock allocation lives in the fleet "
                      "package; recent changes are in CHANGELOG.md.\n"),
    },
    turns=[{
        "prompt": "Where is the DockAllocator class defined in this codebase? I need to check "
                  "its scoring weights.",
        "expect": {
            "output_contains": ["DockAllocator"],
            "output_contains_any": words,
            "output_excludes": ["is defined in fleet/allocator.py", "It's defined in fleet/allocator.py", "is located in fleet/allocator.py", "can be found in fleet/allocator.py", "Defined in fleet/allocator.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# Spokecraft fleet service", "CHANGELOG.md", "# Changelog",
                       "DockAllocator", "DockAllocatorV2", words),
    notes='''
## Traps
- TR-ABSENT: no file defines the DockAllocator class; CHANGELOG.md records the v1 class as removed on 2026-08-31.
- TR-DECOY: fleet/allocator.py defines the similarly named DockAllocatorV2. Calling DockAllocatorV2 the DockAllocator class is the decoy answer; the changelog states it is a separate rewrite with a different interface, not a rename.

## Reference solution
1. Search for DockAllocator: no class definition; only the CHANGELOG.md entry about the removal.
2. Read CHANGELOG.md and the fleet package: DockAllocatorV2 is a separate rewrite with a different interface.
Final answer (2-4 sentences): The DockAllocator class is not in the codebase any more: the fleet package only defines DockAllocatorV2, a separate rewrite with a different interface, not a rename of the old class. CHANGELOG.md records the v1 DockAllocator as removed on 2026-08-31. For the old scoring weights, check the changelog history or ask the fleet team for the v2 allocator's spec. Criteria: mentions DockAllocator and a removed/rewrite phrase; must not present fleet/allocator.py as the definition site.

## Why the answer is unique
DockAllocatorV2 is a different class with a different interface, and the changelog explicitly says it is not a rename, so naming it as the DockAllocator definition is the decoy answer. No file in the workspace defines DockAllocator, so the only defensible reply is that the class is gone and where its replacement is described.
''',
)

# ---------------------------------------------------------------- code-8007
words = NEG_EN + ["removed", "telemetry", "approximation", "not the same"]
write_case(
    "code-8007",
    desc="Asks where a battery health score function is defined; it was removed to a telemetry "
         "service and the package has a similarly named index function",
    task_type="locate_definition", family="fam-code-b10-packhealth-01", level="L2", ref_calls=2,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "battery/health.py"},
    axes=["DEC", "ERR"],
    files={
        "battery/health.py": (
            '"""Pack health metrics for the Voltway battery library."""\n'
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class PackSnapshot:\n"
            "    cycles: int\n"
            "    depth_of_discharge: float\n"
            "    temp_max_c: float\n"
            "\n"
            "\n"
            "def pack_health_index(snapshot: PackSnapshot) -> int:\n"
            '    """Weighted 0-100 index shown on the fleet dashboard."""\n'
            "    score = 100\n"
            "    score -= snapshot.cycles // 50\n"
            "    score -= int(snapshot.depth_of_discharge * 20)\n"
            "    score -= int(max(0.0, snapshot.temp_max_c - 45.0) * 2)\n"
            "    return max(0, min(100, score))\n"
            "\n"
            "\n"
            "def packs_below_threshold(snapshots, threshold: int) -> list:\n"
            "    return [s for s in snapshots if pack_health_index(s) < threshold]\n"
        ),
        "battery/warranty.py": (
            '"""Warranty lookup helpers."""\n'
            "\n"
            "\n"
            "def packs_in_warranty(snapshots, months: int) -> list:\n"
            "    return [s for s in snapshots if s.cycles < months * 30]\n"
        ),
        "docs/scoring.md": (
            "# Scoring\n\n"
            "pack_health_score (0-1 scale) was removed on 2026-08-31, when scoring moved to the "
            "telemetry service. The battery package's pack_health_index is a different 0-100 "
            "dashboard approximation and does not replace it.\n"
        ),
        "README.md": ("# Voltway battery library\n\nHealth metrics live in the battery "
                      "package; see docs/scoring.md for the old score.\n"),
    },
    turns=[{
        "prompt": "Where is pack_health_score defined in this repo? The warranty team wants its "
                  "exact weights.",
        "expect": {
            "output_contains": ["pack_health_score"],
            "output_contains_any": words,
            "output_excludes": ["is defined in battery/health.py", "It's defined in battery/health.py", "is located in battery/health.py", "can be found in battery/health.py", "Defined in battery/health.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# Voltway battery library", "docs/scoring.md", "# Scoring",
                       "pack_health_score", "pack_health_index", words),
    notes='''
## Traps
- TR-ABSENT: no file defines pack_health_score; docs/scoring.md records it as removed on 2026-08-31, when scoring moved to the telemetry service.
- TR-NEARNAME: battery/health.py defines the similarly named pack_health_index (a 0-100 dashboard approximation). Presenting it as pack_health_score is the decoy answer.

## Reference solution
1. Search for pack_health_score: no definition; only the docs/scoring.md note about the removal.
2. Read docs/scoring.md and the battery package: the index is a different 0-100 dashboard metric.
Final answer (2-4 sentences): pack_health_score is not defined in this repo any more: the battery package only has the similarly named pack_health_index, a 0-100 dashboard approximation that is not the same metric. docs/scoring.md records the old score as removed on 2026-08-31, when scoring moved to the telemetry service. The warranty team should get the exact weights from the telemetry service. Criteria: mentions pack_health_score and a removed/telemetry phrase; must not present battery/health.py as the definition site.

## Why the answer is unique
pack_health_index has a different scale and purpose, and docs/scoring.md states it does not replace the removed score, so presenting it as pack_health_score is the decoy answer. No file in the workspace defines pack_health_score, so the only defensible reply is that the function is gone and where the metric lives now.
''',
)

# ---------------------------------------------------------------- code-8008
words = NEG_EN + ["removed", "permit platform", "unrelated", "moved"]
write_case(
    "code-8008",
    desc="Asks where a dock zone resolver is defined; it was removed to a permit platform and "
         "the package has a similarly named fee helper",
    task_type="locate_definition", family="fam-code-b10-dockzone-01", level="L2", ref_calls=2,
    traps=["TR-ABSENT", "TR-NEARNAME"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-NEARNAME": "geo/zones.py"},
    axes=["DEC", "ERR"],
    files={
        "geo/zones.py": (
            '"""Zone rules for the Cyclelet dock map."""\n'
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class ZoneRule:\n"
            "    zone: str\n"
            "    fee_cents: int\n"
            "    max_minutes: int\n"
            "\n"
            "\n"
            "def resolve_zone_fee(rule: ZoneRule, minutes: int) -> int:\n"
            '    """Parking fee for a stay, capped at one day."""\n'
            "    cap = min(minutes, 1440)\n"
            "    return rule.fee_cents * cap\n"
        ),
        "geo/map.py": (
            '"""Tile rendering for the public dock map."""\n'
            "\n"
            "\n"
            "def render_tiles(tiles: list) -> str:\n"
            '    return "\\n".join(sorted(tiles))\n'
        ),
        "docs/migration.md": (
            "# Migration notes\n\n"
            "resolve_dock_zone was removed on 2026-08-31, when zone assignment moved to the "
            "permit platform. The fee helpers in geo/ are unrelated to zone assignment.\n"
        ),
        "README.md": ("# Cyclelet dock map\n\nZone assignment moved off this repo; see "
                      "docs/migration.md.\n"),
    },
    turns=[{
        "prompt": "Where is resolve_dock_zone defined? Parking-permit auditing needs its zone "
                  "rules.",
        "expect": {
            "output_contains": ["resolve_dock_zone"],
            "output_contains_any": words,
            "output_excludes": ["is defined in geo/zones.py", "It's defined in geo/zones.py", "is located in geo/zones.py", "can be found in geo/zones.py", "Defined in geo/zones.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# Cyclelet dock map", "docs/migration.md", "# Migration notes",
                       "resolve_dock_zone", "resolve_zone_fee", words),
    notes='''
## Traps
- TR-ABSENT: no file defines resolve_dock_zone; docs/migration.md records it as removed on 2026-08-31, when zone assignment moved to the permit platform.
- TR-NEARNAME: geo/zones.py defines the similarly named resolve_zone_fee (a parking-fee helper). Presenting it as resolve_dock_zone is the decoy answer.

## Reference solution
1. Search for resolve_dock_zone: no definition; only the docs/migration.md note about the removal.
2. Read docs/migration.md and geo/: the fee helper is unrelated to zone assignment.
Final answer (2-4 sentences): resolve_dock_zone is not defined in this repo: geo/ only has the similarly named resolve_zone_fee, a parking-fee helper that is unrelated to zone assignment. docs/migration.md records resolve_dock_zone as removed on 2026-08-31, when zone assignment moved to the permit platform. The zone rules live on the permit platform now. Criteria: mentions resolve_dock_zone and a removed/permit-platform phrase; must not present geo/zones.py as the definition site.

## Why the answer is unique
resolve_zone_fee computes parking fees and nothing in it assigns zones, so presenting it as the zone resolver is the decoy answer. No file in the workspace defines resolve_dock_zone, so the only defensible reply is that the function is gone and where zone assignment lives now.
''',
)

# ---------------------------------------------------------------- code-8009
words = NEG_EN + ["deleted", "wallet", "moved", "no rounding"]
write_case(
    "code-8009",
    desc="Asks where a rental credit function is defined; it was deleted when credits moved to "
         "the wallet service and the module has a similarly named apply function",
    task_type="locate_definition", family="fam-code-b10-rentalcredit-01", level="L2",
    ref_calls=2,
    traps=["TR-ABSENT", "TR-DECOY"],
    decoys={"TR-ABSENT": "UNKNOWN", "TR-DECOY": "rental/credit.py"},
    axes=["DEC", "OBS"],
    files={
        "rental/credit.py": (
            '"""Ride credits for the Glidepool rental core."""\n'
            "from dataclasses import dataclass\n"
            "\n"
            "\n"
            "@dataclass\n"
            "class RideRecord:\n"
            "    ride_id: str\n"
            "    minutes: int\n"
            "    delay_minutes: int\n"
            "\n"
            "\n"
            "def apply_rental_credit(record: RideRecord, balance_cents: int) -> int:\n"
            '    """Post an already-computed credit to a rider balance (cents)."""\n'
            "    return balance_cents + record.delay_minutes * 3\n"
            "\n"
            "\n"
            "def credit_statement(records: list) -> str:\n"
            "    total = sum(r.delay_minutes * 3 for r in records)\n"
            '    return "total credit: %d cents" % total\n'
        ),
        "rental/pricing.py": (
            '"""Per-minute pricing for rides."""\n'
            "\n"
            "\n"
            "def ride_price(minutes: int, rate_cents: int) -> int:\n"
            "    return minutes * rate_cents\n"
        ),
        "CHANGELOG.md": (
            "# Changelog\n\n"
            "## 2026-08-31\n"
            "- compute_rental_credit was deleted when credit calculation moved to the wallet "
            "service. apply_rental_credit only posts an already-computed credit and uses no "
            "rounding rule; it is not the old function under a new name.\n"
        ),
        "README.md": ("# Glidepool rental core\n\nCredit calculation moved to the wallet "
                      "service; see CHANGELOG.md.\n"),
    },
    turns=[{
        "prompt": "Where is compute_rental_credit defined? Refund auditing needs its rounding "
                  "rule.",
        "expect": {
            "output_contains": ["compute_rental_credit"],
            "output_contains_any": words,
            "output_excludes": ["is defined in rental/credit.py", "It's defined in rental/credit.py", "is located in rental/credit.py", "can be found in rental/credit.py", "Defined in rental/credit.py"],
            "max_output_chars": 600,
        },
    }],
    verify=code_verify("# Glidepool rental core", "CHANGELOG.md", "# Changelog",
                       "compute_rental_credit", "apply_rental_credit", words),
    notes='''
## Traps
- TR-ABSENT: no file defines compute_rental_credit; CHANGELOG.md records it as deleted on 2026-08-31, when credit calculation moved to the wallet service.
- TR-DECOY: rental/credit.py defines the similarly named apply_rental_credit (posts an already-computed credit, no rounding rule). Presenting it as compute_rental_credit is the decoy answer.

## Reference solution
1. Search for compute_rental_credit: no definition; only the CHANGELOG.md entry about the deletion.
2. Read CHANGELOG.md and rental/credit.py: apply_rental_credit only posts credits and uses no rounding rule.
Final answer (2-4 sentences): compute_rental_credit is not in the codebase: rental/ only has the similarly named apply_rental_credit, which posts an already-computed credit and uses no rounding rule. CHANGELOG.md records compute_rental_credit as deleted on 2026-08-31, when credit calculation moved to the wallet service. The rounding rule lives in the wallet service now. Criteria: mentions compute_rental_credit and a deleted/wallet phrase; must not present rental/credit.py as the definition site.

## Why the answer is unique
apply_rental_credit does no rounding and only posts a computed credit, and the changelog states it is not the old function under a new name, so presenting it as compute_rental_credit is the decoy answer. No file in the workspace defines compute_rental_credit, so the only defensible reply is that the function is gone and where the rounding rule lives now.
''',
)
