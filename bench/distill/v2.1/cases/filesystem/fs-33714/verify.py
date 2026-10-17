# DISTILL-CANARY-8bf28669 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8ac8e4d9326622faa926a8d177655caafadf7f12e8f59934086a719bd60e83cd', "fixture changed"
answers=[str(len([p for p in files if p.endswith('.json')])), str(len([p for p in files if p.endswith(('.yaml','.yml'))]))]
print(json.dumps({"expected_number": float(answers[0])}, ensure_ascii=False))
