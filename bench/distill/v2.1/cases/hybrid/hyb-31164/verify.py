# DISTILL-CANARY-78eca290 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8fab792afd8103d2f447539c99d807bed6ac65c459408dacd06c7ce11f4b4d66', "fixture changed"
def compute(files):
    return {"团队/成员.csv": "name,city,offset\nLu,Boston,UTC-5\nMai,Austin,UTC-6\nNia,Boston,UTC-5\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
