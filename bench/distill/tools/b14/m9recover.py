"""b14 M9d / M9f / M9c-tail: recovering from what the sandbox does not have,
ids 10131-10160.

* M9d script (10131-10142): the user asks to run a python / node / perl / make
  / sqlite3 job; none of those exist (exit 127), so the job's logic has to be
  read and reproduced with awk/jq. Three cases have a second turn that changes
  the job's parameter.
* M9d curl / pip (10143-10148): curl is missing, the page is reachable through
  the web tools; pip is missing, the arithmetic does not need a package.
* M9f cwd (10149-10155): turn 1 cds into a folder, turn 2 asks about a file
  there; a same-named decoy sits at the root because cwd resets every call.
* M9c tail (10156-10160): one file past every read cap, the answer sits near
  the end, so a cut read gives a wrong (earlier) value.
"""
import json
from random import Random

from aggcore import Q, agg_case
from common import NOWEB, REFS, case, has, lines, phrasings, verify_src

BUILDERS = []


def reg(fn):
    BUILDERS.append(fn)
    return fn


def pick(rng, items, weights=None):
    return rng.choices(items, weights)[0] if weights else rng.choice(items)


# ------------------------------------------------------------------ M9d: missing interpreters

W_LEDGER = dict(fmt="csv", root="账本", files=["%s.csv" % m for m in ["2026-06", "2026-07", "2026-08", "2026-09"]], rows=(180, 230),
                cols=["凭证号", "科目", "金额", "状态"], readme_name="说明.md", task_type="reproduce_output",
                readme=["# 账本", "", "每月一个文件。状态：已入账、待审核、作废。"],
                gen=lambda rng, fi, i: {"凭证号": "V%d%04d" % (fi, i), "科目": pick(rng, ["差旅", "办公", "采购", "培训", "招待"]),
                                        "金额": "%.2f" % rng.uniform(10, 5000), "状态": pick(rng, ["已入账", "已入账", "已入账", "待审核", "作废"])},
                unique="脚本的筛选条件写在源码里；按同一条件复算只有一个结果。")

W_ERRLOG = dict(fmt="csv", root="data/errors", files=["%s.csv" % d for d in ["mon", "tue", "wed", "thu", "fri"]], rows=(220, 280),
                cols=["ts", "service", "level", "code"], readme_name="README.md", task_type="reproduce_output",
                readme=["# Error exports", "", "One file per weekday; level is ERROR or WARN."],
                gen=lambda rng, fi, i: {"ts": "T%d%04d" % (fi, i), "service": pick(rng, ["checkout", "search", "auth", "media", "notify"]),
                                        "level": pick(rng, ["ERROR", "WARN", "WARN"]), "code": "E%d" % rng.randint(10, 60)},
                unique="The script's filter is in its source; reproducing it gives one result.")

W_SHOP = dict(fmt="csv", root="订单数据", files=["%02d.csv" % d for d in range(1, 7)], rows=(200, 250), cols=["订单", "门店", "金额", "状态"],
              readme_name="说明.md", task_type="reproduce_output", readme=["# 订单数据", "", "门店编号 S1–S4。"],
              gen=lambda rng, fi, i: {"订单": "O%d%04d" % (fi, i), "门店": pick(rng, ["S1", "S2", "S3", "S4"]), "金额": str(rng.randint(5, 900)),
                                      "状态": pick(rng, ["完成", "完成", "退款"])},
              unique="脚本按门店参数过滤；复算条件相同则结果唯一。")

W_ACTIVITY = dict(fmt="csv", root="data/activity", files=["week-%d.csv" % w for w in range(36, 40)], rows=(260, 320), cols=["user", "day", "action"],
                  readme_name="README.md", task_type="reproduce_output", readme=["# Activity", "", "One row per user action."],
                  gen=lambda rng, fi, i: {"user": "u%03d" % rng.randint(1, 400), "day": "2026-09-%02d" % (fi * 7 + rng.randint(1, 7)),
                                          "action": pick(rng, ["login", "view", "purchase", "share"])},
                  unique="The script's definition is in its source.")

W_TIMESHEET = dict(fmt="csv", root="工时", files=["%s.csv" % n for n in ["研发一组", "研发二组", "测试组", "运维组"]], rows=(200, 260),
                   cols=["工号", "日期", "类型", "小时"], readme_name="说明.md", task_type="reproduce_output",
                   readme=["# 工时", "", "类型：正常、加班、调休。小时为整数。"],
                   gen=lambda rng, fi, i: {"工号": "E%d%02d" % (fi, rng.randint(1, 40)), "日期": "2026-09-%02d" % rng.randint(1, 30),
                                           "类型": pick(rng, ["正常", "正常", "正常", "加班", "调休"]), "小时": str(rng.randint(1, 8))},
                   unique="脚本只累加类型为加班的小时数。")

W_REVIEWS = dict(fmt="jsonl", root="data/applications", files=["batch-%d.jsonl" % i for i in range(1, 6)], rows=(200, 260),
                 readme_name="README.md", task_type="reproduce_output", readme=["# Applications", "", "One JSON object per line."],
                 gen=lambda rng, fi, i: {"id": "A%d%04d" % (fi, i), "status": pick(rng, ["approved", "rejected", "pending", "rejected_auto"]),
                                         "region": pick(rng, ["north", "south", "east", "west"]), "score": rng.randint(1, 100)},
                 unique="The script compares status for exact equality.")
