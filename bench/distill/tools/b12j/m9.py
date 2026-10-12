"""M9 (bash) batch b12j of v1.41: ids 9241-9260, aggregation and long-file lookups.

M9a (9241-9252): one scalar from a pipeline over several .txt/.dat tables, exact-match decoy, criterion in a README.
M9c (9253-9260): one long .txt/.dat file (700-1500 lines); count / max / line number via grep or awk.
Eight cases have two turns (9241-9245, 9253-9255): turn 2 asks for a different filter over the same data.
All cases share one engine: each case lists its table generator and queries; the verify script recomputes
every answer from the fixture, and the same predicates compute the decoys."""
import json
from random import Random

from common import has, lines, phrasings, thousands, verify_src, write_case

REFS = {}
SPEC = {}


def fmt(v):
    if isinstance(v, float):
        s = ("%.2f" % v).rstrip("0").rstrip(".")
        return s
    return str(v)


import re

_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def near_tokens(files, value):
    """Counts numeric tokens equal to value the way the gate's numberMatches scans them."""
    word = re.compile(r"[A-Za-z0-9_.]")
    hits = 0
    for text in files.values():
        for m in _NUM.finditer(text):
            if m.start() > 0 and word.match(text[m.start() - 1]):
                continue
            if m.end() < len(text) and word.match(text[m.end()]):
                continue
            hits += abs(float(m.group()) - value) <= 0.01
    return hits


def apply(kind, col, rows, pred):
    sel = [(n, r) for n, r in rows if eval(pred, {"int": int, "float": float}, {"r": r})]
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(r[col]) for _, r in sel)
    if kind == "max":
        return max(float(r[col]) for _, r in sel)
    if kind == "distinct":
        return len({r[col] for _, r in sel})
    if kind == "first_line":
        return min(n for n, _ in sel)
    if kind == "last_line":
        return max(n for n, _ in sel)
    raise ValueError(kind)


def make_files(c, rng):
    files, tables = {}, {}
    for fi, name in enumerate(c["names"]):
        n = rng.randint(*c["rows"])
        rows = [c["gen"](rng, i, fi, n) for i in range(n)]
        path = f"{c['root']}/{name}"
        body = ([c["sep"].join(c["cols"])] if c.get("header", True) else []) + [c["sep"].join(r) for r in rows]
        files[path] = lines(body)
        tables[path] = [(k + 1 + (1 if c.get("header", True) else 0), dict(zip(c["cols"], r))) for k, r in enumerate(rows)]
    return files, tables


def build(cid):
    c = CASES[cid]
    for attempt in range(600):
        rng = Random(int(cid.split("-")[1]) + attempt * 7919)
        files, tables = make_files(c, rng)
        files[f"{c['root']}/{c['readme_name']}"] = lines(c["readme"])
        allrows = [x for t in tables.values() for x in t]
        first_rows = next(iter(tables.values()))
        vals, decs, firsts = [], [], []
        try:
            for q in c["queries"]:
                vals.append(apply(q["agg"], q.get("col"), allrows, q["pred"]))
                decs.append(apply(q["agg"], q.get("col"), allrows, q["decoy"]))
                firsts.append(apply(q["agg"], q.get("col"), first_rows, q["pred"]))
        except ValueError:
            continue
        ok = all(fmt(v) != fmt(d) and fmt(v) not in fmt(d) for v, d in zip(vals, decs))
        ok = ok and len({fmt(v) for v in vals}) == len(vals) and all(v >= c.get("min", 5) for v in vals)
        if len(c["names"]) > 1 and c["queries"][-1]["agg"] in ("sum", "count"):
            ok = ok and firsts[-1] != vals[-1]
        if ok:
            lead = next((i for i, q in enumerate(c["queries"]) if q["agg"] != "sum"), None)
            if lead is not None:
                hits = near_tokens(files, float(vals[lead]))
                ok = hits == (1 if c["queries"][lead]["agg"] == "max" else 0)
        if ok:
            break
    else:
        raise SystemExit("%s: no seed found" % cid)
    readme_path = f"{c['root']}/{c['readme_name']}"
    data_paths = [f"{c['root']}/{n}" for n in c["names"]]
    qs = [(q["pred"], q["agg"], q.get("col")) for q in c["queries"]]
    body = f'''
SEP = {c["sep"]!r}
COLS = {c["cols"]!r}
HEADER = {c.get("header", True)!r}
DATA = {data_paths!r}
QS = {qs!r}
assert case["files"][{readme_path!r}].startswith({c["readme"][0]!r})

def table(path):
    out = []
    for n, line in enumerate(case["files"][path].splitlines(), 1):
        parts = line.split(SEP)
        if HEADER and n == 1:
            assert parts == COLS, path
            continue
        assert len(parts) == len(COLS), (path, n, line)
        out.append((n, dict(zip(COLS, parts))))
    return out

ALL = [x for p in DATA for x in table(p)]

def agg(kind, col, pred):
    sel = [(n, r) for n, r in ALL if eval(pred, {{"int": int, "float": float}}, {{"r": r}})]
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(r[col]) for _, r in sel)
    if kind == "max":
        return max(float(r[col]) for _, r in sel)
    if kind == "distinct":
        return len({{r[col] for _, r in sel}})
    if kind == "first_line":
        return min(n for n, _ in sel)
    return max(n for n, _ in sel)

vals = [agg(k, col, p) for p, k, col in QS]
out = {{}}
anyv = []
for (p, k, col), val in zip(QS, vals):
    if k == "sum":
        anyv += [str(val)] + ([format(val, ",")] if val >= 1000 else [])
if anyv:
    out["expected_contains_any"] = anyv
nums = [val for (p, k, col), val in zip(QS, vals) if k != "sum"]
if nums:
    v = nums[-1]
    out["expected_number"] = int(v) if isinstance(v, float) and v == int(v) else v
print(json.dumps(out))
'''
    commands = [q["cmd"] for q in c["queries"]]
    size = sum(len(t.encode()) for p, t in files.items() if p in data_paths)
    nrows = sum(len(t) for t in tables.values())
    trap_lines = []
    for i, q in enumerate(c["queries"], 1):
        trap_lines.append(f"- Turn {i}: exact answer {fmt(vals[i-1])}; the loose match ({q['decoy_note']}) gives {fmt(decs[i-1])}."
                          if len(c["queries"]) > 1 else
                          f"- TR-DECOY: exact answer {fmt(vals[i-1])}; the loose match ({q['decoy_note']}) gives {fmt(decs[i-1])}.")
    multi = len(c["names"]) > 1
    long_file = c["sub"] == "M9c"
    notes = "## Traps\n" + "\n".join(trap_lines) + "\n"
    if multi:
        notes += f"- TR-MULTISRC: {len(c['names'])} files; the first file alone gives {fmt(firsts[-1])}.\n"
    if long_file:
        notes += f"- TR-TRUNC: the file is {size // 1024}KB and {nrows} data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.\n"
    if len(c["queries"]) > 1:
        notes += "- Turn 2 needs a different filter over the same data, so turn 1's number is the wrong answer.\n"
    notes += "\n## Reference solution\n"
    for i, q in enumerate(c["queries"], 1):
        notes += f"Turn {i}: bash: `{q['cmd']}` -> {fmt(vals[i-1])}\n"
    notes += f"""Final answer: {c['queries'][-1]['unit'].format(v=fmt(vals[-1]))}

## Why the answer is unique
{c['why']} The README ({readme_path}) fixes the rule; the answer is a single number.
""" + phrasings(*c["queries"][-1]["alts"])
    REFS[cid] = (files, commands, has(fmt(vals[-1])))
    SPEC[cid] = dict(kind="bash_aggregate", sub=c["sub"], needs=[readme_path])
    turns = []
    for q, v in zip(c["queries"], vals):
        want = thousands(fmt(v)) if q["agg"] == "sum" else [fmt(v)]
        exp = {"output_contains_any": want, "max_output_chars": 600} if len(want) > 1 else {"output_contains": want, "max_output_chars": 600}
        turns.append({"prompt": q["prompt"], "expect": exp})
    scen = cid.split("-")[0]
    if scen == "tab":
        task_type = "filter_count" if c["queries"][-1]["agg"] == "count" else "aggregate"
    else:
        task_type = "locate_error" if any(q["agg"].endswith("_line") for q in c["queries"]) else "count_events"
    traps = ["TR-DECOY"] + (["TR-MULTISRC"] if multi else []) + (["TR-TRUNC"] if long_file else [])
    decoys = {"TR-DECOY": fmt(decs[-1])}
    if multi:
        decoys["TR-MULTISRC"] = fmt(firsts[-1])
    if long_file:
        cut, used = 0, 0
        for n, line in enumerate(files[data_paths[0]].splitlines(True), 1):
            used += len(line.encode())
            if used > 64 * 1024:
                break
            cut = n
        view = [(n, r) for n, r in tables[data_paths[0]] if n <= cut]
        try:
            seen = fmt(apply(c["queries"][-1]["agg"], c["queries"][-1].get("col"), view, c["queries"][-1]["pred"]))
        except ValueError:
            seen = "0"
        decoys["TR-TRUNC"] = seen if seen != fmt(vals[-1]) else fmt(decs[-1])
    return write_case(
        cid, desc=c["desc"], task_type=task_type, family="fam-%s-b12j-%s-01" % (cid.split("-")[0], c["topic"]), level=c.get("level", "L2"),
        ref_calls=len(commands), traps=traps, decoys=decoys, axes=["LNG", "OBS"] if long_file else ["CHN", "OBS"],
        files=files, verify=verify_src(files, body), notes=notes, turns=turns)


