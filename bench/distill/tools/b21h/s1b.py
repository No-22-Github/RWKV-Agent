"""b21h sub 1 (format mismatch) part b: 32307-32312."""
from common import make, csv, rng, L, NAMES, NOCALC, people, filler_keys

B = []


def reg(f):
    B.append(f)
    return f


def json_ms(l):
    return int(l.split('"ms": ')[1].rstrip("}"))


@reg
def c7():
    r = rng(7)
    st = ["SHIPPED"] * 120 + ["DELAYED"] * 78 + ["RETURNED"] * 30
    r.shuffle(st)
    rows = [("SH-%d" % (5200 + i), r.choice(["Rotterdam", "Hamburg", "Antwerp", "Gdynia"]), s) for i, s in enumerate(st)]
    f = {"shipments.csv": csv(["ref", "port", "state"], rows)}
    n = st.count("DELAYED")
    make("tab-32307", sub="fmt", task_type="filter_count", desc="Count delayed shipments where states are stored in capitals",
         files=f, turns=[("Could you tell me how many shipments in shipments.csv are delayed?", [str(n)], [" 0 shipments", "is 0", "none are delayed", "no delayed"])],
         truth="ans = sum(1 for l in files['shipments.csv'].splitlines()[1:] if l.endswith(',DELAYED'))",
         ref=[("grep -ci delayed shipments.csv", str(n))], lazy=[("grep -c delayed shipments.csv", "zero")],
         notes={"traps": "State is upper-case DELAYED.", "steps": "grep -ci.", "unique": "13 DELAYED rows."})


@reg
def c8():
    r = rng(8)
    lv = ["info"] * 150 + ["warn"] * 85 + ["error"] * 40
    r.shuffle(lv)
    lines = ["2026-09-1%d 0%d:%02d:%02d [%s] worker-%d %s" % (r.randint(0, 6), r.randint(0, 9), r.randint(0, 59), r.randint(0, 59), l, r.randint(1, 4), r.choice(["queue drained", "slow upstream", "retrying task", "cache refreshed"])) for l in lv]
    f = {"worker.log": "\n".join(lines) + "\n"}
    n = lv.count("warn")
    make("log-32308", sub="fmt", task_type="count_events", desc="Count WARN lines in a log whose level tags are lower-case",
         files=f, turns=[("How many WARN entries does worker.log contain?", [str(n)], [" 0 WARN", "is 0", "no WARN", "zero WARN"])],
         truth="ans = sum(1 for l in files['worker.log'].splitlines() if '[warn]' in l)",
         ref=[("grep -c '\\[warn\\]' worker.log", str(n))], lazy=[("grep -c WARN worker.log", "zero")],
         notes={"traps": "Level tags are lower-case.", "steps": "head the log; grep -ci warn.", "unique": "[warn] lines."}, policy=NOCALC)


@reg
def c9():
    r = rng(9)
    amts = [r.randint(2, 9) for _ in range(150)]
    rows = [("EXP%02d" % (i + 1), r.choice(["打车", "餐费", "文具", "快递"]), "¥%d" % a) for i, a in enumerate(amts)]
    f = {"expenses.csv": csv(["id", "category", "amount"], rows)}
    t = sum(amts)
    make("tab-32309", sub="fmt", task_type="aggregate", desc="Sum an amount column whose cells carry a currency sign",
         files=f, turns=[("帮我把 expenses.csv 里所有报销金额加起来，总共多少钱？", [str(t)], ["总共 0", "共 0", "合计 0", "为 0 元", "是 0 元"])],
         truth="ans = sum(int(l.split(',')[2].lstrip('¥')) for l in files['expenses.csv'].splitlines()[1:])",
         ref=[("awk -F, 'NR>1{gsub(/¥/,\"\",$3);s+=$3}END{print s}' expenses.csv", str(t))],
         lazy=[("awk -F, 'NR>1{s+=$3}END{print s+0}' expenses.csv", "zero")],
         notes={"traps": "Amounts are strings like ¥35, a plain sum gives 0.", "steps": "inspect, strip the sign, sum.", "unique": "Sum of 16 amounts."})


