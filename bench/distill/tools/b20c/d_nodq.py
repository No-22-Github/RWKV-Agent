"""D: no data_query; summarise tables with bash or read_file + calculator (20111-20120)."""
from random import Random

from c_nobash import forms, orders
from common import FORMS as _F, has, lines, mk, value

BUILDERS = []
ND = ["data_query"]
FORMS = ('f = ["%.2f" % s]\nf.append(f[0].rstrip("0").rstrip("."))\ng = "{:,}".format(int(f[0].split(".")[0])) + "." + f[0].split(".")[1]\n'
         'f += [g, g.rstrip("0").rstrip(".")]\nprint(json.dumps({"expected_contains_any": list(dict.fromkeys(f))}))\n')
LOAD = 'import csv, io\nrows = list(csv.DictReader(io.StringIO(case["files"][%r])))\n'


def reg(f):
    BUILDERS.append(f)
    return f


def bash_case(cid, prompt, files, body, exp, cmds, last, *, sub, desc, tt, extra=None, ref_text, why, zh):
    turns = [(prompt, exp)] + ([extra[0]] if extra else [])
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=ND, must=["bash"],
       traps_notes=["No table query tool: a shell pipeline (awk) over the csv is the intended replacement."],
       ref_text=ref_text, why=why, body=body, ref_calls=len(cmds),
       ref=(cmds, has(*last)) if not extra else (cmds, lambda out, read, w=extra[1]: None if all(x in out for x in w) else "bad %r" % out[:200]))


@reg
def d1():
    h, rows, t = orders(21, 300)
    s = round(sum(float(r[4]) for r in rows if r[1] == "官网"), 2)
    body = LOAD % "data/orders.csv" + 's = round(sum(float(r["金额"]) for r in rows if r["渠道"] == "官网"), 2)\n' + FORMS
    bash_case("tab-20111", "data/orders.csv 里渠道是「官网」的订单，金额合计多少？保留两位小数，只回答数字。", {"data/orders.csv": t}, body,
              value([], any_forms=forms(s)),
              ["awk -F, '$2==\"官网\"{s+=$5} END{printf \"%.2f\\n\", s}' data/orders.csv"], forms(s)[:1], sub="D-bash", tt="aggregate",
              desc="Sums an amount column for one channel when no table tool exists", ref_text="bash: awk -F, sum column 5 where column 2 is 官网 -> %.2f" % s,
              why="Exact channel match; sum of 金额.", zh=True)


@reg
def d2():
    h, rows, t = orders(22, 300)
    cnt = {}
    for r in rows:
        cnt[r[2]] = cnt.get(r[2], 0) + 1
    top = sorted(cnt.items(), key=lambda x: -x[1]); assert top[0][1] > top[1][1]
    body = LOAD % "data/orders.csv" + ('c = {}\nfor r in rows:\n    c[r["品类"]] = c.get(r["品类"], 0) + 1\n'
                                       'print(json.dumps({"expected_string": max(c, key=c.get)}, ensure_ascii=False))\n')
    bash_case("tab-20112", "data/orders.csv 里哪个品类的订单最多？只回答品类名。", {"data/orders.csv": t}, body, value([top[0][0]]),
              ["awk -F, 'NR>1{c[$3]++} END{for(k in c) print c[k], k}' data/orders.csv | sort -rn | head -1"], [top[0][0]], sub="D-bash", tt="rank",
              desc="Finds the most frequent category when no table tool exists", ref_text="bash: awk count by column 3, sort -rn -> %s" % top[0][0],
              why="Counts per category differ (top %d vs %d)." % (top[0][1], top[1][1]), zh=True)


