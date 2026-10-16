# DISTILL-CANARY-ec816804 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '81f7db4848f7e62ebc584592992f3dea638a75636d45151d47b1997de8f01d08', "fixture changed"
ans = [l.split(',')[1] for l in files['members.csv'].splitlines()[1:] if int(l.split(',')[0]) == 167][0]
print(json.dumps({"expected_string": ans}, ensure_ascii=False))
