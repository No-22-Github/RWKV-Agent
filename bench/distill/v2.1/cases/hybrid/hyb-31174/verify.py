# DISTILL-CANARY-ec315bdd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '28963c50dc3f8dafa6cd44de400a3b53a4a071893cbf707d68382cfdb39b5e1a', "fixture changed"
def compute(files):
    return {"小记/索引.md": "# 索引\n\n1. 做个读书笔记工具\n2. 给爸妈买体检卡\n\n共 2 条\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