@reg
def d3():
    h, rows, t = orders(23, 280)
    n = sum(1 for r in rows if r[3] == "退款中")
    sel = [float(r[5]) for r in rows if r[3] == "退款中"]
    v = round(sum(sel) / len(sel), 2)
    body = LOAD % "data/orders.csv" + 'print(json.dumps({"expected_number": sum(1 for r in rows if r["状态"] == "退款中")}))\n'
    bash_case("tab-20113", "data/orders.csv 里状态是「退款中」的有多少单？只回答数字。", {"data/orders.csv": t}, body, value([str(n)], token=True),
              ["awk -F, '$4==\"退款中\"{n++} END{print n}' data/orders.csv", "awk -F, '$4==\"退款中\"{s+=$6;n++} END{printf \"%.2f\\n\", s/n}' data/orders.csv"],
              None, sub="D-bash-multi", tt="aggregate", extra=(("这些单子的平均处理时长是多少分钟？保留两位小数，只回答数字。", value([], any_forms=forms(v))), ["%.2f" % v]),
              desc="Counts refunding orders, then averages their minutes, when no table tool exists",
              ref_text="Turn 1: awk count -> %d. Turn 2: awk mean of column 6 -> %.2f." % (n, v), why="One status filter; count then mean.", zh=True)


@reg
def d4():
    h, rows, t = orders(24, 260, zh=False)
    sel = [float(r[5]) for r in rows if r[3] == "pending"]
    v = round(sum(sel) / len(sel), 2)
    body = LOAD % "exports/orders.csv" + 'sel = [float(r["minutes"]) for r in rows if r["status"] == "pending"]\ns = round(sum(sel) / len(sel), 2)\n' + FORMS
    bash_case("tab-20114", "What's the average handling time in minutes for pending orders in exports/orders.csv? Two decimals, number only.",
              {"exports/orders.csv": t}, body, value([], any_forms=forms(v)),
              ["awk -F, '$4==\"pending\"{s+=$6;n++} END{printf \"%.2f\\n\", s/n}' exports/orders.csv"], ["%.2f" % v], sub="D-bash", tt="aggregate",
              desc="Averages minutes for one status when no table tool exists", ref_text="bash: awk mean of column 6 where status is pending -> %.2f" % v,
              why="Exact status match; arithmetic mean rounded to two decimals.", zh=False)


@reg
def d5():
    h, rows, t = orders(25, 240, zh=False)
    best = max(rows, key=lambda r: float(r[4]))
    assert sorted(float(r[4]) for r in rows)[-1] > sorted(float(r[4]) for r in rows)[-2]
    body = LOAD % "exports/orders.csv" + 'b = max(rows, key=lambda r: float(r["amount"]))\nprint(json.dumps({"expected_string": b["order_id"]}))\n'
    bash_case("tab-20115", "Which order in exports/orders.csv has the largest amount? Give me the order id only.", {"exports/orders.csv": t}, body,
              value([best[0]]), ["sort -t, -k5 -rn exports/orders.csv | head -1"], [best[0]], sub="D-bash", tt="rank",
              desc="Finds the largest-amount order when no table tool exists", ref_text="bash: sort -t, -k5 -rn | head -1 -> %s" % best[0],
              why="Amounts are distinct at the top, so one id.", zh=False)


def small(cid, prompt, files, body, exp, *, sub, desc, tt, ref_text, why, extra=None):
    turns = [(prompt, exp)] + ([extra] if extra else [])
    mk(cid, sub=sub, task_type=tt, desc=desc, files=files, turns=turns, never=ND, must=["read_file", "calculator"],
       traps_notes=["No table query tool and a short table: read it and add it up by hand or with the calculator."],
       ref_text=ref_text, why=why, body=body, ref_calls=3)


@reg
def d6():
    r = Random(26)
    rows = [("2026-%02d" % m, r.randint(800, 4200) + r.choice([0, 0.5, 0.25])) for m in range(1, 13)]
    t = lines(["月份,开销"] + ["%s,%s" % x for x in rows])
    s = float(sum(x[1] for x in rows))
    body = ('rows = [l.split(",") for l in case["files"]["data/月度开销.csv"].splitlines()[1:]]\ns = round(sum(float(x[1]) for x in rows), 2)\n' + FORMS)
    small("tab-20116", "data/月度开销.csv 记了今年每个月的开销，全年合计多少？只回答数字。", {"data/月度开销.csv": t}, body,
          value([], any_forms=forms(s), required=["read_file"]), sub="D-small", tt="aggregate",
          desc="Totals twelve monthly amounts when no table tool exists", ref_text="read_file, add the 12 amounts (calculator) -> %.2f" % s, why="Twelve rows, one column.")


