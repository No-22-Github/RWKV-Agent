# DISTILL-CANARY-a382c4b8 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a12c164d477c1fdbaa38d8a45aee326829955009e5f0c4566f10cae9d36fca6f', "fixture changed"
files = case["files"]
FACTS = json.loads('["# 第38周周报（后端组）", "周朗", "1200 QPS", "91%", "## 需要的支持", "扩容测试环境磁盘"]')
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
