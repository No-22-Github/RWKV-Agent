"""M9 (bash) batch b12m of v1.41: ids 9321-9340, fresh data shapes over .txt/.dat tables.

M9a (9321-9332): several tables; top-1 group, distinct count, extreme with a README tie rule, sum / count with
look-alike values. M9c (9333-9340): one long file (1100-1450 lines) with a filler column so reading it whole is
not an option; count between markers, top-1, tie-broken extreme, sum, distinct.
Six cases have two turns (9321, 9322, 9324, 9333, 9334, 9337): turn 2 changes the filter.
Every case lists its table generator and queries; the verify script recomputes the answers from the fixture
with the same aggregation source that picks the seed and the decoys."""
import json
import re
from random import Random

from common import has, lines, phrasings, thousands, verify_src, write_case

REFS = {}
SPEC = {}
CASES = {}

AGG_SRC = '''
def agg(kind, q, rows):
    ev = lambda p, r: eval(p, {"int": int, "float": float}, {"r": r})
    if kind == "between":
        k, state, out = 0, 0, []
        for n, r in rows:
            if state == 0:
                if ev(q["start"], r):
                    k += 1
                    state = 1 if k == q.get("nth", 1) else 0
            elif ev(q["end"], r):
                state = 2
                break
            elif ev(q["pred"], r):
                out.append(n)
        if state != 2:
            raise ValueError("no window")
        return len(out)
    sel = [(n, r) for n, r in rows if ev(q["pred"], r)]
    if not sel:
        raise ValueError("empty")
    col = q.get("col")
    if kind == "count":
        return len(sel)
    if kind == "sum":
        return sum(int(r[col]) for _, r in sel)
    if kind == "max":
        return max(float(r[col]) for _, r in sel)
    if kind == "min":
        return min(float(r[col]) for _, r in sel)
    if kind == "distinct":
        return len({r[col] for _, r in sel})
    if kind == "first_line":
        return min(n for n, _ in sel)
    if kind == "last_line":
        return max(n for n, _ in sel)
    if kind == "top":
        tot = {}
        for _, r in sel:
            tot[r[q["group"]]] = tot.get(r[q["group"]], 0) + (int(r[col]) if col else 1)
        ranked = sorted(tot.items(), key=lambda kv: -kv[1] if q.get("extreme", "max") == "max" else kv[1])
        if len(ranked) < 2 or abs(ranked[0][1] - ranked[1][1]) < q.get("margin", 1):
            raise ValueError("no clear leader")
        return ranked[0][0]
    if kind == "top_n":
        tot = {}
        for _, r in sel:
            tot[r[q["group"]]] = tot.get(r[q["group"]], 0) + (int(r[col]) if col else 1)
        return max(tot.values()) if q.get("extreme", "max") == "max" else min(tot.values())
    if kind in ("argtie", "argtie_first", "argtie_n"):
        pick = max if q.get("extreme", "max") == "max" else min
        best = pick(float(r[col]) for _, r in sel)
        cands = [(n, r) for n, r in sel if float(r[col]) == best]
        if len(cands) < 2 or len({r[q["ret"]] for _, r in cands}) < 2:
            raise ValueError("no tie")
        if kind == "argtie_first":
            return cands[0][1][q["ret"]]
        if kind == "argtie_n":
            return len(sel)
        tp = min if q.get("tie_pick", "min") == "min" else max
        tv = tp(r[q["tie_col"]] for _, r in cands)
        win = [r for _, r in cands if r[q["tie_col"]] == tv]
        if len(win) != 1:
            raise ValueError("tie rule not decisive")
        return win[0][q["ret"]]
    raise ValueError(kind)
'''
_ns = {}
exec(AGG_SRC, _ns)
agg = _ns["agg"]
STRING_KINDS = ("top", "argtie")
_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def fmt(v):
    if isinstance(v, float):
        return ("%.2f" % v).rstrip("0").rstrip(".")
    return str(v)


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


def choice(rng, items, weights=None):
    return rng.choices(items, weights)[0] if weights else rng.choice(items)


def make_files(c, rng):
    files, tables = {}, {}
    header = c.get("header", True)
    for fi, name in enumerate(c["names"]):
        n = rng.randint(*c["rows"])
        rows = [c["gen"](rng, i, fi, n) for i in range(n)]
        path = f"{c['root']}/{name}"
        body = ([c["sep"].join(c["cols"])] if header else []) + [c["sep"].join(r) for r in rows]
        files[path] = lines(body)
        tables[path] = [(k + 1 + (1 if header else 0), dict(zip(c["cols"], r))) for k, r in enumerate(rows)]
    return files, tables


def build(cid):
    c = CASES[cid]
    qs = c["queries"]
    for attempt in range(900):
        rng = Random(int(cid.split("-")[1]) * 31 + attempt * 7919)
        files, tables = make_files(c, rng)
        files[f"{c['root']}/{c['readme_name']}"] = lines(c["readme"])
        allrows = [x for t in tables.values() for x in t]
        first_rows = next(iter(tables.values()))
        try:
            vals = [agg(q["agg"], q, allrows) for q in qs]
            decs = [agg(q["agg"], {**q, **q["decoy"]}, allrows) for q in qs]
            firsts = [agg(q["agg"], q, first_rows) for q in qs] if len(c["names"]) > 1 else [None] * len(qs)
            naive = [agg("argtie_first", q, allrows) if q["agg"] == "argtie" else None for q in qs]
            extras = [agg(q["agg"] + "_n", q, allrows) if q["agg"] in STRING_KINDS else None for q in qs]
        except ValueError:
            continue
        ok = True
        for q, v, d, f, nv in zip(qs, vals, decs, firsts, naive):
            if isinstance(v, str):
                others = {r[q["group"]] for _, r in allrows if q.get("group") in r and r[q["group"]] != v} if q["agg"] == "top" else set()
                ok = ok and v != d and not any(v in o for o in others) and nv != v
            else:
                ok = ok and fmt(v) != fmt(d) and fmt(v) not in fmt(d) and v >= c.get("min", 5)
            if f is not None and q["agg"] in ("sum", "count", "distinct", "top"):
                ok = ok and f != v
        ok = ok and len({fmt(v) for v in vals}) == len(vals)
        shown = [fmt(e) for e in extras if e is not None]
        ok = ok and len(set(shown)) == len(shown) and not any(e in fmt(v) for e in shown for v in vals if not isinstance(v, str))
        if ok:
            for q, ex in zip(qs, extras):
                if q["agg"] == "argtie":
                    ok = ok and near_tokens(files, float(ex)) == 0
        if ok:
            for q, v in zip(qs, vals):
                if q["agg"] in ("count", "distinct", "between", "first_line", "last_line", "max", "min"):
                    ok = ok and near_tokens(files, float(v)) == (1 if q["agg"] in ("max", "min") else 0)
        if ok:
            break
    else:
        raise SystemExit("%s: no seed found" % cid)
    readme_path = f"{c['root']}/{c['readme_name']}"
    data_paths = [f"{c['root']}/{n}" for n in c["names"]]
    qlist = [{k: v for k, v in q.items() if k in ("agg", "col", "pred", "group", "ret", "tie_col", "tie_pick", "extreme", "margin", "start", "end", "nth")} for q in qs]
    body = f'''
SEP = {c["sep"]!r}
COLS = {c["cols"]!r}
HEADER = {c.get("header", True)!r}
DATA = {data_paths!r}
QS = {qlist!r}
assert case["files"][{readme_path!r}].startswith({c["readme"][0]!r})
{AGG_SRC}
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
vals = [agg(q["agg"], q, ALL) for q in QS]
out = {{}}
sums = []
for q, val in zip(QS, vals):
    if q["agg"] == "sum":
        sums += [str(val)] + ([format(val, ",")] if val >= 1000 else [])
if sums:
    out["expected_contains_any"] = sums
last = vals[-1]
if isinstance(last, str):
    out["expected_string"] = last
    extra = agg(QS[-1]["agg"] + "_n", QS[-1], ALL)
    if extra >= 1000:
        out["expected_contains_any"] = [str(extra), format(extra, ",")]
    else:
        out["expected_number"] = extra
elif QS[-1]["agg"] != "sum":
    out["expected_number"] = int(last) if isinstance(last, float) and last == int(last) else last
print(json.dumps(out, ensure_ascii=False))
'''
    commands = [q["cmd"] + ("; " + q["cmd2"] if q.get("cmd2") else "") for q in qs]
    size = sum(len(t.encode()) for p, t in files.items() if p in data_paths)
    nrows = sum(len(t) for t in tables.values())
    long_file = c["sub"] == "M9c"
    multi = len(c["names"]) > 1
    trap_lines = []
    for i, q in enumerate(qs, 1):
        head = f"Turn {i}" if len(qs) > 1 else "TR-DECOY"
        extra = ""
        if q["agg"] == "argtie":
            extra = f" Several rows share the extreme value; file order would give {naive[i-1]}, the README rule gives {vals[i-1]}."
        trap_lines.append(f"- {head}: exact answer {fmt(vals[i-1])}; the loose reading ({q['decoy_note']}) gives {fmt(decs[i-1])}.{extra}")
    notes = "## Traps\n" + "\n".join(trap_lines) + "\n"
    if multi:
        notes += f"- TR-MULTISRC: {len(c['names'])} files; the first file alone gives {fmt(firsts[-1])}.\n"
    if long_file:
        notes += f"- TR-TRUNC: the file is {size // 1024}KB and {nrows} data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.\n"
    if len(qs) > 1:
        notes += "- Turn 2 uses a different filter over the same data, so turn 1's answer is wrong for it.\n"
    notes += "\n## Reference solution\n"
    for i, q in enumerate(qs, 1):
        notes += f"Turn {i}: bash: `{q['cmd']}` -> {fmt(vals[i-1])}\n"
        if q.get("cmd2"):
            notes += f"        then `{q['cmd2']}` for the row count asked in the prompt ({fmt(extras[i-1])})\n"
        elif extras[i-1] is not None:
            notes += f"        the same pipeline prints the total ({fmt(extras[i-1])}) next to the name\n"
    notes += f"""Final answer: {qs[-1]['unit'].format(v=fmt(vals[-1]), n=fmt(extras[-1]))}

## Why the answer is unique
{c['why']} The README ({readme_path}) fixes the rule; the answer is a single {'name' if isinstance(vals[-1], str) else 'number'}.
""" + phrasings(*qs[-1]["alts"])
    REFS[cid] = (files, commands, has(fmt(vals[-1]), fmt(extras[-1])) if extras[-1] is not None else has(fmt(vals[-1])))
    SPEC[cid] = dict(kind="bash_aggregate", sub=c["sub"], needs=[readme_path])
    turns = []
    for q, v, ex in zip(qs, vals, extras):
        if isinstance(v, str):
            want = thousands(fmt(ex))
            exp = ({"output_contains": [v], "output_contains_any": want, "max_output_chars": 600} if len(want) > 1
                   else {"output_contains": [v, fmt(ex)], "max_output_chars": 600})
        else:
            want = thousands(fmt(v)) if q["agg"] == "sum" else [fmt(v)]
            exp = {"output_contains_any": want, "max_output_chars": 600} if len(want) > 1 else {"output_contains": want, "max_output_chars": 600}
        turns.append({"prompt": q["prompt"], "expect": exp})
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
            seen = fmt(agg(qs[-1]["agg"], qs[-1], view))
        except ValueError:
            seen = "0"
        decoys["TR-TRUNC"] = seen if seen != fmt(vals[-1]) else fmt(decs[-1])
    return write_case(
        cid, desc=c["desc"], task_type=c["tt"], family="fam-%s-b12m-%s-01" % (cid.split("-")[0], c["topic"]), level=c.get("level", "L2"),
        ref_calls=len(commands), traps=traps, decoys=decoys, axes=["LNG", "OBS"] if long_file else ["CHN", "OBS"],
        files=files, verify=verify_src(files, body), notes=notes, turns=turns)