def choice(rng, items, weights=None):
    return rng.choices(items, weights)[0] if weights else rng.choice(items)


# ------------------------------------------------------------------ M9a: several tables

CASES = {}


def tsv(*cols):
    return list(cols)


# 9241 warehouse movements, two turns
CASES["tab-9241"] = dict(
    sub="M9a", zh=True, topic="stockmove", task_type="aggregate", root="仓储", names=["仓A.txt", "仓B.txt", "仓C.txt"], sep="\t",
    cols=["单号", "品名", "类型", "数量"], rows=(150, 220), readme_name="说明.md",
    readme=["# 仓储流水说明", "", "每个仓一个文件，列：单号、品名、类型、数量（件），制表符分隔。", "品名和类型都按完整内容匹配：「螺丝刀」不是「螺丝」，「退库」既不是入库也不是出库。"],
    gen=lambda rng, i, fi, n: [f"D{fi + 1}{i:04d}", choice(rng, ["螺丝", "螺丝", "螺丝刀", "螺母", "垫片"]), choice(rng, ["入库", "入库", "出库", "出库", "退库"]), str(rng.randint(10, 400))],
    desc="Two turns over three warehouse ledgers: screws received, then screws shipped out, with a look-alike item name and a third movement type",
    why="品名 and 类型 are exact columns of the tab-separated ledgers.",
    queries=[
        dict(prompt="三个仓这个月「螺丝」一共入库了多少件？口径见 仓储/说明.md，回复数字即可。", agg="sum", col="数量", pred='r["品名"]=="螺丝" and r["类型"]=="入库"',
             decoy='"螺丝" in r["品名"] and r["类型"]=="入库"', decoy_note="品名包含螺丝，含螺丝刀",
             cmd="""cat 仓储/*.txt | awk -F'\\t' '$2=="螺丝" && $3=="入库" {s+=$4} END{print s}'""", unit="三个仓螺丝入库合计 {v} 件。", alts=[]),
        dict(prompt="那同一批流水里，「螺丝」出库了多少件？", agg="sum", col="数量", pred='r["品名"]=="螺丝" and r["类型"]=="出库"',
             decoy='"螺丝" in r["品名"] and r["类型"]=="出库"', decoy_note="品名包含螺丝，含螺丝刀",
             cmd="""cat 仓储/*.txt | awk -F'\\t' '$2=="螺丝" && $3=="出库" {s+=$4} END{print s}'""", unit="螺丝出库合计 {v} 件。",
             alts=["仓储流水里螺丝一共出库多少件？", "三个仓里被领走（出库）的螺丝合计多少件？", "螺丝的出库数量总和是多少？", "按说明.md的口径，螺丝出库共多少件？", "把三份仓单里品名为螺丝、类型为出库的数量加起来。"]),
    ])

# 9242 bus swipes, two turns
CASES["tab-9242"] = dict(
    sub="M9a", zh=True, topic="shuttleswipe", task_type="aggregate", root="班车", names=["第1周.dat", "第2周.dat", "第3周.dat", "第4周.dat"], sep=";",
    cols=["日期", "线路", "站点", "人数"], rows=(120, 180), readme_name="说明.md",
    readme=["# 班车刷卡数据说明", "", "每周一个文件，分号分隔：日期;线路;站点;上车人数。", "线路、站点按完整名称匹配：「7路快」「17路」「27路」都不是「7路」，「南门外」不是「南门」。"],
    gen=lambda rng, i, fi, n: [f"2026-10-{fi * 7 + rng.randint(1, 7):02d}", choice(rng, ["7路", "7路", "17路", "7路快", "27路", "3路"]), choice(rng, ["南门", "南门", "北站", "大学城", "南门外", "医院"]), str(rng.randint(3, 60))],
    desc="Two turns over four weekly boarding tables: riders of line 7, then riders of line 7 at one stop, with look-alike line and stop names",
    why="线路 and 站点 are matched as whole values in the semicolon-separated tables.",
    queries=[
        dict(prompt="十月这四周里，7路班车一共上了多少人？口径见 班车/说明.md。", agg="sum", col="人数", pred='r["线路"]=="7路"', decoy='"7路" in r["线路"]', decoy_note="线路包含7路，含17路、27路、7路快",
             cmd="""cat 班车/*.dat | awk -F';' '$2=="7路" {s+=$4} END{print s}'""", unit="7路合计上车 {v} 人。", alts=[]),
        dict(prompt="其中7路在「南门」站上车的有多少人？", agg="sum", col="人数", pred='r["线路"]=="7路" and r["站点"]=="南门"', decoy='"7路" in r["线路"] and "南门" in r["站点"]', decoy_note="线路、站点都用包含匹配",
             cmd="""cat 班车/*.dat | awk -F';' '$2=="7路" && $3=="南门" {s+=$4} END{print s}'""", unit="7路在南门站上车 {v} 人。",
             alts=["7路班车在南门站一共上车多少人？", "四周数据里，线路是7路、站点是南门的人数合计是多少？", "只算7路和南门站，上车总人数是多少？", "按说明.md的口径，7路南门站的上车人数合计。", "南门站有多少人乘坐7路上车（四周合计）？"]),
    ])

