# DISTILL-CANARY-93b4336d : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4af5d0e24687e5c0dbfe2f1aebc6898a80e11148980dc206aaec5452845fd030', "fixture changed"
import re
def solve(files):
    rows = [json.loads(x) for x in files["ci/runs.jsonl"].splitlines()]
    c = {}
    for r in rows:
        if r["branch"] == "main" and r["result"] == "failure":
            c[r["job"]] = c.get(r["job"], 0) + 1
    al = {}
    for r in rows:
        if r["result"] == "failure":
            al[r["job"]] = al.get(r["job"], 0) + 1
    rk = sorted(c.items(), key=lambda kv: -kv[1])
    ra = sorted(al.items(), key=lambda kv: -kv[1])
    assert rk[0][1] > rk[1][1] and ra[0][0] != rk[0][0]
    job = rk[0][0]
    secs = sum(r["duration_s"] for r in rows if r["branch"] == "main" and r["result"] == "failure" and r["job"] == job)
    return {"turns": [{"number": rk[0][1], "items": [job]}, {"number": secs, "items": []}],
            "decoys": {"TR-DECOY": ra[0][1], "TR-MULTISRC": rk[1][1]}}

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