def case(cid, **kw):
    CASES[cid] = kw


T = "\t"
NAMES = ["赵明轩", "钱雨桐", "孙浩然", "李思远", "周子墨", "吴梓萱", "郑可欣", "王嘉怡", "冯俊杰", "陈诗涵", "褚亦凡", "卫雨泽", "蒋文博", "沈佳琪", "韩宇航", "杨梦琪",
         "朱景行", "秦若曦", "尤子睿", "许安琪", "何泽宇", "吕欣怡", "施博文", "张雅琳", "孔令辉", "曹梓涵", "严子轩", "华美玲", "金宇辰", "魏书瑶", "陶可馨", "姜明哲",
         "戚雅静", "谢承泽", "邹梓萌", "喻思彤", "柏文轩", "水清扬", "窦嘉树", "章若彤", "云天佑", "苏锦程", "潘语嫣", "葛浩宇", "奚晓彤", "范志远", "彭思雨", "郎嘉盛",
         "鲁艺菲", "韦承志", "昌雨欣", "马铭泽", "苗雅茜", "凤梓豪", "花沐辰", "方子涵", "俞悦然", "任星辰", "袁梦洁", "柳青禾", "鲍明远", "史若兰", "唐煜城", "费知远",
         "廉思齐", "岑安然", "薛慕白", "雷振宇", "贺兰心", "倪清和", "汤景明", "滕思哲", "殷晓棠", "罗安阳", "毕文昊", "郝雨辰", "邬静怡", "安子衿", "常乐融", "乐知夏"]

# ================================================================== M9a: several tables

# 9321 club attendance, top-1 group, two turns
case("tab-9321", sub="M9a", tt="rank", topic="clubattend", root="社团活动", names=["9月.txt", "10月.txt", "11月.txt"], sep=T,
     cols=["日期", "社团", "状态", "人数"], rows=(110, 150), readme_name="说明.md", min=1,
     readme=["# 社团活动签到说明", "", "每月一个文件，制表符分隔：日期、社团、状态、人数。", "社团按完整名称区分：「吉他社」和「吉他社(预备)」是两个社团。状态按完整内容匹配：「到场(补签)」是事后补录，「缺席(请假)」是请过假的，它们不算「到场」「缺席」。"],
     gen=lambda rng, i, fi, n: [f"2026-{9 + fi:02d}-{rng.randint(1, 28):02d}", choice(rng, ["吉他社", "吉他社(预备)", "街舞社", "摄影社", "棋牌社"], [4, 3, 4, 3, 3]),
                                choice(rng, ["到场", "到场", "到场", "缺席", "到场(补签)", "缺席(请假)"]), str(rng.randint(3, 40))],
     desc="Two turns over three monthly club tables: the club with the most attendees, then the club with the most absentees, with look-alike statuses and a look-alike club name",
     why="社团 and 状态 are whole-value columns of the tab-separated tables.",
     queries=[
         dict(prompt="三个月的社团签到记录里，状态为「到场」的人数合计最多的是哪个社团？口径见 社团活动/说明.md，回复社团名和它的到场人数合计。", agg="top", group="社团", col="人数", margin=8,
              pred='r["状态"]=="到场"', decoy=dict(pred='r["状态"].startswith("到场")'), decoy_note="状态前缀匹配，含到场(补签)",
              cmd="""cat 社团活动/*.txt | awk -F'\\t' '$3=="到场" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1""", unit="到场人数合计最多的是{v}，共 {n} 人。", alts=[]),
         dict(prompt="那缺席人数合计最多的社团又是哪个？同样给出人数合计。", agg="top", group="社团", col="人数", margin=8,
              pred='r["状态"]=="缺席"', decoy=dict(pred='r["状态"].startswith("缺席")'), decoy_note="状态前缀匹配，含缺席(请假)",
              cmd="""cat 社团活动/*.txt | awk -F'\\t' '$3=="缺席" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1""", unit="缺席人数合计最多的是{v}，共 {n} 人。",
              alts=["缺席的人数加起来最多的是哪个社团？", "三个月里状态是缺席的人数合计，哪个社团排第一？", "按说明.md的口径，缺席人数最多的社团是谁？", "把状态为缺席的人数按社团汇总，最高的是哪个社团？", "请假缺席不算，缺席人数总和最大的社团是哪个？"]),
     ])

