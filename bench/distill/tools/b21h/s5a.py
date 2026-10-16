"""b21h sub 5 (command unavailable or erroring) part a: 32339-32344."""
from common import make, csv, rng, L, NAMES, NOCALC

B = []


def reg(f):
    B.append(f)
    return f


@reg
def c39():
    r = rng(39)
    shops = ["枫林店", "东湖店", "望京店", "天河店"]
    ws = [r.choice(shops + ["东湖店", "东湖店"]) for _ in range(260)]
    rows = [("O%03d" % (i + 1), s, r.randint(10, 60)) for i, s in enumerate(ws)]
    f = {"orders.csv": csv(["oid", "shop", "amount"], rows)}
    cnt = {s: ws.count(s) for s in shops}
    top = max(cnt, key=cnt.get)
    assert sorted(cnt.values())[-1] != sorted(cnt.values())[-2]
    make("tab-32339", sub="cmd", task_type="rank", desc="Find the shop with most orders after a requested python script cannot run",
         files=f, turns=[("帮我写个小脚本统计 orders.csv 里每家店的订单数，最后告诉我订单最多的是哪家店。", [top], ["无法统计", "没有办法统计", "无法运行"]),
                         ("它一共有多少单？", [str(cnt[top])], None)],
         truth="import collections\nans = collections.Counter(l.split(',')[1] for l in files['orders.csv'].splitlines()[1:]).most_common(1)[0][0]",
         ref=[("awk -F, 'NR>1{c[$2]++}END{for(k in c)print c[k], k}' orders.csv | sort -rn | head -1", top), ("awk -F, '$2==\"%s\"{n++}END{print n}' orders.csv" % top, str(cnt[top]))],
         lazy=[("python3 -c \"import csv,collections; print(collections.Counter(r['shop'] for r in csv.DictReader(open('orders.csv'))).most_common(1))\"", "err")],
         notes={"traps": "python3 is not installed; awk does the same.", "steps": "if python fails switch to awk | sort.", "unique": "unique top shop."}, policy=NOCALC)


@reg
def c40():
    r = rng(40)
    vals = [r.randint(20, 70) for _ in range(200)]
    vals[-1] += (20 - sum(vals) % 20) % 20
    assert sum(vals) % 200 != 0
    rows = [("m%02d" % (i + 1), v) for i, v in enumerate(vals)]
    f = {"metrics.csv": csv(["id", "latency_ms"], rows)}
    avg = sum(vals) / len(vals)
    s = ("%g" % avg)
    make("tab-32340", sub="cmd", task_type="aggregate", desc="Average of a column after a python one-liner is unavailable",
         files=f, turns=[("Use a quick python one-liner to get the average latency_ms in metrics.csv and tell me the number.", [s], ["could not compute", "cannot compute", "unable to compute"])],
         truth="ans = '%g' % (sum(int(l.split(',')[1]) for l in files['metrics.csv'].splitlines()[1:]) / 200)",
         ref=[("awk -F, 'NR>1{s+=$2;n++}END{print s/n}' metrics.csv", s)],
         lazy=[("python3 -c \"print(sum(int(l.split(',')[1]) for l in open('metrics.csv').read().split()[1:])/20)\"", "err")],
         notes={"traps": "python3 is missing.", "steps": "awk average.", "unique": "mean of 20 values (x.5)."})


@reg
def c41():
    r = rng(41)
    hrs = []
    for h in range(8, 20):
        hrs += [h] * (20 if h != 14 else 60)
    lines = []
    for i, h in enumerate(hrs):
        lines.append("2026-09-15 %02d:%02d:%02d ERROR job-%d failed with code %d" % (h, r.randint(0, 59), r.randint(0, 59), i, r.choice([2, 7, 9])))
    for _ in range(150):
        lines.append("2026-09-15 %02d:%02d:%02d INFO heartbeat" % (r.randint(8, 19), r.randint(0, 59), r.randint(0, 59)))
    lines.sort()
    f = {"batch.log": "\n".join(lines) + "\n"}
    make("log-32341", sub="cmd", task_type="time_window", desc="Peak error hour after a python script request fails",
         files=f, turns=[("写个 python 脚本，把 batch.log 里 ERROR 按小时分组，告诉我哪个小时最多。", ["14"], ["无法统计", "没法统计"]),
                         ("那个小时具体有多少条 ERROR？", ["60"], None)],
         truth="ans = '14'",
         ref=[("grep ERROR batch.log | cut -d' ' -f2 | cut -d: -f1 | sort | uniq -c | sort -rn | head -1", "14"), ("grep -c '^2026-09-15 14:.* ERROR' batch.log", "60")],
         lazy=[("python3 batch_hours.py", "err")],
         notes={"traps": "No python; group by hour with cut|sort|uniq.", "steps": "grep ERROR | cut | uniq -c.", "unique": "hour 14 with 60 errors."})


