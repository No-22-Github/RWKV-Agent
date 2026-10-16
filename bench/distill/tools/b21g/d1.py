"""b21g sub D: reconcile two lists, 32235-32242 (tabular)."""
import json
from random import Random

from common import L, emit, jl, reg


def pool(rng, prefix, n, width=5, start=1000):
    ids = rng.sample(range(start, start + n * 4), n)
    return ["%s%0*d" % (prefix, width, x) for x in sorted(ids)]


def split(rng, ids, ka, kb):
    """Returns (both, only_a, only_b)."""
    ids = list(ids)
    rng.shuffle(ids)
    oa, ob = ids[:ka], ids[ka:ka + kb]
    both = ids[ka + kb:]
    return sorted(both), sorted(oa), sorted(ob)


@reg
def d1(i):
    rng = Random(3223500 + i * 7919)
    ids = pool(rng, "INV-", rng.randint(330, 420), 5, 20000)
    both, oa, ob = split(rng, ids, rng.randint(4, 7), rng.randint(5, 9))
    amt = {x: rng.randint(900, 90000) / 100 for x in ids}
    led = L("inv_id,amount,customer", *["%s,%.2f,%s" % (x, amt[x], rng.choice(["Ames", "Brill", "Cole"])) for x in sorted(both + oa)])
    bank = jl([{"ref": x, "amount": amt[x], "cleared": "2026-09-%02d" % rng.randint(1, 15)} for x in rng.sample(both + ob, len(both + ob))])
    files = {"finance/ledger.csv": led, "finance/bank.jsonl": bank}

    def solve(files):
        led = {l.split(",")[0] for l in files["finance/ledger.csv"].splitlines()[1:]}
        bank = {json.loads(l)["ref"] for l in files["finance/bank.jsonl"].splitlines()}
        oa = sorted(led - bank)
        return {"turns": [{"number": len(oa), "items": oa}], "decoys": {"TR-DECOY": len(bank - led), "TR-TRUNC": len(led)}}
    emit("tab-32235", sub="reconcile", task_type="reconcile", desc="Lists ledger invoices that never cleared the bank when the bank file also has entries unknown to the ledger",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "finance/ledger.csv 是应收发票，finance/bank.jsonl 是银行到账记录（ref 就是发票号）。哪些发票在账上有，但银行里没有到账？告诉我有几张，并列出发票号。"}],
         ref=(["jq -r .ref finance/bank.jsonl | sort > /tmp/b.txt; tail -n +2 finance/ledger.csv | cut -d, -f1 | sort > /tmp/l.txt; comm -23 /tmp/l.txt /tmp/b.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt"], 0),
         notes_traps=["TR-DECOY: the bank has extra entries absent from the ledger (the other direction)."], notes_ref=["sort both id lists, comm -23."], unique="Set difference, one direction.")


@reg
def d2(i):
    rng = Random(3223600 + i * 7919)
    ids = pool(rng, "E", rng.randint(300, 380), 4, 1000)
    both, oa, ob = split(rng, ids, rng.randint(5, 8), rng.randint(4, 7))
    roster = L("id,name,dept", *["%s,Person %s,%s" % (x, x, rng.choice(["ops", "dev", "fin"])) for x in sorted(both + oa)])
    payroll = L("emp_id,gross", *["%s,%d" % (x, rng.randint(4000, 30000)) for x in sorted(both + ob)])
    files = {"hr/roster.csv": roster, "hr/payroll-sep.csv": payroll}

    def solve(files):
        r = {l.split(",")[0] for l in files["hr/roster.csv"].splitlines()[1:]}
        p = {l.split(",")[0] for l in files["hr/payroll-sep.csv"].splitlines()[1:]}
        o = sorted(p - r)
        return {"turns": [{"number": len(o), "items": o}], "decoys": {"TR-DECOY": len(r - p)}}
    emit("tab-32236", sub="reconcile", task_type="reconcile", desc="Finds payroll employee ids that are not on the roster when some roster people are not on payroll",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "hr/roster.csv is the current employee roster and hr/payroll-sep.csv is what payroll paid in September. Who is being paid but isn't on the roster? Give me the count and the employee ids."}],
         ref=(["tail -n +2 hr/payroll-sep.csv | cut -d, -f1 | sort > /tmp/p.txt; tail -n +2 hr/roster.csv | cut -d, -f1 | sort > /tmp/r.txt; comm -23 /tmp/p.txt /tmp/r.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt"], 0),
         notes_traps=["TR-DECOY: roster-only people exist too."], notes_ref=["comm -23 payroll roster."], unique="Direction fixed by the question.")