# 9322 ride dispatch, distinct, two turns
case("log-9322", sub="M9a", tt="count_events", topic="dispatchdrivers", root="派单", names=["周一.txt", "周二.txt", "周三.txt", "周四.txt"], sep=" ",
     cols=["时间", "司机", "城区", "结果"], rows=(120, 170), readme_name="说明.md", min=20, header=False,
     readme=["# 派单记录说明", "", "每天一个文件，空格分隔，没有表头：时间 司机 城区 结果。", "城区、结果都按完整内容匹配：「东城新区」不是「东城」，「拒单(系统)」是系统自动拒绝，不算司机的「拒单」。"],
     gen=lambda rng, i, fi, n: [f"101{fi}T{rng.randint(6, 23):02d}{rng.randint(0, 59):02d}", f"D{rng.randint(1001, 1260)}",
                                choice(rng, ["东城", "东城", "东城新区", "西城", "南湾", "北辰"]), choice(rng, ["接单", "接单", "拒单", "拒单(系统)", "超时"])],
     desc="Two turns over four daily dispatch logs: distinct drivers who accepted orders in one district, then distinct drivers who declined there, with look-alike district and result values",
     why="城区 and 结果 are whole-value columns; drivers are de-duplicated across the four files.",
     queries=[
         dict(prompt="四天的派单记录里，在「东城」接过单的司机一共有多少位（同一位只算一次）？口径见 派单/说明.md。", agg="distinct", col="司机",
              pred='r["城区"]=="东城" and r["结果"]=="接单"', decoy=dict(pred='"东城" in r["城区"] and r["结果"].startswith("接单")'), decoy_note="城区包含东城、结果前缀匹配",
              cmd="""cat 派单/*.txt | awk '$3=="东城" && $4=="接单" {print $2}' | sort -u | wc -l""", unit="东城接过单的不同司机共 {v} 位。", alts=[]),
         dict(prompt="同样在东城，拒单的司机又有多少位？", agg="distinct", col="司机",
              pred='r["城区"]=="东城" and r["结果"]=="拒单"', decoy=dict(pred='"东城" in r["城区"] and r["结果"].startswith("拒单")'), decoy_note="城区包含东城、结果前缀匹配，含拒单(系统)",
              cmd="""cat 派单/*.txt | awk '$3=="东城" && $4=="拒单" {print $2}' | sort -u | wc -l""", unit="东城拒单的不同司机共 {v} 位。",
              alts=["东城区拒过单的司机有几位？", "四天里城区为东城、结果为拒单的不同司机数量。", "按说明.md，东城拒单的司机去重后是多少人？", "在东城拒绝过订单的司机共有多少位？", "统计东城拒单记录涉及的不同司机人数。"]),
     ])



def rint(rng, lo, hi, step=1):
    return rng.randrange(lo, hi + 1, step)


# 9323 cold rooms, min with tie rule (date), English
case("tab-9323", sub="M9a", tt="rank", topic="coldroommin", root="coldchain", names=["week1.dat", "week2.dat", "week3.dat"], sep=";",
     cols=["date", "unit", "temp_c", "operator"], rows=(120, 160), readme_name="README.md", min=1, header=True,
     readme=["# Cold room logs", "", "One file per week, semicolon separated: date;unit;temp_c;operator (integer degrees).", "Unit codes are whole values: `CR-10` is a different room from `CR-1`.", "When several readings share the lowest temperature, report the earliest date among them."],
     gen=lambda rng, i, fi, n: (lambda u: [f"2026-09-{fi * 7 + rng.randint(1, 7):02d}", u, str({"CR-1": rint(rng, -24, -15), "CR-10": rint(rng, -30, -18)}.get(u, rint(rng, -20, -5))), choice(rng, ["Ana", "Ben", "Chi", "Dev"])])(
         choice(rng, ["CR-1", "CR-1", "CR-10", "CR-2", "CR-3"])),
     desc="Finds on which date cold room CR-1 reached its lowest temperature across three weekly tables, with tied readings broken by the README and a look-alike room code that ran colder",
     why="unit is a whole-value column; the lowest reading is shared by several rows and the README picks the earliest date.",
     queries=[dict(prompt="On which date did cold room CR-1 record its lowest temperature across the three weekly files? coldchain/README.md says how to break ties; reply with the date and the total number of CR-1 readings in the three files.", agg="argtie", extreme="min", col="temp_c", ret="date", tie_col="date", tie_pick="min",
                   pred='r["unit"]=="CR-1"', decoy=dict(pred='r["unit"].startswith("CR-1")'), decoy_note="unit prefix match, includes CR-10",
                   cmd="""cat coldchain/*.dat | awk -F';' '$2=="CR-1" {print $3, $1}' | sort -k1,1n -k2,2 | head -1""", cmd2="""cat coldchain/*.dat | awk -F';' '$2=="CR-1"' | wc -l""", unit="CR-1 reached its lowest temperature on {v}; CR-1 has {n} readings in total.",
                   alts=["Which date has the minimum temperature for room CR-1 in coldchain/? Break ties as the README says.", "When was CR-1 coldest? Give the date, using the README's tie rule.", "Across the weekly cold room logs, on what date does CR-1 hit its lowest reading?", "Find the date of the lowest CR-1 temperature (earliest date if tied).", "CR-1's coldest reading: which date was it taken?"])])

# 9324 school sports, max with tie rule (smallest entry number), two turns
case("tab-9324", sub="M9a", tt="rank", topic="trackfield", root="校运会", names=["初赛.txt", "复赛.txt", "决赛.txt"], sep=T,
     cols=["报名号", "姓名", "项目", "成绩cm"], rows=(150, 200), readme_name="说明.md", min=1,
     readme=["# 校运会成绩说明", "", "每轮一个文件，制表符分隔：报名号、姓名、项目、成绩（厘米，5 的倍数）。", "项目按完整名称匹配：「立定跳远」「三级跳远」都不是「跳远」。", "最好成绩有多人并列时，取报名号最小的那位。"],
     gen=lambda rng, i, fi, n: (lambda a, ev: [f"B{a:03d}", NAMES[a - 1], ev, str({"跳远": rint(rng, 480, 650, 5), "立定跳远": rint(rng, 180, 300, 5), "三级跳远": rint(rng, 900, 1400, 5)}.get(ev, rint(rng, 700, 1300, 5)))])(
         rng.randint(1, 80), choice(rng, ["跳远", "跳远", "立定跳远", "立定跳远", "三级跳远", "铅球"])),
     desc="Two turns over three round tables: the long-jump best's athlete with ties broken by the smallest entry number, then the standing-jump best, with look-alike event names",
     why="项目 is a whole-value column; the best mark is shared by several athletes and the README picks the smallest entry number.",
     queries=[
         dict(prompt="三轮比赛里，「跳远」项目成绩最好的是哪位选手？并列时按 校运会/说明.md 的规则取，回复姓名，并说明跳远项目一共有多少条成绩记录。", agg="argtie", extreme="max", col="成绩cm", ret="姓名", tie_col="报名号", tie_pick="min",
              pred='r["项目"]=="跳远"', decoy=dict(pred='"跳远" in r["项目"]'), decoy_note="项目包含跳远，含立定跳远、三级跳远",
              cmd="""cat 校运会/*.txt | awk -F'\\t' '$3=="跳远" {print $4, $1, $2}' | sort -k1,1nr -k2,2 | head -1""", cmd2="""cat 校运会/*.txt | awk -F'\\t' '$3=="跳远"' | wc -l""", unit="跳远成绩最好的是{v}，跳远共有 {n} 条成绩记录。", alts=[]),
         dict(prompt="那「立定跳远」成绩最好的选手呢？并列规则一样，也告诉我立定跳远一共有多少条成绩记录。", agg="argtie", extreme="max", col="成绩cm", ret="姓名", tie_col="报名号", tie_pick="min",
              pred='r["项目"]=="立定跳远"', decoy=dict(pred='"跳远" in r["项目"]'), decoy_note="项目包含跳远，含跳远和三级跳远",
              cmd="""cat 校运会/*.txt | awk -F'\\t' '$3=="立定跳远" {print $4, $1, $2}' | sort -k1,1nr -k2,2 | head -1""", cmd2="""cat 校运会/*.txt | awk -F'\\t' '$3=="立定跳远"' | wc -l""", unit="立定跳远成绩最好的是{v}，立定跳远共有 {n} 条成绩记录。",
              alts=["立定跳远这个项目谁的成绩最高？并列取报名号小的。", "三轮成绩里立定跳远的最好成绩是谁创造的？", "按说明.md的并列规则，立定跳远冠军是哪位选手？", "项目为立定跳远的记录中，最高成绩对应的选手姓名。", "立定跳远最远的是谁？成绩相同取报名号最小者。"]),
     ])

