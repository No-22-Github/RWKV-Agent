# DISTILL-CANARY-835b756b : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '5f48a003e74d93dd67df8b9c03c5e8b51836277b89d30fd7315bb7cf3fe66346', "fixture changed"
s=sorted(files,key=lambda p:-len(files[p].encode()))[:3]
answers=[s[0].split('/')[-1]]
print(json.dumps({"expected_string": answers[0]}, ensure_ascii=False))
