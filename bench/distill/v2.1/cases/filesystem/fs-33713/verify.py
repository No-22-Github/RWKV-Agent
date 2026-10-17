# DISTILL-CANARY-5e19e395 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '298c029eb400772c5b8277607120cf2706b245aaf2ff6516417cac0f03004d89', "fixture changed"
n=[p for p in files if p.lower().endswith('.md')]
answers=[str(len(n)), str(len([p for p in n if p.count('/')==1]))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
