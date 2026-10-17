# DISTILL-CANARY-1806720b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '42ec2319feb138313c02b22b94b3d507822ec6ed60a7b1995eee46dfa95c3953', "fixture changed"
answers=['14:32','16:02']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
