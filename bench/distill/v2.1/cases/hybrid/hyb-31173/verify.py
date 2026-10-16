# DISTILL-CANARY-dea74515 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '28d035105dcc13d85097dcd01d4a57436873c3757c8c8d917cc856bf00084ce5', "fixture changed"
def compute(files):
    return {"设备/升级单.md": "# 升级单\n\n- agent: 2.1.0 -> 2.2.0\n- proxy: 1.9.4 -> 2.0.0\n- collector: 3.0.1\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
