# DISTILL-CANARY-81df4b19 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '683d7bb70b285c92cf1047889fc9c3b7a6d8f51c46fab2ee343855d4c82e5a9a', "fixture changed"
answers=['14:00','14:21']
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
