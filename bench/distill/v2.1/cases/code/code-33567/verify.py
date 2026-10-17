# DISTILL-CANARY-d288e36e : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '80403cc4225b3cf5f4db1ded1758b890cce5b03f7db9bed65ab5b4eaebb63c02', "fixture changed"
ans = 'bearing_north'
assert 'bearing_north' in files['target/geo-report.xml']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