W_REVIEWS["cols"] = None

W_SALES = dict(fmt="jsonl", root="销售", files=["%s.jsonl" % m for m in ["2026-07", "2026-08", "2026-09"]], rows=(220, 280),
               readme_name="说明.md", task_type="reproduce_output", readme=["# 销售明细", "", "每行一单，金额为整数（元）。"],
               gen=lambda rng, fi, i: {"单号": "S%d%04d" % (fi, i), "月份": "2026-%02d" % (fi + 7), "区域": pick(rng, ["华东", "华南", "华北", "西南"]),
                                       "金额": rng.randint(50, 3000)},
               unique="脚本按月份参数筛选后求和。")
W_SALES["cols"] = None

W_HTTP = dict(fmt="re", root="logs/www", files=["access-%d.log" % i for i in range(1, 6)], rows=(260, 320),
              pattern=r'(?P<ip>\S+) "(?P<method>[A-Z]+) (?P<path>\S+)" (?P<status>\d{3}) (?P<bytes>\d+)', template='{ip} "{method} {path}" {status} {bytes}',
              readme_name="README.md", task_type="reproduce_output", readme=["# www logs", "", "ip \"METHOD path\" status bytes"],
              gen=lambda rng, fi, i: {"ip": "192.0.2.%d" % rng.randint(1, 250), "method": pick(rng, ["GET", "POST"]), "path": pick(rng, ["/", "/shop", "/img/a.png", "/api/cart"]),
                                      "status": pick(rng, ["200", "200", "204", "301", "404", "500"]), "bytes": str(rng.randint(100, 20000))},
              unique="The script's status filter is in its source.")
W_HTTP["cols"] = None

W_KEYWORD = dict(fmt="re", root="客服记录", files=["%s.txt" % d for d in ["周一", "周二", "周三", "周四", "周五"]], rows=(260, 320),
                 pattern=r"(?P<line>.*)", template="{line}", header=False, readme_name="说明.md", task_type="reproduce_output",
                 readme=["# 客服记录", "", "每行一条留言。"],
                 gen=lambda rng, fi, i: {"line": "%s：%s" % (pick(rng, ["顾客", "客服"]), pick(rng, ["我要退货", "退货进度怎么样", "能不能换货", "发票什么时候开", "物流太慢了", "已为您登记退货", "谢谢"]))},
                 unique="脚本统计以「顾客：」开头且包含「退货」的行。")
W_KEYWORD["cols"] = None

W_PAYMENTS = dict(fmt="csv", root="data/payments", files=["%s.csv" % r for r in ["east", "west", "north", "south"]], rows=(220, 270),
                  cols=["id", "region", "status", "amount"], readme_name="README.md", task_type="reproduce_output",
                  readme=["# Payments", "", "One file per region; amount in whole dollars."],
                  gen=lambda rng, fi, i: {"id": "P%d%04d" % (fi, i), "region": ["east", "west", "north", "south"][fi], "status": pick(rng, ["paid", "paid", "failed", "refunded"]),
                                          "amount": str(rng.randint(5, 700))},
                  unique="The Makefile recipe's filter is explicit.")

W_PART = dict(fmt="csv", root="库存", files=["%s.csv" % w for w in ["华东仓", "华南仓", "华北仓"]], rows=(220, 270),
              cols=["料号", "仓库", "数量", "状态"], readme_name="说明.md", task_type="reproduce_output", readme=["# 库存", "", "每个仓一个文件。"],
              gen=lambda rng, fi, i: {"料号": "M%04d" % rng.randint(1, 3000), "仓库": ["华东仓", "华南仓", "华北仓"][fi], "数量": str(rng.randint(1, 200)),
                                      "状态": pick(rng, ["可用", "可用", "冻结", "报废"])},
              unique="Makefile 里的 awk 条件写得很明确。")

W_SIGNUPS = dict(fmt="csv", root="data/signups", files=["2026-09-%02d.csv" % d for d in range(1, 8)], rows=(200, 250),
                 cols=["email", "plan", "country", "trial"], readme_name="README.md", task_type="reproduce_output",
                 readme=["# Signups", "", "Daily exports; trial is yes/no."],
                 gen=lambda rng, fi, i: {"email": "user%d_%d@example.com" % (fi, i), "plan": pick(rng, ["free", "pro", "team"]), "country": pick(rng, ["DE", "FR", "US", "JP", "BR"]),
                                         "trial": pick(rng, ["yes", "no"])},
                 unique="The SQL filter is explicit in the script.")


def script_case(cid, world, queries, *, script_path, script_text, missing, desc, family, seed, axes=("ERR", "OBS")):
    extra = "- The sandbox has no %s, so running %s fails with `command not found` (exit 127); the job's logic has to be read and reproduced.\n" % (missing, script_path)
    def unfiltered(tables, qs):
        from aggcore import agg
        rows = [r for t in tables.values() for r in t]
        try:
            return {"TR-DEFN": str(agg(dict(qs[-1], pred="True"), rows))}
        except ValueError:
            return {"TR-DEFN": "UNKNOWN"}
    return agg_case(cid, world, queries, sub="M9d", seed=seed, desc=desc, family=family, traps=["TR-DEFN"], axes=axes, extra_decoys=unfiltered,
                    prefix_files={script_path: script_text}, notes_extra=extra, task_type="reproduce_output",
                    spec_extra={"kind": "cmd_missing", "script": missing if missing in ("make", "sqlite3") else script_path.rsplit("/", 1)[-1],
                                "needs": [script_path]})


