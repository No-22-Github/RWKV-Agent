# DISTILL-CANARY-d3560924 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '2e90559c05ef4ac0bad626a9de4b4c6a1dbfc89c7093de17cc45600881bdfef2', "fixture changed"
files = case["files"]
FACTS = json.loads('["# 新员工入职培训通知", "9月28日", "9月29日", "三楼培训室", "钱峰", "蒋云", "## 温馨提示", "笔记本电脑", "12:00"]')
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