# 9243 lab reservations, two turns
CASES["tab-9243"] = dict(
    sub="M9a", zh=True, topic="labbooking", task_type="aggregate", root="实验室", names=["预约-9月.txt", "预约-10月.txt", "预约-11月.txt"], sep="\t",
    cols=["日期", "仪器", "预约人", "分钟"], rows=(160, 230), readme_name="说明.md",
    readme=["# 仪器预约记录说明", "", "每月一个文件：日期、仪器、预约人、使用时长（分钟），制表符分隔。", "「显微镜-备用」是另一台设备，单独结算；预约人同名才算同一个人，「陈琳琳」不是「陈琳」。"],
    gen=lambda rng, i, fi, n: [f"2026-{9 + fi:02d}-{rng.randint(1, 28):02d}", choice(rng, ["显微镜", "显微镜", "显微镜-备用", "离心机", "天平"]), choice(rng, ["陈琳", "陈琳", "陈琳琳", "王磊", "赵敏", "孙阳"]), str(rng.choice([30, 45, 60, 90, 120, 150]))],
    desc="Two turns over three monthly lab booking tables: total microscope minutes, then how many bookings one person made, with a backup device and a look-alike name",
    why="仪器 and 预约人 are exact columns.",
    queries=[
        dict(prompt="实验室三个月的预约里，「显微镜」一共用了多少分钟？按 实验室/说明.md 的口径。", agg="sum", col="分钟", pred='r["仪器"]=="显微镜"', decoy='"显微镜" in r["仪器"]', decoy_note="仪器包含显微镜，含显微镜-备用",
             cmd="""cat 实验室/*.txt | awk -F'\\t' '$2=="显微镜" {s+=$4} END{print s}'""", unit="显微镜合计 {v} 分钟。", alts=[]),
        dict(prompt="再查一下，陈琳这三个月一共预约了多少次（任何仪器都算）？", agg="count", pred='r["预约人"]=="陈琳"', decoy='"陈琳" in r["预约人"]', decoy_note="预约人包含陈琳，含陈琳琳",
             cmd="""cat 实验室/*.txt | awk -F'\\t' '$3=="陈琳"' | wc -l""", unit="陈琳共预约 {v} 次。",
             alts=["三个月的记录里，预约人是陈琳的有多少条？", "陈琳一共约了几次仪器？", "统计预约人为陈琳的记录条数（不分仪器）。", "按说明.md，陈琳（不是陈琳琳）总共预约多少次？", "三份预约表里陈琳出现了多少次？"]),
    ])

# 9244 CI runs, English, two turns
CASES["tab-9244"] = dict(
    sub="M9a", zh=False, topic="cijobs", task_type="aggregate", root="ci", names=["runs-w1.dat", "runs-w2.dat", "runs-w3.dat"], sep=" ",
    cols=["job", "branch", "status", "seconds"], rows=(170, 240), readme_name="README.md",
    readme=["# CI run export", "", "One file per week, space separated: job branch status seconds.", "Branch and status are whole values: `main-hotfix` is not `main`, `failed-retry` is not `failed`."],
    gen=lambda rng, i, fi, n: [f"build-{rng.randint(1, 30):02d}", choice(rng, ["main", "main", "main-hotfix", "release", "release-2.1", "dev"]), choice(rng, ["passed", "passed", "failed", "failed", "failed-retry", "cancelled"]), str(rng.randint(40, 1800))],
    desc="Two turns over three weekly CI exports: failed runs on main, then the longest passed run on release, with look-alike branch and status names",
    why="branch and status are whole-value columns of the space-separated export.",
    queries=[
        dict(prompt="How many CI runs on branch main ended with status failed across the three weekly files? ci/README.md has the rule; just give me the count.", agg="count", pred='r["branch"]=="main" and r["status"]=="failed"',
             decoy='r["branch"].startswith("main") and r["status"].startswith("failed")', decoy_note="prefix match on branch and status",
             cmd="""cat ci/*.dat | awk '$2=="main" && $3=="failed"' | wc -l""", unit="{v} failed runs on main.", alts=[]),
        dict(prompt="And what is the longest duration in seconds of a passed run on the release branch?", agg="max", col="seconds", pred='r["branch"]=="release" and r["status"]=="passed"',
             decoy='r["branch"].startswith("release") and r["status"]=="passed"', decoy_note="branch prefix match, includes release-2.1",
             cmd="""cat ci/*.dat | awk '$2=="release" && $3=="passed" && $4+0>m {m=$4+0} END{print m}'""", unit="The longest passed run on release took {v} seconds.",
             alts=["Longest passed run on the release branch, in seconds?", "What is the max seconds among passed runs of branch release in the CI files?", "Across the weekly CI files, how long was the slowest passed release run?", "Max duration (seconds) for status passed on branch release, per ci/README.md.", "Which duration in seconds is the largest for passed runs on release?"]),
    ], min=40)