# 9325 cloud bill, sum with case look-alike
case("tab-9325", sub="M9a", tt="aggregate", topic="cloudproject", root="云账单", names=["8月.txt", "9月.txt", "10月.txt"], sep=",",
     cols=["日期", "项目", "服务", "费用元"], rows=(120, 170), readme_name="说明.md", header=True,
     readme=["# 云账单说明", "", "每月一个文件，逗号分隔：日期、项目、服务、费用（元，整数）。", "项目名区分大小写：「API」是另一个团队的项目，和「api」分开结算。"],
     gen=lambda rng, i, fi, n: [f"2026{8 + fi:02d}{rng.randint(1, 28):02d}", choice(rng, ["api", "api", "API", "web", "batch"]), choice(rng, ["计算", "存储", "网络", "数据库"]), str(rng.randint(3, 900))],
     desc="Sums the cloud cost of project api over three monthly bills where a project named API in capitals is a look-alike",
     why="项目 is a case-sensitive whole-value column.",
     queries=[dict(prompt="8 到 10 月的云账单里，项目 api（小写）的费用一共多少元？口径见 云账单/说明.md，回复数字。", agg="sum", col="费用元", pred='r["项目"]=="api"', decoy=dict(pred='r["项目"].lower()=="api"'), decoy_note="忽略大小写，含API",
                   cmd="""cat 云账单/*.txt | awk -F, '$2=="api" {s+=$4} END{print s}'""", unit="项目 api 三个月合计 {v} 元。",
                   alts=["小写 api 项目这三个月花了多少钱？", "云账单里项目名恰好是 api 的费用加起来是多少元？", "按说明.md，api（不含 API）的费用总额是多少？", "统计项目列等于 api 的费用元之和。", "8、9、10 月 api 项目的账单合计多少元？"])])

# 9326 crash reports, distinct devices, English
case("log-9326", sub="M9a", tt="count_events", topic="crashdevices", root="crashes", names=["w1.txt", "w2.txt", "w3.txt"], sep=",",
     cols=["time", "build", "device", "event"], rows=(130, 180), readme_name="README.md", min=10, header=False,
     readme=["# Crash feed", "", "One file per week, comma separated, no header: time,build,device,event.", "Build and event are whole values: build `4.2.0-rc1` is a release candidate, and `crash-handled` was caught by the app and did not close it, so it is not a `crash`."],
     gen=lambda rng, i, fi, n: [f"202610{fi * 7 + rng.randint(1, 7):02d}T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", choice(rng, ["4.2.0", "4.2.0", "4.2.0-rc1", "4.1.9", "4.2.1"]),
                                f"{choice(rng, ['Pixel', 'Galaxy', 'Redmi', 'Xperia', 'Moto'])}-{choice(rng, list('ABCDEFGHIJ'))}", choice(rng, ["crash", "crash", "crash-handled", "launch", "launch", "anr"])],
     desc="Counts distinct device models that crashed on one app build across three weekly feeds where a release-candidate build and a handled-crash event are look-alikes",
     why="build and event are whole-value columns; device models are de-duplicated across files.",
     queries=[dict(prompt="How many different device models had a crash on build 4.2.0 across the three weekly feeds? crashes/README.md defines what counts; reply with the number.", agg="distinct", col="device",
                   pred='r["build"]=="4.2.0" and r["event"]=="crash"', decoy=dict(pred='r["build"].startswith("4.2.0") and r["event"].startswith("crash")'), decoy_note="prefix match on build and event",
                   cmd="""cat crashes/*.txt | awk -F, '$2=="4.2.0" && $4=="crash" {print $3}' | sort -u | wc -l""", unit="{v} distinct device models crashed on 4.2.0.",
                   alts=["Count the unique devices with event crash on build 4.2.0.", "How many distinct device models crashed on 4.2.0 (rc builds excluded)?", "Across the weekly crash feeds, number of different models with a real crash on build 4.2.0.", "Per crashes/README.md, how many device models hit a crash on 4.2.0?", "De-duplicated device count for build 4.2.0 and event crash."])])

# 9327 metro exits, top-1 by sum
case("tab-9327", sub="M9a", tt="rank", topic="metroexit", root="地铁客流", names=["周一.txt", "周二.txt", "周三.txt", "周四.txt", "周五.txt"], sep=";",
     cols=["时段", "站名", "方向", "人数"], rows=(90, 120), readme_name="说明.md", min=1, header=False,
     readme=["# 地铁客流说明", "", "每个工作日一个文件，分号分隔，没有表头：时段;站名;方向;人数。", "站名按完整名称区分：「人民广场」和「人民广场(东)」是两个出入口。方向按完整内容匹配：「出站(换乘)」是站内换乘，不算「出站」。"],
     gen=lambda rng, i, fi, n: [f"{rng.randint(6, 22):02d}{rng.choice(['00', '30'])}", choice(rng, ["人民广场", "人民广场(东)", "火车站", "大学城", "体育中心", "南京路"], [3, 3, 4, 4, 3, 3]),
                                choice(rng, ["进站", "进站", "出站", "出站", "出站(换乘)"]), str(rng.randint(20, 400))],
     desc="Finds the station with the most exit passengers over five weekday tables where a transfer direction and a twin gate name are look-alikes",
     why="站名 and 方向 are whole-value columns of the semicolon-separated tables.",
     queries=[dict(prompt="这一周五天里，方向为「出站」的人数合计最多的是哪个站？口径见 地铁客流/说明.md，回复站名和它的出站人数合计。", agg="top", group="站名", col="人数", margin=40,
                   pred='r["方向"]=="出站"', decoy=dict(pred='r["方向"].startswith("出站")'), decoy_note="方向前缀匹配，含出站(换乘)",
                   cmd="""cat 地铁客流/*.txt | awk -F';' '$3=="出站" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1""", unit="出站人数合计最多的是{v}，合计 {n} 人。",
                   alts=["五天里出站客流最大的站是哪个？", "按说明.md，出站人数加起来最高的站名是什么？", "哪个站的出站人数总和排第一（换乘不算）？", "统计方向列恰好是出站的人数，按站名汇总后最多的是谁？", "周一到周五，出站旅客最多的站点。"])])

# 9328 wind gusts, max with tie rule (latest timestamp), English
case("tab-9328", sub="M9a", tt="rank", topic="gustpeak", root="gusts", names=["day1.dat", "day2.dat", "day3.dat"], sep=" ",
     cols=["time", "station", "gust_kmh"], rows=(120, 160), readme_name="README.md", min=1, header=False,
     readme=["# Gust readings", "", "One file per day, space separated, no header: time station gust_kmh (integer).", "Station codes are whole values: `N-12` is not `N-120` or `N-21`.", "When several readings share the highest gust, report the latest time among them."],
     gen=lambda rng, i, fi, n: (lambda s: [f"2026-10-{fi + 1:02d}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}", s, str({"N-12": rint(rng, 30, 95), "N-120": rint(rng, 40, 130)}.get(s, rint(rng, 20, 90)))])(
         choice(rng, ["N-12", "N-12", "N-120", "N-21", "S-04"])),
     desc="Finds the time of the strongest gust at station N-12 over three daily tables, with tied readings broken by the latest time and a look-alike station code that blew harder",
     why="station is a whole-value column; the peak value is shared by several rows and the README picks the latest time.",
     queries=[dict(prompt="At what time was the strongest gust at station N-12 across the three daily files? gusts/README.md says how to break ties; reply with the timestamp and the total number of N-12 readings.", agg="argtie", extreme="max", col="gust_kmh", ret="time", tie_col="time", tie_pick="max",
                   pred='r["station"]=="N-12"', decoy=dict(pred='r["station"].startswith("N-12")'), decoy_note="station prefix match, includes N-120",
                   cmd="""cat gusts/*.dat | awk '$2=="N-12" {print $3, $1}' | sort -k1,1nr -k2,2r | head -1""", cmd2="""cat gusts/*.dat | awk '$2=="N-12"' | wc -l""", unit="The strongest N-12 gust was at {v}; N-12 has {n} readings in total.",
                   alts=["When did N-12 record its peak gust? Use the README's tie rule.", "Timestamp of the highest gust for station N-12 in gusts/ (latest one if tied).", "Which time shows the maximum gust_kmh for N-12 over the three days?", "Find the moment of N-12's top gust, breaking ties as the README says.", "Across day1 to day3, what is the timestamp of the strongest N-12 reading?"])])