SCRIPTS = [
    ("scr-10131", W_LEDGER, [Q("sumc", 'r["状态"]=="已入账"', "帮我跑一下 工具/月结.py，它会打印六到九月已入账的总金额，我要这个数。",
      "cat 账本/*.csv | awk -F, '$4==\"已入账\" {s+=$3} END {printf \"%.2f\\n\", s}'", "月结.py 会输出已入账合计 {v} 元——环境里没有 python，我按脚本逻辑用 awk 复算。", val='r["金额"]')],
     "工具/月结.py", lines(["import csv, glob", "total = 0.0", "for path in sorted(glob.glob('账本/*.csv')):", "    for row in csv.DictReader(open(path, encoding='utf-8')):",
                           "        if row['状态'] == '已入账':", "            total += float(row['金额'])", "print(f'已入账合计 {total:.2f}')"]), "python3",
     "Asks for a Python script's ledger total in a sandbox without python; the filter must be reproduced", "fam-scr-b14-ledgerpy-01"),
    ("scr-10132", W_ERRLOG, [Q("top", 'r["level"]=="ERROR"', "Run tools/worst_service.py and tell me which service it reports.",
      "cat data/errors/*.csv | awk -F, '$3==\"ERROR\" {print $2}' | sort | uniq -c | sort -rn | head -3", "worst_service.py would print {v} (most ERROR rows); python is not available, so I reproduced it with awk.", key='r["service"]')],
     "tools/worst_service.py", lines(["import csv, glob, collections", "c = collections.Counter()", "for p in glob.glob('data/errors/*.csv'):",
                                      "    for r in csv.DictReader(open(p)):", "        if r['level'] == 'ERROR':", "            c[r['service']] += 1",
                                      "print(c.most_common(1)[0][0])"]), "python3",
     "Asks for a Python script's top service in a sandbox without python; WARN rows must be left out", "fam-scr-b14-worstsvc-01"),
    ("scr-10133", W_SHOP, [Q("count", 'r["状态"]=="完成"', "执行 脚本/统计.py，看它输出的完成订单数。",
      "cat 订单数据/*.csv | awk -F, '$4==\"完成\"' | wc -l", "{v}。"),
      Q("count", 'r["状态"]=="完成" and r["门店"]=="S2"', "再用 --门店 S2 跑一次呢？",
        "cat 订单数据/*.csv | awk -F, '$4==\"完成\" && $2==\"S2\"' | wc -l", "加上 --门店 S2 时脚本会输出 {v}（只算 S2 的完成订单）。")],
     "脚本/统计.py", lines(["import argparse, csv, glob", "ap = argparse.ArgumentParser()", "ap.add_argument('--门店', dest='store')", "a = ap.parse_args()",
                           "n = 0", "for p in glob.glob('订单数据/*.csv'):", "    for r in csv.DictReader(open(p, encoding='utf-8')):",
                           "        if r['状态'] == '完成' and (a.store is None or r['门店'] == a.store):", "            n += 1", "print(n)"]), "python3",
     "Two turns: reproduces a Python order counter without python, then with its store parameter", "fam-scr-b14-storecount-01"),
    ("scr-10134", W_ACTIVITY, [Q("distinct", 'r["action"]=="purchase"', "Can you run scripts/buyers.py? I need the number it prints.",
      "cat data/activity/*.csv | awk -F, '$3==\"purchase\" {print $1}' | sort -u | wc -l", "buyers.py prints {v} (distinct users with a purchase); reproduced with awk since python is missing.", val='r["user"]')],
     "scripts/buyers.py", lines(["import csv, glob", "users = set()", "for p in glob.glob('data/activity/*.csv'):", "    for r in csv.DictReader(open(p)):",
                                 "        if r['action'] == 'purchase':", "            users.add(r['user'])", "print(len(users))"]), "python3",
     "Asks for a Python script's distinct-buyer count without python", "fam-scr-b14-buyerspy-01"),
    ("scr-10135", W_TIMESHEET, [Q("sum", 'r["类型"]=="加班"', "跑一下 工时/加班统计.py，告诉我九月加班一共多少小时。",
      "cat 工时/*.csv | awk -F, '$3==\"加班\" {s+=$4} END {print s}'", "加班统计.py 会输出 {v} 小时（只算类型=加班）。", val='r["小时"]')],
     "工时/加班统计.py", lines(["import csv, glob", "h = 0", "for p in glob.glob('工时/*.csv'):", "    for r in csv.DictReader(open(p, encoding='utf-8')):",
                               "        if r['类型'] == '加班':", "            h += int(r['小时'])", "print(h)"]), "python3",
     "Asks for a Python overtime total without python; normal and time-off rows must be excluded", "fam-scr-b14-overtimepy-01"),
    ("scr-10136", W_REVIEWS, [Q("count", 'r["status"]=="rejected"', "Run node scripts/rejected.js and give me the count.",
      "cat data/applications/*.jsonl | jq -s 'map(select(.status==\"rejected\")) | length'", "rejected.js prints {v}; node is not installed, so I counted exact status==\"rejected\" with jq (rejected_auto excluded).")],
     "scripts/rejected.js", lines(["const fs = require('fs');", "let n = 0;", "for (const f of fs.readdirSync('data/applications')) {",
                                   "  for (const line of fs.readFileSync('data/applications/' + f, 'utf8').split('\\n')) {",
                                   "    if (line && JSON.parse(line).status === 'rejected') n++;", "  }", "}", "console.log(n);"]), "node",
     "Asks for a Node script's count without node; an exact status comparison must be kept", "fam-scr-b14-rejectedjs-01"),
    ("scr-10137", W_SALES, [Q("sum", 'r["月份"]=="2026-08"', "用 node 跑一下 销售/汇总.js --月份 2026-08，看看结果。",
      "cat 销售/*.jsonl | jq -s 'map(select(.[\"月份\"]==\"2026-08\") | .[\"金额\"]) | add'", "{v}。", val='r["金额"]'),
      Q("sum", 'r["月份"]=="2026-08" and r["区域"]=="华南"', "如果再加 --区域 华南 呢？",
        "cat 销售/*.jsonl | jq -s 'map(select(.[\"月份\"]==\"2026-08\" and .[\"区域\"]==\"华南\") | .[\"金额\"]) | add'", "加上 --区域 华南 后结果是 {v} 元。", val='r["金额"]')],
     "销售/汇总.js", lines(["const fs = require('fs');", "const arg = (k) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };",
                           "const m = arg('--月份'), r = arg('--区域'); let s = 0;", "for (const f of fs.readdirSync('销售').filter(x => x.endsWith('.jsonl'))) {",
                           "  for (const l of fs.readFileSync('销售/' + f, 'utf8').split('\\n')) { if (!l) continue; const o = JSON.parse(l);",
                           "    if ((!m || o['月份'] === m) && (!r || o['区域'] === r)) s += o['金额']; } }", "console.log(s);"]), "node",
     "Two turns: reproduces a Node sales summary for a month without node, then adds a region parameter", "fam-scr-b14-salesjs-01"),
    ("scr-10138", W_HTTP, [Q("sum", 'r["status"].startswith("2")', "Please run tools/bytes.pl over the www logs and tell me the total it reports.",
      "cat logs/www/*.log | awk '$4 ~ /^2/ {s+=$5} END {print s}'", "bytes.pl reports {v} bytes (2xx responses only); perl is missing, so I reproduced it with awk.", val='r["bytes"]')],
     "tools/bytes.pl", lines(["#!/usr/bin/perl", "my $s = 0;", "for my $f (glob 'logs/www/*.log') {", "  open my $h, '<', $f;",
                              "  while (<$h>) { $s += $2 if /\" (2\\d\\d) (\\d+)$/; }", "}", "print \"$s\\n\";"]), "perl",
     "Asks for a Perl byte total without perl; only 2xx responses count", "fam-scr-b14-bytespl-01"),
    ("scr-10139", W_KEYWORD, [Q("count", 'r["line"].startswith("顾客：") and "退货" in r["line"]', "跑一下 统计/退货.pl，告诉我顾客提到退货的有几条。",
      "cat 客服记录/*.txt | grep '^顾客：' | grep -c 退货", "退货.pl 会输出 {v}（只算顾客说的、含「退货」的行）。")],
     "统计/退货.pl", lines(["#!/usr/bin/perl", "use utf8;", "my $n = 0;", "for my $f (glob '客服记录/*.txt') {", "  open my $h, '<:utf8', $f;",
                           "  while (<$h>) { $n++ if /^顾客：.*退货/; }", "}", "print \"$n\\n\";"]), "perl",
     "Asks for a Perl keyword count without perl; agent lines that mention the word must be left out", "fam-scr-b14-returnpl-01"),
    ("scr-10140", W_PAYMENTS, [Q("sum", 'r["status"]=="paid"', "Run make revenue and tell me the number.",
      "cat data/payments/*.csv | awk -F, '$3==\"paid\" {s+=$4} END {print s}'", "make revenue would print {v}; make isn't installed, so I ran its recipe's logic directly.", val='r["amount"]')],
     "Makefile", "revenue:\n\tcat data/payments/*.csv | awk -F, '$$3==\"paid\" {s+=$$4} END {print s}'\n\nclean:\n\trm -f out/*\n", "make",
     "Asks for a make target's output without make; the recipe has to be run by hand with $$ unescaped", "fam-scr-b14-makerevenue-01"),
    ("scr-10141", W_PART, [Q("sum", 'r["状态"]=="可用"', "执行 make 可用库存，看输出多少。",
      "cat 库存/*.csv | awk -F, '$4==\"可用\" {s+=$3} END {print s}'", "{v}。", val='r["数量"]'),
      Q("sum", 'r["状态"]=="可用" and r["仓库"]=="华东仓"', "那 make 华东可用 呢？", "awk -F, '$4==\"可用\" {s+=$3} END {print s}' 库存/华东仓.csv",
        "华东可用 目标会输出 {v}。", val='r["数量"]', scope=["华东仓.csv"])],
     "Makefile", "可用库存:\n\tcat 库存/*.csv | awk -F, '$$4==\"可用\" {s+=$$3} END {print s}'\n\n华东可用:\n\tawk -F, '$$4==\"可用\" {s+=$$3} END {print s}' 库存/华东仓.csv\n", "make",
     "Two turns: reproduces two make targets by hand without make", "fam-scr-b14-makestock-01"),
    ("scr-10142", W_SIGNUPS, [Q("count", 'r["plan"]=="pro" and r["trial"]=="no"', "Run queries/paid_pro.sql with sqlite3 and give me the count.",
      "cat data/signups/*.csv | awk -F, '$2==\"pro\" && $4==\"no\"' | wc -l", "The query returns {v}; sqlite3 is not available, so I counted the same rows with awk.")],
     "queries/paid_pro.sql", lines([".mode csv", ".import data/signups/2026-09-01.csv s", "-- (the import repeats for each daily file)",
                                    "SELECT count(*) FROM s WHERE plan = 'pro' AND trial = 'no';"]), "sqlite3",
     "Asks for a SQL query's count in a sandbox without sqlite3; the WHERE clause must be reproduced", "fam-scr-b14-sqlitepro-01"),
]


