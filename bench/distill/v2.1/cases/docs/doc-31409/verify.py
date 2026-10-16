# DISTILL-CANARY-d74ed9bd : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '89d1386b33386d629c80d43798d9a4a1615da65672e4a364b709a50723c762a1', "fixture changed"
import re
m = re.search('员工 Wi-Fi：(Corp-Secure)', case["files"]['wiki/wifi.md'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
