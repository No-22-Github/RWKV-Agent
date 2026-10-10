"""b10a (v1.4 §3.2 M2) batch F: 「只能回答一部分」 partial-answer cases, 20 items.

Shape follows the b10 pilot's tab-8002: one complete source, one partial source
(migration cutoff / missing export page / channel that stopped being exported),
the gap documented inside the workspace, the complete source's total is the
certain part, and presenting the sum of everything present as the full total is
the TR-ABSENT decoy; reading a single source is the TR-MULTISRC decoy.

Themes: Chinese cases take proper names from a gym chain (岳川健身), English
cases from a farmers market (Thistledown Market).  Run:
    cd bench/distill/tools/b10a && python3 m2f.py
"""
import json
import random
import re

from common import revised

write_case = revised({cid: "去掉部分合计的排除：S5 三遍老师都给出「已记录合计 X，但不完整」，这是 v1.4 §4.1「只能答一部分」示范的写法，被排除词误判；完整性改由逐条读终答把关。" for cid in ['tab-8034', 'tab-8035', 'tab-8036', 'tab-8037', 'tab-8038', 'tab-8039', 'tab-8040', 'tab-8041', 'log-8028', 'log-8029', 'log-8030', 'log-8031', 'log-8032', 'log-8033', 'doc-8020', 'doc-8021', 'doc-8022', 'fs-8020', 'fs-8021', 'fs-8022']})

NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")


def corruptible_numbers(text):
    """Mirror of bank verify's numberMatches: the standalone numbers Go's
    sabotage would consider (+1 on the first one equal to the judged value)."""
    out = []
    for m in NUM_RE.finditer(text):
        s, e = m.start(), m.end()
        if s > 0 and (text[s - 1].isalnum() or text[s - 1] in "_."):
            continue
        if e < len(text) and (text[e].isalnum() or text[e] in "_."):
            continue
        out.append(m.group())
    return out


def assert_value_absent(files, *values):
    """The judged value must not appear as a corruptible literal in any file,
    or the sabotage would corrupt a literal verify.py never reads and pass."""
    for path, content in files.items():
        for tok in corruptible_numbers(content):
            try:
                f = float(tok)
            except ValueError:
                continue
            for v in values:
                assert abs(f - v) > 0.01, ("value collision", path, tok, v)


def both(num):
    """Bare and thousands-separated spellings of a judged/decoy number."""
    if isinstance(num, float):
        bare = "%.2f" % num
        grouped = "{:,.2f}".format(num)
    else:
        bare = str(num)
        grouped = "{:,}".format(num)
    return [bare] if bare == grouped else [bare, grouped]


def money(x):
    return "%.2f" % x


TOOL_NAMES = ("list_files", "read_file", "search_text", "read_lines",
              "write_file", "replace_lines", "append_file", "calculator",
              "data_query", "datetime", "web_search", "web_fetch", "get_weather")
FORBIDDEN_PHRASES = ("if missing", "may not exist", "both files", "all logs",
                     "merge", "quick", "simple", "just", "carefully", "note that")


def check_prompt(prompt):
    low = prompt.lower()
    for word in TOOL_NAMES:
        assert word not in low, ("tool name in prompt", word)
    for phrase in FORBIDDEN_PHRASES:
        assert phrase not in low, ("forbidden phrase in prompt", phrase)


def check_ref(answer, certain_strs, excludes, gap_words):
    """The reference final answer must carry the certain value (either
    spelling) and a gap word, and must never carry an excluded
    (incomplete-total) spelling."""
    assert any(s in answer for s in certain_strs), \
        ("certain value missing from reference answer", certain_strs)
    for e in excludes:
        assert e not in answer, ("excluded value in reference answer", e)
    assert any(g in answer for g in gap_words), "no gap word in reference answer"


GAP_ZH = ["补录", "补齐", "补导", "补传", "补页", "补回", "补上", "补交",
          "迁移", "切换", "更换", "换到", "换新", "迁到", "搬到", "并入", "代收",
          "接入", "没再接", "新系统", "新平台",
          "未导出", "没导出", "还没导出", "尚未导出", "没有导出",
          "未同步", "没同步", "还没同步", "尚未同步", "没有同步",
          "未归档", "还没归档", "尚未归档", "没有归档",
          "暂缺", "缺页", "缺失", "导出失败"]

GAP_EN = ["not exported", "no export", "never exported", "not yet exported",
          "not yet been exported", "hasn't been exported", "haven't been exported",
          "hadn't been exported", "isn't exported", "aren't exported",
          "not been copied", "hasn't been copied", "haven't been copied",
          "not been entered", "hasn't been entered", "haven't been entered",
          "not been synced", "hasn't been synced", "haven't been synced",
          "not been transferred", "hasn't been transferred", "haven't been transferred",
          "not been imported", "hasn't been imported", "haven't been imported",
          "backfill", "backfilled", "backfilling",
          "migration", "migrated", "cutover", "switched over",
          "re-scanning", "rescanning", "re-scan", "rescanned",
          "missing pages", "pages are missing", "didn't transfer",
          "in batches", "October batch", "county portal",
          "new processor", "new system", "new platform", "new portal",
          "new dashboard", "new bookkeeping"]

TRAPS = ["TR-ABSENT", "TR-MULTISRC"]
AXES = ["DEC", "CHN"]


# ---------------------------------------------------------------- tab-8034
rng = random.Random(80341)
stores4 = ["滨江店", "城北店", "大学城店", "老城根店"]
gate_base = {"滨江店": 58, "城北店": 47, "大学城店": 39, "老城根店": 31}
gate_rows = []
for d in range(1, 31):
    for st in stores4:
        gate_rows.append((st, "2026-09-%02d" % d, gate_base[st] + rng.randint(-6, 8)))
qr_rows = []
for d in range(1, 16):
    for st in stores4:
        qr_rows.append((st, "2026-09-%02d" % d, rng.randint(3, 14)))
t34_gate = sum(r[2] for r in gate_rows)
t34_qr = sum(r[2] for r in qr_rows)
t34_all = t34_gate + t34_qr
assert 4600 <= t34_gate <= 6100 and 200 <= t34_qr <= 800
files_8034 = {
    "数据/门店端-9月.csv": "门店,日期,进店人次\n" + "".join("%s,%s,%d\n" % r for r in gate_rows),
    "数据/小程序端-9月.csv": "门店,日期,进店人次\n" + "".join("%s,%s,%d\n" % r for r in qr_rows),
    "数据/README.md": "# 岳川健身 进店人次台账\n\n进店人次分两个渠道记录：门店闸机（门店端）和小程序预约码（小程序端）。\n小程序端 9 月 16 日起切换到新会员系统，切换之后的记录尚未导出，预计 10 月中旬补录。\n",
}
assert_value_absent(files_8034, t34_gate, t34_all)
p_8034 = "岳川健身 9 月所有渠道的进店人次一共是多少？帮我统计一下。"
check_prompt(p_8034)
r_8034 = ("门店闸机 9 月一共进店 %d 人次，这个数是全的；小程序预约码只记录到 9 月 15 日"
          "（%d 人次），16 日以后的记录因为切换新会员系统还没导出，预计 10 月中旬补录，"
          "所以全月全渠道合计现在给不出。等补录之后我可以再合计一次。" % (t34_gate, t34_qr))
