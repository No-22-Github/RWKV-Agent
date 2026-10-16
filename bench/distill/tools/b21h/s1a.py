"""b21h sub 1 (format mismatch) part a: 32301-32306."""
from common import make, csv, rng, L, NAMES, NOCALC, filler_keys

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c1():
    r = rng(1)
    st = ["Paid"] * 60 + ["Shipped"] * 40 + ["Cancelled"] * 20 + ["Refunded"] * 40
    r.shuffle(st)
    rows = [(1000 + i, r.choice(NAMES), s, r.randint(3, 9)) for i, s in enumerate(st)]
    f = {"orders.csv": csv(["order_id", "customer", "Status", "amount"], rows)}
    n = st.count("Refunded")
    tot = sum(x[3] for x in rows if x[2] == "Refunded")
    make("tab-32301", sub="fmt", task_type="filter_count", desc="Count refunded orders where the file spells the status with a capital letter",
         files=f, turns=[("orders.csv 里 refunded 的订单一共有多少条？", [str(n)], ["没有 refunded", "没有退款", "共 0", "是 0 条", "有 0 条"]),
                         ("这些退款订单的金额加起来是多少？", [str(tot)], None)],
         truth="ans = sum(1 for l in files['orders.csv'].splitlines()[1:] if l.split(',')[2].lower() == 'refunded')",
         ref=[("grep -ci refunded orders.csv", str(n)), ("awk -F, 'tolower($3)==\"refunded\"{s+=$4}END{print s}' orders.csv", str(tot))],
         lazy=[("grep -c refunded orders.csv", "zero")],
         notes={"traps": "Status values are written Refunded; a case-sensitive grep for refunded returns 0.", "steps": "head orders.csv; grep -ci refunded orders.csv; awk with tolower for the amount sum.", "unique": "Seven rows have Status Refunded; the amount sum follows from them."})


@reg
def c2():
    r = rng(2)
    regs = ["华东 "] * 54 + ["华北 "] * 42 + ["华南 "] * 72 + ["西南 "] * 30
    r.shuffle(regs)
    rows = [("C%03d" % (i + 1), r.choice(["蓝岸商贸", "云杉电器", "北辰五金", "海禾食品", "启明文具"]) + str(i), g, r.randint(1, 9)) for i, g in enumerate(regs)]
    f = {"customers.csv": csv(["id", "name", "region", "level"], rows)}
    n = regs.count("华南 ")
    make("tab-32302", sub="fmt", task_type="filter_count", desc="Count customers of a region whose values carry a trailing space",
         files=f, turns=[("customers.csv 里华南区的客户有几个？", [str(n)], ["共 0", "为 0", "有 0 个", "没有华南"])],
         truth="ans = sum(1 for l in files['customers.csv'].splitlines()[1:] if l.split(',')[2].strip() == '华南')",
         ref=[("awk -F, '{gsub(/ +$/,\"\",$3)} $3==\"华南\"{n++}END{print n}' customers.csv", str(n))],
         lazy=[("awk -F, '$3==\"华南\"{n++}END{print n+0}' customers.csv", "zero"), ("grep -c ',华南$' customers.csv", "zero")],
         notes={"traps": "Region values end with a space, exact match gets 0.", "steps": "awk -F, with gsub trim on $3.", "unique": "Five customers are 华南."})


@reg
def c3():
    r = rng(3)
    jobs = ["nightly-backup", "sync-ledger", "rebuild-index", "send-digest", "purge-tmp", "rotate-keys"]
    res = ["ok"] * 110 + ["failed"] * 70 + ["skipped"] * 55
    r.shuffle(res)
    rows = [("2026-09-%02d" % (1 + i % 15), r.choice(jobs), r.randint(3, 240), s) for i, s in enumerate(res)]
    f = {"job_runs.csv": csv(["date", "job", "seconds", "result"], rows, eol="\r\n")}
    n = res.count("failed")
    make("log-32303", sub="fmt", task_type="count_events", desc="Count failed jobs in a CRLF csv where the last column never equals the plain word",
         files=f, turns=[("job_runs.csv 记录的任务里，失败（failed）的有多少个？", [str(n)], ["共 0", "为 0", "有 0 个", "没有失败"]),
                         ("那 skipped 的呢？", [str(res.count("skipped"))], None)],
         truth="ans = sum(1 for l in files['job_runs.csv'].split('\\r\\n')[1:] if l.endswith(',failed'))",
         ref=[("tr -d '\\r' < job_runs.csv | awk -F, '$4==\"failed\"{n++}END{print n}'", str(n)), ("tr -d '\\r' < job_runs.csv | awk -F, '$4==\"skipped\"{n++}END{print n}'", str(res.count("skipped")))],
         lazy=[("awk -F, '$NF==\"failed\"{n++}END{print n+0}' job_runs.csv", "zero"), ("grep -c ',failed$' job_runs.csv", "zero")],
         notes={"traps": "CRLF line endings: the last field is failed plus carriage return.", "steps": "inspect with cat -A or od; strip CR with tr -d; then awk.", "unique": "70 failed, 55 skipped."})