def _script(entry, seed):
    cid, world, queries, path, text, missing, desc, family = entry

    def build():
        return script_case(cid, world, queries, script_path=path, script_text=text, missing=missing, desc=desc, family=family, seed=seed)
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(SCRIPTS):
    BUILDERS.append(_script(_e, 14400 + _i))


# ------------------------------------------------------------------ M9d: pip is missing (the job needs no package)

PIPS = [
    ("tab-10143", W_LEDGER, [Q("count", 'r["状态"]=="作废" and r["科目"]=="招待"', "先 pip install pandas，然后帮我统计四个月账本里作废的招待费凭证有几张。",
      "cat 账本/*.csv | awk -F, '$2==\"招待\" && $4==\"作废\"' | wc -l", "作废的招待费凭证 {v} 张（环境没有 pip，这个统计用 awk 就够了）。")],
     "Asks to install pandas before a count; pip is missing and the count needs no package", "fam-tab-b14-nopip-01"),
    ("tab-10144", W_PAYMENTS, [Q("count", 'r["status"]=="refunded" and int(r["amount"])>=300', "pip install polars and use it to count refunds of $300 or more across the payment files.",
      "cat data/payments/*.csv | awk -F, '$3==\"refunded\" && $4>=300' | wc -l", "{v} refunds of $300 or more (pip is not available here; awk does the count).")],
     "Asks to install polars before a count; pip is missing and the count needs no package", "fam-tab-b14-nopip-02"),
]


