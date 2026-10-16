# DISTILL-CANARY-e4dd653f : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7525dfb8be80b7f48c5c8da7ef00966f8f34c23f9f90fb1f09d84928e853dc50', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["pay/ledger.jsonl"].splitlines()]
    sel = [r for r in rows if r["merchant"] == "Kestrel Cafe" and r["status"] == "refunded"]
    t = sum(round(r["amount"] * 100) for r in sel)
    big = [r for r in sel if r["amount"] > 100]
    al = sum(round(r["amount"] * 100) for r in rows if r["merchant"].startswith("Kestrel Cafe") and r["status"] == "refunded")
    return {"turns": [{"number": "%d.%02d" % (t // 100, t % 100), "items": []}, {"number": len(big), "items": []}],
            "decoys": {"TR-DECOY": "%d.%02d" % (al // 100, al % 100)}}

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
