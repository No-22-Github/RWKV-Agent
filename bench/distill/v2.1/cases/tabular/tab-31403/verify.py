# DISTILL-CANARY-2ddcea18 : distillation case
import hashlib, json
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'aa6b514ca024241c4723fea0c38c705781604034c8bf385953239607b302ebf0', "fixture changed"
import re
m = re.search('Ann,eng,(L\\d)', case["files"]['data/staff.csv'])
assert m, "pattern"
ans = m.group(1)
assert ans in case["turns"][0]["expect"]["output_contains"]

print(json.dumps({"expected_string": ans}, ensure_ascii=False))
