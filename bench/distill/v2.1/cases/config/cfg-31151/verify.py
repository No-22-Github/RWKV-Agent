# DISTILL-CANARY-1be33dd5 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'ffaa0eaee38ba06b9bffa9dcf0cf64ef63369894ffeb6c102ac864ffcf621e19', "fixture changed"
def compute(files):
    return {"配置/app.conf": "port = 8080\nhost = 0.0.0.0\nworkers = 8\nlog = info\n"}

FINAL = compute(dict(case["files"]))
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
    elif rule.get("unchanged"):
        assert path in case["files"] and path not in FINAL, path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"]}}, ensure_ascii=False))
