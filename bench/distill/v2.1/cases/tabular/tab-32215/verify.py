# DISTILL-CANARY-03ba5932 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '33832b9838ab74329708c050742049ec507a3ec2cac80635592ce77ec0002bc6', "fixture changed"
import re
def solve(files):
    d = json.loads(files["报表/stores.json"])
    a = sum(m["revenue"] for s in d["stores"] for m in s["months"] if m["month"] == "2026-08" and m["revenue"] is not None)
    b = sum(m["revenue"] for s in d["stores"] for m in s["months"] if m["revenue"] is not None)
    c = sum(m["revenue"] - sum(m["refunds"]) for s in d["stores"] for m in s["months"] if m["month"] == "2026-08" and m["revenue"] is not None)
    return {"turns": [{"number": a, "items": []}], "decoys": {"TR-MISSING": b, "TR-DECOY": c}}

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
