"""b21g sub A (part 2): JSONL, 32210-32214."""
import json
from random import Random

from common import emit, jl, reg


@reg
def a10(i):
    rng = Random(3221000 + i * 7919)
    rows = []
    names = ["拿铁", "冰拿铁", "燕麦拿铁", "美式", "摩卡", "焦糖拿铁"]
    for n in range(rng.randint(500, 620)):
        its = [{"name": rng.choices(names, [5, 3, 2, 5, 2, 1])[0], "qty": rng.randint(1, 3)} for _ in range(rng.randint(1, 3))]
        rows.append({"order": "C%05d" % (n * 2 + rng.randint(0, 1)), "store": rng.choice(["望京店", "国贸店", "中关村店"]), "items": its})
    files = {"门店/orders-0915.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["门店/orders-0915.jsonl"].splitlines()]
        a = sum(i["qty"] for r in rows for i in r["items"] if i["name"] == "拿铁")
        b = sum(i["qty"] for r in rows for i in r["items"] if i["name"] == "冰拿铁")
        c = sum(i["qty"] for r in rows for i in r["items"] if "拿铁" in i["name"])
        return {"turns": [{"number": a, "items": []}, {"number": b, "items": []}], "decoys": {"TR-DECOY": c}}
    emit("tab-32210", sub="jsonl", task_type="aggregate", desc="Adds up nested quantities of one drink name where other names contain it as a substring, then another drink",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "门店/orders-0915.jsonl 是昨天的点单，每行一单，items 里是点的饮品和杯数。名字正好叫“拿铁”的一共卖了多少杯？"},
                {"prompt": "那“冰拿铁”呢？"}],
         ref=(["jq -s '[.[].items[]|select(.name==\"冰拿铁\")|.qty]|add' 门店/orders-0915.jsonl"], 0),
         notes_traps=["TR-DECOY: 冰拿铁/燕麦拿铁/焦糖拿铁 all contain 拿铁."], notes_ref=["jq -s flatten items, select exact name, add qty."], unique="Exact name equality on nested items.")


@reg
def a11(i):
    rng = Random(3221100 + i * 7919)
    rows = []
    for n in range(rng.randint(600, 760)):
        r = {"device": "t-%02d" % rng.randint(1, 14), "temp_c": rng.randint(18, 44), "n": n}
        if rng.random() < 0.9:
            r["valid"] = rng.random() < 0.93
        rows.append(r)
    j0 = rng.randint(0, len(rows) - 1)
    rows[j0]["temp_c"] = rng.randint(46, 52)
    rows[j0]["valid"] = True
    for k in range(3):
        j = rng.randint(0, len(rows) - 1)
        rows[j]["temp_c"] = rng.randint(85, 120)
        rows[j]["valid"] = False
    files = {"sensors/readings.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["sensors/readings.jsonl"].splitlines()]
        ok = [r for r in rows if r.get("valid") is True]
        m = max(r["temp_c"] for r in ok)
        devs = sorted({r["device"] for r in ok if r["temp_c"] == m})
        assert len(devs) == 1
        allm = max(r["temp_c"] for r in rows)
        return {"turns": [{"number": m, "items": devs}], "decoys": {"TR-DECOY": allm, "TR-MISSING": max(r["temp_c"] for r in rows if r.get("valid") is not False)}}
    emit("tab-32211", sub="jsonl", task_type="rank", desc="Finds the hottest valid reading in a JSONL with invalid spikes and a valid flag that is sometimes absent",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "sensors/readings.jsonl has temperature readings. Among readings flagged valid (valid is true), what is the highest temp_c and which device reported it?"}],
         ref=(["jq -s 'map(select(.valid==true))|max_by(.temp_c)|[.device,.temp_c]|@csv' -r sensors/readings.jsonl"], 0),
         notes_traps=["TR-DECOY: three invalid sensor spikes of 85-120 degrees top the unfiltered file."], notes_ref=["jq -s select valid==true, max_by temp_c."],
         unique="Only valid==true readings; unique maximum device.")


