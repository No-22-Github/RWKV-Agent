# DISTILL-CANARY-216e3cc3 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'b5270fcc584396a9e6302b070d0d03123f1c6b245b95ee58c4f37555d09827e9', "fixture changed"
def compute(files):
    return {"备忘/清单.md": "# 采购\n\n- 牙膏\n- 纸巾\n- 洗衣液\n- 电池\n- 垃圾袋\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