# 9329 parcel lockers, count with whole-line decoy
case("tab-9329", sub="M9a", tt="filter_count", topic="lockerpick", root="快递柜", names=["一号楼.txt", "二号楼.txt", "三号楼.txt", "四号楼.txt"], sep=T,
     cols=["日期", "柜号", "格口", "备注"], rows=(110, 150), readme_name="说明.md", min=20, header=True,
     readme=["# 快递柜取件记录说明", "", "每栋楼一个文件，制表符分隔：日期、柜号、格口、备注。", "统计某个柜的取件，只看「柜号」这一列、按完整内容匹配：「B30」是另一个柜；备注里提到的柜号只是提示，不代表取件发生在那个柜。"],
     gen=lambda rng, i, fi, n: (lambda c: [f"2026100{fi + 1}", c, f"{c}-{rng.randint(1, 40):02d}", choice(rng, ["-", "-", "-", "转B3柜", "超时", "-"])])(
         choice(rng, ["A1", "A2", "B1", "B2", "B3", "B3", "B30", "C1"])),
     desc="Counts pickups from locker B3 over four building tables where a longer locker code and a remarks column mentioning B3 are look-alikes",
     why="柜号 is a whole-value column; B3 elsewhere in the line does not count.",
     queries=[dict(prompt="四栋楼的取件记录里，柜号为 B3 的取件一共有多少条？口径见 快递柜/说明.md。", agg="count", pred='r["柜号"]=="B3"', decoy=dict(pred='"B3" in "".join(r.values())'), decoy_note="整行包含B3，含B30和备注",
                   cmd="""cat 快递柜/*.txt | awk -F'\\t' '$2=="B3"' | wc -l""", unit="B3 柜共有 {v} 条取件记录。",
                   alts=["B3 柜被取了多少次件？", "统计柜号列恰好等于 B3 的记录条数。", "按说明.md，四栋楼里 B3 柜的取件记录有几条？", "快递柜记录中柜号是 B3（不是 B30）的行数。", "四个文件合计，B3 柜的取件次数是多少？"])])

# 9330 printers, distinct users
case("log-9330", sub="M9a", tt="count_events", topic="jamusers", root="打印日志", names=["一楼.txt", "二楼.txt", "三楼.txt"], sep=" ",
     cols=["时间", "打印机", "用户", "事件"], rows=(130, 170), readme_name="说明.md", min=8, header=False,
     readme=["# 打印日志说明", "", "每层楼一个文件，空格分隔，没有表头：时间 打印机 用户 事件。", "打印机、事件都按完整内容匹配：「P2-彩色」是另一台机器，「卡纸(已清除)」是用户自己清掉的，不算「卡纸」。"],
     gen=lambda rng, i, fi, n: [f"1012T{rng.randint(8, 18):02d}{rng.randint(0, 59):02d}", choice(rng, ["P2", "P2", "P2-彩色", "P3", "P1"]), f"u{rng.randint(100, 260)}",
                                choice(rng, ["完成", "完成", "完成", "卡纸", "卡纸(已清除)", "缺纸"])],
     desc="Counts distinct users who hit a paper jam on printer P2 over three floor logs where a colour twin printer and a self-cleared jam are look-alikes",
     why="打印机 and 事件 are whole-value columns; users are de-duplicated across floors.",
     queries=[dict(prompt="三层楼的打印日志里，打印机 P2 报过「卡纸」的用户有多少位（同一位只算一次）？口径见 打印日志/说明.md。", agg="distinct", col="用户",
                   pred='r["打印机"]=="P2" and r["事件"]=="卡纸"', decoy=dict(pred='r["打印机"].startswith("P2") and r["事件"].startswith("卡纸")'), decoy_note="打印机和事件都用前缀匹配",
                   cmd="""cat 打印日志/*.txt | awk '$2=="P2" && $4=="卡纸" {print $3}' | sort -u | wc -l""", unit="P2 卡纸涉及 {v} 位不同的用户。",
                   alts=["P2 这台打印机卡纸，涉及多少个不同用户？", "三层楼里，在 P2 上遇到卡纸的用户去重后是多少人？", "按说明.md，打印机为 P2、事件为卡纸的不同用户数。", "有多少位用户在 P2 上发生过卡纸（自己清除的不算）？", "统计 P2 卡纸记录里不重复的用户个数。"])])

# 9331 timesheets, top-1 billable hours, English
case("tab-9331", sub="M9a", tt="rank", topic="billablehours", root="timesheets", names=["jan.txt", "feb.txt", "mar.txt"], sep=",",
     cols=["date", "engineer", "type", "hours"], rows=(90, 120), readme_name="README.md", min=1, header=True,
     readme=["# Timesheets", "", "One file per month, comma separated: date,engineer,type,hours (integer hours).", "Only type `BILL` is billable. `BILL-WAIVED` was written off before invoicing, so it does not count."],
     gen=lambda rng, i, fi, n: [f"2026{1 + fi:02d}{rng.randint(1, 28):02d}", choice(rng, ["Aiko", "Bruno", "Chloe", "Dmitri", "Elena", "Farid", "Greta", "Hugo"]),
                                choice(rng, ["BILL", "BILL", "BILL-WAIVED", "INTERNAL", "LEAVE"]), str(rng.randint(1, 10))],
     desc="Finds the engineer with the most billable hours over three monthly timesheets where a written-off type shares the prefix",
     why="type is a whole-value column; the leader is ahead by at least six hours.",
     queries=[dict(prompt="Which engineer logged the most billable hours (type BILL) over the three monthly files? timesheets/README.md has the rules; reply with the name and that engineer's billable hours.", agg="top", group="engineer", col="hours", margin=6,
                   pred='r["type"]=="BILL"', decoy=dict(pred='r["type"].startswith("BILL")'), decoy_note="type prefix match, includes BILL-WAIVED",
                   cmd="""cat timesheets/*.txt | awk -F, '$3=="BILL" {s[$2]+=$4} END{for (k in s) print s[k], k}' | sort -rn | head -1""", unit="{v} logged the most billable hours ({n}).",
                   alts=["Who has the highest total of BILL hours in timesheets/?", "Name the engineer with the largest billable-hours total, per the README.", "Across January to March, which engineer billed the most hours?", "Top engineer by hours where type is exactly BILL.", "Which person leads on billable hours (written-off time excluded)?"])])

# 9332 purchase ledger, sum with two columns
case("tab-9332", sub="M9a", tt="aggregate", topic="supplierpaid", root="采购台账", names=["7月.dat", "8月.dat", "9月.dat"], sep=";",
     cols=["日期", "供应商", "状态", "金额元"], rows=(100, 140), readme_name="说明.md", header=True,
     readme=["# 采购台账说明", "", "每月一个文件，分号分隔：日期;供应商;状态;金额（元，整数）。", "供应商、状态都按完整内容匹配：「华兴科技」是另一家公司，「已付款(部分)」只付了一部分，还没结清，不算「已付款」。"],
     gen=lambda rng, i, fi, n: [f"2026{7 + fi:02d}{rng.randint(1, 28):02d}", choice(rng, ["华兴", "华兴", "华兴科技", "宏远", "瑞泰"]), choice(rng, ["已付款", "已付款", "已付款(部分)", "待付", "已退款"]), str(rng.randint(200, 9800))],
     desc="Sums the paid amount for one supplier over three monthly ledgers where a longer supplier name and a part-paid status are look-alikes",
     why="供应商 and 状态 are whole-value columns.",
     queries=[dict(prompt="7 到 9 月的采购台账里，供应商「华兴」状态为「已付款」的金额一共多少元？口径见 采购台账/说明.md。", agg="sum", col="金额元", pred='r["供应商"]=="华兴" and r["状态"]=="已付款"',
                   decoy=dict(pred='"华兴" in r["供应商"] and r["状态"].startswith("已付款")'), decoy_note="供应商包含华兴、状态前缀匹配",
                   cmd="""cat 采购台账/*.dat | awk -F';' '$2=="华兴" && $3=="已付款" {s+=$4} END{print s}'""", unit="华兴已付款合计 {v} 元。",
                   alts=["华兴这三个月已经付清的采购金额合计多少？", "供应商是华兴、状态是已付款的金额加起来是多少元？", "按说明.md，华兴（不含华兴科技）已付款总额。", "三个月台账中华兴已付款的金额总和。", "统计供应商列等于华兴且状态列等于已付款的金额元之和。"])])


# ================================================================== M9c: one long file

MSG_ZH = ["依赖解析完成_缓存命中率正常", "编译单元已加入增量构建队列", "镜像层复用成功_跳过基础层重建", "静态检查完成_无新增告警", "产物签名校验通过_准备上传制品库",
          "测试报告已归档到共享存储", "配置快照已写入发布目录", "探针检测到实例响应时间波动", "连接池扩容请求已提交", "健康检查间隔调整完成"]


