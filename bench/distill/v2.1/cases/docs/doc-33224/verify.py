# DISTILL-CANARY-12b50cbd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '13df03ef557ec2be81fa5f2f5ec85c1e05cabcacb8d30cd3df135c2e308fa256', "fixture changed"
files = case["files"]
def compute(files):
    rows = []
    for l in files["notes/standup.md"].split("\n"):
        if " -- due " in l:
            a = l[2:]
            who = a.split(":")[0]
            task = a.split(":")[1].split(" -- due ")[0].strip()
            rows.append((who, task, a.split(" -- due ")[1]))
    rows.sort(key=lambda r: r[2])
    return {"notes/actions.md": "| Owner | Task | Due |\n|---|---|---|\n" + "".join("| %s | %s | %s |\n" % r for r in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
