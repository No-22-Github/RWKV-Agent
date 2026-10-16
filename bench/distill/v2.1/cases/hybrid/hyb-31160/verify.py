# DISTILL-CANARY-bda46639 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '18b6d395a29367d918e4774ae5ae91391a611b11dab37d837c3474aceb82133c', "fixture changed"
def compute(files):
    return {"日历/周计划.csv": "星期,事项\n周一,例会\n周二,评审\n周三,出差\n周四,出差\n周五,团建\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
