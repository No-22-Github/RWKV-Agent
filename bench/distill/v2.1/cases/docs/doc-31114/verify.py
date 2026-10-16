# DISTILL-CANARY-0c64a940 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '9b91709e98b846663c4b6403d5a0dc8e89fb2d1e734d3b2100a652a75d4f75a6', "fixture changed"
def compute(files):
    items = []
    for p in sorted(files):
        for l in files[p].split("\n"):
            if l.startswith("- 待办："):
                items.append(l[5:] + " (" + p.split("/")[1][:-3] + ")")
    return {"会议/待办汇总.txt": "".join(i + "\n" for i in items)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
