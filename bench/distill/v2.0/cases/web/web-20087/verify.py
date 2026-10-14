# DISTILL-CANARY-b12eb10c : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '4dd155b621eca2ffc9841d1d6273d904de20ca189d4e8eccf4e9a67d789be4f2', "fixture changed"
txt = case["files"]['docs/pricing-notes.md']
m = re.search('Pro plan is (29) USD', txt)
print(json.dumps({"expected_string": m.group(1)}, ensure_ascii=False))