# 9245 library loans, two turns
CASES["tab-9245"] = dict(
    sub="M9a", zh=True, topic="libloans", task_type="aggregate", root="借阅", names=["东馆.txt", "西馆.txt", "南馆.txt"], sep="\t",
    cols=["借书证", "书名", "状态", "天数"], rows=(150, 210), readme_name="说明.md",
    readme=["# 借阅记录说明", "", "每个分馆一个文件：借书证、书名、状态、已借天数，制表符分隔。", "状态按完整内容匹配：「逾期已处理」已经结清，不算逾期。同一借书证在不同分馆视为同一读者。"],
    gen=lambda rng, i, fi, n: [f"L{rng.randint(1001, 1070)}", f"《{choice(rng, ['三体', '平凡的世界', '活着', '围城', '百年孤独', '人类简史'])}》", choice(rng, ["逾期", "逾期", "已归还", "已归还", "借出中", "逾期已处理"]), str(rng.randint(1, 60))],
    desc="Two turns over three branch loan tables: count of overdue loans, then the number of distinct readers with an overdue loan, with a look-alike settled status",
    why="状态 is a whole-value column and 借书证 identifies a reader across files.",
    queries=[
        dict(prompt="三个分馆的借阅记录里，状态为「逾期」的一共有多少条？口径见 借阅/说明.md。", agg="count", pred='r["状态"]=="逾期"', decoy='r["状态"].startswith("逾期")', decoy_note="前缀匹配，含逾期已处理",
             cmd="""cat 借阅/*.txt | awk -F'\\t' '$3=="逾期"' | wc -l""", unit="逾期记录共 {v} 条。", alts=[]),
        dict(prompt="这些逾期记录涉及多少个不同的借书证？", agg="distinct", col="借书证", pred='r["状态"]=="逾期"', decoy='r["状态"].startswith("逾期")', decoy_note="前缀匹配，含逾期已处理",
             cmd="""cat 借阅/*.txt | awk -F'\\t' '$3=="逾期" {print $1}' | sort -u | wc -l""", unit="逾期涉及 {v} 个不同的借书证。",
             alts=["有逾期记录的读者（按借书证）一共多少人？", "状态是逾期的记录里，不重复的借书证有多少个？", "三个分馆合起来，有多少个借书证存在逾期？", "按说明.md，逾期读者的人数是多少？", "逾期记录对应的借书证去重后有几个？"]),
    ])

# 9246 parcel weights, max
CASES["tab-9246"] = dict(
    sub="M9a", zh=True, topic="parcelweight", task_type="aggregate", root="快递站", names=["周一.txt", "周二.txt", "周三.txt", "周四.txt"], sep="\t",
    cols=["运单", "类别", "重量克", "城市"], rows=(140, 200), readme_name="说明.md",
    readme=["# 快递站入库表说明", "", "每天一个文件：运单、类别、重量（克）、目的城市，制表符分隔。", "类别按完整名称匹配：「易碎-加固」是加固包装后的单件，单独管理，不算「易碎」。"],
    gen=lambda rng, i, fi, n: (lambda cat: [f"YD{fi}{i:04d}", cat, str(rng.randint(300, 4800) if cat != "易碎-加固" else rng.randint(2500, 9000)), choice(rng, ["杭州", "成都", "武汉", "西安"])])(choice(rng, ["易碎", "易碎", "易碎-加固", "普通", "生鲜", "大件"])),
    desc="Finds the heaviest parcel of one category over four daily tables where a look-alike category has heavier items",
    why="类别 is a whole-value column; the max is taken over rows whose category is exactly 易碎.",
    queries=[dict(prompt="四天的入库表里，「易碎」类别最重的一件是多少克？口径见 快递站/说明.md，只要数字。", agg="max", col="重量克", pred='r["类别"]=="易碎"', decoy='"易碎" in r["类别"]', decoy_note="类别包含易碎，含易碎-加固",
                   cmd="""cat 快递站/*.txt | awk -F'\\t' '$2=="易碎" && $3+0>m {m=$3+0} END{print m}'""", unit="易碎类别最重一件 {v} 克。",
                   alts=["易碎件里单件最大重量是多少克？", "快递站四天数据中，类别为易碎的最大重量。", "按说明.md，易碎类别重量克的最大值是多少？", "四个入库表里最重的易碎包裹有多重（克）？", "类别恰好是易碎的包裹，最重的是多少克？"])], min=100)

# 9247 meter readings, sum
CASES["tab-9247"] = dict(
    sub="M9a", zh=True, topic="meterreading", task_type="aggregate", root="抄表", names=["东区.dat", "西区.dat", "南区.dat", "北区.dat"], sep=";",
    cols=["户号", "区域", "度数", "日期"], rows=(130, 190), readme_name="说明.md",
    readme=["# 抄表汇总说明", "", "每个片区一个文件，分号分隔：户号;区域;度数;日期。", "区域按完整名称匹配：「商铺街」是商业步行街的独立计量区，不属于「商铺」。"],
    gen=lambda rng, i, fi, n: [f"H{fi}{rng.randint(100, 999)}", choice(rng, ["商铺", "商铺", "商铺街", "住宅", "住宅", "园区"]), str(rng.randint(20, 900)), f"2026-09-{rng.randint(1, 30):02d}"],
    desc="Sums meter readings of one area type over four district tables where a look-alike area name shares the prefix",
    why="区域 is a whole-value column of the semicolon-separated tables.",
    queries=[dict(prompt="九月四个片区的抄表数据里，区域为「商铺」的用电量一共多少度？口径见 抄表/说明.md。", agg="sum", col="度数", pred='r["区域"]=="商铺"', decoy='r["区域"].startswith("商铺")', decoy_note="前缀匹配，含商铺街",
                   cmd="""cat 抄表/*.dat | awk -F';' '$2=="商铺" {s+=$3} END{print s}'""", unit="商铺合计用电 {v} 度。",
                   alts=["商铺区域九月一共用了多少度电？", "四个片区里区域为商铺的度数合计是多少？", "按说明.md，把商铺的用电量加总。", "抄表数据中，商铺（不含商铺街）总共多少度？", "九月商铺用电量合计，单位度。"])])

# 9248 gateway tenants, English distinct
CASES["log-9248"] = dict(
    sub="M9a", zh=False, topic="ratelimit", task_type="aggregate", root="gw", names=["edge-a.txt", "edge-b.txt", "edge-c.txt"], sep=" ",
    cols=["time", "tenant", "route", "status"], rows=(200, 280), readme_name="README.md",
    readme=["# Edge request samples", "", "One file per edge node, space separated: time tenant route status.", "Only status 429 means rate limited; other 4xx codes (401, 404, 409) are ordinary client errors."],
    gen=lambda rng, i, fi, n: [f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}", f"t-{rng.randint(1, 420):03d}", choice(rng, ["/v1/items", "/v1/orders", "/v1/search", "/v1/export"]), choice(rng, ["200", "200", "429", "429", "429", "401", "404", "500"])],
    desc="Counts distinct tenants that were rate limited (status 429) across three edge-node samples where other 4xx codes are decoys",
    why="status 429 is matched exactly; tenants are de-duplicated across files.",
    queries=[dict(prompt="How many different tenants got a 429 at least once across the three edge-node files? gw/README.md defines what counts.", agg="distinct", col="tenant", pred='r["status"]=="429"', decoy='r["status"].startswith("4")', decoy_note="any 4xx status",
                   cmd="""cat gw/*.txt | awk '$4==429 {print $2}' | sort -u | wc -l""", unit="{v} distinct tenants were rate limited.",
                   alts=["Number of unique tenants that were rate limited (429) on any edge node?", "Count distinct tenant ids with at least one 429 in gw/.", "Across edge-a, edge-b and edge-c, how many tenants hit the rate limit?", "How many tenants appear with status 429, de-duplicated?", "Per gw/README.md, how many different tenants were throttled?"])], min=100)