@reg
def d3(i):
    rng = Random(3223700 + i * 7919)
    ids = pool(rng, "SO", rng.randint(300, 380), 6, 100000)
    both, oa, ob = split(rng, ids, 0, rng.randint(4, 7))
    price = {x: rng.randint(50, 5000) for x in ids}
    bad = sorted(rng.sample(both, rng.randint(5, 8)))
    orders = L("order,amount", *["%s,%d" % (x, price[x]) for x in sorted(both)])
    ship = jl([{"order": x, "billed": price[x] + (rng.choice([-40, 15, 120]) if x in bad else 0)} for x in sorted(both + ob)])
    files = {"sales/orders.csv": orders, "sales/shipments.jsonl": ship}

    def solve(files):
        o = {l.split(",")[0]: int(l.split(",")[1]) for l in files["sales/orders.csv"].splitlines()[1:]}
        s = {json.loads(l)["order"]: json.loads(l)["billed"] for l in files["sales/shipments.jsonl"].splitlines()}
        diff = sorted(k for k in o if k in s and o[k] != s[k])
        only = sorted(set(s) - set(o))
        return {"turns": [{"number": len(diff), "items": diff}, {"number": len(only), "items": only}], "decoys": {"TR-DECOY": len(diff) + len(only)}}
    emit("tab-32237", sub="reconcile", task_type="reconcile", desc="Finds orders whose billed amount differs between two sources, then shipments without any order",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "sales/orders.csv 是订单金额，sales/shipments.jsonl 是发货单上的 billed 金额。两边都有的订单里，哪些金额对不上？告诉我数量和订单号。"},
                {"prompt": "再查一下，发货单里有、但订单表里根本没有的订单有哪些？数量和订单号。"}],
         ref=(["jq -r .order sales/shipments.jsonl | sort > /tmp/s.txt; tail -n +2 sales/orders.csv | cut -d, -f1 | sort > /tmp/o.txt; comm -13 /tmp/o.txt /tmp/s.txt > /tmp/x.txt; cat /tmp/x.txt; wc -l < /tmp/x.txt"], 0),
         notes_traps=["TR-DECOY: shipment-only orders are not amount mismatches."], notes_ref=["jq -r '[.order,.billed]|@csv' joined with orders.csv via join, compare amounts.", "comm -13 for shipment-only."], unique="Mismatches only among common ids.")


@reg
def d4(i):
    rng = Random(3223800 + i * 7919)
    skus = pool(rng, "SKU-", rng.randint(320, 400), 5, 10000)
    sysq = {s: rng.randint(0, 60) for s in skus}
    bad = sorted(rng.sample(skus, rng.randint(6, 9)))
    cnt = {s: sysq[s] + (rng.choice([-3, -1, 2, 5]) if s in bad else 0) for s in skus}
    for s in bad:
        cnt[s] = max(cnt[s], 0)
        if cnt[s] == sysq[s]:
            cnt[s] += 1
    files = {"inv/system.csv": L("sku,qty", *["%s,%d" % (s, sysq[s]) for s in skus]), "inv/stocktake.csv": L("sku,counted", *["%s,%d" % (s, cnt[s]) for s in skus])}

    def solve(files):
        a = {l.split(",")[0]: int(l.split(",")[1]) for l in files["inv/system.csv"].splitlines()[1:]}
        b = {l.split(",")[0]: int(l.split(",")[1]) for l in files["inv/stocktake.csv"].splitlines()[1:]}
        d = sorted(k for k in a if a[k] != b[k])
        return {"turns": [{"number": len(d), "items": d}], "decoys": {"TR-DECOY": len(a)}}
    emit("tab-32238", sub="reconcile", task_type="reconcile", desc="Lists SKUs whose counted quantity differs from the system quantity across two same-order CSVs",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "inv/system.csv has the system's stock and inv/stocktake.csv has what the warehouse counted. Which SKUs have different quantities in the two files? Tell me how many and list their SKU codes."}],
         ref=(["join -t, <(tail -n +2 inv/system.csv | sort) <(tail -n +2 inv/stocktake.csv | sort) | awk -F, '$2!=$3{print $1; n++} END{print n}'"], 0),
         notes_traps=["TR-DECOY: most SKUs match; only a handful differ."], notes_ref=["join on sku, awk compare."], unique="Join by sku, compare quantities.")


