# DISTILL-CANARY-2c9962c7 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd49cb412a4d0fb0cfea4061313374dded3ef45153ba0388ad4fc75c7b8423a1a', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["财务/payments-0916.jsonl"].splitlines()]

    def f(c):
        return "%d.%02d" % (c // 100, c % 100)
    a = sum(round(r["amount"] * 100) for r in rows if r.get("currency") == "CNY")
    b = sum(round(r["amount"] * 100) for r in rows)
    return {"turns": [{"number": f(a), "items": []}], "decoys": {"TR-MISSING": f(b), "TR-DECOY": f(b - 1)}}

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
