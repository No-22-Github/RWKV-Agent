"""M3 (v1.4 §3.3) b10a, part C: ask-for-the-missing-parameter counter-questions.

Turn 1 names a task but withholds one parameter (path / file name / time range /
keyword / which classes, pumps, rooms...), and the user says to ask first without
calling tools. Turn 2 supplies the parameter and the task completes normally.
"""
import random
import re
from common import revised

write_case = revised({'tab-8052': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'tab-8053': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'tab-8054': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'tab-8055': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'tab-8056': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'tab-8057': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8042': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8043': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8044': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8045': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8046': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'log-8047': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'cfg-8050': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'cfg-8051': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'cfg-8052': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'cfg-8053': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'fs-8029': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'fs-8030': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'fs-8031': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'fs-8032': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'nt-8041': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'nt-8042': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'nt-8043': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'nt-8044': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。', 'nt-8045': '反问词表补上点名参数的常见说法（姓名 / 名称 / 编号 / 路径 / 起止日期等）：S5 老师普遍用「请告诉我教练的姓名」「Which log file」这类问法，已点名缺的参数，但被原词表漏判；词表仍只收点名参数的说法，不收泛问。'})

NOCALL = {"tools": [], "require_active_no_call": True}


def trim(x):
    return ("%.2f" % x).rstrip("0").rstrip(".")


def money_forms(x):
    a = trim(x)
    b = "{:,.2f}".format(x).rstrip("0").rstrip(".")
    return [a] if a == b else [a, b]