@reg
def c10():
    r = rng(10)
    names = people(r, 200)
    rows = [("%06d" % (i + 30), n, r.choice(["gold", "silver"])) for i, n in enumerate(names)]
    f = {"members.csv": csv(["member_no", "name", "tier"], rows)}
    num = int(rows[137][0])
    who = rows[137][1]
    make("tab-32310", sub="fmt", task_type="filter_count", desc="Look up a member by number when ids are zero padded",
         files=f, turns=[("Who is member number %d in members.csv?" % num, [who], ["no member", "not found", "doesn't exist", "does not exist"])],
         truth="ans = [l.split(',')[1] for l in files['members.csv'].splitlines()[1:] if int(l.split(',')[0]) == %d][0]" % num,
         ref=[("awk -F, '$1+0==%d{print $2}' members.csv" % num, who)], lazy=[("grep -E '^%d,' members.csv" % num, "empty")],
         notes={"traps": "Ids are 6-digit zero padded.", "steps": "look at header/sample, match numerically.", "unique": "Single row."})


@reg
def c11():
    r = rng(11)
    names = ["%s_%s" % (a, b) for a in ["fast", "dark", "beta", "audit", "auto", "tele", "smart", "legacy"] for b in ["start", "mode", "search", "log", "update", "export", "cache", "api"]]
    vals = [r.choice(["On", "Enabled", "Yes"]) if i % 3 != 2 else r.choice(["Off", "Disabled", "No"]) for i in range(len(names))]
    f = {"features.conf": L("# feature switches", *["%s = %s" % (n, v) for n, v in zip(names, vals)])}
    n = sum(1 for v in vals if v in ("On", "Enabled", "Yes"))
    make("cfg-32311", sub="fmt", task_type="read_effective", desc="Count switches that are on when the file never spells true",
         files=f, turns=[("features.conf 里有几个功能开关是打开（true）的？", [str(n)], ["共 0", "没有开启", "没有打开", "全部关闭", "0 个"])],
         truth="ans = sum(1 for l in files['features.conf'].splitlines() if '=' in l and l.split('=')[1].strip() in ('On','Enabled','Yes'))",
         ref=[("grep -cE '= (On|Enabled|Yes)$' features.conf", str(n))], lazy=[("grep -ci '= true' features.conf", "zero")],
         notes={"traps": "Values are On/Enabled/Yes, never true.", "steps": "cat the file; count the on-like values.", "unique": "Switches that are on."}, policy=NOCALC)


@reg
def c12():
    r = rng(12)
    codes = [r.choice(["200", "200", "200", "404", "500"]) for _ in range(300)]
    lines = ['{"ts": "2026-09-1%d", "path": "%s", "status": "%s", "ms": %d}' % (r.randint(0, 5), r.choice(["/cart", "/pay", "/search"]), c, r.randint(11, 900)) for c in codes]
    f = {"requests.jsonl": "\n".join(lines) + "\n"}
    n = codes.count("500")
    mx = max(json_ms(l) for l, c in zip(lines, codes) if c == "500")
    make("log-32312", sub="fmt", task_type="aggregate_jsonl", desc="Count status 500 in jsonl where status is a quoted string with a space after the colon",
         files=f, turns=[("requests.jsonl 里状态码 500 的请求有多少条？", [str(n)], ["共 0", "没有 500", "有 0 条", "为 0"]),
                         ("这些 500 请求里，耗时最长的是多少毫秒？", [str(mx)], None)],
         truth="ans = sum(1 for l in files['requests.jsonl'].splitlines() if '\"status\": \"500\"' in l)",
         ref=[("grep -c '\"status\": \"500\"' requests.jsonl", str(n)), ("grep '\"status\": \"500\"' requests.jsonl | jq -s 'map(.ms)|max'", str(mx))],
         lazy=[("grep -c '\"status\":500' requests.jsonl", "zero")],
         notes={"traps": "Status is a string and the file has a space after the colon.", "steps": "head -2, grep with the right spelling, jq for max.", "unique": "Count of status 500 rows."})