def _pip(entry, seed):
    cid, world, queries, desc, family = entry

    def build():
        return agg_case(cid, world, queries, sub="M9d", seed=seed, desc=desc, family=family, traps=["TR-MULTISRC"], axes=("ERR", "OBS"),
                        task_type="filter_count", spec_extra={"kind": "cmd_missing", "script": "pip"},
                        notes_extra="- The sandbox has no pip; installing is not possible and not needed.\n")
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(PIPS):
    BUILDERS.append(_pip(_e, 14450 + _i))


# ------------------------------------------------------------------ M9d: curl is missing (web tools reach the page)


def curl_case(cid, *, url, title, content, note_file, prompt, answer, any_of, alts, reply, desc, family):
    fixture = [{"query_match": url.split("//")[1].split("/")[0].split(".")[-2], "url_match": url.split("//")[1], "url": url,
                "title": title, "snippet": content[:80], "content": content}]
    files = {note_file[0]: lines(note_file[1])}
    body = '''
page = case["web_fixture"][0]["content"]
assert case["files"][%r].startswith(%r)
assert %r in page
print(json.dumps({"expected_contains_any": %s}, ensure_ascii=False))
''' % (note_file[0], note_file[1][0], answer, json.dumps(any_of, ensure_ascii=False))
    notes = """## Traps
- The sandbox has no curl and no network; `curl %s` fails with command not found. The page is reachable through the web fetch tool.

## Reference solution
1. bash: `curl -s %s` -> command not found (optional; the recovery is the point)
2. web_fetch %s
Final answer: %s

## Why the answer is unique
The page states one value.
""" % (url, url, url, reply) + phrasings(*alts)
    path = case(cid, sub="M9d", spec={"kind": "cmd_missing", "script": "curl"}, desc=desc, task_type="lookup_value", family=family,
                ref_calls=1, files=files, turns=[{"prompt": prompt, "expect": {"output_contains_any": any_of, "max_output_chars": 600}}],
                verify=verify_src(files, body), notes=notes, web=fixture, axes=("ERR",))
    return path


@reg
def web_10145():
    content = json.dumps({"service": "Ferrowave CDN", "updated": "2026-09-16T02:10:00Z", "regions": [
        {"name": "eu-west", "status": "operational"}, {"name": "ap-east", "status": "partial_outage"}, {"name": "us-east", "status": "operational"}]})
    return curl_case("web-10145", url="https://status.ferrowave.net/api/summary.json", title="Ferrowave CDN status", content=content,
                     note_file=("ops/vendors.md", ["# Vendors", "", "CDN: Ferrowave. Status JSON: https://status.ferrowave.net/api/summary.json"]),
                     prompt="Can you run curl -s https://status.ferrowave.net/api/summary.json for me? I want to know if any Ferrowave region is in trouble.",
                     answer="ap-east", any_of=["ap-east"],
                     alts=["Which Ferrowave region is down right now?", "Check the Ferrowave status JSON for any outage.", "Is our CDN healthy in every region?",
                           "Fetch the Ferrowave status summary and name the bad region.", "Any partial outage on Ferrowave at the moment?"],
                     reply="ap-east has a partial outage according to Ferrowave's status summary (updated 2026-09-16 02:10 UTC); eu-west and us-east are operational. curl isn't available in the sandbox, so I fetched the page with the web tool.",
                     desc="Asks to curl a CDN status JSON; the sandbox has no curl, so the page must be fetched with the web tool", family="fam-web-b14-curlcdn-01")