# 9249 canteen card swipes
CASES["tab-9249"] = dict(
    sub="M9a", zh=True, topic="canteenwindow", task_type="aggregate", root="食堂", names=["周一.txt", "周二.txt", "周三.txt"], sep="\t",
    cols=["时间", "卡号", "窗口", "金额"], rows=(180, 250), readme_name="说明.md",
    readme=["# 食堂刷卡记录说明", "", "每天一个文件：时间、卡号、窗口、金额（元，整数），制表符分隔。", "窗口按完整名称匹配：「13号窗口」「3号窗口(外卖)」都不是「3号窗口」。"],
    gen=lambda rng, i, fi, n: [f"{rng.randint(11, 13)}:{rng.randint(0, 59):02d}", f"C{rng.randint(1000, 1400)}", choice(rng, ["3号窗口", "3号窗口", "13号窗口", "3号窗口(外卖)", "1号窗口", "5号窗口"]), str(rng.randint(6, 48))],
    desc="Sums the revenue of one canteen window over three daily swipe tables where window names that contain it are decoys",
    why="窗口 is a whole-value column.",
    queries=[dict(prompt="三天食堂刷卡记录里，「3号窗口」的营业额一共多少元？口径见 食堂/说明.md，直接给数字。", agg="sum", col="金额", pred='r["窗口"]=="3号窗口"', decoy='"3号窗口" in r["窗口"]', decoy_note="窗口包含3号窗口，含13号窗口和外卖",
                   cmd="""cat 食堂/*.txt | awk -F'\\t' '$3=="3号窗口" {s+=$4} END{print s}'""", unit="3号窗口营业额 {v} 元。",
                   alts=["3号窗口这三天卖了多少钱？", "统计窗口为3号窗口的金额总和（元）。", "按说明.md，3号窗口三天营业额合计是多少？", "刷卡记录里3号窗口（不含外卖）的金额加起来是多少元？", "三份食堂记录中3号窗口的总收入。"])])

# 9250 shipments, English sum
CASES["tab-9250"] = dict(
    sub="M9a", zh=False, topic="carrierweight", task_type="aggregate", root="freight", names=["oct-w1.dat", "oct-w2.dat", "oct-w3.dat", "oct-w4.dat"], sep=";",
    cols=["id", "carrier", "kg", "date"], rows=(120, 170), readme_name="README.md",
    readme=["# Freight weigh-ins", "", "One file per week, semicolon separated: id;carrier;kg;date.", "The carrier column is exact. `DHL-Freight` is a different contract that is billed separately, so it is not `DHL`."],
    gen=lambda rng, i, fi, n: [f"S{fi + 1}{i:04d}", choice(rng, ["DHL", "DHL", "FedEx", "UPS", "DHL-Freight"]), str(rng.randint(2, 140)), f"2026-10-{fi * 7 + rng.randint(1, 7):02d}"],
    desc="Sums the kilograms shipped by one carrier over four weekly weigh-in tables where a freight-contract carrier name shares the prefix",
    why="carrier is a whole-value column.",
    queries=[dict(prompt="What is the total weight in kg shipped with carrier DHL in the four October files? Follow freight/README.md and reply with the number.", agg="sum", col="kg", pred='r["carrier"]=="DHL"', decoy='r["carrier"].startswith("DHL")', decoy_note="prefix match, includes DHL-Freight",
                   cmd="""cat freight/*.dat | awk -F';' '$2=="DHL" {s+=$3} END{print s}'""", unit="DHL shipped {v} kg in total.",
                   alts=["Sum the kg of DHL shipments over October.", "How many kilograms did DHL carry across the four weekly files?", "Total kg for carrier DHL (not DHL-Freight) in freight/.", "October weigh-ins: what is DHL's total weight in kg?", "Add up the kg column for rows whose carrier is DHL."])])

# 9251 inspection rounds
CASES["tab-9251"] = dict(
    sub="M9a", zh=True, topic="roundcheck", task_type="aggregate", root="巡检", names=["一车间.txt", "二车间.txt", "三车间.txt", "四车间.txt"], sep="\t",
    cols=["时间", "点位", "巡检员", "结果"], rows=(120, 180), readme_name="说明.md",
    readme=["# 巡检打卡说明", "", "每个车间一个文件：时间、点位、巡检员、结果，制表符分隔。", "结果取值：正常、异常、异常已处理、漏检。统计异常只算结果恰好是「异常」的打卡，已处理的和漏检的另算。"],
    gen=lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d} {rng.randint(0, 23):02d}:00", f"P{rng.randint(1, 40):02d}", choice(rng, ["吴刚", "郑洁", "冯涛", "蒋芸"]), choice(rng, ["正常", "正常", "异常", "异常", "异常已处理", "漏检"])],
    desc="Counts inspection rounds with result 异常 over four workshop tables where a handled-exception result is a look-alike",
    why="结果 is a whole-value column.",
    queries=[dict(prompt="四个车间十月的巡检打卡里，结果为「异常」的一共有多少条？口径见 巡检/说明.md。", agg="count", pred='r["结果"]=="异常"', decoy='r["结果"].startswith("异常")', decoy_note="前缀匹配，含异常已处理",
                   cmd="""cat 巡检/*.txt | awk -F'\\t' '$4=="异常"' | wc -l""", unit="异常打卡共 {v} 条。",
                   alts=["巡检记录里结果是异常的有多少次？", "四个车间合计，异常（未处理）的打卡条数。", "统计结果列恰好等于异常的行数。", "按说明.md，十月异常巡检一共几条？", "四份巡检表里异常出现了多少次？"])])

# 9252 exam scores, max
CASES["tab-9252"] = dict(
    sub="M9a", zh=True, topic="examscore", task_type="aggregate", root="成绩", names=["一班.txt", "二班.txt", "三班.txt", "四班.txt", "五班.txt"], sep="\t",
    cols=["学号", "班级", "科目", "分数"], rows=(90, 130), readme_name="说明.md",
    readme=["# 期中成绩说明", "", "每班一个文件：学号、班级、科目、分数，制表符分隔。", "科目按完整名称匹配：「数学建模」是选修课，不是「数学」；数学满分 120，选修课满分 150。"],
    gen=lambda rng, i, fi, n: (lambda sub: [f"2026{fi + 1}{i:03d}", f"{fi + 1}班", sub, "%.1f" % (rng.randint(400, 1200) / 10 if sub != "数学建模" else rng.randint(600, 1500) / 10)])(choice(rng, ["数学", "数学", "数学建模", "语文", "英语"])),
    desc="Finds the top score of one subject over five class tables where a look-alike elective has higher scores",
    why="科目 is a whole-value column.",
    queries=[dict(prompt="五个班的期中成绩里，「数学」科目的最高分是多少？口径见 成绩/说明.md，回复分数即可。", agg="max", col="分数", pred='r["科目"]=="数学"', decoy='"数学" in r["科目"]', decoy_note="科目包含数学，含数学建模（满分更高）",
                   cmd="""cat 成绩/*.txt | awk -F'\\t' '$3=="数学" && $4+0>m {m=$4+0} END{print m}'""", unit="数学最高分是 {v}。",
                   alts=["数学这科全年级最高多少分？", "五个班里科目是数学的最高分。", "按说明.md，数学（不含数学建模）的最高分是多少？", "成绩表中数学成绩的最大值。", "所有班级里数学考得最高的分数是多少？"])], min=60)

