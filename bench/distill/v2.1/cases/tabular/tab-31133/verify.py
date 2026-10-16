# DISTILL-CANARY-cd9f2c16 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'dd1177ccc70741e109aa16edb03f6662f6c2281baf05661c803a7b44fac3929d', "fixture changed"
def compute(files):
    rows = [l.split(",") for l in files["员工/名单.csv"].strip().split("\n")[1:]]
    rows.sort(key=lambda r: -int(r[2]))
    return {"员工/公示.csv": "姓名,部门\n" + "".join("%s,%s\n" % (r[0], r[1]) for r in rows)}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
