# DISTILL-CANARY-69d21dbe : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7b61bbcfc52757fbf11ab63d05b340f8967bdab1e00e38685592c59d3cb530f0', "fixture changed"
import re
def solve(files):
    a = {p: len(v.encode()) for p, v in files.items() if p.startswith("logs/app-")}
    big = [p for p, s in a.items() if s > 1000]
    top = max(a.items(), key=lambda kv: kv[1])
    assert sorted(a.values())[-1] != sorted(a.values())[-2]
    return {"turns": [{"number": len(big), "items": []}, {"number": top[1], "items": [top[0].split("/")[1]]}], "decoys": {"TR-DECOY": len([p for p, v in files.items() if len(v) > 1000]), "TR-TRUNC": 50}}

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
