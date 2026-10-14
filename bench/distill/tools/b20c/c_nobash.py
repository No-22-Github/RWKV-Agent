"""C: no bash; counting/summing with data_query, search_text or read_file (20099-20110)."""
import csv
import io
from random import Random

from common import FORMS, lines, mk, value

BUILDERS = []
NB = ["bash"]


def reg(f):
    BUILDERS.append(f)
    return f


def csv_text(header, rows):
    return lines([",".join(header)] + [",".join(str(c) for c in r) for r in rows])


def orders(seed, n, zh=True):
    r = Random(seed)
    if zh:
        hdr = ["订单号", "渠道", "品类", "状态", "金额", "时长分钟"]
        ch, ca, st = ["小程序", "官网", "门店", "电话"], ["数码", "家居", "食品", "服饰"], ["已完成", "已取消", "待发货", "退款中"]
    else:
        hdr = ["order_id", "channel", "category", "status", "amount", "minutes"]
        ch, ca, st = ["app", "web", "store", "phone"], ["tech", "home", "food", "wear"], ["done", "cancelled", "pending", "refund"]
    rows = [("O%05d" % (20000 + i), r.choice(ch), r.choice(ca), r.choices(st, [5, 3, 2, 1])[0],
             "%d.%02d" % (r.randint(9, 899), r.randint(0, 99)), r.randint(2, 240)) for i in range(n)]
    return hdr, rows, csv_text(hdr, rows)


def forms(x):
    s = "%.2f" % x
    out = [s, s.rstrip("0").rstrip(".") if "." in s else s]
    whole, frac = s.split(".")
    g = "{:,}".format(int(whole)) + "." + frac
    out += [g, g.rstrip("0").rstrip(".")]
    return list(dict.fromkeys(out))


CNT = ('import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"][%r])))\n'
       'print(json.dumps({"expected_number": sum(1 for r in rows if r[%r] == %r)}))\n')
LOADF = 'import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"][%r])))\n'
AVG = ('import csv, io\nrows = [r for r in csv.DictReader(io.StringIO(case["files"][%r])) if r[%r] == %r]\n'
       'print(json.dumps({"expected_number": round(sum(float(r[%r]) for r in rows) / len(rows), 2)}))\n')


def simple(cid, prompt, files, never_must, body, exp, *, sub, desc, ref_text, why, tt="filter_count", extra_turn=None, traps=None):
    must = never_must
    turns = [(prompt, exp)] + ([extra_turn] if extra_turn else [])
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=NB, must=must,
       traps_notes=["The shell is missing: count with the table/search tools or by reading, not by a pipeline."],
       ref_text=ref_text, why=why, body=body, ref_calls=2)


@reg
def c1():
    h, rows, t = orders(1, 420)
    n = sum(1 for r in rows if r[3] == "已取消"); assert 100 <= n <= 999, n
    simple("tab-20099", "订单导出在 data/orders.csv。状态是「已取消」的订单有多少单？只回答数字。", {"data/orders.csv": t}, ["data_query"],
           CNT % ("data/orders.csv", "状态", "已取消"), value([str(n)], token=True, required=["data_query"]), sub="C-table", desc="Counts rows by status in a csv with no shell",
           ref_text="data_query path=data/orders.csv filter={状态:已取消} operation=count -> %d" % n, why="Exact match on the 状态 column of the one csv.")


@reg
def c2():
    h, rows, t = orders(2, 300)
    s = round(sum(float(r[4]) for r in rows if r[2] == "数码"), 2)
    body = ('import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"]["data/orders.csv"])))\n'
            's = round(sum(float(r["金额"]) for r in rows if r["品类"] == "数码"), 2)\n'
            'f = ["%.2f" % s]\nf.append(f[0].rstrip("0").rstrip("."))\ng = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]\n'
            'f += [g, g.rstrip("0").rstrip(".")]\nprint(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))\n')
    simple("tab-20100", "data/orders.csv 里品类是「数码」的订单，金额一共多少？保留两位小数，只回答数字。", {"data/orders.csv": t}, ["data_query"],
           body, value([], any_forms=forms(s), required=["data_query"], any_token=True), sub="C-table", desc="Sums an amount column for one category with no shell",
           ref_text="data_query filter={品类:数码} operation=sum field=金额 -> %.2f" % s, why="Exact category match; sum of the 金额 column.", tt="aggregate")