@reg
def d5(i):
    rng = Random(3223900 + i * 7919)
    ids = pool(rng, "m", rng.randint(300, 380), 4, 1000)
    both, oa, ob = split(rng, ids, rng.randint(5, 8), rng.randint(5, 8))

    def mail(x, up):
        e = "user%s@mail.example" % x[1:]
        return e.upper().replace("MAIL.EXAMPLE", "mail.example") if up else e
    A = L("email,tier", *["%s,%s" % (mail(x, False), rng.choice(["gold", "basic"])) for x in sorted(both + oa)])
    B = L("Email,Joined", *["%s,2026-0%d-1%d" % (mail(x, rng.random() < 0.3), rng.randint(1, 9), rng.randint(0, 9)) for x in sorted(both + ob)])
    files = {"crm/members.csv": A, "crm/newsletter.csv": B}

    def solve(files):
        a = {l.split(",")[0].lower() for l in files["crm/members.csv"].splitlines()[1:]}
        b = {l.split(",")[0].lower() for l in files["crm/newsletter.csv"].splitlines()[1:]}
        o = sorted(a - b)
        raw_b = {l.split(",")[0] for l in files["crm/newsletter.csv"].splitlines()[1:]}
        raw_a = {l.split(",")[0] for l in files["crm/members.csv"].splitlines()[1:]}
        return {"turns": [{"number": len(o), "items": o}], "decoys": {"TR-DECOY": len(raw_a - raw_b), "TR-NUMFMT": len(b - a)}}
    emit("tab-32239", sub="reconcile", task_type="reconcile", desc="Finds members missing from a newsletter list when some newsletter emails are uppercased",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "crm/members.csv 是会员名单，crm/newsletter.csv 是订阅了周报的邮箱（有些邮箱大小写不一样，但算同一个）。哪些会员没有订阅周报？告诉我人数，并列出他们的邮箱。"}],
         ref=(["tail -n +2 crm/members.csv | cut -d, -f1 | tr A-Z a-z | sort > /tmp/a.txt; tail -n +2 crm/newsletter.csv | cut -d, -f1 | tr A-Z a-z | sort > /tmp/b.txt; comm -23 /tmp/a.txt /tmp/b.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt"], 0),
         notes_traps=["TR-DECOY: an exact-case comparison reports extra non-subscribers."], notes_ref=["lowercase both, sort, comm -23."], unique="Case-insensitive set difference.")


@reg
def d6(i):
    rng = Random(3224000 + i * 7919)
    skus = pool(rng, "P", rng.randint(320, 400), 4, 1000)
    old = {s: rng.randint(500, 9000) for s in skus}
    new = dict(old)
    chg = rng.sample(skus, rng.randint(8, 13))
    for s in chg:
        new[s] = old[s] + rng.choice([-200, -50, 100, 300])
    added = pool(rng, "Q", rng.randint(4, 7), 4, 1000)
    for s in added:
        new[s] = rng.randint(500, 9000)
    files = {"price/old.json": json.dumps(old, ensure_ascii=False) + "\n", "price/new.json": json.dumps(new, ensure_ascii=False) + "\n"}

    def solve(files):
        o = json.loads(files["price/old.json"])
        n = json.loads(files["price/new.json"])
        ch = sorted(k for k in o if k in n and o[k] != n[k])
        ad = sorted(set(n) - set(o))
        return {"turns": [{"number": len(ch), "items": []}, {"number": len(ad), "items": ad}], "decoys": {"TR-DECOY": len(ch) + len(ad)}}
    emit("tab-32240", sub="reconcile", task_type="reconcile", desc="Compares two price-list JSON objects for changed prices and for newly added SKUs",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "price/old.json and price/new.json are the old and the new price lists (SKU to price in cents). How many SKUs exist in both but with a different price?"},
                {"prompt": "And which SKUs are brand new in new.json? Count plus the codes."}],
         ref=(["jq -n --slurpfile o price/old.json --slurpfile n price/new.json '$n[0]|keys-($o[0]|keys)|(.[]),length' -r"], 0),
         notes_traps=["TR-DECOY: counting changed plus added gives a bigger number."], notes_ref=["jq: compare entries of both objects; keys difference for new SKUs."], unique="Common keys with different values; new keys.")


