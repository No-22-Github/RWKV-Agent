"""b21g sub A (part 1): JSONL counting and grouped sums, 32201-32207."""
import json
from random import Random

from common import emit, jl, reg, retry


def cents(x):
    return "%d.%02d" % (x // 100, x % 100)


@reg
def a1(i):
    def build(i):
        rng = Random(3220100 + i * 7919)
        rows = []
        for n in range(1, rng.randint(520, 640)):
            st = rng.choices(["paid", "paid_partial", "refunded", "pending"], [10, 2, 3, 3])[0]
            r = {"order_id": "SO-%05d" % (40000 + n * 3 + rng.randint(0, 2)), "status": st,
                 "user": {"uid": "u%03d" % rng.randint(1, 300), "vip": rng.random() < 0.3}}
            k = rng.random()
            if k < 0.86:
                r["amount"] = rng.randint(900, 98000) / 100
            elif k < 0.93:
                r["amount"] = None
            r["created"] = "2026-09-%02d" % rng.randint(1, 15)
            rows.append(r)
        files = {"data/orders-0901-0915.jsonl": jl(rows)}

        def solve(files):
            rows = [json.loads(x) for x in files["data/orders-0901-0915.jsonl"].splitlines()]

            def tot(pred):
                return sum(round(r["amount"] * 100) for r in rows if pred(r) and r.get("amount") is not None)

            def f(c):
                return "%d.%02d" % (c // 100, c % 100)
            a = tot(lambda r: r["status"] == "paid")
            b = tot(lambda r: r["status"] == "paid" and r["user"]["vip"])
            d = tot(lambda r: r["status"].startswith("paid"))
            return {"turns": [{"number": f(a), "items": []}, {"number": f(b), "items": []}],
                    "decoys": {"TR-MISSING": f(d), "TR-DECOY": f(d)}}
        assert i or True
        return files, solve
    files, solve = retry(build)
    emit("tab-32201", sub="jsonl", task_type="aggregate", desc="Sums paid order amounts in a 600-line JSONL where some amounts are null or absent and a look-alike status exists",
         files=files, solve=solve, traps=["TR-MISSING", "TR-DECOY"],
         turns=[{"prompt": "data/orders-0901-0915.jsonl 是 9 月上半月的订单流水。状态为 paid 的订单，实收金额一共多少元？没有金额的订单不用算。"},
                {"prompt": "那这些已支付订单里，会员用户（vip 为 true）的实收一共多少元？"}],
         ref=(["jq -s 'map(select(.status==\"paid\" and .user.vip==true)|.amount//0)|add*100|round/100' data/orders-0901-0915.jsonl"], 0),
         notes_traps=["TR-MISSING: some orders have amount null or no amount key.", "TR-DECOY: status paid_partial also starts with paid; a loose grep over-counts."],
         notes_ref=["jq -s over the file filtering status==\"paid\", amount // 0, add.", "Turn 2 adds .user.vip==true."],
         unique="status is matched exactly and null/absent amounts contribute nothing, so the sum is unique.")


@reg
def a2(i):
    rng = Random(3220200 + i * 7919)
    rows = []
    for n in range(rng.randint(640, 760)):
        path = rng.choices(["/v2/checkout", "/v2/checkout/retry", "/v2/checkout-status", "/v2/cart", "/v2/search", "/health"], [5, 2, 2, 6, 6, 4])[0]
        r = {"ts": "2026-09-14T%02d:%02d:%02dZ" % (rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59)), "method": rng.choice(["GET", "POST"]),
             "path": path, "status": rng.choices([200, 201, 304, 404, 500, 502, 503], [30, 4, 4, 5, 4, 2, 2])[0]}
        if rng.random() < 0.85:
            r["latency_ms"] = rng.randint(12, 1900)
        rows.append(r)
    files = {"edge/access-0914.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["edge/access-0914.jsonl"].splitlines()]
        a = [r for r in rows if r["path"] == "/v2/checkout" and r["status"] >= 500]
        b = [r for r in a if r.get("latency_ms") is not None and r["latency_ms"] > 800]
        c = [r for r in rows if r["path"].startswith("/v2/checkout") and r["status"] >= 500]
        return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DECOY": len(c), "TR-MISSING": len([r for r in a if "latency_ms" in r])}}
    emit("tab-32202", sub="jsonl", task_type="filter_count", desc="Counts 5xx responses for one exact endpoint in a JSONL access log, then those slower than 800 ms where latency is sometimes absent",
         files=files, solve=solve, traps=["TR-DECOY", "TR-MISSING"], forbid_calc=True,
         turns=[{"prompt": "edge/access-0914.jsonl is yesterday's access log. How many requests to exactly /v2/checkout came back with a 5xx status?"},
                {"prompt": "Of those, how many took more than 800 ms?"}],
         ref=(["jq -s 'map(select(.path==\"/v2/checkout\" and .status>=500 and (.latency_ms//0)>800))|length' edge/access-0914.jsonl"], 0),
         notes_traps=["TR-DECOY: /v2/checkout/retry and /v2/checkout-status share the prefix.", "TR-MISSING: about 15% of lines have no latency_ms."],
         notes_ref=["jq -s filter on exact path and status>=500, length.", "Turn 2 adds (.latency_ms//0)>800."],
         unique="Exact path, numeric status and numeric latency comparison; absent latency cannot exceed 800.")


@reg
def a3(i):
    rng = Random(3220300 + i * 7919)
    devs = ["gw-%02d" % k for k in range(1, 13)]
    w = [rng.randint(2, 9) for _ in devs]
    rows = []
    for n in range(rng.randint(700, 820)):
        d = rng.choices(devs, w)[0]
        ev = {"code": "E%d" % rng.randint(100, 140)}
        if rng.random() < 0.93:
            ev["level"] = rng.choices(["error", "warn", "info"], [3, 4, 7])[0]
        rows.append({"device": d, "seq": n, "event": ev})
    files = {"iot/events.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["iot/events.jsonl"].splitlines()]
        err, tot = {}, {}
        for r in rows:
            tot[r["device"]] = tot.get(r["device"], 0) + 1
            if r["event"].get("level") == "error":
                err[r["device"]] = err.get(r["device"], 0) + 1
        er = sorted(err.items(), key=lambda kv: -kv[1])
        to = sorted(tot.items(), key=lambda kv: -kv[1])
        assert er[0][1] > er[1][1] and to[0][0] != er[0][0]
        return {"turns": [{"number": er[0][1], "items": [er[0][0]]}], "decoys": {"TR-DECOY": to[0][1], "TR-MISSING": er[1][1]}}
    emit("tab-32203", sub="jsonl", task_type="rank", desc="Finds the device with the most error-level events in a JSONL where the busiest device is not the one with most errors",
         files=files, solve=solve, traps=["TR-DECOY", "TR-MISSING"],
         turns=[{"prompt": "iot/events.jsonl 是网关上报的事件，一行一条。哪台设备上报的 error 级别事件最多？告诉我设备名和条数。"}],
         ref=(["jq -r 'select(.event.level==\"error\")|.device' iot/events.jsonl | sort | uniq -c | sort -rn | head -3"], 0),
         notes_traps=["TR-DECOY: the device with most events overall differs from the one with most errors.", "TR-MISSING: ~7% of events have no level."],
         notes_ref=["jq -r to print devices of error events, sort | uniq -c | sort -rn."],
         unique="Strict level==error; the winner has a clear margin over second place.")


@reg
def a4(i):
    rng = Random(3220400 + i * 7919)
    rows = []
    skus = ["BK-120", "BK-1200", "BK-12", "DV-040", "MG-777", "BK-120X"]
    for n in range(rng.randint(560, 680)):
        its = [{"sku": rng.choices(skus, [4, 3, 3, 3, 2, 1])[0], "qty": rng.randint(1, 4)} for _ in range(rng.randint(1, 4))]
        rows.append({"loan_id": "LN-%05d" % (7000 + n * 2 + rng.randint(0, 1)), "member": "M%04d" % rng.randint(1, 600), "items": its})
    files = {"library/loans-2026-09.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["library/loans-2026-09.jsonl"].splitlines()]
        a = sum(i["qty"] for r in rows for i in r["items"] if i["sku"] == "BK-120")
        b = sum(i["qty"] for r in rows for i in r["items"] if i["sku"].startswith("BK-120"))
        return {"turns": [{"number": a, "items": []}], "decoys": {"TR-DECOY": b}}
    emit("tab-32204", sub="jsonl", task_type="aggregate", desc="Sums nested item quantities for one SKU in a JSONL of loans with prefix-sharing SKUs",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "Each line of library/loans-2026-09.jsonl is one loan with a list of items. How many copies of SKU BK-120 were lent out in total (add up qty)? Only that exact SKU."}],
         ref=(["jq -s '[.[].items[]|select(.sku==\"BK-120\")|.qty]|add' library/loans-2026-09.jsonl"], 0),
         notes_traps=["TR-DECOY: BK-1200 and BK-120X start with BK-120."], notes_ref=["jq -s flatten items, select exact sku, add qty."],
         unique="Exact sku match on nested array items.")


@reg
def a5(i):
    rng = Random(3220500 + i * 7919)
    rows = []
    regs = ["华东", "华北", "华南", "西南"]
    for n in range(rng.randint(560, 700)):
        r = {"user": "U%03d" % rng.randint(1, 140), "event": rng.choices(["view", "cart", "purchase"], [8, 4, 3])[0], "t": 1757900000 + n * 37}
        if rng.random() < 0.9:
            r["props"] = {"region": rng.choice(regs), "app": rng.choice(["ios", "android", "web"])}
        rows.append(r)
    files = {"埋点/events.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["埋点/events.jsonl"].splitlines()]
        p = [r for r in rows if r["event"] == "purchase"]
        a = {r["user"] for r in p}
        b = {r["user"] for r in p if (r.get("props") or {}).get("region") == "华东"}
        return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-DUPROW": len(p), "TR-MISSING": len({r["user"] for r in p if r.get("props")})}}
    emit("tab-32205", sub="jsonl", task_type="aggregate", desc="Counts distinct purchasing users in a JSONL event stream, then those in one nested region where props may be absent",
         files=files, solve=solve, traps=["TR-DUPROW", "TR-MISSING"],
         turns=[{"prompt": "埋点/events.jsonl 是用户行为事件。event 是 purchase 的记录里，一共有多少个不同的用户下过单？"},
                {"prompt": "这些人里，在华东（props.region）的有多少个人？"}],
         ref=(["jq -s '[.[]|select(.event==\"purchase\" and .props.region==\"华东\")|.user]|unique|length' 埋点/events.jsonl"], 0),
         notes_traps=["TR-DUPROW: users purchase several times; event count differs from user count.", "TR-MISSING: about 10% of events have no props."],
         notes_ref=["jq -s select purchase, map user, unique, length.", "Turn 2 adds .props.region==华东 (absent props yields null, no match)."],
         unique="Distinct by user id; region taken from the same event.")


@reg
def a6(i):
    rng = Random(3220600 + i * 7919)
    regs = ["Harbor", "Uptown", "Lakeside", "Midtown", "Old Quarter", "Airport"]
    wt = [rng.randint(3, 9) for _ in regs]
    rows = []
    for n in range(rng.randint(580, 700)):
        r = {"sale": "S%05d" % (n * 4 + rng.randint(0, 3)), "channel": rng.choice(["store", "online"]), "amount_yuan": rng.randint(20, 3800)}
        r["region"] = rng.choices(regs, wt)[0] if rng.random() < 0.94 else None
        rows.append(r)
    files = {"sales/2026-q3.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["sales/2026-q3.jsonl"].splitlines()]
        s, c = {}, {}
        for r in rows:
            if r["region"] is None:
                continue
            s[r["region"]] = s.get(r["region"], 0) + r["amount_yuan"]
            c[r["region"]] = c.get(r["region"], 0) + 1
        rs = sorted(s.items(), key=lambda kv: -kv[1])
        rc = sorted(c.items(), key=lambda kv: -kv[1])
        assert rs[0][1] - rs[1][1] > 500 and rs[0][0] != rc[0][0]
        return {"turns": [{"number": rs[0][1], "items": [rs[0][0]]}], "decoys": {"TR-MISSING": rs[1][1], "TR-DECOY": rs[0][1] + 1}}
    emit("tab-32206", sub="jsonl", task_type="rank", desc="Finds the sales region with the highest total in a JSONL where region is sometimes null and the busiest region by count differs",
         files=files, solve=solve, traps=["TR-MISSING"],
         turns=[{"prompt": "Which region brought in the most money in sales/2026-q3.jsonl (add up amount_yuan per region)? Tell me the region and its total in yuan. Sales with no region are not counted."}],
         ref=(["jq -s 'map(select(.region!=null))|group_by(.region)|map({r:.[0].region,t:(map(.amount_yuan)|add)})|sort_by(-.t)|.[0:2]' -c sales/2026-q3.jsonl"], 0),
         notes_traps=["TR-MISSING: some sales have region null; the region with most rows is not the one with the largest sum."],
         notes_ref=["jq -s group_by region, sum amount_yuan, sort desc."], unique="Clear margin between first and second by total.")


@reg
def a7(i):
    rng = Random(3220700 + i * 7919)
    rows = []
    for n in range(rng.randint(420, 560)):
        pr = rng.choices(["P1", "P2", "P3"], [3, 5, 8])[0]
        rows.append({"ticket": "TK-%04d" % (1000 + n), "priority": pr, "resolved_at": ("2026-09-%02dT09:00:00Z" % rng.randint(1, 15)) if rng.random() < 0.7 else None,
                     "tags": rng.sample(["billing", "login", "export", "mobile", "api", "refund"], rng.randint(0, 3))})
    files = {"support/tickets.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["support/tickets.jsonl"].splitlines()]
        a = [r for r in rows if r["priority"] == "P1" and r["resolved_at"] is not None]
        b = [r for r in a if "billing" in r["tags"]]
        p1 = [r for r in rows if r["priority"] == "P1"]
        return {"turns": [{"number": len(a), "items": []}, {"number": len(b), "items": []}], "decoys": {"TR-MISSING": len(p1), "TR-DECOY": len([r for r in p1 if "billing" in r["tags"]])}}
    emit("tab-32207", sub="jsonl", task_type="filter_count", desc="Counts resolved P1 tickets in a JSONL where unresolved ones have a null timestamp, then those tagged billing",
         files=files, solve=solve, traps=["TR-MISSING", "TR-DECOY"],
         turns=[{"prompt": "support/tickets.jsonl has one ticket per line. How many P1 tickets already have a resolution time (resolved_at filled in)?"},
                {"prompt": "And how many of those carry the billing tag?"}],
         ref=(["jq -s 'map(select(.priority==\"P1\" and .resolved_at!=null and (.tags|index(\"billing\"))!=null))|length' support/tickets.jsonl"], 0),
         notes_traps=["TR-MISSING: unresolved tickets have resolved_at null.", "TR-DECOY: counting every P1 or every P1 billing ticket gives other numbers."],
         notes_ref=["jq -s select priority P1 and resolved_at!=null, length.", "Turn 2 adds the billing tag test."], unique="Exact priority, non-null resolved_at, tag membership.")


@reg
def a8(i):
    rng = Random(3220800 + i * 7919)
    rows = []
    for n in range(rng.randint(520, 640)):
        r = {"txn": "P%06d" % (200000 + n * 5 + rng.randint(0, 4)), "merchant": rng.choice(["晨光文具", "七号书店", "老张面馆", "小林烘焙"]), "amount": rng.randint(300, 52000) / 100}
        if rng.random() < 0.9:
            r["currency"] = rng.choices(["CNY", "HKD", "USD"], [7, 2, 1])[0]
        rows.append(r)
    files = {"财务/payments-0916.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["财务/payments-0916.jsonl"].splitlines()]

        def f(c):
            return "%d.%02d" % (c // 100, c % 100)
        a = sum(round(r["amount"] * 100) for r in rows if r.get("currency") == "CNY")
        b = sum(round(r["amount"] * 100) for r in rows)
        return {"turns": [{"number": f(a), "items": []}], "decoys": {"TR-MISSING": f(b), "TR-DECOY": f(b - 1)}}
    emit("tab-32208", sub="jsonl", task_type="aggregate", desc="Sums only CNY payment amounts in a JSONL with mixed currencies and a currency field that is sometimes absent",
         files=files, solve=solve, traps=["TR-MISSING"],
         turns=[{"prompt": "财务/payments-0916.jsonl 是今天的支付流水，每行一笔。币种是 CNY 的那些，金额一共是多少元？没写币种的不算。"}],
         ref=(["jq -s 'map(select(.currency==\"CNY\")|.amount)|add*100|round/100' 财务/payments-0916.jsonl"], 0),
         notes_traps=["TR-MISSING: ~10% of lines have no currency key; adding every amount mixes HKD and USD in."], notes_ref=["jq -s select currency CNY, sum amount, round to 2 decimals."],
         unique="Only rows with currency exactly CNY count.")


@reg
def a9(i):
    rng = Random(3220900 + i * 7919)
    jobs = ["build-linux", "build-mac", "unit", "e2e-web", "lint", "deploy-stg"]
    w = [rng.randint(1, 6) for _ in jobs]
    rows = []
    for n in range(rng.randint(600, 760)):
        rows.append({"run": 90000 + n, "job": rng.choices(jobs, w)[0], "branch": rng.choices(["main", "dev", "release"], [4, 6, 2])[0],
                     "result": rng.choices(["success", "failure", "cancelled"], [10, 3, 2])[0], "duration_s": rng.randint(30, 2400)})
    files = {"ci/runs.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["ci/runs.jsonl"].splitlines()]
        c = {}
        for r in rows:
            if r["branch"] == "main" and r["result"] == "failure":
                c[r["job"]] = c.get(r["job"], 0) + 1
        al = {}
        for r in rows:
            if r["result"] == "failure":
                al[r["job"]] = al.get(r["job"], 0) + 1
        rk = sorted(c.items(), key=lambda kv: -kv[1])
        ra = sorted(al.items(), key=lambda kv: -kv[1])
        assert rk[0][1] > rk[1][1] and ra[0][0] != rk[0][0]
        job = rk[0][0]
        secs = sum(r["duration_s"] for r in rows if r["branch"] == "main" and r["result"] == "failure" and r["job"] == job)
        return {"turns": [{"number": rk[0][1], "items": [job]}, {"number": secs, "items": []}],
                "decoys": {"TR-DECOY": ra[0][1], "TR-MULTISRC": rk[1][1]}}
    emit("tab-32209", sub="jsonl", task_type="rank", desc="Ranks CI jobs by failures on main only, then sums that job's failed main run durations",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "Look at ci/runs.jsonl. On the main branch only, which job failed most often, and how many times?"},
                {"prompt": "How many seconds in total did that job's failed runs on main take?"}],
         ref=(["jq -s 'map(select(.branch==\"main\" and .result==\"failure\"))|group_by(.job)|map({j:.[0].job,n:length,s:(map(.duration_s)|add)})|sort_by(-.n)|.[0].s' ci/runs.jsonl"], 0),
         notes_traps=["TR-DECOY: across all branches a different job fails most."], notes_ref=["jq -r failed main runs | sort | uniq -c | sort -rn.", "Sum duration_s of that job's failed main runs."],
         unique="Branch and result are exact strings; winner has a clear margin.")