@reg
def c3():
    r = Random(3)
    L = []
    for i in range(300):
        lv = r.choices(["INFO", "ERROR", "WARN", "DEBUG"], [4, 4, 2, 1])[0]
        L.append("2026-09-15 %02d:%02d:%02d [%s] svc-%d %s" % (i // 13 % 24, i % 60, r.randint(0, 59), lv, r.randint(1, 4), r.choice(["request ok", "cache miss", "db retry", "queue full"])))
    n = sum(1 for x in L if "[ERROR]" in x); assert 100 <= n <= 999, n
    body = 'print(json.dumps({"expected_number": sum(1 for x in case["files"]["logs/app.log"].splitlines() if "[ERROR]" in x)}))\n'
    simple("log-20101", "logs/app.log 里一共有多少行是 ERROR 级别的？只回答数字。", {"logs/app.log": lines(L)}, ["search_text", "read_file"], body,
           value([str(n)], token=True), sub="C-log", desc="Counts ERROR lines in a log with no shell", tt="count_events",
           ref_text="search_text query='[ERROR]' path=logs/app.log, count the matches -> %d" % n, why="Level is a bracketed exact field on each line.")


@reg
def c4():
    r = Random(4)
    f = {}
    for i in range(37):
        f["docs/ch%02d/note-%02d.md" % (i % 6, i)] = "# n%d\n" % i
    for i in range(52):
        f["docs/ch%02d/img-%02d.png" % (i % 6, i)] = "x\n"
    body = 'print(json.dumps({"expected_number": sum(1 for p in case["files"] if p.endswith(".md"))}))\n'
    simple("fs-20102", "docs 目录下（包括子目录）一共有多少个 .md 文件？只回答数字。", f, ["list_files", "search_text"], body, value(["37"], token=True),
           sub="C-fs", desc="Counts markdown files in a tree with no shell", tt="count_by_type",
           ref_text="list_files docs recursively, count names ending in .md -> 37", why="One extension, one tree; png files are decoys.")


@reg
def c5():
    h, rows, t = orders(5, 260)
    sel = [float(r[5]) for r in rows if r[1] == "电话"]
    v = round(sum(sel) / len(sel), 2)
    simple("tab-20103", "data/orders.csv 里渠道是「电话」的订单，平均处理时长多少分钟？保留两位小数，只回答数字。", {"data/orders.csv": t}, ["data_query"],
           (LOADF % "data/orders.csv") + 'sel = [float(r["时长分钟"]) for r in rows if r["渠道"] == "电话"]\ns = round(sum(sel) / len(sel), 2)\n' + FORMS, value([], any_forms=forms(v), required=["data_query"]), sub="C-table",
           desc="Averages a column for one channel with no shell", tt="aggregate",
           ref_text="data_query filter={渠道:电话} operation=avg field=时长分钟 -> %.2f" % v, why="Exact channel match; mean of the 时长分钟 column rounded to two decimals.")


@reg
def c6():
    r = Random(6)
    L = []
    for i in range(320):
        lv = r.choices(["INFO", "WARN", "ERROR"], [4, 4, 1])[0]
        msg = r.choice(["upstream timeout", "slow query", "disk 80%", "retry ok", "connection reset"]) if lv != "INFO" else "heartbeat"
        L.append("%s %s %s" % ("2026-09-15T%02d:%02d" % (i // 14 % 24, i % 60), lv, msg))
    a = sum(1 for x in L if " WARN " in x); b = sum(1 for x in L if "timeout" in x)
    assert 100 <= a <= 999 and b >= 10, (a, b)
    f = {"logs/gateway.log": lines(L)}
    body = 'ls = case["files"]["logs/gateway.log"].splitlines()\nprint(json.dumps({"expected_number": sum(1 for x in ls if "timeout" in x)}))\n'
    simple("log-20104", "logs/gateway.log 里 WARN 级别的有多少行？只回答数字。", f, ["search_text", "read_file"], body, value([str(a)], token=True),
           sub="C-log-multi", desc="Counts WARN lines, then lines mentioning a timeout, with no shell", tt="count_events",
           extra_turn=("那整个文件里提到 timeout 的一共多少行？同样只回答数字。", value([str(b)], token=True)),
           ref_text="Turn 1: search_text ' WARN ' -> %d. Turn 2: search_text 'timeout' -> %d." % (a, b),
           why="Level and keyword are literal strings in each line; the two counts are different quantities.")


@reg
def c7():
    h, rows, t = orders(7, 380, zh=False)
    n = sum(1 for r in rows if r[1] == "web" and r[3] == "cancelled"); assert n >= 10, n
    body = ('import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])))\n'
            'print(json.dumps({"expected_number": sum(1 for r in rows if r["channel"] == "web" and r["status"] == "cancelled")}))\n')
    simple("tab-20105", "How many orders in exports/orders.csv came through the web channel and ended up cancelled? Just the number.",
           {"exports/orders.csv": t}, ["data_query"], body, value([str(n)], token=True, required=["data_query"]), sub="C-table",
           desc="Counts rows matching two columns with no shell", ref_text="data_query filter={channel:web,status:cancelled} operation=count -> %d" % n,
           why="Two exact column matches on one csv.")


@reg
def c8():
    r = Random(8)
    L = []
    for i in range(260):
        L.append('10.0.%d.%d - - [15/Sep/2026:%02d:%02d:00 +0800] "%s %s HTTP/1.1" %s' % (r.randint(0, 3), r.randint(2, 90), i // 11, i % 60,
                 r.choice(["GET", "POST"]), r.choice(["/login", "/api/items", "/health"]), r.choices(["200", "404", "500"], [6, 2, 1])[0]))
    n = sum(1 for x in L if x.endswith(" 500")); assert n >= 10
    body = 'print(json.dumps({"expected_number": sum(1 for x in case["files"]["access.log"].splitlines() if x.endswith(" 500"))}))\n'
    simple("log-20106", "How many requests in access.log got a 500 response? Reply with just the number.", {"access.log": lines(L)}, ["search_text", "read_file"],
           body, value([str(n)], token=True), sub="C-log", desc="Counts 500 responses in an access log with no shell", tt="count_events",
           ref_text="search_text ' 500' on access.log, keep lines ending in 500 -> %d" % n, why="Status is the last field of every line.")


@reg
def c9():
    h, rows, t = orders(9, 240, zh=False)
    s = round(sum(float(r[4]) for r in rows if r[2] == "food" and r[3] == "done"), 2)
    body = ('import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])))\n'
            's = round(sum(float(r["amount"]) for r in rows if r["category"] == "food" and r["status"] == "done"), 2)\n'
            'f = ["%.2f" % s]\nf.append(f[0].rstrip("0").rstrip("."))\ng = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]\n'
            'f += [g, g.rstrip("0").rstrip(".")]\nprint(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))\n')
    simple("tab-20107", "What is the total amount of completed (status done) food orders in exports/orders.csv? Two decimals, number only.",
           {"exports/orders.csv": t}, ["data_query"], body, value([], any_forms=forms(s), required=["data_query"], any_token=True), sub="C-table",
           desc="Sums an amount over two filters with no shell", tt="aggregate",
           ref_text="data_query filter={category:food,status:done} operation=sum field=amount -> %.2f" % s, why="Two exact column matches; sum of amount.")


@reg
def c10():
    ids = ["id-%04d" % i for i in range(1, 238)]
    body = 'print(json.dumps({"expected_number": len(case["files"]["data/ids.txt"].splitlines())}))\n'
    simple("fs-20108", "How many lines does data/ids.txt have? Just the number.", {"data/ids.txt": lines(ids)}, ["read_file", "search_text"], body,
           value(["237"], token=True), sub="C-fs", desc="Counts lines of a small file with no shell", tt="count_by_type",
           ref_text="read_file data/ids.txt; the last numbered line is 237", why="One id per line, no blank lines.")


@reg
def c11():
    h, rows, t = orders(11, 300, zh=False)
    n = sum(1 for r in rows if r[1] == "store")
    sel = [float(r[5]) for r in rows if r[1] == "store"]
    v = round(sum(sel) / len(sel), 2)
    body = ('import csv, io\nrows = [r for r in csv.DictReader(io.StringIO(case["files"]["exports/orders.csv"])) if r["channel"] == "store"]\n'
            'print(json.dumps({"expected_number": len(rows)}))\n')
    simple("tab-20109", "How many orders in exports/orders.csv were placed in store? Number only.", {"exports/orders.csv": t}, ["data_query"], body,
           value([str(n)], token=True, required=["data_query"]), sub="C-table-multi", desc="Counts store orders, then averages their minutes, with no shell",
           tt="aggregate", extra_turn=("And the average minutes for those store orders, two decimals? Number only.", value([], any_forms=forms(v))),
           ref_text="Turn 1: data_query count filter channel=store -> %d. Turn 2: avg minutes -> %.2f." % (n, v), why="One channel filter; count then mean of minutes.")


@reg
def c12():
    r = Random(12)
    L = []
    for i in range(300):
        L.append('{"ts": "2026-09-15T%02d:%02d:00", "level": "%s", "msg": "%s"}' % (i // 13 % 24, i % 60, r.choices(["info", "warn", "error"], [4, 4, 2])[0], r.choice(["ok", "slow", "retry"])))
    n = sum(1 for x in L if '"level": "warn"' in x); assert 100 <= n <= 999, n
    body = 'print(json.dumps({"expected_number": sum(1 for x in case["files"]["logs/events.jsonl"].splitlines() if \'"level": "warn"\' in x)}))\n'
    simple("log-20110", "logs/events.jsonl 里 level 是 warn 的记录有多少条？只回答数字。", {"logs/events.jsonl": lines(L)}, ["search_text", "data_query"],
           body, value([str(n)], token=True), sub="C-log", desc="Counts jsonl records by level with no shell", tt="aggregate_jsonl",
           ref_text="data_query filter={level:warn} operation=count on events.jsonl -> %d (or search_text)" % n, why="level is an exact field of every record.")