# ------------------------------------------------------------------ M9c: one long file


def long_case(cid, **kw):
    CASES[cid] = dict(sub="M9c", names=[kw.pop("fname")], rows=kw.pop("rows"), **kw)


def b_gen(rng, i, fi, n):
    msgs = ["依赖解析完成_共计143个包", "编译单元缓存命中率偏低_建议清理增量缓存", "单元测试并发度调整为8_耗时预计增加", "镜像层复用成功_跳过基础层重建",
            "静态检查完成_无新增告警", "产物签名校验通过_准备上传制品库", "缓存目录占用超过阈值_触发自动清理", "测试报告已归档到共享存储"]
    lvl = choice(rng, ["INFO", "INFO", "INFO", "INFO", "WARN", "WARN-DEPRECATED", "ERROR", "ERROR-RETRY"], [30, 30, 30, 30, 6, 6, 1, 3])
    return [f"2026-10-03T{(i // 60) % 24:02d}:{i % 60:02d}:{(i * 7) % 60:02d}", lvl, choice(rng, ["compile", "test", "package", "deploy", "cache"]), choice(rng, msgs)]


# 9253 build log, two turns
long_case("log-9253", fname="build.txt", rows=(1150, 1250), sub_zh=True, zh=True, topic="buildlevels", task_type="count_events", root="构建", sep="\t",
          cols=["时间", "级别", "模块", "信息"], header=False, readme_name="说明.md", gen=b_gen,
          readme=["# 构建日志说明", "", "build.txt 是一次流水线的完整输出，每行：时间、级别、模块、信息，制表符分隔，没有表头，按时间顺序追加。", "级别按完整内容匹配：「WARN-DEPRECATED」是弃用提示，「ERROR-RETRY」是自动重试的中间状态，它们不等于「WARN」「ERROR」。"],
          desc="Two turns over one long build log: count of WARN lines, then the line number of the first ERROR, with look-alike levels",
          why="级别 is a whole-value column and build.txt has no header so line numbers equal row numbers.", min=3,
          queries=[
              dict(prompt="构建/build.txt 里级别为 WARN 的日志一共有多少行？口径见 构建/说明.md。", agg="count", pred='r["级别"]=="WARN"', decoy='r["级别"].startswith("WARN")', decoy_note="前缀匹配，含WARN-DEPRECATED",
                   cmd="""awk -F'\\t' '$2=="WARN"' 构建/build.txt | wc -l""", unit="WARN 共 {v} 行。", alts=[]),
              dict(prompt="第一条级别为 ERROR 的日志在 build.txt 的第几行？", agg="first_line", pred='r["级别"]=="ERROR"', decoy='r["级别"].startswith("ERROR")', decoy_note="前缀匹配，含ERROR-RETRY",
                   cmd="""awk -F'\\t' '$2=="ERROR" {print NR; exit}' 构建/build.txt""", unit="第一条 ERROR 在第 {v} 行。",
                   alts=["build.txt 里最早出现的 ERROR 是哪一行？", "ERROR 级别的日志第一次出现在第几行（行号从1起）？", "按说明.md，首个 ERROR 的行号是多少？", "给我 build.txt 中第一条 ERROR 所在的行号。", "build.txt 的第几行是第一次出现 ERROR。"]),
          ])


def t_gen(rng, i, fi, n):
    s = choice(rng, ["S-07", "S-07", "S-07B", "S-17", "S-70", "S-12", "S-03", "S-21"])
    lo, hi = {"S-07": (100, 310), "S-07B": (200, 450)}.get(s, (50, 380))
    return [f"2026-10-06 {(i // 60) % 24:02d}:{i % 60:02d}", s, "%.1f" % (rng.randint(lo, hi) / 10), str(rng.randint(20, 100))]


# 9254 sensor readings, two turns
long_case("tab-9254", fname="readings.dat", rows=(1200, 1350), zh=True, topic="sensorpeak", task_type="aggregate", root="传感器", sep=",",
          cols=["时间", "传感器", "温度", "电量"], header=True, readme_name="说明.md", gen=t_gen, min=3,
          readme=["# 传感器读数说明", "", "readings.dat 每分钟追加若干传感器的读数，逗号分隔：时间,传感器,温度(摄氏度),电量(%)。", "传感器编号按完整内容匹配：「S-07B」是另一块板子，不是「S-07」。"],
          desc="Two turns over one long readings file: max temperature of sensor S-07, then the number of S-07 readings above 20 degrees, with a look-alike sensor id",
          why="传感器 is a whole-value column; the temperature comparison is numeric.",
          queries=[
              dict(prompt="传感器/readings.dat 里，S-07 温度超过 20 度的读数有多少条？口径见 传感器/说明.md。", agg="count", pred='r["传感器"]=="S-07" and float(r["温度"])>20', decoy='r["传感器"].startswith("S-07") and float(r["温度"])>20', decoy_note="前缀匹配，含S-07B",
                   cmd="""awk -F, '$2=="S-07" && $3+0>20' 传感器/readings.dat | wc -l""", unit="S-07 超过 20 度的读数有 {v} 条。",
                   alts=[]),
              dict(prompt="那同一个传感器 S-07 记录到的最高温度是多少度？", agg="max", col="温度", pred='r["传感器"]=="S-07"', decoy='r["传感器"].startswith("S-07")', decoy_note="前缀匹配，含S-07B",
                   cmd="""awk -F, '$2=="S-07" && $3+0>m {m=$3+0} END{print m}' 传感器/readings.dat""", unit="S-07 最高温度 {v} 度。", alts=["readings.dat 里 S-07 的最高读数是多少度？", "S-07（不是 S-07B）的温度最大值。", "按说明.md，S-07 记录过的最高温度是多少？", "S-07 的所有读数里温度最高的是多少度？", "传感器 S-07 的峰值温度是多少？"]),
          ])


