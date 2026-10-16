# DISTILL-CANARY-6ba4a92b : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '7c923eeb352468e884623396dc5311bb202c53ef6d78db961ef524d605263bac', "fixture changed"
def compute(files):
    rows = []
    for l in files["docs/team.md"].split("\n"):
        if l.startswith("- "):
            n, r, e = [x.strip() for x in l[2:].split("—")]
            rows.append((n, r, e))
    out = "name,role,email\n" + "".join("%s,%s,%s\n" % t for t in sorted(rows, key=lambda t: t[0].split()[-1]))
    return {"docs/team.csv": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
