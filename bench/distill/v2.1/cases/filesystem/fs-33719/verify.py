# DISTILL-CANARY-555caf99 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '8be109e00f3f2794ef65dac62a2bd6bd6b23f4df006034e733e262ae0f66c29f', "fixture changed"
answers=['legal/LICENSE']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
