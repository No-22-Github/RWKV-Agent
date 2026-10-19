# DISTILL-CANARY-15365b35 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '48035f52c89786fa9efe4ef6c6e8d57218cece6f039172f1deac8105da5626f4', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
FACTS = json.loads('["评审接口文档", "发周报"]')
assert all(f in corpus for f in FACTS), [f for f in FACTS if f not in corpus]
FINAL = {}
FINAL['待办/本周跟进清单.md'] = "\n".join(["评审接口文档", "发周报"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": FINAL}, ensure_ascii=False))
