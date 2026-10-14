# DISTILL-CANARY-526a39fc : distillation case
import hashlib, json, re
case = json.load(open("case.json"))
_pin = hashlib.sha256(json.dumps(case["files"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
assert _pin == 'da5e6ac64f4ba1b111835292f95e44e414d1e3043660bcd6e1b6f4ff433e08cc', "fixture changed"
m = re.search('time: \\"([\\d:]+)\\"', case["files"]['backup.yaml'])
assert m and m.group(1) == '02:00'
print(json.dumps({"expected_string": '02:00'}, ensure_ascii=False))
