# DISTILL-CANARY-a506bf61 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4586fbd52a4c12af05befd4bf4faf1fa474ec3978fb40ffd671576fe7b789103', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
FACTS = json.loads('["8081"]')
assert all(f in corpus for f in FACTS), [f for f in FACTS if f not in corpus]
FINAL = {}
FINAL['.env'] = "\n".join(["PORT=8081", "DEBUG=0", "REGION=eu-west"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": FINAL}, ensure_ascii=False))
