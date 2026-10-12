"""M9 (bash) batch b12p of v1.41: ids 9401-9420, multi-file aggregation to one scalar over .txt/.dat/.tsv-like tables.

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
            exp = {"output_contains_any": want, "max_output_chars": 600} if (len(want) > 1 or q["agg"] == "sum") else {"output_contains": want, "max_output_chars": 600}
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
        cid, desc=c["desc"], task_type=c["tt"], family="fam-%s-b12p-%s-01" % (cid.split("-")[0], c["topic"]), level=c.get("level", "L2"),
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

def rint(rng, lo, hi, step=1):
    return rng.randrange(lo, hi + 1, step)


def mkc(cid, sub, tt, topic, root, names, sep, cols, rows, readme, gen, desc, why, q, header=True, readme_name="说明.md", min_=5):
    zh = not root.isascii()
    import re as _re
    pcols = list(dict.fromkeys(_re.findall(r'r\["([^"]+)"\]', q["pred"])))
    rule = ("统计时，" + "、".join("「%s」" % c for c in pcols) + "两列都按整格的完整内容匹配，不是前缀或包含匹配。") if zh else \
        ("When filtering, match " + " and ".join("`%s`" % c for c in pcols) + " on the whole cell value, not by prefix or substring.")
    if q["agg"] == "distinct":
        rule += ("按「%s」去重，同一个只算一次。" % q["col"]) if zh else (" Count each `%s` once." % q["col"])
    readme = list(readme[:3]) + [rule]
    if not zh:
        readme_name = "README.md"
    sepname = {"\t": "制表符", ";": "分号", ",": "逗号", " ": "空格"} if zh else {"\t": "tab", ";": "semicolon", ",": "comma", " ": "space"}
    fields = ("、".join("$%d %s" % (i + 1, c) for i, c in enumerate(cols)) if zh else ", ".join("$%d %s" % (i + 1, c) for i, c in enumerate(cols)))
    if zh:
        extra = "字段顺序固定（awk 的列号）：%s。各文件格式完全一致，%s，没有空行，也没有多余空格。" % (fields, "第一行是表头" if header else "没有表头")
        q = dict(q, prompt=q["prompt"].replace("口径见", "各文件合在一起算，口径见", 1))
    else:
        extra = "Field order is fixed (awk column numbers): %s. All files share the same layout, %s, with no blank lines and no stray spaces." % (fields, "the first line is a header" if header else "there is no header")
        q = dict(q, prompt=q["prompt"].replace("? ", ", all files together? ", 1) if "? " in q["prompt"] else q["prompt"])
    case(cid, sub=sub, tt=tt, topic=topic, root=root, names=names, sep=sep, cols=cols, rows=rows, readme_name=readme_name, header=header, min=min_,
         readme=list(readme) + [extra], gen=gen, desc=desc, why=why, queries=[q])


def dn(rng, k=60):
    return NAMES[rng.randint(0, k - 1)]


# ---------------------------------------------------------------- Chinese (13)
mkc("tab-9401", "M9a", "aggregate", "pharmsold", "药房出库", ["第1周.txt", "第2周.txt", "第3周.txt", "第4周.txt"], T, ["日期", "药品", "状态", "数量"], (80, 110),
    ["# 药房出库说明", "", "每周一个文件，制表符分隔：日期、药品、状态、数量（盒）。", "药品和状态都按完整内容匹配：「布洛芬缓释」是另一种药，状态「已发(补)」是事后补录的，不算「已发」。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["布洛芬", "布洛芬", "布洛芬缓释", "对乙酰氨基酚", "蒙脱石散", "氯雷他定"]),
                           choice(rng, ["已发", "已发", "已发", "已发(补)", "退回"]), str(rng.randint(1, 60))],
    "Sums boxes of one drug in the issued state over four weekly tables with a slow-release look-alike drug and a back-filled status",
    "药品 and 状态 are whole-value columns.",
    dict(prompt="四周的药房出库表里，药品「布洛芬」状态为「已发」的数量一共是多少盒？口径见 药房出库/说明.md，只回复数字。", agg="sum", col="数量", pred='r["药品"]=="布洛芬" and r["状态"]=="已发"',
         decoy=dict(pred='r["药品"].startswith("布洛芬") and r["状态"].startswith("已发")'), decoy_note="药品、状态前缀匹配",
         cmd="""cat 药房出库/*.txt | awk -F'\\t' '$2=="布洛芬" && $3=="已发" {s+=$4} END{print s}'""", unit="{v} 盒。",
         alts=["布洛芬（不含缓释）已发的盒数合计是多少？", "把四周里布洛芬、已发的数量加起来。", "按说明.md，布洛芬已发出库共多少盒？", "药品列等于布洛芬且状态列等于已发的数量总和。", "统计布洛芬正式出库（不含补录）的总盒数。"]))

mkc("log-9402", "M9a", "count_events", "parkingin", "停车场", ["东门.txt", "西门.txt", "南门.txt"], ";", ["时间", "车场", "事件", "尾号"], (110, 150),
    ["# 停车场出入记录说明", "", "每个门一个文件，分号分隔，没有表头：时间;车场;事件;尾号。", "车场、事件都按完整内容匹配：「P10」「P1-VIP」不是「P1」，「驶入(月卡)」是月卡车辆，不算「驶入」。"],
    lambda rng, i, fi, n: [f"1011T{rng.randint(6, 23):02d}{rng.randint(0, 59):02d}", choice(rng, ["P1", "P1", "P10", "P2", "P1-VIP"]),
                           choice(rng, ["驶入", "驶入", "驶出", "驶入(月卡)", "驶出"]), f"{rng.randint(0, 9999):04d}"],
    "Counts entry events at one car park over three gate tables where a ten-times-larger lot code and a monthly-pass event are look-alikes",
    "车场 and 事件 are whole-value columns.",
    dict(prompt="三个门的出入记录里，车场为「P1」、事件为「驶入」的记录一共有多少条？口径见 停车场/说明.md，只回复数字。", agg="count", pred='r["车场"]=="P1" and r["事件"]=="驶入"',
         decoy=dict(pred='r["车场"].startswith("P1") and r["事件"].startswith("驶入")'), decoy_note="车场、事件前缀匹配",
         cmd="""cat 停车场/*.txt | awk -F';' '$2=="P1" && $3=="驶入"' | wc -l""", unit="{v} 条。",
         alts=["P1 车场驶入（不含月卡）的次数是多少？", "统计车场列为 P1、事件列为驶入的行数。", "按说明.md，P1 的普通驶入记录共有几条？", "三个门加起来，P1 驶入一共多少次？", "P1 车场的驶入记录总数。"]), header=False, min_=20)

mkc("log-9403", "M9a", "count_events", "volunteerdone", "志愿服务", ["9月.txt", "10月.txt", "11月.txt", "12月.txt"], T, ["日期", "志愿者", "活动", "状态"], (70, 95),
    ["# 志愿服务登记说明", "", "每月一个文件，制表符分隔：日期、志愿者、活动、状态。", "活动、状态都按完整内容匹配：「植树(预备)」是预备场次，「完成(补录)」是事后补录，都不算「植树」「完成」。同一位志愿者只算一人。"],
    lambda rng, i, fi, n: [f"2026-{9 + fi:02d}-{rng.randint(1, 28):02d}", dn(rng, 70), choice(rng, ["植树", "植树", "植树(预备)", "助老", "社区清扫", "义诊"]),
                           choice(rng, ["完成", "完成", "完成(补录)", "缺席"])],
    "Counts distinct volunteers who completed one activity over four monthly tables with a preparatory session and a back-filled status as look-alikes",
    "活动 and 状态 are whole-value columns; volunteers are de-duplicated across files.",
    dict(prompt="四个月的志愿服务登记里，活动为「植树」且状态为「完成」的志愿者一共有多少位（同一位只算一次）？口径见 志愿服务/说明.md，只回复数字。", agg="distinct", col="志愿者",
         pred='r["活动"]=="植树" and r["状态"]=="完成"', decoy=dict(pred='r["活动"].startswith("植树") and r["状态"].startswith("完成")'), decoy_note="活动、状态前缀匹配",
         cmd="""cat 志愿服务/*.txt | awk -F'\\t' '$3=="植树" && $4=="完成" {print $2}' | sort -u | wc -l""", unit="{v} 位。",
         alts=["完成植树活动的不同志愿者有几位？", "植树、完成这两个条件下去重后的志愿者人数。", "按说明.md，植树完成的志愿者共多少人（去重）？", "四个月里正式完成植树的志愿者数量，同一个人只数一次。", "统计活动是植树、状态是完成的不同志愿者人数。"]))

mkc("tab-9404", "M9a", "rank", "tidemax", "水文站", ["上游.dat", "中游.dat", "下游.dat"], " ", ["时间", "站名", "水位cm"], (110, 150),
    ["# 水文站水位说明", "", "每段河道一个文件，空格分隔，没有表头：时间 站名 水位（厘米，整数）。", "站名按完整名称匹配：「青山闸北」是另一个站，不是「青山闸」。"],
    lambda rng, i, fi, n: (lambda s: [f"1010T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", s, str(rint(rng, 150, 980) if s == "青山闸" else rint(rng, 150, 1300))])(
        choice(rng, ["青山闸", "青山闸", "青山闸北", "石桥", "东渡口"])),
    "Finds the highest water level at one gauge over three river-section tables where a northern twin gauge ran higher",
    "站名 is a whole-value column.",
    dict(prompt="三个河段的水位记录里，站名为「青山闸」的最高水位是多少厘米？口径见 水文站/说明.md，只回复数字。", agg="max", col="水位cm", pred='r["站名"]=="青山闸"',
         decoy=dict(pred='r["站名"].startswith("青山闸")'), decoy_note="站名前缀匹配，含青山闸北",
         cmd="""cat 水文站/*.dat | awk '$2=="青山闸" {print $3}' | sort -rn | head -1""", unit="{v} 厘米。",
         alts=["青山闸历史最高水位多少厘米？", "站名恰好是青山闸的水位最大值。", "按说明.md，青山闸（不含青山闸北）的峰值水位是多少？", "三个文件里青山闸的最高水位读数。", "青山闸水位最高的那条记录是多少厘米？"]), header=False, min_=1)

mkc("tab-9405", "M9a", "aggregate", "seatseconds", "外呼记录", ["早班.txt", "午班.txt", "晚班.txt"], ",", ["日期", "坐席", "类型", "秒"], (110, 150),
    ["# 外呼记录说明", "", "每个班次一个文件，逗号分隔：日期、坐席、类型、通话秒数。", "坐席、类型按完整内容匹配：「A070」「A7」不是「A07」，「外呼(转接)」是转接来的，不算「外呼」。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["A07", "A07", "A070", "A17", "A7"]), choice(rng, ["外呼", "外呼", "呼入", "外呼(转接)"]), str(rng.randint(20, 900))],
    "Sums call seconds of one agent's outbound calls over three shift tables with look-alike agent codes and a transferred call type",
    "坐席 and 类型 are whole-value columns.",
    dict(prompt="三个班次的记录里，坐席「A07」的「外呼」通话秒数一共是多少？口径见 外呼记录/说明.md，只回复数字。", agg="sum", col="秒", pred='r["坐席"]=="A07" and r["类型"]=="外呼"',
         decoy=dict(pred='r["坐席"].startswith("A07") and r["类型"].startswith("外呼")'), decoy_note="坐席、类型前缀匹配",
         cmd="""cat 外呼记录/*.txt | awk -F, '$2=="A07" && $3=="外呼" {s+=$4} END{print s}'""", unit="{v} 秒。",
         alts=["A07 坐席外呼的通话总秒数是多少？", "坐席列等于 A07、类型列等于外呼的秒数之和。", "按说明.md，A07 纯外呼累计通话多少秒？", "把 A07 的外呼秒数加起来，转接不算。", "三个班次里 A07 外呼时长合计。"]))

mkc("tab-9406", "M9a", "filter_count", "clinicseen", "门诊挂号", ["周一.txt", "周二.txt", "周三.txt", "周四.txt", "周五.txt"], T, ["日期", "科室", "状态", "医生"], (70, 95),
    ["# 门诊挂号说明", "", "每个工作日一个文件，制表符分隔：日期、科室、状态、医生。", "科室、状态按完整内容匹配：「内科(急)」是急诊内科，「已就诊(复诊)」是复诊号，都不算「内科」「已就诊」。"],
    lambda rng, i, fi, n: [f"2026-10-{12 + fi:02d}", choice(rng, ["内科", "内科", "内科(急)", "外科", "儿科"]), choice(rng, ["已就诊", "已就诊", "已就诊(复诊)", "爽约"]), dn(rng, 20)],
    "Counts completed visits of one department over five weekday tables with an emergency twin department and a follow-up status as look-alikes",
    "科室 and 状态 are whole-value columns.",
    dict(prompt="这一周的挂号表里，科室为「内科」、状态为「已就诊」的有多少条？口径见 门诊挂号/说明.md，只回复数字。", agg="count", pred='r["科室"]=="内科" and r["状态"]=="已就诊"',
         decoy=dict(pred='r["科室"].startswith("内科") and r["状态"].startswith("已就诊")'), decoy_note="科室、状态前缀匹配",
         cmd="""cat 门诊挂号/*.txt | awk -F'\\t' '$2=="内科" && $3=="已就诊"' | wc -l""", unit="{v} 条。",
         alts=["内科已就诊（不含急诊和复诊）共几条？", "五天里科室是内科且状态是已就诊的行数。", "按说明.md，普通内科的就诊记录总数是多少？", "统计内科已就诊挂号的条数。", "科室列为内科、状态列为已就诊的记录有多少。"]), min_=20)

mkc("log-9407", "M9a", "count_events", "gymyoga", "健身房", ["周一.txt", "周三.txt", "周五.txt", "周日.txt"], ";", ["日期", "会员", "课程", "出勤"], (80, 110),
    ["# 健身房出勤说明", "", "每个上课日一个文件，分号分隔，没有表头：日期;会员;课程;出勤。", "课程、出勤按完整内容匹配：「瑜伽(进阶)」是另一门课，「到课(补课)」是补课，都不算「瑜伽」「到课」。同一位会员只算一人。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", f"M{rng.randint(100, 220)}", choice(rng, ["瑜伽", "瑜伽", "瑜伽(进阶)", "搏击", "动感单车"]), choice(rng, ["到课", "到课", "到课(补课)", "缺课"])],
    "Counts distinct members who attended one class over four tables with an advanced twin class and a make-up attendance as look-alikes",
    "课程 and 出勤 are whole-value columns; members are de-duplicated across files.",
    dict(prompt="四个上课日的出勤表里，课程为「瑜伽」且出勤为「到课」的会员一共有多少位（同一位只算一次）？口径见 健身房/说明.md，只回复数字。", agg="distinct", col="会员",
         pred='r["课程"]=="瑜伽" and r["出勤"]=="到课"', decoy=dict(pred='r["课程"].startswith("瑜伽") and r["出勤"].startswith("到课")'), decoy_note="课程、出勤前缀匹配",
         cmd="""cat 健身房/*.txt | awk -F';' '$3=="瑜伽" && $4=="到课" {print $2}' | sort -u | wc -l""", unit="{v} 位。",
         alts=["上过瑜伽课（到课）的不同会员有多少人？", "瑜伽、到课两个条件下去重的会员数。", "按说明.md，正式到课的瑜伽会员有几位？", "四天里瑜伽到课会员的去重人数。", "统计课程是瑜伽、出勤是到课的不同会员数量。"]), header=False)

mkc("tab-9408", "M9a", "aggregate", "rebarnight", "工地考勤", ["一标段.txt", "二标段.txt", "三标段.txt"], T, ["日期", "工种", "班次", "工时"], (110, 150),
    ["# 工地考勤说明", "", "每个标段一个文件，制表符分隔：日期、工种、班次、工时（小时，整数）。", "工种、班次按完整内容匹配：「钢筋工(学徒)」是学徒，「夜班(加)」是加班夜班，都不算「钢筋工」「夜班」。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["钢筋工", "钢筋工", "钢筋工(学徒)", "木工", "瓦工"]), choice(rng, ["白班", "夜班", "夜班", "夜班(加)"]), str(rng.randint(2, 12))],
    "Sums night-shift hours of one trade over three site tables with an apprentice trade and an overtime night shift as look-alikes",
    "工种 and 班次 are whole-value columns.",
    dict(prompt="三个标段的考勤表里，工种为「钢筋工」、班次为「夜班」的工时一共是多少小时？口径见 工地考勤/说明.md，只回复数字。", agg="sum", col="工时", pred='r["工种"]=="钢筋工" and r["班次"]=="夜班"',
         decoy=dict(pred='r["工种"].startswith("钢筋工") and r["班次"].startswith("夜班")'), decoy_note="工种、班次前缀匹配",
         cmd="""cat 工地考勤/*.txt | awk -F'\\t' '$2=="钢筋工" && $3=="夜班" {s+=$4} END{print s}'""", unit="{v} 小时。",
         alts=["钢筋工夜班的工时总和是多少？", "工种列等于钢筋工、班次列等于夜班的工时相加。", "按说明.md，钢筋工（不含学徒）夜班共多少小时？", "三个标段里钢筋工夜班累计工时。", "把钢筋工夜班的小时数全部加起来，加班夜班不算。"]))

mkc("tab-9409", "M9a", "rank", "tomatolow", "菜价", ["早市.txt", "午市.txt", "夜市.txt"], ",", ["日期", "品名", "摊位", "单价分"], (110, 150),
    ["# 菜价记录说明", "", "每个市场时段一个文件，逗号分隔：日期、品名、摊位、单价（分/斤，整数）。", "品名、摊位按完整内容匹配：「西红柿(有机)」是另一个品类，「13号」「23号」不是「3号」。"],
    lambda rng, i, fi, n: (lambda p, s: [f"2026-10-{rng.randint(1, 28):02d}", p, s, str(rint(rng, 90, 179) if (p == "西红柿(有机)" or s != "3号") and p.startswith("西红柿") and rng.random() < 0.5 else rint(rng, 180, 480))])(
        choice(rng, ["西红柿", "西红柿", "圣女果", "西红柿(有机)", "黄瓜"]), choice(rng, ["3号", "3号", "13号", "23号", "8号"])),
    "Finds the lowest unit price of one vegetable at one stall over three market tables where organic and other-stall look-alikes were cheaper",
    "品名 and 摊位 are whole-value columns.",
    dict(prompt="三个时段的菜价表里，品名为「西红柿」、摊位为「3号」的最低单价是多少分？口径见 菜价/说明.md，只回复数字。", agg="min", col="单价分", pred='r["品名"]=="西红柿" and r["摊位"]=="3号"',
         decoy=dict(pred='r["品名"].startswith("西红柿") and r["摊位"].endswith("3号")'), decoy_note="品名前缀匹配、摊位后缀匹配",
         cmd="""cat 菜价/*.txt | awk -F, '$2=="西红柿" && $3=="3号" {print $4}' | sort -n | head -1""", unit="{v} 分。",
         alts=["3号摊位西红柿最低卖多少分？", "品名是西红柿、摊位是3号的单价最小值。", "按说明.md，3号摊西红柿（非有机）的最低价。", "三个时段里3号摊西红柿的最低单价是多少？", "西红柿在3号摊的最低报价是几分？"]), min_=1)

mkc("log-9410", "M9a", "count_events", "printok", "打印日志", ["上午.txt", "下午.txt", "加班.txt"], " ", ["时间", "打印机", "结果", "页数"], (110, 150),
    ["# 打印日志说明", "", "每个时段一个文件，空格分隔，没有表头：时间 打印机 结果 页数。", "打印机、结果按完整内容匹配：「3F-020」「3F-12」不是「3F-02」，「成功(重试)」是重试后才成功，不算「成功」。"],
    lambda rng, i, fi, n: [f"1012T{rng.randint(8, 21):02d}{rng.randint(0, 59):02d}", choice(rng, ["3F-02", "3F-02", "3F-020", "3F-12", "4F-02"]), choice(rng, ["成功", "成功", "成功(重试)", "失败"]), str(rng.randint(1, 40))],
    "Counts successful print jobs of one printer over three time-slot tables with look-alike printer codes and a retried-success result",
    "打印机 and 结果 are whole-value columns.",
    dict(prompt="三个时段的打印日志里，打印机为「3F-02」、结果为「成功」的任务有多少条？口径见 打印日志/说明.md，只回复数字。", agg="count", pred='r["打印机"]=="3F-02" and r["结果"]=="成功"',
         decoy=dict(pred='r["打印机"].startswith("3F-02") and r["结果"].startswith("成功")'), decoy_note="打印机、结果前缀匹配",
         cmd="""cat 打印日志/*.txt | awk '$2=="3F-02" && $3=="成功"' | wc -l""", unit="{v} 条。",
         alts=["3F-02 打印成功（不含重试）的任务数。", "打印机列等于 3F-02、结果列等于成功的行数。", "按说明.md，3F-02 一次成功的任务共有多少条？", "统计 3F-02 的成功任务总数。", "三个时段里 3F-02 成功记录的条数。"]), header=False, min_=20)

mkc("tab-9411", "M9a", "aggregate", "fuel95", "加油量", ["白班.txt", "夜班.txt", "周末.txt"], T, ["日期", "站", "油品", "升"], (110, 150),
    ["# 加油量记录说明", "", "每个班次一个文件，制表符分隔：日期、站、油品、加油量（升，整数）。", "站、油品按完整内容匹配：「东环站(新)」是新开的另一个站，「95E」是乙醇汽油，不算「东环站」「95」。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["东环站", "东环站", "东环站(新)", "西郊站"]), choice(rng, ["95", "95", "92", "98", "95E", "柴油"]), str(rng.randint(8, 70))],
    "Sums litres of one fuel grade at one station over three shift tables with a new twin station and an ethanol grade as look-alikes",
    "站 and 油品 are whole-value columns.",
    dict(prompt="三个班次的加油量表里，「东环站」的「95」号汽油一共加了多少升？口径见 加油量/说明.md，只回复数字。", agg="sum", col="升", pred='r["站"]=="东环站" and r["油品"]=="95"',
         decoy=dict(pred='r["站"].startswith("东环站") and r["油品"].startswith("95")'), decoy_note="站、油品前缀匹配",
         cmd="""cat 加油量/*.txt | awk -F'\\t' '$2=="东环站" && $3=="95" {s+=$4} END{print s}'""", unit="{v} 升。",
         alts=["东环站 95 号汽油的加油量合计是多少升？", "站列等于东环站、油品列等于95的升数之和。", "按说明.md，东环站（不含新站）95 号累计多少升？", "把东环站95号的加油升数全部相加。", "三个班次里东环站的95号汽油总量。"]))

mkc("log-9412", "M9a", "count_events", "bnbrooms", "民宿订单", ["一楼.txt", "二楼.txt", "三楼.txt"], ";", ["日期", "房号", "渠道", "状态"], (90, 120),
    ["# 民宿订单说明", "", "每层楼一个文件，分号分隔，没有表头：日期;房号;渠道;状态。", "渠道、状态按完整内容匹配：「直订(团购)」是团购券，「已入住(提前)」是提前入住，都不算「直订」「已入住」。同一房号只算一间。"],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", f"{fi + 1}{rng.randint(1, 4)}{rng.randint(1, 9)}", choice(rng, ["直订", "直订", "直订(团购)", "携程", "美团"]), choice(rng, ["已入住", "已入住", "已入住(提前)", "取消"])],
    "Counts distinct rooms that were checked in via direct booking over three floor tables with a coupon channel and an early check-in as look-alikes",
    "渠道 and 状态 are whole-value columns; rooms are de-duplicated across files.",
    dict(prompt="三层楼的订单表里，渠道为「直订」且状态为「已入住」的订单涉及多少间不同的房号？口径见 民宿订单/说明.md，只回复数字。", agg="distinct", col="房号",
         pred='r["渠道"]=="直订" and r["状态"]=="已入住"', decoy=dict(pred='r["渠道"].startswith("直订") and r["状态"].startswith("已入住")'), decoy_note="渠道、状态前缀匹配",
         cmd="""cat 民宿订单/*.txt | awk -F';' '$3=="直订" && $4=="已入住" {print $2}' | sort -u | wc -l""", unit="{v} 间。",
         alts=["直订并且已入住的房间有几间（去重）？", "渠道直订、状态已入住的不同房号个数。", "按说明.md，直订入住过的房号共多少个？", "三层楼里直订已入住涉及的房间数，同一间只算一次。", "统计渠道为直订、状态为已入住的去重房号数。"]), header=False, min_=10)

mkc("tab-9413", "M9a", "rank", "greenhumid", "大棚监测", ["东区.dat", "西区.dat"], ",", ["时间", "棚号", "位置", "湿度"], (150, 200),
    ["# 大棚湿度监测说明", "", "每个区一个文件，逗号分隔，没有表头：时间,棚号,位置,湿度（百分比，整数）。", "棚号、位置按完整内容匹配：「3号(东)」「13号」不是「3号」。"],
    lambda rng, i, fi, n: (lambda b, p: [f"1011T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", b, p, str(rint(rng, 40, 86) if b == "3号" and p == "上层" else rint(rng, 40, 99))])(
        choice(rng, ["3号", "3号", "3号(东)", "13号", "5号"]), choice(rng, ["上层", "下层", "上层", "中层"])),
    "Finds the highest humidity of one greenhouse upper level over two zone tables where an eastern twin and a lookalike number ran higher",
    "棚号 and 位置 are whole-value columns.",
    dict(prompt="东西两个区的监测表里，棚号为「3号」、位置为「上层」的最高湿度是多少（百分比）？口径见 大棚监测/说明.md，只回复数字。", agg="max", col="湿度", pred='r["棚号"]=="3号" and r["位置"]=="上层"',
         decoy=dict(pred='r["棚号"].startswith("3号") and r["位置"]=="上层"'), decoy_note="棚号前缀匹配，含3号(东)",
         cmd="""cat 大棚监测/*.dat | awk -F, '$2=="3号" && $3=="上层" {print $4}' | sort -rn | head -1""", unit="{v}%。",
         alts=["3号棚上层的湿度峰值是多少？", "棚号为3号、位置为上层的最大湿度值。", "按说明.md，3号上层最高湿度百分比。", "两个区里3号棚上层记录到的最高湿度。", "3号棚（不含3号(东)）上层的湿度最大值。"]), header=False, min_=1)

# ---------------------------------------------------------------- English (7)
mkc("tab-9414", "M9a", "aggregate", "ferrypax", "ferry", ["mon.txt", "tue.txt", "wed.txt", "thu.txt"], T, ["date", "route", "status", "seats"], (90, 120),
    ["# Ferry boarding logs", "", "One file per day, tab separated: date, route, status, seats (integer).", "Route and status are whole values: `R70` and `R17` are not `R7`, and `boarded-late` is not `boarded`."],
    lambda rng, i, fi, n: [f"2026-10-{fi + 6:02d}", choice(rng, ["R7", "R7", "R70", "R17", "R7-X"]), choice(rng, ["boarded", "boarded", "boarded-late", "no-show"]), str(rng.randint(1, 40))],
    "Sums boarded seats of one ferry route over four daily tables with look-alike route codes and a late-boarding status",
    "route and status are whole-value columns.",
    dict(prompt="Across the four daily ferry files, how many seats in total were boarded on route R7? ferry/README.md defines the match rules; reply with the number only.", agg="sum", col="seats", pred='r["route"]=="R7" and r["status"]=="boarded"',
         decoy=dict(pred='r["route"].startswith("R7") and r["status"].startswith("boarded")'), decoy_note="prefix match on route and status",
         cmd="""cat ferry/*.txt | awk -F'\\t' '$2=="R7" && $3=="boarded" {s+=$4} END{print s}'""", unit="{v} seats.",
         alts=["Total boarded seats for route R7 over the four days?", "Add up seats where route is R7 and status is boarded.", "Per ferry/README.md, how many seats boarded on R7?", "Sum the seats column for R7 rows with status boarded.", "What is the combined number of boarded seats on R7?"]))

mkc("tab-9415", "M9a", "filter_count", "helpdeskclosed", "helpdesk", ["q1.txt", "q2.txt", "q3.txt"], ",", ["opened", "queue", "status", "agent"], (110, 150),
    ["# Helpdesk export", "", "One file per quarter, comma separated: opened, queue, status, agent.", "Queue and status are whole values: `billing-eu` is a different queue, and `closed-dup` is a duplicate that was merged, not `closed`."],
    lambda rng, i, fi, n: [f"2026-{fi * 3 + rng.randint(1, 3):02d}-{rng.randint(1, 28):02d}", choice(rng, ["billing", "billing", "billing-eu", "shipping", "tech"]),
                           choice(rng, ["closed", "closed", "closed-dup", "open", "pending"]), choice(rng, ["ana", "ben", "chi", "dev"])],
    "Counts closed tickets of one queue over three quarterly exports with a regional queue and a duplicate-closed status as look-alikes",
    "queue and status are whole-value columns.",
    dict(prompt="How many tickets in the three quarterly exports are in the billing queue with status closed? The matching rules are in helpdesk/README.md. Reply with just the number.", agg="count", pred='r["queue"]=="billing" and r["status"]=="closed"',
         decoy=dict(pred='r["queue"].startswith("billing") and r["status"].startswith("closed")'), decoy_note="prefix match on queue and status",
         cmd="""cat helpdesk/*.txt | awk -F, '$2=="billing" && $3=="closed"' | wc -l""", unit="{v} tickets.",
         alts=["Count rows with queue billing and status closed across q1 to q3.", "Per helpdesk/README.md, how many billing tickets were closed?", "Number of closed tickets in the billing queue (not billing-eu).", "How many export rows have queue=billing and status=closed?", "Total closed billing tickets over the three quarters."]), min_=20)

mkc("log-9416", "M9a", "count_events", "mailclicks", "mailstats", ["send1.dat", "send2.dat", "send3.dat", "send4.dat"], ";", ["time", "email", "campaign", "event"], (80, 110),
    ["# Mail event feed", "", "One file per send, semicolon separated, no header: time;email;campaign;event.", "Campaign and event are whole values: `oct-sale-b` is the B variant of another test, and `click-bot` is a security scanner, not a `click`. Count each address once."],
    lambda rng, i, fi, n: [f"1010T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", f"u{rng.randint(100, 330)}@mail.example", choice(rng, ["oct-sale", "oct-sale", "oct-sale-b", "oct-news"]), choice(rng, ["click", "click", "click-bot", "open", "open"])],
    "Counts distinct recipients who clicked one campaign over four send files with a variant campaign and a scanner click event as look-alikes",
    "campaign and event are whole-value columns; addresses are de-duplicated across files.",
    dict(prompt="How many different recipients clicked in campaign oct-sale across the four send files? mailstats/README.md explains the exact matching; reply with the number only.", agg="distinct", col="email",
         pred='r["campaign"]=="oct-sale" and r["event"]=="click"', decoy=dict(pred='r["campaign"].startswith("oct-sale") and r["event"].startswith("click")'), decoy_note="prefix match on campaign and event",
         cmd="""cat mailstats/*.dat | awk -F';' '$3=="oct-sale" && $4=="click" {print $2}' | sort -u | wc -l""", unit="{v} recipients.",
         alts=["Unique addresses with a click event in oct-sale?", "Distinct emails where campaign is oct-sale and event is click.", "Per mailstats/README.md, how many people clicked oct-sale (each once)?", "How many distinct recipients clicked the oct-sale campaign, bots excluded?", "Number of different email addresses with a genuine click in oct-sale."]), header=False)

mkc("tab-9417", "M9a", "rank", "turbinerpm", "turbines", ["site1.dat", "site2.dat", "site3.dat"], " ", ["time", "turbine", "mode", "rpm"], (110, 150),
    ["# Turbine telemetry", "", "One file per site, space separated, no header: time turbine mode rpm (integer).", "Turbine and mode are whole values: `T-070`, `T-17` and `T-7` are not `T-07`, and `run-limited` is not `run`."],
    lambda rng, i, fi, n: (lambda t, m: [f"1011T{rng.randint(0, 23):02d}{rng.randint(0, 59):02d}", t, m, str(rint(rng, 800, 1700) if t == "T-07" and m == "run" else rint(rng, 800, 2100))])(
        choice(rng, ["T-07", "T-07", "T-070", "T-17", "T-7"]), choice(rng, ["run", "run", "run-limited", "idle"])),
    "Finds the highest rpm of one turbine in run mode over three site files where look-alike turbine codes and a limited mode ran higher",
    "turbine and mode are whole-value columns.",
    dict(prompt="Across the three site files, what is the highest rpm of turbine T-07 while in mode run? turbines/README.md has the matching rules; reply with the number only.", agg="max", col="rpm", pred='r["turbine"]=="T-07" and r["mode"]=="run"',
         decoy=dict(pred='r["turbine"].startswith("T-07") and r["mode"].startswith("run")'), decoy_note="prefix match on turbine and mode",
         cmd="""cat turbines/*.dat | awk '$2=="T-07" && $3=="run" {print $4}' | sort -rn | head -1""", unit="{v} rpm.",
         alts=["Peak rpm for T-07 in run mode?", "Maximum rpm where turbine is T-07 and mode is run.", "Per turbines/README.md, how fast did T-07 spin at most in run mode?", "Highest rpm reading of T-07 (mode run only).", "What is T-07's top rpm across the three sites, run mode?"]), header=False, min_=1)

mkc("tab-9418", "M9a", "aggregate", "irrigationl", "irrigation", ["mon.txt", "tue.txt", "wed.txt", "thu.txt", "fri.txt"], ",", ["date", "zone", "valve", "liters"], (80, 100),
    ["# Irrigation meter logs", "", "One file per weekday, comma separated: date, zone, valve, liters (integer).", "Zone and valve are whole values: `Z20`, `Z12` are not `Z2`, and `open-manual` is a hand-operated run, not `open`."],
    lambda rng, i, fi, n: [f"2026-10-{fi + 5:02d}", choice(rng, ["Z2", "Z2", "Z20", "Z12", "Z3"]), choice(rng, ["open", "open", "open-manual", "closed"]), str(rng.randint(5, 300))],
    "Sums litres of one irrigation zone with the valve open over five weekday tables with look-alike zone codes and a manual valve state",
    "zone and valve are whole-value columns.",
    dict(prompt="Over the five weekday meter files, how many litres in total were used in zone Z2 with the valve open? irrigation/README.md gives the matching rules; reply with the number only.", agg="sum", col="liters", pred='r["zone"]=="Z2" and r["valve"]=="open"',
         decoy=dict(pred='r["zone"].startswith("Z2") and r["valve"].startswith("open")'), decoy_note="prefix match on zone and valve",
         cmd="""cat irrigation/*.txt | awk -F, '$2=="Z2" && $3=="open" {s+=$4} END{print s}'""", unit="{v} litres.",
         alts=["Total litres for zone Z2 where valve is open?", "Sum the liters column for Z2 rows with valve open.", "Per irrigation/README.md, how much water did Z2 use with the valve open?", "Add the litres of all Z2/open records Monday to Friday.", "What is the weekly open-valve water use of zone Z2?"]))

mkc("tab-9419", "M9a", "rank", "inverterlow", "solar", ["d1.dat", "d2.dat", "d3.dat"], ";", ["ts", "unit", "state", "watts"], (110, 150),
    ["# Solar inverter samples", "", "One file per day, semicolon separated: ts;unit;state;watts (integer).", "Unit and state are whole values: `INV-30`, `INV-13` are not `INV-3`, and `grid-limited` is a curtailed state, not `grid`."],
    lambda rng, i, fi, n: (lambda u, s: [f"1011T{rng.randint(8, 17):02d}{rng.randint(0, 59):02d}", u, s, str(rint(rng, 900, 4000) if u == "INV-3" and s == "grid" else rint(rng, 100, 4000))])(
        choice(rng, ["INV-3", "INV-3", "INV-30", "INV-13", "INV-1"]), choice(rng, ["grid", "grid", "grid-limited", "off"])),
    "Finds the lowest output of one inverter while feeding the grid over three daily files where look-alike units and a curtailed state read lower",
    "unit and state are whole-value columns.",
    dict(prompt="Across the three daily sample files, what is the lowest watts value of inverter INV-3 while its state is grid? solar/README.md defines the match rules; reply with the number only.", agg="min", col="watts", pred='r["unit"]=="INV-3" and r["state"]=="grid"',
         decoy=dict(pred='r["unit"].startswith("INV-3") and r["state"].startswith("grid")'), decoy_note="prefix match on unit and state",
         cmd="""cat solar/*.dat | awk -F';' '$2=="INV-3" && $3=="grid" {print $4}' | sort -n | head -1""", unit="{v} W.",
         alts=["Minimum watts for INV-3 with state grid?", "Lowest output of INV-3 while feeding the grid.", "Per solar/README.md, what is INV-3's smallest watts reading in state grid?", "Smallest watts value among INV-3/grid samples.", "How low did INV-3 go while in grid state across the three days?"]), min_=1)

mkc("log-9420", "M9a", "count_events", "rsvpyes", "rsvp", ["list-a.txt", "list-b.txt", "list-c.txt"], T, ["time", "event", "reply", "guest"], (110, 150),
    ["# RSVP exports", "", "One file per invitation wave, tab separated: time, event, reply, guest.", "Event and reply are whole values: `Workshop-2` is a different event, and `yes+1` means the guest brings a plus-one, not a plain `yes`."],
    lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["Workshop", "Workshop", "Workshop-2", "Meetup", "Keynote"]), choice(rng, ["yes", "yes", "yes+1", "no", "maybe"]), f"g{rng.randint(100, 999)}"],
    "Counts plain yes replies for one event over three invitation-wave files with a numbered twin event and a plus-one reply as look-alikes",
    "event and reply are whole-value columns.",
    dict(prompt="How many RSVP rows in the three wave files are for event Workshop with reply yes? rsvp/README.md states the exact-match rules; reply with the number only.", agg="count", pred='r["event"]=="Workshop" and r["reply"]=="yes"',
         decoy=dict(pred='r["event"].startswith("Workshop") and r["reply"].startswith("yes")'), decoy_note="prefix match on event and reply",
         cmd="""cat rsvp/*.txt | awk -F'\\t' '$2=="Workshop" && $3=="yes"' | wc -l""", unit="{v} replies.",
         alts=["Count of plain yes replies to Workshop?", "Rows with event Workshop and reply yes, summed over all waves.", "Per rsvp/README.md, how many yes RSVPs does Workshop have?", "How many guests answered yes (not yes+1) for Workshop?", "Number of Workshop RSVP rows whose reply is exactly yes."]), min_=20)


def _mk(cid):
    return lambda: build(cid)


BUILDERS = []
for _cid in sorted(CASES):
    BUILDERS.append(_mk(_cid))
    BUILDERS[-1].__name__ = _cid.replace("-", "_")

# static SPEC (specs.py loads this file by path and needs it at import time)
for _cid, _c in CASES.items():
    SPEC[_cid] = dict(kind="bash_aggregate", sub=_c["sub"], needs=[f"{_c['root']}/{_c['readme_name']}"])
