# DISTILL-CANARY-782bc26d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9798c293426c9de25cfdd630760520868ce63a94e4d537024b4278e1c2491c1f', "fixture changed"
import re
def solve(files):
    md = {p: t for p, t in files.items() if p.endswith(".md")}
    loose = {p: t for p, t in files.items() if ".md" in p}
    n = sum(len(t.splitlines()) for t in md.values())
    return {"turns": [{"number": len(md), "items": []}, {"number": n, "items": []}], "decoys": {"TR-DECOY": len(loose), "TR-TRUNC": 50}}

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