@reg
def web_10146():
    content = "# 澜岳云 对象存储 价格\n\n标准存储：0.12 元/GB/月\n低频存储：0.08 元/GB/月\n归档存储：0.033 元/GB/月\n（2026-09-01 起执行）"
    return curl_case("web-10146", url="https://www.lanyue-cloud.cn/pricing/oss", title="澜岳云 对象存储 价格", content=content,
                     note_file=("采购/云存储.md", ["# 云存储选型", "", "澜岳云价格页：https://www.lanyue-cloud.cn/pricing/oss"]),
                     prompt="用 curl 抓一下 https://www.lanyue-cloud.cn/pricing/oss ，看看澜岳云低频存储现在每 GB 每月多少钱。",
                     answer="0.08", any_of=["0.08"],
                     alts=["澜岳云低频存储多少钱一个 G？", "查一下澜岳云对象存储低频档的单价", "澜岳云 OSS 低频存储价格", "低频存储在澜岳云每月每 GB 要多少",
                           "帮我看下澜岳云价格页里低频存储的价格"],
                     reply="澜岳云低频存储 0.08 元/GB/月（2026-09-01 起执行）。沙箱里没有 curl，我用网页抓取工具打开了价格页。",
                     desc="Asks to curl a pricing page; curl is missing so the page must be fetched with the web tool", family="fam-web-b14-curlprice-01")


@reg
def web_10147():
    content = "# Tallyhook 4.2 release notes\n\nReleased 2026-09-10.\n\n## Breaking changes\n- Minimum supported Node is now 20.\n- The `--legacy-auth` flag was removed."
    return curl_case("web-10147", url="https://tallyhook.dev/releases/4.2", title="Tallyhook 4.2 release notes", content=content,
                     note_file=("deps/README.md", ["# Dependencies", "", "tallyhook ^4.1 (release notes: https://tallyhook.dev/releases/4.2)"]),
                     prompt="Grab https://tallyhook.dev/releases/4.2 with curl and tell me which CLI flag 4.2 removed.",
                     answer="--legacy-auth", any_of=["--legacy-auth", "legacy-auth"],
                     alts=["What flag did Tallyhook 4.2 drop?", "Check the Tallyhook 4.2 notes for removed flags.", "Any breaking CLI change in Tallyhook 4.2?",
                           "Which option is gone in Tallyhook 4.2?", "Read the 4.2 release notes and list removed flags."],
                     reply="Tallyhook 4.2 removed the --legacy-auth flag (and now needs Node 20+). curl isn't installed here, so I fetched the release notes with the web tool.",
                     desc="Asks to curl release notes; curl is missing so the page must be fetched with the web tool", family="fam-web-b14-curlrelease-01")


@reg
def web_10148():
    content = "# 青禾开放平台 接口限流说明\n\n默认每个应用每分钟 600 次请求；超出返回 429。\n企业版可申请提升到每分钟 3000 次。"
    return curl_case("web-10148", url="https://open.qinghe-api.cn/docs/ratelimit", title="青禾开放平台 接口限流说明", content=content,
                     note_file=("对接/青禾.md", ["# 青禾对接", "", "限流文档：https://open.qinghe-api.cn/docs/ratelimit"]),
                     prompt="curl 一下 https://open.qinghe-api.cn/docs/ratelimit ，告诉我青禾接口默认每分钟限多少次。",
                     answer="600", any_of=["600"],
                     alts=["青禾开放平台默认限流是多少？", "青禾接口每分钟能调多少次", "查一下青禾 API 的默认频率限制", "青禾平台超过多少次会 429",
                           "青禾开放平台的限流文档里默认值是多少"],
                     reply="青禾开放平台默认每个应用每分钟 600 次，超出返回 429（企业版可提到 3000 次）。沙箱没有 curl，我用网页抓取工具读的文档。",
                     desc="Asks to curl an API rate-limit doc; curl is missing so the page must be fetched with the web tool", family="fam-web-b14-curlratelimit-01")


# ------------------------------------------------------------------ M9f: cwd does not carry over

