# DISTILL-CANARY-fa220748 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'f13591cd67c6ffb59dbb7f1b884f1bfea7b31dc129add58cf6f048c97fd3f34c', "fixture changed"
def compute(files):
    import json
    d = {}
    for l in files["报表/订单.jsonl"].strip().split("\n"):
        r = json.loads(l)
        if r["paid"]:
            d[r["city"]] = d.get(r["city"], 0) + r["amt"]
    return {"报表/已付款.json": json.dumps(d, ensure_ascii=False, sort_keys=True, indent=2) + "\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
