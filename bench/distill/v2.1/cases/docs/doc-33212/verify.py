# DISTILL-CANARY-468361be : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '35d72d84e9c2267227ef7808d8d2a9f27fab609e7567b528d78db7819f0a6d7b', "fixture changed"
files = case["files"]
FACTS = json.loads('["Priya Raman", "Data Analyst", "2026-10-12", "14,500", "3 months", "Elena Park", "18 days"]')
corpus = "".join(files.values()) + "".join(t["prompt"] for t in case["turns"])
FREE = json.loads('[]')
assert all(f in corpus for f in FACTS if f not in FREE), [f for f in FACTS if f not in corpus and f not in FREE]
FINAL = {p: "\n".join(FACTS) for p, r in case["expect"]["files"].items() if "contains" in r}
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": {k: v for k, v in FINAL.items() if k in case["expect"]["files"] and "unchanged" not in case["expect"]["files"][k]}}, ensure_ascii=False))