@reg
def a12(i):
    rng = Random(3221200 + i * 7919)
    rows = []
    for n in range(rng.randint(640, 820)):
        s = "S%03d" % rng.randint(1, 260)
        rows.append({"student": s, "exam": "E%02d" % rng.randint(1, 12), "score": rng.randint(52, 100)})
    files = {"成绩/records.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["成绩/records.jsonl"].splitlines()]
        d = {}
        for r in rows:
            d.setdefault(r["student"], []).append(r["score"])
        a = [s for s, v in d.items() if len(v) >= 2 and sum(v) / len(v) >= 85]
        b = [s for s, v in d.items() if sum(v) / len(v) >= 85]
        return {"turns": [{"number": len(a), "items": []}], "decoys": {"TR-DEFN": len(b), "TR-DUPROW": len(d)}}
    emit("tab-32212", sub="jsonl", task_type="filter_count", desc="Counts students whose average over at least two exam records is 85 or more, from one JSONL record per sitting",
         files=files, solve=solve, traps=["TR-DEFN", "TR-DUPROW"],
         turns=[{"prompt": "成绩/records.jsonl 每行是一个学生一次考试的分数，同一个学生会有好几行。按学生算平均分，至少考过两次、平均分不低于 85 的学生有多少个？"}],
         ref=(["jq -s 'group_by(.student)|map(select(length>=2 and ((map(.score)|add)/length)>=85))|length' 成绩/records.jsonl"], 0),
         notes_traps=["TR-DEFN: students with one record are excluded even when it is high.", "TR-DUPROW: a row-level count of scores over 85 is not the answer."],
         notes_ref=["jq -s group_by student, filter length>=2 and avg>=85, length."], unique="Average is exact arithmetic mean; threshold inclusive.")


@reg
def a13(i):
    rng = Random(3221300 + i * 7919)
    rows = []
    for n in range(rng.randint(560, 700)):
        rows.append({"txn": "X%06d" % (n * 3 + rng.randint(0, 2)), "merchant": rng.choices(["Kestrel Cafe", "Kestrel Cafe II", "Orchard Books", "Lamp & Loom"], [4, 3, 4, 3])[0],
                     "status": rng.choices(["settled", "refunded", "failed"], [12, 3, 2])[0], "amount": rng.randint(500, 41000) / 100})
    files = {"pay/ledger.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["pay/ledger.jsonl"].splitlines()]
        sel = [r for r in rows if r["merchant"] == "Kestrel Cafe" and r["status"] == "refunded"]
        t = sum(round(r["amount"] * 100) for r in sel)
        big = [r for r in sel if r["amount"] > 100]
        al = sum(round(r["amount"] * 100) for r in rows if r["merchant"].startswith("Kestrel Cafe") and r["status"] == "refunded")
        return {"turns": [{"number": "%d.%02d" % (t // 100, t % 100), "items": []}, {"number": len(big), "items": []}],
                "decoys": {"TR-DECOY": "%d.%02d" % (al // 100, al % 100)}}
    emit("tab-32213", sub="jsonl", task_type="aggregate", desc="Sums refunded amounts for one merchant whose name is a prefix of another, then counts the large ones",
         files=files, solve=solve, traps=["TR-DECOY"],
         turns=[{"prompt": "In pay/ledger.jsonl, how much money was refunded for the merchant \"Kestrel Cafe\" (the exact name; \"Kestrel Cafe II\" is a different shop)? Refunded means status is refunded."},
                {"prompt": "How many of those refunds were for more than 100?"}],
         ref=(["jq -s 'map(select(.merchant==\"Kestrel Cafe\" and .status==\"refunded\" and .amount>100))|length' pay/ledger.jsonl"], 0),
         notes_traps=["TR-DECOY: Kestrel Cafe II shares the prefix."], notes_ref=["jq -s exact merchant, status refunded, sum amount.", "Turn 2: add amount>100, length."],
         unique="Exact merchant and status strings.")


@reg
def a14(i):
    rng = Random(3221400 + i * 7919)
    rows = []
    for n in range(rng.randint(540, 680)):
        r = {"req": "r%05d" % (n * 7 + rng.randint(0, 6)), "svc": rng.choice(["auth", "cart", "pay", "feed"])}
        k = rng.random()
        if k < 0.35:
            r["errors"] = [{"code": "E%d" % rng.randint(100, 199)} for _ in range(rng.randint(1, 4))]
        elif k < 0.55:
            r["errors"] = []
        rows.append(r)
    files = {"trace/spans.jsonl": jl(rows)}

    def solve(files):
        rows = [json.loads(x) for x in files["trace/spans.jsonl"].splitlines()]
        tot = sum(len(r.get("errors") or []) for r in rows)
        lines = sum(1 for r in rows if r.get("errors"))
        return {"turns": [{"number": tot, "items": []}, {"number": lines, "items": []}], "decoys": {"TR-MISSING": len(rows), "TR-DECOY": lines}}
    emit("tab-32214", sub="jsonl", task_type="aggregate", desc="Totals array lengths of an optional errors field in a JSONL, then counts the lines that have any",
         files=files, solve=solve, traps=["TR-MISSING"],
         turns=[{"prompt": "trace/spans.jsonl 里每行是一次请求，有的带 errors 数组（可能为空，也可能没有这个字段）。所有行加起来一共有多少个错误项？"},
                {"prompt": "那有多少行至少带一个错误？"}],
         ref=(["jq -s 'map(select((.errors//[])|length>0))|length' trace/spans.jsonl"], 0),
         notes_traps=["TR-MISSING: errors is absent on ~45% of lines and empty on ~20%."], notes_ref=["jq -s map((.errors//[])|length)|add.", "Turn 2: count lines with non-empty errors."],
         unique="Array lengths summed; absent field counts as zero.")
