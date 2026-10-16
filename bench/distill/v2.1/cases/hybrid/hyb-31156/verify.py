# DISTILL-CANARY-a22ba0af : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'c611a8d4bcd8509398a08c01e0556536337e80b23a8b9e55d046342eaab00413', "fixture changed"
def compute(files):
    return {"项目/计划.md": "# 计划\n\n- 9月：需求\n- 10月：开发\n- 11月：测试\n- 12月：上线\n- 1月：回顾\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