def d_gen(rng, i, fi, n):
    svc = choice(rng, ["payments", "payments", "payments-v2", "orders", "search", "payments-gw"])
    act = choice(rng, ["deploy", "deploy", "deploy", "deploy", "restart", "ROLLBACK", "ROLLBACK-DRY"], [30, 30, 30, 30, 20, 3, 5])
    return [f"2026-{9 + i // 500:02d}-{(i % 28) + 1:02d}", f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}:{rng.randint(0, 59):02d}", svc, act, f"v{rng.randint(1, 4)}.{rng.randint(0, 20)}.{rng.randint(0, 9)}", choice(rng, ["ok", "ok", "ok", "slow", "failed"])]


# 9255 deploy history, English, two turns
long_case("log-9255", fname="deploy-history.txt", rows=(1300, 1450), zh=False, topic="rollbackhist", task_type="locate_error", root="ops", sep=" ",
          cols=["date", "time", "service", "action", "version", "result"], header=False, readme_name="README.md", gen=d_gen, min=3,
          readme=["# Deploy history", "", "deploy-history.txt is append-only, one event per line, no header: date time service action version result.", "Service and action are whole values: `payments-v2` and `payments-gw` are other services, and `ROLLBACK-DRY` is a rehearsal, not a rollback."],
          desc="Two turns over one long deploy history: the line number of the last ROLLBACK of payments, then how many rollbacks payments had, with look-alike service and action names",
          why="service and action are whole-value columns and the file has no header, so line numbers equal row numbers.",
          queries=[
              dict(prompt="In ops/deploy-history.txt, on which line is the last ROLLBACK of the payments service? Rules are in ops/README.md; reply with the line number.", agg="last_line", pred='r["service"]=="payments" and r["action"]=="ROLLBACK"',
                   decoy='r["service"].startswith("payments") and r["action"].startswith("ROLLBACK")', decoy_note="prefix match on service and action",
                   cmd="""awk '$3=="payments" && $4=="ROLLBACK" {n=NR} END{print n}' ops/deploy-history.txt""", unit="The last payments ROLLBACK is on line {v}.", alts=[]),
              dict(prompt="And how many ROLLBACK events does payments have in total in that file?", agg="count", pred='r["service"]=="payments" and r["action"]=="ROLLBACK"',
                   decoy='r["service"].startswith("payments") and r["action"].startswith("ROLLBACK")', decoy_note="prefix match on service and action",
                   cmd="""awk '$3=="payments" && $4=="ROLLBACK"' ops/deploy-history.txt | wc -l""", unit="payments has {v} ROLLBACK events.",
                   alts=["Total number of ROLLBACK lines for the payments service?", "Count the payments rollbacks (not dry runs) in deploy-history.txt.", "How many times was payments rolled back, per ops/README.md?", "Number of lines with service payments and action ROLLBACK.", "How many real rollbacks did the payments service have?"]),
          ])


def c_gen(rng, i, fi, n):
    typ = choice(rng, ["呼入", "呼入", "呼出", "呼入转接", "未接"])
    return [f"2026-10-{(i // 50) % 28 + 1:02d} {rng.randint(8, 21):02d}:{rng.randint(0, 59):02d}", f"1{rng.randint(30, 89)}{rng.randint(10000000, 99999999)}", typ, str(rng.randint(5, 1500) if typ != "未接" else 0)]


# 9256 call records
long_case("tab-9256", fname="calls.dat", rows=(1350, 1450), zh=True, topic="longcalls", task_type="count_events", root="话务", sep=";",
          cols=["时间", "号码", "类型", "时长秒"], header=True, readme_name="说明.md", gen=c_gen, min=10,
          readme=["# 话务记录说明", "", "calls.dat 是整月通话明细，分号分隔：时间;号码;类型;时长（秒），第一行是表头。", "类型按完整内容匹配：「呼入转接」是转接给二线的通话，不算「呼入」。长通话指时长超过 600 秒。"],
          desc="Counts long inbound calls in one big call-detail file where a transferred-call type shares the prefix",
          why="类型 is a whole-value column; the duration threshold is strictly greater than 600.",
          queries=[dict(prompt="话务/calls.dat 里，类型为「呼入」且时长超过 600 秒的通话有多少条？口径见 话务/说明.md，回复数字就行。", agg="count", pred='r["类型"]=="呼入" and int(r["时长秒"])>600',
                        decoy='r["类型"].startswith("呼入") and int(r["时长秒"])>600', decoy_note="前缀匹配，含呼入转接",
                        cmd="""awk -F';' '$3=="呼入" && $4+0>600' 话务/calls.dat | wc -l""", unit="呼入长通话共 {v} 条。",
                        alts=["calls.dat 中呼入通话里超过 600 秒的有几条？", "统计类型是呼入、时长大于 600 秒的记录数。", "按说明.md，长通话（呼入）的数量是多少？", "整月明细里呼入且通话超过十分钟的有多少条？", "类型恰好是呼入、时长高于 600 秒的行数。"])])


def w_gen(rng, i, fi, n):
    syl = ["天", "地", "光", "电", "水", "火", "风", "云", "山", "海", "石", "木", "金", "土", "星", "月", "日", "雨", "雪", "霜"]
    word = "".join(rng.choice(syl) for _ in range(rng.choice([2, 3])))
    if i == 120:
        word = "蓝牙耳机"
    elif i == 300:
        word = "蓝牙音箱"
    elif i in (610, 840):
        word = "蓝牙"
    elif word in ("蓝牙", "蓝牙耳机", "蓝牙音箱"):
        word = word + "石"
    return [word, choice(rng, ["名词", "名词", "动词", "形容词"]), "该词条的释义文字_用于补足行宽"]


# 9257 glossary line number
long_case("tab-9257", fname="词表.txt", rows=(950, 1000), zh=True, topic="glossaryline", task_type="locate_error", root="词典", sep="\t",
          cols=["词条", "词性", "释义"], header=True, readme_name="说明.md", gen=w_gen, min=20,
          readme=["# 词表说明", "", "词表.txt 是按录入顺序排列的词条表，制表符分隔：词条、词性、释义，第一行是表头。", "「行号」指文件里的物理行号，表头算第 1 行。词条按完整内容匹配：「蓝牙耳机」「蓝牙音箱」是独立词条，不是「蓝牙」。"],
          desc="Finds the physical line number of the first entry that is exactly 蓝牙 in a long glossary where longer compound entries come earlier",
          why="词条 is a whole-value column, the header is line 1, and the first exact entry is unique.",
          queries=[dict(prompt="词典/词表.txt 里，词条恰好是「蓝牙」的第一条在文件的第几行？行号的算法见 词典/说明.md。", agg="first_line", pred='r["词条"]=="蓝牙"', decoy='r["词条"].startswith("蓝牙")', decoy_note="前缀匹配，首个是蓝牙耳机",
                        cmd="""awk -F'\\t' '$1=="蓝牙" {print NR; exit}' 词典/词表.txt""", unit="词条「蓝牙」第一次出现在第 {v} 行。",
                        alts=["词表里「蓝牙」这个词条首次出现在哪一行？", "词表.txt 中词条等于蓝牙的最早一行是第几行（表头算第1行）？", "按说明.md，找出蓝牙第一次作为独立词条出现的行号。", "「蓝牙」（不是蓝牙耳机）在词表的第几行第一次出现？", "给我词条列恰好为蓝牙的第一行行号。"])])