@reg
def d7(i):
    rng = Random(3224100 + i * 7919)
    ids = pool(rng, "BX", rng.randint(300, 380), 5, 30000)
    both, oa, ob = split(rng, ids, rng.randint(5, 8), rng.randint(5, 8))
    amt = {x: rng.randint(2000, 480000) for x in ids}
    exp = jl([{"claim": x, "cents": amt[x], "who": rng.choice(["林", "周", "吴"])} for x in sorted(both + oa)])
    inv = L("claim,invoice_no", *["%s,FP%d" % (x, rng.randint(10**7, 10**8)) for x in sorted(both + ob)])
    files = {"报销/claims.jsonl": exp, "报销/invoices.csv": inv}

    def solve(files):
        cl = [json.loads(l) for l in files["报销/claims.jsonl"].splitlines()]
        iv = {l.split(",")[0] for l in files["报销/invoices.csv"].splitlines()[1:]}
        no = [c for c in cl if c["claim"] not in iv]
        t = sum(c["cents"] for c in no)
        ids = sorted(c["claim"] for c in no)
        return {"turns": [{"number": "%d.%02d" % (t // 100, t % 100), "items": ids}], "decoys": {"TR-DECOY": "%d.%02d" % (sum(c["cents"] for c in cl) // 100, sum(c["cents"] for c in cl) % 100)}}
    emit("tab-32241", sub="reconcile", task_type="reconcile", desc="Totals claim amounts that have no matching invoice and lists those claim ids",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "报销/claims.jsonl 是报销单（金额 cents 是分），报销/invoices.csv 是已收到的发票（按报销单号对应）。哪些报销单还没有发票？列出单号，并告诉我这些报销单的金额合计多少元。"}],
         ref=(["tail -n +2 报销/invoices.csv | cut -d, -f1 | sort > /tmp/i.txt; jq -r .claim 报销/claims.jsonl | sort > /tmp/c.txt; comm -23 /tmp/c.txt /tmp/i.txt > /tmp/n.txt; cat /tmp/n.txt; jq -s --rawfile n /tmp/n.txt '($n|split(\"\\n\")) as $m|map(select(.claim as $c|$m|index($c)))|map(.cents)|add/100' 报销/claims.jsonl"], 0),
         notes_traps=["TR-DECOY: the grand total of all claims is not the answer."], notes_ref=["comm -23 claim ids vs invoice ids, then sum cents of those with jq, divide by 100."], unique="Set difference then exact integer-cent sum.")


@reg
def d8(i):
    rng = Random(3224200 + i * 7919)
    hosts = ["srv-%04d" % x for x in sorted(rng.sample(range(1, 3000), rng.randint(300, 380)))]
    both, oa, ob = split(rng, hosts, rng.randint(6, 9), rng.randint(5, 8))
    mon = L(*["target: %s:9100" % x for x in sorted(both + ob)])
    cm = jl([{"hostname": x, "owner": rng.choice(["ops", "dev"])} for x in sorted(both + oa)])
    files = {"mon/targets.yml": mon, "mon/cmdb.jsonl": cm}

    def solve(files):
        m = {l.split(": ")[1].split(":")[0] for l in files["mon/targets.yml"].splitlines()}
        c = {json.loads(l)["hostname"] for l in files["mon/cmdb.jsonl"].splitlines()}
        a, b = sorted(m - c), sorted(c - m)
        return {"turns": [{"number": len(a), "items": a}, {"number": len(b), "items": b}], "decoys": {"TR-DECOY": len(m & c)}}
    emit("tab-32242", sub="reconcile", task_type="reconcile", desc="Finds monitored hosts absent from the CMDB, then CMDB hosts nobody monitors",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "mon/targets.yml lists the hosts our monitoring scrapes (host:port) and mon/cmdb.jsonl is the CMDB. Which monitored hosts are missing from the CMDB? Give the count and hostnames."},
                {"prompt": "Now the other way round: which CMDB hosts are not being monitored? Count and hostnames."}],
         ref=(["sed 's/^target: //; s/:9100$//' mon/targets.yml | sort > /tmp/m.txt; jq -r .hostname mon/cmdb.jsonl | sort > /tmp/c.txt; comm -13 /tmp/m.txt /tmp/c.txt > /tmp/o.txt; cat /tmp/o.txt; wc -l < /tmp/o.txt"], 0),
         notes_traps=["TR-DECOY: ~300 hosts match; the direction matters."], notes_ref=["strip port, sort, comm -23 and comm -13."], unique="Both differences are exact sets.")
