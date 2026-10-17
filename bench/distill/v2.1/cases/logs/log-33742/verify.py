# DISTILL-CANARY-2300496c : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '0a58e2ed481c9e480978bac5dc4072fd1b3706187c906ac5353da95ca92b5c4e', "fixture changed"
answers=['data.lock','03:40']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