def a_gen(rng, i, fi, n):
    act = choice(rng, ["ALLOW", "ALLOW", "ALLOW", "DENY", "DENY-SOFT", "AUDIT"])
    ip = "10.%d.%d.%d" % (rng.randint(0, 3), rng.randint(0, 9), rng.randint(1, 40))
    return [f"2026-10-08T{(i // 60) % 24:02d}:{i % 60:02d}:{rng.randint(0, 59):02d}", ip, f"u{rng.randint(100, 160)}", act, choice(rng, ["/admin", "/export", "/report", "/profile", "/settings"])]


# 9258 audit distinct IPs, English
long_case("log-9258", fname="audit.txt", rows=(1250, 1400), zh=False, topic="denyips", task_type="aggregate", root="security", sep=" ",
          cols=["time", "ip", "user", "action", "resource"], header=False, readme_name="README.md", gen=a_gen, min=10,
          readme=["# Access audit", "", "audit.txt holds one access decision per line, no header: time ip user action resource.", "Only action DENY counts as a denial. `DENY-SOFT` is a warning-only rule hit and does not block anyone."],
          desc="Counts distinct source IPs with a DENY decision in one long audit file where a warn-only action shares the prefix",
          why="action is a whole-value column and IPs are de-duplicated.",
          queries=[dict(prompt="How many distinct IP addresses were denied (action DENY) in security/audit.txt? The README there explains the actions; reply with the number.", agg="distinct", col="ip", pred='r["action"]=="DENY"', decoy='r["action"].startswith("DENY")', decoy_note="prefix match, includes DENY-SOFT",
                        cmd="""awk '$4=="DENY" {print $2}' security/audit.txt | sort -u | wc -l""", unit="{v} distinct IPs were denied.",
                        alts=["Count the unique source IPs that got DENY in audit.txt.", "How many different IPs hit an actual DENY decision?", "Number of distinct ips whose action is exactly DENY.", "Per security/README.md, how many IP addresses were blocked?", "De-duplicated count of IPs with a DENY line."])])


def e_gen(rng, i, fi, n):
    tid = choice(rng, ["W-3021", "W-3021", "W-30210", "W-3022", "W-3019", "W-3021B", "W-3100", "W-2987"], [3, 3, 3, 5, 5, 3, 5, 5])
    ev = choice(rng, ["创建", "受理", "转派", "转派", "备注", "催办", "关闭"])
    return [f"2026-10-{(i // 45) % 28 + 1:02d} {rng.randint(8, 20):02d}:{rng.randint(0, 59):02d}", tid, ev, choice(rng, ["林峰", "钟雪", "叶凡", "周婷", "邵杰"])]


# 9259 ticket flow
long_case("log-9259", fname="events.txt", rows=(1100, 1200), zh=True, topic="ticketforward", task_type="count_events", root="工单", sep="\t",
          cols=["时间", "工单", "事件", "操作人"], header=False, readme_name="说明.md", gen=e_gen, min=4,
          readme=["# 工单流转记录说明", "", "events.txt 记录所有工单的流转事件，制表符分隔：时间、工单、事件、操作人，没有表头。", "工单号按完整内容匹配：「W-30210」「W-3021B」是别的工单，不是「W-3021」。"],
          desc="Counts the 转派 events of one ticket in a long event file where ticket ids that extend it are decoys",
          why="工单 and 事件 are whole-value columns.",
          queries=[dict(prompt="工单/events.txt 里，工单 W-3021 被「转派」过多少次？口径见 工单/说明.md。", agg="count", pred='r["工单"]=="W-3021" and r["事件"]=="转派"', decoy='r["工单"].startswith("W-3021") and r["事件"]=="转派"', decoy_note="工单号前缀匹配，含W-30210、W-3021B",
                        cmd="""awk -F'\\t' '$2=="W-3021" && $3=="转派"' 工单/events.txt | wc -l""", unit="W-3021 被转派 {v} 次。",
                        alts=["W-3021 这张工单的转派事件有几条？", "events.txt 里工单号恰好是 W-3021、事件是转派的行数。", "按说明.md，W-3021 一共转派了多少次？", "统计工单 W-3021 的转派次数。", "W-3021（不是 W-30210）被转派了几次？"])])


def p_gen(rng, i, fi, n):
    code = choice(rng, ["600519", "600519", "60051", "6005", "000858", "300750"])
    base = {"600519": (15000, 17500), "60051": (16000, 21000)}.get(code, (3000, 26000))
    return [f"2026-{1 + i // 250:02d}-{(i % 28) + 1:02d}", code, "%.2f" % (rng.randint(*base) / 10), str(rng.randint(1000, 90000))]


# 9260 stock closes
long_case("tab-9260", fname="prices.dat", rows=(1300, 1400), zh=True, topic="closepeak", task_type="aggregate", root="行情", sep="\t",
          cols=["日期", "代码", "收盘价", "成交量"], header=True, readme_name="说明.md", gen=p_gen, min=100,
          readme=["# 行情数据说明", "", "prices.dat 是多只股票的日线收盘价，制表符分隔：日期、代码、收盘价、成交量，第一行是表头。", "代码按完整内容匹配：「60051」是另一只证券，不是「600519」。"],
          desc="Finds the highest closing price of one security in a long price file where a shorter look-alike code has higher prices",
          why="代码 is a whole-value column.",
          queries=[dict(prompt="行情/prices.dat 里，代码 600519 的最高收盘价是多少？口径见 行情/说明.md，只要数字。", agg="max", col="收盘价", pred='r["代码"]=="600519"', decoy='r["代码"].startswith("60051")', decoy_note="前缀匹配，含60051",
                        cmd="""awk -F'\\t' '$2=="600519" && $3+0>m {m=$3+0} END{print m}' 行情/prices.dat""", unit="600519 最高收盘价 {v}。",
                        alts=["600519 的收盘价最大值是多少？", "prices.dat 里代码为 600519 的最高收盘价。", "按说明.md，600519 历史最高收盘价是多少？", "代码 600519（不是60051）最高收过多少？", "行情文件中 600519 的最大收盘价。"])])


def _mk(cid):
    return lambda: build(cid)


BUILDERS = []
for _cid in sorted(CASES):
    CASES[_cid].setdefault("sub", "M9a")
    BUILDERS.append(_mk(_cid))
    BUILDERS[-1].__name__ = _cid.replace("-", "_")

# static SPEC (specs.py loads this file by path and needs it at import time)
for _cid, _c in CASES.items():
    SPEC[_cid] = dict(kind="bash_aggregate", sub=_c["sub"], needs=[f"{_c['root']}/{_c['readme_name']}"])
