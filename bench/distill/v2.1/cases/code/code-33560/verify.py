# DISTILL-CANARY-16c6e21d : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'eaa0ee2c874ff744c97b1abe8d5e61db2cc3d08b445c8ad8aba0d6dcb488b98c', "fixture changed"
import re
ans = [m for m in re.findall(r'::(\w+) FAILED', files['reports/last_run.log'])]
assert ans == ['test_email_case', 'test_token_refresh', 'test_admin_flag']
ans = ans[0]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
