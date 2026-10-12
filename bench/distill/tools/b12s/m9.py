"""M9 (bash) batch b12s of v1.41: ids 9321-9340, fresh data shapes over .txt/.dat tables.

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


def agg2(q, over, rows, prev):
    # over: extra keys (decoy) merged into q; a "minus" index makes the answer the absolute gap to that earlier turn's answer
    qq = {**q, **over}
    base = agg(qq["agg"], qq, rows)
    if q.get("minus") is not None:
        return abs(base - prev[q["minus"]])
    return base
'''
_ns = {}
exec(AGG_SRC, _ns)
agg = _ns["agg"]
agg2 = _ns["agg2"]
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
            vals, decs, firsts = [], [], []
            for q in qs:
                vals.append(agg2(q, {}, allrows, vals))
                decs.append(agg2(q, q["decoy"], allrows, decs))
                firsts.append(agg2(q, {}, first_rows, firsts) if len(c["names"]) > 1 else None)
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
            if f is not None and q["agg"] in ("sum", "count", "distinct", "top") and q.get("minus") is None:
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
                if q.get("minus") is not None:
                    ok = ok and near_tokens(files, float(v)) == 0
                elif q["agg"] in ("count", "distinct", "between", "first_line", "last_line", "max", "min"):
                    ok = ok and near_tokens(files, float(v)) == (1 if q["agg"] in ("max", "min") else 0)
        if ok:
            break
    else:
        raise SystemExit("%s: no seed found" % cid)
    readme_path = f"{c['root']}/{c['readme_name']}"
    data_paths = [f"{c['root']}/{n}" for n in c["names"]]
    qlist = [{k: v for k, v in q.items() if k in ("agg", "col", "pred", "group", "ret", "tie_col", "tie_pick", "extreme", "margin", "start", "end", "nth", "minus")} for q in qs]
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
vals = []
for q in QS:
    vals.append(agg2(q, {{}}, ALL, vals))
out = {{}}
sums = []
for q, val in zip(QS, vals):
    if q["agg"] == "sum" and q.get("minus") is None:
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
elif QS[-1]["agg"] != "sum" or QS[-1].get("minus") is not None:
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
            want = thousands(fmt(v)) if q["agg"] == "sum" and q.get("minus") is None else [fmt(v)]
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
        cid, desc=c["desc"], task_type=c["tt"], family="fam-%s-b12s-%s-01" % (cid.split("-")[0], c["topic"]), level=c.get("level", "L2"),
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


def rint(rng, lo, hi, step=1):
    return rng.randrange(lo, hi + 1, step)


def Q(prompt, agg, awk, f=None, col=None, pred=None, dpred=None, dnote="", unit="", alts=(), minus=None, cmd=None, **kw):
    q = dict(prompt=prompt, agg=agg, awk=awk, f=f, col=col, pred=pred, decoy=dict(pred=dpred) if dpred else {}, decoy_note=dnote, unit=unit, alts=list(alts), minus=minus)
    if "decoy" in kw:
        kw = dict(kw)
    if cmd:
        q["cmd"] = cmd
    q.update(kw)
    return q


def fld(q):
    return "$%d" % q["f"]


def mkcmd(c, qs):
    sep = c["sep"]
    farg = "" if sep == " " else "-F'%s' " % ("\\t" if sep == "\t" else sep)
    multi = len(c["names"]) > 1
    ext = c["names"][0].rsplit(".", 1)[1]
    pre = "cat %s/*.%s | " % (c["root"], ext) if multi else ""
    post = "" if multi else " %s/%s" % (c["root"], c["names"][0])
    for q in qs:
        if q.get("cmd"):
            continue
        k, cond = q["agg"], q["awk"]
        tail = ""
        if q.get("minus") is not None:
            p = qs[q["minus"]]
            inc = (lambda x: "+=" + fld(x)) if k == "sum" else (lambda x: "++")
            body = "%s {a%s} %s {b%s} END{d=a-b; if (d<0) d=-d; print d}" % (cond, inc(q), p["awk"], inc(p))
        elif k == "sum":
            body = "%s {s+=%s} END{print s}" % (cond, fld(q))
        elif k == "count":
            body = "%s {c++} END{print c+0}" % cond
        elif k == "distinct":
            body = "%s {print %s}" % (cond, fld(q))
            tail = " | sort -u | wc -l"
        else:
            raise ValueError(k)
        q["cmd"] = "%sawk %s'%s'%s%s" % (pre, farg, body, post, tail)
    return qs


def mk(cid, **kw):
    kw["queries"] = mkcmd(kw, kw["queries"])
    case(cid, **kw)


def filler_zh(rng):
    return choice(rng, ["常规批次处理完成_无需人工介入", "已同步到汇总库_下游确认收到", "设备心跳正常_链路延迟在阈值内", "本条由夜间任务补录_来源可信", "已通知值班人员_暂无后续动作",
                        "按排班表自动归档_保留九十天", "与上一条记录间隔正常_未触发合并", "质检抽样通过_批号已登记"])


def filler_en(rng):
    return choice(rng, ["synced-to-summary-store_downstream-acked", "heartbeat-ok_link-latency-within-threshold", "backfilled-by-nightly-job_source-trusted",
                        "on-call-notified_no-follow-up-needed", "archived-by-rota_retention-ninety-days", "interval-since-previous-normal_no-merge",
                        "sampling-check-passed_batch-registered", "routine-batch-finished_no-manual-step"])


def dd(rng, lo=1, hi=28):
    return rng.randint(lo, hi)


HOW = "（以磁盘上现在的文件内容为准）"

# ================================================================== M9a: several tables

# 9461 pharmacy dispatch, sum x3 (third = gap)
mk("tab-9461", sub="M9a", tt="aggregate", topic="pharmdispatch", root="药房出库", names=["第1周.txt", "第2周.txt", "第3周.txt"], sep=T,
   cols=["日期", "药品", "科室", "数量", "状态"], rows=(90, 120), readme_name="说明.md", min=1,
   readme=["# 药房出库说明", "", "每周一个文件，制表符分隔，第一行是表头：日期、药品、科室、数量（盒）、状态。", "药品按完整名称匹配：「阿莫西林克拉维酸」是另一种药，不是「阿莫西林」。状态按完整内容匹配：「已发(部分)」只发了一部分，不算「已发」。"],
   gen=lambda rng, i, fi, n: [f"2026-10-{fi * 7 + dd(rng, 1, 7):02d}", choice(rng, ["阿莫西林", "阿莫西林", "阿莫西林克拉维酸", "布洛芬", "二甲双胍"]),
                              choice(rng, ["急诊", "儿科", "内科", "骨科"]), str(rng.randint(2, 60)), choice(rng, ["已发", "已发", "已发", "已发(部分)", "退回", "待发"])],
   desc="Three turns over three weekly pharmacy tables: boxes of one drug dispensed in total, the same for one ward, then the gap to another ward, with a combination drug and a part-dispensed status as look-alikes",
   why="药品 and 状态 are whole-value columns of the tab-separated tables.",
   queries=[
       Q("三周的药房出库记录里，药品「阿莫西林」状态为「已发」的数量一共多少盒？口径见 药房出库/说明.md，回复数字。", "sum", '$2=="阿莫西林" && $5=="已发"', f=4, col="数量",
         pred='r["药品"]=="阿莫西林" and r["状态"]=="已发"', dpred='r["药品"].startswith("阿莫西林") and r["状态"].startswith("已发")', dnote="药品、状态前缀匹配", unit="阿莫西林已发共 {v} 盒。"),
       Q("只看急诊科，同样的药品和状态口径，已发数量合计是多少盒？" + HOW, "sum", '$2=="阿莫西林" && $5=="已发" && $3=="急诊"', f=4, col="数量",
         pred='r["药品"]=="阿莫西林" and r["状态"]=="已发" and r["科室"]=="急诊"', dpred='r["药品"].startswith("阿莫西林") and r["状态"].startswith("已发") and r["科室"]=="急诊"', dnote="药品、状态前缀匹配", unit="急诊已发共 {v} 盒。"),
       Q("儿科呢？同样口径算儿科的已发数量合计，告诉我它和上一问急诊的合计相差多少盒。" + HOW, "sum", '$2=="阿莫西林" && $5=="已发" && $3=="儿科"', f=4, col="数量", minus=1,
         pred='r["药品"]=="阿莫西林" and r["状态"]=="已发" and r["科室"]=="儿科"', dpred='r["药品"].startswith("阿莫西林") and r["状态"].startswith("已发") and r["科室"]=="儿科"', dnote="药品、状态前缀匹配",
         unit="儿科和急诊的已发数量合计相差 {v} 盒。",
         alts=["儿科的已发合计和急诊的差是多少盒？", "算出儿科已发数量，再告诉我它与急诊相差多少。", "儿科与急诊两个科室的阿莫西林已发数量差额。", "同样口径下儿科比急诊多或少多少盒（取差的绝对值）？", "儿科已发数量合计减去急诊的，差距有多大？"]),
   ])

# 9462 flights, English, two turns
mk("tab-9462", sub="M9a", tt="filter_count", topic="flightdelay", root="flights", names=["mon.dat", "tue.dat", "wed.dat"], sep=";",
   cols=["flight", "route", "status", "delay_min"], rows=(100, 130), readme_name="README.md", min=5, header=False,
   readme=["# Flight board", "", "One file per day, semicolon separated, no header: flight;route;status;delay_min.", "Route and status are whole values: route `PEK-CAN` is not `PEK-CAN2`, and status `DELAYED-WX` is a weather delay that the airline does not count as `DELAYED`."],
   gen=lambda rng, i, fi, n: [f"CA{rng.randint(1000, 1180)}", choice(rng, ["PEK-CAN", "PEK-CAN", "PEK-CAN2", "PEK-SHA", "SHA-CAN"]),
                              choice(rng, ["ON-TIME", "DELAYED", "DELAYED", "DELAYED-WX", "CANCELLED"]), str(rng.randint(0, 240))],
   desc="Two turns over three daily flight boards: how many PEK-CAN rows are DELAYED, then how many different flights were cancelled on that route, with a twin route and a weather-delay status as look-alikes",
   why="route and status are whole-value columns.",
   queries=[
       Q("How many PEK-CAN rows have status DELAYED across the three daily files? flights/README.md defines the terms; reply with the number.", "count", '$2=="PEK-CAN" && $3=="DELAYED"',
         pred='r["route"]=="PEK-CAN" and r["status"]=="DELAYED"', dpred='r["route"].startswith("PEK-CAN") and r["status"].startswith("DELAYED")', dnote="prefix match on route and status", unit="{v} PEK-CAN rows are DELAYED."),
       Q("On that same route, how many different flight numbers show up as CANCELLED? Count from what is on disk now, each flight once.", "distinct", '$2=="PEK-CAN" && $3=="CANCELLED"', f=1, col="flight",
         pred='r["route"]=="PEK-CAN" and r["status"]=="CANCELLED"', dpred='r["route"].startswith("PEK-CAN") and r["status"].startswith("CANCEL")', dnote="route prefix match includes PEK-CAN2",
         unit="{v} different PEK-CAN flights were cancelled.",
         alts=["Number of distinct flights with status CANCELLED on route PEK-CAN.", "How many unique flight numbers were cancelled on PEK-CAN (PEK-CAN2 excluded)?", "Across mon, tue and wed, count each cancelled PEK-CAN flight once.", "Per README, how many different flights on PEK-CAN have status CANCELLED?", "De-duplicated count of CANCELLED flights for the PEK-CAN route."]),
   ])

# 9463 fuel stations, count x3 (third = gap)
mk("tab-9463", sub="M9a", tt="filter_count", topic="fuelpump", root="加油站", names=["周一.txt", "周二.txt", "周三.txt"], sep=" ",
   cols=["日期", "油品", "枪号", "升数", "支付"], rows=(110, 140), readme_name="说明.md", min=5, header=False,
   readme=["# 加油站流水说明", "", "每天一个文件，空格分隔，没有表头：日期 油品 枪号 升数 支付。", "油品、支付都按完整内容匹配：「95#(乙醇)」是另一个油品，不是「95#」；「微信(优惠)」是活动支付，不算「微信」。"],
   gen=lambda rng, i, fi, n: [f"1020{fi + 1}", choice(rng, ["92#", "95#", "95#", "95#(乙醇)", "98#", "0#柴油"]), f"G{rng.randint(1, 8)}", str(rng.randint(101, 480)),
                              choice(rng, ["现金", "微信", "微信", "微信(优惠)", "油卡"])],
   desc="Three turns over three daily fuel tables: how many 95# fills were paid by WeChat, how many by fuel card, then the gap to cash, with an ethanol blend and a promotional payment as look-alikes",
   why="油品 and 支付 are whole-value columns of the space-separated tables.",
   queries=[
       Q("三天的加油流水里，油品「95#」用「微信」支付的有多少笔？口径见 加油站/说明.md，回复数字。", "count", '$2=="95#" && $5=="微信"',
         pred='r["油品"]=="95#" and r["支付"]=="微信"', dpred='r["油品"].startswith("95#") and r["支付"].startswith("微信")', dnote="油品、支付前缀匹配", unit="95# 微信支付共 {v} 笔。"),
       Q("95# 用「油卡」支付的呢，有多少笔？" + HOW, "count", '$2=="95#" && $5=="油卡"',
         pred='r["油品"]=="95#" and r["支付"]=="油卡"', dpred='r["油品"].startswith("95#") and r["支付"]=="油卡"', dnote="油品前缀匹配", unit="95# 油卡支付共 {v} 笔。"),
       Q("再算 95# 用「现金」支付的笔数，告诉我它比上一问的油卡支付多出或少了几笔（差的绝对值）。" + HOW, "count", '$2=="95#" && $5=="现金"', minus=1,
         pred='r["油品"]=="95#" and r["支付"]=="现金"', dpred='r["油品"].startswith("95#") and r["支付"]=="现金"', dnote="油品前缀匹配", unit="现金支付与油卡支付相差 {v} 笔。",
         alts=["95# 现金笔数和油卡笔数差多少？", "算出现金支付的笔数，再给我它和油卡支付笔数的差值。", "现金与油卡两种支付的 95# 笔数相差几笔？", "95# 现金支付比油卡支付多（或少）多少笔，取绝对值。", "把现金笔数减去油卡笔数，答案取绝对值是多少？"]),
   ])

# 9464 parking, distinct x2
mk("tab-9464", sub="M9a", tt="filter_count", topic="parkexit", root="停车场", names=["周六.txt", "周日.txt", "节假日.txt"], sep=",",
   cols=["日期", "车牌", "车型", "出口"], rows=(100, 140), readme_name="说明.md", min=10, header=True,
   readme=["# 停车场出场记录说明", "", "每个文件一类日期，逗号分隔，第一行是表头：日期、车牌、车型、出口。", "车型、出口都按完整内容匹配：「新能源(临牌)」是临时牌照，不算「新能源」；「东门(应急)」是应急通道，不算「东门」。同一车牌多次出场只算一辆。"],
   gen=lambda rng, i, fi, n: [f"2026-10-{rng.randint(1, 28):02d}", f"沪A{rng.randint(10100, 10420)}", choice(rng, ["小型车", "新能源", "新能源", "新能源(临牌)", "货车"]),
                              choice(rng, ["东门", "东门", "东门(应急)", "西门", "南门"])],
   desc="Two turns over three parking tables: distinct plates of new-energy cars leaving by the east gate, then distinct truck plates there, with a temporary-plate type and an emergency gate as look-alikes",
   why="车型 and 出口 are whole-value columns; plates are de-duplicated across files.",
   queries=[
       Q("三份出场记录里，从「东门」出场的「新能源」车一共有多少辆（同一车牌只算一辆）？口径见 停车场/说明.md。", "distinct", '$3=="新能源" && $4=="东门"', f=2, col="车牌",
         pred='r["车型"]=="新能源" and r["出口"]=="东门"', dpred='r["车型"].startswith("新能源") and r["出口"].startswith("东门")', dnote="车型、出口前缀匹配", unit="东门出场的新能源车共 {v} 辆。"),
       Q("同样从东门出场的「货车」呢？按磁盘上现在的文件重新数，同一车牌只算一辆。", "distinct", '$3=="货车" && $4=="东门"', f=2, col="车牌",
         pred='r["车型"]=="货车" and r["出口"]=="东门"', dpred='r["车型"].startswith("货车") and r["出口"].startswith("东门")', dnote="出口前缀匹配，含东门(应急)", unit="东门出场的货车共 {v} 辆。",
         alts=["东门出场的货车有几辆（车牌去重）？", "三个文件里车型为货车、出口为东门的不同车牌数量。", "按说明.md，东门（不含应急）出场的货车共多少辆？", "统计经东门出场的不同货车车牌数。", "东门出口的货车去重后是多少辆？"]),
   ])

# 9465 online course minutes, sum x3
mk("tab-9465", sub="M9a", tt="aggregate", topic="coursemin", root="网课学习", names=["9月.txt", "10月.txt", "11月.txt"], sep=";",
   cols=["日期", "学员", "课程", "分钟", "终端"], rows=(100, 130), readme_name="说明.md", min=1, header=True,
   readme=["# 网课学习时长说明", "", "每月一个文件，分号分隔，第一行是表头：日期;学员;课程;分钟;终端。", "课程按完整名称匹配：「Excel入门(试听)」是免费试听课，不是「Excel入门」。终端只有手机、电脑、平板三种。"],
   gen=lambda rng, i, fi, n: [f"2026-{9 + fi:02d}-{dd(rng):02d}", f"学员{rng.randint(101, 160)}", choice(rng, ["Excel入门", "Excel入门", "Excel入门(试听)", "数据分析", "Python基础"]),
                              str(rng.randint(5, 120)), choice(rng, ["手机", "电脑", "电脑", "平板"])],
   desc="Three turns over three monthly study-time tables: minutes of one course on phones, on computers, then the gap to tablets, with a free trial course sharing the name prefix",
   why="课程 and 终端 are whole-value columns.",
   queries=[
       Q("9 到 11 月的学习记录里，课程「Excel入门」在「手机」上的学习分钟数合计是多少？口径见 网课学习/说明.md，回复数字。", "sum", '$3=="Excel入门" && $5=="手机"', f=4, col="分钟",
         pred='r["课程"]=="Excel入门" and r["终端"]=="手机"', dpred='r["课程"].startswith("Excel入门") and r["终端"]=="手机"', dnote="课程前缀匹配，含试听课", unit="Excel入门在手机上共 {v} 分钟。"),
       Q("改成「电脑」呢？同一门课，电脑上的分钟数合计是多少？" + HOW, "sum", '$3=="Excel入门" && $5=="电脑"', f=4, col="分钟",
         pred='r["课程"]=="Excel入门" and r["终端"]=="电脑"', dpred='r["课程"].startswith("Excel入门") and r["终端"]=="电脑"', dnote="课程前缀匹配，含试听课", unit="Excel入门在电脑上共 {v} 分钟。"),
       Q("再算「平板」上的分钟数合计，告诉我它和上一问电脑合计相差多少分钟。" + HOW, "sum", '$3=="Excel入门" && $5=="平板"', f=4, col="分钟", minus=1,
         pred='r["课程"]=="Excel入门" and r["终端"]=="平板"', dpred='r["课程"].startswith("Excel入门") and r["终端"]=="平板"', dnote="课程前缀匹配，含试听课", unit="平板和电脑的分钟数合计相差 {v} 分钟。",
         alts=["平板上的 Excel入门 学习时长和电脑上的差多少分钟？", "算出平板分钟合计，再给我它与电脑合计的差值。", "同一门课，平板与电脑两种终端的分钟数相差多少？", "平板比电脑多（或少）多少分钟，取绝对值。", "电脑合计和平板合计之间的差距是多少分钟？"]),
   ])

# 9466 delivery, count x2
mk("tab-9466", sub="M9a", tt="filter_count", topic="deliveryslow", root="外卖配送", names=["周一.txt", "周二.txt", "周三.txt", "周四.txt"], sep=" ",
   cols=["时间", "骑手", "区域", "评价", "用时"], rows=(80, 110), readme_name="说明.md", min=5, header=False,
   readme=["# 外卖配送说明", "", "每天一个文件，空格分隔，没有表头：时间 骑手 区域 评价 用时(秒)。", "区域、评价都按完整内容匹配：「滨江新区」不是「滨江」；「超时(天气)」是恶劣天气免责，不算「超时」。"],
   gen=lambda rng, i, fi, n: [f"10{fi + 12}T{rng.randint(10, 21):02d}{rng.randint(0, 59):02d}", f"R{rng.randint(201, 290)}", choice(rng, ["滨江", "滨江", "滨江新区", "老城", "高新"]),
                              choice(rng, ["准时", "准时", "超时", "超时", "超时(天气)", "提前"]), str(rng.randint(1100, 4200))],
   desc="Two turns over four daily delivery tables: overtime orders in one district, then in another, with a longer district name and a weather-excused rating as look-alikes",
   why="区域 and 评价 are whole-value columns.",
   queries=[
       Q("四天的配送记录里，区域为「滨江」、评价为「超时」的订单有多少单？口径见 外卖配送/说明.md，回复数字。", "count", '$3=="滨江" && $4=="超时"',
         pred='r["区域"]=="滨江" and r["评价"]=="超时"', dpred='r["区域"].startswith("滨江") and r["评价"].startswith("超时")', dnote="区域、评价前缀匹配", unit="滨江超时订单共 {v} 单。"),
       Q("那「老城」区域评价为「超时」的呢？按磁盘上现在的文件重新数一遍。", "count", '$3=="老城" && $4=="超时"',
         pred='r["区域"]=="老城" and r["评价"]=="超时"', dpred='r["区域"]=="老城" and r["评价"].startswith("超时")', dnote="评价前缀匹配，含超时(天气)", unit="老城超时订单共 {v} 单。",
         alts=["老城区域超时的订单有几单？", "区域老城、评价超时的记录一共多少条？", "按说明.md，老城（天气免责不算）超时订单数量。", "四天里老城的超时单数是多少？", "统计区域为老城且评价恰好是超时的行数。"]),
   ])

# 9467 rainfall, English, sum x3
mk("tab-9467", sub="M9a", tt="aggregate", topic="rainstation", root="rain", names=["jun.txt", "jul.txt", "aug.txt"], sep=",",
   cols=["date", "station", "mm", "quality"], rows=(90, 120), readme_name="README.md", min=1, header=True,
   readme=["# Rain gauge exports", "", "One file per month, comma separated, header on the first line: date,station,mm,quality (integer mm).", "Station and quality are whole values: `XH-10` is not `XH-1`, and quality `ok-est` is an estimate filled in by the office, not a measured `ok`."],
   gen=lambda rng, i, fi, n: [f"2026{6 + fi:02d}{dd(rng):02d}", choice(rng, ["XH-1", "XH-1", "XH-10", "XH-2", "XH-2"]), str(rng.randint(0, 64)), choice(rng, ["ok", "ok", "ok", "suspect", "ok-est"])],
   desc="Three turns over three monthly rain gauge tables: rainfall of one station, of another, then the gap to a third, with a longer station code and an estimated quality flag as look-alikes",
   why="station and quality are whole-value columns.",
   queries=[
       Q("What is the total rainfall in mm at station XH-1 over June to August, counting only readings with quality ok? rain/README.md defines the terms; reply with the number.", "sum", '$2=="XH-1" && $4=="ok"', f=3, col="mm",
         pred='r["station"]=="XH-1" and r["quality"]=="ok"', dpred='r["station"].startswith("XH-1") and r["quality"].startswith("ok")', dnote="prefix match on station and quality", unit="XH-1 recorded {v} mm."),
       Q("Same quality rule for station XH-2: what is its total rainfall in mm? Use the files as they are on disk now.", "sum", '$2=="XH-2" && $4=="ok"', f=3, col="mm",
         pred='r["station"]=="XH-2" and r["quality"]=="ok"', dpred='r["station"].startswith("XH-2") and r["quality"].startswith("ok")', dnote="quality prefix match", unit="XH-2 recorded {v} mm."),
       Q("Now compute the same total for XH-10 and tell me how far it is from the XH-2 total of the previous question, in mm (absolute difference). Use the files as they are on disk now.", "sum", '$2=="XH-10" && $4=="ok"', f=3, col="mm", minus=1,
         pred='r["station"]=="XH-10" and r["quality"]=="ok"', dpred='r["station"].startswith("XH-1") and r["quality"].startswith("ok")', dnote="station prefix match includes XH-1", unit="XH-10 and XH-2 differ by {v} mm.",
         alts=["How many mm apart are the ok-quality rainfall totals of XH-10 and XH-2?", "Compute XH-10's rainfall total and give me its gap to XH-2's.", "Absolute difference between the XH-10 total and the XH-2 total (quality ok only).", "By how much does XH-10 differ from XH-2 in total ok rainfall?", "Work out XH-10's total, then subtract XH-2's and drop the sign."]),
   ])

# 9468 construction attendance, distinct x2
mk("tab-9468", sub="M9a", tt="filter_count", topic="sitecrew", root="工地考勤", names=["一标段.txt", "二标段.txt", "三标段.txt"], sep=T,
   cols=["日期", "工号", "工种", "状态"], rows=(110, 140), readme_name="说明.md", min=10, header=False,
   readme=["# 工地考勤说明", "", "每个标段一个文件，制表符分隔，没有表头：日期、工号、工种、状态。", "工种、状态都按完整内容匹配：「钢筋工(学徒)」不算「钢筋工」；「出勤(半天)」只上了半天，不算「出勤」。同一工号多天出勤只算一人。"],
   gen=lambda rng, i, fi, n: [f"10{rng.randint(1, 28):02d}", f"G{rng.randint(1001, 1260)}", choice(rng, ["钢筋工", "钢筋工", "钢筋工(学徒)", "木工", "木工", "瓦工"]),
                              choice(rng, ["出勤", "出勤", "出勤(半天)", "缺勤", "请假"])],
   desc="Two turns over three site attendance tables: distinct rebar workers who came in full days, then distinct carpenters, with an apprentice trade and a half-day status as look-alikes",
   why="工种 and 状态 are whole-value columns; worker ids are de-duplicated across files.",
   queries=[
       Q("三个标段的考勤里，工种为「钢筋工」、状态为「出勤」的不同工号有多少个？口径见 工地考勤/说明.md，回复数字。", "distinct", '$3=="钢筋工" && $4=="出勤"', f=2, col="工号",
         pred='r["工种"]=="钢筋工" and r["状态"]=="出勤"', dpred='r["工种"].startswith("钢筋工") and r["状态"].startswith("出勤")', dnote="工种、状态前缀匹配", unit="全勤出勤的钢筋工共 {v} 人。"),
       Q("工种改成「木工」，状态还是「出勤」，不同工号有多少个？以磁盘上现在的文件内容为准。", "distinct", '$3=="木工" && $4=="出勤"', f=2, col="工号",
         pred='r["工种"]=="木工" and r["状态"]=="出勤"', dpred='r["工种"]=="木工" and r["状态"].startswith("出勤")', dnote="状态前缀匹配，含出勤(半天)", unit="出勤的木工共 {v} 人。",
         alts=["木工里出勤过的有多少人（工号去重）？", "工种为木工、状态为出勤的不同工号数。", "按说明.md，出勤（不含半天）的木工共几人？", "三个标段中木工的出勤人数，每个工号只算一次。", "统计木工出勤记录里不同工号的个数。"]),
   ])

# 9469 fruit wholesale, sum x3
mk("tab-9469", sub="M9a", tt="aggregate", topic="fruitbox", root="果品批发", names=["周一.dat", "周二.dat", "周三.dat"], sep=";",
   cols=["日期", "品种", "产地", "箱数", "结算"], rows=(90, 120), readme_name="说明.md", min=1, header=True,
   readme=["# 果品批发说明", "", "每天一个文件，分号分隔，第一行是表头：日期;品种;产地;箱数;结算。", "品种、产地、结算都按完整内容匹配：「红富士(次果)」是降级果，不算「红富士」；「烟台(冷库)」是冷库转售，不算「烟台」；「已结(挂账)」没收到钱，不算「已结」。"],
   gen=lambda rng, i, fi, n: [f"1015{fi}", choice(rng, ["红富士", "红富士", "红富士(次果)", "砂糖橘", "巨峰葡萄"]), choice(rng, ["烟台", "烟台", "烟台(冷库)", "洛川", "洛川", "栖霞"]),
                              str(rng.randint(3, 80)), choice(rng, ["已结", "已结", "已结(挂账)", "未结"])],
   desc="Three turns over three daily fruit wholesale tables: settled boxes of one variety, narrowed to one origin, then the gap to another origin, with grade, cold-store and on-account look-alikes",
   why="品种, 产地 and 结算 are whole-value columns.",
   queries=[
       Q("三天的批发记录里，品种「红富士」结算为「已结」的箱数一共多少箱？口径见 果品批发/说明.md，回复数字。", "sum", '$2=="红富士" && $5=="已结"', f=4, col="箱数",
         pred='r["品种"]=="红富士" and r["结算"]=="已结"', dpred='r["品种"].startswith("红富士") and r["结算"].startswith("已结")', dnote="品种、结算前缀匹配", unit="红富士已结共 {v} 箱。"),
       Q("只算产地为「烟台」的，品种和结算口径不变，是多少箱？以磁盘上现在的文件内容为准。", "sum", '$2=="红富士" && $5=="已结" && $3=="烟台"', f=4, col="箱数",
         pred='r["品种"]=="红富士" and r["结算"]=="已结" and r["产地"]=="烟台"', dpred='r["品种"].startswith("红富士") and r["结算"].startswith("已结") and r["产地"].startswith("烟台")', dnote="三列都是前缀匹配", unit="烟台产的红富士已结共 {v} 箱。"),
       Q("产地换成「洛川」，同样口径的箱数合计也算出来，告诉我它和上一问烟台的合计差多少箱。以磁盘上现在的文件内容为准。", "sum", '$2=="红富士" && $5=="已结" && $3=="洛川"', f=4, col="箱数", minus=1,
         pred='r["品种"]=="红富士" and r["结算"]=="已结" and r["产地"]=="洛川"', dpred='r["品种"].startswith("红富士") and r["结算"].startswith("已结") and r["产地"].startswith("洛川")', dnote="三列都是前缀匹配", unit="洛川和烟台的已结箱数相差 {v} 箱。",
         alts=["洛川产红富士已结箱数和烟台的差多少？", "算出洛川的已结红富士箱数，再给我它与烟台的差值。", "两个产地（洛川、烟台）的红富士已结箱数相差多少箱？", "洛川比烟台多或少多少箱，取绝对值。", "同样口径下洛川合计减去烟台合计，绝对值是多少？"]),
   ])

# 9470 shared bikes, count x2
mk("tab-9470", sub="M9a", tt="filter_count", topic="bikerent", root="单车租借", names=["早高峰.txt", "晚高峰.txt"], sep=" ",
   cols=["日期", "车号", "站点", "类型", "时长"], rows=(150, 190), readme_name="说明.md", min=5, header=False,
   readme=["# 单车租借说明", "", "早、晚高峰各一个文件，空格分隔，没有表头：日期 车号 站点 类型 时长(分钟)。", "站点、类型都按完整内容匹配：「地铁口(南)」是另一个站点，不是「地铁口」；「电单车(试用)」是试运营车辆，不算「电单车」。"],
   gen=lambda rng, i, fi, n: [f"1018", f"B{rng.randint(1000, 1400)}", choice(rng, ["地铁口", "地铁口", "地铁口(南)", "公园东门", "大学城"]), choice(rng, ["电单车", "电单车", "电单车(试用)", "普通车", "普通车"]), str(rng.randint(3, 55))],
   desc="Two turns over two rush-hour rental tables: electric bike rentals at one stop, then ordinary bike rentals there, with a twin stop and a trial vehicle type as look-alikes",
   why="站点 and 类型 are whole-value columns.",
   queries=[
       Q("早晚两个高峰的记录里，站点「地铁口」租出「电单车」的有多少次？口径见 单车租借/说明.md，回复数字。", "count", '$3=="地铁口" && $4=="电单车"',
         pred='r["站点"]=="地铁口" and r["类型"]=="电单车"', dpred='r["站点"].startswith("地铁口") and r["类型"].startswith("电单车")', dnote="站点、类型前缀匹配", unit="地铁口电单车租借共 {v} 次。"),
       Q("同一个站点，类型为「普通车」的租借有多少次？按磁盘上现在的文件重新数。", "count", '$3=="地铁口" && $4=="普通车"',
         pred='r["站点"]=="地铁口" and r["类型"]=="普通车"', dpred='r["站点"].startswith("地铁口") and r["类型"]=="普通车"', dnote="站点前缀匹配，含地铁口(南)", unit="地铁口普通车租借共 {v} 次。",
         alts=["地铁口站点普通车被租了几次？", "站点为地铁口、类型为普通车的记录条数。", "按说明.md，地铁口（不含南口）的普通车租借次数。", "早晚高峰合计，地铁口租出普通车多少次？", "统计站点恰好是地铁口且类型是普通车的行数。"]),
   ])


# ================================================================== M9c: one long file

# 9471 service restarts, English, count x3
def restart_gen(rng, i, fi, n):
    return [f"1013T{(i * 19) // 3600 % 24:02d}{(i * 19) // 60 % 60:02d}", choice(rng, ["api-gw", "api-gw", "api-gw-canary", "worker", "worker", "cache"]),
            choice(rng, ["oom", "oom", "oom-softlimit", "deploy", "deploy", "crashloop"]), filler_en(rng)]


mk("log-9471", sub="M9c", tt="count_events", topic="svcrestart", root="svc", names=["restarts.txt"], sep=" ",
   cols=["time", "unit", "reason", "note"], header=False, rows=(1200, 1300), readme_name="README.md", min=5, gen=restart_gen,
   readme=["# Restart journal", "", "restarts.txt is one day of service restarts, space separated, no header: time unit reason note.", "Unit and reason are whole values: `api-gw-canary` is a separate deployment from `api-gw`, and `oom-softlimit` is a memory warning that did not kill the process, so it is not `oom`."],
   desc="Three turns over one long restart journal: OOM restarts of one service, its deploy restarts, then the gap to another service's OOM restarts, with a canary deployment and a soft-limit reason as look-alikes",
   why="unit and reason are whole-value columns.",
   queries=[
       Q("How many times did api-gw restart because of oom in svc/restarts.txt? svc/README.md defines the terms; reply with the number.", "count", '$2=="api-gw" && $3=="oom"',
         pred='r["unit"]=="api-gw" and r["reason"]=="oom"', dpred='r["unit"].startswith("api-gw") and r["reason"].startswith("oom")', dnote="prefix match on unit and reason", unit="api-gw restarted {v} times because of oom."),
       Q("And how many api-gw restarts have reason deploy? Count from the file as it is on disk now.", "count", '$2=="api-gw" && $3=="deploy"',
         pred='r["unit"]=="api-gw" and r["reason"]=="deploy"', dpred='r["unit"].startswith("api-gw") and r["reason"]=="deploy"', dnote="unit prefix match includes api-gw-canary", unit="api-gw restarted {v} times for deploys."),
       Q("Now count the oom restarts of worker and tell me how far that count is from the api-gw oom count in my first question (absolute difference). Read the file as it is on disk now.", "count", '$2=="worker" && $3=="oom"', minus=0,
         pred='r["unit"]=="worker" and r["reason"]=="oom"', dpred='r["unit"]=="worker" and r["reason"].startswith("oom")', dnote="reason prefix match includes oom-softlimit", unit="worker's oom count differs from api-gw's by {v}.",
         alts=["How many more or fewer oom restarts does worker have than api-gw? Give the absolute gap.", "Count worker's oom restarts, then give me the difference to api-gw's oom count.", "Absolute difference between the oom restart counts of worker and api-gw.", "Compare oom restarts: worker versus api-gw, how big is the gap?", "Work out worker's oom count and subtract api-gw's, ignoring the sign."]),
   ])

# 9472 subscription renewals, sum x2
def sub_gen(rng, i, fi, n):
    return [f"2026-10-{dd(rng):02d}", f"U{rng.randint(10001, 10900)}", choice(rng, ["专业版", "专业版", "专业版(教育)", "团队版", "团队版", "基础版"]),
            choice(rng, ["成功", "成功", "成功(重试)", "失败", "退款"]), str(rng.randint(20, 900)), filler_zh(rng)]


mk("tab-9472", sub="M9c", tt="aggregate", topic="subrenew", root="订阅", names=["续费.txt"], sep=T,
   cols=["日期", "用户", "套餐", "状态", "金额元", "备注"], header=True, rows=(1200, 1300), readme_name="说明.md", min=1, gen=sub_gen,
   readme=["# 订阅续费说明", "", "续费.txt 是整月的续费流水，制表符分隔，第一行是表头：日期、用户、套餐、状态、金额（元，整数）、备注。", "套餐、状态都按完整内容匹配：「专业版(教育)」是教育优惠套餐，不是「专业版」；「成功(重试)」是扣款失败后重试才成功，财务单独核算，不算「成功」。"],
   desc="Two turns over one long renewal ledger: revenue of one plan with successful charges, then another plan, with an education variant and a retried-success status as look-alikes",
   why="套餐 and 状态 are whole-value columns.",
   queries=[
       Q("订阅/续费.txt 里，套餐「专业版」状态为「成功」的金额一共多少元？口径见 订阅/说明.md，回复数字。", "sum", '$3=="专业版" && $4=="成功"', f=5, col="金额元",
         pred='r["套餐"]=="专业版" and r["状态"]=="成功"', dpred='r["套餐"].startswith("专业版") and r["状态"].startswith("成功")', dnote="套餐、状态前缀匹配", unit="专业版成功扣款共 {v} 元。"),
       Q("套餐换成「团队版」，状态口径不变，金额合计是多少元？以磁盘上现在的文件内容为准。", "sum", '$3=="团队版" && $4=="成功"', f=5, col="金额元",
         pred='r["套餐"]=="团队版" and r["状态"]=="成功"', dpred='r["套餐"]=="团队版" and r["状态"].startswith("成功")', dnote="状态前缀匹配，含成功(重试)", unit="团队版成功扣款共 {v} 元。",
         alts=["团队版成功扣款的金额加起来是多少元？", "套餐为团队版、状态为成功的金额元之和。", "按说明.md，团队版（重试成功不算）的收入合计。", "续费.txt 里团队版成功的金额总和。", "统计套餐是团队版且状态恰好是成功的金额。"]),
   ])

# 9473 stocktake window, between x3 (gap)
def take_gen(rng, i, fi, n):
    marks = {int(n * 0.08): "盘点开始(演练)", int(n * 0.20): "盘点结束(演练)", int(n * 0.40): "盘点开始", int(n * 0.66): "盘点结束"}
    stamp = f"1016T{(i * 21) // 3600 % 24:02d}{(i * 21) // 60 % 60:02d}"
    if i in marks:
        return [stamp, "MARK", "总控", marks[i], "-"]
    return [stamp, choice(rng, ["正常", "正常", "正常", "差异", "差异(已核销)", "漏扫", "待复核"], [30, 30, 30, 9, 5, 8, 8]), choice(rng, ["A区", "B区", "C区"]), filler_zh(rng), "-"]


_ST = 'r["级别"]=="MARK" and r["信息"]=="盘点开始"'
_EN = 'r["级别"]=="MARK" and r["信息"]=="盘点结束"'


def _dec(level):
    return dict(start='r["信息"].startswith("盘点开始")', end='r["信息"].startswith("盘点结束")', pred='r["级别"].startswith("%s")' % level)


def _cmd(level):
    return ("""awk -F';' '$2=="MARK" && $4=="盘点开始" {on=1; next} $2=="MARK" && $4=="盘点结束" {on=0} on && $2=="%s" {c++} END{print c+0}' 盘点/现场记录.txt""" % level)


mk("log-9473", sub="M9c", tt="time_window", topic="stocktakewin", root="盘点", names=["现场记录.txt"], sep=";",
   cols=["时间", "级别", "区域", "信息", "备注"], header=False, rows=(1150, 1250), readme_name="说明.md", min=5, gen=take_gen,
   readme=["# 盘点现场记录说明", "", "现场记录.txt 是一次盘点的完整记录，分号分隔，没有表头：时间;级别;区域;信息;备注，按时间追加。", "级别为 MARK 的行是窗口标记。真正的盘点窗口从「盘点开始」到「盘点结束」；带「(演练)」的是演练标记，不算窗口。", "级别按完整内容匹配：「差异(已核销)」已处理完，不算「差异」。"],
   desc="Three turns over one long stocktake record: lines of one level inside the real stocktake window, another level, then the gap, with a rehearsal window and a written-off level as look-alikes",
   why="The window is delimited by two exact MARK rows and levels are whole values.",
   queries=[
       Q("盘点/现场记录.txt 里，「盘点开始」和「盘点结束」之间级别为「差异」的行有多少条？窗口怎么认见 盘点/说明.md，回复数字。", "between", None, nth=1,
         start=_ST, end=_EN, pred='r["级别"]=="差异"', decoy=_dec("差异"), dnote="第一个开始标记是演练、级别前缀匹配", unit="盘点窗口内有 {v} 条差异。", cmd=_cmd("差异")),
       Q("同一个窗口里，级别为「漏扫」的有多少条？以磁盘上现在的文件内容为准。", "between", None, nth=1,
         start=_ST, end=_EN, pred='r["级别"]=="漏扫"', decoy=_dec("漏扫"), dnote="第一个开始标记是演练", unit="盘点窗口内有 {v} 条漏扫。", cmd=_cmd("漏扫")),
       Q("再看「待复核」：窗口里这个级别有多少条？告诉我它和上一问漏扫条数相差多少（绝对值）。以磁盘上现在的文件内容为准。", "between", None, nth=1, minus=1,
         start=_ST, end=_EN, pred='r["级别"]=="待复核"', decoy=_dec("待复核"), dnote="第一个开始标记是演练", unit="待复核与漏扫的条数相差 {v}。",
         cmd="""awk -F';' '$2=="MARK" && $4=="盘点开始" {on=1; next} $2=="MARK" && $4=="盘点结束" {on=0} on && $2=="待复核" {a++} on && $2=="漏扫" {b++} END{d=a-b; if (d<0) d=-d; print d}' 盘点/现场记录.txt""",
         alts=["窗口内待复核和漏扫的条数差多少？", "算出待复核的条数，再给我它与漏扫条数的差值。", "盘点窗口里待复核比漏扫多（或少）多少条，取绝对值。", "待复核与漏扫两种级别在窗口内的数量差距。", "待复核条数减漏扫条数，答案取绝对值。"]),
   ])

# 9474 greenhouse sensors, distinct x2
def gh_gen(rng, i, fi, n):
    return [f"1017T{(i * 20) // 3600 % 24:02d}{(i * 20) // 60 % 60:02d}", choice(rng, ["3号", "3号", "3号东", "1号", "2号"]), f"S{rng.randint(101, 260)}",
            choice(rng, ["告警", "告警", "告警(已恢复)", "正常", "维护"], [8, 8, 5, 30, 6]), filler_zh(rng)]


mk("log-9474", sub="M9c", tt="count_events", topic="greenalarm", root="温室", names=["记录.txt"], sep=" ",
   cols=["时间", "大棚", "设备", "事件", "备注"], header=False, rows=(1250, 1350), readme_name="说明.md", min=10, gen=gh_gen,
   readme=["# 温室传感器记录说明", "", "记录.txt 是一天的全部事件，空格分隔，没有表头：时间 大棚 设备 事件 备注。", "大棚、事件都按完整内容匹配：「3号东」是另一个棚，不是「3号」；「告警(已恢复)」是自动恢复的瞬时告警，不算「告警」。同一设备多次触发只算一台。"],
   desc="Two turns over one long greenhouse event file: distinct devices alarming in one greenhouse, then distinct devices under maintenance there, with a twin greenhouse and a recovered alarm as look-alikes",
   why="大棚 and 事件 are whole-value columns; devices are de-duplicated.",
   queries=[
       Q("温室/记录.txt 里，「3号」大棚发出过「告警」的设备有多少台（同一台只算一次）？口径见 温室/说明.md，回复数字。", "distinct", '$2=="3号" && $4=="告警"', f=3, col="设备",
         pred='r["大棚"]=="3号" and r["事件"]=="告警"', dpred='r["大棚"].startswith("3号") and r["事件"].startswith("告警")', dnote="大棚、事件前缀匹配", unit="3号大棚告警过的设备共 {v} 台。"),
       Q("同样是 3号大棚，事件为「维护」的设备有多少台？按磁盘上现在的文件重新数，同一台只算一次。", "distinct", '$2=="3号" && $4=="维护"', f=3, col="设备",
         pred='r["大棚"]=="3号" and r["事件"]=="维护"', dpred='r["大棚"].startswith("3号") and r["事件"]=="维护"', dnote="大棚前缀匹配，含3号东", unit="3号大棚维护过的设备共 {v} 台。",
         alts=["3号大棚里有多少台设备做过维护？", "大棚为3号、事件为维护的不同设备数。", "按说明.md，3号棚（不含3号东）维护的设备去重后多少台？", "统计3号大棚维护事件涉及的设备台数，每台只算一次。", "记录里3号大棚被维护过的不同设备个数。"]),
   ])

# 9475 payment gateway, English, sum x3
def pay_gen(rng, i, fi, n):
    return [f"1019T{(i * 18) // 3600 % 24:02d}{(i * 18) // 60 % 60:02d}", choice(rng, ["M-17", "M-17", "M-170", "M-18", "M-18", "M-40"]), choice(rng, ["card", "card", "wallet", "wallet", "transfer"]),
            choice(rng, ["ok", "ok", "ok", "ok-review", "declined"]), str(rng.randint(5, 900)), filler_en(rng)]


mk("tab-9475", sub="M9c", tt="aggregate", topic="gwsettle", root="pay", names=["txns.txt"], sep=",",
   cols=["time", "merchant", "method", "result", "amount", "note"], header=False, rows=(1200, 1300), readme_name="README.md", min=1, gen=pay_gen,
   readme=["# Gateway transactions", "", "txns.txt is one day of payments, comma separated, no header: time,merchant,method,result,amount,note (amount in whole yuan).", "Merchant and result are whole values: `M-170` is not `M-17`, and `ok-review` is a payment held for manual review, not settled, so it is not `ok`."],
   desc="Three turns over one long gateway file: settled amount of one merchant by card, by wallet, then the gap to another merchant's card total, with a longer merchant id and a held result as look-alikes",
   why="merchant, method and result are whole-value columns.",
   queries=[
       Q("In pay/txns.txt, what is the total amount for merchant M-17 with method card and result ok? pay/README.md defines the terms; reply with the number.", "sum", '$2=="M-17" && $3=="card" && $4=="ok"', f=5, col="amount",
         pred='r["merchant"]=="M-17" and r["method"]=="card" and r["result"]=="ok"', dpred='r["merchant"].startswith("M-17") and r["method"]=="card" and r["result"].startswith("ok")', dnote="prefix match on merchant and result", unit="M-17 settled {v} yuan by card."),
       Q("Same merchant and result, but method wallet: what is the total amount? Use the file as it is on disk now.", "sum", '$2=="M-17" && $3=="wallet" && $4=="ok"', f=5, col="amount",
         pred='r["merchant"]=="M-17" and r["method"]=="wallet" and r["result"]=="ok"', dpred='r["merchant"].startswith("M-17") and r["method"]=="wallet" and r["result"].startswith("ok")', dnote="prefix match on merchant and result", unit="M-17 settled {v} yuan by wallet."),
       Q("Now take merchant M-18, method wallet, result ok, and tell me how far its total is from the M-17 wallet total of the previous question, in yuan (absolute difference). Use the file as it is on disk now.", "sum", '$2=="M-18" && $3=="wallet" && $4=="ok"', f=5, col="amount", minus=1,
         pred='r["merchant"]=="M-18" and r["method"]=="wallet" and r["result"]=="ok"', dpred='r["merchant"]=="M-18" and r["method"]=="wallet" and r["result"].startswith("ok")', dnote="result prefix match includes ok-review", unit="M-18 and M-17 wallet totals differ by {v} yuan.",
         alts=["What is the gap between M-18's wallet total and M-17's?", "Compute M-18's settled wallet amount, then give me its difference to M-17's.", "By how many yuan do the M-18 and M-17 wallet totals differ?", "Absolute difference of the settled wallet totals, M-18 versus M-17.", "Work out M-18's wallet total and subtract M-17's, dropping the sign."]),
   ])

# 9476 bus swipes, distinct x2
def bus_gen(rng, i, fi, n):
    return [f"1020T{(i * 17) // 3600 % 24:02d}{(i * 17) // 60 % 60:02d}", choice(rng, ["7路", "7路", "17路", "27路", "35路"]), f"C{rng.randint(1000, 1250)}",
            choice(rng, ["成人卡", "成人卡", "成人卡(月票)", "学生卡", "老年卡"]), filler_zh(rng)]


mk("log-9476", sub="M9c", tt="count_events", topic="busswipe", root="公交刷卡", names=["刷卡.txt"], sep=T,
   cols=["时间", "线路", "卡号", "卡类型", "备注"], header=False, rows=(1250, 1350), readme_name="说明.md", min=10, gen=bus_gen,
   readme=["# 公交刷卡说明", "", "刷卡.txt 是一天的刷卡明细，制表符分隔，没有表头：时间、线路、卡号、卡类型、备注。", "线路、卡类型都按完整内容匹配：「17路」「27路」不是「7路」；「成人卡(月票)」是月票，不算「成人卡」。同一张卡多次刷卡只算一张。"],
   desc="Two turns over one long bus swipe file: distinct adult cards on one route, then distinct student cards on it, with longer route numbers and a monthly pass type as look-alikes",
   why="线路 and 卡类型 are whole-value columns; card numbers are de-duplicated.",
   queries=[
       Q("公交刷卡/刷卡.txt 里，「7路」上刷过「成人卡」的不同卡号有多少个？口径见 公交刷卡/说明.md，回复数字。", "distinct", '$2=="7路" && $4=="成人卡"', f=3, col="卡号",
         pred='r["线路"]=="7路" and r["卡类型"]=="成人卡"', dpred='"7路" in r["线路"] and r["卡类型"].startswith("成人卡")', dnote="线路包含7路、卡类型前缀匹配", unit="7路上刷过成人卡的不同卡号共 {v} 个。"),
       Q("还是7路，卡类型改成「学生卡」，不同卡号有多少个？以磁盘上现在的文件内容为准。", "distinct", '$2=="7路" && $4=="学生卡"', f=3, col="卡号",
         pred='r["线路"]=="7路" and r["卡类型"]=="学生卡"', dpred='"7路" in r["线路"] and r["卡类型"]=="学生卡"', dnote="线路包含7路，含17路、27路", unit="7路上刷过学生卡的不同卡号共 {v} 个。",
         alts=["7路学生卡刷了多少张不同的卡？", "线路7路、卡类型学生卡的卡号去重数量。", "按说明.md，7路（不含17路、27路）的学生卡有几张不同的卡？", "统计7路上学生卡的不同卡号个数。", "刷卡.txt 中7路的学生卡，去重后是多少张？"]),
   ])

# 9477 slow queries, count x3 with threshold
def slow_gen(rng, i, fi, n):
    ms = rng.choice([rng.randint(80, 1900), rng.randint(80, 3900), 2000, rng.randint(2000, 8000)])
    return [f"1021T{(i * 16) // 3600 % 24:02d}{(i * 16) // 60 % 60:02d}", choice(rng, ["orders", "orders", "orders_bak", "users", "users", "pay"]),
            choice(rng, ["SELECT", "SELECT", "SELECT-FOR-UPDATE", "UPDATE", "UPDATE", "INSERT"]), str(ms), filler_en(rng)]


mk("log-9477", sub="M9c", tt="count_events", topic="slowsql", root="慢查询", names=["slow.txt"], sep=";",
   cols=["时间", "库", "语句", "耗时ms", "摘要"], header=False, rows=(1250, 1350), readme_name="说明.md", min=5, gen=slow_gen,
   readme=["# 慢查询日志说明", "", "slow.txt 是一天的查询记录，分号分隔，没有表头：时间;库;语句;耗时(ms);摘要。", "库、语句都按完整内容匹配：「orders_bak」是备份库，不是「orders」；「SELECT-FOR-UPDATE」是加锁读，不算「SELECT」。「慢」指耗时大于等于 2000 毫秒（含 2000）。"],
   desc="Three turns over one long slow-query log: slow SELECTs on one database, slow UPDATEs there, then the gap to another database's slow SELECTs, with a backup database, a locking read and an exact-threshold boundary as look-alikes",
   why="库 and 语句 are whole-value columns and the threshold is inclusive at 2000.",
   queries=[
       Q("慢查询/slow.txt 里，库「orders」中语句为「SELECT」且耗时达到慢查询标准的有多少条？标准见 慢查询/说明.md，回复数字。", "count", '$2=="orders" && $3=="SELECT" && $4>=2000',
         pred='r["库"]=="orders" and r["语句"]=="SELECT" and int(r["耗时ms"])>=2000', dpred='r["库"].startswith("orders") and r["语句"].startswith("SELECT") and int(r["耗时ms"])>2000', dnote="库、语句前缀匹配且阈值不含2000", unit="orders 库的慢 SELECT 共 {v} 条。"),
       Q("同一个库，语句换成「UPDATE」，慢查询有多少条？以磁盘上现在的文件内容为准。", "count", '$2=="orders" && $3=="UPDATE" && $4>=2000',
         pred='r["库"]=="orders" and r["语句"]=="UPDATE" and int(r["耗时ms"])>=2000', dpred='r["库"].startswith("orders") and r["语句"]=="UPDATE" and int(r["耗时ms"])>2000', dnote="库前缀匹配且阈值不含2000", unit="orders 库的慢 UPDATE 共 {v} 条。"),
       Q("再看库「users」的慢 SELECT 有多少条，告诉我它和第一问 orders 库慢 SELECT 的条数相差多少（绝对值）。以磁盘上现在的文件内容为准。", "count", '$2=="users" && $3=="SELECT" && $4>=2000', minus=0,
         pred='r["库"]=="users" and r["语句"]=="SELECT" and int(r["耗时ms"])>=2000', dpred='r["库"]=="users" and r["语句"].startswith("SELECT") and int(r["耗时ms"])>2000', dnote="语句前缀匹配且阈值不含2000", unit="users 与 orders 的慢 SELECT 条数相差 {v}。",
         alts=["users 库慢 SELECT 的条数和 orders 库的差多少？", "算出 users 的慢 SELECT 条数，再给我它与 orders 的差值。", "两个库的慢 SELECT 数量（users 对 orders）相差几条？", "users 比 orders 多或少多少条慢 SELECT，取绝对值。", "users 慢 SELECT 条数减去 orders 的，答案取绝对值。"]),
   ])

# 9478 cron runs, English, count then sum
def cron_gen(rng, i, fi, n):
    return [f"1022T{(i * 15) // 3600 % 24:02d}{(i * 15) // 60 % 60:02d}", choice(rng, ["backup-db", "backup-db", "backup-db-weekly", "rotate-logs", "sync-cdn"]), f"h{rng.randint(1, 9)}",
            choice(rng, ["OK", "OK", "FAIL", "FAIL", "FAIL-RETRY", "TIMEOUT"]), str(rng.randint(2, 300)), filler_en(rng)]


mk("log-9478", sub="M9c", tt="count_events", topic="cronruns", root="cron", names=["runs.txt"], sep=" ",
   cols=["time", "job", "host", "status", "secs", "note"], header=False, rows=(1250, 1350), readme_name="README.md", min=5, gen=cron_gen,
   readme=["# Cron run journal", "", "runs.txt is one day of job runs, space separated, no header: time job host status secs note.", "Job and status are whole values: `backup-db-weekly` is a different job from `backup-db`, and `FAIL-RETRY` is a failure that the scheduler retried successfully later, so it is not `FAIL`."],
   desc="Two turns over one long cron journal: failed runs of one job, then total seconds of its successful runs, with a weekly variant job and a retried-failure status as look-alikes",
   why="job and status are whole-value columns.",
   queries=[
       Q("How many runs of the job backup-db have status FAIL in cron/runs.txt? cron/README.md defines the terms; reply with the number.", "count", '$2=="backup-db" && $4=="FAIL"',
         pred='r["job"]=="backup-db" and r["status"]=="FAIL"', dpred='r["job"].startswith("backup-db") and r["status"].startswith("FAIL")', dnote="prefix match on job and status", unit="backup-db failed {v} times."),
       Q("Now add up the secs of the runs of that job with status OK. Use the file as it is on disk now; reply with the total.", "sum", '$2=="backup-db" && $4=="OK"', f=5, col="secs",
         pred='r["job"]=="backup-db" and r["status"]=="OK"', dpred='r["job"].startswith("backup-db") and r["status"]=="OK"', dnote="job prefix match includes backup-db-weekly", unit="Successful backup-db runs took {v} seconds in total.",
         alts=["Total seconds spent by OK runs of backup-db.", "Sum the secs column for job backup-db where status is OK.", "How many seconds did successful backup-db runs take altogether (weekly job excluded)?", "Per cron/README.md, what is the total secs of backup-db runs with status OK?", "Add up the durations of backup-db's OK runs in runs.txt."]),
   ])

# 9479 forklifts, sum x3
def fork_gen(rng, i, fi, n):
    return [f"1023T{(i * 14) // 3600 % 24:02d}{(i * 14) // 60 % 60:02d}", choice(rng, ["F-03", "F-03", "F-030", "F-05", "F-05", "F-11"]),
            choice(rng, ["入库", "入库", "入库(退回)", "出库", "出库", "盘点"]), str(rng.randint(1, 24)), filler_zh(rng)]


mk("log-9479", sub="M9c", tt="count_events", topic="forkpallets", root="叉车作业", names=["作业.dat"], sep=";",
   cols=["时间", "车号", "动作", "托盘数", "备注"], header=False, rows=(1250, 1350), readme_name="说明.md", min=1, gen=fork_gen,
   readme=["# 叉车作业说明", "", "作业.dat 是一天的叉车作业流水，分号分隔，没有表头：时间;车号;动作;托盘数;备注。", "车号、动作都按完整内容匹配：「F-030」是另一台车，不是「F-03」；「入库(退回)」是退货回库，不算「入库」。"],
   desc="Three turns over one long forklift log: pallets one truck put in, pallets it took out, then the gap to another truck's outbound pallets, with a longer truck id and a return action as look-alikes",
   why="车号 and 动作 are whole-value columns.",
   queries=[
       Q("叉车作业/作业.dat 里，车号「F-03」动作为「入库」的托盘数一共多少？口径见 叉车作业/说明.md，回复数字。", "sum", '$2=="F-03" && $3=="入库"', f=4, col="托盘数",
         pred='r["车号"]=="F-03" and r["动作"]=="入库"', dpred='r["车号"].startswith("F-03") and r["动作"].startswith("入库")', dnote="车号、动作前缀匹配", unit="F-03 入库共 {v} 个托盘。"),
       Q("同一台车，动作为「出库」的托盘数一共多少？以磁盘上现在的文件内容为准。", "sum", '$2=="F-03" && $3=="出库"', f=4, col="托盘数",
         pred='r["车号"]=="F-03" and r["动作"]=="出库"', dpred='r["车号"].startswith("F-03") and r["动作"]=="出库"', dnote="车号前缀匹配，含F-030", unit="F-03 出库共 {v} 个托盘。"),
       Q("再算车号「F-05」出库的托盘数，告诉我它和上一问 F-03 出库托盘数相差多少（绝对值）。以磁盘上现在的文件内容为准。", "sum", '$2=="F-05" && $3=="出库"', f=4, col="托盘数", minus=1,
         pred='r["车号"]=="F-05" and r["动作"]=="出库"', dpred='r["车号"].startswith("F-0") and r["动作"]=="出库"', dnote="车号前缀匹配，含F-03、F-030", unit="F-05 与 F-03 的出库托盘数相差 {v}。",
         alts=["F-05 出库托盘数和 F-03 的差多少？", "算出 F-05 的出库托盘数，再给我它与 F-03 的差值。", "两台车（F-05、F-03）出库托盘数相差几个？", "F-05 比 F-03 多或少出库多少托盘，取绝对值。", "F-05 出库合计减去 F-03 出库合计，绝对值是多少？"]),
   ])

# 9480 auth events, English, distinct x2
def auth_gen(rng, i, fi, n):
    return [f"1024T{(i * 13) // 3600 % 24:02d}{(i * 13) // 60 % 60:02d}", f"user{rng.randint(101, 330)}", choice(rng, ["203.0.113.9", "203.0.113.9", "203.0.113.90", "198.51.100.4", "198.51.100.7", "192.0.2.15"]),
            choice(rng, ["OK", "OK", "FAIL", "FAIL", "FAIL-MFA", "LOCKED"], [30, 30, 10, 10, 8, 5]), filler_en(rng)]


mk("log-9480", sub="M9c", tt="count_events", topic="authfails", root="auth", names=["events.txt"], sep=" ",
   cols=["time", "user", "ip", "result", "note"], header=False, rows=(1250, 1350), readme_name="README.md", min=5, gen=auth_gen,
   readme=["# Auth events", "", "events.txt is one day of sign-in attempts, space separated, no header: time user ip result note.", "IP and result are whole values: `203.0.113.90` is not `203.0.113.9`, and `FAIL-MFA` (second factor missing) is reported separately from a plain `FAIL` (wrong password). Count each user once."],
   desc="Two turns over one long sign-in file: distinct users with wrong-password failures from one IP, then distinct users with missing second factor from it, with a longer IP and a failure subtype as look-alikes",
   why="ip and result are whole-value columns; users are de-duplicated.",
   queries=[
       Q("How many different users had a FAIL from IP 203.0.113.9 in auth/events.txt? auth/README.md defines the terms; reply with the number.", "distinct", '$3=="203.0.113.9" && $4=="FAIL"', f=2, col="user",
         pred='r["ip"]=="203.0.113.9" and r["result"]=="FAIL"', dpred='r["ip"].startswith("203.0.113.9") and r["result"].startswith("FAIL")', dnote="prefix match on ip and result", unit="{v} different users failed from 203.0.113.9."),
       Q("From that same IP, how many different users had FAIL-MFA? Count from the file as it is on disk now.", "distinct", '$3=="203.0.113.9" && $4=="FAIL-MFA"', f=2, col="user",
         pred='r["ip"]=="203.0.113.9" and r["result"]=="FAIL-MFA"', dpred='r["ip"].startswith("203.0.113.9") and r["result"].startswith("FAIL")', dnote="prefix match on ip and result, merging both failure kinds", unit="{v} different users had FAIL-MFA from 203.0.113.9.",
         alts=["Number of distinct users with result FAIL-MFA from 203.0.113.9.", "How many unique users hit FAIL-MFA on that address?", "Count each user once: FAIL-MFA events from IP 203.0.113.9 (not .90).", "Per auth/README.md, how many different users show FAIL-MFA for 203.0.113.9?", "De-duplicated user count for ip 203.0.113.9 and result FAIL-MFA."]),
   ])


def _mk(cid):
    return lambda: build(cid)


BUILDERS = []
for _cid in sorted(CASES):
    BUILDERS.append(_mk(_cid))
    BUILDERS[-1].__name__ = _cid.replace("-", "_")

# static SPEC (specs.py loads this file by path and needs it at import time)
for _cid, _c in CASES.items():
    SPEC[_cid] = dict(kind="bash_aggregate", sub=_c["sub"], needs=[f"{_c['root']}/{_c['readme_name']}"])
