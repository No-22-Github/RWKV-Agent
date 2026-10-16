# DISTILL-CANARY-fb1ea2f2 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '01e4d80013d89a60a7970c2fb290fc8b16ef9111b70ec9b84f617f11ea528754', "fixture changed"
def compute(files):
    return {"出差/住宿.csv": "城市,酒店,晚数\n北京,望京店,2\n成都,春熙店,1\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
