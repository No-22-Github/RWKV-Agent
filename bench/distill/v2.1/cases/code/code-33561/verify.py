# DISTILL-CANARY-479a0219 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '852cbfbd24d630a9a64cc711bdcfaa03241ebb246632dc7306e77908c327f3bd', "fixture changed"
import re
ans = re.findall(r'--- FAIL: (\w+)', files['ci/go-test.log'])
assert ans == ['TestMerge', 'TestRetryTimeout']
ans = ans[0]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