def rel_gen(rng, i, fi, n):
    ro, rc, wo, wc = int(n * 0.10), int(n * 0.22), int(n * 0.45), int(n * 0.62)
    stamp = f"1009T{(8 * 3600 + i * 17) // 3600 % 24:02d}{(8 * 3600 + i * 17) // 60 % 60:02d}"
    marks = {ro: "灰度发布开始(演练)", rc: "灰度发布结束(演练)", wo: "灰度发布开始", wc: "灰度发布结束"}
    if i in marks:
        return [stamp, "MARK", "release", marks[i]]
    lvl = choice(rng, ["INFO", "INFO", "INFO", "WARN", "WARN-SLOW", "ERROR", "ERROR-RETRY"], [30, 30, 30, 8, 5, 9, 5])
    return [stamp, lvl, choice(rng, ["gateway", "worker", "cache", "deploy"]), choice(rng, MSG_ZH)]


# 9333 release log, count between markers, two turns
case("log-9333", sub="M9c", tt="time_window", topic="canarywindow", root="发布", names=["release.txt"], sep=T,
     cols=["时间", "级别", "模块", "信息"], header=False, rows=(1150, 1250), readme_name="说明.md", min=5, gen=rel_gen,
     readme=["# 发布日志说明", "", "release.txt 是一次发布的完整输出，制表符分隔，没有表头：时间、级别、模块、信息，按时间顺序追加。", "级别为 MARK 的行是窗口标记，不是普通日志。真正的灰度窗口从「灰度发布开始」到「灰度发布结束」；带「(演练)」的是演练标记，不算窗口。", "级别按完整内容匹配：「ERROR-RETRY」「WARN-SLOW」不等于「ERROR」「WARN」。"],
     desc="Two turns over one long release log: ERROR lines inside the real canary window, then WARN lines inside it, with a rehearsal window and look-alike levels",
     why="The window is delimited by two exact MARK rows and levels are whole values.",
     queries=[
         dict(prompt="发布/release.txt 里，「灰度发布开始」和「灰度发布结束」之间有多少条 ERROR 日志？窗口怎么认见 发布/说明.md。", agg="between", nth=1, start='r["级别"]=="MARK" and r["信息"]=="灰度发布开始"', end='r["级别"]=="MARK" and r["信息"]=="灰度发布结束"',
              pred='r["级别"]=="ERROR"', decoy=dict(start='r["信息"].startswith("灰度发布开始")', end='r["信息"].startswith("灰度发布结束")', pred='r["级别"].startswith("ERROR")'), decoy_note="第一个开始标记是演练、级别前缀匹配",
              cmd="""awk -F'\\t' '$2=="MARK" && $4=="灰度发布开始" {on=1; next} $2=="MARK" && $4=="灰度发布结束" {on=0} on && $2=="ERROR" {c++} END{print c+0}' 发布/release.txt""", unit="灰度窗口内有 {v} 条 ERROR。", alts=[]),
         dict(prompt="同一个窗口里，WARN 级别的日志又有多少条？", agg="between", nth=1, start='r["级别"]=="MARK" and r["信息"]=="灰度发布开始"', end='r["级别"]=="MARK" and r["信息"]=="灰度发布结束"',
              pred='r["级别"]=="WARN"', decoy=dict(start='r["信息"].startswith("灰度发布开始")', end='r["信息"].startswith("灰度发布结束")', pred='r["级别"].startswith("WARN")'), decoy_note="第一个开始标记是演练、级别前缀匹配",
              cmd="""awk -F'\\t' '$2=="MARK" && $4=="灰度发布开始" {on=1; next} $2=="MARK" && $4=="灰度发布结束" {on=0} on && $2=="WARN" {c++} END{print c+0}' 发布/release.txt""", unit="灰度窗口内有 {v} 条 WARN。",
              alts=["灰度窗口里 WARN 日志的条数。", "开始到结束之间级别是 WARN 的有几行？", "按说明.md，真正的灰度窗口内 WARN 一共多少条？", "release.txt 灰度发布期间的 WARN 数量（WARN-SLOW 不算）。", "同样的窗口，统计级别恰好为 WARN 的行数。"]),
     ])


def maint_gen(rng, i, fi, n):
    marks = {int(n * 0.05): "WINDOW-OPEN-DRYRUN", int(n * 0.09): "WINDOW-CLOSE-DRYRUN", int(n * 0.28): "WINDOW-OPEN", int(n * 0.40): "WINDOW-CLOSE",
             int(n * 0.62): "WINDOW-OPEN", int(n * 0.80): "WINDOW-CLOSE"}
    stamp = f"1011T{(i * 23) // 3600 % 24:02d}{(i * 23) // 60 % 60:02d}"
    if i in marks:
        return [stamp, "MARK", "scheduler", marks[i]]
    return [stamp, choice(rng, ["INFO", "INFO", "INFO", "INFO", "WARN", "ERR", "ERR", "ERR-RETRY"], [30, 30, 30, 30, 8, 8, 8, 5]),
            choice(rng, ["db", "queue", "cache", "web"]), choice(rng, ["checkpoint-written", "replica-lag-recovered", "index-rebuild-step-done", "connection-recycled", "snapshot-uploaded", "gc-pause-observed", "lease-renewed"])]


# 9334 maintenance events, nth window, English, two turns
case("log-9334", sub="M9c", tt="time_window", topic="maintwindow", root="maint", names=["events.txt"], sep=" ",
     cols=["time", "level", "svc", "msg"], header=False, rows=(1200, 1300), readme_name="README.md", min=5, gen=maint_gen,
     readme=["# Maintenance events", "", "events.txt is append-only, space separated, no header: time level svc msg.", "Rows with level MARK are scheduler markers. A maintenance window runs from a `WINDOW-OPEN` marker to the next `WINDOW-CLOSE`; the `-DRYRUN` markers belong to a rehearsal and are not windows.", "Levels are whole values: `ERR-RETRY` is not `ERR`."],
     desc="Two turns over one long maintenance event file: the number of lines inside the second real window, then the ERR lines inside it, with a rehearsal window that shifts the count",
     why="Windows are delimited by exact marker rows and the second real window is unambiguous once the dry run is excluded.",
     queries=[
         dict(prompt="In maint/events.txt, how many lines are logged between the second WINDOW-OPEN marker and the WINDOW-CLOSE that follows it? maint/README.md explains which markers count; reply with the number.", agg="between", nth=2,
              start='r["level"]=="MARK" and r["msg"]=="WINDOW-OPEN"', end='r["level"]=="MARK" and r["msg"]=="WINDOW-CLOSE"', pred="True",
              decoy=dict(start='r["level"]=="MARK" and r["msg"].startswith("WINDOW-OPEN")', end='r["level"]=="MARK" and r["msg"].startswith("WINDOW-CLOSE")'), decoy_note="dry-run markers counted, so the second open is the first real window",
              cmd="""awk '$2=="MARK" && $4=="WINDOW-OPEN" {k++; if (k==2) on=1; next} $2=="MARK" && $4=="WINDOW-CLOSE" {on=0} on {c++} END{print c+0}' maint/events.txt""", unit="{v} lines fall inside the second window.", alts=[]),
         dict(prompt="And inside that same window, how many of those lines have level ERR?", agg="between", nth=2,
              start='r["level"]=="MARK" and r["msg"]=="WINDOW-OPEN"', end='r["level"]=="MARK" and r["msg"]=="WINDOW-CLOSE"', pred='r["level"]=="ERR"',
              decoy=dict(start='r["level"]=="MARK" and r["msg"].startswith("WINDOW-OPEN")', end='r["level"]=="MARK" and r["msg"].startswith("WINDOW-CLOSE")', pred='r["level"].startswith("ERR")'), decoy_note="dry-run markers counted and level prefix match",
              cmd="""awk '$2=="MARK" && $4=="WINDOW-OPEN" {k++; if (k==2) on=1; next} $2=="MARK" && $4=="WINDOW-CLOSE" {on=0} on && $2=="ERR" {c++} END{print c+0}' maint/events.txt""", unit="{v} ERR lines fall inside the second window.",
              alts=["Number of ERR-level lines in the second maintenance window.", "Between the second open and its close, count rows whose level is exactly ERR.", "How many ERR events happened during the second real window?", "In the second window of events.txt, how many lines are ERR (not ERR-RETRY)?", "Count the ERR lines inside the window that starts at the second WINDOW-OPEN."]),
     ])

