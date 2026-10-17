# DISTILL-CANARY-365268cc : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'd9c4405b5d0c1ba9e0dd243f7c04a035c7821e119f85cced7f05ee0176c2fd45', "fixture changed"
ans = 'test_url_trailing'
assert 'test_url_trailing FAILED' in files['out/pytest.txt']

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