SURNAMES = ["王", "李", "张", "刘", "陈", "杨", "赵", "周", "吴", "徐",
            "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "郑", "梁"]
GIVEN = ["沐宸", "若汐", "浩宇", "一诺", "梓萱", "宇轩", "雨桐", "子墨", "可欣", "皓轩",
         "思远", "乐怡", "承泽", "芯语", "嘉树", "安然", "知夏", "书瑶", "望舒", "云舟",
         "清越", "既明", "疏影", "鹿鸣", "南乔", "时安", "聿修", "温叙", "砚知", "念初"]


def kid_names(seed, n):
    r = random.Random(seed)
    pairs = [s + g for s in SURNAMES for g in GIVEN]
    r.shuffle(pairs)
    return pairs[:n]


# ---------------------------------------------------------------- tab-8052
rng = random.Random(80521)
classes = ["贝贝班", "星星班", "彩虹班", "月亮班"]
snacks = ["鲜奶", "酸奶", "水果", "软面包"]
days_by旬 = {"上旬": ["09-%02d" % d for d in range(1, 11)],
             "中旬": ["09-%02d" % d for d in range(11, 21)],
             "下旬": ["09-%02d" % d for d in range(21, 31)]}
meal_csv = {k: "班级,日期,加餐项目,金额\n" + "".join(
    "%s,%s,%s,%.2f\n" % (c, d, rng.choice(snacks), rng.choice([6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0]))
    for d in days for c in classes)
    for k, days in days_by旬.items()}
up_sum = round(sum(float(l.rsplit(",", 1)[1]) for l in meal_csv["上旬"].splitlines()[1:]), 2)
forms = money_forms(up_sum)
write_case(
    "tab-8052",
    desc="Turn 1 asks for a snack-fee total but the user will say which of the three ten-day sheets to use and the assistant must ask first; turn 2 names the file",
    task_type="aggregate", family="fam-tab-b10-kinderlunch-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "托管/餐费/九月上旬.csv": meal_csv["上旬"],
        "托管/餐费/九月中旬.csv": meal_csv["中旬"],
        "托管/餐费/九月下旬.csv": meal_csv["下旬"],
        "托管/餐费/说明.md": "餐费表按旬拆成上、中、下旬三份，金额单位为元，每行是一个班一天的加餐支出。\n",
    },
    turns=[
        {"prompt": "帮我汇总九月的加餐费。餐费表按旬拆成了好几份，先用哪一份我来定——你先问我，别自己去翻。",
         "expect": dict(NOCALL, output_contains_any=["哪一份", "哪份", "哪个文件", "文件名", "文件路径", "文件的路径"], max_output_chars=300)},
        {"prompt": "先用 托管/餐费/九月上旬.csv 这一份。",
         "expect": {"output_contains_any": forms, "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
for path in ("托管/餐费/九月上旬.csv", "托管/餐费/九月中旬.csv", "托管/餐费/九月下旬.csv"):
    assert f[path].startswith("班级,日期,加餐项目,金额"), path
assert "按旬" in f["托管/餐费/说明.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".csv") and p in prompt]
assert len(chosen) == 1, chosen
rows = list(csv.DictReader(io.StringIO(f[chosen[0]])))
total = round(sum(float(r["金额"]) for r in rows), 2)
ask = ["哪一份", "哪份", "哪个文件", "文件名", "文件路径", "文件的路径"]
print(json.dumps({"expected_contains_any": ask +
                  [("%.2f" % total).rstrip("0").rstrip("."),
                   "{:,.2f}".format(total).rstrip("0").rstrip(".")]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户说明会指定用哪份表、要求先问；第 2 轮给出文件后正常汇总。

## Reference solution
第 1 轮不调用工具，一句问句点名缺的参数，例如「先用哪一份餐费表？请给我文件名或路径。」
第 2 轮：对 托管/餐费/九月上旬.csv 的 金额 列求和，得 %s 元。终答一句话写明用了哪份表和合计金额。判据：第 1 轮零调用并问到哪份文件；第 2 轮包含 %s。

## Why the answer is unique
第 2 轮指定了上旬表；金额列为正数且每行独立，对指定文件的金额列求和结果唯一。中旬、下旬是别的旬的表。
''' % (forms[0], forms[0]),
)

# ---------------------------------------------------------------- tab-8053
rng = random.Random(80532)
coaches = ["沈教练", "钱教练", "蒋教练"]
weeks = [("2026-08-01_至_07", ["2026-08-%02d" % d for d in range(1, 8)]),
         ("2026-08-08_至_14", ["2026-08-%02d" % d for d in range(8, 15)]),
         ("2026-08-15_至_21", ["2026-08-%02d" % d for d in range(15, 22)])]


def lesson_csv(days):
    rows = []
    for d in days:
        for _ in range(3):
            rows.append([d, rng.choice(coaches), rng.choice(["亲子班", "幼儿班", "学龄班"]),
                         rng.choice([1.0, 1.0, 2.0, 2.0])])
    rows[rng.randrange(len(rows))][3] = 0.5
    return "日期,教练,班型,课时\n" + "".join("%s,%s,%s,%.1f\n" % tuple(r) for r in rows)


lesson_csvs = {name: lesson_csv(days) for name, days in weeks}
week_sum = round(sum(float(l.rsplit(",", 1)[1])
                     for l in lesson_csvs["2026-08-08_至_14"].splitlines()[1:]), 1)
w2 = ("%.1f" % week_sum).rstrip("0").rstrip(".")
write_case(
    "tab-8053",
    desc="Turn 1 asks for a lesson-hour total but the week is undecided and the user will name it; the assistant must ask first without tools; turn 2 gives the week",
    task_type="aggregate", family="fam-tab-b10-swimweeklog-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/消课/2026-08-01_至_07.csv": lesson_csvs["2026-08-01_至_07"],
        "游泳馆/消课/2026-08-08_至_14.csv": lesson_csvs["2026-08-08_至_14"],
        "游泳馆/消课/2026-08-15_至_21.csv": lesson_csvs["2026-08-15_至_21"],
        "游泳馆/说明.md": "消课表按周拆分，每行一节消课记录，课时最小单位 0.5。\n",
    },
    turns=[
        {"prompt": "帮我统计教练的消课课时总数。统计哪一周我还没定——你先问我，别查文件。",
         "expect": dict(NOCALL, output_contains_any=["哪一周", "哪周", "哪个时间段", "时间范围", "起止日期", "日期范围", "哪几天"], max_output_chars=300)},
        {"prompt": "统计 8 月 8 日到 8 月 14 日这一周。",
         "expect": {"output_contains": [w2], "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if path.endswith(".csv"):
        assert f[path].startswith("日期,教练,班型,课时"), path
assert "按周" in f["游泳馆/说明.md"]
chosen = [p for p in f if p.endswith(".csv") and "2026-08-08" in p]
assert len(chosen) == 1, chosen
rows = list(csv.DictReader(io.StringIO(f[chosen[0]])))
dates = [r["日期"] for r in rows]
assert dates[0] == "2026-08-08" and dates[-1] == "2026-08-14"
total = round(sum(float(r["课时"]) for r in rows), 1)
ask = ["哪一周", "哪周", "哪个时间段", "时间范围", "起止日期", "日期范围", "哪几天"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问统计哪一周、不调用工具；第 2 轮给出周次后正常汇总。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要统计哪一周？请给我起止日期。」
第 2 轮：对 游泳馆/消课/2026-08-08_至_14.csv 的 课时 列求和，得 %s 课时。终答一句话写明周次和合计课时。判据：第 1 轮零调用并问到周次；第 2 轮包含 %s。

## Why the answer is unique
第 2 轮指定了 8 月 8 日至 14 日这一周，对应唯一一份消课表；课时列求和结果唯一，另两周的表不在统计范围内。
''' % (w2, w2),
)

# ---------------------------------------------------------------- tab-8054
rng = random.Random(80541)
class_sizes = {"托班": 9, "小班": 11, "中班": 12, "大班": 10}
name_pool = kid_names(8054, sum(class_sizes.values()))
roster = {}
i = 0
for cls, n in class_sizes.items():
    roster[cls] = name_pool[i:i + n]
    i += n
class_csv = {cls: "姓名,月托管费\n" + "".join(
    "%s,%d\n" % (nm, rng.choice([360, 380, 400, 420])) for nm in roster[cls])
    for cls in class_sizes}
fee_sum = {cls: sum(int(l.rsplit(",", 1)[1]) for l in s.splitlines()[1:])
           for cls, s in class_csv.items()}
t2 = fee_sum["小班"] + fee_sum["大班"]
write_case(
    "tab-8054",
    desc="Turn 1 asks for a combined monthly daycare-fee total but the user will pick which two of four classes; the assistant must ask first; turn 2 names the two classes",
    task_type="aggregate", family="fam-tab-b10-kindertuition-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "托班.csv": class_csv["托班"],
        "小班.csv": class_csv["小班"],
        "中班.csv": class_csv["中班"],
        "大班.csv": class_csv["大班"],
        "托管/说明.md": "各班一份在册名单，月托管费为该生十月标准，单位元。\n",
    },
    turns=[
        {"prompt": "我要算其中两个班的月托管费总额，具体哪两个班我来挑——你先问我，别翻班级表。",
         "expect": dict(NOCALL, output_contains_any=["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"], max_output_chars=300)},
        {"prompt": "小班和大班这两个班。",
         "expect": {"output_contains": [str(t2)], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
classes = ["托班", "小班", "中班", "大班"]
for cls in classes:
    assert f[cls + ".csv"].startswith("姓名,月托管费"), cls
assert "月托管费" in f["托管/说明.md"]
chosen = [c for c in classes if c in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
total = 0
for cls in chosen:
    rows = list(csv.DictReader(io.StringIO(f[cls + ".csv"])))
    total += sum(int(r["月托管费"]) for r in rows)
ask = ["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户说要自己挑班、要求先问；第 2 轮点名两个班后正常合计。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要算哪两个班？请告诉我班名。」
第 2 轮：分别读 小班.csv 和 大班.csv，各班 月托管费 求和后相加，得 %d 元。终答一句话写明两个班和合计金额。判据：第 1 轮零调用并问到哪两个班；第 2 轮包含 %d。

## Why the answer is unique
第 2 轮指定小班、大班两份名单；月托管费列求和唯一，托班、中班两份不在范围内。
''' % (t2, t2),
)

# ---------------------------------------------------------------- tab-8055
rng = random.Random(80551)
students = ["Maya Chen", "Liam Ortiz", "Ava Brooks", "Noah Kim", "Sofia Reyes", "Ethan Park",
            "Ivy Nolan", "Owen Diaz", "Ruby Patel", "Leo Marsh", "Tessa Quinn", "Milo Grant"]
rates = {"starter": 45, "ten-pack": 40, "drop-in": 55}
billing_rows = []
for st in students:
    plan = rng.choice(list(rates))
    sess = rng.randint(2, 10)
    billing_rows.append((st, plan, sess, sess * rates[plan]))
    if st in ("Maya Chen", "Owen Diaz"):
        plan2 = rng.choice([p for p in rates if p != plan])
        sess2 = rng.randint(1, 4)
        billing_rows.append((st, plan2, sess2, sess2 * rates[plan2]))
bill_csv = "student,plan,sessions,fee\n" + "".join("%s,%s,%d,%d\n" % r for r in billing_rows)
t2 = sum(r[3] for r in billing_rows if r[0] in ("Maya Chen", "Liam Ortiz"))
write_case(
    "tab-8055",
    desc="Turn 1 asks for a two-student lesson-fee total but the user will name the students and the assistant must ask first; turn 2 names Maya Chen and Liam Ortiz",
    task_type="aggregate", family="fam-tab-b10-tutorbilling-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "tutoring/billing/2026-09.csv": bill_csv,
        "README.md": "BrightPath Tutoring Center billing export for September. One row per student per plan; fee is the row total in dollars.\n",
    },
    turns=[
        {"prompt": "I need the September lesson-fee total for two of our students. I'll tell you which two; ask me first and don't look anything up.",
         "expect": dict(NOCALL, output_contains_any=["which two", "Which two", "which students", "which names", "Which students", "student names", "two student names", "name the two"], max_output_chars=300)},
        {"prompt": "Maya Chen and Liam Ortiz.",
         "expect": {"output_contains": [str(t2)], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["tutoring/billing/2026-09.csv"].startswith("student,plan,sessions,fee")
assert f["README.md"].startswith("BrightPath Tutoring Center")
rows = list(csv.DictReader(io.StringIO(f["tutoring/billing/2026-09.csv"])))
students = sorted({r["student"] for r in rows})
chosen = [s for s in students if s in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
total = sum(int(r["fee"]) for r in rows if r["student"] in chosen)
ask = ["which two", "Which two", "which students", "which names", "Which students", "student names", "two student names", "name the two"]
print(json.dumps({"expected_number": total, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. Turn 1 asks the assistant to wait for the two student names.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two students should I total?"
Turn 2: read tutoring/billing/2026-09.csv, sum the fee column over every row of Maya Chen and Liam Ortiz: %d dollars. Final answer in one sentence with both names and the total. Criteria: turn 1 zero-call and asks which students; turn 2 contains %d.

## Why the answer is unique
Turn 2 fixes the two students; their fee rows sum to a single value, and the other students' rows are out of scope.
''' % (t2, t2),
)

# ---------------------------------------------------------------- tab-8056
rng = random.Random(80562)
members = kid_names(8056, 16)
if "周沐宸" in members:
    members[members.index("周沐宸")] = "周沐知"
members[3] = "周沐宸"
cards = ["亲子畅游卡", "幼儿次卡", "学龄季卡"]
member_csv = "姓名,卡种,剩余课时\n" + "".join(
    "%s,%s,%s\n" % (nm, rng.choice(cards),
                    "13.5" if nm == "周沐宸" else rng.choice(
                        ["8", "8.5", "12", "15", "16", "16.5", "20", "20.5", "22", "24", "25.5", "28", "30", "31", "34"]))
    for nm in members)
write_case(
    "tab-8056",
    desc="Turn 1 asks for one child's remaining swim-lesson hours but the child's name is withheld and the assistant must ask first; turn 2 names the child",
    task_type="filter_count", family="fam-tab-b10-swimmembers-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/会员/剩余课时.csv": member_csv,
        "游泳馆/说明.md": "会员课时余量按月导出，剩余课时最小单位 0.5。\n",
    },
    turns=[
        {"prompt": "帮我查一位小学员还剩多少课时，孩子的姓名我还没说——你先问我，别翻会员表。",
         "expect": dict(NOCALL, output_contains_any=["哪个孩子", "哪位学员", "哪个姓名", "孩子叫什么", "学员的姓名", "孩子的姓名", "学员姓名", "孩子的名字", "学员编号"], max_output_chars=300)},
        {"prompt": "查 周沐宸 这位小学员。",
         "expect": {"output_contains": ["13.5"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["游泳馆/会员/剩余课时.csv"].startswith("姓名,卡种,剩余课时")
assert "最小单位 0.5" in f["游泳馆/说明.md"]
rows = list(csv.DictReader(io.StringIO(f["游泳馆/会员/剩余课时.csv"])))
names = [r["姓名"] for r in rows]
assert len(set(names)) == len(names)
hits = [r for r in rows if r["姓名"] in case["turns"][1]["prompt"]]
assert len(hits) == 1, hits
ask = ["哪个孩子", "哪位学员", "哪个姓名", "孩子叫什么", "学员的姓名", "孩子的姓名", "学员姓名", "孩子的名字", "学员编号"]
print(json.dumps({"expected_number": float(hits[0]["剩余课时"]),
                  "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问孩子姓名、不翻表；第 2 轮给出姓名后正常查询。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要查哪个孩子？请告诉我孩子姓名。」
第 2 轮：在 游泳馆/会员/剩余课时.csv 里按 姓名=周沐宸 找到那一行，报 剩余课时 13.5 节。终答一句话写明孩子和剩余课时。判据：第 1 轮零调用并问到孩子姓名；第 2 轮包含 13.5。

## Why the answer is unique
姓名列取值互不相同，按周沐宸过滤后只剩一行，剩余课时唯一。
''',
)

# ---------------------------------------------------------------- tab-8057
rng = random.Random(80572)
seen = set()
session_rows = []
for d in range(1, 8):
    for sess in ("上午场", "下午场"):
        rev = rng.randint(4200, 8800)
        while rev in seen:
            rev = rng.randint(4200, 8800)
        seen.add(rev)
        session_rows.append(("10-%02d" % d, sess, rng.randint(9, 18), rev))
sess_csv = "日期,场次,入场组数,票房收入\n" + "".join("%s,%s,%d,%d\n" % r for r in session_rows)
target = [r for r in session_rows if r[0] == "10-03" and r[1] == "下午场"][0]
write_case(
    "tab-8057",
    desc="Turn 1 asks for one session's gate revenue but the user will say which of the holiday sessions; the assistant must ask first; turn 2 names Oct 3 afternoon",
    task_type="filter_count", family="fam-tab-b10-swimsession-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/票务/国庆场次.csv": sess_csv,
        "游泳馆/说明.md": "国庆档按日按场记录，票房收入单位为元。\n",
    },
    turns=[
        {"prompt": "帮我报其中一场的票房收入，具体哪一场我来定——你先问我，别查表。",
         "expect": dict(NOCALL, output_contains_any=["哪一场", "哪个场次", "哪一场次", "哪一天的哪一场", "具体场次", "场次名称", "哪个时段"], max_output_chars=300)},
        {"prompt": "10 月 3 日下午场那一场。",
         "expect": {"output_contains": [str(target[3])], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import csv
import io
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["游泳馆/票务/国庆场次.csv"].startswith("日期,场次,入场组数,票房收入")
assert "票房收入单位为元" in f["游泳馆/说明.md"]
rows = list(csv.DictReader(io.StringIO(f["游泳馆/票务/国庆场次.csv"])))
m = re.search(r"(\\d+)\\s*月\\s*(\\d+)\\s*日", case["turns"][1]["prompt"])
day = "10-%02d" % int(m.group(2))
sess = "下午场" if "下午场" in case["turns"][1]["prompt"] else "上午场"
hits = [r for r in rows if r["日期"] == day and r["场次"] == sess]
assert len(hits) == 1, hits
ask = ["哪一场", "哪个场次", "哪一场次", "哪一天的哪一场", "具体场次", "场次名称", "哪个时段"]
print(json.dumps({"expected_number": int(hits[0]["票房收入"]),
                  "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户说要自己定场次、要求先问；第 2 轮点名日期和场次后正常查询。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要报哪一场？请给我日期和场次。」
第 2 轮：在 游泳馆/票务/国庆场次.csv 里按 日期=10-03、场次=下午场 找到那一行，报 票房收入 %d 元。判据：第 1 轮零调用并问到哪一场；第 2 轮包含 %d。

## Why the answer is unique
日期加场次唯一定位一行，且各场票房收入互不相同，答案唯一。
''' % (target[3], target[3]),
)

# ---------------------------------------------------------------- log-8042
rng = random.Random(80422)


def water_log(day, n_alert):
    lines = []
    t = 6 * 3600
    while t < 22 * 3600:
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        lines.append("2026-09-%s %02d:%02d:%02d 余氯 %.2fmg/L 正常" % (day, h, m, s, rng.uniform(0.4, 0.9)))
        t += rng.randint(2400, 4800)
    for i in rng.sample(range(len(lines)), n_alert):
        hi = rng.random() < 0.5
        val = rng.uniform(1.1, 2.2) if hi else rng.uniform(0.05, 0.2)
        lines[i] = re.sub(r"余氯 [0-9.]+mg/L 正常",
                          "余氯 %.2fmg/L " % val + ("偏高 告警" if hi else "偏低 告警"),
                          lines[i])
    return "\n".join(lines) + "\n"


pump_log = "\n".join(
    "2026-09-15 %02d:%02d:00 %s%s" % (h, rng.randint(0, 59), pump,
                                      " 电流波动 告警" if (h, pump) in ((8, "2号泵"), (15, "1号泵")) else " 启动 正常")
    for h, pump in [(7, "1号泵"), (8, "2号泵"), (10, "1号泵"), (12, "3号泵"),
                    (15, "1号泵"), (17, "2号泵"), (19, "3号泵")]) + "\n"
write_case(
    "log-8042",
    desc="Turn 1 asks to count water-quality alerts but the user will name which of several logs to read; the assistant must ask first without tools; turn 2 names the file",
    task_type="count_events", family="fam-log-b10-wateralarm-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/日志/水质-2026-09-15.log": water_log("15", 7),
        "游泳馆/日志/水质-2026-09-16.log": water_log("16", 3),
        "游泳馆/日志/循环泵-2026-09-15.log": pump_log,
        "游泳馆/日志/说明.md": "水质日志每行一次检测，余氯超出 0.3–1.0 mg/L 范围记为告警；循环泵日志单独存放。\n",
    },
    turns=[
        {"prompt": "帮我数池水水质的告警次数。日志有好几份，看哪一份我来定——你先问我，先别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["哪一份", "哪份", "哪个日志", "哪个文件", "文件名", "文件路径", "日志路径"], max_output_chars=300)},
        {"prompt": "看 游泳馆/日志/水质-2026-09-15.log 这一份。",
         "expect": {"output_contains": ["7"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if path.endswith(".log"):
        for line in f[path].splitlines():
            assert re.match(r"^2026-09-1[56] \\d\\d:\\d\\d:\\d\\d ", line), (path, line)
assert "记为告警" in f["游泳馆/日志/说明.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".log") and p in prompt]
assert len(chosen) == 1, chosen
n = sum(1 for line in f[chosen[0]].splitlines() if "告警" in line)
ask = ["哪一份", "哪份", "哪个日志", "哪个文件", "文件名", "文件路径", "日志路径"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问看哪份日志、不调用工具；第 2 轮点名文件后正常计数。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要看哪一份日志？请给我文件名或路径。」
第 2 轮：读 游泳馆/日志/水质-2026-09-15.log，统计含「告警」的行，共 7 次。终答一句话写明文件和次数。判据：第 1 轮零调用并问到哪份日志；第 2 轮包含 7。

## Why the answer is unique
第 2 轮指定 9 月 15 日水质日志；该文件内告警行恰 7 条，9 月 16 日水质日志（3 条）和循环泵日志（2 条）是别的文件，读错文件计数不同。
''',
)

# ---------------------------------------------------------------- log-8043
rng = random.Random(80432)
abn_by_day = {"12": 2, "13": 1, "14": 3, "15": 2, "16": 4}
kids = kid_names(8043, 12)
check_lines = []
for d, n_abn in abn_by_day.items():
    flags = [True] * n_abn + [False] * (len(kids) - n_abn)
    rng.shuffle(flags)
    for nm, abn in zip(kids, flags):
        temp = rng.uniform(37.3, 38.4) if abn else rng.uniform(36.2, 37.0)
        check_lines.append("2026-10-%s 08:%02d %s %.1f %s" % (d, rng.randint(0, 40), nm, temp,
                                                              "异常" if abn else "正常"))
checkf = "\n".join(check_lines) + "\n"
write_case(
    "log-8043",
    desc="Turn 1 asks to count abnormal morning-health-check entries but the date range is undecided; the assistant must ask first without tools; turn 2 gives Oct 14-15",
    task_type="count_events", family="fam-log-b10-morningcheck-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "托管/日志/晨检.log": checkf,
        "托管/说明.md": "晨检记录每行一名幼儿，体温列后为结论，取值 正常 或 异常。\n",
    },
    turns=[
        {"prompt": "帮我数晨检异常的记录条数，统计哪几天我还没定——你先问我，别调工具。",
         "expect": dict(NOCALL, output_contains_any=["哪几天", "哪天到哪天", "日期范围", "哪个日期", "起止日期", "时间范围"], max_output_chars=300)},
        {"prompt": "统计 10 月 14 日到 10 月 15 日这两天的。",
         "expect": {"output_contains": ["5"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["托管/日志/晨检.log"].splitlines():
    assert re.match(r"^2026-10-1[2-6] 08:\\d\\d \\S+ 3[678]\\.\\d (正常|异常)$", line), line
assert "正常 或 异常" in f["托管/说明.md"]
m = re.findall(r"(\\d+)\\s*月\\s*(\\d+)\\s*日", case["turns"][1]["prompt"])
assert len(m) == 2, m
d1, d2 = sorted(int(x[1]) for x in m)
n = sum(1 for line in f["托管/日志/晨检.log"].splitlines()
        if d1 <= int(line[8:10]) <= d2 and line.endswith("异常"))
ask = ["哪几天", "哪天到哪天", "日期范围", "哪个日期", "起止日期", "时间范围"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问统计哪几天、不调用工具；第 2 轮给出日期范围后正常计数。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要统计哪几天？请给我起止日期。」
第 2 轮：读 托管/日志/晨检.log，统计 10 月 14 日和 10 月 15 日（含两端）结论为「异常」的行，共 5 条。终答一句话写明日期范围和条数。判据：第 1 轮零调用并问到日期范围；第 2 轮包含 5。

## Why the answer is unique
日期范围在第 2 轮给定为 14–15 日两端都含；结论列只有 正常、异常 两种取值，计数唯一。
''',
)

# ---------------------------------------------------------------- log-8044
rng = random.Random(80442)
gate_counts = {10: 4, 11: 5, 12: 3, 13: 7, 14: 4, 15: 2, 16: 5, 17: 4, 18: 3}
gate_lines = ["2026-10-03 12:06:06 入园 G-110 1大1小"]
g = 110
for hour in sorted(gate_counts):
    for _ in range(gate_counts[hour]):
        g += 1
        gate_lines.append("2026-10-03 %02d:%02d:%02d 入园 G-%03d %d大%d小" % (
            hour, rng.randint(0, 59), rng.randint(0, 59), g, rng.randint(1, 2), rng.randint(0, 2)))
        if rng.random() < 0.6:
            gate_lines.append("2026-10-03 %02d:%02d:%02d 出园 G-%03d" % (
                hour, rng.randint(0, 59), rng.randint(0, 59), g))
rng.shuffle(gate_lines[1:])
target_n = sum(1 for l in gate_lines if " 入园 " in l and 14 <= int(l[11:13]) < 16)
assert target_n == 6, target_n
write_case(
    "log-8044",
    desc="Turn 1 asks to count gate entries but the time window is undecided and the user will set it; the assistant must ask first without tools; turn 2 gives 14:00-16:00",
    task_type="count_events", family="fam-log-b10-gateflow-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/日志/闸机-2026-10-03.log": "\n".join(gate_lines) + "\n",
        "游泳馆/说明.md": "闸机日志字段：日期 时间 事件 组号 成员构成；入园、出园都记一行。\n",
    },
    turns=[
        {"prompt": "帮我数 10 月 3 日闸机入园的人次，具体统计哪个时间段我还没定——你先问我，先别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["时间段", "几点", "起止", "时间范围"], max_output_chars=300)},
        {"prompt": "就统计下午 2 点到 4 点，含 14:00 整，不含 16:00。",
         "expect": {"output_contains": ["6"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["游泳馆/日志/闸机-2026-10-03.log"].splitlines():
    assert re.match(r"^2026-10-03 \\d\\d:\\d\\d:\\d\\d (入园 G-\\d{3} \\d大\\d小|出园 G-\\d{3})$", line), line
assert "入园、出园都记一行" in f["游泳馆/说明.md"]
n = sum(1 for line in f["游泳馆/日志/闸机-2026-10-03.log"].splitlines()
        if " 入园 " in line and 14 <= int(line[11:13]) < 16)
ask = ["时间段", "几点", "起止", "时间范围"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问时间段、不调用工具；第 2 轮给出 14:00–16:00 后正常计数。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要统计哪个时间段？请给我起止时间。」
第 2 轮：读 游泳馆/日志/闸机-2026-10-03.log，统计事件为「入园」且时间在 [14:00, 16:00) 的行，共 %d 次；出园行不计。终答一句话写明时间段和人次。判据：第 1 轮零调用并问到时间段；第 2 轮包含 %d。

## Why the answer is unique
时间窗在第 2 轮给定为左闭右开 [14:00, 16:00)，事件字段固定，入园计数唯一；出园行是干扰但不属于入园。
''' % (target_n, target_n),
)

# ---------------------------------------------------------------- log-8045
msg_pool = {
    "午睡": ["孩子午睡容易踢被子，麻烦老师留意", "想问问午睡时间多长，要不要带小毯子",
             "孩子说午睡时旁边太吵，能调下床位吗", "午睡起床后嗓子有点哑，请多观察",
             "孩子今天没午睡，晚上可能早接", "能不能把午睡的小被子每周晒一次"],
    "过敏": ["孩子对芒果过敏，加餐请避开", "花粉季孩子过敏，户外活动后请洗脸",
             "孩子对乳胶过敏，请别用乳胶手套碰他的餐具", "新来的保育员请留意孩子海鲜过敏"],
    "接送": ["今天爷爷奶奶代接，密码是后四位", "下周三我出差，改成爸爸接",
             "接送卡丢了，麻烦补办一张", "今天晚点接，大概六点半到", "以后固定姥姥接，照片已发班级群"],
    "加餐": ["孩子不吃甜的，加餐能换水果吗", "孩子乳糖不耐受，鲜奶换酸奶",
             "加餐的软面包有全麦的吗"],
}
talk_lines = []
t = 9 * 3600
for topic, msgs in msg_pool.items():
    for msg in msgs:
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        day = 13 + (1 if h >= 14 else 0) + (1 if h >= 19 else 0)
        hh = (h % 14) + 9 if h >= 14 else h
        talk_lines.append("2026-10-%02d %02d:%02d:%02d 家长=小核桃妈妈 留言=%s" % (day, hh, m, s, msg))
        t += 1500 + (len(talk_lines) * 137) % 2500
random.Random(80452).shuffle(talk_lines)
talkf = "\n".join(talk_lines) + "\n"
write_case(
    "log-8045",
    desc="Turn 1 asks how many parent messages mention a topic but the search word is undecided; the assistant must ask first without tools; turn 2 gives the word",
    task_type="count_events", family="fam-log-b10-napnotes-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "托管/日志/家长留言.log": talkf,
        "托管/说明.md": "家长留言日志每行一条，留言正文里会写主题，如饮食、睡眠、接送等。\n",
    },
    turns=[
        {"prompt": "帮我数家长留言里提到某个主题的有多少条，主题词我还没定——你先问我，别调工具。",
         "expect": dict(NOCALL, output_contains_any=["哪个词", "哪个关键词", "哪个主题", "搜什么", "主题词是什么", "关键词是什么", "什么主题词"], max_output_chars=300)},
        {"prompt": "数提到「午睡」的留言。",
         "expect": {"output_contains": ["6"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["托管/日志/家长留言.log"].splitlines():
    assert re.match(r"^2026-10-1[3-5] \\d\\d:\\d\\d:\\d\\d 家长=\\S+ 留言=\\S+$", line), line
assert "主题" in f["托管/说明.md"]
kw = case["turns"][1]["prompt"].split("「")[1].split("」")[0]
assert kw
n = sum(1 for line in f["托管/日志/家长留言.log"].splitlines() if kw in line.split("留言=")[1])
ask = ["哪个词", "哪个关键词", "哪个主题", "搜什么", "主题词是什么", "关键词是什么", "什么主题词"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问主题词、不调用工具；第 2 轮给出关键词后正常计数。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要搜哪个主题词？请给我关键词。」
第 2 轮：读 托管/日志/家长留言.log，统计 留言 正文里出现「午睡」的行，共 6 条。终答一句话写明关键词和条数。判据：第 1 轮零调用并问到关键词；第 2 轮包含 6。

## Why the answer is unique
关键词在第 2 轮给定为「午睡」；正文按主题分组书写、互不混词，出现「午睡」的留言恰 6 条。
''',
)

# ---------------------------------------------------------------- log-8046
rng = random.Random(80462)
lesson_log = []
t = 9 * 3600
for coach, n in (("沈教练", 5), ("钱教练", 6), ("蒋教练", 4)):
    for _ in range(n):
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        lesson_log.append("2026-10-08 %02d:%02d:%02d %s %s %d组" % (
            h, m, s, coach, rng.choice(["亲子班", "幼儿班", "学龄班"]), rng.randint(2, 6)))
        t += 1200 + (len(lesson_log) * 97) % 1400
random.Random(80463).shuffle(lesson_log)
lessonf = "\n".join(lesson_log) + "\n"
write_case(
    "log-8046",
    desc="Turn 1 asks how many classes a coach taught but the coach is undecided; the assistant must ask first without tools; turn 2 names the coach",
    task_type="count_events", family="fam-log-b10-coachload-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "游泳馆/日志/上课-2026-10-08.log": lessonf,
        "游泳馆/说明.md": "上课日志每行一节课，字段：日期 时间 教练 班型 组数。\n",
    },
    turns=[
        {"prompt": "帮我数某位教练 10 月 8 日当天带课的节数，具体哪位教练我来定——你先问我，别调工具。",
         "expect": dict(NOCALL, output_contains_any=["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"], max_output_chars=300)},
        {"prompt": "数 沈教练 的带课数。",
         "expect": {"output_contains": ["5"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for line in f["游泳馆/日志/上课-2026-10-08.log"].splitlines():
    assert re.match(r"^2026-10-08 \\d\\d:\\d\\d:\\d\\d \\S+教练 (亲子班|幼儿班|学龄班) \\d+组$", line), line
assert "教练 班型" in f["游泳馆/说明.md"]
coaches = sorted({l.split()[2] for l in f["游泳馆/日志/上课-2026-10-08.log"].splitlines()})
chosen = [c for c in coaches if c in case["turns"][1]["prompt"]]
assert len(chosen) == 1, chosen
n = sum(1 for l in f["游泳馆/日志/上课-2026-10-08.log"].splitlines() if chosen[0] in l)
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问哪位教练、不调用工具；第 2 轮点名教练后正常计数。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要数哪位教练的课？请告诉我教练名字。」
第 2 轮：读 游泳馆/日志/上课-2026-10-08.log，统计 教练 列为沈教练的行，共 5 节。终答一句话写明教练和节数。判据：第 1 轮零调用并问到哪位教练；第 2 轮包含 5。

## Why the answer is unique
教练列只有沈、钱、蒋三位，第 2 轮指定沈教练；当天每位教练的行数互不相同，计数唯一。
''',
)

# ---------------------------------------------------------------- log-8047
rng = random.Random(80472)
users = ["maya.chen", "liam.ortiz", "ava.brooks", "noah.kim", "sofia.reyes", "ethan.park"]


def signin_log(day, n_ok, n_fail):
    lines = []
    t = 9 * 3600
    for i in range(n_ok + n_fail):
        h, rem = divmod(t, 3600)
        m, s = divmod(rem, 60)
        fail = i >= n_ok
        lines.append("2026-10-%s %02d:%02d:%02d user=%s room=%s result=%s" % (
            day, h, m, s, rng.choice(users), rng.choice("ABC"), "FAILED" if fail else "OK"))
        t += 400 + (i * 83) % 1600
    random.Random(80473).shuffle(lines)
    return "\n".join(lines) + "\n"


printf = "\n".join("2026-10-07 10:%02d:02 printer=hp-3 job=%d status=DONE" % (i, 400 + i)
                   for i in range(5)) + "\n"
write_case(
    "log-8047",
    desc="Turn 1 asks for a failed-sign-in count but the user will say which log to read; the assistant must ask first without tools; turn 2 names the file",
    task_type="count_events", family="fam-log-b10-signinfail-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "tutoring/logs/signin-2026-10-06.log": signin_log("06", 16, 4),
        "tutoring/logs/signin-2026-10-07.log": signin_log("07", 16, 8),
        "tutoring/logs/printing.log": printf,
        "README.md": "BrightPath Tutoring Center logs. Sign-in logs record one front-desk attempt per line; printing logs are separate.\n",
    },
    turns=[
        {"prompt": "I need the number of failed sign-ins from one of our logs, and I'll say which one. Ask me first and don't look anything up.",
         "expect": dict(NOCALL, output_contains_any=["which log", "which file", "which one", "which date", "Which log", "Which file", "log file path"], max_output_chars=300)},
        {"prompt": "Count FAILED lines in tutoring/logs/signin-2026-10-07.log.",
         "expect": {"output_contains": ["8"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    if "signin" in path:
        for line in f[path].splitlines():
            assert re.match(r"^2026-10-0[67] \\d\\d:\\d\\d:\\d\\d user=[a-z.]+ room=[ABC] result=(OK|FAILED)$", line), line
assert "BrightPath Tutoring Center" in f["README.md"]
prompt = case["turns"][1]["prompt"]
chosen = [p for p in f if p.endswith(".log") and p in prompt]
assert len(chosen) == 1, chosen
n = sum(1 for line in f[chosen[0]].splitlines() if "result=FAILED" in line)
ask = ["which log", "which file", "which one", "which date", "Which log", "Which file", "log file path"]
print(json.dumps({"expected_number": n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. Turn 1 asks the assistant to wait for the log choice.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which log should I check?"
Turn 2: read tutoring/logs/signin-2026-10-07.log and count lines with result=FAILED: 8. Final answer in one sentence naming the log and the count. Criteria: turn 1 zero-call and asks which log; turn 2 contains 8.

## Why the answer is unique
Turn 2 fixes the file; the Oct 7 sign-in log holds exactly 8 FAILED lines, the Oct 6 log has 4, and the printing log has none.
''',
)

# ---------------------------------------------------------------- cfg-8050
write_case(
    "cfg-8050",
    desc="Turn 1 asks to review the card-reader settings but the config directory is unstated; the assistant must ask first; turn 2 gives the path",
    task_type="read_effective", family="fam-cfg-b10-doorreader-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "配置/门禁/读卡器.yaml": "读卡器:\n  开门延时秒: 5\n  刷卡重试上限: 3\n  静音模式: 否\n",
        "配置/温控/教室空调.yaml": "空调:\n  夏季制冷温度: 26\n  冬季制热温度: 20\n",
        "配置/消毒/消毒周期.yaml": "消毒:\n  玩具消毒间隔天: 2\n  口杯消毒间隔天: 1\n",
        "README.md": "各子系统配置分目录存放：门禁、温控、消毒；改动后由保育主任复核。\n",
    },
    turns=[
        {"prompt": "帮我核对园里读卡器的配置项，但配置文件放在哪个目录我没说过——你先问我，别自己去翻。",
         "expect": dict(NOCALL, output_contains_any=["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"], max_output_chars=300)},
        {"prompt": "配置在 配置/门禁/读卡器.yaml。",
         "expect": {"output_contains": ["5"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("各子系统配置")
assert f["配置/门禁/读卡器.yaml"].startswith("读卡器:")
m = re.search(r"开门延时秒:\\s*(\\d+)", f["配置/门禁/读卡器.yaml"])
assert m
assert re.search(r"夏季制冷温度:\\s*(\\d+)", f["配置/温控/教室空调.yaml"])
assert re.search(r"玩具消毒间隔天:\\s*(\\d+)", f["配置/消毒/消毒周期.yaml"])
ask = ["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"]
print(json.dumps({"expected_number": int(m.group(1)), "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问配置文件位置、不翻文件；第 2 轮给出路径后正常读取。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「读卡器配置放在哪个目录？请给我路径。」
第 2 轮：读 配置/门禁/读卡器.yaml，报 开门延时秒 5（可带一句刷卡重试上限 3）。终答一句话写明配置项和取值。判据：第 1 轮零调用并问到路径；第 2 轮包含 5。

## Why the answer is unique
第 2 轮指定了门禁配置文件；开门延时秒在该文件中只出现一次，取值唯一，温控、消毒是别的子系统。
''',
)

# ---------------------------------------------------------------- cfg-8051
rooms = {"maple": ("Maple", 12, "1"), "willow": ("Willow", 8, "2"), "cedar": ("Cedar", 10, "1")}
room_files = {"config/rooms/%s.yaml" % key: "room: %s\nfloor: %s\ncapacity: %d\nwhiteboard: yes\n" % (nm, fl, cap)
              for key, (nm, cap, fl) in rooms.items()}
room_files["README.md"] = "Room capacity caps are set per room in config/rooms/<room>.yaml; floor plans are posted at the front desk.\n"
write_case(
    "cfg-8051",
    desc="Turn 1 asks for class-size caps of two rooms but the user will name the rooms; the assistant must ask first; turn 2 names Maple and Willow",
    task_type="read_effective", family="fam-cfg-b10-roomcaps-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=room_files,
    turns=[
        {"prompt": "I need the class-size caps for two of our rooms. I'll name the rooms; ask me first and don't look anything up.",
         "expect": dict(NOCALL, output_contains_any=["which two", "Which two", "which room", "Which room", "name the two rooms", "room names", "the two rooms"], max_output_chars=300)},
        {"prompt": "Maple and Willow.",
         "expect": {"output_contains": ["12", "8"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("Room capacity caps")
sizes = {}
for room in ("maple", "willow", "cedar"):
    m = re.search(r"capacity: (\\d+)", f["config/rooms/%s.yaml" % room])
    assert m, room
    sizes[room] = int(m.group(1))
ask = ["which two", "Which two", "which room", "Which room", "name the two rooms", "room names", "the two rooms"]
print(json.dumps({"expected_number": sizes["maple"], "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. Turn 1 asks the assistant to wait for the room names.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two rooms should I look up?"
Turn 2: read config/rooms/maple.yaml and config/rooms/willow.yaml: capacity 12 and 8. Final answer in one sentence: Maple caps at 12 children and Willow at 8. Criteria: turn 1 zero-call and asks which rooms; turn 2 contains 12 and 8 as whole tokens.

## Why the answer is unique
Each room file sets capacity explicitly, so the values are 12 (Maple) and 8 (Willow); Cedar is out of scope.
''',
)

# ---------------------------------------------------------------- cfg-8052
pumps = {"1号泵": (22, "1.5"), "2号泵": (18, "1.1"), "3号泵": (26, "2.2")}
pump_files = {"配置/循环泵/%s.yaml" % k: "循环泵:\n  流量立方米每小时: %d\n  额定功率千瓦: %s\n" % v
              for k, v in pumps.items()}
pump_files["配置/说明.md"] = "循环泵参数逐台单列，改动后需当班技师复核。\n"
write_case(
    "cfg-8052",
    desc="Turn 1 asks to check running parameters of two circulation pumps but the user will pick which two; the assistant must ask first; turn 2 names pumps 2 and 3",
    task_type="read_effective", family="fam-cfg-b10-pumpcheck-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=pump_files,
    turns=[
        {"prompt": "我要核对两台循环泵的运行参数，具体哪两台我来指定——你先问我，别翻泵的配置。",
         "expect": dict(NOCALL, output_contains_any=["哪两台", "哪几台", "哪两台泵", "哪几台泵", "位号", "设备编号", "泵编号", "泵的编号"], max_output_chars=300)},
        {"prompt": "核对 2 号泵和 3 号泵。",
         "expect": {"output_contains": ["18", "26"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["配置/说明.md"].startswith("循环泵参数")
flows = {}
for pump in ("1号泵", "2号泵", "3号泵"):
    m = re.search(r"流量立方米每小时:\\s*(\\d+)", f["配置/循环泵/%s.yaml" % pump])
    assert m, pump
    flows[pump] = int(m.group(1))
ask = ["哪两台", "哪几台", "哪两台泵", "哪几台泵", "位号", "设备编号", "泵编号", "泵的编号"]
print(json.dumps({"expected_number": flows["2号泵"], "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问核对哪两台泵、不翻配置；第 2 轮点名后正常读取。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要核对哪两台泵？请告诉我泵的编号。」
第 2 轮：读 配置/循环泵/2号泵.yaml 和 3号泵.yaml，流量分别为 18 和 26 立方米每小时。终答一句话写明两台泵的流量。判据：第 1 轮零调用并问到哪两台；第 2 轮包含 18 和 26。

## Why the answer is unique
各泵参数逐台单列，2 号泵流量 18、3 号泵 26 唯一确定，1 号泵不在范围内。
''',
)

# ---------------------------------------------------------------- cfg-8053
tickets = {"工作日日场": 88, "周末日场": 128, "夜场": 108}
ticket_files = {"配置/票价/%s.yaml" % k: "票价:\n  票价元: %d\n  含成人: 1\n" % v
                for k, v in tickets.items()}
ticket_files["配置/说明.md"] = "票价按场次分档配置，旺季调价走另一份审批单。\n"
write_case(
    "cfg-8053",
    desc="Turn 1 asks to check ticket prices of two sessions but the user will pick which two; the assistant must ask first; turn 2 names weekday-day and night",
    task_type="read_effective", family="fam-cfg-b10-tickettier-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=ticket_files,
    turns=[
        {"prompt": "我要核对两个场次的票价配置，具体哪两个场次我来定——你先问我，别翻票价配置。",
         "expect": dict(NOCALL, output_contains_any=["哪两个场次", "哪几个场次", "哪两场", "哪些场次", "场次的名称", "场次名称", "场次编号"], max_output_chars=300)},
        {"prompt": "工作日日场和夜场。",
         "expect": {"output_contains": ["88", "108"], "output_contains_token": True, "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["配置/说明.md"].startswith("票价按场次")
prices = {}
for tier in ("工作日日场", "周末日场", "夜场"):
    m = re.search(r"票价元:\\s*(\\d+)", f["配置/票价/%s.yaml" % tier])
    assert m, tier
    prices[tier] = int(m.group(1))
chosen = [t for t in ("工作日日场", "周末日场", "夜场") if t in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
ask = ["哪两个场次", "哪几个场次", "哪两场", "哪些场次", "场次的名称", "场次名称", "场次编号"]
print(json.dumps({"expected_number": prices["工作日日场"], "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问核对哪两个场次、不翻配置；第 2 轮点名后正常读取。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要核对哪两个场次？请告诉我场次名。」
第 2 轮：读 配置/票价/工作日日场.yaml 和 夜场.yaml，票价分别为 88 元和 108 元。终答一句话写明两个场次的票价。判据：第 1 轮零调用并问到哪两个场次；第 2 轮包含 88 和 108。

## Why the answer is unique
票价按场次分档、逐档单列，工作日日场 88、夜场 108 唯一确定，周末日场不在范围内。
''',
)

# ---------------------------------------------------------------- fs-8029
write_case(
    "fs-8029",
    desc="Turn 1 asks for the health-check notice text but its directory is unstated; the assistant must ask first; turn 2 gives the directory",
    task_type="find_file", family="fam-fs-b10-healthnotice-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={
        "README.md": "园务通知按分类存放在 通知/ 下的子目录，目录名即分类。\n",
        "通知/伙食/十月带量食谱.md": "十月带量食谱\n\n第一周主食为软米饭，配菜每日更新，见带量表。\n",
        "通知/活动/秋游安排.md": "秋游安排\n\n全园秋游定在 10 月 16 日，地点植物园，请穿园服。\n",
        "通知/体检/秋季体检安排.md": "秋季体检安排\n\n全园体检定在 10 月 21 日（周三）上午，地点妇幼保健院二楼，按班级分批进行。\n",
    },
    turns=[
        {"prompt": "帮我找秋季体检安排的通知原文，具体放在哪个目录我没说过——你先问我，别自己去翻。",
         "expect": dict(NOCALL, output_contains_any=["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"], max_output_chars=300)},
        {"prompt": "在 通知/体检/ 这个目录里。",
         "expect": {"output_contains_any": ["10 月 21 日", "10月21日", "2026-10-21"], "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
assert f["README.md"].startswith("园务通知")
assert f["通知/伙食/十月带量食谱.md"].startswith("十月带量食谱")
assert f["通知/活动/秋游安排.md"].startswith("秋游安排")
assert f["通知/体检/秋季体检安排.md"].startswith("秋季体检安排")
m = re.search(r"(\\d+)\\s*月\\s*(\\d+)\\s*日", f["通知/体检/秋季体检安排.md"])
assert m and m.group(1) == "10"
d = "10 月 %s 日" % m.group(2)
ask = ["哪个目录", "哪条路径", "哪个路径", "放在哪", "目录路径", "所在的目录", "所在目录", "具体路径", "完整路径"]
print(json.dumps({"expected_contains_any": ask + [d, d.replace(" ", ""), "2026-10-%s" % m.group(2)]},
                 ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问通知放在哪个目录、不翻文件；第 2 轮给出目录后正常读取。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「体检通知放在哪个目录？请给我路径。」
第 2 轮：列出并读取 通知/体检/秋季体检安排.md，报体检时间为 10 月 21 日（周三）上午、地点妇幼保健院二楼。终答一两句话概括。判据：第 1 轮零调用并问到目录；第 2 轮包含 10 月 21 日（写法不限）。

## Why the answer is unique
目录在第 2 轮指定为 通知/体检/；体检文件里日期只出现一次，伙食、活动是别的分类。
''',
)

# ---------------------------------------------------------------- fs-8030
duty = {
    "2026-08值班表.md": ("八月教练值班表", ["8 月 3 日（周一）10:00 亲子班 钱教练",
                                          "8 月 8 日（周六）15:00 学龄班 沈教练",
                                          "8 月 15 日（周六）10:00 亲子班 蒋教练",
                                          "8 月 24 日（周一）10:00 亲子班 钱教练"]),
    "2026-09值班表.md": ("九月教练值班表", ["9 月 2 日（周三）09:00 幼儿班 钱教练",
                                          "9 月 4 日（周五）10:00 亲子班 蒋教练",
                                          "9 月 7 日（周一）10:00 亲子班 沈教练",
                                          "9 月 11 日（周五）09:30 幼儿班 钱教练",
                                          "9 月 14 日（周一）10:00 亲子班 沈教练",
                                          "9 月 21 日（周一）15:00 学龄班 沈教练",
                                          "9 月 26 日（周六）10:00 亲子班 钱教练"]),
    "2026-10值班表.md": ("十月教练值班表", ["10 月 5 日（周一）10:00 亲子班 蒋教练",
                                           "10 月 10 日（周六）09:30 幼儿班 钱教练",
                                           "10 月 12 日（周一）10:00 亲子班 沈教练"]),
}
write_case(
    "fs-8030",
    desc="Turn 1 asks what class a coach covers but the coach is undecided; the assistant must ask first; turn 2 names the coach and the date",
    task_type="find_file", family="fam-fs-b10-coachduty-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={("游泳馆/排班/" + p): title + "\n\n" + "\n".join(rows) + "\n" for p, (title, rows) in duty.items()},
    turns=[
        {"prompt": "我要查一位教练的代班安排，具体查哪位教练我还没定——你先问我，别去翻排班表。",
         "expect": dict(NOCALL, output_contains_any=["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"], max_output_chars=300)},
        {"prompt": "查 沈教练 的，他 9 月 7 日那天带哪一班？",
         "expect": {"output_contains": ["亲子班"], "output_contains_any": ["10:00", "10 点"], "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
for path in f:
    assert f[path].splitlines()[0].endswith("值班表"), path
row = [l for l in f["游泳馆/排班/2026-09值班表.md"].splitlines() if "9 月 7 日" in l and "沈教练" in l]
assert len(row) == 1, row
m = re.search(r"日（周[一二三四五六日]）\\s*(\\d{2}:\\d{2})\\s*(\\S+)\\s*沈教练", row[0])
assert m and m.group(1) == "10:00" and m.group(2) == "亲子班", row[0]
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_contains_any": ask + ["10:00", "10 点"]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问查哪位教练、不翻排班表；第 2 轮点名教练和日期后正常查询。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要查哪位教练？请告诉我教练名字。」
第 2 轮：读 游泳馆/排班/2026-09值班表.md，9 月 7 日（周一）10:00 是沈教练的 亲子班。终答一句话写明班型和时段。判据：第 1 轮零调用并问到哪位教练；第 2 轮包含 亲子班 和 10:00。

## Why the answer is unique
第 2 轮同时锁定教练与日期，9 月值班表中 9 月 7 日只有一行且教练为沈教练，班型与时段唯一。
''',
)

# ---------------------------------------------------------------- fs-8031
book_dates = {"小班": "2026-10-09", "中班": "2026-10-11", "大班": "2026-10-10", "托班": "2026-10-13"}
write_case(
    "fs-8031",
    desc="Turn 1 asks which class updated its home-contact book later but the two classes are undecided; the assistant must ask first; turn 2 names them",
    task_type="find_file", family="fam-fs-b10-contactbook-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={("家园/联系册/%s-十月.md" % cls): "%s家园联系册（十月）\n\n最后更新：%s\n\n本月重点：如厕与自理练习，家长可在周五前反馈。\n" % (cls, d)
           for cls, d in book_dates.items()},
    turns=[
        {"prompt": "我要核对两个班的家园联系册更新情况，具体哪两个班我来定——你先问我，别自己翻。",
         "expect": dict(NOCALL, output_contains_any=["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"], max_output_chars=300)},
        {"prompt": "核对 中班 和 托班 这两个班，哪一个更新得更晚？",
         "expect": {"output_contains": ["托班"], "output_contains_any": ["10 月 13 日", "10月13日", "10-13", "2026-10-13"], "required_tools": ["read_file"], "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
f = case["files"]
classes = ["小班", "中班", "大班", "托班"]
dates = {}
for cls in classes:
    body = f["家园/联系册/%s-十月.md" % cls]
    assert body.splitlines()[0].startswith(cls), cls
    m = re.search(r"最后更新：(\\d{4}-\\d{2}-\\d{2})", body)
    assert m, cls
    dates[cls] = m.group(1)
chosen = [c for c in classes if c in case["turns"][1]["prompt"]]
assert len(chosen) == 2, chosen
assert len(set(dates.values())) == 4, dates
latest = max(chosen, key=lambda c: dates[c])
assert latest == "托班" and dates[latest] == "2026-10-13", (latest, dates)
d = dates[latest]
parts = d.split("-")
ask = ["哪两个班", "哪几个班", "哪两个班级", "哪些班", "班级名称", "班的名称", "班级编号"]
print(json.dumps({"expected_contains_any": ask +
                  ["%s 月 %s 日" % (int(parts[1]), int(parts[2])),
                   "%s月%s日" % (int(parts[1]), int(parts[2])), d,
                   "%s-%s" % (parts[1], parts[2])]}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 第 1 轮用户要求先问核对哪两个班、不翻文件；第 2 轮点名后正常比较。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要核对哪两个班？请告诉我班名。」
第 2 轮：读 中班 和 托班 的联系册，最后更新分别为 2026-10-11 和 2026-10-13，托班 更晚。终答一句话写明班名和日期。判据：第 1 轮零调用并问到哪两个班；第 2 轮包含 托班 和 10 月 13 日（写法不限）。

## Why the answer is unique
第 2 轮锁定两个班；各自「最后更新」日期唯一，托班 10-13 晚于中班 10-11，比较结果唯一。
''',
)

# ---------------------------------------------------------------- fs-8032
handouts = {
    "math": ["algebra-drills.md", "fractions-basics.md", "word-problems.md"],
    "reading": ["phonics-set-a.md", "comprehension-checks.md"],
    "writing": ["essay-outline.md", "paragraph-editing.md"],
}
handout_files = {"tutoring/README.md": "BrightPath Tutoring Center. Handouts live under tutoring/handouts/<subject>/; each file is one printable handout.\n"}
for subj, names in handouts.items():
    for nm in names:
        handout_files["tutoring/handouts/%s/%s" % (subj, nm)] = (
            "%s handout: %s\nWork through the examples before class.\n"
            % (subj.title(), nm.replace("-", " ").replace(".md", "")))
write_case(
    "fs-8032",
    desc="Turn 1 asks how many handout files two subjects have but the subjects are undecided; the assistant must ask first; turn 2 names math and writing",
    task_type="count_by_type", family="fam-fs-b10-handoutcount-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files=handout_files,
    turns=[
        {"prompt": "I need the number of handout files for a couple of subjects. I'll pick the subjects; ask me first and don't look anything up.",
         "expect": dict(NOCALL, output_contains_any=["which subjects", "Which subjects", "which two", "which folders", "name the subjects", "subjects you want", "Which two"], max_output_chars=300)},
        {"prompt": "Math and writing, please.",
         "expect": {"output_contains": ["3", "2"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json

case = json.load(open("case.json"))
f = case["files"]
assert f["tutoring/README.md"].startswith("BrightPath Tutoring Center")
counts = {}
for subj in ("math", "reading", "writing"):
    counts[subj] = len([p for p in f if p.startswith("tutoring/handouts/%s/" % subj) and p.endswith(".md")])
assert counts == {"math": 3, "reading": 2, "writing": 2}, counts
prompt = case["turns"][1]["prompt"].lower()
chosen = [s for s in ("math", "reading", "writing") if s in prompt]
assert len(chosen) == 2, chosen
ask = ["which subjects", "Which subjects", "which two", "which folders", "name the subjects", "subjects you want", "Which two"]
print(json.dumps({"expected_number": counts[chosen[0]], "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. Turn 1 asks the assistant to wait for the subject choice.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which subjects' handout folders should I count?"
Turn 2: list tutoring/handouts/math/ and tutoring/handouts/writing/: math has 3 handout files and writing has 2. Final answer in one sentence. Criteria: turn 1 zero-call and asks which subjects; turn 2 contains 3 and 2 as whole tokens.

## Why the answer is unique
Turn 2 fixes the two folders; the file counts are 3 (math) and 2 (writing), and every handout file has a distinct non-empty name.
''',
)

# ---------------------------------------------------------------- nt-8041
write_case(
    "nt-8041",
    desc="Turn 1 asks for a weekly snack order total but the week is undecided; the assistant must ask first without calling any tool; turn 2 gives the week and the headcount",
    task_type="unit_convert", family="fam-nt-b10-snackweek-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={},
    turns=[
        {"prompt": "帮我算托管班某一周的加餐采购总量，具体算哪一周我还没定——你先问我，别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["哪一周", "哪周", "哪几天", "时间范围", "起止日期", "日期范围"], max_output_chars=300)},
        {"prompt": "算 10 月 12 日到 10 月 16 日那一周，在册孩子 45 人，每人每天一份加餐。",
         "expect": {"output_contains": ["225"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
days = re.findall(r"(\\d+)\\s*月\\s*(\\d+)\\s*日", p)
assert len(days) == 2, days
d1, d2 = sorted(int(x[1]) for x in days)
per_head = int(re.search(r"(\\d+)\\s*人", p).group(1))
assert per_head == 45, per_head
ask = ["哪一周", "哪周", "哪几天", "时间范围", "起止日期", "日期范围"]
print(json.dumps({"expected_number": per_head * (d2 - d1 + 1), "expected_contains_any": ask},
                 ensure_ascii=False))
''',
    notes='''
## Traps
- None. 工作区为空，第 1 轮用户要求先问算哪一周、不调用工具；第 2 轮给出周次和人数后口算完成。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要算哪一周？请给我起止日期。」
第 2 轮：10 月 12 日到 16 日共 5 天，45 人每天一份，合计 45 × 5 = 225 份。终答一句话写出算式和结果。判据：第 1 轮零调用并问到周次；第 2 轮包含 225。

## Why the answer is unique
天数由两端日期唯一确定（含首尾 5 天），人数 45 在题面给定，乘积唯一。
''',
)

# ---------------------------------------------------------------- nt-8042
write_case(
    "nt-8042",
    desc="Turn 1 asks for a combined renewal total but the families are undecided; the assistant must ask first without calling any tool; turn 2 names two families with amounts",
    task_type="unit_convert", family="fam-nt-b10-renewfams-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={},
    turns=[
        {"prompt": "帮我合计其中几个家庭的续费金额，具体哪几个家庭我还没说——你先问我，别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["哪几个家庭", "哪几家", "哪几户", "哪几个会员家庭", "哪些家庭", "家庭名称", "家庭编号"], max_output_chars=300)},
        {"prompt": "就合计 周家 2600 元和 吴家 1800 元 这两家。",
         "expect": {"output_contains": ["4400"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
amounts = [int(x) for x in re.findall(r"(\\d+)\\s*元", p)]
assert len(amounts) == 2, amounts
ask = ["哪几个家庭", "哪几家", "哪几户", "哪几个会员家庭", "哪些家庭", "家庭名称", "家庭编号"]
print(json.dumps({"expected_number": sum(amounts), "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 工作区为空，第 1 轮用户要求先问合计哪几家、不调用工具；第 2 轮给出两家金额后口算完成。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要合计哪几个家庭？请告诉我哪几家。」
第 2 轮：周家 2600 元 + 吴家 1800 元 = 4400 元。终答一句话写出算式和结果。判据：第 1 轮零调用并问到哪几家；第 2 轮包含 4400。

## Why the answer is unique
第 2 轮只给两笔金额，加法结果唯一，且 4400 不与题面里任何数字重合。
''',
)

# ---------------------------------------------------------------- nt-8043
write_case(
    "nt-8043",
    desc="Turn 1 asks for a late-care surcharge but the time window is undecided; the assistant must ask first without calling any tool; turn 2 gives the window and the rate",
    task_type="unit_convert", family="fam-nt-b10-latecare-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={},
    turns=[
        {"prompt": "帮我算某个时段的晚托加时看护费，具体哪个时段我还没定——你先问我，别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["哪个时段", "几点到几点", "哪段时间", "时间段", "具体时段", "起止时间"], max_output_chars=300)},
        {"prompt": "算下午 6 点到 7 点半，加时看护每半小时收 20 元。",
         "expect": {"output_contains": ["60"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
m = re.search(r"(\\d+)\\s*点到\\s*(\\d+)\\s*点半", p)
assert m, p
rate = int(re.search(r"每半小时收\\s*(\\d+)\\s*元", p).group(1))
units = (int(m.group(2)) + 0.5 - int(m.group(1))) * 2
assert units == int(units)
ask = ["哪个时段", "几点到几点", "哪段时间", "时间段", "具体时段", "起止时间"]
print(json.dumps({"expected_number": int(units) * rate, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 工作区为空，第 1 轮用户要求先问算哪个时段、不调用工具；第 2 轮给出时段和费率后口算完成。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要算哪个时段？请告诉我几点到几点。」
第 2 轮：下午 6 点到 7 点半共 1.5 小时，即 3 个半小时，3 × 20 = 60 元。终答一句话写出算式和结果。判据：第 1 轮零调用并问到时段；第 2 轮包含 60。

## Why the answer is unique
时段在第 2 轮给定为 18:00–19:30，时长 1.5 小时；按半小时计 3 段，费率 20 元唯一，结果 60 元唯一。
''',
)

# ---------------------------------------------------------------- nt-8044
write_case(
    "nt-8044",
    desc="Turn 1 asks for a two-package lesson total but the packages are undecided; the assistant must ask first without calling any tool; turn 2 gives both packages",
    task_type="unit_convert", family="fam-nt-b10-pkgquote-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={},
    turns=[
        {"prompt": "I need a total for two of our lesson packages, but I'll say which two. Ask me first and don't look anything up.",
         "expect": dict(NOCALL, output_contains_any=["which two", "Which two", "which packages", "which ones", "Which packages", "Which ones", "package names", "the two packages"], max_output_chars=300)},
        {"prompt": "The 8-session package at 45 dollars per session and the 4-session package at 50 dollars per session.",
         "expect": {"output_contains": ["560"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
sessions = [int(x) for x in re.findall(r"(\\d+)-session", p)]
rates = [int(x) for x in re.findall(r"(\\d+)\\s*dollars per session", p)]
assert len(sessions) == 2 and len(rates) == 2, (sessions, rates)
ask = ["which two", "Which two", "which packages", "which ones", "Which packages", "Which ones", "package names", "the two packages"]
print(json.dumps({"expected_number": sum(s * r for s, r in zip(sessions, rates)),
                  "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. No workspace; turn 1 asks the assistant to wait for the package choice.

## Reference solution
Turn 1, no tool call, one question naming the missing parameter: "Which two packages should I quote?"
Turn 2: 8 × 45 = 360 and 4 × 50 = 200, total 560 dollars. Final answer in one sentence with the arithmetic. Criteria: turn 1 zero-call and asks which packages; turn 2 contains 560.

## Why the answer is unique
Turn 2 fixes both sizes and per-session rates; the weighted sum 8×45 + 4×50 = 560 is unique.
''',
)

# ---------------------------------------------------------------- nt-8045
write_case(
    "nt-8045",
    desc="Turn 1 asks for a coach's private-lesson rate but the coach is undecided; the assistant must ask first without calling any tool; turn 2 names the coach and rate",
    task_type="unit_convert", family="fam-nt-b10-coachrate-01", level="L0", ref_calls=1,
    axes=["DEC"],
    files={},
    turns=[
        {"prompt": "帮我报某位教练的私教课单价，具体哪位教练我还没说——你先问我，别调用工具。",
         "expect": dict(NOCALL, output_contains_any=["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"], max_output_chars=300)},
        {"prompt": "沈教练的私教课，一节 320 元，我想给孩子约 3 节，一共多少钱？",
         "expect": {"output_contains": ["960"], "output_contains_token": True, "max_output_chars": 300}},
    ],
    verify='''
import json
import re

case = json.load(open("case.json"))
assert not case["files"]
p = case["turns"][1]["prompt"]
assert "沈教练" in p, p
m = re.search(r"一节\\s*(\\d+)\\s*元", p)
assert m, p
n = int(re.search(r"约\\s*(\\d+)\\s*节", p).group(1))
ask = ["哪位教练", "哪个教练", "哪位", "教练名字", "教练的姓名", "教练姓名", "教练的名字", "教练编号"]
print(json.dumps({"expected_number": int(m.group(1)) * n, "expected_contains_any": ask}, ensure_ascii=False))
''',
    notes='''
## Traps
- None. 工作区为空，第 1 轮用户要求先问报哪位教练、不调用工具；第 2 轮给出教练、单价和节数后口算完成。

## Reference solution
第 1 轮零调用，一句问句点名缺的参数：「要报哪位教练的私教课单价？请告诉我教练名字。」
第 2 轮：沈教练私教课一节 320 元，3 节共 320 × 3 = 960 元。终答一句话写出算式和结果。判据：第 1 轮零调用并问到哪位教练；第 2 轮包含 960。

## Why the answer is unique
教练在第 2 轮指定为沈教练，单价 320 元与节数 3 由题面给定，乘积唯一。
''',
)
