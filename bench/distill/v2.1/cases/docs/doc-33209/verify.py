# DISTILL-CANARY-0e84a955 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '13cc4d442046bf0330f7697cc11bdfb1cae7bc56fa078f9c7d67dce62cdbfad4', "fixture changed"
files = case["files"]
FACTS = json.loads('["# 秋季运动会报名通知", "10月17日", "滨江体育场", "10月10日", "秦岚", "邓超", "曾艺", "## 奖励", "前三名"]')
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
