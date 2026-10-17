# DISTILL-CANARY-fd30f0b6 : distillation case
import hashlib, json
case = json.load(open("case.json"))
files = case["files"]
_pin = hashlib.sha256(json.dumps(files, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '1436a523842782a767022b1e872160a25d76263d639419fa2a23165d73c123a6', "fixture changed"
log = files['build/test.log'].split('## run 2')[1]
import re
ans = re.findall(r'::(\w+) FAILED', log)
assert ans == ['test_keys_sorted']
ans = ans[0]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
