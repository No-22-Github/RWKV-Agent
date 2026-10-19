# DISTILL-CANARY-e29ea846 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '859f83e125dea5e304da57a50ec0a1f6d34be697afa9e6dc462e899677e06dda', "fixture changed"
s = sorted(files, key=lambda p: -len(files[p].encode()))[:3]
assert len(files[s[2]].encode()) > 3400 and len(files[sorted(files, key=lambda p: -len(files[p].encode()))[3]].encode()) < 1900
answers = [[p.split('/')[-1] for p in s]]

print(json.dumps({"expected_string": answers[0][0]}, ensure_ascii=False))
