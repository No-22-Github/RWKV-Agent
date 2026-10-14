# BASHPROBE-CANARY-7d41c0e9 : bashprobe case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'af234f8b93ea7010d3b825995b499ed6543c4902e9626cf677b51c915ba3352d', "fixture changed"
page = case["web_fixture"][0]["content"]
assert case["files"]['ops/vendors.md'].startswith('# Vendors')
assert 'ap-east' in page
print(json.dumps({"expected_contains_any": ["ap-east"]}, ensure_ascii=False))
