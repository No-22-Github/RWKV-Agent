# DISTILL-CANARY-5b8c7ba9 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f77fc04dc5423ab4534214a2d0fde8b9c4f0de6b3fd4b7148e960ca47da6578c', "fixture changed"
import re
def solve(files):
    t = sum(len(v.encode()) for p, v in files.items() if p.endswith(".csv") and "/archive/" not in p)
    a = sum(len(v.encode()) for p, v in files.items() if p.endswith(".csv"))
    return {"turns": [{"number": t, "items": []}], "decoys": {"TR-DECOY": a, "TR-TRUNC": 50}}

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