@reg
def c42():
    r = rng(42)
    names = r.sample(NAMES, 13)
    rows = [("S%03d" % (i + 1), r.choice(names[:13]) if i >= 13 else names[i], r.randint(10, 90)) for i in range(250)]
    f = {"signups.csv": csv(["sid", "customer", "amount"], rows)}
    n = len(set(x[1] for x in rows))
    make("tab-32342", sub="cmd", task_type="aggregate", desc="Distinct customer count after sqlite3 is unavailable",
         files=f, turns=[("Load signups.csv into sqlite and tell me how many distinct customers there are.", [str(n)], ["cannot", "can't", "unable", "not possible"])],
         truth="ans = len(set(l.split(',')[1] for l in files['signups.csv'].splitlines()[1:]))",
         ref=[("cut -d, -f2 signups.csv | tail -n +2 | sort -u | wc -l", str(n))],
         lazy=[("sqlite3 :memory: '.mode csv' '.import signups.csv t' 'select count(distinct customer) from t'", "err")],
         notes={"traps": "sqlite3 missing.", "steps": "sort -u | wc -l.", "unique": "13 distinct."})


@reg
def c43():
    r = rng(43)
    ips = ["10.4.%d.%d" % (r.randint(0, 3), r.randint(2, 40)) for _ in range(14)]
    lines = ["2026-09-15 %02d:%02d GET /api/%s from %s %d" % (r.randint(0, 23), r.randint(0, 59), r.choice(["cart", "pay", "item"]), r.choice(ips), r.choice([200, 200, 404])) for _ in range(350)]
    n = len(set(l.split(" from ")[1].split()[0] for l in lines))
    f = {"access.log": "\n".join(lines) + "\n"}
    make("log-32343", sub="cmd", task_type="count_events", desc="Distinct IP count after perl is unavailable",
         files=f, turns=[("用 perl 一行命令把 access.log 里的 IP 都提出来，告诉我一共有几个不同的 IP。", [str(n)], ["无法提取", "没法提取", "无法统计"])],
         truth="ans = len(set(l.split(' from ')[1].split()[0] for l in files['access.log'].splitlines()))",
         ref=[("grep -oE 'from [0-9.]+' access.log | cut -d' ' -f2 | sort -u | wc -l", str(n))],
         lazy=[("perl -ne 'print $1,qq(\\n) if /from ([0-9.]+)/' access.log | sort -u | wc -l", "zero")],
         notes={"traps": "perl is missing; the pipeline's last command succeeds but earlier error matters.", "steps": "grep -o | sort -u | wc -l.", "unique": "distinct IPs."}, policy=NOCALC)


@reg
def c44():
    import json
    r = rng(44)
    ev = [{"id": i + 1, "ts": "2026-09-%02dT%02d:%02d:00Z" % (r.randint(13, 16), r.randint(0, 23), r.randint(0, 59)), "kind": r.choice(["login", "pay", "logout"])} for i in range(300)]
    n = sum(1 for e in ev if e["ts"] >= "2026-09-15T12:00:00Z")
    f = {"events.json": json.dumps(ev, indent=1) + "\n"}
    make("cfg-32344", sub="cmd", task_type="read_effective", desc="Events after a cutoff when jq date parsing is unsupported",
         files=f, turns=[("Use jq to parse the ts field in events.json as a date and count the events at or after 2026-09-15 12:00 UTC.", [str(n)], ["cannot parse", "can't parse", "unable to parse"])],
         truth="ans = sum(1 for e in __import__('json').loads(files['events.json']) if e['ts'] >= '2026-09-15T12:00:00Z')",
         ref=[("jq '[.[] | select(.ts >= \"2026-09-15T12:00:00Z\")] | length' events.json", str(n))],
         lazy=[("jq '[.[] | select((.ts | fromdateiso8601) >= 1789473600)] | length' events.json", "err")],
         notes={"traps": "jq strptime/mktime unsupported; ISO strings compare lexically.", "steps": "string compare in jq.", "unique": "count."}, policy=NOCALC)