CWDS = [
    ("cfg-10149", "服务/订单", "限流.yaml", {"限流.yaml": ["# 全局默认", "每秒请求: 200"], "服务/订单/限流.yaml": ["# 订单服务", "每秒请求: 75"],
                                           "服务/订单/入口.go": ["package main"], "服务/库存/限流.yaml": ["每秒请求: 120"]},
     "进到 服务/订单 目录，看下里面有哪些文件。", "里面那个 限流.yaml 的每秒请求上限是多少？", "75", "200", "订单服务的每秒请求上限是 75（服务/订单/限流.yaml，根目录默认是 200）。"),
    ("cfg-10150", "apps/billing", "settings.toml", {"settings.toml": ["# defaults", "retries = 3"], "apps/billing/settings.toml": ["# billing", "retries = 7"],
                                                    "apps/billing/Cargo.toml": ["[package]"], "apps/search/settings.toml": ["retries = 5"]},
     "cd into apps/billing and list what's there.", "What's the retries value in that settings.toml?", "7", "3", "Billing's settings.toml sets retries = 7 (apps/billing/settings.toml; the root default is 3)."),
    ("doc-10151", "项目/合同审批", "进度.md", {"进度.md": ["# 总进度", "当前阶段：立项"], "项目/合同审批/进度.md": ["# 合同审批", "当前阶段：法务复核"],
                                            "项目/合同审批/附件.txt": ["无"], "项目/报销系统/进度.md": ["当前阶段：上线"]},
     "cd 到 项目/合同审批 下面，看看有什么。", "这个项目的 进度.md 里写的当前阶段是什么？", "法务复核", "立项", "合同审批项目当前阶段是「法务复核」（项目/合同审批/进度.md；根目录的总进度写的是立项）。"),
    ("cfg-10152", "deploy/staging", "values.yaml", {"values.yaml": ["# chart defaults", "image_tag: 1.8.0"], "deploy/staging/values.yaml": ["# staging", "image_tag: 1.9.0-rc2"],
                                                    "deploy/staging/notes.txt": ["rc testing"], "deploy/prod/values.yaml": ["image_tag: 1.8.3"]},
     "Go into deploy/staging and show me the files.", "Which image tag does its values.yaml pin?", "1.9.0-rc2", "1.8.0", "Staging pins image_tag 1.9.0-rc2 (deploy/staging/values.yaml; the root chart default is 1.8.0)."),
    ("cfg-10153", "门店/杭州西湖店", "营业时间.txt", {"营业时间.txt": ["默认 10:00-22:00"], "门店/杭州西湖店/营业时间.txt": ["周末 09:00-23:30"],
                                                  "门店/杭州西湖店/菜单.md": ["# 菜单"], "门店/上海徐汇店/营业时间.txt": ["周末 10:00-22:30"]},
     "cd 进 门店/杭州西湖店 目录，看看有哪些文件。", "那家店周末几点关门？看它目录里的 营业时间.txt。", "23:30", "22:00", "杭州西湖店周末 23:30 关门（门店/杭州西湖店/营业时间.txt；根目录默认 22:00）。"),
    ("log-10154", "jobs/nightly", "last_run.log", {"last_run.log": ["status=ok exit=0"], "jobs/nightly/last_run.log": ["status=failed exit=137"],
                                                    "jobs/nightly/cron.txt": ["0 2 * * *"], "jobs/hourly/last_run.log": ["status=ok exit=0"]},
     "cd into jobs/nightly and tell me what files it has.", "What exit code did its last run end with?", "137", "0", "The nightly job's last run failed with exit 137 (jobs/nightly/last_run.log; the root file shows exit 0)."),
    ("cfg-10155", "插件/导出", "版本.txt", {"版本.txt": ["主程序 3.2.0"], "插件/导出/版本.txt": ["导出插件 0.9.4"], "插件/导出/readme.md": ["导出插件"],
                                        "插件/导入/版本.txt": ["导入插件 1.1.0"]},
     "到 插件/导出 目录下看看都有什么。", "它目录里的 版本.txt 写的版本号是多少？", "0.9.4", "3.2.0", "导出插件版本是 0.9.4（插件/导出/版本.txt；根目录的版本.txt 是主程序 3.2.0）。"),
]


def _cwd(entry):
    cid, subdir, name, tree, p1, p2, answer, decoy, reply = entry

    def build():
        files = {p: lines(v) for p, v in tree.items()}
        first_file = sorted(p.rsplit("/", 1)[1] for p in files if p.startswith(subdir + "/"))[0]
        body = '''
text = case["files"][%r]
assert %r in case["files"][%r]
print(json.dumps({"expected_string": %r}, ensure_ascii=False))
''' % (subdir + "/" + name, decoy, name, answer)
        body = body.replace('print(json.dumps({"expected_string": %r}' % answer, 'assert %r in text\nprint(json.dumps({"expected_string": %r}' % (answer, answer))
        notes = """## Traps
- TR-DECOY: the root %s says %s. Every bash call starts at the workspace root, so a turn-2 `cat %s` after turn 1's `cd %s` reads the root copy.

## Reference solution
Turn 1: bash `cd %s && ls` -> lists %s among others.
Turn 2: read %s/%s by its full path (read tool or bash) -> %s.
Final answer turn 2: %s

## Why the answer is unique
The question is about the file inside %s.
""" % (name, decoy, name, subdir, subdir, first_file, subdir, name, answer, reply, subdir)
        tok = answer.replace(".", "").replace(":", "").replace("-", "").isalnum() and answer.isdigit()
        e2 = {"output_contains": [answer], "max_output_chars": 600}
        if tok:
            e2["output_contains_token"] = True
        path = case(cid, sub="M9f", spec={"kind": "cwd_reset", "subdir": subdir, "file": name}, desc="Two turns: cd into a folder and list it, then read a same-named file whose root copy is a decoy",
                    task_type="precedence" if cid.startswith("cfg") else ("latest_version" if cid.startswith("doc") else "locate_error"),
                    family="fam-%s-b14-cwd-%s" % (cid.split("-")[0], cid.split("-")[1]), ref_calls=2, files=files,
                    turns=[{"prompt": p1, "expect": {"output_contains": [first_file], "max_output_chars": 600}}, {"prompt": p2, "expect": e2}],
                    verify=verify_src(files, body), notes=notes, traps=["TR-DECOY"], decoys={"TR-DECOY": decoy}, axes=("OBS", "ERR"))
        REFS[cid] = (files, ["cd %s && ls" % subdir, "cat %s/%s" % (subdir, name)], has(answer))
        return path
    build.__name__ = cid.replace("-", "_")
    return build


