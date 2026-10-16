# DISTILL-CANARY-2b78ba61 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4eb695b8dba68adf10810c1c524e3e01fdabf074bf2628932b66a4c9864c3e81', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["sales/2026-q3.jsonl"].splitlines()]
    s, c = {}, {}
    for r in rows:
        if r["region"] is None:
            continue
        s[r["region"]] = s.get(r["region"], 0) + r["amount_yuan"]
        c[r["region"]] = c.get(r["region"], 0) + 1
    rs = sorted(s.items(), key=lambda kv: -kv[1])
    rc = sorted(c.items(), key=lambda kv: -kv[1])
    assert rs[0][1] - rs[1][1] > 500 and rs[0][0] != rc[0][0]
    return {"turns": [{"number": rs[0][1], "items": [rs[0][0]]}], "decoys": {"TR-MISSING": rs[1][1], "TR-DECOY": rs[0][1] + 1}}

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