CITY_ROADS = ["解放路", "中山路", "人民路", "建设路", "新华路", "和平路", "文化路", "朝阳路"]


def addr(rng):
    return f"{rng.choice(['杭州', '成都', '武汉', '西安', '长沙'])}市{rng.choice(CITY_ROADS)}{rng.randint(1, 300)}号{rng.choice(['东门', '西门', '南门'])}-{rng.randint(1, 30)}栋"


# 9335 sales orders, top-1 customer in one long file
case("tab-9335", sub="M9c", tt="rank", topic="orderleader", root="销售", names=["订单.txt"], sep=T,
     cols=["订单号", "客户", "状态", "金额元", "收货地址"], header=True, rows=(1250, 1350), readme_name="说明.md", min=1,
     readme=["# 销售订单说明", "", "订单.txt 是整季度的订单明细，制表符分隔：订单号、客户、状态、金额（元，整数）、收货地址，第一行是表头。", "客户按完整名称区分：「恒达贸易」和「恒达贸易(深圳)」是两家公司。状态按完整内容匹配：「已付款(部分)」还没结清，不算「已付款」。"],
     gen=lambda rng, i, fi, n: [f"SO{i + 1:05d}", choice(rng, ["恒达贸易", "恒达贸易(深圳)", "鼎盛实业", "嘉禾食品", "远航物流", "星河科技", "明德教育", "蓝海渔业", "金穗农业", "北辰电子", "松泰建材", "安和医药"], [3, 3, 4, 4, 3, 5, 3, 3, 3, 3, 4, 3]),
                                choice(rng, ["已付款", "已付款", "已付款(部分)", "待付款", "已取消"]), str(rng.randint(200, 9800)), addr(rng)],
     desc="Finds the customer with the highest paid-order total in one long order file where a part-paid status and a twin customer name are look-alikes",
     why="客户 and 状态 are whole-value columns; the leader is ahead by at least 500 yuan.",
     queries=[dict(prompt="销售/订单.txt 里，状态为「已付款」的订单金额合计最高的是哪个客户？口径见 销售/说明.md，回复客户名和它的已付款金额合计。", agg="top", group="客户", col="金额元", margin=500,
                   pred='r["状态"]=="已付款"', decoy=dict(pred='r["状态"].startswith("已付款")'), decoy_note="状态前缀匹配，含已付款(部分)",
                   cmd="""awk -F'\\t' '$3=="已付款" {s[$2]+=$4} END{for (k in s) print s[k], k}' 销售/订单.txt | sort -rn | head -1""", unit="已付款金额合计最高的是{v}，合计 {n} 元。",
                   alts=["订单.txt 里哪个客户的已付款总额最大？", "按说明.md，已付款订单的金额按客户汇总，谁最高？", "季度订单中，已付款金额加起来最多的客户是谁？", "哪家客户的已付款金额排第一（部分付款不算）？", "统计状态恰好是已付款的金额，按客户求和后最大的客户名。"])])


def gate_gen(rng, i, fi, n):
    zone = choice(rng, ["机房", "机房", "机房-备用", "大厅", "办公区", "仓库"])
    res = choice(rng, ["通过", "通过", "拒绝", "拒绝(超时)"])
    return [f"1012T{rng.randint(6, 22):02d}{rng.randint(0, 59):02d}", f"C{rng.randint(1000, 1400)}", zone, res, f"gate-{rng.choice(['2F', '3F', 'B1'])}-{rng.choice(['东', '西'])}-{rng.randint(1, 9):02d}-终端"]


# 9336 door access, distinct cards in one long file
case("log-9336", sub="M9c", tt="count_events", topic="doordenied", root="门禁", names=["刷卡.txt"], sep=";",
     cols=["时间", "卡号", "区域", "结果", "终端"], header=False, rows=(1300, 1400), readme_name="说明.md", min=20, gen=gate_gen,
     readme=["# 门禁刷卡说明", "", "刷卡.txt 是一天的全部刷卡记录，分号分隔，没有表头：时间;卡号;区域;结果;终端。", "区域、结果都按完整内容匹配：「机房-备用」是另一间机房，「拒绝(超时)」是读卡超时重刷，不算「拒绝」。"],
     desc="Counts distinct cards that were denied entry to the server room in one long swipe file where a backup room and a timeout result are look-alikes",
     why="区域 and 结果 are whole-value columns; cards are de-duplicated.",
     queries=[dict(prompt="门禁/刷卡.txt 里，在「机房」被「拒绝」过的卡号有多少个（同一张卡只算一次）？口径见 门禁/说明.md。", agg="distinct", col="卡号",
                   pred='r["区域"]=="机房" and r["结果"]=="拒绝"', decoy=dict(pred='r["区域"].startswith("机房") and r["结果"].startswith("拒绝")'), decoy_note="区域和结果都用前缀匹配",
                   cmd="""awk -F';' '$3=="机房" && $4=="拒绝" {print $2}' 门禁/刷卡.txt | sort -u | wc -l""", unit="机房拒绝涉及 {v} 张不同的卡。",
                   alts=["机房门禁拒绝过的不同卡号共有多少？", "区域是机房、结果是拒绝的记录，去重后有多少张卡？", "按说明.md，有多少张卡在机房被拒绝过？", "刷卡记录里被机房拒绝的卡号个数（去重）。", "统计机房拒绝记录涉及的不同卡号数量。"])])


def qps_gen(rng, i, fi, n):
    api = choice(rng, ["/pay", "/pay", "/pay", "/pay/refund", "/order", "/order", "/order/list", "/search"])
    hi = {"/pay": (300, 1200), "/pay/refund": (300, 1500), "/order": (200, 900), "/order/list": (300, 1100)}.get(api, (100, 800))
    sec = rng.randint(0, 86399)
    return [f"{sec // 3600:02d}:{sec // 60 % 60:02d}:{sec % 60:02d}", api, str(rint(rng, hi[0], hi[1], 10)), "%.1f" % (rng.randint(0, 80) / 10), f"pod-{rng.choice(['checkout', 'gateway', 'worker'])}-{rng.choice(['7f9c', '5d2a', '9b1e'])}-{rng.choice(['xk2', 'qp8', 'mt4'])}"]


# 9337 load test, max with tie rule (earliest time), two turns
case("tab-9337", sub="M9c", tt="rank", topic="qpspeak", root="压测", names=["qps.txt"], sep=",",
     cols=["时间", "接口", "qps", "错误率", "实例"], header=True, rows=(1300, 1400), readme_name="说明.md", min=1, gen=qps_gen,
     readme=["# 压测采样说明", "", "qps.txt 是一次压测的全部采样，逗号分隔：时间、接口、qps（10 的倍数）、错误率(%)、实例，第一行是表头；行不按时间排序。", "接口按完整路径匹配：「/pay/refund」「/order/list」是独立接口，不属于「/pay」「/order」。", "峰值 qps 有多条并列时，取时间最早的那条。"],
     desc="Two turns over one long load-test file: the time of the peak qps for /pay with ties broken by the earliest time, then for /order, with look-alike sub-paths that peak higher",
     why="接口 is a whole-value column; the peak is shared by several rows and the README picks the earliest time.",
     queries=[
         dict(prompt="压测/qps.txt 里，接口 /pay 的 qps 峰值出现在几点几分几秒？并列的情况按 压测/说明.md 处理，回复时间，并说明 /pay 一共有多少条采样。", agg="argtie", extreme="max", col="qps", ret="时间", tie_col="时间", tie_pick="min",
              pred='r["接口"]=="/pay"', decoy=dict(pred='r["接口"].startswith("/pay")'), decoy_note="接口前缀匹配，含/pay/refund",
              cmd="""awk -F, '$2=="/pay" {print $3, $1}' 压测/qps.txt | sort -k1,1nr -k2,2 | head -1""", cmd2="""awk -F, '$2=="/pay"' 压测/qps.txt | wc -l""", unit="/pay 的 qps 峰值出现在 {v}，/pay 共有 {n} 条采样。", alts=[]),
         dict(prompt="那接口 /order 的 qps 峰值又是什么时间？规则同上，/order 一共有多少条采样也告诉我。", agg="argtie", extreme="max", col="qps", ret="时间", tie_col="时间", tie_pick="min",
              pred='r["接口"]=="/order"', decoy=dict(pred='r["接口"].startswith("/order")'), decoy_note="接口前缀匹配，含/order/list",
              cmd="""awk -F, '$2=="/order" {print $3, $1}' 压测/qps.txt | sort -k1,1nr -k2,2 | head -1""", cmd2="""awk -F, '$2=="/order"' 压测/qps.txt | wc -l""", unit="/order 的 qps 峰值出现在 {v}，/order 共有 {n} 条采样。",
              alts=["/order 接口峰值 qps 对应的时间是多少？并列取最早。", "接口恰好是 /order 的记录里，qps 最高的是哪个时刻？", "按说明.md，/order 的 qps 最大值出现在什么时间？", "qps.txt 中 /order（不含 /order/list）峰值那一刻的时间。", "找出 /order 的峰值 qps，若并列取最早，告诉我时间。"]),
     ])


