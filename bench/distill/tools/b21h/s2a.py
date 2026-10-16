"""b21h sub 2 (column / separator traps) part a: 32313-32317."""
from common import make, csv, rng, L, NAMES, NOCALC

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c13():
    r = rng(13)
    amts = [r.randint(1, 6) for _ in range(200)]
    rows = [("2026-09-%02d" % (1 + i % 14), r.choice(["南京路店", "徐家汇店", "静安店"]), a, r.randint(1, 4)) for i, a in enumerate(amts)]
    f = {"sales_0915.tsv": csv(["date", "shop", "amount", "items"], rows, sep="\t")}
    t = sum(amts)
    make("tab-32313", sub="col", task_type="aggregate", desc="Sum a column of a tsv file with comma-based awk giving 0",
         files=f, turns=[("sales_0915.tsv 里的金额（amount）合计是多少？", [str(t)], ["合计 0", "总计 0", "共 0", "为 0", "是 0"]),
                         ("只算静安店的呢？", [str(sum(a for a, row in zip(amts, rows) if row[1] == "静安店"))], None)],
         truth="ans = sum(int(l.split('\\t')[2]) for l in files['sales_0915.tsv'].splitlines()[1:])",
         ref=[("awk -F'\\t' 'NR>1{s+=$3}END{print s}' sales_0915.tsv", str(t)),
              ("awk -F'\\t' 'NR>1&&$2==\"静安店\"{s+=$3}END{print s}' sales_0915.tsv", str(sum(a for a, row in zip(amts, rows) if row[1] == "静安店")))],
         lazy=[("awk -F, 'NR>1{s+=$3}END{print s+0}' sales_0915.tsv", "zero")],
         notes={"traps": "File is tab separated; -F, sees one field.", "steps": "head, notice tabs, awk -F'\\t'.", "unique": "Sum of column 3."})


@reg
def c14():
    r = rng(14)
    wh = ["Gdansk", "Bremen", "Turin"]
    rows = [("SK-%03d" % (i + 1), r.choice(wh), r.randint(1, 9)) for i in range(200)]
    f = {"stock.csv": csv(["sku", "warehouse", "qty"], rows, sep=";")}
    t = sum(x[2] for x in rows if x[1] == "Gdansk")
    make("tab-32314", sub="col", task_type="aggregate", desc="Total quantity for a warehouse in a semicolon separated file",
         files=f, turns=[("What is the total quantity held in the Gdansk warehouse according to stock.csv?", [str(t)], ["is 0", "total of 0", "no stock", "nothing in Gdansk", "not in the file"])],
         truth="ans = sum(int(l.split(';')[2]) for l in files['stock.csv'].splitlines()[1:] if l.split(';')[1] == 'Gdansk')",
         ref=[("awk -F';' '$2==\"Gdansk\"{s+=$3}END{print s}' stock.csv", str(t))],
         lazy=[("awk -F, '$2==\"Gdansk\"{s+=$3}END{print s+0}' stock.csv", "zero")],
         notes={"traps": "Semicolon separated.", "steps": "head, awk -F';'.", "unique": "Sum for Gdansk."}, policy=NOCALC)


@reg
def c15():
    r = rng(15)
    who = r.sample(NAMES, 5)
    cust = ["Ines Marchetti"] * 40 + [r.choice(who[1:]) for _ in range(200)]
    r.shuffle(cust)
    rows = [("OR-%04d" % (3100 + i), r.choice(["kettle", "lamp", "mug", "rug"]), c, r.randint(1, 3)) for i, c in enumerate(cust)]
    f = {"orders_q3.csv": csv(["order_id", "item", "customer", "qty"], rows)}
    n = cust.count("Ines Marchetti")
    make("tab-32315", sub="col", task_type="filter_count", desc="Count a customer's orders when the name sits in column 3, not 2",
         files=f, turns=[("How many orders did Ines Marchetti place in orders_q3.csv?", [str(n)], ["is 0", "no orders", "zero orders", " 0 orders", "not found"])],
         truth="ans = sum(1 for l in files['orders_q3.csv'].splitlines()[1:] if l.split(',')[2] == 'Ines Marchetti')",
         ref=[("awk -F, '$3==\"Ines Marchetti\"{n++}END{print n}' orders_q3.csv", str(n))],
         lazy=[("awk -F, '$2==\"Ines Marchetti\"{n++}END{print n+0}' orders_q3.csv", "zero")],
         notes={"traps": "Customer is column 3; item is column 2.", "steps": "head -3; awk on $3.", "unique": "Rows with that customer."})


@reg
def c16():
    r = rng(16)
    lv = ["INFO"] * 170 + ["ERROR"] * 90 + ["WARN"] * 54
    r.shuffle(lv)
    lines = ["2026-09-15 %02d:%02d:%02d %s %s %s" % (r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), l, r.choice(["auth", "db", "cache"]), r.choice(["token refreshed", "slow query", "connection reset"])) for l in lv]
    f = {"service.log": "\n".join(lines) + "\n"}
    n = lv.count("ERROR")
    make("log-32316", sub="col", task_type="count_events", desc="Count ERROR using the wrong whitespace field because the timestamp has two fields",
         files=f, turns=[("请用 awk 数一下 service.log 里 ERROR 级别的行有多少条。", [str(n)], ["共 0", "为 0", "有 0 条", "没有 ERROR"])],
         truth="ans = sum(1 for l in files['service.log'].splitlines() if l.split()[2] == 'ERROR')",
         ref=[("awk '$3==\"ERROR\"{n++}END{print n}' service.log", str(n))],
         lazy=[("awk '$2==\"ERROR\"{n++}END{print n+0}' service.log", "zero")],
         notes={"traps": "Date and time are separate fields so level is $3.", "steps": "head -2; awk $3.", "unique": "ERROR lines."})


@reg
def c17():
    r = rng(17)
    deps = ["研发"] * 112 + ["市场"] * 72 + ["财务"] * 48
    r.shuffle(deps)
    rows = [("E%03d" % (i + 1), r.choice(NAMES), d, r.randint(8, 30)) for i, d in enumerate(deps)]
    f = {"staff.txt": csv(["emp_id", "name", "dept", "salary_k"], rows, sep="|")}
    n = deps.count("研发")
    make("tab-32317", sub="col", task_type="filter_count", desc="Count staff of one department in a pipe separated file",
         files=f, turns=[("staff.txt 里研发部有多少人？", [str(n)], ["共 0", "为 0", "有 0 人", "没有研发"]),
                         ("研发部的平均薪资（单位 k）是多少？保留一位小数。", ["%.1f" % (sum(x[3] for x in rows if x[2] == "研发") / n)], None)],
         truth="ans = sum(1 for l in files['staff.txt'].splitlines()[1:] if l.split('|')[2] == '研发')",
         ref=[("awk -F'[|]' '$3==\"研发\"{n++}END{print n}' staff.txt", str(n)),
              ("awk -F'[|]' '$3==\"研发\"{s+=$4;n++}END{printf \"%.1f\\n\", s/n}' staff.txt", "%.1f" % (sum(x[3] for x in rows if x[2] == "研发") / n))],
         lazy=[("awk -F, '$3==\"研发\"{n++}END{print n+0}' staff.txt", "zero"), ("cut -d, -f3 staff.txt | grep -c 研发", "zero")],
         notes={"traps": "Pipe separated, file named .txt.", "steps": "head, awk -F'[|]'.", "unique": "Rows with dept 研发."})
