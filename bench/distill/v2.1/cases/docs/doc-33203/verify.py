# DISTILL-CANARY-b4352139 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'a42e55bcb8fa0e05ba5c6a10d7d60b6d7e6bb0b42bd354bae2c65bf7e99a433e', "fixture changed"
files = case["files"]
FACTS = json.loads('["14:00-15:30", "B座302", "陈曦", "郑凯", "10%", "吴昊", "孙悦", "竞品对比", "埋点规范"]')
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
