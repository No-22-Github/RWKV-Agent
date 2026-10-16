# DISTILL-CANARY-2de56a87 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == '947097adc1584d903e77db9376ba5c06281096555365e6ef3e34f4ae22c52ee4', "fixture changed"
import re
m = re.search('2026-09-15,disk_full,(\\d+)', case["files"]['alerts/history.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
