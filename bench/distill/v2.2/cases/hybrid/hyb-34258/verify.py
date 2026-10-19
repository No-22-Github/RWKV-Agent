# DISTILL-CANARY-f382e87e : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '859a2058968c820e54ed405bcf1306731d32dbd28586506148d714448d4ad391', "fixture changed"
files = case["files"]
corpus = "\n".join(files.values()) + "\n".join(w["content"] + " " + w["snippet"] for w in case["web_fixture"]) + "\n".join(t["prompt"] for t in case["turns"])
FACTS = json.loads('["PORT=9000", "DEMO_TOKEN"]')
assert all(f in corpus for f in FACTS), [f for f in FACTS if f not in corpus]
FINAL = {}
FINAL['notes.txt'] = "\n".join(["setup notes", "PORT=9000", "DEMO_TOKEN"])
for path, rule in case["expect"]["files"].items():
    if "equals" in rule:
        assert FINAL[path] == rule["equals"], path
    elif "contains" in rule:
        assert all(s in FINAL[path] for s in rule["contains"]), path
print(json.dumps({"files": FINAL}, ensure_ascii=False))
