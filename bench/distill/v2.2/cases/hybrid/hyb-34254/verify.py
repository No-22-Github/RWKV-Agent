# DISTILL-CANARY-33209b99 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '88c0e92c4ecbc5293ebf2f2673d53b0e7b88c8659031134519f9f1054343ca0f', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
FACTS = json.loads('[]')
assert all(f in corpus for f in FACTS), [f for f in FACTS if f not in corpus]
FINAL = {}
FINAL['svc/gateway-trace.out'] = ""
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": FINAL}, ensure_ascii=False))
