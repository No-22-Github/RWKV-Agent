# DISTILL-CANARY-8230f37b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '48c41380161bcea7e0d8d960dac84d72ad1873fcaa6d3ec057a3e7807ed5e397', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["hr/policy-dates.md"].split("\n"):
        if l.startswith("- 20"):
            d, t = l[2:].split(": ", 1)
            rows.append((d, t))
    rows = sorted(r for r in rows if r[0] >= "2026-09-16" and "Fire drill" not in r[1])
    return {"hr/upcoming.txt": "".join("%s %s\n" % r for r in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