for _e in CWDS:
    BUILDERS.append(_cwd(_e))


# ------------------------------------------------------------------ M9c: answer near the end of a long file

W_DEPLOY = dict(fmt="kv", root="发布", files=["发布记录.log"], rows=(1500, 1600), cols=["时间", "服务", "版本", "结果"], readme_name="说明.md",
                task_type="locate_error", readme=["# 发布记录", "", "发布系统按时间顺序追加，一行一次发布。"],
                gen=lambda rng, fi, i: {"时间": "2026-%02d-%02dT%02d%02d" % (4 + i // 300, 1 + (i % 300) // 11, (i % 11) * 2, rng.randint(0, 59)),
                                        "服务": pick(rng, ["订单", "支付", "搜索", "会员", "推送"]), "版本": "v%d.%d.%d" % (rng.randint(1, 4), rng.randint(0, 20), rng.randint(0, 9)),
                                        "结果": pick(rng, ["成功"] * 12 + ["回滚"])},
                unique="记录按时间顺序追加，最后一条匹配行就是最近一次。")

W_BACKUP = dict(fmt="kv", root="backup", files=["runs.log"], rows=(1500, 1600), cols=["at", "db", "size_mb", "result"], readme_name="README.md",
                task_type="locate_error", readme=["# Backup runs", "", "Appended by the backup agent in time order."],
                gen=lambda rng, fi, i: {"at": "2026-%02d-%02dT%02d%02d" % (3 + i // 250, 1 + (i % 250) // 9, (i % 9) * 2, rng.randint(0, 59)),
                                        "db": pick(rng, ["orders", "users", "ledger", "events"]), "size_mb": str(rng.randint(100, 9000)),
                                        "result": pick(rng, ["ok"] * 15 + ["failed"])},
                unique="The log is append-only in time order; the last matching line is the latest.")

TAILS = [
    ("log-10156", W_DEPLOY, [Q("last", 'r["服务"]=="支付" and r["结果"]=="回滚"', "支付服务最近一次发布回滚是什么时候？",
      "grep ' 服务=支付 ' 发布/发布记录.log | grep ' 结果=回滚$' | tail -1", "支付服务最近一次回滚是 {v}。", val='r["时间"].split("=")[-1]')],
     "Finds the latest rollback for one service near the end of a deploy log past every read cap", "fam-log-b14-lastrollback-01"),
    ("log-10157", W_BACKUP, [Q("last", 'r["db"]=="ledger" and r["result"]=="failed"', "When did the ledger backup last fail?",
      "grep ' db=ledger ' backup/runs.log | grep ' result=failed$' | tail -1", "The last failed ledger backup was at {v}.", val='r["at"]')],
     "Finds the latest failed backup for one database near the end of a long run log", "fam-log-b14-lastbackup-01"),
    ("log-10158", W_DEPLOY, [Q("last", 'r["服务"]=="搜索"', "搜索服务现在线上跑的是哪个版本？以最后一次发布为准（回滚的也算最后一次）。",
      "grep ' 服务=搜索 ' 发布/发布记录.log | tail -1", "搜索服务最后一次发布的版本是 {v}。", val='r["版本"]')],
     "Finds the latest version deployed for one service at the tail of a long deploy log", "fam-log-b14-lastversion-01"),
    ("log-10159", W_BACKUP, [Q("last", 'r["db"]=="events"', "What size was the most recent events backup, in MB?",
      "grep ' db=events ' backup/runs.log | tail -1", "The most recent events backup was {v} MB.", val='r["size_mb"]')],
     "Reads the size of the latest backup for one database at the tail of a long run log", "fam-log-b14-lastsize-01"),
    ("log-10160", W_DEPLOY, [Q("count", 'r["结果"]=="回滚" and r["时间"]>="2026-09"', "九月份一共回滚了几次？",
      "grep '时间=2026-09' 发布/发布记录.log | grep -c ' 结果=回滚$'", "九月回滚 {v} 次。")],
     "Counts rollbacks in the last month of a long deploy log whose September part lies beyond the read cap", "fam-log-b14-seprollback-01"),
]


def _tail(entry, seed):
    cid, world, queries, desc, family = entry

    def build():
        return agg_case(cid, world, queries, sub="M9c", seed=seed, desc=desc, family=family, traps=["TR-TRUNC"], axes=("LNG", "OBS"),
                        notes_extra="- The answer sits in the last part of the file; a read that stops at 64KB sees an earlier match or none.\n")
    build.__name__ = cid.replace("-", "_")
    return build


for _i, _e in enumerate(TAILS):
    BUILDERS.append(_tail(_e, 14460 + _i))
