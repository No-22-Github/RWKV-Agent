"""M9 (bash) batch b12q of v1.41: ids 9321-9340, fresh data shapes over .txt/.dat tables.

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
    if kind == "between_sum":
        k, state, tot, cnt = 0, 0, 0, 0
        for n, r in rows:
            if state == 0:
                if ev(q["start"], r):
                    k += 1
                    state = 1 if k == q.get("nth", 1) else 0
            elif ev(q["end"], r):
                state = 2
                break
            elif ev(q["pred"], r):
                tot += int(r[q["col"]])
                cnt += 1
        if state != 2 or cnt == 0:
            raise ValueError("no window")
        return tot
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
    if kind == "nth_line":
        if len(sel) < q["nth"] + 2:
            raise ValueError("too few")
        return sel[q["nth"] - 1][0]
    if kind == "longest_line":
        ranked = sorted(((len(q["sep"].join(r.values())), n) for n, r in sel), reverse=True)
        if len(ranked) < 2 or ranked[0][0] == ranked[1][0]:
            raise ValueError("tie")
        return ranked[0][1]
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
    for q in qs:
        q["sep"] = c["sep"]
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
                if q["agg"] in ("count", "distinct", "between", "first_line", "last_line", "nth_line", "longest_line", "top_n", "max", "min"):
                    ok = ok and near_tokens(files, float(v)) == (1 if q["agg"] in ("max", "min") else 0)
        if ok:
            break
    else:
        raise SystemExit("%s: no seed found" % cid)
    readme_path = f"{c['root']}/{c['readme_name']}"
    data_paths = [f"{c['root']}/{n}" for n in c["names"]]
    qlist = [{k: v for k, v in q.items() if k in ("agg", "col", "pred", "group", "ret", "tie_col", "tie_pick", "extreme", "margin", "start", "end", "nth", "sep")} for q in qs]
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
    if q["agg"] in ("sum", "between_sum"):
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
elif QS[-1]["agg"] not in ("sum", "between_sum"):
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
            want = thousands(fmt(v)) if q["agg"] in ("sum", "between_sum") else [fmt(v)]
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
        cid, desc=c["desc"], task_type=c["tt"], family="fam-%s-b12q-%s-01" % (cid.split("-")[0], c["topic"]), level=c.get("level", "L2"),
        ref_calls=len(commands), traps=traps, decoys=decoys, axes=["LNG", "OBS"] if long_file else ["CHN", "OBS"],
        files=files, verify=verify_src(files, body), notes=notes, turns=turns)


def case(cid, **kw):
    CASES[cid] = kw


T = "\t"


def rint(rng, lo, hi, step=1):
    return rng.randrange(lo, hi + 1, step)


def stamp(i, step=23, day="1013"):
    s = i * step
    return f"{day}T{s // 3600 % 24:02d}{s // 60 % 60:02d}"


def marks_at(n, spec):
    return {int(n * f): t for f, t in spec.items()}


ZH_FILL = ["货架编号待复核", "扫码枪读取正常", "叉车通道临时占用", "托盘已转运至缓冲区", "批次标签补打过一次", "夜班交接已登记", "冷链温度在范围内", "库位调整已同步系统"]
EN_FILL = ["scanner-read-ok", "carrier-ack-received", "retry-budget-unchanged", "payload-checksum-matched", "node-heartbeat-seen", "queue-depth-below-limit", "cache-warm-complete", "audit-trail-appended"]
WORDS = ["alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel", "india", "juliet", "kilo", "lima", "mike", "nova", "oscar", "papa", "quebec", "romeo"]


def text_of(rng, lo, hi):
    out = []
    while sum(len(w) + 1 for w in out) < rng.randint(lo, hi):
        out.append(rng.choice(WORDS))
    return "-".join(out)


# ============================================================ M9c: one long file each

# 9421 stocktake, sum inside a section, trial section as decoy
def stock_gen(rng, i, fi, n):
    m = marks_at(n, {0.10: "B区开始(试盘)", 0.19: "B区结束(试盘)", 0.40: "B区开始", 0.70: "B区结束"})
    if i in m:
        return [f"L{i + 1:05d}", "段", m[i], "0", "-"]
    return [f"L{i + 1:05d}", choice(rng, ["入库", "入库", "入库(退回)", "出库", "调拨"]), f"SKU-{rng.choice('ABCDEFGH')}{rng.randint(100, 999)}", str(rng.randint(1, 90)), choice(rng, ZH_FILL)]


case("tab-9421", sub="M9c", tt="aggregate", topic="stockwindowsum", root="盘点", names=["盘点单.dat"], sep=T,
     cols=["序号", "类型", "货号", "数量", "备注"], header=False, rows=(1150, 1250), readme_name="说明.md", min=20, gen=stock_gen,
     readme=["# 盘点单说明", "", "盘点单.dat 是整次盘点的流水，制表符分隔，没有表头：序号、类型、货号、数量、备注。", "类型为「段」的行是区段标记（货号列写标记名），不是货物。真正的 B 区盘点从「B区开始」到「B区结束」；带「(试盘)」的是试盘标记，不算。", "类型按完整内容匹配：「入库(退回)」不是「入库」。"],
     desc="Sums the quantity of inbound rows inside the real B-zone section of one long stocktake file where a trial section and a returned-goods type are look-alikes",
     why="The section is delimited by two exact marker rows and the type is a whole-value column.",
     queries=[dict(prompt="盘点/盘点单.dat 里，「B区开始」和「B区结束」之间类型为「入库」的数量合计是多少？标记和类型的口径见 盘点/说明.md，回复数字。", agg="between_sum", nth=1, col="数量",
                   start='r["类型"]=="段" and r["货号"]=="B区开始"', end='r["类型"]=="段" and r["货号"]=="B区结束"', pred='r["类型"]=="入库"',
                   decoy=dict(start='r["货号"].startswith("B区开始")', end='r["货号"].startswith("B区结束")', pred='r["类型"].startswith("入库")'), decoy_note="第一个开始标记是试盘、类型前缀匹配含入库(退回)",
                   cmd="""awk -F'\\t' '$2=="段" && $3=="B区开始" {on=1; next} $2=="段" && $3=="B区结束" {on=0} on && $2=="入库" {s+=$4} END{print s+0}' 盘点/盘点单.dat""", unit="B 区盘点期间入库数量合计 {v}。",
                   alts=["盘点单里 B 区正式盘点期间，入库的数量加起来是多少？", "从「B区开始」到「B区结束」，类型恰好是入库的行，数量列求和。", "按说明.md，B 区盘点窗口内入库数量总和。", "试盘不算，B 区真正盘点那一段里入库了多少件？", "统计 B 区盘点区段内类型为入库的数量合计。"])])


# 9422 alarms, 3rd record of a level
def alarm_gen(rng, i, fi, n):
    return [f"1013T{(i * 31) // 3600 % 24:02d}{(i * 31) // 60 % 60:02d}", f"DEV{rng.randint(10, 99)}", choice(rng, ["提示", "提示", "警告", "严重", "严重(已恢复)", "警告"], [3, 3, 3, 1, 2, 3]),
            choice(rng, ["风扇转速偏低", "电源模块切换", "链路抖动", "磁盘预警", "温度偏高", "时钟漂移"]), "trace-" + "".join(rng.choice("0123456789abcdef") for _ in range(24))]


case("log-9422", sub="M9c", tt="locate_error", topic="thirdcritical", root="告警", names=["设备告警.txt"], sep=";",
     cols=["时间", "设备", "级别", "内容", "追踪"], header=False, rows=(1100, 1200), readme_name="说明.md", min=20, gen=alarm_gen,
     readme=["# 设备告警说明", "", "设备告警.txt 是一天的告警流水，分号分隔，没有表头：时间;设备;级别;内容;追踪，每行一条。", "级别按完整内容匹配：「严重(已恢复)」是已经恢复的旧告警，不是「严重」。"],
     desc="Finds the line number of the third critical alarm in one long alarm file where a recovered-critical level is a look-alike",
     why="级别 is a whole-value column and the line number counts from the first line of the file.",
     queries=[dict(prompt="告警/设备告警.txt 里，第 3 条级别为「严重」的告警在文件的第几行？级别写法见 告警/说明.md，回复行号。", agg="nth_line", nth=3,
                   pred='r["级别"]=="严重"', decoy=dict(pred='r["级别"].startswith("严重")'), decoy_note="级别前缀匹配，含严重(已恢复)",
                   cmd="""awk -F';' '$3=="严重" {c++; if (c==3) {print NR; exit}}' 告警/设备告警.txt""", unit="第 3 条严重告警在第 {v} 行。",
                   alts=["设备告警.txt 中第三个「严重」级别的记录是第几行？", "把级别恰好是严重的告警按出现顺序数，第 3 条位于哪一行？", "按说明.md，第三条严重告警的行号。", "严重(已恢复)不算，第 3 条严重告警在文件第几行？", "找出级别为严重的第三条记录，告诉我它的行号。"])])


# 9423 payments, first failed wechat payment
def pay_gen(rng, i, fi, n):
    return [f"P{i + 1:06d}", choice(rng, ["微信", "微信小程序", "支付宝", "银联", "微信小程序"], [4, 3, 4, 3, 1]), choice(rng, ["成功", "成功", "成功", "失败", "失败(已重试)", "处理中"], [6, 6, 6, 1, 3, 2]),
            str(rng.randint(10, 3000)), "终端=" + choice(rng, ["门店一号机", "门店二号机", "自助机三楼", "线上网关"]) + "|批次" + "".join(rng.choice("ABCDEFGH") for _ in range(8))]


case("tab-9423", sub="M9c", tt="filter_count", topic="firstfailpay", root="交易", names=["交易.tsv"], sep=T,
     cols=["订单", "渠道", "状态", "金额", "备注"], header=True, rows=(1100, 1200), readme_name="说明.md", min=20, gen=pay_gen,
     readme=["# 交易流水说明", "", "交易.tsv 是一天的交易流水，制表符分隔，第一行是表头：订单、渠道、状态、金额、备注。", "渠道、状态都按完整内容匹配：「微信小程序」是另一个渠道，「失败(已重试)」是重试后已成功的，不算「失败」。", "行号从文件第一行（表头）算起为第 1 行。"],
     desc="Finds the line number of the first failed payment on the WeChat channel in one long transaction file where a mini-program channel and a retried-failure status are look-alikes",
     why="渠道 and 状态 are whole-value columns; the header counts as line 1.",
     queries=[dict(prompt="交易/交易.tsv 里，渠道为「微信」且状态为「失败」的第一条记录在文件第几行？行号的算法见 交易/说明.md，回复行号。", agg="first_line",
                   pred='r["渠道"]=="微信" and r["状态"]=="失败"', decoy=dict(pred='r["渠道"].startswith("微信") and r["状态"].startswith("失败")'), decoy_note="渠道和状态都前缀匹配",
                   cmd="""awk -F'\\t' '$2=="微信" && $3=="失败" {print NR; exit}' 交易/交易.tsv""", unit="第一条微信失败记录在第 {v} 行。",
                   alts=["交易流水里微信渠道第一次失败发生在第几行？", "渠道是微信、状态是失败的记录，最靠前的一条行号是多少？", "按说明.md，微信失败的首条记录位于哪一行（表头算第 1 行）？", "微信小程序不算，微信渠道第一笔失败的行号。", "找到第一条微信失败的交易，告诉我它在文件的第几行。"])])


# 9424 host events, last restart of one host
def run_gen(rng, i, fi, n):
    return [f"1013T{(i * 29) // 3600 % 24:02d}{(i * 29) // 60 % 60:02d}", choice(rng, ["web-01", "web-01", "web-010", "web-02", "db-01"]),
            choice(rng, ["心跳", "心跳", "巡检", "启动", "停止", "重启", "重启中", "重启中"], [8, 8, 4, 1, 1, 1, 2, 3]), "pid" + str(rng.randint(100000, 999999)) + "-" + choice(rng, EN_FILL)]


case("log-9424", sub="M9c", tt="locate_error", topic="lastrestart", root="运行", names=["事件.txt"], sep=" ",
     cols=["时间", "主机", "事件", "备注"], header=False, rows=(1200, 1300), readme_name="说明.md", min=20, gen=run_gen,
     readme=["# 运行事件说明", "", "事件.txt 是机房一天的运行事件，空格分隔，没有表头：时间 主机 事件 备注，按时间顺序追加。", "主机、事件都按完整内容匹配：「web-010」是另一台主机，「重启中」只是过程提示，不是一次「重启」。"],
     desc="Finds the line number of the last restart event of one host in one long event file where a longer host id and an in-progress status are look-alikes",
     why="主机 and 事件 are whole-value columns; the last matching line is unique.",
     queries=[dict(prompt="运行/事件.txt 里，主机 web-01 最后一次「重启」事件在文件第几行？口径见 运行/说明.md，回复行号。", agg="last_line",
                   pred='r["主机"]=="web-01" and r["事件"]=="重启"', decoy=dict(pred='r["主机"].startswith("web-01") and r["事件"].startswith("重启")'), decoy_note="主机和事件都前缀匹配，含web-010和重启中",
                   cmd="""awk '$2=="web-01" && $3=="重启" {n=NR} END{print n}' 运行/事件.txt""", unit="web-01 最后一次重启在第 {v} 行。",
                   alts=["web-01 最近一次重启记录的行号是多少？", "事件列等于重启、主机列等于 web-01 的最后一行是第几行？", "按说明.md，web-01 的最后一次重启出现在第几行？", "web-010 和重启中都不算，web-01 末次重启的行号。", "事件.txt 里 web-01 最晚的一条重启事件位于哪一行？"])])


# 9425 longest reply line (ASCII so character counts are unambiguous)
def post_gen(rng, i, fi, n):
    kind = choice(rng, ["post", "reply", "reply", "reply"])
    return [f"C{i + 1:05d}", kind, "u_" + "".join(rng.choice("abcdefghijklmnop") for _ in range(6)), text_of(rng, 30, 420 if kind == "reply" else 600)]


case("tab-9425", sub="M9c", tt="rank", topic="longestreply", root="评论", names=["评论.dat"], sep=T,
     cols=["编号", "类型", "用户", "内容"], header=False, rows=(1100, 1200), readme_name="说明.md", min=20, gen=post_gen,
     readme=["# 评论数据说明", "", "评论.dat 是一个话题下的全部评论，制表符分隔，没有表头：编号、类型、用户、内容，每条一行，内容全是小写字母和短横线。", "类型 post 是主贴，reply 是回复。比较长短时看整行的字符数（含制表符），行号从文件第一行算起。"],
     desc="Finds the line number of the longest reply line in one long comment file where original posts are even longer",
     why="类型 is a whole-value column; the longest reply line has a strictly greater length than every other reply.",
     queries=[dict(prompt="评论/评论.dat 里，类型为 reply 的行中，整行最长的是文件的第几行？长度怎么比见 评论/说明.md，回复行号。", agg="longest_line",
                   pred='r["类型"]=="reply"', decoy=dict(pred="True"), decoy_note="不限类型，最长的是主贴",
                   cmd="""awk -F'\\t' '$2=="reply" {print length($0), NR}' 评论/评论.dat | sort -rn | head -1""", unit="最长的回复在第 {v} 行。",
                   alts=["评论.dat 里回复（reply）最长的那一行是第几行？", "只看类型为 reply 的行，整行字符数最大的行号是多少？", "按说明.md 的口径，最长回复所在的行号。", "主贴不算，哪一行的回复最长？回复它的行号。", "找出整行最长的 reply 记录，告诉我它位于文件第几行。"])])


# 9426 reconciliation batches, count lines inside the 3rd real window
def recon_gen(rng, i, fi, n):
    m = marks_at(n, {0.08: "对账开始", 0.16: "对账结束", 0.30: "对账开始", 0.38: "对账结束", 0.45: "对账开始(补跑)", 0.50: "对账结束(补跑)", 0.62: "对账开始", 0.85: "对账结束"})
    s = f"1013T{(i * 21) // 3600 % 24:02d}{(i * 21) // 60 % 60:02d}"
    if i in m:
        return [s, "MARK", m[i], "-", "-"]
    return [s, choice(rng, ["acct", "ledger", "fx", "tax"]), choice(rng, ["成功", "成功", "成功", "失败", "跳过"]), str(rint(rng, 5, 900)), choice(rng, ZH_FILL)]


case("log-9426", sub="M9c", tt="time_window", topic="reconrun", root="对账", names=["作业.txt"], sep=T,
     cols=["时间", "作业", "状态", "耗时毫秒", "备注"], header=False, rows=(1150, 1250), readme_name="说明.md", min=20, gen=recon_gen,
     readme=["# 对账作业说明", "", "作业.txt 是一天的对账作业日志，制表符分隔，没有表头：时间、作业、状态、耗时毫秒、备注。", "作业列为 MARK 的行是窗口标记，状态列写标记名。正式的对账窗口从「对账开始」到其后的「对账结束」，当天共有三个；「(补跑)」是补跑的标记，不算正式窗口。数窗口内的行数时，开始、结束这两个标记行本身不算。"],
     desc="Counts the lines inside the third official reconciliation window of one long job log where a re-run window sits before it",
     why="Windows are delimited by exact MARK rows; the re-run markers are excluded, so the third official window is unambiguous.",
     queries=[dict(prompt="对账/作业.txt 里，第三个正式对账窗口（「对账开始」到「对账结束」）之间一共有多少行？窗口怎么认见 对账/说明.md，回复行数。", agg="between", nth=3,
                   start='r["作业"]=="MARK" and r["状态"]=="对账开始"', end='r["作业"]=="MARK" and r["状态"]=="对账结束"', pred="True",
                   decoy=dict(start='r["状态"].startswith("对账开始")', end='r["状态"].startswith("对账结束")'), decoy_note="补跑标记被当作正式窗口",
                   cmd="""awk -F'\\t' '$2=="MARK" && $3=="对账开始" {k++; if (k==3) on=1; next} $2=="MARK" && $3=="对账结束" {on=0} on {c++} END{print c+0}' 对账/作业.txt""", unit="第三个正式窗口内有 {v} 行。",
                   alts=["作业.txt 第 3 个对账窗口里有多少行日志？", "不算补跑，第三次对账开始到对账结束之间的行数。", "按说明.md，当天第三个正式窗口包含几行？", "统计第三个「对账开始」与其后「对账结束」之间的行数（补跑标记除外）。", "第三个对账窗口里一共记录了多少行？"])])


# 9427 lab samples, distinct samples over limit for one item
def lab_gen(rng, i, fi, n):
    return [f"YP{rng.randint(1000, 1700)}", f"B{rng.randint(1, 40):02d}", choice(rng, ["铅", "铅", "铅(溶出)", "镉", "砷"]), choice(rng, ["合格", "合格", "超标", "超标", "超标(复测合格)"], [8, 8, 2, 2, 3]),
            "仪器=" + choice(rng, ["ICP-A", "ICP-B", "AAS-1"]) + "/操作员=" + choice(rng, ["组一", "组二", "组三"])]


case("tab-9427", sub="M9c", tt="filter_count", topic="leadsamples", root="检测", names=["样品检测.txt"], sep=";",
     cols=["样品", "批次", "项目", "结果", "备注"], header=True, rows=(1200, 1300), readme_name="说明.md", min=20, gen=lab_gen,
     readme=["# 样品检测说明", "", "样品检测.txt 是本月全部检测记录，分号分隔，第一行是表头：样品;批次;项目;结果;备注。同一个样品可能被检测多次，有多行。", "项目、结果都按完整内容匹配：「铅(溶出)」是另一个检测项目，「超标(复测合格)」复测后已合格，不算「超标」。"],
     desc="Counts distinct samples that exceeded the lead limit in one long lab file where a leach-test item and a re-test-passed result are look-alikes",
     why="项目 and 结果 are whole-value columns; samples repeat across rows and are de-duplicated.",
     queries=[dict(prompt="检测/样品检测.txt 里，项目为「铅」且结果为「超标」的样品有多少个（同一个样品只算一次）？口径见 检测/说明.md，回复个数。", agg="distinct", col="样品",
                   pred='r["项目"]=="铅" and r["结果"]=="超标"', decoy=dict(pred='r["项目"].startswith("铅") and r["结果"].startswith("超标")'), decoy_note="项目和结果都前缀匹配",
                   cmd="""awk -F';' '$3=="铅" && $4=="超标" {print $1}' 检测/样品检测.txt | sort -u | wc -l""", unit="铅超标的样品共 {v} 个。",
                   alts=["本月铅检测超标的不同样品有多少个？", "项目是铅、结果是超标的记录，样品去重后有几个？", "按说明.md，铅超标涉及多少个样品？", "铅(溶出)和复测合格的不算，超标的铅样品数量。", "统计铅项目超标记录里不同样品的个数。"])])


# 9428 probe max temperature, status filter
def probe_gen(rng, i, fi, n):
    probe = choice(rng, ["S-07", "S-07", "S-070", "S-7", "S-12"])
    status = choice(rng, ["正常", "正常", "正常", "校准中"], [8, 8, 8, 1])
    t = round(rng.uniform(20, 60), 1) if status == "正常" else round(rng.uniform(70, 99), 1)
    return [f"1013T{(i * 19) // 3600 % 24:02d}{(i * 19) // 60 % 60:02d}", probe, "%.1f" % t, status, rng.choice(ZH_FILL)]


case("tab-9428", sub="M9c", tt="rank", topic="probemax", root="温控", names=["探头.txt"], sep=",",
     cols=["时间", "探头", "温度", "状态", "备注"], header=False, rows=(1250, 1350), readme_name="说明.md", min=1, gen=probe_gen,
     readme=["# 温控探头说明", "", "探头.txt 是一天的探头读数，逗号分隔，没有表头：时间,探头,温度,状态,备注。温度单位摄氏度，保留一位小数。", "探头号按完整内容匹配：「S-070」「S-7」是别的探头。状态为「校准中」的读数无效，统计时不算。"],
     desc="Finds the highest valid temperature of probe S-07 in one long reading file where invalid calibration readings and look-alike probe ids run higher",
     why="探头 and 状态 are whole-value columns; the maximum valid reading is unique.",
     queries=[dict(prompt="温控/探头.txt 里，探头 S-07 的有效读数中最高温度是多少？什么算有效见 温控/说明.md，回复温度数值。", agg="max", col="温度",
                   pred='r["探头"]=="S-07" and r["状态"]=="正常"', decoy=dict(pred='r["探头"]=="S-07"'), decoy_note="含校准中的无效读数",
                   cmd="""awk -F, '$2=="S-07" && $4=="正常" && ($3+0>m || m=="") {m=$3+0} END{print m}' 温控/探头.txt""", unit="S-07 的最高有效温度是 {v} 度。",
                   alts=["S-07 探头最高的有效温度读数是多少？", "状态正常的 S-07 读数里，温度的最大值。", "按说明.md，探头 S-07 的最高温度（校准中的不算）。", "探头.txt 中 S-07 最热的有效一次是多少度？", "统计 S-07 在状态为正常时的温度最大值。"])])


# 9429 production, largest station total on morning shift
def prod_gen(rng, i, fi, n):
    return [f"1013", f"G{rng.randint(1, 14):02d}", str(rng.randint(5, 120)), choice(rng, ["早班", "早班", "早班(加班)", "晚班", "夜班"]), rng.choice(ZH_FILL) + "/" + rng.choice(ZH_FILL)]


case("tab-9429", sub="M9c", tt="aggregate", topic="stationtotal", root="产量", names=["日报.dat"], sep=T,
     cols=["日期", "工位", "产量", "班次", "备注"], header=True, rows=(1150, 1250), readme_name="说明.md", min=20, gen=prod_gen,
     readme=["# 产量日报说明", "", "日报.dat 是车间一周的产量明细，制表符分隔，第一行是表头：日期、工位、产量、班次、备注。", "班次按完整内容匹配：「早班(加班)」是加班时段，不算「早班」。汇总按工位分组。"],
     desc="Finds the largest per-station morning-shift production total in one long output file where an overtime shift label is a look-alike",
     why="班次 is a whole-value column; the answer is the maximum of the per-station sums.",
     queries=[dict(prompt="产量/日报.dat 里，只看班次为「早班」的记录，按工位汇总产量，最大的那个工位合计是多少？口径见 产量/说明.md，回复数字。", agg="top_n", group="工位", col="产量", extreme="max",
                   pred='r["班次"]=="早班"', decoy=dict(pred='r["班次"].startswith("早班")'), decoy_note="班次前缀匹配，含早班(加班)",
                   cmd="""awk -F'\\t' '$4=="早班" {s[$2]+=$3} END{m=0; for (k in s) if (s[k]>m) m=s[k]; print m}' 产量/日报.dat""", unit="早班产量最高的工位合计 {v}。",
                   alts=["各工位早班产量加起来，最大的合计数是多少？", "班次恰好是早班的产量按工位求和，取最大值。", "按说明.md，早班里产量最高工位的合计。", "早班(加班)不算，各工位合计的最大值是多少？", "汇总早班产量，哪个工位最多？告诉我那个合计数。"])])


# 9430 ledger, sum inside the second occurrence of a section
def ledger_gen(rng, i, fi, n):
    m = marks_at(n, {0.08: "第二季度开始", 0.30: "第二季度结束", 0.50: "第二季度开始", 0.80: "第二季度结束"})
    if i in m:
        return [f"E{i + 1:05d}", "段", m[i], "0", "-"]
    return [f"E{i + 1:05d}", choice(rng, ["财务部", "财务部", "市场部", "研发部", "财务部(外包)"]), choice(rng, ["差旅", "办公", "培训", "招待", "软件"]), str(rint(rng, 20, 4000, 10)), rng.choice(ZH_FILL)]


case("tab-9430", sub="M9c", tt="aggregate", topic="ledgerq2", root="账本", names=["流水.txt"], sep=" ",
     cols=["序号", "部门", "科目", "金额", "摘要"], header=False, rows=(1150, 1250), readme_name="说明.md", min=20, gen=ledger_gen,
     readme=["# 费用流水说明", "", "流水.txt 是全年费用流水，空格分隔，没有表头：序号 部门 科目 金额 摘要。", "部门列为「段」的行是区段标记，科目列写标记名。文件里「第二季度开始」出现了两次：第一次是草稿期，第二次才是正式记账，正式区段到其后的「第二季度结束」为止。", "部门按完整内容匹配：「财务部(外包)」不是「财务部」。"],
     desc="Sums the finance-department amounts inside the second occurrence of a quarter section in one long ledger file where a draft section precedes it",
     why="The section name occurs twice and the README names the second one as official; 部门 is a whole-value column.",
     queries=[dict(prompt="账本/流水.txt 里，正式记账的第二季度区段（第二个「第二季度开始」到其后的「第二季度结束」）中，部门为「财务部」的金额合计是多少？区段怎么认见 账本/说明.md，回复数字。", agg="between_sum", nth=2, col="金额",
                   start='r["部门"]=="段" and r["科目"]=="第二季度开始"', end='r["部门"]=="段" and r["科目"]=="第二季度结束"', pred='r["部门"]=="财务部"',
                   decoy=dict(nth=1), decoy_note="用了第一个（草稿）区段",
                   cmd="""awk '$2=="段" && $3=="第二季度开始" {k++; if (k==2) on=1; next} $2=="段" && $3=="第二季度结束" {on=0} on && $2=="财务部" {s+=$4} END{print s+0}' 账本/流水.txt""", unit="正式第二季度区段里财务部金额合计 {v}。",
                   alts=["流水.txt 第二个二季度区段里，财务部花了多少钱？", "草稿期不算，正式第二季度区段内部门是财务部的金额求和。", "按说明.md，正式记账区段里财务部的金额总和。", "第二次出现的「第二季度开始」到「第二季度结束」之间，财务部的金额加起来是多少？", "统计正式二季度区段内财务部（不含外包）的金额合计。"])])


# 9431 access log, count by three conditions
def acc_gen(rng, i, fi, n):
    return [f"1013T{(i * 17) // 3600 % 24:02d}{(i * 17) // 60 % 60:02d}", f"10.2.{rng.randint(0, 9)}.{rng.randint(1, 250)}", choice(rng, ["GET", "GET", "POST", "POST", "PUT"]),
            choice(rng, ["/api/order", "/api/order", "/api/order/list", "/api/user", "/api/cart"]), choice(rng, ["200", "200", "200", "502", "500", "504", "502"]),
            "ua-" + rng.choice(["chrome", "safari", "okhttp", "curl"]) + "-" + rng.choice(["win", "mac", "linux", "android"])]


case("log-9431", sub="M9c", tt="count_events", topic="postbadgateway", root="访问", names=["网关.txt"], sep=" ",
     cols=["时间", "地址", "方法", "路径", "状态", "客户端"], header=False, rows=(1250, 1350), readme_name="说明.md", min=5, gen=acc_gen,
     readme=["# 网关访问说明", "", "网关.txt 是一天的网关访问记录，空格分隔，没有表头：时间 地址 方法 路径 状态 客户端。", "路径按完整内容匹配：「/api/order/list」是另一个接口，不属于「/api/order」。状态按完整数字匹配，「502」就是 502，不含 500、504。"],
     desc="Counts POST requests to one API path answered with status 502 in one long gateway log where a sub-path and neighbouring 5xx codes are look-alikes",
     why="方法, 路径 and 状态 are whole-value columns, all three must match.",
     queries=[dict(prompt="访问/网关.txt 里，方法为 POST、路径为 /api/order、状态为 502 的请求一共有多少条？口径见 访问/说明.md，回复条数。", agg="count",
                   pred='r["方法"]=="POST" and r["路径"]=="/api/order" and r["状态"]=="502"', decoy=dict(pred='r["方法"]=="POST" and r["路径"].startswith("/api/order") and r["状态"].startswith("50")'), decoy_note="路径前缀匹配、任意 50x 状态",
                   cmd="""awk '$3=="POST" && $4=="/api/order" && $5==502' 访问/网关.txt | wc -l""", unit="符合条件的请求共 {v} 条。",
                   alts=["网关里 POST /api/order 返回 502 的有多少次？", "方法 POST、路径 /api/order、状态 502 的记录条数。", "按说明.md，订单接口 POST 请求 502 的次数。", "/api/order/list 不算，POST 订单接口 502 一共多少条？", "统计同时满足 POST、/api/order、502 三个条件的行数。"])])


# 9432 switchovers, 4th real one
def sw_gen(rng, i, fi, n):
    return [f"1013T{(i * 27) // 3600 % 24:02d}{(i * 27) // 60 % 60:02d}", choice(rng, ["pay-db", "user-db", "log-db"]),
            choice(rng, ["心跳", "心跳", "心跳", "主备切换", "主备切换(演练)", "手工切换", "同步延迟"], [10, 10, 10, 1, 2, 2, 4]), "op" + str(rng.randint(10, 99)), "node=" + "".join(rng.choice("abcdefgh") for _ in range(10)) + "/zone=" + rng.choice(["华东", "华北", "华南"])]


case("log-9432", sub="M9c", tt="locate_error", topic="fourthfailover", root="切换", names=["记录.dat"], sep=",",
     cols=["时间", "系统", "事件", "操作员", "备注"], header=False, rows=(1250, 1350), readme_name="说明.md", min=20, gen=sw_gen,
     readme=["# 切换记录说明", "", "记录.dat 是一周的数据库事件，逗号分隔，没有表头：时间,系统,事件,操作员,备注，每行一个事件。", "事件按完整内容匹配：「主备切换(演练)」是演练，不是真实的「主备切换」；「手工切换」是另一类事件。"],
     desc="Finds the line number of the fourth real primary-standby switchover in one long event file where drill and manual switchover events are look-alikes",
     why="事件 is a whole-value column and the line number counts from the first line.",
     queries=[dict(prompt="切换/记录.dat 里，第 4 次真实的「主备切换」事件在文件第几行？事件写法见 切换/说明.md，回复行号。", agg="nth_line", nth=4,
                   pred='r["事件"]=="主备切换"', decoy=dict(pred='r["事件"].startswith("主备切换")'), decoy_note="事件前缀匹配，含演练",
                   cmd="""awk -F, '$3=="主备切换" {c++; if (c==4) {print NR; exit}}' 切换/记录.dat""", unit="第 4 次主备切换在第 {v} 行。",
                   alts=["记录.dat 里第四次主备切换的行号是多少？", "演练不算，按出现顺序第 4 条「主备切换」位于哪一行？", "按说明.md，第 4 个真实主备切换事件所在行。", "事件恰好是主备切换的第四条记录在文件第几行？", "找到第四次真正的主备切换，回复它的行号。"])])


# 9433 reconciliation, last long-cash diff for one account
def diff_gen(rng, i, fi, n):
    return [f"2026-10-{rng.randint(1, 28):02d}", choice(rng, ["A-100", "A-100", "A-1001", "A-200", "B-300"]), choice(rng, ["长款", "长款", "短款", "长款(已调平)", "无差异"], [4, 4, 5, 3, 8]),
            str(rint(rng, 1, 800)), rng.choice(ZH_FILL)]


case("tab-9433", sub="M9c", tt="filter_count", topic="lastlongcash", root="对账单", names=["差异.txt"], sep=";",
     cols=["日期", "账户", "差异类型", "差额", "说明"], header=True, rows=(1100, 1200), readme_name="说明.md", min=20, gen=diff_gen,
     readme=["# 对账差异说明", "", "差异.txt 是本月全部对账差异，分号分隔，第一行是表头：日期;账户;差异类型;差额;说明，文件按处理顺序追加，日期不一定递增。", "账户、差异类型都按完整内容匹配：「A-1001」是另一个账户，「长款(已调平)」已经处理完，不算「长款」。", "行号从文件第一行（表头）算起为第 1 行。"],
     desc="Finds the line number of the last over-cash difference of one account in one long reconciliation file where a longer account id and a settled variant are look-alikes",
     why="账户 and 差异类型 are whole-value columns; the file is in append order so the last matching line is unique.",
     queries=[dict(prompt="对账单/差异.txt 里，账户 A-100 最后一条差异类型为「长款」的记录在文件第几行？口径见 对账单/说明.md，回复行号。", agg="last_line",
                   pred='r["账户"]=="A-100" and r["差异类型"]=="长款"', decoy=dict(pred='r["账户"].startswith("A-100") and r["差异类型"].startswith("长款")'), decoy_note="账户和差异类型都前缀匹配",
                   cmd="""awk -F';' '$2=="A-100" && $3=="长款" {n=NR} END{print n}' 对账单/差异.txt""", unit="A-100 最后一条长款在第 {v} 行。",
                   alts=["A-100 账户最后一次长款出现在文件第几行？", "账户是 A-100、差异类型是长款的最后一条记录的行号。", "按说明.md，A-100 最末一条长款记录位于哪一行？", "A-1001 和已调平的不算，A-100 的最后一条长款在第几行？", "差异.txt 里 A-100 最近追加的长款记录行号。"])])


# 9434 overtime hours of one employee
def ot_gen(rng, i, fi, n):
    name = choice(rng, ["李明", "李明", "李明辉", "王芳", "张伟", "李明"], [3, 3, 3, 3, 3, 0])
    note = choice(rng, ["-", "-", "替李明代班", "替王芳代班"]) if name != "李明" else "-"
    return [f"1013-{i + 1:04d}", name, choice(rng, ["加班", "加班", "加班(调休)", "值班"]), str(rint(rng, 1, 9)), note + "/" + rng.choice(ZH_FILL)]


case("tab-9434", sub="M9c", tt="aggregate", topic="overtimehours", root="考勤", names=["工时.txt"], sep=T,
     cols=["编号", "员工", "类型", "工时", "备注"], header=False, rows=(1200, 1300), readme_name="说明.md", min=20, gen=ot_gen,
     readme=["# 考勤工时说明", "", "工时.txt 是整月的工时记录，制表符分隔，没有表头：编号、员工、类型、工时（整数小时）、备注。", "员工、类型都按完整内容匹配：「李明辉」是另一位员工；备注里写「替李明代班」的行，工时记在代班人名下，不算李明。「加班(调休)」已经调休抵扣，不算「加班」。"],
     desc="Sums the overtime hours of one employee in one long attendance file where a similar name, cover-shift remarks and a compensated overtime type are look-alikes",
     why="员工 and 类型 are whole-value columns; remarks mentioning the name do not count.",
     queries=[dict(prompt="考勤/工时.txt 里，员工「李明」类型为「加班」的工时合计是多少？口径见 考勤/说明.md，回复小时数。", agg="sum", col="工时",
                   pred='r["员工"]=="李明" and r["类型"]=="加班"', decoy=dict(pred='"李明" in r["员工"] + r["备注"] and r["类型"].startswith("加班")'), decoy_note="员工或备注包含李明、类型前缀匹配",
                   cmd="""awk -F'\\t' '$2=="李明" && $3=="加班" {s+=$4} END{print s+0}' 考勤/工时.txt""", unit="李明加班工时合计 {v} 小时。",
                   alts=["李明这个月加班一共多少小时？", "员工是李明、类型是加班的行，工时列求和。", "按说明.md，李明（不含李明辉）的加班工时总数。", "调休的加班不算，李明的加班小时合计。", "工时.txt 里李明的加班工时加起来是多少？"])])


# ---------------------------------------------------------------- English prompts
def xfer_gen(rng, i, fi, n):
    m = marks_at(n, {0.08: "SYNC-BEGIN-TEST", 0.17: "SYNC-END-TEST", 0.35: "SYNC-BEGIN", 0.72: "SYNC-END"})
    s = f"1013T{(i * 21) // 3600 % 24:02d}{(i * 21) // 60 % 60:02d}"
    if i in m:
        return [s, "-", "MARK", "0", m[i]]
    return [s, choice(rng, ["s3-eu", "s3-eu", "s3-eu2", "s3-us"]), choice(rng, ["PUT", "PUT", "GET", "GET", "DELETE"]), str(rint(rng, 100, 9000, 10)), rng.choice(EN_FILL)]


case("log-9435", sub="M9c", tt="time_window", topic="syncbytes", root="sync", names=["transfers.txt"], sep=" ",
     cols=["ts", "host", "op", "bytes", "note"], header=False, rows=(1250, 1350), readme_name="README.md", min=20, gen=xfer_gen,
     readme=["# Transfer log", "", "transfers.txt is one day of storage operations, space separated, no header: ts host op bytes note.", "Rows whose op is MARK are window markers (the marker name is in note). The real sync window runs from `SYNC-BEGIN` to `SYNC-END`; the `-TEST` markers belong to a dry run and do not count.", "Host names are whole values: `s3-eu2` is another host from `s3-eu`."],
     desc="Sums the bytes of PUT operations on one host inside the real sync window of one long transfer log where a dry-run window and a look-alike host exist",
     why="The window is delimited by two exact markers; host and op are whole-value columns.",
     queries=[dict(prompt="In sync/transfers.txt, what is the total of the bytes column for PUT operations on host s3-eu between SYNC-BEGIN and SYNC-END? sync/README.md says which markers count; reply with the number.", agg="between_sum", nth=1, col="bytes",
                   start='r["op"]=="MARK" and r["note"]=="SYNC-BEGIN"', end='r["op"]=="MARK" and r["note"]=="SYNC-END"', pred='r["op"]=="PUT" and r["host"]=="s3-eu"',
                   decoy=dict(start='r["note"].startswith("SYNC-BEGIN")', end='r["note"].startswith("SYNC-END")', pred='r["op"]=="PUT" and r["host"].startswith("s3-eu")'), decoy_note="dry-run window used, host prefix match",
                   cmd="""awk '$3=="MARK" && $5=="SYNC-BEGIN" {on=1; next} $3=="MARK" && $5=="SYNC-END" {on=0} on && $3=="PUT" && $2=="s3-eu" {s+=$4} END{print s+0}' sync/transfers.txt""", unit="PUT traffic on s3-eu inside the sync window totals {v} bytes.",
                   alts=["Total bytes written (PUT) to s3-eu during the real sync window.", "Between SYNC-BEGIN and SYNC-END, sum the bytes of PUT rows for host s3-eu.", "Per sync/README.md, how many bytes did s3-eu receive via PUT in the sync window?", "Dry-run markers excluded, add up the bytes of s3-eu PUT operations inside the window.", "What is the sum of bytes for s3-eu PUTs between the real SYNC-BEGIN and SYNC-END?"])])


def app_gen(rng, i, fi, n):
    return [f"1013T{(i * 25) // 3600 % 24:02d}{(i * 25) // 60 % 60:02d}", choice(rng, ["INFO", "INFO", "INFO", "WARN", "ERROR", "FATAL", "FATAL-RECOVERED"], [30, 30, 30, 8, 6, 1, 2]),
            choice(rng, ["billing", "billing", "billing-cron", "auth", "search"]), "msg=" + text_of(rng, 20, 60), "trace=" + "".join(rng.choice("0123456789abcdef") for _ in range(20))]


case("log-9436", sub="M9c", tt="locate_error", topic="firstfatal", root="svc", names=["app.txt"], sep=" ",
     cols=["ts", "level", "svc", "msg", "trace"], header=False, rows=(1250, 1350), readme_name="README.md", min=20, gen=app_gen,
     readme=["# Service log", "", "app.txt is one day of application log, space separated, no header: ts level svc msg trace. One entry per line.", "Level and svc are whole values: `FATAL-RECOVERED` is a self-healed crash and is not a `FATAL`, and `billing-cron` is a different service from `billing`."],
     desc="Finds the line number of the first FATAL entry of one service in one long application log where a recovered-fatal level and a cron service are look-alikes",
     why="level and svc are whole-value columns; the first matching line is unique.",
     queries=[dict(prompt="Which line of svc/app.txt holds the first FATAL entry from the billing service? svc/README.md explains the field values; reply with the line number.", agg="first_line",
                   pred='r["level"]=="FATAL" and r["svc"]=="billing"', decoy=dict(pred='r["level"].startswith("FATAL") and r["svc"].startswith("billing")'), decoy_note="level and svc prefix match",
                   cmd="""awk '$2=="FATAL" && $3=="billing" {print NR; exit}' svc/app.txt""", unit="The first billing FATAL is on line {v}.",
                   alts=["What is the line number of the earliest FATAL record for billing in app.txt?", "Find the first line where level is FATAL and svc is billing.", "Per svc/README.md, on which line does billing first report FATAL?", "FATAL-RECOVERED and billing-cron excluded, where is the first billing FATAL?", "Line number of the first FATAL entry logged by billing."])])


def dep_gen(rng, i, fi, n):
    return [f"1013T{(i * 33) // 3600 % 24:02d}{(i * 33) // 60 % 60:02d}", choice(rng, ["prod", "prod", "prod-canary", "stage", "dev"]), choice(rng, ["PENDING", "OK", "OK", "OK-PARTIAL", "ROLLED-BACK", "OK"]),
            "v" + str(rng.randint(1, 4)) + "." + str(rng.randint(0, 9)) + "." + str(rng.randint(0, 20)), rng.choice(EN_FILL) + "/" + rng.choice(EN_FILL)]


case("log-9437", sub="M9c", tt="locate_error", topic="thirdproddeploy", root="release", names=["deploys.dat"], sep=";",
     cols=["ts", "env", "result", "ver", "note"], header=False, rows=(1150, 1250), readme_name="README.md", min=20, gen=dep_gen,
     readme=["# Deploy history", "", "deploys.dat lists every deployment, semicolon separated, no header: ts;env;result;ver;note, one deployment per line.", "env and result are whole values: `prod-canary` is not `prod`, and `OK-PARTIAL` is not a finished `OK`."],
     desc="Finds the line number of the third successful production deployment in one long deploy history where a canary environment and a partial result are look-alikes",
     why="env and result are whole-value columns and the line number counts from the first line.",
     queries=[dict(prompt="In release/deploys.dat, which line holds the third deployment with env prod and result OK? release/README.md defines both values; reply with the line number.", agg="nth_line", nth=3,
                   pred='r["env"]=="prod" and r["result"]=="OK"', decoy=dict(pred='r["env"].startswith("prod") and r["result"].startswith("OK")'), decoy_note="env and result prefix match",
                   cmd="""awk -F';' '$2=="prod" && $3=="OK" {c++; if (c==3) {print NR; exit}}' release/deploys.dat""", unit="The third successful prod deployment is on line {v}.",
                   alts=["Line number of the 3rd prod deployment whose result is exactly OK.", "Counting only env prod and result OK rows, where does the third one sit?", "Per release/README.md, on which line is the third prod OK deployment?", "prod-canary and OK-PARTIAL excluded, find the third match and give its line number.", "Which line of deploys.dat is the third prod/OK row?"])])


def tkt_gen(rng, i, fi, n):
    kind = choice(rng, ["comment", "comment", "comment", "internal"])
    return [f"T{i + 1:05d}", kind, "agent_" + rng.choice("abcdefgh") + str(rng.randint(1, 9)), text_of(rng, 30, 380 if kind == "comment" else 560)]


case("tab-9438", sub="M9c", tt="rank", topic="longestcomment", root="support", names=["tickets.txt"], sep=T,
     cols=["id", "kind", "author", "body"], header=False, rows=(1100, 1200), readme_name="README.md", min=20, gen=tkt_gen,
     readme=["# Ticket notes", "", "tickets.txt holds every note of a support queue, tab separated, no header: id kind author body, one note per line. The body is lowercase words joined by hyphens.", "Kind `comment` is customer-visible, `internal` is staff-only. Lengths are compared on the whole line (tab characters included); line numbers start at 1 on the first line."],
     desc="Finds the line number of the longest customer-visible comment in one long ticket notes file where internal notes run even longer",
     why="kind is a whole-value column; the longest comment line is strictly longer than every other comment.",
     queries=[dict(prompt="In support/tickets.txt, which line number holds the longest comment (kind = comment)? support/README.md says how lengths are compared; reply with the line number.", agg="longest_line",
                   pred='r["kind"]=="comment"', decoy=dict(pred="True"), decoy_note="internal notes included, the longest line is internal",
                   cmd="""awk -F'\\t' '$2=="comment" {print length($0), NR}' support/tickets.txt | sort -rn | head -1""", unit="The longest comment is on line {v}.",
                   alts=["Which line of tickets.txt is the longest comment?", "Among rows of kind comment, which line has the most characters?", "Per support/README.md, give the line number of the longest customer-visible note.", "Internal notes excluded, find the longest comment line and report its line number.", "Line number of the longest line whose kind is comment."])])


def commit_gen(rng, i, fi, n):
    m = marks_at(n, {0.20: "FREEZE-START", 0.35: "FREEZE-END", 0.55: "FREEZE-START", 0.78: "FREEZE-END"})
    s = f"1013T{(i * 31) // 3600 % 24:02d}{(i * 31) // 60 % 60:02d}"
    if i in m:
        return [s, "-", "MARK", m[i]]
    return [s, "dev_" + rng.choice("abcdefgh"), choice(rng, ["MERGE", "MERGE", "PUSH", "PUSH", "REVERT", "REVIEW"]), "ref=" + text_of(rng, 24, 70)]


case("log-9439", sub="M9c", tt="time_window", topic="freezemerges", root="repo", names=["activity.dat"], sep=" ",
     cols=["ts", "author", "action", "ref"], header=False, rows=(1200, 1300), readme_name="README.md", min=20, gen=commit_gen,
     readme=["# Repository activity", "", "activity.dat is a month of repository events, space separated, no header: ts author action ref. Rows with action MARK are freeze markers (name in ref).", "The month had two code freezes: each runs from `FREEZE-START` to the next `FREEZE-END`. The second one is the release freeze."],
     desc="Counts MERGE events inside the second code freeze of one long repository activity file, where counting the first freeze gives a different number",
     why="Freezes are delimited by exact marker rows and the README names the second as the release freeze.",
     queries=[dict(prompt="How many MERGE events happened during the release freeze in repo/activity.dat (the second FREEZE-START to its FREEZE-END)? repo/README.md describes the markers; reply with the count.", agg="between", nth=2,
                   start='r["action"]=="MARK" and r["ref"]=="FREEZE-START"', end='r["action"]=="MARK" and r["ref"]=="FREEZE-END"', pred='r["action"]=="MERGE"',
                   decoy=dict(nth=1), decoy_note="counted the first freeze",
                   cmd="""awk '$3=="MARK" && $4=="FREEZE-START" {k++; if (k==2) on=1; next} $3=="MARK" && $4=="FREEZE-END" {on=0} on && $3=="MERGE" {c++} END{print c+0}' repo/activity.dat""", unit="{v} MERGE events fall inside the release freeze.",
                   alts=["Number of MERGE rows inside the second freeze window.", "From the second FREEZE-START to its FREEZE-END, count rows whose action is MERGE.", "Per repo/README.md, how many merges landed during the release freeze?", "Count MERGE actions in the release freeze (second window) of activity.dat.", "How many merge events were logged between the second FREEZE-START and the following FREEZE-END?"])])


def login_gen(rng, i, fi, n):
    return [f"1013T{(i * 19) // 3600 % 24:02d}{(i * 19) // 60 % 60:02d}", "u" + str(rng.randint(100, 480)), choice(rng, ["10.1.0.5", "10.1.0.5", "10.1.0.50", "10.1.0.6", "10.1.1.5"]),
            choice(rng, ["OK", "OK", "FAILED", "FAILED", "FAILED-LOCKED"], [8, 8, 3, 3, 2]), "agent=" + rng.choice(["firefox", "chrome", "edge"]) + "-" + rng.choice(["win11", "macos", "ubuntu"]) + "-" + rng.choice(EN_FILL)]


case("tab-9440", sub="M9c", tt="filter_count", topic="failedusers", root="auth", names=["logins.txt"], sep=" ",
     cols=["ts", "user", "ip", "result", "agent"], header=False, rows=(1250, 1350), readme_name="README.md", min=20, gen=login_gen,
     readme=["# Login attempts", "", "logins.txt is one day of login attempts, space separated, no header: ts user ip result agent. A user appears on many lines.", "ip and result are whole values: `10.1.0.50` is another address from `10.1.0.5`, and `FAILED-LOCKED` is an attempt on an already locked account, not a plain `FAILED`."],
     desc="Counts distinct users with a failed login from one IP address in one long login file where a longer address and a locked-account result are look-alikes",
     why="ip and result are whole-value columns; users repeat across rows and are de-duplicated.",
     queries=[dict(prompt="How many distinct users had a FAILED login from the address 10.1.0.5 in auth/logins.txt? auth/README.md defines the fields; reply with the number.", agg="distinct", col="user",
                   pred='r["ip"]=="10.1.0.5" and r["result"]=="FAILED"', decoy=dict(pred='r["ip"].startswith("10.1.0.5") and r["result"].startswith("FAILED")'), decoy_note="ip and result prefix match",
                   cmd="""awk '$3=="10.1.0.5" && $4=="FAILED" {print $2}' auth/logins.txt | sort -u | wc -l""", unit="{v} distinct users failed to log in from 10.1.0.5.",
                   alts=["Number of different users with a FAILED login from 10.1.0.5.", "Rows with ip 10.1.0.5 and result FAILED: how many unique users?", "Per auth/README.md, count the distinct users who failed from 10.1.0.5.", "10.1.0.50 and FAILED-LOCKED excluded, how many users failed from that address?", "How many different accounts had a plain FAILED attempt from 10.1.0.5?"])])


def _mk(cid):
    return lambda: build(cid)


BUILDERS = []
for _cid in sorted(CASES):
    BUILDERS.append(_mk(_cid))
    BUILDERS[-1].__name__ = _cid.replace("-", "_")

# static SPEC (specs.py loads this file by path and needs it at import time)
for _cid, _c in CASES.items():
    SPEC[_cid] = dict(kind="bash_aggregate", sub=_c["sub"], needs=[f"{_c['root']}/{_c['readme_name']}"])
