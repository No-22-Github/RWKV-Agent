# DISTILL-CANARY-a089fecd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '55fe4760ba3f407d17952c895033daef76a1165c544d927f9fa2bed06215df4d', "fixture changed"
files = case["files"]
def compute(files):
    rows = [l.split(" ", 1)[1] for l in files["日程/本周.txt"].split("\n") if l.startswith("周三")]
    rows.sort()
    return {"日程/周三.md": "".join("- %s\n" % r for r in rows)}

FINAL = compute(dict(files))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
