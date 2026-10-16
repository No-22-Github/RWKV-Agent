# DISTILL-CANARY-86a13365 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c4c38cf8d05de43d021375b9a12a062a948c30f264157976f18b6819667c6cad', "fixture changed"
import re
def solve(files):
    d = json.loads(files["shop/orders.json"])
    tot = sorted(((sum(l["qty"] * l["price"] for l in o["lines"]), o["order"]) for o in d), reverse=True)
    assert tot[0][0] > tot[1][0]
    n = len([1 for t, _ in tot if t > 2500])
    return {"turns": [{"number": tot[0][0], "items": [tot[0][1]]}, {"number": n, "items": []}], "decoys": {"TR-DEFN": max(l["price"] for o in d for l in o["lines"])}}

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