@reg
def d7():
    r = Random(27)
    rows = [("学生%d" % i, r.randint(55, 99)) for i in range(1, 10)]
    t = lines(["姓名,分数"] + ["%s,%d" % x for x in rows])
    v = round(sum(x[1] for x in rows) / len(rows), 2)
    body = 'rows = [l.split(",") for l in case["files"]["成绩/期中.csv"].splitlines()[1:]]\ns = round(sum(float(x[1]) for x in rows) / len(rows), 2)\n' + FORMS
    small("tab-20117", "成绩/期中.csv 里的平均分是多少？保留两位小数，只回答数字。", {"成绩/期中.csv": t}, body, value([], any_forms=forms(v), required=["read_file"]),
          sub="D-small", tt="aggregate", desc="Averages nine scores when no table tool exists", ref_text="read_file, sum/9 with the calculator -> %.2f" % v, why="Nine rows, one score column.")


@reg
def d8():
    r = Random(28)
    rows = [("产品%s" % c, r.randint(40, 400)) for c in "ABCDEFGH"]
    t = lines(["产品,销量"] + ["%s,%d" % x for x in rows])
    tot = sum(x[1] for x in rows)
    pct = round(rows[0][1] * 100 / tot, 1)
    body = ('rows = [l.split(",") for l in case["files"]["销售/销量.csv"].splitlines()[1:]]\nt = sum(int(x[1]) for x in rows)\n'
            'print(json.dumps({"expected_number": round(int(rows[0][1]) * 100 / t, 1), "total": t}))\n')
    small("tab-20118", "销售/销量.csv 里八个产品的总销量是多少？只回答数字。", {"销售/销量.csv": t}, body, value([str(tot)], token=True, required=["read_file"]),
          sub="D-small-multi", tt="aggregate", desc="Totals eight sales figures, then the share of the first product, when no table tool exists",
          extra=("产品A 占总销量的百分之几？保留一位小数，只回答数字。", value([str(pct)], token=True)),
          ref_text="Turn 1: read_file, sum -> %d. Turn 2: %d*100/%d -> %s." % (tot, rows[0][1], tot, pct), why="Eight rows; share of the first row over the total.")


@reg
def d9():
    r = Random(29)
    rows = [("item-%d" % i, r.randint(2, 20), "%d.%02d" % (r.randint(3, 60), r.randint(0, 99))) for i in range(1, 8)]
    t = lines(["item,qty,unit_price"] + ["%s,%d,%s" % x for x in rows])
    s = round(sum(q * float(p) for _, q, p in rows), 2)
    body = 'rows = [l.split(",") for l in case["files"]["quote.csv"].splitlines()[1:]]\ns = round(sum(int(x[1]) * float(x[2]) for x in rows), 2)\n' + FORMS
    small("tab-20119", "What does quote.csv add up to if I buy every line (qty times unit price)? Two decimals, number only.", {"quote.csv": t}, body,
          value([], any_forms=forms(s), required=["read_file"]), sub="D-small", tt="aggregate",
          desc="Totals qty times price over seven lines when no table tool exists", ref_text="read_file, qty*price per line, sum (calculator) -> %.2f" % s,
          why="Seven lines; each line is qty times unit_price.")


@reg
def d10():
    r = Random(30)
    rows = [("emp%d" % i, r.choice(["ops", "dev", "sales"]), r.randint(40, 95) * 100) for i in range(1, 13)]
    sel = [x[2] for x in rows if x[1] == "ops"]; assert len(sel) >= 3
    v = round(sum(sel) / len(sel), 2)
    t = lines(["name,dept,salary"] + ["%s,%s,%d" % x for x in rows])
    body = 'rows = [l.split(",") for l in case["files"]["hr/salaries.csv"].splitlines()[1:]]\nsel = [int(x[2]) for x in rows if x[1] == "ops"]\ns = round(sum(sel) / len(sel), 2)\n' + FORMS
    small("tab-20120", "What's the average salary in the ops department in hr/salaries.csv? Two decimals, number only.", {"hr/salaries.csv": t}, body,
          value([], any_forms=forms(v), required=["read_file"]), sub="D-small", tt="aggregate", desc="Averages salaries of one department when no table tool exists",
          ref_text="read_file, pick the ops rows, mean with the calculator -> %.2f" % v, why="Twelve rows, one department filter.")