check_ref(r_8034, both(t34_gate), both(t34_all), GAP_ZH)
write_case(
    "tab-8034",
    desc="Asks September walk-ins across all channels for a gym chain; the mini-program channel switched to a new membership system and records after Sep 15 are unexported, so only the gate-side total is certain",
    task_type="aggregate", family="fam-tab-b10-gymcheckin-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(t34_all), "TR-MULTISRC": str(t34_gate)},
    axes=AXES,
    files=files_8034,
    turns=[{
        "prompt": p_8034,
        "expect": {
            "output_contains_any": both(t34_gate),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
gate = list(csv.DictReader(io.StringIO(files["数据/门店端-9月.csv"])))
qr = list(csv.DictReader(io.StringIO(files["数据/小程序端-9月.csv"])))
assert gate and list(gate[0]) == ["门店", "日期", "进店人次"]
assert qr and list(qr[0]) == ["门店", "日期", "进店人次"]
assert len(gate) == 120 and len(qr) == 60
# 门店端 covers all four stores on all 30 days; 小程序端 stops at 09-15.
assert {(r["门店"], r["日期"]) for r in gate} == {
    (s, "2026-09-" + str(d).zfill(2)) for s in ("滨江店", "城北店", "大学城店", "老城根店")
    for d in range(1, 31)}
assert {r["日期"] for r in qr} == {"2026-09-" + str(d).zfill(2) for d in range(1, 16)}
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 进店人次台账")
assert "尚未导出" in readme and "补录" in readme
total = sum(int(r["进店人次"]) for r in gate)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 数据/小程序端-9月.csv 只有 9 月 1 日至 15 日的记录（{t34_qr} 人次）；数据/README.md 写明小程序端 9 月 16 日起切换到新会员系统，切换之后的记录尚未导出、预计 10 月中旬补录。把 {t34_gate} + {t34_qr} = {t34_all} 当成全月全渠道合计就是诱饵答案。
- TR-MULTISRC: 只看门店端一个文件会得到 {t34_gate}，漏掉小程序渠道。

## Reference solution
1. 列出 数据/：两份 CSV 和 README。
2. 汇总门店端 CSV：四家门店 9 月全月共 {t34_gate} 人次，覆盖完整。
3. 读小程序端 CSV 与 README：只到 9 月 15 日（{t34_qr} 人次），之后尚未导出。
终答（2–4 句）：{r_8034}判据：包含 {t34_gate}（任一写法）；部分合计 {t34_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{t34_all} 只覆盖小程序端的前 15 天，README 明确之后的记录还没导出，把它报成全月合计是错的；{t34_gate} 漏了小程序渠道。能确定的只有门店端的全月数和小程序端截至 15 日的数，所以正确回答是给出确定部分并点名缺口。
''',
)

# ---------------------------------------------------------------- tab-8035
rng = random.Random(80352)
courses4 = ["搏击操", "动感单车", "瑜伽", "杠铃塑形"]
front_rows = []
for d in range(1, 31):
    for c in courses4:
        front_rows.append(("2026-09-%02d" % d, c, rng.randint(8, 22)))
mini_rows = []
for d in list(range(1, 8)) + list(range(13, 19)):
    for c in courses4:
        mini_rows.append(("2026-09-%02d" % d, c, rng.randint(5, 15)))
t35_front = sum(r[2] for r in front_rows)
t35_mini = sum(r[2] for r in mini_rows)
t35_all = t35_front + t35_mini
assert 1400 <= t35_front <= 2200 and 180 <= t35_mini <= 700
files_8035 = {
    "数据/前台登记-9月.csv": "日期,课程,预约人数\n" + "".join("%s,%s,%d\n" % r for r in front_rows),
    "数据/小程序预约-9月.csv": "日期,课程,预约人数\n" + "".join("%s,%s,%d\n" % r for r in mini_rows),
    "数据/导出说明.md": "# 团课预约导出说明\n\n前台登记每日全量导出一份。小程序预约表按周分页导出，9 月 8 日至 12 日这一页当时导出失败暂缺，运维正在补页，预计 10 月 9 日补齐。\n",
}
assert_value_absent(files_8035, t35_front, t35_all)
p_8035 = "岳川健身 9 月前台和小程序两端一共受理了多少人次团课预约？"
check_prompt(p_8035)
r_8035 = ("前台 9 月受理 %d 人次团课预约，这份登记是全月的；小程序端目前只有 9 月 1 日到 7 日"
          "和 13 日到 18 日的记录（%d 人次），8 日到 12 日那一页导出失败暂缺，正在补页、"
          "预计 10 月 9 日补齐，所以两端的全月合计现在定不下来。补齐之后我再重新合计一次。"
          % (t35_front, t35_mini))
check_ref(r_8035, both(t35_front), both(t35_all), GAP_ZH)
write_case(
    "tab-8035",
    desc="Asks September class bookings across the front desk and the mini-program; the mini-program export lost one week's page to a failed export, so only the front-desk total is certain",
    task_type="aggregate", family="fam-tab-b10-gymcheckin-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(t35_all), "TR-MULTISRC": str(t35_front)},
    axes=AXES,
    files=files_8035,
    turns=[{
        "prompt": p_8035,
        "expect": {
            "output_contains_any": both(t35_front),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
front = list(csv.DictReader(io.StringIO(files["数据/前台登记-9月.csv"])))
mini = list(csv.DictReader(io.StringIO(files["数据/小程序预约-9月.csv"])))
assert front and list(front[0]) == ["日期", "课程", "预约人数"]
assert mini and list(mini[0]) == ["日期", "课程", "预约人数"]
assert len(front) == 120 and len(mini) == 52
all_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {r["日期"] for r in front} == all_days
missing = {"2026-09-" + str(d).zfill(2) for d in range(8, 13)}
have = {"2026-09-" + str(d).zfill(2) for d in list(range(1, 8)) + list(range(13, 19))}
assert {r["日期"] for r in mini} == have and not (have & missing)
note = files["数据/导出说明.md"]
assert note.splitlines()[0].startswith("# 团课预约导出说明")
assert "暂缺" in note and "补页" in note and "补齐" in note
total = sum(int(r["预约人数"]) for r in front)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 数据/小程序预约-9月.csv 只有 9 月 1–7 日和 13–18 日的记录（{t35_mini} 人次），8–12 日那一页导出失败暂缺；数据/导出说明.md 写明正在补页、预计 10 月 9 日补齐。把 {t35_front} + {t35_mini} = {t35_all} 当成两端全月合计就是诱饵答案。
- TR-MULTISRC: 只看前台登记会得到 {t35_front}，漏掉小程序端。

## Reference solution
1. 列出 数据/：两份 CSV 和导出说明。
2. 汇总前台登记：9 月全月 {t35_front} 人次，覆盖完整。
3. 读小程序预约表与导出说明：缺 8–12 日一页，现有 {t35_mini} 人次，正在补页。
终答（2–4 句）：{r_8035}判据：包含 {t35_front}（任一写法）；部分合计 {t35_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{t35_all} 把缺页前后的现存记录当成了全月合计，而 8–12 日的预约根本不在数据里，说明文件也写明只是暂缺、要等补页，所以它不是全月数；{t35_front} 漏了小程序端。能确定的只有前台的全月数和小程序端现存页的人数，正确回答是给出确定部分、点名缺页并给出补齐后重算的下一步。
''',
)

# ---------------------------------------------------------------- tab-8036
rng = random.Random(80363)
shop_stores = ["滨江店", "城北店", "老城根店"]
shop_rows = []
for d in range(1, 31):
    for st in shop_stores[:2]:
        shop_rows.append((st, "2026-09-%02d" % d, round(rng.uniform(1600, 5400), 2)))
for d in range(1, 11):
    shop_rows.append(("老城根店", "2026-09-%02d" % d, round(rng.uniform(2800, 4900), 2)))
shop_rows.sort(key=lambda r: (r[1], r[0]))
t36_full = round(sum(r[2] for r in shop_rows if r[0] != "老城根店"), 2)
t36_old = round(sum(r[2] for r in shop_rows if r[0] == "老城根店"), 2)
t36_all = round(t36_full + t36_old, 2)
assert 150000 <= t36_full <= 260000 and 25000 <= t36_old <= 55000
files_8036 = {
    "数据/收银流水-9月.csv": "门店,日期,销售额\n" + "".join("%s,%s,%s\n" % (r[0], r[1], money(r[2])) for r in shop_rows),
    "数据/README.md": "# 岳川健身 商品部收银台账\n\n销售额为当日含税零售额，单位元。\n老城根店 9 月 11 日起更换收银系统，新系统里的流水尚未导出，预计 9 月 30 日前由厂商补导。\n",
}
assert_value_absent(files_8036, t36_full, t36_all)
p_8036 = "岳川健身 9 月三家门店的商品销售额一共是多少？"
check_prompt(p_8036)
r_8036 = ("滨江店和城北店的收银流水是全月的，两家合计 %s 元，这部分可以确定；老城根店只导出到 "
          "9 月 10 日（%s 元），11 日以后换了新收银系统还没导出，预计 9 月 30 日前由厂商补导，"
          "三家门店的全月合计现在算不出来。补导之后我再算一次。" % (money(t36_full), money(t36_old)))
check_ref(r_8036, both(t36_full), both(t36_all), GAP_ZH)
write_case(
    "tab-8036",
    desc="Asks September retail sales across three gym stores; the third store swapped its POS on Sep 11 and its later takings are unexported, so only the two complete stores' total is certain",
    task_type="aggregate", family="fam-tab-b10-gymshop-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(t36_all), "TR-MULTISRC": money(t36_full)},
    axes=AXES,
    files=files_8036,
    turns=[{
        "prompt": p_8036,
        "expect": {
            "output_contains_any": both(t36_full),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
rows = list(csv.DictReader(io.StringIO(files["数据/收银流水-9月.csv"])))
assert rows and list(rows[0]) == ["门店", "日期", "销售额"]
assert len(rows) == 70
full_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {(r["门店"], r["日期"]) for r in rows if r["门店"] != "老城根店"} == {
    (s, d) for s in ("滨江店", "城北店") for d in full_days}
old_days = {r["日期"] for r in rows if r["门店"] == "老城根店"}
assert len(old_days) == 10 and max(old_days) == "2026-09-10"
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 商品部收银台账")
assert "尚未导出" in readme and "补导" in readme
total = round(sum(float(r["销售额"]) for r in rows if r["门店"] != "老城根店"), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 数据/收银流水-9月.csv 里老城根店只有 9 月 1–10 日的记录（{money(t36_old)} 元）；数据/README.md 写明老城根店 9 月 11 日起更换收银系统、新系统里的流水尚未导出、预计 9 月 30 日前补导。把 {money(t36_full)} + {money(t36_old)} = {money(t36_all)} 当成三家门店全月合计就是诱饵答案。
- TR-MULTISRC: 只汇总滨江店一家（或漏掉任何一家完整门店）都得不到 {money(t36_full)} 这个确定数。

## Reference solution
1. 列出 数据/：收银流水 CSV 和 README。
2. 按门店分组汇总：滨江店与城北店全月流水完整，合计 {money(t36_full)} 元。
3. 读 README：老城根店只到 9 月 10 日（{money(t36_old)} 元），之后尚未导出。
终答（2–4 句）：{r_8036}判据：包含 {money(t36_full)}（任一写法）；部分合计 {money(t36_all)} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{money(t36_all)} 把老城根店缺了 20 天的流水当成全月，README 明确 11 日以后的流水还没导出，所以它不是三家门店的全月合计；只报任何一家门店又漏了另一家完整门店。能确定的只有两家完整门店的合计和老城根店已导出的部分，正确回答是给出确定部分、点名缺口并给出补导后重算的下一步。
''',
)

# ---------------------------------------------------------------- tab-8037
rng = random.Random(80374)
market_days = ["2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12",
               "2026-09-15", "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"]
card_rows = [(d, t, round(rng.uniform(320, 620), 2)) for d in market_days for t in ("T1", "T2")]
mob_rows = [(d, round(rng.uniform(180, 460), 2)) for d in market_days[:6]]
t37_card = round(sum(r[2] for r in card_rows), 2)
t37_mob = round(sum(r[1] for r in mob_rows), 2)
t37_all = round(t37_card + t37_mob, 2)
assert 6000 <= t37_card <= 11000 and 1000 <= t37_mob <= 3000
files_8037 = {
    "data/card-takings-september.csv": "day,terminal,gross\n" + "".join("%s,%s,%s\n" % (r[0], r[1], money(r[2])) for r in card_rows),
    "data/mobile-reader-september.csv": "day,gross\n" + "".join("%s,%s\n" % (r[0], money(r[1])) for r in mob_rows),
    "data/README.md": "# Thistledown Market card takings\n\nGross amounts are in pounds, as settled by the processor. The two market terminals settle through the market's own account and are complete for September.\nThe borrowed mobile reader was re-registered to the new processor account on 2026-09-22; takings from that day on haven't been exported yet and should arrive once the processor finishes the account migration.\n",
}
assert_value_absent(files_8037, t37_card, t37_all)
p_8037 = "How much did Thistledown Market take across all its card readers in September?"
check_prompt(p_8037)
r_8037 = ("The market's two card terminals took %s pounds in September, and that figure is complete. "
          "The borrowed mobile reader only has takings through 19 September (%s pounds); from the 22nd on "
          "its takings settled on the new processor account and haven't been exported yet, so the September "
          "total across all readers cannot be settled yet. I can re-run the total once the processor exports "
          "the missing days." % (money(t37_card), money(t37_mob)))
check_ref(r_8037, both(t37_card), both(t37_all), GAP_EN)
write_case(
    "tab-8037",
    desc="Asks September card takings across the market's terminals and a borrowed mobile reader; the reader moved to a new processor account mid-month and later days are unexported, so only the terminal total is certain",
    task_type="aggregate", family="fam-tab-b10-farmcards-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(t37_all), "TR-MULTISRC": money(t37_card)},
    axes=AXES,
    files=files_8037,
    turns=[{
        "prompt": p_8037,
        "expect": {
            "output_contains_any": both(t37_card),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
card = list(csv.DictReader(io.StringIO(files["data/card-takings-september.csv"])))
mob = list(csv.DictReader(io.StringIO(files["data/mobile-reader-september.csv"])))
assert card and list(card[0]) == ["day", "terminal", "gross"]
assert mob and list(mob[0]) == ["day", "gross"]
days9 = {"2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"}
assert len(card) == 18 and {(r["day"], r["terminal"]) for r in card} == {
    (d, t) for d in days9 for t in ("T1", "T2")}
assert len(mob) == 6 and {r["day"] for r in mob} == {
    "2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15", "2026-09-19"}
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market card takings")
assert "haven't been exported" in readme and "migration" in readme
total = round(sum(float(r["gross"]) for r in card), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: data/mobile-reader-september.csv only covers six market days through 19 September ({money(t37_mob)} pounds); data/README.md says the reader moved to the new processor account on 22 September and takings from that day on haven't been exported yet. Presenting {money(t37_card)} + {money(t37_mob)} = {money(t37_all)} as the September total is the decoy answer.
- TR-MULTISRC: reading only one of the two files misses a channel entirely; the terminal total alone is {money(t37_card)}.

## Reference solution
1. List data/: two takings CSVs and a README.
2. Sum card-takings-september.csv: both terminals, all nine market days, {money(t37_card)} pounds complete.
3. Read mobile-reader-september.csv and the README: six days only, later days unexported pending the processor migration.
Final answer (2-4 sentences): {r_8037} Criteria: contains {money(t37_card)} (either spelling); the partial sum {money(t37_all)} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{money(t37_all)} treats six exported reader days as a full month, and the README states the later days are still on the new processor, so it is not the September total; {money(t37_card)} alone ignores the reader channel. The certain part is the terminals' complete total, and the defensible reply names the export gap and the next step.
''',
)

# ---------------------------------------------------------------- tab-8038
rng = random.Random(80385)
ws_rows = []
for d in range(1, 31):
    if rng.random() < 0.72:
        ws_rows.append(("2026-09-%02d" % d, rng.randint(40, 120)))
stand_rows = [("2026-09-%02d" % d, rng.randint(15, 35)) for d in list(range(1, 10)) + list(range(17, 27))]
t38_ws = sum(r[1] for r in ws_rows)
t38_stand = sum(r[1] for r in stand_rows)
t38_all = t38_ws + t38_stand
assert 1300 <= t38_ws <= 2300 and 250 <= t38_stand <= 750 and len(ws_rows) >= 18
files_8038 = {
    "data/wholesale-orders-september.csv": "date,dozens\n" + "".join("%s,%d\n" % r for r in ws_rows),
    "data/farm-stand-september.csv": "date,dozens\n" + "".join("%s,%d\n" % r for r in stand_rows),
    "data/README.md": "# Hollis Family Farm egg ledger\n\nWholesale orders and the farm stand are logged separately, one row per day, dozens of eggs.\nThe farm stand's ledger pages for 10-16 September went to the new bookkeeping system early and those pages didn't transfer; the bookkeeper is re-scanning them and expects them back by 6 October.\n",
}
assert_value_absent(files_8038, t38_ws, t38_all)
p_8038 = "How many dozens of eggs did Hollis Family Farm sell in September across wholesale and the farm stand?"
check_prompt(p_8038)
r_8038 = ("Wholesale orders for September add up to %d dozens, and that sheet is complete. The farm stand sheet "
          "only covers 1-9 and 17-26 September (%d dozens); the pages for 10-16 September went to the new "
          "bookkeeping system and didn't transfer, and the bookkeeper is re-scanning them with an expected return "
          "by 6 October, so the month's total across both channels cannot be totalled yet. I can re-run the sum "
          "once the missing pages are back." % (t38_ws, t38_stand))
check_ref(r_8038, both(t38_ws), both(t38_all), GAP_EN)
write_case(
    "tab-8038",
    desc="Asks September egg sales in dozens across wholesale and the farm stand; the stand's mid-month ledger pages didn't transfer to the new bookkeeping system, so only the wholesale total is certain",
    task_type="aggregate", family="fam-tab-b10-farmeggs-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(t38_all), "TR-MULTISRC": str(t38_ws)},
    axes=AXES,
    files=files_8038,
    turns=[{
        "prompt": p_8038,
        "expect": {
            "output_contains_any": both(t38_ws),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
ws = list(csv.DictReader(io.StringIO(files["data/wholesale-orders-september.csv"])))
stand = list(csv.DictReader(io.StringIO(files["data/farm-stand-september.csv"])))
assert ws and list(ws[0]) == ["date", "dozens"]
assert stand and list(stand[0]) == ["date", "dozens"]
assert len(stand) == 19
stand_days = {r["date"] for r in stand}
assert stand_days == {"2026-09-" + str(d).zfill(2) for d in list(range(1, 10)) + list(range(17, 27))}
missing = {"2026-09-" + str(d).zfill(2) for d in range(10, 17)}
assert not (stand_days & missing) and len({r["date"] for r in ws}) >= 18
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Hollis Family Farm egg ledger")
assert "didn't transfer" in readme and "re-scanning" in readme
total = sum(int(r["dozens"]) for r in ws)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: data/farm-stand-september.csv covers 1-9 and 17-26 September only ({t38_stand} dozens); data/README.md says the 10-16 September pages didn't transfer to the new bookkeeping system and are being re-scanned. Presenting {t38_ws} + {t38_stand} = {t38_all} dozens as the September total is the decoy answer.
- TR-MULTISRC: reading only the wholesale sheet gives {t38_ws} and misses the farm stand.

## Reference solution
1. List data/: two ledger CSVs and a README.
2. Sum wholesale-orders-september.csv: {t38_ws} dozens, the sheet is complete.
3. Read farm-stand-september.csv and the README: 20 days present ({t38_stand} dozens), the 10-16 pages didn't transfer.
Final answer (2-4 sentences): {r_8038} Criteria: contains {t38_ws} (either spelling); the partial sum {t38_all} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{t38_all} sums only what survived the transfer, and the README states a full week of stand pages is missing until the re-scan lands, so it is not the month's total; {t38_ws} alone ignores the stand. The wholesale sheet is complete, so its total is the certain part, and the reply should name the missing pages and the re-scan date.
''',
)

# ---------------------------------------------------------------- tab-8039
rng = random.Random(80396)
coaches4 = ["雷峻", "穆彤", "白宇轩", "黎芷晴"]
inst_rows = []
for d in range(1, 31):
    for c in coaches4:
        if rng.random() < 0.8:
            inst_rows.append(("2026-09-%02d" % d, c, rng.choice([60, 90, 120, 150, 180])))
online_rows = []
for d in range(1, 15):
    for c in coaches4:
        if rng.random() < 0.55:
            online_rows.append(("2026-09-%02d" % d, c, rng.choice([60, 90, 120])))
inst_rows.sort()
online_rows.sort()
t39_inst = sum(r[2] for r in inst_rows)
t39_on = sum(r[2] for r in online_rows)
t39_all = t39_inst + t39_on
assert 10000 <= t39_inst <= 16000 and 800 <= t39_on <= 3200 and len(inst_rows) >= 85
files_8039 = {
    "数据/到店消课-9月.csv": "日期,教练,消课分钟\n" + "".join("%s,%s,%d\n" % r for r in inst_rows),
    "数据/线上私教-9月.csv": "日期,教练,消课分钟\n" + "".join("%s,%s,%d\n" % r for r in online_rows),
    "数据/README.md": "# 岳川健身 私教消课台账\n\n消课分钟按每节课实际时长记录。\n线上私教 9 月 15 日起搬到了新的上课平台，平台里的课时还没同步回来，预计 10 月 8 日完成同步。\n",
}
assert_value_absent(files_8039, t39_inst, t39_all)
p_8039 = "9 月岳川健身到店私教加线上私教一共消了多少分钟的课？"
check_prompt(p_8039)
r_8039 = ("到店私教 9 月一共消了 %d 分钟，这份台账是全月的；线上私教只同步到 9 月 14 日（%d 分钟），"
          "15 日以后的课时因为搬到新平台还没同步回来，预计 10 月 8 日完成同步，所以两条线的全月合计"
          "现在算不出来。同步完成之后我再合计一次。" % (t39_inst, t39_on))
check_ref(r_8039, both(t39_inst), both(t39_all), GAP_ZH)
write_case(
    "tab-8039",
    desc="Asks September personal-training minutes across in-store and online sessions; the online platform moved to a new system mid-month and later sessions are unsynced, so only the in-store total is certain",
    task_type="aggregate", family="fam-tab-b10-gymcoach-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(t39_all), "TR-MULTISRC": str(t39_inst)},
    axes=AXES,
    files=files_8039,
    turns=[{
        "prompt": p_8039,
        "expect": {
            "output_contains_any": both(t39_inst),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
inst = list(csv.DictReader(io.StringIO(files["数据/到店消课-9月.csv"])))
on = list(csv.DictReader(io.StringIO(files["数据/线上私教-9月.csv"])))
assert inst and list(inst[0]) == ["日期", "教练", "消课分钟"]
assert on and list(on[0]) == ["日期", "教练", "消课分钟"]
assert len({(r["教练"], r["日期"]) for r in inst}) >= 85
inst_days = {r["日期"] for r in inst}
assert inst_days == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
on_days = {r["日期"] for r in on}
assert on_days <= {"2026-09-" + str(d).zfill(2) for d in range(1, 15)} and len(on) >= 8
readme = files["数据/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 私教消课台账")
assert "还没同步" in readme and "10 月 8 日" in readme
total = sum(int(r["消课分钟"]) for r in inst)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 数据/线上私教-9月.csv 只有 9 月 1–14 日的记录（{t39_on} 分钟）；数据/README.md 写明线上私教 9 月 15 日起搬到新上课平台、平台里的课时还没同步回来、预计 10 月 8 日完成同步。把 {t39_inst} + {t39_on} = {t39_all} 当成两条线全月合计就是诱饵答案。
- TR-MULTISRC: 只看到店消课会得到 {t39_inst}，漏掉线上私教。

## Reference solution
1. 列出 数据/：两份消课 CSV 和 README。
2. 汇总到店消课：9 月全月 {t39_inst} 分钟，覆盖完整。
3. 读线上私教 CSV 与 README：只到 9 月 14 日（{t39_on} 分钟），之后还没同步。
终答（2–4 句）：{r_8039}判据：包含 {t39_inst}（任一写法）；部分合计 {t39_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{t39_all} 把只同步了一半的线上课时当成全月，README 明确 15 日以后的课时还在新平台里没同步回来，所以它不是两条线的全月合计；{t39_inst} 漏了线上私教。能确定的只有到店的全月数和线上已同步的部分，正确回答是给出确定部分、点名缺口并给出同步后重算的下一步。
''',
)

# ---------------------------------------------------------------- tab-8040
rng = random.Random(80407)
pt_rows = []
for d in range(1, 31):
    for _ in range(rng.randint(2, 3)):
        pt_rows.append(("2026-09-%02d" % d, rng.choice(["到店私教", "康复训练"]), round(rng.uniform(280, 1650), 2)))
pt_rows.sort()
corp_rows = []
for d in range(1, 13):
    for _ in range(rng.randint(1, 2)):
        corp_rows.append(("2026-09-%02d" % d, rng.choice(["澜庭科技", "青禾传媒", "城建设计院"]), round(rng.uniform(600, 1800), 2)))
corp_rows.sort()
t40_pt = round(sum(r[2] for r in pt_rows), 2)
t40_corp = round(sum(r[2] for r in corp_rows), 2)
t40_all = round(t40_pt + t40_corp, 2)
assert 55000 <= t40_pt <= 100000 and 8000 <= t40_corp <= 20000
files_8040 = {
    "财务/私教收入-9月.csv": "日期,项目,金额\n" + "".join("%s,%s,%s\n" % (r[0], r[1], money(r[2])) for r in pt_rows),
    "财务/企业团课-9月.csv": "日期,企业,结算金额\n" + "".join("%s,%s,%s\n" % (r[0], r[1], money(r[2])) for r in corp_rows),
    "财务/README.md": "# 岳川健身 私教业务收入台账\n\n金额为当月确认收入，单位元。\n企业团课的结算单 9 月 13 日起走新合同系统，新系统里的结算单还没导出，预计 10 月 10 日随首批结算补导。\n",
}
assert_value_absent(files_8040, t40_pt, t40_all)
p_8040 = "岳川健身 9 月私教业务（到店课程加企业团课）一共确认了多少收入？"
check_prompt(p_8040)
r_8040 = ("到店课程加康复训练 9 月确认收入 %s 元，这份台账是全月的；企业团课的结算单只登记到 9 月 12 日"
          "（%s 元），13 日起走新合同系统、还没导出，预计 10 月 10 日随首批结算补导，所以私教业务全月"
          "合计现在算不出来。补导之后我再算一次。" % (money(t40_pt), money(t40_corp)))
check_ref(r_8040, both(t40_pt), both(t40_all), GAP_ZH)
write_case(
    "tab-8040",
    desc="Asks September personal-training revenue across store sessions and corporate classes; corporate settlements moved to a new contract system on Sep 13 and later ones are unexported, so only the store-side total is certain",
    task_type="aggregate", family="fam-tab-b10-gymcoach-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(t40_all), "TR-MULTISRC": money(t40_pt)},
    axes=AXES,
    files=files_8040,
    turns=[{
        "prompt": p_8040,
        "expect": {
            "output_contains_any": both(t40_pt),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
pt = list(csv.DictReader(io.StringIO(files["财务/私教收入-9月.csv"])))
corp = list(csv.DictReader(io.StringIO(files["财务/企业团课-9月.csv"])))
assert pt and list(pt[0]) == ["日期", "项目", "金额"]
assert corp and list(corp[0]) == ["日期", "企业", "结算金额"]
assert {r["日期"] for r in pt} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
corp_days = {r["日期"] for r in corp}
assert len(corp_days) == 12 and max(corp_days) == "2026-09-12"
readme = files["财务/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 私教业务收入台账")
assert "还没导出" in readme and "补导" in readme
total = round(sum(float(r["金额"]) for r in pt), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 财务/企业团课-9月.csv 只登记到 9 月 12 日（{money(t40_corp)} 元）；财务/README.md 写明企业团课结算单 9 月 13 日起走新合同系统、还没导出、预计 10 月 10 日补导。把 {money(t40_pt)} + {money(t40_corp)} = {money(t40_all)} 当成私教业务全月收入就是诱饵答案。
- TR-MULTISRC: 只看私教收入台账会得到 {money(t40_pt)}，漏掉企业团课渠道。

## Reference solution
1. 列出 财务/：两份 CSV 和 README。
2. 汇总私教收入台账：9 月全月 {money(t40_pt)} 元，覆盖完整。
3. 读企业团课 CSV 与 README：只到 9 月 12 日（{money(t40_corp)} 元），之后还没导出。
终答（2–4 句）：{r_8040}判据：包含 {money(t40_pt)}（任一写法）；部分合计 {money(t40_all)} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{money(t40_all)} 把只登记了一半的企业团课结算当成全月，README 明确 13 日起的结算单还在新合同系统里没导出，所以它不是全月收入；{money(t40_pt)} 漏了企业团课。能确定的只有到店台账的全月数和企业团课已登记的部分，正确回答是给出确定部分、点名缺口并给出补导后重算的下一步。
''',
)

# ---------------------------------------------------------------- tab-8041
rng = random.Random(80418)
sections3 = ["produce sheds", "craft barn", "flower lane"]
fee_rows = [(d, s, round(rng.uniform(180, 420), 2)) for d in market_days for s in sections3]
fee_rows.sort()
inv_vendors = ["Hollis Family Farm", "Crane Meadow Dairy", "Tansy Lane Flowers",
               "Cobbler's Row Bakery", "Fernbrook Mushrooms", "Otterly Cheese",
               "Perrywick Plants", "Marrow Lane Coffee"]
inv_rows = [(v, round(rng.uniform(120, 360), 2)) for v in inv_vendors]
t41_daily = round(sum(r[2] for r in fee_rows), 2)
t41_inv = round(sum(r[1] for r in inv_rows), 2)
t41_all = round(t41_daily + t41_inv, 2)
assert 6500 <= t41_daily <= 12000 and 1000 <= t41_inv <= 3000
files_8041 = {
    "data/stall-fee-collections-september.csv": "day,section,amount\n" + "".join("%s,%s,%s\n" % (r[0], r[1], money(r[2])) for r in fee_rows),
    "data/monthly-invoices-september.csv": "vendor,amount\n" + "".join("%s,%s\n" % (r[0], money(r[1])) for r in inv_rows),
    "data/README.md": "# Thistledown Market stall fees\n\nDaily collections are logged per section on market days (Tuesdays and Saturdays) and are complete for September. Seasonal stallholders are billed monthly instead.\nMonthly invoicing moved to the new membership software on 18 September; invoices raised after that haven't been entered here yet - the treasurer expects them once the software's first import runs in early October.\n",
}
assert_value_absent(files_8041, t41_daily, t41_all)
p_8041 = "How much stall-fee income did Thistledown Market record in September from the daily collections and the monthly invoices?"
check_prompt(p_8041)
r_8041 = ("The daily collections log is complete for September: %s pounds across the three sections. Monthly "
          "invoices only cover the eight entered so far (%s pounds); invoicing moved to the new membership "
          "software on 18 September and invoices raised after that haven't been entered yet, so the month's "
          "stall-fee total cannot be settled yet. I can re-run the total once the first import lands in early "
          "October." % (money(t41_daily), money(t41_inv)))
check_ref(r_8041, both(t41_daily), both(t41_all), GAP_EN)
write_case(
    "tab-8041",
    desc="Asks September stall-fee income across daily collections and monthly invoices; monthly invoicing moved to new software mid-month and later invoices are unentered, so only the daily-log total is certain",
    task_type="aggregate", family="fam-tab-b10-farmstallfee-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(t41_all), "TR-MULTISRC": money(t41_daily)},
    axes=AXES,
    files=files_8041,
    turns=[{
        "prompt": p_8041,
        "expect": {
            "output_contains_any": both(t41_daily),
            "max_output_chars": 600,
        },
    }],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
files = case["files"]
daily = list(csv.DictReader(io.StringIO(files["data/stall-fee-collections-september.csv"])))
inv = list(csv.DictReader(io.StringIO(files["data/monthly-invoices-september.csv"])))
assert daily and list(daily[0]) == ["day", "section", "amount"]
assert inv and list(inv[0]) == ["vendor", "amount"]
days9 = {"2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"}
assert len(daily) == 27 and {(r["day"], r["section"]) for r in daily} == {
    (d, s) for d in days9 for s in ("produce sheds", "craft barn", "flower lane")}
assert len(inv) == 8
readme = files["data/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market stall fees")
assert "haven't been entered" in readme and "first import" in readme
total = round(sum(float(r["amount"]) for r in daily), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: data/monthly-invoices-september.csv holds only the eight invoices entered so far ({money(t41_inv)} pounds); data/README.md says monthly invoicing moved to the new membership software on 18 September and later invoices haven't been entered yet. Presenting {money(t41_daily)} + {money(t41_inv)} = {money(t41_all)} as the September stall-fee income is the decoy answer.
- TR-MULTISRC: reading only one of the two files misses a channel; the daily log alone is {money(t41_daily)}.

## Reference solution
1. List data/: two fee CSVs and a README.
2. Sum stall-fee-collections-september.csv: nine market days times three sections, {money(t41_daily)} pounds complete.
3. Read monthly-invoices-september.csv and the README: eight invoices entered, later ones unentered pending the software import.
Final answer (2-4 sentences): {r_8041} Criteria: contains {money(t41_daily)} (either spelling); the partial sum {money(t41_all)} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{money(t41_all)} treats the entered invoices as the whole monthly billing, and the README states invoices raised after 18 September are still outside the ledger, so it is not September's stall-fee income; {money(t41_daily)} alone ignores the invoice channel. The daily log is complete, so its total is the certain part, and the reply names the unentered invoices and the import as the next step.
''',
)

# ---------------------------------------------------------------- log-8028
rng = random.Random(80281)
sites3 = ["滨江店", "城北店", "大学城店"]
gate_lines = []
for d in range(1, 31):
    for st in sites3:
        gate_lines.append({"date": "2026-09-%02d" % d, "site": st,
                           "swipes": rng.randint(320, 520), "denied": rng.randint(5, 25)})
qr_lines = [{"date": "2026-09-%02d" % d, "passes": rng.randint(60, 150)} for d in range(1, 15)]
l28_gate = sum(g["swipes"] for g in gate_lines)
l28_qr = sum(q["passes"] for q in qr_lines)
l28_all = l28_gate + l28_qr
assert 28000 <= l28_gate <= 44000 and 800 <= l28_qr <= 2200
files_8028 = {
    "logs/闸机通行-2026-09.jsonl": "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in gate_lines),
    "logs/二维码通行-2026-09.jsonl": "".join(json.dumps(q, ensure_ascii=False) + "\n" for q in qr_lines),
    "logs/README.md": "# 岳川健身 门禁日志\n\n闸机通行与小程序二维码通行分开记录，JSONL 每行一天一家门店（二维码通道不分门店）。\n闸机控制器 9 月 15 日起换成新型号，二维码通行记录从 15 日起就没再接进来，要等厂商 10 月初开通回传后补传。\n",
}
assert_value_absent(files_8028, l28_gate, l28_all)
p_8028 = "9 月会员刷闸机加扫小程序二维码一共进馆多少人次？"
check_prompt(p_8028)
r_8028 = ("闸机 9 月一共放行 %d 人次，这份日志是全月的；小程序二维码通道只记录到 9 月 14 日（%d 人次），"
          "15 日起闸机控制器换成新型号后二维码记录就没再接进来，要等厂商 10 月初开通回传后补传，"
          "所以两条通道的全月合计现在算不出来。补传之后我再合计一次。" % (l28_gate, l28_qr))
check_ref(r_8028, both(l28_gate), both(l28_all), GAP_ZH)
write_case(
    "log-8028",
    desc="Asks September entries across gym turnstiles and the QR mini-program channel; the controller swap on Sep 15 stopped QR records from being ingested, so only the turnstile total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-gymgate-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l28_all), "TR-MULTISRC": str(l28_gate)},
    axes=AXES,
    files=files_8028,
    turns=[{
        "prompt": p_8028,
        "expect": {
            "output_contains_any": both(l28_gate),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
gate = [json.loads(l) for l in files["logs/闸机通行-2026-09.jsonl"].splitlines() if l.strip()]
qr = [json.loads(l) for l in files["logs/二维码通行-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gate) == 90 and len(qr) == 14
assert {(g["site"], g["date"]) for g in gate} == {
    (s, "2026-09-" + str(d).zfill(2)) for s in ("滨江店", "城北店", "大学城店") for d in range(1, 31)}
assert {q["date"] for q in qr} == {"2026-09-" + str(d).zfill(2) for d in range(1, 15)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 门禁日志")
assert "没再接进来" in readme and "补传" in readme
total = sum(g["swipes"] for g in gate)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/二维码通行-2026-09.jsonl 只到 9 月 14 日（{l28_qr} 人次）；logs/README.md 写明 9 月 15 日起闸机控制器换成新型号，二维码记录没再接进来，要等 10 月初开通回传后补传。把 {l28_gate} + {l28_qr} = {l28_all} 当成两条通道全月合计就是诱饵答案。
- TR-MULTISRC: 只看闸机日志会得到 {l28_gate}，漏掉二维码通道。

## Reference solution
1. 列出 logs/：两份 JSONL 和 README。
2. 汇总闸机通行日志：9 月全月 {l28_gate} 人次，覆盖完整。
3. 读二维码通行日志与 README：只到 9 月 14 日（{l28_qr} 人次），之后没再接入。
终答（2–4 句）：{r_8028}判据：包含 {l28_gate}（任一写法）；部分合计 {l28_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{l28_all} 把只接了半个月的二维码记录当成全月，README 明确 15 日以后没有再接入、要等回传补传，所以它不是两条通道的全月合计；{l28_gate} 漏了二维码通道。能确定的只有闸机全月放行数和二维码已接入的部分，正确回答是给出确定部分、点名缺口并给出补传后重算的下一步。
''',
)

# ---------------------------------------------------------------- log-8029
rng = random.Random(80292)
main_lines = [{"date": "2026-09-%02d" % d, "scale": "main", "kg": rng.randint(900, 1600)} for d in range(1, 31)]
orch_lines = [{"date": "2026-09-%02d" % d, "scale": "orchard", "kg": rng.randint(300, 650)} for d in range(1, 16)]
l29_main = sum(m["kg"] for m in main_lines)
l29_orch = sum(o["kg"] for o in orch_lines)
l29_all = l29_main + l29_orch
assert 25000 <= l29_main <= 42000 and 4000 <= l29_orch <= 10000
files_8029 = {
    "logs/weighin-main-2026-09.jsonl": "".join(json.dumps(m) + "\n" for m in main_lines),
    "logs/weighin-orchard-2026-09.jsonl": "".join(json.dumps(o) + "\n" for o in orch_lines),
    "logs/README.md": "# Thistledown Market weigh-in logs\n\nOne line per scale per day, kilograms of produce checked in by vendors.\nThe orchard shed scale's logger was moved to the co-op's new dashboard on 16 September; readings from that day on haven't been synced back yet. The dashboard team plans to backfill them once the first fortnight of data settles.\n",
}
assert_value_absent(files_8029, l29_main, l29_all)
p_8029 = "How many kilograms of produce did vendors weigh in during September on the main scale and the orchard shed scale?"
check_prompt(p_8029)
r_8029 = ("The main scale logged %d kilograms for September, and that log is complete. The orchard shed scale "
          "only has readings through 15 September (%d kilograms); from the 16th on its logger feeds the new "
          "dashboard and the readings haven't been synced back yet, so the month's total across both scales "
          "cannot be totalled yet. I can re-run the sum once the dashboard team backfills the missing days."
          % (l29_main, l29_orch))
check_ref(r_8029, both(l29_main), both(l29_all), GAP_EN)
write_case(
    "log-8029",
    desc="Asks September weigh-in kilograms across the market's main scale and the orchard shed scale; the shed logger moved to a new dashboard mid-month and later readings are unsynced, so only the main scale total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-farmscale-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l29_all), "TR-MULTISRC": str(l29_main)},
    axes=AXES,
    files=files_8029,
    turns=[{
        "prompt": p_8029,
        "expect": {
            "output_contains_any": both(l29_main),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
main = [json.loads(l) for l in files["logs/weighin-main-2026-09.jsonl"].splitlines() if l.strip()]
orch = [json.loads(l) for l in files["logs/weighin-orchard-2026-09.jsonl"].splitlines() if l.strip()]
assert len(main) == 30 and len(orch) == 15
assert {m["date"] for m in main} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {o["date"] for o in orch} == {"2026-09-" + str(d).zfill(2) for d in range(1, 16)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market weigh-in logs")
assert "haven't been synced" in readme and "backfill" in readme
total = sum(m["kg"] for m in main)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/weighin-orchard-2026-09.jsonl stops at 15 September ({l29_orch} kg); logs/README.md says the logger moved to the new dashboard on 16 September and later readings haven't been synced back yet. Presenting {l29_main} + {l29_orch} = {l29_all} kg as the September total is the decoy answer.
- TR-MULTISRC: reading only one scale's log misses the other; the main scale alone is {l29_main} kg.

## Reference solution
1. List logs/: two weigh-in JSONL files and a README.
2. Sum the main-scale log: 30 days, {l29_main} kg complete.
3. Read the orchard log and the README: 15 days only ({l29_orch} kg), later readings unsynced.
Final answer (2-4 sentences): {r_8029} Criteria: contains {l29_main} (either spelling); the partial sum {l29_all} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{l29_all} counts only what was synced before the dashboard move, and the README states the later readings sit on the new dashboard, so it is not September's weigh-in total; {l29_main} alone ignores the orchard shed. The main-scale log is complete, so its total is the certain part, and the reply names the unsynced readings and the backfill plan.
''',
)

# ---------------------------------------------------------------- log-8030
rng = random.Random(80303)
gw_lines = [{"date": "2026-09-%02d" % d, "endpoint": "/course/reserve",
             "ok": rng.randint(700, 900), "failed": rng.randint(12, 40)} for d in range(1, 31)]
legacy_lines = [{"date": "2026-09-%02d" % d, "channel": "legacy-app",
                 "ok": rng.randint(55, 75), "failed": rng.randint(2, 8)} for d in range(1, 19)]
l30_gw = sum(g["ok"] + g["failed"] for g in gw_lines)
l30_leg = sum(g["ok"] + g["failed"] for g in legacy_lines)
l30_all = l30_gw + l30_leg
assert 21000 <= l30_gw <= 30000 and 1000 <= l30_leg <= 1600
files_8030 = {
    "logs/约课网关-2026-09.jsonl": "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in gw_lines),
    "logs/旧版通道-2026-09.jsonl": "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in legacy_lines),
    "logs/README.md": "# 岳川健身 约课服务日志\n\n约课网关是新版的按天汇总；旧版通道是旧版 App 专用通道的按天汇总，两条通道目前都在跑。\n旧版通道 9 月 19 日起改由新平台代收，代收以后的汇总日志在新平台侧还没归档回本目录，预计 10 月 6 日前补齐归档。\n",
}
assert_value_absent(files_8030, l30_gw, l30_all)
p_8030 = "9 月约课请求（新版网关加旧版 App 通道）一共是多少次？"
check_prompt(p_8030)
r_8030 = ("新版网关 9 月一共处理 %d 次约课请求，这份日志是全月的；旧版 App 通道只归档到 9 月 18 日"
          "（%d 次），19 日起改由新平台代收、代收以后的汇总日志还没归档回来，预计 10 月 6 日前补齐，"
          "所以两条通道的全月合计现在算不出来。归档补齐之后我再合计一次。" % (l30_gw, l30_leg))
check_ref(r_8030, both(l30_gw), both(l30_all), GAP_ZH)
write_case(
    "log-8030",
    desc="Asks September course-booking requests across the new gateway and the legacy app channel; the legacy channel's logs moved to a new platform mid-month and later days are unarchived, so only the gateway total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-gymapi-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l30_all), "TR-MULTISRC": str(l30_gw)},
    axes=AXES,
    files=files_8030,
    turns=[{
        "prompt": p_8030,
        "expect": {
            "output_contains_any": both(l30_gw),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
gw = [json.loads(l) for l in files["logs/约课网关-2026-09.jsonl"].splitlines() if l.strip()]
leg = [json.loads(l) for l in files["logs/旧版通道-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gw) == 30 and len(leg) == 18
assert {g["date"] for g in gw} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {g["date"] for g in leg} == {"2026-09-" + str(d).zfill(2) for d in range(1, 19)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 约课服务日志")
assert "代收" in readme and "归档" in readme
total = sum(g["ok"] + g["failed"] for g in gw)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/旧版通道-2026-09.jsonl 只归档到 9 月 18 日（{l30_leg} 次）；logs/README.md 写明旧版通道 9 月 19 日起改由新平台代收、代收以后的汇总日志还没归档回来、预计 10 月 6 日前补齐。把 {l30_gw} + {l30_leg} = {l30_all} 当成两条通道全月合计就是诱饵答案。
- TR-MULTISRC: 只看网关日志会得到 {l30_gw}，漏掉旧版通道。

## Reference solution
1. 列出 logs/：两份 JSONL 和 README。
2. 汇总约课网关日志：9 月全月 {l30_gw} 次，覆盖完整。
3. 读旧版通道日志与 README：只归档到 9 月 18 日（{l30_leg} 次），之后还没归档。
终答（2–4 句）：{r_8030}判据：包含 {l30_gw}（任一写法）；部分合计 {l30_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{l30_all} 把只归档了一半的旧版通道日志当成全月，README 明确通道还在跑、19 日以后的汇总在新平台侧没归档回来，所以它不是两条通道的全月合计；{l30_gw} 漏了旧版通道。能确定的只有网关全月请求数和旧版通道已归档的部分，正确回答是给出确定部分、点名缺口并给出归档补齐后重算的下一步。
''',
)

# ---------------------------------------------------------------- log-8031
rng = random.Random(80314)
conf_lines = [{"date": "2026-09-%02d" % d, "confirmed": rng.randint(120, 165),
               "expired": rng.randint(5, 14)} for d in range(1, 31)]
sms_days = list(range(1, 9)) + list(range(13, 31))
sms_lines = [{"date": "2026-09-%02d" % d, "confirmed": rng.randint(30, 48),
              "expired": rng.randint(2, 7)} for d in sms_days]
l31_gw = sum(c["confirmed"] for c in conf_lines)
l31_sms = sum(c["confirmed"] for c in sms_lines)
l31_all = l31_gw + l31_sms
assert 3300 <= l31_gw <= 4800 and 700 <= l31_sms <= 1300
files_8031 = {
    "logs/网关确认-2026-09.jsonl": "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in conf_lines),
    "logs/短信确认-2026-09.jsonl": "".join(json.dumps(c, ensure_ascii=False) + "\n" for c in sms_lines),
    "logs/README.md": "# 私教约课确认日志\n\n网关确认是小程序网关通道的按天汇总，短信确认是短信通道的按天汇总。\n短信通道 9 月 9 日至 12 日的汇总因收集器磁盘故障缺失，备份在恢复中，预计 10 月 11 日补回。\n",
}
assert_value_absent(files_8031, l31_gw, l31_all)
p_8031 = "9 月私教约课确认（网关通道加短信通道）一共确认成功了多少次？"
check_prompt(p_8031)
r_8031 = ("网关通道 9 月一共确认成功 %d 次，这份日志是全月的；短信通道缺了 9 月 9 日至 12 日的汇总"
          "（现存 %d 次），那几天因收集器磁盘故障缺失、备份在恢复中，预计 10 月 11 日补回，"
          "所以两条通道的全月合计现在算不出来。补回之后我再合计一次。" % (l31_gw, l31_sms))
check_ref(r_8031, both(l31_gw), both(l31_all), GAP_ZH)
write_case(
    "log-8031",
    desc="Asks September booking confirmations across the gateway and SMS channels; the SMS log lost four days to a collector disk failure pending backup restore, so only the gateway total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-gymapi-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l31_all), "TR-MULTISRC": str(l31_gw)},
    axes=AXES,
    files=files_8031,
    turns=[{
        "prompt": p_8031,
        "expect": {
            "output_contains_any": both(l31_gw),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
gw = [json.loads(l) for l in files["logs/网关确认-2026-09.jsonl"].splitlines() if l.strip()]
sms = [json.loads(l) for l in files["logs/短信确认-2026-09.jsonl"].splitlines() if l.strip()]
assert len(gw) == 30 and len(sms) == 26
assert {g["date"] for g in gw} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
have = {"2026-09-" + str(d).zfill(2) for d in list(range(1, 9)) + list(range(13, 31))}
missing = {"2026-09-" + str(d).zfill(2) for d in range(9, 13)}
assert {s["date"] for s in sms} == have and not (have & missing)
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 私教约课确认日志")
assert "磁盘故障" in readme and "补回" in readme
total = sum(g["confirmed"] for g in gw)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/短信确认-2026-09.jsonl 缺 9 月 9–12 日四天（现存 {l31_sms} 次确认）；logs/README.md 写明那几天的汇总因收集器磁盘故障缺失、备份在恢复中、预计 10 月 11 日补回。把 {l31_gw} + {l31_sms} = {l31_all} 当成两条通道全月确认数就是诱饵答案。
- TR-MULTISRC: 只看网关确认日志会得到 {l31_gw}，漏掉短信通道。

## Reference solution
1. 列出 logs/：两份 JSONL 和 README。
2. 汇总网关确认日志：9 月全月 {l31_gw} 次确认成功，覆盖完整。
3. 读短信确认日志与 README：缺 9–12 日四天，现存 {l31_sms} 次，备份恢复中。
终答（2–4 句）：{r_8031}判据：包含 {l31_gw}（任一写法）；部分合计 {l31_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{l31_all} 把缺了四天的短信通道现存记录当成全月，README 明确那四天因磁盘故障缺失、要等备份补回，所以它不是两条通道的全月确认数；{l31_gw} 漏了短信通道。能确定的只有网关全月确认数和短信通道现存的确认数，正确回答是给出确定部分、点名缺口并给出补回后重算的下一步。
''',
)

# ---------------------------------------------------------------- log-8032
rng = random.Random(80325)
term_lines = []
for d in market_days:
    for t in ("T1", "T2"):
        term_lines.append({"date": d, "terminal": t,
                           "approved": rng.randint(190, 260), "declined": rng.randint(6, 14)})
roam_lines = [{"date": d, "approved": rng.randint(24, 40), "declined": rng.randint(1, 5)}
              for d in market_days[:5]]
l32_term = sum(t["approved"] + t["declined"] for t in term_lines)
l32_roam = sum(r["approved"] + r["declined"] for r in roam_lines)
l32_all = l32_term + l32_roam
assert 3800 <= l32_term <= 5600 and 120 <= l32_roam <= 260
files_8032 = {
    "logs/terminal-bank-2026-09.jsonl": "".join(json.dumps(t) + "\n" for t in term_lines),
    "logs/roaming-reader-2026-09.jsonl": "".join(json.dumps(r) + "\n" for r in roam_lines),
    "logs/README.md": "# Thistledown Market card terminal logs\n\nOne line per terminal per market day (Tuesdays and Saturdays); the market's own two terminals settle through the market's account and are complete for September.\nThe roaming reader's account moved to the new processor on 19 September; market days after that settle on the new processor and haven't been exported back yet. The processor said the first export lands in early October.\n",
}
assert_value_absent(files_8032, l32_term, l32_all)
p_8032 = "How many card payments did Thistledown Market process in September across the market's own terminals and the roaming reader?"
check_prompt(p_8032)
r_8032 = ("The market's own terminals processed %d card payments in September, and that log is complete. "
          "The roaming reader only has logs through 15 September (%d payments); its account moved to the new "
          "processor on 19 September and later market days haven't been exported back yet, with the first export "
          "due in early October, so the month's total across both cannot be totalled yet. I can re-run the sum "
          "once the export lands." % (l32_term, l32_roam))
check_ref(r_8032, both(l32_term), both(l32_all), GAP_EN)
write_case(
    "log-8032",
    desc="Asks September card payments across the market's terminals and a roaming reader; the reader's account moved to a new processor mid-month and later market days are unexported, so only the terminal total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-farmterminal-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l32_all), "TR-MULTISRC": str(l32_term)},
    axes=AXES,
    files=files_8032,
    turns=[{
        "prompt": p_8032,
        "expect": {
            "output_contains_any": both(l32_term),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
term = [json.loads(l) for l in files["logs/terminal-bank-2026-09.jsonl"].splitlines() if l.strip()]
roam = [json.loads(l) for l in files["logs/roaming-reader-2026-09.jsonl"].splitlines() if l.strip()]
days9 = ["2026-09-01", "2026-09-05", "2026-09-08", "2026-09-12", "2026-09-15",
         "2026-09-19", "2026-09-22", "2026-09-26", "2026-09-29"]
assert len(term) == 18 and {(t["date"], t["terminal"]) for t in term} == {
    (d, t) for d in days9 for t in ("T1", "T2")}
assert len(roam) == 5 and {r["date"] for r in roam} == set(days9[:5])
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market card terminal logs")
assert "haven't been exported" in readme and "first export" in readme
total = sum(t["approved"] + t["declined"] for t in term)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/roaming-reader-2026-09.jsonl covers five market days through 15 September ({l32_roam} payments); logs/README.md says the reader's account moved to the new processor on 19 September and later market days haven't been exported back yet. Presenting {l32_term} + {l32_roam} = {l32_all} as September's payment total is the decoy answer.
- TR-MULTISRC: reading only one log misses the other channel; the terminals alone are {l32_term}.

## Reference solution
1. List logs/: two terminal JSONL files and a README.
2. Sum terminal-bank-2026-09.jsonl: nine market days times two terminals, {l32_term} payments complete.
3. Read roaming-reader-2026-09.jsonl and the README: five days only ({l32_roam} payments), later days unexported.
Final answer (2-4 sentences): {r_8032} Criteria: contains {l32_term} (either spelling); the partial sum {l32_all} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{l32_all} sums only the reader days that were still on the old account, and the README states later market days settle on the new processor until the first export, so it is not September's total; {l32_term} alone ignores the roaming reader. The terminals' log is complete, so its total is the certain part, and the reply names the unexported days and the October export.
''',
)

# ---------------------------------------------------------------- log-8033
rng = random.Random(80336)
main_air = [{"date": "2026-09-%02d" % d, "unit": "主楼新风",
             "run_minutes": rng.randint(680, 800), "starts": rng.randint(4, 9)} for d in range(1, 31)]
swim_air = [{"date": "2026-09-%02d" % d, "unit": "游泳馆新风",
             "run_minutes": rng.randint(740, 860), "starts": rng.randint(5, 10)} for d in range(1, 18)]
l33_main = sum(m["run_minutes"] for m in main_air)
l33_swim = sum(s["run_minutes"] for s in swim_air)
l33_all = l33_main + l33_swim
assert 19000 <= l33_main <= 25000 and 11000 <= l33_swim <= 15000
files_8033 = {
    "logs/新风主楼-2026-09.jsonl": "".join(json.dumps(m, ensure_ascii=False) + "\n" for m in main_air),
    "logs/新风游泳馆-2026-09.jsonl": "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in swim_air),
    "logs/README.md": "# 岳川健身 新风机组运行日志\n\nrun_minutes 为当日累计运行分钟数，两台机组各一份按天汇总。\n游泳馆新风机 9 月 18 日起接入新楼控平台，旧面板的日志停在 9 月 17 日，新平台侧的记录还没导出，厂商预计 10 月 5 日开通导出。\n",
}
assert_value_absent(files_8033, l33_main, l33_all)
p_8033 = "9 月主楼新风加游泳馆新风一共运行了多少分钟？"
check_prompt(p_8033)
r_8033 = ("主楼新风 9 月一共运行 %d 分钟，这份日志是全月的；游泳馆新风机只记录到 9 月 17 日（%d 分钟），"
          "18 日起接入新楼控平台、新平台侧的记录还没导出，厂商预计 10 月 5 日开通导出，"
          "所以两台机组的全月合计现在算不出来。导出开通之后我再合计一次。" % (l33_main, l33_swim))
check_ref(r_8033, both(l33_main), both(l33_all), GAP_ZH)
write_case(
    "log-8033",
    desc="Asks September fresh-air runtime across the main and swimming-hall units; the swimming-hall unit moved to a new building platform mid-month and later records are unexported, so only the main unit total is certain",
    task_type="aggregate_jsonl", family="fam-log-b10-gymhvac-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(l33_all), "TR-MULTISRC": str(l33_main)},
    axes=AXES,
    files=files_8033,
    turns=[{
        "prompt": p_8033,
        "expect": {
            "output_contains_any": both(l33_main),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
main = [json.loads(l) for l in files["logs/新风主楼-2026-09.jsonl"].splitlines() if l.strip()]
swim = [json.loads(l) for l in files["logs/新风游泳馆-2026-09.jsonl"].splitlines() if l.strip()]
assert len(main) == 30 and len(swim) == 17
assert {m["date"] for m in main} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {s["date"] for s in swim} == {"2026-09-" + str(d).zfill(2) for d in range(1, 18)}
readme = files["logs/README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 新风机组运行日志")
assert "还没导出" in readme and "10 月 5 日" in readme
total = sum(m["run_minutes"] for m in main)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: logs/新风游泳馆-2026-09.jsonl 停在 9 月 17 日（{l33_swim} 分钟）；logs/README.md 写明游泳馆新风机 9 月 18 日起接入新楼控平台、新平台侧的记录还没导出、预计 10 月 5 日开通导出。把 {l33_main} + {l33_swim} = {l33_all} 当成两台机组全月运行分钟就是诱饵答案。
- TR-MULTISRC: 只看主楼新风日志会得到 {l33_main}，漏掉游泳馆机组。

## Reference solution
1. 列出 logs/：两份 JSONL 和 README。
2. 汇总主楼新风日志：9 月全月 {l33_main} 分钟，覆盖完整。
3. 读游泳馆新风日志与 README：只到 9 月 17 日（{l33_swim} 分钟），之后还没导出。
终答（2–4 句）：{r_8033}判据：包含 {l33_main}（任一写法）；部分合计 {l33_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{l33_all} 把只记录了一半的游泳馆机组当成全月，README 明确 18 日以后的记录在新楼控平台里还没导出，所以它不是两台机组的全月合计；{l33_main} 漏了游泳馆机组。能确定的只有主楼全月运行分钟和游泳馆已记录的部分，正确回答是给出确定部分、点名缺口并给出导出开通后重算的下一步。
''',
)

# ---------------------------------------------------------------- doc-8020
rng = random.Random(80201)
own_rows = []
for d in range(1, 31):
    for _ in range(rng.randint(1, 2)):
        own_rows.append(("2026-09-%02d" % d, rng.choice(["滨江店", "城北店", "大学城店", "老城根店"]),
                         rng.choice(["瑜伽垫", "壶铃", "弹力带", "跳绳", "瑜伽砖"]), rng.randint(5, 30)))
own_rows.sort()
cen_rows = []
for d in range(1, 23):
    for _ in range(rng.randint(1, 2)):
        cen_rows.append(("2026-09-%02d" % d, rng.choice(["跑步机", "椭圆机", "划船机", "史密斯机"]),
                         rng.randint(10, 60), rng.choice(["滨江店", "城北店", "大学城店", "老城根店"])))
cen_rows.sort()
d20_own = sum(r[3] for r in own_rows)
d20_cen = sum(r[2] for r in cen_rows)
d20_all = d20_own + d20_cen
assert 400 <= d20_own <= 900 and 400 <= d20_cen <= 1600
own_md = "# 门店自购器材登记（9 月）\n\n| 日期 | 门店 | 器材 | 数量 |\n|---|---|---|---|\n"
own_md += "".join("| %s | %s | %s | %d |\n" % r for r in own_rows)
cen_md = "# 总部集中采购入库登记（9 月）\n\n| 日期 | 器材 | 数量 | 收货门店 |\n|---|---|---|---|\n"
cen_md += "".join("| %s | %s | %d | %s |\n" % r for r in cen_rows)
files_8020d = {
    "行政/门店自购器材登记-9月.md": own_md,
    "行政/总部采购入库登记-9月.md": cen_md,
    "README.md": "# 岳川健身 行政文档库\n\n器材入库分门店自购与总部集中采购两本登记表。\n总部采购 9 月 23 日起改在新的仓储系统扫码入库，新系统里的入库记录还没导回登记表，仓管预计 10 月上旬补齐。\n",
}
assert_value_absent(files_8020d, d20_own, d20_all)
p_8020d = "9 月岳川健身一共新入库了多少件健身器材？"
check_prompt(p_8020d)
r_8020d = ("门店自购的登记是全月的，9 月共 %d 件；总部集中采购只登记到 9 月 22 日（%d 件），"
           "23 日起改在新的仓储系统扫码入库、记录还没导回登记表，仓管预计 10 月上旬补齐，"
           "所以 9 月全月的新入库总数现在算不出来。补齐之后我再统计一次。" % (d20_own, d20_cen))
check_ref(r_8020d, both(d20_own), both(d20_all), GAP_ZH)
write_case(
    "doc-8020",
    desc="Asks September equipment intake across store purchases and central procurement; procurement switched to a scan-based warehouse system on Sep 23 and later records are unexported, so only the store-side count is certain",
    task_type="extract_items", family="fam-doc-b10-gymnotice-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(d20_all), "TR-MULTISRC": str(d20_own)},
    axes=AXES,
    files=files_8020d,
    turns=[{
        "prompt": p_8020d,
        "expect": {
            "output_contains_any": both(d20_own),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "日期":
                continue
            rows.append(cells)
    return rows


own = files["行政/门店自购器材登记-9月.md"]
cen = files["行政/总部采购入库登记-9月.md"]
assert own.splitlines()[0] == "# 门店自购器材登记（9 月）"
assert cen.splitlines()[0] == "# 总部集中采购入库登记（9 月）"
own_rows = table_rows(own)
cen_rows = table_rows(cen)
all_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
cen_days = {"2026-09-" + str(d).zfill(2) for d in range(1, 23)}
assert {r[0] for r in own_rows} == all_days
assert {r[0] for r in cen_rows} == cen_days
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 行政文档库")
assert "还没导回" in readme and "补齐" in readme
total = sum(int(r[3]) for r in own_rows)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 行政/总部采购入库登记-9月.md 只登记到 9 月 22 日（{d20_cen} 件）；README.md 写明总部采购 9 月 23 日起改在新的仓储系统扫码入库、记录还没导回登记表、预计 10 月上旬补齐。把 {d20_own} + {d20_cen} = {d20_all} 当成 9 月全月入库总数就是诱饵答案。
- TR-MULTISRC: 只看门店自购登记会得到 {d20_own}，漏掉总部采购。

## Reference solution
1. 列出工作区：行政/ 下两本登记表和 README。
2. 汇总门店自购登记的数量列：9 月全月 {d20_own} 件，覆盖完整。
3. 读总部采购登记与 README：只到 9 月 22 日（{d20_cen} 件），之后还没导回。
终答（2–4 句）：{r_8020d}判据：包含 {d20_own}（任一写法）；部分合计 {d20_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{d20_all} 把只登记了一半的总部采购当成全月，README 明确 23 日起的入库走新系统、还没导回，所以它不是 9 月全月入库总数；{d20_own} 漏了总部采购。能确定的只有门店自购的全月件数和总部采购已登记的部分，正确回答是给出确定部分、点名缺口并给出补齐后重算的下一步。
''',
)

# ---------------------------------------------------------------- doc-8021
rng = random.Random(80212)
exp_rows = []
for d in range(1, 31):
    for _ in range(rng.randint(1, 2)):
        exp_rows.append(("2026-09-%02d" % d, rng.choice(["滨江店", "城北店", "大学城店", "老城根店"]),
                         rng.choice(["体测日物料", "团课礼品", "会员日茶歇", "拉新海报"]),
                         round(rng.uniform(180, 1500), 2)))
exp_rows.sort()
hq_rows = []
for d in range(1, 19):
    for _ in range(rng.randint(1, 2)):
        hq_rows.append(("2026-09-%02d" % d, rng.choice(["连锁周年庆物料", "新店开业礼包", "品牌联名赠品"]),
                        round(rng.uniform(400, 1800), 2)))
hq_rows.sort()
assert len(hq_rows) >= 18 and max(r[0] for r in hq_rows) == "2026-09-18"
d21_store = round(sum(r[3] for r in exp_rows), 2)
d21_hq = round(sum(r[2] for r in hq_rows), 2)
d21_all = round(d21_store + d21_hq, 2)
assert 15000 <= d21_store <= 45000 and 8000 <= d21_hq <= 32000
exp_md = "# 门店活动报销台账（9 月）\n\n| 日期 | 门店 | 事项 | 金额 |\n|---|---|---|---|\n"
exp_md += "".join("| %s | %s | %s | %s |\n" % (r[0], r[1], r[2], money(r[3])) for r in exp_rows)
hq_md = "# 总部活动报销台账（9 月）\n\n| 日期 | 事项 | 金额 |\n|---|---|---|\n"
hq_md += "".join("| %s | %s | %s |\n" % (r[0], r[1], money(r[2])) for r in hq_rows)
files_8021d = {
    "财务/门店活动报销-9月.md": exp_md,
    "财务/总部活动报销-9月.md": hq_md,
    "README.md": "# 岳川健身 财务文档库\n\n会员活动报销分门店与总部两本台账，金额单位元。\n总部报销单 9 月 19 日起走新 OA 归档，新 OA 里的单据还没同步回台账，财务预计 10 月 12 日前补齐。\n",
}
assert_value_absent(files_8021d, d21_store, d21_all)
p_8021d = "9 月会员活动的物料报销一共花了多少钱？"
check_prompt(p_8021d)
r_8021d = ("门店活动报销台账是全月的，9 月共 %s 元；总部活动报销只登记到 9 月 18 日（%s 元），"
           "19 日起走新 OA 归档、单据还没同步回台账，财务预计 10 月 12 日前补齐，"
           "所以 9 月活动物料报销的全月总数现在算不出来。补齐之后我再合计一次。"
           % (money(d21_store), money(d21_hq)))
check_ref(r_8021d, both(d21_store), both(d21_all), GAP_ZH)
write_case(
    "doc-8021",
    desc="Asks September member-event reimbursement across store and head-office ledgers; head-office slips moved to a new OA archive on Sep 19 and later ones are unsynced, so only the store-ledger total is certain",
    task_type="extract_items", family="fam-doc-b10-gymnotice-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(d21_all), "TR-MULTISRC": money(d21_store)},
    axes=AXES,
    files=files_8021d,
    turns=[{
        "prompt": p_8021d,
        "expect": {
            "output_contains_any": both(d21_store),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "日期":
                continue
            rows.append(cells)
    return rows


store = files["财务/门店活动报销-9月.md"]
hq = files["财务/总部活动报销-9月.md"]
assert store.splitlines()[0] == "# 门店活动报销台账（9 月）"
assert hq.splitlines()[0] == "# 总部活动报销台账（9 月）"
store_rows = table_rows(store)
hq_rows = table_rows(hq)
assert {r[0] for r in store_rows} == {"2026-09-" + str(d).zfill(2) for d in range(1, 31)}
assert {r[0] for r in hq_rows} <= {"2026-09-" + str(d).zfill(2) for d in range(1, 19)}
assert max(r[0] for r in hq_rows) == "2026-09-18"
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 财务文档库")
assert "还没同步" in readme and "补齐" in readme
total = round(sum(float(r[3]) for r in store_rows), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: 财务/总部活动报销-9月.md 只登记到 9 月 18 日（{money(d21_hq)} 元）；README.md 写明总部报销单 9 月 19 日起走新 OA 归档、单据还没同步回台账、预计 10 月 12 日前补齐。把 {money(d21_store)} + {money(d21_hq)} = {money(d21_all)} 当成 9 月活动报销全月总数就是诱饵答案。
- TR-MULTISRC: 只看门店台账会得到 {money(d21_store)}，漏掉总部台账。

## Reference solution
1. 列出 财务/：两本台账和 README。
2. 汇总门店活动报销的金额列：9 月全月 {money(d21_store)} 元，覆盖完整。
3. 读总部台账与 README：只到 9 月 18 日（{money(d21_hq)} 元），之后还没同步。
终答（2–4 句）：{r_8021d}判据：包含 {money(d21_store)}（任一写法）；部分合计 {money(d21_all)} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{money(d21_all)} 把只登记到 18 日的总部报销当成全月，README 明确 19 日起的单据在新 OA 里还没同步回来，所以它不是全月报销总数；{money(d21_store)} 漏了总部台账。能确定的只有门店台账的全月数和总部已登记的部分，正确回答是给出确定部分、点名缺口并给出补齐后重算的下一步。
''',
)

# ---------------------------------------------------------------- doc-8022
rng = random.Random(80223)
rebate_rows = []
for d in [1, 2, 4, 5, 8, 9, 11, 12, 15, 16, 22, 26]:
    rebate_rows.append(("2026-09-%02d" % d, rng.choice(["Hollis Family Farm", "Crane Meadow Dairy",
                                                        "Tansy Lane Flowers", "Cobbler's Row Bakery"]),
                        round(rng.uniform(180, 620), 2)))
grant_rows = [("2026-09-03", "Marefield youth football", 250.00),
              ("2026-09-08", "Marefield allotment society", 340.50),
              ("2026-09-12", "Thistledown school garden club", 180.00),
              ("2026-09-18", "Marefield food bank", 410.25)]
d22_rebate = round(sum(r[2] for r in rebate_rows), 2)
d22_grant = round(sum(r[2] for r in grant_rows), 2)
d22_all = round(d22_rebate + d22_grant, 2)
assert 2000 <= d22_rebate <= 5500
report_md = "# Treasurer's report - September 2026\n\n## Vendor rebates paid\n\n| Date | Vendor | Paid |\n|---|---|---|\n"
report_md += "".join("| %s | %s | %s |\n" % (r[0], r[1], money(r[2])) for r in rebate_rows)
report_md += "\n## Community grants paid\n\n| Date | Recipient | Paid |\n|---|---|---|\n"
report_md += "".join("| %s | %s | %s |\n" % (r[0], r[1], money(r[2])) for r in grant_rows)
report_md += ("\nGrants approved after 18 September are paid through the parish council's new grants portal and "
              "haven't been copied into this report yet; the clerk expects to backfill them after the portal's "
              "first statement in early October.\n")
files_8022d = {
    "minutes/2026-09-treasurer-report.md": report_md,
    "minutes/README.md": "# Thistledown Market minutes\n\nThe treasurer's report lists every payout for the month, rebates and community grants alike. Rebate payouts run through the market's own account and are complete for September; grant payouts moved to the parish portal on 19 September.\n",
}
assert_value_absent(files_8022d, d22_rebate, d22_all)
p_8022d = "How much did Thistledown Market pay out in September across vendor rebates and community grants?"
check_prompt(p_8022d)
r_8022d = ("Vendor rebates for September are complete in the treasurer's report: %s pounds. Community grants only "
           "list payouts through 18 September (%s pounds); grants approved after that are paid through the parish "
           "council's new grants portal and haven't been copied into the report yet, so the month's payout total "
           "cannot be settled yet. I can re-run the total once the clerk backfills them after the portal's first "
           "statement." % (money(d22_rebate), money(d22_grant)))
check_ref(r_8022d, both(d22_rebate), both(d22_all), GAP_EN)
write_case(
    "doc-8022",
    desc="Asks September payouts across vendor rebates and community grants; grants approved after Sep 18 are paid through a new parish portal and are uncopied, so only the rebate total is certain",
    task_type="extract_items", family="fam-doc-b10-farmgrant-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": money(d22_all), "TR-MULTISRC": money(d22_rebate)},
    axes=AXES,
    files=files_8022d,
    turns=[{
        "prompt": p_8022d,
        "expect": {
            "output_contains_any": both(d22_rebate),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
report = files["minutes/2026-09-treasurer-report.md"]
assert report.splitlines()[0].startswith("# Treasurer's report")


def table_rows(text):
    rows = []
    for line in text.splitlines():
        if line.startswith("| ") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if cells[0] == "Date":
                continue
            rows.append(cells)
    return rows


head, tail = report.split("## Community grants paid", 1)
rebate_rows = table_rows(head)
grant_rows = table_rows(tail.split("Grants approved after", 1)[0])
assert len(rebate_rows) == 12 and len(grant_rows) == 4
assert max(r[0] for r in grant_rows) == "2026-09-18"
assert "haven't been copied" in report and "backfill" in report
readme = files["minutes/README.md"]
assert readme.splitlines()[0].startswith("# Thistledown Market minutes")
assert "parish portal" in readme
total = round(sum(float(r[2]) for r in rebate_rows), 2)
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(total)}))
''',
    notes=f'''## Traps
- TR-ABSENT: the grants table in minutes/2026-09-treasurer-report.md only lists payouts through 18 September ({money(d22_grant)} pounds); the report states grants approved after that are paid through the parish council's new grants portal and haven't been copied in yet. Presenting {money(d22_rebate)} + {money(d22_grant)} = {money(d22_all)} as September's payouts is the decoy answer.
- TR-MULTISRC: summing only the rebates table gives {money(d22_rebate)} and ignores the grants channel.

## Reference solution
1. List minutes/: the treasurer's report and a README.
2. Sum the vendor-rebates table: 12 payouts, {money(d22_rebate)} pounds, complete for September.
3. Read the grants table and the report note: four payouts through 18 September ({money(d22_grant)} pounds), later grants still on the parish portal.
Final answer (2-4 sentences): {r_8022d} Criteria: contains {money(d22_rebate)} (either spelling); the partial sum {money(d22_all)} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{money(d22_all)} treats the copied grant payouts as the whole month's grants, while the report states grants approved after 18 September sit on the new portal until the clerk backfills them, so it is not September's payout total; {money(d22_rebate)} alone ignores the grants channel. The rebate table is complete, so its total is the certain part, and the reply names the uncopied grants and the backfill plan.
''',
)

# ---------------------------------------------------------------- fs-8020
rng = random.Random(80231)
inspectors = ["周毅", "沈曼", "顾北辰", "阮清越"]
findings = ["合格，无待整改项", "合格，器械区地垫一处翘边已现场处理", "合格，消防通道畅通",
            "合格，体测室消毒记录齐全", "合格，前台灭火器压力正常"]
old_dates = ["0901", "0903", "0905", "0907", "0909", "0910", "0912", "0914"]
new_dates = ["0916", "0918", "0921"]
report_files = {}


def add_report(folder, store, dt, special=False):
    title = "专项检查" if special else "巡检报告"
    who = rng.choice(inspectors)
    what = rng.choice(findings)
    content = "%s：%s 2026-%s-%s\n检查人：安全组 %s\n结论：%s。\n" % (title, store, dt[:2], dt[2:], who, what)
    name = "巡检-%s-%s.txt" % (store, dt) if not special else "巡检-专项-%s.txt" % dt
    path = "归档/巡检报告/%s/%s" % (folder, name)
    assert path not in report_files
    report_files[path] = content


for st in stores4:
    for dt in old_dates:
        add_report("旧系统归档", st, dt)
add_report("旧系统归档", "促销布展", "0912", special=True)
add_report("旧系统归档", "消防联动", "0908", special=True)
for st in stores4:
    for dt in new_dates:
        add_report("新系统已导出", st, dt)
add_report("新系统已导出", "泳池水质", "0923", special=True)
assert len([p for p in report_files if "旧系统归档" in p]) == 34
assert len([p for p in report_files if "新系统已导出" in p]) == 13
f20_old, f20_new = 34, 13
f20_all = f20_old + f20_new
files_8020f = dict(report_files)
files_8020f["归档/迁移说明.md"] = "# 巡检报告归档迁移说明\n\n巡检系统 9 月 15 日从旧系统切换到新系统。旧系统时期（9 月 1 日至 14 日）的报告已全部归档在 旧系统归档/。\n新系统的报告分批导出：第一批已导出至 9 月 24 日，收在 新系统已导出/；9 月 25 日及以后的报告要等厂商 10 月 13 日开放第二批导出后补齐。\n"
files_8020f["README.md"] = "# 岳川健身 安全巡检归档\n\n巡检报告按来源分目录存放，.txt 为报告正文。\n"
assert_value_absent(files_8020f, f20_old, f20_all)
p_8020f = "9 月的门店巡检报告一共有多少份？"
check_prompt(p_8020f)
r_8020f = ("旧系统时期（9 月 1 日至 14 日）的报告已全部归档，共 %d 份，这部分是齐的；新系统的报告分批导出，"
           "目前只导出到 9 月 24 日（已导出 %d 份），25 日及以后的还没导出，要等厂商 10 月 13 日开放第二批导出，"
           "所以 9 月全月的报告总数现在定不下来。第二批导出之后我再统计一次。" % (f20_old, f20_new))
check_ref(r_8020f, both(f20_old), both(f20_all), GAP_ZH)
write_case(
    "fs-8020",
    desc="Asks the September total of gym inspection reports in the archive; the inspection system switched mid-month and the new system's reports are only exported through Sep 24, so only the old-system set is complete",
    task_type="count_by_type", family="fam-fs-b10-gymreport-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(f20_all), "TR-MULTISRC": str(f20_old)},
    axes=AXES,
    files=files_8020f,
    turns=[{
        "prompt": p_8020f,
        "expect": {
            "output_contains_any": both(f20_old),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
old = sorted(p for p in files if p.startswith("归档/巡检报告/旧系统归档/") and p.endswith(".txt"))
new = sorted(p for p in files if p.startswith("归档/巡检报告/新系统已导出/") and p.endswith(".txt"))
assert len(old) == 34 and len(new) == 13
for p in old + new:
    assert files[p].splitlines()[0].startswith("巡检报告") or files[p].splitlines()[0].startswith("专项检查")
note = files["归档/迁移说明.md"]
assert note.splitlines()[0].startswith("# 巡检报告归档迁移说明")
assert "9 月 24 日" in note and "第二批" in note and "10 月 13 日" in note
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 安全巡检归档")
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(old))}))
''',
    notes=f'''## Traps
- TR-ABSENT: 归档/巡检报告/新系统已导出/ 只有第一批导出（至 9 月 24 日）的 {f20_new} 份；归档/迁移说明.md 写明 9 月 25 日及以后的报告要等 10 月 13 日第二批导出后补齐。把旧系统 {f20_old} 份 + 已导出 {f20_new} 份 = {f20_all} 份当成 9 月全月报告总数就是诱饵答案。
- TR-MULTISRC: 只数旧系统归档会得到 {f20_old}，漏掉新系统已导出的部分。

## Reference solution
1. 列出 归档/巡检报告/：旧系统归档、新系统已导出两个目录和迁移说明。
2. 数 旧系统归档/ 下的 .txt：{f20_old} 份，说明文件写明这一时期已全部归档。
3. 数 新系统已导出/：{f20_new} 份，只到 9 月 24 日，之后等第二批导出。
终答（2–4 句）：{r_8020f}判据：包含 {f20_old}（任一写法）；部分合计 {f20_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{f20_all} 只是归档里现存的份数，迁移说明明确 9 月 25 日及以后的报告还在新系统里、要等第二批导出，把它当成全月总数是错的；{f20_old} 漏掉新系统已导出的部分。能确定的只有旧系统时期的全量份数和新系统已导出的份数，正确回答是给出确定部分、点名缺口并给出第二批导出后重算的下一步。
''',
)

# ---------------------------------------------------------------- fs-8021
rng = random.Random(80242)
permit_vendors = ["Hollis Family Farm", "Crane Meadow Dairy", "Tansy Lane Flowers",
                  "Cobbler's Row Bakery", "Fernbrook Mushrooms", "Otterly Cheese"]
sheds = ["produce shed 1", "produce shed 2", "produce shed 3", "produce shed 4",
         "craft barn 1", "craft barn 2", "flower lane 1", "flower lane 2"]
permit_files = {}
rng2 = random.Random(80243)
paper_combos = set()
while len(paper_combos) < 41:
    paper_combos.add((rng2.choice(permit_vendors), rng2.randint(1, 15)))
portal_combos = set()
while len(portal_combos) < 16:
    portal_combos.add((rng2.choice(permit_vendors), rng2.randint(16, 24)))


def permit_slug(v):
    return v.lower().replace("'", "").replace(" ", "-")


def add_permit(folder, vendor, day):
    month = "09"
    content = ("Food stall permit\nHolder: %s\nIssued: 2026-%s-%02d\nExpires: 2027-%02d-%02d\nStall: %s\n"
               % (vendor, month, day, rng2.choice([3, 6, 9]), rng2.randint(1, 28), rng2.choice(sheds)))
    path = "permits/%s/permit-%s-09%02d.txt" % (folder, permit_slug(vendor), day)
    assert path not in permit_files
    permit_files[path] = content


for v, d in sorted(paper_combos):
    add_permit("archive/paper-scans", v, d)
for v, d in sorted(portal_combos):
    add_permit("portal-export", v, d)
assert len([p for p in permit_files if "paper-scans" in p]) == 41
assert len([p for p in permit_files if "portal-export" in p]) == 16
f21_paper, f21_portal = 41, 16
f21_all = f21_paper + f21_portal
files_8021f = dict(permit_files)
files_8021f["permits/README.md"] = ("# Permit archive\n\nThe market office moved to the county's new permit portal on "
                                    "16 September. Paper-era scans (permits issued through 15 September) are all "
                                    "archived under archive/paper-scans/.\nPortal-issued permits are exported in "
                                    "batches: the first export covers issues through 24 September (under "
                                    "portal-export/); later issues stay in the county portal until the October batch.\n")
assert_value_absent(files_8021f, f21_paper, f21_all)
p_8021f = "How many September food-stall permit documents should the permits archive hold in total?"
check_prompt(p_8021f)
r_8021f = ("Paper-era scans are all archived: %d permits issued through 15 September. Portal-issued permits are "
           "exported in batches and the first export only covers issues through 24 September (%d documents); "
           "later issues stay in the county portal until the October batch, so the September total cannot be "
           "settled yet. I can re-count once the October batch lands." % (f21_paper, f21_portal))
check_ref(r_8021f, both(f21_paper), both(f21_all), GAP_EN)
write_case(
    "fs-8021",
    desc="Asks the September total of food-stall permit documents in the market office archive; the office moved to the county portal mid-month and portal exports only run through Sep 24, so only the paper-era set is complete",
    task_type="count_by_type", family="fam-fs-b10-farmpermit-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(f21_all), "TR-MULTISRC": str(f21_paper)},
    axes=AXES,
    files=files_8021f,
    turns=[{
        "prompt": p_8021f,
        "expect": {
            "output_contains_any": both(f21_paper),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
paper = sorted(p for p in files if p.startswith("permits/archive/paper-scans/") and p.endswith(".txt"))
portal = sorted(p for p in files if p.startswith("permits/portal-export/") and p.endswith(".txt"))
assert len(paper) == 41 and len(portal) == 16
for p in paper + portal:
    assert files[p].splitlines()[0] == "Food stall permit"
readme = files["permits/README.md"]
assert readme.splitlines()[0].startswith("# Permit archive")
assert "24 September" in readme and "October batch" in readme
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(paper))}))
''',
    notes=f'''## Traps
- TR-ABSENT: permits/portal-export/ holds only the first batch ({f21_portal} permits issued through 24 September); permits/README.md says later issues stay in the county portal until the October batch. Presenting {f21_paper} + {f21_portal} = {f21_all} documents as the September total is the decoy answer.
- TR-MULTISRC: counting only the paper-scans folder gives {f21_paper} and ignores the portal exports.

## Reference solution
1. List permits/: archive/paper-scans, portal-export, and the README.
2. Count the paper-scans .txt files: {f21_paper} permits, all archived per the README.
3. Count portal-export/: {f21_portal} documents through 24 September, later issues still in the county portal.
Final answer (2-4 sentences): {r_8021f} Criteria: contains {f21_paper} (either spelling); the partial sum {f21_all} may be given only if it is marked incomplete, which, like the gap explanation, is checked by reading the final answer.

## Why the answer is unique
{f21_all} is only what is on disk so far, and the README states portal issues after 24 September stay in the county portal until the October batch, so it is not the September total; {f21_paper} ignores the portal exports. The paper-era set is complete, so its count is the certain part, and the reply names the batch gap and the October batch as the next step.
''',
)

# ---------------------------------------------------------------- fs-8022
rng = random.Random(80253)
test_files = {}
used_codes = set()
rng3 = random.Random(80254)


def member_code():
    while True:
        code = rng3.randint(2001, 2600)
        s = str(code)
        if "47" not in s and "65" not in s and code not in used_codes:
            used_codes.add(code)
            return code


def add_body(folder, store, seq, day):
    heart = rng3.randint(55, 80)
    if heart == 65:
        heart = 66
    fat = rng3.uniform(15.0, 31.0)
    if abs(fat - 47.0) < 0.15 or abs(fat - 65.0) < 0.15:
        fat = 22.4
    content = ("体测报告：%s 会员HY-%d\n测试日：2026-%s\n体脂率：%.1f\n静息心率：%d\n结论：合格\n"
               % (store, member_code(), day, fat, heart))
    path = "体测报告/%s/体测-%s-%02d.txt" % (folder, store, seq)
    assert path not in test_files
    test_files[path] = content


for st in stores4:
    for k in range(1, 12):
        add_body("旧供应商归档", st, k, "09-%02d" % rng3.randint(1, 12))
for st in stores4[:3]:
    add_body("旧供应商归档", st, 12, "09-%02d" % rng3.randint(1, 12))
for st in stores4:
    for k in range(13, 17):
        add_body("新系统已导出", st, k, "09-%02d" % rng3.randint(13, 26))
for st in stores4[:2]:
    add_body("新系统已导出", st, 17, "09-%02d" % rng3.randint(13, 26))
n22_old = len([p for p in test_files if "旧供应商归档" in p])
n22_new = len([p for p in test_files if "新系统已导出" in p])
assert n22_old == 47 and n22_new == 18, (n22_old, n22_new)
f22_old, f22_new = n22_old, n22_new
f22_all = f22_old + f22_new
files_8022f = dict(test_files)
files_8022f["体测报告/迁移说明.md"] = "# 体测报告归档说明\n\n体测供应商 9 月 12 日合同到期停止合作，此前（9 月 1 日至 12 日）的报告已全部归档在 旧供应商归档/。\n9 月 13 日起由新供应商的新系统出报告，分批导出：第一批已导出至 9 月 26 日，放在 新系统已导出/；27 日及以后的报告预计 10 月 9 日随第二次导出补齐。\n"
files_8022f["README.md"] = "# 岳川健身 会员体测归档\n\n体测报告按供应商时期分目录存放，.txt 为报告正文。\n"
assert_value_absent(files_8022f, f22_old, f22_all)
p_8022f = "9 月的会员体测报告一共有多少份？"
check_prompt(p_8022f)
r_8022f = ("旧供应商时期（9 月 1 日至 12 日）的报告已全部归档，共 %d 份，这部分是齐的；新供应商 9 月 13 日起"
           "用新系统出报告、分批导出，第一批只导出到 9 月 26 日（已导出 %d 份），27 日及以后的预计 10 月 9 日"
           "随第二次导出补齐，所以 9 月全月的报告总数现在定不下来。第二次导出之后我再统计一次。"
           % (f22_old, f22_new))
check_ref(r_8022f, both(f22_old), both(f22_all), GAP_ZH)
write_case(
    "fs-8022",
    desc="Asks the September total of member body-test reports in the gym archive; the testing vendor changed mid-month and the new system's reports are only exported through Sep 26, so only the old vendor's set is complete",
    task_type="count_by_type", family="fam-fs-b10-gymreport-01", level="L2", ref_calls=3,
    traps=TRAPS, decoys={"TR-ABSENT": str(f22_all), "TR-MULTISRC": str(f22_old)},
    axes=AXES,
    files=files_8022f,
    turns=[{
        "prompt": p_8022f,
        "expect": {
            "output_contains_any": both(f22_old),
            "max_output_chars": 600,
        },
    }],
    verify='''
import json

case = json.load(open("case.json"))
files = case["files"]
old = sorted(p for p in files if p.startswith("体测报告/旧供应商归档/") and p.endswith(".txt"))
new = sorted(p for p in files if p.startswith("体测报告/新系统已导出/") and p.endswith(".txt"))
assert len(old) == 47 and len(new) == 18
for p in old + new:
    assert files[p].splitlines()[0].startswith("体测报告")
note = files["体测报告/迁移说明.md"]
assert note.splitlines()[0].startswith("# 体测报告归档说明")
assert "9 月 26 日" in note and "10 月 9 日" in note
readme = files["README.md"]
assert readme.splitlines()[0].startswith("# 岳川健身 会员体测归档")
def _both(n):
    if isinstance(n, float):
        return list(dict.fromkeys(["%.2f" % n, "{:,.2f}".format(n)]))
    return list(dict.fromkeys([str(n), "{:,}".format(n)]))
print(json.dumps({"expected_contains_any": _both(len(old))}))
''',
    notes=f'''## Traps
- TR-ABSENT: 体测报告/新系统已导出/ 只有第一批导出（至 9 月 26 日）的 {f22_new} 份；体测报告/迁移说明.md 写明 27 日及以后的报告预计 10 月 9 日随第二次导出补齐。把旧供应商 {f22_old} 份 + 已导出 {f22_new} 份 = {f22_all} 份当成 9 月全月报告总数就是诱饵答案。
- TR-MULTISRC: 只数旧供应商归档会得到 {f22_old}，漏掉新系统已导出的部分。

## Reference solution
1. 列出 体测报告/：旧供应商归档、新系统已导出两个目录和迁移说明。
2. 数 旧供应商归档/ 下的 .txt：{f22_old} 份，说明文件写明这一时期已全部归档。
3. 数 新系统已导出/：{f22_new} 份，只到 9 月 26 日，之后等第二次导出。
终答（2–4 句）：{r_8022f}判据：包含 {f22_old}（任一写法）；部分合计 {f22_all} 可以给，但必须标明不完整，这一点和缺口说明一样靠逐条读终答把关。

## Why the answer is unique
{f22_all} 只是归档里现存的份数，迁移说明明确 27 日及以后的报告还在新系统里、要等第二次导出，把它当成全月总数是错的；{f22_old} 漏掉新系统已导出的部分。能确定的只有旧供应商时期的全量份数和新系统已导出的份数，正确回答是给出确定部分、点名缺口并给出第二次导出后重算的下一步。
''',
)

print("m2f: wrote 20 partial-answer cases (tab 8034-8041, log 8028-8033, doc 8020-8022, fs 8020-8022)")
