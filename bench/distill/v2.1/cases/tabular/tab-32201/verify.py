# DISTILL-CANARY-7c5589a8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9b9a6e9f51b9da6f7d85971fa98c64393d688a9834e85631a889118fc6b43e33', "fixture changed"
import re
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

ans = solve(case["files"])
def forms(s):
    """Spellings of one number string: plain, thousands-grouped, trailing zeros trimmed."""
    s = str(s)
    out = []

    def add(x):
        if x not in out:
            out.append(x)

    def group(x):
        w, _, f = x.partition(".")
        return format(int(w), ",") + ("." + f if f else "")
    add(s)
    add(group(s))
    if "." in s:
        t = s.rstrip("0").rstrip(".")
        add(t)
        add(group(t))
    return out
out = []
for t in ans["turns"]:
    for f in forms(t["number"]):
        if f not in out:
            out.append(f)
print(json.dumps({"expected_contains_any": out}))
