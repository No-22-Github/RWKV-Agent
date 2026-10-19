# DISTILL-CANARY-c4fa92ae : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '71b8405f002db6a750831cb00002f06650d08b60ce584e0ce9a3b0af157d30a6', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
FACTS = json.loads('["3.6.1"]')
assert all(f in corpus for f in FACTS), [f for f in FACTS if f not in corpus]
FINAL = {}
FINAL['VERSION'] = "\n".join(["3.6.1"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": FINAL}, ensure_ascii=False))
