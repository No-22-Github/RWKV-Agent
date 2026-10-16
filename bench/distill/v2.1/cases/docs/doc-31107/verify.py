# DISTILL-CANARY-dcc98a6c : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1b07c3e67de82af209ef7c86d923ef78be052d406df851461f9b08a3341c528e', "fixture changed"
def compute(files):
    d = {}
    for l in files["项目/任务.md"].split("\n"):
        if l.startswith("- [ ] "):
            t, who = l[6:].rsplit(" @", 1)
            d.setdefault(who, []).append(t)
    out = ""
    for who in sorted(d):
        out += "%s\n" % who + "".join("- %s\n" % t for t in d[who])
    return {"项目/待办清单.txt": out}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
