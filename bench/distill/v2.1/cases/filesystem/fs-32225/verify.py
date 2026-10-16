# DISTILL-CANARY-45185834 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '70857cb1bee004c245caba1e29c9989b10a172414e58c24e11e0591166050c29', "fixture changed"
import re
def solve(files):
    r = sorted(files.items(), key=lambda kv: -len(kv[1].encode()))[:5]
    return {"turns": [{"number": len(r[0][1].encode()), "items": [p.rsplit("/", 1)[1] for p, _ in r]}], "decoys": {"TR-TRUNC": len(r[1][1].encode())}}

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