@reg
def c4():
    r = rng(4)
    days = [r.choice(["2026/09/14", "2026/09/15", "2026/09/15", "2026/09/16"]) for _ in range(220)]
    rows = [("S%04d" % (7100 + i), d, r.choice(["tea", "mug", "lamp", "kettle"]), r.randint(1, 5)) for i, d in enumerate(days)]
    f = {"sales_2026-09.csv": csv(["sale_id", "sold_on", "item", "qty"], rows)}
    n = days.count("2026/09/15")
    make("tab-32304", sub="fmt", task_type="filter_count", desc="Count sales on a date written with slashes while the user writes dashes",
         files=f, turns=[("How many sales were recorded on 2026-09-15 in sales_2026-09.csv?", [str(n)], [" 0 sales", "is 0", "zero sales", "no sales"])],
         truth="ans = sum(1 for l in files['sales_2026-09.csv'].splitlines()[1:] if l.split(',')[1] == '2026/09/15')",
         ref=[("grep -c '2026/09/15' sales_2026-09.csv", str(n))],
         lazy=[("grep -c '2026-09-15' sales_2026-09.csv", "zero")],
         notes={"traps": "Dates are written 2026/09/15, a dash search finds nothing.", "steps": "head the file, then grep with slashes.", "unique": "Count of rows dated 2026/09/15."})


@reg
def c5():
    r = rng(5)
    lines = []
    cnt = 0
    for i in range(300):
        d = r.choice(["14/Sep/2026", "15/Sep/2026", "15/Sep/2026", "16/Sep/2026"])
        lv = r.choice(["INFO", "INFO", "WARN", "ERROR"])
        lines.append("%s:%02d:%02d:%02d +0800 %s gateway request id=%d" % (d, r.randint(0, 23), r.randint(0, 59), r.randint(0, 59), lv, 9000 + i))
        if d.startswith("15/") and lv == "ERROR":
            cnt += 1
    if cnt < 10:
        raise SystemExit("c5 seed gives %d" % cnt)
    f = {"gateway.log": "\n".join(lines) + "\n"}
    make("log-32305", sub="fmt", task_type="count_events", desc="Count ERROR lines for a day in a log that writes dates as dd/Mon/yyyy",
         files=f, turns=[("gateway.log 里 9 月 15 号出了多少条 ERROR？", [str(cnt)], ["共 0", "为 0", "有 0 条", "没有 ERROR", "没有错误"])],
         truth="ans = sum(1 for l in files['gateway.log'].splitlines() if l.startswith('15/Sep/2026') and ' ERROR ' in l)",
         ref=[("grep '^15/Sep/2026' gateway.log | grep -c ' ERROR '", str(cnt))],
         lazy=[("grep -c '2026-09-15.*ERROR' gateway.log", "zero"), ("grep -c '09-15' gateway.log", "zero")],
         notes={"traps": "Date format is 15/Sep/2026, not 2026-09-15.", "steps": "head -3; grep the dd/Mon/yyyy prefix then count ERROR.", "unique": "ERROR lines starting 15/Sep/2026."})


@reg
def c6():
    r = rng(6)
    fk = ["%s = %d" % (k.title(), r.randint(1, 900)) for k in filler_keys(r, 90, avoid=("timeout_seconds", "retry_limit"))]
    conf = L("# service tuning", *(fk[:40] + ["Timeout_Seconds = 135"] + fk[40:70] + ["Retry_Limit = 15"] + fk[70:]))
    f = {"relay.conf": conf}
    make("cfg-32306", sub="fmt", task_type="read_effective", desc="Read a setting whose key is capitalised differently from the user's spelling",
         files=f, turns=[("relay.conf 里 timeout_seconds 配的是多少？", ["135"], None),
                         ("那 retry_limit 呢？", ["15"], None)],
         truth="ans = [l.split('=')[1].strip() for l in files['relay.conf'].splitlines() if l.lower().startswith('timeout_seconds')][0]",
         ref=[("grep -i timeout_seconds relay.conf", "135"), ("grep -i retry_limit relay.conf", "15")],
         lazy=[("grep timeout_seconds relay.conf", "empty")],
         notes={"traps": "Keys are Capitalised; grep is case-sensitive.", "steps": "cat relay.conf or grep -i.", "unique": "Timeout_Seconds = 135."}, policy=NOCALC)