def bat_gen(rng, i, fi, n):
    dev = choice(rng, ["bot-A", "bot-A", "bot-AB", "bot-B", "bot-C"])
    lvl = {"bot-A": rint(rng, 4, 60), "bot-AB": rint(rng, 2, 40)}.get(dev, rint(rng, 8, 100))
    return [f"2026-10-{rng.randint(1, 7):02d}T{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}", dev, str(lvl), choice(rng, ["dock", "hall-east", "hall-west", "yard"]), f"fw-build-{rng.choice(['alpha', 'beta', 'stable'])}-{rng.choice(['north', 'south'])}-cell"]


# 9338 robot battery, min with tie rule (earliest ts), English
case("tab-9338", sub="M9c", tt="rank", topic="botbattery", root="fleet", names=["battery.txt"], sep=";",
     cols=["ts", "device", "battery_pct", "site", "fw"], header=True, rows=(1250, 1350), readme_name="README.md", min=1, gen=bat_gen,
     readme=["# Fleet battery samples", "", "battery.txt holds every sample of the week, semicolon separated: ts;device;battery_pct;site;fw, first line is the header. Rows are not sorted by time.", "Device ids are whole values: `bot-AB` is a different robot from `bot-A`.", "When several samples share the lowest battery level, use the one with the earliest ts."],
     desc="Finds the site where robot bot-A reported its lowest battery in one long sample file, with tied samples broken by the earliest timestamp and a look-alike robot that ran lower",
     why="device is a whole-value column; the lowest level is shared by several rows and the README picks the earliest ts.",
     queries=[dict(prompt="In fleet/battery.txt, at which site was bot-A when it reported its lowest battery level? fleet/README.md explains how to break ties; reply with the site name and the total number of bot-A samples.", agg="argtie", extreme="min", col="battery_pct", ret="site", tie_col="ts", tie_pick="min",
                   pred='r["device"]=="bot-A"', decoy=dict(pred='r["device"].startswith("bot-A")'), decoy_note="device prefix match, includes bot-AB",
                   cmd="""awk -F';' '$2=="bot-A" {print $3, $1, $4}' fleet/battery.txt | sort -k1,1n -k2,2 | head -1""", cmd2="""awk -F';' '$2=="bot-A"' fleet/battery.txt | wc -l""", unit="bot-A was at {v} when its battery was lowest; bot-A has {n} samples in total.",
                   alts=["Where was bot-A when its battery hit the lowest level? Earliest sample wins ties.", "Site of bot-A's lowest battery sample in battery.txt, per the README tie rule.", "Which site did bot-A report from at its minimum battery_pct?", "Find bot-A's lowest battery reading and tell me the site (earliest ts if tied).", "At minimum charge, which site was robot bot-A at?"])])


def meter_gen(rng, i, fi, n):
    dev = choice(rng, ["AC-1", "AC-1", "AC-11", "AC-2", "PUMP-1"])
    return [f"202610{rng.randint(1, 28):02d}", dev, str(rng.randint(5, 300)), choice(rng, ["-", "-", "接AC-1总闸", "巡检", "-"]), f"{rng.choice(['三号', '五号', '七号'])}厂房-{rng.choice(['一层', '二层', '三层'])}-{rng.choice(['东侧', '西侧'])}-配电间"]


# 9339 energy readings, sum with whole-line decoy
case("tab-9339", sub="M9c", tt="aggregate", topic="acenergy", root="能耗", names=["抄表.txt"], sep=" ",
     cols=["日期", "设备", "度数", "备注", "位置"], header=False, rows=(1300, 1400), readme_name="说明.md", gen=meter_gen,
     readme=["# 能耗抄表说明", "", "抄表.txt 是整月的抄表记录，空格分隔，没有表头：日期 设备 度数 备注 位置。", "统计某台设备只看「设备」这一列、按完整内容匹配：「AC-11」是另一台设备；备注里提到的设备名只是提示，那一行的度数不属于它。"],
     desc="Sums the kilowatt-hours of device AC-1 in one long meter file where a longer device id and a remarks column mentioning AC-1 are look-alikes",
     why="设备 is a whole-value column; AC-1 elsewhere in the line does not count.",
     queries=[dict(prompt="能耗/抄表.txt 里，设备 AC-1 这个月的度数合计是多少？口径见 能耗/说明.md，回复数字。", agg="sum", col="度数", pred='r["设备"]=="AC-1"', decoy=dict(pred='"AC-1" in "".join(r.values())'), decoy_note="整行包含AC-1，含AC-11和备注",
                   cmd="""awk '$2=="AC-1" {s+=$3} END{print s}' 能耗/抄表.txt""", unit="AC-1 本月合计 {v} 度。",
                   alts=["AC-1 空调这个月一共用了多少度电？", "抄表记录中设备列等于 AC-1 的度数之和。", "按说明.md，AC-1（不含 AC-11）的用电度数合计。", "整月抄表里 AC-1 的度数总和是多少？", "统计设备为 AC-1 的所有行的度数列合计。"])])


def web_gen(rng, i, fi, n):
    pool = [f"10.0.{a}.{b}" for a, b in [(1, 5), (1, 50), (1, 7), (2, 11), (2, 110), (3, 4), (3, 40), (3, 9), (4, 21), (4, 2)]]
    path = choice(rng, ["/login", "/login", "/login/sso", "/home", "/api/items", "/health"])
    return [f"1012T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", choice(rng, pool, [5, 3, 2, 2, 2, 3, 2, 2, 2, 2]), path, choice(rng, ["200", "200", "401", "401", "403", "500"]), "Mozilla/5.0-Linux-x86_64-Chrome-118"]


# 9340 web access, top-1 ip by count, English
case("log-9340", sub="M9c", tt="count_events", topic="loginfailip", root="web", names=["access.txt"], sep=" ",
     cols=["time", "ip", "path", "status", "ua"], header=False, rows=(1300, 1400), readme_name="README.md", min=1, gen=web_gen,
     readme=["# Access log", "", "access.txt is one day of requests, space separated, no header: time ip path status ua.", "Path and status are whole values: `/login/sso` is a different endpoint from `/login`, and only status 401 means a failed credential check (403 and 500 are other errors)."],
     desc="Finds the client IP with the most failed credential checks on /login in one long access log where a sub-path and other error codes are look-alikes",
     why="path and status are whole-value columns; the leader is ahead by at least three requests.",
     queries=[dict(prompt="Which IP address made the most requests to /login that came back with status 401 in web/access.txt? The README there defines the terms; reply with the IP and how many such requests it made.", agg="top", group="ip", margin=3,
                   pred='r["path"]=="/login" and r["status"]=="401"', decoy=dict(pred='r["path"].startswith("/login") and r["status"].startswith("4")'), decoy_note="prefix match on path and any 4xx status",
                   cmd="""awk '$3=="/login" && $4==401 {c[$2]++} END{for (k in c) print c[k], k}' web/access.txt | sort -rn | head -1""", unit="{v} had the most failed /login requests ({n}).",
                   alts=["Top client IP by 401 responses on the /login endpoint?", "In access.txt, which IP has the highest count of 401s for path /login?", "Per web/README.md, which address failed /login the most?", "Find the IP with the most /login requests answered by status 401.", "Which IP is behind the largest number of 401 login failures?"])])


def _mk(cid):
    return lambda: build(cid)


BUILDERS = []
for _cid in sorted(CASES):
    BUILDERS.append(_mk(_cid))
    BUILDERS[-1].__name__ = _cid.replace("-", "_")

# static SPEC (specs.py loads this file by path and needs it at import time)
for _cid, _c in CASES.items():
    SPEC[_cid] = dict(kind="bash_aggregate", sub=_c["sub"], needs=[f"{_c['root']}/{_c['readme_name']}"])
